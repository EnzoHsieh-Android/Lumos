---
type: verification
status: pass
date: 2026-07-05
valid_under: "dotnet/Roslyn ErrorLog 吐 SARIF v1.0(tool.name/resultFile.uri/message 字串);NuGet flatcontainer index.json {versions:[...]} 形狀"
revalidate_when: "dotnet SARIF 版本預設改 / NuGet API 形狀改 / _lint_run_and_parse 或 _registry_latest 契約改"
tags:
  - type/verification
  - status/pass
related:
  - "[[pitfalls-lint-adapter]]"
  - "[[lint-version-watch]]"
summary: |-
  TEST:test_lumos.py 494 passed(t_lint_sarif_v1/t_lint_watch_nuget/t_lint_runner_stdout_isolation 新增);C# 全面覆蓋對齊 Android
  VERIFY:LandmarkMember(/Users/enzo/backend/LandmarkMember,net9.0 多專案後端)真機——nuget 版本偵測 + dotnet SARIF v1 lint-adapter 端到端
---
# 2026-07-05 C# / Landmark 真機驗證

把 pitfalls 偏科層(lint-adapter + lint-version-watch)擴到 C#/.NET,對齊 Android 的全面度。對 LandmarkMember(net9.0 多專案後端)真機驗證。

## 補的 lumos 能力(2026-07-05,均真機驅動)
1. **lint-adapter 支援 SARIF v1.0**:dotnet/Roslyn `ErrorLog` 預設吐 **v1**(非 v2.1)——`tool.name`(非 `tool.driver.name`)、`locations[].resultFile.{uri,region}`(非 `physicalLocation.artifactLocation`)、`message` 為**字串**(非 `message.text`)。`_lint_run_and_parse` 以 `version` 欄位判別 v1/v2.1、共用 uri 正規化。
2. **lint-watch nuget registry type**:`nuget:<PackageId>` → flatcontainer `index.json` `{"versions":[...]}` 過濾 prerelease 數值 max(id 小寫)。
3. **linter stdout 隔離(真 bug 修)**:dotnet 警告走 **stdout**,原 `_lint_run_and_parse` 繼承 fd → 洩漏污染 lumos `--json`(detekt 走 stderr 僥倖沒事)→ `Popen` 加 `stdout/stderr=DEVNULL`(SARIF 走檔案、console 非契約)。

## Landmark 真機結果
- **lint-watch(nuget,真 API)**:ClosedXML 0.104.2→0.105.0、Dapper 2.1.66→2.1.79、Swashbuckle 6.9.0→10.2.3、xunit 2.9.2→2.9.3、Microsoft.Data.SqlClient 6.1.3→7.0.2 正確偵測落後;StyleCop.Analyzers 1.1.118 判穩定(非 1.2.0-beta);checked=6、failed=[]。
- **lint-adapter(dotnet SARIF v1,e2e)**:`.lumos/lint.json` `cs` 棧跑 `dotnet build Shared -p:ErrorLog={LINT_SARIF_OUT} -p:AnalysisMode=All -t:Rebuild` → 產 v1 SARIF(77 findings)→ lint-adapter 解析、**座標系對齊過濾**:注入一行(CA1051+CA1805 在 line 5)→ manifest **只留該行 2 條**、其餘 75 過濾掉。stdout 修後 `--json` 乾淨。

## C# 適配結論(對齊 Android 全面度)
- **SARIF linter**:dotnet 內建 Roslyn/NetAnalyzers(`-p:AnalysisMode=All`)已可;加 StyleCop.Analyzers/Roslynator/SonarAnalyzer.CSharp(NuGet)更全面——皆走 `dotnet build -p:ErrorLog` 出 SARIF v1 → lint-adapter 吃。
- **版本偵測**:NuGet(nuget type)。
- **偏科工具**:C# 無 Compose,無 compose-metrics 類編譯器 metrics 對應;全面 = 多 analyzer SARIF + nuget 版本偵測。

## 測試
`scripts/test_lumos.py` 494 passed;新增 `t_lint_sarif_v1`(v1 shape 解析 + location-less 跳)、`t_lint_watch_nuget`(beta 過濾穩定 max + 全 beta→no stable)、`t_lint_runner_stdout_isolation`(child stdout 不洩漏)。

## 併發/死鎖 + T-SQL 真機驗(2026-07-05 追加)
- **VSTHRD(C# async 死鎖/併發,Roslyn analyzer)**:Landmark Server build → 144 finding,含 **35× VSTHRD103**(sync-over-async 阻塞=死鎖/執行緒池飢餓風險,真 debt);注入 `.Result` probe → pitfalls manifest 抓到 **VSTHRD002「may cause deadlocks」+VSTHRD104**、tier high。走 Roslyn→SARIF v1→lint-adapter,零新工作(加 NuGet + `.editorconfig` 調噪音)。詳 Landmark Issue。
- **T-SQL(sqlfluff)**:Landmark 65 .sql 檔;`sqlfluff lint --dialect tsql --format json` → **`lumos sqlfluff-sarif`** 橋接 SARIF → lint-adapter;注入行 → 14 claim(AM04/CP01/CP02/LT05)進 manifest source=lint:sqlfluff、對齊過濾只留該行。
- **抓不到的(誠實)**:N+1(Dapper raw SQL,執行期 profiling)、鎖順序/SQL 死鎖(執行期 deadlock graph)——非靜態 lint 範疇。

## 天花板
- dotnet SARIF 版本預設是 v1(`,version=2.1` MSBuild 傳遞不穩,故 lumos 直接支援 v1 較穩健)。
- lint.json 若用 `dotnet build` 每次 pitfalls --diff 都會 build(慢)→ pre-push advisory 用 `--no-lint` 略過;深掃留終審/CI。
- Landmark 的 `.lumos/lint.json` 用單專案 Shared + AnalysisMode=All(示範);真整合可指 solution 或加 StyleCop/Roslynator。
