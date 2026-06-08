"""
v4.0 贝叶斯层次模型 (PyMC) - 修复版
====================================

用 decade-level aggregate data（96 窗均值）做贝叶斯推断
- 比 individual-level 快 100x
- 后验更稳定
- 仍然能给出 P(朝代 A > 朝代 B) 的概率
"""
import sys
import os
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

sys.path = ['/opt/homebrew/Caskroom/miniconda/base/lib/python3.13/site-packages'] + sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymc as pm
import arviz as az


def build_decade_level_model(decade_results, n_dynasties=5, n_sample=2000):
    """
    3 层贝叶斯模型: global → dynasty → decade

    观察数据: 96 个十年的 PSI_z
    """
    # 准备数据
    decade_means = []  # psi_z
    decade_ses = []    # standard error
    dynasty_idx = []
    decade_names = []

    for r in decade_results:
        decade_means.append(r["psi_z"])
        # 用样本量估计 SE
        n = max(1, r.get("expert_count", 1))
        decade_ses.append(1.0 / np.sqrt(n))  # 简化 SE
        dynasty_idx.append(["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"].index(r["dynasty"]))
        decade_names.append(f"{r['dynasty']}_{r['decade']}")

    decade_means = np.array(decade_means)
    decade_ses = np.array(decade_ses)
    dynasty_idx = np.array(dynasty_idx)
    n_decades = len(decade_means)

    print(f"\n构建贝叶斯模型...")
    print(f"  十年级: {n_decades}")
    print(f"  朝代数: {n_dynasties}")

    with pm.Model() as model:
        # 全局超参数
        mu_global = pm.Normal("mu_global", mu=0, sigma=1)
        sigma_global = pm.HalfNormal("sigma_global", sigma=1)

        # 朝代级均值
        mu_dynasty = pm.Normal("mu_dynasty", mu=mu_global, sigma=sigma_global, shape=n_dynasties)
        sigma_dynasty = pm.HalfNormal("sigma_dynasty", sigma=0.5)

        # 十年级均值（hierarchical on dynasty）
        mu_decade = pm.Normal("mu_decade", mu=mu_dynasty[dynasty_idx],
                              sigma=sigma_dynasty, shape=n_decades)

        # 十年级内变异
        sigma_within = pm.HalfNormal("sigma_within", sigma=0.3)

        # 观察
        y_obs = pm.Normal("y_obs", mu=mu_decade, sigma=np.sqrt(decade_ses**2 + sigma_within**2),
                          observed=decade_means)

        # 采样
        print("  开始 MCMC 采样 (2 chains, 2000 draws)...")
        trace = pm.sample(
            draws=n_sample,
            tune=1000,
            chains=2,
            cores=2,
            target_accept=0.9,
            random_seed=42,
            progressbar=False,
            return_inferencedata=True,
        )

    return model, trace, n_decades, n_dynasties


def main():
    print("=" * 70)
    print("v4.0 贝叶斯层次模型 (PyMC) - 修复版")
    print("=" * 70)

    # 1. 加载 PSI 数据
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json") as f:
        psi = json.load(f)
    decade_results = psi["decade_results"]

    print(f"\n加载 {len(decade_results)} 个十年级数据")

    # 2. 构建 + 采样
    try:
        model, trace, n_decades, n_dynasties = build_decade_level_model(decade_results, n_sample=2000)
    except Exception as e:
        print(f"[!] MCMC 失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. 后验分析
    print("\n步骤 3: 后验分析...")

    # 朝代级后验
    dynasty_names = ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"]
    mu_dynasty_samples = trace.posterior["mu_dynasty"].values  # (chains, draws, 5)

    summary_dynasty = az.summary(trace, var_names=["mu_dynasty"], ci_prob=0.95)
    print("\n朝代级后验均值 (95% ETI):")
    for i, name in enumerate(dynasty_names):
        mean = float(summary_dynasty.iloc[i]["mean"])
        hdi_low = float(summary_dynasty.iloc[i]["eti95_lb"])
        hdi_high = float(summary_dynasty.iloc[i]["eti95_ub"])
        print(f"  {name:<8} mean={mean:+.4f}  95%ETI=[{hdi_low:+.4f}, {hdi_high:+.4f}]")

    # 4. 跨朝代对比的后验概率
    print("\n步骤 4: 跨朝代对比后验概率...")

    chains, draws, _ = mu_dynasty_samples.shape
    flat_samples = mu_dynasty_samples.reshape(-1, n_dynasties)  # (chains*draws, 5)

    comparisons = {
        "P(唐朝 > 南宋)": (flat_samples[:, 0] > flat_samples[:, 3]).mean(),
        "P(北宋前期 > 南宋)": (flat_samples[:, 1] > flat_samples[:, 3]).mean(),
        "P(明朝 > 南宋)": (flat_samples[:, 4] > flat_samples[:, 3]).mean(),
        "P(北宋前期 > 唐朝)": (flat_samples[:, 1] > flat_samples[:, 0]).mean(),
        "P(唐朝 > 明朝)": (flat_samples[:, 0] > flat_samples[:, 4]).mean(),
        "P(北宋前期 > 明朝)": (flat_samples[:, 1] > flat_samples[:, 4]).mean(),
    }

    for desc, p in comparisons.items():
        print(f"  {desc} = {p:.3f}")

    # 5. 全局超参数
    summary_global = az.summary(trace, var_names=["mu_global", "sigma_global"], ci_prob=0.95)
    print("\n全局超参数:")
    print(summary_global)

    # 6. 简单对比：v4.0 频率派 vs 贝叶斯后验
    freq_dynasty_means = {dy: psi["by_dynasty"][dy]["psi_z_mean"] for dy in dynasty_names}
    print("\n频率派 vs 贝叶斯后验对比:")
    for i, name in enumerate(dynasty_names):
        freq = freq_dynasty_means[name]
        bayes = float(summary_dynasty.iloc[i]["mean"])
        diff = abs(freq - bayes)
        print(f"  {name:<8} 频率派={freq:+.4f}  贝叶斯={bayes:+.4f}  diff={diff:.4f}")

    # 7. 保存
    output = {
        "meta": {
            "version": "v4.0 Bayesian (修复版)",
            "model": "3-level hierarchical: global → dynasty → decade",
            "n_decades": n_decades,
            "n_mcmc_draws": 2000,
            "n_chains": 2,
        },
        "posterior_means_dynasty": {
            name: float(summary_dynasty.iloc[i]["mean"])
            for i, name in enumerate(dynasty_names)
        },
        "posterior_hdi_dynasty": {
            name: [float(summary_dynasty.iloc[i]["eti95_lb"]),
                   float(summary_dynasty.iloc[i]["eti95_ub"])]
            for i, name in enumerate(dynasty_names)
        },
        "posterior_probabilities": {k: float(v) for k, v in comparisons.items()},
        "global_hyperparams": {
            "mu_global": float(summary_global.iloc[0]["mean"]),
            "sigma_global": float(summary_global.iloc[1]["mean"]),
        },
        "frequentist_vs_bayesian": {
            name: {
                "frequentist": freq_dynasty_means[name],
                "bayesian": float(summary_dynasty.iloc[i]["mean"]),
            }
            for i, name in enumerate(dynasty_names)
        },
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/bayesian_v4_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 贝叶斯结果保存: {out_path}")


if __name__ == "__main__":
    main()
