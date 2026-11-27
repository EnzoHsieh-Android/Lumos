severity: minor

我把「資源」鏡頭要求的三類路徑都過了一遍。第一類是子程序收尾，第二類是時間預算，第三類是大檔與二次方工作。沒有找到會讓正常操作超時、判錯，或留下孤兒程序的缺陷。只有兩條可以更省的 minor。

**已過的項目**

- **子程序收尾**：`_kill_run` 對合批編譯的呼叫帶 `merge=self.prep`，Popen 帶「合併」標記。第一個訊號由 `_kill_signal_marked` 當場收掉整個程序群組，逾時與 Ctrl-C 兩條路徑也都 killpg 後 wait，所以沒有孤兒程序。`apply_compile` 的 `finally: self.restore` 讓 `_KillHalt`、逾時、例外都會先還原再往外丟。
- **編譯預算**：`cap()` 取剩餘預算、剩餘總時限、單支上限的最小值。每次寫檔前都會檢查，預算不夠就回 None 並記 `budget`。檢查之外還有每次編譯固定的約 2 到 4 秒等秒與還原開銷，它們都算進 `csecs`，所以最多超出一次呼叫的固定開銷，不會擋掉後面的測試階段。
- **二次方工作**：`probes()` 的 `while old and more` 迴圈確實是二次方，因為 `old` 不會縮小。我在合成檔上測過，3000 行檔加一行 68 個候選，69 次呼叫共 0.05 秒，可以忽略。
- **讀帳**：`_choice_push_scan` 提前讀 B 版帳。對本 repo 的 22MB 帳，`_choice_push_ledger` 約 0.08 秒，`_gov_vc_gate_events` 約 0.17 秒。帳讀不了時，後面照原路徑擋下，行為沒變。
- **帳的長大**：同一個 (檔, 行指紋, new_sha) 在 blob 沒變時會被跳過集合擋住，不會重複記 invalid。exhausted 的行下一次的狀態是 exhausted，不會再進待跑清單，所以帳不會無限增長。

**minor 一：整份檔剝註解，用量跟檔案大小成正比**

severity: minor
blocking: 否

`scripts/lumos` 的 `_choice_cov_pkg_of` 現在先對整份文字做區塊註解蓋空白，再找 package。以前 `PKG_RE.search` 第一個命中就停。壞法行端那邊讀的是整份檔，`_choice_cov_req` 每個壞法行呼叫一次，`on_swap` 換候選時再呼叫一次。

我實測一支 3.4MB、含大量 `/* */` 與 KDoc 的檔，一次呼叫約 0.15 秒，舊寫法約 1 微秒。最多 30 個壞法加每次換候選，同一支大檔最壞多 4 到 5 秒，發生在跑任何測試之前，也不受 `--max-seconds` 管。實務上的檔小得多，所以只是浪費，不會判錯。修法是掃主程式套件那邊讀檔頭，壞法行這邊也只讀檔頭，或同一支檔快取。

引句:「m = _CHOICE_COV_PKG_RE.search(_CHOICE_COV_BLOCK_COMMENT_RE.sub(lambda x: re.sub(r"[^\n]", " ", x.group(0)), text))」

位置：`scripts/lumos:80206` 與 `scripts/lumos:80409`。

**minor 二：編譯輸出超過 256KB 時整批偵測失效**

severity: minor
blocking: 否

未能重現，所以維持 minor。`_choice_compile_errors` 遇到 `_kill_cap` 的截斷標記就回 None，這一批一個無效壞法都不記。`compile()` 呼叫 `_kill_run` 時沒傳 `keep_re`，所以被砍掉的中段裡的 `e:` 行不會保留。

具體情境：Android 大專案裡，被壞法波及的依賴檔重編，吐出大量 `w:` 警告把輸出推過 256KB。這時對照組、批次編譯與還原的成本都付了，卻一個無效壞法也沒抓到。編不過的壞法全部落回測試階段，各自再付一次編譯，比不開檢查還慢。這是失效開放，不會判錯，只是退化成沒有加速。可以改成只保留 `^e: ` 行（`keep_re` 上限 20 行，不夠就要自己另存 `e:` 行），或在 `_kill_run` 之外另建專用的錯誤行過濾。

引句:「if "...[truncated " in str(out or ""):」

位置：`scripts/lumos` 的 `_choice_compile_errors`（patch 的 r1-pack-code.patch 約第 605 行）。

**範圍外、不報**

- `restore` 在 `_KillPrepAbort` 時中斷迴圈，後面的檔案沒還原。但該平台組會作廢、不再跑測試，隔離樹最後也會被收掉，屬 `_KillPrepAbort` 的既定語意。
- 探針在紅時不記錄，所以每次 run 都會重編一批。這是計劃〈用詞〉跳過集合明寫的行為。
- 併發類題目依派工詞判範圍外。

臨時目錄 `/tmp/lumos-seat-work/code-選擇點存活回指第二段/r1-資源-sonnet` 已用字面絕對路徑刪除。

總結:最高等級是 minor
