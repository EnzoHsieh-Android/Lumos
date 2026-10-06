severity: clean

零 finding。

### 架構對齊三問

1. 分層依賴方向：符合。驗證留在 CLI 收貨邊界，完成後才進材料讀取，沒有跨層直呼。  
   file: `scripts/lumos:23294`  
   file: `scripts/lumos:23323`  
   鄰居同樣在命令入口處處理輸入與 IO：  
   file: `scripts/lumos:23070`  
   file: `scripts/lumos:40076`

2. 命名與錯誤返回：符合。`disp`／`materials` 延續原命名；具體欄位錯誤轉成 `ValueError`，統一由既有分支回 rc2、stderr 診斷且不輸出觀測 JSON。  
   file: `scripts/lumos:23297`  
   file: `scripts/lumos:23311`  
   鄰居的不可讀輸入亦回 rc2：  
   file: `scripts/lumos:23073`  
   file: `scripts/lumos:40077`

3. 是否第二套做法：否。delta 沿用 `json.loads`、`isinstance`、`ValueError` 與既有命令邊界，未新增 schema 引擎或平行入口。現有 `_home_cache_read` 是私有快取的 fail-soft 讀取，錯誤回 `None`，不適合外部派工單的 fail-loud 契約。  
   file: `scripts/lumos:23293`  
   file: `scripts/lumos:41839`

### 四項驗收條款

- S1：非物件 dispatch、非清單 materials 均在 `.get`／材料讀取前回 rc2；普通與 `-O` 測試皆有覆蓋。  
  file: `scripts/lumos:23297`  
  file: `scripts/test_lumos.py:34012`

- S2：逐項拒絕非字串、空字串、NUL、平台不可編碼路徑；完整預檢結束後才讀材料。ledger 不變與真入口讀序均有斷言。  
  file: `scripts/lumos:23304`  
  file: `scripts/lumos:23323`  
  file: `scripts/test_lumos.py:34014`  
  file: `scripts/test_lumos.py:34117`

- S3：缺省、null、空清單仍為 rc0 vacuous；中文含空白路徑仍走實際材料錨定。  
  file: `scripts/lumos:23299`  
  file: `scripts/lumos:23316`  
  file: `scripts/test_lumos.py:34051`

- S4：合法輸入的漏材料、引句越界仍只觀測並回 rc0；ledger 的 round／seat／quote／reason 格式未改。  
  file: `scripts/lumos:23329`  
  file: `scripts/lumos:23344`  
  file: `scripts/lumos:23364`  
  file: `scripts/test_lumos.py:34061`

預設 `json.loads` 保留 Python 對重複鍵的既有處理；未知 metadata 未被拒絕；可編碼 surrogateescape 路徑仍被接受。

### 固定圖譜逐條核對

- `Systems/design-loop`：處置閘材料副檔名與條款綁測試規則未受修改。
- `Systems/lumos-cli-read`：search 的 superseded／stale 過濾路徑未受修改。
- `Systems/bound-tests-gate`：固定席合約測試執行與 rc1 規則未受修改。
- `Systems/guard-kill` rc 優先序：未受修改。
- `Systems/guard-kill` JSON 純度：未受修改。
- `Systems/授權與歸屬` vendored 授權檔禁令：未受修改。
- `Systems/授權與歸屬` SPDX／MIT 檔頭：未受修改。
- `Systems/測試假綠形態`：新增測試含現場成立前置斷言，並以 AST 取得真 `cmd_seat_check`、觀測真實讀序。
- `Systems/lumos-cli-lifecycle`：re-inject sentinel 外 byte-equal 契約未受修改。

### 卷證與執行

- 固定 HEAD raw ref：`b12551e120004a621931df11bc7157456d78a30e`，吻合。
- 已完整逐行讀 `r3-source.patch` 213 行、`r3-graph.patch` 221 行。
- `r3-snapshot.patch` 僅做完整 SHA-256：`8513680e0a6e9591a53b95eec0abf4e04304406f3a9d0de8c30dac23586d5e9b`，未展開。
- 實際子集命令因唯讀環境無可用暫存目錄，在任何斷言執行前以 `FileNotFoundError: No usable temporary directory found` 結束；未冒充綠燈。
- 另以記憶體載入現行 AST，普通與 `optimize=1` 各驗 top-level list、尾端物件、不可編碼 surrogate、缺省、null、有效材料，共 12 組；rc、stdout/stderr 與材料讀序均符合預期。

最高等級：clean。blocking 數：0。