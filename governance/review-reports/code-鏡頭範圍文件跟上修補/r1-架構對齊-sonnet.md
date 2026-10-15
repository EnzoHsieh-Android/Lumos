severity: minor

審了 r1-snapshot.patch 全部 281 行,並對照 repo 現況(templates.md、test_lumos.py)。沒有引入第二種做法或跨層直呼,以下 4 條都是 minor。

**Finding 1**

severity: minor
blocking: 否 — 只是兩處說法暫時不一致,Issue 已排了修正時機,不構成第二種做法
引句:「記帳說明改成「整輪每一條都要標 `--finding-kind`(程式會擋缺漏)」」
對照:`docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:195`(patch 內為 context 行)、`docs/lumos-toolchain-knowledge/Issues/鏡頭範圍代碼審第二輪放行的小缺口.md:40`、`skills/lumos-design-loop/templates.md:493`
判定理由:Issue 把「--finding-kind 全標」的說法列為 B 類待修,理由是程式只在有給時才要求全標。Issue 要修的範圍只列了範本與 Issues/工具鏈範圍外手法紀錄兩處。計劃那句(寫著「以範本為準」)同樣帶著這個錯誤說法,Issue 沒把它列進去。等範本改了,計劃那句會變成唯一沒跟上的地方。計劃、範本、Issue 三處對同一件事的說法目前不一致,屬已知缺口,Issue 有回頭條件。建議把計劃這一句併進 B 類那條的修正範圍。

**Finding 2**

severity: minor
blocking: 否 — 屬風格與規則的邊角,計劃本來就有〈實作紀錄〉段收過程資訊
引句:「代碼審修補後又加 `t_loop_next_lens_scope_loose_code_ids`」
對照:`.../Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:122`(做法 6)、同檔 `:134`(做法 9「代碼審修補又補了 §3.1、§9 跑滿回顧起草者兩份」)
判定理由:CLAUDE.md〈寫筆記時〉規定過程紀錄不寫進筆記,留在 git 與審查卷證。這次改 Systems 時把「代碼審 r1」字樣都拿掉了,是對的。計劃正文做法段這兩處卻新增了「代碼審修補後又加/又補」這類過程字樣,與 Systems 的處理方式不一樣。數量與清單(11 支、10 份)直接寫就夠。計劃裡本來就殘留的「代碼審 r1 補的」是舊帳,這次沒動,不算新增。

**Finding 3**

severity: minor
blocking: 否 — 位置和寫法大體跟同節既有段落一致,問題只在一句過程語與重複
引句:「這兩點是落地時照程式行為補的說明,不是使用者裁定的內容,不帶那條 RULE 的效力」
對照:`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:249`(patch 內新段落),重複的前一段在該檔 `:253` 附近(現況檔行號)
判定理由:RULE 搬出的兩點放在〈工具鏈本 repo 的代碼審鏡頭範圍〉節內,是獨立一段正文,跟同節既有段落的位置和寫法一致,也沒有帶 `[鍵:值]`。有兩個小問題。
- 「落地時」是過程語,可以改成純現況說法,只留「不是使用者裁定」。
- 上一段已有「判別只看那一個根目錄上的那支檔是不是一般檔、不往上找」,新段又講了一次「不往上找」。同節同一事實出現兩次,日後改一處容易漏另一處。
- 測試名那一行拆成獨立段,沒問題。

**Finding 4**

severity: minor
blocking: 否 — 屬時效性寫法,不影響現在的正確性
引句:「已修(本分支):計劃做法 10 還引用舊字串」
對照:`docs/lumos-toolchain-knowledge/Issues/鏡頭範圍代碼審第二輪放行的小缺口.md:27`、`:30`
判定理由:「本分支」是相對說法,分支合併後讀者無從知道指哪一支,屬會過期的描述。「什麼條件算修好」A 類寫「已在一支只改文件的分支全數修掉」,同樣沒有指向。這篇 Issue 的 A 類既然全修完,建議在狀態欄位標明已修,或寫成可查的指向(提交或日期)。其他部分已讀,無 finding:
- 新的 `REVISIT:[when-file:...][by:2027-01-15]` 寫法符合 CLAUDE.md 鐵則 4。
- 舊的 `when-status` 那條 REVISIT 因 A 類已修而拿掉,合理。
- 開頭欄位未被手改,摘要 PITFALL 行的必有鍵齊全。

**已讀,無 finding 的部分**
- **Systems/pitfalls-code-loop 的 RULE 行:** 回到使用者裁定原文,與計劃做法 1 抄的原文逐字相同。`[依據:人]`、`[since:]`、`[retire:]`、`[until:]`、`[confirmed:2026-10-14]` 都沒動。擴寫的內容沒有消失,而是搬進正文,並註明不帶 RULE 效力,沒有拿未經確認的內容冒充人裁。
- **Systems/每輪修補差異派工:** 「該案代碼審 r1」兩處過程字樣已拿掉。這篇現在已無「r1」殘留。
- **計劃的數字:**
  - 刪檔紀律「6 份 + 4 份 = 共 10 份」在做法 9、S9、做法 6 的測試敘述三處一致。
  - 「共 11 支」與列出的測試名一致,回退段也同步。
  - 做法 10 的舊字串改成「『鏡頭範圍』那一行」,與 Systems 現行的條件語氣說法不矛盾。
  - 版本錯位段的條件語氣說法與 Systems 正文一致。
- **S10 加上 manifest 一條:** `t_templates_toolchain_idempotency_scope` 現況已檢查 manifest 須知,S10 的新敘述有測試對應。

最高等級 minor,blocking 0 條。
