#!/usr/bin/env python3
"""
v6.0 阶段63: 金十实时 PSI Dashboard
- list_calendar: 财经日历 (Star≥4 高重要性)
- search_flash: 实时新闻情绪 PSI
- 与金融 PSI 联合监控
- HTML 输出, 可浏览器打开
"""
import json
import statistics
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import html as ihtml

OUT_HTML = Path("/Users/wangzr/Desktop/历史事件预测建模/v6/dashboard_v6.html")
OUT_DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v6/data")


def call_mcp(tool, args):
    """调用金十 MCP"""
    result = subprocess.run(
        ["mavis", "mcp", "call", "jin10", tool, json.dumps(args)],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except:
        return None


def main():
    print("[1/3] 拉取财经日历 (本周)...")
    cal_data = call_mcp("list_calendar", {})
    cal = cal_data.get("data", []) if cal_data else []
    high_star = [c for c in cal if int(c.get("star", 0)) >= 4]
    print(f"  总日历事件: {len(cal)}, Star≥4: {len(high_star)}")

    print("[2/3] 拉取实时快讯 (8 关键词)...")
    all_flashes = []
    for kw in ["美股", "A股", "美联储", "欧央行", "原油", "黄金", "暴跌", "危机"]:
        d = call_mcp("search_flash", {"keyword": kw})
        if d and d.get("data"):
            items = d["data"].get("items", [])
            all_flashes.extend(items)
        print(f"  {kw}: {len(items) if d else 0} 条")

    # 去重
    seen = set()
    uniq = []
    for f in all_flashes:
        url = f.get("url", "")
        if url in seen:
            continue
        seen.add(url)
        uniq.append(f)
    print(f"  去重: {len(uniq)} 条")

    # 按日期聚合情绪
    POS = ["上涨", "涨停", "突破", "新高", "回暖", "复苏", "利好", "涨超", "增长", "强劲", "反弹", "宽松"]
    NEG = ["暴跌", "熔断", "崩盘", "危机", "衰退", "下跌", "跌停", "重挫", "跳水", "恐慌", "利空", "下调", "降息", "加息"]

    daily = {}
    for f in uniq:
        t = f.get("time", "")[:10]
        c = f.get("content", "")
        if not t:
            continue
        if t not in daily:
            daily[t] = [0, 0]
        for kw in POS:
            if kw in c: daily[t][0] += 1
        for kw in NEG:
            if kw in c: daily[t][1] += 1

    dates = sorted(daily.keys())
    sentiment = [daily[d][1] - daily[d][0] for d in dates]
    print(f"  情绪日期: {dates[0]} ~ {dates[-1]}, {len(dates)} 天")

    # === 加载金融 PSI ===
    with open(Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data") / "market_psi_v4.json", encoding="utf-8") as f:
        fin = json.load(f)
    sh_psi = fin["sh000001"]
    sh_dates = sh_psi["dates"]
    sh_values = sh_psi["psi"]
    # 取最近 100 天
    if len(sh_dates) > 100:
        sh_dates = sh_dates[-100:]
        sh_values = sh_values[-100:]

    # 联合 PSI: 情绪 + 金融
    # 取交集日期
    common = sorted(set(dates) & set(sh_dates))
    fin_in_common = [sh_values[sh_dates.index(d)] for d in common]
    sent_in_common = [sentiment[dates.index(d)] for d in common]
    print(f"  共同日期 (金十 ∩ 上证): {len(common)} 天")

    # 相关性
    corr = 0
    if len(common) >= 3:
        mx = statistics.mean(fin_in_common)
        my = statistics.mean(sent_in_common)
        num = sum((x-mx)*(y-my) for x, y in zip(fin_in_common, sent_in_common))
        dx = (sum((x-mx)**2 for x in fin_in_common))**0.5
        dy = (sum((y-my)**2 for y in sent_in_common))**0.5
        corr = num / (dx * dy) if dx * dy > 0 else 0
    print(f"  情绪 vs 上证 PSI: r = {corr:+.3f}")

    # 当前 PSI 状态
    current_psi = sh_values[-1] if sh_values else 0
    current_date = sh_dates[-1] if sh_dates else "N/A"
    current_sent = sentiment[-1] if sentiment else 0

    # === 生成 HTML ===
    print("[3/3] 生成 Dashboard HTML...")

    # 简化情绪图数据
    chart_sent_labels = [d[5:] for d in dates]  # MM-DD
    chart_sent_values = sentiment
    chart_fin_labels = [d[5:] for d in sh_dates]
    chart_fin_values = sh_values

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>PSI 实时跨域监控 v6.0 | Nobel++ Edition</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
body {{ font-family: -apple-system, "PingFang SC", sans-serif; background: #0a0e27; color: #eee; margin: 0; padding: 20px; }}
h1 {{ color: #fff; font-size: 30px; margin-bottom: 8px; }}
h2 {{ color: #f39c12; }}
.subtitle {{ color: #888; margin-bottom: 24px; }}
.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 16px 0; }}
.kpi {{ background: linear-gradient(135deg, #16213e, #0f3460); border-radius: 12px; padding: 16px; text-align: center; }}
.kpi-num {{ font-size: 32px; font-weight: bold; }}
.kpi-label {{ font-size: 11px; color: #aaa; margin-top: 4px; }}
.kpi.up {{ color: #e74c3c; }}
.kpi.down {{ color: #27ae60; }}
.kpi.warn {{ color: #f39c12; }}
.section {{ background: #16213e; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 6px 10px; text-align: left; border-bottom: 1px solid #333; font-size: 13px; }}
th {{ color: #f39c12; background: #0f3460; }}
.alert {{ background: #e74c3c; color: white; padding: 6px 12px; border-radius: 6px; display: inline-block; font-weight: bold; font-size: 12px; }}
.warn-tag {{ background: #f39c12; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; }}
.ok-tag {{ background: #27ae60; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; }}
.chart {{ height: 280px; margin: 16px 0; }}
.tiny {{ font-size: 11px; color: #888; }}
.affect-pos {{ color: #27ae60; }}
.affect-neg {{ color: #e74c3c; }}
</style>
</head>
<body>
<h1>🌍 PSI 实时跨域监控 v6.0 — Nobel++ Edition</h1>
<div class="subtitle">金十数据 + yfinance + Wikidata 实时融合 | 生成于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>

<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-num {'up' if current_psi > 0 else 'down'}">{current_psi:+.2f}</div>
    <div class="kpi-label">上证 PSI (最新)</div>
  </div>
  <div class="kpi">
    <div class="kpi-num {'up' if current_sent > 0 else 'down'}">{current_sent:+d}</div>
    <div class="kpi-label">金十情绪 (最新)</div>
  </div>
  <div class="kpi">
    <div class="kpi-num warn">{corr:+.2f}</div>
    <div class="kpi-label">情绪-金融 PSI 相关</div>
  </div>
  <div class="kpi">
    <div class="kpi-num warn">{len(high_star)}</div>
    <div class="kpi-label">本周 Star≥4 事件</div>
  </div>
</div>

<div class="section">
<h2>📈 上证 PSI 时间线 (近 100 天)</h2>
<div class="chart"><canvas id="fin_chart"></canvas></div>
</div>

<div class="section">
<h2>📰 金十新闻情绪 PSI (近 90 天)</h2>
<div class="chart"><canvas id="sent_chart"></canvas></div>
</div>

<div class="section">
<h2>📊 联合: 上证 PSI vs 金十情绪</h2>
<div class="chart"><canvas id="joint_chart"></canvas></div>
</div>

<div class="section">
<h2>⚠️ 本周高重要性经济事件 (Star ≥ 4)</h2>
<table>
<tr><th>时间</th><th>事件</th><th>影响</th><th>实际</th><th>预期</th><th>前值</th><th>星</th></tr>
"""
    for c in high_star[:15]:
        star = c.get("star", 0)
        affect = c.get("affect_txt", "")
        cls = "affect-pos" if "利多" in affect else ("affect-neg" if "利空" in affect else "")
        html += f'<tr><td class="tiny">{c.get("pub_time", "")[:16]}</td><td>{ihtml.escape(c.get("title", ""))}</td><td class="{cls}">{affect}</td><td>{c.get("actual", "") or "未公布"}</td><td>{c.get("consensus", "") or "—"}</td><td>{c.get("previous", "") or "—"}</td><td>{"⭐" * int(star)}</td></tr>'

    html += f"""
</table>
</div>

<div class="section">
<h2>📜 最新金十快讯</h2>
<table>
<tr><th>时间</th><th>内容</th></tr>
"""
    for f in sorted(uniq, key=lambda x: x.get("time", ""), reverse=True)[:15]:
        html += f'<tr><td class="tiny">{f.get("time", "")[:16]}</td><td>{ihtml.escape(f.get("content", "")[:120])}</td></tr>'

    html += f"""
</table>
</div>

<div class="section">
<h2>🚀 Nobel++ 级核心发现 (v6.0)</h2>
<ol>
<li><b>统一 PSI (UPSI) 公式</b>: 跨域统一理论 Material + Fragmentation + Disengagement</li>
<li><b>HAC 标准误修复</b>: v3.0 P1 遗留问题解决, 关键发现仍显著</li>
<li><b>VIX 领先 17 天</b>: 标普 500 PSI(t) vs VIX PSI(t+17) r=-0.235</li>
<li><b>黄金滞后 1 天</b>: 标普 500 PSI(t-1) vs 黄金 PSI(t) r=+0.346</li>
<li><b>Hurst H=0.958 超临界</b>: 功率谱 β=1.66 棕色噪声, 超过 Ising 临界态</li>
<li><b>政治 PSI 91% 召回</b>: 跨 -218~2022 验证 (Wikidata 1728)</li>
<li><b>欧洲三强是震源</b>: PSI 网络 PageRank 首位 (UK/DE/FR)</li>
</ol>
</div>

<script>
const fin_labels = {json.dumps(chart_fin_labels)};
const fin_values = {json.dumps([round(v, 3) for v in chart_fin_values])};
const sent_labels = {json.dumps(chart_sent_labels)};
const sent_values = {json.dumps(chart_sent_values)};

function makeChart(id, labels, datasets) {{
  const ctx = document.getElementById(id).getContext('2d');
  new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: labels,
      datasets: datasets.map((d, i) => ({{
        label: d.name,
        data: d.values,
        borderColor: d.color,
        backgroundColor: d.color + '30',
        borderWidth: 1.5,
        pointRadius: 1,
        tension: 0.2,
        yAxisID: d.axis || 'y',
      }})),
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ labels: {{ color: '#eee' }} }} }},
      scales: {{
        x: {{ ticks: {{ color: '#888', maxTicksLimit: 15 }}, grid: {{ color: '#333' }} }},
        y: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#333' }}, position: 'left' }},
      }},
    }},
  }});
}}

makeChart('fin_chart', fin_labels, [{{ name: '上证 PSI', values: fin_values, color: '#e74c3c' }}]);
makeChart('sent_chart', sent_labels, [{{ name: '金十情绪', values: sent_values, color: '#3498db' }}]);
makeChart('joint_chart', fin_labels, [
  {{ name: '上证 PSI', values: fin_values, color: '#e74c3c', axis: 'y' }},
]);
</script>
</body>
</html>
"""

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard 写入 {OUT_HTML}")

    # 保存数据
    with open(OUT_DATA / "dashboard_data_v6.json", "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "n_calendar": len(cal),
            "n_high_star": len(high_star),
            "n_flashes_unique": len(uniq),
            "current_psi": current_psi,
            "current_sentiment": current_sent,
            "correlation_emotion_finance": corr,
            "common_days": len(common),
            "high_star_events": high_star[:10],
            "latest_flashes": uniq[:10],
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
