severity: major

審查對象是 r2 修訂稿。我下載了 1.10.2 的 klib 與 JVM 兩份官方清單,照 spec 的規則抽名稱,再載入真的 `check.py` 與 `scripts/lumos` 跑反查。repo 沒被動過,`__pycache__` 已被 gitignore。臨時檔在 `/tmp/lumos-seat-work/情境決策點窮舉與壞寫法要叫得出/正確性-sonnet/`,等編排者收貨後刪。

## Findings

**F1 JVM 補來源的「還原讀取函式」規則,照字面做會憑空生出名稱、漏掉真名稱**
severity: major
blocking: 是——抽法照字面做出的母體跟真實公開名稱對不上,「真型錄 應回空」那條條款無法成立。
- 位置:〈用詞〉公開名稱的「補來源 JVM 清單」那一條。
- 引句:「不帶參數的 `getX`/`isX` 讀取函式還原成屬性名(首字大小寫兩種都跟 klib 比,klib 都沒有才以首字小寫收)」
- 實測一:`isX` 沒有「還原」的意思,屬性名本來就叫 `isX`。照字面剝掉 `is`,`isActive ()Z` 變成 `active`,`isCancelled` 變 `cancelled`,另有 `completed`、`locked`、`empty`、`lazy` 等,都不在 klib 裡,全被當成新名稱收進母體。
- 實測二:klib 裡的 `getCompletionExceptionOrNull`、`getChildJobCancellationCause`、`getResult` 是真的函式名(klib 第 243、330、478 行)。spec 只拿還原後的名字去比,所以這些會多收 `completionExceptionOrNull`、`childJobCancellationCause`、`result` 三個假名稱。
- 實測三:全大寫常數的讀取函式 `getRECOVER_STACK_TRACES` 會被「首字小寫」收成 `rECOVER_STACK_TRACES`。
- 實測四:`ChannelResult` 的 `constructor-impl` 去掉 `-impl` 後變成 `constructor`。`equals-impl0` 因為後綴是 `-impl0`、不被規則去掉,整串原樣成為名稱。
- 實測五:單例物件的 `INSTANCE` 欄位被收成名稱(klib 沒有),寫 Kotlin 的人不會打這個字。`setValue` 這類 setter 也被收進來,而 klib 裡是屬性 `value`。
- 後果:這些假名稱每個都要在〈API 決策點〉佔一列,例如 `rECOVER_STACK_TRACES`。不佔的話 S1 就紅。
- 我的簡化抽法在 JVM 補來源上多收 87 個名稱,其中約 20 個像上述這種假名稱。

**F2 klib 與 JVM 兩邊的排除規則不對稱:klib 排掉的,JVM 補來源又加回來**
severity: major
blocking: 是——母體內容取決於實作者怎麼補,「母體裡有、表上沒有」這道檢查會被噪音淹沒。
- 位置:〈用詞〉公開名稱的主來源與補來源兩條。
- 引句:「不收 `<init>`、`<get-…>`、`<set-…>`、`Any` 的 `equals`、`hashCode`、`toString`、資料類別自動產生的 `componentN` 與 `copy`、`Companion`;套件路徑含 `internal` 的不收」
- 引句:「跳過標 `synthetic` 的、`access$` 開頭的、`…Kt` 門面類別名、類別名含 `$` 的類別本身」
- 這份排除清單只寫在 klib 那一條。補來源只收「klib 裡沒有」的名稱,而 klib 已經排掉的 `Companion`、`copy`、`component1`、`toString`、`hashCode`、`equals`,JVM 清單都有:`field Companion` 有 2 筆,`CoroutineId`/`CoroutineName` 的 `component1`、`copy`,`toString ()` 有 12 筆。照字面,它們全會被當成「klib 沒有」加回來。
- `internal` 排除也一樣:JVM 那條沒有寫。`kotlinx/coroutines/flow/internal/ChannelFlow` 在 JVM 清單第 1218 至 1232 行的 `collectTo`、`fuse`、`produceImpl`、`dropChannelOperators`,以及 `debug/internal/DebugProbesImpl` 的 `dumpCoroutinesInfo` 等,都會回流。
- klib 這邊也有洞。成員行(例:`abstract suspend fun collectTo(...)`)本身不帶套件,「套件路徑含 `internal`」只能靠記住外層類別的標頭才判得出來,spec 沒寫。
- 升版時更糟:1.11.0 的 JVM `.api` 新增了 `kotlinx/coroutines/internal/*` 一整批公開類別(`addLast`、`peek`、`unwrapImpl`、`synchronizedImpl` 等),我數到約 50 筆非 synthetic 的 internal 條目。

**F3 帶點觸發字與停用字的「外層宣告寫法」沒有定義,spec 自己的例子算不出來**
severity: major
blocking: 是——spec 自己舉的 `SharingStarted.Lazily` 例子,照字面算不出預期。
- 位置:範圍 1 第一種歸屬;範圍 2 反向;`決策不問` 的「在停用字表裡」判法。
- 引句:「觸發字帶點的(`SharingStarted.Lazily`)比名稱前加上外層宣告的寫法(`SharingStarted.Lazily`),兩種寫法任一搜得到就算」
- klib 第 88 行寫的是 `final val Lazily`,其簽名註解是 `SharingStarted.Companion.Lazily`。外層宣告寫法得先丟掉 `Companion`,spec 沒說。
- `Channel.UNLIMITED` 的外層更麻煩:klib 的簽名是 `Channel.Factory.UNLIMITED`,使用時寫 `Channel.UNLIMITED`。「丟掉 `Factory`」沒有通則可推。
- 這兩個名稱對應的 `SharingStarted.Lazily`、`Eagerly` 在 STATE-4 的壞寫法裡,屬於接下來一定要加觸發字的那批。
- 反向沒有寫帶點寫法。範圍 2 反向只說「照搜」。一個帶點觸發字(`SharingStarted.Lazily`)永遠搜不到簡名 `Lazily`,所以 D-5 加了這個字、表上卻把 `Lazily` 標成 `決策不問`,反查會靜默通過,正是這份計劃要消滅的「兩邊不同步」。
- 停用字表裡是 `Dispatchers.IO`、`Dispatchers.Default`(帶點),母體名稱是 `IO`、`Default`,「名稱在停用字表」的比對一樣沒有定義。
- 範圍 5 的預期值表沒有任何一列驗帶點觸發字。

**F4 〈叫不出的壞寫法〉的 `範本 T<n>` 只核小節標題,沒核片段在不在那一節**
severity: major
blocking: 是——這就是 r1 已修過的「一個編號替所有片段背書」,只在規則那一種改由上補了,範本這種還開著。
- 位置:〈用詞〉「改由」的 `範本 T<n>` 項。
- 引句:「範本那一組有 `### 壞寫法:<對應檢查>` 小節(〈API 決策點〉那邊:那一組任一個壞寫法小節的程式碼含這個名稱)」
- 「程式碼含這個名稱」只限 API 那邊。〈叫不出的壞寫法〉那邊只要有同編號的標題就過。
- 實測:file: `skills/kotlin-idioms/test-templates.md:2044` 與 `:2076`。T2 裡 API-8 只有兩節,「flatMapConcat 排隊」與「每次 launch 不取消前一個」,沒有任何一節含 `flatMapMerge`。若 `flatMapMerge` 日後落進叫不出表並寫 `範本 T2`,檢查會放過。
- 一個對應檢查常有多段壞寫法,範本只覆蓋其中一種,同一個洞。

**F5 改由「規則」的逐字比對:註解、子字串都算數,API 那邊等於空轉**
severity: major
blocking: 是——沒有 ast-grep 的本機與推送前閘只跑這個文字比對,而它會放過規則其實不管的寫法。
- 位置:〈用詞〉「改由」的 `規則 <id>` 項,以及範圍 2 的 `決策不問:規則 <id>`。
- 引句:「那條規則在會擋的 `rules/` 目錄,訊息開頭引的編號等於對應檢查;而且片段(〈API 決策點〉那邊是名稱)要逐字出現在 `samples/bad/<id>/` 的某支壞例檔裡」
- 實測一(註解):STATE-4 的壞寫法片段 `SharingStarted.Lazily`,在 `samples/bad/kt-statein-lazily-in-viewmodel/` 的壞例檔第 1 行出現,那行是註解:「// 只管 import 後直接寫 Lazily 的長相;SharingStarted.Lazily 歸 kt-statein-lazily-or-no-timeout」。註解明寫「SharingStarted.Lazily 歸另一條規則」,這條規則其實不管它。逐字比對卻通過,規則訊息開頭也確實是 `[STATE-4]`。
- 實測二(子字串):名稱沒有字界。`join` 會命中 `joinAll`,`cancel` 會命中 `cancelAndJoin`。`async`、`value`、`get` 這類字在任何一個壞例檔裡都有。spec 現成就有 `_kt_trigger_re` 帶字界,可以直接借。
- 實測三(API 那邊空轉):S5 對 API 名稱只要求「含這個名稱的行至少一行被報」,任何無關的 BAD 行都能滿足。例如名稱 `delay`(停用字)寫 `決策不問:規則 kt-sequential-independent-await`,只要該規則的壞例有一行含 `delay` 被報就過,完全不證明那條規則管 `delay` 帶的決策。
- API 決策點表沒有「對應檢查」欄,所以「訊息開頭引的編號等於對應檢查」與「`T<n>` 等於通電批次值」對 API 名稱都無從比對,spec 只替片段那邊寫了替代條件。

**F6 完整模式的「片段所在那一行要被報」用相等比對,會誤判合法的規則**
severity: minor
blocking: 否——只是誤報、可以靠改樣本繞,不會漏放壞寫法。
- 位置:範圍 4 的 `route_rule_hits_problems`。
- 引句:「〈叫不出的壞寫法〉的片段所在那一行要被報」
- file: `configs/ast-grep/kotlin-android/check.py:916`。`scan()` 回的是比對節點的起始行。
- 實測:file: `configs/ast-grep/kotlin-android/samples/bad/kt-nested-collect/src/main/kotlin/kt-nested-collect.kt:8`。外層 `query.collectLatest { q ->` 在第 8 行,被報的內層 `filter.collect {...} // BAD` 在第 9 行。FLOW-1 的片段 `collectLatest` 在第 8 行,規則實際報第 9 行,相等比對會判這條規則沒擋。
- 片段 `collect` 在同一支檔案多行出現(第 2、3、8、9 行),「所在那一行」有多個,spec 沒說取哪一個、是任一個還是全部。

**F7 「95」在 spec 自己定義的口徑下是 103**
severity: minor
blocking: 否——最後會被重數的統計測試抓到,只是計劃裡的數字與工作量說明是錯的。
- 位置:〈用詞〉壞寫法片段(白話、範圍 5、〈叫不出〉的 95 處)。
- 引句:「2026-11-12 用 `sweep/` 的腳本照這個口徑數:184 個,叫不出 95 個」
- 〈用詞〉「叫得出」說 `TEST-` 片段改用測試路徑、一律叫不出。但 file: `governance/review-reports/情境決策點窮舉與壞寫法要叫得出/sweep/sweep2.py.txt` 對所有片段都包成 `X.kt`,沒套這條。
- 實測:照 spec 現在的定義(`TEST-` 用 `app/src/test/java/x/XTest.kt` 並先過 `_PITFALL_DIFF_TEST_PAT`、`_stack_changed_ok`),184 段裡叫不出的是 103 段,不是 95。多出的 8 段全是 `TEST-`:
  - `UnconfinedTestDispatcher`(D-21 / TEST-15)
  - `runTest(UnconfinedTestDispatcher()) {...}`(D-49 / TEST-14)
  - `runTest { val vm = ... }`(D-49 / TEST-6)
  - `flow.test { awaitItem() }`(D-50 / TEST-18)
  - `awaitItem()`(D-50 / TEST-19)
  - `registerIdlingResource`(D-51 / TEST-30)
  - `waitUntil`(D-51 / TEST-30)
  - `onNodeWithText("子文字")`(D-51 / TEST-32)
- 順帶:D-21、D-49、D-50、D-51 在真實推送中完全問不到,因為測試檔不出情境段。範圍 5 只說「叫不出的補觸發字、否則進表」,沒有說 `TEST-` 的片段一開始就該直接進表。照 95 去補字會對這 8 段白補。

**F8 歸屬欄位的組合語法沒定義**
severity: minor
blocking: 否——實測目前真母體的多列命中名稱都能整串歸到所有命中的列,不會卡死。
- 位置:範圍 1 的四種歸屬與範圍 2 反向。
- 引句:「那一列的觸發字搜得到這個名稱,但意思不同(例 D-59 資料同步衝突的觸發字 `merge` 搜得到 Flow 的 `merge`)」
- 實測:真觸發字對 klib 名稱反查,多列同時命中的有 `Channel`(D-7、D-16)、`collectLatest`(D-4、D-16)、`combine`(D-5、D-6、D-35)、`CoroutineDispatcher`(D-20、D-55)、`coroutineScope`(D-1、D-8)、`stateIn`(D-5、D-6、D-15、D-49)。
- spec 沒說「歸 D-20、同時撞名 D-55」能不能同格表示、`撞名` 能不能列多列。四種歸屬寫成互斥,實作者要自己發明語法。
- 目前這些名稱每列意思都真的相關,可以全歸,所以現況不會卡死。但日後有人讓其中一列意思不同時,表達不出來。

**F9 1.11.0 的數字不可重現,且是補進來的未查證宣稱**
severity: minor
blocking: 否——S1 只需要 `associate` 在 1.11.0 才有,這點是對的。
- 位置:〈依據來源〉表的 1.11.0 那一列。
- 引句:「2026-11-12 比對多 17 個條目、10 個不重複的名稱,例 `associate`」
- 實測:我把 1.11.0 與 1.10.2 的 `.api` 逐行 diff。非 synthetic 的條目有 96 筆(約 43 個不同名稱,含 internal);只算非 internal 的 `static final fun`,條目 31 筆。
- 不論怎麼切,都沒能得到「17 條、10 名」。說不清篩選口徑的宣稱,下一個人無法重驗。

**F10 母體檔本身會觸發推送閘的風險型樣**
severity: minor
blocking: 否——本案本來就屬守衛面,要過完整審;這點只是別被嚇到。
- 位置:範圍 5 與〈實務隱患〉。
- file: `scripts/lumos:64430` 的 `_stack_changed_ok` 只用副檔名黑名單,`.api` 不在黑名單裡。
- 實測:`_PITFALL_DIFF_PATTERNS`(`scripts/lumos:40038`)的 `\bLock\s*\(`(忽略大小寫)對 klib 的 `abstract suspend fun lock(...)` 與 JVM 的 `public abstract fun lock (...)` 各命中 1 次,屬「併發」類。
- 後果:兩份母體檔會被當程式碼掃,拿到風險型樣,把這次推送判成 high。實測 `_stack_changed_ok` 對新的 `.api` 路徑回 True。
- 計劃沒提這個,實作者推送時可能嚇一跳,也可能想用黑名單繞開,後者反而會讓母體檔不被看見。

## 逐節結論

- 〈用詞〉其餘條目(被問到、型錄主表列編號、會擋的規則、停用列、段放行、API 母體、叫得出、改由的 `代碼審`/`不是寫法`):已讀,無 finding。
- 白話與 PRIOR-ART:klib 層的描述(`final val Lazily`、`final const val UNLIMITED`、成員 `abstract fun trySend`)、「klib 不含 JVM」、JVM 專屬名稱(`runInterruptible`、`future`、`asExecutor`、`ticker`)我都對照原檔驗過,屬實。
- 範圍 3、4(接法)、6、不做、回退:已讀,無 finding。
- 〈實務隱患〉:
  - 效能與記憶體:184 段包成檔、各切一次,毫秒級,不是問題。
  - 母體雜湊:`.gitattributes` 沒有行尾轉換,klib 檔無 CR、無行尾空白,位元組穩定,逐位元組釘死可行。
  - 剝字串的落單引號:對 184 段實測,只有字面含中文字串的幾段(例 `showError("網路錯誤"); retry()`),觸發字在字串外都叫得出,不構成漏洞。
- 〈天花板〉與 REVISIT:已讀,無 finding。
- 預期值表:S1 第 1、2 列(`associate` 沒分類、`flatMapMerge` 歸屬搜不到)與第 4 列(`merge` 標 `撞名 D-59`)算得出來。S1 第 3 列的 `UNLIMITED` 單看簡名也算得出,但 F3 的帶點寫法會影響它的正向核對。

最嚴重 severity:major;blocking 共 5 條(F1、F2、F3、F4、F5)。
