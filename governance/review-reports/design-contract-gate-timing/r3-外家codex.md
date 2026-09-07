severity: major

1. [major] 人裁結果沒有同步回事故節點，判準仍互相矛盾  
blocking: 是  
引句:「★這是一次判準變更(低風險推送會多一種被合約紅擋下的可能)」  
位置：[合約測試閘只在高風險推送跑.md](/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Issues/合約測試閘只在高風險推送跑.md:23)

計劃的具名人裁已改成「低風險測試紅只提醒、不擋」；但仍為 open 的事故節點摘要說低風險會新增「被紅擋下」的可能。兩篇被審文件對同一判準給出相反答案，因此 r2 第 7 條只在計劃內修掉，事故節點尚未修完。

2. [major] S1 所稱「傳下已算好的結果」目前沒有可實作的資料通道，改動面也未具體納入  
blocking: 是  
引句:「拿推送關卡已經算好的那份波及結果」  
位置：[合約測試閘什麼時候跑_計劃.md](/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:78)

引句:「接起來要小心不要讓其中一個的失敗拖垮另一個」  
位置：[合約測試閘什麼時候跑_計劃.md](/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:159)

引句:「impact --diff "$1" --sync-only --repo "$REPO_ROOT"」  
位置：[pre-push](/Users/enzo/harness/lumos-toolchain/scripts/hooks/pre-push:42)

實碼的 `sync_nudge`：

- 把標準輸出直接轉到 stderr；
- 用 `|| true` 吞掉 rc；
- `--sync-only` 只呈現提醒，沒有把完整 `results` 留給後續消費者；
- 函式呼叫點也沒有接收值。

要真正共用一次計算，至少需把該呼叫改成捕獲結構化 JSON，並讓「呈現 sync nudge」與「篩選 bound tests」共同消費該 JSON；這會連帶修改 `scripts/lumos` 的輸入／呈現介面和 pre-push 的失敗隔離。計劃只寫了目標與回訪偵測，沒有把這個必要介面及錯誤語意列入設計，照目前字面無法直接實作 S1 第 3 步。

四種組合推演：

- 低風險＋不可過濾指令：`whole-suite-deferred`，放行。
- 低風險＋測試紅：`red-advisory`，放行。
- 高風險＋測試紅：`red-blocked`，擋下。
- 首推＋低風險：以主線 tip 為起點；主線不存在才 `range-unavailable` 放行，否則依低風險規則處理。

這四種在 S1、S2、S4 之間均有唯一答案，沒有新增 finding。`_mainline_ref()` 也確實存在於 [scripts/lumos](/Users/enzo/harness/lumos-toolchain/scripts/lumos:17520)，依序解析 `main@{upstream}`、`master@{upstream}`、本地 `main/master`；它在 pre-push 呼叫的新頂層 Python 指令內可直接使用。

前輪其餘修復驗收：

- r1 的熱路徑成本否決已明確標為作廢。
- 「反過來算」及其 20% 漏洞方案已刪除。
- 風險分級與執行／阻擋語意已拆開。
- 首推不再以拿掉特例後跑滿全庫為方案。
- 逃生門限制與可量測回訪欄位已補。
- 計劃已有具名人裁，但事故節點未同步，見 finding 1。
- 事故節點摘要已非空。
