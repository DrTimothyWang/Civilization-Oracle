# v11 TrackB: UPSI 第8域新数据源探索报告

**探索员**: v11_TrackB_新数据源探索员  
**日期**: 2026-06-04  
**版本**: v1.0  
**目标**: 为UPSI框架寻找第8个独立验证域，扩展跨文明覆盖范围

---

## 1. 背景与现有7域概览

UPSI（统一压力同步指数）当前已验证的7个独立域：

| 域编号 | 域名称 | 数据类型 | 时间跨度 | 核心数据源 |
|--------|--------|----------|----------|------------|
| 1 | 中华历史 | 传记文本+地理 | 618–1644 CE | CBDB + CHGIS |
| 2 | 美索不达米亚 | 楔形文字文本 | 2334–64 BCE | CDLI + ORACC |
| 3 | 古罗马 | 历史文本 | 753 BCE–476 CE | 自建语料库 |
| 4 | 中国金融 | 市场数据 | 1990–2025 | yfinance |
| 5 | 全球金融 | 市场数据 | 2000–2025 | yfinance + FRED |
| 6 | 全球政治 | 事件数据 | 2000–2025 | GDELT/新闻 |
| 7 | COVID/宏观 | 情绪+宏观 | 2020–2025 | 金十数据 + FRED |

**关键缺口**: 现有7域中，古代文明覆盖中华、美索不达米亚、罗马三大文明，但缺少**古希腊**、**古埃及**、**中世纪欧洲**、**古印度**等重要文明；现代数据覆盖金融与政治，但缺少**全球历史比较**的宏观结构化数据。

---

## 2. 候选数据源清单与详细评估

### 2.1 Perseus Digital Library + Open Greek & Latin

**基本信息**
- **URL**: http://www.perseus.tufts.edu/
- **GitHub**: https://github.com/PerseusDL/canonical-greekLit (Greek), canonical-latinLit (Latin)
- **运营方**: Tufts University Perseus Project
- **许可**: CC BY-SA 3.0/4.0

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | Greek: ~13.5M words (1,300+ texts); Latin: ~10M+ words; First1KGreek adds 23M+ words |
| **时间跨度** | Greek: 8th c. BCE – 2nd c. CE (~1,000 years); Latin: 3rd c. BCE – 2nd c. CE |
| **结构化程度** | TEI-XML编码，含CTS URN标识符、作者、标题、年代、体裁元数据；部分含 morphological annotation |
| **可获取性** | 免费批量下载（GitHub/Zenodo zip）；提供 Stable URI API (data.perseus.org)；支持 HTML/XML 格式 |
| **PSI可计算性** | ✅ 高。可直接计算 SFD（文本密度因子）：按十年/世纪聚合文本量、作者数、体裁多样性；MMP/EMP 可通过 LLM API 对翻译文本做情感分析；GSI 可结合 Pleiades 地理数据计算 |
| **学术认可度** | 极高。数字人文领域最权威的古典学文本库，被数千篇论文引用，是 Ancient Greek NLP 的标准基准 |
| **与现有域独立性** | ⚠️ 中等。与"古罗马域"同属古典文明，但古希腊文明在语言、文化、政治制度上独立于罗马；时间上有重叠但文明实体不同 |

**优势**: 数据质量最高、开放获取最完善、TEI-XML结构化程度最高、已有成熟的NLP工具链（Morpheus, CLTK）。  
**劣势**: 与古罗马域同属地中海古典文明，独立性不如其他候选；文本以文学/哲学为主，历史编年文本比例较低。

---

### 2.2 Seshat: Global History Databank

**基本信息**
- **URL**: https://seshatdatabank.info/
- **数据下载**: https://seshat-db.com/downloads_page/ (Equinox-2020)
- **Zenodo**: https://doi.org/10.5281/zenodo.6642229
- **GitHub**: https://github.com/seshatdb/Equinox_Data
- **运营方**: University of Connecticut / Evolution Institute
- **许可**: CC BY-NC-SA (非商业)

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | ~400 polities, 1,500+ variables, ~400,000 coded records; Equinox-2020 release: 374 polities, 136 variables, 47,400 records |
| **时间跨度** | ~10,000 BCE – 1,900 CE (~12,000 years) |
| **结构化程度** | 极高。每个polity按世纪编码，变量覆盖：人口、领土、首都规模、层级水平、政府复杂度、基础设施、信息系统、文本出版、货币 sophistication；附 narrative paragraphs 和学术引用 |
| **可获取性** | 免费下载（CSV/Spreadsheet）；Zenodo DOI 存档；计划中的RDF triple store；需注册浏览 |
| **PSI可计算性** | ⚠️ 中等。Seshat 已有"Social Complexity"综合指标（PC1，解释77%方差），与UPSI概念相关但非同一指标。可将 Seshat 的 complexity/warfare/instability 变量重新操作化为 UPSI 三维度：Material=人口/领土变化；Fragmentation=层级水平/政府复杂度波动；Disengagement=文本出版/信息系统下降 |
| **学术认可度** | 极高。Turchin et al. PNAS 2017, Cliodynamics 系列论文；被历史经济学、考古学、复杂系统科学广泛引用 |
| **与现有域独立性** | ✅ 极高。全球30+ NGA（自然地理区域），覆盖非洲、美洲、大洋洲、东南亚等现有7域完全未触及的区域 |

**优势**: 真正的全球覆盖、时间跨度最大、结构化程度最高、学术背书最强、可直接与UPSI的"跨文明同步假说"对话。  
**劣势**: 数据类型为专家编码变量而非原始文本，UPSI操作化需重新设计；非商业许可限制；数据更新缓慢（Equinox-2020为最新）；缺失数据较多（61% moralizing gods 数据缺失）。

---

### 2.3 ToposText

**基本信息**
- **URL**: https://topostext.org/
- **运营方**: Aikaterini Laskaridis Foundation (Greece)
- **许可**: Mostly open access (some translations by permission)

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | 860 translated Greek & Latin texts (~20M words); 8,137 mapped places; 21,360 proper names; 277,000 ancient references |
| **时间跨度** | Neolithic – 2nd c. CE (focus on Greek world) |
| **结构化程度** | 高。每段文本关联：日期、地点、体裁、作者；CTS IDs; Wikidata links; 段落级事件日期（精确到年或近似） |
| **可获取性** | 网站免费；gazetteer 可下载 (KML, GeoJSON, Pelagios LOD)；text library 为 RDF turtles；REST API 可段落级访问 |
| **PSI可计算性** | ✅ 高。可按地理区域+时间窗口聚合文本引用密度（SFD）；通过LLM分析文本片段情感（MMP/EMP）；地理压力通过Pleiades坐标计算（GSI） |
| **学术认可度** | 中高。被古典学、数字人文领域认可，但较 Perseus 年轻 |
| **与现有域独立性** | ⚠️ 中等。与 Perseus 高度重叠（大量文本源自 Perseus），但增加了地理索引层和移动应用界面 |

**优势**: 地理-文本关联独特、移动友好、REST API 现代化、与 Pleiades/Wikidata 深度集成。  
**劣势**: 文本库大量依赖 Perseus，非独立数据源；英文翻译为主，原始希腊文较少。

---

### 2.4 Pleiades + Digital Periegesis

**基本信息**
- **Pleiades URL**: https://pleiades.stoa.org/
- **Digital Periegesis URL**: https://digitalperiegesis.github.io/
- **运营方**: NYU ISAW + UNC AWMC (Pleiases); Uppsala University (Digital Periegesis)
- **许可**: CC BY 3.0 (Pleiades); Open LOD (Digital Periegesis)

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | Pleiades: 30,000+ ancient places; Digital Periegesis: 4,225 places, 1,762 objects, 3,882 people, 1,000+ events (Pausanias-focused) |
| **时间跨度** | Pleiades: Archaic – Byzantine; Digital Periegesis: 2nd c. CE (Pausanias) |
| **结构化程度** | 极高。Pleiades: places/locations/names/connections 四层模型；JSON/RDF/CSV 批量导出；API 支持。Digital Periegesis: Recogito annotation → Nodegoat LOD → CSV/GeoJSON |
| **可获取性** | 完全开放。每日 JSON dump: http://atlantides.org/downloads/pleiades/json/ |
| **PSI可计算性** | ⚠️ 中等偏低。Pleiades 是地理 gazetteer，非文本库；Digital Periegesis 是单文本（Pausanias）的深度标注，规模不足以独立支撑 PSI 时序。更适合作为 GSI 计算的地理基础层，而非独立第8域 |
| **学术认可度** | 极高（Pleiades为古代地理标准）；Digital Periegesis 新兴但方法论先进 |
| **与现有域独立性** | ❌ 低。Pleiades 已被现有古罗马/美索不达米亚域用作地理编码基础（v6.3 pleiades_cache.json 已存在） |

**结论**: Pleiades 是**基础设施层**而非独立域；Digital Periegesis 是**示范案例**而非大规模语料。

---

### 2.5 Parker Library on the Web (中世纪欧洲)

**基本信息**
- **URL**: https://parker.stanford.edu/parker/
- **运营方**: Corpus Christi College, Cambridge + Stanford University Libraries
- **许可**: CC BY-NC-ND (2018年后开放)

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | 556 digitized medieval & Renaissance manuscripts (6th–16th c.); 600+ total collection |
| **时间跨度** | 500 – 1,600 CE (~1,100 years) |
| **结构化程度** | 中等。每份手稿有详细目录学元数据（日期、地点、语言、体裁、 illumination）；IIIF manifest；但**无全文转录**（仅图像） |
| **可获取性** | 免费；IIIF API；图像可批量获取；但无文本批量下载 |
| **PSI可计算性** | ❌ 低。缺乏全文文本，无法直接计算 MMP/EMP/SFD；需先进行 OCR/HTR（手写体识别），技术难度极高；元数据可用于"手稿生产密度"代理，但非 PSI 核心指标 |
| **学术认可度** | 极高。最重要的中世纪英文手稿收藏之一，含《盎格鲁-撒克逊编年史》最早副本 |
| **与现有域独立性** | ✅ 极高。时间（中世纪）、空间（西北欧）、文化（基督教/日耳曼）与现有7域完全不重叠 |

**优势**: 填补巨大时间空白（500–1600 CE）、文明独立性最强、IIIF 标准兼容。  
**劣势**: **无全文文本**是致命缺陷；PSI 计算需先解决手写体文本识别（HTR），超出当前项目范围。

---

### 2.6 Sanskrit / GRETIL + Digital Corpus of Sanskrit (DCS)

**基本信息**
- **GRETIL URL**: http://gretil.sub.uni-goettingen.de/
- **DCS URL**: https://www.sanskrit-linguistics.org/dcs/
- **Sanskrit Library**: https://sanskritlibrary.org/
- **SARIT**: https://sarit.indology.info/
- **许可**:  varies (mostly academic free use)

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | GRETIL: ~800 texts; DCS: largest annotated corpus (Sandhi-split, morphological analysis); Sanskrit Voyager: 900+ texts from GRETIL+SARIT |
| **时间跨度** | Vedic (1500 BCE) – Classical (500 CE) (~2,000 years) |
| **结构化程度** | 中等。GRETIL 文本格式不统一（早期贡献者无统一标准）；DCS 有完整 morphological annotation；SARIT 采用 TEI-XML；但**历史年代元数据薄弱** |
| **可获取性** | 免费下载（纯文本/HTML）；但无统一 API；DCS 需在线查询 |
| **PSI可计算性** | ⚠️ 中等。文本量足够，但**历史编年文本比例低**（以宗教/哲学/文学为主）；**年代定位困难**（许多文本年代有争议）；缺乏地理 gazetteer 对应（无印度古代地理标准库如 Pleiades） |
| **学术认可度** | 高（印度学/梵文研究）；但数字人文基础设施较古典学落后 |
| **与现有域独立性** | ✅ 高。印度文明与中华、美索、罗马、欧洲完全独立 |

**优势**: 文明独立性最强、时间跨度大、DCS 有世界领先的梵文 NLP 标注。  
**劣势**: 历史编年文本少、年代元数据弱、地理编码缺失、数据分散在多个平台。

---

### 2.7 UCLA Encyclopedia of Egyptology (UEE)

**基本信息**
- **URL**: https://uee.ucla.edu/
- **运营方**: UCLA / eScholarship
- **许可**: 开放获取（CC-like）

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | ~500+ peer-reviewed articles (steady growth) |
| **时间跨度** | Predynastic – Roman Egypt (~3,100 BCE – 400 CE) |
| **结构化程度** | 高。每篇文章有：主题分类、时间标签、地理标签、关键词、参考文献；支持 Time Map 交互搜索 |
| **可获取性** | 免费在线；PDF 下载；但**无批量数据下载/API** |
| **PSI可计算性** | ❌ 低。百科全书是**二手学术综述**，非原始文本；文章数量不足以支撑十年级 PSI 时序；更适合作为知识库参考，而非独立计算域 |
| **学术认可度** | 极高。世界领先的埃及学在线资源，peer-reviewed |
| **与现有域独立性** | ✅ 高。古埃及文明完全独立 |

**结论**: UEE 是**高质量学术参考**，但数据类型（二手综述）和规模不适合作为 PSI 计算域。

---

### 2.8 DARMC (Digital Atlas of Roman and Medieval Civilizations)

**基本信息**
- **URL**: https://darmc.harvard.edu/
- **运营方**: Harvard University (Michael McCormick)
- **许可**: CC BY-NC-SA

**评估表**

| 维度 | 评估结果 |
|------|----------|
| **数据规模** | Dozens of data layers: Roman roads, ports, settlements, mints, climate, disease, etc. |
| **时间跨度** | 1 – 1,500 CE |
| **结构化程度** | 高。ESRI geodatabases; Excel/CSV download; WMS service |
| **可获取性** | 免费下载 (.xlsx, .csv); WMS/REST for GIS |
| **PSI可计算性** | ⚠️ 中等。纯地理/考古数据，无文本；可计算"定居点密度变化""道路网络连通性"等代理指标，但需重新设计 UPSI 操作化 |
| **学术认可度** | 极高。中世纪研究/罗马研究标准地理数据源 |
| **与现有域独立性** | ⚠️ 中等。与古罗马域地理重叠，但时间延伸至中世纪 |

**结论**: DARMC 是**地理基础设施**，适合作为 GSI 计算层，而非独立 PSI 域。

---

## 3. 综合评估矩阵

| 候选域 | 数据规模 | 时间跨度 | 结构化 | 可获取性 | PSI可算 | 学术认可 | 独立性 | 综合评分 |
|--------|----------|----------|--------|----------|---------|----------|--------|----------|
| **Perseus Greek** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **8.0/10** |
| **Seshat Global** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **8.3/10** |
| **ToposText** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | **7.0/10** |
| **Pleiades/Perieg.** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | **5.5/10** |
| **Parker Library** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **6.3/10** |
| **Sanskrit/GRETIL** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **6.5/10** |
| **UCLA Egyptology** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **5.8/10** |
| **DARMC** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **6.8/10** |

---

## 4. 推荐第8域

### 4.1 首选推荐：Seshat Global History Databank（全球历史复杂性域）

**推荐理由**（按优先级排序）：

1. **独立性最强**: Seshat 覆盖 30+ 自然地理区域（NGA），包括撒哈拉以南非洲、美洲（Cahokia、Valley of Oaxaca）、大洋洲（Chuuk Islands、Big Island Hawaii）、东南亚（Cambodian Basin）等现有7域**完全未触及**的文明。这是真正的"跨文明验证"，而非同一文明圈内的文本补充。

2. **时间跨度最大**: ~10,000 BCE – 1,900 CE，可与中华历史（618–1644）、美索不达米亚（2334–64 BCE）、罗马（753 BCE–476 CE）形成**时间互补**，验证 UPSI 在更长历史尺度上的稳健性。

3. **学术对话价值**: Seshat 的 "Social Complexity PC1" 与 UPSI 概念上相关（都测量社会政治压力/复杂性），但方法论完全不同（专家编码变量 vs. 文本语义+密度）。若两者在相同历史时期给出一致方向，将构成**方法三角验证**（methodological triangulation），极大提升 UPSI 的可信度。

4. **数据质量与透明度**: 每个编码值附带 narrative paragraph 和学术引用，可追溯、可质疑、可更新。Equinox-2020 数据集已通过 Zenodo DOI 永久存档。

5. **政策相关性**: Seshat 被用于测试"国家崩溃理论"（Turchin's cliodynamics），与 UPSI 的"文明稳定性预测"目标高度一致。

**整合方案**：
- 下载 Equinox-2020 CSV
- 筛选与现有7域**不重叠**的 NGA（如 Ghanaian Coast、Cahokia、Hawaii、Chuuk Islands）
- 将 Seshat 变量重新操作化为 UPSI 三维度：
  - **Material**: `polity_population` + `polity_territory` 变化率（对数差分）
  - **Fragmentation**: `hierarchical_levels` 波动 + `government_complexity` 变化
  - **Disengagement**: `information_systems` + `texts_publishing` + `sophistication_of_currency` 下降
- 按世纪聚合，计算 z-score 标准化后的 UPSI
- 与现有7域的 UPSI 进行跨域相关性分析

**预期验证事件**：
- Cahokia 的衰落（~1350 CE）
- 夏威夷王国统一前的政治波动（~1795 CE前）
- 加纳海岸的复杂社会兴起
- 吴哥帝国的扩张与收缩

**实施难度**: 中等。需重新设计 UPSI 操作化（因数据类型不同），但数据结构清晰，预计 2–3 周可完成原型。

---

### 4.2 次选推荐：Perseus Digital Library（古希腊域）

**推荐理由**：

1. **数据质量最高**: TEI-XML、CTS URN、批量下载、开放许可，是数字人文的"黄金标准"。
2. **PSI 计算最顺畅**: 与现有中华历史/古罗马域的文本密度方法完全一致，可直接复用代码。
3. **文明独特性**: 古希腊在民主制度、哲学思想、城邦政治等方面与罗马有本质差异，可提供"同圈不同质"的验证。

**整合方案**：
- 下载 canonical-greekLit + First1KGreek
- 按世纪/十年聚合文本（历史/编年体裁优先）
- 复用现有 v2.4 PSI pipeline：SFD（文本密度）+ MMP/EMP（LLM情感分析）+ GSI（Pleiades地理编码）
- 重点时期：Archaic Period (800–480 BCE) → Classical (480–323 BCE) → Hellenistic (323–31 BCE) → Roman Greece (31 BCE–330 CE)

**预期验证事件**：
- 伯罗奔尼撒战争（431–404 BCE）前的 PSI 下降
- 亚历山大帝国分裂后的城邦动荡
- 希腊化时期的"文化繁荣但政治碎片化"

**实施难度**: 低。预计 1–2 周可完成原型，代码复用率 >80%。

---

### 4.3 第三候选：Parker Library（中世纪欧洲域）

**推荐理由**：填补 500–1500 CE 时间空白；文明独立性最强。  
**主要障碍**: 无全文文本，需 HTR/OCR，技术门槛过高。建议作为 **v12 目标**，待手写体识别技术成熟后纳入。

---

## 5. 实施路线图

### Phase 1: Seshat 整合（第8域，4–6周）

| 周 | 任务 | 产出 |
|----|------|------|
| 1 | 下载 Equinox-2020；数据清洗；理解 codebook | 清洗后的 CSV + 变量映射表 |
| 2 | 设计 Seshat→UPSI 操作化方案；与现有7域对齐 | 操作化规格文档 |
| 3 | 编码实现：按 NGA+世纪 聚合 UPSI | Python 模块 + 单元测试 |
| 4 | 跨域验证：Seshat UPSI vs. 现有7域 UPSI 相关性 | 相关性矩阵 + 可视化 |
| 5 | 撰写验证报告；识别失败案例 | v11c 跨域验证报告 |
| 6 | 整合到 Dashboard / 论文图表 | 更新 v11 交付物 |

### Phase 2: Perseus Greek 整合（第9域，2–3周，可与 Phase 1 并行）

| 周 | 任务 | 产出 |
|----|------|------|
| 1 | 下载 canonical-greekLit + First1KGreek；解析 TEI-XML | 结构化语料库 |
| 2 | 复用 v2.4 pipeline 计算 Greek PSI | decade_psi_greek.json |
| 3 | 与古罗马域对比：Greek vs. Roman PSI 模式 | 对比分析报告 |

### Phase 3: 长期储备（v12+）

- **Parker Library**: 监控 HTR 技术进展（e.g., Transkribus 中世纪拉丁模型）
- **Sanskrit/GRETIL**: 与 Sanskrit Library 合作建立年代-地理元数据标准
- **古埃及**: 探索 UCLA Digital Library 的原始文本转录（如有）

---

## 6. 诚实边界与风险声明

1. **Seshat 非商业限制**: CC BY-NC-SA 许可意味着 UPSI 商业应用需额外授权。建议在论文中明确标注，并联系 Seshat 团队确认。
2. **Seshat 数据质量争议**: Beheim et al. (2019) 指出 Seshat 存在系统性编码偏差（如缺失数据被编码为"不存在"）。整合时需进行敏感性分析。
3. **Perseus 与罗马域重叠**: 若审稿人质疑"古希腊 vs. 古罗马"的独立性，需准备文明差异论证（语言、政治制度、文化认同）。
4. **Parker Library 无文本**: 当前技术条件下，中世纪手稿的批量 HTR 准确率不足以支撑 PSI 计算（拉丁手写体变异极大）。不建议在 v11 强行推进。
5. **梵文年代争议**: 许多 Sanskrit texts 的成书年代存在数百年争议（如 Mahabharata 的 layers），这将污染 PSI 时序的精确性。

---

## 7. 结论

基于实际搜索与访问结果，**推荐 Seshat Global History Databank 作为 UPSI 第8域**。它提供了现有7域完全缺失的全球视角、最大的时间跨度、最高的学术认可度，以及最强的文明独立性。虽然数据类型（结构化编码变量）与现有文本/金融域不同，但这恰恰是优势——它允许验证 UPSI 公式在**不同数据形态**上的稳健性，实现真正的"方法三角验证"。

**Perseus Digital Library（古希腊）** 作为第9域候选，在数据质量和计算便利性上最优，可作为与 Seshat 并行的快速验证通道。

**不推荐的域**（基于实际评估）：
- Pleiades / Digital Periegesis：规模不足，且 Pleiades 已被用作基础设施
- UCLA Egyptology：二手综述，非原始文本
- Parker Library：无全文，技术门槛过高
- Sanskrit/GRETIL：年代元数据薄弱，地理编码缺失

---

**报告完成**。下一步：等待项目负责人确认第8域选择，启动 Phase 1 实施。
