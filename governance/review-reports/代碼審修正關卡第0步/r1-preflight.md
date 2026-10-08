# 前置掃描:代碼審修正關卡第0步_計劃

被審:`Projects/代碼審修正關卡第0步_計劃.md`(negguard 工作樹那份)。行號都指該工作樹的 `scripts/lumos`(單檔)。
實驗在 `pf-fix0-work/repo`(`git clone --shared`),沒有動 repo 根與 /Users/enzo/harness/lumos-toolchain。

白話先說:計劃大方向站得住,既有零件大多存在、語意大致照它說的那樣。但有三處「照它的寫法就行」其實不行或不夠(`_lint_copy_configs`、規格閘兩處抽成一支的介面、`loop next` 的「記帳範本」),兩處行為洞(`LUMOS_SKIP_FIX_CHECK` 跳過後提醒還會一直響;`_bound_tests_check` 回 green 時可能有平台根本沒跑)。

## 一、四類掃描總表

| 類別 | 結果 |
|---|---|
| ① 未定義的詞 | 命中 3 條(下面) |
| ② 壞引用 | 命中 1 條實質(`_lint_copy_configs` 的用途),其餘函式/常數/指令/節點都在;新開節點與新測試名單列 |
| ③ 範圍自相矛盾 | 命中 5 條 |
| ④ 機械宣稱驗語意 | 成立 12 條、部分成立 9 條、不成立 2 條 |

## 二、① 未定義的詞

命中(只列會讓接手實作的人卡住的):

1. **「每條 `unaffected` 有理由(判法同 `[manual:]`)」**:`[manual:]` 的判法只有 `_MANUAL_MIN_CHARS = 4`(內容 <4 字視同未標,`MANUAL_REF_RE` 附近,約 L4471);沒有一支叫「判理由夠不夠」的函式可呼叫。`--refuted-set` 另有一套 `len(v) >= _MANUAL_MIN_CHARS 且 re.search(r"[^\W_]", v)`(L8613 一帶)。接手的人不知道該抄哪一套。建議:計劃直接寫「去前後空白後 ≥4 字、至少含一個非標點非底線字元(同 `--refuted-set` 的理由判法)」。
2. **「判程式檔用 `_nodehome_code_kind`」**:它回 `'ext'` / `'shebang?'` / `None`(L24797)。`'shebang?'`=沒副檔名、要看首行才知道是不是程式檔。本 repo 主程式 `scripts/lumos` 本身就沒副檔名,改名它會回 `'shebang?'`。計劃沒說 `'shebang?'` 算不算。建議:寫「回傳值不是 `None` 就算程式檔(沒副檔名的寧多判)」。
3. **「平台根」在樹裡長什麼樣沒定義**:`load_platforms` 允許 `root` 寫成 `../Compass_KDS` 這種 repo 外的路徑(`Projects/多平台合約測試綁定_計劃.md` L49 的範例;`guard kill` 也是對每個平台根各自 `git -C <平台根>`,所以平台可能是別的 git repo)。在樹(系統暫存資料夾)裡 `(樹 / "../Compass_KDS").resolve()` 會落到不存在的地方,測試跑不起來或根本沒跑到樹。計劃的「repo 頂與每個平台根各用 `_lint_link_deps`」隱含假設平台根都在 repo 內,沒寫。見 ④-I。

未命中:「載體席」「修正後」「樹」「發現清單」「折入清單」「派工單」「一支測試的判法」計劃〈名詞〉都定義了。

## 三、② 壞引用

逐一 grep 結果(函式 `def` 都在 scripts/lumos):

- 存在:`_codeloop_record_valid_ex`(L39233)、`_lint_new_clean_stale`(L23798)、`_LINT_NEW_STALE_SEC`(L23365,=86400)、`_lint_link_deps`(L23630)、`_lint_copy_configs`(L23607)、`cmd_guard_kill`(L14105)、`_spec_gate_run_clauses`(L6625)、`_spec_gate_regress`(L6647)、`_spec_gate_verdict`(L6584)、`_spec_gate_declared`(L6564)、`_ran_count`(L38498)、`_run_bound_tests`(L38606)、`_bound_tests_check`(L38725)、`_platform_test_index`(L11905)、`resolve_test_refs`(L4896)、`_gate_event_or_warn`(L1234)、`_KNOWN_GATES`(L7258)、`_GOV_FIELD_TYPES`(L7577)、`cmd_gov`(L7603)、`cmd_canary`(L8422)、`_drift_jsonl_parse`(L29834)、`_nodehome_code_kind`(L24797)、`_roster_dispatch_entries`(L11144)、`cmd_seat_check`(L21339)、`_kill_run`(L13976)、`cmd_loop_next`(L11531)。
- 指令:`lumos loop status`/`next` 在、`--repo` 在;`--dispositions-template` 是 `lumos pitfalls --diff` 的旗標(L41525),計劃「命名照它」成立;頂層 `fold-check` 在(L41465),`loop fix-check` 沒有撞名。
- 節點:`Projects/代碼審修正關卡_計劃`、`Projects/漂移防治路線圖_計劃`、`Systems/pitfalls-code-loop`、`Systems/bound-tests-gate`、`Systems/規格閘`、`Systems/guard-kill`、`Systems/loop-convergence-recording`、`Systems/finding-refute`、`Systems/診斷迴圈先行` 都在。
- 單列(要新開,不算壞引用):`[[Systems/代碼審修正關卡]]`。
- 單列(新測試名,不算壞引用):`t_fix_check_record_complete`、`t_fix_check_bad_input`、`t_fix_check_test_must_exist`、`t_fix_check_listed_tests_green`、`t_fix_check_bound_tests_green`、`t_fix_check_repeat_category_needs_why`、`t_fix_check_gov_event`、`t_loop_next_fix_check_reminder`、`t_canary_regression_set`、`t_fix_check_record_template`、`t_isolated_worktree_shared`、`t_fix_check_tree_setup`(都還不存在,符合預期)。

實質命中 1 條(壞引用性質):**PRIOR-ART 寫「設定檔取現在版(`_lint_copy_configs`)」**——函式存在,但它做的事跟計劃要的不一樣,見 ④-D。

## 四、③ 範圍自相矛盾

1. **`LUMOS_SKIP_FIX_CHECK=1` 跳過後,`loop next` 會一直提醒**。〈做法〉說跳過記一筆 kind `skipped-env`;〈`loop next` 的提醒〉要求治理帳有 kind **`passed`** 的事件才不提醒;S8 同。兩邊合起來:使用者明確跳過後,下一輪、再下一輪的 `loop next` 仍然印提醒,跳過等於沒用。RETIRE-IF 還把「跳過比例超過三成」當撤除條件,表示計劃預期有人會跳。建議:提醒的比對改成「有符合 loop+round、head_sha 仍有效(`_codeloop_record_valid_ex`)的 `passed` **或 `skipped-env`** 事件就不提醒,跳過的印一行『這輪修正關卡已跳過』」;S8 補一句。
2. **S8 的狀態清單比〈做法〉窄**:〈做法〉寫「不管這次判到哪個狀態都印」,S8 只列 `plant-canary`、`converged`、`cap-reached`;`loop next` 實際有五個 phase(escalate / gate-pending / converged / cap-reached / plant-canary,全部走同一個 `emit`,L11585 起)。建議 S8 寫「五個狀態都印」,或刪掉清單。
3. **S8「第 2 輪起的記帳範本應含 `--regression-set`」對不到文字輸出**:載體席範本是 `out["disposal_cmd"]`(L11663,帶 `--findings-set`),只存在於 `--json`;文字模式 `for k in ("canary_type","record_cmd","scope_cap","cluster_hint","note")`(L11790)只印 `record_cmd`,而 `record_cmd` 沒有 `--findings-set`、不是載體席範本。所以計劃寫的「`loop next` 給的載體席記帳範本」只改得到 JSON。要嘛明寫「只改 `disposal_cmd`,即 `--json` 才看得到」,要嘛文字模式也印 `disposal_cmd`。另外 `t_loop_next_disposal_cmd_actually_runs`(test_lumos.py L23974)會把範本填值後真跑;第 2 輪起多一個 `<id串|none>` 佔位,測試要同步換值,計劃的〈實務隱患〉「既有測試」只提了 `loop next` 輸出字面,沒提這支。
4. **做事順序沒寫,會白建樹**:〈一開始〉先清殘骸、建樹,〈先決條件〉(迴圈 `code-` 開頭、紀錄讀得到、`base` 轉得成、折入是 0 條就回 0)排在後面。S2「回 2、不寫事件」「折入 0 條回 0」都不需要樹。若照文字順序實作,每次失敗都先付約 2 秒建樹 + 磁碟。建議:寫明順序「便宜的先決條件 → 清殘骸 → 建樹 → 樹裡的先決條件(`worktree add` 失敗回 2)」。`--record-template` 也不需要樹。
5. **item 3 失敗的測試還要不要進 item 4**:「能驗的都驗完再一起印」,但 item 4 是「紀錄裡所有測試(去重)」都跑。item 3 判「找不到」的名字,在 item 4 會被當 `real` 送去 `_run_bound_tests`(它不再驗存在,L38606 起;`items` 的 status 由呼叫端給)。要嘛 item 4 只跑 item 3 通過的,要嘛送去的 status 標 `dangling`(`_run_bound_tests` 對非 `real` 直接回紅且不跑)。計劃沒說,而且會讓同一支測試名被兩個項目各報一次。

## 五、④ 機械宣稱驗語意

格式:原句 → 實際行為 → 判定 → 建議。

### A. `_codeloop_record_valid_ex`(S8 做不做得到)

原句:「`_codeloop_record_valid_ex(repo, 事件的 head_sha, 現在的 HEAD)` 判有效(同一個提交,或是祖先而且中間只動了簿記檔——跟代碼審留痕失不失效同一套;判不了也當作無效)」
→ `_codeloop_record_valid_ex(repo_root, rec_sha, marker_sha, timeout=None)` L39233,回 `(ok, 為什麼, 判不了)` 三元組。順序是 (記錄的 sha, 目標 sha),計劃的引數順序(事件 head_sha、現在 HEAD)正確。邏輯:`rec_sha` 空 → `(False,…)`;兩邊字串相等 → `(True,…)`;`git merge-base --is-ancestor`,回 1=不是祖先 → `(False, …, False)`,回其他非零=找不到提交 → `_codeloop_missing_commit`(淺 clone 才 `unsure=True`);祖先成立後 `git diff --no-ext-diff --raw --no-renames -z rec marker`,**所有變動檔都在 `_BOOKKEEPING_FILES`(含 `docs/.canary-log.jsonl`、`docs/.governance-log.jsonl`、`docs/.usage-log.jsonl`,L22664)或 `_BOOKKEEPING_DIRS`(含 `governance/review-reports/`,L22681)** 且簿記資料夾裡沒有程式檔/可執行檔才 True。→ **成立**。S8 的「事件之後只提交了審查帳時不印」做得到(審查帳、治理帳、`<輪>-fix.json`、`rN-dispatch.json` 都在白名單)。
補充(不改判定):
- 只看**已提交**的歷史;fix-check 通過後在工作目錄又改了程式、還沒提交,`loop next` 不會提醒。計劃〈實務隱患〉說的是「提交了簿記檔以外的任何檔」,沒提這個缺口。建議補一句承認它。
- 事件裡的 `head_sha` 來自治理帳,治理帳在簿記白名單裡可被直接手寫提交。呼叫前要先驗是 `^[0-9a-f]{40}$` 的字串;型別不對(例如 list)會在 `subprocess.run(["git", …, rec_sha])` 直接 TypeError,不是回「無效」。計劃的「判不了也當作無效」要寫成「驗不過格式、或 `ok` 為 False 都當無效」。`_GOV_FIELD_TYPES` 補 `head_sha` 只擋 `cmd_gov` 讀端,`loop next` 新寫的讀函式不經過它。

### B. `_lint_new_clean_stale` 與 `_LINT_NEW_STALE_SEC`

原句:「清掉系統暫存資料夾裡修正關卡前綴、超過一天的殘骸(寫法照 `_lint_new_clean_stale`,時限沿用 `_LINT_NEW_STALE_SEC`…)」
→ `_lint_new_clean_stale(repo_root)` L23798:只掃 `repo/.lumos/lintbase-*`(前綴寫死、位置寫死),用目錄 `st_mtime` 比 `_LINT_NEW_STALE_SEC`(L23365,=86400),`shutil.rmtree(ignore_errors=True)`;**不碰系統暫存、不處理 git worktree、不 prune**。`_LINT_NEW_STALE_SEC` 存在且是一天。→ **部分成立**:只能「照寫法新寫一支」,不能呼叫;計劃說的是「寫法照」,字面沒錯,但〈共用函式〉沒把這支新函式列出來(guard kill 的前綴 `lumos-kill-` 與新前綴要分開,不能誤清 guard kill 的殘骸)。
補充:guard kill 的樹是 `mkdtemp(prefix) / "wt"` 兩層(L14192 附近 `tmp_parent`、`wt = join(tmp_parent,"wt")`),前綴在上層目錄、worktree 在 `wt` 子目錄。清殘骸要對上層前綴做 mtime 判斷,對 `上層/wt` 做 `worktree remove --force`。計劃的「資料夾前綴」沒講是哪一層。
建議:〈共用函式〉加一條「清殘骸函式:參數=前綴、時限;比對 realpath;`git worktree remove --force` 失敗(別的 repo 的樹)照樣 rmtree」。

### C. `_lint_link_deps`

原句:「repo 頂與每個平台根各用 `_lint_link_deps` 把 `node_modules`、`.venv`、`venv` 連回主工作目錄的同一位置」
→ `_lint_link_deps(real_dir, snap_dir)` L23630;`_LINT_DEP_DIRS = ("node_modules", ".venv", "venv")`(L23590);只在 `src.is_dir()` 且 `link` 不存在時 `symlink_to`,`OSError` 吞掉。→ **成立**(參數 `(真目錄, 樹裡的對應目錄)`,對頂層與每個平台根各呼叫一次即可)。只連這三個名字,其他依賴(`Pods`、`.dart_tool`、`vendor`)不連,與計劃寫的一致。
但平台根在 repo 外的情形不成立,見 ④-I。

### D. `_lint_copy_configs`(★動到核心★ 不大,但接手最容易被誤導)

原句:PRIOR-ART「設定檔取現在版(`_lint_copy_configs`)」;〈做法〉「複製一份現在版進樹」(`.lumos/config.json`)
→ `_lint_copy_configs(repo_root, config_ref, real_dir, snap_dir, rel_dir)` L23607:對 `_LINT_CONFIG_GLOBS`(L23586:`*.config.js|mjs|cjs|ts`、`.eslintrc*`、`package.json`、`tsconfig*.json`、`pyproject.toml`、`setup.cfg`、`ruff.toml`、`.ruff.toml`、`detekt.yml`、`.swiftlint.yml`、`.stylelintrc*`、`stylelint.config.*`、`.sqlfluff`、`analysis_options.yaml`)在 `real_dir` **當層**逐個 glob,優先用 `git show config_ref:相對路徑` 的內容寫進 `snap_dir`,失敗才讀磁碟。**清單裡沒有 `config.json`,也不進子資料夾 `.lumos/`**,`config_ref` 還是必填。→ **不成立**(不能拿它複製 `.lumos/config.json`)。
計劃〈做法〉那句本身沒有說要呼叫它,只在 PRIOR-ART 把它列為「沿用零件」。樹是 `git worktree` 檢出,版控內的 lint 設定檔本來就在樹裡,不需要複製。
建議(修改前→後):PRIOR-ART「依賴資料夾連結(`_lint_link_deps`)與設定檔取現在版(`_lint_copy_configs`)」→「依賴資料夾連結(`_lint_link_deps`);`.lumos/config.json` 沒進版控時直接 `shutil.copy2`(先 `mkdir 樹/.lumos`)」。S12 的測試也別設計成呼叫 `_lint_copy_configs`。

### E. `cmd_guard_kill` 建樹那段 vs〈共用函式〉

原句:「把 `cmd_guard_kill` 裡『暫存資料夾 + `git -C <在哪建> worktree add --detach <路徑> [<提交>]` + finally 收掉(…)』抽成…回傳樹的路徑,`worktree add` 失敗時回傳原因、不丟例外。guard kill 照現在的寫法傳平台根、測試在樹的最上層跑、失敗記成 error 繼續下一個平台、`--keep-worktree` 時保留並印路徑」
→ 逐點對 L14160–L14330:
- `git -C` 在哪:`proot = Path(pentry["root"])`,`["git","-C",str(proot),"worktree","add","--detach",wt] + ([ghead] if ghead else [])`。**成立**。
- `ghead` 空:`git -C proot rev-parse HEAD` 失敗(例外被吞、輸出空)→ `ghead=""`,add 不帶提交(檢出該 repo 的 HEAD)。**成立**,「空的就不帶」正確。
- 失敗怎麼記:`r_add.returncode != 0` → 對這平台的每個配方 `results.append({…"verdict":"error","head_sha":"","detail":f"worktree add 失敗: {stderr[:120]}"})` 然後 `continue`(進 finally,add 失敗也清 `tmp_parent`)。**成立**。共用函式回原因的話,原因字串要保留 `stderr.strip()[:120]` 的截法,否則 guard kill 輸出字面會變(`t_guard_kill*` 有釘?請抽之前先 grep `worktree add 失敗`)。
- `--keep-worktree`:finally 第一支就是 `if keep_worktree: print(現場保留: wt)`(`as_json` 時走 stderr),**不 remove、不 rmtree**,且是**不收 `tmp_parent`**。**成立**,但共用函式的「要不要保留」要涵蓋「連上層暫存資料夾一起留」。
- 收法順序:`wt_ok` 才 `worktree remove --force`;`rmtree(tmp_parent)` 無條件;`wt_ok` 才 `worktree prune`(prune 放 rmtree 後)。與計劃寫的順序相同。**成立**。
- 測試在樹的最上層跑:`_kill_run(cmd, wt, …)`,cwd=`wt`(平台根所屬 repo 的頂層),**不是**平台根子目錄。**成立**。這跟 fix-check 不同:fix-check 走 `_run_bound_tests`,cwd 是 `pentry["root"]`(樹裡的平台根)。〈共用函式〉沒混淆這兩者,但 S11 的「測試在樹的最上層跑」只能對 guard kill 說,不能放進共用函式的契約。
- 兩層目錄:`wt = join(tmp_parent, "wt")`,所以共用函式「回傳樹的路徑」要同時管上層與 `wt`;若只回傳 `wt`,呼叫端自己 rmtree 上層要再 `dirname`。建議契約寫成 `with isolated_worktree(where, commit, prefix, keep) as (path_or_None, reason)`,內部管兩層。
- 抽成 `with` 之後,guard kill 內層迴圈的 `continue`(add 失敗)、`break`(revert 失敗)都在 `try/finally` 裡,改成 `with` 語意相同;但 `wt_ok` 變數也被外面的 `finally` 用,抽的時候要一起搬。
→ **成立**(三處細節要寫進契約:兩層目錄、`--keep-worktree` 連上層一起留、add 失敗訊息截 120 字)。

### F. 規格閘兩處抽成一支(★動到核心★:S12 與 item 4 都靠它)

原句:「規格閘的條款測試與相依回歸兩處,都是『`_run_bound_tests` 跑一批 → 每支用 `_ran_count`、`_spec_gate_declared`、`_spec_gate_verdict` 判』,手寫了兩份。抽成一支(參數:在哪個根跑、要跑的測試清單;回每支的紅、綠、弱證據與原因),規格閘兩處與修正關卡第 4 項都用它;規格閘印出來的字面不變」
→ 兩處實際長相:
- `_spec_gate_run_clauses(rr, plats, items, per_prof, loose_for)` L6625:`_run_bound_tests(rr, items, tails=tails)`;`results is None` → **印** `[spec-gate] 跑: —(略過:{rerr})` 回 `{}`;逐支 `_ran_count(per_prof(plat), tails[(node_id,plat,method)])`、`_spec_gate_verdict(n, skipped, verdict, detail, declared=_spec_gate_declared(method, loose_for(plat)))`;**同條款多支測試時「任一非綠蓋過綠」**(`prev[0]=="green" and v!="green"` 才覆蓋);最後按條款 id 排序印 `[spec-gate] 跑: {cid} {紅|綠|弱證據}({method}…)`——**印的動作在函式裡**。
- `_spec_gate_regress(...)` L6647 的內段:`ritems` 的 status 是 `"real" if method in methods_for(plat) else "dangling"`(條款那邊一律 `"real"`);`rres is None` → **不印、改 append 到 `fails`**("相依回歸跑不起來:…");逐支同樣算 `(v, why)`,但**紅時用的是 `detail`**(`f"…:紅({str(detail)[:80]})——既有行為回歸,或環境壞"`),不是 `why`;弱證據用 `why`;沒有「任一非綠蓋過綠」,而是逐支各自加進 `ok` 或 `fails`。
→ **部分成立**。「手寫兩份」成立、核心 `_ran_count → _spec_gate_declared → _spec_gate_verdict` 一模一樣,可以抽;但抽出來的函式必須:
 1. 參數要 `(root, items, per_prof, loose_for)`,不是「在哪個根跑、要跑的測試清單」兩個(`per_prof(plat)` 取 `plats[plat]["profile_name"]`,`loose_for` 來自 `_platform_test_index(root)` 第 6 個回傳值;兩處都是呼叫端傳進來的,fix-check 在樹裡要自己 `load_platforms(樹)` 與 `_platform_test_index(樹)` 各取一次);
 2. 回傳要含 `detail`(`_run_bound_tests` 回的原始失敗尾巴),因為相依回歸的紅字面用它,`why` 不等於 `detail`(`n is None and verdict=="red"` 時 `why`=「這棧還讀不出支數,只印有沒有跑過」);
 3. 回傳要能表達「`results is None` + 原因」,兩個呼叫端的處理不同(一個印、一個進 `fails`);
 4. 「任一非綠蓋過綠」與「印出來」留在條款那邊的呼叫端,不進共用函式。
建議(修改前→後):「抽成一支(參數:在哪個根跑、要跑的測試清單;回每支的紅、綠、弱證據與原因)」→「抽成一支 `_spec_gate_judge_items(root, items, per_prof, loose_for)`,回 `(rows, err)`,`rows=[(id, plat, method, v, why, detail)]`、`err` 是 `_run_bound_tests` 的原因字串;印出與聚合留在兩個呼叫端」。S12 的「字面不變」才釘得住。
另:計劃說 item 4「平台的 `run_cmd` 沒有 `{method}` 也不過(同規格閘)」——規格閘對沒有 `{method}` 的平台是 `_spec_gate_runnable`(L6609)**印『略過』、整批不跑**,不是判不過。「同規格閘」只是判法同(都是看 `{method}`),結果不同。建議把「同規格閘」改成「(規格閘是略過,這裡是判不過)」。

### G. `_run_bound_tests`、`_bound_tests_check`、`_platform_test_index`、`resolve_test_refs` 傳樹的路徑

原句:「`_bound_tests_check(Path(樹), "base..修正後")`(推送前那道閘的同一支…它寫的治理帳事件與測試快取落在樹裡、跟著刪掉…)」「`resolve_test_refs`…要恰好解析出一支、而且在樹的測試索引裡找得到(`_platform_test_index(樹)`)」
→
- `load_platforms(repo_root)`(L4811)讀 `repo_root/.lumos/config.json`;legacy 模式 `root=repo_root`;多平台模式 `root=(repo_root / root_str).resolve()`,**`repo_root` 一定要是 `Path`**(字串會在 `/` 上炸)。→ 與計劃「參數要是 `Path`」一致,**成立**。
- `_run_bound_tests(repo_root, items, tails=None)` L38606:每支用 `pentry["root"]`(樹裡的平台根)當 cwd,`_kill_run`;逾時單支 `LUMOS_TEST_TIMEOUT`(預設 180)、整套 600s。**成立**。
- `_bound_tests_check` L38725:`_bound_tests_log(repo_root,…)` 經 `_vault_in(repo_root)` 找樹裡的 `docs/*-knowledge`、`_append_governance_log(vault, …)` 寫 `vault.parent/.governance-log.jsonl`(樹裡);過濾探針快取 key 含 `os.path.realpath(root)`(L38520 一帶)所以每棵新樹都重探。**成立**(含計劃自己承認的重探)。
- `_bound_tests_for_diff` 用 `cmd_impact_diff(range, repo=str(樹))`,節點與合約讀樹裡提交的那版。**成立**。
- **部分成立:`green` 不等於全跑了**。`_bound_tests_check` 在部分平台沒設 `run_cmd`(`no-cmd`)時,**仍可回 `status:"green"`**,只是 `not_run` 非空、`reason` 尾巴加「;另有 N 支沒跑——…」(L38812 一帶、L38870 的 green 分支帶 `not_run`)。計劃說「`green`…過」,會把「有平台的合約一支都沒跑」放行。建議 item 5 加:`green` 且 `not_run` 非空 → 不過(或至少印出並記進 `failed_items`)。
- `skipped` 路徑:`LUMOS_SKIP_BOUND_TESTS=1` → 回 `{"status":"skipped"}`、寫 `skipped-env`/`skipped-flag` 事件到樹的帳(同樣在樹裡)。計劃「`skipped` 也不過,印要用 `LUMOS_SKIP_FIX_CHECK`」**成立**。
- `whole-suite-deferred` 只在 `advisory=True` 回;fix-check 不傳 advisory,永遠不會出現。計劃把它列在「不過」清單無害,但屬死分支。
- `resolve_test_refs(inv_text, platforms, default_platform)` L4896:**只切字串,不驗存在**;`platforms` 非空(多平台)且含 `:` 而前綴不在 `platforms` → **`raise ValueError`**;legacy(`split={}`)不切分。計劃的「恰好解析出一支、找不到的都算不過」沒說 `ValueError` 要接住(`_bound_tests_for_diff` 是 `except ValueError → bad-name`)。建議 item 3 寫「`ValueError` 當作不過,訊息帶原因」。`[test:名]` 包法本身:名字含 `]` 會被 `TEST_REF_RE`(`\[test:\s*([^\]]+)\]`,L4463)截斷、含 `,` 會被切成兩支;「恰好一支」的檢查能擋掉逗號,擋不到「名字尾端有 `]`」(`[test:t_x]]` 仍解析成 `t_x`)。這種名字進不了索引,item 3 本來就判不過,影響不大。
- **存在性的口徑要跟 `_bound_tests_for_diff` 一致**:那邊 `real = method in mset or ("." in method and method.rsplit(".",1)[-1] in mset)`(Class.Method 寫法)並用 `_KILL_METHOD_OK_RE.fullmatch` 白名單(L13159);計劃寫的是「在索引裡找得到」,沒提 `Class.Method` 與白名單。建議抽/抄同一個判法,否則 Kotlin/C# 的 `Class.Method` 在 item 3 會判不過、在合約閘卻是 real。
- `methods_for` 是「錨在欄位 0」的清單(`_platform_test_index` 的 docstring):類別內的測試方法某些棧找不到。本 repo(`t_` 開頭的模組層函式)不受影響;其他棧可能誤判不過,可在〈實務隱患〉記一句。
→ 總評:**大致成立,上面 3 條要寫進計劃**(`green`+`not_run`、`ValueError`、存在性口徑)。

### H. `_gate_event_or_warn` 寫不進去時的行為

原句:「寫不進治理帳時照 `_gate_event_or_warn` 的行為,輸出另加一句『這次通過沒記到帳,`loop next` 會一直提醒』」
→ `_gate_event` L1179–1232:`docs/` 不存在 → 回 **`None`**(不適用,什麼也不印);`gate not in _KNOWN_GATES` → 印警告、回 `False`;`open(...,"a")` `OSError` → 回 `False`。`_gate_event_or_warn` L1234:`ok is None` → 回 None 不印;`ok False` → 印 `⚠ telemetry-write-failed:{gate} 這一筆帳寫不進去(判定不受影響…)` 回 False。→ **成立**,且「判定不受影響」與計劃一致。補充:`None`(沒有 `docs/`)時也不會印「沒記到帳」,計劃的「另加一句」要涵蓋 `ok is not True`,不只 `False`。`note` 是必填位置引數,計劃沒列(寫 `note` 要放什麼)。`kind` 傳入、`hard=False`、`head_sha`、`extra` 都是合法關鍵字(`_gate_event_build` L1147)。事件的 `commit` 欄是 `head_sha[:7]`。

### I. 平台根在 repo 外(★動到核心★)

原句:「依賴資料夾:repo 頂與每個平台根各用 `_lint_link_deps`…」「整次的測試都在樹裡跑」
→ `load_platforms` 的 `root=(repo_root / root_str).resolve()`:`root_str` 為 `../Compass_KDS` 時,在樹(系統暫存)底下解析成 `…/tmp/../Compass_KDS`,不存在(只印警告,不擋,L4860 一帶);`_run_bound_tests` 用它當 cwd,`_kill_run` 的 `Popen(cwd=…)` 會 `FileNotFoundError`(或在「碰巧存在」時跑到別 repo 的主工作目錄,而非樹)。`cmd_guard_kill` 每平台各自 `git -C proot`,說明多根(多 repo)是被支援的。→ **不成立**(對 repo 外的平台根)。
建議:先決條件加一條「任一平台 `root` 不在 repo 內(`Path.resolve()` 後不以 repo 根為前綴)→ 回 2(或該平台的項目標『不支援跨 repo 平台,未驗』並判不過),印原因」;〈實務隱患〉寫明這是已知範圍外。實作者不知道這點,第一個遇到多根專案(本機 18 個專案裡的多平台那幾個)就會看到靜默壞掉或奇怪的錯誤。

### J. `cmd_gov` 的轉換、去重鍵、`_GOV_FIELD_TYPES`

原句:「治理帳讀端(`cmd_gov` 的轉換)對 `fix-check` 事件吐出 `token`…(去重鍵本來就含 `token`,轉換沒吐它,同一個提交連跑兩次同結果會被折成一筆);`_GOV_FIELD_TYPES` 補 `record_sha256`、`secs`(整數與浮點)、`failed_items`、`head_sha`」
→ `.governance-log.jsonl` 的 mapper(L7636 一帶)輸出的 `token` 只在 `gate=="canary" and kind=="blocked"`(用 ts+note)或 `gate=="code-loop" and kind in (dispositions, recall-miss)`(用 written_at)時才有,其餘一律 `""`;去重鍵 `k = (commit, frozenset(nodes), gate, kind, token, check or "")`(L7716)。`commit` 欄是 `head_sha[:7]`。→ **成立**:同一個 `head_sha`、`nodes=[]`、同 `kind` 連跑兩次,在 token 沒吐出時確會折成一筆;mapper 要加分支(例:`gate=="fix-check"` → `d.get("token","")`)。
`_GOV_FIELD_TYPES`(L7577):`token` 已是 `(str,)`、`loop` 是 `(str, None)`、`round` 是 `(str,int,None)`,這三個不用補;`record_sha256`、`secs`、`failed_items`、`head_sha` 目前**沒有**列入,補了才會被檢查。我掃了 `/Users/enzo/harness/lumos-toolchain/docs/.*.jsonl`(目前 HEAD)這幾個鍵:`head_sha` 只有 str(1375 筆)、`secs`/`calc_secs` 只有 float(218 筆,都是 bound-tests 的)、`record_sha256`/`failed_items`/`regression_set` 沒出現。所以計劃的「`secs` 整數與浮點」「`head_sha` 字串」不會丟既有行。→ 成立。一個小提醒:`_gov_event_types_ok` 的規則是 `k in d and not isinstance(d[k], types)` → 整行丟棄,所以 `secs` 若要接受 `null` 要寫 `(int, float, type(None))`;`bool` 是 `int` 子類,`secs: true` 也會過,無害。
`_is_advisory`(L7747):`kind=="warned"` 且沒 token 沒 detail 才會被折成 ×N;fix-check 事件帶 token(plan)與 note,不會被折。

### K. `cmd_canary` 的 `--folded-set` 解析與「要跟 --findings-set 一起給」

原句:「解析照 `--folded-set`;id 都要在 `--findings-set` 裡,否則回 2;沒帶 `--findings-set` 的那筆帶了回 2;迴圈在審查帳上還沒有更早的輪、卻帶了非空清單,回 2。存成排過序的 `regression_set`(`none` 存空清單)」
→ L8566:`_ids(raw)`:`None`=未給、`""`=明示空集合,逗號切、去空白;`f_set is None` 而給了 `fo_set/ac_set/accept_reasons/refute_verdicts/finding_kinds` 任一個 → 擋(L8567–8569 那串)。**`--folded-set` 本身沒有 `none` 關鍵字**(空字串才是空集合),而計劃要 `--regression-set none`;`--refuted-set` 才有 `none`(L8606–8610 `str(refuted_set).strip().lower() != "none"`)。所以「解析照 `--folded-set`」不夠:要自己加 `none` 分支,並決定 `--regression-set ""` 算什麼(建議也擋,「空項要寫 none」,同 `--refuted-set` 的空項規則)。→ **部分成立**。
其他:
- 「沒有更早的輪」要用 `_loop_records(env, loop)` 取同編號紀錄、看**不同於本筆 round 的**輪;同一輪先記的非載體席不算更早的輪。計劃寫「更早的輪」,但 S9 測試要覆蓋「同輪先記了席位列、這筆載體席帶非空 → 仍回 2」。
- `findings_set` 本身不要求 `loop`(L8750 只在 `loop and findings_set is not None` 時要 `round+auditor`),所以 `--regression-set` 沒帶 `--loop` 時「更早的輪」無從查;要寫「沒帶 `--loop` 也回 2」或明說不查。
- 參數要加進 `cmd_canary` 的簽名(L8422)、argparse(L41078 附近)與呼叫端(L42119 附近);計劃沒列,屬實作細節。
- `_GOV_FIELD_TYPES` 對 canary 帳的 mapper 只讀它認得的欄(L7676 一帶),`regression_set` 若不加進 mapper/表,`cmd_gov` 讀它是忽略,無害。

### L. `loop next` 的記帳範本在哪產生

原句:「第 2 輪起,`loop next` 給的載體席記帳範本多帶 `--regression-set <id串|none>`」
→ 見 ③-3:`disposal_cmd`(L11663),僅 `phase=="plant-canary"`、`not light and eff_tier != "legacy"`(code 循序 `seq` 也在內),且**只有 `--json` 看得到**。第幾輪 = `n_next`(L11580,`rounds_count + 1`)。**部分成立**(位置對、可見性不對)。測試 `t_loop_next_disposal_cmd_actually_runs`、`編號加引號①` 等釘著 `disposal_cmd` 字面。

### M. `loop next` 提醒的實作落點與「新寫一支讀函式」

原句:「新寫一支讀函式,逐行先用字串預篩含 `"fix-check"` 的行再交給 `_drift_jsonl_parse`,壞行跳過」
→ `_drift_jsonl_parse(raw)` L29834:**吃整份位元組**(`raw.decode("utf-8", errors="replace").split("\n")`),內部逐行 `json.loads`、接 `ValueError/RecursionError`、非物件行略過。它不是「逐行呼叫」的介面。→ **部分成立**:預篩之後把留下的行 `b"\n".join(...)` 再整批餵進去即可;逐行呼叫會重複 decode/split,不錯但沒必要。位元組層級預篩(`b'"fix-check"' in ln`)比字串預篩便宜。`emit`(L11585)是五個狀態的單一出口(`return 0 if phase == "converged" else 1`),提醒放在 `emit` 就能「不管哪個狀態都印、rc 不變」。文字模式 `emit` 只印選定的鍵(L11790),所以只往 `out` 加 `fix_check` 欄不會出現在文字輸出——要自己加印行(計劃寫了「輸出加一行提醒」,實作要記得兩條路都接)。

### N. 派工單 `base_commit`

原句:「讀派工單的既有函式(`_roster_dispatch_entries`、`cmd_seat_check`)只讀自己認得的鍵,多一欄不影響」「`<輪>-dispatch.json` 的 `base_commit`」「卷證裡有舊形狀的派工單(單席物件、頂層陣列)時,只認物件形狀的頂層 `base_commit`」
→ `_roster_dispatch_entries(loop_dir, rid)` L11144:`glob(f"{rid}-dispatch*.json")`,三種形狀:dict 帶頂層 `auditor`(單席)/dict 帶 `seats` 陣列/頂層 list;只取 `auditor`。`cmd_seat_check` L21339 只取 `materials/round/seat/lens`。兩者都不會因多一欄出事。→ 「多一欄不影響」**成立**。
但有兩處不精確:
- `glob(f"{rid}-dispatch*.json")` 表示一輪可能有**多份**派工單(`r1-dispatch.json`、`r1-dispatch-codex.json`…)。計劃只讀 `<輪>-dispatch.json` 一份;多份且 `base_commit` 不一致時沒說怎麼辦。建議:只讀字面 `<輪>-dispatch.json`,沒有就留空(並在 `--record-template` 的 stderr 說)。
- 「單席物件」也是物件(頂層帶 `auditor`),所以「(單席物件、頂層陣列)…只認物件形狀」自相矛盾:單席物件也是物件形狀。要說的應是「只認頂層是 dict 的檔(含單席物件與帶 `seats` 的 dict);頂層是 list 一律當沒有」。

### O. `git rev-parse --verify --end-of-options <x>^{commit}`(實際跑了)

本機 `git version 2.39.2 (Apple Git-143)`。在 `pf-fix0-work/repo` 跑:`HEAD`、`main`、`HEAD~1`、短 sha → 都回 40 碼、rc=0;`-x`、`--abbrev=4`、`-`、`nonexistent`、空字串、`HEAD:scripts/lumos` → 都 `fatal: Needed a single revision`、rc=128(不會被當旗標)。→ **成立**。補充:`--end-of-options` 是 git 2.24(2019-11)才有,舊機器上 `rev-parse` 會回錯誤,fix-check 會把它當「轉不成」回 2(失敗方向安全,但訊息會誤導)。另外 `base` 若是分支名(計劃允許),它解析的是**跑 fix-check 當下**分支尖端,不是派工當下;模板從 `base_commit` 帶值(40 碼)所以正常流程沒事,手填分支名要自負。

### P. S11 殘骸、S4 `git worktree list`、其他小項

- `git worktree remove --force` 對「別的 repo 的樹」會失敗;計劃寫「是工作樹的先 `git worktree remove --force` 再刪資料夾」,失敗後仍要 rmtree(殘骸才清得掉)。建議寫進〈共用函式〉。
- 事件 `commit` 欄只存前 7 碼,去重鍵用它;兩個不同 `head_sha` 前 7 碼相撞的機率可忽略。
- `_ran_count` 的 python 路徑:自家 runner 印 `lumos 測試(N 案例)`(`_RAN_EVIDENCE["python"]["count_re"]`),這就是計劃 S4 `t_fcdemo` 能得到「篩選匹配到 2 支」的根據;`_spec_gate_verdict` 在 `n>=2 and declared != 1` 回 weak 並帶「篩選匹配到 N 支,測試名要唯一」字樣,**成立**;`declared==1` 且 `n>=2`(參數化)走綠,**成立**。
- 載體席帳上筆數:`negguard` 的 `docs/.canary-log.jsonl` 裡 `code-` 開頭且帶 `findings_set` 的有 315 筆(計劃寫 314,差 1 筆,應為寫計劃後又多記一筆;不影響結論)。

## 六、⑤ 〈實務隱患〉沒寫到的(補充,非壞引用)

1. **時間**:「約 5 分鐘」只算 python 可過濾的情形;`_run_bound_tests` 對沒有 `{method}` 的平台是整套跑、單套 600 秒上限,每個這樣的平台一次最多 10 分鐘(`_BOUND_TESTS_WHOLE_SUITE_TIMEOUT`),計劃的「>10 分鐘」RETIRE-IF 條件與全域規則「對話裡跑不完的交給閘」會撞。item 4 對這種平台判不過(不跑),但 item 5 照跑;建議 item 5 對這種平台也先判再跑,或在輸出標明預估耗時。
2. **派工當下有未提交改動**:計劃只在 fix-check 開跑時警告未提交改動;`base_commit` 是 `git rev-parse HEAD`,若審查材料是工作目錄裡還沒提交的改動,`base..修正後` 會把整個功能都算進去(`fixed` 的「有改動」檢查必然過、受波及合約範圍膨脹到整個功能)。建議手冊第 2 步註明「派工前先提交」,或 `base_commit` 寫入時順便印未提交改動的警告。
3. **路徑安全**:`governance/review-reports/<迴圈編號>/<輪>-fix.json` 由 `--round` 字串直接拼進檔名;`--round "../../x"` 或迴圈編號含 `/`(只要 `code-` 開頭,如 `code-/../..`)可指到 repo 外。既有 `_roster_dispatch_entries` 也是直接 glob 拼接(L11144),但那是讀;這裡 `--record-template` 不寫檔、`fix-check` 只讀,風險低,但仍建議驗「輪與編號不含路徑分隔字元、不是 `..`」(全域規則的「路徑處理」類)。
4. **`loop next` 的提醒會被偽造的 `passed` 事件靜音**:治理帳在簿記白名單裡可直接提交一行。這是只提醒不擋的閘,風險小,可在 RETIRE-IF 或隱患註一句「提醒不是防繞過」。
5. **`_codeloop_record_valid_ex` 的逾時**:預設 `_disp_git_timeout()`(L19003 附近的同一支),`loop next` 每次呼叫多 1–3 次 git;計劃已量過預篩 0.1 秒,但沒量這幾次 git 的耗時,`loop next` 是每輪第一步、頻繁呼叫。

## 七、結論(必修)

1. **`LUMOS_SKIP_FIX_CHECK` 跳過後提醒仍響(③-1)**:S8 與〈提醒〉只認 `passed`,跳過記的 `skipped-env` 不算,跳過沒效。改:`passed` 或 `skipped-env`(同 loop+round、`head_sha` 仍有效)都不提醒,後者印一行「已跳過」。
2. **規格閘抽共用函式的介面不夠(④-F)★動到核心★**:參數要 `(root, items, per_prof, loose_for)`;回傳要含 `detail`;要能回「`results is None` + 原因」;印出與「任一非綠蓋過綠」留在呼叫端。否則 S12「字面不變」做不到(相依回歸的紅字面用 `detail` 不用 `why`)。「同規格閘」對無 `{method}` 的描述也要改(規格閘是略過,這裡是判不過)。
3. **repo 外的平台根(④-I)★動到核心★**:樹放在系統暫存,`root: "../xxx"` 的平台跑不到樹。加先決條件(回 2 或判不過並說明),寫進〈實務隱患〉。
4. **`_bound_tests_check` 回 `green` 但 `not_run` 非空(④-G)**:有平台沒設 `run_cmd` 時,合約測試部分沒跑也回 green;item 5 要把 `not_run` 非空判不過(或列入 `failed_items`)。
5. **`_lint_copy_configs` 不能複製 `.lumos/config.json`(④-D)**:PRIOR-ART 與 S12 的設計別指它;直接 `shutil.copy2`(先 `mkdir 樹/.lumos`)。
6. **`loop next` 的載體席範本是 `disposal_cmd`,只在 `--json`(③-3、④-L)**:決定是只改 JSON、還是文字模式也印;補 `t_loop_next_disposal_cmd_actually_runs` 的同步修改;S8 的範本斷言對準 `disposal_cmd`。
7. **做事順序(③-4)與 item 3→4 的串接(③-5)**:便宜先決條件 → 清殘骸 → 建樹;item 3 判找不到的名字不送 item 4(或標 `dangling`)。
8. **`--regression-set` 的 `none` 與空字串(④-K)**:`--folded-set` 沒有 `none` 語意,要自己加;`--regression-set ""`、沒帶 `--loop`、同輪先記的席位列都要定義(S9 補測)。
9. **事件 `head_sha` 進 `_codeloop_record_valid_ex` 前先驗格式(④-A)**:帳可被手寫,型別不對會 TypeError,不是「無效」。
10. **`resolve_test_refs` 會 `raise ValueError`、存在性口徑要跟 `_bound_tests_for_diff` 一致(④-G)**:接住 `ValueError`、抄 `Class.Method` 與 `_KILL_METHOD_OK_RE` 的判法。
11. **小修**:`_nodehome_code_kind` 回 `'shebang?'` 的處理(②-2);`unaffected` 理由判法寫成具體數字(②-1);S8 狀態清單與〈做法〉對齊(③-2);派工單多份與「單席物件也是物件」的敘述(④-N);`_drift_jsonl_parse` 吃整份位元組(④-M);清殘骸函式列為共用函式的第三支並指明前綴落在上層暫存資料夾(④-B)。
