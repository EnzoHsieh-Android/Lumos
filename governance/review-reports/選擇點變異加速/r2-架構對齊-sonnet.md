severity: major

## 1. 分層與依賴方向

大致對齊,有一處繞過既有入口(finding 1)。

- 對齊:新機制放進 `cmd_guard_kill`,以選用參數 `merge` 接上。這跟既有 `recipes_override`、`source`、`stop_group_on`、`on_row`、`should_stop` 同一套接法(`scripts/lumos:28301-28303`),docstring 也寫了「不傳時行為與輸出不變」。
- 對齊:JUnit 讀法經 `_secev_tq()` 取得 `test_quality.junit()`,例外接法照 `_secev_junit_facts`(`scripts/lumos:9034`、`scripts/lumos:9046-9060`)。
- 對齊:`_gradle_task_list`、`_SR_MODULE_PART` 照用,沒改 `_gradle_test_module`(`scripts/lumos:76983-77009`),另開兄弟函式。
- 對齊:壞法路徑圍欄(`scripts/lumos:26819-26836`)與逾時下限(`scripts/lumos:28363`、`scripts/lumos:78629`)都沿用既有概念。
- 不對齊:合併模式把指令改寫與代換自己做一套,沒走 `_run_cmd_expand`(finding 1)。
- ⚠ 交編排者:既有慣例是把 choice-kill 專用的橫切邏輯收進 `_KillHooks`(`scripts/lumos:28648`)。spec 把合併基準、合併道、逐支道、退回逐支全寫進 `cmd_guard_kill` 本體,沒提及放進 `_KillHooks` 或另一個輔助類別。
- 同樣標 ⚠:`_ChoiceKillRun.on_row` 在合併模式下改成「等全部列到齊才判」,而既有語意是「第一個決定性列就判」(`scripts/lumos:78518-78530`)。這是同一支函式的語意分岔,不是新機制。結構上對得上,放哪裡由編排者定。

## 2. 命名與錯誤處理

- 錯誤與提示一律印標準錯誤,對齊:choice-kill 呼叫 `cmd_guard_kill` 時用 `redirect_stdout` 吞掉標準輸出(`scripts/lumos:78542`),spec 的做法正確。
- 判法欄 `judged` 與 `merge_ver`、run 的 `merged`、`fallback`、`single`:新欄位進 `_GOV_FIELD_TYPES` 並用 `type(x) is int` 排除 bool,做法對齊(`scripts/lumos:18434`、`scripts/lumos:18462`)。
- 以下三處命名或接法不一致,見 finding 2、3、4。

## 3. 第二種做法

- 指令改寫有第二套,見 finding 1。
- 讓舊紀錄過期:沿用既有的「同鍵最新一筆 → stale」狀態(`_choice_disposition`,`scripts/lumos:78074`),沒有另開一套。版本常數加欄位的手法也是專案既有的(`_DOOR_RULE_VERSION`、`door_rule`、`_SMALL_CHANGE_RULE_VERSION`,`scripts/lumos:14034`、`scripts/lumos:14077`),只是缺釘版測試,見 finding 2。
- 結果判讀:經 `junit()`,沒有另寫解析。
- 計劃已明講不改 `_gradle_test_module`,理由站得住。

## 4. 落點

- 合理:`lands_in` 寫規格閘與 guard-kill,對得上現況。choice-kill 的家本來就在規格閘(`Systems/規格閘.md:70`)。guard-kill 的 responsibility 明寫它是 choice-kill 臨時配方的唯一判法(`Systems/guard-kill.md` 第 8 行),`merge` 判法本體放進去是對的。
- 手冊兩處(`06-代碼審與推送.md` 第 18 列、`lumos-code-loop/SKILL.md`)放在落點段,理由也寫了(`lands_in` 只收 Systems)。
- ⚠ 交編排者:參考資料說 guard-kill「沒寫負責範圍」,但該篇 frontmatter 有寫 responsibility。參考資料列它牽連的檔是 `test_quality.py`。這是工具自動附加的牽連,不是 spec 的問題。

## Findings

## 合併指令改寫另走 shlex 與自己的代換,繞過 `_run_cmd_expand`
severity: major
blocking: 是

spec 段落:〈做法〉1「組指令」與「條件」。

問題:專案裡把 `{method}`、`{python}` 換進 `run_cmd` 的單一入口是 `_run_cmd_expand`。它的 docstring 明寫「讀 run_cmd 的三處都經這一支,原本三處各自代換,新佔位符漏補一處就會把字面 {python} 交給 shell」。

spec 另做了一套:
- 用 `shlex.split` 切詞。
- 自己呼叫 `_name_filter_escape` 逐支換 `{method}`。
- 用 `shlex.join` 接回,不經 `_run_cmd_expand`,只靠「條件」排除 `{python}`。

同一條 `run_cmd` 因此有兩套切詞器:
- `_gradle_task_list` 底層是 `_detekt_walk_segments`,會剝環境變數前綴、`env`、`time` 包裝詞,並展開一層 `sh -c`。
- 合併條件另用 `shlex.split`,而且排除 `sh -c` 與含 `$` 的詞。

例:`FOO=1 ./gradlew :app:testDebugUnitTest --tests '*{method}'`
- `_gradle_task_list` 認得這條。
- `shlex.split` 把 `FOO=1` 當第一個詞。spec 沒寫會拿它怎麼辦,可能組出不同的詞序。

這就是「另一套指令改寫」。

引句:「用標準函式庫 `shlex.split(run_cmd)`(posix 模式)切得開」

引句:「最後用 `shlex.join` 把全部詞接回一條指令」

佐證:
- `scripts/lumos:28053-28068`(`_run_cmd_expand` 與它的 docstring)
- `scripts/lumos:76986-76998`(`_gradle_task_list` 用 `_detekt_walk_segments`)

## 版本作廢缺釘版測試,常數與欄位命名跟既有版本欄不同
severity: minor
blocking: 否

spec 段落:〈做法〉6「作廢舊的合併判定」。

問題:既有的版本欄做法是「常數 `_X_RULE_VERSION`、帳欄 `door_rule`、釘版測試」。判法一改,釘版測試(`t_door_rule_version_pin`、`t_door_scan_logic_version_pin`)就紅,逼人升版。spec 的 `_CHOICE_MERGE_VER` 靠人記得加一(「改了就把常數加 1」),沒有對應的釘版測試。判法漏升版時,舊的合併判定會繼續當有效處置。命名也和既有的 `*_RULE_VERSION` 慣例不同。

引句:「判法改了(對名規則、乾淨條件、結果檔讀法)就把常數加 1,舊的合併判定一次全部要重跑。」

佐證:
- `scripts/lumos:14034`(`_DOOR_RULE_VERSION`)
- `scripts/lumos:14047`(兩層連動說明)
- `scripts/test_lumos.py:78251`(`t_door_rule_version_pin`)

## 全域關閉環境變數命名跟既有關閉開關慣例不同
severity: minor
blocking: 否

spec 段落:〈做法〉6「全域關閉」。

問題:repo 裡「出事一次關掉某道」的環境變數幾乎都是 `LUMOS_SKIP_*`(`LUMOS_SKIP_LINT_NEW`、`LUMOS_SKIP_BOUND_TESTS` 等),個別是 `*_OFF`(`LUMOS_ENTRY_HOOK_OFF`)。現有的 `LUMOS_CHOICE_*` 只有 `LUMOS_CHOICE_SINCE`(測試覆寫生效日)。`LUMOS_CHOICE_NO_MERGE` 是第三種形狀。

- ⚠ 交編排者:`--no-merge` 的 `--no-*` 旗標有既有先例(`--no-run`、`--no-pull`),這個沒問題。
- ⚠ 交編排者:既有 `LUMOS_SKIP_*` 通常連帶「留帳」的語意,這支要不要沿用,spec 沒寫。

引句:「環境變數 `LUMOS_CHOICE_NO_MERGE=1` 等同 `--no-merge`,出事時一次關掉所有呼叫」

佐證:
- `scripts/lumos:78023`(`LUMOS_CHOICE_SINCE`)
- `scripts/lumos:82073`(`--no-run`)

## 新帳欄白名單的落點寫成 `_gov_row` 白名單,與既有 `ck` 子字典不符
severity: minor
blocking: 否

spec 段落:RETIRE-IF 與〈做法〉6「run 事件」。

問題:`_gov_row` 現在的 choice-kill 讀取有兩處。
- 頂層白名單只有 `verdict`、`row`、`attempt`、`reason`、`via`、`run_id`。
- 統計用欄位走 `ck` 子字典:`file`、`fp`、`killing_test`、`changed`、`mutant_lines`、`secs`、`reasons`、`site`。

`ran` 目前不在任何一個。spec 把 `ran` 寫成「(既有)」並說都在 `_gov_row` 白名單。`judged`、`merge_ver`、`merged`、`fallback`、`single` 該進頂層還是 `ck`,spec 沒指明。照字面把五個欄位全塞頂層,會和 `secs`、`changed` 這種統計欄走 `ck` 的既有分法不一致。

引句:「兩條讀的欄位都在 `_gov_row` 白名單(見〈做法〉6)。」

佐證:
- `scripts/lumos:18548-18553`(`_gov_row` 的 choice-kill 兩段)
- `scripts/lumos:18462`(`ran` 只是型別登記)

## 版本過期共用 stale 狀態,但推送閘文字與狀態定義只涵蓋「測試沒綁」
severity: minor
blocking: 否

spec 段落:〈做法〉6「作廢舊的合併判定」。

問題:`_choice_disposition` 的 `stale` 定義是「殺掉它的測試已沒有條款綁」,手冊與推送閘的提示也這樣寫(`06-代碼審與推送.md` 第 21 列「過期(殺掉它的測試沒有條款綁了)→ 重綁或重跑」)。spec 讓判法版本落後也回 `stale`,結構上沒另開機制,這點對齊。但新原因(版本過期)沒補提示文字,人照原提示去「重綁」會繞遠路。

spec 的〈落點〉有補推送閘文字:「推送閘把舊版合併判定當過期」,但沒寫提示字串要不要區分。

⚠ 交編排者:要不要在提示補一句「判法版本過期、重跑 choice-kill 即可」,看是否算既有做法的延伸。

引句:「推送閘照既有「過期」擋、`_choice_kill_pick` 照「過期」排進先跑」

佐證:
- `scripts/lumos:78074-78090`(`_choice_disposition`)
- `skills/lumos-project-notes/commands/06-代碼審與推送.md:21`

不對齊共 5 條
