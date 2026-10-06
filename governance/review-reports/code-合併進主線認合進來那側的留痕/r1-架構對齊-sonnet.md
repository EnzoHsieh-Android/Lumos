severity: major

## 分層與依賴方向(問1)
大體對齊:新函式都放在 `_codeloop_read_dispositions` 與 `_codeloop_record_valid` 之間,由 `_codeloop_guard_verdict` 呼叫;表態那關用 merge_side 回呼注入 `_dispositions_verdict`,沒讓表態判定直呼 code-loop 層(對照 `scripts/lumos:46825` `_codeloop_record_valid_ex` 同層、`scripts/lumos:47227` `_codeloop_guard_verdict`)。帳本讀取抽成 `_codeloop_ledger_events` 讓舊的讀帳路徑與新路徑共用,是收斂不是分叉。無跨層直呼。

## F1 另寫一支 git 包裝 _merge_side_git,跟既有 _lens_git 重複
severity: major
blocking: 是
既有入口 `_lens_git` 已有 binary、timeout 參數,並把 OSError 與 TimeoutExpired 收成回 None(`scripts/lumos:43983`),全檔 77 處在用。新的 `_merge_side_git` 只是把 timeout 換成「剩餘時間」、-C 換成 cwd=,卻少接 OSError(git 不在或 cwd 不存在會直接拋),是引入第二種 git 呼叫入口。可以直接用 `_lens_git(repo_root, ..., timeout=剩餘, binary=...)`,剩餘時間的計算留在呼叫端。
引句:「def _merge_side_git(repo_root, args, deadline, binary=False):」

## F2 新增的期限起算點是第二套預算,且逾時例外沒接
severity: minor
blocking: 否
(a) `_codeloop_merge_side_lookup` 自己以 `_DISP_BUDGET` 另起一個 deadline;但表態那關呼叫它時外層 `_dispositions_verdict` 已有自己的 `deadline=_time.monotonic() + _DISP_BUDGET`,兩者相加最壞約兩倍預算,沒跟既有 deadline 串起來(對照 `scripts/lumos:46491` `_DISP_BUDGET`、單次 git 上限 `scripts/lumos:46934` `_disp_git_timeout`)。
(b) 既有慣例是 `_git_is_shallow(timeout=…)` 與 `_codeloop_record_valid_ex` 逾時「照丟 TimeoutExpired 由呼叫端接」(`scripts/lumos:36218` 有 try/except TimeoutExpired,`scripts/lumos:46818`)。新路徑 `_codeloop_merge_side` 呼叫這兩者都沒接 TimeoutExpired:審查那關 `_codeloop_review_block` 沒有外層 try,例外會往上炸;表態那關被 `_codeloop_guard_verdict` 的 `except Exception` 接住後走 fail-open 放行,與「判不了一律不認」的宣稱相反。⚠ 交編排者確認這是否為預期。
引句:「ok, why, _unsure = _codeloop_record_valid_ex(repo_root, p2, marker_sha, timeout=max(0.1, deadline - _t.monotonic()))」

## F3 行內 __import__("time") 與重複 import time
severity: minor
blocking: 否
同檔慣例是函式頂端 `import time as _time`(例 `_dispositions_verdict`);新碼在 `_codeloop_merge_side` 用 `__import__("time")` 行內呼叫、又在同函式後段另 `import time as _t`,同函式兩種寫法。
引句:「if _git_is_shallow(repo_root, timeout=max(1.0, deadline - __import__("time").monotonic())):」

## 問2 命名與錯誤處理小結
命名 `_codeloop_merge_side_*`、`_disp_record_for` 與既有 `_codeloop_*`、`_disp*` 前綴一致;回 (值, 為什麼) 二元組跟 `_codeloop_record_valid` 同形;訊息中文、帶 sha 前 8 碼,一致。判不了一律不認(fail-closed)有在註解裡明講與表態閘 fail-open 相反,屬有意為之,不列。

## 問3 第二種做法小結
- 另一支 git 包裝:是,見 F1。
- 另一套讀帳:否。`_codeloop_ledger_events` 由舊讀帳路徑(`_codeloop_read_from_ledger`、`_codeloop_read_dispositions`)與新路徑共用;只有讀來源改成 git show 第二個母的樹,這是需求所在,合理。
- 另一套期限:部分,見 F2(a)。沿用 `_DISP_BUDGET` 常數,但另起 deadline。
- 測試側:`_mp_git`、`_mp_commit_all` 是測試輔助,新寫而未複用 `_add_commit`、`_make_high_tier_repo` 的 git 小函式;`_make_high_tier_repo`、`_answer_stack_questions` 有複用,不列。

不對齊共 3 條,其中 major 1 條
