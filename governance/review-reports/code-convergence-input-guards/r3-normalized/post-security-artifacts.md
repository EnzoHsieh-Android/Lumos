severity: minor

post-merge-資安-F1  
severity: minor  
blocking: false  
引句:「"report_sha256": "1a79e9f6333763779c7aab0c029dfddf21b0f4674686f7727bb444164fdb26f3"」  
证据file: `docs/.canary-log.jsonl:3539`、`/tmp/lumos-delivery-post-merge-materials/path-index.txt:869`

現象：新增裁決帳宣稱報告雜湊為 `1a79…26f3`，但固定 HEAD 與路徑索引中的實際雜湊是 `8a1b…7e03`。新增帳共核對 22 組路徑／雜湊，僅此一組不符。後續正式放行改綁「重記」迴圈，因此目前不阻斷交付，但原迴圈的接受理由已無法用該路徑重算。

- 誰：能提交治理帳或改寫卷證的貢獻者。
- 入口：canary 裁決帳的 `report_path`／`report_sha256`。
- 輸入：已變動或被還原的同名報告。
- 收益：保留「已接受」裁決，同時讓原始證據無法核驗。
- 本批新增判準：每個新增帳目中的證據路徑與雜湊必須吻合固定路徑索引；本批是 21/22 通過。

post-merge-資安-F2  
severity: minor  
blocking: false  
引句:「VERIFY:再整合main d9f28e3b的結案摘要提醒。隔離整合候選以實際完整CLI與測試来源真跑454通過0失敗0跳過」  
证据file: `docs/lumos-toolchain-knowledge/Verification/2026-10-07_合併前最新主線整合.md:5`、`docs/lumos-toolchain-knowledge/Verification/2026-10-07_合併前最新主線整合.md:37`

現象：正文新增 d9f28e3b 整合與 454 項驗證，但 `status: pass` 的 `valid_under` 仍只寫 c4f2b0cf／90137667 候選。正文已有「不代答最新 HEAD 全套」的限制，所以不算假造全套綠燈；但只讀 frontmatter 的工具或下一位 agent 看不到新增驗證真正適用的版本。

- 誰：能追加 Verification 正文的貢獻者。
- 入口：圖譜查詢或自動化只讀取 `status`、`valid_under`。
- 輸入：新整合驗證追加到舊的 pass 節點。
- 收益：讓新版本主張搭載舊版本的 pass 狀態。
- 本批新增判準：新增整合版本時，同次更新 `valid_under`；若要保留多段歷史，應明列每段版本邊界。

安全類別逐項結果：

- 執行／動態載入：1302 個非源碼檔全為 `100644`，沒有 symlink 或 executable mode。163 個研究檔未發現 runtime 直接引用；1070 個 review-report 會作為治理雜湊／帳務資料讀取，但未見作為程式執行。9 個 bundle 沒有匯入或執行。
- 路徑穿越：1304 條索引路徑沒有絕對路徑、`..` 或反斜線逃逸；19 筆新增 JSON 沒有控制字元。
- 活動帳完整性：三本帳只追加 19 筆、沒有刪行；所有 JSON/JSONL 均可解析。除 F1 外，其餘新增證據路徑及雜湊吻合索引。
- `rel-cascade`：明確分類為活動輸入；本批只有一筆 header，沒有 cascade action。
- 錨點：12/12 個錨點都存在且 SHA-256 符合固定 HEAD；新增 `scripts/test_lumos.py` 錨點亦符合。驗證描述邊界見 F2。
- waiver：新增一筆精確指紋 waiver，沒有萬用路徑；理由包含超過複雜度 52 時撤回及 2026-10-20 重驗。未發現直接放寬資安規則的新增項。
- 機密／個資：對最新五個活動帳、驗證及錨點檔做高可信金鑰樣式檢查，無命中；沒有把路徑雜湊當成秘密掃描。
- 權限、身分驗證、SQL/命令注入、SSRF、密碼學：本次非源碼增量未新增相關執行入口。
- 供應鏈：沒有新增依賴或自動匯入 bundle；bundle 仍屬可人工匯入的高權限材料。
- DoS：依席次要求不報。

圖譜鏡頭核對：

- `canary-record未落盤事件`：因事故節點命中；未附合約正文。
- `lumos-cli-read`：`scripts/lumos`／測試的家，附一條 search 過濾合約。
- `design-loop`：同為家，附處置閘第五步合約。
- `pitfalls-code-loop`：家且標示風險，未附合約正文。
- `bound-tests-gate`：家，附固定席測試真跑合約。
- `guard-kill`：家，附退出碼優先序及 JSON stdout 純度兩條合約。
- `授權與歸屬`：家，附授權檔不得被移除及 vendored 檔頭兩條合約。
- `測試假綠形態`：家，附翻紅釘須證明現場路徑成立的合約。
- 以下 21 項只有名稱，鏡頭因上限未提供理由或正文，不能拿來宣稱已核對合約：`loop-convergence-recording`、`lumos-cli-lifecycle`、`reversibility-governance-ledger`、`lumos-deinit`、`節點範圍與索引守衛`、`check-t-sentinel`、`doctor-irreversible-hint`、`check-r-guard`、`cochange-guard`、`lumos-refcheck`、`canary-audit`、三個 slim install/uninstall 節點、五個 Projects 節點、`core-invariant-baseline`、`judge-severity-gate`。
- 來源限制：鏡頭是 `impact --diff` 的 advisory 輸出；「測試存在」不代表跑過或有殺傷力；另有一個新增／改名檔未列，外部碼表補選也因時限中止。

固定性與分類：

- HEAD 已核對為 `25683c65991e3602335462406893cfa2099b5746`。
- patch 與索引皆為 1304 路徑，集合完全相同；1304 個實體 SHA-256 全符合索引。
- 分類：53 圖譜、4 活動帳、1 waiver、1 錨點、1 rel-cascade、5 replay、163 研究封存、1070 審查卷證、4 skill 指令文件、2 源碼。源碼留給獨立席。

實讀：完整讀取 `closure.patch`、`graph-lens.txt`、最新驗證與錨點；結構化讀取 `incoming-journals.patch` 全部19筆新增；逐條機械分類及雜湊核對 `path-index.txt` 全1304項；對 `full-branch.patch` 核對全部1304個檔案標頭並定點讀高風險 hunk。

未讀：`full-branch.patch` 其餘約68.7萬行、舊研究與其他席報告正文、9個 bundle 內容、舊帳歷史正文、鏡頭只列名的21篇全文。沒有進入 `review-reports` 閱讀其他席報告，也沒有匯入 bundle；因此不宣稱整體 clean。

費用範圍：約1490–1520／1800行；其中約637行是一次 Git 環境警告噪聲，已用無噪聲檢查重跑，不作為證據。