severity: major

投稿設計的方向我認同,但這份 spec 有 6 個會直接擋住實作或讓「窮舉」宣稱破功的洞。下面是我在臨時目錄實測的結果,環境是官方 1.10.2 與 1.11.0 的 `.api`、真型錄,以及真的 `_kt_sit_text_segments`。

固定席:這次沒有收到具體的節點清單,我只讀了 `Systems/kotlin規則包`。它記的「樣本逐行比對壞寫法欄」否決,spec 已在〈舊否決對照〉自己答覆。理由是本案判的是「會不會被問」,不是「哪條 lint 擋得到」。我判不影響。其他節點我沒查,不下判斷。

## 逐節

- 用詞、範圍 1(API 決策點節)、範圍 2:有 finding F1 到 F4。
- 範圍 3:有 F5、F6、F10。
- 範圍 4、5、依據來源、預期值表、回退:有 F7、F8。
- 範圍 2 的「推送前閘與 CI 不直接跑 `check.py`」宣稱,我沒能判斷真假。`t_kt_catalog_stats_consistent` 的 docstring 寫「推送前的規則包自檢與 `--catalog-only` 都會跑」,兩處說法不一致。⚠
- 交叉引用核對:`Systems/pitfalls-code-loop`、`Systems/棧別提問表態閘`、`Systems/bound-tests-gate`、兩篇 Projects 計劃都存在。`lumos gov --stats`、`lumos loop escape`、`lumos rejections` 也都存在。`kt-map-await-deferred` 在 `rules/api.yml`,訊息開頭是 `[API-2]`,和預期值表一致。已讀,無新壞引用。
- 用詞、〈天花板〉1 到 5、REVISIT:已讀,無 finding。

## Findings

**F1(範圍 2 第四、五點:同步檢查只認「整字等於」)**
severity: major
blocking: 是。同步守衛有繞過口,正是本案要封的那種漏洞。
引句:「反向:某列的觸發字整字等於某個公開名稱,但表上那個名稱沒有歸到這一列 → 問題(兩邊不同步)。」
- 問題:反向檢查只在觸發字整字等於名稱時才報。名稱裡含觸發字、但整字不等於的,可以歸 `無決策` 而不被抓。
- 佐證:
  - D-16 觸發字有 `UNLIMITED`,名稱是 `Channel.UNLIMITED`。`_kt_trigger_re("UNLIMITED")` 搜得到它,但整字不等於,所以不報。
  - D-5 觸發字有 `WhileSubscribed`,名稱是 `WhileSubscribed-5qebJ5I`(`SharingStartedKt` 裡的 Duration 版)。正規式搜得到,整字不等於,所以不報。
  - 兩個名稱都能標成 `無決策` 而全部綠燈。實際推送時它們會被問到,表卻說不帶決策。

**F2(範圍 2 第五點:反向檢查會逼出語意錯誤的歸屬)**
severity: major
blocking: 是。照字面實作,真型錄無法同時「回空」又「歸屬有意義」。
引句:「反向:某列的觸發字整字等於某個公開名稱,但表上那個名稱沒有歸到這一列 → 問題(兩邊不同步)。」
- 問題:既有觸發字有一批剛好等於協程函式名,反向規則強迫把這些名稱歸到那一列。
- 佐證:
  - D-59(資料同步衝突)觸發字有 `merge`,而 `FlowKt.merge` 是 Flow 運算子。名稱 `merge` 必須歸 D-59,語意不對。
  - `combine` 要同時歸 D-5、D-6、D-35。`Channel` 要歸 D-7、D-16。
  - 規則只在句法層驗證。`Channel.CONFLATED` 誤歸 D-7 也能過,因為 `Channel` 這個觸發字搜得到它。

**F3(用詞「公開名稱」、範圍 1:母體名稱沒有正規化規則)**
severity: major
blocking: 是。「每個恰好一列」與「同名兩列報問題」在真母體上互相抵觸。
引句:「接一張表「名稱 | 歸屬 | 理由」,公開名稱每個恰好一列:」
- 問題:spec 沒說名稱要不要去重、要不要還原 JVM 名稱修飾。
- 佐證:
  - 1.10.2 的 `…Kt` 門面有 278 個 `public static final fun` 條目,去重後 205 個名稱。51 個名稱重複,例如 `map`、`first`、`filter`、`launch`、`cancel`、`delay`、`stateIn`,分散在不同門面或多載。
  - 有 12 個名稱帶型別修飾的雜湊,例如 `delay-VtjQ1oo`、`withTimeout-KLykuaI`、`debounce-HG0u8IE`、`sample-HG0u8IE`、`WhileSubscribed-5qebJ5I`。`debounce` 和 `debounce-HG0u8IE` 是同一個 Kotlin 名稱的兩列。
  - 有 10 個名稱同時是類別簡名(②)和工廠函式(①):`Channel`、`Job`、`Mutex`、`Semaphore`、`MutableSharedFlow`、`MutableStateFlow`、`CompletableDeferred`、`CoroutineScope`、`CoroutineExceptionHandler`、`BroadcastChannel`。錨點 `Mutex` 就是其中之一。
  - `Channel.map` 和 `Flow.map` 語意不同,卻被併成一個名稱一列。

**F4(用詞 ③:列舉值與物件常數的抽法)**
severity: minor
blocking: 否。只增加雜訊和升版搬動,不漏守。
引句:「公開類別裡大寫開頭的 `public static final field`(例 `BufferOverflow.DROP_OLDEST`)」
- 問題:規則寫得比真檔鬆,會抽出一批不是寫法的名稱。
- 佐證:
  - 「大寫開頭的 `public static final field`」把 `Dispatchers.INSTANCE`、`GlobalScope.INSTANCE`、`ChannelResult.Companion`、`Channel.Factory`、`CoroutineName.Key` 等都抽進來。共抽出 34 個,至少 13 個是這種。
  - 門面常數 `DebugKt.DEBUG_PROPERTY_NAME`、`FlowKt.DEFAULT_CONCURRENCY_PROPERTY_NAME` 的命名,和 ① 去掉 `Kt` 的做法不一致。
  - object 的 getter 在檔裡不是 `static final`,例如 `public fun getCoroutineContext ()`。spec 的條件沒要求 `final`,會抽出 `GlobalScope.CoroutineContext`、`NonCancellable.Parent`、`NonCancellable.OnJoin`。「去掉 get 還原屬性名」無法判斷大小寫,`getIO` 該大寫、`getCoroutineContext` 該小寫。
  - 不在 `internal` 套件、但實為內部的門面(`DebugKt`、`DispatchedTaskKt`、`EventLoopKt`、`DefaultExecutorKt`)會進母體。1.11.0 刪掉了 `isIoDispatcherThread`、`processNextEventInCurrentThread`、`runSingleTaskFromCurrentSystemDispatcher`,升版就會有「表上有、母體沒有」的紅燈,和公開 API 無關。

**F5(範圍 2、3:自檢函式拿不到 lumos 的函式,整合方式沒寫)**
severity: major
blocking: 是。不補就不知道失敗時該報問題還是略過,而兩條路都會出事。
引句:「抽法只有型錄自檢 `check.py` 一處(`api_names`,新增)。」
- 問題:歸屬檢查要 `_kt_trigger_re`,叫得出檢查要 `_kt_sit_text_segments`,兩者都在 `scripts/lumos`,不在 `check.py`。
- 佐證:
  - `catalog_problems(rules)` 沒有 `lumos` 參數。既有的 `situation_sample_problems(lumos=)` 才有,而且接在 `catalog_problems` 之外。
  - `scripts/test_lumos.py` 裡 `catalog_problems` 有 43 處呼叫。`_ktpack(copy=True)` 只複製規則包、型錄、範本,不複製 `scripts/lumos`,並把 `m.HERE` 指到暫存目錄。複本裡 `load_lumos()` 找不到檔。
  - 找不到時若略過,等於沒檢查;若報問題,43 處改壞測試全部連帶紅。S3 要在複本裡拿掉 D-4 的 `flatMapMerge`,同樣受影響。
  - S1 要「母體換成 1.11.0」,但沒說 1.11.0 的檔放哪裡(repo fixture?),也沒說 `api_decision_problems` 是否收母體路徑參數。測試若上網抓會破壞零依賴與離線。

**F6(範圍 3 第四點:改由 `規則` 和 `範本` 只驗編號,不驗真的擋得到)**
severity: major
blocking: 是。它重開了本案要封的「沒被問到也沒人擋」的口,而〈實務隱患〉只把「代碼審」當垃圾桶。
引句:「改由只收四種:`規則 <id>`(那條規則要在會擋的 `rules/` 目錄、訊息開頭引的型錄編號等於這列的對應檢查)」
- 問題:`規則 <id>` 只驗規則在 `rules/` 且訊息引的編號相同。`範本 T<n>` 只驗等於通電批次欄的值。
- 佐證:
  - 一個對應檢查通常有多段片段。一條規則或範本掛上,就讓該檢查所有片段過關,不管規則是否擋得住那一段。
  - `kt-map-await-deferred` 的 `ignores` 排除了 `**/src/test*/**`、`**/src/debug*/**` 等路徑,沒涉及片段本身。
  - 通電批次欄裡「範本 T0」有 10 筆,而 `test-templates.md` 的 T0 是「測試骨架守則」,不是行為測試。
  - 樣本實測:95 個叫不出的片段裡,有 16 個其實會命中別列(不是本列)。這種片段最容易被輕易改歸別處。

**F7(範圍 4 與 PRIOR-ART:數字無法重現)**
severity: minor
blocking: 否。
引句:「2026-11-12 比對 1.10.2 與 1.11.0 兩版的 `.api`,1.11.0 多了 `associate` 等 17 個函式,升版會被點到。」
- 問題:spec 寫「180 段、91 段叫不出」,我用 spec 定義重算不是這兩個數。
- 佐證:
  - 非停用列的 (列, 檢查, 片段) 共 184 筆,叫不出 95 筆(去重片段 92 個)。
  - 差異原因不明,spec 說原始結果要實作時才存進 `sweep/`,所以現在無法覆核。⚠
  - 「1.11.0 多 17 個函式」是原始條目數,含 `$default`、`synthetic`、多載。去重後的真名稱約 10 個:`associate*`、`groupBy*`、`consumeTo`、`runBlockingK`。

**F8(範圍 3 缺口:停用列與沒有觸發字的列)**
severity: minor
blocking: 否,實作者可自行決定,但 S2「真型錄回空」的結果會因此不同。
引句:「情境列「對應檢查」欄每個編號,在型錄主表那一列「壞寫法形狀」欄裡每一段反引號包住的文字」
- 問題:spec 沒說停用列的片段要不要算,也沒說刻意寫 `(無)` 的列怎麼處理。
- 佐證:
  - 停用的 D-38 對應 DATA-68,有 1 段片段。停用列觸發字是 `(無)`,片段必然叫不出。
  - D-2 刻意不設觸發字(型錄寫明「只靠規則包與代碼審」),它的 API-1 片段全部叫不出。這和「有專一字面特徵就補字」的範圍 4 衝突。
  - 實測 `(無)` 列與停用列合計貢獻了 3 筆必然叫不出的片段(D-2 兩筆、D-38 一筆)。

**F9(實務隱患「片段包裝方式」:落單字元不只是引號)**
severity: minor
blocking: 否。spec 已說「不做特例、照判」,所以只是描述不夠完整。
引句:「它是逐字元的詞法掃描,片段裡有落單的引號、`/*` 或反引號時,後面的包裝與片段後半會被當成字串或註解剝掉」
- 問題:會讓整段被剝掉的不只落單引號。
- 佐證(把片段包進 `class X {` / `fun f() {` 後實測 D-4):
  - `"flatMapLatest { x }` 叫不出。
  - `/* flatMapLatest` 叫不出。
  - `// flatMapLatest` 叫不出。
  - `}` 單獨一字叫不出。
  - `'flatMapLatest` 叫得出,單引號不受影響。
  - 以 `import` 或 `package` 開頭的片段會被 `_kt_sit_hits` 跳過,同樣叫不出。
- 這些不是「不是寫法」。`"flatMapLatest {` 是真的壞寫法片段,理由欄寫「不是寫法」會是錯的。

**F10(範圍 3、5:新節放在 `情境決策表` 與 `待查證` 之間,會被舊切法吃進去)**
severity: minor
blocking: 否。結果碰巧正確。
引句:「型錄在〈情境決策表〉之後新增〈API 決策點〉節。」
- 問題:`catalog_problems` 以 `dt = text[i_dt:i_pend]` 取決策表,新節夾在中間就會被含進去。
- 佐證(`check.py:472`、`check.py:504`):
  - 〈叫不出的壞寫法〉列首是 `| D-4 |`,符合決策表列的正規式。
  - 靠欄數 5 不等於表頭 8 而被 `continue`,所以現在碰巧沒事。
  - 但新表若欄數寫錯成 8,會被當決策表列處理;欄數寫錯成別的數,則靜默跳過、不會有人報。
  - 統計核對(`_stats_expected`)也要為「公開名稱數、各歸屬筆數」定義固定行格式。spec 沒寫,「各歸屬筆數」對多值歸屬(`D-4、D-5`)的計法也沒定義。

**F11(範圍 1:「窮舉」的範圍比使用者目標窄,〈天花板〉沒列)**
severity: major
blocking: 是。使用者目標是「Kotlin 語法絕對窮舉得出」,spec 目前只窮舉 ①②③ 三種。
引句:「②公開類別與介面的簡名(例 `Mutex`);③列舉值與物件常數」
- 問題:帶參數的類別成員、object 與伴生物件的成員函式不在母體裡。
- 佐證:
  - D-3 的 `limitedParallelism` 是 `CoroutineDispatcher` 的成員(`a.api` 第 175、521 行)。
  - D-16 的 `trySend`(`trySend-JP2dKIU` 成員,第 843、896 行)也是成員。
  - `SharingStarted.WhileSubscribed(stop…, replay…)` 這個最常見寫法是伴生物件成員,不是 getter。母體裡只剩 Duration 版的擴充 `WhileSubscribed-5qebJ5I`。
  - `Mutex.lock`、`Semaphore.acquire`、`Job.cancel`、`MutableSharedFlow.tryEmit` 同樣不在母體。
  - 這些名稱即使有決策,也不會被「母體多出名稱就紅」守住。〈天花板〉2 只提 androidx,沒提這一塊。

## 實務隱患

- 效能與盲判成本:自檢本身很便宜。實測 `load_lumos` 約 0.15 秒,184 次叫得出共 0.10 秒,整個 `catalog_problems` 約 0.035 秒。成本風險在補字之後推送時的情境段變多,spec 只靠 8% 人工門檻與 RETIRE-IF,自檢不核頻率,也沒有補字數量上限。這點我判無自動防線,屬 minor。
- 格式漂移:spec 驗三種名稱數量與錨點,方向正確。但 F3、F4 顯示真檔已有 spec 未涵蓋的形狀,抽法不是只有格式漂移的風險。
- 資安、金流、對外送出、不可逆:無。spec 已排除,我也只看到本機讀檔。

最嚴重 severity 是 major,blocking 共 5 條(F1、F2、F3、F5、F6、F11 中 F1、F2、F3、F5、F6、F11 皆為 blocking 是,實為 6 條)。

更正:blocking 共 6 條(F1、F2、F3、F5、F6、F11)。
