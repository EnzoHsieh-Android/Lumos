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

> 白話:型錄裡有 15 列「有出處、看形狀判得出、但還沒有任何檢查」的壞寫法。2026-11-09 逐列查了現成檢查(Android Lint、androidx 各函式庫自帶的 lint、detekt、compose-rules、Slack compose-lints)與權威出處:15 列都沒有 CI 跑得到的現成檢查;其中 4 列出處直接講到那個寫法、而且單一檔案的語法樹就認得出——對 Deferred 清單用 map 逐一 await(API-2)、DisposableEffect 沒有註冊任何東西卻寫了空的 onDispose(UI-33,既有規則 UI-32 管「有註冊卻留空」的那半)、同型別多個 Hilt 綁定只有部分加限定詞(ARCH-59)、EntryPointAccessors 的 fromX 跟 entry point 的 @InstallIn 元件不對應(ARCH-62)。這 4 條寫成 ast-grep 規則,先放只登記不擋的目錄,照前幾批的量法在樣本外量誤報:map 逐一 await 那條誤報 3/40、Hilt 限定詞那條誤報 0/40,都過條件,推送前會擋;空 onDispose 那條誤報 6/40、EntryPointAccessors 那條只命中 1 處,都留在只登記。其餘 11 列寫明為什麼不寫(要跨檔、讀 XML 或 Gradle,或出處要推論才接得上)。

PRIOR-ART: 現成檢查逐列查過(androidx compose/runtime/runtime-lint 16 支、work/work-lint 10 支、navigation-runtime-lint 6 支 Detector,detekt 官方 coroutines 規則集 9 條,compose-rules 與 Slack compose-lints 規則頁),15 列都沒有;API-2 只有 IntelliJ 的 IDE 檢查 MapAwaitOnCollectionOfDeferred,CI 與命令列不跑。UI-33 的另一半(有註冊監聽卻留空 onDispose)規則包已有會擋的 kt-compose-dispose-empty-cleanup(UI-32),本篇只補互補的那半,兩條共用同一份「什麼算註冊」的判斷。型錄 API-2 現成規則欄寫的「detekt SequentialAsyncAwait」在 detekt 規則集查不到,照查證結果更正。量法沿用第一到三批(樣本外語料排除已出現過的 repo,每個 repo 最多抽一處、固定種子抽 40 處,升級條件命中 ≥20、誤報 ≤10%,誤報比例=誤報÷判讀數)與 [[Projects/Android不接閘資安規則重量_計劃]] 的判準 v2 寫法(範例碼只看路徑、排除教材與掃描器固件、同源只抽一處)。規則寫法借規則包既有的 `inside`/`has` 關係規則與 `utils/` 共用判斷,測試擴充既有逐例表,不新增機制。
RETIRE-IF: Android Lint、androidx 函式庫 lint、detekt 或 compose-rules 出了同一種檢查 → 該條自寫規則撤掉、型錄改指現成檢查;會擋的那幾條在消費專案推送前一個月內被放行(lint-waive)超過三成 → 降回只登記重量。

## 用詞

- **規則包**:`configs/ast-grep/kotlin-android/`。`rules/` 收 error 與 warning 等級,消費專案照範本宣告 `sgconfig.yml`(只含 `rules/`)後,**新增告警閘**(推送前把改動前後各掃一次、只擋這次新增的告警)擋其中的新告警(error 與 warning 都擋,看的是規則放哪個目錄,不看等級;代碼審 r3 查新增告警閘程式確認);`rules-unwired/` 不在範本宣告裡,只登記、不擋。**lint-waive**:`lumos lint-waive <指紋> --note` 對一筆告警留帳放行。**型錄**:`skills/kotlin-idioms/checks-catalog.md`,每列寫壞寫法、標準寫法、後果、出處;**通電批次欄**寫這列由哪一批接上機械檢查(值的寫法見型錄〈輸入與口徑〉:「告警帶寫法=批一」是會擋的規則已上線、「告警帶寫法=未接(…)」是規則在 `rules-unwired/` 或還沒有規則),**實測狀態欄**寫量過的數字;**〈統計〉**是型錄末尾那一節,規則包條數、各等級條數、不接閘條數、被會擋規則守到的列數、待查證列數由型錄自檢核對;**〈待查證〉**是現成規則欄還寫著「待查」的列的清單。
- **單檔語法**:ast-grep 只看一支檔的語法樹,沒有型別資訊、不跨檔、不讀 XML 與 Gradle。
- **樣本內**:調規則形狀時看過的語料。**樣本外**:形狀定案後另撈、排除先前出現過的 repo 的語料,判升級只看這一份、只用一次(**保留集**的用法:定案後只用一次、不拿來調形狀)。**升級條件**:樣本外命中 ≥20、誤報 ≤10%。**判讀代理**:派去逐處打開前後文判真問題、誤報、判不準的子代理;**判不準**不算真問題,留在誤報比例的分母。
- **限定詞**:Hilt/Dagger 的 qualifier,例如 `@Named("auth")` 或自訂的 `@AuthClient`,用來分辨同型別的多個綁定。
- **壞例、好例樣本**:規則包每條規則在 `samples/bad/<id>/` 放至少 2 處會報的寫法、`samples/good/<id>/` 放至少 2 段頂格宣告且一處都不報的寫法(規則包自測的要求);好例裡容易被誤會成壞寫法的,其他規則的好例樣本慣例在註解寫「容易誤報:」。只登記與覆核級規則另可放檔名 `review-fp-` 開頭的樣本,記下**已知會報**的誤報寫法,自測不把它算成好例失敗。
- **逐例表**:測試裡寫死「哪支檔、哪段程式、哪條規則、報在哪幾行」的表,預期值不拿規則自己算。

## 範圍

1. **四條新規則**(先放 `rules-unwired/`,等級 hint;訊息照規則包既有句式「[型錄編號]錯在哪;改用 …」;路徑排除照既有八項測試碼排除):

   | 型錄列 | 規則(放哪支檔) | 形狀 | 直接出處原文 |
   |---|---|---|---|
   | API-2 | `kt-map-await-deferred`(`rules-unwired/api.yml`) | `$L.map { it.await() }`、`$L.map { $X -> $X.await() }`;不收 `forEach`(出處沒講到) | awaitAll KDoc:This function is not equivalent to deferreds.map { it.await() };IntelliJ 檢查 MapAwaitOnCollectionOfDeferred:Reports map { it.await() } calls on collections of Deferred … can be replaced by … awaitAll() |
   | UI-33 | `kt-compose-dispose-not-needed`(`rules-unwired/compose.yml`,這支檔 2026-11-08 移光規則後刪掉,本篇重開) | `DisposableEffect` 裡的 `onDispose { }` 是空的,**而且**區塊裡沒有 UI-32 認得的註冊呼叫(add…Listener/Observer/Callback、register…、subscribe、setOn…Listener、listen);那份註冊判斷從 UI-32 規則抽成 `utils/` 共用,兩條都引用它 | Compose side-effects 頁:Having an empty block in onDispose is not a good practice. Always reconsider to see if there's an effect that fits your use case better |
   | ARCH-59 | `kt-hilt-binding-missing-qualifier`(`rules-unwired/architecture.yml`) | 同一個 class/object 本體裡,兩個以上 `@Provides`/`@Binds` 函式回傳同一型別,其中至少一個**確定有限定詞**、至少一個**確定沒有**;報沒有的那幾個。確定有限定詞=帶 `@Named(...)`,或帶同一支檔裡用 `@Qualifier` 宣告的註解;確定沒有=身上的註解全在已知非限定詞清單裡(Provides、Binds、Singleton、Reusable、JvmStatic、Suppress、Deprecated、OptIn、名字以 Scoped 結尾的範圍註解);帶多重綁定註解(IntoSet、IntoMap、ElementsIntoSet、…Key)的函式兩邊都不算。其他註解兩邊都不算(判不準就不報) | Hilt 頁:As a best practice, if you add a qualifier to a type, add qualifiers to all the possible ways to provide that dependency. Leaving the base or common implementation without a qualifier is error-prone |
   | ARCH-62 | `kt-hilt-entrypoint-accessor-mismatch`(`rules-unwired/architecture.yml`) | `EntryPointAccessors.fromX(…, I::class.java)` 或泛型寫法 `EntryPointAccessors.fromX<I>(…)`,同檔 `I` 的 `@InstallIn(...)` 裡**沒有**那個 fromX 允許的元件:fromApplication→SingletonComponent;fromActivity→ActivityComponent;fromFragment→FragmentComponent;fromView→ViewComponent 或 ViewNoFragmentComponent。`@InstallIn` 列多個元件時,只要含允許的那個就不報 | Hilt 官方原始碼 EntryPointAccessors.kt 的 KDoc,四個方法各一句:May only be used with entry point interfaces installed in the SingletonComponent / ActivityComponent / FragmentComponent / ViewComponent or ViewNoFragmentComponent |

   - 每條附壞例(至少 2 處)、好例(至少 2 段)樣本;好例裡「不報」的寫法照其他規則好例的慣例寫成「容易誤報:」註解。UI-33 的好例收「有註冊、onDispose 有解除」與改用 LaunchedEffect 的寫法。提早返回或某條分支寫空 `onDispose { }`、別的分支有真正清理時不報:DisposableEffect 規定每條分支都要回傳 onDispose,那支只能寫空的(樣本內調形狀時看到,推翻設計審 r1 放行 f7 時的判斷);全部 onDispose 都空才報。API-2 另放一份 `review-fp-` 樣本,記下 Play services `Task.await()` 這個已知誤報。
   - ARCH-62 的好例樣本 interface 本體寫成多行(一行寫完會被解析器認錯,見〈實驗〉)。
2. **型錄改寫**:四列的現成規則欄改成型錄既有寫法「自寫 ast-grep <規則 id>」;通電批次的「告警帶寫法=」那段改成「未接(規則在 rules-unwired/:還沒在真專案量過誤報)」,其他段(例如 API-2 的「當下推相關列=批二」)照留;UI-33 的「情境怎麼認」照規則改成「空 onDispose 且區塊內沒有註冊呼叫(有註冊的歸 UI-32)」;ARCH-62 的來源欄補 EntryPointAccessors.kt 的網址;API-1、API-2 兩列都拿掉「detekt SequentialAsyncAwait」(detekt 規則集查不到),API-2 改寫 IntelliJ 檢查名 MapAwaitOnCollectionOfDeferred(只在 IDE 跑,來源欄補它的說明頁網址);API-2 的「待查」字樣因此消失,從〈待查證〉拿掉那一列。〈統計〉跟著改:規則包條數、hint 條數、不接閘條數各加 4(224→228、47→51、25→29)(量完搬到 `rules/` 的再照實改等級條數與被會擋規則守到的列數),待查證與規則代號待查各減 1(51→50、48→47)。量完照第 4 點再改。
3. **其餘 11 列寫明不寫的理由**(實測狀態欄補一句,通電批次不變):API-7、UI-18、UI-51、ARCH-43、ARCH-58、DATA-8、DATA-9、DATA-23、DATA-34、TEST-38、PERF-8。理由分三種:要跨檔或型別(UI-18、DATA-8、DATA-9、DATA-23、DATA-34、PERF-8)、要讀 XML 或 Gradle(ARCH-43、TEST-38)、形狀分不出正當用法或出處要推論(API-7:Flow retry KDoc 只說明不帶次數時預設會一直重試,沒說不帶次數是錯的;「要有上限」寫在另一頁離線優先指南的退避策略裡,要兩頁拼起來才成立,照判法不算直接;UI-51:看不到筆數,官方另說小清單用 Column 加 forEach 是對的;ARCH-58:出處只說注入在 super.onCreate() 發生,沒說之前讀會怎樣)。
4. **量誤報與升級**:每條規則照前幾批的量法量一次:
   - 語料:用 GitHub 程式碼搜尋撈一份,排除前幾批出現過的 repo;撈到之後、還沒看任何結果之前,依 repo 全名的 sha256 第一個位元組奇偶固定切成兩半。判準先寫定、算雜湊再撈。
   - 樣本內(偶數那半):看命中、把明顯誤報寫成排除;形狀定案後記規則檔雜湊。
   - 樣本外(奇數那半):形狀定案後只用一次,判升級只看它。跟「另撈一份」一樣保證調形狀時看過的 repo 不拿來判升級。
   - 命中多的每個 repo 抽一處、固定種子抽 40 處;命中 20 多處全判。判讀代理乾淨脈絡、照判準逐處判真問題、誤報、判不準。
   - 過升級條件的規則搬到 `rules/`,等級改 error,或照 `rules/` 既有規則的用法用 warning(兩者推送前都擋),型錄通電批次改「告警帶寫法=批一」,逐例表那條的目錄與檔名跟著改;API-2 若過,`review-fp-` 樣本拿掉(`rules/` 的規則不豁免它),那個已知誤報改寫進型錄實測狀態欄;出處只有建議語氣、沒寫後果的(UI-33 只寫「不是好做法,請重新考慮」),過了也只搬提示目錄 `rules-hints/`(hint,範本預設不接,推送前不擋),不放 `rules/`——`rules/` 的 warning 也會擋(代碼審 r3 架構對齊點出,原本誤以為 warning 不擋);ARCH-59 原文除了 As a best practice 也寫明後果 could result in Hilt injecting the wrong dependency,照一般規則放 `rules/`;
   - 證據放卷證 `governance/review-reports/android形狀列補規則/experiment/`(新增)。
5. **測試**(擴充既有的,不另開):
   - `t_kotlin_rulepack_security_rules` 的逐例表 `_KTSEC_CASES` 加一個選填的第五欄,照 `_KTSEC_PLACE` 加選填位置欄的先例:值是預期報在哪幾行的 tuple;有這欄就表示本體是完整的 kt 檔(含 package 與頂層宣告),不包進 `fun case(...) { … }`(Kotlin 不准在函式裡宣告 interface)(ast-grep 報的是節點起始行:ARCH-59 報在函式第一個註解那行,API-2 鏈式寫法報在接收者那行)。沒帶第五欄的既有一百多例照舊。
   - 行號要從 ast-grep 的 JSON 取 `range.start.line`;規則包 `check.py` 的 `scan` 原本只回 (規則, 檔),改成一律回 (規則, 檔, 起始行),兩個既有呼叫端跟著多解一個值(代碼審 r1:不用旗標切換回傳形狀)。
   - 四條規則加進 `_KTSEC_PLACE`(目錄、檔名、型錄編號、路徑排除),套既有的「目錄、訊息以 [編號] 開頭且不超過 120 字、路徑排除恰好幾項」檢查;同一支測試再驗四列型錄現成規則欄寫著「自寫 ast-grep <規則 id>」而且那個 id 在規則包裡。
   - 逐例表每個樣式至少一例報:API-2 的 `it` 與具名參數兩式各一;ARCH-62 的四個 fromX 各一例報、一例不報,泛型寫法一例,`@InstallIn` 多元件一例不報;ARCH-59 的「@Named」「同檔 @Qualifier 宣告」各一例報,多重綁定、`@Suppress` 對照組各一例不報;UI-33 的有註冊不報(歸 UI-32)、沒註冊報各一例。
   - 樣本自測 `t_kotlin_rulepack_samples` 照舊驗壞例報、好例不報。
   - 統計測試:`_KT_STATS_LINES` 的寫死值照新數改;`_KT_STATS_MUTATIONS` 裡寫死的「待查證:51 列」「50 列」「規則代號待查 48 列」幾個改壞案例的原字串跟著改成新數(不改的話替換找不到原字串、改壞不生效);用 `| API-2 | IJ:「Use awaitAll()` 當錨點的那例,API-2 拿掉後換一列仍在〈待查證〉的當錨點。
6. **圖譜**:[[Systems/kotlin規則包]] 不接閘目錄那行(現在寫共 25 條)的條數與規則清單,新增一條 WHY 記本批的放置與升級條件(記資安各批放置的那條是資安專用,不併進去);[[Projects/Android協程與API寫法機械檢查標準_計劃]] 補一行指向本篇。

**不做**:不寫跨檔或讀 XML、Gradle 的規則;不寫 ARCH-58(出處不直接);不改新增告警閘。

## 實驗(寫計劃前的最小實驗,2026-11-09,ast-grep 0.51.1)

- 四條草稿規則各拿壞寫法與好寫法試跑:壞寫法都報、好寫法都不報。
- API-2:Google Play services 的 `Task` 也有 `await()`,`tasks.map { it.await() }` 會被報——單檔看不到型別,這是預期的誤報來源,樣本外量出比例再判。
- ARCH-62、ARCH-59:Kotlin 解析器有一個限制——宣告上面掛兩個以上註解、本體又寫在同一行或結尾大括號跟在最後一個成員同一行時(`interface X { fun f(): F }`、`object M { @Provides fun a(): X = x() }`),整段被解析成運算式,認不出是宣告;本體分多行就正常。後果是漏報,不是誤報。
- ARCH-59:只比對函式宣告直接帶的回傳型別,參數型別不會被當成回傳型別。
- GitHub 程式碼搜尋粗估(2026-11-09):`onDispose { }` 約 5976 支檔、`onDispose {}` 約 5416、`.map { it.await() }` 約 2116、`EntryPointAccessors.fromApplication` 約 7936、`fromActivity` 約 343、同檔有 `@Provides` 與 `@Named` 約 10432。這些是呼叫點或關鍵字的檔數,不是壞寫法的命中數:ARCH-62 寫錯元件在執行時就會崩潰,ARCH-59 要同檔同型別才算,真命中可能遠少於 20;不到 20 就照第 4 點留在只登記。

## 量測結果(2026-11-09)

語料、切分、掃描、抽樣的程式與結果都在卷證 `experiment/`:`corpus.tsv`(每支檔的 repo、路徑、blob sha、查詢)、`fetch.py.txt`、`pipeline.py.txt`、`summary-A.json` 與 `summary-B.json`、`hits-*.json`、`sample-*.txt`;判準 `judge-criteria.md`(雜湊在 `judge-criteria.sha.txt`,撈語料前寫定);規則定案的雜湊在 `rules-freeze.sha.txt`;判讀原文 `judge-*.md`。

| 規則 | 樣本外檔數 | 命中(合併後;repo 數) | 抽判 | 真問題、誤報、判不準 | 誤報比例(Wilson 95%) | 結果 |
|---|---|---|---|---|---|---|
| kt-map-await-deferred | 545 | 294(207) | 40 | 36、3、1 | 7.5%(2.6%–19.9%) | 搬 `rules/`、error |
| kt-hilt-binding-missing-qualifier | 872 | 68(50) | 40 | 40、0、0 | 0%(0%–8.8%) | 搬 `rules/`、warning(會擋;原文寫明會注入錯的實例) |
| kt-compose-dispose-not-needed | 514 | 311(268) | 40 | 32、6、2 | 15%(7.1%–29.1%) | 留只登記 |
| kt-hilt-entrypoint-accessor-mismatch | 512 | 1(1) | — | — | — | 留只登記(不到 20 處) |

- 誤報類:map 那條是 Flow 的 map 2 處(`.asFlow().map { it.await() }`)、範例碼 1 處;空 onDispose 那條是區塊裡其實有該清理的東西 5 處(背景音樂、螢幕常亮、一直跑的協程、掛到 client 的攔截器,名字不在註冊字表裡)、範例碼 1 處。Play services `Task.await()` 這次抽樣沒出現。
- 樣本內調形狀一次:空 onDispose 那條改成全部 onDispose 都空才報,樣本內命中 410 → 321。
- 樣本外掃描後改一次:EntryPointAccessors 那條的唯一命中用的是 `ApplicationComponent`(SingletonComponent 改名前的舊名,Dagger 2.30 發布說明),規則補認舊名;這條命中不到 20 處、不判升級,改了不影響任何升級判斷,雜湊在 `rules-freeze.sha.txt` 另記。
- 語料 5011 支檔撈到 5000 支,其餘 11 支撞到 GitHub API 每小時上限沒抓,全屬 EntryPointAccessors 那條(清單在 `corpus-missing.tsv`)。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| API-2 | kotlinx.coroutines awaitAll KDoc | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/await-all.html |
| UI-33 | Compose side-effects 官方頁 | https://developer.android.com/develop/ui/compose/side-effects |
| ARCH-59 | Hilt 官方頁(限定詞) | https://developer.android.com/training/dependency-injection/hilt-android |
| ARCH-62(fromX 與元件的對應) | Hilt 官方原始碼 EntryPointAccessors.kt 的 KDoc | https://github.com/google/dagger/blob/master/hilt-android/main/java/dagger/hilt/android/EntryPointAccessors.kt |
| ARCH-62(元件要跟 @InstallIn 對上的原則) | Hilt 官方頁 | https://developer.android.com/training/dependency-injection/hilt-android |
| ARCH-62(ApplicationComponent 是 SingletonComponent 的舊名) | Dagger 2.30 發布說明:Hilt has deprecated ApplicationComponent … Use SingletonComponent instead | https://github.com/google/dagger/releases/tag/dagger-2.30 |
| API-2(IntelliJ 檢查只在 IDE) | IntelliJ 檢查說明頁 | https://www.jetbrains.com/help/inspectopedia/MapAwaitOnCollectionOfDeferred.html |
| ARCH-59(什麼是限定詞、用 @Qualifier 宣告) | Hilt 官方頁 Provide multiple bindings 段:A qualifier is an annotation that you use to identify a specific binding | https://developer.android.com/training/dependency-injection/hilt-android |
| ARCH-59(@Named 是限定詞) | javax.inject.Named javadoc:String-based qualifier | https://javax-inject.github.io/javax-inject/api/javax/inject/Named.html |
| 樣本外語料只用一次、不拿來調形狀 | Dwork 等人 | https://ar5iv.labs.arxiv.org/html/1506.02629 |

## 實務隱患

- 守衛面:量完過了升級條件的規則會搬到 `rules/`,消費專案推送前會多擋這種寫法;沒過的不影響推送。誤擋的出口是 lint-waive 留帳放行,RETIRE-IF 第二句管放行太多的情形。
- 已排除:金流:不碰付款。
- 已排除:對外送出:不寄信、不呼叫外部服務(語料下載只在實驗階段)。
- 已排除:不可逆:全部是 repo 內的文字檔,退回提交即還原。
- 效能:ARCH-59、ARCH-62 的 `inside` 往上找到檔案根再往下找,比對次數隨函式數平方成長。設計審 r1 實測:200 個函式的 module 0.02 秒、2000 個 1.2 到 2.1 秒、2000 組 entry point(16000 行)11.5 秒;一般 Hilt module 不到 50 個函式,遠低於規則包掃描逾時 120 秒。
- 併發寫入不考慮:工具鏈單人、AI 依序操作。

## 驗收條款

- [S1] 當跑規則包樣本自測時,四條新規則 應 報壞例、不報好例 [test:t_kotlin_rulepack_samples]
- [S2] 當用逐例表掃完整的 kt 檔時,四條新規則 應 只在逐例表寫的那幾行報 [test:t_kotlin_rulepack_security_rules]
- [S3] 當真型錄跑型錄自檢時,問題數 應 是 0 [test:t_kotlin_catalog_rows_wired]
- [S4] 當讀真型錄與規則包時,API-2、UI-33、ARCH-59、ARCH-62 四列的現成規則欄 應 寫著「自寫 ast-grep <規則 id>」而且那個 id 在規則包裡、目錄與逐例表登記的一致 [test:t_kotlin_rulepack_security_rules]
- [S5] 當讀型錄那四列的實測狀態欄時,命中、判讀、誤報數 應 跟卷證 `experiment/judge-*.md` 逐處判讀原文數出的數一致 [manual:逐列對照卷證判讀原文與命中檔筆數,設計審或代碼審核一次]

## 預期值表

行號是那支 kt 檔從 1 起算的行。

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S2 | `suspend fun f(ds: List<Deferred<Int>>) = ds.map { it.await() }` | kt-map-await-deferred 報 | awaitAll KDoc、IntelliJ 檢查說明 |
| S2 | `suspend fun f(ds: List<Deferred<Int>>) = ds.map { d -> d.await() }` | 報 | 同上 |
| S2 | `suspend fun f(ds: List<Deferred<Int>>) = ds.awaitAll()` | 不報 | 標準寫法 |
| S2 | `suspend fun f(ds: List<Deferred<Int>>) { ds.forEach { it.await() } }` | 不報 | 出處沒講到 forEach |
| S2 | `DisposableEffect(Unit) { log("x"); onDispose { } }` | kt-compose-dispose-not-needed 報 | side-effects 頁 |
| S2 | `DisposableEffect(o) { o.addObserver(obs); onDispose { } }` | kt-compose-dispose-not-needed 不報(kt-compose-dispose-empty-cleanup 報) | 有註冊的歸 UI-32 |
| S2 | `DisposableEffect(o) { o.addObserver(obs); onDispose { o.removeObserver(obs) } }` | 兩條都不報 | side-effects 頁的範例 |
| S2 | 同一個 object 裡 `@Provides fun a(): OkHttpClient` 與 `@Provides @Named("x") fun b(): OkHttpClient` | kt-hilt-binding-missing-qualifier 只報 a 的 `@Provides` 那行 | Hilt 限定詞段 |
| S2 | 同一個 object 裡兩個沒加的 `a`、`c` 與一個 `@Named("x")` 的 `b`,都回傳 OkHttpClient | 報 a、c 兩行,不報 b | 同上 |
| S2 | 同檔宣告 `@Qualifier annotation class Auth`,`@Provides @Auth fun b(): OkHttpClient` 與 `@Provides fun a(): OkHttpClient` | 報 a | 同上 |
| S2 | `@Provides @IntoSet fun b(): Interceptor` 與 `@Provides fun a(): Interceptor` | 不報 | 多重綁定不是限定詞 |
| S2 | `@Provides @Suppress("x") fun b(): Foo` 與 `@Provides fun a(): Foo` | 不報 | Suppress 不是限定詞 |
| S2 | `@Provides @IntoSet @Named("x") fun b(): OkHttpClient` 與 `@Provides fun a(): OkHttpClient` | 不報 | 多重綁定是往集合放東西,不是同型別的另一個綁定(實作時改壞多重綁定排除沒翻紅才補的例) |
| S2 | `@Provides fun a(): OkHttpClient` 與 `@Provides fun g(): Gson` | 不報 | 型別不同 |
| S2 | 同檔 `@InstallIn(ActivityComponent::class)` 的 `interface E` 與 `EntryPointAccessors.fromApplication(ctx, E::class.java)` | kt-hilt-entrypoint-accessor-mismatch 報 | EntryPointAccessors.kt KDoc |
| S2 | 同上但 `@InstallIn(SingletonComponent::class)` | 不報 | 同上 |
| S2 | `@InstallIn(SingletonComponent::class)` 的 `E` 與 `fromActivity(act, E::class.java)` | 報 | 同上 |
| S2 | `@InstallIn(SingletonComponent::class)` 的 `E` 與 `fromFragment(f, E::class.java)` | 報 | 同上 |
| S2 | `@InstallIn(ViewNoFragmentComponent::class)` 的 `E` 與 `fromView(v, E::class.java)` | 不報 | 同上 |
| S2 | `@InstallIn(ActivityComponent::class)` 的 `E` 與泛型 `fromApplication<E>(ctx)` | 報 | 同上 |
| S2 | `@InstallIn(ActivityComponent::class, SingletonComponent::class)` 的 `E` 與 `fromApplication(ctx, E::class.java)` | 不報 | 含允許的元件 |
| S2 | `EntryPointAccessors.fromApplication(ctx, Other::class.java)`,`Other` 不在同檔 | 不報 | 單檔看不到 @InstallIn |
| S2 | DisposableEffect 裡 `val w = window ?: return@DisposableEffect onDispose { }`,後面 `onDispose { w.clearFlags(FLAG) }` | kt-compose-dispose-not-needed 不報 | 樣本內調形狀:那支 API 規定要回傳 onDispose |
| S2 | DisposableEffect 裡 if 分支 `onDispose { }`、else 分支 `onDispose { window.clearFlags(FLAG) }` | 不報 | 同上 |
| S2 | DisposableEffect 裡提早返回 `onDispose { }`、後面也是 `onDispose { }` | 報 | 全部都空 |
| S2 | `@InstallIn(ApplicationComponent::class)` 的 `E` 與 `fromApplication(x, E::class.java)` | kt-hilt-entrypoint-accessor-mismatch 不報 | Dagger 2.30 發布說明:ApplicationComponent 是 SingletonComponent 的舊名 |
| S2 | `@InstallIn(FragmentComponent::class)` 的 `E` 與 `fromFragment(x, E::class.java)` | 不報 | EntryPointAccessors.kt KDoc(代碼審 r1 補:對應改壞測不到) |
| S2 | `@InstallIn(ViewComponent::class)` 的 `E` 與 `fromView(x, E::class.java)` | 不報 | 同上 |
| S2 | `@InstallIn(SingletonComponent::class)` 的 `E` 與 `fromView(x, E::class.java)` | 報 | 同上 |
| S2 | `@InstallIn(` 換行 `SingletonComponent::class,` 換行 `)` 的 `E` 與 `fromApplication(x, E::class.java)` | 不報 | 同上;代碼審 r1:參數跨行寫原本會誤報 |
| S2 | `ds.asFlow().buffer().map { it.await() }.toList()` | kt-map-await-deferred 不報 | 代碼審 r4:asFlow 後接 Flow 算子仍是 Flow |
| S2 | `ds.asFlow().buffer().toList().map { it.await() }` | 報 | 收成清單後又是集合 |
| S2 | `ds.asFlow().map { it.await() }.toList()` | kt-map-await-deferred 不報 | Flow 一筆一筆來,沒有集合可 awaitAll(量測時的誤報類,代碼審 r1 寫成排除) |

## 回退

退回本計劃的提交,逐項是:
- 規則包:四條新規則與它們的壞例好例樣本、重開的 `rules-unwired/compose.yml`、`utils/` 的註冊判斷;量完搬到 `rules/` 的那幾條。
- 型錄:四列的現成規則、通電批次、實測狀態欄;API-1、API-2 的現成規則更正與 API-2 移出〈待查證〉;11 列實測狀態的補句;〈統計〉。
- 測試:逐例表的第五欄與新例、`_KTSEC_PLACE` 新增的四筆、統計寫死值與改壞案例的原字串、待查證那支的改壞錨點。
- 規則包 `check.py` 的 `scan` 行號參數;UI-32 規則改引共用的註冊判斷(行為不變)。
- 圖譜:Systems/kotlin規則包 的不接閘那行;機械檢查標準計劃的指向;本篇。
- 卷證留著。

## 天花板

- 誤報率是 40 處的點估計:map 那條 7.5% 的 Wilson 95% 上界約 20%,搬去會擋之後真專案的誤報可能高於一成。
- 單檔語法看不到型別:API-2 會報 Play services `Task`、`ListenableFuture` 這類也有 `await()` 的接收者,也會報型別是 `Flow<Deferred>` 的變數的 map(接收者鏈裡有 `.asFlow()`、後面沒收成 toList/toSet/toCollection 的已排除;變數看不出型別);lambda 第一行是註解、參數寫了型別、`it.await() + 1`、安全呼叫 `ds?.map { it.await() }` 這類寫法不報。
- ARCH-62 不認具名參數、完整套件名的呼叫、巢狀類別名與 import 別名(別名可能誤報);`@InstallIn(` 參數裡夾註解寫了另一個元件名時,會當成有那個元件而漏報;ARCH-59 看不到別的檔宣告的自訂限定詞,只認 `@Named` 與同檔 `@Qualifier`,其餘少報。
- ARCH-59、ARCH-62 只看同一支檔:綁定或 entry point 分在不同檔時漏報;一行寫完又掛兩個註解的 interface 或 object 會漏報(解析器限制)。
- 誤報只量命中裡的比例,漏報沒量。

REVISIT:2027-02-09 看 kt-map-await-deferred 搬到會擋後三個月,消費專案對它的 lint-waive 放行占新增告警的比例;超過三成照 RETIRE-IF 降回只登記,Flow 的 map(`.asFlow().map { it.await() }`)若是主要放行原因,先試把它寫成排除再重量
REVISIT:2027-05-09 空 onDispose 那條:把「區塊裡其實有該清理的東西」的寫法(start/stop、keepScreenOn、無限迴圈協程、掛攔截器)整理成共用註冊判斷的補充字表,換一批語料重量;補了以後同一份判斷也會讓會擋的 UI-32 多抓,要一起量
REVISIT:2027-05-09 量一次這四條的漏報:在新語料裡用文字搜尋找出該報沒報的寫法(跨檔的 entry point、分檔的綁定與別檔的自訂限定詞、一行寫完的 interface 與 object、有型別的 lambda 參數),逐處判是不是形狀漏的,寫進型錄實測狀態欄

## 審計修正紀錄

- 代碼審 r4(2026-11-09,兩席,人裁多開的一輪,只審 r3 之後的修補):4 條/blocking 1/map 那條的 asFlow 排除只認結尾,asFlow 後接 buffer、flowOn 仍被當清單擋下,改成「鏈裡有 asFlow 且後面沒收成集合才不報」,補 C222~C226;rules-hints/ 的兩種用途、範圍 4 的等級寫法、型錄通電批次的測試釘住。r1~r3 跑滿回顧在卷證 cap-retro.json。
- 代碼審 r3(2026-11-09,兩席):9 條/blocking 2/同一類第三輪被打穿(結構條件 has/not/inside、變數綁定、字邊界、stopBy 沒有例子),上網查 ast-grep 官方規則測試與變異測試的標準算子後,把自動列舉擴到這四類共 102 項:71 項抓到、8 項規則載入不了、7 項是拿掉註解比對開頭 ^ 的等價改壞、16 項缺口補 C202~C217;ARCH-59 的 \w+Key 會吃掉同檔宣告的 @ApiKey 限定詞,改成只認 Dagger 內建的 Key;更正「warning 只列出不擋」的錯誤前提(warning 也擋)。
- 代碼審 r2(2026-11-09,兩席):7 條/blocking 2/同一類第二輪被打穿(規則某個樣式或清單選項沒有例子,改壞照綠),換形狀:自動列出四條規則與共用註冊判斷的每個樣式與正規式選項共 51 項逐項拿掉,修前 25 項沒紅,補 C158~C184 後全紅;3 條寫法 minor 附理由放行。
- 代碼審 r1(2026-11-09,兩席):11 條/blocking 2/fromFragment、fromView 的元件對應改壞測不到,補三例;測試另寫一套型錄讀法,改用 main_rows;@InstallIn 比對不跨行會誤報,改成可跨行;map 那條把量測時的 `.asFlow()` 誤報寫成排除(只會少報,不影響升級判斷);scan 改成固定回三元組;逐例表選填欄改成位置欄、照編號排;卷證 `governance/review-reports/code-android形狀列補規則/`。
- 實作與量測(2026-11-09,沒有派席,記在這裡給代碼審看):樣本內看到空 onDispose 的分支寫法誤報,推翻 r1 放行 f7 時「提早返回照報」的判斷,改成全部都空才報;量完 ARCH-59 過條件放 `rules/` 的 warning(當時誤以為 warning 不擋,代碼審 r3 更正:warning 也擋,而原文寫明後果,擋是對的);EntryPointAccessors 補認舊名 ApplicationComponent。

- r1(2026-11-09,四席):28 條/blocking 10/ARCH-59 判斷限定詞的方向寫反(清單外的註解當限定詞會多報),改成只認確定的限定詞、多重綁定排除;API-2 拿掉出處沒講到的 forEach;UI-33 改成既有 UI-32 的互補、共用註冊判斷;ARCH-62 的對應改引 Hilt 原始碼 KDoc、加泛型寫法與多元件;測試改成擴充既有逐例表(選填頂層與行號欄)而不另開一支,每個樣式至少一例;統計改壞案例的寫死數字列進範圍;API-2 升級時拿掉 review-fp 樣本、UI-33 最多升 warning(代碼審 r3 更正:warning 也擋,建議語氣的規則改放 rules-hints/)。
- 席報告與收貨紀錄:`governance/review-reports/android形狀列補規則/`(r1-*.md、r1-intake.md)。
