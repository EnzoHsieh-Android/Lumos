severity: major

三十幾組實跑(臨時目錄 `/tmp/lumos-seat-work/code-kotlin規則包/規則3-sonnet/`,用 `rules/` 的 sgconfig 掃)共抓到 8 個 major 和 11 個 minor。8 個 major 都附實跑重現。

## state.yml 與 testing.yml(會擋推送)

### 1. kt-viewmodel-test-no-main-rule 靠名字認 Rule,正確寫法被擋
severity: major
blocking: 是
引句:「regex: 'Dispatchers\.setMain|Main\w*Rule|MainDispatcher\w*|MainCoroutine\w*'」
實跑重現:
- 測試類別有 `@get:Rule val coroutineRule = CoroutineTestRule()`,規則報錯。換成 `TestDispatcherRule()`、`CoroutineRule()`、`TestCoroutineRule()` 也都報。
- JUnit5 `@ExtendWith(CoroutineExtension::class)` 也報。
- Robolectric 測試(`@RunWith(AndroidJUnit4::class)`,有真的 Main looper)只要建構 `A5ViewModel()` 就報。
- 只做純運算、沒碰 viewModelScope 的 ViewModel(`A7ViewModel().computeOnly()`)也報。
- 規則看的是「有沒有出現 Main 開頭的字」,不是有沒有換 Main,所以改名過的 Rule 全被當成沒換。
- message 要使用者改成 `MainDispatcherRule`,但擋的是已經正確的寫法。

### 2. kt-test-multiple-schedulers 與 kt-testdispatcher-before-mainrule 同樣只認 Main*Rule
severity: major
blocking: 是
引句:「regex: '(?i)Main(Dispatcher|Coroutine)Rule'」
實跑重現:
- 類別有 `private val testDispatcher = UnconfinedTestDispatcher()`、`@get:Rule val rule = CoroutineTestRule(testDispatcher)`、`@Test fun t() = runTest { }`。這是排程器共用的正確寫法,卻報 kt-test-multiple-schedulers。
- `CoroutineRule(testDispatcher)` 也同樣報。
- 根因跟第 1 條一樣。建議把 Rule 名單擴成 `\w*(Dispatcher|Coroutine)\w*Rule`,或改成看「建構式有沒有收到那個 dispatcher」。

### 3. kt-livedata-setvalue-background 把 Firebase 的 setValue 當 LiveData
severity: major
blocking: 是(severity 是 error)
引句:「pattern: $L.setValue($$$)」
實跑重現:
- `scope.launch(Dispatchers.IO) { dbRef.child("a").setValue(x).await() }` 報錯。
- `viewModelScope.launch(Dispatchers.IO) { ref.setValue(x) }` 報錯。
- `withContext(Dispatchers.IO) { prefs.setValue(a, b) }` 也報錯。
- Firebase Realtime Database 的 `DatabaseReference.setValue` 本來就能在任意執行緒呼叫,而且很常在 IO 協程裡出現。規則沒有型別資訊,只認方法名。
- 另有一個漏報,相關的第 14 條有說明。

### 4. kt-mutate-state-collection(error)沒型別資訊,誤報 Map.Entry 與 Lazy
severity: major
blocking: 是
引句:「- pattern: $X.value.add($$$)」
實跑重現,以下全部報 error:
- `for (e in map.entries) { e.value.add(Item()) }`
- `map.entries.forEach { it.value.add(Item()) }`
- `val lz = lazy { mutableListOf<Int>() }; lz.value.add(1)`
- 任何自訂 holder 的 `.value.add`
- 同一個根因也讓 kt-state-value-property-assign(error)報 `entry.value.name = "x"` 和 `slider.value.foo = 3`。引句:「regex: '^\s*[\w?!]+(\.[\w?!]+)*\.value(\?|!!)?\.[\w.?!\[\]]+\s*(\+|-|\*)?='」
- `Map<K, MutableList<V>>` 逐 entry 往 value 裡加,是常見的正確寫法。
- 建議:error 級至少限定接收者名稱(`_?\w*(state|flow|live)\w*`),或降為 warning。

### 5. kt-statein-eagerly 說「附一行理由」,規則卻不看理由
severity: major
blocking: 是
引句:「pattern: SharingStarted.Eagerly」
實跑重現:
- 在 `SharingStarted.Eagerly` 上一行加 `// 理由: app-scope cache must warm up`,仍然報。
- 規則不限 ViewModel,連 Repository、application scope 都報。
- 規則也不排除測試:`src/test` 裡 `repo.flow.stateIn(backgroundScope, SharingStarted.Eagerly, 0)` 照報。
- 樣本 `good/kt-statein-eagerly` 只有 WhileSubscribed 一種好例,沒有「附理由」的好例。
- 所以 message 教的出路實際上走不通,真要 Eagerly 只能改寫。
- 建議:認前一行註解,或限定 `inside` ViewModel,並加 ignores。

### 6. kt-statein-in-function 擋掉測試本體與 Hilt `@Provides`
severity: major
blocking: 是
引句:「stateIn/shareIn 寫在函式裡,每呼叫一次建一條新熱流」
實跑重現:
- `@Provides @Singleton fun provideSettings(...): StateFlow<P> = store.data.stateIn(scope, WhileSubscribed(5_000), P())` 報。Provider 函式只會被呼叫一次。
- `@Test fun t() = runTest { val state = repo.flow.stateIn(backgroundScope, ...) }` 報。這是官方測試文件的寫法。
- 這條規則沒有 ignores(同檔的 kt-public-mutable-stateflow 有)。
- 建議:加測試目錄 ignores,並排除帶 `@Provides` 的函式。

### 7. kt-public-mutable-holder 與 kt-repository-exposes-mutable-or-dto 擋測試假實作
severity: major
blocking: 是
引句:「公開可變狀態容器(MutableLiveData/MutableSharedFlow/mutableStateOf/Channel 等)」
實跑重現(`src/test` 和 `src/androidTest` 都一樣):
- `class FakeUserRepository { val userFlow = MutableSharedFlow<User>() }` 報。
- `val events = Channel<Event>()`、`var items = mutableStateListOf<Int>()`、`val live = MutableLiveData<String>()` 也報。
- `class FakeNewsRepository { suspend fun fetch(): NewsDto }` 被 kt-repository-exposes-mutable-or-dto 報,因為類名 `Repository(Impl)?$` 也配到 Fake。
- Android 官方「假實作測試」就是這樣暴露可變流給測試推值。
- 同檔 kt-public-mutable-stateflow 已有 `**/src/test*/**` 等 ignores,這兩條漏了,前後不一致。
- 附帶:`val flowLegit = MutableSharedFlow<Int>().asSharedFlow()` 也被報,因為 `has ... stopBy: end` 抓到巢狀的 MutableSharedFlow。

### 8. kt-nonatomic-state-update 對 Compose MutableState 報錯,而且 message 的修法套不上
severity: major
blocking: 是
引句:「- pattern: $X.value = $X.value + $Y」
實跑重現:
- `@Composable` 裡 `Box(Modifier.clickable { count.value = count.value + 1 })` 報。
- `Modifier.pointerInput(Unit) { detectTapGestures { count.value = count.value + 1 } }` 也報。
- 規則只豁免 `onXxx = { }` 這種具名參數 lambda,`clickable { }`、`pointerInput` 這類尾隨 lambda 都沒豁免。
- 這些 `count` 是 `MutableState<Int>`,message 要改成 `_uiState.update { it.copy(…) }`。就我所知 `MutableState` 沒有 `update` 擴充(未上網核對)。
- `mutex.withLock { _state.value = _state.value.copy(x = 1) }` 受鎖保護也被報。
- 型錄 STATE-1 寫的是「出現在多個並行 launch 裡」,規則卻報所有讀改寫。
- 建議:限定接收者名稱為 `_` 開頭的 StateFlow,或放進 `inside viewModelScope.launch`。

## minor

### 9. kt-test-thread-sleep 範圍比型錄寬
severity: minor
blocking: 否
引句:「[TEST-28]測試用 Thread.sleep/SystemClock.sleep 等畫面,又慢又不穩」
- 型錄 TEST-28 的壞寫法是「Compose UI 測試用 Thread.sleep」。
- 實跑:`src/test` 純 JVM 測試 `class SleepTest { @Test fun t() { Thread.sleep(50) } }` 報,假實作模擬延遲 `Thread.sleep(10)` 也報。
- 這時 message 教的 `composeTestRule.waitUntil` 用不上。

### 10. kt-test-assert-after-launch-no-advance 的停止詞漏了 delay、yield、cancelAndJoin
severity: minor
blocking: 否
引句:「regex: '\b(advanceUntilIdle|runCurrent|advanceTimeBy|join|joinAll|awaitAll)\s*\('」
- `launch { vm.load() }; delay(100); assertEquals(...)` 報。
- `yield()` 後再斷言也報。
- `job.cancelAndJoin()` 後斷言也報,因為 `\bjoin` 對 `cancelAndJoin` 不成立。

### 11. kt-runtest-launch-collect-forever 對有限流也報
severity: minor
blocking: 否
引句:「message: '[TEST-5]runTest 會等所有子協程,用一般 launch 收集永不結束的狀態流會卡到逾時」
- `launch { repo.finiteFlow().collect { list += it } }; advanceUntilIdle()` 報。
- `launch { flowOf(1,2).toList(values) }` 也報,明明有限。
- 規則看不出流是不是無限,message 卻寫「永不結束」。

### 12. kt-test-shared-mutable-state 把 JUnit 慣用的 companion 靜態欄位當壞寫法
severity: minor
blocking: 否
引句:「message: '[TEST-34]測試之間共用可變狀態(companion/object/頂層 var、@FixMethodOrder)」
- `companion object { var server: MockWebServer? = null; @BeforeClass @JvmStatic fun setUp() { server = MockWebServer() } }` 報。
- `private var` 和 `object` 內的 var 也報。
- 型錄要抓的是「沒重置的共用狀態」,規則只看有沒有 var。

### 13. testing.yml 的路徑過濾沒涵蓋全部 Gradle 與 KMP 目錄
severity: minor
blocking: 否
引句:「files: ['**/src/test*/**', '**/src/androidTest*/**']」
實跑 `Thread.sleep(1)` 的結果:
- 有報:`src/test`、`src/testDebug`、`src/testFixtures`、`src/androidTest`、`src/androidTestDebug`。
- 沒報:`src/sharedTest`、KMP 的 `commonTest`、`jvmTest`、`androidUnitTest`、`androidInstrumentedTest`。
- 模組名含 test(`core-testing/src/main`、`feature-test/src/main`)的正式目錄也沒報,例如 nowinandroid 的 core/testing。
- 無 `files:` 的幾條(setmain-without-reset、runtest-launch-collect-forever、multiple-schedulers 等)會連 `src/main` 都掃。
- 漏掃是靜默的,使用者以為有檢查。

### 14. 型錄 STATE-16 的第一個常見長相沒被抓
severity: minor
blocking: 否
引句:「message: '[STATE-16]背景執行緒呼叫 LiveData.setValue 會拋 IllegalStateException」
- 型錄第一個例子是 `withContext(Dispatchers.IO) { live.value = x }`,rules/ 的規則抓不到(實跑 0 命中)。
- 抓得到的 `thread { live.setValue(x) }` 在型錄排第二。
- 因為 rules-hints/state.yml 的 kt-value-assign-background 有收,這是刻意取捨。
- 型錄那一列應註明「`.value =` 只在提示級」。
- 外層是 Main、內層切 IO 時,`not inside withContext(Dispatchers.Main)` 會讓規則整個不報。

### 15. kt-single-live-event 把任何 MutableLiveData 子類都當 SingleLiveEvent
severity: minor
blocking: 否
引句:「regex: ^MutableLiveData<」
- `class NonNullLiveData<T> : MutableLiveData<T>()` 和 `class Debounced<T> : MutableLiveData<T>()` 都被報。
- message 說「Event 包裝類吞事件」,與這些類無關。

### 16. kt-vm-fun-returns-stream 連回傳既有流的 getter 也報
severity: minor
blocking: 否
引句:「[STATE-3]ViewModel 公開函式每呼叫一次就回傳新的 LiveData/Flow,重建後又重打資料層」
- `fun getState(): StateFlow<S> = _state.asStateFlow()` 報。
- `fun events(): Flow<E> = _events.receiveAsFlow()` 也報,但它們不重打資料層。
- 帶參數的 `fun userFlow(id): Flow<User> = repo.user(id)` 才符合型錄描述。

### 17. kt-savedstate-bang 的接收者過濾是子字串比對
severity: minor
blocking: 否
引句:「regex: (?i)(savedState|handle)」
- `handlers[type]!!`、`errorHandler.get(k)!!`、`savedStates[id]!!`、`savedStateRegistry.get("x")!!` 全報。
- 這些都不是 SavedStateHandle。
- 建議:改成 `^_?(savedStateHandle|handle)$`。

### 18. kt-mutate-state-nested-collection 與 kt-state-value-property-assign 的漏報
severity: minor
blocking: 否
引句:「- pattern: $X.value.$F.clear()」
- 巢狀版沒有 `putAll`,非巢狀版有,兩邊不對稱。
- `_state.value.items.putAll(m)` 實跑 0 命中。
- `_state.value.count++`、`.value.items.removeIf {}`、`.sortBy {}`、`.value.items.set(0, x)`、`.value?.add(1)`、`/=` 也都漏。

### 19. 同一處被兩條規則重複報
severity: minor
blocking: 否
引句:「message: '[STATE-4]ViewModel 的 uiState 用 Lazily 或沒給延遲的 WhileSubscribed(),上游永不停或轉螢幕就重啟」
- ViewModel 裡的 `SharingStarted.Lazily` 同時被 kt-statein-lazily-in-viewmodel 和 kt-statein-lazily-or-no-timeout 報。
- `MutableStateFlow` 屬性同時被 kt-public-mutable-stateflow 和 kt-repository-exposes-mutable-or-dto 報。
- kt-repository-exposes-mutable-or-dto 對 `MutableList<Item>` 的 message 也教「asStateFlow()」,不適用。
- 輸出雜訊,不影響對錯。

## rules-hints/(提示級)

### 20. 升降級建議
severity: minor
blocking: 否
引句:「pattern: $M.withLock { $$$ }」
- 可考慮升級:kt-mutex-reentrant。同一把 Mutex 巢狀 `withLock` 必然死鎖,實跑 `mutex.withLock { mutex.withLock { x() } }` 正確命中,`other.withLock` 不報。唯一誤報是中間隔了不等待的 `launch`(實跑第 4 行也報)。若升級,要先排除 `launch`、`async` 之內。
- kt-value-assign-background 放提示級是對的,因為 `.value =` 無型別資訊,StateFlow 很常見,不要升。
- 不要升級:kt-runcatching-in-suspend、kt-work-policy-replace、kt-work-enqueue-not-unique、kt-lazy-thread-mode-none。
- kt-whilesubscribed-no-timeout 與 rules/ 的 kt-statein-lazily-or-no-timeout 重疊,前者只多涵蓋 ViewModel 以外的地方,可以保留。
- 沒有發現提示級該降而未降的規則。
- 以上 hint 部分只實跑了 mutex-reentrant,其餘是讀規則加推論,未逐條實跑。

總結:state.yml 和 testing.yml 沒有一條規則被我實跑證明完全漏接,但有 8 條 major,在常見正確寫法上會擋推送,而且都能在 `rules/` 底下重現。根因分三群:靠名字認 Rule、沒有型別資訊的 error 級規則(第 3、4 條)、缺測試目錄 ignores 或例外(第 5、6、7、8 條)。
