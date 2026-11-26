severity: major

**發現 1:覆蓋造成的紅燈沒有任何煞車,每支測試多跑一次,會把總時限吃光(比不開覆蓋慢)**

severity: major
blocking: 是
`scripts/lumos:79722`(`_CovBase.breaker`)、`scripts/lumos:79800`(`red_rerun`)、`scripts/lumos:29231`(`_kill_measure_singles` 收 `after` 回傳的那份)

引句:「need = min(_CHOICE_COV_BREAKER, self.n_robo - self.red)」

失敗場景:
- 初始化腳本在某個 AGP 或 Gradle 版本上讓每次掛覆蓋的呼叫都紅,例如設定階段就被拒收,或 `enableUnitTestCoverage` 不認得。
- `red_rerun` 對每支都再跑一次不掛覆蓋的版本。紅的不進斷路器,`red` 增加讓 `need` 一路降到 0,`need <= 0` 就直接 return,斷路器永遠不跳。
- 結果是 N 支測試各多一次失敗呼叫,而且每次都再重跑一次(逐支基準至少兩倍呼叫)。不開覆蓋時只有一次。
- 耗時預估也被低估:`after` 回傳的是 plain 那份,`measured.append(b_el)` 只記 plain 的秒數,掛覆蓋失敗那趟的秒數沒進預估。
- 「剩下的總時限 < 平均 × 剩餘支數 × 1.5」這道收手門因此太晚觸發,總時限被基準吃光,一個壞法都不判。這正是 guard-kill 那篇 PITFALL 要防的情形。
- 規格寫的「掛覆蓋紅的不算進斷路器」把這條路整個放在煞車外面。

最小重現(已跑,結果 `tripped False red 40 plain reruns 40`):
- 腳本:`/tmp/lumos-seat-work/code-選擇點存活回指條款第一段/資源-sonnet/rep.py`。
- 做法:用 `python3.14 -I` 載入 `scripts/lumos`,把 `_kill_run` 換成假的。
- 輸入:40 支 Robolectric 測試,每支掛覆蓋回 rc 1。
- 輸出:`tripped False`、`red 40`、`plain reruns 40`。

建議:連續 K 支(例如 3 到 5 支)掛覆蓋才紅、不掛才綠時就斷路(之後都不掛),並把掛覆蓋那趟的秒數併進耗時預估。

**發現 2:掛覆蓋紅後重跑的那次不帶當場收的標記,上限也沒照剩下的總時限重算**

severity: minor
blocking: 否
`scripts/lumos:79800`

引句:「plain = _kill_run(self._cmd[n], self.c.run_dir, cap)」

- 失敗場景 1:第一個中斷訊號來時,這次呼叫沒有 `merge=` 標記,`_KillPrep.on_signal` 收不到它,要等一整支測試跑完(最長 600 秒)才停。這跟新增的 PITFALL「第一個中斷訊號要等一整支 Robolectric 測試才停」是同一件事,而且在這條路上沒修。
- 失敗場景 2:`cap` 是掛覆蓋那趟開跑前算的。若掛覆蓋那趟剛好用滿 `cap == full`(剩下 600 秒以上時)後逾時,重跑再給一次整個 `cap`,總時限可能超出最多約 600 秒。這跟 guard-kill 已記的 PITFALL「快篩逾時上限不受剩下總時限約束」是同一族。
- 未能重現:只確認了重跑呼叫沒帶標記(假 `_kill_run` 收到 `merge=None`),沒有真的送訊號或真逾時,所以自降一級。

**發現 3:分析呼叫沒有替壞法階段留餘裕**

severity: minor
blocking: 否
`scripts/lumos:79644` 到 `79645`

引句:「if self.remaining() < cap:」

- 失敗場景:量完基準後剩下時間剛好略大於 `cap`(至少 60 秒),分析就會開跑並用掉最多 `cap`。壞法階段剩下接近 0,第一個 `hk.between` 就停,零個壞法判完。
- 不開覆蓋時,同樣的預算至少會判 1 個。
- 修法:門檻改成 `cap` 加上至少一個壞法的預估。
- 未能重現:這是推理,沒有實際跑出。

**發現 4:沒開覆蓋的 choice-kill 也多做整棵樹的 git 查詢**

severity: minor
blocking: 否
`scripts/lumos:80198`(`_choice_kill_cov`)、`scripts/lumos:79127`

引句:「tree = _choice_tree_oids(rr, at_sha, deadline=deadline)」

- 場景:`cov_plats` 為空(沒設 `coverage: true`)時仍無條件跑 `_choice_tree_oids`,也就是整棵樹的 `ls-tree`,規格卻說沒開覆蓋時行為不變。
- 同族:`_choice_reach_cur` 在 `choice-points` 每次呼叫都跑 `_choice_test_blobs` 加 `_choice_tree_oids`(`scripts/lumos:78699` 附近),即使沒有任何存活行,且 `_choice_test_blobs` 這裡沒帶期限。大 repo 上原本唯讀、很快的 `choice-points` 會變慢。
- 只是可以更省,沒有錯的行為。

**已查過、沒找到洞的資源面**
- 子程序收尾:覆蓋基準與分析呼叫都帶 `merge` 標記並登記在 `_KILL_RUN_LIVE`,逾時與 KeyboardInterrupt 由 `_kill_run` 收整個程序群組。`_KillHalt` 在 `cmd_guard_kill` 外層被接住,隔離樹由既有 `with` 收掉。發現 2 那一次重跑除外。
- 記憶體:單份 exec 和分析輸出都有 8MB 讀取上限,同一時間只持有一份。分析輸出可能超過 8MB 時會被當「分析失敗」處理,不會爆記憶體。
- 續跑快取:只留最近 2 個 at_sha。同一個 at_sha 內鍵固定(含測試檔 blob),不會無限長大;`.tmp` 殘檔最壞留到該目錄被清掉為止。

**圖譜固定席**(只附到 `guard-kill.md` 的兩條 INVARIANT,其餘節點鏡頭超時沒附)
- `guard kill rc 優先序`(`t_guard_kill_rc_precedence`):prep 只改配方子集,不改 rc 判定。沒有被這份 diff 動搖。
- `guard kill --json` 純度(`t_guard_kill_json_purity`):prep 的提示全部走標準錯誤。沒有被這份 diff 動搖。
- 同一篇的 PITFALL「量基準把總時限吃光」:共用的 `_kill_measure_singles` 在不掛覆蓋時行為不變。掛覆蓋後發現 1 和發現 3 守不住這條 PITFALL,筆記該補一條說明。

總結:最高等級是 major(1 條 major、3 條 minor)
