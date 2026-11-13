# 任務:獨立重判一批檢索評測的候選(抽驗)

這批是從已標好的候選裡隨機抽出來的,你要獨立判分,用來檢查原本的標註品質。**題目檔裡沒有任何既有分數,也不要去找。**

題目檔:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/adj/spot.json
每題有題號、類型、改的檔與改動片段(或查詢詞),以及「待判」清單(候選路徑)。

語料(候選路徑都相對於這個目錄):
/Users/enzo/harness/lumos-goldset-expand/docs/lumos-toolchain-knowledge/
程式碼在 /Users/enzo/harness/lumos-goldset-expand/ 底下,可以打開被改的那支檔看它在做什麼。

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
1. 對每一筆,開那篇筆記看(標題、摘要、正文前段;必要時讀全文與被改的程式),給 0/1/2。
2. 寫成 JSON 存到 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/adj/out-spot.json,格式:{"E24": {"Systems/x.md": 2}};每筆都要有,一筆不多一筆不少。
3. 寫完用一行 python 驗:筆數與題目檔一致、分數只有 0/1/2。
4. 回報:各給了幾個 2、1、0;最難判的三筆與理由;揭露(見紀律)。

## 紀律（違反會讓這次標註作廢）

- **不要派子代理**，自己做完。
- **不要讀任何已經有分數的檔**：`governance/eval/retrieval-goldset.json`、`governance/eval/raters/` 與 `governance/eval/multiword/` 底下所有檔、`governance/eval/retrieval-labeling-sheet.md`、`governance/eval/retrieval-delta*.json`、`governance/eval/retrieval-delta*-sheet.md`，以及 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/ 底下除了你自己那份以外的任何檔。
- **不要去猜「系統會把誰排前面」**。候選順序是打散過的，沒有名次資訊。
- **只寫你自己那一份輸出**，不要改動 repo 裡任何檔案，判讀與理由也不要寫進任何筆記。
- **揭露**：如果你在筆記正文裡讀到有人對這些題目、這些候選寫過判讀（例如「某席判這篇是 2」），不要照著判，自己另外查證；並在回報裡列出是哪一篇、哪一行。沒讀到就回報「沒有」。
- 臨時檔只放在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ff061f69-7c65-4868-bde8-0f97b9b67044/scratchpad/labeling/，用完由派工的人負責清；你不需要刪任何東西。


- 補充:labeling 目錄底下只准讀你這份派工詞寫明的題目檔、只准寫你自己的輸出檔;特別是 rater-A.json、rater-B.json、merge.json、out/ 與 adj/ 裡其他檔都不准開。
