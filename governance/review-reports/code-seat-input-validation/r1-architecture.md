severity: clean

零 finding；未發現具體 delta 缺陷。

架構三問：

1. 分層依賴方向：通過。輸入形態驗證留在 CLI 邊界 `scripts/lumos:23294`，完成全部項目驗證後才進入材料讀取迴圈 `scripts/lumos:23323`。鄰居 `cmd_quote_check`、`cmd_refcheck` 也各自在入口處理讀取與 rc2，見 `scripts/lumos:23070`、`scripts/lumos:40076`；沒有跨層直呼。
2. 命名與錯誤返回：通過。`dispatch`、`materials`、`materials[i]` 診斷具體，`ValueError` 統一在 `scripts/lumos:23311` 轉為 stderr 與 rc2；合法觀測仍於 `scripts/lumos:23364` 回 rc0，與鄰居慣例一致。
3. 是否形成第二套做法：否。沿用既有 `json.loads`、`ValueError`、入口 try/except，只增加標準函式庫 `os.fsencode`；沒有另建 schema 或平行驗證層。

四條驗收逐條比對：

- S1：非物件 dispatch、錯形態 materials 於 `scripts/lumos:23297-23313` 回 rc2；`scripts/test_lumos.py:34012-34035` 覆蓋普通與 `-O`、無 traceback／假 JSON。
- S2：非字串、空字串、NUL、平台不可編碼字串於 `scripts/lumos:23304-23310` 擋下；材料直到 `scripts/lumos:23323` 才讀。讀序證據在 `scripts/test_lumos.py:34087-34109`。
- S3：缺省／null／空清單於 `scripts/lumos:23299-23322` 保持 vacuous rc0；中文含空白路徑由 `scripts/test_lumos.py:34051-34060` 覆蓋。
- S4：合法清單仍走既有 unreported、out_of_scope 與 ledger 路徑 `scripts/lumos:23323-23364`；`scripts/test_lumos.py:34061-34069` 證明仍為 rc0 且帳本欄位不變。

相容性核對：

- 重複 JSON 鍵仍直接交給 Python `json.loads`，未加入唯一鍵政策：`scripts/lumos:23296`。
- 未知 metadata 仍被忽略；`round`、`seat`、`lens` 輸出不變：`scripts/lumos:23314-23315`。
- 原有中文、空清單、觀測性回傳與 ledger 語意未收窄。
- 未加入 Windows 專用處理，符合本次射程。

固定圖譜逐條：

- `Systems/design-loop`：本輪 ID 為 `code-` 前綴，不觸發設計審材料規則；計劃仍為 `.md`，S1–S4 均有測試綁定。
- `Systems/lumos-cli-read`：search 過濾路徑未觸及。
- `Systems/bound-tests-gate`：閘門實作未觸及；三個新增方法均存在。
- `Systems/guard-kill`：rc 優先序與 JSON 純度未觸及。
- `Systems/授權與歸屬`：授權白名單、檔頭及 vendored 集合未觸及。
- `Systems/測試假綠形態`：測試先證明 JSON 現場形態與材料存在，並直接觀測真入口的讀取順序，符合前置斷言要求。
- `Systems/lumos-cli-lifecycle`：re-inject 路徑未觸及。

驗證：

- HEAD 已核對為 `fd255ce01f23460a622b17312dbdf5448d9cbf67`；baseline 是有效 commit。
- 子集 runner 在測試開始前因唯讀環境沒有可用臨時目錄而退出，未把它誤報成測試結果。
- 改以記憶體載入真 `cmd_seat_check` AST，在 optimize 0／1 下完成 18 個錯形態、讀序、vacuous、相容與 ledger 探針，全部通過。

已讀：

- `r1-source.patch`：180/180 行，SHA-256 `fb2c450c8e7bc3fa6f384d2afef6567496d38a5737b052795e3ee8f7947eeb17`
- `r1-graph.patch`：233/233 行，SHA-256 `4ff3ded836568f4c96ed9b60f6f3e1efa1ecdb262ad51be781db9150266b0033`
- `r1-snapshot.patch`：僅完整指紋，4597 行，SHA-256 `6486f72075f68342536b486f3eea14dbaafcdaf51b1223306609946d7347f930`
- 固定圖譜：7 個有內容節點逐條核對
- 最高等級：clean
- blocking 數：0