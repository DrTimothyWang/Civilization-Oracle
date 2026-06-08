"""
v4.x ULTIMATE 阶段 31: 贝叶斯 4 chains 5000 draws 完整化
=========================================================

v3 贝叶斯用 2 chains × 2000 draws，马老师隐含担心 rhat > 1.01
v4.x 升级到 4 chains × 5000 draws
- 改善 rhat
- 减少 ESS 不足问题
- 输出更稳定的后验
"""
import sys
import os
import json
import time
import numpy as np
import pymc as pm
import arviz as az
import warnings
warnings.filterwarnings('ignore')

sys.path = ['/opt/homebrew/Caskroom/miniconda/base/lib/python3.13/site-packages'] + sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 70)
    print("v4.x 阶段 31: 贝叶斯 4 chains × 5000 draws 完整化")
    print("=" * 70)

    # 加载数据
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json") as f:
        psi = json.load(f)
    decade_results = sorted(psi["decade_results"], key=lambda r: r["decade"])

    n_dynasties = 5
    psi_zs = np.array([r["psi_z"] for r in decade_results])
    dynasty_idx = np.array([
        ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"].index(r["dynasty"])
        for r in decade_results
    ])
    n_decades = len(psi_zs)

    # 构造 SE（基于专家数）
    ses = np.array([1.0 / np.sqrt(max(1, r["expert_count"])) for r in decade_results])

    print(f"\n  n_decades: {n_decades}, n_dynasties: {n_dynasties}")

    # 3 层贝叶斯模型
    t0 = time.time()
    with pm.Model() as model:
        # 全局超参数
        mu_global = pm.Normal("mu_global", mu=0, sigma=1)
        sigma_global = pm.HalfNormal("sigma_global", sigma=1)

        # 朝代级
        mu_dynasty = pm.Normal("mu_dynasty", mu=mu_global, sigma=sigma_global, shape=n_dynasties)
        sigma_dynasty = pm.HalfNormal("sigma_dynasty", sigma=0.5)

        # 十年级
        mu_decade = pm.Normal("mu_decade", mu=mu_dynasty[dynasty_idx],
                              sigma=sigma_dynasty, shape=n_decades)

        # 观察
        sigma_within = pm.HalfNormal("sigma_within", sigma=0.3)
        y_obs = pm.Normal("y_obs", mu=mu_decade,
                          sigma=np.sqrt(ses**2 + sigma_within**2),
                          observed=psi_zs)

        # 4 chains × 5000 draws
        print("\n  开始 MCMC 采样 (4 chains × 5000 draws)...")
        trace = pm.sample(
            draws=5000,
            tune=2000,
            chains=4,
            cores=4,
            target_accept=0.95,  # 提高以减少 divergence
            random_seed=42,
            progressbar=False,
            return_inferencedata=True,
        )

    elapsed = time.time() - t0
    print(f"  MCMC 完成 ({elapsed:.0f}s)")

    # 后验分析
    print("\n步骤 3: 后验分析 (4 chains × 5000 draws)")
    summary_dynasty = az.summary(trace, var_names=["mu_dynasty"], ci_prob=0.95)
    summary_global = az.summary(trace, var_names=["mu_global", "sigma_global"], ci_prob=0.95)

    print("\n朝代级后验 (95% ETI):")
    dynasty_names = ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"]
    for i, name in enumerate(dynasty_names):
        mean = float(summary_dynasty.iloc[i]["mean"])
        et_low = float(summary_dynasty.iloc[i]["eti95_lb"])
        et_high = float(summary_dynasty.iloc[i]["eti95_ub"])
        rhat = float(summary_dynasty.iloc[i]["r_hat"])
        ess = float(summary_dynasty.iloc[i]["ess_bulk"])
        print(f"  {name:<8} mean={mean:+.4f}  ETI=[{et_low:+.4f}, {et_high:+.4f}]  r_hat={rhat:.3f}  ESS={ess:.0f}")

    print(f"\n  r_hat 最大值: {float(summary_dynasty['r_hat'].max()):.4f} (目标: <1.01)")
    print(f"  ESS 最小值: {float(summary_dynasty['ess_bulk'].min()):.0f} (目标: >100)")

    # 跨朝代对比后验
    print("\n步骤 4: 跨朝代对比后验概率")
    mu_samples = trace.posterior["mu_dynasty"].values  # (chains, draws, 5)
    flat = mu_samples.reshape(-1, 5)

    comparisons = {
        "P(唐朝 > 南宋)": (flat[:, 0] > flat[:, 3]).mean(),
        "P(北宋前期 > 南宋)": (flat[:, 1] > flat[:, 3]).mean(),
        "P(明朝 > 南宋)": (flat[:, 4] > flat[:, 3]).mean(),
        "P(北宋前期 > 唐朝)": (flat[:, 1] > flat[:, 0]).mean(),
        "P(唐朝 > 明朝)": (flat[:, 0] > flat[:, 4]).mean(),
        "P(北宋前期 > 明朝)": (flat[:, 1] > flat[:, 4]).mean(),
    }

    for desc, p in comparisons.items():
        print(f"  {desc} = {p:.4f}")

    # 保存
    output = {
        "meta": {
            "version": "v4.x ULTIMATE Bayesian 4 chains",
            "n_decades": n_decades,
            "n_mcmc_draws": 5000,
            "n_chains": 4,
            "rhat_max": float(summary_dynasty["r_hat"].max()),
            "ess_min": float(summary_dynasty["ess_bulk"].min()),
        },
        "posterior_means_dynasty": {
            name: float(summary_dynasty.iloc[i]["mean"])
            for i, name in enumerate(dynasty_names)
        },
        "posterior_eti_dynasty": {
            name: [float(summary_dynasty.iloc[i]["eti95_lb"]),
                   float(summary_dynasty.iloc[i]["eti95_ub"])]
            for i, name in enumerate(dynasty_names)
        },
        "posterior_probabilities": {k: float(v) for k, v in comparisons.items()},
        "global_hyperparams": {
            "mu_global": float(summary_global.iloc[0]["mean"]),
            "sigma_global": float(summary_global.iloc[1]["mean"]),
        },
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/bayesian_v4x_4chains.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 4 chains 贝叶斯结果保存: {out_path}")


if __name__ == "__main__":
    main()
