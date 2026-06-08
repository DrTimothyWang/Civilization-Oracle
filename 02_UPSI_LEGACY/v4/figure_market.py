#!/usr/bin/env python3
"""
阶段 36c: 金融 PSI 图表
Figure 10: 上证 PSI_z 时间线 (2018-2026) + 已知危机叠加
Figure 11: 跨市场 PSI 同步性 (上证/恒生/沪深300/深成)
Figure 12: PSI<0 持续期 vs 已知危机
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import numpy as np

# 中文字体
plt.rcParams['font.family'] = ['Heiti TC', 'STHeiti', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
FIG = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/figures")
FIG.mkdir(exist_ok=True)

with open(DATA / "market_psi_v4.json", encoding="utf-8") as f:
    results = json.load(f)

known_crises = [
    ("2018-10-11", "2018-10 美股闪崩"),
    ("2019-05-10", "2019-05 贸易战"),
    ("2020-01-23", "2020-01 COVID"),
    ("2020-03-23", "2020-03 股灾底"),
    ("2022-02-24", "2022-02 俄乌"),
    ("2022-10-31", "2022-Q4 转折"),
    ("2024-02-05", "2024-02 小盘崩"),
]

# Figure 10: 上证 PSI 时间线
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
key = "sh000001"
r = results[key]
dates = [datetime.strptime(d, "%Y-%m-%d") for d in r["dates"]]
psi = r["psi"]
mmp = r["mmp_z"]
sfd = r["sfd_z"]
eed = r["eed_z"]

# 收盘价
with open(DATA / "market_raw_data.json", encoding="utf-8") as f:
    raw = json.load(f)
sse_close = {b[0]: float(b[2]) for b in raw["sh000001"] if isinstance(b, list)}
prices = [sse_close.get(d.strftime("%Y-%m-%d"), None) for d in dates]
prices_clean = [(d, p) for d, p in zip(dates, prices) if p is not None]
p_dates = [x[0] for x in prices_clean]
p_vals = [x[1] for x in prices_clean]

ax = axes[0]
ax.plot(p_dates, p_vals, color="#2c3e50", linewidth=0.8)
ax.set_title("上证综指 sh000001 (2018-2026)", fontsize=12, fontweight='bold')
ax.set_ylabel("收盘价")
ax.grid(True, alpha=0.3)
for crisis_date, crisis_name in known_crises:
    if datetime.strptime(crisis_date, "%Y-%m-%d") >= p_dates[0]:
        ax.axvline(datetime.strptime(crisis_date, "%Y-%m-%d"), color='red', alpha=0.4, linewidth=0.7, linestyle='--')
        ax.text(datetime.strptime(crisis_date, "%Y-%m-%d"), max(p_vals)*0.95, crisis_name,
                rotation=90, fontsize=7, color='red', va='top')

# PSI
ax = axes[1]
ax.plot(dates, psi, color="#e74c3c", linewidth=0.7, label="PSI_z (v4.x 公式)")
ax.axhline(0, color='gray', linewidth=0.5)
ax.axhline(-0.5, color='red', linewidth=0.5, linestyle='--', alpha=0.5, label='PSI=-0.5 警戒线')
ax.fill_between(dates, psi, -2, where=[p < 0 for p in psi], color='red', alpha=0.1)
ax.set_title("上证 PSI_z = 0.4·MMP + 0.3·SFD + 0.3·EED", fontsize=12, fontweight='bold')
ax.set_ylabel("PSI_z")
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.3)
for crisis_date, crisis_name in known_crises:
    if datetime.strptime(crisis_date, "%Y-%m-%d") >= dates[0]:
        ax.axvline(datetime.strptime(crisis_date, "%Y-%m-%d"), color='red', alpha=0.4, linewidth=0.7, linestyle='--')

# 三维度
ax = axes[2]
ax.plot(dates, mmp, color='#3498db', linewidth=0.5, alpha=0.7, label='MMP_z (回撤)')
ax.plot(dates, sfd, color='#f39c12', linewidth=0.5, alpha=0.7, label='SFD_z (波动)')
ax.plot(dates, eed, color='#27ae60', linewidth=0.5, alpha=0.7, label='-EED_z (活跃)')
ax.axhline(0, color='gray', linewidth=0.5)
ax.set_title("PSI 三维度分解", fontsize=12, fontweight='bold')
ax.set_ylabel("z-score")
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.tight_layout()
plt.savefig(FIG / "Figure10_Shanghai_PSI.png", dpi=120, bbox_inches='tight')
plt.close()
print("✅ Figure10_Shanghai_PSI.png")

# Figure 11: 跨市场 PSI 对比
fig, ax = plt.subplots(figsize=(14, 6))
for key, color, label in [("sh000001", "#e74c3c", "上证"),
                           ("hkHSI", "#3498db", "恒生"),
                           ("sh000300_sina", "#27ae60", "沪深300"),
                           ("sz399001_sina", "#9b59b6", "深成")]:
    if key not in results:
        continue
    r = results[key]
    d = [datetime.strptime(x, "%Y-%m-%d") for x in r["dates"]]
    ax.plot(d, r["psi"], color=color, linewidth=0.6, alpha=0.8, label=label)
ax.axhline(0, color='gray', linewidth=0.5)
for crisis_date, crisis_name in known_crises:
    cd = datetime.strptime(crisis_date, "%Y-%m-%d")
    if cd >= datetime(2022, 3, 11):  # 4 指数共同范围
        ax.axvline(cd, color='red', alpha=0.3, linewidth=0.6, linestyle='--')
ax.set_title("跨市场 PSI_z 同步性 (2022-2026)", fontsize=13, fontweight='bold')
ax.set_ylabel("PSI_z")
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.tight_layout()
plt.savefig(FIG / "Figure11_Cross_Market_PSI.png", dpi=120, bbox_inches='tight')
plt.close()
print("✅ Figure11_Cross_Market_PSI.png")

# Figure 12: PSI 与未来收益 (反直觉发现)
with open(DATA / "market_psi_lead.json", encoding="utf-8") as f:
    lead = json.load(f)
fig, ax = plt.subplots(figsize=(10, 6))
labels = ["未来20日", "未来60日"]
neg_vals = [lead["fut20_neg_psi"] * 100, lead["fut60_neg_psi"] * 100]
pos_vals = [lead["fut20_pos_psi"] * 100, lead["fut60_pos_psi"] * 100]
x = np.arange(len(labels))
width = 0.35
b1 = ax.bar(x - width/2, neg_vals, width, color="#e74c3c", label="PSI_z < -0.5 (危机后)")
b2 = ax.bar(x + width/2, pos_vals, width, color="#27ae60", label="PSI_z > +0.5 (危机前)")
ax.axhline(0, color='black', linewidth=0.5)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("平均未来收益 (%)")
ax.set_title("【反直觉发现】PSI_z<0 反而是反弹机会, PSI_z>0 才是危机前征兆\n(危机后回归 + 危机前平静)", fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
for b in b1 + b2:
    h = b.get_height()
    ax.annotate(f"{h:+.2f}%", xy=(b.get_x() + b.get_width()/2, h),
                xytext=(0, 3 if h>0 else -10), textcoords='offset points',
                ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(FIG / "Figure12_PSI_Future_Returns.png", dpi=120, bbox_inches='tight')
plt.close()
print("✅ Figure12_PSI_Future_Returns.png")

print("\n所有 Figure 10-12 已保存到 figures/")
