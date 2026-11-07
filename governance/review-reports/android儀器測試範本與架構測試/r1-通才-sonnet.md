severity: major

F1
severity: major
blocking: 是
引句:「`src/test/resources/archunit.properties` 寫 `freeze.store.default.allowStoreCreation=true`」
引句:「改壞(刪掉清單檔)後舊違規全部重新紅」
問題:照字面實作,凍結清單的行為會跟計劃預期相反,而且會留下一個靜默放行的洞。
- ArchUnit 的 `allowStoreCreation=true` 是「清單檔不在就新建並放行」。依我對 ArchUnit 文件的記憶,預設是 false。這條我沒有實跑,E5 本來就要驗,但字面上刪清單檔後的結果會是新建一份、全部綠,不是舊違規全部重新紅。
- 範本把這個設定當成長駐設定,所以專案把清單檔漏提交、`.gitignore` 掉,或 CI 乾淨 checkout 沒帶到時,K1、K2 會全綠。例:CI 乾淨 checkout 且 `archunit_store` 沒進版控 → 當場把 100 筆違規凍成「已知」→ 綠。
- 清單檔位置也矛盾。依我對 ArchUnit 文件的記憶,清單檔預設路徑是工作目錄下的 `archunit_store`,不是 `src/test/resources`。計劃只寫了 `allowStoreCreation` 一行,沒寫 `freeze.store.default.path`。E5 又預期「清單檔放 `src/test/resources`」,兩處對不起來。
- 前掃 ④10 只補了建檔設定,沒碰這兩點。
- 建議:範本應預設 `allowStoreCreation=false`,只在初次建檔時臨時打開。同時寫明 `freeze.store.default.path`,並把「刪檔後的結果」改成照實驗結果寫。

F2
severity: major
blocking: 是
引句:「`data class ListUiState(val at: java.time.Instant)`」
引句:「**K3 不判 `java.*` 型別、UI-39 後果改寫**」
問題:型錄 UI-39 自己的欄位會跟 T13 互相矛盾,而計劃只改「後果」欄。
- 型錄 `skills/kotlin-idioms/checks-catalog.md:347` 的標題是「資料類別含 var 或外部模組型別 → 不穩定」。壞寫法欄寫「欄位含 `java.time.*`」,好寫法欄是 `@Immutable`/`@Stable`,這些計劃都沒改。
- T13 與 S5 預期值表卻把 `java.time.Instant` 判綠。盲判席讀的是壞寫法欄,會把含 `Instant` 的 UiState 判成壞寫法;T13 對同一寫法判綠。
- 另外 `kt-uistate-mutable-field` 掛在 PERF-30,不會被 UI-39 的修改觸發。
- 建議:做法 2 把壞寫法欄、標題與好寫法欄一起改。S6 的檢查也要涵蓋這幾欄,不能只看「後果」欄。

F3
severity: major
blocking: 是
引句:「`ClassFileImporter` 匯入 app 的套件(Android 本機單元測試的類別路徑有編譯後的 app 類別)」
問題:K1、K2 的匯入範圍沒排除測試源集,測試假實作會誤紅。
- 同一句話已承認本機單元測試的類別路徑有編譯後的類別。在 AGP 的 `debugUnitTest` 輸出目錄,`src/test` 的類別也在同一個類別路徑上,`importPackages` 會一起讀進去。
- `ImportOption.DoNotIncludeTests` 認的是 Maven 與 Gradle 的 `classes/.../test` 這類路徑。AGP 的 `build/tmp/kotlin-classes/debugUnitTest` 能不能被排除,我沒驗,計劃也沒要求驗。
- 例:資料層套件的測試裡有 `withContext(Dispatchers.Default.limitedParallelism(1))`、`CoroutineScope(UnconfinedTestDispatcher())`,或 T12 自己的類別,K1、K2 就會對測試碼紅。
- E5 的樣本全放 `src/main`,測不到這一點。
- 建議:把「排除測試類別」與 AGP 路徑寫進 T12,加進 E5 樣本與 E7 的改壞對照。多模組專案(資料層在 library 模組)怎麼匯入,也要寫。

F4
severity: major
blocking: 是
引句:「位元組碼判:不准 `GlobalScope`、不准在允許類別外呼叫 `CoroutineScope()`/`MainScope()`」
問題:「允許類別」是按類別判的,但 Kotlin 編譯後,合法寫法常常落在別的類別裡,會誤紅。
- 例 1,Hilt 常見的 `@Module abstract class AppModule { @Binds ...; companion object { @Provides @Singleton fun appScope() = CoroutineScope(SupervisorJob() + Dispatchers.Default) } }`。`@Provides` 方法編在 `AppModule$Companion`,這個類別本身沒標 `@Module`。K1 對 `CoroutineScope()` 會紅,K2 若涵蓋資料層也會對 `Dispatchers.Default` 紅。
- 例 2,`Application` 子類別裡的 `launch { CoroutineScope(...) }` 如果落在 suspend lambda 的狀態機類別 `App$onCreate$1`,它不是 `Application` 的子類別。
- E5、E7 只放了「`@HiltAndroidApp class App : Application()` 建 `appScope`」與標在類別上的 `@Module`,沒有涵蓋這兩種形狀。
- 建議:允許類別要判「外層類別」(`getEnclosingClass`)。補上 companion、suspend lambda 與 Hilt 的 `@Binds` 加 `@Provides` 混用模組當 E5 樣本。

F5
severity: minor
blocking: 否
引句:「資料層不准呼叫 `Dispatchers.IO/Default`(建構子預設值與 DI 模組豁免)」
問題:豁免只涵蓋建構子預設值。一般函式的預設參數 `fun load(io: CoroutineDispatcher = Dispatchers.IO)` 會編成 `load$default` 靜態合成方法,不是帶 `DefaultConstructorMarker` 的建構子,K2 照樣紅。
- 這個寫法同樣可注入、可在測試替換,跟型錄 CO-1 的標準寫法精神一致。
- 計劃要不要豁免都沒說,實作者會各自決定。
- 建議:明寫判斷(豁免,或列入已知誤報)。

F6
severity: major
blocking: 是
引句:「只用 0.17.3 與 1.0.0-beta.1 都有的 API(`classes(includeNested = true)`」
問題:T13 沒指定 Konsist 的範圍是 production 原始碼,測試碼可能被一起掃。
- 計劃自己承認 Konsist 0.17.3 與 1.0.0-beta.1 對「哪些檔算測試原始碼集」的處理不同(1.0.0-beta.1 的發行說明寫 `scopeFromProduction` 改成解析前就過濾)。
- 若用 `scopeFromProject()`,測試碼裡的 `class FakeProfileUiState(var loading: Boolean)` 或 `data class TestUiState(val xs: ArrayList<String>)` 會被判紅,而且兩版行為可能不同。
- 預期值表 S5 要求「T13 在兩版結果應相同」,卻沒有任何一個測試源集的樣本。
- 建議:T13 指定 production 範圍,E6 加測試源集的樣本。

F7
severity: minor
blocking: 否
引句:「宣告判:名字結尾 `UiState` 或父型別(含間接)結尾 `UiState` 的類別,屬性不准 `var`」
問題:型錄 UI-39 的對象是任何資料類別含 var,T13 卻只認名字結尾 `UiState`,這個範圍限制沒寫進天花板。
- 例:`data class ProfileState(var name: String)` 或 `ProfileUiModel`、`ScreenContract.State` 全部綠。
- 型錄卻把整列標成「範本 T13」,讀型錄的人會以為都已接上。
- 建議:天花板補一條「命名慣例以外的狀態類別不判」,並讓專案能用常數擴充後綴。

F8
severity: minor
blocking: 否
引句:「當在 Android 實驗專案照骨架逐格跑時,每格每支測試的結果應等於矩陣」
問題:T6–T13 的核心內容只有 [manual] 把關,repo 端沒有任何測試能確認小節完整。
- 我讀過 `configs/ast-grep/kotlin-android/check.py:289` 的 `template_problems`,它只驗「有那一節標題」。S2、S3 另外只檢查標題、骨架的兩個字串與三個禁用寫法。
- 一組範本缺〈紅綠矩陣〉、缺〈壞寫法〉,或「T12 節開頭指到 T11 的 API-9 小節」那句漏寫,所有自動檢查都綠。
- 型錄 API-9 的值寫「範本 T12」,Fragment 那半只有 T11 的小節接,這個指路也沒有自動檢查。
- 建議:S2 加內容檢查,每個 T6–T13 節要有〈紅綠矩陣〉。T12 節要有指向 T11 API-9 小節的字串。

總結:最嚴重是 major,共 8 條,會擋 5 條(F1、F2、F3、F4、F6)。F1 是凍結清單被刪或漏提交時會靜默變綠,F3、F4、F6 是 K1–K3 對真實 Android 專案會誤報,F2 是型錄 UI-39 自相矛盾。
