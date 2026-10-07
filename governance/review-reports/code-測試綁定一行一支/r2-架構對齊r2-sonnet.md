severity: minor

整體分層、呼叫方向和錯誤處理都跟鄰居一致,沒有第二種做法或跨層直呼。有三處形狀上的小不一致,沒有一處是「第二種做法」。

**1. 分層與依賴方向:對齊。**
- 新碼 `_ns_wd_binding_hit` 放在 `_ns_wd_line_hit` 旁邊,由 `_ns_wd_line_hit` 呼叫,結果走 `_ns_wording_hints`、`_ns_wording_collect`、`_ns_wording_emit` 這條既有路徑。
- 層級跟 `_ns_wd_count_hit` 相同,對照 `scripts/lumos:31469` 附近。
- 名稱切法呼叫 `slot_parse`、`_test_names_of`(`scripts/lumos:32266`)和 `_ns_tr_placeholder`(`scripts/lumos:32292`),跟 `_ns_test_ref_lines`(`scripts/lumos:32306`)同一套。
- 它對原文 `raw` 做 `slot_parse(raw)`,跟 `_ns_test_ref_lines` 內 `sp = slot_parse(raw)` 一致,沒有自己解析方括號。
- 層次與呼叫鏈跟鄰居一致,沒有跨層直呼。

**2. 命名與錯誤處理:大致對齊,有兩處小差異。**
- 命名沿用 `_ns_wd_*` 前綴,常數 `_NS_WD_BINDING_SHOW` 也沿用 `_NS_WD_*`。
- 例外處理沒有新增 try。綁定規則丟例外時,走 `_ns_wording_collect` 既有的 try(清空、記類別名、只印一句沒跑完)。
- 印提醒和記帳都用既有的 `_ns_wording_emit` 與 `_gate_event_or_warn`,只在 `word` 表多一個 `binding`,`rules` 多一個值。
- 差異一:`_ns_wd_line_hit` 的回傳形狀從「tuple 或 None」改成「list」。鄰居 `_ns_wd_count_hit`(`scripts/lumos:31469` 附近)和 `_ns_negation_hints`(`scripts/lumos:31061`)都是單筆或 None,只有這裡變成多筆。
- 差異二:`_ns_wording_emit` 的 `tag` 欄位,數量規則放「要貼的標記」,綁定規則放「整句說明字串」,同一欄兩種語意。

**3. 第二種做法:沒有,但有兩處值得註記。**
- 名稱截短:`"、".join(uniq[:5]) + "…等共 N 支"` 是行內手寫。檔內已有同類寫法,如 `scripts/lumos:7754`(`"、".join(outside[:5]) + (f" 等 {len(outside)} 支" ...)`)和 `scripts/lumos:16184`(`[:3]` 加 `等 N 支`)。這是跟既有慣用法同形狀、只是措辭多了「…」和「共」。
- 找 `[test` 位置:`re.search(r"\[\s*test\s*[:：]", raw[cut:], re.I)` 是自己再寫一支正規式。它跟 `slot_parse` 的欄位掃描是兩套邊界判法(`slot_parse` 會處理反引號與方括號層數),雖然提示位置只影響片段截取,風險低。
- `_ns_wd_line_hit` 改回清單:這是為了讓同一行可以同時出數量或位置、再加綁定。它仍在同一函式內、沿用 `_ns_wd_numbers` 等零件,不是新做法。
- 修補前的版本把 `masked` 餵給綁定規則,修補後改成只遮引號的 `ln`,這讓它跟 `_ns_test_ref_lines` 對齊,屬於往一致方向修。

### F1 同一欄位兩種語意
severity: minor
blocking: 否 — 結構沒錯,只是 `tag` 裡有的放標記、有的放整句說明,日後讀的人要靠 `rule` 分支才知道
引句:「→ {tag}:拆成一支一行,每行寫那支測試守的是哪一點」
佐證行 file: `scripts/lumos:31469`

### F2 截短措辭跟檔內既有寫法略不同
severity: minor
blocking: 否 — 跟 `等 N 支` 同形狀,只是多了「…」與「共」
引句:「…等共 {len(uniq)} 支」
佐證行 file: `scripts/lumos:7754`、`scripts/lumos:16184`

### F3 自己再寫一支找 `[test` 位置的正規式
severity: minor
blocking: 否 — 只用於提示片段的起點,不影響判定;但邊界判法跟 `slot_parse` 是兩套
引句:「at = re.search(r"\[\s*test\s*[:：]", raw[cut:], re.I)」
佐證行 file: `scripts/lumos:32306`

總結:不對齊共 3 條,其中 major 0 條
