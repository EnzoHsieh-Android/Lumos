severity: major

我的工作目錄是 `/Users/enzo/harness/lumos-green-scope`,HEAD 是 409ab14fe,也就是被審的那版。下面的行號都是這版的 `scripts/lumos` 與 `scripts/test_lumos.py`。

整體結論:結構大致對齊鄰居,有一處多了第二種淺複製判法,另有一處測試寫法跟鄰居不同。

**1. 分層與依賴方向:對齊**

- `_redbase_on_branch`、`_redbase_branch_name` 放在 `_redbase_branch_rows` 旁邊。它們只呼叫 `_lens_git_dl`、`_lens_git`、`_LENS_SHA_RE`、`_gov_ledger_ignored`、`_gate_event` 這些既有共用層函式。`_redbase_branch_rows` 本來就呼叫 `_lens_git` 與 `_lens_fork_point`(`scripts/lumos:14386-14389`),方向沒變,沒有跨層直呼。
- `_gate_event` 的 `ref=` 參數寫分支名,跟端到端驗收傳 `ref=marker_branch` 同一用法(`scripts/lumos:70676-70677`)。欄位寫入點在 `_gate_event_build`(`scripts/lumos:1595`),新碼沒繞過它。
- `_redbase_attach` 先問 `_gov_ledger_ignored`(`scripts/lumos:14574`),再把結果傳進 `_redbase_branch_rows`。呼叫者不變,只是順序提前,讓同一個截止時間覆蓋兩者。
- 預算常數 `_REDBASE_ANC_BUDGET_SEC`、`_REDBASE_ANC_CAP` 的命名與註解跟 `_NOTE_REREAD_BUDGET_SEC`(`scripts/lumos:51681`)、其他 `_*_CAP` 一致。`_t.monotonic() + 常數` 的建法跟 `scripts/lumos:53231` 一致。
- `_TG_CONST_PAT` 抄一份三引號片段、不拼接,並在註解寫明出處。這跟 `_TG_LIT_PAT` 註解寫「寫法同 _C_STRIP_PAT 的三引號那段」的既有做法一致(`scripts/lumos:49138`)。

**2. 命名與錯誤處理:大致對齊,有一處測試慣用法不同**

- 印說明走 `print(..., file=sys.stderr)`、前綴 `[spec-gate]`,跟同函式既有的幾句一樣(`scripts/lumos:14396`)。
- git 失敗與逾時用 `_lens_git_dl` 回 `None` 判斷,不丟例外,跟 `scripts/lumos:52816` 一致。判祖先的流程也同 `_note_reread_own_fps`:先 `merge-base --is-ancestor`,rc 不是 0/1 再 `cat-file -e`,SHA 驗證用 `_LENS_SHA_RE.fullmatch`。docstring 已說明「判不了」的取向相反,是刻意的。
- 不對齊一:測試 `t_redbase_branch_rows_fallback_keeps` 想同時拿到回傳值和輸出。鄰居的做法是兩種:`_tqg_say(fn, *a)` 只抓輸出(`scripts/test_lumos.py:122211`),或寫 `with contextlib.redirect_stderr(buf): got = f()`(例如 `scripts/test_lumos.py:15147`)。diff 改成 `setattr(m, "_gb_got", ...)`,把回傳值塞到全檔共用的 `_tqg_module()` 單例(`scripts/test_lumos.py:121032`)上。這個屬性之後沒清掉,跟鄰居「換掉模組屬性、finally 換回」的紀律不同。

severity: minor
blocking: 否
引句:「out = _tqg_say(lambda: setattr(m, "_gb_got", m._redbase_branch_rows(d, "甲", _t.monotonic() - 1, "ignored")))」
file: `scripts/test_lumos.py:122211`

- ⚠ 不算條數、判不準:分離 HEAD 時,既有的 `_codeloop_git_branch` 回 `"HEAD"`(`scripts/lumos:64651`)。新的 `_redbase_branch_name` 回空字串,`ref` 欄位乾脆不寫。讀取端「沒有 ref 就照舊留」跟這個取向自洽,而且 `_redbase_branch_rows` 原本內聯的寫法也是空字串。所以我不算它不一致,只提醒兩個取分支名的 helper 語意不同。取分支名的其他內聯寫法(`scripts/lumos:42091`、`:43632`、`:65159`)已有四種以上,這份 diff 只是把本函式內聯的那條抽成 helper,沒新增做法。

**3. 第二種做法:一處**

- 判祖先:沒有共用 helper,各處都是內聯 `merge-base --is-ancestor`(例如 `scripts/lumos:44814`、`:52816`、`:65136`)。新碼沿用同一個原語,不算第二種。
- 截止時間:用既有的 `_lens_git_dl` / `_git_timeout`(`scripts/lumos:64738-64751`),沒有自寫。
- 字串樣式:跟既有做法一致,見第 1 問。
- 淺複製判斷:這是第二種做法。`_redbase_on_branch` 裡的 `is_shallow` 閉包自己用 `_lens_git_dl(... "rev-parse", "--is-shallow-repository" ...)` 加 `nonlocal` 快取,並且以 `not (... == "false")` 判斷。專案已有共用的 `_git_is_shallow(repo_root, timeout=)`(`scripts/lumos:12021`)。它至少有六處呼叫(`:24143`、`:29173`、`:55638`、`:56826`、`:69810`、`:69905`),`_secev_is_shallow` 也包它(`scripts/lumos:11130-11135`)。`scripts/lumos:55638` 的註解直接寫「既有的淺層判法(代碼審 r1 架構對齊席 Z1)」,代表過去審查席就是這樣要求對齊。
- 我看出的差異:`_git_is_shallow` 在 git 起不來時回 False,在逾時時丟 `TimeoutExpired`。這份 diff 要的是「判不了當淺複製、記錄照留」,方向相反,直接套用會丟掉記錄。
- 專案裡 `_e2e_parent` 已經有一條用 `!= "false"` 判法的先例(`scripts/lumos:42826`),所以「判不了就當淺」本身不是新概念。新增的只是第四種寫法(第三種是 `scripts/lumos:48759`、`:50303` 的 `_lens_git == "true"` 內聯),而且沒有解釋為什麼不包 `_git_is_shallow`。

severity: major
blocking: 是
引句:「r = _lens_git_dl(rr, "rev-parse", "--is-shallow-repository", deadline=deadline)」
file: `scripts/lumos:12021`
file: `scripts/lumos:42826`

⚠ 這條判 major 帶一點不確定:極性需求有正當理由,若作者在註解說明「為什麼不用 `_git_is_shallow`」並收斂成共用 helper(或包一層 `unsure=True`),我會降為 minor 或撤。

不對齊共 2 條,其中 major 1 條
