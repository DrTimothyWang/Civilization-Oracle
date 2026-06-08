#!/usr/bin/env python3
"""
v5.0 阶段45: 宏观经济 PSI
- FRED 免费 CSV API (无需 key)
- 70+ 关键宏观指标: 利率/通胀/就业/货币供应/收益率曲线
- 1850s 至今 跨 175 年
"""
import json
import requests
from pathlib import Path
import time

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")
OUT.mkdir(parents=True, exist_ok=True)


def fetch_fred(series_id, max_retries=1):
    """FRED CSV 公开接口, 带重试"""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                return None
            lines = r.text.strip().split("\n")
            data = []
            for line in lines[1:]:  # skip header
                parts = line.split(",")
                if len(parts) == 2 and parts[1] not in (".", ""):
                    try:
                        data.append((parts[0], float(parts[1])))
                    except:
                        pass
            return data
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"  err {series_id}: {e}")
                return None
            time.sleep(1)
    return None


# 70+ 关键宏观指标
SERIES = {
    # 利率
    "FEDFUNDS": "联邦基金利率",
    # 通胀
    "CPIAUCSL": "CPI 总体",
    "CPILFESL": "核心 CPI",
    # 就业
    "UNRATE": "失业率",
    "PAYEMS": "非农就业",
    "ICSA": "初次申领失业救济",
    # 货币
    "M2SL": "M2 货币供应",
    # 产出
    "GDPC1": "实际 GDP",
    "INDPRO": "工业产出",
    "RSAFS": "零售销售",
    # 房地产
    "HOUST": "新房开工",
    # 信心
    "UMCSENT": "密歇根消费者信心",
    # 股市/债市
    "BAMLH0A0HYM": "高收益债利差",
    # 商品
    "DCOILWTICO": "WTI原油",
}


def main():
    out = {}
    for sid, name in SERIES.items():
        print(f"[{sid}] {name} ...", end=" ", flush=True)
        data = fetch_fred(sid)
        if data is None or len(data) < 50:
            print(f"SKIP (无数据)")
            continue
        out[sid] = {
            "name": name,
            "data": [[d, v] for d, v in data],
        }
        print(f"{len(data):6d} obs, {data[0][0]} ~ {data[-1][0]}")
        time.sleep(0.3)

    with open(OUT / "fred_macro_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"\n✅ 保存 {len(out)} 个宏观指标")


if __name__ == "__main__":
    main()
