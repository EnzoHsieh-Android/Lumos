severity: minor

**問 1　分層與依賴方向:對齊**
- 新碼全放在 `impact-hook.py` 內,是 hook 層的私有函式,沒有跨層直呼。
- 新碼呼叫的是同檔既有的 `_frame_injected`、`_sibling_worktree_root`、`_find_lumos_script`,以及共用模組 `_hookevent`(經 `_mark_event` 延遲 import)。這跟 `dispatch-lens-hook.py:341-350` 的做法相同。
- `main()` 拆成 `_query_files`、`_emit_chunks`,`_impact_for_file` 拆成 `_ttl_min`、`_run_impact`、`_ranked_ctx`。呼叫方向都是由上往下,沒有反向。
- `__main__` 仍走 `_guard("pretooluse-impact-hook", …)`,跟 `dispatch-lens-hook.py` 末段一致。

**問 2　命名與錯誤處理:大致對齊,有一處不一致(A2)**
- 固定字彙原因表 `IMPACT_FAIL_REASONS` 對照 `dispatch-lens-hook.py:59` 的 `LENS_FAIL_REASONS`,做法一致:只帶整數結束碼,不轉 lumos 的錯誤原文。
- `_mark_event` 逐字照抄 `dispatch-lens-hook.py:341-350`,包括刻意寬接 `Exception`。
- 事件 kind 的用法與鄰居相同:逾時記 `timeout`,其餘記 `error`。
- 例外處理維持 fail-open,沿用鄰居的 `except OSError`、`SubprocessError` 寫法。
- 不一致處只有 A2。

**問 3　第二種做法:有兩處,都判 minor**
- 圖譜判斷 `_has_graph`,見 A1。
- 「同會談只講一次」的記號寫法,見 A3。
- `_mark_event` 與 `_frame_injected` 的複本沒有算進 finding。hook 彼此 import 不到,「複製加守衛」是這個 repo 明文的慣例,見 `dispatch-lens-hook.py:404-407` 的註解。新碼有 `t_impact_hook_graph_check_agrees` 逐佈局對照 lumos,守衛比鄰居更完整。

### A1　hook 層又多一份「是不是圖譜專案」的判斷,而且規則跟同目錄其他 hook 不同
severity: minor
blocking: no
引句:「★規則是 lumos `_vault_in` 的複本★(hook import 不到 lumos)」
file: `scripts/hooks/claude/check-graph-sync.py:88-99`

- **對照:** 同目錄已有三份同類判斷:
  - `check-graph-sync.py:88-99` 的 `find_graph_root`,規則是 `docs/*-knowledge` 加 `docs/knowledge`。
  - `ci-status-hook.py:73` 只用 glob `*-knowledge`。
  - `lumos-entry-hook.py:46` 與 `lumos-entry-hook.py:367` 也只用 glob `*-knowledge`。
- **不一致:** 新的 `_has_graph` 多了「standalone vault root(`MOC/` 加 `Verification` 或 `Systems`)」這一條。同一個 repo 會被 `impact-hook` 判成圖譜專案,卻被 `check-graph-sync`、`ci-status-hook`、`lumos-entry-hook` 判成不是。
- **理由站得住:** 新規則才是照 lumos 本體 `_vault_in`(`scripts/lumos:33909-33925`)寫的。
- **⚠ 交編排者:** 這是否算「第二種做法」,取決於 hook 之間的判斷本來就容許不同。若要統一,應該是整批 hook 一起對齊 lumos,不是只改這一支。

### A2　失敗說明沒用鄰居已有的「框內一句加框外指示」寫法
severity: minor
blocking: no
引句:「notes.append(_frame_injected(FAIL_NOTE.format(why=why)) + "\n" + FAIL_TAIL)」
file: `scripts/hooks/claude/dispatch-lens-hook.py:307-309`

- **對照:** 鄰居把這個形狀抽成 `_framed_note(note, tail)`,所有說明行都走它(`dispatch-lens-hook.py:366`、`dispatch-lens-hook.py:380`、`dispatch-lens-hook.py:615-617`)。
- **不一致:** `impact-hook.py` 內聯寫 `_frame_injected(...) + "\n" + tail`,沒有同名輔助函式。
- 結構正確,只是命名和寫法跟派工鏡頭 hook 不同。

### A3　「同會談只講一次」的記號檔寫法,跟 hook 層另一套不同
severity: minor
blocking: no
引句:「marker.touch(exist_ok=False)   # 原子的「不存在才建」,已存在丟 FileExistsError」
file: `scripts/hooks/claude/check-graph-sync.py:902-927`

- **對照:** `check-graph-sync.py` 的 `_stop_mark_path`、`_stop_mark_write` 這一套有三個特點:
  - 路徑先過 `re.sub(r"[^A-Za-z0-9_.-]", "_", …)` 消毒,空字串、`.`、`..` 回 None。
  - 目錄先過 `_stop_dir_ok` 檢查。
  - 用 `os.open(O_CREAT|O_EXCL, 0o600)` 建檔。
- **不一致:** 新的 `_voice_once` 沒有消毒,`session_id` 直接拼進 `lumos-impact-{session_id}`;也沒有目錄安全檢查,用的是 `Path.touch`。
- **⚠ 交編排者:** 新碼放在 `impact-hook.py` 自己既有的暫存目錄 `lumos-impact-*`,同檔的 `_ttl_marker_path`(`impact-hook.py:172-174`)也沒有消毒。所以這是「跟本檔一致、跟 `check-graph-sync` 不一致」。同一 repo 內的記號檔寫法本來就分兩套,不是這份 diff 新開的。

不對齊共 3 條,其中 major 0 條
