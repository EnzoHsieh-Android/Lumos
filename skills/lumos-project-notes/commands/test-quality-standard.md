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
