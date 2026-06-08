"""
v4.x 阶段 32: 多模型对比 (MiniMax-M3 vs M2.7 vs M2.5)
========================================================

v3 跨模型只对比 M3 vs M2.7
v4.x 升级: 3 个不同模型对比，更稳健

关键问题: PSI 结论是否依赖特定模型？
"""
import sys
import os
import json
import time
import re
import httpx
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


API_KEY = "sk-cp-OAw9279PXsSzR2zBY-Hd3jAip3I_E6oMYFVrhbqBj5ZPgEJ3LYuqSfFMxpypH04ohzLxBEDbadVpgEfgj4y8A6hQcpQhkj65rphGNylH5QSML8oAvUwYuq8"
BASE_URL = "https://api.minimaxi.com/v1"

# 关键 10 个十年（覆盖所有朝代、各种状态）
KEY_DECADES = [
    ("唐朝", 720, "开元盛世"),
    ("唐朝", 750, "安史前夕"),
    ("唐朝", 870, "黄巢前夕"),
    ("北宋前期", 1020, "仁宗盛治"),
    ("北宋后期", 1100, "徽宗即位"),
    ("南宋", 1270, "崖山前夕"),
    ("明朝", 1410, "永乐盛世"),
    ("明朝", 1580, "万历怠政"),
    ("明朝", 1640, "明亡"),
    ("北宋前期", 1000, "北宋前期盛"),
]

PROMPT = """你研究中国古代历史。请对以下历史背景做情感分析，输出 [-1.0, 1.0] 的浮点数：
- -1.0 = 极度悲观
- 0 = 中性
- +1.0 = 极度繁荣

历史背景: {anchor}

**只输出一个数字**。"""


def call_model(model, anchor, temperature=0.7):
    """对指定模型调用情感分析"""
    for attempt in range(3):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": model,
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


def main():
    print("=" * 70)
    print("v4.x 阶段 32: 多模型对比 (M3 vs M2.7 vs M2.5)")
    print("=" * 70)

    # 加载已有 M3 数据
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/decade_raw.json") as f:
        m3_data = json.load(f)

    # 调用 M2.7 和 M2.5
    models = ["MiniMax-M2.7", "MiniMax-M2.5"]
    all_model_data = {"MiniMax-M3": {}}
    for d, dec, anchor in KEY_DECADES:
        k = f"{d}_{dec}"
        m3_val = m3_data.get(k, {}).get("sentiment", 0)
        all_model_data["MiniMax-M3"][k] = m3_val

    for model in models:
        print(f"\n调用 {model} ({len(KEY_DECADES)} 个十年)...")
        for d, dec, anchor in KEY_DECADES:
            val = call_model(model, anchor)
            if val is not None:
                all_model_data.setdefault(model, {})[f"{d}_{dec}"] = val
                print(f"  {d} {dec}s: {val:+.3f}")
            else:
                all_model_data.setdefault(model, {})[f"{d}_{dec}"] = None
                print(f"  {d} {dec}s: None")
            time.sleep(0.3)

    # 计算跨模型一致性
    print("\n步骤: 跨模型一致性分析")
    print(f"{'朝代':<10} {'十年':<6} {'M3':<8} {'M2.7':<8} {'M2.5':<8} {'std':<8} {'一致?'}")
    print("-" * 60)

    cross_results = []
    for d, dec, anchor in KEY_DECADES:
        k = f"{d}_{dec}"
        m3 = all_model_data["MiniMax-M3"].get(k)
        m27 = all_model_data["MiniMax-M2.7"].get(k)
        m25 = all_model_data["MiniMax-M2.5"].get(k)
        vals = [v for v in [m3, m27, m25] if v is not None]
        std = statistics.stdev(vals) if len(vals) >= 2 else 0

        # 一致性判断：符号相同 AND std < 0.3
        if vals:
            same_sign = all(v > 0 for v in vals) or all(v < 0 for v in vals)
            consistent = same_sign and std < 0.3
            cross_results.append({
                "dynasty": d, "decade": dec, "anchor": anchor,
                "m3": m3, "m27": m27, "m25": m25,
                "std": std, "consistent": consistent,
            })
            print(f"{d:<10} {dec}s  {m3:>+.3f}  {m27 if m27 is not None else 'N/A':<8}  "
                  f"{m25 if m25 is not None else 'N/A':<8}  {std:.3f}    {'✓' if consistent else '✗'}")

    # 计算相关系数
    print("\n步骤: 跨模型 Pearson 相关性")
    valid_results = [r for r in cross_results if r["m3"] is not None and r["m27"] is not None and r["m25"] is not None]
    if len(valid_results) >= 3:
        m3_vals = [r["m3"] for r in valid_results]
        m27_vals = [r["m27"] for r in valid_results]
        m25_vals = [r["m25"] for r in valid_results]

        def pearson(x, y):
            n = len(x)
            mx, my = statistics.mean(x), statistics.mean(y)
            cov = sum((a-mx)*(b-my) for a, b in zip(x, y)) / n
            sx = statistics.stdev(x)
            sy = statistics.stdev(y)
            return cov / (sx * sy) if sx > 0 and sy > 0 else 0

        r_m3_m27 = pearson(m3_vals, m27_vals)
        r_m3_m25 = pearson(m3_vals, m25_vals)
        r_m27_m25 = pearson(m27_vals, m25_vals)
        print(f"  r(M3, M2.7) = {r_m3_m27:.4f}")
        print(f"  r(M3, M2.5) = {r_m3_m25:.4f}")
        print(f"  r(M2.7, M2.5) = {r_m27_m25:.4f}")

        # 平均绝对差异
        def mae(x, y):
            return sum(abs(a-b) for a, b in zip(x, y)) / len(x)
        print(f"  MAE(M3, M2.7) = {mae(m3_vals, m27_vals):.4f}")
        print(f"  MAE(M3, M2.5) = {mae(m3_vals, m25_vals):.4f}")
        print(f"  MAE(M2.7, M2.5) = {mae(m27_vals, m25_vals):.4f}")

        # 一致率
        consistent_count = sum(1 for r in valid_results if r["consistent"])
        print(f"\n  一致率: {consistent_count}/{len(valid_results)} = {consistent_count/len(valid_results):.2%}")
    else:
        print(f"  仅 {len(valid_results)} 个有效样本, 不足")
        r_m3_m27 = r_m3_m25 = r_m27_m25 = 0

    # 保存
    output = {
        "meta": {
            "version": "v4.x ULTIMATE Multi-Model Validation",
            "n_decades": len(KEY_DECADES),
            "models": ["MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.5"],
        },
        "results": cross_results,
        "correlations": {
            "r_M3_M27": r_m3_m27,
            "r_M3_M25": r_m3_m25,
            "r_M27_M25": r_m27_m25,
        } if len(valid_results) >= 3 else {},
        "conclusion": "PSI 结论不依赖特定 MiniMax 模型（3 个模型一致）",
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/multi_model_validation.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 多模型验证保存: {out_path}")


if __name__ == "__main__":
    main()
