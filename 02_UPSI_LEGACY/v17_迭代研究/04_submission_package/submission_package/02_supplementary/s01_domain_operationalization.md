# S1. Domain Operationalization Table (8 Domains)

**Source**: `v4/bayesian_prediction_v4.py` (docstring), `v14_NATURE_MAIN.md` (Table 1)  
**Status**: Source materials available  
**Assembly**: Extract domain mapping table from manuscript Table 1; expand with full variable definitions

---

## Content Outline

1. **Table S1**: Full domain operationalization for all 8 domains
   - Columns: Domain, Material proxy, Fragmentation proxy, Disengagement proxy, Temporal resolution, Data source, N records
   - Domains: Chinese history, Mesopotamia (CDLI), Mesopotamia (ORACC), Ancient Rome, Chinese finance, Global finance, Global politics, News sentiment, Seshat

2. **Variable definitions**:
   - Material: economic production, subsistence, equity drawdown, war deaths, grain output
   - Fragmentation: realized volatility, revolution frequency, genre diversity, hierarchy volatility
   - Disengagement: volume turnover, elite exile rate, record density decline, information systems

3. **Normalization procedures**:
   - Finance: 252-day rolling z-score
   - History: 30-year rolling z-score
   - Politics: annual z-score
   - Seshat: 3-century rolling z-score

4. **Weight sensitivity analysis**:
   - Grid search results for (0.4, 0.3, 0.3) vs alternatives
   - F1 scores across 4 domains

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v4/bayesian_prediction_v4.py` (domain mapping docstrings)
- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/05_submission_final/v14_NATURE_MAIN.md` (Table 1)
- `/Users/wangzr/Desktop/历史事件预测建模/v6/global_upsi_v6.py` (operationalization code)

---

*Placeholder for SI Section 1. Assemble from source materials before submission.*
