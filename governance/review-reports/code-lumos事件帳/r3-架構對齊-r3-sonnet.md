severity: clean

我只審了 r3 的 diff 與 `scripts/lumos` 的對照鄰居,沒有實跑任何指令。

**1. 分層與依賴方向:對齊。**
- `cmd_events` 先呼叫 `_anchor_repo_root`(`scripts/lumos:22406`)取 repo 根,再用 `_events_root`(`scripts/lumos:23529` 一帶)取主 checkout。`_events_root` 走 `_lens_git`(`scripts/lumos:41871`),不自己呼叫 subprocess,方向與 r2 驗收的一致。
- `_events_main_trusted`(`scripts/lumos:23640`)、`_events_path_safe`、`_events_prune` 都是純函式,由 `cmd_events` 在刪除前串起來。沒有跨層直呼。
- 專案內沒有既有的 worktree 登記驗證函式。grep `worktrees` 與 `git-common-dir` 只命中新碼本身,以及 `scripts/lumos:45675` 的註解(講工作樹命名,與驗證無關)。
- ⚠ 同一份 diff 內 `_events_root` 用 `git rev-parse --git-common-dir`,`_events_main_trusted` 直接讀 `.git/worktrees/*/gitdir`,是兩種取法。兩者目的不同(取主根 與 驗證登記),我判不算第二種做法。

**2. 命名與錯誤處理:對齊。**
- `cmd_events` 的「擋下」三處現在都印到 `file=sys.stderr`,與 `cmd_ci_status`、`cmd_handoff`、`_anchor_repo_root` 一致。
- 擋下訊息維持「擋下 → 為什麼在意 → 指令獨立一行」三段式。
- 例外元組 `(RuntimeError, ValueError, OSError, subprocess.TimeoutExpired)` 在 `_ledger_wait` 與 `_sync_claude_plugin` 一致。
- `_ledger_wait` 在函式內寫 `import time as _t`,與檔內 `scripts/lumos:17928`、`30721` 等多處的 `_t` 寫法一致。

**3. 第二種做法:沒有。**
- `_events_main_trusted`:無同功能鄰居,見第 1 問。
- `_ledger_wait`:鄰居的重試等待(`_kill_after_write` 在 `scripts/lumos:15655`、vault 鎖在 `scripts/lumos:17928`)都是各自內嵌的 sleep 迴圈,沒有共用 helper 可呼叫。新函式是通用的「重查 N 次」,不重複任何既有函式。
- `_safe_iterdir`:只有一個呼叫點,鄰居的 `iterdir()` 都是裸呼叫(例如 `scripts/lumos:20484`、`21069`),沒有同功能的 helper。
- `_EVENTS_DAYS_RE`:寫法 `re.compile(r"[0-9]{1,5}")` 與 `_COUNT_NUM_RE`(`scripts/lumos:34063`)同一種「只認 ASCII 數字並限長」做法,而且直接用 `re.compile`。
- `_events_clean` 已改成疊在 `_esc_clean`(`scripts/lumos:10873`)與 `_PATH_SPECIAL_CATS`(`scripts/lumos:31741`)上,不再另寫第四套。

### 前輪修復驗收(r2 本鏡頭)
- F1 `_events_clean` 另寫第四套清理:已修好。現在呼叫 `_esc_clean(text, 2000)`,再用 `_PATH_SPECIAL_CATS` 補 Cf、Zl、Zp、Cs。
- F2 「擋下」印到 stdout:已修好。`--days`、路徑不可信、找不到會談三處都改成 stderr。
- F3 `__import__("re")` 編譯正規式:已修好。現在是 `re.compile`。

不對齊共 0 條,其中 major 0 條
