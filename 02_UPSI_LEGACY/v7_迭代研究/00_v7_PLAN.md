# UPSI v7 迭代研究计划

> **编制日期**: 2026-06-04
> **基础版本**: v6.3 (ORACC数据已落盘, Nature投稿稿已起草)
> **工作目录**: `/Users/wangzr/Desktop/历史事件预测建模/v7_迭代研究/`
> **目标**: 基于深度研究发现的10个洞察, 系统性推进v7迭代

---

## 一、v7 核心目标

基于深度研究交叉验证发现的**6个高优先级行动项**：

| 优先级 | 行动项 | 来源洞察 | 预期产出 |
|--------|--------|----------|----------|
| 🔴 P0 | ORACC数据PSI计算与跨文明验证 | 洞察5, 洞察9 | v7美索PSI报告 |
| 🔴 P0 | COVID域滞后问题修正 | 洞察4 | v7 COVID修正报告 |
| 🟡 P1 | ROC AUC提升与阈值优化 | 洞察3 | v7 ROC优化报告 |
| 🟡 P1 | 投稿材料完善(Nature/PNAS) | 洞察8 | v7投稿稿 |
| 🟢 P2 | 技术债务清理(MCP+A2A/TKG) | 洞察6 | v7架构文档 |
| 🟢 P2 | 方法论论文框架 | 洞察1, 洞察7 | v7方法论论文 |

---

## 二、P0: ORACC数据PSI计算

### 2.1 现状
- v6.3已落盘: ePSD2/admin/ur3 (80,181条), DCCLT (10,215条), RIAO/RINAP/SAAO (~8,000条)
- 总计: ~43万条美索不达米亚数据
- 但: **PSI计算尚未完成**——v6.2仅基于CDLI catalog 33万条做验证

### 2.2 v7目标
- 用ORACC实际文本数据(lem/ATF)计算Ur III时期PSI
- 时间精度从200年→1年(date_of_origin)
- 验证v6.2的7/8通过率能否提升到8/8

### 2.3 实施步骤
1. 解析ePSD2/admin/ur3 corpusjson (1.7GB)
2. 提取lem词形→MiniMax embedding→情感评分
3. 按date_of_origin(年名)聚合→计算MMP/EMP/SFD/GSI
4. 与CBDB中国同期(-2112~-2000)做跨文明互相关
5. 输出v7美索PSI时间序列+验证报告

---

## 三、P0: COVID域修正

### 3.1 现状
- v5 COVID PSI极小点平均滞后实际高峰236天
- 方向错误: PSI应该领先危机, 而非滞后

### 3.2 根因分析
- OWID数据以国家为单位聚合, PSI计算窗口与疫情传播动力学不匹配
- 可能: 疫情高峰时记录密度下降(医疗系统崩溃)→SFD指标反向

### 3.3 v7修正方案
- 改用OWID每日新增病例/死亡率的**变化率**而非绝对值
- 引入**领先指标**: 检测阳性率、R0估计、政策严格度指数
- 重新对齐时间窗口: 从"疫情高峰"对齐改为"政策响应"对齐
- 输出v7 COVID PSI修正报告

---

## 四、P1: ROC AUC提升

### 4.1 现状
- ROC AUC 0.479-0.594 (接近随机)
- 原因: PSI作为同步器, 分类任务本身有局限

### 4.2 v7优化方案
- **阈值动态化**: 从固定-0.5改为按域自适应(基于历史分布百分位)
- **集成模型**: 结合LSTM(78.67%)和Transformer(78.28%)做ensemble
- **特征工程**: 加入PSI变化率(dPSI/dt)和PSI波动率
- 目标: AUC提升至0.65-0.70

---

## 五、P1: 投稿材料完善

### 5.1 基于洞察8的调整
- 降低"诺奖级"声称→强调"跨学科整合""方法论创新"
- 增加"局限性"段落权重
- 准备"幸存者偏差"回答: 明确报告尝试域数vs成功域数

### 5.2 v7产出
- v7_NATURE_MAIN.md (修正版)
- v7_PNAS_MANUSCRIPT.md (修正版)
- 审稿人可能问题Q&A文档

---

## 六、P2: 技术债务清理

### 6.1 MCP+A2A轻量实现
- 基于v6.3已有代码, 实现最小可用版本
- 优先: psi_calculate + cbdb_query + sentiment_analyze 3个Tool

### 6.2 TKG实用化
- 将MRR=0.3631的TKG与PSI做实际联动
- 简化: 用PSI阈值触发TKG查询, 输出"可能因果链"

---

## 七、P2: 方法论论文

### 7.1 框架
- 标题: "AI Agent Teams for Cross-Disciplinary Research: A Case Study in 20 Hours"
- 核心: 展示20小时完成6域验证的过程方法论
- 重点: 马老师审稿模式、物理降级事件、自我修正机制

---

## 八、v7 文件结构

```
v7_迭代研究/
├── 00_v7_PLAN.md              # 本计划
├── 01_oracc_psi/              # ORACC PSI计算
│   ├── parse_ur3_corpus.py
│   ├── compute_meso_psi.py
│   └── meso_psi_report.md
├── 02_covid_fix/              # COVID修正
│   ├── covid_realign.py
│   └── covid_fix_report.md
├── 03_roc_optimize/           # ROC优化
│   ├── adaptive_threshold.py
│   └── roc_report.md
├── 04_submission/             # 投稿材料
│   ├── v7_NATURE_MAIN.md
│   ├── v7_PNAS_MANUSCRIPT.md
│   └── reviewer_QA.md
├── 05_tech_debt/              # 技术债务
│   ├── mcp_minimal.py
│   ├── tkg_psi_bridge.py
│   └── tech_debt_report.md
└── 06_methodology_paper/      # 方法论论文
    └── methodology_framework.md
```

---

## 九、里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| v7.0 | 2026-06-04 | 计划制定 + ORACC解析启动 |
| v7.1 | 2026-06-04 | ORACC PSI计算完成 |
| v7.2 | 2026-06-04 | COVID修正 + ROC优化 |
| v7.3 | 2026-06-04 | 投稿材料完善 |
| v7.4 | 2026-06-04 | 技术债务清理 |
| v7.5 | 2026-06-04 | 方法论论文框架 |
| v7.FINAL | 2026-06-04 | 综合报告 + 压缩包 |

---

*基于深度研究10个洞察制定 | 目标: 将v6.3的"投稿准备"推进到"投稿就绪"*
