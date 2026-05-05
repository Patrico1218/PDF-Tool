#!/bin/bash
# build.sh — 重新打包 PDF 輕巧工具箱.app
# 使用方式：bash build.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ "$(uname -m)" != "arm64" ]]; then
  echo "錯誤：此腳本目前設定為產出 Apple Silicon arm64 版本，請在 arm64 Mac 上執行。"
  exit 1
fi

PYTHON_BIN="/opt/homebrew/bin/python3.12"
GS_BIN="/opt/homebrew/bin/gs"
TESSERACT_BIN="/opt/homebrew/bin/tesseract"
TESSDATA_DIR="/opt/homebrew/share/tessdata"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "錯誤：找不到 arm64 Python 3.12：$PYTHON_BIN"
  echo "請先用 Apple Silicon Homebrew 安裝 Python 3.12。"
  exit 1
fi

if ! file "$PYTHON_BIN" | grep -q "arm64"; then
  echo "錯誤：$PYTHON_BIN 不是 arm64 架構。"
  exit 1
fi

if [[ ! -x "$GS_BIN" ]]; then
  echo "錯誤：找不到 arm64 Ghostscript：$GS_BIN"
  echo "請先用 Apple Silicon Homebrew 安裝 Ghostscript。"
  exit 1
fi

if ! file "$GS_BIN" | grep -q "arm64"; then
  echo "錯誤：$GS_BIN 不是 arm64 架構。"
  exit 1
fi

if [[ ! -x "$TESSERACT_BIN" ]]; then
  echo "錯誤：找不到 arm64 Tesseract OCR：$TESSERACT_BIN"
  echo "請先用 Apple Silicon Homebrew 安裝 tesseract。"
  exit 1
fi

if ! file "$TESSERACT_BIN" | grep -q "arm64"; then
  echo "錯誤：$TESSERACT_BIN 不是 arm64 架構。"
  exit 1
fi

for lang in chi_tra eng; do
  if [[ ! -f "$TESSDATA_DIR/$lang.traineddata" ]]; then
    echo "錯誤：找不到 OCR 語言包：$TESSDATA_DIR/$lang.traineddata"
    echo "請安裝 Tesseract 繁體中文與英文語言資料。"
    exit 1
  fi
done

echo "清除舊的 build / dist 目錄..."
rm -rf build dist

echo "執行 PyInstaller..."
"$PYTHON_BIN" -m PyInstaller build.spec

echo ""
echo "打包完成。輸出位置：dist/PDF 輕巧工具箱.app"
echo "將 dist/PDF 輕巧工具箱.app 拖入 /Applications 即可安裝。"
