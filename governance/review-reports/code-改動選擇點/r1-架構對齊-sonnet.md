severity: major

## a1 選擇點的「是不是主線」自己手寫一套,沒走專案共用的主線判法
severity: major
blocking: 是 — 引入第二種做法:鄰居已有同功能的共用函式,新碼另寫一套,而且兩套對同一個輸入給出不同答案。

- 輸入:遠端名帶斜線(例:`my/fork`)、遠端 HEAD 指到 `trunk`,目前就在 `trunk` 上,跑 `lumos choice-points` 不帶 `--diff`。
- 路徑:`cmd_choice_points` → `_choice_range`,該函式自己下 `symbolic-ref refs/remotes/<遠端>/HEAD`,再用 `split("/", 1)[-1]` 取分支名,另加固定名 main、master 來判斷「目前分支是不是主線」。
- 壞在哪:`--short` 回 `my/fork/trunk`,切完得 `fork/trunk`,認不出 `trunk` 就是主線。預期是回「目前分支就是主線,帶 --diff」並 rc 2。實際沒擋,範圍變成從空樹(`4b825dc6…`)起算,整個 repo 都當成改到的行。
- 鄰居的做法:`_note_reread_mainline_names` 與 `_push_mainlines` 是共用的主線判法。它會取遠端 HEAD 與 main/master upstream 等候選,遠端名依 `git remote` 取最長相符(註解特別寫了遠端名可以帶斜線)。

引句:「if name and name in ("main", "master", default):」

重現:我在臨時副本建一個遠端名 `my/fork` 的 repo,在 `trunk` 分支上,對被審版本(7826895)的 scripts/lumos 呼叫兩個函式。
- `_note_reread_mainline_names(rr, tip)` 回 `['main','master','trunk']`,認得 trunk 是主線。
- `_choice_range(rr, None, None)` 回 `('4b825dc6…..188a5ef2…', …, None)`,沒擋,範圍從空樹起算。

對照:`scripts/lumos` 在 7826895 版的 `_note_reread_mainline_names`(約第 57620 行)、`_push_mainlines`(約第 69327 行)。實驗目錄已刪。

## a2 治理帳寫入失敗的判法,新碼內部兩種寫法,跟專案的警告輔助函式也不同
severity: minor
blocking: 否 — 錯誤處理與日誌寫法跟鄰居不一致,但結構是對的。

- `_choice_push_event` 用 `is False` 判失敗,語意同 `_gate_event_or_warn`(None 表示這個 repo 沒有治理帳,不是故障)。
- `_choice_record` 與 `_choice_kill_report` 用 `is not True`,把 None 也當成「寫不進去」並印警告。
- 同一個 `_gate_event` 的回傳,新碼內部兩種判法,也沒呼叫鄰居的 `_gate_event_or_warn`(`scripts/lumos:1925`)。
- 鄰居本身也混用(`_situation_rule_point_record` 沿用既有的 `is not True`),所以 ⚠ 交編排者判:要不要把選擇點這幾處收斂成同一種。

引句:「if _gate_event(rr, _CHOICE_KILL_GATE, kind, note[:400], hard=(kind == "blocked"), head_sha=at_sha, nodes=[], extra=extra) is False:」

## a3 `check.py --catalog-only` 忽略 `--sg`
severity: minor
blocking: 否 — 命名與參數處理跟同檔主流程不一致,結構對。

- 主流程用 `--sg <路徑>`,沒帶才退到 `shutil.which("ast-grep")`。
- `--catalog-only` 分支現在也需要 ast-grep 來跑選擇點樣本,卻只用 `shutil.which`,不讀 `--sg`。
- 場景:ast-grep 不在 PATH 但有帶 `--sg`,會印「選擇點規則樣本:沒檢查到(沒裝 ast-grep)」,與主流程不一致。

引句:「sg_c = shutil.which("ast-grep")   # 選擇點規則樣本要真的 ast-grep;沒裝只印「沒檢查到」,不算型錄問題」

對照:`configs/ast-grep/kotlin-android/check.py:364`(主流程的 `--sg` 處理)。

## 三問逐問判定(其餘全數對齊)

1. 分層與依賴方向:對齊。
   - 新碼放在 `scripts/lumos` 單檔,沒有跨層直呼。
   - 治理帳走 `_gate_event`、`_gate_event_fit`、`_gov_vc_gate_events`、`_gov_rows_at`。
   - 放行檔走 `_lint_waivers_load`,並從它抽出 `_lint_waivers_parse` 共用。
   - 隔離工作樹不另建,批次交 `cmd_guard_kill(recipes_override, source, on_row, should_stop)`,沿用它的隔離。
   - ast-grep 子程序走 `_lint_spawn`、`_lint_wt_resolve_tool`、`_lint_wt_cfg_inside`(從 `_lint_wt_allow` 抽出)。
   - 改到的行走 `_kt_sit_hunks`、`_kt_sit_hits`。
   - 推送範圍起點走單一來源 `_push_range_start`,改動清單走 `_sc_changed_files`。
   - 抽取的幾處(`_plan_live`、`_situation_rule_same_id`、`_lint_waive_prep`、`_situation_rule_platform_for`、`_table_header`、`section_table`)都標明語意不變並被舊呼叫端沿用。
   - 唯一例外是 a1。
2. 命名與錯誤處理:大致對齊。
   - 擋下訊息(「擋下:…」加 rc 2)、`_situation_rule_say`、`_kill_esc`、推送前掛鉤的 `[spec-gate 推送前]` 前綴,都跟鄰居一致。
   - `--push-remote` 與 `--pushed-ref` 只給一個 rc 2,跟 drift、room-guard 的先例同(`scripts/lumos:53098`、`57384`、`61694`)。
   - 掛鉤的 `_SG_PR` 探測沿用 `_PF_PR` 的 grep dest 字樣做法。
   - 新閘名 `choice-kill` 登記進 `_KNOWN_GATES`,跟 situation-rule 的登記方式一樣。
   - 不一致處見 a2、a3。
3. 第二種做法:除 a1 外沒有。
   - 另一套放行檔格式?沒有,選擇點放行沿用 `.lumos/lint-waivers.json` 與 `lint-waive`,只加 `choice:` 前綴。
   - 另一套讀帳?沒有,被推版本讀帳走 `_gov_rows_at`、`_residual_blob_at`。
   - 另一套隔離工作樹?沒有。
   - 新的 ast-grep 掃描是新功能,沒有既有同功能函式可借,不算第二種做法。
   - 另一個放寬(`.lumos/config.json` 的 `max_file_bytes`)是專案既有設定鍵,不是新做法。

最嚴重:major;blocking 共 1 條
不對齊共 3 條,其中 major 1 條
