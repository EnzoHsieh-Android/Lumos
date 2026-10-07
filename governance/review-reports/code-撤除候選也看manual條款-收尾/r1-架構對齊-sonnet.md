severity: minor

## F1 同一篇筆記在 doctor 迴圈裡解析兩次 front matter
severity: minor
blocking: 否
引句:「rows = _ns_clause_rows(_note_from_text(rel, text), text)   # 同一篇只解析一次,[test:] 與 [manual:] 兩條路共用」
佐證:``scripts/lumos: `scripts/lumos:32003` `` 之前,`_ns_test_ref_lines` 內部已經自己做 `n = _note_from_text(rel, text)`。diff 把 `_ns_clause_rows` 的第一個參數設計成 `n`(筆記物件)。結果 doctor 為了呼叫它,在迴圈裡先 `_note_from_text` 一次,進 `_ns_test_ref_lines` 後又一次。
說明:結構方向是對的:clause_bindings 只跑一次,state 只認解析器給的。只是為了「每篇只解析一次」這個目的,front matter 反而多解析了一次。鄰居的 `_ns_test_ref_lines(rel, text)` 簽名吃 `rel, text`,`_ns_clause_rows` 吃 `n, text`,參數形狀跟它不同。這是簽名風格不一致,不是第二種做法。

## 三問

1. 分層與依賴方向:對齊。`_ns_clause_rows` 放在 `_ns_test_ref_lines` 正上方,同屬 `_ns_*` 筆記測試綁定這一層,只呼叫 `clause_bindings`(``scripts/lumos: `scripts/lumos:31981` ``)。`_ns_tr_manual_clauses` 放在 `_ns_tr_sub_says_retire` 旁,由 `_doctor_test_ref_lines` 呼叫,依賴方向是 doctor 到 `_ns_*` 到 `clause_bindings`,沒有跨層直呼。另外兩個 `_ns_test_ref_lines` 呼叫點(``scripts/lumos: `scripts/lumos:32089` ``、``scripts/lumos: `scripts/lumos:32286` ``)沒給 rows,走預設自己算,行為不變。
引句:「clause = {r["line"] for r in (_ns_clause_rows(n, text) if rows is None else rows) if r.get("defined")}」

2. 命名與錯誤處理:對齊。`_ns_` 前綴與 `_ns_tr_` 前綴沿用既有命名。錯誤處理沿用原本「解析出錯回空」的 `try/except Exception: return []`,只是從 `_ns_test_ref_lines` 與 `_ns_tr_manual_clauses` 兩處搬成一處,語意沒變。`_ns_tr_manual_clauses` 簽名從 `(rel, text)` 改成 `(text, rows)`,比鄰居更貼近純函式用法,不算不一致。
引句:「def _ns_tr_manual_clauses(text, rows):」

3. 第二種做法:沒有。
   - 選填參數接預先算好資料,專案有先例:`_suggest_systems_for_orphan(env, rel, n, vt=None)` 內 `r = vt if vt is not None else _verification_system_targets(env, rel, n)`(``scripts/lumos: `scripts/lumos:946` ``、`scripts/lumos:950`),以及多處 `if rows is None:`(``scripts/lumos: `scripts/lumos:6783` ``)。本 diff 的 `rows=None` 照這個模式寫。
   - 判「靠人驗」一律取 clause_bindings 的 state,不再自己解析,也不再把單行丟回解析器重判。repair 已經移除了單行重判那段。
   - 重複定義(duplicate/shadowed)不列,維護者已裁定,也寫進計劃天花板 2,不算偏離。
引句:「and 0 < r["line"] <= len(lines) and not _ns_tr_retired(slot_parse(lines[r["line"] - 1]))]」
(`_ns_tr_retired(slot_parse(...))` 沿用 ``scripts/lumos: `scripts/lumos:32403` `` 同區的既有用法。)

筆記面:新 WHY 行有 `[出處:]` `[因:]`;說明寫進家 Systems/lumos-cli-read,計劃有對應落點。沒有欄位缺漏。

不對齊共 1 條,其中 major 0 條
