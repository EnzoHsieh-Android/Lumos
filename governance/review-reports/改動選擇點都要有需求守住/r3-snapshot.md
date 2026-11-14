---
type: project
status: todo
created: 2026-11-13
updated: 2026-11-14
tags:
  - type/project
  - status/todo
  - scope/guards-gates
lands_in:
  - Systems/規格閘
  - Systems/guard-kill
  - Systems/kotlin規則包
related:
  - "[[Projects/雙向追溯_需求與語法選擇點互證_計劃]]"
  - "[[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]]"
---
# 改動選擇點都要有需求守住_計劃

## 白話

改動裡「換一種寫法照樣編得過、行為卻不同」的地方(選擇點),是寫的人做了一個決定,背後應該有一條需求。這份計劃照 Google 的差異式變異測試(論文〈Practical Mutation Testing at Scale〉,以下稱「論文」)做:用 ast-grep(tree-sitter 的 Kotlin 語法樹)找出改動行上的語法節點,每一行挑一個壞法(把節點換成另一種寫法),批次跑計劃條款綁的測試:
- 測試紅了(殺掉) → 記下是哪條條款守住這一行的選擇;
- 測試沒紅(存活) → 這個選擇沒有需求守著:規格沒寫、測試太弱、或換了其實一樣 → 推送前擋下交人裁;人裁寫回規格並綁一支會紅的測試,或判「換了一樣/不是需求/壞法不適用」留帳。

不是每一行:log、斷言、時間、樣板方法這類「乾節點」(論文的 arid node)不產生壞法;一行只產生一個壞法(論文 4.1);要人處置的存活有上限「改到的檔數 × 7」(論文 2.3)。哪些節點產生什麼壞法、哪些節點是乾的,由 Kotlin 型錄的〈選擇點表〉與〈乾節點規則〉列出,每列對應一條 ast-grep 規則;乾節點規則由人照回饋手動增補(論文 3.1)。

這份把 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 的正向(條款的測試分不分得出對錯)與反向(程式的選擇有沒有需求撐腰)併成同一個機制:殺掉的那一行是正向的證據,存活的那一行就是反向要找的「沒有出處的選擇」。

大方向(使用者 2026-11-13):「改動中的語法,必定是代表一種需求,而這個需求,必須引得出規格……語法是可以被窮舉的,也就代表 code review 是可以被機械層檢查」;「我想涵蓋的就是所有開發需求中的程式碼,不是特定哪一種類別的語法」;範圍是選擇點、不是每一行;「那就照那份論文來實作」「有什麼問題,優先參考」;設計審兩輪都被「沒有語法樹」打穿後,使用者 2026-11-14 裁「改用 ast-grep 語法樹」。

PRIOR-ART: 主依據是 Google 差異式變異測試(論文 https://arxiv.org/pdf/2102.11378):在語法樹上做(2.2「mutagenesis service … navigating the AST」)、只對改動且有覆蓋的行產生變異、每行一個(4.1 Listing 2:運算子類別隨機排序、第一個產得出的類別產一個壞法)、五個運算子 AOR/LCR/ROR/UOI/SBR(表 1)、乾節點由語法樹節點規則壓掉(3.1 公式 1:簡單節點看專家規則、複合節點所有子節點都乾才乾;附錄 A)、編不過的壞法用規則事前擋(3.2.1)、回饋由人寫成新規則(有用比例 15% → 89%)、每次改動最多回報「檔數 × 7」個存活(2.3)、覆蓋率決定每個壞法要跑的最小測試集(2.1)。語法樹工具:ast-grep 以 tree-sitter 的 Kotlin 文法剖析(https://github.com/ast-grep/tree-sitter-kotlin、節點名照 https://github.com/fwcd/tree-sitter-kotlin 的 grammar.js:comparison_expression、equality_expression、conjunction_expression、disjunction_expression、additive_expression、multiplicative_expression、prefix_expression、call_expression、navigation_expression、statements、lambda_literal),Trail of Bits 的 mewt/MuTON 也用 tree-sitter 做跨語言變異(https://blog.trailofbits.com/2026/04/01/mutation-testing-for-the-agentic-era/)。補充:少數運算子就夠(Offutt 等 1996,https://dblp1.uni-trier.de/rec/journals/tosem/OffuttLRUZ96.html;Just 等,https://homes.cs.washington.edu/~rjust/publ/non_redundant_mutants_icst_2012.pdf);API 兄弟寫法寫成改寫表(MutApi,https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843;Mutant-Kraken,https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin);存活可能是規格缺口(MutDafny,https://arxiv.org/pdf/2511.15403);追不到需求的程式補需求或刪程式(DO-178C,https://ldra.com/ldra-blog/do-178c-structural-coverage-analysis/)。跟論文不同的地方(後果寫在天花板):①論文有覆蓋率挑最小測試集,我們沒有,每個壞法跑全部守的測試(按相關度排序、殺掉就停);②論文的存活是不強制的提示,我們照使用者裁定擋推送;③多了 Kotlin API 兄弟寫法互換(第六類);④UOI 只做布林情境的 `b`→`!b` 與拿掉 `!`,不做 `a++`/`a--`(Kotlin 的 val 與運算式多半不適用);⑤一行挑哪個壞法用「檔+那一行內容」的雜湊當種子(論文沒規定種子,我們要同一行每次挑一樣,帳才對得上);⑥論文 4.2–4.5 依歷史表現排序運算子不做(沒有歷史)。不採:PIT——協程上大量無用變異(https://lightrun.com/answers/hcoles-pitest-pitest-generates-unhelpful-mutations-when-using-kotlins-coroutines),過濾外掛 Arcmutate 商用授權(https://central.sonatype.com/artifact/com.arcmutate/pitest-kotlin-plugin);用剝註解字串的文字比對近似語法樹(本計劃設計審 r1、r2 連兩輪被運算元範圍、陳述位置、乾節點跨行打穿);AI 自動判等價(Meta ACH,https://arxiv.org/html/2501.12862)。
RETIRE-IF: 上線兩個月、被回報的存活累計至少 30 個之後,看 `gov --stats` 的選擇點數字:①被回報的存活裡被人判「等價或不是需求」的超過八成(論文起步時 85% 沒用,補了乾節點規則仍降不下來就是表或判法錯;「壞法不適用」另計,算表的問題),或②每次 choice-kill 呼叫耗時中位數超過十分鐘,或③推送被擋的筆數裡超過一半是「過期」——就把推送那一道降成只提醒,回頭縮表或改判法。
REVISIT:2027-01-15 讀 gov --stats 的選擇點數字(殺掉率、存活處置分布、乾節點候選、每次呼叫的改動行數、有壞法的行數、耗時),決定要不要照論文 4.2 依歷史表現排序運算子、要不要加數字常數類選擇點、要不要接 Kotlin 覆蓋率(JaCoCo)挑最小測試集

## 舊否決比對

- [[Projects/guard殺傷力驗證_計劃]] 決策 d1「合約殺傷力驗證不自動產生變異」(理由:人宣告的壞法保證語意有變、零依賴跨語言工具不內建語言知識):這份是自動產生壞法,等於在「改動選擇點」這個範圍翻了 d1。實作時用 `lumos decision-add` 在那份計劃補一筆決策:d1 限定在「合約殺傷力配方」,改動選擇點改由本計劃依論文以語法樹自動產生;翻案理由是論文的規模實證與乾節點規則把等價與誤報壓到可處置的量。語言知識放在型錄的 ast-grep 規則(工具鏈 configs/,不進 scripts/lumos 本體),lumos 本體仍零依賴;ast-grep 是 Kotlin 規則包既有的外部工具。
- [[Projects/高風險測試證據加嚴_計劃]] 第二批「CI 對改到的行跑變異測試」:那份打算接外部變異工具,排在 2026-12-15 回頭看;這份不碰外部變異工具。回頭看時改讀這份的帳。
- [[Systems/guard-kill]] 否決「另抽一支共用的殺傷力函式」:這份沿用 `cmd_guard_kill` 的 `recipes_override`,不另抽;只加選用參數(見範圍 2)。
- [[Systems/規格閘]] 的裁定「條款全是 `[manual:]` 的小改動不必綁測試、推送印 light」:這份不翻;碰到的計劃沒有可守的測試時,推送前那一道只提醒、不擋。
- [[Systems/規格閘]] 推送閘「算不出來就放行」(工具壞不能擋所有人):這份照它,掃描算不出來只提醒不擋;只有治理帳讀不到才擋(同預期值表那道)。
- 本計劃前一版(「條款近似錯誤寫法要殺得掉」,條款自己宣告 `[near:]`):整個換掉;卷證在 governance/review-reports/條款近似錯誤寫法要殺得掉/。
- 改寫後第一輪設計審提的「需求脈絡組一組一題、判不是需求自動推廣到同樣式」:跟論文不同、連席打穿,撤掉;只留按外層宣告排版顯示。第二輪前的「剝註解字串文字比對」:兩輪打穿,換成語法樹(使用者 2026-11-14 裁)。

## 用詞

- **前置**:[[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]](2026-11-13 已合進主線)。
- **論文**:Petrović、Ivanković、Fraser、Just,〈Practical Mutation Testing at Scale: A view from Google〉,https://arxiv.org/pdf/2102.11378 。本計劃有疑義時先回這份找答案(使用者 2026-11-13 裁)。
- **語法樹掃描**:工具鏈 `configs/ast-grep/kotlin-choice/`(新增)放兩組 ast-grep 規則(選擇點規則、乾節點規則,由型錄兩節產生或對照),lumos 以參數清單(不開 shell)執行 `ast-grep scan --config <那份設定> --json=stream <檔>`,讀每個命中的規則編號、節點範圍(起訖行列)、節點原文與後設變數(運算元)。ast-grep 不在 PATH → choice-points 回 3「沒檢查到」(同新增告警那道的 rc 3 語意)、choice-kill 回 2、推送前那一道擋下 reason「沒有 ast-grep」並印安裝指令(專案沒有 Kotlin 正式碼改動時不需要)。ast-grep 的版本記進每筆 `run` 事件。
- **選擇點表**:Kotlin 型錄(`skills/kotlin-idioms/checks-catalog.md`)新增一節〈選擇點表〉,每列:列號(`C-<n>`)、類別(`AOR`、`LCR`、`ROR`、`UOI`、`SBR`、`API`)、ast-grep 規則(節點種類或樣式與限制)、候選壞法(依序,用後設變數組)、型別前提(哪些情況不產生,論文 3.2.1)、需補的 import(API 類)、對應的情境決策表列號、為什麼行為不同、出處(論文節號)。第一版:
  - ROR(論文表 1):`comparison_expression` 的 `$A > $B` → `$A < $B`、`$A <= $B`、`$A >= $B`、`true`、`false`;`<`、`>=`、`<=` 同形。`equality_expression` 的 `==` 只換 `!=`(附錄 A.1.23);`!=` 只換 `==`(本計劃比照)。型別前提:節點在 `if`/`while`/`when` 條件或 `&&`、`||` 運算元(布林情境)才給 `true`、`false`。
  - LCR:`conjunction_expression` `$A && $B` → `$A || $B`、`$A`、`$B`、`true`、`false`;`disjunction_expression` 同形。
  - AOR:`additive_expression`/`multiplicative_expression` `$A + $B` → `$A - $B`、`$A * $B`、`$A / $B`、`$A % $B`、`$A`、`$B`;其餘同形。型別前提:任一運算元是字串字面值或字串樣板 → 不產生(字串串接)。
  - UOI:布林情境的運算元 `$B`(簡單識別字或呼叫)→ `!$B`;`prefix_expression` 的 `!$B` → `$B`(本計劃加,見差異④)。
  - SBR:`statements` 的直接子節點、而且是 `call_expression` 的陳述 → 刪掉(論文附錄 A.1.12 的不可刪:不在 `value_arguments` 裡、不是 `lambda_literal` 的最後一個陳述、不是 `function_body` 只有一個陳述的非 Unit 函式、不是無大括號控制句的本體)。
  - API(本計劃,MutApi 形狀;只認 `navigation_expression` 後接 `call_suffix` 的呼叫):`filter`↔`filterNot`、`any`→`none`、`all`→`any`、`none`→`any`、`sortedBy`↔`sortedByDescending`、`minByOrNull`↔`maxByOrNull`、`flatMapLatest`→`flatMapConcat`、`flatMapConcat`→`flatMapMerge`、`flatMapMerge`→`flatMapConcat`、`.distinctUntilChanged()` 拿掉。需補的 import:檔頭有逐一 import 原寫法(例 `import kotlinx.coroutines.flow.flatMapLatest`)時,自動補兄弟寫法那一行(套前置計劃的 `also`)。
  - 不收(單元測試分不出或常掛住):`first`/`last`、`take`/`takeLast`、`drop`/`dropLast`(Flow 沒有 `takeLast`,`first`→`last` 在 StateFlow 上會掛住)、`collectLatest`/`collect`、`coroutineScope`/`supervisorScope`、`Dispatchers.*`、`SharingStarted.*`、`flowOn`、`buffer`、`conflate`(論文附錄 A.1.4 時間類、A.3.2 被假實作換掉)。
- **乾節點規則**:同一份型錄新增〈乾節點規則〉,每列:列號(`A-<n>`)、ast-grep 規則(節點種類加名稱限制)、乾的範圍(那個節點整個,含跨行引數與尾隨 lambda——論文公式 1 以節點為單位)、論文對應節、為什麼沒用、加入日期與依據(人裁的哪一筆判定)。第一版:log 呼叫(接收者是 `Log`、`Timber`、`logger`、`log` 的呼叫,或裸呼叫 `println`;A.1.1)、斷言與前置條件(裸呼叫 `require`、`check`、`assert`、`requireNotNull`、`checkNotNull`、`error`,沒有接收者;A.1.5)、時間(`delay`、`withTimeout`、`withTimeoutOrNull` 呼叫的引數節點;A.1.4)、監控與追蹤(接收者是 `Trace`、`FirebaseAnalytics`、`FirebaseCrashlytics`、`analytics` 的呼叫;A.1.3)、容量預配(`ArrayList`、`HashMap`、`StringBuilder` 建構呼叫只有一個整數引數時的那個引數;A.1.2)、樣板方法(`override fun equals`/`hashCode`/`toString` 的整個函式本體;A.1.21)、旗標(含 `BuildConfig.DEBUG` 的條件節點;A.1.13、A.1.16)、集合大小與 0 比較(`$X.size`、`$X.length` 跟 `0` 的 comparison_expression;A.1.20)、提早 return(`if ($X.isEmpty()) return …` 整個 if;A.1.22)、取界(`coerceIn`、`coerceAtLeast`、`coerceAtMost`、`minOf`、`maxOf` 的引數;A.1.24)、浮點與字面值比較(運算元是浮點字面值的 comparison_expression;A.1.11)、資料流 flush/close(`.flush()`、`.close()` 陳述;A.1.15)、依賴注入(`@Module` 類別本體、`@Provides`/`@Binds` 函式本體,註記可在上一行;A.3.2)。乾節點範圍內的節點不產生壞法;複合節點照公式 1:只有所有子節點都乾才整個乾。
- **讀表**:兩節由 `configs/ast-grep/kotlin-android/check.py` 的表讀法讀(把 `dt_table` 一般化成依節名讀;情境決策表行為不變),`catalog_problems` 一併檢查兩節(欄位、列號重複、候選空白、ast-grep 規則檔存在而且列號對得上);型錄照 `_kt_catalog_path()` 取(工具鏈來源那份;測試用 `LUMOS_KT_CATALOG`)。型錄或規則包自檢檔不在(`_kt_catalog_missing`)→ 只提醒不擋;檔在但缺這兩節或表壞 → 擋,指出哪一列。為什麼不併進情境決策表:決策表每列是「要看情境判」的題目;選擇點表每列是論文表 1 那種一對一機械壞法,用途不同;重疊的成員用「對應的情境決策表列號」欄互指,壞法只有選擇點表一個來源。
- **改到的行**:範圍內的增行,沿用情境題的兩道過濾:路徑照 `_kt_sit_path_ok` 再加只收 `.kt`、不是測試檔(`_nodehome_is_test` 帶 `_nodehome_layout`,版面用被讀版本的檔案清單算;另把 source set 名稱以 `Test` 結尾或以 `test` 開頭的(`commonTest`、`jvmTest`、`androidUnitTest`、`androidInstrumentedTest`、`testFixtures`)、`sharedTest`、路徑段是 `testing` 或 `test-utils` 的模組都當測試);增行跟同一 hunk 的刪行去空白後相同的不算(同 `_kt_sit_hits`)。
- **選擇點**:語法樹掃描在改到的行上命中的選擇點規則節點(節點起始行是改到的行),扣掉落在乾節點範圍內的。字串、註解、反引號識別字裡的內容不是運算式節點,自然不算;字串樣板 `${…}` 裡是運算式節點,照算。
- **一行一個壞法**(論文 4.1 Listing 2):對每一行改到的行,把那一行有選擇點的類別(AOR/LCR/ROR/UOI/SBR/API)用「檔的 repo 根相對路徑 + 那一行剝前後空白的原文」的雜湊當種子打亂,依序取第一個類別;在那個類別的節點中取最左邊的一個,候選壞法依同一種子打亂,取第一個「套上後整個 `old` 在檔裡恰好一次、型別前提沒排除」的;一個類別都產不出就這一行沒有壞法。
- **壞法身分**:`file`、`line_sha`(那一行原文的 sha256 前 16 碼)、`row`(列號)、`new_sha`。`old` 是那個節點所在的完整行(節點跨行就含到節點最後一行),整支檔不是恰好一次時依序往上、往下各多帶一行,最多前後各 2 行;還不唯一就這一行標「不唯一」、不跑(可以判)。`new` 是 `old` 套上壞法。換行統一成 `\n`;唯一性照 guard kill 的 `src.count(old) == 1`。
- **定位**:`<檔>:<行>`;解析從右邊切最後一個 `:`,行號要是正整數。
- **有效處置**:以行為單位——帳上同一個 (`file`, `line_sha`) 最新一筆是 `killed` 而且 `killing_test` 還在現在守的測試裡,或是 `judged`。型錄改了、那一行挑到的壞法換了,只要那一行內容沒變,舊的有效處置照算(型錄改動不讓舊帳失效)。
- **過期**:同一行最新一筆是 `killed`,但 `killing_test` 已不在現在守的測試裡。
- **進行中計劃**:status 是 doing,或這次推送改到計劃檔本身而 status 是 done(`_spec_gate_push_scan` 裡 `_live` 的語意;抽成頂層函式共用,語意不變)。
- **碰到的計劃**:在被讀版本的樹上建記憶體圖譜(`_drift_tree_env`,同情境題那道 `_kt_sit_spec_names_calc` 的做法),交 `_spec_gate_push_candidates` 取候選,再取其中的進行中計劃;狀態、`lands_in`、`created` 都從同一版讀。
- **守的測試**:碰到的計劃(聯集)〈驗收條款〉裡 `[test:]` 綁的測試,扣掉 `[manual:]` 與 `[keeps]` 的條款;平台照 `resolve_test_refs`/`_split_test_ref_ex` 取,只留平台 profile 是 kotlin-junit 的;平台 `run_cmd` 要含 `{method}`。排序:先放「計劃的 `lands_in` 或連結指到這支被改檔的家」的計劃所綁的測試,再依計劃名、條款順序。
- **殺掉判定**:同一平台的所有壞法在一次 `cmd_guard_kill` 呼叫裡跑(`node` 填守的測試所屬計劃中名稱排序第一份;一棵隔離工作樹;同一條測試指令的基準只跑一次)。每個壞法對每支守的測試各一個臨時配方,`invariant` 寫 `<定位>|<測試名>`、`platform` 帶那支測試的平台、`group` 寫 `<定位>`;`cmd_guard_kill` 新增選用參數 `stop_group_on_kill=True` 時,同一 `group` 已有一支強 killed 就略過其餘配方(記「略過」)、`on_row` 回呼在每條配方跑完時交出那一列。判定(每個壞法):任一支 `killed` 而且非弱證據 → **killed**,`killing_test` 取排序第一支這樣的測試、`clauses` 是綁它的條款;否則若任一支是 `killed_unattributed`、`timed_out_weak`、`weak`、`drifted`、`error`,或有守的測試沒有列(缺結果) → **no_result**(記第一個原因與失敗摘錄;失敗摘錄是編譯錯誤記「壞法編不過」、逾時記「測試掛住」);其餘每支都有列而且都 `survived` → **survived**。某支測試的基準 abort → 那支測試從這次呼叫的集合拿掉(記「基準不綠沒跑」),其餘照判;所有測試都 abort → 全部 no_result(原因 abort)。
- **回報上限**(論文 2.3):一次推送要處置的存活最多「範圍內改到的檔數(所有種類) × 7」個。抽法:取這個範圍裡「曾經存活過的行」(帳上同一行有任一筆 survived)全部身分排序後的雜湊當種子,抽上限那麼多個;抽中的要有效處置,沒抽中的這個範圍內不要求(處置抽中的行不會讓沒抽中的被重抽,因為種子只看「曾經存活」的集合,提交帳本不改變它)。範圍裡又冒出新的存活行時集合變了,重抽一次;已處置的仍算處置。no_result、不唯一、過期、缺紀錄不受上限(它們不是存活,是沒有結論)。
- **排版**:回報按外層宣告排(`_kt_sit_material` 找得到就用那個宣告的第一行,找不到就按檔),只是顯示。推送訊息每種原因最多列 20 行示例,其餘只給數字與 `lumos choice-points` 指令。
- **人裁同意**:照 `_waive_origin_tty`:終端答 y 記 `origin: human`;沒有終端要 `--consent` 使用者原話,記 `origin: ai`、`consent` 必填非空白。
- **生效日**:常數 `_CHOICE_SINCE`(合進主線的隔天),環境變數 `LUMOS_CHOICE_SINCE` 供測試覆寫(被覆寫成比今天晚時推送輸出印一行「選擇點那一道被環境變數關掉」);測試總檔預設 9999-12-31。碰到的進行中計劃任一份的計劃日期(`_plan_effective_day(..., scope="note")`,`head` 用被讀版本)不早於生效日就適用;沒碰到計劃時看推送當天。不沿用情境題的 `_kt_sit_spec_since`:那是另一道閘的上線日。

## 範圍

1. **`lumos choice-points [--diff <範圍>] [--branch <名>]`**:唯讀,列出改到的行與每行挑中的壞法(定位、列號、類別、壞法、外層宣告)與帳上狀態(沒跑、殺掉 by `<測試>`(`<條款>`)、存活、已判、不唯一、跑不出結果、過期、沒有壞法、乾節點)。範圍沒給時跟推送前那一道同一套:主線照 `_push_mainlines`(遠端取分支的上游遠端,沒有就唯一的遠端),用主線與 HEAD 的分岔點..HEAD;目前分支就是主線而沒給 `--diff` → rc 2。最後一行統計(改到的行數、有選擇點的行數、有壞法的行數)。ast-grep 不在 → rc 3;型錄缺檔 → 提醒、rc 0;表壞 → rc 2。
2. **`lumos choice-kill [--diff <範圍>] [--branch <名>] [--only <定位>] [--max-mutants N]`**(跑):對還沒有有效處置的行,依〈用詞〉殺掉判定批次跑、逐筆寫帳。
   - 跑之前:工作目錄除簿記檔外乾淨;ast-grep 在;守的測試至少一支——範圍沒碰到進行中計劃 → rc 2「沒規格就判不了」;碰到了但沒有可守的測試 → rc 2「計劃沒有可守的測試條款」;平台 `run_cmd` 沒有 `{method}` → rc 2;Android 檢查同人裁那一道。開跑前印「N 個壞法 × 最多 T 支測試」與基準逾時上限。
   - `--max-mutants`(預設 30):一次最多跑幾個壞法,多的印「還有 M 個沒跑,再跑一次」。
   - `cmd_guard_kill` 新增的選用參數(都不傳時行為不變):`source`(寫進殺傷力帳本與配方 note)、`stop_group_on_kill`、`on_row`;另把活著的隔離工作樹登記進模組層清單,強制結束時印出路徑。`source` 是 `choice-kill` 時不寫殺傷力帳本(治理帳已有判定)。
   - 中斷:沿用人裁的兩段式訊號處理包住整次呼叫——第一個訊號:讓正在跑的那條配方收尾,已經由 `on_row` 交出結果而且判定完整的壞法照記,其餘不記,記一筆 `run`(`interrupted: true`),rc 2;第二個:強制結束,印留下的工作樹路徑。
   - 記:每個壞法一筆治理帳 gate `choice-kill`、kind `choice-kill`,欄位 `file`、`line_sha`、`row`、`new_sha`、`verdict`、`killing_test`、`clauses`、`plans`、`tests_sha`(守的測試集合與各自所在檔物件編號的雜湊)、`reason`(no_result)、`via`(`run` 或 `situation-rule`)、`attempt`(同一行第幾筆)、`run_id`、`catalog`(型錄雜湊前 12 碼)、`token`;每次呼叫結束一筆 kind `run`(`run_id`、改到的行數、有選擇點的行數、有壞法的行數、跑的壞法數、各 verdict 數、耗時秒數、ast-grep 版本、守的測試對各自所在檔物件編號的對照、`token`)。寫完印「下一步:提交治理帳(推送閘只讀被推送版本的帳)」。
   - rc 取最大:全部有效處置 → 0;有存活 → 1;有 no_result、不唯一、沒跑完或中斷 → 2。
   - 不寫計劃、不改程式。
   **`lumos choice-judge <定位> --as equivalent|not-requirement|not-applicable --reason "<至少 10 實字>" [--consent …]`**(判,獨立子指令,同 guard 的 kill-add 那種「只寫帳」的指令形狀):讀 HEAD 版的檔與範圍(跟 choice-kill 同一套範圍),不跑測試、不要求工作目錄乾淨;那一行是存活、no_result 或不唯一都能判;不是改到的行、沒有壞法、乾節點、行號不合 → rc 2。記 kind `judged`(欄位 `file`、`line_sha`、`row`、`as`、`reason`、`origin`、`consent`、`token`)。
3. **存活的處置**:
   - **規格沒寫** → `lumos situation-rule --point <定位> --plan … --clause … --test … [--consent …]`:situation-rule 多一條選擇點路徑,`--seg`/`--row`/`--file`/`--old`/`--new` 改選用、跟 `--point` 互斥(入口驗證)。選擇點路徑抽出三塊不吃情境段的零件:平台與檔解析(照 `--test` 那支測試的平台)、事件欄位(帶 `point` 與壞法身分,不帶 seg/row)、結尾提示(講選擇點,不講段與列)。檢查改成「定位在目前範圍算得出壞法、old 在 HEAD 恰好一次」;`--old`/`--new` 由那個壞法帶入,需補的 import 自動帶。條款寫回、綁測試、跑殺傷力(要 killed)、記人裁事件照原本流程;條款文字與測試跟計劃裡既有一條相同時不插第二條,改成對這個壞法跑殺傷力、killed 就把既有條款記給它(冪等鍵是壞法身分)。成功後另記一筆 `choice-kill` killed(`via: situation-rule`)。帶 `point` 的人裁事件:`_gov_situation_spec_counts` 不算;`_spec_gate_ruled_events` 不拿它免預期值表列(選擇點寫回的條款照樣要預期值表列,風險高計劃照樣要簽)。
   - **測試太弱** → 補測試或改綁後重跑 `choice-kill`(或 `--only <定位>`)。
   - **換了一樣/不是需求/壞法不適用** → `choice-judge`。判 `not-requirement` 的不自動推廣;`gov --stats` 依 (列號、外層宣告名) 列「乾節點候選」(同形狀被判 3 次以上),人決定要不要寫成〈乾節點規則〉新列(論文 3.1)。
   - **程式不該有這個選擇**(DO-178C)→ 改程式拿掉它。
4. **推送前那一道**:在 `_spec_gate_push_check` 裡、`_spec_gate_push_scan` 之後另起一圈(沒有候選計劃也跑);擋下輸出跟預期值表缺簽合在同一次輸出,標題與尾段建議依擋下的種類分開寫(`_spec_gate_push_bad_head` 補「選擇點」標籤,計數是行數不是計劃數;只因選擇點被擋時不印「規格閘要紅、推送閘要綠」那段)。
   - **接線**:`spec-gate --push-check` 新增選用參數 `--push-remote <遠端>` 與 `--pushed-ref <被推的 ref>`(成對,同 drift、room-guard、reread-check 的先例);pre-push 掛鉤先 grep lumos 裡這兩個參數的專屬 dest 字樣探版本,有才帶(同 pitfalls 那行的探針做法),沒有就只用推送範圍本身。
   - **範圍**:B 取推送範圍右端;主線照 `_push_mainlines`(跳過被推的那條)。被推的 ref 本身是主線 → 改到的行用推送範圍本身;否則用主線與 B 的分岔點..B;算不出 → 用推送範圍本身。B 取不到照既有算不出範圍放行規則。
   - **讀哪一版**:改到的檔用 `_kt_sit_read_many` 讀 B 版(交 ast-grep 的是暫存檔,掃完刪)、治理帳用 `_gov_rows_at` 讀 B 版、碰到的計劃照〈用詞〉在 B 的樹上建圖譜取,同一輪按 (提交, 檔) 快取只讀一次;測試名存在照 B 版樹判。預期值表那圈照舊讀工作目錄(既有天花板)。不重跑 Gradle。
   - **算不出來**:沿用 `_KT_SIT_BUDGET` 時限;單檔超過讀檔上限 → 那支檔跳過、列出(不擋);整體逾時或讀不到 → 這一圈只提醒不擋並記一筆 kind `unverified`(規格閘「算不出來就放行」)。治理帳在 B 不存在或讀不到 → 擋(同預期值表那道,reason 分「帳不在」「帳讀不了」)。ast-grep 不在而範圍有 `.kt` 正式碼改動 → 擋 reason「沒有 ast-grep」、印安裝指令。
   - **條件**:改到的行裡有 `.kt` 正式碼、至少一行有壞法、專案有 kotlin-junit 平台、生效日之後。
   - **判定**:回報上限抽中的存活行、全部 no_result、不唯一、過期、缺紀錄的行 → 擋;沒抽中的存活列最後一段不擋。範圍沒碰到任何進行中計劃 → 擋 reason「無規格」(訊息提醒:若計劃存在但沒連到被改檔的家,補 `lands_in` 或連結);碰到了但沒有可守的測試 → 不擋,印「這次的選擇點沒有測試守,只能人驗」。紀錄的守的測試所在檔物件編號跟 B 不同只提醒。
   - 擋下時記一筆 gate `choice-kill`、kind `blocked`(`reasons` 各帶行數、`token`、`hard: true`;同一個 B 同一組 reason 不重記)。
5. **登記與讀者**:`choice-kill` 加進 `_KNOWN_GATES`;`("choice-kill", k)`(k 為 `choice-kill`、`judged`、`run`、`blocked`、`unverified`)加進 `LOOP_NOT_CLOSE_EVENTS`(守衛不強制);五種都進版控治理帳。帳量:每筆只存雜湊與短欄位,`run` 那筆放守的測試對照(一次呼叫一筆);實作量一筆 `choice-kill` 事件在守的測試 30 支時的位元組數,要在 4096 以內(S20);`reason` 的失敗摘錄限 300 字。`_gov_row` 對 `choice-kill` 取 `token` 並帶出 `verdict`、`row`、`attempt`、`reason`、`as`、`via`、`run_id`;`_GOV_FIELD_TYPES` 登記新欄位;讀者用 `type(x) is int` 排除 bool。`--stats` 印:每次 choice-kill 的改動行數、有壞法的行數、耗時中位數(讀 `run`)、第一次跑(attempt 1)的殺掉率、存活後的處置分布(`via: situation-rule` 寫回規格、`via: run` 補測試後殺掉、各種 `as`)、no_result 原因前 5(含壞法編不過、測試掛住各自的列號)、乾節點候選前 5、單一測試殺掉 3 支以上不同檔的壞法時列出那支測試、被擋筆數與「過期」占比、`unverified` 筆數。`_backing_kill_rows` 改成「`source` 非空就跳過」;口徑寫進 Systems/guard-kill。
6. **型錄、規則與文件**:Kotlin 型錄新增〈選擇點表〉〈乾節點規則〉、`configs/ast-grep/kotlin-choice/` 規則與設定、`check.py` 的讀法與檢查(〈統計〉節若有手寫數字一併重數);規則的壞例好例樣本放 `configs/ast-grep/kotlin-choice/samples/`(新增),`check.py` 對樣本跑一次確認每條規則命中該命中的。Systems/kotlin規則包、Systems/規格閘、Systems/guard-kill 補 WHY 行;[[Projects/guard殺傷力驗證_計劃]] 補翻案決策;lumos-code-loop 手冊推送前那段補「選擇點沒處置會擋、在代碼審通過前跑 choice-kill 與處置(situation-rule 會改計劃)、帳要提交、要裝 ast-grep」;lumos-project-notes 指令索引補 `choice-points`、`choice-kill`、`choice-judge`、`situation-rule --point`;[[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 改成指向這份。圖譜每處寫到這個機制都標注論文與對應節(使用者 2026-11-13:「圖譜紀錄B案的時候這篇論文一起標注進去」)。

## 不做

- 不是每一行:乾節點不產生壞法;一行只一個壞法(論文 4.1)。
- 不引進外部變異工具(PIT 等);ast-grep 只當剖析器,是 Kotlin 規則包既有的外部工具。
- 不做論文 4.2–4.5 的依歷史排序與語法樹相似度;不接覆蓋率;不收數字常數、字串常數、`when` 分支刪除;REVISIT 看數字再加。
- 不讓 AI 自動判等價;判「不是需求」不自動推廣,乾節點規則人工增補(論文 3.1)。
- 推送前不重跑殺傷力;只讀帳、重算哪些行有壞法、驗新鮮度。
- 不管非 Kotlin 專案;測試檔、測試輔助 source set、`.kts` 不算。
- 不做多個選擇點的組合(天花板 4)。

## 實務隱患

- 跑太久:一行一個壞法;同一平台一次呼叫一棵工作樹;基準每條測試指令只跑一次、基準不綠的測試拿掉;同一壞法殺掉就停(`stop_group_on_kill`);相關的測試排前面;`--max-mutants` 分批;只跑沒有有效處置的行;每次呼叫記 `run` 給 RETIRE-IF ②。Android 新工作樹冷編譯仍貴,實作時量一次 20 行改動的實際耗時寫進報告。
- 中斷白跑:`on_row` 逐列交結果,判定完整的壞法當場記帳;強制結束印工作樹路徑。
- 噪音:乾節點規則(論文附錄 A 譯成 Kotlin 的語法樹規則)、單元測試分不出或會掛住的寫法不收、型別前提事前擋編不過(論文 3.2.1)、回報上限檔數 × 7、只改縮排的行不算、測試輔助 source set 不算。
- 壞法仍編不過或掛住:no_result 記原因,人可判 `not-applicable`;`--stats` 依列號累計給人改表。
- 判定被敷衍:判定必帶理由與同意、`--stats` 列處置分布與殺很多檔的單一測試。
- 殺掉它的測試後來被換弱:要求 `killing_test` 還在守的測試裡;測試本體改過只提醒。
- 型錄改了:有效處置以行為單位,舊帳照算;帳上記型錄雜湊備查。
- ast-grep 版本差異:不同版本剖出的節點可能不同,`run` 記版本;規則樣本由 `check.py` 驗。
- 帳量:版控治理帳已約 22MB;每筆只存雜湊,守的測試對照每次呼叫只記一次;不寫殺傷力帳本。
- 帳沒提交就推:choice-kill、choice-judge 結尾都印「提交治理帳」;推送閘從 B 讀,沒提交就是缺紀錄,訊息附「記得提交帳」。
- 跟代碼審的先後:situation-rule 會改計劃,所以 choice-kill 與處置在 `code-loop pass` 之前做;之後只有帳本提交(choice-kill 與 choice-judge 只寫帳)。回報上限的種子不受帳本提交影響。
- 跟情境題那道重疊(同一行既是情境決策表觸發字又是選擇點):兩道各管各的;人裁事件以 `point` 欄分開統計與分開預期值表豁免;可能各跑一次 Gradle(天花板 6)。
- 併發與交易:已排除:單人單機依序操作,沿用 guard kill 的隔離工作樹與人裁的訊號收尾;治理帳逐筆追加。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 在語法樹上產生壞法 | 論文 2.2(mutagenesis service navigating the AST) | https://arxiv.org/pdf/2102.11378 |
| 只對改動的行、每行一個壞法、運算子類別隨機排序取第一個產得出的 | 論文 2.2、4.1 Listing 2 | https://arxiv.org/pdf/2102.11378 |
| 五個運算子 AOR/LCR/ROR/UOI/SBR 與各自候選 | 論文表 1 | https://arxiv.org/pdf/2102.11378 |
| 乾節點以語法樹節點為單位、複合節點全乾才乾 | 論文 3.1 公式 1 | https://arxiv.org/pdf/2102.11378 |
| 乾節點規則人工照回饋增補(有用比例 15% 到 89%) | 論文 3.1、3.2.5 | https://arxiv.org/pdf/2102.11378 |
| 乾節點規則第一版內容 | 論文附錄 A.1.1–A.1.24、A.3.2 | https://arxiv.org/pdf/2102.11378 |
| `==` 只換 `!=` | 論文附錄 A.1.23 | https://arxiv.org/pdf/2102.11378 |
| SBR 不可刪的節點 | 論文附錄 A.1.12 | https://arxiv.org/pdf/2102.11378 |
| 編不過的壞法用規則事前擋(型別前提) | 論文 3.2.1 | https://arxiv.org/pdf/2102.11378 |
| 回報上限檔數 × 7、從存活隨機挑 | 論文 2.3 | https://arxiv.org/pdf/2102.11378 |
| 每個壞法只跑相關測試(我們用排序加殺掉就停近似) | 論文 2.1 | https://arxiv.org/pdf/2102.11378 |
| Kotlin 語法樹節點名 | tree-sitter-kotlin grammar.js | https://github.com/fwcd/tree-sitter-kotlin |
| ast-grep 的 Kotlin 文法 | ast-grep 維護的 tree-sitter-kotlin | https://github.com/ast-grep/tree-sitter-kotlin |
| 用 tree-sitter 做跨語言變異 | Trail of Bits mewt/MuTON | https://blog.trailofbits.com/2026/04/01/mutation-testing-for-the-agentic-era/ |
| 少數運算子就夠 | Offutt 等 1996 充分運算子 | https://dblp1.uni-trier.de/rec/journals/tosem/OffuttLRUZ96.html |
| 關係運算子只取部分替換 | Just 等非冗餘變異 | https://homes.cs.washington.edu/~rjust/publ/non_redundant_mutants_icst_2012.pdf |
| API 兄弟寫法寫成改寫表 | MutApi | https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843 |
| Kotlin 集合 any/all/none 互換 | Mutant-Kraken | https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin |
| 存活可能是規格缺口 | MutDafny | https://arxiv.org/pdf/2511.15403 |
| 追不到需求的程式補需求或刪程式 | DO-178C 結構覆蓋分析處置 | https://ldra.com/ldra-blog/do-178c-structural-coverage-analysis/ |
| 等價 AI 判讀(這一版不採) | Meta ACH | https://arxiv.org/html/2501.12862 |
| 不採 PIT | PIT 協程議題、Arcmutate 授權 | https://lightrun.com/answers/hcoles-pitest-pitest-generates-unhelpful-mutations-when-using-kotlins-coroutines、https://central.sonatype.com/artifact/com.arcmutate/pitest-kotlin-plugin |
| 換寫法跑測試的零件沿用人裁 | 人裁已在真 Gradle 專案判出 killed | 實測 2026-11-13:測試品質實驗室 Android 副本帶 --import 跑 lumos situation-rule,約 10 秒判 killed、寫回 S3 |
| 選擇點代表需求、可窮舉、審查可機械化 | 使用者大方向 | 使用者 2026-11-13:「改動中的語法,必定是代表一種需求……語法是可以被窮舉的,也就代表 code review 是可以被機械層檢查」 |
| 涵蓋所有開發需求的程式碼 | 使用者方向 | 使用者 2026-11-13:「我想涵蓋的就是所有開發需求中的程式碼,不是特定哪一種類別的語法」 |
| 照論文實作、有問題優先參考論文 | 使用者方向 | 使用者 2026-11-13:「那就照那份論文來實作」「有什麼問題,優先參考」 |
| 改用 ast-grep 語法樹 | 使用者裁定 | 使用者 2026-11-14:「改用 ast-grep 語法樹」(設計審兩輪被文字近似打穿後的選項) |
| 沒碰到計劃照擋 | 使用者裁定 | 使用者 2026-11-13:「照擋,沒規格就無法判定當前需要援引的語法需求來源」 |

## 驗收條款

- [S1] 當改動行有選擇點規則命中的節點,choice-points 應 每行最多挑一個壞法,乾節點範圍、字串與註解、只改縮排的行、測試檔與測試輔助 source set、`.kts` 不挑 [test:t_choice_points_scan]
- [S2] 當運算子節點的運算元跨行或含括號與呼叫,choice-points 應 依語法樹的後設變數組出候選壞法;字串串接的 `+` 與非布林情境的 `true`/`false` 應 不產生 [test:t_choice_points_operands]
- [S3] 當同一行內容不變而重跑,choice-points 應 挑出同一個壞法;那一行不唯一時 應 往外帶行求唯一,仍不唯一標不唯一 [test:t_choice_points_stable]
- [S4] 當節點落在乾節點規則的範圍(含跨行引數與樣板方法本體),choice-points 應 不在裡面產生壞法;複合節點 應 只有所有子節點都乾才算乾 [test:t_choice_points_arid]
- [S5] 當 SBR 的候選陳述在呼叫引數裡、是 lambda 最後一個陳述、或是無大括號控制句的本體,choice-points 應 不產生刪除壞法 [test:t_choice_points_sbr]
- [S6] 當 ast-grep 不在 PATH,choice-points 應 回 3、choice-kill 應 回 2;推送前那一道遇到 .kt 正式碼改動 應 擋下並印安裝指令 [test:t_choice_no_ast_grep]
- [S7] 當同一平台有多個壞法,choice-kill 應 只呼叫一次殺傷力、每條測試指令基準只跑一次、同一壞法殺掉就略過其餘測試,並依 recipe_id 把結果對回 [test:t_choice_kill_batch]
- [S8] 當某壞法有一支守的測試強 killed,choice-kill 應 記 killed、帶排序第一支殺掉它的測試與條款;每支都有列而且都 survived 應 記 survived 並回 1 [test:t_choice_kill_verdicts]
- [S9] 當沒有強 killed 而有弱證據、drifted、error、壞法編不過、測試掛住或缺結果,choice-kill 應 記 no_result 帶原因並回 2;某支測試基準 abort 時 應 拿掉那支、其餘照判 [test:t_choice_kill_no_result]
- [S10] 當工作目錄不乾淨、範圍沒碰到進行中計劃、計劃沒有可守的測試、或 run_cmd 沒有 {method},choice-kill 應 回 2 不跑 [test:t_choice_kill_rejects]
- [S11] 當同一行已有有效處置,choice-kill 應 跳過那一行;壞法超過 --max-mutants 應 只跑那麼多並說還剩幾個;每次呼叫 應 記一筆 run [test:t_choice_kill_incremental]
- [S12] 當 choice-kill 跑到一半收到第一個中斷訊號,choice-kill 應 記下已有完整判定的壞法與一筆 interrupted 的 run 並回 2 [test:t_choice_kill_interrupt]
- [S13] 當 choice-judge 帶 as、理由與同意,choice-judge 應 記一筆 judged、推送前那一道 應 視那一行已處置;理由不到 10 實字或定位不是有壞法的改到的行 應 回 2 [test:t_choice_judge]
- [S14] 當 situation-rule 帶 --point 而寫回成功,situation-rule 應 用那個壞法跑殺傷力、記人裁事件帶 point 並另記 choice-kill killed;條款文字與測試已存在時 應 把既有條款記給這個壞法;帶 point 的事件 應 不免預期值表列 [test:t_situation_rule_point]
- [S15] 當推送範圍有行沒有有效處置(缺、抽中的存活、no_result、不唯一、過期),推送前那一道 應 擋下、每種原因最多列 20 行並記 blocked [test:t_spec_gate_push_choice]
- [S16] 當存活行超過檔數乘 7,推送前那一道 應 只對用「曾經存活的行」集合當種子抽中的那些擋;提交帳本 應 不改變抽中的那批 [test:t_spec_gate_push_choice_cap]
- [S17] 當推送範圍有選擇點但沒碰到任何進行中計劃,推送前那一道 應 擋下 reason 無規格;碰到的計劃沒有可守的測試時 應 只提醒不擋 [test:t_spec_gate_push_choice_no_plan]
- [S18] 當推送的是功能分支,推送前那一道 應 用主線與 B 的分岔點..B 算改到的行;推主線本身時 應 用推送範圍本身;掛鉤遇到不認得新參數的舊 lumos 時 應 不帶參數照舊跑 [test:t_spec_gate_push_choice_range]
- [S19] 當推送範圍是 `A..B` 而工作目錄的檔、計劃狀態或條款跟 B 不同,推送前那一道 應 只看 B 版本 [test:t_spec_gate_push_choice_pushed_version]
- [S20] 當掃描逾時或檔讀不了,推送前那一道 應 只提醒並記 unverified;B 版治理帳不在或讀不了 應 擋下;守的測試 30 支時一筆 choice-kill 事件 應 不超過 4096 位元組 [test:t_spec_gate_push_choice_unverifiable]
- [S21] 當計劃日期早於生效日、專案沒有 kotlin-junit 平台、或改到的行沒有壞法,推送前那一道 應 不要求 [test:t_choice_exemptions]
- [S22] 當治理帳有 choice-kill 事件,gov --stats 應 印每次呼叫的改動行數、有壞法行數與耗時中位數、第一次跑殺掉率、存活處置分布、no_result 原因前 5、乾節點候選前 5、被擋筆數與過期占比 [test:t_gov_stats_choice_kill]
- [S23] 當型錄缺檔,choice-points 與推送前那一道 應 只提醒不擋;型錄在但缺〈選擇點表〉或〈乾節點規則〉、表壞、或規則檔與列號對不上 應 擋並指出哪一列 [test:t_choice_table_missing]
- [S24] 當型錄改了讓同一行挑到另一個壞法,推送前那一道 應 照舊認那一行原本的有效處置 [test:t_spec_gate_push_choice_catalog_change]
- [S25] 當在測試品質實驗室 Android 副本把搜尋 ViewModel 的 `flatMapLatest` 那一行改動推送、綁的測試只送一次值,choice-kill 應 判那一行 survived;換回送兩次值的測試 應 判 killed [manual:在實驗副本裝 ast-grep 後跑 lumos choice-kill,先用只送一次值的 onlyLatestQueryShown 看 survived,再換回原測試看 killed;那一行只有 flatMapLatest 一個類別]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 改動行 `.flatMapLatest { repo.search(it) }`(檔頭逐一 import flatMapLatest) | 一個 API 壞法 flatMapConcat,自動補 `import kotlinx.coroutines.flow.flatMapConcat` | 〈用詞〉選擇點表 API 列 |
| S1 | 改動行 `if (count > limit && enabled)` | 只挑一個壞法(ROR、LCR、UOI 三類依種子取一類) | 論文 4.1 Listing 2 |
| S1 | 改動行 `Log.d(TAG, "q=${q.size > 0}")` | 沒有壞法(log 節點整個乾) | 論文附錄 A.1.1 |
| S1 | 改動行 `require(x > 0)` | 沒有壞法 | 論文附錄 A.1.5 |
| S1 | 改動行 `// flatMapLatest here` 與 `val s = "a < b"` | 沒有壞法 | 〈用詞〉選擇點不在字串與註解 |
| S1 | 改動在 `shared/src/commonTest/…/Helper.kt`、`app/src/testFixtures/…/Fake.kt` | 沒有壞法 | 〈用詞〉改到的行測試判法 |
| S1 | 改動在 `app/build.gradle.kts` 含 `a > b` | 沒有壞法 | 〈用詞〉只收 .kt |
| S1 | 把 10 行包進 `withContext(io) { … }` 只改縮排 | 那 10 行不挑 | 〈用詞〉改到的行沿用 _kt_sit_hits |
| S2 | `if (x.size + 1 > limit)` 抽到 ROR 的 true | 新行 `if (true)`(運算元 `x.size + 1` 整段) | 〈用詞〉ROR 用後設變數 |
| S2 | `if (a > 0 &&` 換行 `    b < 3)` 抽到 LCR 的 `$A` | old 含兩行,new 是 `if (a > 0)` | 〈用詞〉old 含節點最後一行 |
| S2 | `val s = "id=" + n` | AOR 不產生(字串串接) | 論文 3.2.1 型別前提 |
| S2 | `val total = price * qty` 抽到 ROR | 不會(沒有 comparison 節點);AOR 給 `price / qty` 等 | 論文表 1 AOR |
| S2 | `val ok = a > b`(賦值,不是條件) | ROR 只給 `<`、`<=`、`>=`,不給 true/false | 〈用詞〉布林情境才給 true/false |
| S2 | `val s = "x ${a < b}"` | `<` 算選擇點 | 〈用詞〉字串樣板裡的運算式照算 |
| S3 | 同一行跑兩次 choice-points | 兩次挑同一個壞法 | 〈用詞〉一行一個壞法的種子 |
| S3 | 兩行完全相同、前後各兩行也相同 | 標不唯一、不跑 | 〈用詞〉壞法身分 |
| S3 | 那一行是另一行的子字串、多帶上一行就唯一 | old 是兩行 | 〈用詞〉往外帶行 |
| S4 | `Timber.d(` 換行 `    "n=${items.filter { it > 0 }.size}",` 換行 `)` | 三行都沒有壞法 | 論文 3.1 公式 1 節點為單位 |
| S4 | `override fun toString() = "a" + b` | 沒有壞法 | 論文附錄 A.1.21 |
| S4 | `delay(retry * 1000L)` | 引數裡沒有壞法 | 論文附錄 A.1.4 |
| S4 | `if (BuildConfig.DEBUG) { Log.d(TAG, "x") }` | 整個 if 沒有壞法 | 論文附錄 A.1.13、公式 1 |
| S4 | `if (items.size > 0)` | 沒有壞法 | 論文附錄 A.1.20 |
| S4 | `@Provides` 在上一行、下一行 `fun repo(api: Api) = RepoImpl(api)` | 函式本體沒有壞法 | 論文附錄 A.3.2 |
| S4 | `if (BuildConfig.DEBUG && x > 1) …` | `x > 1` 照常可挑(複合節點不是全乾) | 論文 3.1 公式 1 |
| S5 | `combine(` 換行 `    flowA(),` 換行 `    flowB(),` 換行 `) { a, b -> a + b }` | `flowB()` 不是 SBR 候選 | 論文附錄 A.1.12 參數 |
| S5 | `list.map { x ->` 換行 `    transform(x)` 換行 `}` | `transform(x)` 不是 SBR 候選 | 論文附錄 A.1.12 回傳值 |
| S5 | `if (ready)` 換行 `    start()` | `start()` 不是 SBR 候選 | 〈用詞〉SBR 無大括號本體 |
| S5 | 函式本體 `{ save(x)` 換行 `  notify() }` 的 `save(x)` | 是 SBR 候選 | 〈用詞〉SBR statements 直接子節點 |
| S6 | PATH 裡沒有 ast-grep | choice-points rc 3、choice-kill rc 2、推送擋 reason 沒有 ast-grep | 〈用詞〉語法樹掃描 |
| S7 | 假平台:3 個壞法、守的測試 t_a、t_b(都帶 {method}) | 一次殺傷力呼叫、基準 t_a 與 t_b 各一次;t_a 殺掉的壞法不跑 t_b | 〈用詞〉殺掉判定 stop_group_on_kill |
| S7 | 守的測試 t_k 在非預設平台 | t_k 的配方在它的平台根跑 | 〈用詞〉殺掉判定 platform 欄 |
| S8 | 假平台:t_a 紅 | killed、killing_test t_a、clauses 是綁 t_a 的條款 | 〈用詞〉殺掉判定 |
| S8 | 假平台:t_a 弱證據、t_b killed | killed、killing_test t_b | 〈用詞〉任一支強 killed |
| S8 | 假平台:t_a、t_b 都綠 | survived、rc 1 | 〈範圍〉2 rc |
| S9 | 假平台:換完印 `e: Type mismatch` | no_result、reason 壞法編不過、rc 2 | 〈用詞〉殺掉判定 |
| S9 | 假平台:壞法逾時 | no_result、reason 測試掛住 | 〈用詞〉殺掉判定 |
| S9 | 假平台:t_a 基準就紅、t_b 殺掉壞法 | killed by t_b;t_a 記基準不綠沒跑 | 〈用詞〉基準 abort 拿掉那支 |
| S9 | 假平台:revert 失敗讓後面配方沒列 | 沒列的壞法 no_result、reason 缺結果 | 〈用詞〉缺結果 |
| S10 | 計劃檔有未提交改動 | rc 2、沒跑 | 〈範圍〉2 跑之前的檢查 |
| S10 | 範圍碰不到進行中計劃 | rc 2、說沒規格判不了 | 〈範圍〉2 跑之前的檢查 |
| S10 | run_cmd `./gradlew test`(沒有 {method}) | rc 2 | 〈用詞〉守的測試 run_cmd |
| S11 | 第一次 3 行全 killed,再跑一次 | 3 行都跳過、記一筆 run(跑的壞法數 0) | 〈實務隱患〉只跑沒處置的 |
| S11 | 40 個壞法、`--max-mutants 30` | 跑 30 個、說還剩 10 個 | 〈範圍〉2 max-mutants |
| S12 | 假平台:5 個壞法,第 3 個跑完後送 SIGINT | 前 2 到 3 個記帳、run 帶 interrupted、rc 2 | 〈範圍〉2 中斷 |
| S13 | `choice-judge app/…/Vm.kt:12 --as not-applicable --reason "型別不合換了編不過不是需求" --consent "這個不適用"` | 記 judged、origin ai、consent 是原話;推送不擋那一行 | 〈範圍〉2 判 |
| S13 | `--reason "等價"` | rc 2 | 〈範圍〉2 判理由 |
| S13 | 定位指到乾節點那一行 | rc 2 | 〈範圍〉2 判定位 |
| S13 | 定位 `a:b.kt:12`(檔名含冒號) | 檔 `a:b.kt`、行 12 | 〈用詞〉定位從右切 |
| S14 | survived 那一行跑 `situation-rule --point …`,新條款綁的測試在壞法下紅 | 條款寫回、人裁事件帶 point、另記 choice-kill killed | 〈範圍〉3 規格沒寫 |
| S14 | 同一段條款文字與同一支測試,先後給兩個不同的 `--point` | 一條條款、兩行各記 killed | 〈範圍〉3 既有條款記給新壞法 |
| S14 | `--point` 與 `--seg` 一起給 | rc 2 | 〈範圍〉3 來源互斥 |
| S14 | 風險高計劃經 `--point` 寫回新條款 | 預期值表仍要那條的列 | 〈範圍〉3 point 不免預期值表 |
| S15 | 一行沒紀錄 | 擋、列出那一行與 `lumos choice-kill` | 〈範圍〉4 判定 |
| S15 | 一行 killed by t_strong,條款現在綁 t_weak | 擋、reason 過期 | 〈用詞〉過期 |
| S15 | 300 行缺紀錄 | 列 20 行示例與總數 | 〈用詞〉排版 |
| S15 | 同時預期值表缺簽 | 同一次輸出、兩個標題分開 | 〈範圍〉4 同一次輸出 |
| S16 | 改 2 支檔、曾經存活 20 行 | 抽 14 行擋、6 行列在沒抽到 | 論文 2.3 回報上限 |
| S16 | 處置抽中的 14 行、提交帳本再推 | 沒抽到的 6 行仍不要求 | 〈用詞〉回報上限種子 |
| S17 | 改了 Kotlin 選擇點、範圍沒碰任何進行中計劃 | 擋、reason 無規格 | 使用者 2026-11-13 裁:沒規格就照擋 |
| S17 | 碰到的計劃條款全是 `[manual:]` | 不擋、印只能人驗 | 規格閘 manual 小改動裁定 |
| S18 | 推功能分支,分岔點 F | 改到的行用 F..B | 〈範圍〉4 範圍 |
| S18 | 推 main 本身 | 改到的行用推送範圍 A..B | 〈範圍〉4 範圍 |
| S18 | 掛鉤新、lumos 舊(沒有那兩個 dest) | 不帶參數,規格閘其他圈照跑 | 〈範圍〉4 接線探針 |
| S19 | 工作目錄比 B 多一個沒紀錄的選擇點 | 不擋 | 〈範圍〉4 讀哪一版 |
| S19 | 工作目錄的計劃已改成 done、B 是 doing | 照 B 當進行中 | 〈用詞〉碰到的計劃讀被讀版本 |
| S20 | 掃描超過 `_KT_SIT_BUDGET` | 不擋、提醒、記 unverified | 〈範圍〉4 算不出來 |
| S20 | B 版沒有治理帳檔 | 擋、reason 帳不在 | 〈範圍〉4 算不出來 |
| S20 | 守的測試 30 支、reason 帶 300 字摘錄 | 一筆事件 ≤ 4096 位元組 | 〈範圍〉5 帳量 |
| S21 | 計劃日期早於生效日 | 不要求 | 〈用詞〉生效日 |
| S21 | 專案只有 python 平台 | 不要求 | 〈範圍〉4 條件 |
| S21 | 改動只有 log 與 import | 不要求 | 〈範圍〉4 條件 |
| S22 | 帳上 run 兩筆(改動行 10、30,耗時 60、180 秒);attempt 1 的 killed 3、survived 1、no_result 1;via situation-rule 的 killed 1(attempt 2);judged not-applicable 1;blocked 4 筆其中過期 1 | 改動行中位數 20、耗時中位數 120 秒;第一次跑殺掉率 3/5;存活處置寫回規格 1、判不適用 1;被擋 4(過期 1/4) | 〈範圍〉5 RETIRE-IF 的數 |
| S23 | 型錄檔不在 | choice-points 提醒 rc 0;推送不擋、印提醒 | 〈用詞〉讀表缺檔只提醒 |
| S23 | 型錄在但沒有〈乾節點規則〉節 | 擋、說缺哪一節 | 〈用詞〉讀表缺節要擋 |
| S23 | 〈選擇點表〉列 C-3 在規則檔裡沒有對應規則 | 擋、指出 C-3 | 〈用詞〉讀表規則檔對得上 |
| S24 | 那一行原本 killed(挑到 ROR),型錄新增一列讓它挑到 API | 推送不擋(那一行已有有效處置) | 〈用詞〉有效處置以行為單位 |
| S25 | 實驗副本只送一次值的測試 | survived;換回原測試 killed | 使用者 2026-11-13 面試題 |

## 回退

- 整個關掉:`_CHOICE_SINCE` 設成很遠的未來日期,推送那一道不要求;指令照留、只是沒人需要。
- 單一列誤報多:從〈選擇點表〉拿掉那一列,或在〈乾節點規則〉加一列(下一次推送就不再算;舊帳以行為單位照算)。
- `cmd_guard_kill` 的 `source`、`stop_group_on_kill`、`on_row`,situation-rule 的 `--point`,`spec-gate --push-check` 的 `--push-remote`/`--pushed-ref` 都是選用,不傳維持原行為。

## 天花板

1. 只證「選擇點表列到的寫法有測試守著」;表沒列到的選擇(數字常數、`when` 分支、整段邏輯)這一版不管;表與乾節點規則列得好不好決定上限(論文也承認規則依環境調)。
2. ast-grep 給的是語法樹、沒有型別;型別前提只能用語法情境近似(字串字面值、布林情境),推不出型別的壞法仍可能編不過,落成 no_result 要人判。ast-grep 或文法版本變了,節點可能不同。
3. 沒有覆蓋率:沒被守的測試跑到的行一定存活,要人處置;每個壞法跑全部守的測試(排序加殺掉就停),比論文的最小測試集慢。
4. 一行一個壞法、不做組合;同一行其他類別這次沒被挑到就不驗——面試題那種 `flatMapLatest` 若跟條件式同一行,有一半以上的機會挑到別的類別(論文的取捨;情境題那道另外會問 D-4)。
5. 殺掉只證「換成那個壞法時有測試紅」,不證測試紅的理由就是那條需求;條款跟選擇點是不是講同一件事靠人裁與代碼審。
6. 推送前不重跑,信帳;帳是作者自己跑出來的,同代碼審留痕的天花板。跟情境題那道對同一行可能各跑一次 Gradle。
7. 回報上限之外的存活不擋;新的存活行出現時重抽。
8. 判「不是需求」全靠人;判錯會放過規格缺口,乾節點規則寫錯會整類放過。
9. 掃描算不出來時那一圈放行(規格閘既有方針),只留 unverified 紀錄。

## 審計修正紀錄

- r1(2026-11-13,6 席,前一版「條款近似錯誤寫法要殺得掉」):52 條/blocking 24/方向改了。席報告在 governance/review-reports/條款近似錯誤寫法要殺得掉/。
- r1 收斂後複審(同日,3 席,不記帳):28 條/blocking 8。報告在同目錄。
- 方向重定(2026-11-13,使用者):整份改寫成「改動選擇點全數產生壞法、存活交人裁」。
- 前掃(2026-11-13,preflight-4):25 條,都修進真檔;逐條在 governance/review-reports/改動選擇點都要有需求守住/r1-intake.md。
- r1(2026-11-13,6 席):53 條/blocking 22/核心設計站得住,機制層大改並照使用者「照論文實作」對齊 Google 論文。席報告在 governance/review-reports/改動選擇點都要有需求守住/。
- r1 方向由使用者 2026-11-13 裁:「那就照那份論文來實作」「有什麼問題,優先參考」。
- r2(2026-11-14,6 席):73 條/blocking 31/文字近似語法樹連兩輪被打穿(運算元、SBR 位置、乾節點跨行)——照論文改用語法樹(ast-grep);同時修正對論文的誤引(表 1 候選、Listing 2 是類別洗牌、3.2.4 不是種子、A.1.6)、殺掉判定加 abort 拿掉與缺結果、批次加殺掉就停與逐列交結果、回報上限種子改成曾經存活的集合、有效處置改以行為單位、推送閘照規格閘算不出來放行並加掛鉤探針、碰到的計劃從 B 版樹建圖譜。席報告與分組在同目錄 r2-*。
- r2 方向由使用者 2026-11-14 裁:改用 ast-grep 語法樹。
