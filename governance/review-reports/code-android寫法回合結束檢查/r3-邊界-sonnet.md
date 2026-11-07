severity: minor

我讀完整份 r3-repair-乙.patch,並在 HEAD 8717114b0 上實跑。實跑用假 lumos、隔離的 HOME 和臨時 repo,臨時目錄已刪。

**上一輪第二輪邊界席 F1–F2 核對**
- F1(起點檔超大整數或深層巢狀)已修好。
  - 起點檔的 `t` 是 400 位數、`1e999`、20 萬層 `[`、10 萬層 `{`,都是 rc0,印「沒記到起點,不檢查」。
  - `t` 是字串 `"12.5"` 或 `1e300` 時照常往下走,不丟例外。
- F2(SIGINT、SIGHUP 留孤兒)已修好。
  - SIGINT、SIGHUP、SIGTERM 各在 0、0.03、0.06、0.1、0.2、0.5、1.0 秒送一次,共 21 組。
  - 0.1 秒以後都是 rc0,lint-new 都被收掉,零孤兒。
  - 0.06 秒以前訊號到時 lint-new 還沒開,所以沒有孤兒可留。
  - Popen 回傳到登記之間的窗口,靠 `pending` 旗標補收。程式結構看起來對,但這次沒有實測,是 r2 邊界席用注入方式驗過。

**其他邊界,沒有問題**
- `_reason` 擋停訊息的長度邊界:
  - 告警 0 條時只印標頭三行,不崩。
  - 1 到 14 條、訊息 0 到 400 字的全部組合,只要有印出告警條目,整段都沒超過 1500 字。
  - 單條訊息 5000 字會被消毒截短,整段只有 291 字。
  - 三條都是 3000 字的訊息,印 3 條,共 695 字。
- 檔名含反引號、換行、`\x00`、ESC 序列、`\u202e`、5000 字長檔名、非字串(None、整數、清單),輸出都沒有反引號、ESC 或多出的換行,也沒丟例外。
- `unchecked_kind` 欄位缺、值不認得或 JSON 不是物件,都記成 error。rc3 但最後一行不是 JSON 時,也走 error 這條。
- 標記檔名搬進共用模組後,新舊互讀沒有問題。
  - 舊版 `check-graph-sync.py` 的 `_stop_mark_path` 與新版 `_mark_name` 用同一條消毒規則,同樣截 120 字,同樣把 `""`、`.`、`..` 當無效。
  - 這是看程式碼比對的結果,r2 席另有實跑驗過。
- `check-graph-sync.py` 刪掉 `import time` 後,模組裡已沒有 `time.` 的用法(只剩第 743 行的區域匯入 `_tm`),不會有 NameError。
- `impact-hook.py` 的 `extract_delta_text` 拿掉 `new_only`,全 repo 的呼叫端都沒再帶這個參數。

F1 鉤子 stdin 的壞形狀處理三支不一致,同一個 RecursionError 家族只修了起點檔那一處
- 輸入一:stdin 是 30 萬個 `[`。
  - 實際:`stop-lint-hook.py`、`check-graph-sync.py`、`impact-hook.py` 三支都丟 `RecursionError`,rc1。
  - 預期:rc0 靜默放行,同這輪對起點檔做的處理。
  - 原因:`stop-lint-hook.py` 的 main 只接 `(ValueError, OSError)`,另兩支只接 `json.JSONDecodeError`。
- 輸入二:`impact-hook.py` 收到 `null`、`[1]`、`"x"` 或 `5`,實際 `AttributeError: ... has no attribute 'get'`,rc1。預期 rc0,同 `stop-lint-hook.py` 有 `isinstance(payload, dict)` 判斷。
- 輸入三:stdin 是 `\xff\xfe{`(非 UTF-8)。`check-graph-sync.py` 和 `impact-hook.py` 丟 `UnicodeDecodeError`,rc1,`stop-lint-hook.py` 正常放行。
- 輸入四:`check-graph-sync.py` 收到 `{"session_id":` 後接 6000 位數字,丟 `ValueError`(整數位數上限),rc1。
- 影響:rc1 對 Claude Code 是非阻擋的錯誤,不會卡住會談,只會多一行鉤子錯誤。stdin 由 Claude Code 自己產生,正常不會出現這些形狀,所以只列 minor。
- 這輪 r2 邊界席 F1 講的是同一個根因(外來 JSON 的巢狀深度與數字大小),修補只套在起點檔,stdin 讀取沒有跟著收。
引句:「except (OSError, ValueError, RecursionError):」
severity: minor
blocking: 否

另有一個沒列為 finding 的觀察:`_unchecked_kind` 用 `{...}.get(data.get("unchecked_kind"), "error")`,欄位值若是清單或字典會丟 `TypeError`(unhashable),實測 rc1。lint-new 實際只會寫字串(`scripts/lumos:40522-40609`),要有人改壞 lint-new 才會觸發,所以不標。

總結:最嚴重是 minor(三支鉤子 stdin 的深層巢狀與非物件輸入處理不一致,只造成非阻擋的 rc1),會擋 0 條。上一輪邊界席 F1–F2 都驗過已修好,未發現誤擋收工、該擋沒擋或留孤兒程序的問題。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/stop-lint-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/check-graph-sync.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/impact-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/_hookshared.py`
