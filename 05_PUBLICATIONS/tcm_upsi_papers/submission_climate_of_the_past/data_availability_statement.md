# Data Availability Statement

## Primary Datasets

All datasets, code, models, and supplementary materials supporting this study are publicly available under open licenses to ensure full reproducibility and transparency.

### Internal Historical Event Database
- **File**: `historical_events_v21.json`
- **Location**: `/Users/wangzr/Desktop/历史事件预测建模/01_TCM_UPSI_CORE/03_历史事件数据库/`
- **Description**: Manually curated database of 1,202 historical events (1906–2025) with severity scores (1–10), geographic coordinates, temporal bounds, and categorical labels
- **License**: CC BY 4.0
- **Format**: JSON with schema documentation

### Blinded Re-Collection Database
- **File**: `wikipedia_blinded_events_683.json`
- **Location**: `/Users/wangzr/Desktop/历史事件预测建模/01_TCM_UPSI_CORE/03_历史事件数据库/`
- **Description**: 683 events collected by researchers unaware of WuYun-LiuQi assignments, used for selection bias assessment
- **License**: CC BY 4.0

### External Validation Datasets

| Dataset | Source | File | License |
|---------|--------|------|---------|
| UCDP/PRIO Armed Conflict | Uppsala University | `Phase55_UCDP_Validation_Results.json` | Public domain (UCDP terms) |
| Earthquake Catalog (≥ M7) | USGS/ISC | `earthquake_validation_m7.json` | Public domain |
| Historical Epidemics | Literature compilation | `epidemic_subset_16events.json` | CC BY 4.0 |

### Climate Data

| Index | Source | Temporal Coverage | Spatial Coverage | File |
|-------|--------|-------------------|------------------|------|
| ENSO (Niño 3.4) | NOAA Climate Prediction Center | 1906–2025 | Tropical Pacific | `Phase54_Climate_Data_Realtime.json` |
| PDO | JISAO, University of Washington | 1906–2025 | North Pacific | `Phase54_Climate_Data_Realtime.json` |
| GISTEMP | NASA GISS | 1906–2025 | Global | `Phase54_Climate_Data_Realtime.json` |
| NOAA Global Temperature | NOAA National Centers for Environmental Information | 1906–2025 | Global | `Phase54_Climate_Data_Realtime.json` |

All climate data were obtained from public repositories and are redistributable under their respective terms of use.

## Code and Software

### Source Code Repository
- **Location**: `/Users/wangzr/Desktop/历史事件预测建模/04_CODE/tcm_upsi/`
- **License**: MIT License
- **Language**: Python 3.11

### Key Modules

| Module | Description | File |
|--------|-------------|------|
| Dual-model API | Annual + monthly Random Forest inference | `api_dual_model.py` |
| WuYun-LiuQi engine | 60-year and 6-phase cycle computation | `wuyun_liuqi_engine.py` |
| Granger causality | F-test implementation for nested regression | `granger_causality.py` |
| Cross-validation | Expanding-window and sliding-window CV | `temporal_cv.py` |
| Probability calibration | ECE computation and reliability diagrams | `calibration_analysis.py` |
| Feature engineering | Annual and monthly feature generation | `feature_engineering.py` |
| Bias assessment | Blinded re-collection protocol | `blinded_collection.py` |

### Dependencies
- scikit-learn ≥ 1.3.0 (Random Forest, metrics)
- SciPy ≥ 1.11.0 (Granger F-tests, statistical tests)
- NumPy ≥ 1.24.0
- Pandas ≥ 2.0.0
- Matplotlib ≥ 3.7.0 (visualization)

## Model Artifacts

| Model | File | Description |
|-------|------|-------------|
| Annual Strategic Model | `model_annual_rf_v20.pkl` | Random Forest, 15 features, AUC = 0.9538 |
| Monthly Tactical Model | `model_monthly_rf_v20.pkl` | Random Forest, 34 features, AUC = 0.9941 |
| LSTM Benchmark | `model_monthly_lstm_v20.h5` | Deep learning baseline, AUC = 0.5356 |

## API and Real-Time Service

A deployed API provides real-time risk assessment with live climate integration:
- **Endpoint**: [To be filled — if public]
- **Documentation**: `/Users/wangzr/Desktop/历史事件预测建模/04_CODE/tcm_upsi/api_docs.md`
- **OpenAPI spec**: `openapi_spec.yaml`

## Supplementary Materials

All supplementary materials (SI S1–S15) are available in the `supplementary_materials/` directory accompanying this submission. See `supplementary_index.md` for detailed contents.

## Data Archival

Primary datasets and code are archived at:
- **Zenodo**: [DOI to be assigned upon acceptance]
- **GitHub**: [Repository URL to be filled]
- **Figshare**: [DOI to be assigned upon acceptance]

## Reproducibility Statement

All figures, tables, and statistical results in the main text can be reproduced by running the analysis pipeline:

```bash
python run_full_pipeline.py --config pipeline_config.yaml --output results/
```

Expected runtime: ~45 minutes on a standard workstation (Intel i7 or equivalent, 16 GB RAM).

## Contact for Data Access

For questions regarding data access, code execution, or reproduction of results, please contact the corresponding author at [email to be filled].

---

**Data availability compliance**: This statement adheres to the *Climate of the Past* data policy and the Copernicus Publications open data requirements. All data are available without restriction at the time of submission.
