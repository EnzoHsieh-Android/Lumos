severity: major

1. 斷路器跳開後試探快篩恢復了,但「跑到測試後逾時」的連續計數沒歸零。恢復後的第一次掛住就立刻再跳開,印的「連續 15 次」也不是真的。
引句:「        if kind in ("pass", "fail"):   # 讀到了結果檔才算恢復;編不過沒讀結果檔,不算」
file: `scripts/lumos:29123`(`_kill_merge_breaker` 的試探分支)。恢復分支只清 `streak`、加 `reopen`,然後直接 `return`。`hang_streak` 的歸零寫在這個 `return` 之後,試探路徑走不到。
最小重現(python3.14 載入 scripts/lumos 實跑):
   - 對同一平台餵 15 次 `kind="unclean", why=_CHOICE_MERGE_HANG_WHY`,斷路器停用,`hang_streak` 是 15。
   - 再餵 1 次 `pass`(試探恢復),`plats` 回到 `(True, '')`,`hang_streak` 仍是 15,`streak` 是 0。
   - 再餵 1 次掛住,`plats` 變回 `(False, '斷路器')`、`hang_streak` 變成 16、`trips` 加到 2。標準錯誤第二次印出「合併連續 15 次沒跑乾淨」,實際只連續 1 次。
   - 後果:恢復後該平台立刻失去合併快篩,退回逐支。判定不變,但第四段想用「另外數、15 次才跳」留住的快篩加速被吃掉,`merge_trips` 也被灌水。
   - 這屬於「改變行為但不改判定」的速度損失,按判準降一級,標 major 是因為它讓宣稱的計數規則(連續 15 次才跳)失效。測試 `t_choice_kill_merge_hang_breaker` 的「停用中試探逾時有事件行 → 不恢復」那案沒覆蓋「恢復後再掛住」。
severity: major
blocking: 是

2. 帶事件腳本的合併基準重試,第二次沿用第一次算好的 `cap`,沒扣掉第一次已花的時間。
引句:「            mcmd, el, kind, why = _kill_merge_base_run(mg, c, sh, lane, nf, cap, None)」
file: `scripts/lumos:29096`。`cap = _choice_merge_base_cap(..., max(mg.remaining(), 1.0))` 只算一次。
具體輸入:第一次帶腳本的基準跑了接近 `cap` 秒才以「找不到 JUnit 結果檔」結束。例如 Gradle 沒逾時,但結果檔不在預期資料夾。第二次再給一整個 `cap`,合計最多 2×cap,可能超過總時限 `mg.deadline`。後果只有時限超出,不改判定。這種「腳本無關、仍重試」的情形,註解自己也承認是白跑。
severity: minor
blocking: 否

3. 判準疑點:`_choice_merge_events` 用 `_choice_merge_fullname` 把測試名從第一個 `(` 或 `[` 起截掉,Kotlin 反引號名含括號會對不到。
引句:「        full = _choice_merge_fullname(mt.group("cls") + "::" + mt.group("name"))」
具體輸入:Gradle 印 `x.V > foo (bar) FAILED`,`fullname` 得 `x.V.foo `(尾端有空白),`_choice_merge_hits` 對 `m="foo (bar)"` 為 0。這支紅的測試落到未知層,排不到最前面,只影響逐支順序。這是沿用既有 `_choice_merge_fullname` 的行為。
severity: minor
blocking: 否

逐項實測、沒問題的輸入:
- 事件行的 CRLF 與尾端空白(含 tab)都能解析,`splitlines` 先剝掉 `\r`。
- 類別簡名或全名都吃得下。
- 名字含 ` > ` 的 `a b > c` 在第一個 ` > ` 切出類別,能正確對到。
- 參數化 `t1(int)` 與 `[1]` 都對得到。
- 截斷標記出現時掛住層清空。
- 只有一支測試、空輸出時三層都空。
- run_cmd 的 `--tests` 段後面接 `&& echo done` 時,`--init-script` 插在 `&&` 之前,路徑含空白會被 shlex 引號包好。
- Gradle 拒收初始化腳本的訊息不會被 `_KILL_COMPILE_RE` 誤判成編不過,所以重試條件走得到。

pitfalls manifest(1 條,`scripts/lumos:29050` 的 `open(`):`with open(...)` 在 `_choice_merge_init_write`,確定關閉。寫失敗的 `OSError` 被接住並把 `sh["init"]` 改成 `None`,這條不成立。

圖譜鏡頭:
- 固定席的 `guard-kill` 合約 `t_guard_kill_rc_precedence` 管 rc 優先序,diff 沒碰判定路徑,合併仍只能判「全存活」。
- `bound-tests-gate`、`測試假綠形態` 等其餘合約,這次改動沒有破壞其宣稱的行為。
- 「殘留」段:這次沒附,不適用。

最高 major,blocking 1 條
