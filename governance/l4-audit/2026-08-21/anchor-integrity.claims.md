# anchor-integrity.note.md 萃取主張

C1. `lumos anchor approve --note` 對 5 個錨點(runner×2 + hooks×3)重算 sha256,寫入 anchor-baseline.json(該檔已 checked-in 進 repo) | 預期驗證點: scripts/lumos 內 anchor approve 子指令實作; anchor-baseline.json 檔案內容/存在
C2. `lumos anchor verify` 逐一比對錨點現況 hash 與 baseline;有 mismatch 或缺檔則回傳 rc1 | 預期驗證點: scripts/lumos 內 anchor verify 函式邏輯與 return code
C3. `scripts/hooks/pre-push` 呼叫 anchor verify 的位置在「環境檢查之後、vault 閘門之前」,屬 repo 層檢查,即使沒有 vault 也會執行 | 預期驗證點: scripts/hooks/pre-push 原始碼中呼叫順序
C4. pre-push 中 anchor verify rc1 會擋下 push,並提供三選一訊息:還原/approve/使用 --no-verify(且會留痕) | 預期驗證點: scripts/hooks/pre-push 的錯誤訊息文字與 rc1 分支處理
C5. `governance/autonomous-loop.sh` 在每輪派 gap orchestrator 之前呼叫 anchor verify,採 errexit-safe 寫法,且 baseline 缺失視為硬擋(hard block) | 預期驗證點: governance/autonomous-loop.sh 原始碼中呼叫 anchor verify 的位置與錯誤處理
C6. loop 入口(autonomous-loop.sh)對「missing baseline」視同失敗直接擋;pre-push 對同一情況則只回傳 rc0 並給警示(漸進採用,不擋) | 預期驗證點: 比對 autonomous-loop.sh 與 scripts/hooks/pre-push 兩處對 missing baseline 的處理分支
C7. anchor approve 會寫入治理帳(governance log)事件,型別為 `anchor-approve`,其 note 內容會顯示在 `lumos gov` 輸出中 | 預期驗證點: scripts/lumos 中 anchor approve 呼叫 _append_governance_log 的程式碼; lumos gov 顯示邏輯
C8. 錨點集合 v1 為固定列舉的 5 個檔案,刻意不包含 scripts/lumos 本體 | 預期驗證點: anchor-baseline.json 內列舉的檔案清單;scripts/lumos 中定義錨點集合的常數
C9. 測試套件 t_anchor 共 14 項檢查,涵蓋:無 baseline 警示、approve 建檔並留痕、gov 顯示 note、改檔導致 rc1、缺檔導致 rc1、--json 選項、重簽容缺、repo 解析錯誤回傳 rc2 | 預期驗證點: 對應 t_anchor 測試檔案(測試案例數量與涵蓋項目)
C10. 決策 d1:採用「方案 A baseline hash + 顯式 approve」,否決「方案 B RHB 環境硬化」與「方案 C 純 diff 標記送審」 | 預期驗證點: docs/design/2026-07-02-anchor-integrity.md 中方案比較段落
C11. 決策 d2:錨點集合 v1 固定列舉 5 檔,不含 scripts/lumos 本體,理由是 lumos 為自主 loop 每日迭代對象,收進 baseline 會導致每日 approve、盲簽疲勞 | 預期驗證點: docs/design/2026-07-02-anchor-integrity.md 對應決策段落;anchor-baseline.json 實際檔案清單是否確實排除 scripts/lumos
C12. 設計稿 `docs/design/2026-07-02-anchor-integrity.md` 經過 3 輪 design-loop;R1 因「missed」被作廢,R2+R3 收斂;qwen 背書(endorsed);辯方共提出 4 次挑戰,全數被判為假 major 並駁倒 | 預期驗證點: docs/design/2026-07-02-anchor-integrity.md 的輪次記錄/歷程內容
C13. 實作計畫檔案存在於 `docs/superpowers/plans/2026-07-02-anchor-integrity.md` | 預期驗證點: 該路徑檔案是否存在
C14. 節點的 verified_by 指向 `[[Verification/2026-07-02_anchor-integrity]]`,文末「相關」亦連結同一驗證節點 `[[2026-07-02_anchor-integrity]]` | 預期驗證點: docs/lumos-toolchain-knowledge/Verification/2026-07-02_anchor-integrity 節點是否存在且內容對應本筆記
C15. DEP 關聯:anchor-integrity 與 `[[lumos-refcheck]]` 為「vault-free 同型」機制(同構但不依賴 vault) | 預期驗證點: docs/lumos-toolchain-knowledge 中 lumos-refcheck 節點內容,比對其機制是否與 anchor-integrity 同型
