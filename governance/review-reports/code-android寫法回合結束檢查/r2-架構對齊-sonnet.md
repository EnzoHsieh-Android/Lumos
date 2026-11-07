severity: major

先講結論:第一輪 F1–F8 全部照方向修了,沒有退回。這輪新增 1 條會擋的(`_lint_wt_argv` 另寫了一份佔位符展開),另有 4 條結構對、細節沒對齊的小項。

## 第一輪 F1–F8 核對

- **F1**(可信來源、逾時預算)已修。
  - 兩段回到逐字複本,`stop-lint-hook.py` 與 `check-graph-sync.py` 各自帶一份。
  - `_hookshared.py` 的頭註已改成「不放這裡」並說明原因。
  - 守衛補上「用到預算的鉤子自己要有複本」「共用模組不准有」(`scripts/test_lumos.py:29297` 一帶)。
  - 可信來源那條逐字比對的守衛(`scripts/test_lumos.py:29076`)沒放寬,仍是單一版本才過。
  - 共用模組 `_hookshared.py` 的註解與實況一致,沒有再自相矛盾。
- **F2** 已修。
  - `_mark_name`、`_claim_mark` 搬進 `_hookshared.py`,`check-graph-sync.py` 的 `_stop_mark_path`、`_printed_mark_path`、`_stop_mark_write` 與 `stop-lint-hook.py` 的 `_claim` 都改走它。
  - 這是功能類,符合圖譜 `Systems/hook信任邊界.md:80-83` 的分流。
  - 兩道安裝守衛不用另加:`check-graph-sync.py` 原本就匯入共用模組,`stop-lint-hook.py` 這輪沒新增匯入。
- **F3** 已修。`_lens_git` 加了 `data=`,`_lint_wt_git` 只剩薄包裝;`--no-optional-locks` 換成環境變數 `GIT_OPTIONAL_LOCKS=0`,等價。
- **F4** 已修。說明字樣、`_LINT_NEW_CLI_RC` 上方註解都改了。
- **F5** 已修。`_KT_SIT_QID`(`scripts/lumos:38277`)取代寫死的題號。
- **F6** 已修。`_kt_decision_rows` 改走 `_kt_sit_rows_rx`(`scripts/lumos:39143`)加字集合預篩。
- **F7** 實質接受。鉤子側收群組仍是複本,但 `_killpg` 已有平台判斷。細節見下面 ① 的 F4。
- **F8** 已修。`_lint_new_out` 抽成一份,兩個模式共用。

## ① 模組邊界

「收程序群組不抽共用」站得住。圖譜 `Systems/hook信任邊界.md:83` 的判準是漏帶的後果:這段漏收只會留下殘留程序,不會讓安全檢查失效。這屬於功能類,複本或共用模組兩條路都允許。選複本,與 `scripts/hooks/claude/memory-sweep.py:930` 的 `_kill_tree` 並列,沒有跨層呼叫。

「鉤子不用訊號遮罩、主程式用」也站得住。理由是被擋的遮罩會被子程序繼承,而鉤子的子程序 lint-new 必須收得到 SIGTERM,才能刪快照、收工具。主程式側的工具一律 SIGKILL,所以遮罩無害。兩種做法各有明確的層與原因,不算第二種做法。

唯一不齊的是「平台沒有程序群組」的判法寫了三種:

- 鉤子 `_killpg` 用 `hasattr(os, "killpg")`。
- `memory-sweep.py:930` 用 `os.name == "posix"`。
- 主程式 `_kill_proc_group`(`scripts/lumos:26861`)用 `except AttributeError`。

F4
引句:「不用 pthread_sigmask 擋訊號:被擋的遮罩會被子程序繼承,」
引句:「送不到(群組已不在等)也回 False。收群組是功能類(漏收是殘留程序,不是安全檢查失效),」
- 這個判斷站得住,但 `_killpg` 的註解寫「跟記憶清掃那支的 _kill_tree 一樣用平台判斷」,實際判法不同。
- 對照:`scripts/hooks/claude/memory-sweep.py:930`、`scripts/lumos:26861`。
- 屬命名與判法的小差異,結構沒問題。
severity: minor
blocking: 否

## ② 命名與錯誤處理

命名都順著既有前綴:

- `_lint_wt_*`、`_lint_waive_part`、`_lint_new_out` 沿用該區現有命名。
- 鉤子側的 `_killpg`、`_turn_start`、`_unchecked_kind` 命名也一致。

退出碼與擋下格式沿用原樣。`_hookevent` 的記事件合約也接上了:逾時記 timeout、失敗記 error,同 `dispatch-lens-hook.py:341`。

有兩處細節不一致。

F2
引句:「if e.errno == errno.E2BIG and fail_info is not None:」
- `_lint_spawn_argv` 把所有 `OSError` 都吞成 `None`。
- 它的孿生 `_lint_spawn`(`scripts/lumos:41071` 起)只接 E2BIG,其餘「照舊往外丟」。
- 同一個函式的兩個分支,對開程序失敗的處理方式不同,註解卻說「同一個結果」。
- 另外 `open(out_path, "wb")` 失敗也在同一個 `except` 底下,會被當成「工具沒裝」。
- 對照:`scripts/lumos:41071`。
severity: minor
blocking: 否

F3
引句:「記不到不影響本業;★寬接 Exception 是刻意的★(同派工鏡頭 hook 的同名函式)。」
引句:「if _HERE not in sys.path:」
- `stop-lint-hook.py` 的 `_mark_event` 是第三份複本,而且不是逐字的。
  - 另兩份(`dispatch-lens-hook.py:341`、`impact-hook.py:844`)無條件 `sys.path.insert`。
  - 這份多了 `if _HERE not in sys.path`,並用 `_HERE`。
- 註解卻說「同派工鏡頭 hook 的同名函式」。
- 現有守衛 `t_dispatch_lens_hook_mark_event_one_way`(`scripts/test_lumos.py:57415`)只盯派工鏡頭那支。
- 這是功能類複本,選複本沒問題,但複本之間已經開始漂,卻沒有守衛盯。
severity: minor
blocking: 否

## ③ 第二種做法

`shell=False` 讓工作樹模式與 `--diff` 模式成為兩套執行方式。這個分岔站得住:

- 工作樹模式跑的是白名單重組過的命令,可以安全拆成參數清單。
- `--diff` 模式跑的是專案自己宣告的命令,仍需要 shell 語意。

收斂的部分:

- `_lint_new_out` 讓兩個模式共用一份骨架。
- `_lens_git` 加 `data=` 取代第三個 git 包裝。
- 決策列比對改走 `_kt_sit_rows_rx`。
- `_mark_name`、`_claim_mark` 搬進共用模組。

另起一套的部分是佔位符展開。`_lint_cmd_with_files` 的註解寫明自己是「★唯一實作★」,原因是它曾在三個地方各寫一次、漏了一處而出事。`_lint_wt_argv` 是同一件事的第二份實作。

F1
引句:「def _lint_wt_argv(cmd, files, cmd_dir=None):」
引句:「out.append(",".join(_os.path.relpath(str(f), str(cmd_dir)) if cmd_dir and _os.path.isabs(str(f)) else str(f) for f in files))」
- 逗號串的相對路徑改寫,與 `_lint_cmd_with_files`(`scripts/lumos:41345`,相對路徑那行在 41366)是同一條規則的逐字重寫。
- 兩份展開之間沒有等價守衛。
- 難以收進同一個函式的只有輸出形狀(字串對參數清單),相對路徑的算法可以抽成一份共用。
- ⚠ 是否算 major 交編排者:反方理由是 shell 版回字串、這裡要回清單,不能直接重用。我標 major,因為宣告過「唯一實作」的地方又多了一份。
severity: major
blocking: 是

F5
引句:「wcfg = dict(cfg, per_cmd_floor_sec=_LINT_NEW_WORKTREE_FLOOR_SEC, wt_argv=True)」
引句:「return _lint_spawn_argv(injected_cmd, repo_root, fail_info, out_path)」
- 同一個「用不用 shell」的開關,在四層用了三種不同寫法傳遞:
  - cfg 的 `wt_argv` 鍵。
  - `_lint_new_run_one` 的 `argv_mode`。
  - `_lint_run_and_parse` 的 `argv=`。
  - `_lint_spawn` 靠 `isinstance(…, list)` 判型別。
- `_lint_spawn_argv` 另外複製了一份 `pthread_sigmask` 的前後擋放區塊。
- 結構沒有跨層直呼,但同一個決定被表達成三種形狀。
- 對照:`scripts/lumos:41071`、`scripts/lumos:42142`。
severity: minor
blocking: 否

不對齊共 5 條,其中會擋的 1 條
