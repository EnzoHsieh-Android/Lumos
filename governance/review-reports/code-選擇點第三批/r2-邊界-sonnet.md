severity: minor

## b1 C-38/C-39 的「建立後立刻 await/join 不算子協程」會把仍在並行的兄弟協程一起排掉
severity: minor
blocking: 否

引句:「建立後同一個運算式就 .await()/.join() 的不算(做完才開下一支,兩種作用域必然等價」

- 輸入:`supervisorScope { launch { g() }; async { f() }.await() }`。`launch { g() }` 沒有等,和 `async { f() }` 同時在跑。`g` 若失敗,`coroutineScope` 會取消 `f` 並讓整個作用域失敗,`supervisorScope` 不會。兩種作用域在這裡不等價,所以「必然等價」的前提不成立。
- 走到的行:`child-co` 的 `not: inside: navigation_expression(.await|.join) inside call_expression`。`async { f() }.await()` 被剔除後,作用域只剩一個子協程,`many-co` 的配對湊不成,整條不命中。
- 其他實跑:
  - `coroutineScope { val d = async { g() }; val e = async { f() }.await(); d.await() }` 不命中 C-39。
  - `supervisorScope { val d = async { g() }; launch { f() }.join() }` 不命中 C-38。
  - `supervisorScope { launch { a() }; list.forEach { launch { f() }.join() } }` 不命中 C-38。
- 對照:`supervisorScope { launch { a() }.join(); launch { b() }; launch { c() } }` 仍命中(剩兩個沒等的),行為與預期一致。
- 同一案例:
  - claim:有未等待的兄弟協程時,仍有兩個以上並行子協程,應命中。
  - input:上述四個輸入,用 `ast-grep scan --config configs/ast-grep/kotlin-choice/sgconfig.yml` 掃。
  - expected:命中,因為子協程並行。
  - case_source:`r2-behavior-cases.md` 的 G2 repair 案例是我補的反例,材料沒有。
  - before(763081c0d):四個都命中(C-39 一個、C-38 三個)。
  - after(926c72056):四個都不命中。
  - comparison:修前命中、修後消失。
- 歸因:有證據的修復回歸。這條排除是 r2 新加的,兩版實跑結果不同。
- 邊界說明:計劃〈用詞〉明文寫「建立後同一個運算式就 await/join 的也不算」,所以行為符合定義。問題在定義的理由(必然等價)只在其他子協程也都已做完時才成立,計劃〈天花板〉也沒有記這個漏判。嚴重度因此只給 minor,規則本身是 hint。

## 已驗主張與未驗範圍(零 blocker/major)
- C-48 零值寫法。在 `extraBufferCapacity` 搭配 `onBufferOverflow = DROP_OLDEST` 下,以下寫法都被正確排除(不命中):`0`、`0_0`、`00`、`0x0`、`0X00`、`0x0_0`、`0b0`、`0B0`、`0L`、`0x0L`、`0b0L`、`0_0L`、`0x00L`、`-0`、`+0`、`- 0`、`-0x0`。
  - 非零寫法照常命中:`0xA`、`0xFF`、`0x0F`、`0b01`、`007`、`1_0`,以及 `n - n`。
  - 引數順序顛倒、尾端逗號加行註解、多行寫法,判定都正確。
  - `(0)` 仍命中,屬計劃〈天花板〉已記的上限。
- C-48 的 SUSPEND 判斷。裸 `SUSPEND`、`BufferOverflow.SUSPEND`、完整套件名、換行接 `.SUSPEND`、`onBufferOverflow = SUSPEND, extraBufferCapacity = 5` 都照常命中。
  - 在 `DROP_OLDEST` 之外,`overflowFn()`、`MySUSPEND`、`Other.XSUSPEND` 被排除(不命中)。`SUSPEND.also {}` 這類自訂寫法也被排除,極冷門,不另報。
- 樣本檔新加的 HIT/MISS 標記:`fe`(SUSPEND)、`ff` 到 `fl`(各種零)、C-38/C-39 新增樣本(三個 MISS、兩個 HIT),與實跑結果一致。
- 修前對照:`(0)` 與 `0x0` 等零寫法在修前版因 `^0$` 只認十進位 `0` 而漏掉,這是 G1 repair 的行為證據。修前版沒有逐個重跑,是只憑 `^0$` regex 推斷。
- 未驗範圍:
  - `scripts/test_lumos.py -k choice_samples_batch3` 沒跑成,我在要跑測試前就把臨時工作樹移除了。
  - 圖譜鏡頭沒有固定席筆記,未答。
  - `scripts/lumos` 的 `_choice_err_start` 與 `_CHOICE_CALL_NAME_RE` 重構、S9 巢狀合成輸入、`_CB3_S7_PIN` 等測試端修補沒有實跑。
  - 冪等性沒有另測。

三問回答:
- ①原問題修復效果:C-48 零值(`0x0`、`0b0`、`0L`、`±0`)排除與顯式 SUSPEND 仍命中都有行為證據;C-38/39 的「單一協程立刻 await 不命中」成立,但連帶造成 b1。
- ②相鄰路徑:C-48 的正常、錯誤與相鄰寫法都成立;C-38/39 在多個兄弟並行時不成立(b1)。
- ③新發現同一案例的修前、修後:b1 修前命中、修後不命中。

總結:最高嚴重度 minor,blocking 共 0 條
