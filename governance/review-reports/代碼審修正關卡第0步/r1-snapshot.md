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
- **一支測試的判法**:規格閘那套——`_run_bound_tests` 逐支真跑,`_ran_count` 讀篩到幾個案例,`_spec_gate_declared` 數程式裡宣告了幾支名字含這個字串的測試,`_spec_gate_verdict` 判紅、綠或弱證據(篩選選到好幾支不同的測試、被跳過、一支都沒跑到都是弱證據;同一支測試的多組輸入不算撞名)。
- **理由夠不夠**:去掉前後空白後至少 `_MANUAL_MIN_CHARS`(4)個字、至少含一個不是標點也不是底線的字(同 `--refuted-set` 的理由判法)。
- **程式檔**:`_nodehome_code_kind` 回的不是 `None` 就算(沒副檔名、要看首行的也算,寧多判)。
- **受波及合約測試**:`base..修正後` 改到的檔所牽連的、帶 ★INVARIANT★ 合約的節點,其合約行綁的測試;算法與判法是推送前合約測試閘那套([[Systems/bound-tests-gate]])。

## 範圍

- 做:修正紀錄格式與樣板;派工單記 `base_commit`;`lumos loop fix-check` 驗五件事(紀錄完整、同類連兩輪要寫為什麼、測試存在、紀錄裡的測試在修正後是綠的、受波及合約測試全綠);每次跑記治理帳(讀端吐 `token` 與新欄位);`lumos loop next` 提醒、第 2 輪起的記帳範本帶 `--regression-set`;`lumos canary record` 載體席選填 `--regression-set`;guard kill 建、收隔離工作樹那段抽成共用函式;規格閘「跑一批測試再逐支判」那段抽成共用函式。
- 不做:先紅(把修正拿掉看測試會不會紅)、壓力指令、決策備忘錄底稿、doctor 提醒、`gov --stats` 段——都留在 [[Projects/代碼審修正關卡_計劃]],看本步數據再決定;不擋派工、不改處置閘;設計審迴圈不適用;不改 `_kill_run`(被 Ctrl-C 時子行程會變孤兒是既有行為,另開 Issue);不修 `impact --diff` 純改名只算新路徑、`_ran_count` 把失敗訊息裡的 `1 skipped` 字樣當跳過這兩個既有洞(各開 Issue)。

## 做法

### 修正紀錄(每輪一份)

- 位置固定:`governance/review-reports/<迴圈編號>/<輪>-fix.json`(`<輪>` 是審查帳上那一輪的 `round` 字串;不解析數字;不提供指到別處的旗標)。
- 派工單多一個頂層欄位 `base_commit`:派工當下 `git rev-parse HEAD` 的 40 碼(手冊第 2 步寫派工單時一起寫)。讀派工單的既有函式(`_roster_dispatch_entries`、`cmd_seat_check`)只讀自己認得的鍵,多一欄不影響(第 3 輪審查讀過)。只讀字面那一份 `<輪>-dispatch.json`(同一輪另外的 `<輪>-dispatch-*.json` 不看);頂層是物件(單席物件或帶 `seats` 的物件)才讀它的 `base_commit`,頂層是陣列一律當作沒有。
- 樣板:`lumos loop fix-check <迴圈編號> --round <輪> --record-template`(命名照 `--dispositions-template`):骨架 JSON 印到標準輸出、提示印到標準錯誤,不寫檔;`base` 從 `<輪>-dispatch.json` 的 `base_commit` 帶入(沒有、讀不懂、不是 40 碼十六進位都留空並在標準錯誤說一句);這輪要修正紀錄的折入發現各列一組待填。只要求迴圈與輪次存在。
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
- `at` 寫「檔案:函式」,在第一個冒號切開,函式那段不能是空的。`fixed` 的檔必須在 `base..修正後` 之間有改動(`git diff --no-renames --name-only -z`,中文與空白檔名照原樣比);修正後還在的檔,函式那段要在那支檔裡出現、前後不接英數字或底線;修正後已刪掉的檔不驗函式段。`unaffected` 的檔要在修正後的提交裡、函式段要找得到。不驗它真的是函式定義(各棧寫法不同,驗到字面就停)。

### `lumos loop fix-check <迴圈編號> --round <輪> [--repo <根>] [--json]`

名字:頂層的 `fold-check` 已經是設計審「折完看前後矛盾」的指令,所以放在 `loop` 底下叫 `fix-check`。`--repo` 照 `loop status` 的寫法。

執行順序(便宜的先做,失敗就不必建樹):①便宜的先決條件 → ②記下 `HEAD` 的 40 碼當**修正後** → ③清殘骸 → ④建樹與樹的準備 → ⑤逐項驗 → ⑥記帳、收樹。`--record-template` 只做①裡的「迴圈與輪次存在」,不建樹。

先決條件(任一不成立回 2、印原因、不寫治理帳事件):
- 迴圈編號是 `code-` 開頭;迴圈編號與輪次都不含 `/`、`\`、`..`、控制字元(要拼進檔名);審查帳找得到這一輪的載體席。要修正紀錄的折入發現是 0 條 → 印「這輪沒有要修正紀錄的折入,不用跑」回 0、不寫事件。
- 修正紀錄讀得到、是合法 JSON(解析深度過深、形狀不對都回 2)、`base` 轉得成存在的提交。
- 每個平台的平台根(`load_platforms` 解析後)都在 repo 頂底下;有平台根在 repo 外(例如設定寫 `../別的專案`)→ 回 2,說明是哪個平台——那種平台的路徑在樹裡解析不到,測試會跑到別處或跑不起來,本步不支援。
- 樹建得起來(建不起來回 2,附 git 的原因)。

清殘骸:系統暫存資料夾裡修正關卡前綴、超過一天的殘骸(寫法照 `_lint_new_clean_stale`,時限沿用 `_LINT_NEW_STALE_SEC`;是工作樹的先 `git worktree remove --force` 再刪資料夾,最後 `git worktree prune`;比對前兩邊路徑都先取實際路徑——macOS 的 `/var` 與 `/private/var` 是同一個)。

建樹:用共用函式在系統暫存資料夾建一棵檢出修正後的隔離工作樹(下稱**樹**),整次的測試都在樹裡跑,跑完一定收掉;主工作目錄只讀審查帳、治理帳、派工單與修正紀錄,跑的期間別的會談改檔、提交都不影響這次結果。

樹的準備:
- 依賴資料夾:repo 頂與每個平台根各用 `_lint_link_deps` 把 `node_modules`、`.venv`、`venv` 連回主工作目錄的同一位置(那些不進版控,樹裡沒有會整個跑不起來;寫法照新增告警閘)。
- 設定檔:主工作目錄有 `.lumos/config.json`、樹裡沒有(設定檔沒進版控,本機 18 個專案裡有 2 個是這樣,第 3 輪審查數過)時,直接複製那一份進樹的同一位置,輸出說一句。

只印提醒、不擋:主工作目錄有已受版控的改動沒提交(`git status --porcelain -z`,改名條目兩個路徑都列)→ 印「這次驗的是提交裡的版本,工作目錄這幾支沒提交的改動不算」列前幾支(同一個 repo 常有別的會談的改動,所以不擋;修正忘了提交時,`fixed` 的檔多半會判「沒改動」)。

逐項驗(任一不過整次回 1;能驗的都驗完再一起印,寫明哪一項、哪一組哪一條、怎麼修):
1. **紀錄完整**:要修正紀錄的折入發現每條都落在某一組;組裡的發現都在這輪的發現清單裡;類別在固定清單裡,`other` 有 `note`;每組至少一條 `fixed` 路徑;每條 `fixed` 至少一支測試,測試名去掉前後空白後不能是空的;每條 `unaffected` 有理由(判法同 `[manual:]`);`at` 照上面那段驗。
2. **同類連兩輪**:審查帳上這一輪的前一輪(照帳上輪次出現的順序)有修正紀錄、其中有一組跟這組同類別,而且這組收的發現裡有任一條嚴重度 ≥ major,這組就必須有 `prior.why_failed` 與 `prior.new_approach`(各至少十個字)。個別嚴重度看 `finding_severities`;沒記的那條改看這一輪各席宣告的最高嚴重度。
3. **測試存在**:判法跟推送前合約測試閘算受波及測試時同一套(`_bound_tests_for_diff` 那段):每支測試名包成 `[test:名]` 交給 `resolve_test_refs`(它丟 `ValueError` 時接住,這支判不過並附原因),要恰好解析出一支、方法名過 `_KILL_METHOD_OK_RE` 白名單、而且在樹的測試索引裡找得到(`_platform_test_index(樹)`,`Class.Method` 寫法照那段的處理);只在原始碼文字裡出現、或找不到的都算不過。
4. **紀錄裡的測試在修正後是綠的**:第 3 項判存在的那幾支(去重;第 3 項不過的不送,免得同一支被報兩次)用規格閘抽出來的共用函式(見下)在樹裡跑,每支判綠才過;判紅、弱證據(附規格閘給的原因,例:「篩選匹配到 2 支,測試名要唯一」)都不過;平台的 `run_cmd` 沒有 `{method}`(只能整套跑)時這個平台的測試不跑、判不過並說明(規格閘遇到這種是整批略過;這裡要的是「這幾支是綠的」,證不了就是不過)。
5. **受波及合約測試全綠**:`_bound_tests_check(Path(樹), "base..修正後")`(推送前那道閘的同一支,含過濾探針;它寫的治理帳事件與測試快取落在樹裡、跟著刪掉;過濾探針另有一份放在使用者家目錄的快取,鍵含樹的路徑,所以讀不出支數的棧每次會重探一次,接受)。`green`、`no-pins`、`no-bound`、`no-vault` 過,後三種印說明——但回 `green` 而它的結果裡有平台因為沒設 `run_cmd` 沒跑的,不過(說明哪個平台的合約測試沒跑);`red`、`unfilterable`、`no-config`、`diff-unavailable`、`range-unavailable`、`whole-suite-deferred` 不過;`skipped`(有人設了 `LUMOS_SKIP_BOUND_TESTS`)也不過,印「要跳過整道修正關卡請用 `LUMOS_SKIP_FIX_CHECK`」。`base..修正後` 有程式檔被改名時(`git diff -M --name-status -z` 的改名條目,判程式檔用 `_nodehome_code_kind`)這項也判不過,印「改名的檔,舊路徑牽連的合約沒算到」。

另外(只印):這一輪不是第一輪、載體席沒有 `regression_set` 這個欄位(看欄位在不在,空清單=判過沒有)→ 印一行提醒下一輪記帳時要帶。

記帳與跳過:
- 跑完逐項驗(過或不過)用 `_gate_event_or_warn` 寫一筆治理帳:閘名 `fix-check`(加進 `_KNOWN_GATES`)、`hard=False`、kind 過 `passed`、不過 `warned`(不擋的閘的用字)、跳過 `skipped-env`;`head_sha`=修正後的 40 碼;`extra` 放 `loop`、`round`(名稱與型別同審查帳)、`record_sha256`、`secs`(浮點)、`failed_items`(不過的項目代號清單)、`token`(每次跑的隨機碼)。
- 治理帳讀端(`cmd_gov` 的轉換)對 `fix-check` 事件吐出 `token` 與上面這些欄位(去重鍵本來就含 `token`,轉換沒吐它,同一個提交連跑兩次同結果會被折成一筆);`_GOV_FIELD_TYPES` 補 `record_sha256`、`secs`(整數與浮點)、`failed_items`、`head_sha`——第 2 輪審查掃過三本帳沒有型別衝突,實作時加之前再掃一次,不得讓任何既有行從型別對變成型別不對。
- `_gate_event_or_warn` 的 `note` 放一句結果摘要(過幾項、不過哪幾項)。它回的不是 `True` 時(沒有 `docs/` 回 `None` 而且不印;寫入失敗回 `False` 並印警告),輸出另加一句「這次結果沒記到帳,`loop next` 會一直提醒」。
- `LUMOS_SKIP_FIX_CHECK=1`:不驗、回 0、記一筆 kind `skipped-env`。

### 共用函式(兩支)

- **隔離工作樹**:把 `cmd_guard_kill` 裡「暫存資料夾 + `git -C <在哪建> worktree add --detach <路徑> [<提交>]` + finally 收掉(`worktree remove --force`、刪資料夾、`worktree prune`)」抽成 with 區塊用的共用函式,參數:在哪建(`git -C` 的目錄)、檢出哪個提交(空的就不帶)、資料夾前綴、要不要保留;給出 (樹的路徑或空, 失敗原因)——`worktree add` 失敗時不丟例外,原因照 guard kill 現在的截法(標準錯誤去頭尾空白取前 120 字)。內部管兩層:暫存資料夾與它底下的樹;要保留時兩層都留、只印路徑(照 guard kill 現在 `--keep-worktree` 的行為)。guard kill 照現在的寫法傳平台根、測試在樹的最上層跑、失敗記成 error 繼續下一個平台、`--keep-worktree` 時保留並印路徑——行為一點不改。抽之前先補兩條現在沒被測試釘住的行為(`worktree add` 失敗、多平台時在哪建樹與在哪跑測試),先綠、抽完照綠。
- **一批測試逐支判**:規格閘的條款測試與相依回歸兩處,都是「`_run_bound_tests` 跑一批 → 每支用 `_ran_count`、`_spec_gate_declared`、`_spec_gate_verdict` 判」,手寫了兩份。抽成一支 `_spec_gate_judge_items(根, 測試清單, per_prof, loose_for)`,回 (逐支結果, 跑不起來的原因)——逐支結果帶 (編號, 平台, 方法, 紅綠弱, 原因, `_run_bound_tests` 給的原始失敗尾巴);相依回歸的紅字面用的是原始失敗尾巴,不是原因,所以兩個都要回。「同條款多支測試任一非綠蓋過綠」、「印出來」、「跑不起來時一個印略過一個記進失敗」都留在兩個呼叫端,不進共用函式。修正關卡在樹裡自己用 `load_platforms(樹)` 與 `_platform_test_index(樹)` 取 `per_prof`、`loose_for`。規格閘印出來的字面不變。

### `lumos loop next` 的提醒與記帳範本

- 代碼審迴圈、審查帳最新一輪的載體席有要修正紀錄的折入發現,而且治理帳找不到符合下列全部條件的 `fix-check` 事件 → 在輸出加一行提醒與要敲的指令(編號與輪次照 shell 規則加引號;`--json` 多一個 `fix_check` 欄位):kind `passed` 或 `skipped-env`(跳過也算處理過,印一行「這輪修正關卡已跳過」而不是提醒)、`loop` 與 `round` 相同、`passed` 的還要 `record_sha256` 等於現在那份修正紀錄檔的 sha256、事件的 `head_sha` 是 40 碼十六進位(不是就當作無效——治理帳可以被手寫,型別不對不能讓它當掉)而且 `_codeloop_record_valid_ex(repo, 事件的 head_sha, 現在的 HEAD)` 判有效(同一個提交,或是祖先而且中間只動了簿記檔——跟代碼審留痕失不失效同一套;判不了也當作無效)。不管這次判到哪個狀態都印,到上限那條路尤其要印(最後一輪的修補沒有下一輪審查會看到)。修正紀錄檔不存在也印,附 `--record-template` 指令。
- 第 2 輪起,`loop next` 給的載體席記帳範本(`disposal_cmd`,只在 `--json` 輸出裡)多帶 `--regression-set <id串|none>`;既有測試 `t_loop_next_disposal_cmd_actually_runs` 會把範本填值後真跑,要同步給這個佔位填值。提醒行本身文字模式與 `--json` 兩條輸出都要接(文字模式只印選定的鍵)。
- 狀態、回傳碼都不變;設計審迴圈不印。
- 讀治理帳:新寫一支讀函式,以位元組逐行預篩含 `"fix-check"` 的行,留下的行接起來整批交給 `_drift_jsonl_parse`(它吃整份位元組、壞行自己跳過)(本 repo 治理帳約 16MB,預篩掃一遍約 0.1 秒,第 1 輪審查量)。

### `canary record --regression-set`

- 載體席選填 `--regression-set <id 串|none>`:這輪的發現裡,編排者判斷是上一輪修補造成的;`none`=判過、沒有(`--folded-set` 沒有 `none` 這個值,這裡要自己認;只認小寫 `none`)。其餘解析照 `--folded-set`;空字串回 2;id 都要在 `--findings-set` 裡,否則回 2;沒帶 `--findings-set` 的那筆帶了回 2(加進 `cmd_canary` 那串「要跟 `--findings-set` 一起給」的旗標);沒帶 `--loop` 時回 2;審查帳上這個迴圈沒有別的輪次(同一輪先記的席位列不算)、卻帶了非空清單,回 2。存成排過序的 `regression_set`(`none` 存空清單)。由編排者標,辯方不推翻。
- 不加進 `--finding-kind`:那欄量「流程自產工作量」,上一輪修補造成的發現也是程式缺陷,混進去會弄壞那個量。
- 欄位說明寫進 [[Systems/finding-refute]](同族欄位都在那篇)。

### 上線

- 一個功能提交、走代碼審。只提醒不擋;轉成擋、要不要做「先紅」,看 REVISIT 的數字再開改動。

## 條款

- [S1] 當這一輪載體席折入了一條 `code` 類(或沒記類別)的發現、修正紀錄的各組都沒收它時,`loop fix-check` 應回 1 並寫出那條發現的 id;類別不在固定清單、`fixed` 路徑沒有測試或測試名是空白、`unaffected` 路徑沒有理由、`at` 的函式段是空的或找不到、`fixed` 的檔在 `base..修正後` 沒改過(含中文檔名),也應各自回 1 並寫出是哪一組哪一條;`fixed` 的檔在修正後已刪掉時應不驗函式段;同一次有多項不過時應全部列出;折入的發現記成 `spec`、`process` 類時應不要求落在組裡 [test:t_fix_check_record_complete]
- [S2] 當迴圈不是 `code-` 開頭、迴圈編號或輪次含 `/` 或 `..`、修正紀錄不是合法 JSON、`base` 轉不成存在的提交(含以 `-` 開頭的字串)、或有平台根在 repo 外時,`loop fix-check` 應回 2、不寫治理帳事件;主工作目錄有沒提交的改動時應照常驗、印提醒列出那幾支 [test:t_fix_check_bad_input]
- [S3] 當紀錄裡的測試名在樹的測試索引裡找不到(只在原始碼文字裡出現也算)時,`loop fix-check` 應回 1 並寫出那支測試名 [test:t_fix_check_test_must_exist]
- [S4] 當紀錄裡一支測試在修正後是紅的時,`loop fix-check` 應回 1 並寫出那支測試;紀錄寫 `t_fcdemo`、程式裡還有一支 `t_fcdemo_strip` 時應回 1 並附「篩選匹配到」的原因;同一支測試的多組輸入應不算撞名;平台的 `run_cmd` 沒有 `{method}` 時應判不過;第 3 項判不存在的測試應不再送去跑;全部綠時這項應過;跑完 `git worktree list` 應沒有殘留、主工作目錄除了治理帳之外 `git status` 應不變 [test:t_fix_check_listed_tests_green]
- [S5] 當 `base..修正後` 改到一篇帶 ★INVARIANT★ 合約的節點牽連的檔、而那條合約綁的測試在修正後是紅的時,`loop fix-check` 應回 1 並寫出那支測試名;那支測試綠時這項應過;`LUMOS_SKIP_BOUND_TESTS=1` 時這項應判不過;合約測試閘回 `green` 但有平台沒設 `run_cmd` 沒跑時這項應判不過;`base..修正後` 有程式檔改名時這項應判不過 [test:t_fix_check_bound_tests_green]
- [S6] 當前一輪修正紀錄有一組類別 C、這一輪也有一組類別 C、收的發現裡有一條 `finding_severities` 記 major、卻沒寫 `prior.why_failed` 與 `prior.new_approach` 時,`loop fix-check` 應回 1;兩欄都寫了(各至少十個字)時這項應過;沒記個別嚴重度、而這一輪各席宣告的最高只到 minor 時應不要求 [test:t_fix_check_repeat_category_needs_why]
- [S7] 每次 `fix-check` 驗完(過或不過)應在治理帳寫恰好一筆閘名 `fix-check`、kind `passed` 或 `warned`、`hard` 為 false 的事件,帶 `loop`、`round`、`record_sha256`、修正後的 40 碼、`secs`、`token`;同一個提交連跑兩次,`lumos gov` 應讀出兩筆;加了新欄位型別之後,`lumos gov` 讀既有三本帳的筆數應跟加之前一樣;`LUMOS_SKIP_FIX_CHECK=1` 時應回 0 並記一筆 `skipped-env`;要修正紀錄的折入是 0 條、或回 2 時應不寫事件;沒有 `docs/` 時應印「這次結果沒記到帳」 [test:t_fix_check_gov_event]
- [S8] 當代碼審迴圈審查帳最新一輪有要修正紀錄的折入、而治理帳沒有符合條件的 `passed` 事件時,`loop next` 應印一行提醒並附 `lumos loop fix-check` 指令——五個狀態(`plant-canary`、`gate-pending`、`converged`、`cap-reached`、`escalate`)都應印;事件是 `warned`、`record_sha256` 跟現檔不同、`head_sha` 不是 40 碼十六進位、或事件之後的提交動了程式時也應印;事件之後只提交了審查帳時應不印;有同輪的 `skipped-env` 事件時應改印「已跳過」;狀態與回傳碼應跟沒有這段時一樣;設計審迴圈應不印;第 2 輪起的記帳範本應含 `--regression-set` [test:t_loop_next_fix_check_reminder]
- [S9] 當 `canary record` 的 `--regression-set` 帶了不在 `--findings-set` 裡的 id、在沒帶 `--findings-set` 的那筆帶、在迴圈第一輪帶非空清單、或帶空字串時,應回 2;合法時審查帳應存排過序的 `regression_set`,`none` 存空清單 [test:t_canary_regression_set]
- [S10] 當派工單有合法的 `base_commit` 時,`fix-check --record-template` 應把含這一輪每條要修正紀錄的折入發現、`base` 帶入的骨架 JSON 印到標準輸出,提示只在標準錯誤,不寫任何檔;派工單沒有或壞掉時 `base` 應留空並在標準錯誤說明 [test:t_fix_check_record_template]
- [S11] 當共用工作樹函式的 `worktree add` 失敗時,它應不丟例外、回傳原因,guard kill 應照舊記成 error 並繼續下一個平台;多平台時 guard kill 應在平台根下建樹、測試在樹的最上層跑,跟抽函式之前一樣;`fix-check` 一開始應清掉修正關卡前綴、超過一天的殘骸工作樹,不到一天的與別的前綴的應不動 [test:t_isolated_worktree_shared]
- [S12] 當主工作目錄有 `.lumos/config.json`、樹裡沒有時,`fix-check` 應複製一份進樹並說明;規格閘改用抽出來的「一批測試逐支判」之後,它印出來的條款與相依回歸結果字面(含相依回歸的紅附原始失敗尾巴)應跟抽之前一樣 [test:t_fix_check_tree_setup]

## 回退

- revert 這個功能提交:指令與提醒消失;guard kill、規格閘回到各自原本的寫法(行為一樣);審查帳的 `regression_set` 欄、治理帳的 `fix-check` 事件、派工單的 `base_commit` 欄留著,讀端不認得就略過(帳本只追加)。
- revert 之後本計劃條款綁的 `[test:]` 會懸空,status 改 superseded 或在〈實作紀錄〉記一句「已撤回」。

## 實務隱患

- **抓不到的東西**:本步只驗「修正後是綠的」,不驗「修之前是紅的」——一支根本沒碰到修正的弱測試照樣過。這是拆小時接受的代價;REVISIT 那天數「通過之後下一輪仍有上一輪修補造成的發現」就是在量它。
- **時間**:紀錄裡的測試一支幾秒(本 repo `-k` 實測約 2.7 秒)、建樹約 2 秒,受波及合約測試在樹裡實測 59 支 258 秒;一次大約 5 分鐘,多半花在合約測試。
- **讀不出支數的棧**:只有 python 的輸出讀得出支數;其他棧的綠照退出碼與過濾探針判(同規格閘),擋不到「名字選中多支」。
- **依賴資料夾連回主工作目錄**:樹裡的測試會用主工作目錄的依賴;主工作目錄的依賴版本跟提交不一致時,綠的結果跟 CI 可能不同——跟新增告警閘同一個天花板。
- **殘骸**:被強殺(Ctrl-C 也算——`_kill_run` 現在被中斷時不砍子行程)的那次會留樹與孤兒子行程;樹在下一次一天後被清,孤兒子行程跑完自己結束。`_kill_run` 被中斷不收子行程是既有行為(合約測試閘、guard kill 都一樣),另開 Issue。
- **之後有沒有改程式**:沿用代碼審留痕那套,所以 `fix-check` 之後只要提交了簿記檔以外的任何檔(含圖譜筆記),`loop next` 就會再提醒——跟代碼審留痕失效的口徑一樣,寧多提醒。
- **派工時有沒提交的改動**:`base` 是派工當下的提交;那時工作目錄若還有沒提交的修改、之後才提交,`base..修正後` 會把它們也算進來(受波及合約測試多跑一些,方向保守)。手冊第 2 步寫「派工前先提交」。
- **跨 repo 的平台**:平台根在 repo 外的專案(多根設定)本步直接回 2,不支援;第一個要用修正關卡的多根專案出現時(看治理帳有沒有這種回 2 的紀錄——回 2 不記帳,所以靠使用者回報),再看要不要對每個平台根各建一棵樹。
- **紀錄寫錯的代價**:`fixed` 列了沒改過的檔、測試名寫錯,都判不過(失敗方向是擋)。
- **共用函式動到 guard kill 與規格閘**:只搬、不改行為;先補行為測試再搬,`-k guard_kill`、`-k spec_gate` 子集當回歸。
- **既有測試**:`loop next` 輸出字面有測試釘著,`t_loop_next_disposal_cmd_actually_runs` 要給新佔位填值;新子指令要有「什麼時候用」說明、要進指令索引;治理帳讀端改動要跑 `-k gov`;`_KNOWN_GATES` 漏登記沒有測試會紅,S7 直接驗事件寫進去了。
- **要同步的文件**:lumos-code-loop 手冊——第 2 步(派工單寫 `base_commit`)、第 5 步(修完先提交、寫修正紀錄,可用 `--record-template`)、第 6 步(第 2 輪起帶 `--regression-set`、建議帶 `--finding-kind`)、第 7 步之後(問閘過、派下一輪前跑 `lumos loop fix-check`;到上限要推前也跑;跟「收斂前派全新席掃 delta」並列);指令速查第 06 子檔;新開 [[Systems/代碼審修正關卡]];[[Systems/guard-kill]]、[[Systems/規格閘]] 補共用函式;[[Systems/loop-convergence-recording]] 補 `loop next` 提醒;[[Systems/finding-refute]] 補 `regression_set`;開三篇 Issue(改名漏算、`skipped` 字樣誤判、`_kill_run` 被中斷不收子行程)。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只在本機跑測試與讀寫帳本,不連網
- 已排除:不可逆:隔離工作樹跑完就收、殘骸下一次清;帳本只追加;revert 回得去
- 守衛面:新增一道只提醒不擋的檢查;轉成擋另開改動、另審。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- 前掃(2026-10-02):四類都有命中,全部改進真檔;語意類的修改前→後記在 `governance/review-reports/代碼審修正關卡第0步/r1-intake.md`,其中 2 條動到做法(規格閘共用函式的介面要帶 `per_prof`/`loose_for` 與原始失敗尾巴;平台根在 repo 外不支援)。
