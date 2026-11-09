---
type: system
status: done
created: 2026-07-17
updated: 2026-11-09
self_audit: sonnet/2026-07-27
about_code_stamp: batch-2026-08-23/2026-08-23/0c510637cbb0
tags:
  - type/system
  - status/done
  - scope/stack-knowledge
related:
  - "[[Systems/lint-version-watch]]"
  - "[[Systems/pitfalls-lint-adapter]]"
  - "[[Projects/社群規則第二批_計劃]]"
summary: |-
  KEY:各語言精選 linter 參考目錄(2026-07 社群現況搜證)——供各專案 setup 時挑要裝的 linter;裝了才進該專案 .lumos/lint.json(跑 SARIF)+ .lumos/lint-watch.json(盯新版)。此節點是「該裝什麼」的權威菜單,不是「已裝什麼」的清單
  KEY:linter=風格+最佳實踐檢查(抓代碼問題),≠一般依賴——lint-watch.json 只放真 linter(2026-07-17 收窄事故[[Issues/lint-watch空轉假綠]]:LandmarkMember 誤塞 ClosedXML/Dapper/SqlClient 等執行期依賴,已清成只留 StyleCop;[2026-07-27]二次收口:留下的 StyleCop 查證亦從未裝過(csproj 0 引用,「已裝」係循環引用 watch 條目),watch 清空——「裝了才進 watch」須以 csproj 為準,不可信 watch 自身)
  KEY:C#(nuget)——StyleCop.Analyzers(風格/命名/排版)｜Roslynator.Analyzers(500+品質簡化)｜SonarAnalyzer.CSharp(code smell+安全)｜Meziantou.Analyzer(最佳實踐)｜Microsoft.CodeAnalysis.NetAnalyzers(第一方基線,nullable/async/平台;.NET10 SDK 內建)｜Microsoft.VisualStudio.Threading.Analyzers(async死鎖,後端重點)
  KEY:Kotlin/Android(github/google-maven)——detekt(github:detekt/detekt,複雜度/實踐;★coroutines 規則集=併發軸主力:GlobalScope 濫用/結構化併發破壞/Dispatchers 誤用/blocking 混入 suspend,2026-07-26 補點名★)｜ktlint(github:pinterest/ktlint,格式)｜ktfmt(github:facebook/ktfmt,格式,與ktlint二選一)｜Android Lint(隨AGP,google-maven盯AGP,平台特定);[2026-07-27]標準接法立=brew 安裝+本repo configs/detekt/android.yml 共用差分(開預設關的五條:GlobalCoroutineUsage/SuspendFunSwallowedCancellation/SuspendFunWithCoroutineScopeReceiver/CouldBeSequence/ForbiddenMethodCall 禁 collectAsState——「有裝≠有開」,而且[2026-11-04]「有開≠有跑」:除 GlobalCoroutineUsage 外都要型別資訊才跑;[2026-11-06]推送前用 {LINT_FILES_CSV} 只擋不用型別的規則,要型別的靠專案 CI 的 Gradle 型別解析任務加基準線擋,兩段接法見本文,判定表見 Android的detekt規則說實話_計劃),lint.json 樣板見本文,KDS 首消費端
  KEY:Vue/TS/JS(npm)——eslint(基石)｜eslint-plugin-vue(<template>AST,需vue-eslint-parser)｜@vue/eslint-config-typescript(Vue+TS flat config)｜typescript-eslint(TS規則)｜oxlint(Rust 50-100x快,大repo前置加速)｜@biomejs/biome(25-35x+含formatter,ESLint替代)
  KEY:SQL(pypi)——sqlfluff(支援 T-SQL 等多方言,免連DB靜態解析+auto-fix;LandmarkMember/KDS 的 .sql 適用)
  KEY:[2026-09-08 iOS/Node 補棧,★消費專案仍零實跑;SwiftLint 本身 2026-09-13 實跑過(孤立目錄能跑、吐 SARIF),★找不到 Xcode 工具鏈時整支崩潰退出碼 133、零輸出,閘判環境不可用自動放行★;eslint 這台機器根本沒裝,Node/Vue 那條路只有合成測試撐著★,[[Projects/iOS與Node後端補棧_計劃]]]Swift/iOS(github)——SwiftLint(github:realm/SwiftLint,風格+實踐;★內建 `--reporter sarif` 可直接進 lint.json★)｜SwiftFormat(github:nicklockwood/SwiftFormat,格式)或 swift-format(Apple 官方,Swift 6 起隨 toolchain)二選一｜Periphery(github:peripheryapp/periphery,死碼)｜Harmonize(架構 lint,已列);SwiftPM 依賴無中央 registry→lint-watch 用 github 座標盯 release
  KEY:[2026-09-08]Node.js/TS 後端(npm)——eslint+typescript-eslint(基石;SARIF 走 @microsoft/eslint-formatter-sarif,`-f @microsoft/sarif`)｜eslint-plugin-n(Node 專用:未處理 rejection/廢棄 API/同步 fs)｜eslint-plugin-security(注入/regex 回溯/child_process)｜@biomejs/biome(★2.4 起原生 `--reporter=sarif`★,2026 首個 minor)｜knip(專案級死 export/死依賴,ESLint 看不到跨檔)｜dependency-cruiser(分層,已列);跟 Vue 段共用 eslint 家族但插件不同,別把 eslint-plugin-vue 裝進純後端
  KEY:[2026-09-11 Python 補棧,★2026-09-13 工具鏈自己接上 ruff 實跑,當天真的擋下一次推送(20 條新增告警,含 5 條自己剛寫太複雜的函式)★,[[Projects/Python補棧_計劃]]]Python(pypi)——ruff(pypi:ruff,lint+format 基石;★內建 --output-format sarif 直接進 lint.json★;ASYNC/RUF006/S113/RUF032/DTZ 族要在 select 明開,預設只開 E/F)｜mypy(strict,無 SARIF 只 --output json,當 CI 閘)｜bandit(資安,bandit[sarif] 才有 -f sarif,與 ruff S 族重疊)｜pip-audit(依賴漏洞,無 SARIF)｜ty(Astral 新型別檢查器,0.0.x beta 無 SARIF,雷達);格式支援 2026-09-11 本機實跑 --help 核對
  KEY:[2026-07-26 補]架構 lint 品類(抽象軸,AI 世代新主流)——架構規則寫成單元測試,AI 違反→測試翻紅→agent 拿確定性回饋自修:Konsist(Kotlin,github:LemonAppDev/konsist)｜ArchUnitNET(C#,nuget:ArchUnitNET)｜Harmonize(Swift,2026 明打 AI 護欄定位)。★lumos 天作之合:架構規則=可執行測試=可被 `[test:]` 綁→分層邊界這類散文合約可升正式 invariant 走完整合約鏈★
  KEY:[2026-07-26 補]ast-grep(跨語言 AST 結構比對引擎,github:ast-grep/ast-grep)——「事故→固化機械規則」的升級引擎:pitfalls 手刻 regex 升 AST 級(誤報少表達力強);CodeRabbit 拿它當底層,官方有 llms.txt 供 LLM 寫規則(誠實:官方自認 AI 生成規則錯誤率仍高,需自修迴圈)(更正 2026-10-12：官方只說 AI 寫規則容易幻覺、要靠驗證迴圈,沒有「錯誤率仍高」或任何數字;2025-06-21 官方部落格反而說加上驗證迴圈後三家模型表現很好)。走既有 .lumos/lint.json SARIF 橋接=外部 linter 不碰零依賴家規
  KEY:2026 現況三鐵則——①前端:oxlint/Biome 崛起但 eslint-plugin-vue 自帶compiler產改造AST,oxlint 官方明說不完整相容→Vue專案 ESLint 仍主力,oxlint 當前置加速器(eslint-plugin-oxlint 讓ESLint跳過已覆蓋規則) ②.NET:.NET10 起 Roslyn analyzer 是 SDK 核心,NetAnalyzers 內建,第三方疊加 ③Kotlin:detekt(bug/實踐)+ktlint或ktfmt(格式)分工,別重複
  DEP:[[Systems/lint-version-watch]]
  DEP:[[Systems/pitfalls-lint-adapter]]
  FACT:照 detekt 標準接法的命令列樣板(只給 --input)跑,要型別資訊的規則一條都不報也不出錯,kotlin-idioms 點名的協程規則與共用設定開的五條都只剩 GlobalCoroutineUsage 會報;帶 --classpath 與 --jdk-home 才報 [來源:外部] [confirmed:2026-11-01] [查:detekt 1.23.8 最小樣本帶與不帶型別資訊各跑一次]
  REVISIT:2026-12-15 在一個裝了 detekt Gradle 外掛的 Android 專案照 CI 型別檢查範本實跑 detektBaseline<變體> 與 detekt<變體>(驗收 S9),記下任務名、耗時與基準線檔名,跑過就把範本裡「以外掛實際寫出的為準」改成實測值 [closed:2026-11-08 已在 macrobench-lab 複本實跑(AGP 8.13.2、detekt 1.23.8),範本改成實測檔名,紀錄在本篇 verified_by 那篇 2026-11-08 的驗證紀錄]
  PITFALL:compose-rules 那條 detekt 宣告少了 --build-upon-default-config 時,外掛規則一條都不跑、也不報錯 [出處:2026-11-06 本機 detekt 1.23.8 加外掛 0.4.28 實測] [根因:沒帶這個旗標時外掛規則沒被啟用(推測:外掛自帶的預設設定沒疊進來)] [test:t_detekt_compose_rules_shared_config]
  WHY:共用 detekt 設定照 detekt 官方 Compose 頁加六項放寬(Composable 命名、Preview 沒被呼叫與函式數、有預設值的參數、屬性宣告的數字、PascalCase 頂層常數) [出處:2026-11-06 Projects/Android現成檢查接上CI與推送前_計劃;https://detekt.dev/docs/introduction/compose/] [因:現行設定對一支標準 Compose 檔報 6 條,推送前會擋每個新寫的元件] [代價:非 Compose 專案的有預設值長參數、屬性宣告魔術數字、PascalCase 頂層常數也不再報] [test:t_detekt_compose_rules_shared_config]
  PITFALL:AGP 9 內建 Kotlin 下照 CI 型別檢查範本跑 detekt<變體> 會找不到任務 [出處:2026-11-09 nowinandroid 實跑] [根因:detekt 1.23.8 只在套了 kotlin-android 外掛時建型別任務、用舊介面讀變體] [repro:AGP 9.3.2 專案套 detekt 1.23.8 後跑 ./gradlew :app:tasks --all 只見 detekt 與 detektBaseline] [修法:改用 detekt 2.0.0-alpha.6 加 android.disallowKotlinSourceSets=false]
  REVISIT:2027-02-09 查 detekt 2.0 出正式版沒有:出了就把 CI 型別檢查範本裡 AGP 9 那條從 2.0.0-alpha.6 換成正式版、重跑一次 nowinandroid,並決定共用設定與本機 CLI 要不要一起升 2.0(UnusedPrivateMember 鍵名要跟著改)
about_code:
  - configs/detekt/android.yml
  - configs/detekt/compose.yml
verified_by:
  - "[[Verification/2026-09-08_iOS與Node補棧合成樣本測試]]"
  - "[[Verification/2026-09-11_Python補棧合成樣本測試]]"
  - "[[Verification/2026-11-01_Kotlin慣例對齊官方與detekt實測]]"
  - "[[Verification/2026-11-08_detekt的CI型別檢查範本實跑]]"
  - "[[Verification/2026-11-09_Android現成檢查範本在兩個公開專案實跑]]"
---
# linter 精選目錄——各語言該掌握的 linter（2026-07 社群現況）

> **定位**:這是「各專案該裝哪些 linter」的參考菜單(跨專案共用),不是「某專案已裝什麼」的清單。專案 setup 時從此挑對應語言的 linter → 裝進專案 → 才登錄該專案的 `.lumos/lint.json`(終審跑 SARIF)與 `.lumos/lint-watch.json`(盯新版)。
> **緣起**:2026-07-17 使用者發現 lint-watch 收到的是套件升級(ClosedXML/Dapper/SqlClient…)而非 linter——追出宣告檔被誤塞執行期依賴(見 [[Issues/lint-watch空轉假綠]])。收窄回本分之餘,搜社群精選補齊此菜單。

PRIOR-ART: 借社群 curated list(awesome-analyzers / awesome-android-lint)+ 2026 對比評測(oxlint/Biome/ESLint)搜證,非憑印象;裁定=borrow(收錄社群共識,不自造 linter)。

## 工具在「只有原始碼的樹」裡跑不跑得動（2026-09-13 實跑）

> 白話：推送前那道新增告警閘會把改動前後各複製一份出來、各跑一次檢查工具比差集。複製出來的那棵樹只有原始碼——沒有依賴目錄、沒有建置產物。所以「這個工具裝好了」不等於「這道閘用得上它」。

實際跑出來分三類：

| 類別 | 這次驗到的 | 結論 |
|---|---|---|
| 自帶規則的獨立執行檔 | ruff（Python）、detekt（Kotlin）、SwiftLint（Swift）、PMD／Checkstyle（Java）、依賴漏洞掃描器 | **跑得動**，直接吐標準格式(detekt 例外:跑得動不等於規則有在跑,要型別資訊的規則沒給 classpath 就安靜跳過;推送前用 `{LINT_FILES_CSV}` 只擋不用型別的規則,要型別的靠 CI 型別檢查範本,見下面 detekt 標準接法) |
| 要專案先裝依賴才啟動 | eslint（Vue／Node） | **跑得動**，但要把設定檔與依賴目錄一起帶進快照——2026-09-13 拿真的 eslint 端到端驗過，不再只有合成測試 |
| 要先建置才能檢查 | .NET 的 analyzer、Gradle | **完全沒驗過，交付時不要宣稱它可以** |

**SwiftLint 有一個要寫下來的坑**：環境裡找不到 Xcode 工具鏈時，它不是報錯而是整支崩潰——退出碼 133、標準輸出一個字都沒有。這時閘解析不到結果，判定「環境不可用」自動放行。放行會被記次數，但當下不會擋人。接 Swift 專案的命令要自己帶上工具鏈路徑。

### 端到端實跑紀錄（2026-09-13）

三個棧各建一個臨時 repo、宣告檢查工具、故意加一段有問題的新碼，跑推送前那道閘：

| 棧 | 工具與規則集 | 結果 |
|---|---|---|
| Java | PMD `rulesets/java/quickstart.xml` | 新方法的 3 條全抓到；**舊方法裡一模一樣的問題沒報**，基準線比對正確 |
| Node | eslint 10 flat config（`no-unused-vars`／`eqeqeq`） | 新函式的 2 條抓到；**證明快照補設定檔與依賴目錄那一層對真工具有效** |
| Vue | eslint + `eslint-plugin-vue` flat/recommended | 新加的清單少了 key，抓到 `vue/require-v-for-key` |
| SQL | sqlfluff（`--dialect tsql`）+ 既有的格式轉接器 | 新加的查詢 6 條全抓到 |
| Dart | `dart analyze --format=json` + `lumos dart-sarif` | 抓到新函式的沒用到的變數；**轉接器 2026-09-14 已進工具鏈**，讀不懂就失敗、不吐空結果；**編譯期錯誤不收**（快照只有改動檔、import 解析不到會誤報）——**所以這道閘對 Dart 抓不到編譯錯誤**（參數錯、型別不符也算在內），要靠建置與 CI，見 [[Systems/pitfalls-lint-adapter]] |
| C# / .NET | `dotnet build -p:ErrorLog=…` | **今天沒被覆蓋，但不是因為貴**：實測 347 支檔的專案完整建置 8.5 秒、第二次 3.6 秒，格式也讀得懂；真正卡住的是快照裡只有改動檔，編譯起不來 |
| Python | ruff | 見工具鏈自己那次：當天擋下一次真推送 |

**中文專案要放行全形標點（2026-09-14 決定）**：ruff 的 `RUF001`／`RUF002`／`RUF003` 把全形逗號、分號、括號當成「可能打錯的英文標點」。這個 repo 的註解與訊息通篇中文，**一天之內為它繞路三次**（改掉自己寫的標點才推得動）。改法是在宣告裡列白名單（`lint.allowed-confusables`），把我們實際會用的全形標點放進去——**保留它擋真正同形字攻擊那一半價值**（像西里爾字母的 а 冒充拉丁字母 a），只關掉中文標點那一類誤報。實測同一支檔從 11 條降到 0 條。

**規則集要自己挑，預設的不能直接用**：Checkstyle 配它內建的 google 風格，在 3 支 Java 檔上噴 757 條，幾乎全是排版與缺註解；PMD 的 quickstart 在同樣的檔上是 45 條而且是真問題。**這道閘只擋新增的，但噪音大的規則集會讓每次小改都被擋**，所以接的時候先拿專案現有的碼跑一次看數量級。另外 Checkstyle 的訊息會跟著系統語言走（這台機器吐中文）。

### C# 為什麼沒被覆蓋——量過之後的修正（2026-09-13）

**原本的判斷只對了一半。** 先寫的結論是「.NET 的分析器要編譯整個專案，所以這道閘接不上」，聽起來像是成本問題。實際量下來不是：

| 量什麼 | 結果 |
|---|---|
| 347 支 C# 檔的專案，全新副本完整建置 | **8.5 秒**（吐 47 條分析器結果，格式是 1.0 版，本來就支援） |
| 同一個專案第二次建置 | **3.6 秒** |
| 把整棵樹攤出來（取代目前那個只放改動檔的快照） | 這個專案 0.22 秒；工具鏈自己 0.70 秒（3534 檔）；mOrangePos 0.41 秒 |

**真正卡住的是快照的形狀**：閘複製出來的樹裡只有這次改動的檔，專案檔與其他原始碼都不在，`dotnet build` 根本起不來——不是它慢，是它沒東西可編。

**那為什麼不改成攤開整棵樹**：改了會動到其他棧，而且**不會讓事情變簡單**——

- 設定檔還是得強制從新版覆蓋。整棵樹會自然帶著基準版自己那份設定，兩側用不同規則比出來的差集沒有意義（這正是 `t_lint_config_from_head_only` 釘住的事）。
- 依賴目錄那層也還是要。攤樹只攤有進版控的檔，`node_modules` 不在裡面（實測確認）。
- 能跨檔解析的工具在完整的樹裡報出來的東西可能不一樣。兩側待遇相同、差集理論上仍成立，但**沒有實測**。

**Enzo 2026-09-13 裁：先不做。** 這一格由代碼審那條路徑覆蓋。
REVISIT:2026-12-13 若那時有 .NET 專案真的需要這道閘，把「攤開整棵樹」寫成設計稿走設計審。

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

- **安裝=`brew install detekt`**(套件管理器管生命週期)。⚠ 前科:KDS 曾把 detekt jar 放 `/tmp` 被系統清掉兩次(2026-07-17 首發、2026-07-27 重演,見 [[Systems/lint-declaration-health]])——外部工具一律裝進套件管理器,嚴禁易失位置。例外只有 compose-rules 的 detekt 外掛 jar:brew、sdkman 都沒有它的配方、二進位檔不進 repo,所以放本機固定目錄 `$HOME/.local/share/lumos/detekt-plugins/`(不是 `/tmp`),下載指令釘版本與 sha256(見下面推送前第二條)。
- **共用差分設定=`configs/detekt/android.yml`**(本 repo,隨 clone 分發):兩種差分。一是開 detekt 預設關但效能檢核目錄或 kotlin-idioms 點名的五條——`GlobalCoroutineUsage`(GlobalScope 裸用)/`SuspendFunSwallowedCancellation`(runCatching 裡呼叫 suspend=吞取消;try/catch 那型不抓)/`SuspendFunWithCoroutineScopeReceiver`(suspend 又掛在 scope 上)/`CouldBeSequence`(長鏈該 asSequence)/`ForbiddenMethodCall`(禁 `androidx.compose.runtime.collectAsState`,方法要寫全名、放 `style:`)。⚠ 兩層落差:①「有裝≠有開」——`--build-upon-default-config` 裸跑時這五條不開;②「有開≠有跑」(2026-11-04 實測)——除 GlobalCoroutineUsage 外都要型別資訊(`--classpath <依賴 jar>` 加 `--jdk-home <JDK>`),下面推送前那段樣板沒帶,所以它們在推送前安靜不跑、不報錯;要它們擋就照下面第二段「CI 型別檢查範本」接(detekt 官方建議的做法)。Kotlin 標準庫 2.2 以上時吞取消那條補了也不響(detekt 1.23.8 限制)。二是 detekt 官方 Compose 頁(https://detekt.dev/docs/introduction/compose/ )建議的六項放寬:`FunctionNaming` 對 `@Composable` 忽略、`TopLevelPropertyNaming` 常數允許 PascalCase、`LongParameterList` 忽略有預設值的參數、`MagicNumber` 忽略屬性宣告、`UnusedPrivateMember` 對 `@Preview` 忽略、`TooManyFunctions` 不算 `@Preview`——不加的話一支標準 Compose 檔會被內建規則報 6 條(2026-11-06 實跑,[[Projects/Android現成檢查接上CI與推送前_計劃]]);專案用多重預覽註解(例 `@PreviewLightDark`)時要自己把它加進 `UnusedPrivateMember` 的 `ignoreAnnotated`(這個鍵不看元註解)。設定檔的規則名與規則集有一支共用設定檢查測試擋錯(寫錯 detekt 整次拒跑;測試與判定表的家是 [[Systems/lint-declaration-health]])。
接法分兩段([[Projects/Android的detekt推送前真的擋_計劃]],2026-11-06):**推送前只擋不用型別資訊的規則**(GlobalScope 裸用、複雜度、命名這類),**要型別資訊的規則放在專案 CI 用 Gradle 型別解析任務加基準線擋**——detekt 官方提交前掛鉤那頁明寫「只跑改到的檔時,要型別資訊的檢查有些不準,CI 要另跑全量檢查」。

- **①推送前:lint.json 樣板**(新 Android 專案 setup 直接抄):
  ```
  detekt --input {LINT_FILES_CSV} --build-upon-default-config --config $HOME/harness/lumos-toolchain/configs/detekt/android.yml --report sarif:{LINT_SARIF_OUT}
  ```
  Compose 專案另加第二條,只跑 compose-rules 外掛規則(`--disable-default-rulesets`,內建規則照上一條跑):
  ```
  detekt --input {LINT_FILES_CSV} --disable-default-rulesets --plugins $HOME/.local/share/lumos/detekt-plugins/detekt-compose-0.4.28-all.jar --build-upon-default-config --config $HOME/harness/lumos-toolchain/configs/detekt/compose.yml --report sarif:{LINT_SARIF_OUT}
  ```
  外掛先下載到固定目錄並比對雜湊(sha256 是 2026-11-06 自算,官方沒公布;寫法跟本 repo CI 那一步同一個網址)。先下載成暫存檔,雜湊對了才改名成正式檔名,對不上就刪掉暫存檔——推送前那條命令每次都會載入這支 jar,不能留一支沒驗過的在正式位置:
  ```
  d="$HOME/.local/share/lumos/detekt-plugins"; mkdir -p "$d" && curl -sSfL -o "$d/detekt-compose-0.4.28-all.jar.part" "https://github.com/mrmans0n/compose-rules/releases/download/v0.4.28/detekt-compose-0.4.28-all.jar" && (cd "$d" && echo "b8c732880e9d26fac90f44733ecd9dab099e2abb1f597b76ceab29e676d4ddd6  detekt-compose-0.4.28-all.jar.part" | shasum -a 256 -c -) && mv "$d/detekt-compose-0.4.28-all.jar.part" "$d/detekt-compose-0.4.28-all.jar" || { rm -f "$d/detekt-compose-0.4.28-all.jar.part"; echo "下載或雜湊比對失敗,沒有裝"; false; }
  ```
  ★`--build-upon-default-config` 不能少★:少了它外掛規則一條都不跑、也不報錯(2026-11-06 實測)。外掛 0.4.x 對 detekt 1.23.x,0.5 起對 detekt 2.x(https://mrmans0n.github.io/compose-rules/detekt/ ),本機 detekt 升版時兩個一起換。外掛檔不在時 detekt rc 1、不產結果,新增告警閘把這一條判環境不可用、自動放行並記帳,上一條照擋;`lumos lint-check` 與健檢會印 A3。外掛自帶設定預設關的三條(`UnstableCollections`、`PreviewNaming`、`Material2`)在 `compose.yml` 寫明照預設不開。
  `{LINT_FILES_CSV}` 是給 detekt 用的逗號佔位符:新增告警閘把這次改到的 kt 檔用逗號串成一個值交給 `--input`(detekt 只收逗號分隔,用空白串的 `{LINT_FILES}` 兩支以上檔就拒跑),只擋這次新增的告警。別在它外面再包一對引號(換進去的值已經加過 shell 引號;`lumos lint-check` 會記成格式問題)。路徑含逗號或分號的檔 detekt 收不了:閘把它從這條命令拿掉、列進「沒檢查」並擋下,改檔名或照擋下訊息印的指令放行;檔多到命令換完超過 100,000 位元組時自動分批跑。`$HOME` 可用:lint 命令走 shell 執行。
- **②CI 型別檢查範本**(專案自己貼進它的 CI;lumos 不執行 Gradle、不改專案的檔):
  1. 專案的 Gradle 套 detekt 外掛(版本跟本機 CLI 同一版,1.23.8),設定指共用設定:
     ```kotlin
     plugins { id("io.gitlab.arturbosch.detekt") version "1.23.8" }
     detekt {
         buildUponDefaultConfig = true
         config.setFrom(files("<共用設定 android.yml 的路徑>"))   // CI 上要先 clone 工具鏈,或把這份複製進專案
         baseline = file("config/detekt/baseline.xml")
     }
     ```
     **AGP 9 預設的內建 Kotlin 下,1.23.8 不產按變體任務**(只有 `detekt`、`detektBaseline`;1.23.8 只在套了 `kotlin-android` 外掛時建型別任務、用舊介面讀變體,https://github.com/detekt/detekt/issues/8320 ;2026-11-09 nowinandroid 實測,[[Verification/2026-11-09_Android現成檢查範本在兩個公開專案實跑]])。已遷到內建 Kotlin 的專案改用 detekt `2.0.0-alpha.6`:
     ```kotlin
     plugins { id("dev.detekt") version "2.0.0-alpha.6" }   // 2.0 改了外掛代號;detekt { } 區塊寫法同上
     dependencies { detektPlugins("io.nlopez.compose.rules:detekt:0.6.8") }   // compose-rules 0.6.4 到 0.6.8 對 detekt 2.0.0-alpha.6
     ```
     - `gradle.properties` 加 `android.disallowKotlinSourceSets=false`:detekt 支援內建 Kotlin 那次改動原文要求(https://github.com/detekt/detekt/pull/9100 ),沒設時 2.0 一樣只有兩個任務;AGP 會印「實驗性選項」警告,照常。
     - 共用設定 android.yml 的 `UnusedPrivateMember:` 那一鍵在 2.0 不存在(拆成 `UnusedPrivateFunction` 等),複製進專案後改成 `UnusedPrivateFunction:`,不然設定檢查直接讓任務失敗。共用設定本身照舊用 1.23 的鍵名,因為推送前那條用的本機 CLI 是 1.23.8。
     - 2.0 還是 alpha,型別規則在內建 Kotlin 下讀不到 BuildConfig、R 這類產生的類別,可能誤報(detekt 議題 #9402);誤報先進基準線。
     - 退回舊模式(`android.builtInKotlin=false`、`android.newDsl=false`)對已遷移的專案不可行:每個模組要補套 `kotlin-android`,nowinandroid 的建置外掛直接失敗;這兩個旗標 AGP 10 也會移除。
  2. 第一次在本機跑 `./gradlew detektBaseline<變體>`(例 `detektBaselineDebug`)產基準線檔、提交(2026-11-08 實測 detekt 1.23.8:變體任務在 `baseline` 設的檔名後面自動加變體名,上面那樣設會寫成 `config/detekt/baseline-debug.xml`,`detektDebug` 也讀這支;要提交的是它)。要清舊帳時重產。
  3. CI 加一步 `./gradlew detekt<變體>`(例 `detektDebug`;純 Kotlin 模組是 `detektMain`):有基準線以外的新告警就讓 CI 失敗。這一步才有型別資訊,InjectDispatcher、吞取消、`collectAsState` 這類規則在這裡擋。要寫明這個任務名:`./gradlew check` 只帶不吃型別資訊的 `detekt`,不帶 `detekt<變體>`(2026-11-09 AGP 8.7.3 與 9.3.2 兩個專案 `check --dry-run` 實測)。
  - Compose 專案在 `dependencies` 加 `detektPlugins("io.nlopez.compose.rules:detekt:0.4.28")`,CI 這步也帶 compose-rules;外掛的設定照推送前那條指 `compose.yml`(`config.setFrom(files("<android.yml>", "<compose.yml>"))`)。
  - 沒貼的專案,`lumos lint-check` 與健檢會印 T4「型別規則目前哪裡都沒擋」(只看 `.github/workflows/` 字面有沒有 `detekt<變體>`,不驗它真的跑)。

- **這個樣板拿不到型別資訊**(2026-11-01 用 detekt 1.23.8 實測,[[Projects/Kotlin慣例對齊Android官方與本機detekt_計劃]]):只給 `--input` 時,detekt 那批「要型別資訊」的規則一條都不報、也不出錯——kotlin-idioms 點名的協程規則裡只剩 `GlobalCoroutineUsage` 會報;共用設定開的五條裡,除 `GlobalCoroutineUsage` 外四條(`SuspendFunSwallowedCancellation`、`SuspendFunWithCoroutineScopeReceiver`、`CouldBeSequence`、`ForbiddenMethodCall`)都在這批裡,照樣板跑只有 `GlobalCoroutineUsage` 有效。同一份樣本帶上 `--classpath`(協程與標準庫 jar)和 `--jdk-home` 之後,`ForbiddenMethodCall`、`InjectDispatcher`、`RedundantSuspendModifier`、`SuspendFunWithFlowReturnType`、`SleepInsteadOfDelay`、`CouldBeSequence` 都會報;`SuspendFunSwallowedCancellation` 只抓 `runCatching` 包 suspend 呼叫,`try/catch(Exception)` 吞取消帶齊型別資訊也不報。Android 專案的 classpath 要靠 Gradle 才組得出來,所以這些規則走上面第②段的 CI 型別檢查範本,不在推送前硬組 classpath(設計審兩輪實測:參數檔不存在、路徑含空白、flavor、CI 沒有建置產物,每一種都讓閘不是靜默放行就是恆擋)。
  `lumos lint-check` 與健檢會照指令字面印出這些提醒(判定表見 [[Projects/Android的detekt規則說實話_計劃]]):沒有檔案佔位符的印 P1(只記錄不擋)、帶舊 `{LINT_FILES}` 的印 P2(改用 `{LINT_FILES_CSV}`)。
- 自有設定要跟共用設定疊加:用逗號合成一個 `--config a.yml,b.yml`(分開寫兩次 `--config` 會拒跑);清單類欄位(例 ForbiddenMethodCall 的 methods)後面那份整份蓋掉前面那份,不合併、不警告。
- 接完跑 `lumos lint-check --smoke` 驗宣告真跑得動(這正是抓到 /tmp jar 蒸發的守衛);冒煙只驗有沒有產出結果,不驗規則有沒有響。

### Android Lint 與 Compose lint 標準接法(2026-11-06 立,[[Projects/Android現成檢查接上CI與推送前_計劃]])

Android Lint 官方只支援在 Gradle 專案用 `./gradlew lint` 跑整個模組(單機版 lint 對 Gradle 專案會報錯,https://developer.android.com/studio/write/lint ),推送前不跑;放在專案 CI 用基準線擋新增(官方也建議「把 lint 明確放進 CI」)。Slack compose-lints 掛在 Android Lint 上,同一步跑。lumos 不執行 Gradle、不改專案的檔,下面是給專案自己貼的範本。

1. 模組層 `build.gradle.kts`:
   ```kotlin
   android {
       lint {
           baseline = file("lint-baseline.xml")
           warningsAsErrors = true      // 不開時只有 error 級會讓建置失敗;型錄的 Android Lint 列多半是 warning 級
           checkDependencies = true     // app 連同函式庫模組一起查(官方建議)
           sarifReport = true
       }
   }
   dependencies {
       lintChecks("com.slack.lint.compose:compose-lint-checks:<版本>")
       lintChecks("com.android.security.lint:lint:1.0.4")
   }
   ```
   Slack 外掛版本要對 AGP:挑「建置用的 lint 版本不高於專案 lint 版本」的那版,lint 版本等於 AGP 版本加 23(1.5.5 的發行說明同時寫 lint 32.3.2 與 AGP lint plugin 9.3.2)。常見對照:AGP 9.4.1 以上用 `1.6.1`(lint 32.4.1);AGP 9.3.2 到 9.4.0 用 `1.5.5`(lint 32.3.2);AGP 9.2.1 到 9.3.1 用 `1.5.0`(lint 32.2.1);AGP 8.7.1 到 9.2.0 用 `1.4.2`(lint 31.7.1);AGP 8.7.0 用 `1.4.0`(發行說明寫 Build against Lint 8.7.0,即 lint 31.7.0);更舊的照發行說明挑(https://github.com/slackhq/compose-lints/releases )。表只是常見對照,邊界一律照「建置用 lint 版本不高於專案 lint(= AGP 加 23)」挑;1.4.3 的發行說明沒寫建置用 lint 版本,只列一串依賴更新的 PR 標題(lint-api 從 31.7.2 一路升到 32.2.0、lint 外掛升到 9.2.0,另一則寫 lint 31.13.2),看不出最後用哪版建置,不列。版本不合時 lint 任務載不進外掛。Slack 預設關的規則範本不開:`ComposeM2Api` 各版都預設關;`ComposeUnstableReceiver`、`ComposeUnstableCollections` 從 1.5.2 起才預設關(Slack 的理由:強跳過模式下穩定性檢查沒那麼重要,https://github.com/slackhq/compose-lints/pull/541 ),1.5.1 以前預設開(2026-11-09 AGP 8.7.3 專案配 1.4.2 實跑,基準線裡有 `ComposeUnstableCollections`)。用 1.5.1 以前的版本又想跟新版一致,在 `lint { disable += setOf("ComposeUnstableReceiver", "ComposeUnstableCollections") }` 關。
   第二行 `lintChecks` 是 Google 的 Android 資安規則包(2026-11-08 加,[[Projects/Android資安與崩潰靜態檢查補齊_計劃]];官方 README https://github.com/google/android-security-lints ,版本查 Google Maven https://dl.google.com/android/maven2/com/android/security/lint/lint/maven-metadata.xml ,當天最新 1.0.4):官方自己說它比內建檢查「更偏資安、也更實驗性」(more security-focused and experimental),可能誤報。版本規則跟 Slack 外掛同一條:1.0.4 的建置檔寫 `lintVersion = '31.5.1'`,換算要 **AGP 8.5.1 以上**。第一次接一樣照第 2 步先產基準線;**已經照範本接過 CI 的專案**加這一行時,要先刪掉 `lint-baseline.xml`、照第 2 步重產並提交再推,不然舊程式的資安告警會讓 CI 立刻紅。包裡 24 條檢查都登記在 Kotlin 寫法型錄 checks-catalog.md(家在 [[Systems/kotlin規則包]];現成規則欄寫 `資安包:<檢查 id>`),專案要關哪一條,照型錄的檢查 id 在 `lint { disable += "<id>" }` 關。
2. 第一次在本機跑 `./gradlew lint<變體> -Dlint.baselines.continue=true`(例 `lintDebug`)產 `lint-baseline.xml`、提交。**先產基準線、提交,再做第 3 步**——反過來 `warningsAsErrors` 會讓舊專案一接就紅。要清舊帳時刪掉基準線檔重產。
3. CI 加一步 `./gradlew lint<變體>`(或 `./gradlew check`,AGP 讓 `check` 帶 `lint<預設變體>`;2026-11-09 AGP 8.7.3 與 9.3.2 實測都掛上):有基準線以外的新告警就讓 CI 失敗。
- 沒接的專案,`lumos lint-check` 與健檢會印 A1(CI 設定檔裡都找不到 Android Lint 的跡象:lint 任務名,或跟 `gradlew`、`gradle` 寫在同一邏輯行(反斜線續行接起來算一行)的 `check`、`build`,或 Azure `tasks:`、gradle action 的 `arguments:`、Bitrise 的 `gradle_task:` 這三個欄位值裡的 `check`、`build`(CircleCI 的 `command:` 是通用欄位、不算,gradle orb 的 `command: build` 會多印);建置檔的 `lint { }` 區塊與 `lint-baseline.xml` 是第 1、2 步的痕跡,不算 CI 有跑;只看字面,找到一個就不印,找不到不代表一定沒跑)、A2(用 Compose 但 Slack compose-lints 與 compose-rules 兩套都沒接);宣告的 detekt 命令帶的外掛檔不在時印 A3(見上面 detekt 標準接法)。只看字面(A1 看 CI 設定檔、A2 看建置檔、A3 看宣告),不驗 CI 真的跑。

### Kotlin 寫法規則包標準接法(2026-11-05 立,[[Projects/Android協程與API寫法機械檢查標準_計劃]])

規則包本體、每條規則對應型錄哪一列、自我檢查怎麼跑,家在 [[Systems/kotlin規則包]];這裡只放宣告範本。

- **安裝**:`pipx install ast-grep-cli==0.51.1` 或 `brew install ast-grep`(要 0.51.1 以上;規則包用到的語法以 0.51.1 為準)。CI 要先裝同一版並 clone 工具鏈。沒裝時新增告警閘判環境不可用、照既有規則放行並記帳(看得到但不擋)。
- **`.lumos/lint.json` 樣板**(Kotlin 專案直接抄,跟 detekt 那條並列):
  ```
  {"kt": ["ast-grep scan --config $HOME/harness/lumos-toolchain/configs/ast-grep/kotlin-android/sgconfig.yml --format sarif {LINT_FILES} > {LINT_SARIF_OUT}"]}
  ```
  這條帶 `{LINT_FILES}`,ast-grep 收空白分隔的多支檔,推送前的新增告警閘會真的跑、只擋這次新增的告警;每條告警訊息開頭是型錄編號(例 `[API-15]`),後面是一句修法,完整寫法用編號查 `skills/kotlin-idioms/checks-catalog.md`。
- **提示級規則預設不接**:`sgconfig-hints.yml` 是誤報可能較高的提示級規則,新增告警閘不分等級、接了就擋;要用就另加一條宣告指向它,並自己承擔誤報。
- **測試檔也要掃**:型錄 TEST 主題的規則只在 `src/test/`、`src/androidTest/` 底下響,而新增告警閘預設排除 `src/test/`;要掃就在 `.lumos/config.json` 寫 `{"lint_new": {"include_test_paths": ["kt"]}}`。開了以後其他宣告命令(例如 detekt)也會掃到測試檔,可能多出對測試碼的告警(只擋新增的)。
- **路徑過濾的天花板**:規則包裡「只掃測試碼」的規則錨在 `**/src/test*/**` 這類片段;專案本身放在名為 `src/test` 的目錄底下時會反轉(ast-grep 的路徑過濾相對於規則設定檔所在目錄)。

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

## React（registry: `npm:<pkg>`；2026-10-15 補，[[Projects/前端框架從vue分出_計劃]]，消費端 order-web）

| 工具 | 抓什麼 | 備註 |
|---|---|---|
| **eslint-plugin-react-hooks** | `rules-of-hooks`（Hook 只能在頂層呼叫）、`exhaustive-deps`（effect 依賴陣列漏值） | `npm:eslint-plugin-react-hooks`；★2026-10-15 在 order-web 用 eslint 9.39.5＋5.2.0 實跑，兩條各對違規樣本報一條★；recommended 裡 exhaustive-deps 只是 warning，建議升成 error（react-idioms R5） |
| **eslint-plugin-react** | `react/jsx-key`（清單沒 key）、`react/no-array-index-key`（用索引當 key） | `npm:eslint-plugin-react`；未實跑（order-web 沒裝） |
| **typescript-eslint** | type-aware 的 `no-floating-promises`、`no-misused-promises` | 同 Node 段；React 的事件處理常把 async 函式丟給 onClick |
| **eslint-plugin-react-refresh** | 熱更新邊界（`only-export-components`） | Vite 範本預設會裝；不是正確性規則 |

接法:SARIF 走 `@microsoft/eslint-formatter-sarif`(同 Node 段);專案根目錄有 eslint 設定而沒宣告 `.lumos/lint.json` 時,`lumos doctor` 的 [F] 段會印可貼的範本(見 [[Systems/lint-declaration-health]])。

## SQL（registry: `pypi:<pkg>`）
| linter | 用途 | 備註 |
|---|---|---|
| **sqlfluff** | 多方言(含 T-SQL)靜態解析 + auto-fix,免連 DB | LandmarkMember/KDS 的 `.sql` 適用;經 `lumos sqlfluff-sarif` 橋接進 lint-adapter |

## Flutter/Dart（registry: `pub:<pkg>`；2026-07-26 補，taroko_app 接入調研）

- **flutter_lints**（官方推薦基線,Effective Dart 對齊）→ 進階嚴格版 **very_good_analysis**（企業級,強制 const/顯式型別）。
- **custom_lint**:自建規則框架(riverpod_lint 等生態基座)。**DCM**:複雜度/程式碼度量(商用)。
- **架構軸(import 邊界,Dart 3.10+ 才可用)**:`import_rules`(2026/02,YAML 宣告 import 約束進 dart analyze)｜`import_lint`(2026/04)｜`barrel_file_lints`(feature 分層/barrel 規則)。
- ⚠ **SDK 門檻實錘(taroko_app)**:Dart 2.19(pre-Dart 3)上述架構套件與新版 VGA 全裝不了——舊 SDK 專案的架構軸=升級 Flutter 後解鎖;過渡期用 analysis_options 手開嚴格規則(零依賴不受版本卡)。
- **Check T**:dart profile 已內建(test('名')/testWidgets('名') 標題整串比對(2026-10-15 起收句子名,見 [[Projects/測試名收自由字串_計劃]])+*_test.dart 檔名錨)——Dart 測試可正式綁 [test:] 走合約鏈。
- SARIF 橋:`dart analyze` 無原生 SARIF → 2026-09-14 起用 `lumos dart-sarif` 轉(`dart analyze --format=json {LINT_FILES} 2>/dev/null | python3 scripts/lumos dart-sarif --out {LINT_SARIF_OUT}`),Dart 3.13.3 實跑過閘。

## Swift/iOS（registry: `github:<owner>/<repo>`；2026-09-08 補，★尚無 Swift 消費端，未實裝跑過★）
| linter | 用途 | 備註 |
|---|---|---|
| **SwiftLint** | 風格＋最佳實踐（200+ 規則，含 force_unwrap/force_try/implicitly_unwrapped 等安全類與 cyclomatic_complexity） | `github:realm/SwiftLint`；★內建 `swiftlint --reporter sarif --output <檔>`★，可直接進 `.lumos/lint.json`；已知 SARIF 小坑：uri 曾輸出絕對路徑、startColumn 型別（issue #5698/#5699），接進去先拿一份 SARIF 對照 diff 行號對不對 |
| **SwiftFormat**（或 Apple **swift-format**） | 格式；二選一 | `github:nicklockwood/SwiftFormat`；swift-format 自 Swift 6 隨 toolchain 附帶，零安裝但規則少 |
| **Periphery** | 死碼（未用的型別/函式/參數；SwiftPM 與 Xcode 專案都吃） | `github:peripheryapp/periphery`；社群公認 Swift 死碼首選；輸出格式為 xcode/json/csv，無 SARIF→要進 lint.json 得自寫小橋（同 sqlfluff-sarif 模式），未做 |
| Xcode 內建 **Static Analyzer**／**Strict Concurrency**（`-strict-concurrency=complete`） | 併發軸主力：資料競爭、Sendable 違規在編譯期抓 | 隨 toolchain；不是獨立 linter，但 Swift 6 語言模式把大半「idioms 不可機檢」條目變成編譯錯誤——新專案優先開 |
| Harmonize | 架構 lint（見下方架構 lint 品類） | 已列 |

**SwiftPM 沒有中央 registry**：依賴就是 git repo，所以 lint-watch 對 Swift linter 一律用 `github:<owner>/<repo>` 盯 release（既有 kind，不用加）。CocoaPods 專案的 Podspec 版本目前**沒有** registry 種類支援，要盯得自己看。

## Node.js / TypeScript 後端（registry: `npm:<pkg>`；2026-09-08 補，★2026-09-13 eslint 真的裝起來、在推送前的新增告警閘裡端到端跑通；消費專案仍零接入★）
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

## Python（registry: `pypi:<pkg>`；2026-09-11 補，★首個消費端＝自動交易專案建置中，尚未實跑★）

輸出格式全部在本機實跑 `--help` 核對（ruff 0.16.7、bandit 1.x、mypy 2.3.1、ty 0.0.80、pip-audit 2.10.1）。

| linter | 用途 | 備註 |
|---|---|---|
| **ruff** | 基石：lint＋format 一支包辦（取代 flake8／isort／pyupgrade／black 大半）；async 紀律（`ASYNC` 族）、懸空 task（`RUF006`）、requests 無逾時（`S113`）、Decimal 用 float 建（`RUF032`）、naive datetime（`DTZ`）都靠它 | `pypi:ruff`；★內建 `--output-format sarif`★，直接進 `.lumos/lint.json`：`{"py": ["ruff check --output-format sarif -o {LINT_SARIF_OUT} src"]}`；⚠ 預設只開 `E`／`F`，其他族要在 `select` 明確開（清單見 python-idioms 接線表） |
| **mypy** | 型別檢查（`strict = true`）；外部輸入邊界、`Any` 擴散、None 沒處理 | `pypi:mypy`；★無 SARIF★（`--output json`），當 CI 閘，不進 lint.json |
| ty | Astral 出的新型別檢查器（Rust，快） | `pypi:ty`；0.0.x 仍在 beta，輸出只有 full／concise／gitlab／github，★無 SARIF★；生態雷達，先不當主力 |
| **bandit** | 資安：pickle、shell=True、寫死密碼、弱雜湊 | `pypi:bandit`；裝 `bandit[sarif]` 才有 `-f sarif`；與 ruff 的 `S` 族大量重疊，二擇一或 bandit 只跑 CI |
| pip-audit | 依賴已知漏洞（PyPI 漏洞資料庫） | `pypi:pip-audit`；★無 SARIF★（json／cyclonedx／markdown），CI 報表 |

**跟 SQL 段的關係**：registry 同是 `pypi:`（sqlfluff 也住 PyPI），lint-watch 盯版本走同一種座標。

## Java／JVM（registry: `maven:<group>:<artifact>`；2026-09-12 補，★2026-09-13 PMD 與 Checkstyle 都裝起來實跑通，兩支都不需要 Maven／Gradle；消費專案仍零接入★）

跟其他段最大的差別：**這一段的工具全部要靠建置系統才跑得起來**（Maven 或 Gradle 的 plugin，或編譯器外掛），沒有像 `ruff`／`eslint` 那種裝了就能單獨敲的 CLI。所以下表的接法是照官方文件寫的，等第一個 Java 消費端出現時要實際裝一次再回填。

| linter | 用途 | 備註 |
|---|---|---|
| **Error Prone** | 基石：Google 出的**編譯期**檢查，跟 javac 一起跑，錯的直接編不過 | `maven:com.google.errorprone:error_prone_core`；抓 `FutureReturnValueIgnored`（Future 回傳值被丟掉＝例外無聲蒸發）、`EqualsHashCode`、`GuardedBy` 等；★不用另外接進 lint.json，它在編譯那關就擋★ |
| **SpotBugs** | 讀 bytecode 找 bug 樣式：資源沒關（`OBL_UNSATISFIED_OBLIGATION`）、迴圈裡相接字串（`SBSC_USE_STRINGBUFFER_CONCATENATION`）、同步不一致 | `maven:com.github.spotbugs:spotbugs`；有 SARIF 輸出，可進 `.lumos/lint.json` 的 `"java"` 鍵 |
| **PMD** | 讀原始碼找規則違反：`CloseResource`、`AvoidInstantiatingObjectsInLoops`、`AvoidCatchingGenericException` | `maven:net.sourceforge.pmd:pmd-core`；規則集要自己挑，預設全開會很吵 |
| NullAway | Error Prone 的外掛，做空值分析（要先標註哪些套件納管） | `maven:com.uber.nullaway:nullaway`；編譯期 |
| Checkstyle | 排版與命名風格 | `maven:com.puppycrawl.tools:checkstyle`；跟前三支重疊少，但價值也低——排版問題交給格式化工具 |

**跟 Kotlin/Android 段的關係**：registry 同樣走 `maven:` 與 `google-maven`（版本盯法完全一樣）。混編專案（Kotlin＋Java 舊碼）兩段都要裝：detekt 只看 `.kt`，SpotBugs／PMD 只看 Java。

`.lumos/lint.json` 的鍵就是副檔名，所以接 Java 不用改任何程式：

```json
{"java": ["./gradlew spotbugsMain -PsarifOut={LINT_SARIF_OUT}"]}
```


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

AST 級結構比對（比 regex 誤報少、表達力強），多語言單一引擎；CodeRabbit 以它為底層、官方供 `llms.txt` 讓 LLM 寫規則。**用途定位**：pitfalls 的事故 pattern 從手刻 regex 升級 AST 規則——事故再犯的固化路徑。接法＝既有 `.lumos/lint.json` SARIF 橋（外部 linter，不碰零依賴家規）。誠實：官方自認 AI 生成規則錯誤率仍高，規則要配自我修正迴圈、上線前人過目。(更正 2026-10-12:官方只說 AI 寫規則容易幻覺、要靠驗證迴圈,沒有「錯誤率仍高」或任何數字;2025-06-21 官方部落格反而說加上驗證迴圈後三家模型表現很好,見 https://ast-grep.github.io/blog/ast-grep-agent.html)

## 誠實邊界
- 這是 2026-07 快照,linter 生態變動快(oxlint/Biome 仍在成熟弧上;Swashbuckle 這類已被 .NET 內建 OpenAPI/Scalar 挑戰)——`valid_under` 記為「2026-07 社群現況」,半年後宜重搜。
- REVISIT:2027-01-31 重搜 linter 生態(半年快照到期;上行條款)
- 「該裝哪些」是團隊決定,此菜單只列社群共識選項,不強制;裝了才進 lint.json/lint-watch.json。
- registry 座標須與 [[Systems/lint-version-watch]] 支援的 type 對齊(nuget/npm/pypi/github/maven/google-maven);detekt/ktlint 走 github release(maven artifact 亦可)。

## 跨語言的社群規則庫與依賴掃描（2026-09-13，[[Projects/社群規則第二批_計劃]]）

> 這兩個跟上面各語言的 linter 不同：**一個工具吃很多語言**，而且是「社群把經驗寫成規則」的主要載體。兩者都原生吐 SARIF，所以接法跟其他 linter 完全一樣。

| 工具 | 用途 | 座標 | 實測（2026-09-13） |
|---|---|---|---|
| **semgrep** | 跨語言的社群規則庫；規則本身是一小段模式比對，自己也寫得出來 | `pypi:semgrep` | 1.177.0；不用登入可用（`p/python` 151 條規則、含下載約 2 秒）；登入才有更多免費規則 |
| **OSV-Scanner** | 依賴層：已知漏洞與捏造的套件版本，11+ 生態系 | `github:google/osv-scanner` | **未實跑**（只查過官方文件）；已知限制：SARIF 嚴重度一律標 warning，不能用嚴重度分級 |

**怎麼宣告給工具鏈用**：見 [[Systems/pitfalls-lint-adapter]]（程式碼與依賴層各有自己的宣告檔，格式與佔位符都寫在那裡）。

**三個實測踩到的坑**：

- **沒有副檔名的檔在「掃目錄」時被靜默跳過**（工具鏈自己的主程式就是這種檔）。明確把檔名當參數傳就會掃——所以宣告一定要帶檔案清單佔位。
- **速度是超線性的**：843 行的檔 1.8 秒，26718 行的主程式 105 秒。新增告警閘會跑兩次，所以單檔大小上限是必要配套。
- **首次真跑，唯一一條命中是誤報**：對一個刻意設 0700 的快取目錄建議改成 0644（更不安全）——規則是為檔案寫的卻套到目錄。誤報用 `lumos lint-waive` 放行。

**自己寫規則**：把事故或網搜補漏抓到的坑固化成規則的做法（規則放哪、樣本怎麼擺、怎麼驗它真的翻紅）見 [[Systems/pitfalls-lint-adapter]]。

