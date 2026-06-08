#!/usr/bin/env python3
"""阶段 35b 简化版: 直接调腾讯接口"""
import json
import urllib.request
import traceback
from pathlib import Path

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")


def fetch_t(symbol, count=2000):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,{count},qfq"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://gu.qq.com/",
        })
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        if data.get("code") != 0:
            print(f"  [code!=0] {data}")
            return []
        k_data = data["data"][symbol]
        qfq = k_data.get("qfqday", [])
        day = k_data.get("day", [])
        out = qfq if qfq else day
        print(f"  {symbol}: qfq={len(qfq)} day={len(day)} -> {len(out)} bars")
        return out
    except Exception as e:
        traceback.print_exc()
        return []


def fetch_sina(symbol, scale=240, count=1023):
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale={scale}&ma=no&datalen={count}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        if isinstance(data, list):
            print(f"  sina {symbol}: {len(data)} bars")
            return data
        print(f"  sina {symbol}: not list, {data}")
        return []
    except Exception as e:
        traceback.print_exc()
        return []


def main():
    out = {}
    print("[1] 腾讯 sh000001 (max 2000)")
    out["sh000001"] = fetch_t("sh000001", count=2000)
    print("[2] 腾讯 hkHSI")
    out["hkHSI"] = fetch_t("hkHSI", count=2000)
    print("[3] 腾讯 usSPX")
    out["usSPX"] = fetch_t("usSPX", count=2000)

    print("\n[4] 新浪补充: sz399001 (深成指) 1023 bars")
    out["sz399001_sina"] = fetch_sina("sz399001")
    print("[5] 新浪 sh000300 (沪深300) 1023 bars")
    out["sh000300_sina"] = fetch_sina("sh000300")

    with open(OUT / "market_raw_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存到 {OUT}/market_raw_data.json")
    for k, v in out.items():
        print(f"  {k}: {len(v) if v else 0} bars")


if __name__ == "__main__":
    main()
