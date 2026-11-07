# Kotlin 行為測試範本

型錄 [`checks-catalog.md`](checks-catalog.md) 裡級含 C 的列,是「長相看不出錯、要跑起來才知道」的寫法。這份檔替其中在電腦 JVM 上就跑得動的列放測試範本:每組一節,附「好寫法綠、壞寫法紅」的對照,每一格都在純 JVM Gradle 專案實跑過(結果見驗證紀錄 `Verification/2026-11-06_Android行為測試範本紅綠矩陣實跑`(圖譜))。單源=[[Projects/Android行為測試範本與架構測試_計劃]]。

## 怎麼用

1. 在型錄找到那一列,看「通電批次」欄寫的 `行為測試或正向約束=範本 T<n>`。
2. 到這份檔的 `## T<n>` 那一節。〈依據〉是每列的官方出處;〈依賴〉是要加進 `dependencies { }` 的行(版本跟專案實際解析到的對齊:先跑 `./gradlew :<模組>:dependencies --configuration <變體>RuntimeClasspath` 看,見測試品質標準〈Android 本機單元測試的驗收標準〉「加測試函式庫前看實際版本」)。
3. 照抄〈測試〉與〈假依賴〉,類別名、介面名換成專案自己的;〈假依賴〉放 `src/test`。同組有互斥版本的(標題寫「測試:<版本名>」),照那段程式的情境表態答案只留一個版本。
4. 照抄的測試檔第一行留 `// 起手:kotlin-idioms test-templates T<n>`(之後要數有多少測試照範本起手)。
5. 在自己的專案跑一次,綠了才算;再照「故障證明挑本次需求」那條,把被測程式改成這一節〈壞寫法〉的樣子,確認對應的測試翻成**斷言紅**(不是例外或逾時紅,收證工具只把斷言失敗算成抓到錯)。

〈好寫法〉與〈壞寫法〉是實驗用的被測程式,不是要照抄進專案的東西;它們讓你看清楚這支測試抓的是哪一種錯。

**兩個所有組都適用的坑**(實驗踩到的):

- `backgroundScope` 裡的工作,`advanceUntilIdle()` 不會推:它只推到「前景」沒有工作為止。要讓 `backgroundScope` 裡的協程跑起來,用 `runCurrent()`(只跑現在這一刻的)或 `advanceTimeBy()`。
- Turbine 自己的檢查(`awaitComplete()`、`awaitError()`、`expectNoEvents()`、區塊結束時的 Unconsumed events)失敗時丟 `app.cash.turbine.TurbineAssertionError`;它雖然是 `AssertionError` 的子類別,收證工具 `lumos test-quality` 照型別名判,不算成斷言失敗。要拿來當「抓到錯」的那一步,改用 `awaitEvent()` 或 `cancelAndConsumeRemainingEvents()` 取出事件,再用 `assertEquals`/`assertIs` 比。
- 會丟例外的壞寫法,測試先用 `runCatching { … }` 接住,再用斷言比結果;直接讓例外飛出去,紅的是例外紅,收證不算。

## 實驗專案骨架

照下面兩個檔組一個純 JVM Gradle 專案(Gradle 8.13、JDK 17),把某一組〈依賴〉的行貼進 `dependencies { }`;〈測試〉與〈假依賴〉放 `src/test/kotlin`,那一格的被測程式放 `src/main/kotlin`。被測程式的組法:先放〈好寫法〉的每一段程式(一段一個檔),再把那一格點名的〈好寫法:…〉或〈壞寫法:…〉小節的每一段放進去——開頭宣告同名的那一段換掉,不同名的加上去。

`settings.gradle.kts`:

```kotlin
rootProject.name = "kotlin-idioms-test-templates-lab"
```

`build.gradle.kts`:

```kotlin
plugins {
    kotlin("jvm") version "2.2.21"
    kotlin("plugin.serialization") version "2.2.21"
}

repositories {
    google()       // androidx 套件只發在 Google Maven;只有 mavenCentral() 時 lifecycle 解析失敗
    mavenCentral()
}

kotlin { jvmToolchain(17) }

dependencies {
    testImplementation(kotlin("test"))
    // 各組〈依賴〉的行貼在這裡
}

tasks.test { useJUnit() }
```

## T2 Flow 發射

型錄列:API-8、FLOW-3、FLOW-18、FLOW-20、FLOW-23、FLOW-24、STATE-10。斷言收到哪幾筆、順序、有沒有多的;共享類數上游被執行幾次。

### 依據

- API-8:https://github.com/cashapp/turbine 範例 `flowOf("one", "two").test { assertEquals("one", awaitItem()); awaitComplete() }`;https://developer.android.com/kotlin/flow/test 「The third-party Turbine library offers a convenient API」;型錄 API-8 標準寫法 `flatMapLatest`
- FLOW-3:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/combine.html 「combining the most recently emitted values by each flow」(頁面沒明寫「每個來源都要先發過」;本組實跑是旁證)
- FLOW-18:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/share-in.html 「every time it is collected a fresh connection is established」
- FLOW-20:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/ 「State flow never completes」
- FLOW-23:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/first.html 「Throws NoSuchElementException if the flow was empty」
- FLOW-24:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/ 「the emitted value is immediately lost」
- STATE-10:同 FLOW-20 那頁「suppress emission of the values to collectors when new value is equal」

### 依賴

```kotlin
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
implementation("androidx.lifecycle:lifecycle-viewmodel:2.9.4")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
testImplementation("app.cash.turbine:turbine:1.2.1")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T2
import app.cash.turbine.test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class FlowEmissionTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    // API-8:慢的舊查詢不能蓋掉新的結果,也不能晚一點冒出來
    @Test
    fun latest_query_wins() = runTest {
        val vm = SearchViewModel(FakeSearchRepository())
        vm.results.test {
            assertEquals(emptyList(), awaitItem())
            vm.onQueryChange("a")
            runCurrent()   // 慢的舊查詢先出發
            vm.onQueryChange("ab")
            advanceUntilIdle()
            assertEquals(listOf("ab:1"), awaitItem())
            // 不用 expectNoEvents():它失敗丟 TurbineAssertionError,收證不算斷言失敗
            assertEquals(emptyList(), cancelAndConsumeRemainingEvents())
        }
    }

    // FLOW-3:有來源一直不發,畫面也要從 Loading 走到 Ready
    @Test
    fun feed_ready_even_if_prefs_never_emit() = runTest {
        val vm = FeedViewModel(FakeFeedRepository(), SilentPrefsRepository())
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { vm.state.collect {} }
        assertEquals(FeedState.Loading, vm.state.value)
        advanceUntilIdle()
        assertEquals(FeedState.Ready(listOf("a"), compact = false), vm.state.value)
    }

    // FLOW-18:兩個收集者共用一次上游
    @Test
    fun two_collectors_share_one_fetch() = runTest {
        val api = FakePriceApi()
        val repo = PriceRepository(api, backgroundScope)
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { repo.price.collect {} }
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { repo.price.collect {} }
        runCurrent()   // shareIn 開在 backgroundScope,advanceUntilIdle() 不推
        assertEquals(1, api.calls, "上游被執行 ${api.calls} 次")
    }

    // FLOW-20:等熱流某個值之後要做的事,真的有做
    @Test
    fun code_after_login_runs() = runTest {
        val session = MutableStateFlow<String?>(null)
        val greeter = SessionGreeter(session)
        backgroundScope.launch { greeter.greetAfterLogin() }
        session.value = "Ada"
        runCurrent()
        assertEquals("歡迎 Ada", greeter.greeting)
    }

    // FLOW-23:空流回 null,不丟例外;壞寫法的例外用 runCatching 接住
    @Test
    fun missing_user_returns_null() = runTest {
        val r = runCatching { UserFinder(FakeUserRepository()).name("404") }
        assertTrue(r.isSuccess, "查不到要回 null,實際丟了:${r.exceptionOrNull()}")
        assertNull(r.getOrNull())
    }

    // FLOW-24:畫面晚一點才開始收,第一個事件也要收到
    @Test
    fun late_collector_still_gets_welcome() = runTest {
        val vm = WelcomeViewModel()
        advanceUntilIdle()
        val got = mutableListOf<String>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { vm.events.toList(got) }
        runCurrent()
        assertEquals(listOf("歡迎回來"), got)
    }

    // STATE-10:同一則錯誤連發兩次,畫面收到兩個不同 id
    @Test
    fun same_error_twice_shows_twice() = runTest {
        val vm = FormViewModel(FailingFormRepository())
        val seen = mutableListOf<FormState>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { vm.state.toList(seen) }
        vm.save()
        advanceUntilIdle()
        vm.save()
        advanceUntilIdle()
        val messages = seen.mapNotNull { it.message }
        assertEquals(2, messages.map { it.id }.distinct().size, "畫面收到的訊息:$messages")
    }
}
```

### 假依賴

```kotlin
import java.io.IOException
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.emptyFlow
import kotlinx.coroutines.flow.flowOf

class FakeSearchRepository : SearchRepository {
    override suspend fun search(query: String): List<String> {
        delay(if (query.length == 1) 1_000 else 100)   // 舊的短查詢比較慢
        return listOf("$query:1")
    }
}

class FakeFeedRepository : FeedRepository {
    override val items = MutableStateFlow(listOf("a"))
}

class SilentPrefsRepository : PrefsRepository {
    override val compactMode = MutableSharedFlow<Boolean>()   // 設定還沒讀出來:一筆都不發
}

class FakePriceApi : PriceApi {
    var calls = 0
    override suspend fun fetch(): Int { calls++; return 100 }
}

class FakeUserRepository : UserRepository {
    override fun find(id: String): Flow<String> = if (id == "1") flowOf("Ada") else emptyFlow()
}

class FailingFormRepository : FormRepository {
    override suspend fun save() { throw IOException("網路失敗") }
}
```

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.rules.TestWatcher
import org.junit.runner.Description

// 同 T0;範本一律明傳 StandardTestDispatcher()
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = UnconfinedTestDispatcher(),
) : TestWatcher() {
    override fun starting(description: Description) = Dispatchers.setMain(testDispatcher)
    override fun finished(description: Description) = Dispatchers.resetMain()
}
```

### 好寫法

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.stateIn

interface SearchRepository {
    suspend fun search(query: String): List<String>
}

@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val query = MutableStateFlow("")

    val results: StateFlow<List<String>> = query
        .flatMapLatest { q -> if (q.isEmpty()) flowOf(emptyList()) else flow { emit(repo.search(q)) } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    fun onQueryChange(q: String) {
        query.value = q
    }
}
```

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.onStart
import kotlinx.coroutines.flow.stateIn

interface FeedRepository {
    val items: Flow<List<String>>
}

interface PrefsRepository {
    val compactMode: Flow<Boolean>
}

sealed interface FeedState {
    data object Loading : FeedState
    data class Ready(val items: List<String>, val compact: Boolean) : FeedState
}

class FeedViewModel(feed: FeedRepository, prefs: PrefsRepository) : ViewModel() {
    val state: StateFlow<FeedState> =
        combine(feed.items, prefs.compactMode.onStart { emit(false) }) { items, compact ->
            FeedState.Ready(items, compact)
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), FeedState.Loading)
}
```

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.shareIn

interface PriceApi {
    suspend fun fetch(): Int
}

class PriceRepository(private val api: PriceApi, scope: CoroutineScope) {
    val price: Flow<Int> = flow { emit(api.fetch()) }
        .shareIn(scope, SharingStarted.WhileSubscribed(5_000), replay = 1)
}
```

```kotlin
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first

class SessionGreeter(private val session: StateFlow<String?>) {
    var greeting: String? = null
        private set

    suspend fun greetAfterLogin() {
        val user = session.first { it != null }
        greeting = "歡迎 $user"
    }
}
```

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull

interface UserRepository {
    fun find(id: String): Flow<String>
}

class UserFinder(private val repo: UserRepository) {
    suspend fun name(id: String): String? = repo.find(id).firstOrNull()
}
```

```kotlin
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.onSubscription

class WelcomeViewModel : ViewModel() {
    private val _events = MutableSharedFlow<String>()
    val events: Flow<String> = _events.onSubscription { emit("歡迎回來") }   // 每個收集者訂閱時補發
}
```

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import java.io.IOException
import java.util.UUID
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class UserMessage(val text: String, val id: String = UUID.randomUUID().toString())

data class FormState(val message: UserMessage? = null)

interface FormRepository {
    suspend fun save()
}

class FormViewModel(private val repo: FormRepository) : ViewModel() {
    private val _state = MutableStateFlow(FormState())
    val state: StateFlow<FormState> = _state.asStateFlow()

    fun save() {
        viewModelScope.launch {
            try {
                repo.save()
            } catch (e: IOException) {
                _state.update { it.copy(message = UserMessage("網路失敗")) }   // 每則訊息帶新 id
            }
        }
    }
}
```

### 壞寫法:API-8 flatMapConcat 排隊

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.flatMapConcat
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.stateIn

interface SearchRepository {
    suspend fun search(query: String): List<String>
}

@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val query = MutableStateFlow("")

    val results: StateFlow<List<String>> = query
        .flatMapConcat { q -> if (q.isEmpty()) flowOf(emptyList()) else flow { emit(repo.search(q)) } }   // 壞:舊查詢跑完才輪到新的
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    fun onQueryChange(q: String) {
        query.value = q
    }
}
```

### 壞寫法:API-8 每次 launch 不取消前一個

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

interface SearchRepository {
    suspend fun search(query: String): List<String>
}

class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val _results = MutableStateFlow<List<String>>(emptyList())
    val results: StateFlow<List<String>> = _results.asStateFlow()

    fun onQueryChange(q: String) {
        viewModelScope.launch { _results.value = repo.search(q) }   // 壞:慢的舊查詢晚到,蓋掉新結果
    }
}
```

### 壞寫法:FLOW-3 來源沒有初始值

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn

interface FeedRepository {
    val items: Flow<List<String>>
}

interface PrefsRepository {
    val compactMode: Flow<Boolean>
}

sealed interface FeedState {
    data object Loading : FeedState
    data class Ready(val items: List<String>, val compact: Boolean) : FeedState
}

class FeedViewModel(feed: FeedRepository, prefs: PrefsRepository) : ViewModel() {
    val state: StateFlow<FeedState> =
        combine(feed.items, prefs.compactMode) { items, compact ->   // 壞:compactMode 沒發過,combine 一筆都不發
            FeedState.Ready(items, compact)
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), FeedState.Loading)
}
```

### 壞寫法:FLOW-18 冷流各自收

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

interface PriceApi {
    suspend fun fetch(): Int
}

class PriceRepository(private val api: PriceApi, scope: CoroutineScope) {
    val price: Flow<Int> = flow { emit(api.fetch()) }   // 壞:每個收集者各打一次
}
```

### 壞寫法:FLOW-20 collect 之後寫程式

```kotlin
import kotlinx.coroutines.flow.StateFlow

class SessionGreeter(private val session: StateFlow<String?>) {
    var greeting: String? = null
        private set

    suspend fun greetAfterLogin() {
        var user: String? = null
        session.collect { if (it != null) user = it }
        greeting = "歡迎 $user"   // 壞:StateFlow 永不結束,這行永遠走不到
    }
}
```

### 壞寫法:FLOW-23 空流用 first()

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first

interface UserRepository {
    fun find(id: String): Flow<String>
}

class UserFinder(private val repo: UserRepository) {
    suspend fun name(id: String): String? = repo.find(id).first()   // 壞:空流丟 NoSuchElementException
}
```

### 壞寫法:FLOW-24 沒訂閱者就 emit

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.launch

class WelcomeViewModel : ViewModel() {
    private val _events = MutableSharedFlow<String>()
    val events: Flow<String> = _events

    init {
        viewModelScope.launch { _events.emit("歡迎回來") }   // 壞:畫面還沒開始收,值直接丟掉
    }
}
```

### 壞寫法:STATE-10 訊息沒有唯一 id

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import java.io.IOException
import java.util.UUID
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class UserMessage(val text: String, val id: String = UUID.randomUUID().toString())

data class FormState(val message: UserMessage? = null)

interface FormRepository {
    suspend fun save()
}

class FormViewModel(private val repo: FormRepository) : ViewModel() {
    private val _state = MutableStateFlow(FormState())
    val state: StateFlow<FormState> = _state.asStateFlow()

    fun save() {
        viewModelScope.launch {
            try {
                repo.save()
            } catch (e: IOException) {
                // 壞:固定 id,第二次的狀態跟第一次相等,StateFlow 不發
                _state.value = FormState(UserMessage("網路失敗", id = "save-failed"))
            }
        }
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:latest_query_wins、feed_ready_even_if_prefs_never_emit、two_collectors_share_one_fetch、code_after_login_runs、missing_user_returns_null、late_collector_still_gets_welcome、same_error_twice_shows_twice |
| 測試 | 壞寫法:API-8 flatMapConcat 排隊 | latest_query_wins 斷言紅「expected:<[ab:1]> but was:<[a:1]>」;其他綠 |
| 測試 | 壞寫法:API-8 每次 launch 不取消前一個 | latest_query_wins 斷言紅「Item([a:1])」;其他綠 |
| 測試 | 壞寫法:FLOW-3 來源沒有初始值 | feed_ready_even_if_prefs_never_emit 斷言紅「but was:<Loading>」;其他綠 |
| 測試 | 壞寫法:FLOW-18 冷流各自收 | two_collectors_share_one_fetch 斷言紅「上游被執行 2 次」;其他綠 |
| 測試 | 壞寫法:FLOW-20 collect 之後寫程式 | code_after_login_runs 斷言紅「expected:<歡迎 Ada> but was:<null>」;其他綠 |
| 測試 | 壞寫法:FLOW-23 空流用 first() | missing_user_returns_null 斷言紅「NoSuchElementException」;其他綠 |
| 測試 | 壞寫法:FLOW-24 沒訂閱者就 emit | late_collector_still_gets_welcome 斷言紅「expected:<[歡迎回來]> but was:<[]>」;其他綠 |
| 測試 | 壞寫法:STATE-10 訊息沒有唯一 id | same_error_twice_shows_twice 斷言紅「expected:<2> but was:<1>」;其他綠 |

## T3 程序被殺還原

型錄列:STATE-6、STATE-26。把第一個 ViewModel 寫進 `SavedStateHandle` 的內容帶到「程序被殺後重建」的第二個 ViewModel,斷言輸入與待處理的 id 還在。

### 依據

- STATE-6、STATE-26:https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate 「These values persist after the process is killed by the system」「create a new instance of SavedStateHandle with the test values it requires and pass it to the ViewModel instance you are testing」
- 純 JVM 可用、`ViewModelScenario.recreate()`:https://developer.android.com/jetpack/androidx/releases/lifecycle 2.9.0「The lifecycle-viewmodel-savedstate module is now KMP compatible including APIs like SavedStateHandle」「A new androidx.lifecycle:lifecycle-viewmodel-testing KMP artifact … testing process death and recreation via recreate()」

### 依賴

```kotlin
implementation("androidx.lifecycle:lifecycle-viewmodel-savedstate:2.9.4")
testImplementation("androidx.lifecycle:lifecycle-viewmodel-testing:2.9.4")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T3
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.viewmodel.testing.viewModelScenario
import kotlin.test.assertEquals
import org.junit.Test

class SearchFormRestoreTest {
    // STATE-6:使用者輸入在程序被殺、重建後還在
    @Test
    fun query_survives_process_death() {
        viewModelScenario { SearchFormViewModel(createSavedStateHandle()) }.use { scenario ->
            scenario.viewModel.onQueryChange("kotlin")
            scenario.recreate()
            assertEquals("kotlin", scenario.viewModel.query.value)
        }
    }

    // STATE-26:開相機前記下的待處理 id,回來時還找得到
    @Test
    fun pending_scan_survives_process_death() {
        viewModelScenario { SearchFormViewModel(createSavedStateHandle()) }.use { scenario ->
            scenario.viewModel.startScan(orderId = "A-42")
            scenario.recreate()
            assertEquals("A-42:QR123", scenario.viewModel.onScanResult("QR123"))
        }
    }
}
```

### 測試:複製 handle 版

```kotlin
// 起手:kotlin-idioms test-templates T3
// 專案的 lifecycle 早於 2.9.0、沒有 lifecycle-viewmodel-testing 時用這版:官方「用測試值建新的 SavedStateHandle」
import androidx.lifecycle.SavedStateHandle
import kotlin.test.assertEquals
import org.junit.Test

class SearchFormRestoreByCopyTest {
    private fun SavedStateHandle.afterProcessDeath() = SavedStateHandle(keys().associateWith { get<Any?>(it) })

    @Test
    fun query_survives_process_death_copy() {
        val handle = SavedStateHandle()
        SearchFormViewModel(handle).onQueryChange("kotlin")
        val restored = SearchFormViewModel(handle.afterProcessDeath())
        assertEquals("kotlin", restored.query.value)
    }

    @Test
    fun pending_scan_survives_process_death_copy() {
        val handle = SavedStateHandle()
        SearchFormViewModel(handle).startScan(orderId = "A-42")
        val restored = SearchFormViewModel(handle.afterProcessDeath())
        assertEquals("A-42:QR123", restored.onScanResult("QR123"))
    }
}
```

### 好寫法

```kotlin
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.StateFlow

class SearchFormViewModel(private val handle: SavedStateHandle) : ViewModel() {
    val query: StateFlow<String> = handle.getStateFlow("query", "")

    fun onQueryChange(q: String) {
        handle["query"] = q
    }

    fun startScan(orderId: String) {
        handle["pendingId"] = orderId
    }

    fun onScanResult(code: String): String? {
        val id = handle.get<String>("pendingId") ?: return null
        handle.remove<String>("pendingId")
        return "$id:$code"
    }
}
```

### 壞寫法:STATE-6 輸入只放記憶體

```kotlin
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class SearchFormViewModel(private val handle: SavedStateHandle) : ViewModel() {
    private val _query = MutableStateFlow("")   // 壞:程序被殺就沒了
    val query: StateFlow<String> = _query.asStateFlow()

    fun onQueryChange(q: String) {
        _query.value = q
    }

    fun startScan(orderId: String) {
        handle["pendingId"] = orderId
    }

    fun onScanResult(code: String): String? {
        val id = handle.get<String>("pendingId") ?: return null
        handle.remove<String>("pendingId")
        return "$id:$code"
    }
}
```

### 壞寫法:STATE-26 待處理 id 放一般欄位

```kotlin
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.StateFlow

class SearchFormViewModel(private val handle: SavedStateHandle) : ViewModel() {
    val query: StateFlow<String> = handle.getStateFlow("query", "")
    private var pendingId: String? = null   // 壞:開相機時程序被殺,回來找不到

    fun onQueryChange(q: String) {
        handle["query"] = q
    }

    fun startScan(orderId: String) {
        pendingId = orderId
    }

    fun onScanResult(code: String): String? {
        val id = pendingId ?: return null
        pendingId = null
        return "$id:$code"
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:query_survives_process_death、pending_scan_survives_process_death |
| 測試 | 壞寫法:STATE-6 輸入只放記憶體 | query_survives_process_death 斷言紅「expected:<[kotlin]> but was:<[]>」;其他綠 |
| 測試 | 壞寫法:STATE-26 待處理 id 放一般欄位 | pending_scan_survives_process_death 斷言紅「expected:<A-42:QR123> but was:<null>」;其他綠 |
| 測試:複製 handle 版 | 好寫法 | 全綠:query_survives_process_death_copy、pending_scan_survives_process_death_copy |
| 測試:複製 handle 版 | 壞寫法:STATE-6 輸入只放記憶體 | query_survives_process_death_copy 斷言紅「expected:<[kotlin]> but was:<[]>」;其他綠 |
| 測試:複製 handle 版 | 壞寫法:STATE-26 待處理 id 放一般欄位 | pending_scan_survives_process_death_copy 斷言紅「expected:<A-42:QR123> but was:<null>」;其他綠 |

## T4 HTTP 邊界

型錄列:API-21、API-26。真的 OkHttp/Retrofit 打本機 MockWebServer。MockWebServer 照專案實際解析到的 OkHttp 主版本挑:OkHttp 4 用〈依賴:OkHttp 4〉與〈測試:OkHttp 4〉,OkHttp 5 用〈依賴:OkHttp 5〉與〈測試:OkHttp 5〉,兩份測試只差 import 與排回應的寫法。不要讓 OkHttp 4 的專案配 `mockwebserver3`:Gradle 會在測試的類別路徑上默默把 OkHttp 升成 5(測試綠,但測的不是正式用的版本);用 `strictly` 釘住 4.12.0 時每支測試都 `NoClassDefFoundError: okhttp3/internal/_UtilJvmKt`(實驗實測)。走真的 socket,不在 `runTest` 的虛擬時間裡用 `withTimeout`(虛擬時間遇到真實 I/O 會直接跳到逾時點);要等真實時間就包進 `withContext(Dispatchers.Default)`。

### 依據

- MockWebServer:https://github.com/square/okhttp/tree/master/mockwebserver(README 的依賴行 `com.squareup.okhttp3:mockwebserver3`;OkHttp 4 對應的是 `com.squareup.okhttp3:mockwebserver`,套件 `okhttp3.mockwebserver`)
- API-21:OkHttp `Authenticator` KDoc「Returns null if the challenge cannot be satisfied」,範例 `while ((response = response.priorResponse()) != null)` 與「Give up, we've already failed to authenticate.」(https://square.github.io/okhttp/5.x/okhttp/okhttp3/-authenticator/)
- API-26:Retrofit 對 204/205 不呼叫轉換器、body 是 null;型錄 API-26 標準寫法 `Response<Unit>`(出處不全)

### 依賴:OkHttp 4

```kotlin
implementation("com.squareup.okhttp3:okhttp:4.12.0")
implementation("com.squareup.retrofit2:retrofit:3.0.0")
implementation("com.squareup.retrofit2:converter-kotlinx-serialization:3.0.0")
implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0")
testImplementation("com.squareup.okhttp3:mockwebserver:4.12.0")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

### 依賴:OkHttp 5

```kotlin
implementation("com.squareup.okhttp3:okhttp:5.5.1")
implementation("com.squareup.retrofit2:retrofit:3.0.0")
implementation("com.squareup.retrofit2:converter-kotlinx-serialization:3.0.0")
implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0")
testImplementation("com.squareup.okhttp3:mockwebserver3:5.5.1")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

### 測試:OkHttp 4

```kotlin
// 起手:kotlin-idioms test-templates T4
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

class HttpBoundaryTest {
    private val server = MockWebServer()

    @After
    fun tearDown() = server.shutdown()

    // API-21:權杖刷新有上限;壞寫法一路重試到 OkHttp 的追隨上限丟 ProtocolException,用 runCatching 接住
    @Test
    fun refresh_gives_up_after_three_tries() {
        repeat(25) { server.enqueue(MockResponse().setResponseCode(401)) }
        val client = OkHttpClient.Builder().authenticator(TokenAuthenticator(FakeTokenStore())).build()
        val r = runCatching {
            client.newCall(Request.Builder().url(server.url("/me")).build()).execute().use { it.code }
        }
        assertTrue(server.requestCount <= 3, "打了 ${server.requestCount} 次才停,結果:$r")
        assertEquals(401, r.getOrNull())
    }

    // API-26:204 沒有 body 也算成功
    @Test
    fun delete_204_is_success() = runTest {
        server.enqueue(MockResponse().setResponseCode(204))
        val service = Retrofit.Builder()
            .baseUrl(server.url("/"))
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(CartService::class.java)
        val r = runCatching { CartRepository(service).remove("42") }
        assertEquals(true, r.getOrNull(), "204 要算成功,實際:$r")
    }
}
```

### 測試:OkHttp 5

```kotlin
// 起手:kotlin-idioms test-templates T4
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.Json
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import org.junit.After
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

class HttpBoundaryTest {
    private val server = MockWebServer()

    @Before
    fun setUp() = server.start()

    @After
    fun tearDown() = server.close()

    // API-21:權杖刷新有上限;壞寫法一路重試到 OkHttp 的追隨上限丟 ProtocolException,用 runCatching 接住
    @Test
    fun refresh_gives_up_after_three_tries() {
        repeat(25) { server.enqueue(MockResponse.Builder().code(401).build()) }
        val client = OkHttpClient.Builder().authenticator(TokenAuthenticator(FakeTokenStore())).build()
        val r = runCatching {
            client.newCall(Request.Builder().url(server.url("/me")).build()).execute().use { it.code }
        }
        assertTrue(server.requestCount <= 3, "打了 ${server.requestCount} 次才停,結果:$r")
        assertEquals(401, r.getOrNull())
    }

    // API-26:204 沒有 body 也算成功
    @Test
    fun delete_204_is_success() = runTest {
        server.enqueue(MockResponse.Builder().code(204).build())
        val service = Retrofit.Builder()
            .baseUrl(server.url("/"))
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(CartService::class.java)
        val r = runCatching { CartRepository(service).remove("42") }
        assertEquals(true, r.getOrNull(), "204 要算成功,實際:$r")
    }
}
```

### 假依賴

```kotlin
class FakeTokenStore : TokenStore {
    var refreshes = 0
    override fun refresh(): String { refreshes++; return "token-$refreshes" }
}
```

### 好寫法

```kotlin
import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

interface TokenStore {
    fun refresh(): String?
}

class TokenAuthenticator(private val tokens: TokenStore) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        if (response.tries() >= MAX_TRIES) return null   // 有上限:放棄,讓 401 回到呼叫端
        val token = tokens.refresh() ?: return null
        return response.request.newBuilder().header("Authorization", "Bearer $token").build()
    }

    private fun Response.tries(): Int = generateSequence(this) { it.priorResponse }.count()

    companion object {
        const val MAX_TRIES = 3
    }
}
```

```kotlin
import kotlinx.serialization.Serializable
import retrofit2.Response
import retrofit2.http.DELETE
import retrofit2.http.Path

@Serializable
data class CartDto(val id: String)

interface CartService {
    @DELETE("cart/{id}")
    suspend fun remove(@Path("id") id: String): Response<Unit>
}

class CartRepository(private val service: CartService) {
    suspend fun remove(id: String): Boolean = service.remove(id).isSuccessful
}
```

### 壞寫法:API-21 刷新沒有上限

```kotlin
import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

interface TokenStore {
    fun refresh(): String?
}

class TokenAuthenticator(private val tokens: TokenStore) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        val token = tokens.refresh() ?: return null   // 壞:每次 401 都刷新重送,不數次數
        return response.request.newBuilder().header("Authorization", "Bearer $token").build()
    }
}
```

### 壞寫法:API-26 204 宣告成有 body

```kotlin
import kotlinx.serialization.Serializable
import retrofit2.http.DELETE
import retrofit2.http.Path

@Serializable
data class CartDto(val id: String)

interface CartService {
    @DELETE("cart/{id}")
    suspend fun remove(@Path("id") id: String): CartDto   // 壞:伺服器回 204 沒有 body
}

class CartRepository(private val service: CartService) {
    suspend fun remove(id: String): Boolean {
        service.remove(id)
        return true
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試:OkHttp 4 | 好寫法 | 全綠:refresh_gives_up_after_three_tries、delete_204_is_success |
| 測試:OkHttp 4 | 壞寫法:API-21 刷新沒有上限 | refresh_gives_up_after_three_tries 斷言紅「打了 21 次才停」;其他綠 |
| 測試:OkHttp 4 | 壞寫法:API-26 204 宣告成有 body | delete_204_is_success 斷言紅「204 要算成功」;其他綠 |
| 測試:OkHttp 5 | 好寫法 | 全綠:refresh_gives_up_after_three_tries、delete_204_is_success |
| 測試:OkHttp 5 | 壞寫法:API-21 刷新沒有上限 | refresh_gives_up_after_three_tries 斷言紅「打了 21 次才停」;其他綠 |
| 測試:OkHttp 5 | 壞寫法:API-26 204 宣告成有 body | delete_204_is_success 斷言紅「204 要算成功」;其他綠 |

## T5 序列化契約

型錄列:DATA-72、DATA-73、DATA-74。用專案正式的 `Json {}` 設定物件(範本用 `AppJson` 佔位)解碼、編碼伺服器可能回的 JSON;不在測試裡另建一個 `Json`,不然測的不是正式設定。

### 依據

- DATA-72、DATA-73:https://kotlinlang.org/docs/serialization-json-configuration.html coerceInputValues 套用於「null inputs for non-nullable types」「unknown values for enums」
- DATA-74:同上頁「the JSON encoder omits default property values」(`encodeDefaults` 預設關);`@EncodeDefault` 讓單一欄位照送
- 依賴版本:https://github.com/Kotlin/kotlinx.serialization/releases 1.9.0「This release updates Kotlin version to 2.2.0」、1.12.0「This release is based on Kotlin 2.4.10」

### 依賴

```kotlin
// 1.9.0 對 Kotlin 2.2;1.10 起要 Kotlin 2.3、1.12.0 要 2.4.10(Kotlin 2.2.21 實測編不過),跟專案的 Kotlin 版本對齊
implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T5
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.serialization.encodeToString
import org.junit.Test

class SerializationContractTest {
    // DATA-72:缺欄位或 null 照樣解得出來;壞寫法丟 MissingFieldException,用 runCatching 接住
    // JSON 帶上 status:只讓 name 缺,DATA-73 的壞寫法才不會連這支一起紅
    @Test
    fun missing_or_null_name_still_decodes() {
        val r = runCatching { AppJson.decodeFromString<List<UserDto>>("""[{"id":"1","status":"ACTIVE"},{"id":"2","name":null,"status":"ACTIVE"}]""") }
        assertTrue(r.isSuccess, "解碼失敗:${r.exceptionOrNull()}")
        assertEquals(listOf("", ""), r.getOrThrow().map { it.name })
    }

    // DATA-73:伺服器新增的列舉值變成 UNKNOWN,不讓整份解碼失敗
    @Test
    fun unknown_status_becomes_unknown() {
        val r = runCatching { AppJson.decodeFromString<UserDto>("""{"id":"1","name":"Ada","status":"SUSPENDED"}""") }
        assertTrue(r.isSuccess, "解碼失敗:${r.exceptionOrNull()}")
        assertEquals("UNKNOWN", r.getOrThrow().status.name)
    }

    // DATA-74:等於預設值的必填欄位也要送出去
    @Test
    fun default_quantity_is_sent() {
        val body = AppJson.encodeToString(OrderRequest(item = "pen"))
        assertTrue("\"quantity\":1" in body, "送出去的 JSON 少了 quantity:$body")
    }
}
```

### 好寫法

```kotlin
import kotlinx.serialization.json.Json

// 專案正式的 Json 設定;測試讀這一個
val AppJson = Json {
    ignoreUnknownKeys = true
    coerceInputValues = true
}
```

```kotlin
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    val id: String,
    val name: String = "",
    val status: Status = Status.UNKNOWN,
)

@Serializable
enum class Status { ACTIVE, BANNED, UNKNOWN }
```

```kotlin
import kotlinx.serialization.EncodeDefault
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.Serializable

@OptIn(ExperimentalSerializationApi::class)
@Serializable
data class OrderRequest(
    val item: String,
    @EncodeDefault val quantity: Int = 1,
)
```

### 壞寫法:DATA-72 非可空欄位沒預設值

```kotlin
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    val id: String,
    val name: String,   // 壞:伺服器缺欄位或回 null 就整份失敗
    val status: Status = Status.UNKNOWN,
)

@Serializable
enum class Status { ACTIVE, BANNED, UNKNOWN }
```

### 壞寫法:DATA-73 列舉沒有 UNKNOWN

```kotlin
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    val id: String,
    val name: String = "",
    val status: Status,   // 壞:伺服器多一個值,舊版 App 解不出來
)

@Serializable
enum class Status { ACTIVE, BANNED }
```

### 壞寫法:DATA-74 預設值沒送出去

```kotlin
import kotlinx.serialization.Serializable

@Serializable
data class OrderRequest(
    val item: String,
    val quantity: Int = 1,   // 壞:encodeDefaults 預設關,等於預設值就被省略
)
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:missing_or_null_name_still_decodes、unknown_status_becomes_unknown、default_quantity_is_sent |
| 測試 | 壞寫法:DATA-72 非可空欄位沒預設值 | missing_or_null_name_still_decodes 斷言紅「MissingFieldException」;其他綠 |
| 測試 | 壞寫法:DATA-73 列舉沒有 UNKNOWN | unknown_status_becomes_unknown 斷言紅「SerializationException」;其他綠 |
| 測試 | 壞寫法:DATA-74 預設值沒送出去 | default_quantity_is_sent 斷言紅「少了 quantity」;其他綠 |
