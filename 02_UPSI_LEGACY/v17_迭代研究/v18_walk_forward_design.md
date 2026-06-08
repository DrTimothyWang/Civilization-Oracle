# v18 Major Revision 准备: Walk-Forward OOS 验证设计

> **版本**: v18.0 (规划稿)  
> **日期**: 2026-06-05  
> **目标**: 设计审稿人最可能要求的 walk-forward out-of-sample 验证框架  
> **状态**: 设计完成，待实施

---

## 1. 背景: 为什么 Walk-Forward OOS 是审稿人的"第一枪"

从 v17A 审稿回应分析，审稿人最可能的致命批评是:

> **Q4**: "所有 AUC 都是 in-sample。Walk-forward OOS 验证在哪里？"

当前状态:
- 基线 AUC: 0.48-0.59 (in-sample)
- 特征工程 AUC: 0.62-0.73 (in-sample)
- 唯一 OOS: 2020-2023 训练 → 2024-2025 测试 (中国金融 PSI 基线，非 AUC)

**Walk-forward OOS 是区分"真实预测能力"和"过拟合"的金标准。**

---

## 2. Walk-Forward OOS 设计框架

### 2.1 核心原则

| 原则 | 说明 |
|------|------|
| **滚动窗口** | 训练期固定长度，测试期固定长度，逐步向前滚动 |
| **无信息泄漏** | 训练期严格在测试期之前，不使用未来数据 |
| **固定超参** | 权重 (0.4/0.3/0.3) 和阈值 (-0.5) 全局固定，不在窗口内调优 |
| **多域验证** | 金融 (日频) + 政治 (年频) + 历史 (十年频) 分别设计 |

### 2.2 金融域 Walk-Forward (日频，最严格)

```
窗口设计:
  训练期: 252 交易日 (1年)
  测试期: 63 交易日 (1季度)
  步长: 63 交易日 (每季度滚动一次)

时间范围: 2018-01-01 至 2026-06-01
总窗口数: ~32 个 (8年 × 4季度)

危机标签: NBER 衰退期 + 已知市场崩盘 (2018-10, 2020-03, 2022-02, 2024-02)

评估指标:
  - AUC (主要)
  - Precision @ Recall=0.75
  - F1-score
  - 校准曲线 (Calibration curve)
  - Brier score

特征工程限制:
  - 只允许使用训练期内计算的滚动统计量
  - 不允许使用全局 min/max (信息泄漏)
  - 标准化参数在训练期计算，应用于测试期
```

### 2.3 政治域 Walk-Forward (年频)

```
窗口设计:
  训练期: 50 年
  测试期: 10 年
  步长: 10 年

时间范围: -218 至 2022
总窗口数: ~24 个

危机标签: 标准历史参考 (Turchin, Goldstone)

特殊挑战:
  - 年频数据稀疏，窗口数少
  - 危机标签主观性强
  - 解决方案: 使用 Conformal Prediction 提供有限样本保证
```

### 2.4 历史域 Walk-Forward (十年频)

```
窗口设计:
  训练期: 200 年 (20 decades)
  测试期: 50 年 (5 decades)
  步长: 50 年

时间范围: 610-1644 (CBDB 数据)
总窗口数: ~20 个

危机标签: 王朝更替 + 重大叛乱

特殊挑战:
  - 样本量极小 (n=7 王朝)
  - 解决方案: 使用贝叶斯层次模型"借 strength"
  - 交叉验证: Leave-one-dynasty-out
```

---

## 3. 实施计划

### 3.1 代码架构

```
v18_walk_forward/
├── v18a_finance_oos.py      # 金融域 walk-forward
├── v18b_politics_oos.py     # 政治域 walk-forward
├── v18c_history_oos.py      # 历史域 walk-forward
├── v18d_cross_domain_oos.py # 跨域联合 OOS
├── v18e_calibration.py      # 校准曲线与 Brier score
├── v18f_conformal.py        # Conformal Prediction  wrapper
└── v18_results.json         # 汇总结果
```

### 3.2 关键算法

**金融域滚动特征工程 (无泄漏)**:
```python
def rolling_features_no_leak(train_psi, test_psi):
    """
    仅使用训练期数据计算标准化参数和滚动统计量
    """
    # 训练期统计量
    train_mean = np.mean(train_psi)
    train_std = np.std(train_psi)
    train_min = np.min(train_psi)
    
    # 标准化 (使用训练期参数)
    test_psi_norm = (test_psi - train_mean) / train_std
    
    # 滚动特征 (仅在训练期计算参数)
    # σ: 训练期滚动标准差的中位数
    train_rolling_std = pd.Series(train_psi).rolling(20).std()
    sigma_ref = np.median(train_rolling_std.dropna())
    
    # dPSI/dt: 训练期一阶差分标准差
    dpsi_ref = np.std(np.diff(train_psi))
    
    # 测试期特征
    features = {
        'psi_norm': test_psi_norm,
        'sigma': sigma_ref,  # 固定值，非滚动
        'dpsi_dt': np.diff(test_psi, prepend=test_psi[0]) / dpsi_ref,
        'dist_to_min': (test_psi - train_min) / train_std,
    }
    return features
```

**Conformal Prediction (有限样本保证)**:
```python
from nonconformist.cp import IcpClassifier
from nonconformist.nc import NcFactory

# 使用随机森林作为底层分类器
nc = NcFactory.create_nc(RandomForestClassifier())
icp = IcpClassifier(nc)

# 训练期拟合
icp.calibrate(X_cal, y_cal)

# 测试期预测 (带置信度)
prediction, significance = icp.predict(X_test, significance=0.1)
# significance=0.1 表示 90% 置信度
```

### 3.3 预期结果与风险

| 场景 | 预期 OOS AUC | 风险 |
|------|-------------|------|
| 乐观 | 0.60-0.68 | 金融域有 enough 数据 |
| 基准 | 0.55-0.62 | 政治/历史域数据稀疏 |
| 悲观 | 0.50-0.55 | 过拟合严重，接近随机 |

**诚实报告策略**:
- 如果 OOS AUC < 0.55: 诚实报告，强调"monitoring tool"定位
- 如果 OOS AUC 0.55-0.62: 报告为"moderate discrimination, sufficient for monitoring"
- 如果 OOS AUC > 0.62: 谨慎庆祝，检查是否有信息泄漏

---

## 4. 与 v17 的衔接

### 4.1 v17B 完成后 → v18A 启动

v17B 贝叶斯结果将提供:
- 域间异质性估计 (σ_δ)
- 先验敏感性分析
- 这些将用于 v18 的贝叶斯 walk-forward (域间 borrow strength)

### 4.2 v18 产出 → v19 投稿修订

v18 完成后:
- 更新 Nature Letter ¶2.4: 添加 OOS AUC 结果
- 更新 SI Section 10: 添加 Walk-Forward 详细方法
- 更新 Cover Letter: "We have now added walk-forward OOS validation..."

---

## 5. 时间线

| 阶段 | 任务 | 预计时间 | 依赖 |
|------|------|----------|------|
| v18A | 金融域 walk-forward | 4-6 小时 | yfinance 数据 |
| v18B | 政治域 walk-forward | 2-3 小时 | Wikidata 数据 |
| v18C | 历史域 walk-forward | 2-3 小时 | CBDB 数据 |
| v18D | 跨域联合 OOS | 2 小时 | v18A-C 结果 |
| v18E | 校准与 Conformal | 2 小时 | v18A-C 结果 |
| v18F | 报告生成 | 1 小时 | 以上全部 |
| **合计** | | **13-17 小时** | |

---

## 6. 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 训练期长度 | 金融 252d, 政治 50yr, 历史 200yr | 平衡样本量与 stationarity |
| 步长 | 金融 63d, 政治 10yr, 历史 50yr | 确保测试期独立性 |
| 特征工程 | 无泄漏滚动统计 | 防止信息泄漏 |
| 阈值 | 固定 -0.5 | 不在窗口内调优 |
| 评估 | AUC + Brier + Calibration | 全面评估 discrimination 和 calibration |
| 有限样本 | Conformal Prediction | 提供 coverage guarantee |

---

*设计完成。待 v17B 采样完成后启动实施。*
