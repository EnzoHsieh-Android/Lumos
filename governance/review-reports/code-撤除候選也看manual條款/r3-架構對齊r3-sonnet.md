severity: major

## F1 重複定義時把單一行再丟回 clause_bindings,是專案裡沒有的第二種做法
severity: major
blocking: 是
引句:「r = next(iter(clause_bindings(lines[no - 1], {}, None, lambda _p: set(), lambda _p: "")), {})」
佐證:
- ``scripts/lumos: `7991:` ``(untagged 集合直接包含 "duplicate" 與 "shadowed")
- ``scripts/lumos: `8012:` ``(spec-trace 把 duplicate 與 shadowed 標成 ✗)
- ``scripts/lumos: `6795:` ``(dups 另列)
- ``scripts/lumos: `6798:` ``(shad 另列)
- ``scripts/lumos: `31995:` ``(同樣的空索引呼叫 clause_bindings(text, …) 只取 `defined` 的行號,餵的一律是整篇 text)

說明:
- 既有碼對 `clause_bindings` 回傳的 `state` 只有一種用法:原樣信它。duplicate 與 shadowed 在處置閘與 spec-trace 都是獨立狀態,沒有人拿來重判。
- 這份 diff 遇到這兩個狀態,就把那一行單獨切出來再丟進同一支解析器,拿第二次的 state 當結論。
- 原本的「判靠人驗只信 `clause_bindings`」口徑因此分成兩套:整篇解析一套,單行重判一套。
- 單行重判還會丟掉 `_visible_lines` 的 fence 與跨行註解狀態,以及「同編號是否已定義過」的脈絡。這個脈絡正是 duplicate 與 shadowed 這兩個狀態要表達的東西。
- 這正是上一輪 r1 已經判為「自己又解析一次等於第二種做法」的那一類,換了個形狀回來。
- 空索引的 lambda 呼叫本身有先例(31995)。沒有先例的是對單行重判。

## F2 條款解析在同一篇筆記被呼叫兩次
severity: minor
blocking: 否
引句:「rows = clause_bindings(text, {}, None, lambda _p: set(), lambda _p: "")」
佐證:``scripts/lumos: `31995:` ``(`_ns_test_ref_lines` 已經為同一篇 text 跑過一次 clause_bindings)
說明:
- `_doctor_test_ref_lines` 每篇先呼叫 `_ns_test_ref_lines`(內部解析一次),再呼叫 `_ns_tr_manual_clauses`(又解析一次)。
- 結構上沒有跨層,只是同一份解析重做了。
- 既有的做法是同一個迴圈裡取一次結果。這裡的第二個迴圈與 `_ns_test_ref_lines` 平行,是補丁式的鋪法。

## 三問

1. 分層與依賴方向:對齊。
   - 新碼 `_ns_tr_manual_clauses` 放在 `_ns_tr_sub_says_retire` 之後、`_doctor_test_ref_lines` 之前,同屬 `_ns_tr_*` 層。
   - 它由 doctor 呼叫,呼叫 `clause_bindings`、`slot_parse`、`_ns_tr_retired`,方向與鄰居一致,沒有跨層直呼。
   - 引句:「for no in _ns_tr_manual_clauses(rel, text):」
2. 命名與錯誤處理:對齊。
   - `_ns_tr_` 前綴與鄰居一致。
   - `except Exception: return []` 與 `_ns_test_ref_lines` 的 `except Exception: clause = set()` 同形(31995 附近)。
   - 入口篩選沿用已有的 `MANUAL_REF_RE`(5275)。
   - 引句:「except Exception:」
3. 第二種做法:有一處,即 F1。
   - 其餘部分沒有新做法:`state == "manual"` 直接取自 `clause_bindings`(r1 已修),`_ns_tr_retired` 與 `_ns_tr_sub_says_retire` 沿用。
   - 引句:「if r.get("state") in ("duplicate", "shadowed"):   # 重複定義時整列不給 manual;只拿這一行再判一次」

筆記欄位:新 WHY 行有 `[出處:]` 與 `[因:]`。計劃的 `lands_in` 已補上 Systems/lumos-cli-read,與實際寫了說明的節點相符,沒有 minor。

不對齊共 2 條,其中 major 1 條
