#!/usr/bin/env python3
"""
v15a_precision_analysis.py
Analyze precision vs NGA count, data completeness, and crisis label density
for the v15a Seshat expansion.

Outputs:
- Console tables
- v15a_precision_analysis.json (structured results)
"""

import json
import os
import sys
from collections import defaultdict

import numpy as np

RESULTS_JSON = os.path.join(os.path.dirname(__file__), "v15a_seshat_expanded_results.json")
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "v15a_precision_analysis.json")


def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_precision_vs_nga_count(data):
    """
    Simulate cumulative precision/recall as NGAs are added one by one,
    ordered by: (1) data quality, (2) original v14a set first.
    """
    per_nga = data["per_nga_summary"]
    
    # v14a original set
    v14a_ngas = {"Upper Egypt", "Latium", "Susiana", "Middle Yellow River Valley", "Valley of Oaxaca"}
    
    # Order: v14a first (by quality), then new NGAs (by quality)
    v14a_items = [(n, d) for n, d in per_nga.items() if n in v14a_ngas]
    new_items = [(n, d) for n, d in per_nga.items() if n not in v14a_ngas]
    
    # Sort each group by observed_pct descending
    v14a_items.sort(key=lambda x: x[1]["quality"]["observed_pct"], reverse=True)
    new_items.sort(key=lambda x: x[1]["quality"]["observed_pct"], reverse=True)
    
    ordered = v14a_items + new_items
    
    cumulative = []
    cum_tp = cum_fp = cum_fn = cum_tn = 0
    
    for i, (nga, info) in enumerate(ordered, start=1):
        m = info["metrics"]
        cum_tp += m["tp"]
        cum_fp += m["fp"]
        cum_fn += m["fn"]
        cum_tn += m["tn"]
        
        recall = cum_tp / (cum_tp + cum_fn) if (cum_tp + cum_fn) > 0 else 0.0
        precision = cum_tp / (cum_tp + cum_fp) if (cum_tp + cum_fp) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        cumulative.append({
            "nga_count": i,
            "nga_name": nga,
            "is_v14a": nga in v14a_ngas,
            "cum_tp": cum_tp,
            "cum_fp": cum_fp,
            "cum_fn": cum_fn,
            "cum_tn": cum_tn,
            "cum_recall": round(recall, 3),
            "cum_precision": round(precision, 3),
            "cum_f1": round(f1, 3),
        })
    
    return cumulative


def analyze_precision_vs_completeness(data):
    """Correlate per-NGA precision/recall with data completeness metrics."""
    per_nga = data["per_nga_summary"]
    rows = []
    
    for nga, info in per_nga.items():
        q = info["quality"]
        m = info["metrics"]
        rows.append({
            "nga": nga,
            "observed_pct": q["observed_pct"],
            "avg_variable_completeness": q["avg_variable_completeness"],
            "interpolated_pct": q["interpolated_pct"],
            "n_centuries": info["n_centuries"],
            "n_crisis_known": info["n_crisis_known"],
            "crisis_density": round(info["n_crisis_known"] / info["n_centuries"], 4) if info["n_centuries"] > 0 else 0,
            "recall": m["recall"],
            "precision": m["precision"],
            "f1": m["f1"],
            "tp": m["tp"],
            "fp": m["fp"],
            "fn": m["fn"],
        })
    
    # Compute simple correlations
    def corr(x_list, y_list):
        if len(x_list) < 2:
            return None
        x = np.array(x_list, dtype=float)
        y = np.array(y_list, dtype=float)
        # Pearson
        mx, my = x.mean(), y.mean()
        sx, sy = x.std(ddof=1), y.std(ddof=1)
        if sx == 0 or sy == 0:
            return 0.0
        return round(float(np.corrcoef(x, y)[0, 1]), 3)
    
    observed_pcts = [r["observed_pct"] for r in rows]
    var_comps = [r["avg_variable_completeness"] for r in rows]
    recalls = [r["recall"] for r in rows]
    precisions = [r["precision"] for r in rows]
    f1s = [r["f1"] for r in rows]
    crisis_densities = [r["crisis_density"] for r in rows]
    
    correlations = {
        "observed_pct_vs_recall": corr(observed_pcts, recalls),
        "observed_pct_vs_precision": corr(observed_pcts, precisions),
        "observed_pct_vs_f1": corr(observed_pcts, f1s),
        "var_completeness_vs_recall": corr(var_comps, recalls),
        "var_completeness_vs_precision": corr(var_comps, precisions),
        "var_completeness_vs_f1": corr(var_comps, f1s),
        "crisis_density_vs_recall": corr(crisis_densities, recalls),
        "crisis_density_vs_precision": corr(crisis_densities, precisions),
        "crisis_density_vs_f1": corr(crisis_densities, f1s),
    }
    
    return {"per_nga_rows": rows, "correlations": correlations}


def compare_v14a_v15a(data):
    """Compare aggregate metrics between v14a (5 NGAs) and v15a (all processed)."""
    v14a_ngas = {"Upper Egypt", "Latium", "Susiana", "Middle Yellow River Valley", "Valley of Oaxaca"}
    per_nga = data["per_nga_summary"]
    
    # v14a subset
    v14a_tp = sum(per_nga[n]["metrics"]["tp"] for n in v14a_ngas if n in per_nga)
    v14a_fp = sum(per_nga[n]["metrics"]["fp"] for n in v14a_ngas if n in per_nga)
    v14a_fn = sum(per_nga[n]["metrics"]["fn"] for n in v14a_ngas if n in per_nga)
    v14a_tn = sum(per_nga[n]["metrics"]["tn"] for n in v14a_ngas if n in per_nga)
    v14a_recall = v14a_tp / (v14a_tp + v14a_fn) if (v14a_tp + v14a_fn) > 0 else 0.0
    v14a_precision = v14a_tp / (v14a_tp + v14a_fp) if (v14a_tp + v14a_fp) > 0 else 0.0
    v14a_f1 = 2 * v14a_precision * v14a_recall / (v14a_precision + v14a_recall) if (v14a_precision + v14a_recall) > 0 else 0.0
    
    agg = data["aggregate_metrics"]
    
    return {
        "v14a_subset": {
            "ngas": 5,
            "tp": v14a_tp,
            "fp": v14a_fp,
            "fn": v14a_fn,
            "tn": v14a_tn,
            "recall": round(v14a_recall, 3),
            "precision": round(v14a_precision, 3),
            "f1": round(v14a_f1, 3),
        },
        "v15a_full": {
            "ngas": agg["ngas_processed"],
            "tp": agg["total_tp"],
            "fp": agg["total_fp"],
            "fn": agg["total_fn"],
            "tn": agg["total_tn"],
            "recall": agg["aggregate_recall"],
            "precision": agg["aggregate_precision"],
            "f1": agg["aggregate_f1"],
        },
        "precision_change": round(agg["aggregate_precision"] - v14a_precision, 3),
        "recall_change": round(agg["aggregate_recall"] - v14a_recall, 3),
        "f1_change": round(agg["aggregate_f1"] - v14a_f1, 3),
    }


def main():
    if not os.path.exists(RESULTS_JSON):
        print(f"[FATAL] Results not found at {RESULTS_JSON}")
        sys.exit(1)
    
    data = load_results(RESULTS_JSON)
    
    print("=" * 70)
    print("v15a Precision Analysis")
    print("=" * 70)
    
    # 1. Cumulative metrics as NGAs added
    print("\n[1] Cumulative metrics as NGAs are added (v14a first, then new by quality)")
    print("-" * 70)
    cum = analyze_precision_vs_nga_count(data)
    print(f"{'Count':>5} | {'NGA':<25} | {'v14a?':>5} | {'Recall':>7} | {'Precision':>9} | {'F1':>6}")
    print("-" * 70)
    for row in cum:
        print(f"{row['nga_count']:>5} | {row['nga_name']:<25} | {'Yes' if row['is_v14a'] else 'No':>5} | {row['cum_recall']:>7.3f} | {row['cum_precision']:>9.3f} | {row['cum_f1']:>6.3f}")
    
    # 2. Completeness correlation
    print("\n[2] Per-NGA metrics vs data completeness")
    print("-" * 70)
    comp = analyze_precision_vs_completeness(data)
    print(f"{'NGA':<25} | {'Obs%':>5} | {'Var%':>5} | {'Interp%':>7} | {'Crisis#':>7} | {'Recall':>6} | {'Prec':>6} | {'F1':>6}")
    print("-" * 70)
    for r in comp["per_nga_rows"]:
        print(f"{r['nga']:<25} | {r['observed_pct']:>5.1f} | {r['avg_variable_completeness']:>5.1f} | {r['interpolated_pct']:>7.1f} | {r['n_crisis_known']:>7} | {r['recall']:>6.3f} | {r['precision']:>6.3f} | {r['f1']:>6.3f}")
    
    print("\n[2b] Correlations (Pearson r)")
    print("-" * 70)
    for k, v in comp["correlations"].items():
        print(f"  {k}: {v if v is not None else 'N/A'}")
    
    # 3. v14a vs v15a comparison
    print("\n[3] v14a (5 NGAs) vs v15a (all processed) comparison")
    print("-" * 70)
    comp_v = compare_v14a_v15a(data)
    v14 = comp_v["v14a_subset"]
    v15 = comp_v["v15a_full"]
    print(f"{'Metric':<15} | {'v14a':>10} | {'v15a':>10} | {'Change':>10}")
    print("-" * 70)
    print(f"{'NGAs':<15} | {v14['ngas']:>10} | {v15['ngas']:>10} | {v15['ngas'] - v14['ngas']:>+10}")
    print(f"{'TP':<15} | {v14['tp']:>10} | {v15['tp']:>10} | {v15['tp'] - v14['tp']:>+10}")
    print(f"{'FP':<15} | {v14['fp']:>10} | {v15['fp']:>10} | {v15['fp'] - v14['fp']:>+10}")
    print(f"{'FN':<15} | {v14['fn']:>10} | {v15['fn']:>10} | {v15['fn'] - v14['fn']:>+10}")
    print(f"{'Recall':<15} | {v14['recall']:>10.3f} | {v15['recall']:>10.3f} | {comp_v['recall_change']:>+10.3f}")
    print(f"{'Precision':<15} | {v14['precision']:>10.3f} | {v15['precision']:>10.3f} | {comp_v['precision_change']:>+10.3f}")
    print(f"{'F1':<15} | {v14['f1']:>10.3f} | {v15['f1']:>10.3f} | {comp_v['f1_change']:>+10.3f}")
    
    # 4. Key findings
    print("\n[4] Key Findings")
    print("-" * 70)
    if comp_v["precision_change"] > 0:
        print(f"  ✓ Precision IMPROVED by {comp_v['precision_change']:.3f} with expansion")
    elif comp_v["precision_change"] < 0:
        print(f"  ✗ Precision WORSENED by {comp_v['precision_change']:.3f} with expansion")
    else:
        print(f"  → Precision UNCHANGED at {v15['precision']:.3f}")
    
    if comp_v["recall_change"] > 0:
        print(f"  ✓ Recall IMPROVED by {comp_v['recall_change']:.3f} with expansion")
    elif comp_v["recall_change"] < 0:
        print(f"  ✗ Recall WORSENED by {comp_v['recall_change']:.3f} with expansion")
    else:
        print(f"  → Recall UNCHANGED at {v15['recall']:.3f}")
    
    # Identify best/worst performers
    per_nga = data["per_nga_summary"]
    best_recall = max(per_nga.items(), key=lambda x: x[1]["metrics"]["recall"])
    worst_recall = min(per_nga.items(), key=lambda x: x[1]["metrics"]["recall"])
    best_precision = max(per_nga.items(), key=lambda x: x[1]["metrics"]["precision"])
    
    print(f"\n  Best recall: {best_recall[0]} ({best_recall[1]['metrics']['recall']})")
    print(f"  Worst recall: {worst_recall[0]} ({worst_recall[1]['metrics']['recall']})")
    print(f"  Best precision: {best_precision[0]} ({best_precision[1]['metrics']['precision']})")
    
    # Save structured output
    output = {
        "cumulative_analysis": cum,
        "completeness_analysis": comp,
        "v14a_vs_v15a": comp_v,
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[5] Structured analysis saved to {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
