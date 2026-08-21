C1. `lumos search <詞>` 預設走 BM25F 排序（2026-07-11 轉正為預設），標題欄位權重為 body 的 4 倍 | 預期驗證點: lumos search 排序邏輯（BM25F 實作、title 權重係數 4）

C2. `search --legacy` 走舊字母序全量排列（逃生旗標） | 預期驗證點: search --legacy 分支邏輯

C3. `search --regex` 查詢自動改走 legacy 舊路（不經 BM25F） | 預期驗證點: search --regex 判斷分支

C4. `search --ranked` 旗標仍保留（相容用途，功能等同新預設） | 預期驗證點: search --ranked 參數解析

C5. `--any` 旗標（多詞片語回退）2026-08-03 起預設為開：整串片語在全庫無命中時，退成各詞 OR 召回；`--no-any` 為逃生關閉旗標 | 預期驗證點: search 內 --any/--no-any 旗標與其預設值、回退觸發條件（整串 0 候選才觸發）

C6. `lumos context <節點> --recommend` 推薦分數為圖分與詞彙分融合，公式 R = 0.6×L + 0.4×G | 預期驗證點: context --recommend 融合公式係數 0.6/0.25/0.15（G 內部三分量）與 0.6/0.4（R 外層融合）

C7. `_reco` 推薦圖分由 BFS 衰減（1/2^k）+ 共引同行加權（×2，有飽和上限）+ Jaccard 三者組成 | 預期驗證點: _reco 或同義推薦函式中的 BFS 衰減公式、共引 ×2 邏輯、Jaccard 計算

C8. `lumos impact --file F --ranked` 的動態閾值係數現行為 0.65（標記為 v1.2，非舊文檔記載的 0.55） | 預期驗證點: impact ranked 程式碼中動態閾值係數常數（應為 0.65）

C9. `lumos impact --ranked` 有 R1 直連保底席機制：rescued 項目恆為 `pinned:false`，不受 threshold/quota 影響，旋鈕 `LUMOS_IMPACT_RESCUE_N` 預設值為 1 | 預期驗證點: 測試 t_impact_direct_rescue；環境變數 LUMOS_IMPACT_RESCUE_N 預設值

C10. `lumos impact --ranked` 有 R2 裸檔名容錯機制：以 `git ls-files` 作唯一母體反查，旋鈕 `BASENAME_MATCH` 預設值為 1 | 預期驗證點: 測試 t_impact_basename_match

C11. `lumos impact --ranked` 有 S2 水位謂詞機制：當 free 直連候選數 < N 時補至 need = N − count，N 值為 3 | 預期驗證點: 測試 t_s2_waterline_rescue；N=3 常數

C12. `impact --ranked` 加入 `_impact_query_junk` 查詢品質閘：剝除 shebang 首行後，殘餘長度 < MINLEN（預設 1，即僅剩 shebang/空白）視同空查詢，L 臂靜默處理，但事故探針不受此閘影響；旋鈕為 `LUMOS_IMPACT_QGATE_MINLEN`（設為 <=0 或 NaN/Inf 時停用） | 預期驗證點: 測試 t_impact_query_junk_unit、t_impact_query_gate_e2e；環境變數 LUMOS_IMPACT_QGATE_MINLEN 語意

C13. `lumos impact --diff <base>..HEAD [--json]` 聚合整段 diff 各檔的 ranked impact（query = 該檔 hunk），輸出受影響功能面 manifest（固定席全保留 + top-8 + 來源檔）；此為 advisory 性質，--diff 聚合版本並未接上 PreToolUse hook（僅單檔版本已轉正接 hook） | 預期驗證點: lumos impact --diff 實作；hook 掛載點程式碼確認 --diff 路徑未被 hook 呼叫

C14. `lumos impact --file` 的 PreToolUse hook（v1.1）：窗外顯示 ranked top-8，TTL 窗內顯示 incidents-only；content trigger 比對 delta 內容（非整份檔案內容） | 預期驗證點: hook 實作中 top-8 常數、TTL 窗口邏輯、delta-based content trigger（非整檔比對）

C15. `context --recommend` 面為 dormant 狀態（尚未如 search 面轉為預設行為，需顯式帶 --recommend 旗標） | 預期驗證點: context 指令預設行為（不帶 --recommend 時不觸發推薦排序）

C16. A3（權威度評分）已消融殺除，現行程式碼路徑不應再有 authority/PPR 相關評分邏輯生效 | 預期驗證點: 排序程式碼中搜尋 authority/PPR 相關函式，應為不存在或已被移除/停用；A1.5 狀態降權旋鈕預設為關

C17. A1 型別先驗：moc 類型節點的詞彙分乘以係數 0.4（train 網格搜尋後凍結值） | 預期驗證點: 排序程式碼中 A1 型別先驗係數常數 0.4，套用對象為 moc 類型節點

C18. 評測器 `governance/eval/retrieval_eval.py` 支援 nDCG、MRR、P@k 指標計算，並可用環境變數 `LUMOS_EVAL_VAULT` 覆寫評測語料所在 vault 路徑 | 預期驗證點: governance/eval/retrieval_eval.py 原始碼；LUMOS_EVAL_VAULT 環境變數讀取邏輯

C19. goldset 生成器 `governance/eval/build_goldset.py` 產出 30 題 search（分層：繁中短詞/identifier/縮寫/單漢字）+ 20 題 edit（真實 git 案例）；候選池為 legacy∪ranked 聯集後以 sha256+salt 去識別洗牌，具備 `--force-full` 旗標拆分空金標情境 | 預期驗證點: build_goldset.py 原始碼中題數常數（30/20）、去識別洗牌邏輯、--force-full 旗標

C20. `hop≥2` 的推薦候選必須 L（詞彙分）> 0 才納入，`hop1` 候選僅受靜態底線約束（不需 L>0） | 預期驗證點: _reco 推薦邏輯中 hop 層級與 L 分數門檻的判斷分支
