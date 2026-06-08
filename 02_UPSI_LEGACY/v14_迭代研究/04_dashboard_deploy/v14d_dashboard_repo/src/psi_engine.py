"""PSI Engine — Compute PSI three dimensions and UPSI."""

import logging
import statistics
from typing import Dict, List, Tuple

from .config import DashboardConfig


class PSIEngine:
    """Compute PSI three dimensions (Material / Fragmentation / Disengagement) and UPSI."""

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
        """Return (psi, material_z, fragmentation_z, disengagement_z)."""
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
        """Global UPSI = equal-weighted average of asset PSI."""
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
