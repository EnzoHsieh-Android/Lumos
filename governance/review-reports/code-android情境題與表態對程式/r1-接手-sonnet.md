severity: major

審查方式:我把 `scripts/lumos` 當模組載入,在臨時 git repo 裡呼叫 `_kt_situation_segments` 與 `_kt_sit_row_check`,用真的段與真的證據樣式跑。repo 沒有被改動,臨時目錄已刪。

整體情況:56 列的樣式全部能編譯,條數也對。型錄末尾寫的「主 `(無)` 8 列、例外 `(無)` 31 列、兩段都 `(無)` 5 列」我重算過,數字相符。

我把 56 列的 `標準寫法` 欄與「壞寫法形狀」欄(用各列 `對應檢查` 去查)逐條比對。以下問題都已跑出來。

F1
引句:`主:`\.clickable\b` `\.clickable\s*\((?:[^()]\|\([^()]*\))*\)\s*\.padding\s*\(``
file: `skills/kotlin-idioms/checks-catalog.md:D-34 列`
severity: major
blocking: 是
D-34 的樣式要求 `.clickable(` 後面接圓括號。型錄自己在 D-52 的標準寫法就用尾隨 lambda 寫法 `Modifier.clickable { … }`,這種標準寫法被擋下。括號只容許一層巢狀,`clickable(onClick = { vm.go(item(1)) })` 也被擋。例外寫法的樣式同樣只認圓括號。
最小重現(臨時 repo,`Row1` 是函式):
- `Box(Modifier.clickable { onClick() }.padding(8.dp))` 以 D-34、main、指到 `.clickable` 那行,得到「證據樣式對不上…不在段材料」。
- `Modifier.clickable(onClick = { vm.go(item(1)) }).padding(8.dp)` 同樣被擋。
- 例外寫法 `Modifier.padding(8.dp).clickable { onClick() }` 以 alt 答也被擋。
- 圓括號版本 `Modifier.clickable(onClick = onClick).padding(8.dp)` 則通過。
實際後果:這個擋沒有出口,見 F7。

F2
引句:`主:`\bResponse<Unit>` `\.isSuccessful\b`;例外:(無)`
file: `skills/kotlin-idioms/checks-catalog.md:D-23 列`
severity: major
blocking: 是
D-23 的標準寫法是兩件事:介面宣告 `Response<Unit>`,呼叫端用 `.isSuccessful` 判成敗。這兩處通常在不同檔案、不同函式。第二條樣式要在「包住那段程式的函式」裡找,所以只改介面宣告就被擋。
最小重現:只新增 `interface Api { @DELETE("users/{id}") suspend fun delete(@Path("id") id: Long): Response<Unit> }`,以 D-23、main、指到 `Response<Unit>` 那行,得到「第二條 `\.isSuccessful\b` 不在段材料(第 2 到 5 行)」。

F3
引句:`\bcoerceInputValues\b\|@EncodeDefault\b\|\bencodeDefaults\b\|\bval\s+\w+\s*:[^=,)]*=` `@Serializable\b``
file: `skills/kotlin-idioms/checks-catalog.md:D-47 列`
severity: major
blocking: 是
D-47 標準寫法的第二句是單獨一行 `val format = Json { coerceInputValues = true }`(`encodeDefaults = true` 同理)。樣式卻要求同一段材料裡有 `@Serializable`,它在另一個宣告上。
最小重現:檔內只有 `val format = Json { coerceInputValues = true }`,以 D-47、main 答,得到「`@Serializable\b` 不在段材料(第 2 到 4 行)」。
另一個副作用:最後一個選項 `val x: T =` 幾乎等於任何有型別的屬性初始化。

F4
引句:`主:`\bcoroutineScope\b` `\btry\s*\{` `\bcatch\s*\(`;例外:(無)`
file: `skills/kotlin-idioms/checks-catalog.md:D-8 列`
severity: major
blocking: 是
D-8 標準寫法的重點是「try 包在 `coroutineScope` 外面」,樣式卻只要求三個字都出現,沒有要求順序。
這一列對應的 CO-8 壞寫法是 `coroutineScope { val d = async { fail() }; try { d.await() } catch (e: Exception) {} }`,三條樣式全中。
最小重現:`suspend fun load(): Ui = coroutineScope { val d = async { api.fail() }; try { Ui(d.await()) } catch (e: Exception) { Ui.Error } }`,以 D-8、main、指到 `coroutineScope` 那行,檢查回 None(放行)。壞寫法與標準寫法的結果相同。
可補的字面特徵:標準寫法的 `try {` 緊接 `coroutineScope`,可以寫成 `\btry\s*\{\s*coroutineScope\b`。

F5
引句:`\bcallTimeout\(\|\bHttpTimeout\b\|\bwithTimeout(?:OrNull)?\(`
file: `skills/kotlin-idioms/checks-catalog.md:D-10 列`
severity: major
blocking: 是
D-10 的標準寫法只列 `withTimeoutOrNull`,樣式的 `(?:OrNull)?` 卻把裸 `withTimeout(` 也收進來。型錄把它列為壞寫法:API-32 是 `launch { withTimeout(5_000) { fetch() } }`,CO-14 是 `val r = withTimeout(1000) { openResource() }`。這是樣式教了型錄沒寫的寫法。
最小重現:CO-14 那行,以 D-10、main、指到 `withTimeout` 那行,檢查回 None(放行)。
同類問題還有:
- D-16 的樣式含 `\.buffer\(` 與 `\btrySend\(`。FLOW-30 壞寫法 `.buffer(Channel.UNLIMITED)` 與 FLOW-31 壞寫法 `trySend(v)` 不檢查回傳值,都全中。重現:`src.buffer(Channel.UNLIMITED)` 以 D-16、main 答,放行。
- D-32 的 `\bLaunchedEffect\s*\(` 讓 UI-35 壞寫法 `LaunchedEffect(viewModel, onClick, list)` 放行。
- D-14 的 `\bgetBackStackEntry\(` 讓 ARCH-37 壞寫法放行。
- D-13 的 `\brememberSaveable\b` 讓 STATE-18 壞寫法 `rememberSaveable { bigObject }` 放行。
- D-45 的 `\bworkDataOf\(` 讓 DATA-39 壞寫法 `workDataOf("list" to bigJson)` 放行。
後三類(D-14、D-13、D-45)偏語意,正規式難分;我沒逐條補重現。D-16 這類有字面特徵可補,例如 `\.buffer\((?!\s*(?:Channel\.)?UNLIMITED)`。

F6
引句:`\bStandardTestDispatcher\(` `\brunCurrent\(\)\|\badvanceTimeBy\(``
file: `skills/kotlin-idioms/checks-catalog.md:D-21 列`
severity: major
blocking: 是
常見的 JUnit 寫法是把 `private val dispatcher = StandardTestDispatcher()` 放在類別屬性,測試函式用 `runTest(dispatcher) { runCurrent() }`。這種標準寫法在第二條樣式上被擋,和 F2、F3 是同一根因:`_mat` 只取包住「第一個命中行」的那個宣告,跨宣告的兩條樣式永遠湊不齊。
最小重現:
- 兩處新增,一處 `private val dispatcher = StandardTestDispatcher()`,一處 `fun loads() = runTest(dispatcher) { vm.load(); runCurrent(); advanceTimeBy(500) }`。
- 屬性那段以 D-21、main 答,得到「`\brunCurrent\(\)|\badvanceTimeBy\(` 不在段材料(第 3 到 5 行)」。
- 測試函式那段指到 `runCurrent` 那行,得到「第一條 `\bStandardTestDispatcher\(` 不在 evidence 那一行」。
- 兩段都過不了,只剩答 `applies:false`,那是在說謊。
另外,Systems 筆記說材料是「包住它的函式」,實際是「最近的頂層或類別層宣告」(可能是類別或屬性),找不到或超過 120 行時退成前後各 20 行。這句和程式不符,但失敗場景由 F2、F3、F6 承擔,不另立一條。

F7
引句:`這題不收 na、todo、tension(要人裁的出口是段放行,還沒上線)`
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md`,`Systems/pitfalls-code-loop.md`(新寫的 WHY 行)
severity: major
blocking: 是
這次只做範圍 1–3,但上面 F1 到 F6 的誤擋沒有出口。
- 計劃範圍 3 寫「機器判不了、要人裁的出口是範圍 5 的段放行」,而範圍 5 還沒做。程式的 docstring 自己承認「還沒上線」。
- Systems 兩篇新 WHY 與〈Android 寫法情境題〉一節,都沒有寫「目前被擋就沒有出口」。
- 計劃的 REVISIT 只寫 `上線前情境段只核表態對程式`,沒說這段期間誤擋會擋死推送。
- 實際出路只有三條:改型錄、答 `applies:false` 說謊、或把整個專案的 `stack_questions.gate` 調成 off。
- 三者都沒有寫進筆記,而 F1 到 F6 說明誤擋是真的會發生。
建議:
- 在 Systems〈Android 寫法情境題〉明寫「範圍 5 前的出口」。
- 計劃 REVISIT 加一句「到 2026-11-20 前,範圍 5 沒做就先限縮觸發字或把證據樣式降為 `(無)`」。

F8
引句:`"switch": ev["alt"] is None and re.search(_KT_DT_SWITCH_RE, get("不適用時")) is not None}, None`
file: `scripts/lumos`(`_kt_dt_row`)
severity: minor
blocking: 否
「換列的列」靠不適用時欄的中文用語加上「例外樣式為 `(無)`」推出,現在是 D-1、D-2、D-8、D-9、D-50 共 5 列。
- check.py 沒有驗證這個推論,測試只釘住 D-1。
- 型錄把「見下一列」改個說法,該列就悄悄變回「可選 alt、完全不核」。
- D-25 的「見既有「背壓」列」因為中間有「既有」兩字沒被認成換列,這可能是有意的,但筆記沒講認法。
- Systems 只寫「換到別列的列不准選例外寫法」,沒寫怎麼認。
建議:在型錄加明確標記,或讓格式檢查釘住這 5 列。

F9
引句:`實作分三次:第一次範圍 1–3(2026-11-06)`
file: `docs/lumos-toolchain-knowledge/Projects/Android寫法語意情境表態與盲判_計劃.md`
severity: minor
blocking: 否
三處和計劃對不上,筆記沒有同步:
- 觸發字判斷:計劃範圍 2 仍寫 `_stack_applicability` 只判觸發字有沒有中,實作改成 `_kt_situation_apply` 看切不切得出段來覆蓋。這在 Systems 有寫,計劃本文沒改。
- 改檔前推播只做逐行粗判:Systems 有 REVISIT:2026-11-20,寫得實在,影響只是推播多亮、不影響閘。
- 整字比對:程式沒有改,但沒有專門測試。我在 `scripts/test_lumos.py` 沒找到任何針對 `_kt_trigger_re` 的測試,但我沒發現具體失敗場景。
計劃的審計修正紀錄只有一行,沒有列這些偏離。下個接手人讀計劃做範圍 4 的盲判材料,會以為適用性仍是逐行觸發字。

F10
引句:`資料層自己 `withContext(ioDispatcher) { … }`(dispatcher 從建構子注入)`
file: `skills/kotlin-idioms/checks-catalog.md:D-20 列`
severity: minor
blocking: 否
D-20 的第一條樣式 `\bwithContext\(\s*\w*[dD]ispatcher\s*\)` 依變數名稱認。型錄 CO-1、CO-5 的標準寫法用 `withContext(io)`,依這個名字寫就被擋。
重現:`class Repo(private val io: CoroutineDispatcher = Dispatchers.IO) { suspend fun load() = withContext(io) {…} }`,以 D-20、main 答,得到「第一條…不在 evidence 那一行」。
`withContext(dispatchers.io)` 這種包裝器寫法也過不了,但那不是型錄寫過的寫法,不算。
D-20 列自己的寫法 `ioDispatcher` 是通過的,所以只標 minor。

根因與建議(一條,不另立 finding):
- F1 到 F6、F10 是同一個漏洞。型錄格式檢查只驗樣式能編譯,沒有驗「那一列自己的 `標準寫法` 範例是否中 `主:`、`不適用時` 範例是否中 `例外:`、對應檢查的壞寫法是否不中」。
- 補一支測試,把每列反引號範例餵給自己的樣式就能擋。我的重現腳本就是這個做法,約 30 行。
- 這類一次修,可以同時避免下一輪再補單點。

沒有找到問題的部分:
- 其餘 40 多列(含 D-1、D-3、D-5、D-9、D-11、D-22、D-25、D-35、D-36、D-44、D-56)的標準寫法範例都比中。
- 證據樣式裡沒有發現 ReDoS(D-34 的巢狀量詞各分支開頭字元互斥)。
- 筆記對「型錄讀不到就不出題、`pitfalls --diff` 與 `code-loop check` 各印一行提醒、不擋」「`situation_segments` JSON 欄」「段併法(行號差不超過 4、同 hunk、同宣告、40 行上限)」的描述,都和程式行為一致。

總結:最嚴重是證據樣式擋掉標準寫法本身(D-34 尾隨 lambda、D-23、D-47、D-21)與放過壞寫法(D-8、D-10、D-16),再加上沒有出口的文件缺口,會擋 7 條。

相關檔案:
- Diff:`/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence/governance/review-reports/code-android情境題與表態對程式/r1-snapshot-甲丙.patch`
- 型錄:`/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence/skills/kotlin-idioms/checks-catalog.md`
- 重現腳本(僅草稿,未動 repo):`/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/5b6d202a-9139-47f7-b6b9-deb227707ba4/scratchpad/t.py`、`t2.py`
