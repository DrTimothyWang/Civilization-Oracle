#!/usr/bin/env python3
"""阶段 35b 真实采集 v3: 用 requests 替代 urllib"""
import json
import time
import requests
from pathlib import Path

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://gu.qq.com/",
}


def fetch_tencent(symbol, count=2000):
    """腾讯日K: qfq=前复权. URL格式: symbol,day,start_date,end_date,count,fqt"""
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,,{count},qfq"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        data = r.json()
        if data.get("code") != 0:
            print(f"  [code!=0] {symbol}")
            return []
        k_data = data["data"].get(symbol, {})
        if not k_data:
            return []
        qfq = k_data.get("qfqday", [])
        day = k_data.get("day", [])
        out = qfq if qfq else day
        return out
    except Exception as e:
        print(f"  [err] {symbol}: {e}")
        return []


def fetch_sina(symbol, scale=240, count=1023):
    """新浪日K"""
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale={scale}&ma=no&datalen={count}"
    try:
        r = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=20)
        data = r.json()
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print(f"  [err] {symbol}: {e}")
        return []


def main():
    out = {}
    print("[1] 腾讯 sh000001 (max 2000, 循环拉历史)")
    sse = []
    end_date = ""  # 默认从今天往回
    for batch in range(8):  # 8 批 = 16000 bars ≈ 60 年
        # 用日期参数分批拉: ,day,start,end,count,fqt
        if sse:
            last_date = sse[0][0]  # 最早日期
            end_date = last_date  # 拉更早
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000001,day,,{end_date},2000,qfq"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            data = r.json()
            if data.get("code") != 0:
                print(f"  batch {batch+1}: code != 0")
                break
            k_data = data["data"].get("sh000001", {})
            qfq = k_data.get("qfqday", [])
            day = k_data.get("day", [])
            chunk = qfq if qfq else day
            if not chunk:
                print(f"  batch {batch+1}: empty")
                break
            if sse and chunk[-1][0] >= sse[0][0]:
                # 没有更早的数据了
                print(f"  batch {batch+1}: 无新增更早数据，停止")
                break
            sse = chunk + sse
            print(f"  batch {batch+1}: {len(chunk)} bars, 累计 {len(sse)}, 最早 {sse[0][0]}")
            time.sleep(0.4)
        except Exception as e:
            print(f"  batch {batch+1} err: {e}")
            break
    out["sh000001"] = sse

    time.sleep(0.5)
    print("\n[2] 腾讯 hkHSI")
    out["hkHSI"] = fetch_tencent("hkHSI", 2000)
    print(f"  hkHSI: {len(out['hkHSI'])} bars")

    time.sleep(0.5)
    print("\n[3] 腾讯 usSPX (标普500)")
    # 尝试不同代码
    for sym in ["us.SPX", "usSPX", "usGSPC", "INX"]:
        r = fetch_tencent(sym, 100)
        if r:
            print(f"  {sym}: {len(r)} bars, 用此代码")
            out["usSPX"] = r
            break
    else:
        out["usSPX"] = []

    print("\n[4] 新浪 sz399001 (深成指)")
    out["sz399001_sina"] = fetch_sina("sz399001")
    print(f"  sz399001: {len(out['sz399001_sina'])} bars")

    print("[5] 新浪 sh000300 (沪深300)")
    out["sh000300_sina"] = fetch_sina("sh000300")
    print(f"  sh000300: {len(out['sh000300_sina'])} bars")

    with open(OUT / "market_raw_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存到 {OUT}/market_raw_data.json")

    total = sum(len(v) for v in out.values() if v)
    print(f"   总计: {total} bars")
    for k, v in out.items():
        if v:
            print(f"   {k}: {len(v)} bars, {v[0][0] if isinstance(v[0], list) else v[0]['day']} ~ {v[-1][0] if isinstance(v[-1], list) else v[-1]['day']}")


if __name__ == "__main__":
    main()
