共找到 2 條 blocking finding。

1. blocking: 是；群標: structural  
   引句:「現行 panel/disposal 閘判『該輪存活 max ≤ minor=乾淨輪』語意本來正確」  
   查證: `/tmp/prose-convergence-r1.md:32`；`scripts/lumos:3759-3794`；`scripts/lumos:3825-3829`；`scripts/lumos:9986-10038`  
   問題: 這只適用於 panel 的無-cluster 路徑，而且新 panel 還要求連續兩輪均通過。cluster panel 判的是「fold 後無 disputed-major」，不是 severity max；disposal 更完全不以 max≤minor 為條件，而是要求 findings 全部 folded 或 accepted，只有 blocker 禁止 accepted，major 可附理由接受後過閘。照提案把兩套閘統稱為「minor=乾淨」，會錯誤描述主要 design-loop 使用的 disposal 放行語意，也會讓後續 skill/prompt 與實際閘脫節。

2. blocking: 是；群標: evidence  
   引句:「估計殘餘 blocking(capture-recapture 或 找到×3 粗估)超過門檻(暫定 >5 條/千字)」  
   查證: `/tmp/prose-convergence-r1.md:34`；`governance/review-reports/prose-convergence/web-research.md:6`  
   問題: 歸檔原數字是「估總量≈找到×3」，不是「殘餘量≈找到×3」；若要換算殘餘，依該粗模型應約為找到×2。原門檻則是 0.1、0.25、寬至 1 條／頁，歸檔沒有頁數到「千字」的換算依據，更沒有 >5 條／千字。照字面執行會同時高估殘餘量並採用無來源的新門檻，直接錯觸發或漏觸發整份重寫。

② d2 未發現 blocking 級不相容：panel 的有效輪仍須至少兩席記帳，K=2 新制第二輪須審全量材料；disposal 仍須 report/snapshot 全席留痕重驗。只要「不受理新 minor」是分類政策，而不是省略席報告、快照或記帳，兩套閘都能運作。相關查證: `scripts/lumos:3765-3785`、`scripts/lumos:3897-3907`、`scripts/lumos:10039-10068`。但實作文字應明訂 minor 仍可留在報告並標 non-blocking，避免「不受理」被解讀成不留痕。

最嚴重是否 blocking：是。
