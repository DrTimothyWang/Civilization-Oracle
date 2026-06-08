## 维度01: 项目元信息与管理档案

> **编制日期**: 2026-06-04
> **信息来源**: 综合阅读 14 份项目元信息与管理档案
>   - `PROJECT_LOG.md`
>   - `00_PROJECT_MASTER/00_PROJECT_HANDOFF.md`
>   - `00_PROJECT_MASTER/01_PROJECT_MASTER_RECORD.md`
>   - `00_PROJECT_MASTER/02_完整文件清单.md`
>   - `00_PROJECT_MASTER/03_计划书与决策日志.md`
>   - `00_PROJECT_MASTER/04_PROJECT_DATA_RECORD.md`
>   - `v6.2_README.md`
>   - `decision.json`
>   - `验证报告.md`
>   - `P3_里程碑报告_v2.4.md`
>   - `P5_里程碑报告_v2.5.md`
>   - `P6_里程碑报告_v2.6.md`
>   - `P7_里程碑报告_v3.0.md`
>   - `Civilization-Oracle_v3.0_项目交付总结.md`

---

### 1. 项目基本信息

| 项目属性 | 具体内容 | 来源 |
|---------|---------|------|
| **项目代号** | Civilization-Oracle（v1.0–v3.0）→ UPSI（Unified Pressure Synchronization Index，v4.x–v6.2） | `00_PROJECT_HANDOFF.md` §A.1, `01_PROJECT_MASTER_RECORD.md` §1 |
| **副标题** | "文明先知" / "Unified Pressure Synchronization Index" | `01_PROJECT_MASTER_RECORD.md` §1 |
| **作者** | Wang Z.（王滇让，广州中医药大学公共卫生管理学院）+ Mavis Agent Team | `00_PROJECT_HANDOFF.md` §A.3, `v3.0_项目交付总结.md` §一 |
| **学术顾问** | 马利军教授（语义心理学） | `00_PROJECT_HANDOFF.md` §A.3, `v3.0_项目交付总结.md` §一 |
| **核心问题** | 历史文明演化有没有可识别的"先兆"？金融危机能不能提前预警？ | `01_PROJECT_MASTER_RECORD.md` §0 |
| **核心答案** | 有。提出 PSI（Psychological Semantic Index / 压力同步指数）作为跨域统一指标，召回率 >85%，跨 6–7 域、~3.5 百万观测、跨 5,500 年 | `01_PROJECT_MASTER_RECORD.md` §0, `v6.2_README.md` |
| **总投入时间** | ~18–20 小时（v3.0 Alpha → v6.2 NOBEL ULTIMATE，约 3–5 天集中研究） | `00_PROJECT_HANDOFF.md` §A.3, `v6.2_README.md` |
| **累计文件数** | 168 个（v6.0）/ 194 个（v6.2） | `00_PROJECT_HANDOFF.md` §A.3, `02_完整文件清单.md` §0, `v6.2_README.md` |
| **数据规模** | ~3.5 百万观测，跨 5,500 年（v6.2）；CBDB 658,339 条总记录，30,518 条 A/B 级纳入分析 | `01_PROJECT_MASTER_RECORD.md` §0, `00_PROJECT_HANDOFF.md` §D.1 |
| **当前版本** | v6.2 NOBEL++ ULTIMATE（2026-06-04） | `v6.2_README.md` |
| **目标期刊** | Nature Letter（首选）→ Nature Human Behaviour → PNAS → PNAS 6 页（v6.1.1 修正版） | `00_PROJECT_HANDOFF.md` §A.3, `v6.2_README.md` |
| **范式定位** | "比诺奖级"——范式转移级，6–7 域统一理论 + 物理谱 + 因果识别 + 政策应用完整体系 | `00_PROJECT_HANDOFF.md` §A.3 |

**三句话核心结论**（`00_PROJECT_HANDOFF.md` §A.4）：
1. UPSI 统一 6–7 个独立域（中华历史 / 美索不达米亚 / 古罗马 / 中国金融 / 全球金融 / 全球政治 / 宏观），~3.5 百万观测、跨 5,500 年、召回率 >85%。
2. 时序呈现超临界相变特征（v6.0：Hurst H=0.958、1/f^1.66 棕色噪声）；v6.1.1 修正为经典分形市场假说（fBm H=1.57，收益率 EMH H=0.45）。
3. 3 大反直觉发现：VIX 领先股市 17 天、黄金滞后 1 天、全球 PSI 同步无因果链。

---

### 2. 版本演进时间线

> **关键说明**：v1.0–v3.0 阶段是「Civilization-Oracle」名义（中华历史聚焦），v4.x 起转型为「UPSI」跨域统一理论框架。

| 版本 | 日期 | 核心突破 | 解决的问题 | 关键交付物 | 来源 |
|------|------|---------|-----------|-----------|------|
| **Phase 0** | < 2026-05-27 | 理论孕育 | 核心假设成型 | PSI 公式雏形 | `00_PROJECT_HANDOFF.md` §B.1 |
| **v1.0** | 2026-05-28 | 理论框架 + 公式设计 | "怎么做" | `06_Agent开发指南.md`、论文框架、CBDB 下载脚本 | `00_PROJECT_HANDOFF.md` §B.2 |
| **v2.3** | 2026-05-27 | 首版完整技术文档 | 文档体系建立 | 技术文档 44.7 KB、论文 v0.1/v0.2、PDF 1.8 MB | `00_PROJECT_HANDOFF.md` §B.3 |
| **v2.4** | 2026-05-28 | 单周期北宋 PSI 基线验证 | "能做" | 四朝 PSI + IPW + SikuBERT NLP；`P3_里程碑报告_v2.4.md` | `00_PROJECT_HANDOFF.md` §B.4, `P3_里程碑报告_v2.4.md` |
| **v2.5** | 2026-05-29 | 全历史覆盖 + 云端 NLP | "解决规模问题" | 96 窗十年级真实 MiniMax API；五朝 30,518 条；`P5_里程碑报告_v2.5.md` | `00_PROJECT_HANDOFF.md` §B.5, `P5_里程碑报告_v2.5.md` |
| **v2.6** | 2026-05-30 | 统计敏感性分析 | "解决可信度问题" | Bootstrap 95% CI、Cohen's d=7.35、Adjusted R²=0.36；`P6_里程碑报告_v2.6.md` | `00_PROJECT_HANDOFF.md` §B.6, `P6_里程碑报告_v2.6.md` |
| **v3.0 Alpha** | 2026-05-30 | TKG + MCP+A2A + 四诊合参 2.0 | "解决预测深度问题" | TKG MRR=0.3631、8 Agent Card、四诊一致性 0.8407；`P7_里程碑报告_v3.0.md` | `00_PROJECT_HANDOFF.md` §B.7, `P7_里程碑报告_v3.0.md` |
| **v3.0 收尾** | 2026-05-31 | CDLI 跨文明 + 论文冲刺 | 跨文明验证从 0 到 1 | CDLI API 100 条、论文 v2.0→v3.0（91K 字）、4 个验证脚本 | `00_PROJECT_HANDOFF.md` §B.8, `v3.0_项目交付总结.md` |
| **v4.x ULTIMATE** | 2026-06-03 上午 | 重做：统一公式 + 288 次真实 LLM | 公式混乱 + 聚合级统计谬误 | 个体级 n=30,518、8 维度独立验证、15 张 Figure、reproduce.py、4 篇 Nature 变体 | `00_PROJECT_HANDOFF.md` §B.9 |
| **v5.0 NOBEL** | 2026-06-03 下午 | 政治 PSI + 物理理论 | 跨政治制度验证 + 物理机制 | 6 域跨 3 百万观测、政治 PSI 91% 召回、Hurst H=0.958、PageRank 震源 | `00_PROJECT_HANDOFF.md` §B.10 |
| **v6.0 NOBEL++** | 2026-06-03 晚 | 因果识别 + 实时 + 范式 | 修复 12 个审稿问题 | HAC/PSM 严格统计、真正未来盲测、金十 Dashboard、Nature 投稿稿 + 12 节 SI | `00_PROJECT_HANDOFF.md` §B.11 |
| **v6.1** | 2026-06-04 上午 | H-β fBm 修正 + 物理降级 + PNAS | 物理理论错误（"超临界"不符合任何标准分形过程） | fBm H=1.5662、β=4.0、PNAS 6 页稿、央行 MPA 白皮书 | `v6.2_README.md` §4, §9.1 |
| **v6.2** | 2026-06-04 上午 | CDLI 完整 catalog + 4 层因果推断 | 跨文明样本量不足 | CDLI 331,173 条（从 100 条→33 万条，3,300 倍）、7/8=87.5% 验证正确、MOU 模板 | `v6.2_README.md` §9.3 |

**关键转折点**：
1. **v2.4→v2.5**：从"单周期北宋"到"五朝全历史覆盖"，从本地 SikuBERT 到云端 MiniMax API（轻资产转型）。
2. **v3.0→v4.x**：马老师审稿指出 12 个问题（公式混乱、Table 矛盾、事件泄漏），项目从"框架探索"彻底重做为"严格统计"，具备 Nature 投稿资格。
3. **v5.0→v6.0**：从"相关性"升级为"因果识别"（HAC + PSM + 真正盲测），从"历史回顾"升级为"实时 Dashboard"。
4. **v6.0→v6.1**：用户的 CZ-1 警示拯救了 5 年研究可信度——H=0.958/β=1.66 被修正为 fBm H=1.57/β=4.0，主文移除"超临界"和"比 Ising 更强"表述。

---

### 3. 核心数据指标

#### 3.1 6–7 域验证结果汇总

| 域 | 数据源 | 时期 | 规模 | 召回率 | 领先时间 | 来源 |
|----|--------|------|------|--------|---------|------|
| **中华历史** | CBDB n=30,518 A/B 级 | -500~1900 CE | 5 朝 | 6/6 = **100%** | 30–60 年 | `00_PROJECT_HANDOFF.md` §E.3, `04_PROJECT_DATA_RECORD.md` |
| **美索不达米亚** | CDLI Uruk III/IV | ~-3200 BCE | 100 条（v3–v4）/ **331,173 条（v6.2）** | 1/1=100%（v4）/ **7/8=87.5%（v6.2）** | N/A | `00_PROJECT_HANDOFF.md` §E.3, `v6.2_README.md` §9.3 |
| **古罗马** | LLM 评估 14 期 | -509~476 CE | 14 个关键节点 | 4/4 = **100%** | 10–100 年 | `00_PROJECT_HANDOFF.md` §E.3, `04_PROJECT_DATA_RECORD.md` §4.5 |
| **中国金融** | 腾讯/新浪 4 指数 | 2018–2026 | 6,048 bars | 7/7 = **100%** | 0–34 天 | `00_PROJECT_HANDOFF.md` §E.3 |
| **全球金融** | yfinance 20 资产 | 1927–2026 | 187,073 bars | 241/295 = **81.7%** | 35.6 天 | `00_PROJECT_HANDOFF.md` §E.3 |
| **全球政治** | Wikidata SPARQL | -218~2022 | 1,728 战争+革命 | 30/33 = **91%** | ±5 年 | `00_PROJECT_HANDOFF.md` §E.3 |
| **宏观（FRED）** | 11 宏观指标 | 1919–2026 | - | HOUST 100%, UMCSENT 70% | 6.78 月 / 5.14 月 | `04_PROJECT_DATA_RECORD.md` §4.7 |
| **合计** | - | 跨 **5,500 年** | ~3.5 百万观测 | **~85%** | - | `v6.2_README.md` |

#### 3.2 关键数字速查

| 指标 | 数值 | 含义 | 来源 |
|------|------|------|------|
| 五朝 PSI 范围 | 0.3804 ~ 0.6250 | 盛世 > 危机 | `04_PROJECT_DATA_RECORD.md` §Part 7 |
| 盛世 vs 危机 PSI 差 | **51.5%** | 结构性差异 | `00_PROJECT_HANDOFF.md` §E.1, `04_PROJECT_DATA_RECORD.md` |
| Cohen's d（个体级 IPW） | **0.533** | 大效应（v4 重做后） | `00_PROJECT_HANDOFF.md` §E.2, `04_PROJECT_DATA_RECORD.md` §3.4 |
| Cohen's d（v2.6 朝代级） | **7.35** | 大效应（但为聚合级，有生态学谬误） | `P6_里程碑报告_v2.6.md` §2.1 |
| Walk-Forward 相关系数 | **0.9643** | 时序预测准确率 | `04_PROJECT_DATA_RECORD.md` §3.4 |
| 重测信度 r | **0.9617** | 一致性 | `01_PROJECT_MASTER_RECORD.md` §2 |
| 贝叶斯 P(明>南) | **99.78%** | 后验极强 | `00_PROJECT_HANDOFF.md` §E.2, `04_PROJECT_DATA_RECORD.md` §3.5 |
| HAC t 统计量 | **>4**（唐/北宋后/南宋） | 修正时间自相关后仍显著 | `00_PROJECT_HANDOFF.md` §E.6, `04_PROJECT_DATA_RECORD.md` §5.1 |
| PSM ATE | **-1.05** (p<<0.01) | 因果识别：危机朝代 PSI 系统性低 1.05 个单位 | `00_PROJECT_HANDOFF.md` §E.6, `04_PROJECT_DATA_RECORD.md` §5.2 |
| LSTM 准确率 | **78.67%** / F1=0.7621 | 现代 ML 对照 | `04_PROJECT_DATA_RECORD.md` §5.5 |
| VIX 领先股市 | **17 天** (r=-0.235) | 颠覆"波动率=已实现" | `00_PROJECT_HANDOFF.md` §E.7 |
| 黄金滞后 | **1 天** (r=+0.346) | 颠覆"黄金避险" | `00_PROJECT_HANDOFF.md` §E.7 |
| 政治 PSI 召回 | **91%** (30/33) | 跨制度跨文化跨千年 | `00_PROJECT_HANDOFF.md` §E.7 |
| PageRank 震源 | **DE.DAX 0.0698** | 欧洲三强（DE/FR/UK）不是美国 | `00_PROJECT_HANDOFF.md` §E.5 |
| Hurst H（v6.0） | **0.958**（4 市场平均） | 超临界（后被修正） | `00_PROJECT_HANDOFF.md` §E.4 |
| Hurst H（v6.1 修正） | **fBm H=1.5662**, β=4.0 | 经典分形市场假说 | `v6.2_README.md` §4, §9.1 |
| 真正盲测 | 训练 2020-2023 → 测试 2024-2025 | PSI 0.31→0.07 正确预测压力升高 | `00_PROJECT_HANDOFF.md` §E.6, `04_PROJECT_DATA_RECORD.md` §5.4 |

#### 3.3 8 个免费数据源

| 数据源 | URL | 规模 | 用途 | 来源 |
|--------|-----|------|------|------|
| **CBDB** | cbdb.fas.harvard.edu | 658,339 总，30,518 A/B 级 | 中华历史主数据 | `00_PROJECT_HANDOFF.md` §D.1 |
| **CDLI** | cdli.ucla.edu / github.com/cdli-gh/data | 100 条（公共 API）/ **331,173 条（v6.2 GitHub）** | 美索不达米亚跨文明 | `00_PROJECT_HANDOFF.md` §D.1, `v6.2_README.md` |
| **Wikidata SPARQL** | query.wikidata.org | 1,728 战争+革命 | 全球政治 PSI | `00_PROJECT_HANDOFF.md` §D.1 |
| **yfinance** | finance.yahoo.com | 187,073 bars | 全球 20 资产金融 | `00_PROJECT_HANDOFF.md` §D.1 |
| **腾讯/新浪** | web.ifzq.gtimg.cn | 6,048 bars | 中国金融 | `00_PROJECT_HANDOFF.md` §D.1 |
| **FRED** | fred.stlouisfed.org | 11 宏观指标 | 宏观 PSI | `00_PROJECT_HANDOFF.md` §D.1 |
| **OWID COVID** | github.com/owid/covid-19-data | 429,436 行 | COVID PSI | `00_PROJECT_HANDOFF.md` §D.1 |
| **金十 MCP** | mcp.jin10.com/mcp | 1,055 快讯 | 实时监控 | `00_PROJECT_HANDOFF.md` §D.1 |
| **LLM 服务** | api.minimaxi.com/v1 | 288+ 次真实 API 调用 | 语义分析 | `00_PROJECT_HANDOFF.md` §D.1 |

---

### 4. 项目决策日志

> 共 12 条关键决策，按时间倒序排列。来源：`00_PROJECT_HANDOFF.md` §Part I、`03_计划书与决策日志.md` §第二部分。

| # | 日期 | 决策 | 理由 | 影响 | 来源 |
|---|------|------|------|------|------|
| 1 | 2026-06-03 晚 | v6.0 NOBEL ULTIMATE 作为最终交付 | 修复 12 审稿问题 + 盲测通过 + Nature 就绪 | 可投 Nature | `00_PROJECT_HANDOFF.md` §I.1 |
| 2 | 2026-06-03 下午 | v5.0 引入政治 PSI + 物理 | 跨政治制度验证 + 物理机制 | 6 域 4200 年范式 | `00_PROJECT_HANDOFF.md` §I.2 |
| 3 | 2026-06-03 上午 | v4.x 重做（公式统一 + 288 次真实 LLM） | v3.0 公式混乱 + 聚合级统计谬误 | 严格统计 | `00_PROJECT_HANDOFF.md` §I.3 |
| 4 | 2026-05-31 | v3.0 接受 12 个审稿问题为方向 | 诚实记录 + 重写优于修补 | v4.x 8 维度验证 | `00_PROJECT_HANDOFF.md` §I.4 |
| 5 | 2026-05-30 | v3.0 引入 TKG + MCP+A2A + 四诊 | 用户要 AI 自主推进 + 协议标准化 | 从指标到预测 | `00_PROJECT_HANDOFF.md` §I.5 |
| 6 | 2026-05-29 | v2.5 切到云端 MiniMax API | 避免环境依赖 + 自动降级 | 轻资产可复现 | `00_PROJECT_HANDOFF.md` §I.6 |
| 7 | 2026-05-28 | 选择 CDLI 而非 Perseus 先做 | 公共 API 可访问 + 学术独特性 | 跨文明从 0 到 1 | `00_PROJECT_HANDOFF.md` §I.7 |
| 8 | 2026-05-28 | v2.4 先做北宋（不是全朝代） | 时间适中 + 明确危机节点 | 渐进式验证 | `00_PROJECT_HANDOFF.md` §I.8 |
| 9 | 2026-05-28 | PSI 权重 0.25/0.25/0.5（SDT 论证） | 客观 > 主观 | 理论基石 | `00_PROJECT_HANDOFF.md` §I.9 |
| 10 | 2026-05-27 | 引入 IPW 校正 CBDB 精英偏差 | 70% 官员偏向 | 方法论贡献 | `00_PROJECT_HANDOFF.md` §I.10 |
| 11 | 2026-05-27 | 借鉴中医"四诊合参"做交叉验证 | 单一信号易被质疑 | 多模态架构 | `00_PROJECT_HANDOFF.md` §I.11 |
| 12 | 2026-05-27 之前 | 整合 SDT + PSI + 四诊合参 | 三者缺一不可 | 理论框架完整 | `00_PROJECT_HANDOFF.md` §I.12 |

**关闭的决策/修正**：
- **v6.0 "超临界"物理理论被关闭**：v6.1.1 发现 H=0.958、β=1.66 "不符合任何标准分形过程"，修正为 fBm H=1.57、β=4.0，主文移除"超临界"和"比 Ising 更强"表述，移至 SI 作为"启发性类比"。来源：`v6.2_README.md` §4, §9.2。
- **12 维度研究 8 大洞察中关闭 1 项**："H-β → 新普适类"因 H-β 修正而关闭。来源：`v6.2_README.md` §9.5。

#### 方法论教训（8 条）

来源：`00_PROJECT_HANDOFF.md` §Part J、`03_计划书与决策日志.md` §第四部分。

1. **公式混乱是审稿杀手**：v3.0 有 4-6 种公式 → Table 矛盾。**经验**：每个项目有"唯一真相源"——一个公式、一个权重、一个阈值。
2. **聚合级别统计有生态学谬误**：v3.0 Cohen's d=7.35 是朝代级聚合，个体级只有 0.43。**经验**：报告效应量时必须说明聚合级别。
3. **盲测合规是不可妥协的**：v3.0 12 个问题中事件泄漏最严重——隐藏期事件泄漏，移除后纯时序统计仍有效。**经验**：训练期/测试期严格分隔。
4. **长短期数据需要分层结论**：短期 20-60 年相符率 70-96.6%，长期 300+ 年 21.4-50.6%。**经验**：按时间窗口/数据稀疏度分层报告。
5. **阴性结果有独立价值**：气候对照 r=0.02（独立）——PSI 不被气候混杂，反向证明其独立性。**经验**：不追求全阳性。
6. **跨学科合作要尊重对方领域**：马利军教授是语义心理学，PSI 必须用其理论语言描述。**经验**：跨学科论文用对方领域术语。
7. **版本压缩包要按时归档**：8 个 .zip 文件每次阶段性产出都打一个。**经验**：阶段末必归档。
8. **Project memory 三件套**：PROJECT_LOG.md + 06_Agent开发指南.md + 主档案 = 接手 Agent 完整心智模型。

---

### 5. 当前状态与待办

#### 5.1 已完成 ✅

来源：`00_PROJECT_HANDOFF.md` §K.1、`01_PROJECT_MASTER_RECORD.md` §8.1、`v6.2_README.md`。

- 6–7 域跨 5,500 年验证，召回率 >85%
- 7 个反直觉发现
- 物理理论统一（v6.1.1 修正为经典分形市场 fBm + EMH）
- 因果识别（HAC + PSM + 4 层因果推断 + 真正盲测）
- 实时数据接入（金十 MCP Dashboard）
- Nature/PNAS 投稿稿（4 页精炼 + 15 节 SI / PNAS 6 页）
- 政策/监管/投资三层应用框架（央行 MPA 白皮书 + MOU 模板）
- CDLI 完整 catalog 331,173 条（v6.2）
- 项目通盘档案建立（168–194 个文件 / 5.8–20.8 MB）

#### 5.2 进行中 / 待开始

来源：`00_PROJECT_HANDOFF.md` §K.2、`03_计划书与决策日志.md` §第五部分、`v6.2_README.md`。

| 优先级 | 任务 | 前置条件 | 负责人 |
|--------|------|---------|--------|
| **P0（立即）** | 用户决策 Nature/PNAS 投稿版本 | 用户决策 | Mavis |
| **P0（立即）** | 央行 MPA 对接（3-6 月政策窗口） | 投稿策略确定 | Mavis |
| **P1（本月）** | 跨学科合作接洽（央行/IMF/物理学家） | 投稿策略确定 | Mavis |
| **P1（本月）** | 真实 UPSI Dashboard 部署（cron + 金十每日） | cron 任务 | Mavis |
| **P1（本月）** | Nature/PNAS 投稿 Cover Letter + SI 完整性 | 版本确定 | Mavis |
| **P2（下月）** | CPM-KB 扩展（10→1,000 条，TSI 半自动框架） | TSI 框架 | Mavis |
| **P2（下月）** | CEGRL-TKGR 集成（因果 + TKG 融合） | 算法就绪 | Mavis |
| **P2（下月）** | 贝叶斯层次推断（PyMC） | 样本量 n≥31 | Mavis |
| **P2（下月）** | 古罗马 Perseus 接入 | CDLI Phase 2A 完成 | Mavis |
| **P3（季度）** | TKG 真实数据训练（ICEWS） | tkg_v3/ 代码就绪 | 待定 |
| **P3（季度）** | 四诊合参"闻"真实数据（REACHES 气候） | REACHES 数据接入 | 待定 |
| **P3（季度）** | 多尺度 PSI 验证（年/十年/世纪级） | - | 待定 |
| **P3（季度）** | Monte Carlo 1000+ 模拟 | - | 待定 |
| **P4（年度）** | 跨学科教科书 | - | 待定 |
| **P4（年度）** | Seshat 互操作性 | - | 待定 |
| **P4（年度）** | 政策实施报告 | - | 待定 |

#### 5.3 长期路线图（6 年）

来源：`00_PROJECT_HANDOFF.md` §K.3、`03_计划书与决策日志.md` §1.1。

| 年份 | 目标 |
|------|------|
| **2026** | Nature/PNAS 投稿 + 5 朝覆盖完成 + 央行 MPA 试点 |
| **2027** | 跨文明扩展（古巴比伦、古罗马深度）、样本量 n→150-300 |
| **2028** | 贝叶斯层次 + IPW 跨数据源 |
| **2029** | 实时 PSI 监控 + 政策实施 |
| **2030+** | Seshat 互操作 + 跨平台比较研究 + 跨学科教科书 |

---

### 6. 关键发现摘要

#### 6.1 7 大反直觉发现

来源：`00_PROJECT_HANDOFF.md` §E.7、`01_PROJECT_MASTER_RECORD.md` §4.4、`v6.2_README.md` §3。

| # | 发现 | 颠覆性 | 关键数字 | 来源 |
|---|------|--------|---------|------|
| 1 | **VIX 领先股市 17 天** | 颠覆"波动率=已实现" | r=-0.235, 95% CI [-0.30, -0.17] | `00_PROJECT_HANDOFF.md` §E.7 |
| 2 | **黄金滞后 1 天** | 颠覆"黄金避险" | r=+0.346, 95% CI [+0.30, +0.39] | `00_PROJECT_HANDOFF.md` §E.7 |
| 3 | **全球 PSI 同步无因果** | 推翻"美国先跌欧洲跟跌" | 13 市场 lag=0 r>0.5 | `00_PROJECT_HANDOFF.md` §E.7 |
| 4 | **PSI 是同步器非预测器** | 框架定位 | 不是预测未来，是量化当前系统压力状态 | `00_PROJECT_HANDOFF.md` §E.7 |
| 5 | **物理过程: fBm (H=1.57) + 收益率 EMH (H=0.45)** | v6.0 曾误称"超临界"，v6.1.1 修正为经典分形 | 价格水平有长记忆，收益率不可预测 | `v6.2_README.md` §3, §4 |
| 6 | **政治 PSI 91% 召回** | 跨制度跨文化跨千年 | 30/33 重大历史事件 PSI<0 同步 | `00_PROJECT_HANDOFF.md` §E.7 |
| 7 | **欧洲三强是震源**（DE/FR/UK） | 不是美国 | PageRank 0.064-0.070，2000s/2010s/2020s 均居前 | `00_PROJECT_HANDOFF.md` §E.5 |

#### 6.2 物理理论结论（v6.1.1 修正版）

来源：`v6.2_README.md` §4, §9.1, §9.2。

- **v6.0 错误**：H=0.958, β=1.66 被宣称为"超临界"、"比 Ising 临界态更强"——**不符合任何标准分形过程**。
- **v6.1.1 修正**：
  - 价格水平是 **fBm 过程**（fractional Brownian motion）：H=1.5662, β=4.0000——完全符合 fBm 理论（偏差仅 3.2%）。
  - 收益率是 **EMH 随机游走**：H=0.45——接近 0.5，不可预测。
  - 方法：DFA + Whittle 估计（替代 R/S + FFT）。
- **哲学结论**："同步器非预测器"——价格水平有长记忆（可描述当前状态），收益率不可预测（无法预测未来）。
- **降级声明**：物理指标移至 SI，标注为"启发性类比"；主文保留 7 大反直觉发现。

#### 6.3 因果识别结果

来源：`00_PROJECT_HANDOFF.md` §E.6、`04_PROJECT_DATA_RECORD.md` §5、`v6.2_README.md` §6。

| 方法 | 结果 | 意义 |
|------|------|------|
| **Newey-West HAC** | t_HAC > 4（唐/北宋后/南宋衰退期仍显著） | 修正时间自相关后关键发现仍成立 |
| **PSM 倾向得分匹配** | ATE on PSI = -1.05 (t=-17.52, p<<0.01) | 危机朝代 PSI 系统性低 1.05 个单位——满足 2021 Nobel 因果识别标准 |
| **4 层因果推断（v6.1）** | L1 SDID τ=-0.050; L2 FCI 6 条跨域边; L3 置换检验 p=0.0054 (n=7); L4 盲测通过 | 从准实验到完整因果架构 |
| **真正未来盲测** | 训练 2020-2023 → 测试 2024-2025：PSI 0.31→0.07 正确预测压力升高 | 与 2024 雪球崩吻合，泛化能力验证 |
| **ROC + 阈值优化** | 中国金融 AUC=0.59 最佳；三域最佳阈值不同（金融 0.0/-1.5，政治 +1.0） | 阈值按域校准，不通用 |

---

### 7. 文件清单概览

#### 7.1 各版本交付包内容

来源：`02_完整文件清单.md` §6-§9、`00_PROJECT_HANDOFF.md` §F.3-F.6、`v6.2_README.md` §📦 文件交付。

| 版本 | 文件/目录 | 大小 | 核心内容 | 来源 |
|------|-----------|------|---------|------|
| **v2.4 完整交付包** | `Civilization-Oracle_v2.4_完整交付包/` | - | 01_论文/ 02_演示/ 03_技术报告/ 04_规格与架构/ 05_迭代升级过程/ 06_核心代码/ 07_工具模块/ 08_测试/ 09_配置/ 10_数据/ | `02_完整文件清单.md` §5.13 |
| **v4.x** | `v4/` 目录 | 68 个文件 | formula.py（唯一公式）、reproduce.py（一键复现）、8 维度验证 13 个脚本、15 张 Figure、910 KB HTML 报告、4 篇 Nature 变体 | `02_完整文件清单.md` §6, `00_PROJECT_HANDOFF.md` §F.3 |
| **v5.0** | `v5/` 目录 | 18 个文件 | compute_political_psi.py（91% 召回）、physics_theory.py（Hurst/β）、psi_network.py（PageRank）、dashboard.html | `02_完整文件清单.md` §7, `00_PROJECT_HANDOFF.md` §F.4 |
| **v6.0** | `v6/` 目录 | 23 个文件 | NATURE_LETTER_FINAL.md（4 页精炼）、NATURE_SI.md（12 节 SI）、hac_v4_fix.py、psm_v6.py、blind_test_v6.py、dashboard_v6.py | `02_完整文件清单.md` §8, `00_PROJECT_HANDOFF.md` §F.5 |
| **v6.1/6.2** | `v6.1/` 目录 | 24 个文件 | PNAS_MANUSCRIPT.md、NATURE_SI_V61.md（15 节）、PBOC_MPA_WHITE_PAPER.md、PBOC_MPA_MOU.md、CDLI_APPLICATION.md、h_beta_recheck.py、causal_4_layer.py、cdli_psi_analysis.py、cdli_real_year_psi.py | `v6.2_README.md` §📦 文件交付 |
| **压缩包归档** | `v6_2_NOBEL_ULTIMATE.zip` | **20.8 MB / 194 files** | v4/(110) + v5/(15) + v6/(43) + v6.1/(24) | `v6.2_README.md` |

**8 个 .zip 归档历史**：

| 文件 | 大小 | 阶段 | 来源 |
|------|------|------|------|
| v4x_ULTIMATE_FINAL.zip | 2.1 MB | v4.0 | `02_完整文件清单.md` §9 |
| v4x_ULTIMATE_FINAL_v2.zip | 3.2 MB | v4.1 | `02_完整文件清单.md` §9 |
| v4x_NOBEL_FINAL.zip | 5.3 MB | v4.x | `02_完整文件清单.md` §9 |
| v5_NOBEL_FINAL.zip | 5.6 MB | v5.0 | `02_完整文件清单.md` §9 |
| v6_NOBEL_PLUS.zip | 5.6 MB | v6.0 初 | `02_完整文件清单.md` §9 |
| v6_NOBEL_PLUS_FINAL.zip | 5.8 MB | v6.0 修 | `02_完整文件清单.md` §9 |
| v6_NOBEL_ULTIMATE.zip | 5.8 MB | v6.0 终 | `02_完整文件清单.md` §9 |
| v6_NOBEL_ULTIMATE_FINAL.zip | 5.8 MB | v6.0 终极 | `02_完整文件清单.md` §9 |
| **v6_2_NOBEL_ULTIMATE.zip** | **20.8 MB** | **v6.2 终极** | `v6.2_README.md` |

#### 7.2 核心文件位置速查

来源：`00_PROJECT_HANDOFF.md` §Part L（必读清单）、`02_完整文件清单.md`。

| 我想了解…… | 文件位置 |
|-------------|---------|
| 项目一句话定义 | `00_PROJECT_MASTER/00_PROJECT_HANDOFF.md` §A.1 |
| 完整时间线 | `00_PROJECT_MASTER/00_PROJECT_HANDOFF.md` §Part B |
| 主档案（30 秒读懂） | `00_PROJECT_MASTER/01_PROJECT_MASTER_RECORD.md` |
| 计划书 + 决策日志 | `00_PROJECT_MASTER/03_计划书与决策日志.md` |
| 全部数据真实值 | `00_PROJECT_MASTER/04_PROJECT_DATA_RECORD.md` |
| 项目持续日志 | `PROJECT_LOG.md` |
| v6.2 终极 README | `v6.2_README.md` |
| v4 入口 + 一键复现 | `v4/README.md`、`v4/reproduce.py` |
| v5 总表 | `v5/V5_SUMMARY.md` |
| v6 入口 | `v6/README.md` |
| Nature 投稿稿（4 页精炼） | `v6/NATURE_LETTER_FINAL.md` |
| PNAS 投稿稿（6 页，v6.1） | `v6.1/PNAS_MANUSCRIPT.md` |
| Nature SI（15 节，v6.1） | `v6.1/NATURE_SI_V61.md` |
| 范式转移论文 | `v6/UPSI_PAPER.md` / `v6.1/UPSI_PAPER.md` |
| 唯一公式实现 | `v4/formula.py` |
| 五朝 PSI 数据 | `output/psi_唐朝.json`、`output/psi_明朝.json`、`output/psi_北宋前期.json`、`output/psi_北宋后期.json`、`output/psi_南宋.json` |
| 96 窗十年级 PSI | `output/decade_psi_all_api.json` |
| CDLI 跨文明分析 | `output/cdli_analysis.json`（v3）/ `v6.1/data/cdli_psi_v61.json`（v6.2） |
| 8 维度验证数据 | `v4/data/statistics_v4.json`、`v4/data/bayesian_v4_results.json` 等 13 个 JSON |
| 政治 PSI | `v5/data/political_psi_v5.json` |
| 物理理论 | `v5/data/physics_theory_v5.json`（v6.0）/ `v6.1/data/hbeta_recheck_v61.json`（v6.1 修正） |
| 因果识别（HAC/PSM/盲测） | `v6/data/hac_v6.json`、`v6/data/psm_v6.json`、`v6/data/blind_test_v6.json` |
| 金十实时数据 | `v6/data/daily_jin10.jsonl` |
| 论文主稿（v3.0） | `论文草稿_Civilization-Oracle_v3.0.md`（91.6 KB，~20,000 词） |
| 马老师审稿 Checklist | `马老师审稿Checklist_v3.0.md` |
| 验证报告 | `验证报告.md` |
| Agent 协作指南 | `06_Agent开发指南.md` |
| 决策日志（JSON） | `decision.json` |

---

*报告编制: 研究员_维度01 | 2026-06-04*
*信息来源: 14 份项目元信息与管理档案完整阅读*
