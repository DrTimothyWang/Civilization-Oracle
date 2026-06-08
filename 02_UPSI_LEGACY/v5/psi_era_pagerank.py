#!/usr/bin/env python3
"""
v5.0 阶段48b: 历史震源变迁
- 不同时期 PSI 中心度对比
- 1990s vs 2000s vs 2010s vs 2020s
- 看震源是否从 US → 中国/印度转移
"""
import json
import statistics
from pathlib import Path
import numpy as np

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
v5 = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")

with open(DATA / "global_market_data.json", encoding="utf-8") as f:
    raw = json.load(f)


def returns(p):
    return [p[i]/p[i-1] - 1 for i in range(1, len(p))]

def rolling_mmp(p, w=60):
    return [p[i]/max(p[i-w:i+1]) - 1 for i in range(w, len(p))]

def rolling_vol(r, w=20):
    return [statistics.stdev(r[i-w:i]) * (252**0.5) for i in range(w, len(r))]


def compute_psi_simple(bars):
    bars.sort(key=lambda x: x[0])
    prices = [b[1] for b in bars]
    rets = returns(prices)
    mmp = rolling_mmp(prices, 60)
    sfd = rolling_vol(rets, 20)
    L = min(len(mmp), len(sfd))
    psi = [(mmp[i] + sfd[i]) / 2 for i in range(L)]
    offset = len(bars) - L
    return {"dates": [b[0] for b in bars[offset:]], "psi": psi}


# 选 8 个核心市场
CORE = ["US.SP500", "JP.N225", "UK.FTSE", "DE.DAX", "FR.CAC", "HK.HSI", "IN.NIFTY", "BR.BVSP"]

psi_ts = {}
for name in CORE:
    if name in raw:
        psi_ts[name] = compute_psi_simple(raw[name])

# 4 个时代
ERAS = [
    ("1990s", "1990-01-01", "1999-12-31"),
    ("2000s", "2000-01-01", "2009-12-31"),
    ("2010s", "2010-01-01", "2019-12-31"),
    ("2020s", "2020-01-01", "2026-12-31"),
]


def pagerank(T, n_iter=100, d=0.85):
    """T: 转移矩阵 (N x N), T[i][j] = i→j 强度"""
    N = T.shape[0]
    v = np.ones(N) / N
    # 列归一化 (T[i][j] 是从 i 到 j, PageRank 用 T.T)
    T_norm = T / np.maximum(T.sum(axis=0, keepdims=True), 1e-10)
    for _ in range(n_iter):
        v_new = d * T_norm @ v + (1 - d) / N
        if np.allclose(v, v_new, atol=1e-7):
            break
        v = v_new
    return v


print("=" * 80)
print("【历史震源变迁】 不同时代 PSI 网络 PageRank")
print("=" * 80)
results = {}
for era_name, start, end in ERAS:
    # 找本时代共同日期
    common = None
    for m in CORE:
        if m not in psi_ts:
            continue
        d_set = set(psi_ts[m]["dates"])
        # 过滤到本时代
        d_set = {d for d in d_set if start <= d <= end}
        if common is None:
            common = d_set
        else:
            common &= d_set
    if not common or len(common) < 100:
        print(f"  {era_name}: 无足够数据")
        continue
    common = sorted(common)
    # 建 PSI 矩阵
    N = len(CORE)
    M = np.zeros((N, len(common)))
    valid_markets = []
    for i, m in enumerate(CORE):
        if m not in psi_ts:
            continue
        m_map = dict(zip(psi_ts[m]["dates"], psi_ts[m]["psi"]))
        vals = [m_map.get(d, np.nan) for d in common]
        if any(np.isnan(v) for v in vals):
            continue
        M[i] = vals
        valid_markets.append(m)
    if len(valid_markets) < 3:
        continue
    # 计算相关矩阵
    M = M[:len(valid_markets)]
    C = np.corrcoef(M)
    np.fill_diagonal(C, 0)
    C = np.maximum(C, 0)  # 只用正相关建图
    # 阈值: > 0.3 视为有边
    T = (C > 0.3).astype(float) * C
    pr = pagerank(T)
    results[era_name] = {m: float(p) for m, p in zip(valid_markets, pr)}
    sorted_pr = sorted(results[era_name].items(), key=lambda x: -x[1])
    print(f"\n  【{era_name}】 N={len(common)} 天")
    for m, p in sorted_pr[:5]:
        bar = "█" * int(p * 100)
        print(f"    {m:12s} PR={p:.4f} {bar}")

# 跨时代趋势
print()
print("=" * 80)
print("【跨时代震源转移】 PageRank 排名前 3 变化")
print("=" * 80)
print(f"  {'时代':10s} | Top 1 (震源)         | Top 2              | Top 3")
for era_name, _ in results.items():
    pr = results[era_name]
    top3 = sorted(pr.items(), key=lambda x: -x[1])[:3]
    line = f"  {era_name:10s} | "
    for m, p in top3:
        line += f"{m}({p:.3f})   | "
    print(line)

# 保存
with open(v5 / "psi_era_pagerank.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n✅ 保存 {v5}/psi_era_pagerank.json")
