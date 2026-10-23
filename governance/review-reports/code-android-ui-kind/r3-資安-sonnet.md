severity: clean

我讀了 patch 裡全部 9 個檔案,沒有可利用的洞。

我沒有實際執行重跑腳本,結論靠讀 patch 和 skill 文件。

### 逐類清單

**①提示注入:已看,無。**
- patch 新增的自由文字都是靜態內容:筆記、Verification、skill 與 reference 文件、SQL 範本的註解。
- 沒有任何一處把筆記內容、檔名、分支名、帳本欄位或席報告自動拼進派工詞或 hook 附加段。
- 唯一會進 SQL 的外來值是 `__PROCESS__`(App 套件名),是 AI 照 skill 步驟手動替換。
  - skill 第 1 步已要求套件名只含英數字、底線與點,含別的字元就停下來問人。
  - 範本裡 `p.name = '__PROCESS__'` 在引號內,這個限制足以擋住引號逃逸。

**②讀寫與執行越界:已看,無。**
- 重跑腳本(`scripts/templates/android-receipt-rerun.sh`):
  - 本輪只加了 `encoding='utf-8'`、`errors='replace'` 和 `stdout/stderr.reconfigure`。
  - 執行對象仍是 `$TP` 或 `trace_processor`,這是既有設計,環境變數覆蓋由使用者自己決定。
  - 暫存檔用 `NamedTemporaryFile`,用完 `os.unlink`。
  - 呼叫 `subprocess.run` 時是 list 形式,沒有 shell 插值。
  - 本輪沒有新增下載、網路或跨 repo 寫入。
- 兩處我認為「不報」,理由如下。這兩處是修補前就有的行為,patch 沒改動:
  - 收據 manifest 的 `path` 直接 `os.path.join` 到專案根目錄,理論上絕對路徑或 `..` 可以指到 repo 外。但收據是使用者或 AI 在自己專案寫的,要利用得刻意偽造 manifest,屬系統天花板。
  - `python3 -` 讀 stdin 時 `sys.path[0]` 是空字串,也就是當前目錄。要利用得刻意在當前目錄放 `json.py` 之類的檔案,同樣屬刻意佈置。
- `scripts/lumos` 只在 `_VENDORED_TREE_FILES` 加一行新範本路徑,沒有執行或寫入的新行為。
- 測試檔用 `tempfile.TemporaryDirectory(prefix="gctl-uirerun-")` 和 `gctl-mbthr-`,只寫臨時目錄,假分析工具是測試自己產生的 `#!/bin/sh`。
  - `sp.run(["sh", ...])` 是 list 形式。
  - 傳給子程序的環境只加 `TP`、`LC_ALL` 等,沒有看起來真能用的憑證。
- 新進程式、範本與文件的內容只有 SPDX 版權行,已看過沒有新增密鑰或信箱。「Enzo Hsieh」是既有的授權標頭慣例。

**③非刻意、一步就能繞過的守衛:已看,無。**
- LC_ALL=C 下原本會在寫暫存檔或印結果時崩潰,本輪已修。
- 新測試確實用 `LC_ALL=C` 加 `PYTHONUTF8=0` 去驗證這件事。
- 解析失敗或編碼出錯時,腳本不會誤回 0:
  - `errors='replace'` 只影響顯示和子程序輸出的解碼。
  - 比對不符時 `ok` 為 False,仍會回 1。
  - 檔頭的「不准空轉」檢查和 exit 2 邏輯沒有被動到。
- 我沒有發現可被一個指令或一次編輯意外走過去的新旁路。

**語言棧條款對照:**
- python-idioms R15 邊界驗證:已看,無。
- python-idioms R16 秘密不進 log:已看,無。
- python-idioms R18 反序列化與 shell:已看,無。`json.load` 只讀本地 manifest,`subprocess.run` 是 list 形式。
- SQL 範本:無對應條款。
- Markdown:無對應條款。

總結:最高嚴重度 clean
