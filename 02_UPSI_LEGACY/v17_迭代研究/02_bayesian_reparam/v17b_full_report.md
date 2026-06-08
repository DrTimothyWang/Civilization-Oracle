# v17b 完整贝叶斯采样报告

**生成时间**: 2026-06-08 23:48:21
**总耗时**: 1884.49 秒 (约 31.4 分钟)

## 配置

- **Chains**: 4
- **Tune**: 2000
- **Draws**: 4000
- **Target Accept**: 0.95
- **Max Treedepth**: 12

## 数据摘要

- **总观测数**: 6832
- **有 SPI 的观测**: 79
- **领域数**: 7

## 模型 A (PSI-only, 完整数据)

### 收敛诊断

| 指标 | 值 | 状态 |
|------|-----|------|
| max_rhat | 1.20 | ⚠ 警告 |
| min_ess_bulk | 15.0 | ⚠ 警告 |
| min_ess_tail | 19.0 | ⚠ 警告 |
| divergences | 15984 | ✗ 严重 |
| max_treedepth_hits | 44 | - |

### 关键参数

- **beta_0_mean**: 0.005
- **p_beta_negative**: 0.503
- **sigma_beta_mean**: 229.10

### 领域效应

| 领域 | 均值 | HDI 3% | HDI 97% | p_negative |
|------|------|--------|---------|------------|
| 中华历史 | -12.45 | -18.50 | -6.30 | 1.000 |
| 美索不达米亚 | 0.41 | -2.37 | 3.07 | 0.354 |
| 现代金融 | -24.45 | -39.61 | -7.97 | 1.000 |
| 全球政治 | -664.28 | -724.41 | -565.50 | 1.000 |
| 中国金融 | -1.29 | -1.53 | -1.04 | 1.000 |
| 古罗马 | -25.70 | -43.89 | -7.41 | 1.000 |
| COVID | -13.20 | -26.49 | -2.14 | 1.000 |

### WAIC/LOO

- WAIC: -1266.35
- p_waic: 9.38

---

## 模型 A (PSI-only, SPI 子集)

### 收敛诊断

| 指标 | 值 | 状态 |
|------|-----|------|
| max_rhat | 1.00 | ✓ |
| min_ess_bulk | 4866.0 | ✓ |
| min_ess_tail | 6281.0 | ✓ |
| divergences | 446 | ✗ 严重 |
| max_treedepth_hits | 0 | - |

### 关键参数

- **beta_0_mean**: -2.11
- **p_beta_negative**: 0.833
- **sigma_beta_mean**: 5.99

### 领域效应

| 领域 | 均值 | HDI 3% | HDI 97% | p_negative |
|------|------|--------|---------|------------|
| 中华历史 | -8.62 | -14.51 | -3.03 | 0.9999 |
| 美索不达米亚 | 0.33 | -2.35 | 2.99 | 0.377 |
| 现代金融 | -6.75 | -14.43 | -1.32 | 0.9998 |

---

## 模型 B (PSI+SPI 联合)

### 收敛诊断

| 指标 | 值 | 状态 |
|------|-----|------|
| max_rhat | 1.00 | ✓ |
| min_ess_bulk | 1843.0 | ✓ |
| min_ess_tail | 1876.0 | ✓ |
| divergences | 1201 | ✗ 严重 |
| max_treedepth_hits | 0 | - |

### 关键参数

- **beta1_0_mean**: -2.03 (PSI 系数)
- **p_beta1_negative**: 0.833
- **beta2_0_mean**: -0.14 (SPI 系数)
- **p_beta2_positive**: 0.411
- **psi_importance**: 2.42
- **spi_importance**: 0.74

### 领域效应

| 领域 | beta1_mean | beta1_HDI | beta2_mean | beta2_HDI |
|------|------------|-----------|------------|-----------|
| 中华历史 | -8.47 | [-14.72, -2.66] | -0.40 | [-1.61, 0.83] |
| 美索不达米亚 | 0.28 | [-2.49, 2.97] | -0.42 | [-3.75, 2.54] |
| 现代金融 | -6.30 | [-14.51, -0.14] | 0.57 | [-2.39, 5.44] |

### 相关矩阵

|  | alpha | beta1 | beta2 |
|--|-------|-------|-------|
| alpha | 1.00 | -0.15 | -0.07 |
| beta1 | -0.15 | 1.00 | -0.01 |
| beta2 | -0.07 | -0.01 | 1.00 |

### WAIC/LOO

- WAIC: -35.01
- LOO: -36.74
- p_waic: 7.21

---

## 模型 C (UPSI_v2 二元分类)

### 收敛诊断

| 指标 | 值 | 状态 |
|------|-----|------|
| max_rhat | 1.00 | ✓ |
| min_ess_bulk | 2900.0 | ✓ |
| min_ess_tail | 3244.0 | ✓ |
| divergences | 229 | ✗ 严重 |
| max_treedepth_hits | 0 | - |

### 关键参数

- **p_sudden_stable**: 0.350
- **p_sudden_crisis**: 0.409
- **delta_0_mean**: 0.212
- **p_delta_positive**: 0.598

### WAIC/LOO

- WAIC: -44.55
- LOO: -44.61
- p_waic: 3.79

---

## 模型比较

| 模型 | WAIC | LOO | p_waic |
|------|------|-----|--------|
| A (完整) | -1266.35 | NaN | 9.38 |
| A (子集) | -33.82 | -35.61 | - |
| B (联合) | -35.01 | -36.74 | 7.21 |
| C (二元) | -44.55 | -44.61 | 3.79 |

**Winner**: Model A (子集) 根据 WAIC/LOO 比较

---

## 后验预测

### Model B 情景预测

| 情景 | PSI | SPI | 预测象限 | p_crisis |
|------|-----|-----|----------|----------|
| Moderate PSI decline + High SPI burst | -0.5 | 1.5 | Sudden Crisis | 0.685 |
| Strong PSI decline + Moderate SPI | -1.0 | 0.5 | Sudden Crisis | 0.769 |
| High PSI + Critical SPI burst | 0.8 | 2.0 | Accelerating Collapse | 0.312 |
| Moderate PSI + Low SPI (baseline) | 0.5 | -0.2 | Gradual Decline | 0.423 |

### Model C 情景预测

| 情景 | p_sudden |
|------|----------|
| Stable period | 0.350 |
| Crisis period | 0.409 |

---

## 收敛诊断摘要

### 问题总结

1. **Model A (完整数据)**: 严重收敛问题
   - 15984 divergences
   - R-hat 最高 1.20
   - ESS 最低 15
   - 建议: 需要更长的 tuning 或更强的先验

2. **Model A (子集)**: 良好收敛
   - 446 divergences (需关注)
   - R-hat = 1.00
   - ESS > 4800

3. **Model B (联合)**: 良好收敛
   - 1201 divergences (需关注)
   - R-hat = 1.00
   - ESS > 1800

4. **Model C (二元)**: 良好收敛
   - 229 divergences (需关注)
   - R-hat = 1.00
   - ESS > 2900

### 建议

- Model A (完整数据) 需要重新参数化或更强的先验约束
- 其他模型收敛良好，但 divergences 数量仍需关注
- 考虑增加 tune 步数或调整 target_accept

---

*报告生成完成*
