#!/bin/bash
# =============================================================================
# 丰悦云创官网部署脚本
# 支持 Vercel / GitHub Pages / 本地预览 三种方式
# =============================================================================

set -e

DOMAIN="fengyue-yunchuang"
WEBSITE_DIR="$(cd "$(dirname "$0")" && pwd)"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo_step() { echo -e "${GREEN}[步骤]${NC} $1"; }
echo_note() { echo -e "${YELLOW}[注意]${NC} $1"; }
echo_error() { echo -e "${RED}[错误]${NC} $1"; }

# -----------------------------------------------------------------------------
# 方式一：Vercel 部署（推荐，免费 + 全球CDN）
# -----------------------------------------------------------------------------
deploy_vercel() {
    echo_step "开始 Vercel 部署..."

    if ! command -v vercel &>/dev/null && ! command -v npx &>/dev/null; then
        echo_error "请先安装 Vercel CLI：npm install -g vercel"
        return 1
    fi

    local token="${VERCEL_TOKEN:-}"
    if [ -z "$token" ]; then
        echo_note "首次部署需要 Vercel Token："
        echo "  1. 访问 https://vercel.com/account/tokens"
        echo "  2. 点击 Create Token，名称随意（如 fengyue-deploy）"
        echo "  3. 复制 Token，运行时设置："
        echo ""
        echo "    export VERCEL_TOKEN='你的Token'"
        echo "    ./deploy.sh vercel"
        echo ""
        return 1
    fi

    cd "$WEBSITE_DIR"
    npx vercel --token "$token" --yes --prod 2>&1
    echo_step "Vercel 部署完成！"
}

# -----------------------------------------------------------------------------
# 方式二：GitHub Pages 部署（需要 GitHub 账号 + Git）
# -----------------------------------------------------------------------------
deploy_github_pages() {
    echo_step "开始 GitHub Pages 部署..."

    if ! command -v gh &>/dev/null; then
        echo_error "请先安装 GitHub CLI：brew install gh 或 https://cli.github.com/"
        return 1
    fi

    cd "$WEBSITE_DIR/.."

    # 初始化 GitHub Pages 分支
    git checkout --orphan gh-pages 2>/dev/null || true
    git rm -rf . --quiet 2>/dev/null || true
    cp website/index.html index.html
    cp website/vercel.json vercel.json 2>/dev/null || true
    echo "*.log" > .gitignore

    git add .
    git commit -m "Deploy: 丰悦云创官网 $(date '+%Y-%m-%d %H:%M')"

    # 启用 GitHub Pages
    echo_note "请确保你的 GitHub 仓库已设置 GitHub Pages："
    echo "  Settings → Pages → Source: Deploy from a branch → gh-pages"
    echo ""
    echo "手动推送到 GitHub："
    echo "  git push origin gh-pages"
    echo ""
    echo "部署后访问：https://你的用户名.github.io/仓库名/"
}

# -----------------------------------------------------------------------------
# 方式三：本地预览（局域网内手机/其他设备访问）
# -----------------------------------------------------------------------------
deploy_local() {
    echo_step "启动本地预览服务器..."

    local ip
    ip=$(hostname -I 2>/dev/null | awk '{print $1}' || ipconfig getifaddr en0 2>/dev/null)

    cd "$WEBSITE_DIR"
    echo_note "在浏览器打开："
    echo "  电脑访问：http://localhost:8080"
    [ -n "$ip" ] && echo "  手机访问：http://$ip:8080"
    echo ""
    echo_note "按 Ctrl+C 停止服务器"
    echo ""

    # Python 内置服务器，自动打开浏览器
    if command -v python3 &>/dev/null; then
        python3 -m http.server 8080
    elif command -v python &>/dev/null; then
        python -m SimpleHTTPServer 8080
    else
        echo_error "未找到 Python，无法启动本地服务器"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# 主入口
# -----------------------------------------------------------------------------
main() {
    echo ""
    echo "=========================================="
    echo "  丰悦云创科技 · 官网部署脚本"
    echo "=========================================="
    echo ""
    echo "部署方式："
    echo "  1) Vercel（推荐，免费全球CDN，即时生效）"
    echo "  2) GitHub Pages（需要GitHub账号）"
    echo "  3) 本地预览（手机/其他设备查看）"
    echo ""
    read -p "请选择 [1/2/3，默认 1]: " choice
    choice="${choice:-1}"

    case $choice in
        1) deploy_vercel ;;
        2) deploy_github_pages ;;
        3) deploy_local ;;
        *) echo_error "无效选择"; exit 1 ;;
    esac
}

main "$@"
