severity: minor

我沒有找到會讓照文件做的人做錯、或讓測試與推送擋下的洞,只有一條範圍很窄的原有漏查。

1. 帶 use-site 目標的方括號註記(`@get:[A B]`)不被當成註記跳過
severity: minor
blocking: 否
引句:「註記照結構逐字元讀,`@名稱` 後面可接任意層 `<…>`、`(…)`、`@[…]`,參數可跨行,括號到檔尾沒關就不當註記」
file: `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py:1138-1160`(`_one_annotation_end` 只在名稱後試 `<` 與 `(`,沒有 `[`)
具體失敗場景:接手者照計劃寫 `// BAD` 單獨一行,下一行是 `@get:[Inject Named("x")]`,再下一行才是 `fun z()`。`@get:[…]` 是 Kotlin 合法的多註記寫法。自檢把標記綁在註記那一行,而不是 `fun z()`。這時片段寫在函式那一行,會被報成「片段不在 // BAD 行」。這是誤報,不會靜默放行。計劃寫的是「不列舉寫法、照結構讀」,讀者會以為這種寫法也跳過。
重現:`python3.14 -c "import check as kp;lm,_=kp.load_lumos();print(kp._bad_lines_in(lm,'// BAD\n@get:[A B]\nfun z() = 3\n'))"` 修後輸出 `[(2, '@get:[A B]')]`。同樣輸入拿 `@[A B]` 則輸出 `[(3, 'fun z() = 3')]`。
修前版本:修前沒有 `_bad_lines_in`,我直接呼叫 `_bad_lines`(同一支 `// BAD` 解析)比對。修前的整行註記正規式 `@[\w.:]+(\([^()]*\))?` 也吃不了 `[`,所以結果相同。
歸因:有證據的原有漏查。真實壞例樣本沒有這種寫法,見下面 preserve。

**三問**
1. 原問題的修復效果(repair):
   - G1(註記形狀):`-k bad_snippets_reach` 修後 57 全過,對得上驗證紀錄。我另用同一個解析函式跑五種形狀,都標到 `fun z() = 3`:巢狀括號 `@Foo(bar(1))`、泛型 `@Foo<A<B>>(1)`、跨行 `@Foo(\n 1)`、具名參數帶呼叫 `@Foo(x = bar())`、`@A @B`。`@Foo(` 沒關括號則標回 `@Foo(` 那一行,與計劃一致。
   - G2、G3、G4:這幾組我沒有逐案跑,只依測試全過判斷。`-k template_fence_parity` 22 過,`-k api_decision_points` 38 過,`-k kt_catalog` 320 過。
   - 修前結果:我沒有重跑修前的測試。修前只比對了 G1 的輸出,見下。
2. 修補處的正常、錯誤與相鄰路徑(preserve):
   - 修前後 `_bad_lines` 輸出比對:對真實 `samples/bad` 全部規則逐一比,536 筆標記行,0 條規則有差異。
   - `--catalog-only` 回「型錄問題 0 個」。
   - 範本圍欄沒關的檢查(`_template_route_problems`)寫法與計劃第 263 行逐句相符:嚴格讀、寬鬆讀都關不上才報,寬鬆讀關得上則照舊退讓。
   - 沒關的圍欄會讓整份範本檔的所有「範本 T<n>」改由都報問題,不分組。計劃寫的是「直接報問題」,是有意的,不算偏差。
3. 新發現的同一案例修前後:只有 finding 1。修前修後相同,都是 `@get:[A B]` 不跳過。

**其他已驗**
- 計劃「233 支壞例檔有 199 支已標」與實數一致(用 `rglob` 數出 233 支,其中 199 支含 `// BAD`)。
- Systems/kotlin規則包 改寫後的 D-4 WHY(不選、代價)讀得通。型錄 D-4 例外證據樣式 `\bflatMapConcat\b\|\bflatMapMerge\b` 與它一致。
- 〈叫不出〉表「規則」改由共 5 條,與驗證紀錄寫的 5 個相符。
- 新增的 Error Prone 依據列:`DiagnosticTestHelper` 頁面寫「at the line below a comment」,只直接支持「標註檢查它下一行」。「隔著 `@Override` 時報在方法那一行」只靠 PR #4575 裡的一個測試範例,PR 沒有把它寫成規則,屬於間接支持。我認為不到要報的程度,但接手者要引用時應知道這點。

**未驗範圍**
- `check.py --sg`:本機沒有 ast-grep,「228 條規則、起訖行涵蓋」沒驗。
- `-k kt_situation` 145、`kt_catalog_stats_consistent` 128:前者在背景跑,我結束前沒等到結果;後者沒跑。
- 修前版本的整套測試沒重跑。
- 形如 `@Foo<(Int) -> Unit>` 的函式型別泛型註記會被 `->` 的 `>` 提早配對,也不跳過。實務上極罕見,不另立 finding。

總結:最高等級 minor,共 1 條
