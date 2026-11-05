severity: minor

整體:新碼放在原本的層(`check.py` 自我檢查、`test_lumos.py` 的 `t_kotlin_*` 測試群),沒有跨層直呼,也沒有新的外部依賴或另一套測試略過機制。只有一條命名不一致。

**1. 分層與依賴方向:對齊**
- `dt_triggers`、`_NONE_TRIGGER` 加在 `configs/ast-grep/kotlin-android/check.py` 的 `_cells` 與 `catalog_problems` 之間,只被同檔的 `catalog_problems` 呼叫。我 grep 過,別處沒有引用。
- 回傳形狀 `(清單, 問題或 None)` 跟同檔 `catalog_problems`、`message_problems` 的 `(id, 訊息)` 問題串列相容。
- `_files_block_is_test_only` 的註解剝除是在同一函式內做,沒有新增 helper。
- 逾時處理沿用 `check.py:223` 的 `_TIMED_OUT` 旗標,`check.py:284` 在每次 `check()` 開頭重設。diff 讓 `check()` 認得 `loaded_count` 回傳的 `None`,跟 `scan`(`check.py:228`、`check.py:234`)的處理對稱。
- 測試只呼叫 `_ktpack()`、`_ktpack_sg()`、`check()`,跟 `test_lumos.py:125002`、`test_lumos.py:125139` 一樣。
- 零依賴家規沒被破壞:只用 `re`、`subprocess`、`pathlib`。

**2. 命名與錯誤處理:大致對齊,有一條不一致**
- 錯誤回傳方式跟鄰居一致:問題一律回 `(id, 中文訊息)`,不丟例外。缺〈來源縮寫〉節改成「記一筆、往下檢查」,跟檔內其他檢查一致。
- 訊息格式一致:`<檔>.yml 載入 N 條(略過 M)…` 與新加的 `讀不到載入條數` 同風格。
- 不對齊(minor):測試 `t_kotlin_rulepack_samples_not_scanned_as_code` 改名為 `t_rulepack_sample_dir_skips_risk_scan`(`scripts/test_lumos.py:125247`)。同群鄰居全是 `t_kotlin_rulepack_*` 或 `t_kotlin_catalog_*`(`test_lumos.py:125002`、`:125106`、`:125139`),只有它丟了 `kotlin_` 前綴。
- 這支測的是通用的「規則包樣本目錄不當產品碼掃」,不限 Kotlin,所以去前綴有理由。改名也是為了不互為前綴,有 `.governance-log.jsonl:124325` 的簽核紀錄。
- 引用這個名字的 `[test:]`(`pitfalls-code-loop.md:85`)已同步更新。所以只列 minor,屬於刻意取捨。

**3. 第二種做法:沒有**
- 沒有自創工具函式去重複鄰居已有的功能。`dt_triggers` 是把原本散在 `catalog_problems` 裡的解析抽成函式,且 `catalog_problems` 已改成呼叫它,沒有兩份並存。我沒找到鄰居裡有同功能的函式。
- 逾時旗標沿用既有的 `_TIMED_OUT`,沒另開機制。
- 測試改壞複本沿用 `_ktpack(copy=True)` 加 `Path.write_text` 的既有套路,檢查用同一個 `check(name, cond, detail)`。
- 把 `MSG_MAX` 與 `SCAN_TIMEOUT` 兩行誤黏的註解各歸各位,是純修正,不算新做法。

不對齊共 1 條,其中 major 0 條。

未驗範圍:我沒對修前版本(`af64ec645`)另取出跑命令。本席只管一致性,不判行為回歸。
