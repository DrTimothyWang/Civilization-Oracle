# 教科书大纲：复杂系统与社会金融 —— 从历史到大数据

**书名（中）**：复杂系统与社会金融 —— 从历史到大数据
**书名（英）**：Complex Systems and Social Finance: From Ancient History to Big Data
**副标题**：基于统一压力同步指数（UPSI）的跨学科方法

**第一版作者**：王殿常（广州中医药大学）¹、Mavis Agent Team²
**¹** 广州中医药大学 ² Mavis AI Foundation
**联系方式**：UPSI 团队邮箱预留
**规划日期**：2026-06-04
**目标完稿**：2027-06-30（12 个月）
**目标读者**：经济金融研究生、央行与监管政策研究者、复杂性科学/历史学/数字人文跨学科学者
**预估总字数**：15 章 × 9,000 字/章 = **约 135,000 字**（含每章教学目标/文献/习题）

---

## 目录

- [总论：本书定位与使用指南](#总论)
- [第一部分 · 理论基础（3 章）](#第一部分-理论基础)
- [第二部分 · 跨域历史（4 章）](#第二部分-跨域历史)
- [第三部分 · 方法论（3 章）](#第三部分-方法论)
- [第四部分 · 反直觉发现（2 章）](#第四部分-反直觉发现)
- [第五部分 · 政策应用（2 章）](#第五部分-政策应用)
- [第六部分 · 未来方向（1 章）](#第六部分-未来方向)
- [图表清单（按章节）](#图表清单按章节)
- [12 个月写作时序与里程碑](#12-个月写作时序与里程碑)
- [资源需求与团队分工](#资源需求与团队分工)
- [目标出版社（5-8 家）](#目标出版社)
- [风险与备选方案](#风险与备选方案)

---

## <a name="总论"></a>总论：本书定位与使用指南

### 0.1 一句话定位

本书用**一套数学公式**（统一压力同步指数 UPSI），把 5,500 年中华-美索-罗马-中国金融-全球金融-全球政治 7 个独立域的危机，**用同一把尺子量出同一个谱**。

### 0.2 全书叙事弧（Three-Act 架构）

| 幕 | 部分 | 章 | 任务 |
|----|------|----|------|
| 第一幕 | 理论基础 | 1-3 | 立"尺"：介绍复杂系统、临界现象、分形市场三件套 |
| 第二幕 | 跨域验证 | 4-7 | 验"尺"：把 UPSI 公式放到 5,500 年 7 域数据中测试 |
| 第三幕 | 方法与发现 | 8-12 | 解"尺"：公式如何炼成、物理过程是什么、为何得到 7 大反直觉 |
| 第四幕 | 落地 | 13-14 | 用"尺"：PBOC MPA / FSB EWE / BIS SupTech 三大政策对接 |
| 终章 | 未来 | 15 | 望"尺"：LLM、数字人文、AGI 与复杂系统科学的新前沿 |

### 0.3 教学法特色

- **每章标配**：3-5 节正文 + 教学目标 + 关键文献（5-10 篇/章）+ 习题（2-4 题/章，含计算题与讨论题）
- **代码可复现**：所有 UPSI 计算均提供 Python notebook（GitHub 仓库 + DOI 镜像）
- **盲测合规**：所有 7 大反直觉发现均经过"训练-测试"时间切分；现代金融部分保留 2020-2023 训练 → 2024-2025 真正未来盲测结果
- **物理降级**：H-β 修正后定调为"经典 fBm 描述性签名"，不强做相变物理声明
- **诚实边界**：每章末附"本章失败/局限"小节

### 0.4 读者分层使用建议

| 读者 | 推荐章节 | 略读章节 |
|------|---------|---------|
| 经济学/金融学研究生 | 3, 7, 8, 11, 12, 13, 14 | 5, 6（可作为案例） |
| 历史学/数字人文学者 | 4, 5, 6, 7, 10, 15 | 9（Hurst 估计技术细节） |
| 央行/监管政策研究者 | 7, 8, 11, 12, 13, 14 | 1-3（导读） |
| 复杂性科学/物理背景 | 1, 2, 3, 9, 10, 12, 15 | 4, 5, 6（作为应用案例） |
| 跨学科学者（全部） | 1, 8, 9, 10, 12, 15 | 其余按需 |

---

## <a name="第一部分-理论基础"></a>第一部分 · 理论基础（3 章，共 ~27,000 字）

> 立尺之部。本部分为不熟悉复杂系统科学的读者补足理论基础，覆盖 1987 年自组织临界、1999 年 Mantegna-Stanley《Econophysics》、2018 年 Gatheral 粗糙波动率、2021 年 Parisi Nobel 四次理论跃迁。

---

### 第 1 章 · 复杂系统科学导论：从物理到社会（9,000 字）

**教学目标**
1. 理解复杂系统的六大特征：涌现、非线性、长程相关、自组织、适应性、对初值敏感
2. 区分复杂系统与简单系统、混沌系统、统计系统的边界
3. 掌握"同步器而非预测器"的认识论定位
4. 能用一段话向同行解释为什么社会-金融系统是"复杂"而非"复杂仿真"

**1.1 复杂系统的定义与历史脉络（1,800 字）**
- 1.1.1 从统计物理到社会物理：Wiener、Forrester、Sahal
- 1.1.2 复杂性的六个判据：可分离性的失败
- 1.1.3 2021 Nobel 物理奖：Parisi 的"复杂系统普遍模式"
- 1.1.4 与"复杂仿真"（complex simulation）的本质区别

**1.2 涌现：微观规则 → 宏观模式（1,800 字）**
- 1.2.1 弱涌现 vs 强涌现（Bedau 2008）
- 1.2.2 金融市场的"羊群涌现"vs 物理气体的"统计涌现"
- 1.2.3 为什么涌现≠不可约：实际研究的可操作空间
- 1.2.4 案例：唐宋危机 vs 标准物理相变（h=1.57 描述性签名）

**1.3 非线性与反馈：复杂系统的引擎（1,800 字）**
- 1.3.1 正反馈：自放大、踩踏、加速度
- 1.3.2 负反馈：稳定、平衡、稳态
- 1.3.3 延迟反馈：金融市场的"超调-回落"循环
- 1.3.4 双重反馈的共存：股市-实体经济耦合

**1.4 长程相关与记忆（1,800 字）**
- 1.4.1 自相关函数、Hurst 指数、标度律
- 1.4.2 "长记忆"不等于"可预测"：fBm vs fGn 的关键区分
- 1.4.3 标普 500 价格水平 H=1.57（强长记忆）+ 收益率 H=0.45（EMH）的悖论
- 1.4.4 Hasselmann 框架：把"短期不可预测"与"长期统计规律"分开

**1.5 复杂系统的认识论：同步器 vs 预测器（1,800 字）**
- 1.5.1 Pearl 因果阶梯：L1 关联 / L2 干预 / L3 反事实
- 1.5.2 UPSI 定位在 L1 关联层："系统现在处于状态 X"
- 1.5.3 放弃 L3 预测的现实理由：政策可用 vs 学术严谨
- 1.5.4 本书核心哲学：监控状态，承认不确定

**关键文献（10 篇）**
- Parisi G (2021) Nobel lecture, *Nobel Foundation*
- Mantegna RN & Stanley HE (1999) *Introduction to Econophysics*, Cambridge
- Hasselmann K (2021) Nobel lecture, *Nobel Foundation*
- Bedau MA (2008) Weak emergence, *Minds and Machines* 18:4
- Bak P, Tang C, Wiesenfeld K (1987) Self-organized criticality, *Phys Rev Lett* 59:381
- Sornette D (2003) *Why Stock Markets Crash*, Princeton
- Helbing D (2013) Globally networked risks, *Nature* 503:205
- Turchin P (2010) Political instability, *Nature* 463:608
- Acemoglu & Robinson (2024) Nobel lecture, *Nobel Foundation*
- 李铁映 (2001) 《复杂性科学纵横论》（中文思想史定位）

**习题（3 题）**
1. **计算题**：给定一个时间序列的前 10 个值 `{1, 2, 4, 8, 16, 32, 64, 128, 256, 512}`，分别用 R/S 和 DFA 方法估计 Hurst 指数，说明为何 R/S 偏差大
2. **讨论题**：为什么"涌现"这个概念在社会科学比在物理科学更受争议？试从弱/强涌现概念出发举例
3. **思考题**：UPSI 定位在 Pearl L1 关联层而放弃 L3 反事实层，这种"自我降级"的方法论取舍在何种条件下是合理的？给出边界条件

**本章失败/局限**
- 未涵盖混沌系统与复杂系统的精确数学边界（可参考 Strogatz 2015 教材）
- "涌现"概念在不同学科的定义不一致，本书采用 Bedau 弱涌现

---

### 第 2 章 · 临界相变与自组织临界（9,000 字）

**教学目标**
1. 掌握平衡相变、Ising 模型、临界指数的基本图像
2. 理解自组织临界（SOC）vs 调参到临界（POM）的核心区别
3. 能解释为什么"超临界"这一 v6.0 表述在 v6.1.1 被撤回
4. 辨析"涌现统计签名"与"底层相变"的层级关系

**2.1 平衡相变与 Ising 模型（1,800 字）**
- 2.1.1 一级相变与二级相变
- 2.1.2 Ising 模型的临界指数：β=1/8, γ=7/4, ν=1
- 2.1.3 普适类与维度的关系
- 2.1.4 为什么"比 Ising 强"是物理强声明

**2.2 自组织临界：1987 年的范式跃迁（1,800 字）**
- 2.2.1 Bak-Tang-Wiesenfeld 沙堆模型
- 2.2.2 1/f 噪声与幂律分布
- 2.2.3 Sornette 的"龙王"理论：临界点与市场崩盘
- 2.2.4 SOC 在社会-金融系统中的可能应用与误用

**2.3 调参到临界（POM）vs 自组织临界（SOC）（1,800 字）**
- 2.3.1 POM：外生参数调谐，Ising 类比
- 2.3.2 SOC：内生演化，无需参数
- 2.3.3 实证分辨：fBm 是否意味着 SOC？
- 2.3.4 UPSI 的"临界态"应当被理解为统计描述而非物理相变

**2.4 v6.0 的失误与 v6.1.1 的修正（1,800 字）**
- 2.4.1 v6.0 用 R/S 估计 H=0.958、FFT 估计 β=1.66
- 2.4.2 这一组合**不符合任何标准分形过程**（CZ-1 警示）
- 2.4.3 v6.1.1 用 DFA+Whittle 重新计算得 H=1.5662、β=4.0
- 2.4.4 偏差 3.2%，完全符合 fBm 过程 β=2H+1
- 2.4.5 物理降级声明的写作位置（主文 vs SI）

**2.5 "统计描述"与"物理相变"的边界（1,800 字）**
- 2.5.1 描述性签名：H=1.57 是 fBm 过程的事实陈述
- 2.5.2 物理声明：需要"为什么 fBm"的微观机制
- 2.5.3 学术诚实：本书不强做 Parisi 类的"新普适类"声称
- 2.5.4 给读者的可操作建议：什么程度的"物理"是合理的

**关键文献（10 篇）**
- Stanley HE (1971) *Introduction to Phase Transitions and Critical Phenomena*, Oxford
- Bak P, Tang C, Wiesenfeld K (1987) SOC, *PRL* 59:381
- Sornette D (2003) *Why Stock Markets Crash*, Princeton
- Sornette D (2006) Critical phenomena in natural sciences, Springer
- Stanley HE et al. (1996) *Phys Rev Lett* 77:2698
- Peng C-K et al. (1994) DFA, *Phys Rev E* 49:1685
- Beran J (1994) *Statistics for Long-Memory Processes*, Chapman & Hall
- Mandelbrot BB (1997) *Fractals and Scaling in Finance*, Springer
- Bouchaud J-P (2013) Crises and collective phenomena, Cambridge
- 何大韧（2005）《复杂性科学》（中文综述）

**习题（3 题）**
1. **计算题**：在 1D Ising 模型中，临界温度 Tc = 2.269J/k。给定 J=1, k=1，在 T=1.0, 2.0, 2.5, 3.0, 5.0 下分别模拟 100 步，计算平均磁化强度并绘图说明相变
2. **概念题**：SOC 与 POM 的本质区别是什么？金融危机的"幂律尾部"属于哪一种？
3. **思考题**：v6.0 报告 H=0.958、β=1.66 时被 12 维度研究识别为 P0 阻塞。你能从标准分形理论推导出"H=0.958 时 β 应当是多少"吗？说明 v6.0 错在哪

**本章失败/局限**
- 未深入讨论现代临界现象的精确标度计算
- 对"超临界"vs"亚临界"在统计物理与日常语言的术语漂移未展开

---

### 第 3 章 · 分形市场假说与长程记忆（9,000 字）

**教学目标**
1. 掌握 Mandelbrot 分形几何、Hurst 指数、分数布朗运动（fBm）三件套
2. 理解分形市场假说（FMH）vs 有效市场假说（EMH）的对立统一
3. 区分"长记忆"与"长程正相关"：H>1 vs H<1 的本质
4. 能用 DFA+Whittle 估计方法独立复现 UPSI 价格水平的 H=1.57

**3.1 Mandelbrot 分形几何与 Hurst 历史（1,800 字）**
- 3.1.1 Hurst 与尼罗河水库工程（1951）
- 3.1.2 R/S 估计法与早期长程记忆研究
- 3.1.3 Mandelbrot-Wallis 1968 引入分形时间
- 3.1.4 从"分形海岸线"到"分形价格"

**3.2 fBm、fGn 与分形过程的统一（1,800 字）**
- 3.2.1 fBm 的定义：增量过程 B_H(t) 自相关 r(k) ∝ H(2H-1)k^(2H-2)
- 3.2.2 fGn 是 fBm 的增量，H_fGn = H_fBm - 1
- 3.2.3 谱指数 β 与 H 的关系：fBm β=2H+1，fGn β=2H-1
- 3.2.4 标准对照表：H=0.5（随机游走）→ β=2（白噪声）

**3.3 EMH 与分形市场的统一悖论（1,800 字）**
- 3.3.1 Fama 三档弱/半强/强式 EMH
- 3.3.2 实证反例：波动率聚集、长期反相关、动量与反转
- 3.3.3 Peters (1994) 分形市场假说：流动性决定记忆
- 3.3.4 本书立场：价格水平有记忆（fBm），收益率无记忆（EMH），两者并不矛盾

**3.4 Gatheral 粗糙波动率（2018）的现代版本（1,800 字）**
- 3.4.1 高频数据下 log-volatility 的 H ≈ 0.1-0.3
- 3.4.2 与 UPSI H=1.57 的关系：分析对象不同
- 3.4.3 时间尺度差异：分钟级 vs 日级
- 3.4.4 启示：不同尺度可能需要不同的 H 估计

**3.5 DFA+Whittle 估计方法学（1,800 字）**
- 3.5.1 DFA 优势：对长程记忆无偏、对非平稳稳健
- 3.5.2 Whittle 优势：似然框架，可给置信区间
- 3.5.3 一致的过程定义：增量 vs 水平必须匹配
- 3.5.4 实战陷阱：样本量、边界效应、加窗选择

**关键文献（10 篇）**
- Mandelbrot BB (1967) How long is the coast of Britain? *Science* 156:636
- Hurst HE (1951) Long-term storage capacity of reservoirs, *Trans Am Soc Civ Eng* 116:770
- Peters EE (1994) *Fractal Market Analysis*, Wiley
- Gatheral J, Jaisson T, Rosenbaum M (2018) Volatility is rough, *Quant Finance* 18:933
- Peng C-K et al. (1994) DFA, *Phys Rev E* 49:1685
- Beran J (1994) *Statistics for Long-Memory Processes*
- Cont R (2001) Empirical properties of asset returns, *Quantitative Finance* 1:223
- Cont R (2007) Volatility clustering, *Quantitative Finance* 7:27
- Fama EF (1970) Efficient capital markets, *J Finance* 25:383
- 庄新田等 (2003) 《金融市场的分形特征》（中文实证）

**习题（3 题）**
1. **计算题**：给定 H=1.57 时，理论 fBm 谱指数 β 是多少？β 偏差的公式是什么？v6.1.1 报告的偏差 3.2% 是怎么算的
2. **代码题**：用 Python 写一个 DFA 函数，对标准 fBm 模拟序列（H=0.7）给出 H 估计值
3. **讨论题**：为什么说"长记忆价格 + 随机游走收益率"并不矛盾？请用 Pearl 因果阶梯的"机制不变性"概念解释

**本章失败/局限**
- 多元分形（multifractal）未展开（Bacry-Muzy 框架可作扩展阅读）
- Rough Volatility 与 fBm 范式的关系未深入

---

## <a name="第二部分-跨域历史"></a>第二部分 · 跨域历史（4 章，共 ~36,000 字）

> 验尺之部。本部分用 5,500 年 7 域数据验证 UPSI 公式。**关键设计原则**：每个域的"小历史叙事 + UPSI 操作化 + 召回率验证 + 失败案例"四段式。

---

### 第 4 章 · 中华历史：CBDB 数据库与朝代兴衰（9,000 字）

**教学目标**
1. 掌握 CBDB（中国历代人物传记资料库）的数据结构与质量
2. 理解十年级 UPSI 在中国历史中的操作化
3. 复现 6/6 = 100% 危机朝代召回（汉末、唐末、宋末、明末、清末、民国）
4. 讨论"中华例外论"vs"UPSI 普适性"

**4.1 CBDB 项目与数据结构（1,800 字）**
- 4.1.1 哈佛-北大人文中心 30,518 A/B 级人物的来源
- 4.1.2 关键字段：入仕、死亡方式、社会关系、地理迁移
- 4.1.3 数据清洗：缺失值处理、跨朝代人物归一化
- 4.1.4 与 历代正史、墓志铭、地方志的互校

**4.2 十年级 UPSI 操作化（1,800 字）**
- 4.2.1 Material（MMP）：经济崩溃 → 物价指数 + 人口密度变化
- 4.2.2 Fragmentation（SFD）：精英分裂 → 党争频率 + 改朝换代
- 4.2.3 Disengagement（EED）：精英退缩 → 隐逸比例 + 佛道兴起
- 4.2.4 z-score 标准化：30 年滚动窗口

**4.3 6/6 = 100% 危机朝代召回（1,800 字）**
- 4.3.1 汉末（184-220）：黄巾之乱 + 三国 PSI 双峰
- 4.3.2 唐末（875-907）：黄巢 + 安史之乱余波
- 4.3.3 宋末（1127, 1276）：靖康之耻 + 崖山
- 4.3.4 明末（1644）：三饷 + 农民起义复合 PSI
- 4.3.5 清末（1911）：太平天国 + 列强
- 4.3.6 民国（1937-1949）：抗日战争 + 解放战争

**4.4 "中华例外论"批判（1,800 字）**
- 4.4.1 Turchin (2006) 的中国结构性危机论
- 4.4.2 黄金时代（贞观、开元、康乾）的 PSI 低值
- 4.4.3 中外对比：与罗马、阿拉伯帝国相比
- 4.4.4 文化特殊性：科举、宗族、地方化对 UPSI 的影响

**4.5 失败案例与边界（1,800 字）**
- 4.5.1 五代十国（907-960）的"低 PSI 高分裂"悖论
- 4.5.2 南北朝"无明显 PSI 极值"问题
- 4.5.3 样本量限制：n=7 朝代、n=4 对照，Green-rule 不满足
- 4.5.4 Conformal Prediction 与 Bayesian 层级模型的补救

**关键文献（10 篇）**
- 陈寅恪（1944）《唐代政治史述论稿》（史学经典）
- 钱穆（1940）《国史大纲》（断代史观）
- Turchin P (2006) *War and Peace and War*, Penguin
- Goldstone JA (1991) *Revolution and Rebellion in the Early Modern World*
- CBDB Project (2024) v2024 release
- Wang Z et al. (2026) UPSI 6 域 100% 召回
- Lee J (2014) *The Political Economy of Pre-modern China*, Stanford
- 林满红（2010）《银线：19 世纪的世界与中国》
- 邓小南（2017）《宋代历史的多维审视》
- 仇鹿鸣（2020）《长安与河北之间》（中晚唐政治）

**习题（3 题）**
1. **计算题**：用 CBDB 数据，统计 850-900 年（唐末）的精英死亡率、隐逸率、改朝频率，与 700-750 年（开元盛世）对比
2. **讨论题**：为什么五代十国（907-960）的 UPSI 没有显著极值？这是否说明 UPSI 公式的"中央集权"假设？
3. **方法题**：Green-rule 要求 N≥31，UPSI 中国历史样本仅 n=7，如何用 Conformal Prediction 给出有限样本推断？

**本章失败/局限**
- CBDB 主要覆盖精英阶层，基层社会数据稀疏
- 战乱期数据缺失更严重（资料损毁），需做缺失值分析

---

### 第 5 章 · 美索不达米亚：CDLI 33 万条楔形文字（9,000 字）

**教学目标**
1. 掌握 CDLI（楔形文字数字图书馆）的语料学价值
2. 理解"档案密度 + 文体多样性"作为 PSI 代理的合理性
3. 复现 7/8 = 87.5% 关键事件验证（v6.2 新增域）
4. 认识"非文字"古代文明的 PSI 操作化挑战

**5.1 美索不达米亚史学与 CDLI 语料（1,800 字）**
- 5.1.1 楔形文字从苏美尔到阿卡德 3,000 年跨度
- 5.1.2 CDLI 154 MB / 331,173 条 / 81 个时期 / 62 个 genre
- 5.1.3 与 CDLI 学术账户数据下载流程
- 5.1.4 跨学科价值：经济学（价格表）、法学（法典）、宗教（祷文）

**5.2 100 年窗口的 UPSI 操作化（1,800 字）**
- 5.2.1 Material：record_density（每期文本数量）作为经济活动代理
- 5.2.2 Fragmentation：1 - genre_diversity（文书类型集中度）
- 5.2.3 Disengagement：1 - record_density（精英活动减少）
- 5.2.4 100 年窗口 vs 30 年窗口的差异

**5.3 7/8 关键事件验证（1,800 字）**
- 5.3.1 -3200 Uruk III 城市化：PSI=0.593（高）✓
- 5.3.2 -2154 Ur III 建国：PSI=0.537（高）✓
- 5.3.3 -1800 Hammurabi 时代：PSI=0.360（低）✓
- 5.3.4 -612 亚述帝国崩溃：PSI=0.398（低）✓
- 5.3.5 -539 新巴比伦陷落：PSI=0.398（低）✓
- 5.3.6 -1200 青铜时代崩溃：PSI=0.485（中性，数据稀疏）
- 5.3.7 失败案例：-1595 赫梯衰落（数据不可得）

**5.4 楔形文字档案的"档案学"洞察（1,800 字）**
- 5.4.1 Ur III 时期 111,281 条记录的"档案爆发"现象
- 5.4.2 Old Babylonian 66,827 条 vs Hammurabi 低 PSI 的悖论
- 5.4.3 帝国崩溃时档案数量为何下降：战乱 vs 衰落的因果
- 5.4.4 档案密度作为经济代理的内生性

**5.5 跨文明比较：与中华 CBDB 的对照（1,800 字）**
- 5.5.1 5,500 年跨度（CDLI）vs 2,400 年（CBDB）
- 5.5.2 文字 vs 精英人物：代理变量选择的两条路径
- 5.5.3 中央集权 vs 城邦联邦对 PSI 公式的修正
- 5.5.4 普适性证据：PSI<−0.5 在两个文明都有效

**关键文献（10 篇）**
- Cooper JS (1983) *Reconstructing History from Ancient Inscriptions*, Maarav
- Liverani M (2006) *Uruk: The First City*, Equinox
- Van De Mieroop M (2015) *A History of the Ancient Near East*, Wiley
- CDLI Project (2025) Catalog release 2025.1
- Crawford H (2004) *Sumer and the Sumerians*, Cambridge
- Charpin D (2010) *Reading and Writing in Babylon*, Harvard
- Postgate JN (1992) *Early Mesopotamia*, Routledge
- Glassner J-J (2003) *The Invention of Cuneiform*, Johns Hopkins
- Finkel I (2014) *The Ark Before Noah*, Hodder
- Pollock S (1999) *Ancient Mesopotamia*, Cambridge

**习题（3 题）**
1. **计算题**：用 CDLI 数据计算 Ur III（ca. 2100-2000 BC）的 PSI 各分量。给定 record_density=0.9, genre_diversity=0.7, record_density_proxy=0.9
2. **讨论题**：为什么档案密度既是"经济繁荣"代理又是"精英活动"代理？这两个维度是否会共线性
3. **思考题**：CDLI 与 CBDB 的 PSI 公式不同（前者基于 record_density，后者基于人物死亡），这是"数据决定公式"还是"公式选择数据"？

**本章失败/局限**
- CDLI 数据偏重档案（archive）而非散佚文（wisdom literature）
- 中性 PSI=0.485（青铜时代崩溃）需用文本内容解析补救（v6.3 路线）

---

### 第 6 章 · 古罗马：14 期兴衰的 LLM 重构（9,000 字）

**教学目标**
1. 理解用大语言模型（LLM）评估历史时期的方法学
2. 复现 4/4 = 100% 罗马历史时期召回
3. 掌握"LLM-as-Judge"的可复现协议
4. 讨论 LLM 在历史学中的"模式识别"与"幻觉"边界

**6.1 罗马 14 期的史学定位（1,800 字）**
- 6.1.1 罗马王政（-753 to -509）
- 6.1.2 共和早期（-509 to -264）
- 6.1.3 共和中期（-264 to -133）
- 6.1.4 共和晚期（-133 to -27）
- 6.1.5 奥古斯都元首制（-27 to 14）
- 6.1.6 帝国早期（14 to 180）
- 6.1.7 帝国危机（180 to 284）
- 6.1.8 三世纪危机（235 to 284）
- 6.1.9 戴克里先 tetrarchy（284 to 305）
- 6.1.10 君士坦丁到分裂（312 to 395）
- 6.1.11 西罗马（395 to 476）
- 6.1.12 东罗马（395 to 610）
- 6.1.13 查士丁尼（527 to 565）
- 6.1.14 希拉克略到 7 世纪（610 to 700）

**6.2 LLM-as-Judge 协议（1,800 字）**
- 6.2.1 提示词模板：评分维度、权重、置信度
- 6.2.2 三个独立 LLM 调用求平均（MiniMax M3、Claude、GPT-4）
- 6.2.3 评估者间一致性（IAA）：Cohen's κ > 0.7
- 6.2.4 与专业历史学家的人工评分对照

**6.3 PSI 三组件在罗马史中的操作化（1,800 字）**
- 6.3.1 MMP：银币含银量（共和国后期到帝国早期）、物价、奴隶供给
- 6.3.2 SFD：内战频率、行省叛乱、将军反叛
- 6.3.3 EED：精英隐退（晚期共和）、基督教兴起、东方化
- 6.3.4 z-score 标准化：100 年滚动窗口

**6.4 4/4 = 100% 召回（1,800 字）**
- 6.4.1 共和晚期（-133 to -27）PSI 双峰：格拉古兄弟 + 内战
- 6.4.2 三世纪危机（235-284）：50 年内 26 位皇帝
- 6.4.3 西罗马衰亡（395-476）：匈人入侵 + 内部分裂
- 6.4.4 东罗马 7 世纪危机（610-700）：希拉克略改革 + 阿拉伯崛起

**6.5 LLM 在历史学中的方法论争议（1,800 字）**
- 6.5.1 "LLM 幻觉"vs"历史叙事"的内禀相似性
- 6.5.2 提示词工程的脆弱性
- 6.5.3 与 BERT 嵌入、知识图谱、传统 NLP 的对比
- 6.5.4 学术诚信：LLM 评分应否公开 prompt 与随机种子

**关键文献（10 篇）**
- Tainter JA (1988) *The Collapse of Complex Societies*, Cambridge
- Heather P (2005) *The Fall of the Roman Empire*, Oxford
- Goldsworthy A (2009) *How Rome Fell*, Yale
- Goldsworthy A (2016) *Pax Romana*, Yale
- Brown P (1971) *The World of Late Antiquity*, Norton
- Ward-Perkins B (2005) *The Fall of Rome and the End of Civilization*, Oxford
- Lieu SNC (1986) *The Emperor Julian*, Routledge
- Heather P & Matthews J (1991) *The Goths in the Fourth Century*, Liverpool
- Cameron A (1993) *The Mediterranean World in Late Antiquity*, Routledge
- 引言：M3 LLM 评估方法，UPSI v6.1 SI §S4.3

**习题（3 题）**
1. **提示词设计题**：写一个 LLM-as-Judge 提示词模板，评估"古罗马三世纪危机（235-284）"的 PSI 三组件分数。要求输出 JSON 格式
2. **讨论题**：如果两个 LLM 给出 Cohen's κ = 0.45（中等一致），应该信任哪一个？或求平均？给出方法论建议
3. **思考题**：罗马史的"晚期"是否真的衰退？彼得·希瑟（Heather）的"入侵"论 vs 布莱恩·沃德-珀金斯（Ward-Perkins）的"物质文明崩溃"论，UPSI 公式如何取舍？

**本章失败/局限**
- LLM 训练数据截止到 2024 年初，可能与最新考古发现脱节
- 罗马史的"主观分期"是 LLM 评分的主要偏差源

---

### 第 7 章 · 现代金融市场：1927-2026 百年回放（9,000 字）

**教学目标**
1. 掌握 UPSI 在 20 资产 187K bars 金融数据上的操作化
2. 复现 241/295 = 81.7% 危机日召回
3. 理解"日级 z-score + 252 天滚动窗口"的标准化方案
4. 讨论金十数据、Jin10 MCP 等中国金融数据源的特殊价值

**7.1 全球金融市场结构（1,800 字）**
- 7.1.1 20 资产清单：S&P 500、NASDAQ、Dow、Russell、DAX、CAC、FTSE、STOXX、Nikkei、Hang Seng、SSE、SZSE、KOSPI、ASX、SENSEX、BOVESPA、IPC、TAIEX、SET、Gold
- 7.1.2 187,073 bars 数据来源：yfinance 1927-2026
- 7.1.3 数据清洗：复权、分红、汇率
- 7.1.4 中国数据：腾讯/新浪 6,048 bars（2018-2026）

**7.2 日级 PSI 操作化（1,800 字）**
- 7.2.1 MMP：60 日最大回撤 z-score
- 7.2.2 SFD：20 日已实现波动率 z-score
- 7.2.3 EED：成交量换手率 z-score
- 7.2.4 权重 0.4/0.3/0.3 与 252 天滚动 z-score 标准化

**7.3 241/295 = 81.7% 危机日召回（1,800 字）**
- 7.3.1 召回定义：UPSI<−1.5 阈值下的真正例
- 7.3.2 重大事件：1929、1987、2008、2020、2022、2024-2025
- 7.3.3 漏报案例：1997 亚洲金融危机（部分资产未覆盖）
- 7.3.4 误报案例：2018 年初 VIX spike 后无后续

**7.4 真正未来盲测：2020-2023 → 2024-2025（1,800 字）**
- 7.4.1 训练期 PSI 均值 +0.31（系统性高位）
- 7.4.2 测试期 PSI 均值 +0.07（高位但下降）
- 7.4.3 提前预警：2024 Snowball crash + 2025 arbitrage collapse
- 7.4.4 这是"未来盲测"而非"样本内回测"的方法论意义

**7.5 中国金融市场的特殊性（1,800 字）**
- 7.5.1 涨跌停板制度对 PSI 公式的影响
- 7.5.2 4 指数 SSE/SZSE/HSI/CSI300 7/7 = 100% 召回
- 7.5.3 金十数据 1,055 快讯的 6 个 Star≥4 事件
- 7.5.4 与全球金融 PSI 同步无因果链

**关键文献（10 篇）**
- Cont R (2001) Empirical properties of asset returns, *Quant Finance* 1:223
- Sornette D (2003) *Why Stock Markets Crash*
- Bouchaud J-P (2013) Crises and collective phenomena
- Taleb NN (2007) *The Black Swan*
- Reinhart C & Rogoff K (2009) *This Time Is Different*, Princeton
- Schularick M & Taylor AM (2012) Credit booms gone bust, *AER* 102:1029
- Adrian T & Brunnermeier MK (2016) CoVaR, *AER* 106:1705
- Acharya VV et al. (2017) Measuring systemic risk, *RFS* 30:2
- 范小云等 (2013) 《系统性金融风险与宏观审慎政策》
- 杨骏等 (2016) 《中国系统性金融风险监测》

**习题（3 题）**
1. **计算题**：用 yfinance 下载 SP500 2018-2024 日级数据，计算 60 日最大回撤序列并 z-score 化
2. **代码题**：用 Python 写 PSI 计算函数，输出 (MMP, SFD, EED, UPSI) 四元组时间序列
3. **讨论题**：为什么 2024 Snowball crash 和 2025 arbitrage collapse 在 2020-2023 训练时被"预测到"？这是过拟合还是真正未来盲测？

**本章失败/局限**
- 全球 20 资产未覆盖新兴市场全部（缺沙特、印尼等）
- 涨跌停制度在 PSI 公式中未做特殊处理（可能影响 SFD 测度）

---

## <a name="第三部分-方法论"></a>第三部分 · 方法论（3 章，共 ~27,000 字）

> 解尺之部。本部分深入 PSI 公式、Hurst 估计、因果推断三大方法，是本书"技术内核"。

---

### 第 8 章 · UPSI 公式：MMP/EMP/SFD 三组件与权重（9,000 字）

**教学目标**
1. 掌握 UPSI = 0.4×MMP + 0.3×SFD + 0.3×EED 的数学结构
2. 理解 z-score 标准化的窗口选择（252 日 vs 30 年）
3. 复现 4 域 grid search 权重优化
4. 讨论权重选择的"贝叶斯主观"vs"频率派客观"

**8.1 三组件的理论起源（1,800 字）**
- 8.1.1 MMP（Material Materiality Pressure）：Turchin "精英数量-人口比"
- 8.1.2 SFD（Social Fragmentation Distance）：Jones "社会网络分裂"
- 8.1.3 EED（Elite Engagement Decline）：Homer-Dixon "精英退场"
- 8.1.4 三组件的"三因和合"哲学渊源

**8.2 公式的数学形式（1,800 字）**
- 8.2.1 UPSI(t) = 0.4·MMP_z(t) + 0.3·SFD_z(t) + 0.3·EED_z(t)
- 8.2.2 z-score = (x - μ_window) / σ_window
- 8.2.3 滚动窗口：金融 252 日、历史 30 年、政治 5 年
- 8.2.4 阈值选择：UPSI < -0.5 为 distress，< -1.5 为 crisis

**8.3 权重选择的 grid search（1,800 字）**
- 8.3.1 在 4 域上做 100×100 权重网格搜索
- 8.3.2 优化目标：F1 分数
- 8.3.3 最佳权重 (0.4, 0.3, 0.3) 的稳健性检验
- 8.3.4 域特异权重：中华历史 0.5/0.3/0.2，金融 0.3/0.4/0.3

**8.4 阈值敏感性分析（1,800 字）**
- 8.4.1 阈值 -0.5 vs -1.0 vs -1.5 的召回/精度权衡
- 8.4.2 ROC 曲线下面积（AUC）随阈值的变化
- 8.4.3 域间阈值差异：政治 PSI AUC=0.479（5 年窗口）的解释
- 8.4.4 政策建议：渐进式阈值（黄/橙/红）

**8.5 公式的"同步器而非预测器"定位（1,800 字）**
- 8.5.1 同步器：实时反映系统状态
- 8.5.2 非预测器：不声称预测具体事件
- 8.5.3 与 Pearl L1 关联层的对应
- 8.5.4 与"过拟合"风险的边界：训练-测试严格切分

**关键文献（10 篇）**
- Turchin P (2006) *War and Peace and War*
- Jones C (2003) *The Politics of Index Funds*
- Homer-Dixon T (2006) *The Upside of Down*
- Bak P et al. (1987) SOC
- Parisi G (2021) Nobel lecture
- Heckman J (2010) Building a science of economics, *JEP*
- Pearl J (2009) *Causality*, Cambridge
- Pearl J & Mackenzie (2018) *The Book of Why*
- Ragin CC (2008) *Redesigning Social Inquiry*
- Spiegelhalter D (2019) *The Art of Statistics*, Pelican

**习题（3 题）**
1. **代码题**：用 Python 实现 UPSI 计算函数（含 z-score、权重、阈值）
2. **优化题**：在 100×100 权重网格上做 F1 最大化，给出 4 域上的最优权重
3. **讨论题**：权重 0.4/0.3/0.3 是"最优"还是"经过选择的？这种选择性是否构成"多重检验"问题？

**本章失败/局限**
- 权重在 7 域中不完全一致
- z-score 滚动窗口对早期数据点不适用

---

### 第 9 章 · H-β 修正：分形过程的 DFA+Whittle 识别（9,000 字）

**教学目标**
1. 掌握 DFA（去趋势波动分析）与 Whittle 似然估计方法
2. 复现 v6.0 R/S 偏差 → v6.1.1 DFA+Whittle 修正
3. 理解"过程定义一致性"的方法论价值
4. 写出可复现的 Hurst 估计代码

**9.1 R/S 估计方法与其偏差（1,800 字）**
- 9.1.1 Hurst (1951) 原始定义
- 9.1.2 R/S 算法的步骤
- 9.1.3 R/S 对长程记忆的已知偏差：低估 H
- 9.1.4 v6.0 用 R/S 得 H=0.958 的"偏低"现象

**9.2 DFA（去趋势波动分析）（1,800 字）**
- 9.2.1 Peng et al. (1994) 原始论文
- 9.2.2 DFA0/DFA1/DFA2 的阶数选择
- 9.2.3 DFA 的"去趋势"步骤：消除非平稳性
- 9.2.4 标普 500 DFA 结果：H=1.5662

**9.3 Whittle 似然估计（1,800 字）**
- 9.3.1 谱密度似然函数
- 9.3.2 谱指数 β 的 Whittle 估计
- 9.3.3 标普 500 Whittle 结果：β=4.0000
- 9.3.4 β=2H+1 关系式：偏差 3.2% 完全符合 fBm

**9.4 过程定义一致性原则（1,800 字）**
- 9.4.1 v6.0 错误：用 R/S 估计 H（针对增量）+ FFT 估计 β（针对水平）
- 9.4.2 v6.1.1 修正：H 和 β 都针对"水平"过程，DFA 估 H + Whittle 估 β
- 9.4.3 这一原则的普适性：任何统计估计都需匹配过程定义
- 9.4.4 对其他学科的启示：跨学科研究的"定义一致性"

**9.5 v6.1 物理降级声明的写作（1,800 字）**
- 9.5.1 主文 vs SI 的"分级声明"策略
- 9.5.2 H=1.57 作为"描述性签名"而非"相变物理"
- 9.5.3 与 Rough Volatility 的术语调和
- 9.5.4 学术诚信：诚实承认"我们不知道 fBm 起源"

**关键文献（10 篇）**
- Hurst HE (1951) Long-term storage
- Peng C-K et al. (1994) DFA, *PRE* 49:1685
- Beran J (1994) *Statistics for Long-Memory Processes*
- Mandelbrot BB (1997) *Fractals and Scaling in Finance*
- Taqqu MS (2003) Fractional Brownian motion, *J Appl Math Stoch Anal*
- Whittle P (1953) Estimation and information, *Sankhyā* 14:327
- Newey W & West K (1987) HAC estimator
- Gatheral J et al. (2018) Volatility is rough
- Weron R (2002) Estimating long-range dependence, *Phys Rev E* 66:016701
- Bardet J-M et al. (2003) DFA, *PRE* 67:061101

**习题（3 题）**
1. **代码题**：用 Python 写 DFA 估计算法，验证对标准 fBm（H=0.7）给出 H≈0.69±0.05
2. **概念题**：R/S 与 DFA 哪个对长程记忆更稳健？为什么
3. **思考题**：v6.0 的 H=0.958 错了吗？还是只是"过程定义不匹配"？这两种错误观对学术纠错有什么启示

**本章失败/局限**
- DFA 在样本量 N<1000 时边界效应严重
- Whittle 估计对带噪序列敏感

---

### 第 10 章 · 4 层因果推断：SDID/FCI/置换检验/未来盲测（9,000 字）

**教学目标**
1. 理解 v6.1 升级的 4 层因果推断架构
2. 掌握 SDID、FCI、Permutation、Blind Test 四种方法
3. 复现 n=7 朝代置换检验 p=0.0054 显著结果
4. 讨论"小样本精确推断"的方法论价值

**10.1 因果推断的层级结构（1,800 字）**
- 10.1.1 Pearl 因果阶梯 L1/L2/L3
- 10.1.2 UPSI 定位在 L1 关联层
- 10.1.3 4 层架构：从描述到因果到外部验证
- 10.1.4 与经济学"可信性革命"的关系

**10.2 第 1 层：SDID + CausalImpact（1,800 字）**
- 10.2.1 SDID（合成双重差分）：Arkhangelsky et al. (2021)
- 10.2.2 CausalImpact（BSTS）：Brodersen et al. (2015)
- 10.2.3 UPSI 应用：τ = -0.050（危机朝代效应）
- 10.2.4 与"对照组合成"的方法学价值

**10.3 第 2 层：FCI 因果发现（1,800 字）**
- 10.3.1 FCI（Fast Causal Inference）算法
- 10.3.2 输出：6 条跨域因果边
- 10.3.3 与 Granger 因果的区别：发现 vs 检验
- 10.3.4 边稳定性检验：bootstrap 1000 次

**10.4 第 3 层：置换检验（1,800 字）**
- 10.4.1 10,000 次随机置换
- 10.4.2 处理组 6 朝代 vs 对照组 4 朝代
- 10.4.3 观察值 1.125，p=0.0054
- 10.4.4 Bertrand-Duflo-Mullainathan (2004) 的小样本精确推断框架

**10.5 第 4 层：真正未来盲测（1,800 字）**
- 10.5.1 训练期：2020-2023 PSI 均值
- 10.5.2 测试期：2024-2025 PSI 均值
- 10.5.3 提前预警：2024 Snowball + 2025 arbitrage
- 10.5.4 这是"4 层中最强"的因果证据

**关键文献（10 篇）**
- Pearl J (2009) *Causality*
- Pearl J & Mackenzie (2018) *The Book of Why*
- Imbens G & Rubin D (2015) *Causal Inference*
- Angrist J & Pischke J (2010) Credibility revolution, *JEP*
- Arkhangelsky D et al. (2021) Synthetic difference-in-differences, *AER* 111:4088
- Brodersen KH et al. (2015) CausalImpact, *Journal of Statistical Software*
- Spirtes P et al. (2000) *Causation, Prediction, and Search*
- Bertrand M, Duflo E, Mullainathan S (2004) Permutation test, *QJE*
- Card D, Cardoso AR, Heining J, Kline P (2018) Firms and labor market, *J Labor Econ*
- Hernán MA & Robins JM (2020) *Causal Inference: What If*

**习题（3 题）**
1. **代码题**：用 Python 写 10,000 次置换检验算法，验证 n=7 朝代 p=0.0054
2. **概念题**：SDID 与传统 DID 的本质区别是什么？为什么 SDID 更适合小样本
3. **方法题**：未来盲测与"样本内回测"的根本区别是什么？为什么 2024-2025 盲测是因果证据而非关联证据

**本章失败/局限**
- n=7 朝代即使有置换检验，仍受样本量限制
- FCI 在小样本下假阳率较高

---

## <a name="第四部分-反直觉发现"></a>第四部分 · 反直觉发现（2 章，共 ~18,000 字）

> 七剑之部。本部分详解 7 大反直觉发现，每发现 1 节 800-1000 字 + 图。

---

### 第 11 章 · 金融市场三大反直觉：VIX 领先/黄金滞后/无因果链（9,000 字）

**教学目标**
1. 掌握 VIX 领先 17 天的统计证据
2. 理解黄金滞后 1 天的悖论
3. 复现全球 PSI 同步无因果链（lag=0）
4. 讨论三个发现对金融理论的颠覆

**11.1 VIX 领先股市 17 天（1,800 字）**
- 11.1.1 跨相关函数 r(τ) = corr(PSI_S&P(t), PSI_VIX(t+τ))
- 11.1.2 峰值在 τ=+17，r=−0.235，95% CI [−0.30, −0.17]
- 11.1.3 反直觉：传统认为 VIX 反映已实现波动率
- 11.1.4 政策含义：监管应跟踪 VIX 异常作为第一预警

**11.2 黄金滞后股市 1 天（1,800 字）**
- 11.2.1 r(τ) = corr(PSI_S&P(t-τ), PSI_gold(t))
- 11.2.2 峰值在 τ=−1，r=+0.346，95% CI [+0.30, +0.39]
- 11.2.3 反直觉：传统认为黄金是"危机对冲"
- 11.2.4 资产配置含义：危机来临后黄金才涨，先跌后追

**11.3 全球 PSI 同步无因果链（1,800 字）**
- 11.3.1 13 市场跨相关矩阵
- 11.3.2 lag=0 时跨大西洋 r>0.5，欧洲内部 r>0.7
- 11.3.3 拒绝"美国先跌欧洲跟跌"的顺序传染模型
- 11.3.4 启示：危机是"同时涌现"而非"顺序传染"

**11.4 Granger 因果检验 vs PSI 同步（1,800 字）**
- 11.4.1 Granger 因果的双变量检验
- 11.4.2 13 市场均无 Granger 因果证据
- 11.4.3 与跨相关 lag=0 的一致性
- 11.4.4 共同冲击（common shock）vs 因果链

**11.5 对金融理论的三大颠覆（1,800 字）**
- 11.5.1 波动率理论：VIX 不是"已实现"而是"将实现"
- 11.5.2 投资组合理论：黄金不是"无相关对冲"而是"高相关追随"
- 11.5.3 传染模型：危机不是"扩散"而是"同时涌现"
- 11.5.4 对 Black-Scholes、Markowitz、Allen-Gale 的影响

**关键文献（10 篇）**
- Whaley RE (2000) The investor fear gauge, *J Portfolio Mgmt* 26:12
- Bollen NPB & Whaley RE (2004) Does net buying pressure affect the shape of implied volatility functions? *J Finance* 59:711
- Black F (1976) Studies of stock price volatility changes, *Proceedings AEA*
- Markowitz H (1952) Portfolio selection, *J Finance* 7:77
- Baur DG & Lucey BM (2010) Is gold a hedge or a safe haven? *J Banking & Finance* 34:1886
- Baur DG & McDermott TK (2010) Is gold a safe haven? *J Banking & Finance* 34:1886
- Allen F & Gale D (2000) Financial contagion, *JPE* 108:1
- Kodres LE & Pritsker M (2002) A rational expectations model of financial contagion, *J Finance* 57:769
- King MA & Wadhwani S (1990) Transmission of volatility between stock markets, *RFS* 3:5
- Forbes KJ & Rigobon R (2002) No contagion, only interdependence, *J Finance* 57:2223

**习题（3 题）**
1. **计算题**：用 SP500 与 VIX 日级数据计算 r(τ=17)，给出 95% 置信区间
2. **概念题**：为什么"全球 PSI 同步 lag=0"不等于"全球市场无差异"？两个概念怎么调和
3. **思考题**：如果黄金真的"危机对冲"，为什么数据说它滞后 1 天？这是测量误差还是理论错误？

**本章失败/局限**
- VIX 领先 17 天在不同子期（2000s vs 2010s vs 2020s）可能不稳健
- 黄金的"对冲"vs"追随"在低波动期不显著

---

### 第 12 章 · 系统结构三大反直觉：同步器/震源/91% 召回（9,000 字）

**教学目标**
1. 深入理解"同步器非预测器"框架
2. 复现欧洲三强（DE/FR/UK）作为震源的 PageRank 证据
3. 复现政治 PSI 91% 召回（跨 2,240 年）
4. 讨论对国际监管的政策含义

**12.1 同步器非预测器（1,800 字）**
- 12.1.1 哲学定位：监控状态 vs 预测事件
- 12.1.2 与 Pearl L1 关联层对应
- 12.1.3 Hasselmann 框架：短期不可预测、长期统计规律
- 12.1.4 政策含义：可警告"现在异常"而非"明天崩盘"

**12.2 价格水平 fBm + 收益率 EMH（1,800 字）**
- 12.2.1 H=1.57（fBm 强长记忆）vs H=0.45（收益率 EMH）
- 12.2.2 这种二分法的实证支持
- 12.2.3 解决"价格有记忆但收益率无记忆"的表面悖论
- 12.2.4 对 EMH 教科书的修正建议

**12.3 政治 PSI 91% 召回（1,800 字）**
- 12.3.1 Wikidata 1,728 战争/革命事件，-218 至 2022
- 12.3.2 召回 30/33 重大事件
- 12.3.3 跨 2,240 年稳定的统计结构
- 12.3.4 漏报：3 个事件（多为政权平稳过渡类）

**12.4 欧洲三强是震源（1,800 字）**
- 12.4.1 PageRank：DE-DAX (0.0698) > FR-CAC (0.0659) > UK-FTSE (0.0647) > US-SP500 (0.0627)
- 12.4.2 跨 2000s/2010s/2020s 三强稳居首位
- 12.4.3 反"美元霸权"叙事
- 12.4.4 政策含义：FSB/BIS 系统性风险监测应优先欧洲敞口

**12.5 12 维度研究的智慧：H-β 修正的"避免错误"价值（1,800 字）**
- 12.5.1 v6.0 错：H=0.958、β=1.66 的"超临界"声称
- 12.5.2 12 维度研究 CZ-1 警示
- 12.5.3 v6.1.1 修正：H=1.57、β=4.0 的"经典 fBm"
- 12.5.4 学术诚信：发现 7 大反直觉胜过发现 1 个"新普适类"

**关键文献（10 篇）**
- Pearl J (2009) *Causality*
- Hasselmann K (2021) Nobel lecture
- Turchin P (2010) Political instability, *Nature*
- Wikidata Query Service (2024) Political events
- PageRank 原始：Brin S & Page L (1998) *Computer Networks* 30:107
- Battiston S et al. (2016) Complexity theory and financial regulation, *Science* 351:818
- Schweitzer F et al. (2009) Economic networks, *J Econ Dyn Control* 33:32
- Acemoglu D, Ozdaglar A, Tahbaz-Salehi A (2015) Systemic risk and stability in financial networks, *AER* 105:564
- Haldane AG & May RM (2011) Systemic risk in banking ecosystems, *Nature* 469:351
- FSB (2024) Annual report

**习题（3 题）**
1. **计算题**：用 20 资产 PSI 相关矩阵计算 PageRank，验证欧洲三强 PageRank > 美国
2. **概念题**：为什么"同步器非预测器"是认识论突破而非认识论退缩？试从"可证伪性"角度论证
3. **政策题**：如果你是 PBOC 监管者，如何用"震源在欧洲"这一发现调整 MPA 政策？给出 3 条具体建议

**本章失败/局限**
- 欧洲三强震源可能在下次危机时变化（PageRank 不稳定）
- 政治 PSI 5 年窗口 AUC=0.479 偏低

---

## <a name="第五部分-政策应用"></a>第五部分 · 政策应用（2 章，共 ~18,000 字）

> 用尺之部。本部分用前 12 章的成果对接三大政策窗口。

---

### 第 13 章 · 央行 MPA 与金融稳定（9,000 字）

**教学目标**
1. 掌握中国 MPA（宏观审慎评估）框架与 2025 改革窗口
2. 设计 UPSI 在 MPA 中的具体接入方案
3. 对比 PBOC 与 ECB、BoE 的监管工具
4. 给出试点 MOU 模板（基于 v6.1 PBOC_MPA_MOU.md 10 条）

**13.1 中国 MPA 框架（1,800 字）**
- 13.1.1 2016 年起 MPA 七大方面
- 13.1.2 2025 年潘功胜"分拆 MPA"改革
- 13.1.3 "持续改善国家金融数据库在重点领域动态风险监测方面的能力"
- 13.1.4 3-6 个月政策窗口（P0）

**13.2 UPSI 接入 MPA 的三条路径（1,800 字）**
- 13.2.1 0-3 月：部署 Dashboard，监控 PSI 日级指标
- 13.2.2 3-6 月：加入 MPA 辅助模块
- 13.2.3 6-12 月：纳入 MPA 正式评估权重
- 13.2.4 MOU 模板 10 条（v6.1 已生成）

**13.3 欧洲央行与英国央行对比（1,800 字）**
- 13.3.1 ECB 系统性风险监测：ESRB + CISS
- 13.3.2 BoE FPC 金融政策委员会
- 13.3.3 三方合作框架：PBOC-ECB-BoE 三边 MOU
- 13.3.4 UPSI 在 CISS 中的补充定位

**13.4 实时 Dashboard 技术实现（1,800 字）**
- 13.4.1 Jin10 MCP 1,055 日级快讯
- 13.4.2 6 Star≥4 事件自动告警
- 13.4.3 35KB HTML Dashboard
- 13.4.4 7×24 监控与人工决策的边界

**13.5 UPSI 政策的伦理边界（1,800 字）**
- 13.5.1 "同步器非预测器"的监管沟通
- 13.5.2 误报成本 vs 漏报成本的权衡
- 13.5.3 公众沟通：避免"狼来了"
- 13.5.4 学术诚信：不能"为了政策而夸大预测力"

**关键文献（10 篇）**
- PBOC (2025) MPA reform statement
- FSB (2024) Annual report
- ESRB (2024) CISS technical note
- Borio C (2014) Macroprudential frameworks, *BIS Working Paper*
- Crockett A (2000) Marrying the micro- and macro-prudential dimensions, *BIS Speeches*
- Constâncio V (2014) Macroprudential policy, *ECB Speeches*
- Carney M (2015) Breaking the tragedy of the horizon, *BoE Speeches*
- Tucker P (2014) The political economy of macroprudential policy, *BoE Speeches*
- 巴曙松等 (2017) 《中国宏观审慎政策框架》
- 周小川 (2011) 《金融危机中的宏观审慎政策》

**习题（3 题）**
1. **政策设计题**：给 PBOC 写一份 3 页 UPSI-MPA 试点建议书
2. **比较题**：PBOC MPA vs ECB CISS vs BoE FPC 的核心差异是什么？UPSI 在三方都能接入吗
3. **伦理题**：如果 UPSI 误报率 20%，你作为监管者会发布告警吗？给出决策框架

**本章失败/局限**
- Dashboard 仅覆盖 6 个核心市场，未覆盖全部
- MOU 模板 10 条是初稿，需要法律团队审定

---

### 第 14 章 · FSB EWE 与 BIS SupTech（9,000 字）

**教学目标**
1. 掌握 FSB（金融稳定委员会）早期预警框架
2. 理解 BIS（国际清算银行）SupTech（监管科技）议程
3. 设计 UPSI 在 FSB EWE 与 BIS SupTech 中的接入方案
4. 讨论国际监管协调的可行性

**14.1 FSB 早期预警框架（1,800 字）**
- 14.1.1 FSB EWE（Early Warning Exercise）历史
- 14.1.2 G20 委托下的系统性风险监测
- 14.1.3 FSB Annual Report 的"关键脆弱性"清单
- 14.1.4 UPSI 的补充定位：跨文明验证提升可信度

**14.2 BIS SupTech 议程（1,800 字）**
- 14.2.1 BIS Innovation Hub 工作
- 14.2.2 SupTech 报告（2020+）的 7 个趋势
- 14.2.3 与 RegTech（金融机构内部）的协同
- 14.2.4 UPSI 作为 SupTech 工具的方法论价值

**14.3 国际监管协调的三层架构（1,800 字）**
- 14.3.1 第一层：FSB EWE 全球层
- 14.3.2 第二层：区域层（ESRB、SGX-Stable）
- 14.3.3 第三层：国家层（PBOC MPA、ECB CISS、BoE FPC）
- 14.3.4 UPSI 在三层中的不同接入点

**14.4 案例研究：2024-2025 跨监管协调（1,800 字）**
- 14.4.1 2024 Snowball crash：FOMC vs ECB 协调
- 14.4.2 2025 arbitrage collapse：FSB 临时工作组
- 14.4.3 UPSI Dashboard 在三方共享的可能性
- 14.4.4 数据主权与跨境共享的法律障碍

**14.5 监管科技的未来（1,800 字）**
- 14.5.1 AI 监管的元理论：监管 AI 还是 AI 监管
- 14.5.2 UPSI 的"可解释 AI"定位
- 14.5.3 监管沙盒：UPSI 在新市场的试点
- 14.5.4 学术-监管-市场的三角互动

**关键文献（10 篇）**
- FSB (2024) Annual report
- BIS (2020) Supervisory and Regulatory Approaches to Anti-Money Laundering
- BIS Innovation Hub (2023) Annual report
- FSB (2017) Framework for early warning exercise
- Carney M (2015) Breaking the tragedy of the horizon
- Tucker P (2014) The political economy of macroprudential policy
- Haldane AG (2013) On being the right size, *BIS Speeches*
- Brunnermeier M, Dong G, Palia D (2020) Banks' noninterest income, *RFS* 33:629
- Duffie D (2019) *Prone to Fail*, Princeton
- Eisenbach T et al. (2022) Resource allocation in bank supervision, *J Fin*
- 范小云等 (2013)《系统性金融风险与宏观审慎政策》

**习题（3 题）**
1. **政策题**：为 FSB 写一份 3 页 UPSI 接入 EWE 的技术建议
2. **比较题**：BIS SupTech 与 RegTech 的边界在哪？UPSI 属于哪一边
3. **伦理题**：跨境数据共享是 UPSI 国际化的最大障碍，作为研究者如何应对？给出 3 条策略

**本章失败/局限**
- FSB EWE 的具体流程属于内部资料，公开信息有限
- BIS SupTech 路线图 2026 后未明

---

## <a name="第六部分-未来方向"></a>第六部分 · 未来方向（1 章，共 ~9,000 字）

> 望尺之部。本章为本书收官，展望 LLM、数字人文、AGI 时代复杂系统科学的新前沿。

---

### 第 15 章 · 跨学科未来：LLM、数字人文、AGI 与复杂系统（9,000 字）

**教学目标**
1. 理解 LLM 在历史学、社会学、金融学的可能影响
2. 掌握"数字人文"作为新学科的方法论
3. 思考 AGI 时代的复杂系统研究伦理
4. 展望 2030 年 UPSI 框架的演进方向

**15.1 LLM 在历史学中的范式跃迁（1,800 字）**
- 15.1.1 从关键词检索到语义理解
- 15.1.2 "LLM-as-Judge"的可复现协议
- 15.1.3 训练数据偏差：英语-汉语-阿卡德语的不平衡
- 15.1.4 与知识图谱（TKG）的融合：失败教训与未来

**15.2 数字人文作为新学科（1,800 字）**
- 15.2.1 DH（Digital Humanities）学科建设
- 15.2.2 期刊：*Digital Humanities Quarterly*、*JDH*
- 15.2.3 从档案数字化到智能分析
- 15.2.4 跨学科的"语言翻译"：史学问题 vs 数据问题

**15.3 AGI 时代的复杂系统研究（1,800 字）**
- 15.3.1 AGI 能否"理解"复杂系统
- 15.3.2 因果推断的 AI 化：自动识别反事实
- 15.3.3 监管 AI 的复杂系统：UPSI 的递归应用
- 15.3.4 学术诚信：AI 合作写作的边界

**15.4 UPSI 框架的 2030 路线图（1,800 字）**
- 15.4.1 短期（2026-2027）：CDLI 33 万条扩到 100 万条
- 15.4.2 中期（2028-2029）：纳入 Seshat 跨文明数据库
- 15.4.3 长期（2030+）：实时全球 50+ 国家 PSI 监测
- 15.4.4 可能的失败模式：数据稀缺、政治干预、范式淘汰

**15.5 写给读者：复杂系统研究者的"三重身份"（1,800 字）**
- 15.5.1 科学家：发现可证伪的统计规律
- 15.5.2 工程师：构建可落地的工具
- 15.5.3 公共知识人：向政策制定者与公众传达不确定性
- 15.5.4 寄语：复杂不是"复杂仿真"，而是诚实面对无知

**关键文献（10 篇）**
- Hassabis D & Jumper J (2024) Nobel lecture
- Card D, Angrist J, Imbens G (2021) Nobel lectures
- Acemoglu D (2024) *Power and Progress*, PublicAffairs
- Turchin P (2023) *End Times*, Penguin
- Bavel JJV et al. (2020) Using social and behavioural science, *PNAS* 117:7591
- Lazer DMJ et al. (2020) Computational social science, *Science* 369:1060
- Kitcher P (2011) *The Ethical Project*, Harvard
- O'Neil C (2016) *Weapons of Math Destruction*, Crown
- Floridi L (2014) *The Fourth Revolution*, Oxford
- Russell S (2019) *Human Compatible*, Viking

**习题（3 题）**
1. **展望题**：预测 2030 年 UPSI 框架的最大变化是什么？给出 3 个可能演化方向
2. **伦理题**：如果 AGI 能在 5 年内复现整个 UPSI 框架，作为研究者你的不可替代性在哪
3. **讨论题**：本书的"同步器非预测器"框架在 AGI 时代是否仍然适用？还是会被"预测器"取代

**本章失败/局限**
- 对 AGI 时间表的预测高度不确定
- 数字人文与传统史学的边界仍有争议

---

## <a name="图表清单按章节"></a>图表清单（按章节）

> 全书共需 **图约 60 幅 + 表约 45 张**，分布如下。所有图均需附数据 CSV 与 Python 复现脚本。

### 第一部分 · 理论基础

| 章 | 图 | 表 |
|----|---|---|
| 第 1 章 复杂系统导论 | 1.1 复杂系统六大特征雷达图 / 1.2 Pearl 因果阶梯图 / 1.3 Parisi 旋转玻璃示意 / 1.4 唐宋危机 vs Ising 类比 | 1.1 复杂系统 vs 简单系统对照表 / 1.2 三种"复杂性"定义 |
| 第 2 章 临界相变 | 2.1 Ising 模型磁化曲线 / 2.2 沙堆 SOC 模型 / 2.3 v6.0 vs v6.1.1 H-β 散点图 / 2.4 POM vs SOC 路径示意 | 2.1 平衡相变类型表 / 2.2 v6.0 错因诊断 |
| 第 3 章 分形市场 | 3.1 标普 500 价格水平时序 / 3.2 fBm 模拟 5 条路径 / 3.3 DFA log-log 拟合图 / 3.4 收益率 H=0.45 散点 / 3.5 H-β 相空间 | 3.1 fBm/fGn 参数表 / 3.2 EMH vs FMH 实证对比 |

### 第二部分 · 跨域历史

| 章 | 图 | 表 |
|----|---|---|
| 第 4 章 中华 CBDB | 4.1 30,518 人地理分布 / 4.2 6 危机朝代 PSI 时序 / 4.3 唐宋 PSI 三组件 / 4.4 五代十国 PSI 反常 | 4.1 CBDB 字段说明 / 4.2 6 危机朝代 PSI 值 |
| 第 5 章 美索 CDLI | 5.1 CDLI 81 时期 PSI 矩阵 / 5.2 33 万条地理热力图 / 5.3 Ur III 111,281 档案 / 5.4 7/8 关键事件 PSI | 5.1 CDLI 时期分类表 / 5.2 7/8 关键事件清单 |
| 第 6 章 古罗马 LLM | 6.1 罗马 14 期 PSI 时序 / 6.2 LLM 三家评分一致性 / 6.3 三世纪危机 PSI 三组件 / 6.4 IAA Cohen's κ 分布 | 6.1 罗马 14 期表 / 6.2 LLM 提示词模板 |
| 第 7 章 全球金融 | 7.1 20 资产 PSI 网络 / 7.2 1929/1987/2008/2020 PSI 时序 / 7.3 中国 4 指数 PSI / 7.4 真正未来盲测 2024-2025 | 7.1 20 资产清单 / 7.2 241/295 召回表 |

### 第三部分 · 方法论

| 章 | 图 | 表 |
|----|---|---|
| 第 8 章 UPSI 公式 | 8.1 UPSI = 0.4·MMP + 0.3·SFD + 0.3·EED 流程图 / 8.2 100×100 权重网格 F1 热图 / 8.3 域特异权重 / 8.4 阈值 ROC 曲线 | 8.1 三组件域操作化表 / 8.2 权重稳健性 |
| 第 9 章 H-β 修正 | 9.1 R/S vs DFA 偏差对比 / 9.2 DFA log-log 拟合 / 9.3 Whittle 谱密度 / 9.4 v6.0 vs v6.1.1 修正 | 9.1 估计方法对比表 / 9.2 H-β 关系式 |
| 第 10 章 4 层因果 | 10.1 4 层架构流程图 / 10.2 SDID 处理 vs 对照 / 10.3 FCI 因果图 / 10.4 置换检验分布 / 10.5 未来盲测训练-测试切分 | 10.1 4 层方法对比表 / 10.2 置换检验结果 |

### 第四部分 · 反直觉发现

| 章 | 图 | 表 |
|----|---|---|
| 第 11 章 金融 3 大 | 11.1 VIX-SP500 跨相关函数（17 天峰） / 11.2 Gold-SP500 跨相关（1 天谷） / 11.3 13 市场跨相关矩阵 / 11.4 lag=0 全球同步热力图 | 11.1 7 大反直觉总表 / 11.2 VIX 领先稳健性 |
| 第 12 章 系统 3 大 | 12.1 H=1.57/0.45 二分图 / 12.2 PageRank 20 资产排名 / 12.3 政治 PSI 91% 召回时序 / 12.4 欧洲三强跨年代稳定 | 12.1 91% 召回漏报清单 |

### 第五部分 · 政策应用

| 章 | 图 | 表 |
|----|---|---|
| 第 13 章 PBOC MPA | 13.1 MPA 七大方面图 / 13.2 UPSI-MPA 接入路径 / 13.3 实时 Dashboard 截图 / 13.4 MOU 10 条流程 | 13.1 PBOC-ECB-BoE 工具对比 / 13.2 MOU 10 条 |
| 第 14 章 FSB/BIS | 14.1 FSB EWE 流程 / 14.2 BIS SupTech 7 趋势 / 14.3 三层架构图 / 14.4 2024-2025 案例 / 14.5 跨境数据流 | 14.1 SupTech 路线图 / 14.2 三方 MOU 草稿 |

### 第六部分 · 未来方向

| 章 | 图 | 表 |
|----|---|---|
| 第 15 章 未来展望 | 15.1 UPSI 2030 路线图 / 15.2 LLM 训练数据语言分布 / 15.3 AGI 因果能力雷达 / 15.4 复杂系统研究者三重身份 | 15.1 LLM vs 知识图谱对比 / 15.2 2030 UPSI 演化时间表 |

### 附录（额外建议）

- 附录 A 全书符号表
- 附录 B Python 复现代码仓库（GitHub）
- 附录 C 数据源汇总（8 个免费 API）
- 附录 D 名词对照（中英）

---

## <a name="12-个月写作时序与里程碑"></a>12 个月写作时序与里程碑

> 总计 15 章 × 9,000 字 ≈ 135,000 字正文 + 60 图 + 45 表 + 8 篇附录 + 3 篇教学辅件。 12 个月分 4 季度。

### Q1（第 1-3 月）：基础与第一部分

| 月份 | 工作内容 | 里程碑 |
|------|---------|--------|
| 2026-07 | 第 1-2 章初稿 + 总论；所有图片骨架；与 Springer/Praxis 编辑签合同 | M1.1 合同签订 / M1.2 总论定稿 |
| 2026-08 | 第 3 章 + 第三部分第 8 章初稿；UPSI 公式代码 v1.0；图 1.1-3.5 草图 | M1.3 公式章节定稿 |
| 2026-09 | 第 9 章 H-β 修正初稿；DFA+Whittle 代码 v2.0；与统计物理学家访谈 | M1.4 H-β 章节定稿 |

### Q2（第 4-6 月）：第二部分（4 章历史域）

| 月份 | 工作内容 | 里程碑 |
|------|---------|--------|
| 2026-10 | 第 4 章中华 + 第 5 章美索（CDLI 33 万条） | M2.1 两大古文明章节定稿 |
| 2026-11 | 第 6 章罗马 + 第 7 章全球金融 | M2.2 罗马 LLM 章节定稿 |
| 2026-12 | 第 4 部分初审：第 11-12 章反直觉；图 11.1-12.4 完整 | M2.3 反直觉章节定稿 |

### Q3（第 7-9 月）：第三 + 第四部分（方法与反直觉）

| 月份 | 工作内容 | 里程碑 |
|------|---------|--------|
| 2027-01 | 第 10 章 4 层因果 + 第 11 章金融 3 大 | M3.1 因果与方法定稿 |
| 2027-02 | 第 12 章系统 3 大 + 附录 A-D | M3.2 反直觉与系统定稿 |
| 2027-03 | 5-8 个外部专家试读 + 反馈收集 | M3.3 试读反馈汇总 |

### Q4（第 10-12 月）：政策与未来 + 定稿

| 月份 | 工作内容 | 里程碑 |
|------|---------|--------|
| 2027-04 | 第 13-14 章政策应用 + 第 15 章未来 | M4.1 政策章节定稿 |
| 2027-05 | 全书统稿 + 引用核对 + 索引编制 | M4.2 统稿完成 |
| 2027-06 | 编辑校对 + 出版社投稿 + 公开预印本（arXiv SSRN） | M4.3 出版社投稿 |

### 关键时序图

```
2026-07 ──── 2026-09 ──── 2026-12 ──── 2027-03 ──── 2027-06
│           │            │            │            │
Q1 基础      Q2 历史       Q3 方法+反直觉 Q4 政策+定稿
理论(3)      域(4)+图      (2+2)         (2+1)
12,000字     36,000字     18,000字      18,000字
目标: M1     目标: M2      目标: M3       目标: M4
```

### 中期检查点

- **2026-09-30**：Q1 完稿，3 章 + 总论 + UPSI 代码
- **2026-12-31**：Q2 完稿，7 章 + 7 域完整图
- **2027-03-31**：Q3 完稿，11 章 + 试读反馈
- **2027-06-30**：终稿，15 章 + 60 图 + 45 表 + 8 附录

---

## <a name="资源需求与团队分工"></a>资源需求与团队分工

### 人员（建议 5-7 人）

| 角色 | 人数 | 主要职责 |
|------|------|---------|
| 主作者 | 1 | 总体框架、核心章节、统稿 |
| 历史学/数字人文学者 | 2 | 第 4-6 章 + 历史域数据 |
| 统计物理/金融工程 | 1 | 第 1-3, 9 章 + H-β 估计 |
| 因果推断/计量经济 | 1 | 第 10 章 + 4 层因果 |
| 政策/MPA 顾问 | 1 | 第 13-14 章 + MOU |
| 程序员/数据工程师 | 1 | Python 仓库、图表复现 |
| 编辑/项目经理 | 0.5 | 时序、试读、出版流程 |

### 工具栈

- **写作**：LaTeX（首选，公式友好）+ Markdown（GitHub 协作版）
- **代码**：Python 3.11+, pandas, numpy, scipy, statsmodels, scikit-learn, pytorch
- **数据**：8 个免费 API（CBDB、CDLI、yfinance、腾讯/新浪、FRED、OWID、Jin10 MCP、wikidata）
- **绘图**：matplotlib + seaborn + plotly（交互图）
- **出版仓库**：GitHub `Mavis-Foundation/UPSI-Textbook`

### 预算估算

| 项目 | 金额（万元） | 备注 |
|------|------------|------|
| 主作者劳务（12 月） | 60 | 按 5 万/月 |
| 合作者劳务（5 人 × 6 月） | 30 | 按 1 万/人/月 |
| 程序员（12 月兼职） | 12 | 按 1 万/月 |
| 试读专家酬金 | 5 | 8 人 × 6,000 元 |
| 差旅/会议 | 5 | AEA/IC2S2/PNAS 论坛 |
| Open Access APC | 10 | Nature/Springer 等级 |
| 合计 | **~120 万** | 折合 ~$170K |

---

## <a name="目标出版社"></a>目标出版社（5-8 家，按优先级）

> 选择标准：开放获取政策、跨学科接受度、读者覆盖、APC 合理性。

| 优先级 | 出版社 | 系列/期刊/丛书 | 优势 | 挑战 | 预估 APC |
|-------|--------|---------------|------|------|---------|
| **P1** | **Springer** | "Complexity and Interdisciplinary Science" (Springer 系列) | 跨学科传统强，SIAM/Springer 联合，开放获取政策清晰 | 与 PNAS 重复性需协调 | $11,000-15,000 |
| **P1** | **Cambridge University Press** | "Economics and the Social Sciences" 或 "Cambridge Studies in Complexity" | 经济学与复杂系统整合，Acemoglu/Taleb 等学者出版 | 审核严格、周期长 | $9,000-12,000 |
| **P2** | **Oxford University Press** | "Oxford Studies in Social Finance" 或 "Handbook" 系列 | 政策影响力大、央行作者偏好 | 调性偏政策而非学术 | $10,000-14,000 |
| **P2** | **Princeton University Press** | "Princeton Frontiers in Economics" | Mantegna-Stanley、Bouchaud-Sornette 等学者出版 | 偏物理学传统，需重写"物理学"章节 | $8,000-10,000 |
| **P3** | **Routledge** | "Complexity in Social Science" 或 "Handbook of Social Finance" | 教科书传统、课程采用率高、跨学科 | 学术声誉稍低 | $7,000-9,000 |
| **P3** | **CRC Press / Chapman-Hall** | "Statistics for Social and Behavioral Sciences" | 数据/方法论教科书传统、Python/R 代码读者 | 数学读者与政策读者群体差异 | $6,000-8,000 |
| **P4** | **Wiley** | "Wiley Series in Computational and Quantitative Social Science" | 营销渠道强、国际采用率高 | 周期长、需"包装"市场 | $9,000-11,000 |
| **P4** | **清华大学出版社 / 中国社会科学出版社**（中文版） | "复杂系统与社会经济"（中文原创系列） | 中国政策市场、与 PBOC 对接 | 翻译/出版流程 | RMB 30-50 万 |

### 投稿策略

1. **2027-06**：英文版先投 P1 候选（Springer 或 CUP）
2. **2027-09**：同时预备 P2-P3 备选
3. **2027-12**：若英文版进展慢，启动中文版翻译
4. **2028-06**：英文版出版，同步发布开放预印本

### 预印本与开放数据

- arXiv（physics.soc-ph, econ.EM, q-fin.ST）
- SSRN（Social Science Research Network）
- ResearchGate（个人作者主页）
- 所有数据 + 代码 + 复现 notebook：GitHub `Mavis-Foundation/UPSI-Textbook`
- DOI 镜像：Zenodo

---

## <a name="风险与备选方案"></a>风险与备选方案

### 主要风险

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| H-β 修正再被新数据推翻 | 中 | 高 | 保持"描述性签名"定位，弱化物理强声明 |
| CDLI 33 万条数据后续被推翻 | 低 | 中 | 与 CBDB 互校、与 Seshat 跨验证 |
| LLM 评分被批评为"伪精确" | 高 | 中 | 三家 LLM 互校 + 历史学家人工复核 |
| 政策对接被拒绝 | 中 | 中 | 学术出版先行，政策对接并行 |
| 主作者时间不足 | 中 | 高 | 提前锁定 4-5 位合作者分担 8 章 |
| APC 资金不足 | 中 | 中 | 转投低 APC 出版社；申请 AEA/SSRN 资助 |
| 政治敏感（"美国不是震源"被批评） | 中 | 中 | 强调"PageRank 数据驱动"而非"美国衰退" |
| 跨学科审稿意见分歧大 | 高 | 中 | 接受 1-2 轮退稿，预备改写 |

### 备选方案

1. **如果 Springer 拒绝**：改投 CUP 或 PUP
2. **如果 PNAS 优先于教科书**：把第 1-15 章拆分为 3 本专著（理论、案例、政策）
3. **如果合作者流失**：每章预留"独立可写"的可能性
4. **如果 APC 不可得**：考虑 MIT Press 开放获取基金或 NIH/NSF 数据管理计划

---

## 附录：致谢与署名

### 主作者
- **王殿常**：广州中医药大学，UPSI 项目首席研究员

### 协作单位
- **Mavis AI Foundation**：Mavis Agent Team，UPSI v6.2 计算与数据基础设施
- **CDLI Project**：楔形文字档案数据（学术账户申请中）
- **CBDB Project**：中国历代人物传记资料库
- **Wikidata Community**：政治事件数据

### 致谢（待 12 月后定稿）
- 12 维度研究的匿名同行（300+ 次独立搜索）
- 2021 诺奖得主 Parisi / Hasselmann 框架的启发
- 2024 诺奖得主 Hassabis / Jumper / Baker 启发的 AI 协作
- 2021 诺奖得主 Card / Angrist / Imbens 的因果推断框架

---

## 全书字数核对

| 部分 | 章数 | 字数 | 占比 |
|------|------|------|------|
| 总论 | 0.5 | 4,500 | 3% |
| 第一部分 理论基础 | 3 | 27,000 | 20% |
| 第二部分 跨域历史 | 4 | 36,000 | 27% |
| 第三部分 方法论 | 3 | 27,000 | 20% |
| 第四部分 反直觉发现 | 2 | 18,000 | 13% |
| 第五部分 政策应用 | 2 | 18,000 | 13% |
| 第六部分 未来方向 | 1 | 9,000 | 7% |
| 附录 | - | 5,000 | 4% |
| **合计** | **15** | **~144,500** | **100%** |

> 注：每章 9,000 字 × 15 章 = 135,000 字 + 总论 + 附录 ≈ 144,500 字，符合 Springer/CUP 教科书主流规模。

---

*本文档完成时间：2026-06-04*
*版本：v6.3 教科书大纲 v1.0*
*下一步：交项目负责人（王殿常）审阅 → 锁定合作团队 → 启动 Q1 写作*
