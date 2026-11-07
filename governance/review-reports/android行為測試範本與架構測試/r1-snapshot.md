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
  - Systems/android-arch-template
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
    decision: "#d2"
  - id: Q3
    text: Konsist 要不要現在換成 1.0.0-beta.1(2026-11-04 發的 beta,resideIn 改名讓舊產出編不過)?建議:換,0.17.3 的理由(0.18 綁 Kotlin 2.4)已被它撤掉;不換就等 1.0.0 正式版、K1–K3 只用兩版都有的 API
    class: 依賴
    stage: 架構
    status: 已決
    decision: "#d3"
  - id: Q4
    text: K1–K3 跟規則包的 kt-unmanaged-scope-launch、kt-hardcoded-dispatchers-io、kt-uistate-mutable-field 形狀重複,還要不要做?自答:做;規則包只看新增行、要宣告且裝 ast-grep,K 測試跑在專案自己的單元測試、看整個目標範圍
    class: 範圍
    stage: 架構
    status: 自答
    source: "[[Projects/Android協程與API寫法機械檢查標準_計劃]]〈分批〉批五寫明擴充 arch-template;本計劃〈實務隱患〉K 測試跟規則包重複"
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
    valid: true
  - content: Q3:Konsist 換 1.0.0-beta.1,條件是實作時 K1–K3 與既有產出逐條編譯過;編不過就留 0.17.3 並記 Issue
    id: d3
    context: 0.17.3 的理由(0.18 綁 Kotlin 2.4)已被 1.0.0-beta.1 撤掉,但它是 beta
    why_chosen: 編排者代裁,依使用者授權原話「我要睡了，你有裁量權、簽核權」「你的標準、最佳寫法來源要有依據，不要你自己寫」;官方安裝頁現寫 1.0.0-beta.1,附編譯驗證當退路
    decided: 2026-11-06
    valid: true
---
# Android行為測試範本與架構測試_計劃

> 白話:型錄 `skills/kotlin-idioms/checks-catalog.md` 裡有 68 列「長相看不出錯、要跑起來才知道」的寫法(級含 C),目前只寫了「批五再接」。這份計劃替其中在電腦 JVM 上就跑得動的 34 列做測試範本(每組附「好寫法綠、壞寫法紅」的對照,實作時真的跑一次),另把 3 列做成 Konsist 架構測試補進 `lumos arch-template android` 的產出;要模擬器的 24 列與只能代碼審或真機的 7 列明寫這批不做與理由。範本跟型錄用編號對得上,由型錄的自我檢查機械驗。是 [[Projects/Android協程與API寫法機械檢查標準_計劃]] 分批表的第五批。

立案:使用者 2026-11-06 原話「遵照上面三個要點，完成這五個批次功能，目標是把Android靜態能先掃描的實務隱患都先處理過」,三要點是「1.實作連續被打穿、或顯著無法收斂，就上網印證方向、業界實作找最佳解 2.所有機制都要實驗一遍，看看可行性、有沒有漏洞，修的流程遵照第一條 3.Android的規則也一樣，來源、依據，這可以在語意盲判的時候起到輔助判別的作用」,另一句「我們開發的過程中，所有機制的依據來源，最後也要補回plan，方便後續迭代」。輸入是 2026-11-06 的第五批調研稿(68 列分類、T0–T11 範本組、K1–K5 架構測試、本機實驗),調研稿放在會談暫存區,本計劃把要用的結論與已開頁核對的原文搬進〈依據來源〉,不靠那份暫存稿。

PRIOR-ART: ①測試寫法全照官方:Android 協程測試頁與 Flow 測試頁(`runTest`、`StandardTestDispatcher`、`backgroundScope`、`advanceUntilIdle`)、kotlinx.coroutines API 文件、Turbine README、OkHttp MockWebServer README、kotlinx.serialization JSON 設定頁、Android SavedStateHandle 頁;`MainDispatcherRule` 照 nowinandroid `core/testing` 同名類別。②「範本放技能文件、由 AI 照抄改名」照 DDD 與前端兩份目標架構範本的既有做法(沒有開關需求的範本照抄,有開關的才用產生器,見 [[Projects/Android目標架構開關與舊檔畢業_計劃]]〈做法〉1);「Markdown 當單一資料來源、程式讀它」照 `scripts/templates/android-arch-target.md` 的做法;塊頭改用圍欄的資訊字串而不是 `===` 行,因為範本是給人與 AI 讀的文件,圍欄在一般 Markdown 檢視器裡會顯示成程式。③範本與型錄的對應由既有的型錄自我檢查 `configs/ast-grep/kotlin-android/check.py` 多驗一項,不另開檢查程式。④架構測試照 Konsist 官方 starter snippets(Android 與 clean architecture 兩頁)的 `hasImport`、`assertFalse` 形狀,加進既有產生器資料檔。⑤「每支範本附會紅的壞例」借 lumos 破壞測試與變異測試「拿掉保護要看到紅」的做法;紅要是斷言失敗才算,照測試品質標準〈Android 本機單元測試的驗收標準〉與收證工具 `scripts/test_quality.py` 的 `assertion_failure` 同一套判準。裁定:全借用,新寫的只有範本內容、一個抽出實驗專案的函式與型錄自檢的一項。
RETIRE-IF: 2027-05-06 人裁時,在消費專案的 git 歷史裡數照範本起手的測試檔(檔頭留了範本組代號的),全部專案加起來少於 5 支,就把範本檔降成 kotlin-idioms 裡的一段連結清單(只留官方頁連結),型錄自檢的範本對應那一項一起拿掉 [retire:人裁] [until:2027-05-06]。

## 用詞

- **型錄**:`skills/kotlin-idioms/checks-catalog.md`,473 列,欄位見它的〈輸入與口徑〉;本計劃只動「通電批次」欄與〈輸入與口徑〉一句。
- **C 列**:型錄「級」欄含 C 的列(68 列,2026-11-06 用 `check.py` 讀表數出);68 列的通電批次欄目前全都寫「行為測試或正向約束=批五」。
- **範本組**:一組同測法的測試範本,代號 T0–T5(本批做)、T6–T11(儀器批);架構測試代號 K1–K5。代號沿用調研稿,不重編;本批不做的那幾組:T6 Room 遷移與資料層、T7 Paging、T8 WorkManager、T9 Compose UI 測試(含 T9a 無障礙檢查)、T10 LeakCanary 儀器測試、T11 生命週期(Robolectric 或 TestLifecycleOwner);K4 Hilt 宿主(ARCH-56)、K5 每個 Migration 要有測試(DATA-19)。
- **範本檔**:`skills/kotlin-idioms/test-templates.md`(新增)。Markdown,一組一節;節裡用帶標頭的 Kotlin 圍欄放程式,標頭寫在圍欄開頭那一行的資訊字串:`kotlin T1 template`(消費專案照抄的測試)、`kotlin T1 badtest`(T0 才有:示範錯的測試寫法)、`kotlin T1 support`(假依賴等共用碼)、`kotlin T1 good`(照標準寫法的被測程式)、`kotlin T1 bad`(照型錄壞寫法的被測程式)、`kotlin T1 gradle`(實驗專案要的依賴行)。每節另有一行 `涵蓋:` 列型錄編號、每列一行 `依據:`(網址加原文摘句)、一張〈紅綠矩陣〉。
- **紅綠矩陣**:一組裡「哪一份測試 × 哪一份被測程式 → 應該是什麼結果」的表。結果只准三種:`綠`、`斷言紅 <測試名>「<訊息片段>」`、`逾時紅 <測試名>`;逾時紅只准出現在 `badtest` 那一列(示範錯的測試寫法會卡住),`template` 那一列的紅一律要是斷言紅——收證工具只把斷言失敗算成「測試抓到錯」,例外或逾時的紅不算(測試品質標準〈Android 本機單元測試的驗收標準〉的「被當掉抓到的錯不算」)。
- **實驗專案**:型錄自檢多一個入口 `check.py --lab <空資料夾>`,照範本檔把每個矩陣格子組成一個獨立的純 JVM Gradle 專案(`settings.gradle.kts`、`build.gradle.kts`、`src/main`、`src/test`),只寫檔不執行;跑 Gradle 是人或 AI 在實作時手動做,結果寫進驗證紀錄。
- **儀器批**:要 Android 模擬器、Robolectric 或 Android 建置外掛才跑得動的範本組(STATE-23 跟 T3 同主題「程序被殺還原」,但它驗 Compose `rememberSaveable` 要用 `StateRestorationTester`,得跑 Compose UI 測試,所以歸儀器批;另加 T6–T11),下一批另開計劃。
- **Konsist**:讀 Kotlin 原始碼的架構測試函式庫,跑在一般 JVM 單元測試裡;本 repo 的產生器 `lumos arch-template android` 從 `scripts/templates/android-arch-target.md` 組出它的測試檔。
- **K 測試**:本批補進產生器資料檔的三支 Konsist 測試(K1–K3)。

## 範圍

### 做(37 列)

| 組 | 型錄列 | 測法(一句) | 跑在哪 |
|---|---|---|---|
| T0 測試骨架守則 | TEST-4、TEST-5、TEST-6、TEST-7、TEST-9、TEST-14、TEST-17、TEST-18、TEST-19、TEST-20(10) | 正確的協程/Flow 測試起手式(`MainDispatcherRule`、`runTest`、`backgroundScope` 收集者、斷言前推進、Turbine 收完事件);矩陣是「好測試 vs 壞測試 × 正確程式 vs 埋錯程式」 | 純 JVM |
| T1 虛擬時間 | API-1、API-4、API-10、API-31、API-32、API-34、FLOW-29、CO-14(8) | 假依賴用 `delay` 模擬耗時,斷言 `testScheduler.currentTime`、呼叫次數、逾時後狀態 | 純 JVM |
| T2 Flow 發射 | API-8、FLOW-3、FLOW-18、FLOW-20、FLOW-23、FLOW-24、STATE-10、STATE-17(8) | Turbine `test { awaitItem() … }` 斷言收到哪幾筆、順序、有沒有多;共享類數上游被執行幾次 | 純 JVM(STATE-17 待實驗 E4) |
| T3 程序被殺還原(兩列) | STATE-6、STATE-26(2) | 同一份 `SavedStateHandle` 內容建第二個 ViewModel,斷言輸入與待處理 id 還在 | 純 JVM(待實驗 E5) |
| T4 HTTP 邊界 | API-21、API-26、API-30(3) | 真的 OkHttp/Retrofit 打本機 MockWebServer,排好 204、連續 401、慢速大 body | 純 JVM |
| T5 序列化契約 | DATA-72、DATA-73、DATA-74(3) | 用專案正式的 `Json {}` 實例解碼/編碼伺服器可能回的 JSON | 純 JVM |
| K1 不准無主協程 | API-9(1) | Konsist:範圍內不准 `GlobalScope`、不准類別裡當場建 `CoroutineScope(…)` | 純 JVM(Konsist) |
| K2 資料層 dispatcher 注入 | CO-5(1) | Konsist:`data` 套件的類別不在方法本體寫死 `Dispatchers.IO/Default` | 純 JVM(Konsist) |
| K3 UiState 不可變 | UI-39(1) | Konsist:`UiState` 結尾的類別屬性一律 `val`、不用可變集合、不帶 `java.` 型別 | 純 JVM(Konsist) |

做法:

1. **範本檔** `skills/kotlin-idioms/test-templates.md`(新增):開頭一段講怎麼用(找到型錄編號 → 搜這份檔 → 照抄 `template` 與 `support` 改名套進專案 → 依賴照 `gradle` 塊加 → 跑一次確認綠),照抄的測試檔第一行留一行註解 `// 起手:kotlin-idioms test-templates <組代號>`(RETIRE-IF 靠它數);每組一節,節的內容照〈用詞〉的範本檔。範本的程式碼要點(寫進範本、實驗驗過才算):
   - T0:`MainDispatcherRule` 屬性宣告在其他用到 dispatcher 的屬性前面;`stateIn(WhileSubscribed)` 先在 `backgroundScope` 掛空收集者;斷言 StateFlow 的最終 `value`,不逐一比中間值;Turbine 不用 `cancelAndIgnoreRemainingEvents` 吞事件、錯誤用 `awaitError`。
   - T1:虛擬時間讀 `testScheduler.currentTime`(調研第一次實跑用 `currentTime` 編譯失敗:它是另一個要 opt-in 的擴充);API-4 放兩個互斥的斷言版本、不設預設,範本註解寫「照情境表態的答案留一個、刪另一個」(決策 d1);API-10 與 API-31 預設斷言「連點兩次只打一次 API」,另附「後端有冪等鍵時兩次帶同一冪等鍵」的替代版(決策 d2);會丟例外的壞寫法(API-34 第二次 resume)用 `runCatching` 接住再斷言,讓紅成為斷言紅;FLOW-29 把被測函式放進 `backgroundScope.launch`、推進後斷言那個 Job `isCompleted`,不讓 `runTest` 自己卡到 60 秒逾時。
   - T2:STATE-10 斷言「同一則錯誤連發兩次,畫面收到兩個不同 id」;FLOW-18 數上游被執行幾次;FLOW-3 斷言第一筆是 Loading 而不是等到逾時。
   - T3:照官方「用測試值建新的 SavedStateHandle」,把第一個 ViewModel 寫過的 handle 內容複製成第二個 handle 再建 ViewModel;`ViewModelScenario.recreate()` 是否在純 JVM 可用看實驗 E5。
   - T4:204 與未知 enum 這類「壞寫法丟例外」的,一律 `runCatching` 後斷言成功,不讓例外直接把測試打紅;依賴 `mockwebserver3`。
   - T5:測試讀專案正式的 `Json` 設定物件(範本用 `AppJson` 佔位),不在測試裡另 new 一個。
2. **實驗專案抽出**:`configs/ast-grep/kotlin-android/check.py` 加 `--lab <空資料夾>` 入口與一支函式,照範本檔的矩陣每格寫一個子資料夾 `<組>-<測試份>-<程式份>/`;資料夾不是空的就拒絕(rc2、不寫任何檔);只寫檔不跑 Gradle。版本號寫在每組 `gradle` 塊,不寫死在程式裡。
3. **型錄自檢多一項** `template_problems()`(在同一支 `check.py`,掛在 `catalog_problems` 同一條路徑,`--catalog-only` 與完整模式都會跑;CI 會紅靠的是 S1、S2 的新測試直接呼叫它):
   - 正向:型錄裡通電批次欄含「行為測試或正向約束=批五」的每一列,要剛好被一處認領——範本檔某一節的 `涵蓋:` 行,或 `scripts/templates/android-arch-target.md` 某一支 `test` 塊裡的 `// 型錄:` 註解;被兩處認領、或沒人認領,都報。
   - 反向:`涵蓋:` 與 `// 型錄:` 列的每個編號都要在型錄主表、級含 C;不在或級不含 C 都報。
   - 形狀:每節有 `涵蓋:`、至少一行 `依據:` 帶網址、`template`/`support`/`good`/`bad`/`gradle` 五種圍欄(T0 多 `badtest`)各至少一個、一張矩陣;矩陣裡點名的測試名要在 `template` 或 `badtest` 圍欄裡找得到 `fun <名>(`;`template` 列的格子不准寫逾時紅;`template × good` 那格要是 `綠`。
4. **型錄改兩處**:①沒做的 31 列(儀器批 24 列、只能代碼審或真機的 7 列)通電批次欄把「行為測試或正向約束=批五」改成「行為測試或正向約束=未接(儀器批)」或「行為測試或正向約束=不接(代碼審或真機)」(實驗 E4、E5 移出的列同樣改),其他接電方式的批次照舊;接電方式欄不動(型錄格式檢查要求形狀類至少有告警或正向約束,不能拿掉)。②〈輸入與口徑〉加一句「級含 C 的列,範本在 `skills/kotlin-idioms/test-templates.md` 或 Android 架構測試產生器,用列編號搜」。統計節若有受影響的數字照 `check.py` 讀表重算(2026-11-06 前掃核對:統計節目前沒有「批五」或各批次列數,預期不變)。
5. **K 測試進產生器資料檔** `scripts/templates/android-arch-target.md`:
   - 三支 `=== test *`(一律收,跟開關無關)加三條 `=== rule *` 的 RULE 行(帶 `[test:]` 綁定),每支測試塊開頭一行 `// 型錄:<編號>`。
   - K1:檔案匯入 `kotlinx.coroutines.GlobalScope`、或有 `kotlinx.coroutines.*` 星號匯入而本文出現 `GlobalScope.`、或本文出現完整名稱 `kotlinx.coroutines.GlobalScope`,都算違規;類別屬性的初始值裡出現 `CoroutineScope(` 算違規(注入進來的 `CoroutineScope` 參數不算)。比對前先去掉註解與字串的做法看實驗 E7。
   - K2:`data` 套件裡的類別,方法本體與屬性初始值不准出現 `Dispatchers.IO`、`Dispatchers.Default`;主建構子參數的預設值(`io: CoroutineDispatcher = Dispatchers.IO`)不算——那正是注入寫法。
   - K3:名稱以 `UiState` 結尾的類別,自己的屬性(不含巢狀)一律 `val`、型別名不以 `Mutable` 開頭、型別不是 `java.` 開頭的外部型別。
   - Konsist 版本:技能文件 `skills/lumos-project-notes/commands/target-arch-android-template.md` 的依賴行從佔位 `konsist:<版本>` 改寫成具體的官方現行版本號,產生器資料檔檔頭註解新增一行寫同一個版本號(兩處現在都沒有具體版本;2026-11-06 核對為 `1.0.0-beta.1`,見〈待決問題〉Q3);既有測試裡的 `resideInPackage`(資料檔三處:`convention`、`interfaces=deep`、`interfaces=always` 那三支)照 1.0.0-beta.1 的更名改成 `residesInPackage`(新名字以實驗 E8 編譯為準);技能文件「Konsist 0.18 起綁 Kotlin 2.4 標準庫,改用 0.17.3」那句照 1.0.0-beta.1 的發行說明改寫(它改回 JVM 11、發佈 `kotlin-stdlib` 2.0.21)。
   - 既有守產生器的測試(`t_arch_template_android_all_combos` 等)照多三條規則、三支測試更新預期數字(規則數基準從 9 改 12)。
   - lumos 自己重寫了一份「Konsist 怎麼判測試原始碼集」的算法(`scripts/lumos` 的 `_arch_tpl_konsist_test`,照 0.17.3 反組譯,用來產舊檔清單)與對照測試(`t_arch_template_android_legacy_modes` 一帶);1.0.0-beta.1 改了 `scopeFromProduction` 的收檔範圍,這支要照新版重核並更新,實驗 E8 驗兩者對同一專案算出一樣的檔清單。
   - `Systems/android-arch-template` 與驗證紀錄 `Verification/2026-10-30_Android產生器在示範專案實跑` 寫死 0.17.3 的句子同步改(驗證紀錄改的是 revalidate_when 觸發,不改當時的結果)。
6. **指路**:kotlin-idioms 的 `SKILL.md` 開頭那段(已指向型錄)加一句「寫協程、Flow、HTTP、序列化或 SavedStateHandle 的測試,先從 `test-templates.md` 對應組起手」;測試品質標準〈Android 本機單元測試的驗收標準〉的「協程」「Flow」兩小段尾各加一句指到範本檔。
7. **實驗與驗證紀錄**:照〈實驗〉逐項跑,結果寫進一篇 `Verification/` 驗證紀錄(`plan_refs` 連回這篇);實驗推翻範本寫法的,改範本、重跑那一格。

### 不做(31 列,與理由)

- **儀器批 24 列**:STATE-12、STATE-23、UI-36、UI-52、UI-106、UI-110、ARCH-2、ARCH-3、ARCH-31、ARCH-35、DATA-17、DATA-19、DATA-21、DATA-38、DATA-39、DATA-58、DATA-60、DATA-63、DATA-65、DATA-69、TEST-29、TEST-32、TEST-35 與 ARCH-56(K4)。理由:要 Compose UI 測試、Room `MigrationTestHelper`、Paging、WorkManager、LeakCanary 或 Robolectric,得建 Android 建置與模擬器,本批的實驗環境(純 JVM Gradle)跑不動,消費專案也不能在推送前不開模擬器就跑完;DATA-39 單看 `Data` 類別是純 JVM 可測,但跟 DATA-38 同一組 WorkManager 範本,拆開會多一份依賴說明,跟 T8 一起做。DATA-19 的 K5(每個 Migration 要有測試)跟 T6 一起做。ARCH-56 的 K4 另缺依據:Hilt 官方頁現版找不到「Fragment 標了宿主 Activity 也要標」的原句,要先找到 dagger.dev 的原句或實跑一次崩潰。
- **只能代碼審或真機的 7 列**:STATE-20(SavedStateHandle 的寫入時機看 Activity 停止的系統時序,官方頁 Caution 段寫「only saves data written to it when the host Activity is stopped」)、CO-39(多執行緒競態,測試派發器是單執行緒,測不出)、UI-109(截字要看實際字型與螢幕)、DATA-44(前景服務的時限由系統計時)、DATA-77(R8 只在 release 建置出現)、PERF-1、PERF-2(StrictMode 只在裝置上偵測)。維持代碼審與真機驗收(lumos-android-evidence)。
- **不改任何推送閘、收證工具與新增告警閘的判定**;不新增 lumos 子命令(抽實驗專案是型錄自檢程式的一個入口)。
- **不在本 repo 的 CI 跑 Gradle**:CI 沒有 JDK 與 Gradle 下載這一步,範本的 Kotlin 寫錯在這裡看不出來(產生器那篇已記同一個坑);紅綠只靠實作時的實驗與驗證紀錄,天花板見下。
- **不在型錄每列「實測狀態」欄補範本實測**:實測結果寫在範本檔的矩陣與驗證紀錄,型錄只靠編號指過去。
- **不做 K1–K3 以外的架構規則**;不做 PERF-1/2 的 debug 版 StrictMode 開關(那是真機流程)。

## 實驗(每個機制都跑一遍,找漏洞)

照使用者第二要點,下面每一項在實作時真的跑;結果不符預期就照第一要點先查官方與業界做法再改,寫進〈依據來源〉與審計修正紀錄。實驗跑在會談暫存區的資料夾,Gradle 用本機 `~/.gradle/wrapper/dists/gradle-8.13-bin/` 那份(調研 2026-11-06 已用它跑通),Kotlin Gradle 外掛 2.2.21、JDK 17。

- **E1 紅要是斷言紅**:每組 `template × bad` 的紅,讀 JUnit XML 的失敗型別,用 `scripts/test_quality.py` 的 `assertion_failure` 判,全部要判成斷言失敗。已知會是例外紅、要先改寫的:T4 的 204(調研實跑是 `IllegalArgumentException: EOF`)、T5 未知 enum(解碼丟 `SerializationException`)、T1 的 API-34(第二次 resume 丟 `IllegalStateException`)、T1 的 FLOW-29(會卡到 `runTest` 逾時)。
- **E2 每格只紅點名的那支**:`template × bad` 那格,矩陣沒點名的測試要綠;一個壞寫法讓整組全紅,代表範本的測試沒有分開。
- **E3 時序穩定**:T1(含 CO-14「逾時剛好落在取得資源之後」)與 T2 每格各跑 20 次,結果要每次一樣;不穩的那支改寫或拿掉,型錄那列改「未接」並寫原因。
- **E4 STATE-17 測得出來嗎**:官方 `InstantTaskExecutorRule` 讓 Architecture Components 的背景工作同步執行,`postValue` 連發兩次在這規則下可能每次都送到,壞寫法反而綠。先實跑確認;測不出就改用自訂的 `TaskExecutor`(主執行緒工作排隊、測試手動放行)再跑;還是測不出就把 STATE-17 移到不做清單、型錄通電批次改「不接(代碼審或真機)」。
- **E5 SavedStateHandle 在純 JVM**:①`SavedStateHandle.set` 在本機單元測試(只有 android.jar 空殼)會不會因型別驗證碰到 Android 類別而失敗;②`lifecycle-viewmodel-testing` 的 `ViewModelScenario.recreate()` 在純 JVM 能不能用(Lifecycle 2.9.0-alpha01 發行說明寫 SavedStateHandle 支援是「Android only」)。①不行就把 T3 移到儀器批;②行的話範本改用它(跟測試品質標準的「畫面重建與程序被回收」那條一致),不行就在測試品質標準那條補一句「純 JVM 用複製 handle 的寫法」。
- **E6 FLOW-3 的後果**:官方 `combine` 頁沒明寫「每個來源都要先發過」,用範本的紅綠對照實證,實跑訊息寫進驗證紀錄,當型錄那列「後果」欄的佐證。
- **E7 K 測試的漏網與誤報**:在 macrobench-lab(本機 Android 示範專案,`/Users/enzo/lumos-scratch/android-checks/scratchpad/lab`,根目錄有 gradlew;Konsist 在沒有 gradlew 的資料夾會以內部例外紅、不是斷言紅,調研實測)的實驗分支各放壞例與好例:K1 壞例 = 匯入 GlobalScope、星號匯入加 `GlobalScope.launch`、完整名稱寫法、屬性 `CoroutineScope(Dispatchers.Main)`;K1 好例 = 註解裡寫 GlobalScope、建構子收 `CoroutineScope`;K2 壞例 = `withContext(Dispatchers.IO)` 在方法裡;K2 好例 = 建構子參數預設值 `Dispatchers.IO`、`domain` 套件裡寫(不在 K2 管轄);K3 壞例 = `var`、`MutableList`、`java.time.Instant`;K3 好例 = 全 `val` 加 `List`、`kotlinx.datetime.Instant`。每個壞例只讓它那支紅、好例全綠;每支 K 測試各改壞一次(拿掉判斷式)確認壞例轉綠。
- **E8 Konsist 換版**:用 1.0.0-beta.1 跑產生器預設組與六開關全反那組的整份架構測試(含既有十多支),確認編譯過、既有的紅綠不變;1.0.0-beta.1 發行說明寫 `scopeFromProduction` 改成只收模組 `src` 底下的檔,要確認範圍目錄過濾後的檔數跟 0.17.3 一樣。
- **E9 抽出器本身**:對範本檔跑 `check.py --lab`,資料夾數要等於全部矩陣格子數;把範本檔某個圍欄標頭改錯、矩陣點名不存在的測試,自檢要各自報出來。

## 實務隱患

(`lumos pitfalls <計劃> --check` 逐類答,見節末)

- **範本照抄出錯被當成標準**:範本只在實驗專案跑過,消費專案的類別名、依賴版本不同;範本開頭寫明「照抄後在自己的專案跑一次,綠了才算」,並留「故障證明挑本次需求」那條既有標準(測試品質標準)讓審查看。
- **範本的壞例被本 repo 的推送閘當產品碼**:2026-11-05 規則包樣本 `.kt` 被測試作弊比對與 Room 守衛當產品碼擋過([[Issues/Kotlin規則包代碼審放行的小問題]] 第 7 條)。本批的壞例放在 Markdown 圍欄裡、repo 裡不新增任何 `.kt` 檔,實驗專案只寫到會談暫存區,不進 repo,所以不碰那個坑。
- **版本漂移**:Turbine、MockWebServer、kotlinx-coroutines-test、Konsist 的版本寫在範本 `gradle` 塊與技能文件,官方改版會過期;版本只在一處寫(範本檔每組的 `gradle` 塊、產生器資料檔的檔頭註解),回頭條件見節末 REVISIT。
- **Konsist 1.0.0-beta.1 是兩天前的 beta**(2026-11-04 發佈):API 還可能再改名;已照舊版採用的專案重產架構測試時要一起升依賴,不然 `residesInPackage` 編譯不過。技能文件〈已照舊範本採用的專案怎麼升級〉加這一句;要不要現在就換版是 Q3。
- **K 測試跟規則包重複**:K1、K2、K3 的形狀規則包已有(`kt-unmanaged-scope-launch`、`kt-hardcoded-dispatchers-io`、`kt-uistate-mutable-field`)。兩者分工:規則包接在新增告警閘、只看這次新增的行、消費專案要宣告 `.lumos/lint.json` 且裝了 ast-grep 才響(沒裝判環境不可用、自動放行);K 測試跑在專案自己的 Gradle 單元測試裡、看整個目標範圍、不靠 lumos。兩邊的訊息都以型錄編號開頭,改型錄那列的標準寫法時兩邊要一起看;自檢的反向檢查讓 K 測試的 `// 型錄:` 編號一定存在。
- **效能**:型錄自檢多讀兩支檔(範本檔、產生器資料檔),各幾百行;`--lab` 只寫檔。產生器多三條規則、三支測試,64 種組合的守衛測試多跑的時間可忽略。
- **併發**:`--lab` 只寫到呼叫者給的空資料夾,資料夾不空就拒絕,不會蓋到別人的檔。
- **守衛面**:型錄自檢是本 repo CI 跑的格式檢查,多一項會讓「範本與型錄對不上」的提交在 CI 紅;不改任何推送閘或收證判定。
- **舊否決對照**:2026-11-06 跑 `lumos rejections` 按概念比對,見審計修正紀錄第一行(動筆時跑、結果照實記)。
- 前端:不改任何前端檔;「前端」只出現在引用既有的前端目標架構範本那一句。
- 已排除:金流:範本與實驗只用假資料,不碰付款或點數。
- 已排除:對外送出:MockWebServer 只聽本機回環位址;實驗下載依賴只從 Maven Central 讀,不送出任何資料。
- 已排除:不可逆:新增一份 Markdown、擴充自檢程式與產生器資料檔、改型錄一欄的文字,退提交即回原狀;已照新產出採用的專案,架構測試是一般檔,可刪。

REVISIT:2027-02-06 Konsist 出 1.0.0 正式版或 1.0.0-beta.1 之後的版本時,重跑實驗 E8 並更新產生器資料檔與技能文件的版本號
REVISIT:2027-02-06 範本檔各組 `gradle` 塊的依賴版本與 Maven Central 最新版對一次,有大版本差就重跑那組的紅綠矩陣

## 驗收條款

- [S1] 當型錄自檢讀型錄、範本檔與產生器資料檔時,通電批次含「行為測試或正向約束=批五」的每一列應剛好被一處 `涵蓋:` 或 `// 型錄:` 認領;把某列的認領刪掉、把同一列寫進兩處、在 `涵蓋:` 寫一個不存在的編號或一個級不含 C 的編號,自檢應各自報出那個編號;真檔應零問題。 [test:t_kotlin_test_templates_cover_catalog]
- [S2] 當型錄自檢讀範本檔的每一節時,缺 `涵蓋:`、缺帶網址的 `依據:`、缺五種圍欄任一種、缺矩陣、矩陣點名的測試名在 template 與 badtest 圍欄裡找不到、template 列寫了逾時紅、template 配 good 那格不是綠,自檢應各自報出那一節與原因;真檔應零問題。 [test:t_kotlin_test_templates_shape]
- [S3] 當對空資料夾跑 `check.py --lab` 時,子資料夾數應等於範本檔全部矩陣格子數,每個子資料夾應有 settings、build 兩支 Gradle 檔與 src/main、src/test,內容應逐字等於範本檔對應圍欄;資料夾不空時應以 rc2 拒絕且不寫任何檔。 [test:t_kotlin_test_templates_lab_extract]
- [S4] 當在實驗專案逐格跑 Gradle 測試時,每格結果應等於矩陣寫的結果,template 列的每個紅經 `assertion_failure` 判定應是斷言失敗,T1 與 T2 每格重跑 20 次結果應不變;結果與 JUnit XML 摘要應寫進驗證紀錄。 [manual:在會談暫存區用 check.py --lab 抽出後逐格跑 Gradle,記每格結果、失敗型別與重跑次數]
- [S5] 當產生器在 64 種開關組合產出時,每一份的 Konsist 檔應含 K1、K2、K3 三支測試與各自的 `// 型錄:` 註解,節點應含三條綁到它們的 RULE 行,產出與技能文件應不再出現 `resideInPackage` 與 `0.17.3`,技能文件的依賴行應寫官方現行版本號。 [test:t_arch_template_android_k_tests]
- [S6] 當在 macrobench-lab 的實驗分支放進實驗 E7 列的壞例與好例並用新版 Konsist 跑架構測試時,每個壞例應只讓它那支 K 測試以斷言紅、好例應全綠、既有架構測試的紅綠應跟換版前相同;每支 K 測試拿掉判斷式後它的壞例應轉綠。 [manual:在 macrobench-lab 實驗分支跑 Gradle 單元測試,逐例記紅綠,結果寫進驗證紀錄]
- [S7] 當讀 kotlin-idioms 的 SKILL.md 與測試品質標準〈Android 本機單元測試的驗收標準〉時,前者開頭應指到 `test-templates.md`,後者的協程與 Flow 兩小段應各有一句指到它;型錄〈輸入與口徑〉應有指到範本檔的那一句。 [test:t_kotlin_test_templates_linked]
- [S8] 當型錄自檢讀不做清單的 31 列時,它們的通電批次欄應寫「行為測試或正向約束=未接(儀器批)」或「行為測試或正向約束=不接(代碼審或真機)」,應不再出現「行為測試或正向約束=批五」;統計節的數字應等於程式重算的結果。 [test:t_kotlin_catalog_rows_wired]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 真的型錄、範本檔、產生器資料檔 | 零問題;37 列(扣掉實驗 E4、E5 移出且型錄已改「未接」或「不接」的列)各被認領一次 | 本計劃〈範圍〉做的 37 列;使用者「型錄每列要能指到它的範本」 |
| S1 | 範本檔 T1 的 `涵蓋:` 刪掉 API-1 | 報 API-1 沒人認領 | 本計劃〈做法〉3 正向檢查 |
| S1 | API-1 同時寫在 T1 與 T2 的 `涵蓋:` | 報 API-1 被兩處認領 | 本計劃〈做法〉3 正向檢查 |
| S1 | T1 的 `涵蓋:` 加 API-99 | 報 API-99 不在型錄 | 本計劃〈做法〉3 反向檢查 |
| S1 | T1 的 `涵蓋:` 加 API-3(級 A) | 報 API-3 級不含 C | 本計劃〈做法〉3 反向檢查 |
| S2 | T4 那節拿掉 `bad` 圍欄 | 報 T4 缺 bad 圍欄 | 本計劃〈用詞〉範本檔 |
| S2 | T1 矩陣 template 列寫「逾時紅 independent_calls_run_in_parallel」 | 報 template 列不准逾時紅 | 測試品質標準「被當掉抓到的錯不算」 |
| S2 | T1 矩陣點名 `no_such_test` | 報測試名找不到 | 本計劃〈做法〉3 形狀檢查 |
| S3 | 空資料夾 | 子資料夾數 = 矩陣格子總數,內容逐字等於圍欄 | 本計劃〈用詞〉實驗專案 |
| S3 | 資料夾裡已有一支檔 | rc2、資料夾內容不變 | 本計劃〈實務隱患〉併發 |
| S4 | T1 template × bad(依序呼叫的 loadScreen) | 斷言紅 independent_calls_run_in_parallel「expected:<1000> but was:<2000>」 | 調研 2026-11-06 實跑訊息;developer.android.com/kotlin/coroutines/test「it will automatically skip any delays」 |
| S4 | T4 template × bad(204 宣告成要解析 body) | 斷言紅 delete_204_is_success(不是 IllegalArgumentException) | 調研實跑是例外紅;本計劃實驗 E1 |
| S4 | T0 badtest × 正確程式(TEST-4:沒推進就斷言) | 斷言紅(錯紅) | developer.android.com/kotlin/coroutines/test「advanceUntilIdle … This is a good default choice」 |
| S5 | 產生器預設組 | Konsist 檔有 noGlobalOrAdHocScope、dataLayerInjectsDispatchers、uiStateIsImmutable 三支 | 本計劃〈做法〉5 |
| S5 | 64 組任一組的 Konsist 檔 | 不含 `resideInPackage` | Konsist 1.0.0-beta.1 發行說明「resideIn* → residesIn*」 |
| S6 | 星號匯入加 `GlobalScope.launch` 的類別 | K1 斷言紅 | 本計劃實驗 E7 |
| S6 | 建構子參數預設值 `Dispatchers.IO` | K2 綠 | developer.android.com/kotlin/coroutines/test「Using dependency injection to provide dispatchers」 |
| S7 | kotlin-idioms SKILL.md | 開頭段含 `test-templates.md` | 本計劃〈做法〉6 |
| S8 | 型錄 STATE-12 列 | 通電批次含「行為測試或正向約束=未接(儀器批)」 | 本計劃〈不做〉儀器批 |
| S8 | 型錄 PERF-1 列 | 通電批次含「行為測試或正向約束=不接(代碼審或真機)」 | 本計劃〈不做〉七列 |

## 回退

退回本計劃的提交即可:刪範本檔;`check.py` 拿掉 `template_problems` 與 `--lab`;型錄通電批次欄改回「行為測試或正向約束=批五」、〈輸入與口徑〉那句拿掉、統計重算;產生器資料檔拿掉三條 RULE 行與三支測試、`residesInPackage` 改回 `resideInPackage`、版本號改回;技能文件、SKILL.md、測試品質標準的指路句拿掉;相關測試一起退。已照新產出採用的消費專案:節點多的三條 RULE 行與架構測試多的三支是一般內容,不升級也照常運作;要回到舊版就用舊產生器重產兩份,依賴降回 0.17.3。不碰任何帳本。

## 天花板

1. 範本的紅綠只在實驗專案驗過;消費專案照抄改名後寫錯,本 repo 的測試看不出來(CI 不跑 Gradle),只能靠消費專案自己跑與代碼審。
2. 範本證的是「這種寫法的測試抓得到這種錯」,不證消費專案的程式沒有這種錯——專案沒照範本寫測試,這 34 列就沒有接上。
3. API-4 的「該不該連坐」、API-10 的「該不該防重複」是業務決定:API-4 範本給兩種斷言不設預設,API-10 預設只打一次並附冪等鍵替代版;選錯的話測試照綠。
4. K 測試讀原始碼文字與匯入,分不出型別:同名的別人家 `GlobalScope`、用型別別名藏起來的 `Dispatchers.IO` 會漏或誤報;實驗 E7 只覆蓋列出的幾種寫法。
5. STATE-17 與 T3 是否留在這批取決於實驗 E4、E5;移出時型錄那幾列改「未接」,本批實際涵蓋列數會少於 37。

## 依據來源

每個機制一行:機制|依據|網址或實測|在哪看得到。標「調研開頁」的是 2026-11-06 調研時用 WebFetch 打開、確認頁面寫了那個測法的原文;標「本次開頁」的是寫這份計劃時再開一次核對的。

- T0 斷言前推進|官方「advanceUntilIdle … This is a good default choice」「If your test focuses on concurrency, prefer using StandardTestDispatcher」|https://developer.android.com/kotlin/coroutines/test(調研開頁)|範本檔 T0 節、TEST-4/TEST-14
- T0 換測試 dispatcher|官方「In tests, replace real dispatchers with instances of TestDispatchers」|同上(調研開頁)|TEST-9、`MainDispatcherRule`
- T0 Unconfined 不跑完|官方「this doesn't mean that it'll run them to completion eagerly」|同上(調研開頁)|TEST-14
- T0 stateIn 要收集者|官方「there must be at least one collector present during the test」|https://developer.android.com/kotlin/flow/test(調研開頁)|TEST-6
- T0 backgroundScope|官方「ensures that the coroutine gets cancelled before the end of the test」|同上(調研開頁)|TEST-5、TEST-17
- T0 StateFlow 斷言 value|官方「we generally recommend treating StateFlow as a data holder and asserting on its value」|同上(調研開頁)|TEST-7
- T0 Turbine 未消費事件會紅|「Failing to consume all events before the end of a flow-based Turbine's validation block will fail your test」|https://github.com/cashapp/turbine(調研開頁;版本 1.2.1 為 Maven Central 現行,本次查)|TEST-18、TEST-19、TEST-20
- T0 MainDispatcherRule|「A JUnit [TestRule] that sets the Main dispatcher to [testDispatcher]」|nowinandroid `core/testing` 的 MainDispatcherRule.kt(調研開頁)|範本檔 T0 support
- T1 虛擬時間跳過 delay|官方「it will automatically skip any delays in coroutines」「advanceTimeBy: Advances virtual time by the given amount」「There should only be one scheduler instance used in a test」|https://developer.android.com/kotlin/coroutines/test(調研開頁);本機實跑依序寫法 `expected:<1000> but was:<2000>`(調研 2026-11-06)|API-1、API-10、API-31、API-32
- T1 用 testScheduler.currentTime|本機實跑:`currentTime` 是另一個要 opt-in 的擴充,直接用編譯失敗 `Unresolved reference 'currentTime'`|調研 2026-11-06 實驗紀錄|範本檔 T1
- T1 逾時是取消的子類|「The TimeoutCancellationException that is thrown by withTimeout is a subclass of CancellationException」「may happen at any time, even right before the return from inside of the timeout block」|kotlinx.coroutines 指南 cancellation-and-timeouts.md(android.googlesource 鏡像,調研開頁;kotlinlang.org 原頁 WebFetch 讀不到正文)|API-32、CO-14
- T1 重複 resume|「Concurrent invocations of resume methods lead to a IllegalStateException」|https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-cancellable-continuation/(調研開頁;頁面沒寫依序呼叫兩次的訊息,待實驗 E1 補)|API-34
- T1 produce 的父範圍等它結束|「The lifecycle of the parent [CoroutineScope] cannot end until this coroutine … completes」|https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html(調研開頁)|FLOW-29
- T2 Turbine 寫法|README 範例 `flowOf("one", "two").test { assertEquals("one", awaitItem()); awaitComplete() }`;官方「The third-party Turbine library offers a convenient API」|https://github.com/cashapp/turbine ;https://developer.android.com/kotlin/flow/test(調研開頁);API-8 本機實跑 `expected:<result:a[b]> but was:<result:a[]>`|API-8
- T2 StateFlow 合併相等值、不會結束|「suppress emission of the values to collectors when new value is equal」「State flow never completes」|https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/(調研開頁)|STATE-10、FLOW-20
- T2 SharedFlow 無訂閱者丟值|「the emitted value is immediately lost」「Shared flow never completes」|…/kotlinx.coroutines.flow/-shared-flow/(調研開頁)|FLOW-24、FLOW-20
- T2 shareIn|「every time it is collected a fresh connection is established」|…/kotlinx.coroutines.flow/share-in.html(調研開頁)|FLOW-18
- T2 first 空流丟例外|「Throws NoSuchElementException if the flow was empty」|…/kotlinx.coroutines.flow/first.html(調研開頁)|FLOW-23
- T2 combine 首發條件|頁面只寫「combining the most recently emitted values by each flow」,沒明寫要每個來源先發過|…/kotlinx.coroutines.flow/combine.html(調研開頁);待實驗 E6 實證|FLOW-3
- T2 postValue 只送最後一個|「If you called this method multiple times before a main thread executed a posted task, only the last value would be dispatched.」|https://developer.android.com/reference/androidx/lifecycle/LiveData(本次開頁)|STATE-17
- T2 InstantTaskExecutorRule|「A JUnit Test Rule that swaps the background executor used by the Architecture Components with a different one which executes each task synchronously.」,在 `androidx.arch.core:core-testing`|https://developer.android.com/reference/androidx/arch/core/executor/testing/InstantTaskExecutorRule(本次開頁);它同步執行會不會讓 STATE-17 測不出,見實驗 E4|STATE-17
- T3 測 SavedStateHandle|「create a new instance of SavedStateHandle with the test values it requires and pass it to the ViewModel instance you are testing」「These values persist after the process is killed by the system」|https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate(本次開頁)|STATE-6、STATE-26
- T3 ViewModelScenario|「A new androidx.lifecycle:lifecycle-viewmodel-testing KMP artifact … testing process death and recreation via recreate()」(2.9.0);2.9.0-alpha01 寫 SavedStateHandle 支援是「(Android only)」|https://developer.android.com/jetpack/androidx/releases/lifecycle(本次開頁;Lifecycle 現行穩定版 2.11.0)|實驗 E5、測試品質標準「畫面重建與程序被回收」
- STATE-20 不做的理由|Caution:「In Compose, SavedStateHandle only saves data written to it when the host Activity is stopped」|同 T3 頁(本次開頁)|〈不做〉
- T4 MockWebServer|「MockResponse can be used to simulate a slow network」;依賴 `com.squareup.okhttp3:mockwebserver3`,Maven Central 現行 5.5.1(本次查)|https://github.com/square/okhttp/tree/master/mockwebserver(調研開頁);204 本機實跑 `IllegalArgumentException: EOF: empty body`|API-26、API-30
- T4 權杖刷新有上限|OkHttp `Authenticator.kt` KDoc「Returns null if the challenge cannot be satisfied」,範例 `while ((response = response.priorResponse()) != null)` 與「Give up, we've already failed to authenticate.」|okhttp 原始碼 KDoc(調研開頁)|API-21
- T4 Ktor 串流|「use HttpStatement with a scoped execute block」(頁面沒寫離開區塊即釋放連線,靠實驗)|https://ktor.io/docs/client-responses.html(調研開頁)|API-30
- T5 序列化設定|coerceInputValues 套用「null inputs for non-nullable types」「unknown values for enums」;「the JSON encoder omits default property values」(encodeDefaults);kotlinx-serialization-json Maven Central 現行 1.12.0(本次查)|https://kotlinlang.org/docs/serialization-json-configuration.html(調研開頁)|DATA-72、DATA-73、DATA-74
- K 測試形狀|Konsist starter snippets:ViewModel 命名、`hasImport` 禁 `android.util.Log`;clean architecture「every UseCase class has test」|https://docs.konsist.lemonappdev.com/samples/starter-test-snippets/android-test-snippets.md ;…/clean-architecture-test-snippets.md(調研開頁)|產生器資料檔 K1–K3
- K2 注入 dispatcher|「Using dependency injection to provide dispatchers to your classes makes it easy to replace the real dispatchers in tests」|https://developer.android.com/kotlin/coroutines/test(調研開頁)|K2、CO-5
- Konsist 現行版本|官方安裝頁 `testImplementation("com.lemonappdev:konsist:1.0.0-beta.1")`;Maven Central latest 1.0.0-beta.1(2026-11-04 更新)|https://docs.konsist.lemonappdev.com/getting-started/getting-started/add-konsist-dependency(本次開頁)|技能文件依賴行、Q3
- Konsist 1.0.0-beta.1 改了什麼|「Konsist targets JVM 11 again and publishes kotlin-stdlib 2.0.21」;「resideIn* → residesIn*」「builds fail until call sites are renamed」;`scopeFromProduction` 改成只收模組 `src` 底下;0.18.0「built with Kotlin 2.4.21」、最低 Kotlin 2.0 與 Java 17|https://github.com/LemonAppDev/konsist/releases(本次開頁)|實驗 E8、技能文件那句改寫
- Konsist 要專案根有 gradlew|本機實跑:沒有 gradlew 時 `KoInternalException: Project directory not found`,補了才有真的斷言紅綠|調研 2026-11-06 實驗紀錄|實驗 E7 選 macrobench-lab
- 壞例紅要是斷言紅|收證工具只把斷言失敗算成抓到錯;判定函式 `assertion_failure`|`scripts/test_quality.py`;測試品質標準〈Android 本機單元測試的驗收標準〉「被當掉抓到的錯不算」|〈用詞〉紅綠矩陣、實驗 E1
- 範本照抄、不用產生器|沒有開關需求的範本照抄是既有決定|[[Projects/Android目標架構開關與舊檔畢業_計劃]]〈做法〉1|〈範圍〉做法 1
- 壞例不放 .kt 進 repo|規則包樣本被推送閘當產品碼擋過|[[Issues/Kotlin規則包代碼審放行的小問題]] 第 7 條|〈實務隱患〉
- 儀器批的依據(下一批用)|Room 遷移「you should include a test that covers all migrations」;Paging「the endOfPaginationReached property should be true」;WorkManager「use TestListenableWorkerBuilder」;Compose 無障礙「color contrast, small touch target size」;LeakCanary「automatically call LeakAssertions.assertNoLeaks()」|調研稿第二節 T6–T11 的網址(調研開頁)|〈不做〉;下一批計劃要把這幾行搬過去

## 待決問題

(由 `lumos question-add` 寫進開頭欄位,這裡只放建議答案與理由的長版)

- Q1 API-4 一支失敗時連坐或不連坐:建議範本放兩個互斥版本(`…_one_fails_all_fail` 斷言整體失敗、`…_one_fails_others_shown` 斷言其他結果仍顯示),不設預設;採用時照第三批情境表態對那段程式的答案留一個。理由:型錄這列級是 C+D,「一支壞了其他還要不要」是業務決定([[Projects/Android寫法語意情境表態與盲判_計劃]] 把它交給表態與盲判),範本替人選等於替業務做決定。
- Q2 API-10、API-31 重複送出:建議預設斷言「連點兩次只打一次 API」;只有後端用冪等鍵保證重送無害時,改成「兩次呼叫帶同一個冪等鍵」的版本。理由:型錄標準寫法是防重複;重送是否有害只有業務知道。
- Q3 Konsist 版本:建議現在換成 1.0.0-beta.1。理由:舊版留在 0.17.3 是因為 0.18 綁 Kotlin 2.4,1.0.0-beta.1 改回 JVM 11、`kotlin-stdlib` 2.0.21,那個理由不在了,而且它是官方安裝頁現在寫的版本;代價是它兩天前才發、是 beta,`resideIn*` 改名讓舊產出在新依賴下編譯不過。另一選項是等 1.0.0 正式版,K1–K3 先用兩版都有的 API 寫(只用 `hasImport`、`name`、`text`,不用 `resideIn*`)。

## 審計修正紀錄

- 舊否決對照(2026-11-06 動筆時跑 `lumos rejections`,453 行,按概念比對):沒有撞到本案的否決;三條同向——[[Projects/Room資料庫測試守衛_計劃]] 否決「推送前故障注入(要編譯跑 Android 測試,太慢)」,本案也不在推送閘或 CI 跑 Gradle;[[Projects/Macrobenchmark退步提醒_計劃]] 否決「由 Lumos 呼叫 gradlew」,本案的 `--lab` 只寫檔不執行;[[Projects/Android逐層診斷_計劃]] 否決「skill 目錄附一支 rerun.sh 讓消費專案直接呼叫」(收據會綁工具鏈安裝位置),本案的範本是給 AI 讀了照抄改名的文字,消費專案不呼叫工具鏈裡的檔,跟 DDD、前端兩份照抄式範本同一種放法。
