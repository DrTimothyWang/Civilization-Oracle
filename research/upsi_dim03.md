## 维度03: 数据工程与跨域验证

> **研究员**: 维度03 (数据工程与跨域验证)  
> **阅读文件**: 36 个文件 (含代码、JSON 数据、Markdown 设计文档)  
> **生成时间**: 2026-06-04  
> **版本**: v6.1 综合

---

### 1. 数据源全景

#### 1.1 八大免费 API / 数据源

| 数据源 | URL / 获取方式 | 规模 | 用途 | 来源文件 |
|--------|----------------|------|------|----------|
| **CBDB (SQLite)** | `https://huggingface.co/datasets/cbdb/cbdb-sqlite/resolve/main/latest.zip` | ~200 MB, 658,339 人物 | 中华历史专家传记 | `cbdb_download.py`, `CDLI_跨文明验证技术设计.md` |
| **CDLI** | `https://cdli.earth/artifacts.json` | 368,735 artifacts (公开 API 限 100 条/次) | 美索不达米亚楔形文字 | `cdli_ingestor.py`, `CDLI_跨文明验证技术设计.md` |
| **CTEXT** | `https://ctext.org/api/search/zh` | 需人机验证 | 古籍文本语料 | `deploy_data.py` |
| **CHGIS** | `https://worldmap.harvard.edu/api` | 30,000+ 历史行政单元 | 历史地理编码 | `phase2_data_ingest.py` |
| **Wikidata** | `https://query.wikidata.org/sparql` | 1,728 战争+革命事件 | 全球政治危机 | `compute_political_psi.py` |
| **FRED** | `https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}` | 11+ 宏观指标 (1919-2026) | 宏观经济 PSI | `fetch_fred.py` |
| **yfinance** | Yahoo Finance API | 4 指数 / 20 资产 | 中国/全球金融 PSI | `V5_SUMMARY.md` (v5/v6 代码引用) |
| **OWID COVID** | `/tmp/owid_covid.csv` | 429,436 行, 200+ 国家日度 | COVID PSI | `compute_covid_psi.py` |
| **金十数据** | 本地 `jin10_daily.py` | 实时新闻流 | 新闻情绪 | `v6/jin10_daily.py` (提及) |

#### 1.2 CBDB 数据结构

CBDB 采用 SQLite 格式，核心表包括 (`phase2_data_ingest.py`):
- `CBDB_PERSON`: personid, name, birthyear, deathyear, origin_c, origin_s, gender
- `CBDB_PERSON_AFFILIATIONS`: 人物-机构关联
- `CBDB_AFFILIATIONS`: 机构/学派描述
- `CBDB_CODES`: 职官代码
- `CBDB_KIN_DATA`: 亲属关系网络

**质量分级** (`cbdb_import.py`):
- **A**: 完整（有生卒年+姓名+籍贯），score ≥ 7
- **B**: 良好（有生年+姓名），score ≥ 4
- **C**: 一般（有生年或姓名之一），score ≥ 2
- **D**: 缺失较多

实际五朝质量分布 (`output/psi_all_summary.json`):
- 北宋前期: A=1596, B=21 (总计 1,617)
- 北宋后期: A=2614, B=387 (总计 3,001)
- 南宋: A=1617, B=778 (总计 2,395)
- 明朝: A=4331, B=11995 (总计 16,326)
- 唐朝: A=7124, B=55 (总计 7,179)
- **五朝合计**: 30,518 条 A/B 级专家记录

#### 1.3 CDLI 数据结构

CDLI (Cuneiform Digital Library Initiative) 完整 catalog (`v6.1/data/cdli_psi_v61.json`):
- **总记录数**: 331,173 条楔形文字铭文/文献
- **时期数**: 81 个不同时期
- **体裁 (genre) 数**: 579 种
- **主要时期分布**:
  - Ur III (ca. 2100-2000 BC): 110,984 条
  - Old Babylonian (ca. 1900-1600 BC): 66,236 条
  - Neo-Assyrian (ca. 911-612 BC): 35,478 条
  - Neo-Babylonian (ca. 626-539 BC): 15,633 条
  - Middle Babylonian (ca. 1400-1100 BC): 12,704 条
  - Middle Hittite (ca. 1500-1100 BC): 14,692 条
  - Old Akkadian (ca. 2340-2200 BC): 9,974 条
  - Ebla (ca. 2350-2250 BC): 7,111 条

字段包括: `period`, `genre`, `provenience`, `dates_referenced`, ATF transliteration。

#### 1.4 其他数据源

- **CPM-KB (隐喻知识库)**: `data/cpm_kb_v0.2.json` — 当前仅 10 条手动编码隐喻，目标扩展至 1,000 条 (`迭代升级_Track2_数据工程与知识库.md`)
- **Perseus Digital Library**: 古希腊/罗马文本，免费 API，用于拉丁文 PSI 验证备选 (`CDLI_跨文明验证技术设计.md`)
- **ORACC / ETCSL / BDTNS**: 阿卡德语/苏美尔语备选语料 (`v6.1/CDLI_APPLICATION.md`)

---

### 2. 数据 Pipeline

#### 2.1 从原始数据到 PSI 的计算流程

```
原始数据层
    ├─ CBDB SQLite (Hugging Face / GitHub)
    ├─ CDLI API (cdli.earth)
    ├─ Wikidata SPARQL
    ├─ FRED CSV
    ├─ yfinance (Yahoo Finance)
    └─ OWID COVID CSV
         ↓
数据接入层 (Ingestion)
    ├─ cbdb_download.py → 下载 + 验证 SQLite
    ├─ cdli_ingestor.py → CDLI API 分页获取 (limit=100)
    ├─ deploy_data.py → 依赖检查 (Neo4j/Redis/CBDB/CTEXT)
    └─ fetch_fred.py → 11 宏观指标 CSV
         ↓
清洗与质量控制 (Cleaning & QC)
    ├─ cbdb_import.py → 按朝代过滤 + 质量标签 A/B/C/D
    ├─ phase2_data_ingest.py → CHGIS 地理编码 + DataIngestAgent
    └─ 迭代升级_Track2 → CHGIS 时态地理编码推理 (缺失率 94.9%→40%)
         ↓
PSI 计算层 (Computation)
    ├─ v4.x: 中华五朝 PSI (MMP_z + SFD_z + EED_z)
    ├─ v4.x: CDLI 美索不达米亚 PSI (MiniMax-M3 情感分析)
    ├─ v4.x: 古罗马 LLM 评估 (14 个历史时期)
    ├─ v5.x: 宏观 PSI (FRED 11 指标)
    ├─ v5.x: 政治 PSI (Wikidata 1728 事件)
    ├─ v5.x: COVID PSI (OWID 24 国)
    └─ v6.x: 全球金融 PSI (20 资产 PageRank 网络)
         ↓
验证层 (Validation)
    ├─ 气候对照 (竺可桢 1972)
    ├─ 跨模型验证 (M3 vs M2.7)
    ├─ IPW 精英偏差校正
    └─ Bootstrap CI 稳健性检验
```

#### 2.2 各 Phase 职责

基于代码文件与架构文档，Pipeline 可分为以下阶段:

| Phase | 职责 | 关键文件 |
|-------|------|----------|
| **Phase 1 (Deploy)** | 环境检查、数据下载、依赖验证 | `deploy_data.py`, `cbdb_download.py` |
| **Phase 2 (Ingest)** | CBDB/CTEXT/CHGIS 数据接入、清洗、质量标签 | `phase2_data_ingest.py`, `cbdb_import.py`, `cdli_ingestor.py` |
| **Phase 3 (NLP)** | SikuBERT 隐喻抽取、LLM 情感分析 | `utils/sikubert_nlp.py` (项目结构提及) |
| **Phase 4 (Master)** | 队列调度、多进程协调 | `mcp_a2a/orchestrator.py` (项目结构提及) |
| **Phase 5 (KGraph)** | 知识图谱构建 (内存降级/Neo4j) | `tkg_v3/` 模块 (项目结构提及) |
| **Phase 6 (Predictor)** | PSI 核心公式计算 (MMP+SFD+EED+GSI) | `v4/*.py`, `v5/*.py`, `tkg_v3/tkg_predictor.py` |
| **Phase 7 (Viz)** | 可视化、仪表盘生成 | `dashboard_v5.py`, `dashboard_v6.py` |
| **Phase 8 (QC/Report)** | 跨域验证、IPW 校正、报告输出 | `v4/ipw_correction_v4.py`, `scripts/verify_*.py` |

#### 2.3 数据清洗与质量控制

- **CBDB 质量标签**: 基于生卒年、姓名、籍贯、index_year 等字段自动评分 (`cbdb_import.py`)
- **地理编码**: CBDB x_coord/y_coord 关联，CHGIS 时态 Gazetteer 回退 (`phase2_data_ingest.py`)
- **CDLI ATF 清洗**: 去除行号、列标记、符号标注、编辑代码，保留纯音译文本 (`cdli_ingestor.py`)
- **Seshat 三层 QC 参照** (`迭代升级_Track2_数据工程与知识库.md`):
  - L1 数据层: CBDB 已实现 (cbdb_id 溯源)
  - L2 编码层: 需引入双人独立编码 (Krippendorff α ≥ 0.80)
  - L3 解释层: 需引入历史学家复核

---

### 3. 精英偏差与 IPW 校正

#### 3.1 CBDB 精英偏差问题

CBDB 存在三大系统性偏差 (`迭代升级_Track2_数据工程与知识库.md`):

| 偏差类型 | 表现 | 量化指标 |
|----------|------|----------|
| **精英偏向** | 明确包含"更丰富的高官精英男性传记数据" | 高官 (品级≥3) 占比 > 80% |
| **北方政治中心偏向** | 北方仅 0.5% (19人), 南方 4.6% (165人) | 南北记录比 |
| **时期集中偏向** | 唐宋时期数据占 75%+ | 各时期记录密度 |
| **性别偏差** | 女性记录占比 < 1% | 性别比约 50:1 |

#### 3.2 IPW 校正原理

**逆概率加权 (Inverse Probability Weighting)** (`v4/ipw_correction_v4.py`):
- 因变量: "被 CBDB 详细记录"的概率（用信息丰富度代理: 有卒年、有名字、有地理坐标）
- 自变量: 出生年份、出生年是否近似、朝代时期
- 方法: Logistic 回归估计倾向评分 p_i，权重 w_i = 1 / p_i
- 校正后 PSI = Σ(w_i × psi_i) / Σ(w_i)

v4.x 改进 (`v4/ipw_correction_v4.py`):
1. 用 logistic 回归替代硬编码规则
2. 在 individual-level 上做（v3.0 在朝代级）
3. Bootstrap CI (2000 次) 验证稳健性

#### 3.3 校正前后对比

基于 `v4/data/ipw_correction_v4.json`:

| 朝代 | n | 未校正均值 | IPW 校正均值 | 差异 |
|------|---|-----------|-------------|------|
| 北宋前期 | 1,758 | +0.5773 | +0.5736 | -0.0037 |
| 北宋后期 | 3,196 | -0.1261 | -0.1390 | -0.0129 |
| 南宋 | 3,066 | -0.5449 | -0.5659 | -0.0211 |
| 唐朝 | 9,599 | -0.0851 | -0.0672 | +0.0178 |
| 明朝 | 25,253 | -0.0438 | -0.0607 | -0.0170 |

**Cohen's d 对比**:
- 未校正: 0.4842
- IPW 校正: 0.5331
- 差异: +0.0489

**结论**: IPW 校正后 Cohen's d 略有提升，但核心结论（盛世 PSI > 危机 PSI）保持稳健。校正幅度较小（< 0.02），说明偏差虽存在，但未根本改变朝代级排序。

---

### 4. 跨域验证结果

#### 4.1 六域验证总表

基于 `v5/V5_SUMMARY.md` 及各级数据文件:

| 域 | 数据源 | 时期 | 样本规模 | 召回率 | 平均 Lead | 来源文件 |
|----|--------|------|----------|--------|-----------|----------|
| **中华历史** | CBDB 30,518 A/B 级专家 | -500 ~ 1900 AD | 96 十年窗 | **6/6 = 100%** | 30-60 年 | `psi_all_summary.json` |
| **美索不达米亚** | CDLI 331,173 条 | -3200 ~ -3100 BC (Uruk) | 100 文本 (API 限) | **1/1 = 100%** | N/A | `cdli_v4_results.json` |
| **古罗马** | LLM 评估 14 个历史时期 | BC 509 ~ AD 476 | 14 时期 | **4/4 = 100%** | 10-100 年 | `rome_psi_v4.json` |
| **中国金融** | 4 指数 6,048 bars | 2018-2026 | 7 危机 | **7/7 = 100%** | 0-34 天 | `V5_SUMMARY.md` |
| **全球金融** | 20 资产 187K bars | 1927-2026 | 24 危机×20=295 | **241/295 = 81.7%** | 35.6 天 | `V5_SUMMARY.md` |
| **全球政治** | Wikidata 1,728 战争+革命 | -218 ~ 2022 | 33 大事件 | **30/33 = 91%** | ±5 年 | `political_psi_v5.json` |
| **COVID** | OWID 429,436 行 (24 国) | 2020-2024 | 24 国日度 | 部分有效 | 混合 | `covid_psi_v5.json` |
| **宏观经济** | FRED 11 指标 | 1919-2026 | 多指标月度 | 混合 (HOUST 100%, M2SL 0%) | 0-7 月 | `macro_psi_v5.json` |

**总观测数**: 约 300 万条 (跨 6 域)  
**总时间跨度**: 约 5,200 年 (BC 3200 ~ AD 2026)

#### 4.2 各域详细结果

**中华历史** (`output/psi_all_summary.json`):
- 北宋前期: PSI=0.518, IPW=0.575, GSI=0.763
- 北宋后期: PSI=0.436, IPW=0.493, GSI=0.676
- 南宋: PSI=0.380, IPW=0.438, GSI=0.623
- 明朝: PSI=0.625, IPW=0.682, GSI=0.794
- 唐朝: PSI=0.612, IPW=0.669, GSI=0.806
- 排序: 明朝 > 唐朝 > 北宋前期 > 北宋后期 > 南宋

**美索不达米亚 (v4.0)** (`v4/data/cdli_v4_results.json`):
- Uruk III (n=95): MMP=+0.065, SFD=4.56, PSI_z=+1.0 (rising)
- Uruk IV (n=5): MMP=+0.020, SFD=1.79, PSI_z=-1.0 (declining)
- **关键发现**: v4.0 公式对样本量极不平衡敏感 (95 vs 5)，SFD 主导了 PSI_z 差异

**古罗马** (`v4/data/rome_psi_v4.json`):
- 共和国建立 (BC 509): -0.20
- 第二次布匿战争 (BC 218): -0.75
- 迦太基灭亡 (BC 146): +0.75
- 凯撒遇刺 (BC 44): -0.85
- 奥古斯都帝国建立 (BC 27): +0.65
- 图拉真巅峰 (AD 117): +0.85
- 3世纪危机 (AD 235): -0.92
- 西罗马灭亡 (AD 476): -0.95

**全球政治** (`v5/data/political_psi_v5.json`):
- 33 个重大历史事件中 30 个 PSI < -0 同步
- 命中: 第二次布匿战争、凯撒内战、三世纪危机、西罗马灭亡、黑死病、君士坦丁堡陷落、法国大革命、美国内战、一战、二战、911、GFC、COVID、俄乌
- 召回率: 30/33 = **91%**

**COVID** (`v5/data/covid_psi_v5.json`):
- 24 个主要国家分析
- 有效国家 (lead < 365 天): 4 国
- PSI 领先实际高峰: 0/4 = 0% (v5 版本存在滞后问题)
- 平均 Lead: -236 天 (PSI 极小点滞后于实际高峰)
- **注**: v5 COVID 使用 14 日滚动窗口，v6 已计划修正为滚动 z-score

**宏观经济** (`v5/data/macro_psi_v5.json`):
- 11 个 FRED 指标危机召回差异极大:
  - HOUST (新房开工): 9/9 = **100%**, lead 6.8 月
  - UMCSENT (消费者信心): 7/10 = **70%**, lead 5.1 月
  - CPILFESL (核心 CPI): 3/10 = 30%, lead 5 月
  - UNRATE (失业率): 3/12 = 25%, lead 6 月
  - M2SL (M2 货币供应): 0/9 = **0%**
- 总召回: 约 20-40% (宏观指标单独预测力有限)

---

### 5. 跨文明验证

#### 5.1 CDLI 美索不达米亚结果

**v4.0 初步验证** (`v4/CROSS_CIVILIZATION_CDLI.md`, `v4/data/cdli_v4_results.json`):
- 公共 API 限制: 每次最多 100 条，均为 Uruk III/IV (~前 3200 BCE)
- 92% 为 Lexical 词典，8% Vocabularies，缺乏叙事性文本
- Uruk III PSI_z = +1.0 (rising), Uruk IV = -1.0 (declining)
- **去 SFD 后 MMP 排序**: 美索不达米亚 Uruk III (MMP=+0.065) 高于中华 4 个朝代（除北宋前期外）
- 与历史事实一致: Uruk III 是城市革命鼎盛期（象形文字发明、寺庙经济）

**v6.1 完整 Catalog 验证** (`v6.1/data/cdli_psi_v61.json`, `v6.1/data/cdli_psi_real_v61.json`):
- 完整 catalog: **331,173 条** (154 MB)
- 按 `dates_referenced` 真实年代解析: 320,778 条成功 (90.8%)
- 覆盖 199 个不同年份，31 个 100 年窗口
- 关键窗口 PSI:
  - -2100 (Ur III): n=111,281, PSI=0.528 ← 文本密度最高
  - -1800 (Old Babylonian): n=66,827, PSI=0.360 ← 体裁多样性最高 (40 genres)
  - -800 (Neo-Assyrian): n=35,514, PSI=0.407
  - -1300 (Middle Babylonian): n=27,607, PSI=0.407
  - -600 (Neo-Babylonian): n=17,510, PSI=0.398

#### 5.2 古罗马结果

基于 LLM 评估 14 个历史时期 (`v4/data/rome_psi_v4.json`):
- 方法: MiniMax-M3 对已知历史事件做情感极性评估（非真实拉丁文文本爬取）
- Perseus Digital Library 受 Cloudflare 保护，无法直接爬取
- 与中华 PSI_z 对比:
  - 罗马共和国建立 (-0.20) ≈ 唐朝 (-0.19)
  - 图拉真巅峰 (+0.85) > 明朝 (+0.34)
  - 西罗马灭亡 (-0.95) << 南宋 (-0.44)
- 危机事件 PSI 显著为负: 3世纪危机 (-0.92), 西哥特洗劫 (-0.92), 汪达尔洗劫 (-0.95), 西罗马灭亡 (-0.95)

#### 5.3 气候对照（竺可桢）

基于 `v4/data/climate_validation.json`:
- 数据源: 竺可桢 (1972) 《中国近五千年气候变迁的初步研究》
- 跨 96 个十年窗，PSI vs 温度距平 **Pearson r = 0.022** (极弱相关)
- **结论**: PSI 独立于气候，不是气候的简单代理

按朝代分层:

| 朝代 | n (十年窗) | avg PSI | avg 温度距平 | r |
|------|-----------|---------|-------------|---|
| 唐朝 | 31 | -0.194 | +0.381 | **+0.631** |
| 北宋前期 | 8 | +0.318 | +0.144 | +0.473 |
| 北宋后期 | 11 | +0.113 | -0.147 | +0.391 |
| 南宋 | 17 | -0.444 | -0.573 | **-0.573** |
| 明朝 | 29 | +0.337 | -0.507 | +0.239 |

- 唐朝、南宋内部 PSI-气候正相关较强
- 整体跨朝代弱相关支持 "PSI 反映社会心理压力而非单纯气候响应"

#### 5.4 跨模型验证（M3 vs M2.7）

基于 `v4/data/cross_model_validation.json`:
- 模型: MiniMax-M3 vs MiniMax-M2.7-highspeed
- 相关系数 r = **0.7401**
- 平均差异 = 0.1175
- 示例差异:
  - 唐朝 720s: M3=0.95, M2.7=0.90 (diff=0.05)
  - 北宋前期 1020s: M3=0.70, M2.7=0.90 (diff=0.20)
  - 明朝 1580s: M3=-0.50, M2.7=-0.70 (diff=0.20)

**结论**: 两模型高度一致 (r=0.74)，但个别十年存在 ±0.20 差异，建议使用 M3 作为主力模型。

---

### 6. 数据局限

#### 6.1 CBDB 局限

1. **女性代表严重不足**: 性别比约 50:1，女性占比 < 1% (`迭代升级_Track2_数据工程与知识库.md`)
2. **地理覆盖偏差**: 北宋 3,564 条中 94.9% 无法分类区域；北方仅 19 人 (0.5%)，南方 165 人 (4.6%)
3. **精英偏向**: 高官 (品级≥3) 占比 > 80%，不代表普通民众情绪
4. **时期集中**: 唐宋数据占 75%+，其他时期稀疏

#### 6.2 CDLI 局限

1. **API 限制**: 公共 API 每次最多 100 条，无法批量获取完整 331,173 条 (`cdli_ingestor.py`, `v4/CROSS_CIVILIZATION_CDLI.md`)
2. **内容类型单一**: v4.0 样本中 92% 为 Lexical 词典，缺乏书信、法律、史诗等叙事性文本
3. **时间跨度有限**: v4.0 仅覆盖 Uruk III/IV (~200 年)，无法验证长期 PSI 模式
4. **GSI 不适用**: 美索不达米亚没有"南北"概念，GSI 强制设为 1.0 中性
5. **语言障碍**: 阿卡德语楔形文字需亚述学知识，ATF → 英语翻译质量不稳定

#### 6.3 其他域局限

1. **古罗马**: Perseus Digital Library 受 Cloudflare 保护，当前为 LLM 模拟评估，非真实文本爬取 (`v4/rome_psi_v4.py`)
2. **COVID**: v5 版本 PSI 极小点滞后于实际高峰 (平均 -236 天)，公式需修正 (`v5/data/covid_psi_v5.json`)
3. **宏观指标**: M2SL 召回率 0%，不同指标预测力差异极大 (`v5/data/macro_psi_v5.json`)
4. **CPM-KB**: 当前仅 10 条隐喻，与 CMDAG 的 27,989 条差距三个数量级 (`迭代升级_Track2_数据工程与知识库.md`)

---

### 7. 关键数字汇总

#### 7.1 规模统计

| 指标 | 数值 | 来源 |
|------|------|------|
| **总观测数** | ~3,000,000 | `V5_SUMMARY.md` |
| **跨域数** | 6-7 个独立域 | 综合 |
| **时间跨度** | BC 3200 ~ AD 2026 (~5,200 年) | 综合 |
| **CBDB 专家记录** | 30,518 (A/B 级) | `psi_all_summary.json` |
| **CDLI 楔形文字** | 331,173 条 | `cdli_psi_v61.json` |
| **Wikidata 政治事件** | 1,728 | `wikidata_events.json` |
| **OWID COVID 行数** | 429,436 | `/tmp/owid_covid.csv` |
| **FRED 宏观指标** | 11 个 | `fetch_fred.py` |
| **全球金融资产** | 20 资产, 187K bars | `V5_SUMMARY.md` |
| **中国金融指数** | 4 指数, 6,048 bars | `V5_SUMMARY.md` |

#### 7.2 各域召回率与领先时间

| 域 | 召回率 | 领先时间 | 来源 |
|----|--------|----------|------|
| 中华历史 | 100% (6/6) | 30-60 年 | `V5_SUMMARY.md` |
| 美索不达米亚 (v4) | 100% (1/1) | N/A | `V5_SUMMARY.md` |
| 古罗马 | 100% (4/4) | 10-100 年 | `V5_SUMMARY.md` |
| 中国金融 | 100% (7/7) | 0-34 天 | `V5_SUMMARY.md` |
| 全球金融 | 81.7% (241/295) | 35.6 天 | `V5_SUMMARY.md` |
| 全球政治 | 91% (30/33) | ±5 年 | `V5_SUMMARY.md` |
| 宏观经济 (HOUST) | 100% (9/9) | 6.8 月 | `macro_psi_v5.json` |
| 宏观经济 (M2SL) | 0% (0/9) | N/A | `macro_psi_v5.json` |
| COVID (v5) | 0% (0/4 有效国) | -236 天 (滞后) | `covid_psi_v5.json` |

#### 7.3 跨文明 PSI 对比 (去 SFD 后 MMP)

| 文明/时期 | MMP (中位数情绪) | 来源 |
|-----------|-----------------|------|
| 美索不达米亚 Uruk III | +0.065 | `v4/CROSS_CIVILIZATION_CDLI.md` |
| 中华 北宋前期 | +0.571 | `v4/CROSS_CIVILIZATION_CDLI.md` |
| 中华 明朝 | -0.045 | `v4/CROSS_CIVILIZATION_CDLI.md` |
| 中华 唐朝 | -0.073 | `v4/CROSS_CIVILIZATION_CDLI.md` |
| 中华 北宋后期 | -0.126 | `v4/CROSS_CIVILIZATION_CDLI.md` |
| 中华 南宋 | -0.515 | `v4/CROSS_CIVILIZATION_CDLI.md` |

---

### 附录: 引用文件清单

1. `CDLI_跨文明验证技术设计.md` — 跨文明技术架构与数据源评估
2. `cbdb_download.py` — CBDB 下载与验证脚本
3. `cbdb_import.py` — CBDB 朝代提取与质量标签
4. `cdli_ingestor.py` — CDLI API 接入与 ATF 清洗
5. `deploy_data.py` — 依赖检查与部署脚本
6. `phase2_data_ingest.py` — Phase 2 数据接入层 (CBDB+CHGIS+CTEXT)
7. `迭代升级_Track2_数据工程与知识库.md` — CHGIS/CPM-KB/IPW 路线图
8. `data/cbdb/cbdb_20260523.json` — CBDB SQLite 元数据
9. `data/cpm_kb_v0.2.json` — 隐喻知识库样本
10. `output/decade_psi_all_api.json` — 十年级 PSI 时序
11. `output/cdli_analysis.json` — CDLI v3.0 100 条缓存分析
12. `output/psi_all_summary.json` — 五朝 PSI 汇总
13. `v4/CROSS_CIVILIZATION_CDLI.md` — v4.0 跨文明验证报告
14. `v4/cdli_v4_mesopotamia.py` — CDLI v4.0 PSI 计算代码
15. `v4/rome_psi_v4.py` — 古罗马 LLM 评估代码
16. `v4/climate_validation.py` — 竺可桢气候对照代码
17. `v4/cross_model_validation.py` — 跨模型验证代码 (输出见 JSON)
18. `v4/ipw_correction_v4.py` — IPW 校正代码
19. `v4/data/cdli_v4_results.json` — CDLI v4.0 结果
20. `v4/data/rome_psi_v4.json` — 古罗马 PSI 结果
21. `v4/data/climate_validation.json` — 气候验证结果
22. `v4/data/cross_model_validation.json` — M3 vs M2.7 对比
23. `v4/data/ipw_correction_v4.json` — IPW 校正前后对比
24. `v5/compute_political_psi.py` — 政治 PSI 计算
25. `v5/compute_macro_psi.py` — 宏观 PSI 计算
26. `v5/compute_covid_psi.py` — COVID PSI 计算
27. `v5/fetch_fred.py` — FRED 数据采集
28. `v5/data/political_psi_v5.json` — 政治 PSI 结果
29. `v5/data/macro_psi_v5.json` — 宏观 PSI 结果
30. `v5/data/covid_psi_v5.json` — COVID PSI 结果
31. `v5/data/wikidata_events.json` — Wikidata 1,728 事件
32. `v6.1/CDLI_APPLICATION.md` — CDLI 学术账户申请模板
33. `v6.1/cdli_psi_analysis.py` — CDLI 完整 catalog PSI 分析
34. `v6.1/cdli_real_year_psi.py` — CDLI 真实年代 PSI 重算
35. `v6.1/data/cdli_psi_v61.json` — v6.1 CDLI 时期统计
36. `v6.1/data/cdli_psi_real_v61.json` — v6.1 真实年代 PSI 结果
37. `v5/V5_SUMMARY.md` — v5.0 跨域验证总表 (补充阅读)
