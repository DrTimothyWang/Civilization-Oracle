# S20. UPSI_v2 Quadrant Classifier

**Source**: `v14_迭代研究/03_upsi_v2/v14c_upsi_v2.py`, `v14_迭代研究/03_upsi_v2/v14c_upsi_v2_plots/`  
**Status**: Source materials available  
**Assembly**: Document four-quadrant taxonomy, domain-specific confidence weighting

---

## Content Outline

1. **Four-quadrant taxonomy**
   - Stable: PSI low, SPI low
   - Gradual Decline: PSI high, SPI low
   - Sudden Crisis: PSI low, SPI high
   - Accelerating Collapse: PSI high, SPI high

2. **Physical analogy**
   - PSI = temperature (system state)
   - SPI = dT/dt (rate of change)
   - Both necessary for complete monitoring

3. **Domain-specific confidence weighting**
   - w_SPI increases with exact-year data ratio
   - Modern finance: w_SPI = 0.8
   - Old Babylonian: w_SPI = 0.1
   - Formula: w_SPI = min(0.8, max(0.1, exact_year_ratio))

4. **Phase portraits**
   - Tang dynasty: 31 decades, 7 alerts
   - Northern Song: Jingkang catastrophe flagged as Sudden Crisis
   - Southern Song: Gradual Decline pattern
   - Ming: Gradual Decline pattern

5. **Quadrant transition rules**
   - Confirmation window: 2+ consecutive windows before alert
   - Rapid oscillation suppression: hysteresis band of 0.2σ
   - Dynasty-specific baseline calibration

6. **Validation**
   - Chinese history: 4/5 dynasties correctly classified in terminal phase
   - Finance: SPI flags COVID crash 6–10 days before PSI trough
   - Mesopotamia: Hammurabi fragmentation correctly classified as Sudden Crisis

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/03_upsi_v2/v14c_upsi_v2.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/03_upsi_v2/v14c_upsi_v2_demo.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/03_upsi_v2/v14c_upsi_v2_plots/` (phase portraits and quadrant legends)
- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/03_upsi_v2/v14c_upsi_v2_report.md`

---

*Placeholder for SI Section 20. Assemble from source materials before submission.*
