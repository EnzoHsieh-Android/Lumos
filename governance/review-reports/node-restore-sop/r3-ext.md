未見 blocker；有 2 條 major、3 條 minor。指定的 system 骨架四行及 [S3] 四處宣稱均與現況相符。

1. **major** — 合約候選「13 篇」已與 repo 現況不符

   引句：「用過合約候選章節的 13 篇先例全在 Projects、零篇在 Systems」

   問題：按章節標題 `^#{2,3} .*合約候選` 實際得到 Projects **16 篇**、Systems 0 篇；即使排除本 spec 同步進圖譜的 `節點還原SOP_計劃.md`，仍有 **15 篇**，不是 13。逐字短版確為 3 篇，但「同族變體 10 篇」也不足以涵蓋現存其餘 12 篇。照字面把這個數字寫進 reference，落地當天即是 stale 計數宣稱。

   查證：`/tmp/node-restore-sop-r3.md:106`；`docs/lumos-toolchain-knowledge/Projects/精簡版update指令_計劃.md:78` 至 `docs/lumos-toolchain-knowledge/Projects/Android側UI測試綁圖譜工作流_計劃.md:290` 的 16 個標題命中；Systems 目錄同式 grep 為 0。

2. **major** — 「照原文機制原樣用／全對齊」仍不成立

   引句：「照 reference.md 原文的機制原樣用(r2 三席抓到上一版借名走樣,此處全對齊)」

   問題：原文指定兩階段「每節點各派一個乾淨 **Sonnet** agent」，spec 改成泛稱「兩個乾淨 agent」，會允許不同模型或任意 agent，並非原樣。另一方面，原文的 Verification 留痕是在 `❌` 處置鏈中；spec 隨即稱「這就是出口的正式留痕」，但全數 ✅ 時該鏈不會執行。雖然 [S7] 又要求留 Verification 筆記，七步正文沒有交代 PASS 批次如何建立該紀錄，照步驟 6 字面執行可無正式留痕，和 [S7] 互相脫節。

   查證：`/tmp/node-restore-sop-r3.md:109,123`；`skills/lumos-project-notes/reference.md:1040-1052`。

3. **minor** — 「緊貼」及唯一合法範例把正則允許範圍說窄了

   引句：「`推測:`/`佚失:` 必須緊貼行首標籤——`DECISION:推測:依據…` 才算標了」

   問題：`REGEN_PREFIX_RE` 是 `^(?:KEY|DECISION):\s*(推測|佚失):`，`\s*` 接受零個或多個空白。因此以下都合法：

   - `DECISION:推測:…`
   - `DECISION: 推測:…`
   - `DECISION:\t推測:…`

   只有在標籤與身分標記間插入非空白正文，例如 spec 的 `DECISION: 原因不明,推測:…`，才不匹配。故範例本身相容，但「緊貼」及「才算」不是正則的真實邊界，會讓實作者誤把合法的空格形式拒掉。應寫成「標籤後可有空白，但 `推測:`／`佚失:` 必須是第一個非空白內容」。

   查證：`/tmp/node-restore-sop-r3.md:96`；`scripts/lumos:2302-2303,2527-2532,2545-2546`。

4. **minor** — 「隱患」清單中兩個已承認風險沒有可執行回頭條件

   引句：「骨架節點腐化:只寫指針(錯得便宜,讀者走到現場自己發現)、不寫合成敘事;既有 stale/doctor 兜底」

   問題：這只列緩解，沒有定義何時重驗或何種觀測觸發立案；而 `CLAUDE.md` 明定承認風險須附回頭條件。相鄰的「注入面改動」也只有「過設計審+情境探針才推」，這是推前 gate，不是推後何時回頭。兩條均無可操作的事件、門檻或期限。

   查證：`/tmp/node-restore-sop-r3.md:130-131`；`CLAUDE.md:42`。

5. **minor** — 隱患實際只有八條，不是題設所稱九條，且回頭條件完整度不一

   引句：「## 實務隱患」

   問題：該節從編假 why、半成品、併發、注入面、骨架腐化、外洩、不可逆、實跑次數，共 **8 個 bullet**。其中明寫「回頭條件」的只有 5 條；注入面、骨架腐化沒有，金流／不可逆是排除說明而非回頭條件。若設計意圖確為九條，已有一條在修訂時遺失；若只意圖八條，外部審查索引應同步更正。

   查證：`/tmp/node-restore-sop-r3.md:125-134`。

補驗結果：

- `lumos new system` 確實產生 FLOW／KEY／DEP／TEST 四行，沒有 DECISION：`scripts/lumos:8424-8428`。
- [S3] 的「八類」活文字確實恰有四處：`skills/lumos-project-notes/commands/INDEX.md:24`、`CLAUDE.md:31`、`scripts/templates/graph-discipline.md:29`、`scripts/hooks/claude/lumos-entry-hook.py:74`。
- 句中 `DECISION: 原因不明,推測:…` 確會觸發 J-b；這部分宣稱正確：`scripts/lumos:2545-2546`。

最嚴重 severity：major
