severity: minor

主要寫入流程、帳檔讀取、徽章、逃逸欄位四塊都沿用既有做法,沒有第二種做法或跨層直呼。有兩處重複實作,都是 minor。

沒問題的部分:
- **寫入流程。** `guard residual` 外層拿 `_vault_write_lock`,內層用 `atomic_write_verify` 寫後自驗,跟 `cmd_guard_audit` 同形。`residual-ask` 的「查有沒有問過再寫一筆」包在同一把鎖裡。`WriteBlocked` 同時是 `ValueError` 和 `RuntimeError`,所以 `except (ValueError, RuntimeError)` 接得住。
- **治理帳。** 讀帳是從 `_retro_gov_events` 抽成 `_gov_vc_gate_events`,loop-retro 與 residual-ask 共用一份路徑守衛和切行,沒有另寫一套。`residual-ask` 登記進 `_KNOWN_GATES`,不在 `_GOV_LOCAL_PAIRS`,走版控帳,跟 loop-retro 一樣。
- **索引檔。** `governance/residual-index.json` 用 `_write_refusal_reason` 加 `_write_lf` 寫,格式與 lint waivers 帳同款。
- **pitfalls 讀 git。** 用 `git show rev:path`,範圍拆解用既有的 `_diff_range_ends`,檔清單用 `--no-renames`。這跟 `_test_suite_for_range` 同款。
- **徽章。** `_LENS_BADGE` 的 dict 沒動,殘留徽章另接在後面,不依賴 `bidx`。`guard list` 也是另加一個 tag。
- **逃逸帳。** `residual_ref` 是 `rec` 上的新鍵,驗法用 `_residual_ref_problem`(與 `guard residual` 同一支)。`--auto`、`--list`、撤回都顯式擋掉。`_escape_stats` 的 `totals` 多一個計數,輸出多一行。

severity: minor
blocking: 否 — 重複的是定位的前置樣板,行為與 `guard audit` 一致,沒有分岔
引句:「loc = _residual_locate(env, node, substr)」
對照:`file: scripts/lumos:18777`(`_cmd_guard_audit_locked` 內聯的 `env.find`、`load_raw_for_edit`、`_kill_find_contract` 與兩種擋下訊息)
判定理由:新的 `_residual_locate` 把這段樣板抽成函式,但 `guard audit` 和 `kill-add` 沒有改用它。同一套定位流程現在有兩種寫法。底層的 `_kill_find_contract` 是共用的,所以只是樣板重複,沒有判準分岔。

severity: minor
blocking: 否 — 兩邊的結果在實務上一致,因為 `_residual_ref_problem` 先擋過一遍
引句:「lit = nfc(pr[0])」
對照:`file: scripts/lumos:7624`(`_pq_decision_state` 帶路徑的節點解析:完全相符優先,否則做不分大小寫的路徑索引,多於一篇判 bad)
判定理由:`_residual_decision` 另寫了一份「決策指標對應到節點」的解析,撞名時取第一篇,`_pq_decision_state` 則判 bad。`_residual_add_problem` 先呼叫 `_residual_ref_problem`,撞名的情況已被擋下,所以不會分岔。但這是第二份路徑解析。

總結:不對齊 2 條(都是 minor),major 0 條。
