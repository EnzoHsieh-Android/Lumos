severity: major

我對三份規則檔逐條讀過,並用 ast-grep 實跑重現。實跑用臨時 Kotlin 檔,規則包與 Android 指令都是本機的。下面每條都跑過,輸出是 `行號 規則id`。臨時目錄已刪(`/tmp/lumos-seat-work/code-kotlin規則包/規則1-sonnet`)。

## 一、Major(會擋推送的規則,在常見正確寫法上誤報,或 message 教錯)

### M1 kt-retrofit-body-bang(error):先擋掉失敗再 `body()!!` 也被擋
引句:「regex: '^if\s*\(\s*[\w.?]*\.isSuccessful\s*\)'」
severity: major
blocking: 是

規則只認 `if (x.isSuccessful)` 緊貼著的外層 if。下面三種正確寫法都被報 error。
```kotlin
if (!response.isSuccessful) throw HttpException(response)
return response.body()!!          // 報
if (response.isSuccessful && response.body() != null) { return response.body()!! }  // 報
check(response.isSuccessful); return response.body()!!   // 報
```
輸出:`10 kt-retrofit-body-bang`、`14 …`、`20 …`。型錄 API-15 的標準寫法就是「先判 isSuccessful」,但最常見的 guard clause(提早 throw)反而被擋。建議改成 hint,或把「同函式內先出現 `isSuccessful` 判斷」也算已檢查。

### M2 kt-viewmodel-holds-ui-context(error):自己 message 教的 `@ApplicationContext` 也被擋
引句:「regex: ':\s*(Context|Activity|AppCompatActivity|ComponentActivity|FragmentActivity|View|Fragment)\b'」
severity: major
blocking: 是

```kotlin
@HiltViewModel
class A @Inject constructor(@ApplicationContext private val context: Context) : ViewModel()
```
輸出:`3 kt-viewmodel-holds-ui-context`。message 與型錄 ARCH-4 都寫「注入 Application 層依賴(@ApplicationContext)」,規則卻對它報 error。該排除帶 `@ApplicationContext` 註解的參數。

### M3 UI-30 / UI-7 / UI-16 / UI-70 共用的 `deferred-lambda` 清單漏了 `rememberXxx { }` 回呼與其他延後 lambda
引句:「regex: '^(LaunchedEffect|SideEffect|DisposableEffect|onDispose|remember|rememberSaveable|derivedStateOf|produceState|snapshotFlow|rememberUpdatedState|clickable|combinedClickable|selectable|toggleable|pointerInput|detectTapGestures|detectDragGestures|launch|async|withContext|LifecycleEventEffect|LifecycleResumeEffect|LifecycleStartEffect|BackHandler|on[A-Z]\w*)$'」
severity: major
blocking: 是(kt-compose-backwards-write 與 kt-compose-navigate-in-body 是 error)

清單用完整比對,`rememberLauncherForActivityResult` 與 `rememberDraggableState` 不在內。下面這些延後執行的回呼,都被當成組建本體:
```kotlin
val imageUri = remember { mutableStateOf<Uri?>(null) }
val launcher = rememberLauncherForActivityResult(GetContent()) { uri -> imageUri.value = uri }   // 報 error UI-30
val perm = rememberLauncherForActivityResult(RequestPermission()) { ok -> if(!ok) Toast.makeText(ctx,"x",0).show() } // 報 UI-7
val drag = rememberDraggableState { delta -> offset.value += delta }   // 報 error UI-30
val l2 = rememberLauncherForActivityResult(GetContent()) { navController.navigate("y") } // 報 error UI-70
```
輸出:`4 / 7 kt-compose-backwards-write`、`5 kt-compose-side-effect-in-body`、`18 kt-compose-navigate-in-body`。

同一個清單還漏了這幾類,也實跑確認會誤報:
- `rememberTransformableState { s.value += z }`
- `rememberSwipeToDismissBoxState(confirmValueChange = { s.value = 2; true })`
- `Canvas { s.value = 3 }`
- `AndroidView(update = { it.value = progress })`(Slider/NumberPicker 的 `.value` 是 View 屬性)
- 組建內的區域函式,例如 `fun reset() { imageUri.value = null }`(輸出 `11`、`12`)

建議:`remember` 與 `rememberXxx` 用 `^remember\w*$`,並把 `local function_declaration`、`update`、`confirmValueChange` 等具名 lambda 引數併入延後清單。

### M4 kt-compose-heavy-object-in-body(warning):Canvas / drawBehind 的繪製 lambda 內 `Path()`、`Paint()` 被當重組成本
引句:「- pattern: Path()」
severity: major
blocking: 是
```kotlin
Canvas(Modifier) { val p = Path(); drawPath(p, Color.Red) }   // 報
Modifier.drawBehind { val q = Paint() }                         // 報
```
輸出:`13 / 14 kt-compose-heavy-object-in-body`。繪製 lambda 在 draw 階段執行,不是重組熱路徑,message「每次重組都新建」對它是錯的。Compose 官方範例大量用 `Canvas { val path = Path() … }`。deferred 清單沒有 `Canvas`、`drawBehind`、`drawWithContent`、`drawWithCache`、`layout`。

### M5 kt-compose-scroll-state-not-remembered(warning):包在 `remember { }` / `rememberSaveable { }` 裡也報
引句:「- pattern: ScrollState($$$)」
severity: major
blocking: 是
```kotlin
val s = rememberSaveable(saver = ScrollState.Saver) { ScrollState(0) }   // 報
val l = remember { LazyListState() }                                       // 報
```
輸出:`15 / 16 kt-compose-scroll-state-not-remembered`。message 自己說「改用 remember 版本」,規則卻沒排除已在 remember 內的呼叫。

### M6 kt-launchedeffect-constant-key(warning):用到函式參數就報,包括永遠不變的 state holder / ViewModel
引句:「- pattern: LaunchedEffect(Unit) { $$$ }」
severity: major
blocking: 是
```kotlin
@Composable fun A(snackbarHostState: SnackbarHostState, viewModel: VM, listState: LazyListState) {
    LaunchedEffect(Unit) { snackbarHostState.showSnackbar("x") }   // 報
    LaunchedEffect(Unit) { viewModel.events.collect { } }           // 報
    LaunchedEffect(Unit) { listState.scrollToItem(0) }              // 報
}
```
輸出:`8 / 9 / 10 kt-launchedeffect-constant-key`。這是最常見的合法寫法。型錄 UI-3 的壞例只列「依賴參數 id」「onTimeout 是回呼」。規則卻把任何同名參數都報,連具名引數標籤(`vm.load(id = 5)` 的 `id`)也報。建議收斂到「參數名是 `on[A-Z]` 回呼,或名稱不含 ViewModel/State/Controller/Host 的值型參數」,否則降 hint。

### M7 kt-compose-lazy-in-same-direction-scroll(error):固定高度的 LazyColumn 放在 verticalScroll 裡不會崩,卻被報 error
引句:「regex: ^verticalScroll$」
severity: major
blocking: 是
```kotlin
Column(Modifier.verticalScroll(rememberScrollState())) {
    LazyColumn(Modifier.height(300.dp)) { items(list, key = { it.id }) { Text("") } }   // 報
}
```
輸出:`23 kt-compose-lazy-in-same-direction-scroll`。Compose 文件的因應就是給 Lazy 清單固定尺寸。崩潰只發生在高度沒有上限時。建議排除 Lazy 自己的 modifier 帶 `height(`、`size(`、`heightIn(max` 的情況,或降級為 warning/hint。

### M8 kt-compose-preview-real-viewmodel(error):預覽裡直接 new 一個 Fake ViewModel 也被擋
引句:「regex: ^(viewModel|hiltViewModel|koinViewModel|hiltNavGraphViewModel|[A-Z]\w*ViewModel)$」
severity: major
blocking: 是
```kotlin
@Preview @Composable fun P() { HomeScreen(vm = FakeHomeViewModel()) }   // 報
```
輸出:`31 kt-compose-preview-real-viewmodel`。`[A-Z]\w*ViewModel` 把建構子呼叫(包含官方鼓勵的 Fake / 手建 ViewModel)當成取真 ViewModel。message 的壞處是「沒有 DI」,手建不經 DI 不會崩。該限制在 `viewModel()` 這類取得函式,拿掉建構子分支。

### M9 kt-uistate-android-type(warning):命名 `*State` 的 Compose 狀態容器類別收 Resources / Context 是官方寫法
引句:「regex: (State|UiModel)$」
severity: major
blocking: 是
```kotlin
class MyAppState(val navController: NavHostController, private val resources: Resources, val ctx: Context)  // 報 2 筆
```
輸出:`15 kt-uistate-android-type`(兩筆)。Compose 官方的 state holder 範例就長這樣(`MyAppState(scaffoldState, navController, resources, scope)`),類別名都以 State 結尾。規則本意是擋 ViewModel 輸出的 UiState。建議限定 `data class`,或名稱 `(UiState|UiModel)$`,不要套所有 `*State`。

### M10 kt-okhttp-response-not-closed(warning):`execute().body?.string()` 一行讀完也被報
引句:「pattern: $C.newCall($$$).execute()」
severity: major
blocking: 是
```kotlin
return c.newCall(r).execute().body?.string()   // 報 (api2.kt 2)
return response.body!!.string()                 // 報 (api.kt 4)
```
輸出:`kt-okhttp-response-not-closed`。OkHttp 官方說明是讀完 `string()` 會關閉 body,連線隨之歸還。最常見的一行寫法被報,message「沒關閉會洩漏連線」是錯的。至少要排除 `.body?.string()` / `.body!!.string()` / `.body?.bytes()` / `.body?.close()`。

### M11 kt-suspendcoroutine 第二分支:message 對 suspendCancellableCoroutine 教的是它自己
引句:「message: '[API-11]suspendCoroutine 取消不了,畫面關了請求還在跑、資源洩漏;改用 suspendCancellableCoroutine 並在 invokeOnCancellation 裡取消請求'」
severity: major
blocking: 是

```kotlin
suspend fun sus() = suspendCancellableCoroutine<Int> { cont ->
    task.addOnSuccessListener { cont.resume(it) }
}   // 報,message 卻說「改用 suspendCancellableCoroutine」
```
輸出:`30 kt-suspendcoroutine`。使用者已經在用 suspendCancellableCoroutine,看到的修法卻是「改用 suspendCancellableCoroutine」,教錯。更糟的是 Play Services Task、一次性取值的 wrapper 沒有可取消的資源,不加 `invokeOnCancellation` 本來就正確,卻被擋。建議分成兩條:第二分支 message 改成「補 `cont.invokeOnCancellation { … }`」,並降成 hint。

### M12 kt-callbackflow-no-awaitclose(error):漏掉泛型寫法 `callbackFlow<T> { }`
引句:「pattern: callbackFlow { $$$ }」
severity: major
(漏的是這列最主要的長相之一)
blocking: 是
```kotlin
fun flow1() = callbackFlow<Int> {
    val l = Listener { trySend(it) }
    api.register(l)          // 沒 awaitClose,沒報
}
fun flow2() = callbackFlow { api.register(l) }   // 這個才報 (27)
```
輸出只有 `27`,第 24 行的泛型版漏掉。`callbackFlow<T>` 在型別推不出時是必寫的寫法。要補 `callbackFlow<$T> { $$$ }`。

### M13 kt-okhttp-no-calltimeout(warning):`apply { callTimeout(...) }` 被報
引句:「pattern: $X.callTimeout($$$)」
severity: major
blocking: 是
```kotlin
OkHttpClient.Builder().apply { callTimeout(30, TimeUnit.SECONDS) }.build()   // 報 (33)
```
`apply` 裡省略 receiver 的 `callTimeout(...)` 不符合 `$X.callTimeout`。補一個 `callTimeout($$$)` 無 receiver 的分支即可。

### M14 kt-ktor-client-per-call(warning):函式內有 `client.close()` 也報,message 卻寫「而且沒關」
引句:「message: '[API-29]函式裡新建 Ktor HttpClient 而且沒關,引擎的執行緒與連線跟著洩漏;改用單例,生命週期結束時 close(),臨時用就 HttpClient().use { }'」
severity: major
blocking: 是
```kotlin
fun ktor() { val client = HttpClient(CIO); try { client.get("x") } finally { client.close() } }   // 報 (43)
```
規則只排除 `.use { }` 與 `@Provides` 函式,沒有像 API-17 那樣檢查同函式有沒有 `close()`,與 message 的「沒關」不符。

### M15 kt-lazy-items-no-key-ext / no-key:位置式 key 引數被報
引句:「- regex: '\bkey\s*='」
severity: major
blocking: 是
```kotlin
LazyColumn { items(list, { it.id }) { } }   // 報 (27),第二個位置引數就是 key
```
`items(items, key, …)` 的 key 可以不寫具名。只認 `key=` 會誤報。另外還有反向漏報:整個 `items(...) { … }` 文字裡任何地方出現 `key =`,例如 lambda 內某個元件的 `key = 3`,就算過。建議只檢查 value_arguments 裡有沒有具名 `key`,或第二個位置引數是 lambda。

## 二、Minor

### m1 kt-fragment-observe-this(error):`onCreate` 裡 `observe(this)` 不是 Lint 要擋的位置
引句:「- pattern: $L.observe(this) { $$$ }」
severity: minor
blocking: 否

`FragmentLiveDataObserve` Lint 只管 onCreateView / onViewCreated 一帶。onCreate 裡觀察與 View 無關的資料用 `this` 是合法的。輸出:`22 kt-fragment-observe-this`。建議限縮在這兩個函式內,或降為 warning。

### m2 重複命中同一個呼叫(噪音)
引句:「id: kt-register-pair-missing」
severity: minor
blocking: 否

同一行 `registerReceiver(r, f)` / `registerListener(...)` 同時被 `kt-register-without-unregister` 與 `kt-register-pair-missing` 報(輸出 `54` 兩筆、`34` 兩筆)。`OkHttpClient.Builder()…build()` 同時被 `kt-okhttp-no-calltimeout` 與 `kt-okhttp-client-per-call` 報,並且被外層 `Retrofit.Builder()…build()` 又報一次(輸出 `40` 兩筆)。`kt-vm-direct-datasource` 與 `kt-viewmodel-depends-on-api-dao` 對同一個參數也雙報(輸出 `42`)。建議合併規則,或讓其中一條 `not` 掉另一條。

### m3 kt-register-result-late:擴充函式 helper 被當「太晚註冊」
引句:「regex: ^(onCreate|onAttach)$」
severity: minor
blocking: 否

`fun ComponentActivity.registerPick(cb) = registerForActivityResult(GetContent(), cb)` 這種 helper,供 onCreate 或屬性初始化呼叫,被報(輸出 `27`)。

### m4 kt-compose-hardcoded… / 其他
- kt-fragment-binding-not-cleared:`this._binding = null` 不被認得,會誤報(輸出 `36`)。引句:「- pattern: _binding = null」,minor。
- kt-http-logging-body-unguarded:`when { BuildConfig.DEBUG -> Level.BODY else -> Level.NONE }` 被報(輸出 `58`),只認 if。引句:「pattern: HttpLoggingInterceptor.Level.BODY」,minor。
- kt-vm-direct-datasource:`*Service` 後綴會抓到 `AnalyticsService` 這類非資料來源(輸出 `5`)。引句:「regex: ^(\w*(Dao|Api|Service|Database)|SharedPreferences|DataStore|FirebaseFirestore|LocationManager|Retrofit|OkHttpClient)\b」,minor。
- kt-compose-clickable-icon-null-description:`IconButton { Row { Icon(null); Text("Add") } }` 圖示旁有文字標籤時被報(輸出 `41`),minor。
- kt-vm-stores-ui-callback:任何 `() -> Unit` 型別屬性都被當回呼(輸出 `12`),minor。
- kt-register-without-unregister / kt-register-pair-missing:Application 類別中永久註冊(輸出 `34` / `54`)被報,minor。
- kt-compose-false-stable-annotation:`@Stable` 類別用自訂 getter 的 `var`,或方法內區域變數 `val out: MutableList<Int>`,都被報(輸出 ui2 `1`、`8`)。第二種來自 `has … stopBy: end` 掃進了方法本體。引句:「kind: binding_pattern_kind」,minor,但屬 warning。

以上四條 minor 以外,也各自可在同一臨時檔重現。

## 三、沒找到問題的規則
已讀過、也試了常見變體,沒發現新問題:
- kt-vm-navcontroller、kt-vm-observeforever-leak、kt-vm-own-scope-not-cancelled、kt-hilt-retain-instance、kt-hiltworker-missing-assisted、kt-launch-when-deprecated
- kt-compose-navcontroller-param、kt-compose-font-size-from-dp、kt-compose-pointerinput-stale-callback、kt-compose-dispose-empty-cleanup

總結:本席共 15 條 major(M1 至 M15)與 7 條 minor 類發現;各誤報都已用 ast-grep 實跑重現。最需要優先處理的是 `body()!!` 的 guard clause(M1)、`@ApplicationContext`(M2)、共用 deferred-lambda 清單(M3)、`LaunchedEffect(Unit)` 用參數(M6)、Lazy 固定高度(M7)。這些都是 error 或常見寫法,會直接擋住正常的 Android 專案。
