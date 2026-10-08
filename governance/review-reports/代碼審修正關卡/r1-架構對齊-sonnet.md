severity: major

# 架構對齊審查(架構對齊-sonnet)

四問先答(每問附佐證行),再列不對齊清單。

## 四問摘要

1. 分層與依賴方向:`fix-check` 放 `loop` 底下,跟 `status/next/list/escape` 同組,收「迴圈編號」這點對得上(file: `scripts/lumos:41099`、`scripts/lumos:41135`)。呼叫的 `_gate_event_or_warn`、`_KNOWN_GATES`、`resolve_test_refs`、`_platform_test_index`、`_ran_count`、`_ran_evidence_check`、`_bound_tests_for_diff`、`_run_bound_tests` 都是既有函式,方向沒反。有兩處跟鄰居不同:先紅後綠另寫一份建工作樹(F1)、受波及合約測試的判讀繞過既有的 `_bound_tests_check` 另組一份(F2)。
2. 命名與錯誤處理:閘名 `fix-check`、環境變數 `LUMOS_SKIP_FIX_CHECK=1`(只認 1)、kind `skipped-env`、回傳碼 0/1/2、欄位 `secs`/`record_sha256` 都對得上鄰居(file: `scripts/lumos:30899`、`scripts/lumos:38743`、`scripts/lumos:14105`)。不一致的是 kind `failed`(F4)、迴圈編號放 `extra.loop`(F5)、設定讀取形狀(F6)、入口旗標與 doctor 編號(F7)。
3. 第二種做法:有兩個(F1 建工作樹、F2 合約測試判讀),其餘「治理帳讀取、紀錄檔格式、切點判斷」只算輕度偏離(F5、F10)。切點判斷明寫照 `_panel_retired_for`,對得上(file: `scripts/lumos:9105`)。
4. 落點:`lands_in` 兩篇已各 32KB/25KB,而且這份是一道新閘(新紀錄格式、14 條條款、新治理帳閘名),鄰居的慣例是各自有家(F9)。

## F1 先紅後綠另寫第二份建工作樹,而且刻意留到第 2 步才抽共用
severity: major
blocking: 是
引句:「第 1 步先紅後綠照 guard kill 的寫法另寫一份,第 2 步改 guard kill 時抽成共用」
file: `scripts/lumos:14202`(`tempfile.mkdtemp` + `worktree add --detach`)
file: `scripts/lumos:14312`(`worktree remove --force` / `rmtree` / `worktree prune` 在 finally)
file: `scripts/lumos:23942`(告警閘 lint-new 另有一套 `mkdtemp(dir=.lumos)`,不碰 git 工作樹,只供對照:專案裡建隔離目錄已有兩種寫法,不宜再加第三種)

1. 專案裡「開隔離工作樹、跑指定測試、收掉」目前只有一份實作,就是 `cmd_guard_kill` 裡那段(寫在 200 多行的迴圈內,綁著 `wt_ok`、`tmp_parent`、`keep_worktree`)。
2. 這份設計第 1 步明寫「另寫一份」,第 2 步才改 guard kill 抽共用,〈範圍〉也明寫「第 1 步不改 guard kill」。照字面實作,第 1 步功能提交進主線時,repo 裡就同時有兩套建/收工作樹的寫法;而且兩套建法已經不同:guard kill 固定檢出平台根的 `HEAD`(`git -C proot rev-parse HEAD`,file: `scripts/lumos:14181`),新的要檢出任意 `base` 還要疊測試檔。
3. 第 2 步再抽共用,等於重構一個剛過完代碼審的第 1 步產物加一個前一天才改過的 guard kill,而且〈實務隱患〉自己承認這是重複。這正是「接手的人要在兩套之間猜」的情形。
4. 不採「抽共用要動 guard kill、所以延後」當理由:共用函式可以先在第 1 步抽出,guard kill 改成呼叫它(行為不變,有 `t_guard_kill*` 測試守),比日後兩套並存再合併便宜。
5. 未實測,依據是讀碼。

## F2 受波及合約測試的判讀繞過 `_bound_tests_check`,在 fix-check 裡另組一份判法
severity: major
blocking: 是
引句:「用 `_run_bound_tests` 在主工作目錄真跑」
file: `scripts/lumos:38725`(`_bound_tests_check`:一支函式包住 範圍換算 → `_bound_tests_for_diff` → `_run_bound_tests` → red/unproven/no-cmd 分流 → 過濾探針冒煙測試 → 記治理帳 `bound-tests`)
file: `scripts/lumos:38814`(red 分支)、`scripts/lumos:38843`-`38868`(對沒有 `_RAN_EVIDENCE` 的 profile 退回 `_bound_tests_filter_probe`,不過就回 `unfilterable`)
file: `scripts/lumos:39740`(`LUMOS_SKIP_BOUND_TESTS` 的處理也在這支裡)

1. 專案「判某批受波及合約測試算不算綠」的唯一做法是 `_bound_tests_check` 回的 status(green/red/unfilterable/no-config/…),推送前掛鉤、`code-loop check`、獨立 `bound-tests` 指令都走它。
2. 這份設計第 5 項自己組:`_bound_tests_for_diff` → `_run_bound_tests` → 自訂的判法表(green 過;red/unproven/no-cmd/懸空不過;no-pins/no-bound/no-vault 過;diff-unavailable/no-config 不過)。表裡沒有 `unfilterable` 那一層:對沒有實測輸出樣式的 profile,推送閘會用冒煙測試判「綠不可信」,fix-check 這邊會直接放行。同一批合約測試,推送閘說「證不出真的跑過」、修正關卡說「全綠」,兩邊結論對不上。
3. 若改成直接呼叫 `_bound_tests_check`,它會多寫一筆 `gate=bound-tests` 事件(`_bound_tests_log`),跟條款 [S7]「恰好一筆閘名 fix-check」不衝突,但設計沒說要不要、也沒說 `LUMOS_SKIP_BOUND_TESTS=1`(CI 常設)時 fix-check 要不要跟著跳過——兩種做法在設計裡都沒選,字面實作只能是「另組一份」。
4. 修法方向(只指出對齊點,不評好壞):要嘛呼叫 `_bound_tests_check`(並寫明多出的 `bound-tests` 事件與環境變數行為),要嘛把它尾段的判讀抽成純函式兩邊共用。
5. 未實測,依據是讀碼。

## F3 先紅後綠要用哪支「跑指令」的函式沒寫,TMPDIR 隔離沒有現成入口
severity: minor
blocking: 否
引句:「跑測試時把 `TMPDIR` 指到修正關卡自己的暫存資料夾,跟工作樹一起刪」
file: `scripts/lumos:13976`(`_kill_run(cmd, cwd, timeout, keep_re)` 沒有 env 參數,`Popen` 繼承父環境)
file: `scripts/lumos:38641`(`_run_bound_tests` 也是呼叫 `_kill_run`)

1. 專案裡跑 `run_cmd` 的共用函式是 `_kill_run`(合約測試閘與 guard kill 都用它)。設計寫了逾時、`{method}` 展開、`_ran_count`,卻沒指名它。
2. 要把 `TMPDIR` 指到自己的暫存資料夾,`_kill_run` 沒有 env 入口。字面實作只有兩條路:改共用函式加參數(動到 guard kill 與合約測試閘的共用路徑,而〈範圍〉說第 1 步不碰 guard kill),或自己 `subprocess.Popen` 第三個跑指令的寫法。設計兩條都沒選。
3. ⚠ 交編排者:這條判 minor 是因為結構上可以對齊(`_kill_run` 加 `env=None`),但設計沒寫,實作者會各猜各的。

## F4 治理帳 kind 用 `failed`,專案鄰居沒有這個字
severity: minor
blocking: 否
引句:「閘名 `fix-check`(加進 `_KNOWN_GATES`,同步對文件的測試),kind `passed` / `failed`」
file: `scripts/lumos:25830`(nodehome-check:`blocked`/`warned`/`passed`)
file: `scripts/lumos:31835`(drift-check:`passed`/`blocked`/`warned`/`range-unavailable`)
file: `scripts/lumos:38814`(bound-tests:`red-advisory`/`red-blocked`,advisory 與擋分帳)
file: `scripts/lumos:7470`(`gov --stats` 的「閘的動作」段只認 `blocked`、`skipped*`、`fail-open`)

1. 鄰居的「驗了沒過」:會擋的叫 `blocked`(帶 `hard=True`)、只提醒的叫 `warned`,bound-tests 另用 `red-advisory`/`red-blocked` 分帳。全專案治理帳沒有 `failed` 這個 kind(grep `"failed"` 作 kind 零筆)。
2. fix-check 兩步都只提醒不擋,對應鄰居的詞是 `warned`(或像 bound-tests 那樣的 `red-advisory`);日後「轉成擋」那刻,依鄰居慣例會換成 `blocked`,而 `failed` 要不要改名、舊帳怎麼讀,設計沒講。
3. `gov --stats` 現有讀「閘的動作」的地方不認 `failed`,所以 [S14] 的新段要自己認;設計有寫新段,只是 kind 名跟既有統計口徑接不上。
4. 結構(`_gate_event_or_warn` + `_KNOWN_GATES`)對得上,只有詞不一致。

## F5 迴圈編號放在 `extra.loop`,治理帳裡已有兩種認迴圈的寫法,這是第三種
severity: minor
blocking: 否
引句:「欄位放 `extra`:`loop`、`round`、`record_sha256`、`groups`(組數)」
file: `scripts/lumos:9557`-`9579`(設計審那組:迴圈編號寫在 `nodes` 欄;code-loop 那組:只能從 `detail` 自由文字猜,並寫明 REVISIT「正解是寫進 nodes」)
file: `scripts/lumos:24007`(又一支讀治理帳的函式,預篩字串再解析,跟設計說的做法一致)

1. 治理帳認迴圈的既有慣例:`nodes[0]` 放編號(設計審),code-loop 那組是被承認的缺陷,註解寫「正解是 nodes」。這份設計新增的事件把編號放 `extra.loop`(攤平成最外層 `loop` 欄),是第三種。
2. 設計要新寫一支讀函式讀它,跟「讀治理帳」的鄰居(`_loop_close_stamps`、`_codeloop_read_from_ledger` 等)做法同形(先字串預篩再解析),這部分對齊;只有編號欄位的位置不對。
3. ⚠ 交編排者:判 minor,因為 `loop list` 的關門事件表只認 `design-loop`/`code-loop` 兩個閘(`t_loop_close_kinds_classified` 不會被新閘名觸發),讀端不會跟這個差異打架;但若日後 `loop list`、`loop memo` 想用治理帳串迴圈,會得認三種位置。

## F6 `fix_check.stress` 沒有照鄰居的「設定讀取函式」形狀,也沒有 gate 模式鍵
severity: minor
blocking: 否
引句:「兩步都只提醒不擋。轉成擋是另一個小改動:`loop next` 在缺通過紀錄時改回新狀態 `fix-check-pending`」
file: `scripts/lumos:5762`(`_note_lint_config`:回 `{"mode", "warnings"}`;不存在用預設、壞掉用預設並警告、值看不懂當 on 並警告)
file: `scripts/lumos:30808`(`_drift_config`)
file: `scripts/lumos:34517`(`_ci_config`:未宣告=全關、壞損 fail-safe)

1. 鄰居每個設定區塊(`note_lint`、`drift_check`、`node_home`、`ci`)都各有一支讀取函式,處理「檔不存在/JSON 壞/區塊不是物件/捷徑檔/值看不懂」五種情況並回警告給 doctor。設計只寫了鍵名 `fix_check.stress` 與其內容形狀,沒提讀取函式與壞設定時的行為(`stress` 不是陣列、`timeout` 非數字怎麼辦)。
2. 鄰居的「先提醒後擋」是用設定鍵 `gate: warn|block|off`(例:`note_lint.gate` 預設 warn)切換;設計改用「程式常數日期 + 環境變數覆寫」(照 `_panel_retired_for`)。兩種在專案裡都有先例,但 `_panel_retired_for` 的場景是「舊迴圈回放不翻」,修正關卡轉成擋同樣要保舊迴圈,所以選常數日期說得通;只是設計沒說為什麼不用 `fix_check.gate`,下一個人會問。
3. 結構性衝突不大,列 minor。

## F7 入口旗標與 doctor 提醒的登記方式跟鄰居不同
severity: minor
blocking: 否
引句:「`lumos loop fix-check <迴圈編號> --round <輪> [--record <檔>] [--json]`」
file: `scripts/lumos:41109`、`scripts/lumos:41144`、`scripts/lumos:41194`(`loop status/next/replay` 都有 `--repo`)
file: `scripts/lumos:7284`-`7288`(doctor P2:有編號、`--ci` 記 `check-p2` 事件、登記進 `_KNOWN_GATES`)

1. fix-check 要開工作樹、跑 `git status`、讀 `.lumos/config.json`,都需要 repo 根;鄰居靠 `--repo`(預設向上找 `.git`)或 `_repo_root_from_env(env)`(file: `scripts/lumos:11898`)。設計的指令列沒有 `--repo`,也沒說用哪一個。
2. 第 2 步「doctor 提醒沒宣告壓力指令」:鄰居的 doctor 提醒都有編號並登記 `check-xx` 閘名;設計的 [S13] 只說「印一行提醒」,沒有編號、沒有 `--ci` 事件、沒有 `_KNOWN_GATES` 同步。

## F8 第 2 步殺傷力重跑:怎麼從 `cmd_guard_kill` 拿到逐條結果沒寫
severity: minor
blocking: 否
引句:「判 `survived`、`drifted`(配方失配)、`error`、`abort`(baseline 就紅)的都算不過並列出配方短身分」
file: `scripts/lumos:14105`(`cmd_guard_kill(env, node, ...)` 一次只吃一個節點,結果只印出來與寫 `.kill-log.jsonl`,回傳值只有 rc)
file: `scripts/lumos:14199`(唯一呼叫點在 argparse 分派)
file: `scripts/lumos:13357`(`_kill_recipe_judge`:doctor P2 走的是共用純函式,不是 `cmd_guard_kill`)

1. 設計要「掃每篇筆記的配方比對 `file`,只重跑那幾條」,而 `cmd_guard_kill` 是單節點、印出式的指令函式,沒有任何地方把它當函式呼叫過。要拿到每條配方的 verdict,只有:擷取它的標準輸出(`cmd_loop_next` 對 `cmd_loop_status` 有 `contextlib` 擷取的先例)、讀 kill-log、或重構出回傳結構的核心函式。三條都是專案裡有的做法,設計沒選。
2. 結構上不衝突,列 minor;不挑哪條是因為這屬於實作選擇,但要在設計寫明,否則實作者容易再造第四種。

## F9 落點:新閘建議不只塞進兩篇既有 Systems
severity: minor
blocking: 否
引句:「與 [[Systems/loop-convergence-recording]] 各補一段」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`(32,470 位元組、158 行;管 `pitfalls` 風險分級與 `code-loop` 的 pass/skip/check/表態)
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md`(24,971 位元組、174 行;管審查帳、`loop status/next/list/escape`、`canary record`)
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`(20,443 位元組)、`Systems/guard-kill.md`(20,632 位元組)、`Systems/規格閘.md`、`Systems/存量漂移守衛.md`(各自一道閘各自一個家的先例)

1. 這份設計的內容分三類:①`canary record --regression-set`、`loop next` 提醒、`loop memo`:屬 `loop-convergence-recording`(審查帳與 loop 指令),落點對。②`fix-check` 本體(修正紀錄格式、五項檢查、治理帳新閘 `fix-check`、第 2 步壓力指令):既不是 `pitfalls`、也不是 `code-loop pass/skip`,放進 `pitfalls-code-loop` 會讓這篇繼續膨脹(已 32KB);鄰居的做法是一道閘一篇,例如 `bound-tests-gate`、`規格閘`、`存量漂移守衛`。③第 2 步改 `cmd_guard_kill`(殺傷力重跑、共用建工作樹):屬 `guard-kill`,而 `lands_in` 與 〈要同步的文件〉都沒列它(只在 `related`)。
2. 建議:新開一篇 `Systems/修正關卡`(或 `fix-check`)當本體的家,`loop-convergence-recording` 補 `--regression-set` 與 `loop next` 提醒兩句並連過去,第 2 步另在 `guard-kill` 補一段。
3. ⚠ 交編排者:判 minor;「該不該另開一篇」是慣例判斷,不是機械可驗,所以不判 major。

## F10 修正紀錄是人手填的 JSON,沒有像表態檔那樣的樣板產生入口
severity: minor
blocking: 否
引句:「用 JSON 不用 Markdown 表——要機械驗每個欄位,表格解析容易因為一個直線字元壞掉。」
file: `scripts/lumos:40022`(`code-loop dispositions` 的流程:先 `pitfalls --diff <範圍> --dispositions-template > 檔` 產樣板,填完再帶進來,工具驗並綁定 branch/sha、寫進治理帳)
file: `scripts/lumos:41753`(`dispositions` 子指令與它的 `--branch`/`--at-sha`)

1. 專案裡「編排者填一份 JSON、工具驗證並記帳」的既有做法是 `dispositions`:有樣板產生器、有綁版本。fix-check 的紀錄同樣是編排者填、工具驗,卻沒有樣板產生入口,`base`、`groups[].findings` 都要手抄(這輪折入的發現清單其實審查帳上就有,可以預填)。
2. 只算輕度偏離:JSON 格式與 `rN-dispatch.json` 同目錄同命名風格,這部分對齊(file: `scripts/lumos:41099` 同組、目錄見 `governance/review-reports/*/r1-dispatch.json`)。缺的是樣板那一半,日後要補成新指令。

## 已讀無 finding 的部分

- 命名 `LUMOS_SKIP_FIX_CHECK`(只認 `1`、跳過時記 `skipped-env`)與 `LUMOS_SKIP_NOTE_SHAPE`/`LUMOS_SKIP_DRIFT_CHECK`/`LUMOS_SKIP_BOUND_TESTS` 一致(file: `scripts/lumos:26887`、`scripts/lumos:30899`、`scripts/lumos:38739`)。
- 回傳碼 0/1/2(過/不過/輸入錯)與 `cmd_guard_kill` 的 rc 語意同形(file: `scripts/lumos:14108`)。
- 記帳寫入走 `_gate_event_or_warn`、閘名進 `_KNOWN_GATES`、寫不進不改判定,與鄰居一致(file: `scripts/lumos:1234`、`scripts/lumos:7258`)。
- 測試存在檢查走 `resolve_test_refs` + `_platform_test_index`,是既有共用解析(file: `scripts/lumos:4896`、`scripts/lumos:11905`)。
- 轉成擋的切點判斷明寫照 `_panel_retired_for`(常數日期 + 環境變數覆寫 + 非日期當舊帳),對得上(file: `scripts/lumos:9105`)。
- 「決策備忘錄」只印底稿不另設「人裁定」紀錄檔,沒有引入新的人裁定格式;`loop rewrite`、`signoff` 的既有紀錄不受影響。

不對齊共 10 條,其中 major 2 條

最高等級:major,blocking 共 2 條
