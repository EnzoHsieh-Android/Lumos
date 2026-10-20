---
type: project
status: todo
created: 2026-10-19
updated: 2026-10-19
tags:
  - type/project
  - status/todo
  - scope/loop-engineering
lands_in:
  - Systems/情境出題
  - Systems/pitfalls-code-loop
  - Systems/lumos-cli-read
related:
  - "[[Projects/消費專案產品安全Brief與證據驗收_計劃]]"
  - "[[Projects/安全主張驗收閘_計劃]]"
  - "[[Projects/資安護欄唯讀盤點_計劃]]"
  - "[[Projects/後端工程提問與證據擴充_計劃]]"
  - "[[Projects/待決問題改存開頭欄位_計劃]]"
  - "[[Projects/前端知識與風險詞_計劃]]"
pending_questions:
  - id: Q1
    text: inventory 要加 actors、surfaces 的 kind／actor_ids／trust_boundary、controls 的 threat_categories、considerations 與 coverage 的 cells,這是唯讀盤點的契約變更;要在哪份計劃過設計審?已依 d2 併進 Projects/安全主張驗收閘_計劃 那次設計審一起審,審過後同步更新盤點計劃的契約段
    class: 範圍
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d2"
  - id: Q2
    text: 威脅類別表 12 類、各類的最低證據種類與適用入口是第一版設計值,誰核可?之後誰負責改版?
    class: 權責
    stage: 需求
    status: 已決
    blocking: true
    decision: "#d1"
  - id: Q3
    text: P2 擴大訊號的門檻:加了格子與新風險面的臂,漏放要比 A 臂少多少、誤觸發率與每案回答時間上限多少,才把 open 格子改成擋或推廣到所有專案?要在看 P2 成績前定
    class: 風險接受
    stage: 驗證
    status: 待人
  - id: Q4
    text: deliver-security 要不要改成只問未驗與例外、原本「誰能做」移到需求階段(會讓現在會列它的計劃改列新項)?還是保留原句、另加一項?本篇目前照母計劃 d7 小節採「保留原句、另加 deliver-sec-exceptions」,答改寫的話照〈三〉寫的翻法改
    class: 範圍
    stage: 需求
    status: 待人
  - id: Q5
    text: 40 篇人工標註(該不該問資安)由誰標?建議使用者標 20 篇、獨立審查標 20 篇並互相抽 5 篇對照
    class: 權責
    stage: 驗證
    status: 待人
decisions:
  - content: 威脅類別對照表(類別、各類最低證據種類、適用入口)由使用者核可,AI 只能提案;表放在工具鏈圖譜當單一來源,每次改版走設計審後由使用者核可並升版號,對照 ASVS/WSTG 等要附來源
    id: d1
    context: 待決 Q2:12 類威脅表誰核可、誰改版
    why_chosen: 使用者 2026-10-19 選「你核可,AI 只能提案」
    decided: 2026-10-19
    valid: true
  - content: 盤點契約變更(inventory 的 actors、surfaces 的 kind/actor_ids/trust_boundary、controls 的 threat_categories、considerations 等)併進 Projects/安全主張驗收閘_計劃 那次設計審一起審,不分開跑;審過後同步更新 Projects/資安護欄唯讀盤點_計劃 的契約段並標明凍結版本差異
    id: d2
    context: 待決 Q1:盤點契約變更要在哪份計劃過審
    why_chosen: 編排者 2026-10-19 依流程安排決定:兩份新計劃都改同一份盤點 schema v2,分開審會讓同一契約有兩份審查結論;這是流程歸屬不是產品規則
    decided: 2026-10-19
    valid: true
  - content: 實作期間 order-demo 當資安功能的實驗專案:新指令、轉接器、閘門判定、階段提問先在 order-demo 真跑驗證;條件沿用母計劃 d8(隔離副本、本機合成資料、只打本機回環、單次 10 分鐘、整批 1 小時、不呼叫額外付費模型);實驗產生的產品證據留在 order-demo 自己的圖譜,不複製成工具鏈證據;實驗結果不代表真實認證安全;新工具仍照逐項核可
    id: d3
    context: 設計需要一個真實消費專案驗證閘門與提問;order-demo 已有 P1 證據與 k6 核可
    why_chosen: 使用者 2026-10-19 指示「order-demo可以在資安功能實作中，作為實驗專案」
    decided: 2026-10-19
    valid: true
---
# 資安風險提問分階段_計劃

## 接手先讀：這份計劃管什麼

白話：資安問題漏掉，多半不是不會答，而是當時沒想到要問。這份計劃讓問題從「要保護什麼、誰會碰、從哪裡進來」的清單長出來，像查帳時逐格對表，而不是靠當下想起什麼問什麼；每個問到的問題最後都要有去向，沒去向的會變成看得到的缺口。

- 只管「想到哪些問題、什麼時候問、答案去哪」，不管證據合不合格；證據判定與推送閘在姊妹計劃 [[Projects/安全主張驗收閘_計劃]]。兩篇共用同一套資產、入口、證據種類與工具類別詞彙：證據種類的值域與定義、工具類別的叫法以姊妹計劃〈二〉的證據種類表與〈三〉的工具類別表為準，本篇照抄名稱不另取；本篇的〈威脅類別表〉是「威脅類別 → 最低證據種類 → 工具類別」對照的單一來源，姊妹計劃只引用。
- 要求來源：母計劃 [[Projects/消費專案產品安全Brief與證據驗收_計劃]] 的〈提問依決策時機安排，不等交付才確認權限〉（需求、架構、驗證、交付各階段都要有）、〈消費專案資安護欄盤點指令〉的安全覆蓋盤點（G8）、P2 五案三臂方法試行。
- 沿用：需求風險面表 `_REQUIREMENT_FACETS` 與 `pitfalls --stage`（[[Projects/後端工程提問與證據擴充_計劃]] d12、d13）、開頭欄位 `pending_questions` 與它的阻塞規則（[[Projects/待決問題改存開頭欄位_計劃]]）、唯讀盤點的 inventory 與 coverage（[[Projects/資安護欄唯讀盤點_計劃]]）。
- 威脅類別表是「類別對照」，不是題庫：它只決定一格該套哪類問題的模板；產生出來的題一律進消費專案計劃既有的 `pending_questions`，不另開提問帳、不另存一份題目清單。這跟母計劃 d7「不新增平行題庫」不衝突：d7 擋的是另建一套跟情境出題並行的題目與流程，本篇的類別表接在既有需求風險面與 `pending_questions` 後面，題目的家仍是那兩處。
- 這份只寫設計，不改程式。實作前過本篇規格閘與設計審；其中盤點契約變更（〈一〉〈三〉的 schema v2）依 d2 併進 [[Projects/安全主張驗收閘_計劃]] 那次設計審一起審，不另跑。
- 本篇的決策寫 d1–d3；母計劃的決策一律寫「母計劃 dN」，兩邊編號不通用。

## 現況（2026-10-19 讀程式）

- 需求風險面表共 25 項（15 項一般加 10 項前端），專門問資安的只有交付階段的 `deliver-security` 一項：「誰能做這件事?有哪些敏感資料?邊界在哪?」；另有前端面的 `arch-fe-origin`（架構階段，只在計劃提到前端字樣時列，問 CORS、cookie、CSRF 誰設定）。等到交付才問誰能做什麼，權限設計早就定了，跟母計劃 d7 標題下〈提問依決策時機安排，不等交付才確認權限〉一節的時機安排不合。
- 它的觸發詞是「會員、使用者、帳號、權限、個資、付款、登入、管理員」任一。2026-10-19 在提交 301b0916 上重算：`docs/lumos-toolchain-knowledge/Projects/` 358 篇筆記有 222 篇命中，其中檔名帶 `_計劃` 的 298 篇有 188 篇命中（口徑：用 `scripts/lumos` 裡 deliver-security 的那條正規式對全文 `re.search`，本篇自己也算在內；重跑指令見下）。「使用者」幾乎每篇都有，等於永遠觸發；人看久了就不看了。
  - 重跑：`python3.14 -c "import re,glob;fs=glob.glob('docs/lumos-toolchain-knowledge/Projects/*_計劃.md');print(len(fs),sum(1 for f in fs if re.search(r'會員|使用者|帳號|權限|個資|付款|登入|管理員',open(f,encoding='utf-8-sig').read())))"`
- 盤點的 inventory 只有 assets 與 surfaces（surfaces 有描述與對應資產），沒有角色、入口種類與信任邊界的結構欄位；coverage 只算入口有沒有對到護欄，不算「這個入口的這類威脅想過沒」。

## 一、從「要保護什麼」出發

問題由盤點長出來，不靠臨場回想：
- 沿用盤點 `lumos-security-v1` 的 inventory（已核可的資產與入口清單）當起點；母計劃 G8 本來就要求有版本、有核可的入口盤點。
- inventory 要多三樣才長得出問題（schema v2，契約變更；依 d2 併進姊妹計劃那次設計審，審過後同步更新盤點計劃的契約段）：
  - `actors`：角色清單（例：擁有者、同站他人、未登入者、管理員、外部系統），每項有 id 與描述。
  - surfaces 每項加 `kind`（固定值域：http_api、web_page、export、file_upload、file_download、webhook_in、outbound_call、batch、message_consumer、admin、cli）、`actor_ids`（誰會從這裡進來）、`trust_boundary`（跨了哪道信任邊界，文字）。
  - 用來寫「想過、不適用」與「想過、接受風險」的 `considerations` 清單（見〈四〉）。
  - 保留入口 id `@repo`：代表「整個部署單位」，給以 repo 為單位問一次的三類（secrets-crypto、supply-chain、config-deploy）當格子的入口；它不寫在 surfaces 裡、作者不能自己宣告同名入口（surfaces 出現 `@` 開頭的 id 列錯誤），它的資產固定是 `@repo`（整個 repo 的秘密、依賴、部署設定）。本篇的**部署單位就是一個 repo 根**：一個 repo 根一組 `@repo` 格子，同一 repo 裡有幾個服務也不拆。
  - controls 的 `required_evidence` 值域擴成姊妹計劃〈二〉證據種類表的全部種類（現行盤點只認 behavior、fault_sensitivity、review、deployment、dependency_scan；新增 concurrency、static_analysis、secret_scan、dynamic_scan、fuzz、config_scan），定義以那張表為準；照盤點規矩升 `schema_version`，不用未知字串冒充。
- 理由：問題要逐格產生，格子的兩個軸（入口、資產）與角色必須是結構資料；寫在散文裡工具算不出缺口。
- 不選：另開一份威脅模型檔或引入 pytm 的 Python 模型（零依賴家規下不採；pytm 的威脅庫還會 eval 字串）；從程式碼自動推入口（推得出路由，推不出哪個資產敏感、誰不該碰）。
- 入口盤點本身漏項，工具發現不了；這點承接盤點計劃 Q1（誰審入口盤點、多久重驗），不在本篇另問。

## 二、每格套固定威脅類別

格子＝入口 × 該入口對應的資產 × 適用的威脅類別。「該入口對應的資產」就是那個入口自己的 `asset_ids`，不是全部資產；以 repo 為單位的三類，格子是 `@repo × @repo × 類別`，每個 repo 根各一格。適用與否由入口 kind 決定（表的「適用入口」欄），不由作者臨場挑。每格產生一個候選問題，問題句由表的模板加上入口、資產、角色名稱組成。

分類只借，不宣稱合規：類別骨架用 STRIDE 逐元素的想法（入口對資料流與處理、資產對資料儲存、角色對外部互動者），每類掛 ASVS 5.0.0 章節當驗收錨點、WSTG v4.2 類別當測法提示、OWASP API Security Top 10 2023 當 API 入口的細分提示。ASVS 章節對 STRIDE 沒有 OWASP 官方對照，下表的對應是本篇自建。

### 威脅類別表 v1（單一來源；姊妹計劃引用「最低證據種類」與「工具類別」兩欄）

版號寫在這個標題上（現在是 v1）。依 d1，每次改版走設計審、由使用者核可，核可那次就升一號（v1→v2），核可決策記成本篇（之後是表的家那篇）的一條 decisions；盤點算出的每一格帶著建立時的表版號。

| id | 要問什麼（模板） | STRIDE | ASVS 5.0.0 | WSTG v4.2 | API Top10 2023 | 適用入口 | 最低證據種類 | 能產生證據的工具類別 | 沒有工具時 |
|---|---|---|---|---|---|---|---|---|---|
| authz-object | {角色} 從 {入口} 能不能讀、改、刪不屬於他的 {資產}?被拒時資料與副作用怎樣? | E、I | V8 | ATHZ | API1、API3、API5 | http_api、web_page、export、file_download、admin | behavior、fault_sensitivity、review | 既有單元與整合測試 runner、破壞測試與故障收證；動態掃描補充 | 可執行反例（他人身分的請求＋合法對照） |
| authn-identity | {入口} 的身分從哪來、何時可信?偽造、過期、撤權後會怎樣? | S | V6、V7、V9、V10 | IDNT、ATHN、SESS | API2 | http_api、web_page、admin、webhook_in | behavior、review | 既有單元與整合測試 runner、動態掃描（含登入證據） | 人工審（不做登入的示範專案寫明「身分可信」是未驗前提） |
| input-injection | {入口} 收到的輸入會不會被當成指令、查詢或路徑執行? | T | V1、V2 | INPV | — | 全部 | behavior、static_analysis、review | 既有單元與整合測試 runner、靜態分析、模糊測試、動態掃描 | 可執行反例（惡意輸入樣本） |
| flow-abuse | 重送、並發、大量或跳步驟時，{資產} 會不會被他人操作生效、超賣或耗盡? | T、D | V2 | BUSL | API4、API6 | http_api、web_page、webhook_in、message_consumer | behavior、concurrency、review | 既有單元與整合測試 runner（並發測試）、壓測與並發 | 可執行反例（固定次數的並發測試） |
| data-exposure | 錯誤訊息、日誌、回應欄位會不會帶出 {資產} 或它存不存在? | I | V14、V16 | ERRH、INFO | API3 | 全部 | behavior、review | 既有單元與整合測試 runner、動態掃描 | 可執行反例（對照存在與不存在資源的回應） |
| file-handling | {入口} 處理的檔名、內容、大小會不會讓人讀寫到別的檔或塞爆空間? | T、I、D | V5 | INPV、BUSL | — | file_upload、file_download、export | behavior、static_analysis、review | 既有單元與整合測試 runner、靜態分析、模糊測試 | 可執行反例 |
| outbound | {入口} 會不會被拿來打內網或不該打的位址?第三方回應被信任到什麼程度? | T、I | V1（SSRF 在 v5.0.0-1.3.6）、V4、V15 | INPV | API7、API10 | outbound_call、webhook_in | behavior、review | 既有單元與整合測試 runner、靜態分析 | 可執行反例（指向內網位址的請求） |
| secrets-crypto | 這功能用到的秘密、金鑰、憑證放哪、誰讀得到、傳輸有沒有保護? | I | V11、V12、V13 | CRYP、CONF | — | `@repo`（每個 repo 根問一次） | secret_scan、review | 秘密掃描、設定與容器掃描 | 人工審 |
| supply-chain | 新加的依賴、映像、工具從哪來、版本怎麼釘、誰核可? | T | V15 | CONF | — | `@repo`（每個 repo 根問一次） | dependency_scan、review | 依賴漏洞掃描 | 人工審 |
| config-deploy | 部署設定、容器、對外開的埠與預設帳號有沒有守住? | T、I、D | V13 | CONF | API8、API9 | `@repo`（每個 repo 根問一次） | config_scan、review；沒有設定與容器掃描工具時 config_scan 改成 deployment | 設定與容器掃描 | 人工審 |
| audit | 誰在什麼時候對 {資產} 做了什麼，事後查得到嗎?紀錄本身會不會被改? | R | V16 | — | — | admin、http_api | review | — | 人工審 |
| frontend-origin | 前端跨來源、cookie、CSRF 與畫面上的敏感資料誰負責? | S、T、I | V3 | CLNT | — | web_page | behavior、review | 既有單元與整合測試 runner、動態掃描 | 可執行反例 |

- 「最低證據種類」是下限：每條登記成護欄的答案，`required_evidence` 不能比它所屬類別的這一欄少（姊妹計劃 S14 擋）。每類都含 review，因為判準獨立與適用性機械做不到。
- 以 repo 為單位問一次的三類（secrets-crypto、supply-chain、config-deploy）不逐入口展開，避免同一題重複幾十次；它們的格子用保留入口 `@repo` 表示（見〈一〉）；反過來，表裡「適用入口」寫「全部」是指 surfaces 裡所有 kind 的入口，不含 `@repo`。
- config-deploy 的「沒有設定與容器掃描工具時改成 deployment」：deployment 是姊妹計劃〈二〉證據種類表裡「實際部署設定符合（沒有工具時）、人工核對」那一種；替換後最低證據種類是 deployment、review，不是只剩 review。
- frontend-origin 跟既有前端面 `arch-fe-origin` 的關係：問的是同一件事（跨來源、cookie、CSRF 誰負責）。需求風險面那一層**沿用 arch-fe-origin、不另加一題**；frontend-origin 只在格子這一層存在（web_page 入口逐格問、追去向）。同一份計劃若已在 arch-fe-origin 答過，格子那一題的去向直接引用那個答案（寫成護欄或 considerations），不重複出題。
- ASVS 章節：SSRF 在 v5.0.0 是 V1〈Encoding and Sanitization〉的 1.3.6（出處：OWASP ASVS 官方 GitHub 標籤 `v5.0.0_release` 的 `5.0/en/0x10-V1-Encoding-and-Sanitization.md`，2026-10-19 查閱），所以 outbound 補掛 V1；其餘章節對應是本篇自建、未逐條核對 ASVS 原文。
- 表的內容是第一版設計值；要改類別、模板或最低種類，照 d1 改這張表並升版號，舊格子的狀態照舊保留。
- **單一來源照 d1 放在工具鏈圖譜**：實作時這張表搬到 [[Systems/情境出題]] 這篇圖譜筆記（需求風險面表的內容源也在那裡），那裡是唯一的正本；本篇這張表改成一行指過去並刪掉，避免兩份。程式不讀圖譜（`pitfalls --stage` 不需要筆記庫，消費專案跑 `security list` 時也沒有工具鏈的圖譜），所以 `scripts/lumos` 放一份鏡像常數，另寫一支漂移測試讀 Systems/情境出題 那張表逐欄比對常數，任一欄不同就紅；要改表先改圖譜正本、經使用者核可升版，再改常數。
- 本篇 `lands_in` 的 [[Systems/情境出題]]：那篇現在的 responsibility 只涵蓋需求風險面表的內容源；實作落地時要把它擴成「也管威脅類別表的正本與版號、程式鏡像的漂移測試」。擴的是那篇的 responsibility，本篇設計階段不改那篇。

## 三、依決策時機排進既有分階段提問

格子回答的是「這份產品要想哪些」，需求風險面回答的是「這份計劃現在這個階段該釐清哪些」。兩條路分工：
- **需求風險面表**（`pitfalls --stage`，比對計劃文字）：補下列七項，只決定「這個階段多列幾題」，仍是提醒，不擋。既有 25 項（含 `deliver-security`）的問題句、觸發詞與階段一字不改——這照母計劃 d7 標題下〈提問依決策時機安排〉一節「不改既有風險面表的觸發字、階段」。

| 新 id | 階段 | 要釐清什麼 | 觸發（草案；強詞表見下） |
|---|---|---|---|
| req-sec-assets | 需求 | 這功能碰到哪些要保護的資料與操作?誰可以做、誰不可以做(角色 × 資源 × 動作)?最不能發生的事是什麼(寫成看得到的結果)? | 通用強詞至少兩個不同的 |
| req-sec-actors | 需求 | 誰可能濫用這功能(他人、未登入者、內部人、外部系統)?他能做到什麼程度? | 同上 |
| arch-sec-boundary | 架構 | 身分從哪來、何時可信?授權在哪個服務端邊界強制?外部輸入在哪一層驗? | 同上；或通用強詞至少一個，再加邊界詞（API、入口、webhook、回呼、匯入、第三方、管理後台）至少一個 |
| arch-sec-secrets | 架構 | 會用到哪些秘密、金鑰、憑證?放哪、誰讀得到、外洩了怎麼換? | 秘密詞至少兩個不同的 |
| arch-sec-supply | 架構 | 要新加的依賴、映像或掃描工具從哪來、版本怎麼釘、誰核可? | 供應鏈詞至少兩個不同的 |
| verify-sec-evidence | 驗證 | 每條資安護欄要哪幾種證據?用哪個工具(查威脅類別表)?沒有工具時是人工審還是可執行反例?合法對照是什麼? | 通用強詞至少兩個不同的 |
| deliver-sec-exceptions | 交付 | 還有哪些資安護欄沒驗或走例外?例外誰核可、哪天到期? | 同上 |

- **`deliver-security` 不改**：原句「誰能做這件事?有哪些敏感資料?邊界在哪?」、觸發詞與交付階段照舊；「未驗與例外」另加 `deliver-sec-exceptions` 一項問。原本打算把它改寫、把「誰能做」移到需求階段，那會改既有風險面的問題句，跟母計劃 d7 小節衝突，而且 Q4 還待人。Q4 若改答「改寫」：把 deliver-security 的問題句換成 deliver-sec-exceptions 那句、刪掉 deliver-sec-exceptions、S9 改回「只問未驗與例外」，其餘不動；這樣翻只動兩列與一條條款。
- **誤觸發怎麼壓**：
  - 三張詞表都只收少歧義的詞；英文詞照 `scripts/lumos` 前端字樣那條正規式（`_REQ_FE_WHEN`）的詞界寫法：整條不分大小寫、前後不接英數字（`(?<![a-z0-9])詞(?![a-z0-9])`），所以 `pip` 不會撞到 pipeline。「使用者」「會員」不算強詞。
  - 通用強詞：登入、權限、個資、租戶、他人的、別人的、擁有者、所有權、越權、上傳、下載、匯出、密碼、金鑰、憑證，以及英文 secret、api key、oauth、jwt、session、cookie、csrf、cors、token。
  - 秘密詞：金鑰、私鑰、憑證、密碼、加密、secret、api key、token、keystore、kms。
  - 供應鏈詞：新依賴、新增依賴、映像、鎖檔、供應鏈，以及英文 docker、npm、gradle、maven、pypi、lockfile、sbom、`pip install`（兩個字之間可有空白）。原草案的「安裝」「套件」「pip」拿掉：前兩個是太常見的單詞，pip 沒詞界會撞 pipeline。
  - 所有新項都要求至少兩個**不同的**詞才觸發（「不同」是指詞表裡不同的兩列，同一個詞出現多次只算一個）；arch-sec-boundary 另有「一個強詞加一個邊界詞」這條替代規則。
  - 新詞表的觸發篇數與誤觸發率還沒量（詞表已改過，舊草案的估計不沿用）；上線前用跟〈現況〉同一種可重跑的指令量篇數，再照〈五〉的人工標註量誤報與漏報。
  - 被觸發但不適用的，作者照既有規矩一句話寫不適用就結束，不必建問題。
- **觸發規則的新資料形狀（引擎改動，新增）**：現在每一項只有 `when`（正規式字串清單），`_pitfalls_stage` 用「任一條命中就觸發」判。新增一個選填鍵 `triggers`，七個新項只用它、不寫 `when`；既有 25 項照舊只用 `when`，行為不變。
  - 形狀：`"triggers": [{"words": [正規式字串, …], "min_distinct": 2}, {"words": […], "min_distinct": 1, "plus_any": [正規式字串, …]}]`。一條規則成立＝`words` 裡至少 `min_distinct` 個不同的元素對全文 `re.search` 命中，且有 `plus_any` 時其中至少一個也命中；`triggers` 裡任一條規則成立，這一項就觸發。
  - 一項只能有 `when` 或 `triggers` 其中一個（兩個都有或都沒有，表的自我檢查測試紅）。判斷收成一支函式，`--stage` 與其他讀風險面表的地方都呼叫它，不在各處各寫。
  - `--stage --json` 現在會把整列原樣序列化；`triggers` 裡只有字串與整數，照樣原樣輸出，所以新項的 JSON 多一個 `triggers` 鍵、沒有 `when` 鍵，既有 25 項的 JSON 逐字不變。
- **問題怎麼進待決問題**：該人裁的照既有 `question-add` 寫進消費專案計劃的 `pending_questions`，標階段；會影響實作的權限題標需求階段與阻塞，規格閘照既有規則擋。題目文字開頭寫格子身份（例：`格 orders-pay/authz-object:`），讓人讀得出是哪一格；格子狀態不靠這段字算（見〈四〉）。
  - 不選：在 `pending_questions` 加「格子」欄（改既有開頭欄位契約，而且題目結了不代表格子有去向，兩者會漂移）。
- **格子怎麼看**：盤點 coverage 加一區 `cells`（入口 × 資產 × 類別，各帶狀態與表版號），由 `security list` 列出；這是唯讀盤點的契約變更，跟〈一〉的 schema v2 一起依 d2 併進姊妹計劃那次設計審。
- **跟筆記庫有關的檢查放在讀得到筆記庫的指令**：`pitfalls --stage` 只讀那份計劃的文字、不讀筆記庫（`_pitfalls_stage` 只收計劃檔路徑、自己讀那一個檔，連待決問題也是從那份檔的開頭欄位解析），解析不了計劃連到哪篇 Systems、那篇登記了哪些護欄、哪些格子是 open。所以：
  - 「這份計劃連到登記了資安護欄的 Systems」與「這些 Systems 的 open 格子」由 `security list`（盤點，本來就讀筆記庫）與 `spec-gate`（規格閘，本來就讀筆記庫）列出。spec-gate 這一行是新增的提醒：計劃 `lands_in` 或 `related` 連到的 Systems 有資安登記時，印出那些護欄與 open 格子數，不擋。
  - `pitfalls --stage 驗證` 與 `--stage 交付` 在 verify-sec-evidence 或 deliver-sec-exceptions 觸發時，只多印一行指路：「這份計劃連到的資安護欄與 open 格子，跑 `lumos security list` 或 `lumos spec-gate <計劃>` 看」。

## 四、每個答案只有三條去向，機械追得到

一格的狀態只由盤點資料算出，不靠作者勾選：

| 去向 | 寫在哪 | 格子狀態 |
|---|---|---|
| 登記成護欄，交給驗收閘 | controls 條目同時滿足三件事：`surfaces` 含該入口、`assets` 含該資產、而且該資產在**那個入口自己的** `asset_ids` 裡；再加 `threat_categories` 含該類別（controls 加這個欄位，schema v2） | `control:<id>`；之後證據合不合格由驗收閘判 |
| 不適用 | inventory 的 `considerations`：入口、資產、類別、`outcome: not_applicable`、理由、核可決策 | `not_applicable`；盤點另列一區「待審適用性的格子」（新增輸出，見下） |
| 接受風險 | `considerations` 的 `outcome: risk_accepted`：入口、資產、類別、理由、補償措施、核可決策、到期日；走母計劃 d9 的例外規則：只有使用者核可、最長 30 天 | `risk_accepted`；過期或不合格就變回 `open` |
| 想過但沒下文 | 什麼都沒寫 | `open`：盤點輸出的缺口，不能當安全 |

- **護欄覆蓋格子不吃交叉積**：一條護欄寫了兩個入口、兩個資產，只覆蓋「入口 × 它自己 `asset_ids` 裡有的資產」那幾格，不是 2×2 全蓋。要更細就拆成兩條護欄。以 repo 為單位的三類：護欄的 `surfaces` 與 `assets` 寫 `@repo`。
- **護欄層 not_applicable 跟格子層 not_applicable 是兩件事**：護欄自己的 `reported_status: not_applicable`（v1 既有）是「這條護欄宣稱自己不適用」，照現在的行為進 `applicability_pending_control_ids`；它覆蓋到的格子狀態仍是 `control:<id>`，不會變成格子的 not_applicable。格子層的 not_applicable 只來自 considerations。
- **去向之間互斥**（S3 怎麼判）：同一格只要同時有「覆蓋它的護欄（不論那條護欄的 reported_status）」與「considerations 裡 outcome 是 not_applicable 或 risk_accepted 的一列」，就列錯誤、退出 2，不任選一個；同一格有兩列 considerations 也算錯。
- **待審適用性的格子是新行為**：現在的 `applicability_pending_control_ids` 只來自護欄自己的 `reported_status`（`scripts/lumos` 的 `_secinv_surface`），沒有 considerations。v2 新增一區 `applicability_pending_cells`，列出所有格子層 not_applicable 的格子；盤點只列、不裁核可足不足。
- **risk_accepted 的期限**：30 天從核可決策（`核可決策` 指到的那條 decisions）的 `decided` 日起算；`到期日` 晚於 decided 日加 30 天，或核可決策找不到、已作廢、缺補償措施或理由，這一列不算數、格子是 open。到期日當天仍算有效，隔天自動變回 open，跟盤點現在處理護欄例外的時點一樣（今天晚於到期日才算過期）。
- 「想過沒下文」不靠追問題：只要格子在、三種去向都沒有，就一直是 `open`。題目結成已決但沒有寫成護欄或 considerations，格子照樣 open。
- `risk_accepted` 的「只有使用者能核可」跟驗收閘的例外用同一套核准來源（姊妹計劃 d6：寫進這一列的提交要由使用者釘住的簽章金鑰簽），不另做一套。
- open 格子現在**不擋推送**：母計劃 d9 擋的是「已登記護欄的證據不合格」；open 只在 `security list` 列出、spec-gate 提醒（見〈三〉）。要不要擋，等〈五〉的量測。

## 五、這套提問有沒有用，由母計劃 P2 驗

- 量測沿用母計劃 P2 五類已知漏洞 × 三臂（A 既有流程、B 加 Brief、C 加 Brief 與可執行反例）；本篇的格子與新風險面屬於 B、C 臂的處置，要明記在 P2 的處置說明裡，不另開試驗。
- 量三件事：
  - **漏放**：每案事先寫好「該被問到的格子與人裁決定」清單，數各臂沒問到的；已知漏洞沒對應到任何格子，記成類別表的漏項。
  - **誤觸發**：在本 repo 與 order-demo 的計劃上，人工標 40 篇「該不該問資安」，算新觸發詞的誤報與漏報；P2 場內另數「被觸發但答不適用」的題數。
  - **成本**：每案的題數、人回答所花的時間（自報分鐘）、token 與費用。
- 推廣線：
  - 新增的風險面先以提醒上線（本來就只是提醒）。
  - open 格子在拿到 P2 擴大訊號、使用者確認前，不改成擋，也不推廣成所有專案預設擋。
  - 擴大訊號的門檻（漏放要減少多少、誤觸發與成本上限）在看 P2 成績前由使用者定（Q3，待人）。

REVISIT:2026-12-31 核對 40 篇人工標註與 P2 的量測是否完成;沒完成就維持只提醒,並把卡在哪一步寫回本節

## 驗收條款

以下實作前逐條改綁真測試；可機械化的不准長期停在 manual。

- [S1] 當 inventory 有 actors、帶 kind 的 surfaces 與資產時,`security list` 的 coverage 應逐格列出入口 × 資產 × 適用類別,適用與否只由入口 kind 決定。 [manual:合成 vault 三個不同 kind 的入口核對格子清單]
- [S2] 當某格沒有護欄也沒有 considerations 時,該格應列為 open,而且題目在 pending_questions 結成已決也不改變這個狀態。 [manual:同一格有無已決題目各一份樣本]
- [S3] 當同一格同時有覆蓋它的護欄(不論 reported_status)與 outcome 為 not_applicable 或 risk_accepted 的 considerations 時,盤點應列錯誤並退出 2,不得任選一個去向;護欄自己的 reported_status 為 not_applicable 時,它覆蓋的格子應仍是 control 狀態。 [manual:衝突樣本與護欄層 not_applicable 樣本各一]
- [S4] 當 risk_accepted 的到期日已過、晚於核可決策 decided 日加 30 天、缺補償措施或核可決策找不到或已作廢時,該格應回到 open。 [manual:到期前、當天、隔天、超過 30 天、缺補償措施、決策作廢六份樣本]
- [S5] 當護欄的 required_evidence 少於它威脅類別的最低證據種類時,盤點應列 insufficient_required_evidence 問題。 [manual:authz-object 只宣告 behavior 的樣本]
- [S6] 當計劃只出現「使用者」「會員」而沒有兩個不同強詞時,新的需求與架構資安面應不觸發;只出現 pipeline、安裝、套件或同一個秘密詞重複多次時,arch-sec-supply 與 arch-sec-secrets 應不觸發。 [manual:固定十篇不談資安的計劃文字加三份撞詞樣本]
- [S7] 當計劃同時出現兩個不同強詞時,`pitfalls --stage 需求` 應列出 req-sec-assets 與 req-sec-actors,架構階段應列出 arch-sec-boundary。 [manual:固定十篇談權限的計劃文字]
- [S8] 當不帶 `--stage` 執行 pitfalls 時,輸出應跟改動前逐字相同。 [manual:既有 pitfalls 測試樣本前後比對]
- [S9] 當計劃有兩個不同強詞而跑 `pitfalls --stage 交付` 時,deliver-security 應照原句列出,另應列出問未驗與例外的 deliver-sec-exceptions。 [manual:讀 --stage 交付 的 JSON 核對兩項的 id 與問題句]
- [S10] 當威脅類別表改版時,舊格子的 considerations 與狀態應保留,新類別的格子應列為 open,每格應帶建立時的表版號。 [manual:新增一個類別前後各跑一次盤點比對]
- [S11] 當風險面用 triggers 時,`pitfalls --stage --json` 應原樣輸出 triggers 鍵,既有 25 項的 JSON 應跟改動前逐字相同;同一項同時有 when 與 triggers 時,表的自我檢查應紅。 [manual:改動前後各存一份四個階段的 JSON 比對，另做一份兩鍵並存的壞表]
- [S12] 當 Systems/情境出題 的威脅類別表與 scripts/lumos 的鏡像常數有任一欄不同時,漂移測試應紅。 [manual:改正本一格、改常數一格各跑一次]
- [S13] 當 verify-sec-evidence 或 deliver-sec-exceptions 觸發時,`pitfalls --stage` 應只多印一行指向 security list 與 spec-gate 的指路且不讀筆記庫;spec-gate 對連到有資安登記 Systems 的計劃應印出護欄與 open 格子數而不擋。 [manual:無筆記庫的暫存目錄跑 --stage，加一個合成 vault 跑 spec-gate]
- [S14] 當一條護欄寫了兩個入口與兩個資產、而每個入口的 asset_ids 只含其中一個資產時,該護欄應只覆蓋入口自己資產的那兩格,不覆蓋交叉的兩格。 [manual:兩入口兩資產的合成 inventory 核對四格狀態]

## 世界解與採用判斷

PRIOR-ART: 最小解是在既有需求風險面表加七項、既有項不改，並在唯讀盤點的 inventory 與 coverage 加角色、入口種類、格子與 considerations；分類借 OWASP 與 STRIDE，不引入威脅建模工具。以下 2026-10-19 查閱：
- [OWASP ASVS](https://github.com/OWASP/ASVS)：最新穩定版 5.0.0（2025-05-30，標籤 `v5.0.0_release`），17 章 V1–V17；SSRF 是 V1.3.6（[原文](https://github.com/OWASP/ASVS/blob/v5.0.0_release/5.0/en/0x10-V1-Encoding-and-Sanitization.md)，2026-10-19 核對）；引用一律帶版本前綴（例 `v5.0.0-8.2.1`），不帶版本的編號會隨改版歧義。
- [OWASP WSTG](https://github.com/OWASP/wstg)：穩定版 v4.2，v5.0 開發中；引用格式 `WSTG-v42-ATHZ-02`，開發版已把輸入驗證改名 Injection（INJT），所以鎖在 v4.2。
- [OWASP API Security Top 10 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10)：API1–API10。
- STRIDE：定義取 [Microsoft Threat Modeling Tool 文件](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)；逐元素對照（資料流與資料儲存 T、I、D，處理六類，外部互動者 S、R）取 Hernan、Lambert、Ostwald、Shostack 2006-11 MSDN Magazine〈Threat Modeling: Uncover Security Design Flaws Using the STRIDE Approach〉。
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)：把六類當提示套到元件、資料流、信任邊界；沒有元素對類別的表。
- [OWASP pytm](https://github.com/OWASP/pytm)：威脅庫每筆有 target 與 condition，逐元素產生發現，結構最接近本篇的格子；不採用它本身（Python 依賴、威脅庫字串會 eval）。
- [Threat Dragon](https://www.threatdragon.com/docs/usage/threats.html)：依元素類型與依元素屬性兩種提示。
- ASVS 章節對 STRIDE 沒有 OWASP 官方對照，本篇表格的對應是自建。

RETIRE-IF: P2 量測顯示加了格子與新風險面的臂，漏放沒有比 A 臂少、或誤觸發與回答成本超過使用者事先定的上限時，撤掉新風險面與格子展開，回到現行一項 deliver-security；inventory 的角色與入口種類若有別的用途可保留。若上線 8 週內所有消費專案合計新增的 considerations 與護欄少於 3 筆，也撤回重想。

## 實務隱患

已排除:金流:只讀計劃文字與筆記、不呼叫任何業務 API。
已排除:對外送出:不連網、不呼叫模型；P2 量測的模型呼叫與費用歸母計劃 P2 另核可。
已排除:不可逆:只改提問與盤點的唯讀輸出;回退撤掉新增項即可,消費專案寫下的 considerations 留著不刪。
守衛面:新風險面只是提醒,不改規格閘的擋法(只多一行提醒)與推送閘;既有 25 項(含 deliver-security)不改,新項的觸發由 S6、S7、S9、S11 守住,並在上線說明列出。open 格子不擋推送,直到使用者依 P2 結果另裁。
資源:格子數是入口 × 資產 × 類別，大型專案可能上千格；以 repo 為單位問的三類不逐入口展開，實作時對 200 個入口、50 個資產的合成 inventory 量一次時間與輸出大小再定上限。

## 回退

撤掉七個新風險面、`triggers` 判法與 spec-gate 那行提醒，即回到現行 25 項；盤點的 cells 與 considerations 若被盤點計劃的設計審否決，先修規格，不對消費專案自動轉寫；已寫進消費專案的 considerations 與 pending_questions 不刪。
