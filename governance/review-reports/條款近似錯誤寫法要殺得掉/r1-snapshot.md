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

規格閘現在要求條款綁的測試在「還沒實作」時紅,但這只證明測試在「沒做」時紅,不證明在「做錯」時紅:面試題那種只送一次值的測試,對空殼是紅的、對寫錯成 `flatMapConcat` 的實作卻是綠的,規格閘照樣放行。這份計劃是 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 的正向那一半:風險高計劃的條款除了綁測試,再宣告「接近但錯的寫法」;實作完、推送前,把實作換成那個錯寫法跑條款綁的測試,要紅(殺得掉)才算這條條款真的被守住。換寫法、跑測試的零件直接用人裁已經在用的 `cmd_guard_kill` 帶 `recipes_override`,不另寫一套。

PRIOR-ART: Meta ACH(2025)依「關注的需求」生少量針對性變異體再生會殺掉它的測試,在 10,795 個 Android Kotlin 類別上工程師接受 73%;Google 的變異測試實務只變異改到的行、每行最多一個,擋的是「活下來的變異都有處置」而不是分數百分比(Petrović 等,TSE 2021);PIT 是 JVM 主流變異引擎,但 2026-11-13 在 Android 實驗副本跑出的變異體絕大多數落在內聯的協程函式庫(雜訊),也不產 API 層兄弟寫法。採用:ACH 的「依需求宣告壞法」、Google 的「活下來就要處置、不看分數」;不採:自動產生變異(沿用 [[Projects/guard殺傷力驗證_計劃]] 決策 d1 不自動產生變異的理由:等價變異不可判定、零依賴),PIT 整合留給雙向追溯計劃的反向那一半。
RETIRE-IF: 上線兩個月,宣告的近似錯誤寫法第一次跑就殺掉的比例超過九成五(作者只挑測試本來就抓得到的,沒有提供新證據),或推送前因「近似錯誤寫法沒跑或過期」被擋的次數裡超過一半是工具誤判(錯誤寫法其實還有效)——就把推送那一道降成只提醒。

## 舊否決比對

- [[Projects/guard殺傷力驗證_計劃]] 決策 d1「合約殺傷力驗證不自動產生變異」:這份不自動產生,近似錯誤寫法由寫規格的人(或 AI 依需求)宣告,跟合約的 `kill_recipes` 同一種宣告式壞法;不衝突。
- [[Projects/高風險測試證據加嚴_計劃]] 第二批「CI 對改到的行跑變異測試」:那份是自動變異、要外部工具,排在 2026-12-15 回頭看;這份不碰外部工具,也不取代它。
- [[Systems/guard-kill]] 否決「另抽一支共用的殺傷力函式」:這份照那條決定,沿用 `cmd_guard_kill` 的 `recipes_override`,不另抽。

## 用詞

- **前置**:要等 [[Projects/人裁殺傷力在真實Android專案跑得起來_計劃]](另一條分支)合進主線才動工:補 import 的 `also` 路徑、失敗摘錄 `fail_excerpt`、Android run_cmd 檢查都來自那份。
- **近似錯誤寫法**:條款行上的標記 `[near:<一句話>]`,講「接近但錯的實作」長怎樣(例:`[near:用 flatMapConcat 代替 flatMapLatest,舊查詢的結果會照順序顯示]`)。一行可以有多個;一句話至少 6 個實字、不得含 `]`(含了會讓標記截斷)。寫在規格階段,還不知道實作的原文,所以只寫意思。
- **免宣告**:`[near:無 <理由>]`,理由至少 10 個實字,用在想不出有意義錯寫法的條款(例:純格式輸出)。
- **第幾個**:同一行 `[near:]` 由左到右從 1 數起,`[near:無 …]` 也算一個位置。
- **具體化**:實作完成後,把一個 `[near:]` 落成一條可套用的壞法:被改檔、原文、錯寫法、要補的 import(同前置計劃的 `--import`)。指令 `lumos clause-kill`(見範圍 2)。
- **殺得掉**:`cmd_guard_kill` 帶 `recipes_override` 跑那條壞法,判定是 `killed` 而且沒有弱證據。
- **生效日**:常數 `_NEAR_SINCE`(YYYY-MM-DD,上線當天),環境變數 `LUMOS_NEAR_SINCE` 供測試覆寫(同 `_expected_since` 的寫法);計劃的日期用 `_plan_effective_day`(開頭欄位 created 與第一次進 git 的日期取較晚者),不用首筆設計審帳(消費專案的審查帳不進版控,推送閘與 CI 讀不到)。
- **風險高**:跟預期值表那道同一個判法(`_expected_requirement` 裡呼叫的 `_door_judge`,門判成高)。
- **有效紀錄**:版控治理帳(`docs/.governance-log.jsonl`)裡 gate 與 kind 都是 `clause-kill` 的一筆(寫法照人裁的 `_situation_rule_event_parts`),欄位 `plan`、`clause_id`、`clause_sha`(`_clause_sha`)、`near_index`、`near_text`、`test_name`、`file`、`old`、`verdict`;計劃、條款編號、條款雜湊、第幾個、那句原文都對得上現在那一行,判定殺得掉,而且 `old` 在被推送版本(`git show <推送提交>:<file>`)的整份檔恰好出現一次。同一個條款同一個第幾個有多筆時取最新一筆。殺傷力帳本(`docs/.kill-log.jsonl`)照常記一筆,但推送閘不讀它(消費專案不進版控)。

## 範圍

1. **條款標記**:`INV_TAG_RE` 的名單加 `near`,讓 `_clause_body_of` 剝掉 `[near:…]`、條款雜湊與文法檢查不受它影響。規格閘對風險高、計劃日期不早於生效日的計劃要求:每條綁了 `[test:]` 的條款至少一個 `[near:]`(或 `[near:無 …]`);形狀不合(太短、含 `]`、理由太短)也擋。`[manual:]` 條款不要求。風險低的計劃不要求(那邊已經各自要紅)。
2. **`lumos clause-kill <計劃> S<n> --near <第幾個> --file <檔> --old <原文> --new <錯寫法> [--test <測試名>] [--import "import <pkg>.<Name>"]…`**:
   - 驗:計劃找得到、條款存在而且綁了測試;條款綁多支時要 `--test` 指定其中一支(綁一支時可省);第幾個 `[near:]` 存在而且不是「無」;工作目錄除簿記檔外乾淨;平台有 `run_cmd`(Android 檢查同人裁那一道)。不合 → rc 2、不跑殺傷力。
   - 跑:組一條壞法(`invariant` 填 `S<n>`、`test` 填那支、`note` 帶那句 `[near:]` 原文),呼叫 `cmd_guard_kill(..., recipes_override=[壞法], source="clause-kill")`;補 import 走人裁同一條 `also` 路徑。
   - `cmd_guard_kill` 多一個選用參數 `source`(預設維持現在的行為:給了 `recipes_override` 寫 `situation-rule`),殺傷力帳本那筆的 `source` 照它寫。讀殺傷力帳本、目前只跳過人裁那幾筆的讀者(`_backing_kill_rows`、doctor P2 等,實作時 grep `_SITUATION_RULE_SOURCE` 列全)一併跳過 `clause-kill`。
   - 記:不論判定,治理帳寫一筆 `clause-kill` 事件(欄位見〈用詞〉有效紀錄);判定不是殺得掉時 rc 1,印「補測試讓它紅,或改寫這條近似錯誤寫法」。
   - 不寫計劃。
3. **推送前那一道**:接在 `_spec_gate_push_check` 現有的計劃清單上,只看風險高、計劃日期不早於生效日的計劃:每個非「無」的 `[near:]` 要有一筆有效紀錄;缺、判定不是殺得掉、條款雜湊對不上、`old` 在推送版本裡不是恰好一次(實作改了,紀錄過期)→ 擋,訊息印要跑的 `lumos clause-kill` 指令骨架。治理帳讀不到 → 擋(同預期值表那道讀帳失敗的做法)。推送前不重跑 Gradle(太久),只讀帳。
4. **文件**:Systems/規格閘、Systems/guard-kill 補 WHY 行;lumos-design-loop 手冊寫條款那段補 `[near:]` 寫法;lumos-project-notes 指令索引補 `clause-kill`。

## 不做

- 不自動產生近似錯誤寫法(理由見〈舊否決比對〉);AI 依需求生的寫法也是寫進 `[near:]` 由人審計劃時看。
- 不在推送前重跑殺傷力(Gradle 可能十幾分鐘);只讀帳、驗新鮮度。
- 不處理「活下來但其實等價」的寫法:等價就代表這句近似錯誤寫法寫錯了,改寫那句 `[near:]` 或改成 `[near:無 …]`,不另開放行通道。
- 不管風險低的計劃與 `[manual:]` 條款。
- 不碰反向(從程式的選擇點反推需求),那是雙向追溯計劃的另一半。

## 實務隱患

- 作者挑太容易殺的錯寫法:機器擋不住,靠設計審看 `[near:]` 選得好不好;RETIRE-IF 第一條量這件事。
- 錯寫法編不過:同人裁,import 由人用 `--import` 明寫;其他編不過(型別不合)會判弱證據,印失敗摘錄(`fail_excerpt`)。
- 實作改了、紀錄過期:原文不在了就擋;原文還在但周邊改了不會發現(天花板 2)。
- 計劃改了 `[near:]` 的順序:紀錄用第幾個加原文雙重比對,順序換了就對不上、要重跑。
- 併發與交易:已排除:單人單機依序操作,沿用 guard kill 的隔離工作樹。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 依需求宣告針對性壞法、測試要殺掉 | Meta ACH 在 Android Kotlin 規模化實作,工程師接受 73% | https://arxiv.org/pdf/2501.12862 |
| 活下來就要處置、不擋分數 | Google 變異測試實務 | https://research.google/pubs/practical-mutation-testing-at-scale-a-view-from-google/ |
| 換寫法跑測試的零件沿用人裁 | 人裁已用 cmd_guard_kill 的 recipes_override 在真 Gradle 專案判出 killed | 實測 2026-11-13:測試品質實驗室 Android 副本把搜尋 ViewModel 改成逐一 import,帶 --import 跑 lumos situation-rule,約 10 秒判 killed、寫回 S3 |
| 只送一次值的測試對錯寫法是綠的 | 使用者 2026-11-13 面試題情境 | [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] |

## 驗收條款

- [S1] 當風險高的計劃(生效日後)有一條綁了測試的條款沒有任何 `[near:]`,規格閘 應 擋下並指出那一條 [test:t_spec_gate_near_required]
- [S2] 當 `[near:]` 少於 6 個實字或 `[near:無 …]` 的理由少於 10 個實字,規格閘 應 判形狀不合 [test:t_spec_gate_near_shape]
- [S3] 當條款行多了 `[near:]`,條款雜湊與文法判定 應 跟沒有它時一樣 [test:t_clause_body_strips_near]
- [S4] 當 clause-kill 的壞法讓綁的測試紅、沒有弱證據,clause-kill 應 回 0、在治理帳記一筆帶計劃與條款雜湊的 clause-kill 事件、殺傷力帳本那筆 source 寫 clause-kill [test:t_clause_kill_records]
- [S5] 當 clause-kill 的壞法沒讓測試紅或判弱證據,clause-kill 應 回 1、照實記帳 [test:t_clause_kill_survived]
- [S6] 當條款不存在、沒綁測試、綁多支卻沒給 --test、第幾個 `[near:]` 不存在或是「無」、工作目錄不乾淨,clause-kill 應 回 2、不跑殺傷力 [test:t_clause_kill_rejects]
- [S7] 當推送範圍碰到風險高計劃,而某個 `[near:]` 沒有有效紀錄(缺、沒殺掉、雜湊對不上),推送前那一道 應 擋下並印 clause-kill 指令骨架 [test:t_spec_gate_push_near]
- [S8] 當紀錄的原文在推送版本那支檔不是恰好一次,推送前那一道 應 判過期、擋下 [test:t_spec_gate_push_near_stale]
- [S9] 當計劃日期早於生效日或風險低,規格閘與推送前那一道 應 不要求 `[near:]` [test:t_near_since_and_low_exempt]
- [S10] 當在測試品質實驗室 Android 副本把搜尋計劃 S2 加上 `[near:用 flatMapConcat 代替 flatMapLatest]` 並對只送一次值的測試跑 clause-kill,clause-kill 應 判沒殺掉(證明抓得到面試題的弱測試) [manual:在實驗副本把 onlyLatestQueryShown 換成只送一次值的版本,跑 lumos clause-kill 看 rc 1]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 風險高計劃、生效日後,S1 綁 `[test:t_a]`、沒有 `[near:]` | 擋,指出 S1 | 〈範圍〉1 條款標記:風險高綁測試的條款要宣告 |
| S1 | 同上但 S1 有 `[near:用 >= 代替 >,邊界那天也算過期]` | 不擋 | 〈範圍〉1 條款標記:風險高綁測試的條款要宣告 |
| S1 | 同上但 S1 是 `[manual:…]` | 不擋 | 〈範圍〉1 條款標記:風險高綁測試的條款要宣告 |
| S2 | `[near:改錯]`(2 個實字) | 形狀不合 | 〈用詞〉至少 6 個實字 |
| S2 | `[near:無 純格式]`(理由 3 個實字) | 形狀不合 | 〈用詞〉理由至少 10 個實字 |
| S3 | 同一條條款加與不加 `[near:用 flatMapConcat 代替]` | `_clause_sha` 相同、文法判定相同 | 〈範圍〉1 條款標記:風險高綁測試的條款要宣告 |
| S4 | 假平台:壞法套上後綁的測試失敗 | rc 0、治理帳一筆 clause-kill、clause_sha 等於那行的雜湊;殺傷力帳本那筆 source 是 clause-kill | 〈範圍〉2 clause-kill 驗、跑、記三步 |
| S5 | 假平台:壞法套上後測試仍過 | rc 1、帳上判定 survived | 〈範圍〉2 clause-kill 驗、跑、記三步 |
| S6 | `--near 2` 但那條只有一個 `[near:]` | rc 2、殺傷力沒跑 | 〈範圍〉2 clause-kill 驗、跑、記三步 |
| S6 | 指到的 `[near:]` 是 `[near:無 …]` | rc 2 | 〈範圍〉2 clause-kill 驗、跑、記三步 |
| S6 | `S9` 但計劃只有 S1–S3 | rc 2、殺傷力沒跑 | 〈範圍〉2 驗條款存在 |
| S6 | 條款綁兩支測試、沒給 `--test` | rc 2、殺傷力沒跑 | 〈範圍〉2 綁多支要指定 |
| S6 | 工作目錄有未提交的程式改動 | rc 2、殺傷力沒跑 | 〈範圍〉2 工作目錄要乾淨 |
| S7 | 推送範圍改到風險高計劃、S1 的 `[near:]` 帳上沒有紀錄 | 擋,印 `lumos clause-kill <計劃> S1 --near 1 --file … --old … --new …` | 〈範圍〉3 推送前只讀帳、缺就擋 |
| S7 | 同上、帳上有對得上的殺得掉紀錄 | 不擋 | 〈範圍〉3 推送前只讀帳、缺就擋 |
| S7 | 帳上最新一筆判定是 survived | 擋 | 〈用詞〉有效紀錄要殺得掉 |
| S7 | 帳上紀錄的條款雜湊跟現在那一行不同(條款改過字) | 擋 | 〈用詞〉有效紀錄要雜湊對得上 |
| S8 | 帳上紀錄的原文在推送版本那支檔出現 0 次 | 擋、說過期 | 〈用詞〉有效紀錄 |
| S9 | 計劃日期(created 與首次進 git 取較晚)早於生效日 | 規格閘與推送都不要求 | 〈用詞〉生效日用計劃日期 |
| S9 | 風險低的計劃,條款沒有 `[near:]` | 規格閘與推送都不要求 | 〈範圍〉1 風險低不要求 |
| S10 | 實驗副本搜尋計劃 S2 加 `[near:用 flatMapConcat 代替 flatMapLatest]`,綁的測試只送一次值 | clause-kill 回 1、帳上判定不是殺得掉 | 使用者 2026-11-13 面試題:只送一次值分不出兩種寫法 |

## 回退

- 整個關掉:`_NEAR_SINCE` 設成很遠的未來日期,規格閘與推送那一道都不要求;`clause-kill` 照留但沒人需要。
- `[near:]` 只是條款行上的標記,範圍 1 讓 `_clause_body_of` 剝掉它之後,不要求時留著無害。
- `cmd_guard_kill` 的 `source` 是選用參數,不傳維持原行為。

## 天花板

1. 只證「宣告的那幾種錯寫法會被抓」,沒宣告的錯法照樣漏;錯寫法挑得好不好靠設計審。
2. 新鮮度只看原文還在不在,周邊程式改了但原文沒變時,紀錄不會失效。
3. 推送前不重跑,信帳;帳是作者自己跑出來的,同代碼審留痕的天花板。

## 審計修正紀錄
