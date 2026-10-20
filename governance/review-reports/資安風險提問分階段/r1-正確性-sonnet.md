severity: major

先講結論：照這份設計字面實作，會出現 3 個會做錯行為的缺口。第一，適用入口表漏掉了該問的威脅類別。第二，格子「被護欄覆蓋」的判法太鬆，不該算已覆蓋的也會算。第三，「建立時表版號」和「狀態只由盤點資料算出」互相打架。另有 4 條 minor。審查範圍是 `r1-snapshot.md` 全文，另對照了 `scripts/lumos` 現況。

附加節點對照：
- `Systems/情境出題`：不影響。它現有的 KEY 行沒有鎖死風險面表的條數或內容，計劃只說擴大它的 responsibility。
- `Systems/lumos-cli-read` 的 ★INVARIANT★：不影響。那條只管 search 預設排除 superseded，計劃沒碰。
- `Systems/pitfalls-code-loop`：不影響。計劃不改不帶 `--stage` 的 pitfalls，守衛面由 S8 守。
- 這三篇我只用 grep 掃了合約與 KEY 行，沒有逐篇讀全文。

## findings

### 1. 〈二〉威脅類別表「適用入口」欄漏掉該問的類別
severity: major
blocking: 是（照表實作，上傳、匯出、下載、訊息消費入口永遠不會產生身分與授權格子，實作者會做出漏問的系統）

- 段落：〈二〉威脅類別表 v1，加上〈一〉的 `kind` 單值值域。
- 問題：一個入口只有一個 `kind`，表裡 `authz-object`、`authn-identity`、`flow-abuse` 的適用入口欄卻只收 http_api 等少數 kind。
  - `authz-object` 收了 export、file_download，卻沒收 file_upload。
  - `authn-identity` 只收 http_api、web_page、admin、webhook_in，漏了 export、file_download、file_upload、message_consumer。
  - `flow-abuse` 沒收 file_upload、export。
- 具體例：
  - `POST /files` 標 `kind: file_upload`。
  - 預期要問「他人能不能覆寫我的檔案」和「身分從哪來」。
  - 照表只會產生 input-injection、data-exposure、file-handling 三格，沒有身分與授權格子。
  - 同理 `GET /export` 標 `kind: export`，有 authz 格子，但沒有「誰能呼叫」的身分格子。
- 佐證：
  - 引句：「適用與否由入口 kind 決定（表的「適用入口」欄），不由作者臨場挑。」
  - 作者不能臨場補，所以漏掉的格子沒有補救路徑。
  - S1 也只驗「適用與否只由入口 kind 決定」，驗不出表本身有沒有漏。

### 2. 〈四〉格子被護欄覆蓋的條件沒限定 concerns 與 lifecycle
severity: major
blocking: 是（該顯示為 open 的格子會被判成已有護欄）

- 段落：〈四〉去向表第一列「登記成護欄」。
- 問題：
  - 條件只寫「surfaces 含入口、assets 含資產、資產在入口 asset_ids 裡、threat_categories 含類別」。
  - 現行入口覆蓋只計 `"security" in concerns`、非 retired 的控制項，並分 active 與 candidate。
  - 佐證：`scripts/lumos:7209` 的 `_secinv_surface` 用 `live` 並濾 `"security" in r["concerns"]`；`:7216` 用 `act`/`cand` 區分 mapped 與 candidate_only。
- 具體例：
  - 一條 `lifecycle: candidate`（尚未採用）或 `concerns: [business]` 的護欄，寫了 `threat_categories: [authz-object]`。
  - 預期該格仍是 open。
  - 照 spec 該格是 `control:<id>`，缺口消失。
  - 撤除（retired）的護欄也有同樣問題，spec 沒排除。
- 佐證：引句：「controls 條目同時滿足三件事：`surfaces` 含該入口、`assets` 含該資產、而且該資產在**那個入口自己的** `asset_ids` 裡」
- 修法方向：格子覆蓋沿用現行 `live` 加 security 加 active 的口徑，candidate 另列狀態。這件事 S1 到 S14 都沒條款守。

### 3. 〈二〉「最低證據種類」和「沒有工具時」互相矛盾，S5 照字面做不出來
severity: major
blocking: 是（沒有掃描工具的專案登記不了合格護欄，只能反覆走 30 天風險接受）

- 段落：〈二〉表的「最低證據種類」欄與「沒有工具時」欄，以及 S5。
- 問題：
  - 「最低證據種類」是下限，S5 要擋比它少的 `required_evidence`。
  - 但 secrets-crypto 的最低是 secret_scan 加 review，supply-chain 是 dependency_scan 加 review。它們「沒有工具時」的做法只剩「人工審」。
  - 一條沒有掃描工具的護欄宣告 `[review]`，會被 S5 判 `insufficient_required_evidence`。
  - config-deploy 有一條替換規則（config_scan 改 deployment），但沒說盤點怎麼得知「沒有工具」。inventory 沒有對應欄位。
- 具體例：
  - 沒有秘密掃描工具的專案登記 secrets-crypto 護欄，宣告 `[review]`。
  - 預期被接受為人工審。
  - 照 spec 被 S5 擋，唯一出路是 risk_accepted，最長 30 天，要反覆續。
  - config-deploy 時盤點無從判斷該套哪個最低。
- 佐證：
  - 引句：「config-deploy 的「沒有設定與容器掃描工具時改成 deployment」：」
  - 引句：「每條登記成護欄的答案，`required_evidence` 不能比它所屬類別的這一欄少」
- 另一個相關缺口：一條護欄的 `threat_categories` 含多類時，下限是各類聯集還是逐類，spec 沒寫。

### 4. S10「每格帶建立時的表版號」沒有存放處
severity: major
blocking: 是（照字面做會出兩種都不符合 S10 的實作）

- 段落：〈二〉標題下的版號說明，〈四〉開頭，S10。
- 問題：
  - 〈四〉寫「一格的狀態只由盤點資料算出」，格子是入口 × 資產 × 類別的純計算結果，沒有儲存的物件。
  - 但〈二〉和 S10 要求格子「帶著建立時的表版號」，舊格子保留舊版號。
  - 沒有 considerations 或護欄的 open 格子沒有任何資料列可以記「建立時」。
- 具體例：
  - 表從 v1 升 v2、新增一類。
  - 預期舊格子仍標 v1、新類別的格子標 v2。
  - 照 spec，實作者只能把當前版號蓋在所有格子上，S10 的「舊格子帶舊版號」就不成立。或者另建儲存，那是 spec 沒寫的新契約。
- 佐證：引句：「盤點算出的每一格帶著建立時的表版號。」

### 5. S3 把已過期的 risk_accepted 也算進衝突，補護欄時整份盤點變成 exit 2
severity: minor
blocking: 否（不改，作者清掉舊列即可，但體驗是無預警的整體錯誤）

- 段落：〈四〉「去向之間互斥」，以及〈回退〉的「considerations 留著不刪」。
- 問題：
  - 互斥判法是「同一格有覆蓋護欄，加上 considerations 裡 not_applicable 或 risk_accepted 的一列」就列錯誤。
  - 沒有區分該列是否已過期或不合格。過期的 risk_accepted 本身已讓格子回 open。
- 具體例：
  - 風險接受過期後，作者補一條真護欄來處理。
  - 預期格子轉為 `control:<id>`。
  - 照 spec 退出 2，直到作者刪掉那列過期的 considerations。
  - 這和〈回退〉「考慮項留著不刪」的精神相反，審計軌跡會被迫丟掉。
- 另外，considerations 指到不存在的格子（例如入口 id 打錯、類別被表移除）沒有驗證，spec 沒說。

### 6. S9 前提與 deliver-security 觸發詞不一致
severity: minor
blocking: 否（寫測試時會發現，但字面條款自相矛盾）

- 段落：S9。
- 問題：
  - S9 說「兩個不同強詞」就應照原句列出 deliver-security。
  - 但 deliver-security 的觸發是 `會員|使用者|帳號|權限|個資|付款|登入|管理員`（`scripts/lumos:31048`），而通用強詞還有金鑰、憑證、token、session 等。
- 具體例：計劃只提「金鑰」和「憑證」。
  - 預期（照 S9）deliver-security 要列出。
  - 實際不會，因為 8 個觸發詞一個都沒中。
  - 想讓條款字面成立就得動 deliver-security 的觸發詞，那違反 d7。
- 佐證：引句：「當計劃有兩個不同強詞而跑 `pitfalls --stage 交付` 時，deliver-security 應照原句列出」

### 7. 詞界寫法與現行常數不同，且 token 和 session 在本工具鏈的計劃裡高頻
severity: minor
blocking: 否（上線前會量，這是提前預警）

- 段落：〈三〉「誤觸發怎麼壓」。
- 問題一：
  - spec 說比照 `_REQ_FE_WHEN` 的寫法「前後不接英數字」。
  - 現況 `scripts/lumos:31056` 的框架名那條尾端是 `(?![a-z])`，沒有 0-9，因為要容許 Vue3、React18。
  - 寫成 `(?![a-z0-9])` 對 secret、token 這類詞無影響，但「照抄」並不精確。
  - 每個 `words` 元素各自需要 `(?i)`，spec 只說「整條不分大小寫」，沒說誰加。
- 問題二：
  - 我用 spec 的通用強詞表對 `Projects/*_計劃.md`（298 篇）重算，70 篇有至少兩個不同強詞，其中 20 篇同時有 session 和 token。
  - 這個工具鏈的計劃裡，session（AI 會談）和 token（AI 用量）本來就是常用詞。
  - 這是命中數，不是誤報數，誤報要等 40 篇人工標註才知道。
- 佐證：引句：「「使用者」「會員」不算強詞。」
- 這份計劃的三階段範圍有寫「新詞表的觸發篇數與誤觸發率還沒量」，所以只列 minor。

## 前端入口（browser 端、跨來源、cookie、CSRF）的額外問題

結論：會漏問，也會重複問。

**漏問**
- `frontend-origin` 只適用 `web_page`。純後端 repo 的盤點裡，SPA 另外放在別的 repo，入口全是 `http_api`，不會有 `web_page` 入口。
  - CORS、cookie 屬性、CSRF 都是後端 `http_api` 設定的，卻沒有任何格子會問到。
  - `authn-identity` 的模板只問「身分從哪來、撤權後會怎樣」，沒問 cookie 與 CSRF。
- 需求風險面那層的 `arch-fe-origin` 只在計劃出現前端字樣時才列（`scripts/lumos:31056` 的 `_REQ_FE_WHEN`）。
  - 一份後端計劃只寫 cookie 與 cors，雖然會觸發新的通用強詞面，但那些新題目（req-sec-assets、req-sec-actors、arch-sec-boundary）都沒問跨來源。
  - 這種計劃整條路徑都問不到 CORS 與 CSRF。
- 這是上面 finding 1 的延伸。要修的話，把 cors、csrf、cookie 這類 http_api 面的問題掛到 `authn-identity` 或加 http_api 的適用入口。

**重複問**
- 同一份計劃若提到前端字樣、盤點又有 web_page 入口，同一個題目會被問兩次：架構階段一次、格子一次。
- spec 的緩解辦法是「格子那題直接引用 arch-fe-origin 的答案，寫成護欄或 considerations」。但格子的狀態只由護欄與 considerations 算，題目結成已決不會讓格子離開 open（S2）。所以重複是設計內建的，靠作者手動抄答案。
- 這不會錯放，只是多一道手續，所以不另列 finding。

已讀無 finding：〈接手先讀〉、〈現況〉（數字與口徑我未逐項重跑，只確認 25 項風險面表與 `deliver-security` 的觸發詞相符）、〈五〉、〈世界解〉、〈實務隱患〉、〈回退〉。

最嚴重 severity：major，blocking 共 4 條（findings 1、2、3、4）。
