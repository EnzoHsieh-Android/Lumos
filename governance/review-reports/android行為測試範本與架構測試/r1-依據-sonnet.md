severity: major

以下 F1–F15 是「審材引句 + 審材外佐證」的對照結果。除標「推測」外都是實際讀到或打開的。

網址與版本核對結果(沒列為 finding 的都過了):
- 官方頁原句核對過、逐字符合:Android 協程測試頁、Flow 測試頁、Turbine README(1.2.1)、LiveData 頁、InstantTaskExecutorRule 頁、SavedStateHandle 頁、StateFlow、SharedFlow、shareIn、first、`produce`、OkHttp `Authenticator.kt`、serialization 設定頁、Ktor 頁。
- 版本核對過:Maven Central 上 mockwebserver3 是 5.5.1、serialization-json 是 1.12.0、konsist 是 1.0.0-beta.1(2026-11-04)。官方安裝頁寫 1.0.0-beta.1。Lifecycle 現行穩定版是 2.11.0。
- Konsist 發行說明核對過:`resideIn*` 改名、`builds fail until call sites are renamed`、JVM 11、`kotlin-stdlib` 2.0.21、`scopeFromProduction` 只收 `src` 底下,都真的寫在 v1.0.0-beta.1 頁上。
- 型錄 68 列、各組歸屬、31 列不做清單,我用程式跟 `checks-catalog.md` 對過,集合完全一致。
- `kotlinx-coroutines-test` 現行是 1.11.0。計劃沒寫具體版號,所以沒有不符。

---

F1
引句:「`MainDispatcherRule` 照 nowinandroid `core/testing` 同名類別」
引句:「T0 badtest × 正確程式(TEST-4:沒推進就斷言)」
問題:nowinandroid 的 `MainDispatcherRule` 預設是 `UnconfinedTestDispatcher()`,Android 官方協程測試頁的同名規則範例也是。Main 被換成 Unconfined 時,`viewModelScope.launch` 會馬上執行。這樣 TEST-4 的壞測試「沒推進就斷言」對正確程式反而是綠的,預期值表要的「斷言紅」出不來。
計劃只說照抄這個類別,沒寫要傳 `StandardTestDispatcher`。照抄會讓 T0 的紅綠矩陣第一格就錯。
佐證:https://raw.githubusercontent.com/android/nowinandroid/main/core/testing/src/main/kotlin/com/google/samples/apps/nowinandroid/core/testing/util/MainDispatcherRule.kt 、`skills/lumos-project-notes/commands/test-quality-standard.md:143`(既有標準寫「預設用 StandardTestDispatcher」)
severity: major
blocking: 是

F2
引句:「API-10 與 API-31 預設斷言」
問題:型錄 API-31 是「同一資源同時多個請求沒合併」,壞例是多個畫面同時呼叫 `refresh()`,標準寫法是 `Deferred` 共用加 mutex。這列講的是讀取流量,不是寫入重送。
計劃替它掛的「後端有冪等鍵時,兩次帶同一冪等鍵」替代版只適用 API-10 這類送出動作。拿來斷言 API-31,壞寫法(各自打網路)同樣是綠。
API-10 的另一種標準寫法(`isSubmitting` 加按鈕 `enabled`)也驗不到:ViewModel 層連呼兩次 `submit()` 不經過按鈕。決策 d2 把兩列併成同一個斷言,沒有分開處理。
佐證:`skills/kotlin-idioms/checks-catalog.md:158`(API-10)、`:179`(API-31)
severity: major
blocking: 是

F3
引句:「T4 | HTTP 邊界 | API-21、API-26、API-30(3) | 真的 OkHttp/Retrofit 打本機 MockWebServer」
問題:API-30 的壞寫法是 Ktor 的 `prepareGet().execute()`,回應物件被帶出 `execute` 區塊才讀。T4 的測法和 gradle 依賴只有 OkHttp、Retrofit、`mockwebserver3`,沒有 Ktor client,所以驗不到這列說的錯。
依據節對這列的說法是「頁面沒寫離開區塊即釋放連線,靠實驗」,後果「連線提前釋放」沒有官方原文支持。T4 的矩陣格子要寫什麼,計劃也沒定。
佐證:`skills/kotlin-idioms/checks-catalog.md:178`
severity: major
blocking: 是

F4
引句:「Turbine 不用 `cancelAndIgnoreRemainingEvents` 吞事件」
問題:這跟三處既有規則直接矛盾。
- 型錄 TEST-18 的標準寫法是「`expectNoEvents()` 或明確 `cancelAndIgnoreRemainingEvents()`」。
- `test-quality-standard.md` 第 152 行寫「每個發出的值都要收掉,或用 `cancelAndIgnoreRemainingEvents()` 明講不管」。
- 計劃 S7 還要在該段(Flow 小段)尾加一句指到範本檔,卻沒要求兩邊對齊。
範本會教人禁用型錄與標準都允許的寫法。審查者拿標準去挑範本,或反過來拿範本去挑專案,都會互相打架。
佐證:`skills/kotlin-idioms/checks-catalog.md:597`、`skills/lumos-project-notes/commands/test-quality-standard.md:152`
severity: major
blocking: 是

F5
引句:「照 `scripts/test_quality.py` 的 `assertion_failure` 判」
問題:這句在 E1 的原文是「讀 JUnit XML 的失敗型別,用 `scripts/test_quality.py` 的 `assertion_failure` 判」,對應「已知會是例外紅」那份清單。清單只列 T4 的 204、T5 的未知 enum、T1 的 API-34、T1 的 FLOW-29 四項,漏了形狀相同的:
- FLOW-23:`first()` 在空流丟 `NoSuchElementException`,是例外紅。
- DATA-72:缺欄位解碼丟 `MissingFieldException`,是例外紅。
- FLOW-20:對熱流 `toList()` 會一路卡到 `runTest` 逾時,跟 FLOW-29 同形,但只有 FLOW-29 被給了 `backgroundScope` 加 `Job.isCompleted` 的處理。
範本列出現逾時紅會直接違反計劃自己的 S2 規則。`assertion_failure` 對 `UncompletedCoroutinesError` 判非斷言。
佐證:`scripts/test_quality.py:108`、`skills/kotlin-idioms/checks-catalog.md:212`(FLOW-23)、`:209`(FLOW-20)、`:568`(DATA-72)
severity: major
blocking: 否

F6
引句:「每格各跑 20 次,結果要每次一樣;不穩的那支改寫或拿掉」
引句:「T1 與 T2 每格重跑 20 次結果應不變」
問題:穩定性驗證只涵蓋 T1 和 T2。真有時序風險的是沒被涵蓋的格子:
- T0 的 TEST-9:型錄後果寫「偶發紅」,壞例是真 dispatcher 加 `GlobalScope`。
- T4 的慢速大 body 和連續 401:走真的 socket。
這兩種格子在實作者機器上綠一次就被寫進矩陣,消費專案照抄後可能時綠時紅。
佐證:`skills/kotlin-idioms/checks-catalog.md:588`(TEST-9)
severity: major
blocking: 否

F7
引句:「當型錄自檢讀不做清單的 31 列時」
引句:「[test:t_kotlin_catalog_rows_wired]」
問題:`t_kotlin_catalog_rows_wired` 已經存在,只檢查型錄格式:欄位數、編號唯一、非空,以及形狀類與語意類該有的接電方式。它不檢查「31 列通電批次欄寫成未接或不接、且不再出現批五」。
把 S8 綁在這支現有測試上,即使 31 列沒改,綁定測試照綠。計劃做法 3 只新增了 `template_problems()`,沒寫要擴充這支測試,也沒寫新增另一支。
佐證:`scripts/test_lumos.py:125644`
severity: major
blocking: 是

F8
引句:「純 JVM(STATE-17 待實驗 E4)」
問題:E4 只擔心 `InstantTaskExecutorRule` 會讓 `postValue` 每次都送到,漏了更前面的障礙。`lifecycle-livedata-core` 的 Google Maven 模組檔只發布 `.aar`(`androidJvm`),沒有 `jvm` 變體,純 JVM Gradle 專案解析不到。
所以 STATE-17 的 `gradle` 塊在這個實驗環境裡根本寫不出來,E4 的「改用自訂 `TaskExecutor`」備案也一樣被擋住。E4 最後應該會走到「移出」,但現在寫的失敗原因不對。
這是我讀 `.module` 檔得到的,沒實際跑 Gradle。
佐證:https://dl.google.com/dl/android/maven2/androidx/lifecycle/lifecycle-livedata-core/2.9.0/lifecycle-livedata-core-2.9.0.module(只列 `.aar`)
severity: minor
blocking: 否

F9
引句:「2.9.0-alpha01 寫 SavedStateHandle 支援是」
問題:這句拿 alpha 版的「(Android only)」當 E5 的疑慮來源。同頁的 2.9.0 穩定版已寫「The `lifecycle-viewmodel-savedstate` module is now KMP compatible including APIs like `SavedStateHandle`」。
`lifecycle-viewmodel-savedstate-2.9.0.module` 也含 `jvm` 平台變體。E5① 說「只有 android.jar 空殼」,在 pure JVM 實驗專案裡也不成立,實驗專案根本沒有 android.jar。
過時的前提會誤導實作者怎麼設計 T3 的實驗。
佐證:https://developer.android.com/jetpack/androidx/releases/lifecycle
severity: minor
blocking: 否

F10
引句:「kotlinx.coroutines 指南 cancellation-and-timeouts.md(android.googlesource 鏡像,調研開頁;kotlinlang.org 原頁 WebFetch 讀不到正文)」
問題:這行沒給完整網址。我打開 android.googlesource 的 `main` 分支,只看到「文件已搬到 kotlinx.coroutines 官方」的導向頁,沒有那兩句原文。
kotlinlang.org 文件頁 WebFetch 回空,GitHub raw 的 `docs/topics/` 與 `docs/` 兩個路徑都 404。這行無法複驗,只能信調研稿。
這兩句支持 API-32 與 CO-14 的範本寫法。
佐證:https://android.googlesource.com/platform/external/kotlinx.coroutines/+/refs/heads/main/docs/cancellation-and-timeouts.md
severity: minor
blocking: 否

F11
引句:「頁面沒寫依序呼叫兩次的訊息,待實驗 E1 補」
問題:依據節自己承認三行的出處不支持範本寫的說法,卻仍放在「依據」欄:
- API-34:`CancellableContinuation` 頁只說 concurrent 的 resume。依序 resume 兩次不在頁面上,我也確認頁面沒有「Already resumed」。
- FLOW-29:`produce` 頁只說父範圍等它完成。我確認頁面沒寫 `send` 卡住會讓父範圍不結束,那是推論。
- FLOW-3:`combine` 頁沒寫「每個來源都要先發過」,計劃已用 E6 補。
這三行是旁證,不是依據,依據欄應該標明。
佐證:https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-cancellable-continuation/
severity: minor
blocking: 否

F12
引句:「排好 204、連續 401、慢速大 body」
問題:API-21 的型錄 後果欄含「刷新風暴、權杖互相覆蓋」,標準寫法含 `mutex.withLock` 與「已被別人刷新就用新的」。T4 只描述連續 401 的上限那一半,沒有多執行緒同時 401 的格子。
`涵蓋:` 會把整列認領,實際驗不到 mutex 那半。沒有 mutex 的專案,範本測試照綠。
天花板節沒承認這件事。
佐證:`skills/kotlin-idioms/checks-catalog.md:169`
severity: minor
blocking: 否

F13
引句:「`Systems/android-arch-template` 與驗證紀錄 `Verification/2026-10-30_Android產生器在示範專案實跑` 寫死 0.17.3 的句子同步改」
問題:`Systems/android-arch-template` 的〈開關資料檔的形狀〉寫「規則數是 9 條共通、`ddd=full` 多 3 條聚合類…」。計劃新增三條一律收的 RULE 行(基準 9 改 12),該句會變成錯的。
同步清單只列 0.17.3 的句子,沒列規則數。
佐證:`docs/lumos-toolchain-knowledge/Systems/android-arch-template.md`(〈開關資料檔的形狀〉第 3 條)
severity: minor
blocking: 否

F14
引句:「編不過就留 0.17.3 並記 Issue」
引句:「產出與技能文件應不再出現 `resideInPackage` 與 `0.17.3`」
問題:決策 d3 保留退路是編不過就留 0.17.3,S5 卻要求產出與技能文件完全不出現 0.17.3。走退路時 S5 不可能滿足,條款沒寫退路下的版本。
severity: minor
blocking: 否

F15
引句:「不改任何推送閘、收證工具與新增告警閘的判定」
問題:`lands_in` 列了 `Systems/test-quality-cli`(管 `scripts/test_quality.py`),本文卻明說不動收證工具,所以那篇節點沒有東西落進去。
實際會被改的沒有登記落點的文件有:`test-quality-standard.md`、`kotlin-idioms/SKILL.md`、新增的 `test-templates.md`、`target-arch-android-template.md`。
「每支檔有家」檢查只看程式檔副檔名,這幾支 .md 不算違規。但計劃寫的「現況落在哪幾篇」不完整。
至於其他會被改的程式檔,都已有家:`check.py` 與 `checks-catalog.md` 歸 `Systems/kotlin規則包`,`android-arch-target.md` 與 `scripts/lumos` 歸 `Systems/android-arch-template`。
severity: minor
blocking: 否

---

總計:共 15 條,整份最嚴重的是 major(F1–F7),會擋 5 條(F1、F2、F3、F4、F7)。

我沒有寫任何檔,`/tmp/lumos-seat-work/` 底下沒建過東西,不需要清理。
