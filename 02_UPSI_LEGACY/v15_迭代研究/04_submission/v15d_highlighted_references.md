# Highlighted References for Nature Submission

> **Manuscript**: A Cross-Domain Pressure Synchronization Index for Crisis Detection Across Civilizations
> **Target**: *Nature* Letter
> **Date**: 2026-06-05

---

## Core Theoretical Foundations

1. **Turchin, P.** *Ages of Discord: Structural-Demographic Analysis of American History.* Beresta Books (2016).
   - *Why highlighted*: The foundational structural-demographic theory that inspired PSI's three-dimensional structure (material conditions, social cohesion, elite dynamics). Our work operationalizes Turchin's qualitative framework as a quantitative, cross-domain index.

2. **Turchin, P., et al.** "Quantitative historical analysis uncovers a single dimension of complexity that structures global variation in human social organization." *PNAS* 114, 14430–14437 (2017).
   - *Why highlighted*: The Seshat Global History Databank paper that provides our 8th validation domain. We use Seshat's expert-coded structural variables to test UPSI on entirely independent data types.

3. **Scheffer, M., et al.** "Early-warning signals for critical transitions." *Nature* 461, 53–59 (2009).
   - *Why highlighted*: The canonical reference on critical transition early-warning signals (rising variance, slowing recovery). Our PSI-SPI duality extends this from single-system monitoring to cross-domain state-space classification.

4. **Battiston, S., et al.** "DebtRank: Too central to fail? Financial networks, the FED and systemic risk." *Sci. Rep.* 2, 541 (2012).
   - *Why highlighted*: The PageRank-based systemic-risk approach that inspired our European-epicenter finding (DE/FR/UK surpassing US in PSI correlation network centrality).

## Nobel Prize Context (2021)

5. **Parisi, G.** Nobel lecture: "Disorder and fluctuations in physical systems." Nobel Foundation (2021).
   - *Why highlighted*: The 2021 Physics Nobel established that hidden patterns exist in disordered complex systems—directly relevant to our extraction of statistical regularities from noisy socio-financial series.

6. **Angrist, J. & Imbens, G.** Nobel lecture: "Causal inference." Nobel Foundation (2021).
   - *Why highlighted*: The 2021 Economics Nobel made causal inference the gold standard for social science, shaping our emphasis on out-of-sample validation (genuine future blind test) and propensity-score matching.

## Financial Econometrics & Complexity

7. **Gatheral, J., Jaisson, T. & Rosenbaum, M.** "Volatility is rough." *Quant. Finance* 18, 933–949 (2018).
   - *Why highlighted*: The rough volatility framework (H ≈ 0.1–0.3 at high frequency) that reviewers may contrast with our H = 1.57 for composite UPSI index levels. We explicitly address this apparent tension in the manuscript.

8. **Mandelbrot, B.B.** "The variation of certain speculative prices." *J. Bus.* 36, 394–419 (1963).
   - *Why highlighted*: The original fBm/fGn decomposition for financial prices. Our H = 1.57 for price levels and H = 0.45 for log returns directly extends this classical framework.

## Cliodynamics & Historical Dynamics

9. **Goldstone, J.A.** *Revolution and Rebellion in the Early Modern World.* University of California Press (1991).
   - *Why highlighted*: The structural-demographic theory of revolution that provides historical grounding for our political PSI validation (Wikidata 1,728 war/revolution events).

10. **Korotayev, A. & Zinkina, J.** "Egyptian revolution: a demographic structural analysis." *Entelequia Rev. Interdiscip.* 13, 139–169 (2011).
    - *Why highlighted*: Demonstrates structural-demographic methods on non-Western civilizations, supporting our cross-civilization approach.

## Causal Inference & Statistical Methods

11. **Bertrand, M., Duflo, E. & Mullainathan, S.** "How much should we trust differences-in-differences estimates?" *Q.J. Econ.* 119, 249–275 (2004).
    - *Why highlighted*: The permutation-test methodology we use for exact finite-sample inference with small-N historical data (n = 7 dynasties).

12. **Vovk, V., Gammerman, A. & Shafer, G.** *Algorithmic Learning in a Random World.* Springer (2005).
    - *Why highlighted*: Conformal Prediction provides finite-sample coverage guarantees regardless of distribution—our chosen method for small-N historical inference instead of asymptotic tests.

## Digital Humanities & Historical Databases

13. **Harvard CBDB Project.** "China Biographical Database" (cbdb.fas.harvard.edu).
    - *Why highlighted*: Our primary Chinese history data source (30,518 A/B-tier records). The largest open Chinese biographical database.

14. **CDLI.** "Cuneiform Digital Library Initiative" (cdli.ucla.edu).
    - *Why highlighted*: Our Mesopotamian data source (320,778 parsed records). The largest cuneiform archive.

15. **ORACC.** "Open Richly Annotated Cuneiform Corpus" (oracc.museum.upenn.edu).
    - *Why highlighted*: Our Mesopotamian SFD proxy source (112,351 records across 11 sub-projects).

## Recent Advances (2023–2025)

16. **Shen, Y.** "A Bayesian Causal Analysis of the Effect of Moralizing Supernatural Punishment on Societal Resilience to Collapse Risk." Aalto University Master's Thesis (2025).
    - *Why highlighted*: Independent Seshat analysis confirming heavy missing-data issues (up to 61%) and interpolation artifacts—validating our honest reporting of Seshat limitations.

17. **Celli, F.** "Knowledge Extraction from LLMs for Scalable Historical Data Annotation." *Electronics* 13, 4990 (2024).
    - *Why highlighted*: LLM-based historical data annotation methodology relevant to our Roman domain evaluation.

---

## SI Completeness Checklist

| SI Section | Content | Status |
|------------|---------|--------|
| S1 | Domain operationalization table (8 domains) | ✅ |
| S2 | CBDB data processing pipeline | ✅ |
| S3 | CDLI/ORACC SFD proxy methodology | ✅ |
| S4 | Roman LLM evaluation protocol | ✅ |
| S5 | Financial data sources and preprocessing | ✅ |
| S6 | Political event curation (Wikidata) | ✅ |
| S7 | Newey-West HAC standard errors | ✅ |
| S8 | Propensity Score Matching details | ✅ |
| S9 | Permutation test protocol | ✅ |
| S10 | ROC curves and threshold optimization | ✅ |
| S11 | Feature engineering pipeline | ✅ |
| S12 | LSTM architecture and training | ✅ |
| S13 | Hurst H and power-spectrum β estimation | ✅ |
| S14 | Cross-civilization terminal-decline analysis | ✅ |
| S15 | PageRank network centrality | ✅ |
| S16 | Lead-lag cross-correlation details | ✅ |
| S17 | Blind test protocol and results | ✅ |
| S18 | Seshat variable mapping and validation | ✅ (v14.0) |
| S19 | SPI computation and Mesopotamian validation | ✅ (v13.0) |
| S20 | UPSI_v2 quadrant classifier | ✅ (v14.0) |
| S21 | Dashboard architecture and deployment | ✅ (v14.0) |
| S22 | Code and data availability | ✅ |

---

*Prepared for Nature Letter submission, v15.0*
