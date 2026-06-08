#!/usr/bin/env python3
"""
v15a_seshat_expansion.py
Extended UPSI (Unified Pressure Synchronization Index) engine for Seshat Domain 8.
Expands from 5 NGAs (v14a) to 12 NGAs with geographic diversity and data completeness filtering.

Reuses v14a PSI computation logic with the following additions:
- NGA selection logic with data completeness filter (>30% observed, >15 rows)
- 12 NGAs across Africa, Europe, Asia, Americas, Oceania
- Expanded crisis labels from well-documented historical events
- Confidence flags per NGA (data quality, interpolation %)
"""

import os
import sys
import json
import math
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(
    BASE_DIR, "..", "..", "v14_迭代研究", "01_seshat_prototype",
    "seshatdb-Equinox_Data-ed8f570", "Equinox_on_GitHub_June9_2022.xlsx"
)
OUTPUT_JSON = os.path.join(BASE_DIR, "v15a_seshat_expanded_results.json")

# ---------------------------------------------------------------------------
# Target NGAs — 12 NGAs for v15a expansion
# Geographic coverage:
#   Africa: Upper Egypt, Niger Inland Delta
#   Europe: Latium, Paris Basin
#   SW Asia: Susiana
#   East Asia: Middle Yellow River Valley
#   South Asia: Deccan
#   Southeast Asia: Cambodian Basin
#   Central Asia: Orkhon Valley
#   Mesoamerica: Valley of Oaxaca
#   South America: Cuzco
#   Oceania: Big Island Hawaii
# ---------------------------------------------------------------------------
TARGET_NGAS = [
    "Upper Egypt",
    "Latium",
    "Susiana",
    "Middle Yellow River Valley",
    "Valley of Oaxaca",
    "Deccan",
    "Paris Basin",
    "Orkhon Valley",
    "Cambodian Basin",
    "Cuzco",
    "Big Island Hawaii",
    "Niger Inland Delta",
]

# ---------------------------------------------------------------------------
# Known crisis events (century-mark aligned)
# Format: (nga, century_mark, crisis_name, severity_score, source_note)
# Sources: historian-curated ground truth from standard historical references.
# Severity: 1–10 scale (10 = civilizational collapse, 1 = minor transition)
# ---------------------------------------------------------------------------
KNOWN_CRISES = [
    # === v14a original 5 NGAs (retained) ===
    # Upper Egypt — First Intermediate Period collapse visible at -2100 (EgRegns)
    ("Upper Egypt", -2100, "First Intermediate Period collapse", 5,
     "Old Kingdom collapse; historian consensus"),
    # Upper Egypt — Third Intermediate Period decline visible at -1000 (EgThebL)
    ("Upper Egypt", -1000, "Third Intermediate Period / Late Period decline", 3,
     "Post-Ramesside fragmentation"),
    # Latium — Western Roman material collapse visible at 500 CE (ItOstrg)
    ("Latium", 500, "Western Roman collapse / Ostrogothic Italy", 7,
     "Fall of Western Roman Empire; standard reference"),
    # Latium — Early Medieval fragmentation visible at 600 CE (ItRav**)
    ("Latium", 600, "Early Medieval Italy / Ravenna exarchate", 4,
     "Lombard invasion; Byzantine exarchate fragmentation"),
    # Susiana — Elamite collapse visible at -1100 (IrElmCP)
    ("Susiana", -1100, "Elamite collapse / Assyrian conquest", 5,
     "Elamite political collapse under Assyrian pressure"),
    # Susiana — Achaemenid-Seleucid transition visible at -300 (IrSeleu)
    ("Susiana", -300, "Seleucid transition / Hellenistic decline", 3,
     "Post-Alexander transition; minor institutional stress"),
    # Middle Yellow River Valley — Northern Wei transition at 400 CE (CnNWei*)
    ("Middle Yellow River Valley", 400, "Northern Wei / Sixteen Kingdoms transition", 3,
     "Northern and Southern Dynasties fragmentation"),
    # Valley of Oaxaca — Monte Albán Postclassic decline at 900 CE (MxAlb5*)
    ("Valley of Oaxaca", 900, "Monte Albán V / Postclassic decline", 3,
     "Monte Albán abandonment; Mixtec rise"),
    # Valley of Oaxaca — Spanish conquest / colonial transition at 1600 CE (EsHabsb)
    ("Valley of Oaxaca", 1600, "Spanish conquest / colonial transition", 5,
     "Spanish colonial imposition; demographic collapse"),

    # === v15a new NGAs ===
    # Deccan — Maurya decline at -200 (InDecIA → InMaury → InDecKg)
    ("Deccan", -200, "Maurya decline / post-Maurya fragmentation", 4,
     "Maurya Empire fragmentation; Shunga rise"),
    # Deccan — Vijayanagara decline at 1500 (InVijay → InMugl*)
    ("Deccan", 1500, "Vijayanagara Empire decline", 4,
     "Battle of Talikota aftermath; Deccan Sultanate expansion"),

    # Paris Basin — Late Roman transition at 400 (TrERom*)
    ("Paris Basin", 400, "Late Roman transition / early medieval fragmentation", 5,
     "Fall of Western Roman administration in Gaul"),
    # Paris Basin — Carolingian decline / Viking raids at 900 (FrCarlL)
    ("Paris Basin", 900, "Carolingian decline / Viking raids", 4,
     "Carolingian fragmentation; Norman incursions"),
    # Paris Basin — Black Death / Hundred Years' War at 1400 (FrValoL)
    ("Paris Basin", 1400, "Black Death / Hundred Years' War crisis", 6,
     "Bubonic plague peak; Anglo-French war stress"),
    # Paris Basin — French Revolution at 1700 (FrBurbL)
    ("Paris Basin", 1700, "French Revolution / Ancien Régime collapse", 7,
     "1789 Revolution; regime collapse"),

    # Orkhon Valley — Xiongnu decline at 0 (MnXngnL → MnXianb)
    ("Orkhon Valley", 0, "Xiongnu confederation decline", 4,
     "Xiongnu split; Southern Xiongnu submission to Han"),
    # Orkhon Valley — Uyghur Khaganate collapse at 900 (MnUigur → MnShiwe)
    ("Orkhon Valley", 900, "Uyghur Khaganate collapse", 5,
     "Uyghur defeat by Kyrgyz; capital relocation"),
    # Orkhon Valley — Zunghar / post-Mongol transition at 1700 (MnMongL → MnZungh)
    ("Orkhon Valley", 1700, "Zunghar / post-Mongol transition", 3,
     "Qing-Zunghar wars; Mongol successor state stress"),

    # Cambodian Basin — Angkor / Khmer Empire decline at 1400 (KhAngkL → KhCambd)
    ("Cambodian Basin", 1400, "Angkor / Khmer Empire decline", 5,
     "Angkor abandonment; Thai-Ayutthaya pressure; hydraulic collapse hypothesis"),

    # Cuzco — Wari decline at 900 (PeWari* → PeCuzL1)
    ("Cuzco", 900, "Wari decline / post-Wari fragmentation", 4,
     "Wari state dissolution; Middle Horizon transition"),
    # Cuzco — Inca Empire collapse at 1600 (PeInca* → EsHabsb)
    ("Cuzco", 1600, "Inca Empire collapse / Spanish conquest", 6,
     "Spanish conquest 1532–1572; smallpox and civil war"),

    # Big Island Hawaii — Kamehameha unification / pre-contact stress at 1700 (Hawaii3 → USKameh)
    ("Big Island Hawaii", 1700, "Kamehameha unification / pre-contact stress", 4,
     "Late pre-contact warfare; Kamehameha I consolidation c. 1790"),

    # Niger Inland Delta — Ghana Empire decline at 1200 (MrWagdL → MlMali*)
    ("Niger Inland Delta", 1200, "Ghana Empire decline / Mali rise", 4,
     "Sosso conquest; Mali Empire succession"),
    # Niger Inland Delta — Songhai collapse at 1600 (MlSong2 → MaSaadi)
    ("Niger Inland Delta", 1600, "Songhai Empire collapse / Moroccan invasion", 5,
     "Battle of Tondibi 1591; Moroccan pashalik imposition"),
]

# ---------------------------------------------------------------------------
# Variable mapping to UPSI dimensions
# ---------------------------------------------------------------------------
MATERIAL_VARS = ["Pop", "Terr", "Agri"]          # Pop/Terr already log-like in ImpSCDat; Agri from Aggr
FRAGMENTATION_VARS = ["Hier", "Gov", "MilTech"]   # abs(delta) computed
DISENGAGEMENT_VARS = ["Info", "Infra", "FullTBur"]  # FullTBur from TSDat123

# Weights
W_MAT = 0.4
W_FRAG = 0.3
W_DIS = 0.3
PSI_THRESHOLD = 0.5  # v13a convention: positive UPSI = distress (differs from finance domains)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_data(excel_path):
    """Load and merge key Seshat sheets."""
    xls = pd.ExcelFile(excel_path)

    # Primary aggregated time-series
    aggr = pd.read_excel(xls, sheet_name="AggrSCWarAgriRelig")
    spc = pd.read_excel(xls, sheet_name="SPC_MilTech")
    ts = pd.read_excel(xls, sheet_name="TSDat123")
    polities = pd.read_excel(xls, sheet_name="Polities")

    # Merge MilTech
    df = aggr.merge(
        spc[["NGA", "PolID", "Time", "MilTech"]],
        on=["NGA", "PolID", "Time"],
        how="left",
    )

    # Merge FullTBur from TSDat123
    ts_sub = ts[["NGA", "PolID", "Time", "FullTBur", "Court", "LegCode"]].copy()
    df = df.merge(ts_sub, on=["NGA", "PolID", "Time"], how="left")

    # Ensure numeric
    for col in MATERIAL_VARS + FRAGMENTATION_VARS + DISENGAGEMENT_VARS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Time as int century mark
    df["Time"] = df["Time"].astype(int)

    # Interpolation flag: uniq='y' => observed, 'n' => interpolated
    df["is_interpolated"] = df["uniq"] != "y"

    return df, polities


def assess_nga_quality(df, nga_name, min_rows=15, min_observed_pct=30.0):
    """
    Assess whether an NGA meets minimum quality thresholds.
    Returns (pass_flag, quality_dict).
    """
    sub = df[df["NGA"] == nga_name]
    n_rows = len(sub)
    if n_rows == 0:
        return False, {"error": "No data"}

    n_observed = int((sub["uniq"] == "y").sum())
    observed_pct = round(n_observed / n_rows * 100, 1)
    n_interpolated = n_rows - n_observed
    interp_pct = round(n_interpolated / n_rows * 100, 1)

    # Variable-level completeness
    per_var = {}
    for col in MATERIAL_VARS + FRAGMENTATION_VARS + DISENGAGEMENT_VARS:
        if col in sub.columns:
            per_var[col] = round(sub[col].notna().sum() / n_rows * 100, 1)
    avg_var_comp = round(sum(per_var.values()) / len(per_var), 1) if per_var else 0.0

    time_range = [int(sub["Time"].min()), int(sub["Time"].max())]

    passes = (n_rows >= min_rows) and (observed_pct >= min_observed_pct)

    quality = {
        "n_rows": n_rows,
        "n_observed": n_observed,
        "observed_pct": observed_pct,
        "n_interpolated": n_interpolated,
        "interpolated_pct": interp_pct,
        "avg_variable_completeness": avg_var_comp,
        "time_range": time_range,
        "per_variable_completeness": per_var,
        "passes_threshold": passes,
        "min_rows_required": min_rows,
        "min_observed_pct_required": min_observed_pct,
    }
    return passes, quality


def impute_within_nga(df, vars_to_impute, method="mean"):
    """Simple mean imputation within NGA. Documented per v13a plan."""
    for col in vars_to_impute:
        if col not in df.columns:
            continue
        for nga in df["NGA"].unique():
            mask = df["NGA"] == nga
            sub = df.loc[mask, col]
            if sub.isna().all():
                continue
            if method == "mean":
                fill_val = sub.mean(skipna=True)
            elif method == "median":
                fill_val = sub.median(skipna=True)
            else:
                fill_val = sub.mean(skipna=True)
            df.loc[mask & df[col].isna(), col] = fill_val
    return df


def compute_nga_psi(nga_df):
    """Compute PSI time series for a single NGA."""
    nga_df = nga_df.sort_values("Time").reset_index(drop=True)
    n = len(nga_df)
    if n < 3:
        return nga_df  # insufficient for 3-century window

    # --- Material ---
    # Use imputed Pop, Terr, Agri. Invert so decline = stress.
    # Smooth with 3-century rolling mean before z-scoring (per v13a plan)
    mat_raw = nga_df[MATERIAL_VARS].mean(axis=1, skipna=True)
    mat_smooth = mat_raw.rolling(window=3, min_periods=1, center=True).mean()
    # Backward-looking z-score: compare current century to previous 5 centuries
    roll_mean = mat_smooth.rolling(window=5, min_periods=3).mean()
    roll_std = mat_smooth.rolling(window=5, min_periods=3).std()
    mat_z = (mat_smooth - roll_mean.shift(1)) / roll_std.shift(1).replace(0, np.nan)
    # Invert: lower material = higher stress => positive z = stress
    mat_z = -mat_z

    # --- Fragmentation ---
    # First-difference absolute values, then backward-looking z-score
    frag_deltas = pd.DataFrame(index=nga_df.index)
    for v in FRAGMENTATION_VARS:
        if v in nga_df.columns:
            frag_deltas[v + "_delta"] = nga_df[v].diff().abs()
    frag_raw = frag_deltas.mean(axis=1, skipna=True)
    frag_smooth = frag_raw.rolling(window=3, min_periods=1, center=True).mean()
    roll_mean = frag_smooth.rolling(window=5, min_periods=3).mean()
    roll_std = frag_smooth.rolling(window=5, min_periods=3).std()
    frag_z = (frag_smooth - roll_mean.shift(1)) / roll_std.shift(1).replace(0, np.nan)
    # Higher fragmentation = higher stress (positive z) — no inversion

    # --- Disengagement ---
    dis_raw = nga_df[DISENGAGEMENT_VARS].mean(axis=1, skipna=True)
    dis_smooth = dis_raw.rolling(window=3, min_periods=1, center=True).mean()
    roll_mean = dis_smooth.rolling(window=5, min_periods=3).mean()
    roll_std = dis_smooth.rolling(window=5, min_periods=3).std()
    dis_z = (dis_smooth - roll_mean.shift(1)) / roll_std.shift(1).replace(0, np.nan)
    # Invert: lower disengagement = higher stress
    dis_z = -dis_z

    # Cap extreme z-scores to avoid division-by-near-zero artifacts
    mat_z = mat_z.clip(-5, 5)
    frag_z = frag_z.clip(-5, 5)
    dis_z = dis_z.clip(-5, 5)

    # --- UPSI ---
    # v13a pseudocode: positive UPSI = stress (historical domain convention)
    # All three dimensions are aligned so that positive = stress:
    #   Material decline    -> +Material_z
    #   Fragmentation rise    -> +Fragmentation_z
    #   Disengagement decline -> +Disengagement_z
    upsi = W_MAT * mat_z.fillna(0) + W_FRAG * frag_z.fillna(0) + W_DIS * dis_z.fillna(0)

    # Down-weight interpolated centuries in final UPSI
    upsi_weighted = np.where(nga_df["is_interpolated"], upsi * 0.5, upsi)

    nga_df["Material_raw"] = mat_raw
    nga_df["Material_z"] = mat_z
    nga_df["Fragmentation_raw"] = frag_raw
    nga_df["Fragmentation_z"] = frag_z
    nga_df["Disengagement_raw"] = dis_raw
    nga_df["Disengagement_z"] = dis_z
    nga_df["UPSI"] = upsi
    nga_df["UPSI_weighted"] = upsi_weighted
    nga_df["UPSI_threshold_pass"] = upsi > PSI_THRESHOLD
    nga_df["UPSI_weighted_pass"] = upsi_weighted > PSI_THRESHOLD

    return nga_df


def attach_crisis_labels(nga_df, nga_name):
    """Attach known crisis labels based on century marks, with ±1-century window."""
    crises = [c for c in KNOWN_CRISES if c[0] == nga_name]
    nga_df["crisis_known"] = False
    nga_df["crisis_name"] = ""
    nga_df["crisis_severity"] = 0
    nga_df["crisis_source"] = ""

    for _, century, name, severity, source in crises:
        # Exact match first
        exact_mask = nga_df["Time"] == century
        if exact_mask.any():
            idx = nga_df[exact_mask].index[0]
            nga_df.loc[idx, "crisis_known"] = True
            nga_df.loc[idx, "crisis_name"] = name
            nga_df.loc[idx, "crisis_severity"] = severity
            nga_df.loc[idx, "crisis_source"] = source
            continue

        # Fallback: nearest century within ±1 century
        near_mask = nga_df["Time"].between(century - 100, century + 100)
        if near_mask.any():
            candidates = nga_df.loc[near_mask]
            nearest_idx = (candidates["Time"] - century).abs().idxmin()
            nga_df.loc[nearest_idx, "crisis_known"] = True
            nga_df.loc[nearest_idx, "crisis_name"] = name + f" (nearest @ {int(nga_df.loc[nearest_idx, 'Time'])}"
            nga_df.loc[nearest_idx, "crisis_severity"] = severity
            nga_df.loc[nearest_idx, "crisis_source"] = source
    return nga_df


def compute_metrics(nga_df):
    """Recall, precision, F1 for UPSI > 0.5 vs known crises."""
    # Only consider rows with valid UPSI
    valid = nga_df.dropna(subset=["UPSI"])
    if len(valid) == 0:
        return {"recall": 0.0, "precision": 0.0, "f1": 0.0,
                "tp": 0, "fp": 0, "fn": 0, "tn": 0, "n_crisis": 0, "n_stable": 0}

    tp = ((valid["UPSI"] > PSI_THRESHOLD) & valid["crisis_known"]).sum()
    fp = ((valid["UPSI"] > PSI_THRESHOLD) & ~valid["crisis_known"]).sum()
    fn = ((valid["UPSI"] <= PSI_THRESHOLD) & valid["crisis_known"]).sum()
    tn = ((valid["UPSI"] <= PSI_THRESHOLD) & ~valid["crisis_known"]).sum()

    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "recall": round(float(recall), 3),
        "precision": round(float(precision), 3),
        "f1": round(float(f1), 3),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "n_crisis": int(valid["crisis_known"].sum()),
        "n_stable": int((~valid["crisis_known"]).sum()),
    }


def build_time_series_records(nga_df, nga_name):
    """Build JSON-serializable time-series records."""
    records = []
    for _, row in nga_df.iterrows():
        if pd.isna(row.get("UPSI")):
            continue
        rec = {
            "nga": nga_name,
            "polity_id": str(row.get("PolID", "")),
            "century_mark": int(row["Time"]),
            "data_type": "interpolated" if row.get("is_interpolated") else "observed",
            "material_raw": round(float(row["Material_raw"]), 4) if not pd.isna(row.get("Material_raw")) else None,
            "material_z": round(float(row["Material_z"]), 4) if not pd.isna(row.get("Material_z")) else None,
            "fragmentation_raw": round(float(row["Fragmentation_raw"]), 4) if not pd.isna(row.get("Fragmentation_raw")) else None,
            "fragmentation_z": round(float(row["Fragmentation_z"]), 4) if not pd.isna(row.get("Fragmentation_z")) else None,
            "disengagement_raw": round(float(row["Disengagement_raw"]), 4) if not pd.isna(row.get("Disengagement_raw")) else None,
            "disengagement_z": round(float(row["Disengagement_z"]), 4) if not pd.isna(row.get("Disengagement_z")) else None,
            "upsi": round(float(row["UPSI"]), 4),
            "upsi_weighted": round(float(row["UPSI_weighted"]), 4),
            "upsi_pass": bool(row["UPSI_threshold_pass"]),
            "crisis_known": bool(row.get("crisis_known", False)),
            "crisis_name": str(row.get("crisis_name", "")),
            "crisis_severity": int(row.get("crisis_severity", 0)),
            "crisis_source": str(row.get("crisis_source", "")),
        }
        records.append(rec)
    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(EXCEL_PATH):
        print(f"[FATAL] Excel not found at {EXCEL_PATH}")
        sys.exit(1)

    print("[1/6] Loading Seshat data ...")
    df, polities = load_data(EXCEL_PATH)
    print(f"  -> {len(df)} total rows, {df['NGA'].nunique()} NGAs")

    print("[2/6] Assessing NGA quality and filtering ...")
    quality_reports = {}
    passed_ngas = []
    excluded_ngas = []
    for nga in TARGET_NGAS:
        passes, quality = assess_nga_quality(df, nga, min_rows=15, min_observed_pct=30.0)
        quality_reports[nga] = quality
        if passes:
            passed_ngas.append(nga)
            print(f"  [PASS] {nga}: {quality['n_rows']} rows, {quality['observed_pct']}% observed, avg_var={quality['avg_variable_completeness']}%")
        else:
            excluded_ngas.append(nga)
            reason = "rows" if quality["n_rows"] < 15 else "observed_pct"
            print(f"  [EXCLUDE] {nga}: {quality['n_rows']} rows, {quality['observed_pct']}% observed — fails {reason} threshold")

    print(f"  -> {len(passed_ngas)} NGAs passed, {len(excluded_ngas)} excluded")

    print("[3/6] Filtering to selected NGAs ...")
    df_target = df[df["NGA"].isin(passed_ngas)].copy()
    print(f"  -> {len(df_target)} rows for target NGAs")

    print("[4/6] Imputing missing data (mean within NGA) ...")
    vars_to_impute = [v for v in MATERIAL_VARS + FRAGMENTATION_VARS + DISENGAGEMENT_VARS if v in df_target.columns]
    df_target = impute_within_nga(df_target, vars_to_impute, method="mean")
    # Report missingness after imputation
    for nga in passed_ngas:
        sub = df_target[df_target["NGA"] == nga]
        for v in vars_to_impute:
            missing = sub[v].isna().sum()
            if missing > 0:
                print(f"  [WARN] {nga} {v}: still {missing} missing after imputation")

    print("[5/6] Computing PSI per NGA ...")
    nga_results = {}
    all_records = []
    per_nga_metrics = {}

    for nga in passed_ngas:
        nga_df = df_target[df_target["NGA"] == nga].copy()
        if len(nga_df) < 3:
            print(f"  [SKIP] {nga}: only {len(nga_df)} rows (< 3-century window)")
            continue

        nga_df = compute_nga_psi(nga_df)
        nga_df = attach_crisis_labels(nga_df, nga)
        metrics = compute_metrics(nga_df)
        per_nga_metrics[nga] = metrics

        records = build_time_series_records(nga_df, nga)
        all_records.extend(records)

        # Summary stats
        valid_upsi = nga_df["UPSI"].dropna()
        nga_results[nga] = {
            "n_centuries": len(nga_df),
            "n_observed": int((~nga_df["is_interpolated"]).sum()),
            "n_interpolated": int(nga_df["is_interpolated"].sum()),
            "observed_pct": round((~nga_df["is_interpolated"]).sum() / len(nga_df) * 100, 1),
            "upsi_mean": round(float(valid_upsi.mean()), 4) if len(valid_upsi) > 0 else None,
            "upsi_std": round(float(valid_upsi.std()), 4) if len(valid_upsi) > 0 else None,
            "upsi_min": round(float(valid_upsi.min()), 4) if len(valid_upsi) > 0 else None,
            "upsi_max": round(float(valid_upsi.max()), 4) if len(valid_upsi) > 0 else None,
            "n_upsi_pass": int((nga_df["UPSI"] > PSI_THRESHOLD).sum()),
            "n_crisis_known": int(nga_df["crisis_known"].sum()),
            "metrics": metrics,
            "time_range": [int(nga_df["Time"].min()), int(nga_df["Time"].max())],
            "quality": quality_reports[nga],
        }
        print(f"  {nga}: {len(nga_df)} centuries, UPSI pass={metrics['tp']}/{metrics['n_crisis']} crises, recall={metrics['recall']}, precision={metrics['precision']}")

    # Aggregate metrics
    total_tp = sum(m["tp"] for m in per_nga_metrics.values())
    total_fp = sum(m["fp"] for m in per_nga_metrics.values())
    total_fn = sum(m["fn"] for m in per_nga_metrics.values())
    total_tn = sum(m["tn"] for m in per_nga_metrics.values())
    agg_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    agg_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    agg_f1 = 2 * agg_precision * agg_recall / (agg_precision + agg_recall) if (agg_precision + agg_recall) > 0 else 0.0

    aggregate = {
        "ngas_targeted": len(TARGET_NGAS),
        "ngas_processed": len(nga_results),
        "ngas_excluded": len(excluded_ngas),
        "excluded_nga_names": excluded_ngas,
        "total_centuries": sum(r["n_centuries"] for r in nga_results.values()),
        "total_crisis_events": len([c for c in KNOWN_CRISES if c[0] in passed_ngas]),
        "total_tp": int(total_tp),
        "total_fp": int(total_fp),
        "total_fn": int(total_fn),
        "total_tn": int(total_tn),
        "aggregate_recall": round(float(agg_recall), 3),
        "aggregate_precision": round(float(agg_precision), 3),
        "aggregate_f1": round(float(agg_f1), 3),
    }

    output = {
        "_metadata": {
            "source": "Seshat: Global History Databank — Equinox-2020 snapshot",
            "license": "CC BY-NC-SA 4.0",
            "upsi_version": "v15.0-alpha",
            "nga_count_target": len(TARGET_NGAS),
            "ngas_processed": len(nga_results),
            "ngas_excluded": len(excluded_ngas),
            "imputation_method": "mean_within_nga",
            "rolling_window_centuries": 3,
            "psi_formula": "0.4*Material_z + 0.3*Fragmentation_z + 0.3*Disengagement_z",
            "threshold": PSI_THRESHOLD,
            "interpolation_downweight": 0.5,
            "note": "v15a expansion using real Equinox-2020 data. Crisis labels are historian-curated ground truth with source notes.",
        },
        "per_nga_summary": nga_results,
        "aggregate_metrics": aggregate,
        "time_series": all_records,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[6/6] Results written to {OUTPUT_JSON}")
    print(f"  Aggregate recall: {aggregate['aggregate_recall']}")
    print(f"  Aggregate precision: {aggregate['aggregate_precision']}")
    print(f"  Aggregate F1: {aggregate['aggregate_f1']}")
    print(f"  NGAs processed: {aggregate['ngas_processed']}/{aggregate['ngas_targeted']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
