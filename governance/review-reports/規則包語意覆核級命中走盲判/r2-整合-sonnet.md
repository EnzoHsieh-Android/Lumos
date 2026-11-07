severity: major

整體判斷:第 2 版修掉了 r1 的主要方向(判誤報只留治理帳、宣告另開檔、共用 `_rule_review_hits`)。但補進來的段落有幾處自帶「沿用既有」的宣稱,對不上程式碼現況。我另外確認:Semgrep 九成底線與「判誤報藏起來、不自動關」屬實,兩級共 62 條、出處不全 7 條也屬實。ast-grep 沒裝,我沒辦法實跑規則。

severity: major
blocking: 是
判準:spec 說「沿用」的函式其簽名或形狀對不上,照做的人會卡住。
spec 段落:範圍 3(擋停)與範圍 6 的 `merge side`
問題:範圍 3 說合併提交那一側「照表態那一道 `_disp_bj_source` 的讀法」。但 `_disp_bj_source(rec, marker_branch, merge_ledger)` 要一筆表態紀錄 `rec`,靠 `rec["_merge_side"]` 分流,而規則判定沒有 `rec`。`_codeloop_lint_new_step(repo_root, diff_range, tier)` 也沒有 `marker_branch`、`marker_sha`、`raw_range`、`merge_cache`。它有兩個呼叫端:一般檢查與 pitfalls 失敗時的 `kg.lint_on_pf_fail`。另有 `code-loop pass` 的 `mech_only` 路徑。
問題 2:`_codeloop_merge_side_record` 只回一筆有效事件,規則判定要的卻是跨多次記帳、加上 overturn 事件的集合。
問題 3:`_codeloop_merge_side_lookup(..., kinds, ...)` 的 kinds 也沒說明。S12 因此沒有可實作的路徑。
引句:「分支、版本、合併提交那一側照表態那一道 `_disp_bj_source` 的讀法」
file: `scripts/lumos:74237`、`scripts/lumos:74556`、`scripts/lumos:73340`

severity: major
blocking: 是
判準:「自己接住例外、只回一個結果」與現有擋下訊息的資料形狀不相容,spec 沒定義。
spec 段落:範圍 3
問題:現有擋下訊息只讀 `verdict["lint_new"]["new"]` 這類欄位,把每條新增告警印成「檔:行 [規則] 訊息」,再附放行指令。覆核擋沒有對應欄位,也沒有說回傳的 dict 長什麼樣。
問題 2:`kg.hit` 一次只收一個停點。一般段與覆核段同時擋時,`--keep-going` 怎麼累積?
問題 3:JSON 輸出、`_cl_say_lint_ok`、`gov` 的小結都沒提。
問題 4:覆核範圍用 `_codeloop_disp_range`,一般段卻用推送範圍。把主線合進分支再推時,兩段會看到不同範圍。
引句:「`_codeloop_lint_new_step` 在一般段之後另跑一段覆核:呼叫範圍 2 那支拿命中」
file: `scripts/lumos:75561`、`scripts/lumos:75430`、`scripts/lumos:73997`

severity: major
blocking: 是
判準:統計(S8)所需的資料在帳裡根本沒有。
spec 段落:範圍 8,S8
問題:spec 說統計「全部從治理帳算」,包含「`real` 判定後被放行幾筆(人放、AI 放分開數)」。但 `cmd_lint_waive` 寫的 `waived` 事件只帶 `origin`、`scope` 與一句理由,沒有指紋、規則或檔案。放行檔(`.lumos/` 底下)才有規則與指紋,而且 `--rule` 是選填。
後果:被放行數無法對回規則,升擋建議永遠算不出來。
引句:「全部從治理帳算(判定事件、人複查事件、放行事件)」
file: `scripts/lumos:41232`

severity: major
blocking: 是
判準:守衛面的人複查沒有防偽造,跟 d4 的理由矛盾。
spec 段落:用詞「人複查」、範圍 6
問題:放行會問終端、區分 `human` / `ai`(`_waive_origin_tty`)。但 `rule-review` 沒寫要不要這一步,也沒記 origin。
後果:AI 可以對自己的判定逐筆 `agree`,把「待人看」清空、灌高人複查準確率。
後果 2:RETIRE-IF 與升降建議全靠「人複查過」的數字,這會讓數字失真。
問題 2:沒有列出待看清單的指令(指紋、token 從哪來),人無從下手。
引句:「寫一筆治理帳事件,不碰放行檔。」
file: `scripts/lumos:41156`

severity: major
blocking: 是
判準:漏列必須同步的註冊面,照做會讓守衛測試翻紅或指令查不到。
spec 段落:範圍 9
問題:範圍 9 只列手冊、範本與兩處說明,新增的子指令、旗標與事件種類漏了這些地方:
- `HELP_WHEN` 的 `code-loop rule-review` 說明列。
- argparse 的 `code-loop` 子指令表,以及 `cmd_code_loop` 的分派。
- `docs/指令參考.md` 與 `docs/command-reference.md` 兩份(雙語)。
- `skills/lumos-project-notes/commands/INDEX.md` 的指令索引。
- `LOOP_NOT_CLOSE_EVENTS`:新的複查事件種類沒登記,`t_loop_close_kinds_classified` 會紅。
- `_gate_failopen(repo_root, gate, why)` 沒有 `scope` 參數,spec 寫的 scope `rule-review` 沒辦法照現行簽名寫出。
- `lint_new` 的 fail-open 計數(doctor 的 `_lint_new_autopass_count`)只認 gate=`lint-new`,spec 把事件掛在 gate=`code-loop`,doctor 數不到。
file: `scripts/lumos:19935`、`scripts/lumos:72878`、`scripts/lumos:76170`、`scripts/lumos:77645`、`docs/指令參考.md:134`、`scripts/lumos:42740`

severity: major
blocking: 否
判準:新宣告檔「照 `_lint_deps_load` 讀、副檔名→命令清單」自相矛盾,且驗證條件不全。
spec 段落:用詞「覆核宣告」、範圍 1
問題:`_lint_deps_load` 讀的是 `{"cmds":[…]}`,不分副檔名。spec 的範例卻是 `{"kt":[…]}`,那是 `.lumos/lint.json` 的形狀。
問題 2:「另開檔」的理由寫成「lint.json 每個頂層鍵都被當副檔名驗」,但新檔本身就是副檔名形狀,理由不成立。真正的理由應是覆核命令要另判擋不擋。
問題 3:驗證只要求 `{LINT_FILES}` 或 `{LINT_FILES_CSV}`,沒要求 `{LINT_SARIF_OUT}`。型錄範本與 `_lint_new_tools` 都靠 SARIF 輸出解析。
問題 4:`_lint_new_declared` 只看 `lint.json` 與 `lint-deps.json`,只有覆核宣告的專案會被一般段判成 `no-config` 而早退,spec 只提了 `no-files`。
引句:「讀法照 `_lint_deps_load` 那套(另一支讀檔函式、另一份驗證)」
file: `scripts/lumos:41928`、`scripts/lumos:42587`、`scripts/lumos:39627`

severity: major
blocking: 否
判準:改共用載入的 `required` 會牽動現有情境題路徑與版本錯位。
spec 段落:範圍 4「讀型錄主表」
問題:`_load_hook_file` 沒有呼叫端自己傳 `required`,只有 `_kt_pack_check()` 寫死 `("dt_table",)`。把它擴成 `("dt_table","main_rows")`,會讓情境題整條路連帶要求 `main_rows`。
後果:消費專案的 lumos 搭配舊版 check.py 時,所有情境題都變成「讀不到」而被擋,等於覆核案拖垮既有功能。
問題 2:`main_rows()` 不帶 `text` 時讀 check.py 自己的 `CATALOG`,不理 `_kt_catalog_path()`(含測試用的 `LUMOS_KT_CATALOG` 覆寫),spec 沒說要傳文字進去。
問題 3:四欄在 12 欄列裡的位置是 `c[2]`、`c[3]`、`c[4]`、`c[7]`,spec 沒指明。
file: `scripts/lumos:38350`、`configs/ast-grep/kotlin-android/check.py:534`

severity: minor
blocking: 否
判準:新增檢查與既有檢查重複,引用的「原本只靠一次性核對」不實。
spec 段落:範圍 4 型錄自檢
問題:`catalog_problems` 已經用 `main_rows(text, problems)` 報「編號重複」,「主表編號只有一列」早有機檢。真正新增的只有「訊息開頭編號要存在於主表」。
引句:「覆核與提示規則訊息開頭的型錄編號要在主表存在、而且主表那個編號只有一列」
file: `configs/ast-grep/kotlin-android/check.py:340`

severity: minor
blocking: 否
判準:與既有政策不一致。
spec 段落:範圍 4「型錄讀不到時」
問題:既有情境題的先例是「型錄檔不在是環境不可用,只提醒不擋」(`_kt_catalog_missing`,2026-11-06 編排者裁定)。覆核案卻裁成「讀不到一律當不是出處不全、會擋」,而且材料四欄只寫「型錄讀不到」,盲判代理等於沒資料可判。這個分歧應該明講理由。
引句:「出處不全一律當「不是出處不全」(會擋,寧多擋不漏)」
file: `scripts/lumos:38371`

severity: minor
blocking: 否
判準:spec 沒寫到的邊界組合與雙重計算。
spec 段落:範圍 1、範圍 4
問題:同一條 `sgconfig-hints.yml` 命令若在 `lint.json` 與覆核宣告各有一份(舊範本曾建議自己加),兩段會對同一指紋各算一次,一般段會直接擋。spec 沒說怎麼去重。
問題 2:`--unsure` 沒配 `--rule-hits` 時的行為沒寫。
問題 3:`--rule-hits --disagreements` 沒意義(規則命中沒有作者表態),也沒寫怎麼拒絕。
問題 4:弱比對(工具沒附片段,指紋退成 `~msg~` 加訊息)沒提。
問題 5:誤報判定在處數沒變多的情況下,重新縮排整批造成的新指紋會被當新命中,這個代價只在實務隱患裡提了盲判成本。
file: `scripts/lumos:42244`

severity: minor
blocking: 否
判準:數字算錯,會誤導 REVISIT 的量測。
spec 段落:實務隱患「治理帳長大」
問題:「每筆理由最長 2000 字,一份 30 筆約 60KB」是以字元算。治理帳寫入用 `ensure_ascii=False`,中文每字約 3 位元組,最壞約 180KB。
引句:「每筆判定理由最長 2000 字,一份 30 筆約 60KB 進版控治理帳」
file: `scripts/lumos:74230`(`_codeloop_gov_append` 內的 `json.dumps`)

severity: minor
blocking: 否
判準:出處自相不一致。
spec 段落:PRIOR-ART 與〈依據來源〉第一列
問題:同一篇 Semgrep 文章,PRIOR-ART 寫 `semgrep.dev/blog/2025/...`,依據表寫 `ai.semgrep.dev/blog/2025/...`。我實際抓 `semgrep.dev` 那個網址可讀,內容與「九成底線、判誤報只隱藏不關」相符。`ai.semgrep.dev` 那個我沒驗過。
引句:「https://ai.semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories」

**固定席逐條判**
- 〈Systems/pitfalls-code-loop〉:會影響。覆核擋停與例外隔離掛在 `_codeloop_lint_new_step` 與推送前判定,上面前三條 major 都出在這裡。
- 〈Systems/kotlin規則包〉:不影響規則本身。型錄自檢多一條檢查可行,但「編號唯一」已存在;`required` 擴充有版本錯位風險。
- 〈Systems/linter精選目錄〉:範本加覆核宣告可行。但舊範本曾建議在 `lint.json` 自接 hints,升級會雙重計算。
- 〈Systems/lint-declaration-health〉:`--smoke` 與 doctor 要認新檔,spec 只簡述。
- 〈Systems/棧別提問表態閘〉:不影響其合約,前提是 `_kt_bj_event_ok` 與 `rule_hits` 欄互不干擾。純 `rule_hits` 事件會被 `_kt_bj_event_ok` 略過,讀到不會當掉。

**升級與回退**
- 回退:舊版不讀 `rule_hits`、`lint-review.json`,這點成立。
- 升級:消費專案的 lumos 與 check.py 版本錯位(`required` 問題),以及舊範本雙重計算,是實際會撞到的兩處。

**對 r1 的核對**
- 判誤報只留治理帳:改對了。
- 宣告另開檔:方向對,但「照 `_lint_deps_load`」的形狀寫錯。
- 擋停接線:寫了位置,沒寫接線需要的參數。

最後一行總結:方向正確,但有四個 blocking 缺口(合併側讀法、擋下資料形狀、放行統計無資料、人複查可被 AI 偽造),加上多處「沿用」宣稱與程式碼現況不符。接手的人照做會在擋停接線與註冊面卡住。
