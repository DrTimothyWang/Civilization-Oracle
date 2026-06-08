"""
修复版：重跑失败的十年，用更强 retry + 备选 prompt
"""
import sys
import os
import json
import time
import re
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_pipeline_fast import DECADE_ANCHORS, all_decades

API_KEY = "sk-cp-OAw9279PXsSzR2zBY-Hd3jAip3I_E6oMYFVrhbqBj5ZPgEJ3LYuqSfFMxpypH04ohzLxBEDbadVpgEfgj4y8A6hQcpQhkj65rphGNylH5QSML8oAvUwYuq8"
BASE_URL = "https://api.minimaxi.com/v1"

# 备选 prompt 1: 极简短
PROMPT_V2 = """中国历史情感分析。请对"{anchor}"这段历史时期的社会氛围打分（-1.0 极度悲观，0 中性，+1.0 极度繁荣）。只输出数字。"""

# 备选 prompt 2: 关键词式
PROMPT_V3 = "为以下历史时期打分（-1到1）: {short}\n只输出数字:"


def call_v2(anchor: str, max_retries: int = 5) -> float:
    """极简 prompt 版本"""
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "MiniMax-M2.7-highspeed",
                        "messages": [{"role": "user", "content": PROMPT_V2.format(anchor=anchor)}],
                        "max_tokens": 800,
                        "temperature": 0.7,
                    }
                )
                if resp.status_code != 200:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                data = resp.json()
                content = data["choices"][0]["message"]["content"] or ""
                # 提取数字
                content_clean = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                match = re.search(r'-?\d+\.?\d*', content_clean)
                if match:
                    val = float(match.group())
                    return max(-1.0, min(1.0, val))
                time.sleep(0.5)
        except Exception as e:
            time.sleep(1.0)
    return None


def call_v3(anchor: str, max_retries: int = 5) -> float:
    """关键词 prompt 版本"""
    # 提取关键词
    short = anchor.split("，")[0].split(",")[0][:20]
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "MiniMax-M2.7-highspeed",
                        "messages": [{"role": "user", "content": PROMPT_V3.format(short=short)}],
                        "max_tokens": 600,
                        "temperature": 0.8,
                    }
                )
                if resp.status_code != 200:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                data = resp.json()
                content = data["choices"][0]["message"]["content"] or ""
                content_clean = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                match = re.search(r'-?\d+\.?\d*', content_clean)
                if match:
                    val = float(match.group())
                    return max(-1.0, min(1.0, val))
                time.sleep(0.5)
        except Exception as e:
            time.sleep(1.0)
    return None


def fix_failed_decades(input_path, output_path, max_workers=4):
    with open(input_path) as f:
        data = json.load(f)

    failed = [k for k, v in data.items() if v.get("sentiment", 0) == 0]
    print(f"失败: {len(failed)}/{len(data)}")

    if not failed:
        return data

    # 准备修复任务
    def fix_one(key):
        dynasty, decade = key.rsplit("_", 1)
        decade = int(decade)
        anchor = DECADE_ANCHORS.get((dynasty, decade), f"{dynasty} {decade}s")

        # 尝试 v2
        result = call_v2(anchor)
        if result is not None:
            return key, result, "v2"

        # 备选 v3
        result = call_v3(anchor)
        if result is not None:
            return key, result, "v3"

        return key, None, "failed"

    print(f"开始重试 {len(failed)} 个失败的...")
    t0 = time.time()
    completed = 0
    successes = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fix_one, k): k for k in failed}

        for future in as_completed(futures):
            key, result, method = future.result()
            completed += 1
            if result is not None:
                # 保留原始的 expert_count 等，只更新 sentiment
                data[key]["sentiment"] = result
                data[key]["sentiment_method"] = method
                data[key]["success"] = True
                successes += 1

            if completed % 5 == 0 or completed == len(failed):
                elapsed = time.time() - t0
                eta = elapsed / completed * (len(failed) - completed) if completed > 0 else 0
                print(f"  [{completed:3d}/{len(failed)}] {key:<22} "
                      f"result={result if result is not None else '✗'} "
                      f"({method}) ETA={eta:.0f}s")

    elapsed = time.time() - t0
    print(f"\n[✓] 修复完成: 成功 {successes}/{len(failed)}, 耗时 {elapsed:.1f}s")

    # 重新计算成功率
    total_success = sum(1 for v in data.values() if v.get("sentiment", 0) != 0 or v.get("success"))
    print(f"[✓] 总成功率: {total_success}/{len(data)}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] 保存: {output_path}")

    return data


if __name__ == "__main__":
    fix_failed_decades(
        "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json",
        "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw_fixed.json",
        max_workers=4,
    )
