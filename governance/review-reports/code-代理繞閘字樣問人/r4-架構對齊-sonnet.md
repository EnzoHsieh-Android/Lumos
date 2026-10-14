severity: minor

**已驗範圍。** 我讀了 code patch 全文，對照 `impact-hook.py` 整檔、`_hookevent.py` 全檔，以及 `scripts/lumos` 的 `_write_lf`（:20597）、`_home_cache_write`（:47696）、`_codeloop_write_dispositions`（:50534）。三支掛鉤（`bypass-ask-hook.py`、`impact-hook.py`、`ci-status-hook.py`）的逾時預算區塊，我用 `sed -n '/^_BUDGET_RATIO/,/逾時預算結束/p'` 取出後做 md5，三份一致。`dispatch-lens-hook.py` 沒有逐條對照，只確認它同樣呼叫 `_inner_budget`。
未驗：`memory-sweep.py` 沒有讀；`scripts/merge-claude-settings.py:126` 註冊表的 5 秒預算也只看了登記行。

## 三問

**1. 分層與依賴方向：對齊。**
- 新掛鉤只依賴同層的 `_hookevent`（掛鉤頂端 `from _hookevent import guard as _guard, mark`），不呼叫 `scripts/lumos`，也沒有互相引用其他掛鉤。依賴方向跟 `impact-hook.py:922-928` 一樣只往共用模組。
- 預算區塊逐字複製。`bypass-ask-hook.py` 的 `_BUDGET_RATIO` 到「逾時預算結束」那段，md5 與 `impact-hook.py:343-397` 相同。
- 預算天花板仍由註冊表 `HOOK_BUDGET` 一處生成（`scripts/merge-claude-settings.py:126`，`"bypass-ask-hook.py": 5`）。
- 「共用模組在模組頂層載入」已列在已知偏離，不重報。

**2. 命名與錯誤處理：結構對，有兩處不一致，都是 minor。**
- `_GIT_STATE` 是模組全域 dict，跟 `_hookevent.py:155` 的 `_MARKED` 同一種寫法，算有先例。`_IN_HOOK = {"on": False}` 則是第三種狀態寫法（`_BUDGET_START` 用 `global`），不過也沒有更好的先例可比，不算偏離。
- `_FD_MARK` 用 U+E0FF，落在 `_MASK_BASE` 的 U+E000 起 16 碼遮罩區之外。這是新增常數，沒有可比對的既有寫法，我只確認它與遮罩區不重疊。
- `_scope_cd`、`_note_markers`、`_dir_change` 都是 `_Walker` 的私有方法，這類一詞一職的拆法在掛鉤層沒有先例可比。
- `_hookevent._trim` 用 `mkstemp` 再 `copymode`，`except BaseException` 時刪暫存檔再 raise。清理的形狀等同 `_write_lf`（:20608-20618）；用 `mkstemp` 的做法等同 `_codeloop_write_dispositions` 與 `_home_cache_write`。`_write_lf` 不用 `mkstemp` 的理由是「新建檔權限受 umask 影響」，這裡原檔一定存在而且會 `copymode`，理由不適用，所以不算不對齊。
- 每次記事件都清殘檔（`_clear_stale_trims`）：`scripts/lumos` 的三支寫入函式都不掃殘檔，但 `impact-hook.py:175` 的 `_ttl_lazy_cleanup` 有同型的惰性清理，所以有先例。

**3. 第二種做法：沒有 major。**
- 預算只有一套（上述逐字複本）。
- 前處理只有一套 `_Normalizer`：`prefilter` 與 `bypass_reasons` 都走同一個類別（跑兩次，沒有第二份實作）。
- 分類器只有一個入口 `bypass_reasons`。

## 不對齊清單

1. **修剪失敗的警告缺 `telemetry-write-failed` 關鍵字。**
severity: minor
blocking: 否
引句:「print(f"  ⚠ hook 事件檔修剪失敗({type(e).__name__}),檔案會繼續長大:{f}", file=__import__("sys").stderr)」
   - 同檔 `guard` 的兩處和 `scripts/lumos` 的記帳失敗警告，都以 `⚠ telemetry-write-failed:` 開頭。
   - file: `scripts/hooks/claude/_hookevent.py:192` 與 `scripts/hooks/claude/_hookevent.py:205`
   - file: `scripts/lumos:1628`、`scripts/lumos:1674`、`scripts/lumos:1691`
   - 計劃 `Projects/enforcement可觀測性_計劃` 的 S7 也要求「記帳失敗要在 stderr 講 `telemetry-write-failed`」。
   - 影響：照關鍵字找記帳失敗的人，找不到這一種。
   - 修法：訊息改成 `⚠ telemetry-write-failed:hook 事件檔修剪失敗(…)`。

2. **`_temp_roots` 的 docstring 引用了不存在的先例。**
severity: minor
blocking: 否
引句:「"""暫存根:與審查席外掛的暫存根取聯集,再加上本機的暫存目錄(同 scripts/lumos 的做法,一律加)。"""」
   - `git grep` 在 `scripts/lumos` 找不到 `/private/tmp`、`/var/tmp`、`/var/folders`，只有 `tempfile.gettempdir()` 單獨使用。
   - file: `scripts/lumos:18226` 只有 `Path(os.path.realpath(tempfile.gettempdir()))`，沒有暫存根清單。
   - 影響：維護者會去 `scripts/lumos` 找一份不存在的暫存根清單來對照，或以為兩邊要同步。
   - ⚠ 該清單可能在 repo 外的審查席外掛（`lumos-guard`），我不能在審查席的 Bash 裡確認。
   - 修法：指到實際出處，或刪掉這句宣稱。

3. **`prefilter` 與 `_literal` 重複同一段字面判斷。**
severity: minor
blocking: 否
引句:「return "git" in low and re.search(r"\bcommit\b", low) is not None and _PRE_SHORT_N.search(low) is not None」
   - `prefilter` 與 `_literal` 兩處都有 `re.sub(r"['\"\\]","",…).lower()`、`_PRE_WORDS` 檢查，以及「`commit` + `_PRE_SHORT_N`」檢查。
   - 同一個判斷出現兩份，兩處日後可能走樣。
   - 這不算第二種做法（共用同一組常數），只是可抽成一個小函式。

4. **`bypass_reasons` 直接重設 `_BUDGET_START`。**
severity: minor
blocking: 否
引句:「_BUDGET_START = None         # 不是掛鉤進場(例如拿事件帳批次重跑):每次判斷重新起算預算」
   - 它用 `global _BUDGET_START` 改逐字複本區塊裡的變數，其他掛鉤都只透過 `_inner_budget()` 使用這個變數。
   - file: `scripts/hooks/claude/impact-hook.py:343-397` 是複本區塊，變數只由 `_inner_budget` 讀寫。
   - 這不是跨層呼叫，結構上仍是同檔內。
   - 但如果日後同步更新複本區塊，這個外部依賴容易被漏掉。

不對齊共 4 條，其中 major 0 條。

**暫存清理：** 我沒有建立任何暫存目錄或實驗檔，不需要刪除。
