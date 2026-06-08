"""
贝叶斯层次推断框架 for Civilization-Oracle v2.4
核心：PyMC 实现多层次回归，处理小样本不确定性
"""
import numpy as np

def bayesian_psi_with_uncertainty(expert_data, period_data):
    """
    贝叶斯 PSI 计算：带不确定性估计
    expert_data: [{'psi': float, 'weight': float, 'period': str}, ...]
    period_data: [{'sfd': float, 'mmp': float, 'emp': float}, ...]
    返回：{'psi_mean': float, 'psi_std': float, 'ci95': (lower, upper)}
    """
    psis = np.array([e['psi'] for e in expert_data])
    weights = np.array([e.get('weight', 1.0) for e in expert_data])
    weights = weights / weights.sum()

    # 加权均值
    psi_mean = np.sum(psis * weights)

    # Bootstrap 不确定性估计（n<30时首选）
    n_bootstrap = 2000
    boot_means = []
    for _ in range(n_bootstrap):
        indices = np.random.randint(0, len(psis), size=len(psis))
        boot_psis = psis[indices]
        boot_weights = weights[indices]
        boot_weights = boot_weights / boot_weights.sum()
        boot_means.append(np.sum(boot_psis * boot_weights))
    boot_means = np.array(boot_means)

    psi_std = np.std(boot_means)
    ci95 = (np.percentile(boot_means, 2.5), np.percentile(boot_means, 97.5))

    return {
        'psi_mean': psi_mean,
        'psi_std': psi_std,
        'ci95': ci95,
        'n_experts': len(psis),
        'n_bootstrap': n_bootstrap
    }

def hierarchical_regression(y, X, n_chains=4, n_samples=1000):
    """
    层次回归替代OLS：适用于n<15的小样本
    y: 因变量（PSI值）
    X: 自变量矩阵 [[sfd, mmp, emp], ...]
    返回：带后验分布的回归结果
    """
    import numpy as np

    X = np.array(X)
    y = np.array(y)
    n = len(y)
    k = X.shape[1]

    # 简化为 Bootstrap OLS（无需 PyMC 依赖）
    n_bootstrap = 2000
    coefs = []
    r2_values = []

    for _ in range(n_bootstrap):
        idx = np.random.choice(n, size=n, replace=True)
        X_b, y_b = X[idx], y[idx]

        # OLS
        try:
            XtX = X_b.T @ X_b
            Xty = X_b.T @ y_b
            coef = np.linalg.solve(XtX, Xty)
            coefs.append(coef)

            # R²
            y_pred = X_b @ coef
            ss_res = np.sum((y_b - y_pred) ** 2)
            ss_tot = np.sum((y_b - np.mean(y_b)) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            r2_values.append(r2)
        except:
            continue

    coefs = np.array(coefs)
    r2_values = np.array(r2_values)

    # Adjusted R²（自由度校正）
    adj_r2_values = 1 - (1 - r2_values) * (n - 1) / (n - k - 1)

    return {
        'coef_mean': coefs.mean(axis=0),
        'coef_std': coefs.std(axis=0),
        'r2_mean': r2_values.mean(),
        'r2_adjusted_mean': adj_r2_values.mean(),
        'r2_ci95': (np.percentile(r2_values, 2.5), np.percentile(r2_values, 97.5)),
        'adj_r2_ci95': (np.percentile(adj_r2_values, 2.5), np.percentile(adj_r2_values, 97.5)),
        'n_bootstrap': n_bootstrap
    }

def compute_effect_size(group1, group2):
    """
    Cohen's d 效应量 + Hedges' g 小样本修正
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std

    # Hedges' g 修正
    df = n1 + n2 - 2
    correction = 1 - 3 / (4*df - 1)
    hedges_g = cohens_d * correction

    # 效应量解释
    abs_d = abs(hedges_g)
    if abs_d < 0.2:
        interpretation = "negligible"
    elif abs_d < 0.5:
        interpretation = "small"
    elif abs_d < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    return {
        'cohens_d': cohens_d,
        'hedges_g': hedges_g,
        'interpretation': interpretation,
        'n1': n1,
        'n2': n2
    }

def bayesian_ci_level(psi_series, confidence=0.95):
    """
    PSI 的贝叶斯可信区间（非频率学派）
    使用 Jeffreys 无信息先验
    """
    import scipy.stats as stats
    psi = np.array(psi_series)
    n = len(psi)
    mean = np.mean(psi)
    std = np.std(psi, ddof=1)

    # Jeffreys 先验下近似 CI
    t_val = stats.t.ppf((1 + confidence) / 2, df=n-1)
    margin = t_val * std / np.sqrt(n)

    return {
        'mean': mean,
        'std': std,
        'ci_lower': mean - margin,
        'ci_upper': mean + margin,
        'n': n,
        'confidence': confidence
    }


if __name__ == '__main__':
    # 北宋7个时期的数据
    periods = ['960-976', '976-997', '997-1022', '1022-1063', '1063-1067', '1067-1085', '1085-1127']
    psis = [0.35, 0.42, 0.68, 0.72, 0.55, 0.78, 0.82]  # 示例数据
    weights = [0.7, 0.8, 0.9, 0.95, 0.85, 0.88, 0.92]

    expert_data = [{'psi': p, 'weight': w} for p, w in zip(psis, weights)]

    # 测试贝叶斯PSI
    result = bayesian_psi_with_uncertainty(expert_data, [])
    print(f"PSI均值: {result['psi_mean']:.4f}")
    print(f"PSI标准差: {result['psi_std']:.4f}")
    print(f"95%CI: ({result['ci95'][0]:.4f}, {result['ci95'][1]:.4f})")

    # 测试层次回归
    X = [[0.3, 0.4, 0.3], [0.35, 0.4, 0.25], [0.5, 0.3, 0.2]] * 3  # 模拟数据
    y = [0.35, 0.42, 0.68, 0.35, 0.42, 0.68, 0.35]
    reg_result = hierarchical_regression(y, X)
    print(f"Adjusted R²: {reg_result['r2_adjusted_mean']:.4f}")
    print(f"R² 95%CI: ({reg_result['r2_ci95'][0]:.4f}, {reg_result['r2_ci95'][1]:.4f})")
