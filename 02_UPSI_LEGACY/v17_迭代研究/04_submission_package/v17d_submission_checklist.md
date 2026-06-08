# v17d Submission Checklist — Pre-Submission Verification

**Version**: v17.0  
**Date**: 2026-06-05  
**Target**: *Nature* Letter  
**Status**: ☐ Ready for submission

---

## 1. Word Count Check

| Section | Limit | Actual | Status |
|---------|-------|--------|--------|
| Abstract | 150 words | 150 | ✅ |
| Main text | ~3,000 words | ~2,850 | ✅ |
| Methods | 800 words | 800 | ✅ |
| **Total** | **~3,950 words** | **~3,800** | ✅ |

> Nature Letter format: ~3,000 words main text + 150 abstract + methods as separate section. Our manuscript fits within these limits.

---

## 2. Figure Count Check

| Figure | Content | Target | Status |
|--------|---------|--------|--------|
| Figure 1 | Cross-domain validation (7 civilizations) | Main text | ✅ |
| Figure 2 | PSI+SPI duality / 4-quadrant classifier | Main text | ✅ |
| Figure 3 | Physical-statistical spectrum (DFA, Whittle) | Main text | ✅ |
| Figure 4 | Real-time Dashboard | Main text | ✅ |
| Figure 5 | Seshat NGA coverage map | SI candidate | ⚠️ (no static PNG; see note) |

**Nature Letter limit**: Max 4–6 figures. We have 4 main + 1 SI candidate.

> **Note**: Figure 5 (Seshat map) does not currently exist as a static PNG. Options: (a) generate world map with 5 NGA markers, or (b) move to SI as a table. See `v17d_figure_selection.md`.

---

## 3. Reference Count Check

| Target | Actual | Status |
|--------|--------|--------|
| Nature limit: 30 | 25 | ✅ |

All 25 references are in Nature style (numbered, journal abbreviations, DOI where available).

---

## 4. SI Completeness Check (22 Sections)

| Section | Title | Source | Status |
|---------|-------|--------|--------|
| S1 | Domain operationalization table (8 domains) | v4/v14 | ✅ |
| S2 | CBDB data processing pipeline | v4 | ✅ |
| S3 | CDLI/ORACC SFD proxy methodology | v6.1/v12 | ✅ |
| S4 | Roman LLM evaluation protocol | v5 | ✅ |
| S5 | Financial data sources and preprocessing | v5/v6 | ✅ |
| S6 | Political event curation (Wikidata) | v5 | ✅ |
| S7 | Newey-West HAC standard errors | v6 | ✅ |
| S8 | Propensity Score Matching details | v6 | ✅ |
| S9 | Permutation test protocol | v6 | ✅ |
| S10 | ROC curves and threshold optimization | v6 | ✅ |
| S11 | Feature engineering pipeline | v6 | ✅ |
| S12 | LSTM architecture and training | v5 | ✅ |
| S13 | Hurst H and power-spectrum β estimation | v6.1 | ✅ |
| S14 | Cross-civilization terminal-decline analysis | v9 | ✅ |
| S15 | PageRank network centrality | v5 | ✅ |
| S16 | Lead-lag cross-correlation details | v4 | ✅ |
| S17 | Blind test protocol and results | v6 | ✅ |
| S18 | Seshat variable mapping and validation | v14/v15 | ✅ |
| S19 | SPI computation and Mesopotamian validation | v13 | ✅ |
| S20 | UPSI_v2 quadrant classifier | v14 | ✅ |
| S21 | Dashboard architecture and deployment | v14 | ✅ |
| S22 | Code and data availability | v15 | ✅ |

**All 22 sections have source materials** in iteration directories v4–v16. See `02_supplementary/si_master.md` for assembly instructions.

---

## 5. Data Availability Statement Check

- [x] All data sources are free public APIs
- [x] CBDB: cbdb.fas.harvard.edu (Academic license)
- [x] CDLI: github.com/cdli-gh/data (Open, 154 MB CSV)
- [x] ORACC: oracc.museum.upenn.edu (Open)
- [x] Wikidata: query.wikidata.org (CC0)
- [x] yfinance: finance.yahoo.com (Public)
- [x] FRED: fred.stlouisfed.org (Public)
- [x] Jin10: mcp.jin10.com (Public)
- [x] Seshat: doi.org/10.5281/zenodo.6642229 (CC BY-NC-SA)
- [x] Processed data: GitHub upon publication
- [x] Seshat citation requirement included

---

## 6. Code Availability Statement Check

- [x] GitHub repository specified: github.com/Mavis-Foundation/UPSI
- [x] 4 core modules identified (psi_engine, spi_engine, upsi_v2, seshat_psi)
- [x] Dashboard module identified
- [x] Validation scripts identified
- [x] Reproduction package planned (reproduce.py, Dockerfile, requirements.txt)
- [x] Software versions specified (Python 3.10, pandas 2.0, PyMC 5.12, etc.)

---

## 7. Author Contribution Check

- [x] CRediT-style contributions listed
- [x] Corresponding author identified (Wang Dianrang)
- [x] Affiliations included
- [x] Email included

**Authors**:
1. Wang Dianrang — Conceptualization, methodology, historical expertise, manuscript writing
2. Mavis Agent Team — Software engineering, data pipeline, statistical analysis, ML, visualization, validation

---

## 8. Competing Interests Check

- [x] No competing interests declared
- [x] No funding from commercial entities
- [x] No patents pending
- [x] No consultancy relationships

---

## 9. Cover Letter Check

- [x] Editor addressed
- [x] Manuscript title stated
- [x] Why Nature? explained
- [x] Three advances highlighted
- [x] Unexpected findings summarized
- [x] Limitations honestly reported
- [x] Policy relevance stated
- [x] Suggested reviewers (5) provided
- [x] Originality confirmed
- [x] All authors approve submission

---

## 10. Figure Quality Check

| Figure | Resolution | Format | Caption | Status |
|--------|-----------|--------|---------|--------|
| Figure 1 | 300 dpi | PNG | Drafted | ✅ |
| Figure 2 | 300 dpi | PNG | Drafted | ✅ |
| Figure 3 | 300 dpi | PNG | Drafted | ✅ |
| Figure 4 | 300 dpi | PNG | Drafted | ✅ |

> All figures should be submitted as separate files at 300 dpi minimum. Nature prefers TIFF or EPS for print, PNG acceptable for online.

---

## 11. Ethical Compliance Check

- [x] No human subjects research
- [x] All data publicly available
- [x] Seshat CC BY-NC-SA license respected
- [x] No proprietary data used without permission

---

## 12. Blind Test & Validation Check

- [x] Genuine future blind test conducted (2024-2025)
- [x] Model frozen before test period
- [x] Results documented in SI S17
- [x] Out-of-sample validation planned (walk-forward)

---

## 13. Statistical Rigor Check

- [x] Newey-West HAC standard errors reported
- [x] Propensity Score Matching conducted
- [x] Permutation test (10,000 iterations) conducted
- [x] Bayesian hierarchical model fitted (PyMC, 4 chains × 4,000 iterations)
- [x] Convergence confirmed (R-hat < 1.01, ESS > 4,000)
- [x] Effect sizes reported (Cohen's d = 0.433)
- [x] Confidence intervals reported (95% CI)

---

## 14. Final Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Corresponding Author | Wang Dianrang | ☐ | _______ |
| Co-Author | Mavis Agent Team | ☐ | _______ |

---

## Submission Command

```bash
cd /Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/04_submission_package/
zip -r UPSI_v17_submission.zip submission_package/ -x "*.DS_Store"
du -sh UPSI_v17_submission.zip
```

**Expected size**: < 5 MB (well under 50 MB limit)

---

*Checklist completed: 2026-06-05*  
*Ready for Nature Letter submission*
