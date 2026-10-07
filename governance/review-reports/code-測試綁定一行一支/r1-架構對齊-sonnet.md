severity: minor

**1. 分層與依賴方向:對齊**
- 新函式 `_ns_wd_binding_hit` 放在 `scripts/lumos:31498`,緊接 `_ns_wd_line_hit`(`scripts/lumos:31478`)。呼叫方向是 `_ns_wd_line_hit`(`:31495`)到 `_ns_wd_binding_hit`,再往下呼叫 `slot_parse`(`:4268`)、`_test_names_of`(`:32256`)、`_ns_tr_placeholder`(`:32282`)。
- 這跟鄰居 `_ns_wd_count_hit`(`:31469` 附近,由 `_ns_wd_line_hit` 呼叫)的方向一致,也沒有跨層直呼。
- 輸出走原有的 `_ns_wording_hints`(`:31515` 以下)到 `_ns_wording_emit`。記帳還是同一支 `_gate_event_or_warn`,`rules` 只多一個值。
- 引號遮罩沿用 `_ns_wd_line_hit` 開頭的 `_ns_neg_quote_spans` 與 `_inline_blank`,沒有另寫。

**2. 命名與錯誤處理:對齊**
- 函式名 `_ns_wd_*`、規則字串 `"binding"`、`word` 對照表多一項「綁定」,都照 count 與 position 的寫法。
- 沒有新的例外處理路徑。出錯仍由 `_ns_wording_collect`(`scripts/lumos:31541` 附近)的 try/except 與 `_ns_wording_emit` 的收尾 except 接住,只印一句,不改判定。
- 唯一的小偏差是第三個元素型別變了。原本鄰居的 `tag` 是 `str` 或 `None`,現在 binding 規則塞的是名稱清單。`_ns_wording_emit` 因此要靠 `rule == "binding"` 再用 `len(tag)` 分流,巢狀三元式也比原本難讀。結構還是對的,所以只列為不對齊。

**3. 第二種做法:大致對齊,有一處切法偏差**
- 名稱切法用的是 `slot_parse` 加 `_test_names_of`,跟 `_ns_test_ref_lines`(`scripts/lumos:32312`、`:32317`)和 S20(`:32381`)同一套。過濾佔位名稱用 `_ns_tr_placeholder`,沒有自創工具函式。
- 差別在餵進去的文字。`_ns_test_ref_lines` 餵的是原文(`rest` 或 `raw`),綁定規則餵的是已遮罩的文字:`_ns_wd_binding_hit(masked, cut)` 裡的 `tail = masked[cut:]`,而 `masked` 來自 `_inline_visible_mask`(`:383`)再加引號遮罩。
- 我實測了 `甲句 [test:`t a`,`t b`] 尾`。`_inline_visible_mask` 把反引號包住的名稱整段換成 `\0`,綁定規則回 `None`。但 `_test_names_of` 本來就為「包住名稱的反引號」(Kotlin 測試名)寫了去反引號的邏輯,test_refs 與 S20 都認得這種寫法。
- 所以同一行在存在檢查那組算得出名稱,在綁定提醒這組算不出來,切法等於分岔了。
- 影響只是少一則提醒,不誤擋。不過這是本 diff 想避免的「兩套切法」的縫隙,所以列為不對齊。
- 摘要區塊的續行,`_ns_test_ref_lines` 以條目為單位接起來,綁定規則是逐實體行看。這跟鄰居的 count 與 position 逐行看一致,計劃「天花板」第 2 條也寫了,所以不列。

### F1 綁定規則拿遮罩過的行去切測試名,反引號包住的名稱算不出來,跟 test_refs 與 S20 的切法不一致
severity: minor
blocking: 否 — 只會少一則只提醒不擋的提示,不影響任何判定與回傳碼;結構上仍走同一套 `slot_parse` 加 `_test_names_of`,不是第二種工具
引句:「names, _empty = _test_names_of(slot_parse(tail))」
佐證行 file: `scripts/lumos:31505`(餵遮罩文字),對照 `scripts/lumos:32317`(`_ns_test_ref_lines` 餵原文)、`scripts/lumos:32256`(`_test_names_of` 有去反引號邏輯)

### F2 count、position、binding 共用的第三個回傳元素型別變成 str、None、list 三種
severity: minor
blocking: 否 — 只是讓 `_ns_wording_emit` 要多一層型別分流,功能正確
引句:「f"      → 這行綁了 {len(tag)} 支({'、'.join(tag)}):拆成一支一行,每行寫那支測試守的是哪一點"」
佐證行 file: `scripts/lumos:31574`(emit 內分流),對照 `scripts/lumos:31475` 附近(`_ns_wd_count_hit` 回字串標記)

總結:不對齊共 2 條,其中 major 0 條
