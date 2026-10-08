severity: major

F1 父 runner 異常死亡會先釋放鎖，但已啟動的探針子程序繼續執行；第二個 CLI 隨即取得鎖並啟動第二支探針，造成重複配額消耗與並行污染。

severity: major  
blocking: 是  
引句:「r = subprocess.run(cmd, cwd=str(ROOT), stdout=lf, stderr=subprocess.STDOUT, text=True)」  
file: `governance/eval/ablation_lumos_first.py:205`  
最小翻紅重現：用假探針寫出 PID 後睡眠 60 秒；啟動第一個 `main`，探針開始後對父 runner 送 `SIGKILL`，再以相同 `--out-dir` 啟動第二個 `main`。斷言「第一探針仍活著時不得啟動第二探針」翻紅；實測為 `orphan_still_alive_during_second=true`、`second_probe_started=true`、第二批 `rc=0`。鎖 fd 沒傳給子程序，父程序一死便失去互斥所有權。

F2 目錄鎖只綁定當時的 inode；輸出目錄被改名並在原路徑重建後，第二個 CLI 可鎖住新 inode，舊批次之後仍按路徑寫入新目錄並覆蓋新摘要。

severity: major  
blocking: 是  
引句:「lock_fd = os.open(out_dir, os.O_RDONLY | os.O_DIRECTORY)」  
file: `governance/eval/ablation_lumos_first.py:425`  
最小翻紅重現：第一批取得鎖後暫停，將 `out` 改名為 `out-old` 並重建 `out`，第二批以同一路徑純合併題 `second`，再恢復第一批題 `first`。斷言第二批應回 3 翻紅；實測第二批 `rc=0`，摘要先是 `["second"]`，第一批恢復後變成 `["first"]`。這也會讓同目錄暫存檔的建立與替換失去原鎖保護。

F3 `max-per-window` 只判斷目前是否已滿，沒有把單一工作的 `n` 限縮到剩餘額度；使用者可用一個串行工作任意越過窗口上限。

severity: major  
blocking: 是  
引句:「五小時窗口滿就留待下次補缺；本批只准單路派工，避免並行 TOCTOU 多開模型。」  
file: `governance/eval/ablation_lumos_first.py:188`  
佐證 file: `scripts/scenario_probe.py:1009`  
最小翻紅重現：令 `runs_in_window()` 回 0，呼叫 `run_job(..., n=100, max_per_window=1)`，攔截交給探針的命令並斷言 `--runs <= 1`。實測命令帶 `--runs 100`；真探針會按 `range(1, a.runs + 1)` 執行全部 100 場。單路消除了 worker 間 TOCTOU，沒有實現 CLI 所宣告的場次上限。

表態 `py-eventloop na`：已讀,無 finding。  
表態 `py-parallel satisfied`：F1 證明只驗串行呼叫順序不足以涵蓋父程序死亡後的在途子程序。

固定席 `Systems/codex-harness`：F1。  
固定席 `Systems/測試假綠形態`：已讀,無 finding；既有測試確實走到鎖與原子寫入路徑，但未覆蓋上述三個反例。  
固定席 `Systems/lumos-cli-read`：已讀,無 finding。  
固定席 `Systems/canary-audit`：已讀,無 finding。  
固定席 `Systems/design-loop`：已讀,無 finding。  
固定席 `Systems/bound-tests-gate`：已讀,無 finding。  
固定席 `Systems/guard-kill`：已讀,無 finding。  
固定席 `Systems/lumos-cli-lifecycle`：已讀,無 finding。  
`Projects/探針隔離與清理收斂_計劃` S8：已讀,無 finding。  
`Projects/探針隔離與清理收斂_計劃` S9：F1。  
`Projects/探針隔離與清理收斂_計劃` S10：F1、F2。  
既有 `probe_boundary_postreview` 子集：18 passed、0 failed；未覆蓋 F1–F3。

總結：最嚴重 severity: major；blocking: 3
