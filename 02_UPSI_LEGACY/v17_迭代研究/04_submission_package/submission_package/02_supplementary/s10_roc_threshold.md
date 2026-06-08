# S10. ROC Curves and Threshold Optimization

**Source**: `v6/figures/Figure16_ROC_Curves.png`, `v6/figures/Figure17_Threshold_F1.png`, `v6/data/roc_v6.json`  
**Status**: Source materials available  
**Assembly**: Include ROC curves for 3 domains; baseline vs feature-engineered AUC table

---

## Content Outline

1. **Baseline ROC AUC (PSI level only)**
   - Chinese finance: 0.608
   - Global finance: 0.573
   - Global politics: 0.515
   - Interpretation: near-random; confirms PSI is a poor *predictor*

2. **Feature-engineered ROC AUC**
   - Chinese finance: 0.733 (+0.125)
   - Global finance: 0.658 (+0.085)
   - Global politics: 0.621 (+0.107)
   - Interpretation: moderate discrimination; consistent with monitoring screen

3. **Feature importance (logistic regression coefficients)**
   - Top feature: rolling volatility σ (+0.456 to +0.511)
   - PSI level: −0.552 (politics)
   - d²PSI/dt²: +0.066 to +0.220

4. **Threshold optimization**
   - F1-maximizing threshold by domain
   - Sensitivity vs specificity trade-off
   - Domain-adaptive thresholds (future work)

5. **Walk-forward validation (planned)**
   - Training: 1927–2000
   - Test: 2001–2026
   - Out-of-sample AUC expected to be 5–10% lower than in-sample

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v6/figures/Figure16_ROC_Curves.png`
- `/Users/wangzr/Desktop/历史事件预测建模/v6/figures/Figure17_Threshold_F1.png`
- `/Users/wangzr/Desktop/历史事件预测建模/v6/data/roc_v6.json`
- `/Users/wangzr/Desktop/历史事件预测建模/v6/global_upsi_v6.py` (feature engineering code)

---

*Placeholder for SI Section 10. Assemble from source materials before submission.*
