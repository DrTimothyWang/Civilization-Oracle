# S21. Dashboard Architecture and Deployment

**Source**: `v14_迭代研究/04_dashboard_deploy/v14d_dashboard_repo/`, `v14_迭代研究/04_dashboard_deploy/v14d_deployment_report.md`  
**Status**: Source materials available  
**Assembly**: Document modular architecture, GitHub Actions workflow, API list

---

## Content Outline

1. **System architecture**
   - DataFetcher: 8 free public APIs
   - PSIEngine: real-time PSI computation
   - SPIEngine: real-time SPI computation
   - AlertSystem: threshold-based alerting
   - Renderer: HTML dashboard generation

2. **APIs consumed**
   - yfinance: 20 global assets
   - FRED: 11 US macro indicators
   - Jin10 MCP: real-time Chinese financial news
   - Tencent/Sina: 4 Chinese indices
   - Wikidata: political events (batch)
   - CBDB: historical biographies (batch)
   - CDLI/ORACC: cuneiform archives (batch)
   - Seshat: structured historical data (batch)

3. **Deployment**
   - GitHub Actions workflow (`.github/workflows/dashboard.yml`)
   - gh-pages hosting (zero cost)
   - MIT license
   - 35 KB HTML output

4. **Local testing**
   - 19/20 yfinance assets process correctly
   - 1 delisted asset falls back to simulated data
   - Test results: `06_dashboard/local_test_results.json`

5. **Configuration**
   - External config: `config/config.yaml`
   - Thresholds, asset lists, alert rules editable without code changes
   - Modular design: swap data sources without rewriting core logic

6. **Use cases**
   - Central bank monitoring (PBOC, FSB, BIS)
   - Emerging-market regulators (no Bloomberg required)
   - Academic research (real-time validation)
   - Personal finance (risk awareness)

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/04_dashboard_deploy/v14d_dashboard_repo/`
- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/04_dashboard_deploy/v14d_deployment_report.md`
- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/04_dashboard_deploy/v14d_local_test_results.json`
- `/Users/wangzr/Desktop/历史事件预测建模/v15_迭代研究/02_spi_dashboard/v15b_dashboard_v3.py`

---

*Placeholder for SI Section 21. Assemble from source materials before submission.*
