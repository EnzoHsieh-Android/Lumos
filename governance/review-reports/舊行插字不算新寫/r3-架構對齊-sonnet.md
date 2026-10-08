severity: minor

審查範圍:`/tmp/舊行插字-r3.md` 對 rw 工作樹的 `scripts/lumos`(以下行號都指這支檔)。沒有 major,四條 minor 都不擋。四條裡有一條(R3A4)我用讀程式判斷,沒有實跑驗證,標 ⚠。

## 問一:分層與依賴方向

這版方向對得上。配對表只在 `_note_shape_eval` 前半(新增行那一路)建,依賴方向是 eval 往下呼叫 `_ns_check_line`、`_ns_revisit_violations`、`_ns_negation_hints`,沒有往上或跨層呼叫。放寬帳由 `cmd_note_shape` 寫,eval 只負責收集,doctor 不傳容器。這跟 `hints`、`tags`、`slots` 的現行做法一致:eval 收集,cmd 層印出並記帳(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw/scripts/lumos:28629`、`:28666-28683`)。

- 用 `_ns_check_line` 對 N、O 各算一次再比計數,復用既有函式,沒有另寫一套規則。
- `_ns_negation_hints` 多一個有預設值的參數,只是擴充既有簽名(`:27784`),不算新層。
- 小缺口:收集端的錯誤隔離沒寫清楚,見 R3A3。

## 問二:命名與錯誤處理(`relaxed` 是不是另起一套)

`relaxed` 不是另起一套。治理帳的 kind 本來就是開放字串,除了 blocked/warned/skipped-env/hinted/acked,還有 passed、skipped、skipped-flag(`:40616`)。`_gate_event_build` 沒有 kind 白名單,閘名才有 `_KNOWN_GATES`(`:7537`、`:1201`),`note-shape` 已在名單內。

- 不借 `hinted` 的理由站得住。格子度量的 `_SLOT_METRIC_KINDS` 是按 kind 計數(`:3759`),放進 `hinted` 底下用 `check` 區分,度量還是會被混進去。
- `extra.check: "insert-only"` 沿用現有 `check` 欄位的慣例(`:28680`)。
- ⚠ 我沒有逐一確認 `cmd_gov`(`:7888`)等讀帳端對沒見過的 kind 怎麼處理,實作時要核對。
- 錯誤處理有兩處不齊,見 R3A2 和 R3A3。

## 問三:第二種做法

「喚醒那一路不動、三種舊行各問各的」站得住:

- 喚醒那一路問「這行沒改、是程式檔變了」,基準是上線點版本加 `old_by`(`:28436-28445`)。
- 格子問「摘要欄位有沒有補」,用同前綴同核心一句的文字鍵比(`:28266-28290`)。
- 本案問「行改了但只多了字」,基準是起點版本。
- 三者問題不同,版本也不同,不是同一件事的兩套寫法。
- 刪掉的行只能從 diff 取到摘要區的(`_ns_deleted_summary_lines`,`:28240`),看不到區塊和 regen。所以本案改用整檔行數計數表,這個選擇合理。
- 讀起點版本失敗時,鄰居是整個格子檢查放行(`:28271-28282` 的 fail-open),本案是這篇不配對、照今天整行查。方向相反,但本案是放寬機制,失敗退回現行行為是對的,不算不一致。

不對的地方有兩處:

- 起點版本沒有跟格子共用一次讀取,見 R3A1。
- 被放寬的行還可能被喚醒那一路重報,見 R3A4。

---

**R3A1** 起點版本讀了兩次,而且上限與解碼口徑不同
severity: minor
blocking: 否 — 結構上沒跨層,只是同一批 blob 在同一次提交裡被讀兩遍,口徑也不同
引句:「起點版本用 `_nodehome_cat_blobs_capped` 批次讀、`utf-8-sig` 解碼」
- 本案在 eval 內用帶上限的批次讀,解碼失敗就不配對。
- 格子在 eval 之後另讀一次:`_ns_base_summary_lines` 用不帶上限的 `_nodehome_cat_blobs`,解碼用 `errors="replace"`。
- 兩邊讀的筆記集合也不同:本案是所有有新增行的筆記,格子只讀摘要有新寫行的筆記。
- eval 已經有把中間產物放進格子容器的先例(`slots["notes"], slots["old_by"] = notes, old_by`),起點版本可以同樣放進去。這樣只讀一次,格子那邊直接取用。
- 佐證:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw/scripts/lumos:28292`、`.../scripts/lumos:28277`、`.../scripts/lumos:28413`

**R3A2** 新門檻多數沒有名字,位元組上限也沒指定
severity: minor
blocking: 否 — 只是命名不一致,不影響行為
引句:「每次呼叫最多做 5000 次子序列判定(常數 `_NS_INSERT_MAX_CHECKS`)」
- 規格只替 5000 命名。
- 開頭 8 字、插入 500 字、N 的 2000 字、帳裡最多 50 條路徑行號,以及 `_nodehome_cat_blobs_capped` 的 `max_bytes` 都沒有名字。
- 鄰居都用 `_NS_` 前綴的常數(`_NS_SLOT_SHOW = 20`、`_NS_DOCTOR_SCAN_CAP = 200`)。
- 現成的 `_ROLE_MAX_BYTES` 是角色鏡頭專用,不該直接借用。
- 佐證:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw/scripts/lumos:27995`、`.../scripts/lumos:27109`、`.../scripts/lumos:23632`

**R3A3** 放寬容器缺少與 `hints`、`tags` 對等的收集與隔離
severity: minor
blocking: 否 — 規格有說傳法同 `hints`,只是少了「失敗不能害閘失敗」的收集端規矩
引句:「由 `_note_shape_eval` 多收一個容器參數(同 `hints` 的傳法,有預設值;不傳就不收)」
- 現行每個容器都有 collect、collected、emit 三段。
- collect 有 try:丟例外就清空 `items`、`error` 記例外類別名,這次不再算(`:27859`、`:27921`)。
- 本案的違規側(`_ns_check_line` 對 O 與 N 的比對、配對表)沒有任何隔離說明。
- 否定側的計數要在 `_ns_negation_hints` 內遞增。如果它在例外清空 `items` 之前遞增,放寬帳會記到實際沒減掉的條數。
- 建議規格補一句:放寬帳的計數一律在 try 外、確認成功後才寫入,並且配對或計數失敗不得改變違規判定。
- 佐證:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw/scripts/lumos:27859`、`.../scripts/lumos:27921`、`.../scripts/lumos:28666`

**R3A4** ⚠ 被放寬的行與喚醒那一路的交界沒說清楚
severity: minor
blocking: 否 — 屬行為界線沒寫明,不是結構問題,我只靠讀程式判斷
引句:「照舊用自己的整行集合」
- 喚醒那一路的去重只看 `viol` 裡已有的 `(路徑, 行號)`。
- 判舊行用的是上線點版本的整行集合與 `old_by`。
- 一行被配對放寬後不在 `viol` 裡,它改過的文字也不在上線點版本裡。
- 所以這行若含指向「這次才變成程式檔」的舊引用,喚醒那一路會把它當新行重報(新程式檔喚醒)。
- 這可能正是想要的行為,因為程式檔變了,舊行號確實會錯位。
- 但規格只用 S14 守「既有測試照綠」,沒寫「被放寬又碰到喚醒」該怎麼算。
- 建議補一個驗收條款,或在〈做法〉1 明寫這種情況照喚醒報。
- 佐證:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw/scripts/lumos:28422`、`.../scripts/lumos:28436`

不對齊共 4 條,其中 major 0 條
