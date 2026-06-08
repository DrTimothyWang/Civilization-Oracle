#!/usr/bin/env python3
"""调试: 打印 data['data'] 实际类型"""
import json
import requests
from pathlib import Path

url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000001,day,,,2000,qfq"
headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"}

r = requests.get(url, headers=headers, timeout=20)
print("r type:", type(r))
print("r.json type:", type(r.json))

data = r.json()
print("data type:", type(data))
print("data['data'] type:", type(data.get("data", None)))
print("data['data']:", str(data.get("data", None))[:200])

# 用纯 json
import io
data2 = json.loads(r.text)
print("\nvia json.loads:")
print("data2['data'] type:", type(data2.get("data", None)))
print("data2['data']:", str(data2.get("data", None))[:200])
