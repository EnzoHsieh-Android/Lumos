severity: clean

零 finding；未發現具體 delta 缺陷。

四項驗收條款：

- S1：非物件 dispatch、錯型 `materials` 均由明確檢查轉成 rc2；stderr 有欄位診斷，不輸出 traceback 或觀測 JSON。
- S2：逐項檢查型別、空字串、NUL 與 `os.fsencode`；完整清單驗完後才進入材料讀取，且不依賴會被 `-O` 移除的 `assert`。
- S3：缺省、`null`、`[]` 仍為 vacuous rc0；中文及空白路徑維持正常。
- S4：合法 dispatch 的漏材料、引句越界仍是 rc0 觀測；ledger 欄位與追加時機未改。

相容性核對：

- Python 預設重複 JSON 鍵行為未改，未引入唯一鍵政策。
- 未知欄位及 `round`、`seat`、`lens` 輸出未收窄。
- 可編碼的 surrogateescape 路徑保留；不可編碼 surrogate 轉為索引化 rc2。
- Windows 行為未被本次變更宣稱解決。
- 半寫 JSON 在材料讀取及 ledger 寫入前失敗；無新衍生格式、時間語意、遷移或不可逆操作。

固定圖譜逐條核對：

- `design-loop`：本次不改處置閘；計劃仍是 `.md`，S1–S4 都有測試綁定。
- `lumos-cli-read`：未碰 search／superseded／stale 行為。
- `bound-tests-gate`：未改合約測試執行、阻擋或記帳語意。
- `guard-kill` 兩條：未碰 rc 優先序或 JSON stdout 純度。
- `授權與歸屬` 兩條：未改 vendored 白名單、授權檔或主程式檔頭。
- `測試假綠形態`：新測試包含真實檔案／真入口前置斷言、材料讀取觀測及已提供的翻紅對照，未見只測空殼路徑。
- `lumos-cli-lifecycle`：未碰 re-inject 或 sentinel 外內容。
- 其餘僅列名節點未據此推導額外結論。

驗證情況：

- 定向測試框架因唯讀環境沒有可寫暫存目錄，在收集前以 `FileNotFoundError` 結束；未宣稱該次測試通過或失敗。
- 另以記憶體直接抽取固定來源中的真 `cmd_seat_check` AST：普通與 `optimize=1` 共驗證 30 個錯輸入、6 個 vacuous、2 個有效輸入，以及讀取順序與 fsencode 邊界，全部通過。
- `LUMOS-ROLE-CARDS: on` 僅依派工內容執行，未宣稱 CLI 已自動附卡。

已讀：

- `r3-source.patch`：213/213 行，逐 hunk。
- `r3-graph.patch`：221/221 行，逐 hunk。
- `r3-snapshot.patch`：僅完整指紋；SHA-256 `8513680e0a6e9591a53b95eec0abf4e04304406f3a9d0de8c30dac23586d5e9b`。
- 固定圖譜：所有貼有內容的九條 invariant 均逐條核對。

最高等級：clean  
blocking 數：0