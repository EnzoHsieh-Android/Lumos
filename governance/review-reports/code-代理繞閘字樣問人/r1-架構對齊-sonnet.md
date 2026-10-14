severity: minor

我只讀了 diff 和鄰居檔,沒有跑任何東西重現。報告裡的行號指 `/tmp/code-代理繞閘字樣問人-r1.patch` 的行,或 repo 內檔案的行(repo 是 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass`)。我的 Bash 被 lumos-guard 擋過一次(路徑含 claude),改加結尾斜線後可用。三問都沒有 major。

## 1. 分層與依賴方向

分層跟鄰居一致,沒有跨層直呼。

- 新掛鉤放在 `scripts/hooks/claude/`,跟 `impact-hook.py`、`dispatch-lens-hook.py` 同層。它只依賴 `_hookevent.guard` 與 `mark`,再加標準庫、`git` 子程序,沒有 `import` `scripts/lumos`。
- 註冊走 `merge-claude-settings.py` 既有路徑:`HOOK_BUDGET` 加 `"bypass-ask-hook.py": 5`,`HOOK_ENTRIES["PreToolUse"]` 加 `matcher: "Bash"`(patch 1060-1095 行)。
- Codex 側在 `_codex_entries` 用 `continue` 跳過 Bash matcher(1125-1126 行)。形狀跟旁邊 `Edit|Write|MultiEdit`、`Agent` 的 matcher 特例一樣。
- `scripts/lumos` 的四處名單(`_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES`、`enforcement_status` 列舉)都補了,跟既有掛鉤同一套(patch 964、987、1009、1031-1034 行)。
- 分類邏輯放在掛鉤內,是計劃 d1 已決的偏離,不重報。我查了先例:`impact-hook.py` 與 `memory-sweep.py` 確實是厚掛鉤,理由不假。

## 2. 命名與錯誤處理

**finding 1**
severity: minor
blocking: 否

`__main__` 收尾與 stdin 讀法跟四個鄰居不同。

- 鄰居的做法:`impact-hook.py:919-928`、`dispatch-lens-hook.py:546-555`、`ci-status-hook.py:244-256`、`memory-sweep.py:959` 都在 `__main__` 區塊內用 `import sys as _s, pathlib as _p`,再 `from _hookevent import guard as _guard`,最後 `sys.exit(_guard(名, __file__, main) ...)`。`main()` 無參數,自己在內部 `json.loads(sys.stdin.read())`,JSON 壞掉就 `return 0`(`impact-hook.py:769-773`)。
- 新檔的做法:
  - 模組頂層 `sys.path.insert` 加 `try: from _hookevent import guard as _guard, mark`,失敗時自定一個 `mark` 空殼(patch 256-263 行)。
  - 在 `__main__` 以 `sys.stdin.buffer.read().decode("utf-8","replace")` 先讀,預篩後用 `lambda: main(_raw)` 傳入,`main(raw: str)` 帶參數(patch 928-948 行)。
- 錯誤處理的差異:`main` 內是 `decide(json.loads(raw))`,JSON 壞掉靠 `guard(swallow=True)` 吞掉,不是鄰居那種就地 `return 0`。結果仍是放行,只是路徑不同。
- 計劃明文要求「讀一次、預篩在 guard 之外」,所以讀 stdin 的位置不同有理由。結構對,這是形狀不一致,故為 minor。
- 引句:「sys.exit(_guard("pretooluse-bypass-ask-hook", __file__, lambda: main(_raw), swallow=True))」

已對齊、不報的項目:

- 輸出 JSON 是 `{"hookSpecificOutput": {"hookEventName": "PreToolUse", ...}}` 加 `ensure_ascii=False`,與 `dispatch-lens-hook.py:285` 同形。
- 事件名 `pretooluse-bypass-ask-hook` 等於 `enforcement_status` 的列名,命名規則與 `pretooluse-impact-hook`、`pretooluse-dispatch-lens-hook` 一致。
- `--budget` 預算段是 `impact-hook.py` 的逐字複本(`_BUDGET_RATIO`、`_outer_budget`、`_inner_budget`)。

## 3. 第二種做法

我 grep 了 `_sh_quote`(`scripts/lumos:450`)、`_repo_path_unsafe`、`_path_special_chars`。新碼完全不用這三個:它不印給人照抄的指令,理由文字也不嵌入指令內容,所以沒有重造引號或路徑消毒。

**finding 2**
severity: minor
⚠
blocking: 否

新增了一套自寫的 shell 解析器,專案裡已有一套較弱的。

- 已有的一套:`check-graph-sync.py:431-442` 的 `_segment_command` 用 regex 切 `&&`、`||`、`;`、`|`,`_tokens_of` 用 `shlex.split`,但不追蹤引號。作者自己註明「Quote-aware 不嚴格」。
- 新增的一套:`_Quotes`、`_join_continuations`、`strip_heredocs`、`_replace_cmdsubs`、`_tokens`(`shlex` 加 `punctuation_chars`)、`_Walker`,共約 400 行(patch 377-547、791-889 行)。
- 為什麼不算 major:
  - 兩邊需求不同。新碼要追蹤引號、heredoc、`cd`、子殼層,舊的做不到。
  - 兩支掛鉤各自獨立安裝,新檔不能 `import` 檔名帶連字號的 `check-graph-sync.py`。
  - 舊函式只服務已無呼叫點的 `touched_graph_via_cli`。
- 缺口:計劃 d1 只裁了「邏輯放掛鉤內」,沒有交代為何不復用或為何要另寫切段器。判不準,標 ⚠ 交編排者。
- 引句:「lex = shlex.shlex(cmd, posix=True, punctuation_chars="();<>|&\n")」

**finding 3**
severity: minor
blocking: 否

暫存根名單另立一份,而且組法跟 Python 側既有的不同。

- 既有的 Python 做法:`scripts/lumos:18226` 與 `impact-hook.py:172,179` 都只用 `tempfile.gettempdir()`(前者再 `realpath`)。
- 新檔的做法:`_temp_roots()` 寫死六個路徑,只有 `os.environ.get("TMPDIR")` 為真才加 `tempfile.gettempdir()`(patch 131-135 行)。
- 這份名單與 `mods/claude/lumos-guard/hooks/register.ts` 的暫存根是另一種語言的另一份,計劃明寫「取聯集」,屬已知設計。
- 不一致處:Python 側沒有共用名單函式可呼叫,但「gettempdir 要不要無條件加」的條件不同。`TMPDIR` 未設時,`gettempdir()` 若落在名單外(Linux 自訂 `TMPDIR` 之外的情況很少見),新碼與 `scripts/lumos:18226` 的判定會不同。我給不出具體失敗場景,只標形狀不一致。
- 引句:「if os.environ.get("TMPDIR"):」

其他我查過、沒有第二種做法的地方:

- shlex 用法是 `scripts/lumos` 與 `check-graph-sync.py` 已有的標準庫用法,沒有新依賴。
- 子程序用 `subprocess.run(["git","-C",...], timeout=_inner_budget(...))`,與 `impact-hook.py` 的 subprocess 加預算逾時同做法。
- 註冊方式沒有另一種,就是 `HOOK_ENTRIES`。

## 固定席節點

- `lumos-cli-lifecycle` 的 re-inject INVARIANT:diff 只動安裝名單與 WHY 行,沒碰 sentinel 與 re-inject 邏輯,不影響。
- 其他 INVARIANT(`search` 預設排除、還原翻紅釘、設計審處置閘、`guard kill` 的 rc 優先序與 JSON 純度):diff 沒碰這些路徑,不影響。
- `test_lumos.py` 只把 `enforcement_status` 的列數 24 改成 25,與新增那一列同步。

不對齊共 3 條,其中 major 0 條。
