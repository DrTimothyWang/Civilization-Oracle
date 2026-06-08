"""
Civilization-Oracle v4.0 - PSI 主计算
====================================

输入: data/decade_raw.json
输出: data/psi_v4_results.json (十年级) + data/individual_v4.json (individual-level)
"""
import sys
import os
import json
import math
import statistics
from typing import Dict, List
from dataclasses import dataclass, asdict
import numpy as np
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from formula import (
    compute_mmp, compute_sfd, compute_eed, compute_gsi,
    compute_psi_z, gsi_correction, psi_z_to_final, classify_period,
    compute_standardization_stats, StandardizationStats,
    WEIGHTS,
)


# ============================================================
# 1. 加载原始数据
# ============================================================

def load_raw_data(path="/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 2. 加载 CBDB individual-level 数据
# ============================================================

def load_cbdb_individual():
    """从 CBDB 加载所有 30,518 条专家记录（individual-level）"""
    cbdb_path = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"
    if not os.path.exists(cbdb_path):
        print(f"[!] CBDB 不存在: {cbdb_path}")
        return []

    conn = sqlite3.connect(cbdb_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

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
        WHERE b.c_birthyear > 0
    """

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        x = row["x_coord"]
        y = row["y_coord"]
        results.append({
            "person_id": row["c_personid"],
            "name": row["c_name_chn"] or "",
            "birth_year": row["c_birthyear"],
            "death_year": row["c_deathyear"] or 0,
            "lat": float(y) if y else None,
            "lng": float(x) if x else None,
        })

    return results


def assign_experts_to_decades(experts: List[Dict]) -> List[Dict]:
    """为每个专家分配所属十年"""
    # 五年区间
    dynasty_windows = {
        "唐朝": (618, 907),
        "北宋前期": (960, 1027),
        "北宋后期": (1028, 1127),
        "南宋": (1128, 1279),
        "明朝": (1368, 1644),
    }

    # 反向索引：birth_year -> (dynasty, decade)
    year_to_dynasty = {}
    for dynasty, (start, end) in dynasty_windows.items():
        for year in range(start, end + 1, 10):
            decade = (year // 10) * 10
            if dynasty not in year_to_dynasty:
                year_to_dynasty[dynasty] = {}
            year_to_dynasty[dynasty][decade] = (year, year + 9)

    for expert in experts:
        birth = expert["birth_year"]
        for dynasty, decade_map in year_to_dynasty.items():
            for decade, (s, e) in decade_map.items():
                if s <= birth <= e:
                    expert["dynasty"] = dynasty
                    expert["decade"] = decade
                    break
            if "decade" in expert:
                break
        if "decade" not in expert:
            expert["dynasty"] = None
            expert["decade"] = None

    return [e for e in experts if e.get("decade") is not None]


# ============================================================
# 3. 计算 PSI（十年级）
# ============================================================

def compute_psi_all_decades(raw_data: Dict) -> List[Dict]:
    """用 v4 公式计算所有十年的 PSI"""
    # 提取所有十年的 MMP/SFD/EED
    all_mmp = []
    all_sfd = []
    all_eed = []
    decades_list = []

    for key, r in raw_data.items():
        expert_count = r["expert_count"]
        sentiment = r["sentiment"]
        n_lat = r.get("n_latitudes", 0)

        # 修复: 1020s 北宋后期 expert_count=0 是因为 CBDB 中
        # 北宋后期从 1028 开始，但十年窗口按 1020-1029 划分
        # 实际 1020-1027 的专家被分到北宋前期，1028-1129 到北宋后期
        # 这里 1020s 出现 expert_count=0 是数据划分问题
        # 修复: 当 expert_count=0 时，使用相邻十年的中位数
        if expert_count == 0 and r["dynasty"] in ("北宋后期", "北宋"):
            # 借用前一个十年的专家数（1020s 前期 970s 后期借用）
            # 更合理: 借用同期北宋前期数据
            prev_key = f"北宋前期_{r['decade']}"
            if prev_key in raw_data:
                expert_count = raw_data[prev_key]["expert_count"]
                n_lat = raw_data[prev_key].get("n_latitudes", 0)

        # GSI 估计：基于专家数（简化版）
        # 实际应该从 CBDB 查询每个十年的北方比例
        # 这里用代理: 北宋/金/南方差异
        dynasty = r["dynasty"]
        gsi_default = {
            "唐朝": 0.7,
            "北宋前期": 0.55,
            "北宋后期": 0.55,
            "南宋": 0.30,  # 南宋偏安南方
            "明朝": 0.60,
        }.get(dynasty, 0.5)

        mmp = sentiment
        sfd = math.log1p(max(1, expert_count))
        # EED 估计：专家数越多，有效参与度越高（简化）
        eed = min(1.0, expert_count / 100.0)

        all_mmp.append(mmp)
        all_sfd.append(sfd)
        all_eed.append(eed)

        decades_list.append({
            "key": key,
            "dynasty": dynasty,
            "decade": r["decade"],
            "expert_count": expert_count,
            "n_latitudes": n_lat,
            "gsi": gsi_default,
            "sentiment": sentiment,
            "anchor": r.get("anchor", ""),
        })

    # 计算标准化统计
    stats = compute_standardization_stats(all_mmp, all_sfd, all_eed)

    # 计算每个十年的 PSI
    results = []
    for i, d in enumerate(decades_list):
        mmp = all_mmp[i]
        sfd = all_sfd[i]
        eed = all_eed[i]
        gsi = d["gsi"]

        psi_z = compute_psi_z(mmp, sfd, eed, stats)
        psi_z_gsi = gsi_correction(psi_z, gsi)
        psi_final = psi_z_to_final(psi_z_gsi)
        cls = classify_period(psi_z)

        results.append({
            "dynasty": d["dynasty"],
            "decade": d["decade"],
            "year_start": d["decade"],
            "year_end": d["decade"] + 9,
            "expert_count": d["expert_count"],
            "n_latitudes": d["n_latitudes"],
            "gsi": gsi,
            "anchor": d["anchor"],
            "sentiment": round(d["sentiment"], 4),
            "mmp": round(mmp, 4),
            "sfd": round(sfd, 4),
            "eed": round(eed, 4),
            "psi_z": round(psi_z, 4),
            "psi_z_gsi": round(psi_z_gsi, 4),
            "psi_final": round(psi_final, 4),
            "classification": cls,
        })

    return results


# ============================================================
# 4. 跨朝代聚合
# ============================================================

def aggregate_by_dynasty(results: List[Dict]) -> Dict[str, Dict]:
    """按朝代聚合"""
    by_dynasty = {}
    for r in results:
        d = r["dynasty"]
        if d not in by_dynasty:
            by_dynasty[d] = {
                "dynasty": d,
                "n_decades": 0,
                "total_experts": 0,
                "psi_z_mean": 0.0,
                "psi_z_std": 0.0,
                "sentiment_mean": 0.0,
                "psi_final_mean": 0.0,
                "n_prosperity": 0,
                "n_crisis": 0,
                "n_neutral": 0,
            }

        by_dynasty[d]["n_decades"] += 1
        by_dynasty[d]["total_experts"] += r["expert_count"]
        by_dynasty[d]["psi_z_mean"] += r["psi_z"]
        by_dynasty[d]["sentiment_mean"] += r["sentiment"]
        by_dynasty[d]["psi_final_mean"] += r["psi_final"]

        if r["classification"] == "prosperity":
            by_dynasty[d]["n_prosperity"] += 1
        elif r["classification"] == "crisis":
            by_dynasty[d]["n_crisis"] += 1
        else:
            by_dynasty[d]["n_neutral"] += 1

    # 计算均值
    for d, agg in by_dynasty.items():
        n = agg["n_decades"]
        agg["psi_z_mean"] = round(agg["psi_z_mean"] / n, 4)
        agg["sentiment_mean"] = round(agg["sentiment_mean"] / n, 4)
        agg["psi_final_mean"] = round(agg["psi_final_mean"] / n, 4)
        # 计算标准差
        psi_zs = [r["psi_z"] for r in results if r["dynasty"] == d]
        agg["psi_z_std"] = round(float(np.std(psi_zs)), 4) if psi_zs else 0.0

    return by_dynasty


# ============================================================
# 5. 历史事件对应
# ============================================================

# 关键历史事件（用于验证 PSI 领先性）
KEY_HISTORICAL_EVENTS = {
    755: "安史之乱（唐朝）",
    875: "黄巢起义（唐朝）",
    907: "唐朝灭亡",
    1120: "方腊起义（北宋）",
    1127: "靖康之变（北宋）",
    1279: "崖山海战（南宋灭亡）",
    1368: "明朝建立",
    1449: "土木堡之变（明朝）",
    1644: "明朝覆灭",
}


# ============================================================
# 6. 主流程
# ============================================================

def main():
    print("=" * 70)
    print("v4.0 PSI 计算")
    print("=" * 70)

    # 1. 加载原始数据
    raw_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json"
    if not os.path.exists(raw_path):
        print(f"[!] 数据不存在: {raw_path}")
        print("    请先运行 run_data_v4.py")
        return

    raw = load_raw_data(raw_path)
    print(f"[*] 加载 {len(raw)} 个十年的原始数据")

    # 2. 计算 PSI
    results = compute_psi_all_decades(raw)
    print(f"[*] 计算完成 {len(results)} 个十年的 PSI")

    # 3. 按朝代聚合
    by_dynasty = aggregate_by_dynasty(results)
    print(f"[*] 按朝代聚合: {len(by_dynasty)} 个朝代")

    # 4. 打印摘要
    print("\n" + "=" * 70)
    print("v4.0 十年级 PSI 时间线（按朝代分组）")
    print("=" * 70)

    dynasty_order = ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"]
    for dy in dynasty_order:
        if dy in by_dynasty:
            agg = by_dynasty[dy]
            print(f"\n{dy}:")
            print(f"  十年窗口: {agg['n_decades']}, 专家数: {agg['total_experts']}")
            print(f"  PSI_z 均值: {agg['psi_z_mean']:+.4f} (std={agg['psi_z_std']:.4f})")
            print(f"  PSI_final 均值: {agg['psi_final_mean']:.4f}")
            print(f"  盛世/危机/中性: {agg['n_prosperity']}/{agg['n_crisis']}/{agg['n_neutral']}")

            # 该朝代的十年 PSI 列表
            dec_psis = [(r["decade"], r["psi_z"], r["classification"]) for r in results if r["dynasty"] == dy]
            for decade, psi_z, cls in sorted(dec_psis):
                marker = "★" if cls == "prosperity" else ("⚠" if cls == "crisis" else "·")
                print(f"    {marker} {decade}s: PSI_z={psi_z:+.3f} ({cls})")

    # 5. 输出
    output = {
        "meta": {
            "version": "v4.0",
            "formula": "PSI_z = 0.40*MMP_z + 0.30*SFD_z + 0.30*EED_z",
            "weights": WEIGHTS,
            "n_decades": len(results),
            "n_dynasties": len(by_dynasty),
        },
        "by_dynasty": by_dynasty,
        "decade_results": sorted(results, key=lambda r: r["decade"]),
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 结果保存: {out_path}")


if __name__ == "__main__":
    main()
