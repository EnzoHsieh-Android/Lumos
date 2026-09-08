severity: major

### f1 整檔刪除跳過適用題
severity: major
blocking: 是
file: `scripts/lumos:16916`
引句:「if cur_file and _stack_changed_ok(cur_file):」
標準整檔刪除的 `+++ /dev/null` 不會設定 `cur_file`，所以刪除 `App.kt` 內 `viewModelScope.launch` 後 `stack_questions_applicable` 是空，pre-push/CI 不要求表態。已跑最小重現：以該 deletion diff 呼叫 `_pitfall_diff_collect`，斷言適用題非空翻紅為 `AssertionError: {}`。佐證：`scripts/lumos:16904`。

### f2 非 checkout ref 無法寫到被推版本
severity: major
blocking: 是
file: `scripts/lumos:21763`
引句:「return _cmd_codeloop_dispositions(repo_root, marker_branch or branch, head_sha, ts, disp_file)」
人在 `main` checkout 時推 `git push origin feat:feat`，check 以 `--at-sha feat` 驗證，但修復指令 `dispositions --branch feat` 仍把 `main` 的 `head_sha` 寫入；新 clone 又沒有本機 marker 時，ledger fallback 讀到的是 main 的帳，合法推送會被卡住。已跑最小重現，強制期待 `PUSHED_SHA`，實際翻紅：`AssertionError: expected PUSHED_SHA, got CHECKED_OUT_SHA`；CLI 沒有可指定 target SHA 的 dispositions 參數。佐證：`scripts/hooks/pre-push:208`。

### f3 advisory 沒有傳給合約測試器
severity: major
blocking: 是
file: `scripts/lumos:21511`
引句:「if bt["status"] == "red" and not bound_advisory:」
`--bound-tests-advisory` 只抑制最外層 rc=1，卻沒有以 `advisory=bound_advisory` 呼叫 `_bound_tests_check`；低風險且 `run_cmd` 無 `{method}` 的推送因此會跑整套測試（最長 600 秒）並寫成 `red-blocked`，最後仍被放行。已跑最小重現，將 helper 斷言 advisory 必須為真，實際翻紅：`AssertionError: advisory=False`。

### f4 重表態在統計中折成一筆
severity: minor
blocking: 否
file: `scripts/lumos:4733`
引句:「else d.get("ts", "") if (d.get("gate") == "code-loop" and d.get("kind") in ("dispositions", "recall-miss")) else ""),」
寫側把 `ts` 取自 HEAD 的 committer date，同一 SHA 上反覆 `dispositions` 的 ts 固定相同；讀側再把它當去重 token，兩筆會折成一筆，違反「同 sha 重表態各算各的」。已跑 probe：連續兩次 `_codeloop_git_ts(HEAD)` 翻紅為 `AssertionError: consecutive dispositions use same ts: 2026-09-09T01:49:45+08:00`。佐證：`scripts/lumos:21759`。

圖譜鏡頭：`Systems/pitfalls-code-loop`、`Systems/效能檢核目錄`、`Systems/棧別提問表態閘`、`Projects/棧別提問表態閘_計劃` 受 f1/f2 破壞：宣稱的「增刪行全算、適用題逐題表態、遠端分支座標」不成立；`Systems/bound-tests-gate` 與 `Projects/合約測試閘什麼時候跑_計劃` 受 f3 破壞，既有「紅即 blocked」合約與實際 `red-blocked` 帳、實際放行互相矛盾；`Systems/loop-convergence-recording` 與 `Systems/測試假綠形態` 受 f4 及其未覆蓋的真實寫側時間戳影響。`Issues/code-loop守衛main-direct盲區`、`Projects/prepush主幹範圍修法_計劃` 的 main-direct 範圍仍由 stdin push range 計算，未受影響；`Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`、`Systems/lumos-cli-lifecycle`、`Systems/lumos-cli-read`、`Systems/slim-get-一行安裝`、`Systems/slim-install-安裝器`、`Systems/slim-uninstall-一行卸載`、`Systems/授權與歸屬`、`Systems/anchor-integrity`、`Systems/check-r-guard`、`Systems/cochange-guard`、`Systems/lumos-deinit`、`Systems/core-invariant-baseline`、`Systems/judge-severity-gate`、`Systems/check-t-sentinel`、`Systems/lumos-refcheck`、`Systems/doctor-irreversible-hint`、`Projects/code側刪除傳播守衛_實作計畫`、`Projects/公開精簡版_實作計畫`、`Projects/test-layers軟提醒_實作計畫` 沒有對應行為路徑被本 diff 改寫，故其既有合約不受影響。

pitfalls manifest：唯一 claim 是誤報；`scripts/lumos:21218` 的檔案操作已使用 `with open(...)`，handle 不會漏關。

最嚴重 severity: major,blocking 條數 3
