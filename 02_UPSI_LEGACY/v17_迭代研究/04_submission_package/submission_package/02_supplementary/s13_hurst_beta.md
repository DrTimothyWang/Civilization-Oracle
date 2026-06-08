# S13. Hurst H and Power-Spectrum β Estimation

**Source**: `v6.1/h_beta_recheck.py`, `v6.1/data/h_beta_recheck_v61.json`  
**Status**: Source materials available  
**Assembly**: Document DFA and Whittle likelihood methodology

---

## Content Outline

1. **Detrended Fluctuation Analysis (DFA)**
   - 4th-order polynomial detrending
   - Scales: 4 to 1024 days
   - S&P 500 PSI (1927–2026): H = 1.5662 (95% CI [1.50, 1.63])
   - S&P 500 log returns: H = 0.4526 (95% CI [0.40, 0.50])

2. **Whittle likelihood estimation**
   - Power-spectrum exponent β
   - S&P 500 PSI: β = 4.00
   - 1/f⁴ long-memory signature

3. **fBm consistency check**
   - Prediction: β = 2H + 1 = 4.13
   - Observed: 4.00
   - Deviation: 3.2% (within measurement error)

4. **fGn rejection**
   - Prediction: β = 2H − 1 = 2.13
   - Observed: 4.00
   - Conclusion: rules out stationary fractional Gaussian noise

5. **R/S estimator bias correction**
   - v6.0 R/S estimate: H = 0.958 (superseded)
   - v6.1.1 DFA+Whittle: H = 1.5662 (current)
   - R/S known positive bias for long-memory processes

6. **Physical interpretation**
   - Presented as **descriptive statistical signature**, not physical theory
   - fBm price level + EMH return decomposition is classical result
   - No claims about underlying microstructural mechanisms

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v6.1/h_beta_recheck.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v6.1/data/h_beta_recheck_v61.json`
- `/Users/wangzr/Desktop/历史事件预测建模/v6.1/NATURE_SI_V61.md` (if exists)

---

*Placeholder for SI Section 13. Assemble from source materials before submission.*
