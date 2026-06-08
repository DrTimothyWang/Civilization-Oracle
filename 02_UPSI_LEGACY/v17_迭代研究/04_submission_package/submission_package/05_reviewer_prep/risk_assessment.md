# Risk Assessment — Submission Risk Matrix

**Version**: v17.0  
**Date**: 2026-06-05  
**Target**: *Nature* Letter  
**Backup**: *PNAS* (6-page format)

---

## Overall Risk Profile

| Criterion | Assessment | Risk Level |
|-----------|-----------|------------|
| Novelty | First unified cross-domain crisis index across 5,500 years | Low |
| Scope | 8 domains, ~3.6M observations | Low |
| Rigor | HAC, PSM, permutation, Bayesian hierarchical | Low |
| Honesty | Explicit limitations, near-random baseline AUC reported | Low |
| Relevance | Complexity science, finance, history, policy | Low |
| **Weaknesses** | Small historical N, proxy limitations, AI-assisted | **Medium** |
| **Fit** | Nature Letter (4 pages) may be too short for scope | **Medium** |

**Overall risk**: Medium-Low. Strong empirical result with honest limitations. Main risk is scope-length mismatch for Nature Letter format.

---

## Risk Matrix by Reviewer Concern

| Concern | Probability | Impact | Risk Level | Mitigation |
|---------|-------------|--------|------------|------------|
| "Too broad for Nature Letter" | 40% | High | Medium | Emphasize 3 advances; SI handles breadth |
| "Small historical sample (n=7)" | 60% | Medium | Medium | Permutation + Conformal Prediction; Bayesian borrow strength |
| "Proxy limitations (Mesopotamia)" | 50% | Medium | Medium | Honest 75% reporting; SPI resolves 2 failures; proxy boundary analysis |
| "AI-assisted methodology" | 30% | Medium | Low-Medium | Full transparency; human review; independent replication package |
| "Near-random baseline AUC" | 40% | Medium | Medium | Two-tier reporting; "synchronizer, not predictor" framing |
| "Cross-civilization r=0.96 is spurious" | 20% | Low | Low | Explicitly labeled exploratory; full caveats in SI |
| "LSTM 78% is unimpressive" | 30% | Low | Low | Intentionally reported as negative result; not used for prediction |
| "Policy overpromising" | 25% | Medium | Low | Downgraded claims; pilot program proposal; explicit caveats |
| "Seshat 75% with 5.8% precision" | 35% | Low | Low | Labeled as proof-of-concept; cross-methodological robustness argument |
| "H=1.57 vs Gatheral contradiction" | 20% | Low | Low | Different objects/scales; explicit comparison table |

---

## Scenario Analysis

### Scenario A: Accept Without Revision (Probability: 15%)
- **Trigger**: Reviewers find novelty sufficient, limitations honestly reported, scope appropriate for Letter
- **Action**: Celebrate; assemble full SI; upload code to GitHub; publish data on Zenodo
- **Timeline**: 2–4 weeks for production

### Scenario B: Minor Revision (Probability: 35%)
- **Trigger**: Reviewers request clarifications, additional SI material, or minor figure adjustments
- **Likely requests**:
  - Expand Methods section (currently 800 words)
  - Add SI figure for Seshat NGA map
  - Clarify SPI weight derivation
  - Add more detailed proxy boundary analysis
- **Action**: Address within 4 weeks; resubmit
- **Timeline**: 4 weeks revision + 2 weeks re-review

### Scenario C: Major Revision (Probability: 30%)
- **Trigger**: Reviewers question core claims, request additional validation, or suggest structural changes
- **Likely requests**:
  - Expand historical sample beyond n=7 (requires new data collection)
  - Add walk-forward out-of-sample validation for finance
  - Validate on additional Seshat NGAs (10+ instead of 5)
  - Separate PSI and SPI into two papers
  - Add causal identification beyond PSM (SDID, FCI)
- **Action**: Prioritize changes; some may be deferred to future work
- **Timeline**: 8 weeks revision + 4 weeks re-review
- **Risk**: Some requests may be infeasible within revision window

### Scenario D: Reject with Encouragement to Resubmit (Probability: 15%)
- **Trigger**: Reviewers find value but scope too broad for Letter, or methodological concerns too serious for quick fix
- **Likely feedback**:
  - "Consider Nature Communications or PNAS for full-length treatment"
  - "Split into two papers: PSI framework + SPI extension"
  - "Add more domains before claiming cross-domain universality"
- **Action**: Evaluate feedback; consider PNAS transfer or Nature Communications
- **Timeline**: 2 weeks decision + 4 weeks reformatting

### Scenario E: Reject (Probability: 5%)
- **Trigger**: Fundamental disagreement on validity of approach or irredeemable flaws
- **Likely feedback**:
  - "Proxy-based historical validation is inherently circular"
  - "UPSI is an arbitrary weighted sum without theoretical foundation"
  - "AI-assisted research lacks methodological credibility"
- **Action**: Evaluate carefully; if valid, publish as preprint and pivot; if biased, appeal or resubmit elsewhere
- **Timeline**: Indefinite

---

## Risk Mitigation Strategies

### Pre-Submission (Now)
1. ✅ Honest limitation reporting throughout manuscript
2. ✅ Preemptive fixes documented (see `preemptive_fixes.md`)
3. ✅ Anticipated Q&A prepared (see `anticipated_qa.md`)
4. ✅ PNAS backup manuscript ready (`pnas_backup.md`)
5. ☐ Generate 300-dpi versions of all figures (currently screen resolution)
6. ☐ Verify all references have DOIs
7. ☐ Run final spell-check and grammar check

### Post-Submission (If Revision Requested)
1. **Minor revision**: Address all points within 4 weeks; no new data collection needed
2. **Major revision**: Prioritize:
   - High impact + feasible: Additional Seshat NGAs (can be done in 4–6 weeks)
   - High impact + infeasible: Expand historical sample beyond n=7 (defer to future work)
   - Medium impact + feasible: Walk-forward validation for finance (2–3 weeks)
   - Low impact + feasible: Additional SI figures and tables
3. **Reject with encouragement**: Reformat for PNAS or Nature Communications within 2 weeks

### Post-Rejection (If Occurs)
1. Publish preprint on arXiv or bioRxiv within 1 week
2. Upload full code and data to GitHub immediately
3. Solicit community feedback via Twitter/X, Reddit r/statistics, Hacker News
4. Prepare revised version for PNAS or Nature Communications
5. Consider splitting into two papers:
   - Paper 1: PSI framework + 7-domain validation (Nature Communications)
   - Paper 2: SPI + UPSI_v2 + Dashboard (PNAS or specialist journal)

---

## PNAS Transfer Plan

If Nature rejects or requests transfer:

| Aspect | Nature Letter | PNAS Backup |
|--------|--------------|-------------|
| Format | 4 pages, ~3,000 words | 6 pages, ~3,500 words |
| Figures | 4 main | 3 main |
| References | 25 | 32 |
| SI | 22 sections | 15 sections |
| Significance Statement | Not required | Required (120 words) |
| APC | ~$5,000 | ~$2,400 |
| Review time | 2–3 months | 4–6 months |

**PNAS advantages**:
- Longer format allows more detailed Methods
- Turchin has 4 PNAS cliodynamics papers (precedent)
- Lower APC
- 6 pages is better fit for scope

**PNAS disadvantages**:
- Lower impact factor than Nature
- Longer review time
- No "Letter" prestige

---

## Final Risk Score

| Category | Score (1–10) | Weight | Weighted |
|----------|-------------|--------|----------|
| Empirical strength | 8 | 25% | 2.0 |
| Methodological rigor | 7 | 20% | 1.4 |
| Novelty | 9 | 20% | 1.8 |
| Honesty/transparency | 9 | 15% | 1.35 |
| Fit to journal format | 5 | 10% | 0.5 |
| Reviewer bias risk | 6 | 10% | 0.6 |
| **Total** | | | **7.65 / 10** |

**Interpretation**: 7.65/10 = Good chance of at least minor revision. Strong empirical result with honest reporting. Main risk is format fit (Nature Letter may be too short) and small historical sample.

---

*Risk assessment prepared: 2026-06-05*  
*Recommendation: Submit to Nature Letter; prepare for minor-to-major revision; PNAS backup ready*
