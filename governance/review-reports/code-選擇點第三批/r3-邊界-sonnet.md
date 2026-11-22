severity: clean

這一輪沒有找到會擋推送的問題,也沒有新的 minor。下面是已驗主張的證據與沒驗到的範圍。

## 修復效果(repair 案例)

**C-38、C-39 拿掉「立刻 await/join 排除」後,同時在跑的兄弟會命中。** 用修前(926c72056)與修後(9ebd62d60)兩版 api.yml,對我自寫的 Kotlin 樣本跑 `ast-grep scan --rule`,結果如下。

| 輸入 | 修前 | 修後 |
|---|---|---|
| `supervisorScope { launch{a()}; async{b()}.await() }` | 不命中 | 命中 |
| `supervisorScope { val a = async{f()}; val b = async{g()}.await(); a.await() }` | 不命中 | 命中 |
| `coroutineScope { launch{a()}; val r = async{b()}.await() }` | 不命中 | 命中 |
| `supervisorScope { async{a()}.await() }`(只有一支) | 不命中 | 不命中 |

另外幾個組合修後都命中,修前部分不命中,後面「已知取捨」會再提:
- 迴圈裡立刻等:`for`、`while`、`map`、`forEach`、`repeat`。
- 兩支都立刻 `.await()` 並排。
- 兩支都立刻 `.await()`,換行並排。
- 兩支之間夾註解。
- `l?.map { async }`。

**長鏈掃描時間回到正常。** 作用域裡 `launch{a()}` 後接 500 個 `.join()`,修前掃 8.12 秒,修後 0.22 秒。

**大輸入沒有新問題。**
- 作用域裡 2000 個 `val vN = async{}.await()`:修後 0.09 秒,輸出 528 位元組。
- 作用域裡 3000 個並排的 `async{}.await()`:修後 0.1 秒,輸出 60KB。
- 巢狀 150 層的 `supervisorScope`:修前修後輸出同為 1.1MB,命中集合相同。
- 60 層 `foo(async{})` 包裝:修前修後同樣命中 C-39,輸出 1335 位元組。

## 保留(preserve)案例

這些輸入修前修後結果相同:
- 只有一個子協程,不命中。
- 外層只有內層作用域的 `async`,C-38 不命中。
- `list.map { coroutineScope { async } }`,C-39 不命中。
- 只有一個 `launch` 包在另一個 `launch` 裡,不命中。
- 完整套件名 `kotlinx.coroutines.supervisorScope { launch; launch }` 不命中。這與修前一致,不是回歸;因為規則要求 `nthChild: 1` 的識別字,屬於設計取捨。

**C-40~C-47 改回正面 inside 後,命中位置與修前逐點相同。**
- 樣本共 19 個命中點,修前與修後的 (規則, 行, 欄) 清單 `cmp` 比對完全一致。
- 樣本涵蓋 `?.` 呼叫、換行接 `.firstOrNull`、行尾夾註解後換行、`.single` 屬性存取、`::single` 函式參照、`?.let { it.toIntOrNull() }`、尾隨 lambda、同一行多個方法名鏈接、裸呼叫 `singleOrNull()`、完整套件名 `kotlin.collections.single(l)`、頂層與類別屬性、當引數 `foo(l.single())`。
- 光是屬性存取 `.single`、`::single`、沒有呼叫的 `l.firstOrNull` 這幾種「不是呼叫」的寫法,修前修後都不命中。
- C-40 的規則本文與 C-19(inside navigation_expression inside call_expression)形狀一致,C-19 是第一版同形規則。

## 形狀測試 `t_choice_rule_shape_batch3`

**判準在邊界形狀上沒有誤判。**
- C-40~C-47 的 inside 深度是 2,判成不用包;C-38、C-39 因為有 `has` 與 `precedes`,判成要包;C-48~C-53 判成要包,C-54、C-55 判成不用包。
- 以上全部實跑通過(20 passed)。
- `_cb3_rule_shape` 靠逐行縮排與字串比對,我沒有找到會被 `has-co:`、`matches: has-co` 騙到的例子。流程式 `inside: {…, inside: {…}}` 的深度用 `body.count("inside:")` 計入,也判得對。

**其他相關測試通過。**
- `-k choice_samples_batch3`:43 passed。
- `-k choice_scope_rule_output`(S9):14 passed。

## 已知取捨(不算 finding)

兩者都是作者已列入〈天花板〉的代價。

- **每支都立刻 await/join 的作用域**:修後照樣命中 C-38 或 C-39。換寫法必然等價,實務上落成「等價」放行,不影響正確性。
- **C-40~C-47 改回正面寫**:巢狀輸出量變大。我的 200 層 `firstOrNull` 單檔整包規則掃描輸出,從修前 0.79MB 變成 1.6MB,比不上作者說的 24MB 量級,同方向。

## 未驗範圍

- 沒有跑全套測試。
- 沒有對真實 Android 專案的大檔實跑。
- 沒有拿掉 C-38 雙重否定、或把 C-40 包回雙重否定,實測翻紅釘。只確認了判準函式對現行檔案的判定,沒有實際「變異後測試紅」的證據。
- 圖譜鏡頭:本輪沒有附固定席筆記,依派工詞不補算。

引句:「# 的照算:不看先後的排除會把同時跑的兄弟一起排掉、又讓長方法鏈的掃描時間三次方成長,不收(計劃〈天花板〉第 3 條;代碼審 r2 c1 b1 g1 r1)」

總結:最高嚴重度 clean,blocking 共 0 條
