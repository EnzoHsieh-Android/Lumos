severity: major

## 1. 真型錄的證據樣式測試在修前、修後都是紅的
severity: major
blocking: 是
引句:「用 `collect`、`flatMapConcat` 依序做完,或排隊(`Channel` + 單一消費者)」
file: `scripts/test_lumos.py:131152`(`t_kt_catalog_evidence_patterns`)
失敗場景:
- 輸入:真型錄 `skills/kotlin-idioms/checks-catalog.md`。
- 斷言一:`_n` 用 `^\|\s*D-\d+\s*\|` 在整份型錄數列。新增的〈叫不出的壞寫法〉表也有 `| D-n |` 開頭的列,所以 `_n` 是 171,決策表實際只有 60 列,連號比對必紅。
- 斷言二:要求 D-4 主樣式是 `\bflatMapLatest\b|\?\.cancel\(\)`,實際是四個或。
- 這個函式不在 r2 補修的 diff 裡,修後仍是 2 條斷言紅。
- 推送前的全套閘會被它擋下。

歸因:有證據的原有漏查,不是這次補修造成。
- 修後命令:`python3.14 scripts/test_lumos.py -k kt_catalog_evidence_patterns`(repo 根,commit 594f97e),結果 `9 passed, 2 failed`。
- 修前命令:在我的副本把 `checks-catalog.md` 換成 8cd6d3c 的版本,再跑同一條指令,結果同樣 `2 failed`,失敗的是同兩條。

## 2. 單獨一行的 `// BAD` 會跳過「同一行就有程式的 @ 註記行」,標到錯的行
severity: minor
blocking: 否
引句:「nxt = next((k for k in range(no, len(raw)) if code[k].strip() and not code[k].lstrip().startswith("@")), None)」
file: `configs/ast-grep/kotlin-android/check.py` 的 `_bad_lines`
失敗場景:
- 輸入檔(編號為行號):`1 // BAD`、`2 @Composable fun A(vm: Vm = viewModel()) { }`、`3 val z = 1`。
- 預期:標到第 2 行。
- 修後:走到上引那行,整行 `@Composable fun …` 被當純註記行跳過,回 `(3,'val z = 1')`。
- 後果:要驗的片段在第 2 行時,「規則」改由會誤報「不在 // BAD 行」。片段碰巧也在第 3 行時會錯放行。`--sg` 起訖行檢查也用同一個行號。
- 目前真型錄 5 條「規則」改由沒踩到,所以只算 minor。

歸因:有證據的修復回歸。
- 命令:同一份輸入呼叫 `_bad_lines`。
- 修前(8cd6d3c)回 `[(2, '@Composable fun A(...) { }')]`,正確。
- 修後(594f97e)回 `[(3, 'val z = 1')]`。

## 3. `_fence_body` 改用 keep_fenced 後,圍欄沒關時檔尾那一行被吃掉
severity: minor
blocking: 否
引句:「outside = {no - 1 for no, _ln in _visible_lines(lines)}」
file: `configs/ast-grep/kotlin-android/check.py` 的 `_visible_lines`,其中 `hidden.update({a, end} if keep_fenced else …)`
失敗場景:
- 範本檔某個「### 壞寫法:API-1」小節的圍欄沒關,最後一行是程式。例如 `"## T2 x\n### 壞寫法:API-1 y\n```kotlin\nval out = query.flatMapConcat { search(it) }"`。
- `end = len(lines)-1` 把檔尾那行當成圍欄標記行丟掉,小節內文回空字串,「範本」改由誤報「不在範本」。
- 該檔另一個說明寫「同 scripts/lumos 的 keep_fenced」,但實際不同:scripts/lumos 的同一輸入保留第 4 行 `y`,check.py 把它吃掉。
- 真範本檔圍欄都有關,實際沒踩到,所以只算 minor。

歸因:有證據的修復回歸。
- 命令:`_fence_body(t,"T2","API-1")`,t 是上面那份輸入。
- 修前(8cd6d3c)回 `'val out = query.flatMapConcat { search(it) }'`。
- 修後(594f97e)回 `''`。

## 4. `_bad_lines` 的 `raw`(splitlines)與 `code`(split("\n"))行數不一致
severity: minor
blocking: 否
引句:「raw = text.splitlines()」
file: `configs/ast-grep/kotlin-android/check.py` 的 `_bad_lines`
失敗場景:
- 壞例檔含 `\x0c` 或 U+2028。
- 輸入:`val a = 1\x0c\nfoo() // BAD\nbar()\n`。
- `raw` 多切一行,第 3 行才有 `// BAD`,`code[2]` 卻是 `bar()`,回 `(3,'bar()')`。
- 標記在 U+2028 字串之後時,`code[no-1]` 為空,標記被靜默丟掉,「規則」改由報假紅。
- 現有壞例樣本沒有這類字元。

歸因:未判定。
- 修前也用 `splitlines`,行號本來就對不上 ast-grep。
- 修前同輸入回 `(3,'foo()')`,內容碰巧對、行號仍錯。
- 修後內容也錯。

## 5. `// BAD` 標記在原始行上比對,字串或註解裡的 `// BAD` 也算
severity: minor
blocking: 否
引句:「if not _BAD_MARK_RE.search(ln):」
file: `configs/ast-grep/kotlin-android/check.py` 的 `_bad_lines`
失敗場景:
- 輸入:`val s = "// BAD"`。
- docstring 寫「去註解用 Kotlin 剝法(字串裡的 // 不算註解)」,但標記偵測在 `raw` 上。字串、raw string 內的 `// BAD`、`/* // BAD */` 都被當成標記。
- 實測回 `(1,'val s = ""')`。

歸因:有證據的原有漏查。
- 修前同輸入回 `(1,'val s = "')`,一樣誤認。

## 三問回答

**①原問題的修復效果。**
- `// BADGE` 不算、`//BAD` 算、`BAD-NEXT` 併續行、字串裡的 `//` 不截斷、非 UTF-8 回問題而不崩:我用 `_bad_lines` 跑暫存檔,行為與測試描述一致。輸入是 `p1.py` 的各檔,出處是 diff 的 `_bad_lines`。
- 這些測試靠 `_bad_lines` 單元。
- `--sg` 起訖行涵蓋的新案例沒跑成,因為本機沒有 ast-grep(`which sg ast-grep` 皆無)。
- 該項判定:未判定。
- `-k kt_catalog` 結果是 302 passed、2 failed,失敗的 2 條就是 finding 1。
- 兩組守衛測試(S7 改壞、`_reach_route_guards`)我沒有做逐道改壞實驗。
- `-k kt_situation` 與 `-k kotlin_rulepack` 在背景跑,收尾時還沒回結果,未判定。

**②修補處的正常、錯誤與相鄰路徑。**
- `dt_evidence_parse` 改用 `_snippets`:與舊式 findall 加 replace 等價。
- `_norm_colon` 換成 `_norm`:`_norm` 多做全形括號轉換,對歸屬、理由與標題格無影響。
- `_parts_in_order` 對「只有 … 或空白」回 False:已確認。
- 〈叫不出的壞寫法〉重複列、理由裡引用的檢查標題:我機械核對,111 列的「犯了 X-n「…」」引句全在對應主表列文字裡,沒有不符。
- 新發現:finding 2 與 3 是修補引入的退步;finding 4、5 偏邊角。

**③新發現同一案例的前後結果。** 見各 finding 的歸因行。

**未驗範圍。**
- `--sg` 完整模式。
- API 歸屬表的撞名與停用字騙過案例:`last` 的「同名異義:」前綴可讓任何代碼審名稱略過「片段寫到它」的檢查,屬設計,沒找到實際被濫用的列。
- 兩個 pitfalls 表態(na / satisfied)我沒看出答錯。
- 圖譜固定席:hook 未附節點(鏡頭超時),我沒讀 `lens-r2.txt`,未逐條判。
- 後端卡 be-api-compat、be-authz:本案是離線型錄自檢,沒有對外 API 或授權端點,不適用。

總結:最高等級 major,共 5 條
