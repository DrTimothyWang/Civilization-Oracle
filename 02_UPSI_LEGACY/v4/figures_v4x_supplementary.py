"""
v4.x ULTIMATE 补充 Figure (5-8)
================================

Figure 5: PSI → P(未来 10 年危机) 映射曲线
Figure 6: IPW 校正前后 Cohen's d 对比
Figure 7: 精英网络密度时间线（危机前异常）
Figure 8: 跨文明 PSI 对比（中华 vs 美索）
"""
import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


V4_DIR = "/Users/wangzr/Desktop/历史事件预测建模/v4"
FIG_DIR = os.path.join(V4_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def figure_5_psi_to_crisis():
    """PSI_z → P(未来 10 年危机) 映射"""
    with open(os.path.join(V4_DIR, "data/psi_to_crisis_mapping.json")) as f:
        data = json.load(f)

    mapping = data["psi_to_crisis_mapping"]

    psi_vals = [m["psi_z"] for m in mapping]
    p_mean = [m["p_crisis_mean"] for m in mapping]
    p_low = [m["p_crisis_low"] for m in mapping]
    p_high = [m["p_crisis_high"] for m in mapping]

    fig, ax = plt.subplots(figsize=(12, 7))

    # 主曲线
    ax.plot(psi_vals, p_mean, 'b-', linewidth=2.5, label='Posterior P(crisis) mean')
    # 不确定区间
    ax.fill_between(psi_vals, p_low, p_high, alpha=0.2, color='blue', label='95% ETI')

    # 关键点
    key_psi = [-2.0, -1.0, 0.0, 1.0]
    for p in key_psi:
        idx = psi_vals.index(p) if p in psi_vals else None
        if idx is not None:
            ax.scatter([p], [p_mean[idx]], s=100, zorder=5, edgecolors='black', linewidth=1.5)
            ax.annotate(f'P={p_mean[idx]:.2f}\n(95% ETI [{p_low[idx]:.2f}, {p_high[idx]:.2f}])',
                       xy=(p, p_mean[idx]), xytext=(p+0.3, p_mean[idx]+0.05),
                       fontsize=9, color='darkred',
                       arrowprops=dict(arrowstyle='->', color='darkred', lw=0.5))

    # 阈值线
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=0.5, color='red', linestyle=':', alpha=0.5, label='P=0.5')

    # 真实历史事件
    crisis_examples = [
        (-2.14, 0.49, "黄巢前夕 (875)"),
        (-0.42, 0.09, "崖山前夕 (1279)"),
        (-0.22, 0.07, "明亡前夕 (1644)"),
    ]
    for psi_val, p_val, name in crisis_examples:
        ax.scatter([psi_val], [p_val], s=200, marker='*', color='gold', edgecolors='black',
                  linewidth=1.5, zorder=10)
        ax.annotate(name, xy=(psi_val, p_val), xytext=(psi_val+0.2, p_val+0.15),
                   fontsize=8, color='darkblue',
                   arrowprops=dict(arrowstyle='->', color='darkblue', lw=0.5))

    ax.set_xlabel('Current PSI_z (z-score)', fontsize=12)
    ax.set_ylabel('Posterior P(crisis within 10 years)', fontsize=12)
    ax.set_title('Figure 5: PSI → P(Future Crisis within 10 Years)\n(Bayesian Logistic Regression on 96 CBDB Decade Windows)',
                 fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(-3.5, 2.5)

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "Figure5_PSI_to_Crisis.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 5: {out}")


def figure_6_ipw_comparison():
    """IPW 校正前后 Cohen's d 对比"""
    with open(os.path.join(V4_DIR, "data/ipw_correction_v4.json")) as f:
        data = json.load(f)

    comparison = data["psi_comparison"]
    cd_comp = data["cohens_d_comparison"]

    # Plot 1: 各朝代 IPW 校正前后
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax1 = axes[0]
    dynasties = ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"]
    unw = [comparison[d]["unweighted_mean"] for d in dynasties if d in comparison]
    weighted = [comparison[d]["ipw_weighted_mean"] for d in dynasties if d in comparison]
    n_samples = [comparison[d]["n"] for d in dynasties if d in comparison]
    valid_dys = [d for d in dynasties if d in comparison]

    x = np.arange(len(valid_dys))
    width = 0.35
    bars1 = ax1.bar(x - width/2, unw, width, label='Unweighted', color='#94a3b8')
    bars2 = ax1.bar(x + width/2, weighted, width, label='IPW Weighted', color='#2A9D8F')

    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{d}\n(n={n_samples[i]})" for i, d in enumerate(valid_dys)], fontsize=9)
    ax1.set_ylabel('PSI (mean)', fontsize=11)
    ax1.set_title('IPW Correction Effect by Dynasty', fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Cohen's d 对比
    ax2 = axes[1]
    d_unw = cd_comp["unweighted"]
    d_w = cd_comp["ipw_weighted"]
    diff = cd_comp["difference"]
    cats = ['Unweighted\nPSI', 'IPW-Weighted\nPSI']
    vals = [d_unw, d_w]
    colors = ['#94a3b8', '#2A9D8F']
    bars = ax2.bar(cats, vals, color=colors)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.005,
                f'{val:.4f}', ha='center', fontsize=11, fontweight='bold')
    ax2.set_ylabel("Cohen's d (Prosperity vs Crisis)", fontsize=11)
    ax2.set_title(f'IPW Correction Effect: d = {d_unw:.4f} → {d_w:.4f}\n(Improvement: {diff:+.4f}, +{diff/d_unw*100:.1f}%)',
                  fontsize=11)
    ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='Medium effect (d=0.5)')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 0.6)

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "Figure6_IPW_Correction.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 6: {out}")


def figure_7_network_density():
    """精英网络密度时间线"""
    with open(os.path.join(V4_DIR, "data/network_density_v4.json")) as f:
        data = json.load(f)

    network_data = data["network_data"]

    decades = [d["decade"] for d in network_data]
    densities = [d["density"] for d in network_data]
    dynasties = [d["dynasty"] for d in network_data]
    n_experts = [d["n_experts"] for d in network_data]

    # 加载 PSI
    with open(os.path.join(V4_DIR, "data/psi_v4_results.json")) as f:
        psi = json.load(f)
    psi_by_decade = {r["decade"]: r["psi_z"] for r in psi["decade_results"]}
    psi_zs = [psi_by_decade.get(d, 0) for d in decades]

    # 归一化网络密度
    norm_densities = [d / max(densities) for d in densities]

    fig, ax1 = plt.subplots(figsize=(15, 8))

    # 用条形图显示密度
    color_map = {
        "唐朝": "#E63946", "北宋前期": "#2A9D8F", "北宋后期": "#264653",
        "南宋": "#9D4EDD", "明朝": "#F4A261"
    }
    bar_colors = [color_map.get(dy, "gray") for dy in dynasties]
    bars = ax1.bar(decades, norm_densities, color=bar_colors, alpha=0.6, width=8)

    ax1.set_ylabel('Normalized Elite Network Density', fontsize=12)
    ax1.set_xlabel('Decade', fontsize=12)
    ax1.set_ylim(0, 1.1)
    ax1.set_title('Figure 7: Elite Social Network Density vs PSI\n(反直觉发现: 危机前网络密度上升而非下降)',
                  fontsize=13)

    # 叠加 PSI 线
    ax2 = ax1.twinx()
    ax2.plot(decades, psi_zs, 'k-', linewidth=2, label='PSI_z')
    ax2.scatter(decades, psi_zs, c='black', s=20, zorder=5)
    ax2.axhline(y=-1, color='red', linestyle='--', alpha=0.5, label='Crisis threshold')
    ax2.axhline(y=+1, color='green', linestyle='--', alpha=0.5, label='Prosperity threshold')
    ax2.set_ylabel('PSI_z (z-score)', fontsize=12)
    ax2.set_ylim(-3, 3)

    # 关键危机
    crisis_events = [
        (755, "An Lushan"), (875, "Huang Chao"), (907, "Tang End"),
        (1127, "Jingkang"), (1279, "Yashan"), (1644, "Ming End")
    ]
    for year, name in crisis_events:
        decade = (year // 10) * 10
        ax2.axvline(x=year, color='red', linestyle=':', alpha=0.3)
        ax2.annotate(name, xy=(year, 2.5), xytext=(year, 2.5),
                     fontsize=7, color='red', rotation=45, ha='right')

    # 图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color_map["唐朝"], alpha=0.6, label='Tang'),
        Patch(facecolor=color_map["北宋前期"], alpha=0.6, label='N. Song early'),
        Patch(facecolor=color_map["北宋后期"], alpha=0.6, label='N. Song late'),
        Patch(facecolor=color_map["南宋"], alpha=0.6, label='S. Song'),
        Patch(facecolor=color_map["明朝"], alpha=0.6, label='Ming'),
        plt.Line2D([0], [0], color='black', linewidth=2, label='PSI_z'),
        plt.Line2D([0], [0], color='red', linestyle='--', label='Crisis'),
    ]
    ax1.legend(handles=legend_elements, loc='upper left', ncol=2, fontsize=9)

    ax1.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "Figure7_Network_Density.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 7: {out}")


def figure_8_cross_civilization():
    """跨文明 PSI 对比 (中华 vs 美索不达米亚)"""
    # 加载中华 PSI
    with open(os.path.join(V4_DIR, "data/psi_v4_results.json")) as f:
        china_psi = json.load(f)
    china_means = [(d, agg["psi_z_mean"]) for d, agg in china_psi["by_dynasty"].items()]
    china_means.sort(key=lambda x: -x[1])

    # 加载 CDLI
    with open(os.path.join(V4_DIR, "data/cdli_v4_results.json")) as f:
        cdli = json.load(f)
    meso = [(r["period"], r["psi_z"]) for r in cdli["psi_results"]]

    # 合并
    all_data = [("中国 " + d, v) for d, v in china_means]
    all_data += [("美索 " + p, v) for p, v in meso]
    all_data.sort(key=lambda x: -x[1])

    fig, ax = plt.subplots(figsize=(14, 7))

    labels = [x[0] for x in all_data]
    values = [x[1] for x in all_data]
    colors = ['#E63946' if '美索' in l else '#2A9D8F' for l in labels]

    bars = ax.barh(range(len(labels)), values, color=colors, alpha=0.8)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.axvline(x=0, color='gray', linestyle='-', alpha=0.5)
    ax.axvline(x=1, color='green', linestyle='--', alpha=0.5)
    ax.axvline(x=-1, color='red', linestyle='--', alpha=0.5)

    for i, (label, value) in enumerate(zip(labels, values)):
        ax.text(value + (0.1 if value > 0 else -0.1), i, f'{value:+.2f}',
                va='center', ha='left' if value > 0 else 'right', fontsize=9)

    ax.set_xlabel('PSI_z (z-score)', fontsize=12)
    ax.set_title('Figure 8: Cross-Civilization PSI Comparison\n(China 5 Dynasties vs Mesopotamia Uruk)',
                  fontsize=13)
    ax.grid(True, alpha=0.3, axis='x')

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2A9D8F', label='中华 (5 朝代)'),
        Patch(facecolor='#E63946', label='美索不达米亚 (CDLI)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    plt.tight_layout()
    out = os.path.join(FIG_DIR, "Figure8_Cross_Civilization.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[✓] Figure 8: {out}")


def main():
    print("=" * 70)
    print("v4.x ULTIMATE 补充 Figure 生成 (5-8)")
    print("=" * 70)

    figure_5_psi_to_crisis()
    figure_6_ipw_comparison()
    figure_7_network_density()
    figure_8_cross_civilization()

    print("\n[✓] 所有补充 Figure 生成完成")
    print(f"  输出: {FIG_DIR}")


if __name__ == "__main__":
    main()
