## 维度02: 理论框架与PSI公式演进

> **研究员**: 维度02 (理论框架与PSI公式演进)
> **阅读文件**: 18份核心文档 (v2.3-v6.3全周期)
> **报告日期**: 2026-06-04
> **核心任务**: 提取PSI指标的理论基础、公式推导和演进过程

---

### 1. PSI指标定义

#### 1.1 组件数学定义

PSI (Psychological Semantic Index / Pressure Synchronization Index / Unified Pressure Synchronization Index) 是 Civilization-Oracle 项目的核心量化指标，其定义经历了从 v2.3 到 v6.3 的重大演进。

**v3.0 及以前版本 (四组件模型)**

根据 `Civilization-Oracle_v3.0_研究全景报告.md` (§2.1-2.2) 和 `Civilization-Oracle_完整技术文档_v2.3.md` (§2.1)：

```
PSI = (MMP × 0.25 + EMP × 0.25 + SFD × 0.50) × GSI
```

各组件定义：

| 组件 | 全称 | 数学定义 | 范围 | 数据来源 |
|------|------|----------|------|----------|
| **MMP** | Mean Metaphor Polarity (语义情绪极性) | 该十年所有历史专家文本的情感极性均值 | [-1, +1] | MiniMax API / SikuBERT |
| **EMP** | Expert Emotional Polarity (专家情绪极性) | 核心专家群体(史官/官员/学者)的情感极性均值 | [-1, +1] | CBDB 专家子池 |
| **SFD** | Scholar Frequency Density (专家密度标准化值) | 单位时间内专家出现的密度，经标准化处理 | [0, 1] | CBDB 人物计数 |
| **GSI** | Geographical Stress Index (地理压力指数) | 区域压力标准化值: 北方1.4x, 南方0.8x | [0.8, 1.4] | CHGIS 地理编码 |

**v4.x+ 版本 (三组件z-score模型)**

根据 `v4/DESIGN.md` (§3) 和 `v4/formula.py`：

```
PSI_z^(d) = 0.40 × MMP_z^(d) + 0.30 × SFD_z^(d) + 0.30 × EED_z^(d)
```

其中：
- **MMP_z** = 该十年情感极性均值的 z-score 标准化值
- **SFD_z** = log(1 + 该十年专家数) 的 z-score 标准化值
- **EED_z** = 该十年有文本的专家比例 的 z-score 标准化值

z-score 标准化公式 (`v4/formula.py`, §2)：
```
X_z^(d) = (X^(d) - μ_X) / σ_X
```
其中 μ_X, σ_X 是该组分在所有 96 个十年上的均值和标准差。

**v5.0/v6.0+ 版本 (跨域统一模型)**

根据 `v6/UPSI_PAPER.md` (§2) 和 `v6/README.md`：

```
UPSI = 0.4 × Material(z) + 0.3 × Fragmentation(z) + 0.3 × Disengagement(z)
```

| 维度 | 经济学含义 | 物理学含义 | 历史域映射 |
|------|------------|------------|------------|
| Material | 物质压力 (回撤/GDP↓) | 系统的"势能" | MMP (文本情感) |
| Fragmentation | 派系分裂 (波动/极化) | 系统的"动能" | SFD (专家密度波动) |
| Disengagement | 精英脱节 (VIX↑/外流) | 系统的"熵增" | EED (有效参与度) |

#### 1.2 权重分配的理论依据 (SDT信号检测论)

权重分配的核心依据来自 **信号检测论 (Signal Detection Theory, SDT)**。

根据 `Civilization-Oracle_v3.0_研究全景报告.md` (§2.3)：
> "SDT 的核心洞见是：在高噪声环境下，**客观的物理信号**比**主观的报告**更可靠。"

权重逻辑：
- MMP 和 EMP 是文本情感 → **主观报告** → 可能被政治立场、文学惯例扭曲 → 权重各 0.25
- SFD 是专家密度 → **客观计数** → 实际发生的社会活动 → 权重 0.50
- GSI 是地理压力 → **客观环境** → 不以人的意志为转移 → 作为独立修正因子

v4.0 权重调整 (`v4/DESIGN.md`, §3.3)：
> "0.40/0.30/0.30 的权重是通过网格搜索(grid search)在四个域上最大化 F1 后锁定的。"

v4.0 将 SFD 权重从 0.50 降至 0.30，原因是：
- v3.0 的 SFD 权重过高导致对样本量不平衡敏感
- 引入 EED (Expert Engagement Density) 后，需要平衡密度与参与度
- 网格搜索显示 0.40/0.30/0.30 在跨域 F1 上最优

#### 1.3 输出映射

**Sigmoid 映射** (`v4/formula.py`, §3.6)：
```
PSI_final = 1 / (1 + exp(-PSI_z))
```
- PSI_z = 0 时 → 0.5
- PSI_z = +1 时 → 0.731
- PSI_z = -1 时 → 0.269

**GSI 独立修正** (`v4/formula.py`, §3.4)：
```
GSI^(d) = 1 + 0.2 × (R_north^(d) - 0.5)
PSI_z,gsi = PSI_z × GSI_factor
```
其中 R_north 是该十年北方(纬度>35°N)专家占比。v4.0 关键改进：GSI 不再在 SFD 内重复计权，仅作为独立修正因子。

---

### 2. 理论基础

#### 2.1 语义心理学 (马利军教授)

**核心命题** (`Civilization-Oracle_v3.0_研究全景报告.md`, §1.2; `语意演化预测系统_v2.0.md`, §2.2)：
> "文本隐喻反映作者的心理状态与社会语境。"

**扩展假设**：如果一群人（而非一个人）的文本汇聚起来，能否反映一个文明的心理状态？

**CPM-KB (Conceptual Metaphor Knowledge Base)** (`Civilization-Oracle_完整技术文档_v2.3.md`, §2.3)：

| 隐喻模式 | 心理状态 | 极性 | PEN三维 (P,E,N) | 样本数 | IAA |
|----------|----------|------|-----------------|--------|-----|
| 心为火 | 焦虑/愤怒 | -1 | (-0.6, +0.4, +0.7) | 320 | 0.82 |
| 心为水 | 平静/超脱 | +1 | (+0.5, -0.2, -0.4) | 215 | 0.79 |
| 家国为舟 | 希望/焦虑 | 语境依赖 | (+0.1, +0.2, +0.3) | 580 | 0.71 |
| 天地不仁 | 绝望/虚无 | -1 | (-0.7, -0.1, +0.8) | 140 | 0.85 |
| 春风得意 | 乐观/自豪 | +1 | (+0.6, +0.3, -0.2) | 390 | 0.88 |

**PEN三维模型**：
- **P** (Pleasantness)：愉悦度 -1.0 ~ +1.0
- **E** (Excitement)：激活度 -1.0 ~ +1.0
- **N** (Nervousness)：紧张度 -1.0 ~ +1.0

#### 2.2 Cliodynamics (Peter Turchin)

**理论定位** (`Civilization-Oracle_v3.0_研究全景报告.md`, §1.1; `语意演化预测系统_v2.0.md`, §2.4)：

Cliodynamics（历史动力学）代表人物 Peter Turchin 的核心假设：历史并非完全不可预测，存在可辨识的社会动力学规律。

Turchin 的方法依赖宏观指标：
- 人口结构
- 精英供需
- 国家脆弱度

**关键局限** (`Civilization-Oracle_v3.0_研究全景报告.md`, §1.1)：
> "这些指标都是事后诸葛——在危机爆发前几年才能看到明显变化。"

**PSI 的差异化定位**：
- Turchin 的 PSI (Political Stress Index) = MMP × EMP × SFD (`语意演化预测系统_v2.0.md`, §2.4)
- Civilization-Oracle 的 PSI 是**语义增强型**，在 Turchin 定量框架基础上增加古籍语义和隐喻心理的深度层

Turchin 验证结果引用 (`语意演化预测系统_v2.0.md`, §2.4)：
> "清朝PSI峰值领先内部战争约10年（p<0.001），是唯一中国朝代验证（Orlandi-Turchin 2023）。"

#### 2.3 信号检测论 (SDT)

**全称**：Structural Demographic Theory (结构人口理论) / Signal Detection Theory (信号检测论)

**在 PSI 中的应用** (`Civilization-Oracle_v3.0_研究全景报告.md`, §2.3; `语意演化预测系统_v2.0.md`, §2.4)：

1. **权重分配依据**：客观信号（密度+地理）> 主观报告（文本情绪）
2. **阈值设定依据**：决策标准 β = 0.5 来自 SDT 框架
3. **Bootstrap 验证**：五朝 PSI 95% 置信区间不跨越 0.5，朝代差异是结构性的

#### 2.4 复杂系统科学

**物理理论统一** (`v6/UPSI_PAPER.md`, §4; `v6.1/PHYSICS_DOWNGRADE.md`, §1)：

v6.0 声称 PSI 时序呈现**超临界相变特征**：
- Hurst H = 0.958
- 功率谱 β = 1.66
- 声称"比 Ising 经典临界态更强"

v6.1.1 修正后 (`v6.1/PHYSICS_DOWNGRADE.md`, §1.2; `v6.3/NATURE_MAIN.md`, §Methods)：
- **H (DFA on level) = 1.5662**
- **β (Whittle on level) = 4.0000**
- 理论 fBm 预测: β = 2H + 1 = 4.1324
- **偏差仅 3.2%** — 完全符合分数布朗运动 (fBm) 过程

**新解读**：
- 价格水平 = fBm 过程 (H=1.57) → 强长程正相关
- 收益率 ≈ 随机游走 (H=0.45) → 符合有效市场假说 (EMH)
- 这与"同步器非预测器"框架完全一致

---

### 3. 公式演进历史

#### 3.1 版本演进路线图

| 版本 | 时间 | 公式 | 核心变化 | 解决的核心问题 |
|------|------|------|----------|----------------|
| **v1.0** | 2026-05-28 | PSI = MMP × EMP × SFD | 三组件乘积 | 回答"怎么做" |
| **v2.0** | 2026-05-28 | PSI = MMP × EMP × SFD | 同上 | 理论框架 |
| **v2.1** | 2026-05-27 | PSI = MMP×0.4 + EMP×0.3 + SFD×0.3 | 线性加权 | 改善趋势但不足 |
| **v2.3** | 2026-05-27 | **PSI = 0.25×MMP + 0.25×EMP + 0.5×SFD** | SFD权重升至0.5 | ✅ 正确趋势 |
| **v2.4** | 2026-05-29 | 同上 + GSI 修正 | 引入地理压力 | 全历史覆盖 |
| **v3.0** | 2026-05-31 | PSI = (MMP×0.25 + EMP×0.25 + SFD×0.50) × GSI | 统一公式 | TKG融合+四诊合参 |
| **v4.0** | 2026-06-02 | **PSI_z = 0.40×MMP_z + 0.30×SFD_z + 0.30×EED_z** | z-score+唯一公式 | 修复v3.0三大致命伤 |
| **v5.0** | 2026-06-03 | UPSI = 0.4×Material + 0.3×Fragmentation + 0.3×Disengagement | 跨域统一命名 | 6域验证+物理理论 |
| **v6.0** | 2026-06-03 | 同上 | 超临界相变声称 | Nobel++包装 |
| **v6.1.1** | 2026-06-04 | 同上 | H-β修正+fBm | 物理降级声明 |
| **v6.3** | 2026-06-04 | 同上 | PNAS投稿稿 | 4页精炼版 |

#### 3.2 每次变化的原因和验证

**v2.0 → v2.3 的关键校准** (`Civilization-Oracle_完整技术文档_v2.3.md`, §4.1-4.2)：

| 时期 | v2.0 PSI | v2.3 PSI | 变化 |
|------|----------|----------|------|
| 北宋初期 | 0.031 | 0.311 | +903% |
| 北宋中期 | 0.030 | 0.312 | +940% |
| 北宋后期 | 0.045 | 0.362 | +704% |
| 北宋末期 | 0.104 | **0.610** | +486% |

校准方法：
1. 增加 SFD 权重从 0.33 → 0.5
2. 引入历史冲击系数（8个时期，1.0→2.5）
3. 引入区域压力系数（北方1.4x，南方0.8x）
4. 北宋末期 EMP 从 0.35 → 0.60（危机感而非悲观）

**v3.0 → v4.0 的范式转移** (`v4/DESIGN.md`, §1; `v4/V40_VS_V30_COMPARISON.md`)：

v3.0 存在**三大致命伤**：
1. **公式不统一**：摘要/正文/附录/代码/讲稿/MCP 出现 4-6 种 PSI 公式
2. **96窗"API数据"是mock**：avg_sentiment 尾数全部是 0.05 整数倍
3. **统计对象错配**：Bootstrap CI 在 n=5 聚合点算，Cohen's d 在 n=4 朝代均值算

v4.0 修复：
- 锁定**唯一公式**：`PSI_z = 0.40×MMP_z + 0.30×SFD_z + 0.30×EED_z`
- 288 次真实 MiniMax-M3 API 调用（100% 成功）
- 所有统计基于 n=30,518 individual-level 记录

**v4.0 → v5.0 → v6.0 的跨域扩展** (`v5/V5_SUMMARY.md`; `v6/UPSI_PAPER.md`)：

| 版本 | 验证域数 | 总样本 | 跨度 |
|------|----------|--------|------|
| v4.0 | 4 (中华/美索/罗马/中国金融) | ~30万 | 2500年 |
| v5.0 | 6 (+全球金融/全球政治) | ~300万 | 4200年 |
| v6.0 | 7 (+实时新闻) | ~350万 | 5500年 |

#### 3.3 公式统一过程

v4.0 的核心贡献是**公式唯一性** (`v4/DESIGN.md`, §2; `v4/V40_VS_V30_COMPARISON.md`, §2.1)：

| 文档位置 | v3.0 公式 | v4.0 公式 |
|----------|----------|----------|
| 摘要 | `PSI = MMP×0.25 + EMP×0.25 + GSI×0.50` | `PSI_z = 0.40×MMP_z + 0.30×SFD_z + 0.30×EED_z` |
| 3.3节 | `SFD = 0.25×MMP + 0.25×EMP + 0.5×GSI` | 同上 |
| 附录A | `PSI_raw = SFD × density_norm` | 同上 |
| 代码 | `SFD = 0.5×(MMP+1)/2 + 0.5×density_norm` | 同上（重写） |
| 讲稿 | 多种 | 同上 |
| MCP server | `PSI = MMP×0.25 + EMP×0.25 + SFD×0.50`（无GSI） | 同上 |

**反算验证** (`v4/FINAL_REPORT.md`, §2.1)：
> "用前10条数据反算，**代码公式100%命中实际PSI值，论文公式全部对不上**（唐朝620s：论文算0.85 vs 实际0.78）。"

---

### 4. 阈值设定

#### 4.1 0.5阈值的来源

**v3.0 阈值** (`Civilization-Oracle_v3.0_研究全景报告.md`, §2.4)：
> "PSI 的阈值 0.5 来自 SDT 框架的决策标准（β）。我们没有事先设定这个阈值——而是从数据出发，验证了五朝的 PSI 95% 置信区间，发现它们均不跨越 0.5，且朝代之间的差异是结构性的。"

**v4.0 阈值重构** (`v4/formula.py`, §4; `v4/V40_VS_V30_COMPARISON.md`, §2.11)：

由于 v4.0 采用 z-score 量纲，阈值重新定义为：
- **危机阈值**：PSI_z < -1.0（即1个标准差以下）
- **盛世阈值**：PSI_z > +1.0（即1个标准差以上）
- **警戒阈值**：PSI_z < 0（中位数以下）

v4.0 关键发现：
> "PSI_z < 0 阈值下 6/6 危机 100% 召回"

#### 4.2 Bootstrap验证

**v3.0 Bootstrap** (`Civilization-Oracle_v3.0_研究全景报告.md`, §2.4; `语意演化预测系统_v2.0.md`, §4.4)：
- 五朝 PSI 的 95% 置信区间**不重叠**
- 唐朝 PSI=0.6122 vs 明朝 PSI=0.6250 — 结构性地相似
- Cohen's d = 7.35（但后被证明是生态学谬误）

**v4.0 Bootstrap** (`v4/FINAL_REPORT.md`, §3.3; `v4/STATISTICS_SUMMARY.md`, §1)：
- 基于 n=30,518 individual-level 记录
- 2000 次重抽样
- 5 朝 CI 宽度 0.02-0.03（合理）
- 5 朝 CI **完全不重叠**

| 朝代 | n | PSI_z 均值 | 95% CI |
|------|---|------------|--------|
| 唐朝 | 8,901 | -0.19 (IPW后-0.07) | [-0.085, -0.061] |
| 北宋前期 | 1,597 | +0.39 (IPW后+0.57) | [+0.570, +0.594] |
| 北宋后期 | 2,952 | -0.13 (IPW后-0.14) | [-0.144, -0.110] |
| 南宋 | 2,367 | -0.52 (IPW后-0.57) | [-0.529, -0.502] |
| 明朝 | 16,840 | -0.05 (IPW后-0.06) | [-0.054, -0.037] |

#### 4.3 敏感性分析

**v4.0 阈值敏感性** (`v4/FINAL_REPORT.md`, §4.5; `v4/V40_VS_V30_COMPARISON.md`, §2.11)：

| PSI_z 阈值 | 召回率 | 解读 |
|------------|--------|------|
| < -1.5 | 17% | 过于严格 |
| < -1.0 (v4.0 default) | 17% | 红色警戒 |
| < -0.5 | 33% | 中高风险 |
| < 0.0 | **100%** | 历史预警（推荐） |
| < 0.5 | 100% | 过于宽松 |

**关键发现**：
> "PSI_z < 0 阈值下，6 个主要历史危机 100% 召回。但这不意味着 100% 准确率（false positive 率未知）。"

**v6.1 ROC曲线** (`v6.1/NATURE_SI_V61.md`, §S10)：

| 域 | AUC | 最佳阈值 | F1 |
|------|-----|----------|-----|
| 中国金融 (SSE) | 0.594 | 0.00 | 36.6% |
| 全球金融 (SP500) | 0.573 | -1.50 | 17.9% |
| 全球政治 (Wikidata) | 0.479 | +1.00 | 7.2% |

---

### 5. 跨域适配

#### 5.1 历史域 vs 金融域的公式差异

**历史域** (`v4/DESIGN.md`, §3.1; `v4/formula.py`)：
- 时间粒度：十年窗口 (decade)
- MMP：MiniMax API 情感分析，每个十年调用3次取中位数
- SFD：log(1 + 该十年专家数)
- EED：该十年有文本的专家比例
- 标准化窗口：全部 96 个十年

**金融域** (`v6/UPSI_PAPER.md`, §2; `v5/V5_SUMMARY.md`)：
- 时间粒度：日度 (daily)
- Material：60日股权回撤
- Fragmentation：实现波动率
- Disengagement：成交量换手率
- 标准化窗口：滚动 252 日

**政治域** (`v5/V5_SUMMARY.md`, §2.2; `v6.1/NATURE_SI_V61.md`, §S4.6)：
- 时间粒度：10年窗口
- MMP：当前事件数 vs 前期均值
- SFD：死亡数波动
- EED：强度变化率

**美索不达米亚域** (`v6.1/NATURE_SI_V61.md`, §S4.2; `v6.3/NATURE_MAIN.md`, §Methods)：
- 时间粒度：100年窗口
- 代理变量：记录数(record count)作为物质产出代理
- Fragmentation：1 - 体裁多样性(genre diversity)
- Disengagement：1 - 记录密度(record density)

#### 5.2 标准化方法 (z-score)

**核心原则** (`v4/DESIGN.md`, §3.2; `v4/formula.py`, §2)：

所有组分先 z-score 标准化，再加权：
```
X_z^(d) = (X^(d) - μ_X) / σ_X
```

其中 μ_X, σ_X 的计算窗口因域而异：
- 历史域：全部 96 个十年上的均值和标准差
- 金融域：滚动 252 日窗口
- 政治域：全部时间跨度

**v4.0 关键改进** (`v4/DESIGN.md`, §4)：
> "v3.0 无标准化（不同量纲混合）。v4.0 z-score 标准化（先标准化再加权）。"

#### 5.3 滚动窗口选择

| 域 | 滚动窗口 | 理由 |
|------|----------|------|
| 历史 (CBDB) | 96个十年全量 | 数据稀疏，需全量估计 |
| 中国金融 | 252日 | 约1年交易周期 |
| 全球金融 | 252日 | 标准金融年化窗口 |
| 全球政治 | 10年 | 与事件密度匹配 |
| 美索不达米亚 | 100年 | 数据极度稀疏 |
| 实时新闻 | 30日 | 快速响应 |

---

### 6. 理论争议与修正

#### 6.1 v6.1.1 的 H-β 修正 (fBm)

**v6.0 的问题** (`v6.1/PHYSICS_DOWNGRADE.md`, §1.1; `v6.1/NATURE_SI_V61.md`, §S3.1)：

v6.0 报告 **H=0.958, β=1.66**，并声称"超临界相变"、"比 Ising 临界态更强"。

**CZ-1 警示**（12维度研究识别）：
> "这个组合**不符合标准分形理论**：fBm 预测 β = 2H + 1 = 2.916；fGn 预测 β = 2H - 1 = 0.916。实测 β=1.66 都不匹配。"

**问题根源**：v6.0 使用 R/S 方法估计 H，使用 FFT 估计 β。两个估计方法**对过程定义不一致**（R/S 假设增量过程，FFT 假设水平过程）。

**v6.1.1 修正** (`v6.1/PHYSICS_DOWNGRADE.md`, §1.2; `v6.3/NATURE_MAIN.md`, §Methods)：

| 维度 | v6.0 (R/S + FFT) | v6.1.1 (DFA + Whittle) |
|------|------------------|---------------------|
| H 估计 | R/S (对长记忆偏差) | DFA (更稳健) |
| β 估计 | FFT (log-log 拟合) | Whittle 似然 |
| 过程定义 | 不一致 | 一致 (增量) |
| 样本量 | 全 25,000+ | 3,000 (避免边界效应) |

**修正后结果** (标普 500, 1927-2026)：
- **H (DFA on level) = 1.5662**
- **β (Whittle on level) = 4.0000**
- 理论 fBm 预测: β = 2H + 1 = 4.1324
- **偏差: 3.2%** — **完全符合 fBm 过程**

#### 6.2 "超临界"到"经典分形"的转变

**重新解读** (`v6.1/PHYSICS_DOWNGRADE.md`, §1.3)：

| 指标 | v6.0 (错误) | v6.1.1 (正确) | 含义 |
|------|------------|------------|------|
| H | 0.958 | **1.5662** | 价格水平是 fBm 过程 (H>1) |
| β | 1.66 | **4.0** | 长程记忆, 强长程正相关 |
| 物理过程 | "超临界相变" (错) | **分数布朗运动 (fBm)** (对) | 经典分形过程 |
| 收益率 H | 未测 | **0.4526** | 收益率接近随机游走 (EMH) |

**新解读**：
- 价格水平 = fBm 过程 (H=1.57) → 强长程正相关
- 收益率 ≈ 随机游走 (H=0.45) → 符合有效市场假说
- **价格水平 + 强长记忆** = 系统状态可持续, 但不可预测具体事件
- 这与"同步器非预测器"框架**完全一致**

#### 6.3 物理降级声明

**主文表述修正** (`v6.1/PHYSICS_DOWNGRADE.md`, §2.1-2.2)：

| 原表述 (v6.0) | 新表述 (v6.1) | 位置 |
|---------------|---------------|------|
| "超临界相变" | **"强长程正相关"** | 移至 SI |
| "比 Ising 临界态更强" | **删除** | — |
| "H=0.958 超临界证据" | **删除** | — |
| "功率谱 β=1.66 棕色噪声" | **保留为"长程相关统计签名"** | 移至 SI |
| "新普适类" | **"经典 fBm 过程的强长程相关"** | SI 讨论 |

**v6.3 主文核心叙事** (`v6.3/NATURE_MAIN.md`, §¶2.3, Discovery #4)：

> "Statistical analysis of S&P 500 PSI series (1927-2026) using DFA and Whittle estimators yields **H = 1.57 for price levels** (consistent with fractional Brownian motion, fBm; the 1/f^4 long-memory signature) and **H = 0.45 for log returns** (consistent with the efficient-market random-walk hypothesis, EMH). This fBm-plus-EMH decomposition is a classical result in financial econometrics. The 'synchronizer, not predictor' framing is its operational consequence."

**v6.3 局限声明** (`v6.3/NATURE_MAIN.md`, §¶3, Limitations)：

> "Second, the **H = 1.57 long-memory signature is an empirical statistical result, not a physical theory**; we report it as the well-known fBm scaling and avoid stronger claims about underlying mechanisms."

---

### 7. 核心概念词典

| 缩写 | 全称 | 定义 | 首次出现 |
|------|------|------|----------|
| **PSI** | Psychological Semantic Index (v3.0前) / Pressure Synchronization Index (v4.x) / Unified Pressure Synchronization Index (v5.0+) | 核心量化指标，衡量系统压力同步水平 | v2.3 |
| **MMP** | Mean Metaphor Polarity / Mass Mobilization Potential / Material | 语义情绪极性/物质压力维度 | v2.3 |
| **EMP** | Expert Emotional Polarity / Elite Mentality Pattern / Elite Mobilization Potential | 专家情绪极性/精英心理状态 | v2.3 |
| **SFD** | Scholar Frequency Density / Social Fracture Degree / State Fiscal Distress / Fragmentation | 专家密度/社会分裂维度 | v2.3 |
| **EED** | Expert Engagement Density / Disengagement | 有效专家比例/精英脱节维度 | v4.0 |
| **GSI** | Geographical Stress Index | 地理压力指数 | v2.3 |
| **TSI** | Temporal Stress Index / 地缘压力推理 | 时序压力指数 | v2.4 |
| **IPW** | Inverse Probability Weighting | 逆概率加权，校正CBDB精英偏差 | v2.4 |
| **SDT** | Signal Detection Theory / Structural Demographic Theory | 信号检测论/结构人口理论 | v2.3 |
| **CBDB** | China Biographical Database | 中国历代人物传记数据库，65万+记录 | v2.3 |
| **CHGIS** | China Historical GIS | 中国历史地理信息系统 | v2.3 |
| **CPM-KB** | Conceptual Metaphor Knowledge Base | 概念隐喻知识库 | v2.3 |
| **PEN** | Pleasantness-Excitement-Nervousness | 愉悦度-激活度-紧张度三维模型 | v2.3 |
| **TKG** | Temporal Knowledge Graph | 时序知识图谱 | v3.0 |
| **MGKGR** | Multi-modal Graph Knowledge Representation | 多模态图知识表示 | v3.0 |
| **HAC** | Heteroskedasticity and Autocorrelation Consistent | Newey-West标准误，处理自相关 | v6.0 |
| **PSM** | Propensity Score Matching | 倾向得分匹配，因果识别 | v6.0 |
| **fBm** | fractional Brownian motion | 分数布朗运动 | v6.1.1 |
| **fGn** | fractional Gaussian noise | 分数高斯噪声 | v6.1.1 |
| **DFA** | Detrended Fluctuation Analysis | 去趋势波动分析，估计Hurst指数 | v6.1.1 |
| **Whittle** | Whittle likelihood | Whittle似然，估计功率谱指数 | v6.1.1 |
| **R/S** | Rescaled Range | 重标极差法，估计Hurst指数（有偏） | v6.0 |
| **FFT** | Fast Fourier Transform | 快速傅里叶变换，估计功率谱（v6.0使用） | v6.0 |
| **EMH** | Efficient Market Hypothesis | 有效市场假说 | v6.1.1 |
| **ROC** | Receiver Operating Characteristic | 受试者工作特征曲线 | v6.0 |
| **AUC** | Area Under Curve | 曲线下面积 | v6.0 |
| **ATE** | Average Treatment Effect | 平均处理效应 | v6.0 |
| **CI** | Confidence Interval / Credible Interval | 置信区间/可信区间 | v2.4 |
| **ETI** | Equal-Tailed Interval | 等尾区间（贝叶斯） | v4.x |
| **HPDI** | Highest Posterior Density Interval | 最高后验密度区间 | v2.4 |
| **ESS** | Effective Sample Size | 有效样本量 | v4.x |
| **r_hat** | Gelman-Rubin convergence diagnostic | Gelman-Rubin收敛诊断 | v4.x |
| **MAE** | Mean Absolute Error | 平均绝对误差 | v4.x |
| **RMSE** | Root Mean Squared Error | 均方根误差 | v4.x |
| **MAPE** | Mean Absolute Percentage Error | 平均绝对百分比误差 | v2.4 |
| **MRR** | Mean Reciprocal Rank | 平均倒数排名 | v3.0 |
| **Cohen's d** | Cohen's d effect size | 效应量（忽略样本量不平衡） | v2.4 |
| **Hedges' g** | Hedges' g effect size | 效应量（小样本偏差校正） | v2.4 |
| **CR** | Contradiction Rule | 矛盾检测规则 (CR-001~CR-004) | v2.3 |
| **CDLI** | Cuneiform Digital Library Initiative | 楔形文字数字图书馆倡议 | v3.0 |
| **FRED** | Federal Reserve Economic Data | 美联储经济数据 | v5.0 |
| **VIX** | Volatility Index | 波动率指数 | v5.0 |
| **LLM** | Large Language Model | 大语言模型 | v3.0 |
| **MCP** | Model Context Protocol | 模型上下文协议 | v3.0 |
| **A2A** | Agent-to-Agent | Agent互操作协议 | v3.0 |

---

### 附录：关键数字速查表

| 指标 | 数值 | 来源文件 |
|------|------|----------|
| CBDB 人物记录总数 | 649,533条 | `Civilization-Oracle_完整技术文档_v2.3.md` |
| A/B级高质量记录 | 30,518条 | `v4/FINAL_REPORT.md` |
| 北宋专家数 | 3,564条 | `Civilization-Oracle_完整技术文档_v2.3.md` |
| 十年窗口数 | 96个 | `v4/FINAL_REPORT.md` |
| LLM API调用次数 | 288次 (96窗×3次) | `v4/STATISTICS_SUMMARY.md` |
| LLM成功率 | 100% | `v4/FINAL_REPORT.md` |
| Cohen's d (盛世vs危机) | 0.43→0.53 (IPW后) | `v4/STATISTICS_SUMMARY.md` |
| Walk-Forward r | 0.964 (76折) | `v4/FINAL_REPORT.md` |
| 贝叶斯 P(明>南) | 99.8% | `v4/STATISTICS_SUMMARY.md` |
| PSI vs 气候 (竺可桢) | r=0.02 (独立) | `v4/STATISTICS_SUMMARY.md` |
| 跨模型一致率 | 6/6 = 100% | `v4/FINAL_REPORT.md` |
| 跨文明 (CDLI Uruk III) | MMP=+0.07 | `v4/STATISTICS_SUMMARY.md` |
| 全球金融召回率 | 241/295 = 81.7% | `v5/V5_SUMMARY.md` |
| 全球政治召回率 | 30/33 = 91% | `v5/V5_SUMMARY.md` |
| Hurst H (v6.0 R/S, 错误) | 0.958 | `v6/UPSI_PAPER.md` |
| 功率谱 β (v6.0 FFT, 错误) | 1.66 | `v6/UPSI_PAPER.md` |
| Hurst H (v6.1.1 DFA, 正确) | 1.5662 | `v6.1/PHYSICS_DOWNGRADE.md` |
| 功率谱 β (v6.1.1 Whittle, 正确) | 4.0000 | `v6.1/PHYSICS_DOWNGRADE.md` |
| 收益率 H (v6.1.1) | 0.4526 | `v6.1/PHYSICS_DOWNGRADE.md` |
| fBm 理论预测 β | 2H+1 = 4.1324 | `v6.1/PHYSICS_DOWNGRADE.md` |
| 实测偏差 | 3.2% | `v6.1/PHYSICS_DOWNGRADE.md` |
| VIX领先股市 | 17天 (r=-0.235) | `v5/V5_SUMMARY.md` |
| 黄金滞后股票 | 1天 (r=+0.346) | `v5/V5_SUMMARY.md` |
| 新闻情绪领先PSI | 3天 | `v6.1/NATURE_SI_V61.md` |
| 欧洲三强PageRank | DE 0.0698, FR 0.0659, UK 0.0647 | `v5/V5_SUMMARY.md` |
| 总文件数 (v6.0) | 165个 / 5.8 MB | `v6/README.md` |
| 总研究时间 | ~18小时 | `v6/README.md` |
| 验证域数 (v6.3) | 7个 | `v6.3/NATURE_MAIN.md` |
| 总观测数 (v6.3) | ~350万 | `v6.3/NATURE_MAIN.md` |
| 时间跨度 (v6.3) | 5,500年 | `v6.3/NATURE_MAIN.md` |

---

*报告完成。所有信息均标注来源文件名，公式、数字、理论引用均来自原始文档。*
