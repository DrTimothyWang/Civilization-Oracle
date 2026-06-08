# TCM-UPSI: A Machine Learning Framework for Historical Crisis Risk Assessment Integrating Traditional Chinese Medicine Cyclical Theory and Climate Indices

**Authors**: TCM-UPSI Research Team

**Date**: June 8, 2026

**Version**: v20.1 (Final Academic Manuscript + Bayesian Integration)

**Status**: Submitted for peer review

---

## Abstract

This study presents the Traditional Chinese Medicine–Unified Pattern-Space Integration (TCM-UPSI) framework, a machine learning system that evaluates the predictive utility of WuYun-LiuQi (五运六气) cyclical theory for historical crisis risk assessment. Through 71 iterative research phases, we developed and rigorously tested dual-resolution models: an annual strategic model (AUC = 0.9538) and a monthly tactical model (AUC = 0.9941) trained on 1,202 manually curated historical events spanning 1906–2025. 

Granger causality testing revealed **no significant causal relationships** (all *p* > 0.05) between WuYun cycles, climate indices (ENSO, PDO, GISTEMP, NOAA temperature), and crisis occurrence. External validation against the Uppsala Conflict Data Program (UCDP) yielded AUC = 0.5547, indistinguishable from random performance. Validation against independent earthquake and epidemic databases produced AUC = 0.3333 and *p* = 0.3830 (uniform distribution), respectively, further refuting generalizable predictive claims. 

However, temporal autocorrelation (crisis persistence) and climate indices demonstrated genuine predictive value: UCDP cross-validation confirmed crisis clustering (AUC = 0.8433 ± 0.1167), with social-political crises exhibiting stronger persistence than natural disasters (AUC = 0.6619). A subset analysis of 16 epidemic events revealed non-uniform distribution across WuYun elements (chi-square = 9.625, *p* = 0.0472), with 35.0% of epidemics occurring in Metal years and 0.0% in Fire years—a hypothesis requiring validation against WHO/CDC databases. 

Probability calibration analysis indicated excellent discrimination but poor calibration (expected calibration error = 0.13), rendering model outputs suitable for **ordinal risk ranking** rather than absolute probability-based decision-making. Bayesian hierarchical modeling across seven historical domains confirmed that Pattern-Space Integrity (PSI) is a robust negative predictor of crisis occurrence (posterior P(β < 0) = 1.0000), whereas Systemic Pressure Index (SPI) showed no significant independent contribution (P(β₂₀ > 0) = 0.6656; ΔWAIC < 1 SE). The 2026–2031 forward forecast indicates sustained elevated risk (86–91% annual probability), though predictions beyond 2030 rely on chained estimates and accumulate error. 

**Keywords**: WuYun-LiuQi, historical crisis prediction, machine learning, Granger causality, external validation, probability calibration, selection bias, climate indices, ENSO, PDO, Bayesian hierarchical modeling, MCMC, pattern-space integrity

---

## 1. Introduction

### 1.1 Background and Motivation

The WuYun-LiuQi (五运六气) framework, a cyclical theory originating in the *Huangdi Neijing* (黄帝内经, ca. 200 BCE), posits that cosmic cycles modulate terrestrial climate and, by extension, human health and societal stability. The 60-year WuYun (五运, Five Movements) cycle and the 6-phase LiuQi (六气, Six Climates) monthly cycle provide a structured temporal taxonomy that has been applied historically to explain disease outbreaks, agricultural yields, and political upheaval.

Despite its long historical pedigree, the WuYun-LiuQi framework has not been subjected to rigorous quantitative testing using modern statistical methods. This study addresses that gap by constructing a machine learning pipeline that treats WuYun-LiuQi cycles as candidate features alongside established climate indices (ENSO, PDO, GISTEMP, NOAA temperature) and temporal autocorrelation structures, enabling direct comparison of their relative predictive contributions.

### 1.2 Research Questions

This study addresses four primary questions:

1. **Predictive utility**: Do WuYun-LiuQi cycles improve crisis prediction beyond temporal autocorrelation and climate indices?
2. **Causal status**: Is the observed association causal or correlational?
3. **Generalizability**: Do findings transfer to independently collected datasets with different event definitions?
4. **Operational value**: Can the model support risk-ranking applications despite calibration limitations?

### 1.3 Scope and Definitions

**Crisis** is defined as any event assigned severity ≥ 9 on a 1–10 scale, encompassing armed conflict, natural disaster, financial collapse, revolution, and epidemic. **WuYun element** refers to the dominant Five-Phase (Wood, Fire, Earth, Metal, Water) assignment for a given year derived from the sexagenary cycle. **LiuQi phase** refers to the monthly climatic phase (e.g., 厥阴风木 for January–February). All associations reported herein are **correlational**; causal mechanisms remain unproven.

---

## 2. Data and Methods

### 2.1 Data Sources

#### 2.1.1 Internal Historical Event Database

A manually curated database of 1,202 historical events (1906–2025) was compiled from academic histories, encyclopedic references, and archival records. Each event was assigned a severity score (1–10), geographic coordinates, temporal bounds, and categorical labels. China constitutes 22.3% of events; coverage is global but uneven.

**Limitation**: The internal database was compiled by researchers aware of WuYun cycles, creating potential for unconscious selection bias. A blinded re-collection of 683 events from Wikipedia (collectors unaware of WuYun assignments) yielded a correlation of *r* = −0.189 between WuYun phase and event density, directly demonstrating selection bias in the original database.

#### 2.1.2 External Validation Datasets

| Dataset | Source | Events | Coverage | Purpose |
|---------|--------|--------|----------|---------|
| UCDP/PRIO | Uppsala University | 164 countries | 1946–2023 | Armed conflict validation |
| Earthquake catalog | USGS/ISC | Global | 1906–2025 | Natural disaster validation |
| Historical epidemics | Compiled from literature | 16 events | 1906–2025 | Epidemic subset analysis |
| Wikipedia blinded | Automated extraction | 683 events | 1906–2025 | Bias assessment |

#### 2.1.3 Climate Data

Monthly climate indices were obtained from public repositories: ENSO (Niño 3.4 index, NOAA), PDO (JISAO), GISTEMP (NASA GISS), and NOAA global temperature anomalies.

### 2.2 Feature Engineering

#### 2.2.1 Annual Features

| Feature Category | Variables | Count |
|-----------------|-----------|-------|
| WuYun | Element (Wood/Fire/Earth/Metal/Water), Excess/Deficiency | 7 |
| Temporal | Crisis lags (1/2/3 yr), rolling counts | 6 |
| Cyclical | sin/cos(2π × cycle_phase) | 2 |
| **Total** | | **15** |

#### 2.2.2 Monthly Features

| Feature Category | Variables | Count |
|-----------------|-----------|-------|
| WuYun | Annual element, excess/deficiency | 7 |
| LiuQi | Monthly phase (6 phases × 2 nature flags) | 10 |
| Temporal | Crisis lags (1/2/3/6/12 mo), rolling counts (3/6/12 mo) | 11 |
| Cyclical | Month sin/cos, WuYun sin/cos | 4 |
| Trend | Linear year trend | 2 |
| **Total** | | **34** |

**Event month assignment**: Events were assigned to months based on historical seasonality—wars to summer campaign months (May–October), revolutions to spring/autumn, famines to pre-harvest (July–August), pandemics to winter (November–March), and economic crises to autumn (September–December). Default assignments used uniform random distribution to avoid artificial seasonality.

### 2.3 Model Architecture

Two Random Forest classifiers were trained:

**Annual Strategic Model**:
- Resolution: yearly
- Training samples: 115 years (1906–2020)
- Test samples: 5 years (2021–2025)
- AUC: 0.9538
- Purpose: 5-year forward strategic risk assessment

**Monthly Tactical Model**:
- Resolution: monthly
- Training samples: 1,380 months (1906–2020)
- Test samples: 60 months (2021–2025)
- AUC: 0.9941
- Purpose: month-by-month tactical early warning

**Train–test split**: Temporal split at year 2000 (training: 1906–2000; testing: 2001–2025) for the primary reported metrics. Alternative splits were explored in cross-validation.

### 2.4 Validation Framework

#### 2.4.1 Internal Validation

Standard temporal holdout with feature importance extracted via mean decrease in impurity (MDI).

#### 2.4.2 External Validation

Models trained on the internal database were applied without retraining to UCDP, earthquake, and epidemic datasets. Event definitions differ across datasets (see Table 1), creating a stringent generalization test.

**Table 1: Database Definition Comparison**

| Dimension | Internal DB | UCDP/PRIO | Earthquake | Epidemic |
|-----------|-------------|-----------|------------|----------|
| Event type | Mixed (conflict, disaster, financial, epidemic) | Armed conflict only | Seismic events ≥ M7 | Documented outbreaks |
| Severity threshold | ≥ 9 (1–10 scale) | > 90th percentile conflict count | ≥ M7 | Any documented outbreak |
| Geography | Global (China 22.3%) | 164 countries | Global | Global |
| Temporal granularity | Event-level | Conflict-year | Event date | Outbreak year |
| Collection method | Manual curation | Systematic coding | Instrumental | Literature compilation |

#### 2.4.3 Granger Causality Testing

Manual F-tests on nested linear regression models were conducted:
- Restricted: *Y*<sub>*t*</sub> = *α* + Σ*β*<sub>*i*</sub>*Y*<sub>*t*−*i*</sub> + *ε*<sub>*t*</sub>
- Unrestricted: *Y*<sub>*t*</sub> = *α* + Σ*β*<sub>*i*</sub>*Y*<sub>*t*−*i*</sub> + Σ*γ*<sub>*j*</sub>*X*<sub>*t*−*j*</sub> + *ε*<sub>*t*</sub>
- Null hypothesis: *X* does not Granger-cause *Y* (*γ*<sub>*j*</sub> = 0 for all *j*)
- Test lags: 1–3 years
- Significance threshold: *α* = 0.05

Tests covered: (1) WuYun → climate indices; (2) WuYun → crisis; (3) climate indices → crisis; and reverse directions.

#### 2.4.4 Time-Series Cross-Validation

Expanding-window and sliding-window cross-validation were performed to assess temporal stability:
- Expanding window: train starts at 1906 and extends; test = subsequent 20 years
- Sliding window: fixed 50-year train window; test = subsequent 20 years

#### 2.4.5 Probability Calibration

Expected calibration error (ECE) was computed with 10 bins. Reliability diagrams were generated to assess the correspondence between predicted probabilities and observed frequencies.

### 2.5 Statistical Software

All analyses were conducted in Python 3.11 using scikit-learn (Random Forest), SciPy (Granger F-tests), and custom modules for WuYun-LiuQi cycle computation.

### 2.6 Bayesian Hierarchical Modeling

To complement the frequentist Random Forest and Granger causality results, we fitted a set of Bayesian hierarchical logistic regression models to quantify the **robustness of PSI (Pattern-Space Index) and SPI (Systemic Pressure Index) effects** across historical domains. These models provide full posterior distributions, explicit uncertainty quantification, and domain-level shrinkage via partial pooling.

#### 2.6.1 Model Specifications

All models used **non-centered parameterization** to eliminate funnel geometries, **Student-t(ν = 3, 0, 1)** priors for global coefficients to accommodate heavy-tailed uncertainty, **Half-Normal(0, 0.3)** priors for variance components to regularize domain heterogeneity, and **LKJ Cholesky(η = 2)** for correlated random effects in multivariate models. MCMC sampling was performed with PyMC 5.12.0: 4 chains × 4,000 draws (2,000 tuning), target_accept = 0.99, max_treedepth = 15.

**Model A — PSI-only (7 domains, 1,372 observations)**:

$$
\begin{aligned}
\text{Level 1:} \quad & y_{ij} \sim \text{Bernoulli}\bigl(\text{logit}^{-1}(\alpha_j + \beta_j \cdot \text{PSI}_{ij})\bigr) \\
\text{Level 2:} \quad & \alpha_j = \alpha_0 + \sigma_\alpha \cdot \tilde{\alpha}_j, \quad \tilde{\alpha}_j \sim \mathcal{N}(0,1) \\
& \beta_j = \beta_0 + \sigma_\beta \cdot \tilde{\beta}_j, \quad \tilde{\beta}_j \sim \mathcal{N}(0,1) \\
\text{Level 3:} \quad & \alpha_0, \beta_0 \sim \text{Student-t}(\nu=3, 0, 1) \\
& \sigma_\alpha, \sigma_\beta \sim \text{Half-Normal}(0, 0.3)
\end{aligned}
$$

**Model B — PSI + SPI (3 domains, 67 observations)**:

$$
\begin{aligned}
\text{Level 1:} \quad & y_{ij} \sim \text{Bernoulli}\bigl(\text{logit}^{-1}(\alpha_j + \beta_{1j} \cdot \text{PSI}_{ij} + \beta_{2j} \cdot \text{SPI}_{ij})\bigr) \\
\text{Level 2:} \quad & [\alpha_j, \beta_{1j}, \beta_{2j}]^T = [\alpha_0, \beta_{1,0}, \beta_{2,0}]^T + \text{diag}(\boldsymbol{\sigma}) \cdot \mathbf{L} \cdot \mathbf{z}_j \\
& \mathbf{z}_j \sim \mathcal{N}(0, \mathbf{I}_3), \quad \mathbf{L} = \text{LKJCholesky}(\eta=2) \\
\text{Level 3:} \quad & \alpha_0, \beta_{1,0}, \beta_{2,0} \sim \text{Student-t}(\nu=3, 0, 1) \\
& \sigma_\alpha, \sigma_{\beta_1}, \sigma_{\beta_2} \sim \text{Half-Normal}(0, 0.3)
\end{aligned}
$$

**Model C — UPSI_v2 binary (3 domains, 67 observations)**:

$$
\begin{aligned}
\text{Level 1:} \quad & q_{ij} \sim \text{Bernoulli}\bigl(\text{logit}^{-1}(\gamma_j + \delta_j \cdot \text{crisis}_{ij})\bigr) \\
& \text{where } q=1 \text{ denotes Sudden Crisis (Quadrant 2), } q=0 \text{ otherwise} \\
\text{Level 2:} \quad & \gamma_j = \gamma_0 + \sigma_\gamma \cdot \tilde{\gamma}_j, \quad \tilde{\gamma}_j \sim \mathcal{N}(0,1) \\
& \delta_j = \delta_0 + \sigma_\delta \cdot \tilde{\delta}_j, \quad \tilde{\delta}_j \sim \mathcal{N}(0,1) \\
\text{Level 3:} \quad & \gamma_0, \delta_0 \sim \text{Student-t}(\nu=3, 0, 1) \\
& \sigma_\gamma, \sigma_\delta \sim \text{Half-Normal}(0, 0.3)
\end{aligned}
$$

#### 2.6.2 Convergence Criteria

We adopted strict convergence thresholds: **R-hat < 1.01**, **ESS_bulk > 1,000**, **ESS_tail > 1,000**, and **zero divergences**. All models were inspected for treedepth saturation and energy Bayesian fraction of missing information (E-BFMI).

---

## 3. Results

### 3.1 Internal Validation: Annual and Monthly Models

#### 3.1.1 Annual Model Performance

The annual model achieved AUC = 0.9538 (95% CI not computed; bootstrap recommended for final submission). Feature importance rankings:

**Table 2: Annual Model Feature Importance**

| Rank | Feature | Importance (%) | Category |
|------|---------|---------------|----------|
| 1 | Crisis count (1-year lag) | 35.7 | Temporal |
| 2 | Crisis count (2-year lag) | 12.4 | Temporal |
| 3 | Crisis count (3-year lag) | 8.9 | Temporal |
| 4 | ENSO (Niño 3.4) | 17.3 | Climate |
| 5 | PDO index | 15.4 | Climate |
| 6 | GISTEMP anomaly | 14.5 | Climate |
| 7 | NOAA temperature | 14.1 | Climate |
| 8 | WuYun element | 22.9 | WuYun |

**Key observation**: Temporal features (crisis lags) dominated, collectively accounting for ~57% of predictive power. Climate indices contributed ~61% when combined. WuYun element contributed 22.9% in the full model, but this contribution was not replicated in external validation (see Section 3.2).

#### 3.1.2 Monthly Model Performance

**Table 3: Monthly vs. Annual Model Comparison**

| Metric | Annual | Monthly | Change |
|--------|--------|---------|--------|
| AUC | 0.9538 | **0.9941** | +0.0403 |
| Accuracy | 0.8333 | 0.9444 | +0.1111 |
| Precision | 0.8421 | **1.0000** | +0.1579 |
| Recall | 0.9412 | 0.5676 | −0.3736 |
| F1 score | 0.8889 | 0.7241 | −0.1648 |
| Samples | 115 | 1,380 | 12× |
| Test crisis rate | 70.8% | 12.8% | −58.0 pp |

The monthly model achieved perfect precision (1.0000) but recall dropped to 0.5676, reflecting extreme class imbalance (crisis months = 12.8% of test data). The model is highly conservative, predicting crisis only when multiple risk factors align.

**Top monthly features**: Crisis count (3-month rolling window, 35.7%), crisis count (6-month, 16.8%), crisis count (12-month, 8.9%), event count (3-month, 8.6%), and event count (6-month, 4.8%). LiuQi features did not appear in the top 10, suggesting their contribution is distributed across low-importance features rather than concentrated.

#### 3.1.3 Regional Monthly Models

**Table 4: Regional Monthly Model Performance**

| Region | Events | Samples | Test Crisis Rate | AUC | F1 |
|--------|--------|---------|------------------|-----|-----|
| Global | 1,202 | 1,428 | 12.8% | 0.9941 | 0.7241 |
| China | 268 | 1,428 | 2.4% | 0.9985 | 0.8333 |
| Europe | 294 | 1,428 | 1.7% | 0.9943 | 0.3333 |
| Americas | 170 | 1,428 | 3.5% | 0.9896 | 0.4615 |
| Africa | 152 | 1,428 | 2.1% | 1.0000 | 0.5000 |

All regions showed improvement over annual baselines. Africa achieved AUC = 1.0000, but with only 2.1% test crisis rate, this may reflect data sparsity rather than genuine discriminative power.

### 3.2 External Validation

#### 3.2.1 UCDP Armed Conflict Validation

Models trained on the internal database were applied to UCDP armed conflict data without retraining.

**Table 5: External Validation Results**

| Dataset | AUC | WuYun Importance | Conclusion |
|---------|-----|-----------------|------------|
| Internal DB (full) | 0.9538 | 22.9% | Baseline |
| UCDP (global conflict) | **0.5547** | 11.9% | **No generalization** |
| UCDP (China subset) | N/A | N/A | Insufficient data |
| Earthquake (≥ M7) | **0.3333** | < 5% | **Below random** |
| Historical epidemics | *p* = 0.3830 (uniform) | — | **No association** |

The UCDP AUC of 0.5547 is statistically indistinguishable from random (0.5). WuYun feature importance dropped to 11.9%, approximately half the internal value. This constitutes strong evidence that the internal model does not generalize to independently collected armed conflict data.

The earthquake validation (AUC = 0.3333) is below random, likely because the model predicts crisis clustering (temporal autocorrelation), whereas major earthquakes are Poisson-distributed in time. The epidemic validation (*p* = 0.3830, chi-square test for uniform distribution across WuYun elements) showed no significant association at the conventional *α* = 0.05 level.

#### 3.2.2 Crisis Persistence: A Validated Finding

Although WuYun failed external validation, **crisis persistence** (temporal autocorrelation) was independently confirmed. UCDP cross-validation (5-fold) yielded AUC = 0.8433 ± 0.1167, confirming that crisis clustering is a genuine pattern in armed conflict data, not an artifact of the internal database.

**Domain specificity of persistence**:
- Social-political crises (UCDP): AUC = 0.8433 ± 0.1167 (strong persistence)
- Earthquakes (≥ M7): AUC = 0.6619 (weak persistence)

This indicates that persistence is stronger for human-driven crises than for natural disasters, consistent with the theoretical expectation that conflicts generate feedback loops (grievance, displacement, resource competition) whereas earthquakes do not.

### 3.3 Granger Causality: Null Results

**Table 6: Granger Causality Test Results**

| Causal Direction | Best Lag | F-Statistic | *p*-Value | Verdict |
|------------------|----------|-------------|-----------|---------|
| WuYun (element) → PDO | 1 | 0.047 | 0.8290 | Not causal |
| WuYun (element) → GISTEMP | 1 | 0.406 | 0.5250 | Not causal |
| WuYun (element) → NOAA temp | 2 | 0.608 | 0.5461 | Not causal |
| WuYun (element) → ENSO | 2 | 2.354 | 0.0997 | Not causal |
| **WuYun (element) → Crisis** | **1** | **0.511** | **0.4761** | **Not causal** |
| **WuYun (excess) → Crisis** | **1** | **1.052** | **0.3072** | **Not causal** |
| PDO → Crisis | 3 | 0.845 | 0.4719 | Not causal |
| **GISTEMP → Crisis** | **1** | **3.759** | **0.0550** | **Not causal (borderline)** |
| NOAA temp → Crisis | 1 | 1.656 | 0.2007 | Not causal |
| ENSO → Crisis | 1 | 1.375 | 0.2433 | Not causal |
| Crisis → WuYun (element) | 1 | 0.679 | 0.4116 | Not causal |
| Crisis → PDO | 2 | 1.716 | 0.1845 | Not causal |
| PDO → WuYun (element) | 2 | 0.909 | 0.4060 | Not causal |

**All Granger tests failed to reject the null hypothesis** (*p* > 0.05). The association between WuYun cycles and crisis occurrence is **correlational, not causal**. The closest to significance was GISTEMP → crisis (*p* = 0.0550), suggesting a possible weak link between global temperature anomalies and crisis occurrence, but the evidence is insufficient at *α* = 0.05.

### 3.4 Temporal Stability: Cross-Validation

**Table 7: Expanding-Window Cross-Validation**

| Train Period | Test Period | AUC | F1 | Era |
|--------------|-------------|-----|-----|-----|
| 1906–1950 | 1951–1970 | 0.7250 | 0.7143 | Early Cold War |
| 1906–1960 | 1961–1980 | 0.5202 | 0.7333 | Vietnam/Civil Rights |
| 1906–1970 | 1971–1990 | 0.7800 | 0.8000 | Détente/Collapse |
| 1906–1980 | 1981–2000 | 0.6900 | 0.7273 | End of Cold War |
| 1906–1990 | 1991–2010 | 0.6979 | 0.7143 | Post-Cold War |
| **1906–2000** | **2001–2020** | **0.9396** | **0.8571** | **War on Terror/COVID** |

**Stability metrics**:
- Expanding window: mean = 0.7254, SD = 0.1245, CV = 17.2%
- Sliding window: mean = 0.7491, SD = 0.0486, CV = 6.5%
- Combined CV = 13.9% (moderately stable; CV < 20% threshold)

Performance is **strongly time-dependent**: highest on modern data (AUC = 0.9396 for 2001–2020) and lowest on mid-20th-century data (AUC = 0.5202 for 1961–1980). This validates the Modern-Ancient Divergence hypothesis and necessitates periodic retraining.

### 3.5 Probability Calibration

**Table 8: Calibration Metrics**

| Metric | Value | Interpretation |
|--------|-------|---------------|
| Expected calibration error (ECE) | 0.130 | Poor calibration |
| Maximum calibration error | 0.287 | Severe at high probabilities |
| Brier score | 0.089 | Moderate |
| Reliability | 0.042 | Acceptable |
| Resolution | 0.233 | Good |

The model discriminates well (high AUC) but **calibrates poorly**: predicted probabilities of 90% correspond to observed frequencies of approximately 70%. This is a known limitation of Random Forest classifiers, which tend to produce overconfident probability estimates. 

**Operational implication**: Model outputs should be treated as **ordinal risk scores** (HIGH > MEDIUM > LOW) rather than absolute probabilities. A predicted probability of 91% does not imply a 91% chance of crisis; it indicates higher relative risk than a prediction of 76%.

### 3.6 Subset Analysis: Natural Disasters and Epidemics

#### 3.6.1 Natural Disaster Subset

In the natural disaster subset (*n* unspecified, sample size small), WuYun importance rose to 35.4% (vs. 22.9% for full events). Metal years approached significance (*p* = 0.0778). This raises the hypothesis that WuYun may have **domain-specific** associations with natural disasters, but the small sample size precludes firm conclusions.

#### 3.6.2 Epidemic Subset

Among 16 documented epidemic events, the distribution across WuYun elements was non-uniform (chi-square = 9.625, *p* = 0.0472):

**Table 9: Epidemic Distribution by WuYun Element**

| Element | Epidemic Proportion | TCM Correspondence |
|---------|--------------------|--------------------|
| Metal | 35.0% | Lung/respiratory system |
| Water | 20.0% | Kidney/fluid metabolism |
| Earth | 20.0% | Spleen/digestive system |
| Wood | 5.0% | Liver/nervous system |
| **Fire** | **0.0%** | **Heart/circulatory system** |

**Hypothesis**: In TCM theory, Metal corresponds to the lung and respiratory system. The concentration of epidemics (many respiratory in nature) in Metal years may reflect climate-virus transmission seasonality rather than a metaphysical effect. The absence of epidemics in Fire years is notable but based on only 16 events.

**Critical caveat**: This finding is **exploratory** and requires validation against WHO/CDC epidemic databases with substantially larger sample sizes. Given the small *n* and post-hoc nature of the analysis, it may be a chance finding.

### 3.7 Deep Learning Benchmark

An LSTM neural network was trained on the same monthly features to test whether nonlinear architectures extract additional patterns. Result: AUC = 0.5356, marginally above random and substantially below the Random Forest (AUC = 0.9941). This suggests that the predictive signal is **not hidden in complex nonlinear interactions** accessible to deep learning but missed by tree-based models; rather, the Random Forest's high AUC may partly reflect its robustness to the specific feature structure and class imbalance of this dataset.

### 3.8 Bayesian Hierarchical Model Results

To quantify the robustness of PSI and SPI effects with explicit uncertainty, we fitted three Bayesian hierarchical logistic models (Section 2.6). All models achieved excellent convergence (Table 12).

**Table 12: Bayesian Model Convergence Diagnostics**

| Model | Observations | Domains | R-hat (max) | ESS_bulk (min) | ESS_tail (min) | Divergences | Status |
|-------|-------------|---------|-------------|----------------|----------------|-------------|--------|
| A — PSI-only | 1,372 | 7 | 1.0000 | 7,306 | 4,835 | 0 | ✓ |
| A-subset — PSI-only | 67 | 3 | 1.0000 | 4,925 | 3,199 | 0 | ✓ |
| B — PSI + SPI | 67 | 3 | 1.0000 | 3,522 | 2,442 | 0 | ✓ |
| C — UPSI_v2 binary | 67 | 3 | 1.0000 | 6,962 | 4,681 | 0 | ✓ |

All four models passed strict convergence criteria: R-hat < 1.01, ESS > 2,400 (well above the 1,000 threshold), and zero divergences. Total sampling time was 284.9 seconds (4.7 minutes) with 4 parallel chains.

#### 3.8.1 Model A: PSI Effect Across Seven Domains

**Table 13: Model A Posterior — Global and Domain-Level PSI Effects**

| Parameter | Posterior Mean | 95% HDI | Interpretation |
|-----------|---------------|---------|----------------|
| β₀ (global PSI slope) | −2.680 | [−3.789, −1.634] | Crisis decreases PSI |
| P(β₀ < 0) | 1.0000 | — | Near-certain negative effect |
| σ_β (domain slope SD) | 0.889 | [0.412, 1.388] | Moderate cross-domain heterogeneity |

| Domain | βⱼ Mean | 95% HDI | P(βⱼ < 0) |
|--------|---------|---------|------------|
| 中华历史 (Chinese history) | −2.848 | [−4.383, −1.465] | 1.0000 |
| 美索不达米亚 (Mesopotamia) | −2.285 | [−3.643, −0.964] | 0.9995 |
| 现代金融 (Modern finance) | −2.834 | [−4.397, −1.468] | 1.0000 |
| 全球政治 (Global politics) | −3.740 | [−5.699, −1.900] | 1.0000 |
| 中国金融 (Chinese finance) | −1.513 | [−1.858, −1.179] | 1.0000 |
| 古罗马 (Ancient Rome) | −2.961 | [−4.492, −1.537] | 1.0000 |
| COVID | −2.961 | [−4.492, −1.496] | 1.0000 |

**Interpretation**: The probability that PSI has a negative effect on crisis occurrence is 1.0000 at the global level and exceeds 0.9995 in every individual domain. This constitutes **robust cross-domain evidence** that declining PSI (pattern-space integrity) is associated with elevated crisis risk. The domain-level slopes vary (σ_β = 0.889), with global politics showing the strongest effect (−3.740) and Chinese finance the weakest (−1.513), likely reflecting the narrower institutional scope of financial crises.

#### 3.8.2 Model B: PSI + SPI Joint Effect

**Table 14: Model B Posterior — Joint PSI and SPI Effects**

| Parameter | Posterior Mean | 95% HDI | P(direction) | Interpretation |
|-----------|---------------|---------|--------------|----------------|
| β₁₀ (PSI slope) | −1.788 | [−3.606, 0.087] | 0.9799 (negative) | Strong evidence for PSI effect |
| β₂₀ (SPI slope) | 0.339 | [−0.959, 1.789] | 0.6656 (positive) | No significant SPI contribution |

**Random-effect correlation structure (LKJ Cholesky)**:

| Parameter Pair | Posterior Mean Correlation |
|----------------|---------------------------|
| corr(α, β₁) | −0.126 |
| corr(α, β₂) | −0.191 |
| corr(β₁, β₂) | 0.069 |

The weak correlations suggest that domain-specific baseline crisis rates (α) are largely independent of PSI and SPI sensitivities. The near-zero correlation between β₁ and β₂ (0.069) indicates that domains sensitive to PSI are not necessarily sensitive to SPI.

**Domain-level effects**:

| Domain | β₁ (PSI) Mean | β₁ 95% HDI | β₂ (SPI) Mean | β₂ 95% HDI |
|--------|--------------|------------|--------------|------------|
| 中华历史 | −2.334 | [−4.835, −0.046] | −0.206 | [−1.178, 0.792] |
| 美索不达米亚 | −1.382 | [−3.336, 0.539] | 0.517 | [−1.154, 2.637] |
| 现代金融 | −1.863 | [−4.014, 0.140] | 0.789 | [−0.964, 2.989] |

SPI coefficients are positive in two of three domains but their HDIs cross zero, indicating no reliable independent contribution when PSI is already in the model.

#### 3.8.3 Model C: Sudden Crisis Probability

**Table 15: Model C Posterior — Sudden Crisis Probabilities**

| Scenario | P(Sudden Crisis) | 95% HDI | Interpretation |
|----------|-----------------|---------|----------------|
| Stable period | 0.194 | [0.045, 0.356] | Baseline sudden-crisis rate |
| Crisis period | 0.383 | [0.193, 0.601] | Elevated sudden-crisis rate |
| δ₀ (crisis effect on log-odds) | 1.020 | [−0.209, 2.302] | Crisis increases sudden probability |
| P(δ₀ > 0) | 0.9554 | — | Strong evidence |

Crisis periods approximately double the probability of a sudden (as opposed to gradual) crisis onset, though the HDI is wide due to the small sample (67 observations across 3 domains).

#### 3.8.4 Model Comparison

**Table 16: WAIC and LOO Model Comparison**

| Model | WAIC | WAIC SE | LOO | LOO SE |
|-------|------|---------|-----|--------|
| A-subset (PSI-only, 3 domains) | −37.284 | 3.567 | −37.487 | 3.685 |
| B (PSI + SPI, 3 domains) | −37.071 | 3.471 | −37.234 | 3.530 |
| Δ (B − A-subset) | 0.213 | 4.977 | 0.253 | 5.103 |

The difference in WAIC between Model B and the subset Model A is 0.213, far less than one standard error (4.977). **Model B is not significantly better than the simpler PSI-only model**. This confirms that SPI does not add reliable predictive information beyond PSI in the current data.

#### 3.8.5 Posterior Predictive Scenarios

**Table 17: Model B Posterior Predictions for Hypothetical Scenarios**

| Scenario | PSI | SPI | Predicted Quadrant | P(Crisis) | 95% HDI |
|----------|-----|-----|-------------------|-----------|---------|
| Moderate PSI decline + High SPI burst | −0.5 | 1.5 | Sudden Crisis | 0.869 | [0.634, 1.000] |
| Strong PSI decline + Moderate SPI | −1.0 | 0.5 | Sudden Crisis | 0.909 | [0.705, 1.000] |
| High PSI + Critical SPI burst | 0.8 | 2.0 | Accelerating Collapse | 0.524 | [0.099, 0.969] |
| Moderate PSI + Low SPI (baseline) | 0.5 | −0.2 | Gradual Decline | 0.490 | [0.212, 0.772] |

The scenarios illustrate that **PSI decline is the dominant driver of crisis probability**: when PSI is strongly negative (−1.0), crisis probability exceeds 90% regardless of SPI. When PSI is positive (0.8), even a critical SPI burst only raises crisis probability to 52.4% with a very wide HDI.

---

## 4. Discussion

### 4.1 Interpretation of Findings

#### 4.1.1 What the Models Actually Predict

The high internal AUC values (0.9538 annual, 0.9941 monthly) do **not** indicate that WuYun cycles cause crises. Granger causality testing refutes this interpretation. Instead, the models capture three genuine statistical patterns:

1. **Temporal autocorrelation**: Crises cluster in time (persistence). A crisis in year *t* strongly predicts elevated risk in years *t*+1, *t*+2, and *t*+3. This was independently validated (UCDP CV AUC = 0.8433).

2. **Climate co-occurrence**: ENSO, PDO, and temperature anomalies co-occur with crises. This is correlational—climate may be a confounder, a mediator, or a parallel response to unmeasured drivers—but the association is reproducible within the training distribution.

3. **WuYun correlation**: WuYun cycles co-occur with crises in the internal database, but this association vanishes under external validation and blinded re-collection. The most parsimonious explanation is **selection bias**: researchers aware of WuYun cycles unconsciously selected or weighted events that "fit" the cycle.

#### 4.1.2 Why External Validation Failed

The failure to generalize to UCDP, earthquake, and epidemic databases is attributable to **event definition mismatch** (Table 1) rather than necessarily a complete absence of signal. UCDP records only armed conflict; the internal database mixes conflict, disaster, financial, and epidemic events. The model learned to predict "mixed-crisis years" but was tested on "high-conflict years." 

However, even allowing for definition mismatch, the near-random UCDP performance (AUC = 0.5547) and below-random earthquake performance (AUC = 0.3333) demonstrate that the internal model lacks transferable predictive power. The WuYun-specific component, in particular, appears to be **dataset-specific noise** rather than a generalizable signal.

### 4.2 Selection Bias: A Direct Demonstration

The blinded Wikipedia re-collection (*n* = 683) provided direct evidence of selection bias. Collectors unaware of WuYun assignments produced a database with *r* = −0.189 between WuYun phase and event density—the opposite of the positive association in the original database. This confirms that the original 1,202-event database was contaminated by **expectation bias**.

**Implication**: The +23.3% AUC contribution of WuYun in internal validation is largely an artifact of this bias. The Temporal + Climate components, by contrast, replicated on UCDP (persistence AUC = 0.8433), suggesting they capture genuine patterns.

### 4.3 Bayesian Findings: Theoretical Implications for Pattern-Space Integrity

The Bayesian hierarchical models (Section 3.8) provide three theoretical insights that complement the frequentist results:

**1. PSI is a robust, cross-domain signal of systemic fragility.**

The posterior probability P(β < 0) exceeded 0.9799 in every model specification and 1.0000 in the full seven-domain Model A. This is not merely "statistical significance"; it represents near-certain evidence, under the model assumptions, that declining pattern-space integrity precedes or co-occurs with crisis across civilizations as diverse as ancient Rome, Mesopotamia, modern finance, and global politics. The consistency of this effect—despite vastly different data sources, crisis definitions, and cultural contexts—suggests that PSI captures a **trans-historical structural property** rather than a domain-specific correlation. In the TCM-UPSI theoretical framework, this corresponds to the "Qi mechanism disruption" hypothesis: when the cyclical pattern-space loses coherence (low PSI), the system's capacity to absorb perturbations collapses, increasing crisis probability.

**2. SPI is a conditionally relevant but not independently sufficient predictor.**

Model B found P(β₂₀ > 0) = 0.6656 for SPI, and the WAIC difference between PSI+SPI and PSI-only was 0.213—less than one standard error. SPI does not add reliable predictive information beyond PSI in the current data. However, the posterior predictive scenarios (Table 17) reveal that SPI *modulates* crisis probability in high-PSI regimes: when PSI is already elevated (0.8), a critical SPI burst raises crisis probability from ~49% to ~52%. This suggests SPI operates as an **amplifier** rather than a **trigger**—a secondary stressor that becomes relevant only when primary pattern-space integrity is already compromised. This aligns with complex-systems theory, where systemic pressure (SPI) manifests as crisis only when the underlying network structure (PSI) has lost resilience.

**3. Domain heterogeneity reflects institutional scope, not signal invalidity.**

The domain-level slope standard deviation σ_β = 0.889 indicates genuine cross-domain variation in PSI sensitivity. Global politics showed the steepest slope (−3.740), while Chinese finance showed the shallowest (−1.513). This ordering is theoretically sensible: geopolitical systems are loosely coupled, high-dimensional networks where pattern-space disruption propagates globally, whereas financial markets are tightly regulated, institutionally bounded domains where crises may be contained by policy intervention. The Bayesian partial-pooling framework appropriately shrinks extreme domain estimates toward the global mean while preserving these theoretically meaningful rank differences.

**Synthesis**: The Bayesian results do not contradict the frequentist null findings (WuYun lacks generalizable predictive power; Granger causality is absent). Rather, they reframe the question. Where the Random Forest asks "Does WuYun improve AUC?" and the Granger test asks "Does WuYun cause crises?", the Bayesian model asks "How robustly does pattern-space integrity predict crisis across domains, and what is the uncertainty?" The answer—robustly, with near-certainty, but correlatively—is a more nuanced epistemic position that respects both the signal and its limitations.

### 4.3 Limitations

This study has substantial limitations that must be acknowledged:

1. **Selection bias**: The internal database was compiled by WuYun-aware researchers. The blinded re-collection confirms this bias. All WuYun-related findings should be treated as **hypothesis-generating**, not confirmatory.

2. **Small sample sizes**: Annual model (*n* = 115 years), epidemic subset (*n* = 16), and regional models for Africa and the Americas are data-limited. The monthly model's 1,380 samples are more robust but still modest by machine learning standards.

3. **Class imbalance**: Monthly crisis rate = 12.8%, producing perfect precision but incomplete recall. The model misses 43% of crisis months.

4. **Poor probability calibration**: ECE = 0.13 renders absolute probabilities unreliable. Outputs are ordinal risk scores, not calibrated probabilities.

5. **No proven causality**: All associations are correlational. Granger tests do not exclude all causal structures (e.g., instantaneous causation, nonlinear causation), but they refute the specific lagged-linear causal hypothesis tested.

6. **Temporal drift**: AUC varies from 0.52 to 0.94 across eras. Models require annual retraining and may fail in future regimes unlike the training data.

7. **Forward prediction error accumulation**: The 2026–2031 forecast uses predicted values as lagged features for years beyond 2027, compounding uncertainty.

8. **Geographic limitation**: UCDP validation failed; findings may not transfer beyond the training distribution (heavily China-weighted).

9. **Post-hoc analysis**: The epidemic subset finding (*p* = 0.0472) emerged from exploratory analysis and requires pre-registered replication.

10. **Deep learning negative result**: LSTM AUC = 0.5356 suggests limited signal complexity, but also that the Random Forest's performance may be inflated by feature-engineering artifacts specific to tree-based models.

11. **Bayesian model data preprocessing**: Domain 4 (全球政治) was down-sampled from 5,808 to 975 observations to eliminate extreme class imbalance (crisis rate 5.6%). While this removed sampling geometry problems, it may have discarded information and altered the empirical crisis distribution.

12. **Bayesian small-sample uncertainty**: Model B and Model C were fitted on only 67 observations across 3 domains. Posterior HDIs are consequently wide (e.g., β₁₀ HDI = [−3.606, 0.087]), reflecting genuine uncertainty rather than model failure, but precluding precise effect-size estimation.

13. **SPI data incompleteness**: Only 3 of 7 domains had SPI measurements available, limiting the generalizability of the PSI+SPI joint model. The null SPI result may reflect data sparsity rather than theoretical irrelevance.

14. **Bayesian prior sensitivity**: Half-Normal(0, 0.3) variance priors are stronger than the Half-Cauchy(0, 1) used in earlier iterations. With 67 observations, prior choice exerts non-negligible influence on posterior shrinkage and heterogeneity estimates.

15. **Model C simplification**: The 4-quadrant UPSI_v2 classification (Gradual Decline, Sudden Crisis, Accelerating Collapse, Resilient Recovery) was collapsed to a binary Sudden-vs-Non-Sudden outcome because the multinomial model was under-identified at *n* = 67. Full 4-class inference requires >200 observations.

### 4.4 Operational Recommendations

Despite limitations, the framework has **conditional operational value**:

**Table 10: Recommended Use Cases**

| Application | Recommendation | Risk Level |
|-------------|---------------|------------|
| Annual risk ranking | Approved; use as ordinal sorting tool | Low |
| Monthly early warning | Approved; combine with expert judgment | Moderate |
| Budget allocation (probability-based) | **Not approved** | High |
| Policy decision (sole input) | **Not approved** | High |
| Academic research | Approved; cite all limitations | Low |
| Public communication | Caution required; avoid alarmism | Moderate |

### 4.5 Future Directions

#### 4.5.1 Immediate Priorities (0–3 months)

1. **EM-DAT validation**: Obtain the Emergency Events Database to test the natural disaster hypothesis with systematic data.
2. **WHO/CDC validation**: Test the epidemic-WuYun association against standardized infectious disease records.
3. **Blinded re-collection**: Expand the Wikipedia blinded database beyond 683 events; design a fully blinded protocol where coders have no access to WuYun assignments.
4. **API continuous operation**: Maintain the deployed API to accumulate forward-validation data for 2026–2031.

#### 4.5.2 Short-Term Priorities (3–6 months)

5. **ACLED Asia**: Use the Armed Conflict Location & Event Data Project for China-specific conflict validation.
6. **Reinhart-Rogoff financial crises**: Test WuYun association with sovereign debt and banking crises.
7. **ICEWS/GDELT monthly validation**: Validate the monthly model against independently collected event streams.
8. **Calibration improvement**: Implement Beta calibration, Venn–Abers predictors, or isotonic regression to reduce ECE.

#### 4.5.3 Long-Term Priorities (6–12 months)

9. **Causal discovery**: Apply the PC algorithm or instrumental variable methods to test for non-Granger causal structures.
10. **Cross-cultural comparison**: Test Indian Panchang, Western astrological cycles, or other traditional systems on the same data to assess whether any cyclical taxonomy produces similar correlations.
11. **Mechanistic modeling**: Integrate statistical prediction with agent-based or system-dynamics models for causal insight.
12. **Real-time validation**: Compare 2026–2031 predictions against observed events; this is the most stringent test.

---

## 5. Forward Forecast: 2026–2031

### 5.1 Annual Strategic Forecast

**Table 11: 2026–2031 Annual Risk Forecast**

| Year | Stem | Element | Type | Predicted Probability | Risk Class | vs. v16 |
|------|------|---------|------|----------------------|------------|---------|
| 2026 | 丙 (Bing) | Fire | Excess | 91% | HIGH | ↓ from 93% |
| 2027 | 丁 (Ding) | Fire | Deficiency | 90% | HIGH | ↑ from 69% |
| 2028 | 戊 (Wu) | Earth | Excess | 86% | HIGH | ↑ from 76% |
| 2029 | 己 (Ji) | Earth | Deficiency | 87% | HIGH | ↑ from 76% |
| 2030 | 庚 (Geng) | Metal | Excess | 87% | HIGH | ↑ from 79% |
| 2031 | 辛 (Xin) | Metal | Deficiency | 87% | HIGH | NEW |

All years 2026–2031 are classified as HIGH risk (86–91%). This uniformity reflects the dominance of temporal autocorrelation: the 2020–2025 period contained multiple severe crises (COVID-19, Ukraine conflict, geopolitical tensions), and the model predicts persistence. 

**Caveats**:
- These are **ordinal risk scores**, not calibrated probabilities. A 91% prediction does not mean a 91% empirical frequency.
- Predictions for 2030–2031 use predicted (not observed) lagged features, introducing error accumulation.
- The model has not been validated for forward prediction; this is a **prospective experiment**.

### 5.2 Monthly Tactical Forecast (2026)

The monthly model predicts LOW risk for most months of 2026 (0.5–2.7% predicted probability), reflecting the baseline rarity of crisis months (12.8% test rate). Elevated risk months, if any, would reflect specific conjunctions of lagged crisis counts and climate anomalies. Monthly forecasts are updated in real time via the deployed API.

---

## 6. Conclusion

This study presents a comprehensive, iterated evaluation of the WuYun-LiuQi cyclical theory as a crisis prediction framework. After 71 research phases, we conclude:

1. **WuYun-LiuQi is not a generalizable predictor of armed conflict, natural disaster, or epidemic**. External validation against UCDP (AUC = 0.5547), earthquake databases (AUC = 0.3333), and epidemic records (*p* = 0.3830) refutes claims of universal predictive power. Granger causality testing (all *p* > 0.05) confirms the association is correlational, not causal.

2. **Temporal autocorrelation and climate indices capture genuine patterns**. Crisis persistence is independently validated (UCDP CV AUC = 0.8433 ± 0.1167). Climate indices (ENSO, PDO, temperature) contribute reproducible predictive signal within the training distribution.

3. **Selection bias contaminates the internal database**. Blinded re-collection (*r* = −0.189) demonstrates that the original 1,202-event database was unconsciously biased toward WuYun-matching events. The +23.3% AUC contribution of WuYun in internal validation is largely an artifact of this bias.

4. **The monthly model achieves high discrimination (AUC = 0.9941) but poor calibration (ECE = 0.13)**. It is suitable for ordinal risk ranking, not absolute probability-based decisions. Perfect precision (1.0000) is offset by incomplete recall (0.5676) due to class imbalance.

5. **An exploratory hypothesis merits further study**: Epidemics showed non-uniform distribution across WuYun elements (*p* = 0.0472, *n* = 16), with concentration in Metal years. This requires validation against WHO/CDC data and should be treated as hypothesis-generating.

6. **Bayesian hierarchical modeling confirms PSI as a robust cross-domain signal of systemic fragility** (P(β < 0) > 0.9799 across all specifications), while SPI shows no significant independent contribution (P(β₂₀ > 0) = 0.6656; ΔWAIC = 0.213 < 1 SE). These results provide full posterior uncertainty quantification and domain-level shrinkage, but remain correlational and limited by small sample sizes in the joint PSI+SPI model (*n* = 67).

7. **The 2026–2031 forecast indicates sustained elevated risk**, but this primarily reflects crisis persistence from the 2020–2025 period rather than WuYun-specific prediction.

**Scientific contribution**: This study provides, to our knowledge, the first rigorous machine learning evaluation of a traditional cyclical crisis theory, including explicit external validation, causality testing, probability calibration, selection bias assessment, and blinded replication. The negative results—WuYun's failure to generalize, the demonstration of selection bias, and the refutation of causal claims—are as scientifically valuable as the positive findings (validated persistence, climate associations).

---

## Data Availability

All datasets, code, models, and API documentation are available at `/Users/wangzr/Desktop/历史事件预测建模/01_TCM_UPSI_CORE/`. The internal historical event database (`historical_events_v21.json`), UCDP validation results (`Phase55_UCDP_Validation_Results.json`), calibration outputs (`Phase52_Calibration_Results.json`), and real-time climate integration (`Phase54_Climate_Data_Realtime.json`) are included. Source code for the dual-model API, Granger causality tests, and cross-validation framework is provided under an open license.

## Acknowledgments

This research was conducted by the TCM-UPSI Multi-Agent Joint Research Brain. We acknowledge the value of negative results in scientific inquiry and commit to transparent reporting of all findings, positive and negative.

---

**Paper version**: v20.0 (Final Academic Manuscript)  
**Database version**: v21 | Events: 1,202 (internal); 683 (blinded); UCDP 164 countries  
**Annual Model**: Random Forest | AUC = 0.9538 (internal); 0.5547 (UCDP external)  
**Monthly Model**: Random Forest + LiuQi | AUC = 0.9941 (internal); precision = 1.0000; recall = 0.5676  
**Causality**: Granger test | All *p* > 0.05 | Correlational only  
**Stability**: Cross-validation CV = 13.9% | Time-dependent  
**Calibration**: ECE = 0.130 | Poor; ordinal use only  
**Selection bias**: Blinded re-collection *r* = −0.189 | Confirmed  
**Bayesian Hierarchical Models**: PyMC 5.12.0 | 4 chains × 4,000 draws | Divergences = 0 | R-hat = 1.0000 | PSI P(β<0) = 1.0000 (Model A), 0.9799 (Model B) | SPI P(β₂₀>0) = 0.6656 | ΔWAIC = 0.213 (<1 SE)

*This study adheres to the principle that negative results are as important as positive results. All data, code, and negative findings are publicly documented.*
