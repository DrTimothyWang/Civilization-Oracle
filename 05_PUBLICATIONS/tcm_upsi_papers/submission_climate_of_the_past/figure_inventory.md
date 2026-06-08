# Figure Inventory

## Overview

This document provides a complete inventory of all figures in the manuscript **"TCM-UPSI: A Machine Learning Framework for Historical Crisis Risk Assessment Integrating Traditional Chinese Medicine Cyclical Theory and Climate Indices"** submitted to *Climate of the Past*.

Each figure is described with its purpose, key content, approximate dimensions, and color requirements.

---

## Figure 1: WuYun Cycle Timeline and Crisis Density (1906–2025)

**Type**: Timeline / stacked area chart
**Dimensions**: 180 mm × 120 mm (2-column width)
**Color**: Yes (5 WuYun element colors: Wood=green, Fire=red, Earth=yellow, Metal=gray, Water=blue)

**Content**:
- Horizontal timeline from 1906 to 2025
- Background color bands indicating WuYun element for each year
- Overlay: annual crisis count (line or bar)
- Major crisis annotations: 1918 Spanish Flu, 1929 Great Depression, 1939 WWII, 1966 Cultural Revolution, 1989 Tiananmen, 2008 Financial Crisis, 2019 COVID-19
- Inset: 60-year cycle diagram showing element sequence

**Purpose**: Visualizes the 60-year WuYun cycle and its temporal relationship to major historical crises. Provides intuitive context for the cyclical theory.

**Source data**: `SI_S14_Figure_Source_Data/Figure1_WuYun_Timeline.csv`

---

## Figure 2: Inverse Probability Weighting (IPW) Correction Effect

**Type**: Before/after bar chart
**Dimensions**: 180 mm × 90 mm (2-column width)
**Color**: Yes (before=blue, after=orange)

**Content**:
- Left panel: Event density by WuYun element before IPW correction
- Right panel: Event density by WuYun element after IPW correction
- Error bars: 95% confidence intervals
- Annotation: chi-square test results, p-values
- Dashed line: uniform distribution expectation (20% per element)

**Purpose**: Demonstrates the bias correction methodology and its impact on event distribution.

**Source data**: `SI_S14_Figure_Source_Data/Figure2_IPW_Correction.csv`

---

## Figure 3: PSI Distribution by Historical Dynasty/Period

**Type**: Boxplot / violin plot
**Dimensions**: 180 mm × 120 mm (2-column width)
**Color**: Yes (period-specific colors)

**Content**:
- X-axis: Historical periods (Qing late, Republic, PRC early, PRC reform, Post-2000)
- Y-axis: Pattern-Space Integration (PSI) score distribution
- Boxplots: median, quartiles, whiskers, outliers
- Overlay: individual data points (jittered)
- Annotation: Kruskal-Wallis or ANOVA test result

**Purpose**: Shows temporal variation in composite risk scores across historical eras.

**Source data**: `SI_S14_Figure_Source_Data/Figure3_Dynasty_Boxplot.csv`

---

## Figure 4: Feature Importance Comparison (Annual vs. Monthly Models)

**Type**: Horizontal bar chart / grouped bar chart
**Dimensions**: 180 mm × 150 mm (2-column width)
**Color**: Yes (temporal=blue, climate=red, WuYun=green, LiuQi=purple, cyclical=orange)

**Content**:
- Left panel: Annual model feature importance (top 15 features)
- Right panel: Monthly model feature importance (top 15 features)
- Feature categories color-coded
- Percentage labels on bars
- Annotation: cumulative importance by category

**Purpose**: Compares predictive contributions across resolutions and identifies dominant feature classes.

**Source data**: `SI_S14_Figure_Source_Data/Figure4_Feature_Importance.csv`

---

## Figure 5: ROC Curves for All Validation Scenarios

**Type**: ROC curve / multi-line plot
**Dimensions**: 180 mm × 180 mm (2-column width, square)
**Color**: Yes (internal=green, UCDP=red, earthquake=blue, epidemic=orange, random=gray dashed)

**Content**:
- X-axis: False positive rate (0–1)
- Y-axis: True positive rate (0–1)
- Curves: Internal DB (AUC=0.9538), Monthly (AUC=0.9941), UCDP (AUC=0.5547), Earthquake (AUC=0.3333), Epidemic (p=0.3830)
- Diagonal reference line: random classifier (AUC=0.5)
- Legend with AUC values and 95% CIs (where available)

**Purpose**: Visualizes discriminative performance across all validation scenarios, highlighting the generalization failure.

**Source data**: `SI_S14_Figure_Source_Data/Figure5_ROC_Curves.csv`

---

## Figure 6: Probability Calibration Reliability Diagram

**Type**: Reliability diagram / bar chart with diagonal reference
**Dimensions**: 90 mm × 90 mm (1-column width)
**Color**: Yes (bars=blue, diagonal=gray dashed, perfect calibration=green line)

**Content**:
- X-axis: Mean predicted probability (10 bins: 0–0.1, 0.1–0.2, ..., 0.9–1.0)
- Y-axis: Observed frequency (fraction of positives)
- Bars: observed frequency per bin
- Error bars: 95% confidence intervals (Clopper-Pearson or bootstrap)
- Diagonal: perfect calibration line
- Histogram: sample count per bin (small inset or secondary y-axis)
- Annotation: ECE = 0.130, MCE = 0.287

**Purpose**: Demonstrates the calibration gap—high discrimination but poor probability calibration.

**Source data**: `SI_S14_Figure_Source_Data/Figure6_Calibration_Plot.csv`

---

## Figure 7: Temporal Stability — Cross-Validation AUC by Era

**Type**: Line plot with confidence bands
**Dimensions**: 180 mm × 120 mm (2-column width)
**Color**: Yes (expanding window=blue, sliding window=red, combined=purple)

**Content**:
- X-axis: Test period start year (1951, 1961, 1971, 1981, 1991, 2001)
- Y-axis: AUC (0.5–1.0)
- Lines: expanding-window AUC, sliding-window AUC
- Shaded regions: ±1 SD or 95% CI
- Horizontal reference: AUC = 0.7 (minimum acceptable)
- Annotation: CV = 13.9%, Modern-Ancient Divergence label

**Purpose**: Shows time-dependent performance and validates the need for periodic retraining.

**Source data**: `SI_S14_Figure_Source_Data/Figure7_CV_Stability.csv`

---

## Figure 8: Regional Monthly Model Performance Comparison

**Type**: Grouped bar chart / radar chart (alternative)
**Dimensions**: 180 mm × 120 mm (2-column width)
**Color**: Yes (Global=black, China=red, Europe=blue, Americas=green, Africa=orange)

**Content**:
- X-axis: Region (Global, China, Europe, Americas, Africa)
- Y-axis: AUC (left) and F1 (right, secondary axis)
- Grouped bars: AUC and F1 per region
- Error bars: bootstrap 95% CIs
- Annotation: test crisis rate per region (small text)
- Dashed line: AUC = 0.98 reference

**Purpose**: Demonstrates geographic robustness of seasonal climate–crisis associations.

**Source data**: `SI_S14_Figure_Source_Data/Figure8_Regional_Comparison.csv`

---

## Figure 9: Granger Causality Test Results Visualization

**Type**: Heatmap / matrix plot
**Dimensions**: 180 mm × 150 mm (2-column width)
**Color**: Yes (significant=red, non-significant=blue, borderline=yellow)

**Content**:
- Rows: Predictor variables (WuYun element, WuYun excess, ENSO, PDO, GISTEMP, NOAA temp, Crisis)
- Columns: Response variables (same set)
- Cells: p-values (color-coded) or F-statistics (size-coded)
- Diagonal: grayed out (self-causality not tested)
- Annotation: all p > 0.05 summary, GISTEMP→crisis p=0.0550 highlighted
- Inset: lag structure (1–3 years) for key tests

**Purpose**: Provides an at-a-glance summary of all causality tests, emphasizing the universal null result.

**Source data**: `SI_S14_Figure_Source_Data/Figure9_Granger_Heatmap.csv`

---

## Figure 10: Epidemic Distribution by WuYun Element

**Type**: Bar chart with expected vs. observed
**Dimensions**: 90 mm × 90 mm (1-column width)
**Color**: Yes (observed=blue, expected=gray dashed, respiratory=red highlight)

**Content**:
- X-axis: WuYun element (Wood, Fire, Earth, Metal, Water)
- Y-axis: Proportion of epidemics (%)
- Bars: observed proportion (n=16)
- Dashed line: expected uniform proportion (20%)
- Error bars: 95% CIs (binomial)
- Annotation: chi-square = 9.625, p = 0.0472
- Small text: TCM correspondence (Lung/respiratory for Metal)

**Purpose**: Presents the exploratory epidemic-WuYun association with appropriate caveats.

**Source data**: `SI_S14_Figure_Source_Data/Figure10_Epidemic_Distribution.csv`

---

## Figure 11: Forward Forecast 2026–2031

**Type**: Timeline / bar chart with uncertainty bands
**Dimensions**: 180 mm × 120 mm (2-column width)
**Color**: Yes (HIGH risk=red, MEDIUM=orange, LOW=green, uncertainty=gray shaded)

**Content**:
- X-axis: Year (2026–2031)
- Y-axis: Predicted probability (0–100%)
- Bars: annual predicted probability
- Color coding: risk class (all HIGH: 86–91%)
- Error bars: 95% prediction intervals (Monte Carlo)
- Background: WuYun element label for each year (Fire, Earth, Metal)
- Annotation: "Ordinal risk scores, not calibrated probabilities"
- Inset: 2026 monthly forecast (mini line plot)

**Purpose**: Communicates the prospective prediction with explicit uncertainty and caveats.

**Source data**: `SI_S14_Figure_Source_Data/Figure11_Forward_Forecast.csv`

---

## Figure 12: Blinded vs. Original Database Comparison

**Type**: Side-by-side bar chart / difference plot
**Dimensions**: 180 mm × 120 mm (2-column width)
**Color**: Yes (original=blue, blinded=orange, difference=red arrow)

**Content**:
- Left panel: Event density by WuYun element — original database (n=1,202)
- Right panel: Event density by WuYun element — blinded database (n=683)
- Middle panel: Difference (original − blinded) with significance stars
- Annotation: r = −0.189 (blinded), selection bias confirmed
- Dashed line: uniform expectation (20%)

**Purpose**: Provides direct visual evidence of selection bias, the central methodological finding.

**Source data**: `SI_S14_Figure_Source_Data/Figure12_Blinded_Comparison.csv`

---

## Summary Table

| Figure | Title | Type | Width | Color | Key Message |
|--------|-------|------|-------|-------|-------------|
| 1 | WuYun Cycle Timeline | Timeline | 2-col | Yes | 60-year cycle context |
| 2 | IPW Correction Effect | Before/after bar | 2-col | Yes | Bias correction methodology |
| 3 | PSI by Dynasty | Boxplot | 2-col | Yes | Temporal risk variation |
| 4 | Feature Importance | Grouped bar | 2-col | Yes | Temporal > Climate > WuYun |
| 5 | ROC Curves | Multi-line | 2-col | Yes | Generalization failure |
| 6 | Calibration Diagram | Reliability | 1-col | Yes | Poor calibration |
| 7 | CV Stability | Line plot | 2-col | Yes | Time-dependent performance |
| 8 | Regional Comparison | Grouped bar | 2-col | Yes | Geographic robustness |
| 9 | Granger Heatmap | Matrix | 2-col | Yes | All null (non-causal) |
| 10 | Epidemic Distribution | Bar chart | 1-col | Yes | Exploratory association |
| 11 | Forward Forecast | Timeline | 2-col | Yes | 2026–2031 HIGH risk |
| 12 | Blinded Comparison | Side-by-side | 2-col | Yes | Selection bias confirmed |

---

## Technical Specifications

- **Resolution**: 300 DPI minimum for print
- **Format**: TIFF (preferred) or high-resolution PNG
- **Color space**: CMYK for print, RGB for online
- **Font**: Arial or Helvetica, minimum 8 pt for labels
- **Line weight**: 0.5–1.0 pt for data lines, 0.25 pt for gridlines
- **Accessibility**: Colorblind-friendly palettes (consider viridis or ColorBrewer schemes); patterns or hatching as secondary encoding

## Data and Code for Reproduction

All figures can be reproduced using:
- Source data: `SI_S14_Figure_Source_Data.zip` (see Supplementary Index)
- Plotting code: `/04_CODE/tcm_upsi/generate_figures.py`
- Dependencies: Matplotlib ≥ 3.7.0, Seaborn ≥ 0.12.0

---

**Contact**: For figure-related queries, contact the corresponding author at [email to be filled].
