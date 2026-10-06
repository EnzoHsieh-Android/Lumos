severity: major

design3-integration-F1

severity: major  
blocking: 是

引句:「增量bundle需前置c4f2b0cf完整物件閉包；未取得前置時verify應拒收。」

目前交付方案只保存增量 bundle，前置提交仍依賴可改寫的遠端 `main`。冷還原收據已證明空物件庫會因缺少前置提交而失敗，且明載封存不是 self-contained；遠端收據也明載不保證歷史永久存在。計劃要求在 squash/rebase 前「先冷還原」只能證明當下可讀，沒有把該前置閉包留下；重寫完成後，增量 bundle 仍可能永久失去還原能力。

佐證 file: `governance/review-reports/code-convergence-input-guards/r3-validation/reviewed-957-incremental-cold.json:6`  
佐證 file: `governance/review-reports/code-convergence-input-guards/r3-validation/reviewed-957-incremental-cold.json:63`  
佐證 file: `governance/review-reports/code-convergence-input-guards/r3-validation/remote-prerequisite-cold.json:127`

修補驗收：在歷史重寫前，必須另外保存包含 `c4f2b0cf…` 完整物件閉包的可取回 artifact，或建立有可驗證保護與保留期的不可變 ref；再模擬遠端已不含該提交，從真正空物件庫只靠記錄入口與兩份封存完成 verify、fetch、commit/tree/blob 比對。否則 S3 不能放行。

design3-integration-F2

severity: minor  
blocking: 否

引句:「超額席留證並把未驗範圍列未判定。」

S4 的人工驗收要求核對「原報告閱讀帳」，但計劃沒有定義該帳的具體路徑、欄位或核對算法。現有 dispatch 只有預計材料與 `mandatory_lines`、`prompt_lines`、`context_cap`，不足以單獨證明席位實際讀了多少、重讀與搜尋是否已計入。末輪可人工判，但日後無法穩定重放。

佐證 file: `governance/review-reports/code-convergence-input-guards/r3-dispatch.json:73`  
佐證 file: `governance/review-reports/code-convergence-input-guards/r3-dispatch.json:82`  
佐證 file: `governance/review-reports/code-convergence-input-guards/r3-dispatch.json:98`

修補驗收：S4 指名實際閱讀帳的固定路徑與最小欄位，例如逐材料實讀行數、搜尋輸出、重讀行數、總量及未讀範圍；不要只以 dispatch 的預算值代答。

design3-integration-F3

severity: minor  
blocking: 否

引句:「只改三份已有家的技能來源：詳細做法放共用範本§3.1，代碼審手冊的「修與釘」接上修前選例，速查僅指路。」

五篇計劃多次使用「三份技能來源」「共用範本」「代碼審手冊」「速查」等名稱，但沒有在計劃中建立名稱到實際路徑的固定對照。實際落點可由 repo 推得出來，卻會讓人工條款可能核對安裝副本或錯誤文件。

佐證 file: `skills/lumos-design-loop/templates.md:190`  
佐證 file: `skills/lumos-code-loop/SKILL.md:45`  
佐證 file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:99`

修補驗收：在主計劃固定材料入口列出三個權威來源的完整 repo-relative path及節次；各子計劃條款改引用該清單。

三類風險

- 主線既有缺陷：計劃有區分規則與既有主線對照收據；本席未發現把既有缺陷誤算成本批新增的 blocking 問題。
- 本批新增缺陷：來源留存設計有 design3-integration-F1；在前置閉包能獨立取回前，不得宣稱整理歷史後仍可還原。
- 有因果證據的修補回歸：本席沒有取得足以判定存在修補回歸的完整兩端行為證據，因此結論是未判定，不是 `none`。

圖譜合約

實際查詢結果中，`Systems/每輪修補差異派工` 與 `Systems/每支檔有家` 沒有登記固定合約；`Systems/測試假綠形態` 有一條「翻紅釘必須配現場成立前置斷言」的固定合約。已定點讀取的 ABA、輸入快照及捕獲失敗測試均包含注入成立／還原檢查，未發現違反該實存合約。佐證 file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:611`

查證與範圍

- 已完整讀五篇計劃，共348行。
- 已讀 `CLAUDE.md` 101行、兩份技能手冊及設計審命令指引共202行，並定點讀 CLI、測試、dispatch與來源收據。
- 實際閱讀量約1,800行，已觸及席位上限。
- 已確認 `home check`、`loop retro-stats`、`loop fix-check`、`spec-gate --no-run` 等具體指令／旗標存在；五篇 `spec-trace` 無未標或懸空條款。
- 未讀任何前輪席報告；未跑完整測試套件、未重新連網驗遠端、未驗Windows、正式部署或DB。
- 未修改 repo，未提交或推送。