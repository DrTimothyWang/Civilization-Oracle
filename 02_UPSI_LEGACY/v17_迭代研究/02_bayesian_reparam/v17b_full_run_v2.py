#!/usr/bin/env python3
"""
v17b_full_run_v2.py — 精简版完整采样脚本
"""
import sys
import os
import json
import time
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, "/Users/wangzr/Desktop/历史事件预测建模/02_UPSI_LEGACY/v17_迭代研究/02_bayesian_reparam")

import numpy as np
import pymc as pm
import arviz as az

from v17b_bayesian_reparam import (
    prepare_all_data,
    build_model_a_reparam,
    build_model_b_reparam,
    build_model_c_reparam,
    analyze_model_a,
    analyze_model_b,
    analyze_model_c,
    compute_waic_loo,
    compare_models_ab,
    posterior_predictive_model_b,
    posterior_predictive_model_c,
    generate_report,
)

OUTPUT_DIR = "/Users/wangzr/Desktop/历史事件预测建模/01_TCM_UPSI_CORE"
os.makedirs(OUTPUT_DIR, exist_ok=True)
RESULTS_FILE = os.path.join(OUTPUT_DIR, "v17b_full_sampling_results.json")
REPORT_FILE = os.path.join(OUTPUT_DIR, "v17b_full_sampling_report.md")

import v17b_bayesian_reparam as v17b
v17b.N_CHAINS = 4
v17b.N_TUNE = 2000
v17b.N_DRAWS = 4000
v17b.TARGET_ACCEPT = 0.99
v17b.MAX_TREEDEPTH = 15

print("=" * 70)
print("v17b 完整贝叶斯采样")
print(f"配置: {v17b.N_CHAINS} chains × {v17b.N_DRAWS} draws + {v17b.N_TUNE} tune")
print(f"target_accept={v17b.TARGET_ACCEPT}, max_treedepth={v17b.MAX_TREEDEPTH}")
print("=" * 70)

total_start = time.time()
all_results = {}

# 1. 数据
print("\n[1/6] 加载数据...")
data = prepare_all_data()
print(f"  总观测: {len(data)}")

# 2. Model A
print("\n[2/6] Model A (PSI-only)...")
try:
    t0 = time.time()
    model_a, trace_a, psi_mean_a, psi_std_a, n_dom_a, elapsed_a = build_model_a_reparam(data, "medium")
    results_a = analyze_model_a(trace_a, psi_mean_a, psi_std_a, n_dom_a)
    results_a["model"] = "A_psi_only_full"
    results_a["elapsed_seconds"] = elapsed_a
    waic_a = compute_waic_loo(trace_a)
    results_a["waic_loo"] = waic_a
    
    # Convergence check
    div_a = int(trace_a.sample_stats.diverging.values.sum())
    summary_a = az.summary(trace_a, var_names=["alpha_0", "beta_0", "sigma_alpha", "sigma_beta"])
    max_rhat_a = float(summary_a["r_hat"].max())
    min_ess_bulk_a = float(summary_a["ess_bulk"].min())
    min_ess_tail_a = float(summary_a["ess_tail"].min())
    results_a["convergence_check"] = {
        "divergences": div_a,
        "max_rhat": max_rhat_a,
        "min_ess_bulk": min_ess_bulk_a,
        "min_ess_tail": min_ess_tail_a,
        "pass_divergences": div_a == 0,
        "pass_rhat": max_rhat_a < 1.01,
        "pass_ess_bulk": min_ess_bulk_a > 1000,
        "pass_ess_tail": min_ess_tail_a > 1000,
    }
    print(f"  ✓ 完成 ({elapsed_a:.1f}s), div={div_a}, rhat={max_rhat_a:.4f}, ess_bulk={min_ess_bulk_a:.0f}")
    all_results["model_a_full"] = results_a
except Exception as e:
    print(f"  ✗ 失败: {e}")
    all_results["model_a_full"] = {"error": str(e)}

# 3. Model A subset
print("\n[3/6] Model A (子集, SPI域)...")
data_b_subset = [d for d in data if not np.isnan(d["psi"]) and not np.isnan(d["spi"])]
try:
    t0 = time.time()
    model_a_sub, trace_a_sub, psi_mean_as, psi_std_as, n_dom_as, elapsed_as = build_model_a_reparam(data_b_subset, "medium")
    results_a_sub = analyze_model_a(trace_a_sub, psi_mean_as, psi_std_as, n_dom_as)
    results_a_sub["model"] = "A_psi_only_subset"
    results_a_sub["elapsed_seconds"] = elapsed_as
    div_as = int(trace_a_sub.sample_stats.diverging.values.sum())
    summary_as = az.summary(trace_a_sub, var_names=["alpha_0", "beta_0", "sigma_alpha", "sigma_beta"])
    max_rhat_as = float(summary_as["r_hat"].max())
    min_ess_bulk_as = float(summary_as["ess_bulk"].min())
    min_ess_tail_as = float(summary_as["ess_tail"].min())
    results_a_sub["convergence_check"] = {
        "divergences": div_as,
        "max_rhat": max_rhat_as,
        "min_ess_bulk": min_ess_bulk_as,
        "min_ess_tail": min_ess_tail_as,
        "pass_divergences": div_as == 0,
        "pass_rhat": max_rhat_as < 1.01,
        "pass_ess_bulk": min_ess_bulk_as > 1000,
        "pass_ess_tail": min_ess_tail_as > 1000,
    }
    print(f"  ✓ 完成 ({elapsed_as:.1f}s), div={div_as}, rhat={max_rhat_as:.4f}, ess_bulk={min_ess_bulk_as:.0f}")
    all_results["model_a_subset"] = results_a_sub
except Exception as e:
    print(f"  ✗ 失败: {e}")
    all_results["model_a_subset"] = {"error": str(e)}

# 4. Model B
print("\n[4/6] Model B (PSI+SPI)...")
try:
    t0 = time.time()
    model_b, trace_b, psi_mean_b, psi_std_b, spi_mean_b, spi_std_b, n_dom_b, elapsed_b = build_model_b_reparam(data_b_subset, "medium")
    results_b = analyze_model_b(trace_b, psi_mean_b, psi_std_b, spi_mean_b, spi_std_b, n_dom_b)
    results_b["model"] = "B_psi_spi_joint"
    results_b["elapsed_seconds"] = elapsed_b
    waic_b = compute_waic_loo(trace_b)
    results_b["waic_loo"] = waic_b
    
    div_b = int(trace_b.sample_stats.diverging.values.sum())
    summary_b = az.summary(trace_b, var_names=["alpha_0", "beta1_0", "beta2_0", "sigma_alpha", "sigma_beta1", "sigma_beta2"])
    max_rhat_b = float(summary_b["r_hat"].max())
    min_ess_bulk_b = float(summary_b["ess_bulk"].min())
    min_ess_tail_b = float(summary_b["ess_tail"].min())
    results_b["convergence_check"] = {
        "divergences": div_b,
        "max_rhat": max_rhat_b,
        "min_ess_bulk": min_ess_bulk_b,
        "min_ess_tail": min_ess_tail_b,
        "pass_divergences": div_b == 0,
        "pass_rhat": max_rhat_b < 1.01,
        "pass_ess_bulk": min_ess_bulk_b > 1000,
        "pass_ess_tail": min_ess_tail_b > 1000,
    }
    print(f"  ✓ 完成 ({elapsed_b:.1f}s), div={div_b}, rhat={max_rhat_b:.4f}, ess_bulk={min_ess_bulk_b:.0f}")
    all_results["model_b"] = results_b
except Exception as e:
    print(f"  ✗ 失败: {e}")
    all_results["model_b"] = {"error": str(e)}

# 5. Model C
print("\n[5/6] Model C (UPSI_v2 二元)...")
try:
    t0 = time.time()
    model_c, trace_c, n_dom_c, n_quad_c, elapsed_c, is_binary = build_model_c_reparam(data_b_subset, "medium", binary_fallback=True)
    results_c = analyze_model_c(trace_c, n_dom_c, n_quad_c, is_binary)
    results_c["model"] = "C_upsi_v2_binary"
    results_c["elapsed_seconds"] = elapsed_c
    waic_c = compute_waic_loo(trace_c)
    results_c["waic_loo"] = waic_c
    
    div_c = int(trace_c.sample_stats.diverging.values.sum())
    summary_c = az.summary(trace_c, var_names=["gamma_0", "delta_0", "sigma_gamma", "sigma_delta"])
    max_rhat_c = float(summary_c["r_hat"].max())
    min_ess_bulk_c = float(summary_c["ess_bulk"].min())
    min_ess_tail_c = float(summary_c["ess_tail"].min())
    results_c["convergence_check"] = {
        "divergences": div_c,
        "max_rhat": max_rhat_c,
        "min_ess_bulk": min_ess_bulk_c,
        "min_ess_tail": min_ess_tail_c,
        "pass_divergences": div_c == 0,
        "pass_rhat": max_rhat_c < 1.01,
        "pass_ess_bulk": min_ess_bulk_c > 1000,
        "pass_ess_tail": min_ess_tail_c > 1000,
    }
    print(f"  ✓ 完成 ({elapsed_c:.1f}s), div={div_c}, rhat={max_rhat_c:.4f}, ess_bulk={min_ess_bulk_c:.0f}")
    all_results["model_c"] = results_c
except Exception as e:
    print(f"  ✗ 失败: {e}")
    all_results["model_c"] = {"error": str(e)}

# 6. 模型比较 & 后验预测
print("\n[6/6] 模型比较与后验预测...")
try:
    if "error" not in all_results.get("model_a_subset", {}) and "error" not in all_results.get("model_b", {}):
        comparison = compare_models_ab(trace_a, trace_a_sub, trace_b)
        all_results["model_comparison"] = comparison
        print(f"  ✓ 模型比较完成")
    else:
        all_results["model_comparison"] = {"error": "Model A or B failed"}
except Exception as e:
    all_results["model_comparison"] = {"error": str(e)}

try:
    if "error" not in all_results.get("model_b", {}):
        pp_b = posterior_predictive_model_b(trace_b, psi_mean_b, psi_std_b, spi_mean_b, spi_std_b)
        all_results["posterior_predictive_b"] = pp_b
except Exception as e:
    all_results["posterior_predictive_b"] = {"error": str(e)}

try:
    if "error" not in all_results.get("model_c", {}):
        pp_c = posterior_predictive_model_c(trace_c, True)
        all_results["posterior_predictive_c"] = pp_c
except Exception as e:
    all_results["posterior_predictive_c"] = {"error": str(e)}

# 汇总
all_results["config"] = {
    "n_chains": v17b.N_CHAINS,
    "n_tune": v17b.N_TUNE,
    "n_draws": v17b.N_DRAWS,
    "target_accept": v17b.TARGET_ACCEPT,
    "max_treedepth": v17b.MAX_TREEDEPTH,
}
all_results["data_summary"] = {
    "total_observations": len(data),
    "spi_available": sum(1 for d in data if d["has_spi"]),
}
all_results["total_elapsed_seconds"] = time.time() - total_start
all_results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

# 保存 JSON
def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

with open(RESULTS_FILE, "w", encoding="utf-8") as f:
    json.dump(clean_for_json(all_results), f, indent=2, ensure_ascii=False, default=str)
print(f"\n✓ 结果已保存: {RESULTS_FILE}")

# 生成报告
try:
    report = generate_report(all_results, REPORT_FILE)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✓ 报告已保存: {REPORT_FILE}")
except Exception as e:
    print(f"⚠ 报告生成失败: {e}")

print(f"\n总耗时: {all_results['total_elapsed_seconds'] / 60:.1f} 分钟")
print("=" * 70)

# 最终收敛摘要
print("\n收敛诊断摘要:")
for name, key in [("Model A", "model_a_full"), ("Model B", "model_b"), ("Model C", "model_c")]:
    res = all_results.get(key, {})
    if "error" in res:
        print(f"  {name}: ✗ 失败 - {res['error']}")
    else:
        conv = res.get("convergence_check", {})
        status = "✓" if all(conv.get(k, False) for k in ["pass_divergences", "pass_rhat", "pass_ess_bulk", "pass_ess_tail"]) else "⚠"
        print(f"  {name}: {status} div={conv.get('divergences', 'N/A')}, rhat={conv.get('max_rhat', 0):.4f}, ess_bulk={conv.get('min_ess_bulk', 0):.0f}, ess_tail={conv.get('min_ess_tail', 0):.0f}")
