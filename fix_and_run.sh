#!/bin/bash
# ============================================
# 🎵 音乐播放器 - 环境修复和启动脚本
# ============================================

# 设置颜色（美化输出）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color（重置颜色）

# 清屏并显示标题
clear
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   🎵 音乐播放器 - 环境修复工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================
# 功能 1: 查找 Python
# ============================================
find_python() {
    echo -e "${YELLOW}[1/5] 查找 Python...${NC}"
    echo ""
    
    # 尝试不同的 Python 命令
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
        echo -e "${GREEN}✅ 找到: python${NC}"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        echo -e "${GREEN}✅ 找到: python3${NC}"
    elif command -v py &> /dev/null; then
        PYTHON_CMD="py"
        echo -e "${GREEN}✅ 找到: py${NC}"
    else
        echo -e "${RED}❌ 未找到 Python${NC}"
        echo ""
        echo -e "${YELLOW}请安装 Python:${NC}"
        echo "  1. 访问 https://www.python.org/downloads/"
        echo "  2. 下载并安装 Python 3.6+"
        echo "  3. 勾选 'Add Python to PATH'"
        echo "  4. 重新运行此脚本"
        echo ""
        read -p "按 Enter 键退出..."
        exit 1
    fi
    
    # 显示 Python 版本
    VERSION=$($PYTHON_CMD --version 2>&1)
    echo -e "${GREEN}✅ Python 版本: ${VERSION}${NC}"
    echo ""
}

# ============================================
# 功能 2: 检查 pip
# ============================================
check_pip() {
    echo -e "${YELLOW}[2/5] 检查 pip...${NC}"
    echo ""
    
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        echo -e "${GREEN}✅ pip 已安装${NC}"
    else
        echo -e "${YELLOW}⚠️ pip 未安装，正在安装...${NC}"
        $PYTHON_CMD -m ensurepip --upgrade
        echo -e "${GREEN}✅ pip 安装完成${NC}"
    fi
    echo ""
}

# ============================================
# 功能 3: 安装依赖
# ============================================
install_dependencies() {
    echo -e "${YELLOW}[3/5] 安装项目依赖...${NC}"
    echo ""
    
    # 升级 pip
    echo "📦 升级 pip..."
    $PYTHON_CMD -m pip install --upgrade pip -q
    
    # 安装 pygame
    echo "📦 安装 pygame..."
    if $PYTHON_CMD -m pip install pygame -q 2>/dev/null; then
        echo -e "${GREEN}✅ pygame 安装成功${NC}"
    else
        echo -e "${YELLOW}⚠️ 尝试 --user 模式...${NC}"
        $PYTHON_CMD -m pip install --user pygame -q
        echo -e "${GREEN}✅ pygame 安装完成${NC}"
    fi
    
    # 安装 mutagen
    echo "📦 安装 mutagen..."
    if $PYTHON_CMD -m pip install mutagen -q 2>/dev/null; then
        echo -e "${GREEN}✅ mutagen 安装成功${NC}"
    else
        echo -e "${YELLOW}⚠️ 尝试 --user 模式...${NC}"
        $PYTHON_CMD -m pip install --user mutagen -q
        echo -e "${GREEN}✅ mutagen 安装完成${NC}"
    fi
    
    echo ""
}

# ============================================
# 功能 4: 检查文件
# ============================================
check_files() {
    echo -e "${YELLOW}[4/5] 检查项目文件...${NC}"
    echo ""
    
    if [ -f "src/main.py" ]; then
        echo -e "${GREEN}✅ 找到 src/main.py${NC}"
    else
        echo -e "${RED}❌ 找不到 src/main.py${NC}"
        echo "请确保在项目根目录运行此脚本"
        echo "当前目录: $(pwd)"
        read -p "按 Enter 键退出..."
        exit 1
    fi
    echo ""
}

# ============================================
# 功能 5: 启动程序
# ============================================
run_player() {
    echo -e "${YELLOW}[5/5] 启动音乐播放器...${NC}"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   🎵 正在启动音乐播放器...${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # 运行程序
    $PYTHON_CMD src/main.py
    
    # 程序退出后的提示
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   程序已退出${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    read -p "按 Enter 键退出..."
}

# ============================================
# 主程序执行
# ============================================
main() {
    find_python
    check_pip
    install_dependencies
    check_files
    run_player
}

# 运行主程序
main