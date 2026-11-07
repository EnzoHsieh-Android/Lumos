severity: major

F1 範本裡兩個互斥斷言放在同一個 `template` 圍欄,`template × good` 不可能是綠
引句:「API-4 放兩個互斥的斷言版本、不設預設,範本註解寫」
severity: major
blocking: 是
- 做法1 把 API-4 的 `…_one_fails_all_fail` 與 `…_one_fails_others_shown` 放進同一個 T1 `template` 圍欄,API-10/31 的冪等鍵替代版也一樣。
- S2 要求 `template × good` 那格必須是 `綠`,實驗專案又是照 `template` 圍欄逐字抽出再整個跑。
- 輸入是 good 程式(`coroutineScope{awaitAll}`)加上這個 template。`others_shown` 那支必然斷言紅,整格不是綠。換成 supervisor 版的 good,`all_fail` 那支又紅。
- 冪等鍵替代版對「只打一次」的 good 程式也會紅。
- 照字面實作的結果有兩種:矩陣被迫寫成「綠但其實紅」,或 S2/S4/E2 的「只紅點名的那支」永遠不成立。
- 計劃沒說替代版放哪個圍欄,也沒說替代版對應哪份 good 程式。

F2 圍欄資訊字串沒有區分同一組的多份 good/bad,矩陣格子與實驗資料夾無法對應
引句:「`kotlin T1 bad`(照型錄壞寫法的被測程式)」
severity: major
blocking: 是
- T1 要涵蓋 8 列,壞寫法至少有 API-1 的依序呼叫、API-34 的重複 resume、FLOW-29 的 produce 沒消費等不同程式。
- 資訊字串只有「組代號 + 種類」。若同組有多個 `bad` 圍欄,`--lab` 的資料夾 `<組>-<測試份>-<程式份>/` 會重名,矩陣的「程式份」欄也指不到是哪一個。
- 若每組只允許一個 `bad`,它就得把全部壞點塞進同一份程式。矩陣會點名所有測試,E2「一個壞寫法讓整組全紅代表沒分開」就檢查不出任何東西。
- S3「子資料夾數 = 矩陣格子數」也算不出來。
- 計劃要補圍欄的識別欄位(例如 `bad API-34`),並規定矩陣用它當欄名。

F3 實驗專案要「逐字等於圍欄」,但 Gradle 檔沒有對應的圍欄來源
引句:「每個子資料夾應有 settings、build 兩支 Gradle 檔與 src/main、src/test,內容應逐字等於範本檔對應圍欄」
severity: major
blocking: 是
- `gradle` 圍欄被定義為「實驗專案要的依賴行」,沒有 `settings.gradle.kts` 的圍欄。
- `build.gradle.kts` 還需要 Kotlin 外掛 2.2.21、`mavenCentral()`、`useJUnit()` 等。T5 還需要 `kotlin("plugin.serialization")` 外掛,不是依賴行。
- 這些只能硬寫在 `check.py` 裡,但做法2 又說「版本號寫在每組 `gradle` 塊,不寫死在程式裡」。
- S3 的「逐字等於」對 build/settings 無法成立。
- `support` 圍欄放 `src/main` 還是 `src/test` 也沒說。放錯會讓 `template` 找不到假依賴而編不過。
- 這是做法2 與 S3 之間的規格洞。

F4 K3 排除巢狀屬性,常見的 sealed UiState 會空過
引句:「名稱以 `UiState` 結尾的類別,自己的屬性(不含巢狀)一律 `val`」
severity: major
blocking: 是
- 輸入:`sealed interface HomeUiState { data class Success(var items: MutableList<Item>) : HomeUiState }`。
- 只檢查名稱以 UiState 結尾的類別本身。`HomeUiState` 沒有屬性,`Success` 名稱不以 UiState 結尾且屬於巢狀。
- K3 預期綠,UI-39(var、外部型別)卻實際違規,漏報。
- E7 的 K3 壞例只列 `var`、`MutableList`、`java.time.Instant` 平面寫法,沒有 sealed 子類。
- 天花板第4點也沒提到這個漏洞。
- 另外「型別不是 `java.` 開頭」要靠 import 解析。`import java.time.*` 的星號匯入怎麼處理,計劃沒寫。

F5 K1 只查屬性初始值,漏掉型錄壞形狀「函式裡當場建 scope」,還會誤報合法的 applicationScope
引句:「類別屬性的初始值裡出現 `CoroutineScope(` 算違規(注入進來的 `CoroutineScope` 參數不算)」
severity: major
blocking: 是
- 型錄 API-9 的壞形狀是「當場 `CoroutineScope(…).launch`」。
- 漏報:`fun refresh() { CoroutineScope(Dispatchers.IO).launch { api.sync() } }` 在函式本體裡,不是屬性初始值,K1 綠。
- 誤報:型錄標準寫法是「注入的 applicationScope」。自訂 `Application` 或 DI 類別裡的 `val appScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)` 正是建立點,卻會被 K1 判紅。
- 整列 API-9 被標成已涵蓋,但 Fragment 用 `lifecycleScope` 那一半 K1 完全沒碰。
- 另外「比對前先去掉註解與字串的做法看實驗 E7」沒有定案方法。S6 的好例「註解裡寫 GlobalScope」必須綠,規格卻留空。
- 審材外佐證 file: `skills/kotlin-idioms/checks-catalog.md:157`(API-9 列)。

F6 K2 會誤報標準的 dispatcher 注入模組,且驗不到 CO-5 的 main-safe
引句:「K2:`data` 套件裡的類別,方法本體與屬性初始值不准出現 `Dispatchers.IO`、`Dispatchers.Default`」
severity: major
blocking: 是
- 誤報:Hilt 的 `@Module object DispatchersModule { @Provides fun io(): CoroutineDispatcher = Dispatchers.IO }` 放在 `data.di`,就是「建構子預設值」之外最常見的注入來源。方法本體含 `Dispatchers.IO`,K2 判紅。計劃只豁免主建構子預設值。
- 屬性初始值 `Dispatchers.IO.limitedParallelism(4)` 也會紅。
- 漏報:型錄 CO-5 的壞形狀是 `suspend fun load() = dao.blockingQuery()`,完全沒有 Dispatchers 字樣,K2 綠。「禁寫死」不等於 main-safe,卻因此認領了整個 CO-5。
- 審材外佐證 file: `skills/kotlin-idioms/checks-catalog.md`(CO-5 列)。

F7 d3 的退路與 S5/預期值互相矛盾
引句:「Q3:Konsist 換 1.0.0-beta.1,條件是實作時 K1–K3 與既有產出逐條編譯過;編不過就留 0.17.3 並記 Issue」
severity: major
blocking: 是
- 決策 d3 允許退回 0.17.3。
- S5 與預期值表卻寫死「產出與技能文件應不再出現 `resideInPackage` 與 `0.17.3`」,技能文件依賴行也要寫具體版號。
- 退路一旦啟動,S5 與所有 `residesInPackage` 的步驟(含 `t_arch_template_android_k_tests`)都成了必紅。
- 計劃沒有說退路啟動時 S5 怎麼改,也沒說 K1–K3 要先用兩版共通 API 寫。
- 「新名字以實驗 E8 編譯為準」也代表 `residesInPackage` 本身未驗證,S5 卻已把它當預期值。

F8 做法5 重寫 `_arch_tpl_konsist_test` 與舊檔清單對照測試,沒有任何 S 條款
引句:「1.0.0-beta.1 改了 `scopeFromProduction` 的收檔範圍,這支要照新版重核並更新,實驗 E8 驗兩者對同一專案算出一樣的檔清單。」
severity: major
blocking: 是
- 這是會改變 `new-only` 舊檔清單的行為變更。算錯會把舊檔誤算成新檔,或相反,讓採用中的專案突然多出一批紅。
- 驗收只靠實驗 E8,而 E8 沒有對應的 S 條款或自動化測試。
- S5/S6 只管產出文字與手動實驗,`t_arch_template_android_legacy_modes` 一帶要不要改、怎麼驗,沒有條款綁。
- 審材外佐證 file: `scripts/lumos:61475`(`_arch_tpl_konsist_test` 的 0.17.3 反組譯注解)。

F9 T4 釘死 `mockwebserver3` 5.x,照抄進用 OkHttp 4 的消費專案會編不過或版本衝突
引句:「不讓例外直接把測試打紅;依賴 `mockwebserver3`。」
severity: major
blocking: 是
- 依據來源釘 `com.squareup.okhttp3:mockwebserver3` 現行 5.5.1,範本又說「真的 OkHttp/Retrofit」。
- 輸入:消費專案用 Retrofit 加 OkHttp 4.12(仍是多數 Android 專案),照 `gradle` 塊加 5.5.1。測試 classpath 會被拉成混用 OkHttp 5 與 4,出現 `NoSuchMethodError`,或 import `mockwebserver3.*` 解析不到。
- 計劃的實務隱患「版本漂移」只談官方改版過期,沒談消費專案已有的 OkHttp 主版本。「照抄後自己跑一次」也沒教怎麼挑版本。
- 這個在實驗專案(純新依賴)驗不出來,只會在消費端爆。

F10 E4/E5 移出列時,自檢抓不到半移狀態,S8 又寫死 31
引句:「當型錄自檢讀不做清單的 31 列時,它們的通電批次欄應寫」
severity: minor
blocking: 否
- 反向檢查只要求 `涵蓋:` 的編號在型錄且級含 C。
- 若 STATE-17 因 E4 移出、型錄已改「未接」,但 T2 的 `涵蓋:` 忘了刪,正向與反向檢查都不報。範本宣稱涵蓋、型錄說未接,兩邊對不上卻過關。
- S8 的 31 列是寫死數字。E4/E5 移出 1 到 3 列後就變 32 到 34 列,測試要從哪裡算清單,條款沒說。

F11 回退清單漏列實際動到的檔
引句:「退回本計劃的提交即可:刪範本檔;`check.py` 拿掉 `template_problems` 與 `--lab`」
severity: minor
blocking: 否
- 做法5 與 7 另外改了 `scripts/lumos` 的 `_arch_tpl_konsist_test`、`Systems/android-arch-template`、`Verification/2026-10-30_…` 的 0.17.3 句子,還新增一篇 `Verification/` 驗證紀錄(帶 `plan_refs`)。
- 回退段全沒列。靠 git revert 同一個提交可以回去,但逐項手動回退時這幾處會被漏掉。
- 新增的驗證紀錄回退後會變成指向不存在計劃的孤兒。

F12 形狀檢查只確認矩陣點名的測試存在,沒確認 `template` 裡每支測試都在矩陣
引句:「矩陣裡點名的測試名要在 `template` 或 `badtest` 圍欄裡找得到 `fun <名>(`」
severity: minor
blocking: 否
- 輸入:`template` 裡新增一支 `fun some_new_test()`,但矩陣沒提它。自檢零問題,實驗也不會對它驗紅綠,E2「矩陣沒點名的要綠」也驗不到有效性。
- `fun <名>(` 的比對不涵蓋用反引號、含空白的 Kotlin 測試名。
- 圍欄抽取規則完全沒寫。範本檔「用法」段若在縮排或清單裡舉例 `kotlin T1 template` 圍欄,可能被抽成多餘的格子,或內容帶縮排,使 S3「逐字」失敗。

F13 E3 的重跑只涵蓋 T1/T2,T4 用真實時間卻不在內
引句:「與 T2 每格各跑 20 次,結果要每次一樣」
severity: minor
blocking: 否
- T4 的「慢速大 body」用 MockWebServer 實際節流,時間不是虛擬的。
- 在慢的 CI 或消費機器上,斷言「讀到不完整資料」可能時紅時綠。S4 同樣只對 T1/T2 要求重跑。

總結:最嚴重是 major,共 9 條 major(F1–F9)、4 條 minor,會擋 9 條。
