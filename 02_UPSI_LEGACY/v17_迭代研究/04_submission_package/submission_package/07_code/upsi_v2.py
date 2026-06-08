"""
UPSI_v2 Core Engine
===================
4-quadrant crisis classifier combining PSI (level) and SPI (velocity).

Author: UPSI_v2_Prototype_Engineer
Date: 2026-06-04
Version: v14c
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUADRANT_NAMES = {
    (0, 0): "Stable",
    (0, 1): "Sudden Crisis",
    (1, 0): "Gradual Decline",
    (1, 1): "Accelerating Collapse",
}

QUADRANT_COLORS = {
    "Stable": "#2ecc71",               # 🟢 Green
    "Gradual Decline": "#f1c40f",      # 🟡 Yellow
    "Sudden Crisis": "#e67e22",        # 🟠 Orange
    "Accelerating Collapse": "#e74c3c", # 🔴 Red
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

DEFAULT_PSI_HIGH_OFFSET = 0.5   # mean + 0.5 * std
DEFAULT_SPI_HIGH_OFFSET = 1.5   # mean + 1.5 * std


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class UPSIAlert:
    """Single alert event."""
    time_idx: int
    from_quadrant: str
    to_quadrant: str
    message: str
    emoji: str
    year_label: Optional[Any] = None


@dataclass
class UPSIResult:
    """Container for UPSI_v2 classification results."""
    time: np.ndarray
    psi: np.ndarray
    spi: np.ndarray
    time_labels: List[Any]
    psi_high: float
    spi_high: float
    quadrants: List[str]
    quadrant_codes: List[Tuple[int, int]]
    alerts: List[UPSIAlert] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dataframe(self) -> pd.DataFrame:
        """Export results as a pandas DataFrame."""
        return pd.DataFrame({
            "time_idx": self.time,
            "time_label": self.time_labels,
            "psi": self.psi,
            "spi": self.spi,
            "quadrant": self.quadrants,
            "psi_high": self.psi > self.psi_high,
            "spi_high": self.spi > self.spi_high,
        })

    def summary(self) -> Dict[str, Any]:
        """JSON-serializable summary."""
        return {
            "n_points": int(len(self.time)),
            "psi_high_threshold": float(self.psi_high),
            "spi_high_threshold": float(self.spi_high),
            "quadrant_distribution": {
                q: int(sum(1 for qq in self.quadrants if qq == q))
                for q in set(self.quadrants)
            },
            "n_alerts": len(self.alerts),
            "alerts": [
                {
                    "time_idx": a.time_idx,
                    "year_label": a.year_label,
                    "from": a.from_quadrant,
                    "to": a.to_quadrant,
                    "message": a.message,
                    "emoji": a.emoji,
                }
                for a in self.alerts
            ],
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class UPSIv2Engine:
    """
    UPSI_v2 4-quadrant crisis classifier.

    Parameters
    ----------
    psi_high_offset : float
        Multiplier for PSI std above mean to define "high" (default 0.5).
    spi_high_offset : float
        Multiplier for SPI std above mean to define "high" (default 1.5).
    """

    def __init__(
        self,
        psi_high_offset: float = DEFAULT_PSI_HIGH_OFFSET,
        spi_high_offset: float = DEFAULT_SPI_HIGH_OFFSET,
    ):
        self.psi_high_offset = psi_high_offset
        self.spi_high_offset = spi_high_offset

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(
        self,
        psi: np.ndarray,
        spi: np.ndarray,
        time_labels: Optional[List[Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UPSIResult:
        """
        Classify each time point into one of 4 quadrants.

        Parameters
        ----------
        psi : np.ndarray
            Pressure Synchronization Index time series (level).
        spi : np.ndarray
            Sudden Pressure Indicator time series (velocity).
        time_labels : list, optional
            Human-readable labels for each time point (e.g., years).
        metadata : dict, optional
            Extra info (domain name, source file, etc.).

        Returns
        -------
        UPSIResult
        """
        psi = np.asarray(psi, dtype=float)
        spi = np.asarray(spi, dtype=float)
        if psi.shape != spi.shape:
            raise ValueError("psi and spi must have the same shape")
        if len(psi) == 0:
            raise ValueError("Input arrays must not be empty")

        n = len(psi)
        time_labels = time_labels if time_labels is not None else list(range(n))
        if len(time_labels) != n:
            raise ValueError("time_labels length must match psi/spi length")

        # Thresholds
        psi_mean, psi_std = float(np.mean(psi)), float(np.std(psi))
        spi_mean, spi_std = float(np.mean(spi)), float(np.std(spi))
        psi_high = psi_mean + self.psi_high_offset * psi_std
        spi_high = spi_mean + self.spi_high_offset * spi_std

        # Quadrant assignment
        quadrants: List[str] = []
        codes: List[Tuple[int, int]] = []
        for i in range(n):
            p_flag = 1 if psi[i] > psi_high else 0
            s_flag = 1 if spi[i] > spi_high else 0
            codes.append((p_flag, s_flag))
            quadrants.append(QUADRANT_NAMES[(p_flag, s_flag)])

        result = UPSIResult(
            time=np.arange(n),
            psi=psi,
            spi=spi,
            time_labels=time_labels,
            psi_high=psi_high,
            spi_high=spi_high,
            quadrants=quadrants,
            quadrant_codes=codes,
            metadata=metadata or {},
        )

        # Alert detection
        result.alerts = self._detect_alerts(result)
        return result

    def _detect_alerts(self, result: UPSIResult) -> List[UPSIAlert]:
        """Detect quadrant transitions that trigger alerts."""
        alerts: List[UPSIAlert] = []
        for i in range(1, len(result.quadrants)):
            prev_q = result.quadrants[i - 1]
            curr_q = result.quadrants[i]
            if prev_q == curr_q:
                continue
            key = (prev_q, curr_q)
            if key in ALERT_RULES:
                msg, emoji = ALERT_RULES[key]
                alerts.append(
                    UPSIAlert(
                        time_idx=i,
                        from_quadrant=prev_q,
                        to_quadrant=curr_q,
                        message=msg,
                        emoji=emoji,
                        year_label=result.time_labels[i],
                    )
                )
        return alerts

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def plot_phase_portrait(
        self,
        result: UPSIResult,
        title: str = "UPSI_v2 Phase Portrait",
        figsize: Tuple[float, float] = (8, 8),
        alpha_base: float = 0.6,
        save_path: Optional[str] = None,
        show_time_trajectory: bool = True,
    ) -> plt.Figure:
        """
        2D phase portrait: PSI (x) vs SPI (y) with quadrant coloring.

        Time progression is encoded via point size (later = larger).
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Background quadrant shading
        psi_max = float(np.max(result.psi)) * 1.05
        psi_min = float(np.min(result.psi)) * 0.95
        spi_max = float(np.max(result.spi)) * 1.05
        spi_min = float(np.min(result.spi)) * 0.95

        ax.axvline(result.psi_high, color="gray", linestyle="--", linewidth=1, alpha=0.7)
        ax.axhline(result.spi_high, color="gray", linestyle="--", linewidth=1, alpha=0.7)

        # Quadrant background colors (very faint)
        bg_colors = {
            (0, 0): "#d5f5e3",  # Stable
            (1, 0): "#fcf3cf",  # Gradual Decline
            (0, 1): "#fdebd0",  # Sudden Crisis
            (1, 1): "#f5b7b1",  # Accelerating Collapse
        }
        ax.fill_betweenx([spi_min, spi_max], psi_min, result.psi_high, color=bg_colors[(0, 0)], alpha=0.3, zorder=0)
        ax.fill_betweenx([spi_min, spi_max], result.psi_high, psi_max, color=bg_colors[(1, 0)], alpha=0.3, zorder=0)
        ax.fill_betweenx([result.spi_high, spi_max], psi_min, result.psi_high, color=bg_colors[(0, 1)], alpha=0.3, zorder=0)
        ax.fill_betweenx([result.spi_high, spi_max], result.psi_high, psi_max, color=bg_colors[(1, 1)], alpha=0.3, zorder=0)

        # Scatter by quadrant
        sizes = np.linspace(20, 200, len(result.psi))
        for q_name in QUADRANT_NAMES.values():
            mask = np.array([qq == q_name for qq in result.quadrants])
            if not np.any(mask):
                continue
            ax.scatter(
                result.psi[mask],
                result.spi[mask],
                c=QUADRANT_COLORS[q_name],
                s=sizes[mask],
                alpha=alpha_base,
                edgecolors="black",
                linewidth=0.5,
                label=q_name,
                zorder=3,
            )

        # Time trajectory (thin line connecting points in time order)
        if show_time_trajectory:
            ax.plot(result.psi, result.spi, "k-", alpha=0.2, linewidth=0.8, zorder=2)
            # Annotate start and end
            ax.annotate(
                f"Start: {result.time_labels[0]}",
                (result.psi[0], result.spi[0]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=8,
                color="darkgreen",
            )
            ax.annotate(
                f"End: {result.time_labels[-1]}",
                (result.psi[-1], result.spi[-1]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=8,
                color="darkred",
            )

        ax.set_xlabel("PSI (Level)", fontsize=12)
        ax.set_ylabel("SPI (Velocity)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(loc="upper right", title="Quadrant")
        ax.set_xlim(psi_min, psi_max)
        ax.set_ylim(spi_min, spi_max)

        # Annotation for thresholds
        ax.text(
            result.psi_high + 0.01 * (psi_max - psi_min),
            spi_min + 0.02 * (spi_max - spi_min),
            f"PSI_high = {result.psi_high:.3f}",
            fontsize=8,
            color="gray",
        )
        ax.text(
            psi_min + 0.01 * (psi_max - psi_min),
            result.spi_high + 0.02 * (spi_max - spi_min),
            f"SPI_high = {result.spi_high:.3f}",
            fontsize=8,
            color="gray",
        )

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
        return fig

    def plot_time_series(
        self,
        result: UPSIResult,
        title: str = "UPSI_v2 Time Series",
        figsize: Tuple[float, float] = (14, 10),
        save_path: Optional[str] = None,
        highlight_alerts: bool = True,
    ) -> plt.Figure:
        """
        3-panel time-series plot:
        1. PSI level
        2. SPI spike
        3. Quadrant timeline
        """
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
        x = np.arange(len(result.time_labels))
        labels = [str(l) for l in result.time_labels]

        # --- Panel 1: PSI ---
        ax1 = axes[0]
        ax1.fill_between(x, result.psi, alpha=0.3, color="#3498db")
        ax1.plot(x, result.psi, color="#2980b9", linewidth=2, label="PSI")
        ax1.axhline(result.psi_high, color="red", linestyle="--", linewidth=1, label=f"High threshold = {result.psi_high:.3f}")
        ax1.set_ylabel("PSI (Level)", fontsize=11)
        ax1.set_title(title, fontsize=14, fontweight="bold")
        ax1.legend(loc="upper left")
        ax1.grid(True, alpha=0.3)

        # --- Panel 2: SPI ---
        ax2 = axes[1]
        ax2.fill_between(x, result.spi, alpha=0.3, color="#e74c3c")
        ax2.plot(x, result.spi, color="#c0392b", linewidth=2, label="SPI")
        ax2.axhline(result.spi_high, color="red", linestyle="--", linewidth=1, label=f"High threshold = {result.spi_high:.3f}")
        ax2.set_ylabel("SPI (Velocity)", fontsize=11)
        ax2.legend(loc="upper left")
        ax2.grid(True, alpha=0.3)

        # --- Panel 3: Quadrant timeline ---
        ax3 = axes[2]
        quadrant_to_int = {
            "Stable": 0,
            "Gradual Decline": 1,
            "Sudden Crisis": 2,
            "Accelerating Collapse": 3,
        }
        y_vals = [quadrant_to_int[q] for q in result.quadrants]
        colors = [QUADRANT_COLORS[q] for q in result.quadrants]

        ax3.scatter(x, y_vals, c=colors, s=100, edgecolors="black", linewidth=0.5, zorder=3)
        ax3.plot(x, y_vals, "k-", alpha=0.2, linewidth=0.8, zorder=2)
        ax3.set_yticks([0, 1, 2, 3])
        ax3.set_yticklabels(["Stable", "Gradual Decline", "Sudden Crisis", "Accelerating Collapse"])
        ax3.set_ylabel("Quadrant", fontsize=11)
        ax3.set_xlabel("Time", fontsize=11)
        ax3.set_xlim(x[0] - 0.5, x[-1] + 0.5)
        ax3.grid(True, alpha=0.3)

        # Alert annotations
        if highlight_alerts and result.alerts:
            for alert in result.alerts:
                ax3.axvline(alert.time_idx, color="black", linestyle=":", alpha=0.5, linewidth=1)
                ax3.annotate(
                    f"{alert.emoji} {alert.to_quadrant}",
                    xy=(alert.time_idx, quadrant_to_int[alert.to_quadrant]),
                    xytext=(alert.time_idx + 0.5, quadrant_to_int[alert.to_quadrant] + 0.3),
                    fontsize=7,
                    arrowprops=dict(arrowstyle="->", color="black", alpha=0.5),
                )

        # X-tick labels (sparse to avoid crowding)
        step = max(1, len(labels) // 20)
        ax3.set_xticks(x[::step])
        ax3.set_xticklabels(labels[::step], rotation=45, ha="right", fontsize=8)

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
        return fig

    def plot_quadrant_legend(
        self,
        save_path: Optional[str] = None,
        figsize: Tuple[float, float] = (6, 4),
    ) -> plt.Figure:
        """Standalone quadrant legend / reference card."""
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

        # Title
        ax.text(5, 9.2, "UPSI_v2 Quadrant Legend", fontsize=14, fontweight="bold", ha="center")

        # 2x2 grid
        positions = {
            "Accelerating Collapse": (7.5, 6.5),
            "Gradual Decline": (7.5, 3.5),
            "Sudden Crisis": (2.5, 6.5),
            "Stable": (2.5, 3.5),
        }
        descriptions = {
            "Stable": "PSI low, SPI low\nNo action needed",
            "Gradual Decline": "PSI high, SPI low\nMonitor long-term",
            "Sudden Crisis": "PSI low, SPI high\nPrepare for shock",
            "Accelerating Collapse": "PSI high, SPI high\nAct immediately",
        }

        for q_name, (cx, cy) in positions.items():
            rect = plt.Rectangle(
                (cx - 1.8, cy - 1.3), 3.6, 2.6,
                facecolor=QUADRANT_COLORS[q_name],
                edgecolor="black",
                linewidth=1.5,
                alpha=0.7,
            )
            ax.add_patch(rect)
            ax.text(cx, cy + 0.5, f"{QUADRANT_EMOJI[q_name]} {q_name}", fontsize=10, fontweight="bold", ha="center")
            ax.text(cx, cy - 0.3, descriptions[q_name], fontsize=8, ha="center", va="center")

        # Axis labels
        ax.text(5, 1.0, "PSI (Level) →", fontsize=10, ha="center", style="italic")
        ax.text(0.3, 5, "SPI (Velocity)\n↑", fontsize=10, ha="center", va="center", style="italic", rotation=90)

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
        return fig

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def compute_spi_from_psi(psi: np.ndarray, window: int = 1) -> np.ndarray:
        """
        Approximate SPI as the discrete derivative (rate of change) of PSI.
        This is a fallback when native SPI is unavailable.
        """
        psi = np.asarray(psi, dtype=float)
        if len(psi) < 2:
            return np.zeros_like(psi)
        # Central difference for interior, forward/backward at edges
        spi = np.empty_like(psi)
        spi[0] = psi[1] - psi[0]
        spi[-1] = psi[-1] - psi[-2]
        for i in range(1, len(psi) - 1):
            spi[i] = (psi[i + 1] - psi[i - 1]) / 2.0
        return spi

    @staticmethod
    def save_result_json(result: UPSIResult, path: str) -> None:
        """Save result summary to JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result.summary(), f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def run_upsi_v2(
    psi: np.ndarray,
    spi: np.ndarray,
    time_labels: Optional[List[Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    psi_high_offset: float = DEFAULT_PSI_HIGH_OFFSET,
    spi_high_offset: float = DEFAULT_SPI_HIGH_OFFSET,
    output_dir: Optional[str] = None,
    prefix: str = "upsi_v2",
) -> Tuple[UPSIResult, UPSIv2Engine]:
    """
    One-shot classification + plotting + JSON export.

    Returns
    -------
    (result, engine)
    """
    engine = UPSIv2Engine(psi_high_offset=psi_high_offset, spi_high_offset=spi_high_offset)
    result = engine.classify(psi, spi, time_labels=time_labels, metadata=metadata)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        engine.plot_phase_portrait(result, save_path=os.path.join(output_dir, f"{prefix}_phase_portrait.png"))
        engine.plot_time_series(result, save_path=os.path.join(output_dir, f"{prefix}_time_series.png"))
        engine.plot_quadrant_legend(save_path=os.path.join(output_dir, f"{prefix}_quadrant_legend.png"))
        UPSIv2Engine.save_result_json(result, os.path.join(output_dir, f"{prefix}_result.json"))

    return result, engine
