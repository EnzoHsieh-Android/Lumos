---
type: project
status: todo
created: 2026-11-06
updated: 2026-11-06
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
lands_in:
  - Systems/kotlin規則包
  - Systems/test-quality-cli
related:
  - "[[Projects/Android行為測試範本與架構測試_計劃]]"
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Projects/Room資料庫測試守衛_計劃]]"
  - "[[Projects/Android端到端驗收_計劃]]"
  - "[[Projects/Android寫法語意情境表態與盲判_計劃]]"
  - "[[Systems/kotlin規則包]]"
  - "[[Systems/android-arch-template]]"
  - "[[Systems/room-guard]]"
pending_questions:
  - id: Q1
    text: K1、K2(API-9 不准無主協程、資料層不寫死 dispatcher)要不要用 ArchUnit 讀位元組碼做成範本 T12(消費專案多一個測試依賴)?建議:用;預實驗證過它把設計審打穿的寫法全判對,detekt 與規則包只看新增的行或要型別資訊;不用就 API-9 改不接、交給 detekt 加規則包
    class: 依賴
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d1"
  - id: Q2
    text: 產生器 lumos arch-template android 的 Konsist 要不要現在換 1.0.0-beta.1?建議:不換、等 1.0.0 正式版(REVISIT 2027-03-31);範本 T13 只用兩版共通的 API,不受影響;要換就另開 android-arch-template 的工作
    class: 依賴
    stage: 架構
    status: 已決
    decision: "#d2"
  - id: Q3
    text: K5(每個 Migration 要有測試)要不要做成架構測試?自答:不做,room-guard 已在推送前擋升級沒測試,DATA-19 的行為測試接範本 T6
    class: 範圍
    stage: 架構
    status: 自答
    source: Projects/Room資料庫測試守衛_計劃 條款 S6、S7
  - id: Q4
    text: API-30(Ktor 串流回應帶出 execute 區塊)要不要做?自答:做,併進範本 T4;前半移出的「依據不全」已被 Ktor API 頁原文補上,依賴只落在用 Ktor 的專案
    class: 範圍
    stage: 架構
    status: 自答
    source: https://api.ktor.io/ktor-client-core/io.ktor.client.statement/-http-statement/execute.html
decisions:
  - content: Q1:K1、K2 用 ArchUnit 讀位元組碼判協程歸屬與寫死 dispatcher,只加在消費專案的測試依賴
    id: d1
    context: 設計審打穿的寫法要不看字面的判法
    why_chosen: 編排者依使用者授權原話「我要睡了，你有裁量權、簽核權」代裁,使用者在場可改;實驗證過打穿寫法全判對,測試依賴不進正式包
    decided: 2026-11-06
    valid: true
  - content: Q2:產生器的 Konsist 先不換 1.0.0-beta.1,等正式版;T13 用兩版都有的寫法
    id: d2
    context: 1.0.0-beta.1 是 beta
    why_chosen: 編排者依使用者授權原話「我要睡了，你有裁量權、簽核權」代裁,使用者在場可改;不換不影響本批,REVISIT 2027-03-31 回頭看
    decided: 2026-11-06
    valid: true
---
# Android儀器測試範本與架構測試_計劃

> 白話:第五批前半([[Projects/Android行為測試範本與架構測試_計劃]])替型錄 32 列「長相看不出錯、要跑起來才知道」的寫法做了純 JVM 測試範本,另外 29 列移到後續:要模擬器或 Robolectric 的 25 列(儀器批)、前半打算做成架構測試 K1–K3 的三列(API-9、CO-5、UI-39)、一列 Ktor(API-30)。這份計劃把它們接完:儀器批照前半的格式加進同一份範本檔(T6–T11),每組附「好寫法綠、壞寫法紅」的對照、實作時真的在模擬器或 Robolectric 跑;架構測試改成不看字面的判法(K1、K2 讀編譯後的位元組碼,K3 讀 Kotlin 宣告),做成照抄範本 T12、T13——K2 的對象改成 CO-1(見〈用詞〉K 測試);Ktor 那列併進 T4。做不到的寫理由:CO-5(suspend 函式要 main-safe)本質是「有沒有真的阻塞」,架構測試驗不到,改歸代碼審或真機;K5(每個 Migration 要有測試)已由 room-guard 在推送前擋,不另做;Konsist 換版等 1.0.0 正式版(決策 d2)。

立案:使用者 2026-11-06 原話「遵照上面三個要點，完成這五個批次功能，目標是把Android靜態能先掃描的實務隱患都先處理過」,三要點「1.實作連續被打穿、或顯著無法收斂，就上網印證方向、業界實作找最佳解 2.所有機制都要實驗一遍，看看可行性、有沒有漏洞，修的流程遵照第一條 3.Android的規則也一樣，來源、依據，這可以在語意盲判的時候起到輔助判別的作用」,另一句「我們開發的過程中，所有機制的依據來源，最後也要補回plan，方便後續迭代」。輸入:前半計劃的〈不做〉、決策 d4 與設計審 r1 卷證(`governance/review-reports/android行為測試範本與架構測試/`,通才 F4–F6、可行性 F4–F6 共六條發現,打穿的是四種寫法:函式本體當場建 scope、`rememberCoroutineScope`、sealed UiState、DI 模組)、第五批調研稿(會談暫存區,要用的結論已搬進〈依據來源〉)、本計劃動筆時的本機預實驗(〈前提〉)。

PRIOR-ART: ①儀器測試全照官方測試頁的寫法:Room `MigrationTestHelper` 與記憶體資料庫、Paging `asSnapshot` 與 RemoteMediator 三情境、WorkManager `TestListenableWorkerBuilder`、Compose `createComposeRule`/`StateRestorationTester`/`mainClock.autoAdvance`/`useUnmergedTree`/`enableAccessibilityChecks`、LeakCanary `LeakAssertions.assertNoLeaks()`、`FragmentScenario` 與 `TestLifecycleOwner`;Robolectric 照官方 androidx_test 頁跑同一份 AndroidX Test API。②K1、K2 照 ArchUnit 的位元組碼匯入(`ClassFileImporter`)與舊違規凍結(`FreezingArchRule`,ArchUnit 官方給既有專案的做法);K3 照 Konsist starter snippets 的宣告層斷言;三條都不自寫解析器。③範本檔、紅綠矩陣、通電批次欄的值與 `check.py` 的 `template_problems` 全沿用前半,不新增格式、認領語法或自檢項。④紅要是斷言紅,照收證工具 `scripts/test_quality.py` 的 `assertion_failure`(儀器測試 XML 沒有型別,看第一行與 JUnit 斷言框)。裁定:全借用;新寫的只有範本內容、一節 Android 實驗專案骨架、型錄的值與幾支資料測試的期望。
RETIRE-IF: 2027-05-06 人裁時,在消費專案的 git 歷史裡數第一行留了 `// 起手:kotlin-idioms test-templates T6`~`T13` 的測試檔,全部專案加起來少於 5 支,就把 T6–T13 降成 kotlin-idioms 裡的一段官方頁連結清單,型錄那幾列改回「未接(儀器批)」 [retire:人裁] [until:2027-05-06]

## 用詞

- **前半**:[[Projects/Android行為測試範本與架構測試_計劃]],T0–T5 已上線;本計劃沿用它〈用詞〉裡的「型錄」「C 列」「範本組」「範本檔」「紅綠矩陣」「實驗專案」,不重定義;K 代號只有 K2 的對象改了(見下面 K 測試)。
- **第五批、前半、後半**:[[Projects/Android協程與API寫法機械檢查標準_計劃]] 把型錄的接電工作分成五批,第五批是 C 級列(「長相看不出錯、要跑起來才知道」)的行為測試與架構測試;第五批拆成兩份計劃,前半是下一條那份,後半是本計劃。**第五批調研稿**是 2026-11-06 為第五批寫的調研筆記,放在會談暫存區,本計劃要用的結論已搬進〈依據來源〉。
- **通電批次欄**:型錄每列的一欄,寫「這列的每種接電方式在哪一批、接到什麼」,格式見型錄〈輸入與口徑〉;本計劃只動其中「行為測試或正向約束=」那一段的值,值的寫法沿用前半(「範本 T<n>」「未接(…)」「不接(…)」)。
- **會談暫存區**:做實作的那個 Claude 會談自己的 scratchpad 目錄(`/private/tmp/claude-501/` 底下、每個會談不同),不進 repo,實驗做完由該會談刪掉;本計劃所有實驗專案與輸出都放這裡。
- **lab、lab 複本**:lab 是本機 Android 示範專案 macrobench-lab(`/Users/enzo/lumos-scratch/android-checks/scratchpad/lab`,根目錄有 gradlew);lab 複本是從它 `git clone` 到會談暫存區、再加測試依賴的那份,實驗只在複本上做。
- **r1 與 F 編號**:r1 指前半的設計審第一輪,卷證在 `governance/review-reports/android行為測試範本與架構測試/`;「通才 F4」是通才席報告裡編號 F4 的發現,其他席同理(可行性、依據、架構對齊)。
- **儀器測試**:跑在 Android 裝置或模擬器上的測試(`src/androidTest`,`./gradlew connected<變體>AndroidTest`)。
- **Robolectric**:在電腦 JVM 上模擬 Android 框架的函式庫,測試放 `src/test`、用 `@RunWith(AndroidJUnit4::class)`,跟儀器測試共用 AndroidX Test API。
- **Android 實驗專案**:實作者在會談暫存區照範本檔新節〈Android 實驗專案骨架〉組的 Android app 模組(不是前半那種純 JVM 專案);一格一份被測程式,儀器測試在模擬器跑、Robolectric 測試在 JVM 跑。
- **K 測試**:架構測試,判斷「整個程式有沒有某種寫法」,不跑被測程式。K1 不准無主協程(API-9)、K2 資料層不寫死 dispatcher(CO-1 的整個範圍版;**前半的 K2 掛在 CO-5,本計劃改掛 CO-1**,理由見決定 3,其餘代號意思沿用前半)、K3 UiState 不可變(UI-39)、K4 Hilt 宿主(ARCH-56)、K5 Migration 有測試(DATA-19)。
- **位元組碼判法**:讀編譯後的 `.class`(ArchUnit),看的是「呼叫了哪個類別的哪個方法、存取了哪個欄位」,不看原始碼字面;import 寫法、完整名稱、註解與字串都不影響。
- **宣告判法**:讀 Kotlin 原始碼的宣告(Konsist),看的是「這個類別的父型別、屬性是 val 還是 var、型別是不是可變型別」,不看函式本體的文字。
- **凍結**:ArchUnit `FreezingArchRule` 把第一次跑出的違規存成一份清單檔,之後只有清單外的新違規才紅;清單裡的修掉時清單自動縮小。

## 前提(2026-11-06 動筆時本機查到與預實驗)

- **裝置**:`adb devices` 有一台實機 `R52X305YY7W`(Samsung SM-X710,API 36,使用者的平板,實驗不用它);`emulator -list-avds` 有 `kds_bench`(system-images android-34 google_apis arm64-v8a,2G RAM),無視窗開機 30 秒內 `sys.boot_completed=1`。實驗一律用這台模擬器;本機 JDK 是 JBR 17.0.14,Gradle 8.13、AGP 8.13.2、Kotlin 2.2.21(macrobench-lab 示範專案的組合)。
- **示範專案**:`/Users/enzo/lumos-scratch/android-checks/scratchpad/lab` 有 gradlew,但工作目錄有別人沒提交的改動(`app/build.gradle.kts` 改過、多一個未追蹤目錄),**不碰它**;實驗一律 `git clone` 到會談暫存區再改。
- **預實驗 P1(無障礙檢查在哪跑得出來)**:在 lab 複本加一支測試,24dp 可點方塊 vs 48dp 方塊,`enableAccessibilityChecks()` 後 `tryPerformAccessibilityChecks()`。模擬器:24dp 那支丟 `AccessibilityViewCheckException`(「This item's size is 24dp x 24dp」),用 `runCatching` 接住後斷言紅,48dp 綠;**Robolectric 4.16:兩支都綠——無障礙檢查在 Robolectric 不報**。所以 T9 的無障礙兩列只能在模擬器跑。
- **預實驗 P2(Robolectric 與 JDK)**:Robolectric 4.16 對 compileSdk 36 的專案預設用 SDK 36,在 JDK 17 上整個類別例外紅「Android SDK 36 requires Java 21 (have Java 17)」;在 `src/test/resources/robolectric.properties` 寫 `sdk=34` 後正常。骨架要寫這一行。
- **預實驗 P3(K1–K3 不靠字面能不能判)**:純 JVM 專案放設計審打穿的寫法當樣本,ArchUnit 1.5.1 判 K1、K2,Konsist 判 K3,結果全照預期:
  - K1(位元組碼):紅 = 函式本體 `CoroutineScope(Dispatchers.IO).launch`、星號匯入的 `GlobalScope.launch`、完整名稱 `kotlinx.coroutines.GlobalScope.launch`;綠 = `rememberCoroutineScope()`(名字含 `CoroutineScope(` 子字串)、註解與字串裡的 `GlobalScope`、建構子注入的 scope、`Application` 子類別裡建 `appScope`。
  - K2(位元組碼):紅 = 方法裡 `withContext(Dispatchers.IO)`、屬性 `Dispatchers.IO.limitedParallelism(4)`;綠 = 建構子預設值 `io: CoroutineDispatcher = Dispatchers.IO`(呼叫落在帶 `DefaultConstructorMarker` 參數的合成建構子,豁免它)、標 `@Module` 的 DI 物件。`suspend fun load() { Thread.sleep(10) }` 綠——K2 驗不到 main-safe。
  - K3(宣告):紅 = `sealed interface HomeUiState { data class Success(var items: MutableList<String>) }` 的 `Success`、`data class CartUiState(val items: ArrayList<String>)`、類別本體 `var dirty`;綠 = `val` 加 `List` 加 `java.time.Instant`、sealed 子類全 `val`。同一份 K3 在 Konsist 0.17.3 與 1.0.0-beta.1 都編得過、結果相同。
  - 改壞對照:拿掉豁免,K1 多紅 `Application` 子類別,K2 多紅建構子預設值與 DI 模組;K3 只看名字結尾 `UiState` 時漏掉 `Success`(r1 打穿點重現)。ArchUnit 看 K3 只看得到 `var`(非 final 欄位)與 `ArrayList`,看不出 `MutableList` 與 `List` 的差別(位元組碼都是 `java.util.List`),所以 K3 不用它。
  - Konsist 1.0.0-beta.1 裡舊名 `resideInPackage` 編譯失敗「Unresolved reference」,新名 `residesInPackage` 可用(發行說明頁現版沒寫這個改名,以編譯為準)。
- 預實驗的程式與輸出在會談暫存區,收尾時刪;要留的結論都寫在這一節。

## 範圍

### 做(28 列)

| 組 | 型錄列 | 測法(一句) | 跑在哪 |
|---|---|---|---|
| T6 Room 與資料層 | DATA-17、DATA-19、DATA-21、DATA-65、DATA-69(5) | `MigrationTestHelper` 從最舊版逐版升、另一支 `addMigrations(*ALL_MIGRATIONS)` 開到最新;記憶體資料庫配會失敗的假 API 斷言本機資料還在、衝突照「後寫贏」;一次查 40000 個 id | 模擬器(官方不建議 Robolectric 跑 Room) |
| T7 Paging | DATA-58、DATA-60(2) | `asSnapshot` 對 ViewModel 的分頁流收兩次;RemoteMediator 三情境(有資料 false、空 true、例外 Error) | DATA-58 Robolectric;DATA-60 模擬器(要真 Room) |
| T8 WorkManager | DATA-38、DATA-39(2) | `TestListenableWorkerBuilder` 建 CoroutineWorker,取消後斷言迴圈停下、資源關掉;被測程式產的 `Data` 斷言小於上限 | Robolectric |
| T9 Compose UI | STATE-12、STATE-23、UI-36、UI-52、ARCH-2、ARCH-3、TEST-29、TEST-32、DATA-63;無障礙 UI-106、UI-110(11) | `createComposeRule` 掛畫面、假 ViewModel 推狀態;訊息顯示後已消費、`StateRestorationTester` 還原、`snapshotFlow` 有發、項目載入前有高度、返回不被推回、連點只多一頁、動畫關自動推進、子節點用未合併樹、載入中不顯示空畫面;無障礙用 `enableAccessibilityChecks()` | 九列 Robolectric(實驗 E4 在模擬器對一次);無障礙兩列只在模擬器(預實驗 P1) |
| T10 LeakCanary | TEST-35(1) | 走完一個畫面流程後 `LeakAssertions.assertNoLeaks()`,用 `runCatching` 接住再斷言 | 模擬器 |
| T11 生命週期與框架 | ARCH-31、ARCH-35、STATE-17、ARCH-56(4) | `FragmentScenario` 移到 CREATED 後送回呼斷言沒丟例外;`TestLifecycleOwner` 走到 DESTROYED 斷言監聽數歸零;LiveData 在暫停的主 Looper 上連發兩次斷言兩筆都收到;Hilt Fragment 放進宿主 Activity 斷言沒丟例外;另接 API-9 的 Fragment 那半(view 銷毀後不再收) | Robolectric(ARCH-56 要 Hilt 測試設定,實驗 E9 決定) |
| T12 架構測試:協程歸屬(ArchUnit) | API-9(1;K1),另含 K2(CO-1,型錄 CO-1 列不改值) | 位元組碼判:不准 `GlobalScope`、不准在允許類別外呼叫 `CoroutineScope()`/`MainScope()`;資料層不准呼叫 `Dispatchers.IO/Default`(建構子預設值與 DI 模組豁免);舊違規凍結 | 專案的本機單元測試(JVM) |
| T13 架構測試:UiState 不可變(Konsist) | UI-39(1;K3) | 宣告判:名字結尾 `UiState` 或父型別(含間接)結尾 `UiState` 的類別,屬性不准 `var`、型別不准是可變型別或 `ArrayList`/`HashMap`/`HashSet` | 專案的本機單元測試(JVM) |
| T4 補 Ktor | API-30(1) | 真的 Ktor client 打本機 MockWebServer,斷言在 `execute { }` 區塊裡讀完的 body 是完整的;壞寫法把 response 帶出區塊再讀 | 純 JVM(前半骨架) |

做法:

1. **範本檔 `skills/kotlin-idioms/test-templates.md` 加節**(不另開檔;節標題照前半 `## T<n> ` 規則,`check.py` 的 `template_problems` 原樣驗得到):
   - 新節〈Android 實驗專案骨架〉放在〈實驗專案骨架〉之後:`settings.gradle.kts`、根 `build.gradle.kts`、`app/build.gradle.kts` 全文(AGP 8.13.2、Kotlin 2.2.21 與 Compose 外掛、compileSdk 36、minSdk 24、`testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"`、`testOptions.unitTests.isIncludeAndroidResources = true`),`src/test/resources/robolectric.properties` 一行 `sdk=34` 與為什麼(預實驗 P2);儀器測試指令 `ANDROID_SERIAL=<模擬器> ./gradlew :app:connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=<類別>`、Robolectric 指令 `./gradlew :app:testDebugUnitTest --tests <類別>`;每組〈依賴〉標明是 `androidTestImplementation`、`testImplementation` 還是 `debugImplementation`。
   - 每組節裡的小節照前半(〈依據〉〈依賴〉〈測試〉〈假依賴〉〈好寫法〉〈壞寫法:變體〉〈紅綠矩陣〉);節開頭一句寫「跑在哪」。
   - 範本的程式要點(寫進範本、實驗驗過才算):
     - **T6**:`MigrationTestHelper(instrumentation, AppDb::class, driver = AndroidSQLiteDriver(), file = …)` 的建構子是 Room 2.7 起的形狀,〈依賴〉寫 Room 2.7 以上;DATA-17、DATA-19 一支逐版 `runMigrationsAndValidate`、一支 `addMigrations(*ALL_MIGRATIONS)` 開到最新(官方「include a test that covers all migrations」),壞寫法「少一個 Migration」丟 `IllegalStateException`、「SQL 寫錯」丟 `SQLiteException`,都 `runCatching` 後斷言;結構檔要進 `androidTest` 的 assets(`sourceSets["androidTest"].assets.srcDir("$projectDir/schemas")`,實驗驗);DATA-21 查 40000 個 id(SQLite 3.32.0 起參數上限 32766、之前 999,用 40000 讓新舊裝置都紅,壞寫法不分批、好寫法 `chunked(500)`;壞寫法丟 `SQLiteException`(too many SQL variables),測試先 `runCatching` 接住再斷言查到的筆數);DATA-69 假 API 丟 `IOException`,斷言刷新失敗後本機清單不變;DATA-65 照型錄標準寫法「後寫贏」:本機有較新未同步修改時,較舊的伺服器資料不得蓋掉,範本註解寫「衝突策略是業務決定,照情境表態換斷言」。
     - **T7**:DATA-58 對 `vm.items` 連呼兩次 `asSnapshot { }`,壞寫法(沒 `cachedIn` 再 `combine` 或兩處收)丟 `IllegalStateException`,`runCatching` 後斷言;DATA-60 照官方 RemoteMediator 頁的三情境,空回應斷言 `endOfPaginationReached == true`。
     - **T8**:DATA-38 只做 CoroutineWorker 版(型錄標準寫法說它由框架自動取消):在 `backgroundScope` 啟動 `worker.doWork()`、推進、取消,斷言迴圈次數不再增加且 `finally` 關了假資源;壞寫法 `catch (e: Exception)` 吞掉取消。一般 `Worker` 的 `isStopped` 從測試觸發不了(官方測試頁沒示範,`stop` 是框架內部方法),寫進天花板。DATA-39 斷言被測程式產的 `Data.toByteArray().size < Data.MAX_DATA_BYTES`。
     - **T9**:STATE-12 `waitUntil` 等 `userMessage == null` 改成推時鐘後直接斷言(`waitUntil` 逾時丟的是 `ComposeTimeoutException`,不是斷言紅);STATE-23 `StateRestorationTester.emulateSavedInstanceStateRestore()` 後斷言畫面狀態還在,存不進 Bundle 的型別丟例外用 `runCatching`;TEST-29 `mainClock.autoAdvance = false` 加 `advanceTimeBy`;TEST-32 `useUnmergedTree = true`;ARCH-3 同一個節點 `performClick()` 兩次後斷言返回堆疊只多一頁;ARCH-2 用 `TestNavHostController`(Navigation 測試套件,實驗查版本)導航到 B、`popBackStack()` 後斷言目前目的地是 A;無障礙兩列(〈測試:無障礙〉小節,節開頭寫「只在模擬器」)照預實驗 P1 的寫法。
     - **T10**:不用 `DetectLeaksAfterTestSuccess` 規則(它在測試本體外丟 `NoLeakAssertionFailedError`,收證不算斷言),改在測試最後 `runCatching { LeakAssertions.assertNoLeaks() }` 再 `assertNull`。
     - **T11**:STATE-17 不用 `InstantTaskExecutorRule`(它讓 `postValue` 同步執行,壞寫法照綠),改 Robolectric 暫停的主 Looper:背景執行緒連 `postValue` 兩次後 `shadowOf(getMainLooper()).idle()`,斷言觀察者收到兩筆;ARCH-31 `scenario.moveToState(CREATED)` 後送回呼,`runCatching` 接住「Can not perform this action after onSaveInstanceState」再斷言;ARCH-35 用 `TestLifecycleOwner`;ARCH-56 見 E9;**API-9 的 Fragment 那半**另一個小節〈測試:API-9 Fragment 畫面銷毀後〉:Fragment 在 `onViewCreated` 收一個假的 `MutableSharedFlow` 並更新 view,`scenario.moveToState(CREATED)` 讓 view 銷毀後再發一筆,斷言沒有丟例外、也沒有更新已銷毀的 view;壞寫法用 Fragment 自己的 `lifecycleScope`(view 沒了還在收,碰 binding 丟例外,`runCatching` 接住後斷言),好寫法用 `viewLifecycleOwner.lifecycleScope` 加 `repeatOnLifecycle`(型錄 API-9 標準寫法)。型錄 API-9 的值仍寫「範本 T12」(一列只寫一個組),T12 節開頭指到這個小節。
     - **T12**:兩支 `@Test`,各用 `FreezingArchRule.freeze(...)` 包;允許建 scope 的類別是「`Application` 子類別或標 `@Module` 的類別」,範本留一個常數讓專案改;Fragment 用 `lifecycleScope` 那一半位元組碼判不到(看不出接收者是 Fragment 還是 `viewLifecycleOwner`),規則包也沒有規則判它(只有 STATE-5、PERF-4、ARCH-50 三條碰 `lifecycleScope`,都不是這件事),所以本計劃改用 T11 的行為測試接(見 T11 的 API-9 小節),T12 節開頭指過去。另一個允許:呼叫了 `BroadcastReceiver.goAsync()` 的方法裡建 scope 豁免(規則包 `kt-unmanaged-scope-launch` 排除含 `goAsync()` 的函式,K1 用位元組碼判同一件事:同一個方法裡也呼叫了 `goAsync`)。`FreezingArchRule` 第一次要建清單檔,`src/test/resources/archunit.properties` 寫 `freeze.store.default.allowStoreCreation=true`(實驗 E5 驗預設值與這行要不要)。
     - **T13**:只用 0.17.3 與 1.0.0-beta.1 都有的 API(`classes(includeNested = true)`、`parents(indirectParents = true)`、`properties(includeNested = false)`、`isVar`、`type.isMutableType`、`type.name`,預實驗 P3);舊檔用一個常數清單排除(Konsist 沒有凍結),跟 `lumos arch-template android` 的舊檔清單是同一個概念,節開頭寫「採用目標架構產生器的專案,把這支併進產生的測試檔、舊檔清單共用」。不判 `java.*` 型別(見〈範圍〉決定 2)。
     - **T4 補**:〈測試:API-30 Ktor 版〉配〈依賴:Ktor〉(引擎用 CIO,避開跟 T4 的 OkHttp 主版本打架;版本照實驗 E8 挑對得上 Kotlin 2.2.21 的),〈好寫法:API-30 區塊內讀完〉、〈壞寫法:API-30 response 帶出區塊〉;壞寫法讀 body 丟取消例外,`runCatching` 後斷言。
2. **型錄改值**(`skills/kotlin-idioms/checks-catalog.md` 通電批次欄的「行為測試或正向約束=」那段):儀器批 25 列改「範本 T6」~「範本 T11」;API-9 改「範本 T12」、UI-39 改「範本 T13」、API-30 改「範本 T4」;CO-5 改「不接(代碼審或真機)」。實驗把某列移出時,同一個提交裡改回「未接(儀器批)」並在驗證紀錄記原因。另改兩處內容:UI-39 的「後果」欄改寫成強跳過模式下的後果(見決定 2,附出處);ARCH-56 的出處欄補 dagger.dev 原句(調研時找不到的那句)。〈輸入與口徑〉不用改(前半已寫「範本 T<n>」的意思)。
3. **資料測試跟著改期望**(都在 `scripts/test_lumos.py`,共五支):
   - `t_kotlin_catalog_c_rows_batch_resolved`:允許的範本組從 T0–T5 擴成 T0–T13;未接值清單(`_KT_UNWIRED`)拿掉「未接(架構測試後續計劃)」與「未接(Ktor 範本後續)」兩個值(這兩個值本批後不該再出現);寫死的「範本 32 列」改成照新〈範圍〉的列數與各組列編號。允許的值不新增新種類,只是範圍變了。
   - `t_kotlin_test_templates_sections`:**新寫內容檢查**——範本檔有 `## T6`~`## T13` 與〈Android 實驗專案骨架〉,骨架節含 `sdk=34` 與 `testInstrumentationRunner`(現在這支只驗 `template_problems` 與三種改壞,沒有內容檢查)。
   - `t_kotlin_test_templates_content_guards`:斷言範本組清單的地方從 T0–T5 改成 T0–T13;加 S3 那幾個禁用寫法。
   - `t_kotlin_test_templates_linked`:加 S7 的兩句。
   - `t_kotlin_catalog_instrumented_batch_notes`(新增):驗 S6。
4. **指路**:測試品質標準(`skills/lumos-project-notes/commands/test-quality-standard.md`)〈Android 資料層(Room)的撰寫補充〉一節的「升級」條尾加一句指到範本 T6;〈Android 本機單元測試的驗收標準〉加一句「要 Android 框架的測試(Fragment、LiveData、WorkManager、Compose)先看範本 T7–T11,Robolectric 釘 `sdk=34` 的理由在範本骨架」;kotlin-idioms `SKILL.md` 開頭那句(已指 `test-templates.md`)不用改。
5. **實驗與驗證紀錄**:照〈實驗〉逐項跑,結果寫進一篇 `Verification/` 驗證紀錄(`plan_refs` 連回這篇)。
6. **寫回家**:[[Systems/kotlin規則包]] 記範本檔多了 T6–T13 與 Android 骨架、型錄 UI-39 後果改寫與 CO-5 改歸;[[Systems/test-quality-cli]] 記指路兩句。

決定(本計劃自答,附出處):

1. **K1–K3 用位元組碼與宣告判,不用字面**:設計審 r1 打穿的四種寫法全是「拿文字比對判語意」造成的。先查世界:ArchUnit 官方寫明它「analyzing given Java bytecode, importing all classes into a Java code structure」,呼叫與欄位存取是解析後的完整型別,不受 import 寫法、註解、字串影響;Konsist 讀原始碼宣告,有父型別、`isVar`、`isMutableType`,但看不進函式本體的運算式(只有 `text`)。所以函式本體裡的事(K1、K2)交給 ArchUnit,宣告層的事(K3)交給 Konsist;預實驗 P3 證過兩邊各自把 r1 的漏報與誤報樣本判對。代價:消費專案多一個測試依賴 ArchUnit(決策 d1 裁定照這樣做)。
2. **K3 不判 `java.*` 型別、UI-39 後果改寫**:官方強跳過頁「Strong Skipping is enabled by default in Kotlin 2.0.20」「Unstable parameters are compared using instance equality (===)」——不穩定的參數不再讓畫面「不可跳過」,而是用同一個實例比。`java.time.Instant` 這類不可變型別每次狀態更新都是新實例,沒有壞處;真正的壞處是 `var` 或可變集合**就地改**:實例沒變,強跳過下畫面直接被跳過、不更新。型錄 UI-39 後果欄「不可跳過,多餘重組」是強跳過之前的說法,改寫成兩種情況並附出處(Kotlin 2.0.20 之前照舊)。
3. **K2 對應 CO-1、不對應 CO-5**:CO-5 的壞形狀是 `suspend fun load() = dao.blockingQuery()`,沒有 dispatcher 字樣,K2 判不到(預實驗 P3 `Thread.sleep` 那個樣本綠,r1 通才 F6)。查過的行為測法:BlockHound 能在「被標成不准阻塞的執行緒」上抓阻塞呼叫,但單元測試的資料層都是假實作,真阻塞根本不發生,抓不到;要真 I/O 才抓得到,那就是真機。CO-5 改「不接(代碼審或真機)」,真機那半已有 PERF-1/2 的 StrictMode 路線(lumos-android-evidence)。K2 是 CO-1「Dispatcher 可注入」的整個範圍版,CO-1 的接電方式欄只有告警,本批不替它加接電方式,T12 節開頭寫明它順帶驗 CO-1。
4. **K4 不做成架構測試、ARCH-56 改成行為測試**:哪個 Activity 承載哪個 Fragment 是執行時才定(導航圖、`supportFragmentManager`),宣告層只能保守近似(有一個 Hilt Fragment 就要所有 Activity 都標),會誤報不承載它的 Activity。依據補到了:dagger.dev「So before adding @AndroidEntryPoint to a fragment, the activity must be annotated as well.」。改成 T11 的行為測試:把 Hilt Fragment 放進宿主 Activity,斷言沒丟例外。
5. **K5 不做**:「改了資料庫版本卻沒有升級測試」已由 room-guard 在推送前擋([[Projects/Room資料庫測試守衛_計劃]] 條款 S6、S7:要有一支提到 `MigrationTestHelper` 與資料庫類別、帶新版本號或跑完全部升級的測試)。DATA-19 的行為測試接範本 T6;再做一支 Konsist「每個 Migration 物件有測試類別」只是同一件事的弱版(`hasTestClasses` 只看名字對得上,調研稿)。
6. **API-30 改做**:前半移出的兩個理由,「依據不全」已不成立——Ktor API 頁 `execute` 原文「The response object should not be accessed outside of block as it will be canceled upon block completion」;「多一套 HTTP 用戶端」的成本只落在用 Ktor 的消費專案(範本是照抄的,不用 Ktor 的專案不加依賴)。

### 不做(與理由)

- **CO-5 的行為測試**:見決定 3,改「不接(代碼審或真機)」。
- **K4、K5 的架構測試**:見決定 4、5。
- **Konsist 換版(產生器 `lumos arch-template android` 的產出)**:本批不換(決策 d2)。理由:①T13 只用兩版共通的 API,不需要換;②換版要改產生器資料檔三處 `resideInPackage`、技能文件的版本句,還要重核 `scripts/lumos` 的 `_arch_tpl_konsist_test`(它照 0.17.3 反組譯「哪些檔算測試原始碼集」,1.0.0-beta.1 的發行說明寫 `scopeFromProduction` 改成解析前就過濾),那是 [[Systems/android-arch-template]] 的事,跟範本無關;③1.0.0-beta.1 的發行說明自稱「the final release before 1.0.0」「the API freeze candidate」,正式版近,等它省一次重核。預實驗 P3 已驗「舊名在 beta.1 編不過、新名可用」,換版時直接用。
- **不在本 repo 的 CI 或推送閘跑 Gradle、模擬器**:同前半;[[Projects/Room資料庫測試守衛_計劃]] 否決過「推送前故障注入(要編譯跑 Android 測試,太慢)」。
- **不改任何推送閘、收證工具、新增告警閘、`check.py` 的判定**;不新增 lumos 子命令;不動規則包的規則。
- **不用使用者的實機跑實驗**:實機是使用者的平板,實驗裝 APK、跑測試會留東西;只用模擬器 `kds_bench`。
- **Room 3(`androidx.room3`)**:範本寫 Room 2.7 以上的 API;Room 3 換了套件名,另見 REVISIT。

### K 測試、規則包、detekt 的分工

| 型錄列 | 規則包(ast-grep) | detekt | K 測試(本批) |
|---|---|---|---|
| API-9 | `kt-unmanaged-scope-launch`、`kt-compose-globalscope-in-composable`:語法樹判整支檔,新增告警閘只報這次新增的行;含 `goAsync()` 的函式豁免;Fragment 用 `lifecycleScope` 沒有規則 | `GlobalCoroutineUsage`(不要型別資訊,只認 import 後的 `GlobalScope.launch/async`) | T12 K1:整個專案、位元組碼判、舊違規凍結、`goAsync` 同豁免;Fragment `lifecycleScope` 那半由 T11 的行為測試接 |
| CO-1 | `kt-hardcoded-dispatchers-io`(訊息以 `[CO-1]` 開頭):名字結尾 Repository/DataSource 的類別;新增告警閘只報新增的行 | `InjectDispatcher`(要型別資訊,CI 的 Gradle 那步才響) | T12 K2:資料層套件、整個專案、位元組碼判、DI 模組豁免 |
| UI-39 | 沒有直接對應的規則;同形的 `kt-uistate-mutable-field` 訊息以 `[PERF-30]` 開頭,掛在型錄 PERF-30(「data class 帶 var 或可變集合欄位」,級 A+B,不是 C 列、不在本批範圍) | 無 | T13 K3:整個專案、宣告判、含間接父型別、舊檔清單排除 |

改 API-9、CO-1 的標準寫法時,規則包、detekt、T12 三邊一起看;改 UI-39 時要連 PERF-30 與它的規則一起看(規則訊息掛的是 PERF-30,不會因 UI-39 改了而被看到),T13 節開頭寫這一句。規則包(經新增告警閘)與 detekt(推送前只給改到的檔時)管「這次寫的」,K 測試管「整個專案現在有沒有」,而且跑在專案自己的單元測試裡、不靠 lumos 有沒有裝。

## 實驗(每個機制都跑一遍,找漏洞)

照使用者第二要點,實作時逐項跑;結果不符預期就照第一要點先查官方與業界做法再改,寫進〈依據來源〉與審計修正紀錄。Android 實驗專案從 lab `git clone` 到會談暫存區;模擬器 `kds_bench` 無視窗開,實驗完自己關;Gradle 8.13、JDK 17。

- **E1 紅要是斷言紅**:每組〈測試〉列的每個紅,Robolectric 與 JVM 讀 JUnit XML 的型別、儀器測試讀 XML 第一行與 JUnit 斷言框,用 `assertion_failure` 判,全部要是斷言失敗。已知會是例外紅、範本要先改寫的:T6 少 Migration(`IllegalStateException`)、SQL 錯與 DATA-21(`SQLiteException`)、T7 DATA-58(`IllegalStateException: Attempt to collect twice`)、T9 STATE-23(存不進 Bundle)、STATE-12(`ComposeTimeoutException`)、無障礙兩列(`AccessibilityViewCheckException`,預實驗 P1 已證 `runCatching` 後是斷言紅)、T10(`NoLeakAssertionFailedError`)、T11 ARCH-31 與 ARCH-56(`IllegalStateException`)、T4 API-30(取消例外)、T12 與 T13(ArchUnit 的 `AssertionError`、Konsist 的 `KoAssertionFailedException`——後者型別名收證不認,T13 改成收集違規再 `assertEquals(emptyList(), 違規)`)。
- **E2 每格只紅點名的那支**:同前半;小節裡每支 `@Test` 都在矩陣出現。
- **E3 時序穩定**:JVM 與 Robolectric 的每格重跑 20 次、模擬器的每格重跑 5 次(一次要裝 APK,約一分鐘),結果要每次一樣;不穩的那支改寫或拿掉,型錄那列改回「未接(儀器批)」並寫原因。T9 有動畫與時鐘的格子(TEST-29、STATE-12)、T11 STATE-17(Looper 排程)特別看。
- **E4 跑在哪的對照**:T7 DATA-58、T8、T9 九列、T11 在 Robolectric 跑完矩陣後,再在模擬器跑一次同一份(放 `androidTest`),結果要一樣;不一樣的照官方說法改成只在模擬器跑,節開頭寫明。T9 無障礙兩列反過來在 Robolectric 跑一次,記下它照綠(重做預實驗 P1,證明「只在模擬器」那句)。
- **E5 K1、K2 在 Android 模組**:lab 複本的 `src/test` 放 T12,`ClassFileImporter` 匯入 app 的套件(Android 本機單元測試的類別路徑有編譯後的 app 類別),預實驗 P3 的樣本搬進 `src/main` 跑一次,結果要一樣;另加 Android 才有的樣本:`viewModelScope.launch`(綠)、Fragment 裡 `lifecycleScope.launch`(T12 綠——那半由 T11 的 API-9 小節接)、`@HiltAndroidApp class App : Application()` 裡建 `appScope`(綠)、`BroadcastReceiver.onReceive` 裡 `goAsync()` 後建 scope(綠)、同一個 Receiver 沒有 `goAsync()` 就建 scope(紅);先不放 `archunit.properties` 跑一次,記下 ArchUnit 預設准不准建清單檔。凍結:第一次跑把既有違規寫進清單檔、測試綠;加一個新違規→紅;修掉一個舊違規→綠且清單縮小;清單檔放 `src/test/resources`,改壞(刪掉清單檔)後舊違規全部重新紅。
- **E6 K3 在 Android 模組**:同上放 T13,樣本加 `@Immutable data class XUiState(var a: Int)`(紅:標註不改變就地修改的壞處)、`typealias Items = MutableList<String>` 的屬性、泛型 `List<MutableList<String>>`(記下 `isMutableType` 只看最外層的話是天花板)、`data object Loading : HomeUiState`(物件沒有屬性,不影響);Konsist 0.17.3 與 1.0.0-beta.1 各跑一次,結果要一樣;沒有 gradlew 的資料夾 Konsist 例外紅(調研實測),骨架寫明。
- **E7 每道檢查各改壞一次**:T12 的三個豁免(允許類別、帶 `DefaultConstructorMarker` 的合成建構子、`goAsync`)、T13 的「間接父型別」條件,各拿掉一次,對應的好樣本要轉紅(預實驗 P3 已在純 JVM 做過一次,這裡在 Android 模組重做)。
- **E8 Ktor 版本**:Ktor client(CIO 引擎)在 Kotlin 2.2.21 編得過的最新版(前半 kotlinx-serialization 1.12.0 就因綁 Kotlin 2.4 編不過);跟 T4 的 OkHttp 4 與 5 兩套依賴並存時都要能跑;好寫法綠、壞寫法斷言紅。
- **E9 ARCH-56 的 Hilt 設定**:lab 複本加 Hilt 外掛與 KSP、`hilt-android-testing`,Robolectric 用 `@HiltAndroidTest` 與 `HiltTestApplication`,壞寫法(宿主沒標)要在 `runCatching` 裡丟 `IllegalStateException`、好寫法綠;Robolectric 跑不起來就改在模擬器跑;兩邊都跑不起來,ARCH-56 照〈做法〉2 改回「未接(儀器批)」(跟其他實驗移出的列同一個值,S1 的計數照算),驗證紀錄記原因並註明「第一次開那個畫面就崩,端到端驗收的 flow 走到就紅」。
- **E10 Room 版本與結構檔**:T6 在 Room 2.7.2(lab 用的)與實作當天 Google Maven 上 Room 2 的最新穩定版各跑一次矩陣,結果要一樣;結構檔沒加進 `androidTest` assets 時 `MigrationTestHelper` 的錯誤訊息記進範本的坑。
- **E12 LeakCanary 在 debug 建置拿得到堆積**:T10 在模擬器的 debug 建置跑一次,壞寫法(留住 Activity 的單例)要斷言紅、好寫法綠,記下 `assertNoLeaks()` 有沒有拿到堆積;拿不到(像 [[Projects/Android記憶體與穩定性驗收_計劃]] 在實機 profileable 建置遇到的 `SecurityException`)就把 TEST-35 照〈做法〉2 改回「未接(儀器批)」。
- **E11 自檢與資料測試**:型錄改值後跑 `python3.14 scripts/test_lumos.py -k kotlin_`,`template_problems` 零問題、`t_kotlin_catalog_c_rows_batch_resolved` 綠;把某列改成「範本 T14」要被報(沿用前半的自檢,這裡只確認新節認得到)。

## 實務隱患

(`lumos pitfalls <計劃> --check` 逐類答,結果見節末)

- **範本照抄出錯被當成標準**:同前半,〈怎麼用〉第 5 步「在自己的專案跑一次,綠了才算」照舊;儀器範本另寫明「要開模擬器跑」。
- **範本的壞例被本 repo 的推送閘當產品碼**:壞例都在 Markdown 圍欄裡,repo 不新增 `.kt` 檔;實驗專案只在會談暫存區。
- **實驗動到別人的工作目錄**:lab 有別人沒提交的改動;一律 `git clone` 到暫存區,不在原地改、不在原地跑 Gradle。
- **模擬器與 Gradle 常駐程序吃資源**:模擬器 2G RAM、無視窗;實驗完 `adb -s emulator-5554 emu kill` 關掉自己開的那台;Gradle daemon 是共用的,不停。
- **消費專案的 JDK**:Robolectric 對 SDK 36 要 JDK 21;骨架釘 `sdk=34`,專案用 JDK 21 時可拿掉(回頭條件見節末)。
- **ArchUnit 與 Konsist 的版本漂移**:版本只寫在範本檔各組〈依賴〉;Konsist 正式版出來後 T13 要重跑(回頭條件見節末)。
- **凍結清單被當成「已處理」**:`FreezingArchRule` 的清單檔讓舊違規永遠綠;範本節開頭寫明「清單只能縮小,新增一筆要在代碼審說明」,不機械擋(消費專案的事,本 repo 驗不到)。
- **效能**:型錄自檢多讀的只有範本檔變長(多八節),判法不變。
- **併發**:實驗在會談暫存區;本 repo 只改 Markdown 與一支資料測試的期望。
- **守衛面**:型錄自檢與資料測試在本 repo CI 跑;不改任何推送閘或收證判定。
- **舊否決對照**:見審計修正紀錄第一行。
- 前端:不改任何前端檔;本計劃的「畫面」都是 Android Compose。
- 已排除:金流:範本與實驗只用假資料。
- 已排除:對外送出:MockWebServer 只聽本機回環位址;實驗只從 Maven Central 與 Google Maven 下載依賴;模擬器不登入任何帳號。
- 已排除:不可逆:新增 Markdown 節、改型錄文字與一支測試的期望,退提交即回原狀。

REVISIT:2027-02-06 範本檔 T6–T13 各組〈依賴〉的版本(Room、Paging、WorkManager、Compose BOM、LeakCanary、Robolectric、ArchUnit、Konsist、Ktor)與 Maven Central、Google Maven 最新版對一次,有大版本差就重跑那組的紅綠矩陣
REVISIT:2027-03-31 Konsist 出 1.0.0 正式版時,重跑實驗 E6(T13 兩版共通),並開 [[Systems/android-arch-template]] 的換版工作(產生器資料檔三處 `resideInPackage`、技能文件版本句、`_arch_tpl_konsist_test` 對新版重核);到期還沒出正式版就人裁要不要翻 d2、改換 beta
REVISIT:2027-03-31 Robolectric 的 Android 15 以上要 JDK 21:查消費專案與本機 JDK,都到 21 就拿掉骨架的 `sdk=34` 那行並重跑 T7–T11
REVISIT:2027-05-06 查 Room 3(`androidx.room3`)的穩定度與消費專案有沒有人用;有就替 T6 加一份 Room 3 的〈依賴〉與 import

## 驗收條款

- [S1] 當讀型錄 C 列時,每列通電批次的「行為測試或正向約束=」值應是「範本 T0」到「範本 T13」、「未接(儀器批)」、「不接(代碼審或真機)」之一,應不再出現「未接(架構測試後續計劃)」與「未接(Ktor 範本後續)」;各值的列數與各範本組的列應等於本計劃〈範圍〉〈做〉表(實驗移出的列照〈做法〉2 計入「未接(儀器批)」),CO-5 應是「不接(代碼審或真機)」。 [test:t_kotlin_catalog_c_rows_batch_resolved]
- [S2] 當型錄自檢讀真的型錄與範本檔時,應零問題;範本檔應有 `## T6` 到 `## T13` 八節與〈Android 實驗專案骨架〉一節,骨架節應含 `sdk=34` 與 `testInstrumentationRunner`。 [test:t_kotlin_test_templates_sections]
- [S3] 當讀範本檔 T6–T13 的〈測試〉小節時,應不出現 `DetectLeaksAfterTestSuccess`、`InstantTaskExecutorRule` 與不帶 `runCatching` 的 `LeakAssertions.assertNoLeaks()`;T13 的〈測試〉應不呼叫 Konsist 的 `assertTrue`/`assertFalse`(改收集違規再比)。 [test:t_kotlin_test_templates_content_guards]
- [S4] 當在 Android 實驗專案照骨架逐格跑時,每格每支測試的結果應等於矩陣,〈測試〉列的每個紅經 `assertion_failure` 判定應是斷言失敗;JVM 與 Robolectric 的格子重跑 20 次、模擬器的格子重跑 5 次結果應不變;E4 對照兩邊結果應一致或已照官方改成只在模擬器;結果寫進驗證紀錄。 [manual:會談暫存區的 lab 複本逐格跑 Gradle 與模擬器,記每格結果、失敗型別與重跑次數]
- [S5] 當 T12、T13 在 Android 實驗專案對〈實驗〉E5、E6 列的樣本跑時,壞樣本應紅、好樣本應綠,拿掉每個豁免或條件後對應的好樣本應轉紅,凍結清單應照 E5 的四步變化;T13 在 Konsist 0.17.3 與 1.0.0-beta.1 的結果應相同。 [manual:會談暫存區的 lab 複本跑 E5、E6、E7,結果寫進驗證紀錄]
- [S6] 當讀型錄 UI-39 列時,「後果」欄應提到強跳過模式與實例相等比較,出處欄應有強跳過頁網址;讀 ARCH-56 列時出處欄應有 dagger.dev 的網址。 [test:t_kotlin_catalog_instrumented_batch_notes](新增)
- [S7] 當讀測試品質標準時,〈Android 資料層(Room)的撰寫補充〉的升級條應提到範本 T6,〈Android 本機單元測試的驗收標準〉應有一句提到範本 T7–T11 與 Robolectric 的 `sdk=34`。 [test:t_kotlin_test_templates_linked]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 型錄 DATA-19 列 | 通電批次含「行為測試或正向約束=範本 T6」 | 本計劃〈做〉表 T6;決定 5 |
| S1 | 型錄 API-9 列 | 含「行為測試或正向約束=範本 T12」 | 本計劃〈範圍〉決定 1;決策 d1(用 ArchUnit) |
| S1 | 型錄 UI-39 列 | 含「行為測試或正向約束=範本 T13」 | 決定 1、2 |
| S1 | 型錄 API-30 列 | 含「行為測試或正向約束=範本 T4」 | 本計劃〈範圍〉決定 6;Ktor execute API 頁 |
| S1 | 型錄 CO-5 列 | 含「行為測試或正向約束=不接(代碼審或真機)」 | 決定 3;r1 通才 F6 |
| S1 | 型錄 68 列 C 列(實驗全過時) | 範本 60(T0–T5 的 32 列、T4 補 1、T6–T11 共 25、T12 1、T13 1)、不接(代碼審或真機)8、未接(儀器批)0 | 本計劃〈範圍〉 |
| S2 | 真的型錄與範本檔 | 零問題 | 前半〈做法〉3 的自檢 |
| S3 | T10〈測試〉含 `@get:Rule val rule = DetectLeaksAfterTestSuccess()` | 守衛測試紅 | LeakCanary 頁「will throw a NoLeakAssertionFailedError」;收證只認斷言型別 |
| S4 | T9〈測試:無障礙〉×〈壞寫法:UI-106 24dp 可點〉,模擬器 | 斷言紅,訊息含「This item's size is 24dp x 24dp」 | 預實驗 P1;官方 Compose 無障礙測試頁 |
| S4 | 同上,Robolectric | 綠(記成天花板,不列入矩陣的〈測試〉格) | 預實驗 P1 |
| S4 | T6〈測試〉×〈壞寫法:DATA-21 不分批〉,40000 個 id | 斷言紅(不是 SQLiteException) | sqlite.org/limits.html「defaults to 999 for SQLite versions prior to 3.32.0 … or 32766」 |
| S4 | T11〈測試〉×〈壞寫法:STATE-17 連發兩次 postValue〉 | 斷言紅,收到 1 筆不是 2 筆 | LiveData 頁「only the last value would be dispatched」 |
| S5 | `fun refresh() { CoroutineScope(Dispatchers.IO).launch { } }` | T12 K1 紅 | 預實驗 P3;r1 可行性 F4 |
| S5 | `val s = rememberCoroutineScope()` | T12 K1 綠 | 預實驗 P3;r1 可行性 F4 |
| S5 | `@Module object DispatchersModule { fun io() = Dispatchers.IO }` | T12 K2 綠 | 預實驗 P3;r1 通才 F6 |
| S5 | `sealed interface HomeUiState { data class Success(var items: MutableList<String>) : HomeUiState }` | T13 K3 紅 | 預實驗 P3;r1 通才 F4、可行性 F5 |
| S5 | `data class ListUiState(val at: java.time.Instant)` | T13 K3 綠 | 決定 2;強跳過頁 |
| S6 | 型錄 UI-39 後果欄 | 提到強跳過與 `===` | developer.android.com 強跳過頁 |
| S6 | 型錄 ARCH-56 出處欄 | 含 `https://dagger.dev/hilt/android-entry-point` | 本計劃〈範圍〉決定 4;dagger.dev 原句 |
| S7 | 測試品質標準〈Android 資料層(Room)的撰寫補充〉升級條 | 含「範本 T6」 | 本計劃〈做法〉4 指路 |
| S7 | 測試品質標準〈Android 本機單元測試的驗收標準〉 | 有一句同時提到「範本 T7–T11」與 `sdk=34` | 本計劃〈做法〉4;預實驗 P2 |

## 回退

退回本計劃的提交即可,逐項是:範本檔拿掉 `## T6`~`## T13` 八節、〈Android 實驗專案骨架〉一節與 T4 的 API-30 小節;型錄 29 列的「行為測試或正向約束=」值改回前半的值(儀器批 25 列「未接(儀器批)」、API-9 與 CO-5 與 UI-39「未接(架構測試後續計劃)」、API-30「未接(Ktor 範本後續)」),UI-39 後果欄與 ARCH-56 出處欄改回;`t_kotlin_catalog_c_rows_batch_resolved` 的期望改回、`t_kotlin_test_templates_sections`、`t_kotlin_test_templates_content_guards`、`t_kotlin_test_templates_linked` 拿掉這次加的檢查、刪這次新增的 `t_kotlin_catalog_instrumented_batch_notes`;測試品質標準的兩句指路拿掉;[[Systems/kotlin規則包]] 與 [[Systems/test-quality-cli]] 這次加的行拿掉;驗證紀錄保留、狀態改成作廢並註明計劃已退回。不碰任何帳本、推送閘或 `check.py`。

## 天花板

1. 範本的紅綠只在實驗專案與模擬器 `kds_bench`(API 34)驗過;消費專案照抄改名後寫錯,本 repo 看不出來(CI 不跑 Gradle、沒有模擬器)。
2. 儀器測試要開模擬器,消費專案不會在推送前跑;它們接的是專案自己的 CI 或端到端驗收,本批不把它們接進任何閘。
3. 無障礙兩列在 Robolectric 不報(預實驗 P1),只在模擬器或真機抓得到;對比檢查要實際算繪。
4. K1 判不到 Fragment 用 `lifecycleScope` 還是 `viewLifecycleOwner.lifecycleScope`(位元組碼看不出接收者);那半只有 T11 的行為測試接,專案沒照範本替每個 Fragment 寫就沒接上,規則包沒有對應規則。
5. K1、K2 的「允許建 scope 的類別」「資料層套件」是範本常數,專案沒改就照範本預設判;凍結清單讓舊違規永遠綠。
6. K3 的 `isMutableType` 對泛型參數裡的可變型別、型別別名判不判得到看實驗 E6;判不到的寫進範本節開頭。K3 不判外部模組的類別(Konsist 只讀本專案原始碼)。
7. DATA-38 只涵蓋 CoroutineWorker;一般 `Worker` 的 `isStopped` 從測試觸發不了。
8. DATA-65 的「後寫贏」與 API-4 一樣是業務決定,選錯照綠。
9. CO-5 沒有自動測法,只剩代碼審、盲判與真機 StrictMode。

## 依據來源

每個機制一行:機制|依據|網址或實測|在哪看得到。標「調研開頁」的是第五批調研時開頁核對;「本次開頁」是寫這份計劃時用 WebFetch 開的;「預實驗」見〈前提〉。

- K1、K2 用位元組碼|「It does so by analyzing given Java bytecode, importing all classes into a Java code structure」;ArchUnit 現行 1.5.1|https://www.archunit.org/userguide/html/000_Index.html(本次開頁);預實驗 P3|範本 T12、決定 1
- 舊違規凍結|ArchUnit 使用手冊的 `FreezingArchRule`(既有專案只擋新違規)|同上(實驗 E5 驗行為)|範本 T12
- K3 用宣告|Konsist 1.0.0-beta.1 與 0.17.3 都有 `parents(indirectParents)`、`properties`、`isVar`、`isMutableType`|預實驗 P3(兩版編譯並實跑)|範本 T13
- K3 不判 java.*、UI-39 後果改寫|「Strong Skipping is enabled by default in Kotlin 2.0.20」「Unstable parameters are compared using instance equality (===)」「Stable parameters are compared using object equality」|https://developer.android.com/develop/ui/compose/performance/stability/strongskipping(本次開頁)|決定 2、型錄 UI-39
- K2 注入的理由|「Using dependency injection to provide dispatchers to your classes makes it easy to replace the real dispatchers in tests」|https://developer.android.com/kotlin/coroutines/test(調研開頁)|範本 T12
- detekt 對照|`InjectDispatcher`「Always use dependency injection to inject dispatchers for easier testing」、Requires type resolution、預設開;`GlobalCoroutineUsage`「Report usages of GlobalScope.launch and GlobalScope.async」、預設關|https://detekt.dev/docs/rules/coroutines/(本次開頁)|〈K 測試、規則包、detekt 的分工〉
- 規則包同形三條|`kt-unmanaged-scope-launch`、`kt-hardcoded-dispatchers-io`、`kt-uistate-mutable-field` 的現行判法|[[Systems/kotlin規則包]](讀規則檔)|分工表
- CO-5 不接|r1 通才 F6「完全沒有 Dispatchers 字樣,K2 綠」;預實驗 P3 `Thread.sleep` 樣本綠|`governance/review-reports/android行為測試範本與架構測試/r1-通才-sonnet.md`;預實驗 P3|決定 3
- Konsist 換版|發行說明「the final release before 1.0.0」「the API freeze candidate for 1.0.0」「Konsist targets JVM 11 again」「publishes kotlin-stdlib 2.0.21」「filter files before parsing」;安裝頁 `testImplementation("com.lemonappdev:konsist:1.0.0-beta.1")`;舊名 `resideInPackage` 編譯失敗(發行說明現版沒寫這個改名)|https://github.com/LemonAppDev/konsist/releases ;https://docs.konsist.lemonappdev.com/getting-started/getting-started/add-konsist-dependency(本次開頁);預實驗 P3|〈不做〉、Q2
- Konsist 要 gradlew|沒有 gradlew 時 `KoInternalException: Project directory not found`|調研 2026-11-06 實驗紀錄|範本 T13、E6
- K4 依據|「So before adding @AndroidEntryPoint to a fragment, the activity must be annotated as well.」「as a general rule, Hilt types need to be attached to other Hilt types to work」|https://dagger.dev/hilt/android-entry-point(本次開頁)|決定 4、型錄 ARCH-56、範本 T11
- K5 已由 room-guard 擋|升級測試要提到 `MigrationTestHelper` 與類別簡名並帶新版本號或跑完全部升級|[[Projects/Room資料庫測試守衛_計劃]] 條款 S6、S7|決定 5
- API-30 依據|「The response object should not be accessed outside of block as it will be canceled upon block completion」;不帶區塊的 `execute()`「the response body is downloaded fully into memory, and the connection is released」|https://api.ktor.io/ktor-client-core/io.ktor.client.statement/-http-statement/execute.html(本次開頁)|決定 6、範本 T4
- T6 Room 遷移|「an incorrectly defined migration can cause your app to crash」「you should include a test that covers all migrations」;缺路徑「an IllegalStateException occurs」|https://developer.android.com/training/data-storage/room/migrating-db-versions(調研開頁)|範本 T6
- T6 不用 Robolectric|「We don't recommend Android local unit tests with Robolectric」;「create an in-memory version of your database」|https://developer.android.com/training/data-storage/room/testing-db(調研開頁)|〈做〉表 T6 跑在哪
- DATA-21 參數上限|「defaults to 999 for SQLite versions prior to 3.32.0 (2020-05-22) or 32766 for SQLite versions after 3.32.0」|https://www.sqlite.org/limits.html(本次開頁)|範本 T6 DATA-21
- DATA-65、DATA-69|型錄標準寫法(「last write wins」、成功後才換)與它的查證網址 offline-first 頁|型錄 DATA-65、DATA-69 列;https://developer.android.com/topic/architecture/data-layer/offline-first|範本 T6
- T7 Paging|「the endOfPaginationReached property should be true」;「include the paging-testing dependency. It contains the asSnapshot extension」|https://developer.android.com/topic/libraries/architecture/paging/test(調研開頁)|範本 T7
- T8 WorkManager|「To test a ListenableWorker or its variants (CoroutineWorker and RxWorker), use TestListenableWorkerBuilder」;`Data`「This class will throw IllegalStateExceptions if you try to serialize or deserialize past this limit」|https://developer.android.com/develop/background-work/background-tasks/testing/persistent/worker-impl ;https://developer.android.com/reference/androidx/work/Data(調研開頁)|範本 T8
- T9 Compose 測試|「set the autoAdvance property in the mainClock to false」;「The useUnmergedTree parameter is available in all finders」;「There are specific APIs to achieve this, such as StateRestorationTester」;事件頁「the UI needs to notify the ViewModel of that」、`dropUnlessResumed`|https://developer.android.com/develop/ui/compose/testing/synchronization ;…/testing/apis ;…/state-saving ;https://developer.android.com/topic/architecture/ui-layer/events(調研開頁)|範本 T9
- T9 無障礙|「Other available checks look for accessibility issues with color contrast, small touch target size」;Robolectric 不報、模擬器報|https://developer.android.com/develop/ui/compose/accessibility/testing(調研開頁);預實驗 P1|範本 T9、天花板 3
- T10 LeakCanary|`androidTestImplementation 'com.squareup.leakcanary:leakcanary-android-instrumentation:2.14'`;「If application leaks are found, LeakAssertions.assertNoLeaks() will throw a NoLeakAssertionFailedError」|https://square.github.io/leakcanary/ui-tests/(本次開頁)|範本 T10、S3
- T11 FragmentScenario 在 Robolectric|「FragmentScenario, which offers APIs to safely create your Fragment under test and drive it through valid transitions」|https://robolectric.org/androidx_test/(調研開頁)|範本 T11
- STATE-17 不用 InstantTaskExecutorRule|LiveData「only the last value would be dispatched」;`InstantTaskExecutorRule`「executes each task synchronously」|https://developer.android.com/reference/androidx/lifecycle/LiveData ;https://developer.android.com/reference/androidx/arch/core/executor/testing/InstantTaskExecutorRule(前半 r1 依據席核對)|範本 T11
- Robolectric 要釘 sdk=34|Robolectric 4.16 在 JDK 17 對 SDK 36 例外紅「Android SDK 36 requires Java 21 (have Java 17)」|預實驗 P2|範本〈Android 實驗專案骨架〉
- 儀器測試的紅要是斷言紅|AGP 儀器測試 XML 沒有型別,收證看第一行與 JUnit 斷言框;預實驗 P1 的 `runCatching` 加 `assertNull` 第一行是 `java.lang.AssertionError`|`scripts/test_quality.py` 的 `assertion_failure`;預實驗 P1|實驗 E1
- 範本放法與自檢|沿用前半的範本檔、`template_problems`、通電批次欄|[[Projects/Android行為測試範本與架構測試_計劃]]〈做法〉1–3|〈做法〉1–3

## 待決問題

(開頭欄位 Q1–Q4 都已結;這裡只放長版)

- Q1 K1、K2 要不要用 ArchUnit → 決策 d1:用(決定 1、預實驗 P3)。當時的另一選項是不用:API-9 與 CO-1 的整個範圍版交給 detekt(`GlobalCoroutineUsage` 不要型別資訊、`InjectDispatcher` 要 CI 的 Gradle 那步)加規則包,API-9 改「不接(代碼審或真機)」,T12 不做;代價是函式本體當場建 scope 只剩規則包看新增的行。
- Q2 產生器的 Konsist 要不要現在換 1.0.0-beta.1 → 決策 d2:先不換、等正式版(〈不做〉第三條、REVISIT)。之後要換就另開 [[Systems/android-arch-template]] 的工作,範圍是前半〈不做〉記的三件事。
- Q3 K5 → 自答不做(決定 5)。Q4 API-30 → 自答做(決定 6)。

## 審計修正紀錄

- 舊否決對照(2026-11-06 動筆時跑 `lumos rejections`,459 行,按 ArchUnit、Konsist、Robolectric、模擬器、LeakCanary、凍結、Hilt、Ktor 等概念比對):沒有撞到本案的否決。最近的一條是 [[Projects/Android記憶體與穩定性驗收_計劃]] 否決「LeakCanary 本身」當驗收工具——它靠 `am dumpheap`,在使用者實機 Android 16 上對 profileable 建置回 `SecurityException: Process not debuggable`;本案 T10 跑在模擬器的 debug 建置(可除錯),不是那個情境,實驗 E12 會實證;若 debug 建置也拿不到堆積,T10 照〈做法〉2 改回「未接(儀器批)」。前半核過的三條同向否決(Room 守衛否決推送前故障注入、Macrobenchmark 否決 lumos 呼叫 gradlew、逐層診斷否決 skill 附腳本讓消費專案呼叫)本案照舊不碰。Konsist 那條(前半 Q3/d3 被 d4 取代)本案沿用 d4 的方向:產生器不在本批換版。
