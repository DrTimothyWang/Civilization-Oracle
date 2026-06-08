"""
Civilization-Oracle v4.0 - 高效批量数据收集
==========================================

优化策略:
1. 跳过叙述生成，直接用历史事件关键词作为分析对象（节省 50% 时间）
2. 用模糊 prompt + 0.9 temperature 让 LLM 给出有噪声的合理回答
3. 用 threading 并发加速（10 个并发）
4. 断点续传

v3.0 的关键问题: mock 数据太规整
v4.0 的修复: 真实 LLM 调用 + 模糊 prompt + 多次调用取中位数
"""
import sys
import os
import json
import sqlite3
import time
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx

# 重新定义 API key
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
MINIMAX_MODEL = "MiniMax-M2.7-highspeed"
API_KEY = "sk-cp-OAw9279PXsSzR2zBY-Hd3jAip3I_E6oMYFVrhbqBj5ZPgEJ3LYuqSfFMxpypH04ohzLxBEDbadVpgEfgj4y8A6hQcpQhkj65rphGNylH5QSML8oAvUwYuq8"


# ============================================================
# API 调用（精简版，去掉 think 标签 + 重试）
# ============================================================

# 极简 prompt：直接问情感分数，不要任何思考
DIRECT_SENTIMENT_PROMPT = """你研究中国古代历史。请阅读以下历史背景，用一个 [-1, 1] 之间的浮点数评估该时期社会氛围的情感极性。

-1 = 极度悲观绝望（如亡国前夕、严重战乱、大饥荒）
-0.5 = 明显负面（如藩镇割据、党争激烈）
0 = 中性
+0.5 = 明显正面（如中兴、改革有成）
+1 = 极度繁荣（如开元盛世、康乾盛世）

**只输出一个浮点数（保留2-3位小数），不要任何其他文字、解释或前缀。**

历史背景: {anchor}"""


def call_api_direct(anchor: str, max_retries: int = 2, temperature: float = 0.7) -> Optional[float]:
    """直接调用 API 获取情感分数"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MINIMAX_MODEL,
        "messages": [
            {"role": "user", "content": DIRECT_SENTIMENT_PROMPT.format(anchor=anchor)}
        ],
        "max_tokens": 600,  # 足够 thinking 模式
        "temperature": temperature,
    }

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"{MINIMAX_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )

                if resp.status_code != 200:
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                        continue
                    return None

                data = resp.json()
                content = data["choices"][0]["message"]["content"] or ""

                # 剥离 think 标签
                content_clean = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

                # 提取最后一个浮点数
                # 模式1: 整行就是数字
                # 模式2: 文本末尾有数字
                lines = [l.strip() for l in content_clean.split('\n') if l.strip()]
                if not lines:
                    return None

                last_line = lines[-1]

                # 尝试提取数字（包括负号、小数点）
                match = re.search(r'-?\d+\.?\d*', last_line)
                if match:
                    try:
                        val = float(match.group())
                        # 限制到 [-1, 1]
                        return max(-1.0, min(1.0, val))
                    except ValueError:
                        pass

                return None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue

    return None


def call_api_multi(anchor: str, n_calls: int = 3) -> List[float]:
    """多次调用取所有有效结果"""
    results = []
    temps = [0.5, 0.8, 1.0, 0.6, 0.9][:n_calls]

    for temp in temps:
        val = call_api_direct(anchor, temperature=temp)
        if val is not None:
            results.append(val)
        time.sleep(0.15)  # 防限流

    return results


# ============================================================
# 历史事件锚点（每个十年的简短描述）
# ============================================================

DECADE_ANCHORS = {
    # 唐朝
    ("唐朝", 610): "隋末战乱后，唐王朝建立初期，社会百废待兴",
    ("唐朝", 620): "贞观之治初期，唐太宗即位，励精图治",
    ("唐朝", 630): "贞观盛世，对外征服突厥，对内休养生息",
    ("唐朝", 640): "高宗前期，永徽之治延续，朝野清明",
    ("唐朝", 650): "高宗后期，朝政开始出现权力斗争",
    ("唐朝", 660): "武则天临朝称制，政治格局剧变",
    ("唐朝", 670): "武则天称帝前夜，徐敬业起兵反武",
    ("唐朝", 680): "武则天改唐为周，女皇政治确立",
    ("唐朝", 690): "武周革命完成，神都洛阳政治动荡",
    ("唐朝", 700): "武周末年，神龙政变酝酿",
    ("唐朝", 710): "开元盛世前期，玄宗即位初期",
    ("唐朝", 720): "开元全盛，海内富庶，百姓乐业",
    ("唐朝", 730): "玄宗后期，朝政渐荒，边将势大",
    ("唐朝", 740): "天宝盛世表象下，安禄山崛起",
    ("唐朝", 750): "安史之乱爆发前夕",
    ("唐朝", 760): "安史之乱，藩镇割据加剧",
    ("唐朝", 770): "代宗朝，吐蕃入侵京师",
    ("唐朝", 780): "德宗朝，藩镇跋扈",
    ("唐朝", 790): "德宗后期，四镇之乱",
    ("唐朝", 800): "元和中兴，宪宗削藩有成",
    ("唐朝", 810): "元和后期，党争初起",
    ("唐朝", 820): "穆宗朝，河北再乱",
    ("唐朝", 830): "文宗朝，甘露之变",
    ("唐朝", 840): "武宗灭佛，会昌中兴",
    ("唐朝", 850): "宣宗朝，大中之治",
    ("唐朝", 860): "懿宗朝，浙东裘甫起义",
    ("唐朝", 870): "黄巢起义，天下大乱",
    ("唐朝", 880): "黄巢入长安，唐室衰微",
    ("唐朝", 890): "唐末藩镇混战，名义唐朝实已不存",
    ("唐朝", 900): "五代十国前夕",
    ("唐朝", 910): "后梁取代，唐朝正式灭亡",
    # 北宋前期
    ("北宋前期", 950): "五代十国末期，北方政权更替",
    ("北宋前期", 960): "陈桥兵变，赵匡胤建立北宋",
    ("北宋前期", 970): "太祖统一，灭南唐",
    ("北宋前期", 980): "太宗即位，太平兴国",
    ("北宋前期", 990): "太宗后期，党争初现",
    ("北宋前期", 1000): "真宗朝，咸平之治",
    ("北宋前期", 1010): "真宗朝后期，澶渊之盟后",
    ("北宋前期", 1020): "仁宗即位初，朝野清明",
    # 北宋后期
    ("北宋后期", 1020): "北宋后期起点，仁宗亲政",
    ("北宋后期", 1030): "仁宗中期，党争加剧",
    ("北宋后期", 1040): "庆历新政失败",
    ("北宋后期", 1050): "仁宗晚年，朝政平稳",
    ("北宋后期", 1060): "神宗即位，王安石变法前",
    ("北宋后期", 1070): "熙宁变法，新旧党争激化",
    ("北宋后期", 1080): "元丰年间，新法推行",
    ("北宋后期", 1090): "元祐更化，司马光执政",
    ("北宋后期", 1100): "徽宗即位，蔡京当权",
    ("北宋后期", 1110): "花石纲扰民，方腊起义",
    ("北宋后期", 1120): "宋金海上之盟前夕",
    # 南宋
    ("南宋", 1120): "南宋初建，高宗即位",
    ("南宋", 1130): "建炎南渡，秦桧初相",
    ("南宋", 1140): "绍兴和议，岳飞被害",
    ("南宋", 1150): "秦桧专权后期",
    ("南宋", 1160): "孝宗即位，隆兴北伐",
    ("南宋", 1170): "孝宗后期，理学兴起",
    ("南宋", 1180): "光宗朝，孝宗忧死",
    ("南宋", 1190): "宁宗朝，庆元党禁",
    ("南宋", 1200): "韩侂胄北伐失败",
    ("南宋", 1210): "史弥远专权",
    ("南宋", 1220): "理宗朝初，蒙古崛起",
    ("南宋", 1230): "蒙古南侵，襄阳告急",
    ("南宋", 1240): "端平入洛失败",
    ("南宋", 1250): "贾似道误国",
    ("南宋", 1260): "蒙古建国号，攻宋加剧",
    ("南宋", 1270): "崖山前夕，宋室将亡",
    ("南宋", 1280): "元朝统一，南宋亡",
    # 明朝
    ("明朝", 1360): "元末农民起义，朱元璋崛起",
    ("明朝", 1370): "洪武开国，颁行律令",
    ("明朝", 1380): "胡惟庸案，废丞相",
    ("明朝", 1390): "锦衣卫设立，特务政治",
    ("明朝", 1400): "靖难之役，建文帝出亡",
    ("明朝", 1410): "永乐盛世，郑和下西洋",
    ("明朝", 1420): "永乐迁都北京",
    ("明朝", 1430): "仁宣之治，明朝黄金期",
    ("明朝", 1440): "土木堡之变前夕",
    ("明朝", 1450): "北京保卫战，景泰帝",
    ("明朝", 1460): "成化朝，宪宗犁庭",
    ("明朝", 1470): "弘治中兴",
    ("明朝", 1480): "弘治晚期",
    ("明朝", 1490): "武宗朝，荒政乱政",
    ("明朝", 1500): "正德晚期",
    ("明朝", 1510): "嘉靖初期，大礼议",
    ("明朝", 1520): "嘉靖中期，壬寅宫变",
    ("明朝", 1530): "嘉靖中期，倭患初起",
    ("明朝", 1540): "嘉靖中后期，严嵩专权",
    ("明朝", 1550): "庚戌之变，倭患加剧",
    ("明朝", 1560): "隆庆开关，俺答封贡",
    ("明朝", 1570): "万历初期，张居正改革",
    ("明朝", 1580): "张居正去世，万历怠政",
    ("明朝", 1590): "万历中期，党争再起",
    ("明朝", 1600): "万历晚期，矿税之祸",
    ("明朝", 1610): "万历后期，三大征",
    ("明朝", 1620): "天启朝，阉党专权",
    ("明朝", 1630): "崇祯初，农民起义",
    ("明朝", 1640): "明末崇祯帝自缢，明亡",
}


def all_decades() -> List[Tuple[str, int]]:
    """返回所有 96 个十年窗口"""
    decades = []
    # 唐朝
    for d in range(610, 920, 10):
        decades.append(("唐朝", d))
    # 北宋前期
    for d in range(950, 1030, 10):
        decades.append(("北宋前期", d))
    # 北宋后期
    for d in range(1020, 1130, 10):
        decades.append(("北宋后期", d))
    # 南宋
    for d in range(1120, 1290, 10):
        decades.append(("南宋", d))
    # 明朝
    for d in range(1360, 1650, 10):
        decades.append(("明朝", d))
    return decades


# ============================================================
# CBDB 数据接入
# ============================================================

CBDB_PATH = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"


def get_cbdb_data():
    """从 CBDB 提取所有 96 个十年的专家分布和地理信息"""
    if not os.path.exists(CBDB_PATH):
        print(f"[!] CBDB 数据库不存在: {CBDB_PATH}")
        return {}

    conn = sqlite3.connect(CBDB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 一次性提取所有需要的字段
    query = """
        SELECT
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

    print("[*] 加载 CBDB 全表...")
    t0 = time.time()
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except Exception as e:
        print(f"[!] CBDB 查询失败: {e}")
        return {}
    print(f"[✓] CBDB 加载完成: {len(rows)} 条记录，耗时 {time.time()-t0:.1f}s")

    conn.close()

    # 按十年窗口分组
    decade_data = {}
    decades_list = all_decades()

    # 构建 decade -> (year_start, year_end) 映射
    decade_range = {}
    for dynasty, decade in decades_list:
        decade_range[(dynasty, decade)] = (decade, decade + 9)

    # 初始化
    for dynasty, decade in decades_list:
        decade_data[(dynasty, decade)] = {
            "expert_count": 0,
            "latitudes": [],
        }

    # 分配
    for row in rows:
        birth = row["c_birthyear"]
        x = row["x_coord"]
        y = row["y_coord"]
        lat = float(y) if y else None

        for (dynasty, decade), (start, end) in decade_range.items():
            if start <= birth <= end:
                decade_data[(dynasty, decade)]["expert_count"] += 1
                if lat is not None:
                    decade_data[(dynasty, decade)]["latitudes"].append(lat)
                break  # 一个专家只属于一个十年（按生年）

    return decade_data


# ============================================================
# 并发批量调用
# ============================================================

def process_one_decade(args):
    """处理单个十年"""
    dynasty, decade, expert_count, latitudes = args
    key = (dynasty, decade)
    anchor = DECADE_ANCHORS.get(key, f"{dynasty} {decade}s")

    # 3 次调用取中位数
    sentiments = call_api_multi(anchor, n_calls=3)

    if sentiments:
        import statistics
        median_sent = statistics.median(sentiments)
    else:
        median_sent = 0.0

    return {
        "dynasty": dynasty,
        "decade": decade,
        "expert_count": expert_count,
        "n_latitudes": len(latitudes),
        "anchor": anchor,
        "sentiment_calls": sentiments,
        "sentiment_median": median_sent,
    }


def run_batch(cbdb_data, max_workers=5, output_path=None):
    """并发批量处理所有十年"""
    decades = all_decades()

    # 准备参数
    tasks = []
    for dynasty, decade in decades:
        key = (dynasty, decade)
        data = cbdb_data.get(key, {"expert_count": 0, "latitudes": []})
        tasks.append((
            dynasty,
            decade,
            data["expert_count"],
            data["latitudes"],
        ))

    print(f"\n[*] 开始并发批量处理 {len(tasks)} 个十年（{max_workers} workers）...")

    results = {}
    t_start = time.time()
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(process_one_decade, task): task for task in tasks
        }

        for future in as_completed(future_to_task):
            result = future.result()
            key = (result["dynasty"], result["decade"])
            results[key] = result
            completed += 1

            if completed % 5 == 0 or completed == len(tasks):
                elapsed = time.time() - t_start
                eta = elapsed / completed * (len(tasks) - completed)
                print(f"  [{completed:3d}/{len(tasks)}] "
                      f"{result['dynasty']:<8} {result['decade']}s "
                      f"专家={result['expert_count']:4d} "
                      f"sentiment={result['sentiment_median']:+.3f} "
                      f"calls={len(result['sentiment_calls'])} "
                      f"ETA={eta:.0f}s")

    elapsed = time.time() - t_start
    print(f"\n[✓] 完成 {len(results)} 个十年，总耗时 {elapsed:.1f}s")
    print(f"  平均每十年: {elapsed/len(results):.1f}s")

    # 保存
    if output_path:
        # 转换 key 为字符串
        out = {}
        for (d, dec), r in results.items():
            out[f"{d}_{dec}"] = r
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"[✓] 保存到: {output_path}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="v4.0 高效数据收集")
    parser.add_argument("--workers", type=int, default=5, help="并发数")
    parser.add_argument("--output", type=str,
                        default="/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json")
    args = parser.parse_args()

    # 1. 加载 CBDB
    cbdb_data = get_cbdb_data()
    if not cbdb_data:
        print("[!] 无 CBDB 数据，使用空数据")
        cbdb_data = {(d, dec): {"expert_count": 0, "latitudes": []}
                     for d, dec in all_decades()}

    # 2. 并发批量调用 API
    results = run_batch(cbdb_data, max_workers=args.workers, output_path=args.output)
