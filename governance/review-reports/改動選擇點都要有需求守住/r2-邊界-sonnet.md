severity: major

## b1 候選壞法要「運算元範圍」,全文沒有定義運算元怎麼取
severity: major
blocking: 是——照字面實作,`a`、`b`、`true`、`false`、`!b` 這幾類候選取不出可編譯的壞法,每個實作者取法不同。
- 位置:〈用詞〉選擇點表(ROR、LCR、AOR、UOI)與〈用詞〉選擇點。
- 問題:LCR 候選含 `a`、`b`,ROR 候選含 `true`、`false`,AOR 候選含 `a`、`b`。這些都要先知道運算元從哪到哪。沒有 Kotlin 語法樹,純文字取運算元要處理優先序、括號、呼叫鏈、lambda、`as`/`is`/`in` 中綴、字串樣板,全文一句沒寫。
- 例 1:`if (x.size + 1 > limit && enabled)` 的 `>` 換成 `true`,左運算元是 `x.size + 1`,不是 `1`。取錯就產生 `if (x.size + true && …)`,編不過,落成 no_result 擋推送。
- 例 2:S2 要求行尾 `&&` 照算。`if (a > 0 &&` 換行 `b < 3)` 的 `&&` 換成 `a` 或 `b`,運算元落在另一行,單行 `old`/`new` 做不出合法壞法。spec 沒說這種行只出「換運算子」類候選,還是要把 `old` 擴成多行。
- 後果:身分雜湊(`old_sha`、`new_sha`)要在 B 版重算再對,只有同一份實作對得上自己。spec 的預期值表沒有一列釘死運算元範圍。
引句:「LCR:`a && b` → `a || b`、`a`、`b`、`true`、`false`;`||` 同形。」
引句:「運算子成員要兩側是空白或換行(`a > b`、行尾的 `a &&`);」

## b2 SBR 可刪判定缺「陳述位置」,引數行、lambda 結果行、無大括號本體都會被刪
severity: major
blocking: 是——判準只看那一行自己的形狀,看不到它是陳述還是別的結構的一部分,會批量產生編不過或改到別的陳述的壞法。
- 位置:〈用詞〉選擇點表 SBR 列;〈天花板〉2。
- 問題:判準是「一行恰好一個完整呼叫、括號成對、不是宣告、不是 return、不是函式最後一句」,全是單行屬性。論文 A.1.12 不可刪清單有「呼叫參數」、「非 void 函式唯一陳述」、含 return 路徑的區塊。spec 只翻了一部分,且「函式最後一句」不含 lambda 最後一句。
- 例 1:多行引數 `combine(` 換行 `    flowA()` 換行 `    flowB()` 換行 `) { a, b -> … }`,`flowB()` 這行通過四項判準,刪掉變成引數數量錯誤,編不過。
- 例 2:`val r = list.map { x ->` 換行 `    transform(x)` 換行 `}`,`transform(x)` 是 lambda 的結果值,刪掉型別錯,編不過。
- 例 3:無大括號 `if (ready)` 換行 `    start()`,刪掉 `start()` 後 `if (ready)` 改去管下一個陳述。這能編過,但是改到別的陳述的壞法,殺不殺掉都不能算這一行的需求。
- 〈編不過的形狀〉救不了:SBR 的壞法恆為空,(列號, 壞法) 這個鍵對 SBR 沒有分辨力。天花板 2 只說「多行呼叫鏈的 SBR 不做」,沒提引數行與 lambda 結果行。
- 補法:要求該行起點的括號深度為 0,且不在 lambda 結果位置。
引句:「只限那一行恰好是一個完整的呼叫、括號成對、不是宣告、不是 return、不是函式最後一句的運算式」
引句:「不照格式寫的運算子會漏、多行呼叫鏈的 SBR 不做、乾節點只認型錄寫的形狀」

## b3 〈一行一個壞法〉與〈壞法身分〉對不唯一的行互相矛盾,S3 後半句走不到
severity: major
blocking: 是——兩處字面指示相反,一種讀法下重複的行永遠不會被標「不唯一」,悄悄放行。
- 位置:〈用詞〉一行一個壞法、壞法身分、S3、預期值表 S3 第 2、3 列。
- 問題:一行一個壞法的篩選條件是「新那一行在整支檔裡恰好一次」,不滿足就換下一個候選,「一個都沒有就這一行沒有壞法」。壞法身分卻說整支檔不唯一時往上下各多帶一行,最多 2 行,仍不唯一才標「不唯一」。
- 照第一段字面實作,重複的行(兩個 `if (x > 0) return` 完全一樣)在挑壞法時就被丟掉,變成「沒有壞法」,推送閘不擋。S3 預期的「標不唯一、不跑」與範圍 4「不唯一要擋」都走不到。
- 「新那一行」若指「變異後的那行」,這個條件沒有動機,且與身分段無關。兩種讀法都需要改寫成一句話。
引句:「一個都沒有就這一行沒有壞法」
引句:「整支檔不是恰好一次時依序往上、往下各多帶一行,最多前後各 2 行」
引句:「那一行不唯一時 應 往外帶行求唯一,仍不唯一標不唯一」

## b4 「已知編不過的形狀」沒有定義;若取自治理帳,壞法會隨帳漂移,違反穩定回報
severity: major
blocking: 是——挑壞法的輸入不明,取自帳的話同一行內容不變也會換壞法,B 版重算的雜湊就對不上。
- 位置:〈用詞〉一行一個壞法、編不過的形狀、S3。
- 問題:全文只有一處定義與「編不過」有關:同一個 (列號, 壞法) 在 `--stats` 累計 3 次以上,列為給人看的「表要改」候選。它是統計輸出,不是型錄裡的過濾表。〈一行一個壞法〉卻拿「已知編不過的形狀」當每次挑壞法的過濾條件。
- 若取自帳:同一行、同一內容,帳多一筆編不過累計,下次挑中的壞法就換了。推送閘用 B 版帳重算,跟 choice-kill 當時用的帳不同,`new_sha` 對不上,變成缺紀錄或過期,與「同一行內容不變,每次挑中的都一樣」互相打架。
- 若取自型錄:型錄沒有這一節,也沒有欄位。
- 驗證:對照 `scripts/lumos` 的 `cmd_guard_kill`,編譯失敗只回 `killed_unattributed` 加失敗摘錄,沒有任何「已知編不過」的結構可查。
引句:「同一行內容不變,每次挑中的都一樣」
引句:「同一個 (列號, 壞法) 在 `--stats` 累計 3 次以上列為」
引句:「推送閘在 B 版重算壞法再用雜湊對」

## b5 乾節點規則只有「那一行」或「函式本體」兩種範圍,擋不住多行 log 與斷言呼叫
severity: major
blocking: 是——論文的乾節點是語法樹節點,連同多行引數一起乾。這裡的行級比對,續行會漏出來產生壞法。
- 位置:〈用詞〉乾節點規則、S4、預期值表 S4。
- 問題:log、斷言、前置條件、時間的範圍是「那一行」。多行呼叫的續行不含呼叫名,不命中任何規則,仍會被挑壞法。
- 例:`Log.d(` 換行 `    TAG,` 換行 `    "n=${items.filter { it > 0 }.size}"` 換行 `)`,第三行的 `filter`→`filterNot` 是論文 A.1.1 明講不該產生的壞法。
- 例:`require(x > 0) {` 換行 `    "bad ${y > 1}"` 換行 `}` 的訊息行,`${y > 1}` 在剝字串後保留為程式碼,被挑 ROR。
- 這類壞法一律存活,每一個要人處置才能推,是論文 3.2.5 說最早也最有效的兩類(log、時間)的漏網。
- 缺的是:範圍要有第三種「整個呼叫(含多行引數與尾隨 lambda)」。
引句:「範圍(那一行、或整個函式本體)」
引句:「log(`Log.*`、`Timber.*`、`println`、`logger.*`)」

## b6 「整個函式本體」的範圍怎麼取沒定義,現成可用的 `_kt_sit_material` 會悄悄多壓
severity: major
blocking: 是——取錯方向是漏判(該有壞法的行被當乾節點),閘整段不報,沒有訊號可查。
- 位置:〈用詞〉乾節點規則(樣板方法、`@Module`、`@Provides`/`@Binds`)、排版。
- 問題:spec 只在排版處指名 `_kt_sit_material`。乾節點的函式本體範圍若沿用同一支,我實跑以下四種情況都出錯:
  - 運算式本體加 `init` 區塊:`class A(val a: Int) {` / `override fun toString() = "A" + a` / `init {` / `if (a > 1) check2()` / `}` / `}`,`init` 區塊的行(第 3 到 5 行)回的範圍是 (2, 5),整個併進 `toString` 的本體。`init` 裡的 `a > 1` 被當樣板方法本體壓掉,漏判。
  - 次建構子 `constructor() : this(0) {` 這幾行回 None,不知道在哪個宣告裡。
  - `@Module` 物件裡 40 個 `@Provides` 函式(160 多行),超過 120 行的位置回 None。範圍不到整個類別,A.3.2 的「`@Module` 類別本體」做不出來。
  - `@Provides` 單獨一行在 `fun` 上一行,`_KT_SIT_DECL_RE` 的註記只吃同一行,取到的範圍從 `fun` 開始,看不到註記。
- 這支函式的設計目的是情境題切段,不是找外層類別或註記,spec 沒要求另寫。
引句:「依賴注入模組(`@Module` 類別本體、`@Provides`/`@Binds` 函式本體)」
引句:「樣板方法(`equals`、`hashCode`、`toString` 整個本體)」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40083`
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39990`

## b7 UOI 的前置 `!` 與「兩側空白」邊界規則互斥,且布林運算元無從判定
severity: minor
blocking: 否——最常見的 `!x` 寫法落在規則外,只是少壞法,不是做錯。
- 位置:〈用詞〉選擇點表 UOI 列、選擇點。
- 問題:「拿掉前置 `!`」命中的是 `if (!ready)`、`&& !done` 這類,`!` 前面是 `(` 或空白,後面緊接識別字,兩側都不是空白。照「運算子成員要兩側是空白或換行」,這個候選永遠不會發生,而 spec 又說天花板 2 只漏「不照格式寫的運算子」,這是標準寫法。
- `b → !b` 要判斷運算元是布林,沒型別資訊只能猜。猜到非布林,`!` 加上去編不過,同 b1 的 no_result 噪音。
- 論文表 1 的 UOI 是 `a → {a++, a--}`、`b → !b`,沒有「拿掉 `!`」,這也不在 spec 的「跟論文不同」清單。
引句:「UOI:布林運算元 `b` → `!b`;拿掉前置 `!`。」

## b8 測試輔助路徑只補兩個資料夾名,KMP、輔助模組、僅有 androidTest 的模組仍被當正式碼
severity: minor
blocking: 否——只會多出必存活的選擇點,可靠判 not-requirement 放行。
- 位置:〈用詞〉改到的行、〈不做〉。
- 驗證:我實際呼叫 `_nodehome_is_test(path, layout)`(layout 用 `_nodehome_layout` 算出)。
  - 回 False,會產生選擇點:`shared/src/commonTest/kotlin/Helper.kt`、`shared/src/jvmTest/…`、`shared/src/androidUnitTest/…`、`shared/src/androidInstrumentedTest/…`、`core/testing/src/main/java/a/Util.kt`(NowInAndroid 式測試輔助模組)。
  - 在 `app/src/main/java/` 只有 `.java`、`src/androidTest/` 有 `.kt` 的模組,回 False。androidTest 判定要求同模組 `src/main` 有同副檔名的檔,見 `_nodehome_in_stack_test_dir`。
  - `testFixtures`、`sharedTest` 回 False,spec 已補。
- spec 補的是這兩個名字,沒有補通則(例如 `src/<名字>Test` 或 `Test` 結尾的 source set)。
引句:「另把 `src/testFixtures/`、`src/sharedTest/` 當測試」
引句:「不管非 Kotlin 專案;測試檔、測試輔助資料夾、`.kts` 不算。」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:48097`

## b9 API 兄弟寫法表在 Flow 與 Sequence 上常見編不過,`--import` 只能配 `--only` 逐筆
severity: minor
blocking: 否——spec 有 not-applicable 與 `--import` 兩個出口,只是代價高。
- 位置:〈用詞〉選擇點表 API 列、〈範圍〉2 `--import`、S21。
- 問題 1:`kotlinx.coroutines.flow` 沒有 `takeLast`、`dropLast`,Sequence 也沒有。`take`↔`takeLast`、`drop`↔`dropLast` 遇到這兩類接收者必編不過,表上沒有「接收者限定」欄。
- 問題 2:`first`↔`last`、`flatMapLatest`→`flatMapConcat`、`flatMapMerge` 在 Flow 上是擴充函式,檔案若沒有對應 import,壞法要補一行。`_KILL_IMPORT_RE` 不收萬用字元。S21 的主角正是 `flatMapLatest`→`flatMapConcat`,手動驗證步驟沒提 `--import`,實際要加。
- 問題 3:宣告行 `fun <T> Flow<T>.first()` 也命中 `.first(` 這個呼叫形,改名後整個檔編不過。API 列沒有 SBR 那樣的「不是宣告」。
- 後果:缺 import 的壞法被迫判 not-applicable 才能推,語意上是「適用但缺 import」,每筆都是一次判斷。
- 補法:選擇點表加「需補的 import」欄,並讓 choice-kill 自動帶入。
引句:「`take`↔`takeLast`、`drop`↔`dropLast`」
引句:「`--import`:壞法要補的 import(同前置計劃),只能配 `--only`。」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:26751`

## b10 論文表 1 與 3.2.4、2.3 的抄寫有差,且不在「跟論文不同」清單
severity: minor
blocking: 否——差異讓候選變少或換口徑,不會讓閘做錯,但「照論文」的宣稱不實。
- 位置:〈用詞〉選擇點表、一行一個壞法、回報上限、PRIOR-ART。
- ROR:論文表 1 的 `a > b` 候選是 `a < b, a <= b, a >= b, true, false`,spec 少了 `<=`(整個取反的那個)。
- AOR:論文 `a + b` 候選含 `a * b, a / b, a % b`,spec 只列 `-`、`a`、`b`,「`-`、`*`、`/`、`%` 同形」沒展開 `*` 該換成什麼。
- UOI:論文沒有「拿掉前置 `!`」,是 spec 自加的。
- 打散單位:論文 Listing 2 是先洗運算子、第一個能產生的運算子只產一個壞法。spec 把「選擇點 × 候選壞法」整個攤平洗牌,ROR(4 個候選)比 SBR(1 個)中的機率高很多。後果沒寫。
- 3.2.4:論文那節講的是「壓掉互相等價的壞法」(例:對 `nullptr` 的 LCR,`if (x != nullptr)` 的候選互等價),spec 把它當作固定種子的出處,沒有等價壓抑規則。
- 2.3:回報上限論文數的是 changelist 的全部檔數,spec 數 `.kt` 正式碼檔數。口徑更嚴,沒標。
- A.1.6:spec 拿它說明「測試裡被假實作換掉」,但 A.1.6 講的是 Beam、TensorFlow 這類管線組裝碼不被測,假實作取代是 A.3.2 與 A.1.4 的理由。
引句:「ROR(論文表 1):`a > b` → `a >= b`、`a < b`、`true`、`false`」
引句:「AOR:`a + b` → `a - b`、`a`、`b`」
引句:「理由同論文附錄 A.1.4 時間類與 A.1.6 框架類:測試裡被假實作換掉」
引句:「一次推送要處置的存活最多」

## b11 乾節點規則第一版漏了論文自己說貢獻最大的旗標與提早 return,PRIOR-ART 卻寫已含
severity: minor
blocking: 否——乾節點規則設計上由人增補(論文 3.1),但 spec 的兩處說法互相矛盾。
- 位置:PRIOR-ART 與〈用詞〉乾節點規則。
- 問題:PRIOR-ART 列的附錄 A 內容含「提早 return、旗標」,〈用詞〉第一版清單沒有。論文 3.2.5 明講最早實作的三條(log、時間、旗標)貢獻最大的生產力提升。`BuildConfig.DEBUG`、feature flag 的 gate 在 Kotlin 專案很常見,沒有它們會是第一個噪音來源。
- 另缺:A.1.20(集合大小與 0 比較)、A.1.11(浮點與常值比較)、A.1.24(`coerceIn`、`minOf`、`maxOf` 限界)。
引句:「提早 return、旗標、資料流 flush/close、依賴注入」
引句:「第一版照論文附錄 A 譯成 Kotlin:log(」

## b12 幾條乾節點的形狀寫得過寬,會把真邏輯整行壓掉
severity: minor
blocking: 否——方向是漏判,天花板 8 已承認「乾節點規則寫錯會整類放過」,但這幾條現在就看得出會誤壓。
- 位置:〈用詞〉乾節點規則。
- `Firebase*`:`FirebaseAuth`、`FirebaseRemoteConfig` 都命中,整行當監控壓掉。例:`val ok = FirebaseAuth.getInstance().currentUser != null && x > 1`,`x > 1` 的 ROR 被壓。
- `error`、`check`、`assert`:沒寫是限定名還是裸名。專案自己的 `Result.error(…)`、領域函式 `check(permissions)` 會誤判。
- `ArrayList(`、`HashMap(`、`StringBuilder(`:規則本意只壓容量引數,範圍卻是「那一行」。`ArrayList(items.filter { it > 0 })`(複製建構)整行壓掉。
- `Duration`:任何含這個字的行都壓,`if (session.age > Duration.ofMinutes(30))` 的邊界需求被壓。論文 A.1.4 針對的是「deadline 脈絡的時間表達式」。
引句:「監控與追蹤(`Trace.*`、`Firebase*`、`analytics.*`)」
引句:「容量預配(`ArrayList(`、`HashMap(`、`StringBuilder(` 的容量參數)」

## b13 `--judge` 與 `--only` 的 `<定位>` 解析與對不上壞法的行為沒定義
severity: minor
blocking: 否——都是 rc 的選擇,spec 缺一句;但缺 rc 規定時各實作不同。
- 位置:〈用詞〉定位、〈範圍〉2 判。
- 輸入:`<檔>:<行>` 沒定義切法。檔名含 `:` 或全形冒號 `：` 時,從左切會切錯;行號是空、非整數、超出行數;`--judge` 給了一個乾節點行、沒有壞法的行、或不在改到範圍的行。
- 判不跑檢查,工作目錄可以不乾淨。工作目錄的行號與 B 版不同時,算出的壞法身分(`old_sha`、`new_sha`)是工作樹的,推送閘從 B 版重算會對不上,判完還是缺紀錄。spec 沒說判要讀哪個版本。
- 預期值表只有理由不足 10 實字一列(S10)。
引句:「不跑測試、不套跑之前那串檢查;存活或 no_result 都能判」
引句:「`<檔>:<行>`(一行只一個壞法,不用再分第幾個)」

## b14 `old` 的唯一性是子字串計數,縮排較深的相同行與檔尾無換行都會對不上
severity: minor
blocking: 否——落成 drifted 的 no_result,不會誤殺,只是多一次判。
- 位置:〈用詞〉壞法身分。
- 查證:`cmd_guard_kill` 用 `src.count(old)` 數,`old` 帶縮排與換行。`    x = a > b\n` 會同時命中 `        x = a > b\n`(更深縮排的另一行)的後半,count 為 2,判 drifted。檔尾沒換行的最後一行,`old` 以 `\n` 結尾,count 為 0。
- spec 只說「整支檔不是恰好一次」,沒說用子字串還是整行相等數。choice-points 端若用整行相等判唯一,和 guard kill 就對不上。
引句:「`old` 是那一行(含縮排與換行),整支檔不是恰好一次時依序往上」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:28072`

## 驗收 r1 折入
- b1(layout):到位。spec 已寫「用 B 版檔案清單算的版面」,另補 testFixtures 與 sharedTest。通則部分見本輪 b8。
- b2(整字比對):到位。API 成員只認 `.成員(`、`.成員 {`、`.成員<`,`padding(all = 8.dp)`、`pair.first` 不再命中。新的洞見 b9。
- b3(no_result 沒出口):到位。`--judge` 加 `not-applicable`,存活與 no_result 都能判。新的洞見 b4。
- b4(`?.` 邊界):到位。改為呼叫形,不再依賴 `?.`。
- b5、b6(需求脈絡組):到位。整段撤掉,只留排版。`_kt_sit_material` 找不到就按檔,不影響判定。
- b7(BOM):到位。spec 寫「先剝檔首 BOM」。我用 `\ufeff` 驗過原函式不處理 BOM,現在補上。
- b8(反引號、字串樣板):結果到位,機制沒寫。我實跑 `_strip_c_comments(..., kotlin=True, keep_length=True, blank_strings=True)`:反引號識別字原樣留、`${a < b}` 保留,所以「反引號裡不算」要另外掃反引號區段,S2 有一列守它,可接受。
- b9(算不出來):到位。`_KtSitUnverifiable`、`_KtSitOverBudget` 對應 reason「算不出來」。
- b10(組號)、b11(來源指錯):到位。
- CRLF:無問題。`_kt_sit_read_many` 換成 `\n`,`cmd_guard_kill` 用 universal newline 讀,兩邊一致。

## 逐節與其他
- 〈白話〉、〈舊否決比對〉、〈不做〉、〈依據來源〉、〈回退〉、〈審計修正紀錄〉:已讀,無 finding。
- 〈驗收條款〉:S1 到 S21 編號齊全,預期值表每列的「來源」對得到目標節。S2 預期值沒有 `->`、`?:` 的列,spec 的規則寫了這兩個,測試沒釘。
- 論文引用對照:附錄 A.1.23(`==` 只換 `!=`)、A.1.1、A.1.4、A.1.5、A.1.21、A.3.2、2.3(×7、批次)、3.2.1、4.1 Listing 2 的出處正確。有誤的見 b10。
- 論文「跟論文不同」清單的後果:天花板 3(沒覆蓋率)讓測試沒跑到的行必存活。Compose 畫面的 `@Preview` 函式沒有乾節點規則,這類行都要人處置,是最直接的噪音來源,見 b11 的補法。

## 實務隱患鏡頭
- 輸入消毒:壞法顯示的是原始碼行,含終端控制字元時原樣回顯。屬自用單人範疇,按威脅模型放行,不計 finding。
- 路徑與定位字串:見 b13。檔名含引號與換行已由 `_kt_sit_hunks` 擋(`_KtSitUnverifiable`)。
- 換行與編碼:BOM、CRLF 見驗收段,無隱患。
- 效能與記憶體:每個壞法一次 Gradle,choice-kill 沒有跑的壞法數上限,只有推送端有回報上限。整個新檔或重新產生的生成碼(無 `@Generated` 規則)會一次產生大量壞法,屬資源席範圍,此處不另計。
- 併發:單人依序操作,spec 已排除,無。
- 資安:選擇點內容來自作者自己的原始碼,無外部輸入面,無。

## 固定席節點(Systems/guard-kill)
- INVARIANT rc 優先序(survived→rc1、drifted/abort/error→rc2、弱證據不放行):不影響。spec 對 `cmd_guard_kill` 只多選用參數 `source`(不傳維持原行為),verdict 與 rc 判定沒改。choice-kill 只讀 `result_out` 的列,自己另算 rc。
- INVARIANT `--json` 純度:不影響。choice-kill 以非 json 模式呼叫,不碰 json 輸出路徑,`source` 只加在 kill-log 與臨時配方。

最嚴重:major;blocking 共 6 條
