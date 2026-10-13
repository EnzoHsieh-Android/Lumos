severity: clean

這輪沒有 finding。我替極端輸入各跑了一遍,都站得住。

## 實跑環境
- 在 `/tmp` 乾淨 clone(`--shared`),checkout 54b01b1a。
- 用 `PYTHONDONTWRITEBYTECODE=1`(冷快取)跑 `python3.14 scripts/test_lumos.py -k bound_tests_parallel`:46 passed、0 failed。
- 中斷測試(S7)冷快取下開跑 2 支,在 1 到 2 的範圍內。
- 出錯測試(S5)兩種排序都約 2.0 到 2.1 秒結束,不留孤兒。
- 本機是 macOS、非 root、非 Windows。Linux CI、root 和慢機器沒實測,只做了讀碼推演。
- 臨時目錄已刪。

## 三問
**① 原問題的修復效果有何行為證據?**
- claim:出錯或中斷時,同批已開跑的子程序整個群組被收掉,連剛開出還沒登記的也收。
- input:S5 的兩種排序,出錯那支排第一,或排在慢測試後面同時開跑。
- expected:例外照丟,5 秒內結束,pid 檔裡的程序全部消失。
- case_source:binding 的 GE/repair。
- 修後:`t_bound_tests_parallel_error_stops_fast` 全綠。
- 修前:未判定。我沒有跑 3daa00a8 的對照;作者說修前會留孤兒,我沒有獨立證據。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常路徑:`t_bound_tests_parallel_matches_sequential` 綠,並行與循序結果逐項相同。
- 循序路徑:`workers==1`、`jobs<=1`、`jobs` 為空走 `seen.update(...)`,`started` 只累積 Popen,不收也不殺。
- 開不了程序:所有 job 的 root 都不存在時,workers 為 2 和 5 都在約 0.02 到 0.04 秒內丟出 `FileNotFoundError`,沒有卡住。
- 其他呼叫者:規格閘與修正關卡經 `_spec_gate_judge_items` 呼叫 `_run_bound_tests`,簽名沒變。
- `_kill_run` 不傳 `started` 時行為不變。這靠讀 hunk 判斷,我沒有跑 `-k guard_kill`。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- 沒有新發現。

## 設定值邊界(實跑 `_bound_tests_parallel`)
以下都當 1,而且都有提醒:
- NaN、`1e400`(即 inf)、`[2]`、`{"a":1}`、`99999999999999999999`、`True`、`bound_tests=false`。

其他值:
- `parallel=16` 回 16。
- `bound_tests=null` 和設定檔最上層是 `[]` 都靜默回 1。

我讀碼核對、沒有逐一實跑的值:1、0、負數、1.0、`"4"`、17。這幾個走 `type(v) is int and v == 1` 靜默、其餘出聲的邏輯。S2 測試實跑過 0、-2、`True`、2.5、1.0、`"4"`、17 和 bound_tests 非物件,都符合預期。

## 工作數與時間邊界(讀碼加實跑)
- 工作數 0 或 1 走循序。
- workers 大於 jobs 時取 `min(workers, len(jobs))`。
- 出錯在最後一支:主迴圈等到執行緒都結束後才檢查 `errs`,照樣丟出。
- 收尾 2 秒上限:只有某個工作被領走後卡超過 2 秒才登記程序時才會失效。這時由 `_BtProcs.append` 在登記當下收掉,但前提是主程序還活著。極端情況下主流程先結束、daemon 執行緒隨之消失,仍有孤兒的可能。這要超過 2 秒的停頓才發生,我給不出具體重現,所以不列 finding。
- Windows:`os.killpg` 和 `signal.SIGKILL` 都在 try 內,`AttributeError` 會被接住並退回 `proc.kill()`。這靠讀碼,沒在 Windows 實測。
- pgid 回收:`poll()` 為 None 才殺,競態窗口極小,而且 `ProcessLookupError` 會被接住。
- 測試小疑慮:S5 的 `_bt_alive_pids` 用 `os.kill(pid, 0)` 判活。在 PID 1 不回收殭屍的容器裡,它會把殭屍誤判為活著。本 repo 的 CI 是 `ubuntu-latest`、不是 container job,所以不構成失敗場景,不列。

## 圖譜鏡頭
- **guard-kill**(★INVARIANT★:rc 優先序、`--json` 純度):不破壞。diff 只給 `_kill_run` 多一個預設 None 的選用參數,回傳形狀不變,rc 與 JSON 輸出路徑沒動。
- **bound-tests-gate**(★INVARIANT★:紅、懸空、偽證據、`unproven` 擋下 rc1;沒指令、算不出、沒綁則不擋但寫帳):不破壞。
  - 判紅綠、逾時、跑過證據檢查和去重都照舊。
  - `plan` 保留原項目順序,`dangling`、`fake`、`bad-name` 仍記為 red,`no-cmd` 仍記為沒跑。
  - 唯一語意變動是 `secs` 改為牆上時間並多寫 `secs_kind: wall`,合約沒有規定 `secs` 的算法。
- **測試假綠形態**(還原翻紅釘要配前置斷言):新測試遵守。S5 檢查 `RAISED` 和 pid 存在,S7 先確認有測試開跑,S6 有前置斷言。
- **lumos-cli-read**、**lumos-cli-lifecycle**、**design-loop**:這份 diff 沒碰 search 的過濾、re-inject 的 sentinel,也沒碰處置閘。不破壞。
- **loop-convergence-recording**、**pitfalls-code-loop**(★RISK★)和其餘只列名的節點:這份 diff 沒碰它們的主題。唯一牽連是 `_bound_tests_log` 多寫 `secs_kind` 欄位,是新增欄位,且用 try/except 包住。

## 未驗範圍
- Linux、root 與慢機器沒實測。
- 修前版本的對照沒跑。
- Windows 沒實測。

總結:最高等級 clean
