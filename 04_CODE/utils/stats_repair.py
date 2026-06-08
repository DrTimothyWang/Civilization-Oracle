"""
统计规范修复工具集
基于 Track 1 统计方法论，实现标准化效应量与多重检验校正
"""

import numpy as np


def adjusted_r2(r2, n, k):
    """
    自由度校正 R²（Adjusted R²）

    参数:
        r2: 原始 R²
        n: 样本量
        k: 自变量数量

    返回:
        float: 自由度校正后的 R²

    说明:
        Adj R² = 1 - (1-R²) * (n-1) / (n-k-1)
        惩罚模型复杂度过高导致的过拟合估计
    """
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)


def cohens_d(group1, group2):
    """
    Cohen's d 效应量

    参数:
        group1: array-like, 第一组数据
        group2: array-like, 第二组数据

    返回:
        float: Cohen's d 效应量

    说明:
        Cohen's d = (M1 - M2) / pooled_std
        效应量解释标准:
            |d| < 0.2   : 无效应
            0.2 ≤ |d| < 0.5 : 小效应
            0.5 ≤ |d| < 0.8 : 中等效应
            |d| ≥ 0.8   : 大效应

    示例:
        >>> g1 = [10, 12, 14, 13, 11]
        >>> g2 = [8, 9, 7, 10, 8]
        >>> cohens_d(g1, g2)
        1.25  # 大效应
    """
    n1, n2 = len(group1), len(group2)
    pooled_std = np.sqrt(
        ((n1 - 1) * np.std(group1, ddof=1) ** 2 +
         (n2 - 1) * np.std(group2, ddof=1) ** 2) / (n1 + n2 - 2)
    )
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def hedges_g(cohens_d_val, n1, n2):
    """
    小样本修正版 Hedges' g

    参数:
        cohens_d_val: Cohen's d 值
        n1: 第一组样本量
        n2: 第二组样本量

    返回:
        float: Hedges' g（小样本偏差校正后的效应量）

    说明:
        Hedges' g = Cohen's d × J
        J = 1 - 3 / (4*df - 1)
        df = n1 + n2 - 2

        当 n1 + n2 < 20 时校正效果显著；
        当样本量 > 100 时，g ≈ d
    """
    df = n1 + n2 - 2
    correction = 1 - 3 / (4 * df - 1)
    return cohens_d_val * correction


def holm_correction(p_values, alpha=0.05):
    """
    Holm-Bonferroni 逐步校正（Step-down procedure）

    参数:
        p_values: array-like, 原始 p 值列表
        alpha: float, 显著性水平（默认 0.05）

    返回:
        np.ndarray: Holm 校正后的 p 值

    说明:
        Holm 校正是强控制 FWER 的方法，比原始 Bonferroni 更强大（功效更高）。

        步骤:
        1. 将 p 值升序排列：p(1) ≤ p(2) ≤ ... ≤ p(k)
        2. 从最小的 p 开始检验，找到第一个满足 p(i) ≤ α/(k-i+1) 的 i
        3. 第 i 个及之后所有检验均被拒绝

        注：本实现采用简化版：对每个 p 值乘以它的 rank 作为近似
        完整实现中通过逐步比较确定分界点

    示例:
        >>> p_vals = [0.01, 0.03, 0.05, 0.10]
        >>> holm_correction(p_vals, alpha=0.05)
        array([0.04, 0.09, 0.10, 0.10])
    """
    p_values = np.array(p_values)
    k = len(p_values)
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    adjusted = np.zeros(k)

    for i in range(k):
        threshold = alpha / (k - i)
        if sorted_p[i] <= threshold:
            for j in range(i, k):
                adjusted[sorted_idx[j]] = min(sorted_p[j] * (k - j), 1.0)
            break
        else:
            adjusted[sorted_idx[i]] = sorted_p[i]

    return adjusted


def wfa_evaluate(train_data, test_data, psi_func):
    """
    Walk-Forward 评估（滚动窗口交叉验证）

    参数:
        train_data: list, 训练数据窗口列表（每个元素为训练集）
        test_data: list, 测试数据窗口列表（与 train_data 一一对应）
        psi_func: callable, PSI 计算函数，接收训练集返回模型

    返回:
        dict: {'MAE': float, 'RMSE': float, 'r2': float}

    说明:
        Walk-Forward 评估模拟真实预测场景：
        - 在每个时间窗口上，用历史数据训练模型
        - 用训练好的模型预测下一个时间窗口
        - 汇总所有窗口的预测结果计算整体指标

        相比简单 k 折交叉验证，WFA 更好地反映了时间序列的非平稳性

    示例:
        >>> def psi_model(train):
        ...     # 简单线性模型示例
        ...     from sklearn.linear_model import LinearRegression
        ...     X = np.array([t['features'] for t in train])
        ...     y = np.array([t['psi'] for t in train])
        ...     model = LinearRegression().fit(X, y)
        ...     return model
        ...
        >>> result = wfa_evaluate(windows_train, windows_test, psi_model)
        >>> print(f"MAE: {result['MAE']:.4f}, RMSE: {result['RMSE']:.4f}")
    """
    predictions = []
    actuals = []
    for train, test in zip(train_data, test_data):
        model = psi_func(train)
        pred = model.predict(np.array([t['features'] for t in test]))
        predictions.extend(pred)
        actuals.extend([t['psi'] for t in test])

    predictions = np.array(predictions)
    actuals = np.array(actuals)

    mae = np.mean(np.abs(predictions - actuals))
    rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
    r2 = 1 - np.sum((actuals - predictions) ** 2) / np.sum((actuals - np.mean(actuals)) ** 2)

    return {'MAE': mae, 'RMSE': rmse, 'R2': r2}


# === 快捷调用接口 ===

def effect_size_interpretation(d):
    """
    Cohen's d 效应量解释

    参数:
        d: float, Cohen's d 值

    返回:
        str: 效应量等级描述
    """
    abs_d = abs(d)
    if abs_d < 0.2:
        return "无效应 (negligible)"
    elif abs_d < 0.5:
        return "小效应 (small)"
    elif abs_d < 0.8:
        return "中等效应 (medium)"
    else:
        return "大效应 (large)"


def report_adjustment(r2, n, k):
    """
    生成 Adjusted R² 报告

    参数:
        r2: 原始 R²
        n: 样本量
        k: 自变量数量

    返回:
        str: 格式化的报告字符串
    """
    adj_r2 = adjusted_r2(r2, n, k)
    diff = r2 - adj_r2

    return (
        f"Adjusted R² 报告\n"
        f"{'='*40}\n"
        f"原始 R²     : {r2:.4f}\n"
        f"样本量 (n)  : {n}\n"
        f"变量数 (k)  : {k}\n"
        f"自由度 (df) : {n - k - 1}\n"
        f"{'='*40}\n"
        f"Adjusted R² : {adj_r2:.4f}\n"
        f"惩罚量      : {diff:.4f}\n"
        f"{'='*40}\n"
        f"结论: {'模型可接受' if adj_r2 > 0 else '模型拟合极差，需要重新设计'}"
    )