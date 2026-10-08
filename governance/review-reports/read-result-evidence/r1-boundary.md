severity: blocker  
blocking: 是  
已讀審材完整路徑：`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/read-result-evidence/r1-snapshot.md`

## 路徑邊界

severity: blocker  
blocking: 是  
引句:「不影響其他題、不改結果passed布林形狀、不碰真repo/全域設定」  
finding: `make_sandbox` 會清除 `GIT_DIR`／`GIT_WORK_TREE`，但 Claude、Codex runner 重新繼承原始環境，逐場 `git checkout`／`git clean` 也未傳乾淨環境。呼叫端若帶著這些變數，被測模型與清理命令可越過沙盒，落到真 repo，重開指定 Issue 的 P0 事故。file: `scripts/scenario_probe.py:440`、file: `scripts/scenario_probe.py:513`、file: `scripts/scenario_probe.py:524`、file: `scripts/scenario_probe.py:724`、file: `docs/lumos-toolchain-knowledge/Issues/探針以工作樹為來源會改到本體.md:66`  
最小重現: 以 stub 取代 `subprocess.run`，設定 `GIT_DIR=/outside/repo/.git`、`GIT_WORK_TREE=/outside/repo`，分別呼叫 `run_one`、`run_one_codex`；兩者傳入子程序的環境仍保留這兩個值。已重現，未啟動模型、未執行 Git 寫入。

## 注入／清理生命週期

severity: major  
blocking: 是  
引句:「還原前重驗路徑安全，失敗列儀器例外並停止整批，避免後續污染」  
finding: 「還原失敗停止整批」沒有對應的例外通道或驗收斷言。現有 per-attempt 外層捕捉所有普通 `Exception`，改寫成儀器例外後繼續；source-probe 的 `finally` 若拋 `PermissionError`／`RuntimeError`，後續嘗試仍可能在無法證明已還原的副本上執行。S4 也未斷言還原失敗後不得呼叫下一個 runner。file: `scripts/scenario_probe.py:701`、file: `scripts/scenario_probe.py:705`、file: `governance/review-reports/read-result-evidence/r1-snapshot.md:23`、file: `governance/review-reports/read-result-evidence/r1-snapshot.md:34`  
最小重現: 未能重現（`source_probe` 尚未實作）。翻紅測試應安排兩次嘗試，讓第一次 finally 還原拋 `PermissionError`，斷言第二次 runner 呼叫數為 0、main 回儀器致命退出碼，且不產生可評分摘要。

## 工具結果關聯與判分

已讀,無 finding

## 重試與標記遮罩

已讀,無 finding

總結: 最嚴重 severity=blocker，blocking=2
