severity: major

本輪審查的 repo 沒被我改動。`docs/.canary-log.jsonl` 與 `docs/.governance-log.jsonl` 的未提交改動在我開始前就有。

**重現方式**:在 repo 根目錄用 `check.load_lumos()` 載入真的 `scripts/lumos`,用 `lm._kt_sit_text_segments("X.kt", 程式, rows)` 切段。再呼叫 `check._sit_first_pass(lm, segs, 該列, "main" 或 "alt")`。回 `(None, 原因)` 是被擋,回 `((段, 行), None)` 是放行。這正是 `situation_sample_problems` 用的路徑。

**鏡頭 2 結論**:
- **自測走真的切段與核對。** 它直接呼叫 `lumos._kt_sit_text_segments` 與 `_kt_sit_row_check`,沒有另寫一套。
- **`python3.14 scripts/test_lumos.py -k kt_situation_evidence_samples` 通過**(23 passed)。
- **`.kt.txt` 不會被當產品碼,也沒有漏掉。**
  - `_stack_changed_ok`、`_nodehome_code_kind`、`_docs_only_file`、`_is_code_file` 都判它不是程式檔。
  - 它在 `configs/` 底下,不在文件白名單內,單獨推它會跑全套。
- **註解有一處不準確。** 註解寫「副檔名不是 .kt:不讓推送閘的棧別題把教材當產品碼」,但 `.kt` 樣本本來就被 `_RULEPACK_SAMPLE_RE` 排除,所以這句理由不實。

## F1 D-1 的 `awaitAll` 寫法被誤擋

severity: major
blocking: 是

引句:「// === main-ok 帶 dispatcher 的 async(代碼審 r1 邊界 F3)」

型錄 `skills/kotlin-idioms/checks-catalog.md:152` 的 API-4 自己寫「要一起失敗:`coroutineScope { awaitAll(...) }`」。D-1 的主樣式第三條 `\.await\(\)` 認不得 `awaitAll`。

輸入:
```
suspend fun f() = coroutineScope {
    val (a, b) = awaitAll(async { api.a() }, async { api.b() })
    Ui(a, b)
}
```
輸出:`BLOCK`,原因是第一條 `\basync\b(?!...)` 不在 evidence 那一行。`listOf(1,2).map { async { api.get(it) } }` 加 `ds.awaitAll()` 也被擋。

## F2 D-1 立刻 await 的壞寫法換個寫法就放過

severity: major
blocking: 是

引句:「// === bad API-14 async 立刻 await,等於沒並行」

樣本只擋同一行的 `}.await()`。第一條的 `(?!.*\}\s*\.await\(\))` 只看單行,所以兩種常見變形都放行。

輸入 A:
```
val a = async { api.a() }
val ra = a.await()
val b = async { api.b() }
val rb = b.await()
```
輸入 B:
```
val a = async {
    api.a()
}.await()
```
輸出:兩者都是 `PASS line2`。

## F3 D-16 的 `Channel.BUFFERED`、`CONFLATED`、`trySend().isSuccess` 被誤擋

severity: major
blocking: 是

引句:「// === main-ok Channel 用有上限的容量」

主樣式的 Channel 分支要求容量是數字:`Channel\s*(?:<[^>]*>)?\(\s*(?:capacity\s*=\s*)?\d`。但同一份型錄 D-7 的例外寫法就是 `Channel<Event>(Channel.BUFFERED)`。輸入 `private val _events = Channel<Event>(Channel.BUFFERED)` 被擋,`Channel.CONFLATED` 也被擋。

`trySend(v).isSuccess` 與 `.getOrNull()` 也被擋,多行 `trySend(v)\n.onFailure{}` 同樣被擋。

## F4 D-16 的 `UNLIMITED` 壞寫法換個寫法就放過

severity: minor
blocking: 否

引句:「// === bad FLOW-30 無上限的緩衝(代碼審 r1 接手 F5)」

`buffer(capacity = Channel.UNLIMITED)` 輸出 `PASS line1`。`buffer(\n    Channel.UNLIMITED\n)` 也是 `PASS line1`,因為負向前瞻只看行尾。這種寫法比較少見,所以只列 minor。

## F5 D-23 擋掉型錄自己允許的 `Unit` 回傳

severity: major
blocking: 是

引句:「// === main-ok 只改介面宣告:Response<Unit>(代碼審 r1 接手 F2)」

型錄 `checks-catalog.md:174`(API-26)寫「空回應宣告成 `suspend fun delete(): Response<Unit>` 或 `Unit`」。D-23 的樣式只認 `Response<Unit>` 與 `.isSuccessful`。

輸入:
```
@DELETE("users/{id}")
suspend fun delete(@Path("id") id: Long)
```
輸出:`BLOCK`。寫成 `): Unit` 也被擋。

## F6 D-24 擋掉型錄 API-30 自己的標準寫法

severity: major
blocking: 是

引句:「// === main-ok 在 execute 區塊內讀完串流」

型錄 `checks-catalog.md:178` 的 API-30 標準寫法是 `client.prepareGet(url).execute { resp -> resp.bodyAsChannel().copyTo(out) }`。D-24 的第三條 `\bexhausted\(\)|\breadRemaining\(` 認不得 `copyTo`。

輸入就是那一行原文,輸出 `BLOCK`:第一條 `\.execute\s*\{` 找得到,但第三條不在段材料。

## F7 D-47 的泛型逗號被誤擋

severity: major
blocking: 是

引句:「// === main-ok 可缺的欄位給預設值」

樣式 `\bva[lr]\s+\w+\s*:[^=,)]{0,200}=` 排除逗號,所以 `Map<String, String>` 這種泛型型別有預設值時,擋掉的是標準寫法。

輸入:
```
@Serializable
data class P(
    val name: String,
    val extras: Map<String, String> = emptyMap(),
)
```
輸出:`BLOCK`。`val m: Map<String, Int>? = null` 也被擋。

## F8 D-42 擋掉 DataStore 的 `edit {}`

severity: major
blocking: 是

引句:「// === main-ok 少量設定用 DataStore,更新寫成一個交易」

主樣式只認 `updateData`、`Room`、`RoomDatabase`、`@Dao`。Preferences DataStore 最常見的寫法是 `ds.edit { it[DARK] = v }`,輸出 `BLOCK`。

## F9 D-32 的 `LaunchedEffect(Unit)` 被誤擋

severity: major
blocking: 是

引句:「// === alt-ok 要跟呼叫點同壽:LaunchedEffect(true)」

例外樣式只認 `LaunchedEffect(true)`。實際專案裡更常見的 `LaunchedEffect(Unit) { vm.start() }` 輸出 `BLOCK`,`LaunchedEffect(key1 = true)` 也被擋。多行寫成 `DisposableEffect(\n owner\n)` 同樣被擋。這一列的主樣式是 `(無)`,所以作者還有出口(答 main)。

## F10 D-34 在 clickable 與 padding 之間夾別的 Modifier 被誤擋

severity: major
blocking: 是

引句:「// === main-ok 標準寫法:clickable 在 padding 前(圓括號)」

主樣式第二條要求 `.clickable(...)` 後面緊接 `.padding`。以下三種都 `BLOCK`:
- 輸入 `Modifier.clickable { onClick() }.background(Color.Red).padding(8.dp)`:被擋。
- 輸入 `Modifier.clickable { go() }.size(48.dp).padding(8.dp)`:被擋。
- 輸入 `Modifier.clickable { items.forEach { go(it) } }.padding(8.dp)`:被擋,因為 lambda 內再有大括號。

例外寫法也有同樣問題:`Modifier.padding(8.dp).background(c).clickable {…}` 與 `.padding(8.dp).clip(..).clickable` 都被擋。

## F11 D-27 擋掉非 `UiState` 命名的狀態類別

severity: major
blocking: 是

引句:「// === main-ok 可缺的欄位給預設值」(D-27 沒有這類引句可用,以上列代表,實際證據在 `checks-catalog.md` D-27 列的主樣式)

主樣式第一條只認 `UiState` 命名。輸入:
```
private val _state = MutableStateFlow<ViewState>(ViewState.Loading)
...
_state.value = ViewState.Success(repo.get())
```
輸出 `BLOCK`;`MutableStateFlow(HomeState())` 同樣被擋。除非程式剛好有 `.copy(` 可以引。

## F12 反例太容易擋,樣式放寬後自測仍全綠

severity: major
blocking: 是

引句:「// === bad UI-66 padding 與 background 順序誤解」

我在複本上做變異,把 D-34 主樣式放寬成 `.clickable\b` 加 `.padding\b`(順序檢查整個拿掉)。`check.py --catalog-only` 仍回「型錄問題 0 個」,因為這個反例沒有 `.clickable`,放寬後照樣被第一條擋掉。

D-23 放寬成 `\bResponse\b` 也沒被發現,因為反例是 `): User`,這種反例太遠、碰不到放寬的地方。D-1、D-8、D-10、D-16、D-21、D-47 放寬後都有紅,只有 D-34 與 D-23 抓不到。意思是自測沒證明 D-34 主樣式真的在管順序。

## F13 `(無)` 的列在推送前等於放行,不是「交盲判」

severity: minor
blocking: 否

引句:「反例(對應檢查列的壞寫法)要擋;做不到的那一段改寫(無)交盲判。」

`scripts/lumos` 裡沒有盲判實作(`grep -c "blind-judge\|blind_judge" scripts/lumos` 是 0)。`_kt_sit_row_check` 對樣式為 `(無)` 的寫法直接 `return None`。計劃 REVISIT 2026-11-20 也承認「上線前情境段只核表態對程式」,所以和計劃的分期一致,但「交盲判」目前沒有人接。

實測:
- **D-20 整列是 `(無)`。** `Thread.sleep` 那段答 D-20 `applies:true, main`,對 D-20 沒有任何問題(只有同段的 D-55 報錯)。
- **D-13、D-15、D-39、D-45 同理。**
- **主樣式有、例外是 `(無)` 且不是「(換列)」的列**(D-16、D-23、D-22、D-24、D-25 等),壞寫法答 `alt` 就放行。例如 `Channel<Event>(Channel.UNLIMITED)` 答 D-16 alt,D-16 沒有問題。
- **D-32 的主樣式是 `(無)`。** 壞寫法 `LaunchedEffect(viewModel, onClick, list)` 答 main 也放行。

自測的「反例要擋」對這些答法不成立,只對有樣式的那個寫法成立。建議在 `(無)` 的列加提醒,或在盲判上線前把「alt 是 `(無)` 且不是換列」這件事講在文件裡。

總結:最嚴重是 D-1、D-16、D-23、D-24、D-47、D-42、D-34 等列擋掉型錄自己的標準寫法或常見變體,另有 D-1 的立刻 await 壞寫法與 D-34/D-23 的反例放寬後自測不紅;共 11 條 major(F1、F2、F3、F5 至 F12),會擋 11 條。F4、F13 為 minor 不擋。
