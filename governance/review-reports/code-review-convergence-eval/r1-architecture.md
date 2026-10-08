severity: minor

F1
severity: minor  
blocking: 否  
逐字引句:「responsibility: 負責審查帳衍生資料集、案例來源及試行證據比較與專屬測試，不負責產品審查閘、人裁或執行模型及產品指令」  
審材外查證file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:16`  
審材外查證file: `docs/lumos-toolchain-knowledge/MOC/index.md:75`

新增的 `Systems/review-convergence-eval` 已標成 `scope/evals`，但 MOC 的「評測 Evals」段仍只列三個舊 Systems，沒有新增節點。這違反鏡頭中「索引覆蓋尊重索引宣告範圍」的硬合約，會讓索引導覽漏掉新機制。補一行 `[[Systems/review-convergence-eval]]` 即可；不影響工具執行，故為 minor、非阻擋。

三問

1. 層與依賴方向：對齊。正式鏈為 `scripts/test_lumos.py` → 專屬 unittest → 同層 `governance/eval/review_convergence.py`；產品碼沒有反向依賴治理 eval。新 CLI 本身只依賴標準庫。證據：`scripts/test_lumos.py:75508`、`governance/eval/test_review_convergence.py:9`、`governance/eval/review_convergence.py:3`、`governance/eval/review_convergence.py:412`。這與 `retrieval_eval_multiword.py` 在 eval 層引用同層計分原語的方向一致：`governance/eval/retrieval_eval_multiword.py:30`。未見跨層直呼。

2. 命名與錯誤處理：對齊。函式採 snake_case、CLI 統一由 `main()` 回退出碼；I/O、UTF-8、JSON 錯誤集中轉成 `DataError` 並保留原因鏈，入口在 stderr 印穩定錯誤碼後回 2：`governance/eval/review_convergence.py:15`、`governance/eval/review_convergence.py:19`、`governance/eval/review_convergence.py:456`。對照檔也以輸入錯誤回 2：`governance/eval/retrieval_eval.py:807`、`governance/eval/retrieval_eval_multiword.py:252`。新工具比 `rule_conflict_scan.py:63` 的壞檔跳過策略更嚴格，但這符合 receipt/manifest 必須 fail-closed 的不同資料契約，不是命名或錯誤模型分岔。

3. 是否第二套同功能：否。`ablation_lumos_first.py` 是會派模型、寫結果與合併既有輸出的 runner：`governance/eval/ablation_lumos_first.py:135`、`governance/eval/ablation_lumos_first.py:265`；新工具只驗本機 manifest/trial/receipt 並成對彙整：`governance/eval/review_convergence.py:369`、`governance/eval/review_convergence.py:412`。兩者責任不同，沒有第二個模型執行器。新檔內 `read_ledger()` 與 `main()` 的 cohort 分支確實重複 JSONL 拆行：`governance/eval/review_convergence.py:77`、`governance/eval/review_convergence.py:425`；目前兩段語意相同，未找到具體分歧或失敗，因此不把純重複硬報成 finding。

硬合約逐條回覆

鏡頭只附了節點名稱，沒有自動附上任何硬合約原文；以下由本席唯讀執行 `lumos contracts` 補查。

- `Systems/測試假綠形態`
  1. bug 翻紅釘需證明現場分支成立：本次是新功能 TDD，不是 bug 還原釘；不適用，未破壞。

- `Systems/bound-tests-gate`
  1. 固定席合約測試必須真跑並 fail-closed：未修改 gate、解析或既有綁定；未破壞。

- `Systems/canary-audit`
  1. record/second 成功必須已落盤可讀回：未修改。
  2. second 僅為 telemetry、不得影響 status：未修改。

- `Systems/guard-kill`
  1. rc 優先序：未修改。
  2. JSON 模式 stdout 純度：未修改。

- `Systems/slim-get-一行安裝`
  1. 三支 PowerShell 必須 ASCII-only、無 BOM：未修改。
  2. PowerShell 參數不得使用 `$Args`：未修改。

- `Systems/slim-install-安裝器`
  1. sentinel 外內容 byte-equal：未修改。
  2. 重裝冪等：未修改。
  3. 完整版區塊需精確備份：未修改。
  4. 安裝時寫 manifest 與 bin SHA：未修改。
  5. CLAUDE.md 注入前的三層目標守衛：未修改。
  6. Windows shim 不得寫死 `python`：未修改。
  7. Windows 碰撞須同看 `lumos` 與 `lumos.cmd`：未修改。

- `Systems/slim-uninstall-一行卸載`
  1. 刪 bin 前須以 manifest／備援內容比對：未修改。
  2. 各清理步驟互不阻擋：未修改。
  3. skill 目錄移除前須備份：未修改。
  4. CLAUDE.md sentinel 移除／還原須 byte-equal：未修改。
  5. 孤兒 `lumos.cmd` 須獨立處理：未修改。
  6. manifest 清理須依 bin 實況且收尾失敗不誤升級：未修改。

- `Systems/lumos-cli-read`
  1. search 排除 superseded、不排 stale，且三路一致：未修改。

- `Systems/lumos-cli-lifecycle`
  1. re-inject 只改 sentinel 內文：未修改。

- `Systems/design-loop`
  1. 新設計案必須用 Markdown 計劃、條款逐條綁測試並具合格句式與回退節：符合。S1–S4 均綁測試，見 `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:36`；回退節見同檔 `:48`。

- `Systems/節點範圍與索引守衛`
  1. 三道檢查重用既有解析器：未修改檢查器。
  2. 索引覆蓋尊重索引宣告範圍：不符合，見 F1。
  3. 沒有總索引時必須明說跳過：MOC 存在；未修改。
  4. 節點過載只按合約數判斷：未修改。
  5. doctor 區段須位於 E3 後、H 前：未修改。
  6. 新閘名須登記：本次沒有新增 doctor 閘。
  7. 懸空狀態須共用 `_CLAUSE_HANG_STATES`：未修改。
  8. 門檻型別須單獨拒絕 bool：未修改。
  9. S5／S6／S7 均須落治理帳：未修改。

驗證限制：本席未在其他位置重跑。指定實驗目錄因唯讀沙箱無法建立，實際輸出為 `mkdir: /tmp/lumos-seat-work/code-review-convergence-eval/架構對齊-sol: Operation not permitted`。凍結審材內的既有紀錄為 4 passed / 0 failed，但尚無模型實輪成效。

最高等級: minor  
阻擋條數: 0