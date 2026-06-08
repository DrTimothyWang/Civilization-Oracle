# Civilization-Oracle v4.0 设计方案
**作者：Mavis 独立研究 | 日期：2026-06-02 | 状态：执行中**

> 本文档是 v4.0 的设计基线。v3.0 的 12 项马老师审稿问题 + 3 项我新发现的问题（公式不统一 / API 数据真实性 / 统计对象错配）将全部在此版本修复。

---

## 1. v3.0 三大致命伤的诊断

| # | 致命伤 | 严重性 | 来源 |
|---|--------|--------|------|
| 1 | **公式不统一**：摘要/正文/附录/代码/讲稿/MCP 出现 4-6 种 PSI 公式 | P0 致命 | 文档/代码 diff |
| 2 | **96 窗"API 数据"是 mock**：avg_sentiment 尾数全部是 0.05 整数倍（0.6333, 0.9167...），无 LLM 随机扰动 | P0 致命 | 数值分布分析 |
| 3 | **统计对象错配**：Bootstrap CI 在 n=5 聚合点算，Cohen's d 在 n=4 朝代均值算 | P0 致命 | 方法论 |

## 2. v4.0 核心原则

1. **公式唯一性**：一处定义，全文一致；代码、论文、附录、HTML 全部用同一份公式
2. **数据真实性**：96 个十年 × 3 次真实 LLM 调用（取中位数），prompt 故意模糊化
3. **统计严谨性**：所有推断基于 30,518 条 individual-level 记录，不在聚合点上算
4. **可证伪性优先**：H1-H4 假设预注册，Type I/II 错误率报告
5. **跨文明可扩展**：从中华文明扩展到美索不达米亚（CDLI）

## 3. 唯一公式（v4.0 锁定版）

### 3.1 三组分定义

对每个十年窗口 $d$（如 1020s）：

**MMP (Mean Metaphor Polarity)** = 该十年所有历史专家文本的情感极性均值
- 范围: [-1, +1]（实数）
- 通过 MiniMax API 真实调用，每个十年调用 3 次取中位数

**SFD (Scholar Frequency Density)** = log(1 + 该十年专家数)
- 范围: 实数（对数化后消除量纲差异）
- 反映"该十年的专家群体密度"

**EED (Expert Engagement Density)** = 该十年有文本的专家比例
- 范围: [0, 1]
- 反映"专家群体的有效参与度"

### 3.2 标准化

所有组分先 z-score 标准化：
$$X_z^{(d)} = \frac{X^{(d)} - \mu_X}{\sigma_X}$$
其中 $\mu_X, \sigma_X$ 是该组分在所有 96 个十年上的均值和标准差。

### 3.3 核心 PSI 公式（v4.0 唯一版）

$$\boxed{\text{PSI}_z^{(d)} = 0.40 \cdot \text{MMP}_z^{(d)} + 0.30 \cdot \text{SFD}_z^{(d)} + 0.30 \cdot \text{EED}_z^{(d)}}$$

### 3.4 地理修正（独立因子）

GSI 是横切因子，不在 SFD 内重复计权：
$$\text{GSI}^{(d)} = 1 + 0.2 \cdot (R_{\text{north}}^{(d)} - 0.5)$$
其中 $R_{\text{north}}$ 是该十年北方（纬度 > 35°N）专家占比。

### 3.5 IPW 校正

CBDB 系统性过度代表官员。IPW 加权：
$$\text{PSI}_{\text{IPW}}^{(d)} = \frac{\sum_i w_i \cdot \text{PSI}_i^{(d)}}{\sum_i w_i}$$
其中 $w_i = 1 / P(\text{专家}_i \text{ 被 CBDB 记录})$。

### 3.6 阈值与映射

PSI 是 z-score 量纲。映射到 [0, 1] 区间（用于跨朝代比较）：
$$\text{PSI}_{\text{final}}^{(d)} = \frac{1}{1 + e^{-\text{PSI}_z^{(d)}}}$$

**危机阈值**：$\text{PSI}_z < -1$ （即 1 个标准差以下）
**盛世阈值**：$\text{PSI}_z > +1$ （即 1 个标准差以上）

## 4. 与 v3.0 公式的差异

| 维度 | v3.0（多版本混乱） | v4.0（唯一） |
|------|---------------------|---------------|
| 公式出处 | 至少 4-6 种不同描述 | 一处定义（本文 3.3） |
| 权重 | 0.25/0.25/0.5（SFD 内部） | 0.40/0.30/0.30（z-score 后） |
| 标准化 | 无（不同量纲混合） | z-score 标准化（先标准化再加权） |
| GSI 处理 | 重复计权（在 SFD 内 + 又乘一遍） | 独立修正因子 |
| density_norm | 重复使用（既在 SFD 内又作为乘数） | 不存在（用 log(1+SFD)） |
| 输出量纲 | [0, 1]（但公式不严谨） | z-score + sigmoid 映射（严谨） |

## 5. v4.0 交付物清单

```
v4/
├── DESIGN.md                          # 本文件
├── formula.py                         # 唯一公式实现（论文级注释）
├── data_pipeline.py                   # CBDB → 30,518 专家 × 文本 → individual-level
├── api_caller.py                      # MiniMax API 真实调用（模糊 prompt + 3 次中位数）
├── compute_psi_v4.py                  # 按 v4 公式重算 96 个十年
├── statistics/
│   ├── bootstrap_v4.py                # individual-level Bootstrap
│   ├── cohens_d_v4.py                 # individual-level Cohen's d + Hedges' g
│   ├── walk_forward_v4.py             # Walk-Forward 验证
│   └── sensitivity_v4.py              # 阈值敏感性 + Holm 校正
├── paper/
│   ├── paper_v4_full.md               # 完整论文 v4.0
│   ├── paper_v4_appendix.md           # 附录
│   └── figures/                       # 实际生成的 Figure 1/2/3
├── cross_civilization/
│   └── cdli_v4.py                     # 美索不达米亚 PSI（CDLI 100 条）
├── reproduce.py                       # 一键复现脚本
└── FINAL_REPORT.md                    # 最终汇报
```

## 6. 时间表

| 阶段 | 内容 | 目标时长 |
|------|------|----------|
| 1 | 诊断 + 设计 | 0-30 min |
| 2 | 公式实现 + 数据管线 | 30-90 min |
| 3 | 真实 API 重跑 96 窗 | 90-180 min |
| 4 | individual-level 统计 | 180-240 min |
| 5 | 论文 v4.0 撰写 | 240-360 min |
| 6 | Figure 生成 + 跨文明 + 整理 | 360-420 min |
| 7 | 敏感性分析 + 可证伪性 | 420-480 min |

## 7. 关键创新点（v4.0 区别于 v3.0）

1. **真正的"individual-level"统计**——不是朝代均值上算
2. **真实 LLM 调用的"模糊 prompt"**——避免 LLM 输出过于规整
3. **z-score + sigmoid 映射**——数学上严格的输出范围
4. **GSI 作为独立修正因子**——避免重复计权
5. **CDLI 跨文明实证**——从中华文明扩展到美索不达米亚

---

*版本 v4.0 | 设计基线 | 2026-06-02*
