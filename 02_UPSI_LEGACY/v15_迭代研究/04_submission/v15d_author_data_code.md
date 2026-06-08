# Author Contributions, Data Availability, and Code Availability

> **Manuscript**: A Cross-Domain Pressure Synchronization Index for Crisis Detection Across Civilizations
> **Version**: v15.0
> **Date**: 2026-06-05

---

## Author Contributions

**Wang Dianrang (王滇让)**¹: Conceptualization, methodology design, historical domain expertise, Chinese history data curation, manuscript writing, project supervision.

**Mavis Agent Team**²: Software engineering, data pipeline development, statistical analysis, machine learning implementation, visualization, cross-domain validation, Seshat integration, SPI framework development, UPSI_v2 prototype, Dashboard deployment, manuscript drafting and revision.

¹ Guangzhou University of Chinese Medicine, School of Public Health and Management
² Mavis AI Foundation

**Corresponding author**: Wang Dianrang (wangdianrang@gzhmu.edu.cn)

---

## Data Availability

All data used in this study are from **free public sources**:

| Domain | Source | URL | License | Records |
|--------|--------|-----|---------|---------|
| Chinese history | CBDB v2.5 | cbdb.fas.harvard.edu | Academic | 30,518 |
| Mesopotamia (CDLI) | CDLI GitHub | github.com/cdli-gh/data | Open | 320,778 |
| Mesopotamia (ORACC) | ORACC | oracc.museum.upenn.edu | Open | 112,351 |
| Ancient Rome | LLM-evaluated | N/A | N/A | 14 periods |
| Global politics | Wikidata SPARQL | query.wikidata.org | CC0 | 1,728 events |
| Global finance | yfinance | finance.yahoo.com | Public | 187,073 bars |
| Chinese finance | Tencent/Sina | web.ifzq.gtimg.cn | Public | 6,048 bars |
| News sentiment | Jin10 MCP | mcp.jin10.com | Public | 1,055 flashes |
| Macro indicators | FRED | fred.stlouisfed.org | Public | 11 series |
| COVID-19 | OWID | github.com/owid/covid-19-data | CC BY | 429,436 rows |
| **Seshat** | **Zenodo** | **doi.org/10.5281/zenodo.6642229** | **CC BY-NC-SA** | **47,400** |

**Processed data** (PSI time series, validation results, feature-engineered datasets) are available at the GitHub repository upon publication.

**Seshat-specific note**: The Seshat Databank is licensed under Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA 4.0). Our use is non-commercial academic research. All publications using Seshat data must include the citation: "This research employed data from the Seshat Databank (seshatdatabank.info) under Creative Commons Attribution Non-Commercial (CC By-NC SA) licensing."

---

## Code Availability

All code is available at **github.com/Mavis-Foundation/UPSI** upon publication.

The repository includes:

1. **PSI computation pipeline** (`psi_engine.py`): Domain-agnostic PSI calculator for historical, financial, and political data
2. **SPI computation module** (`spi_engine.py`): Sudden Pressure Indicator for burst-crisis detection
3. **UPSI_v2 classifier** (`upsi_v2.py`): Four-quadrant state-space crisis classifier
4. **Seshat integration** (`seshat_psi.py`): Seshat-to-UPSI variable mapping and computation
5. **Dashboard** (`dashboard/`): Cloud-deployable real-time monitoring system
   - GitHub Actions workflow (`.github/workflows/dashboard.yml`)
   - Modular architecture: DataFetcher / PSIEngine / SPIEngine / AlertSystem / Renderer
   - Configuration: `config/config.yaml`
6. **Validation scripts** (`validation/`): ROC, permutation test, PSM, HAC, Bayesian hierarchical model
7. **Visualization** (`viz/`): Phase portraits, quadrant timelines, alert tables
8. **Reproduction package**:
   - `reproduce.py`: One-command reproduction of all figures and tables
   - `requirements.txt`: Pinned dependencies
   - `Dockerfile`: Containerized environment
   - `README.md`: Step-by-step reproduction instructions

**Software versions**: Python 3.10, pandas 2.0, numpy 1.24, scikit-learn 1.3, PyTorch 2.0, PyMC 5.12, matplotlib 3.7, yfinance 0.2.

---

## Competing Interests

The authors declare no competing interests.

## Ethics Approval

Not applicable. This study uses publicly available historical and financial data. No human subjects research was conducted.

## Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The Mavis Agent Team contributed computational resources pro bono.

---

*Prepared for Nature Letter submission, v15.0*
