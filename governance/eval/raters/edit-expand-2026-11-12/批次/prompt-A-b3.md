# 任務：替檢索評測的候選標相關度（第 3 批,A 席）

你是獨立評審。工作是：對每一題，判斷每一篇候選筆記「該不該被主動推到正要改這支程式的人眼前」（搜尋題則是「對想查這個詞的人有多有用」）。

## 材料

本批題目（只有題目與候選，沒有任何答案）：
/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/batches/b3.json

每題的格式：題號、類型（edit=改檔題 / search=搜尋題）、改的檔（edit 才有）、這次改動的一行片段（edit 才有）或查詢詞（search）、候選清單。

語料（候選路徑都相對於這個目錄）：
/Users/enzo/harness/lumos-goldset-expand/docs/lumos-toolchain-knowledge/

程式碼在 /Users/enzo/harness/lumos-goldset-expand/ 底下，可以打開被改的那支檔看它在做什麼。

本批共 17 題、168 筆候選。**每一筆都要給分，不得略過。**

## 評分尺度

改檔題（想像開發者正要改這支檔、做這段改動）：
- **2 ＝ 必看**：不看會出事——這支檔的家（主要描述它的系統筆記）、這段程式的合約或不能碰的規則、在這裡出過的事故、這段改動直接對應的計劃。
- **1 ＝ 有用**：背景參考，讀了有幫助但不看也不至於出事。
- **0 ＝ 噪音**：跟這支檔、這段改動沒有實質關係，只是字面或連結碰到。

搜尋題（想像有人在知識圖譜搜這個詞）：
- **2 ＝ 必看**：這個查詢的正主、核心文件。
- **1 ＝ 有用**：相關但不是核心。
- **0 ＝ 噪音**：只是字面碰到。

判準是「對這個人有沒有用」，不是「字面出現幾次」。

## 怎麼做

1. 讀題目檔。
2. 對每一筆候選，開那篇筆記看（至少看標題、摘要那幾行、正文前段），改檔題必要時打開被改的檔對照，再給分。
3. 把結果寫成 JSON 存到：
   /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/out/A-b3.json

   格式（分數是整數，不要包成物件、不要加註解）：
   {"E24": {"Systems/xxx.md": 2, "Projects/yyy.md": 0}, "S03": {...}}

   **每一題的鍵必須跟題目檔裡那一題的候選清單完全一致**，一筆不多一筆不少。
4. 寫完自己用一行 python 驗一次：每題候選數跟題目檔一致、分數只有 0/1/2。
5. 最後回報：各給了幾個 2、1、0；最難判的三筆與理由；以及下面「揭露」那一項。

## 紀律（違反會讓這次標註作廢）

- **不要派子代理**，自己做完。
- **不要讀任何已經有分數的檔**：`governance/eval/retrieval-goldset.json`、`governance/eval/raters/` 與 `governance/eval/multiword/` 底下所有檔、`governance/eval/retrieval-labeling-sheet.md`、`governance/eval/retrieval-delta*.json`、`governance/eval/retrieval-delta*-sheet.md`，以及 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/out/ 底下除了你自己那份以外的任何檔。
- **不要去猜「系統會把誰排前面」**。候選順序是打散過的，沒有名次資訊。
- **只寫你自己那一份輸出**，不要改動 repo 裡任何檔案，判讀與理由也不要寫進任何筆記。
- **揭露**：如果你在筆記正文裡讀到有人對這些題目、這些候選寫過判讀（例如「某席判這篇是 2」），不要照著判，自己另外查證；並在回報裡列出是哪一篇、哪一行。沒讀到就回報「沒有」。
- 臨時檔只放在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/out/，用完由派工的人負責清；你不需要刪任何東西。
