#!/bin/bash
# ============================================
# 🎵 音乐播放器 - 一键启动
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   🎵 音乐播放器 - 一键启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Python 路径
PYTHON="/c/Users/Administrator/AppData/Local/Programs/Python/Python312/python.exe"

echo -e "${YELLOW}1️⃣ 检查依赖...${NC}"
echo ""

# 检查 pygame
if ! $PYTHON -c "import pygame" 2>/dev/null; then
    echo -e "${YELLOW}⚠️ pygame 未安装，正在安装...${NC}"
    $PYTHON -m pip install pygame -q
    echo -e "${GREEN}✅ pygame 安装完成${NC}"
fi

# 检查 mutagen
if ! $PYTHON -c "import mutagen" 2>/dev/null; then
    echo -e "${YELLOW}⚠️ mutagen 未安装，正在安装...${NC}"
    $PYTHON -m pip install mutagen -q
    echo -e "${GREEN}✅ mutagen 安装完成${NC}"
fi

echo ""
echo -e "${YELLOW}2️⃣ 启动音乐播放器...${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   🎵 正在启动...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

$PYTHON src/main.py

echo ""
echo -e "${GREEN}程序已退出${NC}"
read -p "按 Enter 键退出..."