severity: minor

審查結論：原四個問題已修好，原先通過的 19 案全部保留；找到一個修前、修後都存在的 `template` 輸入邊界問題，不能歸因於本輪修補。

F1 — `template` 接受超過 manifest 上限的 loop

severity: minor  
blocking: 否

`template` 只檢查 `code-` 前綴，會以 rc=0 輸出 129 字元的 loop；但同一 loop 放進 manifest 時，`text_field` 的 128 字元上限必定拒收。模板因此可能產生無法直接補齊使用的骨架。

完整快照引句：「if not args.loop.startswith("code-"):」  
file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:728

產品佐證：

- 前綴檢查未套用 `text_field`：file: governance/eval/review_convergence.py:538
- manifest 的字串上限為 128：file: governance/eval/review_convergence.py:260
- manifest 案例以該限制驗證 loop：file: governance/eval/review_convergence.py:306
- 規格期望 template 產生待補案例骨架：file: docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:26

同案例 input：`code-` 加 124 個 `x`，總長 129。  
expected：拒收並回 rc=2；至少不得輸出一份已知 loop 欄位不符合 manifest schema 的骨架。  
case_source：現有 template 測試只使用 `code-x`，file: governance/eval/test_review_convergence.py:235

修前實跑：

- command：`/opt/homebrew/opt/python@3.14/bin/python3.14 governance/eval/review_convergence.py template <code-+124*x>`
- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/after`
- 載入 SHA：`f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- 前提：Darwin、Python 3.14、無網路
- rc：0
- 原始輸出：`input_length=129`，JSON 內保留完整 129 字元 loop。

修後實跑：

- command：同上
- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/fixed_r2`
- 載入 SHA：`4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`
- 前提：同上
- rc：0
- 原始輸出：與修前相同。

可比與歸因界線：兩端同案例、同命令皆 rc=0，故這是既存產品缺陷，不是 cd0ae310 新增的回歸。

F2 — template 測試守衛沒有覆蓋自身輸入上限

severity: minor  
blocking: 否

這是測試守衛缺陷，與 F1 的產品行為分開計。現有測試直接呼叫 `case_template("code-x")`，沒有走 CLI 的前綴檢查，也沒有覆蓋 128/129 邊界。

完整快照引句：「x = ev.case_template("code-x")」  
file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:991

file: governance/eval/test_review_convergence.py:234  
file: governance/eval/review_convergence.py:538

同案例、命令、cwd、載入 SHA、rc 與原始輸出同 F1。建議新增 128 字元成功與 129 字元 rc=2 的 CLI 邊界案。

已驗正向行為

共同 case_source：`cd0ae310ccf1609a56a2552374eab47b13c55882:governance/eval/test_review_convergence.py`，SHA `03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`。完整 argv、cwd、環境及輸出指紋見 file: governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:2。

- 顯示控制字元：輸入含 C1、雙向控制字及 U+2028；預期 stdout 不含原始控制字且 JSON round-trip 不改資料。修前 FAIL、修後 ok。  
  引句：「self.assertNotIn(chr(point), result.stdout)」  
  file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:962  
  file: governance/eval/test_review_convergence.py:193

- 十萬筆短行放大：輸入 100001 行 `{}`；預期 `DataError`。修前 FAIL、修後 ok。  
  引句：「if len(rows) >= 100000:」  
  file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:314  
  file: governance/eval/test_review_convergence.py:226

- token 型別衝突：同 token 分別帶 `0/false`、`1/true`；預期標記衝突且成本未知。修前 FAIL、修後 ok。  
  引句：「self.assertTrue(x["conflicting_tokens"])」  
  file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:973  
  file: governance/eval/test_review_convergence.py:212

- 129 字元真實 receipt 路徑：預期有效 trial。修前 FAIL、修後 ok。  
  引句：「self.assertTrue((root / name).is_file())」  
  file: governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:1048  
  file: governance/eval/test_review_convergence.py:285

paired 原始結果：

- 修前：rc=1，`FAILED (failures=4)`。file: governance/review-reports/code-review-convergence-eval/r3-paired-before.log:65
- 修後：rc=0，23 案全過。file: governance/review-reports/code-review-convergence-eval/r3-paired-after.log:27
- 原先正常案例：修前 19 個 ok，修後 23 個 ok，沒有任何修前 ok 案在修後消失。

硬合約核對

- `py-eventloop na`：符合，同步 CLI，未見事件迴圈。
- `py-parallel na`：符合，未見並行工作。
- `py-external na`：符合，產品入口未呼叫網路或資料庫。
- `py-memory tension / chosen suggested`：維持原表態。16 MiB 輸入與十萬筆限制不是總 RAM 保證；仍會整份 decode、解析並保留 rows。依既定條件於 2026-10-21 重新核對實輪資料量／記憶體。
- `py-hotpath satisfied`：固定來源中的 comparison 案皆通過；沒有另跑會寫暫存資料的正式 runner。
- 測試假綠合約：描述符拒絕案含 `rejected == 80` 前置斷言，且 paired 兩端皆通過。file: governance/eval/test_review_convergence.py:181
- bound-tests、canary、guard-kill、slim-get/install/uninstall、lumos-cli-read 等間接合約未在本席重跑，不能冒充已驗。
- Windows 原生驗證依指示排除，未宣稱 Windows 相容性通過。

來源閉包

r3 bundle 記錄顯示前置 commit 為 `ce4c30f9…`、空物件庫無 alternates、fetch rc=0；還原 commit/tree 分別為 `cd0ae310…`／`e588725a…`。修前重生記錄為 `ce4c30f9..c909bf98`、`exact_match=true`。這些只用作來源身分，不作修補因果證據。

實讀行數：1,397 行逐行正文／程式／測試／log，另有 33 個定向匹配或 JSON 欄位，合計 1,430。未驗範圍：module 426–517、tests 361–469、完整 repair/snapshot 其餘內容、Windows 原生、模型實輪及其他 graph-lens 間接合約。單一邊界家族視角不保證沒有其他回歸。

最高等級：minor  
阻擋條數：0