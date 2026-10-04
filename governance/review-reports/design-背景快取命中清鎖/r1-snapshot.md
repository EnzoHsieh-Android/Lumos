---
type: project
status: doing
created: 2026-10-05
updated: 2026-10-05
tags:
  - type/project
  - status/doing
  - scope/guards-gates
related:
  - "[[Issues/背景快取命中留下暖機鎖]]"
  - "[[Projects/過期鎖安全接手_計劃]]"
lands_in:
  - Systems/lumos-cli-write
---
# 背景快取命中清鎖_計劃

## 問題與邊界

[[Issues/背景快取命中留下暖機鎖]] 是前案第三輪找到的獨立缺陷：派工端建立 `.warming` 鎖，背景程序繼承暖機標記與派工端 PID 副本，負責在工作結束時清理那把鎖；但 `_dispatch_lens_graph` 早期讀到快取時直接返回，跳過函式尾端的清鎖。快取過期後殘留鎖阻止新暖機。前掃另查到快取未命中後仍有 impact、JSON、base 樹等錯誤提前出口，也會繞過尾端清理；本小修將背景程序從算得出快取路徑後的所有出口一起包住。`Popen` 啟動失敗誤報由 [[Issues/背景啟動失敗誤報逾時]] 的另一個修復循環處理。等待端仍只讀快取，不得按「曾取得」推論現在持有而刪鎖。

保留既有鎖格式與鎖內 PID 比對；在原本只有 PID 比對的清理判斷外，加一道 `_LENS_WARM_ENV` 條件，避免一般呼叫碰鎖。把身份核對收成同層 helper，以 `try…finally` 包住快取路徑已算出後的鏡頭主體，讓快取命中、正常算完、已知錯誤返回和未預期例外都走同一個清理出口；非背景呼叫及身份不符都不刪。這只延伸現行同版身份界線，不把 PID 當跨版本或人工換檔的強身份保證。若現有 PID 可在真實同版競爭中撞名，應改成每次 acquisition 唯一身份，不靠多次 PID 比對硬補。

## 驗收條款

- [S1] 當背景程序持有本次 `.warming` 鎖且進場命中快取時，`_dispatch_lens_graph` 應回快取並清掉自己的鎖；測試先在舊碼驗 rc 0 且鎖仍在，再驗修後鎖消失。 [test:t_lens_warmer_cache_hit_releases_owned_lock]
- [S2] 當鎖內 PID 不符或一般呼叫沒有暖機標記時，`_dispatch_lens_graph` 應在快取命中後保留那把鎖。 [test:t_lens_warmer_cache_hit_releases_owned_lock]
- [S3] 當背景程序算完新快取時，`_dispatch_lens_graph` 應清自己的鎖，且等待端命中快取應保留其他持有者的鎖。 [test:t_lens_timeout_keeps_warming_cache] [test:t_lens_stale_lock_reports_uncertainty]
- [S4] 當背景程序在快取路徑算出後遇到 impact 錯誤而提前返回時，`_dispatch_lens_graph` 應清理身份相符的鎖，且保留原返回碼。 [test:t_lens_warmer_cache_hit_releases_owned_lock]

PRIOR-ART: [Python `try…finally` 語法文件](https://docs.python.org/3/reference/compound_stmts.html#the-finally-clause)確認 `return` 也會走清理段；本案沿用此現成語意，把背景清鎖掛在整個鏡頭工作出口，不再逐個出口補刪鎖呼叫。程式主體縮排變動較多，但控制流程只有一個清理點且不增加依賴。

RETIRE-IF: 若同版程序能以相同 PID 換入新鎖，或再有一例「清不到自己的鎖／清到別人的鎖」，撤掉只靠 PID 的身份判斷，改用每次取鎖唯一身份；若實際需要在快取路徑算出前就清鎖，將清理範圍上移到能確定鎖路徑的入口，而不猜路徑。

## 實務隱患

已排除:金流:此路徑只計算派工鏡頭快取，不處理付款。
已排除:對外送出:本修復不推送、不部署、不寄送資料。
已排除:不可逆:只動隔離 clone 的程式與測試，真實鎖不在本次操作範圍。
守衛面:誤刪他人的鎖會讓兩支背景工作同時運作；S2 必須釘住身份不符及一般呼叫。

## 回退

若新 helper 誤刪他人鎖，回退本次分支到父提交 `930915bb` 並暫停背景暖機入口，不恢復等待端按舊狀態刪鎖。這個父提交仍有 F1/F2，不能當成可部署的安全版本。

## 驗證順序

先以 S1 紅燈固定現場，再做最小修補；S2 驗不能誤刪，S3 驗既有背景與等待端。完成後記獨立驗證紀錄、審查快照與處置；前案仍因 F2 未修保持 pending，不把此小修聲稱為整體放行。
