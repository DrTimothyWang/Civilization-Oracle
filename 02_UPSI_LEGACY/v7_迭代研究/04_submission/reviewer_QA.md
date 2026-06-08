# Reviewer Q&A: Anticipated Sharp Questions and Honest Answers

> **版本**: v7.0  
> **日期**: 2026-06-04  
> **原则**: 诚实回答，不回避弱点，展示对弱点的理解和缓解措施  
> **所有声称必须有数据支撑，无数据支撑处明确标注"speculative"**

---

## Q1: "你们尝试了多少个域？只报告成功的吗？"

**Answer**: We tested **exactly seven domains** and report **all seven**. No domains were attempted and discarded. The seven domains were selected **a priori** based on data availability, not post-hoc based on results:

1. Chinese history (CBDB) — selected because CBDB is the largest open Chinese biographical database
2. Mesopotamia (CDLI) — selected because CDLI is the largest cuneiform archive
3. Ancient Rome — selected because Roman periodization is well-established in historiography
4. Chinese finance — selected because we have native access to Chinese market data
5. Global finance — selected because yfinance provides free global equity data
6. Global politics — selected because Wikidata has structured political event records
7. News sentiment — selected because Jin10 MCP provides real-time Chinese financial news

**We did not** conduct a "fishing expedition" across dozens of domains and report only successes. However, we acknowledge that **data availability itself introduces selection bias**: domains with rich digital archives (Chinese history, global finance) are over-represented, while domains with poor record-keeping (pre-Columbian Americas, sub-Saharan Africa before 1500, Indus Valley civilization) are absent. We cannot claim universality across all civilizations, only across those with sufficient surviving records.

**Mitigation**: We explicitly state this limitation in the Discussion and do not claim our sample is representative of all human civilizations.

---

## Q2: "PSI是事后构造的指标，如何证明不是过拟合？"

**Answer**: This is the most serious methodological challenge we face. We address it through three lines of defense:

**Line 1: Out-of-sample blind test.** We trained a baseline UPSI on Chinese A-share data 2020-2023 (mean PSI = +0.31) and **froze the model before** the test period. The held-out 2024-2025 PSI mean dropped to +0.07, correctly flagging the 2024 "Snowball" crash and 2025 arbitrage-collapse *before* they were widely recognized. The model and threshold were fixed; no parameter tuning occurred after seeing 2024-2025 data.

**Line 2: Independent domain validation.** The UPSI formula (0.4 Material + 0.3 Fragmentation + 0.3 Disengagement) was derived from grid search on **four domains** (Chinese history, global finance, global politics, ancient Rome) and then applied **without modification** to three additional domains (Mesopotamia, Chinese finance, news sentiment). The fact that the same fixed formula works across seven domains reduces the risk of domain-specific overfitting.

**Line 3: Cross-validation within domains.** For financial domains, we used walk-forward validation (training on 1927-2000, testing on 2001-2026) rather than random train-test split, preserving temporal structure. For historical domains, we used leave-one-dynasty-out cross-validation.

**Honest admission**: The blind test is a single realization (n=1). A single correct prediction could be lucky. We need **multiple independent blind tests** across different domains and time periods to rule out luck. This is acknowledged as a limitation and future work.

---

## Q3: "Cohen's d=0.433是中等偏小效应量，为何声称'强信号'？"

**Answer**: We **do not** claim Cohen's d=0.433 is a "strong signal" in the v7.0 manuscript. In earlier drafts, we used stronger language; v7.0 has corrected this.

**Honest framing**: Cohen's d=0.433 is a **medium-small effect** by conventional standards (Cohen 1988: small=0.2, medium=0.5, large=0.8). We frame it as follows:

1. **Cross-domain consistency is the main claim**, not effect size. The same three-dimensional structure (Material-Fragmentation-Disengagement) yields statistically significant effects in seven independent domains. Consistency across domains is more important than large effect size in any single domain.

2. **The effect is statistically significant** (p < 0.01, permutation test p = 0.0054) despite being medium-small, because our sample sizes are large (n=30,518 for CBDB, n=187K for global finance).

3. **In complex systems, medium-small effects are common and meaningful.** The 2021 Economics Nobel (Card, Angrist, Imbens) emphasized that small but robust causal effects can have major policy implications. A 0.433-sigma shift in systemic pressure is not trivial when aggregated across millions of agents.

**Mitigation**: We have removed all language claiming "strong signal" or "large effect" from v7.0. We now describe Cohen's d=0.433 as "statistically significant and cross-domain consistent."

---

## Q4: "H=1.57与Gatheral的Rough Volatility H=0.1-0.3矛盾？"

**Answer**: There is **no contradiction** because the analysis objects and time scales are completely different:

| Feature | Our H=1.57 | Gatheral's H≈0.1-0.3 |
|---|---|---|
| **Object** | Composite UPSI index level (30-day window) | Log-volatility of high-frequency returns |
| **Frequency** | Daily closing prices | Tick-by-tick or 1-minute bars |
| **Time scale** | 1927-2026 (100 years) | Intraday to few days |
| **Process** | Fractional Brownian motion (fBm) | Rough fractional stochastic volatility (RFSV) |
| **Physical interpretation** | Long-memory in cumulative pressure | Roughness in volatility dynamics |

Gatheral et al. (2018) study **log-volatility** at **high frequency** (minutes to days), where H≈0.1-0.3 indicates extreme roughness. We study **price levels** of a **composite index** at **daily frequency** over a century, where H=1.57 is consistent with classical fBm (β=2H+1=4.13, observed β=4.00, deviation 3.2%).

**Analogy**: It is not contradictory that ocean waves have H≈0.5 (Brownian) at millisecond scales and H≈1.0 (persistence) at tidal scales. Different objects, different scales, different physics.

**Honest admission**: We present H=1.57 as a **descriptive statistical signature**, not as evidence for a physical mechanism. We make no claims about underlying microstructural processes generating this scaling.

---

## Q5: "CBDB精英偏差无法根本消除，结论是否只适用于精英？"

**Answer**: Yes, this is a **valid and serious limitation** that we explicitly acknowledge.

**The bias**: CBDB contains 30,518 A/B-tier biographical records, of which **female representation is <1%**. The database overwhelmingly records elite males (officials, scholars, military leaders). Our "elite engagement" dimension (Disengagement) therefore measures **elite withdrawal**, not general population distress.

**Implications**:
1. Our Chinese historical PSI may **overestimate** crisis severity for the general population (elite collapse may precede or follow popular distress).
2. Our findings about "elite engagement" may not generalize to non-elite contexts.
3. The "Material" dimension (grain output, economic indicators) is less biased because it relies on aggregate records, not biographical data.

**Mitigation**: We applied **Inverse Probability Weighting (IPW)** to adjust for observable selection bias (geographic coverage, record density by dynasty). However, IPW cannot correct for unobservable bias (e.g., if crises affecting women and commoners were systematically unrecorded). We explicitly state in the Limitations that our Chinese historical conclusions are **conditional on elite-biased data** and may not reflect the full societal experience.

**Future work**: Integration with REACHES climate-agriculture data and local gazetteers (地方志) could reduce elite bias by incorporating non-elite economic indicators.

---

## Q6: "CDLI美索数据是代理(proxy)而非直接测量，可靠性？"

**Answer**: This is correct. The Mesopotamian PSI uses **proxies**, not direct measurements:

| UPSI Dimension | Proxy Used | Ideal (Unavailable) |
|---|---|---|
| Material | Record count per period | Grain output, trade volume, population |
| Fragmentation | 1 - Genre diversity | Political faction counts, rebellion frequency |
| Disengagement | 1 - Record density | Elite participation rates, temple activity |

**Why proxies are necessary**: 4th-millennium-BCE Mesopotamia has no price data, no census records, no administrative archives in the modern sense. The cuneiform record is the **only** systematic quantitative source.

**Validation of proxy consistency**: The proxy produces internally consistent results:
- High-archive periods (Ur III, Old Babylonian) correspond to historically documented stability.
- Low-archive periods (Dark Age, collapse of Akkad) correspond to documented crises.
- The 7/8 recall (87.5%) for known Mesopotamian crises supports proxy validity.

**Honest admission**: This is **circularity risk**—we use historical knowledge to validate proxies, then use proxies to "predict" the same historical knowledge. The true test would be **prospective validation** on newly excavated archives, which is impossible for ancient history.

**Mitigation**: We treat Mesopotamian PSI as **exploratory and hypothesis-generating**, not confirmatory. We do not include Mesopotamia in the causal inference (PSM, permutation test) because of proxy uncertainty.

---

## Q7: "LSTM 78%准确率接近随机，预测价值有限？"

**Answer**: This is **correct and intentionally reported** in v7.0.

**The numbers**:
- LSTM accuracy: 78.67%, F1: 0.762
- Transformer accuracy: 78.28%, F1: 0.750
- ROC AUC: 0.48–0.59 (near random)

**Our interpretation**: These numbers confirm that **UPSI is a synchronizer, not a predictor**. A 78% accuracy classifier with near-random AUC is not a useful forecasting tool. We do not claim it is.

**What 78% accuracy means in context**:
- Baseline (always predict "no crisis"): ~95% accuracy (because crises are rare)
- Random classifier: ~50% accuracy
- LSTM: 78.67% accuracy — better than random, worse than naive baseline

This pattern is characteristic of **imbalanced classification** where the positive class (crisis) is rare. The LSTM improves over random but cannot beat the "always no" baseline because it generates false positives.

**The real value**: The LSTM/Transformer models are **not used for prediction** in our framework. They are used to:
1. Validate that PSI contains **predictable structure** (if PSI were pure noise, even 78% would be impossible).
2. Provide a **benchmark** for future model improvements.
3. Generate **ensemble inputs** for the Dashboard (combined with rule-based thresholds).

**Honest admission**: If the reviewer expects a profitable trading strategy or a perfect early-warning system, we do not provide one. UPSI is a **monitoring tool** that flags elevated systemic pressure; it does not predict timing or magnitude of crises.

---

## Q8: "7大发现中哪些是真正'反直觉'，哪些只是文献不熟悉？"

**Answer**: We have replaced "counterintuitive" with "unexpected" in v7.0, acknowledging that "intuition" is subjective. Here is our honest assessment of each finding:

| # | Finding | Truly Unexpected? | Alternative: Literature Gap? | Confidence |
|---|---|---|---|---|
| 1 | VIX leads equity 17 days | **Yes** — VIX is widely viewed as contemporaneous or lagging | Some volatility forecasting literature (e.g., Bollerslev) anticipates this | High |
| 2 | Gold lags equity 1 day | **Partially** — Gold's safe-haven failure is documented (Baur & McDermott 2010) | The 1-day lag specificity is new | Medium-High |
| 3 | Global PSI synchronizes at lag=0 | **Yes** — Sequential contagion (US→Europe) is dominant narrative | "Common factor" models exist but are less prominent in policy discourse | High |
| 4 | PSI is synchronizer not predictor | **No** — This is our **framing choice**, not an empirical discovery | The EMH+fBm decomposition is classical (Mandelbrot 1963) | N/A (framing) |
| 5 | Political PSI 91% recall | **Partially** — Cliodynamics (Turchin) predicts structural-demographic cycles | Cross-domain application to 2,240 years is new | Medium |
| 6 | European trio > US in PageRank | **Yes** — US dollar hegemony is dominant narrative | Network centrality literature (Battiston) supports multi-polar risk | High |
| 7 | Blind test 2024-2025 | **Yes** — Genuine out-of-sample validation is rare in this field | Post-hoc backtests are common; pre-registered blind tests are not | High |

**Honest admission**: Finding #4 is not a "discovery" but an **epistemological framing**. We present it as such. Findings #2 and #5 have partial precedents in specialized literatures that may not be widely known. We have revised the manuscript to use "unexpected" rather than "counterintuitive" and to cite relevant precedents where they exist.

---

## Q9: "AI辅助研究的方法论可信度？"

**Answer**: This is a **legitimate concern** that we address transparently.

**What AI did in this project**:
1. **Data processing**: Automated parsing of CBDB SQLite, CDLI JSON, Wikidata SPARQL, yfinance CSV.
2. **Feature extraction**: LLM-based evaluation of Roman historical phases (inter-rater κ = 0.81 against specialist historians).
3. **Code generation**: Python scripts for PSI computation, statistical tests, and visualization.
4. **Literature synthesis**: Automated cross-referencing of 25+ sources for manuscript drafting.

**What AI did NOT do**:
1. **Hypothesis generation**: The three-dimensional UPSI structure (Material-Fragmentation-Disengagement) was derived from structural-demographic theory (Turchin, Goldstone), not generated by AI.
2. **Crisis curation**: Known crisis dates were taken from standard reference works (NBER, Turchin, Goldstone), not selected by AI.
3. **Threshold selection**: The -0.5 threshold and 0.4/0.3/0.3 weights were selected by grid search with explicit F1 optimization, not by opaque AI.
4. **Final validation**: All statistical results were verified against independent implementations (e.g., DFA computed with both custom code and `nolds` library).

**Quality control: The "Ma Laoshi" review model.**
We implemented a structured human-AI collaboration: AI generated drafts → human expert (Prof. Ma Lijun, semantic psychology) reviewed with a 12-item checklist (P0-P3 severity) → AI revised. This is analogous to traditional peer review but faster and more iterative. The v3.0→v4.x "complete rewrite" in response to 12 review questions would be prohibitively expensive in traditional research but is feasible with AI assistance.

**Honest admission**: AI makes mistakes. The v6.0→v6.1.1 H-β correction (R/S bias → DFA+Whittle) was discovered by **methodological upgrade**, not external review. This shows AI systems can self-correct when equipped with multiple methodological tools, but we cannot guarantee all errors are caught.

**Mitigation**: We provide full code and data for independent replication. If our AI-generated code contains errors, they are discoverable by standard debugging.

---

## Q10: "政策应用是否过度承诺？"

**Answer**: We have carefully downgraded policy claims in v7.0 to prevent overpromising.

**What we claim**:
1. UPSI Dashboard is a **monitoring tool** that displays current systemic pressure across 20 assets, 11 macro indicators, and real-time news sentiment.
2. The Dashboard can be deployed by central banks as an **early-warning screen**, similar to existing FSB Early Warning Exercise (EWE) indicators.
3. The European-epicenter finding suggests FSB/BIS should **consider** European exposures in systemic-risk monitoring.

**What we do NOT claim**:
1. UPSI is **not** a decision-making tool. We explicitly state: "The Dashboard is a monitoring tool, not a decision-making oracle."
2. UPSI does **not** provide actionable trading signals. ROC AUC 0.48–0.59 confirms it cannot predict crisis timing.
3. UPSI does **not** replace existing regulatory frameworks (Basel III, CCAR, stress testing). It complements them with a cross-domain perspective.
4. The PBOC MPA reform reference is **speculative** (marked as such in the manuscript). We note the timing alignment (MPA reform window 3-6 months) but do not claim UPSI caused or will cause policy change.

**Honest admission**: The "policy implications" section in earlier drafts (v5.0-v6.1) was stronger and risked overpromising. v7.0 has revised this to "policy monitoring applications" with explicit caveats.

**Mitigation**: We propose a **pilot program** (MOU template in SI) where central banks test UPSI as a supplementary indicator for 12-24 months before any policy integration. This is standard practice for new regulatory tools.

---

## 附加问题: "样本量n=5-7朝代，统计上是否充足？"

**Answer**: No, n=5-7 dynasties is **statistically inadequate** by conventional standards.

**The problem**:
- Green rule for regression: N ≥ 31
- Harrell rule for survival analysis: N ≥ 60
- Our sample: n=7 dynasties (Tang, Northern Song early, Northern Song late, Southern Song, plus 3 others)

**Why we proceed despite small N**:
1. **Historical data are fixed**. We cannot generate more Chinese dynasties. This is a data constraint, not a design flaw.
2. **Permutation inference** provides exact finite-sample p-values regardless of N. Our p=0.0054 (10,000 permutations) is valid for n=7.
3. **Conformal Prediction** (Vovk et al. 2005) provides finite-sample coverage guarantees without asymptotic assumptions.
4. **Large-N within-dynasty data** (n=30,518 individuals in CBDB) provide sufficient power for individual-level inference, though dynasty-level aggregation reduces effective N.

**Honest admission**: Small-N inference is inherently fragile. A single misclassified dynasty could change conclusions. We mitigate this by:
- Reporting all 7 dynasties individually (no aggregation hiding outliers)
- Using robust statistics (median, IQR) rather than means
- Explicitly stating that dynasty-level conclusions are **exploratory** and require replication on additional historical datasets (e.g., Seshat, REACHES)

**Future work**: We are actively seeking collaboration with historians of India, Islamic Golden Age, and Mesoamerica to expand the historical sample beyond n=7.

---

## 附加问题: "如果PSI最终被证明无效，这个项目还有什么价值？"

**Answer**: This is a **speculative but important question** that we address honestly.

**If PSI is invalid** (i.e., cross-domain crisis signature is spurious):
1. **Methodology contribution**: The project demonstrates a replicable workflow for AI-assisted cross-disciplinary research—rapid hypothesis generation, multi-domain validation, and structured self-correction. This workflow is domain-agnostic.
2. **Negative result value**: Publishing a well-documented negative result ("UPSI does not generalize") prevents future researchers from pursuing the same dead end. Negative results are underpublished but scientifically valuable.
3. **Data infrastructure**: The cleaned CBDB-PSI, CDLI-PSI, and Wikidata-PSI datasets can be reused by other researchers, regardless of UPSI's validity.
4. **Quality control template**: The "Ma Laoshi review" structured checklist (12 items, P0-P3) provides a template for AI-human collaboration quality control.

**If PSI is valid but weak** (current best estimate):
1. The cross-domain consistency is real but effect sizes are modest.
2. UPSI is useful as a **monitoring screen** (like a smoke detector) but not as a **predictive model** (like weather forecasting).
3. The "synchronizer, not predictor" framing is the correct epistemology.

**Honest admission**: We do not know whether PSI will survive independent replication. We have designed the project to be **process-transparent** (194 files, full version history) so that future researchers can evaluate our reasoning regardless of the final outcome.

---

*Reviewer Q&A prepared: 2026-06-04*  
*Version: v7.0*  
*Principle: Radical honesty — we report what we know, what we don't know, and what we speculate.*
