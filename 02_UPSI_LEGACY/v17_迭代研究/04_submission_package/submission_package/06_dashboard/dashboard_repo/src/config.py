"""Dashboard Config — Runtime configuration supporting YAML/JSON loading or defaults."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass
class DashboardConfig:
    """Runtime configuration, supports loading from YAML/JSON or default values."""
    assets: Dict[str, str] = field(default_factory=lambda: {
        "US.SP500": "^GSPC",
        "JP.N225": "^N225",
        "CA.TSX": "^GSPTSE",
        "UK.FTSE": "^FTSE",
        "DE.DAX": "^GDAXI",
        "HK.HSI": "^HSI",
        "BR.BVSP": "^BVSP",
        "AR.MERVAL": "^MERV",
        "TR.XU100": "XU100.IS",
        "AU.ASX": "^AXJO",
        "FR.CAC": "^FCHI",
        "IN.NIFTY": "^NSEI",
        "RU.IMOEX": "IMOEX.ME",
        "USDJPY": "JPY=X",
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "US.10Y": "^TNX",
        "GOLD": "GC=F",
        "OIL.WTI": "CL=F",
        "VIX": "^VIX",
    })
    history_days: int = 252
    alert_threshold_upsi: float = -0.5
    alert_threshold_asset: float = -0.5
    alert_assets_count_critical: int = 5
    output_dir: str = "."
    output_html: str = "dashboard_latest.html"
    output_json: str = "dashboard_data_v2.json"
    log_level: str = "INFO"
    daemon_interval_hours: float = 4.0
    max_retries_yf: int = 3
    retry_delay_seconds: float = 2.0
    webhook_url: Optional[str] = None
    email_recipient: Optional[str] = None
    simulated_data_bias: float = -0.0002
    simulated_data_volatility: float = 0.012

    @classmethod
    def from_yaml(cls, path: Path) -> "DashboardConfig":
        if yaml is None:
            raise ImportError("PyYAML is required to load YAML configs. Install: pip install pyyaml")
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(**raw)

    @classmethod
    def from_json(cls, path: Path) -> "DashboardConfig":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(**raw)
