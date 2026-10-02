severity: major

# r2 整合-sonnet(鏡頭:整合與接手)

立場:三個月後照這一版實作的接手者。所有程式碼查證都在凍結的 repo 根(`.../scratchpad/negguard`,HEAD 58519acf)做,未動任何檔、未跑全套。

## F1 測試名白名單的字面描述跟實際正則對不上,照字面做會擋掉合法的「平台:名」、又放過帶空白的名字
severity: major
blocking: 是
引句:「去掉前後空白後要過 `_KILL_METHOD_OK_RE` 白名單(含 `]`、空白、shell 字元的直接判不過」
file: `scripts/lumos:13159`
file: `scripts/lumos:13193`
file: `scripts/lumos:38434`

1. 實際正則是 `^[A-Za-z_][A-Za-z0-9_]*$|^[\w .]+$`,第二支允許中間的空白與句點,不允許冒號。快照說「空白直接判不過」不是這支正則做的事。
2. 最小實驗(本機直接跑那條正則):
   - `"t x"` -> True(中間空白通過白名單)
   - `"a.b"` -> True
   - `"py:t_x"` -> False(平台前綴被擋)
   - `"a;b"` -> False
3. 壞在兩處:
   - 第 86 行把白名單套在「紀錄裡寫的整串測試名」上。多平台設定下非預設平台的測試必須寫 `平台:名`(`resolve_test_refs` 靠冒號切平台,見 `scripts/lumos:4896`),整串過白名單會把所有非預設平台的測試判成不合法。S4 明寫要支援多平台。現有兩處用法都是先去前綴再驗:`_kill_method_name`(`scripts/lumos:13193`)與 `_bound_tests_for_diff`(`scripts/lumos:38434`,驗的是 `resolve_test_refs` 之後的 `method`)。快照沒說驗哪一段,第 3 項又寫「`resolve_test_refs` 丟 `ValueError`」,兩處讀起來不是同一個順序。
   - S1 條款寫「測試名含 `]` 或空白應回 1」。含 `]` 會被白名單擋,含中間空白的 `t x` 不會被白名單擋;它只會在第 3 項「索引裡找不到」才判不過。回 1 還是對的,但「這條被哪一項擋」跟條款字面不同,而且 Kotlin 這類索引裡真有含空白方法名的棧,會直接放行。
4. 接手者要的決定:白名單套在 `resolve_test_refs` 之後的 `method` 上(跟 `_bound_tests_for_diff` 同一個位置),並另寫「名字裡有空白一律不收」是額外規則,或把 S1 的字面改成「判不過」不指定哪一項。

## F2 手冊同步清單指的 reference.md「步驟 1–8」不是現行段落,是整段封存的舊版全文
severity: minor
blocking: 否
引句:「lumos-code-loop 手冊 `SKILL.md` 與 `reference.md` 裡那份步驟 1–8 都要改」
file: `skills/lumos-code-loop/reference.md:31`
file: `skills/lumos-code-loop/reference.md:553`
file: `skills/lumos-code-loop/reference.md:580`

1. `reference.md` 現行的〈步驟總覽〉是 7 步、編號跟 SKILL.md 不同(它的 4=派審、5=判讀、6=記錄、7=mutation;修正在〈修與翻紅釘〉小節,沒有編號)。快照寫的「第 2、5、6、7 步」在 reference.md 現行段落找不到對應。
2. SKILL.md 那種「1–8」編號只存在 reference.md 第 553 行起的〈入口頁舊版全文(去時效前)〉,該段開頭自己寫「只供查每條規則的由來與踩過的事故,不是現行規則」。照字面去改它,等於改歷史封存檔。
3. 接手者實際要改的:SKILL.md 的第 2、5、6、7 步(都找得到:派工單落 `rN-dispatch.json` 在第 2 步末、「修與釘」第 5 步、記帳第 6 步、問閘第 7 步),reference.md 要改的是〈步驟總覽〉第 4/6 項與〈修與翻紅釘〉、〈5 · 記錄〉。快照要明講改哪幾節、不動封存段。
4. 同一行的「跟『收斂前派全新席掃 delta』並列」:那句話在 SKILL.md 第 5 步,不是第 7 步之後;並列位置要改成第 5 步。
5. 數字檢查:SKILL.md 本體現有日期 3 個(2026-09-12、2026-09-30、2026-08-25),剛好壓在 `t_skill_entry_pages_no_dated_history` 的上限 3,新增任何日期字樣就紅。

## F3 前一輪的判法:`_disposal_round_groups` 可以直接呼叫,但快照沒說它回 (None, 訊息) 與「前一輪」可能是 delta 輪
severity: minor
blocking: 否
引句:「前一輪=審查帳上這個迴圈、在這一輪之前最近出現的那一輪(照 `_disposal_round_groups` 的分輪與順序」
file: `scripts/lumos:20590`
file: `scripts/lumos:11090`

1. 可行:簽名 `_disposal_round_groups(rounds)` 回 `(OrderedDict, None)` 或 `(None, 訊息)`,順序是帳上首次出現序,取 `--round` 那組的前一個 key 即可。讀帳用 `_loop_records(env, loop_id, strict=True)`(`cmd_loop_next` 同一支,已濾掉 `kind=spec-gate`),快照沒點名這支,自己讀帳會漏濾規格閘列。
2. 快照沒寫:回 `(None, 訊息)`(輪次用 `__` 開頭、或同一輪被別輪隔開後重現)時 fix-check 怎麼辦。照 `cmd_loop_status` 的做法是印訊息回 2;沒寫的話接手者會對 `None` 迭代而丟例外。
3. 本機帳實測輪次字串:r1、r2、r3、r4、r5、r3b、r3-dref、r4-dref-delta、r5-recap 等。「前一輪」照帳上順序會是 delta 輪,delta 輪通常沒有修正紀錄,S6「同類連兩輪」就整個不要求。這是設計選擇,不是錯,但要在快照寫成已知行為。

## F4 「規格閘遇到這種是整批略過」只對條款那一處成立;共用函式若把這道略過收進去會改掉另兩處
severity: minor
blocking: 否
引句:「平台的 `run_cmd` 沒有 `{method}`(只能整套跑)時這個平台的測試不跑、判不過並說明(規格閘遇到這種是整批略過」
file: `scripts/lumos:6591`
file: `scripts/lumos:6647`
file: `scripts/lumos:7029`

1. 三處副本核對過,抽 `_spec_gate_judge_items(根, 測試清單, per_prof, loose_for)` 的介面抽得出來:
   - `_spec_gate_run_clauses`(6625):迴圈內用 `per_prof(plat)`,同一條款多支取最壞,印出在函式外圍。
   - `_spec_gate_regress`(6647):`rmap` 以 `(rid, plat, method)` 找來源節點,紅的字面用結果元組第 5 個值(`detail`)。`_spec_gate_verdict` 在 `n is None` 時會丟掉 detail,只回「這棧還讀不出支數」,所以非回傳 detail 不可,快照已寫到。
   - `_spec_gate_push_one`(7029):`per_prof` 其實是 `(plats.get(pl) or {}).get("profile_name")`,與 `cmd_spec_gate` 內定義的 `per_prof` 等價,可統一。
2. 只有條款那一處先經 `_spec_gate_runnable`(6591)濾掉沒有 `{method}` 的平台;相依回歸與推送前這兩處沒有這道濾網,`_run_bound_tests` 對沒有 `{method}` 的平台會跑整套(`scripts/lumos:38629`)。快照這句會讓人把濾網寫進共用函式,結果相依回歸與推送前的行為被改掉,違反 S12 的「判定跟抽之前一樣」。
3. 該寫明:濾網留在 fix-check 自己的呼叫端,共用函式不含。
4. 抽之前後要一起跑的既有測試(都走 CLI,沒有直接引用內部函式,翻紅風險在行為而非介面):
   - 條款:`t_spec_gate_run_summary`、`t_spec_gate_writes_run_record`、`t_spec_gate_needs_method_filter`、`t_spec_gate_zero_ran_is_weak`、`t_spec_gate_multi_ran_is_weak`、`t_spec_gate_parametrized_is_not_weak`、`t_spec_gate_collision_inside_class_still_weak`、`t_spec_gate_twoway_pass_each_red`、`t_spec_gate_twoway_weak_blocks`、`t_spec_gate_twoway_unique_tests`
   - 相依回歸:`t_spec_gate_regress_lists_linked_contract_tests`、`t_spec_gate_regress_red_blocks`、`t_spec_gate_regress_unbound_contract_flagged`
   - 推送前:`t_prepush_spec_gate_tests_green`、`t_prepush_spec_gate_red_blocks`、`t_prepush_spec_gate_stale_record`、`t_prepush_spec_gate_door_rejudged`、`t_prepush_spec_gate_nonclause_edit_ok`、`t_prepush_spec_gate_code_home`
   - 守衛:`t_platform_index_consumers_drift_guard`(解構必須剛好六個值)

## F5 `--keep-worktree` 的輸出串流:共用函式若自己印路徑會讓 `--json` 純度測試翻紅
severity: minor
blocking: 否
引句:「要保留時兩層都留、只印路徑(照 guard kill 現在 `--keep-worktree` 的行為)」
file: `scripts/lumos:14290`
file: `scripts/test_lumos.py:20245`

1. 現行 guard kill 的保留訊息走 `file=(sys.stderr if as_json else sys.stdout)`;`t_guard_kill_json_purity` 的 `--json --keep-worktree` 情境斷言 stdout 恰一行合法 JSON。
2. 快照沒說「誰印、印去哪」。共用函式若自己印到 stdout,該測試翻紅;應由呼叫端印,或傳串流。
3. `with` 區塊化本身可行:guard kill 迴圈內的 `continue`(add 失敗)與 `break`(revert 失敗)在 `with` 內語意不變,現有 finally 的收拾順序(`worktree remove` -> rmtree -> `prune`)可原樣搬。
4. 要連同翻的既有測試:`t_guard_kill`、`t_guard_kill_json_purity`、`t_guard_kill_rc_precedence`、`t_guard_kill_attribution`(含「worktree 無殘留」那段,`scripts/test_lumos.py:20504`)。

## F6 `fix_check.link_deps` 沒有現成的 fix_check 讀取;而且 `load_platforms` 讀到壞 JSON 不會丟例外
severity: minor
blocking: 否
引句:「`load_platforms(樹)` 讀得懂(丟例外就回 2)」
file: `scripts/lumos:4811`
file: `scripts/lumos:23507`
file: `scripts/lumos:5760`

1. 現行程式沒有任何 `fix_check` 設定讀取。可沿用的寫法有兩支:`_lint_new_config(repo_root)`(`scripts/lumos:23507`,直讀 `.lumos/config.json`、回含 `warnings` 的 dict、每鍵驗型別、不合法用預設並警告)與 `_note_lint_config`(`scripts/lumos:5760`,多了捷徑檔與非物件判斷)。要讀的是樹裡那份,路徑是 `Path(樹)/.lumos/config.json`;`_note_lint_config` 的「resolve 後相等」比法在 macOS 的 `/var` 對 `/private/var` 下是兩邊都 resolve,不會誤判。
2. 快照只寫「設定 `fix_check.link_deps: true`」,沒寫非布林(`"false"` 字串、`1`)怎麼處理。照 `_lint_new_config` 的做法,要明寫「只有 `True`(布林)才連,其他值警告並當不連」。
3. `load_platforms` 遇到 JSON 壞掉、讀不了時只印警告並退成單平台預設(`scripts/lumos:4826`-`4829`),不丟例外。快照把「讀不懂」等同「丟例外」,壞設定的樹會走到 csharp-xunit 預設、沒有 `run_cmd`,結果是第 4 項整批判不過、回 1,而不是先決條件的 2,訊息也指向測試而非設定。
4. 連依賴資料夾:`_lint_link_deps(real_dir, snap_dir)` 簽名與常數 `_LINT_DEP_DIRS = ("node_modules", ".venv", "venv")` 跟快照寫的一致;需要自己把「平台根在樹裡的位置」對回「平台根在主工作目錄的位置」(相對路徑換底),快照沒寫換法。

## F7 殘骸清理:暫存資料夾是全機共用的,`git worktree remove` 沒有說在哪個 repo 下跑
severity: minor
blocking: 否
引句:「底下是工作樹的先 `git worktree remove --force` 再刪資料夾,最後 `git worktree prune`」
file: `scripts/lumos:23798`
file: `scripts/lumos:14202`

1. `_lint_new_clean_stale` 只掃 repo 底下的 `.lumos/lintbase-*`;新寫的要掃系統暫存資料夾,那裡會有別的專案、別的使用者(同機)用同前綴留下的過期資料夾。
2. `git worktree remove` 只在登記過那棵樹的 repo 看得到;對別的 repo 的殘骸會失敗,結果是資料夾被刪、那個 repo 的 `.git/worktrees/` 登記留著,等它自己下次 `prune` 才清。不致命,但快照要寫「失敗就只刪資料夾、不報錯」。
3. 並行會談:另一個會談正在跑的樹不到一天不會被清,沒有衝突。

## F8 時間:受波及合約測試遇到沒有 `{method}` 的平台會跑整套,單套上限 600 秒,超出手冊建議的「10 分鐘」
severity: minor
blocking: 否
引句:「手冊寫明 `fix-check` 要在背景跑或把指令逾時拉到 10 分鐘(一次約 5 分鐘」
file: `scripts/lumos:38353`
file: `scripts/lumos:38629`

1. 第 5 項用 `advisory=False` 的 `_bound_tests_check`;`_run_bound_tests` 對沒有 `{method}` 的平台不略過、整套跑,單套逾時 `_BOUND_TESTS_WHOLE_SUITE_TIMEOUT` = 600 秒(`scripts/lumos:38353`)。第 4 項不跑這種平台,但第 5 項會,單一次最壞已經等於 10 分鐘,加上建樹與第 4 項就超過。
2. 「一次約 5 分鐘」是本 repo 有 `{method}` 的量測,對沒有的專案不成立。手冊與 RETIRE-IF 的「中位數超過 10 分鐘」會被這類專案單獨拉爆。要不就在輸出裡先說「這個專案的合約測試要整套跑」,要不就把這種平台在第 5 項也當成不過並指路。

## 已讀、核對過、無 finding 的項目

- `_escape_reason_ok`:實際判法是 `isinstance(v, str) and len(v.strip()) >= _MANUAL_MIN_CHARS and bool(re.search(r"[^\W_]", v))`,`_MANUAL_MIN_CHARS = 4`(`scripts/lumos:8284`、`scripts/lumos:4472`),跟快照「去掉前後空白後至少 `_MANUAL_MIN_CHARS` 個字、要有實字」一致;非字串回 False,不會丟例外。`prior` 的「各至少十個字」是另寫的,不用它。
- 從 `_bound_tests_for_diff` 抽「測試名解析」:抽得出來。現有那段是「`resolve_test_refs` 丟 `ValueError` -> `(node, "?", 訊息前 60 字, "bad-name")`;白名單不過 -> `bad-name`;`methods_for` 命中(含 `Class.Method` 取最後一段)-> `real`;`hay_for` 命中 -> `fake`;否則 `dangling`」。共用函式傳入 `(合約文字, split, default, methods_for, hay_for)` 回 `(平台, 方法, 狀態)` 清單即可,`hay_for` 要保持惰性(只在非 real 才呼叫,它會掃整個平台根)。
  - 不要順手併進 `_classify_one`(`scripts/lumos:11962` 起):它沒有白名單、沒有 `Class.Method` 處理,語意不同,併了會動到 `guard list` 與 doctor Check T。
  - 抽之後要跟著跑的既有測試:`t_bound_tests_gate`、`t_bound_tests_shared_impact_payload`、`t_bound_tests_rejects_unfilterable_cmd`、`t_bound_tests_explains_no_pins`、`t_bound_tests_unproven_blocks_push`、`t_bound_tests_multiplatform_missing_cmd`、`t_bound_tests_no_config_message_not_doubled`、`t_skip_code_loop_never_skips_bound_tests`;沒有任何測試直接呼叫 `_bound_tests_for_diff`,介面變動的翻紅風險低。
  - fix-check 第 3 項「要恰好一支」:`[test:a,b]` 會被逗號切成兩支,`resolve_test_refs` 會回兩筆;單名包成 `[test:名]` 後數結果筆數即可。
- `_gate_event_or_warn(repo_root, gate, kind, note, **kw)` 回 `True`/`False`/`None` 與快照一致(`scripts/lumos:1234`);`head_sha`、`extra`、`hard` 都是 `_gate_event` 的具名參數。`_KNOWN_GATES` 要加 `"fix-check"`,不加會被擋並印警告(`scripts/lumos:1220`)。
- 治理帳讀端:`cmd_gov` 的 governance 載入 mapper 目前只在 canary/blocked 與 code-loop dispositions/recall-miss 吐 `token`,快照說「轉換沒吐 `token`、同一提交連跑兩次會被折成一筆」成立。本機帳實測 `head_sha` 全是字串(1785 筆)、`secs` 全是浮點(254 筆),補進 `_GOV_FIELD_TYPES`(`scripts/lumos:7577`)不會讓既有行被丟;`record_sha256`、`failed_items` 本機治理帳現無此鍵。
- 治理帳預篩 + `_drift_jsonl_parse`:該函式吃整份位元組、只在 `\n` 切行、壞行與非物件行略過(`scripts/lumos:29834`),預篩後用 `b"\n".join` 接起來可行。
- `loop next` 提醒:全部狀態都走同一個 `emit` 閉包(`scripts/lumos:11591`),JSON 與文字模式的 cap-hint 都在 `emit` 末段,提醒插在 `_cap_hint_lines` 之前可行。`escalate` 只在 light 出現、light 帶輪次會被擋(`scripts/lumos:11589` 前的一致性檢查)屬實。`disposal_cmd` 只在 `plant-canary` 且非 light、非 legacy 時建;`t_loop_next_disposal_cmd_actually_runs` 用 `.replace("<id串>", "F1", 1)` 只換第一處,新增 `<id串|none>` 不會被它誤換。
- `_codeloop_record_valid_ex(repo_root, rec_sha, marker_sha, timeout=None)` 回三元組 `(ok, 為什麼, 判不了)`,快照「判不了也當作無效」要取前兩個值判 `ok`;`governance/review-reports/`、`docs/.governance-log.jsonl`、`docs/.canary-log.jsonl` 都在簿記白名單(`scripts/lumos:22664`、`22681`),所以提交修正紀錄與帳本不會讓提醒復發,跟 S8 一致。
- `canary record --regression-set`:`cmd_canary` 現有「要跟 `--findings-set` 一起給」那串旗標判斷在 `scripts/lumos:8567`,`--refuted-set` 的「去空白、轉小寫比 none」寫法在 `scripts/lumos:8606` 起,快照要照的都在;`--finding-kind` 的「給了就要給全」寫法也對得上。
- 手冊與索引:`skills/lumos-project-notes/commands/INDEX.md` 現 4211 字元,上限 4500(`t_command_index_complete`),剩約 289 字,代碼審那一列(INDEX 第 36 行)加 `loop fix-check` 夠用;`t_command_index_complete` 要求「`loop fix-check`」字樣出現在 commands 子檔,放 06 即可;`HELP_WHEN` 要補 `"fix-check"` 或 `"loop fix-check"` 一條(`scripts/lumos:40722` 起那張表,`t_every_subcommand_has_when` 會釘)。
- 快照內交叉引用:`Systems/reversibility-governance-ledger`、`bound-tests-gate`、`guard-kill`、`規格閘`、`loop-convergence-recording`、`finding-refute`、`pitfalls-code-loop` 都存在;`Systems/代碼審修正關卡` 本來就是要新開;`Projects/代碼審修正關卡_計劃`、`Projects/漂移防治路線圖_計劃` 存在。
- 本 repo 自己的 `.lumos/config.json` 有進版控,`run_cmd` 是 `{python} scripts/test_lumos.py -k {method}`,吃自己的狗食時第 4 項可行。

最高等級:major,blocking 共 1 條
