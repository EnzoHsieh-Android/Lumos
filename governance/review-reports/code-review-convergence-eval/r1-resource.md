severity: major

ID: RES-01
severity: major
blocking: 是
逐字引句:「with os.fdopen(fd, "rb") as f:」
file: `governance/eval/review_convergence.py:24`

`os.open()` 成功後，若 `os.fdopen()` 因輸入是目錄而在進入 `with` 前失敗，fd 不會被關閉。大量非法 receipt 可耗盡 fd，令後續正常檔案也被誤判為不可讀。

最小實驗：將 fd 上限設為 64，連續讀目錄 80 次，再讀正常 Python 檔。

實際輸出：

```text
nofile_soft=64 directory_attempts=80 errors={'input-unreadable': 80}
subsequent_regular_file=FAIL input-unreadable
```

應先對原始 fd 執行 `fstat`，並以 `try/finally` 保證 `fdopen` 尚未取得所有權時也會關閉。

ID: RES-02
severity: major
blocking: 是
逐字引句:「先凍結 manifest 再跑試行；最多1000題。」
file: `governance/eval/review_convergence.py:193`
file: `governance/eval/review_convergence.py:441`
file: `governance/eval/review_convergence.md:15`

文件及 validator 接受 1000 題、每題每組 100 次，但 CLI 將 manifest 限為 256 KiB、trial 索引限為 16 MiB。即使用緊縮 JSON、一字元 receipt 路徑，合法邊界資料仍超限，尚未比較便會回 `input-too-large`。

純記憶體最小實驗實際輸出：

```text
manifest_validator=PASS bytes=388000 limit=262144
trial_index_records=200000 bytes=29262000 limit=16777216
max_dataset_fits_cli_caps=False
rc=1
```

因此宣告的最大資料量不可達；需提高／重新推導上限，或改成串流解析並同步調低公開案例與 repeat 上限。

ID: RES-03
severity: minor
blocking: 否
逐字引句:「c = next((c for c in m["cases"] if key and c["id"] == key[0]), None)」
file: `governance/eval/review_convergence.py:262`
file: `/tmp/review-eval-disp.json:31`

每筆 trial 都重新線性掃描最多 1000 個 case。200,000 筆邊界資料平均約做一億次 ID 比對；純記憶體、尚未進行 receipt I/O 的量測已耗時：

```text
compare_seconds=5.688 invalid_records=200000 expected_trials=200000
```

這反駁 `py-hotpath: satisfied` 對「成對結果使用字典索引」的完整性：彙總使用字典，但驗證入口沒有。離線工具未訂延遲合約，故列 minor；可在 `compare` 預建 `cases_by_id`。

圖譜硬合約逐條答：`/tmp/review-eval-graph-lens.txt` 只附受影響節點名稱與合約類別，沒有自動附加任何硬合約原文、綁定測試狀態或逐條問題；本席沒有可逐條判答的合約正文，也未由節點名稱自行臆測。

成效宣告邊界：未發現誇大。文件與 Verification 均明說合成測試不是模型效果，且尚無真實 baseline/candidate 實輪。

驗證限制：指定暫存目錄因執行沙箱唯讀而無法建立；以上實驗均以純記憶體或既有唯讀檔完成。repo 起訖狀態相同，本席未寫入。

最高等級: major
阻擋條數: 2