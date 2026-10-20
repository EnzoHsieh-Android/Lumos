# 威脅類別表 v1 定稿（供 Claude 與 Codex 再確認）

依據:草案 `threat-table-v1.md`、Codex 審查（`threat-review-codex.md` 第 1733 行起的結論）、Claude 審查（`threat-review-claude.md`）;確認輪 Codex（`threat-confirm-codex.md` 第 2667 行起）、Claude（`threat-confirm-claude.md`）。背景定義讀自 `security-gate` 工作樹的 `Projects/安全主張驗收閘_計劃`〈二〉〈三〉與 `Projects/資安風險提問分階段_計劃`〈一〉〈二〉（只讀、未改）。

---

## 〈定稿表〉

> 以下整段直接替換姊妹計劃 `Projects/資安風險提問分階段_計劃` 的〈二〉底下「### 威脅類別表」那一節。

### 威脅類別表 v1（定稿候選;實作時搬到 [[Systems/資安威脅類別表]] 當正本）

版號寫在這個標題上（現在是 v1）。依 d5（取代 d1）,每次核可或改版由 Claude 與 Codex 兩家各自獨立審、意見一致才核可並升版號,核可紀錄記在 [[Systems/資安威脅類別表]] 的 decisions,附兩份審查報告（`governance/security-consensus/threat-table-v<N>/claude.md`、`codex.md`）的路徑與 sha256。兩家對這一版都確認之前,表仍是提案,閘門不拿最低種類擋人。

| id | 要問什麼（模板） | STRIDE | ASVS 5.0.0 | WSTG v4.2 | API Top10 2023 | 適用入口 | 有角色維度 | 最低證據種類 | 能產生證據的工具類別 | 沒有工具時（由驗收閘依工具清單換算） |
|---|---|---|---|---|---|---|---|---|---|---|
| authz-object | {角色} 從 {入口} 能不能（1）讀、改、刪不屬於他或不在他租戶範圍的 {資產}（含批次與列表操作）;（2）呼叫他的角色不該用的功能或管理操作;（3）在自己的 {資產} 上寫入不該他改的欄位（如角色、價格、擁有者）,或讀到不該他看的欄位?被拒時資料與副作用怎樣?（webhook_in、message_consumer、batch 另問:照訊息或工作內容裡的 id 去改資料前,有沒有核對這個來源有權動這一筆?） | E、I、T | V8、V15（15.3.3 批量賦值） | ATHZ | API1、API3、API5 | http_api、web_page、export、file_upload、file_download、admin、webhook_in、message_consumer、batch、cli | 是 | behavior、fault_sensitivity、review | 既有單元與整合測試 runner（behavior）、破壞測試與故障收證（fault_sensitivity）、人工或獨立審查（review）、動態掃描（補充;產出 dynamic_scan,不抵 behavior） | 無替代（測試 runner 與 lumos 的 guard kill、test-quality 在專案裡本來就有） |
| authn-identity | {角色} 在 {入口} 的身分從哪來、何時可信?偽造、過期、撤權、登出後會怎樣?登入、重設密碼、驗證碼這類端點能不能被暴力嘗試或用來列舉帳號?重設與邀請權杖會不會被猜到、重用或不失效?登入後 session 有沒有換新?（用權杖的另問:簽章、issuer、audience 怎麼驗?）（webhook_in、message_consumer 另問:來源簽章怎麼驗、時間戳與重送怎麼擋?）（這個入口若供瀏覽器使用,且會自動帶憑證或允許跨來源呼叫,另問:session cookie 的 Secure、HttpOnly、SameSite 怎麼設?允許哪些來源（CORS）?改狀態的請求怎麼防 CSRF?登入後跳轉與 OAuth 回呼的目的地有沒有限定白名單?state 或 PKCE 有沒有驗?WebSocket 握手有沒有驗 Origin 與身分?） | S | V6、V7、V9、V10、V3（3.3 cookie／3.4.2 CORS／3.5 跨來源／3.7 跳轉）、V4（4.4 WebSocket） | IDNT、ATHN、SESS、CLNT | API2 | http_api、web_page、admin、webhook_in、export、file_upload、file_download、message_consumer、cli | 是 | behavior、fault_sensitivity、review | 既有單元與整合測試 runner（behavior）、破壞測試與故障收證（fault_sensitivity）、人工或獨立審查（review）、動態掃描（補充;要附登入成功證據） | 無替代（不做登入的示範專案寫明「身分可信」是未驗前提,走 considerations） |
| input-injection | 來自 {入口} 的不可信內容（含先存進資料庫、檔案、訊息,之後才被用到的,以及第三方回應）在組查詢、命令、範本,或輸出到 HTML、JavaScript、Email、CSV／Excel、日誌時,會不會改變原定語意或被執行（SQL／NoSQL／命令／範本注入、XSS、公式注入、日誌注入）?解析時會不會反序列化成任意物件,或解析 XML 外部實體? | T、I、E | V1、V2（2.2 輸入驗證） | INPV | — | 全部 | 否 | behavior、static_analysis、review | 既有單元與整合測試 runner（behavior）、靜態分析（static_analysis）、人工或獨立審查（review）、模糊測試（補充;產出 fuzz）、動態掃描（補充） | 沒有靜態分析工具:static_analysis 換成「每個危險輸入點至少一個惡意輸入反例的 behavior」加上 review 多蓋判斷 `manual_check_scope`（紀錄列出逐點核對的危險輸入點清單） |
| flow-abuse | 合法或非法的 {角色} 在 {入口} 重送、並發或大量操作時,能不能讓 {資產} 被他人操作生效、重複生效、超賣,或耗盡運算、儲存、佇列與第三方付費配額（簡訊、Email、外部 API）? | T、D | V2（2.3 業務邏輯／2.4 防自動化）、V15（15.4 並發安全） | BUSL | API4、API6 | http_api、web_page、webhook_in、message_consumer、file_upload、export、file_download、batch、admin | 是 | behavior、concurrency、review | 既有單元與整合測試 runner（behavior;並發測試產出 concurrency）、壓測與並發（concurrency）、人工或獨立審查（review） | 無替代（沒有壓測工具時 concurrency 用 runner 的並發測試,格式 junit;本機調低配額後的小規模測試即可,不要求大型壓測） |
| flow-sequence | {入口} 的業務流程能不能被跳步驟、亂序或重放其中一步繞過（例:沒付款就確認、取消後照樣出貨）?竄改業務參數（負數量、改單價、重複套用折扣）會不會被接受? | T | V2（2.3 業務邏輯） | BUSL | API6 | http_api、web_page、webhook_in、message_consumer、admin、batch、file_upload、cli | 否 | behavior、review | 既有單元與整合測試 runner（behavior）、人工或獨立審查（review） | 無替代 |
| data-exposure | 錯誤訊息、日誌、除錯輸出、URL 參數、共用快取與匯出暫存,會不會帶出 {資產} 的內容、秘密,或洩漏它存不存在?應用程式自己產生的匯出與暫存檔多久刪、有沒有真的刪? | I | V14（14.2 一般資料保護）、V13（13.4 非預期資訊外洩）、V16（16.5 錯誤處理） | ERRH、INFO | — | 全部 | 否 | behavior、review | 既有單元與整合測試 runner（behavior）、人工或獨立審查（review）、動態掃描（補充） | 無替代 |
| file-handling | {入口} 處理的檔案,實際格式、檔名與路徑、壓縮檔內的路徑與符號連結、解開後的大小與檔數有沒有限住?能不能讀寫到別的檔（路徑穿越、zip slip）、塞爆空間或處理器,或讓上傳內容被當成網頁或程式執行（SVG／HTML、Content-Type 被瀏覽器猜成可執行）而傷到下載的人? | T、I、D | V5 | INPV、BUSL | — | file_upload、file_download、export、message_consumer、batch、outbound_call | 否 | behavior、static_analysis、review | 既有單元與整合測試 runner（behavior）、靜態分析（static_analysis）、人工或獨立審查（review）、模糊測試（補充） | 沒有靜態分析工具:static_analysis 換成「每個檔案處理點至少一個惡意檔案反例的 behavior」加上 review 多蓋判斷 `manual_check_scope`（紀錄列出逐點核對的處理點清單） |
| outbound | {入口} 會不會被拿來打內網、雲端 metadata 或不該打的位址?重新導向與 DNS 解析之後的目的地還受限嗎?第三方回應的格式、大小、內容有沒有驗過才信?逾時、重試與帶出去的憑證有沒有限住?TLS 有沒有驗對方憑證? | T、I | V1（1.3.6 SSRF）、V12（12.3 服務間 TLS）、V13（13.2 後端通訊設定）、V15（15.3.2 不跟隨重新導向） | INPV | API7、API10 | outbound_call、webhook_in | 否 | behavior、review | 既有單元與整合測試 runner（behavior）、人工或獨立審查（review）、靜態分析（補充） | 無替代 |
| secrets-mgmt | 這個 repo 用到的秘密、金鑰、憑證放在哪（程式碼、git 歷史、設定檔、平台的秘密管理）?誰讀得到、權限是不是最小?外洩時怎麼撤銷與輪替? | I | V13（13.3 秘密管理） | CONF | — | `@repo`（每個 repo 根問一次） | 否 | secret_scan、deployment、review | 秘密掃描（secret_scan）、人工或獨立審查（review／deployment） | 沒有秘密掃描工具:secret_scan 換成 review 多蓋判斷 `manual_check_scope`（紀錄寫明核對了工作目錄與 git 歷史的哪些範圍、用什麼方法;這次核對只對紀錄當時的提交有效,寫進 limitations）;deployment 本來就在最低種類裡,不換 |
| crypto-use | 這個 repo 的雜湊、加密、簽章與亂數,用的是不是標準庫或成熟套件建議的演算法與參數?有沒有自寫加密?密碼用什麼存（該用 Argon2、bcrypt、scrypt、PBKDF2 這類密碼雜湊）?驗簽或解密失敗時會不會照樣放行? | I、T | V11 | CRYP | — | `@repo`（每個 repo 根問一次） | 否 | behavior、review | 既有單元與整合測試 runner（behavior）、人工或獨立審查（review）、靜態分析（補充;可抓弱演算法） | 無替代 |
| supply-chain | 目前用到的直接與間接依賴、容器映像、建置工具與 CI 動作從哪來?版本或 digest 怎麼釘、完整性怎麼核?安裝與建置腳本有多大權限?新披露的漏洞多久處理? | T | V15（15.1 文件與元件清冊／15.2 依賴） | CONF | — | `@repo`（每個 repo 根問一次） | 否 | dependency_scan、review | 依賴漏洞掃描（dependency_scan）、人工或獨立審查（review） | 沒有依賴掃描工具:dependency_scan 換成 review 多蓋判斷 `manual_check_scope`（紀錄附直接與間接依賴的套件與版本清單、查過的公告來源與查閱日期;只確認鎖檔存在不算） |
| config-deploy | 各部署環境的服務權限、對外開的埠、管理與除錯介面、預設帳號與設定有沒有守住?對外是不是只走 TLS、憑證與 HSTS 怎麼設?有沒有舊版、測試用或沒列在盤點裡的端點與環境還開著?備份、快照與日誌存在哪、保存多久、有沒有加密、誰能刪改? | T、I、D | V13、V12（12.1 TLS 一般／12.2 對外 HTTPS）、V16（16.4 日誌保護） | CONF、CRYP | API8、API9 | `@repo`（每個 repo 根問一次） | 否 | config_scan、deployment、review | 設定與容器掃描（config_scan）、人工或獨立審查（review／deployment） | 沒有設定與容器掃描工具:config_scan 換成 deployment（deployment 已在最低種類裡,換算後就是 deployment、review）;repo 裡沒有可掃的容器或 IaC 檔時,工具清單不登記這類工具,替代自然生效 |
| audit | {入口} 上的安全相關操作（登入與登出、權限或帳號變更、改狀態的業務操作、被拒的嘗試、防護失效）與敏感資料的讀取、匯出、下載,誰在什麼時候對 {資產} 做了什麼,事後查得到、串得起來嗎?紀錄會不會帶進秘密或個資?應用程式有沒有提供刪改紀錄的途徑?（不要求記錄每一次普通瀏覽） | R | V16（16.2 一般日誌／16.3 安全事件） | — | — | admin、http_api、web_page、webhook_in、message_consumer、batch、export、file_upload、file_download、cli | 否 | behavior、review | 既有單元與整合測試 runner（behavior）、人工或獨立審查（review） | 無替代 |
| frontend-origin | 前端畫面會不會把不可信內容當 HTML 插入（innerHTML、v-html、dangerouslySetInnerHTML）?CSP 怎麼設?別的網站能不能把敏感畫面嵌進去（點擊劫持）,或偽造跨視窗訊息（postMessage）?瀏覽器儲存（localStorage、IndexedDB）裡放了什麼敏感資料,登出後清不清? | S、T、I | V3（3.2 非預期內容解讀／3.4 瀏覽器安全標頭／3.5 來源隔離）、V14（14.3 用戶端資料保護） | CLNT | — | web_page | 否 | behavior、review | 既有單元與整合測試 runner（behavior;含瀏覽器端整合測試,如 Playwright 輸出 JUnit）、人工或獨立審查（review）、動態掃描（補充） | 無替代 |

**下限與替代怎麼算**
- 「最低證據種類」是下限:一條護欄寫了幾個類別,下限就是那幾類最低種類的聯集。這條檢查（`insufficient_required_evidence`）只有一個擁有者:姊妹計劃的閘門（它讀得到 `.lumos/security-tools.json`,才知道哪個工具類別沒工具、要不要照最後一欄換算）;盤點不判這一項。作者在護欄裡自述「沒有工具」不算數。每類都含 review,因為判準獨立與適用性機械做不到。
- **不新增證據種類**。替代欄只用姊妹計劃〈二〉已有的種類,分兩種形狀:
  - **真的是部署設定的**（config-deploy 的 config_scan）:換成 deployment（人工核對平台上的實際設定,格式 `review_record`,一律要人）。
  - **原本是掃程式碼、秘密或依賴的**（input-injection、file-handling 的 static_analysis,secrets-mgmt 的 secret_scan,supply-chain 的 dependency_scan）:不換成 deployment（deployment 證的是部署設定,拿它記「人工看過程式碼」是語意錯置）,改成 review 多蓋一項要人的判斷 `manual_check_scope`;紀錄要寫明原本工具該掃的範圍、逐項核對清單、用了哪些原始材料、限制與重驗條件。程式碼類另要 behavior 對清單上每個點至少一個惡意輸入反例。
  - 替換後最低種類是替代種類加上原本的其他種類,不是只剩 review;review 本來就在,所以替代的實質是「review 多一項要人判斷」加上「behavior 案例要涵蓋清單」。走了替代欄的護欄,`security evidence` 照樣列出原本那個種類是被替代的,不當成原掃描已完成。
- 閘門機械上只核得到「review 蓋了 `manual_check_scope`」;清單上每個點是不是真的有對應的 behavior 反例,由簽紀錄的人負責,機械不比對。
- REVISIT:[when-status:Systems/資安威脅類別表=done][by:2027-03-31] 數一次走替代欄的護欄有幾條、`manual_check_scope` 清單跟 behavior 案例對不上的有幾件;有對不上的,就改成清單每項帶 behavior 案例 id、由閘門機械比對。
- **部署面的宣稱另登一條 repo 層級護欄,不在入口護欄上加標**:最低種類是每類固定的集合,閘門做不到「宣稱 X 時才多要 Y」;在入口護欄上另標 config-deploy 又會把不相干的 config_scan 帶進來。所以備份、快照、日誌保存期限、儲存加密、日誌防竄改這類部署面控制,一律另登一條 `surfaces`、`assets` 都是 `@repo`、`threat_categories` 含 config-deploy 的護欄;data-exposure 與 audit 的護欄只宣稱應用程式自己做得到、behavior 測得到的部分。這樣部署面的宣稱一定落在有 deployment 下限的 `@repo` 格子裡,沒有去向時那一格顯示 open。宣稱「某端點外部不可達」的 config-deploy 護欄,review 要判斷是否另附 behavior 實測（`category_sufficient`）。
- `@repo` 護欄的家（Systems 節點的 about_code）只列真正承擔的檔:秘密設定、部署設定、鎖檔這類;列得太寬,綁定的檔每次推送都在變,review 與 deployment 兩筆人簽紀錄就得一直重簽。

**誰問什麼、不重複問**
- 以 repo 為單位問一次的四類（secrets-mgmt、crypto-use、supply-chain、config-deploy）不逐入口展開,避免同一題重複幾十次;它們的格子用保留入口 `@repo` 表示（見〈一〉）;反過來,表裡「適用入口」寫「全部」是指 surfaces 裡所有 kind 的入口,不含 `@repo`。`@repo` 只是合併出題:這四類的 review 紀錄要寫明證據涵蓋了 repo 裡哪些服務、哪些部署環境、哪份依賴清單與哪些秘密來源;只掃了一個服務或只看了開發環境的,不能代表全部（由 `inventory_complete` 判斷）。
- **cookie、CORS、CSRF 只在 authn-identity 問**:純後端 repo（前端在別的 repo）只有 http_api、沒有 web_page,frontend-origin 一格都不會長,但 cookie 屬性、CORS、CSRF 都是後端在設定,所以放在 authn-identity 的瀏覽器括號題。同一 repo 同時有 http_api 與 web_page 時,frontend-origin 的格子不再問這三件事;frontend-origin 管的是前端自己的渲染、CSP、嵌入、跨視窗訊息與瀏覽器儲存。
- frontend-origin 跟既有前端面 `arch-fe-origin` 的關係:需求風險面那一層**沿用 arch-fe-origin、不另加一題**;frontend-origin 只在格子這一層存在（web_page 入口逐格問、追去向）。同一份計劃若已在 arch-fe-origin 答過,格子那一題可以引用那個答案裡的分工與決策,但格子的去向仍要寫成護欄或 considerations;arch-fe-origin 的答案本身不算驗證完成。
- **檔案路徑穿越歸 file-handling**,input-injection 不重複問;**CSV／Excel 公式注入歸 input-injection**（輸出語境的注入）,file-handling 不重複問。日誌注入歸 input-injection;audit 只問紀錄有沒有、串不串得起來、應用程式有沒有刪改紀錄的途徑;日誌存哪、保存多久、儲存層防不防竄改歸 config-deploy。
- **回應欄位依角色該不該給歸 authz-object**（API3 只掛在那裡,因為它有角色維度）;data-exposure 管的是錯誤、日誌、快取這些旁路把資料帶出去。
- **密碼怎麼存歸 crypto-use**;authn-identity 管登入流程本身（嘗試限制、重設、session、權杖驗證）。
- **跳步驟與竄改業務參數歸 flow-sequence**（最低 behavior、review）;重送、並發、耗盡歸 flow-abuse（才要 concurrency）。兩者都宣稱的護欄兩類都標。
- **一個功能兼有多種性質時,每種性質各登一個入口**（盤點規則）:一個入口只有一個 `kind`,不會自動繼承別的 kind 的題目。所以一個功能同時有上傳、下載、匯出、外呼、批次處理或訊息消費這些性質時,每種性質各登一個對應 kind 的入口,例如:
  - 管理後台的 CSV／ZIP 匯入:登 `admin` 之外另登 `file_upload`,file-handling 那一類才問得到 zip slip 與解壓上限。
  - 伺服器會依使用者給的網址或主機名發出請求的功能（頭像網址、webhook 註冊、匯入連結、PDF 產生抓圖）:另登 `outbound_call`,outbound 那一格才長得出來。
  - CLI 不因為是操作者（本人或 AI）啟動就當成沒跨信任邊界:它處理外來檔案、遠端資料或做高權限操作時,照性質另登 `file_upload`、`batch`、`outbound_call` 或 `admin`。
  - 入口漏登由 review 的 `inventory_complete` 判斷抓。outbound 的 behavior 要用本機模擬的目的地證明「禁止的請求實際沒送出去」,不能只測網址檢查函式。

**各類共同的附問與證據注意**
- 每一題的候選題尾端固定附一句:「這道防護依賴的服務逾時、丟例外或不可用時,是拒絕還是放行?」（ASVS 5.0.0 V16.5.2、16.5.3）;宣稱會安全失敗的,behavior 要有一個依賴失效的案例。
- 每條護欄的證據要對到它實際宣稱的那個處理點或授權維度（例如 input-injection 的 behavior 與靜態規則各自覆蓋哪個 sink）,不能拿一份不相干的整體掃描充數;這由 review 的 `category_sufficient` 判斷。
- 工具類別欄每項後面括號寫它產生的證據種類;標「補充」的工具不在最低種類裡,產出的種類也不能抵別的種類（動態掃描產出 dynamic_scan,不抵 behavior;fuzzer 沒當機不代表授權正確）。工具裝了不等於已有可用的測試、故障配方或校準樣本。
- 防毒掃描不強制,消費專案依用途自選。
- **適用範圍**:記憶體安全類問題（越界讀寫、use-after-free、整數溢位）在本表受管語言後端的範圍外;消費專案用到原生擴充、影像或文件解析的 C／C++ 元件時另議,按需加 fuzz 或 sanitizer 證據。

**標準對應只是查閱索引**
- STRIDE、ASVS、WSTG、API Top 10 四欄只是「去哪裡查」的索引,**不表示符合任何標準**,也不表示本表承接了那一章的全部要求。ASVS 章節對 STRIDE 沒有 OWASP 官方對照,STRIDE 字母是本表自建。
- 已回原文核對（2026-10-20）:
  - ASVS 5.0.0:官方 GitHub 標籤 `v5.0.0_release` 的 `5.0/en/` 目錄,V1–V17 的章名與表中括號裡的節號都存在,且節號內容對得上括號說明（1.2.10 CSV 公式、1.3.6 SSRF、1.3.7 範本注入、1.5.1 XML 外部實體、1.5.2 反序列化、2.4.1 防自動化、3.3 cookie、3.4.2 CORS、3.4.6 frame-ancestors、3.5.5 postMessage、3.7.2 跳轉到外部網域、4.4.2 WebSocket 握手驗 Origin、5.2.3 解壓上限、5.2.5 符號連結、5.3.3 zip slip、6.3.8 帳號列舉、8.2.3 欄位層級授權、11.4.2 密碼雜湊、12.3.2 TLS 用戶端驗憑證、13.3 秘密管理、13.4.2 除錯模式、14.2.1 URL 不帶敏感資料、14.2.2 伺服器端快取、15.1.2 元件清冊、15.2.4 依賴來源、15.3.2 不跟隨重新導向、15.3.3 批量賦值、15.4 並發、16.3 安全事件、16.4 日誌保護、16.4.1 日誌注入、16.5.2／16.5.3 安全失敗）。
  - WSTG v4.2:官方 GitHub 標籤 `v4.2` 的 `document/4-Web_Application_Security_Testing/`,類別代號 INFO、CONF、IDNT、ATHN、ATHZ、SESS、INPV、ERRH、CRYP、BUSL、CLNT 對應的目錄都存在;CORS 是 CLNT-07、點擊劫持 CLNT-09、Web Messaging CLNT-11、瀏覽器儲存 CLNT-12、cookie 屬性 SESS-02、session fixation SESS-03、CSRF SESS-05、密碼重設 ATHN-09、SSRF INPV-19、XML 注入 INPV-07、弱 TLS CRYP-01。
  - API Top 10 2023:官方 GitHub `OWASP/API-Security` 的 `editions/2023/en/0x11-t10.md`,API1–API10 的名稱與表中用法一致。
- 未核對:每個類別「只掛這幾章就夠」的完整性（本表自建判斷,只核了章節存在與括號節號的內容）;沒有括號節號的整章對應（例如 authz-object 的 V8、crypto-use 的 V11）只核到章名;STRIDE 字母。
- 寫法:欄內多個值用全形頓號 `、` 分開,括號裡的多個節號用 `／` 分開,讓漂移測試照頓號切集合時不會把一個章節切成兩半。
- **漂移測試分欄比**:id、STRIDE、ASVS、WSTG、API、適用入口、有角色維度、最低證據種類八欄照全形頓號切成集合比（順序不算差異）;模板、工具類別、沒有工具時三欄比整串原文（這三欄的文字本身含頓號,而且候選題要用模板原字串,切成集合會丟掉順序）。

**版號、改名與單一來源**
- **版號跟著資料列走,不跟著格子走**:格子每次從 inventory 與當前的表現算,沒有地方存「格子建立時」的版號,所以不寫這種東西。改成:每一列 considerations 與每一條 controls 寫入時帶 `threat_table_version`（寫入當下表的版號）;有資料列的格子顯示那一列的版號,沒有資料列的 open 格子只顯示當前版號。表改版後,舊版號的資料列照舊算數,`security list` 另列「資料列版號比當前舊」的數量,提醒重審。
- **類別被改名或刪除**:considerations 引用了當前表沒有的類別 id,列格子層錯誤 `unknown_category`（見〈四〉的格子層錯誤）,不靜默忽略,也不擋推送。controls 的 `threat_categories` 引用表裡沒有的 id 不歸格子層:依姊妹計劃屬護欄層錯誤 `threat_category_unknown`（整條護欄 unsound、例外蓋不掉）,由姊妹計劃的閘門判,這裡不重複列。v1 定稿相對草案改了 id（`secrets-crypto` 拆成 `secrets-mgmt` 與 `crypto-use`,新增 `flow-sequence`）;草案沒核可過、沒有資料列帶它的版號,所以不做舊 id 轉寫,寫了舊 id 的照上面兩條報錯。
- **單一來源**:實作時這張表搬到 [[Systems/資安威脅類別表]],那裡是唯一的正本;本篇這張表改成一行指過去並刪掉,避免兩份。不擴大 [[Systems/情境出題]] 的負責範圍——那篇管對照實驗的量測與需求風險面表的內容源,威脅類別表的主要讀者是盤點與驗收閘,語意屬資安,另開一篇比把一篇擴成包四件事清楚。程式不讀圖譜（`pitfalls --stage` 不需要筆記庫,消費專案跑 `security list` 時也沒有工具鏈的圖譜）,所以 `scripts/lumos` 放一份鏡像常數,另寫一支漂移測試讀 [[Systems/資安威脅類別表]] 那張表,逐列逐欄比對常數（比法照上面〈標準對應〉的「漂移測試分欄比」,標題上的版號也比）,任一欄不同就紅;要改表先改圖譜正本、依 d5 經 Claude 與 Codex 雙家一致核可升版,再改常數。

---

## 〈處置清單〉

### Codex

| 編號 | 意見 | 處置 | 理由 |
|---|---|---|---|
| Codex#1 | authz-object 補功能、欄位、跨租戶授權;入口加 webhook_in、message_consumer、batch、cli | 採納 | 跟 Claude M1、S3 同向;cli 也加,因為管理用 CLI 常繞過應用層授權,單人 CLI 真的不適用時用 considerations 標掉即可。模板採「三點列舉」寫法,比 Codex 的抽象句好答。 |
| Codex#2 | authn-identity 補帳號恢復、登入限制、session 換新、權杖驗證、webhook／訊息來源驗證;「http_api 另問」改成瀏覽器可達入口;入口加 batch、cli | 部分採納 | 模板與括號條件全收（確認輪把瀏覽器括號題的 kind 限制拿掉,改成「供瀏覽器使用且自動帶憑證或允許跨來源」）;入口加 cli,不加 batch:batch 沒有呼叫進來的人要驗身分,它用的服務帳號權限歸 authz-object（系統角色）,憑證歸 secrets-mgmt。 |
| Codex#3 | input-injection 改寫成涵蓋儲存後使用、XSS、CSV、XXE、反序列化;每條護欄要指明覆蓋的處理點 | 採納 | 跟 Claude M2、M3 一致;「指明處理點」寫進共同注意,由 `category_sufficient` 判斷。 |
| Codex#4 | flow-abuse 補合法使用者濫用與資源／費用耗盡;入口加 export、file_download、admin、outbound_call、batch、cli;concurrency 定義擴大 | 部分採納 | 模板採納;入口加 export、file_download、batch、admin,不加 outbound_call（費用由觸發它的那個入口問,重試風暴已在 outbound 模板）與 cli（CLI 的外來輸入照「兼有多種性質各登一個入口」規則落到 batch、file_upload 等入口,那些已在清單上;確認輪改正了原先「操作者自己跑」的理由）;concurrency 定義擴成「宣告不該生效的操作（他人操作、重複生效、超過配額）仍不生效」,列進連動。 |
| Codex#5 | data-exposure 補快取、暫存、備份、保存與刪除;涉及備份時另要 deployment | 部分採納 | 模板採納（備份部分確認輪移到 config-deploy）;「涉及備份時另要 deployment」是條件式下限,閘門做不到;確認輪改成「部署面宣稱另登 `@repo` 的 config-deploy 護欄」,原先的「另標 config-deploy」撤掉。 |
| Codex#6 | file-handling 補實際格式、連結、解壓大小、可執行內容、傷害下載者;入口加 message_consumer、batch、cli、outbound_call;防毒不強制 | 部分採納 | 模板、防毒不強制、前三個入口採納;cli 不加:CLI 處理外來檔案時照定稿表下方的明文盤點規則另登 file_upload 或 batch（確認輪改正:原先「操作者自己給的檔沒跨信任邊界」不能當通則）。 |
| Codex#7 | outbound 入口改「全部、不外呼者附理由判不適用」;模板補重新導向、DNS、metadata、第三方回應、逾時重試、憑證轉送;behavior 要證實際沒送出 | 部分採納 | 模板與 behavior 要求採納;入口不改「全部」:每個不外呼的入口都要一列有人簽、最長 180 天的 considerations,單人專案負擔太大。改採 Claude S10 的做法:使用者給網址的功能必須另登 outbound_call,由 `inventory_complete` 抓漏登。 |
| Codex#8 | secrets-crypto 拆成 secrets-management 與 crypto-transport | 部分採納 | 拆,理由見下〈衝突取捨〉（a）;但拆法不同:傳輸（TLS）移到 config-deploy 與 outbound,新類 crypto-use 只管程式裡的加密用法,最低 behavior、review,不加 deployment。 |
| Codex#9 | supply-chain 涵蓋既有與間接依賴、CI 動作、digest、安裝權限、持續處理漏洞 | 採納 | 草案只問「新加的」,漏了既有依賴的新漏洞;review 核來源與權限、掃描涵蓋實際交付依賴寫進替代欄與 `@repo` 說明。 |
| Codex#10 | config-deploy 補 API9 清冊與除錯介面;最低加 deployment;「外部不可達」另要 behavior | 部分採納 | 模板與 deployment 採納（設定檔掃描證不了平台上的實際狀態）;「外部不可達另要 behavior」是條件式,改成由 review 的 `category_sufficient` 判斷要不要附。 |
| Codex#11 | audit 最低改 behavior、deployment、review;模板補成功／拒絕／失敗事件、日誌注入、刪改、秘密入紀錄;入口改全部 | 部分採納 | behavior 與模板採納;deployment 不放進最低（儲存層防竄改與保存期限確認輪移到 config-deploy,另登 `@repo` 護欄）;日誌注入歸 input-injection;入口不改全部（理由同 Codex#7）;確認輪改成除了 outbound_call 以外的十種入口,模板限定安全相關操作與敏感資料存取（原先「會改狀態或帶走資料的六種入口」漏了 file_upload、file_download 等,說法已改正）。 |
| Codex#12 | frontend-origin 從「誰負責」改成可測的防護題;補點擊劫持、瀏覽器儲存、跨視窗訊息;工具加瀏覽器整合測試;arch-fe-origin 答案不能當驗證 | 採納 | 全收;瀏覽器測試歸在既有 runner 底下（Playwright 輸出 JUnit）,不新增工具類別;cookie、CSRF 留在 authn-identity,見 Claude S2。 |
| Codex#13 | 人工替代不能都叫 deployment;要嘛新增 `manual_verification`,要嘛正式擴充背景定義 | 部分採納 | 同意語意錯置;但不新增種類,改用 review 加要人判斷 `manual_check_scope`,見〈衝突取捨〉（c）。 |
| Codex#14 | 全表補安全失敗附問;`@repo` 證據要寫明涵蓋的服務與環境 | 採納 | 安全失敗寫成每題固定附問（ASVS V16.5）;`@repo` 涵蓋範圍由 `inventory_complete` 判斷。 |
| Codex#15 | 工具欄標明各自產生的種類、必要或補充;dynamic_scan 不抵 behavior | 部分採納 | 欄名不改（漂移測試與兩篇計劃都用這個欄名）,改成每項後面括號寫產生的種類並標「補充」;每類都補上「人工或獨立審查（review）」。 |
| Codex#16 | 不整批合併;加「標準對應只是索引」;補 ASVS V3（authn）、V13（outbound）、WSTG INFO;條件式記憶體安全提示 | 採納 | 都收;V3、V13 已回原文核對節號（3.3／3.4.2／3.5、13.2）;INFO 草案本來就有。 |

### Claude

| 編號 | 意見 | 處置 | 理由 |
|---|---|---|---|
| Claude#M1 | authz-object 問不到功能層級授權與批量賦值;STRIDE 補 T | 採納 | 跟 Codex#1 一致;ASVS 另補 V15（15.3.3 批量賦值,已核原文）。 |
| Claude#M2 | XSS 問不到;input-injection 補輸出語境,frontend-origin 補不安全 HTML 插入與 CSP | 採納 | 跟 Codex#3、#12 一致。 |
| Claude#M3 | input-injection 點名反序列化與 XXE | 採納 | 跟 Codex#3 一致;ASVS 1.5.1、1.5.2 已核。 |
| Claude#M4 | authn-identity 補暴力嘗試、帳號列舉、重設權杖 | 採納 | 跟 Codex#2 一致。 |
| Claude#M5 | authn-identity 最低證據加 fault_sensitivity | 採納 | 見〈衝突取捨〉（b）。 |
| Claude#M6 | input-injection、file-handling 的 deployment 替代語意錯配;建議甲（behavior 反例 + 寫明清單的 review） | 採納 | 見〈衝突取捨〉（c）;同一條規則也套到 secret_scan、dependency_scan。 |
| Claude#S1 | API3 只留 authz-object,data-exposure 收窄 | 採納 | 角色相關的欄位外洩只有在有角色維度的類別才問得準。 |
| Claude#S2 | cookie、CORS、CSRF 兩處都問;建議甲（只在 authn-identity 問）,authn 補 V3、CLNT | 採納 | 採甲;CORS 是 CLNT-07、CSRF 是 SESS-05,已核。 |
| Claude#S3 | authz-object 入口補 webhook_in、message_consumer、batch | 採納 | 同 Codex#1。 |
| Claude#S4 | flow-abuse 入口補 export、file_download、batch、admin | 採納 | 同 Codex#4 的採納部分。 |
| Claude#S5 | 跳步驟不需要 concurrency;注腳豁免或拆類 | 採納（拆類） | 注腳豁免是條件式下限,閘門做不到;拆出 flow-sequence（behavior、review）。 |
| Claude#S6 | file-handling 補惡意內容、壓縮檔、CSV 公式;路徑穿越歸 file-handling | 部分採納 | 惡意內容、壓縮檔、路徑穿越歸屬採納;CSV 公式改歸 input-injection（它是輸出語境的注入,input-injection 適用全部入口本來就問得到）。 |
| Claude#S7 | audit 對 admin 加 behavior;可加 webhook_in | 部分採納 | 最低種類是每類固定的,不能只對 admin 加,所以整類改 behavior、review;入口加 webhook_in 等。 |
| Claude#S8 | config-deploy 在沒有可掃檔的 repo 會空掃 | 採納 | 替代欄寫明「沒有可掃檔就不登記這類工具」;登記了卻空掃,閘門照既有規則判 `coverage_unproven`。 |
| Claude#S9 | config-deploy 掛 API9 但證據證不了 | 採納 | 模板補問舊版與沒列管的端點;deployment 與 review 承擔,不靠 config_scan。 |
| Claude#S10 | 使用者給網址的 SSRF 易漏;要求另登 outbound_call;靜態分析標補充 | 採納 | 見 Codex#7 的處置。 |
| Claude#S11 | CodeQL 對私有商用 repo 不免費 | 採納 | 列進連動:驗收閘工具表 CodeQL 後註明。 |
| Claude#S12 | 記憶體安全類寫明在範圍外 | 採納 | 跟 Codex#16 的條件提示合併寫。 |
| Claude#S13 | input-injection STRIDE 改 T、I、E;密碼雜湊與弱演算法要有人問;webhook／consumer 問簽章與重送 | 採納 | 密碼雜湊與弱演算法放進新類 crypto-use;簽章與重送放進 authn-identity 括號題。 |

### 確認輪處置

兩家確認都判不可核可;以下逐條處置,改動已併進上方〈定稿表〉。

| 編號 | 意見 | 處置 | 理由 |
|---|---|---|---|
| Codex-C#1 | 瀏覽器安全附問限定 http_api、web_page、admin,登成 file_upload 的 cookie 驗證匯入端點問不到 CSRF | 採納 | 一個入口只有一個 kind、不繼承別的 kind 的題目;改成「這個入口若供瀏覽器使用,且會自動帶憑證或允許跨來源呼叫,另問」,判準是瀏覽器憑證,不是 kind。authn-identity 的適用入口本來就含 export、file_upload、file_download,改完都問得到。 |
| Codex-C#2 | flow-sequence 漏了 batch、file_upload、cli | 採納 | 批次對已取消訂單出貨、匯入負數量都是跳步驟或竄改業務參數,別類補不上;沒有這類流程的入口照常用 considerations 判不適用。 |
| Codex-C#3 | audit 排除 web_page、file_upload、file_download、cli 不成立;模板限定安全相關操作 | 採納 | 入口改成除了 outbound_call 以外的十種;模板限定登入、權限變更、改狀態操作、被拒嘗試、防護失效與敏感資料讀取、匯出、下載,寫明不要求記錄普通瀏覽,避免格子變多後負擔失控。處置清單 Codex#11 的「六種」說法已改正。 |
| Codex-C 其他（CLI 不能一律當沒跨信任邊界;#6 另登補救要成明文） | — | 採納 | 寫成定稿表下方〈誰問什麼〉的明文盤點規則「一個功能兼有多種性質時,每種性質各登一個入口」,CLI 那一項明說不因為是操作者啟動就當成沒跨邊界;Codex#4、#6 的理由一併改正。 |
| Codex-C 其他（單人可行性:唯一的人也是作者時找不到審查人） | — | 列待辦 | 這是背景閘門「審查人不能是作者」的限制,不在這張表改;列進〈對姊妹計劃的連動〉。 |
| Claude-C#1 | 備份與保存期限放在證據證不了的 data-exposure;「另標 config-deploy」會帶進不相干的 config_scan,而且漏標擋不住 | 採納（甲） | 備份、快照、日誌保存與儲存層防竄改搬進 config-deploy 的模板（它是 `@repo`、最低種類已含 deployment）;data-exposure 只留應用程式自己產生的暫存;部署面宣稱改成另登一條 `@repo` 的 config-deploy 護欄,刪掉「另標」那套,連動清單同步。audit 的「能不能被刪改」只留應用層有沒有刪改途徑。 |
| Claude-C#2 | audit 入口跟「會改狀態或帶走資料」的理由不一致,漏 file_upload、file_download | 採納 | 跟 Codex-C#3 合併處理,入口範圍取 Codex 較寬的版本（另加 web_page、cli）;Claude 認為 web_page、cli 可不加,但 Codex 舉的帳號管理表單與 CLI 高權限操作確實需要追查,模板已限定範圍,負擔可控。 |
| Claude-C 建議1 | 兼有多種性質的入口寫成統一另登規則 | 採納 | 見 Codex-C 其他第一列。 |
| Claude-C 建議2 | 開放重新導向與 OAuth 回呼沒有一題點名 | 採納 | authn-identity 瀏覽器括號題補「登入後跳轉與 OAuth 回呼目的地白名單、state 或 PKCE」;ASVS 補 3.7（3.7.2 已核原文）。 |
| Claude-C 建議3 | WebSocket 握手來源沒點名、V4 沒掛 | 採納 | 同一括號題補「WebSocket 握手有沒有驗 Origin 與身分」;ASVS 補 V4（4.4,4.4.2 已核原文）。 |
| Claude-C 建議4 | 單一請求的資源上限（分頁、本文大小、ReDoS）也被迫交 concurrency | 不採納（暫不拆） | Claude 自己也判不阻擋:junit 並發測試門檻低、單人做得到;再拆一類會多一組格子。先觀察實際護欄有沒有因此不標 flow-abuse,有再比照 flow-sequence 拆。 |
| Claude-C 建議5 | 漂移測試分欄寫清楚哪些比集合、哪些比整串 | 採納 | 寫進〈標準對應〉的「漂移測試分欄比」:八欄比集合,模板、工具、替代三欄比整串;單一來源那一條改成引用它;連動清單同步提問計劃的漂移測試條款。 |
| Claude-C 建議6 | 「deployment 一律要人」那句理由在定稿後不再成立 | 採納 | 規則不變,理由半句列進連動第 1 條一起改。 |
| Claude-C 建議7 | 秘密掃描的人工替代,核對範圍跟綁定對不上 | 採納 | secrets-mgmt 替代欄補「這次核對只對紀錄當時的提交有效,寫進 limitations」;綁定規則本身是閘門天花板,不在本表改。 |
| Claude-C 三之一（審查人不能是作者,單人可能找不到人） | — | 列待辦 | 同 Codex-C 單人可行性那一列。 |
| Claude-C 三之二（`@repo` 護欄的家列太寬會一直重簽） | — | 採納 | 〈下限與替代怎麼算〉補一條:`@repo` 護欄的家只列秘密設定、部署設定、鎖檔這類真正承擔的檔。 |

### 兩家衝突的三點:取捨與理由

**（a） secrets-crypto 要不要拆:拆成 `secrets-mgmt` 與 `crypto-use`。**
- 下限是聯集:草案一條「驗簽失敗要拒絕」的護欄只要標了 secrets-crypto,就被迫交一份 secret_scan,而秘密掃描對驗簽正不正確什麼也證不了;作者為了避開不相干的證據,會乾脆不標這一類。不拆,證據就對不上它要證的事。
- 拆法跟 Codex 不同:傳輸保護（TLS、HSTS）是部署設定,放進 config-deploy（本來就要 deployment）;對外連線驗憑證放進 outbound;crypto-use 只管程式裡的雜湊、加密、簽章、亂數與密碼儲存,最低 behavior、review（竄改的權杖被拒、密碼雜湊格式對,單人做得到）。這樣 Claude 指出的「密碼雜湊與弱演算法沒人問」也有了去處。
- 兩類都維持 `@repo`,不逐入口展開。

**（b） authn-identity 最低證據要不要加 fault_sensitivity:加。**
- 身分驗證最常見的假綠是「測試裡被拒,其實是別層拒的」或測試環境把驗證整段跳過。behavior 的合法對照證明不了「被拒的原因就是這道防護」;`legit_control_real` 是人工判斷,fault_sensitivity（拿掉這道防護後目標斷言翻紅）是機械能證的。
- 成本:工具是專案本來就有的 runner 加 lumos guard kill,跟 authz-object 同一套,單人做得到;Codex 說「可維持」只是沒看到需要,沒有指出加了做不到。

**（c） 沒有工具時的替代:不新增 `manual_verification`,改成「behavior 惡意輸入反例 + review 多蓋要人判斷 `manual_check_scope`」。**
- deployment 證的是「實際部署設定符合」;拿它記「人工看過程式碼、秘密或依賴」確實是語意錯置（兩家都同意這點）。
- 不新增種類也不會錯置:人工核對本來就是 review 的範圍（人工判斷、要非作者、要綁版本與時效）,缺的只是「這次核對了什麼範圍」這一項,在〈機械做不到的判斷〉表加一個判斷 id 就補得上;程式碼類再要 behavior 反例,這是背景已有、而且能機械判的種類。
- 新增 manual_verification 要動種類表、格式對照、工具類別表、盤點值域與 schema 說明五處,還會跟 review 的紀錄規則重疊成兩套;加一個判斷 id 只動判斷表與「要蓋哪些判斷」那一句。
- 強度不降:`manual_check_scope` 設成要人,跟 deployment 一律要人同等;而且只在走替代欄時才要蓋,不加重有工具的護欄。
- config-deploy 的 config_scan 照舊換成 deployment,因為那真的是部署設定。

---

## 〈對姊妹計劃的連動〉

只列定稿改到、兩篇計劃要同步的地方;兩篇都不是本次可改的檔,由那個工作樹的作者處理。

### `Projects/安全主張驗收閘_計劃`

1. **〈二〉〈證據種類（schema v2,契約變更）〉表的 deployment 列**:「證明什麼」從「實際部署設定符合（沒有工具時）」改成「實際部署設定符合（人工核對平台上的實際設定;也是 config_scan 沒有工具時的替代）」。理由:定稿裡 secrets-mgmt、config-deploy 直接把 deployment 列為最低種類,不再只是替代。同時改〈機械做不到的判斷〉裡「deployment 一律要人:deployment 是『沒有工具時的人工核對』,代替的是一個掃描工具」的理由半句,改成「deployment 是人工核對平台上的實際設定,機械驗不了」;規則（一律要人）不變。
2. **同表 concurrency 列**:「證明什麼」從「重送、並發、壓力下他人操作仍不生效」改成「重送、並發、壓力下,宣告不該生效的操作（他人操作、重複生效、超過配額）仍不生效」;合法對照要求不變。
3. **〈二〉〈最低種類怎麼算〉的替代那一條**:例句「例如沒有秘密掃描工具時 secret_scan 換成 deployment」改成「例如沒有設定與容器掃描工具時 config_scan 換成 deployment;沒有秘密掃描工具時 secret_scan 換成 review 多蓋判斷 `manual_check_scope`」;並補一句「替代可以是『已在集合裡的種類多蓋一項判斷』,這時被替代的種類照樣列出、標明走了替代」。
4. **〈二〉〈機械做不到的判斷〉表**:新增一列 `manual_check_scope`|沒有工具時的人工核對:紀錄寫明原本工具該掃的範圍、逐項核對清單、原始材料、限制與重驗條件;程式碼類的清單每項要有 behavior 惡意輸入反例|是。
5. **同節「每條護欄的 review 種類要蓋住哪幾項判斷」那一句**:「表裡全部『要人』的項一律要蓋」改成「表裡『要人』的項一律要蓋,`manual_check_scope` 只在這條護欄的最低種類走了類別表的替代欄時才要蓋」。
6. **同表 `inventory_complete` 列**:「要審什麼」補「`@repo` 四類的證據涵蓋了 repo 裡全部服務、部署環境、依賴清單與秘密來源;依使用者輸入網址發出請求的功能有另登 outbound_call」。
7. **同表 `category_sufficient` 列**:「要審什麼」補「證據對到護欄宣稱的處理點或授權維度;宣稱外部不可達的設定護欄是否另附 behavior」。
8. **〈三〉工具類別表**:
   - 「靜態分析」列候選工具 `Semgrep、CodeQL` 改成 `Semgrep CE、CodeQL（私有 repo 需 GitHub Advanced Security 授權）`。
   - 「既有單元與整合測試 runner」列候選工具補「瀏覽器端整合測試（如 Playwright,輸出 JUnit）」。
9. **〈二〉〈最低種類怎麼算〉的 REVISIT 那一行**（只宣告 behavior 的護欄被擋的真實樣本）:不必改;但實作鏡像常數時,類別 id 要用定稿的 14 個（見下方新舊對照）。
10. **〈一〉schema v2 欄位清單 `threat_categories` 那一列**:不用改欄位定義;若那裡或其他段落有列舉類別 id 當例子,`secrets-crypto` 改成 `secrets-mgmt` 或 `crypto-use`（2026-10-20 grep 這篇沒有直接寫到任何類別 id,目前無須改）。
11. **待辦（不在本表改,背景閘門的限制）**:〈機械做不到的判斷〉規定審查人不能是作者;單人專案若程式由使用者本人寫、不是 AI 寫,唯一的人就是作者,找不到合格的 human 審查人,而且不能用另一個 AI 代替。要在這篇寫明「AI 寫、人審」是前提,並另議唯一的人也是作者時怎麼辦（例如外部審查人、或明文接受這個缺口並附回頭條件）。

### `Projects/資安風險提問分階段_計劃`

1. **〈二〉「### 威脅類別表」整節**:換成本檔〈定稿表〉。
2. **〈一〉保留入口 `@repo` 那一段**:「給以 repo 為單位問一次的三類（secrets-crypto、supply-chain、config-deploy）」改成「四類（secrets-mgmt、crypto-use、supply-chain、config-deploy）」;〈二〉開頭「以 repo 為單位的三類」、〈四〉「以 repo 為單位的三類:護欄的 surfaces 與 assets 寫 @repo」也一併改成四類。
3. **〈二〉開頭有角色維度的三類**:仍是 authz-object、authn-identity、flow-abuse 三類（新增的 flow-sequence 沒有角色維度）,這句不用改。
4. **〈二〉「### 威脅類別表」底下「單一來源」那一條**:「要改表先改圖譜正本、經使用者核可升版,再改常數」改成「依 d5 經 Claude 與 Codex 雙家一致核可升版」（現行全文還留著 d1 的說法,跟同節開頭的 d5 矛盾）。
5. **〈三〉候選題輸出**:產生候選題時,每一題尾端固定附「這道防護依賴的服務逾時、丟例外或不可用時,是拒絕還是放行?」;要寫進候選題產生的規則與對應測試,不寫進表的模板欄（免得 14 列都重複一句、漂移測試多比一段）。
6. **〈三〉需求風險面表的 `arch-sec-secrets`**:問題句不改（d7 不改既有風險面;這是新列,可改但不必）,它對應的格子類別從 secrets-crypto 改成 secrets-mgmt;若那一列或說明有寫到類別 id,一併改。
7. **〈一〉inventory 的 surfaces 說明**:補盤點規則「一個功能兼有上傳、下載、匯出、外呼、批次處理或訊息消費多種性質時,每種性質各登一個對應 kind 的入口;依使用者給的網址或主機名發出請求的功能必須另登 `outbound_call`;CLI 處理外來檔案、遠端資料或做高權限操作時照性質另登,不因為是操作者啟動就當成沒跨信任邊界」。
8. **〈四〉去向那一段（護欄覆蓋格子）**:補一句「備份、快照、日誌保存、儲存加密、日誌防竄改這類部署面宣稱,另登一條 `surfaces`、`assets` 為 `@repo`、`threat_categories` 含 config-deploy 的護欄,不在入口護欄上加標 config-deploy」;原草案裡「另標 config-deploy」的補法已撤掉,姊妹計劃若有引用一併刪。
9. **〈五〉驗收條款 S12（漂移測試）**:比法改成「id、STRIDE、ASVS、WSTG、API、適用入口、有角色維度、最低證據種類八欄比集合;模板、工具類別、沒有工具時三欄比整串」,manual 驗收樣本補「改模板裡一個頓號前後順序」應紅的一份。
10. **入口詞彙**:沒有新增或改名,`kind` 值域維持 11 個,不用改。
11. **證據種類值域**（〈一〉controls 的 `required_evidence`）:沒有新增種類,不用改。
12. **〈五〉驗收條款**:S1（格子逐列）的合成樣本若用到 secrets-crypto,改成新 id;S15（`@repo` 放行）的說明「secrets-crypto 等三類」改成「secrets-mgmt 等四類」。

### 類別 id 新舊對照

| 草案 id | 定稿 id | 說明 |
|---|---|---|
| authz-object | authz-object | 不變 |
| authn-identity | authn-identity | 不變 |
| input-injection | input-injection | 不變 |
| flow-abuse | flow-abuse | 不變（跳步驟拆出去） |
| — | flow-sequence | 新增:跳步驟、亂序、竄改業務參數 |
| data-exposure | data-exposure | 不變 |
| file-handling | file-handling | 不變 |
| outbound | outbound | 不變 |
| secrets-crypto | secrets-mgmt | 拆出:秘密放哪、誰讀得到、怎麼輪替 |
| secrets-crypto | crypto-use | 拆出:程式裡的雜湊、加密、簽章、亂數、密碼儲存（傳輸保護移到 config-deploy 與 outbound） |
| supply-chain | supply-chain | 不變 |
| config-deploy | config-deploy | 不變 |
| audit | audit | 不變 |
| frontend-origin | frontend-origin | 不變 |

共 14 類（草案 12 類）。
