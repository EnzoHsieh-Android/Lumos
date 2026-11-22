---
type: project
status: doing
created: 2026-11-21
updated: 2026-11-21
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/kotlin規則包
  - Systems/規格閘
related:
  - "[[Projects/改動選擇點都要有需求守住_計劃]]"
  - "[[Projects/選擇點表第二批常見誤用寫法_計劃]]"
---
# 選擇點表第三批業務情境寫法_計劃

## 白話

選擇點表([[Projects/改動選擇點都要有需求守住_計劃]])每列是「一個語法節點換成兄弟寫法」的機械壞法:換了測試還綠,就表示沒有測試守住那條需求,推送前要作者補測試或寫理由放行。第一、二批收的是運算子、集合與 Flow 兄弟寫法、空值處理與 Compose 副作用。使用者 2026-11-21 問:協程作用域「一支子協程失敗要不要連坐兄弟」(`coroutineScope` 對 `supervisorScope`)這種語境,能不能靠選擇點抓出來、回頭詰問需求;接著要求「先調研 kotlin 相仿的業務需求情境用法」,調研回來後選了「前五名加中段四條」。

這一批的共同點:兩種寫法都合法、編得過、單元測試分得出,**哪一個對取決於業務需求**(永遠只有一邊對的寫法歸靜態告警,不收)。每列要詰問的那句業務問題寫在型錄列的「行為差異」欄。

第三批(候選,設計審定案;每一列上線前還要過範圍 7 的實測門檻):
- 協程作用域:`supervisorScope {` ↔ `coroutineScope {`(一支子協程失敗時,兄弟照常做完/一起取消)。問:「其中一支壞了,其他還要不要照常顯示?」
- 筆數:`.singleOrNull` → `firstOrNull`、`.single` → `first`(多筆時回 null 或丟例外/取第一筆)。問:「符合條件的一定只有一筆嗎?多筆算資料錯誤嗎?」
- 找不到與解析失敗:`.firstOrNull` → `first`、`.toIntOrNull` → `toInt`、`.toLongOrNull` → `toLong`、`.toDoubleOrNull` → `toDouble`(回 null/丟例外)。問:「找不到或格式不對是正常情況還是錯誤?」
- 晚到的訂閱者:具名引數 `replay = 1` ↔ `replay = 0`(`MutableSharedFlow`、`shareIn`)。問:「畫面重建後要不要再看到上一個值?這是狀態還是只發一次的事件?」
- 延後啟動:`CoroutineStart.LAZY` → `CoroutineStart.DEFAULT`。問:「條件不成立時能不能根本不做(省一次呼叫)?」
- 緩衝滿了:`BufferOverflow.DROP_OLDEST` ↔ `BufferOverflow.DROP_LATEST`。問:「來不及處理時留最新的還是最早的?」
- 取消後還要做完:`withContext(NonCancellable)` → `withContext(kotlin.coroutines.EmptyCoroutineContext)`。問:「使用者離開之後,這次寫入還要不要做完?」
- 重試:拿掉 `.retry(…)`、`.retryWhen { … }`。問:「失敗要不要重試?重試安全嗎?」
- 新值取消舊的:`.mapLatest` → `map`、`.transformLatest` → `transform`。問:「新的值來了,舊的那次還要做完嗎?」

PRIOR-ART: 同第一、二批的論文〈Practical Mutation Testing at Scale〉https://arxiv.org/pdf/2102.11378 (2.2 在語法樹上產生、表 1、3.1 乾節點、3.2.1 型別前提事前擋)與 MutApi API 兄弟改寫表 https://sqlab-sustech.github.io/files/paper/ICSE2019-mutapi.pdf 。各列的語意出處:kotlinx.coroutines 官方〈Coroutine exceptions handling〉Supervision 一節 https://kotlinlang.org/docs/exception-handling.html ;官方〈Composing suspending functions〉Lazily started async 一節 https://kotlinlang.org/docs/composing-suspending-functions.html ;官方〈Cancellation and timeouts〉NonCancellable 一節 https://kotlinlang.org/docs/cancellation-and-timeouts.html ;Android 官方 StateFlow 與 SharedFlow https://developer.android.com/kotlin/flow/stateflow-and-sharedflow ;kotlinx.coroutines API 文件(`supervisorScope`、`coroutineScope`、`retry`、`mapLatest`、`BufferOverflow`、`CoroutineStart.LAZY`)https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/ ;Kotlin 標準庫 `singleOrNull`、`firstOrNull`、`toIntOrNull` https://kotlinlang.org/api/core/kotlin-stdlib/ 。候選、行為差異與排除理由來自 2026-11-21 的調研(本機 Kotlin 2.2.21、kotlinx-coroutines 1.10.2、`runTest` 對每組兩種寫法實跑:換過去編得過、兩種結果不同)。不採:`SupervisorJob()` ↔ `Job()`(型錄 CO-12 已判長壽元件用 `Job()` 永遠錯,歸靜態告警);`receiveAsFlow` ↔ `consumeAsFlow`(FLOW-28 已靜態把關);`first` → `firstOrNull`、`withTimeout` → `withTimeoutOrNull`(放寬方向,`T?` 放不進 `T`,編不過);`tryEmit` ↔ `emit`、`stateIn` ↔ `shareIn`(回傳型別不同);`BufferOverflow.SUSPEND` → `DROP_*`(容量 0 時執行就丟例外,只會被輕易殺掉);`Mutex.withLock` 拿掉(多節點、`runTest` 單執行緒測不出);`Channel.CONFLATED` ↔ `BUFFERED`(找不到點名這組互換的官方來源)。中段沒選的三條(`withTimeoutOrNull` → `withTimeout` 要先縮乾節點 A-4、`roundToInt` → `toInt`、`repeatOnLifecycle` 的狀態)留給下一批。
RETIRE-IF: 同第二批:上線日(寫進第三批的 Verification)起滿兩個月,讀 `gov --stats` 選擇點段的「依列號」數字:第三批任一列放行至少 5 筆、其中理由是「等價」或「不是需求」的超過八成,或那一列至少 5 個壞法、其中跑不出結果超過一半(「基準不綠沒跑」不算),就把那一列撤掉(〈回退〉第 1 項)。
REVISIT:2027-01-21 第三批上線滿兩個月前後,連同第二批的 REVISIT 一起看第三批各列的殺掉率、跑不出結果比例與放行理由,決定留哪幾列;同時重看 `collectLatest` 該不該跟 `mapLatest` 一樣收

## 舊否決比對

- 型錄〈選擇點表〉說明段的「不收(單元測試分不出或常掛住)」清單列了 `coroutineScope`/`supervisorScope`。**這份翻案**:2026-11-21 調研用 `runTest` 實測,async 形狀的測試(一支在 10 毫秒後丟例外、另一支 100 毫秒後完成並記一筆,斷言回傳與那筆紀錄)在兩種寫法下結果不同、沒有掛住;等價只發生在大括號裡少於兩個子協程時,由規則排除(範圍 2)。使用者 2026-11-21 看過翻案理由後選了含這一列的「前五名加中段四條」。同一張清單的其他項(`first`/`last`、`collectLatest`/`collect`、`Dispatchers.*`、`SharingStarted.*`、`buffer`、`conflate` 等)不動。
- 同一張清單收 `collectLatest`/`collect` 為「不收」,這份卻收 `mapLatest` → `map`:兩者理由要一致。這份只收 `mapLatest`、`transformLatest`(調研以虛擬時間實測分得出);`collectLatest` 照舊不收,REVISIT 那天依 `mapLatest` 的數字一起重看。
- [[Projects/選擇點表第二批常見誤用寫法_計劃]]〈不做〉「回傳型別不同的互換」:這份每一列都是同型別互換或 `T` 放進 `T?` 的單向互換(`firstOrNull` → `first`、`toIntOrNull` → `toInt`),不碰反方向。
- [[Systems/kotlin規則包]] 否決過「選擇點表跟情境決策表合成一張」:照舊寫在〈選擇點表〉,跟決策表重疊的列(D-4、D-7、D-8、D-9、D-11、D-15、D-16、D-17、D-26)用列號互指。
- [[Systems/規格閘]] 否決過「處置鍵帶列號或壞法雜湊」:這份只加列,不改 (檔, 行指紋) 的處置鍵。
- [[Systems/kotlin規則包]] 否決過「把 Detekt 規則點名的寫法全收」:這份每列都有「看業務需求」的理由,不是照規則清單收。

## 用詞

- **論文**、**選擇點表**、**乾節點規則**、**錨點**、**型別前提**:同 [[Projects/改動選擇點都要有需求守住_計劃]]〈用詞〉。
- **跑不出結果**:壞法編不過、逾時或基準不綠,得不出殺掉或存活的終態;統計口徑見 [[Systems/規格閘]] 的 gov --stats 依列號那條 WHY。
- **業務情境寫法**:兩種寫法都合法、都可能是對的,哪一個對取決於需求;跟「永遠只有一邊對」的靜態告警相對。
- **整個呼叫命中**:規則用樣式 `$A.retry($$$B)` 命中整個呼叫運算式,`$A` 是接收者;跟第一、二批「只命中 `.方法名` 那一段」的 API 列相對。錨點仍是「方法名」,位置是 `$A` 結尾之後跳過空白、換行後的 `.` 或 `?.` 後面那個識別字(換行寫法的 `.retryWhen` 在下一行時,錨點行就是那一行)。這種列的編輯從 `$A` 結尾開始,換行寫法時起點落在上一行行尾,所以壞法身分的 `old` 含接收者那一行與錨點那一行(母計劃〈用詞〉「API 換記號時只有錨點那一行」的例外)。
- **子協程**:作用域大括號裡直接呼叫、或位在迴圈呼叫大括號裡的 `async`、`launch`。
- **迴圈呼叫**:`.map`、`.forEach`、`.mapIndexed`、`.forEachIndexed`、`.flatMap` 這幾個帶大括號的呼叫(大括號會對每個元素跑一次,裡面的一個 `async` 等於開出好幾個子協程)。

## 範圍

1. **型錄**:`skills/kotlin-idioms/checks-catalog.md`〈選擇點表〉新增第三批列,類別一律 API,欄位同第一、二批;列號照第二批規則在範圍 7 過門檻後才給(從 C-38 起依本節順序,被擋下的不給號、後面的往前補)。
   - `supervisorScope` 列:錨點「運算元起始」(命中的是作用域名稱那個識別字)、候選壞法 `coroutineScope`、需補的 import `kotlinx.coroutines.coroutineScope`、型別前提(無)、對應決策表 D-8、D-9。
   - `coroutineScope` 列:同上反方向,候選 `supervisorScope`、import `kotlinx.coroutines.supervisorScope`。
   - `singleOrNull`、`single`、`firstOrNull`、`toIntOrNull`、`toLongOrNull`、`toDoubleOrNull`、`mapLatest`、`transformLatest` 各一列:錨點「方法名」、候選 `firstOrNull`、`first`、`first`、`toInt`、`toLong`、`toDouble`、`map`、`transform`;Flow 版本要補的 import 照第一版「檔頭逐一 import 原寫法才補」(`kotlinx.coroutines.flow.firstOrNull`、`.first`、`.map`、`.transform`);對應決策表:`singleOrNull`、`single` —(型錄觸發字表標「無決策」),`firstOrNull` D-26,`toIntOrNull` 三列 —(決策表沒有數字解析那一列),`mapLatest` 兩列 D-4。
   - `replay` 兩列:錨點「運算元起始」(命中的是具名引數 `replay = ` 後面那個整數字面值本身,不是整個引數——整個引數被換成樣板會丟掉 `replay =`)、候選 `0`(命中 `1`)與 `1`(命中 `0`)、對應決策表 D-7、D-15。
   - `CoroutineStart.LAZY` 列:錨點「方法名」(命中 `.LAZY` 那一段)、候選 `DEFAULT`、對應決策表 —(型錄觸發字表把 `LAZY` 標「決策不問」;相關檢查 CO-18)。
   - `DROP_OLDEST`、`DROP_LATEST` 兩列:錨點「方法名」(命中 `BufferOverflow.` 後那一段)、候選互換、對應決策表 D-16。
   - `NonCancellable` 列:錨點「運算元起始」(命中 `withContext(` 唯一引數那個識別字)、候選 `kotlin.coroutines.EmptyCoroutineContext`(寫完整套件名,免補 import)、對應決策表 D-17。
   - `retry`、`retryWhen` 兩列:錨點「方法名」(整個呼叫命中,〈用詞〉)、候選 `(拿掉呼叫)`、對應決策表 D-11。
   - 說明段同步:「不收」清單拿掉 `coroutineScope`/`supervisorScope` 並補一句翻案理由與日期;補「第三批來源與不收理由」;〈統計〉的選擇點表列數改成 37 加實際上線列數。
2. **規則**:`configs/ast-grep/kotlin-choice/rules-choice/api.yml` 補第三批各條(規則 id 等於列號),樣本寫進新檔 `samples/choice-batch3.kt`。各條的命中條件:
   - 作用域兩列:命中 call_expression 第一個子節點的 `supervisorScope`/`coroutineScope` 識別字,而且大括號的 statements 裡①有兩個不同的陳述各自含 `async`/`launch` 呼叫(後一個 follows 前一個),或②有 `async`/`launch` 呼叫位在 `.map`、`.forEach`、`.mapIndexed`、`.forEachIndexed`、`.flatMap` 這類迴圈呼叫的大括號裡。少於兩個子協程時不命中(兩種寫法必然等價)。2026-11-21 以 ast-grep 0.51.2 試做:兩個 `async`、兩個 `launch`、`map { async }`、`forEach { launch }` 命中,只有一個 `async`、大括號裡沒有子協程、`load { async }` 不命中。
   - 方法名各列:照第一版 `$R.方法名` 後接呼叫的 navigation_suffix 規則;`CoroutineStart.LAZY`、`BufferOverflow.DROP_*` 命中接在那個型別名後面的 navigation_suffix(不是呼叫)。`LAZY` 列另排除「建立後同一個運算式就 `.await()`」(`async(start = CoroutineStart.LAZY) { … }.await()`,必然等價)。
   - `replay` 兩列:命中節點是整數字面值 `1`(或 `0`)本身,用 `inside` 限定它的外層 value_argument 名稱是 `replay`;其他數字不收。
   - `NonCancellable` 列:`withContext(` 的唯一引數是 `NonCancellable` 識別字,而且不在 `finally` 區塊裡(那裡一定要用,型錄 CO-15 已靜態把關,換掉只會造出已知錯誤寫法)。
   - `retry` 兩列:樣式 `$A.retry($$$B)`、`$A.retry($$$B) { $$$C }`、`$A.retry { $$$C }`、`$A.retryWhen($$$B)`、`$A.retryWhen { $$$C }` 與 `?.` 版本;接收者是 `Result`(WorkManager `Result.retry()`)時拿掉呼叫會編不過,規則排除接收者是 `Result` 識別字的寫法。2026-11-21 試做:單行、換行、帶 lambda、`?.` 都命中,`$A` 取得到接收者範圍。
3. **lumos 產壞法**(只動 scripts/lumos 的選擇點程式):
   - `_choice_anchor` 的「方法名」:命中帶 `$A` 後設變數時(整個呼叫命中),從 `$A` 結尾開始跳過空白與換行再比對 `.` 或 `?.` 加識別字;沒有 `$A` 照舊從命中開頭比對。
   - `_choice_api_edits` 的 `(拿掉呼叫)`:現在只收 `s, e`,`_choice_anchor_edits` 要把命中的 `mv` 一併傳進去;命中帶 `$A` 時刪掉 `mv["A"]` 結尾到 `e` 那一段(引數、尾隨 lambda 都在語法樹的範圍內,不自己數括號);沒有 `$A` 照舊只刪 `.方法名()` 加空括號。
   - `_choice_also`(補 import)多收命中範圍 `(s, e)`:錨點是「運算元起始」而候選是單一識別字的列(作用域兩列),原寫法取 `b[s:e]`,不再要求 `op` 不是 None(運算元起始的 `op` 一律是 None);其餘照第一版(檔頭逐一 import 原寫法才補);`_choice_pick` 呼叫它的地方跟著傳範圍。
   - 其餘(運算元起始換整個節點、方法名換識別字)沿用第一、二批的通用路徑,不另寫。
4. **check.py**:類別、錨點白名單不動(第三批只用 API 類與既有錨點);樣本核對照舊;〈統計〉列數照實際上線改。
5. **統計**:沿用第二批的「依列號」,不改。
6. **文件**:Systems/kotlin規則包 `about_code` 加 `samples/choice-batch3.kt`,補一條 WHY 行(第三批收「業務情境寫法」、翻案 `coroutineScope`/`supervisorScope` 的理由);Systems/規格閘 補「整個呼叫命中」的錨點位置說明。
7. **上線前實測門檻**:照第二批範圍 7 的樣本、量法與門檻(兩個真實 Kotlin 專案甲、乙,各最近 10 個改到 `.kt` 的非合併提交;改動行有選擇點的比例增加不超過 10 個百分點、每個提交挑壞法不超過 10 秒且驗不了的檔數與壞法超過 30 的提交數不增加、最大檔掃描輸出不超過 16MB),超過時依單獨增量拿掉列。另記每列在這 20 個提交裡命中幾次(命中 0 次的列照樣可上線,寫進 Verification 給 REVISIT 對照)。

## 不做

- 不收調研排除表裡的寫法(理由見 PRIOR-ART),也不收中段沒選的三條。
- 不改一行一個壞法、回報上限、乾節點表、殺傷力判定、處置鍵與推送前那一道的規則。
- 不加新類別、新錨點;不改型錄讀表與 check.py 白名單。
- 不替 `collectLatest` 翻案(REVISIT 再看)。

## 實務隱患

- 編不過:`toIntOrNull` 系列只存在於 String,換成 `toInt` 一定有;`firstOrNull` → `first` 在結果後面接 `?.`、`?:` 時 K2 只出警告,專案開 `allWarningsAsErrors` 時會編不過,落成跑不出結果。作用域兩列若檔頭只單獨 import 原寫法,範圍 3 補 import;用萬用 import 的檔不用補。同名的自訂 `retry`、`single` 等語法樹分不出,落成跑不出結果或等價放行。
- 等價存活:`singleOrNull` 以唯一鍵比對而測試資料沒有重複、`firstOrNull` 的接收者一定非空、`replay` 測試總是先訂閱再送、`DROP_*` 測試從沒塞滿緩衝——這些存活正是要逼作者補「重複資料」「找不到」「晚到訂閱」「塞滿」的測試,不算白擋;作用域兩列少於兩個子協程的必然等價由範圍 2 排除;`LAZY` 建立後立刻 `.await()` 的由範圍 2 排除。其餘靠回報上限與放行理由「等價」承接,RETIRE-IF 看比例。
- 同一行重疊:`x.firstOrNull { … } ?: d` 同一行同時有第二批 `?:` → `!!` 與這份 `firstOrNull` → `first` 兩個選擇點,一行只挑一個(論文 4.1),兩者詰問的是同一件事(找不到要怎麼辦),挑到哪一個都可以;處置以行為單位,不會重複要求。
- 測試成本:作用域兩列的守門測試要用 async 形狀或在被測程式自己的 scope 裝例外處理器——`runTest` 不收 `CoroutineExceptionHandler`,`supervisorScope` 裡 `launch` 失敗會讓測試以未捕捉例外收場;`DROP_*`、`replay` 要虛擬時間或 `replayCache`。這些寫法寫進型錄列的出處欄指向 skills/kotlin-idioms/test-templates.md 既有範本,沒有就由人放行。
- 推送負擔:`firstOrNull`、`toIntOrNull` 很常見,有選擇點的行會變多;範圍 7 用實測門檻決定每列上不上線。
- 規則誤命中:作用域規則②的「迴圈呼叫大括號裡」往外找最近的 lambda,若整個作用域本身就寫在外層 `map { }` 裡(`list.map { coroutineScope { async { } } }`),只有一個子協程也可能命中;設計審與樣本要驗這一型。
- 併發與交易:已排除:沿用第一、二批,單人單機依序操作。
- 已排除:金流:只改型錄、規則與產壞法的程式,不碰付款或金額計算
- 已排除:對外送出:掃描與殺傷力都在本機跑,不對外送任何資料
- 已排除:不可逆:治理帳照舊逐筆追加,撤列後新推送不再產那一列的壞法,已記的處置照第一版以行為單位續用
- 守衛面:不排除——新列與三處產壞法擴充會改推送前選擇點那一道挑出的壞法,所以走設計審;S7 守住只含第一、二批語法的行挑選結果不變;型錄、規則、樣本任一項半套會讓整張表判壞、所有 Kotlin 推送被擋,〈回退〉要一次做齊並先跑 check.py。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 一對一機械壞法、在語法樹上產生、型別前提事前擋、乾節點 | 論文 2.2、表 1、3.1、3.2.1 | https://arxiv.org/pdf/2102.11378 |
| API 兄弟寫法寫成改寫表 | MutApi | https://sqlab-sustech.github.io/files/paper/ICSE2019-mutapi.pdf |
| `supervisorScope` 與 `coroutineScope` 的失敗傳遞 | kotlinx.coroutines 官方例外處理 Supervision 一節 | https://kotlinlang.org/docs/exception-handling.html |
| `CoroutineStart.LAZY` 的依序陷阱與不 await 就不做 | 官方 Composing suspending functions | https://kotlinlang.org/docs/composing-suspending-functions.html |
| `NonCancellable` 讓取消後的掛起照常做完 | 官方 Cancellation and timeouts | https://kotlinlang.org/docs/cancellation-and-timeouts.html |
| `replay` 與晚到訂閱者、一次性事件 | Android 官方 StateFlow 與 SharedFlow | https://developer.android.com/kotlin/flow/stateflow-and-sharedflow |
| `retry`、`mapLatest`、`BufferOverflow` 語意 | kotlinx.coroutines API 文件 | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/ |
| `singleOrNull` 多筆回 null、`toIntOrNull` 格式錯回 null | Kotlin 標準庫 API 文件 | https://kotlinlang.org/api/core/kotlin-stdlib/ |
| 整個呼叫用樣式命中、靠後設變數取接收者範圍 | ast-grep 規則文件(pattern 與 meta variable) | https://ast-grep.github.io/guide/pattern-syntax.html |
| 必然等價的壞法事前排除 | Trivial Compiler Equivalence;常見寫法造成的等價用靜態分析抓 | https://discovery-pp.ucl.ac.uk/id/eprint/1499169/1/Jia_Trivial_Compiler_mutation-testing-papadakis-icse15.pdf、https://homes.cs.washington.edu/~rjust/publ/equi_mutants_ems_issta_2024.pdf |
| 收這批寫法 | 使用者方向 | 使用者 2026-11-21:「可以先調研kotlin相仿的業務需求情境用法? 我們再來收錄第三批」;選「前五名加中段四條」;「開始」 |

## 驗收條款

測試做法同第二批:S1–S4 測 lumos 這一側,規則文字寫在測試裡、跟合成的型錄列一起放進暫存目錄;規則本身該不該命中由 S5 讀真規則與真樣本核對;要 ast-grep 的測試在本機沒裝時用 `_SrcOnly` 標成跳過,不准空 return。

- [S1] 當改動行有 `supervisorScope {` 而大括號裡有兩個 `async`,choice-points 應 挑出 `coroutineScope`,反方向同理;檔頭只單獨 import 原寫法時 應 補兄弟寫法的 import,萬用 import 時 應 不補 [test:t_choice_points_batch3_scope]
- [S2] 當改動行有 `.retry(3)`、`.retryWhen { … }`、`.retry(3) { … }`,choice-points 應 刪掉接收者之後到呼叫結尾那一段;`.retryWhen` 換行寫在下一行、只改了那一行時 應 照樣挑出,錨點行是 `.retryWhen` 那一行 [test:t_choice_points_batch3_retry]
- [S3] 當改動行有 `replay = 1`、`CoroutineStart.LAZY`、`BufferOverflow.DROP_OLDEST`、`withContext(NonCancellable)`,choice-points 應 分別換成 `replay = 0`、`CoroutineStart.DEFAULT`、`BufferOverflow.DROP_LATEST`、`withContext(kotlin.coroutines.EmptyCoroutineContext)` [test:t_choice_points_batch3_values]
- [S4] 當改動行有 `.singleOrNull`、`.single`、`.firstOrNull`、`.toIntOrNull`、`.mapLatest`,choice-points 應 照方法名錨點換成 `firstOrNull`、`first`、`first`、`toInt`、`map`,Flow 版本照第一版在檔頭有逐一 import 時補 import [test:t_choice_points_batch3_api]
- [S5] 當第三批樣本檔跑過選擇點樣本核對,每條第三批規則 應 命中該命中的、不命中不該命中的,不命中的包含:作用域裡只有一個 `async`、`load { async { } }`、建立後立刻 `.await()` 的 `LAZY`、`finally` 裡的 `withContext(NonCancellable)`、`replay = 2`、`Result.retry()` [test:t_choice_samples_batch3]
- [S6] 當型錄加入第三批列,check.py 應 認得(類別 API、錨點方法名與運算元起始),〈統計〉列數 應 等於表裡實際列數,「不收」清單 應 不再有 `coroutineScope` [test:t_choice_table_batch3]
- [S7] 當第三批列加入後,只含第一、二批語法的既有樣本行 應 挑出跟加入前相同的壞法(加入前的結果在實作第一步先跑一次、釘成測試裡的常數);沒有 `$A` 的既有 `(拿掉呼叫)` 列 應 照舊只刪 `.方法名()` [test:t_choice_points_batch3_stable]
- [S8] 當第三批規則在兩個真實 Kotlin 專案最近 10 個改到 `.kt` 的提交上跑過,照第二批範圍 7 的門檻 應 全部通過,超過時依單獨增量拿掉列 [manual:照範圍 7 在兩個真實專案各量加入前後,數字、每列命中次數與拿掉的列寫進 Verification]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | `supervisorScope {` 下面兩行 `val a = async { f() }`、`val b = async { g() }` | 壞法把 `supervisorScope` 換成 `coroutineScope` | 官方例外處理 Supervision 一節 |
| S1 | 同上,檔頭有 `import kotlinx.coroutines.supervisorScope`、沒有 `coroutineScope` 的 import | 檔頭補 `import kotlinx.coroutines.coroutineScope` | 第一版 API 列補 import 做法 |
| S1 | 同上,檔頭是 `import kotlinx.coroutines.*` | 不補 import | 第一版「逐一 import 原寫法才補」 |
| S2 | `val w = flow.retry(3).map { it }` | `val w = flow.map { it }` | kotlinx.coroutines retry 文件 |
| S2 | `val z = repo.items()` 下一行 `    .retryWhen { c, n -> n < 2 }`,只改第二行 | 結果是第一行原樣、第二行消失;錨點行是第二行,壞法的 `old` 含第一、二兩行 | 本計劃〈用詞〉整個呼叫命中 |
| S2 | `repo.items().retry(3) { it is IOException }` | `repo.items()` | 本計劃範圍 3 |
| S3 | `MutableSharedFlow<Int>(replay = 1)` | `MutableSharedFlow<Int>(replay = 0)` | Android 官方 SharedFlow |
| S3 | `async(start = CoroutineStart.LAZY) { f() }` | `async(start = CoroutineStart.DEFAULT) { f() }` | 官方 Composing suspending functions |
| S3 | `onBufferOverflow = BufferOverflow.DROP_OLDEST` | `onBufferOverflow = BufferOverflow.DROP_LATEST` | kotlinx.coroutines BufferOverflow 文件 |
| S3 | `withContext(NonCancellable) { save() }` | `withContext(kotlin.coroutines.EmptyCoroutineContext) { save() }` | 官方 Cancellation and timeouts |
| S4 | `val u = users.singleOrNull { it.id == id }` | `val u = users.firstOrNull { it.id == id }` | Kotlin 標準庫 singleOrNull |
| S4 | `val n = s.toIntOrNull() ?: 0` | 挑到這一列時 `val n = s.toInt() ?: 0`(同一行另有 `?:` 列,挑哪個由行指紋決定) | Kotlin 標準庫 toIntOrNull;論文 4.1 一行一個壞法 |
| S4 | `q.mapLatest { search(it) }`,檔頭有 `import kotlinx.coroutines.flow.mapLatest` | `q.map { search(it) }`,檔頭補 `import kotlinx.coroutines.flow.map` | kotlinx.coroutines mapLatest 文件;第一版補 import |
| S5 | `supervisorScope { val a = async { f() }; a.await() }` | 不命中(只有一個子協程,必然等價) | TCE 研究 |
| S5 | `coroutineScope { ids.map { async { load(it) } }.awaitAll() }` | 命中 | 型錄決策表 D-3、D-8 |
| S5 | `async(start = CoroutineStart.LAZY) { f() }.await()` | 不命中 | 官方 Composing suspending functions(立刻 await 等於依序) |
| S5 | `finally { withContext(NonCancellable) { close() } }` | 不命中 | 型錄 CO-15 |
| S5 | `MutableSharedFlow<Int>(replay = 2)`、`Result.retry()` | 不命中 | 本計劃範圍 2 |
| S6 | 型錄加第三批列後跑 `check.py --catalog-only` | 不報錯;〈統計〉選擇點表列數等於表裡列數 | 第二批範圍 4 |
| S7 | 第一、二批既有樣本裡不含第三批語法的行 | 每行的行指紋與挑出的壞法等於加入前釘下的常數 | 論文 4.1 挑選要穩定 |
| S7 | 既有 `.distinctUntilChanged()` 的 `(拿掉呼叫)` 列 | 照舊只刪 `.distinctUntilChanged()` | 第一版 API 列 |
| S8 | 兩個真實專案最近 10 個改到 `.kt` 的提交,加入第三批前後 | 照第二批範圍 7 門檻全過;否則依單獨增量拿掉列 | 第二批範圍 7 |

## 回退

1. 單列撤掉:照第二批〈回退〉第 1 項(拿掉型錄列、規則、樣本標記,列號加進 `已撤列號:`,撤之前抄「依列號」數字進 Verification,推之前跑 check.py)。
2. 整批撤掉:第 1 項對第三批每一列各做一次,刪掉 `samples/choice-batch3.kt`,「不收」清單加回 `coroutineScope`/`supervisorScope`;範圍 3 的三處擴充留著(`_choice_anchor`、`_choice_api_edits` 在沒有帶 `$A` 的方法名列時走不到,`_choice_also` 在沒有運算元起始的 import 列時走不到;S7 守既有行為不變)。
3. 已記的處置照第一版以 (檔, 行指紋) 為單位續用(同第二批〈回退〉第 3 項)。

## 天花板

1. 只收調研找到、有官方出處的幾組寫法;沒列到的業務情境照樣不管。
2. 語法樹沒有型別:同名自訂函式分不出,`firstOrNull` 接 `?.` 在開 `allWarningsAsErrors` 的專案編不過,落成跑不出結果要人放行。
3. 作用域兩列只認〈用詞〉定義的子協程(大括號裡直接看得到的,與迴圈呼叫大括號裡的);子協程藏在別的函式裡呼叫的,命中不到(漏判)。
4. 「哪一邊對看需求」是調研依官方文件判的,沒有頻率統計;放行理由「不是需求」的比例由 RETIRE-IF 看。
5. 處置以「行」為單位(第一版取捨)。

## 審計修正紀錄
