severity: clean

零 finding。

架構三問

1. 分層依賴方向：一致。驗證留在 CLI 收貨邊界，只依賴標準庫，未跨層直呼。  
   file: `scripts/lumos:23293`  
   鄰居對照：`cmd_quote_check`、`cmd_refcheck` 同樣在命令入口完成讀取與 rc2 轉換。  
   file: `scripts/lumos:23068`  
   file: `scripts/lumos:40075`

2. 命名與錯誤返回：一致。診斷精確指出 `dispatch`、`materials` 或 `materials[i]`；解析、形態與編碼錯誤統一走既有「擋下」rc2，合法觀測仍 rc0。  
   file: `scripts/lumos:23297`  
   file: `scripts/lumos:23311`  
   file: `scripts/lumos:23364`

3. 是否形成第二套做法：否。沒有新增 schema 引擎或平行入口；仍沿用命令邊界的局部 `ValueError` 驗證，以及既有 `_quote_rows`／`_quote_norm` 錨定實作。  
   file: `scripts/lumos:23304`  
   file: `scripts/lumos:23335`

四項驗收逐條比對

- S1：非物件 dispatch、非 list/null materials 均在初始 try 內轉 rc2；無觀測 JSON。符合。  
  file: `scripts/lumos:23294`  
  file: `scripts/test_lumos.py:33999`

- S2：逐項完成型別、空字串、NUL、`os.fsencode` 驗證後，才從第 23323 行開始讀材料；ledger 更晚才寫。普通與 `-O`、有效首項後接壞尾項皆有覆蓋。符合。  
  file: `scripts/lumos:23304`  
  file: `scripts/lumos:23323`  
  file: `scripts/test_lumos.py:34106`

- S3：缺省、null、空清單均正規化成 vacuous rc0；中文含空白路徑仍能實際錨定。可編碼的 surrogateescape 路徑也未被一律拒絕。符合。  
  file: `scripts/lumos:23299`  
  file: `scripts/test_lumos.py:34039`  
  file: `scripts/test_lumos.py:34073`

- S4：漏材料、引句越界仍只觀測並回 rc0；ledger 保留 round、seat、quote、reason。符合。  
  file: `scripts/lumos:23329`  
  file: `scripts/lumos:23344`  
  file: `scripts/test_lumos.py:34061`

相容性核對

- `json.loads` 未加唯一鍵 hook，重複 JSON 鍵仍維持 Python 預設。
- round／seat／lens 與未知 metadata 未新增形態限制。
- report、dispatch 先讀；所有 dispatched material 都在全清單驗完後才讀。
- 本次沒有擴張 Windows 支援。

固定圖譜逐條

- `Systems/design-loop`：未改 loop 分類、審材副檔名或條款綁定規則。
- `Systems/lumos-cli-read`：未碰 search 過濾。
- `Systems/bound-tests-gate`：未碰合約測試執行或 blocked 判定。
- `Systems/guard-kill`：未碰 rc 優先序或 JSON 純度。
- `Systems/授權與歸屬`：未碰 vendored 清單、授權檔或檔頭。
- `Systems/測試假綠形態`：新測試具現場前置斷言，且直接走真 CLI／真入口。  
  file: `scripts/test_lumos.py:34022`  
  file: `scripts/test_lumos.py:34085`  
  file: `scripts/test_lumos.py:34122`
- `Systems/lumos-cli-lifecycle`：未碰 reinject。

卷證範圍

- 完整讀取 `r2-source.patch`：213 行，SHA-256 `151f11d7d30985bdb8f121f5c1f6d8323ed1f2cb42b5cbb506260628df49727a`
- 完整讀取 `r2-graph.patch`：221 行，SHA-256 `a0bb88fdaa37100e32463e3841d34c21a5263754e64983f54dbc51f298a67bb2`
- `r2-snapshot.patch` 僅取完整指紋：12,645 行、1,005,791 bytes，SHA-256 `8578c7f7ccf5f415b64e4f34d7ae3f147cae09379b348d3832b377197fe8ad4e`
- HEAD 符合固定版本 `1d9f4720a914d22c1cc0500bdd5974771e0161f2`
- 未讀 r1 席報告或封存設計報告；未重跑測試，提供的綠燈數字未作為結論依據。

最高等級：clean  
blocking 數：0