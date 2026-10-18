severity: minor

finding: 前導提問流程宣稱沿用既有機制，卻把可自行查證的題排除於 `pending_questions`；既有規則要求此類題標「自答」並附來源，否則會失去追蹤與來源留痕。建議改成「需追蹤的題均寫入；可查證者標自答並附 source，需人裁者標待人」。
severity: minor
blocking: 否
引句:「每題先查已有來源；需要人裁的才寫入該消費專案計劃，既有有效答案直接引用。」
對照 file: `governance/review-reports/code-security-integration-docs/snapshot.patch:85`
對照 file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:236`
對照 file: `docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:57`

finding: 故障執行結果層的 `invalid` 與安全主張層的「未驗」被寫成二選一，未保持既有錯誤語意分層；編譯錯、零案例、非目標失敗的執行證據應判 `invalid`，並因此讓主張維持未驗，而不是任選其一。
severity: minor
blocking: 否
引句:「P1判invalid或未驗，不算有效檢出；真正目標斷言翻紅與還原綠另收證」
對照 file: `governance/review-reports/code-security-integration-docs/snapshot.patch:107`
對照 file: `skills/lumos-project-notes/commands/test-quality-standard.md:90`
對照 file: `skills/lumos-project-notes/commands/test-quality-standard.md:106`
對照 file: `docs/lumos-toolchain-knowledge/Projects/測試品質工具接線_計劃.md:38`

分層與依賴：除上述兩處語意邊界外，已讀，無 finding。提問、主張、測試、卷證、唯讀盤點及正式驗收的責任有分開。

是否引入第二種做法：已讀，無 finding。P1 對照被限定為引用關係，未另建權威格式、runner、題庫或狀態機；`evidence_refs` 仍指向 Verification。

lands_in 落點：已讀，無 finding。本次只補文件整合，母計劃既有候選落點未被冒充成已修改系統；唯讀盤點仍由子計劃落在 `Systems/lumos-cli-read`。

所讀材料：

- `governance/review-reports/code-security-integration-docs/snapshot.patch`，完整 153 行、逐 hunk
- `skills/lumos-project-notes/commands/test-quality-standard.md`
- `skills/lumos-project-notes/commands/03-寫回圖譜.md`
- `Projects/待決問題改存開頭欄位_計劃`
- `Projects/資安護欄唯讀盤點_計劃`
- `Projects/測試品質工具接線_計劃`
- `Projects/後端工程提問與證據擴充_計劃`
- `Projects/消費專案產品安全Brief與證據驗收_計劃`
- `lumos lint Projects/消費專案產品安全Brief與證據驗收_計劃`：0 問題

總結：最嚴重 severity minor；blocking 0 條。
