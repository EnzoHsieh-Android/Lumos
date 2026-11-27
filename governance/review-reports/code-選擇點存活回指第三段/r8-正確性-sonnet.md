severity: minor

修補驗收:這次修補修到了,也沒有引入新問題。

- 要修的情況:驗收條款標題帶說明,讀取器讀不到那一節時,條款原文不再同時出現在條款和正文。
- 我自造輸入走了一遍,也跑了新測試 `t_choice_plan_view_body_drops_clause_lines`,結果 2 passed、0 failed。
- 見 [S1] 這種行內引用行、條款旁的說明句,都照樣留在正文,沒被誤扣。原因是 `clause_bindings` 只把「該編號第一次出現在行首」那一行標成定義行,`r["line"]` 也只取這一行。
- `_choice_plan_view` 是三個讀者(第 2 層驗證、deps_sha、材料)唯一取段落的地方,看了 `_choice_plan_view` 的呼叫點只有 `_ChoiceLayerCtx` 一處,沒有另開一套取段。

finding(同類位置,兩條):

1. 標題形式的條款(例如 `### [S2] 條款原文`)原文仍會從段名漏進正文那一邊。`_CLAUSE_LEAD_RE` 把 `#` 標題算成定義行。但 `_choice_plan_sections` 的迴圈先判標題,標題行不經 `taken` 過濾,於是段名 `〈範圍〉/〈[S2] 標題條款原文 …〉` 同時帶著條款原文。我造了 `## 範圍` 底下接 `### [S2] 標題條款原文 [manual:人工看一次]`,段名確實出現這串字。影響是第 1、4 層的 `all` 和材料的 `##### 段名` 會看到條款原文。第 2 層的 quote 錨點取自段落內文 txt、不取段名,不會判錯,只是材料重複。

severity: minor
blocking: 否
scripts/lumos:81134 標題形式條款的原文從段名漏進正文側,屬於上一輪(r7)同類。
引句:「m = _CHOICE_HEAD_RE.match(lines[no - 1]) if no in visible else None」

2. 重複定義的條款,第二個定義行仍留在正文。我造了 `- [S1] 條款甲原文` 加一行 `- [S1] 重複第二行`,第二行出現在段落〈驗收條款(說明)〉的正文裡。`clause_bindings` 的 duplicate 和 shadowed 列只回報第一個定義行,所以扣不到第二行。這種情況在規格閘本身就會因重複定義而擋下,實際影響很小。

severity: minor
blocking: 否
scripts/lumos:81174 重複定義的後續行不在 `clause_lines`,仍留在正文。
引句:「secs = _choice_plan_sections(text, {r["line"] for r in rows})」

沒有發現會做錯事的輸入。

總結:最高等級是 minor
