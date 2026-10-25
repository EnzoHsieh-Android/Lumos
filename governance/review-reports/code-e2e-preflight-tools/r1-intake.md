# code-e2e-preflight-tools r1 收貨

- 第一輪(標準分級):兩席都是新代理;單審席與架構對齊席同輪收齊後才寫進卷證,報告從各席逐字稿存檔(完成通知會把角括號轉成跳脫字)。
- 兩份報告 quote-check 全錨、report-normalize 已是正規化格式。
- 編號:F 單審、A 架構對齊,後接各席報告裡的條號。
- 本輪有 major(F1),照規則所有 minor 一併折入,不放行。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| F1 | 把門條件從 e2e 段改成讀最外層 stability,測試照綠 | 在工作目錄把 `if e2e.get("stability")` 改成 `if cfg.get("stability")` 後跑 `-k preflight_stability_tools`:11 passed, 0 failed(紅不起來),再還原 | HIT | 折(補「只有最外層 stability、e2e 沒開、兩支都缺」案例預期放行;同一改壞改跑後 16 passed, 2 failed) |
| F2 | 工具齊的案例整套跑那一趟沒檢查結果 | 讀測試:`elif extra:` 只檢查 --preflight 那趟,整套跑的結果沒用到 | HIT | 折(整套跑那趟改成檢查開跑前檢查放行、真的裝到 App;不檢查回傳碼,因為後面的收集腳本用假工具,成敗不在這條測) |
| A1 | 缺工具訊息句式跟同檔 ADB 那條、收集腳本不同 | 讀 `scripts/templates/android-e2e-run.sh` 的 ADB 檢查與新訊息 | HIT | 折(改成「找不到 X(…);用環境變數 Y= 指定」;測試斷言改成要有「找不到 <工具名>」,舊句式改跑後 14 passed, 4 failed) |
| A2 | 「有沒有宣告測試資料」兩支範本各寫一份 | 讀兩支範本:各是獨立的 python3 - 腳本、照抄進消費專案,不能共用 | HIT | 折(不合併成一份;測試加比對兩邊判斷式一字不差,只改收集腳本那邊改跑後 17 passed, 1 failed) |

修補對照:修正提交的差異就是修改前→後。
