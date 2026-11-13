severity: major

審查範圍:逐節讀完整份 spec。我實測了 `.api` 抽名、`_kt_sit_text_segments` 的叫得出判法、`_kt_situation_segments` 的路徑篩選、`rules/` 規則檔,以及真型錄 60 列觸發字。固定席節點(`Systems/kotlin規則包`)沒有附上,只能憑 spec 自己引用處判斷:本案不改情境題、表態、盲判,對這些行為「不影響」。理由是 spec 只新增兩節與兩道自檢。但自檢會擋推送,所以有守衛面風險(見最後的風險類)。

**Finding 1:「叫得出」用假檔名切段,繞過了真推送會跳過測試檔的篩選**
severity: major
blocking: 是(判準:反查證明的「叫得出」跟真推送的行為不同,對測試類列會給出假的綠燈,而這正是本案要消除的「默默放行」)
- spec 段落:〈用詞〉「叫得出」、〈範圍〉3、〈實務隱患〉舊否決對照。
- 引句:「用的是推送前真正跑的同一套切段程式,判的就是它自己,不衝突。」
- 引句:「片段單獨包成 `class X {` / `fun f() {` / 片段 / `}` / `}` 當整支新增,經情境段切法切出的段的候選列含那一列。」
- 問題:真推送走 `_kt_situation_segments`,切段前會用 `_PITFALL_DIFF_TEST_PAT` 和 `_stack_changed_ok` 把測試檔整支排除。反查走的 `_kt_sit_text_segments` 沒有這道篩選,用的是 `X.kt` 這種假路徑。
- 佐證(輸入→結果):
  - 包 `runTest` 和 `StandardTestDispatcher()` 的片段,假路徑 `X.kt` 切出 `['D-21','D-49']`,判成「叫得出」。
  - `app/src/test/java/a/FooTest.kt` 的 `_PITFALL_DIFF_TEST_PAT` 為 True、`_stack_changed_ok` 為 False。這個路徑的改動在真推送裡完全不會出情境段。
  - 所以 D-21、D-49、D-50、D-51、D-54 這類 TEST-* 檢查的壞寫法片段,都會被反查判「叫得出」,過期檢查還會要求你刪掉〈叫不出〉的列。實際上標準測試目錄 `src/test` 下它們永遠不被問。
- file: `scripts/lumos:40098`(`_PITFALL_DIFF_TEST_PAT`)
- file: `scripts/lumos:39941`(`_kt_situation_segments` 的篩選 `not _PITFALL_DIFF_TEST_PAT.search(rel) and _stack_changed_ok(...)`)
- 建議:反查的假路徑改用不被篩掉的真實樣子,另加規則「該列屬測試類時,要用 `src/test/...` 路徑驗證」。或者明講測試類列不納入反查,走〈叫不出〉的「代碼審」。

**Finding 2:「窮舉母體」不含成員函式,真型錄已有觸發字落在母體之外**
severity: major
blocking: 是(判準:「窮舉得出來」是本案的核心宣稱,而三種名稱的抽法系統性漏掉整類決策點,〈天花板〉也沒寫)
- spec 段落:〈用詞〉公開名稱(三種)、〈範圍〉1、〈天花板〉2。
- 引句:「公開名稱:從 API 母體抽出的名稱,三種:①頂層與擴充函式」
- 問題:只抽 `…Kt` 門面的靜態函式、類別簡名、靜態欄位和物件的 getter。類別與介面的成員函式一律不進母體,但情境選擇常是成員函式。〈天花板〉只承認 androidx 和自家包裝,沒提成員。
- 佐證:用 `kotlinx-coroutines-core-1.10.2.api` 檢查真型錄觸發字,下列觸發字沒有任何對應的母體名稱:
  - D-3 `limitedParallelism`:`.api` 第 176、521 行,是 `CoroutineDispatcher` 的成員。
  - D-16 `trySend`:是 `SendChannel` 成員,而且名稱帶雜湊後綴 `trySend-JP2dKIU`。
  - D-26 `receive`:`.api` 第 874 行是成員,不在母體裡。
  - D-25 `resume`、`invokeOnCancellation`:同為成員。
  - `SharingStarted.WhileSubscribed(…)` 本體是 `SharingStarted$Companion` 的一般方法,不是 `get` 讀取函式,也不在母體。
- 後果:S1 的「母體多了名稱就紅」對這類決策點完全無感。`send`、`tryEmit`、`Mutex.lock`、`Semaphore.acquire` 這些成員新增或換簽名都不會被點到,但使用者原話要的是窮舉。
- file: `skills/kotlin-idioms/checks-catalog.md:742`(D-3 觸發字含 `limitedParallelism`)
- 建議:把成員函式納入母體,或在〈天花板〉明寫「成員函式不在窮舉範圍」並降低「窮舉」的宣稱。

**Finding 3:反向同步檢查只比「整字相等」,漏掉雜湊後綴名稱和帶點名稱**
severity: major
blocking: 是(判準:正反兩向同步是本案的守衛之一,而它在真型錄上會放過「觸發字會命中、卻被歸成無決策」的名稱)
- spec 段落:〈範圍〉2 第五點、預期值表 S1 第三列。
- 引句:「反向:某列的觸發字整字等於某個公開名稱,但表上那個名稱沒有歸到這一列 → 問題(兩邊不同步)。」
- 佐證:`.api` 裡 12 個函式名帶 Kotlin 內嵌類別(Duration)的雜湊後綴。
  - 這 12 個是 `delay-VtjQ1oo`、`withTimeout-KLykuaI`、`withTimeoutOrNull-KLykuaI`、`debounce-HG0u8IE`、`sample-HG0u8IE`、`timeout-HG0u8IE`、`WhileSubscribed-5qebJ5I` 等。spec 沒說要不要還原。
  - 真觸發字 D-10 `withTimeout`、D-4 `debounce`、D-5 `WhileSubscribed` 用 `_kt_trigger_re` 搜這些名稱都命中。
  - 但名稱不等於觸發字,所以把 `withTimeout-KLykuaI` 填成 `無決策`,第五點不報。
  - D-5 `WhileSubscribed` 更糟:母體裡唯一的同名項就是 `WhileSubscribed-5qebJ5I`,它只要填 `無決策` 就逃過兩個方向的檢查。
  - 同理 D-16 觸發字 `UNLIMITED` 對不上 `Channel.UNLIMITED`(外層類別.名稱)。
  - 實測:真觸發字對 353 個抽出名稱做 regex 搜尋,命中但「不等於」的有 `debounce-HG0u8IE`、`withTimeout-KLykuaI`、`withTimeoutOrNull-KLykuaI`、`WhileSubscribed-5qebJ5I`、`NonCancellable.*`、`GlobalScope.*`、`CoroutineDispatcher.Key`。
- 另外,「整字相等」會硬把 D-59 的 `merge`(資料衝突合併)綁上 Flow 的 `merge`。
- 建議:反向規則改成跟正向同一個方向:觸發字的正規式搜得到名稱而該名稱被歸 `無決策` 就報。這也避開 spec 自己擔心的 `launch` 問題,因為方向沒變。另外要明定雜湊後綴是否還原。

**Finding 4:改由「規則」「範本」只核編號,不核規則或範本真的守得到這段片段**
severity: major
blocking: 是(判準:改由是「叫不出時的替代守衛」,但驗證不到它守得到,等於把默默放行搬到另一張表)
- spec 段落:〈範圍〉3「改由只收四種」。
- 引句:「`規則 <id>`(那條規則要在會擋的 `rules/` 目錄、訊息開頭引的型錄編號等於這列的對應檢查)」
- 佐證:自檢只核規則 id 存在、訊息開頭的 `[API-2]` 編號等於這列的對應檢查,沒有任何機制確認這條規則會命中那一段片段。
  - 規則 `kt-map-await-deferred` 的 pattern 只有 `$L.map { it.await() }` 和 `$L.map { $X -> $X.await() }`。檔內註解寫「都只講 map,不收 forEach」。
  - 型錄 D-3/API-2 的片段 `forEach { it.await() }` 填「規則 kt-map-await-deferred」,照 spec 會通過自檢,實際沒有規則擋它。
  - 範本也一樣:只核對應檢查列通電批次欄「行為測試或正向約束=範本 T<n>」的值,不核該範本涵蓋那段片段。
  - 還有 `範本 T0` 這個值(10 列使用),T0 是「測試骨架守則」,不是行為測試範本,spec 沒排除。
- file: `configs/ast-grep/kotlin-android/rules/api.yml:325`
- 建議:規則類改為對片段真跑 ast-grep,或至少要求〈叫不出〉表附規則的正例片段。範本類要註明只能算「有範本、需人照寫」,並排除 T0。

**Finding 5:公開名稱抽法有幾處沒寫死,不同實作會抽出不同的表**
severity: minor
blocking: 否(判準:自檢本身可以在實作時補規則,但現在寫的是會導致表與自檢互相卡住的模糊處)
- spec 段落:〈用詞〉公開名稱、〈範圍〉1、〈範圍〉2。
- 佐證:
  - 去重:1.10.2 的 `…Kt` 門面函式 281 個項目、208 個唯一名稱,49 個名稱重複(`map`、`launch`、`combine`、`first`、`merge`…)。spec 沒說「每個名稱恰好一列」是用集合還是逐項。照字面逐項,會直接撞「同一名稱兩列 → 問題」。
  - `$` 名稱:類別簡名包含 `Job$DefaultImpls`、`Channel$Factory`、`SharingStarted$Companion` 等 29 個以上帶 `$` 的名稱。排除清單的「還原之後仍含 $」只對第③類寫得通,第②類沒講。
  - 雜訊名稱:
    - `INSTANCE` 欄位(`GlobalScope.INSTANCE`、`NonCancellable.INSTANCE`)會被第③類的「大寫開頭靜態欄位」收進來。
    - `DebugKt.DEBUG_PROPERTY_NAME`、`DispatchedTaskKt.MODE_CANCELLABLE` 這種 Kt 門面常數,外層名稱不是使用者寫的名字。
    - getter 只剝 `get` 不轉小寫,會得到 `GlobalScope.CoroutineContext`、`NonCancellable.Children`、`NonCancellable.CancellationException`,而真屬性名是小寫開頭,但 `getIO` 這種就是大寫。
  - 解析陷阱:`.api` 的介面標頭是 `public abstract interface class X {`,「interface class」兩個字連著。我用 `(class|interface)\s+(\S+)` 解析時抓到字面 `class`(我自己犯的錯,但照 spec 簡述的抽法最容易犯同樣的錯)。
  - 另外 1.11.0 實測:新增的唯一函式名只有 10 個(`associate`、`associateBy`、`associateByTo`、`associateTo`、`associateWith`、`associateWithTo`、`consumeTo`、`groupBy`、`groupByTo`、`runBlockingK`),同時移除 3 個(`isIoDispatcherThread` 等)。spec 的「多了 17 個函式」大概是計重載。S1 只列「新名稱沒分類」,沒寫移除的方向,但範圍 2 第二點有。
- 建議:寫死去重口徑、`$` 與 `INSTANCE` 與 Kt 常數的排除、getter 還原規則。

**Finding 6:反查的計數與涵蓋範圍沒寫死(停用列、`(無)` 列、重複的檢查)**
severity: minor
blocking: 否(判準:數字與涵蓋差一兩個,實作時可補,但預期值不確定)
- spec 段落:〈範圍〉3、〈範圍〉4、〈用詞〉壞寫法片段。
- 佐證:我用 spec 描述的包裝法,對真型錄實測,得到 185 個(列, 檢查, 片段),去重成 (檢查, 片段) 是 180 個。叫不出的分別是 95 個和 92 個。spec 寫 180 段、91 段,跟哪個口徑都對不上。
- 另外:
  - 停用列 D-38 的對應檢查是 DATA-68,spec 沒說停用列要不要納入反查。納入會要求替一個「不出題」的列填〈叫不出〉的列。
  - D-2 觸發字刻意是 `(無)`,所以 API-1 的片段只要列入 D-2 就必然「叫不出」。這跟「有專一字面特徵的補觸發字」的步驟衝突。
- 建議:明寫「只算非停用列;`(無)` 列的片段一律進〈叫不出〉」,並用腳本重數後寫進預期值表。

**Finding 7:未見問題的節**
severity: clean
blocking: 否(判準:已讀並實測,無 finding)
- 〈範圍〉5(規則包筆記)與〈回退〉:已讀,無 finding。
- 〈範圍〉2 的「誰會跑自檢」:前掃的說法我對得上。`catalog_problems` 由 `t_kt_catalog_*` 測試呼叫,`skills/` 的改動不被判成純文件。
- 效能:185 次切段加載入 scripts/lumos 合計約 0.37 秒,每次 `catalog_problems` 加一道反查,不會讓 35 處呼叫變慢到成問題。
- 新增兩節放在〈情境決策表〉之後,`dt_table`/`_dt_header` 只掃到下一個 `## `,`_main_names` 只認主題前綴的列編號,我看不到被新表誤讀的路徑。

**實務隱患鏡頭(此功能碰到的風險類)**
- 守衛面(自檢會擋推送):有隱患,見 Finding 1、3、4。自檢變嚴後,現有型錄的 95 段全部要處理,擋人的是假的反查結果而不是真漏洞。
- 觸發字變多導致情境段變多:spec 已列,頻率量法沿用 E9。我沒有重新量 Now in Android 文件頻率,標 ⚠ 未查證。
- 金流、對外送出、不可逆:無。理由:只讀本機型錄與 `.api`,退提交即回原狀,跟 spec 的「已排除」一致。
- 資安:無。理由:沒有外部輸入進程式,`.api` 是釘版的官方原檔,只做文字抽名。

總結:最嚴重 severity 是 major,blocking 共 4 條(Finding 1、2、3、4)。
