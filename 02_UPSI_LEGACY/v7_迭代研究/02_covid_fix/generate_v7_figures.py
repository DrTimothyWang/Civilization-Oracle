#!/usr/bin/env python3
"""
生成v7 COVID PSI修正后的对比图
"""
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v7_迭代研究/02_covid_fix")

with open(OUT / "covid_psi_v7.json", encoding="utf-8") as f:
    data = json.load(f)

# 选6个代表性国家，每个国家画1-2个波次
selected = {
    "United States": [0, 4],   # 2020-04, 2021-09 (Delta)
    "India": [1],              # 2021-05 Delta高峰
    "United Kingdom": [0, 3],  # 2020-04, 2021-01 Alpha
    "Germany": [2, 5],         # 2020-12, 2021-12 Omicron
    "Japan": [2, 4],           # 2021-09, 2022-08
    "Brazil": [1, 3],          # 2020-07, 2021-01
}

fig, axes = plt.subplots(3, 2, figsize=(16, 14))
axes = axes.flatten()

for idx, (country, wave_indices) in enumerate(selected.items()):
    ax = axes[idx]
    country_data = data["results"][country]
    
    for w_idx in wave_indices:
        wave = country_data["waves"][w_idx]
        dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in wave["psi_series"]]
        psi_vals = [v for _, v in wave["psi_series"]]
        
        peak_dt = datetime.strptime(wave["wave_peak_date"], "%Y-%m-%d")
        psi_min_dt = datetime.strptime(wave["psi_min_date"], "%Y-%m-%d")
        
        ax.plot(dates, psi_vals, label=f"Wave {w_idx+1}", linewidth=1.5)
        ax.axvline(x=peak_dt, color='red', linestyle='--', alpha=0.7, label=f'Peak {wave["wave_peak_date"]}')
        ax.axvline(x=psi_min_dt, color='green', linestyle='--', alpha=0.7, label=f'PSI_min {wave["psi_min_date"]}')
    
    ax.set_title(f"{country} — PSI vs COVID Waves", fontsize=12, fontweight='bold')
    ax.set_ylabel("PSI (lower = stronger warning)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.tick_params(axis='x', rotation=30)
    ax.legend(fontsize=7, loc='upper left')
    ax.grid(True, alpha=0.3)

plt.suptitle("v7 COVID PSI Correction: PSI Minimums Lead Case Peaks\n(Green=PSI_min, Red=Case Peak)", 
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUT / "covid_psi_v7_comparison.png", dpi=200, bbox_inches='tight')
print(f"✅ Saved {OUT}/covid_psi_v7_comparison.png")

# 再生成一个领先时间分布直方图
fig, ax = plt.subplots(figsize=(10, 6))
leads = [l for l in data["summary"]["all_leads"] if -30 <= l <= 60]
ax.hist(leads, bins=20, color='steelblue', edgecolor='white', alpha=0.8)
ax.axvline(x=data["summary"]["avg_lead_days"], color='red', linestyle='-', linewidth=2, 
           label=f'Mean: {data["summary"]["avg_lead_days"]:.1f} days')
ax.axvline(x=data["summary"]["median_lead_days"], color='orange', linestyle='--', linewidth=2,
           label=f'Median: {data["summary"]["median_lead_days"]:.1f} days')
ax.axvspan(7, 30, alpha=0.2, color='green', label='Target range (7-30 days)')
ax.set_xlabel("Lead Days (PSI_min → Case Peak)", fontsize=12)
ax.set_ylabel("Frequency (Waves)", fontsize=12)
ax.set_title("v7 COVID PSI Lead Time Distribution\n(Positive = PSI leads case peak)", fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "covid_psi_v7_lead_distribution.png", dpi=200, bbox_inches='tight')
print(f"✅ Saved {OUT}/covid_psi_v7_lead_distribution.png")
