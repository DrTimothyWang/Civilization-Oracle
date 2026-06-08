# S2. CBDB Data Processing Pipeline

**Source**: `v4/cbdb_data_pipeline.py`, `v6/cbdb_psi_v6.py`  
**Status**: Source materials available  
**Assembly**: Copy docstrings and key functions; include data cleaning steps

---

## Content Outline

1. **CBDB v2.5 API access**
   - Endpoint: cbdb.fas.harvard.edu
   - A/B-tier record filtering (30,518 records)
   - Exclusion criteria: C-tier (unverified), D-tier (fragmentary)

2. **Data cleaning**
   - Date standardization (Chinese lunar → Gregorian)
   - Geographic coordinate assignment
   - Biographical record deduplication

3. **Decade aggregation**
   - 30-year rolling windows
   - Z-score normalization within dynasty
   - Missing data handling (linear interpolation for gaps < 50 years)

4. **Dynasty segmentation**
   - Tang (618–907): 31 decades
   - Northern Song early (960–1067): 11 decades
   - Northern Song late (1068–1127): 6 decades
   - Southern Song (1127–1279): 17 decades
   - Ming (1368–1644): 29 decades

5. **IPW correction**
   - Inverse Probability Weighting for elite bias
   - Geographic coverage adjustment
   - Record density by dynasty normalization

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v4/cbdb_data_pipeline.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v6/cbdb_psi_v6.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v6/data/psm_v6.json`

---

*Placeholder for SI Section 2. Assemble from source materials before submission.*
