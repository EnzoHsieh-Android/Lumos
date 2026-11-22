severity: major

## b1 `replay = 1` 換成 `replay = 0` 在帶 `onBufferOverflow = DROP_*` 的寫法上建構就丟例外,殺傷力是假的
spec 段落:範圍 1/2 的 `replay` 兩列、〈不做〉與 PRIOR-ART 的排除表(`SUSPEND → DROP_*` 因容量 0 會丟例外而排除)。
severity: major
blocking: 是 判準:照這份做,最常見的 `replay = 1` 寫法會被「任何碰到建構的測試」殺掉,等於裝了一道假守衛,實作者會做出壞系統。

引句:「`BufferOverflow.SUSPEND` → `DROP_*`(容量 0 時執行就丟例外,只會被輕易殺掉)」

問題:spec 為了同一個理由排除了 `SUSPEND → DROP_*`,卻沒發現 `replay` 列有同一個洞。
失敗場景:
- 輸入是 `MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)`,這是 Android 上「像狀態的熱流」的常見寫法。
- 規則命中 `1`,壞法換成 `replay = 0`。
- 這時 replay 與 extraBufferCapacity 都是 0,但 overflow 不是 SUSPEND,建構子直接 `IllegalArgumentException`。
- 任何會建出這個流的測試都紅,判成「殺掉」,但它守的不是「畫面重建後要不要再看到上一個值」這條需求。
- 範圍 2 的 `replay` 規則只用 `inside` 限定引數名稱,沒有排除同一個呼叫帶非預設 `onBufferOverflow` 的情況。

佐證:
- 實跑 kotlinx-coroutines 1.11.0 的 jar:`MutableSharedFlow(0,0,BufferOverflow.DROP_OLDEST)` 丟 `IllegalArgumentException: replay or extraBufferCapacity must be positive with non-default onBufferOverflow strategy DROP_OLDEST`,`MutableSharedFlow(1,0,DROP_OLDEST)` 正常建構。
- file: `/Users/enzo/.gradle/caches/modules-2/files-2.1/org.jetbrains.kotlinx/kotlinx-coroutines-core-jvm/1.11.0/3d57dc678bd8d72a60e7adf0eca5c54e3f4f4b79/kotlinx-coroutines-core-jvm-1.11.0.jar`

## b2 作用域規則 ① 寫「含」,〈用詞〉寫「直接」,兩者對不上,會命中必然等價的巢狀作用域
spec 段落:範圍 2 作用域兩列 ①,對照〈用詞〉子協程。
severity: major
blocking: 是 判準:實作者要自己選一種定義,選「含」會產出一批必然等價的壞法,放行比例直接影響 RETIRE-IF 撤列判定。

引句:「大括號的 statements 裡①有兩個不同的陳述各自含 `async`/`launch` 呼叫(後一個 follows 前一個)」
引句:「作用域大括號裡直接呼叫、或位在迴圈呼叫大括號裡的 `async`、`launch`」

問題:①寫「含」,ast-grep 的自然寫法是任意深度。〈用詞〉卻限定「直接呼叫」。
失敗場景:
- 輸入 `supervisorScope { val x = coroutineScope { async { 1 }.await() }; val y = coroutineScope { async { 2 }.await() } }`。
- 外層大括號裡沒有任何子協程,兩個 `async` 都在內層作用域。
- 我用任意深度的「含」寫法實跑,外層 `supervisorScope` 命中。
- 換成 `coroutineScope` 必然等價,但規則不排除。
- `withContext(IO) { launch {} }` 與 `a.launch {}`、`this.async {}` 這類寫法,spec 也沒說算不算「async/launch 呼叫」。

佐證:本機 ast-grep 0.51.2 實跑,statements 兩個子句各含內層 `async` 時,外層命中(`supervisorScope` 第 1 行)。

## b3 `$A.retry(…)` 整個呼叫樣式遇到接收者與 `.retry` 之間的註解就整條不命中,spec 沒交代
spec 段落:範圍 2 `retry` 兩列、範圍 3 `_choice_anchor` 的「跳過空白與換行」、S2。
severity: minor
blocking: 否 判準:只是漏判,不會產出壞法,屬未標明的天花板。

引句:「從 `$A` 結尾開始跳過空白與換行再比對 `.` 或 `?.` 加識別字」

問題:Flow 鏈上最常見的是在 `.retry(3)` 上一行寫註解,或在上一行行尾寫 `// …`。
失敗場景:
- 輸入 `repo.items()\n    // 失敗重試三次\n    .retry(3)`。
- ast-grep 的 `$A.retry($$$B)` 樣式在 call_expression 中間夾到註解節點就不匹配。
- 我實跑:`.map { it } // keep` 後接 `.retry(3)`、`repo.items() // fetch` 後接 `.retry(3)`、獨立一行註解後接 `.retry(3)` 全部 0 命中。
- 單行、純換行、註解在更前面的鏈段仍命中。
- 就算規則改成能命中,錨點算法也只跳空白;既有 `_CHOICE_GAP_SKIP_RE` 是跳空白加註解,spec 沒沿用。

佐證:
- file: `scripts/lumos:77402`(`_choice_anchor` 方法名現行算法)
- file: `scripts/lumos:77450`(`_CHOICE_GAP_SKIP_RE` 定義處,以 `grep -n "_CHOICE_GAP_SKIP_RE" scripts/lumos` 對得上)

## b4 `Result.retry()` 排除只寫「Result 識別字」,帶限定名的寫法排除不到
spec 段落:範圍 2 `retry` 兩列、S5。
severity: minor
blocking: 否 判準:落成「編不過」,只會灌高 RETIRE-IF 的「跑不出結果」比例。

引句:「規則排除接收者是 `Result` 識別字的寫法」

失敗場景:
- 輸入 `return ListenableWorker.Result.retry()` 或 `androidx.work.ListenableWorker.Result.retry()`。
- ast-grep 的 `$A` 是整串點狀接收者,不是 `Result` 識別字,排除失效。
- 壞法拿掉呼叫變成 `return ListenableWorker.Result`,編不過,落成跑不出結果。
- 在 WorkManager 專案這種寫法很常出現,會把這一列的跑不出結果比例推高,導致誤撤。

佐證:實跑 `androidx.work.ListenableWorker.Result.retry()` 命中,`$A` 為 `androidx.work.ListenableWorker.Result`(完整接收者)。

## b5 作用域規則漏掉單一陳述內的多個子協程、`for`/`repeat` 迴圈,天花板沒寫
spec 段落:範圍 2 作用域兩列 ①②、〈天花板〉第 3 條。
severity: minor
blocking: 否 判準:漏判(沒有選擇點),不會產出壞法。

引句:「作用域兩列只認〈用詞〉定義的子協程(大括號裡直接看得到的,與迴圈呼叫大括號裡的);子協程藏在別的函式裡呼叫的,命中不到(漏判)」

問題:〈天花板〉只承認「藏在別的函式裡」會漏,實際還有更常見的漏判。
失敗場景(都是「兩支以上子協程、換寫法結果會不同」的真需求,我實跑都不命中):
- `awaitAll(async { a() }, async { b() })`
- `listOf(async { 1 }, async { 2 })`:兩個 `async` 在同一個陳述裡,①要求兩個不同陳述。
- `for (id in ids) { launch { load(id) } }`:`for` 不在迴圈呼叫那五個名字裡。
- `repeat(3) { launch { … } }`
- `this.async { … }` ×2:不是以識別字開頭的呼叫。

佐證:本機 ast-grep 0.51.2 實跑的結果與上面一致,上面這幾型都 0 命中。

## b6 `LAZY` 列只排除立刻 `.await()`,同形的 `.join()` 與子表達式型沒排除
spec 段落:範圍 2 `LAZY` 列、S5。
severity: minor
blocking: 否 判準:只多出等價放行,不產出壞法。

引句:「`LAZY` 列另排除「建立後同一個運算式就 `.await()`」」

失敗場景:
- 輸入 `launch(start = CoroutineStart.LAZY) { f() }.join()`:建立後立刻 `.join()` 與 `.await()` 同樣必然等價,規則不排除。
- 實跑時,若排除條件用「往外找任意層 `.await`/`.join`」的寫法,`foo(async(start = LAZY) { }).await()` 這種不是必然等價的寫法會被誤排除。
- spec 只寫「同一個運算式」,沒定義往外找幾層,實作者必須自己決定。

佐證:本機 ast-grep 0.51.2 實跑,`.LAZY` 命中,加上 `not inside` 的 `.await` 條件時行為依 `stopBy` 而變。

## b7 `replay` 規則只收具名引數,位置引數 `MutableSharedFlow<Int>(1)` 漏掉;也沒限定呼叫名稱
spec 段落:範圍 2 `replay` 兩列。
severity: minor
blocking: 否 判準:漏判,以及同名引數的少量等價放行。

引句:「用 `inside` 限定它的外層 value_argument 名稱是 `replay`;其他數字不收」

失敗場景:
- `MutableSharedFlow<Int>(1)`:`replay` 是第一個位置參數,不命中。
- 規則沒限定被呼叫的函式。我實跑 `Foo(replay = 1)` 也命中,同名自訂參數會走到等價放行。
- 這兩點〈天花板〉都沒列。

佐證:本機 ast-grep 0.51.2 實跑,`MutableSharedFlow<Int>(1)` 0 命中,`Foo(replay = 1)` 命中。

## 圖譜鏡頭(固定席)
- ‹Systems/kotlin規則包›:這份設計會破壞它嗎?不會。「型錄、規則、樣本三項要一次做齊」這條合約被計劃〈實務隱患〉守衛面與〈回退〉自己承認,且範圍 4 不動 check.py 白名單,類別與錨點都是既有的。我沒找到 spec 與該節點衝突的地方。
- ‹Systems/規格閘›:這份設計會破壞它嗎?不會。處置鍵 (檔, 行指紋) 不變,「整個呼叫命中」只影響錨點行與壞法 `old`,不影響 `_choice_fp` 的種子,S7 另外守既有行為。

## 各節逐讀與風險類
已讀,無 finding:白話、舊否決比對、用詞、不做、依據來源、驗收條款、預期值表、回退。我只抽查了對應決策表 D-3、D-4、D-7、D-8、D-9、D-11、D-15、D-16、D-26 存在。
實務隱患逐類:
- 併發、金流、對外送出:已排除,維持原判。
- 不可逆:無。治理帳逐筆追加,spec 已說明撤列後的處置續用規則。
- 守衛面:有,即 b1 與 b2。
- 編不過:有,即 b4。

可執行性:`_choice_anchor`、`_choice_api_edits`、`_choice_also` 與 `_choice_pick` 的簽名與 spec 描述一致,我對照原始碼確認過。`mv` 目前只讀 `metaVariables.single`,`$A` 屬於 single,取得到。範圍 3 的三處擴充可以照 spec 一步步做完。

總結:最高嚴重度 major,blocking 共 2 條
