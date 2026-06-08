"""Renderer — Generate HTML Dashboard and JSON API output."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from .config import DashboardConfig


class Renderer:
    """Generate HTML Dashboard and JSON API output."""

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
            "version": "v14d",
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

        # Historical data (last 100 days for chart)
        hist_len = min(100, len(upsi_series))
        hist_dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(hist_len - 1, -1, -1)]
        hist_upsi = upsi_series[-hist_len:]

        # Heatmap
        heatmap_assets = list(self.cfg.assets.keys())
        heatmap_values = [round(current_psi.get(a, 0), 2) for a in heatmap_assets]
        heatmap_labels = [a.replace(".", " ") for a in heatmap_assets]
        heat_colors = [self._heat_color(v) for v in heatmap_values]

        # Alert assets list
        alert_assets = alert.get("alert_assets", [])

        # All assets ranking
        sorted_assets = sorted(current_psi.items(), key=lambda x: x[1])

        html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UPSI Dashboard v14d | Global Pressure Index</title>
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
<h1>🌍 UPSI 全球压力指数 Dashboard v14d</h1>
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
            idx = heatmap_labels.index(label)
            sim_badge = '<span class="simulated">[SIM]</span>' if not real_flags.get(heatmap_assets[idx], True) else ''
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
  UPSI Dashboard v14d | 数据来源: yfinance ({len(self.cfg.assets)} 资产) | 更新频率: 每4小时<br>
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
