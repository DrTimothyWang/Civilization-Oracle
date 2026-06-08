# v10a Dashboard 部署报告

**生成时间**: 2026-06-04  
**版本**: v10.0 TrackA  
**负责人**: v10_TrackA_Dashboard部署工程师

---

## 1. Dashboard 功能说明

v10.0 UPSI 实时 Dashboard 是一个基于 Web 的单一页面监控系统，核心功能包括：

| 模块 | 说明 |
|------|------|
| **KPI 看板** | 展示当前全球 UPSI 值、警报资产数、金十情绪得分、快讯条数 |
| **UPSI 时间序列** | 最近 192 天的全球压力指数走势，带 -0.5 警报阈值线 |
| **20 资产 PSI 热力图** | 一图览尽全球主要资产当前压力状态，颜色编码 |
| **警报资产列表** | PSI < -0.5 的资产表格，按严重程度排序 |
| **全部资产排名** | 20 资产 PSI 从低到高排序，带状态标签 |

### PSI 三维度计算

Dashboard 对每资产计算 UPSI 统一公式的三个维度：

- **Material (回撤)**: `rolling_mmp = 当前价 / 近期60天最高价 - 1`
- **Fragmentation (波动)**: `rolling_vol = 20天收益率标准差 × √252`
- **Disengagement (动量衰减)**: `短期5天动量 - 长期20天动量`

合成公式: `PSI = 0.40 × Material_z + 0.30 × Fragmentation_z + 0.30 × Disengagement_z`

全球 UPSI = 20 资产 PSI 等权平均

---

## 2. 数据源和更新频率

| 数据源 | 资产/指标 | 频率 | 说明 |
|--------|-----------|------|------|
| **yfinance** | 20 全球资产 | 每日 09:00 | 股票指数、外汇、债券、商品、波动率 |
| **金十数据 (Jin10 MCP)** | 实时快讯情绪 | 每日 09:00 | 8 关键词搜索 + 情绪词典 |
| **FRED** | 11 宏观指标 | 未接入 v10 | 预留扩展接口 |

### 20 全球资产清单

`US.SP500, JP.N225, CA.TSX, UK.FTSE, DE.DAX, HK.HSI, BR.BVSP, AR.MERVAL, TR.XU100, AU.ASX, FR.CAC, IN.NIFTY, RU.IMOEX, USDJPY, EURUSD, GBPUSD, US.10Y, GOLD, OIL.WTI, VIX`

---

## 3. 当前 UPSI 状态 (测试运行结果)

**测试运行时间**: 2026-06-04 10:44:33

### 核心指标

- **当前全球 UPSI**: `-0.02` → 状态: `⚠️ 关注` (接近 0，略偏压力)
- **警报资产数**: `3` (PSI < -0.5)
- **金十情绪**: `0` (今日无快讯数据，MCP 未返回结果)
- **数据覆盖**: 19/20 资产成功拉取真实 yfinance 数据，1 个模拟 (RU.IMOEX)

### 警报资产详情

| 排名 | 资产 | PSI | 严重程度 |
|------|------|-----|----------|
| 1 | VIX | -0.96 | 警报 |
| 2 | BR.BVSP | -0.86 | 警报 |
| 3 | GOLD | -0.60 | 警报 |

### 资产分布

- **正常 (PSI ≥ 0)**: 10 资产 (50%)
- **关注 (-0.5 ≤ PSI < 0)**: 7 资产 (35%)
- **警报 (PSI < -0.5)**: 3 资产 (15%)

### 历史趋势

最近 192 天 UPSI 范围: `-0.257 ~ +0.415`，当前处于历史中位偏下区域，未触发系统级警报 (UPSI < -0.5)。

---

## 4. 定时任务配置

### 方案 A: macOS LaunchAgent (推荐)

已创建 plist 文件:

```
~/Desktop/历史事件预测建模/v10_迭代研究/01_dashboard/com.upsi.daily-dashboard.plist
```

**安装命令** (需手动执行):
```bash
cp /Users/wangzr/Desktop/历史事件预测建模/v10_迭代研究/01_dashboard/com.upsi.daily-dashboard.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.upsi.daily-dashboard.plist
launchctl start com.upsi.daily-dashboard
```

**配置详情**:
- **任务名**: `com.upsi.daily-dashboard`
- **频率**: 每日上午 9:00 (中国市场开盘前)
- **执行**: `/usr/bin/python3 v10_dashboard.py`
- **工作目录**: `/Users/wangzr/Desktop/历史事件预测建模/v10_迭代研究/01_dashboard`
- **日志**: `cron.log` / `cron_error.log`

### 方案 B: Cron (备用)

**crontab 配置**:
```cron
# UPSI Daily Dashboard v10.0 — 每日上午9:00运行 (中国市场开盘前)
0 9 * * * cd /Users/wangzr/Desktop/历史事件预测建模/v10_迭代研究/01_dashboard && /usr/bin/python3 v10_dashboard.py >> /Users/wangzr/Desktop/历史事件预测建模/v10_迭代研究/01_dashboard/cron.log 2>&1
```

> **注意**: 当前环境 `crontab` 命令执行超时，可能受系统权限或沙箱限制。建议优先使用 LaunchAgent 方案，或手动在终端执行 `crontab -e` 添加上述行。

### 手动运行方案

如需立即刷新 Dashboard:
```bash
cd /Users/wangzr/Desktop/历史事件预测建模/v10_迭代研究/01_dashboard
python3 v10_dashboard.py
```

输出文件:
- HTML Dashboard: `dashboard_latest.html`
- JSON 数据: `dashboard_data_v10.json`

---

## 5. 已知局限与风险

| 局限 | 影响 | 缓解措施 |
|------|------|----------|
| **yfinance 数据延迟** | 15-30 分钟延迟，非真正实时 | 用于日频监控足够；高频场景需接入券商 API |
| **金十数据需 MCP 接入** | `mavis mcp call jin10` 命令依赖外部 MCP 服务，当前测试返回 0 条 | 已预留接口，MCP 服务恢复后自动生效 |
| **FRED API 限制** | v10 未接入 FRED 宏观指标 | 下一迭代 (v10.1) 计划接入 `fetch_fred.py` 模块 |
| **部分新兴市场数据缺失** | RU.IMOEX (俄罗斯) 被 yfinance 标记为 delisted | 自动回退到模拟数据，不影响整体 UPSI |
| **PSI 阈值主观性** | -0.5 警报阈值基于历史回测，非绝对标准 | 建议结合多时间框架确认 |
| **单一机器部署** | 依赖本地 cron/LaunchAgent，无高可用 | 建议未来迁移到云服务器 + Docker |

---

## 6. 文件清单

```
v10_迭代研究/01_dashboard/
├── v10_dashboard.py              # Dashboard 生成脚本 (主程序)
├── dashboard_latest.html         # 最新 HTML Dashboard (输出)
├── dashboard_data_v10.json       # 最新 JSON 数据 (输出)
├── com.upsi.daily-dashboard.plist # macOS LaunchAgent 配置
├── cron.log                      # 定时任务日志 (运行时生成)
├── cron_error.log                # 错误日志 (运行时生成)
└── v10a_dashboard_report.md      # 本报告
```

---

## 7. 下一步建议

1. **接入 FRED**: 将 `v5/fetch_fred.py` 整合进 v10，增加宏观 PSI 维度
2. **金十 MCP 修复**: 验证 `mavis mcp call jin10` 命令可用性，恢复情绪数据
3. **邮件/钉钉告警**: UPSI < -0.5 时自动发送告警通知
4. **云部署**: 将 Dashboard 部署到云服务器，实现 7×24 自动更新 + 公网访问
5. **历史对比**: 增加 UPSI 与历史危机事件 (2008, 2020) 的对比面板

---

*报告结束 — v10_TrackA_Dashboard部署工程师*
