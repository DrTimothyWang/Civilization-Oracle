# Dashboard v2 部署指南

**版本**: v13c  
**目标**: 让非技术用户也能独立完成 UPSI Dashboard 的云部署  
**预计时间**: 15-20 分钟  
**前提**: 拥有 GitHub 账号（免费注册）

---

## 快速开始 (3 步)

```bash
# 1. 创建 GitHub 仓库并上传代码
# 2. 复制 workflow 文件到 .github/workflows/
# 3. 启用 GitHub Pages
# → 完成！Dashboard 将自动每 4 小时更新
```

---

## 详细步骤

### 步骤 1: 准备 GitHub 仓库

#### 1.1 注册/登录 GitHub
- 访问 https://github.com
- 如无账号，点击 **Sign up** 免费注册（只需邮箱）

#### 1.2 创建新仓库
1. 点击右上角 **+** → **New repository**
2. 填写信息:
   - **Repository name**: `upsi-dashboard`（或任意名称）
   - **Description**: `UPSI Global Pressure Index Dashboard`
   - **Visibility**: ⭐ 选择 **Public**（免费 Actions + Pages 必需）
   - ✅ 勾选 **Add a README file**
3. 点击 **Create repository**

#### 1.3 上传项目文件

**方式 A: 网页上传（推荐非技术用户）**
1. 在新仓库页面，点击 **Add file** → **Upload files**
2. 将以下文件拖入上传区域:
   - `v13c_dashboard_v2.py`
   - `v13c_dashboard_v2_architecture.md`
   - `v13c_deployment_guide.md`（本文件）
3. 点击 **Commit changes**

**方式 B: 命令行上传（熟悉 git 的用户）**
```bash
# 在本地项目目录执行
git init
git remote add origin https://github.com/YOUR_USERNAME/upsi-dashboard.git
git add .
git commit -m "Initial commit: UPSI Dashboard v13c"
git push -u origin main
```

---

### 步骤 2: 配置 GitHub Actions

#### 2.1 创建工作流目录
1. 在仓库主页，点击 **Add file** → **Create new file**
2. 文件名输入: `.github/workflows/upsi-dashboard.yml`
3. 将 `v13c_github_actions.yml` 的内容完整复制粘贴到编辑器
4. 点击 **Commit changes...** → **Commit new file**

> **注意**: 文件路径必须是 `.github/workflows/xxx.yml`，这是 GitHub Actions 的固定位置。

#### 2.2 验证工作流已加载
1. 点击仓库顶部 **Actions** 标签
2. 应看到名为 **UPSI Dashboard v13c** 的工作流
3. 此时可能显示 "This workflow has no runs yet"，这是正常的

---

### 步骤 3: 启用 GitHub Pages

#### 3.1 进入 Pages 设置
1. 点击仓库顶部 **Settings** 标签
2. 左侧菜单找到 **Pages**（在 Code and automation 下）

#### 3.2 配置构建源
1. **Source** 部分，选择 **Deploy from a branch**
2. **Branch** 下拉菜单选择 `gh-pages`
3. **Folder** 保持 `/ (root)`
4. 点击 **Save**

> **注意**: 首次运行工作流后才会生成 `gh-pages` 分支。如果此时看不到该分支，请先执行步骤 4 手动触发一次工作流，然后再回来设置。

#### 3.3 获取访问地址
- 保存后，页面会显示您的 Dashboard URL，格式为:
  ```
  https://YOUR_USERNAME.github.io/upsi-dashboard/
  ```
- 点击 **Visit site** 即可查看（首次可能需要 5-10 分钟部署）

---

### 步骤 4: 首次手动运行 (验证)

#### 4.1 触发工作流
1. 点击仓库顶部 **Actions** 标签
2. 点击左侧 **UPSI Dashboard v13c**
3. 点击右侧 **Run workflow** 下拉按钮
4. 保持默认参数，点击绿色 **Run workflow** 按钮

#### 4.2 观察运行状态
1. 点击新出现的运行记录（黄色圆圈表示进行中）
2. 展开 **build-dashboard** 任务，查看实时日志
3. 正常应看到:
   ```
   [DataFetcher] Pulling 20 assets from yfinance...
     ✅ US.SP500: 252 days (real)
     ...
   [PSIEngine] UPSI series length=192, current=-0.02
   [Renderer] HTML written to ...
   ```

#### 4.3 验证输出
- 运行完成后（绿色勾），访问 `https://YOUR_USERNAME.github.io/upsi-dashboard/dashboard_latest.html`
- 应看到带有 UPSI 图表的 Dashboard 页面

---

### 步骤 5: 配置告警 (可选)

#### 5.1 Webhook 告警 (Slack/钉钉/企业微信)

1. 获取 Webhook URL:
   - **Slack**: 在 Slack App 中创建 Incoming Webhook
   - **钉钉**: 在群设置 → 智能群助手 → 添加机器人 → 复制 Webhook
   - **企业微信**: 在群机器人设置中复制 Webhook

2. 添加到 GitHub Secrets:
   - 仓库 **Settings** → **Secrets and variables** → **Actions**
   - 点击 **New repository secret**
   - **Name**: `ALERT_WEBHOOK_URL`
   - **Secret**: 粘贴您的 Webhook URL
   - 点击 **Add secret**

3. 工作流会自动读取该 secret，当 UPSI < -0.5 时发送告警

#### 5.2 邮件告警
- **无需配置**: GitHub 默认会在工作流失败时邮件通知仓库所有者
- 如需额外收件人，在仓库 **Settings** → **Notifications** 中添加协作者

---

### 步骤 6: 自定义配置 (可选)

#### 6.1 创建配置文件
1. 在仓库中创建 `config.yaml`:
   ```yaml
   assets:
     US.SP500: "^GSPC"
     JP.N225: "^N225"
     # ... 其他资产
   history_days: 252
   alert_threshold_upsi: -0.5
   alert_threshold_asset: -0.5
   alert_assets_count_critical: 5
   log_level: "INFO"
   max_retries_yf: 3
   retry_delay_seconds: 2.0
   ```

2. 修改工作流文件，在运行命令中增加 `--config=config.yaml`

#### 6.2 调整运行频率
编辑 `.github/workflows/upsi-dashboard.yml` 中的 cron:
```yaml
# 每 4 小时 (默认)
cron: '0 */4 * * *'

# 每日 2 次 (节省分钟数)
cron: '0 8,20 * * *'

# 每日 1 次
cron: '0 8 * * *'
```

> cron 语法: `分 时 日 月 星期`，UTC 时间。北京时间 = UTC + 8。

---

## 故障排查

### 问题 1: Actions 页面看不到工作流
**原因**: 文件路径错误或 YAML 语法错误  
**解决**:
1. 确认文件在 `.github/workflows/` 目录下
2. 使用在线 YAML 校验工具检查语法: https://www.yamllint.com/

### 问题 2: 运行失败，提示 yfinance 错误
**原因**: Yahoo Finance 临时限制  
**解决**:
1. 等待 10 分钟后点击 **Re-run jobs** 重试
2. 检查日志中是否有 "fallback to simulated data"，这是正常降级行为

### 问题 3: gh-pages 分支未生成
**原因**: 工作流未成功运行  
**解决**:
1. 先手动触发一次工作流（步骤 4）
2. 确认运行成功（绿色勾）
3. 刷新 Settings → Pages，此时应能看到 `gh-pages` 分支

### 问题 4: 网页显示 404
**原因**: Pages 部署有延迟，或分支配置错误  
**解决**:
1. 确认 Settings → Pages 中选择了 `gh-pages` 分支
2. 等待 5-10 分钟后刷新
3. 检查仓库是否 Public（Private 仓库 Pages 需付费）

### 问题 5: 收到 "Actions 额度警告"
**原因**: 接近 2000 分钟/月限制  
**解决**:
1. 降低运行频率（改为每日 1-2 次）
2. 优化脚本运行时间（已优化至 < 5 分钟）
3. 公共仓库额度通常足够，检查是否有其他工作流占用

---

## 验证清单

部署完成后，请确认以下项目:

- [ ] 仓库已创建且为 **Public**
- [ ] `.github/workflows/upsi-dashboard.yml` 已上传
- [ ] `v13c_dashboard_v2.py` 已上传
- [ ] GitHub Actions 中能看到 **UPSI Dashboard v13c** 工作流
- [ ] 手动触发运行成功（绿色勾）
- [ ] Settings → Pages 已选择 `gh-pages` 分支
- [ ] 访问 `https://YOUR_USERNAME.github.io/upsi-dashboard/dashboard_latest.html` 能看到图表
- [ ] (可选) Webhook Secret 已配置

---

## 文件清单

```
upsi-dashboard/
├── .github/
│   └── workflows/
│       └── upsi-dashboard.yml      # GitHub Actions 工作流 (从 v13c_github_actions.yml 复制)
├── v13c_dashboard_v2.py            # Dashboard 主程序
├── config.yaml                     # (可选) 自定义配置
├── v13c_dashboard_v2_architecture.md  # 架构文档
└── v13c_deployment_guide.md        # 本部署指南
```

---

## 后续维护

| 维护项 | 频率 | 操作 |
|--------|------|------|
| 查看 Dashboard | 随时 | 打开 GitHub Pages URL |
| 检查运行状态 | 每周 | Actions 页面查看最近运行记录 |
| 更新资产列表 | 按需 | 修改 `config.yaml` 或代码中的 `ASSETS` |
| 清理旧 Artifacts | 每月 | Actions → Artifacts → 删除过期文件 |
| 更新 yfinance | 按需 | 工作流中 `pip install yfinance --upgrade` |

---

## 联系与支持

- **GitHub Issues**: 在仓库中创建 Issue 记录问题
- **Actions 日志**: 运行失败时，日志是最详细的诊断信息
- **文档**: 参考 `v13c_dashboard_v2_architecture.md` 了解技术细节

---

*指南结束 — 祝您部署顺利！*
