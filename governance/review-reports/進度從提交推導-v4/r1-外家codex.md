severity: blocker

1. d9 類比失效：語意錯綁未被驗證  
引句:「它不爛,不是因為誰在記,是因為①寫入時驗證證據」  
severity: blocker  
blocking: 是  
`canary record` 不只驗落盤：它讀取報告、核對報告最高 severity、保存報告與審材雜湊，後續 `loop next/status` 直接以這些可重驗輸入判斷能否前進；file: `scripts/lumos:4860`、file: `scripts/lumos:4875`、file: `scripts/lumos:4910`、file: `scripts/lumos:7415`。v4 只驗「Task 7 字串存在」和「某些檔有改」，完全不驗改動屬於 Task 7；這正是 v1「任意瑣碎提交掛任意任務」的洞換到 `task record`，file: `governance/review-reports/進度從提交推導/r1-接手.md:53`。

2. 入口綁定在首次逃生後歸零  
引句:「逃生:一句話「這輪不是任務工作」→放行(同既有 honor 契約)。擋一次,不重複擋」  
severity: blocker  
blocking: 是  
依規格驗收，同一 session 首輪受擋後可說逃生句，之後「同 session 不二擋」，所以第二輪起即使持續改 code、不記 task，也不再需要帳本才能前進。相較勾選框只多了一次可說謊的提示與 skip 留痕，沒有 d9 所稱「不記帳就問不到下一輪」的結構性依賴。

3. 帳只定位任務，仍回答不了任務內進度  
引句:「每個:最後一筆帳的 session/ts/距今/files,或「沒帳」」  
severity: blocker  
blocking: 是  
十二步任務做到 Task 7 的第一子步或最後子步，輸出都只是同一個 Task 7 加檔案快照；接手者仍須讀 diff、逐字稿或散文才能知道真正停點。這是 v3 接手席已否決的「活動粒度不足」換成較細標籤，沒有解掉原症狀，file: `governance/review-reports/進度從提交推導-v3/r1-接手.md:20`。

4. 問題立案成立，但 v4 方案未通過最小解判準  
引句:「症狀:任何一個 session 都答不出「這件實作做到哪一步了」」  
severity: major  
blocking: 是  
症狀與接手消費者成立，但 v4 自己只承諾「最後誰動某任務」，不能回答任務內做到哪；永久新增帳、兩個 CLI、Stop/SessionStart 改造和治理白名單，尚無改善接手的實驗證據。前掃發現的純 Bash 漏檢是獨立既有缺陷，最小交付應先只修該閘；它本身不能證成 `task record`，舊卷亦已指出應先用無帳唯讀原型量接手命中率，file: `governance/review-reports/進度從提交推導/r1-外家codex.md:2451`。

5. 第七條路存在：接手時直接讀現成逐字稿尾端  
引句:「逐字稿認不得時整輪略過(既有行為)」  
severity: major  
blocking: 是  
接手視圖可直接合併逐字稿最後 N 個工具呼叫、最後幾輪對話意圖與當前 `git diff`：前者給「正在做哪個子步」，後者給可驗的實際改動，不新增自報帳，也不把兩者硬綁成假事實。逐字稿缺失或格式認不得時應明報「意圖不可得」，再退回既有無帳唯讀視圖；v3 已提出該最小基線，file: `governance/review-reports/進度從提交推導-v3/r1-外家codex.md:43`。
