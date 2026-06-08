# Supplementary Materials Index

## Overview

This document provides a complete index of all supplementary materials (SI S1–S15) accompanying the manuscript **"TCM-UPSI: A Machine Learning Framework for Historical Crisis Risk Assessment Integrating Traditional Chinese Medicine Cyclical Theory and Climate Indices"** submitted to *Climate of the Past*.

---

## SI S1: WuYun-LiuQi Cycle Computation Details

**File**: `SI_S1_WuYun_LiuQi_Computation.pdf`

**Contents**:
- Complete algorithm for computing the 60-year WuYun (五运) cycle from sexagenary year stems and branches
- 6-phase LiuQi (六气) monthly assignment rules based on solar terms (节气)
- Excess (太过) and Deficiency (不及) determination from stem dominance
- Conversion tables: Gregorian year → Stem-Branch → WuYun element → Excess/Deficiency
- LiuQi phase calendar: month → solar term → climatic phase (厥阴风木, 少阴君火, etc.)
- Python implementation pseudocode and validation against classical *Huangdi Neijing* references

**Relevance**: Ensures reproducibility of the core cyclical features used in the machine learning models.

---

## SI S2: Historical Event Database Schema and Curation Protocol

**File**: `SI_S2_Event_Database_Schema.pdf`

**Contents**:
- JSON schema for `historical_events_v21.json`
- Severity scoring rubric (1–10 scale) with exemplar events
- Geographic coordinate assignment methodology
- Temporal bound determination (start month, end month, peak severity month)
- Event categorization taxonomy (conflict, disaster, financial, epidemic, revolution)
- Curation workflow: source selection → event identification → severity assignment → cross-validation
- Inter-rater reliability statistics (if multiple coders)
- Blinded re-collection protocol for bias assessment

**Relevance**: Documents the data generation process and enables independent replication or extension.

---

## SI S3: Complete Feature Engineering Specifications

**File**: `SI_S3_Feature_Engineering.pdf`

**Contents**:
- Annual feature set (15 features): detailed definitions, computation formulas, and encoding schemes
- Monthly feature set (34 features): detailed definitions, computation formulas, and encoding schemes
- Event month assignment rules: historical seasonality mapping (wars → summer, revolutions → spring/autumn, etc.)
- Cyclical encoding: sin/cos transformation for month and WuYun phase
- Rolling window specifications for crisis counts (3-month, 6-month, 12-month)
- Lag structure: 1/2/3-year lags (annual) and 1/2/3/6/12-month lags (monthly)
- Feature correlation matrix and multicollinearity assessment (VIF)

**Relevance**: Enables exact reproduction of the model input features.

---

## SI S4: Model Hyperparameters and Training Protocols

**File**: `SI_S4_Model_Hyperparameters.pdf`

**Contents**:
- Random Forest hyperparameters: n_estimators, max_depth, min_samples_split, min_samples_leaf, max_features, bootstrap
- Hyperparameter tuning methodology: grid search vs. random search, cross-validation strategy
- Train–test split specifications: temporal split at 2000, alternative splits explored
- Class imbalance handling: class_weight, SMOTE evaluation (rejected due to temporal leakage risk)
- Feature importance computation: mean decrease in impurity (MDI) vs. permutation importance
- LSTM benchmark architecture: layer dimensions, activation functions, dropout rates, optimizer, learning rate schedule
- Training convergence diagnostics: loss curves, validation curves

**Relevance**: Documents model configuration to ensure reproducibility.

---

## SI S5: Complete Granger Causality Test Results

**File**: `SI_S5_Granger_Causality_Results.pdf`

**Contents**:
- Full F-statistic tables for all 12 causal directions tested
- Lag selection criteria: AIC, BIC, HQIC comparison for 1–5 year lags
- Residual diagnostics: Ljung-Box tests for autocorrelation, Jarque-Bera tests for normality
- Robustness checks: alternative lag structures (1–10 years), subsample tests (pre-1950, post-1950)
- Nonlinear Granger causality: Hiemstra-Jones test results (if conducted)
- Instantaneous causality tests (if conducted)
- Power analysis: post-hoc power for detecting medium effect sizes

**Relevance**: Provides complete transparency for the central negative finding (all Granger tests non-significant).

---

## SI S6: External Validation Detailed Results

**File**: `SI_S6_External_Validation_Results.pdf`

**Contents**:
- UCDP/PRIO validation: year-by-year predicted vs. observed conflict counts (1946–2023)
- UCDP feature importance breakdown: WuYun vs. climate vs. temporal contributions
- Earthquake validation (≥ M7): confusion matrix, ROC curve, precision-recall curve
- Epidemic validation: full chi-square test details, expected vs. observed counts by WuYun element
- Event definition mismatch analysis: systematic comparison of internal DB vs. UCDP coding rules
- Sensitivity analysis: varying severity thresholds, geographic subsets, time windows

**Relevance**: Documents the generalization failure and supports the selection bias conclusion.

---

## SI S7: Cross-Validation and Temporal Stability

**File**: `SI_S7_Cross_Validation_Results.pdf`

**Contents**:
- Expanding-window CV: complete results for all train/test splits (1906–1950/1951–1970 through 1906–2000/2001–2020)
- Sliding-window CV: complete results for 50-year train windows
- AUC and F1 time series plots
- Coefficient of variation (CV) computation details
- Modern-Ancient Divergence hypothesis: statistical tests for performance differences across eras
- Alternative split strategies: random split (rejected due to temporal leakage), stratified split

**Relevance**: Demonstrates temporal stability and identifies regime-dependent performance.

---

## SI S8: Probability Calibration Analysis

**File**: `SI_S8_Calibration_Analysis.pdf`

**Contents**:
- Reliability diagrams: predicted probability bins vs. observed frequencies (10 bins)
- Expected calibration error (ECE) computation: bin boundaries, bin counts, bin accuracies
- Maximum calibration error (MCE) identification
- Brier score decomposition: reliability, resolution, uncertainty
- Calibration improvement attempts: Platt scaling, isotonic regression, Beta calibration, Venn–Abers predictors
- Comparison: uncalibrated Random Forest vs. calibrated variants
- Operational implications: ordinal risk score derivation from calibrated probabilities

**Relevance**: Documents the calibration limitation and justifies ordinal-risk operational use.

---

## SI S9: Regional Model Performance Details

**File**: `SI_S9_Regional_Models.pdf`

**Contents**:
- China subset: confusion matrix, feature importance, seasonal pattern analysis
- Europe subset: confusion matrix, feature importance, seasonal pattern analysis
- Americas subset: confusion matrix, feature importance, seasonal pattern analysis
- Africa subset: confusion matrix, feature importance, data sparsity assessment
- Regional climate index correlations: ENSO/PDO regional teleconnection patterns
- Geographic bias assessment: event density maps, prediction accuracy by latitude/longitude

**Relevance**: Supports the claim of geographically robust seasonal climate–crisis associations.

---

## SI S10: Epidemic Subset Analysis

**File**: `SI_S10_Epidemic_Subset.pdf`

**Contents**:
- Complete list of 16 epidemic events: name, year, month, pathogen (if known), severity, geographic location
- WuYun element assignment for each event
- LiuQi phase assignment for outbreak month
- Chi-square test computation: observed counts, expected counts (uniform), residuals, standardized residuals
- Fisher's exact test (alternative to chi-square for small samples)
- Respiratory vs. non-respiratory epidemic stratification
- Climate context: ENSO/PDO/temperature anomalies during outbreak years
- WHO/CDC database comparison: mapping our 16 events to standardized disease surveillance records

**Relevance**: Documents the exploratory epidemic-WuYun association and identifies validation needs.

---

## SI S11: Selection Bias Assessment

**File**: `SI_S11_Selection_Bias_Assessment.pdf`

**Contents**:
- Blinded re-collection protocol: coder instructions, WuYun assignment concealment methods
- Wikipedia event extraction methodology: search queries, inclusion/exclusion criteria, automated vs. manual steps
- Comparison: original 1,202-event database vs. blinded 683-event database
- Statistical tests: correlation difference test, event density comparison, severity distribution comparison
- Event-by-event mismatch analysis: events in original but not in blinded, and vice versa
- Bias magnitude estimation: expected AUC inflation due to selection bias
- Recommendations for bias-free curation in future studies

**Relevance**: Provides direct evidence for the central methodological critique (selection bias).

---

## SI S12: Deep Learning Benchmark Details

**File**: `SI_S12_Deep_Learning_Benchmark.pdf`

**Contents**:
- LSTM architecture diagram: input layer → LSTM layers → dense layers → output
- Hyperparameter search space: number of layers, hidden units, dropout rates, learning rates
- Training curves: training loss, validation loss, AUC by epoch
- Attention mechanism evaluation (if attempted): attention weights visualization
- Comparison with other architectures: GRU, Transformer, 1D-CNN
- Failure mode analysis: why LSTM underperforms Random Forest on this dataset
- Feature interaction analysis: SHAP values for LSTM vs. Random Forest

**Relevance**: Documents the negative deep learning result and supports the "signal not hidden in nonlinearity" conclusion.

---

## SI S13: Forward Forecast Methodology and Uncertainty Quantification

**File**: `SI_S13_Forward_Forecast.pdf`

**Contents**:
- 2026–2031 annual forecast: step-by-step computation for each year
- Lagged feature propagation: how predicted values become inputs for subsequent years
- Error accumulation model: Monte Carlo simulation of prediction uncertainty
- Confidence intervals: bootstrap-derived 95% CIs for annual probabilities
- Monthly forecast 2026: month-by-month predicted probabilities
- Scenario analysis: best-case, worst-case, and median climate index assumptions
- Real-time update protocol: how the deployed API incorporates new climate data
- Validation plan: how 2026–2031 predictions will be evaluated against observed events

**Relevance**: Documents the prospective experiment and its uncertainty structure.

---

## SI S14: Complete Figure Source Data

**File**: `SI_S14_Figure_Source_Data.zip`

**Contents**:
- Figure 1: WuYun cycle timeline data (1906–2025, element assignments, crisis counts)
- Figure 2: IPW correction data (before/after event density by element)
- Figure 3: Dynasty boxplot data (PSI distributions by dynasty)
- Figure 4: Feature importance data (annual and monthly, all features)
- Figure 5: ROC curves data (annual, monthly, UCDP, earthquake, epidemic)
- Figure 6: Calibration plot data (predicted vs. observed, 10 bins)
- Figure 7: Cross-validation stability data (AUC by train period)
- Figure 8: Regional comparison data (AUC by region)
- Figure 9: Granger causality visualization data (F-statistics, p-values)
- Figure 10: Epidemic subset data (observed/expected by element)
- Figure 11: Forward forecast data (2026–2031 probabilities)
- Figure 12: Blinded vs. original comparison data (event density by element)

**Format**: CSV files with column headers, ready for plotting.

**Relevance**: Enables readers to reproduce or extend all figures.

---

## SI S15: Glossary of TCM and Climate Terms

**File**: `SI_S15_Glossary.pdf`

**Contents**:
- **WuYun (五运)**: Five Movements — Wood (木), Fire (火), Earth (土), Metal (金), Water (水)
- **LiuQi (六气)**: Six Climates — 厥阴风木, 少阴君火, 少阳相火, 太阴湿土, 阳明燥金, 太阳寒水
- **Sexagenary cycle**: 60-year cycle combining 10 heavenly stems and 12 earthly branches
- **Excess (太过) / Deficiency (不及)**: Dominant vs. subdued element manifestation
- **Solar terms (节气)**: 24 divisions of the solar year used for LiuQi phase assignment
- **ENSO**: El Niño–Southern Oscillation (Niño 3.4 index)
- **PDO**: Pacific Decadal Oscillation
- **GISTEMP**: NASA Goddard Institute for Space Studies surface temperature analysis
- **AUC**: Area under the receiver operating characteristic curve
- **ECE**: Expected calibration error
- **IPW**: Inverse probability weighting (bias correction method)
- **UCDP**: Uppsala Conflict Data Program
- **PSI**: Pattern-Space Integration score (composite risk metric)

**Relevance**: Ensures accessibility for readers from climate science, history, and machine learning backgrounds without TCM expertise.

---

## SI S16: Bayesian Hierarchical Inference (v17B)

**File**: `TCM_UPSI_Bayesian_Supplementary_v1.md` (located in `05_PUBLICATIONS/tcm_upsi_papers/`)

**Contents**:
- **S1. Sampling Configuration**: 4 chains × 4000 draws, target_accept=0.95, max_treedepth=12
- **S2. Convergence Diagnostics**: R-hat, ESS (bulk/tail), divergences, treedepth hits by model
- **S3. Posterior Distributions**: Model A (PSI-only), Model B (PSI+SPI joint), Model C (UPSI_v2 binary)
- **S4. Model Comparison**: WAIC, LOO-CV, ΔWAIC, model selection rationale
- **S5. Posterior Predictive Checks**: Scenario-based probability predictions
- **S6. Sensitivity Analysis**: Prior sensitivity (Half-Normal scale), configuration sensitivity (2nd sampling validation)
- **S7. Limitations & Validation**: Full-data sampling failure disclosure, small-sample caveats
- **S8. Figure Source Data**: Figure S1–S4 source data and generation code
- **S9. Reproducibility**: PyMC model code, data preprocessing pipeline, environment specification

**Associated Figures**:
- **Figure S1**: Convergence diagnostics panel (R-hat, ESS, divergences by model)
- **Figure S2**: Forest plot — Model A domain effects with 94% HDI
- **Figure S3**: WAIC/LOO-CV model comparison bar chart
- **Figure S4**: Posterior mean correlation matrix heatmap (Model B)

**Key Findings**:
1. PSI is a robust cross-domain crisis signal: P(β₀<0) = 0.833 (Model A subset), P(β₁₀<0) = 0.833 (Model B)
2. SPI independent contribution not significant: P(β₂₀>0) = 0.411
3. Model B (PSI+SPI) not significantly better than Model A: ΔWAIC = 1.19 (< 1 SE)
4. Full 7-domain sampling failed (15,984 divergences, r̂=1.20); subset models (n=67, 3 domains) converged well
5. **Formal result**: 1st sampling (target_accept=0.99, max_treedepth=15, non-centered parameterization) used as primary; 2nd sampling as validation

**Relevance**: Provides rigorous Bayesian validation of the PSI/SPI framework and documents both successful convergence and honest failure modes.

---

## File Summary

| SI Code | File | Size (est.) | Format |
|---------|------|-------------|--------|
| S1 | `SI_S1_WuYun_LiuQi_Computation.pdf` | ~500 KB | PDF |
| S2 | `SI_S2_Event_Database_Schema.pdf` | ~800 KB | PDF |
| S3 | `SI_S3_Feature_Engineering.pdf` | ~600 KB | PDF |
| S4 | `SI_S4_Model_Hyperparameters.pdf` | ~400 KB | PDF |
| S5 | `SI_S5_Granger_Causality_Results.pdf` | ~700 KB | PDF |
| S6 | `SI_S6_External_Validation_Results.pdf` | ~900 KB | PDF |
| S7 | `SI_S7_Cross_Validation_Results.pdf` | ~600 KB | PDF |
| S8 | `SI_S8_Calibration_Analysis.pdf` | ~700 KB | PDF |
| S9 | `SI_S9_Regional_Models.pdf` | ~800 KB | PDF |
| S10 | `SI_S10_Epidemic_Subset.pdf` | ~500 KB | PDF |
| S11 | `SI_S11_Selection_Bias_Assessment.pdf` | ~600 KB | PDF |
| S12 | `SI_S12_Deep_Learning_Benchmark.pdf` | ~500 KB | PDF |
| S13 | `SI_S13_Forward_Forecast.pdf` | ~600 KB | PDF |
| S14 | `SI_S14_Figure_Source_Data.zip` | ~2 MB | ZIP (CSV) |
| S15 | `SI_S15_Glossary.pdf` | ~300 KB | PDF |
| S16 | `TCM_UPSI_Bayesian_Supplementary_v1.md` | ~19 KB | Markdown (+ 4 PNG figures) |

**Total estimated size**: ~10 MB (+ ~2 MB for Bayesian SI figures)

---

**Contact**: For questions about supplementary materials, contact the corresponding author at [email to be filled].
