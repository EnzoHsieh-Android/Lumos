severity: major

**Finding 1**

severity: major
blocking: 是 — 治理帳 ts 解析已有共用函式,這份 diff 另寫第二套,兩套接的例外和處理的範圍不一樣
引句:「沒帶時區的 ts 當本機時間(_gate_event_build 寫的都帶)」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:1425`(`_gov_ts`)
判定理由:
- `_gov_ts` 的註解寫明它是度量段與兩本合讀共用,而且是代碼審 code-gov-ledger-split r1 架構對齊席點名後才合併成一份的。原因是之前兩處各寫一份,接的例外還不一樣。
- 這份 diff 的 `_residual_ev_order` 又直接呼叫 `datetime.fromisoformat`,另寫了一套「沒帶時區當本機時間」的規則。
- 兩套規則不一致:
  - `_gov_ts` 接 ValueError、OverflowError、OSError,並先呼叫 `t.timestamp()` 擋掉出界值。
  - `_residual_ev_order` 只接 ValueError。
  - 事件的 ts 年份出界時,`t.astimezone()` 或後續比較會直接丟例外,崩的是 `guard residual --add` 和 doctor 的檢查路徑。
- 修法:改成 `t = _gov_ts(d.get("ts"))`,再回 `(t, d.get("_seq", -1))`。
- 這是 r1 架構席指出過、已收斂的同一類問題(兩處各寫一份),所以算 major。

**Finding 2**

severity: minor
blocking: 否 — 兩種寫法都能用,只是同一族函式裡出現兩種讀法
引句:「用 git cat-file blob 讀原始位元組:不經 diff」
對照:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:44509`(殘留索引的同族函式用 `git show {rev}:{path}`)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:48351`(`_lens_git(..., "show", ..., binary=True)`)
判定理由:
- 「讀某個版本的檔案」的既有慣例是 `git show rev:path`。
- 新的 `_residual_ask_rows_at` 與同一段的 `_residual_index_at` 骨架相同(missing / unreadable / ls-tree 判斷),卻改用 `cat-file blob`。
- 兩者對 blob 的位元組結果相同,所以不影響正確性,也不構成跨層直呼。
- 但同一族函式現在有兩種寫法,日後調整讀法(例如逾時)要改兩處。
- 建議:統一成 `show`,或在註解寫明 `cat-file` 不經 textconv 的理由。

**Finding 3**

severity: minor
blocking: 否 — 常數已抽出但沒套到所有既有字面值
引句:「版控帳的 repo 相對路徑:_gov_vc_gate_events 讀檔、pitfalls 比兩版」
對照:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:14929`(`Path(root) / "docs" / GOV_LOG_NAME`)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:14562`(`f"docs/{GOV_LOG_NAME}"`)
判定理由:
- 新增的 `GOV_LOG_REL` 只套到兩處:`_gov_vc_gate_events` 和 pitfalls 的 residual-ask 比對。
- 檔內另有至少 14562、14929、14932 這幾處仍用 `"docs" / GOV_LOG_NAME` 或 `docs/{GOV_LOG_NAME}` 的拼法。
- 這讓「版控帳路徑」同時有常數和字面拼法兩種寫法。
- 只是不徹底,不影響行為。

**已對照、未見不對齊的項目**
- `guard audit` 記帳:走 `_gate_event(_vault_repo_root(env), "guard-audit", "stamped", ..., hard=False, nodes=[...], extra={...})`,和 `residual-ask` 的 `_gate_event` 呼叫形狀相同。
- 閘名已補進 `_KNOWN_GATES`(lumos:9417)。
- `guard-audit` 沒有進 `_GOV_LOCAL_PAIRS`,所以走版控帳,符合判定類事件的規則。
- 讀取走既有的 `_gov_vc_gate_events`,沒有另開讀檔路徑。
- 事件的 kind 命名(`stamped`)和既有的 `asked` 是同一種動詞過去分詞風格。

不對齊共 3 條,major 1 條(finding 1)。
