# build.spec
# 使用方式：pyinstaller build.spec
import os
import sys
import customtkinter

# ── 路徑設定 ──────────────────────────────────────────────────────────────────
# 依照開發機架構選擇正確 gs 路徑
GS_CANDIDATES = ["/opt/homebrew/bin/gs", "/usr/local/bin/gs"]
GS_PATH = next((p for p in GS_CANDIDATES if os.path.exists(p)), None)
if GS_PATH is None:
    raise FileNotFoundError(
        "找不到 Ghostscript binary。請先執行 brew install ghostscript"
    )

CTK_DIR = os.path.dirname(customtkinter.__file__)
PROJECT_DIR = os.path.dirname(os.path.abspath(SPEC))  # SPEC 為 PyInstaller 內建變數

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(PROJECT_DIR, "app.py")],
    pathex=[PROJECT_DIR],
    binaries=[
        (GS_PATH, "."),           # gs binary 放在 _MEIPASS 根目錄
    ],
    datas=[
        (CTK_DIR, "customtkinter"),  # customtkinter 主題與資源
    ],
    hiddenimports=[
        "customtkinter",
        "PIL",
        "PIL._tkinter_finder",
        "fitz",
        "pdf2docx",
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
    name="PDF 工具",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # windowed 模式，不跳 terminal
    argv_emulation=False,
    target_arch=None,
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
    name="PDF 工具",
)

app = BUNDLE(
    coll,
    name="PDF 工具.app",
    icon=None,              # 若有 .icns 圖示，在此指定路徑
    bundle_identifier="com.internal.pdf-tools",
    info_plist={
        "CFBundleDisplayName": "PDF 工具",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
    },
)
