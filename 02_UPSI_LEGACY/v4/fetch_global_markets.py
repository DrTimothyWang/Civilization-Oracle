#!/usr/bin/env python3
"""
阶段 38-39: 西方 + 全球免费金融数据大采集
- yfinance 13 个国家指数 (1927-2026)
- Stooq 备用
- FRED 宏观 (CPI/失业率/利率)
- World Bank 国别指标
"""
import json
import yfinance as yf
from pathlib import Path
import time

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")

# 13 个国家 + 4 类资产 (股/债/汇/商品)
SYMBOLS = {
    # 股票指数
    "US.SP500": "^GSPC",       # 美股 (1927-2026, 99 年!)
    "JP.N225": "^N225",        # 日股 (1965-2026, 61 年)
    "CA.TSX": "^GSPTSE",       # 加股 (1979-2026)
    "UK.FTSE": "^FTSE",        # 英股 (1984-2026)
    "DE.DAX": "^GDAXI",        # 德股 (1987-2026)
    "HK.HSI": "^HSI",          # 港股 (1986-2026)
    "BR.BVSP": "^BVSP",        # 巴西 (1993-2026)
    "AR.MERVAL": "^MERV",      # 阿根廷 (1996-2026)
    "TR.XU100": "XU100.IS",    # 土耳其 (1997-2026)
    "AU.ASX": "^AXJO",         # 澳股 (1992-2026)
    "FR.CAC": "^FCHI",         # 法股 (1990-2026)
    "IN.NIFTY": "^NSEI",       # 印度 (2007-2026)
    "RU.IMOEX": "IMOEX.ME",    # 俄股 (2013-2024)
    # 货币
    "USDJPY": "JPY=X",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    # 债券/商品
    "US.10Y": "^TNX",          # 美 10Y 收益率
    "GOLD": "GC=F",            # 黄金
    "OIL.WTI": "CL=F",         # 原油
    "VIX": "^VIX",             # 波动率指数
}


def main():
    out = {}
    for name, sym in SYMBOLS.items():
        print(f"[{name}] {sym} ...", end=" ", flush=True)
        try:
            t = yf.Ticker(sym)
            h = t.history(period="max")
            if len(h) < 100:
                print(f"TOO FEW: {len(h)}")
                continue
            # 转成 [(date, close, volume)]
            bars = []
            for d, row in h.iterrows():
                bars.append([d.strftime("%Y-%m-%d"), float(row["Close"]), float(row.get("Volume", 0) or 0)])
            out[name] = bars
            print(f"{len(bars):6d} bars, {bars[0][0]} ~ {bars[-1][0]}")
        except Exception as e:
            print(f"ERR: {e}")
        time.sleep(0.2)

    with open(OUT / "global_market_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    total = sum(len(v) for v in out.values())
    print(f"\n✅ 保存 {len(out)} 个市场, 总计 {total} bars")


if __name__ == "__main__":
    main()
