severity: blocker

## F1 多 ref 或非目前分支推送會檢查錯誤版本
severity: blocker
blocking: yes
引句:「有碰到清單時推送前掛鉤本來就傳;CI 改成用推送前的起點算出同一份清單」
pre-push 先把所有 ref 的路徑聯集成一份清單，再只呼叫一次 doctor；現有 `Env` 卻從目前工作目錄載入筆記。執行 `git push origin branchB:main` 而工作目錄停在 branchA 時，清單來自 branchB、lint 內容來自 branchA，branchB 的錯誤可被漏放；同次推多個 ref 更沒有唯一可檢查版本。`scripts/hooks/pre-push:24`、`scripts/hooks/pre-push:47`、`scripts/hooks/pre-push:123`、`scripts/hooks/pre-push:178`、`scripts/lumos:320`

## F2 新遠端分支會把整庫舊帳判成新違規
severity: major
blocking: yes
引句:「若讀不到上一版新建的筆記、改名、或上一版讀取失敗,則這一版的違規應全部當成新違規」
現有 pre-push 對新 ref 的通用碰觸範圍使用空樹到 tip，因此整個 repo 都進 touched 清單；配合 S11，消費專案第一次推 feature branch 時，所有既有欄位違規都會成為新違規並擋下。既有「每支檔有家」硬閘已為同一情境另算未推提交的起點並把基準夾到守衛上線提交，本 spec 沒有保留等價基準。`scripts/hooks/pre-push:36`、`scripts/hooks/pre-push:47`、`scripts/hooks/pre-push:215`、`scripts/lumos:22070`

## F3 刪除程式檔不會把既有 about_code 變成新違規
severity: major
blocking: yes
引句:「若筆記的 about_code 有一項不在這一版的提交內容裡,且這一項是這一版新加的,則應報錯誤」
若上一版有 `about_code: src/a.py` 且檔案存在，本版刪除 `src/a.py`、不改筆記，違規是本版才產生，但該 about_code 項不是新加，依 S8 只會提醒。這與第 44 行以「違規是否新出現」為判準不一致；既有讀取層已明確把刪除及改名舊路徑列為變動。`scripts/lumos:21636`、`scripts/lumos:22105`

## F4 決策沒有穩定身分，無法判斷哪條是新加
severity: major
blocking: yes
引句:「若一條決策的 valid 這一版不是 true 或 false,且這條決策是新加的或上一版的值是 true/false,則應報錯誤」
現有 parser 接受以 `content` 起頭、沒有 `id` 的決策，lint 也明確認可 `- id:` 或 `- content:`；spec 又把 `decisions.id` 唯一性排除在本案外。當無 id 的決策重排、內容改寫或有重複內容時，無法穩定判定「這條決策是新加的」；按位置會因重排誤擋，按內容會因改寫或重複而漏判。`scripts/lumos:4914`、`scripts/lumos:4935`、`scripts/lumos:12218`

## F5 pull request 的 CI 被設計成只提醒
severity: major
blocking: yes
引句:「沒有碰到清單時例如 pull request 事件拿不到起點:全部只提醒」
workflow 明確在 pull_request 事件執行，而目前只有 push 事件使用 `github.event.before` 算範圍。照 S2 實作後，使用 `commit --no-verify` 帶入欄位錯誤的分支，其 PR doctor 對全部 lint 錯誤只提醒、退出碼仍為零，CI 這條後盾不會擋。` .github/workflows/ci.yml:4`、`.github/workflows/ci.yml:30`、`.github/workflows/ci.yml:34`、`.github/workflows/ci.yml:96`

## F6 staged 刪除讀不到時回退磁碟會檢查未提交內容
severity: major
blocking: yes
引句:「讀不到時退回讀磁碟並照舊判不因讀取失敗而放行」
執行 `git rm --cached <筆記>` 後在工作目錄保留或重建該檔時，hook 仍因磁碟檔存在而呼叫 lint；索引 reader 對已刪除路徑回傳 None，按 spec 再回退磁碟，會以根本不在提交中的內容擋下提交，直接違反 S4 的提交索引真相。`scripts/hooks/pre-commit:97`、`scripts/hooks/pre-commit:99`、`scripts/lumos:21678`、`scripts/lumos:21702`

## F7 type 轉換可繞過 status 新違規判定
severity: major
blocking: yes
引句:「若系統、專案、驗證、問題筆記這一版沒有填 status 而上一版有填或這篇是新建的,則應報錯誤」
上一版可為合法的 `type: moc` 且沒有 status，本版只把 type 改成 system 並保留有效 summary；缺 status 是本版才成立的違規，但 S5 因上一版也沒填 status 而只提醒。現有 lint 的合法 status 集合依 type 決定，證明違規狀態必須比較整體 type/status 組合，不能只比較 status 欄是否存在。`scripts/lumos:4840`、`scripts/lumos:4861`

## 實務隱患覆核

守衛面：有；F1、F2、F5 是直接漏擋或錯誤快照，F3、F4、F7 是新違規判定缺口。  
消費專案相容性：有；F2 會在新遠端分支把存量舊帳一次升成硬擋。  
Git 拓撲與並行工作目錄：有；F1、F6 分別覆蓋多 ref／非目前分支與索引、磁碟分歧。  
資料完整性：有；F3、F4、F7 會讓實際新產生的欄位錯誤只停在提醒。  
效能與資源：無；現有程式不足以佐證全庫 lint 會超出 hook 或 CI 預算。  
金流、外部送出、正式環境不可逆：無；本案只改本地 lint、Git hooks 與 CI 判定，沒有這三類動作。  
圖譜鏡頭附節點：無；凍結快照止於第 92 行，沒有尾端附加的合約或事故節點可逐條判定。

總結: 最嚴重 severity blocker，blocking 共 7 條。
