Android Lint 在本機離線跑完了：23 列加上補的變體，**全部能編譯**，報告也都產出。結論是：**型錄登記的檢查裡，約一半照型錄原文的壞寫法不會報**。原因有兩種：一是那個檢查 Id 在這批套件裡根本不存在；二是檢查存在，但只管比型錄寫的更窄的情況。

### 結果(TSV)
「預設開不開」是那條檢查自己預設開或關，跟這次用 checkAllWarnings 全開無關。查法是用跟 AGP 8.13.2 同版的 lint-api 31.13.2,直接載入各套件的檢查清單讀出來。命令列的 `lint --show` 是 8.9.0,而且讀不到外加套件，所以沒用它。

```
列編號	壞例	登記的檢查Id	有沒有報	等級	預設開不開	實際報出的Id與訊息首句
UI-96	ArcAnimationSpec<Float>	ArcAnimationSpecTypeIssue	報	Hint	開	ArcAnimationSpecTypeIssue: Arc animation is intended for 2D values such as Offset, IntOffset or DpOffset.
UI-13	a mutableStateOf(0)	AutoboxingStateCreation	報	Hint	開	AutoboxingStateCreation: Prefer `mutableIntStateOf` instead of `mutableStateOf`
UI-13	b mutableStateOf(0f)	AutoboxingStateCreation	報	Hint	開	AutoboxingStateCreation: Prefer `mutableFloatStateOf` instead of `mutableStateOf`
UI-13	c MutableIntState 用 .value 讀寫	AutoboxingStateValueProperty	報	Warning	開	AutoboxingStateValueProperty: Reading/Assigning `value` will cause an autoboxing operation.(讀寫各一筆;cr:MutableStateAutoboxing 是 detekt 的,lint 沒有)
UI-92	M3 lightColorScheme(primary=secondary,on色不同)	ConflictingOnColor	沒報	-	開(只在 M2)	無;這個 Id 不在 material3 1.4.0 的 lint.jar 裡
UI-92	變體:M2 lightColors 同形狀	ConflictingOnColor	報	Error	開	ConflictingOnColor: Conflicting 'on' color for a given background(onPrimary、onSecondary 各一筆;另報 ComposeM2Api Error,預設關)
UI-43	items(list, key={ it.hashCode() })	slack:ComposeItemKeyHashCode	沒報	-	未註冊	無;compose-lints 1.4.2 沒有這個 Id
UI-44	只讀 LocalDensity.current 沒標 @ReadOnlyComposable	slack:ComposeReadOnlyComposable	沒報	-	未註冊	無;1.4.2 沒有這個 Id
UI-45	@Composable fun greeting() = println("hello")	slack:ComposeRedundantComposable	沒報	-	未註冊	無(1.4.2 沒有這個 Id);只報了不相干的 ComposableNaming Warning: Composable functions that return Unit should start with an uppercase letter
UI-46	只轉呼叫 BasicText 的 composable	slack:ComposeNonRestartableComposable	沒報	-	未註冊	無;1.4.2 沒有這個 Id
UI-11	照抄:MyList(vm),項目裡 vm.onClick()	slack:ComposeViewModelForwarding	沒報	-	開	無(只報了無關的 ComposeModifierMissing)
UI-11	變體:MyScreen(vm){ MyList(vm) } 往下傳	slack:ComposeViewModelForwarding	報	Error	開	ComposeViewModelForwarding: Forwarding a ViewModel through multiple @Composable functions should be avoided.
UI-100	@Preview×2 annotation class DarkLight	slack:ComposePreviewNaming	報	Error	開	ComposePreviewNaming: Preview annotations with 2 preview annotations should end with the `Previews` suffix.
API-9	a GlobalScope.launch{}	GlobalCoroutineUsage(detekt)/SC 系列	沒報	-	未註冊	無(lint 裡沒有 GlobalScopeUsage、InlineCoroutineScope、UnstructuredLaunch、ViewModelScopeLeak、LifecycleAwareScope 這些 Id)
API-9	b CoroutineScope(Dispatchers.IO).launch{}	InlineCoroutineScope 等	沒報	-	未註冊	無
API-9	c1 Fragment 裡 lifecycleScope.launch{ collect }	UnsafeRepeatOnLifecycleDetector	沒報	-	開	無
API-9	c2 Fragment 裡 lifecycleScope+repeatOnLifecycle	UnsafeRepeatOnLifecycleDetector	報	Error	開	UnsafeRepeatOnLifecycleDetector: The repeatOnLifecycle API should be used with viewLifecycleOwner
API-9	d 資料層 GlobalScope.launch{ api.sync() }	GlobalCoroutineUsage	沒報	-	未註冊	無
API-9	e GlobalScope.launch{ anim.animateTo() }	GlobalCoroutineUsage	沒報	-	未註冊	無
PERF-1	a onCreate 裡 File.readText()	WrongThread	沒報	-	開	無
PERF-1	b SharedPreferences.commit()	WrongThread	沒報	-	開	未登記的 ApplySharedPref 報了 Warning(預設開): Consider using `apply()` instead; `commit` writes its data to persistent storage immediately
PERF-1	c/d Composable 裡 getSharedPreferences/readText	WrongThread	沒報	-	開	無
PERF-1	變體:onCreate 呼叫自標 @WorkerThread 的函式	WrongThread	報	Error	開	WrongThread: Method perf1LoadFromDisk must be called from the worker thread, currently inferred thread is main thread
PERF-36	a x as Foo	CheckResult	沒報	-	開	無
PERF-36	b 公開函式回傳平台型別	CheckResult	沒報	-	開	未登記的 UnknownNullness 報了 Warning(預設關): Should explicitly declare type here since implicit type does not specify nullness
PERF-36	c list.map{} 結果沒用	CheckResult	沒報	-	開	無
UI-49	a items(list, key={ "row" })	ConstantContentStateKeyInItemsCall	沒報	-	開	無(這條只管 LazyList 裡的 sharedElement)
UI-49	變體:items 裡 rememberSharedContentState(key="row")	ConstantContentStateKeyInItemsCall	報	Error	開	ConstantContentStateKeyInItemsCall: Each Composable within a LazyList `items` call should have unique content state keys.(報在 shared state key 那行,不是 items 的 key)
ARCH-28	a class DetailFragment(val id: Long) : androidx Fragment()	ValidFragment	沒報	-	開	無(FragmentConstructorInjection、FragmentFieldInjection 未註冊)
ARCH-28	變體 b:androidx Fragment 只有帶參次建構子	ValidFragment	沒報	-	開	無
ARCH-28	變體 c:平台 android.app.Fragment 帶參建構子	ValidFragment	報	Error	開	ValidFragment: Avoid non-default constructors in fragments: use a default constructor plus `Fragment#setArguments(Bundle)` instead
DATA-32	a internal class SyncWorker(沒排入)	WorkerHasAPublicModifier	沒報	-	開(Fatal)	無
DATA-32	變體 b/c/d:internal + OneTimeWorkRequestBuilder<>/Builder(X::class.java)/from(X::class.java)	WorkerHasAPublicModifier	沒報	-	開	無
DATA-32	變體 e:private 巢狀 Worker + from(X::class.java)	WorkerHasAPublicModifier	報	Fatal	開	WorkerHasAPublicModifier: lint.pilot.Data32Holder.PrivWorker needs to be public
TEST-25	a assert(list.removeAt(0) == x)	AssertionSideEffect/ExpensiveAssertion	沒報	-	開/關	無
TEST-25	b assert(expensiveCheck())	ExpensiveAssertion	沒報	-	關	無
TEST-25	變體:assert(bump()),bump 裡 counter++	AssertionSideEffect/ExpensiveAssertion	報	Warning	開/關	AssertionSideEffect: Assertion condition has a side effect: counter++ ;ExpensiveAssertion: Kotlin assertion arguments are always evaluated, even when assertions are off
UI-80	fun X(body: @Composable () -> Unit)	ComposableLambdaParameterNaming	報	Warning	關	ComposableLambdaParameterNaming: Composable lambda parameter should be named `content`
UI-64	ModifierNodeElement 沒覆寫 inspectableProperties	ModifierNodeInspectableProperties	報	Hint	開	ModifierNodeInspectableProperties: Ui64Element does not override inspectableProperties().
ARCH-17	lifecycleScope.launchWhenStarted{ collect }	UnsafeLifecycleWhenUsage(相關)	沒報	-	開	無(跟型錄寫的「只管 finally/catch 碰 UI」一致)
STATE-5	a vm.state.collectAsState()	CollectAsStateWithoutLifecycle	沒報	-	未註冊	無
STATE-5	b lifecycleScope.launch{ flow.collect{} }	RepeatOnLifecycleWrongUsage/LifecycleAwareFlowCollection	沒報	-	開/未註冊	無
STATE-5	c flow.onEach{}.launchIn(lifecycleScope)	LaunchInWithUnstructuredScope	沒報	-	未註冊	無
UI-24	LocalConfiguration.current.screenWidthDp	ConfigurationScreenWidthHeight	報	Warning	開	ConfigurationScreenWidthHeight: Using Configuration.screenWidthDp instead of LocalWindowInfo.current.containerSize
ARCH-26	activity!! / context!! / arguments!!	UseRequireInsteadOfGet	報(3/3)	Error	開	UseRequireInsteadOfGet: Use requireActivity() instead of activity!!(另兩筆對應 requireContext、requireArguments)
ARCH-36	onDestroyView 沒呼叫 super	MissingSuperCall	報	Error	開	MissingSuperCall: Overriding method should call `super.onDestroyView`
```

三個對照組都報了。

### 跟型錄對不上、值得回頭改的地方
- **型錄登記錯或範圍寫太寬**:
  - UI-49 登記的 ConstantContentStateKeyInItemsCall 只管 LazyList 裡的 sharedElement,管不到 items 的常數 key。
  - UI-92 的 ConflictingOnColor 只在 M2 `lightColors` 報,M3 `lightColorScheme` 不報。
  - ARCH-28 的 ValidFragment 只對平台 `android.app.Fragment` 報,androidx Fragment 不報。
  - UI-11 照型錄原文寫(只用 vm、沒往下傳)不報，要往下傳給另一個 composable 才報。
- **DATA-32 的壞例本身可能不成立**:`internal` 怎麼寫都不報，只有 `private` 才報 Fatal。我的推論是 Kotlin 的 `internal` 編譯後在 JVM 上是 public,預設 WorkerFactory 用反射照樣建得出來，所以型錄寫的「工作永遠失敗」可能不對。這點我沒在執行期驗過，要改型錄前得先驗。
- **TEST-25、PERF-1**:型錄原文的壞例都不報。要斷言裡呼叫本專案自己寫、看得到在改狀態的函式才報;要函式自己標了 `@WorkerThread` 才報。
- **STATE-5、API-9 的舊紀錄可能有問題**:型錄記著 2026-11-05 實跑命中 RepeatOnLifecycleWrongUsage 與 UnsafeRepeatOnLifecycleDetector。這次照型錄原文的壞例，前者不報;後者只在「Fragment 裡 lifecycleScope 包 repeatOnLifecycle」那個變體報。那兩筆舊紀錄應該是別的樣本形狀。
- **型錄沒登記、但這次實際報出來的**:ApplySharedPref(PERF-1 的 commit 壞例)、UnknownNullness(PERF-36 的平台型別壞例，預設關)。

### 版本與偏離
- **主要版本**:AGP 8.13.2(內附 lint 31.13.2)、Gradle 8.13、JDK 17、Kotlin 與 Compose 編譯器外掛 2.2.21,compileSdk 與 targetSdk 都是 36。
- **Compose 系**:runtime、ui、foundation、animation(含 animation-core)1.11.4;material3 1.4.0;M2 material 1.6.1;ui-tooling-preview 1.11.2。
- **其他 androidx**:activity-compose 1.10.1、fragment 1.8.9、work 2.10.5;lifecycle 寫 2.7.0,實際被 Compose 拉成 2.9.4。
- **Slack**:compose-lint-checks 1.4.2(快取裡只有這版)。UI-43、44、45、46 的 Id 在 1.4.2 裡沒有，新版有沒有，離線沒辦法查。
- **material3、M2 material、ui-tooling-preview 是改用本地 aar**:快取裡這三樣缺 metadata 或 aar,離線解析不了，所以把快取裡的 aar 複製到 `app/libs` 直接引用。它們內附的 lint.jar 有被載入。
- **lifecycle 2.11.0 沒用**:它要求 AGP 9.1 和 compileSdk 37。
- **關掉了 androidTest 變體**:它需要的 lifecycle 2.8.7 不在快取。
- **TEST-25 放在 main**:照派工，測試程式也放在 `src/main`。
- **ARCH-17 沒看到棄用警告**:我在檔裡加了 `@Suppress("DEPRECATION")`,所以這次也沒有編譯期的 launchWhenStarted 棄用警告。

### 檔案
都在 /tmp/lumos-seat-work/lint-pilot/。Gradle daemon 已用 `./gradlew --stop` 停掉;build 目錄留著，由你處理。
- 各列原始碼:/tmp/lumos-seat-work/lint-pilot/app/src/main/java/lint/pilot/(檔名帶列編號)
- lint 報告原檔:/tmp/lumos-seat-work/lint-pilot/lint-results-debug.xml
- 只列 Kotlin 檔的報告摘要:/tmp/lumos-seat-work/lint-pilot/issues.tsv
- 讀預設值的小程式:/tmp/lumos-seat-work/lint-pilot/probe/Probe.java