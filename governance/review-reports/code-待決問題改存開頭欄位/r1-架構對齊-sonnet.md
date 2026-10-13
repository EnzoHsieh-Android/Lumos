severity: major

**問 1 分層與依賴方向**

大致對齊,沒有跨層直呼。
- 新碼的位置和鄰居一致:
  - 讀取放在 `PQ_STAGES` 旁,和 `_nl_rule_*` 同區(`scripts/lumos:6891` 一帶)。
  - 寫入放在 `cmd_decision_add` 後面。
  - 規格閘那道放在 `_spec_gate_front` 的判門之後、條款之前。
  - 推送前提醒掛在 `_spec_gate_push_check`(`scripts/lumos:8436`)。
- 呼叫方向和鄰居一致。規格閘、lint、`pitfalls --stage`、兩支寫入指令都呼叫同一支 `pq_parse`。寫入走 `_vault_write_lock`、`load_raw_for_edit`、`atomic_write_verify`,和 `cmd_decision_add` 一樣。
- 唯一的層次問題在 `parse_decisions` 的 `key`、`strict` 參數,見第 3 問的第一條。

**問 2 命名與錯誤處理**

- 錯誤與輸出大致對齊:
  - 輸出前綴 `[spec-gate] 待決問題: ✗ —` 和 `scripts/lumos:7814`、`8085` 同形。
  - 推送前的 `[spec-gate 推送前] 提醒:` 沿用 `_spec_gate_push_check` 既有的 `P`。
  - `question-add`、`question-set` 在 dispatcher 印「擋下:」並回 rc2,和 `decision-amend`(`scripts/lumos:52863`)一致。
- 差異只有下面兩條。

**問 3 第二種做法**

---

severity: major
blocking: 是
引句:「def _strict_list_scan(fm_lines, key, line0):」
對照 `scripts/lumos:18408`(`parse_decisions`)、`scripts/lumos:19721`(`decisions_items`)。設計審說好擴充 `parse_decisions`,實際只在 `parse_decisions` 開了 `strict=True` 的轉接口,函式本體是另一套「怎麼認清單項」的定義:
- 只認 2 格 `- id:` 起頭、4 格 `鍵: 值`,
- 用的是 `_PQ_ITEM_RE`、`_PQ_SUB_RE`、`_PQ_TOP_KEY_RE`,
- 第一個鍵寫死必須是 `id`。

`key` 參數看起來通用,其實 `decisions` 呼叫了也不能用。而且 `parse_decisions` 非嚴格模式還在,同一個函式名底下現在有兩種語意、兩種回傳形狀(`items` 對 `(present, items, errs)`)。`question-set` 另外又用 `strict=True, line0=0` 取原始項目定位行號,讀取端等於有三條路。
這就是「第二種做法」。要嘛把嚴格掃描做成通用、讓 `decisions` 也能用,要嘛承認它是 pending_questions 專用,改成獨立函式、不掛在 `parse_decisions` 的參數上。

---

severity: minor
blocking: 否
引句:「def _pq_decision_state(env, rel, ref, self_fm=None):」
對照 `scripts/lumos:4082`(`_slot_replacement_dead`)、`scripts/lumos:21186`(`_dref_parse`)、`scripts/lumos:21195`(`_dref_norm`)、`scripts/lumos:21211`(`_node_decisions`)。專案已有「決策連結 → 存在?作廢?」的判法:`_dref_norm` 解析,`_node_decisions` 取決策,`valid: false` 算翻案。新函式部分沿用 `_dref_parse`,查找與作廢判斷卻自己重寫一份,多了 `self_fm` 與 `#dN` 簡寫。多這兩樣有理由(寫入前要看尚未落檔的內容),但可以疊在 `_dref_norm`、`_node_decisions` 上,不必另寫迴圈。⚠ 作者可能認為兩邊語意有差。

---

severity: minor
blocking: 否
引句:「def _pq_test_same(a, b):」
對照 `scripts/lumos:5901`(`invariant_test_refs`)、`scripts/lumos:5910`(`resolve_test_refs`)。專案的測試名比對一律走 `resolve_test_refs`:
- 有 `平台:名` 就檢查平台前綴是否已定義,未定義就擲 ValueError(「不猜,免得綁錯平台」),
- 沒前綴就歸預設平台。

`_pq_test_same` 是另一套規則:任一邊沒前綴就只比名字。所以 lint 放行的「已驗」測試名,到規格閘綁定可能被判壞名或懸空。它的取名源(`invariant_test_refs`)倒是有共用。⚠ 這邊 lint 拿不到平台索引,作者在函式註解與計劃裡寫明不建索引,算有意為之,但仍是第二種比法。

---

severity: minor
blocking: 否
引句:「p.add_argument("pairs", nargs="+", metavar="鍵=值"」
對照 `scripts/lumos:51763`(`set`:`key` 與 `value` 兩個位置參數)、`decision-amend`(`did field text`)。專案裡改欄位的指令都是分開的位置參數或旗標。`鍵=值` 這種位置參數在 CLI 裡沒有先例,這是新的參數慣例。它支援一次改多鍵、跨鍵規則一次驗,理由說得通,但仍是新慣例。

---

severity: minor
blocking: 否
引句:「atomic_write_verify(path, new_lines, "pending_questions", lambda _f: True)」
對照 `scripts/lumos:20786`(`cmd_decision_add`)的 `atomic_write_verify(path, new_lines, "decisions", _check)`。鄰居的做法是把「寫完讀回來驗」放進 `_check`,例如用精確 id 比對。新碼把驗證搬到寫前的 `_pq_commit`,寫後的檢查器換成永遠回 True。寫前驗證本身沒問題,但 `atomic_write_verify` 的寫後驗證機制被架空,和其他呼叫點的用法不一致。

---

severity: minor
blocking: 否
引句:「def pq_parse(fm_lines, line0=2):」
`pq_parse` 沒有底線開頭,而同批新函式 `_strict_scalar`、`_strict_list_scan`、`_pq_*` 都有底線。
- 對照 `parse_decisions`(`scripts/lumos:18408`)這類讀取入口本來就是公開名,所以有先例。
- 但 `PQ_STAGES`(既有)、`PQ_STATUSES`(新)公開,`_PQ_KEYS`、`_PQ_REQUIRED` 私有,同一組常數公私混用,沒有規則可循。
- 不影響結構,只提醒命名要有一條線。

---

沒列為不對齊的項目:
- `_pq_git_show` 自己跑 `git show`:專案有 `_lens_git`(`scripts/lumos:46447`)與 `_nodehome_git`(`scripts/lumos:29775`)兩套共用函式,但同在規格閘區的 `scripts/lumos:8224`、`8298` 也是原地 `subprocess.run(["git","-C",...,"show",...])`,參數形狀完全相同。這邊與鄰居一致。
- `_nl_rule_pending_questions` 用 `env_text` 讀全文:`env_text` 是現有函式(`scripts/lumos:761`),只在「已驗」才讀,沒有新做法。

不對齊共 6 條,其中 major 1 條
