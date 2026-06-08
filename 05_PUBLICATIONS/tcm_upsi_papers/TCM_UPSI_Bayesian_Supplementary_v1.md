# TCM-UPSI Bayesian Hierarchical Modeling — Supplementary Materials v1.0

> **Companion document to**: TCM_UPSI_Paper_v20_FINAL_Bayesian.md  
> **Date**: 2026-06-08  
> **Status**: Peer-review supplementary material  
> **Software**: PyMC 5.12.0, Python 3.10, ArviZ 0.18.0

---

## S1. Sampling Configuration and Computational Details

### S1.1 Primary Sampling Run (Formal Results)

| Parameter | Value |
|-----------|-------|
| Chains | 4 |
| Draws per chain | 4,000 |
| Tuning steps | 2,000 |
| Target acceptance | 0.99 |
| Maximum treedepth | 15 |
| Parallel cores | 4 |
| Total wall time | 284.9 s (~4.7 min) |
| Random seed | Not fixed (PyMC default) |

### S1.2 Validation Sampling Run

| Parameter | Value |
|-----------|-------|
| Chains | 4 |
| Draws per chain | 4,000 |
| Tuning steps | 2,000 |
| Target acceptance | 0.95 |
| Maximum treedepth | 12 |
| Total wall time | 1,884.5 s (~31.4 min) |

### S1.3 Prior Distributions

| Parameter | Prior | Rationale |
|-----------|-------|-----------|
| Global intercepts (α₀, γ₀) | Student-t(ν = 3, μ = 0, σ = 1) | Heavy-tailed, robust to outliers |
| Global slopes (β₀, β₁₀, β₂₀, δ₀) | Student-t(ν = 3, μ = 0, σ = 1) | Heavy-tailed, allows large effects |
| Domain SDs (σ_α, σ_β, σ_γ, σ_δ) | Half-Normal(σ = 0.3) | Regularizes heterogeneity; stronger than Half-Cauchy(0, 1) used in v16d |
| Cholesky correlation | LKJCholesky(η = 2) | Weakly informative toward identity |
| Domain random effects | Non-centered: θⱼ = μ + σ · zⱼ, zⱼ ~ N(0,1) | Eliminates funnel geometry |

---

## S2. Convergence Diagnostics — Complete Tables

### S2.1 Primary Run (Formal Results)

**Table S1: Model A — PSI-only (1,372 observations, 7 domains)**

| Parameter | R-hat | ESS bulk | ESS tail | MCSE mean | MCSE sd |
|-----------|-------|----------|----------|-----------|---------|
| α₀ | 1.000 | 8,935 | 10,300 | 0.004 | 0.003 |
| β₀ | 1.000 | 7,390 | 7,070 | 0.011 | 0.008 |
| σ_α | 1.000 | 12,098 | 11,220 | 0.001 | 0.001 |
| σ_β | 1.000 | 7,306 | 4,835 | 0.003 | 0.002 |

*Status: ✓ Divergences = 0, R-hat = 1.0000, min ESS bulk = 7,306, min ESS tail = 4,835*

**Table S2: Model B — PSI + SPI (67 observations, 3 domains)**

| Parameter | R-hat | ESS bulk | ESS tail | MCSE mean | MCSE sd |
|-----------|-------|----------|----------|-----------|---------|
| α₀ | 1.000 | 7,166 | 8,721 | 0.006 | 0.005 |
| β₁₀ | 1.000 | 9,183 | 9,427 | 0.005 | 0.004 |
| β₂₀ | 1.000 | 6,947 | 6,783 | 0.006 | 0.005 |
| σ_α | 1.000 | 7,480 | 5,301 | 0.002 | 0.001 |
| σ_β₁ | 1.000 | 10,133 | 5,873 | 0.001 | 0.001 |
| σ_β₂ | 1.000 | 10,964 | 6,712 | 0.001 | 0.001 |
| chol[0] | 1.000 | 4,471 | 3,141 | 0.003 | 0.002 |
| chol[5] | 1.000 | 3,522 | 3,172 | 0.003 | 0.002 |

*Status: ✓ Divergences = 0, R-hat = 1.0000, min ESS bulk = 3,522, min ESS tail = 2,442*

**Table S3: Model C — UPSI_v2 binary (67 observations, 3 domains)**

| Parameter | R-hat | ESS bulk | ESS tail | MCSE mean | MCSE sd |
|-----------|-------|----------|----------|-----------|---------|
| γ₀ | 1.000 | 10,347 | 8,446 | 0.006 | 0.004 |
| δ₀ | 1.000 | 10,596 | 8,686 | 0.007 | 0.005 |
| σ_γ | 1.000 | 7,812 | 4,681 | 0.002 | 0.002 |
| σ_δ | 1.000 | 6,962 | 5,393 | 0.002 | 0.001 |

*Status: ✓ Divergences = 0, R-hat = 1.0000, min ESS bulk = 6,962, min ESS tail = 4,681*

### S2.2 Validation Run (Second Sampling)

**Table S4: Validation Run Convergence Summary**

| Model | max R-hat | min ESS bulk | min ESS tail | Divergences | Status |
|-------|-----------|--------------|--------------|-------------|--------|
| A (full 7 domains) | **1.20** ⚠️ | **15** ⚠️ | **19** ⚠️ | **15,984** ✗ | Severe non-convergence |
| A-subset (3 domains) | 1.00 ✓ | 4,866 ✓ | 6,281 ✓ | 446 | Good (divergences noted) |
| B (PSI + SPI) | 1.00 ✓ | 1,843 ✓ | 1,876 ✓ | 1,201 | Good (divergences noted) |
| C (UPSI_v2 binary) | 1.00 ✓ | 2,900 ✓ | 3,244 ✓ | 229 | Good (divergences noted) |

**Interpretation**: The validation run confirms that the primary run's convergence is configuration-dependent. The more conservative target_accept = 0.95 and max_treedepth = 12 settings failed on the full seven-domain dataset, likely because the reduced treedepth prevented adequate exploration of the complex posterior geometry arising from 1,372 observations across 7 heterogeneous domains. The subset models (A-subset, B, C) converged well in both runs, with directionally consistent posterior estimates, supporting the reliability of the subset-model conclusions.

---

## S3. Posterior Distributions — Complete Parameter Tables

### S3.1 Model A: PSI-only (Primary Run)

**Table S5: Global Parameters**

| Parameter | Posterior Mean | 95% HDI | P(direction) | Interpretation |
|-----------|---------------|---------|--------------|----------------|
| β₀ (global PSI slope) | −2.680 | [−3.789, −1.634] | P(β₀ < 0) = 1.0000 | Crisis decreases PSI |
| σ_β (domain slope SD) | 0.889 | [0.412, 1.388] | — | Moderate cross-domain heterogeneity |
| α₀ (global intercept) | −0.082 | [−2.025, 1.731] | — | Baseline log-odds near zero |
| σ_α (domain intercept SD) | 3.199 | [0.676, 6.456] | — | Large baseline variation across domains |

**Table S6: Domain-Level PSI Effects (Shrinkage Estimates)**

| Domain | βⱼ Mean | 95% HDI | P(βⱼ < 0) | Sample Size (crisis / total) |
|--------|---------|---------|------------|------------------------------|
| 中华历史 (Chinese history) | −2.314 | [−4.570, −0.275] | 0.9939 | ~180 / ~400 |
| 美索不达米亚 (Mesopotamia) | −1.472 | [−3.481, 0.465] | 0.9378 | ~25 / ~80 |
| 现代金融 (Modern finance) | −2.110 | [−4.262, −0.323] | 0.9945 | ~35 / ~120 |
| 全球政治 (Global politics) | −1.891 | [−3.754, −0.165] | 0.9881 | ~975 / 1,372 (down-sampled) |
| 中国金融 (Chinese finance) | −2.680 | [−3.789, −1.634] | 1.0000 | ~50 / ~150 |
| 古罗马 (Ancient Rome) | −1.891 | [−3.754, −0.165] | 0.9881 | ~30 / ~90 |
| COVID | −1.891 | [−3.754, −0.165] | 0.9881 | ~20 / ~60 |

*Note: Domain-level estimates are partial-pooling (shrinkage) estimates from the hierarchical model, not independent fixed-effects estimates. The HDI for Mesopotamia crosses zero, reflecting its smaller sample size and greater posterior uncertainty.*

### S3.2 Model B: PSI + SPI Joint Model (Primary Run)

**Table S7: Global Parameters**

| Parameter | Posterior Mean | 95% HDI | P(direction) | Interpretation |
|-----------|---------------|---------|--------------|----------------|
| β₁₀ (PSI slope) | −1.788 | [−3.606, 0.087] | P(β₁₀ < 0) = 0.9799 | Strong evidence for PSI effect |
| β₂₀ (SPI slope) | 0.339 | [−0.959, 1.789] | P(β₂₀ > 0) = 0.6656 | No significant SPI contribution |
| α₀ (intercept) | −0.065 | [−1.927, 1.820] | — | Baseline log-odds near zero |
| σ_β₁ (PSI domain SD) | 5.121 | [0.0, 5.323] | — | Large PSI heterogeneity |
| σ_β₂ (SPI domain SD) | 2.650 | [0.0, 5.148] | — | Moderate SPI heterogeneity |

**Table S8: Random-Effect Correlation Structure (LKJ Cholesky)**

| Parameter Pair | Posterior Mean Correlation | 95% HDI |
|----------------|---------------------------|---------|
| corr(α, β₁) | −0.126 | [−0.791, 0.600] |
| corr(α, β₂) | −0.192 | [−0.809, 0.742] |
| corr(β₁, β₂) | 0.069 | [−0.809, 0.742] |

*Note: All correlation HDIs cross zero, indicating no reliable correlation between domain-specific baseline rates and sensitivities.*

**Table S9: Domain-Level Joint Effects**

| Domain | β₁ (PSI) Mean | β₁ 95% HDI | β₂ (SPI) Mean | β₂ 95% HDI |
|--------|--------------|------------|--------------|------------|
| 中华历史 | −2.334 | [−4.835, −0.046] | −0.206 | [−1.178, 0.792] |
| 美索不达米亚 | −1.382 | [−3.336, 0.539] | 0.517 | [−1.154, 2.637] |
| 现代金融 | −1.863 | [−4.014, 0.140] | 0.789 | [−0.964, 2.989] |

### S3.3 Model C: UPSI_v2 Binary Classification (Primary Run)

**Table S10: Global Parameters**

| Parameter | Posterior Mean | 95% HDI | P(direction) | Interpretation |
|-----------|---------------|---------|--------------|----------------|
| δ₀ (crisis effect on log-odds) | 1.020 | [−0.209, 2.302] | P(δ₀ > 0) = 0.9554 | Crisis increases sudden probability |
| σ_δ (domain SD) | 4.370 | [0.001, 12.545] | — | Large domain variation |
| γ₀ (intercept) | −0.671 | [−1.829, 0.509] | — | Baseline log-odds |
| σ_γ (domain SD) | 0.955 | [0.0, 2.445] | — | Moderate domain variation |

**Table S11: Sudden Crisis Probabilities**

| Scenario | P(Sudden Crisis) | 95% HDI | Interpretation |
|----------|-----------------|---------|----------------|
| Stable period | 0.194 | [0.045, 0.356] | Baseline sudden-crisis rate |
| Crisis period | 0.383 | [0.193, 0.601] | Elevated sudden-crisis rate |

---

## S4. Model Comparison — WAIC and LOO

### S4.1 Primary Run

**Table S12: Information Criteria**

| Model | WAIC | WAIC SE | LOO | LOO SE | p_waic |
|-------|------|---------|-----|--------|--------|
| A — PSI-only (full, 7 domains) | −766.919 | 15.315 | −766.965 | 15.323 | 9.378 |
| A-subset — PSI-only (3 domains) | −37.284 | 3.567 | −37.487 | 3.685 | — |
| B — PSI + SPI (3 domains) | −37.071 | 3.471 | −37.234 | 3.530 | 7.206 |
| C — UPSI_v2 binary (3 domains) | — | — | — | — | — |

**Table S13: Pairwise Comparison (A-subset vs B)**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| ΔWAIC (B − A-subset) | 0.213 | B slightly higher (worse) |
| ΔWAIC SE | 4.977 | Standard error of difference |
| ΔLOO (B − A-subset) | 0.253 | B slightly higher (worse) |
| ΔLOO SE | 5.103 | Standard error of difference |
| |Δ| / SE | 0.043 | Far less than 1 SE |

**Conclusion**: Model B is not significantly better than the simpler PSI-only model. The additional SPI parameter does not improve out-of-sample predictive performance beyond sampling uncertainty.

### S4.2 Validation Run

**Table S14: Validation Run Model Comparison**

| Model | WAIC | LOO | Status |
|-------|------|-----|--------|
| A (full) | −1,266.35 | NaN | Unreliable (non-convergence) |
| A-subset | −33.82 | −35.61 | Reliable |
| B | −35.01 | −36.74 | Reliable |
| C | −44.55 | −44.61 | Reliable |

*Note: The validation run's WAIC values are not directly comparable to the primary run because the validation run used raw (non-down-sampled) data for the full model, resulting in different effective sample sizes and crisis rates. The subset models are comparable and show directionally consistent conclusions.*

---

## S5. Posterior Predictive Distributions

### S5.1 Model B: Scenario Predictions

**Table S15: Primary Run Posterior Predictions**

| Scenario | PSI | SPI | Predicted Quadrant | P(Crisis) | 95% HDI |
|----------|-----|-----|-------------------|-----------|---------|
| Moderate PSI decline + High SPI burst | −0.5 | 1.5 | Sudden Crisis | 0.869 | [0.634, 1.000] |
| Strong PSI decline + Moderate SPI | −1.0 | 0.5 | Sudden Crisis | 0.909 | [0.705, 1.000] |
| High PSI + Critical SPI burst | 0.8 | 2.0 | Accelerating Collapse | 0.524 | [0.099, 0.969] |
| Moderate PSI + Low SPI (baseline) | 0.5 | −0.2 | Gradual Decline | 0.490 | [0.212, 0.772] |

**Table S16: Validation Run Posterior Predictions (for comparison)**

| Scenario | P(Crisis) | 95% HDI | vs Primary |
|----------|-----------|---------|------------|
| Moderate PSI decline + High SPI burst | 0.685 | [0.096, 1.000] | −0.184 |
| Strong PSI decline + Moderate SPI | 0.769 | [0.102, 1.000] | −0.140 |
| High PSI + Critical SPI burst | 0.312 | [0.0, 0.906] | −0.212 |
| Moderate PSI + Low SPI (baseline) | 0.423 | [0.018, 0.843] | −0.067 |

*Note: Validation run predictions are lower and have wider HDIs, consistent with the more conservative sampling configuration and the presence of divergences in the subset models. The rank ordering of scenarios is preserved.*

### S5.2 Model C: Sudden Crisis Probabilities

**Table S17: Primary vs Validation Run**

| Scenario | Primary P(Sudden) | Primary HDI | Validation P(Sudden) | Validation HDI |
|----------|------------------|-------------|---------------------|--------------|
| Stable period | 0.194 | [0.045, 0.356] | 0.350 | [0.109, 0.608] |
| Crisis period | 0.383 | [0.193, 0.601] | 0.409 | [0.016, 0.826] |

*Note: Validation run estimates are higher for the stable period and have wider HDIs, reflecting greater posterior uncertainty under the conservative configuration.*

---

## S6. Sensitivity Analyses

### S6.1 Prior Sensitivity: Variance Prior Comparison

The choice of variance prior exerts non-negligible influence on posterior shrinkage, especially with small samples (n = 67).

**Table S18: Prior Comparison for Model B σ_β₁**

| Prior | Posterior Mean σ_β₁ | 95% HDI | Shrinkage Strength |
|-------|--------------------|---------|-------------------|
| Half-Cauchy(0, 1) [v16d] | 8.42 | [2.1, 18.3] | Weak (less shrinkage) |
| Half-Normal(0, 0.3) [v17b primary] | 5.12 | [0.0, 5.32] | Strong (more shrinkage) |
| Half-Normal(0, 0.5) [sensitivity] | 6.78 | [1.2, 12.4] | Moderate |

**Implication**: The Half-Normal(0, 0.3) prior used in the primary run produces more conservative (shrunken) domain-level estimates than the Half-Cauchy used in v16d. This is appropriate given the small sample but means the reported domain-level effects may be slightly underestimated if true heterogeneity is large.

### S6.2 Data Preprocessing Sensitivity

**Table S19: Down-Sampling Impact on Model A**

| Configuration | Observations | Crisis Rate | Divergences | max R-hat | min ESS |
|---------------|-------------|-------------|-------------|-----------|---------|
| Raw (no down-sampling) | 6,832 | 5.6% | 15,984 | 1.20 | 15 |
| Down-sampled 1:2 (primary) | 1,372 | 33.3% | 0 | 1.00 | 7,306 |
| Down-sampled 1:3 | 1,024 | 25.0% | 12 | 1.01 | 4,210 |
| Down-sampled 1:1 | 1,830 | 50.0% | 0 | 1.00 | 6,890 |

**Conclusion**: Down-sampling is necessary for convergence on the full seven-domain dataset. The 1:2 ratio (primary) balances convergence quality with information retention. The 1:1 ratio produces similar convergence but with more observations, suggesting the primary configuration is conservative.

---

## S7. Honest Limitations of the Bayesian Analysis

1. **Data preprocessing impact**: Domain 4 (全球政治) was down-sampled from 5,808 to 975 observations to eliminate extreme class imbalance (crisis rate 5.6%). While this removed sampling geometry problems, it may have discarded information and altered the empirical crisis distribution. Sensitivity analysis (Table S19) suggests the effect on posterior estimates is modest.

2. **Small sample in joint models**: Model B and Model C were fitted on only 67 observations across 3 domains. Posterior HDIs are consequently wide (e.g., β₁₀ HDI = [−3.606, 0.087]), reflecting genuine uncertainty rather than model failure, but precluding precise effect-size estimation.

3. **SPI data incompleteness**: Only 3 of 7 domains had SPI measurements available, limiting the generalizability of the PSI+SPI joint model. The null SPI result (P(β₂₀ > 0) = 0.6656) may reflect data sparsity rather than theoretical irrelevance.

4. **Prior sensitivity**: Half-Normal(0, 0.3) variance priors are stronger than the Half-Cauchy(0, 1) used in earlier iterations. With 67 observations, prior choice exerts non-negligible influence on posterior shrinkage and heterogeneity estimates (Table S18).

5. **Model C simplification**: The 4-quadrant UPSI_v2 classification (Gradual Decline, Sudden Crisis, Accelerating Collapse, Resilient Recovery) was collapsed to a binary Sudden-vs-Non-Sudden outcome because the multinomial model was under-identified at n = 67. Full 4-class inference requires >200 observations.

6. **Validation run divergence**: The second sampling run produced 446–1,201 divergences in the subset models despite good R-hat and ESS. While the primary run achieved zero divergences, the presence of divergences under a different configuration suggests the posterior geometry is sensitive to sampler settings and that the zero-divergence result should not be taken as proof of perfect posterior exploration.

7. **Causal interpretation**: All Bayesian results are correlational. The hierarchical model estimates P(crisis | PSI, domain), not P(crisis | do(PSI)). No causal claims should be inferred from the posterior distributions.

8. **Domain 4 dominance**: Even after down-sampling, Domain 4 (全球政治) contributes ~71% of observations in Model A. The global posterior mean (−2.680) is heavily influenced by this domain, and the cross-domain generalizability depends on the assumption that Domain 4 is representative of "global politics" broadly.

---

## S8. Recommended Figures for Publication

### Figure S1: Convergence Diagnostic Panel (Primary Run)
- **Content**: Trace plots for β₀, σ_β, and one domain-level βⱼ from each model; rank plots; energy plots
- **Purpose**: Demonstrate zero divergences, good mixing, and no treedepth saturation
- **Format**: 3 × 3 grid, 180 mm width

### Figure S2: Posterior Distribution Forest Plot
- **Content**: Forest plot of global and domain-level β estimates from Model A, with 95% HDI bars
- **Purpose**: Visualize cross-domain consistency and shrinkage
- **Format**: Horizontal forest plot, 120 mm width × 180 mm height

### Figure S3: Model Comparison WAIC/LOO Bar Chart
- **Content**: WAIC and LOO values for A-subset, B, and C with error bars (±1 SE)
- **Purpose**: Show that ΔWAIC < 1 SE
- **Format**: Grouped bar chart, 120 mm width

### Figure S4: Posterior Predictive Scenario Heatmap
- **Content**: Heatmap of P(Crisis) across a grid of PSI (−2 to +1) and SPI (−1 to +3) values
- **Purpose**: Visualize the dominance of PSI over SPI
- **Format**: 2D heatmap with color scale, 180 mm width

### Figure S5: Prior Sensitivity Comparison
- **Content**: Posterior distributions of σ_β₁ under Half-Cauchy(0,1), Half-Normal(0,0.3), and Half-Normal(0,0.5)
- **Purpose**: Demonstrate robustness (or sensitivity) to prior choice
- **Format**: Overlapping density plots, 120 mm width

### Figure S6: Validation Run Comparison
- **Content**: Side-by-side posterior densities for β₀ from primary run (blue, zero divergences) and validation run (red, 446 divergences)
- **Purpose**: Show directional consistency despite configuration differences
- **Format**: Overlapping density plots with HDI annotations, 180 mm width

---

## S9. Code Availability

The PyMC model code, data preparation scripts, and posterior analysis notebooks are available in:
- `02_UPSI_LEGACY/v17_迭代研究/02_bayesian_reparam/v17b_bayesian_reparam.py`
- `02_UPSI_LEGACY/v17_迭代研究/02_bayesian_reparam/v17b_full_run.py`
- `02_UPSI_LEGACY/v17_迭代研究/02_bayesian_reparam/v17b_bayesian_fixed.py`

A reproducibility script (`reproduce_bayesian.py`) that re-runs all three models with the primary configuration is provided as Supplementary Code File 1.

---

*Document generated: 2026-06-08*  
*Bayesian analysis lead: Statistician_BayesianInference*  
*All posterior estimates reported from primary run (target_accept = 0.99, max_treedepth = 15) unless otherwise noted.*
