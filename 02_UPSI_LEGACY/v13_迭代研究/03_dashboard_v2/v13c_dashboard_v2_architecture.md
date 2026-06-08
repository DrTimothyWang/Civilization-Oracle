# Dashboard v2 云部署架构设计文档

**版本**: v13c — Dashboard Cloud Architecture  
**日期**: 2026-06-04  
**目标**: 将 UPSI Dashboard 从本地单机迁移至 24/7 云自动运行

---

## 1. 部署方案对比

| 方案 | 成本 | 可靠性 | 复杂度 | 定时触发 | 持久存储 | 公网访问 | 推荐度 |
|------|------|--------|--------|----------|----------|----------|--------|
| **GitHub Actions + gh-pages** | **免费** | ⭐⭐⭐⭐ | 低 | ✅ 原生支持 | Artifacts / gh-pages | ✅ 自动 | **★★★★★** |
| AWS Lambda (EventBridge) | 免费额度内 | ⭐⭐⭐⭐⭐ | 中高 | ✅ EventBridge | S3 / DynamoDB | ✅ API Gateway | ★★★☆☆ |
| Google Cloud Run + Scheduler | 免费额度内 | ⭐⭐⭐⭐⭐ | 中高 | ✅ Cloud Scheduler | Cloud Storage | ✅ 原生URL | ★★★☆☆ |
| Render (Web Service + Cron) | 免费 | ⭐⭐⭐ | 低 | ⚠️ 免费版休眠 | 磁盘 (非持久) | ✅ 原生URL | ★★☆☆☆ |
| Heroku (Scheduler) | 已取消免费版 | — | 中 | — | — | — | ☆☆☆☆☆ |
| Vercel (Serverless) | 免费 | ⭐⭐⭐ | 低 | ⚠️ 需外部触发 | 无原生 | ✅ 原生URL | ★★☆☆☆ |

### 1.1 方案详细分析

#### A. GitHub Actions + GitHub Pages (推荐)

**原理**: GitHub Actions 作为无服务器执行环境，按 cron 调度运行 Python 脚本，生成 HTML/JSON 后自动提交到 `gh-pages` 分支，GitHub Pages 提供免费静态托管。

**优势**:
- **完全免费**: 公共仓库 Actions 2000 分钟/月，Pages 无流量限制
- **零运维**: 无需服务器、Docker、IAM 配置
- **原生定时**: `schedule` 事件支持 cron 语法
- **版本控制**: 每次运行留痕，可回滚历史数据
- **公网访问**: `https://<user>.github.io/<repo>/dashboard_latest.html`

**劣势**:
- 单次运行最长 6 小时（Dashboard < 5 分钟，无影响）
- 仓库需公开（或付费私有 + Pages）
- 无原生数据库，历史数据需用 JSON/Artifacts 模拟

**成本估算**:
- 每日 6 次运行 × 5 分钟 = 30 分钟/天 ≈ 15 小时/月
- 远低于 2000 分钟免费额度

#### B. AWS Lambda + S3 + EventBridge

**原理**: Lambda 函数被 EventBridge 定时触发，拉取 yfinance 数据，计算 PSI，将 HTML 写入 S3 静态网站桶。

**优势**:
- 企业级可靠性，冷启动 < 1s
- S3 静态网站托管几乎无限流量
- 可扩展至 DynamoDB 存储历史时序

**劣势**:
- 需 AWS 账号、IAM 配置、S3 桶策略
- Lambda 层需打包 yfinance + pandas（体积大）
- 免费额度 1M 请求/月 + 400,000 GB-s，但配置复杂

#### C. Google Cloud Run + Cloud Scheduler + Cloud Storage

**优势**: 类似 AWS，但容器化部署更直观  
**劣势**: 需 GCP 账号、Cloud Run 服务配置、容器构建

#### D. Render / Heroku

**劣势**: 免费 Web Service 30 分钟无访问即休眠，不适合纯后台任务；Heroku 已取消免费 dyno。

---

## 2. 推荐方案: GitHub Actions + gh-pages

**决策理由**:
1. **零预算**: 项目明确无预算，GitHub 是唯一完全免费且不限流量的方案
2. **低复杂度**: 无需云服务商账号、IAM、网络配置
3. **足够可靠**: GitHub Actions 可用性 > 99%，对日频监控足够
4. **可扩展**: 未来如需数据库，可叠加 GitHub Releases / Artifacts / 外部免费 DB

---

## 3. 数据流架构

```
┌─────────────────┐     cron (每4小时)      ┌─────────────────┐
│  GitHub Actions │ ──────────────────────> │  ubuntu-latest  │
│   (scheduler)   │                       │   (runner)        │
└─────────────────┘                       └────────┬────────┘
                                                   │
                          ┌────────────────────────┼────────────────────────┐
                          │                        │                        │
                          ▼                        ▼                        ▼
                   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
                   │  yfinance   │          │  PSI Engine │          │  Renderer   │
                   │  (20资产)   │          │ (3维度计算)  │          │ (HTML+JSON) │
                   └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
                          │                        │                        │
                          │  失败 → 模拟数据回退    │                        │
                          │                        │                        │
                          └────────────────────────┴────────────────────────┘
                                                   │
                                                   ▼
                          ┌─────────────────────────────────────────────────────┐
                          │                  输出产物                              │
                          │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
                          │  │dashboard_   │  │dashboard_   │  │  gh-pages   │ │
                          │  │latest.html  │  │data_v2.json │  │  branch     │ │
                          │  └─────────────┘  └─────────────┘  └─────────────┘ │
                          └─────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
                          ┌─────────────────────────────────────────────────────┐
                          │              GitHub Pages 静态托管                    │
                          │   https://<user>.github.io/<repo>/dashboard.html    │
                          └─────────────────────────────────────────────────────┘
```

### 3.1 数据流说明

| 阶段 | 输入 | 处理 | 输出 | 容错 |
|------|------|------|------|------|
| **Fetch** | 20 资产 yfinance ticker | 下载最近 252 天收盘价 | 资产价格字典 | 失败资产用模拟数据填充 |
| **PSI Compute** | 价格序列 | Material / Fragmentation / Disengagement + z-score | 各资产 PSI 时序 | 空序列跳过 |
| **UPSI合成** | 20 资产 PSI | 等权平均 | 全球 UPSI 时序 | — |
| **Render** | PSI + UPSI + 元数据 | Jinja2 / f-string 模板 | HTML + JSON | 降级为纯文本输出 |
| **Deploy** | HTML + JSON | `git commit` 到 gh-pages | 公网可访问 URL | Actions 失败发邮件通知 |

---

## 4. 存储策略

### 4.1 当前需求

- **单次数据量**: 20 资产 × 252 天 ≈ 5,040 个浮点数 ≈ 40 KB JSON
- **历史累积**: 每日 6 次 × 365 天 ≈ 2,190 个快照/年
- **总存储**: ~85 MB/年（纯 JSON）

### 4.2 存储方案对比

| 方案 | 容量 | 持久性 | 查询能力 | 成本 | 适用场景 |
|------|------|--------|----------|------|----------|
| **gh-pages branch** | 1 GB | ⭐⭐⭐ | 无（静态文件） | 免费 | **HTML 托管首选** |
| **GitHub Artifacts** | 500 MB/仓库 | ⭐⭐⭐ | 无（需下载） | 免费 | 历史 JSON 归档 |
| **GitHub Releases** | 2 GB/文件 | ⭐⭐⭐⭐⭐ | 无（需下载） | 免费 | 月度/季度数据包 |
| **SQLite (repo内)** | 无限制 | ⭐⭐⭐ | SQL 查询 | 免费 | 需复杂历史查询时 |
| **JSON Append** | 无限制 | ⭐⭐⭐ | 线性扫描 | 免费 | 简单追加场景 |

### 4.3 推荐存储架构 (分层)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 实时数据 (Hot)                                     │
│  ├── dashboard_latest.html  → gh-pages (覆盖更新)              │
│  └── dashboard_data_v2.json → gh-pages (覆盖更新)            │
│  用途: 用户直接访问的最新面板                                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 近期历史 (Warm) — 可选                              │
│  ├── history/YYYY-MM-DD_HH.json → gh-pages (追加)            │
│  └── 保留最近 30 天快照                                       │
│  用途: 短期趋势回溯，超期自动清理                               │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 长期归档 (Cold) — 可选                              │
│  ├── 每月打包为 Release Asset                                 │
│  └── 如: upsi_history_2026-06.json                            │
│  用途: 学术研究、模型回测                                       │
└─────────────────────────────────────────────────────────────┘
```

**默认实现**: 仅 Layer 1（覆盖式最新数据），满足基本需求且最简单。  
**扩展实现**: 增加 Layer 2，每次运行将 JSON 以时间戳命名写入 `history/` 目录，保留 30 天后由 Actions 自动清理。

---

## 5. 告警机制

### 5.1 告警触发条件

| 级别 | 条件 | 动作 |
|------|------|------|
| **CRITICAL** | UPSI < -0.5 或 ≥ 5 资产 PSI < -0.5 | 邮件 + Webhook |
| **WARNING** | UPSI < 0 或 1-4 资产 PSI < -0.5 | Webhook 可选 |
| **INFO** | 数据拉取失败 ≥ 3 资产 | Actions 日志标记 |

### 5.2 告警通道实现

#### A. 邮件告警 (推荐，零成本)

利用 GitHub Actions 内置的邮件通知:
- Actions 工作流失败时，GitHub 自动邮件通知仓库所有者
- 在 workflow 中显式使用 `actions/github-script` 创建 Issue 作为告警记录

**进阶**: 使用 SendGrid / Mailgun 免费额度 (100 封/天)，通过 repository secret 注入 API key。

#### B. Webhook 告警

```yaml
# 在 workflow 中增加步骤
- name: Alert Webhook
  if: env.UPSI_ALERT == 'true'
  run: |
    curl -X POST ${{ secrets.ALERT_WEBHOOK_URL }} \
      -H "Content-Type: application/json" \
      -d '{"upsi": "'${UPSI_VALUE}'", "level": "critical"}'
```

用户可配置:
- Slack Incoming Webhook
- 钉钉机器人
- 企业微信
- 自建 HTTP 端点

#### C. GitHub Issues 告警 (内置、可追踪)

```yaml
- name: Create Alert Issue
  if: env.UPSI_ALERT == 'true'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: `🚨 UPSI Alert: ${process.env.UPSI_VALUE}`,
        body: `Triggered at ${new Date().toISOString()}`,
        labels: ['upsi-alert']
      })
```

### 5.3 推荐组合

**最小可行**: GitHub Actions 失败自动邮件 + 在 HTML 中显示告警状态（用户主动查看）  
**标准配置**: 增加 Webhook 支持（通过 Secrets 配置）  
**完整配置**: 增加 GitHub Issues 自动创建（可追踪、可讨论）

---

## 6. 免费 tier 可行性分析

### 6.1 GitHub 免费额度

| 服务 | 免费额度 | Dashboard 用量 | 余量 |
|------|----------|----------------|------|
| Actions 执行时间 | 2,000 分钟/月 | ~900 分钟/月 (6次/天 × 5min × 30天) | 55% |
| Actions 存储 (Artifacts) | 500 MB | ~50 MB (30天历史) | 90% |
| Pages 托管 | 1 GB | ~1 MB (HTML+JSON) | 99.9% |
| Pages 流量 | 100 GB/月 | < 1 GB (纯文本) | 99% |

### 6.2 外部依赖免费额度

| 服务 | 免费额度 | 是否足够 |
|------|----------|----------|
| yfinance | 无限制 (Yahoo Finance 非官方) | ✅ 足够 |
| SendGrid | 100 封/天 | ✅ 足够 |
| Slack Webhook | 无限制 | ✅ 足够 |

### 6.3 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| GitHub Actions 排队延迟 | 中 | 更新延迟 5-30 分钟 | 降低频率至每日 1-2 次 |
| yfinance 被封/IP限流 | 中 | 数据全部回退模拟 | 增加重试 + 随机 User-Agent |
| gh-pages 1GB 限制 | 低 | 无法追加历史 | 仅保留最新文件，历史放 Artifacts |
| Actions 2000分钟超限 | 低 | 计费 $0.008/分钟 | 优化运行时间 < 3 分钟 |

---

## 7. 架构决策记录 (ADR)

### ADR-001: 使用 GitHub Actions 替代 cron
- **状态**: 已接受
- **背景**: 本地 cron/LaunchAgent 依赖用户机器开机，且沙箱环境受限
- **决策**: 使用 GitHub Actions `schedule` 事件触发
- **后果**: 正：7×24 自动运行；负：需公开仓库或付费私有

### ADR-002: 使用 gh-pages 替代服务器托管
- **状态**: 已接受
- **背景**: 无预算购买云服务器，需公网可访问
- **决策**: 将 HTML 提交到 gh-pages 分支，利用 GitHub Pages 静态托管
- **后果**: 正：零成本、自动 HTTPS、全球 CDN；负：仅静态内容，无后端 API

### ADR-003: 使用 JSON 文件替代数据库
- **状态**: 已接受
- **背景**: 数据量小（< 1 MB），无需复杂查询
- **决策**: 用 JSON 文件存储历史，追加写入 gh-pages
- **后果**: 正：简单、无依赖；负：无索引、大数据量时查询慢（可未来迁移到 SQLite）

### ADR-004: 使用模拟数据回退替代中断
- **状态**: 已接受
- **背景**: yfinance 偶尔失败，不能因此中断整个流程
- **决策**: 单资产失败时生成模拟数据，标记为 simulated，继续计算 UPSI
- **后果**: 正：高可用；负：模拟数据可能降低准确性（已用随机游走+负偏模拟压力）

---

## 8. 未来扩展路径

| 阶段 | 扩展内容 | 触发条件 |
|------|----------|----------|
| **v13.1** | 增加 Layer 2 历史存储 (30天) | 用户需要短期回溯 |
| **v13.2** | 接入 FRED 宏观指标 | v5 模块复用 |
| **v13.3** | 邮件/Webhook 告警自动化 | UPSI 频繁触发阈值 |
| **v14** | 迁移至 AWS Lambda + S3 | GitHub 额度不足或需 < 1分钟延迟 |
| **v15** | 增加用户交互（时间范围选择） | 需前端 JS + 后端 API（可能需 Cloudflare Workers） |

---

*文档结束 — Dashboard_Cloud_Architect*
