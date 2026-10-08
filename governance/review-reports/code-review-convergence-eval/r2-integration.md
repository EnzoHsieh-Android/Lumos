severity: major

## Finding R2-INT-1

severity: major  
blocking: 是  
引句:「or not text_field(ref.get("path"))」  
file: `governance/eval/review_convergence.py:372`  
file: `governance/eval/review_convergence.md:15`  
file: `governance/eval/review_convergence.md:17`

修補把 receipt 的一般相對路徑套用到「識別欄位最多 128 字元」的 `text_field()`。因此合法且位於 receipts 目錄內、長度 129 字元的路徑，從 before 的有效 trial 退化成 after 的 `receipt-reference` 無效紀錄。

這不是文件宣告的限制：128 字元限制寫給識別欄位；receipt path 的明文合約只有「相對路徑、不得連結或跳出目錄」。常見的巢狀案例目錄很容易超過 128 字元。`compare` 仍可正常結束並把 trial 排除，會改變有效樣本與成對統計。

案例 R2-INT-1-PATH129：

- input：1 case、1 repeat、baseline receipt；path 為 `"p"*124 + ".json"`，共 129 字元；內容 888 bytes、SHA 正確，其餘 receipt pin 全部有效。
- expected_source：`governance/eval/review_convergence.md:15`、`:17`、`:28`。
- expected：`valid_trials=1`、`invalid_records=[]`。
- case_source：inline path-length probe，SHA256 `7e64099259b3a788e82d5f021e448c98a742cd177f7d42f62ccb2fd079a1a23f`。
- case 前提：沙箱拒絕建立指定 integration-tmp，因此只把 `read_bytes` 等價替換成回傳同一份不可變 receipt bytes；`load_receipt` 的路徑驗證、SHA、JSON 與 `compare` 均為固定端原碼。問題分支發生在任何磁碟讀取之前。

before：

- command：`python3.14 -c <inline:7e6409…> /private/tmp/lumos-future-repair-regression-research 8950308b71969f95119c7b2780f7a9ef93f669ac`
- cwd：`/private/tmp/lumos-future-repair-regression-research`
- loaded commit：`8950308b71969f95119c7b2780f7a9ef93f669ac`
- loaded module SHA256：`6e7b04fcc03c0c9712de38d7e4f47e4cce04429f52390905c9da58c9380e2dc4`
- executed：是
- rc：0
- 原始輸出：`{"actual":{"invalid_records":[],"valid_trials":1},"expected":{"invalid_records":[],"valid_trials":1},"path_chars":129,"raw_bytes":888}`

after：

- command：`python3.14 -c <inline:7e6409…> /private/tmp/lumos-future-repair-regression-research c909bf980125dc90f1696372205e322e2ac877c7`
- cwd：同上
- loaded commit：`c909bf980125dc90f1696372205e322e2ac877c7`
- loaded module SHA256：`f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- executed：是
- rc：1
- 原始輸出：`{"actual":{"invalid_records":[{"reason":"receipt-reference","record":0}],"valid_trials":0},"expected":{"invalid_records":[],"valid_trials":1},"path_chars":129,"raw_bytes":888}`

可比與歸因界線：

- 兩端使用完全相同的 manifest、receipt、預期與 probe。
- 完整快照第 557 行恰好把 `isinstance(ref.get("path"), str)` 改成 `text_field(ref.get("path"))`；`text_field` 的 128 字元限制因此直接造成翻紅。
- 可歸因為本輪修補新增的回歸，不是修後才發現的既存問題。
- 尚未做真實磁碟長路徑端到端案例，原因是指定暫存目錄被沙箱拒絕建立；這不影響已定位的讀檔前驗證分支。

## 修補三問

1. 原問題有沒有修好：鏡頭內已驗部分有修好。round 重入現在令 `round_count=null`，跨 loop 的相同 token 衝突也會令兩個 loop 都標記 `conflicting_tokens=true`。
2. 之前正常路徑是否仍成立：「較快但破壞 preserve 不算改善」兩端皆維持 `quality_delta=-1.0`、`round_delta_on_joint_success=null`。
3. 新增問題是否能歸因修補：是，R2-INT-1 可由單一修補行直接歸因。

共同案例證據：

- case_source：inline cohort repair plus preserved quality guard，SHA256 `bb2d09001fc9b9383535e5e00cb892d5f6f375c400daf536ef55ed21ae61be8d`
- command：`python3.14 -c <inline:bb2d09…> <repo> <固定commit>`
- cwd：repo 根
- before：loaded module `6e7b04…2dc4`，executed=是，rc=1；實得 round count `2`、global conflicts `[false,false]`，但既有品質守衛已是 `-1.0/null`。
- after：loaded module `f1e5df…933c`，executed=是，rc=0；實得 round count `null`、global conflicts `[true,true]`、品質守衛仍是 `-1.0/null`。
- 可比界線：同一記憶體輸入、同一預期；只替換固定來源 commit。

歷史來源／CLI 摘要也獨立重播：

- case_source SHA256：`c145516f3747fcba8a5459d61fc9947887a45fe36a6bb5a89576fe941610d78e`
- ledger SHA256：`8352d051e806606a6530b452ea7f06737adafec4e80d4c8f3115a70f03c7e4c6`
- expected_source：`governance/research/review-convergence-eval/cohort-smoke.json:3`、`:9`、`:10`、`:11`、`:12`
- before：inner CLI rc=0，probe rc=1；`224 / 10 / 151`，與固定摘要的 unknown_tokens=153 不同。
- after：inner CLI rc=0，probe rc=0；`224 / 10 / 153`，source 與 collector SHA 均吻合。
- loaded SHAs 分別為 `6e7b04…2dc4`、`f1e5df…933c`；兩端均 executed=是。

## 圖譜硬合約逐條答覆

1. 測試假綠形態：已驗的 round/token 案例有實際前置值與兩端翻紅／轉綠；R2-INT-1 沒有既有綁定測試覆蓋。
2. bound-tests 任一紅／懸空／偽證據須擋：未判定；本鏡頭未讀其實作區段，也未把「綁定測試有」當成跑過。
3. canary record 成功必須落盤可讀回：未判定。
4. canary second 不得影響 gate／rc：未判定。
5. guard kill rc 優先序：未判定。
6. guard kill JSON 純度：未判定。
7. 三支 PowerShell ASCII-only、無 BOM：依指示排除 Windows 原生驗證。
8. PowerShell 不得使用保留 `$Args`：依指示排除 Windows 原生驗證。
9. CLAUDE 注入原地取代並保留外部內容：未判定。
10. CLAUDE 注入冪等：未判定。
11. 完整版區塊需 byte-equal 備份：未判定。
12. 安裝需寫 bin 身分 manifest：未判定。
13. 注入前需通過三層目標守衛：未判定。
14. `.cmd` 不得寫死 `python`：Windows 原生驗證排除。
15. Windows 碰撞檢測需同看 `lumos`、`lumos.cmd`：Windows 原生驗證排除。
16. 卸載 bin 前需依 manifest／內容比對：未判定。
17. 四個卸載清理步驟互不阻擋：未判定。
18. skill 目錄移除前需備份：未判定。
19. CLAUDE sentinel 還原需 byte-equal：未判定。
20. `lumos.cmd` 與 `lumos` 移除需獨立：Windows 原生驗證排除。
21. 卸載需清掉 manifest 與空父目錄：未判定。
22. search 預設只排 superseded、不排 stale：未判定。

表態核對：eventloop、parallel、external、extcode 的 N/A 與同步本機入口相符；hotpath 的字典索引成立。py-memory 的 suggested 做法確有檔案上限與 receipt 欄位投影，但共用 128 字元驗證被誤套到路徑，不能視為無條件滿足。

## 實讀範圍

- 完整：`CLAUDE.md:1-101`、`r2-graph-lens.txt:1-69`、固定 after module `1-557`、`r2-repair-review.patch:1-384`、`r2-repair-binding.json`、`r2-dispositions.json`、README `1-28`、cohort-smoke `1-20`。
- 測試：固定 after tests `1-155`、`340-430`。
- 定點：paired case metadata、兩端 log 的案例名稱／失敗摘要、source-restore 的固定 SHA／命令、完整 snapshot 第 557 行。
- 未讀：所有 r1 席報告與 intake、tests `156-339`、原始 3669 行 repair 全文、snapshot 其他非鏡頭段、純歷史報告正文。
- 未驗：Windows 原生、完整測試套件、上述未判定硬合約實作、真實磁碟長路徑端到端。
- repo 未寫入；收尾 HEAD 仍為 `c909bf980125dc90f1696372205e322e2ac877c7`，工作樹既有卷證狀態未被本席改動。
- 單家族視角不保證無其他回歸。

最高等級: major  
阻擋條數: 1