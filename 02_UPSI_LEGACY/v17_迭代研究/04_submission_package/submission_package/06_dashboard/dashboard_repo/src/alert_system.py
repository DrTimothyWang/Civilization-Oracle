"""Alert System — Threshold-based alerting with optional webhook extension."""

import json
import logging
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import DashboardConfig


class AlertSystem:
    """Detect alerts based on thresholds and output structured alert info."""

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger

    def check(self, current_upsi: float, current_psi: Dict[str, float]) -> Dict[str, Any]:
        """Check alert conditions and return structured alert information."""
        alerts: List[str] = []
        level = "OK"

        # Asset-level alerts
        alert_assets = [(n, v) for n, v in current_psi.items() if v < self.cfg.alert_threshold_asset]
        alert_assets.sort(key=lambda x: x[1])

        if current_upsi < self.cfg.alert_threshold_upsi:
            level = "CRITICAL"
            alerts.append(f"UPSI {current_upsi:+.2f} below threshold {self.cfg.alert_threshold_upsi}")
        elif current_upsi < 0:
            level = "WARNING"
            alerts.append(f"UPSI {current_upsi:+.2f} in watch zone")

        if len(alert_assets) >= self.cfg.alert_assets_count_critical:
            level = "CRITICAL"
            alerts.append(f"{len(alert_assets)} assets in alert state")
        elif alert_assets:
            if level == "OK":
                level = "WARNING"
            alerts.append(f"{len(alert_assets)} assets in alert state")

        result = {
            "level": level,
            "upsi": current_upsi,
            "alert_assets": alert_assets,
            "messages": alerts,
            "timestamp": datetime.now().isoformat(),
        }
        self.log.info("[AlertSystem] Level=%s, Alerts=%d", level, len(alert_assets))
        return result

    def send_webhook(self, alert: Dict[str, Any]) -> bool:
        """Send webhook alert (if webhook_url is configured)."""
        if not self.cfg.webhook_url:
            return False
        try:
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
