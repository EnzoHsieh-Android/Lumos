---
type: verification
status: pass
date: 2026-07-05
valid_under: "scripts/lumos compose-metrics 邏輯不變;Compose Compiler Metrics 格式(module.json 鍵/composables.csv 欄/composables.txt 區塊)為 compose-compiler 1.5.x 形狀"
revalidate_when: "Compose 編譯器 metrics 格式改(欄名/檔名/strong-skipping 語意) / _compose_diff 或解析契約改 / baseline schema 改"
tags:
  - type/verification
  - status/pass
related:
  - "[[compose-metrics-adapter]]"
summary: |-
  TEST:test_lumos.py 476 passed(t_compose_parse/t_compose_diff/t_compose_metrics_cli);KDS 真機端到端(baseline 21 non-skippable + 注入 unstable-param probe→delta 精準抓到 unstable_params)
  VERIFY:subagent-driven 4 task、每 task 乾淨 reviewer 雙判;3 task 有 fix 派修(T1 col-0 fun/T3 baseline footgun)
---
# 2026-07-04_compose-metrics-adapter

compose-metrics-adapter(pitfalls 偏科層 Compose 重組效能)實作驗證。spec KDS 真機驅動 + design-loop 2 輪(核心硬化)→ writing-plans 4 task → subagent-driven。

## 測試覆蓋
- `t_compose_parse`(T1)——module.json 解析(缺/壞→None)、csv non-skippable 集合、txt 解析硬化(泛型 `<T>` 剝除、col-0 裸 fun、scheme() 夾中間、空行不斷區塊、unstable 參數)。
- `t_compose_diff`(T2)——new_non_skippable 集合差 + unstable_params 附上、skippable_ratio EPS(微幅不報/大跌報)、count 升報/不變不報、移除不報。
- `t_compose_metrics_cli`(T3)——端到端 subprocess:baseline_missing/--update-baseline 立基準/新增 non-skippable 抓到/checked_modules/壞宣告 rc2/**0 模組解析不清空 baseline**/**corrupt vs missing baseline 區分**。

## 逐 task review 結論
- T1-T3:spec ✅ + quality Approved 0 Critical/Important(T3 opus 複核 runtime traces)。
- fix 派修:**T1 真潛伏 bug**——txt 區塊起始 `" fun "`(需前導空格)漏 col-0 裸 fun(真機 `calculateYOffset`),改 `"fun "` 涵蓋 + col-0-unstable 證明測試;**T3 data-loss footgun**——`--update-baseline` 0 模組解析時會清空 baseline,改不寫 + corrupt/missing 區分。
- Minor 留最終 review:cur_agg={} 空 dict 邊界(T3 None→failed 已覆蓋主路徑);baseline_unreadable 只在該路徑出現(happy-path 省略,消費端當 false)。

## KDS 真機驗證(2026-07-05,/Users/enzo/Citrus_KDS)
- 專案 build 給 Compose 編譯器 `metricsDestination`/`reportsDestination` 旗標 → 產真 metrics(app_release-module.json + composables.csv/txt)。
- **baseline 建立**:首跑 `baseline_missing:true`+`new_modules:[app]` → `--update-baseline` → `baseline updated (1 modules, 0 skipped)`,baseline 含 **21 non_skippable**(agg 96/233),再跑 0 regressions(乾淨)。
- **delta 精準抓到**:注入 `@Composable fun LumosDeltaProbe(vm: CentralViewModel)`(unstable 參數→non-skippable)、完整重 build → `compose-metrics` 回 **1 regression:new_non_skippable `com.citrus.citruskds.LumosDeltaProbe` unstable_params `['vm: CentralViewModel']`**(txt↔csv join 於真資料成立)。
- **真機發現(已記天花板)**:incremental build 只產部分 metrics(cached 2s build 的 csv 僅 185B/部分檔)→ 現況集合殘缺、delta 失準;**須用完整 build(--rerun-tasks/clean)的 metrics**。
- KDS build.gradle.kts 的 metrics 旗標與 probe 驗完已還原;`.lumos/compose-metrics.json` + `compose-baseline.json` 留作真整合(future build 需保留 Compose metrics 旗標)。

## 已知限制 / 天花板
- 只報退步不報怎修;需完整 build 的 metrics(lumos 不 build);name-based 無 file:line;metrics 語意依 Compose 編譯器版本。
- test_lumos.py 為 anchor,merge 後 push 前須 anchor approve。
