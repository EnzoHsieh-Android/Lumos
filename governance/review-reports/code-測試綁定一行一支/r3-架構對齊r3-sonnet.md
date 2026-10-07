severity: minor

**1. 分層與依賴方向:對齊。**
- `_ns_wd_binding_hit`(`scripts/lumos:31507` 起)放在 `_ns_wd_line_hit`、`_ns_wd_count_hit` 同一組,由 `_ns_wd_line_hit`(`scripts/lumos:31478`)呼叫,再經 `_ns_wording_hints`(`scripts/lumos:31526`)、`_ns_wording_collect` 進 `_ns_wording_emit`。這條鏈跟數量、位置兩條規則一樣。
- 新碼只往下呼叫 `_slot_scan`(`scripts/lumos:4239`)、`_test_names_of`(`scripts/lumos:32268`)、`_ns_tr_placeholder`、`_NS_NEG_QUOTES`。沒有跨層直呼,也沒有繞過判定層去碰印出或記帳。
- `_slot_scan` 原本有兩個呼叫端,`slot_parse`(`scripts/lumos:4274`)和 `_slot_strip_keys`(`scripts/lumos:4292`),現在多一個(`scripts/lumos:31513`)。它自己的 docstring 寫明「掃描規則只有這一份」,所以這是沿用,不是另起一套。

**2. 命名與錯誤處理:對齊。**
- 命名跟鄰居一致:`_ns_wd_*`、`_NS_WD_BINDING_SHOW`、規則字串 `"binding"`。`_slot_scan` 的 6 元組解包名(`kind, a, _b, key, val, err`)也跟 `slot_parse` 同形。
- 沒有新增例外處理。失敗仍由 `_ns_wording_collect` 清空並記類別名、`_ns_wording_emit` 只印一句,判定不受影響。
- 印出和記帳(`_gate_event_or_warn`、`rules` 排序去重、`lines`、`notes`)都沿用原路。
- 名稱截短改成 `f" 等 {n} 支"`,跟檔內既有寫法一致(`scripts/lumos:7754`、`scripts/lumos:16184`、`scripts/lumos:36429`)。`scripts/lumos:34410` 的「…等共」是檔內少見的那種,修補把它改掉了,方向對。

**3. 第二種做法:大致沒有,只有一處小重複。**
- `_ns_wd_binding_hit` 自組 `{"fields": fields}` 餵 `_test_names_of`,檔內已有先例:`scripts/lumos:28998` 也是 `_test_names_of({"fields": [(key, val, None)]}, key)`。所以這不算第二種做法。直接用 `_slot_scan` 取欄位起點,是因為要拿起點座標去對引號範圍,`slot_parse` 不回座標,合理。
- 「整個被引號包住的名稱不算」(`scripts/lumos:31519`)是手寫的 `nm.startswith(qa) and nm.endswith(qb) and len(nm) > 1`。專案已有 `_ns_neg_quote_spans`(`scripts/lumos:30975`)做同一件事:成對引號判定,同樣用 `_NS_NEG_QUOTES`。這裡沒呼叫它,等於另寫一份配對判斷。不過它共用同一張引號表,判定也只有一行,結構上沒有新的分歧來源。我判 minor。
- 三條規則的建議句統一放第三欄,`_ns_wording_emit` 簡化成 `→ {tag}`(`scripts/lumos:31577` 附近)。這跟數量、位置兩條規則本來就用同一個三元組形狀,只是把原本在 emit 裡的 if 鏈搬到各規則自己手上,是收斂而非新做法,對齊。

### F1 手寫的整個被引號包住判定沒用既有的 `_ns_neg_quote_spans`
severity: minor
blocking: 否 — 共用同一張 `_NS_NEG_QUOTES` 表,行為等價,只是同一件事有兩種寫法,可在之後順手收成呼叫既有函式
引句:「and not any(nm.startswith(qa) and nm.endswith(qb) and len(nm) > 1 for qa, qb in _NS_NEG_QUOTES)」
佐證行 file: `scripts/lumos:31519`、`scripts/lumos:30975`

總結:不對齊共 1 條,其中 major 0 條
