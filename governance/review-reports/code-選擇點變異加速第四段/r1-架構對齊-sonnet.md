severity: minor

整份 diff 的結構跟鄰居一致,沒有第二種加引號、寫暫存檔、解析輸出、排序或假工具的做法。我找到 3 條 minor,都是結構對、寫法跟鄰居有落差。

**1. 分層與依賴方向:對齊**
- 新函式都放在合併快篩那一帶,依賴方向跟鄰居一樣。呼叫鏈是 `cmd_guard_kill` → `_kill_merge_iter` → `_kill_merge_ready`/`_kill_merge_base`/`_kill_merge_screen` → `_choice_merge_*`。
  - 事件解析 `_choice_merge_events` 和 `_choice_merge_timeout_kind` 只被 `_choice_merge_classify` 與 `_kill_merge_screen` 呼叫,沒有往上直呼 `cmd_guard_kill`。
  - 新的 `_kill_merge_base_run` 是從 `_kill_merge_base` 抽出的一段(鄰居 `_kill_merge_halt_check` 也是這種小助手)。
  - 初始化腳本路徑先在 `_choice_merge_init_path` 只算不寫,寫檔在 `_choice_merge_init_write`,跟既有的「`_kill_merge_ready` 判斷、`_kill_merge_base` 動手」分工一致。
  - file: `scripts/lumos:29046`(`_kill_merge_ready` 的既有分工)
- `_isolated_worktree` 多一個 `scratch=parent` 欄位:這支共用助手另一個呼叫端 `scripts/lumos:23663`(fix-check)不受影響,因為只加欄位、沒改行為。`cmd_guard_kill` 用 `getattr(_iw, "scratch", None)` 取,跟同檔 `getattr(c, ...)` 的防禦寫法同調。

**2. 命名與錯誤處理:大致對齊,有 2 條 minor**
- 命名:`_CHOICE_MERGE_*`、`_choice_merge_*`、`_kill_merge_*` 前綴和鄰居一致。印字用 `print(f"⚠ {_kill_esc(c.plat)}:…", file=sys.stderr)`,跟 `_kill_merge_breaker` 那幾行一致。寫檔失敗只抓 `OSError`,印一行後降級照常合併,跟快篩「不確定就交回逐支」的慣例一致。

severity: minor
(blocking: 否)
斷路器的新分支靠比對原因字串 `why == _CHOICE_MERGE_HANG_WHY` 分流,不走 `_choice_merge_classify` 既有的第三個回傳值 `counts`。新增的連續 15 次門檻是模組常數 `_CHOICE_MERGE_HANG_BREAKER`,不像既有的 5 次能經 `_KillMerge(breaker=…)` 注入(`_KillMerge.__init__` 只有 `breaker` 和 `probe_every` 兩個參數)。
引句:「elif why == _CHOICE_MERGE_HANG_WHY:   # 另外數,不動 streak;到 _CHOICE_MERGE_HANG_BREAKER 照跳開的寫法跳開」
file: `scripts/lumos:28963`(`_KillMerge.__init__`,既有 `breaker` 是注入參數)

severity: minor
(blocking: 否)
這個分支把「跳開」那 5 行(設 `mg.plats`、`mg.trips`、`mg.cool`、印 ⚠)整段複製一份,同一支函式裡出現兩份。結構同做法,只是重複,沒有抽共用。
引句:「mg.plats[plat], mg.tripped = (False, _CHOICE_MERGE_TRIPPED), True」
file: `scripts/lumos:29230`(既有那份跳開寫法,`elif counts:` 分支內)

**3. 第二種做法:沒有引入,只有 1 條 minor**
- 加引號:`_choice_merge_cmd` 內 `_sp.list2cmdline([str(init)]) if _IS_WIN else _shlex.quote(str(init))` 跟 `_run_cmd_expand` 的 `{python}`、`{method}` 是同一套,不是另一套。但這是同一行寫法的第三份複製,沒有走同一支呼叫。Windows 特殊字元也沿用既有 `_WIN_CMD_SPECIAL`(`scripts/lumos:6507`)。
- 暫存檔:放在 `_isolated_worktree` 的上層暫存資料夾(隨工作樹收尾刪、keep 時一起留),沒另開 `tempfile`,也沒有第二套清理。
- 解析外部工具輸出:`_CHOICE_MERGE_EVENT_RE` 是模組級 `re.compile` 常數,寫法同 `_CHOICE_MERGE_SYSKILL_RE`、`_KILL_COMPILE_RE`。測試名身分沿用 `_choice_merge_fullname`/`_choice_merge_hits`,沒另寫比對。
- 排序:`_kill_merge_failed_first` 擴充成前、中、後三層。仍在同一支函式裡用列表推導加 `sorted(..., key=)`,沒有引入新的排序機制。
- 測試假工具:擴充既有的 `_CKM_GRADLE`,新旗標 `__events__`、`__init_reject__` 沿用 `__merge__`、`__msleep__` 的行為字典做法。呼叫既有的 `_ckm_repo`、`_ckm_run_many`、`_ckm_ready_ctx`、`_ck_cleanup`,暫存目錄前綴沿用 `gctl-ckm-`。

severity: minor
(blocking: 否)
引句:「extra = "" if not init else " --init-script " + (_sp.list2cmdline([str(init)]) if _IS_WIN else _shlex.quote(str(init)))」
file: `scripts/lumos:28081`(`_run_cmd_expand` 內同一套寫法的原件;最近的單參數包裝是 `_sh_quote`,在 `scripts/lumos:468`,但只有 shlex 沒有 Windows 分支,所以不能直接換)

不對齊共 3 條,其中 major 0 條
