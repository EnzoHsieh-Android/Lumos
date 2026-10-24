severity: clean

**1. 結構與位置:一樣。**
- 新驗證筆記放在 `Verification/2026-10-24_效能判定規則實機評測.md`。檔名格式「日期_主題」,跟 `Verification/2026-10-23_macrobench實機端到端.md` 和 `Verification/2026-10-24_Android記憶體與穩定性實驗室驗收.md` 同一個。
- 研究資料放 `governance/research/macrobench/2026-10-24-perf-stats/`。這跟既有的 `2026-10-23-lab-tablet/` 同一個父目錄、同一種「日期-名稱」命名;`2026-10-23_macrobench實機端到端.md` 第 25 行也是用反引號寫 `governance/research/macrobench/…` 指向資料。
- 功能筆記 `Systems/macrobenchmark-adapter.md` 只在 `verified_by` 清單末尾加一條,跟清單裡已有的五條驗證連結是同一種寫法。

**2. 寫法:一樣。**
- 開頭欄位有 `type: verification`、`status`、`date`、`valid_under`、`revalidate_when`、`tags`、`plan_refs`,跟 `2026-10-23_macrobench實機端到端.md` 第 1–16 行相同。`valid_under` 用清單,該篇也用清單,另一篇(記憶體與穩定性)用單行字串,兩種在鄰居裡都有。
- 開頭用「白話:」一段,然後是小節,最後一行 `REVISIT:2026-11-30 …` 放在檔尾。`2026-10-23_macrobench實機端到端.md` 也是這樣(檔尾一行 `REVISIT:2026-12-21 …`)。
- 計劃那邊:`RETIRE-IF:` 只改了內容,位置不變。新增的 `REVISIT:[when-status:Projects/Android效能判定統計化_計劃=doing][by:2027-03-31] …` 用的是既有的事件式寫法,`Projects/治理帳封存_計劃.md:26` 就是同一種。一篇計劃有兩行 REVISIT 也不稀奇,`Projects/審查席唯讀隔離_計劃.md` 有五行。
- 連結全用 `[[Projects/…]]`、`[[Verification/…]]`,跟鄰居一致。

**3. 有沒有第二種做法:沒有。**
- 驗證紀錄、資料目錄、REVISIT、`verified_by` 全走既有管道,沒有新開目錄、欄位或標記。
- 兩個很小的差別我沒列:新篇的實驗腳本路徑寫成相對路徑 `scripts/perf-stats-experiment.sh`,舊篇寫的是絕對路徑 `/Users/enzo/orca/workspaces/macrobench-lab`。計劃的 `status` 現在是 `todo`,而新 REVISIT 等的是 `doing`,這是等開工的意思,不是不一致。這兩點算風格偏好,不算結構分歧。

不對齊共 0 條,其中重大 0 條
