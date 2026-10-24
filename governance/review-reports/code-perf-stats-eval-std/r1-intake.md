preflight-4: ran

# code-perf-stats-eval-std r1 收貨

由 code-perf-stats-eval(light)升級:light 第一輪出現 major,輕量閘永久失效(ratchet),改用 standard 新編號。審材:主線 b9e35042 到 1f07e112 的改動 r1-snapshot.patch(139 行,不含研究資料夾與卷證)。兩席全新:單審、架構對齊,都交回後才一起存檔,引句全錨。

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | major | 跑 which.py(cross-session-which-metric.txt):現行規則跨時段誤報 5、3、0 組全是冷啟動中位數;每幀類跨時段配對最大差都不到 1ms 下限 | HIT | 折:改用同口徑(配對最大差)比,冷啟動約 1.3–1.5 倍、每幀 P90 約 2.7–5 倍;寫明誤報全是冷啟動、每幀類被下限蓋住;計劃第 1 條理由同步改寫 |
| F2 | minor | 讀 device-observations.txt:只有重開機嘗試、沒有開機時間 | HIT | 折:改成「做過一次重開機嘗試」、剛開機是推定;溫度註明來源是腳本讀 dumpsys battery |
| F3 | minor | 讀計劃:RETIRE-IF 退回 10 輪,但第 3 條 10 輪會多誤報 | HIT | 折:退回 10 輪時第 3 條一起回退 |
| F4 | minor | 讀紀錄:REVISIT 2026-11-30 寫「同場比較做完設計後」,計劃 11-30 才開設計 | HIT | 折:改成綁計劃狀態 done、期限 2027-03-31 |
| F5 | minor | 讀計劃:每幀超時 P50 的 17–29% 對負數基準、都在 1ms 下限內 | HIT | 折:寫出 0.53–0.89ms、相對約 −3ms 基準;註明現在不會報、是為收窄容差預備;倍數改同口徑 |
| F6 | minor | 讀紀錄:雙道、P50/P90、每幀 CPU 耗時、每幀超時、Mann-Whitney、K-S 沒解釋 | HIT | 折:「怎麼量」補一段名詞白話 |
| A1 | minor | 讀計劃:新 REVISIT 夾在待辦清單中間 | HIT | 折:移到開頭,跟其他 REVISIT、RETIRE-IF 放一起 |

折 7、放行 0、駁回 0。
