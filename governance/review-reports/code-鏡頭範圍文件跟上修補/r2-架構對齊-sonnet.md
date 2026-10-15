severity: minor

已讀 r2-snapshot.patch 全部 281 行,並對照 repo 現況(HEAD 即 8bc09d70)。沒有第二種做法或跨層直呼。以下三條都是 minor。

**Finding 1**

severity: minor
blocking: 否 — 計劃內部兩處說法互相矛盾,但不構成第二種做法;不影響程式或測試
引句:「改:補「工具鏈本 repo 歸資源席」(圍欄內會動的三處之一)」
對照:``file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:79` ``(現況表那一列,patch 內為 context 行)、`同檔:135`(本次改的「圍欄內只動兩個填空與第二行的刪檔紀律(做法 9;原本列的「一句補充」已收回)」)、`同檔:154`(「驗兩個填空與一句補充」)
判定理由:本次把做法 2 那條改成「補充已收回、圍欄內只動兩處」,但同一份計劃的現況表(第 79 列)仍寫要補這句、算「三處之一」,測試寫法(第 154 行)也還寫要驗「一句補充」。三處現在互相矛盾。patch 自己就在同一個 hunk 內展示了第 79 列,所以這是「改一處沒跟上同一事實的其他處」。第 79 列和第 154 行要一併改成「已收回、改寫進〈工具鏈三類〉」。Systems/每輪修補差異派工 的 WHY 已寫「DoS 那句維持原文」,所以矛盾只在計劃內。

**Finding 2**

severity: minor
blocking: 否 — 屬過程字樣的邊角;計劃有〈實作紀錄〉段,但這兩處在做法與回退段
引句:「拿掉做法 6 列的 11 支新測試(含後加的 `t_loop_next_lens_scope_loose_code_ids`」
對照:``file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:235` ``(回退,「含後加的」);`同檔:135`(做法 2,「原本列的…已收回」);`同檔:226`(實作紀錄段內的「起初擴寫進第一條 RULE,後來搬出」,位置合法,不列)
判定理由:CLAUDE.md〈寫筆記時〉規定過程紀錄(哪天做了什麼、怎麼折的)不寫進筆記。上一輪本席第 2 條指的就是計劃做法段的「又加/又補」。這次做法 6、做法 9 已改成直接寫數量與清單,這部分收了。但同一輪又在做法 2 與回退段新增「原本列的…已收回」「含後加的」這類時序字樣,同類沒掃乾淨。回退段只要寫「11 支新測試」並列名,就夠了,不必講哪幾支是後來加的。

**Finding 3**

severity: minor
blocking: 否 — 純文字殘留,不影響意思判讀
引句:「`t_toolchain_lens_scope_note_pointers` 三支,共 11 支」
對照:``file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:150` ``(做法 6)
判定理由:原句是「又加 X、Y、Z 三支」。把三支併進清單後,「三支」留在最後一個測試名後面,變成只有最後一支有量詞,又接「共 11 支」。這是拆句留下的殘字,拿掉「三支」即可。

**上一輪四條是否真的收了**
- 第 1 條(計劃那句 `--finding-kind` 沒列進 Issue):已收。Issue 的 B 類列了「計劃〈實作紀錄〉」,對應 plan 第 228 行確實有該句。
- 第 2 條(計劃新加過程字樣):部分收,見上面的 Finding 2。
- 第 3 條(搬段有過程語與重複):已收。新段拿掉「落時」,改成「判別看的就是上一段那支檔」;Systems 內已沒有重複的「不往上找」。
- 第 4 條(Issue 寫「本分支」):已收。改成「lens-scope-docs 分支,2026-10-15」,A 類狀態也改成帶日期。

**已讀,無 finding 的部分**
- **Systems/pitfalls-code-loop 的 RULE 行:** 只留使用者裁定的原文,`[依據:人]`、`[since]`、`[retire]`、`[until]`、`[confirmed]` 都沒動。搬出的兩點是獨立正文段,位置在〈鏡頭範圍〉那一節、緊接該節段落,測試名拆成獨立一段。寫法跟同節既有段落一致,沒有帶 `[鍵:值]`。
- **Systems/每輪修補差異派工:** 兩處「該案代碼審 r1」過程字樣已拿掉。
- **S9、S10:** 「10 份」算得出來(6 份 LUMOS-SEAT 加 4 份)。S10 新加的 manifest 一條在 `t_templates_toolchain_idempotency_scope` 有對應斷言(`scripts/test_lumos.py` 約 96638 行)。
- **三處對「新規則 2/3」:** 範本 `skills/lumos-design-loop/templates.md:144` 還寫「新規則 2」,Issue 已明列為 B 類待修,不算新矛盾。
- **Issue:** 開頭欄位沒被手改;摘要 PITFALL 行必有鍵齊全。兩條 REVISIT 的寫法符合鐵則 4。

最高等級 minor,blocking 0 條。
