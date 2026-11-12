severity: minor

LUMOS-LENS 沒附固定席節點,我也沒讀 `lens-r4.txt`,所以圖譜鏡頭沒有逐條答。

1. 連續多行註記的跳過沒有測試把關
severity: minor
blocking: 否
引句:「        end = _annotation_end(code, nxt)」
file: `configs/ast-grep/kotlin-android/check.py:1129`(`_next_statement` 的 while 迴圈,修後行號)
失敗場景:在修後版本的副本裡,把 `_next_statement` 的迴圈改成「最多只跳過一段註記」。`-k bad_snippets_reach` 仍是 57 passed、`-k kt_catalog` 仍是 320 passed。同一個改壞跑 `// BAD\n@A\n@B(1)\nfun z() = 3`,結果是 `[(3, '@B(1)')]`,應該是 `[(4, 'fun z() = 3')]`。新增的 `shapes` 案例每個都只有一行註記,既有的「跳過註記」案例也只有一行。舊版「整行只有註記就跳過」是逐行判斷,連續多行註記本來就能過。這個「跳過一段後繼續找」的行為,修前修後都沒有案例保護。我沒等到 `-k kt_situation` 跑完。
歸因:未判定。修前版本沒有 `_bad_lines_in`,所以我沒法在修前跑出同一個改壞。
查證:修後版本直接跑 `_bad_lines_in` 得到 `(4, 'fun z() = 3')`,改壞後得到 `(3, '@B(1)')`。

三問的答案

1. 原問題的修復效果:我在修後版本直接呼叫 `_bad_lines_in`,逐案確認 G1 各形狀都標到修飾的語句,行號都是語句那一行。
   - 巢狀括號 `@Foo(a = bar(1))`、泛型 `@Foo<List<Int>>`、一行兩個註記、`@[A B(1)]`、參數跨多行、use-site `@get:...` 加 `@set:...`、字串或字元字面值裡的括號都過。
   - 括號沒關(`@Foo(` 後面沒有 `)`)回到標那一行,符合設計。
   - 修前版本沒有 `_bad_lines_in`,所以這幾個形狀沒有修前逐案輸出,只能靠程式推:舊的 `_ANNOTATION_ONLY_RE` 只認單層括號,巢狀括號不會被跳過。
   - 另有一個小邊角:`@Foo<(Int) -> Unit>` 裡的 `->` 會被當成 `>`,結果標到註記那一行。Kotlin 註記類別不能有型別參數,所以我沒列成 finding。
2. 相鄰路徑:
   - `-k bad_snippets_reach` 是 57 passed,`-k template_fence` 是 22 passed,`-k kt_catalog` 對修後版本的改壞副本是 320 passed。
   - 真型錄 `check.py --catalog-only` 修後與修前都是 0 個問題。
   - 行數對不上時,`_bad_lines_in` 回傳的問題文字拼回去,和修前完全一樣。
   - `_unpipe` 抽出後只有 `_snippets` 與 `_unreach_table` 兩處呼叫,還原邏輯只有一個出口。
   - 範本檔沒關的圍欄檢查位在 `_template_route_problems`,其他路徑不受影響。這個檢查是整份範本檔,不是只看該組,所以任何一組的圍欄沒關,每一條「範本」改由都會報同一個問題。這符合新測試與注釋的意圖。
   - 效能:`// BAD` 加沒關的 `@Foo(` 重複 N 次,N=500、1000、2000 分別用 0.06、0.22、0.88 秒,是平方成長但在實際壞例檔的規模下可忽略。
3. 新發現案例的修前修後結果:只有 finding 1 一個案例。修前沒有對應函式,所以修前結果是未判定。

未驗範圍:`-k kt_situation` 在我的改壞副本上沒等到結果;`--sg` 完整掃描模式沒跑;筆記與驗證紀錄的文字沒逐字對照程式。

總結:最高等級 minor,共 1 條
