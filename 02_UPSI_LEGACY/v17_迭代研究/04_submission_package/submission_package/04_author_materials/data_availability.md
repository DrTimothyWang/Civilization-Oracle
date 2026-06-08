# Data Availability Statement

**Manuscript**: A Cross-Domain Pressure Synchronization Index for Crisis Detection Across Civilizations  
**Version**: v17.0  
**Date**: 2026-06-05

---

## Summary

All data used in this study are from **free public sources** with open or academic licenses. No proprietary or restricted data were used. Processed data (PSI time series, validation results, feature-engineered datasets) are available at the GitHub repository upon publication.

---

## Primary Data Sources

| Domain | Source | URL | License | Records | Access Date |
|--------|--------|-----|---------|---------|-------------|
| Chinese history | CBDB v2.5 | cbdb.fas.harvard.edu | Academic | 30,518 | 2024-06 |
| Mesopotamia (CDLI) | CDLI GitHub | github.com/cdli-gh/data | Open | 320,778 | 2024-06 |
| Mesopotamia (ORACC) | ORACC | oracc.museum.upenn.edu | Open | 112,351 | 2024-08 |
| Ancient Rome | LLM-evaluated | N/A | N/A | 14 periods | 2024-06 |
| Global politics | Wikidata SPARQL | query.wikidata.org | CC0 | 1,728 events | 2024-06 |
| Global finance | yfinance | finance.yahoo.com | Public | 187,073 bars | 2024-06 |
| Chinese finance | Tencent/Sina | web.ifzq.gtimg.cn | Public | 6,048 bars | 2024-06 |
| News sentiment | Jin10 MCP | mcp.jin10.com | Public | 1,055 flashes | 2026-01–06 |
| Macro indicators | FRED | fred.stlouisfed.org | Public | 11 series | 2024-06 |
| COVID-19 | OWID | github.com/owid/covid-19-data | CC BY | 429,436 rows | 2024-06 |
| **Seshat** | **Zenodo** | **doi.org/10.5281/zenodo.6642229** | **CC BY-NC-SA** | **47,400** | **2024-09** |

---

## Seshat-Specific Licensing

The Seshat Global History Databank is licensed under **Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA 4.0)**. Our use is non-commercial academic research. All publications using Seshat data must include the citation:

> "This research employed data from the Seshat Databank (seshatdatabank.info) under Creative Commons Attribution Non-Commercial (CC By-NC SA) licensing."

---

## Processed Data Availability

Processed data are available at **github.com/Mavis-Foundation/UPSI** upon publication. This includes:

1. **PSI time series** (CSV): Decade-level for Chinese history, daily for finance, year-level for politics
2. **Validation results** (JSON): Crisis detection tables, ROC curves, permutation test outputs
3. **Feature-engineered datasets** (CSV/Parquet): Rolling σ, derivatives, skewness, distance-to-minimum
4. **Dashboard data** (JSON): Real-time snapshots for reproducibility
5. **Seshat-derived UPSI** (CSV): Century-level PSI for 5 NGAs

---

## Large Raw Datasets

The following raw datasets are too large (>10 MB) to include in the repository but are freely accessible:

| Dataset | Size | Access |
|---------|------|--------|
| CDLI catalog CSV | 154 MB | github.com/cdli-gh/data |
| ORACC JSON dumps | ~2 GB | oracc.museum.upenn.edu |
| yfinance historical | ~500 MB | finance.yahoo.com (via API) |
| Seshat Equinox-2020 | ~50 MB | doi.org/10.5281/zenodo.6642229 |

---

## Data Sample Files

For reviewer inspection, small sample files are included in this package:

- `08_data_samples/chinese_history_psi.json` — Tang dynasty decade-level PSI (sample)
- `08_data_samples/mesopotamia_psi.json` — Mesopotamian validation summary
- `08_data_samples/global_finance_psi.json` — Blind test results (sample)
- `08_data_samples/seshat_psi.json` — Seshat NGA data sample (5 polities)

---

## Data Curation

All data were curated according to the following protocols:

1. **CBDB**: A/B-tier records only; excluded C-tier (unverified) and D-tier (fragmentary)
2. **CDLI**: Parsed JSON dumps; excluded records without period codes
3. **ORACC**: SFD proxy computation for period-level analysis; excluded records without genre classification
4. **Wikidata**: SPARQL query for war/revolution events; manual curation of 33 major episodes
5. **yfinance**: 20 global assets; excluded delisted assets (1 fallback to simulated data)
6. **Seshat**: Mean imputation for missing values (up to 61% in some variables); interpolated values down-weighted by 0.5

---

## Reproducibility

A **reproducibility package** is provided:

1. `reproduce.py`: One-command reproduction of all figures and tables
2. `requirements.txt`: Pinned dependencies
3. `Dockerfile`: Containerized environment
4. `README.md`: Step-by-step reproduction instructions

---

*Data availability statement prepared: 2026-06-05*
