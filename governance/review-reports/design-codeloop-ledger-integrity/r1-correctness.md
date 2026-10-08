severity: major

已核對凍結稿 SHA-256：`f66bd1107b9fa25523d4ee9517c9b038e9e9eb8260d22a88cedfd7f9f8cc2577`。本席只讀派工材料、程式與測試；以下重現輸入是依程式路徑判讀，未在唯讀席執行寫入實驗。

## Finding 1：最小紅燈驗不到 `pass/skip` 真 CLI 的失敗路徑

severity: major  
blocking: 是  
引句:「呼叫現行寫者寫新 SHA，斷言「回報失敗、讀者仍只看舊紀錄、帳尾未接新 JSON」」  
file:line：`governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:36`；程式對照 `scripts/lumos:36036`

可重現輸入：在帳尾放 `{"cut":`，分別呼叫真 `lumos code-loop pass`、`skip`、`dispositions`，再移除本機 marker，從治理帳執行 `check --json`。預期是三個寫入命令都回失敗、不新增 marker，乾淨讀者也讀不到新留痕。現況是 `pass/skip` 先寫 marker、治理帳寫入錯誤又被吞掉，最後仍回 0；凍結稿的「最小紅燈」只明指呼叫寫者函式，真 CLI 僅用於表態讀側，因此可在這個錯誤仍存在時通過所描述的最小驗收。

## Finding 2：治理帳已寫成、marker 寫不成時，`pass/skip` 的結果未定義

severity: major  
blocking: 是  
引句:「`pass/skip` 及 `dispositions` 的成功訊息與 marker 只能在治理帳成功寫入後出現」  
file:line：`governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`；程式對照 `scripts/lumos:35951`、`scripts/lumos:36038`

可重現輸入：讓 `docs/.governance-log.jsonl` 可寫、`governance/code-loop/` 不可寫，執行 `pass` 或 `skip`。預期須明定：帳上已有完整可讀事件時，CLI 應如何回報，且訊息不能稱 marker 已寫成。現況的 `dispositions` 對同一情形回 0 並警告；`pass/skip` 目前先寫 marker，失敗會在寫帳前中斷。凍結稿只規定先後，沒有規定改序後的回傳值與訊息，故「寫入成功 ↔ 可讀回」無法據此驗收。

## 其餘條款

S4、S5、S6 已讀無 finding。

總結：**2 條 blocking finding**。主要缺口在真 CLI 寫入驗收，以及帳已成功但本機 marker 失敗時的結果契約。