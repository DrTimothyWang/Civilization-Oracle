"""
Civilization-Oracle v4.0 - Figure 生成
====================================

生成 v3.0 缺失的 Figure 1/2/3:
- Figure 1: 96 窗十年级 PSI 时间线（按朝代分色）
- Figure 2: PSI 与历史危机叠加图（领先关系可视化）
- Figure 3: 朝代级 PSI 箱线图 + Cohen's d
"""
import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
from typing import List, Dict

# 输出目录
FIG_DIR = "/Users/wangzr/Desktop/历史事件预测建模/v4/figures"
os.makedirs(FIG_DIR, exist_ok=True)


# ============================================================
# 加载数据
# ============================================================

def load_psi_results():
    path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json"
    with open(path) as f:
        return json.load(f)


def load_statistics():
    path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/statistics_v4.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


# ============================================================
# Figure 1: 十年级 PSI 时间线
# ============================================================

def figure_1_psi_timeline(psi_data: Dict, output_path: str = None):
    """96 窗十年级 PSI 时间线"""
    if output_path is None:
        output_path = os.path.join(FIG_DIR, "Figure1_PSI_Timeline.png")

    decade_results = sorted(psi_data["decade_results"], key=lambda r: r["decade"])

    # 按朝代分组
    dynasty_color = {
        "唐朝": "#E63946",
        "北宋前期": "#2A9D8F",
        "北宋后期": "#264653",
        "南宋": "#9D4EDD",
        "明朝": "#F4A261",
    }

    fig, ax = plt.subplots(figsize=(16, 8))

    # 绘制每条 decade
    for r in decade_results:
        color = dynasty_color.get(r["dynasty"], "gray")
        ax.scatter(r["decade"], r["psi_z"], color=color, s=30, alpha=0.7,
                   edgecolors='black', linewidth=0.5, zorder=3)

    # 绘制每个朝代的连线
    for dy in dynasty_color.keys():
        years = [r["decade"] for r in decade_results if r["dynasty"] == dy]
        psis = [r["psi_z"] for r in decade_results if r["dynasty"] == dy]
        if years:
            ax.plot(years, psis, color=dynasty_color[dy], alpha=0.4, linewidth=1.5, zorder=2)

    # 危机阈值线
    ax.axhline(y=-1, color='red', linestyle='--', alpha=0.5, label='Crisis threshold (PSI_z = -1)')
    ax.axhline(y=+1, color='green', linestyle='--', alpha=0.5, label='Prosperity threshold (PSI_z = +1)')
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)

    # 关键历史事件标注
    events = [
        (755, "安史之乱 (755)"),
        (875, "黄巢起义 (875)"),
        (907, "唐亡 (907)"),
        (1127, "靖康之变 (1127)"),
        (1279, "崖山海战 (1279)"),
        (1644, "明亡 (1644)"),
    ]
    for year, name in events:
        ax.axvline(x=year, color='red', linestyle=':', alpha=0.3)
        # 找最近的 decade
        decade = (year // 10) * 10
        ax.annotate(name, xy=(decade, 2.5), xytext=(decade, 2.5),
                    fontsize=8, ha='center', color='red', rotation=45)

    # 图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color, label=dy)
        for dy, color in dynasty_color.items()
    ]
    legend_elements.extend([
        plt.Line2D([0], [0], color='red', linestyle='--', label='Crisis (PSI_z=-1)'),
        plt.Line2D([0], [0], color='green', linestyle='--', label='Prosperity (PSI_z=+1)'),
    ])
    ax.legend(handles=legend_elements, loc='upper left', ncol=2, fontsize=9)

    ax.set_xlabel('Year (decade)', fontsize=12)
    ax.set_ylabel('PSI_z (z-score)', fontsize=12)
    ax.set_title('Civilization-Oracle v4.0: 96-Window Decade-Level PSI Timeline\n(610-1644 CE, 5 dynasties)', fontsize=14)
    ax.set_ylim(-3, 3)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 1 saved: {output_path}")


# ============================================================
# Figure 2: PSI 领先危机关系
# ============================================================

def figure_2_crisis_lead(psi_data: Dict, output_path: str = None):
    """PSI 与历史危机的领先关系"""
    if output_path is None:
        output_path = os.path.join(FIG_DIR, "Figure2_Crisis_Lead.png")

    decade_results = sorted(psi_data["decade_results"], key=lambda r: r["decade"])

    # 主要历史危机
    crises = [
        {"name": "安史之乱", "year": 755, "color": "red"},
        {"name": "黄巢起义", "year": 875, "color": "red"},
        {"name": "靖康之变", "year": 1127, "color": "red"},
        {"name": "崖山海战", "year": 1279, "color": "red"},
        {"name": "明朝覆灭", "year": 1644, "color": "red"},
    ]

    fig, axes = plt.subplots(len(crises), 1, figsize=(14, 2.5 * len(crises)), sharex=False)

    for i, crisis in enumerate(crises):
        ax = axes[i]
        # 危机前 30 年到危机年
        window_start = crisis["year"] - 100
        window_end = crisis["year"] + 10

        relevant = [r for r in decade_results if window_start <= r["decade"] <= window_end]

        if not relevant:
            continue

        decades = [r["decade"] for r in relevant]
        psis = [r["psi_z"] for r in relevant]

        # 绘制 PSI
        ax.plot(decades, psis, 'b-o', linewidth=2, markersize=5, label='PSI_z')
        ax.axhline(y=-1, color='red', linestyle='--', alpha=0.5)
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)

        # 标记危机年
        ax.axvline(x=crisis["year"], color='red', linewidth=2, alpha=0.7, label=crisis["name"])

        # 标记危机前 5/10/15 年的 lead
        for lead in [5, 10, 15]:
            target = crisis["year"] - lead
            target_decade = (target // 10) * 10
            for r in relevant:
                if r["decade"] == target_decade:
                    ax.scatter([target_decade], [r["psi_z"]], color='orange', s=100,
                              zorder=5, marker='*', label=f'Lead {lead}y' if lead == 5 else "")
                    ax.annotate(f"Lead {lead}y\n{crisis['year']-target_decade}y",
                              xy=(target_decade, r["psi_z"]),
                              xytext=(target_decade, r["psi_z"] - 0.5),
                              fontsize=8, ha='center', color='darkorange')

        ax.set_ylabel('PSI_z', fontsize=10)
        ax.set_title(f'{crisis["name"]} ({crisis["year"]}): PSI lead analysis', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)

    axes[-1].set_xlabel('Year', fontsize=12)
    plt.suptitle('v4.0: PSI Lead Time Analysis for Major Historical Crises',
                fontsize=14, y=1.0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 2 saved: {output_path}")


# ============================================================
# Figure 3: 朝代级 PSI 箱线图 + Cohen's d
# ============================================================

def figure_3_dynasty_boxplot(psi_data: Dict, stats_data: Dict, output_path: str = None):
    """朝代级 PSI 分布 + 盛世/危机对比"""
    if output_path is None:
        output_path = os.path.join(FIG_DIR, "Figure3_Dynasty_Comparison.png")

    decade_results = psi_data["decade_results"]
    by_dynasty = psi_data["by_dynasty"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 3.1 五朝 PSI_z 箱线图
    ax1 = axes[0]
    dynasties = ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"]
    data_to_plot = []
    labels = []
    for dy in dynasties:
        vals = [r["psi_z"] for r in decade_results if r["dynasty"] == dy]
        if vals:
            data_to_plot.append(vals)
            labels.append(f'{dy}\n(n={len(vals)})')

    bp = ax1.boxplot(data_to_plot, labels=labels, patch_artist=True)
    colors = ['#E63946', '#2A9D8F', '#264653', '#9D4EDD', '#F4A261']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax1.axhline(y=-1, color='red', linestyle='--', alpha=0.5, label='Crisis threshold')
    ax1.axhline(y=+1, color='green', linestyle='--', alpha=0.5, label='Prosperity threshold')
    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax1.set_ylabel('PSI_z (z-score)', fontsize=11)
    ax1.set_title('v4.0: PSI Distribution by Dynasty\n(96 decade-level windows)', fontsize=11)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0, fontsize=9)

    # 3.2 Cohen's d 视觉化
    ax2 = axes[1]
    if stats_data and "cohens_d" in stats_data:
        d = stats_data["cohens_d"]
        cohens_d_val = d["d"]
        hedges_g = d["g"]
        ci_lower = d["ci_lower"]
        ci_upper = d["ci_upper"]

        # 绘制 d 值
        ax2.errorbar([1], [cohens_d_val], yerr=[[cohens_d_val - ci_lower], [ci_upper - cohens_d_val]],
                    fmt='o', markersize=12, capsize=8, color='darkblue', linewidth=2)
        ax2.axhline(y=0.2, color='gray', linestyle=':', alpha=0.5, label='Small effect (d=0.2)')
        ax2.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Medium effect (d=0.5)')
        ax2.axhline(y=0.8, color='gray', linestyle='-', alpha=0.7, label='Large effect (d=0.8)')

        ax2.set_xlim(0, 2)
        ax2.set_xticks([1])
        ax2.set_xticklabels(['盛世 (唐+明) vs 危机 (北宋后+南宋)'], fontsize=10)
        ax2.set_ylabel("Cohen's d", fontsize=11)
        ax2.set_title("Effect Size: Prosperity vs Crisis\n(individual-level, 30,518 records)", fontsize=11)
        ax2.legend(loc='upper right', fontsize=8)
        ax2.grid(True, alpha=0.3, axis='y')

        # 标注
        textstr = f"d = {cohens_d_val:.3f}\nHedges' g = {hedges_g:.3f}\n95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]"
        ax2.text(1.5, cohens_d_val, textstr, fontsize=9, va='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 3 saved: {output_path}")


# ============================================================
# Bonus Figure 4: PSI 阈值敏感性
# ============================================================

def figure_4_threshold_sensitivity(stats_data: Dict, output_path: str = None):
    """PSI 阈值敏感性曲线"""
    if output_path is None:
        output_path = os.path.join(FIG_DIR, "Figure4_Threshold_Sensitivity.png")

    if not stats_data or "threshold_sensitivity" not in stats_data:
        print("[!] 无敏感性数据，跳过 Figure 4")
        return

    sens = stats_data["threshold_sensitivity"]
    thresholds = sorted(sens.keys())
    recalls = [sens[t]["recall"] for t in thresholds]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(thresholds, recalls, 'o-', linewidth=2, markersize=10, color='darkred')
    ax.axvline(x=-1, color='green', linestyle='--', alpha=0.7, label='v4.0 default (PSI_z = -1)')
    ax.set_xlabel('PSI_z Threshold', fontsize=12)
    ax.set_ylabel('Recall (true positives / total crises)', fontsize=12)
    ax.set_title('v4.0: PSI Threshold Sensitivity\n(6 major historical crises)', fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower left', fontsize=11)
    ax.set_ylim(0, 1.1)

    # 标注每个点
    for t, r in zip(thresholds, recalls):
        ax.annotate(f'{r:.2f}', xy=(t, r), xytext=(t, r + 0.03),
                   fontsize=9, ha='center')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 4 saved: {output_path}")


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 70)
    print("v4.0 Figure 生成")
    print("=" * 70)

    psi_data = load_psi_results()
    if not psi_data:
        print("[!] 无 PSI 数据，请先运行 compute_psi_v4.py")
        return

    stats_data = load_statistics()

    figure_1_psi_timeline(psi_data)
    figure_2_crisis_lead(psi_data)
    figure_3_dynasty_boxplot(psi_data, stats_data)
    figure_4_threshold_sensitivity(stats_data)

    print("\n[✓] 所有 Figure 已生成")
    print(f"  输出目录: {FIG_DIR}")


if __name__ == "__main__":
    main()
