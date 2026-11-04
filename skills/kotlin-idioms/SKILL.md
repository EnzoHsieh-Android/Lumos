---
name: kotlin-idioms
description: 寫或審 Kotlin（Coroutines/Flow/Compose）代碼前必讀——通用不變量層的慣例規則：並行等待、Flow 合成、協程紀律、Compose 重組。每條附壞例→好例與機檢對照。框架選擇（Hilt/Koin、Retrofit/Ktor 等）不在此裁——那是各專案自己的事，查該專案圖譜。
---

# Kotlin 慣例（通用不變量層）

**這份文件治的病**：AI 寫出「正確但笨」的 Kotlin——能跑、測試會過，但串聯了本該並行的等待、巢狀了本該 combine 的流、吞了不該吞的取消例外。這些 bug 不炸在功能上，炸在效能、電量、和上線三個月後的詭異取消行為上。

**分層原則（重要）**：本文件只寫「不隨框架選擇改變的原則」。用 Hilt 還是 Koin、Retrofit 還是 Ktor、MVI 還是 MVVM——那是各專案的當地選擇，**去讀該專案的知識圖譜和 CLAUDE.md**（`lumos search <關鍵字>` 起手）。本文件的規則以「可注入」「可替換」等能力措辭，不點名框架。

**機檢欄說明**：`detekt:規則名`＝有現成規則；`自訂`＝可寫 detekt/Semgrep 自訂規則；`不可機檢`＝只有本文件與審查鏡頭能守——這類規則排最前面，因為文件是唯一防線。標「要型別資訊」的 detekt 規則，照一般接法跑時多半**沒在跑**，見下方〈型別資訊〉；而且所有 detekt 規則推送前的新增告警檢查目前都**只記錄、不擋**（見〈機檢接線〉）。

> **核對邊界**：**已核對**（2026-11-04，本機 detekt 1.23.8）：協程與效能兩組規則的名稱、預設開關、要不要型別資訊。**未核對**：其餘（含 R16 的 compose-rules 條數、Slack compose-lints）——接入時以該工具當前的規則清單為準。
> REVISIT:2027-03-01 detekt 2.0 出正式版沒；出了就重核協程組，並把 R12 標「2.0 才有」的兩條改成可開。

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
- 機檢：`detekt:SuspendFunSwallowedCancellation`（預設關，要開；要型別資訊）——★只抓「runCatching 裡呼叫 suspend」★，上面壞例那種 `try { } catch (e: Exception)` 它不抓（detekt 1.23.8 官方規則頁）；而且 Kotlin 標準庫 2.2 以上時補了型別資訊也不響（detekt 1.23.8 限制，2026-11-04 逐版實測）。try/catch 那型要靠審查，或第三方 structured-coroutines 的 `CancellationExceptionSwallowed`

### R11. 禁 `GlobalScope`；活過畫面的工作用注入的應用級 scope
- 機檢：`detekt:GlobalCoroutineUsage`（預設關，要開；**不要型別資訊**，一般接法就會響）

### R12. 其餘機檢組（開了不等於有在跑，見〈型別資訊〉）
`SleepInsteadOfDelay`（協程內用 delay 不用 Thread.sleep，預設開，要型別資訊加 JDK 位置）、`RedundantSuspendModifier`（沒暫停點就拿掉 suspend，預設開，要型別資訊）。`CoroutineLaunchedInTestWithoutRunTest`（測試協程要包 runTest）**只有 detekt 2.0 才有，1.23.8 寫進設定會讓 detekt 整個拒跑**，1.23 先靠審查或 structured-coroutines 的 `RunBlockingInsteadOfRunTest`。runBlocking **不全面禁**：`ForbiddenMethodCall` 分不出在不在 suspend 裡，而 OkHttp Authenticator 這類同步介面裡橋接 suspend 是正當用法；suspend 內的 runBlocking 靠審查，或 structured-coroutines 的 `RunBlockingInSuspend`。
另兩條靠審查：CPU 密集迴圈內定期 `ensureActive()`（取消是合作式的）；`Job()/SupervisorJob()` 不當參數傳進 launch（要 supervisor 語意用 `supervisorScope {}`）。

## 三、Compose

### R13. 收流一律 `collectAsStateWithLifecycle()`
`collectAsState()` 在 App 退到背景時照樣收集，浪費電和網路——且要跟 R3 的 `WhileSubscribed` 成對才生效。
- 機檢：`detekt:ForbiddenMethodCall` 配置完整名稱 `androidx.compose.runtime.collectAsState`（只寫 `collectAsState` 不報錯也不響；規則放 `style:` 底下；要型別資訊，classpath 要有 Compose runtime）

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

---

## 機檢接線（一次設好，CI 自動把關）

detekt 設定要點（`--build-upon-default-config` 之上；lumos-toolchain 分發的共用設定已含這些，自己寫的話照抄）：
```yaml
coroutines:
  GlobalCoroutineUsage: { active: true }
  SuspendFunSwallowedCancellation: { active: true }
  SuspendFunWithCoroutineScopeReceiver: { active: true }
style:
  ForbiddenMethodCall:
    active: true
    methods:
      - "androidx.compose.runtime.collectAsState"
```
- 自有設定要跟共用設定疊加：用逗號合成一個 `--config a.yml,b.yml`（分開寫兩次 `--config` 會拒跑）；清單類欄位（例上面的 methods）後面那份整份蓋掉前面那份，不合併、不警告。
- 加掛 compose-rules（detekt plugin jar）補 R16 整組。
- 專案把 detekt 指令宣告進 `.lumos/lint.json`，`lumos pitfalls --diff` 會吃 SARIF、命中行進審查 manifest。★但推送前的新增告警檢查對 detekt 目前只記錄不擋★（沒有 `{LINT_FILES}` 就只記錄；有的話多檔時 detekt 拒跑、檢查放行）——`lumos lint-check` 與健檢會照指令字面把這些印出來。

### 型別資訊（detekt 有開≠有在跑）

- **是什麼**：detekt 很多規則要知道每個呼叫的型別才判得了。指令列要帶 `--classpath <依賴 jar，冒號分隔>`（簡寫 `-cp`）與 `--jdk-home <JDK 路徑>`；沒帶時這些規則**安靜跳過，不報錯也不警告**（detekt 官方型別解析文件：沒有型別解析時要型別的規則不會跑）。`--jvm-target` 實測不影響。
- **哪些要**：上面標「要型別資訊」的都要；`GlobalCoroutineUsage`、`ForEachOnRange` 不要。
- **怎麼取得**：一般 JVM 專案可用 Gradle 印出依賴清單（絕對路徑，相對路徑放在第一個以外的位置會被靜默忽略）；Gradle 外掛的 `detekt<變體>` 任務（例 `detektMain`、`detektDebug`）自帶型別，純 `detekt` 任務沒有。**Android 專案的依賴散在建置快取，目前沒有能接進推送前檢查的現成取法。**
- **版本限制**：Kotlin 標準庫 2.2 以上時，`SuspendFunSwallowedCancellation` 與標準庫函式的 `ForbiddenMethodCall` 補了型別資訊也不響（detekt 1.23.8 內建編譯器太舊）。

REVISIT:[when-status:Projects/Android的detekt推送前真的擋_計劃=done][by:2027-03-01] 推送前真的擋落地了，把本節與機檢接線段「推送時只記錄不擋」「Android 沒有現成取法」改掉

## 審查鏡頭（code-loop 用）

給審查員的一句 framing：「對照 kotlin-idioms 的 R1–R18 逐條掃這份 diff；**finding 必須引用條號**（如『違反 R1：`loadA()`/`loadB()` 無資料依賴卻串聯』），引用不出條號的風格意見不要標。」——執法不立法，品味之爭擋在門外。

## 誠實邊界

1. 最重要的三條（R1 並行、R2 combine、R8 main-safe）恰好都不可機檢——「無依賴」「該不該合成」是語意判斷，這份文件＋審查鏡頭是唯一防線，這正是它存在的理由。
2. 機檢規則抓形狀不抓意圖：過了 detekt 不代表寫得好。
3. 本文件不裁框架。發現某條規則與專案當地慣例衝突時：當地慣例贏，但把衝突記進該專案圖譜（可能是當地的技術債，也可能是本文件該修）。
4. 回填：被人工糾正的寫法先記進該專案圖譜；確認它在多數專案都會再犯（不是單次個案），才走 [[Projects/idioms自維護迴路_計劃]] 的候選流程加進本文件。
