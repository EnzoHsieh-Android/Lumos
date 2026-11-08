---
type: project
status: doing
created: 2026-11-09
updated: 2026-11-09
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
  - risk/守衛面
related:
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Systems/kotlin規則包]]"
  - "[[Projects/Android資安靜態檢查補齊第三批_計劃]]"
lands_in:
  - Systems/kotlin規則包
---
# Android形狀列補規則_計劃

> 白話:型錄裡有 15 列「有出處、看形狀判得出、但還沒有任何檢查」的壞寫法。2026-11-09 逐列查了現成檢查(Android Lint、androidx 各函式庫自帶的 lint、detekt、compose-rules、Slack compose-lints)與權威出處:15 列都沒有 CI 跑得到的現成檢查;其中 4 列出處直接講到那個寫法、而且單一檔案的語法樹就認得出——多筆 Deferred 逐一 await(API-2)、DisposableEffect 的 onDispose 是空的(UI-33)、同型別多個 Hilt 綁定只有部分加限定詞(ARCH-59)、EntryPointAccessors 的 fromX 跟 entry point 的 @InstallIn 元件不對應(ARCH-62)。這 4 條寫成 ast-grep 規則,先放只登記不擋的目錄,照前幾批的量法在樣本外量誤報,過了升級條件的才改成推送前會擋。其餘 11 列寫明為什麼不寫(要跨檔、讀 XML 或 Gradle,或出處要推論才接得上)。

PRIOR-ART: 現成檢查逐列查過(androidx compose/runtime/runtime-lint 16 支、work/work-lint 10 支、navigation-runtime-lint 6 支 Detector,detekt 官方 coroutines 規則集 9 條,compose-rules 與 Slack compose-lints 規則頁),15 列都沒有;API-2 只有 IntelliJ 的 IDE 檢查 MapAwaitOnCollectionOfDeferred,CI 與命令列不跑。型錄 API-2 現成規則欄寫的「detekt SequentialAsyncAwait」在 detekt 規則集查不到,照查證結果更正。量法沿用第一到三批(樣本外語料排除已出現過的 repo,每個 repo 最多抽一處、固定種子抽 40 處,升級條件命中 ≥20、誤報 ≤10%,誤報比例=誤報÷判讀數)與 [[Projects/Android不接閘資安規則重量_計劃]] 的判準 v2 寫法(範例碼只看路徑、排除教材與掃描器固件、同源只抽一處)。規則寫法借規則包既有的 `inside`/`has` 關係規則,不新增機制。
RETIRE-IF: Android Lint、androidx 函式庫 lint、detekt 或 compose-rules 出了同一種檢查 → 該條自寫規則撤掉、型錄改指現成檢查;會擋的那幾條在消費專案推送前一個月內被放行(lint-waive)超過三成 → 降回只登記重量。

## 用詞

- **規則包**:`configs/ast-grep/kotlin-android/`。`rules/` 收 error 與 warning 等級,消費專案照範本宣告 `sgconfig.yml`(只含 `rules/`)後,**新增告警閘**(推送前把改動前後各掃一次、只擋這次新增的告警)擋其中 error 等級的新告警;`rules-unwired/` 不在範本宣告裡,只登記、不擋。**lint-waive**:`lumos lint-waive <指紋> --note` 對一筆告警留帳放行。**型錄**:`skills/kotlin-idioms/checks-catalog.md`,每列寫壞寫法、標準寫法、後果、出處;**通電批次欄**寫這列由哪一批接上機械檢查(值的寫法見型錄〈輸入與口徑〉:「告警帶寫法=批一」是會擋的規則已上線、「告警帶寫法=未接(…)」是規則在 `rules-unwired/` 或還沒有規則),**實測狀態欄**寫量過的數字;**〈統計〉**是型錄末尾那一節,規則包條數、各等級條數、不接閘條數、被會擋規則守到的列數、待查證列數由型錄自檢核對;**〈待查證〉**是現成規則欄還寫著「待查」的列的清單。
- **單檔語法**:ast-grep 只看一支檔的語法樹,沒有型別資訊、不跨檔、不讀 XML 與 Gradle。
- **樣本內**:調規則形狀時看過的語料。**樣本外**:形狀定案後另撈、排除先前出現過的 repo 的語料,判升級只看這一份、只用一次(**保留集**的用法:定案後只用一次、不拿來調形狀)。**升級條件**:樣本外命中 ≥20、誤報 ≤10%。**判讀代理**:派去逐處打開前後文判真問題、誤報、判不準的子代理;**判不準**不算真問題,留在誤報比例的分母。
- **限定詞**:Hilt/Dagger 的 qualifier,例如 `@Named("auth")` 或自訂的 `@AuthClient`,用來分辨同型別的多個綁定。
- **壞例、好例樣本**:規則包每條規則在 `samples/bad/<id>/` 放至少 2 處會報的寫法、`samples/good/<id>/` 放至少 2 段頂格宣告且一處都不報的寫法(規則包自測的要求);好例裡容易被誤會成壞寫法的,其他規則的好例樣本慣例在註解寫「容易誤報:」。只登記與覆核級規則另可放檔名 `review-fp-` 開頭的樣本,記下**已知會報**的誤報寫法,自測不把它算成好例失敗。
- **逐例表**:測試裡寫死「哪支檔、哪段程式、哪條規則、報在哪幾行」的表,預期值不拿規則自己算。

## 範圍

1. **四條新規則**(先放 `rules-unwired/`,等級 hint;訊息照規則包既有句式「[型錄編號]錯在哪;改用 …」):

   | 型錄列 | 規則 | 形狀 | 出處原文 |
   |---|---|---|---|
   | API-2 | `kt-map-await-deferred` | `$L.map { it.await() }`、`$L.map { $X -> $X.await() }`、`$L.forEach { it.await() }`、`$L.forEach { $X -> $X.await() }` | awaitAll KDoc:This function is not equivalent to deferreds.map { it.await() } which fails only when it sequentially gets to wait for the failing deferred |
   | UI-33 | `kt-disposable-effect-empty-dispose` | `DisposableEffect(...) { … }` 裡的 `onDispose { }` 是空的 | Compose side-effects 頁:Having an empty block in onDispose is not a good practice |
   | ARCH-59 | `kt-hilt-binding-missing-qualifier` | 同一個 class/object 本體裡,有 `@Provides`/`@Binds` 函式身上只有已知非限定詞註解(Provides、Binds、Singleton、Reusable、JvmStatic、…Scoped)、另一個回傳同型別的 `@Provides`/`@Binds` 帶了別的註解;報沒加的那個 | Hilt 頁:if you add a qualifier to a type, add qualifiers to all the possible ways to provide that dependency. Leaving the base or common implementation without a qualifier is error-prone |
   | ARCH-62 | `kt-entrypoint-accessor-mismatch` | `EntryPointAccessors.fromApplication/fromActivity/fromFragment/fromView($$$, I::class.java)`,同檔 `I` 的 `@InstallIn` 元件不是那個 fromX 對應的元件(fromApplication↔SingletonComponent、fromActivity↔ActivityComponent、fromFragment↔FragmentComponent、fromView↔ViewComponent) | Hilt 頁:Make sure that the component you pass as a parameter and the EntryPointAccessors static method both match the Android class in the @InstallIn annotation |

   - 每條附壞例(至少 2 處)、好例(至少 2 段)樣本;好例裡「不報」的寫法照其他規則好例的慣例寫成「容易誤報:」註解。API-2 另放一份 `review-fp-` 樣本,記下 Play services `Task.await()` 這個已知誤報。
   - ARCH-59 的「已知非限定詞註解」清單寫死在規則裡;清單外的註解一律當成限定詞(寧可少報)。
2. **型錄改寫**:四列的現成規則欄改成型錄既有寫法「自寫 ast-grep <規則 id>」;通電批次改成「告警帶寫法=未接(規則在 rules-unwired/:還沒在真專案量過誤報)」;API-1、API-2 兩列都拿掉「detekt SequentialAsyncAwait」(detekt 規則集查不到),API-2 改寫 IntelliJ 檢查名 MapAwaitOnCollectionOfDeferred(只在 IDE 跑);API-2 的「待查」字樣因此消失,從〈待查證〉拿掉那一列。〈統計〉跟著改:規則包條數、hint 條數、不接閘條數各加 4(量完搬到 `rules/` 的再照實改等級條數與被會擋規則守到的列數),待查證與規則代號待查各減 1。量完照第 4 點再改。
3. **其餘 11 列寫明不寫的理由**(實測狀態欄補一句,通電批次不變):API-7、UI-18、UI-51、ARCH-43、ARCH-58、DATA-8、DATA-9、DATA-23、DATA-34、TEST-38、PERF-8。理由分三種:要跨檔或型別(UI-18、DATA-8、DATA-9、DATA-23、DATA-34、PERF-8)、要讀 XML 或 Gradle(ARCH-43、TEST-38)、形狀分不出正當用法或出處要推論(API-7 的 `retry()` 分不出是不是 Flow、UI-51 看不到筆數、ARCH-58 出處只說注入在 super.onCreate() 發生,沒說之前讀會怎樣)。
4. **量誤報與升級**:每條規則照前幾批的量法量一次:
   - 樣本內:用 GitHub 程式碼搜尋撈一份語料,看命中、把明顯誤報寫成排除;形狀定案後記規則檔雜湊。
   - 樣本外:另撈一份,排除樣本內與前幾批出現過的 repo;判準先寫定、算雜湊再撈。
   - 命中多的每個 repo 抽一處、固定種子抽 40 處;命中 20 多處全判。判讀代理乾淨脈絡、照判準逐處判真問題、誤報、判不準。
   - 過升級條件的規則搬到 `rules/`、等級改 error,型錄通電批次改「告警帶寫法=批一」;沒過的留在 `rules-unwired/`,通電批次改「未接(規則在 rules-unwired/:樣本外誤報超過一成或量不夠)」,實測狀態欄寫數字。
   - 證據放卷證 `governance/review-reports/android形狀列補規則/experiment/`(新增)。
5. **測試**:
   - 新增 `t_kotlin_shape_rows_rules`(新增):自己的逐例表,每例寫成一支**完整的 kt 檔**(含 package 與頂層宣告),用規則包設定檔實跑 ast-grep,比對**報在哪幾行**;同時驗四列型錄現成規則欄的規則 id 在規則包裡存在、在計劃寫的目錄。不擴充 `t_kotlin_rulepack_security_rules` 的逐例表:那張表把每段程式包進一個函式(`fun case(...) { … }`),Kotlin 不准在函式裡宣告 interface,ARCH-62 的例子放不進去;改它的包法會牽動既有一百多例。
   - 樣本自測 `t_kotlin_rulepack_samples` 照舊驗壞例報、好例不報。
   - 統計測試 `_KT_STATS_LINES` 的寫死值照新數改;待查證統計那支用 `| API-2 | IJ:「Use awaitAll()` 當改壞錨點的案例,API-2 拿掉後換一列仍在〈待查證〉的當錨點。
6. **圖譜**:[[Systems/kotlin規則包]] 不接閘目錄那行(現在寫共 25 條)的條數與規則清單;[[Projects/Android協程與API寫法機械檢查標準_計劃]] 補一行指向本篇。

**不做**:不寫跨檔或讀 XML、Gradle 的規則;不寫 ARCH-58(出處不直接);不改新增告警閘。

## 實驗(寫計劃前的最小實驗,2026-11-09,ast-grep 0.51.1)

- 四條草稿規則各拿壞寫法與好寫法試跑:壞寫法都報、好寫法都不報。
- API-2:Google Play services 的 `Task` 也有 `await()`,`tasks.map { it.await() }` 會被報——單檔看不到型別,這是預期的誤報來源,樣本外量出比例再判。
- ARCH-62:Kotlin 解析器有一個限制——interface 本體寫在同一行(`interface X { fun f(): F }`)而且上面掛兩個以上註解時,整段被解析成運算式,認不出是 interface 宣告;本體分多行就正常。後果是漏報,不是誤報。
- ARCH-59:只比對函式宣告直接帶的回傳型別,參數型別不會被當成回傳型別。
- GitHub 程式碼搜尋粗估(2026-11-09):`onDispose { }` 約 5976 支檔、`onDispose {}` 約 5416、`.map { it.await() }` 約 2116、`EntryPointAccessors.fromApplication` 約 7936、`fromActivity` 約 343、同檔有 `@Provides` 與 `@Named` 約 10432。命中數應能到 20 以上。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| API-2 | kotlinx.coroutines awaitAll KDoc | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/await-all.html |
| UI-33 | Compose side-effects 官方頁 | https://developer.android.com/develop/ui/compose/side-effects |
| ARCH-59 | Hilt 官方頁(限定詞) | https://developer.android.com/training/dependency-injection/hilt-android |
| ARCH-62 | Hilt 官方頁、Dagger entry points 頁 | https://developer.android.com/training/dependency-injection/hilt-android 、https://dagger.dev/hilt/entry-points.html |
| 樣本外語料只用一次、不拿來調形狀 | Dwork 等人 | https://ar5iv.labs.arxiv.org/html/1506.02629 |

## 實務隱患

- 守衛面:量完過了升級條件的規則會搬到 `rules/`,消費專案推送前會多擋這種寫法;沒過的不影響推送。誤擋的出口是 lint-waive 留帳放行,RETIRE-IF 第二句管放行太多的情形。
- 已排除:金流:不碰付款。
- 已排除:對外送出:不寄信、不呼叫外部服務(語料下載只在實驗階段)。
- 已排除:不可逆:全部是 repo 內的文字檔,退回提交即還原。
- 效能:四條規則多一次語法樹比對;ARCH-59、ARCH-62 的 `inside` 往上找到檔案根再往下找,檔案很大時比對次數隨函式數成長,規則包自測與推送前掃描的時間要量一次。
- 併發寫入不考慮:工具鏈單人、AI 依序操作。

## 驗收條款

- [S1] 當跑規則包樣本自測時,四條新規則 應 報壞例、不報好例 [test:t_kotlin_rulepack_samples]
- [S2] 當用逐例表掃完整的 kt 檔時,四條新規則 應 只在逐例表寫的那幾行報 [test:t_kotlin_shape_rows_rules]
- [S3] 當真型錄跑型錄自檢時,問題數 應 是 0 [test:t_kotlin_catalog_rows_wired]
- [S5] 當讀真型錄與規則包時,API-2、UI-33、ARCH-59、ARCH-62 四列的現成規則欄 應 寫著「自寫 ast-grep <規則 id>」而且那個 id 在規則包裡存在 [test:t_kotlin_shape_rows_rules]
- [S4] 當讀型錄那四列的實測狀態欄時,命中、判讀、誤報數 應 跟卷證 `experiment/judge-*.md` 逐處判讀原文數出的數一致 [manual:逐列對照卷證判讀原文與命中檔筆數,設計審或代碼審核一次]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S2 | `suspend fun f(ds: List<Deferred<Int>>) = ds.map { it.await() }` | kt-map-await-deferred 報 | awaitAll KDoc |
| S2 | `suspend fun f(ds: List<Deferred<Int>>) = ds.awaitAll()` | 不報 | awaitAll KDoc 的標準寫法 |
| S2 | `DisposableEffect(Unit) { log("x"); onDispose { } }` | kt-disposable-effect-empty-dispose 報 | side-effects 頁 |
| S2 | `DisposableEffect(o) { o.add(obs); onDispose { o.remove(obs) } }` | 不報 | side-effects 頁的範例 |
| S2 | 同一個 object 裡 `@Provides fun a(): OkHttpClient` 與 `@Provides @Named("x") fun b(): OkHttpClient` | kt-hilt-binding-missing-qualifier 只報 a 那一行 | Hilt 限定詞段 |
| S2 | 同一個 object 裡兩個沒加限定詞的 `@Provides fun a(): OkHttpClient`、`fun c(): OkHttpClient` 與一個 `@Provides @Named("x") fun b(): OkHttpClient` | 報 a、c 兩行,不報 b | 同上:報沒加的那幾個 |
| S2 | 同一個 object 裡 `@Provides fun a(): OkHttpClient` 與 `@Provides fun g(): Gson` | 不報 | 型別不同 |
| S2 | 同檔 `@InstallIn(ActivityComponent::class)` 的 `interface E` 與 `EntryPointAccessors.fromApplication(ctx, E::class.java)` | kt-entrypoint-accessor-mismatch 報 | Hilt EntryPointAccessors 段 |
| S2 | 同檔 `@InstallIn(SingletonComponent::class)` 的 `interface E` 與 `EntryPointAccessors.fromApplication(ctx, E::class.java)` | 不報 | 同上 |
| S2 | `EntryPointAccessors.fromApplication(ctx, Other::class.java)`,`Other` 不在同檔 | 不報 | 單檔看不到 @InstallIn |

## 回退

退回本計劃的提交,逐項是:
- 規則包:四條新規則與它們的壞例好例樣本;量完搬到 `rules/` 的那幾條。
- 型錄:四列的現成規則、通電批次、實測狀態欄;API-1、API-2 的現成規則更正與 API-2 移出〈待查證〉;11 列實測狀態的補句;〈統計〉。
- 測試:新增的 `t_kotlin_shape_rows_rules`、統計寫死值、待查證那支的改壞錨點。
- 圖譜:Systems/kotlin規則包 的不接閘那行;機械檢查標準計劃的指向;本篇。
- 卷證留著。

## 天花板

- 單檔語法看不到型別:API-2 會報 Play services `Task`、`ListenableFuture` 這類也有 `await()` 的接收者。
- ARCH-59、ARCH-62 只看同一支檔:綁定或 entry point 分在不同檔時漏報;ARCH-62 遇到一行寫完又掛兩個註解的 interface 會漏報(解析器限制)。
- ARCH-59 的非限定詞清單寫死,專案自訂的範圍註解(不以 Scoped 結尾)會被當成限定詞,少報。
- 誤報只量命中裡的比例,漏報沒量。

REVISIT:2027-05-09 量一次這四條的漏報:在新語料裡用文字搜尋找出該報沒報的寫法(跨檔的 entry point、分檔的綁定、一行寫完的 interface),逐處判是不是形狀漏的,寫進型錄實測狀態欄

## 審計修正紀錄
