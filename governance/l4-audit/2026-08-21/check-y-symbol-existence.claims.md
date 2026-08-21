C1. FLOW: doctor 掃 Systems 節點正文的 inline-code → 篩「方法/類別形狀」→ 比對 code haystack → 查無則軟提醒 | 預期驗證點: doctor 相關指令/程式碼中處理 Systems 節點 inline-code 掃描與比對的實作
C2. delguard 是 diff-based（staged diff，commit 時觸發）；Check Y 是全量掃描（隨時可跑） | 預期驗證點: delguard 實作觸發時機 vs Check Y 實作觸發時機
C3. 首發實績：活動報名節點圖譜寫 `ActivityService.RegisterAsync`，實際方法名為 `SubmitRegistrationAsync` | 預期驗證點: ActivityService 原始碼中是否有 RegisterAsync（應無）與 SubmitRegistrationAsync（應有）
C4. 首發實績：滿額贈節點圖譜寫 `ListAvailableAsync`，實際方法名為 `GetActivitiesAsync` | 預期驗證點: 滿額贈相關 service 原始碼中 ListAvailableAsync（應無）與 GetActivitiesAsync（應有）
C5. 首發實績：滿額贈節點圖譜寫 `GetOrdersForRedeemAsync`，實際方法名為 `GetOrderSelectionAsync` | 預期驗證點: 滿額贈相關 service 原始碼中 GetOrdersForRedeemAsync（應無）與 GetOrderSelectionAsync（應有）
C6. 上述三條符號錯誤，在同一天（2026-08-12）10 個 agent 的兩階段交叉審計中全被漏掉 | 預期驗證點: 該日交叉審計記錄/Verification 節點是否載明此三條漏檢
C7. 只掃 Systems 型別節點；Projects/Verification/Issues 不掃（語意決定，非調參） | 預期驗證點: Check Y 實作中節點型別過濾條件（是否僅比對 type: system）
C8. 實測數字：全型別掃描產生 37 命中；限定只掃 Systems 後降為 4 命中 | 預期驗證點: 對同一份圖譜分別以全型別/僅 Systems 跑掃描的命中數
C9. 形狀過濾前（寬鬆抽取任何 PascalCase inline-code）在真實圖譜上有 7%（74/930）未命中率 | 預期驗證點: 對真實圖譜跑寬鬆 PascalCase 抽取，統計未命中比例是否為 74/930
C10. 形狀過濾規則：符號需「無底線、無數字、非全大寫、無副檔名」，且「以 Async 結尾」或「含點號（Class.Method 形式）」才視為候選 | 預期驗證點: Check Y 實作中的符號形狀正規表達式/判斷邏輯
C11. 套用形狀過濾後：279 候選中僅 1 筆未命中（0.4%），且該筆為真陽性（非誤報） | 預期驗證點: 對真實圖譜跑形狀過濾後的候選數與未命中數統計
C12. 否定語境豁免詞清單：零命中、已移除、不存在、查無、已刪、從未、已退役、移除、無此、原記、舊名、改名、removed、no longer、deleted、renamed | 預期驗證點: Check Y 實作中否定語境詞清單的完整內容
C13. 已知限制：Check Y 只認 C#/前端命名慣例（Async 後綴、PascalCase），其他語言棧需擴充形狀規則 | 預期驗證點: 形狀過濾規則是否僅涵蓋 C#/前端慣例、有無其他語言的形狀規則
C14. Check Y 只驗「符號存在」，不驗「用對地方」；後者仍需交叉審計（機制邊界宣稱） | 預期驗證點: Check Y 實作/測試是否只做存在性比對、無語意正確性驗證
C15. 依附節點：DEP 為 `[[Systems/lumos-cli-read]]`；驗證節點為 `[[Verification/2026-08-12_CheckY_符號存在性]]` 與 `[[Verification/2026-08-12_通用性修正_profile化與歷史重放]]` | 預期驗證點: 這些節點/檔案是否存在於 docs/lumos-toolchain-knowledge/
C16. TEST 宣稱有 5 條牙齒測試，涵蓋否定語境豁免、Projects 不掃、形狀過濾擋環境變數/範例ID/檔名 | 預期驗證點: Check Y 對應測試檔案中測試案例數與涵蓋範圍
