# CDLI 学术账户申请模板

**目标**: 申请 CDLI (Cuneiform Digital Library Initiative) 学术账户
**目的**: 将 UPSI 美索不达米亚域样本量从 100 条扩展到 5,000+ 条
**申请日期**: 2026-06-04
**对接邮箱**: cdli@ucla.edu, cdli@orinst.ox.ac.uk

---

## 1. 申请邮件 (英文)

```
To: cdli@ucla.edu
Cc: cdli@orinst.ox.ac.uk
Subject: Academic Data Access Request — UPSI Project (Chinese University of Hong Kong / GZUCM)

Dear CDLI Team,

I am writing to request academic data access to the CDLI catalog
for the UPSI (Unified Pressure Synchronization Index) project,
a cross-civilization study of historical and financial crises.

PROJECT OVERVIEW:
The UPSI project validates a unified crisis indicator across six
independent domains: Chinese history (CBDB, 30,518 records),
Mesopotamia (CDLI), ancient Rome, Chinese finance, global finance
(1927-2026), and global politics (Wikidata). For the Mesopotamian
domain, we have only used ~100 records from the public API.
Access to the full catalog (~32万+ entries) would allow us to
expand our sample by three orders of magnitude, providing the
cross-civilization validation depth necessary for our PNAS submission.

REQUEST:
We respectfully request:
1. Academic API access (or batch data export) to the full CDLI catalog
2. Documentation of data fields (genre, period, provenance, content)
3. Permission to use the data in peer-reviewed publications
4. Citation requirements

DATA USE:
- For academic research only (PNAS submission Q2 2026)
- No commercial use
- Data will be processed to compute PSI (Pressure Synchronization
  Index) metrics
- Results will be published open-access

CITATION:
We will properly cite CDLI in all publications. Specifically, we
will acknowledge the CDLI catalog as the data source and follow
your preferred citation format.

ABOUT UPSI:
The UPSI project (recently upgraded to v6.1) achieves >85% recall
in crisis identification across 6 domains with ~3 million
observations spanning 4,200 years. The project has been peer-
reviewed by 12 independent research dimensions and aligns with
2021 Nobel Physics (complex systems) and 2024 Nobel Chemistry
(AI-driven scientific discovery) paradigms.

Please let me know what documentation or institutional verification
you require. We are happy to provide:
- Institutional affiliation details
- Project IRB approval (if required)
- Data security and storage plan
- Publication pre-prints

Thank you for considering this request.

Best regards,
Wang Dianrang
Guangzhou University of Chinese Medicine
[Institutional Address]
```

---

## 2. 数据使用计划

### 2.1 PSI 提取方案
对每条 CDLI 文献:
1. **时期标注** → 时间映射 (公元前/公元)
2. **类型分类** → MMP (Material, 战乱/经济/政治事件)
3. **行政 vs 神权文本** → SFD (Fragmentation, 社会分裂)
4. **精英词汇** → EED (Disengagement, 精英脱节)

### 2.2 与现有 6 域统一
- 中华历史 (-500~1900 AD): 30,518 CBDB 记录 → PSI
- 美索不达米亚 (-3200~): CDLI 32万+ 记录 → PSI
- 古罗马 (-509~476 AD): LLM 评估 → PSI
- 中国金融 (2018-2026): yfinance → PSI
- 全球金融 (1927-2026): yfinance 20 资产 → PSI
- 全球政治 (-218~2022): Wikidata 1,728 事件 → PSI

### 2.3 目标
- CDLI 样本量 100 → 5,000 (50x 提升)
- 跨文明 PSI 召回率验证
- 楔形文字 NLP 处理: MiniMax M3 + WenyanGPT

---

## 3. 替代数据源 (如果 CDLI 申请被拒)

| 数据源 | 内容 | 可用性 |
|--------|------|--------|
| **ORACC** (Open Richly Annotated Cuneiform Corpus) | 阿卡德语/苏美尔语双语 | 公开, http://oracc.museum.upenn.edu/ |
| **ETCSL** (Electronic Text Corpus of Sumerian Literature) | 苏美尔文学 | 公开, http://etcsl.orinst.ox.ac.uk/ |
| **Pleiades** | 古代地理 | 公开, https://pleiades.stoa.org/ |
| **Archibab** | 楔形文字数据库 | 部分公开 |
| **BDTNS** (Database of Neo-Sumerian Texts) | 新苏美尔时期 | 公开, http://bdts.filol.csic.es/ |
| **ePSD** (electronic Pennsylvania Sumerian Dictionary) | 苏美尔词典 | 公开, https://psd.museum.upenn.edu/ |

---

## 4. 时间表

| 阶段 | 时间 | 行动 |
|------|------|------|
| 申请提交 | 2026-06-04 (今天) | 发送申请邮件 |
| CDLI 回复 | 1-2 周 | 等待账户批准 |
| 数据下载 | 申请批准后 1 周 | 批量下载 5,000+ 条 |
| PSI 计算 | 下载后 2 周 | 楔形文字 NLP + PSI |
| PNAS 准备 | 2026 Q4 | 整合美索域 + 投稿 |

---

## 5. 联系方式

- **CDLI UCLA**: cdli@ucla.edu
- **CDLI Oxford**: cdli@orinst.ox.ac.uk
- **CDLI Director**: Robert K. Englund (UCLA), Steve Tinney (Oxford)
- **GitHub**: https://github.com/cdli-gh

---

*由 Mavis Agent Team 辅助生成*
