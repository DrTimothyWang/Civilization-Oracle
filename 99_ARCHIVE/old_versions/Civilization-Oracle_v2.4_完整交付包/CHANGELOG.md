# Civilization-Oracle 完整变更日志

---

## P3 (2026-05-29) — 全周期扩展与模型升级

### 新增文件
- `multi_dynasty_results.json` — 唐宋明+北宋四朝PSI分析结果
- `utils/cbdb_ipw_correction.py` — CBDB逆概率加权偏差校正模块
- `utils/sikubert_nlp.py`（升级）— ernie-3.0-mini-zh真实模型双模式接入
- `phase_pipeline_v2.py`（升级）— dynasty_periods字典 + --multi参数
- `P3_里程碑报告_v2.4.md` — P3完整交付报告
- `论文草稿_Civilization-Oracle_v0.3.md` — ~3000词完整论文
- `Civilization-Oracle_v2.4_演示文稿.pptx` — 10页学术演示
- `v2.4_四朝PSI可视化报告.html` — ECharts交互式图表

### 技术变更
- 全周期扩展: 北宋/南宋/明朝/唐朝四朝并行PSI分析
- IPW偏差校正: 倾向分sigmoid模型，逆稳定化权重
- SikuBERT: load_model()类方法，try/except降级兜底
- SFD权重: 0.33→0.50（贝叶斯校正）
- CR-001阈值: 0.25→0.55（适配真实数据）

---

## P2 (2026-05-27) — 贝叶斯PSI与TKG因果推理

### 新增文件
- `utils/bayesian_framework.py` — Bootstrap+Jeffreys先验贝叶斯推断
- `utils/tkg_upgrade.py` — CEGRL因果推理，5节点5边
- `phase_pipeline_v2.py` — v2.4主管线（7→5阶段合并）
- `论文草稿_Civilization-Oracle_v0.2.md` — 237行论文草稿

---

## P1 (2026-05-27) — 数据工程与NLP

### 新增文件
- `utils/sikubert_nlp.py` — SikuBERT古籍NLP（规则词典降级）
- `utils/chgis_geo.py` — CHGIS地理编码，GSI计算
- `utils/cpm_kb.py` — 隐喻知识库v0.1（50条）
- `phase6_pipeline.py` — 端到端Pipeline
- `phase5_kgraph.py` — 知识图谱构建

---

## P0 (2026-05-26-27) — 测试与配置化

### 新增文件
- `utils/stats_repair.py` — 64个单元测试，统计验证
- `config/pipeline_config.yaml` — YAML配置化
- `验证报告.md` — P0验证报告
- `data/cpm_kb_v0.2.json` — 隐喻知识库升级（100条，9域）

---

## 系统架构变更

### 5阶段管线（v2.4）
```
Stage1: 数据采集（CBDB 658,339条人物）
Stage2: 语义分析（SikuBERT双模式NLP）
Stage3: 地理编码（CHGIS GSI计算）
Stage4: PSI计算（贝叶斯+IPW偏差校正）
Stage5: 输出报告（四朝PSI+因果链）
```

### 核心公式

**PSI = SFD_weight * SFD + GSI_weight * GSI + TSI_weight * TSI**
- SFD权重: 0.50（MMP 0.25 + EMP 0.25）
- GSI权重: 0.30
- TSI权重: 0.20

**IPW逆稳定化权重**: weight = mean(propensity) / propensity

**倾向分**: propensity = sigmoid(0.3 + rank_bonus + north_bonus + school_bonus)
