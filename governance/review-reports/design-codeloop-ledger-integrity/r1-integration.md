severity: major

已核對凍結稿 SHA-256：`f66bd1107b9fa25523d4ee9517c9b038e9e9eb8260d22a88cedfd7f9f8cc2577`。審查僅使用派工材料，未讀其他席報告，未修改檔案。

## 同帳寫者與直接讀者

已讀，無 finding。`scripts/lumos` 的四個直接寫入入口，以及凍結稿列出的 rewrite、doctor、gov、迴圈關門、逃逸、lint-new 和 code-loop 讀取路徑，未發現漏列。缺口在寫入結果傳到呼叫端之後。

## Findings

### 1. `recall-miss` 寫入失敗仍回報記錄成功

severity: major  
blocking: 是  
引句:「best-effort 事件維持「寫帳失敗不改原閘判定」，但須回失敗並顯示既有警告。」  
file:line: `governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`；`scripts/lumos:35979`、`scripts/lumos:35982`

可重現輸入：在有 `docs/` 的暫存 Git repo，讓治理帳鎖持續被占用超過兩秒，再執行有效的 `code-loop recall-miss kt-flow --note "審查發現未觸發題"`。

預期：這個指令的本業就是記錄事件；未入帳時應回報記錄失敗，不能宣稱已記下。現況：`_gate_event_or_warn` 的失敗值被忽略，指令仍印「✅ 記下 recall-miss」並回 `0`；日後的次數統計沒有這筆。凍結稿把通用事件歸為 best-effort，卻未區分這種**只為記帳而存在**的入口。

### 2. 重凍路徑未被關門事件的驗收條款涵蓋

severity: major  
blocking: 是  
引句:「`_loop_gov_mark` 及其 `cmd_loop_rewrite` 等聲稱「入治理帳」的呼叫端必須依回傳值改訊息，不能吞錯後宣稱記帳成功。」  
file:line: `governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`、`:32`；`scripts/lumos:1019`、`scripts/lumos:1020`

可重現輸入：已有 golden 的迴圈執行 `loop replay --freeze --note ...`，同時讓治理帳鎖取得失敗。

預期：重凍結果可以按原判定處理，但輸出不得說理由「已寫治理帳」，並應指出 telemetry 失敗。現況：`_loop_gov_mark` 吞掉結果後，重凍仍印「重凍理由已寫治理帳」。S4 的可驗收輸入只寫「設計迴圈關門事件」；`replay-refreeze` 不是關門事件，故可在 S4 通過後留下這條假成功路徑。

### 3. `_append_governance_log` 的其他呼叫端仍會靜默丟失事件

severity: major  
blocking: 是  
引句:「best-effort 事件維持「寫帳失敗不改原閘判定」，但須回失敗並顯示既有警告。」  
file:line: `governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`、`:32`；`scripts/lumos:34554`、`scripts/lumos:29404`、`scripts/lumos:9923`

可重現輸入：讓共用 append 因鎖逾時回失敗，再觸發一次 bound-tests 跳過事件、delguard 結果事件或 escape-auto 失敗事件。

預期：原閘判定不變，但操作者能看到該筆治理事件未入帳。現況：這些包裝函式不檢查 `_append_governance_log` 的結果，部分還直接吞例外；若只依 S4 測通用 gate 事件及迴圈關門，這些事件仍會無聲消失。凍結稿需要把這些呼叫端的失敗訊號列入驗收。

總結：直接寫者與讀者清單完整；**blocking finding：3**，均為寫入結果沒有傳到實際宣稱或依賴入帳的呼叫端。