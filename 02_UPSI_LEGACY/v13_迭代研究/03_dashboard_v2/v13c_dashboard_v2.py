#!/usr/bin/env python3
"""
v13c Dashboard v2 — Cloud-Deployable UPSI Dashboard
=====================================================
模块化、可配置、支持本地和 CI 环境运行。

Usage:
    python v13c_dashboard_v2.py --mode=once          # 单次运行（CI / 手动）
    python v13c_dashboard_v2.py --mode=daemon        # 守护模式（本地长期运行）
    python v13c_dashboard_v2.py --config=custom.yaml # 指定配置文件

Exit codes:
    0 — 成功
    1 — 严重错误（无法生成输出）
    2 — 部分失败（有资产回退到模拟数据）
"""

import argparse
import json
import logging
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 第三方依赖（优雅降级）
# ---------------------------------------------------------------------------
try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# ---------------------------------------------------------------------------
# 配置数据类
# ---------------------------------------------------------------------------

@dataclass
class DashboardConfig:
    """运行时配置，支持从 YAML/JSON 加载或默认值。"""
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


# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 模块 1: Data Fetcher
# ---------------------------------------------------------------------------

class DataFetcher:
    """负责从 yfinance 拉取资产数据，失败时回退到模拟数据。"""

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
        拉取单个资产。
        返回: (prices_list, is_real)
        is_real=True 表示真实数据，False 表示模拟回退。
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

                # 处理 yfinance 新旧格式兼容性
                if pd is not None and isinstance(df.columns, pd.MultiIndex):
                    prices = df["Close"][ticker].dropna().tolist()
                else:
                    prices = df["Close"].dropna().tolist()

                if len(prices) >= 60:
                    trimmed = prices[-self.cfg.history_days:]
                    self.log.info(f"  ✅ {name}: {len(trimmed)} days (real)")
                    return trimmed, True
                else:
                    raise ValueError(f"Only {len(prices)} days available (< 60)")

            except Exception as e:
                self.log.warning(f"  ⚠️ {name} attempt {attempt}/{self.cfg.max_retries_yf}: {e}")
                if attempt < self.cfg.max_retries_yf:
                    time.sleep(self.cfg.retry_delay_seconds)
                else:
                    break

        # 回退: 模拟数据
        simulated = self._generate_simulated(name)
        self.log.warning(f"  ⚠️ {name}: fallback to simulated data ({len(simulated)} days)")
        return simulated, False

    def _generate_simulated(self, name: str) -> List[float]:
        import random
        random.seed(hash(name) % 2**31)
        p = 100.0
        prices = []
        for _ in range(self.cfg.history_days):
            p *= (1 + random.gauss(self.cfg.simulated_data_bias, self.cfg.simulated_data_volatility))
            prices.append(p)
        return prices

    def fetch_all(self) -> Tuple[Dict[str, List[float]], Dict[str, bool]]:
        """拉取全部资产，返回 (data_dict, real_flag_dict)。"""
        self.log.info("[DataFetcher] Pulling %d assets from yfinance...", len(self.cfg.assets))
        data: Dict[str, List[float]] = {}
        real_flags: Dict[str, bool] = {}
        for name, ticker in self.cfg.assets.items():
            prices, is_real = self.fetch_single(name, ticker)
            if prices is not None:
                data[name] = prices
                real_flags[name] = is_real
        return data, real_flags


# ---------------------------------------------------------------------------
# 模块 2: PSI Engine
# ---------------------------------------------------------------------------

class PSIEngine:
    """计算 PSI 三维度 (Material / Fragmentation / Disengagement) 及 UPSI。"""

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
        """返回 (psi, material_z, fragmentation_z, disengagement_z)。"""
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
        """全球 UPSI = 等权平均各资产 PSI。"""
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


# ---------------------------------------------------------------------------
# 模块 3: Alert System
# ---------------------------------------------------------------------------

class AlertSystem:
    """基于阈值检测并输出告警信息，支持 webhook 扩展。"""

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger

    def check(self, current_upsi: float, current_psi: Dict[str, float]) -> Dict[str, Any]:
        """检查告警条件，返回结构化告警信息。"""
        alerts = []
        level = "OK"

        # 资产级告警
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
        """发送 webhook 告警（如配置了 webhook_url）。"""
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


# ---------------------------------------------------------------------------
# 模块 4: Renderer
# ---------------------------------------------------------------------------

class Renderer:
    """生成 HTML Dashboard 和 JSON API 输出。"""

    def __init__(self, config: DashboardConfig, logger: logging.Logger):
        self.cfg = config
        self.log = logger

    def render_json(
        self,
        asset_data: Dict[str, List[float]],
        asset_psi: Dict[str, List[float]],
        upsi_series: List[float],
        real_flags: Dict[str, bool],
        alert: Dict[str, Any],
    ) -> Dict[str, Any]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_upsi = upsi_series[-1] if upsi_series else 0.0
        current_psi = {name: (psi[-1] if psi else 0.0) for name, psi in asset_psi.items()}

        return {
            "generated_at": now,
            "version": "v13c",
            "mode": "cloud",
            "current_upsi": round(current_upsi, 3),
            "upsi_status": self._status_text(current_upsi),
            "upsi_series": [round(v, 3) for v in upsi_series],
            "asset_psi": {k: round(v, 3) for k, v in current_psi.items()},
            "alert": alert,
            "real_data_flags": real_flags,
            "real_data_ratio": round(sum(1 for v in real_flags.values() if v) / len(real_flags), 2) if real_flags else 0,
            "config": {
                "history_days": self.cfg.history_days,
                "alert_threshold_upsi": self.cfg.alert_threshold_upsi,
                "assets_count": len(self.cfg.assets),
            },
        }

    def render_html(
        self,
        asset_data: Dict[str, List[float]],
        asset_psi: Dict[str, List[float]],
        upsi_series: List[float],
        real_flags: Dict[str, bool],
        alert: Dict[str, Any],
    ) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_upsi = upsi_series[-1] if upsi_series else 0.0
        current_psi = {name: (psi[-1] if psi else 0.0) for name, psi in asset_psi.items()}
        upsi_class = self._css_class(current_upsi)
        upsi_status = self._status_text(current_upsi)

        # 历史数据（最近 100 天用于图表）
        hist_len = min(100, len(upsi_series))
        hist_dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(hist_len - 1, -1, -1)]
        hist_upsi = upsi_series[-hist_len:]

        # 热力图
        heatmap_assets = list(self.cfg.assets.keys())
        heatmap_values = [round(current_psi.get(a, 0), 2) for a in heatmap_assets]
        heatmap_labels = [a.replace(".", " ") for a in heatmap_assets]
        heat_colors = [self._heat_color(v) for v in heatmap_values]

        # 告警资产列表
        alert_assets = alert.get("alert_assets", [])

        # 全部资产排名
        sorted_assets = sorted(current_psi.items(), key=lambda x: x[1])

        html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UPSI Dashboard v13c | Global Pressure Index</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
body{{font-family:-apple-system,"PingFang SC","Segoe UI",sans-serif;background:#f5f6fa;color:#2c3e50;margin:0;padding:20px;}}
.container{{max-width:1200px;margin:0 auto;}}
h1{{color:#2c3e50;font-size:28px;margin-bottom:4px;font-weight:600;}}
.subtitle{{color:#7f8c8d;font-size:13px;margin-bottom:24px;}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-bottom:24px;}}
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
table{{width:100%;border-collapse:collapse;font-size:13px;}}
th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #ecf0f1;}}
th{{background:#f8f9fa;color:#7f8c8d;font-weight:600;font-size:11px;text-transform:uppercase;}}
tr:hover{{background:#f8f9fa;}}
.tag{{display:inline-block;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:600;color:#fff;}}
.tag-alert{{background:#c0392b;}} .tag-warn{{background:#f39c12;}} .tag-ok{{background:#27ae60;}}
.footer{{text-align:center;color:#95a5a6;font-size:12px;margin-top:20px;padding-bottom:20px;}}
.info-box{{background:#e8f4f8;border-left:3px solid #3498db;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;color:#2c3e50;margin-bottom:16px;}}
.simulated{{color:#e74c3c;font-size:11px;}}
</style>
</head>
<body>
<div class="container">
<h1>🌍 UPSI 全球压力指数 Dashboard v13c</h1>
<div class="subtitle">{len(self.cfg.assets)} 全球资产 | 生成于 {now} | 真实数据比例: {sum(1 for v in real_flags.values() if v)}/{len(real_flags)}</div>

<div class="info-box">
  <b>UPSI 统一公式:</b> UPSI = 0.40 × Material(回撤) + 0.30 × Fragmentation(波动) + 0.30 × Disengagement(动量衰减)<br>
  阈值: UPSI &lt; {self.cfg.alert_threshold_upsi} 为警报状态，UPSI &lt; 0 为关注状态
</div>

<div class="kpi-grid">
  <div class="kpi {upsi_class}">
    <div class="kpi-num {upsi_class}">{current_upsi:+.2f}</div>
    <div class="kpi-label">全球 UPSI (最新)</div>
    <span class="kpi-status status-{upsi_class}">{upsi_status}</span>
  </div>
  <div class="kpi {'alert' if len(alert_assets) >= self.cfg.alert_assets_count_critical else ('warn' if alert_assets else 'ok')}">
    <div class="kpi-num {'alert' if len(alert_assets) >= self.cfg.alert_assets_count_critical else ('warn' if alert_assets else 'ok')}">{len(alert_assets)}</div>
    <div class="kpi-label">警报资产数 (PSI &lt; {self.cfg.alert_threshold_asset})</div>
  </div>
  <div class="kpi {'alert' if alert['level'] == 'CRITICAL' else ('warn' if alert['level'] == 'WARNING' else 'ok')}">
    <div class="kpi-num {'alert' if alert['level'] == 'CRITICAL' else ('warn' if alert['level'] == 'WARNING' else 'ok')}">{alert['level']}</div>
    <div class="kpi-label">告警级别</div>
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

<div class="section">
<h2>🔥 {len(self.cfg.assets)} 资产 PSI 热力图 (当前)</h2>
<div class="heatmap-grid">
"""
        for label, val, color in zip(heatmap_labels, heatmap_values, heat_colors):
            sim_badge = '<span class="simulated">[SIM]</span>' if not real_flags.get(heatmap_assets[heatmap_labels.index(label)], True) else ''
            html += f'  <div class="heatmap-item" style="background:{color}">{label}{sim_badge}<div class="heatmap-value">{val:+.2f}</div></div>\n'

        html += """</div>
</div>

<div class="section">
<h2>⚠️ 警报资产列表 (PSI &lt; """ + str(self.cfg.alert_threshold_asset) + """)</h2>
<table>
<tr><th>资产</th><th>当前 PSI</th><th>状态</th><th>数据来源</th></tr>
"""
        if alert_assets:
            for name, psi_val in alert_assets[:20]:
                tag_class = "tag-alert" if psi_val < -1.0 else "tag-warn"
                tag_text = "严重" if psi_val < -1.0 else "警报"
                data_src = "真实" if real_flags.get(name, False) else "模拟"
                html += f'<tr><td>{name}</td><td>{psi_val:+.2f}</td><td><span class="tag {tag_class}">{tag_text}</span></td><td>{data_src}</td></tr>\n'
        else:
            html += '<tr><td colspan="4" style="text-align:center;color:#7f8c8d;">当前无警报资产 ✅</td></tr>\n'

        html += """</table>
</div>

<div class="section">
<h2>📊 全部资产 PSI 排名</h2>
<table>
<tr><th>排名</th><th>资产</th><th>当前 PSI</th><th>状态</th><th>数据来源</th></tr>
"""
        for rank, (name, psi_val) in enumerate(sorted_assets, 1):
            if psi_val < self.cfg.alert_threshold_asset:
                status = '<span class="tag tag-alert">警报</span>'
            elif psi_val < 0:
                status = '<span class="tag tag-warn">关注</span>'
            else:
                status = '<span class="tag tag-ok">正常</span>'
            data_src = "真实" if real_flags.get(name, False) else "模拟"
            html += f'<tr><td>{rank}</td><td>{name}</td><td>{psi_val:+.2f}</td><td>{status}</td><td>{data_src}</td></tr>\n'

        html += f"""</table>
</div>

<div class="footer">
  UPSI Dashboard v13c | 数据来源: yfinance ({len(self.cfg.assets)} 资产) | 更新频率: 每4小时<br>
  部署: GitHub Actions + GitHub Pages | 局限: yfinance 数据有延迟; 部分资产可能使用模拟数据<br>
  生成时间: {now}
</div>
</div>

<script>
const upsiLabels = {json.dumps(hist_dates)};
const upsiValues = {json.dumps([round(v, 3) for v in hist_upsi])};
const alertLine = upsiValues.map(() => {self.cfg.alert_threshold_upsi});

const ctx = document.getElementById('upsiChart').getContext('2d');
new Chart(ctx, {{
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


# ---------------------------------------------------------------------------
# 主控流程
# ---------------------------------------------------------------------------

class DashboardApp:
    """编排各模块的主应用类。"""

    def __init__(self, config: DashboardConfig):
        self.cfg = config
        self.log = setup_logging(config.log_level)
        self.fetcher = DataFetcher(config, self.log)
        self.engine = PSIEngine(config, self.log)
        self.alerts = AlertSystem(config, self.log)
        self.renderer = Renderer(config, self.log)

    def run_once(self) -> int:
        """单次运行，返回 exit code。"""
        self.log.info("=" * 60)
        self.log.info("UPSI Dashboard v13c — Starting (mode=once)")
        self.log.info("=" * 60)

        try:
            # 1. Fetch
            asset_data, real_flags = self.fetcher.fetch_all()
            if not asset_data:
                self.log.error("No asset data available. Aborting.")
                return 1

            # 2. Compute PSI
            self.log.info("[PSIEngine] Computing PSI for %d assets...", len(asset_data))
            asset_psi: Dict[str, List[float]] = {}
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
            # 尝试生成降级输出
            try:
                fallback = {
                    "generated_at": datetime.now().isoformat(),
                    "version": "v13c",
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
        """守护模式：循环运行。"""
        self.log.info("[Daemon] Starting with interval=%.1f hours", self.cfg.daemon_interval_hours)
        while True:
            self.run_once()
            sleep_seconds = self.cfg.daemon_interval_hours * 3600
            self.log.info("[Daemon] Sleeping %.0f seconds...", sleep_seconds)
            time.sleep(sleep_seconds)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="UPSI Dashboard v13c")
    parser.add_argument("--mode", choices=["once", "daemon"], default="once",
                        help="Run mode: once (default) or daemon")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to YAML or JSON config file")
    parser.add_argument("--output-dir", type=str, default=".",
                        help="Output directory for HTML and JSON")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    # 加载配置
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

    # CLI 覆盖
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
