# S18. Seshat Variable Mapping and Validation

**Source**: `v14_迭代研究/01_seshat_prototype/v14a_seshat_psi_engine.py`, `v15_迭代研究/01_seshat_expansion/v15a_seshat_expansion.py`  
**Status**: Source materials available  
**Assembly**: Document 5 NGAs, 337 centuries, variable mapping, 75% recall

---

## Content Outline

1. **Seshat Equinox-2020 snapshot**
   - 374 polities, 136 variables, 47,400 records
   - 35+ Natural Geographic Areas (NGAs)
   - CC BY-NC-SA 4.0 license
   - Citation requirement included

2. **Selected NGAs (5)**
   - Upper Egypt (Africa): 2/2 crises detected
   - Latium (Europe): 2/2 crises detected
   - Susiana (Asia): 1/2 crises detected
   - Middle Yellow River Valley (Asia): 1/1 crises detected
   - Valley of Oaxaca (Americas): 0/1 crises detected
   - **Total: 6/8 (75%)**

3. **Variable mapping to UPSI dimensions**
   - Material: Polity population (log) + Polity territory (log) + Agricultural productivity (inverted)
   - Fragmentation: |ΔHierarchy levels| + |ΔGovernance sophistication| + |ΔMilTech index|
   - Disengagement: Information systems + Infrastructure + Full-time bureaucrats (inverted)

4. **Computation details**
   - 3-century rolling windows (matching Seshat's 100-year timestep)
   - Z-scoring within NGA
   - Missing value imputation: NGA-specific mean (up to 61% missing in some variables)
   - Interpolated values down-weighted by 0.5

5. **Validation results**
   - Recall: 75% (6/8)
   - Precision: 5.8% (many false positives from coarse 100-year timestep)
   - No parameter tuning: same 0.4/0.3/0.3 weights and −0.5 threshold

6. **Limitations**
   - Only 5 of 35+ NGAs tested
   - Coarse 100-year timestep generates many false positives
   - 61% missing data in some variables
   - Interpolation artifacts (`uniq = n` carry-forward values)
   - Proof-of-concept, not validated eighth domain

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/01_seshat_prototype/v14a_seshat_psi_engine.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v15_迭代研究/01_seshat_expansion/v15a_seshat_expansion.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v15_迭代研究/01_seshat_expansion/v15a_precision_analysis.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v13_迭代研究/01_seshat_domain/v13a_seshat_data_sample.json`

---

*Placeholder for SI Section 18. Assemble from source materials before submission.*
