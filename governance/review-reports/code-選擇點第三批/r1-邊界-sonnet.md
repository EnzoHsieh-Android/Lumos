severity: minor

整體判斷:我用 ast-grep 對 C-38 到 C-55 各寫了一批界線樣本,並用 `lumos choice-points` 在臨時 repo 實跑。沒有找到會讓規則做出錯誤行為的洞,只有三條 minor。測試 `choice_samples_batch3` 與 `choice_points_batch3` 在本機全綠,型錄 `check.py --catalog-only` 報 0 個問題。

**實跑確認沒問題的界線**
- 作用域兩列:
  - 單一或零個子協程、`launch` 帶接收者(`scope.launch`、`Foo.launch`)、`kotlinx.coroutines.supervisorScope`、`x.supervisorScope`,都照計劃不命中。
  - 同陳述兩個、兩行各一個、`for` 無大括號本體、`?.forEach`、多行 `ids.map { id -> async {…} }.awaitAll()`、`launch` 之間夾註解,都命中。
  - `mapNotNull`、`do-while`、`.also { launch }` 不命中,與〈天花板〉一致。
- 效能:單一作用域裡 3000 個 `launch`、3000 個其他陳述加一個 `launch`、1500 個並排作用域,都在 0.15 秒內。巢狀 60 層和巢狀迴圈 40 層也沒有輸出爆量。
- C-54/55:
  - 接收者是 `!!`、`as`、`?.` 鏈、字串字面值、多行,都命中,壞法剛好刪到呼叫結尾。
  - `Result`、`foo.Result`、`kotlin.Result`、`Result ` 後帶空白都被排除。
  - `fooResult.retry()` 和 `WorkResult.retry()` 照命中。
  - `flow.retry(3).retry(2)` 與換行寫法都有挑出,換行寫法的 `old` 含兩行。
- 其他:C-40 到 C-47 的屬性存取、`::single` 函式參照、`users.single.foo()` 都不命中。C-53 在 `finally` 內不命中,其他位置命中。C-50 的 `.await()`、`.join()`、`?.await()` 都排除。
- `_choice_also` 的運算元起始分支:`supervisorScope` 與 `mapLatest` 的 import 補法正確。既有的運算元起始列只有 C-18,沒有帶 import 的,第一版行為不受影響。

## b1 作用域兩列的錨點在識別字那一行,新增第二個子協程的改動不會被問到
severity: minor
blocking: 否

引句:「命中 call_expression 第一個子節點的 supervisorScope/coroutineScope 識別字」

file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`,C-38、C-39 規則(patch 第 48 到 108 行)。

失敗場景:
- 輸入:base 版 `supervisorScope {` 裡只有一個 `launch { a() }`,這次改動只在大括號裡新增一行 `launch { b() }`。
- 走到哪:規則命中的是第一行的識別字。改動行不含錨點,所以 C-38 不入選。
- 結果:作用域從一個子協程變成兩個、業務問題剛好成立的那一刻,沒有被詰問。
- 這型〈天花板〉沒列。

重現(臨時 repo,base 與 feat 如上):
```
lumos choice-points --repo <repo> --diff main..feat
→ 統計:改到的行 1、有選擇點的行 0、有壞法的行 0
```
這是錨點選擇的取捨,只會漏判。建議在〈天花板〉補一條,或接受為已知取捨。

## b2 C-48 的排除條件在兩個方向上不準
severity: minor
blocking: 否

引句:「帶 onBufferOverflow、又沒有值不是 0 的 extraBufferCapacity」

引句:「not: {has: {kind: integer_literal, nthChild: {position: 1, reverse: true}, regex: '^0$'}}」

file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`,C-48 規則(patch 第 271 到 303 行)。

失敗場景有兩個:
- 排除過頭:`MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.SUSPEND)`(顯式 SUSPEND,沒有 `extraBufferCapacity`)不入選。換成 `replay = 0` 並不會丟例外,這個壞法本來該被問。
- 排除不足:`extraBufferCapacity = 0x0`、`-0`、`(0)` 加 `onBufferOverflow = BufferOverflow.DROP_OLDEST`,正規式 `^0$` 認不出這些零,仍然命中。`replay = 0` 的壞法在建構時就丟例外,落成「跑不出結果」要人放行。

重現:
- ast-grep 對 `MutableSharedFlow<Int>(replay = 1, extraBufferCapacity = 0x0, onBufferOverflow = BufferOverflow.DROP_OLDEST)` 命中 C-48,應排除。
- 對 `MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.SUSPEND)` 不命中,應命中。

兩者都很罕見,屬於覆蓋精度。

## b3 完整套件名與逐一 import 的裸名稱,C-50 到 C-53 都漏判,〈天花板〉沒列
severity: minor
blocking: 否

引句:「命中接在 BufferOverflow 後面那一段 navigation_suffix」

引句:「命中接在 CoroutineStart 後面那一段 navigation_suffix」

file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`,C-50 到 C-53 規則(patch 第 327 到 410 行)。〈天花板〉第 3 條只列了作用域與 `MutableSharedFlow` 的完整套件名漏判。

實跑確認以下都不命中:
- `kotlinx.coroutines.channels.BufferOverflow.DROP_OLDEST`
- `kotlinx.coroutines.CoroutineStart.LAZY`
- `withContext(kotlinx.coroutines.NonCancellable)`
- 逐一 `import ...BufferOverflow.DROP_OLDEST` 或 `...CoroutineStart.LAZY` 之後直接寫的裸 `DROP_OLDEST`、`LAZY`

這幾種寫法漏判後沒有任何提示。建議在〈天花板〉第 3 條補上這幾種寫法。

總結:最高嚴重度 minor,blocking 共 0 條
