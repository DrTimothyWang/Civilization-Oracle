#!/usr/bin/env python3
"""
Dashboard App — Main orchestrator for UPSI Dashboard v14d.
=============================================================
Usage:
    python -m src.dashboard --mode=once          # Single run (CI / manual)
    python -m src.dashboard --mode=daemon        # Daemon mode (local long-running)
    python -m src.dashboard --config=custom.yaml # Specify config file

Exit codes:
    0 — Success
    1 — Critical error (cannot generate output)
    2 — Partial failure (some assets fell back to simulated data)
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .config import DashboardConfig
from .data_fetcher import DataFetcher
from .psi_engine import PSIEngine
from .alert_system import AlertSystem
from .renderer import Renderer


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("upsi_dashboard")
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


class DashboardApp:
    """Orchestrates all modules."""

    def __init__(self, config: DashboardConfig):
        self.cfg = config
        self.log = setup_logging(config.log_level)
        self.fetcher = DataFetcher(config, self.log)
        self.engine = PSIEngine(config, self.log)
        self.alerts = AlertSystem(config, self.log)
        self.renderer = Renderer(config, self.log)

    def run_once(self) -> int:
        """Single run, returns exit code."""
        self.log.info("=" * 60)
        self.log.info("UPSI Dashboard v14d — Starting (mode=once)")
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
                psi, mmp_z, sfd_z, eed_z = self.engine.compute_psi(prices)
                asset_psi[name] = psi
                if psi:
                    self.log.info("  %s: PSI=%+.2f M=%+.2f F=%+.2f D=%+.2f",
                                    name, psi[-1], mmp_z[-1], sfd_z[-1], eed_z[-1])

            # 3. Compute UPSI
            upsi_series = self.engine.compute_upsi(asset_psi)
            if not upsi_series:
                self.log.error("Failed to compute UPSI series.")
                return 1
            self.log.info("[PSIEngine] UPSI series length=%d, current=%+.2f",
                          len(upsi_series), upsi_series[-1])

            # 4. Alerts
            current_psi = {name: (psi[-1] if psi else 0.0) for name, psi in asset_psi.items()}
            alert = self.alerts.check(upsi_series[-1], current_psi)
            self.alerts.send_webhook(alert)

            # 5. Render
            html = self.renderer.render_html(asset_data, asset_psi, upsi_series, real_flags, alert)
            json_data = self.renderer.render_json(asset_data, asset_psi, upsi_series, real_flags, alert)
            self.renderer.write_outputs(html, json_data)

            # 6. Exit code
            simulated_count = sum(1 for v in real_flags.values() if not v)
            exit_code = 2 if simulated_count > 0 else 0
            self.log.info("=" * 60)
            self.log.info("Done. Simulated assets: %d/%d", simulated_count, len(real_flags))
            self.log.info("=" * 60)
            return exit_code

        except Exception as e:
            self.log.exception("Fatal error in dashboard run: %s", e)
            # Try to generate degraded output
            try:
                fallback: Dict[str, Any] = {
                    "generated_at": datetime.now().isoformat(),
                    "version": "v14d",
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
        """Daemon mode: loop forever."""
        self.log.info("[Daemon] Starting with interval=%.1f hours", self.cfg.daemon_interval_hours)
        while True:
            self.run_once()
            sleep_seconds = self.cfg.daemon_interval_hours * 3600
            self.log.info("[Daemon] Sleeping %.0f seconds...", sleep_seconds)
            time.sleep(sleep_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="UPSI Dashboard v14d")
    parser.add_argument("--mode", choices=["once", "daemon"], default="once",
                        help="Run mode: once (default) or daemon")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to YAML or JSON config file")
    parser.add_argument("--output-dir", type=str, default=".",
                        help="Output directory for HTML and JSON")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    # Load config
    if args.config:
        config_path = Path(args.config)
        if config_path.suffix in (".yaml", ".yml"):
            cfg = DashboardConfig.from_yaml(config_path)
        elif config_path.suffix == ".json":
            cfg = DashboardConfig.from_json(config_path)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    else:
        cfg = DashboardConfig()

    # CLI overrides
    cfg.output_dir = args.output_dir
    cfg.log_level = args.log_level

    app = DashboardApp(cfg)
    if args.mode == "daemon":
        app.run_daemon()
        return 0  # unreachable
    else:
        return app.run_once()


if __name__ == "__main__":
    sys.exit(main())
