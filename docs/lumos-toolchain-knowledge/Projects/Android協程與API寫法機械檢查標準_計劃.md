---
type: project
status: todo
created: 2026-11-04
updated: 2026-11-04
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
related:
  - "[[Projects/Android協程與API協同機械審_調研]]"
  - "[[Projects/Android的detekt規則說實話_計劃]]"
  - "[[Projects/Android的detekt推送前真的擋_計劃]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/棧別提問表態閘]]"
lands_in:
  - Systems/linter精選目錄
  - Systems/棧別提問表態閘
---
# Android協程與API寫法機械檢查標準_計劃

> 白話:Android(Kotlin 協程)的「標準寫法」原本大多只寫在 kotlin-idioms 慣例文件裡、靠審查員記得看。這份計劃把三類議題——①同一個功能裡多支 API 的同步非同步、②資料流合併、③狀態保存——加上底層的協程紀律與 Compose 收集,逐條窮舉成「機器怎麼查」:能開現成規則的就開、能列出壞寫法形狀的就自己寫結構比對規則、語意上只能靠跑的就給測試範本,真的只能人看的才留給人,而且寫明為什麼。目標是先把機械能查的鋪滿,減少人工審查。出身:[[Projects/Android協程與API協同機械審_調研]];使用者 2026-11-04 要求「就算窮舉也要把標準寫法的檢查制定下來」「先把機械能檢查的鋪完」。

PRIOR-ART: ①現成規則先查過四個規則庫逐條對照(detekt 1.23.8 官方規則頁、structured-coroutines、Sonar Kotlin、androidx 隨函式庫附帶的 lint、compose-rules、Slack compose-lints),能開的不自寫。②自寫規則的判準照抄其他生態已上線的做法:「互不依賴卻串著等」照 react-doctor 的 server-sequential-independent-await(相鄰兩句都在等、第二句沒讀到第一句宣告的名字才報)與 Vercel NO_SERIAL_ASYNC_CALLS(保守,寧漏不誤報);「舊回應蓋新資料」借 ESLint require-atomic-updates 的「先讀、等、再寫回」形狀。③承載工具用 ast-grep(結構比對、輸出 SARIF,[[Systems/linter精選目錄]] 已收為「事故固化引擎」)為主,需要跨條件綁定變數的那條用 semgrep;兩者都收空白分隔的多個檔,接 `.lumos/lint.json` 的 `{LINT_FILES}` 就能進推送前的新增告警檢查,不踩 detekt 只收逗號分隔的坑([[Issues/推送閘對Android的detekt只記錄不擋]])。④語意題用 kotlinx-coroutines-test 的虛擬時間與 Turbine 寫測試範本,這是官方測試文件的做法。來源見〈來源〉。
RETIRE-IF: 某條自寫規則上線三個月,在消費專案的放行帳裡誤報(被放行並寫理由)多過真報,就把那條降成提問或拿掉;detekt 2.0 或 structured-coroutines 的現成規則涵蓋到某條自寫規則時,換成現成的、刪掉自寫那條。

## 手段分四級

| 級 | 意思 | 會不會擋 |
|---|---|---|
| A 現成規則 | 開別人維護的 lint 規則 | detekt 那批要等 [[Projects/Android的detekt推送前真的擋_計劃]] 才擋;androidx lint 走 Android Lint |
| B 自寫結構規則 | 列出壞寫法的語法形狀,用 ast-grep/semgrep 比對 | 接 `{LINT_FILES}` 後推送前就擋新增的 |
| C 測試範本 | 給一段可抄的測試,斷言行為(虛擬時間、呼叫次數、最終狀態) | 綁進測試後由測試擋 |
| D 人審 | 機器判不了語意,用棧別提問逼審查員作答 | 推送前要表態 |

## 一、同一個功能裡多支 API 的同步非同步(一次性呼叫)

| 編號 | 要守的寫法 | 壞寫法形狀(要抓的) | 不報的 | 手段 | 本機實測 |
|---|---|---|---|---|---|
| API-1 | 互不依賴的呼叫要並行 | suspend 函式裡相鄰兩句 `val a = x.f(…)`、`val b = y.g(…)`,第二句的參數、具名參數、接收者都沒用到 a | 第二句任何位置用到 a;不在 suspend 函式裡 | B(semgrep,提示級)+ C(虛擬時間:假 API 各延遲 100,斷言總時間 100 不是 200) | 2026-11-04 樣本 2 壞例全中,3 個有依賴的好例(位置參數、具名參數、接收者)不報 |
| API-2 | 多筆同型要用 `awaitAll()` | `.map { it.await() }`、`forEach { it.await() }` | `awaitAll()` | B | 未寫 |
| API-3 | async 的結果要有人接 | 單獨一句 `async { }` 結果沒人用 | 有接 | A:structured-coroutines `UnusedDeferred`;IDE `DeferredResultUnused` | 未在本機跑 |
| API-4 | 一支失敗時連坐或不連坐要選對 | `supervisorScope { … async … await }` 沒有 try 包住 await | — | D(業務語意)+ C(讓一支假 API 丟例外,斷言另一支被取消或沒被取消,照需求) | — |
| API-5 | HTTP 整個呼叫要有上限 | `OkHttpClient.Builder()…build()` 鏈上沒有 `callTimeout(`(OkHttp 預設 0=沒上限) | 有 callTimeout | B(ast-grep) | 樣本壞例中、好例不報 |
| API-6 | Ktor 要裝逾時 | `HttpClient(…) { }` 裡沒有 `install(HttpTimeout)` | 有裝 | B | 未寫 |
| API-7 | 重試要有上限與退避 | Flow 的 `retry()` 不帶次數;`while (true)` 裡重送;重試迴圈用固定 `delay(常數)` | 帶次數與遞增延遲 | B | 未寫 |
| API-8 | 舊回應不能蓋新資料 | ViewModel 裡帶參數、非 private 的函式每次呼叫都 `viewModelScope.launch { }` 寫 state,而且函式裡沒有取消前一個 Job | 先 `job?.cancel()`;改用 `collectLatest`/`flatMapLatest`/`mapLatest` | B(ast-grep)+ C(q1 延遲 300、q2 延遲 100,先 q1 後 q2,斷言最後是 q2 且從沒出現 q1) | 樣本壞例中、先取消的好例不報 |
| API-9 | 離開畫面要取消在途請求 | `GlobalScope.`、當場 `CoroutineScope(…).launch`、Fragment 裡用 `lifecycleScope` 而不是 `viewLifecycleOwner.lifecycleScope` | viewModelScope、注入的應用級 scope(要能標豁免) | A:detekt `GlobalCoroutineUsage`、structured-coroutines `InlineCoroutineScope`、androidx `UnsafeRepeatOnLifecycleDetector`;B 補 Fragment 那型 + C(onCleared 後斷言假 API 收到取消) | GlobalScope 已實測(detekt 不需型別就響) |
| API-10 | 防重複送出 | `onClick` 觸發的函式裡直接 `launch`,沒有「進行中」判斷(`if (inFlight) return`、`job?.isActive`) | 有判斷 | D + C(同一虛擬時間連叫兩次 submit,斷言假 API 只被叫一次);B 太容易誤報,不做 | — |
| API-11 | callback 轉 suspend 要能取消 | `suspendCoroutine { }`;`suspendCancellableCoroutine { }` 裡沒有 `invokeOnCancellation` | 有註冊取消 | B(ast-grep);IDE 有 `SuspendCoroutineLacksCancellationGuarantees` | 樣本兩壞例中、好例不報 |
| API-12 | callbackFlow 要 awaitClose | `callbackFlow { }` 裡沒有 `awaitClose` | 有 | B(ast-grep);執行期本來就會丟例外,靜態提早抓 | 樣本壞例中、好例不報 |
| API-13 | 阻塞呼叫不在協程裡直接跑 | `Thread.sleep`、`Call.execute()`、`Future.get()` 出現在 suspend 函式或 `launch` 裡、沒包 `withContext` | — | A:detekt `SleepInsteadOfDelay`(要 JDK 型別)、structured-coroutines `BlockingCallInCoroutine`、`RunBlockingInSuspend`;執行期 StrictMode | SleepInsteadOfDelay 已實測 |

## 二、資料流合併(持續更新的狀態)

| 編號 | 要守的寫法 | 壞寫法形狀 | 不報的 | 手段 | 本機實測 |
|---|---|---|---|---|---|
| FLOW-1 | 合成用 combine,不巢狀收集 | `.collect { }` 或 `.collectLatest { }` 裡面又 `.collect { }`/`.collectLatest { }` | `combine(a, b) { }` | B(ast-grep) | 樣本壞例中、combine 好例不報 |
| FLOW-2 | zip 只用在一對一配對 | 對狀態流(`StateFlow`、`stateIn` 出來的)用 `.zip(` | 冷流的配對 | B 只能看名字猜型別,誤報高 → 降成 D 提問 | — |
| FLOW-3 | combine 的每個來源都要有初始值 | — | — | C(讓其中一個來源永遠不發,斷言畫面狀態仍有初始值、不卡在載入) | — |
| FLOW-4 | `flow { }` 裡不換執行緒 | `flow { }` 裡出現 `withContext(` | `.flowOn(…)` | B(ast-grep);執行期本來就會炸 | 樣本壞例中、flowOn 好例不報 |
| FLOW-5 | 回傳 Flow 的函式不標 suspend | `suspend fun x(): Flow<…>` | — | A:detekt `SuspendFunWithFlowReturnType`(要型別) | 已實測(帶型別響) |
| FLOW-6 | 背壓策略要寫明 | — | — | D(語意) | — |
| FLOW-7 | 狀態用 StateFlow、事件用 SharedFlow 或 Channel | — | — | D | — |

## 三、狀態保存

| 編號 | 要守的寫法 | 壞寫法形狀 | 不報的 | 手段 | 本機實測 |
|---|---|---|---|---|---|
| STATE-1 | 讀改寫用原子 `update { }` | `X.value = X.value.copy(…)`、`X.value = X.value + …` | `X.update { it.copy(…) }` | B(ast-grep) | 樣本壞例中、update 好例不報 |
| STATE-2 | 不公開可變狀態 | 非 private 的屬性 `= MutableStateFlow(…)` | private | B(ast-grep);structured-coroutines `MutableFlowExposed`;Sonar S6305 | 樣本壞例中、private 不報 |
| STATE-3 | `stateIn`/`shareIn` 只建一次 | 寫在函式本體或 `get() =` 裡 | 類別屬性 | B(ast-grep) | 樣本函式那型中、屬性那型不報;`get() =` 那型未寫 |
| STATE-4 | 共享策略預設 WhileSubscribed(5_000) | `SharingStarted.Eagerly`(要一行理由才放行) | WhileSubscribed | B(ast-grep);structured-coroutines `StateInWithEagerlyStrategy` | 樣本中 |
| STATE-5 | 畫面收集跟生命週期 | `collectAsState()`;`lifecycleScope.launch { flow.collect }` 沒包 `repeatOnLifecycle` | `collectAsStateWithLifecycle()` | A:detekt `ForbiddenMethodCall`(要型別,[[Projects/Android的detekt規則說實話_計劃]] 補開)、structured-coroutines lint `CollectAsStateWithoutLifecycle`、androidx `RepeatOnLifecycleWrongUsage` | collectAsState 已實測(帶 Compose runtime 型別響) |
| STATE-6 | 被系統殺掉後能還原 | — | — | C(用同一個 `SavedStateHandle` 重建 ViewModel,斷言使用者輸入與選中 id 還在)+ D(哪些欄位要存是業務決定) | — |

## 四、協程紀律(三類共用的底層)

| 編號 | 要守的寫法 | 手段 |
|---|---|---|
| CO-1 | Dispatcher 可注入 | A:detekt `InjectDispatcher`(要型別) |
| CO-2 | 不吞取消 | A:detekt `SuspendFunSwallowedCancellation`(只抓 runCatching 那型,要型別)+ structured-coroutines `CancellationExceptionSwallowed`(抓 try/catch 那型) |
| CO-3 | Job()/SupervisorJob() 不傳進 launch | A:structured-coroutines `JobInBuilderContext`;Sonar S6306 |
| CO-4 | CPU 長迴圈要讓出取消點 | A:structured-coroutines `LoopWithoutYield` |
| CO-5 | suspend 函式 main-safe | D(誰阻塞誰負責);A 只抓得到已知阻塞 API(見 API-13) |
| CO-6 | 測試協程用 runTest | A:structured-coroutines `RunBlockingInsteadOfRunTest`;detekt 2.0 的 `CoroutineLaunchedInTestWithoutRunTest` 等正式版 |

## 五、Compose 收集與清單(跟狀態保存相鄰)

| 編號 | 要守的寫法 | 手段 |
|---|---|---|
| UI-1 | Lazy 清單給穩定 key | B(ast-grep:`items(` 沒有 `key =`)| 樣本壞例中、有 key 不報 |
| UI-2 | 組建畫面時不直接 launch、不在組建裡呼叫 Flow 運算子 | A:androidx `CoroutineCreationDuringComposition`、`FlowOperatorInvokedInComposition`(依賴函式庫就生效) |
| UI-3 | LaunchedEffect 的 key 選對 | B 提示級:`LaunchedEffect(Unit)` 本體讀到外層參數或 state;compose-rules `LambdaParameterInRestartableEffect` |

## 範圍

- 自寫規則包:放在本 repo 分發的 configs 底下(ast-grep 規則與 semgrep 那一條各一個資料夾),每條規則附壞例與好例樣本;規則包自己的測試用 ast-grep 內建的規則測試(valid/invalid 樣本)。
- 宣告範本:[[Systems/linter精選目錄]] 加 ast-grep 與 semgrep 的 `.lumos/lint.json` 範本(帶 `{LINT_FILES}`、輸出 SARIF),寫明哪些是提示級。
- 測試範本:kotlin-idioms 加一節〈機械驗證範本〉,把 C 級每條給一段可抄的測試。
- kotlin-idioms 每條規則的機檢欄改成指向本表編號。
- 棧別提問:Kotlin 補外呼逾時與重試題(照 Java 棧那題)、舊回應與重複送出題,觸發詞含 Retrofit、OkHttp、Ktor;D 級每條都要有一題對應。
- 現成規則 A 級裡的 structured-coroutines:先在一個消費專案試跑看誤報,不直接進共用設定。

**不做**:不改 detekt 的推送閘接法(那是推送前真的擋那案);不寫 detekt 自訂規則 jar(要 Kotlin 建置,ast-grep 能做到的形狀先用它);不碰消費專案。

## 實務隱患

- 提示級規則(API-1、UI-3)上線先當提示、不擋,放行帳累積後再決定升級。
- ast-grep 的子規則之間不共用變數,所以「第二句沒用到第一句」這種要綁名字的判準做不到,只能用 semgrep;兩種工具並存是刻意的,寫進範本說明。
- 只看語法分不出呼叫是不是 suspend,API-1 會把 suspend 函式裡兩句普通的取值也報出來;這是它降成提示級的原因。
- 消費專案要多裝兩個工具(ast-grep、semgrep),安裝方式寫進範本。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只在本機跑檢查
- 已排除:不可逆:新增規則與文件,退提交即回原狀

## 驗收條款(初稿,設計審前再定)

- [S1] 當對附帶的壞例樣本跑自寫規則包時,表上每條 B 級規則 應 各自至少命中一個壞例,對好例樣本 應 零命中 [manual:設計審前定測試名與做法,這版是草稿]
- [S2] 當 `.lumos/lint.json` 用範本宣告規則包、一次改兩支以上 kt 檔推送時,新增的壞寫法 應 被新增告警檢查擋下 [manual:設計審前定測試名與做法,這版是草稿]

## 來源

- detekt 1.23.8 規則:https://detekt.dev/docs/1.23.8/rules/coroutines
- structured-coroutines:https://github.com/santimattius/structured-coroutines
- Sonar Kotlin:https://github.com/SonarSource/sonar-kotlin
- androidx lint 索引:https://googlesamples.github.io/android-custom-lint-rules/checks/index.md.html
- compose-rules:https://mrmans0n.github.io/compose-rules/rules/
- react-doctor:https://react.doctor/docs/rules/react-doctor/server-sequential-independent-await
- Vercel:https://vercel.com/docs/conformance/rules/NO_SERIAL_ASYNC_CALLS
- ESLint require-atomic-updates:https://eslint.org/docs/latest/rules/require-atomic-updates
- OkHttp 預設逾時:https://square.github.io/okhttp/5.x/okhttp/okhttp3/-ok-http-client/
- kotlinx-coroutines-test:https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md

REVISIT:[when-status:Projects/Android協程與API寫法機械檢查標準_計劃=done][by:2027-03-01] 在一個消費專案量 API-1、UI-3 的誤報率(目前只在十幾段樣本上驗過),決定要不要升級成擋
