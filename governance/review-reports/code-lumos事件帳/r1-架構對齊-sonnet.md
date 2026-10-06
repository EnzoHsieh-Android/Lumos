severity: major

**1. 分層與依賴方向:有一處不對齊(F1),其餘對齊。**
- 讀取端(`_events_*`、`cmd_events`)放在 `enforcement_status` 之前,`cmd_events` 在 `main()` 的 `enforcement` 分派之前分派,位置與鄰居一致。`enforcement_status` 新增的 ⑪ 層只查資料夾時間、不呼叫外部指令,跟既有各層「各自 try 包住」的寫法一致。
- 外掛同步 `_sync_claude_plugin` 掛在 `_sync_global_hooks` 裡。`_sync_global_hooks` 本來就在函式內自己 print Codex 審查席訊息,所以對齊。對照 file: `scripts/lumos:18609`、`scripts/lumos:18637`。
- `_events_repo_root` 是第二支解析 repo 根的函式,見 F1。
- `_testmap_git` 是 testmap 的包裝,被借去讀事件帳,見 F2。
- 拆除放在 `cmd_uninstall` 而不是 `_teardown_global_hooks`,見 F4。

**2. 命名與錯誤處理:大致對齊,有三處小差異(F2、F3、F4)。**
- 三段式訊息(擋下、為什麼在意、指令獨立一行)、回 2 代表擋下、`--json` 開關,都跟 `cmd_ci_status` 與 `cmd_handoff` 同款。對照 file: `scripts/lumos:31485`、`scripts/lumos:36787`。
- 狀態字串 `ok/absent/no-source/failed` 與 `_sync_msg` 的三態字串同一路。
- 例外只接 `(RuntimeError, ValueError, OSError, TimeoutExpired)`,比 `enforcement_status` 的 `except Exception` 更嚴。
- 不對齊處:刪檔錯誤處理(F3)、拆除的位置與回報(F4)。

**3. 第二種做法:有一處(F1),其餘沒有。**
- 外部 `claude` 呼叫:新的 `_claude_json` 與 `_claude_do` 用 `subprocess.run(... timeout=30)`,跟鄰居行內的 `subprocess.run(..., timeout=10)` 同一種寫法(file: `scripts/lumos:20642`)。專案沒有共用的外部指令包裝,所以不算第二種。
- JSON 解析、`_py_which`、`_lumos_src` 都沿用既有函式。
- 測試的假 `claude` 是新寫的 Python 假執行檔,用 FAKE_CLAUDE_STATE 存狀態。鄰居的假 `gh` 是 shell 腳本(file: `scripts/test_lumos.py:25331`)。這個要記錄每次呼叫和狀態,需求不同,我判不算第二種。
- `_with_env` 是新的環境變數還原 helper,見 F5。

### F1 新增 `_events_repo_root`,跟既有的 `_anchor_repo_root` 重複,而且壞 `--repo` 沒有擋下
severity: major
blocking: 是 — 鄰居已有同功能的 repo 根解析函式,卻另寫一套,行為還不同(多了 git 呼叫、少了擋下)。
引句:「base = Path(repo) if repo else Path.cwd()」
`_anchor_repo_root`(file: `scripts/lumos:19272`)在給了 `--repo` 但不是目錄時印「擋下」並回 None。`cmd_enforcement` 也對不是目錄的 `--repo` 回 2(file: `scripts/lumos:20828`)。新函式對不存在的 `--repo` 靜默往下走,最後印「沒有事件帳」並回 0,打錯的路徑會被誤讀成「沒有事件帳」。

### F2 事件帳借用 testmap 的 git 包裝,其他功能的 git 呼叫用 `_lens_git`
severity: minor
blocking: 否 — 結構對,只是借用了命名屬於別的功能的 helper。
引句:「r = _testmap_git(root, ["rev-parse", "--path-format=absolute", "--git-common-dir"], timeout=3)」
`_testmap_git`(file: `scripts/lumos:30821`)原本只被 testmap 自己的九處呼叫(`scripts/lumos:30928` 到 `31112`)。testmap 以外要拿 repo 根的地方是 `_lens_git(".", "rev-parse", "--show-toplevel")`(file: `scripts/lumos:24813`、`scripts/lumos:25610`)。`_events_root` 與 `_events_repo_root` 是第一批跨功能借用 `_testmap_git` 的。

### F3 `--prune` 的刪檔沒有錯誤處理,而且把刪檔放進標為唯讀的指令
severity: minor
blocking: 否 — 結構沒問題,是錯誤處理比鄰居少。
引句:「shutil.rmtree(d)」
`_note_audit_work_dir` 的清理包在 `try/except OSError`(file: `scripts/lumos:26258`)。其餘 `rmtree` 多數帶 `ignore_errors=True`(`scripts/lumos:16994`、`17003`、`13166`)。新的 `_events_prune` 沒處理,碰到權限錯誤會中途丟例外,留下刪一半的結果。另外 `HELP_WHEN` 與 `cmd_events` docstring 都寫「唯讀」,但 `--prune` 會刪檔。鄰居的唯讀指令(`cmd_ci_status`、`cmd_handoff`)沒有帶破壞性旗標的先例。docstring 有註明例外,所以只算輕微。

### F4 外掛拆除放在 `cmd_uninstall`,不在 `_teardown_global_hooks`,成功時也不進 `removed` 清單
severity: minor
blocking: 否 — 結構能跑,位置與回報跟既有拆除路徑不一致。
引句:「_teardown_claude_plugin()                # teardown 第三步也經過這裡」
全域 hook 的拆除集中在 `_teardown_global_hooks`(file: `scripts/lumos:18890`)。`cmd_uninstall` 用 `removed` 列表回報自己刪了什麼(file: `scripts/lumos:16972`)。新增的拆除既不進 `removed`,成功時也完全不印訊息,只在失敗時印。另外 `_sync_global_hooks` 在 merge-failed 與 ok 兩條路徑各呼叫一次 `_sync_claude_plugin`,是重複分支,鄰居不這樣寫。

### F5 測試新增 `_with_env` 環境還原 helper,鄰居是行內 try/finally 寫法
severity: minor
blocking: 否 — 只是還原寫法多了一種,行為正確。
引句:「def _with_env(env, fn, drop=("LUMOS_SKIP_CLAUDE_PLUGIN",)):」
既有測試是行內 `old = dict(os.environ)` 加 `try/finally` 還原(file: `scripts/test_lumos.py:895` 到 `912`,另有 `scripts/test_lumos.py:51800` 到 `51913`)。`t_enforcement_ledger_row` 自己也用行內的 PATH 還原,同一份 diff 裡就有兩套。

不對齊共 5 條,其中 major 1 條
