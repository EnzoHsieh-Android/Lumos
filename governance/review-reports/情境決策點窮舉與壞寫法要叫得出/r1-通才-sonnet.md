severity: major

審查範圍:全份逐節讀完,程式碼側都實際開檔或實跑過。交叉引用的節點(`Systems/kotlin規則包` 等六篇)、`lumos gov --stats`、`lumos loop escape --list`、`lumos rejections`、`lumos lint-waive`、`STOP_TRIGGERS`、`stats_problems`、`t_kt_catalog_stats_consistent` 都存在。新增的三個測試名與兩支函式本來就是計劃要建的。

前掃覆核:第 2 項「`Dispatchers.IO` 只有 `getIO()`」屬實。1.10.2 原檔的 `Dispatchers` 是 `public static final fun getIO`,並非 `public final fun`。另外 1.11.0 相對 1.10.2 多 17 個 `public static final fun` 也屬實,我自己抓檔比對過。

固定席:未附。

**1. 〈用詞〉公開名稱第③類:`$` 排除規則會靜默拿掉整組 `Channel.UNLIMITED` 系列**

severity: major
blocking: 是。實作者照字面做,會讓最典型的緩衝容量決策點(D-16 的 `UNLIMITED`)不在母體裡,而自檢仍然全綠。
- spec 位置:〈用詞〉公開名稱第③類,「都排除:…還原之後名稱仍含 `$` 的」。
- 引句:「還原之後名稱仍含 `$` 的、標 `synthetic` 的(隱藏的舊版相容入口)」
- 問題:`Channel.UNLIMITED`、`CONFLATED`、`BUFFERED`、`RENDEZVOUS` 在 `.api` 裡是具名伴生物件 `Channel$Factory` 的 static field。它不是 `$Companion`,所以套公式會還原成 `Channel$Factory.UNLIMITED`,含 `$` 被排除。
- 連帶:D-16 現有觸發字 `UNLIMITED` 不等於任何母體名稱,範圍 2 第五點的反向同步檢查也看不到它。母體裡少一整組,還不會紅。
- 同類漏網:`ChannelResult$Companion`、`Job$Key` 等 `$` 嵌套類別,同一規則下也被丟掉。
- 佐證:`/tmp/lumos-seat-work/情境決策點窮舉與壞寫法要叫得出/通才-sonnet/a.api`(1.10.2 原檔)中 `public final class kotlinx/coroutines/channels/Channel$Factory` 只有 `BUFFERED`、`CONFLATED`、`RENDEZVOUS`、`UNLIMITED` 等 static field。
- 佐證:file: `skills/kotlin-idioms/checks-catalog.md:755` D-16 觸發字含 `UNLIMITED`。

**2. 母體只收「…Kt 靜態函式、類別簡名、常數」,完全不含成員函式與成員屬性,但計劃稱「窮舉」**

severity: major
blocking: 是。「選錯寫法一定被問到」的主張對成員形態的決策點不成立,而計劃沒承認。
- spec 位置:〈用詞〉公開名稱、PRIOR-ART、白話。
- 問題:下列都是 `abstract`/`final` 成員,不在母體裡:`emit` 與 `tryEmit`、`send` 與 `trySend`、`receive`、`Mutex.lock` 與 `tryLock`、`Job.cancel` 與 `join`、`Dispatchers.Main.immediate`。
- 現有觸發字也證實了這點:D-16 的 `trySend`、D-26 的 `receive` 都是成員,不等於任何母體名稱。反向同步檢查對它們是瞎的。
- 天花板第 2 點只說「第一版只窮舉協程核心」,沒說成員不在內。
- 佐證:file: `skills/kotlin-idioms/checks-catalog.md:765` D-26 觸發字含 `receive`。
- 佐證:`a.api` 中 `trySend-JP2dKIU` 只以 `SendChannel` 的 abstract 成員出現,不在任何 `…Kt` 門面類別。

**3. 「無決策」可以拿「頻率 x%,改由 <哪裡>」過關,但「改由」是沒驗證的自由文字**

severity: major
blocking: 是。與天花板 4 自相矛盾,把最常見的選錯寫法合法地擋在題外。
- spec 位置:範圍 4 第一點,對照天花板 4 與〈實務隱患〉「代碼審變成新的垃圾桶」。
- 引句:「改寫 `無決策` 並在理由寫「頻率 x%,當觸發字會到處亮,改由 <哪裡>」」
- 問題:`STOP_TRIGGERS` 已含 `launch`、`async`、`await`、`collect`、`withContext`、`delay`、`Dispatchers.IO`、`Dispatchers.Default`、`Deferred`、`StateFlow`、`Job`、`cancel`、`first`。這些就是最常被選錯的名稱,一律會走「無決策+改由」。
- 範圍 3 對「改由」收四種受驗值,範圍 1 對「無決策」只要求「理由不得空白」。自檢和統計都不認這類名稱,天花板 4 說「寫在〈叫不出的壞寫法〉節裡讓人看得到」,但這些名稱根本不在那一節。
- 佐證:file: `configs/ast-grep/kotlin-android/check.py:150` `STOP_TRIGGERS`。

**4. 反查壞寫法可以用「片段裡的佔位字」當觸發字過關,但真程式不會中**

severity: major
blocking: 是。第二道自檢可被輕易地「綠」掉而實際不守。
- spec 位置:範圍 4 第二點,「有專一字面特徵、頻率在門檻內的補觸發字(讓它叫得出)」。
- 問題:「專一字面特徵」沒有定義,而「叫得出」只驗片段原文。片段裡充滿佔位名,例如 `bigList`、`slowWork(it)`、`x.f(…)`、`scope.async(handler)`、`val a = x.f(…)`。補 `bigList` 當觸發字就能讓 PERF-26 的片段叫得出,真專案的 `users.contains(x)` 完全不會被問。
- 這個模式已經存在:D-60 現有觸發字是 `in bigList`,字面就是型錄示範用的變數名。
- 實測我複現了 spec 的掃描(用 `_kt_sit_text_segments` 包 `class X { fun f() {…} }`)。叫不出的片段裡含 `…`、`...` 或佔位名的約 24 筆,純識別字或單字的約 38 筆(`HashMap`、`@Entity`、`postDelayed`、`bigList`)。這些最容易被「補一個字」硬湊過關。
- 佐證:file: `skills/kotlin-idioms/checks-catalog.md:799` D-60 觸發字 `contains(`、`in bigList`、`indexOf(`。
- 佐證:file: `skills/kotlin-idioms/checks-catalog.md:717` PERF-26 片段 `bigList.contains(x)`。

**5. 「改由 規則 <id>」只驗規則存在與訊息編號,不驗它會對這段片段亮**

severity: major
blocking: 是。叫不出的壞寫法一旦被歸到「規則」,既沒被問到、也未必被擋,卻被當成已處理。
- spec 位置:範圍 3 第四點,以及預期值表 S2 的 `kt-map-await-deferred` 列。
- 問題:自檢只比「規則在 `rules/`、訊息開頭引的編號等於對應檢查」。一個編號(例 API-2)下有多段片段,規則只管其中一種寫法。
- 實例:`kt-map-await-deferred` 只有兩個 pattern(`$L.map { it.await() }`、`$L.map { $X -> $X.await() }`),`ignores` 掉 `src/debug*` 與各測試目錄,還有 `.asFlow()` 排除條件。把 API-2 的 `forEach { it.await() }` 之類片段寫成「改由 規則 kt-map-await-deferred」會通過自檢,實際不會被擋。
- 佐證:file: `configs/ast-grep/kotlin-android/rules/api.yml:326`。
- 補救方向:`check.py` 已有 `scan()`,可以對每個「改由規則」的片段實跑一次。

**6. 沒有「確實是決策點、但沒有任何 D 列可歸」的出路,也無法機檢「歸對列」**

severity: major
blocking: 是。「窮舉分類」這一步的判準寫不清,實作者會被迫做錯決定。
- spec 位置:範圍 1「歸屬是一到多個 `D-n`,或 `無決策`」。
- 問題一:現有 60 列觸發字完全沒有這些名稱:`runBlocking`、`SupervisorJob`、`CoroutineStart.*`(`UNDISPATCHED`、`ATOMIC`)、`BufferOverflow`/`DROP_OLDEST`、`SharingStarted`/`Eagerly`/`Lazily`、`tryEmit`、`yield`、`ensureActive`、`Dispatchers.Unconfined`。
- 這些名稱明確帶決策,卻沒有對應的情境列。只剩「硬塞進不相干的 D 列」或「謊稱無決策」兩條路。計劃沒寫「可以新開 D 列」,新開列要寫標準寫法與證據,範圍沒算進去。
- 問題二:反向同步規則會逼出錯歸屬。D-59(資料同步合併)的觸發字有 `merge`,Flow 的 `merge` 是公開名稱,規則逼它歸 D-59。`combine` 要同時歸 D-5、D-6、D-35,`stateIn` 要歸 D-5/6/15/49。歸對與否只靠人,兩道自檢都抓不到,答錯列的情境題會問錯題。
- 佐證:file: `skills/kotlin-idioms/checks-catalog.md:798` D-59。

**7. 「選錯寫法一定會被問到」的天花板列得不全:別名匯入與「沒用某個 API」兩類都漏**

severity: major
blocking: 是。白話與標題宣稱的保證,兩道自檢都兜不住,計劃沒承認。
- spec 位置:〈白話〉、〈天花板〉1 到 4。
- 引句:「這份計劃讓「沒被問到」不能再默默發生」
- 漏網一:別名匯入(`import …flatMapMerge as fm`)。觸發字只比增行文字,`fm {` 不中;import 行本身又被切段程式略過。
- 漏網二:壞在「沒寫」。逐筆串行呼叫該並行、`launch` 進迴圈沒限流、`viewModelScope.launch` 之外沒有任何受控名稱。這種片段只能歸「代碼審」,而〈叫不出〉節可以無限寫,沒有上限(RETIRE-IF 是八週後才看)。
- 漏網三:歸屬列對但寫法在另一個維度選錯,如 D-4 已被問到但候選列裡沒有該壞寫法對應的列。
- 天花板第 3 點(自家包裝函式)有承認,但上面三類沒有。

**8. 母體名稱抽出的雜訊與不穩定名稱沒處理(`-hash` 修飾名、`…Kt` 門面類別、系統屬性常數、`Key`)**

severity: minor
blocking: 否。實作者能自行排除,但「約 270 個」與結果對不上,會多花工。
- 修飾名:`delay-VtjQ1oo`、`withTimeout-KLykuaI`、`withTimeoutOrNull-KLykuaI`、`debounce-HG0u8IE`、`sample-HG0u8IE`、`timeout-HG0u8IE`、`WhileSubscribed-5qebJ5I` 等 12 個。Kotlin 編譯器版本一變 hash 就變,會造成假的「新名稱」紅燈。同時它們與 `delay` 等 Long 版名稱並存,「同名兩列」檢查不會逮到。
- `…Kt` 門面類別:46 個(`FlowKt`、`DebugKt`、`LintKt`、`GuidanceKt`…)會被②當類別簡名抽出,使用者程式不會寫到這些名字。
- 系統屬性名稱與 `Key`:`DebugKt.DEBUG_PROPERTY_NAME`、`DispatchersKt.IO_PARALLELISM_PROPERTY_NAME`、`CoroutineName.Key` 等約 12 個也被抽出,同樣沒有決策意義。
- 計數:照 spec 規則我算約 300 到 310,不是「約 270」,規則與數字不符。

**9. 8% 常用字門檻沒有可照做的量法,也沒有總量上限**

severity: minor
blocking: 否。只影響噪音多寡,事後有 RETIRE-IF 把關。
- spec 位置:範圍 4 第一點「同 E9 的量法」、〈實務隱患〉第一點。
- 問題:E9 只記結果(Now in Android 310 支檔),沒有留下量測腳本或複本路徑。第二個人照做不出來。
- 門檻只管單字;補 100 多個字,每個都低於 8%,合起來可能讓幾乎每次改動都出情境段。E9 本來就記載整檔至少命中一列已 64%。合併後的上限只放在 RETIRE-IF(八週後),而且是以「盲判不適用比例」量。
- 佐證:file: `docs/lumos-toolchain-knowledge/Projects/Android寫法回合結束檢查與改檔前推列_計劃.md:158`。

**10. 91 段與 180 段的數字我複現不出來**

severity: minor
blocking: 否。
- spec 位置:〈白話〉、範圍 4。
- 我用 spec 描述的做法(`class X {`、`fun f() {`、片段、兩個 `}`,經 `_kt_sit_text_segments`)掃,對每個 D 列的每個對應檢查的每段反引號片段,得到 185 段、叫不出 96 段。
- 差 5 可能來自去重口徑。spec 沒寫是否以(對應檢查, 片段)去重,以及同一編號出現在多個 D 列時怎麼算。`sweep/` 的 tsv 要補上這個口徑。

**11. 母體原檔沒有雜湊釘死**

severity: minor
blocking: 否。
- spec 位置:〈用詞〉API 母體、範圍 1 第一行「母體:…<官方 .api 檔網址>」。
- 問題:「逐位元組放」只靠人保證。型錄只記網址,沒記 sha256。日後有人編輯那份 `.api`(漏掉一個名稱),自檢會把它當母體,不會紅。
- 建議:母體行加 sha256,自檢核對。

**12. S3 的後半沒有綁到對應測試**

severity: minor
blocking: 否。
- spec 位置:S3。
- 問題:S3 說「S1 應紅、S2 應紅/綠」,但只綁了 `t_kt_catalog_api_decision_points`(S1 的測試)。S2 那一半的斷言沒有測試名,實作時容易被漏掉或放進錯誤的測試。
- 建議:S3 加綁 `t_kt_catalog_bad_snippets_reach_rows`,或另寫一條聯合測試。

**實務隱患鏡頭逐類**
- **觸發字變多、情境段變多(效能、噪音):** 有,見第 9 點。切段預篩有字集合,效能風險不大;切段快取鍵含 rows,改型錄會正確失效。
- **母體抽法漂移:** 有,見第 8 點(修飾名、門面類別)與第 11 點(沒釘雜湊)。
- **「代碼審」垃圾桶:** 有,見第 3 點(`無決策` 沒有驗證)與第 7 點。
- **金流、不可逆、對外送出:** 無。只讀本機型錄與 `.api`,退提交即回原狀。這與計劃自己的「已排除」一致,我覆核同意。
- **供應鏈:** 有,即第 11 點。

最嚴重 severity 是 major,blocking 共 6 條(第 1 到 7 點中除第 7 點外是 1、2、3、4、5、6,第 7 點也標 blocking:是,合計 7 條)。

更正總結:blocking 為 7 條(第 1、2、3、4、5、6、7 點),最嚴重 severity 是 major。
