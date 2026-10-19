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
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:[2026-09-29 Enzo 裁 [[Projects/代碼審前後端角色鏡頭_計劃]] d3「另外開」]前端依賴裡有 react/next/svelte/@angular/core/solid-js/preact 的檔,現在一律拿 vue 的棧別檢核題與 vue-idioms;要不要各自分出題組與慣例,走補新語言的標準流程另案處理
  REVISIT:2027-01-15 React 部分已開工(2026-10-15 order-web 接入滿足開工條件);到期時回填 order-web 或下一個 React 專案第一輪代碼審的結果:react 題組哪題從沒亮、哪題每次答不適用、react-idioms 漏了哪些坑;Svelte、Angular 仍歸 vue,到期還沒有這兩種專案就維持現狀再延一季
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
decisions:
  - content: React 效能追問題組走 React 專屬題:effect 依賴與清理、回應亂序、重繪成本、清單 key、StrictMode、bundle 六題(另加各棧共有的外部回應碼題);Svelte、Angular 之後有專案再各自補,現在照舊歸 vue
    id: d1
    context: order-web(Vite+React+TS)是第一個 React 消費專案,.tsx 一律被判成 vue,拿到 ref()/v-for/watch 這類問錯方向的題與 vue-idioms;題目 id 被 t_stack_question_triggers 釘住,方向一開始就要選對(補新語言SOP 第 2 步)
    why_chosen: 六題都是 order-web 兩輪設計審與三輪代碼審真的出過、而且換一個 React 專案照樣成立的坑(輪詢亂序蓋掉新資料、卸載後在途結果還寫狀態、StrictMode 重掛載多發請求),問到點上;Svelte/Angular 目前沒有專案,照補新語言SOP 第 0 步不先補。不選:通用網頁前端題(一份題組給所有框架共用,問不到 effect 依賴、key、StrictMode 這些 React 才有的寫法,跟現在的 vue 題組一樣問偏);不選:維持歸 vue(現況,order-web 實測 vue 題對 React 寫法全部問錯方向);不選:React、Svelte、Angular 一次各補一組(後兩者零專案,補出來是零實證文件)。代價:Next.js 伺服端渲染與 Server Components 沒有專題(水合差異交給代碼審角色卡 fe-hydration);Svelte、Angular 專案接進來前仍拿 vue 題組,維持問偏,靠本篇 REVISIT 回頭;題組只從 order-web 一個專案的審查報告取材,第二個 React 專案跑完第一輪代碼審要回填哪題沒亮過
    decided: 2026-10-15
    valid: true
  - content: Kotlin 檔看建置檔的外掛宣告分辨 Android 與伺服端:最近的 build.gradle(.kts)/pom.xml 寫 org.springframework.boot 或 io.ktor、檔內沒有 android/androidx 匯入 → 伺服端,不列 Android 三題、角色判後端;翻掉 Projects/代碼審前後端角色鏡頭_計劃〈已知限制〉裡「.kt 沒有 android 匯入一律判不出」的設計取捨
    id: d2
    context: B10:order-web 示範的 Spring 後端改 .kt 檔被問 Compose、洩漏、冷啟動題,角色判成「後端 0 支、判不出 1 支」。原取捨的理由是只看檔內匯入時 Kotlin 後端與 Android 非畫面檔分不開,寧可不附;那是代碼審角色鏡頭設計時的取捨,不是使用者裁定(編排者 2026-10-15 確認)
    why_chosen: 原理由的前提是「只有檔內匯入可看」;建置檔的外掛宣告是專案層級的硬訊號,Android 專案一定宣告 com.android.application/library,Spring Boot 專案一定宣告 org.springframework.boot,兩者分得開,前提不成立了;判法跟 .ts 看最近 package.json 同一個形狀,不新造機制;判不出(沒有建置檔、兩種都沒寫、檔內有 android 匯入)照舊不附,保守方向不變。不選:維持判不出(Spring 專案永遠拿 Android 題、拿不到後端卡);不選:看檔內 Spring 匯入(領域類、資料類多半沒有 Spring 匯入,大部分檔仍判不出);不選:要專案在 review_roles 自己宣告(既有出路,但每個 Kotlin 後端都要手寫,接入時沒人知道要寫)。代價:同一個 Gradle 模組同時套 Android 與 Spring 外掛的怪專案會判成 Android(照舊拿 Android 題);多模組專案靠「最近的建置檔」,子模組沒有自己的建置檔時會吃到根的宣告
    decided: 2026-10-15
    valid: true
---
# 前端框架從 vue 分出_計劃

> 白話:工具現在把所有前端框架都當成 vue 來審,React 專案改一支 `.tsx` 會被問「有沒有整包 ref()」這種問錯方向的題、拿到 vue 的慣例手冊。2026-10-15 第一個 React 專案(order-web)接進來,這篇從「等有專案再做」改成開工:讓 React 有自己的題組與慣例手冊,順手補 init 對 Vite 專案猜錯測試指令、不認得 eslint 設定、前端沒有目標架構範本,以及 Kotlin 後端被問 Android 題這幾個同一次示範撞到的缺口。

PRIOR-ART: 最小解在既有機制層——判前後端本來就靠「往上找最近的 package.json」(`_node_flavor`,[[Projects/iOS與Node後端補棧_計劃]] 的設計),這裡只把它回傳的前端值從一種拆成 vue/react 兩種;題組、慣例 skill、目標架構範本、init 骨架、doctor 的 [F] 段全部是既有形狀加條目,照 [[Systems/補新語言SOP]] 八格走,零新機制、零新依賴。世界解:React 官方的 eslint-plugin-react-hooks(`rules-of-hooks`、`exhaustive-deps`,order-web 裝的 5.2.0 實際列出這兩條)管依賴陣列,eslint-plugin-react 的 `jsx-key`/`no-array-index-key` 管清單 key;題組只問 linter 抓不到的那一半(亂序、清理、重繪範圍、StrictMode 重跑)。Vitest 是 Vite 團隊維護、Vite 專案慣用的測試工具(order-web 的 package.json 就是 `vitest run`);eslint 9 起預設讀 flat config(`eslint.config.*`)——佐證:order-web 裝的 eslint 9.39.5 原始碼 `lib/eslint/eslint.js` 的判定函式回 `process.env.ESLINT_USE_FLAT_CONFIG !== "false"`,即沒設環境變數就走 flat config;舊 `.eslintrc*` 要設 `ESLINT_USE_FLAT_CONFIG=false` 才讀,仍有專案在用。Kotlin 分 Android/伺服端借 Gradle 外掛宣告(`com.android.*` vs `org.springframework.boot`),跟 package.json 看依賴同一個思路。

RETIRE-IF: 2027-04-15 人裁時,若 order-web 之外沒有任何 React 專案接 lumos,而且 order-web 在帳上的推送裡 react 題組沒有任何一題被答成「適用並改了程式」,就把 react 題組併回 vue(撤 `_node_flavor` 的 react 分支)、react-idioms 標 superseded;前端目標架構範本照 [[Projects/DDD目標架構範本_計劃]] 的撤除條件另算 [retire:人裁] [until:2027-04-15]。

## 現況(2026-10-15 讀程式確認)

- **判棧**:`.ts/.tsx/.js/.jsx` 走 `_stack_key_for_file` → `_node_flavor` → `_node_flavor_of`,依賴裡有 `_NODE_FRONTEND_MARKERS`(vue、nuxt、react、next、svelte、@angular/core、solid-js、preact)任一個就回 `vue`。實測:含 react 依賴的 package.json 底下 `src/App.tsx` 判成 `vue`,慣例 skill 判成 `vue-idioms`(`_idiom_skill_for`)。審查角色那邊 `.tsx/.jsx` 本來就在 `_ROLE_FRONT_EXTS` 判前端,`.ts` 靠題組鍵是 `vue` 才判前端。
- **init 骨架**:`_init_config_skeleton` 用 `_SKELETON_RUN_CMD` 查表,`.ts/.tsx` 的測試 profile 是 `node-jest`,run_cmd 一律 `npx jest -t {method}`(`{method}` 是設定檔 run_cmd 的佔位符,合約測試閘跑單支測試時換成那支測試名、經 shell 引號處理);`node-vitest` 只是 `TEST_PROFILES` 裡指向同一份設定的別名,骨架從不寫它。
- **跑過的證據**:`_RAN_EVIDENCE` 收了 swift-xctest、csharp-xunit、node-jest、python 四種;JS 系列只有 `node-jest` 一條(`Tests:.*?[1-9]\d*\s+passed`,jest 29 的摘要有冒號),沒有 `node-vitest`。2026-10-15 在 order-web 實跑 vitest 5.0.4(`NO_COLOR=1 npx vitest run -t <名>`;原始輸出存在 `governance/review-reports/前端框架從vue分出/r1-intake.md` 附錄):跑到 1 支印 `Tests  1 passed | 33 skipped (34)`、對不到印 `Tests  34 skipped (34)`,兩種都回 0、都沒有冒號——**現行樣式對 vitest 永遠證不出跑過**;設定寫 `node-vitest` 時查表連樣式都沒有。這就是 [[Projects/逾期回頭條件立案清單2026-10_計劃]] 第 10 節「vitest 被 node-jest 樣式誤擋」的根因。
- **linter**:doctor [F] 段(`_lint_load_and_validate`)只看 `.lumos/lint.json` 在不在;沒有就印「這個 repo 沒有接 linter」,不管專案根目錄有沒有 `eslint.config.js`。init 完全不看 linter 設定。
- **目標架構範本**:`skills/lumos-project-notes/commands/` 只有 `target-arch-ddd-template.md`。
- **B10 觸發機制(比對表寫「只看副檔名」,實際不只)**:副檔名決定棧(`.kt` → `kt`),再用三條路決定哪題亮——①改動行比對每題的觸發詞,而且**整組不分大小寫**;②同一棧改動行超過 `ask_all_over_lines`(預設 300)就整組亮(題目表裡標 `shape_only` 的題除外——`shape_only` 是題目的一個旗標,意思是「只在改動行真的寫出那種形狀時才亮,不因行數門檻整組亮、也不進改檔前推播的整組清單」,現在標它的是 Spring 兩題與外部回應碼題);③改檔前推播(impact hook)沒帶改動內容時印整組。實測一段十行的 Spring Service:`val view = repo.findById(...)` 因為不分大小寫撞到 kt-leaks 的 `\bView\b`,Kotlin 的 `init { }` 撞到 kt-startup 的 `\binit\s*\{`;同一段複製到超過 300 行,kt-compose 在內的七題全亮。角色那邊,`.kt` 沒有 android 匯入時刻意判不出([[Projects/代碼審前後端角色鏡頭_計劃]]:「Kotlin 後端與 Android 非畫面檔分不開,寧可不附」)。

## 八格盤點(照 [[Systems/補新語言SOP]] 第 1 步)

| 格子 | 現況 | 要補什麼 |
|---|---|---|
| 程式碼副檔名清單 | `.tsx/.jsx` 已在主程式、post-commit、pre-commit、兩支 hook 的清單裡(`t_code_exts_lists_agree` 釘住) | 不用補 |
| 符號形狀 profile | `typescript` 收 `.ts/.tsx/.mts/.cts/.js/.mjs/.cjs`,**沒收 `.jsx`**;PascalCase 元件名合它的形狀 | `typescript` 的 `code_exts` 加 `.jsx`(純 `.jsx` 專案 init 才猜得出 symbol_profile,不再留空) |
| 測試綁定 profile | `node-jest`(含 `.tsx/.jsx`,`JEST_TEST_RE`,Jest/Vitest 同語法);`node-vitest` 是別名 | 不新開 profile;測試名寫中文句子會懸空是比對表 W1,不在本篇 |
| 骨架測試指令 | 只有 `npx jest -t {method}` | 見〈做法〉F1:Vite 專案改給 vitest 那條,並補 vitest 的「跑過的證據」 |
| 效能題組 | 沒有 `react` 鍵,React 檔拿 vue 五題 | 見〈做法〉F2/W2:react 七題(六題專屬+外部回應碼) |
| 副檔名→慣例 skill | `_idiom_skill_for` 前端一律 vue-idioms | 前端值是 react 時回 react-idioms |
| 慣例 skill 本體 | 沒有 | 新寫 `skills/react-idioms/SKILL.md` |
| 兩份目錄 | [[Systems/效能檢核目錄]] 沒有 React 段;[[Systems/linter精選目錄]] 只有 Vue 與 Node 段 | 各加一段 React(第二個提交,見〈做法〉提交方式) |

## 做法

### F2 + W2:前端值拆成 vue 與 react(一條規則改源頭,下游全部跟著走)

- **改 `_node_flavor_of`**(唯一判定點):依賴裡有 vue 或 nuxt → `vue`(照舊);沒有 vue/nuxt、但有 react、next、preact 任一 → `react`;只有 svelte、@angular/core、solid-js → `vue`(照舊,依使用者 2026-10-15 裁定,這三種之後有專案再各自補)。`_NODE_FRONTEND_MARKERS` 拆成兩組常數,docstring 改寫成三種回傳值。
- **`_stack_key_for_file`**:`_node_flavor` 回 `react` 時回 `react`。順手改正它的 docstring:現在寫「純 .ts 前端檔目前無獨立題組,回 None」,但程式從 2026-09-09 起對前端 `.ts` 回 `vue`,改成照實寫三種回傳值(node/vue/react,找不到或解析不了 package.json 才回 None)。因為 pitfalls --diff、改檔前推播、架構對齊的張力候選三個消費者都走這一支,不必各自改。
- **`_STACK_QUESTION_SPECS` 加 `react` 鍵**(id 照 `^[a-z]+-[a-z0-9]+$`),`_EXTCODE_STACKS` 加 `react`(自動得到 `react-extcode`)。觸發字照 SOP 第 5 步「範式詞+反面詞」。每題有兩欄觸發:`when` 先把改動行裡的字串字面挖空、註解剝掉再比(日誌訊息裡的字不會誤觸);`when_raw` 只剝註解、保留字串內容再比,只放「要看字串才判得出」的樣式(例如 JSX 屬性值、import 的套件名字串):
  - `react-effect`:effect 依賴與清理——依賴陣列有沒有漏讀到的值?計時器、訂閱、監聽有沒有在清理函式收掉?是不是用 effect+setState 同步一個由 props 算得出來的值(該直接算)?觸發:`useEffect`、`useLayoutEffect`、`setInterval(`、`setTimeout(`、`addEventListener`、`subscribe(`、`componentDidMount`、`componentWillUnmount`。
  - `react-race`:回應亂序——同一畫面連發的請求,舊回應晚到會不會蓋掉新的(序號、AbortController 或忽略旗標)?卸載後 await 回來還寫狀態嗎?被新請求取代而中止的那次,算不算失敗?觸發:`fetch(`、`axios`、`\bawait\b`、`\.then\(`、`AbortController`、`XMLHttpRequest`、`useSWR`、`useQuery`。
  - `react-render`:重繪成本——高頻更新的狀態(輪詢、計時、輸入)放在哪一層、會不會整棵樹跟著重畫?Context 的 value 是不是每次重建新物件?昂貴計算有沒有 useMemo,而且只在量級值得時才加?觸發:`useState`、`useReducer`、`useContext`、`createContext`、`useMemo`、`useCallback`、`(?-i:\bmemo\()`、`forceUpdate`。
  - `react-key`:清單 key——key 是不是穩定的業務 id,不是陣列索引或隨機數?會插入、刪除、重排的清單用索引當 key,輸入框狀態會跟錯列。觸發:`\.map\(`;`when_raw` 收 `key=\{\s*(?:i|idx|index)\s*\}`、`Math\.random\(\)` 出現在 key 的寫法。
  - `react-strict`:StrictMode——開發模式下 effect 會掛載→清理→再掛載一次:setup 跑兩次會不會重複發請求、重複訂閱、重複送出?state 更新函式與 useState 初始化函式是不是純的(會被呼叫兩次)?用 ref 擋重複的地方,清理時有沒有重設?觸發:`StrictMode`、`useRef`、`useEffect`、`useState\(\s*\(\)`。
  - `react-bundle`:新依賴多重?路由層級能不能 `lazy` + `Suspense` 拆塊?有沒有整包匯入圖示庫或工具庫?觸發:`(?-i:\blazy\()`、`Suspense`、`import\(`;`when_raw` 收從套件名(非相對路徑)匯入的 import 行,同 vue-bundle。
  - 觸發字的大小寫:整組照既有慣例不分大小寫;會撞到一般英文字的(`memo`、`lazy`)用 `(?-i:…)` 局部分大小寫,跟 kt-springdata 已有的寫法同一招。
- **`_idiom_skill_for`**:改成「前端值 → skill」一張小表(node → node-idioms、react → react-idioms、其他或找不到 package.json → vue-idioms,後者是現況),不再用 if/else 夾副檔名表。
- **審查角色 `_review_role_for`**:題組鍵是 `react` 也判前端(現在只認 `vue`);`_ROLE_FRONT_EXTS` 那行「現在沒有題組鍵的前端檔」的註解改正(`.tsx/.jsx` 之後有題組鍵了,但留在集合裡不影響判定)。
- **新寫 `skills/react-idioms/SKILL.md`**:版型借 vue-idioms(治的病、分層原則、機檢欄、每條壞例→好例、機檢接線、審查鏡頭、誠實邊界)。只收程式碼層、換一個 React 專案照樣成立的規則,條目從 order-web 的審查報告挑(卷證在 `/Users/enzo/orca/workspaces/order-web/governance/review-reports/` 底下的 `搶購下單畫面/` 與 `code-搶購下單畫面/`),每條寫成現象:①互不依賴的等待要並行(同 vue R1)②回應亂序要有序號或中止,被取代的中止不算失敗(輪詢的舊回應晚到蓋掉較新的庫存;中止舊請求被算成抓取失敗)③卸載後在途結果不得寫狀態或觸發重查(離開畫面後,下單、付款結果回來仍觸發重查)④計時器與輪詢鏈要有唯一擁有者,多個觸發點不得各起一條鏈(前景事件、下單結果、定時各自起計時器,變成多條輪詢鏈)⑤effect 依賴陣列照實寫,`exhaustive-deps` 不准關(機檢)⑥StrictMode 重掛載安全:setup 可重跑、更新函式與初始化函式是純的、用世代號或 ref 擋晚到的舊結果(StrictMode 第一次掛載的請求晚到,把第二次掛載的「在飛」旗標清掉,接著多發一個併行請求)⑦衍生值直接算,不用 effect 同步⑧清單 key 用業務 id(`jsx-key`、`no-array-index-key` 機檢)⑨現在時間與亂數從參數或注入時鐘進來,不在純函式裡直接呼叫 `Date.now()`(分頁回到前景時倒數沒有立刻重讀時間,過期訂單仍顯示可付款)⑩重繪會不會讓鍵盤焦點掉回頁首(按鈕停用加上輪詢重繪,鍵盤焦點跳回頁首)⑪測試照使用者看得到的行為查(Testing Library 依角色與文字),不斷言元件內部狀態。狀態管理選型(Redux/Zustand/Context)、資料抓取庫選型(SWR/React Query)、路由選型不在此裁,寫明「查該專案圖譜」。機檢欄的規則代號在實作時用 order-web 已裝的 eslint 9.39.5 與 eslint-plugin-react-hooks 5.2.0 實跑核對;eslint-plugin-react 那幾條本機沒裝就標「未實跑」。
- **散落清單**(SOP 第 9 步):`skills/lumos-design-loop/templates.md` 兩處 idioms 清單(一般派工那行與資安席那行;資安席那行 React 寫「無」或收 react-idioms 裡 `dangerouslySetInnerHTML` 那條)、`ONBOARDING.md` 的 idioms 清單、node-idioms 的 description 那句「前端 TS(Vue)另有 vue-idioms」改成也指 react-idioms。README 兩份目前沒有支援語言表(SOP 第 9 步記的那張表已不在),不用改。test-profile-multiplatform 的「profile 共幾個」不變(沒有新 profile)。

### F1:init 對 Vite 專案給 vitest 的指令,並讓「跑過的證據」認得 vitest

- **判定**:新增一支小函式「這個 repo 用不用 vitest」:repo 根有 `vite.config.*`(`.ts/.js/.mjs/.cjs/.mts/.cts`)或 `vitest.config.*`,或根 package.json 的 dependencies/devDependencies 有 `vitest` → 是。只看根目錄,不往下掃(init 本來就只產一份根設定)。
- **`_init_config_skeleton`**:測試 profile 猜到 `node-jest` 而且上面判定為是時,單語言骨架寫 `"test_profile": "node-vitest"`、`run_cmd` 寫 `npx vitest run -t {method}`;多平台骨架的 node 平台同樣換。`_推測` 說明多一句「看到 vite/vitest 設定,所以給 vitest 的指令」。`_SKELETON_RUN_CMD` 加 `node-vitest` 一條,不另造查表以外的分支。沒有 vite/vitest 跡象的照舊給 jest。
- **`_RAN_EVIDENCE`(統一一條樣式,不分兩份)**:`node-jest` 的樣式放寬成同時吃 jest 與 vitest 兩種摘要——「行首(前面可有空白,vitest 的摘要行是縮排的)的 `Tests` 後面可有可無冒號,同一行有 `N passed`(N≥1)」;`measured` 欄記 jest 29 與 vitest 5.0.4 兩組實測輸出;`node-vitest` 指向同一條(跟 `TEST_PROFILES` 的別名一樣)。這樣設定寫 `node-jest` 卻用 vitest 跑的專案(order-web 現在就是)也認得,`Test Files  1 passed` 那行不會被誤當(開頭是 `Test Files` 不是 `Tests`)。全部 skipped 的那行沒有 passed,照舊判沒跑過。
- **吸收《逾期回頭條件立案清單2026-10_計劃》第 10 節**(編排者 2026-10-15 定):那一節「vitest 被 node-jest 樣式誤擋」的最小版本(實跑 vitest、記下跑 1 支與跑 0 支的輸出、補一條樣式)由本計劃做完,怎麼算做完也照那一節:新樣式有測試(S4–S7),order-web 下一次推送拿到綠燈。那一節已補一句指到本篇。

### 符號比對 profile 收 `.jsx`

- `SYMBOL_PROFILES["typescript"]` 的 `code_exts` 加 `.jsx`。現在 `.jsx` 沒有任何符號 profile 認領,`_stack_guess` 反查得到空字串,純 `.jsx` 專案 init 產的骨架 symbol_profile 留空、doctor 再唸一次。加了之後反查自然得到 typescript,不用改 `_stack_guess` 本身。驗收是 S28;放在第一個提交(跟程式一起)。

### W7:init 與 doctor 認得 eslint 設定

- **一張偵測表**:新增 `_LINTER_CONFIG_MARKERS`,目前只放 eslint:`eslint.config.{js,mjs,cjs,ts,mts,cts}` 與 `.eslintrc`、`.eslintrc.{js,cjs,json,yml,yaml}`,只看 repo 根。表的每一列附一份「可貼的 lint.json 範本」,eslint 那份照 [[Systems/linter精選目錄]] Node 段既有的 SARIF 寫法(`@microsoft/eslint-formatter-sarif`,`-f @microsoft/sarif -o {LINT_SARIF_OUT} {LINT_FILES}`;兩個佔位符是 lint.json 既有格式:`{LINT_SARIF_OUT}` 由 lumos 換成 SARIF 輸出檔路徑,宣告缺它會被格式檢查唸;`{LINT_FILES}` 由推送前的新增告警閘換成這次改到的檔清單,見 [[Systems/lint-declaration-health]]),鍵列 `ts`、`tsx`、`js`、`jsx`。
- **doctor [F] 段**:`.lumos/lint.json` 不存在時先查偵測表。命中就改印「專案裡有 eslint 設定(`eslint.config.js`),但 lumos 還沒接上它——代碼審看不到它的告警」,下一步印那份範本與「裝 `@microsoft/eslint-formatter-sarif` → 存成 `.lumos/lint.json` → `lumos lint-check --smoke`」;沒命中照舊印「沒有接 linter」那段。仍是提醒、不計 issues,跟現在一樣。
- **init**:跑完設定骨架之後查同一張表,命中就印一行「看到 eslint 設定 `<檔名>`;要讓代碼審看得到它的告警,照 `lumos doctor` [F] 段印的範本建 `.lumos/lint.json`」。**不替使用者寫 lint.json**:宣告了跑不動的 linter(formatter 沒裝)會讓 doctor [F] 一直唸、讓推送前的新增告警閘拿到壞宣告,[[Projects/消費專案接入靜默失效_計劃]] 的裁定也是「除了必要的機械擋,其餘只加提醒與骨架」。

### F7:前端分層目標架構範本

- 新增 `skills/lumos-project-notes/commands/target-arch-frontend-template.md`,形狀照 `target-arch-ddd-template.md`:採用步驟(開節點、貼規則、換日期、加 `arch_targets` 宣告)、為什麼是這幾條、可直接存成節點檔的範本區塊、調整與撤除。
- 範本五條 RULE 行,從 order-web 的 `Systems/前端分層目標架構` 一般化(目錄名寫成常見預設 `src/api/`、`src/domain/`,採用步驟註明照專案改):①只有 API 層能呼叫網路與讀寫 HTTP 標頭,元件與 domain 不直接打網路 ②API 層對外回型別化結果(成功/業務錯誤/程式錯誤/結果不確定/呼叫端中止),不把 HTTP 例外或原始 Response 丟給畫面 ③domain 只放純函式與型別,不 import 框架、網路與瀏覽器全域,現在時間與亂數由參數傳入 ④畫面狀態放在用到它的最近共同父元件,用 props 往下傳,要跨三層以上才引入 Context 或全域狀態庫 ⑤測試從使用者看得到的行為驗,網路用替身,不斷言元件內部狀態、不 mock 自己的 domain 函式。每條附「違反長怎樣」,日期用 `<採用日>`、`<回頭日>` 佔位,寫法跟 DDD 範本一樣不綁 React(Vue 專案也能用,元件與 props 的說法照抄成立)。
- `commands/06-代碼審與推送.md` 的 `arch_targets` 那一列、`SKILL.md` 首頁那句「新模組要照 DDD 這類目標架構寫」各補一句指到新範本。

### B10:Kotlin 改動檔只有伺服端寫法時,不列 Android 題

- **一條統一規則**:kt 題組裡 Android 專屬的三題(`kt-compose`、`kt-leaks`、`kt-startup`)在題目表加 `"platform": "android"`;這次改動的 `.kt` 檔**全部**判成伺服端時,這三題一律不列——觸發詞命中、行數超過門檻、改檔前推播印整組,三條路都不列。只要有一支 `.kt` 檔判成 Android 或判不出,就照現況。其他四題(協程、Dispatchers、Flow、集合)兩邊都成立,不動;Spring 兩題本來就只在 Spring 寫法時亮,不動。
- **判伺服端的訊號**(新增一支跟 `_node_flavor` 同形狀的小函式,結果快取):①檔案本身有 `import android.` 或 `import androidx.` → Android;②否則從檔案所在目錄往上找最近的 `build.gradle.kts` / `build.gradle` / `pom.xml`:寫了 `com.android.application` 或 `com.android.library` → Android;寫了 `org.springframework.boot` 或 `io.ktor` → 伺服端;都沒有或找不到 → 判不出。只看檔案頭的匯入與建置檔的外掛宣告,不猜程式內容。
- **接線**:`_stack_applicability` 多收一個「要排除的題號集合」參數(預設空,既有呼叫照舊);pitfalls --diff 由改動檔的判定結果算出集合傳進去;改檔前推播那條路(只有一支檔)用同一支判定,整組清單(`_STACK_PERF_QUESTIONS` 派生值)在輸出前濾掉同一批題。表態閘讀的題表跟著少這三題,不用另外改。
- **角色**:同一支判定回伺服端時,`_review_role_for` 對 `.kt` 判後端(現在判不出)。這翻掉 [[Projects/代碼審前後端角色鏡頭_計劃]]〈已知限制〉裡「Kotlin 後端與 Android 非畫面檔分不開,寧可不附」的設計取捨(那是設計取捨、不是使用者裁定),理由與被否決的選項記在決策 d2;判不出的情況(沒有建置檔、兩種都沒寫)照舊不附。
- 觸發詞整組不分大小寫讓 `val view` 撞到 `\bView\b` 的問題,在 Android 專案同樣存在,但那邊撞到的通常也真的跟畫面有關;本篇只靠平台判定讓 Spring 專案不再看到,不改觸發詞(見〈不做〉)。

### 提交方式(SOP 第 10 步)

實作分兩個提交:①程式(含符號 profile 收 `.jsx`)+家節點([[Systems/棧別提問表態閘]]、[[Systems/test-profile-multiplatform]]、[[Systems/bound-tests-gate]]、[[Systems/lint-declaration-health]]、[[Systems/lumos-cli-lifecycle]]、[[Systems/arch-alignment-lens]] 各寫自己那段)+本篇+驗證紀錄+react-idioms+範本與使用說明;②只有兩份目錄筆記([[Systems/效能檢核目錄]]、[[Systems/linter精選目錄]] 的 React 段)。驗證紀錄 `Verification/<日期>_React補棧合成樣本測試` 照 SOP 第 7、8 步寫翻紅表。

## 驗收條款

- [S1] 當 init 在根目錄有 vite.config.ts 的 TypeScript 專案產設定骨架時,測試 profile 應寫 node-vitest,run_cmd 應是 `npx vitest run -t {method}`。 [test: t_init_skeleton_vitest_from_vite_config]
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
- [S17] 當題目觸發樣本逐題比對時,react 七題的命中樣本應各自亮、不命中樣本應不亮,全表 id 集合應含這七個 id。 [test: t_stack_question_triggers]
- [S18] 當審查角色判 React 專案的 .ts 檔時,應判前端。 [test: t_review_role_react_ts_frontend]
- [S19] 當改檔前推播替 React 專案的 .tsx 檔附棧別題時,應附 react 題組。 [test: t_impact_stack_questions_react]
- [S20] 當前端範本區塊的日期佔位換成實際日期存成節點時,lumos lint 應回報 0 問題,目標架構規則讀法應讀到五條有效 RULE 行。 [test: t_arch_target_frontend_template_valid]
- [S21] 當使用說明 06 的 arch_targets 那一列被讀時,應同時提到 DDD 與前端兩份範本的檔名。 [test: t_arch_target_frontend_template_linked_from_usage]
- [S22] 當改動的 .kt 檔全部判成伺服端、改動行撞到 kt-leaks 或 kt-startup 的觸發詞時,這兩題應不列。 [test: t_kt_spring_drops_android_questions]
- [S23] 當改動的 .kt 檔全部判成伺服端、改動行超過整組門檻時,kt-compose、kt-leaks、kt-startup 應不列,其他 kt 題應照舊整組列出。 [test: t_kt_spring_drops_android_questions_over_threshold]
- [S24] 當同一次改動同時有 Android 與伺服端的 .kt 檔時,Android 三題應照現況依觸發詞判。 [test: t_kt_mixed_keeps_android_questions]
- [S25] 當 .kt 檔往上找不到建置檔、或建置檔沒寫 Android 也沒寫 Spring/Ktor 外掛時,題目應跟現況一樣。 [test: t_kt_unknown_flavor_unchanged]
- [S26] 當審查角色判伺服端那種 .kt 檔時,應判後端。 [test: t_review_role_kt_spring_backend]
- [S27] 當改檔前推播替伺服端 .kt 檔印整組題時,應不含 Android 三題。 [test: t_impact_stack_questions_kt_spring]
- [S28] 當 init 在只有 .jsx 檔的專案產骨架時,symbol_profile 應猜成 typescript。 [test: t_init_skeleton_jsx_symbol_profile]
- [S29] 當 react-idioms 寫完時,每條機檢欄的 eslint 規則代號應在 order-web 已裝的 eslint 與 eslint-plugin-react-hooks 上實跑核對過,沒裝的那幾條應標「未實跑」。 [manual: 在 order-web 跑 `npx eslint --print-config src/App.tsx` 與對每條規則各造一個違規樣本,把版本與結果寫進 skill 的核對邊界]

## 實務隱患

- 效能:判伺服端要讀建置檔與 `.kt` 檔頭,跟 `_node_flavor` 一樣每份只讀一次、快取;改檔前推播的時間預算照既有上限。eslint 偵測只看根目錄幾個固定檔名,不掃樹。
- 併發:只讀檔與產骨架,單人依序操作,沒有共用狀態要鎖。
- 守衛面:會碰。①「跑過的證據」樣式放寬是合約測試閘的判準——放太寬會把沒跑的當跑過(假綠),所以 S5 釘「全部 skipped 判沒跑過」、S7 釘 jest 原樣式不退化;②B10 讓表態閘少問三題,判錯平台會讓 Android 專案漏問——只在「全部 .kt 都判成伺服端」才拿掉,判不出一律照舊,S24、S25 釘住;③react 題組上線後,React 專案推送前要表態的題換一批,在途分支會重新表態(SOP 第 2 步記過的代價),order-web 是唯一受影響的專案。
- 相容:既有 Vue 專案、Node 後端、svelte/angular 專案的判棧結果不變(S13、S14);設定寫 node-jest 的既有 Node 專案跑過證據照舊(S7)。
- 已排除:金流:只改判棧、題目、骨架與說明文件,不碰任何金流資料。
- 已排除:對外送出:init 與 doctor 只印提醒、寫本機設定骨架,不對外寄送任何東西。
- 已排除:不可逆:全部是程式與文件改動,git revert 即可回退;init 不覆寫既有設定、也不寫 lint.json。

## 不做

- Svelte、Angular、Solid 的題組與慣例(使用者 2026-10-15 裁:之後有專案再各自補,照補新語言SOP 開案)。
- Next.js 伺服端渲染、React Server Components 專題(水合差異已有代碼審角色卡 fe-hydration)。
- init 自動寫 `.lumos/lint.json`(理由見〈做法〉W7)。偵測表也先不收 eslint 以外的 linter(biome、ruff、detekt、swiftlint),之後有專案撞到再加列。
- 比對表 W1(測試名寫中文句子會懸空)、F4/F10(需求與設計審的前端鏡頭)、W11(前端測試品質指引)——各在別的組。
- 改 kt 觸發詞的大小寫規則(`val view` 撞 `\bView\b`):Android 專案那邊沒有回報,改了要重驗全表樣本;Spring 專案靠平台判定已不受影響。
- Java 檔的 Android/伺服端分流:java 題組的 Android 題本來就靠觸發詞,`.java` 角色判定已有「沒 android 匯入判後端」。

## 回退

程式改動 git revert 那個提交即可:`_node_flavor_of` 回到只回 vue/node,react 題組與 `react-extcode` 一起消失,表態閘的全表 id 集合跟著回去(`t_stack_question_triggers` 同一個提交改回);B10 拿掉 `platform` 欄與排除參數,行為回到現況;init 骨架回到只給 jest;跑過證據樣式回到 jest 那條。`skills/react-idioms/` 與前端範本檔刪掉,06 那一列與 SKILL.md 首頁的指路句刪掉,templates.md 與 ONBOARDING 的清單刪掉 react-idioms。兩份目錄筆記的 React 段是第二個提交,單獨 revert。已經用了 vitest 骨架的消費專案設定不會被改回,它的 `node-vitest` 仍是合法 profile 名。不碰任何帳本。

## 合約候選

(無)

## 審計修正紀錄

