#!/usr/bin/env python3
"""
v15b SPI (Sudden Pressure Indicator) Computation Engine — Financial Dashboard Edition
=====================================================================================

SPI is a velocity-based companion indicator to PSI (level-based).
- PSI = integral/smoothed level indicator (long windows)
- SPI = derivative/rate-of-change indicator (short windows)

For financial data:
- τ = 5 trading days (default)
- Velocity: V(t) = (price[t] - price[t-τ]) / τ
- Acceleration: A(t) = (V(t) - V[t-τ]) / τ
- Volatility spike: rolling std of velocity over 20 days
- ΔGSI replaced with cross-asset correlation breakdown (single-asset finance)

Key design principles:
1. Same raw data as PSI (OHLCV price DataFrames)
2. Rate-of-change based, not level-based
3. Spike detection (upper tail), not trough detection (lower tail)
4. Adaptive temporal resolution based on data density
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


# ============================================================
# Configuration
# ============================================================

# SPI default weights for financial data
SPI_WEIGHTS_FINANCE = {
    "velocity": 0.35,
    "acceleration": 0.25,
    "correlation_breakdown": 0.25,
    "volatility_spike": 0.15,
}

# Thresholds
SPI_THRESHOLD_ELEVATED = 1.5  # z-score
SPI_THRESHOLD_CRITICAL = 2.5  # z-score

# Quadrant thresholds
DEFAULT_PSI_HIGH_OFFSET = 0.5  # mean + 0.5 * std
DEFAULT_SPI_HIGH_OFFSET = 1.5  # mean + 1.5 * std

QUADRANT_NAMES = {
    (0, 0): "Stable",
    (0, 1): "Sudden Crisis",
    (1, 0): "Gradual Decline",
    (1, 1): "Accelerating Collapse",
}

QUADRANT_COLORS = {
    "Stable": "#2ecc71",
    "Gradual Decline": "#f1c40f",
    "Sudden Crisis": "#e67e22",
    "Accelerating Collapse": "#e74c3c",
}

QUADRANT_EMOJI = {
    "Stable": "🟢",
    "Gradual Decline": "🟡",
    "Sudden Crisis": "🟠",
    "Accelerating Collapse": "🔴",
}

ALERT_RULES = {
    ("Stable", "Gradual Decline"): ("Yellow alert (monitor)", "🟡"),
    ("Stable", "Sudden Crisis"): ("Orange alert (prepare)", "🟠"),
    ("Stable", "Accelerating Collapse"): ("Red alert (act now)", "🔴"),
    ("Gradual Decline", "Accelerating Collapse"): ("Red alert (escalation)", "🔴"),
    ("Gradual Decline", "Sudden Crisis"): ("Orange alert (unexpected shock)", "🟠"),
    ("Sudden Crisis", "Accelerating Collapse"): ("Red alert (deepening crisis)", "🔴"),
    ("Accelerating Collapse", "Stable"): ("Green (all clear - recovery)", "🟢"),
    ("Sudden Crisis", "Stable"): ("Green (all clear - resolved)", "🟢"),
    ("Gradual Decline", "Stable"): ("Green (all clear - stabilized)", "🟢"),
}


# ============================================================
# Data structures
# ============================================================

@dataclass
class SPIResult:
    """Container for SPI computation results for a single asset."""

    asset_name: str
    tau: int
    velocity: List[float] = field(default_factory=list)
    acceleration: List[float] = field(default_factory=list)
    volatility: List[float] = field(default_factory=list)
    correlation_breakdown: List[float] = field(default_factory=list)
    spi_series: List[float] = field(default_factory=list)
    alert_levels: List[str] = field(default_factory=list)
    time_labels: List[str] = field(default_factory=list)

    def current_spi(self) -> float:
        return self.spi_series[-1] if self.spi_series else 0.0

    def current_alert(self) -> str:
        return self.alert_levels[-1] if self.alert_levels else "NORMAL"


@dataclass
class QuadrantResult:
    """Container for quadrant classification results."""

    asset_name: str
    psi_series: List[float]
    spi_series: List[float]
    time_labels: List[str]
    psi_high: float
    spi_high: float
    quadrants: List[str]
    quadrant_codes: List[Tuple[int, int]]
    alerts: List[Dict] = field(default_factory=list)

    def current_quadrant(self) -> str:
        return self.quadrants[-1] if self.quadrants else "Stable"

    def summary(self) -> Dict:
        return {
            "asset": self.asset_name,
            "current_quadrant": self.current_quadrant(),
            "psi_high_threshold": round(self.psi_high, 3),
            "spi_high_threshold": round(self.spi_high, 3),
            "quadrant_distribution": {
                q: sum(1 for qq in self.quadrants if qq == q) for q in set(self.quadrants)
            },
            "n_alerts": len(self.alerts),
            "alerts": self.alerts,
        }


# ============================================================
# SPI Core Functions
# ============================================================

class SPIEngine:
    """Compute SPI (Sudden Pressure Indicator) for financial asset price data."""

    def __init__(
        self,
        tau: int = 5,
        vol_window: int = 20,
        weights: Optional[Dict[str, float]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.tau = tau
        self.vol_window = vol_window
        self.weights = weights or SPI_WEIGHTS_FINANCE
        self.log = logger or logging.getLogger("spi_engine")

    # ------------------------------------------------------------------
    # Component computations
    # ------------------------------------------------------------------

    def compute_velocity(self, prices: List[float]) -> List[float]:
        """
        Compute first derivative (velocity) of price.
        V(t) = (price[t] - price[t-τ]) / τ
        """
        if len(prices) < self.tau + 1:
            self.log.warning("Insufficient data for velocity: %d < %d", len(prices), self.tau + 1)
            return []
        velocity = []
        for i in range(self.tau, len(prices)):
            v = (prices[i] - prices[i - self.tau]) / self.tau
            velocity.append(v)
        return velocity

    def compute_acceleration(self, velocity: List[float]) -> List[float]:
        """
        Compute second derivative (acceleration).
        A(t) = (V(t) - V(t-τ)) / τ
        """
        if len(velocity) < self.tau + 1:
            self.log.warning("Insufficient data for acceleration: %d < %d", len(velocity), self.tau + 1)
            return []
        acceleration = []
        for i in range(self.tau, len(velocity)):
            a = (velocity[i] - velocity[i - self.tau]) / self.tau
            acceleration.append(a)
        return acceleration

    def compute_volatility(self, velocity: List[float]) -> List[float]:
        """
        Compute rolling volatility (std) of velocity over vol_window days.
        sigma_V(t) = std(V[t-vol_window+1], ..., V[t])
        """
        if len(velocity) < self.vol_window:
            self.log.warning("Insufficient data for volatility: %d < %d", len(velocity), self.vol_window)
            return []
        volatility = []
        for i in range(self.vol_window - 1, len(velocity)):
            window = velocity[i - self.vol_window + 1 : i + 1]
            try:
                std_v = statistics.stdev(window)
            except statistics.StatisticsError:
                std_v = 0.0
            volatility.append(std_v)
        return volatility

    def compute_correlation_breakdown(
        self,
        prices: List[float],
        all_prices: Optional[Dict[str, List[float]]] = None,
        asset_name: Optional[str] = None,
    ) -> List[float]:
        """
        Compute cross-asset correlation breakdown as proxy for ΔGSI.

        In single-asset finance data, geographic velocity (ΔGSI) is not applicable.
        We use the deviation from average cross-asset correlation as a proxy:
        - High breakdown = asset decouples from market (crisis signal)
        - Returns absolute deviation from mean correlation
        """
        if all_prices is None or asset_name is None or len(all_prices) < 2:
            # Fallback: use price autocorrelation breakdown
            return self._compute_autocorrelation_breakdown(prices)

        # Align all price series to same length
        min_len = min(len(p) for p in all_prices.values())
        if min_len < self.tau + 1:
            return self._compute_autocorrelation_breakdown(prices)

        # Compute returns for all assets
        returns_dict = {}
        for name, p in all_prices.items():
            aligned = p[-min_len:]
            rets = [aligned[i] / aligned[i - 1] - 1 for i in range(1, len(aligned))]
            returns_dict[name] = rets

        if len(returns_dict) < 2:
            return self._compute_autocorrelation_breakdown(prices)

        # Compute rolling correlation breakdown for target asset
        target_rets = returns_dict.get(asset_name, [])
        if not target_rets:
            return self._compute_autocorrelation_breakdown(prices)

        breakdown = []
        corr_window = min(20, len(target_rets) // 4)
        if corr_window < 5:
            corr_window = 5

        for i in range(corr_window - 1, len(target_rets)):
            # Compute correlations with all other assets in this window
            correlations = []
            for other_name, other_rets in returns_dict.items():
                if other_name == asset_name:
                    continue
                if len(other_rets) < i + 1:
                    continue
                target_window = target_rets[i - corr_window + 1 : i + 1]
                other_window = other_rets[i - corr_window + 1 : i + 1]
                if len(target_window) != len(other_window):
                    continue
                corr = self._pearson_correlation(target_window, other_window)
                correlations.append(corr)

            if not correlations:
                breakdown.append(0.0)
                continue

            # Breakdown = how much this asset deviates from average correlation
            mean_corr = sum(correlations) / len(correlations)
            # In crisis, correlations spike (flight to safety) or collapse (decoupling)
            # We use absolute deviation as the signal
            breakdown.append(abs(mean_corr))

        return breakdown

    def _compute_autocorrelation_breakdown(self, prices: List[float]) -> List[float]:
        """Fallback: use rolling autocorrelation breakdown of price returns."""
        if len(prices) < self.tau + 2:
            return []
        rets = [prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))]
        breakdown = []
        window = min(20, len(rets) // 4)
        if window < 5:
            window = 5
        for i in range(window - 1, len(rets)):
            current_rets = rets[i - window + 1 : i + 1]
            # Autocorrelation lag-1
            if len(current_rets) < 2:
                breakdown.append(0.0)
                continue
            lag0 = current_rets[1:]
            lag1 = current_rets[:-1]
            corr = self._pearson_correlation(lag0, lag1)
            breakdown.append(abs(corr))
        return breakdown

    @staticmethod
    def _pearson_correlation(x: List[float], y: List[float]) -> float:
        """Compute Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        var_x = sum((xi - mean_x) ** 2 for xi in x) / n
        var_y = sum((yi - mean_y) ** 2 for yi in y) / n
        if var_x == 0 or var_y == 0:
            return 0.0
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        return cov / (math.sqrt(var_x) * math.sqrt(var_y))

    # ------------------------------------------------------------------
    # SPI aggregation
    # ------------------------------------------------------------------

    def compute_spi(
        self,
        prices: List[float],
        all_prices: Optional[Dict[str, List[float]]] = None,
        asset_name: Optional[str] = None,
    ) -> SPIResult:
        """
        Compute full SPI series for a single asset.

        Returns SPIResult with velocity, acceleration, volatility, correlation_breakdown, spi_series.
        """
        if len(prices) < self.tau + self.vol_window + 1:
            self.log.warning(
                "Insufficient data for SPI computation: %d < %d",
                len(prices),
                self.tau + self.vol_window + 1,
            )
            return SPIResult(asset_name=asset_name or "unknown", tau=self.tau)

        # 1. Velocity
        velocity = self.compute_velocity(prices)
        if not velocity:
            return SPIResult(asset_name=asset_name or "unknown", tau=self.tau)

        # 2. Acceleration
        acceleration = self.compute_acceleration(velocity)
        if not acceleration:
            return SPIResult(asset_name=asset_name or "unknown", tau=self.tau)

        # 3. Volatility
        volatility = self.compute_volatility(velocity)
        if not volatility:
            return SPIResult(asset_name=asset_name or "unknown", tau=self.tau)

        # 4. Correlation breakdown (proxy for ΔGSI)
        corr_breakdown = self.compute_correlation_breakdown(prices, all_prices, asset_name)
        if not corr_breakdown:
            corr_breakdown = [0.0] * len(volatility)

        # Align all series to same length (shortest)
        min_len = min(len(velocity), len(acceleration), len(volatility), len(corr_breakdown))
        velocity = velocity[-min_len:]
        acceleration = acceleration[-min_len:]
        volatility = volatility[-min_len:]
        corr_breakdown = corr_breakdown[-min_len:]

        # 5. Z-score each component
        z_vel = self._zscore(velocity)
        z_acc = self._zscore(acceleration)
        z_vol = self._zscore(volatility)
        z_corr = self._zscore(corr_breakdown)

        # 6. Aggregate SPI
        spi_series = []
        alert_levels = []
        for i in range(min_len):
            spi = (
                self.weights["velocity"] * abs(z_vel[i])
                + self.weights["acceleration"] * abs(z_acc[i])
                + self.weights["correlation_breakdown"] * abs(z_corr[i])
                + self.weights["volatility_spike"] * z_vol[i]
            )
            spi_series.append(spi)

            if spi > SPI_THRESHOLD_CRITICAL:
                alert_levels.append("CRITICAL")
            elif spi > SPI_THRESHOLD_ELEVATED:
                alert_levels.append("ELEVATED")
            else:
                alert_levels.append("NORMAL")

        return SPIResult(
            asset_name=asset_name or "unknown",
            tau=self.tau,
            velocity=velocity,
            acceleration=acceleration,
            volatility=volatility,
            correlation_breakdown=corr_breakdown,
            spi_series=spi_series,
            alert_levels=alert_levels,
        )

    @staticmethod
    def _zscore(values: List[float]) -> List[float]:
        """Compute z-scores for a list of values."""
        if not values:
            return []
        mean_v = sum(values) / len(values)
        try:
            std_v = statistics.stdev(values)
        except statistics.StatisticsError:
            std_v = 1e-6
        if std_v == 0:
            std_v = 1e-6
        return [(v - mean_v) / std_v for v in values]

    # ------------------------------------------------------------------
    # Quadrant classification
    # ------------------------------------------------------------------

    def classify_quadrant(
        self,
        psi_series: List[float],
        spi_series: List[float],
        asset_name: str = "unknown",
        time_labels: Optional[List[str]] = None,
        psi_high_offset: float = DEFAULT_PSI_HIGH_OFFSET,
        spi_high_offset: float = DEFAULT_SPI_HIGH_OFFSET,
    ) -> QuadrantResult:
        """
        Classify each time point into one of 4 UPSI_v2 quadrants.

        Quadrants:
        - Stable: PSI low, SPI low
        - Gradual Decline: PSI high, SPI low
        - Sudden Crisis: PSI low, SPI high
        - Accelerating Collapse: PSI high, SPI high
        """
        if len(psi_series) != len(spi_series):
            raise ValueError("psi_series and spi_series must have the same length")
        if not psi_series:
            raise ValueError("Input series must not be empty")

        n = len(psi_series)
        time_labels = time_labels if time_labels is not None else [str(i) for i in range(n)]
        if len(time_labels) != n:
            raise ValueError("time_labels length must match psi/spi length")

        # Thresholds
        psi_mean = sum(psi_series) / n
        spi_mean = sum(spi_series) / n
        try:
            psi_std = statistics.stdev(psi_series)
        except statistics.StatisticsError:
            psi_std = 1e-6
        try:
            spi_std = statistics.stdev(spi_series)
        except statistics.StatisticsError:
            spi_std = 1e-6

        psi_high = psi_mean + psi_high_offset * psi_std
        spi_high = spi_mean + spi_high_offset * spi_std

        # Quadrant assignment
        quadrants = []
        codes = []
        for i in range(n):
            p_flag = 1 if psi_series[i] > psi_high else 0
            s_flag = 1 if spi_series[i] > spi_high else 0
            codes.append((p_flag, s_flag))
            quadrants.append(QUADRANT_NAMES[(p_flag, s_flag)])

        # Alert detection
        alerts = []
        for i in range(1, n):
            prev_q = quadrants[i - 1]
            curr_q = quadrants[i]
            if prev_q == curr_q:
                continue
            key = (prev_q, curr_q)
            if key in ALERT_RULES:
                msg, emoji = ALERT_RULES[key]
                alerts.append(
                    {
                        "time_idx": i,
                        "time_label": time_labels[i],
                        "from_quadrant": prev_q,
                        "to_quadrant": curr_q,
                        "message": msg,
                        "emoji": emoji,
                    }
                )

        return QuadrantResult(
            asset_name=asset_name,
            psi_series=psi_series,
            spi_series=spi_series,
            time_labels=time_labels,
            psi_high=psi_high,
            spi_high=spi_high,
            quadrants=quadrants,
            quadrant_codes=codes,
            alerts=alerts,
        )

    def compute_all(
        self,
        asset_data: Dict[str, List[float]],
        asset_psi: Dict[str, List[float]],
    ) -> Tuple[Dict[str, SPIResult], Dict[str, QuadrantResult]]:
        """
        Compute SPI and quadrant classification for all assets.

        Returns:
            (spi_results, quadrant_results)
        """
        spi_results = {}
        quadrant_results = {}

        for name, prices in asset_data.items():
            psi = asset_psi.get(name, [])
            if not psi:
                self.log.warning("No PSI data for %s, skipping SPI", name)
                continue

            # Compute SPI
            spi_result = self.compute_spi(prices, all_prices=asset_data, asset_name=name)
            spi_results[name] = spi_result

            # Align PSI and SPI to same length for quadrant classification
            min_len = min(len(psi), len(spi_result.spi_series))
            if min_len < 2:
                self.log.warning("Insufficient aligned data for quadrant: %s", name)
                continue

            aligned_psi = psi[-min_len:]
            aligned_spi = spi_result.spi_series[-min_len:]

            # Generate time labels
            time_labels = [f"T-{min_len - i - 1}" for i in range(min_len)]

            # Classify quadrant
            quadrant_result = self.classify_quadrant(
                aligned_psi,
                aligned_spi,
                asset_name=name,
                time_labels=time_labels,
            )
            quadrant_results[name] = quadrant_result

        return spi_results, quadrant_results


# ============================================================
# Convenience functions
# ============================================================

def compute_spi_single(
    prices: List[float],
    tau: int = 5,
    vol_window: int = 20,
    asset_name: str = "unknown",
    all_prices: Optional[Dict[str, List[float]]] = None,
) -> SPIResult:
    """One-shot SPI computation for a single asset."""
    engine = SPIEngine(tau=tau, vol_window=vol_window)
    return engine.compute_spi(prices, all_prices=all_prices, asset_name=asset_name)


def classify_quadrant_single(
    psi_series: List[float],
    spi_series: List[float],
    asset_name: str = "unknown",
    time_labels: Optional[List[str]] = None,
    psi_high_offset: float = DEFAULT_PSI_HIGH_OFFSET,
    spi_high_offset: float = DEFAULT_SPI_HIGH_OFFSET,
) -> QuadrantResult:
    """One-shot quadrant classification."""
    engine = SPIEngine()
    return engine.classify_quadrant(
        psi_series,
        spi_series,
        asset_name=asset_name,
        time_labels=time_labels,
        psi_high_offset=psi_high_offset,
        spi_high_offset=spi_high_offset,
    )


if __name__ == "__main__":
    print("SPI Computation Engine v15b — Financial Dashboard Edition")
    print("Import this module and call SPIEngine.compute_spi() or SPIEngine.compute_all()")
