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
---
# 條款近似錯誤寫法要殺得掉_計劃

## 白話

規格閘現在要求條款綁的測試在「還沒實作」時紅,但這只證明測試在「沒做」時紅,不證明在「做錯」時紅:面試題那種只送一次值的測試,對空殼是紅的、對寫錯成 `flatMapConcat` 的實作卻是綠的,規格閘照樣放行。這份計劃是 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 的正向那一半:Kotlin 專案風險高計劃的條款,除了綁測試,再指名「型錄裡跟這個寫法同一列的兄弟寫法」;實作完、推送前,由工具在實作裡把那個寫法換成兄弟寫法(壞法由工具產生、不由作者自填),跑條款綁的測試要紅(殺得掉)才算這條條款真的被守住。想不出兄弟寫法、或換了測試沒紅要改宣告,都要人在對話裡點頭。

大方向(使用者 2026-11-13):「改動中的語法,必定是代表一種需求……語法是可以被窮舉的,也就代表 code review 是可以被機械層檢查」。所以壞法照「可窮舉的兄弟寫法」機械產生,跟反向那一半共用同一張型錄。

PRIOR-ART: 業界的壞法都不交給寫測試的人自填——Meta ACH(2025)由一個 AI 代理依「關注的需求」改程式碼產生壞法、另一個代理判等價、生成的測試要在原程式綠在壞法紅,人只審測試不審壞法(https://arxiv.org/html/2501.12862);MutApi(Wen 等,ICSE 2019)把 API 誤用寫成固定的改寫運算子、工具機械套用(https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843),等同我們型錄〈情境決策表〉的兄弟寫法;Google 只在改到的行由工具產生變異、存活的在代碼審顯示、工程師回報「沒用」再壓掉同類(https://arxiv.org/pdf/2102.11378v1、https://testing.googleblog.com/2021/04、https://arxiv.org/html/2306.09130v1),擋的是「存活都有處置」不是分數(https://homes.cs.washington.edu/~rjust/publ/mutation_testing_resolution_icse_2023.pdf);Kotlin 專用的變異工具 Mutant-Kraken 有 Kotlin 運算子但沒有 API 兄弟寫法(https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin),PIT 在協程上產生大量無用變異(https://lightrun.com/answers/hcoles-pitest-pitest-generates-unhelpful-mutations-when-using-kotlins-coroutines;2026-11-13 實驗副本也量到)。採用:壞法由工具依型錄兄弟寫法產生(MutApi 形狀)、生產壞法與寫測試分開(ACH)、存活要處置而且留帳(Google);不採:作者自填壞法(三家都沒有、本計劃設計審 r1 四席各自打穿)、PIT 整合(雜訊,留給雙向追溯反向)、這一版不做 ACH 那種 AI 依需求產生壞法(見〈不做〉與 REVISIT)。
RETIRE-IF: 上線兩個月,①宣告的兄弟寫法第一次跑就殺掉的比例超過九成五(型錄的兄弟寫法對實際測試沒有鑑別力),或②推送前因缺紀錄被擋的次數裡超過一半是工具誤判,或③條款裡 `[near:無 …]` 的占比超過一半(型錄覆蓋不夠、機制空轉)——就把推送那一道降成只提醒,改走 REVISIT 的 AI 產生壞法。
REVISIT:2027-01-15 讀 gov --stats 的 clause-kill 數字(殺掉率、無的占比、存活後改寫次數),決定要不要照 ACH 加「另一個代理依條款產生壞法」的路(型錄沒列到的錯誤)

## 舊否決比對

- [[Projects/guard殺傷力驗證_計劃]] 決策 d1「合約殺傷力驗證不自動產生變異」,理由是等價變異不可判定、誤報、零依賴:這份產生壞法只做「型錄同一列兩個觸發字互換」,不是任意運算子;型錄那一列本身就是「這兩個寫法行為不同、選哪個看需求」的宣告,等價問題在型錄寫列時已經判過;零依賴照守。差異已在這裡寫明,沒有翻 d1。
- [[Projects/高風險測試證據加嚴_計劃]] 第二批「CI 對改到的行跑變異測試」:那份是外部工具自動變異,排在 2026-12-15 回頭看;這份不碰外部工具,也不取代它。
- [[Systems/guard-kill]] 否決「另抽一支共用的殺傷力函式」:這份沿用 `cmd_guard_kill` 的 `recipes_override`,外層把人裁的 `_situation_rule_kill` 參數化共用,不另抽。

## 用詞

- **前置**:要等 [[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]](另一條分支)合進主線才動工:補 import 的 `--import` 與 `also`、失敗摘錄 `fail_excerpt`、Android run_cmd 檢查、殺傷力在平台根跑,都來自那份。
- **適用的計劃**:風險高(跟預期值表那道同一判法:`_expected_requirement` 裡呼叫的 `_door_judge` 判成高)、狀態算「進行中」(同預期值表那道的 `_live`:doing,或這次推送改到的 done)、計劃日期(`_plan_effective_day(..., scope="note")`)不早於生效日、而且專案有 Kotlin 平台(`.lumos/config.json` 有 profile 是 kotlin-junit 的平台)。其他專案沒有兄弟寫法型錄,這一版不要求。
- **要宣告的條款**:適用計劃〈驗收條款〉裡綁了 `[test:]` 的條款,扣掉 `[manual:]`、`[keeps]`、人裁寫回且沒改過字的條款(同預期值表那道:`_spec_gate_ruled_ids`;人裁已經做過同一種殺傷力證明)。
- **兄弟寫法宣告**:條款行上的標記 `[near:D-<n>:<原寫法>→<兄弟寫法>]`(箭頭也收 `->`),例 `[near:D-4:flatMapLatest→flatMapConcat]`。`D-<n>` 是 Kotlin 型錄〈情境決策表〉的列號(`_kt_decision_table`),原寫法與兄弟寫法都要是那一列「觸發字」欄裡的識別字、而且不同。一行可以有多個。
- **免宣告**:`[near:無 <理由>]`,理由至少 10 個實字(`_real_chars`),用在型錄沒有對應列的條款(例:「漏掉一步」這類只能描述的錯)。免宣告要人核可才算(見範圍 2 的 `--waive`)。
- **第幾個**:同一行的宣告與免宣告由左到右從 1 數起。
- **掃描**:條款行先遮掉反引號內容(`_inline_visible_mask`)再找 `[near`;每個 `[near` 要能從頭到尾對上上面兩種形狀之一,對不上(全形冒號、大寫、空標記、列號不存在、識別字不在那列、含多餘 `]`)一律判形狀不合。剝除用條款專用的正規式,只在 `_clause_body_of` 用,不加進合約行共用的 `INV_TAG_RE`(合約指紋不受影響);剝掉時一併吃掉前導空白,`[near:]` 放在行中也不改條款雜湊。
- **壞法**(工具產生):在 `--file` 的被推送版本裡,找出含原寫法整字(`\b<原寫法>\b`)的行;恰好一行時那一行就是 `old`,把那一行裡的原寫法整字換成兄弟寫法就是 `new`;零行或多行 → rc 2,多行時可給 `--line <行號>` 指定(該行要含原寫法)。`--file` 不准是測試檔(`_nodehome_is_test`)、要在平台根底下、以 repo 根為基準寫相對路徑(同人裁的 `kfile` 換算);原寫法另外有逐一 import 時,兄弟寫法要補的 import 由人用 `--import` 明寫(同前置計劃)。
- **殺得掉**:`cmd_guard_kill` 帶 `recipes_override` 跑那條壞法,判定 `killed` 而且 `weak` 為否(從 `result_out` 的列讀,不看回傳碼——`cmd_guard_kill` 對弱證據的 killed 也回 0)。
- **有效紀錄**:版控治理帳(`docs/.governance-log.jsonl`)裡 gate 與 kind 都是 `clause-kill` 的一筆,欄位 `plan`、`clause_id`、`clause_sha`、`near_index`、`near`(那個標記原文)、`test_name`、`file`、`old`、`new`、`verdict`(`killed` 或 `survived`)、`token`;計劃、條款編號、條款雜湊、第幾個、標記原文都對得上現在那一行,`test_name` 在那一行現在綁的測試裡,判定 `killed`,而且 `old` 在被推送版本那支檔恰好出現一次。比對法:先篩出計劃、條款編號、第幾個、標記原文、條款雜湊都對得上的,再取檔內最後一筆。殺傷力帳本(`docs/.kill-log.jsonl`)照常記一筆、`source` 寫 `clause-kill`,但推送閘不讀它(消費專案不進版控)。
- **免宣告核可**:治理帳 gate 是 `clause-kill`、kind 是 `waive` 的一筆,欄位 `plan`、`clause_id`、`clause_sha`、`near_index`、`near`(那個免宣告原文)、`consent`、`by`(`human` 或 `ai-with-consent`,同人裁的判誰裁)。
- **存活後改寫**:帳上有某條款某個兄弟寫法判 `survived`,而現在那一行已經沒有同一個標記原文(改寫、刪掉、改成免宣告)。要繼續推,要有一筆 kind 是 `ack-survived` 的人核可(欄位同免宣告核可,`near` 寫當初存活的那個標記)。
- **生效日**:常數 `_NEAR_SINCE`(YYYY-MM-DD,合進主線的隔天——照 repo「設隔日不設當日」的慣例),環境變數 `LUMOS_NEAR_SINCE` 供測試覆寫;測試總檔比照 `LUMOS_HIGH_RISK_EVIDENCE_SINCE` 預設成 9999-12-31,既有測試停在生效前。

## 範圍

1. **規格閘的宣告檢查**:適用的計劃裡,每條要宣告的條款至少一個兄弟寫法宣告或免宣告;每個 `[near` 形狀要合(〈用詞〉掃描)。不合 → 規格閘擋、指出條款與原因。`_clause_body_of` 剝掉合法標記與前導空白(條款雜湊與文法判定不受影響)。
2. **`lumos clause-kill <計劃> S<n> --near <第幾個> --file <檔> [--line <行號>] [--test <測試名>] [--import "import <pkg>.<Name>"]…`**:
   - 驗:計劃找得到、條款存在而且綁了測試;綁多支時 `--test` 必給、綁一支時省略或給那一支,給了不在綁的清單裡 → 拒;第幾個存在而且是兄弟寫法宣告(免宣告走 `--waive`);計劃檔與工作目錄除簿記檔外乾淨(計劃檔不乾淨時,`cmd_guard_kill` 會把結果判弱證據);`--file` 與壞法照〈用詞〉;平台有 `run_cmd`(Android 檢查同人裁那一道)。不合 → rc 2、不跑殺傷力、不記帳。
   - 跑:把人裁的 `_situation_rule_kill` 參數化(來源、note、訊息),clause-kill 共用它(含 Ctrl-C/SIGTERM/SIGHUP 兩段式收尾 `_situation_rule_signals`、基準耗時提示、失敗摘錄);`cmd_guard_kill` 多一個選用參數 `source`(不傳維持現在的行為),殺傷力帳本那筆照它寫。
   - 記:只有 `killed`(沒有弱證據)與 `survived` 寫治理帳 `clause-kill` 事件(rc 0 與 rc 1);弱證據、abort、drifted、error 不記帳、rc 2,訊息分流(弱證據與 abort 印失敗摘錄、說改設定或環境;drifted 說換 `--line` 或檢查原寫法;survived 才說「補測試讓它紅,或改宣告——改宣告要人核可」)。中斷 → rc 2、不記帳。
   - `--waive --consent "<使用者原話>"`(或終端答 y):第幾個是免宣告時,記一筆免宣告核可;不跑殺傷力。`--ack-survived <標記原文> --consent …`:記一筆存活後改寫核可。判誰裁照人裁那套(`_situation_rule_*` 的同意判定)。
   - 不寫計劃。
3. **推送前那一道**:在 `_spec_gate_push_check` 裡、跟預期值表那道同一圈(共用 `ctx` 讀一次治理帳:`clause-kill` 併進預期值表那道讀帳的閘名清單),只看適用的計劃:每個兄弟寫法宣告要有有效紀錄、每個免宣告要有對得上的免宣告核可、每個存活後改寫要有核可。缺 → 擋,訊息列出每一條缺什麼與要跑的指令骨架;同一圈的預期值表缺簽與這一道缺紀錄一起列出,不分兩輪。治理帳讀不到 → 擋(同預期值表那道)。被推送版本取範圍右端(同 `_spec_gate_push_check` 解析範圍的方式;算不出照那支既有的放行規則),同一輪按 (提交, 檔) 快取檔內容只讀一次。不重跑 Gradle。
4. **登記與讀者**:`clause-kill` 加進 `_KNOWN_GATES`、`LOOP_NOT_CLOSE_EVENTS`、gov 的去重 token(帶 `token` 欄,同人裁)、`--stats` 印殺掉率、免宣告占比、存活後改寫次數(RETIRE-IF 要量的三個數);讀殺傷力帳本時跳過人裁那幾筆的讀者(`_backing_kill_rows` 等)改成「`source` 非空就跳過」,下一種來源不用再改。
5. **文件**:Systems/規格閘、Systems/guard-kill 補 WHY 行;lumos-design-loop 手冊寫條款那段補 `[near:]` 寫法;lumos-project-notes 指令索引補 `clause-kill`;Kotlin 型錄說明補「〈情境決策表〉同列觸發字也是正向殺傷力的兄弟寫法來源」。

## 不做

- 不讓作者自填壞法(業界三家都沒有;本計劃設計審 r1 四席各自打穿)。
- 這一版不做 AI 依條款產生壞法(ACH 那條路):型錄沒有的錯誤走免宣告、要人核可;REVISIT 看數字再決定。
- 不在推送前重跑殺傷力(Gradle 可能十幾分鐘);只讀帳、驗新鮮度。
- 不批次:一次 clause-kill 跑一個宣告;同一份計劃很多宣告時建議放背景跑(人裁的提示照印)。
- 不管非 Kotlin 專案、風險低的計劃、不在進行中的計劃。
- 不碰反向(從程式的選擇點反推需求),那是雙向追溯計劃的另一半;但共用同一張型錄。

## 實務隱患

- 作者挑「本來就殺得掉」的兄弟寫法:壞法限型錄同一列,列本身就是「選哪個要看需求」的寫法;殺掉率進 RETIRE-IF ①。
- 濫用免宣告:要人核可才算,占比進 RETIRE-IF ③。
- 換了測試沒紅就改宣告:存活紀錄留帳,改寫要人核可(存活後改寫)。
- 換綁較弱的測試:有效紀錄要求 `test_name` 還在現在綁的清單裡;測試本體被改弱不會被發現(天花板 2)。
- 兄弟寫法編不過:import 由人 `--import` 明寫;其他編不過判弱證據、印失敗摘錄、不記帳。
- 實作改了、紀錄過期:`old` 那一行在推送版本不是恰好一次就擋。
- 帳膨脹:`old`、`new` 是單行,超過 500 字 rc 2 不記帳。
- 併發與交易:已排除:單人單機依序操作,沿用 guard kill 的隔離工作樹與人裁的訊號收尾。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 壞法不交給寫測試的人自填、生產壞法與寫測試分開、測試要原程式綠壞法紅 | Meta ACH:一個代理產生壞法、另一個判等價,人只審測試;Android Kotlin 上工程師接受 73% | https://arxiv.org/html/2501.12862 |
| 壞法照固定改寫運算子機械產生(API 兄弟寫法互換) | MutApi:API 誤用寫成改寫運算子 | https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843 |
| 只在改到的地方產生壞法、存活在代碼審處置 | Google 差異式變異測試 | https://arxiv.org/pdf/2102.11378v1 |
| 存活要處置、不擋分數;回報沒用的壓掉 | Google 變異測試處置率研究 | https://homes.cs.washington.edu/~rjust/publ/mutation_testing_resolution_icse_2023.pdf |
| 無用變異要壓掉、否則沒人用 | Google 測試部落格(Petrović) | https://testing.googleblog.com/2021/04 |
| 依開發者回饋排序與壓掉變異 | MuRS | https://arxiv.org/html/2306.09130v1 |
| Kotlin 變異工具沒有 API 兄弟寫法 | Mutant-Kraken | https://conf.researchr.org/details/icst-2024/mutation-2024-papers/2/Mutant-Kraken-A-Mutation-Testing-Tool-for-Kotlin |
| 不採 PIT:協程上大量無用變異 | PIT 協程議題 | https://lightrun.com/answers/hcoles-pitest-pitest-generates-unhelpful-mutations-when-using-kotlins-coroutines |
| 換寫法跑測試的零件沿用人裁 | 人裁已用 cmd_guard_kill 的 recipes_override 在真 Gradle 專案判出 killed | 實測 2026-11-13:測試品質實驗室 Android 副本把搜尋 ViewModel 改成逐一 import,帶 --import 跑 lumos situation-rule,約 10 秒判 killed、寫回 S3 |
| 語法選擇可窮舉、審查可機械化 | 使用者大方向 | 使用者 2026-11-13:「改動中的語法,必定是代表一種需求……語法是可以被窮舉的,也就代表 code review 是可以被機械層檢查」 |
| 只送一次值的測試對錯寫法是綠的 | 面試題情境 | [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] |

## 驗收條款

- [S1] 當適用的計劃有一條要宣告的條款沒有任何兄弟寫法宣告或免宣告,規格閘 應 擋下並指出那一條 [test:t_spec_gate_near_required]
- [S2] 當 `[near` 標記對不上兄弟寫法宣告或免宣告的形狀,規格閘 應 判形狀不合 [test:t_spec_gate_near_shape]
- [S3] 當條款行多了合法的 `[near:]` 標記(行尾或行中),條款雜湊與文法判定 應 跟沒有它時一樣 [test:t_clause_body_strips_near]
- [S4] 當 clause-kill 產生的壞法讓綁的測試紅而且沒有弱證據,clause-kill 應 回 0 並在治理帳記一筆 verdict 為 killed、帶 old 與 new 的 clause-kill 事件 [test:t_clause_kill_records]
- [S5] 當 clause-kill 產生的壞法沒讓測試紅,clause-kill 應 回 1 並記一筆 verdict 為 survived 的事件 [test:t_clause_kill_survived]
- [S6] 當條款或第幾個不存在、綁多支沒給 --test、--test 不在綁的清單、--file 是測試檔、原寫法在檔裡不是恰好一行、工作目錄不乾淨,clause-kill 應 回 2 不跑殺傷力不記帳 [test:t_clause_kill_rejects]
- [S7] 當殺傷力判弱證據、abort、drifted、error 或被中斷,clause-kill 應 回 2 不記帳並依原因印不同訊息 [test:t_clause_kill_not_recorded]
- [S8] 當推送範圍碰到適用的計劃而某個宣告沒有有效紀錄(缺、survived、雜湊對不上、test_name 不在現在綁的清單、old 在推送版本不是恰好一次),推送前那一道 應 擋下並印指令骨架 [test:t_spec_gate_push_near]
- [S9] 當免宣告沒有核可、或存活後改寫沒有核可,推送前那一道 應 擋下 [test:t_spec_gate_push_near_waive]
- [S10] 當計劃日期早於生效日、風險低、不在進行中、專案沒有 Kotlin 平台、或條款是人裁寫回或 keeps,規格閘與推送前那一道 應 不要求宣告 [test:t_near_exemptions]
- [S11] 當治理帳有 clause-kill 事件,gov --stats 應 印殺掉率、免宣告占比與存活後改寫次數 [test:t_gov_stats_clause_kill]
- [S12] 當在測試品質實驗室 Android 副本把搜尋計劃 S2 加上 `[near:D-4:flatMapLatest→flatMapConcat]`、綁的測試只送一次值時跑 clause-kill,clause-kill 應 回 1 判 survived(抓得到面試題的弱測試) [manual:在實驗副本把 onlyLatestQueryShown 換成只送一次值的版本,跑 lumos clause-kill 看 rc 1 與帳上 survived]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 適用計劃,S1 綁 `[test:t_a]`、沒有 `[near:]` | 擋,指出 S1 | 〈範圍〉1 要宣告的條款至少一個 |
| S1 | 同上但 S1 有 `[near:D-4:flatMapLatest→flatMapConcat]` | 不擋 | 〈範圍〉1 有兄弟寫法宣告就過 |
| S1 | 同上但 S1 有 `[near:無 這條是輸出格式沒有型錄寫法可換]` | 規格閘不擋(核可在推送前查) | 〈範圍〉1 免宣告也算宣告 |
| S2 | `[near:D-4:flatMapLatest→collect]`(collect 不在 D-4 觸發字) | 形狀不合 | 〈用詞〉兩個識別字都要在那一列觸發字 |
| S2 | `[near:D-999:a→b]` | 形狀不合 | 〈用詞〉列號要存在 |
| S2 | `[near：D-4:flatMapLatest→flatMapConcat]`(全形冒號) | 形狀不合 | 〈用詞〉對不上形狀一律不合 |
| S2 | `[near:無 純格式]`(理由 3 個實字) | 形狀不合 | 〈用詞〉理由至少 10 個實字 |
| S2 | 條款行反引號裡寫 `` `[near:]` `` 當說明 | 不算宣告也不算形狀不合 | 〈用詞〉掃描先遮反引號 |
| S3 | `當 A [near:D-4:flatMapLatest→flatMapConcat],應 B` 對 `當 A,應 B` | `_clause_sha` 相同、文法判定相同 | 〈用詞〉剝除連前導空白 |
| S4 | 假平台:`--file` 有一行含 flatMapLatest,換成 flatMapConcat 後綁的測試失敗 | rc 0、治理帳一筆 killed,old 是原行、new 是換掉後的行 | 〈範圍〉2 壞法由工具產生 |
| S5 | 假平台:換成兄弟寫法後測試仍過 | rc 1、治理帳一筆 survived | 〈範圍〉2 survived 也記帳 |
| S6 | 條款綁 t_a,給 `--test t_other` | rc 2、沒跑、沒記帳 | 〈範圍〉2 --test 要在綁的清單 |
| S6 | `--file` 是 `app/src/test/…/SearchTest.kt` | rc 2 | 〈用詞〉壞法不准打在測試檔 |
| S6 | `--file` 有兩行含 flatMapLatest、沒給 `--line` | rc 2、說要給 --line | 〈用詞〉原寫法要恰好一行 |
| S6 | 條款綁 t_a、t_b,沒給 `--test` | rc 2 | 〈範圍〉2 綁多支要指定 |
| S6 | 計劃檔有未提交改動 | rc 2 | 〈範圍〉2 計劃檔要乾淨 |
| S7 | 假平台:run_cmd 沒有 `{method}`、整套跑時紅(弱證據) | rc 2、沒記帳、印失敗摘錄 | 〈用詞〉殺得掉要沒有弱證據 |
| S7 | 假平台:基準就紅(abort) | rc 2、沒記帳、說改設定或環境 | 〈範圍〉2 只記 killed 與 survived |
| S8 | 適用計劃 S1 宣告帳上沒有紀錄 | 擋,印 `lumos clause-kill <計劃> S1 --near 1 --file …` | 〈範圍〉3 缺就擋 |
| S8 | 帳上有對得上的 killed 紀錄 | 不擋 | 〈範圍〉3 有效紀錄就過 |
| S8 | 帳上 killed 之後又一筆 survived(同條款同宣告) | 擋 | 〈用詞〉取篩完的最後一筆 |
| S8 | 帳上 killed 用 t_strong,條款現在綁 t_weak | 擋 | 〈用詞〉test_name 要在現在綁的清單 |
| S8 | 帳上 old 在推送版本那支檔出現 0 次 | 擋、說過期 | 〈用詞〉old 要恰好一次 |
| S9 | S1 有 `[near:無 …]`、帳上沒有 waive 核可 | 擋 | 〈用詞〉免宣告要人核可 |
| S9 | 帳上 S1 的 flatMapLatest→flatMapConcat 曾 survived,條款已改成別的宣告、沒有 ack-survived | 擋 | 〈用詞〉存活後改寫要人核可 |
| S10 | 計劃日期早於生效日 | 不要求 | 〈用詞〉生效日用計劃日期 |
| S10 | 專案 `.lumos/config.json` 只有 python 平台 | 不要求 | 〈用詞〉適用要有 Kotlin 平台 |
| S10 | 條款是人裁寫回、沒改過字 | 不要求 | 〈用詞〉要宣告的條款扣掉人裁 |
| S10 | 計劃 status 是 todo | 推送前不要求 | 〈用詞〉適用要進行中 |
| S11 | 帳上 killed 3 筆、survived 1 筆、waive 1 筆、ack-survived 1 筆 | 印殺掉率 3/4、免宣告 1、存活後改寫 1 | 〈範圍〉4 RETIRE-IF 三個數 |
| S12 | 實驗副本搜尋計劃 S2 加 `[near:D-4:flatMapLatest→flatMapConcat]`,綁的測試只送一次值 | clause-kill 回 1、帳上 survived | 使用者 2026-11-13 面試題:只送一次值分不出兩種寫法 |

## 回退

- 整個關掉:`_NEAR_SINCE` 設成很遠的未來日期,規格閘與推送那一道都不要求;`clause-kill` 照留但沒人需要。
- `[near:]` 只是條款行上的標記,剝掉之後不要求時留著無害。
- `cmd_guard_kill` 的 `source` 是選用參數,不傳維持原行為。

## 天花板

1. 只證「型錄那一列的兄弟寫法會被抓」,型錄沒列到的錯誤靠免宣告與人核可;型錄列得好不好決定上限。
2. 新鮮度只看 `old` 那一行還在不在、測試名還在不在,測試本體被改弱、周邊程式改了都不會讓紀錄失效。
3. 推送前不重跑,信帳;帳是作者自己跑出來的,同代碼審留痕的天花板(手寫偽造一行屬刻意多步,範圍外)。
4. 條款跟兄弟寫法是不是在講同一件事,機器只驗列號與識別字合法;選錯列靠設計審。

## 審計修正紀錄

- r1(2026-11-13,6 席):52 條/blocking 24/方向改了——宣告與實際壞法脫鉤(四席各自打穿),照業界(ACH、MutApi、Google)改成壞法由工具依型錄兄弟寫法產生、免宣告與存活後改寫要人核可;其餘折:換綁測試、弱證據、閘名登記、只看進行中計劃、人裁條款豁免、測試總開關、掃描器、讀帳一次。席報告在 governance/review-reports/條款近似錯誤寫法要殺得掉/。
- r1 方向由使用者 2026-11-13 裁:「照方向,計畫連結到這些 sources,日後好說明」。
