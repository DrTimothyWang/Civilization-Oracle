"""
Civilization-Oracle v4.0 - 极简并发数据收集
==========================================

策略:
- 1 次 API 调用 per 十年（节省时间）
- 5 个并发线程
- 自动重试
- 断点续传
"""
import sys
import os
import json
import sqlite3
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_pipeline_fast import (
    call_api_direct,
    DECADE_ANCHORS,
    all_decades,
    get_cbdb_data,
)


def process_decade_simple(args):
    """单次 API 调用"""
    dynasty, decade, expert_count, n_lat = args
    anchor = DECADE_ANCHORS.get((dynasty, decade), f"{dynasty} {decade}s")

    sentiment = call_api_direct(anchor, max_retries=3, temperature=0.7)

    return {
        "dynasty": dynasty,
        "decade": decade,
        "expert_count": expert_count,
        "n_latitudes": n_lat,
        "anchor": anchor,
        "sentiment": sentiment if sentiment is not None else 0.0,
        "success": sentiment is not None,
    }


def run(output_path, max_workers=8):
    cbdb_data = get_cbdb_data()
    if not cbdb_data:
        print("[!] CBDB 数据为空")
        return

    decades = all_decades()
    tasks = []
    for d, dec in decades:
        data = cbdb_data.get((d, dec), {"expert_count": 0, "latitudes": []})
        tasks.append((d, dec, data["expert_count"], len(data["latitudes"])))

    print(f"\n[*] 开始并发处理 {len(tasks)} 个十年 ({max_workers} workers)")
    t0 = time.time()

    results = {}
    success_count = 0
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_decade_simple, t): t for t in tasks}

        for future in as_completed(futures):
            r = future.result()
            key = f"{r['dynasty']}_{r['decade']}"
            results[key] = r
            completed += 1
            if r['success']:
                success_count += 1

            if completed % 5 == 0 or completed == len(tasks):
                elapsed = time.time() - t0
                eta = elapsed / completed * (len(tasks) - completed)
                print(f"  [{completed:3d}/{len(tasks)}] {key:<22} "
                      f"expert={r['expert_count']:4d} "
                      f"sent={r['sentiment']:+.3f} "
                      f"{'✓' if r['success'] else '✗'} "
                      f"ETA={eta:.0f}s")

    elapsed = time.time() - t0
    print(f"\n[✓] 完成 {len(results)} 个十年，成功 {success_count}/{len(results)}")
    print(f"[✓] 总耗时: {elapsed:.1f}s ({elapsed/len(results):.1f}s/十年)")

    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[✓] 保存: {output_path}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=str,
                        default="/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json")
    args = parser.parse_args()

    run(args.output, max_workers=args.workers)
