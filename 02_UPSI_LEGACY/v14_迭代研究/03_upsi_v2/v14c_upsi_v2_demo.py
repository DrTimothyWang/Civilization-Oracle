#!/usr/bin/env python3
"""
UPSI_v2 Demo Script
===================
Runs the UPSI_v2 engine on:
1. Synthetic civilization lifecycle data
2. Real Chinese dynasty data (from decade_psi_summary.json)

Author: UPSI_v2_Prototype_Engineer
Date: 2026-06-04
"""

import json
import os
import sys
import numpy as np

# Ensure the engine module is importable
sys.path.insert(0, os.path.dirname(__file__))
from v14c_upsi_v2 import UPSIv2Engine, run_upsi_v2

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
PLOTS_DIR = os.path.join(BASE_DIR, "v14c_upsi_v2_plots")
REAL_DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "..", "output", "decade_psi_summary.json")

os.makedirs(PLOTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Synthetic Data: Civilization Lifecycle
# ---------------------------------------------------------------------------

def generate_synthetic_lifecycle(n: int = 120) -> tuple:
    """
    Generate a synthetic civilization lifecycle:
    Stable -> Gradual Decline -> Accelerating Collapse -> Sudden Crisis -> Stable
    """
    np.random.seed(42)
    t = np.arange(n)

    # PSI: starts moderate, rises to peak, then collapses, then recovers to low stable
    # Phase 1 (0-29): Stable moderate PSI
    psi = np.zeros(n)
    psi[0:30] = 0.5 + np.random.normal(0, 0.03, 30)

    # Phase 2 (30-59): Gradual rise (high PSI building)
    psi[30:60] = np.linspace(0.5, 0.85, 30) + np.random.normal(0, 0.02, 30)

    # Phase 3 (60-79): Accelerating collapse (PSI still high but dropping fast)
    psi[60:80] = np.linspace(0.85, 0.3, 20) + np.random.normal(0, 0.04, 20)

    # Phase 4 (80-99): Sudden crisis / post-collapse (low PSI, volatile)
    psi[80:100] = 0.25 + np.random.normal(0, 0.06, 20)

    # Phase 5 (100-119): Recovery to new stable (low PSI, low volatility)
    psi[100:120] = 0.35 + np.random.normal(0, 0.02, 20)

    # SPI: low during stable, spikes during transitions
    spi = np.zeros(n)
    spi[0:30] = np.random.normal(0, 0.05, 30)          # Stable: low SPI
    spi[30:60] = np.random.normal(0.1, 0.08, 30)        # Gradual: slightly elevated
    spi[60:80] = np.linspace(0.3, 0.9, 20) + np.random.normal(0, 0.1, 20)  # Accelerating: SPI spikes
    spi[75] = 1.2  # sharp spike
    spi[80:100] = np.random.normal(0.6, 0.2, 20)        # Sudden crisis: high SPI
    spi[95] = 1.5  # secondary shock
    spi[100:120] = np.random.normal(0.05, 0.04, 20)     # New stable: low SPI

    labels = [f"Year {i}" for i in t]
    return t, psi, spi, labels


# ---------------------------------------------------------------------------
# 2. Real Data: Chinese Dynasties
# ---------------------------------------------------------------------------

def load_chinese_dynasty_data(path: str) -> dict:
    """Load decade PSI data and compute proxy SPI from PSI derivative."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    series_by_dynasty = {}
    for entry in data["results"]:
        dynasty = entry["dynasty"]
        if dynasty not in series_by_dynasty:
            series_by_dynasty[dynasty] = []
        series_by_dynasty[dynasty].append(entry)

    # Sort each dynasty by decade
    for dynasty in series_by_dynasty:
        series_by_dynasty[dynasty].sort(key=lambda x: x["decade"])

    return series_by_dynasty


def prepare_dynasty_series(records: list) -> tuple:
    """Extract PSI and compute proxy SPI from decade records."""
    decades = [r["decade"] for r in records]
    psi = np.array([r["psi"] for r in records], dtype=float)
    # Proxy SPI: rate of change of PSI between decades
    spi = np.empty_like(psi)
    spi[0] = psi[1] - psi[0] if len(psi) > 1 else 0.0
    spi[-1] = psi[-1] - psi[-2] if len(psi) > 1 else 0.0
    for i in range(1, len(psi) - 1):
        spi[i] = (psi[i + 1] - psi[i - 1]) / 2.0
    # Normalize SPI to have comparable scale to PSI (z-score-ish)
    spi = (spi - np.mean(spi)) / (np.std(spi) + 1e-9) * 0.3 + np.mean(spi)
    return decades, psi, spi


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main():
    engine = UPSIv2Engine()

    # =====================================================================
    # A. Synthetic Demo
    # =====================================================================
    print("=" * 60)
    print("UPSI_v2 Demo — Synthetic Civilization Lifecycle")
    print("=" * 60)

    t_syn, psi_syn, spi_syn, labels_syn = generate_synthetic_lifecycle(n=120)
    result_syn, _ = run_upsi_v2(
        psi=psi_syn,
        spi=spi_syn,
        time_labels=labels_syn,
        metadata={
            "domain": "synthetic",
            "description": "Synthetic civilization lifecycle: Stable -> Gradual Decline -> Accelerating Collapse -> Sudden Crisis -> Stable",
            "note": "This is synthetic data for demonstration purposes only.",
        },
        output_dir=PLOTS_DIR,
        prefix="synthetic",
    )

    print(f"Synthetic data points: {len(result_syn.time)}")
    print(f"PSI high threshold:  {result_syn.psi_high:.4f}")
    print(f"SPI high threshold:  {result_syn.spi_high:.4f}")
    print(f"Quadrant distribution:")
    for q, count in result_syn.summary()["quadrant_distribution"].items():
        print(f"  {q}: {count}")
    print(f"Alerts triggered: {len(result_syn.alerts)}")
    for alert in result_syn.alerts:
        print(f"  [{alert.time_idx:3d}] {alert.emoji} {alert.from_quadrant} -> {alert.to_quadrant}: {alert.message}")

    # Rename outputs to requested filenames
    os.rename(os.path.join(PLOTS_DIR, "synthetic_phase_portrait.png"),
              os.path.join(PLOTS_DIR, "phase_portrait_synthetic.png"))
    os.rename(os.path.join(PLOTS_DIR, "synthetic_time_series.png"),
              os.path.join(PLOTS_DIR, "time_series_synthetic.png"))

    # =====================================================================
    # B. Real Data Demo — Chinese Dynasties
    # =====================================================================
    print("\n" + "=" * 60)
    print("UPSI_v2 Demo — Real Chinese Dynasty Data")
    print("=" * 60)

    if not os.path.exists(REAL_DATA_PATH):
        print(f"WARNING: Real data file not found at {REAL_DATA_PATH}")
        print("Skipping real-data demo.")
        return

    dynasty_data = load_chinese_dynasty_data(REAL_DATA_PATH)
    print(f"Loaded dynasties: {list(dynasty_data.keys())}")

    # Run on each dynasty individually + combined
    all_decades, all_psi, all_spi, all_labels, all_dynasty_tags = [], [], [], [], []

    for dynasty, records in dynasty_data.items():
        decades, psi, spi = prepare_dynasty_series(records)
        result_dyn, _ = run_upsi_v2(
            psi=psi,
            spi=spi,
            time_labels=decades,
            metadata={
                "domain": "chinese_dynasty",
                "dynasty": dynasty,
                "source_file": REAL_DATA_PATH,
                "n_decades": len(decades),
                "note": "SPI computed as proxy from PSI decade-to-decade derivative.",
            },
            output_dir=PLOTS_DIR,
            prefix=f"dynasty_{dynasty}",
        )
        print(f"\nDynasty: {dynasty}")
        print(f"  Decades: {decades[0]}–{decades[-1]}")
        print(f"  Quadrants: {result_dyn.summary()['quadrant_distribution']}")
        print(f"  Alerts: {len(result_dyn.alerts)}")
        for alert in result_dyn.alerts:
            print(f"    [{alert.year_label}] {alert.emoji} {alert.from_quadrant} -> {alert.to_quadrant}")

        all_decades.extend(decades)
        all_psi.extend(psi.tolist())
        all_spi.extend(spi.tolist())
        all_labels.extend([f"{dynasty} {d}" for d in decades])
        all_dynasty_tags.extend([dynasty] * len(decades))

    # Combined phase portrait across all dynasties
    print("\n--- Combined cross-dynasty analysis ---")
    all_psi = np.array(all_psi, dtype=float)
    all_spi = np.array(all_spi, dtype=float)
    result_all, _ = run_upsi_v2(
        psi=all_psi,
        spi=all_spi,
        time_labels=all_labels,
        metadata={
            "domain": "chinese_dynasty_combined",
            "dynasties": list(dynasty_data.keys()),
            "source_file": REAL_DATA_PATH,
            "note": "Combined analysis across all Chinese dynasties in dataset.",
        },
        output_dir=PLOTS_DIR,
        prefix="combined_chinese",
    )
    print(f"Combined points: {len(result_all.time)}")
    print(f"Quadrants: {result_all.summary()['quadrant_distribution']}")
    print(f"Alerts: {len(result_all.alerts)}")

    # Rename one dynasty plot as the representative real-data phase portrait
    # Use Tang dynasty as it has the most dramatic collapse pattern
    tang_pp = os.path.join(PLOTS_DIR, "dynasty_唐朝_phase_portrait.png")
    if os.path.exists(tang_pp):
        os.rename(tang_pp, os.path.join(PLOTS_DIR, "phase_portrait_real.png"))

    # =====================================================================
    # C. Quadrant Legend
    # =====================================================================
    engine.plot_quadrant_legend(save_path=os.path.join(PLOTS_DIR, "quadrant_legend.png"))

    print("\n" + "=" * 60)
    print("All plots saved to:", PLOTS_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
