severity: minor

## 1. 範本圍欄新守衛只用寬鬆讀法判斷,把嚴格讀法下關得好好的檔也報成「沒關的圍欄」
severity: minor
blocking: 否
引句:「+    if _fence_regions(env["templates"].splitlines(), False)[1]:」
file: `configs/ast-grep/kotlin-android/check.py:1329`(守衛),`configs/ast-grep/kotlin-android/check.py:1447`(`_visible_lines` 先嚴格讀,嚴格讀沒問題就不退回寬鬆)
具體失敗場景:範本小節裡有一個圍欄,圍欄內文中途有一行 ```` ```kotlin ````(帶語言標記的行),最後用單獨的 ```` ``` ```` 關上。
- 嚴格讀法(`_visible_lines` 實際採用的):區段 `[(2,6)]`,沒有未關圍欄。`_fence_body` 取出 `'val a = 1\n```kotlin\nval b = 2'`,內文正確。
- 寬鬆讀法:把中途那行當成收尾,於是 `[(2,4),(6,None)]`,判成「還有圍欄開著」。
- 守衛只問寬鬆讀法,所以這份檔會在 `_template_route_problems` 被報「範本檔有沒關的圍欄」。
- 錯成什麼:範本背書被擋掉,理由卻是假的。
- 修前沒有這道守衛,這條路徑是照正確內文比對。
- 現有測試只造「真的沒關」的檔(`leak`)。把 `False` 改成 `True` 測試照樣紅,所以測試分不出對錯。
- 註解寫的意圖是「寬鬆讀法也關不上」,也就是嚴格讀法沒關、寬鬆讀法也沒關才報。程式沒有先判嚴格讀法。
- 我在 `/tmp` 用 importlib 載入 check.py 重現,時間點是這一輪派工當下的修後版本。
歸因:有證據的修復回歸。修前沒有這道守衛(`git show 6d5394398c30d25756a063be468e8a9ef3fb24eb:configs/ast-grep/kotlin-android/check.py` 沒有 `_fence_regions(env["templates"]`)。修後同一份輸入:`_fence_body` 回正確內文,`_fence_regions(…, False)[1]` 為 True,範本背書被擋。

## 2. 註記讀法對 `->` 與「名稱後有空白再接括號」判錯
severity: minor
blocking: 否
引句:「+            depth += (c == op) - (c == cl)」
file: `configs/ast-grep/kotlin-android/check.py:1125`(`_balanced_end`),`configs/ast-grep/kotlin-android/check.py:1138`(`_one_annotation_end` 名稱後直接接括號)
具體失敗場景:
- `// BAD\n@Foo<(Int) -> Unit>\nfun x() { bad() }`:`->` 的 `>` 被當成 `<` 的收尾,深度提早歸零,剩下的 ` Unit>` 讓 `_annotation_end` 回 `i`。標記被綁到註記行 `@Foo<(Int) -> Unit>`,不是 `fun x()`。
- `// BAD\n@Foo (x)\nfun x() { bad() }`:名稱後有空白,`(` 不被讀成參數,同樣綁到 `@Foo (x)`。
- 錯成什麼:`// BAD` 標到註記行,規則報在函式行,起訖行對不上時型錄自檢報假問題。方向是偏安全(多報,不漏報)。
- 新增的測試沒有 `->`,也沒有空白接括號的案例。
- 同一個測試把 `_balanced_end` 改成跨種類計數也不會紅:測試裡的括號都是同一種配對。
歸因:有證據的原有漏查。我用 `_bad_lines` 兩版對同一檔跑:修前(`_ANNOTATION_ONLY_RE`)與修後,`@Foo<(Int) -> Unit>` 都綁到第 2 行。`@Foo (x)` 兩版也都綁到第 2 行。修後沒有變壞,只是新註解宣稱的「任意層 <…>」沒涵蓋 `->`。

## 已驗主張與證據
三個問題的回答:
1. 原問題修復效果:以下輸入修後都正確跳過註記、標到 `fun x()`(其餘輸入我造了就跑,沒有挑)。
   - 巢狀 `<A, Map<B, C>>`
   - 字元常值 `'('`、`')'`、`'<'`
   - 多註記同行 `@A @B`
   - 跨行參數
   - `@field:Foo`、`@get:Bar(1)`
   - 註記後接 `/* */`
   - 註記後接 `// 註`
   - `@[A(1) B]`
   - 字串、原始字串裡含 `(`
   - `@Foo<*>`、`@Foo<out Bar>`
   - `(a > b)`、`(a < b)`
   - 檔尾 `@Foo` 沒換行(回空,不崩)
   - 括號到檔尾沒關 `@Foo(` 標在該行
2. 相鄰路徑:
   - 同一行 `@A fun x()` 與 `@Foo(1) val x = bad()` 維持標在該行。
   - CRLF 檔經 `read_text` 轉成 `\n`,`_bad_lines` 兩版結果一致(第 3 行),沒有回歸。我只對 `\n` 切的文字測過,直接餵含 `\r` 的字串給 `_bad_lines_in` 沒有走過這條路徑。
3. 新發現的同案例修前修後:finding 1 修前沒有守衛(照內文比對),修後誤報。finding 2 修前修後同樣錯。
- `t_kt_catalog_evidence_patterns` 11 passed。
- 未驗範圍:沒有在副本改壞跑測試(repo 不許改、也沒有副本版 test_lumos.py);finding 2 的「測試改壞照綠」只是從測試輸入推論,未實際翻紅。
- 暫存目錄已刪。派工詞指的鎖檔 `.warming` 我讀不到內容(`cat` 無輸出),沒有動它。

總結:最高等級 minor,共 2 條
