---
type: project
status: todo
created: 2026-11-15
updated: 2026-11-16
tags:
  - type/project
  - status/todo
  - scope/guards-gates
lands_in:
  - Systems/kotlin規則包
  - Systems/規格閘
related:
  - "[[Projects/改動選擇點都要有需求守住_計劃]]"
  - "[[Verification/2026-11-15_改動選擇點真實Android端到端驗收]]"
---
# 選擇點表第二批常見誤用寫法_計劃

## 白話

[[Projects/改動選擇點都要有需求守住_計劃]] 第一版的選擇點表只收論文表 1 的五類運算子加 13 個集合與 Flow 兄弟寫法;在兩個真實 Kotlin 專案量到只有 13–15% 的程式行有選擇點([[Verification/2026-11-15_改動選擇點真實Android端到端驗收]])。使用者 2026-11-15 要「上網搜一下,最容易誤用的情境語法列進來」。這份把網上有公開來源點名「常被誤用、換成兄弟寫法照樣編得過、行為卻不同、單元測試分得出」的 Kotlin/Android 寫法收成第二批列,每列仍是一個語法節點對一組一對一機械壞法,沿用同一套掃描、挑壞法、殺傷力與推送前那一道,不改判定規則。

第二批(候選,設計審定案):
- 空值處理:`$A ?: $B` → `$A!!`(遇到 null 從用預設值變成當掉);`$A?.方法` → `$A!!.方法`(從略過變成當掉)。
- 範圍函式:`.let` → `.also`(回傳值從區塊結果變成接收者本身)。
- Flow 合併:接收者寫法 `a.combine(b) { … }` → `a.zip(b) { … }`(任一邊有新值就輸出 → 兩邊成對才輸出)。頂層寫法 `combine(a, b) { … }` 不收:kotlinx.coroutines 的 `zip` 只有擴充函式、沒有頂層兩參數版本,換識別字必定編不過,要改成接收者寫法又得搬引數(多節點)。
- Compose 副作用與記憶:`LaunchedEffect(<key…>)` 的 key 換成 `Unit`(key 變了不重跑);`remember(<key…>) { … }` 拿掉 key(參數變了還顯示舊值)。

PRIOR-ART: 第一版同一套(論文〈Practical Mutation Testing at Scale〉https://arxiv.org/pdf/2102.11378 2.2 在語法樹上產生、表 1、3.2.1 型別前提事前擋;MutApi 的 API 兄弟改寫表(Wen 等,ICSE 2019,https://doi.org/10.1109/ICSE.2019.00093,全文 https://sqlab-sustech.github.io/files/paper/ICSE2019-mutapi.pdf))。誤用證據:Kotlin null safety 官方頁 https://kotlinlang.org/docs/null-safety.html 與 Detekt `UnsafeCallOnNullableType`(https://detekt.dev/docs/rules/potential-bugs);範圍函式官方頁 https://kotlinlang.org/docs/scope-functions.html;Flow 官方頁 combine 與 zip 段 https://kotlinlang.org/docs/flow.html;Compose 副作用官方頁 https://developer.android.com/develop/ui/compose/side-effects(LaunchedEffect key)與狀態官方頁 https://developer.android.com/develop/ui/compose/state(remember key)。不採:`runCatching` 吞取消(Detekt `SuspendFunSwallowedCancellation` https://detekt.dev/docs/rules/coroutines)——壞的方向是把 try/catch 改寫成 runCatching,跨多個節點、不是一對一壞法,改由情境決策表或 Detekt 規則管;Flow `catch` 換位置——要動兩個節點的順序;頂層 `combine(a, b)` → `zip`——見上;`launch`↔`async`、`groupBy`↔`associateBy`、`MutableStateFlow`↔`MutableSharedFlow`——回傳型別不同多半編不過;`remember`↔`rememberSaveable`、拿掉 `derivedStateOf` 外的 remember——單元測試分不出(論文附錄 A.1.4 同理);`==`→`===`——論文附錄 A.1.23 只換對應的否定。
RETIRE-IF: 上線兩個月後讀 `gov --stats` 選擇點段的「依列號」數字(範圍 5 新增):第二批任一列被回報存活之後的放行裡,理由是「等價」或「不是需求」的超過八成,或那一列的壞法「跑不出結果」超過一半,就把那一列從表裡拿掉(〈回退〉第 1 項)。
REVISIT:2027-01-15 跟第一版的 REVISIT 一起看第二批各列的殺掉率、跑不出結果比例與放行理由,決定留哪幾列、要不要再收 Compose 參數常數

## 舊否決比對

- [[Projects/改動選擇點都要有需求守住_計劃]]〈不做〉「不收數字常數、字串常數、when 分支刪除」:這份不碰,只加 API 與空值兩種節點。
- 同一份〈選擇點表〉的「不收」清單(first/last、collectLatest、Dispatchers.* 等):這份不翻,理由同(單元測試分不出或常掛住)。
- [[Systems/規格閘]] 否決過「處置鍵帶列號或壞法雜湊(型錄一改整批作廢)」:這份只加列、不改 (檔, 行指紋) 的鍵,新增列不會讓舊處置作廢。
- [[Systems/kotlin規則包]] 否決過「選擇點表跟情境決策表合成一張」:這份照舊寫在〈選擇點表〉,每列一對一機械壞法。
- [[Systems/規格閘]] 否決過「剝註解字串的文字比對」:新列照舊用 ast-grep 語法樹規則。
- 論文附錄 A.1.10「跟 null 比較不產生」:這份的空值兩列換的是 `?:` 與 `?.`,不是 `== null`;乾節點規則 A-8 不動。

## 用詞

- **論文**、**選擇點表**、**乾節點規則**、**錨點**、**型別前提**、**跑不出結果**:同 [[Projects/改動選擇點都要有需求守住_計劃]]〈用詞〉。
- **接收者寫法**:`a.combine(b) { … }`,`combine` 出現在 `.` 之後的 navigation_suffix 裡,走第一版的「方法名」錨點。
- **新錨點「安全呼叫符」**:`?.` 那兩個字元所在的位置(navigation_suffix 開頭);壞法只把那兩個字元換成 `!!.`,不動後面的方法名與鏈上其他 `?.`。
- **新錨點「引數」**:ast-grep 規則命中的節點本身就是呼叫的 `value_arguments`(左括號到右括號);錨點行是左括號所在行。壞法直接以樣板文字覆蓋整個節點,或用 `(刪掉)` 刪掉整個節點;不經第一版「不是單一記號就加括號」那一步。
- **新類別 NUL**:null-safety 運算子(`?:`、`?.`)的壞法。不是論文縮寫,也不是 NUL 字元(`\0`)。
- **第二批各列的類別**:`?:`、`?.` 兩列 NUL;`.let`、接收者 `combine`、`LaunchedEffect`、`remember` 四列 API(API 兄弟寫法,錨點分別是方法名、方法名、引數、引數)。

## 範圍

1. **型錄**:`skills/kotlin-idioms/checks-catalog.md`〈選擇點表〉新增第二批六列(列號接 C-32 起),每列欄位與第一版相同,出處欄寫上面 PRIOR-ART 的來源;〈選擇點表〉說明段補「第二批來源與不收理由」,並把說明段裡「錨點只用四種」那句改成六種、列出新錨點;〈統計〉的選擇點表列數同步(check.py 會比對)。
   - `$A ?: $B` 列:錨點「運算元起始」、候選壞法 `$A!!`、型別前提「運算元有 null 字面值」(`$A` 或 `$B` 任一個是 null 字面值就不產生:`null ?: x` 換成 `null!!` 必當、`x ?: null` 的預設值本來就是 null,兩者都不是有意義的壞法)。
   - `?.` 列:錨點「安全呼叫符」、候選壞法 `!!.`、型別前提「(無)」。
   - `.let` 列與接收者 `combine` 列:錨點「方法名」、候選壞法 `also`、`zip`(`zip` 列需補的 import 寫 `kotlinx.coroutines.flow.zip`,沿用第一版「檔頭逐一 import 原寫法才補」)、型別前提「(無)」。
   - `LaunchedEffect` 列:錨點「引數」、候選壞法 `(Unit)`、型別前提「(無)」。
   - `remember` 列:錨點「引數」、候選壞法 `(刪掉)`、型別前提「(無)」。
2. **規則**:`configs/ast-grep/kotlin-choice/rules-choice/` 新增 `nul.yml`(`elvis_expression`;`?.` 的 navigation_suffix)、`compose.yml`(`LaunchedEffect` 呼叫的 value_arguments,引數只有一個而且是 `Unit`、`true`、`false` 字面值時不命中——換成 Unit 是等價壞法;`remember` 呼叫的 value_arguments,只在呼叫帶尾隨 lambda 時命中)、`api.yml` 補 `let`、`combine`(接收者寫法);`samples/` 補每列的命中與不命中樣本(含鏈式另起一行、`?.` 連鎖 `a?.b?.c`、`LaunchedEffect` 多個 key、`LaunchedEffect(Unit)` 不命中、沒有尾隨 lambda 的 `remember(k)` 不命中、頂層 `combine(a, b)` 不命中)。
3. **lumos 產壞法**(只動 scripts/lumos 的選擇點程式,不動型錄讀表):
   - `_choice_anchor` 認新錨點「安全呼叫符」(位移取 navigation_suffix 開頭的 `?.`)與「引數」(位移取節點開頭);「運算元起始」照第一版回節點開頭,不改運算子正規式 `_CHOICE_OP_RE`。
   - `_choice_edits` 加三個分支,放在通用樣板替換之前:錨點「安全呼叫符」→ 只把那兩個位元組換成 `!!.`;錨點「引數」→ 樣板文字直接覆蓋整個節點(`(刪掉)` 照第一版 delete 分支刪整個節點);樣板 `$A!!` → `$A` 不是單一記號時先包成 `($A)` 再接 `!!`,整個替換結果放在運算式裡、優先序需要時再整體加括號(沿用 `_choice_ctx_safe`)。
   - `?.` 列一行只挑一個節點(第一版 `_choice_pick` 每行一個),鏈上其他 `?.` 不動。
4. **check.py**:`CHOICE_CATEGORIES` 尾端加 `NUL`(順序是 lumos 洗牌前的基準,加在尾端不動第一版五類加 API 的相對順序);`CHOICE_ANCHORS` 加「安全呼叫符」「引數」;類別、錨點的白名單只在這裡一份,lumos 讀表經 check.py 的 `choice_tables` 取得,錯了由 check.py 指出列號。新樣本照第一版 `choice_sample_problems` 的 HIT/MISS 核對。
5. **統計**:`gov --stats` 選擇點段加一小節「依列號」:第二批與第一版每一列各自的壞法數、殺掉數、存活數、跑不出結果數,以及被回報存活後的放行理由分布(等價、不是需求、其他)。不加的最小解為什麼不夠:現行選擇點段的跑不出結果依原因文字計、放行依 (列號, 外層宣告) 形狀滿三次才列,RETIRE-IF 要的「某一列的比例」讀不出來,沒有它撤除條件就沒人能判。
6. **文件**:Systems/kotlin規則包 補 WHY 行(第二批來源與不收理由);Systems/規格閘 補選擇點段「依列號」的說明;[[Projects/改動選擇點都要有需求守住_計劃]]〈天花板〉第 1 條補指向這份。

## 不做

- 不收多節點壞法(`runCatching` 改寫、`catch` 換位置、頂層 `combine` 改接收者寫法)、回傳型別不同的互換、單元測試分不出的互換(理由見 PRIOR-ART)。
- 不改一行一個壞法、回報上限、乾節點、殺傷力判定與推送前那一道的規則。
- 不收 Compose 參數常數(`16.dp` 等),等 REVISIT 看數字。

## 實務隱患

- 編不過:`.let`→`.also` 在區塊結果型別跟接收者不同、而外面有用到結果時編不過;`$A ?: $B`→`$A!!` 在 `$A` 不是可空型別時編譯器只警告不報錯(行為不變,等價存活)。語法樹沒有型別,這兩列除了「運算元有 null 字面值」之外不設型別前提(近似條件判不準,寧可讓它跑);編不過的落成跑不出結果、人可判不適用,範圍 5 依列號累計,跑不出結果超過一半照 RETIRE-IF 拿掉那一列。
- 等價存活:`$A!!` 在 `$A` 實際不會是 null 的地方是等價;`LaunchedEffect` 的 key 本來就是常數時規則不命中(範圍 2),其餘靠回報上限與放行理由「等價」承接,RETIRE-IF 看比例。
- 換壞法:含第二批語法的既有改動行,類別變多後洗牌結果可能挑到別的壞法;處置鍵是 (檔, 行指紋),已記的殺掉照算,只有之後重跑時壞法可能不同。只含第一版語法的行挑法不變(S7)。
- Compose 測試成本:`LaunchedEffect`、`remember` 列要 Compose UI 測試(`createComposeRule`)才分得出,單元測試平台 `kotlin-junit` 跑不到時那幾行只能人驗或放行;推送前那一道碰到沒有可守測試時照第一版只提醒不擋。
- 掃描量:新規則讓有選擇點的行變多,推送前時限照第一版(`_KT_SIT_BUDGET`、`_CHOICE_PICK_BUDGET`);實作時在兩個真實專案重量一次掃描耗時。
- 併發與交易:已排除:沿用第一版,單人單機依序操作。
- 已排除:金流:只改型錄、規則與產壞法的程式,不碰付款或金額計算
- 已排除:對外送出:掃描與殺傷力都在本機跑,不對外送任何資料
- 已排除:不可逆:治理帳照舊逐筆追加,拿掉第二批列即回到第一版行為
- 守衛面:不排除——新錨點與新類別會改推送前選擇點那一道挑出的壞法,所以走設計審;S7 守住只含第一版語法的行挑選結果不變。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 一對一機械壞法、在語法樹上產生、型別前提事前擋 | 論文 2.2、表 1、3.2.1 | https://arxiv.org/pdf/2102.11378 |
| API 兄弟寫法寫成改寫表 | MutApi | https://sqlab-sustech.github.io/files/paper/ICSE2019-mutapi.pdf |
| `?:` 與 `!!`、`?.` 的語意 | Kotlin 官方 null safety | https://kotlinlang.org/docs/null-safety.html |
| `!!` 是常見誤用 | Detekt UnsafeCallOnNullableType | https://detekt.dev/docs/rules/potential-bugs |
| `let` 與 `also` 回傳值不同 | Kotlin 官方範圍函式 | https://kotlinlang.org/docs/scope-functions.html |
| `combine` 與 `zip` 的輸出時機;`zip` 只有擴充函式 | Kotlin 官方 Flow | https://kotlinlang.org/docs/flow.html |
| `LaunchedEffect` key 決定重跑 | Android 官方 Compose 副作用 | https://developer.android.com/develop/ui/compose/side-effects |
| `remember` key 決定重算 | Android 官方 Compose 狀態 | https://developer.android.com/develop/ui/compose/state |
| 不收 runCatching(多節點) | Detekt SuspendFunSwallowedCancellation | https://detekt.dev/docs/rules/coroutines |
| 收這批寫法 | 使用者方向 | 使用者 2026-11-15:「或是把上網搜一下,最容易誤用的情境語法列進來」;「開」 |

## 驗收條款

- [S1] 當改動行有 `$A ?: $B`,choice-points 應 挑出 NUL 類壞法 `$A!!`;`$A` 不是單一記號時 應 寫成 `($A)!!`;`$A` 或 `$B` 是 null 字面值時 應 不產生 [test:t_choice_points_nul_elvis]
- [S2] 當改動行有 `a?.b?.c` 鏈,choice-points 應 只把挑中的那一個 `?.` 換成 `!!.`、其餘不動 [test:t_choice_points_nul_safecall]
- [S3] 當改動行有 `.let {` 與接收者寫法 `.combine(`,choice-points 應 照方法名錨點換成 `also`、`zip`,`zip` 照第一版補 import;頂層 `combine(a, b) {` 應 不產生 [test:t_choice_points_batch2_api]
- [S4] 當改動行有 `LaunchedEffect(k1, k2) {`,choice-points 應 把引數清單換成 `(Unit)`(不多包括號);`LaunchedEffect(Unit) {` 應 不產生;`remember(k) {` 應 刪掉引數清單;沒有尾隨 lambda 的 `remember(k)` 應 不產生 [test:t_choice_points_compose]
- [S5] 當型錄有 NUL 類別、安全呼叫符或引數錨點的列,check.py 應 認得;類別或錨點寫錯 應 擋並指出哪一列,lumos 讀表經 check.py 印出同一個問題 [test:t_choice_table_batch2]
- [S6] 當第二批樣本檔跑過選擇點樣本核對,每條第二批規則 應 命中該命中的、不命中不該命中的 [test:t_choice_samples_batch2]
- [S7] 當第二批列加入後,只含第一版語法的既有樣本行 應 挑出跟加入前相同的壞法(行指紋相同、壞法相同) [test:t_choice_points_batch2_stable]
- [S8] 當帳上有第二批與第一版列的選擇點事件,`gov --stats` 選擇點段 應 依列號印出每列的壞法數、殺掉數、存活數、跑不出結果數與放行理由分布 [test:t_gov_stats_choice_by_row]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `val n = name ?: "guest"` 改動行 | 壞法 `val n = name!!` | Kotlin null safety 官方頁;論文表 1 形狀 |
| S1 | `f(a + b ?: c)` | 壞法 `f((a + b)!!)`(`?:` 優先序低於 `+`,`$A` 是 `a + b`) | Kotlin 官方文法運算子優先序 |
| S1 | `x ?: null` 與 `null ?: x` | 都不產生(運算元有 null 字面值) | 論文 3.2.1(無意義或必當) |
| S2 | `user?.profile?.name` 挑中第一個 `?.` | `user!!.profile?.name` | 一行一個壞法(論文 4.1) |
| S3 | `.let { it + 1 }` | `.also { it + 1 }` | 範圍函式官方頁 |
| S3 | `a.combine(b) { x, y -> x + y }`,檔頭有 `import kotlinx.coroutines.flow.combine` | `a.zip(b) { x, y -> x + y }`,檔頭補 `import kotlinx.coroutines.flow.zip` | Flow 官方頁;第一版 API 列補 import 做法 |
| S3 | 頂層 `combine(a, b) { x, y -> x + y }` | 不產生 | `zip` 只有擴充函式(Flow 官方頁) |
| S4 | `LaunchedEffect(userId) { load(userId) }` | `LaunchedEffect(Unit) { load(userId) }` | Compose 副作用官方頁 |
| S4 | `LaunchedEffect(Unit) { load() }` | 不產生 | 等價壞法(Compose 副作用官方頁) |
| S4 | `remember(items) { items.sorted() }` | `remember { items.sorted() }` | Compose 狀態官方頁 |
| S4 | `remember(items)` 沒有尾隨 lambda | 不產生 | 刪了編不過(論文 3.2.1) |
| S5 | 型錄某列類別欄寫成 `NULL`(不是 `NUL`) | check.py 擋,訊息指出那一列的列號;lumos 讀表印同一句 | 第一版〈選擇點表〉讀表擋法 |
| S5 | 型錄某列錨點欄寫「安全呼叫符」 | 認得、不擋 | 本計劃〈用詞〉新錨點 |
| S6 | `samples/` 第二批每條規則的命中與不命中樣本 | 命中行全中、不命中行零命中 | 第一版選擇點樣本核對做法 |
| S7 | 第一版既有樣本裡不含 `?:`、`?.`、`let`、`combine`、`LaunchedEffect`、`remember` 的行,加入第二批列前後各跑一次 choice-points | 每行的行指紋與挑出的壞法相同 | 論文 4.1 每行一個壞法、挑選要穩定 |
| S8 | 帳上 C-32 列 4 個壞法:1 殺掉、2 存活(放行理由各一筆「等價」「不是需求」)、1 跑不出結果 | 「依列號」那一列印 壞法 4、殺掉 1、存活 2、跑不出結果 1、放行 等價 1 不是需求 1 | 本計劃 RETIRE-IF |

## 回退

1. 單列誤報或跑不出結果多:從〈選擇點表〉拿掉那一列(下一次推送就不再算;舊帳以行為單位照算)。
2. 整批撤掉:拿掉 C-32 起的列與新規則檔;新錨點、NUL 類別與「依列號」統計的程式碼留著不影響第一版。

## 天花板

1. 只收網上有公開來源點名的少數寫法;沒列到的誤用照樣不管(同第一版天花板 1)。
2. 語法樹沒有型別:`let`→`also`、`$A!!` 的型別前提只能近似,編不過的落成跑不出結果要人放行。
3. Compose 兩列在只有單元測試平台的專案多半沒有可守的測試,只提醒、靠人驗。
4. 誤用證據來自官方文件與規則頁的說明,沒有頻率統計;「最容易誤用」是依來源強度排的,不是量出來的。
