severity: minor

## 1. 分層與依賴方向:大致對齊,推送那一道的落點有疑慮

選擇點掃描沒有另開底層。它沿用 `_kt_sit_path_ok`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:40169`)、`_kt_sit_hits`(40184)、`_kt_sit_read_many`(40114)、`_KT_SIT_BUDGET`(39986)。治理帳也沿用 `_gov_rows_at`(65061)。殺傷力呼叫走 `cmd_guard_kill` 加 `recipes_override`(27902),與 `_situation_rule_kill`(76076)同一條路。這些都和鄰居一致。

可疑的是推送前那一道的位置。它被放進 `_spec_gate_push_check`(17387),而這支函式現在整段沒有呼叫任何 `_kt_*` 函式。同樣吃 `--push-remote`/`--pushed-ref` 的鄰居,如 `room-guard`(52906、`_rg_precheck` 52839),是獨立指令,各有自己的掛鉤接線。計劃把「讀 Kotlin 檔、讀治理帳」的新圈塞進規格閘,又承認預期值表那圈仍讀工作目錄。這使同一支函式裡一圈讀 B 版、一圈讀工作目錄。它不算跨層直呼,因為規格閘本來就要碰計劃條款,但這是新的混搭,列為 a1。

引句:「在 `_spec_gate_push_check` 裡、`_spec_gate_push_scan` 之後另起一圈(沒有候選計劃也跑)」

## 2. 命名與錯誤處理:大致對齊,有兩處介面形狀跟鄰居不同

- **新治理帳事件**:gate 名 `choice-kill`,加進 `_KNOWN_GATES`(17706)和 `LOOP_NOT_CLOSE_EVENTS`(20645),寫法照 `situation-rule` 先例(20661)。對齊。
- **rc 語意**:全部有效處置為 0、有存活為 1、no_result 或中斷為 2,與 `cmd_guard_kill` docstring 的「全 killed=0;任一 survived=1;有 drifted/abort/error 而無 survived=2」一致。對齊。
- **`source` 參數**:現行 `cmd_guard_kill` 的 `source` 只在 docstring 描述,簽名裡沒有這個參數,行為由 `recipes_override` 隱含。計劃改成明確參數,方向合理。讀者端 `_backing_kill_rows`(77491)從「等於 situation-rule 就跳過」改成「非空就跳過」,也和現有跳過邏輯同形。
- **`choice-kill --judge` 與 `situation-rule --point`**:這兩處介面形狀跟鄰居不同,分別列為 a2、a3。
- **定位 `<檔>:<行>`**:現有情境題用段身分,選擇點用檔加行。因為一行只一個壞法,這樣可行。
- **錯誤訊息**:帶「擋下:」前綴與 rc 2,走法與鄰居一致。

引句:「rc 取最大:全部有效處置 → 0;有存活 → 1;有 no_result、不唯一或中斷 → 2。」

## 3. 第二種做法:沒有真正的第二套,但有三處重疊值得留意

- **掃描**:選擇點掃描與情境題掃描共用 `_kt_sit_*` 那組零件(hunks、path_ok、hits、read_many、budget)。它跟 `kt-situation` 的差別只在比對的表與「一行取一個壞法」的邏輯,不是第二套掃描。計劃也寫明不沿用 `_kt_sit_spec_since`。
- **殺傷力**:`choice-kill` 沒有另抽共用殺傷力函式,而是沿用 `cmd_guard_kill` 加 `recipes_override`,與 `Systems/guard-kill` 的既有否決一致。
- **兩張表**:選擇點表和情境決策表(`_kt_decision_table` 39325)各自成表,用「對應的情境決策表列號」欄互指。計劃寫了理由,表的讀法也由 `check.py` 的 `dt_table`(254)一般化。這是同一套讀表機制,不是第二種做法。
- **快取**:`kt-situation` 有家目錄快取(40287、`_kt_situation_segments` 40298)。計劃的選擇點掃描沒提快取。若效能不夠,可能長出第二套。計劃有預算與 RETIRE-IF 條件,我暫不列發現。

引句:「兩節都由 `configs/ast-grep/kotlin-android/check.py` 的表讀法讀(把 `dt_table` 一般化成依節名讀;情境決策表行為不變)」

## 4. 落點:合理,有一處小提醒

`lands_in` 列 `Systems/規格閘`、`Systems/guard-kill`、`Systems/kotlin規則包`,與現況對得上。
- `Systems/規格閘`:已有負責範圍,推送前那一道寫進去合理。
- `Systems/guard-kill`:`source` 參數、`_backing_kill_rows` 的口徑與帳本口徑寫在這裡合理。但它目前沒寫負責範圍,補寫時要一併補上。
- `Systems/kotlin規則包`:型錄兩節與 `check.py` 的讀法屬於它。

引句:「Kotlin 型錄新增〈選擇點表〉〈乾節點規則〉與 `check.py` 的讀法與檢查」

## a1 推送前那一道塞進規格閘,跟鄰居的獨立指令形狀不同,且同函式混讀 B 版與工作目錄
severity: minor
blocking: 否
引句:「預期值表那圈照舊讀工作目錄(既有天花板,不在這份改)」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:17387`

⚠ 判不準。若把這一道單獨成指令,像 `room-guard` 那樣自帶 `--push-remote`/`--pushed-ref`,結構較乾淨。但計劃要和預期值表缺簽合在同一次輸出,所以放在規格閘也有理由。

## a2 `choice-kill --judge` 是把不跑測試的另一種動作塞進同一個指令的旗標
severity: minor
blocking: 否
引句:「不跑測試、不套跑之前那串檢查;存活或 no_result 都能判」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:27464`

鄰居把「寫帳不跑」的動作拆成獨立子指令,例如 `guard kill-add`(27215)、`kill-rm`(27464)。`--judge` 與「跑」共用同一個指令名,卻有完全不同的前置檢查與 rc。

## a3 `situation-rule --point` 讓情境題指令多一條互斥的參數路徑
severity: minor
blocking: 否
引句:「`--seg`/`--row`/`--file`/`--old`/`--new` 改成選用,跟 `--point` 互斥(入口驗證)」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:76534`

現行簽名 `cmd_situation_rule(env, seg, row, plan, clause, test, file, old, new, …)` 把這幾個都當必填位置參數。改成互斥之後,指令名「situation」也不再貼切。人裁、寫回條款、跑殺傷力的流程在計劃裡是共用的,所以只算形狀不一致,不算第二種做法。

不對齊共 3 條,其中 major 0 條
