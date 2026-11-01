# 各技術棧測試撰寫與工具檢驗接入標準 v1

寫新功能、修 bug、重構、補測試或接入測試品質工具時，先讀這份。共用撰寫規範仍以 [03-寫回圖譜.md](03-寫回圖譜.md)〈實作測試品質〉為準；本文件規定如何提供與核對證據。適用 Python、Node.js／TypeScript、C#、Android Kotlin／Java、iOS Swift、PHP／Laravel。這是接入要求，不是已完成所有平台的支援宣告。

## 開發時：先固定需求答案，再寫測試

對本次改動的每個重要行為交代輸入、預期結果、來源、應抓到的錯誤；簡單情境放測試名或註解即可。expected 用需求例子、人工確認結果或独立可信參考。固定字面值也要有來源：从程式目前輸出貼出的 88 並不因為是字面值就獨立。可信參考應記錄版本、适用範圍與獨立性理由；不同函式名或不同模型生成不等於獨立。

辨識兩條分開的證據：

- **需求判準**：独立案例能否指出程式和測試共同誤解需求？由審查者核對來源與案例，JSON 填了 `oracle_source` 不能當證明。
- **抓錯能力**：原缺陷或相關故障是否使目標行為斷言紅，還原後綠？它只能證明對所選錯誤敏感，不能證明 expected 正確、所有錯誤均被覆蓋。

修 bug 與關鍵守衛沿共用規範提供實跑紅綠證據。其他測試按風險選取有代表性的故障，不要求每支測試、每輪審查跑全套 mutation。保留真正情境與拒絕原因的前置斷言，避免另一道守衛替目標代打。測試在修復版本來就紅時，先處理基準，不能把故障結果算檢出。

## 審查時：再看重構是否讓測試不必要地壞掉

若測試依赖來源文字、內部呼叫、私有結構或需要隨實作機械重寫，選一次保持被守護行為的代表性重構，確認行為測試仍綠；適配器初次接入必須驗這個反例。一般 PR 只在出現這類脆弱性訊號時實跑，不為每輪制造额外重構提交。重構用暫存副本，驗完清理，無須併入功能。

重構等價性必须另有理由：需求域內的推導、獨立案例或可信參考；不能只因受測測試都綠就宣稱等價。必要結構測試按結構合約裁定，不用這項強迫它們承受破壞結構合約的重構。

合法性質測試、确定性與 snapshot 可提供補充證據，配獨立已知答案或其他足夠約束。例如只驗排序兩次等於一次，永遠回傳空陣列也能過；再驗元素保留、順序與已知例子。snapshot 要交代核對來源，批量接受目前輸出不能當需求正確。靜態命中先核對目的，不因形式相似自動刪除。

## 工具接入：統一證據，按棧接 runner

使用各專案既有 runner，选配成熟 mutation 工具。Lumos 不自建通用多語言解析器或 mutation engine，也不靠記帳欄位宣稱語意正確。所有執行限隔離的本機、可信 fixture；外部服務、資料庫、副作用須另設隔離，暫存原始碼不能代替環境隔離。

| 棧 | 本機測試入口（由專案固定實際命令） | 抓錯工具方向 | 资格需分開驗的範圍 |
|---|---|---|---|
| Python | unittest／pytest／既有 runner | 固定原缺陷或選配 mutmut | framework、helper斷言、參數化、真實發現數 |
| Node.js／TS | node:test／Jest／Vitest | 固定故障或選配 StrykerJS | TS編譯、runner/plugin、reporter，不從JS推論TS |
| PHP／Laravel | php artisan test／vendor/bin/pest／vendor/bin/phpunit | 固定故障；PHPUnit評估Infection，Pest評估其mutation功能 | PHP/Laravel/framework版本、Unit/Feature、資料庫、queue/fake、coverage與reporter分開資格 |
| C# | dotnet test + 專案 framework | 固定故障或選配 Stryker.NET | xUnit／NUnit／MSTest、target framework、實際斷言歸因 |
| Android Kotlin／Java | Gradle unit tests；裝置／模擬器另跑 | 純JVM評估PIT；平台故障用既有runner | Kotlin/Java、JUnit、AGP、Robolectric、裝置分開，JVM不等於Android |
| iOS Swift | Swift package tests；Xcode target另跑 | 固定原缺陷；通用工具採用前另驗 | XCTest／Swift Testing、Swift/Xcode、模擬器／裝置、UI分開 |

工具版本与候選來源： [StrykerJS](https://stryker-mutator.io/docs/stryker-js/incremental/)、[Stryker.NET](https://stryker-mutator.io/docs/stryker-net/introduction/)、[Gradle PIT 相容限制](https://github.com/szpak/gradle-pitest-plugin)、[Apple 測試入口](https://developer.apple.com/documentation/xcode/testing)。各專案固定版本後跑資格考卷，表格不是指定必裝的新依賴。

### PHP／Laravel 的撰寫與接入補充

沿共用規範驗需求答案與相關故障，框架特性另驗以下範圍。此節是官方文件核對後的接入規格。2026-10-08 獨立消費案例已用 Laravel12.69.3／PHPUnit11.5.57／PHP8.5.10 實跑 Unit、HTTP、記憶體 SQLite、故障／還原／重構／零選中控制；這只是部分原生驗證，未完成下方全部資格考卷。選配 Semgrep1.179.0 已辨識 PHPUnit assertSame/assertEquals、Pest expect 自比介面；Pest 執行、完整算法同源與框架情境分開驗，零候選不放行。

- **Unit／Feature 分開**：Laravel預設Unit測試不啟動應用，適合純業務邏輯；需要路由、middleware、FormRequest、Policy、Eloquent與container時用會啟動應用的Feature測試。對本次守護的結果斷言HTTP內容、拒絕理由、資料狀態或副作用，不只看200/403，也不重抄rules陣列或controller算法當expected。
- **資料與判準分開**：factory可建立情境，但預期價格、權限或狀態另有已確認來源；不要從同一Model accessor、resource或service讀出expected再與它自己比。檢查資料寫入可使用assertDatabaseHas等行為斷言，依需求檢查應有與不應有的內容，不能只查測試自己剛建立的factory記錄。
- **fake按宣稱分工**：Queue／Event／Mail／Notification fake可驗對外派送合約；宣稱job或listener的業務效果時另測其實際處理結果。全域Event fake可能停掉factory需要的事件／observer，前置情境要核對，不能把fake造成的繞路當正式行為。
- **環境先隔離**：核對.env.testing、phpunit.xml、config cache與實際DB連線，隔離資料庫及外部副作用後再跑RefreshDatabase或故障測試。RefreshDatabase提供測試清理，不證明連到的是測試資料庫。SQLite與正式DB的SQL、交易差異需另驗；依賴after-commit或真queue處理的情境不可從交易包裹或fake的成功外推。
- **故障挑本次需求**：選錯折扣、漏tenant/owner限制、略過FormRequest/Policy、漏寫入或job略過更新等相關變體；先證明情境進場，再核對目標失敗，避免早一層認證或資料驗證代打。這些是選題方向，不是每個PR必跑的固定清單。
- **runner與抓錯工具鎖版**：用專案已安裝的Pest／PHPUnit，由composer.lock固定Laravel/Pest/PHPUnit等套件版本；另存php --version、實際extensions與coverage driver版本，執行composer check-platform-reqs核對實機平台需求。config.platform可模擬PHP版本，不能代替實際runtime證據。PHPUnit路線評估Infection；Pest官方提供mutation testing，是否可用依已安裝版本與相應工具／coverage需求核對，兩條路線分開驗。不把歷史Pest相容訊息當目前Infection整合保證，也不要求兩套都裝。

資格考卷除下方共用負例外，加入framework bootstrap失敗、fake使前置情境失效、factory與expected同源、拒絕理由代打、測試DB設定錯與漏tenant限制。使用隔離可信fixture驗錯誤設定，不連正式DB。每個PHP/Laravel/Pest或PHPUnit組合分開標記；Dusk/browser、真queue及正式DB相容證據各列範圍。

來源（本次核對Laravel12.x作例子，消費專案須換成自己的版本）：[Laravel testing](https://laravel.com/docs/12.x/testing)、[database testing](https://laravel.com/docs/12.x/database-testing)、[mocking](https://laravel.com/docs/12.x/mocking)、[Event fake 與factory限制](https://laravel.com/docs/12.x/events#testing)、[Pest mutation testing](https://pestphp.com/docs/mutation-testing)、[Infection supported frameworks](https://infection.github.io/guide/supported-test-frameworks.html)、[Composer platform](https://getcomposer.org/doc/06-config.md#platform)。

### 網頁前端(Vitest／Jest + Testing Library)的撰寫補充

沿共用規範驗需求答案與相關故障;前端畫面測試另有三個常見的假綠或卡死來源(2026-10-15 order-web 示範踩到;單源=[[Projects/前端知識與風險詞_計劃]] 做法 8)。

- **假計時器與 user-event**:`vi.useFakeTimers()`(或 `jest.useFakeTimers()`)之後,user-event 在連續輸入之間加的延遲等不到、測試逾時。用 `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })` 把延遲交給假計時器推進(user-event v14.1 起的建議寫法;不要改用 `delay: null`,官方說會有非預期行為),或只假 `setTimeout`/`setInterval`。Vitest 的假計時器預設連 `Date` 一起假(依安裝版本核對 `toFake` 預設):測倒數、時鐘偏移時用 `vi.setSystemTime` 明寫「現在」,不要讓真時間與假時間混在同一支測試。測完 `vi.useRealTimers()`,切回前先跑完待執行的計時器。
- **fetch 替身要能控制先後**:用 `vi.stubGlobal('fetch', …)` 或 MSW 回可控的 Promise,由測試決定哪個請求先回,才測得到「舊回應晚回來不會蓋掉新資料」;只回固定成功值的替身證明不了亂序處理。斷言畫面最後顯示的是新資料,不只斷言 fetch 被呼叫幾次。測完還原(`vi.unstubAllGlobals()`)。
- **同輪連點**:user-event 的兩次 `click` 之間會等畫面更新,第二下按到的已經是 disabled 的按鈕,測不到「同一輪事件裡連點兩次」。要測防重送的守衛(例如用 ref 記住送出中),在同一個同步區塊連發兩次 `fireEvent.click`,再斷言只送出一個請求;只用 user-event 連點得綠,不代表守衛有效。

故障挑本次需求:拿掉亂序判斷(舊回應照寫)、拿掉送出中守衛、讓計時器卸載時不清,確認對應斷言翻紅。

來源(核對時的版本要記下):[user-event options:advanceTimers](https://testing-library.com/docs/user-event/options#advancetimers)、[Using Fake Timers](https://testing-library.com/docs/using-fake-timers)、[Vitest vi.useFakeTimers / setSystemTime / stubGlobal](https://vitest.dev/api/vi.html)。

### Android 資料層(Room)的撰寫補充

沿共用規範驗需求答案與相關故障;資料層另有兩條分工(2026-10-28 官方文件核對,單源=[[Projects/Room資料庫測試守衛_計劃]]):**mock DAO 只證 Repository 自己的邏輯**(合併、快取、錯誤處理),SQL 根本沒執行;查詢、資料限制、交易、升級要用真的 Room。真的 Room 用**記憶體資料庫**(`Room.inMemoryDatabaseBuilder`,每支測試乾淨開始、關掉就消失);跑在哪:純 Android 模組放 `androidTest` 在裝置或模擬器上跑(交給 CI 或 Android 端到端驗收),Room KMP 專案可在本機 JVM 跑並搭 `BundledSQLiteDriver`(電腦與手機用同一份 SQLite);官方**不建議用 Robolectric 跑 Room**(電腦上的 SQLite 版本可能跟手機不同)。

- **查詢**:先寫入涵蓋「該出現、不該出現、排序邊界」的資料,再斷言回傳的內容與順序;不要只斷言筆數或「不是空的」。
- **資料限制**:主鍵、唯一索引、外鍵(Room 宣告了 `ForeignKey` 就會開外鍵檢查)各寫一支:違反時丟 `SQLiteConstraintException`,而且資料沒被改;衝突策略是 `REPLACE` 或 `IGNORE` 的,改成斷言覆蓋或略過後的結果。
- **交易**:`@Transaction` 方法或 `withTransaction` 區塊,讓後半步失敗(例如第二筆主鍵重複),斷言前半步也撤回、舊資料原樣在;只測成功路徑證不了交易。
- **升級**:`exportSchema` 要開、`schemas/<類別完整名稱>/<版本>.json` 要提交;每一步升級用 `MigrationTestHelper` 先 `createDatabase(舊版)` 用原始 SQL 塞資料,再 `runMigrationsAndValidate(新版, …)` 驗結構與資料都還在;另有一支跑完全部升級的測試(官方建議,`addMigrations(*全部)` 從最舊版開到最新版)。Room 2 是 `androidx.room`、Room 3 是 `androidx.room3`,後者的 `MigrationTestHelper` 要帶 driver 與資料庫檔。社群做法(非官方):用 Robolectric 跑升級測試時,結構檔要加進 debug 的 assets,測試資料夾的 assets 讀不到。升級測試一跑就丟 `AbstractMethodError`(kotlinx.serialization 的方法)時,多半是 Android 測試套件的依賴版本被鎖成跟 App 一樣、App 這邊的 kotlinx-serialization 比 room-testing 要的舊而被降版;在 App 端明確加較新的 `kotlinx-serialization-core`(2026-10-28 Room 2.8.5 實測要 1.8.1)。
- **Flow/LiveData 重送**:收第一次發出的值、寫入、斷言下一次發出的值;Room 只要表有寫入就會重送(值沒變也送),畫面層要的是「值變了才更新」時另驗 `distinctUntilChanged`。LiveData 要搭 `InstantTaskExecutorRule` 或 `observeForever`。
- **TypeConverter**:經 DAO 寫進去再讀出來一圈,斷言值相等,另測 null、時區、極端值;只單獨呼叫轉換函式證不了 Room 有用到它。
- **預載資料庫(createFromAsset)**:第一次開啟時斷言預載的資料讀得到;資產檔的結構要跟目前版本一致,不一致 Room 會在開啟時丟例外,升版時連資產檔一起測。

故障挑本次需求:拿掉查詢的 WHERE 條件、拿掉 `@Transaction`、刪掉一條 Migration、把衝突策略改掉,確認對應斷言翻紅。

推送前的 Room 守衛(`lumos room-guard`)只證「有升級路徑、有結構檔、有沒被 mock 的測試呼叫到改到的 DAO 方法」,不證測試跑過或寫得對;寫得對要靠這一節與審查。

來源(核對時的版本要記下):[Room 測試與除錯](https://developer.android.com/training/data-storage/room/testing-db)、[Room 資料庫升級](https://developer.android.com/training/data-storage/room/migrating-db-versions)、[預載資料庫](https://developer.android.com/training/data-storage/room/prepopulate)。

### C#、Android、iOS 的原生收證接入

沿已安裝 `lumos test-quality capture/check` 保存 JUnit；原生 runner 必須實際執行、report 全新、`--target` 指向真正案例。reporter／橋接腳本、設定、runtime 及 lock 用 `--context` 綁定，原始報告與退出碼一起歸檔。以下是固定消費案例的部分原生資格，完整考卷仍逐項驗，不自動升格整棧 synthetic-verified。

| 棧與本次組合 | 實跑範圍 | 收證與資格邊界 |
|---|---|---|
| C# net9.0／SDK9.0.117、xUnit／VSTest、JunitXml.TestLogger4.1.0 | 獨立金額案例、故障／還原／重構、零選中、編譯錯、一般執行例外 | native TRX與JUnit／退出碼並存；部分logger抹掉例外型別時只認已測的assertion訊息簽名；ASP.NET、NUnit、MSTest另验 |
| Android AGP8.13.2／Gradle8.13／Kotlin2.2.21、JUnit4、API35模擬器 | Local unit與instrumentation分開跑，私有SharedPreferences的寫入／拒絕理由／零副作用 | 保留兩路原始XML及退出碼，匯整不吞錯；JVM全綠不能當装置實跑；Compose／UI／生命週期／其他API另驗 |
| iOS Xcode26.6／iOS26.5模擬器、XCTest、xcbeautify3.2.1 | 價格與test-only UserDefaults寫入／拒絕理由／零副作用 | 保留xcresult及原始退出碼；JUnit是reporter轉出，不單看Xcode65或共同非零碼；Swift Testing／真機／UI另驗 |

當原生工具失敗時，編譯錯、零選中、逾時與錯誤原因代打均保留 invalid。一般例外的訊息提到 AssertionError／XCTAssert 等字樣也不能當失敗歸因；只接受已確認的reporter型別或訊息結構，新增框架／reporter版本先跑真正正反例，再擴充辨識。

C#固定SDK與packages.lock.json，Android固定AGP/Kotlin/Gradle與測試依賴、記錄SDK/JVM/裝置，iOS固定Xcode/runtime/reporter與destination。跨版本、參數化或多destination的身份、skip、crash需要新資格證據，不能直接套本次固定案例。

原生工具參考：[VSTest dotnet test](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest)、[JUnit logger](https://github.com/spekt/junit.testlogger)、[Android命令列測試](https://developer.android.com/studio/test/command-line)、[xcbeautify](https://github.com/cpisciotta/xcbeautify)、[Xcode測試結果](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)。

### Android 本機單元測試的驗收標準

沿共用規範驗需求答案與相關故障。這一節講跑在電腦 JVM 上的本機單元測試(`src/test`):要有哪些、怎麼寫才算數、跑出什麼證據才算驗收過;資料庫照前面的〈Android 資料層(Room)〉節,裝置上的畫面與流程照 lumos-android-evidence 的端到端驗收。官方條目 2026-11-01 核對,各頁當天的更新日期列在最後;標「社群」的是非官方做法(單源=[[Projects/Android本機單元測試驗收標準_計劃]])。

**要有哪些**

- **必有的單元**:ViewModel(含它對外的狀態與 Flow)、資料層的 Repository 與資料來源、領域層的用例、字串與數學這類工具類別。
- **每個單元都要有邊界**:負數、零與邊界值;每一種網路錯誤;壞資料(例如格式錯的 JSON);存檔時儲存空間滿;流程進行到一半物件被重建(例如畫面旋轉)。只有正常路徑不算。
- **不要寫的**:驗框架或函式庫本身行為的測試;Activity、Fragment、Service 這類入口(它們不該有業務邏輯,交給畫面測試)。
- **碰到 Android 框架時的選擇順序**:先把框架依賴移出被測的類別 → 用假實作頂替 → Robolectric(官方說單元測試只在舊碼或依賴 Android 類別的 API 時當最後手段)。Room 不用 Robolectric 跑(見前面的〈Android 資料層(Room)〉節)。
- **加測試函式庫前看實際版本**:協程這類函式庫常被別的套件拉高,build 檔宣告的版本不是實際用的;先用 `./gradlew :<模組>:dependencies --configuration <變體>RuntimeClasspath` 看解析後的版本,測試函式庫對齊它(演練實測:宣告 1.5.1、實際 1.9.0,照宣告會以為沒有 `runTest`)。
- **跑在哪、什麼時候跑**:小測試多、大測試少;單元測試在本機 JVM 跑,每次提交跑、只跑受影響的模組。

**怎麼寫才算數**

- **替身**:假實作優先(實作同一個介面、資料放記憶體,放在 `src/test` 或共用的測試模組);mock 與 stub 次之,spy 避免,複雜的 mock 不寫。先看函式庫有沒有官方提供的測試用假實作。社群:Now in Android 整個專案不用 mock 套件,一律假實作。
- **不用 Hilt 建被測物件**:建構子注入的類別在單元測試裡直接建、傳假實作進去;Hilt(`@HiltAndroidTest`)留給整合測試。
- **不開 `isReturnDefaultValues`**(Groovy 寫 `unitTests.returnDefaultValues = true`):官方說回傳 null 與零會讓該失敗的測試通過,只當最後手段;真的開了,設定旁邊寫理由。
- **協程**:
  - 一支測試一個 `runTest`,寫成運算式本體;`runTest` 會跳過 `delay`,整支測試預設 60 秒逾時。
  - 被測程式用的 dispatcher 要能注入;同一支測試裡的所有測試 dispatcher 共用同一個排程器(`StandardTestDispatcher(testScheduler)`)。
  - `viewModelScope` 寫死主執行緒:本機測試用 `MainDispatcherRule` 把 Main 換成測試 dispatcher(儀器測試不換);這個規則的屬性要宣告在其他用到 dispatcher 的屬性前面,不然那些 dispatcher 拿不到同一個排程器。
  - 預設用 `StandardTestDispatcher`(新協程排隊,行為接近正式環境),排完用 `advanceUntilIdle()`、`runCurrent()` 或 `advanceTimeBy()` 推進;`UnconfinedTestDispatcher` 會馬上開跑、跟正式環境不同,測併發時不用它。
  - 不會自己結束的協程(例如一直收集的),注入 `backgroundScope`,測試結束自動取消。
  - 儀器測試不換 Main 時,工作跑在真的執行緒上,`runTest` 裡的 `withTimeout` 卻用虛擬時間,測試執行緒一閒就快轉、提早逾時;要等真執行緒的結果,把等待包進 `withContext(Dispatchers.Default) { withTimeout(…) }` 改用真時間(協程測試函式庫說明:`Dispatchers.Default` 不走虛擬時間;演練實測)。
  - 不用 `Thread.sleep` 或真實時間等結果,用虛擬時間;非同步工作改用可控制的 dispatcher,固定等待只會讓測試又慢又不穩。
- **Flow**:
  - StateFlow 斷言 `value`,不去收每個中間值(值變得快時,收集的一方只保證拿到最新那個)。
  - `stateIn` 配 `WhileSubscribed` 或 `Lazily` 的,就算只斷言 `value`,也要先起一個空的收集者:`backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { viewModel.uiState.collect {} }`,不然上游不會跑、`value` 永遠是初始值。
  - 有限的流用 `first()`、`toList()`、`take(n).toList()`;不會結束的流在 `backgroundScope` 收,不然 `toList()` 永遠不回來。
  - 被測對象收別人的流時,把來源換成可以從測試推值的假實作(`MutableSharedFlow` 加一個 `emit`)。
  - 社群:用 Turbine 時,每個發出的值都要收掉,或用 `cancelAndIgnoreRemainingEvents()` 明講不管;錯誤用 `awaitError()` 收;不要用 `runCurrent()` 去推 Turbine。
  - ViewModel 的一次性結果化成狀態後(kotlin-idioms R19),測「出現在狀態裡 → 呼叫已顯示 → 從狀態清掉」三步。
- **斷言與命名**:斷言輸出、狀態、寫入結果或錯誤理由(共用規範第 3 條);測試名照官方範例的形式 `被測對象_動作或輸入_預期結果`。
- **Compose 畫面行為在本機跑**(選配):測試放 `src/test`,加 `@RunWith(RobolectricTestRunner::class)` 與 `createComposeRule()`,`isIncludeAndroidResources = true`;適合「點了按鈕畫面有變」這類行為。Robolectric 沒有螢幕、部分 API 只部分支援(系統 UI、WebView 不支援),這些照樣要上裝置驗。
- **截圖測試**(選配):官方推薦用來驗 Compose 的視覺;官方工具是 Compose Preview Screenshot Testing(實驗性),Robolectric 要搭第三方函式庫(社群:Now in Android 用 Roborazzi)。張數要少、每張給獨特的回饋;容差門檻會漏掉門檻以下的差異;參考圖在固定環境(例如 CI)產,不同作業系統的渲染不一樣。

**什麼證據才算過**

- **指令與報告**:`./gradlew :<模組>:test<變體>UnitTest`(例 `testDebugUnitTest`),單支用 `--tests '<完整類名>.<方法>'`;XML 在 `<模組>/build/test-results/`、HTML 在 `<模組>/build/reports/tests/`。收證照上一節:用 `lumos test-quality capture` 保存原始 XML 與退出碼,`--target` 指到真正的案例。Gradle 看到輸入沒變會跳過測試、舊報告留著,`capture` 要求報告在跑之前不存在:先刪掉那份 XML,命令在任務名後面加 `--rerun`(Gradle 7.6 起才有;更舊的用 `--rerun-tasks`,整個建置都重跑)。`--report` 一次只收一個檔,Gradle 每個測試類別各寫一份,收據按類別收。同一個錯讓同一類別好幾支紅時,`--target` 要全部列上(核對只准目標紅);其中有的是「當掉」紅(見下面),就用 `--tests` 縮到用斷言抓到的那幾支再收。收據裡存著當時的歸因結果(不記工具版本),收證工具換了版本之後,同一份報告重算的結果跟記錄不同時,舊收據核對會回 `recorded test outcomes differ from raw report`(記錄的結果跟原始報告重算的不同),要重收,不是偽造。
- **不算過的證據**:
  - 零選中:篩選沒選到任何測試。Gradle 預設這時會失敗(Kotlin DSL 的 `filter.isFailOnNoMatchingTests`、Groovy 的 `filter.failOnNoMatchingTests` 預設開;Gradle 9 起另有 `failOnNoDiscoveredTests`,有測試原始碼卻沒發現測試也失敗,預設開);專案把它們關掉時,退出碼 0 不代表有跑,要數 XML 裡的案例;這時沒有新報告,收證在讀報告那一步就判無效(`--target` 是報告存在時才輪到的下一道)。
  - 編譯錯、逾時、只跑到檔案包裝案例。
  - 開了 `isReturnDefaultValues` 才變綠。
  - 本機或 Robolectric 綠,拿去當裝置實跑的證據。
  - 重試到過才綠:官方說重試只是保住開發速度,不穩的測試一定要修。
  - 錯是被「當掉」抓到的:假實作遇到沒排好的呼叫就丟例外時,多出來的呼叫會讓測試以例外失敗,收證不算它抓到錯;每條需求至少要有一支用斷言抓。反過來,假實作要丟一般例外(例如 `IllegalStateException`),不要用 `fail()` 或 `assertThat` 自我檢查——收證只看例外型別,假實作丟的斷言失敗會被算成抓到錯。
  - 裝置那一路收得到哪些失敗:AGP 的儀器報告不寫例外型別,收證只認第一行剛好是 `java.lang.AssertionError`(可帶訊息)或 `org.junit.ComparisonFailure`、而且從第一個堆疊行起(含這一行)第一個 `Caused by:` 之前有 JUnit `Assert` 或 Hamcrest `MatcherAssert.assertThat` 堆疊的失敗,也就是 JUnit 的 `assertEquals`(數字或字串)、`assertTrue`(帶不帶訊息都行)、Hamcrest 的 `assertThat` 這類;Truth 與 JUnit 的 `assertArrayEquals` 在裝置上第一行沒有型別名,收不到,要拿故障收據就改用上面那幾種,或在本機那路收。本機報告有型別,Truth 的 `assertThat` 與 `assertArrayEquals` 收得到;Truth 的 `Expect` 規則丟的 `Truth$SimpleAssertionError` 也會包住不是斷言的例外,收不到。
  - 裝置那一路收證時用類別篩選(`-Pandroid.testInstrumentationRunnerArguments.class=<類名>`)只跑這次的測試:專案原有的範本測試若在這個變體必紅,原版那份收據就不是全綠。
- **涵蓋率只拿來找漏**:官方說它找得出沒測到的地方,但不能當測試策略好不好的唯一指標。要量就用 AGP 的 `enableUnitTestCoverage = true`(會自動套 JaCoCo)或 Kover;兩者算出的分支涵蓋率可能不同,不跨工具比數字。
- **故障證明挑本次需求**(共用規範第 5 條):例如拿掉 ViewModel 更新狀態那一行、讓假 Repository 丟錯、刪掉一個邊界檢查,確認對應的斷言翻紅、還原後翻綠。社群:變異測試(Pitest 的 Android 外掛、arcmutate 的 Kotlin 外掛)可以補,但有人回報協程程式碼會產生大量雜訊,不當必要條件。
- **機器抓不到、要靠審查的**(演練實測,見 [[Verification/2026-11-01_Android單元測試標準實機演練]]):預期值照抄實作算法(故障證明照樣判抓到)、用 `Thread.sleep` 等結果(detekt 不帶型別資訊不報,不在協程裡也不報)、build 檔開了 `returnDefaultValues`;Kotlin 的 `test-quality scan` 要裝 Semgrep 並帶 `--semgrep <semgrep 執行檔>` 才會掃,沒有就回「不完整、零候選」,等於沒掃,不能當通過;規則只有 `assertEquals(x, x)`,Truth 寫法的自比不在內。

來源(核對當天看到的更新日期):[要測什麼](https://developer.android.com/training/testing/fundamentals/what-to-test)(2026-03-05)、[測試策略](https://developer.android.com/training/testing/fundamentals/strategies)(2026-10-08)、[測試替身](https://developer.android.com/training/testing/fundamentals/test-doubles)(2026-03-05)、[本機單元測試](https://developer.android.com/training/testing/local-tests)(2026-10-23)、[命令列測試](https://developer.android.com/studio/test/command-line)(2026-10-15)、[協程測試](https://developer.android.com/kotlin/coroutines/test)(2026-09-22)、[Flow 測試](https://developer.android.com/kotlin/flow/test)(2026-09-24)、[Robolectric](https://developer.android.com/training/testing/local-tests/robolectric)(2026-03-05)、[截圖測試](https://developer.android.com/training/testing/ui-tests/screenshot)(2026-10-08)、[測試穩定性](https://developer.android.com/training/testing/instrumented-tests/stability)(2026-03-05)、[Hilt 測試](https://developer.android.com/training/dependency-injection/hilt-testing)、[Gradle 測試篩選](https://docs.gradle.org/current/kotlin-dsl/gradle/org.gradle.api.tasks.testing/-test-filter/is-fail-on-no-matching-tests.html)、[程式碼涵蓋率](https://developer.android.com/studio/test/coverage-report)、[kotlinx-coroutines-test 說明](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md)(2026-11-01 核對);社群:[Now in Android 測試策略](https://github.com/android/nowinandroid/wiki/Testing-strategy-and-how-to-test)、[Turbine](https://github.com/cashapp/turbine)、[Pitest 與協程的雜訊回報](https://github.com/hcoles/pitest/issues/579)。

### 適配器資格考卷

接入的每個語言／framework／runner/report組合都保存這些控制：

1. 獨立答案：正确版綠、錯誤規則版的目標斷言紅。
2. 重抄算法：展示故障可翻紅但仍沒有獨立來源；不得把 mutation 分數當來源審查。
3. 合理性質與有目的的結構測試：候選可裁成補充／結構，不自動定罪。
4. 保持行為的重構：行為測試綠；只綁實作的反例可紅，確認重構等價理由。
5. 執行負例：零發現、基準失敗、匯入／編譯錯、未知錯誤理由、故障未進場、逾時、缺工具，各自顯示無效或未驗，不能算 detected。
6. 還原：測試源碼與案例身份不變，原版／還原版 hash 一致且綠。證據綁 implementation、tests、fixture、runner、設定與依賴版本；環境不一致須重驗。

靜態掃描另外跑人工標註的正反例、helper／多步計算漏報與解析失敗，記錄候選裁決、漏報／誤報／未分析。零候選與「掃完」不等於品質通過。

標記 `planned` → `synthetic-verified`（完成上述原生 runner 資格考卷）→ `project-verified`（另保存真專案變更、人工裁決及相關故障證據）。每個標記附語言、framework、runner與版本，不以一個語言、斷言 primitive 或固定示範 harness 替其他範圍升級。本次 Python unittest 與 Node assert 固定 harness 僅證互補機制，不構成任何整棧適配器資格。

### 共用證據格式（接入契約，v1）

各工具輸出可不同，歸檔时保存以下資料。這是內容契約。已安裝 `lumos test-quality capture/check` 實作其中 JUnit 執行、來源快照與故障一致性核對子集；人工判準、完整依賴閉包、報告真實性與各棧全部資格仍須另驗。用法見 [CLI 手冊](03-寫回圖譜.md#事後掃描與執行收證已安裝-cli)。

- 身份：case_id、language、framework、runner/tool版本、測試身份、實際選取命令与發現數。
- 来源：需求／合約版本、输入与expected、oracle_source、人工核對者及理由。`declared`、`reviewed-independent`、`unknown` 分列；自述只到 declared。
- 快照：implementation/tests/fixture/config/dependency指紋、範圍、未驗範圍、原始 runner 報告。
- 執行：baseline、fault、restored 分別存測試數、斷言／失敗身份、失敗種類與理由、exit code、耗時；故障位置、觸發前置、與需求的相關理由另列。
- 重構：`verified`／`not-run`／`not-applicable`、等價理由及實跑證據；不適用寫原因，不記成功。
- 結果：靜態 candidate/dismissed/confirmed 與 runtime detected/survived/invalid/unavailable 分開；timeout、零測試、編譯錯與未歸因失敗歸 invalid。等價變體獨立裁決，未決保留，不用100% mutation當硬目標。

單一 pass 欄位不得吞掉 unknown／not-run。開發者交代過每個改到的重要行為，審查者核對独立來源與所選故障，工具提供可重放的執行證據，才算完成本次驗證；不能從完成直接推論所有測試都已正確。

## 本次結論與後續量測

2026-10-07 固定五種測試×五版本×Python/Node共50格符合事前預期，另6次確認重抄錯誤規則的基準綠→故障紅→還原錯版綠：重抄正确算法与独立已知答案有相同紅綠向量；重抄錯誤規則也可在錯版上綠、固定回傳故障上紅；結構反例因改名重構紅；只有穩定性的測試全綠。據此採取判準來源人工核對、抓錯證據與有條件的重構檢查三者分工，並明示工具边界。

這是合成機制實驗，沒有模型呼叫、沒有真專案適配器资格或收斂輪數改善證據。後續各棧按资格考卷接入，真專案再量測漏放錯誤、誤報、修測試往返與耗時；不把本次50格當50個獨立樣本。
