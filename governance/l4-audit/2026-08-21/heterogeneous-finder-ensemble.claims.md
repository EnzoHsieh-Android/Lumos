C1. `_capture_counts_from_finders(finders)` 是純函式,做跨 finder 正規化(casefold+strip)、finder 內去重、數每個 distinct key 被幾個 finder 找到、降序回傳 | 預期驗證點: 函式 `_capture_counts_from_finders`

C2. 存在 CLI 指令 `lumos loop capture-counts --finder ... [--from-pitfalls <range> --repo <root>]`,算 capture_counts + Chao1 殘餘估計、吐可貼的 `canary record --capture-counts` 串 | 預期驗證點: 指令 `lumos loop capture-counts`

C3. `--from-pitfalls <range>` 旗標會自動跑 `pitfalls --diff`,按 `source` 欄位分組成確定性 finder(免手貼) | 預期驗證點: 旗標 `--from-pitfalls`

C4. `_pitfall_diff_collect` 是從 `_pitfall_diff_mode` 抽出的純計算函式(不印),供「印」與「收割」共用邏輯 | 預期驗證點: 函式 `_pitfall_diff_collect`、`_pitfall_diff_mode`

C5. capture_counts 語意 = 各 distinct finding-key「被幾個 finder 找到」的次數列表,餵給 `_estimate_remaining_defects`(Chao1 公式)算殘餘估計 | 預期驗證點: 函式 `_estimate_remaining_defects`

C6. 編排流程第4步使用指令 `lumos canary record caught --loop code-<topic> --round rN --capture-counts <串> ...` | 預期驗證點: 指令 `lumos canary record --capture-counts`

C7. `lumos loop status code-<topic> --gate --panel` 的 PASS 判準 = 「輪有效」+「存活 max≤minor」兩條合取 | 預期驗證點: 指令 `lumos loop status --gate --panel`

C8. 2026-08-14 決定將 capture-recapture 殘餘估計降級為 advisory 觀測、不進合取閘,理由是鑑別力≈0(殘餘<1 組下輪 major+ 67% vs ≥1 對照組 79%,p≈0.25;f1≤1 公式退化) | 預期驗證點: 節點/計劃 `Projects/收斂閘殘餘估計降級_計劃`

C9. panel_width(派幾個 LLM reviewer)由 tier 決定 | 預期驗證點: 節點 `risk-tiered-review`

C10. d1 決定:code-loop panel 成員組合為「LLM reviewer + 確定性工具(SARIF linter/測試/type/mutation)」,辯方改為可執行反證,並非直接沿用 design-loop 的 canary 機制換名字 | 預期驗證點: `lumos-code-loop` skill / code-loop 實作中的 panel 組成邏輯

C11. 測試覆蓋:`t_capture_counts_from_finders`(5 案例)+ `t_loop_capture_counts_cli`(7)+ `t_loop_capture_counts_from_pitfalls`(5)+ `t_pitfalls_diff`(11)+ `t_pitfalls_lint_integration`(15,重構後逐鍵不變);全套 865 passed | 預期驗證點: 測試函式 `t_capture_counts_from_finders`、`t_loop_capture_counts_cli`、`t_loop_capture_counts_from_pitfalls`、`t_pitfalls_diff`、`t_pitfalls_lint_integration`;測試套件總數 865

C12. 確定性 finder 來源包含 SARIF linter(讀 `.lumos/lint.json`)、測試 gate、mutation 存活結果 | 預期驗證點: 檔案 `.lumos/lint.json`

C13. `--from-pitfalls` 依 `source` 欄位分組——每個 linter driver / pitfalls 內建各算一個獨立確定性 finder | 預期驗證點: `source` 分組邏輯(capture-counts 實作)

C14. finding-key 的三種產生管道:① LLM reviewer 手動下 `--finder`、② `pitfalls --diff` 命中的 SARIF linter/regex 用 `--from-pitfalls` 自動收割、③ 測試失敗/mutation 存活 | 預期驗證點: 旗標 `--finder`、`--from-pitfalls`

C15. `lumos loop capture-counts` 是 vault-free 純機械原語(執行不寫入知識圖譜) | 預期驗證點: 指令 `lumos loop capture-counts` 的實作(不含圖譜寫入呼叫)
