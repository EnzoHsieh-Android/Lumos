severity: minor

## 問 1:分層與依賴方向
大致對齊。
- `cmd_guard_kill` 新增 `prep`,並在平台組建好隔離工作樹之後呼叫 `prep.run(mctx)`。形狀、`mctx` 的建法和 `merge` 一致。對照:`scripts/lumos:28512`(mctx 建構)、`scripts/lumos:29010`(`_KillMerge`)。
- 量基準抽成共用的 `_kill_measure_singles`,`_kill_merge_singles` 改成薄包裝。這是同層合併,沒有另寫量基準迴圈。對照:`scripts/lumos:29150` 一帶。
- 新碼沒有跨層直呼,依賴方向和鄰居一樣。
- 不一致只有兩處,放在問 2 的 F3、F4。

## 問 2:命名與錯誤處理
大致對齊,有五處小差異。
- 帳欄位與 kind:`reach` 和 `reach-run` 走 `_choice_gate_event`,和 `run` 一致(`scripts/lumos:80096`)。
- 帳欄位的登記:欄位型別進了 `_GOV_FIELD_TYPES`,`LOOP_NOT_CLOSE_EVENTS` 也補了(`scripts/lumos:18490`)。
- 衝突檢查:`_choice_reach_only_clash` 用 `_situation_rule_say` 回 rc 2,和鄰居同一套。
- 不一致的五處見下面各條。

severity: minor
blocking: 否
引句:「init = os.path.join(c.scratch, _CHOICE_COV_INIT_NAME) if c.scratch else None」
F1,初始化腳本路徑:`_CovBase.start` 自己算路徑、自己寫檔。
- 鄰居有 `_choice_merge_init_path` 的 Windows 路徑特殊字元防護(`scripts/lumos:29094-29100`),新碼沒有。
- 失敗處理也不同。鄰居是寫不進去就把 `sh["init"]` 設成 None,合併照走(`scripts/lumos:29103-29112`)。新碼是整個覆蓋功能退成「覆蓋接不起來」。
- 腳本內容不同,所以另開常數合理。只是路徑與寫入沒走同一個 helper,跟 `_choice_merge_init_write` 不同形。

severity: minor
blocking: 否
引句:「wd, _why = _note_audit_work_dir(rr)」
F2,續跑快取資料夾:`_choice_cov_dir` 把原因丟掉,拿不到資料夾就靜默回 None。
- 另外兩個呼叫端有看 `why`(`scripts/lumos:56848`、`scripts/lumos:58467`)。鄰居 `_choice_merge_init_write` 失敗會印 ⚠ 到 stderr。
- 快取放在 `note-audit` 名下,並用 `shutil.rmtree` 照「最近兩個 at_sha」清。這和該資料夾「14 天清 `*.md`」的規矩不同,是另一套清理規則。
- 計劃有寫「擴充 `_note_audit_work_dir`」,結構上算沿用,所以只列 minor。⚠ 請編排者看這個位置與命名能不能接受。

severity: minor
blocking: 否
引句:「class _CovBase:」
F3,類別放哪裡與取名:
- 取名:既有類別都用 `_Kill*` 或 `_Choice*` 前綴(`_KillMerge`、`_KillHooks`、`_ChoiceKillRun`),`_CovBase` 沒有。`_jacoco_block`、`_jacoco_varint`、`_JACOCO_MAGIC` 也自成一個前綴,其餘新碼用 `_choice_cov_*`。
- 放置:`_KillPrep` 的職責是「給 `cmd_guard_kill` 的選用參數,形狀同 `_KillMerge`」。`_KillMerge` 和 `_KillHooks` 放在 `scripts/lumos:28728` 到 `29010` 的 kill 段。`_KillPrep` 卻放在約 79xxx 的 choice 段,和 `_ChoiceKillRun` 同區。

severity: minor
blocking: 否
引句:「def _choice_reach_cur(rr, at_sha, guard, new_sha_of):」
F4,`cov_sha` 讀端與寫端各算一次:
- 寫端是 `_choice_kill_cov` 內的 `cov_sha_of`,讀端是這支 `_choice_reach_cur`。兩邊都做「`_choice_tests_sha` 加 `_choice_tree_oids` 再 `_choice_cov_sha`」。
- 錯誤處理不同。寫端經 `_choice_kill_blobs`,會帶期限、印「守的測試雜湊標成不明」的提醒(`scripts/lumos:79058` 一帶)。讀端直接呼叫 `_choice_test_blobs`,沒有期限、`_ok` 丟掉、不提醒。
- 兩邊重複,日後可能不同步。

severity: minor
blocking: 否
引句:「max_mutants=None, max_seconds=_CHOICE_MAX_SECONDS」
F5,設定預設值:`--max-mutants` 的 argparse 預設與 `cmd_choice_kill` 簽名預設從常數 `_CHOICE_MAX_MUTANTS` 改成 None 哨兵,函式內再補預設,為了判斷「有沒有給」好做 `--reach-only` 衝突檢查。
- 同組的 `--max-seconds` 仍用常數預設,help 也還寫「預設 30」。這是 argparse 預設的做法,和鄰居不一致。

severity: minor
blocking: 否
引句:「for proc in list(_KILL_RUN_LIVE.values()):」
F6,訊號處理:`_KillPrep.on_signal` 逐字重寫了 `_KillMerge.on_signal`(`scripts/lumos:29038-29044`)。
- 機制是同一套(`_lumos_merge` 標記加 `_kill_run(merge=…)`),不算第二種做法。
- 但 `_kill_run` 文件仍寫「merge 給 choice-kill 的 _KillMerge」(`scripts/lumos:28228`)。`_KillPrep` 現在靠鴨子型別(只需要 `.interrupted`)借這條路,文件沒更新。

## 問 3:第二種做法
沒有 major 等級的第二種做法。
- 量基準:共用 `_kill_measure_singles`,用 `wrap` 和 `after` 掛鉤,沒有另一套迴圈。
- 工作目錄:沿用 `_note_audit_safe_dir` 與 `_note_audit_work_dir`(見 F2)。
- 讀帳:`_choice_ledger_aux` 是另掃一遍 `evs`,只收 `reach`;`_choice_ledger_index` 仍只收 `choice-kill`。兩邊各管各的,算對齊。
- 訊號:同一套標記機制(見 F6)。
- init 腳本:同一機制,只是路徑與寫入沒共用 helper(見 F1)。
- ⚠ 判不準,請編排者看:同一份 JaCoCo exec 檔有兩條讀法。
  - Python 端的 `_choice_cov_exec_classes` 自己解二進位,供斷路器數類別數。
  - Gradle 端的 `_CHOICE_COV_ANALYZE` 用 JaCoCo API 做逐行命中分析。
  - 專案裡原本沒有 exec 讀取,所以不是「另一套」。但同一個格式有兩套讀法,屬於新碼內部的重複,我不計入下面的數。

不對齊共 6 條,其中 major 0 條。
