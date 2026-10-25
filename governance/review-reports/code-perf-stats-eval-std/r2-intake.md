preflight-4: ran

# code-perf-stats-eval-std r2 收貨

審材:主線 b9e35042 到 b202a4ea 的改動 r2-snapshot.patch(140 行)。兩席全新:單審、架構對齊,都交回後才一起存檔,引句全錨。
修補因果:F1 是重排待辦時沒同步外部引用(上一輪修補前就有,前兩輪沒人看);F2 是首版就漏寫的規則;F9 是上一輪把 REVISIT 改成綁計劃狀態時帶出的(上一輪修補造成);其餘是前面沒人看的角落。

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | major | grep:Android記憶體與穩定性驗收_計劃 寫「移到…的第 6 條」,重排後第 6 條是 vitals | HIT | 折:記憶體計劃改成第 8 條(3 處) |
| F2 | major | 讀 scripts/lumos:MACROBENCH_ZERO_CROSS 讓每幀超時 P90 跨零直接算變慢;評估程式 R2、R4 的 mag 只算 delta>tol | HIT | 折:名詞補跨零那條;註明 R2、R4 一起拿掉了跨零、本批現行規則沒因跨零報過、數字不受影響;計劃第 2 條寫明實作只拿掉啟動類那道 |
| F3 | minor | 算:冷啟動容差約 29ms,+20ms 低於容差;24 組來自 3 次注入 | HIT | 折:補說明抓到的多是配對雜訊、彼此不獨立 |
| F4 | minor | 讀 cross-session-report.txt:現行 20 輪跨時段已 0/48 | HIT | 折:待辦改成 20 輪第一、拿掉最大值那道第二、同場比較第三(用處是讓收窄容差安全、兩個 APK 交錯安裝本批沒試過);所有引用編號同步 |
| F5 | minor | 讀報告:跨時段沒算 Mann-Whitney | HIT | 折:摘要限定同場、跨時段沒試算 |
| F6 | minor | 讀 cross-session-report.txt 20 輪:間隔批同場雜訊每項都不大於連跑批 | HIT | 折:改成 0/150 幾乎必然、驗不出容差,跨天驗證留給 REVISIT |
| F7 | minor | git -C macrobench-lab:main 沒有實驗腳本,只在 perf-stats-experiment 分支 8bc68d4 | HIT | 折:寫明分支與提交 |
| F8 | minor | 讀紀錄:次、輪、組、冷啟動沒定義;4.47 與 4.7 口徑沒說明 | HIT | 折:名詞補定義;註明 4.47 是各輪 P90 的中位數、工具彙總值 4.7→10.2 |
| F9 | minor | 讀紀錄:REVISIT 綁計劃 done,文字講同場比較上線 | HIT | 折:改成日期型,寫明要查第 3、5 條上線了沒 |
| F10 | minor | 讀 magnitude-only-report.txt:10 輪 4 對 3,5 輪 5 對 5 | HIT | 折:RETIRE-IF 與第 2 條改寫成「線索、未證」 |
| A1 | minor | 讀計劃:REVISIT 用日期開頭卻寫事件條件 | HIT | 折:改成日期型的「到期查第 1、2、3、5 條上線了沒」 |

折 11、放行 0、駁回 0。--regression-set F9。
