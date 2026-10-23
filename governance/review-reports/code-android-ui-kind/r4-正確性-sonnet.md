severity: minor

我找不到會讓本輪修補算錯的輸入。唯一站得住腳的發現是一條 minor:使用者環境變數 `PYTHONIOENCODING` 設成非 UTF-8 時,拿掉逐處參數後腳本會崩潰。

## 1. 使用者設了 PYTHONIOENCODING=ascii 時,重跑腳本在印中文比對值時崩潰回 1(拿掉 reconfigure 的副作用)
severity: minor
blocking: 否
引句:「exec env PYTHONUTF8=1 python3 - "$HERE" "$PROJECT_ROOT" "${TP:-trace_processor}" <<'PY'」
file: `scripts/templates/android-receipt-rerun.sh:12`(印結果的 print 在腳本第 66 行附近)
歸因:有證據的修復回歸
- **原因:** `PYTHONUTF8=1` 管不到 `PYTHONIOENCODING`,後者優先權較高。上一版的 `sys.stdout.reconfigure(encoding='utf-8')` 會覆蓋使用者的環境變數,這一版拿掉後就沒有這層保護。
- **輸入:** `expect=k:v=甲` 這種帶中文比對值的收據,加上 `PYTHONIOENCODING=ascii`。
- **走到哪:** 比對完後 `print(('OK  ' if ok else 'BAD ') + qid, kv['expect'], ...)` 輸出時丟 `UnicodeEncodeError`,腳本帶 Traceback 結束,rc=1。
- **影響:** 比對成功時應回 0 卻回 1。這個方向不會假過,但 rc=1 和「比對不符」同碼,Traceback 在 stderr。
- **兩版查證,命令相同:** `PYTHONIOENCODING=ascii TP=<假分析工具,印 "k","v" 與 "k","甲"> sh rerun.sh`
  - 修前(e3ea2c16):`OK  Q1 k:v=甲`,rc=0。加 `LC_ALL=C` 也是 rc=0。
  - 修後(ab35a0f8):`UnicodeEncodeError: 'ascii' codec can't encode character '\u7532'`,rc=1。
- **等級理由:** 這個環境變數少見,而且只有比對值含非 ASCII 時才崩。「擋下:」訊息走 stderr,stderr 的錯誤處理是 backslashreplace,不會崩。所以我標 minor,不是 major,也沒有能當場翻紅的 blocker 級重現。
- **可選修法:** 改成 `env PYTHONUTF8=1 PYTHONIOENCODING=utf-8`,或在腳本頂端保留一行 `sys.stdout.reconfigure(encoding='utf-8')`。現有測試沒設這個變數,所以抓不到。

## 已驗主張的證據

**Linux 容器**(python:3.14-slim,唯讀掛載後複製出來跑):
- `-k android_ui_attribution`:54 passed, 0 failed
- `-k android_evidence`:7 passed, 0 failed
- `-k license_headers`:8 passed, 0 failed

**重跑腳本修補處,手跑假分析工具的結果:**

| 情境 | 結果 |
|---|---|
| 預設環境,中文比對值 | `OK`,rc=0 |
| `LC_ALL=C`,stdout 導到檔案 | 檔案內容正確,rc=0 |
| `TP` 是目錄 | rc=2,擋下訊息帶「Permission denied」 |
| `TP` 是不可執行的檔案 | rc=2,擋下訊息帶「Permission denied」 |
| `TP` 是空字串 | 退回預設 `trace_processor`,找不到時 rc=2 |

- 之前擔心的 `try/except OSError/finally`,走過例外路徑和 `sys.exit(2)` 後,`finally` 仍會 `unlink` 暫存檔。
- 測試的 `TMPDIR` 斷言也確認暫存目錄為空。
- 官方 `trace_processor` 是 Python 包裝腳本,會繼承 `PYTHONUTF8=1`,這是無害的。
- Python 3.6 的路徑:`capture_output` 本來就是 3.7 起才有,所以拿掉 `reconfigure` 不使它比修前更糟。

**授權守衛:** `f.lower().endswith(".sql")` 對 `x.SQL` 認 `--`,也不會讓 `.sql` 誤收 `#`。

**pitfalls manifest:** 我沒有逐條看 `r4-manifest.json` 的 pitfalls-builtin 條目。
**圖譜固定席:** 本輪改動只動範本腳本與測試,沒有動 `scripts/lumos`,我判斷這些固定席合約不會被破壞,但沒有逐篇驗證。
**角色卡:** 兩題都不適用。這份 diff 沒有對外 API,也沒有端點。

## 未驗範圍
- 沒有逐項對 mutation 測試(拿掉 `utf-8-sig`、`except`、`finally` 各自是否紅),只信任 `r4-behavior-cases.json` 的宣稱。
- Python 3.6 實機沒跑。
- Windows 與 Git Bash 沒跑。
- SQL 範本本體(`android-ui-attribution.sql`)沒有重審。

## 三問
1. **修復效果有行為證據嗎?** 有。Linux 測試全綠,加上手跑的 `LC_ALL=C`、stdout 導檔、`TP` 異常、暫存檔清除各路徑。
2. **修補處的正常、錯誤、相鄰路徑有走過嗎?** 有,唯一偏差是上面第 1 條。
3. **新發現的案例在修前修後各是什麼結果?** 只有第 1 條:修前 rc=0,修後 rc=1。

總結:最高嚴重度 minor
