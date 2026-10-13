severity: clean

我沒有找到 blocker、major 或 minor 的 finding。下面是各鏡頭的逐條判定和三問的回答。

## 鏡頭逐條判定

**1. launch/reap 協定的正確性**
- 登記與「收尾中」標記都在同一把 Condition 鎖內讀寫。reap 立標記後才進來的 launch 一定丟 `_BtStopped`。在標記之前已數過「正在開」的,reap 會等它,或等到期限後由 launch 在開完當下 `_kill_proc_group`。我找不到「已開完卻沒被收」的交錯。
- 過了期限才開完的程序:launch 的 finally 在鎖內登記並讀到 `stop=True`,鎖外砍。我用探針實測(popen 卡 3 秒、`wait=1`),結果是「late proc dead: True」。
- `_BtStopped` 從工作執行緒丟出時,被 `_worker` 的 `except BaseException` 接住並 append 進 `errs`。因為標記只會在 `errs` 已有第一筆之後才立,所以 `errs[0]` 一定是真正的原因,不會是 `_BtStopped`。
- notify 與等待:`_opening` 減一和 `notify_all` 在同一個鎖內,popen 丟例外也走 finally。`wait()` 的負數逾時等同不等待。我看不到漏通知或死等。
- returncode 判斷:新版只看 `returncode is None`,不再呼叫 `poll()`。如果 leader 已死但還沒被 wait 收掉,新版會照砍整個群組,這比舊版 `_bt_kill_proc` 的 `poll()` 更能收到孫程序。已被 communicate 收掉的跳過,pid 被重用的理論視窗只剩 communicate 返回到 reap 檢查之間,小到可以忽略。

**2. 併發與資源**
- 鎖次序沒有巢狀:`lock`(工作清單、錯誤清單)與 `_cond` 從不同時持有,所以沒有死結路徑。
- 重試迴圈的上限:每次重試都要一次新的 KeyboardInterrupt。期限固定在第一次 reap,所以總等待最多 30 秒,另加砍的時間。KeyboardInterrupt 落在 `cond.wait` 時,鎖由 with 釋放,重叫 reap 沒問題。
- 探針實測期限不重算:修後第二次 reap 是 0.00 秒。把 `_deadline` 改回每次重算的版本跑,是 1.01 秒。所以 `t_bound_tests_reap_deadline_not_reset` 的 `second < 0.3` 在拿掉修補時會翻紅。
- 一個沒有可重現場景的觀察:`th.start()` 迴圈在 `try` 之外,主流程在那裡被中斷就不會 reap。窗口只有執行緒啟動握手那一小段,我造不出穩定重現,所以不列為 finding。

**3. 相鄰呼叫路徑**
- `_kill_run` 的逾時路徑:`os.killpg(proc.pid)` 對 `start_new_session=True` 的子程序等價於舊的 `getpgid(pid)`。不給 `started` 的呼叫者走 `_popen()` 直接開,行為不變。
- lint 指令逾時那處:舊版 except 只接 `(ProcessLookupError, OSError)`,Windows 沒有 killpg 時 AttributeError 會直接逃出去。新版退回 `proc.kill()`,這是行為改善,不是回歸。

**4. 測試品質**
- 我跑了 `-k t_bound_tests_parallel`(52 項)和新增的 `t_bound_tests_reap_deadline_not_reset`(3 項),都全綠。
- 延遲鍵 `t_g0` 確實套上:S5 的前置檢查「出錯前確實有慢測試開出程序」兩個情境都過。這個鍵只出現在展開後指令字串的方法名,不會誤配到 `t_slow*`。
- S7 和 S5、S7 補共用的探針開頭都會把 SIGINT 裝回預設處理,在背景分片裡不會被忽略 SIGINT 吞掉。`1 到 2 支` 的上限在忙碌機器上只有中斷延遲超過 1.5 秒才可能誤紅,這個機率不高。
- `second < 0.3` 和 `0.8 <= first < 2.5` 在極忙的機器上理論上可能誤紅。我沒有重現,所以不標。

## 三問
1. 原問題的行為證據:重叫 reap 不重算期限。兩次 `reap(wait=1.0)` 在修後是 1.00 秒加 0.00 秒,把修補拿掉是 1.01 秒加 1.01 秒。過期才開完的程序被收掉也已實測。
2. 修補處的正常、錯誤與相鄰呼叫路徑:正常路徑沒有動到。錯誤路徑,S5、S7 補、慢交回測試都綠。相鄰路徑是 `_kill_run` 逾時與 lint 逾時,行為等價或更寬容。
3. 新發現的同一案例:沒有新發現,所以沒有修前修後的對照。

我在 `/tmp/lumos-seat-work/code-合約測試閘收尾/正確性-sonnet/` 建的暫存已刪,沒有留下子程序。

總結:最高等級 clean
