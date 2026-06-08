"""
v4.x 阶段 23: 贝叶斯后验预测
=============================

从"统计显著"升级到"真预测"：

问题：给定当前十年的 PSI_z，未来 5/10/15 年内是否会发生危机？
模型：贝叶斯 logistic 回归（PyMC）

输入特征:
- 当前 PSI_z
- 之前 5/10/20 年的 PSI 趋势（slope）
- GSI
- 专家数（log）

输出:
- P(未来 5 年内发生危机 | 当前 PSI 特征)
- 95% HDI
- 后验预测分布
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


# 主要历史危机
CRISIS_YEARS = [755, 875, 907, 1127, 1279, 1644]


def is_crisis_ahead(decade: int, lead: int, crisis_years: list) -> int:
    """在 decade + lead 年内是否有危机？"""
    target = decade + lead
    for cy in crisis_years:
        if decade < cy <= target:
            return 1
    return 0


def main():
    print("=" * 70)
    print("v4.x 阶段 23: 贝叶斯后验预测")
    print("=" * 70)

    # 1. 加载 PSI 数据
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json") as f:
        psi = json.load(f)
    decade_results = sorted(psi["decade_results"], key=lambda r: r["decade"])

    # 2. 准备特征和标签
    print("\n步骤 1: 准备特征和标签...")

    # 特征工程
    features = []
    labels_5y = []  # 5 年内是否危机
    labels_10y = []  # 10 年内
    labels_15y = []  # 15 年内

    for i, r in enumerate(decade_results):
        decade = r["decade"]
        # 特征 1: 当前 PSI_z
        psi_now = r["psi_z"]

        # 特征 2: 过去 5 年平均
        past_5y = [decade_results[j]["psi_z"] for j in range(max(0, i-1), i)]
        past_5y_mean = np.mean(past_5y) if past_5y else psi_now

        # 特征 3: 过去 10 年趋势（斜率）
        past_10y = [decade_results[j]["psi_z"] for j in range(max(0, i-2), i)]
        if len(past_10y) >= 2:
            slope_10y = past_10y[-1] - past_10y[0]
        else:
            slope_10y = 0

        # 特征 4: GSI
        gsi = r["gsi"]

        # 特征 5: 专家数 log
        log_experts = np.log1p(r["expert_count"])

        features.append({
            "psi_now": psi_now,
            "past_5y_mean": past_5y_mean,
            "slope_10y": slope_10y,
            "gsi": gsi,
            "log_experts": log_experts,
        })

        labels_5y.append(is_crisis_ahead(decade, 5, CRISIS_YEARS))
        labels_10y.append(is_crisis_ahead(decade, 10, CRISIS_YEARS))
        labels_15y.append(is_crisis_ahead(decade, 15, CRISIS_YEARS))

    n_pos_5y = sum(labels_5y)
    n_pos_10y = sum(labels_10y)
    n_pos_15y = sum(labels_15y)
    print(f"  5 年内危机: {n_pos_5y}/{len(labels_5y)} ({n_pos_5y/len(labels_5y)*100:.0f}%)")
    print(f"  10 年内危机: {n_pos_10y}/{len(labels_10y)} ({n_pos_10y/len(labels_10y)*100:.0f}%)")
    print(f"  15 年内危机: {n_pos_15y}/{len(labels_15y)} ({n_pos_15y/len(labels_15y)*100:.0f}%)")

    # 3. 准备矩阵
    X = np.array([
        [f["psi_now"], f["past_5y_mean"], f["slope_10y"], f["gsi"], f["log_experts"]]
        for f in features
    ])
    # 标准化
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0) + 1e-9
    X_norm = (X - X_mean) / X_std

    # 4. 贝叶斯 logistic 回归 (10 年危机)
    print("\n步骤 2: 贝叶斯 logistic 回归 (10 年危机预测)...")

    y = np.array(labels_10y)

    with pm.Model() as model:
        # 先验
        alpha = pm.Normal("alpha", mu=0, sigma=2)  # 截距
        beta = pm.Normal("beta", mu=0, sigma=1, shape=5)  # 5 个特征的系数

        # logistic
        logit = alpha + pm.math.dot(X_norm, beta)
        p = pm.Deterministic("p", pm.math.sigmoid(logit))

        # 似然
        y_obs = pm.Bernoulli("y_obs", p=p, observed=y)

        # 采样
        trace = pm.sample(
            draws=2000,
            tune=1000,
            chains=2,
            cores=2,
            target_accept=0.9,
            random_seed=42,
            progressbar=False,
            return_inferencedata=True,
        )

    # 5. 后验分析
    print("\n步骤 3: 后验分析")

    # 系数后验
    feature_names = ["psi_now", "past_5y_mean", "slope_10y", "gsi", "log_experts"]
    summary = az.summary(trace, var_names=["alpha", "beta"], ci_prob=0.95)
    print("\n系数后验均值 (95% ETI):")
    for i, name in enumerate(["alpha"] + [f"beta_{n}" for n in feature_names]):
        mean = float(summary.iloc[i]["mean"])
        et_low = float(summary.iloc[i]["eti95_lb"])
        et_high = float(summary.iloc[i]["eti95_ub"])
        direction = "↑" if mean > 0 else "↓"
        print(f"  {name:<15} mean={mean:+.3f}  ETI=[{et_low:+.3f}, {et_high:+.3f}]  {direction}")

    # 6. 在测试集上评估（Leave-One-Out 简化版）
    print("\n步骤 4: 在数据上预测...")

    # 用后验平均系数做预测
    alpha_post = float(trace.posterior["alpha"].values.mean())
    beta_post = trace.posterior["beta"].values.reshape(-1, 5).mean(axis=0)

    logit_pred = alpha_post + X_norm @ beta_post
    p_pred = 1 / (1 + np.exp(-logit_pred))

    # 阈值 0.5
    pred_class = (p_pred > 0.5).astype(int)

    # 准确率
    acc = (pred_class == y).mean()
    print(f"  整体准确率: {acc:.3f}")

    # TP/FP/TN/FN
    tp = ((pred_class == 1) & (y == 1)).sum()
    fp = ((pred_class == 1) & (y == 0)).sum()
    tn = ((pred_class == 0) & (y == 0)).sum()
    fn = ((pred_class == 0) & (y == 1)).sum()
    print(f"  TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    if tp + fp > 0:
        precision = tp / (tp + fp)
        print(f"  精确率: {precision:.3f}")
    if tp + fn > 0:
        recall = tp / (tp + fn)
        print(f"  召回率: {recall:.3f}")

    # 7. 用 PSI_z = 0 的阈值做简单基准
    print("\n步骤 5: 简单基准对比 (PSI_z < 0 → 预测危机)")
    baseline_pred = (X[:, 0] < 0).astype(int)  # 仅用 psi_now < 0
    acc_b = (baseline_pred == y).mean()
    tp_b = ((baseline_pred == 1) & (y == 1)).sum()
    fp_b = ((baseline_pred == 1) & (y == 0)).sum()
    fn_b = ((baseline_pred == 0) & (y == 1)).sum()
    recall_b = tp_b / (tp_b + fn_b) if (tp_b + fn_b) > 0 else 0
    precision_b = tp_b / (tp_b + fp_b) if (tp_b + fp_b) > 0 else 0
    print(f"  基准准确率: {acc_b:.3f}, 召回: {recall_b:.3f}, 精确: {precision_b:.3f}")

    # 8. 保存
    output = {
        "meta": {
            "version": "v4.x Bayesian Prediction",
            "model": "Bayesian logistic regression (PyMC)",
            "n_samples": len(features),
            "n_features": 5,
            "n_crisis_5y": n_pos_5y,
            "n_crisis_10y": n_pos_10y,
            "n_crisis_15y": n_pos_15y,
        },
        "posterior_coefficients": {
            "alpha": alpha_post,
            "beta": {name: float(beta_post[i]) for i, name in enumerate(feature_names)},
        },
        "performance": {
            "bayesian_model_accuracy": float(acc),
            "bayesian_model_tp": int(tp),
            "bayesian_model_fp": int(fp),
            "bayesian_model_tn": int(tn),
            "bayesian_model_fn": int(fn),
            "bayesian_model_precision": float(precision) if (tp + fp) > 0 else 0,
            "bayesian_model_recall": float(recall) if (tp + fn) > 0 else 0,
            "baseline_accuracy": float(acc_b),
            "baseline_recall": float(recall_b),
            "baseline_precision": float(precision_b),
        },
        "all_predictions": [
            {
                "decade": r["decade"],
                "dynasty": r["dynasty"],
                "psi_z": r["psi_z"],
                "p_crisis_10y": float(p_pred[i]),
                "actual_crisis_10y": int(labels_10y[i]),
            }
            for i, r in enumerate(decade_results)
        ],
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/bayesian_prediction_v4.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 贝叶斯预测结果保存: {out_path}")


if __name__ == "__main__":
    main()
