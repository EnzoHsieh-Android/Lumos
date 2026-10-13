severity: minor

整體判斷:launch/reap 協定的主線(鎖次序、Condition 通知、`returncode` 判斷、`_kill_proc_group` 取代三處舊寫法)我沒找到 blocker 或 major。下面兩條 minor 是我實際跑過的結果。

## 1. 重試迴圈每次 Ctrl-C 都重置 30 秒上限,上限在連按 Ctrl-C 時失效
severity: minor
blocking: 否
引句:「                    procs.reap()
                    return
                except KeyboardInterrupt:
                    continue」
file: `scripts/lumos:48273`
file: `scripts/lumos:48360`

1. 輸入:同時跑兩支測試,t_g0 的 Popen 開出程序後在交回前卡住(探針延遲 45 秒),主流程被 SIGINT。
2. 走到:`reap()` 在 `while self._opening and deadline > ...` 等 Condition。每次 SIGINT 都讓 `reap` 丟 `KeyboardInterrupt`,`_settle_and_reap` 的 `continue` 重新呼叫 `reap()`,`deadline` 重算成新的 30 秒。
3. 重現:我用 `_bt_spawn_probe` 讓 t_g0 開完後卡 45 秒,每 8 秒送一次 SIGINT。程序在 8、16、24、32、40 秒都還活著。沒有第 2 次 Ctrl-C 時,30 秒一到就會收尾退出。
4. 壞在哪:使用者想停下卡住的收尾,越按越停不下來,只能 SIGTERM 或 SIGKILL。註解寫「reap 自己最多等 30 秒,所以這裡不會卡死」,與實測不符。觸發條件(Popen 本身卡住)罕見,所以只標 minor。
5. 修法:`deadline` 由 `_settle_and_reap` 在迴圈外算一次,傳進 `reap(deadline=...)`。

## 2. t_bound_tests_parallel_error_stops_fast 的延遲設定是死碼,「0.3 秒後才出錯」沒有發生
severity: minor
blocking: 否
引句:「str(sp), _j.dumps({"no-such-dir": [0.3, 0]})], capture_output=True, text=True, timeout=60)」
file: `scripts/test_lumos.py:50199`

1. 探針用 `s in str(cmd)` 比對延遲鍵。`cmd` 是 `"{python} run.py {method}"` 展開後的字串,不含 `no-such-dir`(那是 cwd,不在指令裡)。
2. 實測輸出「整個程式 5 秒內結束…(實際 0.1 秒)」與「(實際 0.2 秒)」。都小於 0.3 秒,表示延遲沒生效,出錯那支是立刻失敗。
3. 後果:註解和 `前置` 檢查想保證「出錯前慢測試已開出程序」,實際靠另一條執行緒在主流程每 0.1 秒輪詢之前恰好先開出程序。目前連跑 3 次都綠,忙碌機器上可能在 `前置` 檢查誤紅。
4. 修法:鍵改成 `t_g0`,並讓出錯那支的指令字串帶得出該子字串。或在探針裡改用 `cwd` 比對。

## 鏡頭逐條判定
- 孤兒與卡死:`launch` 在鎖內檢查 `_stop` 並計數 `_opening`。`finally` 裡登記、減數、`notify_all` 都在同一把鎖內,沒有漏通知。`reap` 立標記後等 `_opening` 歸零再快照 `_procs`,沒有被漏收的空檔。標記立了之後才開完的,`launch` 當下自己收掉。
- 次序:`reap` 和 `launch` 只用 `_cond` 一把鎖,和 `_run_bound_tests` 的 `lock` 沒有巢狀,沒有死鎖。
- `_BtStopped`:只有在 `reap` 立標記之後才會丟,那時 `errs[0]` 已經是原因,主流程丟的是 `errs[0]`,不會被它蓋掉。
- 雙重擊殺:標記立了之後才開完的程序,可能被 `launch` 和 `reap` 都砍一次。第二次 `killpg` 只有在 pgid 被重用時才會誤殺,窗口極小,不標。
- 30 秒之後才開完的程序:註解說「開完當下收掉」,但那時主流程已往外丟、程式結束,守護執行緒可能來不及砍。這只在 Popen 卡超過 30 秒時發生,屬極端情形,不標。
- `_kill_run` 沒給 `started`:走原本的 `_popen()`,行為與改前一致。`_lint_run_and_parse` 逾時改走 `_kill_proc_group`:Windows 沒有 `killpg` 時改為退回 `proc.kill()`(舊版會留下 AttributeError),屬行為改善。`getpgid` 換成 `proc.pid` 在 `start_new_session=True` 下等價。
- 背景分片繼承忽略 SIGINT:新測試用的 `_bt_spawn_probe` 第一行把 SIGINT 裝回 `default_int_handler`,不會因繼承忽略而誤紅。
- 翻紅能力:`interrupt_reaps`、`slow_spawn_reaped` 都有「確實開了程序、確實被中斷或例外」的前置檢查,拿掉對應修補會翻紅。我沒有逐一做還原實驗。
- 資料狀態五問:不涉及持久資料格式或不可逆操作,不適用。

總結:最高等級 minor
