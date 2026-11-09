---
type: project
status: done
created: 2026-11-06
updated: 2026-11-09
tags:
  - type/project
  - status/done
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
  - content: 翻案:K1、K2 改用 ArchUnit,推翻 Projects/Android的MVVM與DDD目標架構範本_計劃 對 ArchUnit「屬 Java 生態、不選」的舊否決;分工是 ArchUnit 只管看得進函式本體的兩條(協程歸屬、寫死 dispatcher),目標架構分層與 K3 照舊用 Konsist
    id: d3
    context: 設計審 r1 架構對齊席 F1 指出 d1 撞到舊否決;使用者被問「上次因為這個理由否決,現在還這麼想嗎」後裁定
    why_chosen: 使用者 2026-11-06 原話「A」(選項 A:翻案改用 ArchUnit);舊否決是挑整套目標架構分層規則時做的,本案要判函式本體,Konsist 只讀宣告看不進去,預實驗 P3 證 ArchUnit 把設計審打穿的寫法全判對
    decided: 2026-11-06
    valid: true
---
# Android儀器測試範本與架構測試_計劃

> 白話:第五批前半([[Projects/Android行為測試範本與架構測試_計劃]])替型錄 32 列「長相看不出錯、要跑起來才知道」的寫法做了純 JVM 測試範本,另外 29 列移到後續:要模擬器或 Robolectric 的 25 列(儀器批)、前半打算做成架構測試 K1–K3 的三列(API-9、CO-5、UI-39)、一列 Ktor(API-30)。這份計劃把它們接完:儀器批照前半的格式加進同一份範本檔(T6–T11),每組附「好寫法綠、壞寫法紅」的對照、實作時真的在模擬器或 Robolectric 跑;架構測試改成不看字面的判法(K1、K2 讀編譯後的位元組碼,K3 讀 Kotlin 宣告),做成照抄範本 T12、T13——K2 的對象改成 CO-1(見〈用詞〉K 測試);Ktor 那列併進 T4。做不到的寫理由:CO-5(suspend 函式要 main-safe)本質是「有沒有真的阻塞」,架構測試驗不到,改歸代碼審或真機;K5(每個 Migration 要有測試)已由 room-guard 在推送前擋,不另做;Konsist 換版等 1.0.0 正式版(決策 d2)。

立案:使用者 2026-11-06 原話「遵照上面三個要點，完成這五個批次功能，目標是把Android靜態能先掃描的實務隱患都先處理過」,三要點「1.實作連續被打穿、或顯著無法收斂，就上網印證方向、業界實作找最佳解 2.所有機制都要實驗一遍，看看可行性、有沒有漏洞，修的流程遵照第一條 3.Android的規則也一樣，來源、依據，這可以在語意盲判的時候起到輔助判別的作用」,另一句「我們開發的過程中，所有機制的依據來源，最後也要補回plan，方便後續迭代」。輸入:前半計劃的〈不做〉、決策 d4 與設計審 r1 卷證(`governance/review-reports/android行為測試範本與架構測試/`,通才 F4–F6、可行性 F4–F6 共六條發現,打穿的是四種寫法:函式本體當場建 scope、`rememberCoroutineScope`、sealed UiState、DI 模組)、第五批調研稿(會談暫存區,要用的結論已搬進〈依據來源〉)、本計劃動筆時的本機預實驗(〈前提〉)。

PRIOR-ART: ①儀器測試全照官方測試頁的寫法:Room `MigrationTestHelper` 與記憶體資料庫、Paging `asSnapshot` 與 RemoteMediator 三情境、WorkManager `TestListenableWorkerBuilder`、Compose `createComposeRule`/`StateRestorationTester`/`mainClock.autoAdvance`/`useUnmergedTree`/`enableAccessibilityChecks`、LeakCanary `LeakAssertions.assertNoLeaks()`、`FragmentScenario` 與 `TestLifecycleOwner`;Robolectric 照官方 androidx_test 頁跑同一份 AndroidX Test API。②K1、K2 照 ArchUnit 的位元組碼匯入(`ClassFileImporter`)與舊違規凍結(`FreezingArchRule`,ArchUnit 官方給既有專案的做法);K3 照 Konsist starter snippets 的宣告層斷言;三條都不自寫解析器。用 ArchUnit 是翻案(決策 d3):[[Projects/Android的MVVM與DDD目標架構範本_計劃]] 的 PRIOR-ART 否決過「ArchUnit 加 jMolecules……屬 Java 生態,沒查到在 Kotlin 編譯出的類別上的實證,不選」;翻案理由與分工見〈範圍〉決定 1。③範本檔、紅綠矩陣、通電批次欄的值與 `check.py` 的 `template_problems` 全沿用前半,不新增認領語法或自檢項;範本格式只多兩個小元素——每組節開頭一句「跑在哪」、跑法不同的測試另開小節(例〈測試:無障礙〉)——因為同一組的列有的在 Robolectric、有的只能在模擬器,前半全是純 JVM 沒有這個需要。④紅要是斷言紅,照收證工具 `scripts/test_quality.py` 的 `assertion_failure`(儀器測試 XML 沒有型別,看第一行與 JUnit 斷言框)。裁定:全借用;新寫的只有範本內容、一節 Android 實驗專案骨架、型錄的值與幾支資料測試的期望。
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
- **凍結**:ArchUnit `FreezingArchRule` 把第一次跑出的違規存成一份清單檔,之後只有清單外的新違規才紅;清單要變(建清單、加規則、改規則描述、修掉舊違規)一律帶 `-ParchunitFreezeInit` 跑一次並提交,不帶時這些都紅(代碼審 code-android儀器測試範本 r1 後加 `allowStoreUpdate=false`,見審計修正紀錄)。

## 前提(2026-11-06 動筆時本機查到與預實驗)

- **裝置**:`adb devices` 有一台實機 `R52X305YY7W`(Samsung SM-X710,API 36,使用者的平板,實驗不用它);`emulator -list-avds` 有 `kds_bench`(system-images android-34 google_apis arm64-v8a,2G RAM),無視窗開機 30 秒內 `sys.boot_completed=1`。實驗一律用這台模擬器;本機 JDK 是 JBR 17.0.14,Gradle 8.13、AGP 8.13.2、Kotlin 2.2.21(macrobench-lab 示範專案的組合)。
- **示範專案**:`/Users/enzo/lumos-scratch/android-checks/scratchpad/lab` 有 gradlew,但工作目錄有別人沒提交的改動(`app/build.gradle.kts` 改過、多一個未追蹤目錄),**不碰它**;實驗一律 `git clone` 到會談暫存區再改。
- **預實驗 P1(無障礙檢查在哪跑得出來)**:在 lab 複本加一支測試,24dp 可點方塊 vs 48dp 方塊,`enableAccessibilityChecks()` 後 `tryPerformAccessibilityChecks()`。模擬器:24dp 那支丟 `AccessibilityViewCheckException`(「This item's size is 24dp x 24dp」),用 `runCatching` 接住後斷言紅,48dp 綠;**Robolectric 4.16:兩支都綠——無障礙檢查在 Robolectric 不報**。所以 T9 的無障礙兩列只能在模擬器跑。
- **預實驗 P2(Robolectric 與 JDK)**:Robolectric 4.16 對 targetSdk 36 的專案(lab 的設定)預設用 SDK 36,在 JDK 17 上整個類別例外紅「Android SDK 36 requires Java 21 (have Java 17)」;在 `src/test/resources/robolectric.properties` 寫 `sdk=34` 後正常。骨架要寫這一行。r1 可行性 F7 實跑補充:不設 targetSdk 時 Robolectric 用 minSdk(SDK 24)跑、不釘也綠,但那就跟模擬器 API 34 不同級;所以骨架明寫 `targetSdk = 36` 加 `sdk=34`。P1、P2 都只在 Robolectric 4.16 量過,Maven Central 現有 4.16.1 與 4.17(r1 依據 F5),實作時用 4.17 重跑(實驗 E4)。
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
| T8 WorkManager | DATA-38、DATA-39(2) | `TestListenableWorkerBuilder` 建 CoroutineWorker,取消後用假依賴的計數斷言「取消後沒再跑一圈、沒記成錯誤、資源關了一次」;被測程式產的 `Data` 斷言小於上限 | Robolectric |
| T9 Compose UI | STATE-12、STATE-23、UI-36、UI-52、ARCH-2、ARCH-3、TEST-29、TEST-32、DATA-63;無障礙 UI-106、UI-110(11) | `createComposeRule` 掛畫面、假 ViewModel 推狀態;訊息顯示後已消費、`StateRestorationTester` 還原、`snapshotFlow` 有發、項目載入前有高度、返回不被推回、連點只多一頁、動畫關自動推進、子節點用未合併樹、載入中不顯示空畫面;無障礙用 `enableAccessibilityChecks()` | 九列 Robolectric(實驗 E4 在模擬器對一次);無障礙兩列只在模擬器(預實驗 P1) |
| T10 LeakCanary | TEST-35(1) | 走完一個畫面流程後 `LeakAssertions.assertNoLeaks()`,用 `runCatching` 接住再斷言 | 模擬器 |
| T11 生命週期與框架 | ARCH-31、ARCH-35、STATE-17、ARCH-56(4) | `FragmentScenario` 移到 CREATED 後送回呼斷言沒丟例外;`TestLifecycleOwner` 走到 DESTROYED 斷言監聽數歸零;LiveData 在暫停的主 Looper 上連發兩次斷言兩筆都收到;Hilt Fragment 放進宿主 Activity 斷言沒丟例外;另接 API-9 的 Fragment 那半(view 銷毀後不再收) | Robolectric(ARCH-56 要 Hilt 測試設定,實驗 E9 決定) |
| T12 架構測試:協程歸屬(ArchUnit) | API-9(1;K1),另含 K2(CO-1,型錄 CO-1 列不改值) | 位元組碼判:不准 `GlobalScope`、不准在允許類別外呼叫 `CoroutineScope()`/`MainScope()`(允許與否看最外層宣告類別);資料層不准呼叫 `Dispatchers.IO/Default`(建構子與函式的預設值、DI 模組豁免);不匯入測試類別;舊違規凍結 | 專案的本機單元測試(JVM) |
| T13 架構測試:UiState 不可變(Konsist) | UI-39(1;K3) | 宣告判,只掃正式程式(`scopeFromProduction`):名字結尾 `UiState`(後綴清單是常數,可加)或父型別(含間接)結尾同樣後綴的類別,屬性不准 `var`、型別不准是可變型別或 `ArrayList`/`HashMap`/`HashSet` | 專案的本機單元測試(JVM) |
| T4 補 Ktor | API-30(1) | 真的 Ktor client(CIO 引擎)打 JDK 內建的 `com.sun.net.httpserver.HttpServer`(不用 MockWebServer,測試不碰 OkHttp),斷言在 `execute { }` 區塊裡讀完的 body 是完整的;壞寫法把 response 帶出區塊再讀 | Android app 模組的本機單元測試(照〈Android 實驗專案骨架〉組;沒在純 JVM 專案跑過) |

做法:

1. **範本檔 `skills/kotlin-idioms/test-templates.md` 加節**(不另開檔;節標題照前半 `## T<n> ` 規則,`check.py` 的 `template_problems` 原樣驗得到):
   - 新節〈Android 實驗專案骨架〉放在〈實驗專案骨架〉之後:`settings.gradle.kts`、根 `build.gradle.kts`、`app/build.gradle.kts` 全文(AGP 8.13.2、Kotlin 2.2.21 與 Compose 外掛、compileSdk 36、`targetSdk = 36`、minSdk 24、`testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"`、`testOptions.unitTests.isIncludeAndroidResources = true`),`src/test/resources/robolectric.properties` 一行 `sdk=34` 與為什麼(預實驗 P2);儀器測試指令 `ANDROID_SERIAL=<模擬器> ./gradlew :app:connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=<類別>`、Robolectric 指令 `./gradlew :app:testDebugUnitTest --tests <類別>`;每組〈依賴〉標明是 `androidTestImplementation`、`testImplementation` 還是 `debugImplementation`;跑在 Robolectric 的組(T7–T9、T11),〈依賴〉節尾另寫 `robolectric.properties` 那一行 `sdk=34` 與一句理由——〈怎麼用〉只叫消費專案抄〈依賴〉,只放骨架節的話照抄的人會漏(r1 架構對齊 F3);〈怎麼用〉第 2 步也補一句「Robolectric 組要連 `robolectric.properties` 一起抄」。
   - 每組節裡的小節照前半(〈依據〉〈依賴〉〈測試〉〈假依賴〉〈好寫法〉〈壞寫法:變體〉〈紅綠矩陣〉);節開頭一句寫「跑在哪」。
   - 範本的程式要點(寫進範本、實驗驗過才算):
     - **T6**:Room 3 已是穩定版(官方版本頁 3.0.0 於 2026-07-01、穩定版 3.0.3 於 2026-09-09;遷移頁的 `MigrationTestHelper` 範例已是 `androidx.room3:room3-testing:3.0.3`),所以 T6 寫兩份〈依賴〉:〈依賴:Room 2〉(2.8.5,套件 `androidx.room`)與〈依賴:Room 3〉(3.0.3,套件 `androidx.room3`),〈測試〉照兩個套件名各一份 import;`MigrationTestHelper` 一律用具名參數寫(`instrumentation = …, file = …, driver = …, databaseClass = AppDb::class`),不混位置參數——官方參考頁的參數順序是 `instrumentation, file, driver, databaseClass`,前一版計劃把 `AppDb::class` 放在第二個位置參數會編不過(r1 可行性 F10);DATA-17、DATA-19 一支逐版 `runMigrationsAndValidate`、一支 `addMigrations(*ALL_MIGRATIONS)` 開到最新(官方「include a test that covers all migrations」),壞寫法「少一個 Migration」丟 `IllegalStateException`、「SQL 寫錯」丟 `SQLiteException`,都 `runCatching` 後斷言;結構檔要進 `androidTest` 的 assets(`sourceSets["androidTest"].assets.srcDir("$projectDir/schemas")`,實驗驗);DATA-21 查 40000 個 id(SQLite 3.32.0 起參數上限 32766、之前 999,用 40000 讓新舊裝置都紅,壞寫法不分批、好寫法 `chunked(500)`;壞寫法丟 `SQLiteException`(too many SQL variables),測試先 `runCatching` 接住再斷言查到的筆數);DATA-69 假 API 丟 `IOException`,斷言刷新失敗後本機清單不變;DATA-65 照型錄標準寫法「後寫贏」:本機有較新未同步修改時,較舊的伺服器資料不得蓋掉,範本註解寫「衝突策略是業務決定,照情境表態換斷言」。
     - **T7**:DATA-58 對 `vm.items` 連呼兩次 `asSnapshot { }`,壞寫法(沒 `cachedIn` 再 `combine` 或兩處收)丟 `IllegalStateException`,`runCatching` 後斷言;DATA-60 照官方 RemoteMediator 頁的三情境,空回應斷言 `endOfPaginationReached == true`。
     - **T8**:DATA-38 只做 CoroutineWorker 版(型錄標準寫法說它由框架自動取消)。被測 Worker 的迴圈次數有上限(從假設定讀,範本用 50),每圈呼叫假來源一次、`delay`,跑完呼叫假結果的 `markDone()`,錯誤時呼叫 `recordError()`,`finally` 關假資源;測試在 `backgroundScope` 啟動 `worker.doWork()`、推進兩圈、取消、`runCurrent()`,用 `runTest(timeout = 10.seconds)`,斷言「取消後假來源的呼叫次數沒再增加、`markDone` 0 次、`recordError` 0 次、資源 `close` 恰好 1 次」——全部是計數比較,不靠接例外。壞寫法兩種:〈壞寫法:DATA-38 迴圈裡吞取消〉(`try { delay } catch (e: Exception) {}` 在迴圈內,取消後每圈的 `delay` 立刻丟例外又被吞,沒有上限會空轉卡死——r1 可行性 F3 實跑在 Robolectric 卡 190 秒以上、`runTest` 逾時沒生效;有上限就跑完剩下的圈數並 `markDone`,斷言紅)與〈壞寫法:DATA-38 迴圈外吞取消〉(`catch (e: Exception)` 在迴圈外並 `recordError()`,前一版測試分不出它,現在 `recordError` 1 次斷言紅)。一般 `Worker` 的 `isStopped` 從測試觸發不了(官方測試頁沒示範,`stop` 是框架內部方法),寫進天花板。DATA-39 斷言被測程式產的 `Data.toByteArray().size < Data.MAX_DATA_BYTES`。
     - **T9**:STATE-12 `waitUntil` 等 `userMessage == null` 改成推時鐘後直接斷言(`waitUntil` 逾時丟的是 `ComposeTimeoutException`,不是斷言紅);STATE-23 `StateRestorationTester.emulateSavedInstanceStateRestore()` 後斷言畫面狀態還在,存不進 Bundle 的型別丟例外用 `runCatching`;TEST-29 `mainClock.autoAdvance = false` 加 `advanceTimeBy`;TEST-32 `useUnmergedTree = true`;ARCH-3 先 `mainClock.autoAdvance = false`,同一個節點 `performClick()` 兩次(中間不推時鐘)後再推時鐘,斷言返回堆疊只多一頁——時鐘自動推進時第一次點擊的轉場立刻跑完、生命週期回到 RESUMED,好寫法 `dropUnlessResumed` 也會多一頁(r1 依據 F6);ARCH-2 用 `TestNavHostController`(Navigation 測試套件,實驗查版本)導航到 B、`popBackStack()` 後斷言目前目的地是 A;無障礙兩列(〈測試:無障礙〉小節,節開頭寫「只在模擬器」)照預實驗 P1 的寫法。
     - **T10**:不用 `DetectLeaksAfterTestSuccess` 規則(它在測試本體外丟 `NoLeakAssertionFailedError`;這個型別雖可能是 `AssertionError` 的子類,收證照型別名判、儀器 XML 只看第一行是不是 `java.lang.AssertionError`,所以不認,實驗 E1 實跑確認型別),改在測試最後 `runCatching { LeakAssertions.assertNoLeaks() }` 再 `assertNull`。
     - **T11**:STATE-17 不用 `InstantTaskExecutorRule`(它讓 `postValue` 同步執行,壞寫法照綠),改 Robolectric 暫停的主 Looper:背景執行緒連 `postValue` 兩次後 `shadowOf(getMainLooper()).idle()`,斷言觀察者收到兩筆;ARCH-31 `scenario.moveToState(CREATED)` 後送回呼,`runCatching` 接住「Can not perform this action after onSaveInstanceState」再斷言;ARCH-35 用 `TestLifecycleOwner`;ARCH-56 見 E9;**API-9 的 Fragment 那半**另一個小節〈測試:API-9 Fragment 畫面銷毀後〉:Fragment 在 `onViewCreated` 收一個假的 `MutableSharedFlow`,每收到一筆就呼叫假畫面記錄器 `render()`;記錄器在 `onDestroyView` 被標成已銷毀,之後再被呼叫就把「銷毀後被呼叫次數」加一(不丟例外)。`scenario.moveToState(CREATED)` 讓 view 銷毀後再發一筆、推主 Looper,斷言「銷毀後被呼叫次數 == 0」。壞寫法用 Fragment 自己的 `lifecycleScope`(view 沒了還在收,次數變 1,斷言紅),好寫法用 `viewLifecycleOwner.lifecycleScope` 加 `repeatOnLifecycle`(型錄 API-9 標準寫法)。不用 `runCatching`:例外丟在 `lifecycleScope.launch` 的協程裡,測試本體接不到——r1 可行性 F4 實跑 `runCatching` 沒接到、例外只印到 stderr、建置照樣成功;官方協程例外處理頁也寫 launch 的例外交給 `CoroutineExceptionHandler`。型錄 API-9 的值仍寫「範本 T12」(一列只寫一個組),T12 節開頭指到這個小節。
     - **T12**:兩支 `@Test`,各用 `FreezingArchRule.freeze(...)` 包;允許建 scope 的類別是「`Application` 子類別或標 `@Module` 的類別」,範本留一個常數讓專案改;**判允許與否看最外層宣告類別**——呼叫端類別用 `JavaClass.getEnclosingClass` 一路往外找到頂層再判,因為 Kotlin 會把程式編進別的類別:suspend lambda 的狀態機 `App$onCreate$1`(r1 可行性 F5 實跑誤報)、`AppModule$Companion` 裡的 `@Provides`(通才 F4);**預設值豁免兩種**:帶 `DefaultConstructorMarker` 參數的合成建構子(建構子預設值)與名字結尾 `$default` 的合成靜態方法(一般函式的預設參數 `fun load(io: CoroutineDispatcher = Dispatchers.IO)`,r1 可行性 F6 實跑誤報;它一樣可注入、跟型錄 CO-1 標準寫法同精神);**不匯入測試類別**:`ClassFileImporter` 加自訂 `ImportOption`,排除路徑含 AGP 的單元測試與儀器測試輸出(`/debugUnitTest/`、`/releaseUnitTest/`、`UnitTest/`、`AndroidTest/` 這類變體目錄)與 Gradle 的 `/test/`,ArchUnit 內建的 `DoNotIncludeTests` 認不認 AGP 路徑由實驗 E5 決定(r1 通才 F3);多模組專案(資料層在 library 模組)時,K 測試放在 app 模組、`importPackages` 照根套件匯入(library 模組的類別以 jar 或類別目錄在測試類別路徑上),實驗 E5 驗;**inline 函式**:使用者自己的 inline 函式裡建 scope,定義處與每個呼叫端各報一筆(r1 可行性 F8 實跑),範本節開頭寫明,library 的 inline 展開進資料層也會被報,寫進天花板;Fragment 用 `lifecycleScope` 那一半位元組碼判不到(看不出接收者是 Fragment 還是 `viewLifecycleOwner`),規則包也沒有規則判它(只有 STATE-5、PERF-4、ARCH-50 三條碰 `lifecycleScope`,都不是這件事),所以本計劃改用 T11 的行為測試接(見 T11 的 API-9 小節),T12 節開頭指過去。另一個允許:呼叫了 `BroadcastReceiver.goAsync()` 的方法裡建 scope 豁免(規則包 `kt-unmanaged-scope-launch` 排除含 `goAsync()` 的函式,K1 用位元組碼判同一件事:同一個方法裡也呼叫了 `goAsync`)。**凍結清單**:`src/test/resources/archunit.properties` 寫 `freeze.store.default.path=src/test/resources/archunit_store`(相對模組目錄,Gradle 測試的工作目錄是模組根;不寫的話清單落在模組根的 `archunit_store`,r1 可行性 F2 實跑)與 `freeze.store.default.allowStoreCreation=false`(官方手冊 8.6.2 的預設就是 false,明寫是為了不讓人改成 true)。只有第一次建清單時臨時打開:範本的 `build.gradle.kts` 片段在 `tasks.withType<Test>` 裡,有 Gradle 屬性 `archunitFreezeInit` 時才把系統屬性 `archunit.freeze.store.default.allowStoreCreation=true` 傳給測試(ArchUnit 設定可被 `archunit.` 開頭的系統屬性蓋過,實驗 E5 驗),指令 `./gradlew :app:testDebugUnitTest -ParchunitFreezeInit --tests '*CoroutineOwnershipTest'`;建好後**把 `archunit_store` 目錄提交進版控**,範本〈怎麼用〉這一組多一步寫明。另加 `freeze.store.default.allowStoreUpdate=false`,`-ParchunitFreezeInit` 同時傳 `allowStoreCreation=true` 與 `allowStoreUpdate=true`:`allowStoreCreation` 只管索引檔 `stored.rules` 整份不見,新加的凍結規則或改了描述的規則不在索引裡時 ArchUnit 會把當下違規靜默存成新的一份、測試綠,`allowStoreUpdate=false` 讓這兩種情況紅 `StoreUpdateFailedException`(代碼審 code-android儀器測試範本 r1 範本丙 F1,驗證紀錄 E13 實跑)。為什麼不常駐 true:r1 可行性 F1 實跑,常駐 true 時刪掉或漏提交清單檔,下一次跑會把當下所有違規(含剛加的新違規)重新凍結、測試綠;設 false 時清單不見就丟 `StoreInitializationFailedException`,測試紅(這個紅是設定錯的大聲失敗,不是斷言紅,範本節開頭寫明)。
     - **T13**:範圍一律 `Konsist.scopeFromProduction()`(只掃正式程式;測試碼裡的 `FakeProfileUiState(var loading: Boolean)` 不判,r1 通才 F6),只用 0.17.3 與 1.0.0-beta.1 都有的 API(`scopeFromProduction()`、`classes(includeNested = true)`、`parents(indirectParents = true)`、`properties(includeNested = false)`、`isVar`、`type.isMutableType`、`type.name`,預實驗 P3);後綴清單是常數(預設只有 `UiState`,專案的狀態類別叫 `State`、`UiModel` 時自己加)。舊違規的容忍:單獨照抄時用一個逐檔常數清單排除(Konsist 沒有凍結);採用目標架構產生器的專案,把這支併進產生的測試檔,改用那支檔已從 `.lumos/arch-legacy.json` 讀好的 `legacyFiles`,不另留常數。三種舊違規容忍的邊界(r1 架構對齊 F2):產生器的 `.lumos/arch-legacy.json` 管目標架構分層與併進去的 T13;T13 單獨用時的常數只管 T13;T12 的 ArchUnit 凍結清單只管 K1、K2——各管各的測試,不互相讀。不判 `java.*` 型別(見〈範圍〉決定 2)。
     - **T4 補**:〈測試:API-30 Ktor 版〉配〈依賴:Ktor〉(引擎用 CIO,避開跟 T4 的 OkHttp 主版本打架;版本照實驗 E8 挑對得上 Kotlin 2.2.21 的),〈好寫法:API-30 區塊內讀完〉、〈壞寫法:API-30 response 帶出區塊〉;壞寫法讀 body 丟取消例外,`runCatching` 後斷言。
2. **型錄改值**(`skills/kotlin-idioms/checks-catalog.md` 通電批次欄的「行為測試或正向約束=」那段):儀器批 25 列改「範本 T6」~「範本 T11」;API-9 改「範本 T12」、UI-39 改「範本 T13」、API-30 改「範本 T4」;CO-5 改「不接(代碼審或真機)」。實驗把某列移出時,同一個提交裡改回「未接(儀器批)」並在驗證紀錄記原因。另改內容:UI-39 的標題、壞寫法、好寫法、後果四欄一起改(見決定 2,附出處)——標題改成「資料類別含 var 或可變集合 → 就地修改後畫面不更新」,壞寫法只留 `var` 與可變集合(`MutableList`、`ArrayList` 等)就地修改,`java.time.*` 這類外部模組型別從壞寫法拿掉、在後果欄寫成「外部模組型別:輕微多餘重組、不判」,好寫法改成「`val` 加唯讀集合、變更用 `copy`;外部模組型別值相同的新實例常配時才考慮 `@Immutable`/`@Stable` 或穩定設定檔」;只改後果欄的話,盲判席讀到的壞寫法欄仍說 `java.time.*` 是壞的、跟 T13 判綠矛盾(r1 通才 F2、依據 F3)。ARCH-56 的出處欄補 dagger.dev 原句。〈輸入與口徑〉那段拿掉「未接(架構測試後續計劃)」「未接(Ktor 範本後續)」兩個值的說明(本批後不該再出現,r1 架構對齊 F4)。
3. **資料測試跟著改期望**(都在 `scripts/test_lumos.py`,共五支):
   - `t_kotlin_catalog_c_rows_batch_resolved`:允許的範本組從 T0–T5 擴成 T0–T13;未接值清單(`_KT_UNWIRED`)拿掉「未接(架構測試後續計劃)」與「未接(Ktor 範本後續)」兩個值(這兩個值本批後不該再出現);寫死的「範本 32 列」改成照新〈範圍〉的列數與各組列編號。允許的值不新增新種類,只是範圍變了。
   - `t_kotlin_test_templates_sections`:**新寫內容檢查**——範本檔有 `## T6`~`## T13` 與〈Android 實驗專案骨架〉,骨架節含 `sdk=34`、`targetSdk = 36` 與 `testInstrumentationRunner`;T6–T13 每一節都有〈紅綠矩陣〉小節;T12 節有指到 T11〈測試:API-9 Fragment 畫面銷毀後〉的那句(小節名字串);T12 節含 `allowStoreCreation=false` 與 `freeze.store.default.path`(現在這支只驗 `template_problems` 與三種改壞,沒有內容檢查;r1 通才 F8)。**代碼審 r1 後改**:這段內容檢查搬進 `t_kotlin_test_templates_content_guards`(`sections` 是 [S1] 型錄自檢);T12 的凍結設定只在 properties 與 kotlin 圍欄裡比對整行(三行設定與建清單的兩行 `systemProperty`),矩陣要有 `StoreUpdateFailedException` 格。
   - `t_kotlin_test_templates_content_guards`:斷言範本組清單的地方從 T0–T5 改成 T0–T13;加 S3 那幾個禁用寫法。
   - `t_kotlin_test_templates_linked`:加 S7 的兩句。
   - `t_kotlin_catalog_instrumented_batch_notes`(新增):驗 S6。
4. **指路**:測試品質標準(`skills/lumos-project-notes/commands/test-quality-standard.md`)〈Android 資料層(Room)的撰寫補充〉一節的「升級」條尾加一句指到範本 T6;〈Android 本機單元測試的驗收標準〉加一句照既有格式的「照抄起手:要 Android 框架的測試(Fragment、LiveData、WorkManager、Compose、Paging)的範本在 `…test-templates.md`(T7–T11 節;…專案形狀與 Robolectric 設定照該檔〈Android 實驗專案骨架〉節)」,`sdk=34` 這類骨架細節不在標準重抄(代碼審 r1 架構對齊 F2);kotlin-idioms `SKILL.md` 開頭那句(已指 `test-templates.md`)不用改。
5. **實驗與驗證紀錄**:照〈實驗〉逐項跑,結果寫進一篇 `Verification/` 驗證紀錄(`plan_refs` 連回這篇)。
6. **前半計劃同步**(r1 依據 F2):前半 [[Projects/Android行為測試範本與架構測試_計劃]] 的 S2 與本計劃 S1 綁同一支 `t_kotlin_catalog_c_rows_batch_resolved`、期望相反;實作的同一個提交裡,前半 S2 句尾加「(已被 [[Projects/Android儀器測試範本與架構測試_計劃]] S1 取代,那支測試的期望以後半為準)」,前半 `REVISIT:2027-01-31 開「架構測試後續計劃」` 那行刪掉、前半〈審計修正紀錄〉記一行「由後半計劃結案」。
7. **寫回家**:[[Systems/kotlin規則包]] 記範本檔多了 T6–T13 與 Android 骨架、型錄 UI-39 後果改寫與 CO-5 改歸;[[Systems/test-quality-cli]] 記指路兩句。

決定(本計劃自答,附出處):

1. **K1–K3 用位元組碼與宣告判,不用字面**:設計審 r1 打穿的四種寫法全是「拿文字比對判語意」造成的。先查世界:ArchUnit 官方寫明它「analyzing given Java bytecode, importing all classes into a Java code structure」,呼叫與欄位存取是解析後的完整型別,不受 import 寫法、註解、字串影響;Konsist 讀原始碼宣告,有父型別、`isVar`、`isMutableType`,但看不進函式本體的運算式(只有 `text`)。所以函式本體裡的事(K1、K2)交給 ArchUnit,宣告層的事(K3)交給 Konsist;預實驗 P3 證過兩邊各自把 r1 的漏報與誤報樣本判對。代價:消費專案多一個測試依賴 ArchUnit(決策 d1 裁定照這樣做)。**這是翻案(決策 d3,使用者 2026-11-06 裁)**:[[Projects/Android的MVVM與DDD目標架構範本_計劃]] 挑目標架構分層規則時否決過 ArchUnit(「屬 Java 生態,沒查到在 Kotlin 編譯出的類別上的實證,不選」)。翻案理由:那次要判的是分層與宣告,Konsist 夠用;這次要判的是函式本體裡的呼叫,Konsist 看不進去;「沒有 Kotlin 類別上的實證」已由預實驗 P3 與 r1 可行性席實跑補上。分工:ArchUnit 只管看得進函式本體的兩條(K1 協程歸屬、K2 寫死 dispatcher);目標架構分層(`lumos arch-template android` 產生的測試)與 K3 照舊用 Konsist。
2. **K3 不判 `java.*` 型別、UI-39 後果改寫**:官方強跳過頁「Strong Skipping is enabled by default in Kotlin 2.0.20」「Unstable parameters are compared using instance equality (===)」——不穩定的參數不再讓畫面「不可跳過」,而是用同一個實例比。`java.time.Instant` 這類外部模組型別:官方同一頁寫「Add `@Stable` or `@Immutable` when the compiler can't infer stability (such as classes from non-Compose modules) and new instances with identical values are frequently allocated」——值相同的新實例會被 `===` 判成不同、多重組一次,是**輕微多餘重組**,不是錯,所以 K3 不判(型錄後果欄寫明「輕微多餘重組、不判」)。真正的錯是 `var` 或可變集合**就地改**:實例沒變,`===` 判相同,畫面被跳過、不更新——這句是從「不穩定參數用 `===` 比」推出來的,官方頁沒有逐字這樣寫(依據來源標推論)。型錄 UI-39 標題、壞寫法、好寫法、後果四欄一起改(〈做法〉2),Kotlin 2.0.20 之前的專案照舊說法。
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

### K 測試、規則包、detekt 的分工

| 型錄列 | 規則包(ast-grep) | detekt | K 測試(本批) |
|---|---|---|---|
| API-9 | `kt-unmanaged-scope-launch`、`kt-compose-globalscope-in-composable`:語法樹判整支檔,新增告警閘只報這次新增的行;含 `goAsync()` 的函式豁免;Fragment 用 `lifecycleScope` 沒有規則 | `GlobalCoroutineUsage`(不要型別資訊,只認 import 後的 `GlobalScope.launch/async`) | T12 K1:整個專案、位元組碼判、舊違規凍結、`goAsync` 同豁免;Fragment `lifecycleScope` 那半由 T11 的行為測試接 |
| CO-1 | `kt-hardcoded-dispatchers-io`(訊息以 `[CO-1]` 開頭):名字結尾 Repository/DataSource 的類別;新增告警閘只報新增的行 | `InjectDispatcher`(要型別資訊,CI 的 Gradle 那步才響) | T12 K2:資料層套件、整個專案、位元組碼判、DI 模組豁免 |
| UI-39 | 沒有直接對應的規則;同形的 `kt-uistate-mutable-field` 訊息以 `[PERF-30]` 開頭,掛在型錄 PERF-30(「data class 帶 var 或可變集合欄位」,級 A+B,不是 C 列、不在本批範圍) | 無 | T13 K3:整個專案、宣告判、含間接父型別、舊檔清單排除 |

改 API-9、CO-1 的標準寫法時,規則包、detekt、T12 三邊一起看;改 UI-39 時要連 PERF-30 與它的規則一起看(規則訊息掛的是 PERF-30,不會因 UI-39 改了而被看到),T13 節開頭寫這一句。規則包(經新增告警閘)與 detekt(推送前只給改到的檔時)管「這次寫的」,K 測試管「整個專案現在有沒有」,而且跑在專案自己的單元測試裡、不靠 lumos 有沒有裝。

## 實驗(每個機制都跑一遍,找漏洞)

照使用者第二要點,實作時逐項跑;結果不符預期就照第一要點先查官方與業界做法再改,寫進〈依據來源〉與審計修正紀錄。Android 實驗專案從 lab `git clone` 到會談暫存區;模擬器 `kds_bench` 無視窗開,實驗完自己關;Gradle 8.13、JDK 17。

- **E1 紅要是斷言紅**:每組〈測試〉列的每個紅,Robolectric 與 JVM 讀 JUnit XML 的型別、儀器測試讀 XML 第一行與 JUnit 斷言框,用 `assertion_failure` 判,全部要是斷言失敗。已知會是例外紅、範本要先改寫的:T6 少 Migration(`IllegalStateException`)、SQL 錯與 DATA-21(`SQLiteException`)、T7 DATA-58(`IllegalStateException: Attempt to collect twice`)、T9 STATE-23(存不進 Bundle)、STATE-12(`ComposeTimeoutException`)、無障礙兩列(`AccessibilityViewCheckException`,預實驗 P1 已證 `runCatching` 後是斷言紅)、T10(`NoLeakAssertionFailedError`,記下它的實際型別與父類別)、T11 ARCH-31 與 ARCH-56(`IllegalStateException`)、T4 API-30(取消例外)、T12 與 T13(ArchUnit 的 `AssertionError`、Konsist 的 `KoAssertionFailedException`——後者型別名收證不認,T13 改成收集違規再 `assertEquals(emptyList(), 違規)`)。
- **E2 每格只紅點名的那支**:同前半;小節裡每支 `@Test` 都在矩陣出現。
- **E3 時序穩定**:JVM 與 Robolectric 的每格重跑 20 次、模擬器的每格重跑 5 次(一次要裝 APK,約一分鐘),結果要每次一樣;不穩的那支改寫或拿掉,型錄那列改回「未接(儀器批)」並寫原因。T9 有動畫與時鐘的格子(TEST-29、STATE-12)、T11 STATE-17(Looper 排程)特別看。
- **E4 跑在哪的對照**:Robolectric 用實作當天 Maven Central 的最新穩定版(2026-11-06 是 4.17),先重跑預實驗 P1、P2 確認結論沒變;T7 DATA-58、T8、T9 九列、T11 在 Robolectric 跑完矩陣後,再在模擬器跑一次同一份(放 `androidTest`),結果要一樣;不一樣的照官方說法改成只在模擬器跑,節開頭寫明。T9 無障礙兩列反過來在 Robolectric 跑一次,記下它照綠(重做預實驗 P1,證明「只在模擬器」那句)。
- **E5 K1、K2 在 Android 模組**:lab 複本的 `src/test` 放 T12,`ClassFileImporter` 匯入 app 的套件(Android 本機單元測試的類別路徑有編譯後的 app 類別),預實驗 P3 的樣本搬進 `src/main` 跑一次,結果要一樣;另加 Android 才有的樣本:`viewModelScope.launch`(綠)、Fragment 裡 `lifecycleScope.launch`(T12 綠——那半由 T11 的 API-9 小節接)、`@HiltAndroidApp class App : Application()` 裡建 `appScope`(綠)、`BroadcastReceiver.onReceive` 裡 `goAsync()` 後建 scope(綠)、同一個 Receiver 沒有 `goAsync()` 就建 scope(紅)、`class App : Application` 裡 `launch { CoroutineScope(…) }`(suspend lambda 編成 `App$onCreate$1`,綠)、`@Module abstract class AppModule { @Binds …; companion object { @Provides fun appScope() = CoroutineScope(SupervisorJob() + Dispatchers.Default) } }`(綠)、資料層 `suspend fun load(io: CoroutineDispatcher = Dispatchers.IO)`(`load$default`,綠)、`src/test` 裡的 `CoroutineScope(UnconfinedTestDispatcher())` 與 `withContext(Dispatchers.Default.limitedParallelism(1))`(不被匯入,綠;另跑一次只用 ArchUnit 內建 `DoNotIncludeTests`,記下它認不認 AGP 的 `debugUnitTest` 路徑)、資料層放在另一個 library 模組的樣本(K2 仍判得到)。凍結五步(預期照 r1 可行性 F1、F2 實跑):①沒有清單檔、`allowStoreCreation=false` → `StoreInitializationFailedException` 紅;②帶 `-ParchunitFreezeInit` 跑 → 清單檔建在 `src/test/resources/archunit_store`、綠;③不帶屬性、加一個新違規 → 斷言紅;④修掉一個舊違規 → 紅 `StoreUpdateFailedException`,帶 `-ParchunitFreezeInit` 再跑一次綠、清單縮小(代碼審 r1 後加 `allowStoreUpdate=false` 的結果;原本是「綠、清單自動縮小」);⑤刪掉清單檔、不帶屬性 → 回到①的紅(不會全綠)。另跑一次「常駐 true」的對照,記下刪檔後全綠且新違規一起被凍結(證明為什麼不常駐)。
- **E6 K3 在 Android 模組**:同上放 T13,樣本加 `@Immutable data class XUiState(var a: Int)`(紅:標註不改變就地修改的壞處)、`typealias Items = MutableList<String>` 的屬性、泛型 `List<MutableList<String>>`(記下 `isMutableType` 只看最外層的話是天花板)、`data object Loading : HomeUiState`(物件沒有屬性,不影響)、`src/test` 裡的 `class FakeProfileUiState(var loading: Boolean)` 與 `data class TestUiState(val xs: ArrayList<String>)`(不在正式程式範圍,綠;另用 `scopeFromProject()` 跑一次記下它會紅,證明要指定範圍)、加了後綴常數 `State` 後 `data class ProfileState(var name: String)` 轉紅;Konsist 0.17.3 與 1.0.0-beta.1 各跑一次,結果要一樣;沒有 gradlew 的資料夾 Konsist 例外紅(調研實測),骨架寫明。
- **E7 每道檢查各改壞一次**:T12 的各個豁免與條件(允許類別、往外找最外層類別、帶 `DefaultConstructorMarker` 的合成建構子、`$default` 合成方法、`goAsync`、排除測試類別的 `ImportOption`)、T13 的「間接父型別」條件與 `scopeFromProduction` 範圍,各拿掉一次,對應的好樣本要轉紅(預實驗 P3 已在純 JVM 做過一次,這裡在 Android 模組重做)。
- **E8 Ktor 版本**:Ktor client(CIO 引擎)在 Kotlin 2.2.21 編得過的最新版(前半 kotlinx-serialization 1.12.0 就因綁 Kotlin 2.4 編不過);跟 T4 的 OkHttp 4 與 5 兩套依賴並存時都要能跑;好寫法綠、壞寫法斷言紅。
- **E9 ARCH-56 的 Hilt 設定**:lab 複本加 Hilt 外掛與 KSP、`hilt-android-testing`,Robolectric 用 `@HiltAndroidTest` 與 `HiltTestApplication`,壞寫法(宿主沒標)要在 `runCatching` 裡丟 `IllegalStateException`、好寫法綠;Robolectric 跑不起來就改在模擬器跑;兩邊都跑不起來,ARCH-56 照〈做法〉2 改回「未接(儀器批)」(跟其他實驗移出的列同一個值,S1 的計數照算),驗證紀錄記原因並註明「第一次開那個畫面就崩,端到端驗收的 flow 走到就紅」。
- **E10 Room 兩個主版本與結構檔**:T6 在〈依賴:Room 2〉(2.8.5)與〈依賴:Room 3〉(3.0.3)各跑一次矩陣,結果要一樣(room-guard 2026-10-29 已用 Room 3.0.3 的實驗專案實跑過,見 [[Systems/room-guard]] 的 PITFALL 行);結構檔沒加進 `androidTest` assets 時 `MigrationTestHelper` 的錯誤訊息記進範本的坑。
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
- **凍結清單被當成「已處理」**:`FreezingArchRule` 的清單檔讓舊違規永遠綠;範本節開頭寫明清單裡的違規只准變少、帶 `-ParchunitFreezeInit` 那次多出來的要在代碼審說明;改了規則描述時舊描述的清單條目與檔案一起刪(新描述另存、舊的不會自己消失,驗證紀錄 E13),帶屬性那次的清單差異在代碼審特別看新增的違規;不機械擋(消費專案的事,本 repo 驗不到)。
- **凍結清單漏提交或被刪變假綠**:`allowStoreCreation` 常駐 true 時會發生(r1 可行性 F1 實跑);範本預設 false、只在初次建清單時用 Gradle 屬性打開,並教使用者提交 `archunit_store`。
- **新規則或改描述被靜默凍結**:`allowStoreCreation=false` 只擋索引檔整份不見;加凍結規則、改規則描述時,沒設 `allowStoreUpdate=false` 會把當下違規存成新的一份、測試綠(驗證紀錄 E13 實跑);範本設 false,代價是修掉舊違規也要帶屬性跑一次,清單每次變動都在版控裡。
- **效能**:型錄自檢多讀的只有範本檔變長(多八節),判法不變。
- **併發**:實驗在會談暫存區;本 repo 只改 Markdown(範本檔、型錄、測試品質標準、前半計劃)與五支資料測試。
- **守衛面**:型錄自檢與資料測試在本 repo CI 跑;不改任何推送閘或收證判定。
- **舊否決對照**:見審計修正紀錄第一行。
- 前端:不改任何前端檔;本計劃的「畫面」都是 Android Compose。
- 已排除:金流:範本與實驗只用假資料。
- 已排除:對外送出:MockWebServer 與 T4 Ktor 小節用的 JDK 內建 HttpServer 都只聽本機回環位址(HttpServer 綁 InetAddress.getLoopbackAddress());實驗只從 Maven Central 與 Google Maven 下載依賴;模擬器不登入任何帳號。
- 已排除:不可逆:新增 Markdown 節、改型錄文字與一支測試的期望,退提交即回原狀。

REVISIT:2027-02-06 範本檔 T6–T13 各組〈依賴〉的版本(Room、Paging、WorkManager、Compose BOM、LeakCanary、Robolectric、ArchUnit、Konsist、Ktor)與 Maven Central、Google Maven 最新版對一次,有大版本差就重跑那組的紅綠矩陣
REVISIT:2027-03-31 Konsist 出 1.0.0 正式版時,重跑實驗 E6(T13 兩版共通),並開 [[Systems/android-arch-template]] 的換版工作(產生器資料檔三處 `resideInPackage`、技能文件版本句、`_arch_tpl_konsist_test` 對新版重核);到期還沒出正式版就人裁要不要翻 d2、改換 beta
REVISIT:2027-03-31 Robolectric 的 Android 15 以上要 JDK 21:查消費專案與本機 JDK,都到 21 就拿掉骨架的 `sdk=34` 那行並重跑 T7–T11
REVISIT:2027-02-06 Robolectric 出 4.17 之後的穩定版(或 4.18 正式版)時,重跑預實驗 P1(無障礙在 Robolectric 不報)與 P2(JDK 17 對 SDK 36),結論變了就改範本骨架與〈依賴〉

## 驗收條款

- [S1] 當讀型錄 C 列時,每列通電批次的「行為測試或正向約束=」值應是「範本 T0」到「範本 T13」、「未接(儀器批)」、「不接(代碼審或真機)」之一,應不再出現「未接(架構測試後續計劃)」與「未接(Ktor 範本後續)」;各值的列數與各範本組的列應等於本計劃〈範圍〉〈做〉表(實驗移出的列照〈做法〉2 計入「未接(儀器批)」),CO-5 應是「不接(代碼審或真機)」。 [test:t_kotlin_catalog_c_rows_batch_resolved]
- [S2] 當型錄自檢讀真的型錄與範本檔時,應零問題;範本檔應有 `## T6` 到 `## T13` 八節與〈Android 實驗專案骨架〉一節,骨架節應含 `sdk=34`、`targetSdk = 36` 與 `testInstrumentationRunner`;T6–T13 每節應有〈紅綠矩陣〉小節;T12 節應含指到 T11〈測試:API-9 Fragment 畫面銷毀後〉的字串;T12 的 properties 圍欄應有整行 `freeze.store.default.path=src/test/resources/archunit_store`、`freeze.store.default.allowStoreCreation=false`、`freeze.store.default.allowStoreUpdate=false`,建清單的 kotlin 圍欄應有傳 `allowStoreCreation` 與 `allowStoreUpdate` 為 true 的兩行,T12 矩陣應有 `StoreUpdateFailedException` 的格;只改散文、圍欄照舊時應零問題。 [test:t_kotlin_test_templates_content_guards]
- [S3] 當讀範本檔 T6–T13 的〈測試〉小節時,應不出現 `DetectLeaksAfterTestSuccess`、`InstantTaskExecutorRule` 與不帶 `runCatching` 的 `LeakAssertions.assertNoLeaks()`;T13 的〈測試〉應不呼叫 Konsist 的 `assertTrue`/`assertFalse`(改收集違規再比)。 [test:t_kotlin_test_templates_content_guards]
- [S4] 當在 Android 實驗專案照骨架逐格跑時,每格每支測試的結果應等於矩陣,〈測試〉列的每個紅經 `assertion_failure` 判定應是斷言失敗;JVM 與 Robolectric 的格子重跑 20 次、模擬器的格子重跑 5 次結果應不變;E4 對照兩邊結果應一致或已照官方改成只在模擬器;結果寫進驗證紀錄。 [manual:會談暫存區的 lab 複本逐格跑 Gradle 與模擬器,記每格結果、失敗型別與重跑次數]
- [S5] 當 T12、T13 在 Android 實驗專案對〈實驗〉E5、E6 列的樣本跑時,壞樣本應紅、好樣本應綠,拿掉每個豁免或條件後對應的好樣本應轉紅,凍結清單應照 E5 的五步變化(清單不見時紅、不是全綠),加一支凍結規則或改規則描述時應紅 `StoreUpdateFailedException`、不是靜默凍結成綠(E13);T13 在 Konsist 0.17.3 與 1.0.0-beta.1 的結果應相同。 [manual:會談暫存區的 lab 複本跑 E5、E6、E7,結果寫進驗證紀錄]
- [S6] 當讀型錄 UI-39 列時,「後果」欄應提到強跳過模式與實例相等比較、外部模組型別「輕微多餘重組、不判」,標題與壞寫法欄應不再出現「外部模組型別」與 `java.time`,出處欄應有強跳過頁網址;讀型錄〈輸入與口徑〉時應不再出現「未接(架構測試後續計劃)」與「未接(Ktor 範本後續)」;讀 ARCH-56 列時出處欄應有 dagger.dev 的網址。 [test:t_kotlin_catalog_instrumented_batch_notes](新增)
- [S7] 當讀測試品質標準時,〈Android 資料層(Room)的撰寫補充〉的升級條應提到範本 T6,〈Android 本機單元測試的驗收標準〉應有一句「照抄起手:…(T7–T11 節…)」指到範本〈Android 實驗專案骨架〉,那句應不重抄 `sdk=34`。 [test:t_kotlin_test_templates_linked]

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
| S5 | `class App : Application` 裡 `launch { CoroutineScope(SupervisorJob()) }` | T12 K1 綠(往外找到 `App`) | r1 可行性 F5 實跑;通才 F4 |
| S5 | 資料層 `suspend fun load(io: CoroutineDispatcher = Dispatchers.IO)` | T12 K2 綠(`load$default` 豁免) | r1 可行性 F6 實跑;型錄 CO-1 標準寫法 |
| S5 | 刪掉 `archunit_store`、不帶 `-ParchunitFreezeInit` | T12 紅(`StoreInitializationFailedException`),不是全綠 | ArchUnit 手冊 8.6.2 `allowStoreCreation` 預設 false;r1 可行性 F1 實跑 |
| S5 | 清單提交後加一支 `FreezingArchRule` 包的 `@Test`,或改既有規則的 `ArchCondition` 描述,不帶 `-ParchunitFreezeInit` | 那支紅 `StoreUpdateFailedException`,不是靜默凍結成綠 | ArchUnit 手冊 8.6.2 `allowStoreUpdate`;代碼審 code-android儀器測試範本 r1 範本丙 F1;驗證紀錄 E13 實跑 |
| S5 | `src/test` 裡的 `class FakeProfileUiState(var loading: Boolean)` | T13 K3 綠(不在正式程式範圍) | r1 通才 F6;Konsist `scopeFromProduction` |
| S4 | T8〈測試〉×〈壞寫法:DATA-38 迴圈裡吞取消〉 | 斷言紅(`markDone` 1 次),10 秒內結束、不卡死 | r1 可行性 F3 實跑;官方 CoroutineWorker 頁「由框架自動取消」 |
| S4 | T11〈測試:API-9 Fragment 畫面銷毀後〉×〈壞寫法:API-9 Fragment 自己的 lifecycleScope〉 | 斷言紅(銷毀後被呼叫 1 次) | r1 可行性 F4 實跑;官方協程例外處理頁 |
| S6 | 型錄 UI-39 後果欄 | 提到強跳過與 `===`,外部模組型別寫「輕微多餘重組、不判」 | developer.android.com 強跳過頁 |
| S6 | 型錄 UI-39 壞寫法欄 | 不含 `java.time` | 本計劃〈範圍〉決定 2;r1 通才 F2 |
| S6 | 型錄 ARCH-56 出處欄 | 含 `https://dagger.dev/hilt/android-entry-point` | 本計劃〈範圍〉決定 4;dagger.dev 原句 |
| S7 | 測試品質標準〈Android 資料層(Room)的撰寫補充〉升級條 | 含「範本 T6」 | 本計劃〈做法〉4 指路 |
| S7 | 測試品質標準〈Android 本機單元測試的驗收標準〉 | 有一句「照抄起手:…(T7–T11 節…)」提到〈Android 實驗專案骨架〉,不含 `sdk=34` | 本計劃〈做法〉4;代碼審 r1 架構對齊 F2 |

## 回退

退回本計劃的提交即可,逐項是:範本檔拿掉 `## T6`~`## T13` 八節、〈Android 實驗專案骨架〉一節與 T4 的 API-30 小節;型錄 29 列的「行為測試或正向約束=」值改回前半的值(儀器批 25 列「未接(儀器批)」、API-9 與 CO-5 與 UI-39「未接(架構測試後續計劃)」、API-30「未接(Ktor 範本後續)」),UI-39 後果欄與 ARCH-56 出處欄改回;`t_kotlin_catalog_c_rows_batch_resolved` 的期望改回、`t_kotlin_test_templates_sections`、`t_kotlin_test_templates_content_guards`、`t_kotlin_test_templates_linked` 拿掉這次加的檢查、刪這次新增的 `t_kotlin_catalog_instrumented_batch_notes`;測試品質標準的兩句指路拿掉;UI-39 的標題、壞寫法、好寫法三欄與〈輸入與口徑〉那兩個值的說明改回;前半計劃 S2 句尾的「已被取代」拿掉、`REVISIT:2027-01-31` 那行與它〈審計修正紀錄〉的結案行改回;[[Systems/kotlin規則包]] 與 [[Systems/test-quality-cli]] 這次加的行拿掉;驗證紀錄保留、狀態改成作廢並註明計劃已退回。不碰任何帳本、推送閘或 `check.py`。

## 天花板

1. 範本的紅綠只在實驗專案與模擬器 `kds_bench`(API 34)驗過;消費專案照抄改名後寫錯,本 repo 看不出來(CI 不跑 Gradle、沒有模擬器)。
2. 儀器測試要開模擬器,消費專案不會在推送前跑;它們接的是專案自己的 CI 或端到端驗收,本批不把它們接進任何閘。
3. 無障礙兩列在 Robolectric 不報(預實驗 P1),只在模擬器或真機抓得到;對比檢查要實際算繪。
4. K1 判不到 Fragment 用 `lifecycleScope` 還是 `viewLifecycleOwner.lifecycleScope`(位元組碼看不出接收者);那半只有 T11 的行為測試接,專案沒照範本替每個 Fragment 寫就沒接上,規則包沒有對應規則。
5. K1、K2 的「允許建 scope 的類別」「資料層套件」是範本常數,專案沒改就照範本預設判;凍結清單讓舊違規永遠綠。inline 函式裡建 scope 會在每個呼叫端各報一筆,library 模組的 inline 展開進資料層也會被報(r1 可行性 F8)。
10. K3 只判名字(或父型別名字)結尾在後綴常數裡的類別;命名慣例以外的狀態類別(`ProfileState`、`ScreenContract.State`,沒加後綴時)不判,型錄 UI-39 寫「範本 T13」不代表全部狀態類別都接上了(r1 通才 F7)。
6. K3 的 `isMutableType` 對泛型參數裡的可變型別、型別別名判不判得到看實驗 E6;判不到的寫進範本節開頭。K3 不判外部模組的類別(Konsist 只讀本專案原始碼)。
7. DATA-38 只涵蓋 CoroutineWorker;一般 `Worker` 的 `isStopped` 從測試觸發不了。
8. DATA-65 的「後寫贏」與 API-4 一樣是業務決定,選錯照綠。
9. CO-5 沒有自動測法,只剩代碼審、盲判與真機 StrictMode。

## 依據來源

每個機制一行:機制|依據|網址或實測|在哪看得到。標「調研開頁」的是第五批調研時開頁核對;「本次開頁」是寫這份計劃時用 WebFetch 開的;「預實驗」見〈前提〉。

- K1、K2 用位元組碼|「It does so by analyzing given Java bytecode, importing all classes into a Java code structure」;ArchUnit 現行 1.5.1|https://www.archunit.org/userguide/html/000_Index.html(本次開頁);預實驗 P3|範本 T12、決定 1
- 舊違規凍結|ArchUnit 使用手冊的 `FreezingArchRule`(既有專案只擋新違規);手冊 8.6.2 `freeze.store.default.allowStoreCreation` 預設 false、要設 true 才能建新清單;`freeze.store.default.path` 設清單位置;常駐 true 時刪清單全綠、不設路徑時清單落在模組根(r1 可行性 F1、F2 實跑)|https://www.archunit.org/userguide/html/000_Index.html ;r1 可行性席報告|範本 T12、E5
- 凍結清單擋新規則與改描述|手冊 8.6.2「can be set to false to forbid updates of the violations stored for frozen rules」(`freeze.store.default.allowStoreUpdate`,預設 true);手冊沒寫「索引在、規則是新的」怎麼辦,ArchUnit 1.5.1 `FreezingArchRule.evaluate` 對不在索引裡的規則直接存檔回成功(代碼審 r1 範本丙席讀原始碼);實測預設設定下新規則、改描述都靜默凍結成綠,設 false 後紅 `StoreUpdateFailedException`,建清單那一步要同時打開更新|https://www.archunit.org/userguide/html/000_Index.html(2026-11-06 開頁);驗證紀錄 [[Verification/2026-11-06_Android儀器測試範本與架構測試實跑]] E13|範本 T12〈依賴〉與矩陣末四格、S2、S5
- 判允許類別看最外層、預設值兩種豁免|Kotlin 把 suspend lambda 編成 `X$f$1`、companion 編成 `X$Companion`、函式預設參數編成 `f$default`;r1 可行性 F5、F6 實跑誤報|`governance/review-reports/android儀器測試範本與架構測試/r1-可行性-sonnet.md`|範本 T12、E5、E7
- 協程裡的例外測試本體接不到|官方協程例外處理頁(launch 的例外交給 `CoroutineExceptionHandler`);r1 可行性 F4 實跑 `runCatching` 沒接到|https://kotlinlang.org/docs/exception-handling.html ;r1 可行性席報告|範本 T11 API-9 小節、T8
- 翻案用 ArchUnit|舊否決「ArchUnit 加 jMolecules 規則最完整但屬 Java 生態,沒查到在 Kotlin 編譯出的類別上的實證,不選」;使用者 2026-11-06 原話「A」|[[Projects/Android的MVVM與DDD目標架構範本_計劃]] PRIOR-ART;決策 d3|決定 1
- K3 用宣告|Konsist 1.0.0-beta.1 與 0.17.3 都有 `parents(indirectParents)`、`properties`、`isVar`、`isMutableType`|預實驗 P3(兩版編譯並實跑)|範本 T13
- K3 不判 java.*、UI-39 四欄改寫|「Strong Skipping is enabled by default in Kotlin 2.0.20」「Unstable parameters are compared using instance equality (===)」「Stable parameters are compared using object equality」「Add `@Stable` or `@Immutable` when the compiler can't infer stability (such as classes from non-Compose modules) and new instances with identical values are frequently allocated」;「就地改→畫面被跳過」是從 `===` 推出的,頁面沒逐字寫(推論)|https://developer.android.com/develop/ui/compose/performance/stability/strongskipping(本次開頁)|決定 2、型錄 UI-39
- K2 注入的理由|「Using dependency injection to provide dispatchers to your classes makes it easy to replace the real dispatchers in tests」|https://developer.android.com/kotlin/coroutines/test(調研開頁)|範本 T12
- detekt 對照|`InjectDispatcher`「Always use dependency injection to inject dispatchers for easier testing」、Requires type resolution、預設開;`GlobalCoroutineUsage`「Report usages of GlobalScope.launch and GlobalScope.async」、預設關|https://detekt.dev/docs/rules/coroutines/(本次開頁)|〈K 測試、規則包、detekt 的分工〉
- 規則包同形三條|`kt-unmanaged-scope-launch`、`kt-hardcoded-dispatchers-io`、`kt-uistate-mutable-field` 的現行判法|[[Systems/kotlin規則包]](讀規則檔)|分工表
- CO-5 不接|r1 通才 F6「完全沒有 Dispatchers 字樣,K2 綠」;預實驗 P3 `Thread.sleep` 樣本綠|`governance/review-reports/android行為測試範本與架構測試/r1-通才-sonnet.md`;預實驗 P3|決定 3
- Konsist 換版|發行說明「the final release before 1.0.0」「the API freeze candidate for 1.0.0」「Konsist targets JVM 11 again」「publishes kotlin-stdlib 2.0.21」「filter files before parsing」;安裝頁 `testImplementation("com.lemonappdev:konsist:1.0.0-beta.1")`;舊名 `resideInPackage` 編譯失敗(發行說明現版沒寫這個改名)|https://github.com/LemonAppDev/konsist/releases ;https://docs.konsist.lemonappdev.com/getting-started/getting-started/add-konsist-dependency(本次開頁);預實驗 P3|〈不做〉、Q2
- Konsist 要 gradlew|沒有 gradlew 時 `KoInternalException: Project directory not found`|調研 2026-11-06 實驗紀錄|範本 T13、E6
- K4 依據|「So before adding @AndroidEntryPoint to a fragment, the activity must be annotated as well.」「as a general rule, Hilt types need to be attached to other Hilt types to work」|https://dagger.dev/hilt/android-entry-point(本次開頁)|決定 4、型錄 ARCH-56、範本 T11
- K5 已由 room-guard 擋|升級測試要提到 `MigrationTestHelper` 與類別簡名並帶新版本號或跑完全部升級|[[Projects/Room資料庫測試守衛_計劃]] 條款 S6、S7|決定 5
- API-30 依據|「The response object should not be accessed outside of block as it will be canceled upon block completion」;不帶區塊的 `execute()`「the response body is downloaded fully into memory, and the connection is released」|https://api.ktor.io/ktor-client-core/io.ktor.client.statement/-http-statement/execute.html(本次開頁)|決定 6、範本 T4
- T6 Room 遷移|「an incorrectly defined migration can cause your app to crash」「you should include a test that covers all migrations」;缺路徑「an IllegalStateException occurs」;現版範例已是 `androidx.room3:room3-testing:3.0.3`(r1 依據 F1)|https://developer.android.com/training/data-storage/room/migrating-db-versions(調研開頁;r1 依據席重開)|範本 T6
- T6 Room 3 穩定、兩份依賴|官方版本頁 3.0.0(2026-07-01)、穩定 3.0.3(2026-09-09);Room 2 現行 2.8.5;`MigrationTestHelper` 參數順序 `instrumentation, file, driver, databaseClass`|https://developer.android.com/jetpack/androidx/releases/room3 ;https://developer.android.com/reference/kotlin/androidx/room/testing/MigrationTestHelper(r1 依據、可行性席開頁)|範本 T6〈依賴:Room 2〉〈依賴:Room 3〉
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
- Robolectric 要釘 sdk=34|Robolectric 4.16 在 JDK 17、targetSdk 36 時例外紅「Android SDK 36 requires Java 21 (have Java 17)」;不設 targetSdk 時用 minSdk 跑(r1 可行性 F7);Maven Central 現有 4.16.1、4.17(r1 依據 F5),4.17 待重跑|預實驗 P2;r1 可行性、依據席報告|範本〈Android 實驗專案骨架〉、Robolectric 組〈依賴〉、E4、REVISIT
- ARCH-3 要關自動時鐘|時鐘自動推進時轉場立刻跑完,`dropUnlessResumed` 的好寫法也多一頁(r1 依據 F6 讀文件推論,E1、E2 實證)|https://developer.android.com/develop/ui/compose/testing/synchronization|範本 T9 ARCH-3
- 儀器測試的紅要是斷言紅|AGP 儀器測試 XML 沒有型別,收證看第一行與 JUnit 斷言框;預實驗 P1 的 `runCatching` 加 `assertNull` 第一行是 `java.lang.AssertionError`|`scripts/test_quality.py` 的 `assertion_failure`;預實驗 P1|實驗 E1
- 範本放法與自檢|沿用前半的範本檔、`template_problems`、通電批次欄|[[Projects/Android行為測試範本與架構測試_計劃]]〈做法〉1–3|〈做法〉1–3
- 實作時 AGP 8.13.2 的版本天花板|Compose 1.12(BOM 2026.08 起)、lifecycle 2.11、navigation 2.10 的 AAR 要 compileSdk 37 與 AGP 9.1,`checkDebugAarMetadata` 擋;Hilt 2.59 起 Gradle 外掛要 AGP 9.0(「The Hilt Android Gradle plugin is only compatible with Android Gradle plugin (AGP) version 9.0.0 or higher」),改用 2.58|2026-11-06 實作實跑|範本〈Android 實驗專案骨架〉、T11〈依賴:Hilt〉
- Konsist 找專案根的條件|Konsist 0.17.3 的 `GradleProjectRootDirResolver` 認 `gradlew`、`gradlew.bat`、`gradle/wrapper/gradle-wrapper.jar`/`.properties`,另有 Maven wrapper 與 `.git` 兩種解析器;只拿掉 `gradlew` 照綠,三樣都拿掉才 `KoInternalException`(調研稿「沒有 gradlew 就例外」不精確)|javap 讀 konsist-0.17.3.jar;實驗 E6|範本 T13、骨架
- Compose 無障礙檢查的對比門檻|`enableAccessibilityChecks()` 不帶參數時只對 ERROR 丟例外,ATF 的文字對比報 WARNING(白底 `#CCCCCC` 對比 1.61 照綠);傳 `AccessibilityValidator().setRunChecksFromRootView(true).setThrowExceptionFor(WARNING)` 才紅;API 在 `androidx.compose.ui.test.junit4.accessibility` 套件|2026-11-06 模擬器實跑;javap 讀 ui-test-junit4-accessibility 1.11.4|範本 T9〈測試:無障礙〉
- LeakCanary 要裝在 App 裡|「You still need to include the LeakCanary artifact in your app」`debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.14'`;只加 instrumentation 那一行時壞寫法照綠;`NoLeakAssertionFailedError` 父類別是 `java.lang.AssertionError`(實驗 E1、E12)|https://square.github.io/leakcanary/ui-tests/(本次開頁);模擬器實跑|範本 T10
- Room Gradle 外掛自己接 androidTest assets|外掛的 `AndroidPluginIntegration` 把結構檔目錄加進 `AndroidTest` 的 assets(`copyRoomSchemasToAndroidTestAssets…` 任務),手動 `srcDir` 不必要;升版後第一次建置時最新版 json 還沒進 assets,`runMigrationsAndValidate` 丟 `FileNotFoundException … Missing file: AppDb/3.json`,第二次建置才綠|javap 讀 room-gradle-plugin 2.8.5、room3-gradle-plugin 3.0.3;實驗 E10|範本 T6
- Room 3 與 Room 2 的程式差異|Room 3 的 `Migration.migrate(SQLiteConnection)`、`MigrationTestHelper.createDatabase`、`runMigrationsAndValidate` 都是 suspend;外掛 id `androidx.room3`、擴充 `room3 { }`|javap 讀 room3-runtime/room3-testing 3.0.3;實驗 E10|範本 T6
- 儀器報告截斷|AGP 儀器報告的失敗文字截在 64KB:DATA-21 的 `SQLiteException` 訊息含 4 萬個 `?`,斷言框被截掉、`assertion_failure` 判不到;訊息只帶例外類別名|2026-11-06 模擬器實跑|範本 T6 DATA-21、T10
- Hilt 測試類別要有具名套件|預設套件的 `@HiltAndroidTest` 類別產生的 `…_GeneratedInjector` 在預設套件,Hilt 彙整的元件引用不到,`hiltJavaCompileDebugUnitTest` 失敗 cannot find symbol|2026-11-06 Robolectric 實跑|範本 T11〈測試:Hilt〉
- API-30 不用 MockWebServer|Ktor 測試改打 JDK 內建 `com.sun.net.httpserver.HttpServer`,不碰 OkHttp,跟 T4 的 OkHttp 4、5 兩套依賴並存都照跑;Ktor 3.6.1 在 Kotlin 2.2.21 編得過|2026-11-06 實跑(實驗 E8)|範本 T4〈測試:Ktor〉

## 待決問題

(開頭欄位 Q1–Q4 都已結;這裡只放長版)

- Q1 K1、K2 要不要用 ArchUnit → 決策 d1:用(決定 1、預實驗 P3)。當時的另一選項是不用:API-9 與 CO-1 的整個範圍版交給 detekt(`GlobalCoroutineUsage` 不要型別資訊、`InjectDispatcher` 要 CI 的 Gradle 那步)加規則包,API-9 改「不接(代碼審或真機)」,T12 不做;代價是函式本體當場建 scope 只剩規則包看新增的行。
- Q2 產生器的 Konsist 要不要現在換 1.0.0-beta.1 → 決策 d2:先不換、等正式版(〈不做〉第三條、REVISIT)。之後要換就另開 [[Systems/android-arch-template]] 的工作,範圍是前半〈不做〉記的三件事。
- Q3 K5 → 自答不做(決定 5)。Q4 API-30 → 自答做(決定 6)。

## 審計修正紀錄

- 舊否決對照(2026-11-06 動筆時跑 `lumos rejections`,459 行,按 ArchUnit、Konsist、Robolectric、模擬器、LeakCanary、凍結、Hilt、Ktor 等概念比對):**更正(r1 架構對齊 F1)**:動筆時寫「沒有撞到本案的否決」是錯的——[[Projects/Android的MVVM與DDD目標架構範本_計劃]] 的 PRIOR-ART 明文否決過 ArchUnit(那句在正文、不在 `lumos rejections` 掃的欄位,按概念比對時漏了);已問使用者,翻案記為決策 d3,理由與兩套函式庫分工見〈範圍〉決定 1。其餘沒有撞到。最近的另一條是 [[Projects/Android記憶體與穩定性驗收_計劃]] 否決「LeakCanary 本身」當驗收工具——它靠 `am dumpheap`,在使用者實機 Android 16 上對 profileable 建置回 `SecurityException: Process not debuggable`;本案 T10 跑在模擬器的 debug 建置(可除錯),不是那個情境,實驗 E12 會實證;若 debug 建置也拿不到堆積,T10 照〈做法〉2 改回「未接(儀器批)」。前半核過的三條同向否決(Room 守衛否決推送前故障注入、Macrobenchmark 否決 lumos 呼叫 gradlew、逐層診斷否決 skill 附腳本讓消費專案呼叫)本案照舊不碰。Konsist 那條(前半 Q3/d3 被 d4 取代)本案沿用 d4 的方向:產生器不在本批換版。
- r1(2026-11-06,4 席:通才、可行性、依據、架構對齊,全 sonnet):28 條/blocking 16/凍結清單常駐建檔會假綠、Kotlin 合成類別與預設參數讓 K1、K2 誤報、兩個壞寫法(WorkManager 吞取消、Fragment `lifecycleScope`)靠接例外測不出、Room 3 已穩定、UI-39 型錄只改一欄會自相矛盾、ArchUnit 撞舊否決(使用者裁翻案 d3);全部折入。
- 席報告與編排者裁決:`governance/review-reports/android儀器測試範本與架構測試/`(四份 `r1-*-sonnet.md` 與 `r1-intake.md`〈先查世界與裁決〉;架構對齊 F3 以更正版為準)。

折入時新增的機制,先寫不加它的最小解為什麼不夠:

- 凍結清單「預設 false、初次建檔才用 Gradle 屬性打開」:最小解是照前一版常駐 true,但可行性 F1 實跑刪檔或漏提交就全綠、新違規一起被凍結,等於守衛自己關掉;只寫「記得提交」不機械,CI 乾淨 checkout 照樣假綠。
- 判允許類別「往外找最外層類別」與 `$default` 豁免:最小解是只看呼叫端類別,但 Kotlin 把合法寫法編進 `App$onCreate$1`、`AppModule$Companion`、`load$default`(可行性 F5、F6 實跑誤報),誤報會逼專案把真違規一起凍結。
- 自訂 `ImportOption` 排除測試類別:最小解是 ArchUnit 內建 `DoNotIncludeTests`,它認不認 AGP 的 `debugUnitTest` 路徑沒人驗過(通才 F3),先寫自訂排除、E5 對照內建那個,內建夠用就改回內建。
- T8、T11 的壞寫法改成「假依賴計數」:最小解是 `runCatching` 接例外,可行性 F3、F4 實跑兩種都接不到或卡死,不換形狀就沒有斷言紅。
- `t_kotlin_test_templates_sections` 加內容檢查(每節有〈紅綠矩陣〉、T12 指到 T11 的那句):最小解是只靠 `template_problems` 驗標題,一組缺矩陣或漏指路時所有自動檢查都綠(通才 F8)。

### r1 逐條去向

| 席與編號 | 嚴重度 | 去向 |
|---|---|---|
| 通才 F1 凍結清單常駐 true、刪檔預期相反、沒寫路徑 | major | 折:〈做法〉1 T12「凍結清單」改預設 false、`-ParchunitFreezeInit` 初次建檔、`freeze.store.default.path`、提交 `archunit_store`;E5 改五步;S2、S5、預期值表、〈實務隱患〉、〈依據來源〉同步 |
| 通才 F2 UI-39 型錄只改後果欄自相矛盾 | major | 折:〈做法〉2 標題、壞寫法、好寫法、後果四欄一起改;S6 與預期值表加檢查標題與壞寫法欄 |
| 通才 F3 K1、K2 會匯入測試類別 | major | 折:T12「不匯入測試類別」自訂 `ImportOption`(AGP 路徑);E5 加 `src/test` 樣本與內建 `DoNotIncludeTests` 對照、多模組樣本;E7 拿掉排除那道 |
| 通才 F4 Companion 裡的 `@Provides`、suspend lambda 誤紅 | major | 折:T12 判最外層宣告類別;E5 加 companion 與 `@Binds`+`@Provides` 模組、Application 裡 suspend lambda 樣本;預期值表一列 |
| 通才 F5 函式預設參數 `load$default` | minor | 折:T12 豁免 `$default` 合成方法;E5 樣本、E7 改壞、預期值表一列 |
| 通才 F6 T13 沒指定 production 範圍 | major | 折:T13 一律 `scopeFromProduction()`;E6 加 `src/test` 樣本與 `scopeFromProject()` 對照;預期值表一列 |
| 通才 F7 命名慣例以外的狀態類別不判 | minor | 折:T13 後綴改常數可擴充;天花板 10;E6 加後綴 `State` 樣本 |
| 通才 F8 範本內容只有 manual 把關 | minor | 折:〈做法〉3 與 S2:sections 測試檢查每節〈紅綠矩陣〉、T12 指到 T11 的字串、凍結設定 |
| 可行性 F1 常駐 true 刪檔全綠 | major | 折:同通才 F1(E5 預期照實跑改寫,另跑常駐 true 對照) |
| 可行性 F2 清單檔落在模組根 | major | 折:T12 寫 `freeze.store.default.path=src/test/resources/archunit_store` |
| 可行性 F3 WorkManager 壞寫法卡死或分不出 | major | 折:T8 改成有上限迴圈加假依賴計數(`markDone`、`recordError`、`close`、來源呼叫次數),`runTest(timeout = 10.seconds)`,兩個壞寫法變體各自斷言紅;預期值表一列 |
| 可行性 F4 Fragment 例外 `runCatching` 接不到 | major | 折:T11 API-9 小節改成假畫面記錄器數「銷毀後被呼叫次數」,不丟例外、不靠接例外;依據加官方協程例外頁;預期值表一列 |
| 可行性 F5 suspend lambda 合成類別誤報 | major | 折:同通才 F4 |
| 可行性 F6 `load$default` 誤報 | major | 折:同通才 F5 |
| 可行性 F7 骨架沒寫 targetSdk | minor | 折:骨架寫 `targetSdk = 36`;前提 P2 補實跑結論;S2 檢查 |
| 可行性 F8 inline 函式報兩筆 | minor | 折:T12 節開頭寫明;天花板 5 補一句 |
| 可行性 F9 `NoLeakAssertionFailedError` 型別 | minor | 折:T10 說法改「可能是 AssertionError 子類,收證照型別名判不認」;E1 記實際型別與父類別 |
| 可行性 F10 `MigrationTestHelper` 位置參數編不過 | minor | 折:T6 一律具名參數,寫明官方參數順序 |
| 依據 F1 Room 3 已穩定 | major | 折:T6 兩份〈依賴〉(Room 2.8.5、Room 3.0.3)與兩份 import;刪 Room 3 的 REVISIT 與〈不做〉那行;E10 改兩個主版本;依據來源兩行 |
| 依據 F2 前半 S2 與 REVISIT 沒處理 | major | 折:〈做法〉6 前半 S2 標被取代、`REVISIT:2027-01-31` 刪掉並記結案;〈回退〉補還原 |
| 依據 F3 `Instant`「沒有壞處」不符官方 | major | 折:決定 2 改「輕微多餘重組、不判」並引官方原句;「就地改→跳過」標推論;型錄四欄一起改 |
| 依據 F4 凍結設定與 E5 矛盾 | major | 折:同通才 F1 |
| 依據 F5 Robolectric 版本 | minor | 折:前提 P2 標只在 4.16 量過;E4 用 4.17 先重跑 P1、P2;新 REVISIT |
| 依據 F6 ARCH-3 沒關自動時鐘 | minor | 折:T9 ARCH-3 先 `mainClock.autoAdvance = false`;依據來源一行 |
| 架構對齊 F1 ArchUnit 撞舊否決 | major | 折:使用者裁翻案(決策 d3);PRIOR-ART ②、決定 1 寫推翻哪條舊否決、理由、兩套函式庫分工;〈審計修正紀錄〉第一行更正「沒有撞到」;依據來源一行 |
| 架構對齊 F2 三套舊違規容忍 | minor | 折:T13 併進產生器時改用 `legacyFiles`;寫明產生器 JSON、T13 常數、T12 凍結清單三者邊界 |
| 架構對齊 F3(更正版)`sdk=34` 只在骨架、新元素 | minor | 折:Robolectric 組〈依賴〉節尾寫 `sdk=34`、〈怎麼用〉補一句;PRIOR-ART ③ 承認兩個新的小元素與理由 |
| 架構對齊 F4〈輸入與口徑〉留作廢值 | minor | 折:〈做法〉2 拿掉兩個值的說明;S6 檢查 |

### 實作實驗修正(2026-11-06)

實驗照〈實驗〉E1–E12 跑完,結果與證據在 [[Verification/2026-11-06_Android儀器測試範本與架構測試實跑]];計劃預期被實驗推翻或補充的地方,範本照實跑寫,這裡記改了什麼:

- 骨架:`buildFeatures { compose = true }` 與 Compose 外掛不放骨架,改由用到 Compose 的組(T9、T12 的實驗樣本)在〈依賴〉加;骨架開著外掛時沒有 Compose runtime 的組編譯 `IncompatibleComposeRuntimeVersionException`。版本照 AGP 8.13.2 的天花板(見〈依據來源〉)。
- T6:手動 `sourceSets["androidTest"].assets.srcDir(…)` 拿掉(Room 外掛自己接);補「升版後第一次建置就跑升級測試會找不到最新版 json」的坑;Room 3 的差異不只 import(`migrate` 是 suspend、helper 的方法是 suspend),所以〈測試:Room 3〉另寫一份、〈好寫法〉照 Room 2 寫並寫明兩處機械改法;每支升級測試先刪資料庫檔(上一支留下的第 3 版檔會讓 `createDatabase(2)` 找 3→2 路徑);DATA-21 訊息只帶例外類別名(儀器報告 64KB 截斷)。
- T9:無障礙要傳 WARNING 門檻的 validator(預設不報對比);ARCH-3 不關自動時鐘時第二次點擊丟「node is no longer in the tree」、好壞一起紅(不是計劃寫的「好寫法也多一頁」,結論相同:要關);STATE-23 的例外在 `rememberSaveable` 登記時(組建當下)就丟,`runCatching` 要包住 `setContent`;DATA-63 加一支「真的沒資料要顯示空畫面」;TEST-29 的〈壞測試〉在 Robolectric 與模擬器的結果記在驗證紀錄。
- T10:`debugImplementation` 要加 `leakcanary-android`(官方頁有寫、計劃漏了),只加 instrumentation 時壞寫法照綠。
- T11:Hilt 用 2.58(2.59 起要 AGP 9);Hilt 測試類別放具名套件。
- T13:「沒有 gradlew 就例外」改成「Gradle wrapper、Maven wrapper、`.git` 都沒有才例外」;型別別名 0.17.3 判不到、1.0.0-beta.1 判得到(兩版矩陣相同,這一點不同,寫進範本)。
- T4 API-30:測試伺服器改 JDK `HttpServer`,不用 MockWebServer(避開 OkHttp 主版本分岔)。
- TEST-29 照〈做法〉2 移出、改回「未接(儀器批)」:Compose 1.11 下讓時鐘自動推進的〈壞測試〉在 Robolectric 與模擬器都綠、沒卡住(官方同步頁也沒說無限動畫會卡),範本抓不到差別;〈測試〉與〈壞測試〉留在 T9 當對照。其餘 28 列照〈範圍〉接上,範本 59 列、「未接(儀器批)」1 列。

### 代碼審 code-android儀器測試範本 r1 修正(2026-11-06)

五席(範本甲、範本乙、範本丙、測試、架構對齊,全 sonnet)13 條、major 2 條,全數折入;卷證 `governance/review-reports/code-android儀器測試範本/`(五份席報告與 `r1-intake.md`)。

- T12 凍結(範本丙 F1,major):範本照實寫 `allowStoreCreation=false` 只擋索引檔整份不見;加 `freeze.store.default.allowStoreUpdate=false`,`-ParchunitFreezeInit` 同時打開建立與更新;矩陣補四格(加規則、改描述、修掉舊違規、刪清單)。實驗見驗證紀錄 E13。
- T12 守衛(測試 F1,major):`_kt_instr_template_problems` 只在 T12 的 properties 與 kotlin 圍欄裡比對整行設定,加矩陣 `StoreUpdateFailedException` 格的檢查;改壞只改圍欄行(含搬到散文、搬進 build 圍欄),另有「只改散文不報」的對照。
- UI-39 守衛(測試 F2、F3):判準抽成 `_kt_ui39_problems`,加好寫法欄;改壞對照拿改壞後的型錄跑同一組判準。
- 措辭(範本甲 F1、範本乙 F1/F2、範本丙 F2、測試 F4):檔頭把 T4 Ktor 小節寫進 Android 模組那一半;TEST-29 兩處註解改成實測結論;T9「九列」改成「〈測試〉10 支」;STATE-17 說明改成通知一次、內容兩筆;UI-39 後果欄寫明 `===` 是官方頁原文、只有畫面不更新是推論。新加 `_kt_instr_wording_problems` 守這幾句。
- 一致性(架構對齊 F1、F2):缺節訊息改成跟 `template_problems` 同一句「範本檔沒有 T<n> 節」;後半 S2 的內容檢查從 `t_kotlin_test_templates_sections` 搬進 `t_kotlin_test_templates_content_guards`(S2 綁定跟著改);測試品質標準的指路句改成「照抄起手:…(T7–T11 節…)」,`sdk=34` 指到骨架節(S7 與預期值表跟著改)。

### 代碼審 code-android儀器測試範本 r2 修正(2026-11-06)

兩席(通才、架構對齊,全 sonnet)6 條、全 minor,全數折入;卷證同上目錄的 `r2-intake.md` 與兩份席報告。

- T12 矩陣基準(通才 F1):末四格的被測程式欄照 E13 實際基準改成〈好寫法〉加〈壞寫法:CO-1 資料層寫死 withContext〉(舊違規 `TagRepository`);「修掉舊違規」那格改寫在被測程式欄、〈測試〉不動;前導句分開前七格的零違規基準與末四格的一筆舊違規基準。守衛 `_kt_t12_freeze_rows_problems` 查凍結格的被測程式帶舊違規、修掉那格寫在被測程式欄、前導句不再說每一格零違規。
- T12 建清單條件(通才 F2):`_kt_instr_template_problems` 要求兩行 `systemProperty(… "true")` 在 `if (project.hasProperty("archunitFreezeInit")) {` 區塊裡(配大括號);改壞含 `if (true)`、別的屬性、拿掉條件、把一行搬到條件外。
- 改描述的清單(通才 F3):範本寫明改描述時把 `stored.rules` 裡舊描述那一行與它的清單檔一起刪、帶屬性那次的清單差異要特別看新增的違規;「清單只能縮小」改成「違規只准變少,多出來的在代碼審說明」;〈風險〉那行跟著改。`_kt_instr_wording_problems` 守這三句。
- 計劃與驗證紀錄(通才 F4):〈做〉表 T4 補 Ktor 列改成 Android app 模組的本機單元測試;驗證紀錄總格數 61→65、T12 7→11,寫明末 4 格是 E13 新加、每格跑一次(原 7 格連跑 20 次)。新加 `_kt_instr_records_problems` 守:驗證紀錄 S4 的 T12 格數等於範本 T12 矩陣列數、總格數等於各組加總、T4 補 Ktor 列不寫純 JVM;拿修正前的兩篇筆記跑會報 T12 格數與 Ktor 列兩處。
- 測試總檔寫法(架構對齊 F1、F2):`_kt_template_sections` 多一個 `""` 鍵放組開頭段,T9、T11、T12 開頭都從這裡取,不再手切字串(圍欄裡的 `###` 不算小節,有對照案例);圍欄語言收成 `_kt_lang_fences`/`_kt_fence_blocks`,照 CommonMark 取 info string 第一個字整字比對,`_kt_kotlin_blocks`、T12 設定比對與改壞輔助 `_in_t12_fence` 都走它。
- 改壞:新加與改過的 17 道判準在 `git clone --shared` 複本各拿掉一次,各自翻紅(其中「修掉舊違規寫在測試欄」第一次沒紅——改壞案例的期望字太寬、落到另一條訊息也命中,收緊後翻紅)。
- 代碼審 r2 後補(2026-11-06):T12 第 2 步(改描述時刪 `stored.rules` 舊行與舊清單檔)實跑,與範本說法一致、範本不改,原 `REVISIT:2027-02-06 實跑一次 T12 範本第 2 步` 那行刪掉,結果見驗證紀錄 [[Verification/2026-11-06_Android儀器測試範本與架構測試實跑]] E14;〈做〉表 T4 補 Ktor 列的「本機 MockWebServer」改成範本實際用的 JDK `HttpServer`;測試總檔 `_kt_instr_wording_problems` 的檔頭改取到第一個圍欄外的 `## `(不再 `split("\n## ")` 手切),新加「檔頭圍欄裡的 `## `」對照案例,先紅後綠,`git clone --shared` 複本改回手切翻紅。
