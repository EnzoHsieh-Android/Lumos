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
  - Systems/代碼審修正關卡
  - Systems/reversibility-governance-ledger
  - Systems/bound-tests-gate
  - Systems/guard-kill
  - Systems/規格閘
  - Systems/loop-convergence-recording
  - Systems/finding-refute
related:
  - "[[Projects/代碼審修正關卡_計劃]]"
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Systems/bound-tests-gate]]"
  - "[[Systems/規格閘]]"
  - "[[Systems/guard-kill]]"
---
# 代碼審修正關卡第0步_計劃

白話:代碼審一輪修完、派下一輪之前,先讓工具機械驗一次編排者的修正紀錄——每個折入的發現有沒有歸到一組根因、每條修了的路徑有沒有測試守著、那些測試在修好的版本裡真的存在而且是綠的、受波及的合約測試全綠;最新一輪有修正卻沒驗過,`lumos loop next` 就印提醒。這是 [[Projects/代碼審修正關卡_計劃]] 拆出來的第一步:那份完整設計的核心「把修正拿掉、看測試會不會紅」跑滿三輪設計審還有 17 條 major,Enzo 2026-10-02 裁定先做不含它的這部分、跑兩週看數據再決定要不要做。前兩週只提醒不擋。

依據:
- 動機與提案:見 [[Projects/代碼審修正關卡_計劃]] 的〈依據〉(rtb 會談提案、insights 報告「修補本身造成新 bug」46 件)。
- Enzo 2026-10-02 裁定:①完整設計到上限未收斂 → 拆小,先做這份;②決策備忘錄不設機械擋、③受影響測試只跑合約測試+紀錄裡的測試(兩條沿用完整設計那時的裁定)。
- 完整設計三輪審查(卷證 `governance/review-reports/代碼審修正關卡/`)裡跟本步有關、已經查清楚的事:本 repo 測試工具 `-k` 是子字串篩選、規格閘已有一支測試的紅綠判法(參數化測試看宣告支數);`_run_bound_tests`、`_bound_tests_check` 傳隔離工作樹的路徑進去跑得起來(第 3 輪實測 59 支 258 秒、帳只寫在樹裡;參數要是 `Path`);治理帳讀端轉換沒吐 `token`、照第 1 版補 `tests` 整數型別會讓 81 筆既有審查帳行被丟;guard kill 是用 `git -C <平台根> worktree add` 建樹、測試在樹的最上層跑(第 3 輪兩席實測);「之後有沒有改程式」代碼審留痕已有現成判法。

PRIOR-ART: SWE-bench 的 PASS_TO_PASS(修正後受影響的測試要全綠)——本步只做這一半,FAIL_TO_PASS(修之前要紅)留給完整設計。全部沿用 lumos 既有零件:guard kill 的隔離工作樹建法、新增告警閘的殘骸清理(`_lint_new_clean_stale` 那種「同前綴超過一天就清」)與依賴資料夾連結(`_lint_link_deps`)、規格閘的一支測試判法(`_spec_gate_verdict`/`_spec_gate_declared`)、推送前合約測試閘(`_bound_tests_check`)、代碼審留痕的「之後只動簿記檔」判法(`_codeloop_record_valid_ex`)。
RETIRE-IF: 上線滿四週,`fix-check` 從沒擋到過一次真問題(人判:擋下的項目裡沒有一條是修正紀錄或測試真的有缺);或跳過比例超過三成;或每次耗時中位數超過 10 分鐘。任一成立就拿掉,連同完整設計一起停案。
REVISIT:2026-10-20 上線滿兩週左右,從治理帳與審查帳數:跑了幾次、擋了幾次、擋在哪一項、耗時;`fix-check` 通過的輪,下一輪仍被標成「上一輪修補造成的」發現有幾條——那就是只驗綠、不驗紅漏掉的量,決定完整設計的「先紅」要不要做、做哪幾個棧。

## 名詞

- **審查帳**:`docs/.canary-log.jsonl`,`lumos canary record` 寫的那本;每輪每席一筆。**載體席**:同一輪裡帶了 `--findings-set` 的那一筆(一輪只准一筆);它的 `findings_set` 是這輪的**發現清單**、`folded_set` 是**折入清單**、`finding_kinds` 是每條在修什麼(`code`/`spec`/`process`,選填但給就要給全)、`finding_severities` 是個別嚴重度(選填)。代碼審載體席都帶 `round`(2026-10-02 數過 314 筆,全帶)。
- **治理帳**:`docs/.governance-log.jsonl`,各道閘的過、擋、跳過事件;`fix-check` 的事件寫這本。
- **派工單**:每輪派審查員時寫的 `rN-dispatch.json`;**編排者**:派席、判讀、修正的主會談。都是 lumos-code-loop 手冊的詞。
- **修正後**:`fix-check` 開跑那一刻的 `HEAD`(40 碼),整次都對它跑。
- **樹**:`fix-check` 為這次建的、檢出修正後的隔離工作樹;程式裡一律用 `Path` 傳(`load_platforms` 多平台時、`_lint_link_deps`、`_bound_tests_check` 都要 `Path`,傳字串會丟例外——第 0 步第 1 輪審查實測)。**這次用的設定**:樹裡那份 `.lumos/config.json`(就是提交裡那份;設定檔沒進版控時是從主工作目錄複製進去的那份),先決條件與逐項驗全部讀它,不讀主工作目錄那份。
- **一支測試的判法**:規格閘那套——`_run_bound_tests` 逐支真跑,`_ran_count` 讀篩到幾個案例,`_spec_gate_declared` 數程式裡宣告了幾支名字含這個字串的測試,`_spec_gate_verdict` 判紅、綠或弱證據(篩選選到好幾支不同的測試、被跳過、一支都沒跑到都是弱證據;同一支測試的多組輸入不算撞名)。
- **理由夠不夠**:用既有的 `_escape_reason_ok`(去掉前後空白後至少 `_MANUAL_MIN_CHARS` 個字、要有實字),不另寫。
- **受波及合約測試**:`base..修正後` 改到的檔所牽連的、帶 ★INVARIANT★ 合約的節點,其合約行綁的測試;算法與判法是推送前合約測試閘那套([[Systems/bound-tests-gate]])。

## 範圍

- 做:修正紀錄格式與樣板;派工單記 `base_commit`;手冊寫明 `fix-check` 要在背景跑或把指令逾時拉到 10 分鐘(一次約 5 分鐘,對話裡跑指令的預設上限 2 分鐘會把它砍掉、沒記到帳就一直被提醒);`lumos loop fix-check` 驗五件事(紀錄完整、同類連兩輪要寫為什麼、測試存在、紀錄裡的測試在修正後是綠的、受波及合約測試全綠);每次跑記治理帳(讀端吐 `token` 與新欄位);`lumos loop next` 提醒、第 2 輪起的記帳範本帶 `--regression-set`;`lumos canary record` 載體席選填 `--regression-set`;guard kill 建、收隔離工作樹那段抽成共用函式;規格閘「跑一批測試再逐支判」那段(三處)抽成共用函式;推送前合約測試閘「測試名解析成平台與方法、判在不在索引裡」那段抽成共用函式。
- 不做:先紅(把修正拿掉看測試會不會紅)、壓力指令、決策備忘錄底稿、doctor 提醒、`gov --stats` 段——都留在 [[Projects/代碼審修正關卡_計劃]],看本步數據再決定;不擋派工、不改處置閘;設計審迴圈不適用;不改 `_kill_run`(被 Ctrl-C 時子行程會變孤兒是既有行為,另開 Issue);不修 `impact --diff` 純改名只算新路徑、`_ran_count` 把失敗訊息裡的 `1 skipped` 字樣當跳過這兩個既有洞(各開 Issue;改名在本步只印提醒);不清 guard kill 自己的殘骸(它沒有清殘骸的步驟是既有行為,共用函式只在修正關卡呼叫時清)。

## 做法

### 修正紀錄(每輪一份)

- 位置固定:`governance/review-reports/<迴圈編號>/<輪>-fix.json`(`<輪>` 是審查帳上那一輪的 `round` 字串;不解析數字;不提供指到別處的旗標)。
- 派工單多一個頂層欄位 `base_commit`:派工當下 `git rev-parse HEAD` 的 40 碼(手冊第 2 步寫派工單時一起寫)。讀派工單的既有函式(`_roster_dispatch_entries`、`cmd_seat_check`)只讀自己認得的鍵,多一欄不影響(第 3 輪審查讀過)。讀同一輪的 `<輪>-dispatch*.json`(照既有讀派工單的通配);頂層是物件(單席物件或帶 `seats` 的物件)才讀它的 `base_commit`,頂層是陣列一律當作沒有;幾份都有而且不一樣時當作沒有並說明。
- 樣板:`lumos loop fix-check <迴圈編號> --round <輪> --record-template`(命名照 `--dispositions-template`):骨架 JSON 印到標準輸出、提示印到標準錯誤,不寫檔;`base` 從派工單的 `base_commit` 帶入(沒有、讀不懂、不是 40 碼十六進位都留空並在標準錯誤說一句);這輪要修正紀錄的折入發現各列一組待填。只要求迴圈與輪次存在。
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
- `base`:修正前的提交;接受短 sha、分支名,工具先用 `git rev-parse --verify --end-of-options <base>^{commit}` 轉成 40 碼(以 `-` 開頭的輸入不會被當成旗標),轉不成就回 2。不要求是修正後的祖先(壓提交之後就不是了)。
- 要修正紀錄的發現:載體席有 `finding_kinds` 時只有 `code` 的折入發現要落在某一組;`spec`、`process` 的不用,輸出列出「這幾條判成不用修正紀錄」。沒有 `finding_kinds` 時全部折入的都要,輸出提醒「記帳時帶 `--finding-kind` 可讓文件、流程類發現免填」。
- 根因類別固定清單(`category` 只能填左邊的值):`escaping` 跳脫或清洗不完整、`path` 路徑處理、`nesting` 巢狀深度或遞迴、`output-path` 輸出路徑不一致、`name-collision` 名稱碰撞、`concurrency` 並行或交易邊界、`perf-memory` 效能或記憶體、`boundary` 邊界值、`other` 其他(要寫 `note`)。
- 路徑狀態兩種:`fixed`=這條路徑這次修了,要列守著它的測試;`unaffected`=查過、同一根因不會出現在這裡,要寫理由。
- 紀錄的大小上限:檔案 1MB、組 100 個、全部測試名 200 支;超過回 2(防手寫失手或惡意餵爆)。
- 測試名:去掉前後空白後要過 `_KILL_METHOD_OK_RE` 白名單(含 `]`、空白、shell 字元的直接判不過——否則 `[test:名]` 解析時會被截斷,驗的跟紀錄寫的不是同一支)。
- `at` 寫「檔案:函式」,在第一個冒號切開,函式那段不能是空的、要含至少一個字母、數字、底線或中日韓文字;檔案那段不能是絕對路徑、不能含 `..`,而且在修正後的提交裡要是一般檔(`git ls-tree` 模式 100644 或 100755;資料夾、符號連結、子模組都判不過)——或在 `base..修正後` 之間被刪掉(`fixed` 才允許)。`fixed` 的檔必須在 `base..修正後` 之間有改動(`git diff --no-renames --name-only -z`,中文與空白檔名照原樣比);修正後還在的檔,函式那段要在那支檔裡出現、前後不接英數字或底線;修正後已刪掉的檔不驗函式段。`unaffected` 的檔要在修正後的提交裡、函式段要找得到。不驗它真的是函式定義(各棧寫法不同,驗到字面就停)。

### `lumos loop fix-check <迴圈編號> --round <輪> [--repo <根>] [--json]`

名字:頂層的 `fold-check` 已經是設計審「折完看前後矛盾」的指令,所以放在 `loop` 底下叫 `fix-check`。`--repo` 照 `loop status` 的寫法。

執行順序(便宜的先做,失敗就不必建樹):⓪迴圈編號與輪次的字元檢查 → `LUMOS_SKIP_FIX_CHECK=1` 就在這裡記 `skipped-env`、回 0 → ①其餘便宜的先決條件 → ②記下 `HEAD` 的 40 碼當**修正後** → ③清殘骸 → ④建樹與樹的準備、樹裡的先決條件 → ⑤逐項驗 → ⑥記帳、收樹。`--record-template` 只做⓪與「迴圈與輪次存在」,不建樹。

先決條件(任一不成立回 2、印原因、不寫治理帳事件):
- 迴圈編號是 `code-` 開頭;迴圈編號與輪次都不含 `/`、`\`、`..`、控制字元(要拼進檔名);審查帳找得到這一輪的載體席。要修正紀錄的折入發現是 0 條 → 印「這輪沒有要修正紀錄的折入,不用跑」回 0、不寫事件。
- 修正紀錄讀得到、是合法 JSON(解析深度過深、形狀不對都回 2)、`base` 轉得成存在的提交。
- 樹建得起來(建不起來回 2,附 git 的原因)。
- 樹裡的先決條件(建樹、準備之後判,用這次的設定):`load_platforms(樹)` 讀得懂(丟例外就回 2);每個平台的平台根取實際路徑後都在樹的實際路徑底下、而且是存在的資料夾——平台根寫成 repo 外的相對路徑或絕對路徑(解析出來落在主工作目錄或別處)、平台資料夾沒進版控(樹裡沒有)都回 2,說明是哪個平台、為什麼(第 0 步第 1 輪審查實測:絕對路徑會讓測試在主工作目錄跑、提交版是紅的也判綠;沒進版控的平台資料夾每支測試都判找不到)。

清殘骸:新寫一支(`_lint_new_clean_stale` 只清 repo 底下的 `.lumos/lintbase-*`、不碰工作樹,只借它「同前綴、超過 `_LINT_NEW_STALE_SEC` 就清」的規則):系統暫存資料夾(`tempfile.gettempdir()`)裡修正關卡前綴、修改時間超過一天的資料夾,底下是工作樹的先 `git worktree remove --force` 再刪資料夾,最後 `git worktree prune`;比對前兩邊路徑都先取實際路徑(macOS 的 `/var` 與 `/private/var` 是同一個)。放在共用工作樹函式裡當選項,只有修正關卡打開。

建樹:用共用函式在系統暫存資料夾建一棵檢出修正後的隔離工作樹(下稱**樹**),整次的測試都在樹裡跑,跑完一定收掉;主工作目錄只讀審查帳、治理帳、派工單與修正紀錄,跑的期間別的會談改檔、提交都不影響這次結果。

樹的準備:
- 設定檔:主工作目錄有 `.lumos/config.json`、樹裡沒有(設定檔沒進版控,本機 18 個專案裡有 2 個是這樣)時,直接複製那一份進樹的同一位置,輸出說一句;樹裡有、而主工作目錄那份跟提交裡的不一樣(有沒提交的設定改動)時,輸出說「這次用提交裡那份設定」。
- 依賴資料夾:預設不連。設定 `fix_check.link_deps: true` 時,repo 頂與每個平台根各用 `_lint_link_deps` 把 `node_modules`、`.venv`、`venv` 連回主工作目錄的同一位置,輸出警告一句「依賴資料夾連回主工作目錄:Node 多套件專案的其他套件、Python 可編輯安裝會載到主工作目錄的程式,沒提交的改動可能讓樹裡的測試變綠」(第 0 步第 1 輪審查實測)。不連的專案,需要依賴才跑得起來的測試會在第 4、5 項判不過,輸出附這個設定的說明。

只印提醒、不擋:主工作目錄有已受版控的改動沒提交(`git status --porcelain -z`,改名條目兩個路徑都列)→ 印「這次驗的是提交裡的版本,工作目錄這幾支沒提交的改動不算」列前幾支(同一個 repo 常有別的會談的改動,所以不擋;修正忘了提交時,`fixed` 的檔多半會判「沒改動」)。

逐項驗(任一不過整次回 1;能驗的都驗完再一起印,寫明哪一項、哪一組哪一條、怎麼修):
1. **紀錄完整**:要修正紀錄的折入發現每條都落在某一組;組裡的發現都在這輪的發現清單裡;類別在固定清單裡,`other` 有 `note`;每組至少一條 `fixed` 路徑;每條 `fixed` 至少一支測試,測試名去掉前後空白後不能是空的;每條 `unaffected` 有理由(判法同 `[manual:]`);`at` 照上面那段驗。
2. **同類連兩輪**:前一輪=審查帳上這個迴圈、在這一輪之前最近出現的那一輪(照 `_disposal_round_groups` 的分輪與順序;輪次字串不必是 rN 形式,但要過⓪的字元檢查才拿來拼檔名,過不了就當作沒有前一輪紀錄)。前一輪有修正紀錄、其中有一組跟這組同類別(`other` 不算同類——兩組都填 `other` 不代表同一種根因),而且這組收的發現裡有任一條嚴重度 ≥ major,這組就必須有 `prior.why_failed` 與 `prior.new_approach`(各至少十個字)。個別嚴重度看 `finding_severities`;沒記的那條改看這一輪各席宣告的最高嚴重度。
3. **測試存在**:用從 `_bound_tests_for_diff` 抽出來的共用函式(見下)判,跟推送前合約測試閘同一套:測試名包成 `[test:名]` 解析成平台與方法(`resolve_test_refs` 丟 `ValueError` 時接住、這支判不過並附原因),要恰好一支、方法名過白名單、在 `_platform_test_index(樹)` 的索引裡(`Class.Method` 寫法照那段的處理);只在原始碼文字裡出現、或找不到的都算不過。
4. **紀錄裡的測試在修正後是綠的**:第 3 項判存在的那幾支(去重;第 3 項不過的不送,免得同一支被報兩次)用規格閘抽出來的共用函式(見下)在樹裡跑,每支判綠才過;判紅、弱證據(附規格閘給的原因,例:「篩選匹配到 2 支,測試名要唯一」)都不過;平台的 `run_cmd` 沒有 `{method}`(只能整套跑)時這個平台的測試不跑、判不過並說明(規格閘遇到這種是整批略過;這裡要的是「這幾支是綠的」,證不了就是不過)。
5. **受波及合約測試全綠**:`_bound_tests_check(Path(樹), "base..修正後")`(推送前那道閘的同一支,含過濾探針;它寫的治理帳事件與測試快取落在樹裡、跟著刪掉;過濾探針另有一份放在使用者家目錄的快取,鍵含樹的路徑,所以讀不出支數的棧每次會重探一次,接受)。`green`、`no-pins`、`no-bound`、`no-vault` 過,後三種印說明——但回 `green` 而它的結果裡有平台因為沒設 `run_cmd` 沒跑的,不過(說明哪個平台的合約測試沒跑);`red`、`unfilterable`、`no-config`、`diff-unavailable`、`range-unavailable`、`whole-suite-deferred` 不過;`skipped`(有人設了 `LUMOS_SKIP_BOUND_TESTS`)也不過,印「要跳過整道修正關卡請用 `LUMOS_SKIP_FIX_CHECK`」。`base..修正後` 有程式檔被改名時(`git diff -M --name-status -z` 的改名條目,判程式檔用 `_drift_m1_code_kind`,沒副檔名的讀首行判)只印提醒「改名的檔,舊路徑牽連的合約沒算到」、不判不過——那是 `impact --diff` 的既有洞(推送前那道閘也一樣),另開 Issue 修;判不過的話純改名或 rebase 帶進上游改名就永遠過不了,只能跳過(第 0 步第 1 輪兩席)。

另外(只印):這一輪不是第一輪、載體席沒有 `regression_set` 這個欄位(看欄位在不在,空清單=判過沒有)→ 印一行提醒下一輪記帳時要帶。

記帳與跳過:
- 跑完逐項驗(過或不過)用 `_gate_event_or_warn` 寫一筆治理帳:閘名 `fix-check`(加進 `_KNOWN_GATES`)、`hard=False`、kind 過 `passed`、不過 `warned`(不擋的閘的用字)、跳過 `skipped-env`;`head_sha`=修正後的 40 碼;`extra` 放 `loop`、`round`(名稱與型別同審查帳)、`record_sha256`、`secs`(浮點)、`failed_items`(不過的項目代號清單)、`token`(每次跑的隨機碼)。
- 治理帳讀端(`cmd_gov` 的轉換)對 `fix-check` 事件吐出 `token` 與上面這些欄位(去重鍵本來就含 `token`,轉換沒吐它,同一個提交連跑兩次同結果會被折成一筆);`_GOV_FIELD_TYPES` 補 `record_sha256`、`secs`(整數與浮點)、`failed_items`、`head_sha`——這張型別表是治理帳讀端讀的所有帳共用(第 0 步第 1 輪審查掃過本機全部帳,沒有型別衝突),實作時加之前再掃一次,不得讓任何既有行從型別對變成型別不對。
- `_gate_event_or_warn` 的 `note` 放一句結果摘要(過幾項、不過哪幾項)。它回的不是 `True` 時(沒有 `docs/` 回 `None` 而且不印;寫入失敗回 `False` 並印警告),輸出另加一句「這次結果沒記到帳,`loop next` 會一直提醒」。
- `LUMOS_SKIP_FIX_CHECK=1`:在⓪之後判,不驗、回 0、記一筆 kind `skipped-env`(帶迴圈編號與輪次;迴圈與輪次在審查帳找不到也照記,記的是使用者給的字串)。

### 共用函式(兩支)

- **隔離工作樹**:把 `cmd_guard_kill` 裡「暫存資料夾 + `git -C <在哪建> worktree add --detach <路徑> [<提交>]` + finally 收掉(`worktree remove --force`、刪資料夾、`worktree prune`)」抽成 with 區塊用的共用函式,參數:在哪建(`git -C` 的目錄)、檢出哪個提交(空的就不帶)、資料夾前綴、要不要保留;給出 (樹的路徑或空, 失敗原因)——`worktree add` 失敗時不丟例外,原因照 guard kill 現在的截法(標準錯誤去頭尾空白取前 120 字)。內部管兩層:暫存資料夾與它底下的樹;要保留時兩層都留、只印路徑(照 guard kill 現在 `--keep-worktree` 的行為)。guard kill 照現在的寫法傳平台根、測試在樹的最上層跑、失敗記成 error 繼續下一個平台、`--keep-worktree` 時保留並印路徑——行為一點不改。抽之前先補兩條現在沒被測試釘住的行為(`worktree add` 失敗、多平台時在哪建樹與在哪跑測試),先綠、抽完照綠。
- **一批測試逐支判**:規格閘的條款測試(`_spec_gate_run_clauses`)、相依回歸(`_spec_gate_regress`)、推送前那段(`_spec_gate_push_one`)三處,都是「`_run_bound_tests` 跑一批 → 每支用 `_ran_count`、`_spec_gate_declared`、`_spec_gate_verdict` 判」,手寫了三份。抽成一支 `_spec_gate_judge_items(根, 測試清單, per_prof, loose_for)`,回 (逐支結果, 跑不起來的原因)——逐支結果帶 (編號, 平台, 方法, 紅綠弱, 原因, 失敗細節);失敗細節=`_run_bound_tests` 回傳那筆結果裡的細節欄(第 5 個值,不是另外收的輸出尾巴),相依回歸的紅字面用的是它,所以兩個都要回。聚合、印出、跑不起來時的處理都留在三個呼叫端,不進共用函式;三處印出來的字面不變。`per_prof` 照呼叫端現在的取法(從 `load_platforms` 的平台設定取 profile 名),`loose_for` 從 `_platform_test_index` 的回傳取——解構它要剛好六個值(既有守衛測試 `t_platform_index_consumers_drift_guard` 會檢查)。修正關卡在樹裡自己取。
- **測試名解析成平台與方法、判在不在索引裡**:從 `_bound_tests_for_diff` 把「`[test:名]` → `resolve_test_refs` → 白名單 → 索引裡有沒有(real/fake/dangling)」那段抽成共用函式,推送前合約測試閘與修正關卡第 3 項都用它;推送前那道閘的判定不變。

### `lumos loop next` 的提醒與記帳範本

- 代碼審迴圈、審查帳最新一輪的載體席有要修正紀錄的折入發現,而且治理帳找不到符合下列全部條件的 `fix-check` 事件 → 在輸出加一行提醒與要敲的指令(編號與輪次照 shell 規則加引號;`--json` 多一個 `fix_check` 欄位):kind `passed` 或 `skipped-env`(跳過也算處理過,印一行「這輪修正關卡已跳過」而不是提醒)、`loop` 與 `round` 相同、`passed` 的還要 `record_sha256` 等於現在那份修正紀錄檔的 sha256、事件的 `head_sha` 是 40 碼十六進位(不是就當作無效——治理帳可以被手寫,型別不對不能讓它當掉)而且 `_codeloop_record_valid_ex(repo, 事件的 head_sha, 現在的 HEAD)` 判有效(同一個提交,或是祖先而且中間只動了簿記檔——跟代碼審留痕失不失效同一套;判不了也當作無效)。不管這次判到哪個狀態都印,到上限那條路尤其要印(最後一輪的修補沒有下一輪審查會看到)。修正紀錄檔不存在也印,附 `--record-template` 指令。提醒行印在 `[cap-hint]` 那段之前;`--json` 的 `fix_check` 欄位形狀:`{"status": "needed"|"passed"|"skipped", "round": 輪次, "cmd": 要敲的指令}`(沒有要修正紀錄的折入時不出這個欄位)。「這一輪有沒有要修正紀錄的折入」跟 `fix-check` 用同一支函式判。
- 第 2 輪起,`loop next` 給的載體席記帳範本(`disposal_cmd`,只在 `--json` 輸出裡)多帶 `--regression-set <id串|none>`。既有測試 `t_loop_next_disposal_cmd_actually_runs` 只跑第 1 輪、碰不到這個佔位,所以另寫一支:先記第 1 輪、取第 2 輪範本、填 `none`、真跑要成功(S8)。提醒行本身文字模式與 `--json` 兩條輸出都要接(文字模式只印選定的鍵)。
- 狀態、回傳碼都不變;設計審迴圈不印。
- 讀治理帳:新寫一支讀函式,以位元組逐行預篩含 `"fix-check"` 的行,留下的行接起來整批交給 `_drift_jsonl_parse`(它吃整份位元組、壞行自己跳過)(本 repo 治理帳約 16MB,預篩掃一遍約 0.1 秒,第 1 輪審查量)。

### `canary record --regression-set`

- 載體席選填 `--regression-set <id 串|none>`:這輪的發現裡,編排者判斷是上一輪修補造成的;`none`=判過、沒有(`--folded-set` 沒有 `none` 這個值,這裡要自己認;照 `--refuted-set` 的寫法去空白、轉小寫後比)。其餘解析照 `--folded-set`;空字串、只有逗號或空白(解析後是空的)回 2;重複的 id 去重;id 都要在 `--findings-set` 裡,否則回 2;沒帶 `--findings-set` 的那筆帶了回 2(加進 `cmd_canary` 那串「要跟 `--findings-set` 一起給」的旗標);沒帶 `--loop` 時回 2;審查帳上這個迴圈沒有別的輪次(同一輪先記的席位列不算)、卻帶了非空清單,回 2。存成排過序的 `regression_set`(`none` 存空清單)。由編排者標,辯方不推翻。
- 不加進 `--finding-kind`:那欄量「流程自產工作量」,上一輪修補造成的發現也是程式缺陷,混進去會弄壞那個量。
- 欄位說明寫進 [[Systems/finding-refute]](同族欄位都在那篇)。

### 上線

- 一個功能提交、走代碼審。只提醒不擋;轉成擋、要不要做「先紅」,看 REVISIT 的數字再開改動。

## 條款

- [S1] 當這一輪載體席折入了一條 `code` 類(或沒記類別)的發現、修正紀錄的各組都沒收它時,`loop fix-check` 應回 1 並寫出那條發現的 id;類別不在固定清單、`fixed` 路徑沒有測試或測試名是空白、`unaffected` 路徑沒有理由、`at` 的函式段是空的或找不到、`fixed` 的檔在 `base..修正後` 沒改過(含中文檔名)、`at` 的檔是資料夾或符號連結或含 `..`、測試名含 `]` 或空白,也應各自回 1 並寫出是哪一組哪一條;`fixed` 的檔在修正後已刪掉時應不驗函式段;同一次有多項不過時應全部列出;折入的發現記成 `spec`、`process` 類時應不要求落在組裡 [test:t_fix_check_record_complete]
- [S2] 當迴圈不是 `code-` 開頭、迴圈編號或輪次含 `/` 或 `..`、修正紀錄不是合法 JSON 或超過大小上限、`base` 轉不成存在的提交(含以 `-` 開頭的字串)、有平台根寫成絕對路徑或 repo 外的相對路徑、或有平台資料夾沒進版控時,`loop fix-check` 應回 2、不寫治理帳事件;主工作目錄有沒提交的改動時應照常驗、印提醒列出那幾支 [test:t_fix_check_bad_input]
- [S3] 當紀錄裡的測試名在樹的測試索引裡找不到(只在原始碼文字裡出現也算)時,`loop fix-check` 應回 1 並寫出那支測試名 [test:t_fix_check_test_must_exist]
- [S4] 當紀錄裡一支測試在修正後是紅的時,`loop fix-check` 應回 1 並寫出那支測試;紀錄寫 `t_fcdemo`、程式裡還有一支 `t_fcdemo_strip` 時應回 1 並附「篩選匹配到」的原因;同一支測試的多組輸入應不算撞名;平台的 `run_cmd` 沒有 `{method}` 時應判不過;第 3 項判不存在的測試應不再送去跑;全部綠時這項應過;多平台設定(平台根是子資料夾)時判法應一樣;跑完 `git worktree list` 應沒有殘留、主工作目錄除了治理帳之外 `git status` 應不變 [test:t_fix_check_listed_tests_green]
- [S5] 當 `base..修正後` 改到一篇帶 ★INVARIANT★ 合約的節點牽連的檔、而那條合約綁的測試在修正後是紅的時,`loop fix-check` 應回 1 並寫出那支測試名;那支測試綠時這項應過;`LUMOS_SKIP_BOUND_TESTS=1` 時這項應判不過;合約測試閘回 `green` 但有平台沒設 `run_cmd` 沒跑、或回 `no-config` 時這項應判不過;`base..修正後` 有程式檔改名時應只印提醒、不因此判不過 [test:t_fix_check_bound_tests_green]
- [S6] 當前一輪修正紀錄有一組類別 C、這一輪也有一組類別 C、收的發現裡有一條 `finding_severities` 記 major、卻沒寫 `prior.why_failed` 與 `prior.new_approach` 時,`loop fix-check` 應回 1;兩欄都寫了(各至少十個字)時這項應過;沒記個別嚴重度、而這一輪各席宣告的最高只到 minor 時應不要求;兩組都是 `other` 時應不要求 [test:t_fix_check_repeat_category_needs_why]
- [S7] 每次 `fix-check` 驗完(過或不過)應在治理帳寫恰好一筆閘名 `fix-check`、kind `passed` 或 `warned`、`hard` 為 false 的事件,帶 `loop`、`round`、`record_sha256`、修正後的 40 碼、`secs`、`token`;同一個提交連跑兩次,`lumos gov` 應讀出兩筆;加了新欄位型別之後,`lumos gov` 讀既有各本帳的筆數應跟加之前一樣;`LUMOS_SKIP_FIX_CHECK=1` 時應回 0 並記一筆 `skipped-env`;要修正紀錄的折入是 0 條、或回 2 時應不寫事件;沒有 `docs/` 時應印「這次結果沒記到帳」 [test:t_fix_check_gov_event]
- [S8] 當代碼審迴圈審查帳最新一輪有要修正紀錄的折入、而治理帳沒有符合條件的 `passed` 事件時,`loop next` 應印一行提醒並附 `lumos loop fix-check` 指令——`plant-canary`、`gate-pending`、`converged`、`cap-reached` 都應印(`escalate` 只在 light 分級出現,而 light 帶輪次會被拒,所以碰不到);事件是 `warned`、`record_sha256` 跟現檔不同、`head_sha` 不是 40 碼十六進位、或事件之後的提交動了程式時也應印;事件之後只提交了審查帳時應不印;有同輪的 `skipped-env` 事件時應改印「已跳過」;狀態與回傳碼應跟沒有這段時一樣;設計審迴圈應不印;`--json` 的 `fix_check` 欄位應是 `status`/`round`/`cmd` 三鍵;第 2 輪起的記帳範本應含 `--regression-set`,填 `none` 後真跑應成功 [test:t_loop_next_fix_check_reminder]
- [S9] 當 `canary record` 的 `--regression-set` 帶了不在 `--findings-set` 裡的 id、在沒帶 `--findings-set` 的那筆帶、在迴圈第一輪帶非空清單、帶空字串或只有逗號、或沒帶 `--loop` 時,應回 2;合法時審查帳應存排過序、去重的 `regression_set`,`none`(大小寫不拘)存空清單 [test:t_canary_regression_set]
- [S10] 當派工單有合法的 `base_commit` 時,`fix-check --record-template` 應把含這一輪每條要修正紀錄的折入發現、`base` 帶入的骨架 JSON 印到標準輸出,提示只在標準錯誤,不寫任何檔;派工單沒有或壞掉時 `base` 應留空並在標準錯誤說明 [test:t_fix_check_record_template]
- [S11] 當共用工作樹函式的 `worktree add` 失敗時,它應不丟例外、回傳原因,guard kill 應照舊記成 error 並繼續下一個平台;多平台時 guard kill 應在平台根下建樹、測試在樹的最上層跑,跟抽函式之前一樣;`fix-check` 一開始應清掉修正關卡前綴、超過一天的殘骸工作樹,不到一天的與別的前綴的應不動 [test:t_isolated_worktree_shared]
- [S12] 當主工作目錄有 `.lumos/config.json`、樹裡沒有時,`fix-check` 應複製一份進樹並說明;主工作目錄那份有沒提交的改動時應用提交裡那份並說明;沒設 `fix_check.link_deps` 時樹裡應沒有連回主工作目錄的依賴資料夾,設了時應有並印警告;規格閘三處改用抽出來的「一批測試逐支判」、推送前合約測試閘改用抽出來的「測試名解析」之後,它們印出來的字面與判定(含相依回歸的紅附失敗細節)應跟抽之前一樣 [test:t_fix_check_tree_setup]

## 回退

- revert 這個功能提交:指令與提醒消失;guard kill、規格閘回到各自原本的寫法(行為一樣);審查帳的 `regression_set` 欄、治理帳的 `fix-check` 事件、派工單的 `base_commit` 欄留著,讀端不認得就略過(帳本只追加)。
- revert 之後本計劃條款綁的 `[test:]` 會懸空,status 改 superseded 或在〈實作紀錄〉記一句「已撤回」。

## 實務隱患

- **抓不到的東西**:本步只驗「修正後是綠的」,不驗「修之前是紅的」——一支根本沒碰到修正的弱測試照樣過。這是拆小時接受的代價;REVISIT 那天數「通過之後下一輪仍有上一輪修補造成的發現」就是在量它。
- **時間**:紀錄裡的測試一支幾秒(本 repo `-k` 實測約 2.7 秒)、建樹約 2 秒,受波及合約測試在樹裡實測 59 支 258 秒;一次大約 5 分鐘,多半花在合約測試。
- **讀不出支數的棧**:只有 python 的輸出讀得出支數;其他棧的綠照退出碼與過濾探針判(同規格閘),擋不到「名字選中多支」。
- **依賴資料夾**:預設不連,需要依賴的專案(Node、用虛擬環境的 Python)要設 `fix_check.link_deps: true`;設了之後樹裡的測試會用主工作目錄的依賴,Node 多套件專案的其他套件、Python 可編輯安裝會載到主工作目錄的程式,沒提交的修正可能讓樹裡的測試變綠(第 0 步第 1 輪實測)——輸出會警告。第一個設了 `link_deps` 的專案跑修正關卡時(看它的治理帳事件),在那次的紀錄裡實測一次載到的是哪一份。
- **殘骸**:被強殺(Ctrl-C 也算——`_kill_run` 現在被中斷時不砍子行程)的那次會留樹與孤兒子行程;樹在下一次一天後被清,孤兒子行程跑完自己結束。`_kill_run` 被中斷不收子行程是既有行為(合約測試閘、guard kill 都一樣),另開 Issue。
- **之後有沒有改程式**:沿用代碼審留痕那套,所以 `fix-check` 之後只要提交了簿記檔以外的任何檔(含圖譜筆記),`loop next` 就會再提醒——跟代碼審留痕失效的口徑一樣,寧多提醒。
- **派工時有沒提交的改動**:`base` 是派工當下的提交;那時工作目錄若還有沒提交的修改、之後才提交,`base..修正後` 會把它們也算進來(受波及合約測試多跑一些,方向保守)。手冊第 2 步寫「派工前先提交」。
- **跨 repo 或沒進版控的平台**:平台根在 repo 外、寫成絕對路徑、或平台資料夾沒進版控的專案本步直接回 2,不支援(要消提醒只能用 `LUMOS_SKIP_FIX_CHECK`,會被記成跳過);第一個要用修正關卡的多根專案出現時(看治理帳有沒有這種回 2 的紀錄——回 2 不記帳,所以靠使用者回報),再看要不要對每個平台根各建一棵樹。
- **紀錄寫錯的代價**:`fixed` 列了沒改過的檔、測試名寫錯,都判不過(失敗方向是擋)。
- **共用函式動到 guard kill、規格閘與推送前合約測試閘**:只搬、不改行為;先補行為測試再搬,`-k guard_kill`(實測約 5 分鐘)、`-k spec_gate`、`-k bound_tests` 子集當回歸。
- **既有測試**:`loop next` 輸出字面有測試釘著;`t_platform_index_consumers_drift_guard` 檢查 `_platform_test_index` 的回傳解構;新子指令要有「什麼時候用」說明、要進指令索引;治理帳讀端改動要跑 `-k gov`;`_KNOWN_GATES` 漏登記沒有測試會紅,S7 直接驗事件寫進去了。
- **要同步的文件**:lumos-code-loop 手冊 `SKILL.md` 與 `reference.md` 裡那份步驟 1–8 都要改——第 2 步(派工前先提交、派工單寫 `base_commit`)、第 5 步(修完先提交、寫修正紀錄,可用 `--record-template`)、第 6 步(第 2 輪起帶 `--regression-set`、建議帶 `--finding-kind`)、第 7 步之後(問閘過、派下一輪前跑 `lumos loop fix-check`,在背景跑或把指令逾時設 10 分鐘;到上限要推前也跑;跟「收斂前派全新席掃 delta」並列);`SKILL.md` 不加日期(`t_skill_entry_pages_no_dated_history` 會擋);指令速查第 06 子檔與 INDEX 的代碼審那一列;新開 [[Systems/代碼審修正關卡]];[[Systems/guard-kill]]、[[Systems/規格閘]] 補共用函式;[[Systems/loop-convergence-recording]] 補 `loop next` 提醒;[[Systems/finding-refute]] 補 `regression_set`;開三篇 Issue(改名漏算、`skipped` 字樣誤判、`_kill_run` 被中斷不收子行程)。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只在本機跑測試與讀寫帳本,不連網
- 已排除:不可逆:隔離工作樹跑完就收、殘骸下一次清;帳本只追加;revert 回得去
- 守衛面:新增一道只提醒不擋的檢查;轉成擋另開改動、另審。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- r1(2026-10-02,4 席:正確性 opus、邊界、整合、架構對齊 sonnet):32 條/blocking 11/見 r1-intake.md。
  - 樹與主工作目錄不一致:先決條件與逐項驗全部讀樹裡那份設定;平台根寫成絕對路徑、在 repo 外、沒進版控都回 2(例:平台根寫絕對路徑 → 原稿在主工作目錄跑、提交版紅也判綠,改後回 2,S2)。
  - 依賴資料夾改成預設不連、設 `link_deps` 才連並警告(例:Node 多套件 → 原稿載到主工作目錄的程式,S12);樹一律用 `Path` 傳、條款補多平台(例:多平台傳字串 → 原稿丟例外,S4)。
  - 規格閘第三份副本 `_spec_gate_push_one` 一起抽;測試名解析從 `_bound_tests_for_diff` 抽共用;改名只提醒不判不過(例:純改名 → 原稿永遠過不了,S5);`escalate` 碰不到從 S8 拿掉;第 2 輪範本另寫真跑測試;手冊寫背景跑或拉長逾時。
- 前掃(2026-10-02):四類都有命中,全部改進真檔;語意類的修改前→後記在 `governance/review-reports/代碼審修正關卡第0步/r1-intake.md`,其中 2 條動到做法(規格閘共用函式的介面要帶 `per_prof`/`loose_for` 與原始失敗尾巴;平台根在 repo 外不支援)。
