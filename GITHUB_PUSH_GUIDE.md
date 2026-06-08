# GitHub 推送指南 - Civilization-Oracle

## 执行摘要

| 项目 | 状态 |
|------|------|
| 本地仓库路径 | `/Users/wangzr/Desktop/历史事件预测建模/` |
| 分支 | `main` |
| 提交数 | 4 |
| 跟踪文件 | 683 |
| 仓库大小 | ~23 MB (git) |
| GitHub CLI | ✅ 已安装 (v2.93.0, 临时路径) |
| GitHub 登录 | ❌ 需要手动完成 |
| 远程仓库 | ❌ 尚未创建 |
| SSH 密钥 | ✅ 已生成 (`~/.ssh/id_ed25519_github`) |

---

## 遇到的问题与解决方案

### 问题 1: GitHub CLI (`gh`) 未安装
- **原因**: 系统未预装 `gh`，且 `brew` 不可用
- **解决**: 从 GitHub Releases 手动下载 `gh_2.93.0_macOS_arm64.zip` 并解压到 `/tmp/gh_2.93.0_macOS_arm64/`
- **状态**: ✅ 已解决

### 问题 2: GitHub 未登录
- **原因**: `gh` 需要 OAuth 认证，自动化环境无法完成浏览器交互
- **解决**: 提供手动登录步骤（见下方"步骤 1"）
- **状态**: ⏳ 需用户手动完成

### 问题 3: 无 SSH 密钥
- **原因**: `~/.ssh/` 目录下无现有密钥
- **解决**: 已生成 ED25519 密钥对 `~/.ssh/id_ed25519_github`
- **状态**: ✅ 已解决

### 问题 4: 工作区未提交更改
- **原因**: 推送前存在未暂存的修改和未跟踪文件
- **解决**: 已自动提交两次（共 29 个文件，5534 行新增）
- **状态**: ✅ 已解决

---

## 推送步骤

### 步骤 1: 登录 GitHub（必需，二选一）

#### 方案 A: 使用 `gh` CLI 登录（推荐）
```bash
export PATH="/tmp/gh_2.93.0_macOS_arm64/bin:$PATH"
gh auth login --web
```
按提示在浏览器中完成授权。

#### 方案 B: 使用 SSH 密钥 + 手动创建仓库
1. 复制公钥:
```bash
cat ~/.ssh/id_ed25519_github.pub
```
2. 打开 https://github.com/settings/keys → "New SSH key"
3. 粘贴公钥，Title 填 `Civilization-Oracle Deploy Key`
4. 在 GitHub 网页创建仓库: https://github.com/new
   - Repository name: `Civilization-Oracle`
   - Description: `Unified Pressure Synchronization Index - Cross-domain civilizational crisis detection framework`
   - Visibility: **Public**
   - License: **MIT License**
   - 不要初始化 README（本地已有）

---

### 步骤 2: 执行推送脚本

完成登录后，在项目根目录执行:

```bash
cd "/Users/wangzr/Desktop/历史事件预测建模/"
./push_to_github.sh [你的GitHub用户名]
```

脚本会自动:
1. 检查 `gh` 登录状态
2. 创建仓库 `Civilization-Oracle`（如不存在）
3. 添加远程 origin
4. 推送 `main` 分支

---

### 步骤 3: 手动推送（如不使用脚本）

如果使用 SSH 方案 B，执行:
```bash
cd "/Users/wangzr/Desktop/历史事件预测建模/"
git remote add origin git@github.com:<你的用户名>/Civilization-Oracle.git
git branch -M main
git push -u origin main
```

---

## 推送后验证清单

访问 `https://github.com/<用户名>/Civilization-Oracle` 确认:

- [ ] 仓库页面可正常访问
- [ ] 文件数约 **683** 个
- [ ] 无 `.env`, `__pycache__/`, `node_modules/`, `.DS_Store` 等被忽略文件
- [ ] 无 API 密钥、密码等敏感信息泄露
- [ ] `.github/workflows/ci.yml` 存在（GitHub Actions 工作流）
- [ ] 提交历史包含 4 条记录:
  1. `cd2d636` Pre-push sync v2
  2. `cd97cd9` Pre-push sync
  3. `73b5a7b` Add GitHub Actions CI workflow
  4. `01bff26` Initial commit

---

## .gitignore 生效确认

以下文件/目录已被正确排除，不会推送到 GitHub:

| 类型 | 排除内容 |
|------|----------|
| 敏感信息 | `.env`, `*.key`, `*.pem`, `secrets/`, `credentials/` |
| Python 缓存 | `__pycache__/`, `*.pyc`, `.pytest_cache/` |
| 依赖目录 | `node_modules/`, `venv/`, `.venv/` |
| 大数据文件 | `*.csv`, `*.jsonl`, `*.parquet`, `*.h5`, `*.pkl`, `*.npy` |
| 临时文件 | `output/`, `tmp/`, `temp/`, `*.log` |
| 嵌套 git 仓库 | `01_TCM_UPSI_CORE/` |
| 历史遗留 API 密钥文件 | `02_UPSI_LEGACY/v4/api_caller.py` 等 |
| 大型归档 | `99_ARCHIVE/zips/`, `*.zip`, `*.tar.gz` |

---

## 仓库元数据

| 属性 | 值 |
|------|-----|
| 仓库名称 | `Civilization-Oracle` |
| 可见性 | Public |
| 许可证 | MIT |
| 描述 | Unified Pressure Synchronization Index - Cross-domain civilizational crisis detection framework |
| 默认分支 | `main` |
| 跟踪文件 | 683 |
| 总提交 | 4 |

---

## 文件位置

- 推送脚本: `/Users/wangzr/Desktop/历史事件预测建模/push_to_github.sh`
- 本指南: `/Users/wangzr/Desktop/历史事件预测建模/GITHUB_PUSH_GUIDE.md`
- SSH 私钥: `~/.ssh/id_ed25519_github`
- SSH 公钥: `~/.ssh/id_ed25519_github.pub`
- `gh` CLI: `/tmp/gh_2.93.0_macOS_arm64/bin/gh`
