---
type: project
status: todo
created: 2026-11-13
updated: 2026-11-13
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

改動裡「換一種寫法照樣編得過、行為卻不同」的地方(選擇點),是寫的人做了一個決定,背後應該有一條需求。這份計劃照 Google 的差異式變異測試(論文〈Practical Mutation Testing at Scale〉,以下稱「論文」)做:工具從改動的每一行挑一個壞法(把選擇點換成表上的另一種寫法),一次批次跑計劃條款綁的測試:
- 測試紅了(殺掉) → 記下是哪條條款守住這個選擇;
- 測試沒紅(存活) → 這個選擇沒有需求守著:規格沒寫、測試太弱、或換了其實一樣 → 推送前擋下交人裁;人裁寫回規格並綁一支會紅的測試,或判「換了一樣/不是需求/壞法不適用」留帳。

不是每一行:log、斷言、時間、樣板方法這類「乾節點」(論文的 arid node)不產生壞法;一行只產生一個壞法;要人處置的存活最多「改到的檔數 × 7」個(論文 2.3 節)。哪些寫法算選擇點、哪些節點是乾的,由 Kotlin 型錄的〈選擇點表〉與〈乾節點規則〉窮舉;乾節點規則由人照回饋手動增補(論文 3.1 節)。

這份把 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 的正向(條款的測試分不分得出對錯)與反向(程式的選擇有沒有需求撐腰)併成同一個機制:殺掉的那一點是正向的證據,存活的那一點就是反向要找的「沒有出處的選擇」。

大方向(使用者 2026-11-13):「改動中的語法,必定是代表一種需求,而這個需求,必須引得出規格……語法是可以被窮舉的,也就代表 code review 是可以被機械層檢查」;「我想涵蓋的就是所有開發需求中的程式碼,不是特定哪一種類別的語法」;範圍是選擇點、不是每一行;實作照論文、「有什麼問題,優先參考」論文(同日對話)。

PRIOR-ART: 主依據是 Google 差異式變異測試(論文 https://arxiv.org/pdf/2102.11378):只對改動且有覆蓋的行產生變異、每行一個(隨機排序運算子、第一個產得出的就用)、五個運算子 AOR/LCR/ROR/UOI/SBR、乾節點由一組人工維護的規則壓掉(附錄 A:log、斷言、時間、監控、容量、樣板方法、提早 return、旗標、資料流 flush/close、依賴注入……)、開發者按「沒用」後由人把整類寫成新規則(有用比例 15% → 89%)、每次改動最多回報「檔數 × 7」個存活、同一個壞法每次都要穩定出現(3.2.4 節)。補充:少數運算子就夠(Offutt 等 1996,https://dblp1.uni-trier.de/rec/journals/tosem/OffuttLRUZ96.html;Just 等,https://homes.cs.washington.edu/~rjust/publ/non_redundant_mutants_icst_2012.pdf);API 兄弟寫法寫成改寫表(MutApi,https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843;Mutant-Kraken 的 any/all/none 互換,https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin);存活可能是規格缺口(MutDafny,https://arxiv.org/pdf/2511.15403);追不到需求的程式是非預期功能,處置是補需求或刪程式(DO-178C,https://ldra.com/ldra-blog/do-178c-structural-coverage-analysis/)。跟論文不同的地方:①論文用語法樹判節點,我們沒有 Kotlin 語法樹,用剝註解字串後的文字比對加「呼叫形」限制近似(天花板 2);②論文只變異有覆蓋的行,我們沒有 Kotlin 覆蓋率,改成只用條款綁的測試、沒覆蓋的行存活時照樣要處置(天花板 3);③論文的存活是不強制的提示,我們照使用者裁定擋推送(使用者 2026-11-13:「照擋,沒規格就無法判定當前需要援引的語法需求來源」);④多了 Kotlin API 兄弟寫法互換(MutApi 形狀)。不採:PIT——協程上大量無用變異(https://lightrun.com/answers/hcoles-pitest-pitest-generates-unhelpful-mutations-when-using-kotlins-coroutines;2026-11-13 實驗副本也量到),過濾外掛 Arcmutate 是商用授權(https://central.sonatype.com/artifact/com.arcmutate/pitest-kotlin-plugin);論文 4.2 的「依歷史表現排序運算子」與 4.3–4.5 的語法樹相似度(這一版樣本不夠,REVISIT);AI 自動判等價(Meta ACH,https://arxiv.org/html/2501.12862)。
RETIRE-IF: 上線兩個月,看 `gov --stats` 的選擇點數字:①被回報的存活裡被人判「等價、不是需求或壞法不適用」的超過八成(論文起步時 85% 沒用,補了乾節點規則仍降不下來就是表或判法錯),或②每次 choice-kill 呼叫耗時中位數超過十分鐘,或③推送被擋的筆數裡超過一半是「過期」——就把推送那一道降成只提醒,回頭縮表或改判法。
REVISIT:2027-01-15 讀 gov --stats 的選擇點數字(殺掉率、存活處置分布、乾節點候選、每次 choice-kill 的行數與耗時),決定要不要照論文 4.2 依歷史表現排序運算子、要不要加數字常數類選擇點、要不要接 Kotlin 覆蓋率(JaCoCo)只變異有覆蓋的行

## 舊否決比對

- [[Projects/guard殺傷力驗證_計劃]] 決策 d1「合約殺傷力驗證不自動產生變異」(理由:人宣告的壞法保證語意有變、零依賴跨語言工具不內建語言知識):這份是自動產生壞法,等於在「改動選擇點」這個範圍翻了 d1。實作時用 `lumos decision-add` 在那份計劃補一筆決策:d1 限定在「合約殺傷力配方」,改動選擇點改由本計劃依論文自動產生;翻案理由是論文的規模實證與乾節點規則把等價與誤報壓到可處置的量。零依賴照守(不引進 PIT)。
- [[Projects/高風險測試證據加嚴_計劃]] 第二批「CI 對改到的行跑變異測試」:那份打算接外部工具,排在 2026-12-15 回頭看;這份不碰外部工具。回頭看時改讀這份的帳。
- [[Systems/guard-kill]] 否決「另抽一支共用的殺傷力函式」:這份沿用 `cmd_guard_kill` 的 `recipes_override`,不另抽。
- [[Systems/規格閘]] 的裁定「條款全是 `[manual:]` 的小改動不必綁測試、推送印 light」:這份不翻;計劃沒有可守的測試時,推送前那一道只提醒、不擋(見範圍 4)。
- 本計劃前一版(2026-11-13 設計審 r1,當時叫「條款近似錯誤寫法要殺得掉」)讓條款自己宣告 `[near:]` 要換的寫法:只管被點名的寫法,整個換掉;卷證留在 governance/review-reports/條款近似錯誤寫法要殺得掉/。
- 同一份計劃改寫後的第一輪設計審(governance/review-reports/改動選擇點都要有需求守住/)提的「需求脈絡組一組一題、判不是需求自動推廣到同樣式」:跟論文不同(論文逐行回報、乾節點規則人工增補),而且分組鍵與樣式範圍連席打穿,撤掉;只留「按外層宣告排版顯示」。

## 用詞

- **前置**:[[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]](2026-11-13 已合進主線):補 import 的 `--import` 與 `also`、失敗摘錄、Android run_cmd 檢查、殺傷力在平台根跑。
- **論文**:Petrović、Ivanković、Fraser、Just,〈Practical Mutation Testing at Scale: A view from Google〉,https://arxiv.org/pdf/2102.11378 。本計劃有疑義時先回這份找答案(使用者 2026-11-13 裁)。
- **選擇點表**:Kotlin 型錄(`skills/kotlin-idioms/checks-catalog.md`)新增一節〈選擇點表〉,每列一個成員:列號(`C-<n>`)、運算子(論文的 `AOR`、`LCR`、`ROR`、`UOI`、`SBR`,加本計劃的 `API`)、成員、候選壞法(一到數個,依序)、對應的情境決策表列號(有就填,例 D-4)、為什麼行為不同、出處。第一版:
  - ROR(論文表 1):`a > b` → `a >= b`、`a < b`、`true`、`false`;其餘關係運算子同形;`==` 只換 `!=`、`!=` 只換 `==`(論文附錄 A.1.23)。
  - LCR:`a && b` → `a || b`、`a`、`b`、`true`、`false`;`||` 同形。
  - AOR:`a + b` → `a - b`、`a`、`b`;`-`、`*`、`/`、`%` 同形。
  - UOI:布林運算元 `b` → `!b`;拿掉前置 `!`。
  - SBR:刪掉一整行的單句呼叫陳述(只限那一行恰好是一個完整的呼叫、括號成對、不是宣告、不是 return、不是函式最後一句的運算式);論文附錄 A.1.12 列的不可刪節點(三元、參數、宣告、非 Unit 函式唯一陳述)不刪。
  - API(本計劃,MutApi 形狀;只認呼叫形 `.成員(`、`.成員 {`、`.成員<`):`filter`↔`filterNot`、`any`→`none`、`all`→`any`、`none`→`any`、`first`↔`last`、`firstOrNull`↔`lastOrNull`、`sortedBy`↔`sortedByDescending`、`take`↔`takeLast`、`drop`↔`dropLast`、`minByOrNull`↔`maxByOrNull`、`flatMapLatest`→`flatMapConcat`、`flatMapConcat`→`flatMapMerge`、`flatMapMerge`→`flatMapConcat`、`collectLatest`↔`collect`、`coroutineScope`↔`supervisorScope`(呼叫形 `coroutineScope {`)、`.distinctUntilChanged()` 拿掉(SBR 的呼叫鏈變形)。
  - 單元測試分不出來的寫法不收(`Dispatchers.*` 互換、`SharingStarted.*` 互換、`flowOn`、`buffer`、`conflate`),理由同論文附錄 A.1.4 時間類與 A.1.6 框架類:測試裡被假實作換掉。
- **乾節點規則**:同一份型錄新增一節〈乾節點規則〉,每列一條:列號(`A-<n>`)、比對形狀(呼叫名、接收者名、所在函式名或註記)、範圍(那一行、或整個函式本體)、論文對應的附錄節、為什麼沒用、加入日期與依據(人裁的哪一筆判定)。第一版照論文附錄 A 譯成 Kotlin:log(`Log.*`、`Timber.*`、`println`、`logger.*`)、斷言與前置條件(`require`、`check`、`assert`、`error`、`requireNotNull`、`checkNotNull`)、時間(`delay(`、`withTimeout(`、`withTimeoutOrNull(`、`Duration` 與毫秒常數所在的那一行)、監控與追蹤(`Trace.*`、`Firebase*`、`analytics.*`)、容量預配(`ArrayList(`、`HashMap(`、`StringBuilder(` 的容量參數)、樣板方法(`equals`、`hashCode`、`toString` 整個本體)、資料流 flush 與 close(`.flush()`、`.close()`)、依賴注入模組(`@Module` 類別本體、`@Provides`/`@Binds` 函式本體)、`Preconditions` 類。乾節點裡不產生壞法。
- **讀表**:兩節都由 `configs/ast-grep/kotlin-android/check.py` 的表讀法讀(把 `dt_table` 一般化成依節名讀;情境決策表行為不變),`catalog_problems` 一併檢查兩節(欄位、列號重複、壞法空白);型錄照 `_kt_catalog_path()` 取(工具鏈來源那份;測試用 `LUMOS_KT_CATALOG`)。型錄或規則包自檢檔不在(`_kt_catalog_missing`)→ 只提醒不擋;檔在但缺這兩節、或表壞 → 擋,指出哪一列。為什麼不併進情境決策表:決策表每列是「要看情境判」的題目、候選寫法要人選;選擇點表每列是論文表 1 那種機械一對一壞法,兩者用途不同;重疊的成員用「對應的情境決策表列號」欄互指,壞法只有選擇點表一個來源。
- **改到的行**:範圍內(見範圍 1、範圍 4)的增行,沿用情境題的兩道過濾:路徑照 `_kt_sit_path_ok`(排除工具自裝檔與非 Kotlin 棧檔)再加只收副檔名 `.kt`、不是測試檔(`_nodehome_is_test` 帶 `_nodehome_layout` 用 B 版檔案清單算的版面;另把 `src/testFixtures/`、`src/sharedTest/` 當測試);增行跟同一 hunk 的刪行去空白後相同的不算(同 `_kt_sit_hits`,只改縮排或包一層的不重算)。
- **選擇點**:改到的行裡,先剝檔首 BOM,再用 `_strip_c_comments(..., blank_strings=True, kotlin=True, keep_length=True)` 得到等長文字(字串樣板 `${…}` 裡的程式碼保留、反引號識別字原樣留),排除 `import`/`package` 行與乾節點之後,選擇點表成員的每一次出現;位置在等長文字上找,原文從原檔取。運算子成員要兩側是空白或換行(`a > b`、行尾的 `a &&`);`List<String>`、`->`、`..`、`?:`、`!!`、`!in`、`!is`、`!=` 裡的字元不算。API 成員只認呼叫形。反引號識別字(`` fun `a > b`() ``)裡的命中不算。
- **一行一個壞法**(論文 4.1 節 Listing 2):對每一行改到的行,把那一行的所有「選擇點 × 候選壞法」排成清單,用以「檔的 repo 根相對路徑 + 那一行剝前後空白的原文」算出的雜湊當種子打亂(同一行內容不變,每次挑中的都一樣——論文 3.2.4 要的穩定回報),依序找第一個「新那一行在整支檔裡恰好一次、而且不是已知編不過的形狀」的當這一行的壞法;一個都沒有就這一行沒有壞法。
- **壞法身分**:`file`、`line_sha`(那一行原文的 sha256 前 16 碼)、`old_sha`(`old` 的 sha256 前 16 碼)、`member`、`new_sha`。`old` 是那一行(含縮排與換行),整支檔不是恰好一次時依序往上、往下各多帶一行,最多前後各 2 行;還不唯一就這一行標「不唯一」、不跑。`new` 是 `old` 套上壞法。換行統一成 `\n`。帳上只存雜湊與 `member`,不存全文(帳量,見範圍 5);推送閘在 B 版重算壞法再用雜湊對。
- **定位**:`<檔>:<行>`(一行只一個壞法,不用再分第幾個)。
- **進行中計劃**:status 是 doing,或這次推送改到計劃檔本身而 status 是 done(預期值表那道 `_live` 的語意;實作時把 `_spec_gate_push_scan` 裡的 `_live` 抽成頂層函式共用,語意不變)。
- **碰到的計劃**:照 `_spec_gate_push_candidates`:範圍改到的計劃檔,加上 `lands_in` 或連結指到被改程式檔的家的計劃;再取其中的進行中計劃。
- **守的測試**:碰到的計劃的〈驗收條款〉裡,`[test:]` 綁的測試,扣掉 `[manual:]` 與 `[keeps]` 的條款;平台照 `resolve_test_refs`/`_split_test_ref_ex` 取,只留平台 profile 是 kotlin-junit 的;平台的 `run_cmd` 要含 `{method}`(不然整套跑是弱證據,同 guard kill 的 `weak`)。
- **殺掉判定**:同一平台、同一份計劃的所有壞法,在一次 `cmd_guard_kill` 呼叫裡跑(`node` 填那份計劃;一棵隔離工作樹;同一條測試指令的基準只跑一次,論文 2.3 的一次產生、批次執行);每個壞法對每支守的測試各一個臨時配方,配方的 `invariant` 寫成 `<定位>|<測試名>`(各自唯一,`recipe_id` 才分得開),`platform` 欄帶那支測試的平台。從 `result_out` 的列依 `recipe_id` 對回壞法與測試:任一支 `killed` 而且 `weak` 為否 → **killed**,`killing_test` 取條款順序第一支這樣的測試、`clauses` 是綁它的條款;否則任一支是 `killed_unattributed`、`timed_out_weak`、`weak`、`drifted`、`error` → **no_result**(記第一個原因與失敗摘錄);其餘全部 `survived` → **survived**。某條測試指令的基準 abort → 這次呼叫裡用到它的壞法全部 no_result(原因 abort),不重跑。
- **編不過的形狀**:壞法跑出 `killed_unattributed` 而失敗摘錄是編譯錯誤(Kotlin 的 `e:` 開頭)→ no_result 原因記「壞法編不過」;同一個 (列號, 壞法) 在 `--stats` 累計,累計 3 次以上列為「表要改」候選(論文 3.2.1 的無法編譯類規則)。
- **有效處置**:同身分最新一筆是 `killed` 而且那筆的 `killing_test` 還在現在守的測試裡;或有同身分的 `judged`。最新是 `survived`、`no_result` 不算,重跑會再跑。
- **過期**:同身分最新一筆是 `killed`,但 `killing_test` 已不在現在守的測試裡。
- **回報上限**(論文 2.3 節):一次推送要處置的存活最多「範圍內改到的 `.kt` 正式碼檔數 × 7」個;超過時用「推送範圍右端提交的完整編號」當種子從存活裡挑那麼多個(同一個 B 每次挑一樣)。沒挑中的存活不擋、列在最後一段「這次沒抽到」;下一次推送(B 變了)會重抽。
- **排版**:存活與 no_result 的回報按外層宣告排(`_kt_sit_material` 找得到的那個宣告的第一行;找不到就按檔),只是顯示,不影響判定與處置。
- **人裁同意**:照人裁那套 `_waive_origin_tty`:終端答 y 記 `origin: human`;沒有終端要 `--consent` 使用者原話,記 `origin: ai`、`consent` 必填非空白。
- **生效日**:常數 `_CHOICE_SINCE`(YYYY-MM-DD,合進主線的隔天),環境變數 `LUMOS_CHOICE_SINCE` 供測試覆寫(被覆寫成比今天晚時,推送輸出印一行「選擇點那一道被環境變數關掉」);測試總檔比照 `LUMOS_HIGH_RISK_EVIDENCE_SINCE` 預設 9999-12-31。碰到的進行中計劃任一份的計劃日期(`_plan_effective_day(..., scope="note")`)不早於生效日就適用;沒碰到計劃時看推送當天。不沿用情境題的 `_kt_sit_spec_since`:那是另一道閘的上線日。

## 範圍

1. **`lumos choice-points [--diff <範圍>] [--branch <名>]`**:唯讀,列出這次改到的行與每行挑中的壞法(定位、列號、成員、壞法、外層宣告),每行標帳上狀態(沒跑、殺掉 by `<測試>`(`<條款>`)、存活、已判、不唯一、跑不出結果、過期、沒有壞法、乾節點)。範圍沒給時照人裁 `--diff` 的規則(`_codeloop_disp_range`);目前分支就是主線而沒給 `--diff` → rc 2、說要給範圍。型錄缺檔 → 提醒、rc 0;表壞 → rc 2。
2. **`lumos choice-kill [--diff <範圍>] [--branch <名>] [--only <定位>] [--import "import …"]…`**(跑):對還沒有有效處置的壞法,依〈用詞〉殺掉判定批次跑、逐筆寫帳。
   - 跑之前:工作目錄除簿記檔外乾淨;守的測試至少一支——範圍沒碰到進行中計劃 → rc 2「沒規格就判不了」;碰到了但沒有可守的測試 → rc 2「計劃沒有可守的測試條款」;平台 `run_cmd` 沒有 `{method}` → rc 2;Android 檢查同人裁那一道。
   - 共用:`cmd_guard_kill` 多一個選用參數 `source`(不傳維持原行為),choice-kill 傳 `choice-kill`、配方 note 寫「改動選擇點」;收尾沿用人裁的兩段式訊號處理,包住整次呼叫加寫帳(第一個訊號 → 等這次殺傷力收尾、已有結果的壞法照記、rc 2;第二個 → 強制結束,印留下的工作樹路徑)。`_situation_rule_kill` 不改回傳形狀(既有測試不動)。
   - `--import`:壞法要補的 import(同前置計劃),只能配 `--only`。
   - 記:每個壞法一筆治理帳 gate `choice-kill`、kind `choice-kill`,欄位 `file`、`line_sha`、`old_sha`、`new_sha`、`member`、`row`(列號)、`verdict`、`killing_test`、`clauses`、`plans`、`test_blobs`、`reason`(no_result)、`via`(`run` 或 `situation-rule`)、`attempt`(同身分第幾筆)、`run_id`(這次呼叫的編號)、`token`;另在呼叫結束寫一筆 kind `run`(`run_id`、壞法數、行數、各 verdict 數、耗時秒數、`token`)。寫完印「下一步:提交治理帳(推送閘只讀被推送版本的帳)」。中斷時已有結果的照記、`run` 那筆照記(帶 `interrupted: true`)。
   - rc 取最大:全部有效處置 → 0;有存活 → 1;有 no_result、不唯一或中斷 → 2。存活按排版列出,每個附處置指令骨架。
   - 不寫計劃、不改程式。
   **`lumos choice-kill --judge <定位> --as equivalent|not-requirement|not-applicable --reason "<至少 10 實字>" [--consent …]`**(判):不跑測試、不套跑之前那串檢查;存活或 no_result 都能判;記 kind `judged`(欄位 `file`、`line_sha`、`old_sha`、`new_sha`、`member`、`row`、`as`、`reason`、`origin`、`consent`、`token`)。`not-applicable` 給「壞法不適用」(例:編不過、型別不合)。
3. **存活的處置**(人裁同意見〈用詞〉):
   - **規格沒寫** → `lumos situation-rule --point <定位> --plan … --clause … --test … [--consent …]`:situation-rule 多一條選擇點路徑。`--seg`/`--row`/`--file`/`--old`/`--new` 改成選用,跟 `--point` 互斥(入口驗證);選擇點路徑檢查「定位在目前範圍算得出壞法、old 在 HEAD 恰好一次」,`--old`/`--new` 由那個壞法帶入,不走情境段與觸發字的檢查。條款寫回、綁測試、跑殺傷力(要 killed)、記人裁事件照原本流程,事件另帶 `point` 欄(定位)與壞法身分;條款文字與測試跟計劃裡既有一條相同時不插第二條,改成對這個壞法跑殺傷力、killed 就把既有條款記給它(`_situation_rule_already` 對選擇點路徑改用壞法身分判冪等)。成功後另記一筆 `choice-kill` killed(`via: situation-rule`)。情境題人裁的統計(`_gov_situation_spec_counts`)不算帶 `point` 欄的事件。
   - **測試太弱** → 補測試或改綁後重跑 `choice-kill`(或 `--only <定位>`)。
   - **換了一樣/不是需求/壞法不適用** → `choice-kill --judge`。判 `not-requirement` 的不自動推廣;`gov --stats` 依 (列號、成員、外層宣告名) 列「乾節點候選」(同形狀被判 3 次以上),人決定要不要寫成〈乾節點規則〉新列(論文 3.1:回饋 → 人工加規則)。
   - **程式不該有這個選擇**(DO-178C)→ 改程式拿掉它;那一行沒有壞法就不再要求。
4. **推送前那一道**:在 `_spec_gate_push_check` 裡、`_spec_gate_push_scan` 之後另起一圈(沒有候選計劃也跑);擋下訊息跟預期值表缺簽合在同一次輸出(`_spec_gate_push_bad_head` 補新標籤)。
   - **接線**:`spec-gate --push-check` 新增選用參數 `--push-remote <遠端>` 與 `--pushed-ref <被推的 ref>`(同 `pitfalls` 那條),pre-push 掛鉤照 pitfalls 那行的寫法傳入;沒給時這一圈只用推送範圍本身。
   - **範圍**:B 取推送範圍右端(`A..B`、`A...B` 取 B,`A..` 取 HEAD,單一版本取它);主線照 `_push_mainlines`(跳過被推的那條)。被推的 ref 本身是主線 → 改到的行用推送範圍本身(`A..B`);否則用主線與 B 的分岔點..B;分岔點算不出 → 用推送範圍本身。B 取不到照既有算不出範圍放行規則。
   - **讀哪一版**:改到的檔用 `_kt_sit_read_many` 讀 B 版、治理帳用 `_gov_rows_at` 讀 B 版、碰到的計劃的條款與 `[test:]` 用 `git show B:<計劃路徑>` 讀後照規格閘的條款解析取(不讀工作目錄的 `env.notes`),同一輪按 (提交, 檔) 快取只讀一次;測試名是否存在照 B 版樹判。預期值表那圈照舊讀工作目錄(既有天花板,不在這份改)。不重跑 Gradle。
   - **預算與讀不到**:時限沿用 `_KT_SIT_BUDGET`;`_KtSitUnverifiable`(單檔超過上限、讀不到)或 `_KtSitOverBudget` → 擋,reason「算不出來」,訊息列哪支檔、建議 `--diff` 縮範圍(同情境題那道的處理);治理帳在 B 不存在 → 擋 reason「帳不在」;讀到但逾時或壞 → 擋 reason「帳讀不了」;兩種訊息分開。
   - **條件**:改到的行裡有 `.kt` 正式碼、至少一行有壞法、專案有 kotlin-junit 平台、生效日之後。
   - **判定**:對回報上限挑中的存活與全部 no_result、不唯一、過期、缺紀錄的行 → 擋,訊息按排版列出(定位、成員、壞法、缺什麼、指令);沒抽到的存活列最後一段不擋。範圍沒碰到任何進行中計劃 → 擋 reason「無規格」;碰到了但沒有可守的測試 → 不擋,印「這次的選擇點沒有測試守,只能人驗」(規格閘 `[manual:]` 小改動裁定)。紀錄的 `test_blobs` 跟 B 不同只提醒。
   - 擋下時記一筆 gate `choice-kill`、kind `blocked`(`reasons` 各帶點數、`token`、`hard: true`;同一個 B 同一組 reason 不重記)。
5. **登記與讀者**:`choice-kill` 加進 `_KNOWN_GATES`;`("choice-kill", k)`(k 為 `choice-kill`、`judged`、`run`、`blocked`)加進 `LOOP_NOT_CLOSE_EVENTS`(守衛不強制,照 situation-rule 先例);四種都進版控治理帳(推送閘要從 B 讀)。帳量:每筆只存雜湊與短欄位(不存 `old`/`new` 全文),實作量一筆的位元組數並保持在 `_gate_event_fit` 的上限內;`run` 那筆給 RETIRE-IF ②。`_gov_row` 對 `choice-kill` 取 `token` 並帶出 `verdict`、`row`、`attempt`、`reason`、`as`、`via`、`run_id`;`_GOV_FIELD_TYPES` 登記新欄位(`attempt`、耗時是 `(int,)`/`(int, float)`;`clauses`、`plans`、`reasons` 是清單;`test_blobs` 是物件);讀者自己用 `type(x) is int` 排除 bool。`--stats` 印:每次 choice-kill 的行數與耗時中位數(讀 `run`)、第一次跑(attempt 1)的殺掉率、存活後的處置分布(`via: situation-rule` 寫回規格、`via: run` 補測試後殺掉、各種 `as`)、編不過的 (列號, 壞法) 前 5、乾節點候選前 5、被擋筆數與「過期」占比。`_backing_kill_rows` 改成「`source` 非空就跳過」;`gov` 讀殺傷力帳本那支 loader 照舊不分來源;兩邊口徑寫進 Systems/guard-kill。
6. **型錄與文件**:Kotlin 型錄新增〈選擇點表〉〈乾節點規則〉與 `check.py` 的讀法與檢查(〈統計〉節若有手寫數字一併重數);Systems/kotlin規則包 補 WHY 行(兩節的用途與論文對應);Systems/規格閘、Systems/guard-kill 補 WHY 行;[[Projects/guard殺傷力驗證_計劃]] 補翻案決策(見〈舊否決比對〉);lumos-code-loop 手冊推送前那段補「選擇點沒處置會擋、在代碼審通過前跑 choice-kill 與處置(situation-rule 會改計劃)、帳要提交」;lumos-project-notes 指令索引補 `choice-points`、`choice-kill`、`situation-rule --point`;[[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 改成指向這份,只留 PIT 實驗紀錄當背景。

## 不做

- 不是每一行:乾節點不產生壞法;一行只一個壞法(論文 4.1)。
- 不引進 PIT 或其他外部變異工具(雜訊、商用過濾、零依賴)。
- 這一版不做論文 4.2–4.5 的依歷史排序與語法樹相似度;不接覆蓋率;不收數字常數、字串常數、`when` 分支刪除;REVISIT 看數字再加。
- 不讓 AI 自動判等價;判「不是需求」不自動推廣,乾節點規則人工增補(論文 3.1)。
- 推送前不重跑殺傷力(Gradle 可能十幾分鐘);只讀帳、重算壞法、驗新鮮度。
- 不管非 Kotlin 專案;測試檔、測試輔助資料夾、`.kts` 不算。
- 不做多個選擇點的組合(天花板 4)。

## 實務隱患

- 跑太久:一行一個壞法、同一平台同一計劃一次呼叫一棵工作樹、基準每條測試指令只跑一次、基準壞了整批 no_result 不重跑;只跑沒有有效處置的;每次呼叫記 `run` 給 RETIRE-IF ②。Android 新工作樹冷編譯仍貴,實作時量一次 20 行改動的實際耗時寫進報告。
- 噪音:乾節點規則(論文附錄 A 譯成 Kotlin)、單元測試分不出的寫法不收、API 成員只認呼叫形、回報上限檔數 × 7、只改縮排的行不算、測試輔助資料夾不算。
- 壞法編不過(型別不合、`!!.` 用在非空、SBR 刪到被用的值):no_result「壞法編不過」,人可判 `not-applicable`;同形累計進 `--stats` 給人改表。
- 判定被敷衍(大量判不是需求、寫一支什麼都殺的測試):判定必帶理由與同意、`--stats` 列處置分布;單一測試殺掉的壞法分布在 3 支以上不同檔時,`--stats` 列出那支測試提醒人看。
- 殺掉它的測試後來被換弱:紀錄要求 `killing_test` 還在守的測試裡;測試本體改過只提醒。
- 實作改了、紀錄過期:身分含那一行與 `old` 的雜湊,行變了就是新壞法。
- 帳量:版控治理帳已約 22MB;每筆只存雜湊,`run` 每次一筆;實作量一筆大小寫進報告。
- 帳沒提交就推:choice-kill 與 judge 結尾都印「提交治理帳」;推送閘從 B 讀,沒提交就是缺紀錄,訊息附「記得提交帳」。
- 跟代碼審的先後:situation-rule 會改計劃,所以 choice-kill 與處置在 `code-loop pass` 之前做;之後只有帳本提交(choice-kill 與 judge 只寫帳,可在通過後補)。
- 跟情境題那道重疊(同一行既是情境決策表觸發字又是選擇點):兩道各管各的(一道問「答案引規格」,一道問「壞法有測試殺」),人裁事件以 `point` 欄分開統計;重複跑 Gradle 的代價承認,天花板 6。
- 併發與交易:已排除:單人單機依序操作,沿用 guard kill 的隔離工作樹與人裁的訊號收尾;治理帳逐筆追加。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 只對改動的行、每行一個壞法、運算子隨機排序取第一個產得出的 | 論文 2.2、4.1 節 Listing 2 | https://arxiv.org/pdf/2102.11378 |
| 五個運算子 AOR/LCR/ROR/UOI/SBR 與各自的壞法 | 論文表 1 | https://arxiv.org/pdf/2102.11378 |
| 乾節點不產生壞法、規則由人照回饋手動增補 | 論文 3.1 節、附錄 A(有用比例 15% 到 89%) | https://arxiv.org/pdf/2102.11378 |
| 乾節點規則第一版內容(log、斷言、時間、監控、容量、樣板方法、flush/close、依賴注入) | 論文附錄 A.1、A.3 | https://arxiv.org/pdf/2102.11378 |
| `==` 只換 `!=`、`!=` 只換 `==` | 論文附錄 A.1.23 | https://arxiv.org/pdf/2102.11378 |
| 不可刪的節點(宣告、參數、非 Unit 唯一陳述) | 論文附錄 A.1.12 | https://arxiv.org/pdf/2102.11378 |
| 回報上限檔數 × 7、從存活隨機挑 | 論文 2.3 節 | https://arxiv.org/pdf/2102.11378 |
| 同一壞法每次穩定回報(固定種子) | 論文 3.2.4 節 | https://arxiv.org/pdf/2102.11378 |
| 一次產生、批次執行 | 論文 2.3 節 | https://arxiv.org/pdf/2102.11378 |
| 編不過的壞法要有規則擋 | 論文 3.2.1 節 | https://arxiv.org/pdf/2102.11378 |
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
| 沒碰到計劃照擋 | 使用者裁定 | 使用者 2026-11-13:「照擋,沒規格就無法判定當前需要援引的語法需求來源」 |

## 驗收條款

- [S1] 當改動行含選擇點表成員,choice-points 應 每行最多挑一個壞法,乾節點、import 行、註解與字串、只改縮排的行、測試檔與測試輔助資料夾、`.kts` 不挑 [test:t_choice_points_scan]
- [S2] 當運算子出現在泛型、`->`、`..`、`?:`、`!!`、`!in`、`!=`、反引號識別字裡,或 API 成員不是呼叫形,choice-points 應 不把它當選擇點;運算子在行尾換行時 應 照算 [test:t_choice_points_operator_edges]
- [S3] 當同一行內容不變而重跑,choice-points 應 挑出同一個壞法;那一行不唯一時 應 往外帶行求唯一,仍不唯一標不唯一 [test:t_choice_points_stable]
- [S4] 當一行命中乾節點規則或在乾的函式本體裡,choice-points 應 不在那一行產生壞法 [test:t_choice_points_arid]
- [S5] 當同一平台同一計劃有多個壞法,choice-kill 應 只呼叫一次殺傷力、每條測試指令基準只跑一次,並依 recipe_id 把結果對回每個壞法與測試 [test:t_choice_kill_batch]
- [S6] 當某壞法有一支守的測試強 killed,choice-kill 應 記 killed、帶條款順序第一支殺掉它的測試與條款;全部 survived 應 記 survived 並回 1 [test:t_choice_kill_verdicts]
- [S7] 當沒有強 killed 而有一支判弱證據、drifted、error 或壞法編不過,choice-kill 應 記 no_result 帶原因並回 2;基準 abort 時 應 讓用到它的壞法全部 no_result、不重跑 [test:t_choice_kill_no_result]
- [S8] 當工作目錄不乾淨、範圍沒碰到進行中計劃、計劃沒有可守的測試、run_cmd 沒有 {method}、或 --import 沒配 --only,choice-kill 應 回 2 不跑 [test:t_choice_kill_rejects]
- [S9] 當同身分已有有效處置,choice-kill 應 跳過那個壞法;每次呼叫 應 記一筆 run 帶行數、壞法數與耗時 [test:t_choice_kill_incremental]
- [S10] 當 choice-kill --judge 帶 as、理由與同意,choice-kill 應 記一筆 judged,推送前那一道 應 視那一行已處置;理由不到 10 實字 應 回 2 [test:t_choice_kill_judge]
- [S11] 當 situation-rule 帶 --point 而寫回成功,situation-rule 應 用那個壞法跑殺傷力、記人裁事件帶 point 欄並另記 choice-kill killed;條款文字與測試已存在時 應 不插第二條而把既有條款記給這個壞法 [test:t_situation_rule_point]
- [S12] 當推送範圍有壞法沒有有效處置(缺、survived 被抽中、no_result、不唯一、過期),推送前那一道 應 擋下、按排版列出並記 blocked [test:t_spec_gate_push_choice]
- [S13] 當存活超過檔數乘 7,推送前那一道 應 只對用 B 當種子抽中的那些擋、其餘列在沒抽到一段 [test:t_spec_gate_push_choice_cap]
- [S14] 當推送範圍有選擇點但沒碰到任何進行中計劃,推送前那一道 應 擋下 reason 無規格;碰到的計劃沒有可守的測試時 應 只提醒不擋 [test:t_spec_gate_push_choice_no_plan]
- [S15] 當推送的是功能分支,推送前那一道 應 用主線與 B 的分岔點..B 算改到的行;推的是主線本身時 應 用推送範圍本身 [test:t_spec_gate_push_choice_range]
- [S16] 當推送範圍是 `A..B` 而工作目錄比 B 多一個沒處置的選擇點或計劃條款不同,推送前那一道 應 只看 B 版本的檔、計劃與帳 [test:t_spec_gate_push_choice_pushed_version]
- [S17] 當掃描超過時限或檔讀不了、或 B 版治理帳不在或讀不了,推送前那一道 應 擋下並用各自的 reason 與訊息 [test:t_spec_gate_push_choice_unverifiable]
- [S18] 當計劃日期早於生效日、專案沒有 kotlin-junit 平台、或改到的行沒有壞法,推送前那一道 應 不要求 [test:t_choice_exemptions]
- [S19] 當治理帳有 choice-kill 事件,gov --stats 應 印每次呼叫的行數與耗時中位數、第一次跑殺掉率、存活處置分布、編不過前 5、乾節點候選前 5、被擋筆數與過期占比 [test:t_gov_stats_choice_kill]
- [S20] 當型錄缺檔,choice-points 與推送前那一道 應 只提醒不擋;型錄在但缺〈選擇點表〉或〈乾節點規則〉或表壞 應 擋並指出哪一列 [test:t_choice_table_missing]
- [S21] 當在測試品質實驗室 Android 副本把搜尋 ViewModel 的 `flatMapLatest` 那一行改動推送、綁的測試只送一次值,choice-kill 應 判那一行 survived;換回送兩次值的測試 應 判 killed [manual:在實驗副本跑 lumos choice-kill,先用只送一次值的 onlyLatestQueryShown 看 survived,再換回原測試看 killed]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 改動行 `.flatMapLatest { repo.search(it) }` | 一個壞法 flatMapConcat(API) | 〈用詞〉選擇點表 API 列 |
| S1 | 改動行 `if (count > limit && enabled)` | 只挑一個壞法(`>` 或 `&&` 的其中一個候選) | 論文 4.1 一行一個 |
| S1 | 改動行 `Log.d(TAG, "q=$q")` | 沒有壞法(乾節點) | 論文附錄 A.1.1 log |
| S1 | 改動行 `require(x > 0)` | 沒有壞法 | 論文附錄 A.1.5 斷言 |
| S1 | 改動行 `import kotlinx.coroutines.flow.flatMapLatest` | 沒有壞法 | 〈用詞〉排除 import |
| S1 | 改動行 `// flatMapLatest here` 與 `"a < b"` | 沒有壞法 | 〈用詞〉剝註解與字串 |
| S1 | 改動在 `app/src/androidTest/…/FooTest.kt` 與 `app/src/testFixtures/…/Fake.kt` 含 `.filter {` | 沒有壞法 | 〈用詞〉改到的行測試判法 |
| S1 | 改動在 `app/build.gradle.kts` 含 `a > b` | 沒有壞法 | 〈用詞〉只收 .kt |
| S1 | 把 10 行包進 `withContext(io) { … }` 只改縮排 | 那 10 行不挑 | 〈用詞〉改到的行沿用 _kt_sit_hits |
| S1 | 檔首有 BOM、第一行 `package com.app.filter` | 沒有壞法 | 〈用詞〉選擇點先剝 BOM |
| S2 | `val m: Map<String, List<Int>>`、`x?.let { it }`、`a!!`、`x !in s`、`0..n` | 沒有選擇點 | 〈用詞〉運算子邊界 |
| S2 | `pair.first`、`padding(all = 8.dp)`、`val filter = 1` | 沒有選擇點(不是呼叫形) | 〈用詞〉API 只認呼叫形 |
| S2 | `if (a > 0 &&` 換行 `    b < 3)` | 行尾 `&&` 算選擇點 | 〈用詞〉空白含換行 |
| S2 | `` fun `a > b`() = x `` | 沒有選擇點 | 〈用詞〉反引號識別字不算 |
| S2 | `val s = "x ${a < b}"` | `<` 算選擇點 | 〈用詞〉字串樣板裡的程式碼照算 |
| S3 | 同一行跑兩次 choice-points | 兩次挑同一個壞法 | 論文 3.2.4 穩定回報 |
| S3 | 兩行完全相同、前後各兩行也相同 | 標不唯一、不跑 | 〈用詞〉壞法身分 |
| S3 | 那一行是另一行的子字串、多帶上一行就唯一 | old 是兩行 | 〈用詞〉往外帶行 |
| S4 | `override fun toString() = "a" + b` | 沒有壞法 | 論文附錄 A.1.21 樣板方法 |
| S4 | `delay(500)`、`withTimeout(3_000) {` | 沒有壞法 | 論文附錄 A.1.4 時間 |
| S4 | `@Module` 類別裡的 `@Provides` 函式本體 | 沒有壞法 | 論文附錄 A.3.2 依賴注入 |
| S5 | 假平台:3 個壞法、守的測試 t_a、t_b(run_cmd 帶 {method}) | 一次殺傷力呼叫、基準 t_a 與 t_b 各一次、6 個配方的結果各自對回 | 論文 2.3 批次執行 |
| S5 | 守的測試 t_k 在非預設平台 | t_k 的配方帶它的平台、在它的平台根跑 | 〈用詞〉殺掉判定 platform 欄 |
| S6 | 假平台:t_a 紅、t_b 綠 | killed、killing_test t_a、clauses 是綁 t_a 的條款 | 〈用詞〉殺掉判定 |
| S6 | 假平台:t_a 弱證據、t_b killed | killed、killing_test t_b | 〈用詞〉任一支強 killed |
| S6 | 假平台:t_a、t_b 都綠 | survived、rc 1、印處置指令 | 〈範圍〉2 rc |
| S7 | 假平台:換完印 `e: Type mismatch`、沒有測試名 | no_result、reason 壞法編不過、rc 2 | 〈用詞〉編不過的形狀 |
| S7 | 假平台:t_a 的基準就紅、3 個壞法都用 t_a | 3 個都 no_result(abort)、基準只跑一次 | 〈用詞〉基準 abort 不重跑 |
| S7 | 一個壞法 survived、另一個 no_result | rc 2(取最大) | 〈範圍〉2 rc 取最大 |
| S8 | 計劃檔有未提交改動 | rc 2、沒跑 | 〈範圍〉2 跑之前的檢查 |
| S8 | 範圍碰不到進行中計劃 | rc 2、說沒規格判不了 | 〈範圍〉2 跑之前的檢查 |
| S8 | 碰到的計劃條款全是 `[manual:]` | rc 2、說沒有可守的測試條款 | 〈範圍〉2 跑之前的檢查 |
| S8 | run_cmd `./gradlew test`(沒有 {method}) | rc 2 | 〈用詞〉守的測試 run_cmd 要含 {method} |
| S8 | `--import` 沒帶 `--only` | rc 2 | 〈範圍〉2 --import 只能配 --only |
| S9 | 第一次 3 個壞法全 killed,再跑一次 | 3 個都跳過、不呼叫殺傷力、記一筆 run(壞法數 0) | 〈實務隱患〉只跑沒處置的 |
| S9 | 其中一行被改了 | 只跑那一行的新壞法 | 〈用詞〉壞法身分含那一行雜湊 |
| S10 | `--judge app/…/Vm.kt:12 --as not-applicable --reason "型別不合換了編不過不是需求" --consent "這個不適用"` | 記 judged、origin ai、consent 是原話;推送不擋那一行 | 〈範圍〉2 判 |
| S10 | `--reason "等價"`(不到 10 實字) | rc 2 | 〈範圍〉2 判理由 |
| S10 | 對 no_result 的那一行 `--judge --as not-applicable` | 記 judged、那一行算已處置 | 〈範圍〉2 存活或 no_result 都能判 |
| S11 | survived 那一行跑 `situation-rule --point app/…/Vm.kt:12 …`,新條款綁的測試在壞法下紅 | 條款寫回、人裁事件帶 point、另記 choice-kill killed(via situation-rule) | 〈範圍〉3 規格沒寫 |
| S11 | 同一段條款文字與同一支測試,先後給兩個不同的 `--point` | 只有一條條款;兩個壞法各記 killed | 〈範圍〉3 既有條款記給新壞法 |
| S11 | `--point` 與 `--seg` 一起給 | rc 2 | 〈範圍〉3 來源互斥 |
| S11 | 帳上有帶 point 的人裁事件 | `_gov_situation_spec_counts` 不算它 | 〈範圍〉3 統計分開 |
| S12 | 一行沒紀錄 | 擋、列出那一行與 `lumos choice-kill` | 〈範圍〉4 判定 |
| S12 | 一行 killed by t_strong,條款現在綁 t_weak | 擋、reason 過期 | 〈用詞〉過期 |
| S12 | 所有行 killed 或 judged | 不擋 | 〈用詞〉有效處置 |
| S12 | killed 那筆的 test_blobs 跟 B 不同 | 不擋、提醒建議重跑 | 〈範圍〉4 判定 |
| S12 | 同時預期值表缺簽 | 兩件一起列在同一次擋下 | 〈範圍〉4 同一次輸出 |
| S13 | 改 2 支 .kt、存活 20 個 | 用 B 當種子抽 14 個擋、6 個列在沒抽到 | 論文 2.3 回報上限 |
| S13 | 同一個 B 推兩次 | 兩次抽到同一批 | 〈用詞〉回報上限固定種子 |
| S14 | 改了 Kotlin 選擇點、範圍沒碰任何進行中計劃 | 擋、reason 無規格 | 使用者 2026-11-13 裁:沒規格就照擋 |
| S14 | 碰到的計劃條款全是 `[manual:]` | 不擋、印只能人驗 | 規格閘 manual 小改動裁定 |
| S15 | 推功能分支,遠端主線在 M、分岔點 F | 改到的行用 F..B | 〈範圍〉4 範圍 |
| S15 | 推 main 本身(被推的 ref 是主線) | 改到的行用推送範圍 A..B | 〈範圍〉4 範圍 |
| S16 | 推 `A..B`,工作目錄比 B 多一個沒紀錄的選擇點 | 不擋(只看 B) | 〈範圍〉4 讀哪一版 |
| S16 | 工作目錄的計劃比 B 多綁一支測試 | 守的測試照 B 版計劃算 | 〈範圍〉4 讀哪一版 |
| S17 | B 版有一支超過讀檔上限的 .kt 在範圍裡 | 擋、reason 算不出來、列那支檔 | 〈範圍〉4 預算與讀不到 |
| S17 | B 版沒有治理帳檔 | 擋、reason 帳不在 | 〈範圍〉4 預算與讀不到 |
| S18 | 計劃日期早於生效日 | 不要求 | 〈用詞〉生效日 |
| S18 | 專案只有 python 平台 | 不要求 | 〈範圍〉4 條件 |
| S18 | 改動只有 log 與 import | 不要求 | 〈範圍〉4 條件 |
| S19 | 帳上 run 兩筆(行數 10、30,耗時 60、180 秒);attempt 1 的 killed 3、survived 1、no_result 1;via situation-rule 的 killed 1(attempt 2);judged not-applicable 1;blocked 4 筆其中過期 1 | 行數中位數 20、耗時中位數 120 秒;第一次跑殺掉率 3/5;存活處置寫回規格 1、判不適用 1;被擋 4(過期 1/4) | 〈範圍〉5 RETIRE-IF 的數 |
| S20 | 型錄檔不在 | choice-points 提醒 rc 0;推送不擋、印提醒 | 〈用詞〉讀表缺檔只提醒 |
| S20 | 型錄在但沒有〈乾節點規則〉節 | 擋、說缺哪一節 | 〈用詞〉讀表缺節要擋 |
| S20 | 〈選擇點表〉有一列候選壞法空白 | 擋、指出那一列 | 〈用詞〉讀表表壞要擋 |
| S21 | 實驗副本只送一次值的測試 | survived;換回原測試 killed | 使用者 2026-11-13 面試題 |

## 回退

- 整個關掉:`_CHOICE_SINCE` 設成很遠的未來日期,推送那一道不要求;`choice-points`、`choice-kill` 照留、只是沒人需要。
- 單一列誤報多:從〈選擇點表〉拿掉那一列,或在〈乾節點規則〉加一列(下一次推送就不再算)。
- `cmd_guard_kill` 的 `source`、situation-rule 的 `--point`、`spec-gate --push-check` 的 `--push-remote`/`--pushed-ref` 都是選用,不傳維持原行為。

## 天花板

1. 只證「選擇點表列到的寫法有測試守著」;表沒列到的選擇(數字常數、`when` 分支、整段邏輯)這一版不管;表與乾節點規則列得好不好決定上限(論文也承認規則依環境調)。
2. 論文用語法樹判節點,這裡用剝註解字串後的文字比對加呼叫形與兩側空白近似;不照格式寫的運算子會漏、多行呼叫鏈的 SBR 不做、乾節點只認型錄寫的形狀。
3. 論文只變異有覆蓋的行,這裡沒有覆蓋率:沒被守的測試跑到的行一定存活,要人處置(可判 not-requirement 或補測試);REVISIT 看要不要接 JaCoCo。
4. 一行一個壞法、不做組合;同一行其他選擇點這次沒被挑到就不驗(論文的取捨)。
5. 殺掉只證「換成那個壞法時有測試紅」,不證測試紅的理由就是那條需求;條款跟選擇點是不是講同一件事靠人裁與代碼審。
6. 推送前不重跑,信帳;帳是作者自己跑出來的,同代碼審留痕的天花板。跟情境題那道對同一行可能各跑一次 Gradle。
7. 回報上限之外的存活不擋;同一批存活要到 B 變了才可能抽到別的。
8. 判「不是需求」全靠人;判錯會放過規格缺口,乾節點規則寫錯會整類放過。

## 審計修正紀錄

- r1(2026-11-13,6 席,前一版「條款近似錯誤寫法要殺得掉」):52 條/blocking 24/方向改了。席報告在 governance/review-reports/條款近似錯誤寫法要殺得掉/。
- r1 收斂後複審(同日,3 席,不記帳):28 條/blocking 8。報告在同目錄。
- 方向重定(2026-11-13,使用者):整份改寫成「改動選擇點全數產生壞法、存活交人裁」。
- 前掃(2026-11-13,preflight-4):25 條,都修進真檔;逐條在 governance/review-reports/改動選擇點都要有需求守住/r1-intake.md。
- r1(2026-11-13,6 席):53 條/blocking 22/核心設計站得住,機制層大改——每點一次殺傷力改成同平台同計劃一次批次、壞法編不過有出口(not-applicable)、選擇點只認呼叫形與運算子邊界、推送閘接 --pushed-ref 與 B 版計劃、帳只存雜湊;同時照使用者「照論文實作」對齊 Google 論文:一行一個壞法、五個運算子加 SBR、乾節點規則人工增補、回報上限檔數 × 7、固定種子穩定回報;撤掉需求脈絡組與樣式自動推廣。席報告與分組在 governance/review-reports/改動選擇點都要有需求守住/。
- r1 方向由使用者 2026-11-13 裁:「那就照那份論文來實作」「有什麼問題,優先參考」。
