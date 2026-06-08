#!/usr/bin/env python3
"""调试 2: 用完全相同的函数但 import 不一样"""
import requests

def fetch_tencent(symbol, count=2000):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,{count},qfq"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        data = r.json()
        print(f"  [debug {symbol}] data['data'] type:", type(data['data']))
        if isinstance(data['data'], list):
            print(f"   list first elem:", str(data['data'][0])[:200])
        if data.get("code") != 0:
            return []
        k_data = data["data"].get(symbol, {})
        return k_data.get("qfqday", []) or k_data.get("day", [])
    except Exception as e:
        print(f"  [err] {symbol}: {e}")
        return []

print("test:", len(fetch_tencent("sh000001")))
