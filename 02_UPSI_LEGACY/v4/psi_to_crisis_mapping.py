"""
v4.x 阶段 23b: PSI → P(未来危机) 函数
========================================

重大发现: 简单基准 PSI_z<0 召回 85.7% > 贝叶斯 14.3%

本步骤: 真正提取出 PSI_z 到 P(未来 10 年危机) 的精确映射
- 用贝叶斯 logistic 拟合
- 后验预测
- 报告 P(危机) 的精确区间

这是论文里"真预测"的核心
"""
import sys
import os
import json
import numpy as np
import pymc as pm
import arviz as az
import warnings
warnings.filterwarnings('ignore')

sys.path = ['/opt/homebrew/Caskroom/miniconda/base/lib/python3.13/site-packages'] + sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


CRISIS_YEARS = [755, 875, 907, 1127, 1279, 1644]


def is_crisis_ahead(decade: int, lead: int) -> int:
    target = decade + lead
    for cy in CRISIS_YEARS:
        if decade < cy <= target:
            return 1
    return 0


def main():
    print("=" * 70)
    print("v4.x 阶段 23b: PSI_z → P(未来 10 年危机) 映射")
    print("=" * 70)

    # 加载数据
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json") as f:
        psi = json.load(f)
    decade_results = sorted(psi["decade_results"], key=lambda r: r["decade"])

    # 准备 PSI_z + 标签
    psi_zs = np.array([r["psi_z"] for r in decade_results])
    y_10y = np.array([is_crisis_ahead(r["decade"], 10) for r in decade_results])
    y_5y = np.array([is_crisis_ahead(r["decade"], 5) for r in decade_results])
    y_15y = np.array([is_crisis_ahead(r["decade"], 15) for r in decade_results])

    print(f"\n标签分布:")
    print(f"  5 年内: {y_5y.sum()}/96 ({y_5y.mean()*100:.0f}%)")
    print(f"  10 年内: {y_10y.sum()}/96 ({y_10y.mean()*100:.0f}%)")
    print(f"  15 年内: {y_15y.sum()}/96 ({y_15y.mean()*100:.0f}%)")

    # 1. 贝叶斯 logistic 拟合 (10 年)
    print("\n步骤 1: 贝叶斯 logistic (10 年危机预测)")

    # 用 Weakly informative 先验
    with pm.Model() as model_10y:
        # 截距先验: 偏向 0 (因为 base rate 7%)
        alpha = pm.Normal("alpha", mu=-2.5, sigma=1.5)

        # 系数先验: PSI 越低 → 危机概率越高
        # beta 应该为负
        beta_psi = pm.Normal("beta_psi", mu=-1.0, sigma=1.0)

        # logistic
        logit = alpha + beta_psi * psi_zs
        p = pm.Deterministic("p", pm.math.sigmoid(logit))

        y_obs = pm.Bernoulli("y_obs", p=p, observed=y_10y)

        trace_10y = pm.sample(draws=2000, tune=1000, chains=2, cores=2,
                              target_accept=0.9, random_seed=42,
                              progressbar=False, return_inferencedata=True)

    # 2. 用后验样本做预测
    print("\n步骤 2: 用后验样本生成 PSI_z → P(危机) 映射")

    alpha_post = trace_10y.posterior["alpha"].values.reshape(-1)
    beta_post = trace_10y.posterior["beta_psi"].values.reshape(-1)

    print(f"  后验 alpha: mean={alpha_post.mean():.3f}, 95% ETI=[{np.percentile(alpha_post, 2.5):.3f}, {np.percentile(alpha_post, 97.5):.3f}]")
    print(f"  后验 beta_psi: mean={beta_post.mean():.3f}, 95% ETI=[{np.percentile(beta_post, 2.5):.3f}, {np.percentile(beta_post, 97.5):.3f}]")

    # 3. 计算不同 PSI_z 下的 P(危机) (95% ETI)
    test_psi = np.linspace(-3, 2, 21)
    p_summary = []

    for psi_val in test_psi:
        logit_samples = alpha_post + beta_post * psi_val
        p_samples = 1 / (1 + np.exp(-logit_samples))
        p_mean = p_samples.mean()
        p_low = np.percentile(p_samples, 2.5)
        p_high = np.percentile(p_samples, 97.5)
        p_summary.append({
            "psi_z": float(psi_val),
            "p_crisis_mean": float(p_mean),
            "p_crisis_low": float(p_low),
            "p_crisis_high": float(p_high),
        })

    print("\nPSI_z → P(未来 10 年危机) 映射:")
    print(f"{'PSI_z':<8} {'P 均值':<8} {'95% ETI':<25}")
    print("-" * 45)
    for r in p_summary:
        print(f"{r['psi_z']:>+.1f}    {r['p_crisis_mean']:.3f}   [{r['p_crisis_low']:.3f}, {r['p_crisis_high']:.3f}]")

    # 4. 关键 PSI_z 下的 P(危机)
    print("\n关键 PSI_z 下的 P(未来 10 年危机):")
    for psi_val in [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0]:
        logit_samples = alpha_post + beta_post * psi_val
        p_samples = 1 / (1 + np.exp(-logit_samples))
        p_mean = p_samples.mean()
        p_low = np.percentile(p_samples, 2.5)
        p_high = np.percentile(p_samples, 97.5)
        print(f"  PSI_z = {psi_val:+.1f}: P = {p_mean:.3f} (95% ETI [{p_low:.3f}, {p_high:.3f}])")

    # 5. 真正的 PSI 谷值 vs 实际危机关系
    print("\n每个主要危机的 PSI 谷值 → 后验 P(危机):")
    crisis_decades = {
        750: "安史之乱 (755)",
        860: "黄巢起义 (875)",
        1100: "靖康之变 (1127)",
        1270: "崖山海战 (1279)",
        1640: "明亡 (1644)",
    }

    for dec, name in crisis_decades.items():
        # 找 PSI
        for r in decade_results:
            if r["decade"] == dec:
                psi_val = r["psi_z"]
                logit_samples = alpha_post + beta_post * psi_val
                p_samples = 1 / (1 + np.exp(-logit_samples))
                p_mean = p_samples.mean()
                print(f"  {name}: PSI_z={psi_val:+.3f}, 后验 P(危机) = {p_mean:.3f}")
                break

    # 6. 评估基准
    print("\n评估: 简单阈值 vs 贝叶斯后验预测")

    # 简单阈值
    for threshold in [-2.0, -1.5, -1.0, -0.5, 0.0]:
        pred = (psi_zs < threshold).astype(int)
        tp = ((pred == 1) & (y_10y == 1)).sum()
        fp = ((pred == 1) & (y_10y == 0)).sum()
        fn = ((pred == 0) & (y_10y == 1)).sum()
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        print(f"  PSI_z < {threshold:+.1f}: TP={tp} FP={fp} FN={fn}  Recall={recall:.2f}  Precision={precision:.2f}  F1={f1:.2f}")

    # 贝叶斯后验预测 (用 p_mean 阈值 0.5)
    logit_post = alpha_post + beta_post * psi_zs
    p_pred = 1 / (1 + np.exp(-logit_post))
    # 对每个 sample, 做 hard prediction
    bayes_pred_samples = (np.array([1/(1+np.exp(-(alpha_post + beta_post * psi_val))) for psi_val in psi_zs]) > 0.5).astype(int)
    # 用平均值
    p_pred_mean = p_pred.mean(axis=1) if p_pred.ndim > 1 else p_pred
    bayes_pred = (p_pred_mean > 0.5).astype(int)
    tp = ((bayes_pred == 1) & (y_10y == 1)).sum()
    fp = ((bayes_pred == 1) & (y_10y == 0)).sum()
    fn = ((bayes_pred == 0) & (y_10y == 1)).sum()
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    print(f"  贝叶斯预测 (p>0.5): TP={tp} FP={fp} FN={fn}  Recall={recall:.2f}  Precision={precision:.2f}")

    # 7. 保存
    output = {
        "meta": {
            "version": "v4.x Bayesian Crisis Mapping",
            "model": "Bayesian logistic regression (PyMC)",
            "n_samples": 96,
            "n_crises_10y": int(y_10y.sum()),
            "posterior_samples": 4000,
        },
        "posterior_coefficients": {
            "alpha": {
                "mean": float(alpha_post.mean()),
                "ci_low": float(np.percentile(alpha_post, 2.5)),
                "ci_high": float(np.percentile(alpha_post, 97.5)),
            },
            "beta_psi": {
                "mean": float(beta_post.mean()),
                "ci_low": float(np.percentile(beta_post, 2.5)),
                "ci_high": float(np.percentile(beta_post, 97.5)),
            },
        },
        "psi_to_crisis_mapping": p_summary,
        "crisis_specific_predictions": [
            {
                "event": name,
                "decade": dec,
                "psi_z": float(next(r["psi_z"] for r in decade_results if r["decade"] == dec)),
                "posterior_p_crisis_10y": float((1/(1+np.exp(-(alpha_post + beta_post * next(r["psi_z"] for r in decade_results if r["decade"] == dec))))).mean()),
            }
            for dec, name in crisis_decades.items()
        ],
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_to_crisis_mapping.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] PSI→P(危机) 映射保存: {out_path}")


if __name__ == "__main__":
    main()
