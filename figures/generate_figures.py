#!/usr/bin/env python3
"""
Generate 3 academic figures for Civilization-Oracle v3.0 paper.
Output: /Users/tianjangwang/Documents/历史事件预测建模/figures/
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path("/Users/tianjangwang/Documents/历史事件预测建模/figures")
OUT.mkdir(exist_ok=True)

# ─── Load data ───────────────────────────────────────────────────────────────
with open("/Users/tianjangwang/Documents/历史事件预测建模/output/decade_psi_all_api.json") as f:
    data = json.load(f)

records = data["results"]
print(f"Loaded {len(records)} records")

# Parse decade -> year range
def parse_decade(d):
    # "610" (int) -> 610-619, or "960-969" (str)
    if isinstance(d, int):
        return d, d + 9
    parts = d.split("-")
    return int(parts[0]), int(parts[1])

# ─── Dynasty colors ────────────────────────────────────────────────────────────
DYN_COLORS = {
    "唐朝":    "#E8A87C",
    "北宋":    "#4A90D9",
    "南宋":    "#87CEEB",
    "辽朝":    "#D4A017",
    "金朝":    "#B8860B",
    "元朝":    "#8B4513",
    "明朝":    "#2E8B57",
    "后唐":    "#E8A87C",
    "后晋":    "#D4956A",
    "后汉":    "#C08458",
    "后周":    "#A87246",
}

def get_color(dynasty):
    return DYN_COLORS.get(dynasty, "#888888")

# ─── Crisis markers (war / dynasty fall) ─────────────────────────────────────
CRISIS = {
    (900, 910): "黄巢之乱",
    (960, 970): "北宋建立",
    (1000, 1010): "澶渊之盟",
    (1030, 1040): "宋夏战争",
    (1100, 1110): "宋金对峙",
    (1125, 1135): "靖康之变",
    (1200, 1210): "蒙古崛起",
    (1230, 1240): "宋蒙战争",
    (1270, 1280): "崖山之变",
    (1350, 1360): "元末农民起义",
    (1400, 1410): "永乐盛世",
    (1450, 1460): "土木堡之变",
    (1550, 1560): "嘉靖危机",
    (1600, 1610): "明末农民起义",
    (1640, 1650): "清军入关",
}

# ─── Figure 1: PSI Timeline ──────────────────────────────────────────────────
def plot_figure1():
    fig, ax = plt.subplots(figsize=(18, 6))

    years, psis, colors = [], [], []
    for r in records:
        start, end = parse_decade(r["decade"])
        years.append((start + end) / 2)
        psis.append(r["psi"])
        colors.append(get_color(r["dynasty"]))

    ax.bar(years, psis, width=8, color=colors, alpha=0.85, edgecolor="white", linewidth=0.5)

    # Crisis markers
    for (y0, y1), label in CRISIS.items():
        ax.axvline(x=y0 + 5, color="red", linestyle="--", alpha=0.4, linewidth=1)
        ax.text(y0 + 5, max(psis) * 0.97, label, ha="center", va="top",
                fontsize=7, color="darkred", rotation=45)

    # Dynasty shading
    dynasty_spans = [
        (618, 907, "唐代", "#FFE4B5"),
        (907, 979, "五代", "#FFDAB9"),
        (960, 1127, "北宋", "#B0D4FF"),
        (1127, 1279, "南宋", "#87CEEB"),
        (916, 1234, "辽/金", "#FFFACD"),
        (1271, 1368, "元代", "#FFE4E1"),
        (1368, 1644, "明代", "#E0FFE0"),
    ]
    for (y0, y1, name, color) in dynasty_spans:
        ax.axvspan(y0, y1, alpha=0.08, color=color)
        ax.text((y0 + y1) / 2, max(psis) * 1.02, name, ha="center", fontsize=8,
                color="gray", style="italic")

    # IPW line overlay
    ipw_years, ipw_psis = [], []
    for r in records:
        if "psi_ipw" in r and r["psi_ipw"] is not None:
            start, end = parse_decade(r["decade"])
            ipw_years.append((start + end) / 2)
            ipw_psis.append(r["psi_ipw"])
    if ipw_years:
        ax.plot(ipw_years, ipw_psis, "k-", linewidth=2, alpha=0.6, label="PSI (IPW-corrected)")
        ax.scatter(ipw_years, ipw_psis, color="black", s=20, zorder=5)

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Psychological Stress Index (PSI)", fontsize=12)
    ax.set_title("Figure 1: PSI Timeline Across Five Chinese Dynasties (900–1600 CE)", fontsize=14, fontweight="bold")
    ax.set_xlim(880, 1620)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # Legend patches
    patches = [mpatches.Patch(color=c, label=k) for k, c in DYN_COLORS.items() if k in ["唐朝", "北宋", "南宋", "辽朝", "金朝", "元朝", "明朝"]]
    ax.legend(handles=patches + [plt.Line2D([0],[0], color="black", linewidth=2, label="PSI (IPW-corrected)")],
              loc="upper right", fontsize=9, ncol=2)

    plt.tight_layout()
    out = OUT / "Figure1_PSI_Timeline.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved {out}")
    plt.close()

# ─── Figure 2: IPW Correction Effect ────────────────────────────────────────
def plot_figure2():
    # Select key windows with both raw and IPW
    key_records = [r for r in records
                  if r.get("psi_ipw") is not None
                  and abs(r["psi_ipw"] - r["psi"]) > 0.001]

    if not key_records:
        print("No IPW data found, skipping Figure 2")
        return

    # Pick 13 key windows (as in paper §5.4)
    key_records = key_records[:13]

    decades = [r["decade"] for r in key_records]
    raw     = [r["psi"] for r in key_records]
    ipw     = [r["psi_ipw"] for r in key_records]

    x = np.arange(len(decades))
    w = 0.35

    fig, ax = plt.subplots(figsize=(14, 7))
    b1 = ax.bar(x - w/2, raw, w, label="PSI (raw)", color="#4A90D9", alpha=0.8)
    b2 = ax.bar(x + w/2, ipw, w, label="PSI (IPW-corrected)", color="#E74C3C", alpha=0.8)

    # Offset rate annotation
    for i, (r_val, i_val) in enumerate(zip(raw, ipw)):
        rate = (i_val - r_val) / r_val * 100 if r_val > 0 else 0
        ax.annotate(f"+{rate:.0f}%", (x[i] + w/2, i_val + 0.01),
                    ha="center", va="bottom", fontsize=7, color="#C0392B")

    ax.set_xticks(x)
    ax.set_xticklabels(decades, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("PSI Value", fontsize=12)
    ax.set_title("Figure 2: IPW Correction Effect — 13 Key Decade Windows", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, max(ipw) * 1.15)

    plt.tight_layout()
    out = OUT / "Figure2_IPW_Correction.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved {out}")
    plt.close()

# ─── Figure 3: Dynasty Box Plot ───────────────────────────────────────────────
def plot_figure3():
    from collections import defaultdict
    dyn_psi = defaultdict(list)
    for r in records:
        dyn = r["dynasty"]
        dyn_psi[dyn].append(r["psi"])

    # Group into major eras
    ERA_MAP = {
        "唐代 (Tang)":        ["唐朝", "后唐", "后晋", "后汉", "后周"],
        "北宋 (N. Song)":  ["北宋"],
        "南宋 (S. Song)":  ["南宋"],
        "辽/金 (Liao/Jin)":    ["辽朝", "金朝"],
        "元代 (Yuan)":        ["元朝"],
        "明代 (Ming)":        ["明朝"],
    }

    era_data = {}
    for era, dyns in ERA_MAP.items():
        vals = []
        for dyn in dyns:
            vals.extend(dyn_psi.get(dyn, []))
        if vals:
            era_data[era] = vals

    eras = list(era_data.keys())
    data = [era_data[e] for e in eras]
    colors = ["#E8A87C", "#4A90D9", "#87CEEB", "#D4A017", "#8B4513", "#2E8B57"]

    fig, ax = plt.subplots(figsize=(12, 6))
    bp = ax.boxplot(data, labels=eras, patch_artist=True,
                    medianprops=dict(color="black", linewidth=2),
                    flierprops=dict(marker="o", markersize=4, alpha=0.5))

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel("PSI Value", fontsize=12)
    ax.set_title("Figure 3: PSI Distribution by Dynasty Era", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    # Add mean dots
    for i, d in enumerate(data):
        ax.scatter([i + 1], [np.mean(d)], color="red", s=40, zorder=5, marker="D", label="Mean" if i == 0 else "")

    ax.legend(fontsize=10)
    plt.tight_layout()
    out = OUT / "Figure3_Dynasty_Boxplot.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved {out}")
    plt.close()

# ─── Run ─────────────────────────────────────────────────────────────────────
plot_figure1()
plot_figure2()
plot_figure3()
print("Done!")