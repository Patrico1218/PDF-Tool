#!/bin/bash
# build.sh — 重新打包 PDF 工具.app
# 使用方式：bash build.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "清除舊的 build / dist 目錄..."
rm -rf build dist

echo "執行 PyInstaller..."
pyinstaller build.spec

echo ""
echo "打包完成。輸出位置：dist/PDF 工具.app"
echo "將 dist/PDF 工具.app 拖入 /Applications 即可安裝。"
