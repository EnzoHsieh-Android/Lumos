severity: clean

這輪的修正差異沒有跟既有做法分叉的地方。r2 報告的兩條 minor 都已對齊,我逐項對過 repo 現況。

**①分層與依賴方向**
- 修正只動三處:`_KNOWN_GATES` 的排法、doctor S16 的記帳、`_ns_rule_hints` 的字樣前綴,另加測試。沒有新的跨層呼叫,也沒有新的函式。
- S16 仍呼叫 `_rule_stale_keys`、`parse_rule_fields`、`slot_parse` 這些既有函式,依賴方向跟 r2 時相同。
- `_ns_rule_hints` 仍是 `slot_check` 加 `rule_lifecycle_warnings` 的組合,與 `context_marker_warnings` 在 `scripts/lumos:3662-3667` 的分派相同。
- 對照:`scripts/lumos:2531`、`scripts/lumos:26585`。

**②命名與錯誤處理(含治理帳寫法)**
- **r2 第一條(`check-s16` 在已知閘名單的位置)已對齊。** `check-s16` 現在是獨立一組,上方帶一行日期註解「2026-10-01 有效 RULE 的到期與確認…」。這與同一張表裡其他後來新增的閘一致,例如 `scripts/lumos:7252-7254` 的 s5 到 s7 一組,以及 `check-s8` 到 `check-s10` 一組。它不再擠在 s5 到 s7 那組註解底下。
- **治理帳寫法對齊。** S16 現在是一篇筆記只記一筆 `{"gate","kind":"warned","hard":False,"nodes":[n.stem]}`,用 `_nodes16` 去重。S7 是每篇一筆(`scripts/lumos:2497`),S8 的 `for _f in …` 迴圈裡一檔一筆(`scripts/lumos:2562`),形狀與粒度跟它們一致。
- **r2 第二條(提交時格子提醒的字樣前綴)已對齊。** 提交時現在加上 `筆記格子『RULE:』` 前綴,與 lint 路徑的 `scripts/lumos:3665` 同字樣。
- lint 路徑尾端多一段 `:{rest[:40]}`,提交時沒有。我判這是因為提交時的輸出已帶 `路徑:行號`(`_ns_tag_hints_emit` 印 `{p}:{n}  {w}`),屬於各自輸出格式的差別,不列為不對齊。
- `rule_lifecycle_warnings` 兩條路徑都沒加前綴,彼此一致。
- SEE 判準改成 `"[[" not in body or not _NS_POINTER_ONLY_RE.match(body)`,違規仍是原本的三元組 `(類別, 摘錄, 修法)`,沒有換格式。

**③第二種做法**
- 沒有。新增的測試用 `_load_lumos_inproc` 與 `Path(GRAPHCTL).read_text`,這兩種寫法在該測試檔裡都有既有用法。
- 提交時和 lint 不再各用一套字樣,分歧已收掉。

不對齊共 0 條,其中 major 0 條。

補充:指定的 r2 報告路徑在 `/Users/enzo/harness/lumos-toolchain` 下不存在,我改讀 rw repo 內的 `governance/review-reports/code-筆記格子第0步/r2-架構對齊-sonnet.md`。
