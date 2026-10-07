severity: minor

ID: SEC-01-WINDOWS-RECEIPT-ROOT-ESCAPE  
severity: minor  
blocking: 否  
逐字引句:「if rel.is_absolute() or ".." in rel.parts or not rel.parts:」  
file: `governance/eval/review_convergence.py:295`

誰：能提供 `trials.jsonl`、能在 Windows 主機其他位置寫檔，但不能寫入受信任 `--receipts` 目錄的人。  
入口：`compare` 的 `receipt.path`。  
輸入：Windows 根相對路徑，例如 `\Users\Public\forged.json`。這類路徑沒有磁碟代號，`Path.is_absolute()` 會是 false；接到 `base` 時卻會重設到該磁碟根目錄。  
拿到什麼：可繞過 receipts 目錄限制，讓比較器接受目錄外自行製作的 receipt，進而操縱品質、輪數或成本摘要。這不是 receipt 真偽驗證問題，而是文件明訂之目錄邊界可被跨越。工具只產生離線摘要且未接產品閘，故降為 minor。  
建議：同時拒絕具有 `drive`、`root` 或 `anchor` 的相對路徑，並加入 Windows 根相對與磁碟相對路徑測試。

ID: SEC-02-UNICODE-OUTPUT-SPOOFING  
severity: minor  
blocking: 否  
逐字引句:「print(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False))」  
file: `governance/eval/review_convergence.py:454`  
file: `governance/eval/test_review_convergence.py:136`

誰：能提交或提供帳本、trial、receipt JSON 的人。  
入口：`cohort` 輸出的 `loop`／`round`，以及 `compare` 回報的非法 `status`。  
輸入：U+2028/U+2029 分行字元或 U+202E 等雙向文字控制字元；現有測試明確接受含 U+2028 的 loop。  
拿到什麼：可在支援這些 Unicode 控制字元的終端、報表 viewer 或逐行紀錄系統中偽造視覺分行、重排文字，誤導讀者對迴圈名稱或錯誤原因的判讀。JSON 結構仍有效，不能執行命令，故為 minor。  
建議：輸出到人類介面前跳脫 Unicode 分行、段落與雙向控制字元。

資安分類核對：

- 注入／路徑：上述兩項 minor；未發現 shell、程式碼、SQL 或反序列化執行入口。
- 登入權限：純本機 CLI，沒有登入、session、角色或提權介面；沿用呼叫者檔案權限。
- 秘密個資：資料只送 stdout，沒有外傳；未發現可直接取得檔案內容或秘密的通道。
- 加密傳輸：沒有網路傳輸。SHA-256 僅用於一致性釘選；程式與文件均未把 receipt 一致性宣稱為真偽證明。
- 執行邊界：主工具不執行 manifest、receipt、產品、模型或使用者命令；未發現動態載入或 subprocess 注入。
- 行動端：不適用。
- 新依賴：沒有；僅使用 Python 標準函式庫。

圖譜硬合約核對：

鏡頭只列出下列節點名稱與 `★INVARIANT★` 標記，未自動附上合約原文、`[test:]` 綁定或綁定狀態；因此逐條均只能判為材料不足，不能宣告符合或違反：

- `Systems/測試假綠形態`：未附硬合約內容。
- `Systems/bound-tests-gate`：未附硬合約內容。
- `Systems/canary-audit`：未附硬合約內容。
- `Systems/guard-kill`：未附硬合約內容。
- `Systems/slim-get-一行安裝`：未附硬合約內容。
- `Systems/slim-install-安裝器`：未附硬合約內容。
- `Systems/slim-uninstall-一行卸載`：未附硬合約內容。
- `Systems/lumos-cli-read`：未附硬合約內容。
- `Systems/lumos-cli-lifecycle`：未附硬合約內容。
- `Systems/design-loop`：未附硬合約內容。
- `Systems/節點範圍與索引守衛`：未附硬合約內容。

表態核對：`py-external=na` 與程式相符；其餘表態屬效能／資源面，沒有涵蓋上述 Windows 路徑與人類輸出顯示邊界。

最高等級: minor  
阻擋條數: 0