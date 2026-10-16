---
type: project
status: todo
created: 2026-10-15
updated: 2026-10-15
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
  - risk/守衛面
lands_in:
  - Systems/情境出題
  - Systems/pitfalls-code-loop
  - Systems/效能檢核目錄
  - Systems/棧別提問表態閘
  - Systems/規格閘
  - Systems/design-loop
  - Systems/每輪修補差異派工
  - Systems/test-quality-cli
related:
  - "[[Projects/前端框架從vue分出_計劃]]"
  - "[[Projects/雙向門放行_計劃]]"
  - "[[Issues/門掃描詞表沒收常見寫法]]"
  - "[[Projects/代碼審前後端角色鏡頭_計劃]]"
  - "[[Projects/後端工程提問與證據擴充_計劃]]"
decisions:
  - content: 風險詞表加兩個例外:「送出」接在請求、表單、第二個(第二次)這類前端語境時不算對外送出(後面緊接寫出去處——給、到、至、往——照算);全大寫識別字裡緊貼底線的 PAYMENT(例 ORDER_PAYMENT_TIMEOUT)不算金流。推翻 Projects/雙向門放行_計劃 取捨段「『當送出表單』被判對外送出,不改表」;門規則版本升到 13
    id: d1
    context: order-web 前端示範:規格閘把「再按也不會送出第二個請求」「請求送出時刻記錄」判成對外送出、把環境變數 ORDER_PAYMENT_TIMEOUT 判成金流,四類已排除行都寫了照樣風險高(硬訊號一命中就不能低);表單送出是前端最常見的詞
    why_chosen: 使用者 2026-10-15 裁「加前端與識別字例外」;同日對本 repo 與三個消費專案共 356 份計劃新舊比對,改判風險低 0 份,新版沒有多出命中;送出例外遇到去處照算、識別字例外只收 payment 一字,把新增漏判收窄到量得到的範圍
    decided: 2026-10-15
    valid: true
  - content: 本機基礎設施腳本題組(infra)進推送前的表態閘:改到 .sh 或測試基礎設施路徑的檔命中 infra 題,要表態才推得出去
    id: d2
    context: 待決問題 Q1:進閘多一道手續(含工具鏈本 repo 的 get.sh 與 governance 腳本),不進則只列在 pitfalls 清單與派工詞;設計審首輪前掃指出計劃在 Q1 未定時已把它寫成定案
    why_chosen: 編排者 2026-10-15 定:能機械擋就不只提醒
    decided: 2026-10-15
    valid: true
pending_questions:
  - id: Q1
    text: 本機基礎設施腳本題組(infra)要不要進推送前的表態閘?進=改到 .sh 命中題就要表態才推得出去(含工具鏈本 repo 的 get.sh 與 governance 腳本);不進=只列在 pitfalls 清單與派工詞
    class: 守衛面
    stage: 實作
    status: 已決
    decision: "#d2"
---
# 前端知識與風險詞_計劃

> 白話:lumos 的提問、審查範本和風險詞表都是照後端長出來的。一次 React 前端示範裡,該問的前端問題(載入/錯誤狀態、時鐘、輪詢、回應亂序、e2e 腳本收尾)全靠編排者自己想到,反過來前端的日常字眼(「送出請求」「ORDER_PAYMENT_TIMEOUT」)又被當成對外送出、金流。這份計劃把前端該問的放進設計階段看得到的地方,並把那兩種誤判拿掉,不碰其他判法。

## 緣起

- 2026-10-15 order-web 示範(React + TypeScript + Vite;order-web 是示範用的消費專案,本機另一個 repo,不在本 repo 裡;卷證在那個 repo 的 `governance/review-reports/code-搶購下單畫面/`):兩輪設計審 96 條發現,lumos 自己的出題、檢核題、規格閘預先指出的是 0 條,全部來自派工詞裡編排者手寫的前端版鏡頭(F19)。代碼審三輪裡,e2e 腳本那一族(共用埠與容器、/tmp 鎖與狀態檔、pid 驗證、路徑別名、curl 沒逾時)換了三次形狀才收斂(rN=那次代碼審的第 N 輪:r1 全機共用資源 → r1 修補把鎖放到 /tmp → r2 資安席實測別的本機使用者可預放狀態檔讓收尾 kill 任意程序 → r2 改成每份工作樹自己的資源 → r3 路徑別名讓 `--cleanup` 假成功、健康檢查沒逾時)。
- 本計劃負責 [[Projects/Web示範前端缺口_調研]](示範缺口比對表;2026-10-15 寫這句時那篇在 EnzoHsieh-Android/web-gaps 分支)的 C 組(F4、F10、F19、F13、F18、F27、F30、W11)與 D 組(F5、W3、W4);本文的 F/W/B 編號都是那篇比對表的列號(F=示範編排者記的、B=後端代理回報、W=前端實作代理回報)。
- 使用者 2026-10-15 裁「加前端與識別字例外」(d1):風險詞表的「送出」接在請求、表單、第二個這類前端語境時不算對外送出,全大寫識別字裡的 PAYMENT 不算金流。這推翻 [[Projects/雙向門放行_計劃]] 取捨段那一行:關鍵字表粗,「送出」出現在條款裡就變風險高(fixture 實測「當送出表單」被判對外送出),而那篇決定不改表、當成預設單向的代價。

PRIOR-ART: 全部借既有形狀,不長新機制——前端面照需求風險面表 `_REQUIREMENT_FACETS` 的列(id/stage/q/when);本機腳本題組照棧別題庫 `_STACK_QUESTION_SPECS` 的形狀(id/q/when),自動進 pitfalls 清單、改檔前推播與表態閘;範本改述照 templates.md §7.7 A 表與 §7.8〈消費專案六類〉之後加 ### 小節的先例;詞表例外寫成詞表本身的正規式,沿用 r11 已用過的「前後不是英文字母或數字」lookaround 寫法,門判定與 `pitfalls --check` 兩條路自動一起變。前端題目內容參考 OWASP 前端資安清單(XSS、CSRF、開放式轉址、CSP、postMessage)與 Testing Library user-event 官方文件的 `advanceTimers` 選項。
RETIRE-IF: 上線後三個月內,前端計劃(`pitfalls` 判成前端的計劃)的設計審與代碼審卷證裡,帶 req-fe-/arch-fe-/impl-fe-/infra- 題號被折入的發現少於 3 條,而且同期沒有一筆前端相關的逃逸帳(`lumos loop escape` 記的漏網紀錄,定義見 [[Systems/loop-convergence-recording]])——把前端面與 infra 題組撤成只在手冊提一句;詞表例外那半另看:逃逸帳出現任何一筆「因為送出例外或識別字例外而判風險低、事後抓到真的對外送出或金流」,撤回該條例外。
REVISIT:[when-file:docs/lumos-toolchain-knowledge/Projects/Web示範前端缺口_調研.md][by:2026-11-15] 比對表那篇合進主線後,拿掉緣起段「那篇在 web-gaps 分支」的說明;到期還沒合就查那條分支的去向
REVISIT:2027-01-15 數 req-fe-/arch-fe-/impl-fe-/infra- 題號在卷證與表態帳裡的出現與折入數,對照 RETIRE-IF 判撤不撤
REVISIT:2027-01-15 對本 repo 與所有消費專案的 Projects 計劃重跑一次詞表新舊比對(做法 9 的量法),數「因例外而少掉、該類在整份再無其他命中」的份數;大於 0 就逐份人看是不是漏判,漏判就收窄例外

## 現況(2026-10-15 讀本工作樹 scripts/lumos 與範本,以程式為準)

- 需求風險面表 `_REQUIREMENT_FACETS` 14 列:req-success、req-scope、arch-irreversible、verify-evidence、deliver-ops 五列對任何計劃都亮(when 是任意字),其餘九列的觸發詞與題目是後端角度(量級、佇列、一致性、併發),沒有一列問前端的事;`pitfalls --stage` 的 `_pitfalls_stage` 只拿計劃全文比 when。`pitfalls <計劃>` 的計劃模式印通用四問、命中類追問,以及圖譜裡帶 `pitfall_ask` 的「業界已知的常見坑」(`_pitfall_scan_known`),都沒有前端題;`--check` 只印 ✓/✗。
- 前端的競態、卸載、狀態、無障礙、XSS 只在代碼審正確性席的角色卡 `_ROLE_CARDS`,經派工詞的 `LUMOS-ROLE-CARDS: on` 由掛鉤附上;設計審沒有。客戶端時鐘偏快哪裡都沒有;退避與冪等鍵只有後端外呼的一般問法(棧別題 kt-springhttp 問重試退避與不可逆操作的冪等鍵、payment 類追問問冪等鍵設計),沒有「前端輪詢怎麼退避」與「換使用者時冪等鍵歸誰」的問法。
- templates.md §1 設計審審計員第 5 點的實務隱患鏡頭(連線/鎖、回滾、遷移順序與鎖表窗口)與 §3 代碼審鏡頭是後端語彙;§7.7 A 表的席位立場本身不帶後端字眼,但五個鏡頭都沒有前端版說法,編排者得自己翻譯。§7.8〈消費專案六類〉只有第 6 類行動端,沒有網頁前端;這段被 `t_` 開頭的鏡頭範圍測試逐字釘住(跟改動前圍欄原文一字不差)。
- 棧別題庫沒有 shell 或本機腳本題組:`_stack_key_for_file` 對 `.sh` 回 None;`e2e/` 底下的 `.ts`(前端 package.json 之下)回 vue,於是 `e2e/global-setup.ts` 的 `fetch(` 亮 vue-reactive 那題。`_PITFALL_DIFF_TEST_PAT` 不認 `e2e` 路徑,`_stack_changed_ok` 照掃,`scripts/e2e.sh` 裡的 `INSERT INTO` 命中 `_PITFALL_DIFF_PATTERNS` 的「寫入有沒有交易包裹?」→ 分級直接 high。
- 架構對齊的對照檔(`_arch_alignment_hints` 取同資料夾、同副檔名最像的三支)不排除工具自帶檔,消費專案 `scripts/` 底下 init 裝進去的 `graph-rename.sh`、`fetch-notesmd.sh` 會被當成 `scripts/e2e.sh` 的鄰居。
- 測試品質指引(lumos-project-notes 的 `commands/test-quality-standard.md` 與 `03-寫回圖譜.md`〈實作測試品質〉)沒有前端:搜不到 fake timers、user-event、Testing Library。
- 風險詞表 `PITFALL_CLASSES`:`送出` 是裸字、`payment` 不分大小寫也不看詞界,`_door_keyword_hits` 對「請求送出時刻記錄」「再按也不會送出第二個請求」回對外送出、對 `ORDER_PAYMENT_TIMEOUT` 回金流。門規則版本 `_DOOR_RULE_VERSION` 現在是 12、掃描判法 `_DOOR_SCAN_LOGIC_VERSION` 是 8。
- **跟比對表不一樣的一處**:比對表 W3 說「實作 diff 判 tier high(同 F5)」。`pitfalls --diff` 的分級(`_pitfall_tier`)只看代碼型樣命中、殘留與告警,**不用這張詞表**;那次實作判 high 的來源是 `scripts/e2e.sh` 的 `INSERT INTO` 命中交易包裹型樣(W4 這條),不是 PAYMENT。所以 D 組改詞表只影響規格閘的門與 `pitfalls --check`,實作分級靠做法 7 處理。

## 做法

### 1. 一條「前端計劃」判準(F4、F13、F10 共用)

- 新增一個正規式常數(暫名 `_FE_PLAN_WHEN`),比計劃全文:副檔名 `.tsx` `.jsx` `.vue` `.svelte`、框架名 React / Vue / Svelte / Angular / Next.js / Nuxt / Vite(前後不是英文字母)、中文「前端」「瀏覽器」。不收「畫面」「元件」「頁面」——後端計劃也常寫(「新元件」在 arch-necessity 那列就是後端意思)。
- 下面的前端面全部用這一條當 when;計劃模式的「前端面」段與 `--check` 的提醒也用它判。判錯的代價是多列幾題,不擋任何東西。

### 2. F4 需求風險面加前端面

在 `_REQUIREMENT_FACETS` 加下列各列,每列多一個鍵 `role: "frontend"`(既有列不帶這個鍵,`--stage --json` 的輸出只是多一個鍵):

| id | 階段 | 要釐清什麼 |
|---|---|---|
| req-fe-states | 需求 | 載入中、空資料、失敗、結果不確定(逾時、斷線、送了沒回)四種狀態各長什麼樣?使用者在每種狀態能做什麼、不能做什麼? |
| req-fe-device | 需求 | 支援哪些裝置、瀏覽器與螢幕寬度?無障礙做到哪(只用鍵盤、螢幕報讀、對比)?哪些瀏覽器的鍵盤行為不同(例:macOS Safari 預設 Tab 不停在按鈕)? |
| arch-fe-clock | 架構 | 倒數、期限、「現在能不能按」用誰的時間?瀏覽器時鐘偏快或偏慢幾分鐘時畫面會怎樣?要不要用伺服器回應的時間校正? |
| arch-fe-stale | 架構 | 畫面上的資料多舊算過期?過期時怎麼讓使用者看得出來、什麼時候重抓? |
| arch-fe-origin | 架構 | 前端跟 API 是不是同一個來源?跨來源時 CORS、cookie、CSRF 誰設定?開發時的代理跟正式環境差在哪? |
| perf-fe-budget | 效能 | 首屏時間、bundle 大小、互動延遲的目標各是多少?在什麼裝置與網路下量? |

### 3. F13 前端問題族進設計階段

同一張表再加(同樣帶 `role: "frontend"`):

| id | 階段 | 要釐清什麼 |
|---|---|---|
| arch-fe-poll | 架構 | 輪詢多久一次、失敗時怎麼退避(間隔拉長、上限、背景分頁暫停)?同時開著的使用者數乘上頻率,後端與連線池扛不扛得住? |
| impl-fe-race | 實作 | 同一畫面連發兩次請求、舊的比新的晚回來,會不會蓋掉新資料?離開畫面或換使用者時,在途請求的結果怎麼丟掉? |
| impl-fe-lifecycle | 實作 | 計時器、輪詢、訂閱在元件卸載時有沒有收掉?重複掛載時會不會跑兩份(React StrictMode 開發模式會故意掛兩次)? |
| impl-fe-idem | 實作 | 連點、重新整理、重送時的冪等鍵由誰產生、存在哪?換使用者、換商品或上一筆已成功時要不要換新的? |

- 設計階段看得到的兩個入口:①`pitfalls --stage <階段>` 照階段列(現有通道);②計劃模式 `pitfalls <計劃>`(不帶 `--check`)在既有輸出後面多一段「前端面(這份計劃提到前端:命中「…」)」,不分階段逐條列出所有 role 為 frontend 的列(題號加題目);③`pitfalls <計劃> --check` 對前端計劃多印一行提醒:「這份計劃是前端:設計審派工用 templates.md §7.7〈前端計劃改述〉,`lumos pitfalls <計劃>` 有前端面要逐條答」,回傳碼不變。設計審手冊第 2 步本來就跑 `--check`,編排者一定看得到這行。
- 跟角色卡的分工:角色卡問「程式有沒有做到」(代碼審),前端面問「設計怎麼定」(設計審),所以亂序、卸載兩族兩邊都有、措辭不同;`_ROLE_CARDS` 不動(題號計數是它的撤除條件,改了等於量測歸零)。
- 內容源照既有規矩記在 [[Systems/情境出題]](它負責需求風險面表的內容源),寫清每一列來自這次示範的哪一族發現。

### 4. F10、F19 設計審派工範本的前端改述

- templates.md §7.7 在 A 表之後加一個 ### 小節〈前端計劃改述〉(不改 A 表本身):被審計劃是前端(做法 1 的判準、`pitfalls --check` 印了前端提醒)時,五個設計審鏡頭的立場照下表換成前端版措辭,其他規矩(引句、severity、抑噪)不變。代碼審也可以用,但代碼審的前端方向主要靠角色卡。

| 鏡頭 | 前端版要看的 |
|---|---|
| 正確性/邏輯 | 每個畫面狀態(載入、空、失敗、不確定)與每條非同步順序(亂序、取消、重送)下,畫面會不會顯示錯的東西或讓人按到不該按的 |
| 邊界可執行 | 空清單、單筆、超長文字、慢網路、斷線、極小螢幕、只用鍵盤、時鐘偏快偏慢 |
| 整合/知識同步 | 前端依賴的 API 欄位與錯誤格式跟後端現況對不對得上;開發代理與正式環境的來源、cookie 差異;瀏覽器相容範圍 |
| 資源併發 | 計時器、輪詢、訂閱的生命週期(卸載、StrictMode 重複掛載);連點與在途請求;輪詢對後端的壓力與退避;e2e 腳本起停的本機資源(做法 6 的題組) |
| 回滾 | 前端部署回退時使用者手上的舊 bundle、快取、本機存的狀態會不會跟新後端打架;功能開關能不能只關前端 |

- §1 審查要求第 5 點(實務隱患鏡頭)後面加一句填空:「{前端計劃:`lumos pitfalls <計劃>` 印的前端面逐條想過,鏡頭措辭用 §7.7〈前端計劃改述〉}」;不是前端就整行刪。
- 架構對齊席要的 React 慣例 skill 不在這裡做(見〈不做〉,交界在 [[Projects/前端框架從vue分出_計劃]])。

### 5. F27 資安席加網頁前端類

- §7.8 在〈消費專案六類〉之後、〈工具鏈三類〉之前加 ### 小節〈網頁前端類〉;〈消費專案六類〉一字不改(被逐字釘住,而且後端專案用不到前端類)。說明句:被審改動含網頁前端檔(`.tsx` `.jsx` `.vue` `.svelte` `.html`,或前端 package.json 底下的 `.ts` `.js`——角色鏡頭會附前端卡的那種)時,把這段接在六類後面一起貼進逐類清單填空。內容八項:
  1. XSS:使用者或外部內容當 HTML 插進頁面(`dangerouslySetInnerHTML`、`v-html`、`innerHTML`)、`javascript:` 網址
  2. CSRF:用 cookie 帶身分的寫入請求有沒有防護
  3. 開放式轉址:跳轉網址來自查詢參數或外部輸入有沒有驗
  4. CSP:有沒有內容安全政策、有沒有被放寬成 `unsafe-inline`、`unsafe-eval`
  5. 權杖與個資放在 localStorage、sessionStorage 這類 JS 讀得到的地方
  6. postMessage:收訊有沒有驗來源、送訊有沒有指定目標來源
  7. 第三方腳本:從外部 CDN 載入有沒有固定版本或完整性雜湊
  8. 開發代理與環境變數:開發伺服器的代理設定、打包進前端的環境變數會不會把內部網址或密鑰帶到正式環境
- §7.8 圍欄裡「(選配)專案資安類 linter 的輸出」之後加一行選配材料:「(選配)pitfalls 清單裡 infra- 開頭的題:{被審改動有本機腳本才附}」——做法 6 的 /tmp、pid、路徑三題是資安面,資安席要看到同一份題,不另抄一份清單。

### 6. F18、F30 本機基礎設施腳本題組

- 棧別題庫 `_STACK_QUESTION_SPECS` 加一組鍵 `infra`(本機基礎設施腳本:起停後端、資料庫、容器的 shell 與 e2e 設定檔),六題,每題 when 只收那一題的寫法:

| id | 題目 | 觸發寫法(方向) |
|---|---|---|
| infra-shared | 埠、容器名、compose 專案名、/tmp 底下的檔與鎖,會不會跟另一份工作樹或另一次執行撞?能不能每份工作樹各自挑、放回工作樹裡? | `/tmp/`、`mktemp`、`--name`、`container_name`、`COMPOSE_PROJECT_NAME`、`-p 數字:`、`localhost:數字`、`PORT=` |
| infra-timeout | 外部指令(curl、docker、資料庫用戶端、建置工具、等待迴圈)有沒有逾時?macOS 沒有 timeout 指令,用什麼替代? | `curl`、`wget`、`docker`、`psql`、`mysql`、`gradlew`、`until`、`sleep` |
| infra-signal | Ctrl-C、kill、腳本中途失敗時,起的程序與容器怎麼收?trap 有沒有涵蓋結束與中斷、TERM 之後有沒有 KILL 兜底、收不乾淨時會不會照樣回報「收尾完成」? | `trap`、行尾 `&`、`nohup`、`setsid`、`kill`、`wait`、`child_process`、`spawn(` |
| infra-pid | 收尾殺程序前,有沒有確認那個 pid 還是自己起的那支(pid 檔可能被別人預放、pid 可能被重用;0 與 -1 會打到整個程序群組)? | `kill`、`.pid`、`$!`、`pkill`、`pgrep` |
| infra-path | 比對或刪除前有沒有先把路徑實體化(realpath、`pwd -P`)?symlink 或別名路徑會不會讓檢查放行、刪錯地方? | `rm -`、`realpath`、`readlink`、`ln -s`、`cd ` |
| infra-portable | macOS 與 Linux 的差異(timeout、setsid、`sed -i`、date、ps 欄位、`readlink -f`、stat)有沒有處理?只在一邊跑過要寫明 | `sed -i`、`date`、`readlink -f`、`setsid`、`ps `、`stat `、`uname` |

- `_stack_key_for_file` 加一條最先判的規則:副檔名 `.sh` `.bash`,或路徑符合「測試基礎設施」樣式(做法 7)的檔 → `infra`。之後才走現有的副檔名與 package.json 判法。四個消費者(pitfalls 清單、架構對齊的可能撞、表態閘、改檔前推播)都經這一支,自動一起變。
- `_STACK_PERF_QUESTIONS` 由題庫派生,不用另改;[[Systems/效能檢核目錄]] 要同步加這一組(題庫註解寫明目錄與表雙向同步)。infra 不是語言,不配慣例 skill、不走 [[Systems/補新語言SOP]] 八格。
- 設計階段的入口:需求風險面加一列 `verify-infra-script`(驗證階段;when 比 e2e、end-to-end、端到端、Playwright、Cypress、docker compose、起後端、起資料庫),題目:「要起本機服務的測試腳本:埠與容器怎麼避開別份工作樹、外部指令的逾時、中斷時怎麼收、殺程序前怎麼確認是自己的、路徑先實體化、macOS 與 Linux 差異,各怎麼定?」這列不帶 `role: "frontend"`(後端專案的 e2e 一樣適用)。
- 角色鏡頭:`_review_role_for` 看到 `infra` 鍵回 None(不是前端也不是後端),所以 `e2e/` 底下原本被判成前端的檔不再附前端卡、改計進「判不出」。這是刻意的:e2e 腳本不是產品畫面。

### 7. W4 腳本與測試資料不當產品程式問(只做這半)

- 新增一個路徑樣式常數(暫名 `_TEST_INFRA_PATH_RE`):路徑裡有一段恰好是 `e2e`(`e2e/global-setup.ts`),或檔名以 `e2e` 開頭或結尾、跟其他字之間用 `.` `-` `_` 隔開(`scripts/e2e.sh`、`e2e-selftest.sh`、`order.e2e.ts`、`run_e2e.sh`),或在 `fixtures/`、`fixture/`、`seeds/`、`seed/` 資料夾底下;`e2easy.ts`、`fixture.ts` 不算。寫法(2026-10-15 對這幾個例子試過):`(?:^|/)e2e(?:/|$)|(?:^|/)e2e[._-][^/]*$|[._-]e2e(?:[._-][^/]*)?$|(?:^|/)(?:fixtures?|seeds?)/`(不分大小寫)。
- 符合這個樣式的檔:①棧別鍵一律 `infra`(做法 6),不再拿 vue-reactive、sql-transaction 這類產品題;②`_pitfall_diff_collect` 掃代碼型樣(`_PITFALL_DIFF_PATTERNS`)時跳過,不產生「寫入有沒有交易包裹?」「N+1」這類 claims,分級不因造資料的 SQL 變 high。只限這個樣式:`scripts/deploy.sh` 這種不在測試路徑的腳本照舊掃型樣(可能真的動正式資料庫)。
- 架構對齊對照檔:`_arch_alignment_hints` 挑鄰居時排除 `_vendored_skip` 那份「原封不動的工具自帶檔」集合(`_pitfall_diff_collect` 已經算好,傳進去即可),消費專案的 `scripts/e2e.sh` 不再拿 `graph-rename.sh` 當對照。工具鏈本 repo 這個集合是空的,行為不變。
- **交界**:`src/api.ts` 這種產品前端檔的 `fetch(` 被當成 vue-reactive 那題,是「React 被歸成 vue」的問題,歸 [[Projects/前端框架從vue分出_計劃]](另一份計劃,同一天在寫)。兩份都改 `_stack_key_for_file`:**本計劃的「測試基礎設施路徑 → infra」排在最前面,那份的框架分流排在後面**;誰後合進主線,誰負責把這個順序接好,並保留兩邊的測試(本計劃 S11 與那份的 React 分流測試)。架構對齊席該配哪份慣例 skill 也歸那份。

### 8. W11 測試品質指引加前端節

- `commands/test-quality-standard.md` 照〈PHP／Laravel 的撰寫與接入補充〉的形狀,加一節〈網頁前端(Vitest／Jest + Testing Library)的撰寫補充〉,至少三條:
  1. 假計時器與 user-event:`vi.useFakeTimers()` 之後 user-event 的內部延遲會卡住、測試逾時;用 `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })`,或只假 `setTimeout`/`setInterval`。假計時器預設連 `Date` 一起假,測時鐘偏移要用 `vi.setSystemTime` 明寫「現在」,不要讓兩種時間混在一起。
  2. fetch 替身:用 `vi.stubGlobal('fetch', …)` 或 MSW 回可控的 Promise,手動決定哪個請求先回,才測得到回應亂序;只回固定成功值的替身證明不了「舊回應不會蓋掉新資料」。測完還原(`vi.unstubAllGlobals`)。
  3. 同輪連點:user-event 的兩次 `click` 之間會等畫面更新,按鈕已經 disabled,測不到「同一輪事件裡連點兩次」;要測防重送的 ref 守衛,用同一個同步區塊連發兩次 `fireEvent.click`,再斷言只送出一個請求。
- 各條實作時對照官方文件核對版本(Vitest、Testing Library user-event),出處連結寫在節尾,跟 PHP 節一樣。
- `03-寫回圖譜.md`〈實作測試品質〉結尾那句「各棧接入…讀 [測試品質接入標準]」補上「前端的假計時器、fetch 替身與連點測法在同一份的網頁前端節」;規範本體只留一份,不在 03 複述。

### 9. F5、W3 風險詞的前端與識別字例外(使用者 d1)

- 改 `PITFALL_CLASSES` 兩個詞的正規式,不加別的機制:
  - 對外送出的 `送出` 改成:前面是「請求」「表單」、或後面接「請求」「表單」「第二個」「第二次」(「第」字後面的數字也可以寫成 兩、2)的不算——只認帶「第」的序數寫法,「送出兩次請求」「送出 2 次」照算;**但前端語境詞後面緊接著寫出去哪(給、到、至、往)照算**——「送出請求到外部物流 API」「把表單送出給第三方」「送出表單至客服信箱」仍命中。寫法(2026-10-15 試算用的):`(?<!請求|表單)送出(?!請求|表單|第[二兩2][個次])|送出(?=(?:請求|表單)[給到至往])|(?<=請求|表單)送出(?=[給到至往])`。
  - 金流的 `payment` 改成:大寫的 `PAYMENT` 前面或後面緊貼底線時不算(`ORDER_PAYMENT_TIMEOUT`、`PAYMENT_TIMEOUT`、`order_PAYMENT`);小寫或大小寫混合的識別字(`payment_service`、`Payment_Gateway`)、單獨的 `PAYMENT`、中文句子照算。寫法:`payment(?<!(?-i:_PAYMENT))(?!(?<=(?-i:PAYMENT))_)`。
- WHY:例外只收 `payment` 一字 [出處:使用者 2026-10-15 裁定點名 ORDER_PAYMENT_TIMEOUT] [因:`STRIPE_SECRET_KEY`、`REFUND_WINDOW_DAYS` 這類大寫識別字多半真的在接金流,一起豁免會漏判] [不選:四類的英文詞全部套大寫識別字例外(規格閘不做節代碼審第 11 輪刻意讓 `send_email`、`prod_db` 命中,`PROD_DB_URL` 跟著豁免就是放寬)]
- WHY:送出例外遇到「給/到/至/往」照算 [出處:2026-10-15 本計劃試算] [因:只看前後兩字,「送出請求到外部物流 API」「把表單送出給第三方」原本命中、會變成漏判,而表裡沒有「外部」「第三方」可接住] [不選:同一句有「到」就照算(「請求送出時刻與收到時刻」的「收到」也有到,例外整個失效)]
- 這張表也是 `pitfalls <計劃> --check`(`_pitfall_scan_classes`)的詞表,兩條路一起變——跟規格閘不做節那次代碼審第 11 輪(code-規格閘不做節 r11)改英文詞界時同一個取捨,不另分岔。
- 門規則版本 `_DOOR_RULE_VERSION` 升到 13(說明加「13=2026-10-15 送出的前端語境與 PAYMENT 大寫識別字例外」);詞表進門規則指紋,`t_door_rule_version_pin` 的指紋跟著更新。掃描判法 `_door_keyword_hits`、`_door_scan_text` 不動,`_DOOR_SCAN_LOGIC_VERSION` 維持 8。舊留痕照門規則版本的既有規矩從零重數。
- 量法與結果(2026-10-15,唯讀腳本,新舊兩版詞表各跑一次 `_door_keyword_hits`,比每份計劃的(行, 類)命中):本 repo 352 份,加三個本機消費專案 repo(order-demo 後端示範、order-web 前端示範、order-web-impl 是 order-web 的實作工作樹)的 Projects,合計 356 份。**新版沒有多出任何命中;少掉命中的只有 2 份**(order-web 與 order-web-impl 的同一份搶購下單畫面計劃,少掉第 185 行的對外送出、第 130 與 203 行的金流),**兩份在那兩類都還有別行命中,門的結論不變,改判風險低的是 0 份**。
- 跟 [[Issues/門掃描詞表沒收常見寫法]](反向、漏判)一起量:那篇列的 `sends`、`寄信`、`TRUNCATE TABLE`、`LINE 推播` 等寫法新舊兩版都比不到——本例外沒讓它們更糟,也沒修它們;那篇照舊 open,修法(補詞)另開計劃。本計劃改的兩個詞跟那篇列的寫法沒有重疊。
- [[Projects/雙向門放行_計劃]] 取捨段那一行改寫成:「關鍵字表粗:『上架』『遷移』出現在條款裡就變風險高。『送出』在請求、表單、第二個這類前端語境已在 2026-10-15 改成不算([[Projects/前端知識與風險詞_計劃]] d1),其餘不改表」;[[Systems/規格閘]] 承認「四類關鍵字表粗」那句同步補一句例外。

## 驗收條款

- [S1] 當計劃文字提到 `.tsx` 時,`pitfalls --stage 需求` 應列出 req-fe-states 與 req-fe-device。[test: t_pitfalls_stage_frontend_facets_listed]
- [S2] 當計劃文字沒有任何前端字樣時,`pitfalls --stage 需求` 應不列任何 role 為 frontend 的面,輸出跟改動前一樣。[test: t_pitfalls_stage_no_frontend_facets_for_backend_plan]
- [S3] 當計劃提到 React 時,`pitfalls --stage 架構` 應列出 arch-fe-clock、arch-fe-stale、arch-fe-origin、arch-fe-poll。[test: t_pitfalls_stage_frontend_arch_facets]
- [S4] 當計劃提到「前端」時,`pitfalls --stage 實作` 應列出 impl-fe-race、impl-fe-lifecycle、impl-fe-idem,而且 impl-fe-lifecycle 的題目含 StrictMode。[test: t_pitfalls_stage_frontend_impl_facets]
- [S5] 當計劃提到 `.vue` 時,`pitfalls --stage 效能` 應列出 perf-fe-budget。[test: t_pitfalls_stage_frontend_perf_facet]
- [S6] 當計劃提到 Playwright 時,`pitfalls --stage 驗證` 應列出 verify-infra-script。[test: t_pitfalls_stage_infra_facet]
- [S7] 當對前端計劃跑 `pitfalls <計劃>`(不帶 --check)時,輸出應有「前端面」一段,列出所有 role 為 frontend 的題號。[test: t_pitfalls_spec_mode_lists_frontend_facets]
- [S8] 當對前端計劃跑 `pitfalls <計劃> --check` 時,應多印一行前端提醒且回傳碼跟改動前相同。[test: t_pitfalls_check_frontend_hint_keeps_rc]
- [S9] 當讀 templates.md 時,§7.7 應有〈前端計劃改述〉小節、五個設計審鏡頭各一句前端版措辭,§1 審查要求第 5 點應有指到它的填空。[test: t_templates_frontend_lens_rewrite]
- [S10] 當讀 templates.md §7.8 時,〈消費專案六類〉應跟改動前逐字相同,而且其後應有〈網頁前端類〉小節列出 XSS、CSRF、開放式轉址、CSP、storage 權杖、postMessage、第三方腳本、開發代理八項。[test: t_templates_security_web_frontend_class]
- [S11] 當 diff 只改到前端 package.json 底下的 `e2e/global-setup.ts`、新增行有 `fetch(` 時,適用題應不含 vue-reactive、應改列 infra 題組。[test: t_stack_key_e2e_path_is_infra]
- [S12] 當 diff 改到 `scripts/e2e.sh`、新增行有 `kill "$pid"` 與 `/tmp/` 時,pitfalls 清單的適用題應含 infra-pid 與 infra-shared。[test: t_pitfalls_diff_infra_questions_for_shell]
- [S13] 當 diff 改到 `scripts/e2e.sh`、新增行只有 `INSERT INTO` 造資料時,claims 應不含交易包裹題,分級應不因這行變 high。[test: t_pitfalls_diff_e2e_sql_not_product_claim]
- [S14] 當 diff 改到 `scripts/deploy.sh`、新增行有 `DELETE FROM` 時,claims 應照舊含交易包裹題。[test: t_pitfalls_diff_plain_shell_sql_still_claimed]
- [S15] 當推送範圍的 `.sh` 改動命中 infra 題時,表態閘應跟其他棧一樣要求表態。[test: t_disposition_gate_covers_infra_questions]
- [S16] 當消費專案改動檔的同資料夾有原封不動的工具自帶檔時,架構對齊對照檔應不列那支自帶檔。[test: t_arch_alignment_skips_vendored_siblings]
- [S17] 當讀 test-quality-standard.md 時,應有網頁前端節,含 advanceTimers 設定、fetch 替身、同輪連點三條,而且 03-寫回圖譜.md〈實作測試品質〉應有一句指到那一節。[test: t_test_quality_standard_frontend_section]
- [S18] 當計劃一行寫「請求送出時刻記錄」時,門的關鍵字掃描應不回對外送出。[test: t_door_keyword_send_request_context_exempt]
- [S19] 當計劃一行寫「按鈕再按也不會送出第二個請求」時,門的關鍵字掃描應不回對外送出。[test: t_door_keyword_send_second_request_exempt]
- [S20] 當計劃一行寫「當送出表單」時,門的關鍵字掃描應不回對外送出。[test: t_door_keyword_send_form_exempt]
- [S21] 當計劃一行寫「送出請求到外部物流 API」時,門的關鍵字掃描應照舊回對外送出。[test: t_door_keyword_send_with_destination_still_hits]
- [S22] 當計劃一行寫「系統會送出通知給客戶」時,門的關鍵字掃描應照舊回對外送出。[test: t_door_keyword_send_plain_still_hits]
- [S23] 當計劃一行寫 `ORDER_PAYMENT_TIMEOUT` 時,門的關鍵字掃描應不回金流。[test: t_door_keyword_caps_identifier_payment_exempt]
- [S24] 當計劃一行寫 `payment_service` 時,門的關鍵字掃描應照舊回金流。[test: t_door_keyword_payment_lowercase_identifier_still_hits]
- [S25] 當計劃一行寫 `STRIPE_SECRET_KEY` 時,門的關鍵字掃描應照舊回金流。[test: t_door_keyword_caps_stripe_still_hits]
- [S26] 當 `pitfalls <計劃> --check` 掃到只有「請求送出時刻」的計劃時,命中類應不含 external-send。[test: t_pitfalls_check_shares_send_exemption]
- [S27] 當載入新版程式時,門規則版本應是 13、掃描判法版本應維持 8,規則指紋應等於測試釘的新值。[test: t_door_rule_version_pin]
- [S28] 當用做法 9 的量法對同一批計劃重跑時,改判風險低的份數應是 0。[manual: 重跑 2026-10-15 那支唯讀比對腳本(對本 repo 與三個消費專案的 Projects),輸出「該類在整份再無其他命中」的行數應為 0]
- [S29] 當讀 [[Projects/雙向門放行_計劃]] 取捨段時,「送出」那一句應已改寫並指到本計劃 d1。[manual: 打開那篇搜「當送出表單」,應找不到「不改表」的舊句]

## 實務隱患

- 守衛面(碰,照實寫):
  - 門的詞表放寬兩個詞:規格閘可能把原本判高的計劃判低、少一輪設計審;`pitfalls --check` 同步少命中。量到的影響是 0 份改判(做法 9),新漏判形狀靠「給/到/至/往照算」與只豁免 payment 一字收窄;剩下的天花板:「送出請求」後面隔了別的字才寫去處(「送出請求,目的地是外部物流」)比不到,寫進逃逸帳的撤除條件(RETIRE-IF)。
  - 測試基礎設施路徑跳過代碼型樣:只改 e2e 腳本的推送分級可能從 high 降成 standard(仍要一席審),換來 infra 題組。路徑樣式寫太寬會讓產品程式躲進來(例:把正式資料庫的維運腳本放在 `seeds/`),所以只收四種資料夾名與 e2e 字樣,不收 `scripts/` 整個資料夾。
  - infra 題組進表態閘:改到 `.sh` 的推送(包含工具鏈本 repo 的 `get.sh`、`governance/*.sh`)命中 infra 題就要表態才推得出去,多一道手續;題目 when 只收具體寫法,不是改到 `.sh` 就整組亮(超過行數門檻時照既有規則整組亮)。進閘已定(d2,編排者 2026-10-15:能機械擋就不只提醒;待決問題 Q1 已結)。
  - 角色鏡頭:e2e 檔改判「判不出」,這些檔不再附前端卡;前端卡撤除條件的計數只算正確性席,影響是少數。
- 併發:不碰,工具一個人依序操作。
- 效能:新增的正規式每行多比幾個詞、每支改動檔多比一次路徑樣式,量級跟既有詞表相同;`_vendored_skip` 已經算好、只是多傳一個參數。
- 相容:`--stage --json` 的前端列多一個 `role` 鍵,既有列形狀不變;`_stack_key_for_file` 多回一種值 `infra`,呼叫端都用 `in _STACK_PERF_QUESTIONS` 或 `in _ROLE_BACK_KEYS` 判,不會崩。
- 已排除:金流:只改判定用的詞表與提問文字,不碰任何付款或點數程式。
- 已排除:對外送出:全是本機判定與手冊文字,不連任何外部服務。
- 已排除:不可逆:還原提交即回到原詞表與原題庫;門規則版本升級讓舊留痕重數,回退時版本號照規矩再升一次,不改舊帳。

## 不做

- 不做 React 慣例 skill、不把 .tsx 從 vue 分出來、不改架構對齊席的慣例 skill 清單(歸 [[Projects/前端框架從vue分出_計劃]])。
- 不改 `_ROLE_CARDS` 的題目與題號(撤除條件靠題號計數)。
- 不補 [[Issues/門掃描詞表沒收常見寫法]] 列的那些寫法(反向漏判,另開計劃)。
- 不把大寫識別字例外套到 payment 以外的詞。
- 不寫 e2e 起停腳本範本(比對表 F26 的 macOS timeout 只進 infra-portable 一題)。
- 不做前端目標架構範本(比對表 F7,B 組)。

## 回退

- 每一塊各自可退:詞表兩個正規式改回裸字並把門規則版本再升一次(13 → 14,說明寫「撤回 13 的例外」);題庫拿掉 `infra` 鍵與 `_stack_key_for_file` 的第一條規則;需求風險面拿掉 role 為 frontend 與 verify-infra-script 的列;範本與測試品質指引刪掉新增的小節。
- 撤回時同一個提交刪掉對應的驗收測試,並把 [[Projects/雙向門放行_計劃]] 那一行改回、記一筆翻案決策。

## 合約候選

(無)

## 審計修正紀錄

