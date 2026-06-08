#!/usr/bin/env python3
"""
reproduce_bayesian.py
===================
Reproducible Bayesian hierarchical inference for TCM-UPSI v17B.

This script reproduces the full Bayesian analysis reported in:
- TCM_UPSI_Paper_v20_FINAL_Bayesian.md (Section 2.6)
- TCM_UPSI_Bayesian_Supplementary_v1.md (SI S16)

Requirements:
    pip install pymc arviz numpy pandas matplotlib seaborn

Usage:
    python reproduce_bayesian.py --data path/to/data.csv --output ./bayesian_output

Author: TCM-UPSI Research Team
Date: 2026-06-09
License: MIT
"""

import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import seaborn as sns
from matplotlib.gridspec import GridSpec

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "n_chains": 4,
    "n_tune": 2000,
    "n_draws": 4000,
    "target_accept": 0.99,
    "max_treedepth": 15,
    "random_seed": 42,
}

# Domain labels (7 domains)
DOMAIN_LABELS = [
    "中华历史", "美索不达米亚", "现代金融", "全球政治",
    "中国金融", "古罗马", "COVID"
]

# Domain labels (3-domain subset)
SUBSET_LABELS = ["中华历史", "美索不达米亚", "现代金融"]


# ---------------------------------------------------------------------------
# Model A: PSI-only (hierarchical, non-centered parameterization)
# ---------------------------------------------------------------------------
def build_model_a_psi_only(df: pd.DataFrame, domain_idx: pd.Series,
                           n_domains: int, **kwargs):
    """
    Model A: y ~ Bernoulli(logit⁻¹(αⱼ + βⱼ · PSI))
    Hierarchical priors with non-centered parameterization.
    """
    psi = df["psi"].values
    y = df["crisis"].values

    with pm.Model() as model:
        # Hyperpriors
        alpha_0 = pm.Normal("alpha_0", mu=0, sigma=1)
        beta_0 = pm.Normal("beta_0", mu=0, sigma=1)
        sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=0.3)
        sigma_beta = pm.HalfNormal("sigma_beta", sigma=0.3)

        # Non-centered domain effects
        alpha_tilde = pm.Normal("alpha_tilde", mu=0, sigma=1, shape=n_domains)
        beta_tilde = pm.Normal("beta_tilde", mu=0, sigma=1, shape=n_domains)

        alpha_j = alpha_0 + sigma_alpha * alpha_tilde
        beta_j = beta_0 + sigma_beta * beta_tilde

        # Linear predictor
        logit_p = alpha_j[domain_idx] + beta_j[domain_idx] * psi
        p = pm.Deterministic("p", pm.math.sigmoid(logit_p))

        # Likelihood
        pm.Bernoulli("y", p=p, observed=y)

    return model


# ---------------------------------------------------------------------------
# Model B: PSI + SPI joint (multivariate random effects)
# ---------------------------------------------------------------------------
def build_model_b_psi_spi(df: pd.DataFrame, domain_idx: pd.Series,
                          n_domains: int, **kwargs):
    """
    Model B: y ~ Bernoulli(logit⁻¹(αⱼ + β₁ⱼ·PSI + β₂ⱼ·SPI))
    Multivariate normal random effects via Cholesky decomposition.
    """
    psi = df["psi"].values
    spi = df["spi"].values
    y = df["crisis"].values

    with pm.Model() as model:
        alpha_0 = pm.Normal("alpha_0", mu=0, sigma=1)
        beta1_0 = pm.Normal("beta1_0", mu=0, sigma=1)
        beta2_0 = pm.Normal("beta2_0", mu=0, sigma=1)

        sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=0.3)
        sigma_beta1 = pm.HalfNormal("sigma_beta1", sigma=0.3)
        sigma_beta2 = pm.HalfNormal("sigma_beta2", sigma=0.3)

        # Cholesky for 3×3 correlation (alpha, beta1, beta2)
        chol, corr, stds = pm.LKJCholeskyCov(
            "chol", n=3, eta=2.0,
            sd_dist=pm.Exponential.dist(1.0),
            compute_corr=True
        )

        # Domain random effects
        domain_effects = pm.MultivariateNormal(
            "domain_effects", mu=0, chol=chol, shape=(n_domains, 3)
        )

        alpha_j = alpha_0 + sigma_alpha * domain_effects[:, 0]
        beta1_j = beta1_0 + sigma_beta1 * domain_effects[:, 1]
        beta2_j = beta2_0 + sigma_beta2 * domain_effects[:, 2]

        logit_p = (alpha_j[domain_idx]
                   + beta1_j[domain_idx] * psi
                   + beta2_j[domain_idx] * spi)
        p = pm.Deterministic("p", pm.math.sigmoid(logit_p))

        pm.Bernoulli("y", p=p, observed=y)

    return model


# ---------------------------------------------------------------------------
# Model C: UPSI_v2 binary (sudden vs gradual)
# ---------------------------------------------------------------------------
def build_model_c_upsi_binary(df: pd.DataFrame, domain_idx: pd.Series,
                              n_domains: int, **kwargs):
    """
    Model C: y ~ Bernoulli(logit⁻¹(γⱼ + δⱼ · UPSI_v2))
    Binary outcome: 1 = sudden crisis, 0 = gradual decline.
    """
    upsi_v2 = df["upsi_v2"].values
    y = df["sudden"].values

    with pm.Model() as model:
        gamma_0 = pm.Normal("gamma_0", mu=0, sigma=1)
        delta_0 = pm.Normal("delta_0", mu=0, sigma=1)
        sigma_gamma = pm.HalfNormal("sigma_gamma", sigma=0.3)
        sigma_delta = pm.HalfNormal("sigma_delta", sigma=0.3)

        gamma_tilde = pm.Normal("gamma_tilde", mu=0, sigma=1, shape=n_domains)
        delta_tilde = pm.Normal("delta_tilde", mu=0, sigma=1, shape=n_domains)

        gamma_j = gamma_0 + sigma_gamma * gamma_tilde
        delta_j = delta_0 + sigma_delta * delta_tilde

        logit_p = gamma_j[domain_idx] + delta_j[domain_idx] * upsi_v2
        p = pm.Deterministic("p", pm.math.sigmoid(logit_p))

        pm.Bernoulli("y", p=p, observed=y)

    return model


# ---------------------------------------------------------------------------
# Sampling wrapper
# ---------------------------------------------------------------------------
def sample_model(model, config: dict, model_name: str):
    """Run MCMC sampling with given configuration."""
    print(f"\n{'='*60}")
    print(f"Sampling {model_name}")
    print(f"Config: {config['n_chains']} chains × {config['n_draws']} draws")
    print(f"{'='*60}")

    t0 = time.time()
    with model:
        idata = pm.sample(
            draws=config["n_draws"],
            tune=config["n_tune"],
            chains=config["n_chains"],
            target_accept=config["target_accept"],
            max_treedepth=config["max_treedepth"],
            random_seed=config["random_seed"],
            return_inferencedata=True,
        )
    elapsed = time.time() - t0
    print(f"Sampling complete: {elapsed:.1f}s")
    return idata, elapsed


# ---------------------------------------------------------------------------
# Convergence diagnostics
# ---------------------------------------------------------------------------
def convergence_summary(idata, model_name: str):
    """Extract convergence diagnostics comparable to ArviZ summary."""
    summary = az.summary(idata, kind="diagnostics")

    max_rhat = summary["r_hat"].max()
    min_ess_bulk = summary["ess_bulk"].min()
    min_ess_tail = summary["ess_tail"].min()
    divergences = int(idata.sample_stats.diverging.sum().values)

    status_rhat = "✓" if max_rhat < 1.01 else "⚠ 警告" if max_rhat < 1.1 else "✗ 严重"
    status_ess = "✓" if min_ess_bulk > 400 else "⚠ 警告"
    status_div = "✓" if divergences == 0 else "✗ 严重" if divergences > 100 else "⚠ 注意"

    print(f"\n--- Convergence: {model_name} ---")
    print(f"  max r_hat      = {max_rhat:.4f}  {status_rhat}")
    print(f"  min ESS (bulk) = {min_ess_bulk:.0f}  {status_ess}")
    print(f"  min ESS (tail) = {min_ess_tail:.0f}  {status_ess}")
    print(f"  divergences    = {divergences}  {status_div}")

    return {
        "max_rhat": float(max_rhat),
        "min_ess_bulk": float(min_ess_bulk),
        "min_ess_tail": float(min_ess_tail),
        "divergences": divergences,
        "status_rhat": status_rhat,
        "status_ess": status_ess,
        "status_divergences": status_div,
    }


# ---------------------------------------------------------------------------
# Posterior extraction
# ---------------------------------------------------------------------------
def extract_posterior_a(idata, domain_labels):
    """Extract Model A posterior quantities."""
    post = idata.posterior
    beta_0 = post["beta_0"].values.flatten()

    results = {
        "p_beta_negative": float((beta_0 < 0).mean()),
        "beta_0_mean": float(beta_0.mean()),
        "beta_0_hdi": [float(np.percentile(beta_0, 3)), float(np.percentile(beta_0, 97))],
        "domain_effects": [],
    }

    for i, label in enumerate(domain_labels):
        alpha = post["alpha_tilde"].values[:, :, i].flatten()
        beta = post["beta_tilde"].values[:, :, i].flatten()
        # Reconstruct domain-level beta_j = beta_0 + sigma_beta * beta_tilde
        sigma_beta = post["sigma_beta"].values.flatten()
        beta_j = beta_0 + sigma_beta * beta

        results["domain_effects"].append({
            "domain": label,
            "mean": float(beta_j.mean()),
            "hdi_low": float(np.percentile(beta_j, 3)),
            "hdi_high": float(np.percentile(beta_j, 97)),
            "p_negative": float((beta_j < 0).mean()),
        })

    sigma_beta = post["sigma_beta"].values.flatten()
    results["sigma_beta_mean"] = float(sigma_beta.mean())
    results["sigma_beta_hdi"] = [float(np.percentile(sigma_beta, 3)),
                                   float(np.percentile(sigma_beta, 97))]
    results["p_low_heterogeneity"] = float((sigma_beta < 1).mean())

    return results


def extract_posterior_b(idata, domain_labels):
    """Extract Model B posterior quantities."""
    post = idata.posterior
    beta1_0 = post["beta1_0"].values.flatten()
    beta2_0 = post["beta2_0"].values.flatten()

    results = {
        "beta1_0_mean": float(beta1_0.mean()),
        "beta1_0_hdi": [float(np.percentile(beta1_0, 3)), float(np.percentile(beta1_0, 97))],
        "p_beta1_negative": float((beta1_0 < 0).mean()),
        "beta2_0_mean": float(beta2_0.mean()),
        "beta2_0_hdi": [float(np.percentile(beta2_0, 3)), float(np.percentile(beta2_0, 97))],
        "p_beta2_positive": float((beta2_0 > 0).mean()),
        "domain_effects": [],
    }

    for i, label in enumerate(domain_labels):
        beta1_j = (post["beta1_0"].values.flatten()
                   + post["sigma_beta1"].values.flatten()
                   * post["domain_effects"].values[:, :, i, 1].flatten())
        beta2_j = (post["beta2_0"].values.flatten()
                   + post["sigma_beta2"].values.flatten()
                   * post["domain_effects"].values[:, :, i, 2].flatten())

        results["domain_effects"].append({
            "domain": label,
            "beta1_mean": float(beta1_j.mean()),
            "beta1_hdi": [float(np.percentile(beta1_j, 3)), float(np.percentile(beta1_j, 97))],
            "beta2_mean": float(beta2_j.mean()),
            "beta2_hdi": [float(np.percentile(beta2_j, 3)), float(np.percentile(beta2_j, 97))],
        })

    # Correlation matrix
    corr = post["chol_corr"].values  # shape: (chain, draw, 3, 3)
    corr_mean = corr.mean(axis=(0, 1))
    results["correlation_matrix_mean"] = corr_mean.tolist()
    results["corr_alpha_beta1"] = float(corr_mean[0, 1])
    results["corr_alpha_beta2"] = float(corr_mean[0, 2])
    results["corr_beta1_beta2"] = float(corr_mean[1, 2])

    return results


def extract_posterior_c(idata, domain_labels):
    """Extract Model C posterior quantities."""
    post = idata.posterior
    delta_0 = post["delta_0"].values.flatten()

    results = {
        "delta_0_mean": float(delta_0.mean()),
        "delta_0_hdi": [float(np.percentile(delta_0, 3)), float(np.percentile(delta_0, 97))],
        "p_delta_positive": float((delta_0 > 0).mean()),
        "domain_effects": [],
    }

    for i, label in enumerate(domain_labels):
        p_sudden = post["p"].values[:, :, i].flatten()  # approximate
        # Use mean p for this domain as proxy
        gamma_j = (post["gamma_0"].values.flatten()
                   + post["sigma_gamma"].values.flatten()
                   * post["gamma_tilde"].values[:, :, i].flatten())
        delta_j = (post["delta_0"].values.flatten()
                   + post["sigma_delta"].values.flatten()
                   * post["delta_tilde"].values[:, :, i].flatten())

        # For binary model, p_sudden at upsi_v2=0 and upsi_v2=1
        p_stable = 1 / (1 + np.exp(-gamma_j))
        p_crisis = 1 / (1 + np.exp(-(gamma_j + delta_j)))

        results["domain_effects"].append({
            "domain": label,
            "p_sudden_stable": float(p_stable.mean()),
            "p_sudden_crisis": float(p_crisis.mean()),
            "delta_mean": float(delta_j.mean()),
        })

    return results


# ---------------------------------------------------------------------------
# WAIC / LOO comparison
# ---------------------------------------------------------------------------
def compare_models(idata_a, idata_b, idata_c):
    """Compare models via WAIC and LOO-CV."""
    comp = az.compare({
        "Model A (PSI-only)": idata_a,
        "Model B (PSI+SPI)": idata_b,
        "Model C (UPSI_v2)": idata_c,
    }, ic="waic", scale="deviance")

    print("\n--- Model Comparison (WAIC) ---")
    print(comp[["rank", "waic", "d_waic", "weight"]])
    return comp


# ---------------------------------------------------------------------------
# Figure generation
# ---------------------------------------------------------------------------
def plot_figure_s1(idata_a, idata_b, idata_c, output_dir: Path):
    """Figure S1: Convergence diagnostics panel."""
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 3, figure=fig)

    models = [("Model A", idata_a), ("Model B", idata_b), ("Model C", idata_c)]

    for row, (name, idata) in enumerate(models):
        summary = az.summary(idata, kind="diagnostics")

        # r_hat
        ax1 = fig.add_subplot(gs[row, 0])
        ax1.hist(summary["r_hat"].dropna(), bins=30, color="steelblue", edgecolor="white")
        ax1.axvline(1.01, color="red", linestyle="--", label="threshold=1.01")
        ax1.set_title(f"{name}: R-hat")
        ax1.set_xlabel("R-hat")
        ax1.legend()

        # ESS bulk
        ax2 = fig.add_subplot(gs[row, 1])
        ax2.hist(summary["ess_bulk"].dropna(), bins=30, color="seagreen", edgecolor="white")
        ax2.axvline(400, color="red", linestyle="--", label="threshold=400")
        ax2.set_title(f"{name}: ESS (bulk)")
        ax2.set_xlabel("ESS")
        ax2.legend()

        # ESS tail
        ax3 = fig.add_subplot(gs[row, 2])
        ax3.hist(summary["ess_tail"].dropna(), bins=30, color="coral", edgecolor="white")
        ax3.axvline(400, color="red", linestyle="--", label="threshold=400")
        ax3.set_title(f"{name}: ESS (tail)")
        ax3.set_xlabel("ESS")
        ax3.legend()

    plt.suptitle("Figure S1: Convergence Diagnostics (R-hat / ESS bulk / ESS tail)",
                 fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / "Figure_S1_convergence_diagnostics.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  → Figure S1 saved")


def plot_figure_s2(results_a, domain_labels, output_dir: Path):
    """Figure S2: Forest plot of domain effects."""
    effects = results_a["domain_effects"]
    domains = [e["domain"] for e in effects]
    means = [e["mean"] for e in effects]
    hdi_low = [e["hdi_low"] for e in effects]
    hdi_high = [e["hdi_high"] for e in effects]

    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(domains))

    ax.errorbar(means, y_pos,
                xerr=[np.array(means) - np.array(hdi_low),
                      np.array(hdi_high) - np.array(means)],
                fmt="o", color="steelblue", ecolor="lightgray",
                capsize=5, markersize=8, elinewidth=2)

    ax.axvline(0, color="red", linestyle="--", alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(domains)
    ax.set_xlabel("Domain-level βⱼ (PSI effect)")
    ax.set_title("Figure S2: Model A Domain Effects with 94% HDI")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_dir / "Figure_S2_forest_plot.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  → Figure S2 saved")


def plot_figure_s3(comp_df, output_dir: Path):
    """Figure S3: WAIC comparison."""
    fig, ax = plt.subplots(figsize=(8, 5))
    models = comp_df.index.tolist()
    waic = comp_df["waic"].values
    d_waic = comp_df["d_waic"].values

    colors = ["steelblue" if d == 0 else "lightgray" for d in d_waic]
    bars = ax.barh(models, waic, color=colors, edgecolor="black")

    ax.set_xlabel("WAIC (deviance scale, lower = better)")
    ax.set_title("Figure S3: Model Comparison via WAIC")
    ax.invert_yaxis()

    for bar, d in zip(bars, d_waic):
        width = bar.get_width()
        ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                f"Δ={d:.1f}", ha="left", va="center", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / "Figure_S3_waic_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  → Figure S3 saved")


def plot_figure_s4(results_b, output_dir: Path):
    """Figure S4: Correlation heatmap (Model B)."""
    corr = np.array(results_b["correlation_matrix_mean"])
    labels = ["α (intercept)", "β₁ (PSI)", "β₂ (SPI)"]

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1,
                xticklabels=labels, yticklabels=labels,
                square=True, linewidths=0.5, ax=ax)
    ax.set_title("Figure S4: Model B Posterior Correlation Matrix")
    plt.tight_layout()
    plt.savefig(output_dir / "Figure_S4_correlation_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  → Figure S4 saved")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Reproduce TCM-UPSI v17B Bayesian analysis")
    parser.add_argument("--data", type=str, default=None,
                        help="Path to CSV data file (optional; uses synthetic if missing)")
    parser.add_argument("--output", type=str, default="./bayesian_output",
                        help="Output directory for results and figures")
    parser.add_argument("--subset-only", action="store_true",
                        help="Run only 3-domain subset models (faster)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Data loading (or synthetic generation for reproducibility testing)
    # -----------------------------------------------------------------------
    if args.data and Path(args.data).exists():
        df = pd.read_csv(args.data)
        print(f"Loaded data: {len(df)} rows from {args.data}")
    else:
        print("No data file provided; generating synthetic data for reproducibility testing.")
        print("NOTE: For exact reproduction of paper results, provide the real dataset.")
        np.random.seed(42)
        n = 67  # subset size
        df = pd.DataFrame({
            "psi": np.random.normal(0, 1, n),
            "spi": np.random.normal(0, 1, n),
            "upsi_v2": np.random.normal(0, 1, n),
            "crisis": np.random.binomial(1, 0.3, n),
            "sudden": np.random.binomial(1, 0.5, n),
            "domain": np.random.choice([0, 1, 2], n),
        })

    # Domain index
    domain_map = {d: i for i, d in enumerate(sorted(df["domain"].unique()))}
    domain_idx = df["domain"].map(domain_map).values
    n_domains = len(domain_map)

    domain_labels = SUBSET_LABELS if n_domains == 3 else DOMAIN_LABELS[:n_domains]

    config = DEFAULT_CONFIG.copy()

    # -----------------------------------------------------------------------
    # Model A: PSI-only
    # -----------------------------------------------------------------------
    model_a = build_model_a_psi_only(df, domain_idx, n_domains)
    idata_a, t_a = sample_model(model_a, config, "Model A (PSI-only)")
    conv_a = convergence_summary(idata_a, "Model A")
    post_a = extract_posterior_a(idata_a, domain_labels)

    # -----------------------------------------------------------------------
    # Model B: PSI + SPI
    # -----------------------------------------------------------------------
    if "spi" in df.columns and not df["spi"].isna().all():
        model_b = build_model_b_psi_spi(df, domain_idx, n_domains)
        idata_b, t_b = sample_model(model_b, config, "Model B (PSI+SPI)")
        conv_b = convergence_summary(idata_b, "Model B")
        post_b = extract_posterior_b(idata_b, domain_labels)
    else:
        print("\n[SKIP] Model B: SPI data not available")
        idata_b = None
        t_b = 0
        conv_b = {}
        post_b = {}

    # -----------------------------------------------------------------------
    # Model C: UPSI_v2 binary
    # -----------------------------------------------------------------------
    if "upsi_v2" in df.columns and "sudden" in df.columns:
        model_c = build_model_c_upsi_binary(df, domain_idx, n_domains)
        idata_c, t_c = sample_model(model_c, config, "Model C (UPSI_v2)")
        conv_c = convergence_summary(idata_c, "Model C")
        post_c = extract_posterior_c(idata_c, domain_labels)
    else:
        print("\n[SKIP] Model C: UPSI_v2 / sudden data not available")
        idata_c = None
        t_c = 0
        conv_c = {}
        post_c = {}

    # -----------------------------------------------------------------------
    # Model comparison
    # -----------------------------------------------------------------------
    if idata_b is not None and idata_c is not None:
        comp = compare_models(idata_a, idata_b, idata_c)
    else:
        comp = None

    # -----------------------------------------------------------------------
    # Figures
    # -----------------------------------------------------------------------
    print("\n--- Generating Figures ---")
    plot_figure_s1(idata_a, idata_b or idata_a, idata_c or idata_a, figures_dir)
    plot_figure_s2(post_a, domain_labels, figures_dir)
    if comp is not None:
        plot_figure_s3(comp, figures_dir)
    if post_b:
        plot_figure_s4(post_b, figures_dir)

    # -----------------------------------------------------------------------
    # Save results JSON
    # -----------------------------------------------------------------------
    results = {
        "config": config,
        "data_summary": {
            "total_observations": len(df),
            "spi_available": int(("spi" in df.columns) and not df["spi"].isna().all()),
            "domains": sorted(df["domain"].unique().tolist()),
        },
        "model_a": {
            "convergence": conv_a,
            **post_a,
            "model": "A_psi_only",
            "elapsed_seconds": t_a,
        },
        "model_b": {
            "convergence": conv_b,
            **post_b,
            "model": "B_psi_spi_joint",
            "elapsed_seconds": t_b,
        } if post_b else None,
        "model_c": {
            "convergence": conv_c,
            **post_c,
            "model": "C_upsi_v2_binary",
            "elapsed_seconds": t_c,
        } if post_c else None,
        "total_elapsed_seconds": t_a + t_b + t_c,
        "timestamp": pd.Timestamp.now().isoformat(),
    }

    out_json = output_dir / "bayesian_results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n→ Results saved to {out_json}")

    # -----------------------------------------------------------------------
    # Summary report
    # -----------------------------------------------------------------------
    report = f"""
{'='*70}
TCM-UPSI v17B Bayesian Reproduction Complete
{'='*70}

Configuration:
  {config['n_chains']} chains × {config['n_draws']} draws
  target_accept={config['target_accept']}, max_treedepth={config['max_treedepth']}

Model A (PSI-only):
  Convergence: r_hat={conv_a['max_rhat']:.4f}, ESS_bulk={conv_a['min_ess_bulk']:.0f},
               divergences={conv_a['divergences']}
  P(β₀ < 0) = {post_a['p_beta_negative']:.4f}

Model B (PSI+SPI):
  Convergence: r_hat={conv_b.get('max_rhat', 'N/A')}, divergences={conv_b.get('divergences', 'N/A')}
  P(β₁₀ < 0) = {post_b.get('p_beta1_negative', 'N/A')}
  P(β₂₀ > 0) = {post_b.get('p_beta2_positive', 'N/A')}

Model C (UPSI_v2):
  Convergence: r_hat={conv_c.get('max_rhat', 'N/A')}, divergences={conv_c.get('divergences', 'N/A')}

Output:
  JSON:  {out_json}
  Figures: {figures_dir}

{'='*70}
"""
    print(report)

    report_path = output_dir / "REPRODUCTION_REPORT.txt"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"→ Report saved to {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
