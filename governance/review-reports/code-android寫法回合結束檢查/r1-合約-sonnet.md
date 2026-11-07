severity: major

審查範圍是 r1-snapshot-丙.patch。複本 `git clone --shared` 到臨時目錄,每次翻紅前清 `__pycache__`。共改壞 25 處:翻紅 14 處、仍綠 9 處,另有 2 處是無害變體。作者說的 39 處 38 處翻紅,我沒法逐處核,下面只講我抽查到的。

F1 可信來源漂移守衛放寬後,擋不住「換成 PATH 找 lumos」
引句:「shared = (name != "_hookshared.py" and ("from _hookshared import" in txt or "import _hookshared" in txt) and "_trusted_lumos" in txt」
- 放寬後只要求兩件事:檔案裡出現 `import _hookshared`,以及 `_trusted_lumos` 這個字串出現在任何位置(註解也算)。
- 原本要求每支 hook 自己有 `def _trusted_lumos():` 整段,而且逐字比對。
- 翻紅實驗:
  - 改的行:`scripts/hooks/claude/stop-lint-hook.py` 的 `lumos = sh._trusted_lumos()`。
  - 改成:`lumos = __import__("shutil").which("lumos")  # _trusted_lumos`
  - 指令:`python3.14 scripts/test_lumos.py -k hooks_never_run_code`
  - 結果:21 passed, 0 failed,沒紅。
- 失敗場景:新 hook 或日後改動用 PATH 的 `which("lumos")` 找 lumos,再加一句註解帶著這個名字,守衛照綠。
- 放寬前,這種寫法因為缺函式定義會紅。
- 後面第 ③ 條只擋「從專案資料夾組 lumos 路徑」,擋不到 `which`。
- 修法:改成要求 hook 的程式碼行(去掉註解)真的呼叫或匯入 `_trusted_lumos`,或 AST 驗。
severity: major
blocking: 是

F2 `--worktree` 的「超過 50 支」上限值沒被測試釘住
引句:「_lwt_put(root, f"app/M{i}.kt", f"package app\nfun m{i}() = {i}\n", since + 5)」
- 測試只造 51 支。其他案例最多 3 支,S2 是單檔 25 條告警。
- 翻紅實驗:
  - 改的行:`scripts/lumos` 的 `_LINT_WT_MAX_FILES = 50` 改成 `= 5`。
  - 指令:`python3.14 scripts/test_lumos.py -k lint_new_worktree`
  - 結果:95 passed, 0 failed,沒紅。
- 失敗場景:閾值被誤調到 4 到 50 之間任何值,測試都不會紅。
- 錯了會讓一回合改 5 支以上就整次 rc3,收工檢查靜默不跑。推送前閘還在,所以降為 minor。
- 同一類:邊界「剛好 50 支仍要檢查」沒有案例。
severity: minor
blocking: 否

F3 rebase / cherry-pick / revert 進行中的狀態只測了兩種
引句:「(root / ".git" / "rebase-merge").mkdir()」
- S1⑪只造了 `MERGE_HEAD` 與 `rebase-merge`。
- 翻紅實驗:
  - 改的行:`_LINT_WT_GIT_STATES` 刪掉 `rebase-apply`、`REBASE_HEAD`,以及 `CHERRY_PICK_HEAD`、`REVERT_HEAD` 兩項。
  - 結果:95 passed, 0 failed,沒紅。
- 失敗場景:`git am` 或 `git rebase --apply` 進行中的工作樹,會被當成完整版本檢查。
severity: minor
blocking: 否

F4 S13「預算從指令一開始起算」的斷言恆真
引句:「check("S13 預算從指令一開始起算(不是從判定函式開始)", d_left is not None and d_left <= 7 - 0 and t_call > 0, str(d_left))」
- `t_call > 0` 恆真,`d_left <= 7` 幾乎恆真。
- 翻紅實驗:
  - 改的行:`scripts/lumos` 的 `deadline = t0 + (float(budget)` 改成 `deadline = _time.monotonic() + (float(budget)`,也就是不從指令一開始起算。
  - 指令:`-k lint_new_budget_flag`
  - 結果:10 passed, 0 failed,沒紅。
- 要驗就得讓指令前段(`_anchor_repo_root` 等)慢下來,再斷言 `d_left` 明顯小於 7。
- 目前實際差距只有毫秒,降為 minor。
severity: minor
blocking: 否

F5 收工鉤子「退出碼必須是 1」這一件沒被測試釘住
引句:「if rc != 1 or not isinstance(data, dict) or data.get("status") != "blocked" or not data.get("new"):」
- 翻紅實驗:
  - 改的行:`stop-lint-hook.py` 的 `if rc != 1 or not isinstance` 改成 `if not isinstance`。
  - 指令:`-k stop_lint_hook`
  - 結果:55 passed, 0 failed,沒紅。
- 測試案例有 rc1 加 traceback、rc1 加 warn、rc1 加空 new、rc3,沒有「rc 非 1(例如被訊號殺掉的 -15 或 0)但最後一行是 blocked JSON」。
- 條款與筆記都寫「三件事都成立才擋」。
severity: minor
blocking: 否

F6 `.kts` 目標的行為條款、計劃與測試三方不一致
引句:「for rel, label in (("app/src/test/kotlin/ScreenTest.kt", "測試檔"), ("app/Screen.java", "不是 kt")):」
- S9 條款寫「不是 kt/kts 應不推」。計劃範圍 3.1 說鉤子對 `.kt`/`.kts` 都送 `delta_new`。
- 實際:`_stack_key_for_file("app/build.gradle.kts")` 回 None,`_impact_decision_rows` 以 `!= "kt"` 擋掉,`.kts` 永遠不推。鉤子對 `.kts` 白送一份 `delta_new`。
- 測試只用 `.java` 當非 kt,沒有 `.kts` 案例,無論哪種解讀都沒釘。
- 需要編排者裁定 `.kts` 要推或不推,再補案例。
severity: minor
blocking: 否

F7 `t_handoff_hook_import_is_pure` 的放寬範圍比理由大,docstring 沒跟著改
引句:「if not (under_std(os.path.realpath(p)) or os.path.realpath(p) == os.path.dirname(hook)):」
- 兄弟檔守衛還在:
  - 在 `check-graph-sync.py` 頂層加 `import _hookevent`,守衛紅,報 `open` 讀 `_hookevent.py`。
  - 對應指令:`-k handoff_hook_import_is_pure`。
- 但「列 hook 自己的目錄」的放行是無條件的:
  - 在 `check-graph-sync.py` 頂層加 `os.listdir(os.path.dirname(os.path.abspath(__file__)))`,守衛仍綠(4 passed, 0 failed)。
  - 這個放行對不匯入共用模組的 hook 也成立,但原因只對匯入共用模組的那一支成立。
- 守衛 docstring 仍寫「listdir/scandir 只准標準庫」、「翻紅釘:…listdir…」,與放寬後行為不符。
- 這是目錄清單的資訊洩漏,不是寫入或執行,所以標 minor。
- 這一項請編排者裁(筆記裡寫了交編排者裁)。
severity: minor
blocking: 否

各支重點分支改壞後仍翻紅的有:
- 回合編號比對。
- 第三批後不再擋的上限。
- 寫不出 stdout 要退名額。
- `LUMOS_STOP_BLOCK_OFF` 變數。
- 擋停時 lint-new 與工具群組都被收掉。
- `new` 為空不擋。
- `.git/index` 位元組不變(要把 `--no-optional-locks` 與 `GIT_OPTIONAL_LOCKS` 兩層同時拿掉才紅)。
- 修改時間篩選。
- SIGTERM 空窗保護(拿掉 `pthread_sigmask` 紅)。
- 工作樹模式保底 1 秒。
- 停用列過濾。
- 伺服端排除(`kt-compose`)。
- Kotlin 剝字串。
- 兄弟檔匯入守衛。

另有幾處改壞後仍綠,但失敗場景給不出具體後果,所以不列 finding:
- 同名唯一刪除檔的基準判斷。
- `AA`/`DD` 衝突碼。
- `--budget` 傳給 lint-new 的實際值。
- 擋停訊息本文的消毒(規則包訊息現在沒有 `$` 變數,不會夾帶換行或反引號)。

有一處我改壞的點等於沒改,不算數:我換掉的那行本來就跟原碼相同。

清理:複本目錄已用字面絕對路徑刪除,沒有程序開著。`/var/folders/.../T/gctl-run-*` 底下有很多目錄,我分不出哪些是這場會談留下的,沒有動。

總結:最嚴重是 F1(守衛放寬後擋不住「換成 PATH 找 lumos」),會擋 1 條。
