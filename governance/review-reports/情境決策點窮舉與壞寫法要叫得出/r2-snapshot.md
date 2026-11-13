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

> 白話:推送前的情境題(型錄〈情境決策表〉每列一個情境,改動命中觸發字就要表態、再由盲判代理獨立判一次)只在「被問到」時守得住;沒被問到就整段默默放行。2026-11-12 實驗發現搜尋框改用 `flatMapMerge`、`flatMapConcat` 時,「只要最新一次」那一列根本不會被問(觸發字只收好寫法的字,`flatMapLatest`、`debounce`),已先補了那一列。接著全表掃描:184 段對應檢查列的壞寫法片段,有 95 段單獨出現時叫不出它對應的情境列。這份計劃讓「沒被問到」不再沒人知道:每一個沒被問到的寫法,都要列在型錄上、寫明改由誰抓,而且「誰抓」要機器驗得到。從兩個方向圍:①**從函式庫窮舉**:協程核心函式庫的公開 API 清單是有限的、官方逐版發布,把每個公開名稱分類成「選了它就等於做了情境決定(歸到某一列,且一定被那列的觸發字搜得到)」「帶決定、但不問(寫明改由誰抓)」「被某列觸發字搜到、但意思不同(撞名,寫差在哪)」或「不帶情境決定(寫理由)」,升版多出來的名稱沒分類就紅;②**從型錄的壞寫法反查**:每段壞寫法片段要嘛照推送前同一套路徑篩選與切段就叫得出對應列,要嘛明寫改由哪裡抓。使用者原話(2026-11-12):「雖然他是需要確認情境的規則,但有時候規則往往沒辦法在第一時間確認清楚,這時候,如果放行AI寫出這樣的語法,就會出問題而沒發現」「我是想避免這種情況出現」「我相信Kotlin的語法絕對窮舉得出來,各種語法對應當下情境是不是符合功能需求,或是功能需求定義不清需要進一步釐清語法有沒有適用,是做得到的對嗎」。

PRIOR-ART: ①窮舉來源:kotlinx.coroutines 用 Kotlin 官方的二進位相容檢查工具(binary-compatibility-validator,https://github.com/Kotlin/binary-compatibility-validator )把每一版的公開 API 存在 repo 裡,有兩份:Kotlin 層級的 klib 清單(`kotlinx-coroutines-core.klib.api`,宣告照原始碼的名字寫,例 `final val Lazily`、`final const val UNLIMITED`、成員 `abstract fun trySend`,沒有 JVM 名稱修飾;格式說明 https://github.com/Kotlin/binary-compatibility-validator/blob/master/docs/design/KLibSupport.md ),與 JVM 層級的 `.api` 清單(編譯後形狀:getter、`-雜湊` 後綴、`$Companion`)。klib 清單只涵蓋原生、JS、Wasm 平台,不含 JVM;2026-11-12 比對 1.10.2 兩份,JVM 專屬的公開名稱有幾十個(例 `runInterruptible`、`future`、`asExecutor`、`ticker`)。採用「klib 清單為主、JVM 清單補 klib 沒有的名稱」;不選:只用 JVM 清單從 getter 與雜湊還原(r1 三席實測:`Channel.UNLIMITED` 被 `$` 規則排掉、getter 還原分不出大小寫、成員函式整類不在、雜湊名讓同步檢查漏);不選:從語料統計常見寫法(窮舉不完)。②強迫分類的形狀:Kotlin 對 sealed 類別的 `when` 要求窮舉每個分支、漏了編譯失敗(https://kotlinlang.org/docs/sealed-classes.html#use-sealed-classes-with-when-expression ),本案照這個形狀——母體裡每個名稱一定要被歸類。③「改由規則」要逐段證明規則真的會報:Semgrep 規則測試以每一行的 `ruleid:` 標註要求那一行一定被報、`ok:` 一定不報(https://semgrep.dev/docs/writing-rules/testing-rules );ast-grep 規則測試的 valid/invalid 同理(https://ast-grep.github.io/guide/test-rule.html )。採用「片段要逐字出現在那條規則的壞例樣本裡,完整自檢模式再實跑規則確認那一行被報」。④常用字門檻沿用 [[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 實驗 E9:Now in Android 310 支 kt 檔的文件頻率超過 8% 的字不當觸發字。
RETIRE-IF: 上線八週後用 `lumos gov --stats` 看:本案新加的觸發字所切出的情境段,盲判判「不適用」超過八成 → 那些字太寬,收窄或改歸「決策不問」;改由寫「代碼審」的超過全部改由的一半而且漏網帳(`lumos loop escape --list`)八週內沒有一筆落在這些列 → 反查那一半降成只在新增列時要求;協程函式庫連兩次升版都沒有新增需要歸到情境列的名稱 → 窮舉改成只在升版時跑。

## 用詞

- **情境列**:型錄〈情境決策表〉的一列(`D-n`),有情境、標準寫法、不適用時、觸發字、證據樣式、對應檢查。
- **被問到**:一支改動檔,先過推送前同一套路徑篩選(測試檔、非正式碼不出情境段:scripts/lumos 的 `_PITFALL_DIFF_TEST_PAT` 與 `_stack_changed_ok`,`_kt_situation_segments` 就是這樣篩),再經情境段切法(`_kt_sit_text_segments` 這一族,剝掉註解與字串、比對觸發字)切出一段、那段的候選列含這一列。被問到之後的路既有、本案不改:情境題只收「適不適用、照哪個寫法」,不收 na 或 todo;缺段、缺列、答案形狀不對、缺第一盲判、作者與第一盲判不一致又沒有仲裁,都擋;證據樣式對不上、仲裁多數判作者沒照做只提醒不擋;判不了的出口是段放行,人或 AI 都能下,AI 下的記成 AI 放行、在 doctor 與推送前小結列到有人確認為止([[Projects/Android寫法語意情境表態與盲判_計劃]])。所以「需求一時說不清」的情況,只要被問到,就不會沒留痕地過。
- **型錄主表列編號**:型錄主表一列一種寫法,編號是主題前綴加數字(例 `API-8`、`FLOW-22`、`TEST-7`);情境列的「對應檢查」欄就是這種編號。
- **會擋的規則**:規則包 `configs/ast-grep/kotlin-android/rules/` 目錄底下的規則(推送前新增告警閘照範本宣告的那份);同層的 `rules-review/`、`rules-hints/`、`rules-unwired/` 都不擋。規則訊息開頭一律是 `[型錄主表列編號]`;每條規則的壞例樣本在 `samples/bad/<規則 id>/`。
- **通電批次欄、範本 T<n>**:型錄主表第 10 欄,記每種接電方式在哪一批生效;其中「行為測試或正向約束=範本 T<n>」指 `skills/kotlin-idioms/test-templates.md` 的第 n 組行為測試範本,每組有 `### 壞寫法:<型錄主表列編號> …` 小節(要有人照範本寫測試才守得住,不會自動跑)。T0 是「測試骨架守則」,不是行為測試範本。
- **停用列、停用字表**:兩件事。停用列是型錄標了「(停用)」的列,觸發字與證據樣式都是(無)、不出題;停用字表是 `check.py` 的 `STOP_TRIGGERS`,列「太常見、不准當觸發字」的字。
- **段放行**:情境題判不了時的出口,`lumos lint-waive kt-situation:<段身分>`,記誰放行、理由。
- **代碼審**:分支推送前派審查代理讀改動的迴圈([[Systems/pitfalls-code-loop]]),靠代理讀,不是機械檢查。
- **API 母體**:兩份釘版檔,`configs/ast-grep/kotlin-android/api/kotlinx-coroutines-core-1.10.2.klib.api`(新增)與 `configs/ast-grep/kotlin-android/api/kotlinx-coroutines-core-1.10.2.api`(新增),照官方 1.10.2 標籤的原檔逐位元組放(版本跟行為測試範本用的 1.10.2 一致);型錄〈API 決策點〉第一行記兩份的網址與 sha256,自檢核對檔案雜湊。
- **公開名稱**:從 API 母體抽出、寫程式時會打出來的名字,一個名字一列(不分多載、不分接收者、不分是類別還是同名工廠函式;`Channel` 類別與 `Channel(...)` 工廠是同一列)。
  - 主來源 klib 清單:每個宣告行(`fun`、`val`、`var`、`const val`、`class`、`interface`、`object`、`enum entry`)的簡名,含類別成員;不收 `<init>`、`<get-…>`、`<set-…>`、`Any` 的 `equals`、`hashCode`、`toString`、資料類別自動產生的 `componentN` 與 `copy`、`Companion`;套件路徑含 `internal` 的不收。
  - 補來源 JVM 清單:只收「正規化後 klib 裡沒有」的名稱。正規化:去掉 `-<7 碼雜湊>` 與 `-impl` 後綴、`$default`;跳過標 `synthetic` 的、`access$` 開頭的、`…Kt` 門面類別名、類別名含 `$` 的類別本身;不帶參數的 `getX`/`isX` 讀取函式還原成屬性名(首字大小寫兩種都跟 klib 比,klib 都沒有才以首字小寫收)。
  - 抽法只有型錄自檢 `check.py` 一處(`_api_names`,新增)。
- **決策點**:選了它就等於做了某個情境決定的公開名稱(例:`flatMapMerge` 等於選了「新值來了舊的不取消、並行跑」)。
- **壞寫法片段**:每個非停用情境列「對應檢查」欄每個編號,在型錄主表那一列「壞寫法形狀」欄裡每一段反引號包住的文字(表格裡的 `\|` 還原成 `|`),不做長度或字元過濾——過濾本身就是不出聲的漏洞。觸發字寫(無)的列(例 D-2)也算,它的片段必然叫不出、必然要進表。單位是(情境列, 對應檢查, 片段);2026-11-12 用 `sweep/` 的腳本照這個口徑數:184 個,叫不出 95 個。
- **叫得出**:片段包成 `class X {` / `fun f() {` / 片段 / `}` / `}`,當成一支新增檔,路徑依對應檢查編號定:`TEST-` 開頭用 `app/src/test/java/x/XTest.kt`,其他用 `app/src/main/java/x/X.kt`;先過推送前那道路徑篩選,過了再切段,切出的段的候選列含那一列才算。測試檔在推送前根本不出情境段,所以 `TEST-` 的片段一律叫不出、要進表。
- **改由**:沒被問到時改由誰抓,〈API 決策點〉與〈叫不出的壞寫法〉兩節共用同一組值與同一套核對:
  - `規則 <id>`:那條規則在會擋的 `rules/` 目錄,訊息開頭引的編號等於對應檢查;而且片段(〈API 決策點〉那邊是名稱)要逐字出現在 `samples/bad/<id>/` 的某支壞例檔裡。完整自檢模式(`check.py --sg <ast-grep>`)另外實跑那條規則,確認片段所在那一行被報。
  - `範本 T<n>`:n 不是 0;等於對應檢查列通電批次欄「行為測試或正向約束=」的值;範本那一組有 `### 壞寫法:<對應檢查>` 小節(〈API 決策點〉那邊:那一組任一個壞寫法小節的程式碼含這個名稱)。
  - `代碼審`:理由要寫代碼審要看什麼。
  - `不是寫法`:片段不是一段程式寫法(例 `[Loading, Success]`、`delay(常數)`);只限〈叫不出的壞寫法〉用。
  - 其他值、或理由空白 → 問題。

## 範圍

1. **API 決策點節**:型錄在〈接電證據〉之後新增〈API 決策點〉節(放在〈情境決策表〉到〈待查證〉那一段之外,免得被決策表的讀法吃進去)。第一行固定 `母體:kotlinx-coroutines-core 1.10.2,klib <網址> sha256 <值>,jvm <網址> sha256 <值>`;接一張表「名稱 | 歸屬 | 理由」,公開名稱每個恰好一列。歸屬四種:
   - 一到多個 `D-n`(以「、」分隔):那個名稱是這幾列的決策點。每一列都要有一個觸發字,經 `_kt_trigger_re` 編成的正規式在名稱字串裡搜得到(方向固定是「觸發字的正規式搜名稱」,跟推送前拿觸發字搜程式碼同方向);觸發字帶點的(`SharingStarted.Lazily`)比名稱前加上外層宣告的寫法(`SharingStarted.Lazily`),兩種寫法任一搜得到就算。
   - `決策不問:<改由>`:是決策點,但不當觸發字(在停用字表裡、Now in Android 文件頻率超過 8%,或還沒有對應的情境列);改由照〈用詞〉的核對。
   - `撞名 D-n`:那一列的觸發字搜得到這個名稱,但意思不同(例 D-59 資料同步衝突的觸發字 `merge` 搜得到 Flow 的 `merge`);理由寫兩者差在哪。
   - `無決策`:不代表情境選擇(例 `emptyFlow` 只是建空流);理由一句。
2. **API 決策點自檢**(`check.py` 的 `api_decision_problems(lumos, catalog_text, api_dir, samples_dir, templates_text)`,新增;回 `[(名稱或 <api>, 原因)]`):
   - 兩份母體檔的 sha256 跟第一行對不上 → 問題(母體被改過)。
   - 母體裡有、表上沒有的名稱 → 問題(升版多出來的名稱一定被點到)。
   - 表上有、母體裡沒有的名稱 → 問題(升版拿掉或打錯)。
   - 同一個名稱出現兩列 → 問題。
   - 歸到 `D-n` 但那列觸發字搜不到它、或那列是停用列 → 問題。
   - 反向:任一非停用列的任一觸發字的正規式搜得到某個名稱,而那個名稱沒有歸到這一列、也沒標 `撞名` 這一列 → 問題(兩邊不同步;跟正向同一個方向,雜湊名與 `Channel.UNLIMITED` 這類都照搜)。
   - 抽不到錨點名稱(`flatMapLatest`、`Mutex`、`Lazily`、`UNLIMITED`、`trySend`)、或抽出的名稱少於 300 個 → 問題(抽法壞了)。
   - 標 `撞名 D-n` 而那一列的觸發字根本搜不到它 → 問題(撞名是假的)。
   - 停用字表裡的名稱標 `無決策`,理由不是以「停用字,不帶決策:」開頭 → 問題(停用字最常被選錯,不准用 `無決策` 默默帶過;真的不帶決策要寫出為什麼)。
   - `決策不問` 的改由寫 `不是寫法` → 問題(名稱一定是寫法)。
   - 任一列理由空白 → 問題。
3. **叫不出的壞寫法節與自檢**:型錄〈API 決策點〉之後新增〈叫不出的壞寫法〉節,表「列編號 | 對應檢查 | 片段 | 改由 | 理由」;`check.py` 的 `bad_snippet_reach_problems(lumos, catalog_text, samples_dir, templates_text)`(新增;回 `[(列編號或 <reach>, 原因)]`):
   - 叫不出、表上又沒有 → 問題,訊息印列編號、對應檢查與片段。
   - 表上有、但現在叫得出 → 問題(過期,補了觸發字就要刪這一列)。
   - 表上有、但型錄壞寫法欄已經沒有這段片段 → 問題。
   - 改由照〈用詞〉的核對,不合 → 問題。
4. **接法**:兩支新函式照既有的 `situation_sample_problems(lumos=)` 接:不放進 `catalog_problems`(它的說明寫明不載入 scripts/lumos,測試用型錄複本呼叫它四十多處),在 `check()` 與 `--catalog-only` 另外串;要用的 lumos 模組、型錄全文、樣本目錄、母體目錄、範本全文都由參數傳入,測試傳型錄複本與暫存母體。完整自檢模式(`check.py --sg <ast-grep>`)另串一支 `route_rule_hits_problems(sg, catalog_text, samples_dir)`(新增):兩節所有寫 `規則 <id>` 的改由都實跑那條規則——〈叫不出的壞寫法〉的片段所在那一行要被報;〈API 決策點〉的名稱:壞例樣本裡含這個名稱的行至少一行被報;沒報 → 問題。只在有 ast-grep 的完整模式跑(同既有規則樣本自檢)。推送前閘與 CI 不直接跑 `check.py`,是跑型錄測試;型錄在 `skills/` 底下,推送前閘不會把它的改動判成純文件,一定跑到這些測試。
5. **填資料**:
   - 公開名稱逐一分類。歸到某列的,那列觸發字搜不到就補;補之前查停用字表與 Now in Android 文件頻率(量法:`sweep/` 裡的腳本,對 Now in Android 釘版提交剝註解字串後算「出現在幾成 kt 檔」;超過 8% 不補,改寫 `決策不問`)。
   - 本案新增的觸發字只准是 API 母體的名稱,或 Kotlin 標準函式庫、androidx 的公開名稱(理由附官方文件網址);不准用型錄示範用的變數名(例 `bigList`)。既有觸發字裡的示範變數名(D-60 的 `in bigList`)同批換掉。
   - D-4 照 `mapLatest`、`transformLatest` 的官方文件(新值來時取消前一個轉換,跟 `flatMapLatest` 同類)補這兩個觸發字;頻率超過門檻就改標 `決策不問` 並把 S4 那兩種寫法改成驗表上有標。
   - 95 段叫不出的壞寫法逐條處理:片段含母體或官方公開名稱、頻率在門檻內的補觸發字;否則寫進〈叫不出的壞寫法〉節。
   - 每補一個觸發字,那列證據樣式自測照跑(`--catalog-only` 到 0 個問題)。
   - 補字前後各量一次「Now in Android 有幾成 kt 檔至少命中一列」(E9 記的基準是 64%),兩個數字寫進驗證紀錄;增加超過 10 個百分點就停下來攤給人看。
6. **規則包筆記與型錄說明**:型錄開頭〈輸入與口徑〉補兩節的欄位定義與改由的四種值;〈統計〉節多四個數(公開名稱數、各歸屬種類筆數、叫不出的壞寫法數、各改由筆數),由 `stats_problems` 核;[[Systems/kotlin規則包]] 補兩條 WHY、兩份母體檔的家(about_code)、`_api_names` 為什麼是私有;順手改正那篇摘要裡「推送前的規則包自檢與 --catalog-only 都會跑」那一句(推送前跑的是型錄測試)。

**不做**:不改情境題、表態、盲判、段放行的判定(被問到之後的路既有);不改 scripts/lumos(只借它既有的路徑篩選、切段與觸發字函式);不在推送前閘呼叫模型;不判「寫法符不符合需求」本身(見〈天花板〉1);不新增情境列(沒有對應列的決策點先標 `決策不問`,見〈天花板〉6);第一版只窮舉協程核心函式庫。

## 實務隱患

- **觸發字變多,情境段跟著變多**:每段每個候選列都要表態與盲判,成本上升。擋法:補字前量單字頻率(8% 門檻),補完量整體命中比例(增加超過 10 個百分點就停);RETIRE-IF 第一條看盲判「不適用」比例。
- **母體抽法跟著格式漂**:klib 清單格式官方標實驗性、跨版本改過(分組與空行)。擋法:兩份母體檔逐位元組釘死、核 sha256;自檢驗錨點名稱都在、總數不少於 300。換版本時抽法要一起驗。
- **「代碼審」變成新的垃圾桶**:寫「代碼審」不用證明什麼。擋法:理由要寫看什麼;〈統計〉列各改由筆數;RETIRE-IF 第二條看比例。
- **改由規則宣稱擋得住其實擋不住**:一個對應檢查下有多段片段,規則只管其中一種寫法。擋法:片段要逐字出現在那條規則的壞例樣本裡,完整自檢模式實跑確認那一行被報。
- **片段被剝掉**:剝註解與字串是逐字元的詞法掃描,片段裡有落單的雙引號、`/*`、`//`、反引號,或片段以 `import`、`package` 開頭時,觸發字可能因此不中(單引號不受影響)。照判,判不中就進表;理由照實寫原因,這種片段是真的寫法時不准寫 `不是寫法`。
- **舊否決對照(2026-11-12 跑 `lumos rejections`,533 筆,按概念比對)**:[[Systems/kotlin規則包]] 記過否決「樣本逐行比對壞寫法欄」當接電判定(三包 30 多列被擋錯)——那是拿壞寫法欄判「哪條 lint 擋得到」,字面跟真跑結果對不上;本案拿壞寫法片段判「會不會被問」,用的是推送前真正跑的同一套路徑篩選與切段程式;改由規則那一半也改成實跑規則,不靠字面。[[Systems/棧別提問表態閘]] 記測試執行器預設把型錄指到觸發字永遠不中的小表,S4 的端到端測試要明確指到真型錄。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只在本機讀型錄與母體檔;測試不上網,母體檔在 repo 裡
- 已排除:不可逆:型錄兩節、兩份母體檔與自檢函式,退提交即回原狀
- 守衛面:改型錄自檢、會讓推送前的型錄測試擋人,屬守衛面,走完整設計審(不寫成已排除)

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 協程函式庫逐版公開 API 清單可當窮舉母體 | binary-compatibility-validator 說明(產生並比對 API 清單) | https://github.com/Kotlin/binary-compatibility-validator |
| klib 清單照原始碼名稱、格式為實驗性 | BCV KLib 支援設計文件 | https://github.com/Kotlin/binary-compatibility-validator/blob/master/docs/design/KLibSupport.md |
| 1.10.2 版 klib 母體原檔 | kotlinx.coroutines 1.10.2 標籤的 `.klib.api` 檔 | https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.klib.api |
| 1.10.2 版 JVM 母體原檔 | kotlinx.coroutines 1.10.2 標籤的 `.api` 檔 | https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.api |
| 升版會多出名稱(S1 案例) | kotlinx.coroutines 1.11.0 標籤的 `.api` 檔(2026-11-12 比對多 17 個條目、10 個不重複的名稱,例 `associate`) | https://github.com/Kotlin/kotlinx.coroutines/blob/1.11.0/kotlinx-coroutines-core/api/kotlinx-coroutines-core.api |
| 每個值都要被分類、漏了就錯 | Kotlin sealed 類別配 `when` 的窮舉要求 | https://kotlinlang.org/docs/sealed-classes.html#use-sealed-classes-with-when-expression |
| `mapLatest`、`transformLatest` 跟 `flatMapLatest` 同屬「新值來就取消舊的」 | kotlinx.coroutines `mapLatest` 文件 | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/map-latest.html |
| 改由規則要逐段證明規則會報 | Semgrep 規則測試(`ruleid:`/`ok:` 逐行標註) | https://semgrep.dev/docs/writing-rules/testing-rules |
| 規則要有正反例樣本自測 | ast-grep 規則測試(valid/invalid) | https://ast-grep.github.io/guide/test-rule.html |

全表掃描的原始結果(壞寫法片段的叫得出判定、分類用的頻率、規則、範本資料,以及數數腳本)存在卷證 `governance/review-reports/情境決策點窮舉與壞寫法要叫得出/sweep/`。

## 驗收條款

- [S1] 當〈API 決策點〉表跟 API 母體一一對上、歸屬都通過核對時,`api_decision_problems` 應 回空;暫存母體加一行 1.11.0 才有的 `associate` 宣告(並更新 sha256)應 報 `associate` 沒分類;表上多一個母體沒有的名稱 應 報;同一名稱兩列 應 報;母體檔改一個位元組 應 報雜湊不符;歸到 `D-4` 但 D-4 觸發字拿掉 `flatMapMerge` 應 報;D-4 觸發字有 `flatMapMerge` 而表上 `flatMapMerge` 歸 `無決策` 應 報;D-16 觸發字 `UNLIMITED` 搜得到名稱 `UNLIMITED` 而表上歸 `無決策` 應 報;名稱 `merge` 被 D-59 的觸發字搜到、表上標 `撞名 D-59` 應 不報;標 `撞名 D-4` 而 D-4 觸發字搜不到那個名稱 應 報;停用字表裡的 `launch` 標 `無決策` 而理由沒有「停用字,不帶決策:」開頭 應 報;`決策不問:不是寫法` 應 報;抽出的名稱少於 300 個 應 報;歸到停用列 應 報;`決策不問:規則 <id>` 而那條規則的壞例樣本沒有這個名稱 應 報;理由空白 應 報;抽不到錨點名稱 應 報;真型錄 應 回空 [test:t_kt_catalog_api_decision_points]
- [S2] 當型錄壞寫法片段照〈用詞〉包成一支檔時,叫不出對應情境列而〈叫不出的壞寫法〉沒有那一列 應 報列編號、對應檢查與片段;`TEST-` 開頭的對應檢查的片段 應 判叫不出(路徑被推送前篩選排除);表上有但現在叫得出 應 報過期;表上的片段在壞寫法欄找不到 應 報;改由寫 `規則 kt-map-await-deferred` 而片段 `forEach { it.await() }` 不在它的壞例樣本 應 報;寫 `範本 T0` 應 報;寫 `範本 T<n>` 而跟通電批次的值不同、或那一組沒有那個對應檢查的壞寫法小節 應 報;改由是四種以外的值或理由空白 應 報;片段含表格跳脫的 `\|` 應 還原後再比;停用列的片段 應 不算;真型錄 應 回空 [test:t_kt_catalog_bad_snippets_reach_rows]
- [S3] 當 D-4 觸發字拿掉 `flatMapMerge` 時,S1 那道 應 紅(歸屬搜不到),S2 那道 應 紅(API-8 壞寫法欄的片段 `flatMapMerge` 叫不出且表上沒有);只拿掉〈API 決策點〉裡 `flatMapMerge` 那一列時,S1 應 紅而 S2 應 綠——兩道各自守、不互相掩護 [test:t_kt_catalog_api_decision_points] [test:t_kt_catalog_bad_snippets_reach_rows]
- [S4] 當實驗 repo(型錄明確指到真型錄,不用測試執行器預設的小表)的搜尋 ViewModel 分別用 `flatMapMerge`、`flatMapConcat`、`mapLatest`、`transformLatest` 接查詢輸入、沒有 `debounce`、檔在 `app/src/main/` 底下時,`lumos pitfalls --diff` 應 每種都出情境段且候選列含 D-4 [test:t_kt_situation_api_family_e2e]
- [S5] 當完整自檢模式(`check.py --sg <ast-grep>`)跑真型錄時,〈叫不出的壞寫法〉每個寫 `規則 <id>` 的改由,那條規則 應 報出片段所在的那一行;〈API 決策點〉每個 `決策不問:規則 <id>`,那條規則 應 在壞例樣本含那個名稱的行至少報一行;把其中一段片段在壞例樣本裡改成規則不報的寫法 應 報問題 [test:t_kotlin_rulepack_samples]
- [S6] 當 `python3 configs/ast-grep/kotlin-android/check.py --catalog-only` 跑真型錄時,應 0 個問題,且〈統計〉節的公開名稱數、各歸屬種類筆數、叫不出的壞寫法數、各改由筆數 應 等於重數(擴充既有的統計核對測試) [test:t_kt_catalog_stats_consistent]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 暫存母體加一行 `associate` 宣告、表不動 | 報 `associate` 沒分類 | 依據來源 1.11.0 那列:1.11.0 新增的不重複名稱含 `associate` |
| S1 | 表上 `flatMapMerge` 歸 `D-4`,D-4 觸發字拿掉 `flatMapMerge` | 報 `flatMapMerge` 歸屬搜不到觸發字 | 範圍 1 第一種歸屬 |
| S1 | D-16 觸發字有 `UNLIMITED`,表上 `UNLIMITED` 歸 `無決策` | 報兩邊不同步 | 範圍 2 反向;r1 三席實測 `Channel.UNLIMITED` 會漏 |
| S1 | 名稱 `merge` 標 `撞名 D-59` | 不報 | 範圍 1 第三種歸屬 |
| S2 | API-8 壞寫法片段 `flatMapConcat { search(it) }`,D-4 觸發字沒有 `flatMapConcat`、表上也沒有 | 報 `D-4`、`API-8`、那段片段 | 2026-11-12 實驗:沒加 debounce 時 D-4 不在候選列 |
| S2 | TEST-7 的片段 `[Loading, Success]`,表上沒有 | 報叫不出(測試路徑被篩掉) | r1 正確性席實測:測試路徑在推送前不出情境段 |
| S2 | 〈叫不出的壞寫法〉一列:D-3、API-2、片段 `forEach { it.await() }`、改由「規則 kt-map-await-deferred」 | 報片段不在那條規則的壞例樣本 | r1 三席:那條規則只收 map、檔內註解寫不收 forEach |
| S2 | 改由寫 `範本 T0` | 報 T0 不是行為測試範本 | 範本檔 T0 標題「測試骨架守則」 |
| S3 | D-4 觸發字拿掉 `flatMapMerge`(表不動) | S1 與 S2 都紅 | 範圍 2、3 各自的判法 |
| S4 | 搜尋 ViewModel 用 `mapLatest` 接查詢、沒有 `debounce` | 出情境段,候選列含 D-4 | `mapLatest` 文件:新值來時取消前一個轉換;範圍 5 照此歸 D-4 |
| S6 | 真型錄跑 `--catalog-only` | 0 個問題 | 範圍 5 填完後的狀態 |

## 回退

退回本案的提交:型錄少兩節、自檢少兩道、兩份母體檔消失;本案補的觸發字(含 D-4 的 `mapLatest`、`transformLatest`)跟著退回,情境段回到原本的範圍;D-4 補 `flatMapMerge`、`flatMapConcat` 那一筆是另一個提交,不跟著退。

## 天花板

1. 窮舉的是「哪些寫法帶情境決定」,不是「這次的寫法合不合需求」;需求在程式外,機器只能保證決策點被問到或寫明改由誰抓、答案留痕、判不了交給人。
2. 第一版只窮舉 kotlinx-coroutines-core;androidx 的 lifecycle、work、room、compose 的決策點(例 `ExistingWorkPolicy.REPLACE`、`repeatOnLifecycle`)還是靠反查與手寫觸發字。
3. 自家包裝函式把決策點藏起來(例自寫 `fun <T> Flow<T>.latest()` 內部用 `flatMapLatest`),呼叫端不會被問;包裝函式本身被寫出來的那次會被問。別名匯入(`import kotlinx.coroutines.flow.flatMapMerge as fm`)同理:呼叫處寫 `fm` 不會被問,`import` 行又被切段略過。
4. 帶情境決定、但字面太常見的寫法不當觸發字:母體裡的(`launch`、`collect`)標 `決策不問`;不在母體的(`onClick`)進〈叫不出的壞寫法〉表。兩邊都只能靠形狀規則、行為測試範本或代碼審,改由寫在表上讓人看得到。
5. 壞在「沒寫某樣東西」的寫法(例 D-2 該並行卻串行、迴圈裡 `launch` 沒限流)沒有字面可以觸發,只能進〈叫不出的壞寫法〉表、改由代碼審或範本。
6. 有決策點、但型錄還沒有對應情境列的(例 `runBlocking`、`SupervisorJob`、`CoroutineStart.UNDISPATCHED`),本案先標 `決策不問:代碼審`,不在本案新增情境列。
7. 被問到之後,作者的答案沒有「依據哪條需求」的欄位,盲判也看不到規格;使用者 2026-11-12 定的最終目標:AI 先依計劃的驗收條款或預期值表判斷並引出處,規格沒寫的一律擋下交人裁,人的決定寫回計劃(新條款與預期值表列)並綁一支改壞會紅的行為測試,下次同一段直接引用——形成「被問到 → 依規格判 → 規格沒寫交人 → 寫回規格 → 測試守住」的循環。這件事改的是已上線的表態與盲判,另開後續計劃,本案推送後接著開工,不排日期等。

REVISIT:2026-11-19 確認後續計劃「情境題答案要引規格出處與回寫循環」已開工(本案推送後當天就開;這行是保底)
REVISIT:2027-01-15 把 androidx.lifecycle、androidx.work、androidx.room 的 API 清單也納入 API 母體,並替〈天花板〉6 那批決策點補情境列

## 審計修正紀錄

- r1(2026-11-12,四席 sonnet:通才、正確性、邊界、架構對齊):33 條/blocking 17(通才 7、正確性 4、邊界 6;架構對齊 0)/母體定義被三席同時打穿(成員函式整類不在、`Channel$Factory` 常數被 `$` 規則排掉、雜湊名讓同步檢查漏)、「改由規則」只核編號不核規則真的會報(三席)、反查用假路徑繞過推送前的測試檔篩選(正確性席獨有,實測屬實);全部折入,歸八組根因,逐條去向與先查世界在 r1-intake.md。卷證:governance/review-reports/情境決策點窮舉與壞寫法要叫得出/。
- r1 新增機制前的最小解檢查:①母體改用 klib 清單——最小解是修 JVM 清單的抽法,三席各舉出不同的還原失敗(getter 大小寫、`$Factory`、雜湊、成員),修補要四條特例且仍判不出大小寫;klib 直接是原始碼名稱,特例只剩 JVM 補來源那一小撮。②母體 sha256——最小解是信任「逐位元組放」,但手改母體會讓自檢把殘缺母體當真、全綠;核雜湊一行就擋。③`撞名` 與 `決策不問` 兩種歸屬——不加的話,反向同步會逼 `merge` 歸到不相干的 D-59、`launch` 這類只能謊稱 `無決策`;兩種歸屬都要寫理由並計數。④反查走推送前的路徑篩選——不加就對 `TEST-` 片段給出假的「叫得出」,正是本案要消的默默放行。⑤改由規則實跑——不加就讓一條規則替同一編號下所有片段背書。
