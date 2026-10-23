severity: minor

## 1. 修補拿掉 stdout 重設後,使用者環境設了 PYTHONIOENCODING 就會在輸出中文時崩潰
severity: minor
blocking: 否
引句:「exec env PYTHONUTF8=1 python3 - "$HERE" "$PROJECT_ROOT" "${TP:-trace_processor}" <<'PY'」
file: `scripts/templates/android-receipt-rerun.sh:11`
歸因:有證據的修復回歸(修前 e3ea2c16 有 `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`,修後 ab35a0f8 拿掉了)
具體失敗場景:
- 使用者環境有 `PYTHONIOENCODING=ascii`,或其他非 UTF-8 的值。
- UTF-8 模式不會壓過 `PYTHONIOENCODING`,所以輸出含中文的 `OK  Q1 甲1:...` 時 stdout 用 ascii 編碼。
- 結果是 `UnicodeEncodeError` 的 Traceback,rc=1。
- 這是比對相符的收據,卻回 1,看起來像比對不符。不會出現假過。

重現命令與結果(本機用假分析工具,輸出 `"frame","compose_ns"` 與 `"甲1","5"`):
- 修前版:`PYTHONIOENCODING=ascii TP=<假tp> sh rerun.sh` 印出 `OK  Q1 甲1:compose_ns=5`。
- 修後版:同一條命令得 `UnicodeEncodeError: 'ascii' codec can't encode character '\u7532'`。
- 在 python:3.14-slim 容器、`LC_ALL=C` 下,修後版同樣崩潰。

建議:`exec env PYTHONUTF8=1 PYTHONIOENCODING=utf-8 ...`。環境也可能設別的值,但 PYTHONIOENCODING 是唯一會壓過 UTF-8 模式的變數。

## 2. 收據自身壞掉時有幾條路徑是 Traceback 回 1,不是文件承諾的回 2
severity: minor
blocking: 否
引句:「`rerun.sh` 遇到標頭數跟解析到的條數不一樣、一條 expect 都沒有、或 manifest 列的 Q 不在檔裡,會回 2 並說原因;這是收據本身寫錯,不是量測結果不符。」
file: `scripts/templates/android-receipt-rerun.sh:61`(`k, v = p.split('=')`)與 `scripts/templates/android-receipt-rerun.sh:15`(讀 manifest)
歸因:有證據的原有漏查(修前後這幾行相同;修補只動了編碼、BOM 與 TP 三處)
具體失敗場景(都是 Traceback、rc=1,與「比對不符」同碼):
- `expect=甲1`(沒有冒號):`ValueError: not enough values to unpack`。
- `expect=甲1:compose_ns=5=5`:`ValueError: too many values to unpack`。
- manifest.json 不存在:`FileNotFoundError`。
- manifest 是 UTF-16 的 BOM(PowerShell 5 的 `>` 會這樣寫):`UnicodeDecodeError`。這是 BOM 修補沒涵蓋到的相鄰格式。

以上都不會假過,所以只標 minor。呼叫端若用 rc 區分收據寫錯(2)與量測不符(1),會被誤導。

## BOM、路徑、TP 錯誤的驗收(未發現問題)
- BOM 加 CRLF、中文加空白的 manifest 路徑、queries.sql 與 manifest 同時帶 BOM:rc=0,`OK  Q1` 照印。
- 單獨改 `expect=` 值讓它不符:第一條會被讀到並回 1(修補確實修好)。
- TP 指到目錄、不可執行的檔、沒有 shebang 的檔:都回 2,訊息以「擋下:」開頭。
- TP 指到不存在的檔:回 2。
- TP 是回非 0 的程式:印 `BAD Q1`、rc=1。
- 使用者環境設 `PYTHONUTF8=0`:被 `env PYTHONUTF8=1` 蓋過,正常。
- 容器(python:3.14-slim)下 `LC_ALL` 設 C、POSIX、空字串、C.UTF-8,且未設 LANG:收據重跑全部 rc=0,中文路徑與中文分析工具路徑都通。
- 同樣四種語系下的測試:`-k android_ui_attribution` 54 過、`-k license_headers` 8 過、`-k android_evidence` 7 過,皆 0 失敗。

## 授權守衛的邊界
- `.SQL` 以及 `.Sql` 之類大小寫混用,經 `.lower()` 都認 `--`。
- `x.sql.bak` 與沒有副檔名的檔,照舊認 `#`。
- 檔案集合來自 `_VENDORED_ALL`,不受影響。
- 未發現問題。

## pitfalls manifest(source:pitfalls-builtin)逐條判斷
- `scripts/templates/android-receipt-rerun.sh:15` 與 `:17` 的 `open(`(檔案 handle 有沒有 with):誤報。這是跑完就退出的單次腳本,只讀兩個小檔,沒有長駐的 handle 洩漏。
- `scripts/templates/android-ui-attribution.sql:31`、`47`、`52`、`68`、`78` 的 SELECT(是否在迴圈內造成 N+1):全部誤報。這些是 CTE 內的集合式子查詢,沒有逐列迴圈。計劃筆記記錄過 12.6 萬個區段 0.5 秒,效能已實測過。

## 圖譜固定席
- 授權與歸屬的 ★INVARIANT★ 兩條:
  - 授權檔不得進 `_VENDORED_TOOLKIT`:本次沒動白名單,不牽連。
  - 每支被複製的檔至少有 SPDX 註解行:本次只放寬 `.sql` 認 `--`(不分大小寫),`#` 寫在 `.sql` 仍不收,合約沒被削弱。
- 其餘固定席節點(lumos-cli-read、測試假綠形態、design-loop、bound-tests-gate、guard-kill、lumos-cli-lifecycle)的合約,與收據重跑腳本、SQL 範本、授權標示守衛都不重疊,不牽連。

## 三問
1. 修復效果有行為證據嗎?有。BOM、中文路徑、`LC_ALL=C`、分析工具執行不了都在 macOS 與 Linux 容器實跑通過。
2. 修補處的正常、錯誤、相鄰路徑呢?正常與錯誤路徑都過;相鄰路徑中,UTF-16 manifest 與 `PYTHONIOENCODING` 沒被涵蓋,見 finding 2 與 1。
3. 新發現的案例在修前修後各是什麼結果?
   - 案例一(`PYTHONIOENCODING=ascii`):修前 OK(rc=0),修後崩潰(rc=1)。
   - 案例二(`expect` 缺冒號、多等號;manifest 缺檔或 UTF-16):修前後都是 Traceback 回 1。

總結:最高嚴重度 minor
