severity: minor

**1. 主流程等待迴圈在第 0 條執行緒結束後變成忙等,吃滿一顆核心**
severity: minor
blocking: 否
引句:「while any(th.is_alive() for th in threads) and not errs:」
- 輸入:任何 `parallel>=2` 且各支耗時不均的批次。例如 51 支裡,第 0 條工作執行緒先把佇列領空,其他執行緒還在跑最後幾支慢測試。
- 路徑:迴圈體是 `threads[0].join(0.1)`。`threads[0]` 一旦結束,`join` 會立刻回傳,0.1 秒的節流就沒了,迴圈變成緊密空轉,直到最後一條執行緒收工。
- 實測:在 /tmp 用 python3.14 複製這段迴圈,執行緒 0 只活 0.1 秒、另一條活 2 秒。迴圈轉了 3,145,788 圈,CPU 時間 1.9 秒,等於 2 秒內吃滿一顆核心。
- 後果:結果不會錯。但閘跑到收尾時,主流程跟測試子程序搶 CPU,在慢機器上可能把接近 180 秒逾時的測試推過線,造成假紅。
- 修法:改成 `any_alive` 迴圈裡用 `time.sleep(0.1)`,或對還活著的第一條執行緒 join。

**2. Ctrl-C 之後 daemon 工作者還會繼續派新測試**
severity: minor
blocking: 否
引句:「except BaseException as e:   # 開不了程序之類;交給主流程往外丟」
- 輸入:並行跑到一半按 Ctrl-C。
- 路徑:`KeyboardInterrupt` 只丟在主執行緒的 `join`。`errs` 此時仍是空的,工作者的 `while not errs` 條件繼續成立,會繼續從 `todo` 取新指令啟動子程序。
- 後果:如果呼叫端接住 `KeyboardInterrupt` 後沒馬上結束程序,新測試仍會一支支被派出去。註解寫「跟循序時按 Ctrl-C 一樣」,但循序時不會再派新的。
- ⚠ 我沒有實際跑過 `pp_stop_if_signaled` 之後程序多快退出,所以只標 minor。
- 修法:主流程用 `try/except BaseException` 包住等待迴圈,往外丟之前先把一個停止旗標設成真。

**3. 牆上時間用 `time.time()`,時鐘倒退時 secs 可能是負值**
severity: minor
blocking: 否
引句:「_wall = round(_time.time() - _t_run, 1)」
- 輸入:跑測試的那段期間系統時鐘被往回調,例如 NTP 校時。
- 路徑:`_wall` 變成負數,直接成為 `secs`,並寫進回報和記帳(帶 `secs_kind: wall`)。以前是各項秒數相加,不會是負的。
- 後果:記帳出現負值,下游若拿 secs 算統計或門檻會誤判。
- 修法:改用 `time.monotonic()`,或取 `max(0, …)`。

**4. 新舊帳 secs 語意混讀**
- 沒有發現會出錯的讀者:diff 內只有 `lumos` 第 48568 行印 `v['secs']`,舊帳沒帶 `secs_kind` 也不影響。
- 圖譜規則要求「回頭條件」的量測(例如「三次 check 超過 3 分鐘」)要以 `secs_kind` 分開讀,diff 沒有改這些地方,所以只靠筆記提醒。
- 沒有具體失敗場景,不標 finding。

**逐 hunk 走過、判為正確的部分**
- `plan` 以 `len(how)==2` 區分「已定紅/無指令」與「待跑」兩種項目,另一種是三元組,不會混淆。
- `jobs[key]` 的 `timeout` 和 `keep_re` 由同一個 key 的第一個項目決定,與舊的 `seen` 快取行為一致。
- 主迴圈結束條件:先看 `any(is_alive)`,結束後再檢查 `errs`,所以工作者在最後一刻把例外放進 `errs` 也不會漏掉。
- 例外丟出後,其他工作者的結果被丟棄,但已開跑的子程序在自己的程序群組裡跑到逾時,和循序按 Ctrl-C 的孤兒行為相同。
- `_bound_tests_parallel`:`None`、`1`、`1.0` 靜默回 1;布林、`0`、負數、小數、字串、大於 16 會出聲;`bound_tests` 不是物件也會出聲。`True` 因 `isinstance(bool)` 這一條會被擋。
- `no-config` 路徑:`secs` 仍是 0.0,沒有受影響。

**測試判斷**
- `t_bound_tests_parallel_config_values` 用 `running/` 標記判斷有沒有同時跑,判準獨立。在舊實作下 `val=3` 看不到別支,會紅。
- `t_bound_tests_parallel_matches_sequential` 在舊實作下會綠,因為舊實作忽略設定。它是等價性測試,不是翻紅釘,這是設計使然。
- `t_bound_tests_parallel_error_stops_fast` 要求整個程式 5 秒內結束,包含載入約 5 萬行的 `lumos`,慢機器上有假紅風險。
- 同一支測試的 S5 檢查用 `pgrep -f str(d)` 清除殘留慢測試,範圍限定在自己的暫存目錄,符合規範。
- `t_bound_tests_secs_is_wall_time` 的區間 1.8 到 3.5 秒:舊實作會報約 4 秒,會紅;慢機器上 2 秒睡眠加載入可能超過 3.5,有輕微假紅風險。
- 我沒有驗證 4 路同時跑 `python3.14 scripts/test_lumos.py -k …` 時,各測試之間有沒有共用的固定路徑。

**圖譜鏡頭**
- `guard-kill`:diff 沒動 rc 優先序或 `--json` 輸出。`_kill_run` 仍每支呼叫一次,不影響這兩條合約。
- `lumos-cli-read`:搜尋濾網未動。
- `測試假綠形態`:新測試 S2、S5 有前置斷言(`saw` 標記、`RAISED`),符合「現場要真的走到被測路徑」的要求。S1 在舊實作下會綠,但它不是修 bug 的翻紅釘,不違反這條。
- `bound-tests-gate`:「受波及合約測試任一紅、懸空、偽證據、不可過濾證不出跑過就擋」的判定邏輯未動。去重、`unproven`、`whole-suite` 的判定都沿用,只改排程。
- `lumos-cli-lifecycle`、`design-loop`:未牽連。
- `loop-convergence-recording`、`pitfalls-code-loop`(RISK 節點):`_bound_tests_log` 多寫 `secs_kind`,沒有改動帳的既有欄位語意。
- 其餘「只列名」的節點:diff 沒有碰到它們宣稱的行為。

總結:最高等級 minor
