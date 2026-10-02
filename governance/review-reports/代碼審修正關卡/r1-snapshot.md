---
type: project
status: doing
created: 2026-10-02
updated: 2026-10-02
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/pitfalls-code-loop
  - Systems/loop-convergence-recording
related:
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/guard-kill]]"
---
# 代碼審修正關卡_計劃

白話:代碼審一輪抓到問題、編排者修好之後,現在是直接派下一輪審查員;修補本身弄出來的新 bug 要等下一輪審查員才看得到,所以很多代碼審跑三到五輪。這個計劃在「這輪問閘過了」和「派下一輪」之間加一道修正關卡:編排者寫一份修正紀錄(每組根因修了哪些路徑、哪幾支測試守著),新指令 `lumos loop fix-check` 機械驗它——紀錄完整、測試真的存在、測試在修之前是紅的修之後是綠的、受波及的合約測試全綠;第 2 步再加壓力指令與殺傷力重跑。前兩週只提醒不擋,量到基準再決定要不要擋。

依據:
- 提案:rtb(另一個使用 lumos 的消費專案)的會談 2026-10-01 寫、Enzo 逐段確認,原文在 Enzo 個人資料夾 `~/.claude/specs/2026-10-01-代碼審修正關卡-design.md`(本計劃是它的單源;提案裡「待工具鏈決定的細節」由本計劃決定,跟提案不同的地方列在〈跟提案不同〉)。
- 動機(提案引 2026-10-01 insights 報告,一個月 43 個會談):「修補本身造成新 bug」是頭號摩擦,46 件;實例是第 2 輪抓到的 blocker 由第 1 輪的修補造成(JSON 輸出路徑繞過修補、清洗造成名稱碰撞、修補造成深層巢狀當機)。數字是報告的,本計劃沒有重算。
- Enzo 2026-10-01 裁定路線圖順序「1a-4 → 修正關卡 → 1a-3 → 1b」(見 [[Projects/漂移防治路線圖_計劃]] 的八項機制表),1a-4 已在 2026-10-02 上線。
- Enzo 2026-10-02 兩個裁定:①決策備忘錄=到頂時產底稿、不另設機械擋;②「受影響的測試」=受波及合約測試+這次新寫的測試,照檔案對應推出來的測試只印出來當參考、不跑。

PRIOR-ART: ①SWE-bench 把驗證測試分成 FAIL_TO_PASS(修之前失敗、修之後通過)與 PASS_TO_PASS(修前修後都要過)——對應本計劃的先紅後綠與受波及測試全綠。②IBM 正交缺陷分類(ODC)用固定的缺陷類型清單,才能統計同類重複——對應根因類別固定清單。③lumos 自己的 guard kill 已有「開隔離工作樹、跑指定測試、判紅綠、收掉工作樹」那套做法,先紅後綠照它的步驟寫,不另想一套。
RETIRE-IF: 轉成擋之後連續十個代碼審迴圈,「上一輪修補造成的」發現比例沒有低於前兩週的基準、收斂所需輪數也沒減少;或修正關卡每輪耗時中位數超過 15 分鐘;或跳過的比例超過三成。任一成立就把這道關卡拿掉或改成只在高風險迴圈用。
REVISIT:2026-10-30 第 2 步上線滿兩週左右,用 `lumos gov --stats` 的修正關卡段看:擋下過幾次真問題、跳過比例、每輪耗時、上一輪修補造成的比例。至少擋到過一次真問題才開「轉成擋」的小改動(做法見〈上線〉);一次都沒擋到就先檢討檢查項;帶了 `--regression-set` 的輪不到 5 輪就判「基準量不到」,量測再延兩週,不轉擋。

## 名詞

- **審查帳**:`docs/.canary-log.jsonl`,`lumos canary record` 寫的那本;每輪每席一筆。**載體席**:同一輪裡帶了 `--findings-set` 的那一筆(一輪只准一筆,處置閘會驗);它的 `findings_set` 是這輪的**發現清單**、`folded_set` 是**折入清單**(這輪改進程式的發現)、`finding_severities` 是個別嚴重度(`--finding-severity id=值`,選填)。
- **治理帳**:`docs/.governance-log.jsonl`,各道閘的過、擋、跳過事件;`fix-check` 的事件寫這本,不寫審查帳。
- **凍結材料**:每輪派工前凍結的 `rN-snapshot.patch`;**編排者**:派席、判讀、修正的主會談;**辯方**:被派去反駁發現的席。都是 lumos-code-loop 手冊的詞。
- **平台、`run_cmd`、平台根**:`.lumos/config.json` 的單平台 `test.run_cmd` 或多平台 `platforms.<名>.run_cmd` / `.root`(多平台時平台根可能是子資料夾,例如 `ios/`);**測試索引**:用平台的測試方法樣式掃出來的測試名集合(`_platform_test_index`)。
- **受波及合約測試**:`base..現在` 改到的檔所牽連的、帶 ★INVARIANT★ 合約的節點,其合約行綁的測試(`_bound_tests_for_diff`,推送前 `code-loop check` 也用它)。
- **殺傷力配方**:節點裡 `kill_recipes` 的壞法(把某支檔的一段改壞,看綁定測試會不會紅);**配方短身分**:guard kill 結果行的 `id=`(`_kill_recipe_id` 算的)。
- **壓力指令**:專案自己宣告的「餵大輸入、深層巢狀、看記憶體上限」指令,例如 `python3 scripts/stress_nested.py --depth 5000`;修補常在這種輸入下才炸,所以修完跑一次。
- **決策備忘錄**:迴圈到上限時,給人裁定「再審一輪、換做法還是停」用的整理稿。

## 範圍

- 做(第 1 步):修正紀錄格式;`lumos loop fix-check` 驗五件事(紀錄完整、同類連兩輪要寫為什麼、測試存在、先紅後綠、受波及合約測試全綠);每次跑記治理帳;`lumos loop next` 在最新一輪有折入卻沒過修正關卡時印提醒;`lumos canary record` 載體席多一個選填的 `--regression-set`(這輪哪些發現是上一輪修補造成的)。
- 做(第 2 步):壓力指令;殺傷力重跑;`lumos loop memo` 決策備忘錄底稿;doctor 提醒沒宣告壓力指令;`lumos gov --stats` 修正關卡段。
- 不做:不改輪數上限、處置閘的判定、外家辯方、審查帳既有欄位、推送前與 CI 的全套測試;這兩步都不擋派工、不改處置閘結果(轉成擋另開小改動);設計審迴圈不適用(只對 `code-` 開頭的迴圈);第 1 步不改 guard kill(1a-4 剛改過,第 2 步殺傷力重跑本來就要動它,那時再一起把建工作樹那段改成共用)。

## 做法

### 修正紀錄(每輪一份)

- 位置:`governance/review-reports/<迴圈編號>/<輪>-fix.json`(`<輪>` 是審查帳上那一輪的 `round` 字串,通常是 `r1`、`r2`;不解析數字);`fix-check` 不帶 `--record` 就讀這個位置。用 JSON 不用 Markdown 表——要機械驗每個欄位,表格解析容易因為一個直線字元壞掉。
- 形狀:
  ```json
  {
    "base": "修正前的提交(40 碼)",
    "groups": [
      {
        "id": "G1",
        "category": "output-path",
        "note": "選 other 時必填一句",
        "findings": ["F1", "F3"],
        "paths": [
          {"at": "scripts/lumos:_kill_run", "status": "fixed", "tests": ["t_x"]},
          {"at": "scripts/lumos:_kill_cap", "status": "unaffected", "reason": "只截輸出,不碰檔名"}
        ],
        "prior": {"why_failed": "上次修法為什麼沒守住", "new_approach": "這次換什麼做法"}
      }
    ]
  }
  ```
- `base`:修正前的提交——通常是這輪凍結材料對應的那個提交。工具不要求它是現在提交的祖先(壓提交、改寫提交之後就不是了),只要求它是這個 repo 裡存在的提交。
- 根因類別固定清單(`category` 只能填左邊的值):`escaping` 跳脫或清洗不完整、`path` 路徑處理、`nesting` 巢狀深度或遞迴、`output-path` 輸出路徑不一致(文字對 JSON 等)、`name-collision` 名稱碰撞、`concurrency` 並行或交易邊界、`perf-memory` 效能或記憶體、`boundary` 邊界值、`other` 其他(要寫 `note`)。
- 路徑狀態兩種:`fixed`=這條路徑這次修了,要列守著它的測試;`unaffected`=查過、同一根因不會出現在這裡,要寫理由。
- `at` 寫「檔案:函式」;檔案要在現在的提交裡,函式名要在那支檔裡整字找得到(不驗它真的是函式定義——各棧寫法不同,驗到字面就停)。
- `prior` 只有同類連兩輪(見下)才必填。

### `lumos loop fix-check <迴圈編號> --round <輪> [--record <檔>] [--json]`

名字:頂層的 `fold-check` 已經是設計審「折完看前後矛盾」的指令,所以放在 `loop` 底下叫 `fix-check`。

先決條件(任一不成立回 2、印原因、不寫治理帳事件——這是輸入錯,不是驗了沒過):
- 迴圈編號是 `code-` 開頭;審查帳找得到這一輪的載體席。它的折入清單是空的 → 印「這輪沒有折入,不用跑」回 0、不寫事件。
- 修正紀錄讀得到、是合法 JSON、`base` 是存在的提交。
- 工作目錄沒有還沒提交的程式檔或測試檔改動:用 `git status --porcelain -z` 取**已受版控**的改動(含已暫存),路徑先排除 `_NODEHOME_EXCLUDE_GLOBS` 與 `governance/`,剩下的用 `_drift_m1_code_kind`(含沒副檔名的看首行 `#!`)判程式檔、`_nodehome_is_test`(layout 用 `_nodehome_layout(所有受版控路徑)`)判測試檔。未追蹤的檔不看(同一個 repo 常有別的會談留下的未追蹤檔;忘了 `git add` 的新測試檔會在下面「測試存在」或綠那步不過,失敗方向是擋)。要驗的是「現在的提交」,沒提交的修正驗不到,印「先提交修正」。

逐項驗(任一不過整次回 1;能驗的都驗完再一起印,輸出寫明哪一項、哪一組哪一條、怎麼修):
1. **紀錄完整**:這輪折入的每個發現都落在某一組;組裡的發現都在這輪的發現清單裡;類別在固定清單裡,`other` 有 `note`;每組至少一條 `fixed` 路徑;每條 `fixed` 至少一支測試;每條 `unaffected` 有理由(至少四個字、要有實字,判法同 `[manual:]`);`at` 的檔與函式名找得到。
2. **同類連兩輪**:審查帳上這一輪的前一輪(照帳上輪次出現的順序)有修正紀錄、其中有一組跟這組同類別,而且這組收的發現裡有任一條嚴重度 ≥ major(看載體席的 `finding_severities`;沒記個別嚴重度就當 major 算,寧嚴),這組就必須有 `prior.why_failed` 與 `prior.new_approach`(各至少十個字)。
3. **測試存在**:每支測試名包成 `[test:名]` 交給合約綁定那套解析(`resolve_test_refs`,平台前綴、方法名),要在測試索引裡找得到;只在原始碼文字裡出現、或找不到的都算不過。測試索引掃的是工作目錄,先決條件已擋掉沒提交的測試檔改動,所以等於現在的提交。
4. **先紅後綠**:開兩個隔離工作樹(建法照 guard kill:暫存資料夾 + `git worktree add --detach <路徑> <版本>`;收法照它:`worktree remove --force`、刪資料夾、`worktree prune`,放在 finally 裡一定收;主工作目錄不動)。跑測試時把 `TMPDIR` 指到修正關卡自己的暫存資料夾,跟工作樹一起刪(本 repo 的測試工具紅的時候會在 `TMPDIR` 留暫存現場)。測試在「工作樹 + 平台根相對 repo 頂的路徑」跑,指令是平台的 `run_cmd` 帶 `{method}`,每支逾時同合約測試(`LUMOS_TEST_TIMEOUT`,預設 180 秒)。
   - **紅那邊**:第一個工作樹檢出 `base`,把 `base` 到現在之間改過的測試檔(用 `_nodehome_is_test` 判)換成現在的內容(現在已刪掉的就刪掉),逐支跑紀錄裡的測試(去重):
     - 非 0 結束,而且 `_ran_count` 讀得到跑了至少一支、沒有全被跳過 → 紅,過;
     - 非 0 結束,但讀不出跑了幾支(這棧還讀不出支數、或要測的函式在修之前不存在而匯入就失敗、或選中 0 支)→ 算紅,但在輸出標「看不出跑了幾支」,讓人看得到、自己判斷是不是假紅;
     - 0 結束 → 不過:「修之前就通過,沒守住這次的問題」;
     - 逾時 → 不過。
   - **綠那邊**:第二個工作樹直接檢出現在的提交(不在第一個工作樹上切換——疊過測試檔的工作樹 `git checkout` 會被當成有本地改動而拒絕,前掃實測),逐支跑:0 結束而且 `_ran_evidence_check` 認得出真的跑過 → 過;非 0、逾時、看不出跑過 → 不過。這棧沒有實測過的輸出樣式時,照推送前合約測試閘的做法退回過濾探針(`_bound_tests_filter_probe`)判;平台的 `run_cmd` 沒有 `{method}`(只能整套跑)→ 這支判不過並說明。
5. **受波及合約測試全綠**:`_bound_tests_for_diff`(範圍 `base..現在`,兩個端點比對,不要求祖先關係)算出來的測試,用 `_run_bound_tests` 在主工作目錄真跑(先決條件已擋掉沒提交的程式與測試改動,所以跑的就是現在的提交)。判法:`green` 過;`red`、`unproven`(回成功但看不出跑過)、`no-cmd`、懸空、只在文字裡出現的都不過;算不出來時 `no-pins`/`no-bound`/`no-vault`(沒有牽連合約)算過並印說明,`diff-unavailable`/`no-config` 算不過。照檔案對應(測試地圖建過才有)推出來的測試檔只印成「參考:可能也該跑」,不跑。

另外(只印,不影響過不過):這一輪不是第一輪、載體席沒有 `regression_set` 欄 → 印一行提醒「記帳時帶 `--regression-set`(沒有就寫 none),不然量不到上一輪修補造成的比例」。

記帳與跳過:
- 跑完逐項驗(過或不過)用 `_gate_event_or_warn` 寫一筆治理帳,閘名 `fix-check`(加進 `_KNOWN_GATES`,同步對文件的測試),kind `passed` / `failed`;欄位放 `extra`:`loop`、`round`、`record_sha256`、`groups`(組數)、`tests`(測試支數)、`unclear_red`(看不出跑了幾支的支數)、`secs`(耗時)、`failed_items`(不過的項目代號清單)、`token`(每次跑的隨機碼)。
- 治理帳讀端(`cmd_gov` 的轉換)補轉這些欄位,`token` 放進去重鍵,不然同一個提交上連跑兩次同結果會被折成一筆、統計少算(前掃讀程式確認);`_GOV_FIELD_TYPES` 同步補上新欄位的型別。
- `LUMOS_SKIP_FIX_CHECK=1`:不驗、回 0、記一筆 kind `skipped-env`。

### `lumos loop next` 的提醒(第 1 步)

- 代碼審迴圈、審查帳最新一輪的載體席折入清單不空、治理帳找不到「同一迴圈、同一輪、`record_sha256` 等於現在修正紀錄檔的 sha256、kind `passed`」的事件 → 在輸出加一行提醒與要敲的指令(`--json` 多一個 `fix_check` 欄位)。不管這次判到哪個狀態都印——★到上限(`cap-reached`)那條路尤其要印★:最後一輪的修補沒有下一輪審查會看到,推之前跑一次修正關卡是唯一的機械檢查。修正紀錄檔不存在也印(提醒裡說要先寫)。
- 狀態、回傳碼都不變;設計審迴圈不印。
- 讀治理帳:新寫一支讀函式,逐行先用字串預篩含 `"fix-check"` 的行再解析(治理帳本 repo 現在約 16MB,每次 `loop next` 都掃),壞行跳過。

### `canary record --regression-set`(第 1 步)

- 載體席選填 `--regression-set <id 串|none>`:這輪的發現裡,編排者判斷是上一輪修補造成的;`none`=判過、這輪沒有。id 都要在 `--findings-set` 裡,否則回 2;沒帶 `--findings-set` 的那筆帶了回 2(加進 `cmd_canary` 那串「要跟 `--findings-set` 一起給」的旗標)。存成排過序的 `regression_set` 清單(`none` 存空清單)。
- 由編排者標,辯方不推翻(辯方只殺程式層的假陽性,「是不是上一輪造成的」要看兩輪的改動,屬編排者的判讀)。
- 不加進 `--finding-kind` 的值:那欄是「這條在修程式、文件還是流程」,是量流程自產工作量的唯一欄位;上一輪修補造成的發現也是程式缺陷,混進去會把那個量弄壞。

### 第 2 步

- **壓力指令**:`.lumos/config.json` 的 `fix_check.stress` 是陣列,每項 `{"cmd": "…", "timeout": 秒}`(逾時預設 300);`fix-check` 在現在的提交、repo 根逐條跑,非 0 或逾時算不過。沒宣告 → 印提醒、這項算過,事件記 `stress: "undeclared"`;宣告成空陣列並寫 `fix_check.stress_none_reason`(至少四個字)算已宣告。
- **殺傷力重跑**:`base..現在` 改到的檔裡,有殺傷力配方指著的(掃每篇筆記的配方,比對 `file`),就只重跑那幾條:`cmd_guard_kill` 加一個「只跑這幾個配方短身分」的內部參數,同時把建工作樹那段抽成跟先紅後綠共用的函式。判 `survived`、`drifted`(配方失配)、`error`、`abort`(baseline 就紅)的都算不過並列出配方短身分;`killed` 過;`killed_unattributed`、`timed_out_weak` 是弱證據,照印、不算不過。照常寫殺傷力帳(這是真跑)。
- **決策備忘錄底稿**:`lumos loop memo <迴圈編號>`(唯讀,印到標準輸出)整理審查帳上每一輪:嚴重度、發現數、折入、放行與理由、重現不到的、上一輪修補造成的;再加每輪修正紀錄的組與類別;最後留「選項與各自代價」「建議」兩節給編排者填,填完拿去問人。代碼審迴圈 `loop next` 判到上限時,多印這個指令。
- **doctor 提醒**:治理帳裡有過至少一筆 `fix-check` 事件、而 `fix_check.stress` 沒宣告 → 印一行提醒;從沒跑過修正關卡的專案不吵。
- **統計**:`lumos gov --stats` 多一段修正關卡:`passed`/`failed`/`skipped-env` 次數、耗時中位數、最常不過的項目、每輪發現裡上一輪修補造成的比例(帶了 `--regression-set` 的輪才算進分母,沒帶的印 ?)。

### 上線

- 第 1 步、第 2 步各一個功能提交、各走代碼審。
- 兩步都只提醒不擋。轉成擋是另一個小改動:`loop next` 在缺通過紀錄時改回新狀態 `fix-check-pending`;處置閘加一步「上一輪有折入就要有修正關卡通過紀錄」,只對首筆帳晚於切換日的迴圈生效(另寫一支切點判斷,寫法照 `_panel_retired_for`:常數日期 + 環境變數覆寫 + 不像日期的時間戳當舊帳),舊迴圈回放不翻。條件與時間見上面的 REVISIT。

## 條款

第 1 步:
- [S1] 當這一輪載體席折入了某條發現、修正紀錄的各組都沒收它時,`loop fix-check` 應回 1 並在輸出寫出那條發現的 id;類別不在固定清單、`fixed` 路徑沒有測試、`unaffected` 路徑沒有理由、`at` 的檔或函式名找不到,也各自回 1 並寫出是哪一組哪一條;同一次有多項不過時全部列出 [test:t_fix_check_record_complete]
- [S2] 當 `base` 不是存在的提交、或已受版控的程式檔或測試檔有還沒提交的改動時,應回 2、不寫治理帳事件;只有筆記、帳本、`governance/` 底下的檔或未追蹤檔時照常驗 [test:t_fix_check_needs_committed_fix]
- [S3] 當紀錄裡的測試名在測試索引裡找不到(只在原始碼文字裡出現也算)時,應回 1 並寫出那支測試名 [test:t_fix_check_test_must_exist]
- [S4] 當一支測試在 `base` 加上新測試檔時失敗、在現在的提交通過時,這項應過;在 `base` 就通過時應回 1 並寫「修之前就通過」;要測的函式在 `base` 不存在、匯入就失敗時應算紅並標「看不出跑了幾支」;在現在的提交失敗時應回 1;跑完主工作目錄的 `git status` 跟跑之前一樣、兩個隔離工作樹都已收掉、`git worktree list` 沒有殘留 [test:t_fix_check_red_then_green]
- [S5] 當 `base..現在` 改到一篇帶 ★INVARIANT★ 合約的節點牽連的檔、而那條合約綁的測試在現在的提交是紅的時,應回 1 並寫出那支測試名 [test:t_fix_check_bound_tests_green]
- [S6] 當前一輪修正紀錄有一組類別 C、這一輪修正紀錄也有一組類別 C 而且收了嚴重度 major 的發現(或沒記個別嚴重度)、卻沒寫 `prior.why_failed` 與 `prior.new_approach` 時,應回 1;兩欄都寫了(各至少十個字)就這項過;同類但收的全是 minor 時不要求 [test:t_fix_check_repeat_category_needs_why]
- [S7] 每次 `fix-check` 驗完(過或不過)應在治理帳寫恰好一筆閘名 `fix-check`、kind `passed` 或 `failed` 的事件,帶迴圈編號、輪次、修正紀錄 sha256、耗時、隨機碼;同一個提交上連跑兩次,`lumos gov` 讀出兩筆;`LUMOS_SKIP_FIX_CHECK=1` 時應回 0 並記一筆 `skipped-env`;這輪折入清單是空的、或回 2 時不寫事件 [test:t_fix_check_gov_event]
- [S8] 當代碼審迴圈審查帳最新一輪有折入、治理帳沒有同輪同修正紀錄 sha256 的 `passed` 事件時,`loop next` 應印一行提醒並附 `lumos loop fix-check` 指令(判到 `plant-canary` 與 `cap-reached` 都印),狀態與回傳碼跟沒有這段時一樣;有 `passed` 事件、或是設計審迴圈時不印 [test:t_loop_next_fix_check_reminder]
- [S9] `canary record` 的 `--regression-set` 帶了不在 `--findings-set` 裡的 id、或在沒帶 `--findings-set` 的那筆帶,應回 2;合法時審查帳存排過序的 `regression_set`,`none` 存空清單 [test:t_canary_regression_set]

第 2 步:
- [S10] 當 `fix_check.stress` 有一條指令非 0 結束或逾時時,`fix-check` 應回 1 並寫出那條指令;沒宣告時應印提醒、這項算過、事件記 `stress: "undeclared"`;宣告成空陣列並寫理由時不印提醒 [test:t_fix_check_stress]
- [S11] 當 `base..現在` 改到一條殺傷力配方指著的檔、而那條重跑判 survived 時,`fix-check` 應回 1 並寫出那條配方的短身分;判 killed 時這項過;同一篇另一條配方指著沒改到的檔時不跑它;沒改到任何配方指著的檔時不跑 guard kill [test:t_fix_check_kill_rerun]
- [S12] `loop memo` 對代碼審迴圈應印出每一輪的發現數、折入、上一輪修補造成的 id、修正紀錄的類別,並留「選項與各自代價」「建議」兩節;跑完 repo 沒有任何檔變動;代碼審迴圈 `loop next` 判到上限時應多印 `lumos loop memo` 指令 [test:t_loop_memo_skeleton]
- [S13] 治理帳有過 `fix-check` 事件、`fix_check.stress` 沒宣告時,doctor 應印一行提醒;治理帳沒有 `fix-check` 事件時不印 [test:t_doctor_fix_check_stress_reminder]
- [S14] `gov --stats` 應印修正關卡段,含 `passed`、`failed`、`skipped-env` 次數與耗時中位數,以及帶了 `--regression-set` 的輪裡上一輪修補造成的比例;沒帶的輪不算進分母 [test:t_gov_stats_fix_check]

## 跟提案不同

- 指令名 `lumos loop fix-check`(提案寫 `loop fold-check`,頂層 `fold-check` 已被佔用,同名會讓人以為是同一件事)。
- 修正紀錄用 JSON(提案留給工具鏈決定)。
- 「上一輪修補造成的」用新的選填欄 `--regression-set`,不加進 `--finding-kind`(理由見上)。
- 受波及的測試只跑合約測試+紀錄裡的測試(Enzo 2026-10-02 裁定)。
- 同類連三輪不另設規則、決策備忘錄不設機械擋:高風險與一般代碼審上限都是三輪,連三輪必然同時到頂;到頂本來就停下來問人,備忘錄改成到頂時印底稿指令(Enzo 2026-10-02 裁定)。
- 修正提交不另記欄位:`fix-check` 驗的就是跑的當下那個提交,治理帳記它。
- 「收集失敗算紅」改成「看不出跑了幾支」:本 repo 的測試工具沒有收集階段,讀不出支數的原因不只收集失敗(前掃實測)。

## 回退

- 每一步各自 revert 那個功能提交:指令與提醒消失;審查帳已寫的 `regression_set` 欄與治理帳 `fix-check` 事件留著,讀端不認得就略過(帳本只追加,不刪)。
- revert 之後本計劃條款綁的 `[test:]` 會懸空,status 改 superseded 或在〈實作紀錄〉記一句「已撤回」。

## 實務隱患

- **時間**:先紅後綠每支測試跑兩次;本 repo 一支 `-k` 測試大約幾秒到一分多鐘(要匯入整支測試檔),一輪修正通常 3–10 支,預估每輪多 2–10 分鐘;受波及合約測試的時間同推送前那段(一次推送實測 59 支約 4 分鐘,沒重跑);第 2 步殺傷力重跑每個測試指令先跑一次 baseline(逾時上限 600 秒)再每條配方各跑一次。實測補進〈實作紀錄〉;超過 15 分鐘就是 RETIRE-IF 的一條。
- **把測試檔疊回修正前**:新測試檔裡可能還有別的新測試或輔助函式引用修正前不存在的東西——只跑紀錄裡的那幾支;整支檔匯入就失敗會落到「看不出跑了幾支」,在輸出看得到,由人判斷是不是假紅。只有 python 讀得出支數,其他棧的紅一律標「看不出跑了幾支」。
- **程式跟測試寫在同一支檔的棧**(像 Rust 的檔內測試):疊回測試檔的做法驗不了先紅,這版不偵測。本工具鏈目前支援的棧都是分開的測試檔,沒實測;第一個用檔內測試的棧接入時(新增那個測試 profile 的提交),在那次的計劃裡重看這段。
- **紀錄寫錯的代價**:`base` 填錯(例如填成已含修正的提交)會讓先紅那步判「修之前就通過」→ 回 1,失敗方向是擋,不是放水。
- **治理帳比對**:`loop next` 的提醒靠修正紀錄 sha256 對得上;紀錄改過就要重跑——這是故意的(紀錄改了就是驗的東西變了)。
- **兩處建工作樹的寫法重複**:第 1 步先紅後綠照 guard kill 的寫法另寫一份,第 2 步改 guard kill 時抽成共用(見〈範圍〉不做)。
- **既有測試**:`loop next` 的輸出字面有測試釘著,新提醒只在最新一輪有折入時出現;`_KNOWN_GATES` 有測試比對文件,新閘名要同步文件;治理帳讀端去重鍵改動要跑 `-k gov`。
- **要同步的文件**:lumos-code-loop 手冊第 5 步(修與釘)加「派下一輪前、到頂要推前跑 `lumos loop fix-check`」;指令速查第 06 子檔加指令;[[Systems/pitfalls-code-loop]] 與 [[Systems/loop-convergence-recording]] 各補一段。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只在本機跑測試與讀寫帳本,不連網
- 已排除:不可逆:隔離工作樹跑完就收;帳本只追加;revert 回得去
- 守衛面:新增一道關卡,兩步都只提醒不擋;轉成擋另開改動、另審。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- 前掃(2026-10-02):四類都有命中,全部改進真檔;語意類 9 條的修改前→後記在 `governance/review-reports/代碼審修正關卡/r1-intake.md`,其中 1 條動到先紅的判法(原本要用的函式只認通過的輸出)。
