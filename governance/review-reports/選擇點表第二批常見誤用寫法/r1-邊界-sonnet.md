severity: major

以下為「邊界可執行」鏡頭的發現。ast-grep 0.51.2 的實驗都在 `/tmp/lumos-seat-work/選擇點表第二批常見誤用寫法/邊界-sonnet/x/`,沒有寫任何檔進 repo。

1. 多行 `?.` 鏈的壞法一律是語法錯誤
   - 位置:範圍 3、`_choice_edits` 安全呼叫符分支;S2。
   - 問題:設計只把那兩個字元換成 `!!.`,沒處理 `?.` 在行首的寫法。Kotlin 常見的鏈式換行 `foo.bar⏎    ?.baz` 會變成 `foo.bar⏎    !!.baz`。後置 `!!` 不能接在換行之後,結果是語法錯誤。這種行的錨點正好落在續行上,是會被選中的行。
   - 重現:`val h = foo.bar⏎    !!.baz⏎    ?.qux()` 用 ast-grep 解析得到 1 個 ERROR 節點。原寫法和把 `!!` 放行尾的寫法都是 0 個 ERROR。
   - 後果:這種行的壞法全部「跑不出結果」,會灌高 C-33 的跑不出結果比例,觸發 RETIRE-IF 的「超過一半就拿掉」。設計沒有把 `!!` 改放到前一行尾的處理。
   - 查證:`m1.kt` 與 `m2.kt`;kotlinc 本機沒裝,所以編譯器行為只能靠語法樹證明(⚠)。
   - 引句:「只把那兩個位元組換成 `!!.`」
   - 引句:「只把挑中的那一個 `?.` 換成 `!!.`、其餘不動」
severity: major
   - blocking: 是,壞法對常見排版必然產生不可編譯結果,而且設計沒有處理這條路徑。

2. `?:` 的規則若照字面只寫 `elvis_expression`,壞法一個都產不出來
   - 位置:範圍 2 的 `nul.yml`;S1。
   - 問題:設計寫的是規則 `elvis_expression`,沒說要不要用 `$A ?: $B` 這種帶後設變數的樣式。我實測 `kind: elvis_expression` 的命中沒有 `metaVariables`。
   - 後果:`_choice_edits` 組 `$A!!` 時 `mv["A"]` 不存在,走到 `val is None` 就回 None(`scripts/lumos:77252` 附近)。`_choice_excluded` 的「運算元有 null 字面值」也因為 `ops` 為空而永遠不排除。
   - 對照:`$A ?: $B` 樣式能帶出 A、B,巢狀 `a ?: b ?: c` 會命中兩個節點,多行 `x⏎ ?: y` 也命中。
   - 判準:這是設計沒講清楚的地方,實作者照字面做就必然紅。
   - 引句:「`nul.yml`(`elvis_expression`;`?.` 的 navigation_suffix)」
   - 查證:`k.yml` 對 `el.kt` 掃描,`metaVariables` 全是 None。
severity: major
   - blocking: 是,規則寫法歧義會讓 S1 無法落地,需要在 spec 裡寫死用樣式。

3. 錨點在第一行,改到續行的 `?:`、引數清單時看不到
   - 位置:用詞〈新錨點引數〉、範圍 3 的 `_choice_anchor`、「運算元起始」不改。
   - 問題:選行只看 `line_of(anchor) in want`(`scripts/lumos:77454`)。
     - `?:` 的錨點是整個節點開頭,也就是 A 所在行。常見寫法是 `val x = foo⏎    ?: defaultValue`,改動只動 `?: defaultValue` 那行時,錨點行沒被改到,不產壞法。
     - 引數錨點是左括號所在行。`remember(⏎    items,⏎    sortOrder,⏎) {`(三個以上 key 加尾逗號的寫法)中,新增或改動 key 只動中間行,錨點行沒變,整列失效。這剛好是這兩列要守的「改 key」場景。
   - 對照:第一版的二元運算用運算子位置當錨點,沒有這個問題。設計換了 NUL 與引數錨點,卻沒說明多行改動的處理。
   - 引句:「錨點行是左括號所在行」
   - 引句:「照第一版回節點開頭,不改運算子正規式 `_CHOICE_OP_RE`」
severity: major
   - blocking: 是,多行的常見寫法會靜默漏守,而且設計沒有交代範圍。

4. `LaunchedEffect` 的排除條件太窄,具名 `block =` 與空括號會產出壞掉的壞法
   - 位置:範圍 2 的 `compose.yml`;S4。
   - 問題:排除只列「只有一個引數而且是 Unit、true、false」。實測下面兩種仍然命中:
     - `LaunchedEffect(key1 = a, block = { go() })`,整段 value_arguments 被覆蓋成 `(Unit)`,具名 lambda 被刪掉,不可編譯。
     - `LaunchedEffect()`,空括號。
   - 對照:`remember` 有「必須帶尾隨 lambda」限制,`LaunchedEffect` 沒有。
   - 引句:「引數只有一個而且是 `Unit`、`true`、`false` 字面值時不命中」
   - 查證:`r2.yml` 對 `c.kt`,第 10、11 行都命中。
severity: minor
   - blocking: 否,這類寫法少見,後果只是落成跑不出結果。

5. 「單一記號」沒有定義,`$A` 要不要包括號可以有兩種讀法
   - 位置:範圍 3 第二項;S1。
   - 問題:`a.b()`、`x?.y` 算不算單一記號沒說。既有 `_choice_atomic` 允許識別字加點、`?`、`!` 與呼叫,`a.b()!!` 本身合法。嚴格讀字面則會多包成 `(a.b())!!`。
   - 後果:實作者與測試作者可能各選一種,S1 的「應寫成 `($A)!!`」不好驗。
   - 另外:`x as? Foo` 之類帶空白的運算元必須包括號,否則變成 `x as? Foo!!`。這條可以落成明確的條款。
   - 引句:「不是單一記號時先包成 `($A)` 再接 `!!`」
severity: minor
   - blocking: 否,不影響行為正確性,只是測試期望不明確。

6. 同名自訂函式與 import 別名沒有處理
   - 位置:實務隱患。
   - 問題:語法樹分不出下面這些情形,而實務隱患只講了 `.let`→`also` 與 `$A!!` 的型別問題,沒提它們。
     - 專案自訂的 `fun LaunchedEffect(...)` 或 `remember`。
     - 非 Flow 的 `Foo.combine(...)`。
     - 型別是 `List` 時 `zip` 其實能編過,但語意不同。
   - 例子:`import ...combine as flowCombine` 之後 `.flowCombine` 不命中,屬於正常的漏判。
   - 後果:跑不出結果或等價存活,只是比例沒被預期。
   - 引句:「語法樹沒有型別,這兩列除了」
severity: minor
   - blocking: 否,後果由跑不出結果與放行機制承接。

7. 常數 key 的排除只列三個字面值
   - 位置:範圍 2 `compose.yml`、實務隱患「等價存活」。
   - 問題:`LaunchedEffect(null)`、`LaunchedEffect(1)`、`LaunchedEffect("tag")` 換成 `Unit` 同樣等價,卻不在排除清單。
   - 引句:「LaunchedEffect」的 key 本來就是常數時規則不命中(範圍 2),其餘靠回報上限與放行理由「等價」承接
     (此引句已避開「」,逐字為:本來就是常數時規則不命中(範圍 2),其餘靠回報上限與放行理由)
severity: minor
   - blocking: 否,實務上罕見,放行機制承接。

8. 實測確認沒問題的邊界
   - 巢狀 `a ?: b ?: c`:外層節點(A 為 `x ?: y`)排在前面,先被選中。
   - 字串樣板 `${a ?: b}` 會命中,替換有效。
   - 註解裡的 `a ?: b` 與 `x?.y` 不會命中。
   - `f()?.g()`、`x?.let { it?.y }` 的 `?.` 位置正確。
   - `remember<Int>(k) {}` 可正確命中並刪除引數。
   - `obj.remember(k) {}` 與 `this.remember` 不命中。
   - 頂層 `combine(a, b)` 不命中。
   - `LaunchedEffect(key1 = a) {}` 命中且替換有效。
   - `?.` 規則不會誤中內層呼叫的引數。

實務隱患鏡頭:
- 編不過、等價存活、換壞法、Compose 測試成本、掃描量:spec 已列。本鏡頭補上第 1、3、4 條。
- 併發與交易、金流、對外送出、不可逆:無。理由是本功能只動本機的型錄、規則與壞法產生程式,單人單機依序操作,不碰付款,不對外送資料,治理帳照舊逐筆追加。
- 守衛面:新規則會改變推送前選擇點那一道挑出的壞法。第 1 條的語法錯誤壞法與第 3 條的漏守都落在這一面。

整份 spec 已讀完,「白話」「舊否決比對」「依據來源」「回退」「天花板」各節沒有額外 finding。交叉引用的〈回退〉第 1 項、範圍 5、〈天花板〉第 1 條都存在。

最嚴重 severity:major;blocking 共 3 條(第 1、2、3 條)。
