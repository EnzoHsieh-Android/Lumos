severity: major

## Finding 1：交易重驗拒絕 claim 後，父子程序間缺少明確的結果協定

severity: major

blocking: 是

逐字引句:「父程序只用帳的剩餘量作提前提醒及本批 max-attempts；探針新增 --max-per-window 接收父派工器原始窗口上限；--max-attempts 仍只限本批。」

問題：交易重驗拒絕 claim 後，父子程序間缺少明確的結果協定。

佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:32`  
佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:36`  
佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:39`  
佐證 file: `scripts/scenario_probe.py:1040`  
佐證 file: `scripts/scenario_probe.py:1061`  
佐證 file: `scripts/scenario_probe.py:1115`  
佐證 file: `governance/eval/ablation_lumos_first.py:298`  
佐證 file: `governance/eval/ablation_lumos_first.py:308`

具體輸入與推導：

1. 同一帳上限為 5，已有 4 筆；兩個 `run_job(..., n=1, max_per_window=5)` 同時讀取剩餘量。
2. 兩個父程序都可能讀到剩餘 1，因而各啟動一個探針；依設計，只有其中一個交易能成功 claim。
3. spec 只規定失敗者不插入、不得啟動模型及不得等待 300 秒，卻未規定它是否：
   - 產生一筆結果列；
   - 使用 `limit_hit`、新欄位或專用例外；
   - 回傳 rc 0、1 或 3；
   - 算入父程序要求的 `len(rows) == n`。
4. 沿用現有分支會得到互斥錯誤：
   - 當作 `ProbeAttemptBudgetExceeded`／fatal，會讓父程序以 rc3 停止整批；
   - 當作 `limit_hit`，會進入 300 秒等待，違反 S4；
   - 不產生結果列，會因 `len(rows) != n` 被父程序判成全域探針失效。

需在凍結 spec 補上「本機帳達限」的子程序結果欄位、是否占結果列、退出碼及父程序處置；否則 S1 的競爭案例無法得到唯一可驗收行為。

實際覆蓋：完整閱讀 52 行凍結 snapshot；精讀 `scenario_probe.py` 的 `run_one_codex`、`run_one`、`main`，以及 `ablation_lumos_first.py` 的 `run_job`，合計約 680 行程式上下文。未讀其他報告、作者 intake 或非指定函式，未寫檔、未呼叫模型或外部服務。

未驗資格：這不是現況實作審；未檢查尚未存在的 SQLite helper、schema、CLI 新 API 或其他呼叫端，也不判定供應商帳務與跨機額度。