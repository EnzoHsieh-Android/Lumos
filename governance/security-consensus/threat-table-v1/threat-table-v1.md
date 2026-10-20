### 威脅類別表 v1（設計提案；實作時搬到 [[Systems/資安威脅類別表]] 當正本）

版號寫在這個標題上（現在是 v1）。依 d1，每次改版走設計審、由使用者核可，核可那次就升一號（v1→v2），核可決策記在 [[Systems/資安威脅類別表]] 的 decisions。**本篇這一輪對表的改動（file_upload、export、file_download、message_consumer 補類別，http_api 的身分模板多問 cookie、CORS、CSRF，「沒有工具時」改成可換算的替代欄）照 d1 只是提案，要使用者核可後才算 v1 的內容**。

| id | 要問什麼（模板） | STRIDE | ASVS 5.0.0 | WSTG v4.2 | API Top10 2023 | 適用入口 | 有角色維度 | 最低證據種類 | 能產生證據的工具類別 | 沒有工具時（由驗收閘依工具清單換算） |
|---|---|---|---|---|---|---|---|---|---|---|
| authz-object | {角色} 從 {入口} 能不能讀、改、刪不屬於他的 {資產}?被拒時資料與副作用怎樣? | E、I | V8 | ATHZ | API1、API3、API5 | http_api、web_page、export、file_upload、file_download、admin | 是 | behavior、fault_sensitivity、review | 既有單元與整合測試 runner、破壞測試與故障收證；動態掃描補充 | 無替代（測試 runner 與 lumos 的 guard kill、test-quality 在專案裡本來就有） |
| authn-identity | {角色} 在 {入口} 的身分從哪來、何時可信?偽造、過期、撤權後會怎樣?(http_api 另問:session cookie 的 Secure、HttpOnly、SameSite 怎麼設?允許哪些跨來源(CORS)?改狀態的請求怎麼防 CSRF?) | S | V6、V7、V9、V10 | IDNT、ATHN、SESS | API2 | http_api、web_page、admin、webhook_in、export、file_upload、file_download、message_consumer | 是 | behavior、review | 既有單元與整合測試 runner、動態掃描（含登入證據） | 無替代（不做登入的示範專案寫明「身分可信」是未驗前提，走 considerations） |
| input-injection | {入口} 收到的輸入會不會被當成指令、查詢或路徑執行? | T | V1、V2 | INPV | — | 全部 | 否 | behavior、static_analysis、review | 既有單元與整合測試 runner、靜態分析、模糊測試、動態掃描 | 沒有靜態分析工具：static_analysis 換成 deployment（人工核對紀錄） |
| flow-abuse | 重送、並發、大量或跳步驟時，{角色} 能不能讓 {資產} 被他人操作生效、超賣或耗盡? | T、D | V2 | BUSL | API4、API6 | http_api、web_page、webhook_in、message_consumer、file_upload | 是 | behavior、concurrency、review | 既有單元與整合測試 runner（並發測試）、壓測與並發 | 無替代（沒有壓測工具時 concurrency 用 runner 的並發測試，格式 junit） |
| data-exposure | 錯誤訊息、日誌、回應欄位會不會帶出 {資產} 或它存不存在? | I | V14、V16 | ERRH、INFO | API3 | 全部 | 否 | behavior、review | 既有單元與整合測試 runner、動態掃描 | 無替代 |
| file-handling | {入口} 處理的檔名、內容、大小會不會讓人讀寫到別的檔或塞爆空間? | T、I、D | V5 | INPV、BUSL | — | file_upload、file_download、export | 否 | behavior、static_analysis、review | 既有單元與整合測試 runner、靜態分析、模糊測試 | 沒有靜態分析工具：static_analysis 換成 deployment |
| outbound | {入口} 會不會被拿來打內網或不該打的位址?第三方回應被信任到什麼程度? | T、I | V1（SSRF 在 v5.0.0-1.3.6）、V4、V15 | INPV | API7、API10 | outbound_call、webhook_in | 否 | behavior、review | 既有單元與整合測試 runner、靜態分析 | 無替代 |
| secrets-crypto | 這功能用到的秘密、金鑰、憑證放哪、誰讀得到、傳輸有沒有保護? | I | V11、V12、V13 | CRYP、CONF | — | `@repo`（每個 repo 根問一次） | 否 | secret_scan、review | 秘密掃描、設定與容器掃描 | 沒有秘密掃描工具：secret_scan 換成 deployment |
| supply-chain | 新加的依賴、映像、工具從哪來、版本怎麼釘、誰核可? | T | V15 | CONF | — | `@repo`（每個 repo 根問一次） | 否 | dependency_scan、review | 依賴漏洞掃描 | 沒有依賴掃描工具：dependency_scan 換成 deployment |
| config-deploy | 部署設定、容器、對外開的埠與預設帳號有沒有守住? | T、I、D | V13 | CONF | API8、API9 | `@repo`（每個 repo 根問一次） | 否 | config_scan、review | 設定與容器掃描 | 沒有設定與容器掃描工具：config_scan 換成 deployment |
| audit | 誰在什麼時候對 {資產} 做了什麼，事後查得到嗎?紀錄本身會不會被改? | R | V16 | — | — | admin、http_api | 否 | review | — | 無替代 |
| frontend-origin | 前端跨來源、cookie、CSRF 與畫面上的敏感資料誰負責? | S、T、I | V3 | CLNT | — | web_page | 否 | behavior、review | 既有單元與整合測試 runner、動態掃描 | 無替代 |

- 「最低證據種類」是下限：一條護欄寫了幾個類別，下限就是那幾類最低種類的聯集。這條檢查（`insufficient_required_evidence`）只有一個擁有者：姊妹計劃的閘門（它讀得到 `.lumos/security-tools.json`，才知道哪個工具類別沒工具、要不要照最後一欄換算）；盤點不判這一項。作者在護欄裡自述「沒有工具」不算數。每類都含 review，因為判準獨立與適用性機械做不到。
- 替代欄的 deployment 是姊妹計劃〈二〉證據種類表裡「沒有工具時的人工核對」那一種，格式 `review_record`；替換後最低種類是替代種類加上原本的其他種類，不是只剩 review。
- 以 repo 為單位問一次的三類（secrets-crypto、supply-chain、config-deploy）不逐入口展開，避免同一題重複幾十次；它們的格子用保留入口 `@repo` 表示（見〈一〉）；反過來，表裡「適用入口」寫「全部」是指 surfaces 裡所有 kind 的入口，不含 `@repo`。
- **純後端 repo 的跨來源問題由 authn-identity 問到**：前端放在別的 repo 時，這個 repo 的盤點只有 http_api 入口、沒有 web_page，frontend-origin 一格都不會長；但 session cookie 屬性、CORS、CSRF 都是後端在設定，所以 authn-identity 的模板對 http_api 另問這三件事。
- frontend-origin 跟既有前端面 `arch-fe-origin` 的關係：問的是同一件事（跨來源、cookie、CSRF 誰負責）。需求風險面那一層**沿用 arch-fe-origin、不另加一題**；frontend-origin 只在格子這一層存在（web_page 入口逐格問、追去向）。同一份計劃若已在 arch-fe-origin 答過，格子那一題的去向直接引用那個答案（寫成護欄或 considerations），不重複出題。
- ASVS 章節：SSRF 在 v5.0.0 是 V1〈Encoding and Sanitization〉的 1.3.6（出處：OWASP ASVS 官方 GitHub 標籤 `v5.0.0_release` 的 `5.0/en/0x10-V1-Encoding-and-Sanitization.md`，2026-10-19 查閱），所以 outbound 補掛 V1；其餘章節對應是本篇自建、未逐條核對 ASVS 原文。
- **版號跟著資料列走，不跟著格子走**：格子每次從 inventory 與當前的表現算，沒有地方存「格子建立時」的版號，所以不寫這種東西。改成：每一列 considerations 與每一條 controls 寫入時帶 `threat_table_version`（寫入當下表的版號）；有資料列的格子顯示那一列的版號，沒有資料列的 open 格子只顯示當前版號。表改版後，舊版號的資料列照舊算數，`security list` 另列「資料列版號比當前舊」的數量，提醒重審。
- **類別被改名或刪除**：considerations 引用了當前表沒有的類別 id，列格子層錯誤 `unknown_category`（見〈四〉的格子層錯誤），不靜默忽略，也不擋推送。controls 的 `threat_categories` 引用表裡沒有的 id 不歸格子層：依姊妹計劃屬護欄層錯誤 `threat_category_unknown`（整條護欄 unsound、例外蓋不掉），由姊妹計劃的閘門判，這裡不重複列。
- **單一來源**：實作時這張表搬到 [[Systems/資安威脅類別表]]，那裡是唯一的正本；本篇這張表改成一行指過去並刪掉，避免兩份。不擴大 [[Systems/情境出題]] 的負責範圍——那篇管對照實驗的量測與需求風險面表的內容源，威脅類別表的主要讀者是盤點與驗收閘，語意屬資安，另開一篇比把一篇擴成包四件事清楚。程式不讀圖譜（`pitfalls --stage` 不需要筆記庫，消費專案跑 `security list` 時也沒有工具鏈的圖譜），所以 `scripts/lumos` 放一份鏡像常數，另寫一支漂移測試讀 [[Systems/資安威脅類別表]] 那張表，逐列逐欄比對常數（欄位內容照全形頓號切開成集合比，標題上的版號也比），任一欄不同就紅；要改表先改圖譜正本、經使用者核可升版，再改常數。

## 三、依決策時機排進既有分階段提問

格子回答的是「這份產品要想哪些」，需求風險面回答的是「這份計劃現在這個階段該釐清哪些」。兩條路分工：
- **需求風險面表**（`pitfalls --stage`，比對計劃文字）：補下列七項，只決定「這個階段多列幾題」，仍是提醒，不擋。既有 25 項（含 `deliver-security`）的問題句、觸發詞與階段一字不改——這照母計劃 d7 標題下〈提問依決策時機安排〉一節「不改既有風險面表的觸發字、階段」。七項新列寫進 [[Systems/情境出題]]（需求風險面表的內容源）與它的「25 項」敘述。
