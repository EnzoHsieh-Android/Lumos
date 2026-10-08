# 前掃與收貨

preflight-4: ran

四類前掃原始報告見r1-preflight-report.md。refcheck無宣稱，prose-lint未命中，四類風險逐類排除。

## 前掃語意修正

| 原文／問題 | 核對 | 修改 |
|---|---|---|
| 指令入口指向舊guard計劃六態含超時成功 | HIT：cmd_guard_kill實際七態，System有2026-07-29取代說明 | 改指向Systems/guard-kill，未改背書或退出碼 |
| 速查「沒翻紅=測試是裝飾」推論過度 | HIT：rc0只判survived，不能證明案例執行或錯誤不等價 | 計劃要求實作收窄這句，仍需相關、載入、實際執行證據 |
| killed不能自動分類語法／收集／行為錯誤 | HIT：_kill_attribute只核測試名近處失敗字樣 | 明寫killed仍須看真正斷言，不自動升格有效偵測 |

核心裁定未反轉；舊語意不作新流程依據，既有guard門檻未改。以上為正式派審前的語意修正，非正式finding。

## 正式發現處置

| ID | 重現與證據 | 結果 | 處置 |
|---|---|---|---|
| g1 | r1-scope-reproductions.json synthetic marker output | HIT | 折：必要節錄／遮罩，無法安全保留就未判定 |
| e1 | r1-weak-test.log 6斷言通過；actual rc不看weak | HIT | 折：weak=true本次未判定，排除弱因後固定重驗 |
| e2 | r1-attribution-probe.json 語法錯同樣attributed | HIT | 折：runner原始報告逐筆綁版本／錯誤／測試；取不到未判定 |
| x1 | r1-scope-reproductions.json 不同目錄仍繼承fake endpoint，無網路操作 | HIT | 折：端點、測試身分、可重置夾具執行前證據；不齊不執行 |
| x2 | r1-scope-reproductions.json 沒產品變異、換夾具仍0→1 | HIT | 折：固定可控狀態與預先安排綠紅綠，非洗綠重跑 |
| a1 | 與e2同根；actual只截200字 | HIT | 折：取不到原始報告未判定；人工probe獨立綁版本、不作原配方或合約背書 |

觀測和修法分開：e2/a1確認既有摘要不足，但不接受必須擴建CLI的推論；原始報告可由既有runner提供，沒有時明確未判定。保留所有原席severity/blocking，六項均折入，未降級或假稱工具已供給完整輸出。g1報告只去尾端Markdown空白；e2程式圍欄的原PY終止字保留。受控資料全為合成值。
