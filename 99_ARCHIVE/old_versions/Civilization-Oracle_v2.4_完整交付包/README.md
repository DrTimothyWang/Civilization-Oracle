# Civilization-Oracle v2.4 完整交付包

> 中华文明语义深度分析历史预测系统
> 版本: v2.4 | 日期: 2026-05-29
> 作者: 王滇让研究团队 | 学术顾问: 马利军 教授

---

## 目录结构

```
Civilization-Oracle_v2.4_完整交付包/
├── README.md                          ← 本文件（项目说明）
├── CHANGELOG.md                      ← 完整变更日志
│
├── 01_论文/
│   ├── 论文草稿_Civilization-Oracle_v0.3.md    ← 最新版（~3000词，整合P3）
│   ├── 论文草稿_Civilization-Oracle_v0.2.md
│   ├── 论文草稿_Civilization-Oracle_v0.1.md
│   └── 论文框架_Civilization-Oracle.md
│
├── 02_演示/
│   ├── Civilization-Oracle_v2.4_演示文稿.pptx  ← 10页PPT演示版
│   └── v2.4_四朝PSI可视化报告.html             ← ECharts交互式图表
│
├── 03_技术报告/
│   ├── P3_里程碑报告_v2.4.md                 ← P3完整交付报告
│   ├── 验证报告_StatsRepair.md               ← P0统计验证报告
│   ├── Civilization-Oracle_完整技术文档_v2.3.md
│   └── Civilization-Oracle_迭代升级路线图_v2.4.md
│
├── 04_规格与架构/
│   ├── 语意演化预测系统_v2.0.md             ← 主规格文档（v2.4更新）
│   ├── 对标分析报告_Civilization-Oracle.md   ← vs Seshat/Clio/Ngram
│   └── 06_Agent开发指南.md                 ← Agent开发指南（1453行）
│
├── 05_迭代升级过程/
│   ├── 迭代升级_Track1_统计方法论.md
│   ├── 迭代升级_Track2_数据工程与知识库.md
│   ├── 迭代升级_Track3_NLP与知识图谱技术.md
│   ├── 迭代升级_Track4_学术定位与伦理框架.md
│   └── 迭代升级_Track5_技术架构重构.md
│
├── 06_核心代码/
│   ├── pipeline/
│   │   ├── phase_pipeline_v2.py             ← 主管线（v2.4，支持--multi）
│   │   ├── phase2_data_ingest.py
│   │   ├── phase3_text_analyst.py
│   │   ├── phase4_master.py
│   │   ├── phase5_kgraph.py
│   │   ├── phase6_pipeline.py
│   │   └── phase8_viz.py
│   ├── cbdb_download.py                    ← CBDB数据下载脚本
│   ├── deploy_data.py
│   └── run_with_real_data.py
│
├── 07_工具模块/
│   ├── bayesian_framework.py                ← 贝叶斯PSI推断
│   ├── cbdb_ipw_correction.py             ← IPW偏差校正
│   ├── chgis_geo.py                       ← CHGIS地理编码
│   ├── sikubert_nlp.py                    ← SikuBERT古籍NLP（双模式）
│   ├── tkg_upgrade.py                      ← TKG因果知识图谱
│   ├── stats_repair.py                     ← 统计验证模块
│   └── config_loader.py
│
├── 08_测试/
│   ├── test_kgraph.py
│   ├── test_predictor.py
│   └── test_text_analyst.py
│
├── 09_配置/
│   └── pipeline_config.yaml                ← YAML配置化
│
└── 10_数据/
    ├── cpm_kb_v0.2.json                   ← 隐喻知识库（100条）
    └── multi_dynasty_results.json          ← 四朝PSI结果
```

---

## 快速开始

### 依赖
```bash
pip install numpy scipy scikit-learn
```

### 运行主管线
```bash
cd 06_核心代码/pipeline
python3 phase_pipeline_v2.py              # 单周期（北宋）
python3 phase_pipeline_v2.py --multi       # 全周期（唐宋明+北宋）
```

### 运行 IPW 偏差校正
```bash
cd 07_工具模块
python3 cbdb_ipw_correction.py
```

### 激活 SikuBERT 真实模型
```bash
pip install transformers
# utils/sikubert_nlp.py 自动切换至 ernie-3.0-mini-zh
```

---

## 版本历史摘要

| 版本 | 日期 | 核心内容 |
|------|------|---------|
| v0.1 | 2026-05-26 | 初始框架 |
| v0.2 | 2026-05-27 | 9章完整草稿 |
| v0.3 | 2026-05-29 | 整合P3：全周期/IPW/SikuBERT |
| v2.0 | 2026-05-27 | 多Agent协同架构 |
| v2.3 | 2026-05-27 | 贝叶斯PSI + TKG因果推理 |
| v2.4 | 2026-05-29 | 全周期扩展 + IPW偏差校正 |

---

## 核心成果

### PSI 校正结果（四朝）
| 朝代 | 年份 | PSI校正 | GSI | 稳定性 |
|------|------|--------|-----|--------|
| 唐朝 | 618-907 | 0.327 | 1.733 | crisis |
| 北宋 | 960-1127 | 0.310 | 1.683 | crisis |
| 南宋 | 1127-1279 | 0.295 | 1.755 | crisis |
| 明朝 | 1368-1644 | 0.246 | 1.683 | crisis |

### IPW 偏差校正
- 倾向分模型: sigmoid(0.3 + rank_bonus + north_bonus + school_bonus)
- PSI 0.614 → 0.604（下降1.6%）
- 高偏差样本（北方+高品级+主流）正确降权

---

## 目标期刊
Digital Humanities（待内部review后投稿）

---

*Civilization-Oracle v2.4 | 王滇让研究团队 | 2026-05-29*
