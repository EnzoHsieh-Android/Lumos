severity: minor

三條都是漏判或偏弱的挑法,沒有會讓推送閘整張壞掉的錯。以下逐節結論:

- 範圍 3 的三處擴充(`_choice_anchor`、`_choice_api_edits`、`_choice_also`):已走過,結論是對的。
- 現有 API 規則沒有帶 `$A` 的,所以新的 `$A` 分支不會影響舊列。
- `_choice_also` 目前只有 `_choice_pick` 一個呼叫端。
- `kotlin.coroutines.EmptyCoroutineContext` 過 `_choice_atomic` 不會被加括號。
- 型錄引用的 D-3、D-4、D-7、D-8、D-9、D-11、D-15、D-16、D-17、D-26、CO-12、CO-15、CO-18、FLOW-28 都存在。
- `test-templates.md` 存在,內有 supervisorScope 範本。
- 〈範圍 7〉〈不做〉〈回退〉〈依據來源〉:已讀,無 finding。

圖譜鏡頭的兩個固定席節點:

- `Systems/kotlin規則包`:這份設計不破壞它。它只新增列、規則與樣本,沿用現有讀表與白名單。`check.py` 對 API 類別沒有「錨點必須是方法名」的限制,已讀 `_choice_row` 確認,所以作用域與 `replay` 兩種「運算元起始」的 API 列讀得進去。
- `Systems/規格閘`:這份設計不破壞它。處置鍵 (檔, 行指紋) 不動,「整個呼叫命中」的壞法身分 `old` 跨兩行,走 `_choice_identity` 現有的兩行以上流程。

## c1 replay = 1 換成 0 時,同一呼叫若帶 onBufferOverflow = DROP_* 又沒給 extraBufferCapacity,壞法一建構就丟例外
severity: minor
blocking: 否(實作者照 spec 做不會出壞系統,只是這個壞法的偵測力偏弱)
引句:「命中節點是整數字面值 `1`(或 `0`)本身,用 `inside` 限定它的外層 value_argument 名稱是 `replay`」

- 位置:範圍 2「replay 兩列」,對照 PRIOR-ART 排除 `BufferOverflow.SUSPEND → DROP_*` 的理由。
- 問題:`replay` 規則只看「整數字面值 1 在名為 replay 的引數裡」,沒排除同一個呼叫帶有非 SUSPEND 的 onBufferOverflow。
- 失敗場景:
  - 輸入是 `MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)`,這是常見的「只留最新值」寫法。
  - 規則命中 `1`,壞法是 `replay = 0`。
  - kotlinx.coroutines 在 `replay`、`extraBufferCapacity` 都是 0 且策略不是 SUSPEND 時,建構就丟 `IllegalArgumentException`。這是我依 kotlinx.coroutines 的行為判斷,沒有實跑 Kotlin。
  - 任何會建構這個 flow 的測試都會紅,壞法被判「殺掉」,作者不會被逼去補「晚到訂閱者看得到上一個值」的測試。
  - spec 自己就是為了同一個理由(只會被輕易殺掉)才排除 SUSPEND → DROP_*。
  - 一行一個壞法時,`replay = 1` 在 `onBufferOverflow = ...` 左邊,依錨點由左到右會先被挑中,把同一行的 DROP 互換擋掉。
- 佐證:用 ast-grep 實跑「整數字面值 1 且 inside value_argument 且有 simple_identifier `replay`」。`replay = 1` 與 `replay = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST` 兩行都命中,`foo(count = 1)` 與 `replay = n + 1` 不命中。
- 佐證:file: `/Users/enzo/harness/lumos-choice-batch3/skills/kotlin-idioms/checks-catalog.md:755`(D-16 的標準寫法是 `buffer(64, onBufferOverflow = BufferOverflow.DROP_OLDEST)`)

## c2 作用域規則「子協程」的判法漏掉同一陳述內多個 async 與 for/while/repeat 迴圈,跟 spec 自己「少於兩個才不命中」的宣稱不一致
severity: minor
blocking: 否(漏判,不會產出錯誤壞法)
引句:「有兩個不同的陳述各自含 `async`/`launch` 呼叫(後一個 follows 前一個)」

- 位置:範圍 2 作用域兩列的①②,對照〈用詞〉子協程與迴圈呼叫、〈天花板〉第 3 項。
- 問題:規則①要「兩個不同的陳述各自含 async/launch」,②只認 `.map`、`.forEach`、`.mapIndexed`、`.forEachIndexed`、`.flatMap` 五個迴圈呼叫。
- 失敗場景:
  - `coroutineScope { awaitAll(async { f() }, async { g() }) }` 或 `listOf(async { }, async { }).awaitAll()`:兩個 async 在同一個陳述裡,不滿足「不同陳述」,不命中。
  - `supervisorScope { for (id in ids) { launch { load(id) } } }` 或 `repeat(n) { launch { } }`:一個 launch 在 for/repeat 裡實際開出多個子協程,不在五個呼叫名單內,不命中。
  - 這些都是大括號裡直接看得到的寫法,兩種作用域在它們身上行為不同(兄弟是否連坐取消)。
  - spec 對 `map { async }` 命中而對 `for { launch }` 不命中沒有給理由。〈天花板〉第 3 項只承認「藏在別的函式裡」的漏判,沒承認這兩型。
- 佐證:用 ast-grep 實跑,`flow.retry` 類樣式能命中但規則①的「不同陳述」條件在語法上必然排除單一陳述內的兩個 async。
- 佐證:file: `/Users/enzo/harness/lumos-choice-batch3/skills/kotlin-idioms/checks-catalog.md:742`(D-3 標準寫法就是 `ids.map { id -> async { … } }.awaitAll()`,同類的 awaitAll 慣用法沒收)

## c3 retry 規則在接收者與 `.retry` 之間夾註解時整個不命中,〈範圍 2〉的「換行都命中」沒涵蓋
severity: minor
blocking: 否(漏判)
引句:「單行、換行、帶 lambda、`?.` 都命中,`$A` 取得到接收者範圍」

- 位置:範圍 2 `retry` 兩列「單行、換行、帶 lambda、`?.` 都命中」。
- 問題:樣式 `$A.retry(...)` 對「接收者、註解行、`.retry`」三段結構不命中。
- 失敗場景:
  - 輸入:
    ```
    val c = repo.items()
        // 失敗重試
        .retryWhen { c, n -> n < 2 }
    ```
  - 結果是規則沒有命中,這一行沒有 retry 選擇點,作者拿掉 retry 也不會被詰問。
  - 附帶一點:現有 `_CHOICE_GAP_SKIP_RE` 本來就能跳過註解,但這個失敗發生在 ast-grep 命中之前,`_choice_anchor` 的新分支改不了。
- 佐證:用 ast-grep 0.51.2 實跑。無註解的換行寫法 `.retryWhen {…}` 命中;同一段中間插 `// comment` 後 `retryWhen` 與 `.retry(3)` 兩種都不命中。同檔其餘寫法的實跑結果:
  - `x?.retry(3)` 命中,`A` 取得 `x`。
  - `Result.retry()` 命中,`A` 是 `Result`,所以接收者排除條件要實作,規則本身不會自己排除。
  - `flow.retry(3).retry(2)` 兩層都命中。
- 佐證:file: `/Users/enzo/harness/lumos-choice-batch3/scripts/lumos:77162`(`_CHOICE_GAP_SKIP_RE` 已有註解跳過邏輯,新規則沒用到)

總結:最高嚴重度 minor,blocking 共 0 條
