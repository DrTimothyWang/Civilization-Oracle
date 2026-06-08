# v22 跨学科合作提案: 与Seshat/CBDB/ORACC/CDLI团队建立联系

> **版本**: v22.0 (提案稿)  
> **日期**: 2026-06-05   
> **目标**: 设计给四大历史数据库团队的合作提案，推动跨学科验证与数据共享  
> **状态**: 提案完成，可直接发送

---

## 1. 合作愿景

**核心命题**: UPSI (Unified Pressure Synchronization Index) 是一个跨文明、跨方法论的压力状态监测框架。它需要四大历史数据库的验证才能从"中国历史假说"升级为"人类文明规律"。

**互惠原则**: 我们提供计算方法论 (PSI+SPI, 贝叶斯层次模型, 实时Dashboard)，合作方提供数据与领域专业知识。

---

## 2. 四大合作方提案

---

### 2.1 Seshat Global History Databank

**联系对象**: Dr. Peter Turchin (UConn), Dr. Daniel Hoyer (Seshat执行主任)
**邮箱**: seshat@uconn.edu, dhoyer@seshatdatabank.info

**提案主题**: "UPSI-Seshat 联合验证项目: 从5 NGA到35+ NGA的跨文明压力监测"

**我们提供**:
- PSI+SPI 计算引擎 (开源Python)
- 贝叶斯层次模型 (跨NGA borrow strength)
- 实时Dashboard框架 (可部署为Seshat可视化工具)
- 中国/东亚历史的专业知识 (广州中医药大学团队)

**我们请求**:
- Equinox-2024 完整数据集访问 (35+ NGA)
- 危机标签的精细化 (从100年时间步降至50年)
- 联合发表论文 (Nature/PNAS级别)

**预期成果**:
- Seshat数据利用率提升 (当前仅5 NGA用于验证)
- 新方法论论文: "Structured Historical Data + Computational Social Science"
- Seshat Dashboard插件 (开源)

**邮件模板**:

```
Subject: Collaboration Proposal: UPSI Cross-Civilization Validation with Seshat

Dear Dr. Hoyer,

I am writing on behalf of the UPSI (Unified Pressure Synchronization Index) 
research team at Guangzhou University of Chinese Medicine. We have developed a 
computational framework for detecting systemic pressure across civilizations, 
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

---

### 2.2 China Biographical Database (CBDB)

**联系对象**: Prof. Peter Bol (Harvard), CBDB Project Manager
**邮箱**: cbdb@fas.harvard.edu

**提案主题**: "CBDB-UPSI 深度集成: 从传记计数到社会网络压力指标"

**我们提供**:
- 社会网络分析算法 (PageRank, 社区检测)
- 压力传播模型 (网络级联模拟)
- 可视化工具 (Gephi/NetworkX集成)

**我们请求**:
- 完整CBDB SQLite (含社会关系边)
- 地理坐标数据 (GIS集成)
- 联合工作坊 (哈佛-广中医)

**预期成果**:
- CBDB社会网络压力指数 (新指标)
- 联合论文: "Elite Network Dynamics and Dynastic Collapse"
- 开源工具: cbdb-network-psi (GitHub)

---

### 2.3 Cuneiform Digital Library Initiative (CDLI)

**联系对象**: Prof. Jacob Dahl (Oxford), CDLI Director
**邮箱**: cdli@ucla.edu (legacy), jacob.dahl@orinst.ox.ac.uk

**提案主题**: "CDLI-UPSI: 从文本计数到文明健康监测"

**我们提供**:
- 时间序列异常检测 (SPI burst detection)
- 多语言NLP管道 (阿卡德语→英语→中文)
- 跨文明比较框架 (美索不达米亚 vs 中国)

**我们请求**:
- 完整CDLI catalog (含地理坐标)
- 时期边界精细化 (从81 period-codes到年级别)
- 联合田野工作坊 (伊拉克/中国)

**预期成果**:
- CDLI文明健康Dashboard
- 联合论文: "Textual Density as Civilizational Vital Sign"
- 开源工具: cdli-psi-engine

---

### 2.4 Open Richly Annotated Cuneiform Corpus (ORACC)

**联系对象**: Prof. Steve Tinney (UPenn), ORACC Director
**邮箱**: tinney@sas.upenn.edu

**提案主题**: "ORACC-UPSI: 从语料库到压力语言学"

**我们提供**:
- 文本情绪分析 (SikuBERT适配阿卡德语)
- 体裁多样性指数 (Genre Diversity Index)
- 跨时期语义漂移检测

**我们请求**:
- 全部20+ sub-projects数据
- 精确年代学改进 (从period-level到year-level)
- 联合研讨会 (UPenn-广中医)

**预期成果**:
- ORACC压力语言学工具包
- 联合论文: "Linguistic Markers of Imperial Stress"
- 开源工具: oracc-semantic-psi

---

## 3. 合作框架设计

### 3.1 联合项目结构

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

### 3.2 知识产权与数据共享

| 方面 | 原则 | 具体措施 |
|------|------|----------|
| 数据许可 | 尊重原许可 | CBDB (CC BY-NC), Seshat (CC BY-NC-SA), CDLI/ORACC (开放) |
| 代码许可 | MIT | 所有UPSI工具开源 |
| 论文作者 | 贡献度排序 | 按ICMJE标准，数据提供方获共同作者 |
| 数据共享 | 分级开放 | 聚合结果公开，原始数据需申请 |
| 商业应用 | 非排他 | 各方可独立商业化，需标注来源 |

### 3.3 会议与工作坊计划

| 时间 | 事件 | 地点 | 目标 |
|------|------|------|------|
| 2026 Q3 | 启动视频会议 | Zoom | 建立联系，明确合作范围 |
| 2026 Q4 | 数据标准化工作坊 | 线上 | 统一变量、时间格式 |
| 2027 Q1 | 联合验证冲刺 | 广州/哈佛 | 各数据库独立运行UPSI |
| 2027 Q2 | 结果整合会议 | 牛津/UPenn | 比较结果，撰写论文 |
| 2027 Q3 | 政策应用研讨会 | 线上 | 邀请央行/IMF/UNESCO |
| 2027 Q4 | 联合投稿 | 各期刊 | Nature/PNAS/Scientific Data |

---

## 4. 预期影响

### 4.1 学术影响

| 指标 | 当前 | 合作后 (3年) |
|------|------|--------------|
| 验证域 | 8 | 15+ |
| 时间跨度 | 5,500年 | 12,000年 |
| NGA覆盖 | 5 | 35+ |
| 记录数 | 3.6M | 10M+ |
| 论文数 | 1 (投稿中) | 5-8 (联合) |
| 引用预期 | - | 500+ (3年) |

### 4.2 政策影响

| 机构 | 应用 | 时间 |
|------|------|------|
| 中国人民银行 | 系统性风险监测 | 2028 |
| IMF | 国家脆弱性评估 | 2029 |
| UNESCO | 文化遗产预警 | 2029 |
| 欧盟FSB | 金融市场监测 | 2028 |

### 4.3 社会影响

- **文明遗产保护**: 提前识别文化遗产地压力状态
- **教育**: UPSI进入大学课程 (数字人文+计算社会科学)
- **公众科学**: 开源Dashboard让公众监测文明健康

---

## 5. 立即行动清单

| # | 行动 | 负责人 | 截止日期 | 状态 |
|---|------|--------|----------|------|
| 1 | 发送Seshat合作邮件 | 王滇让 | 2026-06-10 | 待执行 |
| 2 | 发送CBDB合作邮件 | 王滇让 | 2026-06-10 | 待执行 |
| 3 | 发送CDLI合作邮件 | 王滇让 | 2026-06-15 | 待执行 |
| 4 | 发送ORACC合作邮件 | 王滇让 | 2026-06-15 | 待执行 |
| 5 | 准备UPSI-Consortium GitHub组织 | Mavis Team | 2026-06-20 | 待执行 |
| 6 | 起草MOU模板 | Mavis Team | 2026-06-30 | 待执行 |
| 7 | 申请NSF/ERC合作资助 | 王滇让 | 2026-09-01 | 待执行 |

---

## 6. 附录: 合作方背景研究

### Seshat
- 创始人: Peter Turchin (UConn), Harvey Whitehouse (Oxford)
- 资金: John Templeton Foundation ($4.3M), EU Horizon 2020
- 当前状态: 活跃，寻求方法论合作
- 合作切入点: 计算社会科学方法论

### CBDB
- 创始人: Peter Bol (Harvard), Michael Fuller (UC Irvine)
- 资金: 蒋经国基金会, 哈佛大学
- 当前状态: 活跃，v2024发布
- 合作切入点: 社会网络分析

### CDLI
- 创始人: Bob Englund (UCLA), now Jacob Dahl (Oxford)
- 资金: NSF, NEH, Mellon Foundation
- 当前状态: 活跃，GitHub数据开放
- 合作切入点: 时间序列分析

### ORACC
- 创始人: Steve Tinney (UPenn), Eleanor Robson (UCL)
- 资金: NEH, British Academy
- 当前状态: 活跃，20+ sub-projects
- 合作切入点: NLP + 语义分析

---

*提案完成。邮件模板可直接使用，建议v17投稿后发送以增加可信度。*
