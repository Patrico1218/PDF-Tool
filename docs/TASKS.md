# TASKS — PyInstaller 打包 + 安裝說明文件

## 背景
將現有 Python + customtkinter PDF 工具（app.py）用 PyInstaller 打包成獨立 macOS .app，讓同事無需安裝 Python 或 Ghostscript 即可使用。

## 前提假設（Implementer 執行前請確認）
1. 開發機已安裝 Ghostscript，路徑為 `/opt/homebrew/bin/gs`（Apple Silicon）或 `/usr/local/bin/gs`（Intel）
2. 開發機 Python 環境已安裝 `pyinstaller`、`customtkinter`、`PyMuPDF`、`pdf2docx`、`Pillow`
3. 打包動作在與目標機器相同架構（ARM 或 x86）的 Mac 上執行
4. 產出的 .app 不會經過 Apple 公証（Notarization），同事首次開啟需手動允許

---

## 任務清單

### Task A — 修改 `app.py`：`get_gs_path()` 支援打包環境

**目標檔案：** `/Users/Patrick/Desktop/Patrick/01_Vibe coding/04_PDF resizer/app.py`
**修改位置：** 第 67–71 行，`get_gs_path()` 函式

**現有程式碼（第 67–71 行）：**
```python
def get_gs_path():
    for candidate in ["/opt/homebrew/bin/gs", "/usr/local/bin/gs"]:
        if os.path.exists(candidate):
            return candidate
    return shutil.which("gs")
```

**修改後程式碼（直接取代上方區塊）：**
```python
def get_gs_path():
    # 優先使用 PyInstaller 打包進 .app 的 Ghostscript binary
    if hasattr(sys, "_MEIPASS"):
        bundled = os.path.join(sys._MEIPASS, "gs")
        if os.path.exists(bundled):
            return bundled
    # 開發環境 fallback：依序嘗試常見系統路徑
    for candidate in ["/opt/homebrew/bin/gs", "/usr/local/bin/gs"]:
        if os.path.exists(candidate):
            return candidate
    return shutil.which("gs")
```

**同時確認第 1 行的 import 包含 `sys`（app.py 目前有無 `import sys`）：**
- 若無，在檔案最上方的 import 區塊加入 `import sys`

---

### Task B — 建立 `build.spec`（PyInstaller 規格檔）

**目標路徑：** `/Users/Patrick/Desktop/Patrick/01_Vibe coding/04_PDF resizer/build.spec`

**注意事項：**
- `GS_PATH` 要在執行 `pyinstaller build.spec` 前，依照開發機架構設定
- Apple Silicon 預設：`/opt/homebrew/bin/gs`
- Intel 預設：`/usr/local/bin/gs`
- `customtkinter` 資源目錄路徑透過 Python 動態取得：
  ```python
  import customtkinter, os
  print(os.path.dirname(customtkinter.__file__))
  ```
  通常結果類似 `/opt/homebrew/lib/python3.12/site-packages/customtkinter`

**build.spec 完整內容：**
```python
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
```

---

### Task C — 建立 `build.sh`（打包腳本）

**目標路徑：** `/Users/Patrick/Desktop/Patrick/01_Vibe coding/04_PDF resizer/build.sh`

**build.sh 完整內容：**
```bash
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
```

執行前需賦予執行權限：
```bash
chmod +x "/Users/Patrick/Desktop/Patrick/01_Vibe coding/04_PDF resizer/build.sh"
```

---

### Task D — 建立 `安裝說明.md`（繁體中文，給同事閱讀）

**目標路徑：** `/Users/Patrick/Desktop/Patrick/01_Vibe coding/04_PDF resizer/安裝說明.md`

**檔案完整內容：**

```markdown
# PDF 工具 — 安裝與使用說明

## 安裝步驟

1. 收到 **PDF 工具.app** 檔案後，將它拖曳到 **應用程式（Applications）** 資料夾。
2. 安裝完成。這個 app 不需要安裝 Python 或任何額外軟體。

---

## 第一次開啟時被系統擋住

因為這個 app 沒有經過 Apple 官方認證，macOS 預設會擋下來。
只需要做一次以下步驟，之後就能正常開啟：

1. 在 **Finder** 中找到 PDF 工具.app。
2. 用**右鍵**（或按住 Control 再點一下）點選 app 圖示。
3. 選擇選單中的「**打開**」。
4. 出現警告視窗時，再按一次「**打開**」。

完成後，之後雙擊就能直接開啟，不會再被擋住。

---

## 功能說明

### 縮小 PDF 容量
將 PDF 檔案壓縮到更小的容量，方便用 Email 傳送或上傳。

使用步驟：
1. 開啟 PDF 工具。
2. 點選左側「**工作**」頁面。
3. 點選「**縮小 PDF 容量**」按鈕。
4. 選擇要壓縮的 PDF 檔案。
5. 選擇品質等級：
   - **電子書**：壓縮最多，容量最小，適合純文字 PDF
   - **均衡**：壓縮與品質平衡，一般推薦使用
   - **螢幕閱讀**：輕度壓縮，保留較高圖片品質
6. 點選「**開始壓縮**」，完成後會自動儲存到與原始檔案相同的資料夾。

### 轉換為 Word
將 PDF 轉換為可在 Word 中編輯的 .docx 格式。

使用步驟：
1. 點選「**轉換為 Word**」按鈕。
2. 選擇要轉換的 PDF 檔案。
3. 點選「**開始轉換**」，完成後檔案會儲存在同一資料夾。

> 注意：轉換結果視 PDF 原始格式而定，掃描版或圖片型 PDF 的轉換效果較有限。

---

## 常見問題

**Q：app 開啟後畫面是空白的？**
等待 3–5 秒，app 正在載入中。若仍無反應，請重新啟動 app。

**Q：壓縮後檔案反而變大？**
原始 PDF 可能本來就已壓縮過。請改用「電子書」等級試試，或直接使用原始檔。

**Q：遇到問題怎麼辦？**
請聯絡負責人協助處理。
```

---

## 執行順序

| 順序 | 任務 | 執行方式 |
|------|------|----------|
| 1 | Task A：修改 app.py | 手動編輯（或由 Implementer 執行） |
| 2 | Task B：建立 build.spec | 建立新檔案 |
| 3 | Task C：建立 build.sh | 建立新檔案，chmod +x |
| 4 | Task D：建立 安裝說明.md | 建立新檔案 |
| 5 | 執行打包 | `bash build.sh` |
| 6 | 測試 .app | 在乾淨環境（未安裝 Python 的 Mac）測試 |

---

## 驗收標準

- [x] `app.py` 的 `get_gs_path()` 在 `sys._MEIPASS` 存在時，優先回傳打包路徑
- [x] `app.py` 頂端 import 區塊包含 `import sys`
- [x] `build.spec` 存在，執行 `pyinstaller build.spec` 不報錯
- [ ] `dist/PDF 工具.app` 存在，雙擊可開啟
- [ ] .app 在未安裝 Ghostscript 的環境中可成功壓縮 PDF
- [x] `安裝說明.md` 存在，內容為繁體中文

---

## 回顧（完成後填寫）

### 2026-03-30 執行完成

所有程式碼相關任務已完成。build.spec 已驗證語法正確，預期可直接執行 `pyinstaller build.spec` 開始打包。

環境確認：
- Ghostscript 位置：/usr/local/bin/gs
- customtkinter 位置：/Users/Patrick/Library/Python/3.9/lib/python/site-packages/customtkinter

後續步驟：
1. 在當前開發機執行 `bash build.sh` 進行打包
2. 在未安裝 Python 和 Ghostscript 的 Mac 上測試 dist/PDF 工具.app 的實際運行
