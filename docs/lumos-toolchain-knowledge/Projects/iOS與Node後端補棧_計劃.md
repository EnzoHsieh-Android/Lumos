---
type: project
status: doing
created: 2026-09-08
updated: 2026-09-08
aliases:
  - iOS 補棧
  - Node 後端補棧
  - swift-xctest profile
  - node-jest profile
  - swift-idioms
  - node-idioms
related:
  - "[[Projects/工具分類_計劃]]"
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Systems/check-y-symbol-existence]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Projects/pitfalls棧別效能追問_計劃]]"
  - "[[Projects/kotlin慣例skill_計劃]]"
  - "[[Projects/idioms自維護迴路_計劃]]"
  - "[[Issues/linter-gap實務隱患]]"
  - "[[Systems/補新語言SOP]]"
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
summary: |-
  FLAG:DECISION
  KEY:★立案(2026-09-08 Enzo:「如果 Lumos 拿來開發 iOS 和 Node.js 後端可以嗎?」→「要補的東西先補一補」)★——工具鏈八成不看棧,綁棧的只有第 7 類「技術棧知識與 linter 橋接」+測試綁定 profile;本案把 iOS(Swift)與 Node.js/TS 後端兩棧的缺格一次補齊,★全部只有合成樣本測試、沒有任何真專案跑過★
  KEY:補了七格——①TEST_PROFILES 加 swift-xctest(XCTest test 前綴+Swift Testing @Test 兩代並收,suffix 目錄模式)與 node-jest(=node-vitest 別名;test/it/describe('id'),檔名錨 *.test.*/*.spec.*) ②SYMBOL_PROFILES 加 swift/typescript(借 kotlin 形狀) ③_STACK_PERF_QUESTIONS 加 swift 五問與 node 五問 ④架構對齊鏡頭副檔名→慣例 skill 加 swift-idioms/node-idioms ⑤linter精選目錄加 Swift/iOS 與 Node 後端兩段 ⑥效能檢核目錄加兩段 ⑦新 skill swift-idioms、node-idioms 各 14 條
  KEY:★設計決定:.ts/.js 分前後端靠 package.json 不靠副檔名★——同一個副檔名 Vue 前端與 Node 後端都用;新 helper 從檔案所在目錄往上找最近的 package.json(monorepo 各包各判),依賴有前端框架(vue/nuxt/react/next/svelte/angular…)=前端沿舊行為(vue-idioms、不附 node 題),否則=後端(node-idioms、附 node 題);沒 package.json=舊行為。效能追問表的鍵因此是 "node" 不是副檔名 [test:t_pitfalls_diff_node_flavor_by_package_json]
  KEY:★順手抓到一個舊 bug★——Check Y 掃碼庫走 CODE_EXTS_T 這張表、不走 SYMBOL_PROFILES 的 code_exts,表裡沒有 .swift(也沒 .dart、.mjs/.cjs):Swift 專案每個符號都會被判「查無」;新測試翻紅抓到,已補進表 [test:t_checky_swift_and_typescript_profiles]
  KEY:刻意沒做——CocoaPods 版本盯梢(lint-watch 無 registry 種類,SwiftPM 走既有 github 座標即可);Periphery 的 SARIF 橋(它只吐 xcode/json/csv);__tests__/ 下無後綴檔的 Jest 檔名錨(走 config 逃生口);兩支 idioms skill 的 design-loop(散文 skill 走實作真測=首個接入專案回填,同 kotlin-idioms 路徑;profile/regex 那部分由 3 條合成樣本測試守)
  KEY:[2026-09-08 六棧世界對照]Enzo 問「我們問的這些問題夠了嗎」→六棧各對一次世界清單(nodebestpractices 百條/OWASP Node/Apple Instruments 與 WWDC25/Compose 官方效能頁/MS ASP.NET Core best practices/Vue 官方效能頁/SQL 反模式),13 條候選派乾淨反證席(去 LM/KDS/mOrangePos 實 grep)→駁倒 8、存活 4 條半:kt 副作用 key(折 kt Q1)、sql 隔離等級/鎖順序/parameter sniffing(折 sql Q3)、swift 型別抹除與 layout(折 swift Q2)、swift 耗電(新 Q6)、node 速率限制(只進 idioms R15 不進表);全帳在 [[Issues/linter-gap實務隱患]] 兩段;kt/cs/vue/sql 題數被 t_pitfalls_stack_questions 釘住所以只能折不能加
  PRIOR-ART:借既有 profile 制(TEST_PROFILES/SYMBOL_PROFILES 加條目,零新機制)、既有效能追問三時機管道、既有 idioms skill 版型(kotlin/csharp);世界事實網搜:SwiftLint 內建 --reporter sarif、Biome 2.4 原生 --reporter=sarif、ESLint 走 @microsoft/eslint-formatter-sarif、Swift Testing @Test 任意名/任意位置、Jest 與 Vitest -t 同語法、xcodebuild -only-testing Target/Class/method
  DEP:scripts/lumos(SWIFT_TEST_RE/JEST_TEST_RE/TEST_PROFILES/SYMBOL_PROFILES/CODE_EXTS_T/_STACK_PERF_QUESTIONS/_node_flavor/_stack_key_for_file/_idiom_skill_for)｜skills/swift-idioms｜skills/node-idioms｜skills/lumos-project-notes/reference.md 測試棧 profile 段
---
# iOS 與 Node 後端補棧（2026-09-08）

> 白話：Enzo 問「Lumos 拿去做 iOS 和 Node 後端行不行」。答案是行，因為工具鏈大部分吃的是 markdown 和 git，不看語言；真正綁語言的只有「工具對這個技術棧知道什麼」那一類——測試怎麼認、符號長什麼形狀、該裝哪些 linter、審查該問哪些效能問題、寫碼有哪些慣例。這篇就是把這五樣對 Swift 和 Node 各補一份。**全部是照設計補的，沒有任何一個真專案跑過**，第一個接入的專案要把踩到的坑回填回來。

## 補了什麼（對照最初那張表）

| 要補什麼 | 做法 | 守衛 |
|---|---|---|
| 測試綁定 profile | `swift-xctest`（XCTest `func test*` 靠 lookahead 限前綴；Swift Testing `@Test` 巨集任意名、`@Test("顯示名")`、換行後帶修飾詞都認；測試 target 走頂層 `*Tests` suffix，pure/state 排除 `*UITests`、behavioral 只認 `*UITests`）、`node-jest`＝`node-vitest`（`test/it/describe('id')` 含 `.only/.skip/.concurrent`；檔名錨 `*.test.*`/`*.spec.*`；scaffold `{m}.test.ts`） | 合成樣本測試各 7 條 |
| 符號形狀 profile | `swift`、`typescript` 借 Kotlin 的 PascalCase 形狀；裸 camelCase 自由函式不進候選（保守天花板，噪音比漏檢貴） | doctor 對 .swift/.ts 合成 repo 各跑一次 |
| 效能追問 | `swift` 五問、`node` 五問接進既有三時機（pitfalls --diff／impact hook／code-loop 留痕） | node 分流測試 |
| 慣例 skill 派給審查員 | `.swift`→swift-idioms；`.ts/.js`→看 package.json | 同上 |
| linter 目錄 | Swift 段：SwiftLint（內建 SARIF）、SwiftFormat／swift-format、Periphery、嚴格併發；Node 段：eslint＋typescript-eslint（SARIF formatter）、eslint-plugin-n、eslint-plugin-security、Biome 2.4 SARIF、knip、tsc | 目錄是散文，無機械守 |
| 效能檢核目錄 | iOS 八項、Node 七項，各標「機械可查 vs 人判提問」 | 與 `_STACK_PERF_QUESTIONS` 雙向同步義務（既有家規） |
| idioms skill | `swift-idioms` 14 條（並行／Task 生命週期／actor 重入／MainActor／weak self／SwiftUI body／id 穩定／force unwrap／不可逆防重送）、`node-idioms` 14 條（並行／有界並行／floating promise／不阻塞事件迴圈／逾時取消／程序生命週期／stream／長活集合／邊界驗證／不可逆冪等） | skill 目錄掃描自動註冊（`_skills_list`），無需改安裝器 |

## 前後端分流的設計（唯一一個真的要想的地方）

- **問題**：`.ts`／`.js` 在 Vue 前端和 Node 後端都出現，之前的對映表把它們全歸 vue-idioms；直接加 node 題會塞給前端檔。
- **裁定**：從檔案所在目錄往上找最近的 `package.json`，看 dependencies／devDependencies／peerDependencies 的鍵——有前端框架（vue、nuxt、react、next、svelte、angular、solid、preact）就是前端，維持舊行為；有 package.json 但沒前端框架就是後端；找不到 package.json 維持舊行為。只看鍵不猜內容，因為猜錯的代價是把後端問題塞給前端檔。
- **後果**：效能追問表的鍵是 `node` 不是副檔名；兩個消費者（pitfalls 與 impact hook）都改走同一支 helper，不各抄一份副檔名邏輯。

## 誠實邊界與回頭條件

- **零真專案**：所有 profile 只在合成樣本上跑過。XCTest 的目錄慣例（`AppTests`／`AppUITests`）、SwiftPM 的 `Tests/`、Jest 的 `__tests__/` 都是照文件寫的，真專案的 monorepo／多 target 佈局可能不同。
- **Swift Testing 與 xcodebuild 的 `-only-testing`**：識別子格式對 Swift Testing 的 suite 命名有相容問題（網搜有人踩到），跑單支測試的指令得在真機驗。
- **SwiftLint SARIF 兩個已知小坑**（uri 絕對路徑、startColumn 型別）：接進 lint.json 前先拿一份對照 diff 行號。
- **design-loop 跳過**：散文 skill 走「首個接入專案實跑回填」，跟 kotlin-idioms 當年一樣；程式部分小且有測試。

REVISIT:2026-11-08 兩個月內若仍沒有任何 iOS 或 Node 後端專案接入，這批 profile 與 skill 降成 `[planned]` 標示「未實證」，避免下一個人把它當已驗證的東西用。
