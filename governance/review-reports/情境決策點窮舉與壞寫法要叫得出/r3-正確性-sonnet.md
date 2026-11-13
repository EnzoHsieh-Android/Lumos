severity: major

我照 spec〈用詞〉的抽法實抽了 1.10.2 的 klib 與 JVM 清單,再載入 `scripts/lumos` 與 `check.py`,用真型錄(60 列情境列)跑了正反向歸屬、停用字、反查單位的「叫得出」和「改由」。我的抽取腳本與實驗都放在 `/tmp/lumos-seat-work/情境決策點窮舉與壞寫法要叫得出/正確性-sonnet/`。

**前兩輪修復的驗收**

- 反查單位數:共 195 個,其中 184 個有片段、11 個 `<無片段>`,與 spec 一致。
- 路徑篩選:`_kt_situation_segments` 目前用的條件,在 `app/src/test` 判不過,在 `androidTest` 和 `main` 判得過,與 spec 描述一致。
- 規則訊息編號:`rules/` 底下 148 條規則,訊息開頭全是 `[編號]`,每條都有 `samples/bad/<id>/`。
- `forEach { it.await() }`:確實不在 `kt-map-await-deferred` 的壞例樣本裡,spec 預期的「報」成立。
- `promise`、`asPromise`、`awaitAnimationFrame`、`asCoroutineDispatcher` 這 4 個確實被丟,`coroutineContext`、`immediate`、`runBlocking`、`IO` 都留著。
- `isActive` 沒有多出 `active`。

**finding 1:`Dispatchers.IO` 的停用字檢查在真母體上不會觸發**

severity: major
blocking: 是——spec 點名要擋的旗艦案例,在真資料上擋不到,S1 只能靠人造母體綠。

- 位置:〈用詞〉可見寫法定義,以及〈範圍〉2 的停用字表檢查。
- 問題:可見寫法只給「object 或伴生物件的成員」。1.10.2 klib 裡 `IO` 是頂層擴充屬性,不是 `Dispatchers` 的成員,依 spec 抽法它沒有可見寫法 `Dispatchers.IO`。
- 佐證:klib 第 1057 行是 `final val kotlinx.coroutines/IO // …|@kotlinx.coroutines.Dispatchers{}IO[0]`,第 1058 行的接收者是 `(kotlinx.coroutines/Dispatchers)`。依 spec 抽出的 `IO` 比對形狀只有 `IO` 與 `IO(`。`STOP_TRIGGERS` 與所有名稱的比對形狀交集後,`Dispatchers.Default` 對得上 `Default`,`Dispatchers.IO` 沒有對上任何名稱。
- 後果:真型錄裡 `IO` 標 `無決策`、理由不帶前綴,自檢不會報。S1 預期值表的 `IO` 那一列只有在測試把 `IO` 寫成 `object Dispatchers` 的成員時才會紅,與 1.10.2 真資料不一致。
- 建議:把頂層擴充屬性/函式的接收者是 object 的情況也算可見寫法(`Receiver.名稱`),或把停用字表直接對名稱本身而不是比對形狀。

引句:「停用字表裡的字等於某個名稱的任一種比對形狀(例 `Dispatchers.IO` 等於 `IO` 的可見寫法)」

引句:「是 object(例 `Dispatchers`)或伴生物件(含具名伴生物件,例 `Channel.Factory`)的成員時」

**finding 2:`TEST-` 單位用「兩個路徑任一個」判叫得出,會把平常在 `src/test` 的寫法判成已被問到**

severity: major
blocking: 是——會漏報本案要消除的「默默放行」,而且是漏報在 `runTest` 和 Turbine 這類最常見的位置。

- 位置:〈用詞〉「叫得出」。
- 問題:`TEST-` 單位只要 `androidTest` 路徑切得出就算叫得出,所以不進〈叫不出的壞寫法〉。但 `app/src/test/…` 會被 `_PITFALL_DIFF_TEST_PAT` 整支排除,不出情境段。
- 佐證:我把 12 個 `TEST-` 有片段的單位按 spec 包成檔,放在 `app/src/androidTest/java/x/XTest.kt`,其中 8 個叫得出,放在 `app/src/test/...` 全部叫不出。這 8 個裡有 5 個是 JVM 單元測試專屬的寫法:
  - D-21 / TEST-15:`UnconfinedTestDispatcher`
  - D-49 / TEST-6:`runTest { val vm = VM(fake); … }`
  - D-49 / TEST-14:`runTest(UnconfinedTestDispatcher()) { launch { … } }`
  - D-50 / TEST-18:`flow.test { awaitItem() }`
  - D-50 / TEST-19:`awaitItem()`
- 後果:自檢對這 5 個判「叫得出」,表上不用列,也不會有人知道改由誰抓。其實這些寫在 `src/test` 時一律不被問。
- 建議:`TEST-` 單位至少要分開判 `src/test` 與 `androidTest`。`src/test` 切不出的,要嘛進表、要嘛明寫「測試檔本來就不出情境題」並計數,不能讓任一路徑代表全部。

引句:「任一個路徑切出的段的候選列含那一列就算叫得出」

**finding 3:JVM 補來源會補進讀取函式與 `@JvmName` 別名,與「不補讀取函式」互相矛盾**

severity: minor
blocking: 否——只是母體多幾列雜訊,逐列分類即可,不會讓檢查判錯。

- 位置:〈用詞〉JVM 補來源①。
- 問題:補來源的字面規則是取 `…Kt` 門面類別裡所有 `public static final fun`。頂層屬性的讀取函式就長這樣,所以會被補進來。
- 佐證:按 spec 字面實抽,JVM 補來源比 klib 多出 22 個函式名,裡面有 `getJob`、`getCoroutineContext`、`getDEFAULT_CONCURRENCY`、`getDefaultDelay`、`getRECOVER_STACK_TRACES` 這 5 個讀取函式,以及 `flowCombine`、`flowCombineTransform`、`debounceDuration`、`ensurePresent`、`from` 等 `@JvmName` 別名。這跟同段「成員與讀取函式不從 JVM 清單補」自相矛盾。

引句:「成員與讀取函式不從 JVM 清單補(JVM 專屬的成員列進〈天花板〉)」

**finding 4:`fun interface` 的宣告字母歧義會抽錯名稱**

severity: minor
blocking: 否——錨點檢查和數量下限不一定抓得到,但不影響其他檢查的判斷。

- 位置:〈用詞〉klib 逐行抽法。
- 問題:宣告字列了 `fun` 又列了 `interface`,「修飾字」沒有列表。klib 有 4 個 `abstract fun interface`:`FlowCollector`、`SharingStarted`、`DisposableHandle`、`Runnable`。
- 佐證:我第一版用「找到第一個宣告字就取下一個詞」的寫法,抽出的名稱是 `interface`,`Runnable` 等 3 個名稱消失。`SharingStarted` 正好是 `Lazily`/`WhileSubscribed` 的外層,它的可見寫法會變成 `interface.Lazily` 一類的錯值。
- 因為表是用同一個抽法產生的,錯了會自洽全綠,除非測試釘 `Runnable` 或 `SharingStarted`。

引句:「每個宣告行(`fun`、`val`、`var`、`const val`、`class`、`interface`、`object`、`enum entry`)去掉修飾字」

**finding 5:object 成員的可見寫法讓物件名觸發字「搜到」每個成員,逼出一批假的 D-n/撞名**

severity: minor
blocking: 否——可以全標 `撞名`,機械上過得去,但歸屬欄的意義被稀釋。

- 位置:〈範圍〉1 的 `D-n` 與 `撞名 D-n` 核對,以及〈範圍〉2 反向。
- 佐證:D-17 的觸發字 `NonCancellable` 搜得到 `NonCancellable.cancel`、`.join`、`.start`、`.parent`、`.children`、`.isActive`、`.isCompleted`、`.isCancelled`、`.onJoin`、`.attachChild`、`.invokeOnCompletion`、`.getCancellationException`。D-19 的 `GlobalScope` 搜得到 `GlobalScope.coroutineContext`。
- 後果:這 13 個通用名稱都被反向規則要求標 `D-17`/`D-19` 或 `撞名`。標 `D-17` 時只要是 `NonCancellable` 的成員就過,可以假過。其中 `cancel`、`isActive` 同時是停用字。

引句:「而那個名稱的歸屬沒有 `D-n` 也沒有 `撞名 D-n` → 問題」

**finding 6:反向規則只要求至少一個 D-n/撞名,與 S1 `combine` 要列全三列的說法不同**

severity: minor
blocking: 否——只是歸屬欄可能漏列,不影響窮舉。

- 佐證:`stateIn` 同時被 D-5、D-6、D-15、D-49 搜到,只標 `D-15` 就過。`collectLatest` 被 D-4、D-16 搜到,同理。
- 預期值表寫「`combine` 被三列搜到」,暗示要列全,但檢查沒擋漏列。

**finding 7:`決策不問 <主表列>` 只核「列的壞寫法欄出現這個詞」,同形異義或散文提到就算過**

severity: minor
blocking: 否——檢查本來就只核整字出現,放過的是語意,不是機械條件。

- 位置:〈範圍〉1 `決策不問`。
- 佐證:真型錄裡有 3 個名稱整字出現在主表列,但不在該列任何反引號片段裡。
  - `DEFAULT`(`CoroutineStart.DEFAULT`)出現在 ARCH-76,那條是 intent-filter 的 DEFAULT category,與協程無關。
  - `release`(`Semaphore.release`)出現在 DATA-49,是 WakeLock 的 release。
  - `Deferred` 出現在 API-3。
- 後果:`決策不問 ARCH-76` 就能通過自檢。ARCH-76 又不是任何情境列的對應檢查,按〈天花板〉6 不進反查,等於零驗證,仍是名稱層級背書。

引句:「那個主表列的壞寫法欄,剝掉反引號後要以整字出現這個名稱的任一種比對形狀」

**finding 8:enum entry 沒有可見寫法,但觸發字又只准母體的名稱或比對形狀**

severity: minor
blocking: 否——能用裸名繞過,只是裸名太泛。

- 佐證:`CoroutineStart.LAZY`、`BufferOverflow.DROP_OLDEST` 這類真實寫法,依 spec 只能用裸名 `LAZY`、`DROP_OLDEST`、`SUSPEND`、`DEFAULT`、`START`、`STOP` 當觸發字。後面幾個很泛,很可能超過 8%,結果會被推去 `決策不問`。
- 〈天花板〉6 自己舉了 `CoroutineStart.UNDISPATCHED`。

引句:「本案新增的觸發字只准是 API 母體的名稱或比對形狀」

**finding 9:試抽數字我重現不出來**

severity: minor
blocking: 否——數字只是敘述,對自檢沒有影響。

- 佐證:按 spec 抽法我得到 425 個名稱,丟 4 個後剩 421;spec 寫 427 丟 4。
- 一個可能原因:「最近的類別標頭的完整名稱」有歧義。`CancellableContinuationImpl` 的標頭行含 `kotlinx.coroutines.internal/CoroutineStackFrame` 這個超類型,若整行比對,會多丟 `callerFrame`、`callOnCancellation`、`callCancelHandler`、`getContinuationCancellationCause`、`getStackTraceElement`、`nameString` 共 6 個名稱。
- 建議:寫明只看類別自己的套件路徑,並把數字改成實作時的實測值。

引句:「2026-11-12 照這條試抽 1.10.2:427 個名稱丟 4 個」

**finding 10:`_kt_sit_path_ok(rel)` 的簽名會丟掉 `skip`,與「行為不變」不一致**

severity: minor
blocking: 否——只影響消費專案裡被跳過的工具檔,而且工具檔不是 `.kt`。

- 佐證:`scripts/lumos` 現行的 `_kt_situation_segments` 先用 `not _PITFALL_DIFF_TEST_PAT.search(rel) and _stack_changed_ok(rel, skip)` 篩檔。`skip` 是呼叫端傳入的參數,只收 `rel` 的函式帶不進去。
- 建議:簽名加 `skip`(`check.py` 傳空集合),或明說 `skip` 留在呼叫端。

引句:「本案把它抽成 scripts/lumos 的一支小函式 `_kt_sit_path_ok(rel)`(新增)」

**已讀,無 finding 的節**

- 〈範圍〉3 改由:`規則`/`範本` 的核對方式。真型錄 95 個叫不出的單位裡,規則路線可行 6 個,規則存在但片段不在樣本 14 個,沒有會擋規則 75 個;範本路線 34 個有範本者只有 5 個能字面通過,其餘只能改由代碼審,與 spec 預期的方向一致。
- 〈範圍〉4 接法、〈範圍〉6 筆記與型錄說明:已讀,無 finding。
- S3、S4、S6、S7、S8:S4 的 `flatMapMerge` 在 API-8 壞寫法欄有片段,可成立,其餘依賴實作,無 finding。

最嚴重 severity:major;blocking 共 2 條(finding 1、finding 2)。
