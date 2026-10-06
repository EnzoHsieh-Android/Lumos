severity: clean

正確性鏡頭:遮連結用等長佔位字、位置不變;`_drift_pending_clauses` 回傳的起訖與子句文字仍來自未遮連結的 masked,找連結(`_drift_pending_links`、`_drift_target_clause_ends`)照用原文。
引句:「bare = WIKILINK_RE.sub(lambda m: _DRIFT_QUOTED * len(m.group(0)), cl)」
實測:連結標題內含切點(——、;、別名內。)時,連結被切成兩半、後半的待定詞漏出,`_drift_pending_clauses` 會回 `還沒做]]` 這種子句;但該子句與前半都不含完整連結,所有呼叫者(`_drift_c6`、`_drift_backrefs`、`_drift_target_clause_ends`)都要求同子句有完整連結才列,所以不會誤報,屬無後果的邊角。`_DRIFT_QUOTED` 與 `_DRIFT_MASK` 是不同字元(\x01 對 \0),不撞;`_DRIFT_MASK not in cl` 仍看原子句,已裁定括號判斷不變。連結外沒字只有連結的行改為不列,符合計劃宣告。

測試鏡頭:t_drift_c6_ignores_link_title_words 的寅、辰在不遮連結時確會命中「還沒做」而紅,卯是連結外待定詞的對照,非假綠。
引句:「check("②連結外真的寫了「還沒做」:卯照列", isinstance(got, list) and _c6_ln(live, "卯 ") in got, str(fs))」

圖譜鏡頭:固定席(lumos-cli-read、lifecycle、guard-kill、design-loop、bound-tests-gate 等)的 INVARIANT 都不涉及 c6 待定詞判定,改動只在 `_drift_pending_clause` 一處,未破壞任何宣稱的合約。
引句:「return any(w in bare for w in _DRIFT_PENDING_WORDS) and _DRIFT_MASK not in cl」

角色鏡頭:未附角色卡,略過。

總結:改動小且位置安全,呼叫者行為只有「待定詞僅在連結文字內」的行不再列出,無阻擋性問題。
