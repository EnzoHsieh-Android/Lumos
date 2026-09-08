severity: major

### f1 併發雙寫表態 marker 共用固定暫存檔名,一方拋出未捕捉例外

severity: major
blocking: 是
file: `scripts/lumos:21231`
引句:「暫存+os.replace,同 _write_lf 慣例;r1 外家 F6」
`_codeloop_write_dispositions`(scripts/lumos:21225-21232)呼叫的 `_write_lf`(scripts/lumos:10551-10559)用固定暫存檔名 `<branch>.dispositions.json.tmp-wlf`,兩個行程同時對同一分支跑 `lumos code-loop dispositions` 會共用同一個暫存檔。實測用兩條執行緒交錯呼叫 `_write_lf` 寫同一路徑:一方 `os.replace` 拋 `FileNotFoundError`(暫存檔已被對方搬走)一路傳到 CLI 頂層——`_cmd_codeloop_dispositions`(scripts/lumos:21675-21706)在呼叫這支寫入前後都沒有 try/except——另一方雖回報 OK,最終落盤內容卻是對方寫的那份。

### f2 表態核對的 git 子程序沒有 timeout,20 秒預算形同虛設

severity: major
blocking: 是
file: `scripts/lumos:21296`
引句:「表態核對的時間預算(同派工鏡頭 _LENS_SPEC_BUDGET 慣例)」
`_dispositions_verdict` 的 deadline 只在每題迴圈頂端檢查一次(scripts/lumos:21402),但同一輪會呼叫的 `_git_tree_has`(21288)、`_git_tree_text`(21294,scripts/lumos:21296 即該 subprocess.run 呼叫)、`_disp_check_test` 的 `git grep`(21333)、`_codeloop_record_valid` 的 `git merge-base`/`git diff`(21276、21280)全部沒有帶 `timeout=`。實測把 `git show` 卡 8 秒,`_git_tree_text` 就原地卡滿 8.45 秒,20 秒預算完全攔不住單題卡住的情況;pre-push(`scripts/hooks/pre-push:208`)呼叫 `code-loop check` 同樣沒有外層 timeout,而 S7 又把它改成對每個分支 ref 無條件呼叫,任一次 git 卡住(lock 競爭、網路掛載的 repo)就會讓 `git push` 整個卡死到人工中斷。

### f3 同一 commit 兩筆表態事件因 ts 恆定而在治理帳去重時互相蓋掉

severity: major
blocking: 是
file: `scripts/lumos:21215`
引句:「同 sha 兩筆 dispositions / recall-miss 各算各的,拿 ts 當鑑別子」
`_codeloop_dispositions_gov_log`(scripts/lumos:21215)把呼叫端傳入的 `ts` 原樣寫進治理帳事件,而這個 `ts` 是 `_codeloop_git_ts` 讀到的 HEAD committer date——同一個 commit 不管呼叫幾次都是同一個值,`nodes` 又固定是 `[]`。實測:同一 commit 上因訂正證據重跑 `dispositions` 兩次,兩筆都成功落盤,但 `cmd_gov` 讀側的去重鍵 `(commit, frozenset(nodes), gate, kind, token)`(scripts/lumos:4778,`token` 取自 4732-4734 這段邏輯)把兩筆折成一筆——排序去重保留先出現者,保留的是「訂正前」那筆錯誤證據,訂正後的內容被靜默丟棄(親手重放:2 筆寫入、`ded` 只剩 1 筆,留下的 evidence 是舊值)。

### f4 marker 檔存在但 JSON 壞掉時直接判「沒有表態記錄」而不退治理帳

severity: minor
blocking: 否
file: `scripts/lumos:21244`
引句:「本機 marker 優先;沒有就退治理帳」
`_codeloop_read_dispositions` 只有在 marker 檔「不存在」時才會退去掃治理帳,檔案存在但 `json.loads` 拋例外會直接 `return None`(scripts/lumos:21243-21244),跟「這個分支從沒表態過」在下游完全無法區分。`_dispositions_verdict` 收到 `None` 會印「還沒有表態記錄」並判 `blocked=True`(scripts/lumos:21379-21382),即使治理帳裡其實躺著一筆合法紀錄,開發者也只會被導去整份重填,不是真的沒表態。

### f5 表態 marker 寫入失敗沒有比照治理帳寫入做例外保護

severity: minor
blocking: 否
file: `scripts/lumos:21704`
引句:「★先寫治理帳★(CI 唯一路徑;r2 外家 F2:寫不進去要讓呼叫端知道)」
`_codeloop_dispositions_gov_log` 明確捕捉 `OSError` 並回 `(False, 原因)` 讓呼叫端印出乾淨訊息,但緊接著呼叫的 `_codeloop_write_dispositions`(scripts/lumos:21704)完全沒有 try/except。實測把 `governance/code-loop/` 目錄權限設成 000 後直接呼叫它,`PermissionError` 原樣蓋過去——這時治理帳那筆其實已經寫成功,使用者卻只看到裸 traceback,不是這支指令一貫的「擋下:...」措辭。

### f6 dispatch-lens 在確認快取命中之前無條件多讀一次表態資料

severity: minor
blocking: 否
file: `scripts/lumos:20385`
引句:「表態記錄(表態閘 S8):有才附;快取 key 含它的 sha256」
`cmd_dispatch_lens` 在算出 `cpath` 之前先呼叫 `_codeloop_read_dispositions`(scripts/lumos:20385),對沒有本機 marker 的分支會落到治理帳逐行掃描那條路。實測對本 repo 現有的 `.governance-log.jsonl`(30390 行、4.6MB)掃一次約 18ms;即使最終是 `cache_hit` 也得先付這筆成本,而這本帳只會愈長愈貴,等於讓「命中快取應該幾乎零成本」的假設隨帳齡衰退。

### f7 快取 key 併入可變的表態雜湊,背景暖機行程可能算到跟等待端不同的檔

severity: minor
blocking: 否
file: `scripts/lumos:20268`
引句:「extra=表態記錄的 sha256(表態閘 S8):重表態之後舊快取自然 miss」
鎖檔名衍生自含 `_disp_key` 的 `cpath`(scripts/lumos:20268、20390),而 `_lens_wait_or_warm` 派出的背景行程(`Popen`,scripts/lumos:20319)是重新執行一次 `dispatch-lens`、自己重讀表態記錄再算一次 `cpath`,不是繼承呼叫端已經算好的路徑。若派工與背景行程重算之間剛好有人跑了 `lumos code-loop dispositions`,兩邊會算出不同的 `cpath`;等待端逾時後印「有一支在背景把它算完並寫進快取」,但背景行程其實寫進了另一個檔名,下一次呼叫未必能對上。

## 圖譜鏡頭

- `Systems/bound-tests-gate.md` ★INVARIANT★:未破——`--bound-tests-advisory` 只在非 tier=high 時由 pre-push 傳入(`_ba=(); [[ "$_tier_high" -eq 0 ]] && _ba=(--bound-tests-advisory)`),`_codeloop_guard_verdict` 對 tier=high 路徑仍是「`bt["status"] == "red" and not bound_advisory` → `blocked=True` rc1」;低風險只提醒的行為原本就存在(舊碼另外呼叫 `bound_tests_advisory`),這次只是搬進同一次 `check` 呼叫,語意不變。
- `Systems/canary-audit.md` ★INVARIANT★:不影響——這次 diff 沒有觸及 `canary record`/`second` 的寫入路徑或 gate rc 邏輯。
- `Systems/design-loop.md` ★INVARIANT★(處置閘第五步):不影響——那條講的是設計審迴圈材料格式(.md vs .patch)的判定,跟這次改動的 code-loop 表態閘是同名不同事,程式碼互不重疊。
- `Systems/guard-kill.md` ★INVARIANT★:不影響——沒有觸及 `guard kill` 的 rc 優先序或 `--json` 輸出邏輯。
- `Systems/lumos-cli-lifecycle.md` ★INVARIANT★(re-inject):不影響——沒有觸及 sentinel 覆寫/CLAUDE.md 寫入路徑。
- `Systems/lumos-cli-read.md` ★INVARIANT★(search 排除規則):不影響——沒有觸及 `search` 的 superseded/stale 過濾邏輯。
- `Systems/slim-get-一行安裝.md` ★INVARIANT★(.ps1 ASCII/無 BOM、禁 `$Args`):不影響——沒有觸及任何 `.ps1` 檔。
- `Issues/code-loop守衛main-direct盲區.md` [事故]:不影響——這次改動是強化而非弱化攔截面(pre-push 現在對每個分支 ref 無條件呼叫 `code-loop check`),沒有看到重新開啟該事故所述繞過缺口的跡象。

最嚴重 severity: major,blocking 條數 3
