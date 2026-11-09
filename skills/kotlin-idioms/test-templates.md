# Kotlin 行為測試範本

型錄 [`checks-catalog.md`](checks-catalog.md) 裡級含 C 的列,是「長相看不出錯、要跑起來才知道」的寫法。這份檔替其中在電腦 JVM 上就跑得動的列放測試範本:每組一節,附「好寫法綠、壞寫法紅」的對照,T0–T5 每一格都在純 JVM Gradle 專案實跑過(結果見驗證紀錄 `Verification/2026-11-06_Android行為測試範本紅綠矩陣實跑`(圖譜));T4 的 Ktor 小節與 T6–T13 每一格在照〈Android 實驗專案骨架〉組的 Android app 模組實跑過(Ktor 小節是本機單元測試,沒在純 JVM 專案跑過;T6–T13 是要 Android 模組的組:模擬器、Robolectric、架構測試,模擬器用 `kds_bench`(API 34))(結果見驗證紀錄 `Verification/2026-11-06_Android儀器測試範本與架構測試實跑`(圖譜))。單源=[[Projects/Android行為測試範本與架構測試_計劃]]、[[Projects/Android儀器測試範本與架構測試_計劃]]。

## 怎麼用

1. 在型錄找到那一列,看「通電批次」欄寫的 `行為測試或正向約束=範本 T<n>`。
2. 到這份檔的 `## T<n>` 那一節。〈依據〉是每列的官方出處;〈依賴〉是要加進 `dependencies { }` 的行(版本跟專案實際解析到的對齊:先跑 `./gradlew :<模組>:dependencies --configuration <變體>RuntimeClasspath` 看,見測試品質標準〈Android 本機單元測試的驗收標準〉「加測試函式庫前看實際版本」)。T6–T13 照〈Android 實驗專案骨架〉的專案形狀;Robolectric 組(T7–T9、T11)要連〈依賴〉裡的 `robolectric.properties` 一起抄。
3. 照抄〈測試〉與〈假依賴〉,類別名、介面名換成專案自己的;〈假依賴〉放 `src/test`。同組有互斥版本的(標題寫「測試:<版本名>」),照那段程式的情境表態答案只留一個版本。
4. 照抄的測試檔第一行留 `// 起手:kotlin-idioms test-templates T<n>`(之後要數有多少測試照範本起手)。
5. 在自己的專案跑一次,綠了才算(T6、T10 與標「只在模擬器」的小節要開模擬器跑);再照「故障證明挑本次需求」那條,把被測程式改成這一節〈壞寫法〉的樣子,確認對應的測試翻成**斷言紅**(不是例外或逾時紅,收證工具只把斷言失敗算成抓到錯)。

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

## Android 實驗專案骨架

T6–T13 要 Android 模組(T6、T10 與 T7、T9 各一個小節要模擬器;T7–T9、T11 用 Robolectric;T12、T13 是 Android 模組的本機單元測試)。照下面幾個檔組一個 Android app 專案(Gradle 8.13、JDK 17、AGP 8.13.2、Kotlin 2.2.21;專案根目錄要有 Gradle wrapper,T13 的 Konsist 靠它找專案根,見 T13 節開頭),把某一組〈依賴〉的行貼進 `app/build.gradle.kts` 的 `dependencies { }`;〈依賴〉裡另有第一行標「plugins { } 加」「android { } 加」「檔尾」的圍欄,照標的位置貼(例:用到 Compose 的組要加 Compose 編譯器外掛與 `buildFeatures { compose = true }`;沒有 Compose runtime 卻開了外掛,編譯時 `IncompatibleComposeRuntimeVersionException`)。〈測試〉與〈假依賴〉放哪個資料夾看那一節開頭的「跑在哪」:Robolectric 與本機單元測試放 `app/src/test/kotlin`,模擬器放 `app/src/androidTest/kotlin`;被測程式放 `app/src/main/kotlin`,組法同〈實驗專案骨架〉。

版本是 AGP 8.13.2(最高 compileSdk 36)能用的最新穩定版:Compose BOM 2026.06.01(Compose 1.11)、lifecycle 2.10.0、navigation 2.9.8;再新的 Compose 1.12、lifecycle 2.11、navigation 2.10 要 compileSdk 37 與 AGP 9.1,`checkDebugAarMetadata` 會擋(2026-11-06 實測)。

```kotlin
// settings.gradle.kts
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositories { google(); mavenCentral() } }
rootProject.name = "kotlin-idioms-android-lab"
include(":app")
```

```kotlin
// build.gradle.kts
plugins {
    id("com.android.application") version "8.13.2" apply false
    id("org.jetbrains.kotlin.android") version "2.2.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.2.21" apply false
}
```

```properties
# gradle.properties
android.useAndroidX=true
```

```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.lab"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.example.lab"
        minSdk = 24
        targetSdk = 36   // 不寫的話 Robolectric 改用 minSdk(SDK 24)跑,跟模擬器 API 34 不同級
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    testOptions.unitTests.isIncludeAndroidResources = true   // Robolectric 要讀資源與 manifest
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin { jvmToolchain(17) }

dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation(kotlin("test"))
    androidTestImplementation("androidx.test.ext:junit:1.3.0")
    androidTestImplementation("androidx.test:runner:1.7.0")
    // 各組〈依賴〉的行貼在這裡
}
```

```properties
# app/src/test/resources/robolectric.properties
sdk=34
```

```xml
<!-- app/src/main/AndroidManifest.xml -->
<manifest />
```

這支一定要有:AGP 建置時找不到它就停在 `processDebugMainManifest`。實驗專案用空的就夠(套件名寫在 `build.gradle.kts` 的 `namespace`);要宣告 Activity 的組(T10、T11)在那一組的〈好寫法〉附了完整的 Manifest,換成那一份。

`sdk=34` 為什麼要寫:Robolectric 預設用 `targetSdk` 那一級跑,targetSdk 36 時要 JDK 21,在 JDK 17 上整個測試類別例外紅「Android SDK 36 requires Java 21 (have Java 17)」;釘 34 跟模擬器 `kds_bench`(API 34)同級。專案用 JDK 21 跑測試時可以拿掉。

跑法:

- Robolectric 與本機單元測試:`./gradlew :app:testDebugUnitTest --tests '<完整類名>'`,XML 在 `app/build/test-results/testDebugUnitTest/`。
- 模擬器:`ANDROID_SERIAL=<模擬器> ./gradlew :app:connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=<完整類名>`,XML 在 `app/build/outputs/androidTest-results/connected/debug/<裝置名>/`。儀器報告的 XML 沒有例外型別,收證看第一行是不是 `java.lang.AssertionError`、堆疊裡有沒有 `org.junit.Assert` 的斷言框;所以模擬器上的〈測試〉一律用 `org.junit.Assert` 的斷言。

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

型錄列:API-1、API-4、API-10、API-32、API-34、FLOW-29、CO-14;API-31 型錄已停用(2026-11-09,查兩輪找不到權威原文),這節裡它的測試與壞寫法只當範例,不當標準。假依賴用 `delay` 模擬耗時,`runTest` 跳過 delay 但記下虛擬時間;斷言 `testScheduler.currentTime`、呼叫次數、逾時後的狀態。API-4 的兩個測試版本互斥(一支失敗要不要連坐是業務決定),照那段程式的情境表態答案只留一個;API-10 預設斷言「連點兩次只打一次 API」,後端有冪等鍵時改用〈測試:API-10 冪等鍵版〉。

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

型錄列:API-8、FLOW-18、FLOW-20、FLOW-23、FLOW-24、STATE-10;FLOW-3 型錄已停用(2026-11-09,查兩輪找不到權威原文),這節裡它的測試只當範例,不當標準。斷言收到哪幾筆、順序、有沒有多的;共享類數上游被執行幾次。

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

型錄列:API-21、API-26、API-30。真的 OkHttp/Retrofit 打本機 MockWebServer;API-30 是 Ktor 用戶端,只有用 Ktor 的專案照抄〈依賴:Ktor〉〈測試:Ktor〉(見下)。MockWebServer 照專案實際解析到的 OkHttp 主版本挑:OkHttp 4 用〈依賴:OkHttp 4〉與〈測試:OkHttp 4〉,OkHttp 5 用〈依賴:OkHttp 5〉與〈測試:OkHttp 5〉,兩份測試只差 import 與排回應的寫法。不要讓 OkHttp 4 的專案配 `mockwebserver3`:Gradle 會在測試的類別路徑上默默把 OkHttp 升成 5(測試綠,但測的不是正式用的版本);用 `strictly` 釘住 4.12.0 時每支測試都 `NoClassDefFoundError: okhttp3/internal/_UtilJvmKt`(實驗實測)。走真的 socket,不在 `runTest` 的虛擬時間裡用 `withTimeout`(虛擬時間遇到真實 I/O 會直接跳到逾時點);要等真實時間就包進 `withContext(Dispatchers.Default)`。

API-30(Ktor 串流回應帶出 `execute { }` 區塊)那一份:真的 Ktor 用戶端(CIO 引擎)打 JDK 內建的 `com.sun.net.httpserver.HttpServer`,不用 MockWebServer——測試不碰 OkHttp,跟〈依賴:OkHttp 4〉或〈依賴:OkHttp 5〉放在同一個專案都照跑(兩種組合實跑過)。壞寫法讀 body 時丟 `ClosedByteChannelException: Channel was cancelled`,測試先 `runCatching` 接住,再斷言讀到的位元組數。Ktor 3.6.1 在 Kotlin 2.2.21 編得過。

### 依據

- MockWebServer:https://github.com/square/okhttp/tree/master/mockwebserver(README 的依賴行 `com.squareup.okhttp3:mockwebserver3`;OkHttp 4 對應的是 `com.squareup.okhttp3:mockwebserver`,套件 `okhttp3.mockwebserver`)
- API-21:OkHttp `Authenticator` 原始碼 KDoc「Returns null if the challenge cannot be satisfied」,範例 `while ((response = response.priorResponse()) != null)` 與「Give up, we've already failed to authenticate.」(https://github.com/square/okhttp/blob/master/okhttp/src/commonJvmAndroid/kotlin/okhttp3/Authenticator.kt);加鎖那一半照型錄 API-21 標準寫法 `mutex.withLock { if (token 已被別人刷新) 用新的 else refresh() }`(出處不全,KDoc 沒提並行);範本改用 `synchronized` 是旁證:`authenticate(route: Route?, response: Response): Request?` 是一般函式、不是 suspend(同一份原始碼的方法簽名),在它裡面用不了 `Mutex.withLock`
- API-26:Retrofit 對 204/205 不呼叫轉換器、body 是 null;型錄 API-26 標準寫法 `Response<Unit>`(出處不全)
- API-30:https://api.ktor.io/ktor-client-core/io.ktor.client.statement/-http-statement/execute.html 「The response object should not be accessed outside of block as it will be canceled upon block completion」

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

### 依賴:Ktor

只有用 Ktor 的專案加;跟〈依賴:OkHttp 4〉或〈依賴:OkHttp 5〉並存。

```kotlin
implementation("io.ktor:ktor-client-cio:3.6.1")
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

### 測試:Ktor

```kotlin
// 起手:kotlin-idioms test-templates T4
// API-30:Ktor 串流回應要在 execute { } 區塊裡讀完;打 JDK 內建的 HttpServer,不碰 OkHttp
import com.sun.net.httpserver.HttpServer
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import java.net.InetAddress
import java.net.InetSocketAddress
import kotlin.test.assertEquals
import kotlinx.coroutines.runBlocking
import org.junit.Test

class FileDownloaderTest {
    private val size = 2_000_000   // 大到一次讀不完,壞寫法才會讀到被取消的串流

    @Test
    fun download_reads_whole_body() = runBlocking {
        val server = HttpServer.create(InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0)
        server.createContext("/file") { ex ->
            ex.sendResponseHeaders(200, size.toLong())
            ex.responseBody.use { it.write(ByteArray(size) { 'x'.code.toByte() }) }
        }
        server.start()
        try {
            HttpClient(CIO).use { client ->
                val got = runCatching { FileDownloader(client).download("http://127.0.0.1:${server.address.port}/file") }
                assertEquals(size, got.getOrNull()?.size, "讀到的 body 不完整:${got.exceptionOrNull()}")
            }
        } finally {
            server.stop(0)
        }
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

### 好寫法:API-30 區塊內讀完

```kotlin
import io.ktor.client.HttpClient
import io.ktor.client.request.prepareGet
import io.ktor.client.statement.bodyAsBytes

class FileDownloader(private val client: HttpClient) {
    suspend fun download(url: String): ByteArray = client.prepareGet(url).execute { response -> response.bodyAsBytes() }
}
```

### 壞寫法:API-30 response 帶出區塊

```kotlin
import io.ktor.client.HttpClient
import io.ktor.client.request.prepareGet
import io.ktor.client.statement.bodyAsBytes

class FileDownloader(private val client: HttpClient) {
    suspend fun download(url: String): ByteArray {
        val response = client.prepareGet(url).execute { it }   // 區塊結束時串流就被取消
        return response.bodyAsBytes()
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
| 測試:Ktor | 好寫法:API-30 區塊內讀完 | 全綠:download_reads_whole_body |
| 測試:Ktor | 壞寫法:API-30 response 帶出區塊 | download_reads_whole_body 斷言紅「讀到的 body 不完整」 |

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

## T6 Room 與資料層

型錄列:DATA-17、DATA-19、DATA-21、DATA-65、DATA-69。跑在哪:模擬器(`app/src/androidTest`;官方不建議用 Robolectric 跑 Room,電腦上的 SQLite 版本可能跟手機不同)。

Room 3 已是穩定版,這一組寫兩份:〈依賴:Room 2〉配〈測試:Room 2〉、〈依賴:Room 3〉配〈測試:Room 3〉,照專案用的主版本挑一份。〈好寫法〉〈壞寫法〉是 Room 2 的寫法;Room 3 的專案改兩個地方(實驗就是這樣改了跑的):import 的 `androidx.room.` 換成 `androidx.room3.`、`Migration` 的 `migrate(connection: SQLiteConnection)` 加 `suspend`(Room 3 的 `Migration.migrate` 是 suspend)。

- DATA-17、DATA-19:`MigrationTestHelper` 一律用具名參數寫(`instrumentation = …, file = …, driver = …, databaseClass = AppDb::class`)——官方參考頁的參數順序是 `instrumentation, file, driver, databaseClass`,混位置參數容易編不過。一支一步升級(`createDatabase(舊版)` 用原始 SQL 塞資料 → `runMigrationsAndValidate(新版, 這一步的 Migration)` → 查資料還在),另一支從最舊版用 `addMigrations(*ALL_MIGRATIONS)` 開到最新(官方「include a test that covers all migrations」)。少一個 Migration 丟 `IllegalStateException`、SQL 寫錯也是 `IllegalStateException`(`Migration didn't properly handle`),都 `runCatching` 後斷言。這一組管的是「升了版本卻少 Migration 或 Migration 寫錯」;「改了 Entity 卻沒升版本」由推送前的 Room 守衛(`lumos room-guard`,同一版本的結構檔被改)擋,這裡不另測。
- 結構檔:`exportSchema = true`,Room Gradle 外掛(`room { schemaDirectory(…) }`,Room 3 是 `room3 { … }`)把每一版的結構寫到 `schemas/<資料庫類別完整名稱>/<版本>.json`,要提交進版控(舊版本的檔是專案歷史留下的,範本不附)。`MigrationTestHelper` 從 `androidTest` 的 assets 讀;Room Gradle 外掛自己會把結構檔目錄接成 androidTest 的 assets(`copyRoomSchemasToAndroidTestAssets…` 任務),不用再手動 `sourceSets["androidTest"].assets.srcDir(…)`(兩個主版本實測);沒用外掛、改用 KSP 參數 `room.schemaLocation` 的專案才要手動加。讀不到時丟 `FileNotFoundException: Cannot find the schema file in the assets folder … Missing file: AppDb/3.json`,被 `runCatching` 接住後是斷言紅、訊息帶這一句。
- 坑:升版後**第一次**建置就跑 `connectedDebugAndroidTest`,新版本的 json 這一輪才產生、複製到 androidTest assets 的任務已經先跑完,`runMigrationsAndValidate` 找不到最新版的 json(上一句的錯誤);再跑一次就綠。所以升版時先建置一次、把新的 json 提交,再跑升級測試(兩個主版本實測)。
- DATA-21 查 40000 個 id:SQLite 3.32.0 起參數上限 32766、之前 999,用 40000 讓新舊裝置都紅。壞寫法不分批,丟 `SQLiteException`(too many SQL variables),測試先 `runCatching` 接住再斷言查到的筆數;好寫法 `chunked(500)`。
- DATA-69 假 API 丟 `IOException`,斷言刷新失敗後本機清單不變。
- DATA-65 照型錄標準寫法「後寫贏」:本機有較新的修改時,較舊的伺服器資料不得蓋掉。衝突策略是業務決定,照情境表態換斷言。

### 依據

- DATA-17、DATA-19:https://developer.android.com/training/data-storage/room/migrating-db-versions 「an incorrectly defined migration can cause your app to crash」「you should include a test that covers all migrations」;缺路徑「an IllegalStateException occurs」;現版範例已是 `androidx.room3:room3-testing:3.0.3`
- `MigrationTestHelper` 參數:https://developer.android.com/reference/kotlin/androidx/room/testing/MigrationTestHelper(`instrumentation, file, driver, databaseClass`)
- Room 3 穩定:https://developer.android.com/jetpack/androidx/releases/room3(3.0.0 於 2026-07-01、3.0.3 於 2026-09-09)
- 不用 Robolectric:https://developer.android.com/training/data-storage/room/testing-db 「We don't recommend Android local unit tests with Robolectric」「create an in-memory version of your database」
- DATA-21:https://www.sqlite.org/limits.html 「defaults to 999 for SQLite versions prior to 3.32.0 (2020-05-22) or 32766 for SQLite versions after 3.32.0」
- DATA-65、DATA-69:https://developer.android.com/topic/architecture/data-layer/offline-first;型錄 DATA-65(「last write wins」)、DATA-69(成功後才換)標準寫法

### 依賴:Room 2

```kotlin
// build.gradle.kts 的 plugins { } 加
id("com.google.devtools.ksp") version "2.2.21-2.0.5" apply false
id("androidx.room") version "2.8.5" apply false
```

```kotlin
// app/build.gradle.kts 的 plugins { } 加
id("com.google.devtools.ksp")
id("androidx.room")
```

```kotlin
// app/build.gradle.kts 檔尾
room { schemaDirectory("$projectDir/schemas") }
```

```kotlin
implementation("androidx.room:room-runtime:2.8.5")
ksp("androidx.room:room-compiler:2.8.5")
androidTestImplementation("androidx.room:room-testing:2.8.5")
androidTestImplementation("androidx.test:core-ktx:1.7.0")
androidTestImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

### 依賴:Room 3

```kotlin
// build.gradle.kts 的 plugins { } 加
id("com.google.devtools.ksp") version "2.2.21-2.0.5" apply false
id("androidx.room3") version "3.0.3" apply false
```

```kotlin
// app/build.gradle.kts 的 plugins { } 加
id("com.google.devtools.ksp")
id("androidx.room3")
```

```kotlin
// app/build.gradle.kts 檔尾
room3 { schemaDirectory("$projectDir/schemas") }
```

```kotlin
implementation("androidx.room3:room3-runtime:3.0.3")
ksp("androidx.room3:room3-compiler:3.0.3")
androidTestImplementation("androidx.room3:room3-testing:3.0.3")
androidTestImplementation("androidx.test:core-ktx:1.7.0")
androidTestImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

### 測試:Room 2

```kotlin
// 起手:kotlin-idioms test-templates T6
import androidx.room.Room
import androidx.room.testing.MigrationTestHelper
import androidx.sqlite.driver.AndroidSQLiteDriver
import androidx.sqlite.execSQL
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class NoteMigrationTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val file = instrumentation.targetContext.getDatabasePath("migration-test.db")

    @get:Rule
    val helper = MigrationTestHelper(
        instrumentation = instrumentation,
        file = file,
        driver = AndroidSQLiteDriver(),
        databaseClass = AppDb::class,
    )

    // 每支測試從沒有資料庫檔開始:上一支留下的第 3 版檔案會讓 createDatabase(舊版) 去找 3→2 的路徑
    @Before
    fun deleteOldFile() {
        instrumentation.targetContext.deleteDatabase(file.name)
    }

    // DATA-19:一步一支,舊資料要還在
    @Test
    fun migrate_2_to_3_keeps_notes() {
        helper.createDatabase(2).apply {
            execSQL("INSERT INTO note (id, title, body) VALUES (1, '買牛奶', '兩瓶')")
            close()
        }
        val result = runCatching {
            helper.runMigrationsAndValidate(3, listOf(MIGRATION_2_3)).use { c ->
                c.prepare("SELECT title, body, updatedAt FROM note WHERE id = 1").use { st ->
                    st.step()
                    listOf(st.getText(0), st.getText(1), st.getLong(2).toString())
                }
            }
        }
        assertEquals("升級後的資料:${result.exceptionOrNull()}", listOf("買牛奶", "兩瓶", "0"), result.getOrNull())
    }

    // DATA-17、DATA-19:從最舊版開到最新,讓 Room 驗每一步與最後的結構
    @Test
    fun open_latest_from_oldest_with_all_migrations() {
        helper.createDatabase(1).apply {
            execSQL("INSERT INTO note (id, title) VALUES (1, '買牛奶')")
            close()
        }
        val result = runCatching {
            val db = Room.databaseBuilder(instrumentation.targetContext, AppDb::class.java, file.path)
                .setDriver(AndroidSQLiteDriver())
                .addMigrations(*ALL_MIGRATIONS)
                .build()
            try { runBlocking { db.notes().all().map { it.title } } } finally { db.close() }
        }
        assertEquals("開到最新版:${result.exceptionOrNull()}", listOf("買牛奶"), result.getOrNull())
    }
}
```

```kotlin
// 起手:kotlin-idioms test-templates T6
import androidx.room.Room
import androidx.sqlite.driver.AndroidSQLiteDriver
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class NoteRepositoryTest {
    private val db = Room.inMemoryDatabaseBuilder(ApplicationProvider.getApplicationContext(), AppDb::class.java)
        .setDriver(AndroidSQLiteDriver())
        .build()

    @After fun close() = db.close()

    // DATA-69:刷新失敗時本機資料還在
    @Test
    fun refresh_failure_keeps_local_notes() = runTest {
        db.notes().upsertAll(listOf(Note(1, "本機的")))
        runCatching { NoteRepository(db, FakeNoteApi(fail = true)).refresh() }
        assertEquals("刷新失敗後的本機清單", listOf("本機的"), db.notes().all().map { it.title })
    }

    // DATA-65:後寫贏,較舊的伺服器資料不蓋掉本機較新的修改
    @Test
    fun older_server_copy_does_not_overwrite_newer_local_edit() = runTest {
        db.notes().upsertAll(listOf(Note(1, "我剛改的", updatedAt = 200), Note(2, "舊標題", updatedAt = 100)))
        NoteRepository(db, FakeNoteApi()).mergeFromServer(listOf(Note(1, "伺服器舊版", updatedAt = 150), Note(2, "伺服器新版", updatedAt = 300)))
        assertEquals("合併後的標題", listOf("我剛改的", "伺服器新版"), db.notes().all().map { it.title })
    }

    // DATA-21:一次查 40000 個 id(超過新舊 SQLite 的參數上限)
    @Test
    fun query_40000_ids() = runTest {
        db.notes().upsertAll(listOf(Note(1, "a"), Note(20_000, "b"), Note(40_000, "c")))
        val found = runCatching { NoteRepository(db, FakeNoteApi()).byIds((1L..40_000L).toList()) }
        // 訊息只帶例外類別名:SQLiteException 的訊息含整串 SQL(4 萬個 ?),儀器報告的失敗文字截在 64KB,
        // 斷言框被截掉、收證判不到斷言(實驗實測)
        assertEquals("查到的筆數:${found.exceptionOrNull()?.javaClass?.name}", 3, found.getOrNull()?.size)
    }
}
```

### 測試:Room 3

```kotlin
// 起手:kotlin-idioms test-templates T6
// Room 3:createDatabase、runMigrationsAndValidate 是 suspend
import androidx.room3.Room
import androidx.room3.testing.MigrationTestHelper
import androidx.sqlite.driver.AndroidSQLiteDriver
import androidx.sqlite.execSQL
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class NoteMigrationTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val file = instrumentation.targetContext.getDatabasePath("migration-test.db")

    @get:Rule
    val helper = MigrationTestHelper(
        instrumentation = instrumentation,
        file = file,
        driver = AndroidSQLiteDriver(),
        databaseClass = AppDb::class,
    )

    // 每支測試從沒有資料庫檔開始:上一支留下的第 3 版檔案會讓 createDatabase(舊版) 去找 3→2 的路徑
    @Before
    fun deleteOldFile() {
        instrumentation.targetContext.deleteDatabase(file.name)
    }

    @Test
    fun migrate_2_to_3_keeps_notes() = runBlocking {
        helper.createDatabase(2).apply {
            execSQL("INSERT INTO note (id, title, body) VALUES (1, '買牛奶', '兩瓶')")
            close()
        }
        val result = runCatching {
            helper.runMigrationsAndValidate(3, listOf(MIGRATION_2_3)).use { c ->
                c.prepare("SELECT title, body, updatedAt FROM note WHERE id = 1").use { st ->
                    st.step()
                    listOf(st.getText(0), st.getText(1), st.getLong(2).toString())
                }
            }
        }
        assertEquals("升級後的資料:${result.exceptionOrNull()}", listOf("買牛奶", "兩瓶", "0"), result.getOrNull())
    }

    @Test
    fun open_latest_from_oldest_with_all_migrations() = runBlocking {
        helper.createDatabase(1).apply {
            execSQL("INSERT INTO note (id, title) VALUES (1, '買牛奶')")
            close()
        }
        val result = runCatching {
            val db = Room.databaseBuilder(instrumentation.targetContext, AppDb::class.java, file.path)
                .setDriver(AndroidSQLiteDriver())
                .addMigrations(*ALL_MIGRATIONS)
                .build()
            try { db.notes().all().map { it.title } } finally { db.close() }
        }
        assertEquals("開到最新版:${result.exceptionOrNull()}", listOf("買牛奶"), result.getOrNull())
    }
}
```

```kotlin
// 起手:kotlin-idioms test-templates T6
import androidx.room3.Room
import androidx.sqlite.driver.AndroidSQLiteDriver
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class NoteRepositoryTest {
    private val db = Room.inMemoryDatabaseBuilder(ApplicationProvider.getApplicationContext(), AppDb::class.java)
        .setDriver(AndroidSQLiteDriver())
        .build()

    @After fun close() = db.close()

    @Test
    fun refresh_failure_keeps_local_notes() = runTest {
        db.notes().upsertAll(listOf(Note(1, "本機的")))
        runCatching { NoteRepository(db, FakeNoteApi(fail = true)).refresh() }
        assertEquals("刷新失敗後的本機清單", listOf("本機的"), db.notes().all().map { it.title })
    }

    @Test
    fun older_server_copy_does_not_overwrite_newer_local_edit() = runTest {
        db.notes().upsertAll(listOf(Note(1, "我剛改的", updatedAt = 200), Note(2, "舊標題", updatedAt = 100)))
        NoteRepository(db, FakeNoteApi()).mergeFromServer(listOf(Note(1, "伺服器舊版", updatedAt = 150), Note(2, "伺服器新版", updatedAt = 300)))
        assertEquals("合併後的標題", listOf("我剛改的", "伺服器新版"), db.notes().all().map { it.title })
    }

    @Test
    fun query_40000_ids() = runTest {
        db.notes().upsertAll(listOf(Note(1, "a"), Note(20_000, "b"), Note(40_000, "c")))
        val found = runCatching { NoteRepository(db, FakeNoteApi()).byIds((1L..40_000L).toList()) }
        // 訊息只帶例外類別名:SQLiteException 的訊息含整串 SQL(4 萬個 ?),儀器報告的失敗文字截在 64KB,
        // 斷言框被截掉、收證判不到斷言(實驗實測)
        assertEquals("查到的筆數:${found.exceptionOrNull()?.javaClass?.name}", 3, found.getOrNull()?.size)
    }
}
```

### 假依賴

```kotlin
import java.io.IOException

class FakeNoteApi(private val fail: Boolean = false, private val notes: List<Note> = emptyList()) : NoteApi {
    override suspend fun fetchAll(): List<Note> {
        if (fail) throw IOException("離線")
        return notes
    }
}
```

### 好寫法

```kotlin
import androidx.room.ColumnInfo
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase
import androidx.room.Transaction

// 第 3 版:第 2 版加了 body,第 3 版加了 updatedAt
@Entity(tableName = "note")
data class Note(
    @PrimaryKey val id: Long,
    val title: String,
    @ColumnInfo(defaultValue = "") val body: String = "",
    @ColumnInfo(defaultValue = "0") val updatedAt: Long = 0,
)

@Dao
interface NoteDao {
    @Query("SELECT * FROM note ORDER BY id") suspend fun all(): List<Note>
    @Query("SELECT * FROM note WHERE id IN (:ids)") suspend fun byIds(ids: List<Long>): List<Note>
    @Insert(onConflict = OnConflictStrategy.REPLACE) suspend fun upsertAll(notes: List<Note>)
    @Query("DELETE FROM note") suspend fun clear()

    @Transaction
    suspend fun replaceAll(notes: List<Note>) {
        clear()
        upsertAll(notes)
    }
}

@Database(entities = [Note::class], version = 3, exportSchema = true)
abstract class AppDb : RoomDatabase() {
    abstract fun notes(): NoteDao
}
```

```kotlin
import androidx.room.migration.Migration
import androidx.sqlite.SQLiteConnection
import androidx.sqlite.execSQL

val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(connection: SQLiteConnection) {
        connection.execSQL("ALTER TABLE note ADD COLUMN body TEXT NOT NULL DEFAULT ''")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(connection: SQLiteConnection) {
        connection.execSQL("ALTER TABLE note ADD COLUMN updatedAt INTEGER NOT NULL DEFAULT 0")
    }
}

val ALL_MIGRATIONS = arrayOf(MIGRATION_1_2, MIGRATION_2_3)
```

```kotlin
interface NoteApi {
    suspend fun fetchAll(): List<Note>
}

class NoteRepository(private val db: AppDb, private val api: NoteApi) {
    // DATA-69:先拿到新資料,成功後才在交易裡換掉
    suspend fun refresh() {
        val fresh = api.fetchAll()
        db.notes().replaceAll(fresh)
    }

    // DATA-21:分批查,每批遠低於參數上限
    suspend fun byIds(ids: List<Long>): List<Note> = ids.chunked(500).flatMap { db.notes().byIds(it) }

    // DATA-65:後寫贏,伺服器那份比本機舊就不寫
    suspend fun mergeFromServer(server: List<Note>) {
        val local = byIds(server.map { it.id }).associateBy { it.id }
        db.notes().upsertAll(server.filter { s -> (local[s.id]?.updatedAt ?: Long.MIN_VALUE) <= s.updatedAt })
    }
}
```

### 壞寫法:DATA-17 少一個 Migration

```kotlin
import androidx.room.migration.Migration
import androidx.sqlite.SQLiteConnection
import androidx.sqlite.execSQL

val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(connection: SQLiteConnection) {
        connection.execSQL("ALTER TABLE note ADD COLUMN body TEXT NOT NULL DEFAULT ''")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(connection: SQLiteConnection) {
        connection.execSQL("ALTER TABLE note ADD COLUMN updatedAt INTEGER NOT NULL DEFAULT 0")
    }
}

val ALL_MIGRATIONS = arrayOf(MIGRATION_1_2)   // 升到第 3 版時忘了登記 2→3
```

### 壞寫法:DATA-19 Migration 的 SQL 寫錯

```kotlin
import androidx.room.migration.Migration
import androidx.sqlite.SQLiteConnection
import androidx.sqlite.execSQL

val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(connection: SQLiteConnection) {
        connection.execSQL("ALTER TABLE note ADD COLUMN body TEXT NOT NULL DEFAULT ''")
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(connection: SQLiteConnection) {
        connection.execSQL("ALTER TABLE note ADD COLUMN updatedAt INTEGER")   // 少了 NOT NULL DEFAULT 0,跟 Entity 不符
    }
}

val ALL_MIGRATIONS = arrayOf(MIGRATION_1_2, MIGRATION_2_3)
```

### 壞寫法:DATA-21 不分批

```kotlin
interface NoteApi {
    suspend fun fetchAll(): List<Note>
}

class NoteRepository(private val db: AppDb, private val api: NoteApi) {
    suspend fun refresh() {
        val fresh = api.fetchAll()
        db.notes().replaceAll(fresh)
    }

    suspend fun byIds(ids: List<Long>): List<Note> = db.notes().byIds(ids)   // 參數數量沒上限

    suspend fun mergeFromServer(server: List<Note>) {
        val local = server.map { it.id }.chunked(500).flatMap { db.notes().byIds(it) }.associateBy { it.id }
        db.notes().upsertAll(server.filter { s -> (local[s.id]?.updatedAt ?: Long.MIN_VALUE) <= s.updatedAt })
    }
}
```

### 壞寫法:DATA-65 伺服器資料直接覆蓋

```kotlin
interface NoteApi {
    suspend fun fetchAll(): List<Note>
}

class NoteRepository(private val db: AppDb, private val api: NoteApi) {
    suspend fun refresh() {
        val fresh = api.fetchAll()
        db.notes().replaceAll(fresh)
    }

    suspend fun byIds(ids: List<Long>): List<Note> = ids.chunked(500).flatMap { db.notes().byIds(it) }

    suspend fun mergeFromServer(server: List<Note>) {
        db.notes().upsertAll(server)   // 本機較新的修改被蓋掉
    }
}
```

### 壞寫法:DATA-69 先清本機再打 API

```kotlin
interface NoteApi {
    suspend fun fetchAll(): List<Note>
}

class NoteRepository(private val db: AppDb, private val api: NoteApi) {
    suspend fun refresh() {
        db.notes().clear()   // 先清,API 失敗時本機就空了
        db.notes().upsertAll(api.fetchAll())
    }

    suspend fun byIds(ids: List<Long>): List<Note> = ids.chunked(500).flatMap { db.notes().byIds(it) }

    suspend fun mergeFromServer(server: List<Note>) {
        val local = byIds(server.map { it.id }).associateBy { it.id }
        db.notes().upsertAll(server.filter { s -> (local[s.id]?.updatedAt ?: Long.MIN_VALUE) <= s.updatedAt })
    }
}
```

### 紅綠矩陣

舊版本的結構檔(`schemas/AppDb/1.json`、`2.json`)是實驗前先用第 1、2 版的 Entity 建置產生的,代表專案歷史留下的檔。

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試:Room 2 | 好寫法 | 全綠:migrate_2_to_3_keeps_notes、open_latest_from_oldest_with_all_migrations、refresh_failure_keeps_local_notes、older_server_copy_does_not_overwrite_newer_local_edit、query_40000_ids |
| 測試:Room 2 | 壞寫法:DATA-17 少一個 Migration | open_latest_from_oldest_with_all_migrations 斷言紅「開到最新版」;其他綠 |
| 測試:Room 2 | 壞寫法:DATA-19 Migration 的 SQL 寫錯 | migrate_2_to_3_keeps_notes 斷言紅「升級後的資料」;open_latest_from_oldest_with_all_migrations 斷言紅「開到最新版」;其他綠 |
| 測試:Room 2 | 壞寫法:DATA-21 不分批 | query_40000_ids 斷言紅「查到的筆數」;其他綠 |
| 測試:Room 2 | 壞寫法:DATA-65 伺服器資料直接覆蓋 | older_server_copy_does_not_overwrite_newer_local_edit 斷言紅「合併後的標題」;其他綠 |
| 測試:Room 2 | 壞寫法:DATA-69 先清本機再打 API | refresh_failure_keeps_local_notes 斷言紅「刷新失敗後的本機清單」;其他綠 |
| 測試:Room 3 | 好寫法 | 全綠:migrate_2_to_3_keeps_notes、open_latest_from_oldest_with_all_migrations、refresh_failure_keeps_local_notes、older_server_copy_does_not_overwrite_newer_local_edit、query_40000_ids |
| 測試:Room 3 | 壞寫法:DATA-17 少一個 Migration | open_latest_from_oldest_with_all_migrations 斷言紅「開到最新版」;其他綠 |
| 測試:Room 3 | 壞寫法:DATA-19 Migration 的 SQL 寫錯 | migrate_2_to_3_keeps_notes 斷言紅「升級後的資料」;open_latest_from_oldest_with_all_migrations 斷言紅「開到最新版」;其他綠 |
| 測試:Room 3 | 壞寫法:DATA-21 不分批 | query_40000_ids 斷言紅「查到的筆數」;其他綠 |
| 測試:Room 3 | 壞寫法:DATA-65 伺服器資料直接覆蓋 | older_server_copy_does_not_overwrite_newer_local_edit 斷言紅「合併後的標題」;其他綠 |
| 測試:Room 3 | 壞寫法:DATA-69 先清本機再打 API | refresh_failure_keeps_local_notes 斷言紅「刷新失敗後的本機清單」;其他綠 |

## T7 Paging

型錄列:DATA-58、DATA-60。跑在哪:〈測試〉(DATA-58)Robolectric(`app/src/test`);〈測試:DATA-60 RemoteMediator〉模擬器(`app/src/androidTest`,要真的 Room,官方不建議用 Robolectric 跑 Room)。

- DATA-58:對 ViewModel 的分頁流用 paging-testing 的 `asSnapshot { }` 收,收的途中改篩選條件(`combine` 的另一邊發新值)。沒先 `cachedIn` 就 `combine` 的壞寫法,同一份 `PagingData` 被收第二次,丟 `IllegalStateException: Attempt to collect twice from pageEventFlow`;測試先 `runCatching` 接住再斷言快照內容。`viewModelScope` 用 `Dispatchers.Main`,測試要先 `Dispatchers.setMain(…)`。
- DATA-60:照官方 RemoteMediator 測試頁,直接呼叫 `mediator.load(LoadType.REFRESH, pagingState)`,配記憶體資料庫與假 API。四個情境:有下一頁(`endOfPaginationReached == false`)、空回應(`true`)、有資料的最後一頁(`true`;只看「資料是不是空的」的壞寫法在這裡錯)、API 丟例外(`MediatorResult.Error`)。

### 依據

- https://developer.android.com/topic/libraries/architecture/paging/test 「include the paging-testing dependency. It contains the asSnapshot extension」;RemoteMediator:「the endOfPaginationReached property should be true」
- DATA-58:https://developer.android.com/reference/kotlin/androidx/paging/package-summary#(kotlinx.coroutines.flow.Flow).cachedIn(kotlinx.coroutines.CoroutineScope) `cachedIn` 讓同一個分頁流可以被多處或重新收;型錄 DATA-58 標準寫法
- DATA-60:型錄 DATA-60 標準寫法 `MediatorResult.Success(endOfPaginationReached = response.nextKey == null)`

### 依賴

```kotlin
// build.gradle.kts 的 plugins { } 加
id("com.google.devtools.ksp") version "2.2.21-2.0.5" apply false
```

```kotlin
// app/build.gradle.kts 的 plugins { } 加
id("com.google.devtools.ksp")
```

```kotlin
implementation("androidx.paging:paging-runtime-ktx:3.5.3")
implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.10.0")
// RemoteMediator 寫進真的 Room(DATA-60);只做 DATA-58 的專案不用這三行與 KSP
implementation("androidx.room:room-runtime:2.8.5")
implementation("androidx.room:room-paging:2.8.5")
ksp("androidx.room:room-compiler:2.8.5")
testImplementation("androidx.paging:paging-testing:3.5.3")
testImplementation("org.robolectric:robolectric:4.17")
testImplementation("androidx.test.ext:junit:1.3.0")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

```properties
# app/src/test/resources/robolectric.properties
sdk=34
```

Robolectric 組都要連這個檔一起抄:`targetSdk = 36` 時 Robolectric 預設用 SDK 36 跑、要 JDK 21,JDK 17 上整個測試類別例外紅(見〈Android 實驗專案骨架〉)。

### 依賴:DATA-60 RemoteMediator

在〈依賴〉之外再加(模擬器上的測試):

```kotlin
androidTestImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T7
import androidx.paging.testing.asSnapshot
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.assertEquals
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.Test
import org.junit.runner.RunWith

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(AndroidJUnit4::class)
class FeedViewModelTest {
    @BeforeTest fun setUp() = Dispatchers.setMain(UnconfinedTestDispatcher())
    @AfterTest fun tearDown() = Dispatchers.resetMain()

    // DATA-58:收的途中改篩選,分頁流還能用(不丟 Attempt to collect twice)
    @Test
    fun filter_change_while_collecting_keeps_paging_alive() = runTest {
        val vm = FeedViewModel(FeedRepository(List(100) { "item-$it" }))
        val snapshot = runCatching { vm.items.asSnapshot { vm.setQuery("-1") } }
        assertEquals(listOf("item-1") + List(10) { "item-1$it" }, snapshot.getOrNull(), "篩選後的快照:${snapshot.exceptionOrNull()}")
    }
}
```

### 測試:DATA-60 RemoteMediator

```kotlin
// 起手:kotlin-idioms test-templates T7
import androidx.paging.ExperimentalPagingApi
import androidx.paging.LoadType
import androidx.paging.PagingConfig
import androidx.paging.PagingState
import androidx.paging.RemoteMediator.MediatorResult
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@OptIn(ExperimentalPagingApi::class)
@RunWith(AndroidJUnit4::class)
class ArticleMediatorTest {
    private val db = Room.inMemoryDatabaseBuilder(ApplicationProvider.getApplicationContext(), ArticleDb::class.java).build()
    private val state = PagingState<Int, Article>(listOf(), null, PagingConfig(10), 10)

    @After fun close() = db.close()

    private suspend fun refresh(api: FakeArticleApi) = ArticleMediator(db, api).load(LoadType.REFRESH, state)

    @Test
    fun more_pages_not_end() = runTest {
        val r = refresh(FakeArticleApi(items = List(10) { "a$it" }, nextKey = 2))
        assertTrue("有下一頁時要是 Success(false):$r", r is MediatorResult.Success && !r.endOfPaginationReached)
    }

    @Test
    fun empty_response_is_end() = runTest {
        val r = refresh(FakeArticleApi(items = emptyList(), nextKey = null))
        assertTrue("空回應要是 Success(true):$r", r is MediatorResult.Success && r.endOfPaginationReached)
    }

    @Test
    fun last_page_with_items_is_end() = runTest {
        val r = refresh(FakeArticleApi(items = List(3) { "a$it" }, nextKey = null))
        assertTrue("有資料的最後一頁要是 Success(true):$r", r is MediatorResult.Success && r.endOfPaginationReached)
        assertEquals(3, db.articles().count())
    }

    @Test
    fun api_error_is_error() = runTest {
        val r = refresh(FakeArticleApi(items = emptyList(), nextKey = null, fail = true))
        assertTrue("API 丟例外要是 Error:$r", r is MediatorResult.Error)
    }
}
```

### 假依賴

```kotlin
import java.io.IOException

class FakeArticleApi(private val items: List<String>, private val nextKey: Int?, private val fail: Boolean = false) : ArticleApi {
    override suspend fun page(key: Int): ArticlePage {
        if (fail) throw IOException("離線")
        return ArticlePage(items, nextKey)
    }
}
```

### 好寫法

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.PagingData
import androidx.paging.cachedIn
import androidx.paging.filter
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.combine

class FeedRepository(private val all: List<String>) {
    fun pager() = Pager(PagingConfig(pageSize = 20, enablePlaceholders = false)) { ListPagingSource(all) }
}

// DATA-58:先 cachedIn 再 combine;cachedIn 會多播,重新收拿到的是可以再收的 PagingData
class FeedViewModel(repo: FeedRepository) : ViewModel() {
    private val query = MutableStateFlow("")
    val items: Flow<PagingData<String>> = repo.pager().flow
        .cachedIn(viewModelScope)
        .combine(query) { data, q -> data.filter { q.isEmpty() || it.contains(q) } }

    fun setQuery(q: String) { query.value = q }
}
```

```kotlin
import androidx.paging.PagingSource
import androidx.paging.PagingState

class ListPagingSource(private val all: List<String>) : PagingSource<Int, String>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, String> {
        val start = params.key ?: 0
        val end = minOf(start + params.loadSize, all.size)
        return LoadResult.Page(all.subList(start, end), prevKey = null, nextKey = if (end < all.size) end else null)
    }

    override fun getRefreshKey(state: PagingState<Int, String>): Int? = null
}
```

```kotlin
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase

@Entity data class Article(@PrimaryKey val id: String)

data class ArticlePage(val items: List<String>, val nextKey: Int?)

interface ArticleApi { suspend fun page(key: Int): ArticlePage }

@Dao interface ArticleDao {
    @Insert suspend fun insertAll(items: List<Article>)
    @Query("DELETE FROM Article") suspend fun clear()
    @Query("SELECT COUNT(*) FROM Article") suspend fun count(): Int
}

@Database(entities = [Article::class], version = 1, exportSchema = false)
abstract class ArticleDb : RoomDatabase() { abstract fun articles(): ArticleDao }
```

```kotlin
import androidx.paging.ExperimentalPagingApi
import androidx.paging.LoadType
import androidx.paging.PagingState
import androidx.paging.RemoteMediator
import androidx.room.withTransaction

// DATA-60:有沒有下一頁看伺服器給的 nextKey
@OptIn(ExperimentalPagingApi::class)
class ArticleMediator(private val db: ArticleDb, private val api: ArticleApi) : RemoteMediator<Int, Article>() {
    override suspend fun load(loadType: LoadType, state: PagingState<Int, Article>): MediatorResult = try {
        val page = api.page(key = 1)
        db.withTransaction {
            if (loadType == LoadType.REFRESH) db.articles().clear()
            db.articles().insertAll(page.items.map { Article(it) })
        }
        MediatorResult.Success(endOfPaginationReached = page.nextKey == null)
    } catch (e: java.io.IOException) {
        MediatorResult.Error(e)
    }
}
```

### 壞寫法:DATA-58 沒 cachedIn 就 combine

```kotlin
import androidx.lifecycle.ViewModel
import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.PagingData
import androidx.paging.filter
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.combine

class FeedRepository(private val all: List<String>) {
    fun pager() = Pager(PagingConfig(pageSize = 20, enablePlaceholders = false)) { ListPagingSource(all) }
}

class FeedViewModel(repo: FeedRepository) : ViewModel() {
    private val query = MutableStateFlow("")
    val items: Flow<PagingData<String>> = repo.pager().flow   // 少了 cachedIn:篩選一變,同一份 PagingData 被收第二次
        .combine(query) { data, q -> data.filter { q.isEmpty() || it.contains(q) } }

    fun setQuery(q: String) { query.value = q }
}
```

### 壞寫法:DATA-60 永遠回 false

```kotlin
import androidx.paging.ExperimentalPagingApi
import androidx.paging.LoadType
import androidx.paging.PagingState
import androidx.paging.RemoteMediator
import androidx.room.withTransaction

@OptIn(ExperimentalPagingApi::class)
class ArticleMediator(private val db: ArticleDb, private val api: ArticleApi) : RemoteMediator<Int, Article>() {
    override suspend fun load(loadType: LoadType, state: PagingState<Int, Article>): MediatorResult = try {
        val page = api.page(key = 1)
        db.withTransaction {
            if (loadType == LoadType.REFRESH) db.articles().clear()
            db.articles().insertAll(page.items.map { Article(it) })
        }
        MediatorResult.Success(endOfPaginationReached = false)
    } catch (e: java.io.IOException) {
        MediatorResult.Error(e)
    }
}
```

### 壞寫法:DATA-60 看資料是不是空的

```kotlin
import androidx.paging.ExperimentalPagingApi
import androidx.paging.LoadType
import androidx.paging.PagingState
import androidx.paging.RemoteMediator
import androidx.room.withTransaction

@OptIn(ExperimentalPagingApi::class)
class ArticleMediator(private val db: ArticleDb, private val api: ArticleApi) : RemoteMediator<Int, Article>() {
    override suspend fun load(loadType: LoadType, state: PagingState<Int, Article>): MediatorResult = try {
        val page = api.page(key = 1)
        db.withTransaction {
            if (loadType == LoadType.REFRESH) db.articles().clear()
            db.articles().insertAll(page.items.map { Article(it) })
        }
        MediatorResult.Success(endOfPaginationReached = page.items.isEmpty())   // 有資料的最後一頁會再要一次
    } catch (e: java.io.IOException) {
        MediatorResult.Error(e)
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:filter_change_while_collecting_keeps_paging_alive |
| 測試 | 壞寫法:DATA-58 沒 cachedIn 就 combine | filter_change_while_collecting_keeps_paging_alive 斷言紅「Attempt to collect twice」 |
| 測試:DATA-60 RemoteMediator | 好寫法 | 全綠:more_pages_not_end、empty_response_is_end、last_page_with_items_is_end、api_error_is_error |
| 測試:DATA-60 RemoteMediator | 壞寫法:DATA-60 永遠回 false | empty_response_is_end 斷言紅「空回應要是 Success(true)」;last_page_with_items_is_end 斷言紅「有資料的最後一頁要是 Success(true)」;其他綠 |
| 測試:DATA-60 RemoteMediator | 壞寫法:DATA-60 看資料是不是空的 | last_page_with_items_is_end 斷言紅「有資料的最後一頁要是 Success(true)」;其他綠 |

## T8 WorkManager

型錄列:DATA-38、DATA-39。跑在哪:Robolectric(`app/src/test`)。用 `TestListenableWorkerBuilder` 建 `CoroutineWorker`,在測試裡直接呼叫 `doWork()`,虛擬時間推進、取消,再用假依賴的計數斷言。

- DATA-38 只做 `CoroutineWorker` 版(型錄標準寫法:它由框架自動取消)。被測 Worker 的迴圈次數有上限(從假設定讀,範本用 50),每圈呼叫假來源一次、`delay`,跑完呼叫 `markDone()`,錯誤時呼叫 `recordError()`,`finally` 關資源。測試在 `backgroundScope` 啟動 `doWork()`、推進兩圈、取消、`runCurrent()`,斷言「取消後假來源的呼叫次數沒再增加、`markDone` 0 次、`recordError` 0 次、資源 `close` 恰好 1 次」——全部是計數比較,不靠接例外:取消的例外丟在 `backgroundScope` 的協程裡,測試本體接不到。
- 迴圈次數一定要有上限:迴圈裡吞掉取消的壞寫法,取消後每圈的 `delay` 立刻丟例外又被吞,沒上限就空轉卡死(r1 可行性席實跑在 Robolectric 卡 190 秒以上、`runTest` 的逾時沒生效);有上限它會跑完剩下的圈數並 `markDone`,斷言紅。
- 一般 `Worker` 的 `isStopped` 從測試觸發不了(官方測試頁沒示範,`stop` 是框架內部方法),這一組不涵蓋。
- DATA-39 斷言被測程式產的 `Data` 序列化後小於 `Data.MAX_DATA_BYTES`;超過時 WorkManager 丟 `IllegalStateException`,測試先 `runCatching` 接住再斷言。

### 依據

- https://developer.android.com/develop/background-work/background-tasks/testing/persistent/worker-impl 「To test a ListenableWorker or its variants (CoroutineWorker and RxWorker), use TestListenableWorkerBuilder」
- DATA-38:https://developer.android.com/develop/background-work/background-tasks/persistent/threading/coroutineworker 「CoroutineWorkers handle stoppages automatically by cancelling the coroutine」
- DATA-39:https://developer.android.com/reference/androidx/work/Data 「This class will throw IllegalStateExceptions if you try to serialize or deserialize past this limit」

### 依賴

```kotlin
implementation("androidx.work:work-runtime-ktx:2.11.2")
testImplementation("androidx.work:work-testing:2.11.2")
testImplementation("org.robolectric:robolectric:4.17")
testImplementation("androidx.test:core-ktx:1.7.0")
testImplementation("androidx.test.ext:junit:1.3.0")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

```properties
# app/src/test/resources/robolectric.properties
sdk=34
```

Robolectric 組都要連這個檔一起抄:`targetSdk = 36` 時 Robolectric 預設用 SDK 36 跑、要 JDK 21,JDK 17 上整個測試類別例外紅(見〈Android 實驗專案骨架〉)。

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T8
import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.work.Data
import androidx.work.ListenableWorker
import androidx.work.WorkerFactory
import androidx.work.WorkerParameters
import androidx.work.testing.TestListenableWorkerBuilder
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Test
import org.junit.runner.RunWith

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(AndroidJUnit4::class)
class SyncWorkerTest {
    private fun worker(deps: FakeSyncDeps): SyncWorker =
        TestListenableWorkerBuilder<SyncWorker>(ApplicationProvider.getApplicationContext())
            .setWorkerFactory(object : WorkerFactory() {
                override fun createWorker(appContext: Context, workerClassName: String, workerParameters: WorkerParameters) =
                    SyncWorker(appContext, workerParameters, deps)
            })
            .build()

    // DATA-38:取消後不再跑下一圈、不記成錯誤、資源關一次
    @Test
    fun cancel_stops_loop_without_error_and_closes_once() = runTest(timeout = 10.seconds) {
        val deps = FakeSyncDeps(maxRounds = 50)
        val job = backgroundScope.launch { worker(deps).doWork() }
        runCurrent()
        advanceTimeBy(1_500)   // 跑過兩圈(第 0 秒、第 1 秒各一次 fetch)
        runCurrent()
        val fetchedBeforeCancel = deps.fetchCalls
        job.cancel()
        runCurrent()
        advanceTimeBy(60_000)
        runCurrent()
        assertEquals(2, fetchedBeforeCancel, "取消前應跑了兩圈")
        assertEquals(fetchedBeforeCancel, deps.fetchCalls, "取消後還在跑下一圈")
        assertEquals(0, deps.doneCalls, "取消後不該 markDone")
        assertEquals(0, deps.errorCalls, "取消不該記成錯誤")
        assertEquals(1, deps.closeCalls, "資源要關恰好一次")
    }

    // DATA-39:輸出的 Data 序列化後在上限內
    @Test
    fun output_data_fits_limit() = runTest(timeout = 10.seconds) {
        val deps = FakeSyncDeps(maxRounds = 1, idsPerFetch = 2_000)
        val result = runCatching { worker(deps).doWork() }
        val out = (result.getOrNull() as? ListenableWorker.Result.Success)?.outputData
        val size = runCatching { out!!.toByteArray().size }
        assertTrue(size.getOrNull()?.let { it < Data.MAX_DATA_BYTES } == true,
            "輸出 Data 超過 ${Data.MAX_DATA_BYTES} bytes 或沒成功:result=$result size=$size")
    }
}
```

### 假依賴

```kotlin
import java.io.Closeable

class FakeSyncDeps(override val maxRounds: Int, private val idsPerFetch: Int = 3) : SyncDeps {
    var fetchCalls = 0
    var doneCalls = 0
    var errorCalls = 0
    var closeCalls = 0

    override suspend fun fetch(): List<String> {
        fetchCalls++
        return List(idsPerFetch) { "item-$fetchCalls-$it" }
    }
    override fun markDone() { doneCalls++ }
    override fun recordError() { errorCalls++ }
    override fun open(): Closeable = Closeable { closeCalls++ }
}
```

### 好寫法

```kotlin
import java.io.Closeable

interface SyncDeps {
    val maxRounds: Int
    suspend fun fetch(): List<String>
    fun markDone()
    fun recordError()
    fun open(): Closeable
}
```

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import kotlinx.coroutines.delay

class SyncWorker(context: Context, params: WorkerParameters, private val deps: SyncDeps) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val resource = deps.open()
        try {
            var synced = 0
            repeat(deps.maxRounds) {
                synced += deps.fetch().size
                delay(1_000)
            }
            deps.markDone()
            return Result.success(workDataOf("synced" to synced))   // DATA-39:只回摘要,明細寫進資料庫
        } catch (e: java.io.IOException) {
            deps.recordError()   // 只接 I/O 錯誤;取消照常往外丟
            return Result.retry()
        } finally {
            resource.close()
        }
    }
}
```

### 壞寫法:DATA-38 迴圈裡吞取消

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import kotlinx.coroutines.delay

class SyncWorker(context: Context, params: WorkerParameters, private val deps: SyncDeps) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val resource = deps.open()
        try {
            var synced = 0
            repeat(deps.maxRounds) {
                synced += deps.fetch().size
                try { delay(1_000) } catch (e: Exception) { }   // 取消的例外也被吞,迴圈繼續跑
            }
            deps.markDone()
            return Result.success(workDataOf("synced" to synced))
        } finally {
            resource.close()
        }
    }
}
```

### 壞寫法:DATA-38 迴圈外吞取消

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import kotlinx.coroutines.delay

class SyncWorker(context: Context, params: WorkerParameters, private val deps: SyncDeps) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val resource = deps.open()
        try {
            var synced = 0
            repeat(deps.maxRounds) {
                synced += deps.fetch().size
                delay(1_000)
            }
            deps.markDone()
            return Result.success(workDataOf("synced" to synced))
        } catch (e: Exception) {   // CancellationException 也被當成錯誤
            deps.recordError()
            return Result.failure()
        } finally {
            resource.close()
        }
    }
}
```

### 壞寫法:DATA-39 明細塞進 Data

```kotlin
import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import kotlinx.coroutines.delay

class SyncWorker(context: Context, params: WorkerParameters, private val deps: SyncDeps) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val resource = deps.open()
        try {
            val ids = mutableListOf<String>()
            repeat(deps.maxRounds) {
                ids += deps.fetch()
                delay(1_000)
            }
            deps.markDone()
            return Result.success(workDataOf("ids" to ids.toTypedArray()))   // 整份明細放進 Data
        } catch (e: java.io.IOException) {
            deps.recordError()
            return Result.retry()
        } finally {
            resource.close()
        }
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:cancel_stops_loop_without_error_and_closes_once、output_data_fits_limit |
| 測試 | 壞寫法:DATA-38 迴圈裡吞取消 | cancel_stops_loop_without_error_and_closes_once 斷言紅「取消後還在跑下一圈」;其他綠 |
| 測試 | 壞寫法:DATA-38 迴圈外吞取消 | cancel_stops_loop_without_error_and_closes_once 斷言紅「取消不該記成錯誤」;其他綠 |
| 測試 | 壞寫法:DATA-39 明細塞進 Data | output_data_fits_limit 斷言紅「超過 10240 bytes」;其他綠 |

## T9 Compose UI

型錄列:STATE-12、STATE-23、UI-36、UI-52、ARCH-2、ARCH-3、TEST-32,無障礙 UI-106、UI-110;DATA-63 型錄已停用(2026-11-09,查兩輪找不到權威原文),這節裡它的測試只當範例,不當標準。TEST-29(無限動畫讓測試等不到 idle)的〈測試〉與〈壞測試〉留著當對照,但型錄那列沒接:Compose 1.11 下讓時鐘自動推進的〈壞測試〉在 Robolectric 與模擬器都綠、沒卡住(實驗實測),這一組抓不到差別,型錄寫「未接(儀器批)」。跑在哪:〈測試〉10 支在 Robolectric(`app/src/test`;上面八列各一支、DATA-63 多一支「真的沒資料」、TEST-29 對照一支);〈測試:無障礙〉只在模擬器(`app/src/androidTest`)——無障礙檢查在 Robolectric 不報(好寫法、壞寫法都綠,實驗實測),對比檢查要實際算繪。

`createComposeRule()` 掛畫面,假 ViewModel 直接推狀態。幾個寫法要點:

- STATE-12 不用 `waitUntil { vm.userMessage.value == null }`:等不到時丟的是 `ComposeTimeoutException`,不是斷言紅(實驗實測);改成推時鐘(超過 Snackbar 的顯示時間)後直接斷言。
- STATE-23 存不進 `Bundle` 的型別在存狀態時丟例外,`emulateSavedInstanceStateRestore()` 包 `runCatching` 再斷言。
- ARCH-3 先 `mainClock.autoAdvance = false`,同一個節點 `performClick()` 兩次(中間不推時鐘)後再推時鐘。時鐘自動推進時第一次點擊的轉場立刻跑完、按鈕已離開畫面,第二次點擊丟「Failed to inject touch input. The node is no longer in the tree」,好寫法壞寫法一起紅、分不出來(實驗實測)。
- TEST-29、TEST-32 是測試的寫法:〈測試〉照正確寫法,〈壞測試:…〉示範錯的寫法對正確程式會怎樣。TEST-32 的〈壞測試〉紅的是 Compose 測試自己的 `AssertionError`:Robolectric 的 XML 有型別、收證算斷言;模擬器的儀器報告沒有 `org.junit.Assert` 框、收證不算(實驗實測)——這是錯的寫法示範,不影響〈測試〉。

### 依據

- https://developer.android.com/develop/ui/compose/testing/synchronization 「set the autoAdvance property in the mainClock to false」
- https://developer.android.com/develop/ui/compose/testing/apis 「The useUnmergedTree parameter is available in all finders」
- STATE-23:https://developer.android.com/develop/ui/compose/state-saving 「There are specific APIs to achieve this, such as StateRestorationTester」
- STATE-12、ARCH-2:https://developer.android.com/topic/architecture/ui-layer/events 「the UI needs to notify the ViewModel of that」;ARCH-3 `dropUnlessResumed`:同頁與 https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/package-summary
- UI-36:https://developer.android.com/develop/ui/compose/side-effects#snapshotFlow 「converts Compose State<T> objects into a cold Flow」
- UI-52:https://developer.android.com/develop/ui/compose/lists#avoid-0-pixel-items
- DATA-63:https://developer.android.com/topic/libraries/architecture/paging/load-state
- 無障礙:https://developer.android.com/develop/ui/compose/accessibility/testing 「Other available checks look for accessibility issues with color contrast, small touch target size」
- ARCH-2 用 `TestNavHostController`:https://developer.android.com/guide/navigation/testing

### 依賴

```kotlin
// app/build.gradle.kts 的 plugins { } 加
id("org.jetbrains.kotlin.plugin.compose")
```

```kotlin
// app/build.gradle.kts 的 android { } 加
buildFeatures { compose = true }
```

```kotlin
implementation(platform("androidx.compose:compose-bom:2026.06.01"))
implementation("androidx.compose.material3:material3")
implementation("androidx.activity:activity-compose:1.13.0")
implementation("androidx.lifecycle:lifecycle-runtime-compose:2.10.0")
implementation("androidx.navigation:navigation-compose:2.9.8")
implementation("androidx.paging:paging-compose:3.5.3")
debugImplementation("androidx.compose.ui:ui-test-manifest")
testImplementation(platform("androidx.compose:compose-bom:2026.06.01"))
testImplementation("androidx.compose.ui:ui-test-junit4")
testImplementation("androidx.navigation:navigation-testing:2.9.8")
testImplementation("org.robolectric:robolectric:4.17")
testImplementation("androidx.test.ext:junit:1.3.0")
androidTestImplementation(platform("androidx.compose:compose-bom:2026.06.01"))
androidTestImplementation("androidx.compose.ui:ui-test-junit4")
androidTestImplementation("androidx.compose.ui:ui-test-junit4-accessibility")
```

```properties
# app/src/test/resources/robolectric.properties
sdk=34
```

Robolectric 組都要連這個檔一起抄:`targetSdk = 36` 時 Robolectric 預設用 SDK 36 跑、要 JDK 21,JDK 17 上整個測試類別例外紅(見〈Android 實驗專案骨架〉)。

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T9
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertTextEquals
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.navigation.compose.ComposeNavigator
import androidx.navigation.testing.TestNavHostController
import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.compose.collectAsLazyPagingItems
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ScreensTest {
    @get:Rule
    val rule = createComposeRule()

    // STATE-12:訊息顯示完要回報已消費
    @Test
    fun message_consumed_after_shown() {
        val vm = MessageViewModel()
        rule.setContent { MessageScreen(vm) }
        rule.onNodeWithText("儲存").performClick()
        rule.mainClock.advanceTimeBy(10_000)   // 超過 Snackbar 短顯示的 4 秒
        rule.waitForIdle()
        assertNull(vm.userMessage.value, "訊息顯示後沒回報已消費")
    }

    // STATE-23:畫面狀態在存取還原後還在
    @Test
    fun filter_survives_state_restore() {
        val tester = StateRestorationTester(rule)
        // 存不進 Bundle 的值在 rememberSaveable 登記時就丟例外(組建當下),所以整段包起來
        val error = runCatching {
            tester.setContent { FilterPanel() }
            rule.onNodeWithText("套用").performClick()
            tester.emulateSavedInstanceStateRestore()
        }.exceptionOrNull()
        assertNull(error, "存狀態時丟例外")
        rule.onNodeWithText("關鍵字:kotlin").assertIsDisplayed()
    }

    // UI-36:snapshotFlow 要對每次改變發值
    @Test
    fun snapshot_flow_reports_every_tap() {
        val counter = TapCounter()
        val reported = mutableListOf<Int>()
        rule.setContent { TapReporter(counter) { reported += it } }
        rule.onNodeWithText("點我").performClick()
        rule.waitForIdle()
        rule.onNodeWithText("點我").performClick()
        rule.waitForIdle()
        assertEquals(listOf(0, 1, 2), reported, "snapshotFlow 發出的值")
    }

    // UI-52:資料還沒載入時項目也有高度,只組建畫面放得下的幾個
    @Test
    fun list_composes_only_visible_rows_before_load() {
        val composed = mutableSetOf<Int>()
        rule.setContent { PhotoList(ids = List(1_000) { it }, titles = emptyMap()) { composed += it } }
        rule.waitForIdle()
        assertTrue(composed.size < 50, "載入前就組建了 ${composed.size} 個項目")
    }

    // ARCH-2:從結果頁返回後停在原頁,不被推回
    @Test
    fun back_from_receipt_stays_on_checkout() {
        val vm = CheckoutViewModel()
        lateinit var nav: TestNavHostController
        rule.setContent {
            val context = LocalContext.current
            nav = remember { TestNavHostController(context).apply { navigatorProvider.addNavigator(ComposeNavigator()) } }
            CheckoutNav(nav, vm)
        }
        rule.onNodeWithText("付款").performClick()
        rule.waitForIdle()
        rule.runOnIdle { nav.popBackStack() }
        rule.waitForIdle()
        assertEquals("checkout", nav.currentDestination?.route, "返回後又被推回收據頁")
    }

    // ARCH-3:同一個按鈕在轉場完成前點兩次,只多一頁
    @Test
    fun double_click_opens_one_page() {
        lateinit var nav: TestNavHostController
        rule.setContent {
            val context = LocalContext.current
            nav = remember { TestNavHostController(context).apply { navigatorProvider.addNavigator(ComposeNavigator()) } }
            ListNav(nav)
        }
        rule.waitForIdle()
        rule.mainClock.autoAdvance = false
        val open = rule.onNodeWithText("開啟")
        open.performClick()
        open.performClick()
        rule.mainClock.advanceTimeBy(2_000)
        rule.waitForIdle()
        assertEquals("list", nav.previousBackStackEntry?.destination?.route, "連點後返回堆疊多了一頁")
    }

    // TEST-29(對照,型錄未接):關掉自動推進再推時鐘;Compose 1.11 實測讓時鐘自動推進也綠、沒卡住
    @Test
    fun syncing_banner_shown_with_frozen_clock() {
        rule.mainClock.autoAdvance = false
        rule.setContent { SyncingBanner() }
        rule.mainClock.advanceTimeBy(1_000)
        rule.onNodeWithText("同步中").assertIsDisplayed()
    }

    // TEST-32:合併語意樹裡的子節點,用未合併樹找
    @Test
    fun contact_phone_found_in_unmerged_tree() {
        rule.setContent { ContactRow("王小明", "0912-345-678") }
        rule.onNodeWithText("0912-345-678", useUnmergedTree = true).assertTextEquals("0912-345-678")
    }

    // DATA-63:還在載入時不顯示空畫面
    @Test
    fun loading_does_not_show_empty_view() {
        val flow = Pager(PagingConfig(pageSize = 20)) { NeverLoadingSource() }.flow
        rule.setContent { FeedList(flow.collectAsLazyPagingItems()) }
        rule.waitForIdle()
        assertEquals(0, rule.onAllNodesWithText("沒有資料").fetchSemanticsNodes().size, "載入中就顯示了空畫面")
    }

    // DATA-63 的另一半:真的沒資料時要顯示空畫面(只會「永遠不顯示」的寫法在這裡紅)
    @Test
    fun empty_result_shows_empty_view() {
        val flow = Pager(PagingConfig(pageSize = 20)) { EmptySource() }.flow
        rule.setContent { FeedList(flow.collectAsLazyPagingItems()) }
        rule.waitForIdle()
        assertEquals(1, rule.onAllNodesWithText("沒有資料").fetchSemanticsNodes().size, "沒資料時沒顯示空畫面")
    }
}
```

### 測試:無障礙

只在模擬器跑(`app/src/androidTest`)。檢查失敗丟 `AccessibilityViewCheckException`,`runCatching` 接住再斷言;斷言用 `org.junit.Assert`(儀器報告的收證看 JUnit 斷言框)。

`enableAccessibilityChecks()` 不帶參數時只對 ERROR 等級丟例外;文字對比不足被 ATF 報成 WARNING,預設照綠(白底 `#CCCCCC` 字、對比 1.61 也綠,實驗實測)。所以要自己傳 `AccessibilityValidator().setRunChecksFromRootView(true).setThrowExceptionFor(WARNING)`(`setRunChecksFromRootView(true)` 是不帶參數時的預設)。

```kotlin
// 起手:kotlin-idioms test-templates T9
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.junit4.accessibility.enableAccessibilityChecks
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.tryPerformAccessibilityChecks
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.google.android.apps.common.testing.accessibility.framework.AccessibilityCheckResult.AccessibilityCheckResultType
import com.google.android.apps.common.testing.accessibility.framework.integrations.espresso.AccessibilityValidator
import org.junit.Assert.assertNull
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class AccessibilityTest {
    @get:Rule
    val rule = createComposeRule()

    // 對比不足是 WARNING,預設只對 ERROR 丟例外
    private val validator = AccessibilityValidator()
        .setRunChecksFromRootView(true)
        .setThrowExceptionFor(AccessibilityCheckResultType.WARNING)

    // UI-106:可點的目標至少 48dp
    @Test
    fun favorite_toggle_touch_target() {
        rule.enableAccessibilityChecks(validator)
        rule.setContent { FavoriteToggle() }
        val error = runCatching { rule.onRoot().tryPerformAccessibilityChecks() }.exceptionOrNull()
        assertNull("觸控目標檢查不過:$error", error)
    }

    // UI-110:文字對比夠
    @Test
    fun caption_contrast() {
        rule.enableAccessibilityChecks(validator)
        rule.setContent { Caption("最後同步:剛剛") }
        val error = runCatching { rule.onRoot().tryPerformAccessibilityChecks() }.exceptionOrNull()
        assertNull("對比檢查不過:$error", error)
    }
}
```

### 壞測試:TEST-29 讓時鐘自動推進

```kotlin
// 對照:讓時鐘自動推進。原本預期無限動畫會讓測試卡住,Compose 1.11 在 Robolectric 與模擬器實測都綠、沒卡住,
// 抓不到差別(型錄 TEST-29 因此未接);這裡只留著示範,照抄用〈測試〉不推進的寫法
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class SyncingBannerAutoClockTest {
    @get:Rule
    val rule = createComposeRule()

    @Test
    fun syncing_banner_shown_auto_clock() {
        rule.setContent { SyncingBanner() }
        rule.onNodeWithText("同步中").assertIsDisplayed()
    }
}
```

### 壞測試:TEST-32 在合併樹找子節點

```kotlin
// 錯的寫法:不加 useUnmergedTree,找到的是合併後的父節點,文字是兩段
import androidx.compose.ui.test.assertTextEquals
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ContactRowMergedTest {
    @get:Rule
    val rule = createComposeRule()

    @Test
    fun contact_phone_in_merged_tree() {
        rule.setContent { ContactRow("王小明", "0912-345-678") }
        rule.onNodeWithText("0912-345-678").assertTextEquals("0912-345-678")
    }
}
```

### 好寫法

```kotlin
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class MessageViewModel {
    private val _userMessage = MutableStateFlow<String?>(null)
    val userMessage: StateFlow<String?> = _userMessage
    fun save() { _userMessage.value = "已儲存" }
    fun userMessageShown() { _userMessage.value = null }
}

// STATE-12:顯示完回報已消費
@Composable
fun MessageScreen(vm: MessageViewModel) {
    val snackbar = remember { SnackbarHostState() }
    val message by vm.userMessage.collectAsState()
    message?.let { m ->
        LaunchedEffect(m) {
            snackbar.showSnackbar(m)
            vm.userMessageShown()
        }
    }
    Scaffold(snackbarHost = { SnackbarHost(snackbar) }) { padding ->
        Button(onClick = vm::save, modifier = Modifier.padding(padding)) { Text("儲存") }
    }
}
```

```kotlin
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.listSaver
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue

data class Filter(val keyword: String, val onlyUnread: Boolean)

val FilterSaver = listSaver<Filter, Any>(
    save = { listOf(it.keyword, it.onlyUnread) },
    restore = { Filter(it[0] as String, it[1] as Boolean) },
)

// STATE-23:不能直接放進 Bundle 的型別給 Saver(或 @Parcelize)
@Composable
fun FilterPanel() {
    var filter by rememberSaveable(stateSaver = FilterSaver) { mutableStateOf(Filter("", false)) }
    Column {
        Text("關鍵字:${filter.keyword}")
        Button(onClick = { filter = filter.copy(keyword = "kotlin") }) { Text("套用") }
    }
}
```

```kotlin
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.setValue

// UI-36:snapshotFlow 讀的要是 State
class TapCounter {
    var taps by mutableIntStateOf(0)
}
```

```kotlin
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.snapshotFlow

@Composable
fun TapReporter(counter: TapCounter, onTaps: (Int) -> Unit) {
    LaunchedEffect(counter) { snapshotFlow { counter.taps }.collect { onTaps(it) } }
    Button(onClick = { counter.taps++ }) { Text("點我") }
}
```

```kotlin
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

// UI-52:項目在資料載入前就有固定高度
@Composable
fun PhotoList(ids: List<Int>, titles: Map<Int, String>, onCompose: (Int) -> Unit) {
    LazyColumn(Modifier.height(400.dp)) {
        items(ids) { id ->
            onCompose(id)
            PhotoRow(titles[id])
        }
    }
}

@Composable
fun PhotoRow(title: String?) {
    Box(Modifier.fillMaxWidth().height(72.dp)) { if (title != null) Text(title) }
}
```

```kotlin
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import kotlinx.coroutines.flow.MutableStateFlow

class CheckoutViewModel {
    val done = MutableStateFlow(false)
    fun pay() { done.value = true }
    fun onNavigated() { done.value = false }
}

@Composable
fun CheckoutNav(nav: NavHostController, vm: CheckoutViewModel) {
    NavHost(nav, startDestination = "checkout") {
        composable("checkout") { CheckoutScreen(vm) { nav.navigate("receipt") } }
        composable("receipt") { Text("收據") }
    }
}

// ARCH-2:導航後回報,狀態重設,返回時不會再觸發
@Composable
fun CheckoutScreen(vm: CheckoutViewModel, onDone: () -> Unit) {
    val done by vm.done.collectAsState()
    LaunchedEffect(done) {
        if (done) {
            onDone()
            vm.onNavigated()
        }
    }
    Button(onClick = vm::pay) { Text("付款") }
}
```

```kotlin
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.lifecycle.compose.dropUnlessResumed
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable

// ARCH-3:點擊只在 RESUMED 時生效,轉場中的第二次點擊被丟掉
@Composable
fun ListNav(nav: NavHostController) {
    NavHost(nav, startDestination = "list") {
        composable("list") { Button(onClick = dropUnlessResumed { nav.navigate("detail") }) { Text("開啟") } }
        composable("detail") { Text("詳細") }
    }
}
```

```kotlin
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha

// TEST-29:畫面有無限動畫
@Composable
fun SyncingBanner() {
    val transition = rememberInfiniteTransition(label = "sync")
    val a by transition.animateFloat(0.3f, 1f, infiniteRepeatable(tween(800)), label = "alpha")
    Text("同步中", Modifier.alpha(a))
}
```

```kotlin
import androidx.compose.foundation.layout.Row
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics

// TEST-32:整列合併成一個語意節點
@Composable
fun ContactRow(name: String, phone: String) {
    Row(Modifier.semantics(mergeDescendants = true) {}) {
        Text(name)
        Text(phone)
    }
}
```

```kotlin
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.paging.LoadState
import androidx.paging.PagingSource
import androidx.paging.PagingState
import androidx.paging.compose.LazyPagingItems
import kotlinx.coroutines.awaitCancellation

// DATA-63:refresh 不在載入中、而且沒有項目,才顯示空畫面
@Composable
fun FeedList(items: LazyPagingItems<String>) {
    if (items.loadState.refresh is LoadState.NotLoading && items.itemCount == 0) {
        Text("沒有資料")
    } else {
        LazyColumn { items(items.itemCount) { i -> Text(items[i] ?: "") } }
    }
}

class NeverLoadingSource : PagingSource<Int, String>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, String> = awaitCancellation()
    override fun getRefreshKey(state: PagingState<Int, String>): Int? = null
}

class EmptySource : PagingSource<Int, String>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, String> = LoadResult.Page(emptyList(), null, null)
    override fun getRefreshKey(state: PagingState<Int, String>): Int? = null
}
```

```kotlin
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.material3.minimumInteractiveComponentSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

// UI-106:圖示 24dp,可點範圍至少 48dp
@Composable
fun FavoriteToggle() {
    Box(Modifier.minimumInteractiveComponentSize().clickable { }.semantics { contentDescription = "收藏" }) {
        Box(Modifier.size(24.dp).background(Color.Red))
    }
}

// UI-110:文字用主題的前景色(這裡寫死成接近 onSurface 的深色)
@Composable
fun Caption(text: String) {
    Box(Modifier.background(Color.White)) { Text(text, color = Color(0xFF1C1B1F)) }
}
```

### 壞寫法:STATE-12 顯示完沒回報

```kotlin
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class MessageViewModel {
    private val _userMessage = MutableStateFlow<String?>(null)
    val userMessage: StateFlow<String?> = _userMessage
    fun save() { _userMessage.value = "已儲存" }
    fun userMessageShown() { _userMessage.value = null }
}

@Composable
fun MessageScreen(vm: MessageViewModel) {
    val snackbar = remember { SnackbarHostState() }
    val message by vm.userMessage.collectAsState()
    message?.let { m -> LaunchedEffect(m) { snackbar.showSnackbar(m) } }   // 沒呼叫 userMessageShown()
    Scaffold(snackbarHost = { SnackbarHost(snackbar) }) { padding ->
        Button(onClick = vm::save, modifier = Modifier.padding(padding)) { Text("儲存") }
    }
}
```

### 壞寫法:STATE-23 存不進 Bundle 的型別

```kotlin
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.listSaver
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue

data class Filter(val keyword: String, val onlyUnread: Boolean)

val FilterSaver = listSaver<Filter, Any>(
    save = { listOf(it.keyword, it.onlyUnread) },
    restore = { Filter(it[0] as String, it[1] as Boolean) },
)

@Composable
fun FilterPanel() {
    var filter by rememberSaveable { mutableStateOf(Filter("", false)) }   // 沒給 Saver,Filter 也不是 Parcelable
    Column {
        Text("關鍵字:${filter.keyword}")
        Button(onClick = { filter = filter.copy(keyword = "kotlin") }) { Text("套用") }
    }
}
```

### 壞寫法:UI-36 snapshotFlow 讀一般欄位

```kotlin
// 一般 var,不是 State:snapshotFlow 只會發第一個值
class TapCounter {
    var taps = 0
}
```

### 壞寫法:UI-52 項目載入前高度 0

```kotlin
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun PhotoList(ids: List<Int>, titles: Map<Int, String>, onCompose: (Int) -> Unit) {
    LazyColumn(Modifier.height(400.dp)) {
        items(ids) { id ->
            onCompose(id)
            PhotoRow(titles[id])
        }
    }
}

@Composable
fun PhotoRow(title: String?) {
    Box(Modifier.fillMaxWidth()) { if (title != null) Text(title) }   // 沒資料時高度 0
}
```

### 壞寫法:ARCH-2 狀態觸發導航沒重設

```kotlin
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import kotlinx.coroutines.flow.MutableStateFlow

class CheckoutViewModel {
    val done = MutableStateFlow(false)
    fun pay() { done.value = true }
    fun onNavigated() { done.value = false }
}

@Composable
fun CheckoutNav(nav: NavHostController, vm: CheckoutViewModel) {
    NavHost(nav, startDestination = "checkout") {
        composable("checkout") { CheckoutScreen(vm) { nav.navigate("receipt") } }
        composable("receipt") { Text("收據") }
    }
}

@Composable
fun CheckoutScreen(vm: CheckoutViewModel, onDone: () -> Unit) {
    val done by vm.done.collectAsState()
    LaunchedEffect(done) { if (done) onDone() }   // 返回時 done 還是 true,又導航一次
    Button(onClick = vm::pay) { Text("付款") }
}
```

### 壞寫法:ARCH-3 點擊沒擋生命週期

```kotlin
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable

@Composable
fun ListNav(nav: NavHostController) {
    NavHost(nav, startDestination = "list") {
        composable("list") { Button(onClick = { nav.navigate("detail") }) { Text("開啟") } }
        composable("detail") { Text("詳細") }
    }
}
```

### 壞寫法:DATA-63 只看 itemCount

```kotlin
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.paging.PagingSource
import androidx.paging.PagingState
import androidx.paging.compose.LazyPagingItems
import kotlinx.coroutines.awaitCancellation

@Composable
fun FeedList(items: LazyPagingItems<String>) {
    if (items.itemCount == 0) {   // 載入中也是 0
        Text("沒有資料")
    } else {
        LazyColumn { items(items.itemCount) { i -> Text(items[i] ?: "") } }
    }
}

class NeverLoadingSource : PagingSource<Int, String>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, String> = awaitCancellation()
    override fun getRefreshKey(state: PagingState<Int, String>): Int? = null
}

class EmptySource : PagingSource<Int, String>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, String> = LoadResult.Page(emptyList(), null, null)
    override fun getRefreshKey(state: PagingState<Int, String>): Int? = null
}
```

### 壞寫法:UI-106 可點範圍 24dp

```kotlin
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

@Composable
fun FavoriteToggle() {
    Box(Modifier.size(24.dp).background(Color.Red).clickable { }.semantics { contentDescription = "收藏" })
}

@Composable
fun Caption(text: String) {
    Box(Modifier.background(Color.White)) { Text(text, color = Color(0xFF1C1B1F)) }
}
```

### 壞寫法:UI-110 淺灰字

```kotlin
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.material3.minimumInteractiveComponentSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

@Composable
fun FavoriteToggle() {
    Box(Modifier.minimumInteractiveComponentSize().clickable { }.semantics { contentDescription = "收藏" }) {
        Box(Modifier.size(24.dp).background(Color.Red))
    }
}

@Composable
fun Caption(text: String) {
    Box(Modifier.background(Color.White)) { Text(text, color = Color(0xFFCCCCCC)) }   // 白底淺灰字
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:message_consumed_after_shown、filter_survives_state_restore、snapshot_flow_reports_every_tap、list_composes_only_visible_rows_before_load、back_from_receipt_stays_on_checkout、double_click_opens_one_page、syncing_banner_shown_with_frozen_clock、contact_phone_found_in_unmerged_tree、loading_does_not_show_empty_view、empty_result_shows_empty_view |
| 測試 | 壞寫法:STATE-12 顯示完沒回報 | message_consumed_after_shown 斷言紅「訊息顯示後沒回報已消費」;其他綠 |
| 測試 | 壞寫法:STATE-23 存不進 Bundle 的型別 | filter_survives_state_restore 斷言紅「存狀態時丟例外」;其他綠 |
| 測試 | 壞寫法:UI-36 snapshotFlow 讀一般欄位 | snapshot_flow_reports_every_tap 斷言紅「snapshotFlow 發出的值」;其他綠 |
| 測試 | 壞寫法:UI-52 項目載入前高度 0 | list_composes_only_visible_rows_before_load 斷言紅「載入前就組建了」;其他綠 |
| 測試 | 壞寫法:ARCH-2 狀態觸發導航沒重設 | back_from_receipt_stays_on_checkout 斷言紅「返回後又被推回收據頁」;其他綠 |
| 測試 | 壞寫法:ARCH-3 點擊沒擋生命週期 | double_click_opens_one_page 斷言紅「連點後返回堆疊多了一頁」;其他綠 |
| 測試 | 壞寫法:DATA-63 只看 itemCount | loading_does_not_show_empty_view 斷言紅「載入中就顯示了空畫面」;其他綠 |
| 壞測試:TEST-29 讓時鐘自動推進 | 好寫法 | syncing_banner_shown_auto_clock 綠 |
| 壞測試:TEST-32 在合併樹找子節點 | 好寫法 | contact_phone_in_merged_tree 斷言紅「王小明」 |
| 測試:無障礙 | 好寫法 | 全綠:favorite_toggle_touch_target、caption_contrast |
| 測試:無障礙 | 壞寫法:UI-106 可點範圍 24dp | favorite_toggle_touch_target 斷言紅「觸控目標檢查不過」;其他綠 |
| 測試:無障礙 | 壞寫法:UI-110 淺灰字 | caption_contrast 斷言紅「對比檢查不過」;其他綠 |

## T10 LeakCanary

型錄列:TEST-35。跑在哪:模擬器(`app/src/androidTest`,debug 建置;LeakCanary 要能 dump 堆積,debug 建置是可除錯的)。走完一個畫面流程(開畫面、關掉)後呼叫 `LeakAssertions.assertNoLeaks()`。

- 不用 `DetectLeaksAfterTestSuccess` 規則:它在測試本體外丟 `NoLeakAssertionFailedError`,紅的是那個型別名,收證工具照型別名判、儀器報告只看第一行是不是 `java.lang.AssertionError`,不算斷言失敗。改在測試最後 `runCatching { LeakAssertions.assertNoLeaks() }` 再 `assertNull`。
- `debugImplementation` 的 `leakcanary-android` 一定要加,見〈依賴〉。
- 斷言訊息只帶例外型別與前幾行:洩漏路徑的文字很長,儀器報告的失敗文字截在 64KB,斷言框被截掉時收證判不到。

### 依據

- https://square.github.io/leakcanary/ui-tests/ `androidTestImplementation 'com.squareup.leakcanary:leakcanary-android-instrumentation:2.14'`;「If application leaks are found, LeakAssertions.assertNoLeaks() will throw a NoLeakAssertionFailedError」
- TEST-35:型錄標準寫法(儀器測試接 LeakCanary)

### 依賴

```kotlin
debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")   // 不能省:監看物件的那一半裝在 App 裡
androidTestImplementation("com.squareup.leakcanary:leakcanary-android-instrumentation:2.14")
androidTestImplementation("androidx.test:core-ktx:1.7.0")
```

只加 `androidTestImplementation` 那一行不夠:App 這邊沒裝 LeakCanary 時沒有東西在監看被關掉的 Activity,`assertNoLeaks()` 什麼都找不到,壞寫法照綠(實驗實測;官方頁「You still need to include the LeakCanary artifact in your app」)。

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T10
import androidx.lifecycle.Lifecycle
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.lab.ProfileActivity
import leakcanary.LeakAssertions
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ProfileLeakTest {
    // TEST-35:開過再關掉的畫面不該被留住
    @Test
    fun profile_screen_does_not_leak() {
        ActivityScenario.launch(ProfileActivity::class.java).use { it.moveToState(Lifecycle.State.DESTROYED) }
        val leak = runCatching { LeakAssertions.assertNoLeaks() }.exceptionOrNull()
        val kind = generateSequence(leak?.javaClass as Class<*>?) { it.superclass }.map { it.name }.toList()
        assertNull("有洩漏:$kind ${leak?.message?.lineSequence()?.take(3)?.joinToString(" / ")}", leak)
    }
}
```

### 好寫法

```kotlin
package com.example.lab

import android.app.Activity
import android.os.Bundle

object SessionTracker {
    val listeners = mutableListOf<Any>()
}

// TEST-35 的被測程式:登記到單例的監聽在 onDestroy 解除
class ProfileActivity : Activity() {
    private val listener = Any()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        SessionTracker.listeners += listener
    }

    override fun onDestroy() {
        SessionTracker.listeners -= listener
        super.onDestroy()
    }
}
```

```xml
<!-- src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application>
        <activity android:name="com.example.lab.ProfileActivity" android:exported="false" />
    </application>
</manifest>
```

### 壞寫法:TEST-35 單例留住 Activity

```kotlin
package com.example.lab

import android.app.Activity
import android.os.Bundle

object SessionTracker {
    val listeners = mutableListOf<Any>()
}

class ProfileActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        SessionTracker.listeners += this   // 單例留住 Activity,關掉後也回收不了
    }
}
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:profile_screen_does_not_leak |
| 測試 | 壞寫法:TEST-35 單例留住 Activity | profile_screen_does_not_leak 斷言紅「有洩漏」 |

## T11 生命週期與框架

型錄列:ARCH-31、ARCH-35、STATE-17、ARCH-56,另接 API-9 的 Fragment 那一半(T12 判不到)。跑在哪:Robolectric(`app/src/test`)。

- ARCH-31:`FragmentScenario` 移到 CREATED(狀態已存)後送非同步回呼,`runCatching` 接住「Can not perform this action after onSaveInstanceState」再斷言;回到 RESUMED 後斷言交易真的做了(只是丟掉回呼的寫法也會紅)。
- ARCH-35:`TestLifecycleOwner` 走到 DESTROYED,斷言假匯流排上的監聽數歸零。
- STATE-17:不用 `InstantTaskExecutorRule`(它讓 `postValue` 同步執行,壞寫法照綠);改用 Robolectric 暫停的主 Looper——背景執行緒連 `postValue` 兩次後 `shadowOf(getMainLooper()).idle()`,斷言觀察者最後看到的那份清單有兩則訊息——好寫法下兩次 `postValue` 在主執行緒處理前合併,觀察者只被通知一次、內容兩筆,所以斷言 `seen.lastOrNull()`,不是 `seen.size == 2`。這一支只在 Robolectric 有意義:模擬器的主執行緒沒暫停,兩次 `postValue` 之間主執行緒可能先處理掉第一筆,壞寫法會時綠時紅。
- API-9 的 Fragment 那一半(〈測試:API-9 Fragment 畫面銷毀後〉):Fragment 在 `onViewCreated` 收一個假的 `MutableSharedFlow`,每收到一筆就呼叫假畫面記錄器 `render()`;記錄器在 `onDestroyView` 被標成已銷毀,之後再被呼叫就把「銷毀後被呼叫次數」加一(不丟例外)。`moveToState(CREATED)` 讓 view 銷毀後再發一筆、推主 Looper,斷言次數是 0。不用 `runCatching`:例外丟在 `lifecycleScope.launch` 的協程裡,測試本體接不到(官方協程例外處理頁:launch 的例外交給 `CoroutineExceptionHandler`)。
- ARCH-56(〈依賴:Hilt〉〈測試:Hilt〉,只有用 Hilt 的專案照抄):把 Hilt Fragment 放進宿主 Activity,`runCatching` 接住宿主沒標 `@AndroidEntryPoint` 時的 `IllegalStateException` 再斷言。Robolectric 用 `@HiltAndroidTest` 加 `HiltTestApplication`。

### 依據

- FragmentScenario 在 Robolectric:https://robolectric.org/androidx_test/ 「FragmentScenario, which offers APIs to safely create your Fragment under test and drive it through valid transitions」;https://developer.android.com/guide/fragments/test
- ARCH-31:https://developer.android.com/reference/androidx/fragment/app/FragmentTransaction#commit() 「A transaction can only be committed with this method prior to its containing activity saving its state」
- ARCH-35:https://developer.android.com/topic/libraries/architecture/lifecycle 生命週期觀察者對稱登記與解除;`TestLifecycleOwner`:https://developer.android.com/reference/kotlin/androidx/lifecycle/testing/TestLifecycleOwner
- STATE-17:https://developer.android.com/reference/androidx/lifecycle/LiveData#postValue(T) 「If you called this method multiple times before a main thread executed a posted task, only the last value would be dispatched」;`InstantTaskExecutorRule`「executes each task synchronously」
- API-9 Fragment:https://developer.android.com/topic/libraries/architecture/coroutines 「viewLifecycleOwner.lifecycleScope」與 `repeatOnLifecycle`;https://kotlinlang.org/docs/exception-handling.html
- ARCH-56:https://dagger.dev/hilt/android-entry-point 「So before adding @AndroidEntryPoint to a fragment, the activity must be annotated as well.」;Robolectric 測試:https://dagger.dev/hilt/testing

### 依賴

```kotlin
implementation("androidx.fragment:fragment-ktx:1.9.1")
implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.10.0")
implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.10.0")
debugImplementation("androidx.fragment:fragment-testing-manifest:1.9.1")
testImplementation("androidx.fragment:fragment-testing:1.9.1")
testImplementation("androidx.lifecycle:lifecycle-runtime-testing:2.10.0")
testImplementation("org.robolectric:robolectric:4.17")
testImplementation("androidx.test:core-ktx:1.7.0")
testImplementation("androidx.test.ext:junit:1.3.0")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")
```

```properties
# app/src/test/resources/robolectric.properties
sdk=34
```

Robolectric 組都要連這個檔一起抄:`targetSdk = 36` 時 Robolectric 預設用 SDK 36 跑、要 JDK 21,JDK 17 上整個測試類別例外紅(見〈Android 實驗專案骨架〉)。

### 依賴:Hilt

在〈依賴〉之外再加(只有用 Hilt 的專案):

```kotlin
// build.gradle.kts 的 plugins { } 加
id("com.google.dagger.hilt.android") version "2.58" apply false
id("com.google.devtools.ksp") version "2.2.21-2.0.5" apply false
```

```kotlin
// app/build.gradle.kts 的 plugins { } 加
id("com.google.dagger.hilt.android")
id("com.google.devtools.ksp")
```

```kotlin
implementation("com.google.dagger:hilt-android:2.58")
ksp("com.google.dagger:hilt-compiler:2.58")
testImplementation("com.google.dagger:hilt-android-testing:2.58")
kspTest("com.google.dagger:hilt-compiler:2.58")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T11
import android.os.Looper
import androidx.fragment.app.testing.launchFragmentInContainer
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.testing.TestLifecycleOwner
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlin.concurrent.thread
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Shadows.shadowOf

@RunWith(AndroidJUnit4::class)
class LifecycleTest {
    // ARCH-31:狀態存過之後才到的回呼,不能直接 commit;回到前景後要真的顯示
    @Test
    fun result_after_state_saved_is_shown_on_return() {
        val scenario = launchFragmentInContainer { OrderFragment() }
        scenario.moveToState(Lifecycle.State.CREATED)
        var error: Throwable? = null
        scenario.onFragment { f -> error = runCatching { f.onPaymentResult("paid") }.exceptionOrNull() }
        scenario.moveToState(Lifecycle.State.RESUMED)
        assertNull(error, "狀態存過之後 commit 丟例外")
        scenario.onFragment { f -> assertNotNull(f.childFragmentManager.findFragmentByTag("receipt"), "回到前景後沒顯示結果") }
    }

    // ARCH-35:走到 DESTROYED 後監聽要全部解除
    @Test
    fun listeners_released_after_destroy() {
        val bus = FakeLocationBus()
        val owner = TestLifecycleOwner(Lifecycle.State.INITIALIZED)
        owner.lifecycle.addObserver(LocationTracker(bus))
        owner.currentState = Lifecycle.State.RESUMED
        owner.currentState = Lifecycle.State.DESTROYED
        assertEquals(0, bus.listenerCount, "DESTROYED 後還掛著監聽")
    }

    // STATE-17:主執行緒處理前連發兩筆;觀察者通知一次、內容兩筆都要在
    @Test
    fun two_quick_events_both_delivered() {
        val vm = MessagesViewModel()
        val seen = mutableListOf<List<String>>()
        vm.messages.observeForever { seen += it }
        thread { vm.onSyncFinished(listOf("已同步 3 筆", "有 1 筆衝突")) }.join()
        shadowOf(Looper.getMainLooper()).idle()
        assertEquals(listOf("已同步 3 筆", "有 1 筆衝突"), seen.lastOrNull(), "觀察者最後看到的訊息清單")
    }
}
```

### 測試:API-9 Fragment 畫面銷毀後

```kotlin
// 起手:kotlin-idioms test-templates T11
import android.os.Looper
import androidx.fragment.app.testing.launchFragmentInContainer
import androidx.lifecycle.Lifecycle
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlin.test.assertEquals
import kotlinx.coroutines.flow.MutableSharedFlow
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Shadows.shadowOf

@RunWith(AndroidJUnit4::class)
class FeedFragmentTest {
    // API-9:view 銷毀後不該再收資料去更新畫面
    @Test
    fun no_render_after_view_destroyed() {
        val updates = MutableSharedFlow<String>(extraBufferCapacity = 8)
        val renderer = FakeRenderer()
        val scenario = launchFragmentInContainer { FeedFragment(updates, renderer) }
        updates.tryEmit("第一筆")
        shadowOf(Looper.getMainLooper()).idle()
        scenario.moveToState(Lifecycle.State.CREATED)   // view 銷毀,Fragment 本身還在
        updates.tryEmit("第二筆")
        shadowOf(Looper.getMainLooper()).idle()
        assertEquals(listOf("第一筆"), renderer.rendered, "view 還在時要收到第一筆")
        assertEquals(0, renderer.callsAfterDestroy, "view 銷毀後還在更新畫面")
    }
}
```

### 測試:Hilt

```kotlin
// 起手:kotlin-idioms test-templates T11
// Hilt 測試類別要放在具名套件裡:產生的 HostActivityTest_GeneratedInjector 在預設套件時,
// Hilt 彙整出的元件(具名套件)引用不到它,編譯失敗「cannot find symbol」(實驗實測)
package com.example.lab

import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import kotlin.test.assertNull
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config

@HiltAndroidTest
@Config(application = HiltTestApplication::class)
@RunWith(AndroidJUnit4::class)
class HostActivityTest {
    @get:Rule
    val hilt = HiltAndroidRule(this)

    // ARCH-56:Hilt Fragment 放進宿主 Activity 不崩
    @Test
    fun hilt_fragment_attaches_to_host() {
        val error = runCatching {
            ActivityScenario.launch(HostActivity::class.java).use { scenario ->
                scenario.onActivity { activity ->
                    activity.supportFragmentManager.beginTransaction().add(android.R.id.content, ProfileFragment()).commitNow()
                }
            }
        }.exceptionOrNull()
        assertNull(error, "Hilt Fragment 放進宿主時崩潰")
    }
}
```

### 假依賴

```kotlin
class FakeLocationBus : LocationBus {
    private val listeners = mutableSetOf<(Double) -> Unit>()
    val listenerCount get() = listeners.size
    override fun register(listener: (Double) -> Unit) { listeners += listener }
    override fun unregister(listener: (Double) -> Unit) { listeners -= listener }
}
```

```kotlin
class FakeRenderer : Renderer {
    val rendered = mutableListOf<String>()
    var callsAfterDestroy = 0
    private var destroyed = false
    override fun render(item: String) {
        if (destroyed) callsAfterDestroy++ else rendered += item
    }
    override fun viewDestroyed() { destroyed = true }
}
```

### 好寫法

```kotlin
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment

class ReceiptFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())
}
```

```kotlin
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle

// ARCH-31:結果先記成狀態,STARTED 以上才做交易;回到前景時補做
class OrderFragment : Fragment() {
    private var pendingResult: String? = null

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())

    fun onPaymentResult(result: String) {
        pendingResult = result
        if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) showPending()
    }

    override fun onStart() {
        super.onStart()
        showPending()
    }

    private fun showPending() {
        if (pendingResult == null) return
        pendingResult = null
        childFragmentManager.beginTransaction().add(ReceiptFragment(), "receipt").commit()
    }
}
```

```kotlin
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner

interface LocationBus {
    fun register(listener: (Double) -> Unit)
    fun unregister(listener: (Double) -> Unit)
}

// ARCH-35:onStart 登記、onStop 對稱解除
class LocationTracker(private val bus: LocationBus) : DefaultLifecycleObserver {
    private val listener: (Double) -> Unit = { }
    override fun onStart(owner: LifecycleOwner) = bus.register(listener)
    override fun onStop(owner: LifecycleOwner) = bus.unregister(listener)
}
```

```kotlin
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

// STATE-17:要保留每一筆就放佇列狀態,每次 post 整份佇列
class MessagesViewModel : ViewModel() {
    private val queue = mutableListOf<String>()
    private val _messages = MutableLiveData<List<String>>()
    val messages: LiveData<List<String>> = _messages

    fun onSyncFinished(events: List<String>) {
        for (e in events) {
            synchronized(queue) {
                queue += e
                _messages.postValue(queue.toList())
            }
        }
    }
}
```

```kotlin
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch

interface Renderer {
    fun render(item: String)
    fun viewDestroyed()
}

// API-9:跟著 view 的生命週期收
class FeedFragment(private val updates: Flow<String>, private val renderer: Renderer) : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                updates.collect { renderer.render(it) }
            }
        }
    }

    override fun onDestroyView() {
        renderer.viewDestroyed()
        super.onDestroyView()
    }
}
```

### 好寫法:ARCH-56 宿主也標 @AndroidEntryPoint

```kotlin
package com.example.lab

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class HostActivity : FragmentActivity()

@AndroidEntryPoint
class ProfileFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())
}
```

```xml
<!-- src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application>
        <activity android:name="com.example.lab.HostActivity" android:exported="false" />
    </application>
</manifest>
```

### 壞寫法:ARCH-31 狀態存過後直接 commit

```kotlin
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment

class OrderFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())

    fun onPaymentResult(result: String) {
        childFragmentManager.beginTransaction().add(ReceiptFragment(), "receipt").commit()
    }
}
```

### 壞寫法:ARCH-31 狀態存過就丟掉結果

```kotlin
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle

class OrderFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())

    fun onPaymentResult(result: String) {
        if (!lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) return   // 不崩,但結果不見了
        childFragmentManager.beginTransaction().add(ReceiptFragment(), "receipt").commit()
    }
}
```

### 壞寫法:ARCH-35 登記了沒解除

```kotlin
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner

interface LocationBus {
    fun register(listener: (Double) -> Unit)
    fun unregister(listener: (Double) -> Unit)
}

class LocationTracker(private val bus: LocationBus) : DefaultLifecycleObserver {
    private val listener: (Double) -> Unit = { }
    override fun onStart(owner: LifecycleOwner) = bus.register(listener)
}
```

### 壞寫法:STATE-17 連發兩次 postValue

```kotlin
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class MessagesViewModel : ViewModel() {
    private val _messages = MutableLiveData<List<String>>()
    val messages: LiveData<List<String>> = _messages

    fun onSyncFinished(events: List<String>) {
        val shown = mutableListOf<String>()
        for (e in events) {
            shown += e
            _messages.postValue(listOf(e))   // 每筆當一個事件送,主執行緒處理前只剩最後一筆
        }
    }
}
```

### 壞寫法:API-9 Fragment 自己的 lifecycleScope

```kotlin
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch

interface Renderer {
    fun render(item: String)
    fun viewDestroyed()
}

class FeedFragment(private val updates: Flow<String>, private val renderer: Renderer) : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {   // 跟著 Fragment 而不是 view:view 沒了還在收
            updates.collect { renderer.render(it) }
        }
    }

    override fun onDestroyView() {
        renderer.viewDestroyed()
        super.onDestroyView()
    }
}
```

### 壞寫法:ARCH-56 宿主沒標

```kotlin
package com.example.lab

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import dagger.hilt.android.AndroidEntryPoint

class HostActivity : FragmentActivity()   // 少了 @AndroidEntryPoint

@AndroidEntryPoint
class ProfileFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View = FrameLayout(requireContext())
}
```

```xml
<!-- src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application>
        <activity android:name="com.example.lab.HostActivity" android:exported="false" />
    </application>
</manifest>
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:result_after_state_saved_is_shown_on_return、listeners_released_after_destroy、two_quick_events_both_delivered |
| 測試 | 壞寫法:ARCH-31 狀態存過後直接 commit | result_after_state_saved_is_shown_on_return 斷言紅「狀態存過之後 commit 丟例外」;其他綠 |
| 測試 | 壞寫法:ARCH-31 狀態存過就丟掉結果 | result_after_state_saved_is_shown_on_return 斷言紅「回到前景後沒顯示結果」;其他綠 |
| 測試 | 壞寫法:ARCH-35 登記了沒解除 | listeners_released_after_destroy 斷言紅「DESTROYED 後還掛著監聽」;其他綠 |
| 測試 | 壞寫法:STATE-17 連發兩次 postValue | two_quick_events_both_delivered 斷言紅「觀察者最後看到的訊息清單」;其他綠 |
| 測試:API-9 Fragment 畫面銷毀後 | 好寫法 | 全綠:no_render_after_view_destroyed |
| 測試:API-9 Fragment 畫面銷毀後 | 壞寫法:API-9 Fragment 自己的 lifecycleScope | no_render_after_view_destroyed 斷言紅「view 銷毀後還在更新畫面」 |
| 測試:Hilt | 好寫法:ARCH-56 宿主也標 @AndroidEntryPoint | 全綠:hilt_fragment_attaches_to_host |
| 測試:Hilt | 壞寫法:ARCH-56 宿主沒標 | hilt_fragment_attaches_to_host 斷言紅「Hilt Fragment 放進宿主時崩潰」 |

## T12 架構測試:協程歸屬

型錄列:API-9(K1),順帶驗 CO-1 的整個範圍版(K2;型錄 CO-1 列的值不改)。跑在哪:Android 模組的本機單元測試(`app/src/test`,不用 Robolectric)。用 ArchUnit 讀編譯後的 `.class`,看「呼叫了哪個類別的哪個方法、存取了哪個欄位」,不看原始碼字面:星號匯入、完整名稱都判得到,註解與字串裡的 `GlobalScope`、名字含 `CoroutineScope(` 的 `rememberCoroutineScope()` 都不會誤判。

- **K1 不准無主協程**:不准碰 `GlobalScope`;不准在允許的類別外呼叫 `CoroutineScope(…)`、`MainScope()`。允許的類別是 `Application` 子類別與標 `@Module` 的 DI 模組(常數 `SCOPE_OWNER_SUPERTYPES`、`DI_MODULE_ANNOTATIONS`,專案自己改);判允許與否看**最外層宣告類別**——Kotlin 會把程式編進別的類別:suspend lambda 編成 `App$onCreate$1`、companion 編成 `AppModule$Companion`,只看呼叫端類別會誤報。同一個方法裡也呼叫了 `goAsync()`(`BroadcastReceiver` 把工作帶出 `onReceive` 的官方做法)就豁免,跟規則包 `kt-unmanaged-scope-launch` 排除含 `goAsync()` 的函式同一件事。
- **K2 資料層不寫死 dispatcher**:資料層套件(常數 `DATA_LAYER`)不准呼叫 `Dispatchers.IO`、`Dispatchers.Default`;建構子預設值(編成帶 `DefaultConstructorMarker` 參數的合成建構子)、一般函式的預設參數(編成名字結尾 `$default` 的合成方法)、DI 模組豁免——這三種都還能從外面注入,跟型錄 CO-1 標準寫法同精神。
- **Fragment 用 `lifecycleScope`(API-9 的另一半)這裡判不到**:位元組碼看不出接收者是 Fragment 還是 `viewLifecycleOwner`,規則包也沒有規則判它。那一半照 T11〈測試:API-9 Fragment 畫面銷毀後〉的行為測試接。
- **inline 函式**:自己寫的 inline 函式裡建 scope,定義處與每個呼叫端各報一筆(位元組碼裡呼叫被展開進呼叫端);別的模組的 inline 函式展開進資料層也會被報,看到這種違規先查是不是 inline 展開。
- **不匯入測試類別**:`ClassFileImporter` 加自訂 `ImportOption`,排除 AGP 單元測試與儀器測試的編譯輸出(變體目錄 `…UnitTest`、`…AndroidTest`)與 Gradle 的 `test`;測試碼裡的 `CoroutineScope(UnconfinedTestDispatcher())` 不算違規。ArchUnit 內建的 `ImportOption.DoNotIncludeTests` 認不得 AGP 的路徑(實驗實測,見矩陣下方)。
- **多模組**:資料層在別的 library 模組時,這支測試放 app 模組,`importPackages` 照根套件匯入;library 的類別以 jar 在 app 的本機測試類別路徑上,照樣判得到(實驗實測)。資料層套件或根套件一個類別都沒匯入時 ArchUnit 會失敗(`failOnEmptyShould` 預設開),那是常數設錯的大聲失敗。

**舊違規凍結**:兩支 `@Test` 都用 `FreezingArchRule.freeze(…)` 包:第一次跑出的違規存成一份清單,之後只有清單外的新違規才紅。清單裡的違規只准變少;帶 `-ParchunitFreezeInit` 那次清單多出來的違規,要在代碼審說明理由(見下面第 2 步)——清單讓舊違規永遠綠,不代表那些寫法沒問題。設定照下面〈依賴〉:`app/src/test/resources/archunit.properties` 寫三行——`freeze.store.default.path=src/test/resources/archunit_store`(相對模組目錄;不寫的話清單落在模組根的 `archunit_store`)、`freeze.store.default.allowStoreCreation=false`(ArchUnit 手冊的預設就是 false,明寫是為了不讓人改成 true)、`freeze.store.default.allowStoreUpdate=false`(手冊預設 true;理由見下兩段)。第一次建清單,以及清單要變的時候(加了凍結規則、改了規則描述、修掉舊違規):

1. `./gradlew :app:testDebugUnitTest -ParchunitFreezeInit --tests '*CoroutineOwnershipTest'`(有這個 Gradle 屬性時,`build.gradle.kts` 才把 `archunit.freeze.store.default.allowStoreCreation=true` 與 `archunit.freeze.store.default.allowStoreUpdate=true` 傳給測試,兩個都要:只開建立的話,建清單時寫入違規那一步被擋,丟 `StoreUpdateFailedException`(實驗實測);ArchUnit 的設定可被 `archunit.` 開頭的系統屬性蓋過)。
2. 改了規則描述時,先清掉舊描述留下的條目:清單以描述當鍵,新描述另存一份,舊描述那一份不會自己消失(實驗實測)——把 `archunit_store/stored.rules` 裡舊描述那一行與它指的清單檔一起刪。然後把 `app/src/test/resources/archunit_store/` 整個目錄提交進版控;清單的改動跟程式一起過代碼審,**特別看清單裡新增的違規**:帶屬性那一跑會把當下所有違規照單全收,跟著加規則、改描述一起進來的新違規,只有代碼審看得到。
3. 之後一律不帶 `-ParchunitFreezeInit` 跑。

`allowStoreCreation=false` 只擋「清單索引檔 `archunit_store/stored.rules` 整份不見」:常駐 true 時清單被刪或漏提交,下一次跑會把當下全部違規(含剛加的新違規)重新凍結、測試綠,CI 乾淨 checkout 每次都綠(實驗實測);設 false 時索引不見就丟 `StoreInitializationFailedException`,測試紅。它不管「索引在、但這條規則不在索引裡」:清單以規則描述(`ArchCondition("…")` 的字串、`.as(…)` 的名字)當鍵,加第三支用 `FreezingArchRule` 包的 `@Test`、或改了既有規則的描述,ArchUnit 把那條當成新規則,把當下全部違規存成新的一份、測試綠——描述改名時連同時新加的違規一起被凍結(實驗實測,ArchUnit 1.5.1 `FreezingArchRule.evaluate` 對不在索引裡的規則直接存檔回成功)。

所以要再加 `allowStoreUpdate=false`:設了之後,新規則、改描述都紅 `StoreUpdateFailedException: Updating frozen violations is disabled`,要照上面三步帶 `-ParchunitFreezeInit` 建好、清單改動提交;代價是修掉舊違規時也紅同一個例外(清單要縮小也是一次寫入),同樣帶屬性跑一次、提交縮小後的清單——清單每次變動都在版控裡看得到。這兩種紅都是設定錯的大聲失敗,不是斷言紅,收證不算抓到錯。

改 API-9、CO-1 的標準寫法時,規則包(`kt-unmanaged-scope-launch`、`kt-compose-globalscope-in-composable`、`kt-hardcoded-dispatchers-io`)、detekt(`GlobalCoroutineUsage`、`InjectDispatcher`)與這一組三邊一起看。規則包與 detekt 管「這次寫的」,這一組管「整個專案現在有沒有」,而且跑在專案自己的單元測試裡,不靠 lumos 有沒有裝。

### 依據

- 位元組碼判法:https://www.archunit.org/userguide/html/000_Index.html「It does so by analyzing given Java bytecode, importing all classes into a Java code structure」
- 舊違規凍結:同上手冊〈Freezing Arch Rules〉8.6.2;`freeze.store.default.allowStoreCreation` 預設 false、`freeze.store.default.allowStoreUpdate`「can be set to false to forbid updates of the violations stored for frozen rules」(預設 true)、`freeze.store.default.path` 設清單位置;設定可用 `archunit.` 開頭的系統屬性蓋過(手冊〈Advanced Configuration〉);新規則與改描述會被靜默凍結、`allowStoreUpdate=false` 擋得住:實驗實測(驗證紀錄 E13)
- API-9:https://developer.android.com/kotlin/coroutines/coroutines-best-practices 「Avoid GlobalScope」「the data and business layer should … use an injected CoroutineScope」;`goAsync`:https://developer.android.com/develop/background-work/background-tasks/broadcasts
- K2(CO-1):https://developer.android.com/kotlin/coroutines/test 「Using dependency injection to provide dispatchers to your classes makes it easy to replace the real dispatchers in tests」
- Kotlin 合成類別與 `$default`:r1 可行性席實跑(`governance/review-reports/android儀器測試範本與架構測試/r1-可行性-sonnet.md` F5、F6)

### 依賴

```kotlin
testImplementation("com.tngtech.archunit:archunit:1.5.1")
// 下面幾行只有實驗的被測程式要(專案本來就有)
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")
implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.10.0")
implementation("androidx.fragment:fragment-ktx:1.9.1")
implementation("androidx.compose.runtime:runtime:1.11.4")
implementation("com.google.dagger:dagger:2.57.2")
```

```kotlin
// app/build.gradle.kts 的 plugins { } 加(只有實驗的被測程式有 @Composable 才要)
id("org.jetbrains.kotlin.plugin.compose")
```

```kotlin
// app/build.gradle.kts 的 android { } 加(同上)
buildFeatures { compose = true }
```

```kotlin
// app/build.gradle.kts 檔尾
// 只有帶 -ParchunitFreezeInit 時才准建或改凍結清單(建清單、加規則、改描述、修掉舊違規時用;
// 平常清單不見、新規則、改描述都紅)
tasks.withType<Test>().configureEach {
    if (project.hasProperty("archunitFreezeInit")) {
        systemProperty("archunit.freeze.store.default.allowStoreCreation", "true")
        systemProperty("archunit.freeze.store.default.allowStoreUpdate", "true")
    }
}
```

```properties
# app/src/test/resources/archunit.properties
freeze.store.default.path=src/test/resources/archunit_store
freeze.store.default.allowStoreCreation=false
freeze.store.default.allowStoreUpdate=false
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T12
package com.example.lab.arch

import com.tngtech.archunit.core.domain.JavaAccess
import com.tngtech.archunit.core.domain.JavaClass
import com.tngtech.archunit.core.domain.JavaClasses
import com.tngtech.archunit.core.domain.JavaCodeUnit
import com.tngtech.archunit.core.domain.JavaConstructor
import com.tngtech.archunit.core.importer.ClassFileImporter
import com.tngtech.archunit.core.importer.ImportOption
import com.tngtech.archunit.lang.ArchCondition
import com.tngtech.archunit.lang.ArchRule
import com.tngtech.archunit.lang.ConditionEvents
import com.tngtech.archunit.lang.SimpleConditionEvent
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes
import com.tngtech.archunit.library.freeze.FreezingArchRule
import java.util.regex.Pattern
import org.junit.Test

class CoroutineOwnershipTest {
    companion object {
        const val APP_PACKAGE = "com.example.lab"            // 專案根套件
        const val DATA_LAYER = "com.example.lab.data.."      // 資料層(含子套件)
        val SCOPE_OWNER_SUPERTYPES = setOf("android.app.Application")
        val DI_MODULE_ANNOTATIONS = setOf("dagger.Module")

        // AGP:build/tmp/kotlin-classes/debugUnitTest、build/intermediates/javac/debugUnitTest/…;
        // Gradle:build/classes/kotlin/test。只比 build/ 底下第一層變體目錄,不比套件名
        private val TEST_OUTPUT = Pattern.compile(
            ".*/build/(?:tmp/kotlin-classes|intermediates/[^/]+|classes/(?:kotlin|java))/" +
                "(?:[^/]*UnitTest|[^/]*AndroidTest|test)/.*",
        )
        private val excludeTests = ImportOption { location -> !location.matches(TEST_OUTPUT) }

        val imported: JavaClasses by lazy {
            ClassFileImporter().withImportOption(excludeTests).importPackages(APP_PACKAGE)
        }
    }

    private fun JavaClass.outermost(): JavaClass {
        var c = this
        while (c.enclosingClass.isPresent) c = c.enclosingClass.get()
        return c
    }

    private fun JavaClass.isScopeOwner(): Boolean {
        val top = outermost()
        return SCOPE_OWNER_SUPERTYPES.any { top.isAssignableTo(it) } ||
            DI_MODULE_ANNOTATIONS.any { top.isAnnotatedWith(it) }
    }

    private fun JavaCodeUnit.callsGoAsync() = methodCallsFromSelf.any { it.name == "goAsync" && it.target.rawParameterTypes.isEmpty() }

    private fun JavaCodeUnit.isDefaultValueSynthetic() =
        (this is JavaConstructor && rawParameterTypes.any { it.name == "kotlin.jvm.internal.DefaultConstructorMarker" }) ||
            name.endsWith("\$default")

    private fun violation(events: ConditionEvents, access: JavaAccess<*>, why: String) =
        events.add(SimpleConditionEvent.violated(access, "$why: ${access.description}"))

    // K1(API-9)
    private val noUnownedScope: ArchRule = classes().should(
        object : ArchCondition<JavaClass>("not use GlobalScope nor create a CoroutineScope outside scope owners") {
            override fun check(item: JavaClass, events: ConditionEvents) {
                for (access in item.accessesFromSelf) {
                    val owner = access.targetOwner.name
                    if (owner == "kotlinx.coroutines.GlobalScope") {
                        violation(events, access, "GlobalScope")
                    } else if (owner == "kotlinx.coroutines.CoroutineScopeKt" && access.name in setOf("CoroutineScope", "MainScope") &&
                        !item.isScopeOwner() && !access.origin.callsGoAsync()
                    ) {
                        violation(events, access, "unowned scope")
                    }
                }
            }
        },
    )

    // K2(CO-1 的整個範圍版)
    private val dataLayerInjectsDispatchers: ArchRule = classes().that().resideInAPackage(DATA_LAYER).should(
        object : ArchCondition<JavaClass>("not hardcode Dispatchers.IO or Dispatchers.Default") {
            override fun check(item: JavaClass, events: ConditionEvents) {
                if (DI_MODULE_ANNOTATIONS.any { item.outermost().isAnnotatedWith(it) }) return
                for (call in item.methodCallsFromSelf) {
                    if (call.targetOwner.name == "kotlinx.coroutines.Dispatchers" && call.name in setOf("getIO", "getDefault") &&
                        !call.origin.isDefaultValueSynthetic()
                    ) {
                        violation(events, call, "hardcoded dispatcher")
                    }
                }
            }
        },
    )

    @Test
    fun no_unowned_coroutine_scope() {
        FreezingArchRule.freeze(noUnownedScope).check(imported)
    }

    @Test
    fun data_layer_does_not_hardcode_dispatchers() {
        FreezingArchRule.freeze(dataLayerInjectsDispatchers).check(imported)
    }
}
```

### 好寫法

```kotlin
package com.example.lab

import android.app.Application
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

// 允許:Application 子類別建 appScope;suspend lambda 編成 App$onCreate$1,往外找到 App
class App : Application() {
    val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onCreate() {
        super.onCreate()
        appScope.launch {
            val child = CoroutineScope(SupervisorJob())
            child.launch { }
        }
    }
}
```

```kotlin
package com.example.lab.di

import dagger.Binds
import dagger.Module
import dagger.Provides
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob

interface Clock { fun now(): Long }
class SystemClock : Clock { override fun now() = 0L }

// 允許:標 @Module 的 DI 模組;companion 編成 AppModule$Companion,往外找到 AppModule
@Module
abstract class AppModule {
    @Binds abstract fun clock(impl: SystemClock): Clock

    companion object {
        @Provides fun appScope(): CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    }
}
```

```kotlin
package com.example.lab.data.di

import dagger.Module
import dagger.Provides
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers

// K2 豁免:資料層裡的 DI 模組提供 dispatcher
@Module
object DispatchersModule {
    @Provides fun io(): CoroutineDispatcher = Dispatchers.IO
}
```

```kotlin
package com.example.lab.data

import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

// K2 豁免:建構子預設值(合成建構子)與函式預設參數(load$default),都還能從外面注入
class NoteRepository(private val io: CoroutineDispatcher = Dispatchers.IO) {
    suspend fun count(): Int = withContext(io) { 3 }

    suspend fun load(dispatcher: CoroutineDispatcher = Dispatchers.IO): String = withContext(dispatcher) { "x" }
}
```

```kotlin
package com.example.lab.ui

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModel
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

// 註解與字串裡的 GlobalScope 不算:"GlobalScope.launch"
class Screens {
    val hint = "do not use GlobalScope.launch"
}

class ProfileViewModel : ViewModel() {
    fun refresh() {
        viewModelScope.launch { }
    }
}

// 建構子注入的 scope
class Syncer(private val scope: CoroutineScope) {
    fun start() {
        scope.launch { }
    }
}

@Composable
fun Banner() {
    val scope = rememberCoroutineScope()   // 名字含 CoroutineScope( 的子字串,位元組碼呼叫的是 rememberCoroutineScope
    scope.hashCode()
}

// T12 判不到 Fragment 的 lifecycleScope(那半由 T11 接),這裡綠
class ListFragment : Fragment() {
    fun load() {
        lifecycleScope.launch { }
    }
}

// goAsync 後把工作帶出 onReceive:同一個方法裡呼叫了 goAsync,豁免
class SyncReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pending = goAsync()
        CoroutineScope(SupervisorJob() + Dispatchers.IO).launch {
            try { } finally { pending.finish() }
        }
    }
}
```

### 壞寫法:API-9 函式本體建 scope

```kotlin
package com.example.lab.ui

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class CartPresenter {
    fun refresh() {
        CoroutineScope(Dispatchers.IO).launch { }
    }
}
```

### 壞寫法:API-9 GlobalScope 星號匯入

```kotlin
package com.example.lab.ui

import kotlinx.coroutines.*

class Uploader {
    @OptIn(DelicateCoroutinesApi::class)
    fun upload() {
        GlobalScope.launch { }
    }
}
```

### 壞寫法:API-9 GlobalScope 完整名稱

```kotlin
package com.example.lab.ui

import kotlinx.coroutines.DelicateCoroutinesApi
import kotlinx.coroutines.launch

class Tracker {
    @OptIn(DelicateCoroutinesApi::class)
    fun track() {
        kotlinx.coroutines.GlobalScope.launch { }
    }
}
```

### 壞寫法:API-9 Receiver 沒有 goAsync

```kotlin
package com.example.lab.ui

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        CoroutineScope(Dispatchers.IO).launch { }
    }
}
```

### 壞寫法:CO-1 資料層寫死 withContext

```kotlin
package com.example.lab.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class TagRepository {
    suspend fun tags(): List<String> = withContext(Dispatchers.IO) { emptyList() }
}
```

### 壞寫法:CO-1 屬性 limitedParallelism

```kotlin
package com.example.lab.data

import kotlinx.coroutines.Dispatchers

class ImageCache {
    private val io = Dispatchers.IO.limitedParallelism(4)
    fun dispatcherName() = io.toString()
}
```

### 紅綠矩陣

前七格先用〈好寫法〉帶 `-ParchunitFreezeInit` 建凍結清單(零違規),再換成那一格的被測程式、不帶屬性跑——這樣紅的是「清單外的新違規」。最後四格驗凍結設定本身,基準不同:清單用〈好寫法〉加〈壞寫法:CO-1 資料層寫死 withContext〉(`TagRepository`,當一筆舊違規)帶屬性建(清單一筆違規,跟驗證紀錄 E13 同一個基準),再照那一格改一處、不帶屬性跑。測試小節寫「測試+…」的是〈測試〉照那樣改;被測程式小節用「+」連的是那幾個小節一起放;寫「修掉舊違規」的是被測程式拿掉 `TagRepository`,〈測試〉不動。

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:no_unowned_coroutine_scope、data_layer_does_not_hardcode_dispatchers |
| 測試 | 壞寫法:API-9 函式本體建 scope | no_unowned_coroutine_scope 斷言紅「CartPresenter.refresh」;其他綠 |
| 測試 | 壞寫法:API-9 GlobalScope 星號匯入 | no_unowned_coroutine_scope 斷言紅「Uploader.upload」;其他綠 |
| 測試 | 壞寫法:API-9 GlobalScope 完整名稱 | no_unowned_coroutine_scope 斷言紅「Tracker.track」;其他綠 |
| 測試 | 壞寫法:API-9 Receiver 沒有 goAsync | no_unowned_coroutine_scope 斷言紅「BootReceiver.onReceive」;其他綠 |
| 測試 | 壞寫法:CO-1 資料層寫死 withContext | data_layer_does_not_hardcode_dispatchers 斷言紅「TagRepository.tags」;其他綠 |
| 測試 | 壞寫法:CO-1 屬性 limitedParallelism | data_layer_does_not_hardcode_dispatchers 斷言紅「ImageCache.<init>」;其他綠 |
| 測試+多一支用 `FreezingArchRule` 包的 `@Test`(新描述) | 好寫法+壞寫法:CO-1 資料層寫死 withContext | 新那支紅 `StoreUpdateFailedException`(不是靜默凍結成綠);其他綠。沒設 `allowStoreUpdate=false` 時全綠、清單多一份新規則的檔 |
| 測試+改 `dataLayerInjectsDispatchers` 的 `ArchCondition` 描述 | 好寫法+壞寫法:CO-1 資料層寫死 withContext+壞寫法:CO-1 屬性 limitedParallelism | data_layer_does_not_hardcode_dispatchers 紅 `StoreUpdateFailedException`;其他綠。沒設 `allowStoreUpdate=false` 時全綠,新違規 `ImageCache` 跟舊違規一起被凍結 |
| 測試 | 好寫法(修掉舊違規:被測程式拿掉 `TagRepository`) | data_layer_does_not_hardcode_dispatchers 紅 `StoreUpdateFailedException`;帶 `-ParchunitFreezeInit` 再跑一次全綠、清單縮小一行 |
| 測試+刪掉 `archunit_store` 目錄 | 好寫法+壞寫法:CO-1 資料層寫死 withContext | 兩支都紅 `StoreInitializationFailedException`(不是全綠) |

## T13 架構測試:UiState 不可變

型錄列:UI-39(K3)。跑在哪:Android 模組的本機單元測試(`app/src/test`,不用 Robolectric)。用 Konsist 讀 Kotlin 原始碼的宣告(父型別、屬性是 `val` 還是 `var`、型別是不是可變型別),不看函式本體的文字。

- **判哪些類別**:名字結尾在後綴清單(常數 `STATE_SUFFIXES`,預設只有 `UiState`)裡的類別,或父型別(含間接)名字結尾同樣後綴的類別——`sealed interface HomeUiState { data class Success(…) : HomeUiState }` 的 `Success` 也判。專案的狀態類別叫 `State`、`UiModel` 時自己加後綴;命名慣例以外的狀態類別不判,型錄 UI-39 寫「範本 T13」不代表全部狀態類別都接上了。
- **判什麼**:類別自己的屬性(含主建構子的 `val`/`var` 參數與類別本體宣告的)不准 `var`、型別不准是 Kotlin 可變集合(`MutableList` 等,Konsist 的 `isMutableType`)或 `ArrayList`/`HashMap`/`HashSet` 這類可變實作(常數 `MUTABLE_IMPLS`)。標了 `@Immutable` 還是 `var` 照樣紅:標註只是對編譯器承諾,就地改照樣不更新畫面。
- **只掃正式程式**:範圍一律 `Konsist.scopeFromProduction()`;測試碼裡的 `FakeProfileUiState(var loading: Boolean)` 不判。用 `scopeFromProject()` 會連測試碼一起判(實驗實測)。`scopeFromProduction()` 掃的是整個 Gradle 專案所有模組的正式程式,不只這支測試所在的模組。
- **判不到的**:泛型參數裡的可變集合(`List<MutableList<String>>`,`isMutableType` 只看最外層,兩版都判不到);型別寫成型別別名(`typealias Items = MutableList<String>`)時 0.17.3 判不到、1.0.0-beta.1 判得到(2026-11-06 實跑);外部模組的類別(Konsist 只讀本專案原始碼)。
- **不判外部模組型別**:`java.time.Instant` 這類型別不判。Kotlin 2.0.20 起預設開強跳過,不穩定的參數用實例相等(`===`)比:值相同的新實例只會輕微多餘重組,不是錯;真正的錯是 `var` 或可變集合就地改,實例沒變、畫面被跳過。
- **舊違規**:Konsist 沒有凍結,單獨照抄時用逐檔常數清單 `LEGACY_FILES` 排除(只能縮小,新增一筆要在代碼審說明)。採用目標架構產生器(`lumos arch-template android`)的專案,把這支併進產生的測試檔,改用那支檔已從 `.lumos/arch-legacy.json` 讀好的 `legacyFiles`,不另留常數。三種舊違規容忍各管各的:產生器的 `.lumos/arch-legacy.json` 管目標架構分層與併進去的這支;這支單獨用時的常數只管這支;T12 的 ArchUnit 凍結清單只管 T12。
- **斷言**:收集違規再 `assertEquals(emptyList(), 違規)`;不用 Konsist 的 `assertTrue`/`assertFalse`——它們失敗丟 `KoAssertionFailedException`,收證照型別名判、不算斷言失敗。
- **版本**:只用 Konsist 0.17.3 與 1.0.0-beta.1 都有的 API(`scopeFromProduction()`、`classes(includeNested = true)`、`parents(indirectParents = true)`、`properties(includeNested = false)`、`isVar`、`type.isMutableType`、`type.name`),矩陣兩版實跑結果相同(型別別名那一點不同,見上)。Konsist 靠專案根目錄的 Gradle wrapper(`gradlew` 或 `gradle/wrapper/`)、Maven wrapper 或 `.git` 找專案根,三樣都沒有時測試類別初始化就丟 `KoInternalException: Project directory not found`(XML 上是 `ExceptionInInitializerError`,不是斷言紅)。

改 UI-39 的標準寫法時,連型錄 PERF-30 與規則包 `kt-uistate-mutable-field`(訊息以 `[PERF-30]` 開頭,掛在 PERF-30)一起看:規則訊息掛的是 PERF-30,不會因 UI-39 改了而被看到。

### 依據

- UI-39 與不判外部模組型別:https://developer.android.com/develop/ui/compose/performance/stability/strongskipping 「Strong Skipping is enabled by default in Kotlin 2.0.20」「Unstable parameters are compared using instance equality (===)」「Add @Stable or @Immutable when the compiler can't infer stability (such as classes from non-Compose modules) and new instances with identical values are frequently allocated」;「就地改→畫面被跳過」是從 `===` 推出的,頁面沒逐字寫
- 宣告判法與範圍:https://docs.konsist.lemonappdev.com/writing-tests/koscope(`scopeFromProduction`、`scopeFromProject`)
- Konsist 換版不在本組:決策見 [[Projects/Android儀器測試範本與架構測試_計劃]] d2

### 依賴

```kotlin
testImplementation("com.lemonappdev:konsist:0.17.3")   // 1.0.0-beta.1 同一份測試照跑
// 下面一行只有實驗的被測程式要(專案本來就有)
implementation("androidx.compose.runtime:runtime:1.11.4")
```

### 測試

```kotlin
// 起手:kotlin-idioms test-templates T13
package com.example.lab.arch

import com.lemonappdev.konsist.api.Konsist
import com.lemonappdev.konsist.api.declaration.KoClassDeclaration
import kotlin.test.assertEquals
import org.junit.Test

class UiStateImmutabilityTest {
    companion object {
        val STATE_SUFFIXES = listOf("UiState")   // 專案的狀態類別叫 State、UiModel 時加進來
        val MUTABLE_IMPLS = setOf("ArrayList", "HashMap", "HashSet", "LinkedHashMap", "LinkedHashSet")
        val LEGACY_FILES = setOf<String>()       // 舊違規逐檔排除(路徑結尾),只能縮小
    }

    private fun KoClassDeclaration.isUiState() =
        STATE_SUFFIXES.any { s -> name.endsWith(s) || parents(indirectParents = true).any { it.name.endsWith(s) } }

    @Test
    fun ui_state_classes_are_immutable() {
        val violations = Konsist.scopeFromProduction()
            .classes(includeNested = true)
            .filter { it.isUiState() && LEGACY_FILES.none { f -> it.path.endsWith(f) } }
            .flatMap { c ->
                c.properties(includeNested = false)
                    .filter { p ->
                        p.isVar || p.type?.isMutableType == true || p.type?.name?.substringBefore('<') in MUTABLE_IMPLS
                    }
                    .map { p -> "${c.name}.${p.name}" }
            }
        assertEquals(emptyList(), violations, "UiState 類別不准有 var 或可變集合")
    }
}
```

### 好寫法

```kotlin
package com.example.lab.ui

import java.time.Instant

// val 加唯讀集合,變更用 copy;外部模組型別 Instant 不判
data class ListUiState(
    val items: List<String> = emptyList(),
    val updatedAt: Instant? = null,
    val loading: Boolean = false,
)

sealed interface HomeUiState {
    data object Loading : HomeUiState
    data class Success(val items: List<String>) : HomeUiState
}

// 名字與父型別都不是 UiState 結尾:不判
class ClickCounter {
    var count = 0
}
```

### 壞寫法:UI-39 sealed 子類 var 可變集合

```kotlin
package com.example.lab.ui

sealed interface CartUiState {
    data class Success(var items: MutableList<String>) : CartUiState
}
```

### 壞寫法:UI-39 ArrayList 欄位

```kotlin
package com.example.lab.ui

data class SearchUiState(val results: ArrayList<String>)
```

### 壞寫法:UI-39 類別本體 var

```kotlin
package com.example.lab.ui

data class FormUiState(val name: String) {
    var dirty: Boolean = false
}
```

### 壞寫法:UI-39 標了 @Immutable 還是 var

```kotlin
package com.example.lab.ui

import androidx.compose.runtime.Immutable

@Immutable
data class BadgeUiState(var count: Int)
```

### 紅綠矩陣

| 測試小節 | 被測程式小節 | 結果 |
|---|---|---|
| 測試 | 好寫法 | 全綠:ui_state_classes_are_immutable |
| 測試 | 壞寫法:UI-39 sealed 子類 var 可變集合 | ui_state_classes_are_immutable 斷言紅「Success.items」 |
| 測試 | 壞寫法:UI-39 ArrayList 欄位 | ui_state_classes_are_immutable 斷言紅「SearchUiState.results」 |
| 測試 | 壞寫法:UI-39 類別本體 var | ui_state_classes_are_immutable 斷言紅「FormUiState.dirty」 |
| 測試 | 壞寫法:UI-39 標了 @Immutable 還是 var | ui_state_classes_are_immutable 斷言紅「BadgeUiState.count」 |
