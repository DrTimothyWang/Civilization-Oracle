# S3. CDLI/ORACC SFD Proxy Methodology

**Source**: `v6.1/cdli_psi_analysis.py`, `v12_迭代研究/01_psi_improvement/v12a_meso_psi_engine.py`  
**Status**: Source materials available  
**Assembly**: Document SFD (Source Find Density) proxy formula; include 6/8 validation table

---

## Content Outline

1. **CDLI data**
   - 320,778 parsed records
   - 81 period-codes
   - Genre classification (administrative, legal, literary, royal, etc.)

2. **ORACC data**
   - 112,351 records across 11 sub-projects
   - 7 periods: Early Dynastic, Akkadian, Ur III, Old Babylonian, Middle Babylonian, Neo-Assyrian, Neo-Babylonian
   - 61.2% exact-year dating; 38.8% period-level assignment

3. **SFD proxy formula**
   - SFD_z = z-scored text density per window
   - GSI_cv_z = z-scored geographic-distribution coefficient of variation
   - PSI_proxy = 0.6 × SFD_z − 0.4 × GSI_cv_z

4. **Adaptive window sizes**
   - ≤150 years: 25-year windows
   - ≤300 years: 50-year windows
   - >300 years: 100-year windows
   - Trough threshold: mean − 0.5σ

5. **Validation table (6/8)**
   - Event-by-event pass/fail with reasoning
   - Umma decline: proxy limitation (bureaucratic intensification)
   - Hammurabi fragmentation: temporal resolution limit

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v6.1/cdli_psi_analysis.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v12_迭代研究/01_psi_improvement/v12a_meso_psi_engine.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v12_迭代研究/01_psi_improvement/v12a_event_validation.json`

---

*Placeholder for SI Section 3. Assemble from source materials before submission.*
