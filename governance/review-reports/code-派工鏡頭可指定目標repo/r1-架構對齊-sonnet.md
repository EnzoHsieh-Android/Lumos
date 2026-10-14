severity: major

不對齊 5 條。5 條裡 1 條需修:載入掛鉤檔的第二種做法。

我讀了 patch 全文,對照 `lens-repo` 的既有寫法。沒有逐條跑行為,所以下面都是靜態比對。

**已對齊的部分**
- `_lens_git` 加 `env`:是在既有包裝上加選填參數,沒有另起 git 呼叫包裝。
- 暫存 index:`mkdtemp` 加 `rmtree`,跟 `scripts/lumos:24076` 的 `lumos-bookkeeping-backup-` 同做法。
- 子命令註冊:`HELP_WHEN`、`add_parser`、`main` 分支三處都補了,跟 `enforcement`、`python-path` 同組。
- 讀計劃的共用函式:`_dispatch_lens_read_spec` 與 `_spec_commit_blob` 是唯一入口,沒有留第二份讀法。

severity: major
blocking: 是 — 為「載入別人的檔」又開了第二套做法,而且漏掉既有做法裡專為「不在 repo 留 `.pyc`」加的處理
引句:「mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(」
對照:`scripts/lumos: ` + "`scripts/lumos:52339`" + `(_handoff_load_hook:用 spec_from_file_location 載入掛鉤檔,載入前後設 sys.dont_write_bytecode,並明寫「唯讀指令不該在 repo 裡留 __pycache__」)`
判定理由:`_spec_freeze_hook_lumos` 用 `SourceFileLoader` 手工組載入,沒設 `dont_write_bytecode`。`scripts/hooks/claude/__pycache__` 會被寫進 repo,既有註解點名過這個坑。它也沒有 `_handoff_load_hook` 的「缺函式就回原因」檢查,例外清單也比它窄。同一支檔裡載入掛鉤檔應該只有一種做法,建議把 `_handoff_load_hook` 一般化成「給路徑與必備函式名」再共用。

severity: minor
blocking: 否 — 只是又多一份同形狀的原子寫入,沒有新的語意風險
引句:「def _spec_freeze_write(outp, data):」
對照:`scripts/lumos: ` + "`scripts/lumos:20598`" + `(_write_lf:暫存名帶 pid 與 uuid、O_EXCL、os.replace)`
判定理由:暫存名與 `O_EXCL` 寫法逐字抄自 `_write_lf`,而 `_write_lf` 只收 str。快照要位元組相同,所以需要 bytes 版,這個理由成立。但原子寫入現在又多一份,而且少了 `_write_lf` 的失敗清理 `BaseException` 分支。可以把 `_write_lf` 拆出 bytes 核心共用,也可以接受現狀。

severity: minor
blocking: 否 — 同檔兩種記事件寫法,行為沒有分歧
引句:「def _mark_event(kind, note) -> None:」
對照:`scripts/hooks/claude/dispatch-lens-hook.py: ` + "`dispatch-lens-hook.py:519`、`:532`、`:555`" + `(仍是內嵌的 from _hookevent import mark as _mark,捕捉 Exception)`
判定理由:新 helper 只收斂了 `_fail_note` 與計劃版說明兩處,背景未啟動、鎖失敗、逾時三處仍是舊的內嵌寫法。helper 的 except 也改成列舉型別。同一支掛鉤裡出現兩種寫法,建議一併收斂,或註明刻意不動。

severity: minor
blocking: 否 — 多一份要同步的代碼清單,但掛鉤端另有查表兜底
引句:「_SPEC_FAIL_CODES = (」
對照:`scripts/lumos: ` + "`_LENS_FAIL_CODES`" + `(新增,有 t_dispatch_lens_fail_codes_match_hook 守 LENS_FAIL_REASONS 的鍵)`
判定理由:掛鉤端現在有 `LENS_FAIL_REASONS` 與 `_SPEC_FAIL_CODES` 兩份代碼清單,只有前者有守衛對照 lumos 端。後者是前者的子集,漂移時不會翻紅。建議用「`LENS_FAIL_REASONS` 的鍵減去範圍代碼」推導,或讓守衛也涵蓋它。

severity: minor
blocking: 否 — 屬於另一個命令的失敗字彙,但沒有登記表,慣例不一致
引句:「def fail(code, msg):」
對照:`scripts/lumos: ` + "`_dispatch_lens_fail`" + `(新增的 code not in _LENS_FAIL_CODES 就 raise ValueError,沒登記的代碼印不出去)`
判定理由:`cmd_spec_freeze` 自己用 `freeze_fail` 鍵,放另一個鍵合理。但 `not_git`、`no_head`、`spec_outside_repo`、`spec_missing`、`spec_too_large`、`out_conflict`、`git_failed` 七個代碼只散在區域函式的字串裡。`dispatch-lens` 那邊已有「代碼先登記」的守衛,這裡沒有。建議補一個 `_SPEC_FREEZE_FAIL_CODES` 常數加同形守衛。

不對齊 5 條,其中 1 條需修。
