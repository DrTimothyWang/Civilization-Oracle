#!/usr/bin/env python3
"""
阶段 44: 全球 PSI 图表 (Figure 13-15)
- Figure 13: 13 国 PSI 同期叠加
- Figure 14: 黄金 vs 股票 PSI 领先关系
- Figure 15: 跨域 PSI 网络
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from pathlib import Path

plt.rcParams['font.family'] = ['Heiti TC', 'STHeiti', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
FIG = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/figures")
FIG.mkdir(exist_ok=True)

# 重新算 PSI (简单版)
import statistics

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
    mmp_mu, mmp_sd = statistics.mean(mmp), statistics.stdev(mmp)
    sfd_mu, sfd_sd = statistics.mean(sfd), statistics.stdev(sfd)
    psi = [(mmp[i]-mmp_mu)/mmp_sd*0.5 + (sfd[i]-sfd_mu)/sfd_sd*0.5 for i in range(L)]
    offset = len(bars) - L
    return {"dates": [b[0] for b in bars[offset:]], "psi": psi, "prices": prices[offset:]}


# 已知危机
CRISES = [
    ("1929-10-29", "1929 大萧条"),
    ("1973-10-17", "1973 石油"),
    ("1987-10-19", "1987 黑色星期一"),
    ("1997-10-27", "1997 亚洲金融"),
    ("2000-03-10", "2000 互联网"),
    ("2008-09-15", "2008 雷曼"),
    ("2020-03-23", "2020 COVID"),
    ("2022-02-24", "2022 俄乌"),
]

psi_ts = {}
for name in ["US.SP500", "JP.N225", "CA.TSX", "UK.FTSE", "DE.DAX", "HK.HSI", "FR.CAC", "GOLD", "OIL.WTI", "VIX"]:
    if name not in raw:
        continue
    psi_ts[name] = compute_psi_simple(raw[name])

# Figure 13: 13 国 PSI 同期叠加
fig, ax = plt.subplots(figsize=(16, 7))
colors = plt.cm.tab20(np.linspace(0, 1, len(psi_ts)))
for (name, ts), c in zip(psi_ts.items(), colors):
    d = [datetime.strptime(x, "%Y-%m-%d") for x in ts["dates"]]
    ax.plot(d, ts["psi"], color=c, linewidth=0.5, alpha=0.7, label=name)
ax.axhline(0, color='gray', linewidth=0.3)
for cd, cn in CRISES:
    cdate = datetime.strptime(cd, "%Y-%m-%d")
    if datetime(1927, 1, 1) <= cdate <= datetime(2026, 12, 31):
        ax.axvline(cdate, color='red', alpha=0.2, linewidth=0.5, linestyle='--')
ax.set_title("Figure 13: 全球 10 大资产 PSI_z 同步性 (1927-2026)", fontsize=14, fontweight='bold')
ax.set_ylabel("PSI_z (金融压力)")
ax.legend(loc='upper right', ncol=2, fontsize=8)
ax.grid(True, alpha=0.2)
ax.xaxis.set_major_locator(mdates.YearLocator(10))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig(FIG / "Figure13_Global_PSI.png", dpi=120, bbox_inches='tight')
plt.close()
print("✅ Figure13_Global_PSI.png")

# Figure 14: 黄金 vs 标普500 PSI 领先关系
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
sp = psi_ts["US.SP500"]
gold = psi_ts["GOLD"]
sp_map = dict(zip(sp["dates"], sp["psi"]))
gold_map = dict(zip(gold["dates"], gold["psi"]))
common = sorted(set(sp_map) & set(gold_map))

# lag -10..+30
lags = list(range(-10, 31))
corrs = []
for lag in lags:
    if lag >= 0:
        xs = [sp_map[common[i]] for i in range(len(common)-lag)]
        ys = [gold_map[common[i+lag]] for i in range(len(common)-lag)]
    else:
        xs = [sp_map[common[i]] for i in range(-lag, len(common))]
        ys = [gold_map[common[i+lag]] for i in range(-lag, len(common))]
    if len(xs) > 30:
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
        dx = (sum((x-mx)**2 for x in xs))**0.5
        dy = (sum((y-my)**2 for y in ys))**0.5
        r = num/(dx*dy) if dx*dy > 0 else 0
        corrs.append(r)
    else:
        corrs.append(0)

ax = axes[0]
ax.bar(lags, corrs, color=['red' if l < 0 else 'blue' for l in lags], alpha=0.7)
ax.axvline(0, color='black', linewidth=0.5)
ax.set_title("【领先-滞后相关】 标普500 PSI vs 黄金 PSI (lag<0 = 标普领先黄金)", fontsize=12, fontweight='bold')
ax.set_ylabel("Pearson r")
ax.grid(True, alpha=0.3)
# 标注最强 lag
max_idx = np.argmax(corrs)
ax.annotate(f"max r={corrs[max_idx]:.3f} @ lag={lags[max_idx]:+d}",
            xy=(lags[max_idx], corrs[max_idx]), xytext=(lags[max_idx]+5, corrs[max_idx]),
            fontsize=10, color='red')

# VIX 同样
vix = psi_ts["VIX"]
vix_map = dict(zip(vix["dates"], vix["psi"]))
common = sorted(set(sp_map) & set(vix_map))
corrs2 = []
for lag in lags:
    if lag >= 0:
        xs = [sp_map[common[i]] for i in range(len(common)-lag)]
        ys = [vix_map[common[i+lag]] for i in range(len(common)-lag)]
    else:
        xs = [sp_map[common[i]] for i in range(-lag, len(common))]
        ys = [vix_map[common[i+lag]] for i in range(-lag, len(common))]
    if len(xs) > 30:
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
        dx = (sum((x-mx)**2 for x in xs))**0.5
        dy = (sum((y-my)**2 for y in ys))**0.5
        r = num/(dx*dy) if dx*dy > 0 else 0
        corrs2.append(r)
    else:
        corrs2.append(0)

ax = axes[1]
ax.bar(lags, corrs2, color=['red' if l < 0 else 'blue' for l in lags], alpha=0.7)
ax.axvline(0, color='black', linewidth=0.5)
ax.set_title("【领先-滞后相关】 标普500 PSI vs VIX PSI", fontsize=12, fontweight='bold')
ax.set_ylabel("Pearson r")
ax.set_xlabel("lag (天) | <0 标普领先 | >0 标普滞后")
ax.grid(True, alpha=0.3)
max_idx = np.argmax(np.abs(corrs2))
ax.annotate(f"max |r|={corrs2[max_idx]:.3f} @ lag={lags[max_idx]:+d}",
            xy=(lags[max_idx], corrs2[max_idx]), xytext=(lags[max_idx]-15, corrs2[max_idx]+0.1),
            fontsize=10, color='red')

plt.tight_layout()
plt.savefig(FIG / "Figure14_Lead_Lag.png", dpi=120, bbox_inches='tight')
plt.close()
print("✅ Figure14_Lead_Lag.png")

# Figure 15: 召回率 vs Lead Time
fig, ax = plt.subplots(figsize=(12, 7))
# 用 summary
with open(DATA / "global_psi_v4.json", encoding="utf-8") as f:
    meta = json.load(f)
summary = meta["summary"]
xs, ys, labels = [], [], []
for name, s in summary.items():
    if s["n_crises"] > 0 and s["avg_lead_days"] > 0:
        xs.append(s["recall"] * 100)
        ys.append(s["avg_lead_days"])
        labels.append(name)
sizes = [s["n_crises"] * 30 for s in summary.values() if s["n_crises"] > 0 and s["avg_lead_days"] > 0]
colors_scatter = ["#e74c3c" if s["recall"] >= 0.9 else ("#f39c12" if s["recall"] >= 0.7 else "#95a5a6")
                  for s in summary.values() if s["n_crises"] > 0 and s["avg_lead_days"] > 0]
ax.scatter(xs, ys, s=sizes, c=colors_scatter, alpha=0.7, edgecolors='black', linewidth=0.5)
for x, y, l in zip(xs, ys, labels):
    ax.annotate(l, (x, y), fontsize=8, xytext=(5, 3), textcoords='offset points')
ax.axvline(80, color='red', linestyle='--', alpha=0.5, label='80% 召回线')
ax.set_xlabel("召回率 Recall (%)", fontsize=11)
ax.set_ylabel("平均 Lead Time (天)", fontsize=11)
ax.set_title("Figure 15: 全球 20 资产 PSI 召回率 vs Lead Time\n(气泡大小 = 已知危机数; 颜色: 红>=90%, 黄>=70%, 灰<70%)", fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right')
plt.tight_layout()
plt.savefig(FIG / "Figure15_Recall_Lead.png", dpi=120, bbox_inches='tight')
plt.close()
print("✅ Figure15_Recall_Lead.png")
