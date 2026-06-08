# v17d Figure Selection — Curated for Nature Letter

**Version**: v17.0  
**Date**: 2026-06-05  
**Target**: *Nature* Letter (max 4–6 figures)  
**Selected for main text**: 4 figures  
**SI candidates**: 1 figure + remaining figures from v4–v6

---

## Main Text Figures (4)

### Figure 1 | Cross-Domain Validation of UPSI Across 8 Civilizations

**Source file**: `01_manuscript/figures/figure1_domain_validation.png`  
**Original source**: `v4/figures/Figure1_PSI_Timeline.png`  
**Size**: ~211 KB  
**Dimensions**: 1200 × 800 px (estimated)

**Caption draft**:
> **Figure 1 | Cross-domain validation of UPSI across 8 civilizations.** (a) Three-dimensional PSI components (Material, Fragmentation, Disengagement) plotted as a ternary diagram showing crisis clusters (red) vs stable clusters (blue) for each of the 8 domains. (b) Bar chart of recall by domain: 100% (Chinese history, ancient Rome, Chinese finance, news sentiment), 91% (global politics), 82% (global finance), 75% (Mesopotamia, Seshat). (c) Time series of global-finance UPSI (1927–2026) with 24 known crises highlighted; UPSI < −0.5 threshold marked as horizontal line. **Totals**: ~3.6 million observations, 5,500 years, 8 domains. Six domains achieve ≥75% recall, four achieve 100%.

**Why it matters**: This is the **central empirical result** of the paper. It demonstrates that a single three-dimensional index structure captures crises across financial markets, political regimes, and ancient civilizations with no domain-specific parameter tuning. The 8-domain bar chart is immediately comprehensible and visually striking.

**Nature fit**: High. Nature Letters favor concise, high-impact figures that convey the main result at a glance.

---

### Figure 2 | PSI–SPI Mathematical Duality and Four-Quadrant Crisis Classifier

**Source file**: `01_manuscript/figures/figure2_psi_spi_duality.png`  
**Original source**: `v14_迭代研究/03_upsi_v2/v14c_upsi_v2_plots/phase_portrait_real.png`  
**Size**: ~189 KB  
**Dimensions**: 800 × 800 px (estimated)

**Caption draft**:
> **Figure 2 | PSI–SPI mathematical duality and four-quadrant crisis classifier.** (a) Phase portrait of PSI (level, x-axis) vs SPI (rate of change, y-axis) for Chinese history (Tang dynasty, 31 decades). Quadrants: I = Stable (PSI low, SPI low), II = Gradual Decline (PSI high, SPI low), III = Sudden Crisis (PSI low, SPI high), IV = Accelerating Collapse (PSI high, SPI high). (b) Time-series quadrant timeline showing regime transitions for Northern Song (1127 Jingkang catastrophe flagged as Sudden Crisis). (c) Physical analogy: PSI = temperature (system state), SPI = dT/dt (rate of change). Both are necessary for complete monitoring.

**Why it matters**: This figure introduces the **key conceptual innovation** of the paper—the mathematical duality between level-based PSI (low-pass filter) and velocity-based SPI (high-pass filter). The four-quadrant taxonomy (Stable, Gradual Decline, Sudden Crisis, Accelerating Collapse) is a novel contribution that no prior crisis-detection framework possesses. The phase-portrait visualization is intuitive and physics-inspired.

**Nature fit**: High. The duality framing ("temperature vs. rate of temperature change") is accessible to Nature's broad interdisciplinary readership.

---

### Figure 3 | Physical-Statistical Spectrum of UPSI Series

**Source file**: `01_manuscript/figures/figure3_upsi_v2_quadrants.png`  
**Original source**: `v14_迭代研究/03_upsi_v2/v14c_upsi_v2_plots/combined_chinese_quadrant_legend.png`  
**Size**: ~106 KB  
**Dimensions**: 1200 × 600 px (estimated)

**Caption draft**:
> **Figure 3 | Physical-statistical spectrum of UPSI series and unexpected findings.** (a) DFA log-log plot of S&P 500 PSI (1927–2026), slope H = 1.566 (95% CI [1.50, 1.63]), consistent with fractional Brownian motion. (b) Whittle power-spectrum estimate, slope β = 4.00 (1/f⁴ long-memory signature). (c) DFA on log returns, slope H = 0.453 (95% CI [0.40, 0.50]), consistent with efficient-market random-walk hypothesis. (d) VIX–S&P 500 cross-correlation peaking at τ = +17 days (r = −0.235), challenging the view that VIX merely reflects realized volatility. (e) Gold–S&P 500 cross-correlation peaking at τ = −1 day (r = +0.346), showing gold acts as crisis follower, not hedge. (f) PageRank of 20-asset PSI network: European trio (DE-DAX, FR-CAC, UK-FTSE) surpass US-SP500 as systemic-risk epicenters.

**Why it matters**: This figure bundles **three of the seven unexpected findings** into a single multi-panel figure, maximizing information density per Nature's limited figure allowance. The fBm + EMH decomposition is a classical result presented as descriptive statistical signature, while the VIX lead and gold lag challenge conventional market microstructure theory.

**Nature fit**: High. Multi-panel figures are standard in Nature Letters. The combination of statistical physics (DFA, Whittle) and financial econometrics appeals to Nature's interdisciplinary scope.

> **Note**: The original manuscript describes Figure 3 as purely the physical-statistical spectrum (DFA + Whittle). However, to stay within the 4-figure limit while showcasing the unexpected findings, we propose merging the spectrum panels (a–c) with the lead-lag/network panels (d–f). Alternatively, split into two figures if Nature allows 5.

---

### Figure 4 | Real-Time UPSI Dashboard (Operational Deployment)

**Source file**: `01_manuscript/figures/figure4_dashboard.png`  
**Original source**: `v5/dashboard_v5.png`  
**Size**: ~244 KB  
**Dimensions**: 1600 × 900 px (estimated)

**Caption draft**:
> **Figure 4 | Real-time UPSI Dashboard (operational deployment).** Screenshot of the live Dashboard (35 KB HTML, zero-cost GitHub Actions + gh-pages deployment). **Top**: current PSI for 20 global assets, color-coded by distress level (green = stable, yellow = elevated, red = critical). **Middle-left**: multi-market synchronization heatmap showing lag-0 cross-correlations. **Middle-right**: high-priority news flashes (Jin10 MCP, Star ≥ 4) in the last 24 hours. **Bottom**: FRED macro indicators (industrial output, unemployment, consumer confidence) overlaid on Chinese-finance PSI. The Dashboard consumes only free public APIs and is ready for central-bank deployment as a monitoring tool, not a decision-making oracle.

**Why it matters**: The Dashboard demonstrates **real-world applicability** and policy relevance. It shows that UPSI is not merely a theoretical construct but an operational monitoring system that can be deployed at zero cost by emerging-market regulators lacking Bloomberg terminals. The screenshot provides tangible evidence of the "synchronizer, not predictor" philosophy in action.

**Nature fit**: High. Nature values research with immediate practical implications. The Dashboard screenshot is concrete and visually compelling.

---

## SI Candidate Figures

### Figure 5 | Seshat Global History Databank Coverage and Validation

**Source file**: `01_manuscript/figures/figure5_seshat_map.png`  
**Status**: ⚠️ **No static PNG exists**

**Proposed content**:
- World map showing 5 validated NGAs: Upper Egypt (Africa), Latium (Europe), Susiana (Asia), Middle Yellow River Valley (Asia), Valley of Oaxaca (Americas)
- Validation table: 6/8 crises detected, 75% recall, 5.8% precision
- Timeline: 337 centuries, -7800 to 1900 CE

**Options**:
1. **Generate map**: Use Python (cartopy or basemap) to create a world map with NGA markers. Estimated effort: 2 hours.
2. **Omit figure, use table**: Replace with a simple markdown table in the SI. This is acceptable since Seshat is a proof-of-concept, not a primary domain.
3. **Reference external Seshat visualizations**: Link to seshatdatabank.info maps.

**Recommendation**: Option 2 (table in SI) for speed. Option 1 if time permits before submission.

---

## Remaining Figures (SI or Omitted)

The following figures from v4–v6 are valuable but omitted from the main text due to the 4-figure limit. They should be included in the SI or referenced in text:

| Figure | Source | Content | SI Section |
|--------|--------|---------|------------|
| v4 Figure2 | `v4/figures/Figure2_Crisis_Lead.png` | Crisis lead time distribution | S10 |
| v4 Figure3 | `v4/figures/Figure3_Dynasty_Comparison.png` | Dynasty PSI boxplot | S14 |
| v4 Figure5 | `v4/figures/Figure5_PSI_to_Crisis.png` | PSI-to-crisis mapping | S10 |
| v4 Figure6 | `v4/figures/Figure6_IPW_Correction.png` | IPW correction effect | S8 |
| v4 Figure7 | `v4/figures/Figure7_Network_Density.png` | Network density over time | S15 |
| v4 Figure8 | `v4/figures/Figure8_Cross_Civilization.png` | Cross-civilization convergence | S14 |
| v4 Figure9 | `v4/figures/Figure9_Rome_PSI.png` | Roman PSI timeline | S4 |
| v4 Figure10 | `v4/figures/Figure10_Shanghai_PSI.png` | Shanghai PSI | S5 |
| v4 Figure11 | `v4/figures/Figure11_Cross_Market_PSI.png` | Cross-market PSI | S5 |
| v4 Figure12 | `v4/figures/Figure12_PSI_Future_Returns.png` | PSI future returns | S5 |
| v4 Figure13 | `v4/figures/Figure13_Global_PSI.png` | Global PSI timeline | S5 |
| v4 Figure14 | `v4/figures/Figure14_Lead_Lag.png` | Lead-lag correlations | S16 |
| v4 Figure15 | `v4/figures/Figure15_Recall_Lead.png` | Recall vs lead time | S10 |
| v6 Figure16 | `v6/figures/Figure16_ROC_Curves.png` | ROC curves | S10 |
| v6 Figure17 | `v6/figures/Figure17_Threshold_F1.png` | Threshold F1 optimization | S10 |
| v12 series | `v12_迭代研究/01_psi_improvement/*.png` | Mesopotamian period comparisons | S3 |
| v14 UPSI_v2 | `v14_迭代研究/03_upsi_v2/v14c_upsi_v2_plots/*.png` | Dynasty phase portraits | S20 |

---

## Figure Assembly Workflow

1. **Verify resolution**: All main-text figures must be ≥300 dpi. Current PNGs are screen-capture quality (~96 dpi). For submission, regenerate from source code at 300 dpi or use vector formats (SVG/PDF).
2. **Caption consistency**: Ensure all captions follow Nature style (sentence case, no period at end of title, detailed legend).
3. **Color blindness**: Use colorblind-safe palettes (viridis or ColorBrewer). Current figures use default matplotlib colors—verify accessibility.
4. **Font size**: Minimum 8 pt font in figures at final print size.
5. **File naming**: Nature prefers `fig1.png`, `fig2.png`, etc. Rename before upload.

---

## Recommended Figure Order for Submission

1. `fig1_domain_validation.png` (Figure 1)
2. `fig2_psi_spi_duality.png` (Figure 2)
3. `fig3_spectrum_findings.png` (Figure 3 — merged spectrum + unexpected findings)
4. `fig4_dashboard.png` (Figure 4)

**SI figure**: `figS1_seshat_map.png` (if generated) or table replacement.

---

*Figure selection completed: 2026-06-05*  
*4 main-text figures selected, 1 SI candidate, 16 figures referenced for SI*
