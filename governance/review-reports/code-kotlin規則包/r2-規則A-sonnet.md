severity: minor

我實跑了這份修補的每個放寬點,並把修補前版本(把 patch 反向套用出來的基準)拿來對照,確認哪些是修補才有的差異。沒有發現 major。上一輪 15 條 major 的主要誤報都收掉了,新增的問題都是放寬過頭造成的漏報,或剩下的窄角落誤報。臨時目錄 `/tmp/lumos-seat-work/code-kotlin規則包/規則A-sonnet` 已刪。

## 一、修補放寬過頭、漏掉原本該抓的壞寫法

### F1 kt-retrofit-body-bang:同函式出現 isSuccessful 就放行,第二個呼叫與只拿來印 log 的都漏掉
引句:「# 同一個函式裡判過 isSuccessful(提早 throw、check(...)、&& 併判)就算看過(代碼審 r1 M1)」
severity: minor
blocking: 否
來源:修補引入

```kotlin
suspend fun two(): Foo {
  val a = api.a()
  if (a.isSuccessful) { log(a) }
  val b = api.b()
  return b.body()!!          // b 完全沒檢查
}
suspend fun logonly(): Foo {
  val r = api.get()
  Log.d("x", "ok=${r.isSuccessful}")   // 只是印出來,沒擋
  return r.body()!!
}
```
實跑修補後兩處都沒報,修補前版本都報(基準 `6`、`11`)。單一呼叫的裸 `api.get().body()!!` 仍會報。建議把放行限縮成「與 `body()!!` 同一個接收者的 `isSuccessful`」,也就是比對 `$R` 是否相同。

### F2 kt-vm-stores-ui-callback:有初始 lambda 就放行,連 `var` 都放行
引句:「# 初始值就是 ViewModel 自己寫的 lambda 或函式參照,沒有留 UI 端的參照(代碼審 r1 m4)」
severity: minor
blocking: 否
來源:修補引入

```kotlin
class VM : ViewModel() {
  var onEvent: (String) -> Unit = {}   // Fragment 之後 vm.onEvent = { frag.x() },留住 Fragment
  var cb: () -> Unit = {}
}
```
修補後沒報,修補前版本報。預設空 lambda 再讓 UI 指派的寫法,正是型錄 ARCH-6 要擋的形狀。真正無害的是 `val` 加自己寫的 lambda,建議只對 `val` 放行,`var` 照報。

### F3 kt-uistate-android-type:外層 `sealed *State` 不再算,巢狀 data class 夾 Context 漏掉
引句:「regex: (UiState|UiModel)$」
severity: minor
blocking: 否
來源:修補引入

```kotlin
sealed class LoginState { data class Done(val ctx: Context) : LoginState() }
```
修補後沒報,修補前版本報。外層名字只以 `State` 結尾,既不是 `UiState` 也不是 `data`,而內層 `Done` 的名字又不以 State 結尾,所以兩邊都不中。`sealed interface HomeUiState {…}` 因為名字符合還是會報。建議把「外層是 sealed 或名字以 State 結尾」也算進去,或改成往上找任何 `State$` 祖先、再排除 Compose state holder。

### F4 kt-ktor-client-per-call:任何 `close()` 都放行
引句:「# 同函式裡有 close()(try/finally 關掉)就不算」
severity: minor
blocking: 否
來源:修補引入

```kotlin
fun ext() { val c = HttpClient(CIO); c.get("x"); writer.close() }   // 沒報
```
放行條件是 `$Y.close()`,沒綁到 `HttpClient` 那個變數。修補前版本會報。同函式裡有別的 stream、writer 呼叫 `close()` 很常見。建議改成「`close()` 的接收者就是被賦值的變數」,或乾脆要求 `finally`。

### F5 kt-okhttp-response-not-closed:無關的 `.body?.string()` 讓整個函式放行
引句:「regex: '\.body(\(\))?(\?|!!)?\.(string|bytes|close)\(\)$'」
severity: minor
blocking: 否
來源:修補引入

```kotlin
fun ok1(): String { val r = c.newCall(req).execute(); val x = other.body?.string(); return "a" }  // 沒報
```
函式層級的放行沒有綁到 `execute()` 回傳的那個變數。反過來,`val b = r.body; return b?.string()` 這種正確寫法還是會報(FP),只是少見。

### F6 kt-vm-direct-datasource:`TrackingService` 後綴一律放行,會放掉真的 Retrofit 介面
引句:「regex: ^\w*(Analytics|Tracking|Tracker|Logging|Logger|Crash\w*)Service$」
severity: minor
blocking: 否
來源:修補引入

```kotlin
class ParcelVM(val api: OrderTrackingService) : ViewModel()   // 沒報
```
`OrderTrackingService` 在 Retrofit 專案裡常是真的資料來源,「物流追蹤」跟「分析追蹤」同名,只看字尾分不開。修補前版本報。這條規則是 warning,所以只是漏報。建議收窄到 `Analytics|Crash\w*|Logging`,拿掉 `Tracking`、`Tracker`、`Logger`。

### F7 kt-register-result-late:所有擴充函式一律放行,不只註解說的 `= registerForActivityResult(…)` helper
引句:「# 擴充函式 helper(fun ComponentActivity.registerPick(...) = registerForActivityResult(...))由屬性初始化或 onCreate 呼叫」
severity: minor
blocking: 否
來源:修補引入

```kotlin
fun Fragment.setup() { val l = registerForActivityResult(GetContent()) { } }   // 在點擊處理器裡呼叫就會拋例外,沒報
```
修補前版本報。直接寫在擴充函式本體的註冊也被放行了,不只表達式本體的 helper。建議只放行「函式本體就是這個呼叫」的單式 helper。

### F8 kt-compose-clickable-icon-null-description:按鈕裡任何 `Text` 都放行
引句:「# 按鈕裡有 Text 標籤,讀屏念文字(代碼審 r1 m4)」
severity: minor
blocking: 否
來源:修補引入

```kotlin
IconButton(onClick = {}) { BadgedBox(badge = { Text("3") }) { Icon(Icons.Default.Add, contentDescription = null) } }  // 徽章數字不是按鈕名稱,沒報
```
`stopBy: end` 讓任何深度的 `Text` 都算標籤。建議限定 `Text` 是 `Icon` 的兄弟、不在 `badge =` 引數裡。

### F9 kt-compose-scroll-state-not-remembered:任何 `rememberSaveable` 都放行,包括沒有 saver 的
引句:「# rememberSaveable(saver = ScrollState.Saver) { ScrollState(0) } 就是 rememberScrollState 的做法(代碼審 r1 M5)」
severity: minor
blocking: 否
來源:修補引入

```kotlin
val s = rememberSaveable { ScrollState(0) }   // 沒報;ScrollState 沒有預設 saver,存狀態時會因無法存入而丟 IllegalArgumentException
```
註解說的是帶 `saver = …Saver`,規則卻放行任何 `rememberSaveable`。這一點我是依 Compose 預設 saver 的行為推論,沒有跑 Android 環境驗證執行期崩潰。建議放行條件加上引數含 `saver`。

## 二、修補後仍誤報的正確寫法(上輪沒看的角落)

### F10 kt-compose-lazy-in-same-direction-scroll:位置式 `heightIn(min, max)` 被報 error
引句:「regex: '\.(height|size|requiredHeight|requiredSize)\(|\.(heightIn|requiredHeightIn)\([^)]*max|\.sizeIn\([^)]*maxHeight'」
severity: minor
blocking: 是(error 級)
來源:修補引入(M7 的修法漏了位置引數)

```kotlin
Column(Modifier.verticalScroll(s)) { LazyColumn(Modifier.heightIn(100.dp, 300.dp)) { } }   // 報 error,但有上限、不會崩
```
正則要求引數文字裡出現 `max`,位置引數 `heightIn(100.dp, 300.dp)` 沒有這個字。具名的 `heightIn(max = …)` 都正常。建議改成「`heightIn(` 有兩個引數,或含 `max`」。

### F11 kt-lazy-items-no-key / no-key-ext:key 傳函式參照或變數會被報
引句:「# items(list, { it.id }):key 是第二個位置引數(代碼審 r1 M15)」
severity: minor
blocking: 是(warning 也擋推送)
來源:修補引入

```kotlin
LazyColumn { items(list, ::key) { } }     // 報
LazyColumn { items(list, keyFn) { } }     // 報
```
修補只認第二個位置引數是 `lambda_literal`,函式參照(`callable_reference`)與識別字都不算。`items(list, Item::id)` 這種寫法相對少見。

### F12 kt-lazy-items-no-key:純計數的 `items(5)` 沒有 ext 那條的豁免
引句:「pattern: LazyColumn { $$$ }」
severity: minor
blocking: 是
來源:上輪沒看的角落

`LazyColumn { items(5) { Shimmer() } }` 被 `kt-lazy-items-no-key` 報(實跑),但同樣形狀換成 `LazyColumn() { items(5) {} }` 就走 ext 那條,被「整數字面值或全大寫常數」豁免。兩條規則對同一種骨架佔位寫法行為不一致。plain 這條也該帶同一份豁免,或讓 ext 去管。

## 三、題目要求的其他檢查,沒發現問題

- **拆出的 `kt-suspendcancellable-no-oncancel`**:message 的修法與型錄 API-11「好」那一欄一致(`cont.invokeOnCancellation { call.cancel() }`),沒有自己發明。包一次性 Task、沒有 invokeOnCancellation 的寫法與有註冊的寫法,實跑分別報與不報。severity 是 info 且在 `sgconfig-review.yml`,不擋推送。
- **刪掉的 `kt-register-pair-missing`**:保留的 `kt-register-without-unregister` 涵蓋它的四種壞例(registerReceiver、registerListener、registerNetworkCallback、registerOnSharedPreferenceChangeListener),還多了 `registerDefaultNetworkCallback` 與頂層函式。我實跑確認 `top(ctx) { ctx.registerReceiver }` 與 Activity 內的呼叫都會報,Application 子類別(含 `MultiDexApplication`)不報。
- **刪掉的 `kt-viewmodel-depends-on-api-dao`**:`kt-vm-direct-datasource` 對 `Lazy<UserApi>`、`UserDao?`、`Retrofit` 都會報,涵蓋範圍比被刪的那條大。
- **compose 共用的延後 lambda 清單**:本地函式與 `layout` 的豁免、`remember\w*` 沒有新增放行的壞寫法。`s.value = 3` 與 `navController.navigate(…)` 直接寫在組建本體仍然報。
- **其他放寬**:`@ApplicationContext` 豁免、`callbackFlow<T>` 補上、`this._binding = null`、`when`+`BuildConfig.DEBUG` 的放行都沒有放過明顯壞例。其中 `@Named("x") Context` 與 `Activity` 參數仍然報。

總結:沒有比 minor 更高的等級,共 12 條 minor,其中 9 條是修補放寬過頭造成的漏報(F1 到 F9),3 條是修補後仍擋推送的窄角落誤報(F10 到 F12)。
