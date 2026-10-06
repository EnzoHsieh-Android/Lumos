severity: minor

## F1 close_summary 設成壞值時完全沒講一句
severity: minor
blocking: 否 — 只影響提醒開關的可發現性,不改 rc、不影響判定
引句:「if _note_shape_mode_parse(cfg_text, "close_summary", "結案摘要提醒")["mode"] == "off":」
共用解析函式回的 warns(例:`note_shape.close_summary="block"` 的「看不懂(只認小寫 warn/off),照 warn」)在 _ns_close_summary_collect 被整個丟掉;tag_hints 那條路會印這句、doctor 也有行。實跑:config 設 close_summary:"block" 或 "OFF",提醒照印、無任何「看不懂」訊息,使用者以為已關掉。重現:scratchpad/exp3.py(rc=0、只有提醒本文)。

## F2 摘要比對只認前綴行,與 c7「不分前綴」不一致
severity: minor
blocking: 否 — 只多/少提醒,不擋
引句:「list(_ns_summary_logical(ot).values()), list(_ns_summary_logical(nt).values()))」
_ns_summary_logical 只收符合 SYMBOL_RE 的前綴行。實跑 exp2.py:(a) 摘要裡有一行無前綴自由文字、結案同時把它從「自由文字舊」改成「自由文字新 尚未裁定」,前綴行沒動 → 仍回 ['KEY:a'] 判成「摘要沒動」,誤報;(b) 單行 `summary: KEY:a 尚未裁定`(status 改 resolved)→ 回 None,漏報,而 c7(_drift_pending_lines)會抓到這種單行。罕見形狀,故 minor。

## F3 圖譜內有一個路徑含換行,整批結案對照靜默失效
severity: minor
blocking: 否 — fail-open 且有印一句
引句:「blobs = _nodehome_cat_blobs(root, [f"{base_where}:{o}" for o, _n in cands] + [f":{n}" for _o, n in cands])」
_nodehome_cat_blobs 遇任何含 "\n" 的 spec 回 None,整批變「對照沒做成(git)」。實跑 exp1.py「newline-path+normal」:同次提交另一篇正常結案的筆記也被漏掉,訊息只寫「(git)」看不出原因。現實出現機率極低。

## 已讀無 finding 的節
- 篩選與 -z 解析:`-G ^status:` 對 frontmatter 重排(status 值沒變)不列、CRLF 檔照命中、status 在正文不誤判、帶空白中文路徑與改名(R)正確;引句:「r = _lens_git(root, "diff", "--cached", "--name-status", "-z", "-M", "--diff-filter=MR", "-G", "^status:",」
- 暫存版讀 `:<路徑>` 成立(實跑:提交前只暫存的新 status 被讀到);超過 50 篇時 skipped=10 並印「另 10 篇沒看」,僅輸出偏長(50 篇各最多 7 行),不構成 finding;引句:「skipped = max(0, len(cands) - _NS_CLOSE_SUMMARY_MAX_NOTES)」
- _drift_note_status:雙引號、單引號、status 放在 summary 後、重複 status 皆得 resolved;無 status 欄位回 None,「無 status→resolved」會提醒(合理);`status: resolved # done` 因 parse_frontmatter 保留註解而不命中(與全 repo 讀法一致,非本 diff 新增)。引句:「v = parse_frontmatter(lines[1:e])[0].get("status")」
- _note_shape_mode_parse 共用後 tag_hints 訊息逐字不變(f 字串展開後同字);`-k note_tags_hints` 9 passed;`-k drift` 1053 passed、`-k close_summary`/`-k c7` 全綠;c7 的 drift scan / ack(綁行號與原因)/fix 指路實跑正常。引句:「return _note_shape_mode_parse(text, "tag_hints", "筆記前綴提醒")」
- 新測試不會改壞照綠:⑥⑦(引號、改名)與 ⑨(off)在去掉對應邏輯時各有獨立紅點;c7 測試對 WHY/PITFALL、已裁定括號、連結遮罩都有格子。引句:「check("⑥WHY、PITFALL 行是決策與事故紀錄,不列", not c7b, str(c7b))」
- 圖譜鏡頭:固定席節點(lumos-cli-read、guard-kill、bound-tests-gate 等 INVARIANT)的牽連面是 search 濾網、guard kill rc、bound-tests 逐支真跑、授權白名單、re-inject、處置閘第五步;本 diff 只加提示輸出與 c7 列舉,不碰這些合約,逐條判不影響。唯 hinted 帳共用 gate=note-shape/kind=hinted,度量規則若按 gate.kind 統計會把 close-summary 併入,但 tag-hints、negation 已是同一做法,非新洞。
- 資料狀態五問:新舊互讀(舊筆記無新開關、缺鍵照 warn,可);寫一半(只讀 git 物件,不寫檔,無);衍生資料(hinted 帳多一種 check 值,既有同做法);時間(以暫存當下 HEAD 與索引為準,同一刻自洽);不可逆(只印提醒,無寫入)。

總結:第 2 輪修正沒有引入會誤擋或崩潰的新洞,只剩三個低風險的提醒精度與可發現性小問題。
