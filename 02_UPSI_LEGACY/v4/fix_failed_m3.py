"""
修复版 v2：使用 MiniMax-M3 模型 + 更激进 retry
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
MODEL = "MiniMax-M3"  # 新模型，更稳定

# 极简 prompt：M3 应该不需要 thinking
PROMPT = """中国古代历史情感分析。

时期: {anchor}

请评估该时期社会氛围的情感极性，输出一个 [-1.0, 1.0] 的浮点数：
- -1.0 = 极度悲观（亡国/大乱）
- 0 = 中性
- +1.0 = 极度繁荣（盛世/中兴）

**只输出一个数字，不要其他文字。**"""


def call_m3(anchor: str, max_retries: int = 5) -> float:
    """使用 MiniMax-M3"""
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
                        "temperature": 0.7,
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


def fix_failed(input_path, output_path, max_workers=6):
    with open(input_path) as f:
        data = json.load(f)

    failed = [k for k, v in data.items() if v.get("sentiment", 0) == 0]
    print(f"需重试: {len(failed)}/{len(data)}")
    print(f"使用模型: {MODEL}")

    def fix_one(key):
        dynasty, decade = key.rsplit("_", 1)
        decade = int(decade)
        anchor = DECADE_ANCHORS.get((dynasty, decade), f"{dynasty} {decade}s")
        result = call_m3(anchor)
        return key, result

    print(f"\n开始重试...")
    t0 = time.time()
    completed = 0
    successes = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fix_one, k): k for k in failed}

        for future in as_completed(futures):
            key, result = future.result()
            completed += 1
            if result is not None:
                data[key]["sentiment"] = result
                data[key]["sentiment_method"] = "MiniMax-M3"
                data[key]["success"] = True
                successes += 1

            if completed % 5 == 0 or completed == len(failed):
                elapsed = time.time() - t0
                eta = elapsed / completed * (len(failed) - completed) if completed > 0 else 0
                print(f"  [{completed:3d}/{len(failed)}] {key:<22} "
                      f"sent={result if result is not None else '✗'} "
                      f"ETA={eta:.0f}s")

    elapsed = time.time() - t0
    print(f"\n[✓] 修复完成: 成功 {successes}/{len(failed)}, 耗时 {elapsed:.1f}s")

    total_success = sum(1 for v in data.values() if v.get("sentiment", 0) != 0 or v.get("success"))
    print(f"[✓] 总成功率: {total_success}/{len(data)}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] 保存: {output_path}")

    return data


if __name__ == "__main__":
    fix_failed(
        "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json",
        "/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw_fixed.json",
        max_workers=6,
    )
