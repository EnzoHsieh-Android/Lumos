severity: blocker

## Frontmatter 與決策

已讀,無 finding；三個 `[[...]]` 交叉引用均存在。

## 為什麼（這批的來源）

### F1 現況佐證用了無法定位的指涉
severity: minor
blocking: 否 — 不影響演算法，但讀者無法重驗支撐裁定的數字
引句:「lumos 自己一份份規格做出來，核心節點照樣累積（設計審查迴圈那篇 32 行說明、日期橫跨 7–9 月二十幾天、正文連 14 份計劃」
1. 「設計審查迴圈那篇」未提供節點名或 wikilink；目前最相符的 `Systems/design-loop` 正文為 51 行，因此 32 行與 14 份計劃無法確定指向哪個版本。

## 世界上怎麼做的

已讀,無 finding。

## 名詞

### F2 過期的 about_code 仍會被當成有效的家
severity: major
blocking: 是 — 不改的話，已不再描述該檔的節點仍可讓無家檢查假綠
引句:「家的比對沿用 about_code 既有的比對鍵（解連結、大小寫與 Unicode 寫法照磁碟），不另寫一套」
1. 現行 `about_code` 明定正文雜湊不同即過期，impact 也拒用過期標記；本 spec 的家只看欄位值，沒有要求 stamp 有效。
file: `scripts/lumos:11255` `about_code_expired` 把缺 stamp、舊格式或正文雜湊不符一律判為過期。
file: `scripts/lumos:19896` impact 遇到過期 `about_code` 直接跳過，不把它當有效命中。

### F3 rejected、planned、deferred 節點照字面都能充當家
severity: major
blocking: 是 — 不改的話，被否決或尚未落地的節點可讓歸屬檢查假綠
引句:「狀態不是作廢或過期的 Systems 節點，about_code 列了這支檔」
1. 規則只排除 superseded／stale，現有合法狀態中的 `rejected`、`planned`、`deferred` 都會符合字面定義。
file: `scripts/lumos:4204` Systems 合法狀態包含 `planned`、`deferred`、`rejected`、`superseded`、`stale` 等值。

### F4 node_home.ignore 沒有可實作的比對契約
severity: major
blocking: 是 — 不改的話，不同實作者會排除不同檔案，直接形成漏擋
引句:「排除 docs/ 與建置輸出夾、測試檔、lumos 自己裝進去而且內容沒改過的檔、專案設定 `node_home.ignore` 列的樣式」
1. Spec 未定義樣式是 `fnmatch`、`PurePath.match` 或 gitignore 語法，也未定義根目錄、目錄前綴、反斜線、否定樣式、非字串項與壞設定的處置。

## 規則一：每支檔都要有家

已讀；finding 見 F2、F3、F4。

## 規則二：節點只准用反引號寫自己家的檔

### F5 逐提交檢查無法直接重用只讀現場狀態的抽取器
severity: major
blocking: 是 — 不改的話，pre-push 對較早提交會拿 HEAD 的節點與檔案母體判斷，產生誤擋或漏擋
引句:「新指令 `lumos home check`：`--staged`（提交前，看這次要提交的內容）或 `--diff <範圍>`（推送前，逐個提交檢查、跳過合併提交）」
1. 現行反查直接重讀工作目錄的 Markdown 並執行當前 `git ls-files`，沒有 tree/ref 參數；spec 未定義如何取得每個提交父子兩側的圖譜、檔案模式及唯一檔名母體。
file: `scripts/lumos:19604` 裸檔名唯一性固定從當前 `git ls-files` 取得。
file: `scripts/lumos:19619` 抽取器直接讀 `env.vault` 內的現場 Markdown。

### F6 重名檔會讓裸檔名外家引用完全漏檢
severity: major
blocking: 是 — 不改的話，常見的 `index.ts`、`App.swift` 等重名檔可留在錯誤節點而不被擋
引句:「完整路徑＋在受版控檔裡唯一的裸檔名」
1. 現行算法以所有受版控檔為母體，只要 basename 出現兩次就整條裸檔名路徑失效；測試檔或建置設定中的同名檔也能遮蔽需要家的程式檔。
file: `scripts/lumos:19595` 裸檔名比對只有 `counts.get(base) == 1` 才啟用。
file: `scripts/lumos:19630` basename 不唯一時不再檢查裸反引號引用。

## 規則三：寫回要落在改動檔的家

### F7 核心寫回規則的蘊含方向反了
severity: blocker
blocking: 是 — 不改的話，既有檔改碼後完全不更新其家仍可通過，核心目標沒有被執行
引句:「內容有變的每一篇 Systems 節點（含這次新開的），提交後必須是某支改動檔的家」
1. S13 只驗「被改的節點 → 至少擁有某支改動檔」，沒有驗「每支改動檔 → 至少一個家有內容變更」；零篇 Systems 內容變更時條件真空成立。
file: `scripts/hooks/pre-commit:165` 現行硬擋只要求 staged 中存在任一圖譜 Markdown，不要求改到各檔的家。
file: `scripts/hooks/pre-push:183` 推送前的同步覆蓋目前明定只是提醒，不擋。

## 規則四：一篇管超過上限要寫負責範圍

### F8 新欄位缺少既有節點的合法寫入入口
severity: major
blocking: 是 — 不改的話，使用者無法依專案鐵則替舊 Systems 補 responsibility，計劃也無法用指令填 lands_in
引句:「`lumos new system` 可以帶 `--code`（可多支）與 `--responsibility`，一次建好；帶的檔走 about_code 既有的路徑檢查」
1. Spec 只擴充建檔指令，未要求把 `responsibility` 註冊為 scalar、把 `lands_in` 註冊為 list，亦未另定維護指令。
file: `scripts/lumos:10559` `SCALAR_KEYS` 沒有 `responsibility`。
file: `scripts/lumos:10560` `LIST_KEYS` 沒有 `lands_in`。

### F9 node_home.max_files 的合法值域未定義
severity: major
blocking: 是 — 不改的話，0、負數、布林或小數可被不同實作解讀成永久擋、永久放行或壞值
引句:「這次提交讓某篇的 about_code 變多、提交後超過上限（`node_home.max_files`，預設 3」
1. 「壞值退回預設」沒有定義整數下限、是否接受數字字串，以及 Python 中 `true` 屬於整數子型別時應否拒絕。

## 規則五：規格寫明落點

### F10 設計審適用母體與聲稱沿用的既有步驟不一致
severity: major
blocking: 是 — 不改的話，非計劃 Markdown 會被誤擋，或真正計劃可藉路徑／type 異常漏過
引句:「只看審材是 .md 計劃、首筆帳在上線日之後的迴圈（不回溯，同條款綁定那一步）」
1. Spec 未定義「計劃」靠路徑、frontmatter type 還是副檔名辨識；現行條款步驟只驗 `.md`，並不驗 Projects 路徑或 `type: project`。
file: `scripts/lumos:14840` 現行條款步驟的適用規則列出副檔名與迴圈日期。
file: `scripts/lumos:14864` 實作只以 `str(spec).endswith(".md")` 判定審材種類。

## 在哪裡檢查

### F11 跳過合併提交會漏掉合併本身新增的違規
severity: major
blocking: 是 — 不改的話，衝突解法新增程式檔、移除 about_code 或作廢家節點都可隨 merge commit 進入
引句:「推送前逐個提交檢查時也跳過合併提交（S24），各分支自己的提交已經查過」
1. 「各分支已經查過」不涵蓋 merge conflict resolution，也不涵蓋從未安裝新版 hook 的外部分支，因此不能作為跳過合併提交的保證。
file: `scripts/hooks/pre-push:165` 現行掛鉤實際接收所有待推 ref 並從 remote SHA 建立檢查範圍，沒有「來源提交必已受檢」的證據。

## 舊帳（只提醒）

已讀,無 finding。

## 讓規則被看見

已讀,無 finding。

## 邊界

已讀；逐提交快照缺口見 F5，合併路徑缺口見 F11。

## 範圍外（刻意不做）

已讀,無 finding。

## 落點

已讀,無 finding。

## 實務隱患

### F12 併發段宣稱只讀，卻另條要求每次檢查寫入受版控帳本
severity: major
blocking: 是 — 不改的話，檢查會留下未提交改動，並在並行執行時走沒有鎖的 append 路徑
引句:「處置：檢查只讀不寫；讀到半寫的檔以格式檢查那道既有的擋法為準，這道不另外處理」
1. S27 明定擋下與放行都寫治理帳，與「只讀不寫」直接矛盾；現行治理帳刻意受版控且寫入器沒有共用 vault lock。
file: `scripts/lumos:922` 治理事件直接以 append 模式寫 `.governance-log.jsonl`。
file: `scripts/lumos:13813` 治理帳刻意不列入 gitignore，供 CI 讀取。

- 誤擋／繞過：有，見 F7。
- 提交效能：無新增 finding；S32 已有明確時間門檻。
- 舊專案升級：有，見 F4、F9。
- 併發／資源：有，見 F12。
- 合併／改基底：有，見 F5、F11。
- Claude／Codex 平行路徑：無；兩者確實共用 git 掛鉤。
- 檔案系統與路徑：有，見 F5、F6。
- 不可逆、金流、對外寄送、認證、PII：無；功能只處理本機 git、圖譜與治理帳，不接觸這些資料流。

## 驗收怎麼跑

已讀,無 finding；現列測試名稱均屬待實作驗收目標，未冒充既有測試。

## 回頭條件

已讀,無 finding。

## 審計修正紀錄

已讀,無 finding。

總結:最高 severity blocker,blocking 共 11 條
