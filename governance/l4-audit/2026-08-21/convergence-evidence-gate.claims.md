C1. panel 模式收斂 K 值從 K=1 升級為 K=2,生效門檻為 cutoff 2026-08-06 起新開的 loop;首筆 ts 定錨、不回溯既有 loop;可用環境變數 LUMOS_PANEL_K2_CUTOFF 覆寫此 cutoff 供測試 | 預期驗證點: LUMOS_PANEL_K2_CUTOFF 環境變數讀取點、loop status --panel 相關程式碼

C2. panel 模式下,最後兩輪必須「各自」通過三條合取判準(而非合併看);前一輪為 quiet 評估只印一行摘要;此邏輯由單一函式 _panel_round_conjuncts 於兩處共用實作 | 預期驗證點: 函式 _panel_round_conjuncts

C3. panel 的 cluster 路徑要求「同窗」,且前一輪須為有效輪(cluster 才成立) | 預期驗證點: loop status --panel 的 cluster 邏輯

C4. 收斂後的決定性抽查判定規則:PASS 時計算 sha256(loop_id + rid + 該輪 token 集) % 2,依此決定「應抽」或「免抽」,不依賴編排者誠實回報 | 預期驗證點: 抽查判定相關程式碼中對 sha256(loop_id+rid+tokens) 取模 2 的實作

C5. 應抽中時加開 probe-* 輪,規則為:材料全量、審查席可縮至 3 席、不計入既有輪次 cap、且此類 probe 輪上限 1 次 | 預期驗證點: probe-* 輪的觸發與參數邏輯(席數 3、cap 排除、次數上限 1)

C6. probe 輪若冒出 major 發現,會讓 K=2 收斂窗滑入該髒輪,使 gate 自然回報 FAIL,此為既有機制的自然結果、未新增機制(「撤銷自動化」) | 預期驗證點: K=2 窗口計算邏輯是否會把 probe 輪納入窗內並影響 gate 結果

C7. 循序(非 panel)模式收斂 K=2,對應 CLI 旗標 `--need 2`,程式邏輯為 `all(good(r) for r in rounds[-need:])` | 預期驗證點: `--need` 旗標與程式碼片段 `all(good(r) for r in rounds[-need:])`

C8. 平行 panel 模式收斂為 K=1,程式邏輯為函式 `_loop_status_panel` 只取 `next(reversed(groups.items()))`,即只看最後一輪 | 預期驗證點: 函式 `_loop_status_panel` 中 `next(reversed(groups.items()))` 的取值邏輯

C9. tier=high 實務上走 panel 模式,故實際收斂條件是 K=1(而非部分文件曾誤標的 K=2) | 預期驗證點: tier=high 觸發路徑是否指向 panel 模式(K=1)而非循序模式(K=2)

C10. panel 輪「有效」判準(2026-07-09 落地,`--panel` 旗標)為合取:記帳席數 ≥2 且 0 missed(none 制),且該輪存活的最高嚴重度 max ≤ minor | 預期驗證點: `--panel` 旗標下的輪有效性判斷程式碼(席數≥2、0 missed、max≤minor 三條件)

C11. capture-recapture 殘餘估計已於 2026-08-14 降級為 advisory,不再進入收斂合取判準;理由為鑑別力≈0(殘餘<1 組下輪 major+ 機率 67% vs 殘餘≥1 對照組 79%,p≈0.25;且 f1≤1 時該公式退化) | 預期驗證點: capture-recapture / 殘餘估計相關程式碼是否僅印觀測值(advisory)、不再影響 gate 的合取判準,以及 counts 缺席時是否僅提示不 fail

C12. legacy(無 --panel)路徑的 K-streak ∧ G1 ∧ G2 判準完全不變,只有 panel 模式判準有異動 | 預期驗證點: 無 --panel 旗標時 loop status --gate 的判準邏輯與輸出

C13. GATE PASS(循序模式)的判準為合取:K-streak(必要)∧ G1(_refcheck_scan 掃出的引用座標須 0 missing、0 超界)∧ G2(findings 數列單調不增、末輪 findings ≤1、末步呈下降,K=1 退化時末輪需=0)∧ G3(若帶 --spec,驗雙 hash 鏈,收斂窗內若無 hash 記錄則直接 FAIL,非 advisory) | 預期驗證點: loop status --gate --spec 的 G1/G2/G3 判準程式碼,含 _refcheck_scan 呼叫與 G3 的雙 hash 鏈驗證

C14. cross_audit 使用 _build_prompt 產生 sentinel 定界文字,並以 _parse_worst 函式優先回傳「末行」解析結果,回傳值為 (sev, parse_fallback) 二元組 | 預期驗證點: `governance/autonomous_loop/cross_audit.py` 中 _build_prompt 與 _parse_worst 函式,含其回傳型別 (sev, parse_fallback)

C15. §2.5c 計票規則:發現等級 ≥major 者,須「經機械驗證後仍存活」才計 +1 reject;若該指控被全數反證(全反證),則視為 endorsed-after-refute 並放行,不計 reject | 預期驗證點: cross_audit 或 design-loop 中 §2.5c 對應的計票程式碼/prompt 契約(≥major 存活才 +1、全反證則放行)

C16. 三條向後相容保證:①不帶 --gate 時,既有輸出與 rc 分毫不變 ②不給 --findings 時,對應鍵不寫入 ③run_cross_audit 既有鍵不動,只新增 parse_fallback 鍵 | 預期驗證點: loop status 在無 --gate/--findings 旗標下的輸出格式,以及 run_cross_audit 回傳結構是否僅新增 parse_fallback 鍵而不動既有鍵

C17. 決策 d2:「留痕完整」不再單獨設錨,因 {streak 通過} ⊆ {留痕完整} 恆真、屬零判別力裝飾;此次改動使 gate 從三錨收斂為兩錨 | 預期驗證點: gate 判準錨點數量(應為兩錨而非三錨),不存在獨立的「留痕完整」檢查項

C18. 決策 d3:cross_reject 計票規則由「qwen 喊 major 即計」改為「喊的 major 須經機械驗證後仍存活才計」,全反證則以 endorsed-after-refute 放行 | 預期驗證點: cross_reject 計票邏輯變更前後對照,確認現行規則是「驗證存活才計」

C19. 交付測試規模:t_canary_findings 3 項 + t_loop_gate 16 項 checks(CLI)+ TestCrossAudit 新增 4 項(unittest);全量 352 passed 全綠 | 預期驗證點: 測試檔案 t_canary_findings(3 checks)、t_loop_gate(16 checks)、TestCrossAudit(4 checks 新增),以及全量測試套件執行結果 352 passed
