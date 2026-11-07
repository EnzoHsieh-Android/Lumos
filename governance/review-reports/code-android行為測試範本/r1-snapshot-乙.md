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
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
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
        repo.scores.value = 42
        advanceUntilIdle()
        assertEquals(42, vm.score.value)
    }

    // TEST-17、TEST-20:熱流用 Turbine 收;StateFlow 先消掉初始值;TEST-7 最後只比最新的值
    @Test
    fun state_starts_initial_then_loaded() = runTest {
        val vm = ProfileViewModel(repo)
        vm.state.test {
            assertEquals(ProfileState.Initial, awaitItem())
            vm.load()
            advanceUntilIdle()
            assertEquals(ProfileState.Loaded("Ada"), expectMostRecentItem())
        }
    }

    // TEST-18:每個值都收掉,最後斷言流結束、後面沒有多的
    // 用 awaitEvent() 加 assertEquals,不用 awaitComplete():後者失敗丟 TurbineAssertionError,收證工具不算斷言失敗
    @Test
    fun save_emits_saving_then_saved_once() = runTest {
        ProfileViewModel(repo).save("Ada").test {
            assertEquals(SaveEvent.Saving, awaitItem())
            assertEquals(SaveEvent.Saved, awaitItem())
            assertEquals(Event.Complete, awaitEvent())
        }
    }

    // TEST-19:錯誤要當成錯誤收,再斷言型別(同上理由用 awaitEvent(),不用 awaitError())
    @Test
    fun save_blank_name_reports_error() = runTest {
        ProfileViewModel(repo).save("").test {
            assertEquals(SaveEvent.Saving, awaitItem())
            val end = awaitEvent()
            assertIs<Event.Error>(end, "儲存失敗要以錯誤結束,實際:$end")
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
| 測試 | 好寫法 | 全綠:load_then_advance_shows_loaded、score_follows_repository_while_collected、state_starts_initial_then_loaded、save_emits_saving_then_saved_once、save_blank_name_reports_error、upload_runs_in_injected_scope |
| 測試 | 壞寫法:TEST-4 load 停在 Loading | load_then_advance_shows_loaded 斷言紅「Loading」;state_starts_initial_then_loaded 斷言紅「Loading」;其他綠 |
| 測試 | 壞寫法:TEST-6 score 沒接上游 | score_follows_repository_while_collected 斷言紅「expected:<42> but was:<0>」;其他綠 |
| 測試 | 壞寫法:TEST-9 自建 scope 用真 dispatcher | upload_runs_in_injected_scope 斷言紅「expected:<[a.jpg]> but was:<[]>」;其他綠 |
| 測試 | 壞寫法:TEST-18 Saved 多發一次 | save_emits_saving_then_saved_once 斷言紅「expected:<Complete> but was:<Item(Saved)>」;其他綠 |
| 測試 | 壞寫法:TEST-19 錯誤被吞掉 | save_blank_name_reports_error 斷言紅「實際:Complete」;其他綠 |
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
- API-4:https://kotlinlang.org/docs/exception-handling.html 「A failure of a child does not cause the supervisor job to fail and does not affect its other children」;型錄 API-4 標準寫法(連坐 `coroutineScope`、不連坐 `supervisorScope` 加逐支接住)
- API-10:型錄 API-10 標準寫法 `if (job?.isActive == true) return`(出處不全,範本只驗 ViewModel 層)
- API-31:型錄 API-31 標準寫法「共用 `Deferred` 加 mutex」(出處不全)
- API-32、CO-14:kotlinx.coroutines 指南 cancellation-and-timeouts「The TimeoutCancellationException that is thrown by withTimeout is a subclass of CancellationException」「may happen at any time, even right before the return from inside of the timeout block」(https://kotlinlang.org/docs/cancellation-and-timeouts.html ;原文無法再開頁複驗,以本組實跑當實證)
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
    @Test
    fun timeout_after_open_still_closes_connection() = runTest {
        val pool = SlowOpenPool()
        val r = runCatching { ReportSender(pool).send("daily") }
        assertTrue(pool.opened.all { it.closed }, "有連線沒關:${pool.opened}")
        assertEquals(true, r.getOrNull(), "send() 結果:$r")
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
| 測試 | 壞寫法:API-32 逾時被當成一般取消 | timeout_shows_timed_out_state 斷言紅「but was:<Loading>」;其他綠 |
| 測試 | 壞寫法:API-34 回呼兩次都 resume | callback_twice_resumes_once 斷言紅「Already resumed」;其他綠 |
| 測試 | 壞寫法:FLOW-29 produce 沒收掉 | first_page_releases_producer 斷言紅「firstPage() 沒結束」;其他綠 |
| 測試 | 壞寫法:CO-14 在 withTimeout 裡取得連線 | timeout_after_open_still_closes_connection 斷言紅「conn1(closed=false)」;其他綠 |
| 測試:API-4 連坐版 | 好寫法:API-4 連坐 | 全綠:one_failure_fails_whole_dashboard |
| 測試:API-4 連坐版 | 好寫法:API-4 不連坐 | one_failure_fails_whole_dashboard 斷言紅「連坐版:一支失敗整體失敗」 |
| 測試:API-4 不連坐版 | 好寫法:API-4 不連坐 | 全綠:one_failure_keeps_other_parts |
| 測試:API-4 不連坐版 | 好寫法:API-4 連坐 | one_failure_keeps_other_parts 斷言紅「新聞服務掛了」 |
| 測試:API-4 不連坐版 | 壞寫法:API-4 supervisorScope 沒接住 await | one_failure_keeps_other_parts 斷言紅「新聞服務掛了」 |
| 測試:API-10 冪等鍵版 | 好寫法:API-10 冪等鍵 | 全綠:double_submit_reuses_idempotency_key |
| 測試:API-10 冪等鍵版 | 壞寫法:API-10 冪等鍵每次重產 | double_submit_reuses_idempotency_key 斷言紅「expected:<[key-1, key-1]> but was:<[key-1, key-2]>」 |

