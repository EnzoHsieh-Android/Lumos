severity: major

A1
severity: major
blocking: 是
引句:「z = sum(1 for n in counts if n == 0) if (has_var or len(counts) <= len(segs)) else 0」
file: `governance/eval/lens-utilization/recount.py:951`
`has_var` 為真時整段繞過 `len(counts) <= len(segs)` 的安全網,只要同一次呼叫的輸出裡多出任何符合零命中樣式的行就全部信、全部加總。實測:`for q in "$terms"; do lumos search "$q"; done; grep -n "\"candidates\": 0" scripts/test_lumos.py`(真的跑了一次零命中,後面 grep 到本檔既有測試裡那行 JSON 治具)餵進 `_search_events`,`zero_unattributed` 回報 2,實際只發生 1 次零命中,多算一倍。

A2
severity: major
blocking: 是
引句:「if len(segs) == 1 and segs[0] is not None:」
file: `governance/eval/lens-utilization/recount.py:942`
`xargs -I{}` 這種語法上只出現一次「lumos search」、實際卻逐行各跑一次的形狀,不會被只認 `$` 的 `_VAR_QUERY_RE` 攔到,落進單一分支直接用 `_search_verdict`(`.search()` 只抓第一個計數行判)。實測:`printf "foo\nbar\n" | xargs -I{} lumos search {}` 真的各跑一次零命中與一次有命中,依兩次真實輸出出現的先後,結果會整段判成「hit」或整段判成「zero」,另一次搜尋連 undetermined 都沒留下就消失。

A3
severity: major
blocking: 是
引句:「一次呼叫裡每個 lumos search 各一筆」
file: `governance/eval/lens-utilization/recount.py:932`
這句 docstring 宣稱的目標,在單一 `&`(背景執行,非 `&&`)串接兩個 `lumos search` 時沒做到——沿用的 `_segment_command` 不切單一 `&`,兩次呼叫被併成一個 segment,查詢詞污染成 `"x & lumos search y"`,第二個真實搜尋完全沒被記到。實測:`lumos search "x" & lumos search "y"` 餵入一筆 hit+一筆 zero 的真實輸出,只回傳一筆事件、query 是垃圾字串,第二個搜尋(可能正是那次零命中)整個蒸發,不進 zero、不進 undetermined、也不進 zero_unattributed。

附:圖譜鏡頭前 8 篇逐條判——bound-tests-gate/canary-audit/design-loop/guard-kill/lumos-cli-lifecycle/slim-get/slim-install/slim-uninstall 這八篇 INVARIANT 都跟裝機、re-inject、canary 記帳、guard kill rc 這些機制有關,本次 diff 只動 `lens-utilization/recount.py` 的搜尋零命中計數與 `lens_weekly.py`/README 的對應文字,不觸碰上述任一機制的程式路徑,八篇皆不受這份 diff 影響。

全份最高嚴重度是 major,blocking 共 3 條。
