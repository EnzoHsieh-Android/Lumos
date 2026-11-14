severity: major

## c1 「新那一行在整支檔裡恰好一次」與「往外帶行求唯一」互相矛盾,重複的行被悄悄免驗
severity: major
blocking: 是——照字面實作會讓重複出現的行沒有壞法,而且「不唯一」永遠到不了。
- 位置:〈用詞〉一行一個壞法、壞法身分,條款 S3。
- 問題:
  - 挑壞法時,候選要滿足「新那一行在整支檔裡恰好一次」,一個都沒有就「這一行沒有壞法」。
  - 壞法身分卻寫:不唯一時往外多帶 2 行,仍不唯一才標「不唯一」並要求處置。
  - 若「新那一行」指改動後的該行原文,重複的行在選擇階段就被剔光,「不唯一」和 S3 第二半句永遠觸發不了。
  - 若指套上壞法後的那一行,這個條件跟 `cmd_guard_kill` 要的「`old` 恰好一次」無關。它只會讓「檔裡別處剛好有一行等於壞法結果」時,那個候選被跳過。
  - 這樣一來,挑中哪個壞法會被檔案別處的無關編輯改變。
- 具體例:
  - 同一支檔有兩個相同的 `if (items.size > MAX) return`,一行在函式 A、一行在函式 B,都是改動行。
  - 預期:兩行各帶上下文成為唯一的 `old`,各自跑壞法。
  - 字面實作:兩行都沒有壞法,複製貼上的邏輯反而最不被驗。
- 查證:`cmd_guard_kill` 的唯一性判法是 `src.count(old) == 1`,drifted 才是它的出口,見 `/Users/enzo/harness/lumos-near-miss/scripts/lumos:28072`。
引句:「新那一行在整支檔裡恰好一次、而且不是已知編不過的形狀」
引句:「整支檔不是恰好一次時依序往上、往下各多帶一行,最多前後各 2 行」

## c2 「已知編不過的形狀」沒有定義來源,若取自帳就會讓 B 版重算對不上
severity: minor
blocking: 否——spec 沒說這個詞指什麼,實作者得自己選,選錯只影響重算的一致性。
- 位置:〈用詞〉一行一個壞法、編不過的形狀。
- 〈編不過的形狀〉只定義「累計 3 次以上列為表要改候選」,是 `--stats` 的統計,沒有任何機制把它餵回挑壞法。
- 若實作者拿帳上累計去跳過候選,推送閘在 B 版重算壞法時,帳版本、機器、讀帳時機不同,挑中的壞法就可能不同,雜湊對不上。
- 若實作者寫死一份清單,清單放哪裡、誰維護,spec 沒說。
引句:「同一個 (列號, 壞法) 在 `--stats` 累計,累計 3 次以上列為」

## c3 `true`/`false`/`a`/`b` 類壞法與 UOI 都需要運算元範圍與型別,spec 沒給判法
severity: major
blocking: 是——運算子表的核心候選無法按字面機械產生,各種實作產出的壞法不同。
- 位置:〈用詞〉選擇點表的 ROR、LCR、AOR、UOI。
- 問題:
  - `a > b` → `true`、`a && b` → `a` 或 `b`、`a + b` → `a` 都要先知道 `a`、`b` 的邊界,涉及優先順序、括號、呼叫鏈、lambda。
  - spec 只定義「運算子兩側是空白或換行」,沒有語法樹,也沒給運算元切法。
  - UOI 的「布林運算元 `b`」需要型別。沒有型別資訊就分不出 `count` 和 `enabled`,`!count` 必然編不過。
- 具體例:
  - `if (x + y > z)` 的 ROR→`true`。若左運算元取相鄰 token `y`,得 `if (x + true)`,編不過。
  - 正確取 `x + y`,得 `if (true)`。兩種取法都合 spec 字面。
  - 預期值表 S1 寫 `if (count > limit && enabled)` 只有 `>` 或 `&&` 的候選。但 UOI 表中 `enabled` 是布林運算元,`!enabled` 也是候選,表與條款對不上。
- 後果:大量候選走成「編不過 → no_result」,每個都要人 `--judge`。這是論文 3.2.1 要靠規則預先擋的類型,spec 把它推到事後人工。
引句:「UOI:布林運算元 `b` → `!b`;拿掉前置 `!`。」
引句:「LCR:`a && b` → `a || b`、`a`、`b`、`true`、`false`;`||` 同形。」
引句:「只挑一個壞法(`>` 或 `&&` 的其中一個候選)」

## c4 API 壞法常需要補 import,批次路徑不補,標題範例 S1 與驗收 S21 會判成 no_result
severity: major
blocking: 是——表上最有代表性的壞法在批次跑時多半編不過,S21 的預期 survived/killed 出不來。
- 位置:〈用詞〉選擇點表的 API 列、〈範圍〉2 `--import`、S1 第一列、S21。
- 問題:
  - `flatMapLatest`→`flatMapConcat`、`collectLatest`↔`collect`、`flatMapConcat`↔`flatMapMerge`,以及 Flow 版的 `filter`/`first`/`last` 互換,都是需要各自 import 的擴充函式。
  - 專案若不用萬用 import(ktlint 預設禁止),壞法檔頭沒有那個名字,就是 `Unresolved reference`,殺傷力給 `killed_unattributed`,工具歸為「壞法編不過」。
  - 前置計劃的 `--import` 說明文字用的例子正是 `import kotlinx.coroutines.flow.flatMapConcat`。
  - 本計劃的 `--import` 卻「只能配 `--only`」,批次路徑不帶 `also`。表上也沒有「要補的 import」欄。
  - 路徑是:批次跑 → no_result(編不過)→ 人要自己知道改用 `--only <定位> --import`。
  - spec 把 no_result 的出口寫成「人可判 `not-applicable`」,那是永久放行一個本來有效的壞法。
- 具體例:ViewModel 檔頭只 `import kotlinx.coroutines.flow.flatMapLatest`。
  - S1 第一列預期「一個壞法 flatMapConcat」,批次跑的結果是 no_result,不是 survived 或 killed。
  - S21 要求「判 survived」,在批次路徑同樣得不到。
- 查證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:79358` 的 `--import` 說明例子;`/Users/enzo/harness/lumos-near-miss/scripts/lumos:76295` 的 `_situation_rule_imports_problem` 要求 import 名稱出現在 `--new` 裡。
引句:「`--import`:壞法要補的 import(同前置計劃),只能配 `--only`。」
引句:「改動行 `.flatMapLatest { repo.search(it) }`」

## c5 壞法身分不含計劃,多份計劃碰到同一個壞法時「最新一筆」取決於呼叫順序
severity: major
blocking: 是——同一個壞法在計劃 P1 survived、在 P2 killed,先後順序決定它有沒有有效處置。
- 位置:〈用詞〉殺掉判定、壞法身分、有效處置。
- 問題:
  - 殺傷力是「同一平台、同一份計劃」一次呼叫,節點是那份計劃。
  - 〈守的測試〉是所有碰到的進行中計劃的測試聯集。
  - 帳上壞法身分只有檔、行、`old`、`member`、`new` 的雜湊,不含計劃。
  - 有效處置看「同身分最新一筆」。
- 具體例:
  - 分支碰到 P1(綁 t_a)與 P2(綁 t_b),壞法 m 只有 t_b 殺得掉。
  - 對 P2 呼叫記 killed(attempt 1),對 P1 呼叫記 survived(attempt 2)。最新一筆是 survived,m 被擋。
  - 順序反過來就放行。結果取決於計劃處理的順序。
- spec 沒寫每次呼叫要不要帶聯集測試,也沒寫同身分的 survived 與 killed 怎麼合併。
引句:「同一平台、同一份計劃的所有壞法,在一次 `cmd_guard_kill` 呼叫裡跑」
引句:「同身分最新一筆是 `killed` 而且那筆的 `killing_test` 還在現在守的測試裡」
引句:「`file`、`line_sha`、`old_sha`、`member`、`new_sha`」

## c6 混合結果判法漏掉 `abort`,又跟「任一支 killed 就 killed」衝突;缺列沒有定義(r1 c1 沒折完)
severity: major
blocking: 是——一支壞掉的守的測試會讓整批壞法全部沒有結果,或判成不該有的 survived。
- 位置:〈用詞〉殺掉判定、S7。
- 問題:
  - 判定順序是「任一支 killed 而且非 weak → killed」,再來是「任一支屬於(`killed_unattributed`、`timed_out_weak`、`weak`、`drifted`、`error`)→ no_result」,其餘全部 survived 才 survived。
  - `abort` 不在第二列清單。同一壞法的各測試列若是 {t_a: abort, t_b: survived},既非 killed、不在清單、也不是全部 survived,字面沒有結論。
  - 另一句「基準 abort → 用到它的壞法全部 no_result」,又跟「t_b 已強 killed → killed」衝突。
  - 〈守的測試〉是計劃全部 `[test:]`。懸空測試名(`--tests` 對不到,Gradle 報 no tests found)或單支壞掉的測試,會讓所有壞法都 no_result,不管其他 29 支能不能殺。
  - 缺列沒有定義:`cmd_guard_kill` 遇到 revert 失敗就 `break`,同組後面的配方沒有列。
  - 壞法的某幾支測試只有部分列,「其餘全部 survived」會誤判成 survived,或全缺卻沒有規則。
  - r1 c1 查證三已指出 `break` 讓列缺失,spec 只折了 `recipe_id` 唯一,缺列沒折。
- 具體例:守的測試 t_a、t_b,t_a 基準紅、t_b 強殺某壞法。S7 第二列說「用 t_a 的壞法全部 no_result」,殺掉判定第一句說「killed」。
- 查證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28103` 的 `break`;`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28049` 的 abort 列。
引句:「否則任一支是 `killed_unattributed`、`timed_out_weak`、`weak`、`drifted`、`error`」
引句:「某條測試指令的基準 abort → 這次呼叫裡用到它的壞法全部 no_result(原因 abort),不重跑」

## c7 中斷時「已有結果的壞法照記」做不到:`cmd_guard_kill` 只改 `source` 就拿不到部分結果
severity: major
blocking: 是——對話工具逾時一送 SIGTERM,整批數十分鐘的 Gradle 全部白跑,spec 卻寫成會保留。
- 位置:〈範圍〉2「共用」。
- 問題:
  - spec 說對 `cmd_guard_kill` 只多一個選用參數 `source`。
  - `cmd_guard_kill` 的 `results` 是區域變數,`result_out["rows"]` 與 kill-log 都在迴圈結束之後才寫。
  - 人裁那套訊號處理的第一個訊號,在 `st.defer` 為假時直接轉成 `KeyboardInterrupt`,不是「等這次殺傷力收尾」。例外從 `_kill_run` 一路穿出 `cmd_guard_kill`,沒有任何部分結果。
  - 所以「等收尾、已有結果照記」只有改 `cmd_guard_kill` 本體才做得到,spec 明說不傳參數維持原行為。
  - 重跑不續,因為沒有任何壞法有紀錄,每次重跑從頭來過。
- 查證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:76015` 的 `_situation_rule_signals` 與 `_on`;`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28149` 的 `result_out` 賦值位置;`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28156` 的 kill-log 寫入位置。
引句:「第一個訊號 → 等這次殺傷力收尾、已有結果的壞法照記、rc 2」
引句:「`cmd_guard_kill` 多一個選用參數 `source`(不傳維持原行為)」

## c8 表內壞法會讓測試掛住,`timed_out_weak → no_result` 之後沒有誠實的出口
severity: major
blocking: 是——常見寫法的壞法必然逾時,推送只能靠一筆不實的判定解開。
- 位置:〈用詞〉選擇點表 API 列、殺掉判定、〈範圍〉3。
- 問題:
  - `.first()` 對 StateFlow(永不結束)改成 `.last()`,測試會一直等下去。
  - `cmd_guard_kill` 把逾時記 `timed_out_weak`,殺掉判定歸 no_result。
  - no_result 的出口只有 `--judge --as equivalent|not-requirement|not-applicable`。壞法讓測試掛住,不是等價、不是非需求、也不是不適用。重跑一定同樣逾時。
  - 每個逾時最長佔 `max(基準耗時 × 5, 20)` 秒。Gradle 基準 60 秒就是 5 分鐘。
- 具體例:`state.first { it.isReady }` → `.last { … }`,每次都是 no_result,每次花約 5 分鐘。
- 查證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28091` 的 `m_timeout`;`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28111` 的 `timed_out_weak`。
引句:「`first`↔`last`、`firstOrNull`↔`lastOrNull`」
引句:「`not-applicable` 給」

## c9 乾節點只比對單行,多行呼叫的續行沒被涵蓋
severity: minor
blocking: 否——只會多出該被壓掉的壞法,出口(判 `not-requirement`、增補規則)存在。
- 位置:〈用詞〉乾節點規則「範圍(那一行、或整個函式本體)」。
- 問題:論文的乾節點是語法子樹(附錄 A 的 compound 規則),呼叫的引數整棵都是乾的。spec 的範圍只有「那一行」與「整個函式本體」,沒有「整個呼叫(跨行)」。
- 具體例:ktlint 標準格式會把長呼叫拆開,例如
  ```
  Timber.d(
      "n=${a + b}",
  )
  ```
  - 第二行沒有 `Timber.d(`,字串樣板裡的 `+` 照常產生壞法。
  - `require(\n    x > 0,\n) { ... }`、`delay(\n    retry * 1000L,\n)` 同理。
  - 樣板方法的整個本體(`toString` 的運算式本體跨行)也依賴函式邊界,而 `_kt_sit_material` 只找頂層或類別層宣告(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:40083`)。
引句:「範圍(那一行、或整個函式本體)」

## c10 自稱照論文處有幾處對不上論文原文
severity: minor
blocking: 否——是依據與實作說法不符,不會讓字面實作做錯事。
- 位置:〈PRIOR-ART〉、〈用詞〉選擇點表、依據來源表。
- (a) 3.2.4 被誤引:
  - 論文 3.2.4 的內容是「抑制冗餘壞法,讓報告的壞法一致」,例子是 `x != nullptr` 的 `nullptr`、`false` 互相等價。
  - 論文沒有「固定種子」。spec 的固定種子是自己的做法。依據表把它寫成論文 3.2.4,〈跟論文不同的地方〉也沒列。
  - 冗餘抑制本身沒做:LCR 的 `true`/`false` 與 `a`、`b` 之間仍可能等價。
- (b) 挑法不照論文:
  - 論文 Listing 2 是先隨機排序「運算子」,取第一個產得出的,運算子內再出一個壞法。
  - spec 〈一行一個壞法〉改成把「選擇點 × 候選」整個壓成一份清單再洗牌,候選多的運算子被抽中機率偏高。
  - 一行有 `x > y`(ROR 4 個候選)與 `.filter {`(API 1 個候選)時,API 只有約 1/5,論文是 1/2。
  - 這與 PRIOR-ART 自己寫的「隨機排序運算子」不一致。
- (c) 運算子表與論文表 1 不同:
  - 論文 ROR 的 `a > b` 候選含 `a <= b`,spec 沒有。
  - 論文 AOR 的 `a + b` 候選含 `*`、`/`、`%`,spec 只有 `-`、`a`、`b`。
  - 依據來源表卻寫「五個運算子與各自的壞法 | 論文表 1」。
- (d) 〈單元測試分不出的寫法不收〉引 A.1.6:論文 A.1.6 是 Beam、TensorFlow 這類管線框架,不是「測試裡被假實作換掉」。後者較接近 A.3.2(DI)。
- 查證:論文第 5 頁 3.2.4、第 7 頁 Listing 2、第 4 頁表 1、第 15 頁 A.1.6。
引句:「同一壞法每次穩定回報(固定種子) | 論文 3.2.4 節」
引句:「隨機排序運算子、第一個產得出的就用」
引句:「AOR:`a + b` → `a - b`、`a`、`b`;`-`、`*`、`/`、`%` 同形。」

## c11 乾節點第一版漏了論文附錄 A 裡最常見的 Kotlin 噪音類型
severity: minor
blocking: 否——只增加人工判定量,RETIRE-IF 會量到。
- 位置:〈用詞〉乾節點規則第一版。
- 問題:
  - spec 說第一版照附錄 A 譯成 Kotlin,實際只譯了 log、斷言、時間、監控、容量、樣板、flush/close、DI、Preconditions。
  - 論文語言無關的 A.1.10(對 null 比較)、A.1.20(集合大小與 0 比較)、A.1.9、A.1.11、A.1.8、A.1.24(取界)都沒譯。
  - Kotlin 的 `x != null`、`list.size > 0` 每個改動檔都有。
- 具體例:
  - `if (items.size > 0)` 的 ROR 候選含 `>=`,等於 `size >= 0` 恆為真,論文 A.1.20 明列為等價壞法。
  - 抽中就是一筆只能判 `equivalent` 的存活。
  - `x != null`→`x == null`,在 smart cast 之後用 `x.foo` 的區塊裡幾乎必然編不過,又是 no_result。
引句:「第一版照論文附錄 A 譯成 Kotlin:log」

## c12 回報上限不是處置總量的上限,處置完一輪就換種子
severity: minor
blocking: 否——spec 在天花板 7 已承認重抽,但〈白話〉的「最多 × 7」與事實不符。
- 位置:〈白話〉、〈用詞〉回報上限、天花板 7。
- 問題:
  - 存活 20、上限 14,B1 時抽中 14 個擋下。處置完要提交帳,B 變成 B2,只剩 6 個存活,6 ≤ 14,全部被擋。
  - 每提交一次帳,B 就變,所以人最終要處置全部 20 個。
  - 〈白話〉「要人處置的存活最多『改到的檔數 × 7』個」不成立。論文的上限成立,是因為它是提示、不擋合併。
引句:「下一次推送(B 變了)會重抽」

## c13 計劃的進行中狀態與碰到的計劃仍讀工作目錄,只有條款改讀 B(r1 c10 沒折完)
severity: minor
blocking: 否——只在工作目錄不是被推版本時才分歧。
- 位置:〈範圍〉4「讀哪一版」、〈用詞〉進行中計劃、碰到的計劃。
- 問題:spec 只把條款與 `[test:]` 改讀 B。
  - 進行中計劃的 `status` 沿用 `_live`,讀 `env.notes`。
  - 碰到的計劃是 `_spec_gate_push_candidates`,同樣讀 `env.notes`。
  - 計劃日期的 `created` 也在 `env.notes`。
  - S16 要求「計劃以 B 為準」,這些沒涵蓋。
- 具體例:B 的計劃是 `doing`、工作目錄那份已改成 `done` 且沒碰,工作目錄版本判無進行中計劃,擋「無規格」。B 版其實帳齊全。
- 查證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:17254` 的 `_live`;`/Users/enzo/harness/lumos-near-miss/scripts/lumos:16547` 的 `env.notes.items()`。
引句:「碰到的計劃的條款與 `[test:]` 用 `git show B:<計劃路徑>` 讀後照規格閘的條款解析取」

## c14 `--judge` 不套跑之前的檢查,但沒規定壞法身分從哪一版檔算
severity: minor
blocking: 否——定位與身分可能對不上 B,結果是推送時說缺紀錄。
- 位置:〈範圍〉2 `--judge`。
- 問題:
  - `--judge` 不套用「工作目錄乾淨」,也沒有 `--diff`、`--branch`。
  - 要得到 `old_sha`、`new_sha`、`member`,必須讀檔算壞法。
  - 若讀工作目錄(有未提交編輯),行號與 `old` 就會是未提交版本的,寫進帳的身分跟 B 的重算不同。
  - 預設範圍規則也可能跟推送閘的「主線與 B 的分岔點..B」不同。
引句:「不跑測試、不套跑之前那串檢查;存活或 no_result 都能判」

## c15 全 `[manual:]` 計劃會讓整道閘不擋
severity: minor
blocking: 否——spec 明說沿用規格閘既有裁定,但與「沒規格就判不了」的使用者原意拉扯。
- 位置:〈範圍〉4 判定、S14 第二列。
- 問題:碰到的進行中計劃只要沒有可守的測試,推送只提醒、不擋。碰到的計劃來源包含「`lands_in` 或連結指到被改程式檔的家」,新增一份 `doing`、條款全是 `[manual:]` 的計劃,成本很低。
- 後果:所有選擇點都免驗。spec 在 `[S8]` 對 choice-kill 卻要求 rc 2,兩端不對稱。
引句:「碰到了但沒有可守的測試 → 不擋,印」

## c16 SBR 邊界沒排除無大括號的控制句本體與 lambda 最後一句
severity: minor
blocking: 否——產出的壞法語意不是「刪一句」,多半編不過或改到別句。
- 位置:〈用詞〉選擇點表 SBR。
- 問題:SBR 排除了宣告、return、「函式最後一句的運算式」,沒排除:
  - 無大括號控制句的本體(`if (c)` 下一行 `foo()`)。刪掉後下一行變成本體,語意改變。
  - lambda 的最後一句,那是回傳值。
引句:「SBR:刪掉一整行的單句呼叫陳述」

## 第一輪折入驗收
- G1(批次):
  - 一次呼叫、基準每條指令一次、`invariant` 寫成「定位|測試名」讓 `recipe_id` 唯一,已落地。
  - 缺列與多計劃沒折完,見 c5、c6。
  - 沒折的還有「每個壞法 × 每支測試各跑一次、沒有提早停」。1 次呼叫的壞法數 × 測試數乘開,spec 靠量一次耗時兜底。
- G2:`not-applicable`、`{method}` 檢查已落地。批次沒有補 import,見 c4。
- G3:呼叫形、兩側空白含換行、BOM、反引號識別字不算,已落地。
  - 反引號識別字內的命中不算,實作上要自己遮罩。`_kt_strip_spans` 對反引號是「原樣保留、不當 span」,見 `/Users/enzo/harness/lumos-near-miss/scripts/lumos:6939`。
- G5:接線(`--push-remote`、`--pushed-ref`、主線取法)已落地。計劃狀態與候選仍讀工作目錄,見 c13。
- G6:既有條款記給新壞法已落地。
- G7:`_GOV_FIELD_TYPES`、`LOOP_NOT_CLOSE_EVENTS`、`_KNOWN_GATES` 的登記方式查過,可行。
  - `t_loop_close_kinds_classified` 只管 `design-loop`、`code-loop`,新 gate 不受那條反向守衛影響。
  - 帳量只談治理帳。批次每個「壞法 × 測試」會寫一列 kill-log,含 200 字尾端與最多 800 字失敗摘錄,spec 沒估算。

## 對照論文
- 已核對無誤:
  - 每行一個壞法(Listing 2)。
  - 回報上限 7 × 檔數(2.3)。
  - 乾節點人工增補、15% → 89%(3.1、3.2.5)。
  - A.1.1、A.1.4、A.1.5、A.1.12、A.1.15、A.1.21、A.1.23、A.3.2 的引用。
- 錯或漏見 c10、c11。
- 論文逐項:
  - 論文 2.3 的「壞法測試平行跑、各有暫時版本狀態」,spec 是單一工作樹依序跑,耗時差距沒列入〈跟論文不同的地方〉。
  - 論文 3.2.1 對無法編譯的壞法靠規則預先擋,spec 改成事後記 no_result。
  - 這兩點與 c3、c4 一起,把編譯失敗的處理量推給人。

## 實務隱患鏡頭
- 效能:壞法數 × 守的測試數次 Gradle,沒有提早停。耗時 spec 延後到實作時量。c8 的逾時壞法每個佔 5 分鐘。
- 資料遺失:c7,中斷整批白跑。
- 編碼與換行:`_kt_sit_read_many` 只換 `\r\n`,`cmd_guard_kill` 用通用換行與嚴格 UTF-8。單獨的 `\r` 或壞位元組檔是 drifted。屬極少數。
- 正確性:c1 到 c6。
- 併發與資安:無新增面向。沿用單人依序操作,`file`、`old`、`new` 走既有 `recipes_override` 的路徑圍欄,spec 已排除併發。
- 帳量:kill-log 增長見第一輪折入驗收的 G7。

## 固定席節點判讀
- `guard-kill` INVARIANT 1(rc 優先序 survived→1、drifted/abort/error→2、弱證據不放行):不影響。
  - spec 只加選用的 `source`,不碰 rc 判定。choice-kill 自己「取最大」是另一層,2 優先於 1,與該合約無關。
- `guard-kill` INVARIANT 2(`--json` 成功跑完時 stdout 恰一行合法 JSON):不影響。choice-kill 不傳 `as_json`。
- `規格閘` 節點:沒有合約。spec 抽出 `_live` 為頂層函式、語意不變,不影響。`[manual:]` 小改動裁定沿用,見 c15。

## 其餘已讀、無 finding
- 〈白話〉、〈舊否決比對〉、〈不做〉、〈回退〉、〈天花板〉、〈依據來源〉、〈審計修正紀錄〉:已讀,無 finding。
- 預期值表 S5、S9、S19、S20:數字與口徑互相一致,無 finding。

最嚴重:major;blocking 共 7 條
