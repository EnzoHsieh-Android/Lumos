---
name: kotlin-idioms
description: 寫或審 Kotlin（Coroutines/Flow/Compose）代碼前必讀——通用不變量層的慣例規則：並行等待、Flow 合成、協程紀律、Compose 重組，以及 Android 官方建議的 ViewModel 事件化成狀態、不碰 Context、程序被殺後的狀態還原、假實作測試。每條附壞例→好例與機檢對照。框架選擇（Hilt/Koin、Retrofit/Ktor 等）不在此裁——那是各專案自己的事，查該專案圖譜。
---

# Kotlin 慣例（通用不變量層）

**寫或審 Kotlin 之前先看型錄**：[`checks-catalog.md`](checks-catalog.md) 是「標準寫法」的單一來源——每一列寫壞寫法、標準寫法、出處（官方文件網址）、機器怎麼查、在哪一批接上自動檢查。先看型錄裡的〈情境決策表〉一節認出這段程式屬於哪個情境，再照那一列寫；推送前規則包的告警訊息開頭的 `[編號]` 就是型錄的列編號。名稱標「(出處不全)」的列還沒找到官方出處，只當參考、不當標準。本文件下面的 R 規則是早期整理，跟型錄衝突時以型錄為準。

**這份文件治的病**：AI 寫出「正確但笨」的 Kotlin——能跑、測試會過，但串聯了本該並行的等待、巢狀了本該 combine 的流、吞了不該吞的取消例外。這些 bug 不炸在功能上，炸在效能、電量、和上線三個月後的詭異取消行為上。

**分層原則（重要）**：本文件只寫「不隨框架選擇改變的原則」。用 Hilt 還是 Koin、Retrofit 還是 Ktor、MVI 還是 MVVM——那是各專案的當地選擇，**去讀該專案的知識圖譜和 CLAUDE.md**（`lumos search <關鍵字>` 起手）。本文件的規則以「可注入」「可替換」等能力措辭，不點名框架。

**機檢欄說明**：`detekt:規則名`＝有現成規則；`自訂`＝可寫 detekt/Semgrep 自訂規則；`不可機檢`＝只有本文件與審查鏡頭能守——這類規則排最前面，因為文件是唯一防線。detekt 規則分兩種擋法：**不要型別資訊的推送前擋**（宣告用 `--input {LINT_FILES_CSV}`，推送前的新增告警檢查只擋這次新增的）；**標「要型別資訊」的 CI 擋**（推送前那條命令不帶型別參數、這些規則不跑，要在專案 CI 用 Gradle 型別解析任務加基準線擋），見〈機檢接線〉與〈型別資訊〉。

> **核對邊界**：detekt 那部分已核對（2026-11-01，detekt 1.23.8：規則名與預設開關對照 `detekt --generate-config` 產出的預設設定；要不要型別資訊用最小樣本各跑一次、帶與不帶 `--classpath`／`--jdk-home` 對照；2026-11-04 逐版重驗協程與效能兩組）。R16 引用的 compose-rules 與 Slack compose-lints，規則名與條數仍是網搜整理、**未用本機工具核對**；接入時以該工具當前的規則清單為準。
> REVISIT:2027-05-01 用本機工具核對 R16 引用的 compose-rules 與 Slack compose-lints 規則名與條數，補上核對日期或標明仍未核對。
> REVISIT:2027-03-01 detekt 2.0 出正式版沒；出了就重核協程組，並把 R12 標「2.0 才有」的那條改成可開。

**「要型別資訊」是什麼**：detekt 有一批規則要知道「這個呼叫到底是哪個函式、這個型別是什麼」才判得出來，只有拿到專案的編譯路徑（classpath）時才會報——Gradle 外掛的型別解析任務（例：`detektMain`），或命令列帶 `--classpath` 與 `--jdk-home`。只給 `--input` 的命令列跑法下，這些規則一條都不報，也不會出錯；下面機檢欄標了「要型別資訊」的都屬這種，細節見文末〈型別資訊〉。

---

## 一、並行與 Flow（本文件存在的理由）

> **審查時機管道**:本文標「⚠ 不可機檢」的效能/適用性條目,其載重問已由 lumos 效能檢核機制在三時機自動推送(動手前 impact hook 注入/push 前 pitfalls advisory/終審 code-loop 鏡頭;內容源=lumos-toolchain 圖譜 Systems/效能檢核目錄,雙向同步義務)——可機檢條目歸 linter/analyzer,勿靠人記。

### R1. 互不依賴的等待必須並行 ⚠ 不可機檢，本文件頭號條款
兩個以上 suspend 呼叫，彼此的輸入不依賴對方的輸出 → 必須 `coroutineScope { async }` 並行；串聯 await 只允許在真有資料依賴時。

```kotlin
// ✗ 笨（兩秒）：b 根本不需要 a 的結果
val a = fetchProfile()
val b = fetchOrders()

// ✓ 並行（一秒）
val (a, b) = coroutineScope {
    val pa = async { fetchProfile() }
    val pb = async { fetchOrders() }
    pa.await() to pb.await()
}
```
- 語意選擇：一個失敗要取消整批 → `coroutineScope`；個別失敗不連坐（如掃描一批 IP）→ `supervisorScope`。
- 多筆同型：`items.map { async { fetch(it) } }.awaitAll()`——用 `awaitAll()` 不用 `map { it.await() }`（後者逐一等、首個例外的傳播較差）。
- 依據：[Kotlin 官方 composing-suspending-functions](https://kotlinlang.org/docs/composing-suspending-functions.html)

### R2. 多資料流合成畫面狀態用 `combine`，禁止巢狀 collect ⚠ 不可機檢
```kotlin
// ✗ 巢狀 collect（外層每發一次就重訂閱內層,行為錯亂）
flowA.collect { a -> flowB.collect { b -> render(a, b) } }

// ✓ 任一來源更新就重算
combine(flowA, flowB) { a, b -> UiState(a, b) }
```
- `combine`＝任一更新就重算最新組合（UI state 幾乎都要這個）；`zip`＝嚴格一對一配對（少用，配對語意才用）；`merge`＝多源同型事件匯流。
- 依據：[Android 官方 state production](https://developer.android.com/topic/architecture/ui-layer/state-production)

### R3. ViewModel 曝光 state 的標準形狀
私有 `MutableStateFlow` ＋ 公開 `StateFlow`；串流上游用 `.stateIn(scope, SharingStarted.WhileSubscribed(5_000), initial)`——5 秒是為了撐過螢幕旋轉不重啟上游。`Eagerly` 需一行書面理由。
- 機檢：`自訂`（掃公開 MutableStateFlow / Eagerly）
- 依據：[sharein-statein 官方文章](https://medium.com/androiddevelopers/things-to-know-about-flows-sharein-and-statein-operators-20e6ccb2bc74)

### R4. state 更新一律原子 `update { it.copy(...) }`，禁 `.value =` 做讀改寫
`_state.value = _state.value.copy(...)` 在併發下丟更新，而且測試測不出來。
- 機檢：`自訂`

### R5. `shareIn`/`stateIn` 禁止放在函式回傳裡
每呼叫一次就生一條新熱流佔著記憶體。共享流一律建成類別屬性、只建一次。
- 機檢：`自訂`

### R6. 回傳 `Flow` 的函式不標 `suspend`；`flow {}` 內不 `withContext`
冷流本身就是延遲執行；builder 內換 context 違反 context preservation，runtime 直接炸——換上游執行緒用 `.flowOn(dispatcher)`。
- 機檢：`detekt:SuspendFunWithFlowReturnType`（預設開，要型別資訊）；withContext 需`自訂`

### R7. 高頻流接慢消費者，backpressure 策略要明示
只要最新值 → `conflate()` 或 `collectLatest`；不能丟 → `buffer()`。什麼都不寫＝默默堆積。另外：可被新值作廢的查詢用 `collectLatest`，必須逐筆完成的命令用 `collect`——選錯方向是語意 bug。
- 機檢：`不可機檢`

## 二、協程紀律

### R8. suspend 函式必須 main-safe ⚠ 不可機檢，第二重要
做阻塞／耗時工作的**那個類別自己**負責 `withContext(io)`；呼叫端永遠可以在主執行緒直接呼叫，不准要求呼叫端補 withContext。一句話記住：**誰阻塞，誰負責**。
- 依據：[Google coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

### R9. Dispatcher 不准硬編碼，必須可注入可替換
建構子參數、DI 模組、預設參數皆可——重點是測試時換得成 TestDispatcher。`Dispatchers.IO` 直接寫死在方法裡＝不可測。
- 機檢：`detekt:InjectDispatcher`（預設開，要型別資訊）

### R10. 永不吞 `CancellationException`
```kotlin
// ✗ 取消訊號被吃掉,協程殺不死(runCatching 包 suspend 同罪)
try { work() } catch (e: Exception) { log(e) }

// ✓ 取消先放行,再接業務例外
try { work() }
catch (e: CancellationException) { throw e }
catch (e: IOException) { log(e) }
```
這 bug 只在取消時發作、最難排查。
- 機檢：`detekt:SuspendFunSwallowedCancellation`（預設關，要開；要型別資訊）——★只抓「runCatching 裡呼叫 suspend」★，上面壞例那種 `try { } catch (e: Exception)` 帶齊型別資訊也不抓（detekt 1.23.8 官方規則頁；2026-11-01 實測）；而且 Kotlin 標準庫 2.2 以上時補了型別資訊也不響（detekt 1.23.8 限制，2026-11-04 逐版實測）。try/catch 那型要靠審查，或第三方 structured-coroutines 的 `CancellationExceptionSwallowed`

### R11. 禁 `GlobalScope`；活過畫面的工作用注入的應用級 scope
- 機檢：`detekt:GlobalCoroutineUsage`（預設關，要開；**不要型別資訊**，一般接法就會響）。寫完整套件名 `kotlinx.coroutines.GlobalScope.launch` 不會報，只認 import 之後的 `GlobalScope.launch`。

### R12. 其餘機檢組（開了不等於有在跑，見〈型別資訊〉）
`SleepInsteadOfDelay`（協程內用 delay 不用 Thread.sleep，預設開，要型別資訊加 JDK 位置）、`RedundantSuspendModifier`（沒暫停點就拿掉 suspend，預設開，要型別資訊）。`CoroutineLaunchedInTestWithoutRunTest`（測試協程要包 runTest）**只有 detekt 2.0 才有，1.23.8 寫進設定會讓 detekt 整個以「規則不存在」拒跑、一條都不檢查**（2026-11-01 實測），1.23 先靠審查或 structured-coroutines 的 `RunBlockingInsteadOfRunTest`。runBlocking **不全面禁**：`ForbiddenMethodCall` 分不出在不在 suspend 裡，而 OkHttp Authenticator 這類同步介面裡橋接 suspend 是正當用法；suspend 內的 runBlocking 靠審查，或 structured-coroutines 的 `RunBlockingInSuspend`。不帶型別資訊時退而用 `ForbiddenImport` 擋 `kotlinx.coroutines.runBlocking` 的 import，會連正當用法一起擋、寫完整套件名的呼叫繞得過。
另兩條靠審查：CPU 密集迴圈內定期 `ensureActive()`（取消是合作式的）；`Job()/SupervisorJob()` 不當參數傳進 launch（要 supervisor 語意用 `supervisorScope {}`）。

## 三、Compose

### R13. 收流一律 `collectAsStateWithLifecycle()`
`collectAsState()` 在 App 退到背景時照樣收集，浪費電和網路——且要跟 R3 的 `WhileSubscribed` 成對才生效。
- 機檢：`detekt:ForbiddenMethodCall` 配置完整名稱 `androidx.compose.runtime.collectAsState`（只寫 `collectAsState` 不報錯也不響；規則放 `style:` 底下；要型別資訊，classpath 要有 Compose runtime）；不帶型別資訊時改用 `ForbiddenImport` 擋 `androidx.compose.runtime.collectAsState` 的 import

### R14. Lazy 清單必給穩定 key
`items(list, key = { it.id })`；少了 key，症狀是捲動閃跳與整列白白重組，使用者看得到。
- 機檢：`自訂`

### R15. 重組效能三件套 ⚠ 不可機檢
昂貴計算包 `remember(keys) {}`；高頻 state 的派生判斷用 `derivedStateOf`（如 `firstVisibleItemIndex > 0`，否則每滾一像素重組一次）；動畫／捲動值延遲到 `Modifier.offset { }`／`drawBehind {}` 再讀。另禁 backwards write（composition 中讀完又寫同一 state → 無限重組）。副作用只放 `LaunchedEffect`／`DisposableEffect`，而且 key 要選對：讀了會變的輸入卻用 `Unit` 當 key＝永不重跑；key 太寬＝每次重組重跑（2026-09-08 世界對照補；某消費端 18 處 LaunchedEffect 有 9 處 Unit key）。
- 依據：[Compose 官方效能指南](https://developer.android.com/develop/ui/compose/performance/bestpractices)

### R16. Composable 參數紀律（現成規則整組開）
不傳 ViewModel／MutableState／可變集合往下——傳 immutable data ＋ `onXxx` 事件 lambda 往上；ViewModel 只在 screen 頂層取一次。public composable 必有 `modifier: Modifier = Modifier` 且只施加在 root 一次。
- 機檢：[mrmans0n/compose-rules](https://mrmans0n.github.io/compose-rules/rules/)（detekt/ktlint 雙棲，32 條）＋ [Slack compose-lints](https://slackhq.github.io/compose-lints/rules/)（Android Lint 層，互補）

## 四、結構

### R17. 分層 API 形狀固定
data/domain 層：一次性操作＝`suspend fun(): Result`、串流＝非 suspend 的 `fun(): Flow`；ViewModel 收斂成 StateFlow；UI 只收集。一個邊界只保留一套結果型別，不要 Result／Either／throw 三種混用。
- 機檢：`不可機檢`

### R18. 越層 import 當 build error 治
分層一旦只靠紀律守就會被打穿（UI 直接 import DAO）。自訂 detekt `ForbiddenImport`／層白名單規則，讓越層直接紅。
- 機檢：`自訂`（[完整範例](https://dev.to/wakita181009/an-llm-broke-my-architecture-in-one-generation-i-made-that-a-build-error-1ae0)）

## 五、Android 特有（只有 Android 專案適用）

這一節是 2026-11-01 照 Android 官方建議補的，每條的依據頁與當天看到的更新日期寫在條款最後。Kotlin 寫伺服端（例如 Spring）的專案不適用這一節。分層、用例、聚合怎麼切屬於架構選型，不在這裡裁，見 lumos-project-notes 的 Android 目標架構範本。

### R19. ViewModel 不往畫面送一次性事件：處理完化成狀態 ⚠ 不可機檢
提示訊息、導覽、錯誤這類「發生一次」的結果，ViewModel 處理完就寫進畫面狀態；畫面顯示完回報，ViewModel 再清掉。官方把「不要從 ViewModel 送事件給 UI」列為強烈建議：用 Channel 或其他串流送，ViewModel 活得比畫面久，畫面不在時不保證送得到、也不保證被處理；SharedFlow 預設在沒人收的那一刻直接丟掉。

```kotlin
// ✗ 事件走串流：畫面旋轉或退到背景那一刻沒人收，「已儲存」就不見
private val _events = MutableSharedFlow<String>()
fun save() = viewModelScope.launch { repo.save(); _events.emit("已儲存") }

// ✓ 化成狀態，畫面顯示完回報
data class EditUiState(val userMessage: String? = null)
fun save() = viewModelScope.launch { repo.save(); _uiState.update { it.copy(userMessage = "已儲存") } }
fun userMessageShown() = _uiState.update { it.copy(userMessage = null) }

// 畫面
uiState.userMessage?.let { msg ->
    LaunchedEffect(msg) {
        snackbarHostState.showSnackbar(msg)
        viewModel.userMessageShown()
    }
}
```
- 使用者點了就導覽的，畫面自己處理（把 `onHelp: () -> Unit` 這種回呼傳進畫面），不繞 ViewModel。
- ViewModel 判斷完才導覽的（例：驗證通過），把結果放進狀態（例：`isUserLoggedIn`），畫面看到狀態變了再導覽；來源畫面還留在返回堆疊時，要防使用者按返回回來又自動前進一次（官方範例用 `rememberSaveable` 記一個旗標）。
- 舊碼一次改不完、還在用 Channel 的，旁邊寫一行理由。
- 機檢：`不可機檢`（Flow 審查題會問）
- 依據：[Android 官方 UI 事件](https://developer.android.com/topic/architecture/ui-layer/events)（2026-05-18 更新）、[架構建議](https://developer.android.com/topic/architecture/recommendations)（2026-10-05 更新）

### R20. ViewModel 不碰 Context、不繼承 AndroidViewModel
ViewModel 活得比畫面久（畫面旋轉時畫面重建、ViewModel 留著），抓著 Activity、Context 或 Resources 就會洩漏，單元測試也得帶上 Android 框架。官方把「ViewModel 不持 Context」列為強烈建議、「不用 AndroidViewModel」列為建議：要用到的東西移到畫面層或資料層。

```kotlin
// ✗
class ProfileViewModel(app: Application) : AndroidViewModel(app) {
    fun title() = getApplication<Application>().getString(R.string.title)
}

// ✓ 狀態只帶資源 ID，畫面層解析成字串；檔案、系統服務包進資料層，由建構子注入
data class ProfileUiState(@StringRes val titleRes: Int)
```
- 機檢：`自訂`（檢查 ViewModel 的父類別與建構子參數型別）
- 依據：[Android 官方架構建議](https://developer.android.com/topic/architecture/recommendations)（2026-10-05 更新）

### R21. 程序被系統殺掉：要還原的最小資料放保存狀態，大資料放本機儲存 ⚠ 不可機檢
三種東西撐得住的情況不一樣：

| | 畫面旋轉等設定變更 | 系統在背景殺掉程序 | 使用者自己關掉 App |
|---|---|---|---|
| ViewModel | 撐得住 | 撐不住 | 撐不住 |
| 保存狀態（`SavedStateHandle`、`rememberSaveable`） | 撐得住 | 撐得住 | 撐不住 |
| 本機儲存（資料庫、DataStore） | 撐得住 | 撐得住 | 撐得住 |

- 保存狀態只放基本型別與小字串：ID、查詢字串這類「拿來重建畫面」的最小資料。不放圖片、大清單或要長時間序列化的物件——設定變更時序列化在主執行緒跑，太大會掉幀。
- 程序被殺後還原時，用保存狀態裡的那個小值從本機儲存重新載入；ViewModel 記憶體裡的資料只撐設定變更。ViewModel 和保存狀態都不能取代本機儲存。
- 機檢：`不可機檢`
- 依據：[Android 官方狀態還原](https://developer.android.com/topic/libraries/architecture/saving-states)（2026-10-07 更新）

### R22. ViewModel 與資料層測試用假實作，直接斷言狀態值 ⚠ 不可機檢
- Repository 這類依賴用手寫的假實作（例：`FakeOrderRepository`，實作同一個介面、資料放記憶體），不用 mock 套件模擬——官方列為強烈建議。假實作照真的規則跑；mock 驗的是「有沒有被這樣呼叫」，被測的程式內部一重寫，測試就得跟著改。
- StateFlow 能讀 `value` 就直接斷言 `value`，不去收集每個中間值（值變得快時，收集的一方只保證拿到最新那個）。上游用 `WhileSubscribed` 或 `Lazily` 的，就算只斷言 `value`，也要先在測試裡起一個收集的協程，不然上游不會跑、`value` 永遠是初始值；官方範例用 `backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { viewModel.score.collect {} }`：`UnconfinedTestDispatcher` 讓收集的協程馬上開跑，接著斷言才讀得到更新後的值；測試結束時自動取消。
- 測試裡把 dispatcher 換成測試用的（見 R9）。
- 機檢：`不可機檢`
- 依據：[Android 官方架構建議](https://developer.android.com/topic/architecture/recommendations)（2026-10-05 更新）、[官方 Flow 測試](https://developer.android.com/kotlin/flow/test)（2026-09-24 更新）

---

## 機檢接線（一次設好，CI 自動把關）

detekt 設定要點（`--build-upon-default-config` 之上；lumos-toolchain 分發的共用設定已含這些，自己寫的話照抄）：
```yaml
coroutines:
  GlobalCoroutineUsage: { active: true }
  SuspendFunSwallowedCancellation: { active: true }   # 要型別資訊
  SuspendFunWithCoroutineScopeReceiver: { active: true }   # 要型別資訊
style:
  ForbiddenMethodCall:   # 要型別資訊;只給 --input 的命令列跑法下不會報
    active: true
    methods:
      - "androidx.compose.runtime.collectAsState"
  # 命令列不帶型別資訊時,改用只看 import 的寫法(會連正當用法一起擋,寫完整套件名的呼叫繞得過):
  # ForbiddenImport:
  #   active: true
  #   imports:
  #     - "kotlinx.coroutines.runBlocking"
  #     - "androidx.compose.runtime.collectAsState"
```
detekt 1.23 系列不要加 `CoroutineLaunchedInTestWithoutRunTest`：那個版本沒有這條，設定裡寫了整次執行失敗（見 R12）。
- 自有設定要跟共用設定疊加：用逗號合成一個 `--config a.yml,b.yml`（分開寫兩次 `--config` 會拒跑）；清單類欄位（例上面的 methods）後面那份整份蓋掉前面那份，不合併、不警告。
- 加掛 compose-rules（detekt plugin jar）補 R16 整組。
- **推送前擋不用型別的**：`.lumos/lint.json` 宣告 `detekt --input {LINT_FILES_CSV} --build-upon-default-config --config <共用設定> --report sarif:{LINT_SARIF_OUT}`。`{LINT_FILES_CSV}` 把這次改到的 kt 檔用逗號串成一個值（detekt 的 `--input` 只收逗號分隔；用空白串的 `{LINT_FILES}` 多檔時 detekt 拒跑、檢查放行），推送前的新增告警檢查會真的跑、只擋新增的——擋得到的是 `GlobalCoroutineUsage`、複雜度、命名這類不用型別資訊的規則。`lumos pitfalls --diff` 也會吃同一份 SARIF、命中行進審查 manifest。
- **CI 擋要型別的**（detekt 官方建議：只跑改到的檔時要型別的檢查不準，CI 另跑全量）：專案的 Gradle 套 detekt 外掛、設定指共用設定；第一次跑 `./gradlew detektBaseline<變體>`（例 `detektBaselineDebug`）產基準線檔並提交；CI 跑 `./gradlew detekt<變體>`（例 `detektDebug`，純 Kotlin 模組 `detektMain`），基準線以外的新告警讓 CI 失敗。完整範本在 lumos-toolchain 的 linter 精選目錄（detekt 標準接法第②段）。
- `lumos lint-check` 與健檢會照指令字面印出實際會怎樣：沒有檔案佔位符只記錄不擋、帶舊 `{LINT_FILES}` 多檔拒跑、專案 `.github/workflows/` 沒有 `detekt<變體>` 任務時「型別規則哪裡都沒擋」。

### 型別資訊（detekt 有開≠有在跑）

- **是什麼**：detekt 很多規則要知道每個呼叫的型別才判得了。指令列要帶 `--classpath <依賴 jar，冒號分隔>`（簡寫 `-cp`）與 `--jdk-home <JDK 路徑>`；沒帶時這些規則**安靜跳過，不報錯也不警告**（detekt 官方型別解析文件：沒有型別解析時要型別的規則不會跑）。`--jvm-target` 實測不影響。
- **哪些要**：上面標「要型別資訊」的都要；`GlobalCoroutineUsage`、`ForEachOnRange` 不要。
- **怎麼取得**：Gradle 外掛的 `detekt<變體>` 任務（例 `detektMain`、`detektDebug`）自帶型別，純 `detekt` 任務沒有——**要型別的規則放在 CI 用這個任務加基準線擋**（見〈機檢接線〉）；推送前只跑改到的檔，不帶型別參數（照 detekt 官方提交前掛鉤那頁的建議，推送前硬組 classpath 不準）。一般 JVM 專案在命令列也可以帶 Gradle 印出的依賴清單（絕對路徑，相對路徑放在第一個以外的位置會被靜默忽略）。
- **版本限制**：Kotlin 標準庫 2.2 以上時，`SuspendFunSwallowedCancellation` 與標準庫函式的 `ForbiddenMethodCall` 補了型別資訊也不響（detekt 1.23.8 內建編譯器太舊）。


## 審查鏡頭（code-loop 用）

給審查員的一句 framing：「對照 kotlin-idioms 的 R1–R22 逐條掃這份 diff；**finding 必須引用條號**（如『違反 R1：`loadA()`/`loadB()` 無資料依賴卻串聯』），引用不出條號的風格意見不要標。」——執法不立法，品味之爭擋在門外。

## 誠實邊界

1. 最重要的三條（R1 並行、R2 combine、R8 main-safe）恰好都不可機檢；R19 事件化成狀態、R21 狀態還原也是——「無依賴」「該不該合成」是語意判斷，這份文件＋審查鏡頭是唯一防線，這正是它存在的理由。
2. 機檢規則抓形狀不抓意圖：過了 detekt 不代表寫得好。
3. 本文件不裁框架。發現某條規則與專案當地慣例衝突時：當地慣例贏，但把衝突記進該專案圖譜（可能是當地的技術債，也可能是本文件該修）。
4. 回填：被人工糾正的寫法先記進該專案圖譜；確認它在多數專案都會再犯（不是單次個案），才走 [[Projects/idioms自維護迴路_計劃]] 的候選流程加進本文件。
