1. **blocker**  
   引句:「機器逐篇掃『筆記引用的檔名/函式/欄位是否真的存在於 code』(refcheck/`lumos search --code` 既有零件)」  
   問題:`refcheck` 只抽取 inline code 中含 `/`、且首段是 repo 頂層目錄的「檔案路徑[:行號]」，完全不解析函式名或欄位名；裸函式、類別、欄位會因沒有 `/` 被跳過。`lumos search --code` 更不是搜尋 codebase：它仍只遍歷 `env.notes`，`--code` 僅表示把筆記內 fenced/inline code 納入全文搜尋。因此照本句實作，函式／欄位存在性根本沒有被掃，甚至可得到「零 claim、rc 0」的假綠結果。這直接擊穿步驟 6 宣稱的第一道防編造濾網。  
   查證:`/tmp/node-restore-sop-v2-r1.md:137`; `scripts/lumos:1637-1651`; `scripts/lumos:1670-1676`; `scripts/lumos:1717-1732`; `scripts/lumos:10752-10776`; `scripts/lumos:13706-13710`; `scripts/lumos:13736-13748`; `scripts/lumos:15529-15534`; `scripts/lumos:15685-15688`

2. **major**  
   引句:「進場判斷→`lumos search/context`(有→照慣例用;殘缺→diff 補;沒有→往下)」  
   問題:`search/context` 不是可執行命令形狀，且兩者都要求 positional argument：`search <term>`、`context <note>`。正確流程應是先 `lumos search <詞>`，再把命中的精確節點交給 `lumos context <節點>`。目前 [S2] 是要求落地者把這一排寫入「何時敲哪個指令」薄查表，照字面會產出不能執行的指引；使用場景第 103 行的 `lumos search`/`context` 同樣省略必要參數。  
   查證:`/tmp/node-restore-sop-v2-r1.md:103`; `/tmp/node-restore-sop-v2-r1.md:146`; `scripts/lumos:15529-15531`; `scripts/lumos:6305-6309`；實跑 `python3 scripts/lumos context --help` 顯示必填 `note`，`search --help` 顯示必填 `term`。

3. **major**  
   引句:「兩情境軌跡的交集就是共用基礎設施的機械化定義」  
   問題:正、負兩個情境的軌跡交集，只能證明「這兩次執行都走過」，不能證明它是其他功能也共用的基礎設施，更不能取代「誰還共用它」的掃描。測試啟動器、登入、遙測、快取雜訊都可能進交集；反之條件分支或取樣不足也會漏掉真正共用面。照字面把交集直接登記成承重牆，會製造假共用面與漏共用面。調研原檔也只是將交集稱為共用基礎設施，沒有提出可排除執行雜訊或外推到其他消費者的驗證條件。  
   查證:`/tmp/node-restore-sop-v2-r1.md:121`; `governance/review-reports/node-restore-sop/web-research.md:6-7`

4. **major**  
   引句:「『八類』活文字五處……落地時拿『八類』『八個子檔』兩式全 repo 再掃一次防第六處」  
   問題:第六處現在已經存在，不是待落地時才可能出現：`skills/lumos-project-notes/reference.md` 仍寫「開八個子檔之一」。[S3] 的明列落地面沒有包含它，而 [S1] 又要求修改同一份 `reference.md`；照清單實作後會留下 active 指引自相矛盾，九類索引仍有一個入口宣稱八類。  
   查證:`/tmp/node-restore-sop-v2-r1.md:147`; `skills/lumos-project-notes/reference.md:1211-1213`; 另五處現況見 `CLAUDE.md:31`, `scripts/templates/graph-discipline.md:29`, `scripts/hooks/claude/lumos-entry-hook.py:74`, `skills/lumos-project-notes/SKILL.md:9`, `skills/lumos-project-notes/commands/INDEX.md:24`

雙軌留痕本身核對一致：變體 B 原文要求 ❌ 建 Verification 並同步 `verified_by`；`self-audit` 是節點級戳記，Check S 只讀該欄；L4 清帳確實同時有批次 Verification 與 30 節點逐篇 `self-audit`。PASS 批次建 Verification 則是本 SOP 明標的延伸，與 L4 的 pass Verification 先例相符。查證:`skills/lumos-project-notes/reference.md:1034-1035,1038-1052`; `docs/lumos-toolchain-knowledge/Verification/2026-08-21_L4交叉審計30節點清帳.md:1-13,60-64`

最嚴重 severity：blocker
