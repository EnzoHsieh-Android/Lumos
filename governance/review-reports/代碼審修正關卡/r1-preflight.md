# 設計審前置掃描:代碼審修正關卡_計劃

被審:`.../negguard/docs/lumos-toolchain-knowledge/Projects/代碼審修正關卡_計劃.md`(對照 repo 提交 24f08d48)。
實驗在 `pf-fixgate-work/repo`(shared clone)與 `pf-fixgate-work/wtx`(臨時 git repo)做,repo 根與 /Users/enzo/harness/lumos-toolchain 沒寫過任何東西。
行號是 `scripts/lumos` 在 24f08d48 的大約位置。

---

## ① 未定義的詞:命中

沒脈絡的人接手會卡住的詞(計劃正文只用、不解釋):

1. **載體席 / 處置清單 / 折入清單 / 發現清單**:實際是「`canary record` 帶 `--findings-set` 的那一筆」「它的 `folded_set`」「它的 `findings_set`」(`_loop_records` 取、`cmd_loop_status` 驗「一輪只能一筆」)。計劃只在先決條件括號裡提一次「帶處置清單那一筆」。建議在〈做法〉開頭加一小段名詞表,逐字對到帳欄位。
2. **治理帳 / 帳本 / 帳上**:兩本不同的帳混用。審查帳=`docs/.canary-log.jsonl`(載體席、`regression_set` 住這裡),治理帳=`docs/.governance-log.jsonl`(`fix-check` 事件住這裡)。計劃「帳上找得到第 N 輪的載體席」是前者,「治理帳記一筆」是後者,沒說清楚。
3. **凍結材料**(`rN-snapshot.patch`)、**編排者**(`--orchestrator`)、**辯方**:全是 lumos-code-loop 手冊的詞,沒給連結。
4. **平台、`run_cmd`、平台根目錄、測試索引**:指 `.lumos/config.json` 的 `platforms.<名>.run_cmd` / `.root`,與 `_platform_test_index` 的 `methods_for(plat)`。這個 repo 是單平台、根=repo 根,實作者容易漏掉多平台時根是子目錄。
5. **受波及合約測試**:計劃只說「用推送前那套」。實際=`impact --diff` 的固定席(pinned 且 contract 的節點)裡 ★INVARIANT★ 綁的 `[test:]`(`_bound_tests_for_diff`)。要寫一句。
6. **殺傷力配方 / 配方短身分**:指節點裡的 `[kill:]` 壞法配方,與 `guard kill` 輸出的 `id=` 欄(`_kill_recipe_id`)。
7. **壓力指令**:第 2 步整個機制,但正文沒說它想擋什麼。使用者全域規則的「大型/深層巢狀輸入跑效能與記憶體」才是脈絡,計劃裡一個例子都沒有(建議給 `fix_check.stress` 範例,例如餵 N 層巢狀輸入的指令)。
8. **決策備忘錄**:只在〈依據〉裡出現「到頂時產底稿」。正文要說這是 `loop next` 到 `cap-reached` 時給人裁決用的底稿。
9. **`fixed` / `unaffected`**(JSON 的 status 值)、**收集失敗**(pytest 用語):前者只在範例 JSON 裡出現,後者在本 repo 自家 runner 上根本不存在(見④-4),要定義。
10. **處置閘、首筆帳、panel 閘退場**:〈上線〉用到,沒指向 `loop status --disposal` / `_panel_retired_for`。

---

## ② 壞引用

### 命中

- **[S5] 行內寫了 `[test:X]`**(原句:「改到一篇帶 ★INVARIANT★ 與 `[test:X]` 的節點牽連的檔、而 X 在現在的提交是紅的」)。證據:`docs/.canary-log.jsonl` 裡本計劃的 spec-gate 紀錄 `tests` 欄是 `["X", "t_canary_regression_set", ...]`,第一個就是 `X`。條款解析把那段散文當成一條測試綁定,`X` 會被當成找不到的測試(懸空)。建議:改成「帶 ★INVARIANT★ 與測試綁定的節點」,不要在條款裡出現 `[test:` 字樣。
- **S6 依賴的嚴重度欄沒指名**:「載體席沒記個別嚴重度就當 major 算」。對應的是已存在的 `--finding-severity`(`cmd_canary` 的 `finding_severities`),計劃沒點名,實作者會以為要新增。建議寫明沿用它。
- **`lumos canary record` 的實作函式是 `cmd_canary`**(8422,簽名要加 `regression_set`),不是 `cmd_canary_record`;解析器在 41037 起、呼叫點在 42121、「這幾個旗標要跟 `--findings-set` 一起給」的守衛在 8567(要把 `regression_set` 加進那串)。計劃沒說掛哪,建議在〈做法〉點出這三處。

### 新東西(不算壞引用,單列)

指令 `lumos loop fix-check`、`lumos loop memo`;旗標 `--regression-set`、`--record`;環境變數 `LUMOS_SKIP_FIX_CHECK`;設定鍵 `fix_check.stress` / `fix_check.stress_none_reason`;閘名 `fix-check`;檔案 `rN-fix.json`;治理帳欄位與 kind 名;測試 14 支(`t_fix_check_*`、`t_loop_next_fix_check_reminder`、`t_canary_regression_set`、`t_loop_memo_skeleton`、`t_doctor_fix_check_stress_reminder`、`t_gov_stats_fix_check`),全部 grep 過不存在、沒撞名。(設定檔沒有「未知鍵」白名單,`fix_check` 可直接加。)

### 找得到(未命中)

`_nodehome_is_test`(24776)、`_gate_event_or_warn`(1234)、`_KNOWN_GATES`(7258)、`_run_bound_tests`(38606)、`_bound_tests_for_diff`(38385)、`_ran_evidence_check`(38524)、`_RAN_EVIDENCE`(38467)、`_panel_retired_for`(9105)、`_kill_run`(13976)、`cmd_guard_kill`(14105)、`cmd_loop_next`(11531)、頂層 `fold-check`(解析器 41465、`cmd_fold_check` 35179)、`gov --stats`(41013)、`[[Projects/漂移防治路線圖_計劃]]`、`[[Systems/pitfalls-code-loop]]`、`[[Systems/loop-convergence-recording]]`、`[[Systems/guard-kill]]`(皆有檔)、`skills/lumos-code-loop/SKILL.md` 第 5 步「修與釘」、`skills/lumos-project-notes/commands/06-代碼審與推送.md`、`governance/review-reports/<編號>/`(含 `code-` 前綴那批,153 個目錄,`<編號>`=迴圈編號無歧義;同目錄已有 `r1-dispatch.json` 進版控,`.json` 沒被 gitignore)、路線圖「1a-4 已上線 / 修正關卡排第 2」(路線圖第 39、40 行)、`LUMOS_SKIP_*=1` 的先例(只認 1)。「至少四個字、要有實字」可沿用 `_MANUAL_MIN_CHARS` 那套(8285 附近)。

---

## ③ 範圍自相矛盾

**命中**

1. **`loop next` 提醒只寫「要派第 N+1 輪」,沒列是哪幾個 phase**。`emit()` 有 plant-canary / gate-pending / converged / cap-reached / escalate 五態。最危險的那條路是「最後一輪折入修補、但迴圈到頂(cap-reached)或結案、沒有第 N+1 輪」:那批修補沒人再審,正是計劃的動機。照字面「要派第 N+1 輪」這條路不印提醒。建議:明寫 cap-reached、plant-canary、gate-pending 都印,converged/escalate 要不要印也要裁。
2. **S7「每次跑完寫恰好一筆」與先決條件「回 2、不記通過」**:回 2(base 不存在、工作目錄髒)是「跑完」嗎?要寫不寫沒說,S2 只說「不記通過」。建議寫明:回 2 不寫事件(或寫 kind=`refused`),並讓 S7 對齊。
3. **治理帳事件的 kind 名沒定**:通過/不過各叫什麼?`loop next` 要找「通過紀錄」、S7、S14 都靠 kind。計劃只出現 `skipped-env`。建議定 `passed` / `failed` / `skipped-env`。
4. **REVISIT 與 RETIRE-IF 的核心指標靠選填欄**:「上一輪修補造成的比例」只有編排者帶了 `--regression-set` 才有數字,未帶印 `?`,而第 1 步只提醒不擋、也沒有任何機制催編排者帶。兩週後基準可能量不到,RETIRE-IF 第一條就判不了。建議:要嘛第 1 步的 `fix-check` 通過時順手檢查載體席有沒有 `regression_set` 欄並提醒,要嘛 RETIRE-IF 寫「沒量到就視為沒過基準」。
5. **S2「沒提交的程式檔」在本 repo 平常就成立**:`git status` 現在就有未追蹤的 `governance/eval/maestro-matchpct.py`(別的會談的檔)。`_NODEHOME_EXCLUDE_GLOBS` 只排除 `docs/*` 與建置目錄,不排除 `governance/`。照〈做法〉判,同一 repo 有並行會談時 `fix-check` 常態回 2。建議改成只看 tracked 的改動 + 本次紀錄指到的路徑/測試檔的未追蹤狀態,或限定在平台根底下。
6. **〈實務隱患〉「程式跟測試同一支檔的棧 → 判不過」沒有偵測辦法也沒有條款**:怎麼知道這個棧是同檔?沒寫,也沒綁測試。要嘛在〈做法〉第 4 項加一句判法(例如 `_nodehome_is_test` 判到某個改動檔「同時是程式又是測試」),要嘛明講「這版不處理,留 REVISIT」。
7. **紅燈逾時**:`_kill_run` 逾時回 `(None, tail, secs, True)`。「先紅」那步的三種結果(紅/收集失敗算紅/通過)沒涵蓋逾時;綠那步也沒涵蓋。建議逾時一律不過並說明。

未命中:〈範圍〉說「驗四件事 + 同類連兩輪」對得上〈做法〉第 1~5 項;第 1/2 步的分配跟條款 S1~S9 / S10~S14 一致;〈回退〉「各自 revert」與「兩步都不擋」不衝突;〈不做〉的「不改處置閘」與〈上線〉轉成擋是「另開小改動」,沒打架。

---

## ④ 機械宣稱驗語意

### 1. 「測試檔判法沿用 `_nodehome_is_test`」

- 實際(24776):只看路徑。`scripts/test_lumos.py`=True、`tests/foo.json`=True、`scripts/lumos`=False。**預設 layout 不認各棧測試資料夾**:`src/androidTest/kotlin/A.kt` 預設回 False,`PosTerminalTests/FooTests.swift` 用 `_nodehome_layout(all_paths)` 才可靠(我實測:給 `_nodehome_layout(git ls-files)` 才對)。
- **成立**(但要寫「layout 用 `_nodehome_layout(所有受版控路徑)` 算出來傳進去」)。

### 2. 「程式檔判法沿用每支檔有家那套」

- 實際:**沒有一支函式判「工作目錄有沒有還沒提交的程式檔改動」**。可拼的零件=`_nodehome_code_kind`(24797,副檔名在 `_NODEHOME_CODE_EXTS` 回 `'ext'`;沒副檔名回 `'shebang?'`,要自己讀首行判 `#!`,例如 `scripts/lumos`、`scripts/hooks/pre-push`)+ `_drift_m1_code_kind(p, first_line)`(31030,已包好首行判)+ `_NODEHOME_EXCLUDE_GLOBS`(只排 `docs/*` 與建置目錄)+ 設定 `node_home.ignore`。「每支檔有家」那套本身是 `_nodehome_changes(base, tip)`(提交對提交),不吃工作目錄。
- **部分成立**。
- 修改前→後:「程式檔判法沿用每支檔有家那套」→「用 `git status --porcelain -z`(含未追蹤)取路徑,再以 `_drift_m1_code_kind`(含 shebang 首行)或 `_nodehome_is_test` 判是不是程式/測試檔;排除範圍照 `_NODEHOME_EXCLUDE_GLOBS` 並另加 `governance/`(見 ③-5)」。

### 3. 「開一個隔離工作樹(沿用 guard kill 的建法與收法)…切到 `base`…再切到現在的提交」

- 實際:建法/收法**內嵌在 `cmd_guard_kill` 裡**(14206~14325),不是可呼叫的函式:`tempfile.mkdtemp("lumos-kill-")` → `git -C <平台根> worktree add --detach <wt> <ghead>` → finally 裡 `worktree remove --force` + `rmtree` + `prune`。`worktree add` 本來就收一個 rev 參數,指定 `base` 沒問題。但「沿用」=要抽成共用函式(動到 guard kill,它自己有測試與代碼審歷史)或複製一份。
- **「切到現在的提交再跑一次」不成立**:我在臨時 repo 實測——在 base 的工作樹把測試檔疊成 HEAD 的內容後,`git checkout --detach <HEAD>` 直接失敗:`Please commit your changes or stash them before you switch branches. Aborting`(疊過的檔被視為本地改動,跟目標版本不同就擋;被刪的檔也留下 ` D`)。
- 修改前→後:「把工作樹切到現在的提交再跑一次」→「綠那步另開第二個工作樹直接檢出現在的提交(最乾淨);或用 `git checkout -f --detach <HEAD>` 後 `git clean -fd`,並重用 `_kill_wait_new_second` 錯開寫檔時間(同一秒寫同大小的檔,Python 編譯快取會誤用舊版;1a-4 剛修過)」。
- 另外:guard kill 對髒樹只印警告、以 HEAD 建沙盒;fix-check 先決條件已擋髒樹,沒衝突。
- **部分成立**(建法可指定版本;切換說法錯)。

### 4. 「用平台的 `run_cmd` 帶 `{method}`、在平台根目錄跑」

- 實際:`_run_bound_tests`(38606)用 `pentry["root"] or repo_root` 當 cwd,在**主工作目錄**跑;`cmd_guard_kill` 用 `_kill_run(cmd, wt, …)`,cwd=**工作樹的 repo 最上層**,不是平台根。兩者只在「平台根=repo 根」(本 repo)時一致;多平台且平台根是子目錄(如 ios/)時,guard kill 的作法會在 repo 頂跑,跟 `_run_bound_tests` 不同。
- 計劃選的是 `_run_bound_tests` 那邊(平台根)。但先紅後綠在隔離工作樹跑,所以要自己算 `<工作樹>/<平台根相對 repo 頂的路徑>`(`_kill_plat_top` 可取 repo 頂)。
- 還有:`_run_bound_tests` 吃的是 `(node, plat, method, status)` 與主工作目錄,**不能直接拿來跑隔離工作樹**,要自己寫迴圈:`_run_cmd_expand(run_cmd, method)` + `_kill_run(cmd, root, timeout, keep_re=_ran_evidence_re(profile))`;逾時 `per_test=LUMOS_TEST_TIMEOUT 預設 180`、整套 `_BOUND_TESTS_WHOLE_SUITE_TIMEOUT`。
- **部分成立**。

### 5. ★動到核心★「輸出看得出真的跑了」用 `_ran_evidence_check` 分辨「真的跑了而失敗」跟「收集就失敗」

- 原句:「失敗而且輸出看得出真的跑了 → 紅,過;失敗但輸出看不出跑了任何一支…→ 算紅,但在輸出標『收集失敗算紅』」。
- 實際(38524,樣式 38467):`_ran_evidence_check` 看的是**通過的證據**(python=`[1-9]\d*\s+passed`、swift=`Executed N tests`、csharp=`Passed:\s*[1-9]`、jest=`Tests:.*N passed`)。它對「失敗的測試輸出」多半答 False。
- 我實測(在 clone 的 test_lumos.py 末尾加了三支假測試,真跑 `python3 scripts/test_lumos.py -k …`,再把輸出餵 `_ran_evidence_check("python", out)` 與 `_ran_count`):

| 情境 | 真實輸出重點 | `_ran_evidence_check` | `_ran_count` |
|---|---|---|---|
| 第一個斷言就失敗 | `0 passed, 1 failed` | **False** | (1, …) |
| 先過一條再失敗 | `1 passed, 1 failed` | True | (1, …) |
| 函式不存在(NameError,EXCEPTION) | `✗ t_zz_exc EXCEPTION: … 0 passed, 1 failed` | **False** | (1, …) |
| `-k` 選中 0 支(名字不存在) | `✗ -k 't_zz_nosuch' 選中 0 個測試…` rc=1 | False | (None, …) |
| pytest `1 failed in 0.01s` | | **False** | (1, …) |
| swift 失敗 `Executed 1 test, with 1 failure` | | True | None |
| csharp `Failed: 1, Passed: 0` | | **False** | None |
| jest `Tests: 1 failed, 1 total` | | **False** | None |

- 結論:**不成立**。對本 repo 最典型的紅(整支測試的第一個斷言就失敗、或要測的函式修之前不存在而拋 NameError)`_ran_evidence_check` 都答「看不出跑了」,於是真的跑了的紅會被全部貼上「收集失敗算紅」的標籤——標籤失去意義;而本 repo 自家 runner 根本沒有「收集」階段,真正的「沒跑」只有 `-k` 選中 0 支那一種。
- 判紅綠本身(rc≠0 算紅)不受影響,所以不是「根本做不到」;但計劃明講的「讓人看得到、由人判斷是不是假紅」做不到(§實務隱患「把測試檔疊回修正前」那段整段靠它)。
- 另一個坑:`_kill_attribute(out, "t_zz_nosuch")`(guard kill 用來把紅歸因到測試名)對「選中 0 支」那行也回 True(同行有 ✗ 與名字),不能拿它判「真的跑了」。
- 修改前→後:「輸出看得出真的跑了」→「紅那一步改用 `_ran_count(profile, out)`:回 `N≥1` 才算『真的跑了而失敗』(本 repo python 實測三種失敗輸出皆 N=1,`-k` 選中 0 支回 None);`_ran_count` 回 None 的 profile(swift/csharp/jest/其他)標『無法確認真的跑了』並照樣算紅。『收集失敗算紅』改名成『看不出跑了幾支』。綠那一步繼續用 `_ran_evidence_check`(通過輸出它答得對)」。
- 綠那一步再補一點:`_ran_evidence_check` 對沒實測過的 profile 回 `(None, "")`(只有 python/swift-xctest/csharp-xunit/node-jest 四種有樣式)。推送閘遇到這種 profile 是退回 `_bound_tests_filter_probe`(38832 那段)。計劃寫「每支都要通過而且輸出看得出真的跑了」,對 kotlin/java/go/dart…沒有出路,要寫「沒樣式的 profile 照推送閘退回過濾探針」。
- 附帶副作用:本 repo runner 每次有紅都在 `$TMPDIR` 留下 `gctl-run-*` 暫存現場(輸出最後一行「暫存現場留著沒刪」),先紅那步每支測試都會留一份;要設 `--keep-tmp` 反向開關或跑完清掉。

### 6. 「受波及合約測試的算法」能不能吃任意兩個提交 `base..HEAD`

- 實際:`_bound_tests_for_diff(repo_root, diff_range)` → `cmd_impact_diff` → `git diff --name-only <範圍>`(兩點式,端點比對)。不要求 base 是 HEAD 祖先;`_bound_tests_range` 的特例只處理空樹起點。節點讀的是主工作目錄的 vault(S2 已擋髒樹,等於讀現在的提交)。
- **成立**。要補兩點:(a)回傳 `(items, reason)`,`reason` 可為 `no-vault`/`no-pins`/`no-bound`/`diff-unavailable`/`no-config:…`,計劃沒說各自算過還是不過(建議 `no-pins`/`no-bound` 算過並印說明;`diff-unavailable`/`no-config` 算不過);(b)`_run_bound_tests` 的 verdict 除了 green/red,還有 `unproven`(回成功但看不出跑過)與 `no-cmd`,計劃只寫「紅、懸空、只在文字裡出現」,要把 `unproven`、`no-cmd` 也寫成不過。

### 7. 「測試名用合約綁定那套解析…在現在的提交的測試索引裡找得到;只在原始碼文字裡出現…都算不過」

- 實際:`resolve_test_refs(inv_text, split, default)`(4896)吃的是含 `[test:…]` 的**整行文字**,不是裸測試名——實作時要包成 `f"[test:{name}]"`;`methods_for(plat)`=real、`hay_for(plat)`=fake(只在文字出現)、其餘 dangling,見 `_classify_one`(11960 附近)。`methods_for` 掃的是**工作目錄**,不是 git 提交;S2 擋了髒樹所以等價。
- **成立**(同上補一句包法)。

### 8. `_gate_event_or_warn` 與 `_KNOWN_GATES`;治理帳事件能不能帶那些欄位

- 實際:簽名 `(repo_root, gate, kind, note, **kw)`,kw 可帶 `hard/head_sha/ref/nodes/extra`;`extra` 是 dict 直接併進事件(`_gate_event_build`),欄位自由。閘名不在 `_KNOWN_GATES` 就不寫並印警告(要同步清單與 `t_gov_stats_gate_drift`、2623 行那條對文件的測試)。沒有 `docs/` 回 None。`commit` 取 `head_sha[:7]`。
- **成立**,但有三個計劃沒提的連帶:
  - **讀側去重會吃掉事件**(`cmd_gov`,約 7640~7700):去重鍵=`(commit, nodes, gate, kind, token, check)`,而 `.governance-log.jsonl` 的 mapper 只轉出固定欄位。同一個 commit 上同一迴圈連跑兩次同結果的 `fix-check`(修一點、再跑一次還是不過是常態)會被折成一筆,**S14 的通過/不過次數與耗時中位數會少算**。canary blocked 事件已有先例(`token`=`ts+note` 含隨機碼)。建議:`fix-check` 事件在 mapper 補 `token`(用 `written_at` 或事件隨機碼),並讓 mapper 轉出 `loop`、`round`、`secs`、`failed_items`、`regression_set`、`finding` 等 S14 要的欄位。
  - **`_GOV_FIELD_TYPES`**(7578)明寫「新增 mapper 用到的欄位時一起補進來」,否則型別怪的行會把 `gov` 弄當掉。`regression_set`(list)、`secs`、`tests` 等要補。
  - **`loop next` 要「找同迴圈同輪同 sha256 的通過紀錄」沒有現成讀函式**。最接近的是 `_codeloop_read_from_ledger`(38222,只認 code-loop、以 branch 當鍵)與 `cmd_loop_rewrite` 內嵌的逐行掃描。要新寫一支(沿用 `_drift_jsonl_parse` 容錯讀;先用字串 `'"fix-check"' in line` 預篩——治理帳現在 16MB、每次 `loop next` 都掃,用整行 json 解析會慢)。路徑=`env.vault.parent/".governance-log.jsonl"`。
  - 好消息:閘名用獨立的 `fix-check`,不會撞 `t_loop_close_kinds_classified`(它只管 design-loop/code-loop 兩個閘)。

### 9. `canary record` 的 `--findings-set`/載體席判法;`--regression-set` 掛哪

- 實際:載體席=「這一筆帶了 `--findings-set`」(`f_set is not None`);`--finding-kind`/`--folded-set` 等沒有 `--findings-set` 就回 2(8567)。`--finding-severity`、`--finding-kind` 都是 `id=值`、可重複的 `append`;`--refuted-set` 是 `id=理由` 逗號串或 `none`。`--regression-set <id 串|none>` 照 `--folded-set` 的 `_ids()` 解析最順;「非載體席帶了回 2」只要把它加進 8567 那串即可。
- **成立**。連帶:`_GOV_FIELD_TYPES` 加 `regression_set`;canary 的 gov mapper 補轉這欄,S14 才讀得到。

### 10. `loop next` 的輸出與 `--json`;「狀態與回傳碼不變」

- 實際:`emit(phase, extra)` 組 `out` 字典,`--json` 整個印出,所以多一個欄位很容易;**文字模式只逐鍵印** `("canary_type","record_cmd","scope_cap","cluster_hint","note")` 與專屬段落,新欄位要自己加一段文字輸出(像 `_cap_hint_lines` 那樣)。phase 與 rc 在 `emit` 之前就定了,提醒只是附加欄位,**「狀態與回傳碼不變」做得到**。
- **成立**(但見 ③-1 的 phase 範圍問題;另 `round` 是自由字串,`rN-fix.json` 與「第 N 輪」要從 `"r2"` 解析數字,非 `rN` 格式的輪 id 要說明怎麼辦)。

### 11. 〈上線〉「照 panel 閘退場那套切點」

- 實際:`_panel_retired_for(rounds)`(9105):迴圈**首筆記錄**的 `ts` 日期 ≥ 預設常數 `"2026-08-26"` 就算新迴圈;環境變數 `LUMOS_PANEL_RETIRE_CUTOFF` 可覆寫;ts 不像日期就視為舊帳(fail-open)。
- **成立**(語意與計劃的「只對首筆帳晚於切換日的迴圈生效」一致),但是**樣式不是可重用的函式**:要另寫一支(常數 + 環境變數 + 同樣的日期正則防呆),別直接呼叫它。

### 12. 〈第 2 步〉「殺傷力重跑:照 guard kill 重跑那幾條(只跑那幾條)」

- 實際:`cmd_guard_kill(env, node, invariant_substr, platform_override, as_json, keep_worktree)` 一次只跑**一個節點**,過濾只有 `invariant_substr`(合約文字子字串,不唯一),**沒有按配方 id 或檔案過濾的參數**;每次跑**一定寫** `docs/.kill-log.jsonl`(會弄髒帳、進 `gov`);`--json` 輸出前把 `_rid`(短身分)濾掉,只留長的 `recipe_id`——計劃要的「配方短身分」要另呼叫 `_kill_recipe_id(rel, elem)`;只在「平台根 HEAD」建沙盒,不指定版本。verdict 有七態:`killed / killed_unattributed / timed_out_weak / survived / drifted / abort / error`。
- **部分成立**。修改前→後:「判 survived、error、配方失配的都算不過;killed 算過」→「`survived`、`drifted`(=配方失配)、`error`、`abort`(baseline 就紅)算不過;`killed` 過;`killed_unattributed`、`timed_out_weak` 是弱證據,照印、不算不過(要明寫)」,並指明:需在 `cmd_guard_kill` 加 `only_recipe_ids` 之類的參數(或另寫迴圈呼叫內部函式),要把「base..HEAD 改到的檔 ∩ 各節點配方的 `file`」的反查寫出來(要掃 `env.notes` 每篇的 `_kill_read_recipes`),並注意它會寫 kill-log。時間也要進〈實務隱患〉(每個測試指令一次 baseline,上限 600 秒,加每條配方一次)。

### 13. 「受影響測試」:`fix-check` 在主工作目錄真跑受波及合約測試 vs 在隔離工作樹跑先紅後綠

- 實際:兩處跑的環境不同(主目錄 vs 工作樹),靠 S2 擋髒樹保持等價;`_run_bound_tests` 會在主目錄寫 `.lumos/test-cache*.json`(已 gitignore)。**成立**,不需修,但建議在計劃寫一句「第 5 項跑在主工作目錄、其餘在工作樹,所以必須先通過先決條件三」。

### 14. 〈實務隱患〉「59 支受波及合約測試約 4 分鐘」

- 一次推送的實測數字,標出來,**未重跑**。

---

## 結論(必修)

1. ★動到核心★ **先紅那步的判準不能靠 `_ran_evidence_check`**(④-5):它只認通過輸出,對失敗輸出(本 repo 最典型的兩種紅)都答「看不出跑了」。改用 `_ran_count`(python 才讀得出;其他 profile 標「無法確認」仍算紅),並把「收集失敗算紅」改名、改定義,否則標籤全錯、〈實務隱患〉靠它讓人判斷假紅的設計落空。沒樣式的 profile(只有 4 種有)綠那步要寫退回過濾探針。
2. **「切到現在的提交再跑一次」做不到**(④-3,實測 `git checkout` 被擋):改成第二個工作樹或 `checkout -f` + clean,並說明建法/收法要從 `cmd_guard_kill` 抽出共用函式(或複製)、cwd 要算平台根相對路徑(④-4)。
3. **S5 內的 `[test:X]` 會被條款解析成一條懸空測試**(②,spec-gate 紀錄已看到 `X`):改寫該句。
4. **治理帳事件的讀側去重與 mapper**(④-8):補 `token`、補轉出欄位、補 `_GOV_FIELD_TYPES`、定 kind 名(`passed`/`failed`/`skipped-env`)、寫 `loop next` 讀治理帳的新函式(字串預篩,帳現 16MB),不然 S14 的次數與 S8 的「找通過紀錄」會算錯或很慢。
5. **`loop next` 提醒要列明 phase**(③-1):cap-reached 與結案前的最後一輪折入正是動機所在,照「要派第 N+1 輪」字面不會印。
6. **S2 的「沒提交的程式檔」判法**(③-5、④-2):沒有現成函式,且在本 repo 並行會談下常態回 2;要定義取檔方式與排除範圍(含 `governance/`、未追蹤檔)。
7. **殺傷力重跑要補的介面**(④-12):`cmd_guard_kill` 沒有按配方過濾的參數、會寫 kill-log、`--json` 不含短身分;七態 verdict 裡 `abort` / 弱證據的處理要明寫;時間進〈實務隱患〉。
8. **回 2 要不要記事件**(③-2)、**逾時算什麼**(③-7)、**`_bound_tests_for_diff` 的 reason 與 `unproven`/`no-cmd` 算什麼**(④-6)三處補一句話。
9. **RETIRE-IF/REVISIT 的基準靠選填的 `--regression-set`**(③-4):補提醒機制或改寫撤除條件,否則兩週後量不到。
10. 補〈做法〉開頭名詞表(①):載體席/處置清單/折入清單對到帳欄位、兩本帳的區別、壓力指令的用途與範例、受波及合約測試、配方短身分。
