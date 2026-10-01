severity: major

審查對象是 `/tmp/code0-r1.patch`,對照 repo 是 scratchpad 的 `rw`(HEAD bddb664c)。下面的 file:line 都指 `rw` 裡 `scripts/lumos` 的行號。

## 三問

**1. 分層與依賴方向:對齊**
- RULE 欄位的新舊兩種寫法放在同一個入口,`parse_rule_fields` 看 `slot_is_new` 分流(`scripts/lumos:3365` 一帶)。這是計劃明講的遷移做法,不算第二種。
- `_slot_retire_err` 沒有另寫條件文法,直接呼叫 `_probe_value_err`(`scripts/lumos:26668`)。已知閘的清單用 `_KNOWN_GATES`(`scripts/lumos:6927`),只放連結的判斷用 `_NS_POINTER_ONLY_RE`(`scripts/lumos:25061`)。這三處都是借用鄰居。
- `_plan_system_links` 只加了 `SEE:`,沒另開函式。
- 新的提交前提醒組沿用否定現況句那組的分層:`cmd_note_shape` 呼叫 prepare,再傳進 `_note_shape_eval`,逐篇 collect,最後 emit。沒有跨層直呼。
- doctor 的 S16 段用 `warn_soft`,放在 S7 之後、S8 之前,位置紀律照 S8 的註解。
- 測試用的是既有的 `_load_lumos_inproc`、`mkvault/write/run`、`_ns_repo/_ns_note/_neg_inproc`,沒有自刻夾具。

**2. 命名與錯誤處理:大致對齊,有兩處小偏差**
- 命名 `_note_shape_tag_hints_parse`、`_ns_tag_hints_*` 與 `_note_shape_negation_parse`、`_ns_negation_*` 一致(`scripts/lumos:26455-26500`、`26518-26600`)。
- 例外只印類別名、不改回傳碼、記 `hinted` 帳,與 `_note_shape_negation_emit`(`scripts/lumos:26887`)一致。
- 偏差一是 S16 沒有記治理帳(見 A2)。
- 偏差二是 tag-hints 的 emit 把「設定提醒」與「失敗」的處理塞進同一支函式(見 A3)。

**3. 第二種做法:有一處**
- `_slot_date` 是日期驗證的又一套寫法(見 A1)。
- 新舊兩套 RULE 欄位解析並存是計劃核定的遷移,不另計。

## 不對齊清單

**A1 `_slot_date` 是日期驗證的第三套寫法**
severity: major
blocking: 是 — 同一支檔的同一類資料(`YYYY-MM-DD` 欄位)有三套判法,接手的人要猜該用哪套。`_note_date_problem` 的 docstring 還明寫「同一種資料只准一套判法」
引句:「def _slot_date(v):」
佐證 file: `scripts/lumos:3532`(新寫的 `_slot_date`)
- 對照一:`_rule_date`(`scripts/lumos:3389`)就在同一區塊正上方,回傳 date 或 None,契約相同。
- 對照二:`_note_date_ok` 搭配 DATE_RE(`scripts/lumos:5787`)。
- `_slot_date` 只多了「必須是 `\d{4}-\d{2}-\d{2}`」的限制。這個限制可以用 `_rule_date` 加 DATE_RE 的 fullmatch 組合出來,不必另開函式。
- 同一個 diff 裡「今天」也有兩種取法:`_slot_check_values` 用 `_dt.datetime.now(_dt.timezone.utc).astimezone().date()`(`scripts/lumos:3624`),S16 也是(`scripts/lumos:2511`);同一個 diff 裡的 `rule_lifecycle_warnings` 仍是 `_dt.date.today()`(`scripts/lumos:3436`)。
- 兩種寫法在本機日期上結果相同,所以這點只算順帶,不單獨升級。

**A2 doctor S16 把 RULE 的過期與過久判斷又寫一次,也沒記治理帳**
severity: minor
blocking: 否 — 結構對、也有共用 `_RULE_CONFIRM_STALE_DAYS`,但邏輯複製,日後改門檻或條件容易漂移
引句:「_u, _c = _rule_date(_f.get("until") or ""), _rule_date(_f.get("confirmed") or "")」
佐證 file: `scripts/lumos:2523`
- 對照一:`rule_lifecycle_warnings` 已有同樣的 until 過期與 confirmed 逾 180 天判斷(`scripts/lumos:3441-3450`)。
- 對照二:鄰居 S7、S8、S9、S10 逐條 `gov_events.append({"gate": "check-sN", "kind": "warned", ...})`(`scripts/lumos:2496`,以及 S8 段內 `check-s8`、`check-s9`、`check-s10`)。S16 沒有,所以 doctor 看到的警告不進治理帳。
- S16 多了「沒寫 `[confirmed:]`」這一類,屬於它自己的需求,不算問題。

**A3 tag-hints 的 emit 把鄰居拆開的職責合在一起**
severity: minor
blocking: 否 — 行為與鄰居一致,只是分解方式不同,不構成第二套機制
引句:「def _ns_tag_hints_emit(root, tags, warns, fail):」
佐證 file: `scripts/lumos:26569`
- 對照:否定現況句那組拆成 prepare(`scripts/lumos:26867`)、collected(`scripts/lumos:26876`)、emit(`scripts/lumos:26887`)三支。
- tag-hints 沒有 `_collected`,設定提醒的列印(`seen` 閘門)和失敗訊息都塞進 emit。
- 另外,否定現況句的 collect 只看可見行(`_ns_negation_hints` 內的 `i not in vis_nos` 判斷),`_ns_tag_hints_collect` 沒有這道檢查。後者只看 summary 區,圍欄外一般不成問題。這點屬於行為差異,不是做法對不對的問題。

不對齊共 3 條,其中 major 1 條。

沒有要交編排者裁決的 ⚠ 項。
