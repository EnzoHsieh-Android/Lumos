severity: minor

審查範圍:`r2-snapshot.patch`,對照 `/Users/enzo/harness/lumos-green-scope`(HEAD 6e10ae5bd)。這輪沒有跨層直呼,也沒有另寫一套判祖先、截止時間、淺複製或部分複製判斷、字串樣式或測試替身。新碼用的都是鄰居已有的零件。四條 minor 都是「同一種做法在新處又寫了一次」或「語意跟鄰居差一點」。

## 問 1:分層與依賴方向

- 新碼放在規格閘紅燈版那一區:`_redbase_branch_name`(`scripts/lumos:14372`)、`_redbase_branch_rows`(`:14380`)、`_redbase_on_branch`(`:14412`)。
- 它們呼叫的 `_lens_git`、`_lens_git_dl`(`:64764`)、`_git_timeout`(`:64756`)、`_git_is_shallow`(`:12021`)、`_LENS_SHA_RE`(`:64688`)、`_gov_ledger_ignored`(`:1775`),跟原本 `_redbase_branch_rows` 用 `_lens_full_sha`、`_lens_fork_point` 是同一批 helper。
- 呼叫鏈是 `_redbase_attach`(`:14593`)→ `_redbase_branch_rows` → `_redbase_on_branch`。「治理帳被忽略嗎」由最外層 `_redbase_attach` 問一次、當參數往下傳,下層不自己再問。這跟 `_gov_ledger_ignored` 註解寫的「比對工具、規格閘、doctor 共用」一致。
- 判斷:沒有跨層直呼,依賴方向跟鄰居一樣。

## 問 2:命名、錯誤處理、印說明

對齊的部分:
- 常數 `_REDBASE_ANC_BUDGET_SEC` 對照 `_NOTE_REREAD_BUDGET_SEC`(`:51699`)、`_DRIFT_BUDGET_SEC`(`:53670`)。`_REDBASE_ANC_CAP` 對照 `_ROLE_READ_CAP`(`:37687`)、`_NS_DOCTOR_SCAN_CAP`(`:45397`)。
- git 回 None 或逾時、`_git_is_shallow` 丟 `TimeoutExpired` 都當「判不了」,跟 `_drift_born_env_err`(`:55655`)一樣。
- 說明走 `print(..., file=sys.stderr)`,前綴是 `[spec-gate]`,跟同區其他提醒一致。
- 函式內 `import time as _t`、`import subprocess as _sp`,也是這個檔的寫法。

不對齊的一條:

severity: minor
blocking: 否
引句:「ref = d.get("ref")」不用這條,改用下面這句:
引句:「out = _redbase_on_branch(rr, out, head, name, deadline if deadline is not None else _t.monotonic() + _REDBASE_ANC_BUDGET_SEC)」
- `_redbase_branch_rows(..., deadline=None)` 在 None 時自己起算 10 秒預算。
- 鄰居的 `deadline=None` 一律是「沒有截止時間」:`_git_timeout`(`:64756`)、`_lens_git_dl`(`:64764`)、`_gov_ledger_ignored`(`:1775`)、`_note_reread_own_fps`(`:52811`)。
- 鄰居起算預算都在入口,再往下傳,例如 `:53249`、`:43194`。
- 同一個參數名在這個檔裡有兩種 None 意思。結構是對的,只是語意不一致。

## 問 3:有沒有引入第二種做法

結論:沒有「另一種做法」,但有三處是把鄰居的做法再抄一份,沒抽共用。

severity: minor
blocking: 否
引句:「r = _lens_git_dl(rr, "merge-base", "--is-ancestor", sha, head, deadline=deadline)」
- 這是判祖先的第三份內聯:`:52834`(`_note_reread_own_fps`)是同一個 `_lens_git_dl` 加 rc 0/1 直接用、其他再問 `cat-file -e`,新碼幾乎逐行相同。
- 另一份是 `_codeloop_missing_commit`(`:69923` 一帶),「找不到的提交,淺複製判不了、完整 repo 確定不是」,新碼的 `repo_kind() == "full"` 判斷同義。
- 新碼註解有講明極性相反(判不了照留),所以不是另一種做法。
- 這個檔裡每處判祖先本來就各自內聯,沒有共用 helper。判不準,標 ⚠:是否值得抽共用,由編排者決定。

severity: minor
blocking: 否
引句:「pc = _lens_git_dl(rr, "config", "--get", "extensions.partialClone", deadline=deadline)」
- 部分複製與淺複製的判法,在 `repo_kind()` 閉包裡重寫了一份。
- 上一份在 `_drift_born_env_err`(`:55649`、`:55660`),`extensions.partialClone` 這個鍵全檔只有這兩處。
- 判法同一套:同一個設定鍵、同一個 `_git_is_shallow`。差別是新碼改用有截止時間的 `_lens_git_dl`、回三態標籤而不是原因字串。
- 檔內已有「各處包一層帶預算的淺層判法」的先例(`_secev_is_shallow`,`:11130`)。所以結構對,只是兩處判定日後可能各自漂移。

severity: minor
blocking: 否
引句:「br = _lens_git(rr, "symbolic-ref", "-q", "HEAD")」
- 新增了取分支名的 helper `_redbase_branch_name`。
- 底層指令跟 `_note_reread_branch`(`:53332`)一樣,都是 `symbolic-ref -q HEAD`;該函式回完整 refs 名,分離 HEAD 回空字串。
- `_codeloop_git_branch`(`:64669`)用 `rev-parse --abbrev-ref HEAD`,回短名,分離 HEAD 回 `"HEAD"`。現有端到端事件寫 `ref=marker_branch`(`:70694`)就是這種短名。
- 新 helper 回短名、分離 HEAD 時不寫 `ref`(`or None`)。分離 HEAD 這邊跟 `_codeloop_git_branch` 回 `"HEAD"` 不同,而 `ref` 欄位本來就由 `_gate_event_build`(`:1613`)統一落帳。
- 刻意不用 `--short` 是為了避開同名 tag,理由站得住,而且 `_note_reread_branch` 也避開了。
- 判不準,標 ⚠:檔內取分支名本來就有五、六種寫法,這是新增的一種,不算引入新的 git 指令。

測試與樣式常數,都對齊:
- `_TG_CONST_PAT` 的三引號那段是抄一份、註明出處、不拼接,跟 `_TG_LIT_PAT` 抄 `_C_STRIP_PAT`(`:6786`)的既有做法一樣。
- 測試裡換掉模組屬性、在 `finally` 換回(`_REDBASE_ANC_CAP`、`_TitleIndex`、`_raw_test_titles`),跟 `:52576`、`:56113` 一樣。
- `_gb_repo` 建在 `_ig_sg_repo`(`test_lumos.py:123558`)上,tracked 那支用 `_rb_sg_repo`、`_rb_gov`,載入用 `_tqg_module()`,跟紅燈版其他測試一致。
- `rows()` 裡用 `contextlib.redirect_stderr` 而不用 `_tqg_say`,是因為 `_tqg_say`(`:122211`)不回傳函式的返回值,這裡兩個都要,不算第二種做法。

不對齊共 4 條,其中 major 0 條。
