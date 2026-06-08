#!/usr/bin/env python3
"""
v6.0 阶段68: 金十数据每日自动拉取脚本
- 拉取财经日历 (本周)
- 拉取 8 关键词快讯
- 计算每日情绪 PSI
- 增量保存到 JSON Lines 文件
- 可用于 cron 每日执行
"""
import json
import statistics
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import os

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v6/data")
DAILY = OUT / "daily_jin10.jsonl"  # JSON Lines 增量


def call_mcp(tool, args):
    """调用金十 MCP"""
    result = subprocess.run(
        ["mavis", "mcp", "call", "jin10", tool, json.dumps(args)],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except:
        return None


POS = ["上涨", "涨停", "突破", "新高", "回暖", "复苏", "利好", "涨超", "增长", "强劲", "反弹", "宽松", "降准"]
NEG = ["暴跌", "熔断", "崩盘", "危机", "衰退", "下跌", "跌停", "重挫", "跳水", "恐慌", "利空", "下调", "降息", "加息"]


def compute_sentiment(content):
    pos = sum(1 for kw in POS if kw in content)
    neg = sum(1 for kw in NEG if kw in content)
    return pos, neg


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"=== {today} 金十数据每日拉取 ===\n")

    # 1. 财经日历
    print("[1/3] 财经日历...")
    cal_data = call_mcp("list_calendar", {})
    cal = cal_data.get("data", []) if cal_data else []
    high_star = [c for c in cal if int(c.get("star", 0)) >= 4]
    print(f"  本周日历: {len(cal)} 事件, Star≥4: {len(high_star)}")

    # 2. 快讯
    print("\n[2/3] 快讯 (8 关键词)...")
    all_flashes = []
    for kw in ["美股", "A股", "美联储", "欧央行", "原油", "黄金", "暴跌", "危机"]:
        d = call_mcp("search_flash", {"keyword": kw})
        if d and d.get("data"):
            items = d["data"].get("items", [])
            all_flashes.extend(items)
        print(f"  {kw}: {len(items) if d else 0} 条")
    # 去重
    seen = set()
    uniq = []
    for f in all_flashes:
        url = f.get("url", "")
        if url in seen:
            continue
        seen.add(url)
        uniq.append(f)
    print(f"  去重: {len(uniq)} 条")

    # 3. 情绪 PSI
    print("\n[3/3] 情绪 PSI...")
    daily = {}
    for f in uniq:
        t = f.get("time", "")[:10]
        c = f.get("content", "")
        if not t:
            continue
        if t not in daily:
            daily[t] = {"pos": 0, "neg": 0, "n_flashes": 0}
        p, n = compute_sentiment(c)
        daily[t]["pos"] += p
        daily[t]["neg"] += n
        daily[t]["n_flashes"] += 1
    for d in daily:
        daily[d]["sentiment"] = daily[d]["neg"] - daily[d]["pos"]

    # 4. 增量写入 JSONL
    record = {
        "date": today,
        "n_calendar": len(cal),
        "n_high_star": len(high_star),
        "n_flashes_unique": len(uniq),
        "daily_sentiment": daily,
        "high_star_events": [
            {k: c.get(k) for k in ["title", "pub_time", "actual", "consensus", "previous", "affect_txt", "star"]}
            for c in high_star[:10]
        ],
    }
    with open(DAILY, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"\n✅ 增量写入 {DAILY}")

    # 5. 加载最近 7 天数据
    if DAILY.exists():
        with open(DAILY, encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        recent = lines[-7:]
        print(f"\n最近 {len(recent)} 天情绪趋势:")
        for r in recent:
            avg_sent = statistics.mean([v["sentiment"] for v in r["daily_sentiment"].values()]) if r["daily_sentiment"] else 0
            print(f"  {r['date']}: {r['n_flashes_unique']} 快讯, 平均情绪 {avg_sent:+.1f}")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
