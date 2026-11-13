severity: major

我讀了 r3-snapshot.md 全文和 r2-intake.md,實跑了 1.10.2 的 `.klib.api` 與 `.api`、`scripts/lumos`、`check.py`,並在 Now in Android 提交 `2982e63c` 上量過。本機沒有 ast-grep,`--sg` 的部分是讀程式推論。實驗檔在 `/tmp/lumos-seat-work/情境決策點窮舉與壞寫法要叫得出/邊界-sonnet/`,清理請編排者收貨後處理。

## 前兩輪修復驗收

| 項目 | 結果 |
|---|---|
| 184 個有片段單位、11 對無片段 | 屬實。真型錄用 `main_rows` 重數剛好 184 與 11。 |
| klib 標了平台的名稱丟 4 個 | 屬實。丟的是 `asCoroutineDispatcher`、`asPromise`、`awaitAnimationFrame`、`promise`。 |
| JVM 補來源去 `-` 後 7 字元的雜湊後綴 | 屬實。1.10.2 的 `.api` 只出現長度 7 的後綴與 `-impl`。 |
| r2 的 JVM 補來源修復 | 沒修乾淨,見 F3。 |
| r2 的 `Dispatchers.IO` 可見寫法 | 規則導不出來,見 F2。 |
| r2 加的 `TEST-` 兩個路徑 | 反而掩蓋了單元測試的洞,見 F1。 |

## Findings

### F1 `TEST-` 單元「任一路徑叫得出就算」,把真正寫在 `src/test` 的壞寫法判成叫得出
severity: major
blocking: 是。這正是本案要消滅的「默默放行」,而且 12 個 TEST 片段單位裡有 8 個被判成「不用進表」。
- 位置:〈用詞〉叫得出。
- 引句:「任一個路徑切出的段的候選列含那一列就算叫得出」
- 佐證:我用真型錄、真 `scripts/lumos`、`_stack_changed_ok` 與 `_kt_sit_text_segments`,把每個片段分別放在 `app/src/test/...` 與 `app/src/androidTest/...` 實跑。
  - `src/test` 路徑一律被 `_PITFALL_DIFF_TEST_PAT` 的 `/test/` 擋掉,12 個 TEST 片段單位全部切不出。
  - `androidTest` 路徑因為資料夾名是 `androidTest`、不是 `test`,不被擋。
  - 結果:D-21 TEST-15 `UnconfinedTestDispatcher`、D-49 TEST-6 與 TEST-14 的 `runTest {…}`、D-50 TEST-18 的 `flow.test { awaitItem() }` 與 TEST-19 `awaitItem()`,在 `src/test` 都切不出,在 `androidTest` 切得出。
  - D-21、D-49、D-50 講的是 JVM 單元測試,這些寫法平常就寫在 `src/test`。本案卻把它們全記成「叫得出」,不進〈叫不出的壞寫法〉。
  - 另外 D-51 TEST-30 的 `registerIdlingResource`、`waitUntil` 與 TEST-32 的 `onNodeWithText("子文字")` 屬於儀器測試,放 `androidTest` 判叫得出是對的,不受影響。
- 建議:每個 `TEST-` 對應檢查事先指定它「常駐的」路徑(單元測試用 `src/test`,儀器測試用 `androidTest`),只用常駐路徑判叫得出。常駐路徑是 `src/test` 的,全部進表。

### F2 「可見寫法」的定義導不出 `Dispatchers.IO`,S1 的停用字案例做不出來;列舉項與屬性也缺可見寫法
severity: major
blocking: 是。r2 為停用字加的專門核對在 1.10.2 上根本不會觸發,`IO` 標 `無決策` 會直接過。
- 位置:〈用詞〉公開名稱「可見寫法」,範圍 2 的停用字核對,S1 與預期值表的 `IO` 列。
- 引句:「可見寫法是 `外層類別.名稱`」
- 引句:「例 `Dispatchers.IO` 等於 `IO` 的可見寫法」
- 佐證:
  - klib 的 `Dispatchers` object(`k.api` 第 681-690 行)只有 `Default`、`Main`、`Unconfined`、`injectMain`。
  - `IO` 在 klib 是標了 `// Targets: [native]` 的頂層擴充屬性 `final val kotlinx.coroutines/IO`,getter 長 `final fun (kotlinx.coroutines/Dispatchers).<get-IO>()`。它不縮排在任何 object 底下。
  - JVM 的 `getIO` 是 `Dispatchers` 類別的成員,而規則明說成員不從 JVM 清單補。
  - 所以照規則抽,`IO` 沒有可見寫法,「`Dispatchers.IO` 等於 `IO` 的可見寫法」永遠不成立,S1 那一列做不出來。
- 同根因還有列舉項:`CoroutineStart.UNDISPATCHED`(〈天花板〉6 自己舉的例子)、`BufferOverflow.DROP_OLDEST`、`SharingCommand.STOP` 是 `enum entry`,不是 object 成員,沒有可見寫法。
  - 作者若想用精準的 `CoroutineStart.LAZY` 當觸發字,範圍 1 的 `D-n` 核對會報「搜不到」,逼他改用裸字 `LAZY`、`DEFAULT`、`START`,這些字太常見。
  - 反過來,有人加了 `BufferOverflow.DROP_OLDEST` 這種觸發字,反向同步搜不到名稱 `DROP_OLDEST`,它標 `無決策` 也不被抓。
  - `Dispatchers.Main.immediate` 同理。
- 建議:可見寫法補上「列舉項:`列舉類別.項名`」。`IO` 這種「klib 頂層擴充掛在某 object 上」的,或直接把 `Dispatchers.IO` 手寫進一張小例外表,並在自檢裡驗它存在。

### F3 JVM 補來源仍然把頂層讀取函式與 `@JvmName` 改名函式補進表,r2 的修復沒到位
severity: major
blocking: 是。這是 r2 邊界席 F1 的原症狀(`getRECOVER_STACK_TRACES`、`flowCombine`、`debounceDuration`),r3 只擋了「還原」,沒擋「原樣收進來」。
- 位置:〈用詞〉公開名稱「補來源 JVM 清單」。
- 引句:「門面類別裡的 `public static final fun` 名稱」
- 引句:「成員與讀取函式不從 JVM 清單補」
- 佐證:我照規則抽 1.10.2 `.api` 的 `…Kt` 門面,排除 synthetic、`$`、`-impl`、底線、internal 與 debug 之後,klib 沒有的函式名稱有:`getCoroutineContext`、`getDEFAULT_CONCURRENCY`、`getDefaultDelay`、`getJob`、`getRECOVER_STACK_TRACES`、`flowCombine`、`flowCombineTransform`、`debounceDuration`、`from`(`asCoroutineDispatcher` 的 JVM 名)、`isIoDispatcherThread`、`isPresent`、`ensurePresent`、`cancelFutureOnCancellation`、`processNextEventInCurrentThread`、`runSingleTaskFromCurrentSystemDispatcher` 等。
  - 這些名稱使用者不會打(`getJob` 是頂層屬性 `job` 的 getter,`flowCombine` 是 `combine` 的 `@JvmName`),全部進表,每個都要有人分類。
  - 規則的「讀取函式」例外只寫給成員。S1 只驗 `isActive` 不多出 `active`,驗不到這類頂層 getter。
  - 這也是補來源唯一的實質貢獻(klib 已涵蓋其餘),價值低、噪音高。
- 建議:補來源跳過名稱以 `get`/`is`/`set` 加大寫開頭的,並跳過 klib 已有同簡名者的 `@JvmName` 改名。或者直接不補,把 JVM 專屬的 `actor`、`future`、`runInterruptible`、`ticker`、`asExecutor`、`asContextElement` 這些真名手列進一張小表。

### F4 klib 逐行解析沒講「巢狀泛型」與 `fun interface`,照字面實作會產出垃圾名稱與漏名,而且自檢看不出
severity: major
blocking: 是。表是由抽法自己產生的,「表與母體對得上」的核對自己對自己,抽錯不會紅;錨點只驗 5 個名字,擋不住。
- 位置:〈用詞〉公開名稱的 klib 抽法。
- 引句:「開頭的型別參數 `<…>`(只在宣告字之後、名稱之前那一段)」
- 引句:「每個宣告行(`fun`、`val`、`var`、`const val`、`class`、`interface`、`object`、`enum entry`)」
- 引句:「看那一段最近的類別標頭的完整名稱」
- 佐證(我實作了兩種讀法,對 1.10.2 的 klib 比對):
  - 巢狀泛型:`k.api` 第 189 行 `<#A: kotlin/Throwable & kotlinx.coroutines/CopyableThrowable<#A>>`,第 973-982 行 `<#B: kotlin.collections/MutableCollection<in #A>>`。用非貪婪的 `<…>` 去頭,名稱會抽成字面 `>`。
    - 掉的名稱:`CopyableThrowable`、`filterNotNullTo`、`toCollection`、`toMap`、`toChannel`。
    - 多出的名稱:`>`。
    - 規則沒寫要配對括號。
  - `fun interface`:第 78、82、95、99 行是 `abstract fun interface …`,宣告字清單與修飾字都沒有 `fun interface`。
    - 若按「宣告字 `fun`」處理,`FlowCollector`、`SharingStarted`、`DisposableHandle`、`Runnable` 全漏,多出一個叫 `interface` 的名稱。
    - `SharingStarted` 漏掉還會讓 `Lazily` 的可見寫法 `SharingStarted.Lazily` 掛錯外層,因為它的 `Companion` 掛在 `SharingStarted` 底下。
  - 類別標頭範圍:規則沒說何時結束(`}` 還是縮排)。
    - 若解讀成「往回看最近一個標頭」,內部類 `ChannelFlow`(`flow.internal`)之後的公開類 `AbstractFlow`、`SelectBuilderImpl` 被誤丟(我實測的 naive 讀法只剩 434,正確讀法 436)。
    - 若對整個標頭行做 `internal` 子字串比對,`CancellableContinuationImpl`(只是父型別含 `kotlinx.coroutines.internal/`,自己套件公開)連 31 行成員被誤丟。
- 建議:
  - 寫明型別參數要配對 `<>`。
  - `fun interface` 要列入宣告字。
  - 用 `}` 或縮排結束標頭。
  - 排除只看「名稱自己的套件路徑」。
  - 在 S1 加一組暫存母體案例:巢狀泛型行、`fun interface` 行、內部類之後的公開類。

### F5 `<無片段>` 單位用 `規則`/`範本` 改由時,沒有可核對的片段,規則沒定義;4 對剛好有範本接電
severity: major
blocking: 是。「改由宣稱擋得住其實擋不住」是 r1、r2 都判過 major 的同一類洞,`<無片段>` 單位正好繞開了片段層級驗證。
- 位置:〈用詞〉改由,〈範圍〉3 與 S2。
- 引句:「片段要出現在 `samples/bad/<id>/` 的某支壞例檔裡」
- 引句:「`<無片段>` 單位不准用。」
- 佐證:
  - 11 個 `<無片段>` 單位的片段欄是字面 `<無片段>`。`規則`/`範本` 的核對都要求片段出現在壞例檔或範本圍欄,`<無片段>` 沒有東西可找。
  - 規則沒說這種單位可不可以用 `規則`/`範本`。「不得用不是寫法」只擋了一種,實作者要嘛永遠紅、要嘛空洞通過。
  - 其中 4 對真型錄標了範本接電:D-35/UI-52 `範本 T9`、D-54/TEST-35 `範本 T10`、D-58/UI-110 `範本 T9`、D-59/DATA-65 `範本 T6`。它們被迫只能寫 `代碼審`,與 RETIRE-IF 第二條(代碼審超過一半)的比例也會失真。
- 建議:明寫 `<無片段>` 只准 `代碼審`,或者「`規則`/`範本` 改查壞寫法欄那段文字有沒有出現在小節標題」之類另一種核對。並承認這 4 對只能算代碼審。

### F6 `_kt_sit_path_ok(rel)` 的簽名少了 `skip`,「行為不變」沒有證明
severity: major
blocking: 是。規格要求「抽出後行為不變」,但抽出的函式簽名放不下原有的一個條件,既有測試也驗不到。
- 位置:〈用詞〉路徑篩選,預期值表 S6。
- 引句:「本案把它抽成 scripts/lumos 的一支小函式 `_kt_sit_path_ok(rel)`(新增)」
- 引句:「`_kt_situation_segments` 改呼叫它、行為不變」
- 佐證:`_kt_situation_segments` 現在的篩選是 `not _PITFALL_DIFF_TEST_PAT.search(rel) and _stack_changed_ok(rel, skip) and _kt_sit_may_hit(...)`。
  - `file: `scripts/lumos:39941`` 到 `scripts/lumos:39969`(三個呼叫端都傳 `skip=_vendored_skip(…)`:`scripts/lumos:74296`、`scripts/lumos:74779`、`scripts/lumos:40012`)。
  - `_stack_changed_ok` 還含 `skip`(消費專案裡原封不動的工具檔)、`governance/review-reports/` 前綴、`_RULEPACK_SAMPLE_RE`、簿記檔。
  - 單參數函式要嘛丟掉 `skip`,讓消費專案的工具檔開始出情境段(回歸),要嘛函式外還留一半條件(「反查呼叫同一支」落空)。
  - 既有測試(`scripts/test_lumos.py:131562`)只拿 `skip` 當快取鍵,不驗行為。S6 的預期值表只列兩個路徑,也不涵蓋 `skip`。
- 建議:簽名寫成 `_kt_sit_path_ok(rel, skip=frozenset())`,S6 補一條「`skip` 命中的檔不出段」。

### F7 預期值表 S2 的 TEST-29 例子不是壞寫法片段
severity: minor
blocking: 否。不影響機制,但驗收案例照字面做不出來。
- 位置:預期值表 S2 第三列與驗收條款 S2。
- 引句:「TEST-29 片段 `composeTestRule.mainClock.autoAdvance = false`」
- 佐證:
  - `composeTestRule.mainClock.autoAdvance = false` 在型錄 TEST-29 的「標準寫法」欄(`checks-catalog.md` 第 677 行),不是「壞寫法形狀」欄。
  - 真正的反查單位是 `rememberInfiniteTransition` 與 `assertIsDisplayed()`,我實跑兩個路徑都叫不出。
  - 照規則抽不出這個單位,「androidTest 切得出」的案例要靠造假型錄。

### F8 改由規則的「涵蓋那一行」量法沒定:剝法旗標、折空白後的行號對映、多處出現
severity: minor
blocking: 否。只影響 `--sg` 完整模式,實作時會撞到。
- 位置:〈用詞〉改由 `規則`。
- 引句:「起訖行涵蓋片段所在那一行」
- 引句:「再把連續空白折成一個比對」
- 佐證:
  - `_strip_c_comments(kotlin=True)` 預設不保留換行。我實測 `/* a\n b */\nval x = 1` 剝完行號少一行。
  - 要帶 `keep_newlines=True` 或 `keep_length=True`,才能把比對位置映回行號。字串要帶 `blank_strings=True` 才會被清空。規則沒寫。
  - 折空白是把換行也折成空格,片段橫跨兩行時「所在那一行」是首行還是兩行都要涵蓋,沒定。
  - 片段在同一壞例檔出現多處時,是「任一處被報節點涵蓋」還是「每一處」,沒定。

### F9 `scan_index=None` 同時代表「沒掃」與「掃壞了」
severity: minor
blocking: 否。外層 `scan()` 失敗已經有 `<pack>` 問題兜底,所以不是漏洞,只是介面含糊。
- 位置:範圍 3 的 `bad_snippet_reach_problems(…, scan_index=None)` 與範圍 4 的 `--sg` 接法。
- 引句:「`--catalog-only` 沒有 ast-grep 時是 None、只做靜態核對」
- 佐證:
  - 同一函式另有「掃描逾時或失敗(`scan()` 回 None)時,這道判問題」。
  - `check()` 對四個設定檔各掃壞例、好例,部分失敗時索引是半份。逾時後 `_TIMED_OUT` 讓之後所有掃描都回 None。
  - 規則沒說索引半份與完全沒有各怎麼處理。實作者若把失敗的 None 直接傳進來,這道會當成「沒掃」靜默跳過(只剩 `<pack>` 那條問題在報)。

### F10 `範本 T<n>` 的核對:小節可重複、`T0` 裡其實有壞寫法小節
severity: minor
blocking: 否。
- 位置:〈用詞〉改由 `範本 T<n>`。
- 引句:「n 不是 0;等於這個單位的對應檢查列通電批次欄」
- 佐證:
  - `test-templates.md` 第 430、466、499、520、557 行的 `### 壞寫法:TEST-4/6/9/18/19` 小節位於 `## T0`(第 137 行起)。
  - 真型錄有 10 列通電批次寫 `範本 T0`。這 10 列的單位被禁用範本改由,只能用規則或代碼審,同時又存在可驗證的圍欄壞寫法。
  - 同一編號有多個小節(TEST-6 在 466 與 594 行、TEST-9、API-10、API-8 等)。「那個小節」要在這些小節取聯集還是只看第一個,規則沒定。

### F11 數字與量法:427 數不出來、NiA 基線含測試檔、歸屬欄空白
severity: minor
blocking: 否。
- 位置:〈用詞〉公開名稱,範圍 5 補字前後量法,範圍 1 歸屬欄寫法。
- 引句:「427 個名稱丟 4 個」
- 引句:「項內關鍵字與編號之間一個半形空白」
- 佐證:
  - 427:我照規則的排除條件(並做了 F4 的正確解析)得 440 個去重名稱,丟 4 個剩 436。差 9 個,沒有逐步可重現的算法。
  - NiA 基線:310 支 kt 裡 52 支在 `src/test` 或 `src/androidTest`,「整份 kt 檔當新增、照 `app/src/main` 路徑切段」把它們也算進去,而真實推送會排除測試檔。我量到 164 檔命中、679 段、1048 配對,測試檔的比重沒有被拆出來。20% 門檻的分母因此偏大。
  - 歸屬欄:人手寫 `D-5、 D-6`(頓號後多一個空白)是自然寫法。規則沒說是報錯還是自動去空白,S1 列了 `D-04`、`撞名D-4`,沒列這種。

已讀,無 finding:範圍 5 之外的〈實務隱患〉、〈回退〉、〈依據來源〉、〈天花板〉(與上面有關的部分已併入 F2、F4)。

最嚴重 severity:major,blocking 共 6 條(F1、F2、F3、F4、F5、F6)。
