---
type: issue
status: open
created: 2026-10-06
updated: 2026-10-06
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/guards-gates
related:
  - "[[Projects/CI加速_計劃]]"
summary: |-
  PITFALL:健檢判斷「呼叫閘的 CI 工作有沒有抓完整歷史」的 `_ci_has_full_history` 不認行尾帶註解的 `fetch-depth: 0  # …`,會把有抓完整歷史的工作判成沒抓 [出處:2026-10-06 代碼審 code-ci-speedup r1 架構對齊席建議共用它,編排者實跑發現] [根因:設定行的正則要求 0 後面只能接空白到行尾] [repro:對本 repo 的 .github/workflows/ci.yml 每個工作呼叫 `_ci_has_full_history(工作內容.split("\n"))`,三個都回 False]
---
# CI完整歷史判斷不認行尾註解

白話:健檢有一道檢查,看 CI 裡呼叫筆記形狀閘、筆記內容審的工作有沒有抓完整的 git 歷史(`fetch-depth: 0`)。判斷那行的正則要求 `0` 後面只能接空白到行尾,所以寫成 `fetch-depth: 0   # 說明` 的工作會被判成「沒抓」。本 repo 自己的 ci.yml 就是這樣寫的。

現況:本 repo 的健檢目前沒有因此誤報(健檢 0 issues),原因我沒查——可能那道檢查只在某些條件下跑,或結果算提醒不計入。消費專案在那行後面加註解的話,有可能被誤唸。

怎麼修:正則在 `0` 與引號之後允許 `\s+#.*` 的行尾註解;加一格測試(帶行尾註解的設定行判成有抓)。修的時候順便查清楚為什麼本 repo 沒被唸。

發現經過:[[Projects/CI加速_計劃]] 的代碼審建議 `t_ci_yml_matrix_and_gates_shape` 共用這支函式,共用後三個工作全判成沒抓,才發現;該測試改回自己用正則判,註解指向本篇。
