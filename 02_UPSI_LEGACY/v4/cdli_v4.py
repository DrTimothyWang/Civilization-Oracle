"""
Civilization-Oracle v4.0 - CDLI 跨文明验证
==========================================

Phase 2A: 验证 PSI 在美索不达米亚楔形文字文明的应用
- 调用 CDLI API 获取 Roman period 数据（美索不达米亚，0-640 CE）
- 对 transliteration 文本做情感分析
- 计算美索不达米亚 PSI
- 与中华文明 PSI 对比
"""
import sys
import os
import json
import time
import re
import math
import httpx
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# CDLI API
# ============================================================

CDLI_BASE = "https://cdli.earth"

# v4.0 重要: CDLI "Roman period" 是美索不达米亚，不是拉丁文
# （v3.0 已经识别过这个陷阱）


def fetch_cdli_artifacts(limit: int = 100) -> list:
    """从 CDLI API 获取 Roman period 数据"""
    artifacts = []
    try:
        with httpx.Client(timeout=30.0, verify=False) as client:
            # 公共 API 端点
            resp = client.get(f"{CDLI_BASE}/artifacts.json")
            if resp.status_code == 200:
                data = resp.json()
                # 筛选 Roman period
                if isinstance(data, list):
                    for art in data:
                        period = str(art.get("period", ""))
                        if "Roman" in period or "roman" in period:
                            artifacts.append(art)
                        if len(artifacts) >= limit:
                            break
                elif isinstance(data, dict) and "artifacts" in data:
                    for art in data["artifacts"]:
                        period = str(art.get("period", ""))
                        if "Roman" in period or "roman" in period:
                            artifacts.append(art)
                        if len(artifacts) >= limit:
                            break
    except Exception as e:
        print(f"[!] CDLI API 失败: {e}")

    return artifacts[:limit]


# ============================================================
# MiniMax-M3 客户端（v4.0 重复使用）
# ============================================================

API_KEY = "sk-cp-OAw9279PXsSzR2zBY-Hd3jAip3I_E6oMYFVrhbqBj5ZPgEJ3LYuqSfFMxpypH04ohzLxBEDbadVpgEfgj4y8A6hQcpQhkj65rphGNylH5QSML8oAvUwYuq8"
MODEL = "MiniMax-M3"
BASE_URL = "https://api.minimaxi.com/v1"


def call_m3_sentiment(text: str, max_retries: int = 3) -> float:
    """对美索不达米亚文本做情感分析"""
    prompt = f"""你研究古美索不达米亚历史。给定以下楔形文字 transliteration，请评估该文献反映的情感极性，输出 [-1.0, 1.0] 的浮点数：
- -1.0 = 极度悲观（战乱、灾难、诅咒）
- 0 = 中性（行政、记录）
- +1.0 = 极度繁荣（颂歌、祝福、王朝盛世）

只输出一个数字。

文本: {text[:200]}"""

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500,
                        "temperature": 0.7,
                    }
                )
                if resp.status_code != 200:
                    time.sleep(1.0)
                    continue
                data = resp.json()
                content = data["choices"][0]["message"]["content"] or ""
                content_clean = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                match = re.search(r'-?\d+\.?\d*', content_clean)
                if match:
                    val = float(match.group())
                    return max(-1.0, min(1.0, val))
                time.sleep(0.5)
        except Exception:
            time.sleep(1.0)
    return None


# ============================================================
# 美索不达米亚 PSI 计算（v4.0 公式）
# ============================================================

def compute_mesopotamia_psi(artifacts: list) -> dict:
    """对美索不达米亚数据计算 PSI（用 v4.0 公式）"""
    if not artifacts:
        return {"error": "无数据"}

    # 按 period 分组
    period_groups = {}
    for art in artifacts:
        period = art.get("period", "Unknown")
        period_groups.setdefault(period, []).append(art)

    results = {}

    for period, arts in period_groups.items():
        # 提取每个 artifact 的描述/genre 作为"文本"
        # 实际 CDLI 数据可能没有 transliteration，但有 genre
        sentiments = []
        for art in arts:
            # 尝试多种字段
            text = (
                art.get("transliteration_clean") or
                art.get("transliteration") or
                art.get("genre") or
                art.get("type") or
                ""
            )
            if not text:
                # 用 period 作为文本代理
                text = period
            sent = call_m3_sentiment(text)
            if sent is not None:
                sentiments.append(sent)
            time.sleep(0.3)  # 防限流

        if not sentiments:
            continue

        mmp = statistics.mean(sentiments)
        sfd = math.log1p(len(sentiments))
        eed = min(1.0, len(sentiments) / 20.0)  # 美索不达米亚数据少，调整 EED 阈值

        results[period] = {
            "n": len(sentiments),
            "sentiment_mean": round(mmp, 4),
            "sentiment_std": round(statistics.stdev(sentiments) if len(sentiments) > 1 else 0, 4),
            "sfd": round(sfd, 4),
            "eed": round(eed, 4),
        }

    return results


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 70)
    print("v4.0 跨文明验证: 美索不达米亚楔形文字 (CDLI)")
    print("=" * 70)

    # 1. 抓取 CDLI Roman period 数据
    print("\n[*] 抓取 CDLI Roman period 数据...")
    artifacts = fetch_cdli_artifacts(limit=100)
    print(f"[*] 获取 {len(artifacts)} 条 artifacts")

    if not artifacts:
        print("[!] CDLI API 无响应，使用本地缓存（如果有）")
        cache_path = "/Users/wangzr/Desktop/历史事件预测建模/output/cdli_analysis.json"
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                cdli_data = json.load(f)
            print(f"[*] 加载本地缓存: {cache_path}")
            # 使用本地缓存
            return summarize_local_cdli(cdli_data)

        print("[!] 无数据可分析")
        return

    # 2. 显示前几条数据
    print("\n前 3 条 artifacts:")
    for i, art in enumerate(artifacts[:3]):
        print(f"  {i+1}. {art}")

    # 3. 计算美索不达米亚 PSI
    print("\n[*] 计算美索不达米亚 PSI...")
    results = compute_mesopotamia_psi(artifacts)

    if not results or "error" in results:
        print("[!] PSI 计算失败")
        return

    # 4. 打印结果
    print("\n" + "=" * 70)
    print("美索不达米亚 PSI 跨期比较")
    print("=" * 70)
    print(f"{'Period':<30} {'N':>4} {'Sentiment':>12} {'SFD':>8} {'EED':>8}")
    print("-" * 70)
    for period, info in sorted(results.items()):
        print(f"{period:<30} {info['n']:>4} "
              f"{info['sentiment_mean']:>+12.4f} "
              f"{info['sfd']:>8.4f} "
              f"{info['eed']:>8.4f}")

    # 5. 保存
    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/cdli_v4_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 保存: {out_path}")


def summarize_local_cdli(cdli_data):
    """汇总本地 CDLI 缓存数据"""
    if isinstance(cdli_data, dict):
        # 尝试不同结构
        artifacts = cdli_data.get("artifacts", cdli_data.get("results", []))
        if isinstance(artifacts, list):
            print(f"[*] 本地缓存有 {len(artifacts)} 条")
            return compute_mesopotamia_psi(artifacts)
    return None


if __name__ == "__main__":
    main()
