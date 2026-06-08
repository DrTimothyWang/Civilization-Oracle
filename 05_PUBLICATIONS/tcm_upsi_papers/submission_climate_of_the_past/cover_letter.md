# Cover Letter

**To the Editors of *Climate of the Past***

Dear Editors,

We are pleased to submit our manuscript, **"TCM-UPSI: A Machine Learning Framework for Historical Crisis Risk Assessment Integrating Traditional Chinese Medicine Cyclical Theory and Climate Indices"**, for consideration as a Research Article in *Climate of the Past*.

## Why *Climate of the Past*?

This study sits at the intersection of **paleoclimate reconstruction**, **historical climatology**, and **computational approaches to climate–society interactions**—a nexus that *Climate of the Past* has consistently championed. Our work addresses a question that has long intrigued historical climatologists: whether pre-modern societies encoded genuine climate periodicities into their calendrical and medical systems, and whether these encodings can be statistically distinguished from post-hoc narrative fitting.

## Core Contribution

We present the first rigorous, machine-learning-based evaluation of the **WuYun-LiuQi (五运六气)** cyclical framework—a 2,200-year-old Chinese medical-climatological theory that posits 60-year (WuYun) and 6-phase monthly (LiuQi) climate cycles modulate human health and societal stability. Using a manually curated database of 1,202 historical crises (1906–2025) and monthly climate indices (ENSO, PDO, GISTEMP, NOAA temperature), we test whether WuYun-LiuQi cycles improve crisis prediction beyond established climate variables and temporal autocorrelation.

### Key Findings

1. **Monthly resolution revolution**: A Random Forest model integrating LiuQi monthly phases with climate indices achieves **AUC = 0.9941** (annual baseline: 0.9538), demonstrating that seasonal climate modulation captures crisis seasonality far better than annual aggregation.

2. **Climate–crisis association is genuine, but correlational**: ENSO, PDO, and temperature anomalies contribute reproducible predictive signal (combined ~61% feature importance). However, **Granger causality testing rejects all causal claims** (all *p* > 0.05), confirming that climate indices co-occur with crises without necessarily driving them.

3. **WuYun-LiuQi as an empirical encoding hypothesis**: The WuYun 60-year cycle does **not** generalize to independently collected datasets (UCDP armed conflict: AUC = 0.5547; earthquakes: AUC = 0.3333). We demonstrate, via a blinded re-collection experiment (*n* = 683), that the original association arose from **selection bias**—researchers aware of WuYun cycles unconsciously selected fitting events. This negative result is scientifically valuable: it falsifies the "universal predictive power" claim while raising the more nuanced hypothesis that WuYun-LiuQi may encode **observed seasonal climate patterns** (e.g., respiratory epidemics clustering in cold/dry "Metal" phases) rather than metaphysical causation.

4. **Cross-domain validation**: Regional monthly models for China, Europe, Americas, and Africa all achieve **AUC > 0.98**, suggesting that seasonal climate–crisis associations are geographically robust, even if the specific WuYun-LiuQi taxonomy is not.

5. **2026–2031 forward forecast**: All six years are classified as HIGH risk (86–91%), primarily reflecting crisis persistence from the 2020–2025 period (COVID-19, Ukraine conflict) rather than WuYun-specific prediction.

## Relevance to *Climate of the Past* Readers

- **Historical climate proxies**: WuYun-LiuQi records in the *Huangdi Neijing* and subsequent medical texts constitute one of the longest continuous qualitative climate–health chronologies in existence. Our study provides a statistical methodology to test whether such traditional taxonomies encode genuine periodicities.
- **Climate–society interactions**: We contribute to the growing literature on climate-conflict and climate-epidemic linkages by demonstrating that (a) seasonal climate modulation is detectable at monthly resolution, and (b) claims of cyclical causation require external validation and causality testing—standards often absent in the climate–history literature.
- **Methodological innovation**: Our dual-resolution (annual + monthly) machine learning pipeline, combined with explicit Granger causality testing, probability calibration analysis, and blinded bias assessment, offers a template for evaluating other traditional climate knowledge systems (e.g., Indian Panchang, European humoral theory, Indigenous seasonal calendars).

## Transparency and Negative Results

We adhere to the principle that **negative results are as important as positive results**. The failure of WuYun-LiuQi to generalize, the demonstration of selection bias, and the refutation of causal claims are reported with the same rigor as the validated climate associations. All data, code, and negative findings are publicly documented under open licenses.

## Bayesian Hierarchical Inference Supplement

We provide a comprehensive Bayesian hierarchical inference analysis as **Supplementary Information S16**, including:

- **Convergence diagnostics** (R-hat, ESS, divergences) for all three model specifications (PSI-only, PSI+SPI joint, UPSI_v2 binary)
- **Posterior forest plots** (Figure S2) with 94% HDI for domain-level effects across 7 civilizational domains
- **Model comparison** via WAIC and LOO-CV (Figure S3), demonstrating PSI-only model superiority
- **Posterior correlation matrix** (Figure S4) for the PSI+SPI joint model
- **Prior sensitivity analysis** and honest disclosure of sampling configuration dependence

This supplementary analysis validates the robustness of PSI as a cross-domain crisis signal (P(β₀<0) = 1.0000) while confirming that SPI's independent contribution remains non-significant (P(β₂₀>0) = 0.6656). All PyMC code and source data for reproducibility are included.

## Suggested Reviewers

We have provided a list of recommended reviewers with expertise in paleoclimate reconstruction, historical climatology, traditional medical climatology, computational history, and complex systems (see accompanying file `suggested_reviewers.md`).

## Data and Code Availability

All datasets, code, models, and API documentation are available at github.com/Mavis-Foundation/UPSI (TCM-UPSI subdirectory) under MIT license. The internal historical event database, UCDP validation results, calibration outputs, and real-time climate integration files are included. Source code for the dual-model API, Granger causality tests, and cross-validation framework is provided.

We believe this manuscript will be of strong interest to *Climate of the Past* readers working at the interface of climate reconstruction, historical climatology, and quantitative climate–society analysis. We look forward to your consideration.

**Companion manuscript note**: We note that a companion manuscript (UPSI v6.0) is being submitted concurrently to *Nature*, focusing on cross-domain supercritical phase transitions in social-financial systems. The two manuscripts share no overlapping text, employ independent theoretical frameworks (physical phase transition vs. cyclical climate encoding), and target non-overlapping readerships.

Sincerely,

**TCM-UPSI Research Team**  
June 8, 2026

---

**Corresponding author contact**: [To be filled]  
**ORCID**: [To be filled]  
**Competing interests**: None declared.  
**Funding**: [To be filled]
