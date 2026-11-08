severity: major

固定席逐條判:計劃宣稱為 `[[Systems/kotlin規則包]]` 管 5 支檔,而該節點沒有 KEY、沒有合約行、沒有掛計劃。照字面實作不會破壞它的合約,判不影響。型錄自檢(`check.py`)的統計與目錄規則會被牽動,見下面 F2、F3。

**第一節 範圍 1(四條新規則)**

severity: major
blocking: 是
- 段落:範圍 1 的 ARCH-59 列,以及該列的「ARCH-59 的『已知非限定詞註解』清單寫死在規則裡;清單外的註解一律當成限定詞(寧可少報)」。
- 問題:「寧可少報」只對「被報的那個函式 A」成立。A 身上若有清單外的註解(`@Suppress`、`@OptIn`),A 會被當成已有限定詞,所以少報。
  - 另一個函式 B(對照組)身上若有清單外的註解,B 就被當成有限定詞,A 會被報。這會多報。
  - Hilt/Dagger 的多重綁定註解 `@IntoSet`、`@IntoMap`、`@ElementsIntoSet`、`@ClassKey`、`@StringKey` 都不在清單內。
  - `@Provides @IntoSet fun b(): Foo` 加上 `@Provides fun a(): Foo` 是合法寫法,因為多重綁定的鍵不同於一般綁定。照規格字面,A 會被報成「少了限定詞」。
  - 清單列舉的是「Provides、Binds、Singleton、Reusable、JvmStatic、…Scoped」,沒有多重綁定家族。
  - 「少報」的方向宣稱因此不成立,會推高誤報率,直接傷到升級條件「誤報 ≤10%」。
- 修法方向:清單加入多重綁定註解並寫進壞例好例,或「對照組 B」也套用同一份非限定詞清單、清單外的註解一律不當成對照組。
- 引句:「清單外的註解一律當成限定詞(寧可少報)」
- 佐證:規格範圍 1 的 ARCH-59 列;預期值表沒有 `@IntoSet` 或 `@IntoMap` 的好例。
- 佐證:型錄 ARCH-59 的壞寫法只寫「一個 `@AuthClient`、另一個沒加」,沒涵蓋多重綁定。file: `skills/kotlin-idioms/checks-catalog.md:503`

severity: major
blocking: 是
- 段落:範圍 4 第 3 點「過升級條件的規則搬到 `rules/`、等級改 error」,加上範圍 1 的「API-2 另放一份 `review-fp-` 樣本」。
- 問題:`check.py` 只對 `rules-review/` 與 `rules-unwired/` 的規則豁免 `review-fp-` 開頭的好例樣本,不算好例誤報。API-2 的 Play services `Task.await()` 是已知誤報,樣本內預期必留。
  - API-2 若過升級條件被搬到 `rules/`,`review-fp-` 樣本會被當成好例誤報。型錄自檢和 `t_kotlin_rulepack_samples` 都會紅。
  - 規格沒寫搬動時要拿掉樣本、要降級,或要調整豁免。
  - 更根本的問題是:已知單檔無法排除的誤報類,與「error 等級、會擋推送」互相矛盾。這會讓 RETIRE-IF 第二句的 30% 放行門檻很快被觸發。
  - 規格若要保留這個搬動路徑,就要先寫 API-2 搬到 `rules/` 時的處置,例如只准留在 `rules-unwired/` 或 `rules-hints/`。
- 引句:「API-2 另放一份 `review-fp-` 樣本,記下 Play services `Task.await()` 這個已知誤報。」
- 佐證:`review_ids` 只含 `rules-review` 與 `rules-unwired`。file: `configs/ast-grep/kotlin-android/check.py:1038`
- 佐證:豁免邏輯。file: `configs/ast-grep/kotlin-android/check.py:1044`
- 佐證:`REVIEW_FP_PREFIX` 的定義。file: `configs/ast-grep/kotlin-android/check.py:31`

severity: minor
blocking: 否
- 段落:範圍 1 的 UI-33 列,對照型錄 UI-33。
- 問題:規則形狀是「`onDispose { }` 是空的」就報,不看 `DisposableEffect` 裡有沒有註冊呼叫。型錄 UI-33「情境怎麼認」寫的是「DisposableEffect 只有空 onDispose 且無註冊呼叫」。
  - 規格自己的預期值表也把 `DisposableEffect(Unit) { log("x"); onDispose { } }` 當成要報。
  - 我實跑:`val r = reg(); onDispose { }` 與 `onDispose { /* nothing */ }` 都會被報。
  - 前者通常是真漏洩(註冊了沒解除),卻會收到「改用 LaunchedEffect」的訊息,建議方向反了。
  - 規格沒說訊息怎麼處理有註冊呼叫的情形,也沒說型錄的形狀描述是否同步改。
- 引句:「DisposableEffect(...) { … } 裡的 onDispose { } 是空的」
- 佐證:型錄「無註冊呼叫」的敘述。file: `skills/kotlin-idioms/checks-catalog.md:360`

severity: minor
blocking: 否
- 段落:範圍 1 的 ARCH-62 列,以及天花板。
- 問題:規則只認 `EntryPointAccessors.fromX($$$, I::class.java)` 的 `::class.java` 形式,實務上的漏報與誤報來源沒寫。
  - Kotlin 的 reified 寫法 `EntryPointAccessors.fromApplication<I>(ctx)` 完全不報,天花板沒列。
  - `@InstallIn(ActivityComponent::class, SingletonComponent::class)` 這種多元件安裝,規格沒說「只要含對應元件就不報」。
  - `fromView` 只對 `ViewComponent`,但 `@WithFragmentBindings` 的 View 走 `ViewWithFragmentComponent`,會誤報。這一條我沒對照 Hilt 原始碼核實,請投稿者查證。
  - 預期值表只有 `fromApplication` 兩例,`fromActivity`、`fromFragment`、`fromView` 的對應表沒有任何預期值例。對應表被改壞時 S2 抓不到。
- 引句:「fromApplication↔SingletonComponent、fromActivity↔ActivityComponent、fromFragment↔FragmentComponent、fromView↔ViewComponent」
- 佐證:預期值表只有兩例。見 snapshot 預期值表 S2 的 ARCH-62 三列。
- 佐證:我嘗試用 `$I` 在 `inside`/`has` 之間跨節點共用的草稿規則,在 0.51.1 沒有匹配。這是我自己寫法的限制,不能推翻規格的「草稿試跑都過」,但規格沒附規則原文,請投稿者在設計審補上。

**第二節 範圍 2、5(型錄與統計、測試)**

severity: minor
blocking: 否
- 段落:範圍 5 最後一點與範圍 2。
- 問題:規格沒提 `_KT_STATS_MUTATIONS` 裡另一處寫死的「待查證:51 列」。
  - 「待查證列著主表已解決的 DATA-27」那條改壞案例,把 `- 待查證:51 列` 換成 `52 列`。
  - 〈待查證〉減 1 之後,真型錄是 50 列,這個 `replace` 會對不上、改壞複本沒被改動。該案例要跟著改成 50→51,規格只提 `_KT_STATS_LINES` 與 API-2 錨點。
  - API-2 的通電批次要不要保留「當下推相關列=批二」,規格寫的是整格改成「告警帶寫法=未接(…)」,語意不清。
- 引句:「待查證統計那支用 `| API-2 | IJ:「Use awaitAll()` 當改壞錨點的案例,API-2 拿掉後換一列仍在〈待查證〉的當錨點」
- 佐證:寫死的 `51 列`。file: `scripts/test_lumos.py:129636`(同段相鄰行)
- 佐證:`_KT_STATS_LINES` 的待查證一行。file: `scripts/test_lumos.py:129615`

severity: minor
blocking: 否
- 段落:範圍 5 的 `t_kotlin_shape_rows_rules` 與 S5。
- 問題:S5 與測試描述把「規則 id 在計劃寫的目錄」寫死。
  - 範圍 4 又規定量完過關的規則搬到 `rules/`。搬動後這支測試或型錄會與測試不同步。
  - 測試先寫死 `rules-unwired/`,搬動時要改測試,但規格沒寫這步。
  - 這會在搬動提交紅一次,不是長期缺陷。
- 引句:「同時驗四列型錄現成規則欄的規則 id 在規則包裡存在、在計劃寫的目錄」
- 佐證:`_DIR_SEVERITY` 允許 hint 放 `rules-unwired/`,但 `rules/` 只收 error/warning。file: `configs/ast-grep/kotlin-android/check.py:29`

**第三節 實驗**

severity: minor
blocking: 否
- 段落:實驗最後一點(GitHub 程式碼搜尋粗估)與範圍 4 的升級條件。
- 問題:「命中數應能到 20 以上」的依據是文字搜尋的檔案數,不是壞寫法形狀的命中數。
  - `EntryPointAccessors.fromApplication` 約 7936 支檔是呼叫點總數。壞寫法要求同檔的 `@InstallIn` 元件與 fromX 不對應,真命中近乎零,因為對不上元件的 entry point 執行時就崩潰。
  - ARCH-59 的「同檔有 `@Provides` 與 `@Named`」約 10432 也不是壞寫法形狀(同型別、一個有一個沒有)。
  - 這兩條幾乎必然卡在「命中 ≥20」。規格有「沒過就留在 `rules-unwired/`」的出口,所以不阻擋,但「應能到 20 以上」這句估計不可靠,不能當作排程或收益依據。
- 引句:「命中數應能到 20 以上。」
- 佐證:snapshot 實驗最後一點的數字來源是文字搜尋,不是規則命中。

**其餘各節**

已讀,無 finding:用詞、不做、依據來源、實務隱患(守衛面、效能、金流、對外、不可逆各類)、驗收條款的條款編號與標記形式、回退、天花板。

總結:最嚴重 severity 為 major,blocking 共 2 條(ARCH-59 清單方向、API-2 搬動路徑與 `review-fp-` 豁免)。

我建過的路徑都已清掉。`/tmp/lumos-seat-work/android形狀列補規則/通才-sonnet/` 現在是空目錄,是我自己建的,留著未刪。
