---
type: system
status: doing
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/system
  - status/doing
related:
  - "[[lint-version-watch]]"
  - "[[pitfalls-lint-adapter]]"
  - "[[pitfalls-lint-integration_計劃]]"
verified_by:
  - "[[Verification/2026-07-04_compose-metrics-adapter]]"
summary: |-
  FLOW:讀 .lumos/compose-metrics.json(metrics/reports 目錄宣告)→ 解析現況 metrics(module.json 聚合 + composables.csv 逐 composable + composables.txt unstable 參數)→ 對比 .lumos/compose-baseline.json → delta manifest(regressions) → --update-baseline 放行(bump baseline)
  KEY:定位——Compose 重組效能是 SARIF linter 蓋不到的偏科坑(只有 Compose 編譯器知道 composable 可不可跳過);吃編譯器 metrics(composition over invention)、補 pitfalls 原始痛點
  KEY:baseline+delta——metrics 是整模組快照、無 file:line、無 severity(KDS 現況 21 non-skippable,直接報每次洗版)→ 必須存 baseline 只報退步;同 lint-watch 形狀(baseline≙鎖定版、現況≙latest、delta≙退步、放行≙bump)
  KEY:退步兩類——new_non_skippable(現況 non-skippable FQN 集合 − baseline 集合,附 unstable_params)+ aggregate(skippable_ratio 下降超 COMPOSE_RATIO_EPS=0.01;knownUnstableArguments/inferredUnstableClasses 任何上升);移除的 composable 不報
  KEY:non-skippable = csv row skippable=="0" and restartable=="1" 收 package(FQN);txt↔csv join 以裸 name 為鍵(csv 平行建 {FQN:裸name});txt 區塊起始=含 "fun <Name>("(涵蓋 col-0 裸 fun、scheme() 夾中間、剝泛型 <...>、空行不斷區塊)
  KEY:--update-baseline 只寫成功解析模組(failed 跳過免毒化)+ 0 模組解析不清空既有 baseline;non_skippable sorted() 寫入;corrupt baseline≠missing(baseline_unreadable 不覆蓋)
  KEY:--audit 盤點模式——無視 baseline 列出當下全部 non-skippable(+unstable 原因),補 delta-only「初次採用看不到既有問題點」的洞(KDS 真機:audit 列 22 條、delta 在乾淨 baseline 下 0)
  KEY:vault-free(dispatch 置 find_vault 前)、fail-open(模組解析失敗→failed[] 不升 rc)、rc 成功=0(含 regressions)/宣告壞=2;lumos 只讀 metrics 不 build 專案
  DEP:[[lint-version-watch]]
  DEP:[[pitfalls-lint-adapter]]
  TEST:test_lumos.py(t_compose_parse/t_compose_diff/t_compose_metrics_cli);全套件 476 passed;KDS 真機端到端(21 non-skippable baseline + 注入 unstable-param probe→delta 抓到)
  VERIFY:[[Verification/2026-07-04_compose-metrics-adapter]]
  DECISION:[2026-07-04]Mode B baseline+delta(metrics 整模組快照必須 baseline 才不洗版)(valid);[2026-07-04]不做 file:line grep-back(fragile)、name-based(valid);[2026-07-04]只報退步不報怎修(valid)
---
# compose-metrics-adapter

pitfalls 偏科層新支線——**Compose 重組效能**(SARIF linter 蓋不到的坑,是 pitfalls 原始痛點)。吃 Compose Compiler Metrics(專案 build 產出)、baseline+delta 比對、只報退步信號。

## 組件(spec 逐行權威 `docs/design/2026-07-04-compose-metrics-adapter.md`)
- **解析**:`_compose_read_module`(module.json 聚合)/`_compose_read_composables`(csv non-skippable 集合 + {FQN:裸name} + txt unstable_map)。
- **退步判定**:`_compose_diff`(new_non_skippable 集合差 + aggregate ratio EPS/count 升)。
- **子命令**:`_compose_metrics_mode`(config→per-module partition checked/new_modules/failed→baseline 比對→manifest;--update-baseline 放行)。

## 天花板 / 誠實邊界
- 只報「退步了」不報「怎麼修」(unstable→stable 是人的事:`@Immutable`/`@Stable`/wrapper)。
- **需完整 build 的 metrics**(KDS 真機坐實:incremental build 只出部分檔 → 現況集合殘缺、delta 失準);lumos 不 build,靠專案給 Compose 編譯器旗標。
- name-based、無 file:line;跨 package 同裸名的 unstable_params 可能錯置(輔助資訊、非退步本體);composable 改名=remove+add。
- metrics 語意依賴 Compose 編譯器版本(跨大版本 strong-skipping 語意變 → baseline 需重立)。

## 相關
- 計劃:[[pitfalls-lint-integration_計劃]](偏科層支線)。
- 同形狀:[[lint-version-watch]](baseline+delta+放行;本塊換資料源為本地 build metrics)。
- 補洞對象:[[pitfalls-lint-adapter]](SARIF adapter 蓋不到重組效能)。
