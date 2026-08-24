審查結論：有否決級問題。主要破口是 SOP 宣稱「逐句標身分」，但實際 Check J 只掃 frontmatter 的 `summary`，且普通 `KEY:` 未標來源只警告、不阻擋。

1. **major**

   引句：「**再逐句標身分,寫完 `lumos lint <節點>`——Check J 自動把關**」

   問題：照字面會讓執行者誤以為 `lumos lint` 能機械保證整篇節點逐句標明 `[src:]`、`[git:]`、`推測:` 或 `佚失:`。實作明確「只掃 summary 行」；正文完全不掃。即使在 summary 裡，普通未標身分的 `KEY:` 也只產生 `warns`，不計入 lint rc，仍可「lint 綠」。硬擋僅涵蓋無來源的 `★INVARIANT★`、無來源/身分的 `DECISION:`，以及懸空證據指針。這會使 SOP 的核心品質門檻在驗收時假綠。

   查證：`scripts/lumos:2508-2514`、`scripts/lumos:2521-2527`、`scripts/lumos:2544-2549`、`scripts/lumos:2573-2576`。

2. **major**

   引句：「**實跑還原 ≥2 篇節點且 Check J(重建守衛:專擋「從 code 重建的筆記瞎編」的機械檢查,見 related 節點)全綠**」

   問題：「專擋重建筆記瞎編」的宣稱過廣。Check J 不判斷一般 prose 是否瞎編，也不驗證 `[src:]` 是否真的支持該主張；它只驗路徑存在及行號沒有越界。任意存在的 source 行即可通過 J-c。加上未標來源的普通 `KEY:` 只警告，兩篇節點完全可能在核心敘事未受證的情況下達成「Check J/lint 綠」，使成功條件無法證成 spec 所稱的防瞎編效果。

   查證：`scripts/lumos:2539-2557`、`scripts/lumos:2573-2576`。

3. **major**

   引句：「**升格走既有的 guard scaffold→bind→audit,綁上測試才算**」

   問題：內部流程缺少必要的「先把候選改標為 `★INVARIANT★`」步驟。`guard scaffold` 是針對既有合約產測試骨架；前一句卻要求候選「不標 `★INVARIANT★`」。照所列序列直接執行，scaffold 找不到可操作的合約。SOP 必須明列升格順序，例如：取得意圖證據並改標 invariant → scaffold → 實作測試 → bind → audit；而且「綁上測試才算」也漏掉其自己列出的 audit 門檻。

   查證：`skills/lumos-project-notes/commands/06-代碼審與推送.md:9-12`；Check J 對 regen invariant 另要求 `[src:]`/`[git:]`，見 `scripts/lumos:2539-2543`。

4. **minor**

   引句：「**59 個 CLI 子指令沒有掃 repo 產節點的**」

   問題：repo 現況已宣告並維護為 **62 個頂層命令**，spec 兩處仍用 59。即使「沒有掃 repo 產節點者」的實質結論可能成立，量化宣稱已與現況不符，且把「已完整盤點所有 CLI」的證據做舊了。

   查證：`README.md:42`、`skills/lumos-project-notes/reference.md:114`；argparse 子命令入口始於 `scripts/lumos:15319`。

5. **minor**

   引句：「**圖譜空 → `lumos init` 裝殼,然後建一篇 MOC(Map of Content,整個 repo 的導覽頁)節點**」

   問題：`lumos init` 已自動建立 `MOC/index.md`，不是只建六個空資料夾。照字面再「建一篇 MOC」容易新增第二篇總索引，或讓操作者不知道應更新既有 `MOC/index.md`。SOP 應明寫「填充 init 已建立的 `MOC/index.md`」。

   查證：`scripts/lumos:9447-9458`、`scripts/lumos:9803-9806`。

補充核對：`lumos set … regen …` 確實存在，`regen` 在可寫純量白名單中（`scripts/lumos:7278`、`scripts/lumos:7549-7557`）；`lumos link-candidates` 也存在，但必須提供單一 code 檔或 `--all-goldset`，不能裸跑（`scripts/lumos:10201-10209`、`scripts/lumos:15770-15774`）；`lumos lint` 與 doctor 的 Check J 確實共用同一檢查器（`scripts/lumos:2508-2515`）。

最嚴重 severity：major
