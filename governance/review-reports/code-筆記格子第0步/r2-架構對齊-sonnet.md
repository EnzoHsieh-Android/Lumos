severity: minor

審查範圍：`/tmp/code0-r2.patch`。對照的是 `scripts/lumos` 的鄰居寫法，以及上一輪報告 `governance/review-reports/code-筆記格子第0步/r1-架構對齊-sonnet.md`。我只讀了檔，沒有改任何東西。

**問 1　分層與依賴方向**

結構對，沒有跨層直呼。

- `_rule_stale_keys` 放在 `_rule_date` / `_rule_legacy_shape_warnings` 同一帶，也就是 RULE 欄位與生命週期那一層（`scripts/lumos:3389`）。
- 它只呼叫 `_rule_date` 和常數 `_RULE_CONFIRM_STALE_DAYS`。呼叫它的是 `rule_lifecycle_warnings`（lint）和 doctor S16，方向是由上往下，沒有反過來。
- tag-hints 拆成 `_ns_tag_hints_collect`（收）、`_ns_tag_hints_collected`（eval 之後整理）、`_ns_tag_hints_emit`（印和記帳）三段。這跟否定現況句那組的分層一致：`_ns_negation_collected` 和 `_note_shape_negation_emit` 在 `scripts/lumos:26895`、`26906`。
- `cmd_note_shape` 的呼叫順序與否定組相同：先 collected，再 emit。
- 小差異（不單獨列為不對齊）：否定組的呼叫端寫 `if neg_items or neg_fail:` 才叫 emit。tag 組是無條件叫 emit，由 emit 內部在 `fail` 或 `items` 為空時提早 return。行為等價。

**問 2　命名與錯誤處理**

大致對齊，有兩條小差異。

**R2A1**
severity: minor
blocking: 否 — 治理帳的閘名位置只影響讀表的人，閘名本身有登記，漂移測試不會紅。
引句:「"check-s5", "check-s6", "check-s7", "check-s16", "ci", "code-loop", "design-loop"」
`check-s16` 被塞進「2026-09-10 節點範圍與索引守衛」那組的註解底下。那組註解是在講 s5 到 s7。同一張表裡，後來新增的閘都各自帶一行註解或獨立一行，例如 `check-s11`（`scripts/lumos:7260`）。S16 的記帳寫法本身跟 S7 一樣（`{"gate","kind":"warned","hard":False,"nodes":[n.stem]}`，`scripts/lumos:2497` 對 `2528`），這點對齊。
佐證行 file: `scripts/lumos:7249`

**R2A2**
severity: minor
blocking: 否 — 結構是同一套函式的組合，只是提醒字串的前綴跟 lint 路徑不同。
引句:「return slot_check("RULE", rest, commit_time=True) + rule_lifecycle_warnings(rest)」
`_ns_rule_hints` 重做了一次「新文法就跑 `slot_check`，再加生命週期檢查」的分派。`context_marker_warnings` 已經有同樣的分派，並且會幫每句加上 `筆記格子『RULE:』` 前綴。提交時印出來的格子提醒因此沒有這個前綴，和 lint 路徑不一致。這是同一組函式的第二個呼叫點，不算新做法，所以只列 minor。
佐證行 file: `scripts/lumos:2527`（`context_marker_warnings` 內的分派）；對照 `scripts/lumos:26571`

其他錯誤處理都跟鄰居一樣：

- 「`collect` 出錯就清空、記例外類別名、整次不再算」，這跟否定組同型。
- `emit` 的 `fail` 分支，印出來的字串形狀跟 `_note_shape_negation_emit` 一致。
- hinted 帳走 `_gate_event_or_warn`，跟否定組一致。
- SEE 新增的違規用 `out.append((規則名, 片段, 改法))` 三元組，跟 `_ns_check_line` 既有違規一致。

**問 3　第二種做法？上一輪三條有沒有真的消掉**

沒有引入第二種做法，上一輪三條都已消掉。

1. **`_slot_date`（第三套日期判斷）：已消掉。**
   - 函式整支刪除，連 `_SLOT_DATE_RE` 一起刪。
   - 改成 `DATE_RE.match(...)` 加 `_rule_date`，兩個都是既有的（`scripts/lumos:15731`、`3389`）。
   - 這個組合形狀等於既有的 `_note_date_ok`（`scripts/lumos:5790`），只是回傳 date 而不是 bool。我看不出需要另寫判法，所以不列為不對齊。
   - 可以接受的小事：`DATE_RE` 的 `$` 會放過結尾換行。但 `slot_parse` 的值已經過 strip，所以不構成問題。

2. **doctor S16 複製過期判斷且沒記治理帳：已消掉。**
   - 過期判斷抽成共用的 `_rule_stale_keys`，lint 與 S16 都呼叫它，門檻與判法只剩一份。
   - S16 補了 `gov_events.append`，`check-s16` 也登進 `_KNOWN_GATES`。

3. **tag-hints 分解方式跟否定組不同：已消掉。**
   - 現在是 collect、collected、emit 三段，簽章與否定組同型：`_ns_tag_hints_collected(tags, warns, fail)` 回傳 `(items, fail)`，`_ns_tag_hints_emit(root, items, fail)` 只負責印和記帳。
   - 一個小差異：tag 組的 `collected` 多做了排序，否定組的 `collected` 沒有。否定組是把排序放在格式化那一步，這屬於內部偏好，不列。

另外兩處改動也跟既有做法一致：

- `_ns_check_line` 新增的 SEE 分支用的是既有的 `_NS_POINTER_ONLY_RE`，跟 `slot_check` 的 SEE 判法同一個正規式。
- `context_marker_warnings` 加的空前綴跳過，跟 `_ns_check_line` 的 `skip = (not body)` 同義。

不對齊共 2 條，其中 major 0 條。
