結論: 不可核可

審查人:Claude(獨立審,未讀 threat-confirm-codex*、threat-review-codex*、threat-review-claude.md)
審查日:2026-10-20
讀過的材料:`threat-table-v1-final.md` 全文、`threat-table-v1.md`(草案)、`安全主張驗收閘_計劃` 的〈一〉〈二〉〈三〉(含證據種類表、最低種類怎麼算、綁版本、機械做不到的判斷、工具類別表)、`資安風險提問分階段_計劃` 的〈一〉〈二〉〈三〉〈四〉。

整體判斷:跟草案比,定稿補得很完整:授權、身分、注入、XSS、XXE、反序列化、SSRF、檔案、秘密、加密、供應鏈、設定、前端都有地方問;沒有工具時的替代改成「review 多蓋一項要人判斷」,也解掉了語意錯置。剩下兩處必改。兩處都是「表自己訂的規則跟它自己的欄位對不上」,改起來很小,但不改的話,有一類重要的宣稱證據證明不了,另一類入口會問不到。

---

## 一、必改

### 必改 1:備份與保存期限的問題放在證據證明不了的類別;「另標 config-deploy」這條補法會順手帶進不相干的 config_scan

**原文**
- data-exposure 模板:「……共用快取、匯出暫存與備份,會不會帶出……?暫存與備份多久刪、刪了沒?」,最低證據種類是「behavior、review」。
- 〈下限與替代怎麼算〉:「宣稱備份、保存期限、儲存加密、日誌防竄改這類部署面控制的護欄,除了 data-exposure 或 audit 之外另標 config-deploy,聯集自然帶進 deployment。」

**問題**
1. 「備份多久刪、刪了沒」是部署平台上的事實(備份排程、物件儲存的生命週期規則)。behavior(單元或整合測試)證明不了生產環境的備份真的會刪。data-exposure 的最低種類又沒有 deployment,所以照表問出來的這一題,最低證據證明不了它要問的防護。
2. 補法靠作者「自己記得另標 config-deploy」。閘門機械上擋不住漏標,只能靠 review 的 `category_sufficient` 抓,而這一項在背景定義裡是「不要人」,AI 紀錄就能放行。在單人加 AI 代操作的情境下,AI 寫「備份 30 天後刪」只附 behavior,照樣算 sound。
3. 就算作者照做另標了,config-deploy 的最低種類是「config_scan、deployment、review」。專案只要登記了設定掃描工具,替代欄就不生效,作者得另交一份對 IaC 的 config_scan SARIF(還要有校準與覆蓋證明),而這份掃描證明不了備份保存期限。這正是定稿〈衝突取捨〉(a) 拿來拆 secrets-crypto 的理由:「作者為了避開不相干的證據,會乾脆不標這一類」。同一個問題在這裡又出現一次。

**具體改法(擇一,建議甲)**
- 甲:把部署面的問題整個搬到以 repo 為單位問的類別。
  - data-exposure 模板刪掉「與備份」「暫存與備份多久刪、刪了沒?」,改成只問應用程式自己產生的暫存:「匯出與暫存檔多久刪、應用程式有沒有刪?」(這一題 behavior 測得到)。
  - config-deploy 模板補一句:「備份、快照與日誌存在哪、多久刪、有沒有加密、誰能刪改?」config-deploy 本來就是 `@repo`,最低種類也已經含 deployment,問的地方跟證據就對上了。
  - 〈下限與替代怎麼算〉那一條改成:「宣稱備份、保存期限、儲存加密、日誌防竄改這類部署面控制,另登一條 `surfaces`／`assets` 為 `@repo`、`threat_categories` 含 config-deploy 的護欄,不在 data-exposure 或 audit 的護欄上加標」。這樣入口層的護欄不會被迫交 config_scan;部署面的宣稱也一定會落在一個有 deployment 下限的 `@repo` 格子裡,而且那一格沒有去向時會顯示 open。
- 乙:如果要保留「另標」的寫法,至少在處置清單 Codex#5 的理由寫明:「另標 config-deploy 時,專案有登記設定掃描工具,就也要交 config_scan」;另外把「部署面宣稱有沒有另標 config-deploy」從 `category_sufficient`(不要人)拆成一個要人的判斷。乙比甲多動姊妹計劃的判斷表,也沒解掉第 3 點,所以不建議。

audit 模板的「紀錄能不能被刪改?」是同一族問題:應用層不給刪改的介面,behavior 測得到;儲存層防竄改則是部署面。照甲,前者留在 audit,後者歸進上面 config-deploy 補的那一句。

### 必改 2:audit 的適用入口跟它自己寫的選擇理由不一致,漏了 file_upload 與 file_download

**原文**
- audit 列的適用入口:「admin、http_api、webhook_in、message_consumer、batch、export」
- 處置清單 Codex#11:「入口不改全部(理由同 Codex#7),改成會改狀態或帶走資料的六種入口。」

**問題**
姊妹計劃〈一〉規定一個入口只有一個 `kind`。照「會改狀態或帶走資料」這條準則,`file_upload`(寫入檔案,改狀態)與 `file_download`(把資料帶走)都符合,卻不在清單上。上傳與下載就不會長出 audit 格子:「誰在什麼時候下載了含個資的檔案,事後查不查得到」這一題對下載入口問不到。中小型 Web/API 後端最常見的資料外流路徑之一,就是批次下載與附件下載;它的可追溯性也是個資法令最常要求的紀錄。export 有列、file_download 沒列,這也說不通。

**具體改法**
audit 的適用入口改成「admin、http_api、webhook_in、message_consumer、batch、export、file_upload、file_download」;處置清單 Codex#11 的「六種入口」改成「八種入口」。web_page 與 cli 不加也合理(web_page 改狀態時實際打的是 http_api;cli 是操作者自己跑的),但理由要寫進同一格,讓下一個讀的人看得出是刻意排除的。

---

## 二、處置清單裡「不採納／部分採納」的理由是否成立

| 編號 | 判定 | 說明 |
|---|---|---|
| Codex#2(authn 不加 batch) | 成立 | batch 沒有呼叫進來的身分;服務帳號權限歸 authz-object、憑證歸 secrets-mgmt,分得清楚。 |
| Codex#4(flow-abuse 不加 outbound_call、cli) | 成立 | 費用由觸發它的入口問,batch 已在清單上;cli 由操作者自己跑,沒有跨信任邊界。 |
| Codex#5(備份不設條件式 deployment) | **理由本身成立,替代做法不成立** | 「閘門做不到條件式下限」是對的,但換成「另標 config-deploy」會留下必改 1 的缺口。 |
| Codex#6(file-handling 不加 cli) | 成立 | 「有外來檔就該登 batch 或 file_upload」講得通;建議把它寫成通則,見建議 1。 |
| Codex#7(outbound 不改「全部」) | 成立 | not_applicable 每列要簽、最長 180 天,不外呼的入口逐一簽,單人負擔確實過重;改成「使用者給網址的功能另登 outbound_call」,問到的範圍跟原提案相同。 |
| Codex#8(拆法不同) | 成立 | TLS 歸 config-deploy 與 outbound、crypto-use 只管程式裡的用法,證據也對得上。 |
| Codex#10(外部不可達不設條件式 behavior) | 成立 | 交給 `category_sufficient` 判,這是可接受的天花板。 |
| Codex#11(audit 不加 deployment、入口不改全部) | **一半成立** | 不加 deployment 成立(照必改 1 的甲,防竄改改由 `@repo` 的 config-deploy 承擔,會更乾淨);入口理由跟清單不一致,見必改 2。 |
| Codex#13(不新增 manual_verification) | 成立 | 人工核對本來就屬 review 的範圍;`manual_check_scope` 設成要人,強度跟 deployment 一律要人相同,而且只有走替代欄時才要蓋,不會加重有工具的專案。「清單每點有沒有 behavior 反例,機械不比對」這個缺口已經寫了一條帶事件條件的 REVISIT,算有回頭條件。 |
| Codex#15(欄名不改) | 成立 | 每項加括號寫產生的種類、標補充,已經達到原意。 |
| Claude#S6(CSV 公式改歸 input-injection) | 成立 | 它是輸出語境的注入,input-injection 又適用全部入口,問得到。 |
| Claude#S7(audit 整類改 behavior) | 成立 | 最低種類是每類固定的集合,不能只對 admin 加。 |

---

## 三、單人專案做不到的下限

**表本身新增的下限,單人都做得到**:
- authn-identity 的 fault_sensitivity:跟 authz-object 用同一套 runner 加 guard kill。
- flow-abuse 的 concurrency:用 runner 跑並發測試,調低配額即可。
- secrets-mgmt 與 config-deploy 的 deployment:要人簽,但每條護欄的 review 本來就要人簽要人的那幾項,多一筆的負擔不大。
- 掃描類:Semgrep CE、gitleaks、OSV-Scanner 都免費。CodeQL 對私有 repo 要授權,已列進連動。

沒有找到單人做不到的下限。下面兩點不是這張表造成的,是背景閘門的既有設計,列出來給編排者參考:
- 背景規定「審查人不能是作者」。如果程式由使用者本人寫、不是 AI 寫,單人專案就找不到合格的 human 審查人。目前的前提是 AI 寫、人審,這個前提成立時沒問題,但這個前提沒有寫在表裡。
- secrets-mgmt 與 config-deploy 每條護欄至少要兩筆人簽的紀錄(review 與 deployment 各一筆,一筆只算一個種類),期限 90 天,綁定的檔一改就要重簽。`@repo` 護欄的家如果 about_code 列得很寬,幾乎每次推送都要重簽。建議在〈誰問什麼〉補一句:`@repo` 護欄的家只列秘密、部署設定、鎖檔這類真正承擔的檔。

---

## 四、建議(不阻擋)

1. **一個入口兼具多種性質時,應寫一條統一的另登規則**。現在只有 outbound 有一條「使用者給網址的功能要另登 outbound_call」,cli 也只在處置理由裡提到「外來檔該登 batch 或 file_upload」。管理後台的 CSV／ZIP 匯入如果登成 `admin`,file-handling(zip slip、解壓上限、路徑穿越)整類不適用,問不到。建議把 outbound 那條改成通則:「一個功能同時有上傳、下載、匯出、外呼這些性質時,每種性質各登一個對應 kind 的入口」,由 `inventory_complete` 抓漏登。
2. **開放重新導向與 OAuth 回呼沒有一題點名**。authn-identity 掛了 V10(OAuth／OIDC),模板卻只問權杖的簽章、issuer、audience,沒問 redirect_uri 白名單、state／PKCE;登入後的 `next=` 開放重新導向(ASVS 5.0.0 V3.7)全表沒有地方問。小型 Web 後端很常接社群登入,建議在 authn-identity 的瀏覽器括號題補一句:「登入後跳轉與 OAuth 回呼的目的地有沒有限定白名單?state 或 PKCE 有沒有驗?」
3. **WebSocket 沒有被點名**。入口值域裡沒有 websocket,實際會被登成 http_api。CORS 管不到 WebSocket 握手,只設好 CORS 的開發者容易以為已經防住跨站。ASVS 5.0.0 V4(API 與 Web Service,含 4.4 WebSocket、4.2 HTTP 訊息結構)整章沒掛在任何類別上。建議在 authn-identity 的瀏覽器括號題補「WebSocket 握手有沒有驗 Origin 與身分」,並在 ASVS 欄補 V4.4。
4. **flow-abuse 裡「單一請求的資源上限」(分頁上限、請求本文大小、ReDoS)也要交 concurrency**。這跟 Claude#S5 拆出 flow-sequence 是同一種錯配:這類護欄 behavior 就證得了,concurrency 多餘。目前 junit 並發測試的門檻低、做得到,所以不阻擋;但可以考慮在模板註明「單一請求的上限也照樣要一個重送或並發案例」,或日後比照 flow-sequence 再拆。
5. **漂移測試的比法要分欄寫清楚**。〈寫法〉說「欄位內容照全形頓號切開成集合比」,但模板欄(「讀、改、刪」)與替代欄(括號裡的「guard kill、test-quality」)的文字本身含頓號。切成集合會丟掉順序,而且候選題產生要用的是模板原字串。建議寫明只有 STRIDE、ASVS、WSTG、API、適用入口、最低證據種類六欄比集合,模板、工具、替代三欄比整串。
6. **連動清單可多列一句**:驗收閘〈機械做不到的判斷〉裡「deployment 一律要人:deployment 是『沒有工具時的人工核對』,代替的是一個掃描工具」這句理由,在定稿之後不再成立(secrets-mgmt、config-deploy 把 deployment 列為固定下限)。規則不用改,理由那半句要跟連動 1 一起改。
7. **用秘密掃描的替代時,核對範圍跟綁定對不上**。`manual_check_scope` 核對的是工作目錄與 git 歷史,但 review 紀錄只綁護欄的家列的檔。之後別的檔新提交了一個秘密,這筆紀錄不會 stale,90 天內照樣算數。這是閘門綁定規則的天花板(用工具掃也有同樣的問題),不屬於這張表;建議在 secrets-mgmt 替代欄的 limitations 寫明「這次核對只對紀錄當時的提交有效」。
