severity: major

我用本機 Gradle 8.13、Kotlin 2.2.21、JDK 17 實跑了最小專案,並用 `javap` 讀 Konsist 1.0.0-beta.1 的 jar 查 API。臨時目錄已刪。

好消息先講:
- API-34 第二次 resume 實跑丟 `IllegalStateException: Already resumed`,用 `runCatching` 接住再斷言,會是斷言紅。
- FLOW-29 把被測函式放進 `backgroundScope.launch`,壞寫法的 `job.isCompleted` 為 false,是斷言紅,不會卡到 60 秒逾時。
- T3 的 SavedStateHandle 在純 JVM 專案可用:`lifecycle-viewmodel-savedstate:2.9.4` 解析成功,複製 handle 的寫法測試綠。
- Konsist 1.0.0-beta.1 有 `hasImport`、`imports`、`isVal`、`isVar`、`value`(屬性初始值)、`body`、`residesInPackage`、`isMutableType`。K1–K3 要用的 API 都在。

F1
severity: major
blocking: 是
引句:「實驗下載依賴只從 Maven Central 讀,不送出任何資料」
`--lab` 產出的 `build.gradle.kts` 只靠 Maven Central 會解析失敗。我實跑 `lifecycle-viewmodel-savedstate` 在只有 `mavenCentral()` 時報 FAILED,加上 `google()` 才過。androidx 套件只發在 Google Maven。

T3 的依賴因此解析不了,這句「只從 Maven Central」的宣稱也不成立。

另外,`gradle` 圍欄被定義成只放依賴行。
引句:「`kotlin T1 gradle`(實驗專案要的依賴行)」
外掛 id 與版本、`repositories`、`jvmToolchain`、`useJUnit()` 這些必要骨架,計劃沒說由誰寫。`--lab` 函式與 S3「內容逐字等於圍欄」都沒涵蓋。

建議:明寫骨架範本、repositories 含 `google()`,並改掉「只從 Maven Central」那句。

F2
severity: major
blocking: 否
引句:「純 JVM(STATE-17 待實驗 E4)」
引句:「先實跑確認;測不出就改用自訂的 `TaskExecutor`(主執行緒工作排隊、測試手動放行)再跑」
STATE-17 在純 JVM 實驗專案裡根本編不過。實跑 `androidx.arch.core:core-testing:2.2.0` 與 `androidx.lifecycle:lifecycle-livedata:2.9.4` 在純 JVM Kotlin 專案都是 FAILED(Android 專用 AAR,沒有 JVM 變體)。

E4 的兩條路(`InstantTaskExecutorRule`、自訂 `TaskExecutor`)都需要 Android 建置,第二條也一樣,不是「實跑確認」就能決定的事。

計劃有「移到不做」當退路,所以不擋。但「做 37 列」「34 列」的數字、S1 預期和 E4 的步驟都該先改,不要等實驗才發現。

F3
severity: major
blocking: 是
引句:「真的 OkHttp/Retrofit 打本機 MockWebServer,排好 204、連續 401、慢速大 body」
T4 的 API-30(慢速大 body)如果用 `runTest` 加 `withTimeout`,會對好壞兩種被測程式都立刻逾時。

實跑:`runTest { withTimeout(5000) { withContext(Dispatchers.IO) { 真 OkHttp 讀 throttleBody 的回應 } } }` 立刻得到 `TimeoutCancellationException: Timed out after 5s of _virtual_ (kotlinx.coroutines.test) time`。

虛擬時間遇到真實 I/O 會直接跳到逾時點,所以 `template × good` 也會是例外紅,而且每次一樣。E3 重跑 20 次抓不到,因為它穩定地錯。

計劃沒寫 T4 怎麼處理真實時間。建議明寫:涉及真實 I/O 的逾時要包 `withContext(Dispatchers.Default.limitedParallelism(1))` 或不用 `runTest`,並把這條放進紅綠矩陣。

F4
severity: major
blocking: 是
引句:「類別屬性的初始值裡出現 `CoroutineScope(` 算違規(注入進來的 `CoroutineScope` 參數不算)」
引句:「Konsist:範圍內不准 `GlobalScope`、不准類別裡當場建 `CoroutineScope(…)`」
〈範圍〉表說「類別裡當場建」,〈做法〉卻只查屬性初始值。最常見的無主協程是在函式裡 `CoroutineScope(Dispatchers.IO).launch { … }`,K1 抓不到,是假綠。

另一個假紅:`rememberCoroutineScope(` 含子字串 `CoroutineScope(`。拿 `value` 做子字串比對的話,類別屬性寫 `val s = rememberCoroutineScope()` 會誤報。

建議:改成 `body` 與 `value` 都比對,且比對要有字界(`\bCoroutineScope\(`);E7 壞例補函式內建 scope 與 `rememberCoroutineScope`。

F5
severity: major
blocking: 是
引句:「名稱以 `UiState` 結尾的類別,自己的屬性(不含巢狀)一律 `val`、型別名不以 `Mutable` 開頭、型別不是 `java.` 開頭的外部型別」
Android 慣用的 `sealed interface HomeUiState { data class Success(var items: MutableList<…>) : HomeUiState }`,名稱 `Success` 不以 `UiState` 結尾,而且明寫「不含巢狀」。

`var` 與 `MutableList` 全部漏掉,是假綠。`sealed interface` 本身不是 class,`classes()` 也不會回傳它。

建議:改判「名稱以 `UiState` 結尾或父型別含 `*UiState` 的類別(含巢狀)」,E7 壞例補這種寫法。

F6
severity: minor
blocking: 否
引句:「型別不是 `java.` 開頭的外部型別」
1.0.0-beta.1 的 `KoTypeDeclaration` 沒有 `fullyQualifiedName`,只有 `name`、`text`、`packagee`、`sourceDeclaration`、`typeArguments`、`isMutableType`。「`java.` 開頭」要從 `sourceDeclaration` 或檔案匯入推,對 `List<java.time.Instant>` 這種泛型參數要另走 `typeArguments`。計劃沒寫用哪條路,E7 的 `java.time.Instant` 單層例子過了也不代表泛型過。我沒實跑 Konsist 這段,屬推理。

F7
severity: minor
blocking: 否
引句:「照範本檔的矩陣每格寫一個子資料夾 `<組>-<測試份>-<程式份>/`」
圍欄標頭只有 `kotlin T1 bad` 一種寫法,沒有變體編號,也沒說 `support` 屬於 main 還是 test 來源集。

T1 八列各需要不同的壞程式。若放多個同標頭 `bad` 圍欄,同名類別不能放進同一格;若合併成一個,E2「只紅點名的那支」就要在矩陣逐一列出所有紅測試。S3「內容逐字等於對應圍欄」因此無法機械判定。建議補圍欄變體命名與 `support` 的落點規則。

F8
severity: minor
blocking: 否
引句:「虛擬時間讀 `testScheduler.currentTime`(調研第一次實跑用 `currentTime` 編譯失敗:它是另一個要 opt-in 的擴充)」
實跑 `testScheduler.currentTime`(成員屬性)在 coroutines-test 1.10.2 編譯通過,只有 `ExperimentalCoroutinesApi` 警告,不是錯誤。調研編譯失敗的是頂層擴充 `TestScope.currentTime`,缺的是 `import kotlinx.coroutines.test.currentTime`。範本要寫明用 `testScheduler.currentTime` 並加 `@OptIn(ExperimentalCoroutinesApi::class)`,免得有人照字面改回擴充版。

總結:最嚴重是 major,共 8 條(major 5、minor 3),會擋 4 條(F1、F3、F4、F5)。
