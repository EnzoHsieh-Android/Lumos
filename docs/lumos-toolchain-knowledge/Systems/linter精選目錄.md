---
type: system
status: done
created: 2026-07-17
updated: 2026-07-26
self_audit: sonnet/2026-07-24
tags:
  - type/system
  - status/done
related:
  - "[[Systems/lint-version-watch]]"
  - "[[Systems/pitfalls-lint-adapter]]"
summary: |-
  KEY:各語言精選 linter 參考目錄(2026-07 社群現況搜證)——供各專案 setup 時挑要裝的 linter;裝了才進該專案 .lumos/lint.json(跑 SARIF)+ .lumos/lint-watch.json(盯新版)。此節點是「該裝什麼」的權威菜單,不是「已裝什麼」的清單
  KEY:linter=風格+最佳實踐檢查(抓代碼問題),≠一般依賴——lint-watch.json 只放真 linter(2026-07-17 收窄事故[[Issues/lint-watch空轉假綠]]:LandmarkMember 誤塞 ClosedXML/Dapper/SqlClient 等執行期依賴,已清成只留 StyleCop)
  KEY:C#(nuget)——StyleCop.Analyzers(風格/命名/排版)｜Roslynator.Analyzers(500+品質簡化)｜SonarAnalyzer.CSharp(code smell+安全)｜Meziantou.Analyzer(最佳實踐)｜Microsoft.CodeAnalysis.NetAnalyzers(第一方基線,nullable/async/平台;.NET10 SDK 內建)｜Microsoft.VisualStudio.Threading.Analyzers(async死鎖,後端重點)
  KEY:Kotlin/Android(github/google-maven)——detekt(github:detekt/detekt,複雜度/實踐;★coroutines 規則集=併發軸主力:GlobalScope 濫用/結構化併發破壞/Dispatchers 誤用/blocking 混入 suspend,2026-07-26 補點名★)｜ktlint(github:pinterest/ktlint,格式)｜ktfmt(github:facebook/ktfmt,格式,與ktlint二選一)｜Android Lint(隨AGP,google-maven盯AGP,平台特定)
  KEY:Vue/TS/JS(npm)——eslint(基石)｜eslint-plugin-vue(<template>AST,需vue-eslint-parser)｜@vue/eslint-config-typescript(Vue+TS flat config)｜typescript-eslint(TS規則)｜oxlint(Rust 50-100x快,大repo前置加速)｜@biomejs/biome(25-35x+含formatter,ESLint替代)
  KEY:SQL(pypi)——sqlfluff(支援 T-SQL 等多方言,免連DB靜態解析+auto-fix;LandmarkMember/KDS 的 .sql 適用)
  KEY:[2026-07-26 補]架構 lint 品類(抽象軸,AI 世代新主流)——架構規則寫成單元測試,AI 違反→測試翻紅→agent 拿確定性回饋自修:Konsist(Kotlin,github:LemonAppDev/konsist)｜ArchUnitNET(C#,nuget:ArchUnitNET)｜Harmonize(Swift,2026 明打 AI 護欄定位)。★lumos 天作之合:架構規則=可執行測試=可被 [test:] 綁→分層邊界這類散文合約可升正式 invariant 走完整合約鏈★
  KEY:[2026-07-26 補]ast-grep(跨語言 AST 結構比對引擎,github:ast-grep/ast-grep)——「事故→固化機械規則」的升級引擎:pitfalls 手刻 regex 升 AST 級(誤報少表達力強);CodeRabbit 拿它當底層,官方有 llms.txt 供 LLM 寫規則(誠實:官方自認 AI 生成規則錯誤率仍高,需自修迴圈)。走既有 .lumos/lint.json SARIF 橋接=外部 linter 不碰零依賴家規
  KEY:2026 現況三鐵則——①前端:oxlint/Biome 崛起但 eslint-plugin-vue 自帶compiler產改造AST,oxlint 官方明說不完整相容→Vue專案 ESLint 仍主力,oxlint 當前置加速器(eslint-plugin-oxlint 讓ESLint跳過已覆蓋規則) ②.NET:.NET10 起 Roslyn analyzer 是 SDK 核心,NetAnalyzers 內建,第三方疊加 ③Kotlin:detekt(bug/實踐)+ktlint或ktfmt(格式)分工,別重複
  DEP:[[Systems/lint-version-watch]]
  DEP:[[Systems/pitfalls-lint-adapter]]
---
# linter 精選目錄——各語言該掌握的 linter（2026-07 社群現況）

> **定位**:這是「各專案該裝哪些 linter」的參考菜單(跨專案共用),不是「某專案已裝什麼」的清單。專案 setup 時從此挑對應語言的 linter → 裝進專案 → 才登錄該專案的 `.lumos/lint.json`(終審跑 SARIF)與 `.lumos/lint-watch.json`(盯新版)。
> **緣起**:2026-07-17 使用者發現 lint-watch 收到的是套件升級(ClosedXML/Dapper/SqlClient…)而非 linter——追出宣告檔被誤塞執行期依賴(見 [[Issues/lint-watch空轉假綠]])。收窄回本分之餘,搜社群精選補齊此菜單。

PRIOR-ART: 借社群 curated list(awesome-analyzers / awesome-android-lint)+ 2026 對比評測(oxlint/Biome/ESLint)搜證,非憑印象;裁定=borrow(收錄社群共識,不自造 linter)。

## C#/.NET（registry: `nuget:<id>`）
| linter | 用途 | 備註 |
|---|---|---|
| **StyleCop.Analyzers** | 風格/命名/排版/文件註解(數百規則) | LandmarkMember 已裝(唯一) |
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

## 架構 lint（抽象軸；2026-07-26 補——AI 世代新品類）

「架構規則寫成單元測試」：分層依賴方向、命名慣例、「UseCase 不准碰 DB」這類規則機械可驗，AI 寫的碼違反 → 測試翻紅 → agent 拿到確定性回饋自己修。2026 年此品類明確以「AI 生成碼的確定性護欄」自我定位。

| 語言 | 工具 | registry |
|---|---|---|
| Kotlin | **Konsist**（規則即測試，跑在既有測試套件裡） | `github:LemonAppDev/konsist` |
| C#/.NET | **ArchUnitNET**（ArchUnit 移植） | `nuget:ArchUnitNET` |
| Swift | Harmonize（參考，本組合無 Swift 專案） | github:perrystreetsoftware/Harmonize |

**lumos 接點（此品類最值錢處）**：架構規則＝可執行測試＝可被 `[test:]` 綁定——圖譜裡「分層邊界」等散文級合約可升格正式 invariant 走完整合約鏈（綁定→審計→Check T）。試點：Citrus_KDS **已完成**（2026-07-26，commit 16ee0ce）——5 條規則依其 MVVM架構 節點約定而寫；**首跑 3 紅全真訊號**：抓到真 DIP 違規（VM/UseCase 注入 Impl，修為介面+@Binds）＋ grep 漏看的第二處 GlobalScope（查證後文件化豁免）＋一次規則校準（sealed 結果型別）；已立 ★INVARIANT★ 四子規則各綁 [test:]、獨立審計 mutation 實測非稻草人。**結論：品類有效，可擴 LandmarkMember（ArchUnitNET）**。

## 跨語言：ast-grep（事故固化引擎；2026-07-26 補）

AST 級結構比對（比 regex 誤報少、表達力強），多語言單一引擎；CodeRabbit 以它為底層、官方供 `llms.txt` 讓 LLM 寫規則。**用途定位**：pitfalls 的事故 pattern 從手刻 regex 升級 AST 規則——事故再犯的固化路徑。接法＝既有 `.lumos/lint.json` SARIF 橋（外部 linter，不碰零依賴家規）。誠實：官方自認 AI 生成規則錯誤率仍高，規則要配自我修正迴圈、上線前人過目。

## 誠實邊界
- 這是 2026-07 快照,linter 生態變動快(oxlint/Biome 仍在成熟弧上;Swashbuckle 這類已被 .NET 內建 OpenAPI/Scalar 挑戰)——`valid_under` 記為「2026-07 社群現況」,半年後宜重搜。
- 「該裝哪些」是團隊決定,此菜單只列社群共識選項,不強制;裝了才進 lint.json/lint-watch.json。
- registry 座標須與 [[Systems/lint-version-watch]] 支援的 type 對齊(nuget/npm/pypi/github/maven/google-maven);detekt/ktlint 走 github release(maven artifact 亦可)。
