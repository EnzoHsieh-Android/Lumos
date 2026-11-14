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
related:
  - "[[Projects/雙向追溯_需求與語法選擇點互證_計劃]]"
  - "[[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]]"
---
# 改動選擇點都要有需求守住_計劃

## 白話

改動裡每一個「換一種寫法照樣編得過、行為卻不同」的地方(選擇點),都是寫的人做了一個決定,背後一定有一條需求。這份計劃讓工具自己從改動裡找出全部選擇點,每一點換成表上的另一種寫法(壞法)跑條款綁的測試:
- 測試紅了(殺掉) → 記下是哪條條款守住這個選擇;
- 測試沒紅(存活) → 這個選擇沒有需求守著:規格沒寫、測試太弱、或換了其實一樣 → 推送前擋下交人裁;人裁寫回規格並綁一支會紅的測試,或判「換了一樣/不是需求」留帳。

不是每一行:import、log、純轉接、傳參數沒有「換了行為就不同」的替代寫法,不算選擇點、不產生壞法。哪些寫法算選擇點,由 Kotlin 型錄新增的〈選擇點表〉窮舉。

這份把 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 的正向(條款的測試分不分得出對錯)與反向(程式的選擇有沒有需求撐腰)併成同一個機制:殺掉的那一點是正向的證據,存活的那一點就是反向要找的「沒有出處的選擇」。

大方向(使用者 2026-11-13):「改動中的語法,必定是代表一種需求,而這個需求,必須引得出規格……語法是可以被窮舉的,也就代表 code review 是可以被機械層檢查」;「我想涵蓋的就是所有開發需求中的程式碼,不是特定哪一種類別的語法」;範圍是選擇點、不是每一行(同日對話確認)。

PRIOR-ART: Google 的差異式變異測試只對改動且有覆蓋的行產生變異、每行一個、依語言把 log 這類「乾行」(arid)壓掉、工程師按「沒用」再壓同類,存活的變異在代碼審顯示,每次改動存活中位數 2 個(https://arxiv.org/pdf/2102.11378、https://research.google/pubs/state-of-mutation-testing-at-google/);少數幾種運算子(關係、邏輯、算術、單元插入)就能達到接近全部運算子的效果(Offutt 等 1996 的五個充分運算子,https://dblp1.uni-trier.de/rec/journals/tosem/OffuttLRUZ96.html;Just 等 非冗餘變異,https://homes.cs.washington.edu/~rjust/publ/non_redundant_mutants_icst_2012.pdf);MutApi 把 API 誤用寫成改寫運算子(https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843),Mutant-Kraken 有 Kotlin 專用的 `any`/`all`/`none` 互換(https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin);存活的變異可能是規格缺口而不只是測試缺口,MutDafny 從存活變異找出 5 處規格弱點(https://arxiv.org/pdf/2511.15403);DO-178C 要求程式每一段追溯得到需求,追不到的是「非預期功能」,處置是補需求或刪程式(https://ldra.com/ldra-blog/do-178c-structural-coverage-analysis/);等價變異 AI 判讀 Meta ACH 量到加前處理 precision 0.95、recall 0.96(https://arxiv.org/html/2501.12862)。採用:只看改動、每點一個壞法、乾行不算(Google);運算子取充分集合(Offutt/Just);API 兄弟寫法照 MutApi 寫成表;存活三分(測試缺、規格缺、等價)交人裁;規格缺的處置照 DO-178C(補需求或刪程式)。不採:PIT——在 Kotlin 協程上產生大量無用變異(https://lightrun.com/answers/hcoles-pitest-pitest-generates-unhelpful-mutations-when-using-kotlins-coroutines;2026-11-13 實驗副本 37 個變異體裡落在手寫邏輯的只有一兩個),官方建議的過濾外掛 Arcmutate 是商用授權(https://central.sonatype.com/artifact/com.arcmutate/pitest-kotlin-plugin),也沒有 API 兄弟寫法;這一版不讓 AI 自動判等價(見〈不做〉)。
RETIRE-IF: 上線兩個月,看 `gov --stats` 的選擇點數字:①存活裡被人判「等價或不是需求」的超過八成(選擇點表誤報多過真報),或②每次推送前要補跑的選擇點中位數讓殺傷力總耗時超過十分鐘,或③推送被擋的筆數裡超過一半是「過期」(新鮮度判法太脆)——就把推送那一道降成只提醒,回頭縮表或改判法。
REVISIT:2027-01-15 讀 gov --stats 的選擇點數字(殺掉率、存活三分的比例、每次推送補跑點數與耗時),決定要不要加數字常數(逾時 5 秒對 30 秒)這類選擇點、要不要讓 AI 先判等價

## 舊否決比對

- [[Projects/guard殺傷力驗證_計劃]] 決策 d1「合約殺傷力驗證不自動產生變異」,理由是等價變異不可判定、誤報、零依賴:這份只用〈選擇點表〉窮舉的互換,不是任意運算子;等價由人判而且留帳(判過的同一點不再問);零依賴照守(不引進 PIT)。d1 管的是合約的殺傷力配方,這份管的是改動的選擇點,沒有翻 d1;但「自動產生壞法」這件事本身換了答案,理由寫在 PRIOR-ART。
- [[Projects/高風險測試證據加嚴_計劃]] 第二批「CI 對改到的行跑變異測試」:那份打算接外部工具,排在 2026-12-15 回頭看;這份不碰外部工具。回頭看時改讀這份的帳。
- [[Systems/guard-kill]] 否決「另抽一支共用的殺傷力函式」:這份沿用 `cmd_guard_kill` 的 `recipes_override`,外層把人裁的 `_situation_rule_kill` 參數化共用,不另抽。
- 本計劃前一版(2026-11-13 設計審 r1,當時叫「條款近似錯誤寫法要殺得掉」)讓條款自己宣告 `[near:]` 要換的寫法:只管被點名的一兩個寫法,沒點名的選擇點沒人管,跟大方向不合,整個換掉;卷證留在 governance/review-reports/條款近似錯誤寫法要殺得掉/。

## 用詞

- **前置**:[[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]](2026-11-13 已合進主線):補 import 的 `--import` 與 `also`、失敗摘錄、Android run_cmd 檢查、殺傷力在平台根跑,都來自那份。
- **選擇點表**:Kotlin 型錄(`skills/kotlin-idioms/checks-catalog.md`)新增一節〈選擇點表〉,每列一組:組號(`C-<n>`)、種類(只填 `換寫法`、`換運算子`、`拿掉呼叫` 三種之一)、成員、每個成員的壞法(只一個)、為什麼行為不同、出處。只收換了照樣編得過、行為不同的寫法;行為相同的(例 `mapLatest` 與 `transformLatest`)不收。第一版(下面的小標題只是分類說明,不是種類;空值與集合、協程互換的種類是 `換寫法`):
  - 運算子(換運算子):`<`→`<=`、`<=`→`<`、`>`→`>=`、`>=`→`>`、`==`→`!=`、`!=`→`==`、`&&`→`||`、`||`→`&&`、`+`→`-`、`-`→`+`;拿掉前置 `!`。
  - 空值(換寫法):`?.`→`!!.`。
  - 集合(換寫法):`filter`↔`filterNot`、`any`→`none`、`all`→`any`、`none`→`any`、`first`↔`last`、`firstOrNull`↔`lastOrNull`、`sortedBy`↔`sortedByDescending`、`take`↔`takeLast`、`drop`↔`dropLast`、`minByOrNull`↔`maxByOrNull`。
  - 協程與 Flow(換寫法):`flatMapLatest`→`flatMapConcat`、`flatMapConcat`→`flatMapMerge`、`flatMapMerge`→`flatMapConcat`、`collectLatest`↔`collect`、`coroutineScope`↔`supervisorScope`、`Dispatchers.IO`↔`Dispatchers.Default`、`SharingStarted.Eagerly`↔`SharingStarted.Lazily`。
  - 拿掉呼叫:`.distinctUntilChanged()`、`.flowOn(…)`、`.conflate()`、`.buffer(…)`,只收整個呼叫(含括號)在同一行、括號成對的。
  型錄照 `_kt_catalog_path()` 讀(工具鏈來源那份,不隨被推送版本變;測試用 `LUMOS_KT_CATALOG`),跟情境決策表同一支 `_kt_decision_table` 的檔、新增一份解析。**缺檔**(照 `_kt_catalog_missing` 判:型錄不存在)只提醒不擋;**檔在但讀不了或表壞**(缺欄、組號重複、壞法不在成員的寫法範圍)擋,指出哪一列。
- **選擇點**:改到的行(見〈範圍〉4 的範圍)裡,副檔名 `.kt` 的 Kotlin 正式碼檔(`.kts` 建置腳本不算;不是測試檔 `_nodehome_is_test`;在 kotlin-junit 平台根底下)上,先用情境題剝註解與字串那支 `_strip_c_comments(..., blank_strings=True, kotlin=True, keep_length=True)` 得到等長文字(位置一對一,字串樣板 `${…}` 裡的程式碼保留),排除 `import`/`package` 行之後,選擇點表成員的每一次出現;位置在等長文字上找,`old` 從原文取。識別字成員照整字比對(同 `_kt_trigger_re` 的邊界);運算子成員只認兩側都有空白的(`a < b`;`List<String>` 的角括號、`a!!`、`!=` 裡的 `!` 不算);拿掉前置 `!` 只認 `!` 後面緊接識別字或左括號。同一行多個成員就是多個選擇點。
- **定位**:`<檔>:<行>#<n>`,n 是那一行由左到右第幾個選擇點(從 1 起;那一行只有一點時 `#1` 可省)。所有指令(`--only`、`--point`、`--judge`、`--split`)與報告都用這個。
- **選擇點身分**:檔(repo 根相對路徑)、`old`、`new`。`old` 從那一行起算(含縮排與換行),整支檔不是恰好出現一次時依序往上、往下各多帶一行,最多前後各 2 行;還不唯一就這一點標「不唯一」、不跑,列在報告與推送訊息裡要人改寫或判。`new` 是 `old` 裡那一次出現換成壞法。換行照 guard kill 的讀法統一成 `\n`。`old` 超過 500 字同樣標不唯一處理。
- **進行中計劃**:status 是 doing,或這次推送改到計劃檔本身而 status 是 done(同預期值表那道的 `_live` 語意;實作時把 `_spec_gate_push_scan` 裡的 `_live` 抽成頂層函式共用,語意不變)。
- **守的測試**:範圍碰到的進行中計劃裡,條款 `[test:]` 綁的測試,扣掉 `[manual:]` 與 `[keeps]` 的條款;平台照 `resolve_test_refs`/`_split_test_ref_ex` 取,只留平台 profile 是 kotlin-junit 的。每支測試記它的平台,臨時配方帶 `platform` 欄(不是預設平台時也跑對地方)。
- **殺掉判定**:一個選擇點只呼叫一次 `cmd_guard_kill`,把它全部守的測試當 `recipes_override` 一次丟進去(同一支測試指令的基準只跑一次);從 `result_out` 的列讀:有任一支判 `killed` 而且 `weak` 為否 → **killed**,`killing_test` 取條款順序第一支這樣的測試,`clauses` 是綁它的條款;否則有任一支是 `killed_unattributed`、`timed_out_weak`、弱證據、abort、drifted、error → **no_result**(記第一個原因與失敗摘錄);其餘全部 `survived` → **survived**。
- **有效處置**:帳上同身分最新一筆是 `killed` 而且那筆的 `killing_test` 還在現在守的測試裡;或有同身分的 `judged`;或它的樣式被推定不是需求。最新一筆是 `survived`、`no_result` 不算,重跑會再跑。
- **過期**:帳上同身分最新一筆是 `killed`,但那筆的 `killing_test` 已不在現在守的測試裡。
- **乾行**:不含任何選擇點的改動行;不產生壞法、不要求任何東西。
- **需求脈絡組**:存活的選擇點按「同一個外層函式(往上找最近的 `fun` 宣告,沿用情境題切段找函式邊界那支)而且守的測試集合相同」分組;頂層(不在函式裡)的點按檔分組。組號是 `<檔>::<函式名>`(同檔同名的多載加 `#<第幾個>`)。一組是一題:問的是「這幾個選擇合起來在滿足哪一條需求」,不是逐點問。分組是近似,人可以用 `--split` 把一點拆成單獨一組(記帳)。
- **樣式**:一個選擇點的 (組號 `C-<n>`、成員、外層函式名) 三元組;外層函式名照寫,頂層寫 `<top>`。人判過「不是需求」的點,它的樣式記進帳;之後同樣式的新選擇點自動標「推定不是需求」:報告另列、推送不擋。人可以 `--unsuppress <樣式>` 撤回(記帳),撤回之後同樣式回到要處置。判「等價」的不推廣到同樣式(等價跟上下文有關)。
- **人裁同意**:照人裁那套 `_waive_origin_tty`:終端答 y 記 `origin: human`;沒有終端要 `--consent` 使用者原話,記 `origin: ai`、`consent` 必填非空白。
- **生效日**:常數 `_CHOICE_SINCE`(YYYY-MM-DD,合進主線的隔天),環境變數 `LUMOS_CHOICE_SINCE` 供測試覆寫;測試總檔比照 `LUMOS_HIGH_RISK_EVIDENCE_SINCE` 預設 9999-12-31。適用的計劃是計劃日期(`_plan_effective_day(..., scope="note")`)不早於生效日的。

## 範圍

1. **`lumos choice-points [--diff <範圍>] [--branch <名>]`**:唯讀,列出這次改動的選擇點(定位、成員、組號、壞法、身分的 `old` 前 60 字),每點標它在帳上的狀態(沒跑、殺掉 by `<測試>`(`<條款>`)、存活、已判、推定不是需求、不唯一、跑不出結果、過期)。最後一行統計。範圍沒給時照人裁的 `--diff` 規則算(`_codeloop_disp_range`:找得到主線分岔點就用分岔點..HEAD)。型錄缺檔 → 印提醒、rc 0、不列;表壞 → rc 2。
2. **`lumos choice-kill [--diff <範圍>] [--branch <名>] [--only <定位>] [--import "import …"]… [--draft]`**(跑):對還沒有有效處置的選擇點逐一跑殺掉判定(每點一個壞法、每點一次殺傷力呼叫),寫治理帳。
   - 跑之前:工作目錄除簿記檔外乾淨;守的測試至少一支,沒有 → rc 2,範圍沒碰到進行中計劃時說「沒規格就判不了」,碰到了但條款都沒綁 kotlin-junit 測試時說「計劃沒有可守的測試條款:補一條綁測試的條款,或逐點 --judge」;每個用到的平台有 `run_cmd`(Android 檢查同人裁那一道)。
   - 共用:人裁的 `_situation_rule_kill` 改成只回 (結果列或 None, 狀態 `ok`/`interrupted`/`no_rows`),killed/survived/no_result 與各自訊息由呼叫端判(人裁自己的拒絕訊息搬回 `cmd_situation_rule`,行為不變);保留 Ctrl-C/SIGTERM/SIGHUP 兩段式收尾、基準耗時提示、失敗摘錄;配方的 note 與 `cmd_guard_kill` 新的選用參數 `source` 由呼叫端給(不傳維持原行為)。
   - `--import`:壞法要補的 import(同前置計劃),套用在 `--only` 指定的那一點;沒有 `--only` 時拒絕。
   - 記:每點跑完當場寫一筆治理帳 gate `choice-kill`、kind `choice-kill`,欄位 `file`、`old`、`new`、`group`、`verdict`(`killed`、`survived`、`no_result`)、`killing_test`、`clauses`、`plans`、`test_blobs`(這次跑過的每支測試所在檔在 HEAD 的物件編號)、`reason`(no_result 時)、`via`(`run`;situation-rule 寫的是 `situation-rule`)、`attempt`(同身分第幾次)、`token`。中斷 → 已跑完的點照記、跑到一半的那點不記、rc 2。
   - rc 取最大:全部有效處置 → 0;有存活 → 1;有跑不出結果、不唯一或被中斷 → 2。存活的點按需求脈絡組印:每組一段,列組裡每一點(定位、成員、壞法)、處置選項(見範圍 3)與現成指令骨架;推定不是需求的點另列一段、不算存活。
   - `--draft`:對每個存活組,另印一段「需求草稿」材料:組裡的點、外層函式全文(最多 80 行)、守的測試名,加一段現成派工詞(工具不呼叫模型);草稿只是建議,寫回仍走 situation-rule 的人裁。
   - 不寫計劃、不改程式。
   **`lumos choice-kill --judge|--split|--unsuppress …`**(判):不跑測試,不套用「跑之前」那串檢查;要人裁同意。
3. **存活的處置**(人裁同意見〈用詞〉;處置以需求脈絡組為單位,能給定位處也能給 `--group <組號>` 一次處置整組):
   - **規格沒寫** → `lumos situation-rule --group <組號>`(或 `--point <定位>`)`--plan … --clause … --test … [--consent …]`:situation-rule 新增一條獨立的選擇點路徑——`--seg`/`--row`/`--file`/`--old`/`--new` 改成選用,跟 `--group`/`--point` 互斥(驗證放進入口);選擇點路徑的檢查是「定位在目前範圍算得出、old 在 HEAD 恰好一次、new 是表裡那個成員的壞法」,不走情境段與觸發字那套檢查;`--old`/`--new` 由選擇點帶入。給 `--group` 時對組裡每一點各跑一次殺傷力(新條款綁的測試),全部 killed 才寫回條款;有一點沒殺掉 → rc 1、不寫、列出那一點(人可 `--split` 拆出去,或改條款與測試再跑)。寫回條款、綁測試、記人裁事件照原本流程;冪等鍵從 (seg, row) 換成 (file, old, new) 的集合。寫回成功同時記組裡每一點的 `choice-kill` killed(`via: situation-rule`)。
   - **測試太弱** → 補測試或改綁之後重跑 `choice-kill --only <定位>`(或不帶 `--only` 全跑)。
   - **換了一樣或不是需求** → `lumos choice-kill --judge <定位>|<組號> --as equivalent|not-requirement --reason "<至少 10 實字>" [--consent …]`:每一點記一筆 kind `judged`(欄位 `file`、`old`、`new`、`as`、`reason`、`origin`、`consent`、`style`、`token`);`as` 是 `not-requirement` 時 `style` 帶那一點的樣式,同樣式之後自動推定。
   - **拆組、撤回推定** → `lumos choice-kill --split <定位>` 記 kind `split`(之後那一點自成一組);`--unsuppress <樣式>` 記 kind `unsuppress`(撤回後同樣式回到要處置;之後再判同樣式,以最新一筆為準)。兩者都要人裁同意。
   - **程式不該有這個選擇**(DO-178C 的非預期功能)→ 改程式拿掉它;選擇點消失就不再要求。
4. **推送前那一道**:在 `_spec_gate_push_check` 裡、`_spec_gate_push_scan` 之後另起一圈(不論有沒有候選計劃都跑,因為「沒碰到計劃」本身要擋);擋下訊息跟預期值表缺簽合在同一次輸出,不分兩輪(`_spec_gate_push_bad_head` 為新的擋下標籤補標題與說明)。
   - **範圍**:被推送版本 B(`A..B`、`A...B` 取 B,`A..` 取 HEAD,單一版本取它);改到的行用「主線與 B 的分岔點..B」(主線照 pre-push 的遠端主線 ref;算不出分岔點時退回推送範圍本身),跟 `choice-points` 不帶 `--diff` 時算出的同一個範圍,所以帳上的身分對得上。B 取不到照 `_spec_gate_push_check` 既有的算不出範圍放行規則。
   - **讀哪一版**:選擇點(改到的檔)、計劃(決定守的測試)、治理帳都從 B 讀,重用 `_kt_sit_read_many`(指定版本的檔)與 `_gov_rows_at`(指定版本的治理帳),同一輪按 (提交, 檔) 快取只讀一次;治理帳在 B 讀不到 → 擋。型錄照 `_kt_catalog_path()`(見〈用詞〉)。預期值表那圈照舊讀工作目錄(既有天花板,不在這份改)。不重跑 Gradle。
   - **條件**:B 的改到的行裡有 `.kt` 正式碼、選擇點至少一個、專案有 kotlin-junit 平台、生效日之後(範圍碰到的進行中計劃的日期;沒碰到時看推送當天)。
   - 每個選擇點要有有效處置。缺紀錄、最新 `survived`、`no_result`、不唯一、過期 → 擋,訊息按需求脈絡組列出(每組一段:組號、組裡每一點的定位、成員、壞法、缺什麼)與 `lumos choice-kill` 指令;推定不是需求的點列在最後一段「自動推定、不擋」。
   - 範圍沒碰到任何進行中計劃而有選擇點 → 擋,reason「無規格」(使用者 2026-11-13 裁:「照擋,沒規格就無法判定當前需要援引的語法需求來源」);碰到了但沒有可守的測試 → 擋,reason「無測試」,訊息說補條款或逐點 `--judge`。
   - 擋下時記一筆治理帳 gate `choice-kill`、kind `blocked`(reason 集合:缺紀錄、存活、跑不出結果、不唯一、過期、無規格、無測試;一筆可帶多個 reason 與各自點數)。
   - 紀錄的 `test_blobs` 跟 B 版本不同時只提醒「紀錄後測試改過,建議重跑」,不擋。
5. **登記與讀者**:`choice-kill` 加進 `_KNOWN_GATES`;`("choice-kill", "choice-kill")`、`("choice-kill", "judged")`、`("choice-kill", "split")`、`("choice-kill", "unsuppress")`、`("choice-kill", "blocked")` 這五個 (gate, kind) 配對加進 `LOOP_NOT_CLOSE_EVENTS`(守衛不強制,照 situation-rule 先例登記);`_gov_row` 對 `choice-kill` 取 `token` 並帶出 `verdict`、`group`、`attempt`、`reason`、`as`、`style`、`via`;`_GOV_FIELD_TYPES` 登記新欄位型別(`attempt` 是 `(int,)`;`clauses`、`plans` 是字串清單;`test_blobs` 是物件;`origin`、`consent` 沿用);表只驗 isinstance、排除不了 bool,所以 `--stats` 與推送閘讀者自己用 `type(x) is int` 驗(同 `_spec_gate_ruled_events` 自己驗型別)。`--stats` 印:第一次跑(attempt 1)的殺掉率、存活後的處置分布(`via: situation-rule` 的寫回規格、`via: run` 重跑後殺掉、判等價、判不是需求)、每組平均點數與拆組次數、樣式自動推定的點數與撤回次數(依樣式列前 5)、跑不出結果的筆數、被擋筆數與其中「過期」的占比、每次 choice-kill 的點數與耗時中位數。讀殺傷力帳本時跳過人裁那幾筆的讀者(`_backing_kill_rows`)改成「`source` 非空就跳過」;`gov` 讀殺傷力帳本那支 loader 照舊不分來源(choice-kill 的列會進 gov 統計),兩邊口徑寫進 Systems/guard-kill。
6. **型錄與文件**:Kotlin 型錄新增〈選擇點表〉與它的解析;Systems/規格閘、Systems/guard-kill 補 WHY 行(含兩邊讀殺傷力帳本的口徑);lumos-code-loop 手冊推送前那段補「選擇點沒處置會擋、怎麼補」;lumos-project-notes 指令索引補 `choice-points`、`choice-kill`、`situation-rule --point/--group`。[[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 改成指向這份(正向、反向都在這裡落地),只留 PIT 實驗紀錄當背景。

## 不做

- 不是每一行:乾行不產生壞法(Google 的乾行壓制)。
- 每點只一個壞法,不窮舉同組全部成員(Google 每行一個;成本)。
- 不引進 PIT 或其他外部變異工具(雜訊、商用過濾、零依賴)。
- 這一版不收數字常數、字串常數、`when` 分支刪除、整行刪除、回傳值替換;REVISIT 看數字再加。
- 這一版不讓 AI 自動判等價(ACH 那條);等價一律人判、留帳,判過不再問。
- 工具不呼叫模型:`--draft` 只印材料與派工詞,擬不擬由編排者決定。
- 分組不做真的程式切片(資料流、控制流相依);用「同外層函式、同守的測試」近似,不準時人拆組。
- 不做支配變異(殺掉 A 必殺掉 B 就略過 B):精確算不可判定,而且每點只一個壞法,省不了多少。
- 推送前不重跑殺傷力(Gradle 可能十幾分鐘);只讀帳、驗新鮮度。
- 不管非 Kotlin 專案;測試檔裡的選擇點不算。
- 選擇點的組合(逾時 × 重試)不做,天花板 3。

## 實務隱患

- 選擇點太多、跑太久:每點一個壞法;只跑還沒有有效處置的點(增量,同 Stryker 增量與 PIT 歷史檔的做法);逐點寫帳、中斷不白跑;耗時中位數進 RETIRE-IF ②。
- 等價或不是需求的誤報:判過留帳不再問;占比進 RETIRE-IF ①;表只收型錄判過行為不同的寫法。
- 一題問太多點、選擇點拆太細:存活按需求脈絡組一組一題(t27 專案 98 個存活整理成 15 組缺口的做法);判過的「不是需求」按樣式推廣到同類(Google MuRS 依樣式彙總回饋)。
- 樣式推定把真的規格缺口壓掉:只推廣「不是需求」不推廣「等價」;樣式含外層函式名,不跨函式推廣;推定的點照列在報告與推送訊息最後一段;`--stats` 列推定最多的樣式;人可撤回。
- 分組錯把兩條需求放一組:situation-rule 給 `--group` 時整組都要殺掉才寫回,殺不掉的點列出來,人拆組。
- 壞法編不過(換成 `!!.` 遇到非空型別、拿掉呼叫後型別不合):判跑不出結果、印失敗摘錄;多半要改表(把那個成員拿掉)而不是要人處置,`--stats` 列出跑不出結果最多的組。
- 運算子比對誤判泛型角括號:只認兩側有空白的;ktlint 預設要求二元運算子兩側空白。不照格式寫的程式會漏點,天花板 2。
- 殺掉它的測試後來被換弱:紀錄要求 `killing_test` 還在現在守的測試裡;測試本體改過只提醒。
- 實作改了、紀錄過期:身分是 `old`+`new`,`old` 那一段變了就是新的選擇點、要重跑。
- 守的測試綁在別的計劃:守的測試取範圍碰到的所有進行中計劃,殺掉時記是哪份的哪條。
- 推送閘的耗時:每次推送要從被推送版本解析改動行的選擇點;大分支(改 5000 行)要量,實作時寫進報告。
- 併發與交易:已排除:單人單機依序操作,沿用 guard kill 的隔離工作樹與人裁的訊號收尾;治理帳逐點追加。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 只對改動產生變異、每點一個、存活在代碼審處置 | Google 差異式變異測試,6000 名工程師每次改動都用,存活中位數 2 | https://arxiv.org/pdf/2102.11378 |
| 乾行(log、純轉接)不產生變異、回報沒用就壓同類 | Google 乾行壓制 | https://research.google/pubs/state-of-mutation-testing-at-google/ |
| 運算子只取少數充分的幾種 | Offutt 等五個充分運算子 | https://dblp1.uni-trier.de/rec/journals/tosem/OffuttLRUZ96.html |
| 關係運算子只取部分替換就夠 | Just 等非冗餘變異 | https://homes.cs.washington.edu/~rjust/publ/non_redundant_mutants_icst_2012.pdf |
| API 兄弟寫法寫成改寫表、機械套用 | MutApi | https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843 |
| Kotlin 集合 `any`/`all`/`none` 互換 | Mutant-Kraken | https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin |
| 存活可能是規格缺口、要分三類處置 | MutDafny 從存活變異找出規格弱點 | https://arxiv.org/pdf/2511.15403 |
| 追不到需求的程式是非預期功能,補需求或刪程式 | DO-178C 結構覆蓋分析處置 | https://ldra.com/ldra-blog/do-178c-structural-coverage-analysis/ |
| 等價變異 AI 判讀的準度(這一版不採) | Meta ACH | https://arxiv.org/html/2501.12862 |
| 存活按「講同一件事」分組、一組補一組斷言 | t27 專案 98 個存活:42 等價、55 測試缺口整理成 15 組 | https://github.com/Trinity-S-AI-DNA/t27/issues/12432 |
| 存活按改到的位置分組降冗餘 | 對抗式 LLM 測試生成研究 | https://arxiv.org/pdf/2602.08146 |
| 回饋按程式樣式彙總、壓掉同類 | Google MuRS;有用變異比例 15% 到 89% | https://homes.cs.washington.edu/~rjust/publ/murs_fse_2023.pdf |
| 從程式反推功能:相依的語句是同一關注點(分組的理論依據,這一版用同函式近似) | SCOLOC 切片式關注點定位、功能定位綜述 | https://sel.ist.osaka-u.ac.jp/people/ishio/TR-slicing2007.pdf |
| 不做支配變異:精確算不可判定 | 變異支配圖 | https://www.academia.edu/124341041/Mutant_Subsumption_Graphs |
| 分組與壓同類 | 使用者方向 | 使用者 2026-11-13:「有沒有辦法進一步把,整體的選擇點,能組合出的需求脈絡,再拿來回推? 我主要怕選擇點拆得太細,噪音太多」 |
| 只跑變了的點(增量) | Stryker 增量模式 | https://stryker-mutator.io/docs/stryker-js/incremental/ |
| 不採 PIT:協程雜訊、過濾要商用外掛 | PIT 協程議題、Arcmutate Kotlin 外掛授權 | https://lightrun.com/answers/hcoles-pitest-pitest-generates-unhelpful-mutations-when-using-kotlins-coroutines、https://central.sonatype.com/artifact/com.arcmutate/pitest-kotlin-plugin |
| 換寫法跑測試的零件沿用人裁 | 人裁已在真 Gradle 專案判出 killed | 實測 2026-11-13:測試品質實驗室 Android 副本帶 --import 跑 lumos situation-rule,約 10 秒判 killed、寫回 S3 |
| 選擇點代表需求、可窮舉、審查可機械化 | 使用者大方向 | 使用者 2026-11-13:「改動中的語法,必定是代表一種需求……語法是可以被窮舉的,也就代表 code review 是可以被機械層檢查」 |
| 涵蓋所有開發需求的程式碼,不限某類語法 | 使用者方向 | 使用者 2026-11-13:「我想涵蓋的就是所有開發需求中的程式碼,不是特定哪一種類別的語法」 |

## 驗收條款

- [S1] 當改動行含選擇點表的成員,choice-points 應 每次出現列一個選擇點,乾行、import 行、註解與字串裡的命中、測試檔 不列 [test:t_choice_points_scan]
- [S2] 當運算子出現在泛型角括號、`!!` 或 `!=` 裡,choice-points 應 不把它當選擇點 [test:t_choice_points_operator_edges]
- [S3] 當選擇點那一行在檔裡不唯一,choice-points 應 依序帶前後各最多兩行求唯一,仍不唯一就標不唯一 [test:t_choice_points_identity]
- [S4] 當守的測試有一支讓壞法紅而且沒有弱證據,choice-kill 應 對那一點只呼叫一次殺傷力、記一筆 killed、帶條款順序第一支殺掉它的測試與它的條款 [test:t_choice_kill_killed]
- [S5] 當所有守的測試在壞法下都綠,choice-kill 應 記一筆 survived 並回 1、印處置三選一 [test:t_choice_kill_survived]
- [S6] 當沒有一支強 killed 而有一支判 killed_unattributed、timed_out_weak、弱證據、abort、drifted 或 error,choice-kill 應 記 no_result 帶原因並回 2 [test:t_choice_kill_no_result]
- [S7] 當工作目錄不乾淨、沒有守的測試、或 --import 沒配 --only,choice-kill 應 回 2 不跑 [test:t_choice_kill_rejects]
- [S8] 當同身分已有有效處置,choice-kill 應 跳過那一點不重跑 [test:t_choice_kill_incremental]
- [S9] 當 choice-kill --judge 帶理由與同意,choice-kill 應 記一筆 judged,推送前那一道 應 視那一點已處置 [test:t_choice_kill_judge]
- [S10] 當 situation-rule 帶 --point 而寫回成功,situation-rule 應 用選擇點的 old 與 new 跑殺傷力、以選擇點身分判冪等並另記那一點 killed [test:t_situation_rule_point]
- [S11] 當推送範圍有選擇點沒有有效處置(缺、survived、no_result、不唯一、過期),推送前那一道 應 擋下、按需求脈絡組列出並記 blocked [test:t_spec_gate_push_choice]
- [S12] 當推送範圍有選擇點但沒碰到任何進行中計劃、或碰到的計劃沒有可守的測試,推送前那一道 應 擋下、reason 分別是無規格與無測試 [test:t_spec_gate_push_choice_no_plan]
- [S13] 當推送範圍是 `A..B` 而工作目錄比 B 多一個選擇點,推送前那一道 應 只看 B 版本 [test:t_spec_gate_push_choice_pushed_version]
- [S14] 當計劃日期早於生效日、專案沒有 kotlin-junit 平台、或改動只有乾行,推送前那一道 應 不要求 [test:t_choice_exemptions]
- [S15] 當治理帳有 choice-kill 事件,gov --stats 應 印第一次跑的殺掉率、存活處置分布、跑不出結果筆數、被擋筆數與過期占比 [test:t_gov_stats_choice_kill]
- [S16] 當型錄缺檔,choice-points 與推送前那一道 應 只印提醒不擋;型錄在但表壞了 應 擋 [test:t_choice_table_missing]
- [S18] 當存活的點落在同一個外層函式而且跑過的守的測試相同,choice-kill 與推送前那一道 應 把它們列成同一個需求脈絡組,--split 過的點 應 自成一組 [test:t_choice_groups]
- [S19] 當 situation-rule 帶 --group 而組裡有一點沒被新條款的測試殺掉,situation-rule 應 回 1 不寫回並列出那一點;全部殺掉 應 寫回一條條款並記每一點 killed [test:t_situation_rule_group]
- [S20] 當一點被判 not-requirement,推送前那一道 應 把之後同樣式的新選擇點列成自動推定不擋;判 equivalent 的 不 推廣;unsuppress 之後 應 回到要處置 [test:t_choice_style_suppress]
- [S17] 當在測試品質實驗室 Android 副本把搜尋 ViewModel 的 `flatMapLatest` 改動推送、綁的測試只送一次值,choice-kill 應 判那一點 survived;換回送兩次值的測試 應 判 killed [manual:在實驗副本跑 lumos choice-kill,先用只送一次值的 onlyLatestQueryShown 看 survived,再換回原測試看 killed]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 改動行 `.flatMapLatest { repo.search(it) }` | 一個選擇點,協程與 Flow 那一組(種類換寫法),壞法 flatMapConcat | 〈用詞〉選擇點表 |
| S1 | 改動行 `if (count > limit && enabled)` | 兩個選擇點:`>`→`>=`、`&&`→`\|\|` | 〈用詞〉同一行多個成員 |
| S1 | 改動行 `Log.d(TAG, "query=$q")` | 沒有選擇點(乾行) | 〈用詞〉乾行 |
| S1 | 改動行 `import kotlinx.coroutines.flow.flatMapLatest` | 沒有選擇點 | 〈用詞〉排除 import |
| S1 | 改動行 `// use flatMapLatest here` 與 `"a < b"` | 沒有選擇點 | 〈用詞〉剝註解與字串 |
| S1 | 改動在 `app/src/test/…/SearchTest.kt` 含 `filter` | 沒有選擇點 | 〈用詞〉測試檔不算 |
| S1 | 改動在 `app/src/androidTest/…/FooTest.kt` 含 `filter` | 沒有選擇點 | 〈用詞〉測試檔照 _nodehome_is_test |
| S1 | 改動在 `app/build.gradle.kts` 含 `a > b` | 沒有選擇點 | 〈用詞〉.kts 不算 |
| S1 | 改動行 `val s = "x ${a < b}"` | 一個選擇點 `<`→`<=`(字串樣板裡的程式碼照算) | 〈用詞〉剝字串保留樣板 |
| S1 | 選擇點不在這條分支改到的行 | 不列 | 〈用詞〉只看改到的行 |
| S2 | `val m: Map<String, List<Int>>` | 沒有選擇點 | 〈用詞〉運算子兩側要空白 |
| S2 | `user!!.name`、`a != b` 裡的 `!` | `!!` 不算;`!=` 只算一個 `!=`→`==` | 〈用詞〉拿掉前置 ! 的邊界 |
| S2 | `if (!isEmpty)` | 一個選擇點:拿掉 `!` | 〈用詞〉! 後接識別字 |
| S3 | 兩行完全相同、前後各兩行也相同 | 標不唯一、不跑 | 〈用詞〉身分 |
| S3 | 那一行是另一行的子字串、多帶上一行就唯一 | old 是兩行 | 〈用詞〉往外帶行 |
| S4 | 假平台:守的測試 t_a、t_b,換寫法後 t_a 紅、t_b 綠 | killed、killing_test t_a、clauses 是綁 t_a 的條款;這一點只呼叫一次殺傷力、基準只跑一次 | 〈用詞〉殺掉判定 |
| S4 | 假平台:t_a 判 abort、t_b 判 killed | killed、killing_test t_b | 〈用詞〉有一支強 killed 就是 killed |
| S4 | 守的測試 t_k 在非預設平台(kotlin-junit 不是預設) | t_k 在它自己的平台根跑 | 〈用詞〉配方帶 platform |
| S5 | 假平台:t_a、t_b 換寫法後都綠 | survived、rc 1、印三種處置與指令 | 〈範圍〉3 存活的處置 |
| S6 | 假平台:換完印 `e: Unresolved reference`、沒有測試名 | no_result、reason 帶失敗摘錄、提示 --import、rc 2 | 〈用詞〉殺掉 |
| S6 | 假平台:基準就紅 | no_result(abort)、rc 2 | 〈用詞〉殺掉 |
| S6 | 假平台:t_a 判 abort、t_b 判 survived | no_result、rc 2 | 〈用詞〉沒有強 killed 就看有沒有跑不出結果 |
| S6 | 兩點:一點 survived、一點 no_result | rc 2(取最大) | 〈範圍〉2 rc 取最大 |
| S7 | 計劃檔有未提交改動 | rc 2、沒跑 | 〈範圍〉2 跑之前的檢查 |
| S7 | 範圍碰不到有測試的進行中計劃 | rc 2、說沒規格判不了 | 〈範圍〉2 跑之前的檢查 |
| S7 | `--import` 沒帶 `--only` | rc 2 | 〈範圍〉2 跑之前的檢查 |
| S8 | 第一次跑 3 點全 killed,再跑一次 | 3 點都跳過、不跑殺傷力 | 〈實務隱患〉增量 |
| S8 | 其中一點那一行被改了 | 只跑那一點(新身分) | 〈實務隱患〉紀錄過期 |
| S9 | `--judge app/…/Vm.kt:12 --as equivalent --reason "排序後只取數量順序不影響結果" --consent "這個等價"` | 記 judged、origin ai、consent 是那句原話;推送不擋那一點 | 〈範圍〉3 存活的處置 |
| S9 | `--reason "等價"`(不到 10 實字) | rc 2 | 〈範圍〉3 存活的處置 |
| S10 | survived 那一點跑 `situation-rule --point app/…/Vm.kt:12 …`,新條款綁的測試在壞法下紅 | 條款寫回計劃、記人裁事件、另記那一點 killed | 〈範圍〉3 規格沒寫 |
| S10 | `--point` 與 `--seg` 一起給 | rc 2 | 〈範圍〉3 來源互斥 |
| S10 | 同一段條款文字與同一支測試,先後給兩個不同的 `--point` | 兩次都跑殺傷力、兩點各記 killed(不被判成已寫過) | 〈範圍〉3 冪等鍵換成選擇點 |
| S10 | 同一行兩個選擇點,`--point …Vm.kt:12#2` | 只處置第二點 | 〈用詞〉定位 |
| S11 | 一點沒紀錄 | 擋、列出那一點與 `lumos choice-kill` | 〈範圍〉4 推送前那一道 |
| S11 | 一點最新 survived | 擋、reason 存活 | 〈範圍〉4 推送前那一道 |
| S11 | 一點 killed by t_strong,條款現在綁 t_weak | 擋 | 〈範圍〉4 殺掉它的測試要還在 |
| S11 | 所有點 killed 或 judged | 不擋 | 〈範圍〉4 推送前那一道 |
| S11 | killed 那筆的 test_blobs 跟推送版本不同 | 不擋、提醒建議重跑 | 〈範圍〉4 推送前那一道 |
| S11 | 同時預期值表缺簽 | 兩件一起列在同一次擋下 | 〈範圍〉4 同一圈 |
| S12 | 改了 Kotlin 選擇點、範圍沒碰任何進行中計劃 | 擋、reason 無規格 | 使用者 2026-11-13 裁:沒規格就照擋 |
| S12 | 碰到進行中計劃,但條款全是 `[manual:]` | 擋、reason 無測試、訊息說補條款或逐點 --judge | 〈範圍〉4 推送前那一道 |
| S13 | 推 `A..B`,工作目錄比 B 多一個沒紀錄的選擇點 | 不擋(只看 B) | 〈範圍〉4 被推送版本 |
| S14 | 計劃日期早於生效日 | 不要求 | 〈用詞〉生效日 |
| S14 | 專案只有 python 平台 | 不要求 | 〈範圍〉4 條件 |
| S14 | 改動只有 log 與 import | 不要求 | 〈用詞〉乾行 |
| S15 | 帳上 attempt 1:killed 3(其中 via situation-rule 1)、survived 1、no_result 1;judged 1;blocked 4 筆其中過期 1 | 第一次跑殺掉率 3/5、存活處置寫回規格 1、判等價或不是需求 1、跑不出結果 1、被擋 4(過期 1/4) | 〈範圍〉5 RETIRE-IF |
| S16 | 型錄檔不在 | choice-points 印提醒 rc 0;推送不擋、印提醒 | 〈用詞〉照 _KT_DT_MISSING 先例 |
| S16 | 型錄〈選擇點表〉有一列缺壞法欄 | 擋、指出那一列 | 〈用詞〉表壞了才擋 |
| S18 | `search()` 函式裡 `flatMapLatest`、`> 2`、`.distinctUntilChanged()` 三點存活,守的測試都是 t_a | 一組 `…/SearchViewModel.kt::search`,三點 | 〈用詞〉需求脈絡組 |
| S18 | 同函式兩點,一點跑過 t_a、另一點跑過 t_a 與 t_b | 兩組 | 〈用詞〉同函式且同測試集合 |
| S18 | 同檔兩個同名多載函式各有一點存活 | 兩組,`::search` 與 `::search#2` | 〈用詞〉多載加序號 |
| S18 | 三點一組,對其中一點 `--split` | 兩組:兩點一組、那一點自成一組 | 〈範圍〉3 拆組 |
| S19 | `situation-rule --group` 三點,新條款綁的測試殺掉兩點、一點沒紅 | rc 1、計劃沒動、列出沒紅那一點 | 〈範圍〉3 整組殺掉才寫回 |
| S19 | 同上三點都殺掉 | 寫回一條條款、記人裁、三點各記 killed | 〈範圍〉3 一條條款處理整組 |
| S20 | `toString` 裡 `+`→`-` 判 not-requirement,之後另一支檔的 `toString` 也有 `+` | 新那點列在自動推定、不擋 | 〈用詞〉樣式推廣 |
| S20 | 同上但新那點在 `total` 函式 | 要處置(樣式含函式名) | 〈用詞〉樣式不跨函式 |
| S20 | 一點判 equivalent,同樣式另一點 | 要處置 | 〈用詞〉等價不推廣 |
| S20 | 判 not-requirement 後 `--unsuppress` 那個樣式 | 同樣式的點回到要處置 | 〈範圍〉3 撤回推定 |
| S17 | 實驗副本只送一次值的測試 | survived;換回原測試 killed | 使用者 2026-11-13 面試題 |

## 回退

- 整個關掉:`_CHOICE_SINCE` 設成很遠的未來日期,推送那一道不要求;`choice-points`、`choice-kill` 照留、只是沒人需要。
- 單一組誤報多:從型錄〈選擇點表〉拿掉那一列(下一次推送就不再算)。
- `cmd_guard_kill` 的 `source`、situation-rule 的 `--point` 都是選用,不傳維持原行為。

## 天花板

1. 只證「選擇點表列到的寫法有測試守著」;表沒列到的選擇(數字常數、`when` 分支、整段邏輯)這一版不管,表列得好不好決定上限。
2. 選擇點靠剝註解字串後的文字比對找,不是 Kotlin 語法樹;運算子不照兩側空白格式寫的會漏;字串樣板 `${…}` 裡的程式碼照算,跨行原始字串與反引號識別字裡的不算。
3. 每點單獨換一個壞法,多點組合造成的錯不管。
4. 殺掉只證「換成那一個壞法時有測試紅」,不證測試紅的理由就是那條需求;條款跟選擇點是不是講同一件事靠人裁與代碼審(帳上有 old、new、killing_test、clauses)。
5. 推送前不重跑,信帳;帳是作者自己跑出來的,同代碼審留痕的天花板。
6. 等價與不是需求全靠人判;判錯會把真的規格缺口放過去,判過的同一點不再問;判成不是需求還會推廣到同樣式。
7. 需求脈絡組是「同函式、同守的測試」的近似,不是真的需求;分錯靠人拆組,工具不知道兩個選擇是不是同一條需求。

## 審計修正紀錄

- r1(2026-11-13,6 席,前一版「條款近似錯誤寫法要殺得掉」):52 條/blocking 24/方向改了——宣告與實際壞法脫鉤,改成壞法由工具依型錄兄弟寫法產生。席報告在 governance/review-reports/條款近似錯誤寫法要殺得掉/。
- r1 收斂後複審(同日,3 席,不記帳):28 條/blocking 8/型錄觸發字欄不是兄弟寫法,改成新增互換表。報告在同目錄。
- 方向重定(2026-11-13,使用者):前一版只管條款點名的寫法,使用者要「所有開發需求中的程式碼」、範圍是選擇點不是每一行;整份改寫成「改動選擇點全數產生壞法、存活交人裁」,並照世界解重新調研(Google 差異式變異與乾行、Offutt 充分運算子、MutDafny、DO-178C)。新一輪設計審用新編號。
- 前掃(2026-11-13,preflight-4):25 條(未定義詞 5、壞引用 2、範圍矛盾 6、語意 12),都修進真檔,沒有動核心裁定;改了的機制:每點只呼叫一次殺傷力(基準只跑一次、不再殺掉就停)、situation-rule 選擇點走獨立檢查路徑與新冪等鍵、定位加 `#n`、推送那一道在掃描之後另起一圈並從 B 版讀計劃與帳、範圍用分岔點..B、同意改用 origin/consent、新增 reason 無測試與過期。逐條對照在 governance/review-reports/改動選擇點都要有需求守住/r1-intake.md。
- 降噪(2026-11-13,使用者):怕選擇點拆太細噪音多——存活按需求脈絡組一組一題、整組一條條款寫回;判不是需求按樣式推廣到同類、可撤回(t27 分組、Google MuRS)。
