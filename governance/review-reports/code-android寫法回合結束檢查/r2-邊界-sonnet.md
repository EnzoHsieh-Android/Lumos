severity: minor

我把 r2 乙包 patch 讀完。HEAD a1456f8f6 已含這次修補,我 `git clone --shared` 一份到臨時目錄,用假的 lumos、隔離的 HOME 實跑 `stop-lint-hook.py`。`check-graph-sync.py` 的標記函式與三支鉤子的 `_trusted_lumos` 與預算函式另外直接載入比對。臨時目錄已刪。

**第一輪 F1–F4 核對**
- F1(擋停訊息截斷)已修好。
  - 3 條、10 條、12 條告警都完整輸出;12 條時結尾「另 2 條」保留。
  - 3000 次隨機輸入,整段都沒超過 1500 字,「另 N 條」的數字也都對得上。
  - 放行指令照原樣印,帶反引號或非字串的整行改成指去 `--all`。
- F2(逾時記成 ok)已修好。
  - 實跑逾時,`hook-events.jsonl` 記 `timeout`。
  - lint-new 拋 traceback 記 `error`。
  - 工具跑不出結果(rc3 且 `env-unavailable`)記 `error`。
  - 預算沒跑到(rc3 且 `budget` / `too-long`)記 `timeout`。
- F3(起點檔與 payload 型別錯)大部分修好,還剩兩個漏網,見下方 F1。
  - 修好的有:`t` 是字串、清單、dict、inf、NaN、負數、空檔、二進位檔,`prompt_id` 是清單,`cwd` 是整數或含 `\0`,`session_id` 是整數或 dict。
  - 這些都 rc0 放行,不丟例外。
- F4(Windows 沒有 killpg)已修好。
  - `_killpg` 先判 `hasattr(os, "killpg")`。
  - Windows 路徑不會碰到 `signal.SIGKILL`,因為 `_alive_group` 在那裡恆為 False。

**其他邊界檢查,沒有問題**
- 訊號在 Popen 前、Popen 內、登記之後送,40 個不同延遲,零殘留程序。
- 在 Popen 回傳前注入 SIGTERM:pending 旗標正確,收掉 lint-new,rc0,零孤兒。
- 三支鉤子的 `_trusted_lumos`、`_outer_budget`、`_inner_budget` 語法樹與原始碼逐字一致(各支雜湊相同)。
- 標記檔名新舊互讀:舊版寫的同名檔仍被認出,不會重複擋。`""`、`.`、`..` 回 None。`/`、`\0`、換行都被換成底線。
- 告警 0 條(blocked 但 `new` 為空)直接放行,不輸出。

F1 起點檔內容是超大整數或深層巢狀時,鉤子仍然丟例外(rc1)
- 輸入一:`stop-turn/<會談>` 內容 `{"prompt_id":"p1","t":1<後面 400 個 0>}`。
- 實際:`OverflowError: int too large to convert to float`,rc1。
- 預期:rc0,印「沒記到起點」。
- 原因:`_turn_start` 只接 `(TypeError, ValueError)`,`float(超大 int)` 丟的是 `OverflowError`。
- 輸入二:起點檔內容是 20 萬個 `[`。
- 實際:`RecursionError: Stack overflow while decoding a JSON array`,rc1。
- 原因:讀檔那段只接 `(OSError, ValueError)`。
- 觸發條件:這支鉤子自己寫的 `t` 一定是 float,只有起點檔被手動改壞才會碰到,所以只列 minor。
引句:「except (TypeError, ValueError):」
severity: minor
blocking: 否

F2 鉤子收到 SIGINT 或 SIGHUP(或其他未捕捉例外)時,lint-new 變孤兒
- 輸入:lint-new 在跑(假的睡 60 秒),對鉤子送 SIGINT,另一次送 SIGHUP。
- 實際:鉤子 rc -2 / -1,`pgrep` 各留下一個 lint-new 程序。
  - 原因:`finally` 只還原 SIGTERM 處理器並刪登記檔,不收 proc。
  - lint-new 在自己的 session 裡,不會跟著死。
- 預期:跟 SIGTERM 路徑一樣收掉。
- r1-intake 的乙組寫了「SIGINT 與例外路徑也收工具群組」。這次 patch 的鉤子端沒有對應修補;r1 資源席 F4 原本講的是 lint-new 端。
- 緩解:lint-new 有自己的 `--budget`(最多 inner-2 秒,約 19 秒),孤兒會自己結束,所以列 minor。
引句:「_STATE["proc"] = None」
severity: minor
blocking: 否

總結:最嚴重是 minor(起點檔超大整數或深層巢狀仍丟例外、SIGINT 或 SIGHUP 留下短命孤兒 lint-new),會擋 0 條;第一輪 F1–F4 都已驗證修好或只剩 minor 的邊角。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/stop-lint-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/_hookshared.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/check-graph-sync.py`
