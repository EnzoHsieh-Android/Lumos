複驗結果：5/5 findings 均已 fixed。只核對指定五篇，未做新的代碼審。

1. fixed — 缺帳自動建立與人工確認時序

逐字引句：

> 「這項能力只供完成受控切換後使用；首次部署或遺失帳時，操作者不得先以正窗口值啟動派工器來偷跑冷卻計時，必須先完成下一條的人工確認，才可讓程式建立新帳。」

> 「只有上述確認完成後才允許派工器建立新帳，並從新帳 initialized_at 再冷卻完整五小時。」

來源：[探針持久用量帳_計劃.md:31](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Projects/探針持久用量帳_計劃.md:31>)

現在已明確區分「程式具有自動建帳能力」與「受支援的操作時序」：先完成人工確認，才允許建帳，冷卻從新帳建立時間重新算完整五小時。

2. fixed — 非一般／不可讀物件已有替代留證

逐字引句：

> 「一般且可讀檔保留原物、`stat` 與 SHA-256 到事故目錄，非一般檔或不可讀物件改留 `lstat` 的類型／模式／擁有者／路徑、雜湊失敗錯誤與父目錄清單，原物維持原地等待人工處置，不要求不可能產出的 SHA-256。」

來源：[探針持久用量帳_計劃.md:32](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Projects/探針持久用量帳_計劃.md:32>)

無法雜湊的物件不再被要求產生 SHA-256，替代證據、原物處置和人工接手點都已寫明。

3. fixed — 首次真模型重驗欄位及五小時冷卻已補齊

逐字引句：

> 「首次真模型切換前另開 Verification，記帳路徑、程序盤點與處置、其他帳路徑人工確認、確認者與時間，確認後新建帳並冷卻五小時」

> 「完成後才建立新帳並冷卻完整五小時，再記真窗口觀測與保守誤擋。」

來源：[持久用量帳暫存控制驗證.md:6](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Verification/2026-10-08_持久用量帳暫存控制驗證.md:6>)、[同檔:36](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Verification/2026-10-08_持久用量帳暫存控制驗證.md:36>)

`revalidate_when` 與實際 REVISIT 現在一致，足以讓新 session 知道要另開哪種紀錄、填哪些欄位，以及何時開始冷卻。

4. fixed — `codex-harness status: done` 已明示負面驗證語意

逐字引句：

> 「本 Systems 節點的 `status: done` 只表示既有 Codex harness 已建成；`verified_by` 連到 pending 的 [[Verification/2026-10-08_持久用量帳第四輪代碼審停點]] 是負面驗證與下一入口，不表示持久用量帳分支已通過或可推送。」

來源：[codex-harness.md:127](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Systems/codex-harness.md:127>)

`done` 的範圍及 pending 驗證連結的意義都已消歧，不會再合理推導出持久帳分支已通過。

5. fixed — 已完成事項已退出 REVISIT 待辦

逐字引句：

> 「COMPLETED:2026-10-08 鎖逾時、父程序死亡與雙父派工競爭三項控制均已補齊，證據見後續補強控制。」

來源：[持久用量帳暫存控制驗證.md:35](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Verification/2026-10-08_持久用量帳暫存控制驗證.md:35>)

舊的已關閉 `REVISIT` 已改成 `COMPLETED`，不再會被待辦掃描誤收。

結論：就上一輪五條問題而言，這五篇現在能讓沒有對話脈絡的新 session 自足還原切換時序、壞帳留證、真模型重驗要求、Systems 狀態語意及剩餘待辦。

code-loop 狀態沒有改變，仍明確是：

> `status: pending`

> 「第四輪未通過。」

來源：[持久用量帳第四輪代碼審停點.md:3](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Verification/2026-10-08_持久用量帳第四輪代碼審停點.md:3>)、[同檔:18](</Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/docs/lumos-toolchain-knowledge/Verification/2026-10-08_持久用量帳第四輪代碼審停點.md:18>)