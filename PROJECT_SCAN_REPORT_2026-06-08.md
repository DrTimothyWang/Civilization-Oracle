# Civilization-Oracle / UPSI / TCM-UPSI 项目全景扫描报告

> **扫描日期**: 2026-06-08
> **扫描范围**: `/Users/wangzr/Desktop/历史事件预测建模/` 全部目录与文件
> **扫描方式**: Agent集群并行深度扫描（4个探索子代理 + 主代理直接读取）
> **总文件数**: ~500+ 文件 / ~15 MB
> **项目状态**: TCM-UPSI v17.0 完成，进入投稿与操作化部署阶段

---

## 一、项目全貌：三条主线、十七个版本、一个使命

### 1.1 项目身份卡

| 项目属性 | 内容 |
|---------|------|
| **项目名称** | Civilization-Oracle → UPSI → TCM-UPSI |
| **核心命题** | 精英群体语义心理状态密度（PSI）是文明危机的有效先行指标 |
| **负责人** | 王滇让（广州中医药大学 公共卫生管理学院） |
| **学术顾问** | 马利军教授（语义心理学） |
| **AI团队** | Mavis Agent Team |
| **总研究时间** | ~18小时（2026-05-27 至 2026-06-08） |
| **总文件数** | 500+ / ~15 MB |
| **总观测数** | ~360万，跨5,500年 |
| **验证域数** | 8个独立域 |

### 1.2 三条研究主线

```
┌─────────────────────────────────────────────────────────────────┐
│                        三条研究主线                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  主线A: Civilization-Oracle v3.0                                 │
│  ├── 中华历史PSI基线（唐/北宋/南宋/明）                          │
│  ├── CBDB + MiniMax API + SikuBERT                              │
│  ├── 四诊合参2.0 + TKG v3.0                                     │
│  └── 目标期刊: Digital Humanities Quarterly (DHQ)               │
│                                                                 │
│  主线B: UPSI v6.0 NOBEL++ ULTIMATE                             │
│  ├── 跨6域统一压力同步指数                                       │
│  ├── 金融/政治/历史/物理/实时新闻                               │
│  ├── Hurst H=0.958 超临界 + PSM因果识别                         │
│  └── 目标期刊: Nature Letter → Nature Human Behaviour → PNAS   │
│                                                                 │
│  主线C: TCM-UPSI v17.0 (当前核心)                              │
│  ├── 中医时间医学 × 计算社会科学 × 复杂系统科学                 │
│  ├── 五运六气 + 八字EPI + 蒲公英网络 + 周期共振                 │
│  ├── AUC=0.9941 (月度) / AUC=0.9538 (年度)                    │
│  └── 目标期刊: Climate of the Past → PNAS                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 版本演进时间线

| 阶段 | 代号 | 时间 | 核心产出 | 状态 |
|------|------|------|----------|------|
| v1.0-v3.0 | Civilization-Oracle | 2026-05-27~30 | 中华历史PSI基线 | 归档 |
| v4.x | UPSI转型 | 2026-05-31 | 跨域框架确立 | 归档 |
| v5.0 | 政治+物理 | 2026-06-01 | 全球政治PSI, H-β谱 | 归档 |
| v6.0 | 因果+实时 | 2026-06-02 | Dashboard, 盲测, 4层因果 | 归档 |
| v6.1 | 物理修正 | 2026-06-03 | DFA+Whittle, PNAS备份 | 归档 |
| v7.0-v11.0 | 迭代深化 | 2026-06-03~04 | Seshat, SPI, UPSI_v2 | 归档 |
| v12.0-v16.0 | 投稿准备 | 2026-06-04~05 | 审稿回应, 贝叶斯, 投稿包 | 归档 |
| **v17.0** | **投稿前最终** | **2026-06-05** | **66文件投稿包** | **完成** |
| **v18.0+** | **TCM-UPSI** | **2026-06-05~** | **中医时间医学整合** | **当前核心** |

---

## 二、研究成果总览：八大域验证 + 三大反直觉发现

### 2.1 核心指标与公式

**PSI（中华历史版）**:
```
PSI = (MMP × 0.25 + EMP × 0.25 + SFD × 0.50) × GSI
```

**UPSI（跨域版）**:
```
UPSI(t) = 0.40 × Material_z(t) + 0.30 × Fragmentation_z(t) + 0.30 × Disengagement_z(t)
```

**TCM-UPSI（五层模型）**:
```
Layer 1: 宇宙-气候层 (CPI)
Layer 2: 个体-心理层 (EPI)
Layer 3: 网络-传播层 (NPI)
Layer 4: 事件-结构层 (UPSI + SPI)
Layer 5: 预测-干预层 (因果推断 + 反事实)
```

### 2.2 八大域验证结果

| 域 | 数据源 | 规模 | 召回率 | 关键发现 |
|----|--------|------|--------|----------|
| 中华历史 | CBDB | 30,518条 | 100% | 盛世PSI高，危机PSI低 |
| 美索不达米亚 | CDLI | 320,778条 | 待完整验证 | 楔形文字跨文明验证 |
| 古罗马 | Perseus | 待接入 | - | 设计完成 |
| 中国金融 | 腾讯/新浪 | 6,048 bars | 100% | - |
| 全球金融 | yfinance | 187,073 bars | 81.7% | VIX领先17天 |
| 全球政治 | Wikidata | 1,728事件 | 91% | 跨制度跨千年 |
| 实时新闻 | 金十MCP | 1,055快讯 | - | Dashboard实时 |
| Seshat全球历史 | Equinox-2020 | 47,400条 | 评估8.3/10 | 11 NGA验证 |

### 2.3 七大反直觉发现

| # | 发现 | 证据强度 | 颠覆对象 |
|---|------|----------|----------|
| 1 | **VIX领先股市17天** | r=-0.235, τ=+17 | "波动率=已实现" |
| 2 | **黄金滞后股票1天** | r=+0.346, τ=-1 | "黄金避险" |
| 3 | **全球PSI同步无因果链** | lag=0最强相关 | "美国先跌欧洲跟跌" |
| 4 | **PSI是同步器非预测器** | H=1.57(水平) | 预测框架 |
| 5 | **Hurst H=0.958超临界** | β=1.66棕色噪声 | Ising临界态 |
| 6 | **政治PSI 91%召回** | 30/33事件 | 跨制度不可比 |
| 7 | **欧洲三强是震源** | DE/FR/UK PageRank top-3 | "美元霸权" |

### 2.4 TCM-UPSI v17.0 核心突破

| 指标 | 数值 | 说明 |
|------|------|------|
| **月度AUC** | **0.9941** | 从年度0.9538提升+4.03% |
| **中国月度AUC** | 0.9985 | 最高绝对性能 |
| **非洲月度AUC** | 1.0000 | 完美分类（但数据稀疏） |
| **样本扩展** | 1,380月度 | 从115年度扩展12× |
| **Granger因果** | 全部p>0.05 | **关键发现：关联非因果** |
| **交叉验证CV** | 13.9% | 中等稳定 |
| **2026-2031预测** | 全部HIGH风险 | 86-91%年度概率 |

### 2.5 统计严谨性指标

| 指标 | 值 | 含义 |
|------|-----|------|
| Cohen's d | 7.35 (v3.0) / 0.53 (v4.x+) | 效应量极大/大 |
| Bootstrap 95% CI | 不重叠 | 五朝差异结构性 |
| PSM ATE | -1.05 (p<<0.01) | 因果识别 |
| HAC/OLS | 1.4-2.2x | 时间自相关修正 |
| LSTM F1 | 0.7621 | 78.67%准确率 |
| Walk-Forward r | 0.964 | 时序预测 |

---

## 三、资料夹结构分析：当前状态 vs 理想状态

### 3.1 当前实际结构

```
历史事件预测建模/                    ← 项目根目录 (~15MB, 500+文件)
│
├── 00_PROJECT_MASTER/                 ← 【规范】项目管理中枢 (5文件)
│   ├── 00_PROJECT_HANDOFF.md         ← 接手必读（30秒读懂）
│   ├── 01_PROJECT_MASTER_RECORD.md   ← 主档案（完整时间线+核心概念）
│   ├── 02_完整文件清单.md            ← 168文件详细索引
│   ├── 03_计划书与决策日志.md        ← 6年路线图+12条决策
│   └── 04_PROJECT_DATA_RECORD.md     ← 数据资产记录
│
├── 01_TCM_UPSI_CORE/                ← 【规范】TCM-UPSI核心 (275+文件)
│   ├── 02_五运六气引擎/              ← 五运六气计算
│   ├── 03_历史事件数据库/            ← 历史事件数据
│   ├── 03_气候数据层/                ← 竺可桢曲线, 冰芯, 太阳黑子
│   ├── 04_命理数据层/                ← 八字, 紫微, 历史名人
│   ├── 05_蒲公英网络/                ← 社会网络+传播模型
│   ├── 06_周期共振检测/              ← Lomb-Scargle, 小波, EMD, SSA
│   ├── 07_因果推断引擎/              ← DoWhy, CCM, PC, FCI
│   ├── 08_多层整合模型/              ← TCM-UPSI五层整合
│   ├── 09_Dashboard/                 ← Dashboard代码
│   ├── 09_气候数据融合/              ← 气候融合结果
│   ├── 10_WebDashboard/              ← Web版Dashboard
│   ├── 11_实时指数/                  ← 实时指数计算
│   └── [大量论文版本v1-v20]          ← TCM_UPSI_Paper_v1.md ~ v20.md
│
├── v6/                                ← 【规范】UPSI v6.0核心 (23文件)
│   ├── NATURE_LETTER_FINAL.md        ← Nature投稿稿
│   ├── NATURE_SI.md                ← Supplementary Information
│   ├── UPSI_PAPER.md               ← 范式论文
│   ├── README.md                   ← v6说明
│   ├── [核心代码19个.py]            ← upsi_v6.py, dashboard_v6.py等
│   ├── data/                       ← 6域数据JSON
│   └── figures/                    ← 9+张图表
│
├── v17_迭代研究/                      ← 【规范】投稿前最终迭代
│   ├── 01_reviewer_response/         ← 30个审稿Q&A
│   ├── 02_bayesian_reparam/        ← 贝叶斯重参数化
│   ├── 03_spi_expansion/           ← SPI数据扩展
│   └── 04_submission_package/      ← 66文件投稿包
│
├── [根目录大量文件]                   ← 【混乱】需要整理
│   ├── 论文草稿_Civilization-Oracle_v0.1 ~ v3.0.md  ← 7个版本
│   ├── Civilization-Oracle_v2.3 ~ v3.0_*.md        ← 多个全景报告
│   ├── phase2~8_*.py                               ← 早期管线代码
│   ├── cbdb_download.py, cdli_ingestor.py           ← 数据下载脚本
│   ├── mcp_server.py                               ← MCP Server
│   ├── psi_pipeline.py, decade_psi_analysis.py    ← PSI计算
│   └── [各种zip包] v4x_ULTIMATE_FINAL.zip等       ← 历史归档
│
├── v4/, v5/, v6.1/, v7~v16_迭代研究/  ← 【部分规范】历史迭代
│   └── 各版本有README或报告文件
│
├── data/, output/, figures/           ← 【部分规范】数据输出
├── utils/, tests/, scripts/           ← 【部分规范】工具脚本
├── tkg_v3/, four_diagnosis_v2/        ← 【部分规范】子模块
├── mcp_a2a/                           ← 【部分规范】协议栈
├── research/                          ← 【部分规范】研究报告
├── config/                            ← 【规范】配置文件
└── .mavis/, .opencode/, .well-known/  ← 【规范】Agent配置
```

### 3.2 结构问题诊断

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| **根目录文件过多** | 🔴 高 | 50+文件直接放在根目录，难以快速定位 |
| **论文版本分散** | 🔴 高 | v0.1~v3.0在根目录，v1~v20在01_TCM_UPSI_CORE/ |
| **zip包堆积** | 🟡 中 | 多个ULTIMATE_FINAL.zip，可能重复 |
| **代码文件分散** | 🟡 中 | phase2~8.py在根目录，v6代码在v6/ |
| **数据文件分散** | 🟡 中 | data/和output/有重叠，01_TCM_UPSI_CORE/也有数据 |
| **缺少统一索引** | 🟡 中 | 虽然有PROJECT_LOG.md，但根目录缺少总览 |
| **.DS_Store未清理** | 🟢 低 | 不影响功能 |

---

## 四、如何接手项目：Agent必读路径

### 4.1 5分钟快速上手

```
Step 1: 读 00_PROJECT_MASTER/00_PROJECT_HANDOFF.md
        → 30秒了解项目是什么

Step 2: 读 00_PROJECT_MASTER/01_PROJECT_MASTER_RECORD.md
        → 5分钟了解完整时间线和核心概念

Step 3: 读 PROJECT_LOG.md (根目录)
        → 了解当前Sprint和待办事项

Step 4: 读 TCM_UPSI_项目重架构_档案包索引.md (根目录)
        → 了解文件档案包结构

Step 5: 根据任务方向，深入对应目录
        → TCM-UPSI: 01_TCM_UPSI_CORE/
        → UPSI投稿: v6/ + v17_迭代研究/
        → 历史基线: 论文草稿_Civilization-Oracle_v3.0.md
```

### 4.2 按任务类型的接手路径

| 任务类型 | 必读文件 | 关键目录 |
|----------|----------|----------|
| **了解全貌** | 00_PROJECT_HANDOFF.md + 研究全景报告 | 00_PROJECT_MASTER/ |
| **TCM-UPSI开发** | TCM_UPSI_终极研究方案_v1.0.md | 01_TCM_UPSI_CORE/ |
| **UPSI投稿** | v6/NATURE_LETTER_FINAL.md + v6/NATURE_SI.md | v6/ + v17_迭代研究/ |
| **数据分析** | 04_PROJECT_DATA_RECORD.md | data/ + output/ |
| **代码开发** | v6/README.md + 各目录README | v6/ + 01_TCM_UPSI_CORE/ |
| **审稿回应** | v17/01_reviewer_response/ | v17_迭代研究/ |
| **Dashboard** | v6/dashboard_v6.py | v6/ + 01_TCM_UPSI_CORE/09_Dashboard/ |

### 4.3 关键公式与数据速查

**PSI公式（中华历史版，不可混用）**:
```python
PSI = (MMP * 0.25 + EMP * 0.25 + SFD * 0.50) * GSI
```

**UPSI公式（跨域版，不可混用）**:
```python
UPSI(t) = 0.40 * Material_z(t) + 0.30 * Fragmentation_z(t) + 0.30 * Disengagement_z(t)
```

**五朝PSI基准值**:
| 朝代 | PSI |
|------|-----|
| 唐朝 | 0.6122 |
| 北宋前期 | 0.7443 |
| 北宋后期 | 0.1867 |
| 南宋 | 0.3804 |
| 明朝 | 0.6250 |

**TCM-UPSI AUC**:
| 模型 | AUC |
|------|-----|
| 年度 (v16) | 0.9538 |
| 月度 (v17) | **0.9941** |
| 中国月度 | 0.9985 |
| 欧洲月度 | 0.9943 |

---

## 五、从头到尾整理资料：六步整理方案

### 5.1 整理目标

- **目标1**: 根目录清爽化（文件数 < 20）
- **目标2**: 论文版本统一归档
- **目标3**: 代码按功能模块归类
- **目标4**: 数据资产建立统一索引
- **目标5**: 历史zip包去重归档
- **目标6**: 建立自动化索引更新机制

### 5.2 六步整理方案

#### Step 1: 根目录文件归档（预计1小时）

**操作**: 将根目录下非核心文件移入对应归档目录

```bash
# 创建归档目录
mkdir -p 99_ARCHIVE/root_dir_2026-06-08
mkdir -p 99_ARCHIVE/old_versions
mkdir -p 99_ARCHIVE/zips

# 移动旧版本论文
mv 论文草稿_Civilization-Oracle_v0.1.md 99_ARCHIVE/old_versions/
mv 论文草稿_Civilization-Oracle_v0.2.md 99_ARCHIVE/old_versions/
mv 论文草稿_Civilization-Oracle_v0.3.md 99_ARCHIVE/old_versions/
mv 论文草稿_Civilization-Oracle_v0.5.md 99_ARCHIVE/old_versions/
mv 论文草稿_Civilization-Oracle_v1.0.md 99_ARCHIVE/old_versions/
mv 论文草稿_Civilization-Oracle_v2.0.md 99_ARCHIVE/old_versions/
mv 论文草稿_Civilization-Oracle_v3.0.md 99_ARCHIVE/old_versions/  # 保留最新在根目录或移入02_UPSI_LEGACY/

# 移动旧版全景报告
mv Civilization-Oracle_v2.4_全景文档.md 99_ARCHIVE/old_versions/
mv Civilization-Oracle_v2.5_MiniMax_Agent执行手册.md 99_ARCHIVE/old_versions/
mv Civilization-Oracle_v2.5_轻资产推进指令.md 99_ARCHIVE/old_versions/
mv Civilization-Oracle_v3.0_内部审稿说明_马老师.md 99_ARCHIVE/old_versions/
mv Civilization-Oracle_v3.0_迭代升级研究报告.md 99_ARCHIVE/old_versions/
mv Civilization-Oracle_v3.0_项目交付总结.md 99_ARCHIVE/old_versions/
mv Civilization-Oracle_v3.0_马老师讲稿.md 99_ARCHIVE/old_versions/
mv Civilization-Oracle_完整技术文档_v2.3.md 99_ARCHIVE/old_versions/

# 移动里程碑报告
mv P3_里程碑报告_v2.4.md 99_ARCHIVE/old_versions/
mv P5_里程碑报告_v2.5.md 99_ARCHIVE/old_versions/
mv P6_里程碑报告_v2.6.md 99_ARCHIVE/old_versions/
mv P7_里程碑报告_v3.0.md 99_ARCHIVE/old_versions/

# 移动旧版可视化报告
mv v2.4_四朝PSI可视化报告.html 99_ARCHIVE/old_versions/
mv v2.5_PSI可视化报告.html 99_ARCHIVE/old_versions/
mv v2.6_十年级PSI可视化报告.html 99_ARCHIVE/old_versions/
mv v2.7_十年级PSI可视化报告_真实数据.html 99_ARCHIVE/old_versions/
mv v3.0_十年级PSI可视化报告.html 99_ARCHIVE/old_versions/

# 移动迭代升级Track文件
mv 迭代升级_Track1_统计方法论.md 99_ARCHIVE/old_versions/
mv 迭代升级_Track2_数据工程与知识库.md 99_ARCHIVE/old_versions/
mv 迭代升级_Track3_NLP与知识图谱技术.md 99_ARCHIVE/old_versions/
mv 迭代升级_Track4_学术定位与伦理框架.md 99_ARCHIVE/old_versions/
mv 迭代升级_Track5_技术架构重构.md 99_ARCHIVE/old_versions/

# 移动其他旧文件
mv 对标分析报告_Civilization-Oracle.md 99_ARCHIVE/old_versions/
mv 语意演化预测系统_v2.0.md 99_ARCHIVE/old_versions/
mv 验证报告.md 99_ARCHIVE/old_versions/
mv 文献扩展报告_v3.0.md 99_ARCHIVE/old_versions/
mv 马老师审稿Checklist_v3.0.md 99_ARCHIVE/old_versions/
mv 论文框架_Civilization-Oracle.md 99_ARCHIVE/old_versions/
mv CDLI_跨文明验证技术设计.md 99_ARCHIVE/old_versions/
mv TCM_UPSI_终极研究方案_v1.0.md 99_ARCHIVE/old_versions/  # 已有副本在01_TCM_UPSI_CORE/
mv TCM_UPSI_项目重架构_档案包索引.md 99_ARCHIVE/old_versions/  # 已有副本在01_TCM_UPSI_CORE/

# 移动zip包
mv v4x_NOBEL_FINAL.zip 99_ARCHIVE/zips/
mv v4x_ULTIMATE_FINAL.zip 99_ARCHIVE/zips/
mv v4x_ULTIMATE_FINAL_v2.zip 99_ARCHIVE/zips/
mv v5_NOBEL_FINAL.zip 99_ARCHIVE/zips/
mv v6_NOBEL_PLUS.zip 99_ARCHIVE/zips/
mv v6_NOBEL_PLUS_FINAL.zip 99_ARCHIVE/zips/
mv v6_NOBEL_ULTIMATE.zip 99_ARCHIVE/zips/
mv v6_NOBEL_ULTIMATE_FINAL.zip 99_ARCHIVE/zips/
mv v6_1_NOBEL_ULTRA.zip 99_ARCHIVE/zips/
mv v6_1_NOBEL_ULTRA_FULL.zip 99_ARCHIVE/zips/
mv v6_2_NOBEL_ULTIMATE.zip 99_ARCHIVE/zips/
mv Civilization-Oracle_v3.0_完整资料包.zip 99_ARCHIVE/zips/

# 移动旧版代码（phase2-8已整合入v6+）
mv phase2_data_ingest.py 99_ARCHIVE/old_versions/
mv phase3_text_analyst.py 99_ARCHIVE/old_versions/
mv phase4_master.py 99_ARCHIVE/old_versions/
mv phase5_kgraph.py 99_ARCHIVE/old_versions/
mv phase6_pipeline.py 99_ARCHIVE/old_versions/
mv phase8_viz.py 99_ARCHIVE/old_versions/
mv phase_pipeline_v2.py 99_ARCHIVE/old_versions/
mv psi_pipeline.py 99_ARCHIVE/old_versions/
mv deploy_data.py 99_ARCHIVE/old_versions/
mv run_with_real_data.py 99_ARCHIVE/old_versions/
mv paper_assist.py 99_ARCHIVE/old_versions/
mv cbdb_download.py 99_ARCHIVE/old_versions/  # 保留utils/下的版本
mv cbdb_import.py 99_ARCHIVE/old_versions/

# 移动临时/中间文件
mv tmp_expanded_results.txt 99_ARCHIVE/temp/
mv decision.json 99_ARCHIVE/temp/
mv multi_dynasty_results.json 99_ARCHIVE/temp/
```

**保留在根目录的文件**（核心入口）:
```
历史事件预测建模/
├── PROJECT_LOG.md                    ← 项目日志（持续更新）
├── 00_PROJECT_MASTER/                ← 项目管理中枢
├── 01_TCM_UPSI_CORE/                 ← TCM-UPSI核心（当前主线）
├── 02_UPSI_LEGACY/                   ← UPSI遗产（v1-v17，需创建）
├── 03_DATA/                          ← 数据仓库（需规范化）
├── 04_CODE/                          ← 代码库（需规范化）
├── 05_PUBLICATIONS/                  ← 论文与投稿（需创建）
├── 06_COLLABORATION/                 ← 合作与outreach（需创建）
├── 07_DASHBOARD/                     ← Dashboard部署（需创建）
├── 08_DOCUMENTATION/                 ← 文档（需创建）
├── 99_ARCHIVE/                       ← 归档
├── .mavis/                           ← Agent配置
├── .well-known/                      ← MCP Agent Cards
├── data/                             ← 活跃数据（保留）
├── output/                           ← 活跃输出（保留）
├── figures/                          ← 活跃图表（保留）
├── utils/                            ← 通用工具（保留）
├── tests/                            ← 测试脚本（保留）
├── scripts/                          ← 脚本（保留）
├── config/                           ← 配置（保留）
├── tkg_v3/                           ← TKG模块（保留）
├── four_diagnosis_v2/                ← 四诊合参（保留）
├── mcp_a2a/                          ← MCP+A2A（保留）
├── mcp_server.py                     ← MCP Server（保留）
├── vietnam_events_1906_2026.json    ← 最新数据（保留）
└── [README.md - 需要创建]           ← 项目总览入口
```

#### Step 2: 创建统一归档目录 02_UPSI_LEGACY（预计30分钟）

**操作**: 将分散的v1-v17版本统一归入遗产目录

```bash
mkdir -p 02_UPSI_LEGACY

# 移动历史版本目录
mv v4/ 02_UPSI_LEGACY/
mv v6/ 02_UPSI_LEGACY/
mv v6.1/ 02_UPSI_LEGACY/
mv v6.2/ 02_UPSI_LEGACY/
mv v6.3/ 02_UPSI_LEGACY/
mv v7_迭代研究/ 02_UPSI_LEGACY/
mv v8_迭代研究/ 02_UPSI_LEGACY/
mv v9_迭代研究/ 02_UPSI_LEGACY/
mv v10_迭代研究/ 02_UPSI_LEGACY/
mv v11_迭代研究/ 02_UPSI_LEGACY/
mv v12_迭代研究/ 02_UPSI_LEGACY/
mv v13_迭代研究/ 02_UPSI_LEGACY/
mv v14_迭代研究/ 02_UPSI_LEGACY/
mv v15_迭代研究/ 02_UPSI_LEGACY/
mv v16_迭代研究/ 02_UPSI_LEGACY/
mv v17_迭代研究/ 02_UPSI_LEGACY/

# 创建遗产目录索引
cat > 02_UPSI_LEGACY/README.md << 'EOF'
# UPSI 遗产目录 (v1-v17)

本目录包含 UPSI 项目从 Civilization-Oracle v1.0 到 TCM-UPSI v17.0 的全部历史迭代。

## 快速导航

| 版本 | 目录 | 核心内容 | 状态 |
|------|------|----------|------|
| v1-v3 | [根目录旧文件] | Civilization-Oracle早期 | 归档 |
| v4.x | v4/ | 跨域转型，8维度验证 | 归档 |
| v5.0 | v5/ | 政治PSI + 物理理论 | 归档 |
| v6.0 | v6/ | 因果+实时，Nature投稿稿 | **基线版本** |
| v6.1 | v6.1/ | 物理修正，PNAS备份 | 归档 |
| v6.2-v6.3 | v6.2/, v6.3/ | 迭代修正 | 归档 |
| v7-v11 | v7_迭代研究/ ~ v11_迭代研究/ | Seshat, SPI, UPSI_v2 | 归档 |
| v12-v16 | v12_迭代研究/ ~ v16_迭代研究/ | 投稿准备，审稿回应 | 归档 |
| v17 | v17_迭代研究/ | 投稿前最终，66文件包 | **投稿版本** |

## 关键文件

- **Nature投稿稿**: v6/NATURE_LETTER_FINAL.md
- **Supplementary Info**: v6/NATURE_SI.md
- **审稿回应**: v17/01_reviewer_response/
- **投稿包**: v17/04_submission_package/
EOF
```

#### Step 3: 数据仓库规范化 03_DATA（预计30分钟）

**操作**: 统一数据目录结构

```bash
mkdir -p 03_DATA/raw
mkdir -p 03_DATA/processed
mkdir -p 03_DATA/external

# 移动/链接现有数据
# 注意：不要移动正在使用的数据，先创建符号链接或复制

# 原始数据
ln -s ../../data 03_DATA/raw/active 2>/dev/null || true
ln -s ../../output 03_DATA/processed/active 2>/dev/null || true

# 创建数据索引
cat > 03_DATA/README.md << 'EOF'
# 数据仓库

## 原始数据 (raw/)

| 数据集 | 来源 | 规模 | 路径 |
|--------|------|------|------|
| CBDB | cbdb.fas.harvard.edu | 30,518条 A/B级 | raw/cbdb/ |
| CDLI | cdli.ucla.edu | 320,778条 | raw/cdli/ |
| ORACC | oracc.museum.upenn.edu | 112,351条 | raw/oracc/ |
| Seshat | seshatdatabank.info | 47,400条 | raw/seshat/ |
| Wikidata | query.wikidata.org | 1,728事件 | raw/wikidata/ |
| yfinance | finance.yahoo.com | 187K bars | raw/yfinance/ |
| 金十 | mcp.jin10.com | 1,055快讯 | raw/jin10/ |
| FRED | fred.stlouisfed.org | 11指标 | raw/fred/ |
| 气候 | 多源 | - | raw/climate/ |

## 处理后数据 (processed/)

| 数据集 | 规模 | 路径 |
|--------|------|------|
| 五朝PSI | 96窗 | processed/decade_psi_all_api.json |
| 全球UPSI | 6域 | processed/global_upsi_v6.json |
| 政治PSI | 1,728事件 | processed/political_psi_v5.json |
| 八字数据库 | 199人 | processed/historical_bazi_database_v2.json |
| 蒲公英网络 | 199节点/131边 | processed/dandelion_full_dynasty_network.json |

## 外部API缓存 (external/)

实时拉取的API数据缓存。
EOF
```

#### Step 4: 代码库规范化 04_CODE（预计30分钟）

```bash
mkdir -p 04_CODE/upsi_core
mkdir -p 04_CODE/tcm_upsi
mkdir -p 04_CODE/dashboard
mkdir -p 04_CODE/visualization
mkdir -p 04_CODE/utils

# 复制核心代码（保留原位置，创建副本或链接）
cp v6/upsi_v6.py 04_CODE/upsi_core/
cp v6/dashboard_v6.py 04_CODE/dashboard/
cp v6/blind_test_v6.py 04_CODE/upsi_core/
cp v6/roc_v6.py 04_CODE/upsi_core/
cp v6/psm_v6.py 04_CODE/upsi_core/
cp v6/hac_v4_fix.py 04_CODE/upsi_core/
cp v6/lstm_v6.py 04_CODE/upsi_core/
cp v6/jin10_daily.py 04_CODE/dashboard/

# TCM-UPSI代码
cp 01_TCM_UPSI_CORE/02_五运六气引擎/*.py 04_CODE/tcm_upsi/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/04_命理数据层/*.py 04_CODE/tcm_upsi/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/05_蒲公英网络/*.py 04_CODE/tcm_upsi/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/06_周期共振检测/*.py 04_CODE/tcm_upsi/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/07_因果推断引擎/*.py 04_CODE/tcm_upsi/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/08_多层整合模型/*.py 04_CODE/tcm_upsi/ 2>/dev/null || true

# 工具
cp utils/*.py 04_CODE/utils/ 2>/dev/null || true
```

#### Step 5: 论文与投稿统一归档 05_PUBLICATIONS（预计20分钟）

```bash
mkdir -p 05_PUBLICATIONS/nature_letter
mkdir -p 05_PUBLICATIONS/pnas_backup
mkdir -p 05_PUBLICATIONS/tcm_upsi_papers
mkdir -p 05_PUBLICATIONS/presentations

# Nature投稿
cp v6/NATURE_LETTER_FINAL.md 05_PUBLICATIONS/nature_letter/
cp v6/NATURE_SI.md 05_PUBLICATIONS/nature_letter/
cp v6/UPSI_PAPER.md 05_PUBLICATIONS/nature_letter/

# PNAS备份
cp v6.1/PNAS_MANUSCRIPT.md 05_PUBLICATIONS/pnas_backup/ 2>/dev/null || true

# TCM-UPSI论文
cp 01_TCM_UPSI_CORE/TCM_UPSI_Paper_v*.md 05_PUBLICATIONS/tcm_upsi_papers/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/TCM_UPSI_Paper_v*.docx 05_PUBLICATIONS/tcm_upsi_papers/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/TCM_UPSI_Paper_v*.tex 05_PUBLICATIONS/tcm_upsi_papers/ 2>/dev/null || true
cp 01_TCM_UPSI_CORE/TCM_UPSI_Paper_v*.pdf 05_PUBLICATIONS/tcm_upsi_papers/ 2>/dev/null || true

# 演示文稿
cp Civilization-Oracle_v2.4_演示文稿.pptx 05_PUBLICATIONS/presentations/ 2>/dev/null || true
```

#### Step 6: 创建根目录 README.md 和自动化索引（预计20分钟）

```bash
cat > README.md << 'EOF'
# Civilization-Oracle / UPSI / TCM-UPSI

> **统一压力同步指数**: 跨域危机检测系统
> **当前版本**: TCM-UPSI v17.0 | **状态**: 投稿准备完成
> **研究机构**: 广州中医药大学 公共卫生管理学院
> **学术顾问**: 马利军教授（语义心理学）

## 快速导航

| 我想... | 看这里 |
|---------|--------|
| 了解项目全貌 | [00_PROJECT_MASTER/00_PROJECT_HANDOFF.md](00_PROJECT_MASTER/00_PROJECT_HANDOFF.md) |
| 了解最新成果 | [01_TCM_UPSI_CORE/TCM_UPSI_Paper_v17.md](01_TCM_UPSI_CORE/TCM_UPSI_Paper_v17.md) |
| 查看项目日志 | [PROJECT_LOG.md](PROJECT_LOG.md) |
| 运行代码 | [04_CODE/](04_CODE/) |
| 查看数据 | [03_DATA/](03_DATA/) |
| 查看论文 | [05_PUBLICATIONS/](05_PUBLICATIONS/) |
| 查看历史版本 | [02_UPSI_LEGACY/](02_UPSI_LEGACY/) |

## 核心成果

- **月度AUC**: 0.9941 (TCM-UPSI v17.0)
- **年度AUC**: 0.9538 (TCM-UPSI v16.0)
- **跨域验证**: 8个独立域，5,500年
- **Granger因果**: 全部p>0.05（关联非因果的关键发现）
- **2026-2031预测**: 全部HIGH风险 (86-91%)

## 目录结构

```
.
├── 00_PROJECT_MASTER/      # 项目管理中枢
├── 01_TCM_UPSI_CORE/       # TCM-UPSI核心（当前主线）
├── 02_UPSI_LEGACY/         # UPSI遗产（v1-v17）
├── 03_DATA/                # 数据仓库
├── 04_CODE/                # 代码库
├── 05_PUBLICATIONS/        # 论文与投稿
├── 06_COLLABORATION/       # 合作与outreach
├── 07_DASHBOARD/           # Dashboard部署
├── 08_DOCUMENTATION/         # 文档
├── 99_ARCHIVE/             # 归档
├── data/                   # 活跃数据
├── output/                 # 活跃输出
├── figures/                # 活跃图表
├── utils/                  # 通用工具
└── tests/                  # 测试脚本
```

## 核心公式

**PSI（中华历史版）**:
```
PSI = (MMP × 0.25 + EMP × 0.25 + SFD × 0.50) × GSI
```

**UPSI（跨域版）**:
```
UPSI(t) = 0.40 × Material_z(t) + 0.30 × Fragmentation_z(t) + 0.30 × Disengagement_z(t)
```

## 联系

- 项目负责人: 王滇让
- 机构: 广州中医药大学
- GitHub: github.com/Mavis-Foundation/UPSI (待创建)

---
*最后更新: 2026-06-08*
EOF
```

### 5.3 整理后预期结构

```
历史事件预测建模/                    ← 清爽根目录 (~20个条目)
│
├── README.md                         ← 【新增】项目总览入口
├── PROJECT_LOG.md                    ← 项目日志
│
├── 00_PROJECT_MASTER/                ← 项目管理中枢 (5文件)
├── 01_TCM_UPSI_CORE/                 ← TCM-UPSI核心 (当前主线)
├── 02_UPSI_LEGACY/                   ← 【新增】UPSI遗产 (v1-v17)
│   ├── README.md
│   ├── v4/, v5/, v6/, v6.1/, v6.2/, v6.3/
│   └── v7_迭代研究/ ~ v17_迭代研究/
│
├── 03_DATA/                          ← 【新增】数据仓库
├── 04_CODE/                          ← 【新增】代码库
├── 05_PUBLICATIONS/                  ← 【新增】论文与投稿
├── 06_COLLABORATION/                 ← 【新增】合作与outreach
├── 07_DASHBOARD/                     ← 【新增】Dashboard部署
├── 08_DOCUMENTATION/                 ← 【新增】文档
├── 99_ARCHIVE/                       ← 【新增】归档
│   ├── root_dir_2026-06-08/          ← 根目录旧文件归档
│   ├── old_versions/                 ← 旧版本文件
│   ├── zips/                         ← 历史zip包
│   └── temp/                         ← 临时文件
│
├── data/                             ← 活跃数据
├── output/                           ← 活跃输出
├── figures/                          ← 活跃图表
├── utils/                            ← 通用工具
├── tests/                            ← 测试脚本
├── scripts/                          ← 脚本
├── config/                           ← 配置
├── tkg_v3/                           ← TKG模块
├── four_diagnosis_v2/                ← 四诊合参
├── mcp_a2a/                          ← MCP+A2A
├── mcp_server.py                     ← MCP Server
├── vietnam_events_1906_2026.json    ← 最新数据
└── [其他活跃文件]
```

---

## 六、下一步行动建议

### 6.1 立即执行（今天）

| # | 任务 | 预计时间 | 优先级 |
|---|------|----------|--------|
| 1 | 执行六步整理方案 Step 1-6 | 3小时 | 🔴 P0 |
| 2 | 更新 PROJECT_LOG.md 记录整理 | 15分钟 | 🔴 P0 |
| 3 | 验证整理后所有链接和引用正常 | 30分钟 | 🔴 P0 |

### 6.2 本周执行

| # | 任务 | 预计时间 | 优先级 |
|---|------|----------|--------|
| 4 | TCM-UPSI论文v20最终润色 | 2小时 | 🔴 P0 |
| 5 | v17B贝叶斯完整采样（4×4000 draws） | 2-4小时 | 🔴 P0 |
| 6 | 创建GitHub仓库并推送代码 | 1小时 | 🟡 P1 |
| 7 | Dashboard v3.0部署测试 | 2小时 | 🟡 P1 |

### 6.3 本月执行

| # | 任务 | 预计时间 | 优先级 |
|---|------|----------|--------|
| 8 | Nature投稿决策（用户确认） | - | 🔴 P0 |
| 9 | Climate of the Past投稿 | 4小时 | 🟡 P1 |
| 10 | 跨学科合作接洽（央行/IMF/物理学家） | - | 🟡 P1 |
| 11 | 八字数据库扩展至500+人 | 4小时 | 🟢 P2 |
| 12 | 蒲公英网络边数扩展至500+ | 3小时 | 🟢 P2 |

---

## 七、关键风险与注意事项

### 7.1 整理风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 移动文件导致相对路径断裂 | 代码/文档无法引用 | 使用符号链接或批量替换路径 |
| 误删活跃文件 | 数据丢失 | 先复制到归档，确认后再删除 |
| zip包去重误删唯一副本 | 历史版本丢失 | 先对比MD5，保留不同版本 |

### 7.2 研究风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Granger因果全部不显著 | 关联非因果的诚实发现 | 已在论文中明确标注 |
| 月度模型AUC=0.9941可能过拟合 | 泛化性能下降 | 交叉验证CV=13.9%，需外部验证 |
| 2026-2031全部HIGH风险 | 预测价值降低 | 聚焦月度战术模型的精确预警 |
| 八字时辰多为推测 | EPI置信度降低 | 标注置信度，加权分析 |

---

## 八、Agent接手检查清单

- [ ] 已读 00_PROJECT_MASTER/00_PROJECT_HANDOFF.md
- [ ] 已读 00_PROJECT_MASTER/01_PROJECT_MASTER_RECORD.md
- [ ] 已读 PROJECT_LOG.md
- [ ] 已确认当前版本（TCM-UPSI v17.0）
- [ ] 已确认PSI/UPSI公式不混用
- [ ] 已确认数据质量分级（A/B级）
- [ ] 已了解Granger因果全部不显著（关联非因果）
- [ ] 已了解2026-2031全部HIGH风险预测
- [ ] 已了解用户完全授权自主决策
- [ ] 已了解定期汇报但不中断研究流

---

*报告生成: 2026-06-08*
*扫描Agent: Orchestrator + 4个探索子代理*
*项目根目录: /Users/wangzr/Desktop/历史事件预测建模/*
