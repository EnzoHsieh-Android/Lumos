severity: major

**範圍說明**:diff 全部逐 hunk 讀完。事件行解析、重試分支、排序、斷路器各挑具體輸入走過,有兩處實際跑過(見 1、3)。

### Findings

1. 斷路器恢復後,`hang_streak` 沒有歸零,恢復後只要再掛住一次就又跳開
   - 走到的行:`_kill_merge_breaker` 開頭的「斷路器停用中」分支,恢復時只把 `streak` 設 0,然後 `return`。`hang_streak` 歸零的那行在這個 `return` 之後,試探快篩通過或有失敗時走不到。
   - 具體輸入:同一平台連續 15 個壞法的快篩都跑到測試後逾時(跳開,`hang_streak` = 15),之後試探快篩通過、恢復合併,再來 1 個壞法逾時且有 STARTED。
   - 結果:`hang_streak` 變 16,立刻再跳開,還印「合併連續 15 次沒跑乾淨」。實際只連續 1 次,「連續 15 次」的合約被破壞。
   - 重現:`/tmp/lumos-seat-work/code-選擇點變異加速第四段/正確性-sonnet/p.py`,我跑的輸出如下。
     - `reopen (True, '') {'k': 15} {'k': 0}`
     - `after1 hang (False, '斷路器') {'k': 16}`
   - 測試為什麼沒抓到:`t_choice_kill_merge_hang_breaker` 第三案(10、有失敗、10)是在啟用中用 `fail` 歸零,從沒測過「跳開、恢復、再掛」。把歸零移進恢復分支,或不歸零,測試都照綠。
   - file: `scripts/lumos:29221`
   引句:「if kind in ("pass", "fail"):   # 跑到測試後逾時的連續次數:通過或有失敗歸零(第四段計劃做法 3)」
severity: major
   blocking: 是

2. 重試合併基準沿用同一個 `cap`,不重算剩餘時限
   - 走到的行:`cap` 在第一次呼叫前只算一次,重試直接再用它。
   - 具體輸入:帶腳本的第一次基準呼叫花了 X 秒才失敗,沒有結果檔、不是編不過(例如 Gradle 設定階段因與腳本無關的原因失敗),此時 `cap` 等於當時的剩餘時限。重試再被允許跑 `cap` 秒,總耗時最多超出總時限 X 秒。
   - 只有「慢才失敗」才會發生。Gradle 拒收腳本是快失敗,不受影響,所以不是 major。
   引句:「mcmd, el, kind, why = _kill_merge_base_run(mg, c, sh, lane, nf, cap, None)」
severity: minor
   blocking: 否

3. `_CHOICE_MERGE_EVENT_RE` 對含大量 ` > ` 的長單行輸出是二次方時間
   - 實測 `_choice_merge_events("a > "*n, ["x"])`:n=5000 約 0.45 秒,n=20000 約 7.2 秒,n=60000 約 63.5 秒。
   - 輸出上限 256KB,一條頂格長行就能卡住快篩收尾。行尾不是四個事件字樣時,正規式仍對每個 ` > ` 位置各做一次線性回溯。
   - 輸入不是惡意造不出來,威脅模型也是單人,所以只給 minor。
   - 修法:先用 `line.endswith(("STARTED","PASSED","FAILED","SKIPPED"))` 預篩,再跑正規式。
   引句:「_CHOICE_MERGE_EVENT_RE = re.compile(r"(?P<cls>\S[^\n]*?) > (?P<name>[^\n]+) (?P<ev>STARTED|PASSED|FAILED|SKIPPED)[ \t\r]*")」
severity: minor
   blocking: 否

### 逐項查證後判對的部分

- **重試條件**:只有 `why == "找不到 JUnit 結果檔"` 且 `sh.get("init")` 非空才重試。逾時、編不過、rc 1 但有結果檔都不重試,快篩用的是重試那次回傳的不帶腳本 `mcmd`,沒有用錯指令。
- **腳本寫不進去**:`sh["init"]` 改 None 後不會觸發重試。
- **`scratch`**:`getattr(_iw, "scratch", None)` 接住沒有 scratch 的現場。`scratch` 是 `mkdtemp` 的上層,`wt` 在它底下,結果資料夾圍欄不受影響;`keep` 時一起留,不會洩漏。
- **腳本寫一半被 Ctrl-C**:腳本在 `scratch`,收尾整個資料夾一起刪。
- **新舊帳互讀**:新程式讀舊帳靠 `or {}`。舊程式讀新帳,`merge_init_off` 是未知鍵,被忽略。
- **四層排序**:`front + mid + tail`,`tail` 內 `rank` 是 `hung + passed`,所以紅、未知、掛住、通過的順序成立。只改順序不改判定;最差情況是「合併裡通過、單支卻紅」的測試排到最後,被前面單支逾時的判掛住先停。這跟 `--no-merge` 的原順序有差,但不會變成存活,屬於可接受的排序取捨。
- **事件行**:行首空白被 `\S` 擋掉。`> Task ... FAILED` 與 `FAILURE:` 不命中。`[1]` 這類參數尾巴由 `_choice_merge_fullname` 去掉。截斷時不進掛住層。其他漏認只會讓測試落到未知層,不影響判定。

### Manifest

- scripts/lumos:29050 `open(...)`:**誤報**。它在 `with open(...) as fh:` 裡,離開區塊確定 close。

### 圖譜鏡頭

- 固定席的 `bound-tests-gate`、`lumos-cli-read`、`guard-kill`、`測試假綠形態`、`lumos-cli-lifecycle` 這些合約,這份 diff 都沒破壞。
  - 沒碰 guard-kill 的 rc 優先序或 `--json` 輸出。
  - 沒碰 search 濾網與 re-inject。
  - 沒碰 code-loop check 的綁定測試真跑邏輯。
- `測試假綠形態` 的「還原翻紅釘需前置斷言」:新測試多數有現場成立的檢查(如 `inits`、`merged_starts`)。但上面 finding 1 正是一條沒有被任何測試路徑執行到的分支。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger` 這三個 RISK 節點,這份 diff 沒有走進它們宣稱的行為。
- 合約行沒有「帶殘留」徽章,尾端也沒有「這次新增的殘留」段,所以沒有殘留決策可逐型答。
- 這份 diff 沒有換編號或改字重問任何殘留,也沒有找第二個代理。

最高 major,blocking 1 條
