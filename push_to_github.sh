#!/bin/bash
# ============================================================
# Civilization-Oracle GitHub 推送脚本
# 用法: ./push_to_github.sh [github_username]
# ============================================================

set -euo pipefail

REPO_NAME="Civilization-Oracle"
DESCRIPTION="Unified Pressure Synchronization Index - Cross-domain civilizational crisis detection framework"
GITHUB_USER="${1:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()   { echo -e "${GREEN}[OK]${NC}   $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err()  { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查 gh CLI
GH_BIN="/tmp/gh_2.93.0_macOS_arm64/bin/gh"
if [ ! -x "$GH_BIN" ]; then
    log_err "gh CLI 未找到: $GH_BIN"
    echo "请先运行 gh 安装步骤，或手动在 https://github.com/cli/cli/releases 下载"
    exit 1
fi

export PATH="$(dirname "$GH_BIN"):$PATH"

# 检查登录状态
log_info "检查 GitHub 登录状态..."
if ! gh auth status &>/dev/null; then
    log_warn "未登录 GitHub。正在启动登录流程..."
    echo ""
    echo "请在浏览器中完成 GitHub 授权，或按 Ctrl+C 取消并使用手动方式。"
    echo ""
    gh auth login --web
fi

# 获取用户名（如果未提供）
if [ -z "$GITHUB_USER" ]; then
    GITHUB_USER=$(gh api user -q '.login' 2>/dev/null || true)
    if [ -z "$GITHUB_USER" ]; then
        log_err "无法获取 GitHub 用户名。请提供: ./push_to_github.sh <username>"
        exit 1
    fi
fi

log_info "GitHub 用户: $GITHUB_USER"

# 检查仓库是否已存在
log_info "检查远程仓库 '$REPO_NAME' 是否存在..."
if gh repo view "$GITHUB_USER/$REPO_NAME" &>/dev/null; then
    log_warn "仓库已存在: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    log_info "创建仓库 '$REPO_NAME' (public, MIT license)..."
    gh repo create "$REPO_NAME" \
        --public \
        --description "$DESCRIPTION" \
        --license MIT \
        --source=. \
        --remote=origin \
        --push
    log_ok "仓库创建并推送成功！"
    echo ""
    echo "仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
    exit 0
fi

# 仓库已存在，添加 remote 并推送
REMOTE_URL="git@github.com:$GITHUB_USER/$REPO_NAME.git"
log_info "添加远程 origin: $REMOTE_URL"

if git remote get-url origin &>/dev/null; then
    log_warn "远程 origin 已存在，更新 URL..."
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi

log_info "推送 main 分支到 origin..."
git push -u origin main

log_ok "推送完成！"
echo ""
echo "仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "验证清单:"
echo "  1. 访问仓库页面确认文件数 (~683)"
echo "  2. 检查 .gitignore 生效（无 .env, __pycache__, node_modules 等）"
echo "  3. 确认 GitHub Actions 工作流存在: .github/workflows/ci.yml"
echo "  4. 确认无敏感信息泄露"
