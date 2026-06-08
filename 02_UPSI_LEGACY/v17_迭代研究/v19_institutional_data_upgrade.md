# v19 机构数据升级设计: 从免费API到专业数据栈

> **版本**: v19.0 (设计稿)  
> **日期**: 2026-06-05  
> **目标**: 设计从免费公共API到机构级数据源的升级路径  
> **状态**: 设计完成，待资源到位后实施

---

## 1. 当前数据栈的局限

| 域 | 当前源 | 局限 | 影响 |
|------|--------|------|------|
| 全球金融 | yfinance (免费) | 15分钟延迟，无盘前盘后，无期权/债券 | 实时性不足，资产类别受限 |
| 中国金融 | Tencent/Sina API | 不稳定，无Level 2，无衍生品 | 高频分析不可行 |
| 宏观指标 | FRED (免费) | 月度/季度，延迟1-3月 | 无法捕捉实时经济转折 |
| 新闻情绪 | Jin10 MCP | 仅中文金融新闻，无多语言 | 全球事件覆盖不足 |
| 美索不达米亚 | CDLI + ORACC | 已较完整，但缺乏地理信息系统 | 空间分析受限 |
| Seshat | Equinox-2020 (5 NGA) | 仅5/35+ NGA，100年时间步 | 精度低，覆盖窄 |

---

## 2. 机构级数据升级路径

### 2.1 金融数据: Bloomberg → Refinitiv → 免费替代

**Tier 1: Bloomberg Terminal (理想)**
- 实时全球资产 (股票/债券/外汇/商品/衍生品)
- 历史tick数据 (毫秒级)
- 新闻情绪 (Bloomberg NLP)
- 分析师预期 (EEPS)
- 成本: $24,000/年/终端
- 获取途径: 大学图书馆、实习机构、合作教授

**Tier 2: Refinitiv Eikon / Datastream (现实)**
- 日频全球资产 (1980s至今)
- 宏观数据 (IMF/World Bank/BIS集成)
- 新闻情绪 (Reuters News Analytics)
- 成本: $3,000-8,000/年
- 获取途径: 大学订阅 (许多研究型大学有)

**Tier 3: 免费升级路径 (立即可行)**

| 当前 | 升级 | 来源 | 质量提升 |
|------|------|------|----------|
| yfinance | Alpha Vantage (15 API calls/min) | alphavantage.co | 更稳定，更多指标 |
| yfinance | Tiingo (免费 tier) | tiingo.com | 实时价格，基本面数据 |
| FRED | World Bank Open Data | data.worldbank.org | 全球覆盖，更多变量 |
| Jin10 | GDELT Project | gdeltproject.org | 全球多语言新闻，1979至今 |
| Jin10 | RavenPack (学术试用) | ravenpack.com | 专业新闻情绪，实体识别 |

### 2.2 Seshat 数据: Equinox-2020 → Equinox-2024 → 完整NGA

**当前**: Equinox-2020, 5 NGA, 337 centuries, 8 crises

**升级路径**:

```
Phase 1 (立即, 免费):
  - 联系 Seshat 团队 (seshatdatabank.info)
  - 申请 Equinox-2024 预览版 (通常对学术合作开放)
  - 扩展至 15-20 NGA (覆盖更多文明)
  - 预期: 3-6 个月获取

Phase 2 (中期, 需合作):
  - 参与 Seshat 数据质量改进项目
  - 贡献中国/东亚 NGA 的精细化编码
  - 换取完整 35+ NGA 访问权
  - 预期: 6-12 个月

Phase 3 (长期, 需资助):
  - 申请 NSF/ERC 资助的 Seshat 扩展项目
  - 50+ NGA, 50 变量, 10,000+ years
  - 时间步降至 50 年 (当前 100 年)
  - 预期: 2-3 年
```

### 2.3 历史数据: CBDB v2024 → 完整版

**当前**: CBDB v2024 API, 30,518 A/B-tier records

**升级**:
- 下载完整 CBDB SQLite (约 500MB，含 C/D-tier)
- 地理信息系统集成 (GIS坐标)
- 社会关系网络数据 (亲属、师生、同僚)
- 获取途径: cbdb.fas.harvard.edu (免费注册)

### 2.4 美索不达米亚: ORACC → 完整语料库

**当前**: ORACC 112,351 records, 11 sub-projects

**升级**:
- CDLI 完整 catalog (154MB CSV, 已可用)
- ORACC 全部 20+ sub-projects
- 阿卡德语 NLP 工具 (MTAAC项目)
- 地理信息系统 (Ancient World Mapping Center)

---

## 3. 数据质量评估框架

### 3.1 五维评估体系

```python
class DataQualityScore:
    """
    五维数据质量评分 (0-100)
    """
    def __init__(self):
        self.dimensions = {
            'coverage': 0,      # 时间/空间/变量覆盖
            'granularity': 0,   # 时间分辨率
            'accuracy': 0,      # 与 ground truth 的一致性
            'completeness': 0,  # 缺失值比例
            'timeliness': 0,    # 数据延迟
        }
    
    def overall(self):
        return np.mean(list(self.dimensions.values()))
    
    def tier(self):
        s = self.overall()
        if s >= 80: return "A (机构级)"
        if s >= 60: return "B (研究级)"
        if s >= 40: return "C (探索级)"
        return "D (受限)"
```

### 3.2 当前数据质量评分

| 数据源 | Coverage | Granularity | Accuracy | Completeness | Timeliness | Overall | Tier |
|--------|----------|-------------|----------|--------------|------------|---------|------|
| yfinance | 70 | 90 | 85 | 95 | 60 | 80 | A |
| CBDB | 60 | 40 | 75 | 70 | 100 | 69 | B |
| CDLI | 80 | 30 | 70 | 85 | 100 | 73 | B |
| ORACC | 75 | 25 | 65 | 60 | 100 | 65 | B |
| Wikidata | 85 | 70 | 60 | 75 | 90 | 76 | B |
| Seshat (5 NGA) | 30 | 20 | 70 | 40 | 100 | 52 | C |
| Jin10 | 50 | 90 | 65 | 80 | 95 | 76 | B |
| FRED | 80 | 50 | 90 | 85 | 70 | 75 | B |

**目标**: 所有域达到 B+ (≥65)，核心金融域达到 A (≥80)

---

## 4. 实施路线图

### Phase 1: 免费升级 (0-3个月, $0)

| 任务 | 数据源 | 行动 | 预期提升 |
|------|--------|------|----------|
| 1 | Alpha Vantage | 注册API key，替换yfinance部分调用 | 稳定性+20% |
| 2 | GDELT | 下载1979-2024全球新闻事件数据库 | 新闻覆盖×10 |
| 3 | CBDB完整版 | 下载SQLite，本地查询 | 记录数×3 |
| 4 | CDLI完整版 | 下载154MB CSV | 记录数×1.5 |
| 5 | Seshat联系 | 发邮件申请Equinox-2024 | NGA×3 |

### Phase 2: 学术合作 (3-12个月, $0-5,000)

| 任务 | 合作方 | 行动 | 预期提升 |
|------|--------|------|----------|
| 1 | Refinitiv | 通过大学图书馆申请Eikon | 金融数据质量→A |
| 2 | RavenPack | 申请学术试用 | 新闻情绪专业化 |
| 3 | Seshat团队 | 正式合作申请，贡献编码 | NGA→20+, 时间步→50yr |
| 4 | ORACC团队 | 联系Steve Tinney (UPenn) | 语料库完整化 |
| 5 | CBDB团队 | 联系Peter Bol (Harvard) | 社会关系网络 |

### Phase 3: 资助申请 (12-36个月, $50,000-500,000)

| 资助来源 | 金额 | 用途 | 成功率 |
|----------|------|------|--------|
| NSF SBE | $300K | Seshat扩展+跨文明验证 | 15-20% |
| ERC Starting Grant | €1.5M | 欧洲文明数据+方法论 | 10-15% |
| 中国国家社科基金 | ¥200K | 中国历史精细化 | 20-25% |
| 腾讯/阿里研究基金 | $100K | 中国金融实时数据 | 30-40% |
| Bloomberg Data Grant | $50K | 金融数据终端 | 40-50% |

---

## 5. 数据治理与伦理

### 5.1 数据使用合规

| 数据源 | 许可 | 限制 | 合规措施 |
|--------|------|------|----------|
| yfinance | 免费 | 非商业 | 标注来源 |
| CBDB | CC BY-NC | 非商业 | 学术使用合规 |
| CDLI | 开放 | 引用要求 | 论文中致谢 |
| ORACC | 开放 | 非商业 | 学术使用合规 |
| Seshat | CC BY-NC-SA | 非商业, ShareAlike | 论文中致谢 |
| Wikidata | CC0 | 无 | 自由使用 |
| FRED | 公共领域 | 无 | 自由使用 |
| GDELT | 开放 | 引用要求 | 论文中致谢 |

### 5.2 数据偏见审计

```python
def audit_bias(data, domain):
    """
    系统性偏见审计
    """
    biases = {
        'survivorship': check_survivorship_bias(data),
        'elite': check_elite_bias(data),          # 精英记录过度代表
        'geographic': check_geographic_bias(data),  # 某些地区过度代表
        'temporal': check_temporal_bias(data),      # 近期数据过多
        'linguistic': check_linguistic_bias(data),  # 英语/汉语过度代表
    }
    return biases
```

**当前已知偏见**:
- CBDB: 精英偏见 (仅传记记录者)
- CDLI: 地理偏见 (集中于伊拉克南部)
- Seshat: 时间偏见 (近期NGA编码更详细)
- yfinance: 幸存者偏见 (仅现存资产)

**缓解策略**: 在论文中明确报告偏见，使用IPW校正，多源交叉验证

---

## 6. 技术架构升级

### 6.1 数据管道 v2.0

```
┌─────────────────────────────────────────────────────────────┐
│                    UPSI Data Pipeline v2.0                     │
├─────────────────────────────────────────────────────────────┤
│  Ingestion Layer                                             │
│  ├── Bloomberg API (实时)                                    │
│  ├── Refinitiv Eikon (日频)                                  │
│  ├── GDELT (新闻事件)                                        │
│  ├── Seshat API (历史结构)                                   │
│  └── CBDB SQLite (本地)                                      │
├─────────────────────────────────────────────────────────────┤
│  Quality Layer                                               │
│  ├── 五维质量评分                                            │
│  ├── 偏见审计                                                │
│  ├── 缺失值插补 (MICE, 贝叶斯)                              │
│  └── 异常值检测 (Isolation Forest)                          │
├─────────────────────────────────────────────────────────────┤
│  Computation Layer                                           │
│  ├── PSI Engine (GPU加速)                                    │
│  ├── SPI Engine (流式计算)                                   │
│  ├── Bayesian Hierarchical (PyMC + JAX)                      │
│  └── Walk-Forward OOS (Dask并行)                             │
├─────────────────────────────────────────────────────────────┤
│  Serving Layer                                               │
│  ├── REST API (FastAPI)                                      │
│  ├── Dashboard (React + WebSocket)                           │
│  ├── Alert System (Kafka + Slack/Email)                      │
│  └── Research Export (Jupyter + ArviZ)                       │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 计算资源需求

| 任务 | 当前 | 升级后 | 资源需求 |
|------|------|--------|----------|
| PSI计算 | CPU单核 | GPU并行 (CUDA) | NVIDIA T4 / A100 |
| 贝叶斯采样 | CPU 4核 | CPU 16核 / TPU | 云实例 (AWS c5.4xlarge) |
| Walk-Forward | 串行 | Dask并行 | 8-16 vCPU |
| 数据存储 | 本地JSON | PostgreSQL + S3 | 100GB-1TB |
| 实时Dashboard | 静态HTML | WebSocket流 | 云托管 (Vercel/Netlify) |

---

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 数据许可变更 | 中 | 高 | 多源备份，开源替代 |
| 合作方响应慢 | 高 | 中 | 同时联系多个合作方 |
| 资助申请失败 | 中 | 高 | 申请5+来源，免费路径保底 |
| 数据质量不达预期 | 中 | 中 | 先小规模验证再大规模采购 |
| 技术债务累积 | 高 | 中 | 模块化设计，定期重构 |

---

*设计完成。Phase 1可立即启动，Phase 2需等待v17投稿结果。*
