---
type: project
status: doing
created: 2026-11-06
updated: 2026-11-06
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/kotlin規則包
  - Systems/test-quality-cli
related:
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Projects/Android目標架構開關與舊檔畢業_計劃]]"
  - "[[Projects/Android本機單元測試驗收標準_計劃]]"
  - "[[Projects/Android寫法語意情境表態與盲判_計劃]]"
  - "[[Systems/kotlin規則包]]"
  - "[[Systems/android-arch-template]]"
pending_questions:
  - id: Q1
    text: API-4(一支失敗時連坐或不連坐)的範本要預設哪一種斷言?建議:兩個互斥版本都放、不設預設,採用時照第三批情境表態的答案留一個
    class: 需求
    stage: 實作
    status: 已決
    decision: "#d1"
  - id: Q2
    text: API-10/API-31(重複送出、同一資源多個請求)的範本預設斷言什麼?建議:預設連點兩次只打一次 API;後端有冪等鍵時才換成兩次帶同一個冪等鍵的版本
    class: 需求
    stage: 實作
    status: 已決
    decision: "#d5"
  - id: Q3
    text: Konsist 要不要現在換成 1.0.0-beta.1(2026-11-04 發的 beta,resideIn 改名讓舊產出編不過)?建議:換,0.17.3 的理由(0.18 綁 Kotlin 2.4)已被它撤掉;不換就等 1.0.0 正式版、K1–K3 只用兩版都有的 API
    class: 依賴
    stage: 架構
    status: 已決
    decision: "#d4"
  - id: Q4
    text: K1–K3 跟規則包的 kt-unmanaged-scope-launch、kt-hardcoded-dispatchers-io、kt-uistate-mutable-field 形狀重複,還要不要做?自答:做;規則包只看新增行、要宣告且裝 ast-grep,K 測試跑在專案自己的單元測試、看整個目標範圍
    class: 範圍
    stage: 架構
    status: 已決
    decision: "#d4"
decisions:
  - content: Q1:API-4 範本兩個互斥斷言版本都放、不設預設,採用時照第三批情境表態的答案留一個
    id: d1
    context: 一支失敗要不要連坐是業務決定,範本無法代答
    why_chosen: 編排者代裁,依使用者授權原話「我要睡了，你有裁量權、簽核權」「你的標準、最佳寫法來源要有依據，不要你自己寫」;範本不替業務選邊,把選擇交給既有的情境表態
    decided: 2026-11-06
    valid: true
  - content: Q2:API-10/API-31 範本預設斷言連點兩次只打一次 API;後端有冪等鍵時換成兩次帶同一冪等鍵的版本
    id: d2
    context: 重複送出的預設保護方向
    why_chosen: 編排者代裁,依使用者授權原話「我要睡了，你有裁量權、簽核權」「你的標準、最佳寫法來源要有依據，不要你自己寫」;只打一次是不需後端配合就成立的安全預設
    decided: 2026-11-06
    valid: false
    superseded_by: "#d5"
    ended: 2026-11-06
  - content: Q3:Konsist 換 1.0.0-beta.1,條件是實作時 K1–K3 與既有產出逐條編譯過;編不過就留 0.17.3 並記 Issue
    id: d3
    context: 0.17.3 的理由(0.18 綁 Kotlin 2.4)已被 1.0.0-beta.1 撤掉,但它是 beta
    why_chosen: 編排者代裁,依使用者授權原話「我要睡了，你有裁量權、簽核權」「你的標準、最佳寫法來源要有依據，不要你自己寫」;官方安裝頁現寫 1.0.0-beta.1,附編譯驗證當退路
    decided: 2026-11-06
    valid: false
    superseded_by: "#d4"
    ended: 2026-11-06
  - content: K1–K3 架構測試與 Konsist 換版整組移出本批,型錄 API-9、CO-5、UI-39 通電批次改「未接(架構測試後續計劃)」,另開後續計劃
    id: d4
    context: 設計審 r1 四席共 20 條 major,其中 K1–K3 與 Konsist 換版佔多條
    why_chosen: 編排者 r1 裁決:規則包已有同形三條規則(kt-unmanaged-scope-launch、kt-hardcoded-dispatchers-io、kt-uistate-mutable-field)接在新增告警閘;通才與可行性兩席各自打穿 K1–K3 的判斷形狀(函式內建 scope、rememberCoroutineScope、sealed UiState、DI 模組);Konsist 1.0.0-beta.1 是兩天前的 beta
    decided: 2026-11-06
    valid: true
  - content: API-10 範本預設斷言連點兩次只打一次 API,後端有冪等鍵時換成兩次帶同一冪等鍵的版本;API-31 另寫一支,斷言多個呼叫端同時要同一份資料只打一次網路
    id: d5
    context: 設計審 r1 依據席 F2:API-31 是讀取流量合併、不是寫入重送,冪等鍵版本對它無效
    why_chosen: 編排者 r1 裁決要求兩列分開斷言;型錄 API-31 標準寫法是共用 Deferred 加 mutex,API-10 是防重複送出,測的是兩件事
    decided: 2026-11-06
    valid: true
---
# Android行為測試範本與架構測試_計劃

> 白話:型錄 `skills/kotlin-idioms/checks-catalog.md` 裡有 68 列「長相看不出錯、要跑起來才知道」的寫法(級含 C),目前只寫了「批五再接」。這份計劃替其中在電腦 JVM 上就跑得動的 32 列做測試範本,每組附「好寫法綠、壞寫法紅」的對照,實作時真的跑一次;其餘 36 列明寫這批不做與理由(要模擬器的、只能代碼審或真機的、架構測試留給後續計劃的、Ktor 那一列)。型錄每列的「通電批次」欄直接寫它用哪一組範本,由型錄既有的自我檢查驗那一組真的存在。是 [[Projects/Android協程與API寫法機械檢查標準_計劃]] 分批表的第五批;原本同批的 Konsist 架構測試在設計審第一輪後移出(決策 d4)。

立案:使用者 2026-11-06 原話「遵照上面三個要點，完成這五個批次功能，目標是把Android靜態能先掃描的實務隱患都先處理過」,三要點是「1.實作連續被打穿、或顯著無法收斂，就上網印證方向、業界實作找最佳解 2.所有機制都要實驗一遍，看看可行性、有沒有漏洞，修的流程遵照第一條 3.Android的規則也一樣，來源、依據，這可以在語意盲判的時候起到輔助判別的作用」,另一句「我們開發的過程中，所有機制的依據來源，最後也要補回plan，方便後續迭代」。輸入是 2026-11-06 的第五批調研稿(68 列分類、T0–T11 範本組、K1–K5 架構測試、本機實驗),調研稿放在會談暫存區,本計劃把要用的結論與已開頁核對的原文搬進〈依據來源〉,不靠那份暫存稿。

PRIOR-ART: ①測試寫法全照官方:Android 協程測試頁與 Flow 測試頁(`runTest`、`StandardTestDispatcher`、`backgroundScope`、`advanceUntilIdle`)、kotlinx.coroutines API 文件、Turbine README、OkHttp MockWebServer README、kotlinx.serialization JSON 設定頁、Android SavedStateHandle 頁;`MainDispatcherRule` 的形狀照 nowinandroid `core/testing` 同名類別,但建構時明傳 `StandardTestDispatcher()`(nowinandroid 與官方範例預設 Unconfined,照抄會讓「沒推進就斷言」的壞測試也綠;改照既有測試品質標準「預設用 StandardTestDispatcher」)。②範本檔照 DDD 與前端兩份照抄式目標架構範本的寫法:一般的 ```kotlin 圍欄、節用標題分,不加自訂標頭;放在 `skills/kotlin-idioms/`,跟同目錄的型錄 `checks-catalog.md` 一樣是 `check.py` 會讀的資料檔。③範本與型錄的對應沿用型錄既有的「通電批次」欄:值從「行為測試或正向約束=批五」改成帶組代號的「行為測試或正向約束=範本 T1」,自檢只多驗「組代號在範本檔有那一節」;不新造認領語法。④紅要是斷言失敗才算,照測試品質標準〈Android 本機單元測試的驗收標準〉與收證工具 `scripts/test_quality.py` 的 `assertion_failure` 同一套判準。⑤Turbine 收尾照型錄 TEST-18 與測試品質標準:`expectNoEvents()` 或明確 `cancelAndIgnoreRemainingEvents()`。裁定:全借用,新寫的只有範本內容、自檢的一項與一支資料測試。
RETIRE-IF: 2027-05-06 人裁時,在消費專案的 git 歷史裡數照範本起手的測試檔(第一行留了 `// 起手:kotlin-idioms test-templates <組代號>` 的),全部專案加起來少於 5 支,就把範本檔降成 kotlin-idioms 裡的一段連結清單(只留官方頁連結),型錄的「範本 Tn」值改回「未接」、自檢那一項一起拿掉 [retire:人裁] [until:2027-05-06]。

## 用詞

- **型錄**:`skills/kotlin-idioms/checks-catalog.md`,473 列,欄位見它的〈輸入與口徑〉;本計劃只動「通電批次」欄裡「行為測試或正向約束=」那一段的值,與〈輸入與口徑〉一句。
- **C 列**:型錄「級」欄含 C 的列(68 列,2026-11-06 用 `check.py` 讀表數出);68 列的通電批次欄目前全都寫「行為測試或正向約束=批五」。
- **範本組**:一組同測法的測試範本,代號 T0–T5(本批做,只是 T4 少 API-30)、T6–T11(儀器批);架構測試 K1–K5(全部不在本批)。代號沿用調研稿,不重編。T6 Room 遷移與資料層、T7 Paging、T8 WorkManager、T9 Compose UI 測試(含 T9a 無障礙檢查)、T10 LeakCanary 儀器測試、T11 生命週期;K1 不准無主協程、K2 資料層 dispatcher 注入、K3 UiState 不可變、K4 Hilt 宿主、K5 每個 Migration 要有測試。
- **範本檔**:`skills/kotlin-idioms/test-templates.md`(新增)。開頭兩節是〈怎麼用〉與〈實驗專案骨架〉,之後每組一節,節標題以 `## T<n> ` 開頭(例 `## T1 虛擬時間`)。節裡依序是幾個小節:〈依據〉(每列一行:網址加原文摘句)、〈依賴〉(一個 ```kotlin 圍欄,只放 `dependencies { … }` 裡的行)、〈測試〉(消費專案照抄的測試;同組有互斥版本時各自一個小節,標題寫版本名,例「測試:API-4 連坐版」)、〈假依賴〉(測試用的假實作,放 `src/test`)、〈好寫法〉與〈壞寫法〉(實驗用的被測程式,放 `src/main`;同組多個壞寫法各自一個小節,標題寫變體名,例「壞寫法:API-1 依序呼叫」)、〈紅綠矩陣〉。程式一律用一般的 ```kotlin 圍欄。
- **紅綠矩陣**:一組裡「哪一個測試小節 × 哪一個被測程式小節 → 每支測試應該是什麼結果」的表,用小節標題當列名與欄名,所以每個格子對得到一份程式。結果只准三種:`綠`、`斷言紅`(附訊息片段)、`逾時紅`;逾時紅只准出現在 T0 的〈壞測試〉列(示範錯的測試寫法會卡住),〈測試〉列的紅一律要是斷言紅——收證工具只把斷言失敗算成「測試抓到錯」,例外或逾時的紅不算(測試品質標準〈Android 本機單元測試的驗收標準〉的「被當掉抓到的錯不算」)。小節裡每一支 `@Test` 都要出現在矩陣裡。
- **實驗專案**:實作者在會談暫存區照〈實驗專案骨架〉手工組的純 JVM Gradle 專案:一個格子一份,〈測試〉與〈假依賴〉放 `src/test/kotlin`、那一格的被測程式放 `src/main/kotlin`;跑完的結果寫進驗證紀錄。lumos 不產生也不執行它。
- **儀器批**:要 Android 模擬器、Robolectric 或 Android 專用套件(只發佈 `.aar`、沒有純 JVM 版)才跑得動的列,下一批另開計劃。
- **架構測試後續計劃**:K1–K3 與 Konsist 換版的後續計劃,開的時候帶上〈不做〉裡記的三個打穿點。

## 範圍

### 做(32 列)

| 組 | 型錄列 | 測法(一句) | 跑在哪 |
|---|---|---|---|
| T0 測試骨架守則 | TEST-4、TEST-5、TEST-6、TEST-7、TEST-9、TEST-14、TEST-17、TEST-18、TEST-19、TEST-20(10) | 正確的協程/Flow 測試起手式;矩陣是「好測試 vs 壞測試 × 正確程式 vs 埋錯程式」 | 純 JVM |
| T1 虛擬時間 | API-1、API-4、API-10、API-31、API-32、API-34、FLOW-29、CO-14(8) | 假依賴用 `delay` 模擬耗時,斷言 `testScheduler.currentTime`、呼叫次數、逾時後狀態 | 純 JVM |
| T2 Flow 發射 | API-8、FLOW-3、FLOW-18、FLOW-20、FLOW-23、FLOW-24、STATE-10(7) | Turbine 斷言收到哪幾筆、順序、有沒有多;共享類數上游被執行幾次 | 純 JVM |
| T3 程序被殺還原 | STATE-6、STATE-26(2) | 同一份 `SavedStateHandle` 內容建第二個 ViewModel,斷言輸入與待處理 id 還在 | 純 JVM(`lifecycle-viewmodel-savedstate` 有 JVM 版) |
| T4 HTTP 邊界 | API-21、API-26(2) | 真的 OkHttp/Retrofit 打本機 MockWebServer,排好 204、連續 401 | 純 JVM |
| T5 序列化契約 | DATA-72、DATA-73、DATA-74(3) | 用專案正式的 `Json {}` 實例解碼/編碼伺服器可能回的 JSON | 純 JVM |

做法:

1. **範本檔** `skills/kotlin-idioms/test-templates.md`(新增),形狀照〈用詞〉的範本檔:
   - 〈怎麼用〉:找到型錄那列 → 看通電批次欄寫的組代號 → 到這份檔的那一節 → 照抄〈測試〉與〈假依賴〉改名套進專案、依賴照〈依賴〉加 → 跑一次確認綠;照抄的測試檔第一行留 `// 起手:kotlin-idioms test-templates <組代號>`(RETIRE-IF 靠它數)。
   - 〈實驗專案骨架〉:`settings.gradle.kts` 與 `build.gradle.kts` 全文——`plugins` 有 `kotlin("jvm")` 與 `kotlin("plugin.serialization")`(版本 2.2.21)、`repositories { google(); mavenCentral() }`(androidx 套件只發在 Google Maven,只有 `mavenCentral()` 時 `lifecycle-viewmodel-savedstate` 解析失敗,可行性席實跑)、`kotlin { jvmToolchain(17) }`、`tasks.test { useJUnit() }`;各組〈依賴〉的行貼進它的 `dependencies { }`。
   - 範本的程式碼要點(寫進範本、實驗驗過才算):
     - T0:`@get:Rule val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())`,宣告在其他用到 dispatcher 的屬性前面;`stateIn(WhileSubscribed)` 先在 `backgroundScope` 掛空收集者;斷言 StateFlow 的最終 `value`,不逐一比中間值;Turbine 結束前每個值都收掉,或用 `expectNoEvents()` 斷言沒有多的,真的不管後面的才明寫 `cancelAndIgnoreRemainingEvents()`;錯誤用 `awaitError()`。(實作實驗改寫:Turbine 這幾個檢查失敗丟 `TurbineAssertionError`,收證不算斷言失敗,範本改用 `awaitEvent()`、`cancelAndConsumeRemainingEvents()` 取事件再 `assertEquals`/`assertIs`,見審計修正紀錄〈實作〉)
     - T1:虛擬時間讀 `testScheduler.currentTime`,測試類別加 `@OptIn(ExperimentalCoroutinesApi::class)`(它是成員屬性,只有實驗 API 警告;調研編譯失敗的是另一個頂層擴充 `TestScope.currentTime`)。API-4 是兩個互斥版本(決策 d1):〈測試:API-4 連坐版〉配〈好寫法:API-4 連坐〉、〈測試:API-4 不連坐版〉配〈好寫法:API-4 不連坐〉,各自交叉時斷言紅,範本註解寫「照情境表態的答案留一個版本」。API-10 與 API-31 分開斷言(決策 d5):API-10 斷言「`submit()` 連呼兩次只打一次 API」,另有〈測試:API-10 冪等鍵版〉配〈好寫法:API-10 冪等鍵〉(兩次呼叫帶同一個鍵);API-31 斷言「三個呼叫端同時 `refresh()` 只打一次網路、三個都拿到同一份結果」。會丟例外的壞寫法(API-34 第二次 resume 丟 `IllegalStateException: Already resumed`)用 `runCatching` 接住再斷言;FLOW-29 把被測函式放進 `backgroundScope.launch`、推進後斷言那個 Job `isCompleted`(可行性席實跑:壞寫法是斷言紅、不會卡到 60 秒逾時)。
     - T2:STATE-10 斷言「同一則錯誤連發兩次,畫面收到兩個不同 id」;FLOW-18 數上游被執行幾次;FLOW-3 斷言第一筆是 Loading;FLOW-23 用 `runCatching` 接住 `NoSuchElementException` 再斷言被測函式回了 null;FLOW-20 跟 FLOW-29 同形,把「collect 之後那段」放進 `backgroundScope.launch`,推進後斷言那段的副作用有發生(壞寫法永遠走不到,斷言紅)。
     - T3:照官方「用測試值建新的 SavedStateHandle」,把第一個 ViewModel 寫過的 handle 內容複製成第二個 handle 再建 ViewModel(可行性席在純 JVM 用 `lifecycle-viewmodel-savedstate:2.9.4` 實跑綠);`ViewModelScenario.recreate()` 能不能在純 JVM 用看實驗 E5。(實作:E5 在純 JVM 能用;代碼審 r1 實跑它在 Android 模組的本機單元測試例外紅,所以預設〈測試〉是複製 handle 版、viewModelScenario 版標成只在純 JVM 或 KMP 用,見審計修正紀錄〈代碼審 r1〉)
     - T4:204 這類「壞寫法丟例外」的用 `runCatching` 後斷言成功;API-21 排 25 個 401,斷言 `requestCount <= 3`(沒上限的壞寫法會一路重試到 OkHttp 自己的 20 次追隨上限丟 `ProtocolException`,用 `runCatching` 接住,紅成為斷言紅)。走真的 socket,不在 `runTest` 的虛擬時間裡用 `withTimeout`(可行性席實跑:虛擬時間遇到真實 I/O 會直接跳到逾時點,好壞都例外紅);要等真實時間就包進 `withContext(Dispatchers.Default)`。MockWebServer 的版本照消費專案實際解析到的 OkHttp 主版本挑:OkHttp 4 用 `com.squareup.okhttp3:mockwebserver:4.12.0`(套件 `okhttp3.mockwebserver`),OkHttp 5 用 `com.squareup.okhttp3:mockwebserver3:5.5.1`(套件 `mockwebserver3`);版本號跟專案的 OkHttp 對齊,先用 `./gradlew :<模組>:dependencies` 看解析後的版本(測試品質標準「加測試函式庫前看實際版本」那條)。〈測試〉為兩個主版本各放一份 import 寫法。(實作:兩份測試配兩份〈依賴:OkHttp 4〉〈依賴:OkHttp 5〉;API-26 用 Retrofit 3.0.0 加 `converter-kotlinx-serialization`)
     - T5:測試讀專案正式的 `Json` 設定物件(範本用 `AppJson` 佔位),不在測試裡另 new 一個;DATA-72 缺欄位丟 `MissingFieldException`、DATA-73 未知 enum 丟 `SerializationException`,都用 `runCatching` 接住再斷言解碼成功。
2. **型錄改兩處**:
   - 32 列的通電批次欄把「行為測試或正向約束=批五」改成「行為測試或正向約束=範本 T<n>」;不做的 36 列改成「行為測試或正向約束=未接(儀器批)」「行為測試或正向約束=未接(架構測試後續計劃)」「行為測試或正向約束=未接(Ktor 範本後續)」或「行為測試或正向約束=不接(代碼審或真機)」,其他接電方式的批次照舊;接電方式欄不動(型錄格式檢查要求形狀類至少有告警或正向約束,不能拿掉)。實驗把某列移出時,同一個提交裡把它改成對應的「未接」值。
   - 〈輸入與口徑〉的「通電批次欄的值」那句補上新值的意思,並加一句「級含 C 的列,通電批次寫的範本組在 `skills/kotlin-idioms/test-templates.md` 同名的節」。2026-11-06 前掃核對時統計節沒有各批次列數,改值不影響統計;實作時照 `check.py` 讀表重算一次確認。
3. **型錄自檢多一項** `template_problems(rows)`(在 `configs/ast-grep/kotlin-android/check.py`,回傳形狀跟 `catalog_problems` 一樣是 `(列編號, 原因)`;由 `catalog_problems` 在最後呼叫、把它用 `main_rows()` 讀好的主表列傳進去,所以 `--catalog-only`、完整模式與既有的 `t_kotlin_catalog_rows_wired` 都會走到,主表只有 `main_rows` 一條讀法):主表每列通電批次的「行為測試或正向約束=」那一段(`behavior_value`;別的接電方式那段寫了「範本」不算)寫「範本 T<n>」時,範本檔要有那一節——標題規則是 `TEMPLATE_HEADING_RE`(`## T<n>` 後接空白或整行就這樣),而且要在程式圍欄外(圍欄照 CommonMark 判,口徑跟 `scripts/lumos` 的 `_fence_regions` 對齊,`t_kotlin_template_fence_parity` 比對兩份)——沒有就報那一列;值以「範本」開頭卻不是「範本 T<n>」整段報格式錯;範本檔不存在報一筆 `(<templates>, 找不到範本檔)`、不是 UTF-8 報一筆 `(<templates>, 範本檔不是 UTF-8…)`。只驗這一件事;範本內容對不對靠實驗與驗證紀錄。測試輔助 `_ktpack(copy=True)` 多複製範本檔,讓「改壞一份」的測試碰得到;測試端的主表、批次值、標題切段都呼叫 check.py 的同名函式,不另抄。(代碼審 r1、r2 折入後的現況)
4. **指路**:kotlin-idioms 的 `SKILL.md` 開頭那段(已指向型錄)加一句「寫協程、Flow、HTTP、序列化或 SavedStateHandle 的測試,先看型錄那列通電批次寫的範本組,到 `test-templates.md` 同名的節起手」;測試品質標準〈Android 本機單元測試的驗收標準〉的「協程」「Flow」兩小段尾各加一句指到範本檔。
5. **實驗與驗證紀錄**:照〈實驗〉逐項跑,結果寫進一篇 `Verification/` 驗證紀錄(`plan_refs` 連回這篇);實驗推翻範本寫法的,改範本、重跑那一格。
6. **寫回家**:[[Systems/kotlin規則包]] 記一行範本檔與自檢新項(範本檔加進它的 about_code);[[Systems/test-quality-cli]] 記一行測試品質標準多了指到範本的兩句(上一份 Android 單元測試標準計劃落在這篇)。

### 不做(36 列,與理由)

- **儀器批 25 列**:STATE-12、STATE-17、STATE-23、UI-36、UI-52、UI-106、UI-110、ARCH-2、ARCH-3、ARCH-31、ARCH-35、DATA-17、DATA-19、DATA-21、DATA-38、DATA-39、DATA-58、DATA-60、DATA-63、DATA-65、DATA-69、TEST-29、TEST-32、TEST-35、ARCH-56。理由:要 Compose UI 測試、Room `MigrationTestHelper`、Paging、WorkManager、LeakCanary、Robolectric 或 Android 專用套件,本批的實驗環境(純 JVM Gradle)跑不動,消費專案也不能在推送前不開模擬器就跑完。STATE-17(LiveData)在純 JVM 解析不到:`androidx.arch.core:core-testing:2.2.0` 與 `lifecycle-livedata:2.9.4` 在純 JVM Kotlin 專案都解析失敗(可行性席實跑),`lifecycle-livedata-core` 的模組檔只發佈 `.aar`(依據席讀模組檔);另外官方 `InstantTaskExecutorRule` 讓背景工作同步執行,`postValue` 合併的壞寫法在它底下可能照綠,儀器批要另找測法。STATE-23 驗 Compose `rememberSaveable` 要用 `StateRestorationTester`。DATA-39 單看 `Data` 類別可測,但跟 DATA-38 同一組 WorkManager 範本。DATA-19 的 K5 跟 T6 一起做。ARCH-56 的 K4 另缺依據:Hilt 官方頁現版找不到「Fragment 標了宿主 Activity 也要標」的原句。
- **架構測試後續計劃 3 列**:API-9(K1)、CO-5(K2)、UI-39(K3),連同 Konsist 換版(決策 d4,取代原 d3)。理由:①規則包已有同形的三條規則 `kt-unmanaged-scope-launch`、`kt-hardcoded-dispatchers-io`、`kt-uistate-mutable-field` 接在新增告警閘;②設計審 r1 兩席各自打穿 K1–K3 的判斷形狀:函式本體裡 `CoroutineScope(Dispatchers.IO).launch` 漏報、`rememberCoroutineScope()` 與自訂 Application 的 `appScope` 誤報(K1),`sealed interface HomeUiState` 的巢狀 `data class Success(var …)` 漏報(K3),DI 模組 `@Provides fun io() = Dispatchers.IO` 誤報、CO-5 的阻塞呼叫沒有 Dispatchers 字樣漏報(K2);③Konsist 1.0.0-beta.1 是 2026-11-04 才發的 beta,`resideIn*` 改名讓現有產出在新依賴下編不過,lumos 照 0.17.3 反組譯的 `_arch_tpl_konsist_test` 也要跟著重核。後續計劃開的時候帶上這三點與 r1 席報告。產生器資料檔、技能文件 `skills/lumos-project-notes/commands/target-arch-android-template.md` 的版本說法這批都不動。
- **Ktor 1 列**:API-30(串流回應帶出 `execute` 區塊才讀)。理由:T4 用 OkHttp/Retrofit,驗不到 Ktor 的 `prepareGet().execute()`;要驗得加 Ktor client 與它的引擎依賴、另寫一組,而型錄這列的後果(離開區塊即釋放連線)官方頁沒寫,只能靠實驗。選「移出」不選「改用 Ktor client 寫」:只為一列多一套 HTTP 用戶端的依賴與骨架,成本跟其他 31 列的範本加起來差不多,而且依據不全;等有 Ktor 的消費專案時另開。
- **只能代碼審或真機的 7 列**:STATE-20(SavedStateHandle 的寫入時機看 Activity 停止的系統時序,官方頁 Caution 段寫「only saves data written to it when the host Activity is stopped」)、CO-39(多執行緒競態,測試派發器是單執行緒,測不出)、UI-109(截字要看實際字型與螢幕)、DATA-44(前景服務的時限由系統計時)、DATA-77(R8 只在 release 建置出現)、PERF-1、PERF-2(StrictMode 只在裝置上偵測)。維持代碼審與真機驗收(lumos-android-evidence)。
- **不新增產生實驗專案的程式**:原稿的 `check.py --lab` 拿掉。自檢是唯讀職責;範本格式改成一般圍欄後也沒有可機械對應的標頭。實驗專案由實作者照〈實驗專案骨架〉手工組。
- **不改任何推送閘、收證工具與新增告警閘的判定**;不新增 lumos 子命令。
- **不在本 repo 的 CI 跑 Gradle**:CI 沒有 JDK 與 Gradle 下載這一步,範本的 Kotlin 寫錯在這裡看不出來;紅綠只靠實作時的實驗與驗證紀錄,天花板見下。
- **不在型錄每列「實測狀態」欄補範本實測**:實測結果寫在範本檔的矩陣與驗證紀錄,型錄只靠通電批次的組代號指過去。

## 實驗(每個機制都跑一遍,找漏洞)

照使用者第二要點,下面每一項在實作時真的跑;結果不符預期就照第一要點先查官方與業界做法再改,寫進〈依據來源〉與審計修正紀錄。實驗跑在會談暫存區的資料夾,Gradle 用本機 `~/.gradle/wrapper/dists/gradle-8.13-bin/` 那份(調研與 r1 可行性席都用它跑通),Kotlin Gradle 外掛 2.2.21、JDK 17。

- **E1 紅要是斷言紅**:每組〈測試〉列的每個紅,讀 JUnit XML 的失敗型別,用 `scripts/test_quality.py` 的 `assertion_failure` 判,全部要判成斷言失敗。已知會是例外或逾時紅、範本要先改寫的:T1 的 API-34(`IllegalStateException`)與 FLOW-29(卡到 `runTest` 逾時)、T2 的 FLOW-23(`NoSuchElementException`)與 FLOW-20(熱流 collect 永不結束)、T4 的 API-26 204(`IllegalArgumentException: EOF`)與 API-21(`ProtocolException`)、T5 的 DATA-72(`MissingFieldException`)與 DATA-73(`SerializationException`)。
- **E2 每格只紅點名的那支**:〈測試〉×〈壞寫法:某變體〉那格,矩陣沒點名的測試要綠;小節裡每支 `@Test` 都要在矩陣出現。
- **E3 時序穩定**:T0 的 TEST-9 那幾格(壞例用真 dispatcher,型錄後果寫「偶發紅」)、T1(含 CO-14「逾時剛好落在取得資源之後」)、T2、T4(走真的 socket)每格各跑 20 次,結果要每次一樣;不穩的那支改寫或拿掉,型錄那列改「未接」並寫原因。
- **E4 MainDispatcherRule 的預設**:T0 的〈壞測試:TEST-4 沒推進就斷言〉對正確程式,在 `MainDispatcherRule(StandardTestDispatcher())` 下要斷言紅;另跑一次預設 Unconfined 的版本,記下它照綠(證明明傳的必要)。
- **E5 ViewModelScenario 在純 JVM**:Lifecycle 2.9.0 穩定版發行說明寫 `lifecycle-viewmodel-savedstate`(含 `SavedStateHandle`)已是 KMP、有 JVM 版,`lifecycle-viewmodel-testing` 的 `ViewModelScenario.recreate()` 也是 KMP 套件;實跑它在純 JVM 能不能還原 handle 內容。能的話範本 T3 改用它(跟測試品質標準「畫面重建與程序被回收」那條一致),不能就在測試品質標準那條補一句「純 JVM 用複製 handle 的寫法」。(結果:純 JVM 能用;**代碼審 r1 推翻了「範本 T3 改用它」**——它在 Android 模組的本機單元測試例外紅,T3 預設改回複製 handle 版,它降成〈測試:viewModelScenario 版〉只標純 JVM 或 KMP,測試品質標準「畫面重建與程序被回收」那條也改寫了,見審計修正紀錄〈代碼審 r1〉)
- **E6 FLOW-3 的後果**:官方 `combine` 頁沒明寫「每個來源都要先發過」,用範本的紅綠對照實證,實跑訊息寫進驗證紀錄,當型錄那列「後果」欄的佐證。API-34(依序 resume 兩次的訊息)、FLOW-29(`send` 卡住讓父範圍不結束)同樣以實跑訊息當佐證。
- **E7 OkHttp 兩個主版本**:T4 整組在「OkHttp 4.12.0 加 `mockwebserver:4.12.0`」與「OkHttp 5.5.1 加 `mockwebserver3:5.5.1`」各跑一次矩陣,結果要一樣;另跑一次「OkHttp 4.12.0 加 `mockwebserver3:5.5.1`」,記下它的錯(證明要照主版本挑)。
- **E8 自檢那一項**:把型錄某列改成「範本 T9」、刪掉範本檔的 `## T2` 節、把範本檔改名,自檢要各自報;拿掉 `template_problems` 的判斷式,這三種改壞要轉成不報(證明是那一項在抓)。

## 實務隱患

(`lumos pitfalls <計劃> --check` 逐類答,見節末)

- **範本照抄出錯被當成標準**:範本只在實驗專案跑過,消費專案的類別名、依賴版本不同;範本〈怎麼用〉寫明「照抄後在自己的專案跑一次,綠了才算」,並留「故障證明挑本次需求」那條既有標準讓審查看。
- **範本的壞例被本 repo 的推送閘當產品碼**:2026-11-05 規則包樣本 `.kt` 被測試作弊比對與 Room 守衛當產品碼擋過([[Issues/Kotlin規則包代碼審放行的小問題]] 第 7 條)。本批的壞例放在 Markdown 圍欄裡、repo 裡不新增任何 `.kt` 檔,實驗專案只在會談暫存區,不碰那個坑。
- **消費專案的 OkHttp 主版本**:照抄 T4 到用 OkHttp 4 的專案時,配錯 MockWebServer 會混用兩個主版本;範本照主版本給兩套依賴與 import,實驗 E7 驗兩套都對、混用會錯。
- **版本漂移**:Turbine、MockWebServer、kotlinx-coroutines-test、kotlinx-serialization、Lifecycle 的版本只寫在範本檔各組〈依賴〉與〈實驗專案骨架〉,官方改版會過期;回頭條件見節末 REVISIT。
- **效能**:型錄自檢多讀一支範本檔(幾百行)、對每列做一次標題查表。
- **併發**:自檢只讀;實驗專案在會談暫存區,不碰 repo。
- **守衛面**:型錄自檢是本 repo CI 跑的格式檢查,多一項會讓「型錄寫的範本組在範本檔不存在」的提交在 CI 紅;不改任何推送閘或收證判定。
- **舊否決對照**:見審計修正紀錄第一行。
- 前端:不改任何前端檔;「前端」只出現在引用既有的前端目標架構範本那一句。
- 已排除:金流:範本與實驗只用假資料,不碰付款或點數。
- 已排除:對外送出:MockWebServer 只聽本機回環位址;實驗只從 Maven Central 與 Google Maven 下載依賴,不送出任何資料。
- 已排除:不可逆:新增一份 Markdown、擴充自檢程式一項、改型錄一欄的文字,退提交即回原狀。

REVISIT:2027-02-06 範本檔各組〈依賴〉的版本與 Maven Central、Google Maven 最新版對一次,有大版本差就重跑那組的紅綠矩陣

## 驗收條款

- [S1] 當型錄自檢讀型錄與範本檔時,通電批次寫「範本 T<n>」的每一列,範本檔應有以 `## T<n> ` 開頭的標題;把某列改成「範本 T9」、刪掉範本檔的 `## T2` 節(引用 T2 的每列都要報)、範本檔不存在,自檢應各自以 `(列編號, 原因)` 報出;真檔應零問題。 [test:t_kotlin_test_templates_sections]
- [S2] 當讀型錄 68 列 C 列時,每列通電批次的「行為測試或正向約束=」值應是「範本 T0」到「範本 T5」、「未接(儀器批)」、「未接(架構測試後續計劃)」、「未接(Ktor 範本後續)」、「不接(代碼審或真機)」之一,應不再出現「批五」;各值的列數應等於本計劃〈範圍〉兩張清單(範本 32、儀器批 25、架構測試後續計劃 3、Ktor 1、代碼審或真機 7),各範本組的列應等於〈做〉表那一組列的編號。(已被 [[Projects/Android儀器測試範本與架構測試_計劃]] S1 取代,那支測試的期望以後半為準) [test:t_kotlin_catalog_c_rows_batch_resolved]
- [S3] 當在實驗專案照〈實驗專案骨架〉逐格跑 Gradle 測試時,每格每支測試的結果應等於矩陣寫的結果,小節裡每支 `@Test` 應都在矩陣出現,〈測試〉列的每個紅經 `assertion_failure` 判定應是斷言失敗;T0 的 TEST-9、T1、T2、T4 每格重跑 20 次結果應不變;結果與 JUnit XML 摘要應寫進驗證紀錄。 [manual:在會談暫存區照骨架組專案逐格跑 Gradle,記每格結果、失敗型別與重跑次數]
- [S4] 當 T4 在 OkHttp 4.12.0 配 `mockwebserver:4.12.0`、OkHttp 5.5.1 配 `mockwebserver3:5.5.1` 各跑一次時,兩次的矩陣結果應相同;OkHttp 4.12.0 配 `mockwebserver3:5.5.1` 的那次應記下失敗訊息。 [manual:在會談暫存區換兩組依賴各跑 T4 一次,結果寫進驗證紀錄]
- [S5] 當讀 kotlin-idioms 的 SKILL.md 與測試品質標準〈Android 本機單元測試的驗收標準〉時,前者開頭段應提到 `test-templates.md`,後者的協程與 Flow 兩小段應各有一句提到它;型錄〈輸入與口徑〉應有提到範本檔的那一句。 [test:t_kotlin_test_templates_linked]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 真的型錄與範本檔 | 零問題 | 本計劃〈做法〉3;使用者要求型錄每列指得到範本 |
| S1 | 型錄 API-1 的通電批次改成「行為測試或正向約束=範本 T9」 | 報 (API-1, 範本檔沒有 T9 節) | 本計劃〈做法〉3 |
| S1 | 範本檔刪掉 `## T2 Flow 發射` 那一節 | 報引用 T2 的 7 列,每列一筆 | 本計劃〈做法〉3 |
| S1 | 範本檔不存在 | 報一筆 (<templates>, 找不到範本檔) | 本計劃〈做法〉3 |
| S2 | 型錄 TEST-4 列 | 通電批次含「行為測試或正向約束=範本 T0」 | 本計劃〈做〉表 T0 |
| S2 | 型錄 STATE-17 列 | 通電批次含「行為測試或正向約束=未接(儀器批)」 | 本計劃〈不做〉儀器批;r1 可行性席實跑 |
| S2 | 型錄 API-9 列 | 通電批次含「行為測試或正向約束=未接(架構測試後續計劃)」 | 決策 d4 |
| S2 | 型錄 API-30 列 | 通電批次含「行為測試或正向約束=未接(Ktor 範本後續)」 | 本計劃〈不做〉Ktor |
| S2 | 型錄 PERF-1 列 | 通電批次含「行為測試或正向約束=不接(代碼審或真機)」 | 本計劃〈不做〉七列 |
| S2 | 型錄 68 列 C 列 | 範本 32、儀器批 25、架構測試後續計劃 3、Ktor 1、代碼審或真機 7,沒有「批五」 | 本計劃〈範圍〉 |
| S3 | T1〈測試〉×〈壞寫法:API-1 依序呼叫〉 | 斷言紅 independent_calls_run_in_parallel「expected:<1000> but was:<2000>」,其他支綠 | 調研 2026-11-06 實跑訊息;developer.android.com/kotlin/coroutines/test「it will automatically skip any delays」 |
| S3 | T1〈測試:API-4 連坐版〉×〈好寫法:API-4 不連坐〉 | 斷言紅(連坐版那支) | 決策 d1 |
| S3 | T4〈測試〉×〈壞寫法:API-26 204 解析 body〉 | 斷言紅 delete_204_is_success(不是 IllegalArgumentException) | 調研實跑是例外紅;本計劃實驗 E1 |
| S3 | T0〈壞測試:TEST-4 沒推進就斷言〉×〈正確程式〉,MainDispatcherRule 明傳 StandardTestDispatcher | 斷言紅(錯紅) | developer.android.com/kotlin/coroutines/test「advanceUntilIdle … This is a good default choice」;r1 依據席 F1 |
| S3 | T2〈測試〉×〈壞寫法:FLOW-23 空流 first()〉 | 斷言紅(不是 NoSuchElementException) | kotlinlang.org first.html「Throws NoSuchElementException if the flow was empty」;r1 依據席 F5 |
| S4 | T4,OkHttp 4.12.0 配 mockwebserver 4.12.0 | 矩陣結果同 OkHttp 5.5.1 配 mockwebserver3 5.5.1 | r1 通才席 F9 |
| S5 | kotlin-idioms SKILL.md | 開頭段含 `test-templates.md` | 本計劃〈做法〉4 |

## 回退

退回本計劃的提交即可,逐項是:刪範本檔 `skills/kotlin-idioms/test-templates.md`;`check.py` 拿掉 `template_problems` 與 `catalog_problems` 裡呼叫它的那一行;測試輔助 `_ktpack` 不再複製範本檔;拿掉 `t_kotlin_test_templates_sections`、`t_kotlin_catalog_c_rows_batch_resolved`、`t_kotlin_test_templates_linked`;型錄 68 列的「行為測試或正向約束=」值改回「批五」、〈輸入與口徑〉那兩句拿掉;kotlin-idioms `SKILL.md` 與測試品質標準的指路句拿掉;[[Systems/kotlin規則包]] 的 about_code 拿掉範本檔、那一行說明拿掉;[[Systems/test-quality-cli]] 那一行拿掉;實作時新增的驗證紀錄保留當歷史,但把它的狀態改成作廢並註明計劃已退回(不刪,免得它連回的計劃留下斷鏈的另一頭)。不碰任何帳本。

## 天花板

1. 範本的紅綠只在實驗專案驗過;消費專案照抄改名後寫錯,本 repo 的測試看不出來(CI 不跑 Gradle),只能靠消費專案自己跑與代碼審。
2. 範本證的是「這種寫法的測試抓得到這種錯」,不證消費專案的程式沒有這種錯——專案沒照範本寫測試,這 32 列就沒有接上。
3. API-4 的「該不該連坐」、API-10 的「該不該防重複」是業務決定:API-4 範本給兩個版本不設預設,API-10 預設只打一次並附冪等鍵版;選錯的話測試照綠。
4. API-21 只驗「重試有上限」那一半;「多個請求同時收到 401 時要加鎖、已被別人刷新就用新的」那一半要真的多執行緒同時打,單執行緒的測試派發器測不出,範本不涵蓋,靠代碼審。
5. API-10 範本驗的是 ViewModel 層連呼兩次 `submit()`;另一種標準寫法「`isSubmitting` 加按鈕 `enabled`」擋在畫面層,要 Compose UI 測試才驗得到(儀器批)。
6. 自檢只驗「型錄寫的範本組在範本檔有那一節」,不驗那一節真的涵蓋那一列的測法;那一半靠矩陣與驗證紀錄。

## 依據來源

每個機制一行:機制|依據|網址或實測|在哪看得到。標「調研開頁」的是 2026-11-06 調研時用 WebFetch 打開、確認頁面寫了那個測法的原文;「本次開頁」是寫這份計劃時再開一次;「r1 依據席核對」是設計審第一輪依據席逐頁重開過、逐字符合的;標「旁證」的是頁面沒寫到範本依賴的那一句,只能靠實驗補。

- T0 斷言前推進|官方「advanceUntilIdle … This is a good default choice」「If your test focuses on concurrency, prefer using StandardTestDispatcher」|https://developer.android.com/kotlin/coroutines/test(調研開頁;r1 依據席核對)|範本檔 T0 節、TEST-4/TEST-14
- T0 換測試 dispatcher|官方「In tests, replace real dispatchers with instances of TestDispatchers」|同上|TEST-9、`MainDispatcherRule`
- T0 Unconfined 不跑完|官方「this doesn't mean that it'll run them to completion eagerly」|同上|TEST-14
- T0 MainDispatcherRule 明傳 Standard|nowinandroid 原檔預設 `UnconfinedTestDispatcher()`,官方範例也是;既有標準「預設用 `StandardTestDispatcher`」|https://raw.githubusercontent.com/android/nowinandroid/main/core/testing/src/main/kotlin/com/google/samples/apps/nowinandroid/core/testing/util/MainDispatcherRule.kt (r1 依據席開頁);`skills/lumos-project-notes/commands/test-quality-standard.md`〈Android 本機單元測試的驗收標準〉協程段|範本檔 T0、實驗 E4
- T0 stateIn 要收集者|官方「there must be at least one collector present during the test」|https://developer.android.com/kotlin/flow/test(調研開頁;r1 依據席核對)|TEST-6
- T0 backgroundScope|官方「ensures that the coroutine gets cancelled before the end of the test」|同上|TEST-5、TEST-17
- T0 StateFlow 斷言 value|官方「we generally recommend treating StateFlow as a data holder and asserting on its value」|同上|TEST-7
- T0 Turbine 未消費事件會紅、收尾寫法|「Failing to consume all events before the end of a flow-based Turbine's validation block will fail your test」;型錄 TEST-18 標準寫法「`expectNoEvents()` 或明確 `cancelAndIgnoreRemainingEvents()`」;測試品質標準「每個發出的值都要收掉,或用 `cancelAndIgnoreRemainingEvents()` 明講不管」|https://github.com/cashapp/turbine(調研開頁;r1 依據席核對;Maven Central 現行 1.2.1);型錄 TEST-18 列;測試品質標準 Flow 段|TEST-18、TEST-19、TEST-20
- T1 虛擬時間跳過 delay|官方「it will automatically skip any delays in coroutines」「advanceTimeBy: Advances virtual time by the given amount」「There should only be one scheduler instance used in a test」|https://developer.android.com/kotlin/coroutines/test(調研開頁);本機實跑依序寫法 `expected:<1000> but was:<2000>`(調研 2026-11-06)|API-1、API-10、API-31、API-32
- T1 用 testScheduler.currentTime|實跑:`testScheduler.currentTime` 是成員屬性,只有 `ExperimentalCoroutinesApi` 警告;調研編譯失敗的是頂層擴充 `TestScope.currentTime`(缺 import)|調研 2026-11-06 實驗紀錄;r1 可行性席實跑 coroutines-test 1.10.2|範本檔 T1
- T1 逾時是取消的子類|API 頁原文「when coroutines finish with a CancellationException, the error does not get propagated to the parent」「may happen at any time, even after the block finishes executing but before the caller gets resumed with the result」「Values returned from withTimeout will typically be lost if the caller is cancelled」(代碼審 r1 改引:舊引句「The TimeoutCancellationException that is thrown by withTimeout is a subclass of CancellationException」「may happen at any time, even right before the return from inside of the timeout block」出自指南 cancellation-and-timeouts,那頁已改寫、無法複驗)|https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html(本次開頁;代碼審 r2 範本審逐字核對);舊出處 https://android.googlesource.com/platform/external/kotlinx.coroutines/+/refs/heads/main/docs/cancellation-and-timeouts.md|API-32、CO-14
- T1 重複 resume(旁證)|頁面只寫「Concurrent invocations of resume methods lead to a IllegalStateException」,沒寫依序 resume 兩次;r1 可行性席實跑依序兩次得 `IllegalStateException: Already resumed`|https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-cancellable-continuation/(調研開頁;r1 依據席核對);實驗 E6|API-34
- T1 produce 的父範圍等它結束(旁證)|頁面寫「The lifecycle of the parent [CoroutineScope] cannot end until this coroutine … completes」,沒寫 `send` 卡住會讓父範圍不結束,那是推論;r1 可行性席實跑 `backgroundScope` 加 `isCompleted` 的壞寫法是斷言紅|https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html(調研開頁);實驗 E6|FLOW-29
- T1 API-31 合併在途請求|型錄 API-31 標準寫法:共用 `Deferred` 加 mutex|`skills/kotlin-idioms/checks-catalog.md` API-31 列;決策 d5|範本檔 T1
- T2 Turbine 寫法|README 範例 `flowOf("one", "two").test { assertEquals("one", awaitItem()); awaitComplete() }`;官方「The third-party Turbine library offers a convenient API」|https://github.com/cashapp/turbine ;https://developer.android.com/kotlin/flow/test(調研開頁);API-8 本機實跑 `expected:<result:a[b]> but was:<result:a[]>`|API-8
- T2 StateFlow 合併相等值、不會結束|「suppress emission of the values to collectors when new value is equal」「State flow never completes」|https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/(調研開頁;r1 依據席核對)|STATE-10、FLOW-20
- T2 SharedFlow 無訂閱者丟值|「the emitted value is immediately lost」「Shared flow never completes」|…/kotlinx.coroutines.flow/-shared-flow/(同上)|FLOW-24、FLOW-20
- T2 shareIn|「every time it is collected a fresh connection is established」|…/kotlinx.coroutines.flow/share-in.html(同上)|FLOW-18
- T2 first 空流丟例外|「Throws NoSuchElementException if the flow was empty」|…/kotlinx.coroutines.flow/first.html(同上)|FLOW-23
- T2 combine 首發條件(旁證)|頁面只寫「combining the most recently emitted values by each flow」,沒明寫要每個來源先發過|…/kotlinx.coroutines.flow/combine.html(同上);實驗 E6 實證|FLOW-3
- STATE-17 移到儀器批|LiveData 頁「If you called this method multiple times before a main thread executed a posted task, only the last value would be dispatched.」;`InstantTaskExecutorRule`「executes each task synchronously」,在 `androidx.arch.core:core-testing`;純 JVM 解析失敗(r1 可行性席實跑 core-testing 2.2.0、lifecycle-livedata 2.9.4);`lifecycle-livedata-core` 模組檔只發 `.aar`|https://developer.android.com/reference/androidx/lifecycle/LiveData ;https://developer.android.com/reference/androidx/arch/core/executor/testing/InstantTaskExecutorRule(本次開頁;r1 依據席核對);https://dl.google.com/dl/android/maven2/androidx/lifecycle/lifecycle-livedata-core/2.9.0/lifecycle-livedata-core-2.9.0.module(r1 依據席讀)|〈不做〉儀器批
- T3 測 SavedStateHandle|「create a new instance of SavedStateHandle with the test values it requires and pass it to the ViewModel instance you are testing」「These values persist after the process is killed by the system」|https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate(本次開頁;r1 依據席核對);r1 可行性席純 JVM 實跑 `lifecycle-viewmodel-savedstate:2.9.4` 綠(要 `google()`)|STATE-6、STATE-26
- T3 純 JVM 可用、ViewModelScenario|Lifecycle 2.9.0 穩定版「The lifecycle-viewmodel-savedstate module is now KMP compatible including APIs like SavedStateHandle」;「A new androidx.lifecycle:lifecycle-viewmodel-testing KMP artifact … testing process death and recreation via recreate()」|https://developer.android.com/jetpack/androidx/releases/lifecycle(本次開頁;r1 依據席核對;Lifecycle 現行穩定版 2.11.0)|實驗 E5、測試品質標準「畫面重建與程序被回收」
- 實驗骨架要 google()|androidx 套件只發在 Google Maven;只有 `mavenCentral()` 時 `lifecycle-viewmodel-savedstate` 解析失敗|r1 可行性席實跑|範本檔〈實驗專案骨架〉
- STATE-20 不做的理由|Caution:「In Compose, SavedStateHandle only saves data written to it when the host Activity is stopped」|同 T3 頁|〈不做〉
- T4 MockWebServer|「MockResponse can be used to simulate a slow network」;依賴 `com.squareup.okhttp3:mockwebserver3:5.5.1`(README 只寫這一行,沒講跟舊版 `mockwebserver` 的差別,本次開頁);Maven Central 上 `com.squareup.okhttp3:mockwebserver` 與 `okhttp` 都有 4.12.0(本次查)|https://github.com/square/okhttp/tree/master/mockwebserver ;204 本機實跑 `IllegalArgumentException: EOF: empty body`(調研)|API-26、實驗 E7
- T4 真實 I/O 不用虛擬時間逾時|實跑 `runTest { withTimeout(5000) { withContext(Dispatchers.IO) { 真 OkHttp 讀節流回應 } } }` 立刻 `TimeoutCancellationException: Timed out after 5s of _virtual_ (kotlinx.coroutines.test) time`|r1 可行性席實跑|範本檔 T4
- T4 權杖刷新有上限|OkHttp `Authenticator.kt` KDoc「Returns null if the challenge cannot be satisfied」,範例 `while ((response = response.priorResponse()) != null)` 與「Give up, we've already failed to authenticate.」|okhttp 原始碼 KDoc https://github.com/square/okhttp/blob/master/okhttp/src/commonJvmAndroid/kotlin/okhttp3/Authenticator.kt (調研開頁;r1 依據席核對;代碼審 r1 換掉 404 的文件站網址、本次開頁)|API-21
- T4 權杖刷新要加鎖(代碼審 r1)|型錄 API-21 標準寫法 `mutex.withLock { if (token 已被別人刷新) 用新的 else refresh() }`(出處不全;Authenticator KDoc 沒提並行);Authenticator 跑在 OkHttp 執行緒、不是 suspend,範本用 `synchronized`;實跑 5 個並行 401:沒加鎖刷新 5 次、加鎖 1 次|型錄 API-21 列;驗證紀錄〈代碼審 r1 修正後重跑〉|範本檔 T4
- T5 序列化設定|coerceInputValues 套用「null inputs for non-nullable types」「unknown values for enums」;「the JSON encoder omits default property values」(encodeDefaults);kotlinx-serialization-json Maven Central 現行 1.12.0(本次查)|https://kotlinlang.org/docs/serialization-json-configuration.html(調研開頁;r1 依據席核對)|DATA-72、DATA-73、DATA-74
- 壞例紅要是斷言紅|收證工具只把斷言失敗算成抓到錯;判定函式 `assertion_failure`(`UncompletedCoroutinesError` 判非斷言)|`scripts/test_quality.py`;測試品質標準「被當掉抓到的錯不算」|〈用詞〉紅綠矩陣、實驗 E1
- 範本檔放法|照抄式範本用一般圍欄、節用標題(DDD 範本);放 `skills/kotlin-idioms/` 跟 `check.py` 讀的型錄同目錄|`skills/lumos-project-notes/commands/target-arch-ddd-template.md`;`configs/ast-grep/kotlin-android/check.py` 的 `CATALOG`|〈用詞〉範本檔
- 對應沿用通電批次欄|既有欄位、`catalog_problems` 已讀表檢查|`configs/ast-grep/kotlin-android/check.py`;r1 架構對齊席 F6|〈做法〉2、3
- 壞例不放 .kt 進 repo|規則包樣本被推送閘當產品碼擋過|[[Issues/Kotlin規則包代碼審放行的小問題]] 第 7 條|〈實務隱患〉
- K1–K3 移出|規則包同形三條、r1 兩席打穿點、Konsist 1.0.0-beta.1 發行說明(「resideIn* → residesIn*」、JVM 11、`kotlin-stdlib` 2.0.21、`scopeFromProduction` 只收 `src`)|https://github.com/LemonAppDev/konsist/releases(本次開頁;r1 依據席核對);`governance/review-reports/android行為測試範本與架構測試/`|〈不做〉、決策 d4
- Turbine 失敗型別(實作實驗)|README 範例輸出「app.cash.turbine.TurbineAssertionError: Unconsumed events found」;`TurbineAssertionError extends java.lang.AssertionError`(javap 讀 turbine-jvm 1.2.1);`awaitEvent()`、`cancelAndConsumeRemainingEvents()` 是 `ReceiveTurbine` 的公開方法;收證 `assertion_failure` 照型別名判、不認這個子類別|https://github.com/cashapp/turbine(本次開頁);實驗 E1 T0 兩格|範本檔〈怎麼用〉、T0、T2;測試品質標準 Flow 段指路句
- backgroundScope 不被 advanceUntilIdle 推進(實作實驗)|`advanceUntilIdle` 只推到前景沒有工作為止;`backgroundScope` 的工作要 `runCurrent()` 或 `advanceTimeBy()`|kotlinx-coroutines-test 1.10.2 `TestCoroutineScheduler.advanceUntilIdle` 原始碼(條件 `events.none(isForeground)`);實驗 FLOW-29、FLOW-18、FLOW-20、FLOW-24 格|範本檔〈怎麼用〉、T1、T2;測試品質標準協程段指路句
- ViewModelScenario 在純 JVM(實驗 E5)|`lifecycle-viewmodel-testing:2.9.4` 的 `viewModelScenario { … }.recreate()` 在純 JVM 還原 `SavedStateHandle` 內容,實跑綠/壞寫法斷言紅|驗證紀錄 [[Verification/2026-11-06_Android行為測試範本紅綠矩陣實跑]]|範本檔 T3〈測試:viewModelScenario 版〉(代碼審 r1 起不是預設版:Android 模組跑不起來)
- kotlinx-serialization 版本對 Kotlin(實作實驗)|發行說明 1.9.0「This release updates Kotlin version to 2.2.0」、1.12.0「This release is based on Kotlin 2.4.10」;1.12.0 配 Kotlin 2.2.21 實測編不過(metadata 2.4.0 vs 2.2.0)|https://github.com/Kotlin/kotlinx.serialization/releases(本次開頁)|範本檔 T4、T5〈依賴〉用 1.9.0
- OkHttp 主版本混用(實驗 E7)|OkHttp 4.12.0 配 mockwebserver3 5.5.1:不釘版本時 Gradle 把測試類別路徑的 OkHttp 升成 5.5.1;`strictly("4.12.0")` 時 `NoClassDefFoundError: okhttp3/internal/_UtilJvmKt`|實驗 E7,驗證紀錄|範本檔 T4 開頭說明
- API-4 摘句(代碼審 r1 改成原文)|「a failure or cancellation of a child does not propagate to the supervisor job or its other children」(舊引句不是逐字)|https://kotlinlang.org/docs/exception-handling.html(本次開頁)|範本檔 T1〈依據〉
- T3 在 Android 模組(代碼審 r1)|Android 本機單元測試跑在空殼 android.jar 上,`SavedState` 就是 `Bundle`;`viewModelScenario().recreate()` 例外紅 `Method containsKey in android.os.BaseBundle not mocked`,複製 handle 版綠/斷言紅|https://developer.android.com/training/testing/local-tests ;Android library 模組實跑(AGP 8.13.2)|範本檔 T3、測試品質標準「畫面重建與程序被回收」
- 測行為不測實作(代碼審 r1 先查世界)|斷言只驗型錄那列「後果」欄的可觀察行為;型錄有兩種以上標準寫法的,斷言要對每一種都成立|https://developer.android.com/training/testing/fundamentals ;Google Testing Blog「Test Behavior, Not Implementation」;`governance/review-reports/code-android行為測試範本/r1-intake.md`|範本檔 T1 CO-14、T2 FLOW-23、T5 DATA-72/74
- Turbine 等不到值也丟 TurbineAssertionError(代碼審 r1)|`awaitItem()` 等不到值 3 秒後丟 `TurbineAssertionError: No value produced in 3s`,收證不算斷言;〈測試〉一律推到靜止後 `cancelAndConsumeRemainingEvents()` 一次比|代碼審 r1 丙審實跑;驗證紀錄|範本檔〈怎麼用〉、T0、T2
- 剝圍欄照 CommonMark(代碼審 r2)|「The closing code fence must be at least as long as the opening fence」、圍欄標記縮排最多 3 格、收尾不帶 info string;check.py 零依賴不能 import scripts/lumos,刻意另一份、口徑跟 `_fence_regions`/`_visible_lines` 對齊|https://spec.commonmark.org/0.31.2/#fenced-code-blocks ;`scripts/lumos` 的 `_fence_regions`;`t_kotlin_template_fence_parity`|`configs/ast-grep/kotlin-android/check.py` 的 `_fence_regions`
- Turbine 會丟斷言錯的方法全表(代碼審 r2)|`awaitItem`、`awaitEvent`、`awaitComplete`、`awaitError`、`skipItems`、`expectNoEvents`、`expectMostRecentItem`、`ensureAllEventsConsumed`、`takeItem`、`takeEvent`、`takeComplete`、`takeError`;`test {}` 區塊結束的 Unconsumed events 檢查|turbine-jvm 1.2.1 sources(Maven Central `turbine-jvm-1.2.1-sources.jar` 的 `channel.kt`、`ReceiveTurbine.kt`、`Turbine.kt`、`flow.kt`)|`t_kotlin_test_templates_content_guards` 的 `_KT_TURBINE_THROWING`;範本〈怎麼用〉
- 取事件前先推進(代碼審 r2)|官方 Flow 測試頁的 `advanceUntilIdle` 用法;被測流會掛起時,不推就 `cancelAndConsumeRemainingEvents()` 只拿到一部分事件(實跑)|https://developer.android.com/kotlin/flow/test ;範本審 r2 實跑|範本 T0、守衛測試
- API-21 用 synchronized(旁證,代碼審 r2)|型錄寫 `mutex.withLock`;`Authenticator.authenticate(route: Route?, response: Response): Request?` 是一般函式、不是 suspend,用不了 `Mutex.withLock`——從方法簽名推出,OkHttp 文件沒寫並行刷新怎麼鎖|https://github.com/square/okhttp/blob/master/okhttp/src/commonJvmAndroid/kotlin/okhttp3/Authenticator.kt|範本 T4 好寫法
- DATA-74 比整個 JSON 值(代碼審 r2)|`JsonPrimitive.intOrNull` 會把 `"1"` 字串也讀成 1;改比 `JsonPrimitive(1)`,型別不同就不相等(實跑〈壞寫法:DATA-74 數量送成字串〉斷言紅)|範本審 r2 實跑;驗證紀錄|範本 T5
- 儀器批的依據(下一批用)|Room 遷移「you should include a test that covers all migrations」;Paging「the endOfPaginationReached property should be true」;WorkManager「use TestListenableWorkerBuilder」;Compose 無障礙「color contrast, small touch target size」;LeakCanary「automatically call LeakAssertions.assertNoLeaks()」|調研稿第二節 T6–T11 的網址(調研開頁)|〈不做〉;下一批計劃要把這幾行搬過去

## 待決問題

(開頭欄位的 Q1–Q4 都已決;這裡只放長版)

- Q1 API-4 一支失敗時連坐或不連坐 → 決策 d1:範本放兩個互斥版本,各配自己的好寫法,不設預設;採用時照第三批情境表態對那段程式的答案留一個。理由:型錄這列級是 C+D,「一支壞了其他還要不要」是業務決定([[Projects/Android寫法語意情境表態與盲判_計劃]] 把它交給表態與盲判)。
- Q2 API-10、API-31 → 決策 d5(取代 d2):兩列分開斷言。API-10 預設「連呼兩次只打一次 API」,後端有冪等鍵時換冪等鍵版;API-31 斷言「多個呼叫端同時要同一份資料只打一次網路」。理由:API-31 是讀取流量合併,冪等鍵版本對它無效(r1 依據席 F2)。
- Q3 Konsist 換版、Q4 K1–K3 要不要做 → 決策 d4(取代 d3):整組移出本批,另開架構測試後續計劃。

## 審計修正紀錄

- 2026-11-06 由後半計劃結案:`REVISIT:2027-01-31 開「架構測試後續計劃」` 那行刪掉,K1–K3、儀器批 25 列與 API-30 由 [[Projects/Android儀器測試範本與架構測試_計劃]] 接手;本計劃 S2 的期望改以後半 S1 為準。

- 舊否決對照(2026-11-06 動筆時跑 `lumos rejections`,453 行,按概念比對):沒有撞到本案的否決;三條同向——[[Projects/Room資料庫測試守衛_計劃]] 否決「推送前故障注入(要編譯跑 Android 測試,太慢)」,本案也不在推送閘或 CI 跑 Gradle;[[Projects/Macrobenchmark退步提醒_計劃]] 否決「由 Lumos 呼叫 gradlew」,本案沒有任何程式執行 Gradle;[[Projects/Android逐層診斷_計劃]] 否決「skill 目錄附一支 rerun.sh 讓消費專案直接呼叫」(收據會綁工具鏈安裝位置),本案的範本是給 AI 讀了照抄改名的文字,消費專案不呼叫工具鏈裡的檔。
- r1(2026-11-06,4 席:通才、可行性、依據、架構對齊,全 sonnet):43 條/blocking 21/四樣新東西(圍欄標頭、`--lab`、兩種認領語法、K1–K3 加換版)吃掉多數 major,全部拿掉或移出,範本改照 DDD 範本寫法、對應沿用通電批次欄,另修 MainDispatcherRule、Turbine 收尾、API-10/31 拆開、例外紅清單、OkHttp 主版本等範本內容。
- 席報告與編排者裁決:`governance/review-reports/android行為測試範本與架構測試/`(四份 `r1-*-sonnet.md` 與 `r1-intake.md`)。不加新機制的最小解:編排者在 r1-intake〈先查世界與裁決〉逐項寫了;這輪折入只減不加——唯一新增的是一支資料測試(S2,原 S8 綁的既有測試驗不到那件事)。

### r1 逐條去向

| 席與編號 | 嚴重度 | 去向 |
|---|---|---|
| 通才 F1 互斥斷言同一圍欄 | major | 折:〈用詞〉範本檔與矩陣改成「測試小節 × 程式小節」,API-4、API-10 冪等鍵版各自一個測試小節配自己的好寫法(〈做法〉1 T1) |
| 通才 F2 同組多份 bad 無法區分 | major | 折:壞寫法各自一個小節、標題寫變體名,矩陣用小節標題當欄名(〈用詞〉) |
| 通才 F3 Gradle 檔沒有來源 | major | 折:範本檔開頭加〈實驗專案骨架〉全文;〈假依賴〉放 src/test、被測程式放 src/main;`--lab` 與「逐字等於」條款拿掉 |
| 通才 F4 K3 sealed UiState 漏報 | major | 移出:K1–K3 整組移到〈不做〉,打穿點寫進理由(決策 d4) |
| 通才 F5 K1 函式內建 scope 漏報、appScope 誤報 | major | 移出:同上 |
| 通才 F6 K2 DI 模組誤報、CO-5 驗不到 | major | 移出:同上 |
| 通才 F7 d3 退路與 S5 矛盾 | major | 作廢:d3 由 d4 取代,原 S5 隨 K 組拿掉 |
| 通才 F8 `_arch_tpl_konsist_test` 重核沒條款 | major | 移出:Konsist 換版整組移到後續計劃,〈不做〉寫明那支要跟著重核 |
| 通才 F9 mockwebserver3 對 OkHttp 4 專案 | major | 折:〈做法〉1 T4 照主版本挑依賴與 import;實驗 E7;條款 S4;〈實務隱患〉 |
| 通才 F10 半移狀態抓不到、31 寫死 | minor | 折:對應改成型錄欄位自己寫組代號,沒有第二處可漂移;S2 照新範圍列數驗,移出時同一提交改值(〈做法〉2) |
| 通才 F11 回退漏列 | minor | 折:〈回退〉逐項補齊(測試輔助、三支測試、兩篇 Systems、驗證紀錄的處理) |
| 通才 F12 template 測試沒全進矩陣、抽取規則 | minor | 折:〈用詞〉紅綠矩陣「小節裡每一支 @Test 都要出現在矩陣」、S3;抽取規則隨 `--lab` 拿掉 |
| 通才 F13 T4 重跑沒涵蓋 | minor | 折:E3 與 S3 涵蓋 T4(API-30 慢速 body 已移出) |
| 可行性 F1 只有 mavenCentral 解析失敗、骨架沒人寫 | major | 折:〈實驗專案骨架〉repositories 含 `google()`;〈實務隱患〉對外送出那行改寫 |
| 可行性 F2 STATE-17 純 JVM 編不過 | major | 移出:STATE-17 移到儀器批,型錄改「未接(儀器批)」 |
| 可行性 F3 T4 虛擬時間逾時 | major | 折:〈做法〉1 T4 不在虛擬時間用 `withTimeout`、真實等待包 `Dispatchers.Default`;API-30 慢速 body 移出;依據節加實跑 |
| 可行性 F4 K1 函式內與 rememberCoroutineScope | major | 移出:K 組移到〈不做〉 |
| 可行性 F5 K3 sealed UiState | major | 移出:同上 |
| 可行性 F6 K3 java. 型別判法 | minor | 移出:同上 |
| 可行性 F7 圍欄沒有變體、support 落點 | minor | 折:同通才 F2、F3 |
| 可行性 F8 currentTime 說法 | minor | 折:〈做法〉1 T1 改寫成員屬性與擴充的差別、加 `@OptIn`;依據節同步 |
| 依據 F1 MainDispatcherRule 預設 Unconfined | major | 折:PRIOR-ART ①、〈做法〉1 T0 明傳 StandardTestDispatcher;實驗 E4;依據節新增一行 |
| 依據 F2 API-31 與 API-10 併同一斷言 | major | 折:d2 由 d5 取代,兩列分開斷言(〈做法〉1 T1);天花板 5 補 `isSubmitting` 那半 |
| 依據 F3 API-30 Ktor 驗不到 | major | 移出:API-30 移到〈不做〉Ktor,寫明選移出不選改寫的理由 |
| 依據 F4 Turbine 收尾跟型錄與標準矛盾 | major | 折:PRIOR-ART ⑤、〈做法〉1 T0 對齊 TEST-18 與標準;依據節合併成一行 |
| 依據 F5 例外紅清單漏 FLOW-23、DATA-72、FLOW-20 | major | 折:E1 清單補齊並加 API-21;〈做法〉1 T2、T5 寫處理法 |
| 依據 F6 重跑沒涵蓋 TEST-9 與 T4 | major | 折:E3、S3 涵蓋 T0 的 TEST-9 與 T4 |
| 依據 F7 S8 綁的既有測試驗不到 | major | 折:改綁新測試 `t_kotlin_catalog_c_rows_batch_resolved`(S2) |
| 依據 F8 STATE-17 失敗原因寫錯 | minor | 折:隨 STATE-17 移出,〈不做〉寫對原因(純 JVM 解析不到) |
| 依據 F9 E5 前提用 alpha 說法 | minor | 折:E5 與依據節改用 2.9.0 穩定版的 KMP 說法 |
| 依據 F10 cancellation-and-timeouts 無法複驗 | minor | 折:依據節補網址並標「無法複驗」,以實驗格子當實證 |
| 依據 F11 三行出處只是旁證 | minor | 折:依據節 API-34、FLOW-29、FLOW-3 標「旁證」,E6 擴大到三列 |
| 依據 F12 API-21 加鎖那半 | minor | 折:寫進〈天花板〉4 |
| 依據 F13 規則數 9 改 12 沒列同步 | minor | 移出:K 組不做,規則數不變 |
| 依據 F14 d3 退路與 S5 | minor | 作廢:同通才 F7 |
| 依據 F15 lands_in 對不上 | minor | 折:lands_in 拿掉 android-arch-template;留 kotlin規則包(check.py、型錄、範本檔)與 test-quality-cli(測試品質標準指路句,上一份 Android 單元測試標準計劃落在那篇);〈做法〉6 寫明 |
| 架構對齊 F1 引錯鄰居 | minor | 折:PRIOR-ART ② 與依據節改引同目錄的型錄當放置依據 |
| 架構對齊 F2 `--lab` 讓唯讀自檢寫檔 | major | 折:拿掉 `--lab`(〈不做〉) |
| 架構對齊 F3 check.py 要解析產生器資料檔 | minor | 移出:K 組不做,`// 型錄:` 拿掉,check.py 不讀產生器資料檔 |
| 架構對齊 F4 圍欄資訊字串是第二種區塊格式 | major | 折:改一般 ```kotlin 圍欄、節用標題,照 DDD 範本 |
| 架構對齊 F5 回傳形狀與掛載點、`_ktpack` 複製不到 | minor | 折:〈做法〉3 寫明回 `(列編號, 原因)`、由 `catalog_problems` 呼叫、`_ktpack` 多複製範本檔 |
| 架構對齊 F6 另造兩種認領語法 | major | 折:拿掉 `涵蓋:` 與 `// 型錄:`,沿用通電批次欄 |
| 架構對齊 F7 MainDispatcherRule 借用對得上 | minor | 折:保留借用並寫明來源,另依依據 F1 改明傳 Standard |

### 實作(2026-11-06,實驗推翻與改法)

- 實驗 57 格、20 次重跑全照矩陣,細節在 [[Verification/2026-11-06_Android行為測試範本紅綠矩陣實跑]];沒有列被移出,型錄 68 列照〈範圍〉兩張清單改值。
- E1 推翻〈做法〉1 T0「錯誤用 `awaitError()`」與 Turbine 收尾寫法:`awaitComplete()`、`awaitError()`、`expectNoEvents()` 失敗丟 `app.cash.turbine.TurbineAssertionError`,收證工具不算斷言(本計劃不改收證判定)。先查世界:Turbine README 範例輸出就是這個型別、1.2.1 公開 API 有 `awaitEvent()` 與 `cancelAndConsumeRemainingEvents()`;改法是取出事件再用 kotlin.test 斷言,範本〈怎麼用〉與測試品質標準 Flow 段寫明。收證工具要不要認 Turbine 的型別留給收證工具自己的計劃(本批不動,記在 [[Systems/kotlin規則包]] 的 PITFALL)。
- 實作發現:`backgroundScope` 的工作 `advanceUntilIdle()` 不推(只推前景),用 `runCurrent()`;寫進範本與測試品質標準協程段。
- E2 抓到 DATA-73 壞寫法連帶紅 DATA-72 那支(測試 JSON 沒帶 status),改測試 JSON 只讓 name 缺。
- E5 成立:T3〈測試〉改用 `ViewModelScenario.recreate()`,複製 handle 的版本留作舊 lifecycle 的退路。(**已被代碼審 r1 推翻**:T3 預設改回複製 handle 版,見下方〈代碼審 r1〉)
- 依賴:kotlinx-serialization-json 1.12.0 配 Kotlin 2.2.21 編不過,範本用 1.9.0;API-26 用 Retrofit 3.0.0。範本的組法比〈用詞〉多一條規矩:〈壞寫法〉小節只寫被換掉的那段,實驗格子的被測程式=〈好寫法〉各段再用同名開頭宣告的段換掉,寫在範本〈實驗專案骨架〉;T4 依主版本各一份〈依賴:OkHttp 4/5〉。

### 代碼審 r1(2026-11-06,4 席:甲審、乙審、丙審、架構對齊,全 sonnet,21 條、會擋 5 條)

先查世界(編排者 r1-intake):兩類對稱問題——斷言比型錄那列要的多(寫死某一種標準寫法,誤紅另一種)與比要的少(只驗一次或一半,放過壞寫法變形);照「測行為不測實作」,每支只斷言「後果」欄的可觀察行為,型錄有兩種標準寫法的兩種都要綠,並把席位的變形實跑進矩陣。卷證 `governance/review-reports/code-android行為測試範本/`,修正紀錄 r1-fix.json。

| 席與編號 | 嚴重度 | 去向 |
|---|---|---|
| 丙 F1 T3 在 Android 模組跑不起來 | major | 折:預設〈測試〉改複製 handle 版,viewModelScenario 版標只在純 JVM/KMP,兩版不涵蓋什麼寫在節開頭;Android library 模組實跑;測試品質標準「畫面重建」那條同步改 |
| 丙 F2 API-21 沒測加鎖、好寫法沒鎖 | major | 折:好寫法加 `synchronized` 與「別人已刷新就用新的」,新測試並行 5 個 401 只刷新一次且都成功,壞寫法加「沒加鎖」「不刷新直接放棄」 |
| 丙 F3 DATA-72 寫死預設值 | major | 折:只斷言整份解得出來,加〈好寫法:DATA-72 可空加 null 預設〉 |
| 乙 F1 TEST-6 只取一次快照照綠 | major | 折:收集開始後改兩次值,加〈壞寫法:TEST-6 只取一次快照〉 |
| 乙 F2 CO-14 寫死逾時回 true | major | 折:拿掉結果斷言(由專案表態),加〈好寫法:CO-14 區塊內 try/finally〉 |
| 乙 F3 有限流 expectNoEvents 誤紅 | minor | 折:〈怎麼用〉坑一條 |
| 乙 F4 TEST-9 用 Main 自建 scope 照綠 | minor | 折:新測試「注入的 scope 取消後工作跟著停」,加〈壞寫法:TEST-9 自建 scope 用 Dispatchers.Main〉 |
| 乙 F5 API-4 摘句不是原文 | minor | 折:換成原文 |
| 乙 F6 API-32/CO-14 摘句無法複驗 | minor | 折:改引 withTimeout API 頁原文(本次開頁) |
| 乙 F7 其餘依據(data object 前提) | minor | 折:〈怎麼用〉寫明 data object 要 Kotlin 1.9 |
| 丙 F4 Turbine 漏事件不算斷言 | minor | 折:〈測試〉全改 `cancelAndConsumeRemainingEvents()` 一次比;新守衛測試 `t_kotlin_test_templates_content_guards` 擋〈測試〉用 Turbine 自己的檢查 |
| 丙 F5 複製版不涵蓋 provider | minor | 折:節開頭寫明,矩陣加〈好寫法:STATE-6 用 setSavedStateProvider〉兩格(複製版誤紅照列、viewModelScenario 版綠) |
| 丙 F6 不驗 Bundle 型別、Compose 寫入時機 | minor | 折:節開頭寫明兩版都不涵蓋 |
| 丙 F7 FLOW-18 假上游不掛起 | minor | 折:假 API 加 delay,加〈壞寫法:FLOW-18 沒同步的快取〉 |
| 丙 F8 FLOW-23/DATA-74 斷言過窄 | minor | 折:FLOW-23 收 null 或空字串並加好寫法變形;DATA-74 解回 JSON 比值,加〈壞寫法:DATA-74 預設值寫錯〉與〈好寫法:DATA-74 整個 Json 開 encodeDefaults〉 |
| 丙 F9 API-21 依據網址 404 | minor | 折:換 GitHub 原始碼網址(本次開頁) |
| 甲 F1 圍欄裡的假標題 | minor | 折:check.py 比對前剝程式圍欄,整行 `## T<n>` 也認 |
| 甲 F2 編碼錯丟例外 | minor | 折:回 (`<templates>`, 範本檔不是 UTF-8…) |
| 甲 F3 標準新舊 Turbine 句衝突、指路測試只比檔名 | minor | 折:舊句補一句指到收證那條;`t_kotlin_test_templates_linked` 驗連結目標存在、兩個坑的關鍵字、畫面重建那條 |
| 架 F1 主表讀兩次 | minor | 折:`catalog_problems` 把讀好的列傳給 `template_problems(rows)`,單獨呼叫才走 `main_rows()` |
| 架 F2 通電批次兩套口徑 | minor | 折:check.py 只認「行為測試或正向約束=」那段(`behavior_value`),跟測試同口徑 |

### 代碼審 r2(2026-11-06,修訂輪,3 席:範本審、其他審、架構對齊,全 sonnet,16 條、會擋 3 條)

先查世界(編排者 r2-intake):二範1 是上一輪修補自己帶進的退步(範本寫了「先推到靜止」,兩支漏做),照官方 Flow 測試頁補推進,並在守衛測試機械檢查「每個 `cancelAndConsumeRemainingEvents()` 之前同一 `test {}` 區塊有推進」;二架2 剝圍欄照 CommonMark 實作、刻意另一份並加對照測試防漂移。卷證 `governance/review-reports/code-android行為測試範本/`,修正紀錄 r2-fix.json。

| 席與編號 | 嚴重度 | 去向 |
|---|---|---|
| 範 F1(二範1)新 Turbine 讀法對掛起的 save 誤紅 | major | 折:兩支 save 測試取事件前 `advanceUntilIdle()`;矩陣加〈好寫法:TEST-18 save 會掛起〉;守衛測試檢查推進 |
| 範 F2(二範2)API-31 永久快取照綠 | major | 折:第一批完成後再 refresh 一次斷言共打兩次;加〈壞寫法:API-31 結果永久快取〉 |
| 範 F3(二範3)FLOW-23 沒正向路徑 | minor | 折:加 `name("1")` 要回 "Ada";加〈壞寫法:FLOW-23 不查直接回 null〉 |
| 範 F4(二範4)DATA-74 字串照綠、synchronized 沒出處 | minor | 折:比 `JsonPrimitive(1)`;加〈壞寫法:DATA-74 數量送成字串〉;synchronized 那句標旁證、依據改寫成方法簽名推論 |
| 範 F5(二範5)其餘變形驗過 | minor | 確認:席位實跑的合法與壞變形結果都符合,不另改 |
| 其 F1(二其1)~~~ 與未閉合圍欄沒測 | minor | 折:`t_kotlin_test_templates_sections` 加 `~~~`、四反引號包三反引號、縮排 4 格、檔尾未閉合;`t_kotlin_template_fence_parity` 同組輸入比 lumos |
| 其 F2(二其2)非標準「範本」寫法靜默略過 | minor | 折:`template_problems` 對以「範本」開頭但不是「範本 T<n>」整段的值報格式錯 |
| 其 F3(二其3)Turbine 禁用名單不全 | minor | 折:照 Turbine 1.2.1 原始碼列全 12 個方法,另檢查每個 `test {}` 區塊用 `cancelAndConsumeRemainingEvents()` 收尾 |
| 其 F4(二其4)〈做法〉3 沒同步 | minor | 折:〈做法〉3 改寫成現況 |
| 其 F5(二其5)E5 條文沒標過期 | minor | 折:計劃 E5、〈實作〉那行與驗證紀錄 E5 都標「已被代碼審 r1 推翻」 |
| 其 F6(二其6)Systems/test-quality-cli 沒記 r1 改動 | minor | 折:那篇正文補 r1 三處改動(另一個提交,按家拆) |
| 其 F7(二其7)依據表一行多一欄 | minor | 折:T1 逾時那行併回四欄 |
| 架 F1(二架1)主表三份解析 | minor | 折:`catalog_problems` 改用 `main_rows`(編號重複、欄位數也在那裡報),測試直接呼叫 `m.main_rows()` |
| 架 F2(二架2)第二份剝圍欄口徑分岔 | major | 折:照 CommonMark 與 lumos `_fence_regions` 重寫,註解寫明刻意另一份的理由,加對照測試 |
| 架 F3(二架3)批次值正則抄兩份 | minor | 折:測試改呼叫 `m.behavior_value` |
| 架 F4(二架4)標題規則測試端另一套 | minor | 折:check.py 抽出 `TEMPLATE_HEADING_RE`、`template_sections`,測試切段呼叫它;取 kotlin 程式塊改用 `_fence_regions`,不用成對非貪婪正則 |
