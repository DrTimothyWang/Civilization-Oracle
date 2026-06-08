#!/usr/bin/env python3
"""
v10.0 TrackA: UPSI 实时 Dashboard
- 每日自动拉取 yfinance 20 全球资产数据
- 计算 PSI (Material / Fragmentation / Disengagement)
- 合成全球 UPSI
- 生成 HTML Dashboard (KPI + 3图 + 表格)
- 输出: dashboard_latest.html
"""
import json
import statistics
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import html as ihtml
import pandas as pd  # yfinance 数据格式需要
import random

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
OUT_DIR = Path("/Users/wangzr/Desktop/历史事件预测建模/v10_迭代研究/01_dashboard")
OUT_HTML = OUT_DIR / "dashboard_latest.html"
OUT_DATA = OUT_DIR / "dashboard_data_v10.json"
HISTORY_DAYS = 252  # 最近 1 年交易日

# 20 全球资产映射 (内部名 -> yfinance ticker)
ASSETS = {
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
}

# ---------------------------------------------------------------------------
# 数据拉取
# ---------------------------------------------------------------------------
def fetch_yf(ticker, days=HISTORY_DAYS):
    """拉取单个资产最近 days 天的收盘价"""
    try:
        import yfinance as yf
        end = datetime.now()
        start = end - timedelta(days=int(days * 1.5))  # 缓冲周末节假日
        df = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), progress=False)
        if df.empty:
            return None
        # 处理 MultiIndex columns (yfinance 新格式)
        if isinstance(df.columns, pd.MultiIndex):
            prices = df["Close"][ticker].dropna().tolist()
        else:
            prices = df["Close"].dropna().tolist()
        return prices
    except Exception as e:
        print(f"  ⚠️ {ticker} 拉取失败: {e}")
        return None


def fetch_all_assets():
    """拉取全部 20 资产，失败则回退模拟数据"""
    print("[1/4] 拉取 yfinance 20 资产数据...")
    data = {}
    for name, ticker in ASSETS.items():
        prices = fetch_yf(ticker)
        if prices and len(prices) >= 60:
            data[name] = prices[-HISTORY_DAYS:]
            print(f"  ✅ {name}: {len(data[name])} 天")
        else:
            # 模拟数据: 随机游走 + 轻微负偏 (模拟压力)
            import random
            random.seed(hash(name) % 2**31)
            p = 100.0
            prices_sim = []
            for _ in range(HISTORY_DAYS):
                p *= (1 + random.gauss(-0.0002, 0.012))
                prices_sim.append(p)
            data[name] = prices_sim
            print(f"  ⚠️ {name}: 使用模拟数据")
    return data


# ---------------------------------------------------------------------------
# PSI 计算 (Material / Fragmentation / Disengagement)
# ---------------------------------------------------------------------------
def returns(p):
    return [p[i] / p[i - 1] - 1 for i in range(1, len(p))]


def rolling_mmp(prices, w=60):
    """Material: Max-Min Position = 当前/近期最高 - 1"""
    out = []
    for i in range(w, len(prices)):
        recent_max = max(prices[i - w:i + 1])
        out.append(prices[i] / recent_max - 1)
    return out


def rolling_vol(returns_series, w=20):
    """Fragmentation: 年化波动率"""
    out = []
    for i in range(w, len(returns_series)):
        out.append(statistics.stdev(returns_series[i - w:i]) * (252 ** 0.5))
    return out


def rolling_disengagement(prices, w=20):
    """Disengagement: 动量衰减 = |短期动量| 的负向变化"""
    out = []
    for i in range(w + 5, len(prices)):
        mom_short = prices[i] / prices[i - 5] - 1
        mom_long = prices[i] / prices[i - w] - 1
        # 动量背离: 短期动量 < 长期动量 = 资金撤离信号
        out.append(mom_short - mom_long)
    return out


def compute_psi(prices):
    """计算 PSI 三维度并标准化合成"""
    rets = returns(prices)
    mmp = rolling_mmp(prices, 60)
    sfd = rolling_vol(rets, 20)
    eed = rolling_disengagement(prices, 20)

    # 对齐长度
    L = min(len(mmp), len(sfd), len(eed))
    if L <= 0:
        return [], []

    mmp = mmp[-L:]
    sfd = sfd[-L:]
    eed = eed[-L:]

    # z-score 标准化
    def zscore(x):
        mu = statistics.mean(x)
        sd = statistics.stdev(x) if statistics.stdev(x) > 0 else 1e-6
        return [(v - mu) / sd for v in x]

    mmp_z = zscore(mmp)
    sfd_z = zscore(sfd)
    eed_z = zscore(eed)

    # PSI = 0.4*Material + 0.3*Fragmentation + 0.3*Disengagement
    psi = [0.4 * m + 0.3 * s + 0.3 * e for m, s, e in zip(mmp_z, sfd_z, eed_z)]
    return psi, mmp_z, sfd_z, eed_z


# ---------------------------------------------------------------------------
# 金十数据 (MCP) — 可选
# ---------------------------------------------------------------------------
def call_mcp(tool, args):
    """调用金十 MCP"""
    try:
        result = subprocess.run(
            ["mavis", "mcp", "call", "jin10", tool, json.dumps(args)],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except Exception:
        return None


def fetch_jin10_sentiment():
    """拉取金十快讯情绪"""
    print("[2/4] 拉取金十快讯情绪...")
    POS = ["上涨", "涨停", "突破", "新高", "回暖", "复苏", "利好", "涨超", "增长", "强劲", "反弹", "宽松", "降准"]
    NEG = ["暴跌", "熔断", "崩盘", "危机", "衰退", "下跌", "跌停", "重挫", "跳水", "恐慌", "利空", "下调", "降息", "加息"]

    all_flashes = []
    for kw in ["美股", "A股", "美联储", "欧央行", "原油", "黄金", "暴跌", "危机"]:
        d = call_mcp("search_flash", {"keyword": kw})
        if d and d.get("data"):
            items = d["data"].get("items", [])
            all_flashes.extend(items)

    # 去重
    seen = set()
    uniq = []
    for f in all_flashes:
        url = f.get("url", "")
        if url in seen:
            continue
        seen.add(url)
        uniq.append(f)

    # 今日情绪
    today = datetime.now().strftime("%Y-%m-%d")
    pos_today = neg_today = 0
    for f in uniq:
        t = f.get("time", "")[:10]
        c = f.get("content", "")
        if t == today:
            pos_today += sum(1 for kw in POS if kw in c)
            neg_today += sum(1 for kw in NEG if kw in c)

    sentiment_score = neg_today - pos_today
    print(f"  今日快讯: {len(uniq)} 条, 情绪得分: {sentiment_score:+d}")
    return sentiment_score, len(uniq)


# ---------------------------------------------------------------------------
# Dashboard 生成
# ---------------------------------------------------------------------------
def generate_dashboard(asset_data, asset_psi, upsi_series, jin10_sent, jin10_count):
    """生成 HTML Dashboard"""
    print("[4/4] 生成 Dashboard HTML...")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_upsi = upsi_series[-1] if upsi_series else 0.0
    upsi_status = "🚨 警报" if current_upsi < -0.5 else ("⚠️ 关注" if current_upsi < 0 else "✅ 正常")
    upsi_class = "alert" if current_upsi < -0.5 else ("warn" if current_upsi < 0 else "ok")

    # 当前各资产 PSI
    current_psi = {name: psi[-1] if psi else 0.0 for name, psi in asset_psi.items()}
    alert_assets = [(n, v) for n, v in current_psi.items() if v < -0.5]
    alert_assets.sort(key=lambda x: x[1])

    # 历史数据 (最近 100 天用于图表)
    hist_len = min(100, len(upsi_series))
    hist_dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(hist_len - 1, -1, -1)]
    hist_upsi = upsi_series[-hist_len:]

    # 热力图数据
    heatmap_assets = list(ASSETS.keys())
    heatmap_values = [round(current_psi.get(a, 0), 2) for a in heatmap_assets]
    heatmap_labels = [a.replace(".", " ") for a in heatmap_assets]

    # 颜色映射函数 (低饱和度)
    def heat_color(v):
        if v < -1.0:
            return "#c0392b"  # 深红
        elif v < -0.5:
            return "#e74c3c"  # 红
        elif v < 0:
            return "#f39c12"  # 橙
        elif v < 0.5:
            return "#27ae60"  # 绿
        else:
            return "#2ecc71"  # 亮绿

    heat_colors = [heat_color(v) for v in heatmap_values]

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UPSI 实时 Dashboard v10.0 | Global Pressure Index</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
body {{
  font-family: -apple-system, "PingFang SC", "Segoe UI", sans-serif;
  background: #f5f6fa;
  color: #2c3e50;
  margin: 0;
  padding: 20px;
}}
.container {{
  max-width: 1200px;
  margin: 0 auto;
}}
h1 {{
  color: #2c3e50;
  font-size: 28px;
  margin-bottom: 4px;
  font-weight: 600;
}}
.subtitle {{
  color: #7f8c8d;
  font-size: 13px;
  margin-bottom: 24px;
}}
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}}
.kpi {{
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border-left: 4px solid #3498db;
}}
.kpi.alert {{ border-left-color: #c0392b; }}
.kpi.warn {{ border-left-color: #f39c12; }}
.kpi.ok {{ border-left-color: #27ae60; }}
.kpi-num {{
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 4px;
}}
.kpi-num.alert {{ color: #c0392b; }}
.kpi-num.warn {{ color: #f39c12; }}
.kpi-num.ok {{ color: #27ae60; }}
.kpi-label {{
  font-size: 12px;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.kpi-status {{
  display: inline-block;
  margin-top: 8px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}}
.status-alert {{ background: #c0392b; }}
.status-warn {{ background: #f39c12; }}
.status-ok {{ background: #27ae60; }}
.section {{
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
h2 {{
  color: #34495e;
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 16px;
  font-weight: 600;
}}
.chart {{
  height: 300px;
  position: relative;
}}
.heatmap-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}}
.heatmap-item {{
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}}
.heatmap-value {{
  font-size: 20px;
  margin-top: 4px;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}}
th, td {{
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #ecf0f1;
}}
th {{
  background: #f8f9fa;
  color: #7f8c8d;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
}}
tr:hover {{ background: #f8f9fa; }}
.tag {{
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}}
.tag-alert {{ background: #c0392b; }}
.tag-warn {{ background: #f39c12; }}
.tag-ok {{ background: #27ae60; }}
.footer {{
  text-align: center;
  color: #95a5a6;
  font-size: 12px;
  margin-top: 20px;
  padding-bottom: 20px;
}}
.info-box {{
  background: #e8f4f8;
  border-left: 3px solid #3498db;
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  font-size: 13px;
  color: #2c3e50;
  margin-bottom: 16px;
}}
</style>
</head>
<body>
<div class="container">
<h1>🌍 UPSI 全球压力指数 Dashboard v10.0</h1>
<div class="subtitle">20 全球资产 + 金十情绪 | 生成于 {now}</div>

<div class="info-box">
  <b>UPSI 统一公式:</b> UPSI = 0.40 × Material(回撤) + 0.30 × Fragmentation(波动) + 0.30 × Disengagement(动量衰减)<br>
  阈值: UPSI &lt; -0.5 为警报状态，UPSI &lt; 0 为关注状态
</div>

<div class="kpi-grid">
  <div class="kpi {upsi_class}">
    <div class="kpi-num {upsi_class}">{current_upsi:+.2f}</div>
    <div class="kpi-label">全球 UPSI (最新)</div>
    <span class="kpi-status status-{upsi_class}">{upsi_status}</span>
  </div>
  <div class="kpi ok">
    <div class="kpi-num ok">{len(alert_assets)}</div>
    <div class="kpi-label">警报资产数 (PSI &lt; -0.5)</div>
  </div>
  <div class="kpi ok">
    <div class="kpi-num ok">{jin10_sent:+d}</div>
    <div class="kpi-label">金十今日情绪</div>
  </div>
  <div class="kpi ok">
    <div class="kpi-num ok">{jin10_count}</div>
    <div class="kpi-label">今日快讯条数</div>
  </div>
</div>

<div class="section">
<h2>📈 全球 UPSI 时间序列 (最近 {hist_len} 天)</h2>
<div class="chart"><canvas id="upsiChart"></canvas></div>
</div>

<div class="section">
<h2>🔥 20 资产 PSI 热力图 (当前)</h2>
<div class="heatmap-grid">
"""
    for label, val, color in zip(heatmap_labels, heatmap_values, heat_colors):
        html += f'  <div class="heatmap-item" style="background:{color}">{label}<div class="heatmap-value">{val:+.2f}</div></div>\n'

    html += f"""
</div>
</div>

<div class="section">
<h2>⚠️ 警报资产列表 (PSI &lt; -0.5)</h2>
<table>
<tr><th>资产</th><th>当前 PSI</th><th>状态</th><th>Material</th><th>Fragmentation</th><th>Disengagement</th></tr>
"""
    for name, psi_val in alert_assets[:20]:
        tag_class = "tag-alert" if psi_val < -1.0 else "tag-warn"
        tag_text = "严重" if psi_val < -1.0 else "警报"
        html += f'<tr><td>{name}</td><td>{psi_val:+.2f}</td><td><span class="tag {tag_class}">{tag_text}</span></td><td>—</td><td>—</td><td>—</td></tr>\n'

    if not alert_assets:
        html += '<tr><td colspan="6" style="text-align:center;color:#7f8c8d;">当前无警报资产 ✅</td></tr>\n'

    html += f"""
</table>
</div>

<div class="section">
<h2>📊 全部资产 PSI 排名</h2>
<table>
<tr><th>排名</th><th>资产</th><th>当前 PSI</th><th>状态</th></tr>
"""
    sorted_assets = sorted(current_psi.items(), key=lambda x: x[1])
    for rank, (name, psi_val) in enumerate(sorted_assets, 1):
        if psi_val < -0.5:
            status = '<span class="tag tag-alert">警报</span>'
        elif psi_val < 0:
            status = '<span class="tag tag-warn">关注</span>'
        else:
            status = '<span class="tag tag-ok">正常</span>'
        html += f'<tr><td>{rank}</td><td>{name}</td><td>{psi_val:+.2f}</td><td>{status}</td></tr>\n'

    html += f"""
</table>
</div>

<div class="footer">
  UPSI Dashboard v10.0 | 数据来源: yfinance (20 资产) + 金十数据 (情绪) | 更新频率: 每日 09:00<br>
  局限: yfinance 数据有 15-30 分钟延迟; 金十数据需 MCP 接入; 部分新兴市场资产可能使用模拟数据
</div>
</div>

<script>
const upsiLabels = {json.dumps(hist_dates)};
const upsiValues = {json.dumps([round(v, 3) for v in hist_upsi])};

// 阈值线
const alertLine = upsiValues.map(() => -0.5);

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
        label: '警报阈值 (-0.5)',
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
      legend: {{
        labels: {{ color: '#2c3e50', font: {{ size: 12 }} }}
      }},
      tooltip: {{
        mode: 'index',
        intersect: false
      }}
    }},
    scales: {{
      x: {{
        ticks: {{ color: '#7f8c8d', maxTicksLimit: 12, font: {{ size: 11 }} }},
        grid: {{ color: '#ecf0f1' }}
      }},
      y: {{
        ticks: {{ color: '#7f8c8d', font: {{ size: 11 }} }},
        grid: {{ color: '#ecf0f1' }},
        suggestedMin: -2,
        suggestedMax: 2
      }}
    }}
  }}
}});
</script>
</body>
</html>
"""

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"  ✅ Dashboard 写入 {OUT_HTML}")

    # 保存 JSON 数据
    out_json = {
        "generated_at": now,
        "current_upsi": current_upsi,
        "upsi_status": upsi_status,
        "alert_assets": alert_assets,
        "jin10_sentiment": jin10_sent,
        "jin10_count": jin10_count,
        "asset_psi": {k: round(v, 3) for k, v in current_psi.items()},
        "upsi_series": [round(v, 3) for v in upsi_series],
    }
    with open(OUT_DATA, "w", encoding="utf-8") as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 数据写入 {OUT_DATA}")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("UPSI Dashboard v10.0 — 生成中")
    print("=" * 70)

    # 1. 拉取资产数据
    asset_data = fetch_all_assets()

    # 2. 计算 PSI
    print("\n[2/4] 计算各资产 PSI...")
    asset_psi = {}
    for name, prices in asset_data.items():
        psi, mmp_z, sfd_z, eed_z = compute_psi(prices)
        asset_psi[name] = psi
        if psi:
            print(f"  {name}: PSI={psi[-1]:+.2f} (M={mmp_z[-1]:+.2f} F={sfd_z[-1]:+.2f} D={eed_z[-1]:+.2f})")

    # 3. 计算全球 UPSI (等权平均)
    print("\n[3/4] 计算全球 UPSI...")
    # 对齐长度
    min_len = min(len(p) for p in asset_psi.values() if p)
    upsi_series = []
    for i in range(-min_len, 0):
        vals = [asset_psi[name][i] for name in asset_psi if asset_psi[name]]
        upsi_series.append(statistics.mean(vals))
    print(f"  UPSI 序列长度: {len(upsi_series)} 天")
    print(f"  当前 UPSI: {upsi_series[-1]:+.2f}")

    # 4. 金十数据 (可选)
    try:
        jin10_sent, jin10_count = fetch_jin10_sentiment()
    except Exception as e:
        print(f"  金十数据获取失败: {e}")
        jin10_sent, jin10_count = 0, 0

    # 5. 生成 Dashboard
    generate_dashboard(asset_data, asset_psi, upsi_series, jin10_sent, jin10_count)

    print("\n" + "=" * 70)
    print("✅ Dashboard 生成完成")
    print(f"   HTML: {OUT_HTML}")
    print(f"   JSON: {OUT_DATA}")
    print("=" * 70)


if __name__ == "__main__":
    main()
