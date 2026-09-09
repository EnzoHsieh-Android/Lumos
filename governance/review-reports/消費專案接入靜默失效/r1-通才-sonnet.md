severity: blocker

### f1 兩條 REVISIT 沒有獨立成行,doctor 到期掃描永遠掃不到

severity: major
blocking: 是
引句:「一次冒出很多條。REVISIT:2026-10-09」
doctor 的 Check E5(回訪到期)判準是:strip 掉行首 `-`/`*` 前綴後,整行要以 `REVISIT:` 開頭才算命中(file:`scripts/lumos:1811`、`scripts/lumos:1828`)。計劃裡兩條 REVISIT 都接在同一行其他敘述之後(這一條、以及「這篇沒有涵蓋。REVISIT:2026-10-09 或第二個非 C# 專案接入時回來補」那條),strip 後行首是「既有專案」「四道靜默」,不會命中。到期後 `lumos doctor` 不會唸這兩條,鐵則要求的「接電」形同沒接。

### f2 [D]/[S5] 要反轉同日剛裁定為刻意的「治理帳是CI唯一路徑」

severity: blocker
blocking: 是
引句:「把表態閘的 CI 路徑講對」
`Systems/棧別提問表態閘.md` 同一天(2026-09-09)代碼審 r1 折入的紀錄寫著「表態寫治理帳失敗硬擋而 pass/skip 靜默——刻意:standard 沒有 pass 事件,治理帳是 CI 讀表態的唯一路徑」(file:`docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:38`),而 [D]/[S5] 卻要把訊息改成「CI 讀的是標記檔、治理帳是本機備援」,兩者是同一件事的相反主張。計劃全文沒有一句提到這個同日衝突或給推翻它的新理由,這已經不是「只加提醒不改判定」——提醒的內容本身在否定另一個機制剛審完的刻意裁定。

### f3 S5 只鎖定寫入失敗訊息,放過每次成功都會印的同款主張

severity: major
blocking: 是
引句:「表態寫入失敗的訊息不再說」
`_cmd_codeloop_dispositions` 在治理帳寫入「成功」時印的是「本機記錄…;治理帳也追加了一筆(CI 讀那一筆)」(file:`scripts/lumos:21972`),跟計劃認定錯誤的那句失敗訊息(file:`scripts/lumos:21963`)講的是同一個主張。但 S5 字面只寫「表態寫入失敗的訊息不再說…」,沒把成功路徑那句一起納入驗收範圍,照字面實作完,使用者在每次表態成功(常態路徑,不是例外)時仍會看到同一句被判定為錯的說法。

最嚴重 severity: blocker,blocking 條數: 3
