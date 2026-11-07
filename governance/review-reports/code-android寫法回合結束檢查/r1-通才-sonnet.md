severity: major

我只讀 patch、`scripts/lumos` 與 `impact-hook.py`,沒有用 Bash 實跑 `_safe_path`。F1、F2 是照程式碼推算,沒有輸入→實際→預期的實跑結果。

F1
severity: major
blocking: 是
標題:擋停理由裡的「放行指令」會被 `_safe_path` 截成 160 字,照抄會執行殘缺指令。
引句:「return s.replace("`", "'")[:160]   # r2 delta #2:反引號會跳出 code span,換成單引號」
引句:「lines.append(f"    放行:{sp(c.get('waive_cmd'))}")」
失敗情境:`_reason` 對 `waive_cmd` 也用 `sp`(即 `_safe_path`),字串上限 160 字。`_lint_waive_cmd` 組出的指令格式是 `lumos lint-waive <key> --rule <規則> --file <路徑> --note "<為什麼放行>"`。key、規則名與 Android 的長路徑(例如 `app/src/main/java/com/example/feature/home/HomeViewModel.kt`)加起來很容易超過 160 字。
結果是 `--file` 路徑或 `--note "<為什麼放行>"` 被截斷。模型拿到的是殘缺指令:要嘛引號不成對而報錯,要嘛放行帳記到錯誤或空白的檔名。這條指令的用途是「誤報就照它放行(會留紀錄)」,所以放行紀錄會被弄壞。
佐證:`scripts/lumos:40526` 的 `_lint_waive_cmd` 組出的指令沒有任何長度上限。
修法:`waive_cmd` 只做控制字元消毒、不截長度,或單獨給較大的上限;不要共用檔名那個 160。

F2
severity: minor
blocking: 否
標題:整段理由硬截 1500 字,「最多 10 條」與「另 N 條」的提示實際上常被截掉。
引句:「return out if len(out) <= 1500 else out[:1490] + "…"」
失敗情境:每條告警佔兩行(訊息一行、放行指令一行),每條約 250 字。10 條約 2500 字,截到 1490 字時只剩約 5 條。最後的 `(另 N 條,跑 lumos lint-new --worktree --all 看全部)` 在最尾端,最先被截掉。
截斷點可能落在某條的放行指令中間,模型不知道還有被省略的告警。同一個函式的註解卻寫「最多 10 條」。
修法:先限制條數,以 1500 字為準逐條累加;放不下就停,並保證結尾提示行一定留得下。

F3
severity: minor
blocking: 否
標題:決策列的「已推過」標記在挑選當下就寫下,工具呼叫被拒或失敗時這一列再也不會推。
引句:「if isinstance(r, dict) and r.get("id") and _voice_once(session_id, "row-" + re.sub(r"[^A-Za-z0-9-]", "_", str(r["id"]))[:16]):」
失敗情境:`_rows_to_voice` 在 PreToolUse 階段呼叫 `_voice_once`,它用 `touch(exist_ok=False)` 立刻寫下「已講過」。如果這次編輯後來被使用者拒絕、或 old_string 對不上而失敗,模型其實沒有照決策列寫程式,同會談之後再碰同一列也不會再提醒。
docstring 寫的「沒印出的列下次還能推」只涵蓋沒挑到的列,不涵蓋挑到但沒被用上的列。
修法:要嘛接受並在註解寫明,要嘛改成輸出寫成功後才落標記。

F4
severity: minor
blocking: 否
標題:Popen 與登記 `_STATE` 之間有時間縫,此時收到 SIGTERM 會留下孤兒 lint-new。
引句:「prev = signal.signal(signal.SIGTERM, _on_sigterm)」
引句:「_STATE["proc"], _STATE["pgid_file"] = proc, pgf」
失敗情境:處理器先裝,但 `_STATE["proc"]` 要等 Popen 回傳後才設。這段空窗內 Claude Code 送來的逾時 SIGTERM,會讓 `_on_sigterm` 看到 `proc is None`,`_kill_all` 直接回 False,接著 `os._exit(0)`。
已經用 `start_new_session=True` 啟動的 lint-new 以及它開的工具群組沒人收,會繼續跑到自己的預算用完。窗口很小,但這支鉤子的設計目標正是「逾時要收乾淨」。
修法:先設 `_STATE["pgid_file"]`,並把 Popen 到登記之間用 `signal.pthread_sigmask` 擋住 SIGTERM。

F5
severity: minor
blocking: 否
標題:`stop-lint-hook.py` 裡有一個沒人呼叫的 `_inner_budget` 包裝函式。
引句:「def _inner_budget(elapsed=None, default=30.0):」
失敗情境:`_on_stop` 與記帳那段全都直接呼叫 `sh._inner_budget(...)`,這個包裝函式沒有呼叫端,是死碼。它還在共用模組不在時回 1.0,看起來像兜底,實際不會被走到,日後維護的人會誤以為有這層兜底。
修法:刪掉,或讓 `_on_stop` 真的改呼叫它。

F6
severity: minor
blocking: 否
標題:改 .kt 檔時,同一份編輯內容被取兩次、送兩份。
引句:「pl["delta_new"], new_trunc = extract_delta_text(payload, new_only=True)」
失敗情境:`extract_delta_text` 每次都會 join、UTF-8 編碼並可能截到 2 MB。改 `.kt` 時先算整份(`delta_text`),再算只含新內容的 `delta_new`,而 `delta_text` 已經包含 `delta_new`。大型 Write 或 MultiEdit 因此多一次編碼,stdin JSON 也多帶最多 2 MB 傳給 lumos,在逐次編輯的熱路徑上。
修法:一次取出各段後分別組成兩個字串,或讓 lumos 端自己從已送的內容切出新內容。

總結:最嚴重是擋停理由中的放行指令會被截成殘缺指令(F1),會擋 1 條。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/_hookshared.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/stop-lint-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/impact-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/lumos`
