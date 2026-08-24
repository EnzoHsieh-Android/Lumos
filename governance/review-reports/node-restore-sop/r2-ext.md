否決級未達 blocker，但有 4 條 major；目前不應放行照字面實作。

1. **major**

   引句：「**取得意圖證據→把該行改標 ★INVARIANT★(regen 節點須附 [src:]/[git:],J-a 擋發明)→`lumos guard scaffold`→寫測試→`guard bind`→`guard audit`,全鏈走完才算合約。**」

   問題：三個 guard 指令都不是可執行形式。`guard scaffold` 強制要求 `--node`、`--invariant`、`--method`、`--type`、`--claim`；`guard bind` 要三個位置參數；`guard audit` 要 node 與 invariant。照 SOP 敲會立刻 argparse 失敗，升格鏈無法完成。repo 既有 reference 已給正確 scaffold 形狀。

   查證：`scripts/lumos:5336`、`scripts/lumos:5428`、`scripts/lumos:5938`、`skills/lumos-project-notes/reference.md:571`。

2. **major**

   引句：「**審完 `lumos self-audit <節點>` 蓋章留痕(不蓋 doctor 會一直軟提醒、下個 session 不知道審過)。**」

   問題：把「變體 B 程式碼交叉審計」錯蓋成 `self_audit`。CLI 對該戳記定義的是「一個獨立 agent 只讀圖譜、驗整篇自足性」，不是另一 agent 讀 code 的變體 B。既有變體 B 規範要求建立 Verification 紀錄，並同步 Systems 的 `verified_by`；spec 省掉這兩項，改以語意不同的戳記代替，會留下假的審計種類。工具本身又不驗審計真的發生，無法阻止誤蓋。

   查證：`scripts/lumos:7578-7593`、`skills/lumos-project-notes/reference.md:1034-1035`、`skills/lumos-project-notes/reference.md:1048-1052`。

3. **major**

   引句：「**Check J 綠只證「合約級沒瞎編+指針沒懸空」,防瞎編的主力是交叉審計,不是 lint**」

   問題：前半句仍高估 Check J，且與 spec 後文自相矛盾。J-a 只要求合約行出現 `[src:]`/`[git:]`；J-c 只驗路徑、行號或 commit 是否存在，不驗該證據支持主張。因此 Check J 綠不能證明「合約級沒瞎編」，只能證明合約帶了形狀有效、未懸空的證據指針。spec 自己在第 125 行也承認「只驗存在不驗證據真的支持主張」。

   查證：`scripts/lumos:2539-2572`；spec `/tmp/node-restore-sop-r2.md:65,125`。

4. **major**

   引句：「**『分八類』同句散落三處(INDEX.md:24、本 repo CLAUDE.md 受管區塊、`scripts/templates/graph-discipline.md:29`)一起改**」

   問題：grep 可證不是三處，漏了實際 SessionStart 注入來源 `scripts/hooks/claude/lumos-entry-hook.py`，其中仍寫「按情境分八類」。只改列出的三處後，開 session 時仍會收到過期的「八類」指示，形成範本、索引與 runtime hook 互相矛盾。歷史報告/快照可不改，但活的 hook 必須列入 S3/S5 或另列落地件。

   查證：`skills/lumos-project-notes/commands/INDEX.md:24`、`CLAUDE.md:31`、`scripts/templates/graph-discipline.md:29`、`scripts/hooks/claude/lumos-entry-hook.py:74`。

5. **minor**

   引句：「**兩個乾淨 agent——一個只讀新節點萃取主張,一個只讀 code 逐條判真假**」

   問題：既有變體 B 是「每節點各派」兩階段 agent，且每篇萃取 12–15 條可由程式碼證偽的主張。修訂稿寫成整個「還原批次」只用兩個 agent，未保留逐節點與 12–15 條要求；多篇批次照字面執行可能抽樣不足。此外 `❓ 找不到` 是既有正式結果，spec 的出口只要求「不一致=0 或修正」，沒有處理 unresolved `❓`，仍可能放行無法驗證的主張。

   查證：`skills/lumos-project-notes/reference.md:1040-1052`。

最嚴重 severity：major
