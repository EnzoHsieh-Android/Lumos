severity: major

1. 實際控制流：`_nodehome_code_kind` 先認出 Python；`_nodehome_is_test` 把 `scripts/test_lumos.py` 判為測試；`_nodehome_required` 因而排除它。規則三再只以 `reqN/reqB` 組成 `code_changed`、`g_code`，所以路由集合只剩 `scripts/lumos`；即使「測試假綠形態」的 `about_code` 已列測試檔，也無法相交，遂報「不是任何一支改動檔的家」。證據：`scripts/lumos:26825`、`scripts/lumos:26846`、`scripts/lumos:27109`、`scripts/lumos:27531`、`scripts/lumos:27615`、`scripts/lumos:27642`、`scripts/lumos:27751`；測試家的宣告在 `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:57`。

2. 既有規則能解釋現況，但未完整回答本案。計劃明定規則三「只在改了需要家的檔時生效」，測試檔不屬需要家的檔；另有近案明寫「不做：讓測試檔可以當家」。這是既有設計取捨，不是程式偏離規格；但 `lumos contracts` 對三個相關節點均回報無正式合約，計劃的「合約候選」也明註尚未標。證據：`docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:83`、`:88`、`:120`、`:122`、`:243`；`docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md:35`。

3. 尚未修；兩份卷證在壓縮前後都 rc1，且都只列 `scripts/lumos`。2026-09-12 Issue 修的是「測試被誤要求有家」；2026-10-05 近案修的是「純換測試綁定不算寫說明」，並刻意沒有讓測試家參與路由，故都不是本案修復。證據：`governance/review-reports/snapshot-encoding-preflight/implementation-home-check.json:2`、`:4`；`governance/review-reports/snapshot-encoding-preflight/implementation-home-check-after-squash.json:2`、`:4`；`docs/lumos-toolchain-knowledge/Issues/各棧測試資料夾被當成要家.md:24`、`:34`；`scripts/test_lumos.py:47979`。

4. 最小候選在規則三路由層，不動 `_nodehome_required`／測試辨認：另組「可作寫回落點的改動檔」＝需要家的改動檔＋前後版本已被有效 Systems `about_code` 認領的測試檔；只拿它驅動 `code_touched/g_code` 與 S13 路由。新增沒家、移除家、S13b、foreign-ref 仍沿用 `req`，因此測試仍不強制有家。翻紅控制應新增：已成家的測試＋該家正文改動→rc0；同批再改一般程式仍 rc0；未成家的測試不觸發安家要求；只改一般程式、卻寫測試家仍 rc1。此控制未跑，唯讀席未造暫存 repo；現有兩份 rc1 卷證就是正向案例的紅燈。

已讀路徑：`CLAUDE.md`、`scripts/lumos`、`scripts/test_lumos.py`、兩份 implementation-home-check JSON、`Systems/每支檔有家.md`、`Systems/測試假綠形態.md`、`Issues/各棧測試資料夾被當成要家.md`、`Projects/每支檔有家_計劃.md`、`Projects/只換測試綁定不算寫說明_計劃.md`。