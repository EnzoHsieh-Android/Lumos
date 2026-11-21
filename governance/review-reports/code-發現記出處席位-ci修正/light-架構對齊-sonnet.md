severity: clean

**1. 分層與依賴方向**
- 這份修正放的位置跟鄰居一樣:日期留在 `reference.md` 和命令速查,入口頁 SKILL.md 只指向程式常數。
- 讀取方向也一樣。測試讀 `scripts/lumos` 的常數,再核兩份文件;鄰居測試的做法相同,例如 file: `scripts/test_lumos.py:4841`、file: `scripts/test_lumos.py:41207` 用 `Path(...)/"skills"/...` 直接讀文件。
- 入口頁日期上限由 file: `scripts/test_lumos.py:69451` 的 `t_skill_entry_pages_no_dated_history` 管。它的說明寫明生效日這類規則本身要的日期才算在 ≤3 內,所以把日期搬去參考檔是照既有慣例。
- 參考檔已有 file: `skills/lumos-code-loop/reference.md:143` 的「目前 2026-11-22」,命令速查的對應行是 file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:55`。現在測試核的就是這兩處,沒有新增跨層呼叫。
- 被改的測試仍是 `t_finding_seat_docs_match_since`,沒有新開測試,也沒有新的讀取路徑。

**2. 命名與錯誤處理**
- 入口頁新句「生效日見程式常數 `_FINDING_SEAT_SINCE`」的寫法,跟 file: `skills/lumos-code-loop/reference.md:38` 的「生效日 `_FINDING_SEAT_SINCE` 起」一致。
- 測試只縮減檢查的檔案清單,`check(...)` 的呼叫形式、訊息格式、`days == {day}` 的比對都沒變,跟原本一致。
- 測試沒呼叫 `_need_src`。鄰居有的有(file: `scripts/test_lumos.py:4839`),有的沒有(file: `scripts/test_lumos.py:4841` 附近直接讀檔)。這個測試修正前就是這樣,這份修正沒動,不算這次造成的不一致,只記下。
- 新增的註解提到「≤3」,對得上 file: `scripts/test_lumos.py:69462`。計劃筆記裡新加的一條紀錄,格式沿用同節既有的「代碼審 rN」條目寫法。

**3. 第二種做法**
- 沒有新機制:沒有新函式、新常數或新的日期來源。生效日仍只有程式常數一個真相來源,文件仍用同一條正規式機械核對。
- 入口頁用「見程式常數」代替寫日期,跟同頁其他生效日(例如 file: `skills/lumos-code-loop/SKILL.md:34` 直接寫 2026-09-12)寫法略不同。但這是被 ≤3 上限逼出來的,而且不另立規則;日期仍在參考檔與命令速查可查,所以不判不對齊。

不對齊共 0 條,其中 major 0 條
