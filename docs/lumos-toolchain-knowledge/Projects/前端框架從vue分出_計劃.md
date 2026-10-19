---
type: project
status: doing
created: 2026-09-29
updated: 2026-10-15
aliases:
  - React 分出 vue
  - 前端框架分題
related:
  - "[[Projects/代碼審前後端角色鏡頭_計劃]]"
  - "[[Systems/補新語言SOP]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Projects/前端知識與風險詞_計劃]]"
  - "[[Projects/逾期回頭條件立案清單2026-10_計劃]]"
  - "[[Projects/測試名收自由字串_計劃]]"
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:[2026-09-29 Enzo 裁 [[Projects/代碼審前後端角色鏡頭_計劃]] d3「另外開」]前端依賴裡有 react/next/svelte/@angular/core/solid-js/preact 的檔,現在一律拿 vue 的棧別檢核題與 vue-idioms;要不要各自分出題組與慣例,走補新語言的標準流程另案處理
  REVISIT:2027-01-15 React 部分已開工(2026-10-15 order-web 接入滿足開工條件);到期時回填 order-web 或下一個 React 專案第一輪代碼審的結果:react 題組哪題從沒亮、哪題每次答不適用、react-idioms 漏了哪些坑;Svelte、Angular 仍歸 vue,到期還沒有這兩種專案就維持現狀再延一季;同一天也查 Projects/測試名收自由字串_計劃 做完沒,做完就在 order-web 跑 S30 的實地驗收,過了才把逾期清單第 10 節判成做完
lands_in:
  - Systems/pitfalls-code-loop
  - Systems/效能檢核目錄
  - Systems/棧別提問表態閘
  - Systems/test-profile-multiplatform
  - Systems/bound-tests-gate
  - Systems/lint-declaration-health
  - Systems/lumos-cli-lifecycle
  - Systems/arch-alignment-lens
  - Systems/linter精選目錄
  - Systems/補新語言SOP
decisions:
  - content: React 效能追問題組走 React 專屬題:effect 依賴與清理、回應亂序、重繪成本、清單 key、StrictMode、bundle 六題(另加各棧共有的外部回應碼題);2026-10-15 編排者裁加 react-parallel(並行等待),理由:效能檢核目錄的規矩是 idioms 裡標「⚠ 不可機檢」的條目優先入問,react-idioms ① 正是頭號不可機檢條款,vue 有 vue-parallel 對應;題組是計劃定的、使用者只裁了「走 React 專屬題」,加一題不算翻使用者裁定。Svelte、Angular 之後有專案再各自補,現在照舊歸 vue
    id: d1
    context: order-web(Vite+React+TS)是第一個 React 消費專案,.tsx 一律被判成 vue,拿到 ref()/v-for/watch 這類問錯方向的題與 vue-idioms;題目 id 被 t_stack_question_triggers 釘住,方向一開始就要選對(補新語言SOP 第 2 步)
    why_chosen: 六題都是 order-web 兩輪設計審與三輪代碼審真的出過、而且換一個 React 專案照樣成立的坑(輪詢亂序蓋掉新資料、卸載後在途結果還寫狀態、StrictMode 重掛載多發請求),問到點上;Svelte/Angular 目前沒有專案,照補新語言SOP 第 0 步不先補。不選:通用網頁前端題(一份題組給所有框架共用,問不到 effect 依賴、key、StrictMode 這些 React 才有的寫法,跟現在的 vue 題組一樣問偏);不選:維持歸 vue(現況,order-web 實測 vue 題對 React 寫法全部問錯方向);不選:React、Svelte、Angular 一次各補一組(後兩者零專案,補出來是零實證文件)。代價:Next.js 伺服端渲染與 Server Components 沒有專題(水合差異交給代碼審角色卡 fe-hydration);Svelte、Angular 專案接進來前仍拿 vue 題組,維持問偏,靠本篇 REVISIT 回頭;題組只從 order-web 一個專案的審查報告取材,第二個 React 專案跑完第一輪代碼審要回填哪題沒亮過
    decided: 2026-10-15
    valid: true
  - content: "Kotlin 檔看檔內匯入與建置檔分辨 Android 與伺服端:檔內有 android/androidx 匯入,或最近的 build.gradle(.kts)/pom.xml 先剝掉註解(Gradle 字串原樣留下;pom.xml 只剝 XML 註解)後有任何 Android 跡象(com.android.、版本目錄 libs.plugins.android、行首的 android {)→ Android;沒有 Android 跡象且有伺服端外掛宣告(id(…)/id '…'/apply plugin:/apply(plugin = …)/apply(plugin: …) 形式的 org.springframework.boot、io.ktor.plugin、Maven 的 spring-boot-maven-plugin 或 spring-boot-starter-parent、版本目錄 libs.plugins.spring.boot/springBoot/ktor)→ 伺服端,不列 Android 三題、角色判後端;依賴座標(org.springframework.boot:… 或 ktor-server)不算;被審的原始檔讀不到或超過讀取上限一律判不出;其他判不出照舊。翻掉 Projects/代碼審前後端角色鏡頭_計劃〈已知限制〉裡「.kt 沒有 android 匯入一律判不出」的設計取捨"
    id: d2
    context: B10:order-web 示範的 Spring 後端改 .kt 檔被問 Compose、洩漏、冷啟動題,角色判成「後端 0 支、判不出 1 支」。原取捨的理由是只看檔內匯入時 Kotlin 後端與 Android 非畫面檔分不開,寧可不附;那是代碼審角色鏡頭設計時的取捨,不是使用者裁定(編排者 2026-10-15 確認)
    why_chosen: 原理由的前提是「只有檔內匯入可看」;建置檔是專案層級的硬訊號:Android 模組一定有 Android 外掛(字面 com.android. 或版本目錄 libs.plugins.android),Spring Boot 與 Ktor 伺服端一定宣告自己的外掛,前提不成立了。規則刻意偏向判 Android 或判不出:Android 跡象優先、只認伺服端外掛不認一般 io.ktor 字串(Android 與 KMP 模組常用 ktor 客戶端,r1 設計審正確性與邊界兩席各舉一例),判錯只會多問不會少問;判法跟 .ts 看最近 package.json 同形狀,不新造機制。.java 維持看匯入:Java 後端的檔沒有 Android 匯入就判後端,現行沒有誤判回報;Kotlin 在 Android 的資料層、ViewModel 大量沒有 android 匯入,不能照抄 Java。不選:維持判不出(Spring 專案永遠拿 Android 題、拿不到後端卡);不選:看檔內 Spring 匯入(領域類、資料類多半沒有 Spring 匯入,大部分檔仍判不出);不選:要專案在 review_roles 自己宣告(既有出路,但每個 Kotlin 後端都要手寫,接入時沒人知道要寫)。代價:Android 與 Spring 外掛同模組的怪專案判成 Android(照舊拿 Android 題);多模組專案靠「最近的建置檔」,子模組沒有自己的建置檔時吃到根的宣告;多讀建置檔,有上限與快取
    decided: 2026-10-15
    valid: true
---
# 前端框架從 vue 分出_計劃

> 白話:工具現在把所有前端框架都當成 vue 來審,React 專案改一支 `.tsx` 會被問「有沒有整包 ref()」這種問錯方向的題、拿到 vue 的慣例手冊。2026-10-15 第一個 React 專案(order-web)接進來,這篇從「等有專案再做」改成開工:讓 React 有自己的題組與慣例手冊,順手補 init 對 Vite 專案猜錯測試指令、不認得 eslint 設定、前端沒有目標架構範本,以及 Kotlin 後端被問 Android 題這幾個同一次示範撞到的缺口。

PRIOR-ART: 最小解在既有機制層——判前後端本來就靠「往上找最近的 package.json」(`_node_flavor`,[[Projects/iOS與Node後端補棧_計劃]] 的設計),這裡只把它回傳的前端值從一種拆成 vue/react 兩種;題組、慣例 skill、目標架構範本、init 骨架、doctor 的 [F] 段全部是既有形狀加條目,照 [[Systems/補新語言SOP]] 八格走,零新機制、零新依賴。世界解:React 官方的 eslint-plugin-react-hooks(`rules-of-hooks`、`exhaustive-deps`,order-web 裝的 5.2.0 實際列出這兩條)管依賴陣列,eslint-plugin-react 的 `jsx-key`/`no-array-index-key` 管清單 key;題組只問 linter 抓不到的那一半(亂序、清理、重繪範圍、StrictMode 重跑)。Vitest 是 Vite 團隊維護、Vite 專案慣用的測試工具(order-web 的 package.json 就是 `vitest run`);eslint 9 起預設讀 flat config(`eslint.config.*`)——佐證:order-web 裝的 eslint 9.39.5 原始碼 `lib/eslint/eslint.js` 的判定函式回 `process.env.ESLINT_USE_FLAT_CONFIG !== "false"`,即沒設環境變數就走 flat config;舊 `.eslintrc*` 要設 `ESLINT_USE_FLAT_CONFIG=false` 才讀,仍有專案在用。Kotlin 分 Android/伺服端借 Gradle 外掛宣告(`com.android.*` vs `org.springframework.boot`),跟 package.json 看依賴同一個思路。

RETIRE-IF: 2027-04-15 人裁時,若 order-web 之外沒有任何 React 專案接 lumos,而且 order-web 帳上的表態裡 react 八題由人作答的(不含自動判 na)全部是 `na`——跟 `lumos stats` 列死題候選同一個口徑——就把 react 題組併回 vue(撤 `_node_flavor_of` 的 react 分支)、react-idioms 標 superseded;撤的時候在途分支要照〈回退〉重表態;前端目標架構範本照 [[Projects/DDD目標架構範本_計劃]] 的撤除條件另算 [retire:人裁] [until:2027-04-15]。

## 現況(2026-10-15 改動前讀程式確認;改完之後的樣子見〈實作紀錄〉與各家節點)

下文小節標題的代號(F1、F2、W2、W7、F7、B10)是 2026-10-15 Web 示範缺口逐條比對時的編號,在本篇只當各節的簡稱;那份比對表是對話裡的工作稿、不在圖譜裡,所以每一節第一句都直接寫出現象。

- **判棧**:`.ts/.tsx/.js/.jsx` 走 `_stack_key_for_file` → `_node_flavor` → `_node_flavor_of`,依賴裡有 `_NODE_FRONTEND_MARKERS`(vue、nuxt、react、next、svelte、@angular/core、solid-js、preact)任一個就回 `vue`。實測:含 react 依賴的 package.json 底下 `src/App.tsx` 判成 `vue`,慣例 skill 判成 `vue-idioms`(`_idiom_skill_for`)。審查角色那邊 `.tsx/.jsx` 本來就在 `_ROLE_FRONT_EXTS` 判前端,`.ts` 靠題組鍵是 `vue` 才判前端。
- **init 骨架**:`_init_config_skeleton` 用 `_SKELETON_RUN_CMD` 查表,`.ts/.tsx` 的測試 profile 是 `node-jest`,run_cmd 一律 `npx jest -t {method}`(`{method}` 是設定檔 run_cmd 的佔位符,合約測試閘跑單支測試時換成那支測試名、經 shell 引號處理);`node-vitest` 只是 `TEST_PROFILES` 裡指向同一份設定的別名,骨架從不寫它。
- **跑過的證據**:`_RAN_EVIDENCE` 收了 swift-xctest、csharp-xunit、node-jest、python 四種;JS 系列只有 `node-jest` 一條(`Tests:.*?[1-9]\d*\s+passed`,jest 29 的摘要有冒號),沒有 `node-vitest`。2026-10-15 在 order-web 實跑 vitest 5.0.4(`NO_COLOR=1 npx vitest run -t <名>`;原始輸出存在 `governance/review-reports/前端框架從vue分出/r1-intake.md` 附錄):跑到 1 支印 `Tests  1 passed | 33 skipped (34)`、對不到印 `Tests  34 skipped (34)`,兩種都回 0、都沒有冒號——**現行樣式對 vitest 永遠證不出跑過**;設定寫 `node-vitest` 時查表連樣式都沒有。這就是 [[Projects/逾期回頭條件立案清單2026-10_計劃]] 第 10 節「vitest 被 node-jest 樣式誤擋」的根因。
- **linter**:doctor [F] 段(`_lint_load_and_validate`)只看 `.lumos/lint.json` 在不在;沒有就印「這個 repo 沒有接 linter」,不管專案根目錄有沒有 `eslint.config.js`。init 完全不看 linter 設定。
- **目標架構範本**:`skills/lumos-project-notes/commands/` 只有 `target-arch-ddd-template.md`。
- **B10 觸發機制(示範當時以為「只看副檔名」,實際不只)**:副檔名決定棧(`.kt` → `kt`),再用三條路決定哪題亮——①改動行比對每題的觸發詞,而且**整組不分大小寫**;②同一棧改動行超過 `ask_all_over_lines`(預設 300)就整組亮(題目表裡標 `shape_only` 的題除外——`shape_only` 是題目的一個旗標,意思是「只在改動行真的寫出那種形狀時才亮,不因行數門檻整組亮、也不進改檔前推播的整組清單」,現在標它的是 Spring 兩題與外部回應碼題);③改檔前推播(impact hook)沒帶改動內容時印整組。實測一段十行的 Spring Service:`val view = repo.findById(...)` 因為不分大小寫撞到 kt-leaks 的 `\bView\b`,Kotlin 的 `init { }` 撞到 kt-startup 的 `\binit\s*\{`;同一段複製到超過 300 行,kt-compose 在內的七題全亮。角色那邊,`.kt` 沒有 android 匯入時刻意判不出([[Projects/代碼審前後端角色鏡頭_計劃]]:「Kotlin 後端與 Android 非畫面檔分不開,寧可不附」)。

## 八格盤點(照 [[Systems/補新語言SOP]] 第 1 步)

| 格子 | 現況 | 要補什麼 |
|---|---|---|
| 程式碼副檔名清單 | `.tsx/.jsx` 已在主程式、post-commit、pre-commit、兩支 hook 的清單裡(`t_code_exts_lists_agree` 釘住) | 不用補 |
| 符號形狀 profile | `typescript` 收 `.ts/.tsx/.mts/.cts/.js/.mjs/.cjs`,**沒收 `.jsx`**;PascalCase 元件名合它的形狀 | `typescript` 的 `code_exts` 加 `.jsx`(純 `.jsx` 專案 init 才猜得出 symbol_profile,不再留空) |
| 測試綁定 profile | `node-jest`(含 `.tsx/.jsx`,`JEST_TEST_RE`,Jest/Vitest 同語法);`node-vitest` 是別名 | 不新開 profile;測試名寫中文句子會懸空由另一份計劃處理,見〈不做〉 |
| 骨架測試指令 | 只有 `npx jest -t {method}` | 見〈做法〉F1:Vite 專案改給 vitest 那條,並補 vitest 的「跑過的證據」 |
| 效能題組 | 沒有 `react` 鍵,React 檔拿 vue 五題 | 見〈做法〉F2/W2:react 八題(六題專屬、並行等待、外部回應碼) |
| 副檔名→慣例 skill | `_idiom_skill_for` 前端一律 vue-idioms | 前端值是 react 時回 react-idioms |
| 慣例 skill 本體 | 沒有 | 新寫 `skills/react-idioms/SKILL.md` |
| 兩份目錄 | [[Systems/效能檢核目錄]] 沒有 React 段;[[Systems/linter精選目錄]] 只有 Vue 與 Node 段 | 各加一段 React(第二個提交,見〈做法〉提交方式) |

## 做法

### F2 + W2:前端值拆成 vue 與 react(一條規則改源頭,下游全部跟著走)

- **改 `_node_flavor_of`**(唯一判定點):依賴裡有 react、next、preact 任一,**而且沒有其他任何前端框架**(vue、nuxt、svelte、@angular/core、solid-js)→ `react`;其他只要有前端框架的,一律 `vue`(照舊——含 vue/nuxt,也含 svelte、Angular、Solid,以及它們跟 react 並存的混合依賴;依使用者 2026-10-15 裁定這三種之後有專案再各自補,混合依賴寧可維持現況也不猜成 react)。`_NODE_FRONTEND_MARKERS` 拆成「react 家族」與「其他前端」兩組常數,docstring 改寫成三種回傳值。收依賴鍵的那幾行(dependencies、devDependencies、peerDependencies 三類)抽成一支共用小函式,F1 的 vitest 判定也呼叫它,不另寫一份只收兩類的。
- **`_stack_key_for_file`**:`_node_flavor` 回 `react` 時回 `react`。順手改正它的 docstring:現在寫「純 .ts 前端檔目前無獨立題組,回 None」,但程式從 2026-09-09 起對前端 `.ts` 回 `vue`,改成照實寫三種回傳值(node/vue/react,找不到或解析不了 package.json 才回 None)。因為 pitfalls --diff、改檔前推播、架構對齊的張力候選三個消費者都走這一支,不必各自改。
- **`_STACK_QUESTION_SPECS` 加 `react` 鍵**(id 照 `^[a-z]+-[a-z0-9]+$`),`_EXTCODE_STACKS` 加 `react`(自動得到 `react-extcode`)。觸發字照 SOP 第 5 步「範式詞+反面詞」。每題有兩欄觸發:`when` 先把改動行裡的字串字面挖空、註解剝掉再比(日誌訊息裡的字不會誤觸);`when_raw` 只剝註解、保留字串內容再比,只放「要看字串才判得出」的樣式(例如 import 的套件名字串)。**下面的觸發字一律是寫進題目表的 regex 原文**:題目表在載入時就編譯,壞 regex 會讓整支工具啟動即錯,所以括號、點都已跳脫;實作照抄、不再改寫:
  - `react-effect`:effect 依賴與清理——依賴陣列有沒有漏讀到的值?計時器、訂閱、監聽有沒有在清理函式收掉?是不是用 effect+setState 同步一個由 props 算得出來的值(該直接算)?`when`:`\buseEffect\b`、`\buseLayoutEffect\b`、`\bsetInterval\(`、`\bsetTimeout\(`、`addEventListener\(`、`\.subscribe\(`、`componentDidMount`、`componentWillUnmount`。
  - `react-race`:回應亂序——同一畫面連發的請求,舊回應晚到會不會蓋掉新的(序號、AbortController 或忽略旗標)?卸載後 await 回來還寫狀態嗎?被新請求取代而中止的那次,算不算失敗?`when`:`\bfetch\(`、`\baxios\b`、`\bawait\b`、`\.then\(`、`AbortController`、`XMLHttpRequest`、`\buseSWR\b`、`\buseQuery\b`。
  - `react-render`:重繪成本——高頻更新的狀態(輪詢、計時、輸入)放在哪一層、會不會整棵樹跟著重畫?Context 的 value 是不是每次重建新物件?昂貴計算有沒有 useMemo,而且只在量級值得時才加?`when`:`\buseState\b`、`\buseReducer\b`、`\buseContext\b`、`\bcreateContext\b`、`\buseMemo\b`、`\buseCallback\b`、`(?-i:\bmemo\()`、`\bforceUpdate\b`。
  - `react-key`:清單 key——key 是不是穩定的業務 id,不是陣列索引或隨機數?會插入、刪除、重排的清單用索引當 key,輸入框狀態會跟錯列。`when`:`\.map\(`、`\bkey=\{\s*(?:i|idx|index)\s*\}`、`\bkey=\{[^}]{0,80}Math\.random\(`(JSX 的 `key={…}` 不是字串字面,放 `when` 就看得到)。
  - `react-strict`:StrictMode——開發模式下 effect 會掛載→清理→再掛載一次:setup 跑兩次會不會重複發請求、重複訂閱、重複送出?state 更新函式與 useState 初始化函式是不是純的(會被呼叫兩次)?用 ref 擋重複的地方,清理時有沒有重設?`when`:`\bStrictMode\b`、`\buseRef\b`、`\buseEffect\b`、`\buseState\(\s*\(\)`。
  - `react-bundle`:新依賴多重?路由層級能不能 `lazy` + `Suspense` 拆塊?有沒有整包匯入圖示庫或工具庫?`when`:`(?-i:\blazy\()`、`\bSuspense\b`、`\bimport\(`;`when_raw`:跟 vue-bundle 同一條(`import\s.*from\s+['\"][^./]`,從套件名而非相對路徑匯入)。
  - `react-parallel`:互不依賴的等待有沒有並行——兩個 await 之間沒有資料依賴時,有沒有用 `Promise.all`(或 `allSettled`)一起等,而不是一個等完才發下一個(延遲相加)?迴圈裡逐筆 await 的,能不能改成一次發出、有界並行?這是 react-idioms ① 那條「⚠ 不可機檢」的頭號條款,照效能檢核目錄「不可機檢條目優先入問」的規矩收(2026-10-15 編排者裁,見決策 d1)。`when` 只收具體寫法、不收裸詞 `await`:`^\s*(?:const|let|var)\s+[\w{}\[\],\s]{1,80}=\s*await\b`(賦值式 await)、`\bfor\b[^\n]{0,120}\bawait\b`(同一行的迴圈裡 await)、`\.forEach\(\s*async\b`、`\bPromise\.(?:all|allSettled)\(`(已經並行的地方也亮,讓作者確認範圍對)。題目表加一個 `"min_lines": 2`:觸發詞要命中至少兩行**增行**才算適用(推送前分級數增行;改檔前推播分不出增刪,數全部)——現行比對是逐行的,看不到「上下兩行」,用「至少兩行賦值式 await」近似「連續兩個以上的 await」;只有這題用,其他題不帶這欄行為不變。行數超過整組門檻時照既有規則整組亮,這欄不影響。
  - 觸發字的大小寫:整組照既有慣例不分大小寫;會撞到一般英文字的(`memo`、`lazy`)用 `(?-i:…)` 局部分大小寫,跟 kt-springdata 已有的寫法同一招。
- **`_idiom_skill_for`**:`.ts/.js` 家族改成拿 `_stack_key_for_file` 的結果去查既有的 `_ARCH_IDIOM_SKILL`(它的鍵本來就是棧鍵),表裡補 `node` → node-idioms、`react` → react-idioms 兩列;結果是 None(找不到或解析不了 package.json)沿用 vue-idioms(現況)。不另立第二張表,既有守衛 `t_python_stack_wiring` 裡「表裡每個 skill 都真的存在」那段就自動涵蓋 react-idioms。
- **審查角色 `_review_role_for`**:題組鍵是 `react` 也判前端(現在只認 `vue`;仿 `_ROLE_BACK_KEYS` 寫成一個前端鍵集合);`_ROLE_FRONT_EXTS` 那行「現在沒有題組鍵的前端檔」的註解改正(`.tsx/.jsx` 之後有題組鍵了,但留在集合裡不影響判定)。這段說明寫進 [[Systems/pitfalls-code-loop]] 的角色鏡頭段。
- **新寫 `skills/react-idioms/SKILL.md`**:版型借 vue-idioms(治的病、分層原則、機檢欄、每條壞例→好例、機檢接線、審查鏡頭、誠實邊界)。只收程式碼層、換一個 React 專案照樣成立的規則,條目從 order-web 的審查報告挑(卷證在 `/Users/enzo/orca/workspaces/order-web/governance/review-reports/` 底下的 `搶購下單畫面/` 與 `code-搶購下單畫面/`),每條寫成現象:①互不依賴的等待要並行(同 vue R1)②回應亂序要有序號或中止,被取代的中止不算失敗(輪詢的舊回應晚到蓋掉較新的庫存;中止舊請求被算成抓取失敗)③卸載後在途結果不得寫狀態或觸發重查(離開畫面後,下單、付款結果回來仍觸發重查)④計時器與輪詢鏈要有唯一擁有者,多個觸發點不得各起一條鏈(前景事件、下單結果、定時各自起計時器,變成多條輪詢鏈)⑤effect 依賴陣列照實寫,`exhaustive-deps` 不准關(機檢)⑥StrictMode 重掛載安全:setup 可重跑、更新函式與初始化函式是純的、用世代號或 ref 擋晚到的舊結果(StrictMode 第一次掛載的請求晚到,把第二次掛載的「在飛」旗標清掉,接著多發一個併行請求)⑦衍生值直接算,不用 effect 同步⑧清單 key 用業務 id(`jsx-key`、`no-array-index-key` 機檢)⑨現在時間與亂數從參數或注入時鐘進來,不在純函式裡直接呼叫 `Date.now()`(分頁回到前景時倒數沒有立刻重讀時間,過期訂單仍顯示可付款)⑩重繪會不會讓鍵盤焦點掉回頁首(按鈕停用加上輪詢重繪,鍵盤焦點跳回頁首)⑪測試照使用者看得到的行為查(Testing Library 依角色與文字),不斷言元件內部狀態。狀態管理選型(Redux/Zustand/Context)、資料抓取庫選型(SWR/React Query)、路由選型不在此裁,寫明「查該專案圖譜」。機檢欄的規則代號在實作時用 order-web 已裝的 eslint 9.39.5 與 eslint-plugin-react-hooks 5.2.0 實跑核對;eslint-plugin-react 那幾條本機沒裝就標「未實跑」。
- **散落清單**(SOP 第 9 步,一處都不漏):①[[Systems/效能檢核目錄]] 的「全表各棧題數」那串、「題目 id 對觸發字」鏡像表加 react 八列 ②[[Systems/棧別提問表態閘]] 的「八棧各多一題、全表 id 集合 N 題」那句 ③[[Systems/補新語言SOP]] 第 5 步的題數參考加 react,第 9 步刪掉已不存在的「兩份 README 支援語言表」那列,第 10 步「兩份目錄不是主程式的家」改正(效能檢核目錄的 about_code 已列 `scripts/lumos`,只剩 linter精選目錄要另提交)④`scripts/test_lumos.py` 的 `t_extcode_single_source` 寫死的八棧 tuple 加 `react`、`t_stack_question_triggers` 的 docstring「前端 .ts 歸 vue」改正 ⑤`skills/lumos-design-loop/templates.md` 兩處 idioms 清單(一般派工那行與資安席那行;資安席那行收 react-idioms 裡 `dangerouslySetInnerHTML` 那條)⑥`ONBOARDING.md` 與 `ARCHITECTURE.md` 的 idioms 清單(ARCHITECTURE 那行現在只列五種,一併補齊到以 `ls skills/` 為準)⑦node-idioms 的 description 那句「前端 TS(Vue)另有 vue-idioms」改成也指 react-idioms。test-profile-multiplatform 的「profile 共幾個」不變(沒有新 profile)。

### F1:init 對 Vite 專案給 vitest 的指令,並讓「跑過的證據」認得 vitest

- **判定**:新增一支小函式「這個 repo 用不用 vitest」,**依賴優先**:根 package.json 的依賴鍵(用 F2 那支共用小函式收三類)有 `vitest` → 是;有 `jest` 沒有 `vitest`(Vite 打包、jest 測試)→ 不是;依賴看不出來時,repo 根有確切副檔名的 `vite.config.*`/`vitest.config.*`(`.ts/.js/.mjs/.cjs/.mts/.cts`,`.bak` 不算)→ 是。只看根目錄,不往下掃(init 本來就只產一份根設定)。
- **`_init_config_skeleton`**:測試 profile 猜到 `node-jest` 而且上面判定為是時,單語言骨架寫 `"test_profile": "node-vitest"`、`run_cmd` 寫 `npx vitest run -t {method}`;多平台骨架的 node 平台同樣換。`_推測` 說明多一句「看到 vite/vitest 設定,所以給 vitest 的指令」。`_SKELETON_RUN_CMD` 加 `node-vitest` 一條,不另造查表以外的分支。沒有 vite/vitest 跡象的照舊給 jest。
- **`_RAN_EVIDENCE`(統一一條樣式,不分兩份)**:`node-jest` 的樣式改成(現行版本,代碼審兩輪改過)`(?:Tests:|行首可帶色碼與空白的 Tests\b)[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed`,原文在 `_RAN_EVIDENCE`——同時吃 jest(`Tests:       1 passed, 1 total`)與 vitest(`      Tests  1 passed | 33 skipped (34)`)。三個要點:①**開頭錨在 `Tests:` 或行首(允許色碼與空白)**,不用多行旗標:兩個讀者(`_ran_evidence_check` 對去色後的整段輸出、`_kill_cap` 對每一行且不去色)都適用;測試標題裡剛好有「Tests 2 passed」的行不算。數字前只要求前一個字不是數字(色碼結尾的 m 緊貼數字時字詞邊界不成立),空白不跨行。②**中段限長 200 字**:現行 jest 樣式中段是不限長的 `.*?`,遇到以 `Tests:` 開頭、後面一長串數字的行會二次方回溯(2026-10-15 實測 Python 3.14:2 萬字 2.7 秒、4 萬字 11 秒;兩個讀者都在單支測試逾時之後跑,推送會卡住);限長後同樣輸入 0.0 秒。③全部 skipped 的那行沒有 passed,照舊判沒跑過。`measured` 欄記 jest 29 與 vitest 5.0.4 兩組實測輸出;`fix_hint` 補一句 vitest 的 `--reporter=dot`/`json` 沒有摘要行、要用預設 reporter;`node-vitest` 指向同一條(跟 `TEST_PROFILES` 的別名一樣)。
- **吸收《逾期回頭條件立案清單2026-10_計劃》第 10 節**(編排者 2026-10-15 定):那一節的最小版本(實跑 vitest、記下跑 1 支與跑 0 支的輸出、補一條樣式)由本計劃做,單元層由 S4–S7 驗。那一節「怎麼算做完」的後半——order-web 下一次推送拿到綠燈——**本計劃做不完**:order-web 現在沒有任何合約行,推送時合約測試閘根本不跑 vitest;它的 `[test:]` 全是中文句子,現行測試名比對只收識別字,綁上去會懸空。中文測試名由另一份計劃 `Projects/測試名收自由字串_計劃`(web-gaps 分支,進行中)處理,所以實地驗收寫成 S30 與下面的回頭條件,第 10 節在那之前不算做完。
- **成本要知道**:合約測試閘每支綁定測試各跑一次 `npx vitest run -t <名>`(去重鍵是根目錄加展開後的指令),預設依序跑;vitest 每次都要啟動並收集全部測試檔(`-t` 只篩測試、不篩檔)。order-web 9 個測試檔單次 760ms;測試檔多、綁定多的專案會等很久,出路是既有的 `bound_tests.parallel` 設定。

### 符號比對 profile 收 `.jsx`

- `SYMBOL_PROFILES["typescript"]` 的 `code_exts` 加 `.jsx`。現在 `.jsx` 沒有任何符號 profile 認領,`_stack_guess` 反查得到空字串,純 `.jsx` 專案 init 產的骨架 symbol_profile 留空、doctor 再唸一次。加了之後反查自然得到 typescript,不用改 `_stack_guess` 本身。驗收是 S28;放在第一個提交(跟程式一起)。

### W7:init 與 doctor 認得 eslint 設定

- **一張偵測表**:新增 `_LINTER_CONFIG_MARKERS`,目前只放 eslint:`eslint.config.{js,mjs,cjs,ts,mts,cts}` 與 `.eslintrc`、`.eslintrc.{js,cjs,json,yml,yaml}`,以及根 package.json 裡值是物件的 `eslintConfig`(代碼審 r1、r2 折入),只看 repo 根。表的每一列附一份「可貼的 lint.json 範本」,eslint 那份照 [[Systems/linter精選目錄]] Node 段既有的 SARIF 寫法(`@microsoft/eslint-formatter-sarif`,`-f @microsoft/sarif -o {LINT_SARIF_OUT} {LINT_FILES}`;兩個佔位符是 lint.json 既有格式:`{LINT_SARIF_OUT}` 由 lumos 換成 SARIF 輸出檔路徑,宣告缺它會被格式檢查唸;`{LINT_FILES}` 由推送前的新增告警閘換成這次改到的檔清單,見 [[Systems/lint-declaration-health]]),鍵列 `ts`、`tsx`、`js`、`jsx`。只命中舊式 `.eslintrc*`、沒有 `eslint.config.*` 時,範本指令前面加 `ESLINT_USE_FLAT_CONFIG=false `(eslint 9 不設這個就不讀舊式設定);兩種都有時列出全部命中的檔名、給新式那份。跟 `_LINT_CONFIG_GLOBS`(新增告警閘搬設定檔進快照用的名單)的關係:用途不同、不合併,但 eslint 那幾個檔名要兩邊都認得——`_LINT_CONFIG_GLOBS` 補 `*.config.mts`、`*.config.cts`,並在兩處註解互指。
- **doctor [F] 段**:`.lumos/lint.json` 不存在時先查偵測表。命中就改印「專案裡有 eslint 設定(`eslint.config.js`),但 lumos 還沒接上它——代碼審看不到它的告警」,下一步印那份範本與「裝 `@microsoft/eslint-formatter-sarif` → 存成 `.lumos/lint.json` → `lumos lint-check --smoke`」;沒命中照舊印「沒有接 linter」那段。仍是提醒、不計 issues,跟現在一樣。
- **init**:跑完設定骨架之後,`.lumos/lint.json` 不存在才查同一張表(已接好的不再催)。命中照 init 既有的輸出慣例印兩行:`  ⚠ 看到 eslint 設定 <檔名>,但 lumos 還沒接上它——代碼審看不到它的告警`,下一行獨立印指令 `lumos doctor`(看 [F] 段的範本)。**不替使用者寫 lint.json**:宣告了跑不動的 linter(formatter 沒裝)會讓 doctor [F] 一直唸、讓推送前的新增告警閘拿到壞宣告,[[Projects/消費專案接入靜默失效_計劃]] 的裁定也是「除了必要的機械擋,其餘只加提醒與骨架」。

### F7:前端分層目標架構範本

- 新增 `skills/lumos-project-notes/commands/target-arch-frontend-template.md`,形狀照 `target-arch-ddd-template.md`:採用步驟(開節點、貼規則、換日期、加 `arch_targets` 宣告)、為什麼是這幾條、可直接存成節點檔的範本區塊、調整與撤除。
- 範本五條 RULE 行,從 order-web 的 `Systems/前端分層目標架構` 一般化(目錄名寫成常見預設 `src/api/`、`src/domain/`,採用步驟註明照專案改):①只有 API 層能呼叫網路與讀寫 HTTP 標頭,元件與 domain 不直接打網路 ②API 層對外回型別化結果(成功/業務錯誤/程式錯誤/結果不確定/呼叫端中止),不把 HTTP 例外或原始 Response 丟給畫面 ③domain 只放純函式與型別,不 import 框架、網路與瀏覽器全域,現在時間與亂數由參數傳入 ④畫面狀態放在用到它的最近共同父元件,用 props 往下傳,要跨三層以上才引入 Context 或全域狀態庫 ⑤測試從使用者看得到的行為驗,網路用替身,不斷言元件內部狀態、不 mock 自己的 domain 函式。每條附「違反長怎樣」,日期用 `<採用日>`、`<回頭日>` 佔位,寫法跟 DDD 範本一樣不綁 React(Vue 專案也能用,元件與 props 的說法照抄成立)。
- `commands/06-代碼審與推送.md` 的 `arch_targets` 那一列、`SKILL.md` 首頁那句「新模組要照 DDD 這類目標架構寫」各補一句指到新範本。

### B10:Kotlin 改動檔只有伺服端寫法時,不列 Android 題

- **一條統一規則**:kt 題組裡 Android 專屬的三題(`kt-compose`、`kt-leaks`、`kt-startup`)在題目表加布林旗標 `"android_only": True`(跟 `shape_only`、`needs_backing` 同形狀)。新增一支共用小函式「某棧的題,扣掉這次不適用平台的題」,所有出題的地方都經過它:`_stack_applicability`(觸發詞與行數門檻兩條路)、pitfalls --diff 的整組清單 `stack_qs`(JSON 的 `stack_questions` 欄與人讀輸出)、改檔前推播印的整組清單、架構對齊的張力候選(`_tension_candidates_into`)。`_STACK_PERF_QUESTIONS` 只存題目原文,這支函式從 `_STACK_QUESTION_SPECS` 按旗標取,不靠原文反查。規則:這次改動的「非測試 `.kt` 檔」(跟 `_by_stack` 同一份清單;測試檔照 `_PITFALL_DIFF_TEST_PAT` 判,`test/`、`tests/` 目錄底下的排除,`androidTest/` 不在其中、照一般檔算)扣掉 diff 標為整檔刪除的之後,**全部**判成伺服端時,這三題一律不列;只要有一支判成 Android 或判不出(含工作樹讀不到但沒被刪、超過讀取上限、超過判定支數上限的檔),就照現況。其他四題(協程、Dispatchers、Flow、集合)兩邊都成立,不動;Spring 兩題本來就只在 Spring 寫法時亮,不動。
- **判伺服端的訊號**(新增一支跟 `_node_flavor` 同形狀的小函式,收 `reader`):①檔案本身有 `import android.` 或 `import androidx.` → Android;②否則從檔案所在目錄往上找最近的 `build.gradle.kts` / `build.gradle` / `pom.xml`:**先剝掉註解**(一條從左到右的掃描,字串原樣留下、字串裡的 `/*` 與 `//` 不算),出現**任何 Android 跡象**(`com.android.`、版本目錄寫法 `libs.plugins.android`、行首的 `android {`)→ Android;沒有 Android 跡象、而且有**伺服端外掛宣告**(`id("org.springframework.boot")`/`apply plugin: 'org.springframework.boot'`、Ktor 伺服端的 `io.ktor.plugin`、Maven 的 `spring-boot-maven-plugin`/`spring-boot-starter-parent`、版本目錄 `libs.plugins.spring.boot`/`springBoot`/`ktor`)→ 伺服端;其他(含只有 `io.ktor` 客戶端依賴、`ktor-server` 或 `org.springframework.boot:…` 依賴座標、Kotlin Multiplatform 模組、找不到建置檔)→ 判不出。只認外掛宣告,不認依賴字串——Android 與 KMP 模組常用 ktor 客戶端,手機端也有本機 ktor 伺服器,KMP 共用模組的 jvm 目標也可能宣告 Spring 依賴。判錯的方向只准是「判不出」(照舊附 Android 題),不准是「把 Android 判成伺服端」。
- **讀法、上限與快取**:①pitfalls 與改檔前推播讀工作樹,角色路讀起點版(照既有「圖譜只信起點」);兩條路共用同一支判定,差別只在傳進來的 `reader`。②角色路要讀的建置檔候選加進 `_review_role_wanted` 的批次讀取清單(跟 `.ts/.js` 的 package.json 候選同一個做法),受既有的 `_ROLE_READ_CAP`(數檔不數候選)、`_ROLE_MAX_BYTES`、時間預算管;讀不到就判不出。③`.kt` 檔頭只讀前 64KB 找匯入;建置檔超過 `_ROLE_MAX_BYTES` 不讀(判不出)。④工作樹讀檔走共用的 `_worktree_text`(快取 `_WORKTREE_TEXT_CACHE`,package.json 也用它);一份建置檔的判定以文字記憶在 `_KT_BUILD_VERDICT_CACHE`(最多 64 份),角色路每支 `.kt` 不重掃。角色路的批次讀取對超過單檔或整批上限的建置檔回「在但讀不了」,停在那一層判不出,不往上找。⑤pitfalls 那條路一次最多判 300 支 `.kt`(同 `_ROLE_READ_CAP`),超過的算判不出——Android 題照舊附,只會多問不會少問。
- **接線**:`_stack_applicability` 多收一個「要排除的題號集合」參數(預設空,既有呼叫照舊),集合由上面那支共用小函式算出,pitfalls --diff 與改檔前推播都傳同一份;整組清單由 `_stack_whole_group` 同一處派生;張力候選改收「這次適用的題號」,只出適用題(min_lines 與平台排除都算進去)。這次刪掉的 `.kt` 不算進「全部判伺服端」。表態閘讀的是 `stack_questions_meta`,跟著少這三題,不用另外改。
- **角色**:同一支判定回伺服端時,`_review_role_for` 對 `.kt` 判後端(現在判不出)。這翻掉 [[Projects/代碼審前後端角色鏡頭_計劃]]〈已知限制〉裡「Kotlin 後端與 Android 非畫面檔分不開,寧可不附」的設計取捨(那是設計取捨、不是使用者裁定),理由與被否決的選項記在決策 d2;那篇的兩處原文(判定規則 (c) 那條、〈已知限制〉那條)已各補一句指到本篇 d2。判不出的情況照舊不附。`.java` 維持現行「沒有 android 匯入就判後端」、不改看建置檔:Java 後端服務的檔幾乎都有框架匯入或沒有 Android 匯入,現行判法在 Java 那邊沒有回報誤判;`.kt` 不能照抄,是因為 Kotlin 在 Android 的資料層、ViewModel 大量沒有 android 匯入,照 Java 那樣判會把它們判成後端。兩套判法是刻意的,這段說明寫進 [[Systems/pitfalls-code-loop]]。
- 觸發詞整組不分大小寫讓 `val view` 撞到 `\bView\b` 的問題,在 Android 專案同樣存在,但那邊撞到的通常也真的跟畫面有關;本篇只靠平台判定讓 Spring 專案不再看到,不改觸發詞(見〈不做〉)。

### 跟《前端知識與風險詞_計劃》的交界

`Projects/前端知識與風險詞_計劃`(EnzoHsieh-Android/web-fe-knowledge 分支)也改同一批地方:`_stack_key_for_file`(它要把 `e2e/`、`fixtures/`、`seeds/` 路徑與 `.sh` 判成 infra)、`_review_role_for`、`_arch_alignment_hints`(本篇經 `_idiom_skill_for` 碰到)、`t_stack_question_triggers` 的全表 id 集合、[[Systems/效能檢核目錄]] 的題目 id 對照表、`skills/lumos-design-loop/templates.md` §7.8 的 idioms 清單行。順序規則:**infra 判定排在 react/vue 判定之前**——`_stack_key_for_file` 先看路徑與副檔名是不是 infra,不是才走 package.json 判前端值。`_review_role_for` 那邊照對方計劃的約定保留「infra 回 None」(本篇只把前端鍵擴成 vue 與 react,沒碰 infra)。兩篇誰後合進主線,誰負責接順序並補一支測試斷言「React 專案裡 `e2e/` 底下的 `.ts` 回 infra、`src/` 底下的 `.tsx` 回 react」(`t_infra_before_react_stack_key`),全表 id 集合與對照表把兩邊的新 id 都收進去。

### 提交方式(SOP 第 10 步)

一個功能一個提交,每個提交帶自己那份程式、測試、家節點說明與本篇(`scripts/lumos` 的家照改到的那段寫):①React 補棧(F2/W2 判棧、題組、慣例 skill、角色鍵、散落清單、[[Systems/效能檢核目錄]] 的 React 段與題數串——它的 about_code 已列 `scripts/lumos`,可跟程式同提交;家節點 [[Systems/棧別提問表態閘]]、[[Systems/pitfalls-code-loop]]、[[Systems/arch-alignment-lens]])②vitest 骨架與跑過證據,含符號 profile 收 `.jsx`([[Systems/lumos-cli-lifecycle]]、[[Systems/bound-tests-gate]]、[[Systems/test-profile-multiplatform]])③eslint 偵測([[Systems/lint-declaration-health]]、[[Systems/lumos-cli-lifecycle]])④前端目標架構範本([[Systems/arch-alignment-lens]])⑤B10 Kotlin 平台判定([[Systems/棧別提問表態閘]]、[[Systems/pitfalls-code-loop]],並改正 [[Systems/補新語言SOP]])⑥只有 [[Systems/linter精選目錄]] 的 React 段(它不是主程式的家,跟程式同提交會被「每支檔有家」擋)。驗證紀錄 `Verification/<日期>_React補棧合成樣本測試` 照 SOP 第 7、8 步寫翻紅表,跟①同提交。

## 驗收條款

- [S1] 當 init 在根目錄有 vite.config.ts、依賴看不出測試工具的 TypeScript 專案產設定骨架時,測試 profile 應寫 node-vitest,run_cmd 應是 `npx vitest run -t {method}`。 [test: t_init_skeleton_vitest_from_vite_config]
- [S2] 當 init 在沒有 vite 設定、但根 package.json 的 devDependencies 有 vitest 的專案產骨架時,run_cmd 應是 vitest 那條。 [test: t_init_skeleton_vitest_from_package_dep]
- [S3] 當 init 在沒有任何 vite 或 vitest 跡象的 TypeScript 專案產骨架時,應照舊寫 node-jest 與 `npx jest -t {method}`。 [test: t_init_skeleton_jest_default_kept]
- [S4] 當跑過證據比對 vitest 跑到 1 支的摘要(`Tests  1 passed | 33 skipped (34)`)時,應判為跑過。 [test: t_ran_evidence_vitest_one_passed]
- [S5] 當跑過證據比對 vitest 全部被跳過的摘要(`Tests  34 skipped (34)`)時,應判為沒跑過。 [test: t_ran_evidence_vitest_all_skipped]
- [S6] 當設定的 profile 寫 node-jest、實際輸出是 vitest 摘要時,跑過證據應同樣判為跑過。 [test: t_ran_evidence_node_jest_accepts_vitest]
- [S7] 當跑過證據比對 jest 29 的摘要(`Tests:       1 passed, 1 total`)時,應照舊判為跑過。 [test: t_ran_evidence_jest_summary_kept]
- [S8] 當 doctor 在根目錄有 eslint.config.js、沒有 .lumos/lint.json 的 repo 跑時,[F] 段應寫出偵測到的設定檔名與可貼的 lint.json 範本,不應再說沒有接 linter。 [test: t_doctor_lint_detects_eslint_flat_config]
- [S9] 當 doctor 在根目錄只有 .eslintrc.json 的 repo 跑時,[F] 段應同樣認得它。 [test: t_doctor_lint_detects_eslintrc]
- [S10] 當 doctor 在根目錄沒有任何 eslint 設定檔、也沒有 lint.json 的 repo 跑時,[F] 段應照舊說沒有接 linter。 [test: t_doctor_lint_no_config_message_kept]
- [S11] 當 init 在根目錄有 eslint 設定檔的專案跑時,應印一行指出偵測到的 eslint 設定,而且不應建立 .lumos/lint.json。 [test: t_init_mentions_eslint_without_writing_lint_json]
- [S12] 當 .tsx 檔最近的 package.json 依賴有 react、沒有 vue 時,判棧應回 react。 [test: t_react_stack_key_from_package_json]
- [S13] 當 package.json 依賴有 vue 或 nuxt 時,判棧應照舊回 vue。 [test: t_vue_stack_key_kept]
- [S14] 當 package.json 依賴只有 svelte、@angular/core 或 solid-js 時,判棧應照舊回 vue。 [test: t_other_frontend_frameworks_stay_vue]
- [S15] 當 pitfalls --diff 改到 React 專案的非測試 .tsx 檔時,棧別題應列 react 題組、不應列任何 vue- 開頭的題。 [test: t_react_stack_wiring]
- [S16] 當架構對齊鏡頭替 React 專案的 .ts 或 .tsx 檔挑慣例 skill 時,應回 react-idioms,而且 skills/react-idioms/SKILL.md 應存在。 [test: t_react_idiom_skill_mapping]
- [S17] 當題目觸發樣本逐題比對時,react 八題的命中樣本應各自亮、不命中樣本應不亮,全表 id 集合應含這八個 id。 [test: t_stack_question_triggers]
- [S18] 當審查角色判 React 專案的 .ts 檔時,應判前端。 [test: t_review_role_react_ts_frontend]
- [S19] 當改檔前推播替 React 專案的 .tsx 檔附棧別題時,應附 react 題組。 [test: t_impact_stack_questions_react]
- [S20] 當前端範本區塊的日期佔位換成實際日期存成節點時,lumos lint 應回報 0 問題,目標架構規則讀法應讀到五條有效 RULE 行。 [test: t_arch_target_frontend_template_valid]
- [S21] 當使用說明 06 的 arch_targets 那一列被讀時,應同時提到 DDD 與前端兩份範本的檔名。 [test: t_arch_target_frontend_template_linked_from_usage]
- [S22] 當改動的 .kt 檔全部判成伺服端、改動行撞到 kt-leaks 或 kt-startup 的觸發詞時,這兩題應不列。 [test: t_kt_spring_android_questions_gone_on_triggers]
- [S23] 當改動的 .kt 檔全部判成伺服端、改動行超過整組門檻時,kt-compose、kt-leaks、kt-startup 應不列,協程、Dispatchers、Flow、集合四題應照舊整組列出,shape_only 的三題應照舊不因門檻而亮。 [test: t_kt_spring_drops_android_questions_over_threshold]
- [S24] 當同一次改動同時有 Android 與伺服端的 .kt 檔時,Android 三題應照現況依觸發詞判。 [test: t_kt_mixed_keeps_android_questions]
- [S25] 當 .kt 檔往上找不到建置檔、或建置檔沒有 Android 跡象也沒有伺服端外掛時,題目應跟現況一樣。 [test: t_kt_unknown_flavor_unchanged]
- [S26] 當派工路徑的審查角色判伺服端那種 .kt 檔時(建置檔經批次讀取從起點版讀到),應判後端。 [test: t_review_role_kt_spring_backend]
- [S27] 當改檔前推播替伺服端 .kt 檔印整組題時,應不含 Android 三題。 [test: t_impact_stack_questions_kt_spring]
- [S28] 當 init 在只有 .jsx 檔的專案產骨架時,symbol_profile 應猜成 typescript。 [test: t_init_skeleton_jsx_symbol_profile]
- [S29] 當 react-idioms 機檢欄寫到 eslint 規則代號時,每個代號應在固定名單內(`react-hooks/rules-of-hooks`、`react-hooks/exhaustive-deps` 標已實跑;`react/jsx-key`、`react/no-array-index-key` 標未實跑),名單外的代號應讓測試紅。 [test: t_react_idioms_rule_names_known]
- [S30] 當 order-web 綁上第一條合約、測試名能被綁定比對收下後推送一次時,合約測試閘應以 vitest 實跑那支並拿到綠燈。 [manual: 在 order-web 加一條綁 vitest 測試的合約行推送一次,把 push 輸出存進驗證紀錄;在 `Projects/測試名收自由字串_計劃` 做完之前驗不了]
- [S31] 當建置檔用版本目錄寫 `alias(libs.plugins.android.application)`、依賴有 `io.ktor:ktor-client-android`、改動的 .kt 檔沒有 android 匯入時,應判 Android,三題應照舊依觸發詞判。 [test: t_kt_android_alias_with_ktor_client_stays_android]
- [S32] 當 pitfalls --diff 只改伺服端 .kt 檔時,輸出的 stack_questions 整組欄位應不含 Android 三題。 [test: t_pitfalls_stack_questions_kt_spring]
- [S33] 當架構對齊的張力候選處理伺服端 .kt 檔時,應不產生 Android 三題的候選。 [test: t_tension_candidates_skip_android_only]
- [S34] 當一次改動有超過 300 支 .kt 檔時,平台判定應在上限處收手,超出的檔應算判不出,Android 三題應照舊列出。 [test: t_kt_flavor_cap_keeps_android_questions]
- [S35] 當跑過證據比對一行以 `Tests:` 開頭、後面接 4 萬個數字的輸出時,應在 1 秒內回答沒跑過。 [test: t_ran_evidence_long_line_fast]
- [S36] 當 doctor 在根目錄只有 .eslintrc.json 的 repo 印 lint.json 範本時,範本指令應帶 `ESLINT_USE_FLAT_CONFIG=false`。 [test: t_doctor_lint_eslintrc_template_legacy_flag]
- [S37] 當 init 在已有 .lumos/lint.json、根目錄也有 eslint 設定的專案跑時,應不印 eslint 提醒。 [test: t_init_eslint_hint_skipped_when_declared]
- [S38] 當 package.json 依賴同時有 react 與 svelte(或 @angular/core、solid-js)時,判棧應照舊回 vue。 [test: t_mixed_react_other_framework_stays_vue]
- [S39] 當表態閘發現帳上舊表態的題號有一部分已不在現行題表(例如 vue- 開頭的題換成 react- 開頭)時,擋下訊息應多一行說明題組已換、舊題號不帶過,並指到 `--dispositions-template`。 [test: t_dispositions_hint_when_stack_switched]
- [S40] 當 React 專案的改動裡有兩行以上 `const x = await …` 這類賦值式 await 時,react-parallel 應亮。 [test: t_react_parallel_two_awaits_trigger]
- [S41] 當 React 專案的改動裡只有一行賦值式 await、其他行沒有 react-parallel 的觸發詞時,react-parallel 應不亮。 [test: t_react_parallel_single_await_quiet]
- [S42] 當題目沒有 min_lines 欄時,觸發判定應跟現況一樣只要一行命中就亮。 [test: t_stack_min_lines_default_unchanged]
- [S43] 當改動檔是 `*.test.*` 或 `__tests__/` 底下的 JS/TS 檔時,應被當成測試檔而不附棧別題;`latest`、`contest`、`attest` 這類名字剛好含 test 字樣的產品檔應照舊掃。 [test: t_pitfalls_test_pat_js_conventions]

## 實務隱患

- 效能:判伺服端的讀檔有上限(檔頭 64KB、建置檔照 `_ROLE_MAX_BYTES`、一次最多判 300 支、角色路受批次讀取與時間預算管),建置檔文字依讀取來源快取;超過上限一律判不出,方向是多問不是少問(S34)。跑過證據樣式中段限長,順手消掉現行 jest 樣式的二次方回溯(S35)。vitest 每支綁定測試各起一次,見〈做法〉F1 的成本那條。eslint 偵測只看根目錄幾個固定檔名,不掃樹。
- 併發:只讀檔與產骨架,單人依序操作,沒有共用狀態要鎖。
- 守衛面:會碰。①「跑過的證據」樣式放寬是合約測試閘的判準——放太寬會把沒跑的當跑過(假綠),所以 S5 釘「全部 skipped 判沒跑過」、S7 釘 jest 原樣式不退化;②B10 讓表態閘少問三題,判錯平台會讓 Android 專案漏問——Android 跡象優先、只認伺服端外掛、判不出一律照舊,S24、S25、S31、S34 釘住;③react 題組上線後,React 專案推送前要表態的題換一批,在途分支要重新表態(SOP 第 2 步記過的代價),order-web 與它的實作複本是唯一受影響的專案,S39 讓擋下訊息講明是題組換了、不是帳壞了。
- 相容:既有 Vue 專案、Node 後端、svelte/angular 專案的判棧結果不變(S13、S14);設定寫 node-jest 的既有 Node 專案跑過證據照舊(S7)。
- 已排除:金流:只改判棧、題目、骨架與說明文件,不碰任何金流資料。
- 已排除:對外送出:init 與 doctor 只印提醒、寫本機設定骨架,不對外寄送任何東西。
- 已排除:不可逆:全部是程式與文件改動,git revert 即可回退;init 不覆寫既有設定、也不寫 lint.json。

## 不做

- Svelte、Angular、Solid 的題組與慣例(使用者 2026-10-15 裁:之後有專案再各自補,照補新語言SOP 開案)。
- Next.js 伺服端渲染、React Server Components 專題(水合差異已有代碼審角色卡 fe-hydration)。
- init 自動寫 `.lumos/lint.json`(理由見〈做法〉W7)。偵測表也先不收 eslint 以外的 linter(biome、ruff、detekt、swiftlint),之後有專案撞到再加列。
- 測試名寫中文句子會懸空:`Projects/測試名收自由字串_計劃`(web-gaps 分支)在做;第 10 節的實地驗收等它,見 S30 與摘要的回頭條件。需求風險面的前端面、設計審派工範本的前端改述、前端測試品質指引:`Projects/前端知識與風險詞_計劃`(EnzoHsieh-Android/web-fe-knowledge 分支)在做。
- 改 kt 觸發詞的大小寫規則(`val view` 撞 `\bView\b`):Android 專案那邊沒有回報,改了要重驗全表樣本;Spring 專案靠平台判定已不受影響。
- Java 檔改看建置檔:理由見〈做法〉B10 角色那條。

## 回退

程式改動 git revert 那個提交即可:`_node_flavor_of` 回到只回 vue/node,react 題組與 `react-extcode` 一起消失,表態閘的全表 id 集合跟著回去(`t_stack_question_triggers` 同一個提交改回);B10 拿掉 `android_only` 旗標、共用過濾函式與排除參數,行為回到現況;init 骨架回到只給 jest;跑過證據樣式回到 jest 那條。`skills/react-idioms/` 與前端範本檔刪掉,06 那一列與 SKILL.md 首頁的指路句刪掉,templates.md 與 ONBOARDING 的清單刪掉 react-idioms。兩份目錄筆記的 React 段是第二個提交,單獨 revert。已經用了 vitest 骨架的消費專案設定不會被改回,它的 `node-vitest` 仍是合法 profile 名。不碰任何帳本。

退回時要知道的三件事:①上線後重新表態過的在途分支,帳上是 react- 開頭的題號;退回後舊工具只認 vue- 題,`--carry` 只帶題號相同的,所以要照 `lumos pitfalls --dispositions-template` 再答一次(撤 RETIRE-IF 時同理)。帳本身不改、舊工具讀得懂,只是要重答。②退回後 `_RAN_EVIDENCE` 沒有 vitest 能對上的樣式:設定寫 `node-vitest` 的專案改走「拿假名字跑一次」的探針,vitest 對不存在的名字也回 0,探針判不可信、快取 14 天,合約測試閘每次推送都擋;寫 `node-jest` 的回到冒號樣式對不上 vitest 的老問題。所以要嘛一起退回 vitest 骨架的消費專案設定,要嘛暫時關掉該專案的綁定測試閘。③其他(react-idioms、範本、目錄段)刪檔即可。

## 合約候選

(無)

## 實作紀錄(2026-10-15)

- 六塊照〈提交方式〉各自一個提交:React 補棧、vitest 骨架與跑過證據(含 `.jsx`)、eslint 偵測、前端目標架構範本、Kotlin 平台判定、linter 精選目錄的 React 段;補新語言 SOP 的改正另一個文件提交(它不是主程式的家,跟程式同提交會被擋)。
- S39(題組換過的擋下提示)多一個提交。條款 S1–S29、S31–S43 都綁了真測試,每一塊都做過翻紅驗證,見 [[Verification/2026-10-15_React補棧合成樣本測試]] 與各家節點。
- S30 還沒做完:在 order-web 的複本上用英文名的探針測試實地跑過合約測試閘——改動前的工具擋下、改動後放行、探針改 skip 照樣擋,見 [[Verification/2026-10-15_order-web實地跑vitest合約測試]];用 order-web 自己的中文測試名推送,要等測試名能收中文句子(回頭條件在摘要的 REVISIT)。
- 跟計劃不一樣的地方:①(已不成立)一度是「批次讀取分不出超限與不存在,太大的建置檔會往上一層找」;代碼審 r2 改成超限的建置檔停在那一層判不出,r3 再限縮成只對建置檔與 package.json 這樣做(被審的原始檔沒讀照舊判不出),現在跟計劃寫的一致。②`t_stack_guess_derived_from_canonical_tables` 拿 `.jsx` 當「沒人認領」的舉例,`.jsx` 被收進 typescript 後換成 `.vue` 的測試欄。③實作中發現 `_PITFALL_DIFF_TEST_PAT` 不認 `*.test.tsx` 與 `__tests__/`,React 專案的 `App.test.tsx` 會被當產品程式拿題目;編排者 2026-10-15 裁定在本分支一起修(React 專案幾乎都用這兩種寫法),加了條款 S43。④一度把平台題的排除做成出題後再過濾的兩支小函式,代碼審 r1 架構對齊席指出那是第二條過濾通道;已改回照 `shape_only` 的做法,在 `_stack_applicability` 與整組派生(`_stack_whole_group`)裡消化,張力候選改成只出適用題(順便讓 min_lines 也算進去)。

## 審計修正紀錄

- r1(2026-10-15,六席):38 條,major 6、minor 32/blocking 6;B10 判伺服端的訊號、讀法與過濾範圍收緊成一條統一規則,跑過證據樣式限長消掉二次方回溯,散落清單、提交分法與回退補齊;38 條折入(react 缺並行等待題由編排者裁定加題)、0 條駁回。席報告在 `governance/review-reports/前端框架從vue分出/`。
- r2(2026-10-15,七席):28 條,major 10、minor 18/blocking 數見卷證;剝註解改成認字串的單一掃描、匯入樣式全檔改不吞換行並加守衛、超限建置檔停住、Spring 只認外掛宣告、跑過證據錨定、測試檔判定收窄,文件與 d2 對齊程式;28 條折入、0 條駁回。席報告在 `governance/review-reports/code-前端框架從vue分出/`。
- r3(2026-10-15,七席,上限輪):28 條,major 10、minor 18;剝註解收成測試檔與建置檔共用的 `_strip_c_comments` 並改成不回溯、Spring 樣式去掉相鄰可空白段、原始檔超限維持判不出、跑過證據兩支都錨在行首或工作區前綴之後、原始碼守衛改用 AST、pom 只剝 XML 註解、`test_` 錨定、刪除才略過;28 條折入、0 條駁回,折完不再派席(使用者裁定:跑滿上限折完就合併)。
