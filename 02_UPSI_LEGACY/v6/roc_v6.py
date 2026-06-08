#!/usr/bin/env python3
"""
v6.0 阶段66: ROC 曲线 + 阈值优化

修复 v3.0 P2 遗留:
"PSI 阈值 = 0.5 没有说明为什么选 0.5, 改变阈值对结果有多大影响?"

用 4 个核心 PSI 序列:
- 中华历史 (CBDB)
- 中国金融 (上证)
- 全球金融 (标普)
- 全球政治 (Wikidata)

对每个序列, 扫描阈值 [-2.0, -0.5], 计算:
- 召回率 (Recall)
- 精确率 (Precision)
- F1 Score
- AUC (曲线下面积)
"""
import json
import statistics
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = ['Heiti TC', 'STHeiti', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DATA4 = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
DATA5 = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")
OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v6")


# === 准备 4 个 PSI 序列的"真值标签" ===
# 1. 上证 PSI (中国金融) - 已知 7 危机
with open(DATA4 / "market_psi_v4.json", encoding="utf-8") as f:
    fin = json.load(f)
sh = fin["sh000001"]
sh_dates = sh["dates"]
sh_psi = sh["psi"]

# 已知 7 危机日期 (前后 ±30 天为真值窗口)
SH_CRISES = ["2018-10-11", "2019-05-10", "2020-01-23", "2020-03-23",
             "2022-02-24", "2022-10-31", "2024-02-05"]
sh_label = [0] * len(sh_dates)
for crisis in SH_CRISES:
    if crisis in sh_dates:
        idx = sh_dates.index(crisis)
        for i in range(max(0, idx-30), min(len(sh_dates), idx+30)):
            sh_label[i] = 1

# 2. 标普 500 PSI (全球金融) - 24 危机
with open(DATA4 / "global_psi_v4.json", encoding="utf-8") as f:
    glob = json.load(f)
# 重算标普 PSI
with open(DATA4 / "global_market_data.json", encoding="utf-8") as f:
    raw = json.load(f)

def returns(p): return [p[i]/p[i-1]-1 for i in range(1, len(p))]
def rolling_mmp(p, w=60): return [p[i]/max(p[i-w:i+1])-1 for i in range(w, len(p))]
def rolling_vol(r, w=20): return [statistics.stdev(r[i-w:i])*(252**0.5) for i in range(w, len(r))]

sp_bars = sorted(raw["US.SP500"], key=lambda x: x[0])
sp_dates_all = [b[0] for b in sp_bars]
sp_prices = [b[1] for b in sp_bars]
sp_rets = returns(sp_prices)
sp_mmp = rolling_mmp(sp_prices, 60)
sp_sfd = rolling_vol(sp_rets, 20)
L = min(len(sp_mmp), len(sp_sfd))
sp_psi_raw = [(sp_mmp[i] + sp_sfd[i])/2 for i in range(L)]
sp_psi_mu = statistics.mean(sp_psi_raw)
sp_psi_sd = statistics.stdev(sp_psi_raw)
sp_psi = [(p - sp_psi_mu)/sp_psi_sd for p in sp_psi_raw]
sp_offset = len(sp_bars) - L
sp_dates = sp_dates_all[sp_offset:]

SP_CRISES = ["1929-10-29", "1937-05-01", "1945-08-15", "1962-05-28", "1973-10-17",
             "1980-01-01", "1987-10-19", "1990-08-02", "1997-10-27", "1998-08-17",
             "2000-03-10", "2001-09-11", "2007-10-09", "2008-09-15", "2009-03-09",
             "2010-05-06", "2011-08-08", "2015-06-12", "2016-06-23", "2018-12-24",
             "2020-03-23", "2022-02-24", "2023-03-10", "2024-08-05"]
sp_label = [0] * len(sp_dates)
for crisis in SP_CRISES:
    if crisis in sp_dates:
        idx = sp_dates.index(crisis)
        for i in range(max(0, idx-30), min(len(sp_dates), idx+30)):
            sp_label[i] = 1

# 3. 政治 PSI (Wikidata) - 33 大事件
with open(DATA5 / "political_psi_v5.json", encoding="utf-8") as f:
    pol = json.load(f)
pol_years = pol["psi"]["years"]
pol_psi = pol["psi"]["psi"]
POL_CRISES = [-218, -49, 117, 235, 410, 476, 622, 800, 1066, 1215, 1347, 1453, 1492,
              1517, 1648, 1789, 1815, 1848, 1861, 1914, 1918, 1929, 1939, 1945, 1950,
              1968, 1975, 1989, 1991, 2001, 2008, 2011, 2020, 2022]
pol_label = [0] * len(pol_years)
for crisis in POL_CRISES:
    for i, y in enumerate(pol_years):
        if abs(y - crisis) <= 5:
            pol_label[i] = 1
            break

datasets = {
    "中国金融 (上证)": (sh_psi, sh_label),
    "全球金融 (标普)": (sp_psi, sp_label),
    "全球政治 (Wikidata)": (pol_psi, pol_label),
}


def compute_metrics(y_true, y_score, threshold):
    """计算召回/精确/F1"""
    y_pred = [1 if s < threshold else 0 for s in y_score]
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return recall, precision, f1, tp, fp, fn, tn


def auc_score(y_true, y_score):
    """AUC = P(score(pos) > score(neg))"""
    pos = [s for t, s in zip(y_true, y_score) if t == 1]
    neg = [s for t, s in zip(y_true, y_score) if t == 0]
    if not pos or not neg:
        return 0
    n_correct = 0
    n_total = len(pos) * len(neg)
    for p in pos:
        for n in neg:
            if p < n:  # 因为我们用 < threshold
                n_correct += 1
    return n_correct / n_total


# 扫描阈值
thresholds = [-2.0, -1.5, -1.0, -0.7, -0.5, -0.3, 0.0, 0.5, 1.0]

print("=" * 80)
print("【ROC 曲线 + 阈值优化】 修复 v3.0 P2 遗留")
print("=" * 80)
print(f"\n{'域':18s} | {'阈值':6s} | {'Recall':7s} | {'Precision':10s} | {'F1':7s} | TP | FP | FN")
print("-" * 80)
results = {}
for ds_name, (psi, label) in datasets.items():
    print(f"\n[{ds_name}]")
    results[ds_name] = {"thresholds": [], "recall": [], "precision": [], "f1": []}
    for thr in thresholds:
        r, p, f1, tp, fp, fn, tn = compute_metrics(label, psi, thr)
        results[ds_name]["thresholds"].append(thr)
        results[ds_name]["recall"].append(r)
        results[ds_name]["precision"].append(p)
        results[ds_name]["f1"].append(f1)
        print(f"  {ds_name:18s} | {thr:+5.2f}  | {r:5.1%}   | {p:5.1%}      | {f1:5.1%}  | {tp:3d}| {fp:3d}| {fn:3d}")
    # AUC
    auc = auc_score(label, psi)
    print(f"  AUC: {auc:.3f}")
    results[ds_name]["auc"] = auc

# 找最优阈值 (F1 最高)
print()
print("=" * 80)
print("【最优阈值】")
print("=" * 80)
for ds_name in datasets:
    best_idx = results[ds_name]["f1"].index(max(results[ds_name]["f1"]))
    print(f"  {ds_name}: 最优阈值 = {results[ds_name]['thresholds'][best_idx]:+.2f}, F1 = {max(results[ds_name]['f1']):.1%}, AUC = {results[ds_name]['auc']:.3f}")

# ROC 曲线
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for idx, (ds_name, (psi, label)) in enumerate(datasets.items()):
    ax = axes[idx]
    # ROC 曲线: 召回 vs 假阳率
    fpr_list, rec_list = [], []
    for thr in np.arange(-3.0, 1.0, 0.1):
        r, p, f1, tp, fp, fn, tn = compute_metrics(label, psi, thr)
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fpr_list.append(fpr)
        rec_list.append(r)
    ax.plot(fpr_list, rec_list, color="#e74c3c", linewidth=2)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("假阳率 FPR")
    ax.set_ylabel("召回率 Recall")
    ax.set_title(f"{ds_name}\nAUC = {results[ds_name]['auc']:.3f}", fontsize=10)
    ax.grid(True, alpha=0.3)
    # 标记 PSI=-0.5
    r_05, p_05, f1_05, *_ = compute_metrics(label, psi, -0.5)
    fpr_05 = 1 - sum(1 for t, s in zip(label, psi) if t == 0 and s < -0.5) / (sum(1 for t in label if t == 0))
    ax.scatter([fpr_05], [r_05], s=100, color='blue', zorder=5, label=f"PSI=-0.5 (R={r_05:.1%})")
    ax.legend(loc="lower right", fontsize=8)

plt.suptitle("Figure 16: PSI ROC 曲线 (3 域)", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUT / "figures" / "Figure16_ROC_Curves.png", dpi=120, bbox_inches='tight')
plt.close()
print(f"\n✅ 保存 {OUT}/figures/Figure16_ROC_Curves.png")

# 阈值-F1 曲线
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#e74c3c", "#3498db", "#27ae60"]
for (ds_name, _), c in zip(datasets.items(), colors):
    ax.plot(results[ds_name]["thresholds"], [f*100 for f in results[ds_name]["f1"]],
            color=c, linewidth=2, marker='o', label=ds_name)
ax.axvline(-0.5, color='gray', linestyle='--', alpha=0.5, label='PSI=-0.5 (当前阈值)')
ax.set_xlabel("PSI 阈值")
ax.set_ylabel("F1 Score (%)")
ax.set_title("Figure 17: 阈值-F1 曲线 (最优阈值扫描)", fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "figures" / "Figure17_Threshold_F1.png", dpi=120, bbox_inches='tight')
plt.close()
print(f"✅ 保存 {OUT}/figures/Figure17_Threshold_F1.png")

# 保存结果
with open(OUT / "data" / "roc_v6.json", "w", encoding="utf-8") as f:
    json.dump({
        "datasets": {ds: {k: v for k, v in r.items() if k != "thresholds"} | {"optimal_threshold": r["thresholds"][r["f1"].index(max(r["f1"]))], "max_f1": max(r["f1"])}
                   for ds, r in results.items()},
        "thresholds_tested": thresholds,
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 保存 {OUT}/data/roc_v6.json")
