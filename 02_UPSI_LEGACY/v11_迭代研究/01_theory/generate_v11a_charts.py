import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# Set Chinese font support
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# Load data
with open('/Users/wangzr/Desktop/历史事件预测建模/v9_迭代研究/01_meso_psi_v9/v9a_period_psi.json') as f:
    period_psi = json.load(f)

with open('/Users/wangzr/Desktop/历史事件预测建模/output/decade_psi_all_api.json') as f:
    chinese_psi = json.load(f)

# ========== Figure 1: Ur III Text Density Timeline ==========
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Panel A: Ur III SFD and PSI by window
ur3_windows = ['-2125', '-2100', '-2075', '-2050', '-2025']
ur3_counts = [0, 103, 27607, 48227, 1901]
ur3_sfd_z = [-0.803, -0.798, 0.621, 1.684, -0.705]
ur3_psi = [-0.482, 0.133, -0.137, 0.982, -0.496]

ax1 = axes[0, 0]
ax1_twin = ax1.twinx()
bars = ax1.bar(ur3_windows, ur3_counts, color='steelblue', alpha=0.7, label='Text Count')
line1 = ax1_twin.plot(ur3_windows, ur3_sfd_z, 'ro-', label='SFD_z', linewidth=2)
line2 = ax1_twin.plot(ur3_windows, ur3_psi, 'gs--', label='PSI_proxy', linewidth=2)
ax1.axvline(x=3, color='red', linestyle='--', alpha=0.5, label='Umma衰落 (-2037)')
ax1.axvline(x=4, color='darkred', linestyle='--', alpha=0.5, label='Ur III衰亡 (-2004)')
ax1.set_xlabel('Window Start (BCE)')
ax1.set_ylabel('Text Count', color='steelblue')
ax1_twin.set_ylabel('Z-score / PSI', color='black')
ax1.set_title('Ur III: Text Density vs PSI_proxy\n(Umma衰落 vs Ur III衰亡)')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')

# Panel B: Old Babylonian SFD and PSI
ob_windows = ['-1900', '-1850', '-1800', '-1750', '-1700', '-1650', '-1600']
ob_counts = [0, 2, 0, 7359, 0, 0, 0]
ob_sfd_z = [-0.408, -0.408, -0.408, 2.449, -0.408, -0.408, -0.408]
ob_psi = [-0.245, -0.245, -0.245, 1.469, -0.245, -0.245, -0.245]

ax2 = axes[0, 1]
ax2_twin = ax2.twinx()
ax2.bar(ob_windows, ob_counts, color='coral', alpha=0.7)
ax2_twin.plot(ob_windows, ob_sfd_z, 'ro-', linewidth=2)
ax2_twin.plot(ob_windows, ob_psi, 'gs--', linewidth=2)
ax2.axvline(x=3, color='red', linestyle='--', alpha=0.5, label='Hammurabi死后 (-1750)')
ax2.set_xlabel('Window Start (BCE)')
ax2.set_ylabel('Text Count', color='coral')
ax2_twin.set_ylabel('Z-score / PSI', color='black')
ax2.set_title('Old Babylonian: Text Density vs PSI_proxy\n(Hammurabi死后帝国分裂)')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')

# Panel C: Genre Distribution (approximate from ORACC project stats)
ax3 = axes[1, 0]
genres = ['Administrative\n(ur3)', 'Royal Inscription\n(ur3)', 'Literary\n(ob)', 'Royal\n(ob)', 'Admin\n(ed3b)', 'Admin\n(oakk)']
genre_counts = [79974, 992, 1226, 362, 3472, 5472]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
wedges, texts, autotexts = ax3.pie(genre_counts, labels=genres, autopct='%1.1f%%', colors=colors, startangle=90)
ax3.set_title('ORACC Genre Distribution by Project\n(Approximate Genre Proxy)')

# Panel D: 北宋后期 PSI Timeline
ax4 = axes[1, 1]
nbh_data = [r for r in chinese_psi['results'] if r['dynasty'] == '北宋后期']
decades = [r['decade'] for r in nbh_data]
psi_vals = [r['psi'] for r in nbh_data]
psi_ipw = [r['psi_ipw'] for r in nbh_data]
ax4.plot(decades, psi_vals, 'b-o', label='PSI', linewidth=2)
ax4.plot(decades, psi_ipw, 'g--s', label='PSI_IPW', linewidth=2)
ax4.axvline(x=1127, color='red', linestyle='--', alpha=0.5, label='靖康之变 (1127)')
ax4.set_xlabel('Decade (CE)')
ax4.set_ylabel('PSI')
ax4.set_title('北宋后期 PSI Timeline\n(突发式灭亡模式)')
ax4.legend()
ax4.set_ylim(0, 0.6)

plt.tight_layout()
plt.savefig('/Users/wangzr/Desktop/历史事件预测建模/v11_迭代研究/01_theory/fig1_failure_analysis_overview.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 2: Ur III Sub-window Analysis ==========
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Umma window -2050 to -2025 breakdown
ax1 = axes[0]
periods = ['-2050 to -2037.5\n(前半段)', '-2037.5 to -2025\n(后半段)']
counts = [26238, 21989]
colors = ['#2ca02c', '#d62728']
bars = ax1.bar(periods, counts, color=colors, alpha=0.8)
ax1.set_ylabel('Text Count')
ax1.set_title('Umma衰落窗口 (-2050 ~ -2025)\n子窗口文本分布')
for bar, count in zip(bars, counts):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500, 
             f'{count:,}', ha='center', va='bottom', fontsize=11)
ax1.text(0.5, max(counts)*0.5, '比率(后/前)=0.84\n未达衰退阈值(0.5)', 
         ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

# Hammurabi window -1750 to -1700 breakdown
ax2 = axes[1]
periods2 = ['-1750 to -1725\n(前半段)', '-1725 to -1700\n(后半段)']
counts2 = [7359, 0]
bars2 = ax2.bar(periods2, counts2, color=['#2ca02c', '#d62728'], alpha=0.8)
ax2.set_ylabel('Text Count')
ax2.set_title('Hammurabi死后窗口 (-1750 ~ -1700)\n子窗口文本分布')
for bar, count in zip(bars2, counts2):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200, 
             f'{count:,}', ha='center', va='bottom', fontsize=11)
ax2.text(0.5, max(counts2)*0.5, '比率(后/前)=0.00\n但PSI_proxy=1.469(高峰)', 
         ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))

plt.tight_layout()
plt.savefig('/Users/wangzr/Desktop/历史事件预测建模/v11_迭代研究/01_theory/fig2_subwindow_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 3: Cross-Civilization Crisis Pattern Comparison ==========
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: Crisis Type Classification
ax1 = axes[0]
crisis_types = ['渐进式衰落\n(唐/南宋/明)', '突发式灭亡\n(北宋后期)', '高压繁荣悖论\n(OB/Ur III)']
pre_crisis_psi_trend = [-0.0037, 0.0002, 0.0]  # dPSI/dt
psi_amplitude = [0.73, 0.21, 1.47]  # approximate
x = np.arange(len(crisis_types))
width = 0.35
bars1 = ax1.bar(x - width/2, [abs(v)*1000 for v in pre_crisis_psi_trend], width, label='|dPSI/dt| (×1000)', color='steelblue')
ax1_twin = ax1.twinx()
bars2 = ax1_twin.bar(x + width/2, psi_amplitude, width, label='PSI Amplitude', color='coral')
ax1.set_xticks(x)
ax1.set_xticklabels(crisis_types)
ax1.set_ylabel('|dPSI/dt| (×1000)', color='steelblue')
ax1_twin.set_ylabel('PSI Amplitude', color='coral')
ax1.set_title('危机前兆模式分类')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')

# Panel B: Time Scale Mismatch Illustration
ax2 = axes[1]
# Simulate a sudden crisis vs gradual crisis
time = np.linspace(0, 100, 100)
gradual = 1.0 - 0.008 * time + np.random.normal(0, 0.05, 100)
sudden = np.where(time < 80, 0.5 + 0.01 * time, 0.5 + 0.01 * 80 - 0.5 * (time - 80))
window_50 = np.ones(100)
window_50[::10] = 1  # 50-year window sampling

ax2.plot(time, gradual, 'b-', label='渐进式衰落 (Ur III/唐/明)', linewidth=2)
ax2.plot(time, sudden, 'r-', label='突发式危机 (北宋后期/OB分裂)', linewidth=2)
ax2.axvline(x=80, color='red', linestyle='--', alpha=0.3)
ax2.fill_between([70, 100], -0.5, 1.5, alpha=0.1, color='gray', label='50年窗口')
ax2.set_xlabel('Years Before Crisis')
ax2.set_ylabel('PSI (normalized)')
ax2.set_title('时间尺度错配: 50年窗口能否捕捉突发危机?')
ax2.legend()
ax2.set_ylim(-0.5, 1.5)

plt.tight_layout()
plt.savefig('/Users/wangzr/Desktop/历史事件预测建模/v11_迭代研究/01_theory/fig3_crisis_pattern_theory.png', dpi=150, bbox_inches='tight')
plt.close()

print("Charts generated successfully!")
