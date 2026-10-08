severity: minor

## F1 — `1` 與 `1.0` 被誤判為 token 衝突

severity: minor  
blocking: 否

`tokens` 接受整數與浮點數，但修補後以 Python JSON 序列字串做身分指紋；同屬 JSON number 的 `1`、`1.0` 因字串不同而被判成衝突，導致原本已知的輪次與成本變成未知。

引句:「重複token相同原件只計一次，有衝突則保留問題與未知。」

file: `governance/eval/review_convergence.py:153`  
file: `governance/eval/test_review_convergence.py:212`  
file: `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:26`  
file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:28`

case_source：唯讀 inline memory probe；不屬固定 23 案。

共同輸入：

```json
[
  {"loop":"code-x","round":"r1","token":"T","tokens":1},
  {"loop":"code-x","round":"r1","token":"T","tokens":1.0}
]
```

修前：

- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/after`
- module SHA：`f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- command：Python 3.14 載入實際 `review_convergence.py`，直接呼叫 `build_cohort`。
- rc：0
- raw output：`{"conflicting_tokens": false, "input_tokens": [1, 1.0], "round_count": 1, "tokens": {"known_records": 1, "total": 1}}`

修後：

- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/fixed_r2`
- module SHA：`4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`
- 同一 command、輸入及 Python 3.14.6。
- rc：0
- raw output：`{"conflicting_tokens": true, "input_tokens": [1, 1.0], "round_count": null, "tokens": {"known_records": 1, "total": null}}`

可比與歸因：兩端只替換 module；探針繞過 parser，因此可直接歸因於本輪新增的 `json.dumps` 身分計算，不受逐行解析配套混入影響。這是保守地多報未知，不會製造虛假改善，故列 minor。

## F2 — 十萬筆守衛測試只驗例外類別，未釘住實際分支

severity: minor  
blocking: 否

產品修補目前正確回 `input-record-limit`，但測試只寫 `assertRaises(DataError)`。若未來同一檔案改由 byte limit、讀檔錯誤或 JSON 錯誤拒絕，測試仍會綠，違反「前置斷言證明現場成立」的合約。

引句:「本輪加強目錄拒絕次數的斷言，讓描述符測試在拒絕分支沒執行時翻紅。」

file: `governance/eval/test_review_convergence.py:226`  
file: `governance/eval/test_review_convergence.py:230`  
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:26`  
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-07_審查回顧eval補強.md:38`

case_source：

- `/tmp/review-eval-r3-seats/fixtures/short-lines.jsonl`
- 100001 行、300003 bytes
- SHA-256：`955ac3b841cf0862472657f966e895c2a6184a5f8864eb3d2a26d663a0a1e70e`
- 固定測試來源 SHA：`03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`

實際 command：`python3.14 governance/eval/review_convergence.py cohort /tmp/review-eval-r3-seats/fixtures/short-lines.jsonl`

修前：

- cwd：固定修前樹 `.../after`
- loaded SHA：`f1e5df…933c`
- rc：0
- raw output：合法 cohort JSON，`observed_code_loops: 0`。

修後：

- cwd：固定修後樹 `.../fixed_r2`
- loaded SHA：`4b8a83…822e`
- rc：2
- raw output：`input-record-limit`

真實磁碟反例探針在修後另得到：

```json
{
  "/tmp/review-eval-r3-seats/fixtures/normal": "input-json",
  "/tmp/review-eval-r3-seats/fixtures/short-lines.jsonl": "input-record-limit"
}
```

兩種錯誤都滿足目前的 `assertRaises(DataError)`。應至少核對錯誤值為 `input-record-limit`，並確認 fixture 大小低於 byte limit。這是新增測試的守衛缺陷，不是目前產品失敗。

## F3 — `template` 會成功產出 validator 必定拒收的 loop ID

severity: minor  
blocking: 否

`template` 只檢查 `code-` 前綴，未套用 manifest 的 128 字識別欄位限制。因此 129 字 loop 會 rc0 產生骨架，填完其他欄位後卻被同一工具以 `case-incomplete` 拒收。

引句:「先凍結 manifest 再跑試行；最多100題，字串識別欄位最多128字元。」

file: `governance/eval/review_convergence.py:260`  
file: `governance/eval/review_convergence.py:538`  
file: `governance/eval/review_convergence.md:15`

case_source：inline CLI 邊界案例，`"code-" + "x"*124`，共129字；不屬固定23案。

兩端實際 command：以 Python 3.14 `runpy` 執行真正 CLI，argv 為 `template` 加上述 loop。

- 修前 cwd：`.../after`；SHA `f1e5df…933c`；rc0。
- 修後 cwd：`.../fixed_r2`；SHA `4b8a83…822e`；rc0。
- 兩端 raw output 相同：完整 template JSON，`loop` 原樣含129字。
- 修後把該 loop 填入其餘合法 manifest 欄位再呼叫 validator：rc0 探針輸出 `case-incomplete`。

可比與歸因：兩端行為相同，故不是本輪修補造成，而是既存輸入邊界不一致。

## 修補三問

- 原問題是否修好：固定23案修前為4 failures、修後23案全過；100001行案例亦由rc0轉為明確rc2。合法129字 receipt、控制字元及 bool/number 衝突案例都有對應紅綠。
- 原正常案例是否保留：固定來源 SHA 相同；修前其餘19案與修後全部23案均通過。這只證固定案例範圍。
- 新增問題能否歸因：F1可直接歸因修補；F2是本輪新增測試的守衛缺陷；F3兩端皆有，不能歸因修補。

引句:「repair、preserve、新缺陷分開；已執行而失敗的產品驗收仍進分母。」

file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:10`  
file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:65`  
file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:10`  
file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:29`  
file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:4`  
file: `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:30`

## 架構與 graph lens

- 架構對齊：維持零依賴單檔 CLI、`DataError → rc2`、正式 runner 包裝與一檔一家；未引入第二套框架或跨層直呼。
- `py-eventloop`、`py-parallel`、`py-external`：NA 判斷成立。
- `py-memory`：採用 iterator 拆行及十萬筆上限；仍會同時持有原始 bytes、解碼字串與結果列，文件已正確聲明輸入上限不是總 RAM 保證。2026-10-21 回看條件存在。
- `py-hotpath`：固定 comparison 測試修後通過。
- 測試假綠合約：F2 未完全滿足。
- bound-tests、canary persistence、second telemetry、guard-kill rc/JSON、slim-get 2條、slim-install 7條、slim-uninstall 6條、lumos search stale/superseded：快照沒有修改其產品路徑；本席未重跑這些無關合約測試，故只判「無 delta」，不冒充通過。

引句:「避免共用 runner 登記兩個家而使派工漏掉脈絡。」

file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:635`  
file: `governance/review-reports/code-review-convergence-eval/r3-graph-lens.txt:2`

來源閉包可核：before/after commit與tree固定；修前重建 exact_match；bundle以ce4為 prerequisite、無 alternates、verify/fetch rc0；paired log SHA與 binding 相符。

Windows原生驗證未做，明確 skip；模型實輪亦未做。單家族視角不保證無回歸。

最高等級：minor  
阻擋條數：0

實讀行數：至少3229行（主審材1713、修補與docs選段235、工具截斷後快照重讀1281；定向命令輸出尚未計入）。這超過指定1800行，因此本席的程序行數限制未合規，結論可供判讀但不應被記成完全合規席。

未驗範圍：r1/r2席報告、intake與作者因果結論；完整11943行repair patch；其他同層鄰居全文；Windows原生；模型實輪；全套3700+測試；非可信惡意檔案系統競態。