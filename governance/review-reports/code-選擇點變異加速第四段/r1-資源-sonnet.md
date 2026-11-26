severity: minor

我逐 hunk 讀完整份 diff,並在 `/tmp/lumos-seat-work/code-選擇點變異加速第四段/資源-sonnet/r.py` 裡用載入的 `scripts/lumos` 實跑了下面三個重現。

**資源與預算逐項結論**
- 初始化腳本放在 `_isolated_worktree` 的上層暫存資料夾(`scratch=parent`),在工作樹之外,不會被壞法套用或還原的 `git checkout` 碰到。一般離開、例外、Ctrl-C 都由 finally 的 `rmtree(parent)` 收掉。
- `--keep-worktree` 時腳本隨現場保留;被強殺時留在 `/tmp/lumos-kill-*`,跟既有工作樹殘骸同一類,沒有新增洩漏種類。
- `_kill_run` 逾時後 `_kill_proc_group` 加 `proc.wait()`,Ctrl-C 也有收。重試路徑 `_kill_merge_base_run` 同樣走 `_kill_run`,訊號落在中間時丟 `_KillHalt`,沒有新的孤兒程序。
- 事件解析本身是線性掃描。輸出上限 256KB,`_choice_merge_events` 對 1000 個名字乘 1000 個事件實測 0.31 秒,不是問題。

severity: minor
blocking: 否
1. 斷路器恢復後 `hang_streak` 沒歸零,恢復後第一次掛住就立刻再跳開。
引句:「if kind in ("pass", "fail"):   # 跑到測試後逾時的連續次數:通過或有失敗歸零(第四段計劃做法 3)」
重現:連續 15 次 `_kill_merge_breaker(mg,"k","unclean",False,"逾時(跑到測試後掛住)")` 跳開。接著送一次 `"pass"` 試探,恢復成 `(True,'')`,但 `hang_streak` 仍是 15。再送 1 次掛住,輸出 `(False, '斷路器') {'k': 16} trips {'k': 2}`,一次掛住就第二次跳開。
原因:歸零那行寫在「斷路器停用中」那段的 `return` 之後,恢復那一支走不到;跳開時也沒歸零。
影響:只多損失合併加速,不影響判定結果,所以標 minor。
file: `scripts/lumos:29216-29225`

severity: minor
blocking: 否
2. 事件行正則在長輸出行上是二次方時間。
引句:「_CHOICE_MERGE_EVENT_RE = re.compile(r"(?P<cls>\S[^\n]*?) > (?P<name>[^\n]+) (?P<ev>STARTED|PASSED|FAILED|SKIPPED)[ \t\r]*")」
重現:單行 `"a > "*5000`(20KB)`fullmatch` 要 0.44 秒;`"a > "*50000`(200KB,在 256KB 上限內)要 43.7 秒。
原因:每個 ` > ` 位置都讓 `name` 的貪婪量詞回溯到行尾。
限制:每個非事件行都要過這條正則。要踩到,輸出需有首字非空白、含數千個 ` > ` 的單行,平常的 Gradle 輸出不會有,所以給不出一般規模的失敗場景,維持 minor。
建議:先用 `line.endswith(("STARTED","PASSED","FAILED","SKIPPED"))` 預篩。
file: `scripts/lumos:28740`(diff 內該行)

severity: minor
blocking: 否
3. 合併基準重試沿用第一次算好的 `cap`,沒用剩餘時限重算。
引句:「mcmd, el, kind, why = _kill_merge_base_run(mg, c, sh, lane, nf, cap, None)」
場景:第一次(帶腳本)跑了接近 `cap` 才以「找不到 JUnit 結果檔」收場,重試仍可再跑一個完整 `cap`,最壞用掉兩倍的 `min(…, 當時剩餘時限)`,超出總時限。
緩解:重試前有 `c.hk.between()` 檢查時限,所以只會多一次,不會無限。
建議:重試前用 `min(cap, mg.remaining())` 重算。

severity: minor
blocking: 否
4. 跑到測試後逾時的斷路器門檻從 5 次放寬到 15 次,放大壞法掛住時的耗時。
引句:「_CHOICE_MERGE_HANG_BREAKER = 15          # 跑到測試後逾時(多半是壞法讓測試掛住)另外數,連續幾次才跳開(Projects/選擇點變異加速第四段_計劃 做法 3)」
場景:每個掛住的壞法都付一次快篩上限 `max(合併基準耗時×5, 下限)`,再跑逐支流程。15 次的上限總和是原本 5 次的三倍。合併基準耗時 30 秒時,每次上限 150 秒,15 次約 2250 秒,超過總時限 1800 秒,後面的壞法會因時限用完而沒判。
限制:快篩上限已被剩餘時限夾住,所以不會產生錯誤判定,只是多花預算,維持 minor。這是計劃內的取捨,列出供裁。
file: `scripts/lumos:28876`(`_choice_merge_screen_cap`)

**pitfalls manifest(1 條)**
- `scripts/lumos:29050`(資源,`open(`):誤報。該處是 `with open(sh["init"], "w", encoding="utf-8") as fh:`,離開區塊必關。唯一的例外分支 `except OSError` 也只印訊息並把 `sh["init"]` 設成 None。

**圖譜鏡頭**
- `bound-tests-gate` 與 `guard-kill`(rc 優先序、`--json` 純淨):不影響。diff 只改 choice-kill 合併快篩這條路徑,沒碰這兩個合約綁的函式;新增的輸出都走 stderr,`--json` 的 stdout 不變。
- `lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`:不影響。這次沒碰 search 的濾網、還原翻紅釘的規則、re-inject 的 sentinel。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`:不影響。新增的 `merge_init_off` 欄位照 `_GOV_FIELD_TYPES` 登記型別,讀端缺值讀成空字典。
- 其餘「超出上限只列名」的節點:這份 diff 沒有牽連到它們各自宣稱的行為。
- 本次沒有「這次新增的殘留」段,沒有殘留問答需要比對。

最高 minor,blocking 0 條
