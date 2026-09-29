severity: minor

鏡頭:合約與圖譜一致。已跑 t_drift_unknown_blocks_check_not_scan、t_drift_when_probes_evaluate_and_trigger、t_note_shape_revisit_needs_date_or_probe、t_doctor_revisit_skips_probe_lines、t_drift_exam_scores、t_doctor_drift_section、t_set_plan_closed_lists_satisfied_status_probes(S2 S9 S10 S11 S13 S14 S15)、-k drift_code_review_yi、-k lens(213)、-k note_shape(113)、-k note_audit(175)、-k revisit,全綠;lumos lint 兩篇筆記 0 問題。

## F1 「候選判不了」與「語料有讀不出的檔」兩條新分支沒有任何測試守得住
severity: minor
blocking: 否 — 現行行為對得上筆記與條款文字,只是新增的兩條判不了路徑改壞不會有測試紅,沒有現行的錯誤結果
引句:「+            unknown.append(f"{p}:{no} 的條件判不了(" + ("超過預算" if out() else "git 讀不出這次改到的程式檔") + ")")」
1. 我在自己的臨時副本(/tmp/cy3mut.*,非任何 repo)把 _drift_probe_candidates 裡 `if cand is None:` 之後改成 `continue`(等於候選判不了就放行),跑 `-k drift`(184 支斷言):結果與未改動的副本完全相同(3 紅是副本缺 README/docs 造成的環境紅,未改動時也是同 3 條),S2 綁的 t_drift_unknown_blocks_check_not_scan、r2 回歸全綠。
2. 同樣把 _DriftProbeTree.one 的 `return None if self._unread[test] else False` 改成 `return False`,`-k drift` 一樣沒有新紅。r2 回歸的 C1 只釘「帶路徑」的那條(src/api.py::new_api),不帶路徑找不到定義、語料裡有讀不出檔那條沒有釘。
3. 筆記 Systems/存量漂移守衛.md 的 WHY(乙代碼審 r2 外家席)寫「碰到它的條件算判不了」並綁 t_drift_code_review_yi_r2_regressions;測試 docstring 的翻紅清單也只列 C1、C2。S2 條款是「判不了要算要處理」,這兩條是這份修正新增的判不了來源,綁的測試守不住。
4. 附帶:S9 綁的 t_drift_when_probes_evaluate_and_trigger 對「不帶路徑、名稱只在改到檔的終點全文」那條候選規則也沒紅(把 _drift_probe_cond_candidate 的全文比對整段短路成 return False,S9 測試仍 11 條全過;只有 yi_r1 的 C2 與 yi_r2 的 B1、B2 會紅)。該規則在筆記 PITFALL 已綁 r1、r2 測試,所以只算 S9 條款文字沒涵蓋,不另立。

## F2 Systems〈跟設計稿不一樣〉新增的候選規則那條,跟同一份差異改過的計劃互相矛盾
severity: minor
blocking: 否 — 只是讀者會被誤導去找一個已經不存在的差異,不影響程式行為
引句:「+- **不帶路徑的條件怎麼算候選**(乙代碼審 r2 正確性席):設計寫」
1. 這條寫「設計寫『名稱出現在範圍的改動行』,實作改成『…終點全文』」,放在〈跟設計稿不一樣〉。
2. 但同一份差異已把計劃〈做法〉第 0 節改成「名稱出現在範圍裡改到的程式檔或測試檔的終點全文(乙代碼審 r2 改:原本寫「改動行」…)」,設計稿與實作現在一致。
3. 三個月後的人照這條去計劃找「改動行」的設計會找不到,以為筆記或計劃漏改;該條應改標成「設計已同步改成全文」或搬離〈跟設計稿不一樣〉。
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:55`

## 已看,無 finding 的部分
- 計劃第 0 節 git 次數(只剩一次 name-status;帶路徑條件批次讀):對得上 _drift_probe_changes 已無 -U0 diff、_drift_probe_prefetch 每版一次;兩篇筆記已無「-U0」「新增行」殘留字樣。
- 計劃第 2 節「正規化後再驗一次文法」:_probe_parse 對得上;`..\x.py` 由 D1 釘住,S9/S10 相關測試全綠。
- Systems 三條新 PITFALL 與兩條 WHY:都有出處(輪次與席位)與綁定測試,測試名存在且通過;語意(MemoryError/RecursionError、utf-8-sig、NFD 重讀、樹上列得出讀不出算判不了)逐項對得上 HEAD 程式。
- 筆記沒有新寫程式碼查得到的 FACT/FLOW/DEP;程式註解引用的函式名(_head_is_shebang、_shebang_line_is_python、_drift_status_probe_followups、_NotelinesNet)與席位出處都存在。
- 既有合約:_shebang_python_blob 改呼叫 _shebang_line_is_python,語意與原式相同,-k lens 213 條全綠;筆記形狀擋、筆記內容審、doctor E5 相關測試全綠,未被破壞。
- yi_r1 的 C2(-diff 屬性)在移除 --text 之後仍守得住:把全文比對短路後 C2 轉紅。

最嚴重等級 minor,blocking 共 0 條。
