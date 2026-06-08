# Figure 5 — Seshat Global History Databank Coverage Map

**Status**: ⚠️ **Static PNG does not exist in current iteration directories**

**Intended content**: World map showing 5 validated Natural Geographic Areas (NGAs) with validation summary

---

## Why This Figure Matters

The Seshat validation is the **8th domain** and the **cross-methodological robustness test** of UPSI. Unlike the other 7 domains (which use text counts, market prices, or event frequencies), Seshat uses **expert-coded structural variables** (population, territory, hierarchy levels, military technology). The fact that the same 0.4/0.3/0.3 weights and -0.5 threshold achieve 75% recall on entirely independent data types is a key result.

A world map with NGA markers would make this cross-methodological validation visually compelling.

---

## Proposed Map Content

### Validated NGAs (5)

| NGA | Region | Continent | Crises Tested | Recall |
|-----|--------|-----------|---------------|--------|
| Upper Egypt | Africa | Africa | 2/2 | 100% |
| Latium | Europe | Europe | 2/2 | 100% |
| Susiana | Middle East | Asia | 1/2 | 50% |
| Middle Yellow River Valley | East Asia | Asia | 1/1 | 100% |
| Valley of Oaxaca | Mesoamerica | Americas | 0/1 | 0% |
| **Total** | | | **6/8** | **75%** |

### Map Specifications
- **Projection**: Robinson or Natural Earth (global view)
- **Markers**: Colored circles (green = 100% recall, yellow = 50%, red = 0%)
- **Size**: Proportional to number of centuries covered
- **Legend**: NGA name, period, recall, precision
- **Caption**: "Seshat NGA coverage and UPSI validation. Five NGAs across four continents (Africa, Europe, Asia, Americas) validated with 75% recall (6/8 crises). Same 0.4/0.3/0.3 weights and -0.5 threshold applied without modification."

---

## Options for Submission

### Option A: Generate Map (Recommended if time permits)
**Tools**: Python + cartopy or basemap, or R + ggplot2 + rnaturalearth
**Estimated effort**: 2–3 hours
**Steps**:
1. Obtain NGA centroid coordinates from Seshat metadata
2. Plot world map with country boundaries
3. Add colored markers for 5 NGAs
4. Add annotation table with recall/precision
5. Export as 300 dpi PNG (~500 KB)

### Option B: Omit Figure, Use Table in SI
**Rationale**: Seshat is a proof-of-concept, not a primary domain. A table in SI S18 is sufficient.
**Advantage**: Saves figure slot for main text (Nature Letter max 4–6 figures)

### Option C: Reference External Seshat Visualizations
**Source**: seshatdatabank.info has existing world maps of NGA coverage
**Action**: Cite Seshat website and include a simple table in the manuscript text

---

## Recommendation

**For Nature Letter submission**: Use **Option B** (table in SI). The main text already has 4 strong figures. Adding a 5th figure for a proof-of-concept domain may dilute the main message.

**For PNAS or Nature Communications submission**: Use **Option A** (generate map). Longer format allows more figures, and the visual impact of a world map is high.

---

## Source Files for Map Generation

- Seshat data sample: `08_data_samples/seshat_psi.json`
- Seshat engine: `07_code/seshat_psi.py`
- Seshat validation report: `v14_迭代研究/01_seshat_prototype/v14a_seshat_psi_engine.py`

---

*Figure reference prepared: 2026-06-05*
