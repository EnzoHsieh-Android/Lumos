結論: 修改後可核可

審查員:Claude(獨立審查,未讀另一位審查員的檔)
審查對象:`scratchpad/threat-table-v1.md`(威脅類別表 v1 草案)
背景對照:`security-gate` 工作樹的 `Projects/安全主張驗收閘_計劃.md`〈二〉證據種類表、〈三〉工具類別表;`Projects/資安風險提問分階段_計劃.md` 的入口 kind 值域(http_api、web_page、export、file_upload、file_download、webhook_in、outbound_call、batch、message_consumer、admin、cli)。
外部對照:OWASP ASVS 5.0.0 章節、WSTG v4.2、OWASP API Security Top 10 2023、CWE Top 25(2024)。以下 ASVS/CWE 對應憑審查員對這些標準的知識,沒有逐條重查原文;草案自己也寫了「其餘章節對應未逐條核對」。

整體判斷:骨架合理(12 類大致涵蓋 API Top 10 與 ASVS 主章;證據下限用「種類聯集 + 一律含 review」、替代欄可換算、以 repo 為單位的三類用 `@repo`,都站得住)。但有幾個常見且重要的威脅在模板句裡問不到(功能層級授權、批量賦值、XSS、反序列化、登入暴力嘗試),有一個替代種類的語意錯配,還有一個證據下限偏弱的地方。這些都是改字就能修,不需要重新設計,所以判「修改後可核可」。

---

## 必改

### M1. authz-object 的模板只問「物件層級」,問不到「功能層級授權」(API5 BFLA)與「批量賦值」(API3 寫入那一半)
- 原文:`{角色} 從 {入口} 能不能讀、改、刪不屬於他的 {資產}?被拒時資料與副作用怎樣?`,API 欄卻掛了 `API1、API3、API5`。
- 理由:API5(一般使用者呼叫到管理功能,也就是垂直越權)和 API3 寫入面(對**自己的**資產改了不該他改的欄位,例如 `role`、`price`、`owner_id`)都不是「不屬於他的資產」。照現在的句子,作者答完「別人的訂單讀不到」就算過了,API3、API5 實際上沒被問到。這兩類在中小型後端很常見,CWE-862/863 也都在 Top 25。
- 改法:模板改成「{角色} 從 {入口} 能不能 (1) 讀、改、刪不屬於他的 {資產};(2) 呼叫他的角色不該用的功能或管理操作;(3) 在自己的 {資產} 上改到不該他改的欄位(如角色、價格、擁有者)或讀到不該他看的欄位?被拒時資料與副作用怎樣?」。STRIDE 補 `T`(改、刪就是竄改)→ `E、I、T`。

### M2. XSS(CWE-79,CWE Top 25 第一名)在 12 類裡沒有任何一類的模板問得到
- 原文:input-injection 問「會不會被當成指令、查詢或路徑執行」;frontend-origin 問「前端跨來源、cookie、CSRF 與畫面上的敏感資料誰負責」。
- 理由:XSS 是「輸出到瀏覽器時沒編碼」,不是後端把輸入「執行」。純後端 repo 沒有 web_page 入口,frontend-origin 一格都不長,但後端回 HTML、錯誤頁、Email 範本、或把未編碼字串交給前端渲染,照樣造成 XSS。ASVS 5.0.0 的輸出編碼在 V1。
- 改法:input-injection 模板改成「{入口} 收到的輸入會不會被當成指令、查詢、路徑或範本執行,或原樣輸出到 HTML、JavaScript、Email、CSV 等別的語境(XSS 與輸出編碼)?」。frontend-origin 模板補「前端渲染時有沒有用到不安全的 HTML 插入(innerHTML、v-html、dangerouslySetInnerHTML)與 CSP」。

### M3. input-injection 沒點名反序列化(CWE-502)與 XML 外部實體(CWE-611)
- 原文:`會不會被當成指令、查詢或路徑執行?`
- 理由:不安全反序列化與 XXE 是 Java、.NET、Python(pickle、YAML)後端的典型高危,message_consumer、webhook_in 尤其常見;「當成指令執行」對作者來說不會自然聯想到這兩個。
- 改法:在 M2 改後的句子尾端補「(含反序列化成物件、解析 XML 外部實體)」。

### M4. authn-identity 沒問暴力嘗試、帳號列舉與重設密碼流程(API2 的主體)
- 原文:`身分從哪來、何時可信?偽造、過期、撤權後會怎樣?`
- 理由:API2 Broken Authentication 的大宗是缺少登入頻率限制、撞庫、帳號列舉、重設密碼權杖可預測或不失效,CWE-307 也屬這一族。現在的句子只問到權杖本身,單人開發最常漏的正是登入端點的頻率限制。
- 改法:句子補「登入、重設密碼、驗證碼這類端點能不能被暴力嘗試或用來列舉帳號?重設與邀請權杖會不會被猜到、重用或不失效?」。

### M5. authn-identity 的最低證據少了 fault_sensitivity,跟 authz-object 不對稱
- 原文:authn-identity 的 `behavior、review`;authz-object 的 `behavior、fault_sensitivity、review`。
- 理由:身分驗證最常見的假綠,是測試環境用替身或旗標把驗證整段跳過,測試照樣「偽造權杖被拒」(其實是別層拒的),或根本沒經過那條防護。behavior 依驗收閘〈二〉已經要求合法對照,但證明不了「被拒的原因就是這條防護」;fault_sensitivity(拿掉防護後目標斷言翻紅)正好補這個。工具是專案本來就有的 runner 加 lumos guard kill,單人專案做得到,不算過度要求。
- 改法:最低證據種類改成 `behavior、fault_sensitivity、review`;工具類別欄補「破壞測試與故障收證」。

### M6. input-injection、file-handling 的替代用 `deployment`,語意錯配
- 原文:`沒有靜態分析工具：static_analysis 換成 deployment（人工核對紀錄）`(兩類都這樣寫)。
- 理由:驗收閘〈二〉把 deployment 定義成「實際部署設定符合(沒有工具時)」。注入與檔案處理是程式碼裡的 sink,不是部署設定;換成 deployment 之後,審查人拿到的是一筆「核對部署設定」的紀錄,跟要補的「掃過指定規則、沒有未處置命中」對不上,閘門機械上通過,實際上沒有人核對程式碼。secrets-crypto、supply-chain、config-deploy 換成 deployment 是合理的(那些確實是部署與設定)。
- 改法(擇一,建議甲):
  - 甲:這兩類的替代改成「沒有靜態分析工具:static_analysis 換成 behavior 負例(每個 sink 至少一個惡意輸入案例)加一筆 review(範圍寫明逐項核對的 sink 清單)」。實務上 Semgrep CE 免費、可本機跑,幾乎不會走到替代,所以替代可以比較嚴。
  - 乙:如果要保留「換成一筆人工核對紀錄」的形狀,就在驗收閘〈二〉把 deployment 改名或擴寫成「沒有工具時的人工核對(部署設定或程式 sink 清單)」,並要求紀錄寫明核對範圍;表上照寫 deployment。這會動到姊妹計劃的契約,要一起過設計審。

---

## 建議

### S1. API3 同時掛在 authz-object 和 data-exposure,讀取面的歸屬不清
- 原文:authz-object `API1、API3、API5`;data-exposure `API3`,且 `有角色維度: 否`。
- 理由:「回應帶出不該給這個角色看的欄位」是依角色而定的,但 data-exposure 標了沒有角色維度,所以只能在 authz-object(有角色維度)裡問才準。兩邊都掛 API3 會讓同一件事被答兩次或兩邊都以為對方管。
- 改法:API3 只留在 authz-object(M1 已把讀、寫欄位都寫進模板);data-exposure 的 API 欄改成 `—`,模板收窄成「錯誤訊息、日誌、除錯輸出、URL 參數與快取會不會帶出 {資產} 的內容、秘密,或洩漏它存不存在?」。

### S2. CORS、CSRF、cookie 屬性在 authn-identity 和 frontend-origin 各問一次
- 原文:authn-identity 的 `(http_api 另問:session cookie 的 Secure、HttpOnly、SameSite…CORS…CSRF?)`;frontend-origin 的 `前端跨來源、cookie、CSRF…`。
- 理由:同一 repo 同時有 http_api 和 web_page 時,同一件事會在兩格各出一次;草案只寫了 frontend-origin 跟 `arch-fe-origin` 的去重,沒寫跟 authn-identity 括號題的去重。另外 CSRF、CORS 嚴格說不是「身分」問題,掛在 authn-identity 下 STRIDE 只有 S,也不準。
- 改法(擇一):
  - 甲(最小改):注腳加一句「同一 repo 同時有 http_api 與 web_page 時,cookie、CORS、CSRF 只在 authn-identity 的 http_api 格問,frontend-origin 的格子引用那個答案」;frontend-origin 模板拿掉 cookie、CSRF,改成問 XSS 渲染、CSP、點擊劫持、畫面與瀏覽器儲存裡的敏感資料。
  - 乙:另立一類 `browser-session`(cookie、CORS、CSRF),適用 http_api、web_page,從另兩類拿掉。
  - 不論哪個,authn-identity 的 ASVS 欄補 `V3`(ASVS 5.0.0 的 cookie 與瀏覽器來源隔離在 V3),WSTG 補 `CLNT`(CORS 是 CLNT-07)。

### S3. 入口漏配:message_consumer、webhook_in、batch 沒有 authz-object
- 原文:authz-object 適用 `http_api、web_page、export、file_upload、file_download、admin`。
- 理由:消費者或 webhook 依訊息裡的 `tenant_id`、`order_id` 去改資料時,如果不核對「這個來源有權動這筆」,就是代理人混淆(confused deputy),本質就是物件層級授權。batch 以系統身分跑,跨租戶處理時漏了範圍條件也是同一類。
- 改法:authz-object 適用入口補 `webhook_in、message_consumer、batch`(batch 的角色維度用「系統」這一個角色即可)。

### S4. 入口漏配:flow-abuse 少了 export、file_download、batch、admin
- 理由:大量匯出與下載是 API4(資源耗盡)、API6(爬取敏感業務流程)的典型入口;batch 重跑沒有冪等就會重複入帳;admin 的大量操作也會超量。
- 改法:flow-abuse 適用入口補 `export、file_download、batch、admin`。如果覺得 concurrency 對 export 這種唯讀入口過重,可在注腳寫「唯讀入口的 flow-abuse 以頻率限制與分頁上限的 behavior 負例滿足 concurrency」。

### S5. flow-abuse 對「跳步驟」要求 concurrency 對不上
- 原文:`重送、並發、大量或跳步驟` 對到 `behavior、concurrency、review`。
- 理由:跳步驟(跳過付款直接確認)是狀態機問題,證據是 behavior 負例;concurrency 證不了它,也不需要它。現在一格要求兩者聯集,只防跳步驟的護欄被迫補一份不相干的並發測試。
- 改法:注腳寫明「只宣稱防跳步驟或狀態機繞過的護欄,concurrency 可以免;宣稱防重送、並發、超賣、耗盡的才要」。或者拆成 flow-abuse(重送、並發、耗盡)與 flow-sequence(跳步驟),後者最低證據 `behavior、review`。

### S6. file-handling 少了幾個常見子題:惡意內容、壓縮檔、CSV 公式注入
- 原文:`檔名、內容、大小會不會讓人讀寫到別的檔或塞爆空間?`
- 理由:上傳 SVG/HTML 造成儲存型 XSS、Content-Type 被瀏覽器猜成可執行、zip slip 與解壓炸彈、匯出 CSV/Excel 的公式注入(CWE-1236)都是中小型後端常踩的,「內容」兩字作者不會自然想到這些。
- 改法:句子改成「…會不會讓人讀寫到別的檔、塞爆空間,或讓上傳的內容被當成網頁或程式執行(SVG/HTML、壓縮檔解開越界)?匯出的 CSV/Excel 會不會帶出可執行公式?」。另外,input-injection 的「路徑執行」跟 file-handling 的「讀寫到別的檔」都在問路徑穿越,注腳寫一句「檔案路徑穿越歸 file-handling,input-injection 不重複問」。

### S7. audit 只要 review,偏弱
- 原文:audit 的最低證據 `review`,工具欄 `—`。
- 理由:「事後查得到嗎」是可以機械驗的:對 admin 操作寫一支整合測試,斷言稽核紀錄真的寫進去、欄位齊全,合法對照就是正常操作也有紀錄。這不難,單人做得到;只靠 review,紀錄常在重構時悄悄斷掉。
- 改法:admin 入口的 audit 最低證據改成 `behavior、review`,工具欄補「既有單元與整合測試 runner」;http_api 可維持 review。「紀錄本身會不會被改」仍只能 review 或 deployment,維持。另可考慮把 webhook_in 加進 audit 適用入口(外部觸發的狀態改變事後最難追)。

### S8. config-deploy 對「沒有可掃設定」的 repo 會空掃通過或卡住
- 原文:`config_scan、review`,替代只在「沒有設定與容器掃描工具」時才換。
- 理由:很多中小型後端部署在 PaaS,repo 裡沒有 Dockerfile 或 IaC,Trivy config、Checkov 掃不到東西。這時要嘛產出空 SARIF(覆蓋證明應該擋,但要閘門那邊確實擋到),要嘛作者不知道怎麼辦。
- 改法:替代欄改成「沒有設定與容器掃描工具,**或 repo 裡沒有可掃的容器與 IaC 檔**:config_scan 換成 deployment(核對平台上的實際設定)」,並請姊妹計劃確認空掃描範圍判 `coverage_unproven`。

### S9. config-deploy 掛 API9 但證據證不了它
- 原文:config-deploy 的 API 欄 `API8、API9`。
- 理由:API9 是資產盤點管理不當(舊版 API、沒下線的測試端點、沒列管的環境),設定掃描查不出來。
- 改法:模板補「有沒有舊版、測試用或沒列在盤點裡的端點與環境還開著?」,並在注腳寫明 API9 這半題靠 review 與 inventory 對照,不靠 config_scan。

### S10. outbound 只能透過 outbound_call 入口觸發,使用者給 URL 的 SSRF 容易被漏
- 原文:outbound 適用 `outbound_call、webhook_in`。
- 理由:SSRF 最常見的形狀是 http_api 收到使用者給的 URL(頭像網址、webhook 註冊網址、匯入連結)再由伺服器去抓。適用與否只看入口 kind,如果作者沒有替「伺服器去抓」另登一個 outbound_call 入口,這一格就不會長。
- 改法:注腳加「伺服器會依使用者輸入的網址或主機名發出請求的功能,盤點時必須另登一個 outbound_call 入口」;模板補「重新導向與 DNS 指向內網會不會繞過限制?」。另外工具欄列了「靜態分析」但最低證據沒有 static_analysis,建議標成「(補充)」,跟 authz-object 的「動態掃描補充」寫法一致,免得讀者以為是必要。

### S11. 工具候選的可取得性:CodeQL 對私有商用 repo 不是免費
- 原文:驗收閘〈三〉靜態分析候選 `Semgrep、CodeQL`,本表 input-injection、file-handling 依賴它。
- 理由:CodeQL CLI 的授權只免費給開源與學術研究,私有商用 repo 要 GitHub Advanced Security;消費專案多半是私有 repo。其他候選(Semgrep CE、OSV-Scanner、Trivy、gitleaks、ZAP、k6、Checkov、hadolint、Jazzer、Atheris、Go fuzz)都是免費、可本機跑,沒問題。
- 改法:在姊妹計劃的工具表 CodeQL 後加「(私有 repo 需授權)」,或預設候選只寫 Semgrep CE。

### S12. 適用範圍外的 CWE Top 25 要寫明排除,避免被當成漏掉
- 理由:CWE Top 25 有記憶體安全類(越界讀寫、use-after-free、空指標),對 Java、Kotlin、Python、Node、C# 後端大多不適用,但審查者對照 Top 25 時會以為表漏了。
- 改法:注腳加一行「記憶體安全類 CWE(越界讀寫、use-after-free 等)在本表的受管語言後端範圍外;消費專案有 C/C++ 原生元件時另議」。

### S13. 細部對應
- input-injection 的 STRIDE 只有 `T`;注入常導致資料外洩與提權,建議 `T、I、E`。
- secrets-crypto 的模板沒問「密碼怎麼存(雜湊演算法與參數)」與「有沒有用到弱演算法或自寫加密」;密碼雜湊在 ASVS 5.0.0 屬 V6(authn-identity 已掛 V6),建議在 authn-identity 或 secrets-crypto 其中一處明寫,工具欄補「靜態分析(補充)」可抓弱演算法。
- authn-identity 的 webhook_in 與 message_consumer 格,建議模板括號補一句「(webhook_in、message_consumer 另問:簽章怎麼驗、時間戳與重送怎麼擋?)」,作者才不會只想到使用者登入。

---

## 逐類速覽(對照四個問題)

| id | 1. 漏或重疊 | 2. 最低證據 | 3. 工具與替代 | 4. 入口對應 |
|---|---|---|---|---|
| authz-object | 漏 BFLA、批量賦值(M1);API3 跟 data-exposure 重疊(S1) | 足夠(behavior 依〈二〉自帶反例 + fault_sensitivity) | 合理 | 漏 webhook_in、message_consumer、batch(S3) |
| authn-identity | 漏暴力嘗試與重設流程(M4);CORS/CSRF 跟 frontend-origin 重疊(S2) | 偏弱,補 fault_sensitivity(M5) | 合理 | 合理;webhook/consumer 子題建議明寫(S13) |
| input-injection | 漏 XSS(M2)、反序列化與 XXE(M3);路徑穿越跟 file-handling 重疊(S6) | 足夠 | 替代 deployment 錯配(M6);CodeQL 授權(S11) | 「全部」合理 |
| flow-abuse | 無 | 跳步驟不需 concurrency(S5) | 合理,runner 並發測試可取得 | 漏 export、file_download、batch、admin(S4) |
| data-exposure | API3 歸屬(S1) | 足夠 | 合理 | 合理 |
| file-handling | 漏惡意內容、壓縮檔、CSV 公式注入(S6) | 足夠 | 替代 deployment 錯配(M6) | 合理 |
| outbound | 無 | 足夠 | 靜態分析標補充(S10) | 使用者給 URL 的 SSRF 易漏(S10) |
| secrets-crypto | 密碼雜湊與弱演算法(S13) | 足夠 | 合理(gitleaks 免費) | `@repo` 合理 |
| supply-chain | 無 | 足夠 | 合理(OSV-Scanner 免費) | `@repo` 合理 |
| config-deploy | API9 對不上證據(S9) | 足夠 | 沒有可掃檔時的替代(S8) | `@repo` 合理 |
| audit | 無 | admin 偏弱(S7) | 補 runner(S7) | 可考慮加 webhook_in(S7) |
| frontend-origin | 跟 authn-identity 括號題重疊(S2);補 XSS 渲染與 CSP(M2) | 足夠 | 合理(ZAP 免費) | 合理 |

過度要求的檢查:沒有發現單人專案做不到的下限。所有必要種類的工具都免費、可本機跑(CodeQL 除外,但有 Semgrep CE 可替);M5 加的 fault_sensitivity 用的是專案本來就有的 runner 與 lumos guard kill。
