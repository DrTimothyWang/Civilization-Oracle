# SI Master Assembly Guide

**Version**: v17.0  
**Date**: 2026-06-05  
**Total Sections**: 22  
**Estimated Length**: ~45 pages  
**Status**: Source materials located across v4–v16 iteration directories

---

## Assembly Workflow

### Step 1: Create Working Directory
```bash
mkdir ~/UPSI_SI_v17
cd ~/UPSI_SI_v17
```

### Step 2: For Each Section, Follow Instructions Below
Each section entry contains:
- **Title**: Section name
- **Source**: File path(s) in iteration directories
- **Action**: Copy, summarize, or reference
- **Output**: Expected SI section file

### Step 3: Compile to PDF
```bash
# Using pandoc
pandoc s1.md s2.md ... s22.md -o SI_v17.pdf --toc --number-sections

# Or using LaTeX
# Create main.tex with \input{s1} ... \input{s22}
# pdflatex main.tex
```

---

## Section Directory

### S1. Domain Operationalization Table (8 Domains)
- **Source**: `v4/bayesian_prediction_v4.py` (docstring), `v14_NATURE_MAIN.md` (Table 1)
- **Action**: Extract domain mapping table from manuscript Table 1; expand with full variable definitions
- **Output**: `s1_domain_operationalization.md`
- **Notes**: Include all 8 domains (7 original + Seshat) with Material/Fragmentation/Disengagement mappings

### S2. CBDB Data Processing Pipeline
- **Source**: `v4/cbdb_data_pipeline.py`, `v6/cbdb_psi_v6.py`
- **Action**: Copy docstrings and key functions; include data cleaning steps
- **Output**: `s2_data_processing.md`
- **Notes**: Document v2.5 API usage, A/B-tier record filtering, decade aggregation

### S3. CDLI/ORACC SFD Proxy Methodology
- **Source**: `v6.1/cdli_psi_analysis.py`, `v12_迭代研究/01_psi_improvement/v12a_meso_psi_engine.py`
- **Action**: Document SFD (Source Find Density) proxy formula; include 6/8 validation table
- **Output**: `s3_cdl_oracc_sfd.md`
- **Notes**: Critical section—reviewers will scrutinize Mesopotamian proxy validity

### S4. Roman LLM Evaluation Protocol
- **Source**: `v5/roman_llm_eval.py` (if exists), `v14_NATURE_MAIN.md` (Roman section)
- **Action**: Document LLM evaluator setup, inter-rater κ = 0.81 calibration, 14 historical phases
- **Output**: `s4_roman_llm_protocol.md`
- **Notes**: Include prompt templates and evaluation rubric

### S5. Financial Data Sources and Preprocessing
- **Source**: `v5/fetch_fred.py`, `v5/compute_macro_psi.py`, `v6/global_upsi_v6.py`
- **Action**: Document yfinance (20 assets), FRED (11 indicators), Tencent/Sina (4 Chinese indices)
- **Output**: `s5_financial_data.md`
- **Notes**: Include ticker lists, date ranges, missing data handling

### S6. Political Event Curation (Wikidata)
- **Source**: `v5/compute_political_psi.py`, `v6/data/psm_v6.json`
- **Action**: Document SPARQL queries, event selection criteria, 1,728 events → 33 major episodes
- **Output**: `s6_political_curation.md`
- **Notes**: Include example SPARQL query and event taxonomy

### S7. Newey-West HAC Standard Errors
- **Source**: `v6/data/hac_v6.json`, `v4/bayesian_v4.py`
- **Action**: Document Bartlett kernel, automatic bandwidth, HAC/OLS ratios
- **Output**: `s7_newey_west_hac.md`
- **Notes**: Report HAC/OLS = 1.4–2.2×, t_HAC > 4 for key findings

### S8. Propensity Score Matching Details
- **Source**: `v6/data/psm_v6.json`, `v4/bayesian_prediction_v4.py`
- **Action**: Document 1:1 nearest neighbor, caliper 0.2, 6 crisis vs 4 stable dynasties
- **Output**: `s8_psm_details.md`
- **Notes**: ATE = -1.05, p < 0.01; include balance table

### S9. Permutation Test Protocol
- **Source**: `v6/data/psm_v6.json`, `v4/bayesian_v4.py`
- **Action**: Document 10,000 random assignments, exact finite-sample inference
- **Output**: `s9_permutation_test.md`
- **Notes**: p = 0.0054; reference Bertrand, Duflo, Mullainathan (2004)

### S10. ROC Curves and Threshold Optimization
- **Source**: `v6/figures/Figure16_ROC_Curves.png`, `v6/figures/Figure17_Threshold_F1.png`, `v6/data/roc_v6.json`
- **Action**: Include ROC curves for 3 domains; baseline vs feature-engineered AUC table
- **Output**: `s10_roc_threshold.md`
- **Notes**: Baseline 0.48–0.59 → engineered 0.62–0.73; include feature importance table

### S11. Feature Engineering Pipeline
- **Source**: `v6/global_upsi_v6.py`, `v6/data/roc_v6.json`
- **Action**: Document 7 engineered features: σ, dPSI/dt, d²PSI/dt², skewness, dist_to_min, mean_dev, accel_sign
- **Output**: `s11_feature_engineering.md`
- **Notes**: Logistic regression L2 (C=1.0); scikit-learn 1.3

### S12. LSTM Architecture and Training
- **Source**: `v5/transformer_psi.py`, `v6/data/lstm_v6.json`
- **Action**: Document LSTM architecture (layers, units, dropout); training protocol
- **Output**: `s12_lstm_architecture.md`
- **Notes**: Accuracy 78.67%, F1 0.762; ensemble with logistic regression

### S13. Hurst H and Power-Spectrum β Estimation
- **Source**: `v6.1/h_beta_recheck.py`, `v6.1/data/h_beta_recheck_v61.json`
- **Action**: Document DFA (4th-order polynomial, scales 4–1024) and Whittle likelihood
- **Output**: `s13_hurst_beta.md`
- **Notes**: H = 1.5662, β = 4.00; fBm consistency check β = 2H+1 = 4.13 (3.2% deviation)

### S14. Cross-Civilization Terminal-Decline Analysis
- **Source**: `v4/figures/Figure8_Cross_Civilization.png`, `v9_迭代研究/03_upsi_v2`
- **Action**: Document Ur III vs Chinese dynasties correlation analysis
- **Output**: `s14_cross_civilization.md`
- **Notes**: r = 0.96 (Ur III–Southern Song), r = 0.77 (Ur III–Tang); explicitly label as exploratory

### S15. PageRank Network Centrality
- **Source**: `v5/psi_network.py`, `v4/figures/Figure7_Network_Density.png`
- **Action**: Document thresholded correlation graph (|r| > 0.3), damping 0.85, rolling 10-year windows
- **Output**: `s15_pagerank_centrality.md`
- **Notes**: DE-DAX 0.0698, FR-CAC 0.0659, UK-FTSE 0.0647, US-SP500 0.0627

### S16. Lead-Lag Cross-Correlation Details
- **Source**: `v4/figures/Figure14_Lead_Lag.png`, `v4/figures/Figure15_Recall_Lead.png`
- **Action**: Document τ ∈ [-30, +30] days, Newey-West HAC CIs
- **Output**: `s16_lead_lag.md`
- **Notes**: VIX lead τ = +17 (r = -0.235), gold lag τ = -1 (r = +0.346)

### S17. Blind Test Protocol and Results
- **Source**: `v6/data/blind_test_v6.json`, `v6.1/data/causal_4_layer_v61.json`
- **Action**: Document training 2020-2023, frozen model, test 2024-2025
- **Output**: `s17_blind_test.md`
- **Notes**: PSI mean +0.31 → +0.07; paired t-test p < 0.01; Snowball crash + arbitrage collapse

### S18. Seshat Variable Mapping and Validation
- **Source**: `v14_迭代研究/01_seshat_prototype/v14a_seshat_psi_engine.py`, `v15_迭代研究/01_seshat_expansion/v15a_seshat_expansion.py`
- **Action**: Document 5 NGAs, 337 centuries, variable mapping, 75% recall
- **Output**: `s18_seshat_validation.md`
- **Notes**: Material = population/territory; Fragmentation = hierarchy volatility; Disengagement = info systems/bureaucrats

### S19. SPI Computation and Mesopotamian Validation
- **Source**: `v13_迭代研究/02_spi_burst/v13b_spi_formula.py`, `v13_迭代研究/02_spi_burst/v13b_spi_meso_test.py`
- **Action**: Document SPI formula, adaptive τ, spike detection, 8/8 combined validation
- **Output**: `s19_spi_computation.md`
- **Notes**: τ_adaptive = max(1, ceil(N_period / (N_exact / 100))); CRITICAL if SPI > μ + 2.5σ

### S20. UPSI_v2 Quadrant Classifier
- **Source**: `v14_迭代研究/03_upsi_v2/v14c_upsi_v2.py`, `v14_迭代研究/03_upsi_v2/v14c_upsi_v2_plots/`
- **Action**: Document four-quadrant taxonomy, domain-specific confidence weighting
- **Output**: `s20_upsi_v2_classifier.md`
- **Notes**: w_SPI = 0.8 (finance), w_SPI = 0.1 (Old Babylonian); phase portraits

### S21. Dashboard Architecture and Deployment
- **Source**: `v14_迭代研究/04_dashboard_deploy/v14d_dashboard_repo/`, `v14_迭代研究/04_dashboard_deploy/v14d_deployment_report.md`
- **Action**: Document modular architecture, GitHub Actions workflow, API list
- **Output**: `s21_dashboard_architecture.md`
- **Notes**: DataFetcher / PSIEngine / SPIEngine / AlertSystem / Renderer; 8 free APIs

### S22. Code and Data Availability
- **Source**: `v15_迭代研究/04_submission/v15d_author_data_code.md`
- **Action**: Comprehensive code/data availability statement with repository structure
- **Output**: `s22_code_data_availability.md`
- **Notes**: GitHub repo, Docker container, reproduce.py, requirements.txt, README

---

## Assembly Tips

1. **Consistency**: Use the same heading style across all sections (## for section title, ### for subsections)
2. **Cross-references**: Use [S1], [S2] etc. when referring to other SI sections
3. **Figures**: Include full-resolution PNGs for each section; caption as "Supplementary Figure S1", "Supplementary Figure S2", etc.
4. **Tables**: Number as "Supplementary Table S1", "Supplementary Table S2", etc.
5. **Equations**: Number as (S1), (S2), etc.
6. **Page limit**: Nature SI has no strict page limit, but keep it concise. Target 45 pages.

---

## Quality Checklist

Before submitting SI:
- [ ] All 22 sections present
- [ ] All figures at 300 dpi
- [ ] All tables editable (not images)
- [ ] All equations numbered
- [ ] All cross-references resolved
- [ ] Spell-checked
- [ ] PDF compiled successfully
- [ ] File size < 50 MB

---

*SI master guide prepared: 2026-06-05*
