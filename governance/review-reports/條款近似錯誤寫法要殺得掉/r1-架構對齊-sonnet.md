severity: minor

## 1. 分層與依賴方向:對齊
新邏輯全在單檔 `scripts/lumos`,跟鄰居同一層。依賴方向也一樣:
- 條款標記走 `INV_TAG_RE` 與 `_clause_body_of`(`scripts/lumos:6051`、`scripts/lumos:13902`)。
- 殺傷力走 `cmd_guard_kill(..., recipes_override=)`(`scripts/lumos:27769`)。
- 推送前那一道接在 `_spec_gate_push_check`(`scripts/lumos:17387`)。
- 讀帳走 `_gov_vc_gate_events`,條款雜湊走 `_clause_sha`(`scripts/lumos:13913`)。

沒有看到跨層直呼。人裁 `_situation_rule_kill` 也是從指令層呼叫 `cmd_guard_kill`(`scripts/lumos:75890`),計劃的做法一樣。

引句:「換寫法、跑測試的零件直接用人裁已經在用的 `cmd_guard_kill` 帶 `recipes_override`,不另寫一套。」

## 2. 命名與錯誤處理:大致對齊,有兩處不一致
- 對齊的部分:
  - 事件的 gate 與 kind 取同一個字串。人裁是 `_SITUATION_RULE_SOURCE`(`scripts/lumos:75475`),計劃的 `clause-kill` 照做。
  - 生效日常數加環境變數覆寫,對應 `_expected_since`(`scripts/lumos:14524`)。
  - 計劃日期取 `_plan_effective_day`(`scripts/lumos:14511`)。
  - 事件欄位對應 `_situation_rule_event_parts`(`scripts/lumos:75913`)。
- 不對齊 a1:弱證據的 rc 語意。人裁對「survived 與弱證據」都是 rc 2(`scripts/lumos:75890` 一帶的 `_situation_rule_kill`,只認沒有弱證據的 killed)。計劃把「沒讓測試紅或判弱證據」都併成 rc 1,弱證據不分開。這跟 guard-kill 合約「弱證據不放行執行錯誤」的拆法也不同。
- 不對齊 a2:生效日少了測試總開關。`_expected_since` 的註解寫明測試總開關預設把環境變數設成 9999,讓既有測試停在生效前。計劃只寫了 `LUMOS_NEAR_SINCE` 供覆寫,沒說測試總開關預設,舊測試可能因此被新規則波及。

引句:「判定不是殺得掉時 rc 1,印「補測試讓它紅,或改寫這條近似錯誤寫法」。」

## 3. 第二種做法:大致沒有,但需明講重用
`clause-kill` 跟 `situation-rule` 的前半段幾乎同形:驗參數、驗配方、工作目錄要乾淨、平台要有 `run_cmd`、跑殺傷力、記治理帳。差別在 `situation-rule` 還要人點頭並寫回計劃,`clause-kill` 不寫計劃。它跟 `guard kill-add --try` 的用途不同:後者把配方寫進筆記,前者只做一次性驗證,所以不必併成同一個指令。

但計劃只說重用 `cmd_guard_kill`。下面這些人裁已有的零件它沒提重用:
- `_situation_rule_kill`,含 Ctrl-C 與終止訊號處理 `_situation_rule_signals`(`scripts/lumos:75880`)
- `_dirty_non_bookkeeping`
- `_situation_rule_platform`
- `_situation_rule_recipe_problem`

照字面實作很容易再寫一套平行的流程,等於第二種做法。我判不準計劃的實際意圖,所以這條標 ⚠,按 minor 列。

另外,「讀殺傷力帳本時跳過人裁那幾筆」目前是各處自己比 `== _SITUATION_RULE_SOURCE`(`scripts/lumos:77028`,另有 `scripts/lumos:28041` 一帶寫入端)。計劃叫實作時「grep 列全再各加一個 clause-kill」,會讓判斷散在多處。比較一致的做法是抽成一個來源集合再比對。

引句:「讀殺傷力帳本、目前只跳過人裁那幾筆的讀者(`_backing_kill_rows`、doctor P2 等,實作時 grep `_SITUATION_RULE_SOURCE` 列全)一併跳過 `clause-kill`。」

## 4. 落點:對齊
`Systems/規格閘` 管條款標記與推送前那道,`Systems/guard-kill` 管殺傷力與 `recipes_override`。兩篇都已存在,補 WHY 行是合理的。`situation-rule` 沒有自己的 Systems 節點,它的說明也是散在這兩篇,所以不需要為 `clause-kill` 另開。

唯一的小事是 `Systems/guard-kill` 沒寫負責範圍,補 WHY 時順手補,但這不算不對齊。

引句:「Systems/規格閘、Systems/guard-kill 補 WHY 行;lumos-design-loop 手冊寫條款那段補 `[near:]` 寫法;lumos-project-notes 指令索引補 `clause-kill`。」

## a1 弱證據的 rc 語意與人裁、guard-kill 不一致
severity: minor
blocking: 否
引句:「判定不是殺得掉時 rc 1,印「補測試讓它紅,或改寫這條近似錯誤寫法」。」
file: `scripts/lumos:75890`

## a2 生效日沒提測試總開關預設
severity: minor
blocking: 否
引句:「環境變數 `LUMOS_NEAR_SINCE` 供測試覆寫(同 `_expected_since` 的寫法)」
file: `scripts/lumos:14524`

## a3 clause-kill 沒講明重用人裁的驗證與中斷處理零件(⚠)
severity: minor
blocking: 否
引句:「補 import 走人裁同一條 `also` 路徑。」
file: `scripts/lumos:75880`

## a4 跳過來源的判斷靠 grep 逐點加,沒收成一個集合
severity: minor
blocking: 否
引句:「實作時 grep `_SITUATION_RULE_SOURCE` 列全」
file: `scripts/lumos:77028`

不對齊共 4 條,其中 major 0 條
