severity: minor

已讀兩份 patch 的程式碼部分,並對照 spec-gate-nondo 與 lens-repo 兩邊的 `scripts/lumos`。沒有引入第二套切行規則,也沒有跨層直呼。以下 3 條都是建議,不擋。

severity: minor
blocking: 否 — `_note_lines` 沒有另寫正則,共用 `_LEDGER_LINE_RE`,行號規則與帳檔一致,只差尾行處理,不是第二種做法
引句:「parts = _LEDGER_LINE_RE.split(text or "")」
對照:``_ledger_lines`: `scripts/lumos:14002`;`_LEDGER_LINE_RE`: `scripts/lumos:13998`;`_ledger_physical_lines`: `scripts/lumos:14015` ``
判定理由:
- 切行規則(只認 `\r\n`、`\n`、`\r`)是同一支正則,不是第三種。
- `_note_lines` 另外多一個「尾端空段丟掉」的行為,所以是 `_ledger_lines` 之外的第二個包裝函式。
- 兩者合起來有兩條出口(保留空尾段 vs. 丟掉空尾段),各自帶一段很長的說明。建議改成 `_note_lines` 內部呼叫 `_ledger_lines` 再 pop,讓切行只剩一個入口。這不急。
- 範圍:`t_note_lines_spec_gate_family` 只守「規格閘這一族」的 10 支函式。檔內其他讀筆記的地方(`scripts/lumos:10688`、`10710`、`10787` 等)仍用 `splitlines()`。這在計劃裡有明講是範圍外,我不當 finding。
- 已讀 `_notelines_*`、`split_frontmatter`(`scripts/lumos:515`):沒有重複的切行邏輯。

severity: minor
blocking: 否 — 只是把漢字範圍複製了一份,註解自己承認「同 `_RANK_CJK_RE`」,值目前一致
引句:「(?<=[\u4e00-\u9fff\u3400-\u4dbf]) (?=[\u4e00-\u9fff\u3400-\u4dbf])」
對照:``_RANK_CJK_RE`: `scripts/lumos:4752`;`_cjk_bigrams`: `scripts/lumos:5084` ``
判定理由:
- `_cjk_bigrams` 的說明明文寫著「同一個問題長出第二份獨立實作」付過學費。
- 這裡把同一個漢字範圍手抄成字元類別(`_DOOR_HAN_GAP_RE`),沒有從 `_RANK_CJK_RE` 衍生。以後有人擴範圍(`_cjk_bigrams` 有 `REVISIT:2026-11-14` 要看擴不擴),門這邊會漏改。
- 建議二選一:把範圍抽成共用字串常數,或加一支測試斷言兩者範圍相同。
- 壓空白(`\s+` 壓成單一空格)與 NFKC 沒有重複:
  - `_ANY_SPACE_RE`(`scripts/lumos:5139` 附近)是「有沒有空白」的判斷,用途不同。
  - `nfc()` 是路徑與節點名正規化。
  - `_pq_key`(`scripts/lumos:7265`)另有一處 NFKC,是比對題目鍵名,用途也不同。
  - 所以 `_door_scan_text` 的「拿掉看不見字元 → NFKC → 再拿一次 → 壓空白」是門比對專用,沒有已有的 helper 可復用。

severity: minor
blocking: 否 — 現在各判法的分工在註解和測試裡寫清楚了;問題在與另一支分支合併時才會出現,不是這份 diff 單獨成立的缺陷
引句:「return unicodedata.category(ch) in _INVISIBLE_CATS or _pq_is_default_ignorable(ch) or ch in _PQ_BLANK_LOOKALIKES」
對照:``_lens_hidden_char`: `lens-repo/scripts/lumos:17268`;`_PATH_SPECIAL_CATS`: `lens-repo/scripts/lumos:36961`;`_PQ_BLANK_LOOKALIKES`: spec-gate-nondo `scripts/lumos:7029`(3 個碼位),lens-repo `scripts/lumos:6975`(7 個碼位);`_pq_blank`: `scripts/lumos:7245` ``
判定理由與合併建議:
- 我試跑了 `git merge-tree`:兩分支的 `scripts/lumos` 已經會衝突。
- 兩邊對「看不見」的判法關係:
  - lens 的 `_lens_hidden_char` = `_PATH_SPECIAL_CATS`(Cc、Cf、Zl、Zp、Cs)加 Co、Cn、預設可忽略全表、`_PQ_BLANK_LOOKALIKES`。
  - 這支的 `_is_invisible` = Cc、Cf、Cn、Co、Cs、Mn、Me、Zl、Zp 加同一張預設可忽略全表、同一個 `_PQ_BLANK_LOOKALIKES`,再把 `\t`、`\n`、`\r` 當看得見。
  - 所以 `_is_invisible(c)` 等於「`_lens_hidden_char(c)` 或類別為 Mn、Me」,並排除那三個看得見的控制字元。兩邊其實是同一個底座加不同的差額。
- 具體建議:抽一支底層 `_invisible_base(c)`。
  - 它只含 `_PATH_SPECIAL_CATS`、Co、Cn、預設可忽略全表、`_PQ_BLANK_LOOKALIKES`。
  - `_lens_hidden_char = _invisible_base`。
  - `_is_invisible = (_invisible_base(c) or 類別 in (Mn, Me)) and c not in _VISIBLE_CONTROLS`。
  - `_pq_blank` 和 `_residual_claim_fp` 保持獨立,因為它們的分工有理由(空值判斷、指紋穩定)。
- 誰先合誰收斂(判斷,不是查證):
  - 這支已到第十一輪,lens 在第八輪,而且 lens 工作樹還有未提交改動,我判斷這支較可能先合。
  - 先合的那方不用改,後合的那方負責收斂。lens 的 `_lens_hidden_char` 說明裡已經寫了「兩支後合進主線的那一方要把兩邊建在同一份底層上」,責任在後合方。
  - 如果 lens 先合,這支要在 rebase 時把 `_is_invisible` 改成上面的形狀。
- 合併時一個具體風險:`_PQ_BLANK_LOOKALIKES` 兩邊碼位數不同(3 對 7)。
  - 必須取聯集(7 個)。
  - 取聯集之後 `_is_invisible` 對那 4 個碼位(U+303F、U+16FE4、U+13441、U+13442)的結果會變,會影響門的比對。
  - 所以 `_DOOR_RULE_VERSION` 要再升一版,並重跑 `t_zero_width_strip_all_invisible` 與 `t_pq_blank_division_from_invisible`。
- 提醒:`t_pq_blank_division_from_invisible` 這類「分工測試」若只釘行為不釘定義來源,合併後底座換了它不一定會紅,收斂時建議補一條斷言兩邊都從同一底座導出。

最高等級 minor,blocking 0 條。
