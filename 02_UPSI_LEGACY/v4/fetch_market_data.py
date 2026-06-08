#!/usr/bin/env python3
"""
阶段 35b: 用腾讯/新浪 API 采集上证综指 1990-2026 真实日度数据
- 上证 sh000001 (1990-12-19 至今)
- 标普500 ^GSPC (可选)
- 恒生指数 hkHSI (1990 至今)
"""
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
import os

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
OUT.mkdir(parents=True, exist_ok=True)


def fetch_tencent_kline(symbol, count=800):
    """腾讯日K接口: 数据在 data['data'][symbol] 下的 day / qfqday

    返回: list of [date, open, close, high, low, volume]
    """
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,{count},qfq"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://gu.qq.com/",
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        if data.get("code") != 0:
            return []
        k_data = data["data"].get(symbol, {})
        if not k_data:
            return []
        qfq = k_data.get("qfqday", [])
        day = k_data.get("day", [])
        return qfq if qfq else day
    except Exception as e:
        print(f"  [err] {symbol}: {e}")
        return []


def fetch_sina_kline(symbol, scale=240, datalen=800):
    """新浪日K接口 (scale=240 日, datalen<=1023/批)

    返回: 列表 of {day, open, high, low, close, volume}
    """
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale={scale}&ma=no&datalen={datalen}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print(f"  [err] {symbol}: {e}")
        return []


def main():
    print("=== 采集三大指数 ===\n")

    # 1. 上证 (sh000001) 1990-12-19 至今
    print("[1/3] 上证 sh000001 (1990-2026)")
    sse_data = []
    for batch in range(8):  # 8 批 × 800 = ~6400 天 ≈ 25 年
        chunk = fetch_tencent_kline("sh000001", count=800)
        if not chunk:
            break
        sse_data = chunk + sse_data  # 倒序追加
        # 改用新浪拿更早数据
        print(f"  batch {batch+1}: got {len(chunk)} bars")
        if len(chunk) < 800:
            break
        time.sleep(0.3)
    print(f"  总数: {len(sse_data)} bars, 日期范围: {sse_data[0][0] if sse_data else 'N/A'} ~ {sse_data[-1][0] if sse_data else 'N/A'}")

    # 2. 恒生 (hkHSI) 1990 至今
    print("\n[2/3] 恒生 hkHSI")
    hsi_data = fetch_tencent_kline("hkHSI", count=2000)  # 单批 max
    print(f"  总数: {len(hsi_data)} bars")

    # 3. 标普500 (usSPX)
    print("\n[3/3] 标普500 usSPX")
    spx_data = fetch_tencent_kline("usSPX", count=2000)
    print(f"  总数: {len(spx_data)} bars")

    # 用新浪补全早期
    print("\n[补] 新浪补充上证早期数据")
    sina_sse = fetch_sina_kline("sh000001", scale=240, datalen=1023)
    print(f"  新浪上证: {len(sina_sse)} bars")

    # 保存
    out = {
        "sh000001_tencent": sse_data,
        "hkHSI_tencent": hsi_data,
        "usSPX_tencent": spx_data,
        "sh000001_sina": sina_sse,
    }
    with open(OUT / "market_raw_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存到 {OUT / 'market_raw_data.json'}")
    print(f"   SSE: {len(sse_data)+len(sina_sse)} 总, HSI: {len(hsi_data)}, SPX: {len(spx_data)}")


if __name__ == "__main__":
    main()
