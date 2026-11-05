severity: major

# 第 2 輪 規則B(coroutines、data、flow、perf、state、testing 與 review/hints)審查報告

每條都用 Kotlin 片段實跑過。對照組是基底提交 `44c2b417e` 的舊規則,用來區分「修補引入」和「上輪沒看的角落」。實驗目錄已刪。

語意覆核級搬移(STATE-16、STATE-7 三條、nonatomic、TEST-5)和兩條去重(onReceive 與 `Lazily`/`onEach`),我沒找到問題。

- **覆核級搬移**:這幾條都得知道型別或資料流是否有限,改形狀分不開。
- **去重**:實跑的 `Lazily`、`catch().onEach`、onReceive 起協程,都還有一條規則抓得到。
- **STATE-2 去重**:Repository 的 `MutableStateFlow` 與 `MutableSharedFlow` 也都被另兩條規則抓到。

## Finding 1:CO-1 新 regex 讓 `Dispatchers.Main.immediate` 和 `Main + 其他 context` 誤報
引句:「(withContext|launch|async)\s*\(\s*(\w+\.)*(main\w*|\w*Main\w*)\s*[,)]」
severity: major
blocking: 是
來源:修補引入

regex 尾端要求接 `,` 或 `)`。`Dispatchers.Main.immediate)` 和 `Dispatchers.Main + CoroutineName("x"))` 後面不是這兩個字元,就不算切回 Main。

重現:
```kotlin
viewModelScope.launch(Dispatchers.IO) { withContext(Dispatchers.Main.immediate) { view.setText("a") } }
viewModelScope.launch(Dispatchers.IO) { withContext(Dispatchers.Main + CoroutineName("x")) { view.setText("b") } }
```
- 新規則:`kt-bg-dispatcher-touches-view` 兩行都報。
- 舊規則:兩行都不報,舊 regex 只比對 `Dispatchers.Main` 前綴。
- `Main.immediate` 是 Android 最常見的切回主執行緒寫法,所以這條是會擋推送的誤報。
- 同樣的原因,`withContext(dispatchers.main())` 這種有括號的注入寫法也報(舊版就報,這輪沒修好)。

## Finding 2:外層是 Main 的 launch 吞掉內層 IO 區塊裡真正的壞寫法
引句:「# 切回 Main:Dispatchers.Main 或注入的 main 派發器(CO-1),withContext 或另開 launch/async 都算」
severity: major
blocking: 是
來源:修補引入

`not: inside: stopBy: end` 會一路往外找。新增 `launch|async` 之後,只要最外層是 `launch(Dispatchers.Main)`,裡面再 `withContext(Dispatchers.IO)` 碰 view 就整段放行。

重現:
```kotlin
fun i() = viewModelScope.launch(Dispatchers.Main) { withContext(Dispatchers.IO) { view.setText("bad") } }
fun k() = viewModelScope.launch(Dispatchers.IO) { launch(mainlandIoDispatcher) { view.setText("bad") } }
```
- 舊規則:兩行都報。
- 新規則:兩行都不報。
- `i` 是外層 Main、內層切 IO,正是這條規則要抓的主要壞例。
- `k` 的 `mainland…` 被 `main\w*` 當成 Main 派發器。
- 建議:只認「在碰 view 的那行與最近一層背景區塊之間」的 Main 切換,不要全祖先找;名稱改成 `main`、`mainImmediate`、`Main` 這類完整比對。

## Finding 3:Worker 只要函式裡出現 runAttemptCount 就放行,連只拿來寫 log 也算
引句:「# 同一個函式裡有 runAttemptCount 判斷(含先擋後回的早退寫法)就放行」
severity: major
blocking: 是
來源:修補引入

重現:
```kotlin
override fun doWork(): Result {
    val n = runAttemptCount            // 只讀不判斷,或只寫 log
    return Result.retry()              // 永遠重試
}
```
- 新規則:不報。
- 舊規則:報。
- 任何出現 `runAttemptCount` 的字,哪怕只在 `Log.d` 或賦值裡,都讓 `Result.retry()` 放行。
- 建議:要求 `runAttemptCount` 出現在 `if` 或 `when` 的條件裡,或在 `Result.retry()` 的祖先分支裡。

## Finding 4:Eagerly 的「理由」註解鄰接判定,讓沒寫理由的 Eagerly 漏掉
引句:「regex: '^//\s*(理由|[Rr]eason)'」
severity: major
blocking: 是
來源:修補引入

有兩個漏洞:
1. `follows` 那條沒有 `^//` 錨定,`// TODO fix reasonable thing` 也算有理由。
2. 前一個屬性的行尾註解,會被當成下一個屬性的「上一行註解」。同理,下一個屬性的標題註解,會被當成上一個屬性的「緊貼註解」。

重現:
```kotlin
val a = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0) // 理由: 初始就要
val b = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0)   // 沒理由,卻不報
val c = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0)   // 沒理由,卻不報(precedes 吃到 d 的標題)
// 理由: 要
val d = f.stateIn(viewModelScope, SharingStarted.Eagerly, 0)
```
- 實跑結果:`a` 到 `e` 五行 Eagerly 全部不報。
- 其中 `b`、`c`、`e` 本來該報。舊規則五行都報。
- 建議:`follows` 的註解也要錨定 `^//\s*(理由|[Rr]eason)`,並要求註解與屬性行距為零(上一行獨立註解,或本行行尾註解)。

## Finding 5:`asCoroutineDispatcher` 只認「當場建的」,漏掉最典型的壞寫法
引句:「# 只管自己當場建的執行緒池;db.queryExecutor 這類借來的 executor 不歸這裡關」
severity: major
blocking: 是
來源:修補引入

重現:
```kotlin
class S1 {
  private val e = Executors.newFixedThreadPool(2)
  val d = e.asCoroutineDispatcher()   // 洩漏,也沒 close
}
```
- 舊規則:報。
- 新規則:不報。新規則只認 `Executors.newX(...).asCoroutineDispatcher()` 這種接在同一個運算式上的寫法。
- 先把執行緒池存進變數再轉換,在實務上比鏈式寫法更常見。
- 建議:擴成「同作用域有 `val x = Executors.new…` 且對 `x.asCoroutineDispatcher()`」也算,或改回全報並用 `db.queryExecutor` 這類已知借來的名稱排除。

## Finding 6:`savedstate-bang` 的名稱白名單漏掉 `savedState` 與 `state`
引句:「regex: '^(\w+\.)*_?(savedStateHandle|stateHandle|handle)$'」
severity: major
blocking: 是
來源:修補引入

重現:
```kotlin
class S1(private val savedState: SavedStateHandle, val state: SavedStateHandle) : ViewModel() {
  val a = savedState.get<String>("id")!!
  val b = savedState["id"]!!
  val c = state.get<String>("id")!!
}
```
- 舊規則:`savedState` 兩行都報。
- 新規則:三行都不報。
- `private val savedState: SavedStateHandle` 是官方範例與社群慣用名,卻被排除。
- 修掉的誤報 `handlers["x"]!!` 確實消失了。
- 建議:名單加上 `savedState`、`state`,或改成辨識 `SavedStateHandle` 型別宣告。

## Finding 7:`(?i)\w*(Main|Dispatcher|Coroutine)\w*Rule` 把 `mainActivityRule` 當成換 Main 的 Rule
引句:「regex: '(?i)\w*(Main|Dispatcher|Coroutine)\w*Rule'」
severity: minor
blocking: 否
來源:修補引入

重現:
```kotlin
class VmCTest {
  @get:Rule val mainActivityRule = ActivityScenarioRule(MainActivity::class.java)
  val d1 = StandardTestDispatcher()
  val d2 = StandardTestDispatcher()
}
```
- `kt-test-multiple-schedulers` 因為 `(?i)` 把 `mainActivityRule` 認成換 Main 的 Rule,所以不報。舊規則報。
- `MainActivityTestRule`、`MainLooperRule` 這類 Espresso 常見名稱同樣中招。
- 建議:拿掉 `(?i)`,或要求名稱含 `Dispatcher` 或 `CoroutineRule`,不要單靠 `Main`。

## Finding 8:類別裡有任何 SupervisorJob 屬性,就讓其他不用它的 scope 放行
引句:「# SupervisorJob 先存進同類別的屬性再組 scope」
severity: minor
blocking: 否
來源:修補引入

重現:
```kotlin
class S {
  private val job = SupervisorJob()
  val scope = CoroutineScope(Dispatchers.IO)   // 沒用 job,卻不報
}
```
- 舊規則:`scope` 這行報。
- 新規則:不報。
- 建議:要求該 scope 的引數裡引用到那個屬性名。

## Finding 9:SQL 規則的 DDL 豁免太寬,三引號與 DDL 寫法也不一致
引句:「regex: '(?i)^"\s*(PRAGMA|CREATE|DROP|ALTER)\b'」
severity: minor
blocking: 否
來源:修補引入

重現:
```kotlin
db.execSQL("CREATE TABLE a AS SELECT * FROM b WHERE id='$id'")        // 不報,WHERE 的值其實可以綁定參數
db.execSQL("""
   CREATE TABLE z AS SELECT * FROM y WHERE a='$id'""")                // 三引號開頭不匹配 ^"\s*,照報
```
- `CREATE TABLE … AS SELECT … WHERE 值` 的注入可以用 `?` 綁定,卻被整句豁免。
- 同一種寫法,單引號字串不報、三引號字串報,不一致。
- 另外 `query` 只認名稱含 `db` 或 `database` 的接收者,`sqlite.query`、`conn.query` 都漏掉。
- 建議:豁免只放行 `PRAGMA` 與 `DROP`/`CREATE` 後不含 `SELECT`/`WHERE` 的 DDL,並同樣處理 `"""`。

## Finding 10:DataStore 的 runCatching 豁免讓延遲 Flow 的錯誤漏掉
引句:「- pattern: $Y.runCatching { $$$ }」
severity: minor
blocking: 否
來源:修補引入

重現:
```kotlin
val flow = runCatching { dataStore.data.map { it[K] } }.getOrNull()               // 不報
fun h() { runCatching { viewModelScope.launch { dataStore.data.collect { } } } }  // 不報
```
- `map`(以及 `launch` 裡的 `collect`)只是建立或排程流,IOException 發生在稍後收集時,`runCatching` 根本接不到。
- 這兩行在舊規則下都報。
- `try` 的豁免(上輪就有)有同樣的洞。
- 建議:`runCatching` 豁免只留 `first()`、`firstOrNull()` 這類在區塊內就收集完的終端操作。

## Finding 11:事件包裝類與事件 Channel 的辨識名稱太窄
引句:「regex: (Single|Event|Once|Consumable)」
severity: minor
blocking: 否
來源:修補引入

重現(全部不報):
```kotlin
class OneShotLiveData<T> : MutableLiveData<T>()
private val _ev = Channel<Int>()
```
- 舊規則兩者都報。
- `OneShot`、`UnPeek`、`Action` 這類事件包裝名稱漏掉。
- `_ev`、`_trigger`、`_actions` 等事件 Channel 屬性名也漏掉。
- 這是用名稱換掉 FP 的取捨。建議至少補 `OneShot|Action|UnPeek`,並說明 Channel 辨識的名稱邊界。

## Finding 12:Room `@Entity` 豁免連可變集合欄位也放行
引句:「# Room @Entity 的 var 是框架要的寫法(主鍵回填),不算」
severity: minor
blocking: 否
來源:修補引入

重現:
```kotlin
@Entity
data class Note(@PrimaryKey(autoGenerate = true) var id: Long = 0, val tags: MutableList<String>, val flow: MutableStateFlow<Int>)
```
- 舊規則:`var id`、`tags`、`flow` 三個都報。
- 新規則:整個類別都不報。
- 豁免的理由只涵蓋 `var` 主鍵,卻擴及 `MutableList` 與 `MutableStateFlow` 欄位。
- 建議:Entity 內只放行 `var` 這一支,可變集合分支仍然保留。

## 補充(未成立 finding)
- T35(`@LooperMode(LEGACY)`)從 warning 降到 hint。它是純註解形狀、不需要型別就能判,降級後再也擋不了,請確認這是有意為之。
- `kt-runtest-launch-collect-forever` 只要 runTest 裡有任何 `.cancel()`(甚至是無關的 job)就整支放行,屬於覆核級的已知寬鬆,不開 finding。

總結:6 條 major 都是修補放寬過頭造成的新漏報或新誤報(CO-1 的 Main 判定兩條、Worker retry、Eagerly 註解、asCoroutineDispatcher、savedState 名單),6 條 minor;去重和覆核級搬移本身沒問題。
