severity: major

前置檢查：refcheck 為 0 claims／0 missing／0 out_of_range；prose-lint 為 0。

## F1：來源筆記本身的符號連結未被拒絕，可能讀出 vault 外資料

severity: major  
blocking: 是  
引句:「以選定vault與推得的repo為界，列舉所有Markdown，包含作廢筆記」

規格只明定「引用」不得是符號連結，沒有規定列舉出的 Markdown 來源檔本身必須是非符號連結的一般檔。現有讀取原語會列舉 `*.md` 後直接 `read_text`，因此檔案型符號連結會被跟隨。

file: `scripts/lumos:608`  
file: `scripts/lumos:612`

輸入→錯誤：在 `Systems/leak.md` 建立指向 vault 外哨兵檔的符號連結，外部檔含合法 `lumos-security-v1` 區塊；若沿用現有列舉方式，外部內容會被解析成登記資料，違反 vault 邊界，且可能出現在輸出。

最小翻紅重現：未能重現，因 `lumos security list` 尚未實作。實作測試應建立 vault 外哨兵與 `Systems/leak.md` 符號連結，斷言退出 2、`read_complete=false`，且 stdout／stderr 均不含哨兵內容。

最小修正：資料來源列舉也明定逐段 `lstat`，拒絕來源檔或任一父路徑含符號連結；S3 增加「來源筆記是 symlink」案例，不只測 `evidence_refs` 等引用。

## F2：2 MiB／64 MiB 上限沒有規定在完整讀檔前執行，也沒有驗收案例

severity: major  
blocking: 是  
引句:「單檔大小上限2MiB、總讀取上限64MiB、檔案數上限10000」

現有 `load_vault` 使用 `read_text` 一次讀完整檔案；若新入口先讀完再檢查長度，單檔上限無法防止超大檔先耗盡記憶體。S1–S8 也沒有大檔、總量或檔案數超限案例，因此忽略三個限制仍可通過全部驗收條款。

file: `scripts/lumos:606`  
file: `scripts/lumos:612`

輸入→錯誤：vault 內放入一個遠大於 2 MiB 的 Markdown；完整 `read_text` 先配置內容，再判超限，可能阻塞或 OOM，無法可靠產出退出 2 與可解析 JSON。

最小翻紅重現：未能重現，因指令尚未實作。實作測試應放入大型稀疏 Markdown，監控讀取器不得請求超過 `2 MiB + 1 byte`，並斷言退出 2、JSON 可解析、未解析該檔內容；另測 64 MiB 累計及第 10001 個檔案。

最小修正：規格指定以二進位有界讀取，單檔最多讀 `limit + 1`，累計最多讀「剩餘額度 + 1」，超限即記錯但繼續安全列舉；在解碼、保留快照及 JSON 解析前執行限制，並新增獨立驗收條款。

## F3：併發變動要求沒有對應驗收，逐檔順序讀取可產生 rc0 混合快照

severity: major  
blocking: 是  
引句:「若讀取期間偵測到檔案清單或內容變動，列不完整退出2；不得悄悄用混合結果作驗收。」

現有讀取模型按排序逐檔讀一次，沒有讀取前後 manifest 或檔案身分比對。規格雖要求偵測變動，但 S8 只測「列舉讀取錯誤」，沒有測成功讀取之間發生的替換或改寫；實作者完全不做併發偵測仍可通過 S1–S8。

file: `scripts/lumos:608`  
file: `scripts/lumos:610`  
file: `scripts/lumos:620`

輸入→錯誤：A、B 兩篇均合法；讀完 A 後、讀 B 前，由另一程序改寫 B。輸出會混合 A 舊版與 B 新版，卻可能維持 `read_complete=true`、退出 0。

最小翻紅重現：未能重現，因指令尚未實作。實作測試應以同步屏障在 A 讀完後原子替換 B，斷言 `read_complete=false`、退出 2，且錯誤指出變動路徑；另測讀取中改寫同一檔。

最小修正：定義兩階段 manifest，至少比較相對路徑、非跟隨連結的檔案身分、大小及 `mtime_ns`；每檔開啟前後以 `lstat`／`fstat` 核對，全部讀完再重列一次。任何差異保留安全快照但標不完整，並新增專門併發驗收條款。

## 已讀，無 finding

- 目的與授權：已讀，無 finding。
- 世界解、最小解與落點：已讀，無 finding。
- CLI 契約：已讀，無 finding。
- schema、證據與狀態算法：除 F1–F3 外已讀，無 finding。
- 輸出契約：已讀，無 finding。
- 首案登記與實作順序：已讀，無 finding。
- S1–S8 其餘語意：已讀，無 finding。
- 守衛誤讀：固定 `not_assessed`、分離宣告與核對，已讀，無 finding。
- 輸入安全：除 F1 外已讀，無 finding。
- 資源：F2。
- 併發：F3。
- 回退：已讀，無 finding。
- d5：Invariant 與安全驗收分類分離，盤點不升格為證據通過；已讀，無 finding。
- d6：唯讀盤點與安全覆蓋分開，不以零條目或全綠宣稱安全；已讀，無 finding。
- Q3：仍阻塞故障執行，本案未越界；已讀，無 finding。
- Q4：仍阻塞 CI／push／正式交付接線，本案未越界；已讀，無 finding。

總結：最嚴重 severity: major；blocking: 3。

已完整逐節讀過凍結審材 `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md`。
