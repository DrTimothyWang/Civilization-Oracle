# S19. SPI Computation and Mesopotamian Validation

**Source**: `v13_迭代研究/02_spi_burst/v13b_spi_formula.py`, `v13_迭代研究/02_spi_burst/v13b_spi_meso_test.py`  
**Status**: Source materials available  
**Assembly**: Document SPI formula, adaptive τ, spike detection, 8/8 combined validation

---

## Content Outline

1. **SPI formula**
   - SPI(t) = 0.35 × z(Velocity) + 0.25 × z(Acceleration) + 0.25 × |ΔGSI| + 0.15 × Volatility_Spike
   - Mathematically dual to PSI: PSI = ∫ f(t) dt (low-pass), SPI = df/dt (high-pass)

2. **Computation steps**
   - Short-window aggregation: C_d(t, τ) = Σ w_genre(i) · 1_domain(i)
   - Velocity: V_d(t, τ) = [C_d(t, τ) − C_d(t−τ, τ)] / τ
   - Acceleration: A_d(t, τ) = [V_d(t, τ) − V_d(t−τ, τ)] / τ
   - Geographic velocity: ΔGSI_z(t, τ) = z-score([GSI(t, τ) − GSI(t−τ, τ)] / τ)
   - Volatility spike: σ_V(t, k) = sqrt(1/k Σ (V_d(t−jτ) − V̄)²)

3. **Adaptive window size**
   - τ_adaptive = max(1, ceil(N_period / (N_exact / 100)))
   - Ancient default: τ = 5 years
   - Modern default: τ = 1 year

4. **Alert thresholds**
   - CRITICAL: SPI > μ + 2.5σ
   - ELEVATED: μ + 1.5σ < SPI ≤ μ + 2.5σ
   - NORMAL: otherwise

5. **Mesopotamian validation (8/8 combined)**
   - PSI alone: 6/8 (75%)
   - SPI alone: captures Umma decline (−2037) and Hammurabi fragmentation (−1750)
   - Combined PSI+SPI: 8/8 (100%)

6. **Confidence flags**
   - INTERPOLATED: <10% exact-year records (manual review required)
   - INSUFFICIENT: <100 records (SPI not computed)

---

## Source Files to Consult

- `/Users/wangzr/Desktop/历史事件预测建模/v13_迭代研究/02_spi_burst/v13b_spi_formula.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v13_迭代研究/02_spi_burst/v13b_spi_meso_test.py`
- `/Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/02_spi_cross_domain/v14b_spi_cross_domain.py`

---

*Placeholder for SI Section 19. Assemble from source materials before submission.*
