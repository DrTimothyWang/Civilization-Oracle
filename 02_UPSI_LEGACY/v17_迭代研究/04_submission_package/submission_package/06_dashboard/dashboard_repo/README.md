# 🌍 UPSI Global Pressure Index Dashboard

A modular, cloud-deployable dashboard that computes the **Unified Pressure State Index (UPSI)** across 20 global financial assets. UPSI combines three dimensions—Material (drawdown), Fragmentation (volatility), and Disengagement (momentum decay)—into a single early-warning indicator for systemic pressure. The dashboard auto-refreshes every 4 hours via GitHub Actions and publishes live results to GitHub Pages.

---

## 📦 What's Inside

| File / Folder | Purpose |
|---------------|---------|
| `src/` | Modular Python source code (data fetcher, PSI engine, alerts, renderer, orchestrator) |
| `config/config.yaml` | Editable asset list, thresholds, and runtime settings |
| `.github/workflows/dashboard.yml` | GitHub Actions CI workflow (schedule + manual trigger) |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |
| `LICENSE` | MIT License |

---

## 🚀 Quick Start (Local)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/upsi-dashboard.git
cd upsi-dashboard
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run locally

```bash
# Run once (generates HTML + JSON in current directory)
python -m src.dashboard --mode=once --config=config/config.yaml

# Or run in daemon mode (loops every 4 hours)
python -m src.dashboard --mode=daemon --config=config/config.yaml
```

### 4. View results

Open `dashboard_latest.html` in your browser, or serve it:

```bash
python -m http.server 8000
# Visit http://localhost:8000/dashboard_latest.html
```

---

## ☁️ Deploy to GitHub (One-Time Setup)

> **Prerequisites**: A free GitHub account and a public repository.

### Step 1 — Create a GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `upsi-dashboard` (or any name)
3. Choose **Public** (required for free GitHub Pages)
4. Check **Add a README**
5. Click **Create repository**

### Step 2 — Push this code

```bash
# Inside the upsi-dashboard folder
git init
git add .
git commit -m "Initial commit: UPSI Dashboard v14d"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/upsi-dashboard.git
git push -u origin main
```

> Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3 — Enable GitHub Actions

1. Open your repo on GitHub
2. Click the **Actions** tab
3. If prompted, click **I understand my workflows, go ahead and enable them**

### Step 4 — Enable GitHub Pages

1. Go to **Settings → Pages**
2. Under **Build and deployment → Source**, select **Deploy from a branch**
3. Under **Branch**, select `gh-pages` and folder `/ (root)`
4. Click **Save**

> The `gh-pages` branch is created automatically after the first workflow run. If you don't see it yet, trigger a manual run first (see Step 5).

### Step 5 — Trigger your first run

1. Go to **Actions → UPSI Dashboard v14d**
2. Click **Run workflow → Run workflow**
3. Wait for the green checkmark (≈ 3–5 minutes)

### Step 6 — View the live dashboard

```
https://YOUR_USERNAME.github.io/upsi-dashboard/dashboard_latest.html
```

The dashboard will now auto-update every 4 hours.

---

## ⚙️ Customize

Edit `config/config.yaml` to change assets, thresholds, or behavior:

```yaml
assets:
  US.SP500: "^GSPC"
  JP.N225: "^N225"
  # Add or remove tickers here

alert_threshold_upsi: -0.5   # UPSI below this triggers CRITICAL
alert_threshold_asset: -0.5  # Asset PSI below this counts as alert
history_days: 252            # Look-back window
```

After editing, commit and push:

```bash
git add config/config.yaml
git commit -m "Update config"
git push
```

The workflow will auto-run because `config/config.yaml` is in the `paths` trigger.

---

## 📊 Dashboard Features

- **KPI Cards**: Current UPSI, alert asset count, alert level, real-data ratio
- **Time-Series Chart**: Last 100 days of UPSI with alert threshold line
- **Heatmap**: 20-asset PSI color grid
- **Alert Table**: Assets in alert state with severity and data source
- **Ranking Table**: All assets sorted by PSI

---

## 🔔 Alerts (Optional)

### Webhook (Slack / DingTalk / WeChat Work)

1. Get a webhook URL from your messaging app
2. In your repo, go to **Settings → Secrets and variables → Actions → New repository secret**
3. Name: `ALERT_WEBHOOK_URL`
4. Value: your webhook URL
5. The workflow will auto-send alerts when UPSI < -0.5

### GitHub Issues

When UPSI drops below -0.5, the workflow automatically creates a labeled issue (once per 24 hours to avoid spam).

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Actions tab shows no workflow | Confirm `.github/workflows/dashboard.yml` exists and YAML syntax is valid |
| Run fails with yfinance error | Yahoo Finance may be rate-limiting; re-run manually in 10 minutes |
| gh-pages branch missing | Trigger one manual run first; the branch is created on success |
| Page shows 404 | Confirm Pages source is set to `gh-pages` branch; wait 5–10 minutes |
| Simulated data for all assets | Check internet connectivity; yfinance requires outbound HTTPS |

---

## 📄 License

MIT License — free for academic and commercial use. See [LICENSE](LICENSE).

---

*Built with ❤️ for the UPSI Project.*
