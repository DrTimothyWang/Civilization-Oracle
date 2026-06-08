# SPI-PSI Integration: UPSI_v2 Framework

**Author**: SPI_Burst_Theorist  
**Date**: 2026-06-04  
**Version**: v13b  
**Status**: Theoretical Integration Specification  

---

## 1. The Duality: PSI and SPI

### 1.1 Why One Indicator Is Insufficient

The v12 boundary condition proved that no single indicator can capture all classes of civilizational crises:

| Crisis Class | Example | PSI (Level) | SPI (Velocity) |
|--------------|---------|-------------|----------------|
| Gradual decline | Roman Empire (3rd-5th c. CE) | ✅ Captures | ⚠️ Noisy |
| Sudden collapse | Hammurabi's empire split (-1750) | ❌ Misses | ✅ Captures |
| Local collapse under empire | Umma (-2037) | ❌ Misses | ✅ Captures |
| Stable low | Dark Age Greece | ✅ Captures | ✅ Normal |
| Recovery/renaissance | Carolingian revival | ⚠️ Ambiguous | ⚠️ Ambiguous |

**PSI** measures the *state* of a system (thermometer reading).  
**SPI** measures the *rate of change* of that state (rate of temperature change).

### 1.2 Mathematical Duality

$$PSI(t) \propto \int_{t-T}^{t} f(s) \, ds \quad \text{(integral, smoothed)}$$

$$SPI(t) \propto \frac{d}{dt} f(t) \quad \text{(derivative, sharpened)}$$

Where $f(t)$ is the raw proxy signal (text counts, financial bars, etc.) and $T$ is the PSI window size (50-100 years).

This is the fundamental **integral-derivative duality**:
- PSI = $\int f \, dt$ (low-pass filter)
- SPI = $\frac{df}{dt}$ (high-pass filter)
- Together they form a complete state-space representation

---

## 2. UPSI_v2: The Combined Indicator

### 2.1 Formal Definition

$$UPSI_{v2}(t) = \mathcal{C}(PSI(t), SPI(t))$$

Where $\mathcal{C}$ is a **crisis classifier** mapping the 2D (PSI, SPI) plane to crisis regimes.

### 2.2 The Four Quadrants

```
                    SPI (Velocity)
                    High          Low
                 ┌─────────┬─────────┐
        High     │    A    │    B    │
   PSI           │ACCELERATING│GRADUAL │
   (Level)       │COLLAPSE │DECLINE  │
                 ├─────────┼─────────┤
        Low      │    C    │    D    │
                 │ SUDDEN  │ STABLE  │
                 │ CRISIS  │         │
                 │IMMINENT │         │
                 └─────────┴─────────┘
```

| Quadrant | PSI | SPI | Regime Name | Interpretation | Action |
|----------|-----|-----|-------------|----------------|--------|
| A | High | High | **Accelerating Collapse** | System under peak pressure AND deteriorating rapidly | CRITICAL: Collapse likely within years |
| B | High | Low | **Gradual Decline** | Pressure building but stable rate | WARNING: Monitor for SPI spike |
| C | Low | High | **Sudden Crisis Imminent** | System fragile, shock incoming | ALERT: Sudden transition likely |
| D | Low | Low | **Stable** | No significant pressure | NORMAL: No action needed |

### 2.3 Alert Levels

| PSI | SPI | UPSI_v2 Alert | Color | Time Horizon |
|-----|-----|---------------|-------|--------------|
| Low | Low | STABLE | 🟢 Green | N/A |
| High | Low | GRADUAL_PRESSURE | 🟡 Yellow | Decades |
| Low | High | SUDDEN_CRISIS | 🟠 Orange | Years |
| High | High | ACCELERATING_COLLAPSE | 🔴 Red | Months-Years |

### 2.4 Transition Dynamics

Civilizations move through the quadrants in characteristic patterns:

**Pattern 1: Gradual → Accelerating → Collapse**
```
D (Stable) → B (Gradual Decline) → A (Accelerating Collapse) → C (Post-collapse Sudden Crisis) → D (New Stable)
```
Example: Late Roman Republic → Imperial Crisis of 3rd Century → Fall of West

**Pattern 2: Stable → Sudden Crisis**
```
D (Stable) → C (Sudden Crisis Imminent) → D (New Stable or Collapse)
```
Example: Hammurabi's unified empire → sudden split (-1750)

**Pattern 3: False Alarm (SPI noise)**
```
D → C → D (no collapse)
```
SPI can spike due to data noise or non-crisis shocks (e.g., major construction project producing temporary record surge).

---

## 3. Integration Architecture

### 3.1 Data Pipeline

```
Raw Data (same for both)
    │
    ├──→ PSI Pipeline ──→ 50-100 year windows ──→ Level z-scores ──→ PSI(t)
    │
    └──→ SPI Pipeline ──→ 1-10 year windows ──→ Velocity z-scores ──→ SPI(t)
                              │
                              └──→ Detection algorithms:
                                   - Sudden drop detection
                                   - Volatility spike detection
                                   - Correlation breakdown detection
    │
    └──→ UPSI_v2 Classifier ──→ Quadrant assignment ──→ Alert level
```

### 3.2 Confidence Weighting

UPSI_v2 weights PSI and SPI based on data confidence:

$$UPSI_{v2}(t) = w_{PSI}(t) \cdot \mathcal{C}_{PSI}(PSI(t)) + w_{SPI}(t) \cdot \mathcal{C}_{SPI}(SPI(t))$$

Where:
- $w_{PSI} + w_{SPI} = 1$
- $w_{SPI}$ increases with exact-year data ratio
- $w_{PSI}$ dominates in sparse-data regimes (ancient)
- $w_{SPI}$ dominates in high-resolution regimes (modern)

| Domain | Exact-Year Ratio | $w_{PSI}$ | $w_{SPI}$ | Primary Indicator |
|--------|-----------------|-----------|-----------|-------------------|
| Ur III (ancient) | 75.8% | 0.4 | 0.6 | SPI (high resolution) |
| Old Babylonian | 0.03% | 0.9 | 0.1 | PSI (interpolation needed) |
| Neo-Assyrian | 37.3% | 0.5 | 0.5 | Balanced |
| COVID-19 (modern) | 100% | 0.2 | 0.8 | SPI (real-time) |
| Financial markets | 100% | 0.3 | 0.7 | SPI (high frequency) |

### 3.3 Temporal Resolution Bridge

A key challenge: PSI and SPI operate on different time scales. How do we compare them?

**Solution: Event-aligned comparison**

For a crisis event at year $t_e$:
1. Find $PSI(t_e)$ using the 50-100 year window containing $t_e$
2. Find $SPI(t_e)$ using the 1-10 year window centered on $t_e$
3. Classify the event using the quadrant at $(PSI(t_e), SPI(t_e))$

This is **not** a time-series overlay but an **event-centric snapshot**.

---

## 4. Domain-Specific Integration

### 4.1 Ancient Domains (Mesopotamia, China, Rome)

**Challenge**: SPI often has `INTERPOLATED` or `RULER` confidence.

**Integration rule**:
- If SPI confidence = `EXACT`: Use full 2D classifier
- If SPI confidence = `RULER`: Use PSI-primary, SPI-secondary (weight 0.7/0.3)
- If SPI confidence = `INTERPOLATED`: Use PSI-only for threshold alerts; SPI for exploratory analysis only
- If SPI confidence = `INSUFFICIENT`: PSI-only

### 4.2 Modern Domains (Financial, COVID-19, Political)

**Challenge**: SPI can be noisy at high frequency.

**Integration rule**:
- Use SPI-primary (weight 0.7/0.3) for real-time monitoring
- PSI provides long-term context (is this spike part of a gradual decline?)
- Require SPI confirmation for 2+ consecutive windows before elevating alert

### 4.3 Cross-Domain UPSI

For the global UPSI (across all 7+ domains):

$$UPSI_{global}(t) = \frac{1}{N} \sum_{d=1}^{N} UPSI_{v2}^{(d)}(t) \cdot w_d$$

Where $w_d$ is domain reliability weight based on data quality.

---

## 5. Validation Framework

### 5.1 Testable Predictions

UPSI_v2 generates testable predictions that PSI alone cannot:

| Prediction | PSI-only | UPSI_v2 |
|------------|----------|---------|
| Gradual decline → collapse | Detects late | Detects early (SPI spike precedes PSI trough) |
| Sudden crisis in stable system | Misses | Detects (SPI spike in quadrant C) |
| False alarm (noise spike) | May misclassify | PSI filters noise |
| Recovery vs. collapse | Ambiguous | Quadrant transition pattern distinguishes |

### 5.2 Backtesting Protocol

1. **Historical event database**: 50+ known crises across 7 domains
2. **PSI-only baseline**: Compute classification accuracy
3. **UPSI_v2 test**: Compute classification accuracy with SPI
4. **Expected improvement**: +10-15% accuracy on burst crises; no degradation on gradual crises

### 5.3 Validation Ceiling

Even with UPSI_v2, the theoretical validation ceiling remains:
- **Ancient domains**: ~85-90% (data sparsity limit)
- **Modern domains**: ~95% (noise and non-crisis spikes)
- **Global composite**: ~90% (domain heterogeneity)

---

## 6. Implementation Roadmap

### Phase 1: SPI Core (v13b — current)
- ✅ SPI theoretical framework
- ✅ SPI computation engine
- ✅ Mesopotamian validation test
- ✅ PSI-SPI integration specification

### Phase 2: UPSI_v2 Prototype (v14)
- Implement 2D classifier with quadrant logic
- Build temporal resolution bridge
- Add confidence-weighted aggregation
- Cross-domain testing (China, Rome, modern)

### Phase 3: Real-Time Deployment (v15)
- Modern domain SPI (financial, COVID-19, political polling)
- Streaming SPI computation
- Alert dashboard with quadrant visualization
- Backtesting framework

### Phase 4: Theoretical Refinement (v16)
- Second-order SPI (jerk/curvature of collapse)
- Non-linear dynamics (bifurcation detection)
- Machine learning classifier replacing heuristic quadrants

---

## 7. Summary

UPSI_v2 represents a paradigm shift from **single-indicator** to **state-space** crisis detection:

- **PSI** = state (where is the system?)
- **SPI** = velocity (how fast is it changing?)
- **UPSI_v2** = phase portrait (what regime is the system in?)

The four quadrants provide actionable intelligence:
- 🟢 Stable: No action
- 🟡 Gradual Decline: Long-term monitoring
- 🟠 Sudden Crisis: Short-term preparation
- 🔴 Accelerating Collapse: Immediate response

This framework is theoretically sound, mathematically distinct from PSI, and addresses the v12 boundary condition that no single level-based indicator can capture burst crises.

---

*Integration specification version: v13b*  
*Based on v12 boundary conditions and v11a theoretical proposals*  
*Next milestone: v14 UPSI_v2 prototype implementation*
