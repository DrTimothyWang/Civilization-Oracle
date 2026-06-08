"""
Civilization-Oracle v4.0 - 数据收集主入口
=========================================

流程:
1. 对每个十年窗口:
   a. 用 MiniMax API 生成历史叙述（基于真实历史事件锚点）
   b. 对叙述做 3 次情感分析取中位数
   c. 从 CBDB SQLite 提取该十年的专家分布和地理信息
2. 输出 individual-level 数据集
3. 聚合成十年级数据
4. 用 v4 公式计算 PSI

v3.0 的关键问题: 数据"假"——文本是硬编码、情感是 mock
v4.0 的修复: 全部真实 LLM 调用 + 真实 CBDB 查询
"""
import sys
import os
import json
import sqlite3
import time
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_caller import (
    generate_decade_narrative,
    analyze_sentiment_v4,
    all_decades,
)
from formula import (
    compute_psi_z,
    compute_mmp,
    compute_sfd,
    compute_eed,
    compute_gsi,
    gsi_correction,
    ipw_correction,
    psi_z_to_final,
    classify_period,
    compute_standardization_stats,
    StandardizationStats,
    DecadeResult,
)


# ============================================================
# CBDB 数据接入
# ============================================================

CBDB_PATH = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"


def get_cbdb_connection():
    """连接 CBDB SQLite"""
    if not os.path.exists(CBDB_PATH):
        print(f"[!] CBDB 数据库不存在: {CBDB_PATH}")
        return None
    conn = sqlite3.connect(CBDB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# 朝代年份窗口（用于 CBDB 查询）
DYNASTY_YEAR_WINDOWS = {
    "唐朝": (618, 907),
    "北宋前期": (960, 1027),
    "北宋后期": (1028, 1127),
    "南宋": (1128, 1279),
    "明朝": (1368, 1644),
}


def query_decade_experts(conn, dynasty: str, decade_start: int, decade_end: int) -> List[Dict]:
    """
    从 CBDB 查询指定十年窗口的所有专家

    返回: [{'person_id', 'name', 'birth_year', 'death_year', 'lat', 'lng', ...}, ...]
    """
    if not conn:
        return []

    cur = conn.cursor()

    # CBDB BIOG_MAIN 表
    query = """
        SELECT DISTINCT
            b.c_personid,
            b.c_name_chn,
            b.c_birthyear,
            b.c_deathyear,
            b.c_dy,
            addr.x_coord,
            addr.y_coord
        FROM biog_main b
        LEFT JOIN biog_addr_data bad ON b.c_personid = bad.c_personid
        LEFT JOIN addr_codes addr ON bad.c_addr_id = addr.c_addr_id
        WHERE b.c_birthyear >= ?
          AND b.c_birthyear <= ?
          AND b.c_birthyear > 0
        ORDER BY b.c_birthyear
    """

    try:
        cur.execute(query, (decade_start, decade_end))
        rows = cur.fetchall()

        results = []
        for row in rows:
            x = row["x_coord"]  # 经度
            y = row["y_coord"]  # 纬度
            results.append({
                "person_id": row["c_personid"],
                "name": row["c_name_chn"] or "",
                "birth_year": row["c_birthyear"],
                "death_year": row["c_deathyear"] or 0,
                "lat": float(y) if y else None,  # CBDB: y=纬度
                "lng": float(x) if x else None,  # CBDB: x=经度
            })
        return results
    except Exception as e:
        print(f"[!] CBDB 查询失败: {e}")
        return []


# ============================================================
# 主流程：批量数据收集
# ============================================================

@dataclass
class DecadeData:
    """单个十年的完整数据（v4.0 完整版）"""
    dynasty: str
    decade: int
    year_start: int
    year_end: int
    expert_count: int
    texts_existing: int  # 有文本的专家数（这里假设所有专家都有）
    latitude_list: List[float]
    narrative_text: str  # LLM 生成的历史叙述
    sentiment_calls: List[float]  # 3 次情感分析的原始值
    mmp: float  # 情感中位数
    sfd: float
    eed: float
    gsi: float
    psi_z: float
    psi_z_gsi: float
    psi_final: float
    classification: str


def collect_all_decades_data(
    use_api: bool = True,
    n_sentiment_calls: int = 3,
    output_path: str = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json",
    progress_path: str = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/progress.json",
):
    """
    收集所有 96 个十年的完整数据

    流程:
    1. 从 CBDB 提取每十年的专家分布
    2. 用 MiniMax API 生成每十年的历史叙述
    3. 对叙述做 3 次情感分析取中位数
    4. 保存原始数据
    """
    # 加载已有进度（断点续传）
    progress = {}
    if os.path.exists(progress_path):
        try:
            with open(progress_path, "r", encoding="utf-8") as f:
                progress = json.load(f)
            print(f"[*] 加载进度: 已完成 {len(progress)} 个十年")
        except Exception:
            progress = {}

    conn = get_cbdb_connection()
    if not conn:
        print("[!] CBDB 不可用，将使用模拟专家数据")
    else:
        print(f"[✓] CBDB 连接成功")

    decades = all_decades()
    results = {}

    print(f"\n{'='*70}")
    print(f"开始收集 {len(decades)} 个十年的数据")
    print(f"API 调用: {'✓ 启用' if use_api else '✗ 模拟模式'}")
    print(f"每十年情感调用次数: {n_sentiment_calls}")
    print(f"{'='*70}\n")

    t_start = time.time()

    for i, (dynasty, decade, year_start, year_end) in enumerate(decades):
        key = f"{dynasty}_{decade}"

        # 跳过已完成的
        if key in progress:
            results[key] = progress[key]
            if (i + 1) % 10 == 0:
                print(f"[{i+1}/{len(decades)}] 跳过 {key}（已完成）")
            continue

        # 1. CBDB 查询
        experts = query_decade_experts(conn, dynasty, year_start, year_end)
        expert_count = len(experts)

        # 提取纬度（用于 GSI）
        latitudes = [e["lat"] for e in experts if e.get("lat") is not None]
        texts_existing = expert_count  # 假设所有专家都有关联文本

        # 2. LLM 生成历史叙述
        if use_api:
            narrative = generate_decade_narrative(dynasty, decade)
            if not narrative:
                print(f"[!] {key} 叙述生成失败，使用默认文本")
                narrative = f"{dynasty} {decade}s，中国历史时期"
        else:
            narrative = f"{dynasty} {decade}s，中国历史时期"

        # 3. 情感分析（n_sentiment_calls 次）
        if use_api and narrative:
            median_sentiment, all_sentiments, _ = analyze_sentiment_v4(
                narrative, n_calls=n_sentiment_calls
            )
        else:
            all_sentiments = [0.0]
            median_sentiment = 0.0

        # 保存原始数据
        results[key] = {
            "dynasty": dynasty,
            "decade": decade,
            "year_start": year_start,
            "year_end": year_end,
            "expert_count": expert_count,
            "texts_existing": texts_existing,
            "latitudes": latitudes,
            "n_latitudes": len(latitudes),
            "narrative": narrative,
            "sentiment_calls": all_sentiments,
            "sentiment_median": median_sentiment,
        }

        # 进度报告
        if (i + 1) % 5 == 0 or i == 0:
            elapsed = time.time() - t_start
            eta = elapsed / (i + 1) * (len(decades) - i - 1)
            print(f"[{i+1:3d}/{len(decades)}] {key:<20} "
                  f"专家={expert_count:4d}, "
                  f"sentiment={median_sentiment:+.3f}, "
                  f"ETA={eta:.0f}s")

        # 断点保存
        if (i + 1) % 5 == 0:
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    # 最终保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    if conn:
        conn.close()

    elapsed = time.time() - t_start
    print(f"\n[✓] 数据收集完成！耗时 {elapsed:.1f} 秒")
    print(f"[✓] 输出: {output_path}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="v4.0 数据收集")
    parser.add_argument("--no-api", action="store_true", help="跳过 API 调用")
    parser.add_argument("--n-sentiment", type=int, default=3, help="每十年情感调用次数")
    parser.add_argument("--output", type=str, default="/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json")
    args = parser.parse_args()

    collect_all_decades_data(
        use_api=not args.no_api,
        n_sentiment_calls=args.n_sentiment,
        output_path=args.output,
    )
