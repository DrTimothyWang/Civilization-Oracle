"""
Civilization-Oracle v4.0 - Phase 2: 3 次中位数重测
=================================================

v4.0 第二阶段：用每个十年 3 次调用取中位数重新跑 96 窗
- 验证 v4.0 第一次结果的稳定性
- 提供重测信度（test-retest reliability）
- 输出 v4.0 Phase 2 数据集
"""
import sys
import os
import json
import time
import re
import math
import statistics
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_pipeline_fast import DECADE_ANCHORS, all_decades

API_KEY = "sk-cp-OAw9279PXsSzR2zBY-Hd3jAip3I_E6oMYFVrhbqBj5ZPgEJ3LYuqSfFMxpypH04ohzLxBEDbadVpgEfgj4y8A6hQcpQhkj65rphGNylH5QSML8oAvUwYuq8"
MODEL = "MiniMax-M3"
BASE_URL = "https://api.minimaxi.com/v1"

PROMPT = """中国古代历史情感分析。

时期: {anchor}

请评估该时期社会氛围的情感极性，输出一个 [-1.0, 1.0] 的浮点数：
- -1.0 = 极度悲观（亡国/大乱）
- 0 = 中性
- +1.0 = 极度繁荣（盛世/中兴）

**只输出一个数字，不要其他文字。**"""


def call_m3(anchor, max_retries=3, temperature=0.7):
    """单次 API 调用"""
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": MODEL,
                        "messages": [{"role": "user", "content": PROMPT.format(anchor=anchor)}],
                        "max_tokens": 500,
                        "temperature": temperature,
                    }
                )
                if resp.status_code != 200:
                    time.sleep(0.5)
                    continue
                data = resp.json()
                content = data["choices"][0]["message"]["content"] or ""
                content_clean = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                match = re.search(r'-?\d+\.?\d*', content_clean)
                if match:
                    val = float(match.group())
                    return max(-1.0, min(1.0, val))
                time.sleep(0.3)
        except Exception:
            time.sleep(0.5)
    return None


def call_m3_3times(anchor):
    """3 次调用取中位数"""
    results = []
    temps = [0.5, 0.7, 0.9]
    for t in temps:
        r = call_m3(anchor, temperature=t)
        if r is not None:
            results.append(r)
        time.sleep(0.1)
    if not results:
        return 0.0, []
    return statistics.median(results), results


def run_phase2(input_path, output_path, max_workers=6):
    """每十年 3 次调用"""
    with open(input_path) as f:
        v4_data = json.load(f)

    def retest(key):
        dynasty, decade = key.rsplit("_", 1)
        decade = int(decade)
        anchor = DECADE_ANCHORS.get((dynasty, decade), f"{dynasty} {decade}s")
        median, calls = call_m3_3times(anchor)
        return key, median, calls

    print(f"开始 Phase 2 重测 96 窗 × 3 次...")
    t0 = time.time()
    results = {}
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(retest, k): k for k in v4_data.keys()}

        for future in as_completed(futures):
            key, median, calls = future.result()
            results[key] = {
                "sentiment_v1": v4_data[key]["sentiment"],
                "sentiment_v2_median": median,
                "sentiment_v2_calls": calls,
                "diff": abs(median - v4_data[key]["sentiment"]),
            }
            # 更新主数据
            v4_data[key]["sentiment"] = median
            v4_data[key]["sentiment_v1"] = results[key]["sentiment_v1"]
            v4_data[key]["sentiment_v2_calls"] = calls
            completed += 1

            if completed % 10 == 0 or completed == 96:
                elapsed = time.time() - t0
                eta = elapsed / completed * (96 - completed)
                # 计算重测信度
                diffs = [r["diff"] for r in results.values() if r["diff"] is not None]
                mean_diff = statistics.mean(diffs) if diffs else 0
                print(f"  [{completed:3d}/96] 耗时 {elapsed:.0f}s  "
                      f"ETA {eta:.0f}s  "
                      f"平均差异 {mean_diff:.3f}  "
                      f"最大 {max(diffs) if diffs else 0:.3f}")

    elapsed = time.time() - t0
    print(f"\n[✓] Phase 2 完成: {elapsed:.0f}s")

    # 计算重测信度（Pearson 相关系数）
    v1 = [r["sentiment_v1"] for r in results.values()]
    v2 = [r["sentiment_v2_median"] for r in results.values()]
    if len(v1) > 1:
        n = len(v1)
        mean_v1 = statistics.mean(v1)
        mean_v2 = statistics.mean(v2)
        cov = sum((a - mean_v1) * (b - mean_v2) for a, b in zip(v1, v2)) / n
        std_v1 = statistics.stdev(v1)
        std_v2 = statistics.stdev(v2)
        if std_v1 > 0 and std_v2 > 0:
            r = cov / (std_v1 * std_v2)
        else:
            r = 0
        print(f"  重测信度 (Pearson r): {r:.4f}")
        print(f"  平均差异: {statistics.mean([abs(a-b) for a,b in zip(v1, v2)]):.4f}")
        print(f"  最大差异: {max(abs(a-b) for a,b in zip(v1, v2)):.4f}")

    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(v4_data, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 保存: {output_path}")


if __name__ == "__main__":
    run_phase2(
        "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json",
        "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw_phase2.json",
        max_workers=6,
    )
