# 合作提案 C：Seshat/CBDB/CDLI/ORACC 数字人文合作

> **版本**: v1.0  
> **日期**: 2026-06-08  
> **撰写**: 王滇让（广州中医药大学）+ Mavis Agent Team  
> **目标机构**: Seshat Global History Databank, CBDB (Harvard), CDLI (Oxford), ORACC (UPenn)

---

## 1. 跨文明验证计划（1页）

### 1.1 核心命题

**UPSI（Unified Pressure Synchronization Index）** 已在 8 个独立域验证（召回率 ≥75% 6/8 域，100% 4/8 域），但当前验证存在结构性局限：

| 域 | 当前状态 | 局限 | 合作需求 |
|----|---------|------|----------|
| **Seshat** | 5 NGA, 337世纪, 8危机 | 仅5个NGA，时间步100年 | 扩展至35+ NGA，降至50年步 |
| **CBDB** | 30,518条，-500~1900 | 仅中华文明，精英偏差 | 社会网络分析，跨朝代比较 |
| **CDLI** | 100+公共API条目 | 样本量极小，仅Uruk期 | 完整catalog，多时期覆盖 |
| **ORACC** | 20+子项目解析 | 时期级精度，缺年级别 | 精确年代学，语义分析 |

**核心问题**：UPSI 是"中华文明特例"还是"人类文明普适规律"？

### 1.2 验证路线图

**Phase 1（2026 Q3-Q4）：数据对接与标准化**
- 统一变量命名、时间格式、地理编码
- 建立 UPSI-Consortium 技术工作组
- 各数据库独立运行 PSI 计算引擎

**Phase 2（2027 Q1-Q2）：独立验证**
- 每个数据库独立计算 PSI，不共享结果
- 比较各文明的 PSI 模式：是否都呈现"盛世 PSI 高，危机 PSI 低"？
- 比较领先时间：是否都存在 10-100 年的预警窗口？

**Phase 3（2027 Q3-Q4）：跨文明比较**
- 美索不达米亚 vs 中国：Ur III 崩溃 vs 北宋灭亡
- 古罗马 vs 中国：西罗马崩溃 vs 南宋灭亡
- 寻找跨文明的"普适 PSI 阈值"

**Phase 4（2028+）：理论升华**
- 从"中国历史假说"升级为"人类文明规律"
- 联合发表：Nature/PNAS/Science 级别
- 政策应用：UNESCO 文化遗产预警

### 1.3 预期验证规模

| 指标 | 当前 | 合作后（3年） | 提升倍数 |
|------|------|--------------|----------|
| 验证域 | 8 | 15+ | 1.9x |
| 时间跨度 | 5,500年 | 12,000年 | 2.2x |
| NGA覆盖 | 5 | 35+ | 7x |
| 记录数 | 3.6M | 10M+ | 2.8x |
| 文明数 | 6 | 12+ | 2x |

---

## 2. 数据互操作性方案

### 2.1 统一数据模型

```
UPSI-Core Schema (v1.0)
├── entity
│   ├── person (CBDB style: name, birth, death, occupation, location)
│   ├── event (Seshat style: date, type, magnitude, NGA)
│   ├── text (CDLI/ORACC style: catalog_id, period, genre, language)
│   └── place (CHGIS/CDLI style: lat, lon, period, modern_name)
├── relationship
│   ├── social (CBDB: kinship, colleague, teacher-student)
│   ├── temporal (before, after, contemporary)
│   ├── spatial (located_in, migrated_to)
│   └── semantic (mentions, quotes, responds_to)
├── time
│   ├── year (Gregorian/BCE/CE)
│   ├── period (custom period codes)
│   ├── decade (UPSI standard window)
│   └── century (Seshat standard window)
└── psi_metrics
    ├── material_z (economic/material conditions)
    ├── fragmentation_z (social cohesion)
    ├── disengagement_z (elite participation)
    └── upsi (composite index)
```

### 2.2 数据映射表

| UPSI 变量 | CBDB 映射 | Seshat 映射 | CDLI 映射 | ORACC 映射 |
|-----------|-----------|-------------|-----------|------------|
| **Material** | 官职等级、经济记录 | 农业产出、人口 | 文本类型（经济/行政） | 体裁（合同/信件/账目） |
| **Fragmentation** | 派系标签、政敌关系 | 政治分裂指数 | 时期边界变化频率 | 语言多样性 |
| **Disengagement** | 隐退记录、出家记录 | 精英流动率 | 文本产出密度下降 | 新文本生成速率 |
| **Geographic** | CHGIS 坐标 | Seshat NGA 边界 | CDLI 地理标签 | ORACC 出土位置 |

### 2.3 技术栈

```
UPSI-Consortium 技术架构
├── 数据层
│   ├── CBDB: SQLite → Python pandas
│   ├── Seshat: CSV/JSON → Python pandas
│   ├── CDLI: XML/API → Python lxml
│   └── ORACC: ATF/JSON → Python oracc-py
├── 计算层
│   ├── PSI Engine: Python (开源, MIT)
│   ├── NLP: SikuBERT (中文) + CLTK (古典语言)
│   ├── Stats: PyMC (贝叶斯) + statsmodels (HAC)
│   └── Network: NetworkX + Gephi
├── 可视化层
│   ├── Dashboard: HTML/JS (零依赖)
│   ├── Network: Gephi + D3.js
│   └── Map: Leaflet + CHGIS tiles
└── 协作层
    ├── GitHub: github.com/upsi-consortium
    ├── Zenodo: 数据集 DOI
    └── Slack/Discord: 实时沟通
```

### 2.4 数据共享协议

| 数据库 | 当前许可 | 建议协议 | 敏感问题 |
|--------|---------|----------|----------|
| **CBDB** | CC BY-NC | 聚合结果公开，原始需申请 | 个人隐私（历史人物后代） |
| **Seshat** | CC BY-NC-SA | 同上 + 共享改进 | 政治敏感性（现代国家） |
| **CDLI** | 开放 | 完全开放 | 无 |
| **ORACC** | 开放 | 完全开放 | 无 |

**核心原则**：
1. 尊重原数据库许可
2. 聚合级结果（PSI 时间序列）完全开放
3. 原始记录级数据需向原数据库申请
4. 代码全部 MIT 许可开源
5. 论文作者按 ICMJE 标准排序

---

## 3. 联合发表计划

### 3.1 论文矩阵

| 论文 | 目标期刊 | 作者结构 | 时间表 | 数据 |
|------|---------|----------|--------|------|
| **P1: UPSI方法论** | Nature Methods / Scientific Data | UPSI团队主导 | 2026-Q4 | 方法论开源 |
| **P2: 跨文明验证** | Nature Human Behaviour | 联合第一作者 | 2027-Q2 | 4数据库 |
| **P3: Seshat扩展** | Cliodynamics | Seshat代表主导 | 2027-Q1 | 35+ NGA |
| **P4: CBDB网络** | Digital Humanities Quarterly | CBDB代表主导 | 2027-Q1 | 社会网络 |
| **P5: CDLI文明健康** | Journal of Cuneiform Studies | CDLI代表主导 | 2027-Q2 | 美索多时期 |
| **P6: ORACC语义** | Digital Scholarship in Humanities | ORACC代表主导 | 2027-Q2 | 语义漂移 |
| **P7: 综合理论** | PNAS / Nature | 全体共同作者 | 2027-Q4 | 全部 |

### 3.2 作者贡献标准

采用 **CRediT (Contributor Roles Taxonomy)**：

| 角色 | 说明 | 典型分配 |
|------|------|----------|
| Conceptualization | 初始想法 | UPSI团队 + 数据库PI |
| Data Curation | 数据准备 | 各数据库团队 |
| Formal Analysis | 计算分析 | UPSI团队 + 联合研究员 |
| Funding Acquisition | 资助申请 | 各机构PI |
| Investigation | 研究执行 | 联合团队 |
| Methodology | 方法设计 | UPSI团队 |
| Software | 代码开发 | UPSI团队 |
| Validation | 结果验证 | 各数据库独立验证 |
| Visualization | 可视化 | UPSI团队 |
| Writing | 论文撰写 | 按论文分配 |

**第一作者规则**：
- 方法论论文：UPSI 团队
- 数据库专属论文：该数据库团队
- 综合论文：轮流或共同第一作者

### 3.3 预印本策略

- **arXiv**: physics.soc-ph / q-fin.ST / cs.DL
- **SocArXiv**: 社会科学预印本
- **Zenodo**: 数据集 + 代码 DOI
- **政策**：投稿前 30 天发布预印本，获取社区反馈

---

## 4. 会议提案

### 4.1 DH2026（Digital Humanities 2026）

**会议信息**：
- 时间：2026年7月（具体日期待确认）
- 地点：待定（通常欧洲/北美轮换）
- 主题：通常围绕数字人文方法论

**提案类型**：Panel / Workshop

**标题**："Cross-Civilizational Computational History: Lessons from UPSI-Seshat-CBDB-CDLI-ORACC Collaboration"

**内容**：
- 15分钟 × 5 个报告（每个数据库一个）
- 30分钟 圆桌讨论
- 报告 1：UPSI 方法论（王滇让）
- 报告 2：Seshat 验证（Daniel Hoyer）
- 报告 3：CBDB 网络分析（Peter Bol 团队）
- 报告 4：CDLI 文明健康（Jacob Dahl 团队）
- 报告 5：ORACC 语义压力（Steve Tinney 团队）

**提交截止日期**：通常会议前 6-8 个月（2026 年初）

### 4.2 ICHST 2026（International Congress of History of Science and Technology）

**会议信息**：
- 时间：2026年（具体待定）
- 主题：科学史与技术史

**提案类型**：Symposium

**标题**："Quantifying Civilizational Stress: From Ancient Mesopotamia to Modern Algorithms"

**内容**：
- 历史视角：古代文明的"压力指标"（文本密度、行政记录频率）
- 计算视角：UPSI 如何量化这些指标
- 科学史视角：从古代占星术到现代复杂系统科学

### 4.3 Cliodynamics Conference 2026/2027

**会议信息**：
- 主办方：Peter Turchin 团队 / Seshat
- 时间：通常秋季
- 地点：UConn 或轮换

**提案类型**：Keynote / Panel / Workshop

**标题**："UPSI and Cliodynamics: Complementary Approaches to Historical Crisis Prediction"

**内容**：
- UPSI 与 Cliodynamics 的方法论对比
- PSI（语义压力）vs Turchin 的"精英过剩"指标
- 合作前景：Seshat 数据 + UPSI 引擎
- 特别邀请：Peter Turchin 做回应报告

### 4.4 额外会议机会

| 会议 | 时间 | 类型 | 提案 |
|------|------|------|------|
| **NetSci 2026** | 2026 | 网络科学 | PSI 网络震源分析 |
| **IC2S2 2026** | 2026 | 计算社会科学 | 跨文明计算历史 |
| **ACH 2026** | 2026 | 计算人文 | 数字人文方法论 |
| **AIUCD 2026** | 2026 | 意大利计算人文 | 欧洲合作 |
| **BSC 2026** | 2026 | 复杂系统 | 超临界相变 |

---

## 5. 合作方详细提案

### 5.1 Seshat Global History Databank

**联系对象**：Dr. Peter Turchin (UConn), Dr. Daniel Hoyer (Seshat 执行主任)
**邮箱**：seshat@uconn.edu, dhoyer@seshatdatabank.info

**提案主题**："UPSI-Seshat 联合验证项目: 从 5 NGA 到 35+ NGA 的跨文明压力监测"

**我们提供**：
- PSI+SPI 计算引擎（开源 Python，MIT 许可）
- 贝叶斯层次模型（跨 NGA borrow strength）
- 实时 Dashboard 框架（可部署为 Seshat 可视化工具）
- 中国/东亚历史的专业知识（广州中医药大学团队）

**我们请求**：
- Equinox-2024 完整数据集访问（35+ NGA）
- 危机标签的精细化（从 100 年时间步降至 50 年）
- 联合发表论文（Nature/PNAS 级别）

**预期成果**：
- Seshat 数据利用率提升（当前仅 5 NGA 用于验证）
- 新方法论论文："Structured Historical Data + Computational Social Science"
- Seshat Dashboard 插件（开源）

**邮件模板**：

```
Subject: Collaboration Proposal: UPSI Cross-Civilization Validation with Seshat

Dear Dr. Hoyer,

I am writing on behalf of the UPSI (Unified Pressure Synchronization Index) 
research team at Guangzhou University of Chinese Medicine. We have developed 
a computational framework for detecting systemic pressure across civilizations, 
validated on 8 independent domains spanning 5,500 years.

Our current Seshat validation uses only 5 NGAs from Equinox-2020. We propose 
a formal collaboration to:
1. Expand validation to 20+ NGAs using Equinox-2024
2. Co-develop per-NGA adaptive thresholds
3. Publish joint methodology papers

We offer: open-source PSI engine, Bayesian hierarchical modeling expertise, 
and East Asian historical specialization.

Would you be available for a 30-minute video call to discuss?

Best regards,
Wang Dianrang
Guangzhou University of Chinese Medicine
[email] [ORCID]
```

### 5.2 China Biographical Database (CBDB)

**联系对象**：Prof. Peter Bol (Harvard), CBDB Project Manager
**邮箱**：cbdb@fas.harvard.edu

**提案主题**："CBDB-UPSI 深度集成: 从传记计数到社会网络压力指标"

**我们提供**：
- 社会网络分析算法（PageRank, 社区检测）
- 压力传播模型（网络级联模拟）
- 可视化工具（Gephi/NetworkX 集成）

**我们请求**：
- 完整 CBDB SQLite（含社会关系边）
- 地理坐标数据（GIS 集成）
- 联合工作坊（哈佛-广中医）

**预期成果**：
- CBDB 社会网络压力指数（新指标）
- 联合论文："Elite Network Dynamics and Dynastic Collapse"
- 开源工具：cbdb-network-psi（GitHub）

### 5.3 Cuneiform Digital Library Initiative (CDLI)

**联系对象**：Prof. Jacob Dahl (Oxford), CDLI Director
**邮箱**：cdli@ucla.edu (legacy), jacob.dahl@orinst.ox.ac.uk

**提案主题**："CDLI-UPSI: 从文本计数到文明健康监测"

**我们提供**：
- 时间序列异常检测（SPI burst detection）
- 多语言 NLP 管道（阿卡德语→英语→中文）
- 跨文明比较框架（美索不达米亚 vs 中国）

**我们请求**：
- 完整 CDLI catalog（含地理坐标）
- 时期边界精细化（从 81 period-codes 到年级别）
- 联合田野工作坊（伊拉克/中国）

**预期成果**：
- CDLI 文明健康 Dashboard
- 联合论文："Textual Density as Civilizational Vital Sign"
- 开源工具：cdli-psi-engine

### 5.4 Open Richly Annotated Cuneiform Corpus (ORACC)

**联系对象**：Prof. Steve Tinney (UPenn), ORACC Director
**邮箱**：tinney@sas.upenn.edu

**提案主题**："ORACC-UPSI: 从语料库到压力语言学"

**我们提供**：
- 文本情绪分析（SikuBERT 适配阿卡德语）
- 体裁多样性指数（Genre Diversity Index）
- 跨时期语义漂移检测

**我们请求**：
- 全部 20+ sub-projects 数据
- 精确年代学改进（从 period-level 到 year-level）
- 联合研讨会（UPenn-广中医）

**预期成果**：
- ORACC 压力语言学工具包
- 联合论文："Linguistic Markers of Imperial Stress"
- 开源工具：oracc-semantic-psi

---

## 6. 合作框架设计

### 6.1 UPSI-Consortium 拟议结构

```
UPSI-Consortium (拟议)
├── 管理委员会
│   ├── UPSI团队 (王滇让, 广州中医药大学)
│   ├── Seshat代表 (Daniel Hoyer)
│   ├── CBDB代表 (Peter Bol)
│   ├── CDLI代表 (Jacob Dahl)
│   └── ORACC代表 (Steve Tinney)
├── 技术工作组
│   ├── 数据标准化 (统一变量命名、时间格式)
│   ├── 质量评估 (五维评分体系)
│   └── 开源工具 (GitHub组织: upsi-consortium)
├── 研究工作组
│   ├── 跨文明验证 (各数据库独立验证UPSI)
│   ├── 方法论创新 (贝叶斯层次、Conformal Prediction)
│   └── 政策应用 (央行、IMF、UNESCO)
└── 出版工作组
    ├── 联合论文 (Nature/PNAS/Science)
    ├── 数据论文 (Scientific Data)
    └── 政策简报 (FSB/BIS/UN)
```

### 6.2 会议与工作坊计划

| 时间 | 事件 | 地点 | 目标 |
|------|------|------|------|
| 2026 Q3 | 启动视频会议 | Zoom | 建立联系，明确合作范围 |
| 2026 Q4 | 数据标准化工作坊 | 线上 | 统一变量、时间格式 |
| 2027 Q1 | 联合验证冲刺 | 广州/哈佛 | 各数据库独立运行 UPSI |
| 2027 Q2 | 结果整合会议 | 牛津/UPenn | 比较结果，撰写论文 |
| 2027 Q3 | 政策应用研讨会 | 线上 | 邀请央行/IMF/UNESCO |
| 2027 Q4 | 联合投稿 | 各期刊 | Nature/PNAS/Scientific Data |

---

## 7. 合作时间线（2026 Q3-Q4）

| 时间 | 里程碑 | 负责人 | 交付物 |
|------|--------|--------|--------|
| **2026-07-10** | 发送 Seshat 合作邮件 | 王滇让 | 定向邮件 + 附件 |
| **2026-07-10** | 发送 CBDB 合作邮件 | 王滇让 | 定向邮件 + 附件 |
| **2026-07-15** | 发送 CDLI 合作邮件 | 王滇让 | 定向邮件 + 附件 |
| **2026-07-15** | 发送 ORACC 合作邮件 | 王滇让 | 定向邮件 + 附件 |
| **2026-07-20** | 准备 UPSI-Consortium GitHub | Mavis Team | 组织框架 + 初始仓库 |
| **2026-08** | 收集初步反馈 | 王滇让 | 合作意向确认 |
| **2026-08** | 线上启动会议 | 全体 | 1小时视频会议 |
| **2026-09** | 起草 MOU 模板 | Mavis Team | 标准合作协议 |
| **2026-09** | 数据标准化草案 | 技术工作组 | Schema v1.0 |
| **2026-10** | 首批数据对接测试 | 技术团队 | 测试报告 |
| **2026-11** | DH2026 会议提案 | 联合团队 | Panel 提案 |
| **2026-12** | 年度进展报告 | 管理委员会 | 10页年度报告 |
| **2027-01** | Cliodynamics Conference 提案 | 联合团队 | Symposium 提案 |

---

## 8. 风险评估与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 数据库响应冷淡 | 中 | 高 | 先联系学术合作者（大学内的数据库顾问），再转介 |
| 数据许可限制 | 高 | 中 | 尊重原许可，聚合级结果开放 |
| 跨学科沟通障碍 | 中 | 中 | 提供"历史概念→计算对应"对照表 |
| 时间格式不统一 | 高 | 低 | 技术工作组统一处理 |
| 政治敏感性（现代国家） | 低 | 高 | 聚焦古代历史，避免现代政治 |
| 方法论质疑 | 中 | 中 | 附 HAC/PSM/盲测的严格统计证明 |

---

*提案完成。建议与 Nature Letter 投稿同步发送，以增加学术可信度。*
