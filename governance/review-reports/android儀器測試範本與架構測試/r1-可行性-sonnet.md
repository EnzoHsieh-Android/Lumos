severity: major

審查範圍:實跑了 ArchUnit 1.5.1 加 Kotlin 2.2.21(純 JVM)和 Robolectric 4.16 加 AGP 8.13.2 加 JDK 17。沒實跑模擬器上的儀器測試(T6、T10),也沒跑 Compose 和 Fragment 範本。臨時目錄已刪。

F1
severity: major
blocking: 是
引句:「`FreezingArchRule` 第一次要建清單檔,`src/test/resources/archunit.properties` 寫 `freeze.store.default.allowStoreCreation=true`」
計劃把 `allowStoreCreation=true` 當成永久設定,這會讓清單檔被刪或沒提交時變成假綠。我實跑:刪掉 `archunit_store` 後重跑,測試綠,而且連剛加的新違規 `Bad4` 一起被重新凍結。實驗 E5 預期的結果跟實際相反:
引句:「改壞(刪掉清單檔)後舊違規全部重新紅」
實際上在 `allowStoreCreation=true` 下,這一步是全綠。設成 `false` 才會丟 `StoreInitializationFailedException`。消費專案若忘了提交清單檔,或清單檔被 `.gitignore` 擋掉,CI 每次都是新建清單加綠燈。S5 的「凍結清單應照 E5 的四步變化」會在第四步驗不過。

F2
severity: major
blocking: 是
引句:「清單檔放 `src/test/resources`,改壞(刪掉清單檔)後舊違規全部重新紅」
計劃沒有設 `freeze.store.default.path`。我實跑:清單檔落在 Gradle 測試的工作目錄,也就是 `<module>/archunit_store/stored.rules`,不是 `src/test/resources`。ArchUnit 文件說預設路徑要靠 `freeze.store.default.path` 設定。照計劃字面抄,清單檔會出現在模組根目錄,範本沒教使用者提交它,與 F1 疊加更容易假綠。

F3
severity: major
blocking: 是
引句:「在 `backgroundScope` 啟動 `worker.doWork()`、推進、取消,斷言迴圈次數不再增加且 `finally` 關了假資源;壞寫法 `catch (e: Exception)` 吞掉取消。」
這個壞寫法不會變成斷言紅,實跑有兩種結果。
- **catch 在 `while(true)` 裡面:** `delay` 在已取消的協程裡立刻丟例外,被吞掉後馬上進下一圈,變成空轉。Robolectric 主執行緒 CPU 99%,跑了 190 秒以上沒有逾時,我用 jstack 看到卡在 `runCurrent`,最後手動 kill。`runTest` 的 60 秒逾時沒有生效。這是逾時或卡死,收證工具會判不到斷言。
- **catch 在 `while` 外面:** 好寫法和壞寫法兩個測試都綠(`good` 與 `badB` 實跑皆 PASSED),測試分辨不出對錯,是假綠。

兩種寫法都沒有斷言紅。範本需要換一個能觀測的壞形狀。

F4
severity: major
blocking: 是
引句:「壞寫法用 Fragment 自己的 `lifecycleScope`(view 沒了還在收,碰 binding 丟例外,`runCatching` 接住後斷言)」
例外是丟在 `lifecycleScope.launch` 的協程裡,不在測試本體,`runCatching` 接不到。我用 `LifecycleRegistry` 加 `lifecycleScope` 加 `MutableSharedFlow` 實跑:
- **runCatching 結果:** `RUNCATCHING_FAILURE=false`,而 `touched=true`(`collect` 區塊確實執行了,並丟出 `IllegalStateException: binding is null`)。
- **例外去向:** 只印到 stderr 的 "Exception in thread SDK 34 Main Thread",整個 Gradle 建置是 BUILD SUCCESSFUL。

所以「斷言沒有丟例外」這半句對壞寫法永遠成立,假綠。只有「沒有更新已銷毀的 view」靠旗標或 spy 才抓得到,但計劃沒寫要用旗標。T11 的 ARCH-31(`moveToState` 同步丟例外)沒這個問題。

F5
severity: major
blocking: 是
引句:「允許建 scope 的類別是「`Application` 子類別或標 `@Module` 的類別」」
K1 以「呼叫端類別」判歸屬,但 Kotlin 把部分程式碼編成不屬於該類別的合成類別。我實跑:`class App : Application` 裡 `s.launch { CoroutineScope(SupervisorJob()) }`,被判成 `Method <app.ui.App$onCreate$1.invokeSuspend(...)>`,結果被標違規。`App$onCreate$1` 不是 `Application` 子類別,所以誤報(假紅)。同一個情況也會出現在 `@Module` 物件裡的 suspend lambda。巢狀類別(例如 `Companion`)也不是 `Application` 子類別。這次實跑的 `companion`、`by lazy` 沒被誤報,只有 suspend lambda 的合成類別會;但範本沒有處理這一類,只豁免「Application 子類別」本身。

F6
severity: major
blocking: 是
引句:「呼叫落在帶 `DefaultConstructorMarker` 參數的合成建構子,豁免它」
豁免只涵蓋建構子預設值。我實跑:`suspend fun load(d: CoroutineDispatcher = Dispatchers.IO)` 被判 `Method <app.data.Repo.load$default(...)> calls method <Dispatchers.getIO()>`,是一般函式預設參數產生的靜態合成方法。這個寫法和建構子預設值一樣可注入,卻被 K2 判紅。照 E7 的「帶 `DefaultConstructorMarker` 的合成建構子」豁免做,函式預設值還是會誤報。

F7
severity: minor
blocking: 否
引句:「`src/test/resources/robolectric.properties` 一行 `sdk=34` 與為什麼(預實驗 P2)」
P2 的紅只在 `targetSdk=36`(lab 的設定)出現。計劃骨架只寫了 compileSdk 36 和 minSdk 24,沒寫 targetSdk。我實跑兩組:
- **不設 targetSdk:** Robolectric 以 SDK_INT=24(minSdk)跑,不加 `sdk=34` 也綠。
- **`targetSdk=36` 且不設 `sdk=34`:** 整個類別例外紅,訊息為 "Android SDK 36 requires Java 21 (have Java 17)"。加 `sdk=34` 後正常,SDK_INT=34。

結論:釘 `sdk=34` 在 JDK 17 加 targetSdk 36 時既必要又足夠。但骨架若不寫 targetSdk,Robolectric 實際在 SDK 24 跑,與 E4 要對照的模擬器 API 34 不是同一級。範本骨架要明寫 `targetSdk = 36`。

F8
severity: minor
blocking: 否
引句:「`Dispatchers.IO/Default`(建構子預設值與 DI 模組豁免)」
我另外實跑了 inline 函式:使用者自己的 inline 函式內含 `CoroutineScope(...)`,呼叫端類別會被判違規(`UsesInline.g()`),定義處也各報一筆。同一個 inline 函式在凍結清單裡會變成兩筆。這個行為是合理的,但範本沒提;若 inline 在函式庫(其他模組)裡定義、被展開進資料層,也會被誤報。這條是範本說明不足,不是邏輯錯。

F9
severity: minor
blocking: 否
引句:「T10:不用 `DetectLeaksAfterTestSuccess` 規則(它在測試本體外丟 `NoLeakAssertionFailedError`,收證不算斷言)」
LeakCanary 的 `NoLeakAssertionFailedError` 是 `AssertionError` 的子類,E1 把它列為「例外紅」不準確,至少需實跑確認型別。未實跑。

F10
severity: minor
blocking: 否
引句:「`MigrationTestHelper(instrumentation, AppDb::class, driver = AndroidSQLiteDriver(), file = …)` 的建構子是 Room 2.7 起的形狀」
官方文件列出的建構子第二個參數是 `file: File`(位置順序 `instrumentation, file, driver, databaseClass`)。計劃寫的是具名參數混合位置參數:位置參數 `AppDb::class` 排在第二位,對不上 `file: File`。照字面抄會編不過,除非全部改具名。文件:https://developer.android.com/reference/kotlin/androidx/room/testing/MigrationTestHelper

總結:最嚴重是 F1(`allowStoreCreation=true` 讓清單檔被刪後整批重新凍結而轉綠,與 E5 預期相反),會擋 6 條(F1–F6)。
