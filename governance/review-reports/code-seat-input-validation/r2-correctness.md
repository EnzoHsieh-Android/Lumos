severity: clean

零 finding。未發現此 delta 新增的具體缺陷。

四項驗收條款：

- S1：非物件 dispatch、錯型 materials 均回 rc2，無 traceback 或觀測 JSON。
- S2：每項完成非空、NUL、型別及 `os.fsencode` 驗證後才讀取材料；普通與 `-O` 邏輯一致，錯誤發生於帳本寫入前。
- S3：缺省、null、空清單維持 vacuous rc0；中文及空白路徑不受限。
- S4：有效派工的漏報、越界仍為觀測性 rc0，既有帳本欄位不變。
- 重複 JSON 鍵仍採 Python 預設後值覆蓋；未知 metadata 未被收窄。

資料狀態五問：

- 新舊互讀：既有缺省、null、list 格式均相容。
- 半寫：讀檔或 JSON 解析失敗在材料與帳本操作前回 rc2。
- 衍生資料：壞輸入不產生觀測 JSON，也不改越界帳。
- 時間：未新增快取、時序或期限狀態。
- 不可逆：只有合法越界結果會走既有 append；錯輸入不會寫入。

固定圖譜逐條核對：

- `design-loop`：未改變 `.md` 計劃材料及綁定測試合約。
- `lumos-cli-read`：未碰 search 的 superseded/stale 過濾。
- `bound-tests-gate`：新測試方法均存在，沒有改變 bound-tests 判定。
- `guard-kill`：rc 優先序及 JSON 純度未受影響。
- `授權與歸屬`：未改 vendored 清單或檔頭授權。
- `測試假綠形態`：測試包含現場前置斷言、真入口讀序觀測及普通／`-O` 對照。
- `lumos-cli-lifecycle`：未碰 re-inject 邊界。

可執行證據：

- 從真實 `cmd_seat_check` AST 在記憶體以 optimize 0/1 執行；壞形態、vacuous、surrogateescape、正常錨定、越界 rc0、重複鍵預設行為均通過。
- 嘗試執行 `python3.14 scripts/test_lumos.py -k seat_check`，但唯讀沙盒沒有可寫暫存目錄，於測試隔離初始化時回 `FileNotFoundError: No usable temporary directory`；不把這次執行計為測試通過。

已完整讀取：

- `r2-source.patch`：213 行
- `r2-graph.patch`：221 行
- `r2-snapshot.patch`：僅取完整指紋，SHA-256 `8578c7f7ccf5f415b64e4f34d7ae3f147cae09379b348d3832b377197fe8ad4e`
- 固定圖譜：所有貼有內容的節點
- 未宣稱 CLI 已自動附加角色卡

最高等級：clean  
blocking 數：0