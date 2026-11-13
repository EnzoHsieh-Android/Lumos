severity: minor

這份 diff 的資料大致站得住,我沒找到會讓測試擋下或讓該問的情境被默默放行的錯,所以沒有 major。以下 7 條都是文件與資料的精度問題,另附幾項我實際重跑的結果。

**我重跑確認屬實的部分**
- `--catalog-only` 回報 0 個問題。
- 用 ast-grep-cli 0.51.1 跑 `check.py --sg`,得「規則 228 條,問題 0 個」。所以〈叫不出的壞寫法〉5 條「規則」改由的 `// BAD` 行與起訖行說法屬實。
- 兩份母體檔的 sha256 與型錄第一行一致,也與 raw.githubusercontent.com 上 1.10.2 標籤的原檔一致。
  - LICENSE.txt 第 190 行確有 README 引的那句版權文字。
  - 該版 NOTICE.txt 回 404,「沒有 NOTICE 檔」屬實。
  - 1.11.0 的 klib 清單有 `associate`(8 處),1.10.2 沒有。
- 我用程式重算型錄的數字,與筆記一致:
  - 公開名稱 426 列;D-n 62、撞名 4、決策不問主表列 19、決策不問代碼審 90、無決策 262。
  - 叫不出 111 列:代碼審 104、規則 5、不是寫法 2;`<無片段>` 11 列。
  - 233 支壞例檔有 199 支標 `// BAD`。
- 測試名都存在,實跑全過:`api_decision_points` 28、`bad_snippets_reach` 22、`api_family_e2e` 4、`kt_situation_segments` 39。
- 我改壞幾列再跑自檢,都有紅:`last` 改成 `決策不問 代碼審`、`emit` 改成 D-7、`Lazily` 加 D-6、`supervisorScope` 漏 D-9、`coroutineScope` 漏 D-9、`mapLatest` 改成 `無決策`。
- kotlinlang.org 上 `mapLatest` 與 `transformLatest` 的文件寫的是「新值來時取消前一個轉換」,所以歸 D-4 是對的。
- D-60 拿掉 `in bigList` 沒有漏掉真的壞寫法。PERF-26 的壞寫法是 `bigList.contains(x)`,仍由 `contains(` 抓到。`bigList` 只剩示意變數名這一段,已列進叫不出表。
- 我挑了 30 多列,對照 kotlinx.coroutines 官方文件與原始碼逐列查。`ATOMIC`、`LAZY`、`UNDISPATCHED`、`Eagerly`、`Lazily`、`flatMapConcat`、`flatMapMerge`、`first`、`tryEmit` 等的理由都屬實。`cancelFutureOnCancellation` 是 `DeprecationLevel.WARNING`,「已棄用」也屬實。

**Findings**

severity: minor
blocking: 否
〈API 決策點〉宣稱每個公開名稱恰好一列,但 JVM 專屬的公開型別完全沒進母體。
引句:「JVM 專屬名稱靠人手列在 `jvm-only.txt`,列漏的不會被點到(自檢只核列出來的那幾行對不對)」
- 我用 JVM 清單抽出的 `kotlinx/coroutines` 公開型別,減掉 `_api_names` 的結果,剩 `ActorScope`、`CopyableThreadContextElement`、`CoroutineId`、`ExecutorCoroutineDispatcher`、`ThreadContextElement`、`TickerMode` 共 6 個。
- 它們在 klib 清單裡 0 筆,不在表上也不在 `jvm-only.txt`。
- `jvm-only.txt` 檔頭與驗證紀錄都說初版只拿 `…Kt` 門面類別的函式做差集,型別根本沒判過。
- 〈天花板〉2 只承認「類別成員與屬性不收」,沒講頂層型別。README 的「JVM 專屬、klib 清單沒有的公開名稱」讀起來是全收。
- 這 6 個多半會標 `無決策`,但 `TickerMode` 的 FIXED_PERIOD 與 FIXED_DELAY 是調度決定,`ExecutorCoroutineDispatcher` 是自建執行緒池的型別。
- 修法:補判這 6 個,或在〈天花板〉2 與 README 寫明 JVM 專屬型別不收。

severity: minor
blocking: 否
有幾列的理由與事實不符,歸屬本身沒錯。
引句:「| isClosed | 無決策 | 舊版已棄用的 API |」
- `isClosed` 是 `ChannelResult.isClosed`(klib 第 535 行),沒有棄用;官方 Channel.kt 第 220 行的範例就在用 `result.isClosed`。
- `isClosedForReceive` 與 `isClosedForSend` 標成「ChannelResult 的取值/判斷輔助」,其實是 Channel 的屬性(官方 Channel.kt 第 76 行 `val isClosedForSend`)。
- `CoroutineName`、`currentCoroutineContext`、`emit` 套用「建流或轉型的小工具,不帶決策」。這句對 `emit` 與 `CoroutineName` 不成立,是範本理由被硬套。
- 自檢只檢查理由非空。三個月後有人照理由推論會被誤導。

severity: minor
blocking: 否
`決策不問 <主表列>` 有兩列指到講別的意思的列,理由欄自己也承認。
引句:「| last | 決策不問 UI-21 | 只取最後一筆要等流結束;型錄 UI-21 寫到的是清單的 last |」
- UI-21 講的是 `derivedStateOf` 誤用,壞寫法片段 `"$first $last"` 的 `last` 是字串樣板裡的變數,跟 Flow 的 `last()` 無關。
- 同系的 `lastOrNull` 卻標 `決策不問 代碼審`。這是因為自檢規定「有主表列寫到就必須指向它」,而它分不出同名異義,只好硬指。
- `Default | 決策不問 CO-39` 也一樣:CO-39 是「協程裡改非執行緒安全集合」,`Default` 只是壞例片段 `async(Default) { list.add(…) }` 的附帶字,CO-1 才是講調度器的列。
- 結果是 `last` 與 `Default` 的反查實際落在不相干的片段上,等於沒人負責。
- 建議在理由欄或自檢加「同名異義」的出口(例如允許 `決策不問 代碼審(同名)`),不要靠指到不相干的列來湊。

severity: minor
blocking: 否
104 列「代碼審」的理由全是同一個樣板,沒寫代碼審要看什麼。
引句:「D-1 的觸發字抓不到這種寫法(字面太常見或沒有專一的字);代碼審照 API-1 看」
- 計劃〈範圍〉3 與〈實務隱患〉都說「理由要寫代碼審要看什麼」,拿它擋「代碼審變成新的垃圾桶」。
- 實際只有「照 X 看」,指向主表列編號,沒有內容。
- 自檢也只檢查非空,所以這道防線沒有牙齒。RETIRE-IF 第二條用「代碼審占一半以上」量化這件事,理由欄卻無從區分。

severity: minor
blocking: 否
D-4 的「不適用時」欄沒跟著更新,仍只寫 `collectLatest`/`flatMapLatest`。
引句:「不要 `collectLatest`/`flatMapLatest` | debounce、flatMapLatest、collectLatest、viewModelScope.launch、flatMapConcat、flatMapMerge、mapLatest、transformLatest」
- 標準寫法欄已加上 `mapLatest` 與 `transformLatest` 同類,「每一次都必須做完」時一樣不能用這兩個,但不適用欄沒提。
- 盲判看的是這個欄位,只看欄位的人會漏判 `mapLatest` 用在寫入的情況。
- 觸發字加進 `flatMapConcat` 與 `flatMapMerge` 也一樣,它們是「每一次都做完」那一側的寫法,而 D-4 的證據樣式例外段(`\.collect\s*\{|\bChannel\b`)對不到它們。合法使用的作者只能答「不適用」。

severity: minor
blocking: 否
筆記裡有幾個數字已過期,與最終資料不符。
引句:「全表 184 段壞寫法有 95 段叫不出」
- 這句在 Systems/kotlin規則包的新 WHY 裡。同一批的計劃寫設計時 103 段,最終統計是 195 個單位叫不出 111 個,三個數字並存。
- 驗證紀錄寫 `kt_catalog_stats_consistent` 106 案,我實跑是 128 passed,數字沒更新。
- 這些數字不影響測試,但三個月後會誤導人。

severity: minor
blocking: 否
「規則」改由的 `collect` 單字片段,理由字面比實際保證的多。
引句:「| D-5 | FLOW-1 | `collect` | 規則 kt-nested-collect | kt-nested-collect 在壞例的 // BAD 行抓得到這段 |」
- 規則只在巢狀 collect 時報,片段 `collect` 是單一識別字,幾乎任何壞例行都含它,「抓得到這段」的驗證接近空轉。
- 計劃只擋了單字片段用「範本」,沒擋用「規則」。
- 我的判斷是無害:實際壞寫法(巢狀 collect)確實被規則抓。但措辭過強,建議理由寫成「規則抓巢狀 collect」。

**固定席與圖譜鏡頭**
這次沒附固定席節點,以下是我自己讀 Systems 兩篇筆記的結果。
- **Systems/kotlin規則包:** 新增的 WHY、PITFALL 有 `[出處]`、`[因]` 或 `[根因]`、`[test:]`,測試名都存在。`about_code` 補列了三個母體檔,符合「每支檔有家」。沒碰 ★INVARIANT★ 等合約行。
- **Systems/棧別提問表態閘:** 只加一條 WHY(`_kt_sit_path_ok` 共用)。scripts/lumos 第 39819、39969、69407 行確有這支函式與兩處呼叫,`check.py` 第 1064 行也呼叫它,與計劃一致。`t_kt_situation_segments` 39 案全過,表示抽函式沒改變行為。
- **兩篇筆記的影響判定:** 都不影響既有合約。

**未能重現**
- NIA 量測的 766→775、516→515 這幾個數需要 Now in Android 的指定提交,我沒有拉。其中情境段數減 1 而配對數加 9 看起來合理但無法驗證,我不據此報問題。

最嚴重:minor,blocking 0 條
