# v13a Seshat 8th Domain — Technical Integration Plan

> **Date**: 2026-06-04  
> **Version**: v13.0-alpha  
> **Owner**: Seshat_8th_Domain_Researcher  
> **Status**: Draft — pending Week 1 data download validation

---

## 1. Executive Summary

This document specifies the technical architecture, data pipeline, PSI computation strategy, and validation protocol for integrating **Seshat: Global History Databank** as Domain 8 of the UPSI (Unified Pressure Synchronization Index) framework. The plan is scoped to a **4–6 week prototype** using the **Equinox-2020 snapshot** (374 polities, 136 variables, 47,400 records) across **5 priority NGAs**, with a clear go/no-go gate at Week 3.

**Key design decisions**:
- **No API dependency**: Seshat lacks a public REST API. Pipeline uses CSV download → local ETL.
- **100-year timestep**: Coarser than CBDB (decadal) but aligned with Seshat's native century-mark sampling. PSI z-scores computed over rolling 3-century windows.
- **Interpolation-aware computation**: Flag and down-weight interpolated Seshat records (`uniq = n`) to avoid artificial stability bias.
- **Bayesian validation**: Replicate v12 hierarchical model to estimate P(crisis << stable) and cross-NGA heterogeneity.

---

## 2. Data Pipeline Architecture

### 2.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SESHAT DATA PIPELINE (v13)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Layer 1: INGEST                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Equinox-2020 │  │ Social Comp. │  │   Agri Prod. │  │ Consequences │     │
│  │   CSV/TSV    │  │   Dataset    │  │   Dataset    │  │   of Crisis  │     │
│  │  (Zenodo)    │  │  (seshat-db) │  │  (seshat-db) │  │  (seshat-db) │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │              │
│  Layer 2: ETL & MERGE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  PolityMasterTable (polity_id × century × all_variables)            │    │
│  │  - Left-join Equinox-2020 (base) + Social Complexity + Agri + Crisis│    │
│  │  - Key: (polity_id, century_mark)                                   │    │
│  │  - Flag interpolated rows (source = 'interpolated' vs 'observed')   │    │
│  └────────────────────────┬────────────────────────────────────────────┘    │
│                           │                                                │
│  Layer 3: PSI COMPUTATION                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  NGA-level z-scores (rolling 3-century window, interpolation-aware) │    │
│  │  Material(z)  ← population, territory, agri yield (inverted)        │    │
│  │  Fragmentation(z) ← |Δ hierarchy| + |Δ governance| + |Δ MilTech|    │    │
│  │  Disengagement(z) ← info systems, infrastructure, bureaucrats     │    │
│  │  UPSI = 0.4×Material + 0.3×Fragmentation + 0.3×Disengagement        │    │
│  └────────────────────────┬────────────────────────────────────────────┘    │
│                           │                                                │
│  Layer 4: VALIDATION                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Crisis label merge (Consequences of Crisis 13 binary indicators)   │    │
│  │  Threshold: UPSI < -0.5 (distress) vs UPSI ≥ -0.5 (stable)           │    │
│  │  Metrics: Recall, Precision, F1, Cohen's d, Walk-Forward r            │    │
│  │  Bayesian Hierarchical: P(δ_0 < 0) posterior                      │    │
│  └────────────────────────┬────────────────────────────────────────────┘    │
│                           │                                                │
│  Layer 5: OUTPUT & DASHBOARD                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  v13b_seshat_results.json (per-NGA + aggregate)                     │    │
│  │  UPSI Dashboard v2.4+ Seshat panel (time series + crisis markers)   │    │
│  │  PNAS SI Dataset S3 (replication package)                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Specifications

#### 2.2.1 Ingest Module (`seshat_ingest.py`)

| Function | Input | Output | Library |
|----------|-------|--------|---------|
| `download_equinox()` | Zenodo DOI `10.5281/zenodo.6642229` | `raw/equinox_2020.csv` | `requests`, `zenodo_get` |
| `download_replication()` | URLs from `seshat-db.com/downloads_page/` | `raw/social_complexity.csv`, `raw/agri_productivity.csv`, `raw/consequences_of_crisis.csv` | `requests`, `pandas` |
| `validate_checksum()` | SHA256 from Zenodo metadata | Boolean | `hashlib` |

**Error handling**:
- Zenodo rate-limit: retry with exponential backoff (max 5 attempts).
- Missing replication dataset: log warning; proceed with Equinox-2020 base + manual crisis list.

#### 2.2.2 ETL Module (`seshat_etl.py`)

| Function | Description |
|----------|-------------|
| `load_master_table()` | Reads all CSVs; standardizes column names to snake_case; creates `polity_id` from NGA + polity name slug. |
| `merge_datasets()` | Left-join on `(polity_id, century_mark)`. Century marks are rounded to nearest 100 (Seshat convention). |
| `flag_interpolated()` | Reads `uniq` column (or infers from duplicate values across consecutive centuries). Sets `data_type ∈ {observed, interpolated}`. |
| `impute_missing()` | MICE (Multiple Imputation by Chained Equations) for numeric variables; mode imputation for binary. **Only for non-crisis-label columns.** |
| `export_clean()` | Parquet format for fast I/O; JSON schema for cross-language compatibility. |

**Data quality gates**:
- Gate 1: ≥ 80% of target variables present for a polity → include in PSI computation.
- Gate 2: ≥ 3 consecutive centuries of data → include in z-score window.
- Gate 3: Crisis label available (any of 13 indicators) → include in validation set.

#### 2.2.3 PSI Computation Module (`seshat_psi.py`)

**Rolling window specification**:
- Window size: 3 centuries (minimum n=3 for z-score).
- Step size: 1 century.
- Interpolation weighting: observed records weight = 1.0; interpolated records weight = 0.5 in window mean/std calculation.

**Per-NGA normalization**:
- All z-scores computed **within NGA** to control for geographic baseline (e.g., Egypt vs. Iceland carrying capacity).
- Global cross-NGA z-score computed as secondary robustness check.

**GSI (Geographical Stress Index) for Seshat**:
- Phase 1 (prototype): GSI = 1.0 (neutral) for all NGAs.
- Phase 2 (expansion): Use Pleiades coordinates + paleo-climate proxies (if available) or modern climate CV to compute [0.8, 1.4] range.

#### 2.2.4 Validation Module (`seshat_validate.py`)

| Function | Description |
|----------|-------------|
| `merge_crisis_labels()` | Joins Consequences of Crisis 13 binary indicators. Computes `crisis_severity_score = sum(indicators)` (range 0–13). |
| `compute_metrics()` | Recall, Precision, F1 at UPSI < -0.5 threshold; Cohen's d (individual-century level); Walk-Forward correlation (if time series long enough). |
| `bayesian_hierarchical()` | PyMC model: `crisis_i ~ Bernoulli(p_i)`; `logit(p_i) = α_nga[j] + β × UPSI_i`; `α_nga ~ Normal(μ_α, σ_α)`; priors from v12 model. |
| `export_results()` | JSON + CSV for dashboard ingestion; LaTeX table for manuscript. |

---

## 3. PSI Computation Strategy for Historical NGAs

### 3.1 Variable Selection (Equinox-2020)

Based on data completeness and theoretical relevance, the prototype uses **12 core variables**:

| UPSI Dimension | Seshat Variable(s) | Equinox-2020 Column(s) | Completeness | Transform |
|----------------|--------------------|------------------------|--------------|-----------|
| **Material** | Polity population | `PolPop` (log) | ~85% | z-score, invert |
| | Polity territory | `PolTerr` (log) | ~85% | z-score, invert |
| | Agricultural productivity | `AgriProd` (tonnes/ha) | ~55% | z-score, invert |
| **Fragmentation** | Hierarchy levels (admin + military + settlement) | `HierLevels` | ~80% | abs(Δ), z-score |
| | Governance sophistication | `GovSoph` (PC1) | ~70% | abs(Δ), z-score |
| | Military technology | `MilTech` | ~70% | abs(Δ), z-score |
| **Disengagement** | Information systems | `InfoSys` (PC1) | ~75% | z-score, invert |
| | Infrastructure | `Infrastructure` (PC1) | ~65% | z-score, invert |
| | Full-time bureaucrats | `Bureaucrats` (binary) | ~65% | z-score, invert |
| | Professional officers | `Officers` (binary) | ~65% | z-score, invert |
| | Legal codes | `LegalCodes` (binary) | ~65% | z-score, invert |
| | Courts | `Courts` (binary) | ~65% | z-score, invert |

**Missing variable fallback**:
- If `AgriProd` is missing for a polity-century, impute from NGA-level mean by century.
- If any binary institutional variable is missing, treat as 0 (conservative: assume absence of institution = higher disengagement stress).

### 3.2 Computation Pseudocode

```python
# seshat_psi.py — core computation

def compute_nga_psi(nga_df: pd.DataFrame) -> pd.DataFrame:
    """
    nga_df: polity-century records for a single NGA
    returns: nga_df with Material_z, Fragmentation_z, Disengagement_z, UPSI
    """
    # --- Material ---
    material_vars = ['PolPop', 'PolTerr', 'AgriProd']
    nga_df['Material_raw'] = nga_df[material_vars].mean(axis=1, skipna=True)
    nga_df['Material_z'] = -zscore(nga_df['Material_raw'])  # invert: decline = stress

    # --- Fragmentation ---
    frag_vars = ['HierLevels', 'GovSoph', 'MilTech']
    for v in frag_vars:
        nga_df[f'{v}_delta'] = nga_df[v].diff().abs()
    nga_df['Fragmentation_raw'] = nga_df[[f'{v}_delta' for v in frag_vars]].mean(axis=1, skipna=True)
    nga_df['Fragmentation_z'] = zscore(nga_df['Fragmentation_raw'])

    # --- Disengagement ---
    diseng_vars = ['InfoSys', 'Infrastructure', 'Bureaucrats', 'Officers', 'LegalCodes', 'Courts']
    nga_df['Disengagement_raw'] = nga_df[diseng_vars].mean(axis=1, skipna=True)
    nga_df['Disengagement_z'] = -zscore(nga_df['Disengagement_raw'])  # invert: decline = stress

    # --- UPSI ---
    nga_df['UPSI'] = (
        0.4 * nga_df['Material_z'].fillna(0) +
        0.3 * nga_df['Fragmentation_z'].fillna(0) +
        0.3 * nga_df['Disengagement_z'].fillna(0)
    )

    # --- Interpolation weighting ---
    nga_df['UPSI_weighted'] = np.where(
        nga_df['data_type'] == 'interpolated',
        nga_df['UPSI'] * 0.5,
        nga_df['UPSI']
    )

    return nga_df
```

### 3.3 Threshold & State Classification

- **Distress**: UPSI < -0.5 (same threshold as existing 7 domains).
- **Stable**: UPSI ≥ -0.5.
- **Crisis lead time**: Not applicable at 100-year resolution; instead measure **co-occurrence** (crisis century vs. distress century).
- **Robustness check**: Test thresholds at -0.3, -0.5, -0.7 to assess sensitivity.

---

## 4. Validation Approach

### 4.1 Ground Truth: Crisis Events

Seshat's **Consequences of Crisis** dataset codes 13 binary crisis indicators per polity-century. We use these as ground truth, supplemented by well-known historical crises for polities not yet coded.

| NGA | Polity | Crisis Century | Crisis Type | Expected UPSI |
|-----|--------|--------------|-------------|---------------|
| Upper Egypt | Old Kingdom | -2200 | Collapse (First Intermediate) | < -0.5 |
| Upper Egypt | New Kingdom (Ramesside) | -1100 | Decline + Civil War (Sea Peoples) | < -0.5 |
| Latium | Roman Empire (Dominate) | 300–400 | Crisis of 3rd Century + Fragmentation | < -0.5 |
| Susiana | Elamite polity | -1000 | Decline + Conquest (Assyrian) | < -0.5 |
| Middle Yellow River Valley | Shang → Zhou transition | -1100 | Decline + Conquest | < -0.5 |
| Valley of Oaxaca | Monte Albán | 700–800 | Decline + Collapse | < -0.5 |

**Validation metrics**:
1. **Recall**: Fraction of crisis centuries with UPSI < -0.5.
2. **Precision**: Fraction of UPSI < -0.5 centuries that are true crises.
3. **F1**: Harmonic mean of recall and precision.
4. **Cohen's d**: Effect size between crisis vs. non-crisis centuries (individual level).
5. **Bayesian P(crisis << stable)**: Hierarchical model posterior probability.

### 4.2 Cross-Method Validation

For **Latium**, compare Seshat-derived UPSI with existing **Ancient Rome domain** (LLM-evaluated text corpus). This tests whether:
- Structural variable-based PSI (Seshat) converges with text-density-based PSI (existing Rome domain).
- If correlation r > 0.7, it validates both methods; if r < 0.3, it reveals domain-specific bias.

### 4.3 Blind Test Design

Since Seshat covers pre-1900 societies, true "blind prediction" of future crises is impossible. Instead:
- **Hold-out NGA test**: Train z-score parameters on 4 NGAs; compute UPSI on the 5th held-out NGA using training-set means/SDs.
- **Temporal hold-out**: For NGAs with >10 centuries of data, train on first 70% of centuries; validate on last 30%.

---

## 5. Timeline & Milestones

### 5.1 6-Week Sprint Plan

| Week | Milestone | Deliverable | Success Criteria | Owner |
|------|-----------|-------------|------------------|-------|
| **W1** | Data Ingest & ETL | `seshat_master.parquet` (cleaned, merged, imputed) | All 5 priority NGAs loaded; ≥ 60% variable completeness per NGA | Data Engineer |
| **W2** | PSI Computation | `seshat_psi_timeseries.json` (per-century UPSI for all polities) | Material, Fragmentation, Disengagement z-scores computed; interpolation flags applied | Quant Researcher |
| **W3** | Validation & Go/No-Go Gate | `v13b_midterm_report.md` | Recall ≥ 50% across 5 NGAs; Bayesian model converges (R-hat < 1.05) | Statistician |
| **W4** | IPW-Style Bias Correction | `seshat_psi_corrected.json` | Sensitivity analysis: raw vs. corrected recall difference < 15% | Quant Researcher |
| **W5** | Cross-Domain Comparison | `v13b_cross_domain_report.md` | Latium vs. existing Rome domain correlation computed; dashboard panel drafted | Integration Lead |
| **W6** | Final Report & Replication Package | `v13b_final_report.md` + `SI_Dataset_S3.zip` | PNAS-ready tables; code on GitHub; go/no-go for 35-NGA expansion | Project Lead |

### 5.2 Go/No-Go Criteria at Week 3

| Criterion | Threshold | Go if... | No-Go if... |
|-----------|-----------|----------|-------------|
| Data coverage | ≥ 60% completeness | Met | < 60% → pivot to smaller NGA set or different imputation strategy |
| Recall | ≥ 50% | Met | < 50% → investigate variable mapping; may need to add warfare/religion variables |
| Bayesian convergence | R-hat < 1.05 for all parameters | Met | Divergence → simplify model (remove NGA-level random effects) |
| Effect size | Cohen's d > 0.3 (medium) | Met | d < 0.2 → signal too weak for standalone domain; consider merging with existing history domains |

**No-Go contingency**: If Seshat prototype fails Week 3 gates, pivot to **Perseus Digital Library** (Ancient Greek texts) as Domain 8 alternative, leveraging existing text-density PSI pipeline from Mesopotamia/Rome domains.

### 5.3 Post-Prototype Expansion (Weeks 7–12)

If Week 3 = GO:
- **Weeks 7–8**: Expand to Top 10 NGAs (add Big Island Hawaii, Kansai, Deccan, Paris Basin, Lowland Andes).
- **Weeks 9–10**: Full Equinox-2020 coverage (35 NGAs, 374 polities).
- **Weeks 11–12**: Dashboard integration + PNAS SI preparation + manuscript revision.

---

## 6. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Equinox-2020 download fails / Zenodo downtime | Low | High | Mirror on GitHub (`seshatdb/Equinox_Data`) + local cache |
| Heavy missing data prevents z-score computation | Medium | High | MICE imputation; reduce variable set to 6 highest-completeness vars |
| 100-year resolution too coarse for meaningful recall | Medium | High | Use "crisis century ± 1 century" window for co-occurrence matching |
| Interpolation artifacts suppress true volatility | Medium | Medium | Down-weight interpolated records; exclude from Fragmentation Δ calculation |
| Consequences of Crisis dataset incomplete for target polities | Medium | High | Supplement with historian-curated crisis list (e.g., Cambridge Ancient History) |
| License conflict (CC BY-NC-SA vs. project open-source goals) | Low | Medium | Clearly separate data (NC) from code (MIT/Apache); attribute Seshat in all outputs |
| Turchin et al. data quality scrutiny (re: Big Gods retraction) | Medium | Medium | Pre-register analysis plan; use only "hard" variables; publish all sensitivity analyses |

---

## 7. Dependencies & Resources

### 7.1 Software Stack

| Component | Tool | Version | Purpose |
|-----------|------|---------|---------|
| Data pipeline | Python + Pandas | ≥ 2.0 | ETL, z-score computation |
| Imputation | `sklearn.impute.IterativeImputer` (MICE) | ≥ 1.3 | Missing data handling |
| Bayesian inference | PyMC | ≥ 5.0 | Hierarchical validation |
| Visualization | Matplotlib + Plotly | — | Dashboard panel |
| Storage | Parquet + JSON | — | Fast I/O + cross-language compatibility |

### 7.2 Compute Requirements

- **CPU**: 4 cores (Bayesian sampling is the bottleneck; ~30 min per NGA with 2 chains × 2000 draws).
- **RAM**: 8 GB (Equinox-2020 is < 50 MB; merged dataset < 200 MB).
- **Storage**: 1 GB (raw + intermediate + outputs).
- **GPU**: Not required.

### 7.3 Human Resources

| Role | FTE (6 weeks) | Responsibilities |
|------|--------------|------------------|
| Data Engineer | 0.3 | Download, ETL, quality gates |
| Quantitative Researcher | 0.5 | Variable mapping, PSI computation, sensitivity analysis |
| Statistician | 0.3 | Bayesian model, effect size, replication package |
| Domain Expert (Historian) | 0.2 | Crisis label curation, qualitative validation |
| Integration Lead | 0.2 | Dashboard, cross-domain comparison, manuscript tables |

---

## 8. Outputs & Deliverables

| ID | Name | Format | Due | Location |
|----|------|--------|-----|----------|
| D1 | `seshat_master.parquet` | Parquet | W1 | `v13_迭代研究/01_seshat_domain/data/` |
| D2 | `seshat_psi_timeseries.json` | JSON | W2 | `v13_迭代研究/01_seshat_domain/output/` |
| D3 | `v13b_midterm_report.md` | Markdown | W3 | `v13_迭代研究/01_seshat_domain/` |
| D4 | `v13b_seshat_results.json` | JSON | W6 | `v13_迭代研究/01_seshat_domain/output/` |
| D5 | `SI_Dataset_S3.zip` | ZIP (CSV + code) | W6 | `v13_迭代研究/01_seshat_domain/replication/` |
| D6 | Dashboard Seshat panel | HTML/Plotly | W6 | `v13_迭代研究/03_dashboard_v2/` |
| D7 | `v13b_final_report.md` | Markdown | W6 | `v13_迭代研究/01_seshat_domain/` |

---

## 9. Appendix: File Naming & Schema Conventions

All Seshat-derived files follow UPSI v12+ conventions:
- `seshat_{module}_{version}.{ext}`
- Columns: `nga_id`, `polity_id`, `century_mark`, `data_type`, `{dimension}_z`, `UPSI`, `UPSI_weighted`, `crisis_severity_score`, `crisis_labels[]`
- Metadata block in JSON outputs includes: Seshat citation, download date, variable list, imputation method, interpolation weight.

---

*End of Integration Plan*
