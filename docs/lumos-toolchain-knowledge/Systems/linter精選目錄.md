---
type: system
status: done
created: 2026-07-17
updated: 2026-07-27
self_audit: sonnet/2026-07-27
about_code_stamp: batch-2026-08-23/2026-08-23/0c510637cbb0
tags:
  - type/system
  - status/done
  - scope/stack-knowledge
related:
  - "[[Systems/lint-version-watch]]"
  - "[[Systems/pitfalls-lint-adapter]]"
summary: |-
  KEY:各語言精選 linter 參考目錄(2026-07 社群現況搜證)——供各專案 setup 時挑要裝的 linter;裝了才進該專案 .lumos/lint.json(跑 SARIF)+ .lumos/lint-watch.json(盯新版)。此節點是「該裝什麼」的權威菜單,不是「已裝什麼」的清單
  KEY:linter=風格+最佳實踐檢查(抓代碼問題),≠一般依賴——lint-watch.json 只放真 linter(2026-07-17 收窄事故[[Issues/lint-watch空轉假綠]]:LandmarkMember 誤塞 ClosedXML/Dapper/SqlClient 等執行期依賴,已清成只留 StyleCop;[2026-07-27]二次收口:留下的 StyleCop 查證亦從未裝過(csproj 0 引用,「已裝」係循環引用 watch 條目),watch 清空——「裝了才進 watch」須以 csproj 為準,不可信 watch 自身)
  KEY:C#(nuget)——StyleCop.Analyzers(風格/命名/排版)｜Roslynator.Analyzers(500+品質簡化)｜SonarAnalyzer.CSharp(code smell+安全)｜Meziantou.Analyzer(最佳實踐)｜Microsoft.CodeAnalysis.NetAnalyzers(第一方基線,nullable/async/平台;.NET10 SDK 內建)｜Microsoft.VisualStudio.Threading.Analyzers(async死鎖,後端重點)
  KEY:Kotlin/Android(github/google-maven)——detekt(github:detekt/detekt,複雜度/實踐;★coroutines 規則集=併發軸主力:GlobalScope 濫用/結構化併發破壞/Dispatchers 誤用/blocking 混入 suspend,2026-07-26 補點名★)｜ktlint(github:pinterest/ktlint,格式)｜ktfmt(github:facebook/ktfmt,格式,與ktlint二選一)｜Android Lint(隨AGP,google-maven盯AGP,平台特定);[2026-07-27]標準接法立=brew 安裝+本repo configs/detekt/android.yml 共用差分(開預設關的 GlobalCoroutineUsage/SuspendFunSwallowedCancellation/CouldBeSequence——coroutines 規則集「有裝≠有開」),lint.json 樣板見本文,KDS 首消費端
  KEY:Vue/TS/JS(npm)——eslint(基石)｜eslint-plugin-vue(<template>AST,需vue-eslint-parser)｜@vue/eslint-config-typescript(Vue+TS flat config)｜typescript-eslint(TS規則)｜oxlint(Rust 50-100x快,大repo前置加速)｜@biomejs/biome(25-35x+含formatter,ESLint替代)
  KEY:SQL(pypi)——sqlfluff(支援 T-SQL 等多方言,免連DB靜態解析+auto-fix;LandmarkMember/KDS 的 .sql 適用)
  KEY:[2026-09-08 iOS/Node 補棧,★兩棧都尚無消費端實跑★,[[Projects/iOS與Node後端補棧_計劃]]]Swift/iOS(github)——SwiftLint(github:realm/SwiftLint,風格+實踐;★內建 `--reporter sarif` 可直接進 lint.json★)｜SwiftFormat(github:nicklockwood/SwiftFormat,格式)或 swift-format(Apple 官方,Swift 6 起隨 toolchain)二選一｜Periphery(github:peripheryapp/periphery,死碼)｜Harmonize(架構 lint,已列);SwiftPM 依賴無中央 registry→lint-watch 用 github 座標盯 release
  KEY:[2026-09-08]Node.js/TS 後端(npm)——eslint+typescript-eslint(基石;SARIF 走 @microsoft/eslint-formatter-sarif,`-f @microsoft/sarif`)｜eslint-plugin-n(Node 專用:未處理 rejection/廢棄 API/同步 fs)｜eslint-plugin-security(注入/regex 回溯/child_process)｜@biomejs/biome(★2.4 起原生 `--reporter=sarif`★,2026 首個 minor)｜knip(專案級死 export/死依賴,ESLint 看不到跨檔)｜dependency-cruiser(分層,已列);跟 Vue 段共用 eslint 家族但插件不同,別把 eslint-plugin-vue 裝進純後端
  KEY:[2026-07-26 補]架構 lint 品類(抽象軸,AI 世代新主流)——架構規則寫成單元測試,AI 違反→測試翻紅→agent 拿確定性回饋自修:Konsist(Kotlin,github:LemonAppDev/konsist)｜ArchUnitNET(C#,nuget:ArchUnitNET)｜Harmonize(Swift,2026 明打 AI 護欄定位)。★lumos 天作之合:架構規則=可執行測試=可被 [test:] 綁→分層邊界這類散文合約可升正式 invariant 走完整合約鏈★
  KEY:[2026-07-26 補]ast-grep(跨語言 AST 結構比對引擎,github:ast-grep/ast-grep)——「事故→固化機械規則」的升級引擎:pitfalls 手刻 regex 升 AST 級(誤報少表達力強);CodeRabbit 拿它當底層,官方有 llms.txt 供 LLM 寫規則(誠實:官方自認 AI 生成規則錯誤率仍高,需自修迴圈)。走既有 .lumos/lint.json SARIF 橋接=外部 linter 不碰零依賴家規
  KEY:2026 現況三鐵則——①前端:oxlint/Biome 崛起但 eslint-plugin-vue 自帶compiler產改造AST,oxlint 官方明說不完整相容→Vue專案 ESLint 仍主力,oxlint 當前置加速器(eslint-plugin-oxlint 讓ESLint跳過已覆蓋規則) ②.NET:.NET10 起 Roslyn analyzer 是 SDK 核心,NetAnalyzers 內建,第三方疊加 ③Kotlin:detekt(bug/實踐)+ktlint或ktfmt(格式)分工,別重複
  DEP:[[Systems/lint-version-watch]]
  DEP:[[Systems/pitfalls-lint-adapter]]
about_code:
  - configs/detekt/android.yml
verified_by:
  - "[[Verification/2026-09-08_iOS與Node補棧合成樣本測試]]"
---
# linter 精選目錄——各語言該掌握的 linter（2026-07 社群現況）

> **定位**:這是「各專案該裝哪些 linter」的參考菜單(跨專案共用),不是「某專案已裝什麼」的清單。專案 setup 時從此挑對應語言的 linter → 裝進專案 → 才登錄該專案的 `.lumos/lint.json`(終審跑 SARIF)與 `.lumos/lint-watch.json`(盯新版)。
> **緣起**:2026-07-17 使用者發現 lint-watch 收到的是套件升級(ClosedXML/Dapper/SqlClient…)而非 linter——追出宣告檔被誤塞執行期依賴(見 [[Issues/lint-watch空轉假綠]])。收窄回本分之餘,搜社群精選補齊此菜單。

PRIOR-ART: 借社群 curated list(awesome-analyzers / awesome-android-lint)+ 2026 對比評測(oxlint/Biome/ESLint)搜證,非憑印象;裁定=borrow(收錄社群共識,不自造 linter)。

## C#/.NET（registry: `nuget:<id>`）
| linter | 用途 | 備註 |
|---|---|---|
| **StyleCop.Analyzers** | 風格/命名/排版/文件註解(數百規則) | ⚠2026-07-27 查證:LandmarkMember **從未裝過**(git 全史 csproj 0 引用)——舊記「已裝(唯一)」是循環引用 lint-watch 殘留條目的錯誤認知,watch 已清;LM 實裝=VSTHRD+內建 NetAnalyzers |
| **Roslynator.Analyzers** | 500+ 品質/簡化(冗餘賦值、可簡化條件、缺 ConfigureAwait、未用參數) | 建議補 |
| **SonarAnalyzer.CSharp** | code smell + 安全覆蓋(SonarLint/SonarQube 同源) | 有跑 SonarQube 則必配 |
| **Meziantou.Analyzer** | C# 最佳實踐 | 建議補 |
| **Microsoft.CodeAnalysis.NetAnalyzers** | 第一方基線(nullable/async/平台相容) | .NET10 SDK 內建,獨立 nuget 供舊 SDK |
| **Microsoft.VisualStudio.Threading.Analyzers** | async/併發死鎖 | async 後端(如 LandmarkMember)重點 |

推薦組合:NetAnalyzers(基線) + StyleCop(風格) + Roslynator(簡化) + 選 SonarAnalyzer(深度)。

## Kotlin/Android（registry: `github:<owner>/<repo>` 或 `google-maven`）
| linter | 用途 | registry 座標 |
|---|---|---|
| **detekt** | 複雜度/命名/可維護性靜態分析(抓 bug/實踐) | `github:detekt/detekt` |
| **ktlint** | 格式/風格(縮排/間距/行長) | `github:pinterest/ktlint` |
| **ktfmt** | 格式化(Block 系) | `github:facebook/ktfmt`(與 ktlint 二選一) |
| **Android Lint** | 平台特定問題 | 隨 AGP,用 `google-maven` 盯 AGP 版本 |

分工:detekt 抓 bug/實踐、ktlint 或 ktfmt 管格式——別兩個格式器並用。

### detekt 標準接法（2026-07-27 立;消費端:Citrus_KDS、mOrangePos——mOrangePos 首掃唯一 GlobalScope 命中=crash 補送 App 層正當用法,同 KDS 閃退家族 pattern）

- **安裝=`brew install detekt`**(套件管理器管生命週期)。⚠ 前科:KDS 曾把 detekt jar 放 `/tmp` 被系統清掉兩次(2026-07-17 首發、2026-07-27 重演,見 [[Systems/lint-declaration-health]])——外部工具一律裝進套件管理器,嚴禁易失位置。
- **共用差分設定=`configs/detekt/android.yml`**(本 repo,隨 clone 分發):開 detekt 預設關但效能檢核目錄點名的三條——`GlobalCoroutineUsage`(GlobalScope 裸用)/`SuspendFunSwallowedCancellation`(吞取消)/`CouldBeSequence`(長鏈該 asSequence)。⚠ coroutines 規則集「有裝≠有開」:`--build-upon-default-config` 裸跑時這三條全不生效。
- **lint.json 樣板**(新 Android 專案 setup 直接抄):
  ```
  detekt --input <src 目錄> --report sarif:{LINT_SARIF_OUT} --build-upon-default-config --config $HOME/harness/lumos-toolchain/configs/detekt/android.yml
  ```
  (`$HOME` 可用:lint 命令走 shell 執行;`--input` 要指整個 source set,別只指單檔)
- 接完跑 `lumos lint-check --smoke` 驗宣告真跑得動(這正是抓到 /tmp jar 蒸發的守衛)。

## Vue/TS/JS（registry: `npm:<pkg>`）
| linter | 用途 | 備註 |
|---|---|---|
| **eslint** | 生態基石 | flat config(v13- 才支援舊 .eslintrc) |
| **eslint-plugin-vue** | `<template>` AST 檢查 | 需 vue-eslint-parser |
| **@vue/eslint-config-typescript** | Vue+TS flat config(withVueTs) | |
| **typescript-eslint** | TS 規則 | |
| **oxlint** | Rust,50-100x 快 | 大 repo 前置加速;Vue template 支援不完整、無 formatter、成熟度較早 |
| **@biomejs/biome** | 25-35x 快 + 含 formatter + type-aware 免 tsc | 2026 中小專案 ESLint 替代甜蜜點 |

**Vue 專案要點**:eslint-plugin-vue 自帶 compiler 產改造 AST,oxlint 官方明說**不會完整相容**→ Vue 專案 ESLint 仍是主力,oxlint 只當前置加速器(`eslint-plugin-oxlint` 讓 ESLint 跳過 oxlint 已覆蓋的規則)。純 TS/JS(非 Vue)可考慮 Biome 全換。

## SQL（registry: `pypi:<pkg>`）
| linter | 用途 | 備註 |
|---|---|---|
| **sqlfluff** | 多方言(含 T-SQL)靜態解析 + auto-fix,免連 DB | LandmarkMember/KDS 的 `.sql` 適用;經 `lumos sqlfluff-sarif` 橋接進 lint-adapter |

## Flutter/Dart（registry: `pub:<pkg>`；2026-07-26 補，taroko_app 接入調研）

- **flutter_lints**（官方推薦基線,Effective Dart 對齊）→ 進階嚴格版 **very_good_analysis**（企業級,強制 const/顯式型別）。
- **custom_lint**:自建規則框架(riverpod_lint 等生態基座)。**DCM**:複雜度/程式碼度量(商用)。
- **架構軸(import 邊界,Dart 3.10+ 才可用)**:`import_rules`(2026/02,YAML 宣告 import 約束進 dart analyze)｜`import_lint`(2026/04)｜`barrel_file_lints`(feature 分層/barrel 規則)。
- ⚠ **SDK 門檻實錘(taroko_app)**:Dart 2.19(pre-Dart 3)上述架構套件與新版 VGA 全裝不了——舊 SDK 專案的架構軸=升級 Flutter 後解鎖;過渡期用 analysis_options 手開嚴格規則(零依賴不受版本卡)。
- **Check T**:dart profile 已內建(test('id')/testWidgets('id') 識別字名錨+*_test.dart 檔名錨)——Dart 測試可正式綁 [test:] 走合約鏈。
- SARIF 橋:`dart analyze` 無原生 SARIF → .lumos/lint.json 接法待 Dart 3 升級後再評(現以 analyzer 直跑為主)。

## Swift/iOS（registry: `github:<owner>/<repo>`；2026-09-08 補，★尚無 Swift 消費端，未實裝跑過★）
| linter | 用途 | 備註 |
|---|---|---|
| **SwiftLint** | 風格＋最佳實踐（200+ 規則，含 force_unwrap/force_try/implicitly_unwrapped 等安全類與 cyclomatic_complexity） | `github:realm/SwiftLint`；★內建 `swiftlint --reporter sarif --output <檔>`★，可直接進 `.lumos/lint.json`；已知 SARIF 小坑：uri 曾輸出絕對路徑、startColumn 型別（issue #5698/#5699），接進去先拿一份 SARIF 對照 diff 行號對不對 |
| **SwiftFormat**（或 Apple **swift-format**） | 格式；二選一 | `github:nicklockwood/SwiftFormat`；swift-format 自 Swift 6 隨 toolchain 附帶，零安裝但規則少 |
| **Periphery** | 死碼（未用的型別/函式/參數；SwiftPM 與 Xcode 專案都吃） | `github:peripheryapp/periphery`；社群公認 Swift 死碼首選；輸出格式為 xcode/json/csv，無 SARIF→要進 lint.json 得自寫小橋（同 sqlfluff-sarif 模式），未做 |
| Xcode 內建 **Static Analyzer**／**Strict Concurrency**（`-strict-concurrency=complete`） | 併發軸主力：資料競爭、Sendable 違規在編譯期抓 | 隨 toolchain；不是獨立 linter，但 Swift 6 語言模式把大半「idioms 不可機檢」條目變成編譯錯誤——新專案優先開 |
| Harmonize | 架構 lint（見下方架構 lint 品類） | 已列 |

**SwiftPM 沒有中央 registry**：依賴就是 git repo，所以 lint-watch 對 Swift linter 一律用 `github:<owner>/<repo>` 盯 release（既有 kind，不用加）。CocoaPods 專案的 Podspec 版本目前**沒有** registry 種類支援，要盯得自己看。

## Node.js / TypeScript 後端（registry: `npm:<pkg>`；2026-09-08 補，★尚無 Node 後端消費端，未實裝跑過★）
| linter | 用途 | 備註 |
|---|---|---|
| **eslint** ＋ **typescript-eslint** | 基石（flat config）；`no-floating-promises`/`no-misused-promises`/`require-await` 是後端 async 紀律的機檢主力（需 type-aware 設定） | SARIF：`@microsoft/eslint-formatter-sarif`，指令 `eslint -f @microsoft/sarif -o <檔>`（縮寫 `-f sarif` 不能用，套件名不是 eslint-formatter-* 形） |
| **eslint-plugin-n** | Node 專用：`no-sync`（同步 fs 進請求路徑）、`no-deprecated-api`、`no-process-exit`、`handle-callback-err` | `npm:eslint-plugin-n`（eslint-plugin-node 的維護接班） |
| **eslint-plugin-security** | 注入/`child_process`/不安全正則（回溯炸事件迴圈）/`eval` 類 | `npm:eslint-plugin-security`；誤報偏多，當提醒不當閘 |
| **@biomejs/biome** | ESLint＋Prettier 替代，中小專案甜蜜點；★2.4 起原生 `--reporter=sarif`★，不用第三方 formatter | `npm:@biomejs/biome`；type-aware 規則覆蓋仍不及 typescript-eslint，後端 async 紀律那幾條要確認有沒有等價品再換 |
| **knip** | 專案級死碼：未用的 export／檔案／依賴（ESLint 只看單檔，看不到跨檔死 export） | `npm:knip`；無 SARIF，當 CI 報表用 |
| **tsc --noEmit** | 型別檢查當 lint 跑（`strict` 全開；`noUncheckedIndexedAccess` 抓陣列越界） | 隨 typescript；不是 linter 但漏掉等於少一半機檢 |
| dependency-cruiser | 架構 lint（見架構 lint 品類） | 已列 |

**跟 Vue 段的關係**：同一個 eslint 家族、不同插件——純後端**不要**裝 eslint-plugin-vue；monorepo 前後端各自一份 flat config。`lumos pitfalls --diff` 分前後端靠 `package.json` 的依賴（有前端框架＝前端），不靠副檔名。

## 架構 lint（抽象軸；2026-07-26 補——AI 世代新品類）

「架構規則寫成單元測試」：分層依賴方向、命名慣例、「UseCase 不准碰 DB」這類規則機械可驗，AI 寫的碼違反 → 測試翻紅 → agent 拿到確定性回饋自己修。2026 年此品類明確以「AI 生成碼的確定性護欄」自我定位。

| 語言 | 工具 | registry |
|---|---|---|
| Kotlin | **Konsist**（規則即測試，跑在既有測試套件裡） | `github:LemonAppDev/konsist` |
| C#/.NET | **ArchUnitNET**（ArchUnit 移植；套件 id＝`TngTech.ArchUnitNET.xUnit`，裸名查無） | `nuget:TngTech.ArchUnitNET.xUnit` |
| Vue/TS/JS | **dependency-cruiser**（依賴規則+循環+孤兒檔；深度分析）＋ eslint-plugin-boundaries（分層進 ESLint、編輯器即時紅線；社群建議兩者搭配） | `npm:dependency-cruiser`／`npm:eslint-plugin-boundaries` |
| Swift | Harmonize（2026-09-08 起 Swift 段已補 SwiftLint/Periphery 等，仍無 Swift 消費端實跑） | github:perrystreetsoftware/Harmonize |

**lumos 接點（此品類最值錢處）**：架構規則＝可執行測試＝可被 `[test:]` 綁定——圖譜裡「分層邊界」等散文級合約可升格正式 invariant 走完整合約鏈（綁定→審計→Check T）。試點：Citrus_KDS **已完成**（2026-07-26，commit 16ee0ce）——5 條規則依其 MVVM架構 節點約定而寫；**首跑 3 紅全真訊號**：抓到真 DIP 違規（VM/UseCase 注入 Impl，修為介面+@Binds）＋ grep 漏看的第二處 GlobalScope（查證後文件化豁免）＋一次規則校準（sealed 結果型別）；已立 ★INVARIANT★ 四子規則各綁 [test:]、獨立審計 mutation 實測非稻草人。**結論：品類有效**。**第二試點 LandmarkMember 亦完成**（2026-07-26，commit 977744f5，前後端雙側）：後端 ArchUnitNET 四規則＋五處既有債入 baseline（★DEBT 記載）；前端 dependency-cruiser 首跑 0 error＋**抓到 5 個孤兒死檔**；獨立審計 mutation 通過、並揪出「raw SQL 唯一住所」過度宣稱（Services 層 PointsMall 四處直跑 Dapper→措辭修真＋候選未來規則）。**兩試點共同 pattern：首跑必抓到真東西**（KDS＝DIP 違規＋漏看的 GlobalScope；LM＝死檔＋敘述過寬）——品類轉正，四專案可依需擴。

## 跨語言：ast-grep（事故固化引擎；2026-07-26 補）

AST 級結構比對（比 regex 誤報少、表達力強），多語言單一引擎；CodeRabbit 以它為底層、官方供 `llms.txt` 讓 LLM 寫規則。**用途定位**：pitfalls 的事故 pattern 從手刻 regex 升級 AST 規則——事故再犯的固化路徑。接法＝既有 `.lumos/lint.json` SARIF 橋（外部 linter，不碰零依賴家規）。誠實：官方自認 AI 生成規則錯誤率仍高，規則要配自我修正迴圈、上線前人過目。

## 誠實邊界
- 這是 2026-07 快照,linter 生態變動快(oxlint/Biome 仍在成熟弧上;Swashbuckle 這類已被 .NET 內建 OpenAPI/Scalar 挑戰)——`valid_under` 記為「2026-07 社群現況」,半年後宜重搜。
- REVISIT:2027-01-31 重搜 linter 生態(半年快照到期;上行條款)
- 「該裝哪些」是團隊決定,此菜單只列社群共識選項,不強制;裝了才進 lint.json/lint-watch.json。
- registry 座標須與 [[Systems/lint-version-watch]] 支援的 type 對齊(nuget/npm/pypi/github/maven/google-maven);detekt/ktlint 走 github release(maven artifact 亦可)。
