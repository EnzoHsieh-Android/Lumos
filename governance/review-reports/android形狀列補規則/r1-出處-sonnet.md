severity: major

這份設計有 3 條 major(API-2 的形狀寬於出處、ARCH-62 的對應表超出出處、API-7 的不寫理由站不住),另有 3 條 minor。

先說我沒查到的部分:
- Dagger 的 `EntryPointAccessors` API 頁在 `https://dagger.dev/api/latest/dagger/hilt/android/EntryPointAccessors.html` 回 404,我沒讀到各 `fromX` 的 javadoc。
- 我沒有逐一打開 androidx lint 原始碼、compose-rules 和 Slack compose-lints 的規則頁,也沒查 IntelliJ 的 `MapAwaitOnCollectionOfDeferred` 這個檢查名。這三處的結論只靠搜尋,不算確認。

severity: major
blocking: 是
標題:API-2 的 `forEach { it.await() }` 超出出處原文
引句:「`$L.forEach { it.await() }`、`$L.forEach { $X -> $X.await() }`」
網頁:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/await-all.html 逐字原文:This function is not equivalent to `deferreds.map { it.await() }` which fails only when it sequentially gets to wait for the failing deferred, while this `awaitAll` fails immediately as soon as any of the deferreds fail.
- 兩個 awaitAll 多載的 KDoc 都只點名 `map { it.await() }`(第二個多載寫 `this.map { it.await() }`),完全沒有 `forEach`。
- 原文只說兩者「不等價」,講的是失敗傳遞的時機,沒說這是壞寫法。
- 型錄 API-2 的「形狀」欄也把 `forEach` 一起列了。這兩個 `forEach` 形狀要靠推論才接得上,不符合「直接講到那個寫法」的判法。
- 建議:規則只留 `map` 兩形,`forEach` 形狀另找出處,或降成只登記並明講沒有出處。
- 假陽性也由此而來:`forEach` 常是對 `Task`、`Job` 或 `ListenableFuture` 呼叫 `await()`,出處完全沒涵蓋。

severity: major
blocking: 是
標題:ARCH-62 的 fromFragment/fromView 對應表,引的兩個網頁都沒講到
引句:「fromApplication↔SingletonComponent、fromActivity↔ActivityComponent、fromFragment↔FragmentComponent、fromView↔ViewComponent」
網頁:https://developer.android.com/training/dependency-injection/hilt-android 逐字原文:Make sure that the component you pass as a parameter and the `EntryPointAccessors` static method both match the Android class in the `@InstallIn` annotation on the `@EntryPoint` interface.
網頁:https://dagger.dev/hilt/entry-points.html 逐字原文:the methods in `EntryPointAccessors` are more appropriate and type safe for retrieving entry points
- Android 頁的「元件對照表」只有 Singleton、ActivityRetained、ViewModel、Activity、Service 五個元件,沒有 `FragmentComponent` 和 `ViewComponent`。
- 該頁的範例只有 `fromApplication` ↔ `SingletonComponent`,並說「若綁定在 `ActivityComponent` 就改用 ActivityContext」。所以兩個網頁最多直接支撐 `fromApplication` 和 `fromActivity` 兩對。
- Dagger entry-points 頁完全沒出現 `fromApplication`、`fromActivity`、`fromFragment`、`fromView`,也沒出現 `ViewWithFragmentComponent`。
- 規則比對的四對映射比原文寬,而且是一對一寫死。我能想到的問題(我讀不到 javadoc,未查證):
  - 在 Fragment 內的 View 可能用 `@InstallIn(ViewWithFragmentComponent)` 搭配 `fromView`,會被誤報。
  - `@InstallIn` 帶多個元件的寫法,規則沒交代。
- 建議:規則先收窄到 `fromApplication` 和 `fromActivity` 兩對,另兩對等補到 javadoc 或 Dagger 官方文件再加。「依據來源」表裡 ARCH-62 的 Dagger 網址也不該當成對應表的出處。

severity: major
blocking: 是
標題:API-7 被放進不寫,但出處直接,理由不成立
引句:「API-7 的 `retry()` 分不出是不是 Flow」
網頁:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/retry.html 逐字原文:The default value of retries parameter is Long.MAX_VALUE. This value effectively means to retry forever.
- 出處逐字講到「不帶次數的 `retry()` 等於永遠重試」,正是型錄 API-7 第一個形狀(Flow 的 `retry()` 不帶次數),出處是直接的。
- 「分不出是不是 Flow」不成立:這是 `kotlinx.coroutines.flow` 的擴充函式,同一支檔必須 `import kotlinx.coroutines.flow.retry`(或 `flow.*`)才叫得到。
- 單檔語法看得到 import,拿它當條件,就能排除 Rx 等其他 `retry()`。
- 建議:把「不帶參數的 `retry()` 加同檔 import」拆成獨立形狀重評。`while (true)` 和固定 `delay` 那兩個形狀,出處確實要推論,可以另放。
- 這一條需要實驗量誤報才算定論,所以不直接要求這輪就寫。但「出處要推論」的理由要改掉,不然審計時會被當成錯放。

severity: minor
blocking: 否
標題:ARCH-59 的「已知非限定詞」清單沒寫全,清單外一律當限定詞
引句:「ARCH-59 的「已知非限定詞註解」清單寫死在規則裡;清單外的註解一律當成限定詞(寧可少報)。」
網頁:https://developer.android.com/training/dependency-injection/hilt-android 逐字原文:As a best practice, if you add a qualifier to a type, add qualifiers to all the possible ways to provide that dependency. Leaving the base or common implementation without a qualifier is error-prone and could result in Hilt injecting the wrong dependency.
- 原文逐字存在,而且直接講到 `@Binds` 或 `@Provides` 加限定詞(同頁前文:「define the qualifiers that you will use to annotate the `@Binds` or `@Provides` methods」)。
- 所以 `@Binds` 在出處範圍內,規則沒有超出。
- 但清單只寫了「Provides、Binds、Singleton、Reusable、JvmStatic、…Scoped」。
- 多重綁定相關的註解(`@IntoSet`、`@IntoMap`、`@ElementsIntoSet`、`@StringKey` 等)是否在清單內,spec 沒說。
- 出處沒涵蓋這些:多重綁定的鍵不等於限定詞。
- 影響是少報而不是誤報(不在清單就被當限定詞),所以降成 minor。
- 建議:spec 把清單列全,並說明多重綁定註解的歸類。

severity: minor
blocking: 否
標題:UI-33 規則與型錄「形狀」欄不一致,spec 沒說要同步
引句:「`DisposableEffect(...) { … }` 裡的 `onDispose { }` 是空的」
網頁:https://developer.android.com/develop/ui/compose/side-effects 逐字原文:Having an empty block in `onDispose` is not a good practice. Always reconsider to see if there's an effect that fits your use case better.
- 出處逐字存在,且直接講到空 `onDispose`,判定可以成立。
- 但型錄 UI-33 的「形狀」欄寫的是「DisposableEffect 只有空 onDispose 且無註冊呼叫」。
- spec 的預期值表有一例是 `DisposableEffect(Unit) { log("x"); onDispose { } }` 報,代表規則不管有沒有註冊呼叫。
- 出處講的是空 `onDispose` 本身,所以規則的範圍沒超出出處。
- 但 spec 第 2 點的型錄改寫沒列「形狀」欄,型錄自檢可能出現規則與型錄形狀欄對不上。
- 另外出處是「不是好習慣,請重新考慮」這種柔性語氣,只登記或提示級(hint)是對的;若日後要升 error,要另寫理由。

severity: minor
blocking: 否
標題:型錄來源欄與依據來源表對不上
引句:「API-2 改寫 IntelliJ 檢查名 MapAwaitOnCollectionOfDeferred(只在 IDE 跑)」
- 現有型錄 API-2 寫的是「IJ:「Use awaitAll() and joinAll()」(ID 待查)」。
- spec 要換成檢查名 `MapAwaitOnCollectionOfDeferred`,但「依據來源」表沒列這個檢查名的出處網址。我也沒驗證這個名稱。
- API-1 與 API-2 的「SC CONCUR_003」標籤拿掉 detekt 部分後仍留著,型錄「來源」欄寫法要一併說明。
- 型錄 ARCH-62 的〔查證〕網址列了 dagger.dev entry-points,但該頁沒講到 `fromX` 與元件的對應,spec 沒要求更正。
- 建議:補上 IJ 檢查名的出處,並在「依據來源」表分開寫每個網址實際支撐哪一部分。
- file: `skills/kotlin-idioms/checks-catalog.md:154`
- file: `skills/kotlin-idioms/checks-catalog.md:506`
- file: `skills/kotlin-idioms/checks-catalog.md:360`

已查,無 finding:
- UI-33 的出處原文逐字存在,規則判的就是原文那個寫法(空 `onDispose`)。
- ARCH-59 的出處原文逐字存在,且 `@Binds` 與 `@Provides` 都有被原文點到。
- API-2 的 `map { it.await() }` 兩形與 KDoc 逐字吻合。
- detekt 官方 coroutines 規則集共 9 條,頁面逐字列出 CoroutineLaunchedInTestWithoutRunTest、GlobalCoroutineUsage、InjectDispatcher、RedundantSuspendModifier、SleepInsteadOfDelay、SuspendFunInFinallySection、SuspendFunSwallowedCancellation、SuspendFunWithCoroutineScopeReceiver、SuspendFunWithFlowReturnType。
- 其中沒有 SequentialAsyncAwait,也沒有任何涉及 `await`/`awaitAll` 的規則,spec 這句成立。
- 我另外搜尋空 `onDispose` 與 `EntryPointAccessors` 對應的現成 lint,沒找到;但這只是搜尋結果,不是逐頁確認。
- UI-51(看不到筆數,門檻要人判)和 ARCH-58(出處只講注入發生的時間點,沒講之前讀會怎樣)的不寫理由,我判斷成立。
- 實驗段與 PRIOR-ART 對 detekt 的描述,和我讀到的規則集頁一致。

最嚴重 severity:major,blocking 共 3 條(API-2 的 `forEach` 形狀、ARCH-62 的 fromFragment/fromView 對應、API-7 不寫的理由)。

我只做了網頁查證與讀 repo,沒有建過任何檔案或目錄,`/tmp/lumos-seat-work/android形狀列補規則/出處-sonnet/` 下沒有產物。
