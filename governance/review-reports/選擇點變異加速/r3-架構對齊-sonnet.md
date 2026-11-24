severity: major

## 四問

**1. 分層與依賴方向:不對齊。**
- 放哪一層對。合併邏輯放進 `cmd_guard_kill`,單一壞法的選用參數也是這個慣例(`scripts/lumos:28301`);判誰殺掉、帳與旗標留在 choice-kill 那邊,跟 guard-kill 負責範圍的分工一致(`Systems/guard-kill.md` 的 responsibility 寫「不負責…治理帳的判定紀錄」)。
- 呼叫方向對。`_gradle_task_list`(`lumos:76986`)、`_run_cmd_expand`(`lumos:28053`)、`_test_name_ok` 與 `_name_collision_reason` 都照既有入口呼叫。
- 繞過既有入口:讀 JUnit 結果檔時,spec 直接呼叫 `test_quality.junit()` 並自己抄一份例外處理,沒走 `_secev_junit_facts`(見 findings 一)。
- 另有兩處接線 spec 沒交代清楚(findings 三、四),結果資料夾路徑也沒指到既有的 `_under_root`(findings 五)。

**2. 命名與錯誤處理:大致對齊,有一處不一致。**
- 提示印到標準錯誤,跟 `cmd_guard_kill` 內部的 ⚠ 行一致(`lumos:28360`、`28418` 一帶用 `file=sys.stderr`)。
- `--no-merge` 對得上 `--no-run`(`lumos:82073`)。
- 帳欄位:`_GOV_FIELD_TYPES` 已有 `(bool,)`(`interrupted`)、`(int,)`(`ran`、`changed`)、`(str,)` 的登記形狀(`lumos:18434-18470`),新欄位照這套登記沒問題。
- 統計欄位放 `_gov_row` 的 `ck` 子字典也對(`lumos:18553`)。
- 不一致:`LUMOS_SKIP_CHOICE_MERGE` 的語意跟既有的 `LUMOS_SKIP_*` 不同(findings 二)。

**3. 第二種做法:有一處。**
- 讀 JUnit 的第二條路(findings 一)。
- ⚠ spec 〈做法〉1 在原字串上自己找 `--tests` 那一段字,並說不另起切詞器。既有的 `_gradle_args_tasks(..., values=vals)` 已把 `--tests` 列為帶值選項(`lumos:76999`)。但它回傳的是詞而不是字串位置,無法原位代換。這是出於需求的手寫掃描,我判不準,交編排者。
- ⚠ 完整名的比對規則(`$` 換 `.`、去參數尾巴)是新規則。既有呼叫端有兩種讀法:`_secev_junit_facts` 的身分是 `classname::name`,`_kill_attribute` 是在輸出文字裡找名字,都沒有「方法名對案例」這一層。我找不到可重用的既有函式,不算第二種做法。

**4. 落點:大致合理,有一條對不上家。**
- `Systems/guard-kill` 的 responsibility 已寫明它是 choice-kill 臨時配方的唯一判法,它也是 `_situation_rule_signals` 與 `_KILL_RUN_LIVE` 的家(我搜整個 Systems 資料夾,只有它提到前者)。
- `Systems/規格閘` 管 choice-kill 的批次、帳與 `ck`。
- 落點拆成這兩篇合理,不必另開。唯一對不上的是第一個訊號那條(findings 六)。

## Findings

### 一、讀 JUnit 繞過既有的 `_secev_junit_facts`,自己重寫例外處理
severity: major
blocking: 是

- spec 位置:〈做法〉3「結果檔讀法」、〈用詞〉乾淨、〈依據來源〉第 7 列。
- spec 自己寫:各自呼叫一次 `test_quality.junit(raw)`,模組經 `_secev_tq()` 取得,例外處理「照 `_secev_junit_facts`」,也就是把那段 try/except 抄一份。
- 既有同形做法:`_secev_junit_facts(raw, tq)`(`lumos:9046`)已把 `junit()` 包好:接 `JUnitRejected` 取 code、`ParseError`、`RecursionError`、`ValueError`,另有 `_SECEV_FACTS_MAX` 案例數上限,回 `({id: (status, assertion)}, None)` 或 `(None, 原因碼)`。
- 同層第二個呼叫端已經照這個入口用,沒抄例外鏈:`_e2e_junit_ok`(`lumos:46316-46336`)是 `_secev_tq()` + `read_bytes` + `_secev_junit_facts`。
- spec 要的資訊 facts 都有:狀態 `passed`、`failure`、`error`、`skipped`,加上 `classname::name` 身分。完整名可以從身分用 `::` 切出來。
- 後果:例外鏈與案例數上限變兩份。日後 `junit()` 新增拒收型別或例外,兩邊要各改。spec 〈依據來源〉自己宣稱「JUnit XML 一律經單一入口」,字面跟實作不符。
- 引句:「接例外的寫法照 `_secev_junit_facts`。」
- file: `scripts/lumos:9046`
- file: `scripts/lumos:46316`

### 二、`LUMOS_SKIP_CHOICE_MERGE` 的語意跟既有的 `LUMOS_SKIP_*` 不同 ⚠
severity: minor
blocking: 否

- 既有的 `LUMOS_SKIP_*` 全部是跳過一道關卡或檢查,並印一行、記 `skipped-env` 事件進治理帳:
  - `LUMOS_SKIP_DRIFT_CHECK`:`lumos:61972-61974`
  - `LUMOS_SKIP_FIX_CHECK`:`lumos:23596`
  - `LUMOS_SKIP_ROOM_GUARD`:`lumos:53389`
- 本案的合併只是效能開關,關掉不減少任何檢查。spec 沒有印字、沒有 `skipped-env`,只靠每筆 `judged=single` 留痕。
- 效能類開關的既有命名是 `LUMOS_DISPATCH_LENS_NO_CACHE`(`lumos:71814`)與 `LUMOS_KILL_TIMEOUT_FLOOR` 一類,不是 `SKIP`。
- 使用者在〈人裁紀錄〉第六筆(2026-11-23)裁過這個名字,「只認 1」也對。是否為了前綴統一而接受語意差,交編排者。
- 引句:「只認 `1`,其他值與沒設一樣,照 `LUMOS_SKIP_*` 慣例」
- file: `scripts/lumos:61972`
- file: `scripts/lumos:71814`

### 三、`merge` 只是一個選用參數,但需要的資訊多過它;邏輯放哪裡也不一致
severity: minor
blocking: 否

- 〈做法〉5 的接線只列 `cmd_guard_kill` 多一個 `merge`。
- 〈做法〉2 要求基準上限不超過「這次呼叫剩下的總時限」,從 `t0` 算起。`t0` 與 `max_seconds` 在 `_ChoiceKillRun`(`lumos:78444`),`cmd_guard_kill` 手上只有 `should_stop` 這個回呼。
- 〈做法〉4 要求第一個訊號能收掉合併快篩,而 `st` 在 `_ChoiceKillRun.run` 的 with 區塊裡。
- 這兩個資訊 `merge` 帶不了。既有慣例是 choice-kill 要的東西打包成 hooks:`_KillHooks`(`lumos:28648`)包 `stop_group_on`、`on_row`、`should_stop`,都不傳就什麼都不做。
- spec 沒說期限怎麼進去、合併邏輯是放 `_KillHooks` 還是直接擠進已經很長的 `cmd_guard_kill`。實作者會自己再加參數,等於再開一種慣例。
- 引句:「`cmd_guard_kill` 多一個選用參數 `merge`」
- 引句:「處理器多做的那一步用一個選用的回呼掛在 `st` 上」
- file: `scripts/lumos:28648`
- file: `scripts/lumos:78444`

### 四、合併快篩的 Popen 另開一張登記,跟既有的兩張並行 ⚠
severity: minor
blocking: 否

- 既有登記有兩種:
  - `_KILL_RUN_LIVE`(`lumos:28162`):`_kill_run` 開完程序就登記 pid → Popen,第二個訊號強制結束時 `_situation_rule_force_exit` 讀它(`lumos:76596`)。
  - `started` 參數:合約測試閘用 `_BtProcs`(`lumos:28168`)。
- spec 再加一個「模組層變數」,值是合併快篩的 Popen,第一個訊號時讀它。
- 它存的是 `_KILL_RUN_LIVE` 的子集。如果只是要區分「這支是合併快篩」,可以在既有登記上帶標記,或讓 `_kill_run` 多一個選用參數,不必另開一張表。
- spec 也沒說 `_kill_run` 怎麼知道這一支是合併快篩。`_kill_run` 是 `bound-tests-gate`、guard kill、人裁共用的入口。我判不準另開是否必要,交編排者。
- 引句:「合併快篩開跑時把它的 Popen 記在一個模組層變數」
- file: `scripts/lumos:28162`
- file: `scripts/lumos:28168`
- file: `scripts/lumos:76596`

### 五、結果資料夾的路徑組合與圍欄沒指到既有的單一入口
severity: minor
blocking: 否

- 〈做法〉1 的結果資料夾是 `<執行目錄>/<-p 的值>/<模組各段>/build/test-results/<任務名>/`,而 `-p` 可能是絕對路徑。
- 「絕對路徑照用、相對接根」只准在 `_under_root`(`lumos:16833`)。
- 守衛測試 `t_nogo_shared_helpers_used`(`test_lumos.py:80589`)用語法樹掃全檔,檢查這種寫法只在那一支裡。實作者手寫一遍就會紅。
- 同類路徑邏輯既有的對照:`lumos:77051` 的 `_under_root(pentry["root"], pdir)`,以及 `_kill_run_dir` 對「解析後逃出工作樹」的圍欄(`lumos:26819`)。
- spec 只寫「真實路徑不在工作樹裡就不合併」,沒指名這兩個。
- 引句:「每次合併呼叫之前刪掉這個資料夾,讀到的一定是這次寫的。」
- file: `scripts/lumos:16833`
- file: `scripts/lumos:77051`
- file: `scripts/test_lumos.py:80589`

### 六、第一個訊號的改動寫進規格閘,但它的家是 guard-kill
severity: minor
blocking: 否

- 〈落點〉把「第一個訊號收掉合併快篩」放在 `[[Systems/規格閘]]`。
- 被改的是 `_situation_rule_signals` 的處理器與 `_kill_run`。
- `_situation_rule_signals` 與 `_KILL_RUN_LIVE` 只在 `Systems/guard-kill.md` 有記載;`Systems/規格閘.md` 沒有,我 grep 過。
- 這一條該寫進 guard-kill,否則兩篇對「訊號怎麼收」各說各的。規格閘只需記 `_ChoiceKillRun.run` 掛回呼那一步。
- 引句:「第一個訊號收掉合併快篩、帳與 run 的新欄位。」
- file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md`
- file: `scripts/lumos:76614`

不對齊共 6 條
