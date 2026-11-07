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
- Turbine 自己的檢查(`awaitItem()`、`awaitEvent()`、`awaitComplete()`、`awaitError()`、`skipItems()`、`expectNoEvents()`、`expectMostRecentItem()`、`ensureAllEventsConsumed()`、`takeItem()`/`takeEvent()`/`takeComplete()`/`takeError()`,以及 `test {}` 區塊結束時的 Unconsumed events;依 Turbine 1.2.1 原始碼 `channel.kt`、`ReceiveTurbine.kt`、`flow.kt` 列全)失敗時丟 `app.cash.turbine.TurbineAssertionError`;它雖然是 `AssertionError` 的子類別,收證工具 `lumos test-quality` 照型別名判,不算成斷言失敗。`awaitItem()`、`awaitEvent()` 等不到值時,3 秒後也丟同一個型別(`No value produced in 3s`)——所以「壞寫法少發一筆」也不會被算成抓到錯。範本的做法:每個 `test {}` 區塊先把虛擬時間推到靜止(`advanceUntilIdle()`;被測的流會掛起時少了這步,事件還沒發完就被取走,正確程式也會紅),再用 `cancelAndConsumeRemainingEvents()` 一次取出全部事件,用 `assertEquals`/`assertIs` 比。
- 有限的冷流(例如 `flow { emit(a); emit(b) }`)收完值之後還有一個 `Complete` 事件:型錄 TEST-18 寫的「結尾 `expectNoEvents()`」在這種流上對正確程式也會紅(`Expected no events but found Complete`);有限流要把 `Event.Complete` 當成最後一筆一起比,`expectNoEvents()` 只用在熱流。
- 範本的狀態類別用 `data object`(Kotlin 1.9 起才有);專案的 Kotlin 早於 1.9 時改成 `object` 並自己寫 `toString()`,不然斷言失敗訊息只印雜湊值。
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

## T0 測試骨架守則

型錄列:TEST-4、TEST-5、TEST-6、TEST-7、TEST-9、TEST-14、TEST-17、TEST-18、TEST-19、TEST-20。矩陣是「好測試 vs 壞測試 × 正確程式 vs 埋錯程式」:〈測試〉對正確程式全綠、對埋錯程式只紅點名那支;〈壞測試:…〉示範錯的測試寫法對正確程式錯紅、卡住或錯綠。

### 依據

- TEST-4、TEST-14:https://developer.android.com/kotlin/coroutines/test 「advanceUntilIdle: Runs all other coroutines on the scheduler until there is nothing left in the queue. This is a good default choice」「this doesn't mean that it'll run them to completion eagerly」
- TEST-9:同上頁「In tests, replace real dispatchers with instances of TestDispatchers」
- `MainDispatcherRule` 明傳 `StandardTestDispatcher()`:nowinandroid `core/testing` 的同名類別預設 `UnconfinedTestDispatcher()`(https://github.com/android/nowinandroid/blob/main/core/testing/src/main/kotlin/com/google/samples/apps/nowinandroid/core/testing/util/MainDispatcherRule.kt),照抄預設會讓〈壞測試:TEST-4 規則用預設 Unconfined〉照綠;測試品質標準〈Android 本機單元測試的驗收標準〉「預設用 `StandardTestDispatcher`」
- TEST-5、TEST-17:https://developer.android.com/kotlin/flow/test 「backgroundScope … ensures that the coroutine gets cancelled before the end of the test」
- TEST-6:同上頁「there must be at least one collector present during the test」
- TEST-7:同上頁「we generally recommend treating StateFlow as a data holder and asserting on its value」
- TEST-18、TEST-19、TEST-20:https://github.com/cashapp/turbine 「Failing to consume all events before the end of a flow-based Turbine's validation block will fail your test」;型錄 TEST-18 標準寫法「逐一 `awaitItem()`,結尾 `expectNoEvents()` 或明確 `cancelAndIgnoreRemainingEvents()`」

### 依賴

```kotlin
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
implementation("androidx.lifecycle:lifecycle-viewmodel:2.9.4")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
testImplementation("app.cash.turbine:turbine:1.2.1")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T0
import app.cash.turbine.Event
import app.cash.turbine.test
import java.io.IOException
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ProfileViewModelTest {
    // 先宣告:其他屬性建構時才拿得到同一個測試排程器;明傳 Standard,新協程排隊、要推進才跑
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    private val repo = FakeProfileRepository()

    // TEST-4、TEST-7:launch 之後先推進,再斷言 StateFlow 的最終 value
    @Test
    fun load_then_advance_shows_loaded() = runTest {
        val vm = ProfileViewModel(repo)
        vm.load()
        advanceUntilIdle()
        assertEquals(ProfileState.Loaded("Ada"), vm.state.value)
    }

    // TEST-5、TEST-6:stateIn(WhileSubscribed) 要有收集者;永不結束的收集放 backgroundScope
    @Test
    fun score_follows_repository_while_collected() = runTest {
        val vm = ProfileViewModel(repo)
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { vm.score.collect {} }
        runCurrent()   // 讓 stateIn 先接上上游
        repo.scores.value = 42
        advanceUntilIdle()
        assertEquals(42, vm.score.value)
        repo.scores.value = 43   // 收集開始之後再改一次:只取一次快照、不跟著上游的寫法在這裡露餡
        advanceUntilIdle()
        assertEquals(43, vm.score.value)
    }

    // TEST-17、TEST-20:熱流用 Turbine 收,第一筆是初始值;TEST-7 最後只比最新的值
    // 推到靜止後一次取出全部事件再斷言:awaitItem() 等不到值時丟 TurbineAssertionError,收證不算斷言
    @Test
    fun state_starts_initial_then_loaded() = runTest {
        val vm = ProfileViewModel(repo)
        vm.state.test {
            vm.load()
            advanceUntilIdle()
            val items = cancelAndConsumeRemainingEvents().filterIsInstance<Event.Item<ProfileState>>().map { it.value }
            assertEquals(ProfileState.Initial, items.firstOrNull(), "收到:$items")
            assertEquals(ProfileState.Loaded("Ada"), items.lastOrNull(), "收到:$items")
        }
    }

    // TEST-18:每個值都收掉,有限流連結尾的 Complete 一起比,多一筆少一筆都紅
    // 不用 awaitComplete()/expectNoEvents():失敗丟 TurbineAssertionError,收證工具不算斷言失敗
    @Test
    fun save_emits_saving_then_saved_once() = runTest {
        ProfileViewModel(repo).save("Ada").test {
            advanceUntilIdle()   // 先推到靜止:儲存會掛起時,不推就取會少拿事件
            assertEquals(
                listOf(Event.Item(SaveEvent.Saving), Event.Item(SaveEvent.Saved), Event.Complete),
                cancelAndConsumeRemainingEvents(),
            )
        }
    }

    // TEST-19:錯誤要當成錯誤收,再斷言型別(同上理由不用 awaitError())
    @Test
    fun save_blank_name_reports_error() = runTest {
        ProfileViewModel(repo).save("").test {
            advanceUntilIdle()
            val events = cancelAndConsumeRemainingEvents()
            assertEquals(Event.Item(SaveEvent.Saving), events.firstOrNull(), "事件:$events")
            val end = events.lastOrNull()
            assertIs<Event.Error>(end, "儲存失敗要以錯誤結束,事件:$events")
            assertIs<IOException>(end.throwable)
        }
    }

    // TEST-9、TEST-14:被測物用注入的 scope(這裡是 TestScope 本身),有 delay 就推進後再斷言
    @Test
    fun upload_runs_in_injected_scope() = runTest {
        val api = FakeUploadApi()
        Uploader(this, api).start("a.jpg")
        advanceUntilIdle()
        assertEquals(listOf("a.jpg"), api.uploaded)
    }

    // TEST-9:工作要掛在注入的 scope 上——注入的 scope 結束(例如畫面離開),工作跟著停
    // 只驗上面那支時,自建 scope 卻用 Dispatchers.Main 的寫法照綠(測試把 Main 換成了同一個排程器)
    @Test
    fun upload_stops_when_injected_scope_cancelled() = runTest {
        val api = FakeUploadApi()
        val injected = CoroutineScope(StandardTestDispatcher(testScheduler) + Job())
        Uploader(injected, api).start("a.jpg")
        injected.cancel()
        advanceUntilIdle()
        assertEquals(emptyList(), api.uploaded)
    }
}
```

### 假依賴

```kotlin
import java.io.IOException
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow

class FakeProfileRepository : ProfileRepository {
    override suspend fun loadName(): String = "Ada"   // 不 suspend:「沒推進」的錯只看派發器
    override val scores = MutableStateFlow(0)
    override suspend fun save(name: String) {
        if (name.isBlank()) throw IOException("名字不能空白")
    }
}

class FakeUploadApi : UploadApi {
    val uploaded = mutableListOf<String>()
    override suspend fun upload(file: String) {
        delay(1_000)
        uploaded += file
    }
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

// 形狀照 nowinandroid core/testing 的同名類別;預設值照原檔留 Unconfined,但範本一律明傳 StandardTestDispatcher()
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
import kotlinx.coroutines.flow.Flow

sealed interface ProfileState {
    data object Initial : ProfileState
    data object Loading : ProfileState
    data class Loaded(val name: String) : ProfileState
}

sealed interface SaveEvent {
    data object Saving : SaveEvent
    data object Saved : SaveEvent
}

interface ProfileRepository {
    suspend fun loadName(): String
    val scores: Flow<Int>
    suspend fun save(name: String)
}
```

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    val score: StateFlow<Int> = repo.scores
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    fun load() {
        viewModelScope.launch {
            _state.value = ProfileState.Loading
            _state.value = ProfileState.Loaded(repo.loadName())
        }
    }

    fun save(name: String): Flow<SaveEvent> = flow {
        emit(SaveEvent.Saving)
        repo.save(name)
        emit(SaveEvent.Saved)
    }
}
```

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

interface UploadApi {
    suspend fun upload(file: String)
}

class Uploader(private val scope: CoroutineScope, private val api: UploadApi) {
    fun start(file: String) {
        scope.launch { api.upload(file) }
    }
}
```

### 好寫法:TEST-18 save 會掛起

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    val score: StateFlow<Int> = repo.scores
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    fun load() {
        viewModelScope.launch {
            _state.value = ProfileState.Loading
            _state.value = ProfileState.Loaded(repo.loadName())
        }
    }

    fun save(name: String): Flow<SaveEvent> = flow {
        emit(SaveEvent.Saving)
        delay(100)   // 真的儲存通常會掛起(等網路或磁碟);正確寫法,測試要照綠
        repo.save(name)
        emit(SaveEvent.Saved)
    }
}
```

### 壞寫法:TEST-4 load 停在 Loading

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    val score: StateFlow<Int> = repo.scores
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    fun load() {
        viewModelScope.launch {
            _state.value = ProfileState.Loading
            repo.loadName()   // 壞:拿到結果卻沒寫回狀態
        }
    }

    fun save(name: String): Flow<SaveEvent> = flow {
        emit(SaveEvent.Saving)
        repo.save(name)
        emit(SaveEvent.Saved)
    }
}
```

### 壞寫法:TEST-6 score 沒接上游

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.launch

class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    val score: StateFlow<Int> = MutableStateFlow(0)   // 壞:沒接 repo.scores

    fun load() {
        viewModelScope.launch {
            _state.value = ProfileState.Loading
            _state.value = ProfileState.Loaded(repo.loadName())
        }
    }

    fun save(name: String): Flow<SaveEvent> = flow {
        emit(SaveEvent.Saving)
        repo.save(name)
        emit(SaveEvent.Saved)
    }
}
```

### 壞寫法:TEST-9 自建 scope 用真 dispatcher

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

interface UploadApi {
    suspend fun upload(file: String)
}

class Uploader(scope: CoroutineScope, private val api: UploadApi) {
    private val ownScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)   // 壞:不用注入的 scope

    fun start(file: String) {
        ownScope.launch { api.upload(file) }
    }
}
```

### 壞寫法:TEST-18 Saved 多發一次

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    val score: StateFlow<Int> = repo.scores
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    fun load() {
        viewModelScope.launch {
            _state.value = ProfileState.Loading
            _state.value = ProfileState.Loaded(repo.loadName())
        }
    }

    fun save(name: String): Flow<SaveEvent> = flow {
        emit(SaveEvent.Saving)
        repo.save(name)
        emit(SaveEvent.Saved)
        emit(SaveEvent.Saved)   // 壞:重複通知,畫面會跳兩次「已儲存」
    }
}
```

### 壞寫法:TEST-19 錯誤被吞掉

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    val score: StateFlow<Int> = repo.scores
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    fun load() {
        viewModelScope.launch {
            _state.value = ProfileState.Loading
            _state.value = ProfileState.Loaded(repo.loadName())
        }
    }

    fun save(name: String): Flow<SaveEvent> = flow {
        emit(SaveEvent.Saving)
        repo.save(name)
        emit(SaveEvent.Saved)
    }.catch { }   // 壞:錯誤被吞,畫面以為還在儲存
}
```

### 壞寫法:TEST-6 只取一次快照

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    private val _state = MutableStateFlow<ProfileState>(ProfileState.Initial)
    val state: StateFlow<ProfileState> = _state.asStateFlow()

    val score: StateFlow<Int> = flow { emit(repo.scores.first()) }   // 壞:接了上游,但只取一次就不跟了
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    fun load() {
        viewModelScope.launch {
            _state.value = ProfileState.Loading
            _state.value = ProfileState.Loaded(repo.loadName())
        }
    }

    fun save(name: String): Flow<SaveEvent> = flow {
        emit(SaveEvent.Saving)
        repo.save(name)
        emit(SaveEvent.Saved)
    }
}
```

### 壞寫法:TEST-9 自建 scope 用 Dispatchers.Main

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

interface UploadApi {
    suspend fun upload(file: String)
}

class Uploader(scope: CoroutineScope, private val api: UploadApi) {
    private val ownScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)   // 壞:不用注入的 scope;測試把 Main 換掉了,只驗「有跑」抓不到

    fun start(file: String) {
        ownScope.launch { api.upload(file) }
    }
}
```

### 壞測試:TEST-4 沒推進就斷言

```kotlin
import kotlin.test.assertEquals
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadNoAdvanceTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun load_without_advance() = runTest {
        val vm = ProfileViewModel(FakeProfileRepository())
        vm.load()
        assertEquals(ProfileState.Loaded("Ada"), vm.state.value)   // 壞:launch 還在排隊
    }
}
```

### 壞測試:TEST-4 規則用預設 Unconfined

```kotlin
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadUnconfinedRuleTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()   // 壞:照抄預設 Unconfined,launch 馬上跑完

    @Test
    fun load_without_advance_unconfined_rule() = runTest {
        val vm = ProfileViewModel(FakeProfileRepository())
        vm.load()
        assertEquals(ProfileState.Loaded("Ada"), vm.state.value)
    }
}
```

### 壞測試:TEST-5 熱流收集放一般 launch

```kotlin
import kotlin.test.assertEquals
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadCollectInLaunchTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun collect_state_in_plain_launch() = runTest(timeout = 5.seconds) {
        val vm = ProfileViewModel(FakeProfileRepository())
        val seen = mutableListOf<ProfileState>()
        launch { vm.state.collect { seen += it } }   // 壞:StateFlow 永不結束,runTest 一直等它
        vm.load()
        advanceUntilIdle()
        assertEquals(ProfileState.Loaded("Ada"), seen.last())
    }
}
```

### 壞測試:TEST-6 stateIn 沒收集者

```kotlin
import kotlin.test.assertEquals
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadNoCollectorTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun score_without_collector() = runTest {
        val repo = FakeProfileRepository()
        val vm = ProfileViewModel(repo)
        repo.scores.value = 42
        advanceUntilIdle()
        assertEquals(42, vm.score.value)   // 壞:沒有收集者,stateIn 沒開始
    }
}
```

### 壞測試:TEST-7 逐一比中間值

```kotlin
import kotlin.test.assertEquals
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadEveryIntermediateTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun state_every_intermediate_value() = runTest {
        val vm = ProfileViewModel(FakeProfileRepository())
        val seen = mutableListOf<ProfileState>()
        backgroundScope.launch { vm.state.toList(seen) }   // 收集者在 Standard 派發器上排隊
        vm.load()
        runCurrent()
        // 壞:StateFlow 會合併快速連續的值,中間的 Loading 收不到
        assertEquals(listOf(ProfileState.Initial, ProfileState.Loading, ProfileState.Loaded("Ada")), seen)
    }
}
```

### 壞測試:TEST-9 測試用真 dispatcher

```kotlin
import kotlin.test.assertEquals
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Test

class BadRealDispatcherTest {
    @Test
    fun upload_with_real_dispatcher() = runTest {
        val api = FakeUploadApi()
        Uploader(CoroutineScope(Dispatchers.Default), api).start("a.jpg")   // 壞:工作跑到測試排程器以外
        advanceUntilIdle()
        assertEquals(listOf("a.jpg"), api.uploaded)
    }
}
```

### 壞測試:TEST-14 以為 Unconfined 會跑完

```kotlin
import kotlin.test.assertEquals
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class BadUnconfinedNoAdvanceTest {
    @Test
    fun upload_unconfined_without_advance() = runTest(UnconfinedTestDispatcher()) {
        val api = FakeUploadApi()
        Uploader(this, api).start("a.jpg")
        assertEquals(listOf("a.jpg"), api.uploaded)   // 壞:協程停在 delay,還沒寫進去
    }
}
```

### 壞測試:TEST-17 toList 收熱流

```kotlin
import kotlin.test.assertEquals
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadToListHotFlowTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun state_to_list() = runTest(timeout = 5.seconds) {
        val vm = ProfileViewModel(FakeProfileRepository())
        vm.load()
        val all = vm.state.toList()   // 壞:StateFlow 永不結束,toList 永遠不回來
        assertEquals(ProfileState.Loaded("Ada"), all.last())
    }
}
```

### 壞測試:TEST-18 濫用 cancelAndIgnoreRemainingEvents

```kotlin
import app.cash.turbine.test
import kotlin.test.assertEquals
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadIgnoreRemainingTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun save_ignores_remaining_events() = runTest {
        ProfileViewModel(FakeProfileRepository()).save("Ada").test {
            assertEquals(SaveEvent.Saving, awaitItem())
            assertEquals(SaveEvent.Saved, awaitItem())
            cancelAndIgnoreRemainingEvents()   // 壞:後面多發的事件被吞掉
        }
    }
}
```

### 壞測試:TEST-20 忘了 StateFlow 的初始值

```kotlin
import app.cash.turbine.test
import kotlin.test.assertEquals
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class BadForgetInitialTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun state_forgets_initial_value() = runTest {
        val vm = ProfileViewModel(FakeProfileRepository())
        vm.state.test {
            vm.load()
            advanceUntilIdle()
            assertEquals(ProfileState.Loaded("Ada"), awaitItem())   // 壞:收到的第一筆是 Initial
        }
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:load_then_advance_shows_loaded、score_follows_repository_while_collected、state_starts_initial_then_loaded、save_emits_saving_then_saved_once、save_blank_name_reports_error、upload_runs_in_injected_scope、upload_stops_when_injected_scope_cancelled |
| 測試 | 好寫法:TEST-18 save 會掛起 | 全綠:load_then_advance_shows_loaded、score_follows_repository_while_collected、state_starts_initial_then_loaded、save_emits_saving_then_saved_once、save_blank_name_reports_error、upload_runs_in_injected_scope、upload_stops_when_injected_scope_cancelled |
| 測試 | 壞寫法:TEST-4 load 停在 Loading | load_then_advance_shows_loaded 斷言紅「Loading」;state_starts_initial_then_loaded 斷言紅「Loading」;其他綠 |
| 測試 | 壞寫法:TEST-6 score 沒接上游 | score_follows_repository_while_collected 斷言紅「expected:<42> but was:<0>」;其他綠 |
| 測試 | 壞寫法:TEST-6 只取一次快照 | score_follows_repository_while_collected 斷言紅「expected:<42> but was:<0>」;其他綠 |
| 測試 | 壞寫法:TEST-9 自建 scope 用真 dispatcher | upload_runs_in_injected_scope 斷言紅「expected:<[a.jpg]> but was:<[]>」;其他綠 |
| 測試 | 壞寫法:TEST-9 自建 scope 用 Dispatchers.Main | upload_stops_when_injected_scope_cancelled 斷言紅「expected:<[]> but was:<[a.jpg]>」;其他綠 |
| 測試 | 壞寫法:TEST-18 Saved 多發一次 | save_emits_saving_then_saved_once 斷言紅「Item(Saved), Item(Saved)」;其他綠 |
| 測試 | 壞寫法:TEST-19 錯誤被吞掉 | save_blank_name_reports_error 斷言紅「儲存失敗要以錯誤結束」;其他綠 |
| 壞測試:TEST-4 沒推進就斷言 | 好寫法 | load_without_advance 斷言紅「Initial」 |
| 壞測試:TEST-4 規則用預設 Unconfined | 好寫法 | load_without_advance_unconfined_rule 綠 |
| 壞測試:TEST-5 熱流收集放一般 launch | 好寫法 | collect_state_in_plain_launch 逾時紅 |
| 壞測試:TEST-6 stateIn 沒收集者 | 好寫法 | score_without_collector 斷言紅「expected:<42> but was:<0>」 |
| 壞測試:TEST-7 逐一比中間值 | 好寫法 | state_every_intermediate_value 斷言紅「Loading」 |
| 壞測試:TEST-9 測試用真 dispatcher | 好寫法 | upload_with_real_dispatcher 斷言紅「expected:<[a.jpg]> but was:<[]>」 |
| 壞測試:TEST-14 以為 Unconfined 會跑完 | 好寫法 | upload_unconfined_without_advance 斷言紅「expected:<[a.jpg]> but was:<[]>」 |
| 壞測試:TEST-17 toList 收熱流 | 好寫法 | state_to_list 逾時紅 |
| 壞測試:TEST-18 濫用 cancelAndIgnoreRemainingEvents | 好寫法 | save_ignores_remaining_events 綠 |
| 壞測試:TEST-18 濫用 cancelAndIgnoreRemainingEvents | 壞寫法:TEST-18 Saved 多發一次 | save_ignores_remaining_events 綠 |
| 壞測試:TEST-20 忘了 StateFlow 的初始值 | 好寫法 | state_forgets_initial_value 斷言紅「Initial」 |

讀法:〈壞測試:TEST-4 規則用預設 Unconfined〉對正確程式綠,是「錯綠」——同一支沒推進的測試換成 Standard 就紅,證明 `MainDispatcherRule` 要明傳 `StandardTestDispatcher()`。〈壞測試:TEST-18 …〉對多發一次的壞寫法也綠,是「漏抓」;〈測試〉的 `awaitComplete()` 抓得到。

## T1 虛擬時間

型錄列:API-1、API-4、API-10、API-31、API-32、API-34、FLOW-29、CO-14。假依賴用 `delay` 模擬耗時,`runTest` 跳過 delay 但記下虛擬時間;斷言 `testScheduler.currentTime`、呼叫次數、逾時後的狀態。API-4 的兩個測試版本互斥(一支失敗要不要連坐是業務決定),照那段程式的情境表態答案只留一個;API-10 預設斷言「連點兩次只打一次 API」,後端有冪等鍵時改用〈測試:API-10 冪等鍵版〉。

### 依據

- API-1、API-10、API-31、API-32:https://developer.android.com/kotlin/coroutines/test 「it will automatically skip any delays in coroutines」「advanceTimeBy: Advances virtual time by the given amount」「There should only be one scheduler instance used in a test」
- `testScheduler.currentTime`:`TestCoroutineScheduler` 的成員屬性(要 `@OptIn(ExperimentalCoroutinesApi::class)`);頂層的 `TestScope.currentTime` 是另一個擴充,要另外 import
- API-4:https://kotlinlang.org/docs/exception-handling.html 「a failure or cancellation of a child does not propagate to the supervisor job or its other children」;型錄 API-4 標準寫法(連坐 `coroutineScope`、不連坐 `supervisorScope` 加逐支接住)
- API-10:型錄 API-10 標準寫法 `if (job?.isActive == true) return`(出處不全,範本只驗 ViewModel 層)
- API-31:型錄 API-31 標準寫法「共用 `Deferred` 加 mutex」(出處不全)
- API-32:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html 「when coroutines finish with a CancellationException, the error does not get propagated to the parent」「For ensuring that timeouts are treated as true errors that should cause the parent to fail, use withTimeoutOrNull and check the return value」
- CO-14:同上頁「Cancellation on timeout runs concurrently the code running in the block and may happen at any time, even after the block finishes executing but before the caller gets resumed with the result」「Values returned from withTimeout will typically be lost if the caller is cancelled」;型錄 CO-14 兩種標準寫法(資源在 `withTimeout` 外取得並 `use`,或區塊內 `try { … } finally { close() }`)都要綠,逾時時 `send()` 回成功或失敗由專案表態,測試不驗
- API-34:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-cancellable-continuation/ 「Concurrent invocations of resume methods lead to a IllegalStateException」(頁面沒寫依序 resume 兩次;實跑訊息 `Already resumed` 是旁證)
- FLOW-29:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html 「The lifecycle of the parent [CoroutineScope] cannot end until this coroutine … completes」(`send` 卡住讓父範圍不結束是推論,實跑是旁證)

### 依賴

```kotlin
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
implementation("androidx.lifecycle:lifecycle-viewmodel:2.9.4")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T1
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class VirtualTimeTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    // API-1:兩支各 1 秒,並行總共 1 秒
    @Test
    fun independent_calls_run_in_parallel() = runTest {
        HomeLoader(FakeHomeApi()).load()
        assertEquals(1_000L, testScheduler.currentTime)
    }

    // API-10:連呼兩次只打一次 API
    @Test
    fun double_submit_calls_api_once() = runTest {
        val api = FakeOrderApi()
        val vm = CheckoutViewModel(api)
        vm.submit("A-1")
        vm.submit("A-1")
        advanceUntilIdle()
        assertEquals(1, api.calls.size, "送出 ${api.calls.size} 次:${api.calls}")
    }

    // API-31:三個呼叫端同時 refresh,只打一次網路、拿到同一份
    @Test
    fun concurrent_refresh_hits_network_once() = runTest {
        val api = FakeConfigApi()
        val repo = ConfigRepository(api, backgroundScope)
        val results = List(3) { async { repo.refresh() } }.awaitAll()
        assertEquals(1, api.calls, "打了 ${api.calls} 次網路")
        assertEquals(1, results.toSet().size, "三個呼叫端拿到不同結果:$results")
        repo.refresh()   // 第一批結束之後再要一次:合併的是「同時在途」的請求,不是永久快取
        assertEquals(2, api.calls, "第一批結束後再 refresh,一共打了 ${api.calls} 次網路(應重抓一次)")
    }

    // API-32:逾時要變成畫面看得到的狀態,不是靜默取消
    @Test
    fun timeout_shows_timed_out_state() = runTest {
        val vm = SearchViewModel(SlowSearchApi())
        vm.search("kotlin")
        advanceUntilIdle()
        assertEquals(SearchState.TimedOut, vm.state.value)
    }

    // API-34:回呼觸發兩次,只取第一次;壞寫法丟例外,用 runCatching 接住再斷言
    @Test
    fun callback_twice_resumes_once() = runTest {
        val r = runCatching { LocationReader(TwiceCallingLocationClient()).current() }
        assertEquals("25.03,121.56", r.getOrNull(), "current() 應回第一次的位置,實際:$r")
    }

    // FLOW-29:produce 用完要收掉,不然父範圍等不到它;放 backgroundScope 再看 Job 結束沒
    @Test
    fun first_page_releases_producer() = runTest {
        var page: String? = null
        val job = backgroundScope.launch { page = FirstPageReader(FakePageSource()).firstPage() }
        runCurrent()   // backgroundScope 的工作 advanceUntilIdle() 不推
        assertTrue(job.isCompleted, "firstPage() 沒結束:produce 還掛在 send")
        assertEquals("page-0", page)
    }

    // CO-14:逾時剛好落在取得連線之後,連線也要關
    // 只驗有沒有洩漏;逾時時回成功還是失敗看專案,型錄的兩種標準寫法在這裡結果不同
    @Test
    fun timeout_after_open_still_closes_connection() = runTest {
        val pool = SlowOpenPool()
        runCatching { ReportSender(pool).send("daily") }   // 壞寫法會丟 TimeoutCancellationException
        assertTrue(pool.opened.isNotEmpty(), "連線根本沒開:這支測不到洩漏")
        assertTrue(pool.opened.all { it.closed }, "有連線沒關:${pool.opened}")
    }
}
```

### 測試:API-4 連坐版

```kotlin
// 起手:kotlin-idioms test-templates T1
// 照情境表態的答案留一個版本:一支失敗整頁都算失敗時留這支
import java.io.IOException
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class DashboardAllOrNothingTest {
    @Test
    fun one_failure_fails_whole_dashboard() = runTest {
        val r = runCatching { DashboardLoader(FakeDashboardApi()).load() }
        assertIs<IOException>(r.exceptionOrNull(), "連坐版:一支失敗整體失敗,實際:$r")
        assertEquals(100L, testScheduler.currentTime, "另一支要被取消,不用等滿 1 秒")
    }
}
```

### 測試:API-4 不連坐版

```kotlin
// 起手:kotlin-idioms test-templates T1
// 照情境表態的答案留一個版本:一支壞了其他照常顯示時留這支
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.Test

class DashboardIndependentTest {
    @Test
    fun one_failure_keeps_other_parts() = runTest {
        val r = runCatching { DashboardLoader(FakeDashboardApi()).load() }
        assertEquals(Dashboard(news = null, weather = "晴"), r.getOrNull(), "不連坐版:一支失敗其他照常,實際:$r")
    }
}
```

### 測試:API-10 冪等鍵版

```kotlin
// 起手:kotlin-idioms test-templates T1
// 後端支援冪等鍵時改用這支:允許送兩次,但兩次帶同一個鍵
import kotlin.test.assertEquals
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Rule
import org.junit.Test

class IdempotentCheckoutTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())

    @Test
    fun double_submit_reuses_idempotency_key() = runTest {
        val api = FakeOrderApi()
        var n = 0
        val vm = IdempotentCheckoutViewModel(api) { "key-${++n}" }
        vm.submit("A-1")
        vm.submit("A-1")
        advanceUntilIdle()
        assertEquals(listOf("key-1", "key-1"), api.calls.map { it.second })
    }
}
```

### 假依賴

```kotlin
import java.io.IOException
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

class FakeHomeApi : HomeApi {
    override suspend fun user(): String { delay(1_000); return "Ada" }
    override suspend fun feed(): List<String> { delay(1_000); return listOf("p1") }
}

class FakeOrderApi : OrderApi {
    val calls = mutableListOf<Pair<String, String?>>()
    override suspend fun submit(order: String, idempotencyKey: String?) {
        calls += order to idempotencyKey
        delay(500)
    }
}

class FakeConfigApi : ConfigApi {
    var calls = 0
    override suspend fun fetch(): String { calls++; delay(1_000); return "config-v$calls" }
}

class SlowSearchApi : SearchApi {
    override suspend fun search(query: String): List<String> { delay(10_000); return listOf(query) }
}

class TwiceCallingLocationClient : LocationClient {
    override fun request(callback: (String) -> Unit) {
        callback("25.03,121.56")
        callback("25.04,121.57")   // 有些定位 SDK 會回兩次
    }
}

class FakePageSource : PageSource {
    override suspend fun page(index: Int) = "page-$index"
}

class FakeConnection(private val id: Int) : Connection {
    var closed = false
    override suspend fun write(data: String) { delay(100) }
    override fun close() { closed = true }
    override fun toString() = "conn$id(closed=$closed)"
}

class SlowOpenPool : ConnectionPool {
    val opened = mutableListOf<FakeConnection>()
    // 取得連線不理會取消(底層是阻塞呼叫),1.5 秒後才回來:逾時剛好落在「取得之後、回傳之前」
    override suspend fun open(): Connection = withContext(NonCancellable) {
        delay(1_500)
        FakeConnection(opened.size + 1).also { opened += it }
    }
}

class FakeDashboardApi : DashboardApi {
    override suspend fun news(): String { delay(100); throw IOException("新聞服務掛了") }
    override suspend fun weather(): String { delay(1_000); return "晴" }
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
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

interface HomeApi {
    suspend fun user(): String
    suspend fun feed(): List<String>
}

data class Home(val user: String, val feed: List<String>)

class HomeLoader(private val api: HomeApi) {
    suspend fun load(): Home = coroutineScope {
        val user = async { api.user() }
        val feed = async { api.feed() }
        Home(user.await(), feed.await())
    }
}
```

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch

interface OrderApi {
    suspend fun submit(order: String, idempotencyKey: String?)
}

class CheckoutViewModel(private val api: OrderApi) : ViewModel() {
    private var job: Job? = null

    fun submit(order: String) {
        if (job?.isActive == true) return
        job = viewModelScope.launch { api.submit(order, idempotencyKey = null) }
    }
}
```

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.async
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

interface ConfigApi {
    suspend fun fetch(): String
}

class ConfigRepository(private val api: ConfigApi, private val scope: CoroutineScope) {
    private val mutex = Mutex()
    private var inflight: Deferred<String>? = null

    suspend fun refresh(): String = mutex.withLock {
        inflight?.takeIf { it.isActive } ?: scope.async { api.fetch() }.also { inflight = it }
    }.await()
}
```

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull

interface SearchApi {
    suspend fun search(query: String): List<String>
}

sealed interface SearchState {
    data object Idle : SearchState
    data object Loading : SearchState
    data class Data(val items: List<String>) : SearchState
    data object TimedOut : SearchState
}

class SearchViewModel(private val api: SearchApi) : ViewModel() {
    private val _state = MutableStateFlow<SearchState>(SearchState.Idle)
    val state: StateFlow<SearchState> = _state.asStateFlow()

    fun search(query: String) {
        _state.value = SearchState.Loading
        viewModelScope.launch {
            val items = withTimeoutOrNull(5_000) { api.search(query) }
            _state.value = if (items == null) SearchState.TimedOut else SearchState.Data(items)
        }
    }
}
```

```kotlin
import kotlin.coroutines.resume
import kotlinx.coroutines.suspendCancellableCoroutine

interface LocationClient {
    fun request(callback: (String) -> Unit)
}

class LocationReader(private val client: LocationClient) {
    suspend fun current(): String = suspendCancellableCoroutine { cont ->
        client.request { location -> if (cont.isActive) cont.resume(location) }
    }
}
```

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.channels.consume
import kotlinx.coroutines.channels.produce
import kotlinx.coroutines.coroutineScope

interface PageSource {
    suspend fun page(index: Int): String
}

@OptIn(ExperimentalCoroutinesApi::class)
class FirstPageReader(private val source: PageSource) {
    suspend fun firstPage(): String = coroutineScope {
        val pages = produce {
            var i = 0
            while (true) send(source.page(i++))
        }
        pages.consume { receive() }
    }
}
```

```kotlin
import java.io.Closeable
import kotlinx.coroutines.withTimeoutOrNull

interface Connection : Closeable {
    suspend fun write(data: String)
}

interface ConnectionPool {
    suspend fun open(): Connection
}

class ReportSender(private val pool: ConnectionPool) {
    // 連線在 withTimeout 外取得、用 use 關;逾時只管送資料那一段
    suspend fun send(report: String): Boolean =
        pool.open().use { conn -> withTimeoutOrNull(1_000) { conn.write(report) } != null }
}
```

```kotlin
interface DashboardApi {
    suspend fun news(): String
    suspend fun weather(): String
}

data class Dashboard(val news: String?, val weather: String?)
```

### 好寫法:API-4 連坐

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

class DashboardLoader(private val api: DashboardApi) {
    suspend fun load(): Dashboard = coroutineScope {
        val news = async { api.news() }
        val weather = async { api.weather() }
        Dashboard(news.await(), weather.await())
    }
}
```

### 好寫法:API-4 不連坐

```kotlin
import kotlin.coroutines.cancellation.CancellationException
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

class DashboardLoader(private val api: DashboardApi) {
    suspend fun load(): Dashboard = supervisorScope {
        val news = async { api.news() }
        val weather = async { api.weather() }
        Dashboard(news.awaitOrNull(), weather.awaitOrNull())
    }

    private suspend fun <T> Deferred<T>.awaitOrNull(): T? =
        try {
            await()
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            null
        }
}
```

### 好寫法:API-10 冪等鍵

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import java.util.UUID
import kotlinx.coroutines.launch

class IdempotentCheckoutViewModel(
    private val api: OrderApi,
    private val newKey: () -> String = { UUID.randomUUID().toString() },
) : ViewModel() {
    private var pendingKey: String? = null

    fun submit(order: String) {
        val key = pendingKey ?: newKey().also { pendingKey = it }
        viewModelScope.launch {
            api.submit(order, key)
            pendingKey = null
        }
    }
}
```

### 好寫法:CO-14 區塊內 try/finally

```kotlin
import java.io.Closeable
import kotlinx.coroutines.withTimeoutOrNull

interface Connection : Closeable {
    suspend fun write(data: String)
}

interface ConnectionPool {
    suspend fun open(): Connection
}

class ReportSender(private val pool: ConnectionPool) {
    // 型錄 CO-14 的第二種標準寫法:取得與關閉都在逾時區塊裡,用 try/finally 收
    suspend fun send(report: String): Boolean =
        withTimeoutOrNull(1_000) {
            val conn = pool.open()
            try {
                conn.write(report)
                true
            } finally {
                conn.close()
            }
        } ?: false
}
```

### 壞寫法:API-1 依序呼叫

```kotlin
interface HomeApi {
    suspend fun user(): String
    suspend fun feed(): List<String>
}

data class Home(val user: String, val feed: List<String>)

class HomeLoader(private val api: HomeApi) {
    suspend fun load(): Home {
        val user = api.user()   // 壞:兩支互不依賴卻依序等
        val feed = api.feed()
        return Home(user, feed)
    }
}
```

### 壞寫法:API-10 沒有進行中判斷

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

interface OrderApi {
    suspend fun submit(order: String, idempotencyKey: String?)
}

class CheckoutViewModel(private val api: OrderApi) : ViewModel() {
    fun submit(order: String) {
        viewModelScope.launch { api.submit(order, idempotencyKey = null) }   // 壞:連點就送兩筆
    }
}
```

### 壞寫法:API-10 冪等鍵每次重產

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import java.util.UUID
import kotlinx.coroutines.launch

class IdempotentCheckoutViewModel(
    private val api: OrderApi,
    private val newKey: () -> String = { UUID.randomUUID().toString() },
) : ViewModel() {
    fun submit(order: String) {
        val key = newKey()   // 壞:每次點都換新鍵,後端認不出是同一筆
        viewModelScope.launch { api.submit(order, key) }
    }
}
```

### 壞寫法:API-31 各自打網路

```kotlin
import kotlinx.coroutines.CoroutineScope

interface ConfigApi {
    suspend fun fetch(): String
}

class ConfigRepository(private val api: ConfigApi, scope: CoroutineScope) {
    suspend fun refresh(): String = api.fetch()   // 壞:同時三個呼叫端就打三次
}
```

### 壞寫法:API-31 結果永久快取

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.async
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

interface ConfigApi {
    suspend fun fetch(): String
}

class ConfigRepository(private val api: ConfigApi, private val scope: CoroutineScope) {
    private val mutex = Mutex()
    private var inflight: Deferred<String>? = null

    suspend fun refresh(): String = mutex.withLock {
        inflight ?: scope.async { api.fetch() }.also { inflight = it }   // 壞:做完的也一直重用,refresh 再也不會重抓
    }.await()
}
```

### 壞寫法:API-32 逾時被當成一般取消

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout

interface SearchApi {
    suspend fun search(query: String): List<String>
}

sealed interface SearchState {
    data object Idle : SearchState
    data object Loading : SearchState
    data class Data(val items: List<String>) : SearchState
    data object TimedOut : SearchState
}

class SearchViewModel(private val api: SearchApi) : ViewModel() {
    private val _state = MutableStateFlow<SearchState>(SearchState.Idle)
    val state: StateFlow<SearchState> = _state.asStateFlow()

    fun search(query: String) {
        _state.value = SearchState.Loading
        viewModelScope.launch {
            // 壞:逾時丟的是取消例外,launch 靜默結束,畫面卡在 Loading
            _state.value = SearchState.Data(withTimeout(5_000) { api.search(query) })
        }
    }
}
```

### 壞寫法:API-34 回呼兩次都 resume

```kotlin
import kotlin.coroutines.resume
import kotlinx.coroutines.suspendCancellableCoroutine

interface LocationClient {
    fun request(callback: (String) -> Unit)
}

class LocationReader(private val client: LocationClient) {
    suspend fun current(): String = suspendCancellableCoroutine { cont ->
        client.request { location -> cont.resume(location) }   // 壞:第二次回呼丟 IllegalStateException
    }
}
```

### 壞寫法:FLOW-29 produce 沒收掉

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.channels.produce
import kotlinx.coroutines.coroutineScope

interface PageSource {
    suspend fun page(index: Int): String
}

@OptIn(ExperimentalCoroutinesApi::class)
class FirstPageReader(private val source: PageSource) {
    suspend fun firstPage(): String = coroutineScope {
        val pages = produce {
            var i = 0
            while (true) send(source.page(i++))
        }
        pages.receive()   // 壞:拿一個就走,生產者掛在 send,coroutineScope 永遠等它
    }
}
```

### 壞寫法:CO-14 在 withTimeout 裡取得連線

```kotlin
import java.io.Closeable
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull

interface Connection : Closeable {
    suspend fun write(data: String)
}

interface ConnectionPool {
    suspend fun open(): Connection
}

class ReportSender(private val pool: ConnectionPool) {
    suspend fun send(report: String): Boolean {
        val conn = withTimeout(1_000) { pool.open() }   // 壞:逾時落在取得之後,連線沒人關
        return conn.use { withTimeoutOrNull(1_000) { it.write(report) } != null }
    }
}
```

### 壞寫法:API-4 supervisorScope 沒接住 await

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

class DashboardLoader(private val api: DashboardApi) {
    suspend fun load(): Dashboard = supervisorScope {
        val news = async { api.news() }
        val weather = async { api.weather() }
        Dashboard(news.await(), weather.await())   // 壞:await 照樣把例外丟出來,supervisorScope 白用
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:independent_calls_run_in_parallel、double_submit_calls_api_once、concurrent_refresh_hits_network_once、timeout_shows_timed_out_state、callback_twice_resumes_once、first_page_releases_producer、timeout_after_open_still_closes_connection |
| 測試 | 壞寫法:API-1 依序呼叫 | independent_calls_run_in_parallel 斷言紅「expected:<1000> but was:<2000>」;其他綠 |
| 測試 | 壞寫法:API-10 沒有進行中判斷 | double_submit_calls_api_once 斷言紅「送出 2 次」;其他綠 |
| 測試 | 壞寫法:API-31 各自打網路 | concurrent_refresh_hits_network_once 斷言紅「打了 3 次網路」;其他綠 |
| 測試 | 壞寫法:API-31 結果永久快取 | concurrent_refresh_hits_network_once 斷言紅「一共打了 1 次網路」;其他綠 |
| 測試 | 壞寫法:API-32 逾時被當成一般取消 | timeout_shows_timed_out_state 斷言紅「but was:<Loading>」;其他綠 |
| 測試 | 壞寫法:API-34 回呼兩次都 resume | callback_twice_resumes_once 斷言紅「Already resumed」;其他綠 |
| 測試 | 壞寫法:FLOW-29 produce 沒收掉 | first_page_releases_producer 斷言紅「firstPage() 沒結束」;其他綠 |
| 測試 | 壞寫法:CO-14 在 withTimeout 裡取得連線 | timeout_after_open_still_closes_connection 斷言紅「conn1(closed=false)」;其他綠 |
| 測試 | 好寫法:CO-14 區塊內 try/finally | 全綠:independent_calls_run_in_parallel、double_submit_calls_api_once、concurrent_refresh_hits_network_once、timeout_shows_timed_out_state、callback_twice_resumes_once、first_page_releases_producer、timeout_after_open_still_closes_connection |
| 測試:API-4 連坐版 | 好寫法:API-4 連坐 | 全綠:one_failure_fails_whole_dashboard |
| 測試:API-4 連坐版 | 好寫法:API-4 不連坐 | one_failure_fails_whole_dashboard 斷言紅「連坐版:一支失敗整體失敗」 |
| 測試:API-4 不連坐版 | 好寫法:API-4 不連坐 | 全綠:one_failure_keeps_other_parts |
| 測試:API-4 不連坐版 | 好寫法:API-4 連坐 | one_failure_keeps_other_parts 斷言紅「新聞服務掛了」 |
| 測試:API-4 不連坐版 | 壞寫法:API-4 supervisorScope 沒接住 await | one_failure_keeps_other_parts 斷言紅「新聞服務掛了」 |
| 測試:API-10 冪等鍵版 | 好寫法:API-10 冪等鍵 | 全綠:double_submit_reuses_idempotency_key |
| 測試:API-10 冪等鍵版 | 壞寫法:API-10 冪等鍵每次重產 | double_submit_reuses_idempotency_key 斷言紅「expected:<[key-1, key-1]> but was:<[key-1, key-2]>」 |

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
import app.cash.turbine.Event
import app.cash.turbine.test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceTimeBy
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
            vm.onQueryChange("a")
            runCurrent()   // 慢的舊查詢先出發
            vm.onQueryChange("ab")
            advanceUntilIdle()
            // 推到靜止後一次取出全部事件:少一筆、多一筆、順序錯都是斷言紅
            // (awaitItem() 等不到值、expectNoEvents() 多一筆都丟 TurbineAssertionError,收證不算斷言)
            assertEquals(
                listOf(Event.Item(emptyList()), Event.Item(listOf("ab:1"))),
                cancelAndConsumeRemainingEvents(),
            )
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
        advanceTimeBy(1_000)   // shareIn 開在 backgroundScope,advanceUntilIdle() 不推;假上游要 100 毫秒
        runCurrent()
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
        assertTrue(r.isSuccess, "查不到不能丟例外,實際丟了:${r.exceptionOrNull()}")
        assertTrue(r.getOrNull().isNullOrEmpty(), "查不到要回 null 或空字串,實際:${r.getOrNull()}")
        assertEquals("Ada", UserFinder(FakeUserRepository()).name("1"))   // 正向路徑:查得到的要回名字
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
    override suspend fun fetch(): Int {
        calls++
        delay(100)   // 會掛起:兩個收集者才真的同時在等,沒同步的快取寫法才會露餡
        return 100
    }
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

### 好寫法:FLOW-23 查不到回空字串

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull

interface UserRepository {
    fun find(id: String): Flow<String>
}

class UserFinder(private val repo: UserRepository) {
    suspend fun name(id: String): String? = repo.find(id).firstOrNull() ?: ""   // 也是標準寫法的一種:不丟例外
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

### 壞寫法:FLOW-18 沒同步的快取

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

interface PriceApi {
    suspend fun fetch(): Int
}

class PriceRepository(private val api: PriceApi, scope: CoroutineScope) {
    private var cached: Int? = null
    // 壞:看起來有快取,但兩個收集者同時進來時都看到 null,各打一次
    val price: Flow<Int> = flow { emit(cached ?: api.fetch().also { cached = it }) }
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

### 壞寫法:FLOW-23 不查直接回 null

```kotlin
import kotlinx.coroutines.flow.Flow

interface UserRepository {
    fun find(id: String): Flow<String>
}

class UserFinder(private val repo: UserRepository) {
    suspend fun name(id: String): String? = null   // 壞:永遠不查,查不到那支照綠
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
| 測試 | 壞寫法:API-8 flatMapConcat 排隊 | latest_query_wins 斷言紅「Item([a:1]), Item([ab:1])」;其他綠 |
| 測試 | 壞寫法:API-8 每次 launch 不取消前一個 | latest_query_wins 斷言紅「Item([ab:1]), Item([a:1])」;其他綠 |
| 測試 | 壞寫法:FLOW-3 來源沒有初始值 | feed_ready_even_if_prefs_never_emit 斷言紅「but was:<Loading>」;其他綠 |
| 測試 | 壞寫法:FLOW-18 冷流各自收 | two_collectors_share_one_fetch 斷言紅「上游被執行 2 次」;其他綠 |
| 測試 | 壞寫法:FLOW-18 沒同步的快取 | two_collectors_share_one_fetch 斷言紅「上游被執行 2 次」;其他綠 |
| 測試 | 壞寫法:FLOW-20 collect 之後寫程式 | code_after_login_runs 斷言紅「expected:<歡迎 Ada> but was:<null>」;其他綠 |
| 測試 | 壞寫法:FLOW-23 空流用 first() | missing_user_returns_null 斷言紅「NoSuchElementException」;其他綠 |
| 測試 | 壞寫法:FLOW-23 不查直接回 null | missing_user_returns_null 斷言紅「expected:<Ada> but was:<null>」;其他綠 |
| 測試 | 好寫法:FLOW-23 查不到回空字串 | 全綠:latest_query_wins、feed_ready_even_if_prefs_never_emit、two_collectors_share_one_fetch、code_after_login_runs、missing_user_returns_null、late_collector_still_gets_welcome、same_error_twice_shows_twice |
| 測試 | 壞寫法:FLOW-24 沒訂閱者就 emit | late_collector_still_gets_welcome 斷言紅「expected:<[歡迎回來]> but was:<[]>」;其他綠 |
| 測試 | 壞寫法:STATE-10 訊息沒有唯一 id | same_error_twice_shows_twice 斷言紅「expected:<2> but was:<1>」;其他綠 |

## T3 程序被殺還原

型錄列:STATE-6、STATE-26。把第一個 ViewModel 寫進 `SavedStateHandle` 的內容帶到「程序被殺後重建」的第二個 ViewModel,斷言輸入與待處理的 id 還在。

兩個測試版本,照專案挑一個:

- 〈測試〉(預設):照官方「用測試值建新的 SavedStateHandle」,把第一個 handle 的內容複製成第二個 handle。Android 模組的本機單元測試(`src/test`,跑 `testDebugUnitTest`)與純 JVM 都跑得動(兩邊都實跑過)。
- 〈測試:viewModelScenario 版〉:用 `lifecycle-viewmodel-testing` 的 `viewModelScenario { … }.recreate()`。**只在純 JVM 或 KMP 的共用模組用**:放進 Android 模組的本機單元測試,好寫法、壞寫法一律例外紅 `Method containsKey in android.os.BaseBundle not mocked`(Android 上 `SavedState` 就是 `Bundle`,本機單元測試的 android.jar 是空殼;開 `isReturnDefaultValues` 也只換成 `NullPointerException`,實跑)。Android 模組要用它得放 Robolectric 或儀器測試,這兩條路本範本沒驗。

兩版各自不涵蓋的(要靠代碼審或真機):

- 複製 handle 版只複製 `keys()` 裡已經寫進去的值,不會呼叫 `setSavedStateProvider` 登記的提供者;狀態用提供者存的寫法(官方頁存非 Parcelable 物件的做法)在這一版會誤紅,見矩陣〈好寫法:STATE-6 用 setSavedStateProvider〉那兩格。用提供者的專案挑 viewModelScenario 版。
- 兩版在 JVM 上都不檢查值能不能放進 `Bundle`:存一個不是 Parcelable、也不是 Serializable 的物件照綠,真機才會在存狀態時出錯。
- Compose 裡 `SavedStateHandle` 要等宿主 Activity 停止才真的存(型錄 STATE-20,不接),兩版都測不到寫入時機。

### 依據

- STATE-6、STATE-26:https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate 「These values persist after the process is killed by the system」「create a new instance of SavedStateHandle with the test values it requires and pass it to the ViewModel instance you are testing」
- 純 JVM 可用、`ViewModelScenario.recreate()`:https://developer.android.com/jetpack/androidx/releases/lifecycle 2.9.0「The lifecycle-viewmodel-savedstate module is now KMP compatible including APIs like SavedStateHandle」「A new androidx.lifecycle:lifecycle-viewmodel-testing KMP artifact … testing process death and recreation via recreate()」
- Android 本機單元測試沒有真的 `Bundle`:https://developer.android.com/training/testing/local-tests 本機測試跑在不含 Android 框架實作的 android.jar 上,要用框架類別就換成 Robolectric(實跑訊息見上)

### 依賴

```kotlin
implementation("androidx.lifecycle:lifecycle-viewmodel-savedstate:2.9.4")
testImplementation("androidx.lifecycle:lifecycle-viewmodel-testing:2.9.4")   // 只有 viewModelScenario 版要
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T3
// 照官方「用測試值建新的 SavedStateHandle」:把第一個 handle 的內容帶到重建後的 ViewModel
import androidx.lifecycle.SavedStateHandle
import kotlin.test.assertEquals
import org.junit.Test

class SearchFormRestoreTest {
    // 只帶走已經寫進 handle 的值(setSavedStateProvider 登記的不會被呼叫)
    private fun SavedStateHandle.afterProcessDeath() = SavedStateHandle(keys().associateWith { get<Any?>(it) })

    // STATE-6:使用者輸入在程序被殺、重建後還在
    @Test
    fun query_survives_process_death() {
        val handle = SavedStateHandle()
        SearchFormViewModel(handle).onQueryChange("kotlin")
        val restored = SearchFormViewModel(handle.afterProcessDeath())
        assertEquals("kotlin", restored.query.value)
    }

    // STATE-26:開相機前記下的待處理 id,回來時還找得到
    @Test
    fun pending_scan_survives_process_death() {
        val handle = SavedStateHandle()
        SearchFormViewModel(handle).startScan(orderId = "A-42")
        val restored = SearchFormViewModel(handle.afterProcessDeath())
        assertEquals("A-42:QR123", restored.onScanResult("QR123"))
    }
}
```

### 測試:viewModelScenario 版

```kotlin
// 起手:kotlin-idioms test-templates T3
// 只在純 JVM 或 KMP 共用模組用;Android 模組的本機單元測試跑不起來(見本節開頭)
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.viewmodel.testing.viewModelScenario
import kotlin.test.assertEquals
import org.junit.Test

class SearchFormRecreateTest {
    @Test
    fun query_survives_recreate() {
        viewModelScenario { SearchFormViewModel(createSavedStateHandle()) }.use { scenario ->
            scenario.viewModel.onQueryChange("kotlin")
            scenario.recreate()
            assertEquals("kotlin", scenario.viewModel.query.value)
        }
    }

    @Test
    fun pending_scan_survives_recreate() {
        viewModelScenario { SearchFormViewModel(createSavedStateHandle()) }.use { scenario ->
            scenario.viewModel.startScan(orderId = "A-42")
            scenario.recreate()
            assertEquals("A-42:QR123", scenario.viewModel.onScanResult("QR123"))
        }
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

### 好寫法:STATE-6 用 setSavedStateProvider

```kotlin
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.savedstate.SavedState
import androidx.savedstate.read
import androidx.savedstate.savedState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class SearchFormViewModel(private val handle: SavedStateHandle) : ViewModel() {
    // 用提供者存:狀態放自己的欄位,要存的時候才打包(官方頁存非 Parcelable 物件的做法)
    private val _query = MutableStateFlow(handle.get<SavedState>("form")?.read { getString("query") } ?: "")
    val query: StateFlow<String> = _query.asStateFlow()

    init {
        handle.setSavedStateProvider("form") { savedState(mapOf("query" to _query.value)) }
    }

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

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:query_survives_process_death、pending_scan_survives_process_death |
| 測試 | 壞寫法:STATE-6 輸入只放記憶體 | query_survives_process_death 斷言紅「expected:<[kotlin]> but was:<[]>」;其他綠 |
| 測試 | 壞寫法:STATE-26 待處理 id 放一般欄位 | pending_scan_survives_process_death 斷言紅「expected:<A-42:QR123> but was:<null>」;其他綠 |
| 測試 | 好寫法:STATE-6 用 setSavedStateProvider | query_survives_process_death 斷言紅「expected:<[kotlin]> but was:<[]>」;其他綠 |
| 測試:viewModelScenario 版 | 好寫法 | 全綠:query_survives_recreate、pending_scan_survives_recreate |
| 測試:viewModelScenario 版 | 壞寫法:STATE-6 輸入只放記憶體 | query_survives_recreate 斷言紅「expected:<[kotlin]> but was:<[]>」;其他綠 |
| 測試:viewModelScenario 版 | 壞寫法:STATE-26 待處理 id 放一般欄位 | pending_scan_survives_recreate 斷言紅「expected:<A-42:QR123> but was:<null>」;其他綠 |
| 測試:viewModelScenario 版 | 好寫法:STATE-6 用 setSavedStateProvider | 全綠:query_survives_recreate、pending_scan_survives_recreate |

讀法:〈測試〉對〈好寫法:STATE-6 用 setSavedStateProvider〉紅,是這一版**不涵蓋**的寫法(誤紅),不是那段程式錯;用提供者存狀態的專案改用 viewModelScenario 版。〈測試〉的四格另在 Android library 模組(AGP 8.13.2、compileSdk 36、`testDebugUnitTest`,沒開 `isReturnDefaultValues`)跑過,結果同上;viewModelScenario 版的四格在那裡全部例外紅,所以它只標純 JVM 與 KMP。

## T4 HTTP 邊界

型錄列:API-21、API-26。真的 OkHttp/Retrofit 打本機 MockWebServer。MockWebServer 照專案實際解析到的 OkHttp 主版本挑:OkHttp 4 用〈依賴:OkHttp 4〉與〈測試:OkHttp 4〉,OkHttp 5 用〈依賴:OkHttp 5〉與〈測試:OkHttp 5〉,兩份測試只差 import 與排回應的寫法。不要讓 OkHttp 4 的專案配 `mockwebserver3`:Gradle 會在測試的類別路徑上默默把 OkHttp 升成 5(測試綠,但測的不是正式用的版本);用 `strictly` 釘住 4.12.0 時每支測試都 `NoClassDefFoundError: okhttp3/internal/_UtilJvmKt`(實驗實測)。走真的 socket,不在 `runTest` 的虛擬時間裡用 `withTimeout`(虛擬時間遇到真實 I/O 會直接跳到逾時點);要等真實時間就包進 `withContext(Dispatchers.Default)`。

### 依據

- MockWebServer:https://github.com/square/okhttp/tree/master/mockwebserver(README 的依賴行 `com.squareup.okhttp3:mockwebserver3`;OkHttp 4 對應的是 `com.squareup.okhttp3:mockwebserver`,套件 `okhttp3.mockwebserver`)
- API-21:OkHttp `Authenticator` 原始碼 KDoc「Returns null if the challenge cannot be satisfied」,範例 `while ((response = response.priorResponse()) != null)` 與「Give up, we've already failed to authenticate.」(https://github.com/square/okhttp/blob/master/okhttp/src/commonJvmAndroid/kotlin/okhttp3/Authenticator.kt);加鎖那一半照型錄 API-21 標準寫法 `mutex.withLock { if (token 已被別人刷新) 用新的 else refresh() }`(出處不全,KDoc 沒提並行);範本改用 `synchronized` 是旁證:`authenticate(route: Route?, response: Response): Request?` 是一般函式、不是 suspend(同一份原始碼的方法簽名),在它裡面用不了 `Mutex.withLock`
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
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.mockwebserver.Dispatcher
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import okhttp3.mockwebserver.RecordedRequest
import org.junit.After
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

class HttpBoundaryTest {
    private val server = MockWebServer()

    @After
    fun tearDown() = server.shutdown()

    private fun client(tokens: TokenStore) = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor(tokens))
        .authenticator(TokenAuthenticator(tokens))
        .build()

    // API-21 上限:伺服器一直回 401,重試要有上限;壞寫法一路重試到 OkHttp 的追隨上限丟 ProtocolException,用 runCatching 接住
    @Test
    fun refresh_gives_up_after_three_tries() {
        repeat(25) { server.enqueue(MockResponse().setResponseCode(401)) }
        val r = runCatching {
            client(FakeTokenStore()).newCall(Request.Builder().url(server.url("/me")).build()).execute().use { it.code }
        }
        assertTrue(server.requestCount <= 3, "打了 ${server.requestCount} 次才停,結果:$r")
        assertEquals(401, r.getOrNull())
    }

    // API-21 加鎖:5 個請求同時拿到 401,只刷新一次,其他人用刷新好的權杖,而且都成功
    @Test
    fun concurrent_401s_refresh_once() {
        server.dispatcher = object : Dispatcher() {
            override fun dispatch(request: RecordedRequest) =
                if (request.getHeader("Authorization") in setOf(null, "Bearer token-0")) MockResponse().setResponseCode(401) else MockResponse().setResponseCode(200)
        }
        val tokens = FakeTokenStore()
        val client = client(tokens)
        val start = CountDownLatch(1)
        val pool = Executors.newFixedThreadPool(5)
        val calls = List(5) {
            pool.submit<Int> {
                start.await()
                client.newCall(Request.Builder().url(server.url("/me")).build()).execute().use { it.code }
            }
        }
        start.countDown()
        val codes = calls.map { runCatching { it.get(10, TimeUnit.SECONDS) }.getOrElse { -1 } }
        pool.shutdown()
        assertEquals(List(5) { 200 }, codes, "5 個並行請求的狀態碼")
        assertEquals(1, tokens.refreshes.get(), "5 個並行 401 刷新了 ${tokens.refreshes.get()} 次")
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
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.Json
import mockwebserver3.Dispatcher
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import mockwebserver3.RecordedRequest
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

    private fun client(tokens: TokenStore) = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor(tokens))
        .authenticator(TokenAuthenticator(tokens))
        .build()

    // API-21 上限:伺服器一直回 401,重試要有上限;壞寫法一路重試到 OkHttp 的追隨上限丟 ProtocolException,用 runCatching 接住
    @Test
    fun refresh_gives_up_after_three_tries() {
        repeat(25) { server.enqueue(MockResponse.Builder().code(401).build()) }
        val r = runCatching {
            client(FakeTokenStore()).newCall(Request.Builder().url(server.url("/me")).build()).execute().use { it.code }
        }
        assertTrue(server.requestCount <= 3, "打了 ${server.requestCount} 次才停,結果:$r")
        assertEquals(401, r.getOrNull())
    }

    // API-21 加鎖:5 個請求同時拿到 401,只刷新一次,其他人用刷新好的權杖,而且都成功
    @Test
    fun concurrent_401s_refresh_once() {
        server.dispatcher = object : Dispatcher() {
            override fun dispatch(request: RecordedRequest) =
                if (request.headers["Authorization"] in setOf(null, "Bearer token-0")) MockResponse.Builder().code(401).build() else MockResponse.Builder().code(200).build()
        }
        val tokens = FakeTokenStore()
        val client = client(tokens)
        val start = CountDownLatch(1)
        val pool = Executors.newFixedThreadPool(5)
        val calls = List(5) {
            pool.submit<Int> {
                start.await()
                client.newCall(Request.Builder().url(server.url("/me")).build()).execute().use { it.code }
            }
        }
        start.countDown()
        val codes = calls.map { runCatching { it.get(10, TimeUnit.SECONDS) }.getOrElse { -1 } }
        pool.shutdown()
        assertEquals(List(5) { 200 }, codes, "5 個並行請求的狀態碼")
        assertEquals(1, tokens.refreshes.get(), "5 個並行 401 刷新了 ${tokens.refreshes.get()} 次")
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
import java.util.concurrent.atomic.AtomicInteger

class FakeTokenStore : TokenStore {
    @Volatile
    private var token = "token-0"
    val refreshes = AtomicInteger()

    override fun current(): String = token

    override fun refresh(): String {
        Thread.sleep(200)   // 刷新要一點時間:同時收到 401 的請求才真的會撞在一起
        token = "token-${refreshes.incrementAndGet()}"
        return token
    }
}
```

### 好寫法

```kotlin
import okhttp3.Authenticator
import okhttp3.Interceptor
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

interface TokenStore {
    fun current(): String?
    fun refresh(): String?
}

// 每個請求帶上目前的權杖
class AuthInterceptor(private val tokens: TokenStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokens.current() ?: return chain.proceed(chain.request())
        return chain.proceed(chain.request().newBuilder().header("Authorization", "Bearer $token").build())
    }
}

// 型錄 API-21 寫 mutex.withLock;Authenticator.authenticate 是一般(非 suspend)函式,在 OkHttp 的執行緒上同步呼叫,
// 所以這裡用 synchronized——這是從方法簽名推出來的(旁證),OkHttp 文件沒寫並行刷新該怎麼鎖
class TokenAuthenticator(private val tokens: TokenStore) : Authenticator {
    private val lock = Any()

    override fun authenticate(route: Route?, response: Response): Request? {
        if (response.tries() >= MAX_TRIES) return null   // 有上限:放棄,讓 401 回到呼叫端
        val sent = response.request.header("Authorization")?.removePrefix("Bearer ")
        // 加鎖:同時收到 401 的請求排隊;別人已經刷新過(目前的權杖跟這次送出的不同)就直接用新的
        val token = synchronized(lock) {
            val current = tokens.current()
            if (current != null && current != sent) current else tokens.refresh()
        } ?: return null
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
import okhttp3.Interceptor
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

interface TokenStore {
    fun current(): String?
    fun refresh(): String?
}

// 每個請求帶上目前的權杖
class AuthInterceptor(private val tokens: TokenStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokens.current() ?: return chain.proceed(chain.request())
        return chain.proceed(chain.request().newBuilder().header("Authorization", "Bearer $token").build())
    }
}

// 壞:有加鎖,但每次 401 都刷新重送,不數次數
class TokenAuthenticator(private val tokens: TokenStore) : Authenticator {
    private val lock = Any()

    override fun authenticate(route: Route?, response: Response): Request? {
        val sent = response.request.header("Authorization")?.removePrefix("Bearer ")
        // 加鎖:同時收到 401 的請求排隊;別人已經刷新過(目前的權杖跟這次送出的不同)就直接用新的
        val token = synchronized(lock) {
            val current = tokens.current()
            if (current != null && current != sent) current else tokens.refresh()
        } ?: return null
        return response.request.newBuilder().header("Authorization", "Bearer $token").build()
    }
}
```

### 壞寫法:API-21 沒加鎖

```kotlin
import okhttp3.Authenticator
import okhttp3.Interceptor
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

interface TokenStore {
    fun current(): String?
    fun refresh(): String?
}

// 每個請求帶上目前的權杖
class AuthInterceptor(private val tokens: TokenStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokens.current() ?: return chain.proceed(chain.request())
        return chain.proceed(chain.request().newBuilder().header("Authorization", "Bearer $token").build())
    }
}

// 壞:有上限,但沒加鎖:同時收到 401 的請求各自刷新(刷新風暴、權杖互相覆蓋)
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

### 壞寫法:API-21 不刷新直接放棄

```kotlin
import okhttp3.Authenticator
import okhttp3.Interceptor
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route

interface TokenStore {
    fun current(): String?
    fun refresh(): String?
}

// 每個請求帶上目前的權杖
class AuthInterceptor(private val tokens: TokenStore) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokens.current() ?: return chain.proceed(chain.request())
        return chain.proceed(chain.request().newBuilder().header("Authorization", "Bearer $token").build())
    }
}

class TokenAuthenticator(private val tokens: TokenStore) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        return null   // 壞:一看到 401 就放棄,不刷新
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
| 測試:OkHttp 4 | 好寫法 | 全綠:refresh_gives_up_after_three_tries、concurrent_401s_refresh_once、delete_204_is_success |
| 測試:OkHttp 4 | 壞寫法:API-21 刷新沒有上限 | refresh_gives_up_after_three_tries 斷言紅「打了 21 次才停」;其他綠 |
| 測試:OkHttp 4 | 壞寫法:API-21 沒加鎖 | concurrent_401s_refresh_once 斷言紅「5 個並行 401 刷新了 5 次」;其他綠 |
| 測試:OkHttp 4 | 壞寫法:API-21 不刷新直接放棄 | concurrent_401s_refresh_once 斷言紅「5 個並行請求的狀態碼」;其他綠 |
| 測試:OkHttp 4 | 壞寫法:API-26 204 宣告成有 body | delete_204_is_success 斷言紅「204 要算成功」;其他綠 |
| 測試:OkHttp 5 | 好寫法 | 全綠:refresh_gives_up_after_three_tries、concurrent_401s_refresh_once、delete_204_is_success |
| 測試:OkHttp 5 | 壞寫法:API-21 刷新沒有上限 | refresh_gives_up_after_three_tries 斷言紅「打了 21 次才停」;其他綠 |
| 測試:OkHttp 5 | 壞寫法:API-21 沒加鎖 | concurrent_401s_refresh_once 斷言紅「5 個並行 401 刷新了 5 次」;其他綠 |
| 測試:OkHttp 5 | 壞寫法:API-21 不刷新直接放棄 | concurrent_401s_refresh_once 斷言紅「5 個並行請求的狀態碼」;其他綠 |
| 測試:OkHttp 5 | 壞寫法:API-26 204 宣告成有 body | delete_204_is_success 斷言紅「204 要算成功」;其他綠 |

讀法:〈壞寫法:API-21 不刷新直接放棄〉只靠上限那支抓不到(它本來就該回 401),要靠並行那支的「都成功」。

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
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonObject
import org.junit.Test

class SerializationContractTest {
    // DATA-72:缺欄位或 null 照樣解得出來;壞寫法丟 MissingFieldException,用 runCatching 接住
    // JSON 帶上 status:只讓 name 缺,DATA-73 的壞寫法才不會連這支一起紅
    @Test
    fun missing_or_null_name_still_decodes() {
        val r = runCatching { AppJson.decodeFromString<List<UserDto>>("""[{"id":"1","status":"ACTIVE"},{"id":"2","name":null,"status":"ACTIVE"}]""") }
        assertTrue(r.isSuccess, "解碼失敗:${r.exceptionOrNull()}")
        // 只驗整份解得出來;缺的 name 變成 "" 還是 null 是型錄兩種標準寫法的差別,不寫死
        assertEquals(listOf("1", "2"), r.getOrThrow().map { it.id })
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
        // 解回 JSON 比整個值(含型別),不比子字串("quantity":10 也含 "quantity":1),也不用 intOrNull("1" 字串也會被讀成 1)
        assertEquals(JsonPrimitive(1), Json.parseToJsonElement(body).jsonObject["quantity"], "送出去的 JSON:$body")
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

### 好寫法:DATA-72 可空加 null 預設

```kotlin
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    val id: String,
    val name: String? = null,   // 型錄 DATA-72 標準寫法的第一種
    val status: Status = Status.UNKNOWN,
)

@Serializable
enum class Status { ACTIVE, BANNED, UNKNOWN }
```

### 好寫法:DATA-74 整個 Json 開 encodeDefaults

```kotlin
import kotlinx.serialization.json.Json

// 專案正式的 Json 設定;測試讀這一個
val AppJson = Json {
    ignoreUnknownKeys = true
    coerceInputValues = true
    encodeDefaults = true   // 型錄 DATA-74 標準寫法的另一種:全部預設值都送
}
```

```kotlin
import kotlinx.serialization.Serializable

@Serializable
data class OrderRequest(
    val item: String,
    val quantity: Int = 1,
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

### 壞寫法:DATA-74 預設值寫錯

```kotlin
import kotlinx.serialization.EncodeDefault
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.Serializable

@OptIn(ExperimentalSerializationApi::class)
@Serializable
data class OrderRequest(
    val item: String,
    @EncodeDefault val quantity: Int = 10,   // 壞:有送出去,但預設值不是需求寫的 1
)
```

### 壞寫法:DATA-74 數量送成字串

```kotlin
import kotlinx.serialization.EncodeDefault
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.Serializable

@OptIn(ExperimentalSerializationApi::class)
@Serializable
data class OrderRequest(
    val item: String,
    @EncodeDefault val quantity: String = "1",   // 壞:有送、值也對,但伺服器要的是數字,收到 "1" 字串
)
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:missing_or_null_name_still_decodes、unknown_status_becomes_unknown、default_quantity_is_sent |
| 測試 | 好寫法:DATA-72 可空加 null 預設 | 全綠:missing_or_null_name_still_decodes、unknown_status_becomes_unknown、default_quantity_is_sent |
| 測試 | 好寫法:DATA-74 整個 Json 開 encodeDefaults | 全綠:missing_or_null_name_still_decodes、unknown_status_becomes_unknown、default_quantity_is_sent |
| 測試 | 壞寫法:DATA-72 非可空欄位沒預設值 | missing_or_null_name_still_decodes 斷言紅「MissingFieldException」;其他綠 |
| 測試 | 壞寫法:DATA-73 列舉沒有 UNKNOWN | unknown_status_becomes_unknown 斷言紅「SerializationException」;其他綠 |
| 測試 | 壞寫法:DATA-74 預設值沒送出去 | default_quantity_is_sent 斷言紅「expected:<1> but was:<null>」;其他綠 |
| 測試 | 壞寫法:DATA-74 預設值寫錯 | default_quantity_is_sent 斷言紅「expected:<1> but was:<10>」;其他綠 |
| 測試 | 壞寫法:DATA-74 數量送成字串 | default_quantity_is_sent 斷言紅「expected:<1> but was:<"1">」;其他綠 |
