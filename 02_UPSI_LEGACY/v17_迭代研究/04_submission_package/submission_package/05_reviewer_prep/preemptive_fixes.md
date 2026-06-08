# Preemptive Fixes — Changes Already Made in Response to Anticipated Critiques

**Version**: v17.0  
**Date**: 2026-06-05  
**Purpose**: Document changes made preemptively to address likely reviewer concerns

---

## Fix 1: Honest Reporting of Mesopotamian Validation (v10.0)

**Anticipated critique**: "You reported 87.5% Mesopotamian recall in v9.0, but v10.0 drops it to 75%. Are you cherry-picking?"

**Preemptive fix**:
- Corrected the v9.0 error: the 87.5% figure was incorrectly carried forward from v7 CDLI-only catalog counts
- Recomputed with full ORACC multi-period validation: **6/8 (75%)** across 7 periods
- Added dedicated paragraph in Results ¶2.2 explaining the two failures (Umma decline, Hammurabi fragmentation) as **instructive proxy limitations**
- Added limitation bullet in Discussion explicitly stating the trade-off: "broader coverage, not higher accuracy"

**Status**: ✅ Fixed in v10.0, retained in v14.0/v17.0

---

## Fix 2: Downgrading "Strong Signal" Language (v7.0–v10.0)

**Anticipated critique**: "Cohen's d = 0.433 is only a medium-small effect. Why do you claim 'strong signal'?"

**Preemptive fix**:
- Removed all language claiming "strong signal" or "large effect" from v7.0/v9.0/v10.0
- Replaced with: "statistically significant and cross-domain consistent"
- Added explicit framing: "In complex systems, medium-small effects are common and meaningful"
- Cited 2021 Economics Nobel (Card, Angrist, Imbens) as precedent for small-but-robust effects

**Status**: ✅ Fixed in v7.0, retained in v14.0/v17.0

---

## Fix 3: ROC AUC Honest Reporting (v9.0–v10.0)

**Anticipated critique**: "Your baseline ROC AUC is 0.48–0.59 (near random). How can you claim UPSI is useful?"

**Preemptive fix**:
- Added **two-tier ROC AUC reporting**:
  - Baseline (PSI level only): 0.48–0.59 → "near-random; confirms PSI is a poor *predictor*"
  - Feature-engineered (PSI + σ + derivatives): 0.62–0.73 → "moderate discrimination; consistent with a *monitoring screen*"
- Added medical-screening analogy: "AUC 0.6–0.7 is considered 'fair' — sufficient for screening, not for diagnosis"
- Explicitly stated: "We do not claim trading viability"
- Added caveat: "All AUC values are in-sample; walk-forward out-of-sample validation is future work"

**Status**: ✅ Fixed in v9.0/v10.0, retained in v14.0/v17.0

---

## Fix 4: H-β Estimator Upgrade (v6.0 → v6.1.1)

**Anticipated critique**: "Your H = 0.958 from R/S estimator is known to have positive bias for long-memory processes."

**Preemptive fix**:
- Replaced R/S estimator (Hurst 1951) with **DFA + Whittle** estimators
- New estimates: H = 1.5662 (DFA), β = 4.00 (Whittle)
- Added fBm consistency check: β = 2H + 1 predicts 4.13, observed 4.00 (3.2% deviation)
- Added fGn rejection: β = 2H − 1 predicts 2.13, does not match
- Documented in SI S13 with full methodological details

**Status**: ✅ Fixed in v6.1.1, retained in v14.0/v17.0

---

## Fix 5: "Counterintuitive" → "Unexpected" (v7.0)

**Anticipated critique**: "'Counterintuitive' is subjective. What is counterintuitive to you may be obvious to a specialist."

**Preemptive fix**:
- Replaced all instances of "counterintuitive" with "unexpected" throughout manuscript
- Added honest assessment table (Q8 in anticipated_qa.md) rating each finding as "truly unexpected", "partially unexpected", or "framing choice"
- Cited relevant precedents where they exist (e.g., Baur & McDermott 2010 for gold safe-haven failure)
- Explicitly labeled Finding #4 ("synchronizer, not predictor") as an **epistemological framing**, not an empirical discovery

**Status**: ✅ Fixed in v7.0, retained in v14.0/v17.0

---

## Fix 6: Policy Claims Downgrade (v7.0–v10.0)

**Anticipated critique**: "Your policy implications section overpromises. You claim central banks should adopt UPSI."

**Preemptive fix**:
- Replaced "policy implications" with "policy monitoring applications"
- Added explicit caveats:
  - "The Dashboard is a monitoring tool, not a decision-making oracle"
  - "UPSI does not provide actionable trading signals"
  - "UPSI does not replace existing regulatory frameworks (Basel III, CCAR, stress testing)"
- Marked PBOC MPA reform reference as **speculative**
- Proposed **pilot program** (MOU template in SI) where central banks test UPSI as supplementary indicator for 12–24 months

**Status**: ✅ Fixed in v7.0/v10.0, retained in v14.0/v17.0

---

## Fix 7: Cross-Civilization Convergence Framing (v9.0)

**Anticipated critique**: "r = 0.96 between Ur III and Southern Song is striking but probably spurious given tiny sample size."

**Preemptive fix**:
- Explicitly labeled as **"exploratory"** in title of ¶2.5
- Explicitly labeled as **"small-sample"** and **"hypothesis generation, not validation"**
- Compared to critical phenomena in physics only as a **conceptual analogy**, not empirical physics
- Added full methodological caveats in SI S14
- Added honest admission: "The r = 0.96 correlation is probably the most striking number in the paper and the least statistically defensible"
- Listed requirements for statistical validation (3–5 Mesopotamian periods with annual PSI, unified computation, pre-registered hypothesis)

**Status**: ✅ Fixed in v9.0, retained in v14.0/v17.0

---

## Fix 8: SPI Post-Hoc Defense (v12.0)

**Anticipated critique**: "SPI seems post-hoc — how do we know it wasn't designed to fit those 2 failures?"

**Preemptive fix**:
- Documented SPI as **mathematically distinct** from PSI (integration vs. differentiation, low-pass vs. high-pass)
- Added comparison table: PSI = temperature, SPI = dT/dt
- Motivated SPI by **theoretical boundary analysis** (v12.0): PSI's 50–100 year windows inherently suppress intra-window variance
- Cited standard signal-processing principles (change-point detection, control theory)
- Added honest admission: SPI weights (0.35/0.25/0.25/0.15) are theoretically motivated but **not cross-validated** on independent data

**Status**: ✅ Fixed in v12.0, retained in v14.0/v17.0

---

## Fix 9: Bayesian Hierarchical Model (v12.0)

**Anticipated critique**: "Your cross-domain results could be driven by a single outlier domain."

**Preemptive fix**:
- Fitted three-level Bayesian hierarchical model (PyMC, 4 chains × 4,000 iterations)
- Reported both global effect (P(δ₀ < 0) = 0.9779) and domain heterogeneity (P(σ_δ < 0.3) = 0.0000)
- Explained non-significant global finance effect (P = 0.640) as EMH-consistent noise, not a contradiction
- Used "borrow strength" interpretation: small historical samples inform global prior, large financial samples constrain posterior

**Status**: ✅ Fixed in v12.0, retained in v14.0/v17.0

---

## Fix 10: Survivorship Bias Prevention (v10.0)

**Anticipated critique**: "Did you test many domains and only report the ones that worked?"

**Preemptive fix**:
- Explicitly stated: "We tested eight domains and report all eight"
- Listed all eight domains with selection rationale (a priori based on data availability)
- Added limitation: "data availability itself introduces selection bias"
- No domains were attempted and discarded

**Status**: ✅ Fixed in v10.0, retained in v14.0/v17.0

---

## Fix 11: AI Methodology Transparency (v9.0–v14.0)

**Anticipated critique**: "This paper was written by AI. How can we trust it?"

**Preemptive fix**:
- Added detailed AI methodology section (Q9 in anticipated_qa.md)
- Distinguished what AI did (data processing, code generation, literature synthesis) from what AI did NOT do (hypothesis generation, crisis curation, threshold selection, final validation)
- Documented "Ma Laoshi" review model (human expert review with 12-item checklist)
- Provided full code and data for independent replication
- Acknowledged AI errors (v6.0 → v6.1.1 H-β correction discovered by methodological upgrade)

**Status**: ✅ Fixed in v9.0/v14.0, retained in v17.0

---

## Summary Table

| Fix # | Issue | First Fixed | Status |
|-------|-------|-------------|--------|
| 1 | Mesopotamian validation honesty | v10.0 | ✅ Retained |
| 2 | Effect size language | v7.0 | ✅ Retained |
| 3 | ROC AUC two-tier reporting | v9.0 | ✅ Retained |
| 4 | H-β estimator upgrade | v6.1.1 | ✅ Retained |
| 5 | "Counterintuitive" → "unexpected" | v7.0 | ✅ Retained |
| 6 | Policy claims downgrade | v7.0 | ✅ Retained |
| 7 | Cross-civilization exploratory framing | v9.0 | ✅ Retained |
| 8 | SPI post-hoc defense | v12.0 | ✅ Retained |
| 9 | Bayesian hierarchical model | v12.0 | ✅ Retained |
| 10 | Survivorship bias prevention | v10.0 | ✅ Retained |
| 11 | AI methodology transparency | v9.0 | ✅ Retained |

---

*Preemptive fixes documented: 2026-06-05*  
*All fixes are incorporated in the v17.0 submission package*
