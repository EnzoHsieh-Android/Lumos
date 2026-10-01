---
type: issue
status: done
created: 2026-10-01
updated: 2026-10-01
aliases: []
about_code: []
tags:
  - type/issue
  - status/done
  - scope/guards-gates
summary: |-
  PITFALL:[2026-10-01 殺傷力配方失配提醒實作時發現]`.lumos/config.json` 是合法 JSON、但內容讓 `load_platforms` 丟例外(例:兩個平台沒寫預設平台、root 是 null)時,只要專案裡有任何綁了 `[test:]` 的合約,doctor 的 Check T 會整支崩潰,走不到後面各段(新的 P2 段自己接得住,但輪不到它)。重現:照 `t_doctor_kill_recipe_drift` 的暫存 repo 加一條綁測試的合約、設定寫兩個平台不寫預設,跑 `lumos doctor`
  WHY:[2026-10-01 殺傷力配方失配提醒代碼審第 1 輪折入,已修]Check T 讀平台設定那段包了例外保護:設定讀不了只跳過 test_ref 存在性檢查、收尾不印「都綁了」,doctor 照樣走完 [test:t_doctor_kill_recipe_drift]
---
# 設定內容讓load_platforms丟例外時doctor整支崩潰

白話:設定檔寫錯一種特定的方式,健康檢查就整個當掉,而不是說「設定有問題」。殺傷力配方失配提醒那次實作時順手發現,沒在那次修(範圍外),記在這裡。來源 [[Projects/殺傷力配方失配提醒_計劃]]〈實作紀錄〉。

2026-10-01 已修:代碼審第 1 輪邊界席又碰到這個崩潰,照「有 major 的一輪全折」在 [[Projects/殺傷力配方失配提醒_計劃]] 裡一起修掉。
