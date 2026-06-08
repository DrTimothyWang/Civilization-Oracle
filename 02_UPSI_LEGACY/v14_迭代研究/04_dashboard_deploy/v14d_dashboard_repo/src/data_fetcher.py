"""Data Fetcher — Pull asset data from yfinance with graceful fallback to simulated data."""

import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

from .config import DashboardConfig


class DataFetcher:
    """Responsible for pulling asset data from yfinance, falling back to simulated data on failure."""

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
        """
        Fetch a single asset.
        Returns: (prices_list, is_real)
        is_real=True means real data, False means simulated fallback.
        """
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

                # Handle yfinance old/new format compatibility
                if pd is not None and isinstance(df.columns, pd.MultiIndex):
                    prices = df["Close"][ticker].dropna().tolist()
                else:
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
        """Fetch all assets, return (data_dict, real_flag_dict)."""
        self.log.info("[DataFetcher] Pulling %d assets from yfinance...", len(self.cfg.assets))
        data: Dict[str, List[float]] = {}
        real_flags: Dict[str, bool] = {}
        for name, ticker in self.cfg.assets.items():
            prices, is_real = self.fetch_single(name, ticker)
            if prices is not None:
                data[name] = prices
                real_flags[name] = is_real
        return data, real_flags
