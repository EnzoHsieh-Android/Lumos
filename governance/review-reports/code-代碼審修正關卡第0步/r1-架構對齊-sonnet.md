severity: major

# 架構對齊審(架構對齊-sonnet,第 1 輪)

對照基準:凍結 patch 對應的提交 0cd29fe6 工作樹(`scripts/lumos`、`scripts/test_lumos.py`)。佐證行的行號都是那份樹的行號。

## 三問總答

1. 分層與依賴方向:對齊,沒有跨層直呼。`cmd_loop_fix_check` 放在 `cmd_loop_next` 上方、`_fix_*` 小函式放在它上面,命名前綴同 `_kill_*`、`_lint_new_*`;`_IsolatedWorktree`、`_classify_test_refs`、`_spec_gate_judge_items` 是被呼叫的底層、guard kill / 推送前閘 / 規格閘往下用它,方向沒反。呼叫 `_lint_link_deps`(lint 私有函式)與 `_bound_tests_check` 是同檔跨功能呼叫,本檔常態(`_ns_git` 直接用 `_lens_git`),不算跨層。argparse 的 `fc_*` dest 前綴、`main()` 派發、`HELP_WHEN` 補條目、`_KNOWN_GATES` 加閘名、`cmd_gov` 讀端用「帶 gate 條件的欄位」都照既有做法(例:`pairs` 欄位)。
2. 命名與錯誤處理:rc 0/1/2 與「擋下:」前綴、stderr 輸出、`_gate_event_or_warn` 落帳,都跟鄰居一樣。不一致處見 F4、F6。
3. 第二種做法:有,見 F1(git 小工具自創一套)。其餘重複是 minor(F2、F3、F5)。

## F1 修正關卡自創兩支 git 小工具,鄰居已有同功能的
severity: major
blocking: 是
引句:「return [x.decode("utf-8", "surrogateescape") for x in r.stdout.split(b"\0") if x]」
佐證行:file: `scripts/lumos:11671`(新 `_fix_git_z`)對照 file: `scripts/lumos:25502`(`_nodehome_git`:跑 git、位元組回、失敗回 None)與 file: `scripts/lumos:25515`(`_nodehome_split_z`:`os.fsdecode` 切 NUL);file: `scripts/lumos:11660`(新 `_fix_rev`)對照 file: `scripts/lumos:37991`(`_lens_full_sha`:`rev-parse --verify -q <rev>^{commit}` 加 40 碼正規式檢查)
1. `_fix_git_z` = 「`git -C` 跑指令、`returncode != 0` 回 None、輸出按 NUL 切、解碼成字串清單」,跟 `_nodehome_git` + `_nodehome_split_z` 逐步等價;本檔另有 `_ns_git`、`_lens_git` 同一族,全都是 `_lens_git` 底座的薄包裝。這份 diff 沒走 `_lens_git` 族,另造第四套。
2. `_fix_rev` 跟 `_lens_full_sha` 做同一件事(rev → 40 碼 sha 或空)。差異只有 `--end-of-options`(防 `-x` 被當旗標)這一個。該差異是真需求,但正確做法是把旗標加進既有 `_lens_full_sha`(或讓 `_fix_rev` 呼叫它、前面先擋 `-` 開頭),不是複製一支。
3. 兩支新函式沒有逾時(`_lens_git` 預設 20 秒逾時、`TimeoutExpired` 回 None);這是「第二種做法」連帶的行為差異,不是另外一條。
4. 影響:日後有人改 `_lens_git` 的逾時/編碼,修正關卡不會跟著走。

## F2 兩處自己算檔案 sha256,既有 `_sha256_file`
severity: minor
blocking: 否
引句:「rsha = hashlib.sha256(rpath.read_bytes()).hexdigest()」
佐證行:file: `scripts/lumos:8432`(`_sha256_file`,註明 OSError 交呼叫端兜);新碼出現在 file: `scripts/lumos:11900` 與 file: `scripts/lumos:11964`
1. 同一行等價於 `_sha256_file(rpath)`,新碼兩處都內嵌,還額外在函式裡 `import hashlib`。結構沒壞、行為一樣,所以 minor。

## F3 `_disposal_tpl` 重算一份 `--round`/`--tier` 旗標邏輯
severity: minor
blocking: 否
引句:「_rm = "" if (light or eff_tier == "legacy" or seq) else f" --round r{n_next}"」
佐證行:file: `scripts/lumos:12237`(`_disposal_tpl` 內);同一邏輯原本在 file: `scripts/lumos:12266`(`rmode`)、file: `scripts/lumos:12279`(`_tier_flag`)與 `_qid`、`_orch_flag` 一帶,`record_cmd` 還在用那份
1. 為了讓 gate-pending 也能在 `rmode` 算出來之前給範本,把旗標組裝在 `_disposal_tpl` 裡又寫一遍(`_rm`、`_tf`、`shlex.quote`),`record_cmd` 仍走舊的一份。同一個函式裡兩份旗標組裝,日後改規則(例:legacy 的 --tier 處理)會只改到一邊。把 `rmode/_qid/_tier_flag/_orch_flag` 上移到 `_disposal_tpl` 之前共用即可。結構上不算新做法,minor。

## F4 ⚠ 檔內第一個 `__enter__/__exit__` 類別;既有 with 區塊先例是 `@contextlib.contextmanager` 函式
severity: minor
blocking: 否
引句:「class _IsolatedWorktree:」
佐證行:file: `scripts/lumos:16898`(`_vault_write_lock`,內部 `@contextlib.contextmanager def _cm()`,檔內唯一另一個 with 區塊先例);file: `scripts/lumos:14621`(新類別的 `__enter__`,檔內 grep `__enter__` 只此一處);檔內其他類別(file: `scripts/lumos:26919` `_DriftNames`、file: `scripts/lumos:26943` `_DriftProbeTree`、file: `scripts/lumos:23613` `_NodehomeSide`)都是資料/快取容器,不是 with 區塊
1. 派工詞問「鄰居有沒有類似的類別先例」:有類別先例(上面三個),但沒有「做成 context manager 的類別」先例;with 區塊的先例是 contextmanager 函式。
2. 為什麼只標 minor 並交編排者:新類別要同時暴露 `ok`、`err`、`path` 三個狀態給呼叫端,類別比 contextmanager 函式 yield 一個物件更直白,是合理的結構選擇,不是平行造輪子。判不準算不算「第二種做法」,故標 ⚠。若編排者認定「with 區塊一律 contextmanager」才要升級。

## F5 ⚠ 第二支「清過期暫存殘骸」函式,且通用工具依賴 lint 專用常數
severity: minor
blocking: 否
引句:「def _isolated_worktree_sweep(repo, prefix):」
佐證行:file: `scripts/lumos:14656`(新 sweeper)、file: `scripts/lumos:14667`(用 `_LINT_NEW_STALE_SEC`)對照 file: `scripts/lumos:24485`(`_lint_new_clean_stale`:`.lumos/lintbase-*`、mtime 超過 `_LINT_NEW_STALE_SEC` 就 rmtree)、常數定義 file: `scripts/lumos:24052`
1. 新 sweeper 掃的是系統暫存資料夾、還要先 `worktree remove`,跟 lint 那支(掃 `.lumos/` 下純資料夾)不同,所以不能直接共用;docstring 也寫明「規則借 `_lint_new_clean_stale`」。但「mtime 過一天就清」的判斷仍是第二份。
2. 通用共用類別 `_IsolatedWorktree`(放在 `_kill_run` 旁、guard kill 層)反過來讀 lint 區的常數 `_LINT_NEW_STALE_SEC`,依賴方向是「通用 → 專用」。常數名帶 `LINT_NEW`,日後 lint 閘撤掉或改值,修正關卡殘骸清理會被連帶改動。
3. 判不準要不要為此再抽共用判斷,標 ⚠ minor。

## F6 設定讀取的錯誤處理比 `_lint_new_config` 少一層警告
severity: minor
blocking: 否
引句:「raw = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}」
佐證行:file: `scripts/lumos:24194`(`_lint_new_config`:讀不了時 `cfg["warnings"].append(".lumos/config.json 讀不了…")` 再回預設);新碼 file: `scripts/lumos:11592`(`_fix_check_config`:同樣的 `except` 直接 `return cfg`、不留警告)
1. 新函式 docstring 自稱「同 `_lint_new_config` 的寫法」,單欄位不合法有警告,但整份檔讀不了時靜默回預設,跟被模仿的鄰居不同。實際影響低(`cmd_loop_fix_check` 後面會另外讀樹裡的設定並在讀不懂時 rc2),所以只是 minor。

## 未列(核對過、對齊)
- 測試夾具:`_fc_git` 與 `_kr_git` 字面相同(file: `scripts/test_lumos.py:60729`、file: `scripts/test_lumos.py:62137`),但本檔測試夾具本來就是一個功能族一份(`_nh_git` file: `scripts/test_lumos.py:43339`),不算。`t_canary_regression_set` 用 `_stats_fixture` 與 `run`、`t_isolated_worktree_shared` 用 `_mk_kill_env`/`_kgk_run`/`_kr_git`,都是既有夾具。
- 治理帳事件讀取 `_fix_check_events` 自己逐行讀 `docs/.governance-log.jsonl`:檔內同類讀法本來就各寫各的(file: `scripts/lumos:24688`、file: `scripts/lumos:10647`、file: `scripts/lumos:40330`),且它有走既有的 `_drift_jsonl_parse`,不算。
- 落帳走 `_gate_event_or_warn`、閘名進 `_KNOWN_GATES`、欄位型別進 `_GOV_FIELD_TYPES`,三者都照既有做法。

不對齊共 6 條,其中 major 1 條。

最高等級:major,blocking 共 1 條
