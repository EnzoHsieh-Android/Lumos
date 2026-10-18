severity: major

F1 來源身份在 NFC 等價檔名下會靜默合併：規格指定把快照交給 `Env.from_texts`，現碼卻先將相對路徑正規化後放入 dict，後值覆蓋前值；合法支援區分 Unicode 正規形的檔案系統可漏掉一篇 Systems 筆記，仍可能 `read_complete=true`、退出 0。
severity: major
blocking: 是
引句:「對每篇只讀一次內容快照供本次解析，紀錄內容指紋；偵測到列舉或讀取失敗則read_complete=false，保留已讀項及錯誤。」
file: `scripts/lumos:710`
file: `scripts/lumos:716`
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:81`
最小翻紅：建立 `Systems/é.md` 與 `Systems/é.md`，各放不同合法 control；盤點應列兩筆或以 normalization collision 退出 2，現有 `Env.from_texts(vault, texts).notes` 只剩一筆。
最小修正：進 `Env.from_texts` 前建立「原始路徑→NFC 路徑」表，碰撞即保留兩個出處於 errors、`read_complete=false`、退出 2，禁止覆寫。

F2 `required_evidence` 與 `evidence_refs` 之間沒有可表達的種類對應；因此每個有必要證據的合法 control 都只能落到 incomplete，規格所定義的 control 級 `declared_only` 實際不可達。
severity: major
blocking: 是
引句:「required_evidence為空或證據種類對應未核對時，聚合至少incomplete。」
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:63`
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:64`
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:84`
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:230`
最小翻紅：control 宣告 `required_evidence=["behavior"]`，唯一 `evidence_refs` 指向 status=pass 且 `valid_under`、`revalidate_when` 非空的 Verification；規格要求核對種類，但兩邊都沒有 `behavior` 關聯欄，實作只能猜或輸出 incomplete。
最小修正：將 evidence refs 改為 `{kind,node}` 陣列，或在 Verification 建立可機械核對的種類欄；逐 required kind 聚合後再算 control 狀態。

F3 路徑護欄只明文約束「引用」，沒有約束被列舉的 Markdown 本身；vault 內的 `.md` symlink 可把 repo 外文件當來源快照讀入。現有讀取原語也會 `stat`、`read_text` 跟隨檔案 symlink。
severity: major
blocking: 是
引句:「引用只允許vault內正常檔案；拒絕絕對路徑、父目錄跳脫與符號連結，不讀其他專案、家目錄或外部檔案。」
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:81`
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:83`
file: `scripts/lumos:608`
file: `scripts/lumos:611`
file: `scripts/lumos:612`
最小翻紅：令 `Systems/outside.md` 為指向 vault 外檔案的 symlink，外檔含合法 `lumos-security-v1` block；盤點不得輸出該 control 或外檔文字，且須退出 2。
最小修正：列舉後、讀取前以不跟隨連結的檢查拒絕 symlink，並確認每層父目錄及最終 realpath 都在 vault；列 errors、`read_complete=false`、退出 2。S3/S7 加「來源筆記 symlink」，不要只測引用 symlink。

F4 併發條款只說「紀錄內容指紋」及「若偵測到變動」，未定義第二次比較點；單次讀取所得指紋不能發現已讀檔案稍後被改，會讓跨檔混合時點資料以完整盤點退出 0。
severity: major
blocking: 是
引句:「若讀取期間偵測到檔案清單或內容變動，列不完整退出2；不得悄悄用混合結果作驗收。」
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:81`
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:122`
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:132`
最小翻紅：同步控制盤點先讀 A，再於讀 B 前改寫 A；輸出必須 `read_complete=false` 且退出 2。目前 S8 沒有這個競態案例，也沒有規定重列舉／重雜湊，無法保證翻紅。
最小修正：凍結首次路徑集合與每檔內容雜湊，解析完成後再列舉並重讀雜湊比較；任何新增、刪除、替換或內容差異皆退出 2，並把此案例加入 S8。

已讀，無 finding：

- `lumos-cli-read` 的讀寫分軌與本案唯讀定位相容；除 F3 的讀取邊界缺口外，未破壞「不改圖譜節點」合約。
- 退出碼 0/2、`not_assessed`、不輸出 overall pass 的界線本身清楚。
- d5 的通用 Invariant／安全驗收分離方向保留；F2 會破壞逐條證據對帳。F1、F3、F4 會破壞 d6 的完整盤點承諾。
- Q3 故障執行與 Q4 正式接線均未被擅自解除，本案沒有付款、網路或部署行為。
- 資源上限及超限退出 2 已明定；回退保留原始報告與登記歷史，無 finding。
- 實務隱患逐類：守衛誤讀見 F2；輸入安全見 F1、F3；資源已讀無 finding；併發見 F4；回退已讀無 finding。

總結: major，blocking 4。
