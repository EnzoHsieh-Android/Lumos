severity: major

F1：三支修補回歸測試缺少獨立前置斷言

severity: major  
blocking: 是

硬合約要求修 bug 的翻紅測試先證明目標情境確實成立；但下列測試都是執行產品後才斷言結果：

- 控制字元：產品命令在 file: `governance/eval/test_review_convergence.py:199`，第一個斷言在 file: `governance/eval/test_review_convergence.py:205`。
- token 型別衝突：產品呼叫在 file: `governance/eval/test_review_convergence.py:217`，第一個斷言在 file: `governance/eval/test_review_convergence.py:218`。
- 十萬零一筆：file: `governance/eval/test_review_convergence.py:229` 寫 fixture，file: `governance/eval/test_review_convergence.py:230` 的 `assertRaises` 本身就是結果斷言，沒有先確認實際筆數或檔案大小。
- 129 字 receipt 測試有在產品呼叫前檢查長度及真實檔案，符合合約，見 file: `governance/eval/test_review_convergence.py:292`、file: `governance/eval/test_review_convergence.py:293`。

預期出處：file: `governance/review-reports/code-review-convergence-eval/r3-graph-lens.txt:12`。

完整快照引句：

引句:「self.assertNotIn(chr(point), result.stdout)」  
file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:962`

引句:「self.assertTrue(x["conflicting_tokens"])」  
file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:973`

引句:「def test_short_record_amplification_is_rejected(self):」  
file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:981`

最小翻紅檢查在 repo 根以 Python 3.14 AST 讀取固定測試源，尋找產品呼叫前、且不是 `assertRaises` 的獨立斷言。原始輸出：

```text
test_render_control_characters_without_changing_data: product_line=199 independent_precondition_assertions=[]
test_token_identity_keeps_json_types_and_ignores_key_order: product_line=217 independent_precondition_assertions=[]
test_short_record_amplification_is_rejected: product_line=231 independent_precondition_assertions=[]
missing_precondition=test_render_control_characters_without_changing_data,test_token_identity_keeps_json_types_and_ignores_key_order,test_short_record_amplification_is_rejected
RC=1
```

建議分別增加：

- 控制字元：執行 CLI 前驗證磁碟 JSON 解碼後確實含目標 C1／bidi 字元。
- token 型別：執行 `build_cohort` 前驗證 `tokens` 兩值型別不同。
- 十萬零一筆：執行 `read_ledger` 前驗證檔案大小或實際為 100001 條記錄。

配對證據與歸因邊界：

- case source：修後固定 `governance/eval/test_review_convergence.py`，SHA `03ebe1…27355`；檢索來源見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:48`。
- 修前 argv、cwd、執行狀態及前提在 file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:6`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:13`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:15`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:18`；載入模組 SHA `f1e5df…933c`，見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:1`。rc=1；三案均 FAIL，見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:10`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:12`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:13`。
- 修後 argv、cwd、執行狀態及前提在 file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:28`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:35`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:37`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:40`；載入模組 SHA `4b8a83…822e`，見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:1`。rc=0；三案均 ok，見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:10`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:12`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:13`。
- 環境兩端相同：Python 3.14.6、Darwin、network=none，見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:19`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:41`。
- 來源閉包前提為 `ce4c30f9…`、無 alternates、修後 commit/tree 相符，見 file: `governance/review-reports/code-review-convergence-eval/r3-source-restore.json:3`、file: `governance/review-reports/code-review-convergence-eval/r3-source-restore.json:5`、file: `governance/review-reports/code-review-convergence-eval/r3-source-restore.json:7`、file: `governance/review-reports/code-review-convergence-eval/r3-source-restore.json:8`。
- 配對結果證明產品修補是 fail→pass，但不能替代測試內的前置斷言。token／短行測試是本次新增，測試守衛缺陷可歸因本修補；控制字元測試是既有測試在本輪擴寫，屬於隨修補帶入但非全新產生的守衛債。未發現可歸因本修補的產品回歸。

修補三問：

1. 原問題已修好：四個固定案例由修前 FAIL 變為修後 ok，包括控制字元、短行放大、token 型別及 129 字路徑；見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:10`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:12`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:13`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:24`，以及 file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:10`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:12`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:13`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:24`。
2. 原正常案例保留：同一固定來源共 23 案，修前只有上述四案失敗，修後 23 案全過；見 file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:63`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:65`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:27`、file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:29`。此結論僅限這一測試家族。
3. 新增問題：有一項測試守衛缺陷，即 F1；沒有觀察到同家族產品行為回歸。

硬合約逐條狀態：

1. 修 bug 翻紅釘前置斷言：違反，見 F1。
2. bound-tests gate 真跑及 rc：未執行 `lumos code-loop check`，未驗。
3. canary record 持久化讀回：未驗。
4. canary second 不影響 gate：未驗。
5. guard-kill rc 優先序：未驗。
6. guard-kill JSON 純度：未驗。
7. 三支 PowerShell ASCII/BOM：Windows 原生能力不可得，跳過。
8. PowerShell `$Args` 保留名：Windows 原生能力不可得，跳過。
9. CLAUDE.md sentinel 外 byte-equal：未驗。
10. 精簡安裝冪等：未驗。
11. 完整區塊 byte-level 備份：未驗。
12. 安裝 manifest 身分證：未驗。
13. 安裝三層目標守衛：未驗。
14. `.cmd` 直譯器選擇：Windows 原生能力不可得，跳過。
15. `lumos`／`lumos.cmd` 碰撞偵測：Windows 原生能力不可得，跳過。
16. 卸載 bin 內容比對：未驗。
17. 四項清理獨立：未驗。
18. skill 目錄先備份：未驗。
19. CLAUDE.md 精確還原：未驗。
20. `.cmd` 獨立移除：Windows 原生能力不可得，跳過。
21. 卸載 manifest 清理：未驗。
22. search 預設排除 superseded、不排 stale：未驗。

py-memory 表態：tension；chosen suggested。十六 MiB／十萬筆只是輸入約束，不是程序總 RAM 保證；檔案也明確如此說明，見 file: `governance/eval/review_convergence.md:28`。回看日期：2026-10-21。

來源核對：bundle SHA 實測為 `b8aadb…6741`，與 file: `governance/review-reports/code-review-convergence-eval/r3-source-restore.json:2` 相同；兩端模組及固定測試源 SHA 與配對日誌相同。還原目錄是無 Git metadata 的普通完整快照，因此沒有把其中 `git rev-parse HEAD` 的 harness 失敗算產品失敗。

最高等級：major  
阻擋條數：1  
實讀：1651 行完整材料（AGENTS 97、CLAUDE 101、skills 327、graph lens 69、module 560、tests 469、docs 28），另僅定向抽取綁定欄位與案例日誌；未全文讀取 r1/r2 報告、intake 或完整 repair patch。  
未驗範圍：Windows 原生行為、真實模型試輪、其他測試家族及上述未涉及合約；單一家族結果不保證無回歸。