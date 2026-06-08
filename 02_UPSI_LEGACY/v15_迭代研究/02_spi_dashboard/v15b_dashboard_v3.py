#!/usr/bin/env python3
"""
v15b Dashboard v3 — SPI-Enhanced UPSI Dashboard
================================================

Integrates SPI (Sudden Pressure Indicator) into the v14d dashboard architecture:
- Computes PSI + SPI + quadrant for each asset
- Generates enhanced HTML with quadrant visualization
- Alert rules based on quadrant transitions

Architecture:
  DataFetcher → PSIEngine → SPIEngine → AlertSystem → Renderer

Usage:
    python v15b_dashboard_v3.py --mode=once
    python v15b_dashboard_v3.py --mode=daemon
    python v15b_dashboard_v3.py --output-dir=./output
"""

import argparse
import json
import logging
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================
# Config
# ============================================================

@dataclass
class DashboardConfig:
    """Runtime configuration."""
    assets: Dict[str, str] = field(default_factory=lambda: {
        "US.SP500": "^GSPC",
        "JP.N225": "^N225",
        "UK.FTSE": "^FTSE",
        "DE.DAX": "^GDAXI",
        "HK.HSI": "^HSI",
        "BR.BVSP": "^BVSP",
        "AU.ASX": "^AXJO",
        "FR.CAC": "^FCHI",
        "IN.NIFTY": "^NSEI",
        "GOLD": "GC=F",
        "OIL.WTI": "CL=F",
        "VIX": "^VIX",
    })
    history_days: int = 252
    alert_threshold_upsi: float = -0.5
    alert_threshold_asset: float = -0.5
    alert_assets_count_critical: int = 5
    output_dir: str = "."
    output_html: str = "v15b_dashboard_v3.html"
    output_json: str = "v15b_dashboard_data.json"
    log_level: str = "INFO"
    daemon_interval_hours: float = 4.0
    max_retries_yf: int = 3
    retry_delay_seconds: float = 2.0
    webhook_url: Optional[str] = None
    simulated_data_bias: float = -0.0002
    simulated_data_volatility: float = 0.012
    spi_tau: int = 5
    spi_vol_window: int = 20
    psi_high_offset: float = 0.5
    spi_high_offset: float = 1.5


# ============================================================
# Logging
# ============================================================

def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("upsi_dashboard_v15b")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


# ============================================================
# DataFetcher
# ============================================================

class DataFetcher:
    """Pull asset data from yfinance with graceful fallback to simulated data."""

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger
        self._yf = None

    def _get_yf(self):
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
            except ImportError:
                self.log.error("yfinance not installed. Install: pip install yfinance")
                raise
        return self._yf

    def fetch_single(self, name: str, ticker: str) -> Tuple[Optional[List[float]], bool]:
        yf = self._get_yf()
        end = datetime.now()
        start = end - timedelta(days=int(self.cfg.history_days * 1.5))

        for attempt in range(1, self.cfg.max_retries_yf + 1):
            try:
                df = yf.download(
                    ticker,
                    start=start.strftime("%Y-%m-%d"),
                    end=end.strftime("%Y-%m-%d"),
                    progress=False,
                    auto_adjust=False,
                )
                if df is None or df.empty:
                    raise ValueError("Empty dataframe returned")

                try:
                    import pandas as pd
                    if isinstance(df.columns, pd.MultiIndex):
                        prices = df["Close"][ticker].dropna().tolist()
                    else:
                        prices = df["Close"].dropna().tolist()
                except Exception:
                    prices = df["Close"].dropna().tolist()

                if len(prices) >= 60:
                    trimmed = prices[-self.cfg.history_days:]
                    self.log.info("  ✅ %s: %d days (real)", name, len(trimmed))
                    return trimmed, True
                else:
                    raise ValueError(f"Only {len(prices)} days available (< 60)")

            except Exception as e:
                self.log.warning("  ⚠️ %s attempt %d/%d: %s", name, attempt, self.cfg.max_retries_yf, e)
                if attempt < self.cfg.max_retries_yf:
                    time.sleep(self.cfg.retry_delay_seconds)
                else:
                    break

        # Fallback: simulated data
        simulated = self._generate_simulated(name)
        self.log.warning("  ⚠️ %s: fallback to simulated data (%d days)", name, len(simulated))
        return simulated, False

    def _generate_simulated(self, name: str) -> List[float]:
        random.seed(hash(name) % 2**31)
        p = 100.0
        prices = []
        for _ in range(self.cfg.history_days):
            p *= (1 + random.gauss(self.cfg.simulated_data_bias, self.cfg.simulated_data_volatility))
            prices.append(p)
        return prices

    def fetch_all(self) -> Tuple[Dict[str, List[float]], Dict[str, bool]]:
        self.log.info("[DataFetcher] Pulling %d assets from yfinance...", len(self.cfg.assets))
        data: Dict[str, List[float]] = {}
        real_flags: Dict[str, bool] = {}
        for name, ticker in self.cfg.assets.items():
            prices, is_real = self.fetch_single(name, ticker)
            if prices is not None:
                data[name] = prices
                real_flags[name] = is_real
        return data, real_flags


# ============================================================
# PSIEngine
# ============================================================

class PSIEngine:
    """Compute PSI three dimensions and UPSI."""

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger

    @staticmethod
    def returns(prices: List[float]) -> List[float]:
        return [prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))]

    @staticmethod
    def rolling_mmp(prices: List[float], w: int = 60) -> List[float]:
        out = []
        for i in range(w, len(prices)):
            recent_max = max(prices[i - w:i + 1])
            out.append(prices[i] / recent_max - 1)
        return out

    @staticmethod
    def rolling_vol(returns_series: List[float], w: int = 20) -> List[float]:
        out = []
        for i in range(w, len(returns_series)):
            out.append(statistics.stdev(returns_series[i - w:i]) * (252 ** 0.5))
        return out

    @staticmethod
    def rolling_disengagement(prices: List[float], w: int = 20) -> List[float]:
        out = []
        for i in range(w + 5, len(prices)):
            mom_short = prices[i] / prices[i - 5] - 1
            mom_long = prices[i] / prices[i - w] - 1
            out.append(mom_short - mom_long)
        return out

    def compute_psi(self, prices: List[float]) -> Tuple[List[float], List[float], List[float], List[float]]:
        rets = self.returns(prices)
        mmp = self.rolling_mmp(prices, 60)
        sfd = self.rolling_vol(rets, 20)
        eed = self.rolling_disengagement(prices, 20)

        L = min(len(mmp), len(sfd), len(eed))
        if L <= 0:
            return [], [], [], []

        mmp = mmp[-L:]
        sfd = sfd[-L:]
        eed = eed[-L:]

        def zscore(x: List[float]) -> List[float]:
            mu = statistics.mean(x)
            sd = statistics.stdev(x) if statistics.stdev(x) > 0 else 1e-6
            return [(v - mu) / sd for v in x]

        mmp_z = zscore(mmp)
        sfd_z = zscore(sfd)
        eed_z = zscore(eed)

        psi = [0.4 * m + 0.3 * s + 0.3 * e for m, s, e in zip(mmp_z, sfd_z, eed_z)]
        return psi, mmp_z, sfd_z, eed_z

    def compute_upsi(self, asset_psi: Dict[str, List[float]]) -> List[float]:
        valid = {k: v for k, v in asset_psi.items() if v}
        if not valid:
            self.log.error("No valid PSI series to compute UPSI")
            return []
        min_len = min(len(p) for p in valid.values())
        upsi = []
        for i in range(-min_len, 0):
            vals = [valid[name][i] for name in valid]
            upsi.append(statistics.mean(vals))
        return upsi


# ============================================================
# SPIEngine
# ============================================================

class SPIEngine:
    """Compute SPI (Sudden Pressure Indicator) for financial asset price data."""

    SPI_WEIGHTS_FINANCE = {
        "velocity": 0.35,
        "acceleration": 0.25,
        "correlation_breakdown": 0.25,
        "volatility_spike": 0.15,
    }

    SPI_THRESHOLD_ELEVATED = 1.5
    SPI_THRESHOLD_CRITICAL = 2.5

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

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger
        self.tau = config.spi_tau
        self.vol_window = config.spi_vol_window

    def compute_velocity(self, prices: List[float]) -> List[float]:
        if len(prices) < self.tau + 1:
            return []
        return [(prices[i] - prices[i - self.tau]) / self.tau for i in range(self.tau, len(prices))]

    def compute_acceleration(self, velocity: List[float]) -> List[float]:
        if len(velocity) < self.tau + 1:
            return []
        return [(velocity[i] - velocity[i - self.tau]) / self.tau for i in range(self.tau, len(velocity))]

    def compute_volatility(self, velocity: List[float]) -> List[float]:
        if len(velocity) < self.vol_window:
            return []
        out = []
        for i in range(self.vol_window - 1, len(velocity)):
            window = velocity[i - self.vol_window + 1:i + 1]
            try:
                std_v = statistics.stdev(window)
            except statistics.StatisticsError:
                std_v = 0.0
            out.append(std_v)
        return out

    def compute_correlation_breakdown(self, prices: List[float], all_prices: Dict[str, List[float]], asset_name: str) -> List[float]:
        if len(all_prices) < 2:
            return self._compute_autocorrelation_breakdown(prices)
        min_len = min(len(p) for p in all_prices.values())
        if min_len < self.tau + 1:
            return self._compute_autocorrelation_breakdown(prices)

        returns_dict = {}
        for name, p in all_prices.items():
            aligned = p[-min_len:]
            rets = [aligned[i] / aligned[i - 1] - 1 for i in range(1, len(aligned))]
            returns_dict[name] = rets

        target_rets = returns_dict.get(asset_name, [])
        if not target_rets:
            return self._compute_autocorrelation_breakdown(prices)

        breakdown = []
        corr_window = min(20, len(target_rets) // 4)
        if corr_window < 5:
            corr_window = 5

        for i in range(corr_window - 1, len(target_rets)):
            correlations = []
            for other_name, other_rets in returns_dict.items():
                if other_name == asset_name:
                    continue
                if len(other_rets) < i + 1:
                    continue
                target_window = target_rets[i - corr_window + 1:i + 1]
                other_window = other_rets[i - corr_window + 1:i + 1]
                if len(target_window) != len(other_window):
                    continue
                corr = self._pearson_correlation(target_window, other_window)
                correlations.append(corr)

            if not correlations:
                breakdown.append(0.0)
                continue
            mean_corr = sum(correlations) / len(correlations)
            breakdown.append(abs(mean_corr))

        return breakdown

    def _compute_autocorrelation_breakdown(self, prices: List[float]) -> List[float]:
        if len(prices) < self.tau + 2:
            return []
        rets = [prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))]
        breakdown = []
        window = min(20, len(rets) // 4)
        if window < 5:
            window = 5
        for i in range(window - 1, len(rets)):
            current_rets = rets[i - window + 1:i + 1]
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
        return cov / (var_x ** 0.5 * var_y ** 0.5)

    @staticmethod
    def _zscore(values: List[float]) -> List[float]:
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

    def compute_spi(self, prices: List[float], all_prices: Dict[str, List[float]], asset_name: str) -> List[float]:
        if len(prices) < self.tau + self.vol_window + 1:
            self.log.warning("Insufficient data for SPI: %s (%d days)", asset_name, len(prices))
            return []

        velocity = self.compute_velocity(prices)
        if not velocity:
            return []
        acceleration = self.compute_acceleration(velocity)
        if not acceleration:
            return []
        volatility = self.compute_volatility(velocity)
        if not volatility:
            return []
        corr_breakdown = self.compute_correlation_breakdown(prices, all_prices, asset_name)
        if not corr_breakdown:
            corr_breakdown = [0.0] * len(volatility)

        min_len = min(len(velocity), len(acceleration), len(volatility), len(corr_breakdown))
        velocity = velocity[-min_len:]
        acceleration = acceleration[-min_len:]
        volatility = volatility[-min_len:]
        corr_breakdown = corr_breakdown[-min_len:]

        z_vel = self._zscore(velocity)
        z_acc = self._zscore(acceleration)
        z_vol = self._zscore(volatility)
        z_corr = self._zscore(corr_breakdown)

        spi_series = []
        for i in range(min_len):
            spi = (
                self.SPI_WEIGHTS_FINANCE["velocity"] * abs(z_vel[i])
                + self.SPI_WEIGHTS_FINANCE["acceleration"] * abs(z_acc[i])
                + self.SPI_WEIGHTS_FINANCE["correlation_breakdown"] * abs(z_corr[i])
                + self.SPI_WEIGHTS_FINANCE["volatility_spike"] * z_vol[i]
            )
            spi_series.append(spi)

        return spi_series

    def classify_quadrant(
        self,
        psi_series: List[float],
        spi_series: List[float],
        asset_name: str,
        time_labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if len(psi_series) != len(spi_series) or not psi_series:
            return {"asset": asset_name, "quadrants": [], "alerts": []}

        n = len(psi_series)
        time_labels = time_labels or [str(i) for i in range(n)]

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

        psi_high = psi_mean + self.cfg.psi_high_offset * psi_std
        spi_high = spi_mean + self.cfg.spi_high_offset * spi_std

        quadrants = []
        codes = []
        for i in range(n):
            p_flag = 1 if psi_series[i] > psi_high else 0
            s_flag = 1 if spi_series[i] > spi_high else 0
            codes.append((p_flag, s_flag))
            quadrants.append(self.QUADRANT_NAMES[(p_flag, s_flag)])

        alerts = []
        for i in range(1, n):
            prev_q = quadrants[i - 1]
            curr_q = quadrants[i]
            if prev_q == curr_q:
                continue
            key = (prev_q, curr_q)
            if key in self.ALERT_RULES:
                msg, emoji = self.ALERT_RULES[key]
                alerts.append({
                    "time_idx": i,
                    "time_label": time_labels[i],
                    "from_quadrant": prev_q,
                    "to_quadrant": curr_q,
                    "message": msg,
                    "emoji": emoji,
                })

        return {
            "asset": asset_name,
            "current_quadrant": quadrants[-1] if quadrants else "Stable",
            "psi_high_threshold": round(psi_high, 3),
            "spi_high_threshold": round(spi_high, 3),
            "quadrants": quadrants,
            "quadrant_codes": codes,
            "n_alerts": len(alerts),
            "alerts": alerts,
            "quadrant_distribution": {
                q: sum(1 for qq in quadrants if qq == q) for q in set(quadrants)
            },
        }

    def compute_all(self, asset_data: Dict[str, List[float]], asset_psi: Dict[str, List[float]]) -> Tuple[Dict[str, List[float]], Dict[str, Dict[str, Any]]]:
        spi_results = {}
        quadrant_results = {}

        for name, prices in asset_data.items():
            psi = asset_psi.get(name, [])
            if not psi:
                self.log.warning("No PSI data for %s, skipping SPI", name)
                continue

            spi_series = self.compute_spi(prices, all_prices=asset_data, asset_name=name)
            if not spi_series:
                continue
            spi_results[name] = spi_series

            min_len = min(len(psi), len(spi_series))
            if min_len < 2:
                continue

            aligned_psi = psi[-min_len:]
            aligned_spi = spi_series[-min_len:]
            time_labels = [f"T-{min_len - i - 1}" for i in range(min_len)]

            quadrant_result = self.classify_quadrant(
                aligned_psi, aligned_spi, asset_name=name, time_labels=time_labels
            )
            quadrant_results[name] = quadrant_result

        return spi_results, quadrant_results


# ============================================================
# AlertSystem
# ============================================================

class AlertSystem:
    """Detect alerts based on thresholds, quadrant transitions, and output structured alert info."""

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger

    def check(
        self,
        current_upsi: float,
        current_psi: Dict[str, float],
        current_spi: Dict[str, float],
        quadrant_results: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        alerts: List[str] = []
        level = "OK"

        # Asset-level PSI alerts (trough detection)
        alert_assets_psi = [(n, v) for n, v in current_psi.items() if v < self.cfg.alert_threshold_asset]
        alert_assets_psi.sort(key=lambda x: x[1])

        # Asset-level SPI alerts (spike detection)
        alert_assets_spi = [(n, v) for n, v in current_spi.items() if v > self.cfg.spi_high_offset]
        alert_assets_spi.sort(key=lambda x: x[1], reverse=True)

        # UPSI level check
        if current_upsi < self.cfg.alert_threshold_upsi:
            level = "CRITICAL"
            alerts.append(f"UPSI {current_upsi:+.2f} below threshold {self.cfg.alert_threshold_upsi}")
        elif current_upsi < 0:
            level = "WARNING"
            alerts.append(f"UPSI {current_upsi:+.2f} in watch zone")

        # PSI asset count check
        if len(alert_assets_psi) >= self.cfg.alert_assets_count_critical:
            level = "CRITICAL"
            alerts.append(f"{len(alert_assets_psi)} assets in PSI alert state")
        elif alert_assets_psi:
            if level == "OK":
                level = "WARNING"
            alerts.append(f"{len(alert_assets_psi)} assets in PSI alert state")

        # SPI spike check
        if alert_assets_spi:
            if level == "OK":
                level = "WARNING"
            alerts.append(f"{len(alert_assets_spi)} assets in SPI elevated state")

        # Quadrant transition alerts
        quadrant_alerts = []
        for name, qresult in quadrant_results.items():
            for alert in qresult.get("alerts", []):
                if alert["time_idx"] == len(qresult.get("quadrants", [])) - 1:  # Most recent
                    quadrant_alerts.append({
                        "asset": name,
                        "from": alert["from_quadrant"],
                        "to": alert["to_quadrant"],
                        "message": alert["message"],
                        "emoji": alert["emoji"],
                    })

        if quadrant_alerts:
            if level == "OK":
                level = "WARNING"
            alerts.append(f"{len(quadrant_alerts)} quadrant transitions detected")

        result = {
            "level": level,
            "upsi": current_upsi,
            "alert_assets_psi": alert_assets_psi,
            "alert_assets_spi": alert_assets_spi,
            "quadrant_transitions": quadrant_alerts,
            "messages": alerts,
            "timestamp": datetime.now().isoformat(),
        }
        self.log.info("[AlertSystem] Level=%s, PSI alerts=%d, SPI alerts=%d, Quadrant transitions=%d",
                      level, len(alert_assets_psi), len(alert_assets_spi), len(quadrant_alerts))
        return result

    def send_webhook(self, alert: Dict[str, Any]) -> bool:
        if not self.cfg.webhook_url:
            return False
        try:
            import urllib.request
            import urllib.error
            payload = json.dumps(alert, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                self.cfg.webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.log.info("Webhook sent, status=%d", resp.status)
                return True
        except Exception as e:
            self.log.error("Webhook failed: %s", e)
            return False


# ============================================================
# Renderer
# ============================================================

class Renderer:
    """Generate enhanced HTML Dashboard and JSON API output with SPI + Quadrants."""

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger

    def render_json(
        self,
        asset_data: Dict[str, List[float]],
        asset_psi: Dict[str, List[float]],
        asset_spi: Dict[str, List[float]],
        upsi_series: List[float],
        real_flags: Dict[str, bool],
        alert: Dict[str, Any],
        quadrant_results: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_upsi = upsi_series[-1] if upsi_series else 0.0
        current_psi = {name: (psi[-1] if psi else 0.0) for name, psi in asset_psi.items()}
        current_spi = {name: (spi[-1] if spi else 0.0) for name, spi in asset_spi.items()}
        current_quadrants = {name: q.get("current_quadrant", "Stable") for name, q in quadrant_results.items()}

        return {
            "generated_at": now,
            "version": "v15b",
            "mode": "cloud",
            "current_upsi": round(current_upsi, 3),
            "upsi_status": self._status_text(current_upsi),
            "upsi_series": [round(v, 3) for v in upsi_series],
            "asset_psi": {k: round(v, 3) for k, v in current_psi.items()},
            "asset_spi": {k: round(v, 3) for k, v in current_spi.items()},
            "asset_quadrants": current_quadrants,
            "alert": alert,
            "real_data_flags": real_flags,
            "real_data_ratio": round(sum(1 for v in real_flags.values() if v) / len(real_flags), 2) if real_flags else 0,
            "quadrant_results": {k: {
                "current_quadrant": v.get("current_quadrant", "Stable"),
                "psi_high_threshold": v.get("psi_high_threshold", 0),
                "spi_high_threshold": v.get("spi_high_threshold", 0),
                "n_alerts": v.get("n_alerts", 0),
            } for k, v in quadrant_results.items()},
            "config": {
                "history_days": self.cfg.history_days,
                "alert_threshold_upsi": self.cfg.alert_threshold_upsi,
                "assets_count": len(self.cfg.assets),
                "spi_tau": self.cfg.spi_tau,
                "spi_vol_window": self.cfg.spi_vol_window,
            },
        }

    def render_html(
        self,
        asset_data: Dict[str, List[float]],
        asset_psi: Dict[str, List[float]],
        asset_spi: Dict[str, List[float]],
        upsi_series: List[float],
        real_flags: Dict[str, bool],
        alert: Dict[str, Any],
        quadrant_results: Dict[str, Dict[str, Any]],
    ) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_upsi = upsi_series[-1] if upsi_series else 0.0
        current_psi = {name: (psi[-1] if psi else 0.0) for name, psi in asset_psi.items()}
        current_spi = {name: (spi[-1] if spi else 0.0) for name, spi in asset_spi.items()}
        current_quadrants = {name: q.get("current_quadrant", "Stable") for name, q in quadrant_results.items()}
        upsi_class = self._css_class(current_upsi)
        upsi_status = self._status_text(current_upsi)

        # Historical data (last 100 days for chart)
        hist_len = min(100, len(upsi_series))
        hist_dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(hist_len - 1, -1, -1)]
        hist_upsi = upsi_series[-hist_len:]

        # Heatmap
        heatmap_assets = list(self.cfg.assets.keys())
        heatmap_values = [round(current_psi.get(a, 0), 2) for a in heatmap_assets]
        heatmap_labels = [a.replace(".", " ") for a in heatmap_assets]
        heat_colors = [self._heat_color(v) for v in heatmap_values]

        # SPI heatmap
        spi_values = [round(current_spi.get(a, 0), 2) for a in heatmap_assets]
        spi_colors = [self._spi_heat_color(v) for v in spi_values]

        # Quadrant colors
        quadrant_colors_map = {
            "Stable": "#2ecc71",
            "Gradual Decline": "#f1c40f",
            "Sudden Crisis": "#e67e22",
            "Accelerating Collapse": "#e74c3c",
        }
        quadrant_colors_list = [quadrant_colors_map.get(current_quadrants.get(a, "Stable"), "#95a5a6") for a in heatmap_assets]

        # Alert assets
        alert_assets_psi = alert.get("alert_assets_psi", [])
        alert_assets_spi = alert.get("alert_assets_spi", [])
        quadrant_transitions = alert.get("quadrant_transitions", [])

        # All assets ranking
        sorted_assets = sorted(current_psi.items(), key=lambda x: x[1])

        # Top 5 assets for phase portrait
        top5_assets = sorted(current_psi.items(), key=lambda x: x[1])[:5]
        top5_names = [a[0] for a in top5_assets]

        # Build phase portrait data
        phase_data = []
        for name in top5_names:
            psi = asset_psi.get(name, [])
            spi = asset_spi.get(name, [])
            if psi and spi:
                min_len = min(len(psi), len(spi), 30)  # last 30 points
                aligned_psi = psi[-min_len:]
                aligned_spi = spi[-min_len:]
                phase_data.append({
                    "name": name,
                    "psi": [round(v, 3) for v in aligned_psi],
                    "spi": [round(v, 3) for v in aligned_spi],
                    "quadrant": current_quadrants.get(name, "Stable"),
                })

        html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UPSI Dashboard v15b | SPI-Enhanced Global Pressure Index</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
body{{font-family:-apple-system,"PingFang SC","Segoe UI",sans-serif;background:#f5f6fa;color:#2c3e50;margin:0;padding:20px;}}
.container{{max-width:1400px;margin:0 auto;}}
h1{{color:#2c3e50;font-size:28px;margin-bottom:4px;font-weight:600;}}
.subtitle{{color:#7f8c8d;font-size:13px;margin-bottom:24px;}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px;}}
.kpi{{background:#fff;border-radius:12px;padding:20px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:4px solid #3498db;}}
.kpi.alert{{border-left-color:#c0392b;}} .kpi.warn{{border-left-color:#f39c12;}} .kpi.ok{{border-left-color:#27ae60;}}
.kpi-num{{font-size:36px;font-weight:700;margin-bottom:4px;}}
.kpi-num.alert{{color:#c0392b;}} .kpi-num.warn{{color:#f39c12;}} .kpi-num.ok{{color:#27ae60;}}
.kpi-label{{font-size:12px;color:#7f8c8d;text-transform:uppercase;letter-spacing:0.5px;}}
.kpi-status{{display:inline-block;margin-top:8px;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;color:#fff;}}
.status-alert{{background:#c0392b;}} .status-warn{{background:#f39c12;}} .status-ok{{background:#27ae60;}}
.section{{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.06);}}
h2{{color:#34495e;font-size:18px;margin-top:0;margin-bottom:16px;font-weight:600;}}
.chart{{height:300px;position:relative;}}
.heatmap-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;}}
.heatmap-item{{border-radius:8px;padding:12px;text-align:center;color:#fff;font-weight:600;font-size:14px;text-shadow:0 1px 2px rgba(0,0,0,0.3);}}
.heatmap-value{{font-size:20px;margin-top:4px;}}
.quadrant-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;}}
.quadrant-card{{border-radius:10px;padding:16px;text-align:center;border:2px solid #ecf0f1;transition:all 0.2s;}}
.quadrant-card:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.1);}}
.quadrant-name{{font-size:16px;font-weight:700;margin-bottom:4px;}}
.quadrant-emoji{{font-size:24px;margin-bottom:8px;}}
.quadrant-assets{{font-size:13px;color:#7f8c8d;}}
table{{width:100%;border-collapse:collapse;font-size:13px;}}
th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #ecf0f1;}}
th{{background:#f8f9fa;color:#7f8c8d;font-weight:600;font-size:11px;text-transform:uppercase;}}
tr:hover{{background:#f8f9fa;}}
.tag{{display:inline-block;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:600;color:#fff;}}
.tag-alert{{background:#c0392b;}} .tag-warn{{background:#f39c12;}} .tag-ok{{background:#27ae60;}}
.tag-spi{{background:#8e44ad;}}
.tag-quadrant-stable{{background:#2ecc71;}} .tag-quadrant-decline{{background:#f1c40f;color:#2c3e50;}}
.tag-quadrant-crisis{{background:#e67e22;}} .tag-quadrant-collapse{{background:#e74c3c;}}
.footer{{text-align:center;color:#95a5a6;font-size:12px;margin-top:20px;padding-bottom:20px;}}
.info-box{{background:#e8f4f8;border-left:3px solid #3498db;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;color:#2c3e50;margin-bottom:16px;}}
.simulated{{color:#e74c3c;font-size:11px;}}
.phase-portrait{{width:100%;height:400px;position:relative;}}
.alert-history{{max-height:200px;overflow-y:auto;}}
.alert-item{{padding:8px 12px;border-radius:6px;margin-bottom:6px;font-size:13px;}}
.alert-item.red{{background:#fadbd8;border-left:3px solid #e74c3c;}}
.alert-item.orange{{background:#fdebd0;border-left:3px solid #e67e22;}}
.alert-item.yellow{{background:#fcf3cf;border-left:3px solid #f1c40f;}}
.alert-item.green{{background:#d5f5e3;border-left:3px solid #2ecc71;}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:20px;}}
@media (max-width:900px){{.two-col{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
<div class="container">
<h1>🌍 UPSI 全球压力指数 Dashboard v15b (SPI增强版)</h1>
<div class="subtitle">{len(self.cfg.assets)} 全球资产 | 生成于 {now} | 真实数据比例: {sum(1 for v in real_flags.values() if v)}/{len(real_flags)}</div>

<div class="info-box">
  <b>UPSI v15b 统一公式:</b> UPSI = 0.40 × Material(回撤) + 0.30 × Fragmentation(波动) + 0.30 × Disengagement(动量衰减)<br>
  <b>SPI 突发压力指标:</b> SPI = 0.35×z(V) + 0.25×z(A) + 0.25×|ΔCorr| + 0.15×z(σ_V) &nbsp;|&nbsp; τ = {self.cfg.spi_tau} 交易日<br>
  <b>四象限分类:</b> 🟢 稳定 | 🟡 渐进衰退 | 🟠 突发危机 | 🔴 加速崩溃
</div>

<div class="kpi-grid">
  <div class="kpi {upsi_class}">
    <div class="kpi-num {upsi_class}">{current_upsi:+.2f}</div>
    <div class="kpi-label">全球 UPSI (最新)</div>
    <span class="kpi-status status-{upsi_class}">{upsi_status}</span>
  </div>
  <div class="kpi {'alert' if len(alert_assets_psi) >= self.cfg.alert_assets_count_critical else ('warn' if alert_assets_psi else 'ok')}">
    <div class="kpi-num {'alert' if len(alert_assets_psi) >= self.cfg.alert_assets_count_critical else ('warn' if alert_assets_psi else 'ok')}">{len(alert_assets_psi)}</div>
    <div class="kpi-label">PSI 警报资产数</div>
  </div>
  <div class="kpi {'alert' if alert_assets_spi else ('warn' if alert_assets_spi else 'ok')}">
    <div class="kpi-num {'alert' if alert_assets_spi else ('warn' if alert_assets_spi else 'ok')}">{len(alert_assets_spi)}</div>
    <div class="kpi-label">SPI  elevated 资产数</div>
  </div>
  <div class="kpi {'alert' if alert['level'] == 'CRITICAL' else ('warn' if alert['level'] == 'WARNING' else 'ok')}">
    <div class="kpi-num {'alert' if alert['level'] == 'CRITICAL' else ('warn' if alert['level'] == 'WARNING' else 'ok')}">{alert['level']}</div>
    <div class="kpi-label">综合告警级别</div>
  </div>
  <div class="kpi ok">
    <div class="kpi-num ok">{sum(1 for v in real_flags.values() if v)}/{len(real_flags)}</div>
    <div class="kpi-label">真实数据资产数</div>
  </div>
</div>

<div class="section">
<h2>📈 全球 UPSI 时间序列 (最近 {hist_len} 天)</h2>
<div class="chart"><canvas id="upsiChart"></canvas></div>
</div>

<div class="two-col">
<div class="section">
<h2>🔥 PSI 热力图 (当前 — 低=危机)</h2>
<div class="heatmap-grid">
"""
        for label, val, color in zip(heatmap_labels, heatmap_values, heat_colors):
            idx = heatmap_labels.index(label)
            sim_badge = '<span class="simulated">[SIM]</span>' if not real_flags.get(heatmap_assets[idx], True) else ''
            html += f'  <div class="heatmap-item" style="background:{color}">{label}{sim_badge}<div class="heatmap-value">{val:+.2f}</div></div>\n'

        html += """</div>
</div>

<div class="section">
<h2>⚡ SPI 热力图 (当前 — 高=危机)</h2>
<div class="heatmap-grid">
"""
        for label, val, color in zip(heatmap_labels, spi_values, spi_colors):
            idx = heatmap_labels.index(label)
            sim_badge = '<span class="simulated">[SIM]</span>' if not real_flags.get(heatmap_assets[idx], True) else ''
            html += f'  <div class="heatmap-item" style="background:{color}">{label}{sim_badge}<div class="heatmap-value">{val:+.2f}</div></div>\n'

        html += """</div>
</div>
</div>

<div class="section">
<h2>🎯 四象限分类 (UPSI_v2)</h2>
<div class="quadrant-grid">
"""
        # Group assets by quadrant
        quadrant_assets = {"Stable": [], "Gradual Decline": [], "Sudden Crisis": [], "Accelerating Collapse": []}
        for name in heatmap_assets:
            q = current_quadrants.get(name, "Stable")
            psi_val = current_psi.get(name, 0)
            spi_val = current_spi.get(name, 0)
            quadrant_assets[q].append(f"{name} (P={psi_val:+.2f}, S={spi_val:+.2f})")

        for q_name, q_color in quadrant_colors_map.items():
            assets_in_q = quadrant_assets.get(q_name, [])
            emoji = {"Stable": "🟢", "Gradual Decline": "🟡", "Sudden Crisis": "🟠", "Accelerating Collapse": "🔴"}.get(q_name, "⚪")
            html += f"""  <div class="quadrant-card" style="border-color:{q_color}">
    <div class="quadrant-emoji">{emoji}</div>
    <div class="quadrant-name" style="color:{q_color}">{q_name}</div>
    <div class="quadrant-assets">{len(assets_in_q)} 资产<br>{'<br>'.join(assets_in_q[:5])}{'...' if len(assets_in_q) > 5 else ''}</div>
  </div>
"""

        html += """</div>
</div>

<div class="section">
<h2>📊 2D 相图 — Top 5 最脆弱资产 (PSI vs SPI)</h2>
<div class="phase-portrait"><canvas id="phaseChart"></canvas></div>
</div>

<div class="two-col">
<div class="section">
<h2>⚠️ PSI 警报资产 (PSI &lt; {self.cfg.alert_threshold_asset})</h2>
<table>
<tr><th>资产</th><th>PSI</th><th>SPI</th><th>象限</th><th>状态</th></tr>
"""
        if alert_assets_psi:
            for name, psi_val in alert_assets_psi[:20]:
                spi_val = current_spi.get(name, 0)
                q = current_quadrants.get(name, "Stable")
                tag_class = "tag-alert" if psi_val < -1.0 else "tag-warn"
                tag_text = "严重" if psi_val < -1.0 else "警报"
                q_class = f"tag-quadrant-{q.lower().replace(' ', '-')}"
                html += f'<tr><td>{name}</td><td>{psi_val:+.2f}</td><td>{spi_val:+.2f}</td><td><span class="tag {q_class}">{q}</span></td><td><span class="tag {tag_class}">{tag_text}</span></td></tr>\n'
        else:
            html += '<tr><td colspan="5" style="text-align:center;color:#7f8c8d;">当前无 PSI 警报资产 ✅</td></tr>\n'

        html += """</table>
</div>

<div class="section">
<h2>🚨 SPI Elevated 资产 (SPI &gt; {self.cfg.spi_high_offset})</h2>
<table>
<tr><th>资产</th><th>SPI</th><th>PSI</th><th>象限</th><th>状态</th></tr>
"""
        if alert_assets_spi:
            for name, spi_val in alert_assets_spi[:20]:
                psi_val = current_psi.get(name, 0)
                q = current_quadrants.get(name, "Stable")
                tag_class = "tag-spi"
                tag_text = "Elevated" if spi_val < SPIEngine.SPI_THRESHOLD_CRITICAL else "Critical"
                q_class = f"tag-quadrant-{q.lower().replace(' ', '-')}"
                html += f'<tr><td>{name}</td><td>{spi_val:+.2f}</td><td>{psi_val:+.2f}</td><td><span class="tag {q_class}">{q}</span></td><td><span class="tag {tag_class}">{tag_text}</span></td></tr>\n'
        else:
            html += '<tr><td colspan="5" style="text-align:center;color:#7f8c8d;">当前无 SPI elevated 资产 ✅</td></tr>\n'

        html += """</table>
</div>
</div>

<div class="section">
<h2>📋 象限转换警报历史</h2>
<div class="alert-history">
"""
        if quadrant_transitions:
            for qt in quadrant_transitions:
                alert_class = "red" if "Red" in qt["message"] else ("orange" if "Orange" in qt["message"] else ("yellow" if "Yellow" in qt["message"] else "green"))
                html += f"""<div class="alert-item {alert_class}">
  <b>{qt['emoji']} {qt['asset']}</b>: {qt['from']} → {qt['to']} | {qt['message']}
</div>
"""
        else:
            html += '<div style="text-align:center;color:#7f8c8d;padding:20px;">近期无象限转换 ✅</div>\n'

        html += """</div>
</div>

<div class="section">
<h2>📊 全部资产综合排名</h2>
<table>
<tr><th>排名</th><th>资产</th><th>PSI</th><th>SPI</th><th>象限</th><th>数据来源</th></tr>
"""
        for rank, (name, psi_val) in enumerate(sorted_assets, 1):
            spi_val = current_spi.get(name, 0)
            q = current_quadrants.get(name, "Stable")
            if psi_val < self.cfg.alert_threshold_asset:
                status = '<span class="tag tag-alert">PSI警报</span>'
            elif psi_val < 0:
                status = '<span class="tag tag-warn">关注</span>'
            else:
                status = '<span class="tag tag-ok">正常</span>'
            if spi_val > self.cfg.spi_high_offset:
                status += ' <span class="tag tag-spi">SPI↑</span>'
            q_class = f"tag-quadrant-{q.lower().replace(' ', '-')}"
            data_src = "真实" if real_flags.get(name, False) else "模拟"
            html += f'<tr><td>{rank}</td><td>{name}</td><td>{psi_val:+.2f}</td><td>{spi_val:+.2f}</td><td><span class="tag {q_class}">{q}</span></td><td>{status} {data_src}</td></tr>\n'

        html += f"""</table>
</div>

<div class="footer">
  UPSI Dashboard v15b (SPI-Enhanced) | 数据来源: yfinance ({len(self.cfg.assets)} 资产) | 更新频率: 每4小时<br>
  部署: GitHub Actions + GitHub Pages | 局限: yfinance 数据有延迟; ΔGSI 用跨资产相关性替代<br>
  生成时间: {now}
</div>
</div>

<script>
// UPSI Chart
const upsiLabels = {json.dumps(hist_dates)};
const upsiValues = {json.dumps([round(v, 3) for v in hist_upsi])};
const alertLine = upsiValues.map(() => {self.cfg.alert_threshold_upsi});

const ctx1 = document.getElementById('upsiChart').getContext('2d');
new Chart(ctx1, {{
  type: 'line',
  data: {{
    labels: upsiLabels,
    datasets: [
      {{
        label: '全球 UPSI',
        data: upsiValues,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.3,
        fill: true
      }},
      {{
        label: '警报阈值 ({self.cfg.alert_threshold_upsi})',
        data: alertLine,
        borderColor: '#c0392b',
        borderWidth: 1.5,
        borderDash: [6, 4],
        pointRadius: 0,
        fill: false
      }}
    ]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ labels: {{ color: '#2c3e50', font: {{ size: 12 }} }} }},
      tooltip: {{ mode: 'index', intersect: false }}
    }},
    scales: {{
      x: {{ ticks: {{ color: '#7f8c8d', maxTicksLimit: 12, font: {{ size: 11 }} }}, grid: {{ color: '#ecf0f1' }} }},
      y: {{ ticks: {{ color: '#7f8c8d', font: {{ size: 11 }} }}, grid: {{ color: '#ecf0f1' }}, suggestedMin: -2, suggestedMax: 2 }}
    }}
  }}
}});

// Phase Portrait Chart
const phaseData = {json.dumps(phase_data)};
const quadrantColors = {{"Stable": "#2ecc71", "Gradual Decline": "#f1c40f", "Sudden Crisis": "#e67e22", "Accelerating Collapse": "#e74c3c"}};

const ctx2 = document.getElementById('phaseChart').getContext('2d');
const datasets = phaseData.map(asset => ({{
  label: asset.name,
  data: asset.psi.map((p, i) => ({{x: p, y: asset.spi[i]}})),
  borderColor: quadrantColors[asset.quadrant] || '#95a5a6',
  backgroundColor: (quadrantColors[asset.quadrant] || '#95a5a6') + '40',
  pointRadius: 3,
  pointHoverRadius: 6,
  showLine: true,
  tension: 0.3,
  borderWidth: 1.5
}}));

new Chart(ctx2, {{
  type: 'scatter',
  data: {{ datasets: datasets }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'right', labels: {{ font: {{ size: 11 }} }} }},
      tooltip: {{
        callbacks: {{
          label: function(context) {{
            const pt = context.raw;
            return context.dataset.label + ': PSI=' + pt.x.toFixed(2) + ', SPI=' + pt.y.toFixed(2);
          }}
        }}
      }}
    }},
    scales: {{
      x: {{
        title: {{ display: true, text: 'PSI (Level)', color: '#2c3e50', font: {{ size: 12 }} }},
        ticks: {{ color: '#7f8c8d' }},
        grid: {{ color: '#ecf0f1' }}
      }},
      y: {{
        title: {{ display: true, text: 'SPI (Velocity)', color: '#2c3e50', font: {{ size: 12 }} }},
        ticks: {{ color: '#7f8c8d' }},
        grid: {{ color: '#ecf0f1' }}
      }}
    }}
  }}
}});
</script>
</body>
</html>
"""
        return html

    @staticmethod
    def _css_class(v: float) -> str:
        if v < -0.5:
            return "alert"
        elif v < 0:
            return "warn"
        return "ok"

    @staticmethod
    def _status_text(v: float) -> str:
        if v < -0.5:
            return "🚨 警报"
        elif v < 0:
            return "⚠️ 关注"
        return "✅ 正常"

    @staticmethod
    def _heat_color(v: float) -> str:
        if v < -1.0:
            return "#c0392b"
        elif v < -0.5:
            return "#e74c3c"
        elif v < 0:
            return "#f39c12"
        elif v < 0.5:
            return "#27ae60"
        return "#2ecc71"

    @staticmethod
    def _spi_heat_color(v: float) -> str:
        if v > 2.5:
            return "#c0392b"
        elif v > 1.5:
            return "#e74c3c"
        elif v > 1.0:
            return "#e67e22"
        elif v > 0.5:
            return "#f1c40f"
        return "#27ae60"

    def write_outputs(self, html: str, data: Dict[str, Any]) -> None:
        out_dir = Path(self.cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        html_path = out_dir / self.cfg.output_html
        html_path.write_text(html, encoding="utf-8")
        self.log.info("[Renderer] HTML written to %s", html_path)

        json_path = out_dir / self.cfg.output_json
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.log.info("[Renderer] JSON written to %s", json_path)


# ============================================================
# DashboardApp
# ============================================================

class DashboardApp:
    """Orchestrates all modules: DataFetcher → PSIEngine → SPIEngine → AlertSystem → Renderer"""

    def __init__(self, config: DashboardConfig):
        self.cfg = config
        self.log = setup_logging(config.log_level)
        self.fetcher = DataFetcher(config, self.log)
        self.psi_engine = PSIEngine(config, self.log)
        self.spi_engine = SPIEngine(config, self.log)
        self.alerts = AlertSystem(config, self.log)
        self.renderer = Renderer(config, self.log)

    def run_once(self) -> int:
        self.log.info("=" * 60)
        self.log.info("UPSI Dashboard v15b — Starting (mode=once)")
        self.log.info("=" * 60)

        try:
            # 1. Fetch
            asset_data, real_flags = self.fetcher.fetch_all()
            if not asset_data:
                self.log.error("No asset data available. Aborting.")
                return 1

            # 2. Compute PSI
            self.log.info("[PSIEngine] Computing PSI for %d assets...", len(asset_data))
            asset_psi: Dict[str, list] = {}
            for name, prices in asset_data.items():
                psi, mmp_z, sfd_z, eed_z = self.psi_engine.compute_psi(prices)
                asset_psi[name] = psi
                if psi:
                    self.log.info("  %s: PSI=%+.2f M=%+.2f F=%+.2f D=%+.2f",
                                    name, psi[-1], mmp_z[-1], sfd_z[-1], eed_z[-1])

            # 3. Compute UPSI
            upsi_series = self.psi_engine.compute_upsi(asset_psi)
            if not upsi_series:
                self.log.error("Failed to compute UPSI series.")
                return 1
            self.log.info("[PSIEngine] UPSI series length=%d, current=%+.2f",
                          len(upsi_series), upsi_series[-1])

            # 4. Compute SPI + Quadrants
            self.log.info("[SPIEngine] Computing SPI and quadrants for %d assets...", len(asset_data))
            asset_spi, quadrant_results = self.spi_engine.compute_all(asset_data, asset_psi)
            for name, spi in asset_spi.items():
                q = quadrant_results.get(name, {}).get("current_quadrant", "Stable")
                self.log.info("  %s: SPI=%+.2f Quadrant=%s", name, spi[-1] if spi else 0, q)

            # 5. Alerts
            current_psi = {name: (psi[-1] if psi else 0.0) for name, psi in asset_psi.items()}
            current_spi = {name: (spi[-1] if spi else 0.0) for name, spi in asset_spi.items()}
            alert = self.alerts.check(upsi_series[-1], current_psi, current_spi, quadrant_results)
            self.alerts.send_webhook(alert)

            # 6. Render
            html = self.renderer.render_html(asset_data, asset_psi, asset_spi, upsi_series, real_flags, alert, quadrant_results)
            json_data = self.renderer.render_json(asset_data, asset_psi, asset_spi, upsi_series, real_flags, alert, quadrant_results)
            self.renderer.write_outputs(html, json_data)

            # 7. Exit code
            simulated_count = sum(1 for v in real_flags.values() if not v)
            exit_code = 2 if simulated_count > 0 else 0
            self.log.info("=" * 60)
            self.log.info("Done. Simulated assets: %d/%d", simulated_count, len(real_flags))
            self.log.info("=" * 60)
            return exit_code

        except Exception as e:
            self.log.exception("Fatal error in dashboard run: %s", e)
            try:
                fallback: Dict[str, Any] = {
                    "generated_at": datetime.now().isoformat(),
                    "version": "v15b",
                    "error": str(e),
                    "upsi_series": [],
                }
                out_dir = Path(self.cfg.output_dir)
                out_dir.mkdir(parents=True, exist_ok=True)
                with open(out_dir / self.cfg.output_json, "w", encoding="utf-8") as f:
                    json.dump(fallback, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return 1

    def run_daemon(self) -> None:
        self.log.info("[Daemon] Starting with interval=%.1f hours", self.cfg.daemon_interval_hours)
        while True:
            self.run_once()
            sleep_seconds = self.cfg.daemon_interval_hours * 3600
            self.log.info("[Daemon] Sleeping %.0f seconds...", sleep_seconds)
            time.sleep(sleep_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="UPSI Dashboard v15b (SPI-Enhanced)")
    parser.add_argument("--mode", choices=["once", "daemon"], default="once",
                        help="Run mode: once (default) or daemon")
    parser.add_argument("--output-dir", type=str, default=".",
                        help="Output directory for HTML and JSON")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    cfg = DashboardConfig()
    cfg.output_dir = args.output_dir
    cfg.log_level = args.log_level

    app = DashboardApp(cfg)
    if args.mode == "daemon":
        app.run_daemon()
        return 0
    else:
        return app.run_once()


if __name__ == "__main__":
    sys.exit(main())
