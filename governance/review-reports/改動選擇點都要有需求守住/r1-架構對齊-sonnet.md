severity: major

## 1. 分層與依賴方向:大致對齊,有一處新增的平行路徑
殺傷力那層做法對齊鄰居。`cmd_guard_kill` 本來就有 `recipes_override`,`cmd_situation_rule` 已經當呼叫端用它(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27902`、`:28179`、`:76076`)。計劃的 choice-kill 當第二個呼叫端,沒有跨層直呼。讀指定版本的檔和治理帳也沿用 `_kt_sit_read_many`(`:40114`)與 `_gov_rows_at`(`:65061`)。
引句:「一個選擇點只呼叫一次 `cmd_guard_kill`,把它全部守的測試當 `recipes_override` 一次丟進去」
不對齊的有兩處:選擇點掃描(a1),以及推送前那一道放的位置(a3)。

## 2. 命名與錯誤處理:對齊
- 指令名:`choice-kill` 是頂層連字號指令,跟 `situation-rule`(`:79347`)同型;`guard kill` 是 `guard` 底下的子指令(`:79236`)。
- 治理帳事件:`("choice-kill","choice-kill")` 這種 gate 與 kind 同名,照 `("situation-rule","situation-rule")`(`:20661`)的先例,並登記進 `_KNOWN_GATES`(`:17706`)與 `LOOP_NOT_CLOSE_EVENTS`(`:20645`)。
- rc 語意:0/1/2 取最大,同 `guard kill` 的 rc 優先序合約(`Systems/guard-kill` 的 INVARIANT)。
- 人裁同意:沿用 `_waive_origin_tty`(`:42153`)與 `origin`/`consent`。
引句:「人裁同意見〈用詞〉:照人裁那套 `_waive_origin_tty`:終端答 y 記 `origin: human`;沒有終端要 `--consent` 使用者原話」
小處不一致放在 a2。

## 3. 第二種做法:有兩處(a1 主要、a2 次要),其餘不算
- choice-kill 與 situation-rule、guard kill 功能重疊,但計劃用共用 `_situation_rule_kill` 加 `source` 參數,不另抽新函式(`:76076`、`:28179`)。我判這是第三個呼叫端,不是第二種做法。
- 〈選擇點表〉與〈情境決策表〉是兩張表,見 a1。
- 選擇點掃描與 kt-situation 掃描是兩套掃描,見 a2。
引句:「型錄照 `_kt_catalog_path()` 讀(工具鏈來源那份,不隨被推送版本變;測試用 `LUMOS_KT_CATALOG`),跟情境決策表同一支 `_kt_decision_table` 的檔、新增一份解析」

## 4. 落點:部分合理,見 a4
`Systems/規格閘` 放推送前那一道合理,它已有 `_spec_gate_push_check`(`:17387`)。`Systems/guard-kill` 放 `source` 參數與兩邊讀殺傷力帳本的口徑也合理。型錄〈選擇點表〉的家與選擇點掃描的家,計劃沒有寫。
引句:「Systems/規格閘、Systems/guard-kill 補 WHY 行(含兩邊讀殺傷力帳本的口徑)」

## a1 選擇點表與情境決策表是同一份型錄裡的兩張表、兩套解析
severity: major
blocking: 是
引句:「Kotlin 型錄新增〈選擇點表〉與它的解析」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39325`

⚠ 判斷依據:情境決策表每列已有「觸發字」與「另一種寫法(alt)」(`_kt_decision_table` 的欄位 `triggers`、`alt`、`switch`),語意就是「同組互換寫法」。選擇點表的 `換寫法` 種類(例如 `flatMapLatest`→`flatMapConcat`、`collectLatest`↔`collect`)是同一件事,卻另立一張表、另寫一套解析。專案現有做法是同一個型錄檔用 `check.py` 的 `dt_table` 依表頭取欄,一張表一支讀法。新增第二張表和第二個解析入口會讓壞法有兩個來源,而且 situation-rule 的壞法檢查(同一列的另一種寫法)跟 `--point` 路徑的檢查(表裡那個成員的壞法)是兩套判法。我覺得較自然的對齊方式有兩種:把選擇點表併成決策表的新種類列,或至少共用 `dt_table` 的欄位讀法。計劃沒有說明為什麼不這樣做。

## a2 選擇點掃描另寫「改到的行→位置」,沒標明和 kt-situation 掃描共用多少
severity: minor
blocking: 否
引句:「先用情境題剝註解與字串那支 `_strip_c_comments(..., blank_strings=True, kotlin=True, keep_length=True)` 得到等長文字」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40094`

⚠ 判斷依據:計劃只明確重用 `_strip_c_comments`(`:6869`)、`_kt_sit_read_many`(`:40114`)、情境題切段找函式邊界,這幾處對齊。但改動行怎麼取(`_kt_sit_hunks` `:40094`)、命中怎麼找(`_kt_sit_hits` `:40184`)、命中怎麼分組(`_kt_sit_group` `:40207`)這幾步,計劃另寫了一套敘述(同行多個成員、`#n` 定位、組號)。我不確定實作時會不會重用。我把它判成結構大致對、細節沒講清,所以是 minor。若實作另寫一份,就會升成 major。另外還有兩處小不一致:`--only`/`--point`/`--judge`/`--split` 的定位寫法 `<檔>:<行>#<n>` 是新格式,情境題用段身分(`--seg`,`:79348`)。

## a3 推送前那一道放在規格閘,情境題的推送檢查走另一條路
severity: minor
blocking: 否
引句:「在 `_spec_gate_push_check` 裡、`_spec_gate_push_scan` 之後另起一圈(不論有沒有候選計劃都跑,因為「沒碰到計劃」本身要擋)」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:17387`

⚠ 判斷依據:`kt-situation` 的推送檢查是讀 code-loop 的 `dispositions` 帳(`:17840`~`:17845`),生效日是 `_kt_sit_spec_since`(`:74032`)。`_spec_gate_push_check` 現在管的是預期值表與風險低留痕。這一道新增「不論有沒有候選計劃都跑」,語意和同函式其他圈(只看候選計劃)不同。生效日也多一個 `_CHOICE_SINCE`,等於同一個 Kotlin 情境家族有 `_kt_sit_spec_since` 和 `_CHOICE_SINCE` 兩個生效日常數,計劃沒有交代為什麼不沿用其中之一。結構上是掛在既有函式下的新圈,所以不判 major。

## a4 型錄〈選擇點表〉與選擇點掃描的家沒寫
severity: minor
blocking: 否
引句:「lands_in:Systems/規格閘、Systems/guard-kill」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39302`

⚠ 判斷依據:`Systems/guard-kill` 目前沒寫負責範圍(派工附註「沒寫負責範圍」)。要補的 `source` 參數與帳本口徑可以寫進它,但選擇點掃描、型錄新解析、`choice-points` 指令是 Kotlin 型錄與情境題那一側的程式,不是殺傷力那層。計劃的 lands_in 只列這兩篇,沒有列型錄與情境題那一側的家(`_kt_catalog_path` 一帶的節點)。建議確認選擇點掃描與表解析的程式檔屬於哪一篇的 about_code;屬於兩篇之外的,另開一篇或寫進型錄那篇的家,並先給 `Systems/guard-kill` 補負責範圍。

不對齊共 4 條,其中 major 1 條
