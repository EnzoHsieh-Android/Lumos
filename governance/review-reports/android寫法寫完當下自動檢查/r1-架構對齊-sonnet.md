severity: major

## 問 1. 分層與依賴方向

大方向對得上:判斷在 lumos 本體,鉤子只印。改檔前推列「比對在 lumos 本體做,鉤子只印」,跟既有 `impact-hook.py` 呼叫 `lumos impact --stdin-payload` 的分工一致。回合結束鉤子呼叫 `lumos lint-new`,也跟既有「鉤子 subprocess 呼叫 lumos」同向,例如 `scripts/hooks/claude/check-graph-sync.py:750`。以下幾處不一致。

**F1(工作樹改動清單的解析,第二種做法)**
severity: major
- blocking: 是
- ⚠ 判不準:新解析器可能有正當理由(`u` 與 `2` 的舊路徑),請編排者裁。但 v1 `-z` 也給得出這兩樣。
- 引句:「改讀 `git --no-optional-locks status --porcelain=v2 -z --untracked-files=all`」
- file: `scripts/lumos:68669` 已有 `_porcelain_z_paths`(`-z` 解析)。
- file: `scripts/lumos:50428` 的 `_handoff_files` 附近:要帶狀態碼時用 `--porcelain=v1 -z --untracked-files=all` 自己解。註解寫明先例是 `_handoff_files`(代碼審 r2 架構對齊席 A1)。
- file: `scripts/hooks/claude/check-graph-sync.py:330` 的 `_git_status_entries`。
- 這份計劃在 lumos 本體再加一支 v2 解析器,既有已有兩種寫法。v1 `-z` 同樣給得出 `R` 的舊路徑與未合併碼,沒有非加 v2 不可的理由。計劃的 `u`、`2`、`?` 三類可以用既有解析器的狀態碼處理。
- 建議:沿用 `_handoff_files` 一族的 v1 `-z` 寫法,或在計劃裡寫明 v1 做不到什麼。

**F2(代碼審通過前的「兩道一律都判完」,第二種做法)**
severity: major
- blocking: 是
- 引句:「兩道一律都判完,前面那道出錯不會讓後面那道不跑;推送檢查與 `lumos code-loop pass` 都呼叫它。」
- file: `scripts/lumos:70822-70852` 的 `_CodeloopKg` 與 `_codeloop_kg_finish`,以及 `scripts/lumos:70921-71034` 的 `_codeloop_guard_verdict(keep_going=...)`。
- 既有已有「每道都判完、擋下累積進 blocks、所有回傳經 `_fin` 一處判」的收集模式。注釋寫明 pitfalls 失敗時「新增告警閘只看範圍,照跑」(`scripts/lumos:71012`)。
- 計劃另抽一支新共用函式,等於同一件事有兩套累積擋下的做法。
- 建議:給 `keep_going` 路徑加「只跑這兩道、不含留痕那道」的選項,而不是另抽一支。

**F3(回合結束鉤子自己先判一次宣告檔是否已提交)**
severity: minor
- blocking: 否
- 引句:「而且它與 `.lumos/config.json` 的工作樹內容都跟 HEAD 那一版相同」
- 同一條在範圍 2 又寫了一遍:「宣告檔 `.lumos/lint.json` 與 `.lumos/config.json` 的工作樹內容要跟 HEAD 那一版位元組相同才跑」,由 lumos 本體判。
- 鉤子與 lumos 各判一次,是判斷散在兩層。既有鉤子除了 `_git_status_entries` 問版本控制外,把判斷交給 lumos(`check-graph-sync.py:750`)。
- 建議:鉤子只在專案根沒有 `.lumos/lint.json` 時略過,其餘交給 `lint-new` 的 rc3 處理。

**F4(子程序管理)**
severity: minor
- blocking: 否
- ⚠ 判不準:可能算「新的子程序管理方式」而升 major。
- 引句:「用新程序群組開、逾時整個群組一起殺」
- file: `scripts/lumos:26288` 已有 `_kill_proc_group`(`start_new_session` 加 `killpg`)。
- file: `scripts/hooks/claude/check-graph-sync.py:750` 的鉤子自己是 `subprocess.run(..., timeout=...)`,沒有群組。
- 鉤子是獨立檔、不 import 主程式,要用就得抄一份,跟 `_stop_dir_ok` 抄兩份同樣有漂移風險。
- 鉤子裡內層 `lint-new` 自己的快工具已經走群組殺(`scripts/lumos:39185`)。
- 建議:說明鉤子層為何還需要外層群組殺,或維持既有的 `subprocess.run` 加 `timeout`。

## 問 2. 命名與錯誤處理

對得上的:
- `LUMOS_STOP_LINT_OFF` 對應 `LUMOS_STOP_BLOCK_OFF`(`check-graph-sync.py:891`)。
- `lint_new.worktree_tools` 走 `_lint_new_config`(`scripts/lumos:39463`),snake_case,字串清單的驗證寫法同 `include_test_paths`。
- 指令名 `lint-new` 對應 `lint-check`、`lint-waive`(`scripts/lumos:72600`)。
- 鉤子上限改在 `HOOK_BUDGET`(`merge-claude-settings.py:110`),沒有第二個來源。

**F5(退出碼與記帳)**
severity: minor
- blocking: 否
- 引句:「這支指令不寫治理帳(放行帳只有推送前閘記)。」
- file: `scripts/lumos:70869-70895` 的 `_codeloop_lint_new_step`:`env-unavailable` 時自動放行並記 `_gate_failopen`。
- 計劃的 `lint-new --diff` 把 `env-unavailable` 歸 rc3「不算乾淨」,同時範圍 5 讓推送檢查與 `pass` 共用函式。
- 計劃沒寫共用函式裡 `env-unavailable` 是放行記帳(既有)還是擋(rc3 的語意)。
- 同一個狀態在 CLI、推送閘、`pass` 三處可能有三種結局。
- 建議:寫明三處對 `env-unavailable` 的處理表,並說明 `pass` 沿用推送閘的 failopen 加記帳。

## 問 3. 第二種做法

**F6(回合結束的擋停名額標記,新格式)**
severity: major
- blocking: 是
- 引句:「名額標記是新格式(既有那道是「每會談一個空檔、用獨佔建立搶名額」,裝不下批次與次數)」
- file: `scripts/hooks/claude/check-graph-sync.py:910-925` 的 `_stop_mark_write`:`O_CREAT|O_EXCL`,原子佔名額,「兩個 hook 同時來只有一個成功」。
- file: `check-graph-sync.py:413-432` 的 `_load_printed` 與 `_save_printed`:同一套信任目錄檢查(`_stop_dir_ok`)下,已有「每會談一個 JSON 檔」的格式,另一個目錄 `stop-printed` 存放。
- 計劃在 `stop-block` 目錄再塞 `<會談>.lint.json`,是第三種標記格式,而且讀改寫不是原子的,丟掉既有刻意保留的 `O_EXCL` 保證。
- 同目錄的既有不變量「只有擋過的會談才留東西」與時間戳檔(見 F8)放哪也沒對齊。
- 「裝不下批次與次數」不成立:可以用 `O_EXCL` 建 `<會談>.lint-<批次雜湊>` 一批一檔,次數就是同會談前綴檔數,仍是原子的。
- 建議:沿用「一個名額一個 `O_EXCL` 檔」的做法,或說明為何不行。

**F7(改檔前「已推過」標記,新格式)**
severity: major
- blocking: 是
- 引句:「新標記(既有的只講一次標記鍵是失敗代碼、先寫後印,冷卻標記鍵是檔案路徑,都不合用)」
- file: `scripts/hooks/claude/impact-hook.py:825-833` 的 `_voice_once`:在 `tempfile.gettempdir()/lumos-impact-<sid>/voice-<code>` 下 `marker.touch(exist_ok=False)`,「鍵」可以是任何字串。
- file: `impact-hook.py:171-176` 的 `_ttl_marker_path`:同一個 `lumos-impact-<sid>/` 目錄。
- 同目錄下 `voice-<code>` 的做法,把 `<code>` 換成 `row-D-12` 就能用,「鍵是失敗代碼」不成立,它是任意字串。計劃卻另立「目錄外、一會談一個、一行一個列編號」的檔案,位置與格式都不同。
- 「印完才寫標記」的次序差異,可以用同一個目錄與同一個 touch 寫法,在印之後呼叫。
- 建議:沿用 `lumos-impact-<sid>/` 目錄,改成 `row-<編號>` 一列一檔,並在印出後建立。

**F8(「這一回合」邊界的第二種定義)**
severity: major
- blocking: 是
- ⚠ 判不準:計劃有寫理由(擋停回饋與壓縮接續在逐字稿裡跟使用者輸入同形),但既有程式碼的判斷也是在同一支鉤子裡。請編排者裁是否算第二種做法。
- 引句:「回合結束鉤子每次跑都在自己的標記目錄寫一個這個會談的時間戳檔(新增),下一次讀它」
- file: `scripts/hooks/claude/check-graph-sync.py:204` 的 `collect_turn_actions`:從尾端反向掃到最近一個真實使用者輸入。
- file: `check-graph-sync.py:102` 的 `_is_real_user_input`。
- file: `check-graph-sync.py:330` 的 `_git_status_entries`:2026-09-18 起「問版本控制」,刻意不靠回合邊界。
- 同一支鉤子裡,「這一回合」有兩種定義:既有的逐字稿反向掃,與新增的時間戳加修改時間。
- 時間戳檔每次收工都寫,跟 `stop-block` 目錄「只有擋過的會談才留東西」的既有不變量是否衝突,計劃沒交代放哪個目錄。
- 計劃還寫「逐字稿只從尾端往前讀到這一回合的開頭」,與「不用逐字稿判回合開始」互相矛盾。
- 建議:沿用 `_is_real_user_input` 在尾端讀的邊界定義,或明講為何不能、並讓兩道共用一種定義。

## 問 4. 落點

**F9(`HOOK_BUDGET` 與鉤子檔的家)**
severity: minor
- blocking: 否
- 引句:「鉤子時間上限從 40 秒加到 50 秒。」
- file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:9-14`:`about_code` 含 `scripts/merge-claude-settings.py`、`check-graph-sync.py`、`impact-hook.py`。
- file: `Systems/hook逾時預算.md:7`:`about_code: []`,是預算脈絡的節點但沒有掛檔。
- 計劃的 `lands_in` 沒有 `Systems/codex-harness`,也沒有 `Systems/hook逾時預算`。
- 改到 `merge-claude-settings.py`(`HOOK_BUDGET` 40 改 50),違反「改到的每支檔都得先有家,且寫進那個家」。
- `impact-hook.py` 有兩個家:`Systems/改檔前推播`(`about_code`)與 `Systems/棧別提問表態閘`(`about_code` 也列了)。計劃的 `lands_in` 兩篇都列,但沒說各寫什麼。
- 建議:`lands_in` 補 `Systems/hook逾時預算`,50 秒與公式的說明寫那裡。

**F10(`graph-sync-coverage` 的範圍不符)**
severity: minor
- blocking: 否
- ⚠ 判不準:也可能認為鉤子同檔所以放同一篇。
- 引句:「收工點名那支回合結束鉤子(Claude 與 Codex 共用)多一道「寫法檢查」」
- file: `Systems/graph-sync-coverage.md:34-37`:管 `check-graph-sync.py`、`scripts/lumos`、`probe_sync.py`,節點主題是圖譜同步覆蓋率。
- 寫法檢查跟圖譜同步是兩件事,只是共用同一支鉤子檔。落進這一篇會讓節點的責任範圍膨脹。
- `pitfalls-code-loop` 本身已是 20 KEY、沒寫負責範圍的大節點(管 `scripts/lumos`);新增 `lint-new` 指令、工作樹終點、Kotlin 剝字串函式、決策表讀表函式都往那裡堆,同樣膨脹。
- 建議:考慮為「回合結束寫法檢查」另開一篇 Systems 節點(`lumos new system`),`lands_in` 只在其他節點留一行 `SEE:`。

## 對齊的部分(不列為不對齊)

- 設定鍵讀法:`lint_new.worktree_tools` 走既有 `_lint_new_config`(`scripts/lumos:39463`)。
- 環境變數命名:`LUMOS_STOP_LINT_OFF` 對應 `LUMOS_STOP_BLOCK_OFF`。
- `stop_hook_active` 與「會談標記」兩道護欄的組合。
- 工作樹模式不寫治理帳:判定函式只回傳、帳由上層寫,同 `_lint_new_verdict` 的既有慣例(`scripts/lumos:39856` 注釋)。

不對齊共 10 條,其中 major 5 條(F1、F2、F6、F7、F8)
