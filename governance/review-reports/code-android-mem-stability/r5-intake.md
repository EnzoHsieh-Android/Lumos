preflight-4: ran

# code-android-mem-stability r5 收貨

這輪只派資安(2026-10-24 Enzo 裁:第四輪處置閘卡在資安席覆蓋——編排者把通才席的記帳材料設成修補差異,同一支測試檔的改動指紋跟資安席看的完整改動對不上,同輪補不了;cap-decision 改記 extra-round,只派三席資安對最後一版補審,報 major 就折、不再加輪)。
審材:主線 7d17bd73 到 cacb4d3f(含第四輪修補)的完整改動,切三包:r5-snapshot-code.patch(1337 行)、r5-pkg-tests.patch(1309 行)、r5-pkg-docs.patch(758 行),三席各看一包,合起來涵蓋全部改到的檔;記帳的 --spec 是三包原樣接起來的 r5-snapshot.patch。
三席:程式-資安、測試-資安、文件-資安(都是 sonnet),都交回後才一起存檔;席報告從各席對話紀錄取最後一則回答原文。引句全錨(測試資安席 clean,沒有引句)。
id:X 程式-資安、Y 文件-資安,編號照報告順序。

## 機械重現與去向

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| X1 | minor | 席位實跑:PATH 裡沒有 git 時 preflight 把 None 當成不是 repo、照寫產物 | HIT | 放行:git 執行不了時這台機器本來也沒辦法用 git 提交,產物進不了版控;rev-parse 逾時 120 秒要 git 本身卡死才會發生,觸發條件很窄 |
| X2 | minor | 席位實跑:驅動失敗時輸出最後 200 字進 driver.reason 並印出 | HIT | 放行:最多 200 字、控制字元與分行字元已清掉偽造不出一行判定,只能影響 AI 讀到的一句話;驅動是使用者自己專案設定的指令,同族的工具錯誤訊息是診斷用,在單人、AI 依序操作的威脅模型下照留 |
| Y1 | minor | 讀 Perfetto v57.2 的 heap_profile:轉檔留在系統暫存 heap_profile-*、斷線時裝置留 profile-* | HIT(席位讀工具原始碼) | 折:SKILL L3 第 1 步補兩種殘留要自己看過再刪 |
| Y2 | minor | 席位實跑:SKILL 範本的 decided_by: 誰 照填過得了 --check-config | HIT | 折:SKILL 範本改成 <裁定的人>、<YYYY-MM-DD> 佔位並寫明只能照使用者的回答填 |
| Y3 | minor | 讀 trace_processor 結構:heap_graph_object 有 value_string 欄,計劃說 java_hprof 不含字串沒有證據 | HIT | 折:計劃兩處改成「有沒有字串與陣列內容沒驗過,一律當含個資處理」 |

## 修補因果

| id | 歸因 | 證據 |
|---|---|---|
| X1 | 有證據的原有漏查(修補沒補到) | 第四輪修補只處理 git 回非 0,run 回 None 的路徑跟 5fc4e715 一樣跳過;不是修補讓它變差 |
| X2、Y1、Y2、Y3 | 有證據的原有漏查 | 5fc4e715 的對應程式與文字相同 |

--regression-set none(五條都不是第四輪修補造成的:X1 的路徑在修補前後行為相同)。
