# UPSI Dashboard v14d — Deployment Report

**Date**: 2026-06-04  
**Version**: v14d  
**Status**: ✅ Deployment package ready — awaiting user push to GitHub

---

## 1. What Was Done

### 1.1 Repository Structure Created

A complete, modular repository was prepared under:

```
v14_迭代研究/04_dashboard_deploy/
├── v14d_dashboard_repo/          ← Ready-to-push GitHub repo
│   ├── .github/
│   │   └── workflows/
│   │       └── dashboard.yml     ← GitHub Actions CI (schedule + manual)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py             ← DashboardConfig dataclass
│   │   ├── data_fetcher.py       ← yfinance data pulling + simulated fallback
│   │   ├── psi_engine.py         ← PSI / UPSI computation
│   │   ├── alert_system.py       ← Threshold alerts + webhook
│   │   ├── renderer.py           ← HTML + JSON generation
│   │   └── dashboard.py          ← Main orchestrator + CLI
│   ├── config/
│   │   └── config.yaml           ← External, editable configuration
│   ├── requirements.txt          ← Python dependencies
│   ├── README.md                 ← User-facing setup & deploy guide
│   ├── LICENSE                   ← MIT License
│   └── .gitignore
├── v14d_deploy_script.py         ← Interactive deployment helper
├── v14d_local_test_results.json  ← Local run validation report
└── v14d_deployment_report.md     ← This file
```

### 1.2 Code Modularization

The monolithic `v13c_dashboard_v2.py` was split into 6 focused modules:

| Module | Responsibility | Lines |
|--------|---------------|-------|
| `config.py` | Configuration dataclass (YAML/JSON loading) | ~60 |
| `data_fetcher.py` | yfinance download, retry logic, simulated fallback | ~120 |
| `psi_engine.py` | Returns, rolling MMP/SFD/EED, z-scores, UPSI | ~90 |
| `alert_system.py` | Threshold checks, webhook POST | ~70 |
| `renderer.py` | HTML dashboard (Chart.js), JSON API output | ~330 |
| `dashboard.py` | Orchestration, CLI entry point, logging setup | ~140 |

### 1.3 GitHub Actions Workflow Refined

Key improvements over v13c:

- **Python 3.10** (stable, widely available on `ubuntu-latest`)
- **pip cache** enabled via `actions/setup-python@v5`
- **Paths trigger** updated to new repo structure (`src/**`, `config/config.yaml`)
- **Artifact upload** retention: 30 days
- **Webhook & Issue creation** conditional on `ALERT_WEBHOOK_URL` secret
- **Daily summary job** runs only at 00:00 UTC to reduce minute usage
- **Concurrency group** prevents overlapping runs

### 1.4 Local Test Executed

A full local run was performed. Results:

- **Exit code**: 2 (PARTIAL_SUCCESS — 1 simulated asset)
- **Real data ratio**: 19/20 (95%)
- **Simulated asset**: `RU.IMOEX` (delisted from Yahoo Finance)
- **UPSI**: -0.014 (WARNING level — watch zone, not critical)
- **Alert assets**: VIX, BR.BVSP, GOLD (3 assets below -0.5 threshold)
- **Outputs**: `dashboard_latest.html` and `dashboard_data_v2.json` both generated successfully

All functional checks passed: data fetcher, PSI engine, alert system, renderer, JSON validity.

---

## 2. What Needs User Action

Since this environment cannot create GitHub repositories or push code, the user must complete the following steps:

### Step A — Create GitHub Repository (2 minutes)

1. Visit https://github.com/new
2. Name: `upsi-dashboard` (or preferred name)
3. Visibility: **Public** (required for free GitHub Pages & Actions)
4. Check **Add a README file**
5. Click **Create repository**

### Step B — Push Code (2 minutes)

**Option 1: Use the helper script (recommended)**

```bash
cd /Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/04_dashboard_deploy
python3 v14d_deploy_script.py
```

Follow the interactive prompts. The script will:
- Verify git is installed
- Initialize the local repo
- Ask for your GitHub username and repo name
- Set the remote origin
- Commit and push

**Option 2: Manual git commands**

```bash
cd /Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/04_dashboard_deploy/v14d_dashboard_repo
git init
git add .
git commit -m "Initial commit: UPSI Dashboard v14d"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/upsi-dashboard.git
git push -u origin main
```

### Step C — Enable GitHub Actions (1 minute)

1. Open your repo on GitHub: `https://github.com/YOUR_USERNAME/upsi-dashboard`
2. Click the **Actions** tab
3. If you see a banner saying "Workflows aren't being run on this forked repository", click **I understand my workflows, go ahead and enable them**

### Step D — Trigger First Run (1 minute)

1. In the Actions tab, click **UPSI Dashboard v14d** on the left
2. Click **Run workflow** → **Run workflow**
3. Wait for the green checkmark (≈ 3–5 minutes)

### Step E — Enable GitHub Pages (1 minute)

1. Go to **Settings → Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `gh-pages` / `(root)`
4. Click **Save**

> If `gh-pages` is not visible, wait for the first workflow run to complete successfully — the branch is created automatically by `peaceiris/actions-gh-pages@v4`.

### Step F — View Dashboard

```
https://YOUR_USERNAME.github.io/upsi-dashboard/dashboard_latest.html
```

---

## 3. Expected GitHub Actions Schedule & Output

### Schedule

| Trigger | Cron (UTC) | Beijing Time | Purpose |
|---------|-----------|--------------|---------|
| Scheduled | `0 */4 * * *` | 08:00, 12:00, 16:00, 20:00, 00:00, 04:00 | Auto-refresh every 4 hours |
| Manual | `workflow_dispatch` | On demand | Testing or emergency refresh |
| Push | On `main` push to `src/**` or `config/config.yaml` | Immediate | Auto-deploy after code/config changes |

### Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Live Dashboard | `gh-pages` branch → GitHub Pages | `dashboard_latest.html` (interactive Chart.js) |
| JSON Data | Artifact + `gh-pages` branch | `dashboard_data_v2.json` (machine-readable API) |
| Alert Issue | GitHub Issues (optional) | Auto-created when UPSI < -0.5 (max 1 per 24h) |
| Webhook Alert | Slack/DingTalk/WeChat (optional) | POST when UPSI < -0.5 |

---

## 4. Troubleshooting Guide

| Symptom | Likely Cause | Fix |
|---------|-----------|-----|
| **Actions tab shows no workflow** | YAML file not in `.github/workflows/` or syntax error | Verify `dashboard.yml` path; validate at https://www.yamllint.com/ |
| **Run fails at "Install dependencies"** | Network timeout or PyPI issue | Re-run job; check `requirements.txt` syntax |
| **All assets show "simulated"** | yfinance rate-limit or no internet | Wait 10 min and re-run; check Yahoo Finance availability |
| **gh-pages branch missing** | Workflow never succeeded | Trigger manual run, ensure green checkmark first |
| **Page shows 404** | Pages source not set to `gh-pages` | Go to Settings → Pages → select `gh-pages` branch |
| **Push asks for password repeatedly** | 2FA enabled on GitHub | Use a Personal Access Token (classic) as password |
| **Webhook alerts not sending** | Secret not configured or URL invalid | Add `ALERT_WEBHOOK_URL` in Settings → Secrets → Actions |
| **Duplicate alert issues created** | Normal — but script deduplicates within 24h | No action needed; old issues auto-prevent new ones |

---

## 5. Cost Estimate (GitHub Free Tier)

| Resource | Free Tier Limit | Dashboard Usage | Status |
|----------|----------------|-----------------|--------|
| GitHub Actions minutes | 2,000 min/month (public repos: unlimited) | ~5 min/run × 6 runs/day × 30 days = **900 min/month** | ✅ Well within limit |
| GitHub Pages | 1 GB storage, 100 GB bandwidth/month | ~2 MB HTML + JSON | ✅ Negligible |
| Artifacts | 500 MB storage | ~50 KB per run, 30-day retention | ✅ Negligible |
| Secrets | 100 per repo | 1 (`ALERT_WEBHOOK_URL`) | ✅ Negligible |

**Conclusion**: For a **public repository**, GitHub Actions is unlimited and free. For a **private repository**, 900 min/month is within the 2,000 min free allowance.

---

## 6. Security & Maintenance Notes

- **No API tokens hardcoded**: All secrets use GitHub Actions `secrets.*` context
- **No GitHub CLI required**: Standard git HTTPS push only
- **MIT License**: Compatible with academic and commercial use
- **Recommended maintenance**:
  - Check Actions tab weekly for failed runs
  - Review `config/config.yaml` monthly to update asset tickers if needed
  - Rotate Personal Access Tokens yearly if used for push authentication

---

## 7. Success Criteria Checklist

| Criterion | Status |
|-----------|--------|
| Complete repo structure ready to push | ✅ |
| README that a non-technical user can follow | ✅ |
| Local test passes (dashboard runs, generates HTML) | ✅ |
| Deployment script with clear instructions | ✅ |
| Modular code (separate files per component) | ✅ |
| External editable `config.yaml` | ✅ |
| GitHub Actions workflow (schedule + manual + push triggers) | ✅ |
| Proper error handling and logging | ✅ |
| MIT License included | ✅ |

---

*Report generated: 2026-06-04*  
*Next step: User runs `v14d_deploy_script.py` and completes Steps A–F above.*
