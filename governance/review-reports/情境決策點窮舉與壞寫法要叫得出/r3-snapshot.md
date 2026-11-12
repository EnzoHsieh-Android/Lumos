---
type: project
status: doing
created: 2026-11-12
updated: 2026-11-12
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
  - risk/守衛面
lands_in:
  - Systems/kotlin規則包
related:
  - "[[Systems/kotlin規則包]]"
  - "[[Projects/Android寫法語意情境表態與盲判_計劃]]"
  - "[[Projects/Android寫法回合結束檢查與改檔前推列_計劃]]"
---
# 情境決策點窮舉與壞寫法要叫得出_計劃

> 白話:推送前的情境題(型錄〈情境決策表〉每列一個情境,改動命中觸發字就要表態、再由盲判代理獨立判一次)只在「被問到」時守得住;沒被問到就整段默默放行。2026-11-12 實驗發現搜尋框改用 `flatMapMerge`、`flatMapConcat` 時,「只要最新一次」那一列根本不會被問(觸發字只收好寫法的字,`flatMapLatest`、`debounce`),已先補了那一列。接著全表掃描:型錄每個(情境列, 對應檢查)的壞寫法,有一大半單獨出現時叫不出它對應的情境列。這份計劃讓「沒被問到」不再沒人知道:每一個沒被問到的寫法,都要列在型錄上、寫明改由誰抓,而且「誰抓」要機器驗得到。從兩個方向圍:①**從函式庫窮舉**:協程核心函式庫的公開 API 清單是有限的、官方逐版發布,把每個公開名稱分類成「選了它就等於做了情境決定(歸到某列,且一定被那列的觸發字搜得到)」「被某列觸發字搜到、但意思不同(撞名)」「帶決定、但不問(指向型錄主表管它的那一列,由那一列的壞寫法走反查)」或「不帶情境決定(寫理由)」,升版多出來的名稱沒分類就紅;②**從型錄的壞寫法反查**:每段壞寫法片段(沒有片段的也算一個單位)要嘛照推送前同一套路徑篩選與切段就叫得出對應列,要嘛明寫改由哪裡抓,而且改由在片段層級驗證。使用者原話(2026-11-12):「雖然他是需要確認情境的規則,但有時候規則往往沒辦法在第一時間確認清楚,這時候,如果放行AI寫出這樣的語法,就會出問題而沒發現」「我是想避免這種情況出現」「我相信Kotlin的語法絕對窮舉得出來,各種語法對應當下情境是不是符合功能需求,或是功能需求定義不清需要進一步釐清語法有沒有適用,是做得到的對嗎」。

PRIOR-ART: ①窮舉來源:kotlinx.coroutines 用 Kotlin 官方的二進位相容檢查工具(binary-compatibility-validator,https://github.com/Kotlin/binary-compatibility-validator )把每一版的公開 API 存在 repo 裡,有兩份:Kotlin 層級的 klib 清單(宣告照原始碼的名字寫,例 `final val Lazily`、`final const val UNLIMITED`、成員 `abstract fun trySend`;格式說明 https://github.com/Kotlin/binary-compatibility-validator/blob/master/docs/design/KLibSupport.md ,官方標實驗性)與 JVM 層級的 `.api` 清單(編譯後形狀)。klib 清單涵蓋原生、JS、Wasm 平台,不含 JVM;JVM 清單有 Android 實際用到的全部,但名字是編譯後的。採用「klib 清單的名字為主,只有標了平台限定、JVM 清單又找不到的才丟;再補 JVM 清單裡 klib 沒有的頂層函式與類別」。不選:從 JVM 清單還原讀取函式與成員(r1、r2 兩輪共五席實測:getter 大小寫判不出、`is` 前綴不是 getter、`-impl` 與雜湊後綴、`@JvmName` 改名、`INSTANCE`、內部套件回流,同類兩輪被打穿);不選:從語料統計常見寫法(窮舉不完)。方向參照:Android Lint 的 API 檢查靠 SDK 隨附的 `api-versions.xml`(平台每個類別、方法、欄位的資料庫)逐一檢查呼叫(https://android.googlesource.com/platform/development/+/8ec5006 ),而且他們也因資料庫收了不適用的 API 造成誤報、改成過濾掉那批(https://gitlab.e.foundation/e/os/android_build_soong/-/commit/67cf60e7c5bf29db9dec52c575d0250568371a18 )——「用官方 API 清單當母體」是成熟做法,要注意的是只收適用平台的名字。②強迫分類的形狀:Kotlin 對 sealed 類別的 `when` 要求窮舉每個分支(https://kotlinlang.org/docs/sealed-classes.html#use-sealed-classes-with-when-expression )。③改由要逐段證明:Semgrep 規則測試以每一行的 `ruleid:` 標註要求那一行一定被報(https://semgrep.dev/docs/writing-rules/testing-rules ),ast-grep 規則測試的 valid/invalid 同理(https://ast-grep.github.io/guide/test-rule.html )。採用「改由只在片段層級驗證」;不選:名稱層級背書(r2 三席實測:名稱是子字串、短名在任何壞例行都出現、API 名稱沒有對應檢查可比)。④常用字門檻沿用 [[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 實驗 E9:Now in Android 的 kt 檔文件頻率超過 8% 的字不當觸發字。
RETIRE-IF: 上線八週後用 `lumos gov --stats` 的情境題段看:本案新加觸發字的那幾列,作者判適用的(段,列)數八週都是 0 → 那些字沒抓到任何真情境,撤回改標「決策不問」;〈叫不出的壞寫法〉改由寫「代碼審」的超過全部改由的一半,而且漏網帳(`lumos loop escape --list`)八週內沒有一筆落在這些列 → 反查那一半降成只在新增列時要求;協程函式庫連兩次升版都沒有新增需要歸到情境列的名稱 → 窮舉改成只在升版時跑。

## 用詞

- **情境列**:型錄〈情境決策表〉的一列(`D-n`),有情境、標準寫法、不適用時、觸發字、證據樣式、對應檢查。
- **被問到**:一支改動檔,先過推送前同一套路徑篩選(測試檔、非正式碼不出情境段),再經情境段切法(`_kt_sit_text_segments` 這一族,剝掉註解與字串、比對觸發字)切出一段、那段的候選列含這一列。被問到之後的路既有、本案不改:情境題只收「適不適用、照哪個寫法」,不收 na 或 todo;缺段、缺列、答案形狀不對、缺第一盲判、作者與第一盲判不一致又沒有仲裁,都擋;證據樣式對不上、仲裁多數判作者沒照做只提醒不擋;判不了的出口是段放行,人或 AI 都能下,AI 下的記成 AI 放行、在 doctor 與推送前小結列到有人確認為止([[Projects/Android寫法語意情境表態與盲判_計劃]])。整批改動被判成伺服端專案時情境題不出(`android_only`),這條不在本案範圍。
- **路徑篩選**:推送前 `_kt_situation_segments` 判一支檔能不能出情境段的那串條件。本案把它抽成 scripts/lumos 的一支小函式 `_kt_sit_path_ok(rel)`(新增),`_kt_situation_segments` 改呼叫它、行為不變;`check.py` 的反查也呼叫它,不另抄一份。
- **型錄主表列編號**:型錄主表一列一種寫法,編號是主題前綴加數字(例 `API-8`、`FLOW-22`、`TEST-7`);情境列的「對應檢查」欄就是這種編號。
- **會擋的規則**:規則包 `configs/ast-grep/kotlin-android/rules/` 目錄底下的規則;同層的 `rules-review/`、`rules-hints/`、`rules-unwired/` 都不擋。規則訊息開頭一律是 `[型錄主表列編號]`;每條規則的壞例樣本在 `samples/bad/<規則 id>/`。
- **通電批次欄、範本 T<n>**:型錄主表第 10 欄,記每種接電方式在哪一批生效;其中「行為測試或正向約束=範本 T<n>」指 `skills/kotlin-idioms/test-templates.md` 的第 n 組行為測試範本,每組有 `### 壞寫法:<型錄主表列編號> …` 小節、小節裡有程式圍欄(要有人照範本寫測試才守得住,不會自動跑)。T0 是「測試骨架守則」,不是行為測試範本。
- **停用列、停用字表**:兩件事。停用列是型錄標了「(停用)」的列,觸發字與證據樣式都是(無)、不出題;停用字表是 `check.py` 的 `STOP_TRIGGERS`,列「太常見、不准當觸發字」的字。
- **段放行**:情境題判不了時的出口,`lumos lint-waive kt-situation:<段身分>`,記誰放行、理由。
- **代碼審**:分支推送前派審查代理讀改動的迴圈([[Systems/pitfalls-code-loop]]),靠代理讀,不是機械檢查。
- **API 母體**:兩份釘版檔放在 `configs/ast-grep/kotlin-android/coroutines-api/`(新增)——`kotlinx-coroutines-core-1.10.2.klib.api` 與 `kotlinx-coroutines-core-1.10.2.api`,照官方 1.10.2 標籤的原檔逐位元組放(版本跟行為測試範本用的 1.10.2 一致),同目錄附一支說明檔寫來源網址、版本與 Apache-2.0 授權聲明。目錄名不用 `api/`,因為型錄已有 `API` 主題前綴與 `rules/api.yml`,同一個字兩種意思。型錄〈API 決策點〉第一行記兩份的網址與 sha256(以位元組算),自檢核對。取路徑用 `check.py` 的 `coroutines_api_dir()`(新增,同 `situation_dir` 的寫法)。
- **公開名稱**:從 API 母體抽出、寫程式時會打出來的名字,一個名字一列(不分多載、接收者、類別或同名工廠函式;`Channel` 類別與 `Channel(...)` 工廠是同一列)。抽法只有 `check.py` 的 `_api_names`(新增)一處:
  - 主來源 klib 清單(以 UTF-8 讀):逐行去掉行尾 ` // …` 簽名註解;每個宣告行(`fun`、`val`、`var`、`const val`、`class`、`interface`、`object`、`enum entry`)去掉修飾字、開頭的型別參數 `<…>`(只在宣告字之後、名稱之前那一段)、接收者 `(…).`、套件路徑 `xxx/`,取剩下的簡名。不收:`<init>`、`<get-…>`、`<set-…>`;`equals`、`hashCode`、`toString`、`componentN`、`copy`;列舉的 `values`、`valueOf`、`entries`;伴生物件與具名伴生物件本身的名字(`Companion`、`Factory`、`Key`);名稱含 `$` 或 `-impl` 的、底線開頭的。另外,名稱所在的外層類別(看那一段最近的類別標頭的完整名稱)套件路徑含 `internal` 或 `debug` 的,那一段的名稱都不收——跟 JVM 補來源同一組排除。
  - 只留適用 JVM 的:klib 宣告前一行標了 `// Targets: [...]`(檔頭那一行不算)的是只有部分平台才有的宣告;一個名稱的每一個宣告都標了平台,而且名稱本身與首字大寫的寫法(讀取函式 `getX` 會含它)都不在 JVM 清單全文裡(分大小寫的子字串),才不收——例 `promise`、`awaitAnimationFrame`。沒標平台的宣告是共用程式,JVM 也有,照收。2026-11-12 照這條試抽 1.10.2:427 個名稱丟 4 個(`asCoroutineDispatcher`、`asPromise`、`awaitAnimationFrame`、`promise`),`coroutineContext`、`immediate`、`runBlocking`、`IO` 都留著。
  - 補來源 JVM 清單:只補兩種、只補 klib 沒有的:①`…Kt` 門面類別裡的 `public static final fun` 名稱,去掉 `-` 之後 7 個字元的名稱修飾與 `$default`;②公開類別簡名。都跳過:標 `synthetic` 的、名稱含 `$` 或 `-impl` 的、底線開頭的、外層類別套件路徑含 `internal` 或 `debug` 的、`…Kt` 門面類別名本身。成員與讀取函式不從 JVM 清單補(JVM 專屬的成員列進〈天花板〉)。在 JVM 用 `@JvmName` 改了名的函式補不回原名(例 `asCoroutineDispatcher` 在 JVM 門面類別裡叫 `from`,補來源只會看到 `from`,不收原名),見〈天花板〉2。
  - 每個名稱另記**可見寫法**:是 object(例 `Dispatchers`)或伴生物件(含具名伴生物件,例 `Channel.Factory`)的成員時,可見寫法是 `外層類別.名稱`(`Dispatchers.IO`、`SharingStarted.Lazily`、`Channel.UNLIMITED`,伴生物件名不寫出來);其他名稱沒有可見寫法。
  - **比對形狀**:一個名稱拿三種字串去被比對:簡名、可見寫法(有的話)、簡名後接 `(`。
- **決策點**:選了它就等於做了某個情境決定的公開名稱(例:`flatMapMerge` 等於選了「新值來了舊的不取消、並行跑」)。
- **反查單位**:每個非停用情境列 × 它的每個對應檢查是一對;那個對應檢查在型錄主表「壞寫法形狀」欄裡每一段反引號包住的文字(`\|` 還原成 `|`,不做長度或字元過濾)各是一個單位;那一欄一段反引號都沒有時,這一對算一個 `<無片段>` 單位(一定叫不出、一定要進表)。觸發字寫(無)的列(例 D-2)也算。
- **叫得出**:單位的片段包成 `class X {` / `fun f() {` / 片段 / `}` / `}` 當成一支新增檔;路徑依對應檢查編號:`TEST-` 開頭試 `app/src/test/java/x/XTest.kt` 與 `app/src/androidTest/java/x/XTest.kt` 兩個,其他用 `app/src/main/java/x/X.kt`;路徑先過 `_kt_sit_path_ok`,過了再切段,任一個路徑切出的段的候選列含那一列就算叫得出。
- **改由**:〈叫不出的壞寫法〉每個單位沒被問到時改由誰抓,只在片段層級驗證:
  - `規則 <id>`:那條規則在會擋的 `rules/` 目錄,訊息開頭引的編號等於這個單位的對應檢查;片段要出現在 `samples/bad/<id>/` 的某支壞例檔裡——兩邊都先用 scripts/lumos 的 Kotlin 剝註解與字串,再把連續空白折成一個比對,片段前後要是整字邊界(同 `_kt_trigger_re` 的邊界規則)。完整自檢模式(`check.py --sg <ast-grep>`)另外確認:那條規則在那支壞例檔報出的節點,起訖行涵蓋片段所在那一行。
  - `範本 T<n>`:n 不是 0;等於這個單位的對應檢查列通電批次欄「行為測試或正向約束=」的值;範本那一組有標題是 `### 壞寫法:<對應檢查>` 的小節(編號後面接空白或行尾;冒號全形半形都認),而且片段照上一條的剝法與折空白,出現在那個小節的程式圍欄內文裡。讀圍欄內文用 `check.py` 的 `_fence_body`(新增,建在既有的 `_fence_regions` 上)。
  - `代碼審`:理由要寫代碼審要看什麼。
  - `不是寫法`:片段不是一段程式寫法(例 `[Loading, Success]`、`delay(常數)`);`<無片段>` 單位不准用。
  - 其他值、或理由空白 → 問題。

## 範圍

1. **API 決策點節**:型錄在〈接電證據〉之後、〈統計〉之前新增〈API 決策點〉節。第一行固定 `母體:kotlinx-coroutines-core 1.10.2,klib <網址> sha256 <值>,jvm <網址> sha256 <值>`;接一張表「名稱 | 歸屬 | 理由」,公開名稱每個恰好一列。歸屬欄是一到多個歸屬項,以「、」分隔,每項是下面五種之一(歸屬項之間只用「、」,項內關鍵字與編號之間一個半形空白):
   - `D-n`:那個名稱是這一列的決策點。那一列至少一個觸發字,它的正規式(`_kt_trigger_re`)搜得到這個名稱的任一種比對形狀;那一列不能是停用列。
   - `撞名 D-n`:那一列的觸發字搜得到這個名稱,但意思不同(例 D-59 資料同步衝突的觸發字 `merge` 搜得到 Flow 的 `merge`;`combine` 對 D-5、D-6 是決策點、對 D-35 是撞名,寫成 `D-5、D-6、撞名 D-35`)。
   - `決策不問 <型錄主表列編號>`:是決策點,但不當觸發字(在停用字表裡、Now in Android 文件頻率超過 8%,或沒有對應的情境列)。那個主表列的壞寫法欄,剝掉反引號後要以整字出現這個名稱的任一種比對形狀;那個主表列的壞寫法就會以反查單位進〈叫不出的壞寫法〉的驗證(主表列不是任何情境列的對應檢查時,本案不另做反查,見〈天花板〉6)。
   - `決策不問 代碼審`:是決策點,但型錄主表沒有任何一列寫到它。
   - `無決策`:不代表情境選擇(例 `emptyFlow` 只是建空流)。`無決策` 只能單獨出現,不能跟其他歸屬項並列。
2. **API 決策點自檢**(`check.py` 的 `api_decision_problems(lumos, catalog_text, api_dir, main_rows)`,新增;回 `[(名稱或 <api>, 原因)]`):
   - lumos 載入不到 → 回 `[("<api>", "要載入 scripts/lumos:<原因>")]`,同 `situation_sample_problems`。
   - 兩份母體檔的 sha256 跟第一行對不上 → 問題(母體被改過)。
   - 母體裡有、表上沒有的名稱 → 問題(升版多出來的名稱一定被點到)。
   - 表上有、母體裡沒有的名稱 → 問題(升版拿掉或打錯)。
   - 同一個名稱出現兩列、歸屬欄有不認得的項、同一項重複、`無決策` 跟其他項並列 → 問題。
   - `D-n` 項:那列觸發字搜不到它、或那列是停用列 → 問題。
   - `撞名 D-n` 項:那列觸發字根本搜不到它 → 問題(撞名是假的)。
   - `決策不問 <主表列編號>` 項:主表沒有那一列,或那一列壞寫法欄沒有以整字出現這個名稱 → 問題。
   - `決策不問 代碼審` 項:型錄主表有任何一列的壞寫法欄以整字出現這個名稱 → 問題(有列寫到它,就要指向那一列,讓那一列的片段走反查)。
   - 反向:任一非停用列的任一觸發字的正規式搜得到某個名稱的任一種比對形狀,而那個名稱的歸屬沒有 `D-n` 也沒有 `撞名 D-n` → 問題(跟正向同一個方向,`Channel.UNLIMITED`、`indexOf(` 這類都照搜)。
   - 停用字表:停用字表裡的字等於某個名稱的任一種比對形狀(例 `Dispatchers.IO` 等於 `IO` 的可見寫法),而那個名稱只標 `無決策`,理由又不是以「停用字,不帶決策:」開頭(冒號全形半形都認)→ 問題(停用字最常被選錯,不准用 `無決策` 默默帶過)。
   - 抽不到錨點名稱(`flatMapLatest`、`Mutex`、`Lazily`、`UNLIMITED`、`trySend`)、或抽出的名稱少於 300 個 → 問題(抽法壞了)。
   - 任一列理由空白 → 問題。
3. **叫不出的壞寫法節與自檢**:型錄〈API 決策點〉之後、〈統計〉之前新增〈叫不出的壞寫法〉節,表「列編號 | 對應檢查 | 片段 | 改由 | 理由」(`<無片段>` 單位的片段欄寫 `<無片段>`);`check.py` 的 `bad_snippet_reach_problems(lumos, catalog_text, main_rows, rules, samples_dir, templates_text, scan_index=None)`(新增;`rules` 是既有 `load_rules()` 的結果,用來核規則在哪個目錄與訊息編號;`scan_index` 是 `--sg` 模式那一次掃描建的起訖行索引,`--catalog-only` 沒有 ast-grep 時是 None、只做靜態核對;回 `[(列編號或 <reach>, 原因)]`;lumos 載入不到同上):
   - 叫不出、表上又沒有 → 問題,訊息印列編號、對應檢查與片段。
   - 表上有、但現在叫得出 → 問題(過期,補了觸發字就要刪這一列)。
   - 表上有、但型錄壞寫法欄已經沒有這段片段(或那一對已經有片段卻寫 `<無片段>`)→ 問題。
   - 改由照〈用詞〉的核對,不合 → 問題。
4. **接法**:
   - 兩張新表各只有一支讀表函式:`_api_table`、`_unreach_table`(新增),自檢、統計都走它們,同既有 `_pending_table`、`wiring_table` 的先例。
   - 兩支新自檢照既有的 `situation_sample_problems(lumos=)` 接:不放進 `catalog_problems`(它的說明寫明不載入 scripts/lumos,測試用型錄複本呼叫它四十多處),在 `check()` 與 `--catalog-only` 另外串;`main` 與 `check()` 各載入 lumos 一次、讀主表 `main_rows` 一次,再傳給需要的函式;測試傳型錄複本、暫存母體、樣本與範本複本。
   - `--sg` 完整模式的規則實跑不另掃:`check()` 既有對 `samples/bad` 的那一次掃描,`scan()` 改成多回每筆的起訖行(`--json=stream` 本來就有),同一份結果建索引給改由核對查;掃描逾時或失敗(`scan()` 回 None)時,這道判問題,不當成通過。
   - 推送前閘與 CI 不直接跑 `check.py`,是跑型錄測試;推主線與 CI 全套一定跑到;推功能分支時推送前閘可能只跑子集([[Systems/bound-tests-gate]]),這兩道自檢最晚在 PR 的 CI 擋。
5. **填資料**:
   - 公開名稱逐一分類。歸到某列的,那列觸發字搜不到就補;補之前查停用字表與 Now in Android 文件頻率(量法:`sweep/` 裡的腳本,對 Now in Android 提交 `2982e63cb691ad49cd009aab43dc206fee6699c2` 剝註解字串後算「出現在幾成 kt 檔」;超過 8% 不補,改寫 `決策不問`)。
   - D-4 照 `mapLatest`、`transformLatest` 的官方文件(新值來時取消前一個轉換,跟 `flatMapLatest` 同類)補這兩個觸發字;頻率超過門檻就改標 `決策不問`,並把 S5 與預期值表 S5 列的這兩種寫法改成「〈API 決策點〉標 `決策不問 API-8`、API-8 的片段進反查」(r2 邊界席已量:補這兩個字對 Now in Android 的情境段數幾乎沒有影響)。
   - 本案新增的觸發字只准是 API 母體的名稱或比對形狀,或 Kotlin 標準函式庫、androidx 的公開名稱(理由附官方文件網址);不准用型錄示範用的變數名(例 `bigList`)。既有觸發字裡的示範變數名(D-60 的 `in bigList`)同批換掉。
   - 反查單位逐條處理:`TEST-` 的單位先照兩個測試路徑判;片段含母體或官方公開名稱、頻率在門檻內的補觸發字;否則寫進〈叫不出的壞寫法〉節。
   - 每補一個觸發字,那列證據樣式自測照跑(`--catalog-only` 到 0 個問題)。
   - 補字前後各量一次 Now in Android(同上提交)整份 kt 檔當新增、照 `app/src/main` 路徑切段的三個數:至少命中一列的檔數比例、情境段數、(段,列)配對數;量法腳本放 `sweep/`。(段,列)配對數增加超過 20% 就停下來攤給人看(盲判成本跟配對數成正比)。三個數字寫進驗證紀錄。
6. **規則包筆記與型錄說明**:型錄開頭〈輸入與口徑〉補兩節的欄位定義、歸屬五種寫法與改由四種值;〈統計〉節多四個數,計數單位:公開名稱數=〈API 決策點〉列數;各歸屬種類筆數=每列每個歸屬項各算一筆;叫不出的單位數=〈叫不出的壞寫法〉列數;各改由筆數=每列一筆;由 `stats_problems` 核。[[Systems/kotlin規則包]] 補兩條 WHY、母體目錄的家(about_code)、`_api_names` 為什麼是私有;順手改正那篇摘要裡「推送前的規則包自檢與 --catalog-only 都會跑」那一句(推送前跑的是型錄測試)。`_kt_sit_path_ok` 的家是 [[Systems/棧別提問表態閘]],那篇補一句「反查也呼叫它」。

**不做**:不改情境題、表態、盲判、段放行的判定(被問到之後的路既有);scripts/lumos 只動一處:把路徑篩選抽成 `_kt_sit_path_ok`,行為不變;不在推送前閘呼叫模型;不判「寫法符不符合需求」本身(見〈天花板〉1);不新增情境列(見〈天花板〉6);第一版只窮舉協程核心函式庫。

## 實務隱患

- **觸發字變多,情境段跟著變多**:每段每個候選列都要表態與盲判,成本跟(段,列)配對數成正比。擋法:補字前量單字頻率(8% 門檻),補完量配對數(增加超過 20% 就停);RETIRE-IF 第一條看新字有沒有抓到真情境。
- **母體抽法跟著格式漂**:klib 清單格式官方標實驗性、跨版本改過排版。擋法:兩份母體檔逐位元組釘死、核 sha256;自檢驗錨點名稱都在、總數不少於 300。換版本時抽法要一起驗。
- **母體檔會觸發推送前的風險型樣**:`.api` 不在推送閘的副檔名黑名單,母體裡的 `lock(` 會中併發類型樣,含母體檔的那次推送會判成高風險。本案本來就是守衛面、走完整審,照判;不為它加黑名單(加了反而讓母體檔不被看見)。
- **「代碼審」變成新的垃圾桶**:寫「代碼審」不用證明什麼。擋法:理由要寫看什麼;〈統計〉列各改由筆數;RETIRE-IF 第二條看比例。
- **改由宣稱擋得住其實擋不住**:一個對應檢查下有多段片段,規則或範本只管其中一種寫法。擋法:改由只在片段層級驗——片段要以整字出現在那條規則的壞例樣本或那一組範本的壞寫法程式裡(先剝註解與字串),完整自檢模式實跑確認那一行被報;〈API 決策點〉不自己背書,指向主表列、由那一列的片段走同一條驗證。
- **規則報的是外層或內層節點**:規則報的節點起訖行要涵蓋片段那一行;規則只報內層節點、片段卻在外層那一行時(例 `kt-nested-collect` 報內層 `collect`),判不過,要換一段片段剛好落在被報節點裡的壞例樣本。
- **片段被剝掉**:剝註解與字串是逐字元的詞法掃描,片段裡有落單的雙引號、`/*`、`//`、`"""`,或片段以 `import`、`package` 開頭時,觸發字可能因此不中(單引號、反引號不受影響)。照判,判不中就進表;理由照實寫原因,這種片段是真的寫法時不准寫 `不是寫法`。
- **舊否決對照(2026-11-12 跑 `lumos rejections`,533 筆,按概念比對)**:[[Systems/kotlin規則包]] 記過否決「樣本逐行比對壞寫法欄」當接電判定(三包 30 多列被擋錯)——那是拿壞寫法欄判「哪條 lint 擋得到」,字面跟真跑結果對不上;本案拿壞寫法片段判「會不會被問」,用的是推送前真正跑的同一套路徑篩選與切段程式;改由規則那一半也實跑規則,不靠字面。[[Systems/棧別提問表態閘]] 記測試執行器預設把型錄指到觸發字永遠不中的小表,S4 的端到端測試要明確指到真型錄。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只在本機讀型錄與母體檔;測試不上網,母體檔在 repo 裡
- 已排除:不可逆:型錄兩節、母體目錄、自檢函式與一支抽出來的路徑判斷,退提交即回原狀
- 守衛面:改型錄自檢、會讓推送前的型錄測試擋人,屬守衛面,走完整設計審(不寫成已排除)

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 協程函式庫逐版公開 API 清單可當窮舉母體 | binary-compatibility-validator 說明(產生並比對 API 清單) | https://github.com/Kotlin/binary-compatibility-validator |
| klib 清單照原始碼名稱、格式為實驗性 | BCV KLib 支援設計文件 | https://github.com/Kotlin/binary-compatibility-validator/blob/master/docs/design/KLibSupport.md |
| 1.10.2 版 klib 母體原檔 | kotlinx.coroutines 1.10.2 標籤的 `.klib.api` 檔 | https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.klib.api |
| 1.10.2 版 JVM 母體原檔 | kotlinx.coroutines 1.10.2 標籤的 `.api` 檔 | https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.api |
| 升版會多出名稱(S1 案例) | kotlinx.coroutines 1.11.0 標籤的 `.klib.api` 有 `associate`、1.10.2 沒有 | https://github.com/Kotlin/kotlinx.coroutines/blob/1.11.0/kotlinx-coroutines-core/api/kotlinx-coroutines-core.klib.api |
| 用官方 API 資料庫逐一檢查呼叫、只收適用平台 | Android Lint 的 `api-versions.xml`;過濾不適用 API 以減少誤報 | https://android.googlesource.com/platform/development/+/8ec5006 ;https://gitlab.e.foundation/e/os/android_build_soong/-/commit/67cf60e7c5bf29db9dec52c575d0250568371a18 |
| 每個值都要被分類、漏了就錯 | Kotlin sealed 類別配 `when` 的窮舉要求 | https://kotlinlang.org/docs/sealed-classes.html#use-sealed-classes-with-when-expression |
| `mapLatest`、`transformLatest` 跟 `flatMapLatest` 同屬「新值來就取消舊的」 | kotlinx.coroutines `mapLatest` 文件 | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/map-latest.html |
| 改由要逐段證明規則會報 | Semgrep 規則測試(`ruleid:`/`ok:` 逐行標註) | https://semgrep.dev/docs/writing-rules/testing-rules |
| 規則要有正反例樣本自測 | ast-grep 規則測試(valid/invalid) | https://ast-grep.github.io/guide/test-rule.html |

全表掃描的原始結果(反查單位的叫得出判定、分類用的頻率、規則、範本資料,以及數數腳本)存在卷證 `governance/review-reports/情境決策點窮舉與壞寫法要叫得出/sweep/`。設計時的數:184 個有片段的單位;照「只試 `app/src/test`」的口徑叫不出 103 個(r2 兩席各自重數);`<無片段>` 單位與兩個測試路徑的口徑在實作時用新腳本重數,寫進〈統計〉。

## 驗收條款

- [S1] 當〈API 決策點〉表跟 API 母體一一對上、歸屬都通過核對時,`api_decision_problems` 應 回空;暫存母體加一行 1.11.0 才有的 `associate` 宣告(並更新 sha256)應 報 `associate` 沒分類;表上多一個母體沒有的名稱 應 報;同一名稱兩列 應 報;母體檔改一個位元組 應 報雜湊不符;歸到 `D-4` 但 D-4 觸發字拿掉 `flatMapMerge` 應 報;D-4 觸發字有 `flatMapMerge` 而表上 `flatMapMerge` 歸 `無決策` 應 報;D-16 觸發字 `UNLIMITED` 搜得到 `UNLIMITED` 而表上歸 `無決策` 應 報;觸發字 `indexOf(` 搜得到名稱 `indexOf` 的比對形狀 `indexOf(` 而表上歸 `無決策` 應 報;名稱 `combine` 寫 `D-5、D-6、撞名 D-35` 應 不報;標 `撞名 D-4` 而 D-4 觸發字搜不到那個名稱 應 報;`launch` 標 `決策不問 代碼審` 而型錄主表有列的壞寫法欄寫到 `launch` 應 報;停用字 `Dispatchers.IO` 對到名稱 `IO`、表上 `IO` 標 `無決策` 而理由沒有「停用字,不帶決策:」開頭 應 報;`決策不問 API-2` 而 API-2 壞寫法欄沒有那個名稱 應 報;歸屬欄寫 `D-04`、`撞名D-4` 或 `無決策、D-4` 應 報;抽出的名稱少於 300 個或抽不到錨點 應 報;理由空白 應 報;klib 標了平台、JVM 清單沒有的 `promise` 應 不在母體;沒標平台的 `coroutineContext` 應 在母體;JVM 的 `isActive` 讀取函式 應 不會在母體多出 `active`;真型錄 應 回空 [test:t_kt_catalog_api_decision_points]
- [S2] 當反查單位照〈用詞〉包成一支檔時,叫不出對應情境列而〈叫不出的壞寫法〉沒有那一列 應 報列編號、對應檢查與片段;一對(情境列, 對應檢查)壞寫法欄沒有反引號片段時 應 要求一個 `<無片段>` 列;`TEST-` 的片段放 `app/src/test` 切不出、放 `app/src/androidTest` 切得出時 應 判叫得出;表上有但現在叫得出 應 報過期;表上的片段在壞寫法欄找不到 應 報;改由寫 `規則 kt-map-await-deferred` 而片段 `forEach { it.await() }` 不在它的壞例樣本 應 報;片段只出現在壞例樣本的 `//` 註解裡 應 報;寫 `範本 T0` 應 報;寫 `範本 T1` 而 T1 只有 `### 壞寫法:API-10 …` 沒有 `### 壞寫法:API-1 …` 應 報;片段不在那個壞寫法小節的程式圍欄裡 應 報;`<無片段>` 寫 `不是寫法` 應 報;改由是四種以外的值或理由空白 應 報;片段含表格跳脫的 `\|` 應 還原後再比;停用列的片段 應 不算;真型錄 應 回空 [test:t_kt_catalog_bad_snippets_reach_rows]
- [S3] 當 D-4 觸發字拿掉 `flatMapMerge` 時,S1 那道 應 紅(歸屬搜不到) [test:t_kt_catalog_api_decision_points]
- [S4] 當 D-4 觸發字拿掉 `flatMapMerge` 時,S2 那道 應 紅(API-8 壞寫法欄的片段 `flatMapMerge` 叫不出且表上沒有);只拿掉〈API 決策點〉裡 `flatMapMerge` 那一列時,S2 應 綠——兩道各自守、不互相掩護 [test:t_kt_catalog_bad_snippets_reach_rows]
- [S5] 當實驗 repo(型錄明確指到真型錄,不用測試執行器預設的小表)的搜尋 ViewModel 分別用 `flatMapMerge`、`flatMapConcat`、`mapLatest`、`transformLatest` 接查詢輸入、沒有 `debounce`、檔在 `app/src/main/` 底下時,`lumos pitfalls --diff` 應 每種都出情境段且候選列含 D-4 [test:t_kt_situation_api_family_e2e]
- [S6] 當 `_kt_situation_segments` 改成呼叫 `_kt_sit_path_ok` 之後,既有情境段切段的測試 應 全綠;`check.py` 的反查 應 呼叫同一支函式而不是自己組條件 [test:t_kt_situation_segments]
- [S7] 當完整自檢模式(`check.py --sg <ast-grep>`)跑真型錄時,〈叫不出的壞寫法〉每個 `規則 <id>` 改由,那條規則在壞例檔報出的節點起訖行 應 涵蓋片段所在那一行;把其中一段片段在壞例樣本裡改成規則不報的寫法 應 報問題;掃描逾時或失敗 應 報問題而不是通過 [test:t_kotlin_rulepack_samples]
- [S8] 當 `python3 configs/ast-grep/kotlin-android/check.py --catalog-only` 跑真型錄時,應 0 個問題,且〈統計〉節的公開名稱數、各歸屬種類筆數、叫不出的單位數、各改由筆數 應 照〈範圍〉6 的計數單位等於重數(擴充既有的統計核對測試) [test:t_kt_catalog_stats_consistent]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 暫存母體加一行 `associate` 宣告、表不動 | 報 `associate` 沒分類 | 依據來源 1.11.0 那列 |
| S1 | 表上 `flatMapMerge` 歸 `D-4`,D-4 觸發字拿掉 `flatMapMerge` | 報 `flatMapMerge` 歸屬搜不到觸發字 | 範圍 1 的 `D-n` 項核對 |
| S1 | D-16 觸發字有 `UNLIMITED`,表上 `UNLIMITED` 歸 `無決策` | 報兩邊不同步 | 範圍 2 反向;r1 三席實測 |
| S1 | D-60 觸發字 `indexOf(`,表上 `indexOf` 歸 `無決策` | 報兩邊不同步 | 範圍 2 反向的比對形狀;r2 邊界席實測 |
| S1 | `combine` 寫 `D-5、D-6、撞名 D-35` | 不報 | 範圍 1 歸屬可並列;r2 邊界席實測 `combine` 被三列搜到 |
| S1 | `IO` 標 `無決策`、理由沒有停用字前綴 | 報 | 範圍 2 停用字表;停用字表有 `Dispatchers.IO` |
| S1 | klib 的 `promise`(標了平台、JVM 清單沒有) | 不在母體 | 〈用詞〉只留適用 JVM 的;2026-11-12 試抽 |
| S1 | klib 的 `coroutineContext`(JVM 清單只有 `getCoroutineContext`) | 在母體 | 同上:沒標平台的照收;2026-11-12 試抽 |
| S1 | JVM 的 `isActive ()Z` | 母體不多出 `active` | 〈用詞〉JVM 補來源不還原讀取函式;r2 正確性席實測 |
| S2 | API-8 壞寫法片段 `flatMapConcat { search(it) }`,D-4 觸發字沒有 `flatMapConcat`、表上也沒有 | 報 `D-4`、`API-8`、那段片段 | 2026-11-12 實驗:沒加 debounce 時 D-4 不在候選列 |
| S2 | D-13 對應 STATE-14,壞寫法欄沒有反引號片段、表上沒有 `<無片段>` 列 | 報缺 `<無片段>` | r2 邊界席實測:11 對沒有片段 |
| S2 | TEST-29 片段 `composeTestRule.mainClock.autoAdvance = false` | 判叫得出(androidTest 路徑切得出 D-51) | r2 邊界席實測 |
| S2 | 〈叫不出的壞寫法〉一列:D-3、API-2、片段 `forEach { it.await() }`、改由「規則 kt-map-await-deferred」 | 報片段不在那條規則的壞例樣本 | r1 三席:那條規則只收 map |
| S2 | 改由寫 `範本 T1`、單位的對應檢查是 API-1,範本只留 `### 壞寫法:API-10 …` | 報找不到 API-1 的壞寫法小節 | r2 邊界席:前綴比對會誤過 |
| S3 | D-4 觸發字拿掉 `flatMapMerge`(表不動) | S1 紅 | 範圍 2 的正向核對 |
| S4 | 同上 | S2 紅;只拿掉表上 `flatMapMerge` 那列時 S2 綠 | 範圍 3 的反查判法 |
| S6 | `_kt_sit_path_ok("app/src/test/java/x/XTest.kt")` 與 `_kt_sit_path_ok("app/src/main/java/x/X.kt")` | 前者不通過、後者通過,跟抽出前 `_kt_situation_segments` 的篩選結果相同 | 〈用詞〉路徑篩選:行為不變 |
| S5 | 搜尋 ViewModel 用 `mapLatest` 接查詢、沒有 `debounce` | 出情境段,候選列含 D-4 | `mapLatest` 文件;範圍 5 照此歸 D-4 |
| S7 | `kt-nested-collect` 報內層 `collect` 那一行,片段 `collectLatest` 在外層那一行 | 報問題(要換樣本) | 〈實務隱患〉規則報外層或內層節點;r2 正確性席實測 |
| S8 | 真型錄跑 `--catalog-only` | 0 個問題 | 範圍 5 填完後的狀態 |

## 回退

退回本案的提交:型錄少兩節、自檢少兩道、母體目錄消失、`_kt_sit_path_ok` 併回原處(行為本來就不變);本案補的觸發字(含 D-4 的 `mapLatest`、`transformLatest`)跟著退回,情境段回到原本的範圍;D-4 補 `flatMapMerge`、`flatMapConcat` 那一筆是另一個提交,不跟著退。

## 天花板

1. 窮舉的是「哪些寫法帶情境決定」,不是「這次的寫法合不合需求」;需求在程式外,機器只能保證決策點被問到或寫明改由誰抓、答案留痕、判不了交給人。
2. 第一版只窮舉 kotlinx-coroutines-core;androidx 的 lifecycle、work、room、compose 的決策點(例 `ExistingWorkPolicy.REPLACE`、`repeatOnLifecycle`)還是靠反查與手寫觸發字。JVM 專屬的類別成員與屬性(只在 JVM 清單、klib 沒有的)不收進母體;在 JVM 用 `@JvmName` 改了名、klib 又標成平台限定的名稱會被誤丟(1.10.2 是 `asCoroutineDispatcher`),實作時把「klib 丟掉的名稱」印出來人工核一次、結果寫進驗證紀錄,誤丟的在〈API 決策點〉理由寫明、由反查單位兜底;`@JsName` 留下的名稱(例 `Job0`)會進母體,標 `無決策`;typealias 兩份清單都不列,也不在窮舉內。
3. 自家包裝函式把決策點藏起來(例自寫 `fun <T> Flow<T>.latest()` 內部用 `flatMapLatest`),呼叫端不會被問;包裝函式本身被寫出來的那次會被問。別名匯入(`import kotlinx.coroutines.flow.flatMapMerge as fm`)同理:呼叫處寫 `fm` 不會被問,`import` 行又被切段略過。
4. 帶情境決定、但字面太常見的寫法不當觸發字:母體裡的(`launch`、`collect`)標 `決策不問`;不在母體的(`onClick`)只能由反查單位進〈叫不出的壞寫法〉表。兩邊都只能靠形狀規則、行為測試範本或代碼審,寫在表上讓人看得到。
5. 壞在「沒寫某樣東西」的寫法(例 D-2 該並行卻串行、迴圈裡 `launch` 沒限流)沒有字面可以觸發,只能進〈叫不出的壞寫法〉表、改由代碼審或範本。
6. 有決策點、但型錄還沒有對應情境列的(例 `runBlocking`、`SupervisorJob`、`CoroutineStart.UNDISPATCHED`),本案先標 `決策不問`,不在本案新增情境列;`決策不問` 指到的主表列不是任何情境列的對應檢查時,那一列的壞寫法不進反查。
7. 被問到之後,作者的答案沒有「依據哪條需求」的欄位,盲判也看不到規格;使用者 2026-11-12 定的最終目標:AI 先依計劃的驗收條款或預期值表判斷並引出處,規格沒寫的一律擋下交人裁,人的決定寫回計劃(新條款與預期值表列)並綁一支改壞會紅的行為測試,下次同一段直接引用——形成「被問到 → 依規格判 → 規格沒寫交人 → 寫回規格 → 測試守住」的循環。這件事改的是已上線的表態與盲判,另開後續計劃,本案推送後接著開工,不排日期等。

REVISIT:2026-11-19 確認後續計劃「情境題答案要引規格出處與回寫循環」已開工(本案推送後當天就開;這行是保底)
REVISIT:2027-01-15 把 androidx.lifecycle、androidx.work、androidx.room 的 API 清單也納入 API 母體,並替〈天花板〉6 那批決策點補情境列
REVISIT:2027-02-12 查 kotlinx-coroutines 有沒有比 1.10.2 新、而且行為測試範本已經跟上的版本;有就換母體重新分類(本案上線時 1.11.0 已出、範本還在 1.10.2)

## 審計修正紀錄

- r1(2026-11-12,四席 sonnet:通才、正確性、邊界、架構對齊):33 條/blocking 17(通才 7、正確性 4、邊界 6;架構對齊 0)/母體定義被三席同時打穿(成員函式整類不在、`Channel$Factory` 常數被 `$` 規則排掉、雜湊名讓同步檢查漏)、「改由規則」只核編號不核規則真的會報(三席)、反查用假路徑繞過推送前的測試檔篩選(正確性席獨有,實測屬實);全部折入,歸八組根因,逐條去向與先查世界在 r1-intake.md。卷證:governance/review-reports/情境決策點窮舉與壞寫法要叫得出/。
- r1 新增機制前的最小解檢查:①母體改用 klib 清單——最小解是修 JVM 清單的抽法,三席各舉出不同的還原失敗(getter 大小寫、`$Factory`、雜湊、成員),修補要四條特例且仍判不出大小寫;klib 直接是原始碼名稱,特例只剩 JVM 補來源那一小撮。②母體 sha256——最小解是信任「逐位元組放」,但手改母體會讓自檢把殘缺母體當真、全綠;核雜湊一行就擋。③`撞名` 與 `決策不問` 兩種歸屬——不加的話,反向同步會逼 `merge` 歸到不相干的 D-59、`launch` 這類只能謊稱 `無決策`;兩種歸屬都要寫理由並計數。④反查走推送前的路徑篩選——不加就對 `TEST-` 片段給出假的「叫得出」,正是本案要消的默默放行。⑤改由規則實跑——不加就讓一條規則替同一編號下所有片段背書。
- r2(2026-11-12,四席 sonnet:通才、正確性、邊界、架構對齊):37 條/blocking 10(通才 1、正確性 5、邊界 4;架構對齊 0)/「母體抽法」與「改由驗證」同類第二次被打穿,依規則先查方向(方向:對,換形狀):JVM 補來源不再還原讀取函式與成員、klib 名稱只留 JVM 清單也有的;〈API 決策點〉不再自己背書改由,改指向主表列、由片段層級的同一條驗證負責;另補歸屬可並列、`<無片段>` 單位、測試路徑試兩個、路徑篩選抽成單一函式;全部折入,逐條去向與先查世界在 r2-intake.md。
- r2 新增機制前的最小解檢查:①`_kt_sit_path_ok` 抽出——最小解是 `check.py` 照抄條件,架構對齊席指出會跟推送端悄悄分家,抽成一支兩邊共用的成本只有一個函式;②`<無片段>` 單位——不加就有 11 對(情境列, 對應檢查)在機器眼裡不存在,本案「沒被問到的都要列表」的承諾直接破功;③歸屬並列——不加的話 `combine` 這類被多列搜到的名稱只能說謊;④`scan()` 多回起訖行——不加就要另掃一遍或用起始行誤判,既有掃描本來就拿得到。
