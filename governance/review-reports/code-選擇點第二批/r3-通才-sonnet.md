severity: minor

## g1 C-34 的「when 分支」與「try」當值的命中沒有任何樣本守住
severity: minor
blocking: 否(能指出具體改壞且測試照綠,但規則是否收 try/when 值位置,計劃條文只列「指派右邊、引數、return、lambda 或 if/when 分支最後一個陳述、表達式本體」,try 不在列;屬規則實作的召回守衛,不是條款必要行為)

引句:「- inside: {kind: control_structure_body, inside: {kind: when_entry, inside: {kind: when_expression, matches: value-direct}}}」

失敗情境:這次修補把 value-used 裡的 `value-pos` 全換成 `value-direct`,但 `samples/choice-batch2.kt` 裡 when 分支與 try 的 HIT 樣本是 0 筆。try 只有一行 MISS(`if (c) try { x.let {…} } catch…`),when 只有 MISS(`when (c) { true -> x.let … }`)。我在臨時副本做了兩次變異:
- 拿掉 `value-used` 裡 try_expression 與 catch_block 兩個子句。
- 拿掉頂層 when_entry 那一個子句。

兩次 `python3.14 scripts/test_lumos.py -k batch2` 都是 58 passed, 0 failed。

用 ast-grep 直接跑 `val u = when { c -> x.let { it }; else -> 0 }` 與 `val w = try { x.let { it + 1 } } catch (e: Exception) { 0 }`,修後版本確實命中 C-34。所以實際行為是對的,只是這些子句被改壞時沒有測試會紅。

預期:這兩種寫法各有一條 `// HIT C-34` 樣本。
實際:沒有。

歸因:有證據的原有漏查。修前 6cc9ad8c 的同一批子句(用 value-pos)同樣沒有 HIT 樣本,修前樣本 diff 只有 `val z = if` 一條 HIT。修補只是改了子句內容,沒有補守衛。
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`

## 圖譜鏡頭(固定席逐條判)
- kotlin規則包 [家]:牽連檔 check.py、api.yml、test_lumos.py。這次 check.py 沒改,api.yml 與測試的改法跟計劃條文的新增句一致,不影響。
- bound-tests-gate、guard-kill、lumos-cli-lifecycle、測試假綠形態、lumos-cli-read 的 ★INVARIANT★:都不影響。
  - 修補在 scripts/lumos 只動 `_render_gov_choice` 的排序鍵,不碰 guard kill 的 rc、`--json` 輸出、re-inject、search 篩選與綁定測試跑法。
  - 在 test_lumos.py 只加選擇點案例,沒動任何被這些合約綁定的測試。
- pitfalls-code-loop、loop-convergence-recording 的 ★RISK★ 與其餘只列名的節點:不影響,因為 scripts/lumos 的改動範圍只有 gov --stats 的列號排序。

## 三問(同一案例證據)
修前 = 6cc9ad8c,修後 = 87093835,規則檔用 `ast-grep scan --rule rules-choice/api.yml`。

① 原問題修復效果

| 案例 | 輸入 | 預期 | 修前 | 修後 |
|---|---|---|---|---|
| else-if 當陳述 | `if (c) 1 else if (d) x.let{…} else 0`(巢狀分支裡的 if 當值) | C-34 不命中(刻意漏抓) | 命中 | 不命中 |
| 帶大括號的 else-if | `else if (d) { x.let {…} }`(同上) | C-34 不命中 | 命中 | 不命中 |
| 語意改變的字面值 key | `LaunchedEffect(-1.coerceAtLeast(k))` | C-36 命中 | 不命中 | 命中 |
| 數字常數 key | `+2.5`、`-1L`、`- 1`、`-0x10`、`-1e3`、`+1f`、`-1u`、`remember(-1.5)` | 不命中 | 未跑,見註 | 全部不命中 |
| 變數 key | `LaunchedEffect(-k)`、`--k` | 命中 | 未跑 | 命中 |
| 列號 `C-` 加 5000 個 9 | gov --stats 依列號 | 不丟例外 | 修前測試未跑 | `t_gov_stats_choice_by_row` 6 passed(新案例通過) |

註:數字常數 key 修前沒另外跑;修前規則是 `^[-+]\s*[0-9]`,語意上對這些字面值也應不命中,未判定的是 `-1.coerceAtLeast(k)` 以外的差異。

- 巢狀 else-if 加 1 條單層 if-else 的壓力檔,輸出量從 3,160,157 位元組降到 11,995(同一份 `p.kt`,300 段 else-if 鏈加 200 層巢狀 if)。
- 本鏡頭其餘兩條歸因皆為:修後行為正確;修前行為取自實跑結果。

② 修補處的正常、錯誤與相鄰路徑
- 保留路徑:`val y = x.let{…}`、`val z = if (c) x.let{…} else 0`、`fun h() = if (c) x.let{…} else 2`、`val v = if (c) { x.let{…} } else {1}`、`val u = when{…}`、`val w = try{…}`、`val r = x.let{ it }` 在修後都命中。
- 相鄰路徑:`val s = try { if (c) x.let { it } else 0 } catch …` 修後不命中,屬保守漏抓,修前也是同一判法。
- `-(1)` 仍算命中,這跟修前一樣,不是新問題。
- `list.forEach { if (c) x.let { show(it) } }` 命中(lambda 最後一個陳述),修前也命中,屬既有的保守取向。

③ 新發現的同一案例修前修後:只有 g1,結果見上,修前修後皆「子句被拿掉測試照綠」。

## 其他已驗與未驗
- `python3.14 scripts/test_lumos.py -k batch2` 58 passed;`-k gov_stats_choice_by_row` 6 passed。
- `_row_key` 限 `len(n) <= 9`,對 5000 位數字與 `C-²` 不再丟例外。
- 已撤列號那行前面有縮排時,check.py 回「恰好一行」那句看不懂訊息。
- 未驗:單行上千個 `?.` 的輸出量(作者已標為自動測試沒覆蓋)。

最嚴重:minor;blocking 共 0 條
