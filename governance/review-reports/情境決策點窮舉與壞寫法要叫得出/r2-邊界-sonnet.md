severity: major

我讀了 r2-snapshot.md 全文,也實跑了 `scripts/lumos`、`check.py`、1.10.2 與 1.11.0 兩版的 `.klib.api` 和 `.api`,以及 Now in Android 本機複本(310 支)。本機沒有 ast-grep,涉及 `--sg` 實跑的部分是讀程式推論,不是跑出來的。

## Findings

### F1 JVM 補來源的抽法不完整,照字面做會產出不存在或內部的名稱
severity: major
blocking: 是。母體是整案的地基,兩個人照字面實作會得到不同的名稱集合,而雜湊釘死的母體與自檢錨點都建在這個抽法上。
- 位置:〈用詞〉「公開名稱」補來源 JVM 清單那條。
- 問題:規則沒講清楚的地方,照字面實作會讓假名稱進表。
- 引句:「不帶參數的 `getX`/`isX` 讀取函式還原成屬性名」
- 佐證:照字面實作 1.10.2 `.api` 後,klib 沒有的名稱有 65 個,至少 20 個是假的或內部的。
  - 真的函式被當成屬性還原:`getCompleted`、`getResult`、`getStackTraceElement`、`getCompletionExceptionOrNull`、`getChildJobCancellationCause` 在 klib 裡是函式,還原後多出 `completed`、`result`、`stackTraceElement` 等不存在的屬性名。
  - 大小寫退化:`getRECOVER_STACK_TRACES` 照「klib 都沒有才以首字小寫收」變成 `rECOVER_STACK_TRACES`。
  - 值類別的名稱後綴:`constructor-impl` 變 `constructor`,`box-impl`、`unbox-impl` 變 `box`、`unbox`,`equals-impl0` 原樣留著(規則只去掉 `-impl`)。
  - 編譯器改過的名稱:`isInstalled$kotlinx_coroutines_debug`(名稱本身含 `$`)、`_state`、`_lastObservedFrame`、`INSTANCE`,另有 `flowCombine`、`debounceDuration`(`@JvmName` 改名,原始碼沒人寫)。
  - 套件排除只寫給 klib:「套件路徑含 `internal` 的不收」沒套用到 JVM 補來源。`kotlinx/coroutines/debug/internal/` 的 17 個名稱混進來(`lastObservedThread`、`sequenceNumber`、`dumpCoroutinesInfo` 等)。
  - 反例:klib 自己也有非原始碼名稱。
- 引句:「宣告照原始碼的名字寫」
- 佐證:klib 檔第 935、938 行是 `Job0`、`SupervisorJob0`(`@JsName` 改名),原始碼寫的是 `Job()`。
- 建議:JVM 補來源明列三件事,並放進 S1 的案例。
  - 套用 `internal` 排除。
  - 只還原 JVM 清單裡 `getX` 後面沒有同名函式的讀取函式。
  - 有 `$`、`-impl0`、`INSTANCE`、底線開頭的一律丟掉。

### F2 〈API 決策點〉的「改由」沒有對應檢查可比,證明力只剩子字串
severity: major
blocking: 是。r1 已經因為「只核規則編號」判過 major,這裡是同一類洞換成名稱版,而且規則編號的比對根本做不出來。
- 位置:〈用詞〉「改由」的 `規則`、`範本` 兩條,加上範圍 4 的 `route_rule_hits_problems`。
- 問題一:規則與範本的核對都需要「對應檢查」,但〈API 決策點〉表只有「名稱 | 歸屬 | 理由」三欄,名稱沒有對應檢查。
- 引句:「訊息開頭引的編號等於對應檢查」
- 佐證:`決策不問:規則 kt-x` 時,規則訊息的 `[API-n]` 要跟什麼比,spec 沒寫。`範本 T<n>` 要「等於對應檢查列通電批次欄的值」,也沒有對應檢查列可查。照字面只剩「名稱出現在樣本裡」。
- 問題二:剩下的證明太弱。
- 引句:「壞例樣本裡含這個名稱的行至少一行被報」
- 佐證:`samples/bad/kt-map-await-deferred/.../kt-map-await-deferred.kt` 第 4 行 `ids.map { async { api.get(it) } }.map { it.await() }  // BAD` 含 `async`,規則 pattern 會報這一行。所以 `async`(停用字)標 `決策不問:規則 kt-map-await-deferred` 會過。但這條規則抓的是 map 配 await,跟 async 的決策無關。短名稱如 `all`、`any`、`first`、`map` 更糟,用子字串比對幾乎任何報告行都含。
- 範本那邊同理:「那一組任一個壞寫法小節的程式碼含這個名稱」,T1 到 T3 的程式碼本來就大量用到 `withTimeout`、`launch` 之類的名稱。
- 建議:二選一。
  - 〈API 決策點〉改由補一欄「對應檢查」,沿用〈用詞〉的核對。
  - 名稱比對至少用整字界(`_kt_trigger_re` 同一套),並要求被報的行裡這個名稱是被規則比中的節點。

### F3 歸屬四種互斥,同一個名稱被多列觸發字搜到時說不出實情
severity: major
blocking: 是。現有型錄就有這種名稱,作者只能二選一說謊,而且說謊都過得了自檢。
- 位置:範圍 1 的四種歸屬,加上範圍 2 的反向同步。
- 引句:「那一列的觸發字搜得到這個名稱,但意思不同」
- 引句:「公開名稱每個恰好一列」
- 佐證:拿真型錄的觸發字搜 klib 名稱,已經有多列重疊:
  - `combine`:D-5、D-6、D-35
  - `stateIn`:D-5、D-6、D-15、D-49
  - `Channel`:D-7、D-16
  - `CoroutineDispatcher`:D-20、D-55
  - `collectLatest`:D-4、D-16
  - `coroutineScope`:D-1、D-8
- `combine` 對 D-5、D-6 是決策點,對 D-35(Paging)只是撞名。
  - 寫 `D-5、D-6、D-35`,等於斷言 D-35 也是它的決策點,是錯的。
  - 寫 `撞名 D-35`,D-5、D-6 的正向綁定就丟了。
  - 兩者混寫沒有格式,`撞名` 後面能不能接多列也沒定。
- 建議:歸屬欄允許「`D-5、D-6`」與「`撞名 D-35`」並列(反向同步要求每個被搜到的列都被二者之一覆蓋),並定義 `撞名` 接多列的寫法。

### F4 反查只看有反引號片段的對應檢查,沒有片段的整條默默漏掉
severity: major
blocking: 是。「沒被問到的都要列表」是這案的核心承諾,而這 11 對在機器眼裡根本不存在,連報錯都不會有。
- 位置:〈用詞〉「壞寫法片段」,加上範圍 3。
- 引句:「單位是(情境列, 對應檢查, 片段)」
- 佐證:跑真型錄,「非停用情境列 × 對應檢查」裡有 11 對的壞寫法欄沒有任何反引號片段,整對不產生任何單位。它們不會被判叫不出,也不會被要求進〈叫不出的壞寫法〉。例:
  - D-13/STATE-14:「使用者資料只存在 ViewModel,沒寫進資料庫或 DataStore」
  - D-54/TEST-35:「只靠手動開 LeakCanary 看」
  - D-53/TEST-37:「單元或 UI 測試直接用正式 baseUrl 的 Retrofit 實例」
  - D-58/UI-110:「自訂淺灰字色」
  - D-27/CO-10、D-18/ARCH-64、D-33/UI-90、D-35/UI-52、D-36/DATA-61、D-52/UI-108 同形。
- 天花板 5 只講「壞在沒寫某樣東西」的寫法要進表,但機制上只有帶反引號片段的才會被點名。
- 建議:每對(情境列, 對應檢查)至少要有一個單位。沒有片段的用佔位單位 `<無片段>` 強制進表,並寫明改由。

### F5 「測試路徑一律叫不出」跟程式不符,「95」跟自己的口徑不符
severity: minor
blocking: 否。這是文字與數字對不上,不會讓守衛失效,而且 S6 重數時會紅在數字上。
- 位置:〈用詞〉「叫得出」。
- 引句:「測試檔在推送前根本不出情境段」
- 佐證(路徑):`lumos._PITFALL_DIFF_TEST_PAT` 只認 `/test/`、`test_`、`_test.`、`.spec.` 等。
  - `app/src/androidTest/java/x/XTest.kt`:篩選不命中,`_stack_changed_ok` 回 True。
  - `core/src/commonTest/kotlin/X.kt`、`app/src/sharedTest/...`、`src/testFixtures/...`:同樣回 True。
  - 實跑 `composeTestRule.mainClock.autoAdvance = false`:放在 `src/test` 切不出段,放在 `androidTest` 切出 `[['D-51']]`。
  - D-51(TEST-29、30、32)、D-54(TEST-35)的真實測試多半放 androidTest,實際會被問,表上卻寫成叫不出。
- 引句:「184 個,叫不出 95 個」
- 佐證(數字):照 spec 自己的口徑(含 D-2、`TEST-` 走 `src/test`、非 TEST 走 `app/src/main`)重跑真型錄,單位 184 個,叫不出的是 103 個,不是 95。
  - 差的 8 個是原本當成叫得出的 TEST- 片段:`UnconfinedTestDispatcher`、`awaitItem()`、`registerIdlingResource`、`waitUntil`、`onNodeWithText(...)`、`flow.test { awaitItem() }`、兩個 `runTest {…}`。
  - 舊的 `sweep2.py.txt` 重跑只有 182 個單位、叫不出 93 個,95 是它再補上 D-2 的 2 個。
- 建議:TEST- 單位同時試 `src/test` 與 `src/androidTest` 兩個路徑,只有兩邊都叫不出才進表;重數後把 95 改成實際值。

### F6 範本小節名稱的比對沒講邊界
severity: minor
blocking: 否。是會讓核對變弱的邊角,不影響現有型錄的正確性。
- 位置:〈用詞〉「改由」的 `範本 T<n>`。
- 引句:「範本那一組有 `### 壞寫法:<對應檢查>` 小節」
- 佐證:`test-templates.md` T1 同時有 `### 壞寫法:API-1 依序呼叫` 和 `### 壞寫法:API-10 沒有進行中判斷`。`API-1` 是 `API-10` 的前綴,照前綴比對,拿掉 API-1 的小節核對照樣過。
- 其他變體:
  - T0 用的是 `### 壞測試:`。
  - T1 有 `### 測試:API-4 連坐版`。
  - 型錄別處會用 `_norm` 折疊全形冒號,標題若寫成全形冒號 `：` 要不要認,spec 沒講。
- 建議:寫明「編號後面必須接空白或行尾」,冒號先折成半形再比,並在 S2 補一個拿掉 API-1 小節的案例。

### F7 規則實跑只在 CI 發生,本機那一半的證明可以靠註解矇混
severity: minor
blocking: 否。CI 會抓到,代價是本機綠、CI 紅,不會默默放行。
- 位置:範圍 4 的 `route_rule_hits_problems`,以及 S5。
- 引句:「而且片段(〈API 決策點〉那邊是名稱)要逐字出現在 `samples/bad/<id>/` 的某支壞例檔裡」
- 引句:「只在有 ast-grep 的完整模式跑(同既有規則樣本自檢)」
- 佐證:
  - 逐字出現沒排除註解。壞例檔常帶 `// BAD`,片段只出現在 `//` 註解裡,靜態那半照樣過。
  - `scripts/test_lumos.py:126746-126750` 的 `t_kotlin_rulepack_samples` 在沒有 ast-grep 時直接 return,S5 綁定的就是這支測試,所以本機推送前整段實跑證明都不跑。
  - `check.py` 的 `scan()` 回報的是比對節點的起始行(原文:「ast-grep 報的是比對到的節點的起始行」)。多行運算式裡片段在後面的行時,「片段所在那一行被報」會誤判紅。
  - `scan()` 逾時後會把 `_TIMED_OUT` 設成 True,後面所有掃描回 None。spec 沒說 None 要判問題還是略過。
  - 既有自檢是一次 `scan(sg, cfg, samples/bad)`,「正常不到一秒」。新函式如果每筆各掃一次,約一百筆是分鐘級,spec 沒規定要一次掃完再建索引。
- 建議:寫明三件事。
  - 靜態比對先剝註解。
  - 匹配範圍用起訖行區間,不用起始行。
  - 掃描失敗判問題,並一次掃描後查表。

### F8 RETIRE-IF 第一條的量法不存在
severity: minor
blocking: 否。只是撤除條件到時候量不出來,不影響上線。
- 位置:RETIRE-IF。
- 引句:「上線八週後用 `lumos gov --stats` 看」
- 佐證:`lumos gov --stats` 輸出是每道閘的筆數、節點、起訖日,沒有盲判結論的分布。`docs/.governance-log.jsonl` 裡 `kt-situation` 是 0 筆(grep -c 為 0)。「盲判判不適用超過八成」沒有任何資料來源。
- 建議:先決定紀錄落在哪(例如段放行與盲判結果各記一筆帶列編號),再寫量法。

### F9 命中比例的基準與量法對不上現況
severity: minor
blocking: 否。有兩道各自能獨立擋的把關(8% 單字、10 個百分點整體),問題在基準與單位不一致。
- 位置:範圍 5 最後一條,加上〈實務隱患〉第一條。
- 引句:「E9 記的基準是 64%」
- 佐證:我用正式路徑 `_kt_sit_text_segments`(整支當新增、`app/src/main/...`)掃 Now in Android 310 支。
  - 現況命中檔數比例是 52.9%,不是 64%(E9 是 56 列時、不同方法量的)。
  - 情境段 679 個,(段, 列)配對 1048 組。
  - 實驗把母體裡 90 個 Now in Android 頻率介於 0 與 8% 的非停用名稱全加進 D-4 觸發字:檔數 65.2%(+12.3 個百分點),情境段 900(+32.5%),配對 1400(+33.6%)。
  - 補 `mapLatest`、`transformLatest` 幾乎無影響(678 段 / 1047 配對)。
  - 所以單字 8% 門檻管不住總量。檔數比例會低估盲判成本,因為成本跟「段 × 候選列」成正比。
- 缺口:
  - `sweep/` 沒有「至少命中一列」的腳本,`triage.py` 只算單字頻率。
  - 「釘版提交」的 sha 沒記。
  - 這個量法的語料是 Compose / Hilt 為主,不代表 Flow 或網路密集的專案。
- 建議:補量測腳本、同時報檔數與(段, 列)配對數,把停下門檻改成配對增幅,並記語料 sha。

### F10 klib 抽法的文法沒定,宣告形狀與平台標註沒有處理
severity: minor
blocking: 否。多半是實作者自己能補的細節,但寫明可以免得兩份實作不一致。
- 位置:〈用詞〉「公開名稱」主來源 klib 那條。
- 引句:「每個宣告行(`fun`、`val`、`var`、`const val`、`class`、`interface`、`object`、`enum entry`)的簡名」
- 佐證:
  - 擴充函式與泛型:`final inline fun <#A: kotlin/Any?, #B: …> (kotlinx.coroutines.flow/Flow<#A>).kotlinx.coroutines.flow/flatMapLatest(...)`。簡名要先去泛型、再去接收者括號、再去 `pkg/`,沒寫;還要去掉行尾 ` // …|…[0]` 簽名註解。
  - 存取函式:泛型去除如果寫成「去掉開頭的 `<…>`」,會把 `<get-entries>` 一起吃掉(我的第一版就這樣壞了)。
  - 具名伴生物件:`Channel.Factory` 在 klib 是 `final object Factory`,不是 `Companion`,規則只排除了 `Companion`,所以 `Factory` 會成為一列;`Key` 在四個類別各出現一次。
  - 列舉合成成員:`values`、`valueOf`、`entries` 每個列舉都有,沒被排除。
  - 帶點觸發字的外層:「比名稱前加上外層宣告的寫法」沒定義 `Channel.Factory.UNLIMITED` 跟原始碼寫法 `Channel.UNLIMITED` 怎麼對。
  - `// Targets:` 標註:17 處,例如 `[native]` 的 `runBlocking`、`IO`、`newSingleThreadContext`,以及 `[js]`、`[wasmJs]` 的 `promise`、`asPromise`、`awaitAnimationFrame`。Android 用不到卻要分類,spec 沒說要不要略過。
  - typealias:兩份檔都沒有 typealias 條目。`CompletionHandler` 在兩份檔裡只出現 `CompletionHandlerException`,所以「窮舉」不含 typealias。
  - 檔案編碼:klib 檔含 `§`(UTF-8),讀檔要寫 `encoding="utf-8"`,雜湊要用位元組。
- 母體規模沒問題:排除 internal 套件後 klib 約 428 個名稱,遠高於下限 300。升到 1.11.0 淨增 12 個(`Closed`、`Failed`、`associate*`、`cause`、`consumeTo`、`groupBy*`),`associate` 的 S1 案例成立。

### F11 歸屬欄空值與格式容錯、停用字規則的盲點
severity: minor
blocking: 否。都是補一兩句規則能解決的邊角。
- 位置:範圍 2 的規則清單,以及停用字規則。
- 引句:「停用字最常被選錯,不准用 `無決策` 默默帶過」
- 佐證:
  - 清單只有「理由空白」和「改由值不合」,沒有「歸屬欄不是四種寫法之一就是問題」。例如空白、`TBD`、`D-04`、`d-4`、`D-4、D-4`、`撞名D-4`(缺空格)、`無決策:xx`。
  - 前綴是半形「停用字,不帶決策:」,型錄別處(`_norm`)會折疊全形標點,作者寫全形會被擋但原因不直觀。
  - `STOP_TRIGGERS` 裡是 `Dispatchers.IO`、`Dispatchers.Default`,母體名稱是 `IO`、`Default`,兩者不相等,所以「停用字表裡的名稱」規則對這兩個最容易標錯的名稱不生效。
  - 〈統計〉新增的四個數的計數單位沒定:一個名稱歸多列 `D-n`、同一個名稱在兩節出現的改由,是算一筆還是多筆。
- 引句:「〈統計〉節多四個數(公開名稱數、各歸屬種類筆數、叫不出的壞寫法數、各改由筆數)」

### F12 反向同步用「觸發字的正規式搜名稱」,對結尾帶括號的觸發字永遠搜不到
severity: minor
blocking: 否。目前只影響三個觸發字,但這正是這道檢查要抓的「兩邊不同步」。
- 位置:範圍 2 反向那條。
- 引句:「任一非停用列的任一觸發字的正規式搜得到某個名稱」
- 佐證:D-60 的觸發字 `indexOf(`、`contains(`,D-58 的 `Color(`,編成正規式後要有 `\(`。名稱 `indexOf`(klib 第 990 行,`ReceiveChannel.indexOf`)是裸字串,搜不到。實際寫 `ch.indexOf(x)` 會中 D-60,而反向同步放過,作者可以標 `無決策`。
- 建議:搜之前把名稱補成 `名稱(` 與 `名稱` 兩種形狀。

## 實測效能(兩道檢查在大型錄上的成本)
- 載入 `scripts/lumos`:約 0.15 秒。
- 〈叫不出的壞寫法〉184 個單位全跑 `_kt_sit_text_segments`:0.10 秒。
- 反向同步:888 個名稱 × 所有觸發字的 `search`:0.06 秒。
- 在真型錄插入 700 列〈API 決策點〉假表後,`catalog_problems`:約 0.03 秒,沒有被既有解析器弄壞。
- 型錄現況是 528,001 位元組,加表後約增 60 到 90KB,對讀型錄的 AI 是額外上下文。
- 兩道純 Python 檢查合計低於 1 秒。慢的只可能是 F7 說的實跑規則那一步(沒有一次掃完的話)。
- 這些時間是 Python 單機實測;ast-grep 那一步本機沒有,沒量。

## 其他節
- 〈回退〉、〈依據來源〉、〈審計修正紀錄〉、S3、S4、S6:已讀,無 finding。
- S3 我實跑確認過:API-8 壞寫法欄的 `flatMapMerge` 片段在拿掉 D-4 的 `flatMapMerge` 後叫不出,`viewModelScope.launch { }` 仍是 D-4 觸發字,所以 API-8 另一個片段不受影響,S3 說的兩道各自守成立。
- 反例對照:剝註解與字串的詞法行為 spec 寫得準。實測落單的 `"`、`/*`、`//`、`"""` 會讓 D-4 判不中,反引號與單引號不會。

## 總結
最嚴重 severity 是 major,blocking 共 4 條(F1、F2、F3、F4),非阻擋 8 條(F5 到 F12)。
