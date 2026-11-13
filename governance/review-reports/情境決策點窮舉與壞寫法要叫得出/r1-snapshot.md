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

> 白話:推送前的情境題(型錄〈情境決策表〉每列一個情境,改動命中觸發字就要表態、再由盲判代理獨立判一次)只在「被問到」時守得住;沒被問到就整段默默放行。2026-11-12 實驗發現搜尋框改用 `flatMapMerge`、`flatMapConcat` 時,「只要最新一次」那一列根本不會被問(觸發字只收好寫法的字,`flatMapLatest`、`debounce`),已先補了那一列。接著全表掃描:180 段對應檢查列的壞寫法片段,有 91 段單獨出現時叫不出它對應的情境列。這份計劃讓「沒被問到」不能再默默發生,從兩個方向圍:①**從函式庫窮舉**:協程核心函式庫的公開 API 清單是有限的、官方逐版發布,把每個公開名稱分類成「選了它就等於做了情境決定(歸到某一列,且一定是那列的觸發字)」或「不帶情境決定(寫理由)」,升版多出來的名稱沒分類就紅;②**從型錄的壞寫法反查**:每段壞寫法片段要嘛單獨就叫得出對應列,要嘛明寫改由哪裡抓(會擋的規則、行為測試範本、代碼審)。使用者原話(2026-11-12):「雖然他是需要確認情境的規則,但有時候規則往往沒辦法在第一時間確認清楚,這時候,如果放行AI寫出這樣的語法,就會出問題而沒發現」「我是想避免這種情況出現」「我相信Kotlin的語法絕對窮舉得出來,各種語法對應當下情境是不是符合功能需求,或是功能需求定義不清需要進一步釐清語法有沒有適用,是做得到的對嗎」。

PRIOR-ART: ①窮舉來源:kotlinx.coroutines 用 Kotlin 官方的二進位相容檢查工具(binary-compatibility-validator,https://github.com/Kotlin/binary-compatibility-validator )把每一版的公開 API 存成 `.api` 檔放在 repo 裡(例:https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.api ),新版多了或少了什麼可以直接比對;2026-11-12 比對 1.10.2 與 1.11.0 兩版的 `.api`,1.11.0 多了 `associate` 等 17 個函式,升版會被點到。採用「釘一版 `.api` 當窮舉母體」。不選:從語料統計常見寫法(窮舉不完、新寫法沒出現過就漏)。②強迫分類的形狀:Kotlin 對 sealed 類別的 `when` 要求窮舉每個分支、漏了編譯失敗(https://kotlinlang.org/docs/sealed-classes.html#use-sealed-classes-with-when-expression ),本案照這個形狀——母體裡每個名稱一定要被歸類,沒歸類就是錯,不是預設不管。③反查樣本:沿用型錄既有的證據樣式正反例自測(ast-grep 規則測試的 valid/invalid,https://ast-grep.github.io/guide/test-rule.html ),本案把「反例要切得出含那一列的段」從手寫樣本擴大到型錄壞寫法欄的每段片段。④常用字門檻沿用 [[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 實驗 E9:Now in Android 310 支 kt 檔的文件頻率超過 8% 的字不當觸發字。
RETIRE-IF: 上線八週後用 `lumos gov --stats` 看:本案新加的觸發字所切出的情境段,盲判判「不適用」超過八成 → 那些字太寬,收窄或改歸「不帶情境決定」;〈叫不出的壞寫法〉節超過一半寫「代碼審」而且漏網帳(`lumos loop escape --list`)八週內沒有一筆落在這些列 → 反查那一半降成只在新增列時要求;協程函式庫連兩次升版都沒有新增需要歸到情境列的名稱 → 窮舉改成只在升版時跑。

## 用詞

- **情境列**:型錄〈情境決策表〉的一列(`D-n`),有情境、標準寫法、不適用時、觸發字、證據樣式、對應檢查。
- **被問到**:改動的增行經 scripts/lumos 的情境段切法(`_kt_sit_text_segments` 這一族,剝掉註解與字串、比對觸發字)切出一段、那段的候選列含這一列。被問到之後的路既有、本案不改:情境題只收「適不適用、照哪個寫法」,不收 na 或 todo;缺段、缺列、答案形狀不對、缺第一盲判、作者與第一盲判不一致又沒有仲裁,都擋;證據樣式對不上、仲裁多數判作者沒照做只提醒不擋;判不了的出口是段放行,人或 AI 都能下,AI 下的記成 AI 放行、在 doctor 與推送前小結列到有人確認為止([[Projects/Android寫法語意情境表態與盲判_計劃]])。所以「需求一時說不清」的情況,只要被問到,就不會沒留痕地過。
- **型錄主表列編號**:型錄主表一列一種寫法,編號是主題前綴加數字(例 `API-8`、`FLOW-22`);情境列的「對應檢查」欄就是這種編號。
- **會擋的規則**:規則包 `configs/ast-grep/kotlin-android/rules/` 目錄底下的規則(推送前新增告警閘照範本宣告的那份);同層的 `rules-review/`、`rules-hints/`、`rules-unwired/` 都不擋。規則訊息開頭一律是 `[型錄主表列編號]`。
- **通電批次欄、範本 T<n>**:型錄主表第 10 欄,記每種接電方式在哪一批生效;其中「行為測試或正向約束=範本 T<n>」指 `skills/kotlin-idioms/test-templates.md` 的第 n 組行為測試範本(要有人照範本寫測試才守得住,不會自動跑)。
- **停用列、停用字表**:兩件事。停用列是型錄標了「(停用)」的列,觸發字與證據樣式都是(無)、不出題;停用字表是 `check.py` 的 `STOP_TRIGGERS`,列「太常見、不准當觸發字」的字。
- **段放行**:情境題判不了時的出口,`lumos lint-waive kt-situation:<段身分>`,記誰放行、理由。
- **代碼審**:分支推送前派審查代理讀改動的迴圈([[Systems/pitfalls-code-loop]]),靠代理讀,不是機械檢查。
- **API 母體**:釘版的協程核心函式庫公開 API 清單,檔 `configs/ast-grep/kotlin-android/api/kotlinx-coroutines-core-1.10.2.api`(新增)(照官方該版標籤的原檔逐位元組放;版本跟行為測試範本用的 1.10.2 一致)。
- **公開名稱**:從 API 母體抽出的名稱,三種:①頂層與擴充函式(`…Kt` 門面類別裡的 `public static final fun`,例 `flatMapMerge`);②公開類別與介面的簡名(例 `Mutex`);③列舉值與物件常數,寫成 `外層類別.名稱`,兩種來源:公開類別裡大寫開頭的 `public static final field`(例 `BufferOverflow.DROP_OLDEST`);公開 object(有 `INSTANCE` 欄位的類別,例 `Dispatchers`)或伴生物件(類別名以 `$Companion` 結尾,例 `SharingStarted$Companion`)裡不帶參數、沒標 `synthetic` 的 `get<大寫開頭>` 讀取函式,去掉 `get` 與 `$Companion` 還原成屬性名(`getIO` → `Dispatchers.IO`、`getLazily` → `SharingStarted.Lazily`)。都排除:套件路徑含 `internal` 的、還原之後名稱仍含 `$` 的、標 `synthetic` 的(隱藏的舊版相容入口)、`access$` 開頭的。`.api` 檔是編譯後的 JVM 形狀:`…Kt` 是 Kotlin 把頂層函式放進的門面類別,`synthetic` 是編譯器產生、原始碼呼叫不到的入口。抽法只有型錄自檢 `check.py` 一處(`api_names`,新增)。
- **決策點**:選了它就等於做了某個情境決定的公開名稱(例:`flatMapMerge` 等於選了「新值來了舊的不取消、並行跑」)。
- **壞寫法片段**:情境列「對應檢查」欄每個編號,在型錄主表那一列「壞寫法形狀」欄裡每一段反引號包住的文字(表格裡的 `\|` 還原成 `|`),不做長度或字元過濾——過濾本身就是不出聲的漏洞。
- **叫得出**:片段單獨包成 `class X {` / `fun f() {` / 片段 / `}` / `}` 當整支新增,經情境段切法切出的段的候選列含那一列。

## 範圍

1. **API 決策點節**:型錄在〈情境決策表〉之後新增〈API 決策點〉節。第一行固定 `母體:kotlinx-coroutines-core 1.10.2,<官方 .api 檔網址>`;接一張表「名稱 | 歸屬 | 理由」,公開名稱每個恰好一列:
   - 歸屬是一到多個 `D-n`(以「、」分隔),或 `無決策`。
   - 歸到 `D-n` 時,那一列至少有一個觸發字,經 `_kt_trigger_re` 編成的正規式在名稱字串裡搜得到(方向固定是「觸發字的正規式搜名稱」,跟推送前拿觸發字搜程式碼同方向;反過來用名稱搜觸發字,`launch` 會被觸發字 `viewModelScope.launch` 算成命中,但程式裡單寫 `scope.launch` 根本不會被問)。觸發字帶點的(`SharingStarted.Lazily`)照樣比。
   - `無決策` 的理由一句,寫它為什麼不代表情境選擇(例:`emptyFlow` 只是建空流)。
   - 理由不得空白。
2. **API 決策點自檢**(`check.py` 的 `api_decision_problems`,新增,接進 `catalog_problems`。推送前閘與 CI 不直接跑 `check.py`,是跑型錄測試(`t_kt_catalog_*` 這一族直接呼叫 `catalog_problems`);型錄在 `skills/` 底下,推送前閘不會把它的改動判成純文件,一定跑到這些測試;人手動跑用 `--catalog-only`):
   - 母體裡有、表上沒有的名稱 → 問題(升版多出來的名稱一定被點到)。
   - 表上有、母體裡沒有的名稱 → 問題(升版拿掉或打錯)。
   - 同一個名稱出現兩列 → 問題。
   - 歸到 `D-n` 但那列觸發字命中不到它、或那列是停用列 → 問題。
   - 反向:某列的觸發字整字等於某個公開名稱,但表上那個名稱沒有歸到這一列 → 問題(兩邊不同步)。
3. **叫不出的壞寫法節與自檢**:型錄〈API 決策點〉之後新增〈叫不出的壞寫法〉節,表「列編號 | 對應檢查 | 片段 | 改由 | 理由」;`check.py` 的 `bad_snippet_reach_problems`(新增,接進 `catalog_problems`):
   - 叫不出、表上又沒有 → 問題,訊息印列編號、對應檢查與片段。
   - 表上有、但現在叫得出 → 問題(過期,補了觸發字就要刪這一列)。
   - 表上有、但型錄壞寫法欄已經沒有這段片段 → 問題。
   - 改由只收四種:`規則 <id>`(那條規則要在會擋的 `rules/` 目錄、訊息開頭引的型錄編號等於這列的對應檢查);`範本 T<n>`(要等於那個對應檢查列通電批次欄「行為測試或正向約束=」的值);`代碼審`;`不是寫法`(片段不是一段程式寫法,例 `[Loading, Success]`、`delay(常數)`)。其他值、或理由空白 → 問題。
4. **填資料**:
   - API 母體的公開名稱逐一分類。歸到某列的,那列觸發字沒有就補;補之前查 `STOP_TRIGGERS` 停用字表與 Now in Android 文件頻率(同 E9 的量法,超過 8% 不補,改寫 `無決策` 並在理由寫「頻率 x%,當觸發字會到處亮,改由 <哪裡>」)。
   - 91 段叫不出的壞寫法逐條處理:有專一字面特徵、頻率在門檻內的補觸發字(讓它叫得出);否則寫進〈叫不出的壞寫法〉節。
   - 每補一個觸發字,那列證據樣式自測照跑(`--catalog-only` 到 0 個問題);新增的觸發字不另寫情境樣本(叫得出由範圍 3 的反查證明)。
5. **規則包筆記與型錄說明**:型錄開頭〈輸入與口徑〉補兩節的欄位定義;[[Systems/kotlin規則包]] 補兩條 WHY 與 API 母體檔的家(about_code 加那支 `.api`)。

**不做**:不改情境題、表態、盲判、段放行的判定(被問到之後的路既有);不在推送前閘呼叫模型;不判「寫法符不符合需求」本身(那要需求,程式裡沒有,見〈天花板〉1);第一版只窮舉協程核心函式庫。

## 實務隱患

- **觸發字變多,情境段跟著變多**:每段每個候選列都要表態與盲判,成本上升。擋法:補字前量頻率(8% 門檻);RETIRE-IF 第一條看盲判「不適用」比例。
- **母體抽法跟著格式漂**:`.api` 是工具產生的文字格式,未來版本格式改了,抽法可能抽少。擋法:自檢另驗抽出的三種名稱數量都大於 0、而且已知的錨點名稱(`flatMapLatest`、`Mutex`、`SharingStarted.Lazily`)都在。
- **「代碼審」變成新的垃圾桶**:寫「代碼審」不用證明什麼。擋法:RETIRE-IF 第二條看比例;統計節(型錄〈統計〉)多列四種改由的筆數,由 `stats_problems` 核。
- **片段包裝方式影響叫不叫得出**:片段本身是類別宣告或註記時,包進函式裡不合法 Kotlin,但切段不編譯,這部分不影響。會影響的是剝註解與字串:它是逐字元的詞法掃描,片段裡有落單的引號、`/*` 或反引號時,後面的包裝與片段後半會被當成字串或註解剝掉,觸發字可能因此不中。處理:這種片段照樣判,判不中就進〈叫不出的壞寫法〉表、改由寫 `不是寫法` 或其他三種,理由寫明「片段有落單的引號」——跟真的程式碼被剝掉的結果一致,不另做特例。
- **舊否決對照(2026-11-12 跑 `lumos rejections`,533 筆,按概念比對)**:[[Systems/kotlin規則包]] 記過否決「樣本逐行比對壞寫法欄」當接電判定(三包 30 多列被擋錯)——那是拿壞寫法欄判「哪條 lint 擋得到」,字面跟真跑結果對不上;本案拿壞寫法片段只判「會不會被問」,用的是推送前真正跑的同一套切段程式,判的就是它自己,不衝突。[[Systems/棧別提問表態閘]] 記測試執行器預設把型錄指到觸發字永遠不中的小表,S4 的端到端測試要明確指到真型錄。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:只在本機讀型錄與 `.api` 檔
- 已排除:不可逆:型錄兩節與自檢函式,退提交即回原狀
- 守衛面:改型錄自檢、會讓推送前的規則包自檢擋人,屬守衛面,走完整設計審(不寫成已排除)

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 協程函式庫逐版公開 API 清單可當窮舉母體 | binary-compatibility-validator 說明(產生並比對 `.api` 檔) | https://github.com/Kotlin/binary-compatibility-validator |
| 1.10.2 版母體原檔 | kotlinx.coroutines 1.10.2 標籤的 `.api` 檔 | https://github.com/Kotlin/kotlinx.coroutines/blob/1.10.2/kotlinx-coroutines-core/api/kotlinx-coroutines-core.api |
| 升版會多出名稱(S1 案例) | kotlinx.coroutines 1.11.0 標籤的 `.api` 檔(2026-11-12 比對多 `associate` 等 17 個函式) | https://github.com/Kotlin/kotlinx.coroutines/blob/1.11.0/kotlinx-coroutines-core/api/kotlinx-coroutines-core.api |
| 每個值都要被分類、漏了就錯 | Kotlin sealed 類別配 `when` 的窮舉要求 | https://kotlinlang.org/docs/sealed-classes.html#use-sealed-classes-with-when-expression |
| `mapLatest`、`transformLatest` 跟 `flatMapLatest` 同屬「新值來就取消舊的」 | kotlinx.coroutines `mapLatest` 文件 | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/map-latest.html |
| 規則要有正反例樣本自測 | ast-grep 規則測試(valid/invalid) | https://ast-grep.github.io/guide/test-rule.html |

全表掃描的原始結果(91 段叫不出的片段與分類用的頻率、規則、範本資料)在實作時存進卷證 `governance/review-reports/情境決策點窮舉與壞寫法要叫得出/sweep/`(新增)。

## 驗收條款

- [S1] 當型錄〈API 決策點〉表跟 API 母體一一對上、歸屬都命中觸發字時,`api_decision_problems` 應 回空;母體多一個名稱(用 1.11.0 版多出的 `associate` 當案例)應 報那個名稱;表上多一個母體沒有的名稱 應 報;同一名稱兩列 應 報;歸到 `D-4` 但 D-4 觸發字拿掉 `flatMapMerge` 應 報;D-4 觸發字有 `flatMapMerge` 而表上 `flatMapMerge` 歸 `無決策` 應 報;歸到停用列 應 報;理由空白 應 報;母體抽不到錨點名稱 應 報;真型錄 應 回空 [test:t_kt_catalog_api_decision_points]
- [S2] 當型錄壞寫法片段單獨包成一支檔時,叫不出對應情境列而〈叫不出的壞寫法〉沒有那一列 應 報列編號、對應檢查與片段;表上有但現在叫得出 應 報過期;表上的片段在壞寫法欄找不到 應 報;改由寫 `規則 <id>` 而那條規則不在會擋目錄或訊息引的編號不同 應 報;寫 `範本 T<n>` 而跟通電批次的值不同 應 報;改由是四種以外的值或理由空白 應 報;片段含表格跳脫的 `\|` 應 還原後再比;真型錄 應 回空 [test:t_kt_catalog_bad_snippets_reach_rows]
- [S3] 當 D-4 觸發字拿掉 `flatMapMerge` 時,S1 那道 應 紅(歸屬命中不到),S2 那道 應 紅(API-8 的壞寫法片段叫不出且表上沒有);只拿掉〈API 決策點〉裡 `flatMapMerge` 那一列時,S1 應 紅而 S2 應 綠——兩道各自守、不互相掩護 [test:t_kt_catalog_api_decision_points]
- [S4] 當實驗 repo 的搜尋 ViewModel 分別用 `flatMapMerge`、`flatMapConcat`、`mapLatest`、`transformLatest` 接查詢輸入、沒有 `debounce` 時,`lumos pitfalls --diff` 應 每種都出情境段且候選列含 D-4 [test:t_kt_situation_api_family_e2e]
- [S5] 當 `python3 configs/ast-grep/kotlin-android/check.py --catalog-only` 跑真型錄時,應 0 個問題,且〈統計〉節的公開名稱數、各歸屬筆數、叫不出的壞寫法各種改由的筆數 應 等於重數(擴充既有的統計核對測試) [test:t_kt_catalog_stats_consistent]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 母體換成 1.11.0 版 `.api`、表照 1.10.2 填 | 報 `associate` 等新名稱沒分類 | 依據來源 1.11.0 那列:2026-11-12 比對 1.10.2 多 17 個函式 |
| S1 | 表上 `flatMapMerge` 歸 `D-4`,D-4 觸發字拿掉 `flatMapMerge` | 報 `flatMapMerge` 歸屬命中不到觸發字 | 範圍 2 第四點 |
| S1 | D-4 觸發字有 `flatMapMerge`,表上 `flatMapMerge` 歸 `無決策` | 報兩邊不同步 | 範圍 2 第五點(反向) |
| S2 | API-8 壞寫法片段 `flatMapConcat { search(it) }`,D-4 觸發字沒有 `flatMapConcat`、表上也沒有 | 報 `D-4`、`API-8`、那段片段 | 2026-11-12 實驗:沒加 debounce 時 D-4 不在候選列 |
| S2 | 〈叫不出的壞寫法〉有一列:D-3、API-2、片段 `.map { it.await() }`、改由「規則 kt-map-await-deferred」 | 不報(那條規則在會擋的 `rules/api.yml`、訊息引 `API-2`) | 2026-11-12 分類資料:kt-map-await-deferred 掛 API-2 |
| S2 | 表上寫 `範本 T9`,對應檢查列通電批次寫「範本 T2」 | 報範本不一致 | 範圍 3 改由第二種 |
| S3 | D-4 觸發字拿掉 `flatMapMerge`(表不動) | S1 與 S2 都紅 | 範圍 2、3 各自的判法 |
| S4 | 搜尋 ViewModel 用 `mapLatest` 接查詢、沒有 `debounce` | 出情境段,候選列含 D-4 | `mapLatest` 文件:新值來時取消前一個轉換;範圍 4 照此歸 D-4 |
| S5 | 真型錄跑 `--catalog-only` | 0 個問題 | 範圍 4 填完後的狀態 |

## 回退

退回本案的提交:型錄少兩節、自檢少兩道、API 母體檔消失;本案補的觸發字跟著退回,情境段回到原本的範圍;D-4 補 `flatMapMerge`、`flatMapConcat` 那一筆是另一個提交,不跟著退。

## 天花板

1. 窮舉的是「哪些寫法帶情境決定」,不是「這次的寫法合不合需求」;需求在程式外,機器只能保證決策點一定被問到、答案留痕、判不了交給人。
2. 第一版只窮舉 kotlinx-coroutines-core;androidx 的 lifecycle、work、room、compose 的決策點(例 `ExistingWorkPolicy.REPLACE`、`repeatOnLifecycle`)還是靠反查與手寫觸發字。
3. 自家包裝函式把決策點藏起來(例自寫 `fun <T> Flow<T>.latest()` 內部用 `flatMapLatest`),呼叫端不會被問;包裝函式本身被寫出來的那次會被問。
4. 帶情境決定、但字面太常見的寫法(`launch`、`collect`、`onClick`)不當觸發字,只能靠形狀規則、行為測試範本或代碼審,寫在〈叫不出的壞寫法〉節裡讓人看得到。

5. 被問到之後,作者的答案沒有「依據哪條需求」的欄位,盲判也看不到規格;使用者 2026-11-12 定的最終目標是:AI 先依計劃的驗收條款或預期值表判斷並引出處,規格沒寫的一律擋下交人裁,有依據的留給人事後複核。這件事改的是已上線的表態與盲判,另開後續計劃,本案不做。

REVISIT:2026-12-15 開後續計劃「情境題答案要引規格出處」:答案加依據欄(計劃條款或「規格沒寫」)、規格沒寫就擋、盲判材料附相關規格;先查分支跟計劃有沒有可靠對應
REVISIT:2027-01-15 把 androidx.lifecycle、androidx.work、androidx.room 的 `.api` 檔也納入 API 母體(第一版只有協程核心)

## 審計修正紀錄
