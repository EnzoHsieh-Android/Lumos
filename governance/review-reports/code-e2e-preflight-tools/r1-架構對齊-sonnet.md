severity: minor

## A1 缺工具的擋下訊息句式跟收集腳本不同
severity: minor
blocking: 否

新增的訊息跟收集腳本同一個檢查的句式不一樣。收集腳本是「找不到 X;用環境變數 Y= 指定」。新增的是「記憶體與穩定性要用的 {name} 找不到(找的是 {tool});裝好 Perfetto 的工具,或用環境變數 {var}= 指定」。這個檔自己的 ADB/MAESTRO 檢查用的是收集腳本那個句式。同一件事在三處有兩種說法,結構本身對。

對照:
- ``file: `scripts/templates/android-stability-collect.sh:378` ``(「找不到 {tool};用環境變數 ADB=、TP= 指定」)
- ``file: `scripts/templates/android-stability-collect.sh:381` ``(「宣告了測試資料要錄快照,但找不到 {JHD};用 JAVA_HEAP_DUMP= 指定」)
- ``file: `scripts/templates/android-e2e-run.sh:252` ``(`die(f"找不到 {tool};用環境變數 ADB=、MAESTRO= 指定")`)

引句:「                die(f"記憶體與穩定性要用的 {name} 找不到(找的是 {tool});裝好 Perfetto 的工具,或用環境變數 {var}= 指定")」

## A2 ⚠ 「測試資料有宣告」的判斷在兩支腳本各寫一份
severity: minor
blocking: 否

交編排者判斷,我不硬判是不是 major。
- 收集腳本在 `:379` 寫的是 `test_data = bool((st.get("test_data") or {}).get("value"))`。
- 新增的是同一條判斷的 inline 版本,放在 e2e-run.sh 的 preflight 裡。
- 兩支是各自獨立的 `python3 -` heredoc,不能互相 import,所以重複有結構上的原因。
- 兩邊現在等價,但之後只改一邊會變成兩套。
- 新增的註解有說明「收集腳本自己也查」,但沒有任何綁定,例如測試會同時動兩邊。
- 專案裡沒有可共用的現成做法,所以我只標 ⚠,理由是:這是該統一還是接受重複的取捨題,不是單純不一致。

引句:「        if ((cfg.get("stability") or {}).get("test_data") or {}).get("value"):」

## 三問

1. **分層與依賴方向:對齊。**
   - 新碼放在 `preflight()` 裡,緊接在 ADB/MAESTRO 的 `shutil.which` 迴圈之後、呼叫 `lumos android-e2e judge --precheck` 之前。位置跟既有的開跑前檢查一致,見 `scripts/templates/android-e2e-run.sh:252`。
   - 沒有跨層直呼。它只讀已載入的 `cfg` 和模組層常數 `TP`、`JHD`。
   - `TP`、`JHD` 的宣告方式跟 ADB、MAESTRO 一樣,用 `os.environ.get(名, 預設)` 放在同一區,跟 ``file: `scripts/templates/android-stability-collect.sh:24` `` 一致。
   - 測試側擴充既有的 `_e2e_script_env(td, **proj)`,沒有另起一套輔助,見 `scripts/test_lumos.py:19004`。
2. **命名與錯誤處理:大致對齊,只有句式有差。**
   - 環境變數名 `TP` 和 `JAVA_HEAP_DUMP` 跟收集腳本相同。
   - 錯誤走 `die()`,回傳碼 2,前綴「擋下:」,都對。
   - 句式差異見 A1。
   - 新測試末尾的 `print("  ✓ t_...")` 是專案慣例,全檔有 335 處,不算差異。
3. **第二種做法:沒有明確的新做法。**
   - 唯一接近的是 A2 的重複判斷,已標 ⚠。
   - 缺工具的檢查仍是 `shutil.which` 加 `die`,沒有引入新機制。
   - 測試沿用 `_e2e_script` 和 `_e2e_script_env`,沒有新輔助。

不對齊共 2 條,其中 major 0 條
