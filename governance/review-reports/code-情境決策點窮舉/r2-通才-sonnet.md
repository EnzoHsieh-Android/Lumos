severity: minor

hook 沒附固定席節點,範圍標示「這次沒附固定席節點」。圖譜鏡頭只能從 diff 的內容判斷,見最後一節。另外,`lens-r2.txt` 這份後備我沒去讀。派工詞要求檢查的 `.warming` 鎖,我只看了快取目錄,沒有進一步查它。

## 1. `_visible_lines(keep_fenced=True)` 在圍欄沒關到檔尾時丟掉最後一行,跟 scripts/lumos 不一致
severity: minor
blocking: 否
引句:「hidden.update({a, end} if keep_fenced else range(a, end + 1))」
file: `scripts/lumos:5405-5408`(對照版:未收尾區段 `end` 是 None,只藏開頭標記行);`scripts/test_lumos.py:127641`(`t_kotlin_template_fence_parity` 只比 `keep_fenced=False`)
失敗場景:區段沒收尾時 `end = len(lines) - 1`,於是 keep_fenced 路徑把檔案最後一行當成收尾標記藏掉。
- 實測 `_visible_lines(["a","```","x","y"], keep_fenced=True)`:check.py 回 `['a','x']`,scripts/lumos 回 `['a','x','y']`。
- `_fence_body("## T2 x\n### 壞寫法:API-1 y\n```kotlin\nval a = 1\nval out = query.flatMapConcat { it }", "T2","API-1")` 只回 `val a = 1`,最後一行 `val out = …` 不見了。
- 若有「範本」改由的片段落在檔尾沒關的圍欄最後一行,會被誤報「片段不在範本…小節程式裡」。目前型錄的範本改由是 0 個,所以現在沒有實際影響。
- 這也讓程式註解與計劃寫的「同 scripts/lumos 的 keep_fenced」、「圍欄沒關時的寬嚴退讓照 `_visible_lines` 的同一套」不成立。
- 平行測試抓不到:`t_kotlin_template_fence_parity` 的十一個案例全跑 `keep_fenced=False`。我把 keep_fenced 路徑改壞,這支測試不會變紅,因為它根本沒走到那條路。
歸因:有證據的修復回歸。修前 `_fence_body` 自己的 `fenced.update(range(x + 1, (y if y is not None else len(lines))))` 會保留到檔尾,修後才丟最後一行。修前版本我只讀碼、沒實跑。修後版本實跑如上。

## 2. `_bad_lines` 用 `splitlines()` 與 `split("\n")` 兩套切法,行索引會錯位,`// BAD` 標記被靜默丟掉
severity: minor
blocking: 否
引句:「code = lumos._strip_c_comments(text, blank_strings=True, keep_newlines=True, kotlin=True).split("\n")」
file: `configs/ast-grep/kotlin-android/check.py:1113-1140`;`raw = text.splitlines()` 與 `code[no - 1]` 逐行對位
失敗場景:`raw` 用 `splitlines()`,它在 `\x0c`、`\x0b`、U+2028、U+0085、單獨的 `\r` 也斷行。`code` 用 `split("\n")`,只在 `\n` 斷。壞例檔含這類字元時,後面所有行的 `raw` 行號和 `code` 索引錯位。
- 實測檔案 `val s = "a\x0cb"\nval x = bar() // BAD\n`,`_bad_lines` 回 `[]`,標記整個消失。檔案 `val s = 1 // a\x0cb\nval x = bar() // BAD\n` 結果相同。
- 後果是 `規則` 改由報「片段不在 samples/bad/<id>/ 標了 // BAD 的行上」的假紅。依錯位程度,也可能對到別行,或在檔尾 IndexError 讓整個自檢崩掉(我沒構造出崩掉的案例)。
- 實務上壞例樣本很少含這些字元,所以只列 minor。
歸因:有證據的修復回歸。修前版本(8cd6d3c)只用 `splitlines()`,`out` 回 `…a.kt, 3, 'val x = bar()'`,標記還在(行號也不對,但標記有被認到)。修後版本回 `[]`。修前、修後都實跑過。

## 3. `// BAD` 判斷用原始行、去註解結果用另一份,字串裡寫 `// BAD` 的行會被當標記
severity: minor
blocking: 否
引句:「if not _BAD_MARK_RE.search(ln):」
file: `configs/ast-grep/kotlin-android/check.py:1124-1130`
失敗場景:`_BAD_MARK_RE` 掃的是未剝字串與註解的原始行。壞例裡 `val s = "see // BAD"` 這種字串會被判成標記行,而且 `code[no-1]` 非空,等於把一行不相干的程式登記成「標 BAD 的行」。
- 副作用是片段只要出現在那行字串以外的地方就能蒙混通過。
- 修補理由裡已寫「字串裡的 // 不算註解」,只套在去註解那一邊,沒套在標記判斷。
- 我沒有實跑這個案例,僅從碼推論,所以標 ⚠。
歸因:未判定。修前版本用 `ln.find("// BAD")` 同樣吃字串裡的標記,所以這比較像原有漏查,而不是修補造成。

## 三問回答

1. **原問題的修復效果有何行為證據?**
   - 在修後版本跑了 `--catalog-only`,型錄問題 0 個。
   - `-k api_decision_points` 38 過、`-k bad_snippets_reach` 41 過、`-k template_fence_parity` 11 過。
   - 單項實測:`_parts_in_order(lm,"…",…)` 對只有 `…` 的片段回 False(測試檔有案例)。
   - `_bad_lines` 對 `//BAD`、`// BADGE`、`// BAD-NEXT` 與續行的處理,我沒獨立重跑,只讀了新增的測試。
   - 路徑正規化(`_sample_abs`)、重複列偵測、同名異義例外,我只讀碼,沒獨立構造案例。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - `scan()` 包 `scan_ranges()` 這段不在這份 diff 裡,前後版本相同(三元組推導、`_TIMED_OUT` 行為不變)。我查到 `scan()` 的呼叫者只有 `check.py` 的 `ancestor-named-test` 那段,與 `scripts/test_lumos.py:127400`。
   - `_visible_lines` 新參數預設 False,舊呼叫者(`template_sections`、parity 測試)路徑不變。keep_fenced=True 的新路徑有第 1 條的問題。
   - `dt_evidence_parse` 改用 `_snippets` 與原運算式等價。`_unreach_table` 的片段格改用 `_snippets` 後,「`x` 後面再接雜字」的格子現在會被收成 `x`,比修前寬鬆。這個放寬我沒構造出會讓錯誤放行的案例,未判定。
   - `_norm_colon` 換成 `_norm` 只多轉全形括號,對歸屬欄與理由欄無害。
3. **新發現的同一案例在修前、修後各是什麼結果?** 都列在上面各條「歸因」行。只有第 1、2 條是修補自己引入的,第 3 條未判定。

未驗範圍:`--sg` 完整模式的實跑(沒裝 ast-grep),D-4 例外樣式加 `flatMapConcat` 的行為影響(只從碼讀它放寬了「選 alt 時的證據核對」,那層只提醒不擋,我判定不構成回歸),`jvm-only.txt` 的新列、型錄資料列與卷證 sweep 檔的內容正確性。

## 圖譜鏡頭

hook 沒附固定席節點,只從 diff 內容判斷:
- `Systems/kotlin規則包.md`、計劃與驗證筆記的改動只是補述,沒有改到 `★INVARIANT★` 之類的合約行,我沒看到被破壞的合約。
- 計劃筆記宣稱「圍欄沒關時的寬嚴退讓照 `_visible_lines` 的同一套」,與第 1 條實測不符。這是筆記錯在 keep_fenced 路徑,不是合約。

總結:最高等級 minor,共 3 條
