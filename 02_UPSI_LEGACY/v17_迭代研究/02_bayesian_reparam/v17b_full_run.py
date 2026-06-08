#!/usr/bin/env python3
"""
v17b_full_run.py — 独立长时间运行脚本
=====================================

用途: 在后台执行完整的贝叶斯层次模型采样 (4 chains × 4000 draws)
运行方式: nohup python v17b_full_run.py > v17b_full_run.log 2>&1 &

配置:
  - N_CHAINS = 4
  - N_TUNE = 2000
  - N_DRAWS = 4000
  - TARGET_ACCEPT = 0.95
  - MAX_TREEDEPTH = 12

输出:
  - v17b_full_results.json (完整后验摘要)
  - v17b_full_trace.nc (ArviZ InferenceData, 可选)
  - v17b_full_report.md (Markdown 报告)

预计运行时间: 2-4 小时 (取决于 CPU)
"""

import sys
import os
import json
import time
import warnings
warnings.filterwarnings('ignore')

# 将项目根加入路径
sys.path.insert(0, "/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/02_bayesian_reparam")

# 导入 v17b 核心模块
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
    prior_sensitivity_analysis,
    generate_report,
)

OUTPUT_DIR = "/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/02_bayesian_reparam"
RESULTS_FILE = os.path.join(OUTPUT_DIR, "v17b_full_results.json")
REPORT_FILE = os.path.join(OUTPUT_DIR, "v17b_full_report.md")

# 覆盖为完整采样配置
import v17b_bayesian_reparam as v17b
v17b.N_CHAINS = 4
v17b.N_TUNE = 2000
v17b.N_DRAWS = 4000
v17b.TARGET_ACCEPT = 0.95
v17b.MAX_TREEDEPTH = 12

print("=" * 70)
print("v17b 完整贝叶斯采样 — 独立运行脚本")
print("=" * 70)
print(f"配置: {v17b.N_CHAINS} chains × {v17b.N_DRAWS} draws + {v17b.N_TUNE} tune")
print(f"预计时间: 2-4 小时")
print(f"输出: {RESULTS_FILE}")
print("=" * 70)

total_start = time.time()

# ============================================================
# 1. 加载数据
# ============================================================
print("\n[1/6] 加载跨域数据...")
data = prepare_all_data()
print(f"  总观测数: {len(data)}")
print(f"  有 SPI 的观测: {sum(1 for d in data if d['has_spi'])}")

# ============================================================
# 2. Model A (PSI-only) — 完整数据
# ============================================================
print("\n[2/6] Model A: PSI-only Bernoulli (完整数据)...")
try:
    t0 = time.time()
    model_a, trace_a, psi_mean_a, psi_std_a, n_dom_a, elapsed_a = build_model_a_reparam(data, "medium")
    results_a = analyze_model_a(trace_a, psi_mean_a, psi_std_a, n_dom_a)
    results_a["model"] = "A_psi_only_full"
    results_a["elapsed_seconds"] = elapsed_a
    waic_a = compute_waic_loo(trace_a)
    results_a["waic_loo"] = waic_a
    print(f"  ✓ 完成 ({elapsed_a:.1f}s)")
    print(f"  P(β₀ < 0) = {results_a.get('p_beta_negative', 'N/A'):.4f}")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    results_a = {"model": "A_psi_only_full", "error": str(e)}

# ============================================================
# 3. Model A (PSI-only) — 子集 (有 SPI 的数据, 用于与 B 比较)
# ============================================================
print("\n[3/6] Model A: PSI-only Bernoulli (SPI 子集)...")
data_b_subset = [d for d in data if not np.isnan(d["psi"]) and not np.isnan(d["spi"])]
try:
    t0 = time.time()
    model_a_sub, trace_a_sub, psi_mean_as, psi_std_as, n_dom_as, elapsed_as = build_model_a_reparam(data_b_subset, "medium")
    results_a_sub = analyze_model_a(trace_a_sub, psi_mean_as, psi_std_as, n_dom_as)
    results_a_sub["model"] = "A_psi_only_subset"
    results_a_sub["elapsed_seconds"] = elapsed_as
    print(f"  ✓ 完成 ({elapsed_as:.1f}s)")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    results_a_sub = {"model": "A_psi_only_subset", "error": str(e)}

# ============================================================
# 4. Model B (PSI+SPI 联合)
# ============================================================
print("\n[4/6] Model B: PSI+SPI 联合模型...")
try:
    t0 = time.time()
    model_b, trace_b, psi_mean_b, psi_std_b, spi_mean_b, spi_std_b, n_dom_b, elapsed_b = build_model_b_reparam(data_b_subset, "medium")
    results_b = analyze_model_b(trace_b, psi_mean_b, psi_std_b, spi_mean_b, spi_std_b, n_dom_b)
    results_b["model"] = "B_psi_spi_joint"
    results_b["elapsed_seconds"] = elapsed_b
    waic_b = compute_waic_loo(trace_b)
    results_b["waic_loo"] = waic_b
    print(f"  ✓ 完成 ({elapsed_b:.1f}s)")
    print(f"  P(β₁ < 0) = {results_b.get('p_beta1_negative', 'N/A'):.4f}")
    print(f"  P(β₂ > 0) = {results_b.get('p_beta2_positive', 'N/A'):.4f}")
    print(f"  PSI importance = {results_b.get('psi_importance', 'N/A'):.4f}")
    print(f"  SPI importance = {results_b.get('spi_importance', 'N/A'):.4f}")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    results_b = {"model": "B_psi_spi_joint", "error": str(e)}

# ============================================================
# 5. Model C (UPSI_v2 二元回退)
# ============================================================
print("\n[5/6] Model C: UPSI_v2 二元分类...")
try:
    t0 = time.time()
    model_c, trace_c, n_dom_c, n_quad_c, elapsed_c, is_binary = build_model_c_reparam(data_b_subset, "medium", binary_fallback=True)
    results_c = analyze_model_c(trace_c, n_dom_c, n_quad_c, is_binary)
    results_c["model"] = "C_upsi_v2_binary"
    results_c["elapsed_seconds"] = elapsed_c
    waic_c = compute_waic_loo(trace_c)
    results_c["waic_loo"] = waic_c
    print(f"  ✓ 完成 ({elapsed_c:.1f}s)")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    results_c = {"model": "C_upsi_v2_binary", "error": str(e)}

# ============================================================
# 6. 模型比较 & 后验预测
# ============================================================
print("\n[6/6] 模型比较与后验预测...")

# WAIC/LOO 比较
try:
    if "error" not in results_a_sub and "error" not in results_b:
        comparison = compare_models_ab(trace_a, trace_a_sub, trace_b)
        print(f"  Model comparison: {comparison.get('winner', 'N/A')} wins")
    else:
        comparison = {"error": "One or more models failed"}
except Exception as e:
    comparison = {"error": str(e)}

# 后验预测
try:
    if "error" not in results_b:
        pp_b = posterior_predictive_model_b(trace_b, psi_mean_b, psi_std_b, spi_mean_b, spi_std_b)
    else:
        pp_b = {"error": "Model B failed"}
except Exception as e:
    pp_b = {"error": str(e)}

try:
    if "error" not in results_c:
        pp_c = posterior_predictive_model_c(trace_c, True)
    else:
        pp_c = {"error": "Model C failed"}
except Exception as e:
    pp_c = {"error": str(e)}

# ============================================================
# 7. 汇总保存
# ============================================================
print("\n" + "=" * 70)
print("汇总与保存")
print("=" * 70)

all_results = {
    "config": {
        "n_chains": v17b.N_CHAINS,
        "n_tune": v17b.N_TUNE,
        "n_draws": v17b.N_DRAWS,
        "target_accept": v17b.TARGET_ACCEPT,
        "max_treedepth": v17b.MAX_TREEDEPTH,
    },
    "data_summary": {
        "total_observations": len(data),
        "spi_available": sum(1 for d in data if d["has_spi"]),
        "domains": list(set(d["domain"] for d in data)),
    },
    "model_a_full": results_a,
    "model_a_subset": results_a_sub,
    "model_b": results_b,
    "model_c": results_c,
    "model_comparison": comparison,
    "posterior_predictive_b": pp_b,
    "posterior_predictive_c": pp_c,
    "total_elapsed_seconds": time.time() - total_start,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
}

with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

print(f"  ✓ 结果已保存: {RESULTS_FILE}")

# 生成 Markdown 报告
try:
    report = generate_report(all_results, REPORT_FILE)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✓ 报告已保存: {REPORT_FILE}")
except Exception as e:
    print(f"  ⚠ 报告生成失败: {e}")

print(f"\n总耗时: {all_results['total_elapsed_seconds'] / 3600:.2f} 小时")
print("=" * 70)
print("运行完成。请检查 divergences 和 R-hat 值。")
print("=" * 70)
