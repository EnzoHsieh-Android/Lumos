# design-loop 現況主張萃取（12~15 條）

C1. canary 協議（植入/判定/抽樣分權/漏抓懲罰）已於 2026-08-14 全面停用，單一權威節點為 Systems/canary-audit 的 d5 決定 | 預期驗證點: scripts/lumos 或 skills/lumos-design-loop 中原 canary 植入/判定相關程式路徑是否已不再被現行流程呼叫（若仍存在應標示為 deprecated/歷史帳）

C2. 現行輪記帳改用 `lumos canary record none`，作為純處置帳載體，不再記 caught/missed 語意判定 | 預期驗證點: scripts/lumos 的 cmd_canary（或對應函式）是否接受 `none` 作為 kind/severity 值

C3. panel 輪「有效」的判準 = 記帳席數 ≥ 2 | 預期驗證點: cmd_loop_status 或 disposal-gate 邏輯中對 panel round 有效性的席數常數（≥2）

C4. 收斂機制自 2026-08-04 重設計起改走「處置閘」（--disposal 旗標），為 design-loop 現行推薦路徑；完整設計見 Projects/design-loop重設計 | 預期驗證點: `lumos loop status --disposal` 旗標是否存在且可執行

C5. 舊 K-streak ∧ capture-recapture ∧ 存活≤minor 三合一硬閘已退場（原因：歷史實測 1/38 從未放行，且 capture-recapture 的封閉母體前提不成立）| 預期驗證點: cmd_loop_status 現行收斂合取條件中，capture-recapture 是否已移出必要判準（若仍有輸出應為非阻斷性欄位）

C6. capture-recapture 殘餘估計自 2026-08-14 起降級為 advisory，不進入收斂合取判準（鑑別力 ≈0）| 預期驗證點: 程式碼中 capture-recapture 殘餘估計輸出的欄位是否標示為 advisory / 不影響 exit code

C7. code-loop 已於 2026-08-08 起改走處置閘（與 design-loop 對齊，經具名裁定推翻原防浮動條款），現行 code-loop 收斂路徑不再以舊 panel 閘為主，舊機制碼僅保留供歷史紀錄重放（A 案）| 預期驗證點: skills/lumos-code-loop 文件是否描述現行以處置閘收斂；舊 panel-gate 程式碼是否仍存在但僅用於 replay

C8. seat-check 機制：派工當下產出 dispatch manifest（命名格式 rN-dispatch.json）宣告 materials，分類為 unreported / out_of_scope；越界項目記入 out-of-scope.jsonl、不進收斂帳；materials 為空時視為 vacuous 而豁免，恆回傳 rc0（僅觀測、不做判定）| 預期驗證點: repo 中是否存在 rN-dispatch.json 產生/讀取邏輯與 out-of-scope.jsonl 寫入邏輯

C9. seat-check 有對應機械測試 t_s1_seat_check | 預期驗證點: 測試檔（如 test_lumos.py 或相關）中是否存在名為 t_s1_seat_check 的測試函式，且可執行通過

C10. quote-check：finding 需附逐字引句，與「凍結快照」做機械比對，作為現行把關「審計員是否真的讀過材料」的手段 | 預期驗證點: repo 中是否存在 quote-check 相關程式碼/腳本，比對引句字串與快照內容

C11. `lumos loop status --gate` 現行支援四種收斂模式擇一：legacy（--need 2，K-streak∧G1∧G2∧G3）／panel／light／settle（結清）| 預期驗證點: cmd_loop_status 的旗標解析邏輯是否列出並互斥處理這四種模式

C12. legacy 模式（--panel 未指定時）維持不變：收斂判準 K=2（連續 2 輪 caught 且 severity∈{clean,minor}），max cap = 6 筆 record，達 cap 仍未收斂則停手、記「達 cap 未收斂」攤給人 | 預期驗證點: cmd_loop_status legacy 分支中 K=2 與 cap=6 的常數值

C13. panel 模式收斂判準改為「結構信號」兩條合取：輪有效 ∧ 存活 findings 之 max severity ≤ minor（取代 K-streak∧G2 序列判準），指令為 `lumos loop status --gate --panel` | 預期驗證點: cmd_loop_status --panel 分支中該兩條合取邏輯與對應 CLI 旗標

C14. light 模式 M1 已機械化：`lumos loop status --light --gate` 為單席謂詞判定，FAIL 會區分 retryable 與 ratchet 兩種原因（不再需要人工單靠散文判讀）| 預期驗證點: cmd_loop_status --light 分支程式碼中 retryable/ratchet 分類輸出邏輯

C15. Component A 原語 `lumos canary record --loop/--severity` 與 `lumos loop status --need` 有 test_lumos.py 覆蓋測試 | 預期驗證點: test_lumos.py 中搜尋涵蓋 canary record 與 loop status --need 的測試函式是否存在
