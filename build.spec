# build.spec
# 使用方式：pyinstaller build.spec
import os
import platform
import sys
import customtkinter

# ── 路徑設定 ──────────────────────────────────────────────────────────────────
# Apple Silicon 版本需要使用 arm64 Ghostscript
if platform.machine() == "arm64":
    GS_CANDIDATES = ["/opt/homebrew/bin/gs"]
    TESSERACT_CANDIDATES = ["/opt/homebrew/bin/tesseract"]
    TESSDATA_CANDIDATES = ["/opt/homebrew/share/tessdata"]
else:
    GS_CANDIDATES = ["/usr/local/bin/gs"]
    TESSERACT_CANDIDATES = ["/usr/local/bin/tesseract"]
    TESSDATA_CANDIDATES = ["/usr/local/share/tessdata"]

GS_PATH = next((p for p in GS_CANDIDATES if os.path.exists(p)), None)
if GS_PATH is None:
    raise FileNotFoundError(
        "找不到符合目前架構的 Ghostscript binary。請先用正確架構的 Homebrew 安裝 ghostscript"
    )

TESSERACT_PATH = next((p for p in TESSERACT_CANDIDATES if os.path.exists(p)), None)
if TESSERACT_PATH is None:
    raise FileNotFoundError(
        "找不到符合目前架構的 Tesseract binary。請先用正確架構的 Homebrew 安裝 tesseract"
    )

TESSDATA_DIR = next((p for p in TESSDATA_CANDIDATES if os.path.isdir(p)), None)
if TESSDATA_DIR is None:
    raise FileNotFoundError("找不到 Tesseract tessdata 目錄")

OCR_LANGS = ["chi_tra", "eng"]
TESSDATA_FILES = []
for lang in OCR_LANGS:
    traineddata = os.path.join(TESSDATA_DIR, f"{lang}.traineddata")
    if not os.path.exists(traineddata):
        raise FileNotFoundError(f"找不到 OCR 語言包：{traineddata}")
    TESSDATA_FILES.append((traineddata, "tessdata"))

CTK_DIR = os.path.dirname(customtkinter.__file__)
PROJECT_DIR = os.path.dirname(os.path.abspath(SPEC))  # SPEC 為 PyInstaller 內建變數

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(PROJECT_DIR, "app.py")],
    pathex=[PROJECT_DIR],
    binaries=[
        (GS_PATH, "."),           # gs binary 放在 _MEIPASS 根目錄
        (TESSERACT_PATH, "."),    # tesseract binary 放在 _MEIPASS 根目錄
    ],
    datas=[
        (CTK_DIR, "customtkinter"),  # customtkinter 主題與資源
        *TESSDATA_FILES,
    ],
    hiddenimports=[
        "customtkinter",
        "PIL",
        "PIL._tkinter_finder",
        "fitz",
        "pdf2docx",
        "docx",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDF 輕巧工具箱",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # windowed 模式，不跳 terminal
    argv_emulation=False,
    target_arch="arm64" if platform.machine() == "arm64" else None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PDF 輕巧工具箱",
)

app = BUNDLE(
    coll,
    name="PDF 輕巧工具箱.app",
    icon=None,              # 若有 .icns 圖示，在此指定路徑
    bundle_identifier="com.internal.pdf-tools",
    info_plist={
        "CFBundleDisplayName": "PDF 輕巧工具箱",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
    },
)
