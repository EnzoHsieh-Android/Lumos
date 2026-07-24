---
type: system
status: doing
created: 2026-07-04
updated: 2026-07-04
self_audit: sonnet/2026-07-24
tags:
  - type/system
  - status/doing
related:
  - "[[pitfalls-code-loop]]"
  - "[[lumos-refcheck]]"
  - "[[pitfalls-lint-integration_計劃]]"
summary: |-
  FLOW:偵測 diff 涉及棧(去點副檔名對 .lumos/lint.json key)→ 跑該棧宣告的 lint 指令(各輸出 SARIF、per-command temp)→ 解析合併 SARIF → 對齊則過濾到 diff 觸及行/非對齊降級全收 → 併進 pitfalls --diff manifest 餵 reviewer/code-loop
  KEY:核心定位——lumos 只解 SARIF 一種格式(stdlib json)、不內建任何棧規則、不裝/管 linter;規則庫讓給社群 linter(composition over invention)
  KEY:向後相容(回歸釘)——無 .lumos/lint.json → regex-only 輸出 byte-for-byte 不變、不加 lint_ran/lint_skipped 鍵;config=None 走既有 return 早退,manifest shape 不動
  KEY:uri 正規化(KDS tracer 坐實 detekt 吐絕對 file:///)——剝 file:// + urllib.parse.unquote + 有 uriBaseId 拼 run.originalUriBaseIds[base] + 僅 isabs 才 os.path.relpath(repo_root)(相對 uri 直用,避免 ../.. 誤 drop) + 反斜線轉正斜線
  KEY:runner 承重——per-command tempfile.mkstemp + shlex.quote 注入 {LINT_SARIF_OUT} + Popen(shell=True,cwd=repo_root,start_new_session=True) communicate(timeout=LINT_CMD_TIMEOUT=180) 逾時 os.killpg 整組 + finally os.unlink;rc≠0 且無可解析 SARIF 才算失敗記 lint_skipped(detekt 333 issues exit 非零仍產 SARIF)
  KEY:SQL/T-SQL 橋接——sqlfluff(無原生 SARIF)經 `lumos sqlfluff-sarif`(讀 --format json → SARIF v2.1)進 lint-adapter;專案 .lumos/lint.json 的 sql 棧宣告(Landmark 65 .sql 真機驗)。Dapper 的 C# 內嵌 SQL 非檔案、linter 看不到(天花板)
  KEY:SARIF v1.0 也支援(2026-07-05,dotnet/Roslyn ErrorLog 預設吐 v1:tool.name/resultFile.uri/message 字串;version 欄位判別 v1/v2.1)+ linter console 輸出 DEVNULL 隔離(dotnet 警告走 stdout,不可污染 --json;Landmark 真機暴露)
  KEY:SARIF 迭代容錯——results optional(run.get('results') or []);per-run tool.driver.name 用 .get() 鏈缺則跳該 run 不連坐;單筆 location try/except 空跳該 finding 不連坐整 run
  KEY:座標系對齊——added 行集合僅由 diff + 行構成;對齊=右端 ref(rsplit '...' 後 rsplit '..')rev-parse==HEAD 且 git status --porcelain 空;非對齊或判定失敗→降級全收不過濾、manifest 標 filtered:false、不升 rc
  KEY:manifest claim——lint claim {file,line,source:"lint:<driver>",rule,message}(讀 message 非 question);regex claim 補 source:"pitfalls-builtin" 保留 class/pattern/question;--json 增 lint_ran/lint_skipped
  DEP:[[pitfalls-code-loop]]
  DEP:[[lumos-refcheck]]
  TEST:12+ 案 test_lumos.py(t_lint_aligned/t_lint_config/t_lint_sarif/t_lint_sarif_malformed_run/t_lint_sarif_relative_uri/t_pitfalls_lint_integration);全套件 412 passed
  VERIFY:[[Verification/2026-07-04_pitfalls-lint-adapter]]
  DECISION:[2026-07-04]吃社群 linter(SARIF 整合)不自建規則庫(valid);[2026-07-04]無宣告 regex-only byte-for-byte 不變(valid)
verified_by:
  - "[[Verification/2026-07-04_pitfalls-lint-adapter]]"
  - "[[Verification/2026-07-05_csharp-landmark-verify]]"
---
# pitfalls-lint-adapter

`pitfalls --diff` 從 regex 提示器升級為 **lint 整合器**——偵測 diff 涉及的棧,跑專案 `.lumos/lint.json` 宣告的一組 lint 指令(各輸出 SARIF),lumos 解析合併、過濾到 diff 觸及行,併進既有 pitfalls manifest 餵 reviewer / `lumos-code-loop`。**lumos 只解 SARIF 一種格式、不內建棧規則、不管理 linter**;無宣告則 regex-only 分毫不變。

## 組件(spec 逐行權威 `docs/design/2026-07-04-pitfalls-lint-adapter.md`)
- **①② config + 偵測**:`_lint_load_config(repo_root)` 讀 `.lumos/lint.json`(缺/壞→None);`_lint_stacks_for_diff(added,config)` 對 added 每檔 `Path(f).suffix.lstrip('.')` 對 config key、命中收指令(去重)。
- **③ runner + SARIF 解析**:`_lint_run_and_parse(cmd,repo_root)→(claims,ok)`,承重點見 summary(temp/shell/timeout/killpg/uri 正規化/location-less 不連坐/run 級容錯)。
- **④ added 集合 + 座標系對齊**:`_diff_added_lines(diff)→{file:set(line)}`;`_lint_aligned(diff_range,repo_root)→bool`。
- **⑤⑥ 整合 + fallback**:`_pitfall_diff_mode` 尾段合併/過濾/tier/lint_ran;config=None 走 regex-only 早退。

## 天花板
- lint 整合只驗「lint 有沒有真跑到 + SARIF 有沒有正確解析合併」,不驗規則對錯(規則正確性是社群 linter 的事)。
- 座標系對齊靠 heuristic(右端 ref==HEAD + 乾淨工作區);非對齊時降級全收=寧可噪音不漏,過濾精度讓位安全。

## 相關
- 計劃:[[pitfalls-lint-integration_計劃]](本節點是第 ① 塊落地;②③④ 塊待做)。
- 觸發層:[[pitfalls-code-loop]](tier high 觸發對抗代碼審,吃本 manifest)。
- 機械底座同源:[[lumos-refcheck]](vault-free 機械核對,同「查證不靠 LLM」哲學)。
