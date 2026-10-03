severity: minor

**三問總答**

1. 分層與依賴方向:對齊。
   - 第二層呼叫第一層的 `_NotelinesPairs`(`_note_audit_mark_appended`)。鄰居 `_note_audit_items` 本來就呼叫第一層的 `_notelines_new`,方向一樣,沒有跨層直呼。
   - `_drift_m1_fit` 往下呼叫共用的 `_gate_event_fit`,方向正確。
   - `relaxed` 用容器參數穿過 `_note_shape_eval`,形狀同 `hints`、`tags`、`slots`:提交前傳 `None`,推送時傳 `{}`。對照 `scripts/lumos:28928`(`_ns_negation_prepare`)。
2. 命名與錯誤處理:大致對齊。
   - 例外類別名回傳、旗標加原因的做法,同 `_ns_negation_prepare` 與 `_NotelinesNet.failed`。
   - 用 dict `st` 傳狀態的 `_notelines_parse_hunks`,沒有鄰居可比,不列。
   - 差異見 Z2、Z3。
3. 第二種做法:沒有重大的。
   - diff 讀法:`_notelines_parse_added` 改成包 `_notelines_parse_hunks`,筆記閘這一側是收斂,不是新增一套。
   - 判定合併:`_note_audit_fold` 是 `_note_audit_fold_scoped` 的衍生,不是兩套邏輯。見 Z3。
   - `_gate_event_fit` 的 `then` 回呼是新形狀,見 Z4。
   - 判定檔加欄:`tail` 是可省略欄位,`_note_audit_parse_verdict` 只對它加型別檢查,不升 `version`。現有 `disputes`、`evidence_ok` 也沒升版,所以一致。

**Z1 殘留的第二套 diff 讀法沒跟著收斂**
severity: minor
blocking: 否 — 結構沒有新增第二種做法,只是舊的那套沒一起收掉
引句:「新碼 `_ns_diff` 釘 --inter-hunk-context=0 --diff-algorithm=myers」
(此句是我對 diff 的轉述,不是 patch 原文。逐字引句:「"--inter-hunk-context=0", "--diff-algorithm=myers", "--src-prefix=a/", "--dst-prefix=b/", *args)」)
1. `scripts/lumos:28470` 的 `_ns_deleted_summary_lines` 同屬筆記閘,仍自己讀 `-` 行。
2. 它仍用 `ln.startswith("---")` 判檔頭,和本次修掉的「內容行 `++ x`」是同一類漏洞。被刪的內容行 `-- x` 在 diff 裡是 `--- x`,會被略過。
3. 它直呼 `_ns_git` 並自帶一組旗標(`--no-renames`),沒有釘 `--inter-hunk-context=0` 與 `--diff-algorithm=myers`,也沒走 `_ns_diff`。
4. 新的 `_notelines_parse_hunks` 已經交出 `segs` 的被刪行,可直接取用。
5. 其他讀法不算:`_diff_added_lines`(`scripts/lumos:23964`,-U3 的另一個用途)與 `_lens_hunks_base_ranges`(`scripts/lumos:39256`,只取 `@@` 範圍)用途不同。

**Z2 追加配對在第二層失敗時靜默,第一層會記帳**
severity: minor
blocking: 否 — 失敗時退回整行送審,方向是安全的,只是記帳方式跟鄰居不一致
引句:「_note_audit_mark_appended(items, _NotelinesPairs(repo_root, False, base_where, tip_where, vault_rel))」
1. 第一層用 `_ns_relaxed_record` 把 `pairs.error` 記成 `relaxed` 的 `git-failed` 或 `error`。
2. 第二層(`_note_audit_mark_appended`)不看 `pairs.failed`,也不寫進 `errs`,配對失敗時既不輸出也不記帳。
3. 鄰居 `_note_audit_items` 有 `errs` 這條回報管道,但這裡沒用。

**Z3 判定合併有兩個入口,範圍規則靠呼叫端自己選**
severity: minor
blocking: 否 — `_note_audit_fold` 由 `_note_audit_fold_scoped` 推出來,不是兩套邏輯
引句:「 給不比範圍的地方用:doctor 事後掃描、skip 的「判過了、不能略過」檢查」
1. prepare、record、check 走 `_note_audit_fold_scoped` 加 `_note_audit_class_for`。
2. doctor(`scripts/lumos:34795`)與 skip(`scripts/lumos:29994`)走不分範圍的 `_note_audit_fold`。
3. 同一個項目在不同入口可能得到不同結論。例如只判句尾的 CONTEXT,在 doctor 會算「整行已涵蓋」。
4. 是否為刻意取捨,交編排者。

**Z4 `_gate_event_fit` 的 `then` 回呼是新形狀**
severity: minor
blocking: 否 — 只有一個回呼使用者,且有文件說明
引句:「        nodes = then(extra, nodes)」
1. 回呼同時改 `extra` 並回傳新的 `nodes`,混了「改參數」與「回傳值」兩種協定。
2. 專案裡 `_gate_event*` 一族沒有其他回呼先例。
3. 另一個呼叫端 `_ns_relaxed_record` 沒傳 `then`,也丟棄回傳值。
4. 判不準這算不算「第二種做法」,標 ⚠ 交編排者。

**Z5 規則名分組表手抄、沒有漂移守衛**
severity: minor
blocking: 否 — 字串目前都對得上,只是漏改時沒有機械擋
引句:「_NS_REVISIT_RULES = ("回頭條件格式不合", "條件寫錯", "條件寫在不評估的地方")」
1. `_NS_FRAG_KEY_RULES` 與 `_NS_REVISIT_RULES` 手抄 `_ns_check_line` 與 `_ns_revisit_violations`(`scripts/lumos:27843` 到 `27854`)吐出的規則名。
2. `scripts/test_lumos.py` 裡沒有任何引用這兩張表的測試。
3. 我逐字對過目前的字串,全部一致。日後有人改規則名,`_ns_viol_key` 會靜默退回「整行規則名」的鍵。

**圖譜鏡頭逐條判**
- `lumos-cli-read`:不影響。這份 diff 沒碰 `search` 的 superseded 濾網。
- `bound-tests-gate`:不影響。沒碰 `code-loop check` 的綁定測試執行,也沒碰其 rc 規則。
- `guard-kill`:不影響。沒碰 `guard kill` 的 rc 優先序與 `--json` 輸出。
- `授權與歸屬`:不影響。沒動 `_VENDORED_TOOLKIT`,新增的 `scripts/templates` 檔不屬授權檔。
- `測試假綠形態`:不影響。diff 內沒有測試檔,「還原翻紅」要求的前置斷言留給正確性席。
- `reversibility-governance-ledger`:不影響。只新增 `note-shape` 的 `relaxed` 事件。`_GOV_FIELD_TYPES` 已涵蓋 `pairs` 與 `check`,所以 `lumos gov` 的型別檢查不會跳過這一行。
- `pitfalls-code-loop`:不影響。
- `design-loop`:不影響。
- 其餘只列名的節點不必答。

不對齊共 5 條,其中 major 0 條
最高嚴重度 minor,blocking 0 條
