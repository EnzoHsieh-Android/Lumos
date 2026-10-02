severity: major

# 整合-sonnet 席報告(鏡頭:整合與接手)

白話:我假裝三個月後第一次照這份計劃動手。大部分「接線」的地方都對得上現況(函式、旗標、帳的型別我都開檔核過),但有三處會讓接手的人撞牆:一個條款字面上寫不出測試、一個測試被誤說成會被保護、一條操作手冊漏講會超時。其餘是補充與清單。

驗證用的複本:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/f0-r1-work-整合-sonnet/repo`(`git clone --shared`,只讀、未改任何檔)。

## F1 S8 要求 escalate 狀態也印提醒,但帶輪次的代碼審迴圈根本走不到 escalate
severity: major
blocking: 是
引句:「五個狀態(`plant-canary`、`gate-pending`、`converged`、`cap-reached`、`escalate`)都應印」
file: `scripts/lumos:11609`(light 分級遇到帶 `--round` 的記錄直接 rc2)
file: `scripts/lumos:11831`(escalate 只在 light 時才進)
file: `scripts/lumos:8750`(處置帳 `--findings-set` 必綁 `--round`,否則 rc2)

1. 提醒的前提是「審查帳最新一輪的載體席有折入發現」,而載體席(帶 `--findings-set` 那筆)寫入時一定要有 `--round`(`cmd_canary` 8750 行,否則 rc2)。
2. `cmd_loop_next` 的 escalate 只在 `light` 分級進(11831 行);而 `light` 遇到帶輪次的記錄,在更前面就回 2(11609 行)。所以「有載體席」與「escalate」不可能同時成立。
3. 實測(複本內):`canary record none --loop code-t1 --round r1 --tier light …` 記得進去,接著 `loop next code-t1 --tier light --orchestrator claude --json` 輸出「擋下:light 分級只能用單人、不分輪次的記錄…」,rc 2,不是 escalate。
4. 後果:S8 的 `t_loop_next_fix_check_reminder` 照字面寫不出 escalate 那一格的夾具;接手者要嘛偽造一本矛盾的帳(而 `loop next` 會先擋掉),要嘛默默刪掉這格、條款與測試對不上。
5. 修法方向(只描述,不替作者寫):S8 改成四個狀態,並在〈做法〉明講「escalate 不可能有載體席,所以天然不印,不必處理」。
6. 順帶:〈做法〉寫「設計審迴圈不印」,但 `_roster_kind` 對 `caphint` 這種既非 `code-` 也非 `design-` 的編號回 None(既有測試 `t_loop_next_cap_hint_*` 用這類編號)。要明講「只有 `code-` 開頭才印」,否則實作者會寫成「不是 design 就印」而讓那批既有夾具多出一行。

## F2 操作手冊沒講這個指令一次要 5 分鐘以上,預設 2 分鐘逾時會殺掉它
severity: major
blocking: 是
引句:「受波及合約測試在樹裡實測 59 支 258 秒;一次大約 5 分鐘,多半花在合約測試。」
file: `scripts/lumos:38353`(整套跑逾時下限 600 秒 `_BOUND_TESTS_WHOLE_SUITE_TIMEOUT`)

1. 〈要同步的文件〉只列「第 7 步之後跑 `lumos loop fix-check`」,沒有一句提到要背景執行或拉長逾時。Claude Code 的 Bash 預設逾時是 120 秒、上限 600 秒。
2. 我在複本裡跑 `python3.14 scripts/test_lumos.py -k guard_kill`(計劃自己指定的回歸子集):被自動丟到背景,實際跑了 5 分 02 秒、257 案例全綠。也就是計劃寫的「`-k guard_kill`、`-k spec_gate` 子集當回歸」本身就超過 2 分鐘。
3. 照做會發生的事:接手者在前景敲 `lumos loop fix-check`,120 秒被殺 → 沒有走到「記帳、收樹」那一步 → 治理帳沒有事件,`loop next` 永遠提醒;樹與孤兒子行程留到一天後清(計劃已承認孤兒行為,但沒承認「預設設定下必發生」)。
4. 連帶污染量測:REVISIT 與 RETIRE-IF 靠治理帳的次數、耗時、跳過比例;被殺的跑次不留事件,「中位數耗時」會被低估、「跳過比例」被扭曲。
5. 需要補:手冊第 7 步之後那句要寫明「背景執行或逾時調到 600000 毫秒」;〈做法〉要決定被中斷時要不要至少收樹(目前明說不改 `_kill_run`,那就至少在 `try/finally` 收自己的樹,SIGTERM 另論)。
6. 未實測 `fix-check`(尚未存在);依據是上面 `-k guard_kill` 的實測加計劃自己的 258 秒數字。

## F3 規格閘「跑一批測試再逐支判」其實有三處,不是兩處;`per_prof` 也不是從 `_platform_test_index` 取得
severity: minor
blocking: 否
引句:「規格閘的條款測試與相依回歸兩處」
file: `scripts/lumos:6628`(條款,`_spec_gate_run_clauses`)
file: `scripts/lumos:6664`(相依回歸,`_spec_gate_regress`)
file: `scripts/lumos:7045`(推送前,`_spec_gate_push_one`,第三份手寫副本)
file: `scripts/lumos:6769`(`per_prof` 是 `cmd_spec_gate` 裡的區域函式,不是回傳值)

1. 第三份(7045 行)同樣是 `_run_bound_tests` → `_ran_count` → `_spec_gate_declared` → `_spec_gate_verdict`,只是 profile 名用 `(plats.get(pl) or {}).get("profile_name")` 現場取、tails 的鍵是 `loop_id`。計劃的共用函式 `_spec_gate_judge_items(根, 測試清單, per_prof, loose_for)` 吃得下它,但計劃沒說要不要一併改。不改=抽完還是兩份手寫+一份共用,正是計劃想消滅的漂移;改了就多碰 `-k prepush_spec_gate` 那批。
2. 〈做法〉「修正關卡在樹裡自己用 `load_platforms(樹)` 與 `_platform_test_index(樹)` 取 `per_prof`、`loose_for`」:`_platform_test_index` 回六個值,只有 `loose_for` 在裡面;`per_prof` 要自己用 `load_platforms(樹)["platforms"][平台]["profile_name"]` 組。實作者會照字面去找一個不存在的回傳值。
3. 新程式碼若解構 `_platform_test_index` 必須剛好六個、且不能把整包存進 dict:既有守衛 `t_platform_index_consumers_drift_guard`(`scripts/test_lumos.py`)用語法樹掃全 repo,會對新程式碼翻紅。〈既有測試〉那條沒列它。

## F4 說「既有測試要同步填值」是錯的:那支測試只跑第 1 輪,範本在第 1 輪根本沒有 `--regression-set`
severity: major
blocking: 是
引句:「既有測試 `t_loop_next_disposal_cmd_actually_runs` 會把範本填值後真跑,要同步給這個佔位填值。」
file: `scripts/test_lumos.py:23974`(該測試的夾具是全新迴圈 `t5-…`,`loop next` 吐的是 round 1)
file: `scripts/lumos:11639`(`rmode`)與 `scripts/lumos:11663`(`disposal_cmd` 組字串)

1. 計劃自己規定「第 2 輪起」才多帶 `--regression-set <id串|none>`。該測試用全新迴圈叫 `loop next`,n_next=1,範本根本不含新旗標;實作者照計劃去「同步填值」會發現沒東西可填,結論多半是「不用改」。
2. 結果:第 2 輪起那份範本沒有任何「真跑」的測試。這正是該測試要防的病(它的 docstring:「工具吐的指令必須跑得動,字串斷言只證長得對」;`record_cmd` 曾因寫側新規變成照抄必 rc2)。S8 對範本只斷言「應含 `--regression-set`」(字串存在),不是真跑。
3. `.replace("<id串>", "F1", 1)` 只換第一個,新佔位 `<id串|none>` 不含子字串 `<id串>`,不會被誤換,但填值後的 `"<" not in filled` 檢查會在第 2 輪紅——所以要新寫「先記第 1 輪、再取第 2 輪範本、填 `none`、真跑 rc0」的測試,不是改舊測試。
4. 另外:文字模式不印 `disposal_cmd`(`for k in ("canary_type", "record_cmd", …)` 在 11801 行),計劃已承認只在 `--json`;但手冊第 6 步的使用者看的是 `record_cmd`,不會被提示 `--regression-set`。「第 2 輪起要帶」靠手冊文字,沒有機械提示。

## F5 要同步的文件清單漏了三處,其中一處會讓既有測試翻紅
severity: minor
blocking: 否
引句:「lumos-code-loop 手冊——第 2 步(派工單寫 `base_commit`)、第 5 步(修完先提交、寫修正紀錄,可用 `--record-template`)」
file: `skills/lumos-code-loop/SKILL.md:18`(「一輪怎麼跑」)
file: `skills/lumos-code-loop/reference.md:560-575`(「每一輪的現行步驟」,同一組 1–8 步的另一份)
file: `scripts/test_lumos.py:42373`(`t_skill_entry_pages_no_dated_history`:入口頁日期 ≤3)

1. `SKILL.md` 入口頁現在正好 3 個日期(2026-09-12、2026-09-30、2026-08-25,我數過)。接手者照慣例寫「(2026-10-xx 起)」就是第 4 個,`t_skill_entry_pages_no_dated_history` 翻紅。要在計劃裡寫「手冊新增段落不寫日期」。
2. `reference.md` 有一份獨立的步驟 1–8(含「派工單落 `rN-dispatch.json`」),計劃只列 `SKILL.md`。兩份各說各話就是計劃自己在別處警告過的「版本行為一變就要改三處」。`_SEC_SEAT_DOC_FILES`(`scripts/test_lumos.py`)已有「多檔同步守衛」的前例,這次沒有守衛、只能靠清單。
3. `skills/lumos-project-notes/commands/INDEX.md` 的第 36 列(代碼審那一列)沒列 `loop fix-check`;`t_command_index_complete` 只要求任一 `commands/*.md` 出現 `loop fix-check`(寫進 06 就過),但 INDEX 目前 4211/4500 字元,多寫一個指令名約佔 20 字,沒問題;只是計劃沒提 INDEX,接手者可能不知道有 4500 上限。
4. 新指令要過的既有測試(我逐一核過):`t_every_subcommand_has_when`(`--help` 要有「什麼時候用:」,來自 `HELP_WHEN["loop fix-check"]` 或 `add_parser(description=…)`)、`t_command_index_complete`(上述)。`lumos loop next` 的另外幾條不受影響。

## F6 〈清殘骸〉的「照 `_lint_new_clean_stale`」對不上現況,S11 的測試夾具沒講怎麼做
severity: minor
blocking: 否
引句:「(寫法照 `_lint_new_clean_stale`,時限沿用 `_LINT_NEW_STALE_SEC`」
file: `scripts/lumos:23798`(`_lint_new_clean_stale` 掃的是 `<repo>/.lumos/lintbase-*`,用 `shutil.rmtree`,沒有 worktree、不碰系統暫存)

1. 實際沒有任何現成函式在掃系統暫存資料夾、也沒有處理 worktree 的「先 remove 再 rmtree 再 prune」;`guard kill` 只在自己這次的 finally 收。清殘骸是全新程式,「照 X 寫」只借了「mtime 超過 `_LINT_NEW_STALE_SEC` 就清」這一個點。
2. 計劃沒定:①「系統暫存資料夾」是 `tempfile.gettempdir()`(才會吃 `TMPDIR`)還是寫死 `/tmp`;②`git worktree remove --force` 用哪個 repo 的 `-C`(別的 repo 留下的殘骸,用本 repo 的 git 會回「不是工作樹」,接著 rmtree 掉資料夾,但那個 repo 的 `.git/worktrees/` 登記要等它自己 prune);③「比對前兩邊路徑都先取實際路徑」兩邊是指哪兩邊(git 的 `worktree list` 與資料夾路徑?)。
3. S11 的測試要「到期的清、不到期的與別的前綴不動」:必須 `os.utime` 把假殘骸的 mtime 往前調,且必須把 `TMPDIR` 指到夾具資料夾,否則測試會去清真實 `/tmp` 裡別的會談的同前綴樹。這點要寫進計劃,不然夾具寫成讀寫真實 `/tmp`。
4. guard kill 的前綴現在是 `lumos-kill-`(`scripts/lumos:14153`);共用函式的前綴參數必須讓兩者不同,否則修正關卡的清殘骸會掃到 guard kill 還在跑的樹(同一天內不會被清,所以只有跨天長跑才會撞——低機率,但前綴要在計劃裡定死)。

## F7 提醒行的 JSON 形狀沒定義,文字模式的列印路徑也沒定義插在哪
severity: minor
blocking: 否
引句:「文字模式與 `--json` 兩條輸出都要接(文字模式只印選定的鍵)」
file: `scripts/lumos:11801`(文字模式逐鍵印 `  {k}: {out[k]}`)
file: `scripts/test_lumos.py:33951`(`t_loop_next_cap_hint_appended_without_changing_phase`:`[cap-hint]` 之後的每一行都要以兩個空白開頭)

1. `fix_check` 欄位是字串還是物件(狀態/指令/原因)沒定。文字模式的鍵迴圈對值直接 `print(f"{k}: {out[k]}")`,物件會印出 Python 字典字面。S8 要斷言「改印已跳過」「附 `lumos loop fix-check` 指令」,得先定形狀。
2. 提醒行必須印在 `[cap-hint]` 之前:計劃自己寫「到上限那條路尤其要印」,而既有守衛要求 `[cap-hint]` 之後全是縮排行、且「跑滿上限提示放最後」。把新行接在 cap hint 之後會在 code- 迴圈的 cap 夾具上翻紅(目前那批夾具用的編號不是 `code-`,所以現有測試不會立刻紅,是未來夾具會)。
3. 「有沒有要修正紀錄的折入」這個判斷在 `loop next` 與 `fix-check` 各算一次(計劃兩處都用同一句話描述)。沒指定共用同一個函式;兩邊一旦對 `finding_kinds` 缺漏時的處理不同(「沒有 finding_kinds 時全部折入都要」),會出現「`loop next` 一直提醒、`fix-check` 卻回『不用跑』」的死循環。建議明寫共用一支。

## F8 S7 的「既有三本帳」與實際不符;`LUMOS_SKIP_FIX_CHECK` 與前置檢查的先後沒定
severity: minor
blocking: 否
引句:「`lumos gov` 讀既有三本帳的筆數應跟加之前一樣」
file: `scripts/lumos:7577`(`_GOV_FIELD_TYPES` 七本帳共用)
file: `scripts/lumos:7649`(`.governance-log` 的 `token` 運算式,只對 canary/blocked 與 code-loop dispositions 有值)

1. 型別表是七本帳共用的(註解自己寫「七本帳共用一張表」),計劃說的「三本」我找不到對應。我對本機 `docs/.*.jsonl` 全部掃過:`secs` 只出現在治理帳(218 筆,都是 float,補 `(int, float)` 不會丟任何行)、`head_sha` 只出現在治理帳(1375 筆,都是字串)、`record_sha256`/`failed_items` 零筆。所以〈型別表補欄位〉在本 repo 是安全的,計劃的「實作時再掃一次」可保留,但該寫成一支測試(S7 的「筆數不變」)而不是靠人記得。
2. `token` 的運算式是一條串連的條件式,新增 fix-check 分支要放進去而不是另開鍵;`_is_advisory` 對 `warned` 且無 token 且無 detail 的事件會折疊,fix-check 的 `warned` 帶 token 與 note,不會被折,這是對的,但值得在 S7 補一句斷言(連跑兩次 `warned` 也要兩筆)。
3. `LUMOS_SKIP_FIX_CHECK=1` 與「迴圈不是 `code-` 開頭、輪次含 `/`」誰先判沒寫。其他三道閘(`LUMOS_SKIP_NOTE_AUDIT` 等)都是「先看環境變數就略過並記帳」;照那個慣例,跳過事件會帶任意 `loop`/`round` 字串進治理帳。要定:跳過也先驗編號形狀,或明說不驗。

## S1–S12 測試夾具需求(接手者照這個備料)
共同底:`_mk_bound_tests_repo`(`scripts/test_lumos.py:8600`)與 `_mk_spec_gate_repo`(`:47446`)可重用——都會建 git repo、`.lumos/config.json`、`tests/run.py {method}` 這種假執行器;`_sg_commit`(`:47860`)可重用。審查帳載體席直接寫 jsonl(像 `t_loop_next_roster` 的 `rec(...)`),不必走 `canary record` 的 `--report/--snapshot` 全套。

| 條款 | 夾具要有 |
|---|---|
| S1 | repo 兩個提交(base、修正後);載體席帶 `findings_set`/`folded_set`(含 `finding_kinds` 與不含兩種);修正紀錄 JSON 的各種缺法;一個中文檔名的 `fixed` 檔;一個修正後被刪掉的檔 |
| S2 | 帶空白/`-` 開頭的 base;`.lumos/config.json` 寫 `platforms.x.root: "../elsewhere"`;主工作目錄有未提交的受版控改動(要斷言「照常驗並列出」) |
| S3 | 測試名只出現在原始碼字串、不在測試索引的情況(例如寫在註解裡) |
| S4 | 同前綴兩支測試(`t_fcdemo` 與 `t_fcdemo_strip`);參數化的一支;`run_cmd` 不含 `{method}` 的平台;假執行器要印 `Ran N tests` 或 `N passed` 才讀得出支數(`_ran_count` 的 python 路徑) |
| S5 | 一篇帶 ★INVARIANT★ 的 Systems 筆記,正文用反引號寫程式檔路徑(`_bound_tests_for_diff` 靠 `impact --diff` 的 pinned);合約測試紅/綠兩版;多平台其中一個沒 `run_cmd`;`LUMOS_SKIP_BOUND_TESTS=1`;改名的程式檔 |
| S6 | 兩輪都有載體席與修正紀錄;`finding_severities` 有與沒有兩種 |
| S7 | 有 `docs/` 與沒有 `docs/` 兩個 repo;同提交連跑兩次;`lumos gov --since 9999 --full` 數筆 |
| S8 | 第 1、2 輪的載體席;五個狀態中 plant-canary、gate-pending(不給 `--spec`)好做;converged 要走 `--gate` 全過(連續乾淨輪、引用對得上),夾具重,沿用 `t_m1_loop_next`;cap-reached 要跑滿 `_TIER_PARAMS` 上限;escalate 做不出來(見 F1);手寫壞掉的治理帳行(`head_sha` 非 40 碼、型別錯) |
| S9 | 純 `canary record` 的 rc 斷言,夾具最輕;注意「同一輪先記的席位列不算別的輪次」要有兩筆同輪不同席的帳 |
| S10 | 派工單帶/不帶/壞掉 `base_commit` 三種(頂層是陣列也要一組);斷言 `git status` 不變 |
| S11 | `monkeypatch` 或環境變數讓 `git worktree add` 失敗(例如目標路徑已存在);兩個平台根的多平台 config;`os.utime` 做假殘骸;`TMPDIR` 指到夾具(見 F6) |
| S12 | `.lumos/config.json` 在主工作目錄但未提交(要有別的檔把它從 `git add` 排除,像 `_mk_bound_tests_repo` 若會提交 config 就要改);規格閘改前先錄一份「條款與相依回歸」逐字輸出當黃金檔,抽完比對 |

## 抽共用函式後會被碰到的既有測試(列名)
- guard kill(`-k guard_kill` 實測 257 案例、5 分 02 秒、全綠):`t_guard_kill`(`:20370`,含 `--keep-worktree` 情境 `:20245`)、`t_guard_kill_rc_precedence`(`:20179`)、`t_guard_kill_json_purity`(`:20216`)、`t_guard_kill_attribution`(`:20250`)、`t_guard_kill_no_stale_build_cache`(`:60865`)、`t_guard_kill_no_future_mtime`(`:60925`)、`t_kill_after_write_retry_no_future`(`:60944`)、`t_guard_kill_mtime_unsure_is_weak`(`:60964`)、`t_guard_kill_log_new_fields`(`:60187`)、`t_guard_kill_log_weak_sources`(`:60229`)、`t_guard_kill_add_warns_drifted_recipe`(`:60311`)、`t_kill_recipe_check_matches_guard_kill`(`:60671`)。沒有任何既有測試釘 `worktree add` 失敗字樣(`worktree add 失敗:`)、也沒有用 `git worktree list`;所以計劃說「先補兩條現在沒被釘住的行為」屬實。
- 規格閘(`-k spec_gate` 44 支):`t_spec_gate_regress_lists_linked_contract_tests`(`:47724`)、`t_spec_gate_regress_red_blocks`(`:47735`)、`t_spec_gate_regress_unbound_contract_flagged`(`:47747`)、`t_prepush_spec_gate_stale_record`(`:48195`)與同族推送前測試(若一併改第三處,見 F3)、`t_platform_index_consumers_drift_guard`。
- 治理帳:`t_gov_skips_bad_field_types`(`:55378`,逐欄型別跳過)、`t_gov_stats_gate_drift`(`:6458`,閘名字面值掃描:`_gate_event_or_warn(root, "fix-check", …)` 用位置參數,不會被 `"gate": "…"` 的字面掃描撈到,但 `_KNOWN_GATES` 漏登記只有 S7 會紅)、`t_gov_*` 全族(`-k gov`)。
- `loop next`:`t_loop_next_record_templates_use_current_kind`(`:22072`,斷言模板用 `none`)、`t_loop_next_disposal_cmd_actually_runs`(見 F4)、`t_loop_next_cap_hint_*`(見 F7)、`t_m1_loop_next`、`t_loop_next_roster`。

## 已讀,無 finding(核對過的接線)
- `_gate_event_or_warn(repo_root, gate, kind, note, **kw)` 簽名、沒有 `docs/` 回 `None` 且不印、寫失敗回 `False` 並印警告:與計劃描述一致(`scripts/lumos:1234`)。`extra` 鍵 `loop/round/record_sha256/secs/failed_items/token` 與 `_gate_event_build` 的固定鍵(`ts commit gate kind hard nodes note detail attempt_id ref head_sha`)無撞名。
- `_KNOWN_GATES` 必須加 `fix-check`:`_gate_event` 對不在名單的閘「不寫並回 False」(`:1220`),S7 會紅,計劃已預見。
- 派工單:本 repo 209 份 `code-*/rN-dispatch.json` 全是帶 `seats` 的物件,頂層加 `base_commit` 不影響 `_roster_dispatch_entries`(只讀 `auditor`)與 `cmd_seat_check`(只讀 `materials/round/seat/lens`)。
- 治理帳 15.76 MB(核對:`ls -l` 15764810 位元組)與計劃「約 16MB」一致;`_drift_jsonl_parse` 吃整份位元組、壞行自跳,語意符合計劃用法。
- `--regression-set` 要加進 `cmd_canary` 的位置:簽名在 `scripts/lumos:8422`、argparse 在 `:41075` 附近、分派在 `:42111`、「要跟 `--findings-set` 一起給」那串在 `:8566`;`--folded-set` 的 `_ids` 會把空字串變 `[]`,所以計劃「空字串回 2」必須在 `_ids` 之前自己判(接手者容易漏)。`_loop_records(env, loop)`(`:11090`)可取「別的輪次」。
- `_run_bound_tests(repo_root, items, tails)` 與 `_bound_tests_check(Path, range)` 的回傳形狀、status 字串集合、`not_run` 欄位:與計劃第 5 項的敘述逐項吻合;`tails` 以 `(node, plat, method)` 為鍵。
- 簿記白名單:`governance/review-reports/` 與 `docs/.governance-log.jsonl` 在 `_BOOKKEEPING_DIRS/_BOOKKEEPING_FILES`(`:22664`、`:22681`),所以「事件之後只提交審查帳不再提醒」的判法成立。壓提交(提交規範要求推前壓成一個)之後事件的 `head_sha` 不再是祖先,提醒會再出現——計劃的隱患節講了「寧多提醒」,沒講到「規定的推前壓提交也會觸發」,不是缺陷但要在手冊寫一句。
- guard kill 抽共用函式:現行寫法(`:14152` 起)在 `add` 失敗時 `continue`、成功後 finally 才收;with 區塊版本只要保證「失敗不丟例外、沒建樹也要刪暫存資料夾、有建樹才 `worktree remove` 與 `prune`」即與現制一致,計劃的描述足夠。

最高等級:major,blocking 共 3 條
