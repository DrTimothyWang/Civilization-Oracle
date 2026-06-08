# Code Availability Statement

**Manuscript**: A Cross-Domain Pressure Synchronization Index for Crisis Detection Across Civilizations  
**Version**: v17.0  
**Date**: 2026-06-05

---

## Summary

All code is available at **github.com/Mavis-Foundation/UPSI** upon publication. The repository includes Python scripts for PSI/SPI computation, validation, visualization, and the real-time Dashboard. A Docker container with pinned dependencies ensures full reproducibility.

---

## Repository Structure

```
UPSI/
├── psi_engine.py              # Domain-agnostic PSI calculator
├── spi_engine.py              # Sudden Pressure Indicator (burst-crisis detection)
├── upsi_v2.py                 # Four-quadrant state-space classifier
├── seshat_psi.py              # Seshat-to-UPSI variable mapping
├── dashboard/                 # Cloud-deployable monitoring system
│   ├── src/
│   │   ├── data_fetcher.py
│   │   ├── psi_engine.py
│   │   ├── spi_engine.py
│   │   ├── alert_system.py
│   │   └── renderer.py
│   ├── config/config.yaml
│   ├── .github/workflows/dashboard.yml
│   └── requirements.txt
├── validation/                # Statistical validation scripts
│   ├── roc_analysis.py
│   ├── permutation_test.py
│   ├── psm_analysis.py
│   ├── hac_standard_errors.py
│   └── bayesian_hierarchical.py
├── viz/                       # Visualization scripts
│   ├── phase_portrait.py
│   ├── quadrant_timeline.py
│   └── alert_table.py
├── notebooks/                 # Jupyter notebooks for all figures
│   ├── fig1_domain_validation.ipynb
│   ├── fig2_psi_spi_duality.ipynb
│   ├── fig3_spectrum.ipynb
│   └── fig4_dashboard.ipynb
├── reproduce.py               # One-command reproduction
├── requirements.txt           # Pinned dependencies
├── Dockerfile                 # Containerized environment
└── README.md                  # Step-by-step instructions
```

---

## Core Modules

### 1. PSI Engine (`psi_engine.py`)
- **Purpose**: Domain-agnostic Pressure Synchronization Index calculator
- **Inputs**: Raw time series (financial prices, historical events, political data)
- **Outputs**: PSI time series, z-scored components, distress flags
- **Key functions**:
  - `compute_psi(material, fragmentation, disengagement, weights=(0.4, 0.3, 0.3))`
  - `z_normalize(series, window)`
  - `distress_flag(psi_series, threshold=-0.5)`

### 2. SPI Engine (`spi_engine.py`)
- **Purpose**: Sudden Pressure Indicator for burst-crisis detection
- **Inputs**: Short-window aggregated counts, geographic distribution
- **Outputs**: SPI time series, spike alerts (CRITICAL/ELEVATED/NORMAL)
- **Key functions**:
  - `compute_spi(velocity, acceleration, delta_gsi, vol_spike, weights=(0.35, 0.25, 0.25, 0.15))`
  - `adaptive_tau(n_period, n_exact)`
  - `spike_detect(spi_series, threshold=2.5)`

### 3. UPSI_v2 Classifier (`upsi_v2.py`)
- **Purpose**: Four-quadrant state-space crisis classifier
- **Inputs**: PSI level, SPI rate, domain confidence weights
- **Outputs**: Quadrant labels (Stable, Gradual Decline, Sudden Crisis, Accelerating Collapse)
- **Key functions**:
  - `classify_quadrant(psi, spi, w_spi)`
  - `phase_portrait(psi_series, spi_series)`
  - `quadrant_timeline(quadrant_series)`

### 4. Seshat PSI (`seshat_psi.py`)
- **Purpose**: Seshat Global History Databank integration
- **Inputs**: Seshat Equinox-2020 CSV (polity population, territory, hierarchy levels, etc.)
- **Outputs**: Century-level UPSI for 5+ NGAs
- **Key functions**:
  - `map_seshat_to_upsi(seshat_df)`
  - `impute_missing(df, method='nga_mean')`
  - `compute_century_psi(nga_data, window=3)`

---

## Software Versions

| Package | Version |
|---------|---------|
| Python | 3.10+ |
| numpy | 1.24.0 |
| pandas | 2.0.0 |
| scipy | 1.10.0 |
| scikit-learn | 1.3.0 |
| PyTorch | 2.0.0 |
| PyMC | 5.12.0 |
| arviz | 0.15.0 |
| matplotlib | 3.7.0 |
| yfinance | 0.2.0 |
| nolds | 0.5.2 |

---

## Reproducibility

### One-Command Reproduction
```bash
git clone https://github.com/Mavis-Foundation/UPSI.git
cd UPSI
pip install -r requirements.txt
python reproduce.py
```

### Docker Reproduction
```bash
docker build -t upsi .
docker run -v $(pwd)/output:/app/output upsi
```

### Expected Runtime
- Full reproduction (all figures, tables, validations): ~4 hours on a 4-core CPU
- Dashboard local test: ~5 minutes
- Individual figure: ~10–30 minutes

---

## License

All code is released under the **MIT License** unless otherwise noted. The Dashboard repository is also MIT-licensed. Seshat data integration respects the CC BY-NC-SA 4.0 license of the Seshat Databank.

---

## Contact

For technical questions about the code, please open an issue at github.com/Mavis-Foundation/UPSI or contact the Mavis Agent Team.

---

*Code availability statement prepared: 2026-06-05*
