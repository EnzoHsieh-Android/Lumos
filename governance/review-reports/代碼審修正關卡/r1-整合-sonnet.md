severity: major

整合-sonnet,鏡頭:整合與接手。以下以「三個月後照這份計劃實作、照手冊操作」的人身分,對照 negguard 快照的真碼查證。

## F1 新欄位 `tests` 的型別會撞上審查帳裡既有的 `tests`(清單),整批規格閘留痕被 gov 靜默丟掉
severity: major
blocking: 是
引句:「`_GOV_FIELD_TYPES` 同步補上新欄位的型別。」
file: `scripts/lumos:7577`
file: `scripts/lumos:7620`
1. 計劃要求 fix-check 事件帶 `tests`(測試支數,整數),並在 `_GOV_FIELD_TYPES` 補型別。這張表是「七本帳共用一張表」:`_gov_event_types_ok` 對每本載入的帳的每一行都套,型別不對整行跳過。
2. 審查帳(`.canary-log.jsonl`,gov 會載入)已有 83 行 `kind: "spec-gate"` 的規格閘留痕,`tests` 是字串清單(例:`"tests": ["t_doctor_escape_by_door", ...]`)。
3. 最小實驗(對 negguard 的 `scripts/lumos` 載入模組,取一行真實形狀的規格閘留痕):
   - 補表之前 `_gov_event_types_ok(row)` = True。
   - 照計劃補 `m._GOV_FIELD_TYPES["tests"]=(int,)` 之後 = False。
   - 實測輸出:`before True` / `after adding tests:(int,) False`。
4. 後果:照字面做,gov 的統計與時間軸會悄悄少掉 83 筆規格閘留痕,而且沒有任何測試會紅(既有 gov 測試不含 tests 欄)。表上註解自己寫了「同名欄位在各帳的意思與型別一樣」,這條計劃違反它。
5. 計劃要改成換名(例:`n_tests`、`n_groups`),或表裡不收型別、讀端用 isinstance 自己取;並在條款 S7 或 S14 加一條「規格閘留痕經 gov 照樣讀得到」的斷言。

## F2 `--regression-set` 是選填、提醒又印在記帳之後,基準量不到;範本與手冊第 6 步都沒列
severity: major
blocking: 是
引句:「這一輪不是第一輪、載體席沒有 `regression_set` 欄 → 印一行提醒」
file: `scripts/lumos:11773`
file: `scripts/lumos:8643`
file: `scripts/lumos:8570`
1. 提醒是由 `fix-check` 印的,而 `fix-check` 一開始就要讀這一輪的載體席(先決條件),也就是這一輪已經記完帳。審查帳只追加、一輪只准一筆載體席(處置閘會擋),載體席記完就補不了 `--regression-set`。所以這句提醒對「這一輪」永遠來不及,只能指望人記得下一輪帶。
2. 下一輪記帳前編排者唯一會看的指令範本是 `cmd_loop_next` 印的 `disposal_cmd`(`--findings-set <id串> --folded-set … --refuted-set none`),計劃沒有說要把 `--regression-set <id串|none>` 加進這個範本;手冊第 6 步(記帳)的旗標清單也沒列在〈要同步的文件〉裡(只列第 5 步)。
3. 同一支函式有前科:`cmd_canary` 載體席段落的註解寫「選填的欄位沒人填(refute_verdicts 0/1216 是前科)」;實測審查帳 315 筆代碼審載體席裡只有 66 筆帶 `finding_severities`(選填、全有或全無)。
4. 計劃的 RETIRE-IF、REVISIT 都以「上一輪修補造成的比例」為轉擋的依據,並寫「帶了 `--regression-set` 的輪不到 5 輪就判基準量不到」。在上述接法下,這個分母很可能長期不夠,整個「前兩週只提醒、量到基準再決定」會落空。
5. 要補:把 `--regression-set` 放進 `disposal_cmd`(與 `record_cmd`)範本、手冊第 6 步、指令速查;fix-check 的那句提醒改成「下一輪記帳要帶」並由 `loop next` 在 plant-canary 時印。

## F3 手冊接線:第 5 步在第 6 步(記帳)之前,fix-check 卻要先有載體席;`base` 沒有任何一步會記下來
severity: major
blocking: 是
引句:「lumos-code-loop 手冊第 5 步(修與釘)加」
引句:「`base`:修正前的提交——通常是這輪凍結材料對應的那個提交。」
file: `skills/lumos-code-loop/SKILL.md:17-47`
1. 手冊順序是 1 凍結 → 5 修與釘 → 6 記帳 → 7 問閘 → 8 過了留痕。計劃把 fix-check 掛在第 5 步文字裡,但 fix-check 的先決條件要求審查帳已有這一輪的載體席(折入清單來自記帳那一步)。照字面在第 5 步修完就跑,會得到 rc 2「找不到載體席」。實際順序應該是 修 → 提交 → 記帳 → 寫 `rN-fix.json` → fix-check → 問閘。
2. 第 1 步凍結只做 `git diff <merge-base>..HEAD > rN-snapshot.patch` 加 sha256,沒有任何一步要求記下凍結當下的 HEAD。計劃說 `base` 通常是「凍結材料對應的提交」,但三個月後的接手者除了翻 reflog 沒有地方查;填錯方向是「判修之前就通過」(計劃自己承認)。要在第 1 步加一句 `git rev-parse HEAD` 記進 `rN-intake.md` 或檔名旁。
3. 〈要同步的文件〉沒列:第 1 步(記 base)、第 6 步(`--regression-set`)、第 7 步與「修正差異派新席」之間的關係(fix-check 通過不代替派全新席掃 delta,手冊第 5 步原文「收斂前仍派全新席掃 delta 回歸」要保留並寫明兩者是並列,不是取代)、第 8 步(fix-check 紀錄 `rN-fix.json` 跟卷證一起進功能提交)。
4. 還有一個和既有紀律的碰撞:第 8 步允許「還沒推可以改寫那個提交」,改寫(壓提交)之後 `base` 與治理帳事件裡記的提交都不再是祖先。計劃說不要求祖先,但沒說壓提交之後 `base..HEAD` 兩端點比對會把主線已前進的改動也算進「受波及合約測試」與「疊回的測試檔」(同 `_bound_tests_range` 註解裡 r1 blocker 講的那種方向錯誤),應寫明用 merge-base 還是兩端點。

## F4 `loop next` 提醒的狀態範圍:做法寫「不管哪個狀態」、條款 S8 只釘兩個,而最常見的是 converged
severity: minor
blocking: 否
引句:「不管這次判到哪個狀態都印——★到上限(`cap-reached`)那條路尤其要印★」
引句:「(判到 `plant-canary` 與 `cap-reached` 都印)」
file: `scripts/lumos:11849-11883`
file: `scripts/lumos:21010`
1. `cmd_loop_next` 不帶 `--spec` 一律回 `gate-pending`;帶 `--spec` 時,只要最新一輪每個發現都折掉或附理由放行,處置閘就過,狀態是 `converged`(rc 0)。也就是「最新一輪有折入、折完問閘過了」正是 converged,而最後一輪的修補沒有下一輪審查看到,這比 cap-reached 更常是「推之前唯一的機械檢查」。計劃的理由文字只講 cap-reached。
2. `plant-canary` 只出現在「有 `--spec`、最新一輪有折入、而處置閘沒過」(例如 hash 不符、引句錨不到),S8 的測試要造這種夾具;`cap-reached` 同理。文字與條款不一致時,實作者會依條款只掛兩個狀態。建議 S8 改成四個狀態(gate-pending、converged、plant-canary、cap-reached)都印,並各一條斷言;理由那句改成 converged 與 cap-reached 都是沒有下一輪的路。

## F5 「`_KNOWN_GATES` 同步對文件的測試」不存在;現有漂移釘抓不到這種寫法
severity: minor
blocking: 否
引句:「(加進 `_KNOWN_GATES`,同步對文件的測試)」
file: `scripts/test_lumos.py:6458-6485`
file: `scripts/lumos:1220`
1. 查遍測試總檔,沒有任何一支比對 `_KNOWN_GATES` 與「文件」。`t_gov_stats_gate_drift` 只掃原始碼中的 `"gate": "字面值"`,而 fix-check 走 `_gate_event_or_warn(repo, "fix-check", ...)` 位置參數,不含該字面值,所以忘了加進名單時這條釘子不會紅。
2. 真正的保護是 `_gate_event` 執行時「不在名單就不寫、只在 stderr 喊一句」(`_gate_event_or_warn` 還會多印 telemetry-write-failed);也就是靜默少帳。只有 S7 會間接抓到。
3. 計劃要寫明新增一支具名釘子(例:`t_fix_check_gate_registered`:`"fix-check" in _KNOWN_GATES`,仿 `lint-new` 的 `t_lint_new_*` 那種),不要寫「同步對文件的測試」。

## F6 先紅後綠跑測試要指定 `TMPDIR`,但 `_kill_run` 沒有 env 參數
severity: minor
blocking: 否
引句:「跑測試時把 `TMPDIR` 指到修正關卡自己的暫存資料夾」
file: `scripts/lumos:13976-14007`
1. 計劃要共用 guard kill 的跑法(`_kill_run`),但它的簽名是 `(cmd, cwd, timeout, keep_re=None)`,`subprocess.Popen` 沒帶 env。實作者要嘛改共用的 `_kill_run`(合約測試閘、guard kill 都用它;而計劃「第 1 步不改 guard kill」),要嘛在指令前綴 `TMPDIR=… `(shell=True 可行,但指令含 `&&` 或 `cd` 時只作用在第一段),要嘛改 `os.environ`(整個程序,連帶影響隨後的受波及合約測試與帳本寫入的暫存檔)。計劃應指定:`_kill_run` 加選填 `env=None`,回傳形狀不變,並寫明這算「只加參數、不改行為」。
2. 另外,紅那邊 `_ran_count` 對本 repo 的執行器實測:失敗的測試印 `lumos 測試(1 案例)`,會讀到 N=1,算「確定紅」;選中 0 支印「選中 0 個測試…視為失敗」讀不到支數,算「看不出跑了幾支」。這跟計劃寫的兩種分類相符(已實測:`-k t_zz_probe_red` rc=1 且有「1 案例」;`-k t_nonexistent_zzz` rc=1 且無案例數),無需改。

## F7 條款 S4、S7、S14 的夾具要求:S4「git status 一樣」和 S7「必寫治理帳」直接衝突;`mkvault` 夾具寫不出帳
severity: minor
blocking: 否
引句:「跑完主工作目錄的 `git status` 跟跑之前一樣、兩個隔離工作樹都已收掉」
file: `scripts/test_lumos.py:179-186`
file: `scripts/lumos:1198-1215`
file: `scripts/lumos:8411-8419`
1. fix-check 每次跑完都要追加 `docs/.governance-log.jsonl`(S7)。本 repo 與消費專案該帳都是已追蹤的檔,追加後 `git status` 一定多一行 ` M docs/.governance-log.jsonl`,S4 字面無法成立。要寫成「除帳本檔外」,或夾具把帳檔放進 `.gitignore`。
2. 測試用的 `mkvault()` 是 `<tmp>/kg`,`_vault_repo_root` 在沒 `.git` 時退回 `vault.parent`,`_gate_event` 要求 `<root>/docs` 存在否則回 None 不寫;而 `cmd_gov` 讀的是 `vault.parent/.governance-log.jsonl`。所以 S7、S8、S14 的夾具必須是真實布局(`docs/<名>-knowledge` + `.git`),不能用 `mkvault`。計劃應指定用 `_stats_fixture` 或新寫一支建真 git repo 的夾具(同時 S4、S5 本來就要 git + 平台 `run_cmd` + 輸出會印「N passed」的假執行器,否則 `_ran_evidence_check` 判 unproven)。
3. 新提醒的讀帳位置要跟寫帳同一處(`_vault_repo_root(env)/docs`),不要用 `env.vault.parent`;兩者在真實布局相同、在測試夾具不同。

## F8 新寫的讀帳函式與修正紀錄解析沒提 RecursionError、型別錯的形狀;應共用 `_drift_jsonl_parse`
severity: minor
blocking: 否
引句:「讀治理帳:新寫一支讀函式,逐行先用字串預篩含 `"fix-check"` 的行再解析」
引句:「修正紀錄讀得到、是合法 JSON、`base` 是存在的提交。」
file: `scripts/lumos:29834-29849`
1. 本 repo 已有 `_drift_jsonl_parse`(位元組解碼 errors=replace、只在 `\n` 切行、`except (ValueError, RecursionError)`、非物件略過),`cmd_gov` 與表態檔都共用。計劃要「新寫一支」,實作者很可能只接 `ValueError`。`loop-convergence-recording` 筆記自己記了 2026-09-26 的前科:巢狀極深的一行丟 RecursionError。治理帳在簿記白名單內,誰提交一行含 `"fix-check"` 的深層巢狀都能讓每次 `loop next` 當掉(rc 1,而計劃保證「狀態、回傳碼都不變」)。
2. `rN-fix.json` 同理:深層巢狀的合法 JSON 會 RecursionError,Python 未捕捉時結束碼 1,等於「驗了沒過」卻沒寫事件、沒訊息。計劃只說「合法 JSON」回 2,沒說「形狀錯」(`groups` 不是清單、`paths` 缺 `status`、`findings` 是字串)回幾、算不算先決條件。請寫明:形狀不合一律回 2 並指出欄位路徑。
3. 修法一句:預篩後把整段位元組交給 `_drift_jsonl_parse`;修正紀錄解析接 `(ValueError, RecursionError)`;並依全域規則補一條「巢狀 5000 層」的最小輸入測試。

## F9 同類連兩輪規則:沒記個別嚴重度一律當 major,忽略可用的輪級嚴重度
severity: minor
blocking: 否
引句:「沒記個別嚴重度就當 major 算,寧嚴」
file: `scripts/lumos:8669-8685`
1. `--finding-severity` 要全有或全無,實測 315 筆代碼審載體席只有 66 筆帶;其餘 79% 走「當 major」。但輪級 `--severity` 是整輪最高值:輪級是 minor 時,這輪所有發現必定 ≤ minor,規則本該不要求 `prior`。照字面做,只要兩輪類別相同(例如連兩輪 `boundary`)就必填兩段十字以上的文字,多數會是敷衍字句,反而稀釋這個欄位。
2. 建議改成:有逐條值用逐條;沒有就用載體席的輪級 `severity`(多席時取同輪最高),都沒有才當 major。S6 同步多一條斷言(輪級 minor、沒逐條值 → 不要求)。

## F10 S14 要的 `regression_set` 在 gov 的審查帳轉換裡沒有被帶出來,型別表也沒列
severity: minor
blocking: 否
引句:「以及帶了 `--regression-set` 的輪裡上一輪修補造成的比例」
file: `scripts/lumos:7670-7690`
file: `scripts/lumos:7585`
1. 計劃只寫「治理帳讀端補轉這些欄位」(fix-check 事件的欄位)。但「上一輪修補造成的比例」的分子分母來自審查帳載體席的 `regression_set` 與 `findings_set`;`cmd_gov` 的 canary mapper 目前只帶 `findings_set`、`folded_set`、`accepted_set` 等,不帶 `regression_set`。`_GOV_FIELD_TYPES` 也要補 `regression_set`(清單或 None)。計劃要明列「canary mapper 補 `regression_set`」。
2. 「沒帶 `--regression-set` 的輪印 ?」要分得出「沒帶」與「帶 none(空清單)」:mapper 必須保留鍵是否存在(None vs `[]`),不能用 `d.get("regression_set") or []`。

## F11 圖譜與指令索引:lands_in 少了管 gov 讀端與 step 2 的家;新子指令會踩兩支既有測試
severity: minor
blocking: 否
引句:「[[Systems/pitfalls-code-loop]] 與 [[Systems/loop-convergence-recording]] 各補一段。」
file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:99`
file: `scripts/test_lumos.py:7553-7584`
file: `scripts/test_lumos.py:8180-8197`
1. 計劃改到 `scripts/lumos` 的 gov 轉換與 `_GOV_FIELD_TYPES`、`_KNOWN_GATES`、doctor 提醒、guard kill 共用抽取(第 2 步)。`_GOV_FIELD_TYPES` 的家是 `Systems/reversibility-governance-ledger`(該篇第 99 行寫這張表),guard kill 的是 `Systems/guard-kill`,重用合約測試的是 `Systems/bound-tests-gate`,doctor 段的是 `Systems/doctor-irreversible-hint` 一類。〈lands_in〉只列兩篇(這兩篇的 about_code 都只有 `scripts/lumos`,而該檔有 31 個家),按鐵則 5「改了程式要寫說明就寫進改到那支檔的家」與計劃 lands_in 的要求,第 1 步至少要加 `reversibility-governance-ledger`,第 2 步加 `guard-kill`、`bound-tests-gate`。〈related〉列了 `guard-kill` 卻沒進 lands_in。
2. 新子指令 `loop fix-check`、`loop memo` 會讓 `t_every_subcommand_has_when`(每個子指令 `--help` 要有「什麼時候用:」)與 `t_command_index_complete`(指令索引子檔要提到每個 loop 二層子指令;`INDEX.md` 還有 4500 字元上限)翻紅。計劃的〈要同步的文件〉只寫「指令速查第 06 子檔加指令」,沒寫 `--help` 的「什麼時候用:」,也沒提 INDEX 字數。這兩支會在實作時當場紅,算順手可修,但應列進〈要同步〉。
3. `lands_in` 兩篇的範圍對得上主題(代碼審流程、審查帳/收斂讀端),沒有錯。

## 已讀,無 finding 的部分
- 〈名詞〉、〈範圍〉、〈回退〉:已讀,無 finding。
- 先紅後綠的 worktree 做法、`_ran_count` / `_ran_evidence_check` 判法:對照真碼與本 repo 執行器實測相符(失敗印 `1 案例`、0 支印「選中 0 個測試」),見 F6 第 2 點。
- 與處置閘、`loop replay`:`rN-fix.json` 在 `governance/review-reports/` 之下(屬簿記目錄),不在回放閉包(閉包只收各席 report/snapshot 與資安席檔);`regression_set` 是載體席新增鍵,回放以整行 sha 比對,對舊迴圈不翻。無 finding。
- 與 `code-loop pass`/`check`:fix-check 事件寫進 `docs/.governance-log.jsonl`(`_BOOKKEEPING_FILES`)、`rN-fix.json` 在 `_BOOKKEEPING_DIRS`,不會讓留痕失效。無 finding。

最高等級:major,blocking 共 3 條
