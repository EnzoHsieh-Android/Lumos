# 照留表態要有期限或去處 r2 收貨

六席收齊才判讀。三道:引句除架構對齊席 #3(「開著」不足 10 字)外全錨;refcheck 無越界(邊界席 1 筆缺檔是它引的暫存路徑);報告已正規化(正確性席總結行同行帶 blocking 字樣,只是總結句,不改)。各條由編排者讀碼或照 spec 字面推演重現。

| id | 一句 | 重現 | 去向 |
|---|---|---|---|
| c2-F1 | 寬限寫死設計日 | HIT:spec 依據段寫上線日 | 折:合併時定為合併日+30 |
| c2-F2 | 空樹起點整批當新寫 | HIT:`_drift_probe_old` 沒起點回 None | 折:只標 old is False |
| c2-F3 | 推送路徑沒欄位防護、prev_ack 無來源 | HIT | 折:推送只看非空字串,定義 dead |
| c2-F4 | 補建圖譜物件失敗方向與預算 | HIT | 折:推送不建 |
| c2-F5 | 同條件標記的新行不列 | HIT:既有行為 | 折:寫進天花板 4 |
| b2-F1 | date 缺壞未來、until 格式 | HIT | 折:只用 until、只收 10 字元 ISO |
| b2-F2 | 判不了資料夾、.. 子字串誤殺 | HIT | 折:拿掉路徑字面檢查,交給 note_state 查表 |
| b2-F3 | 推送多建一棵樹、呼叫點名稱 | HIT:扣表態在 `_drift_check_c` | 折:推送不建、改名稱 |
| b2-F4 | 推送路徑失效原因沒來源、提示印兩次 | HIT | 折:定義 dead、有 prev_ack 不另印 |
| b2-F5 | 驗收缺極端輸入 | HIT | 折:S3、S4 補 |
| i2-F1 | 呼叫點名稱不準不全 | HIT | 折:做法 10 |
| i2-F2 | prev_ack dead 沒規格、讀 related 會丟例外 | HIT:`_drift_prev_ack_line` 讀 pa["related"] | 折:先看 dead 鍵 |
| i2-F3 | 到期沒有自動出口 | HIT:scan 沒有自動跑 | 折:doctor 一行、S8 |
| i2-F4 | 說明同步漏、CHANGELOG | HIT | 折:做法 9 |
| i2-F5 | 防線計劃 [S3] 要改 | HIT | 折:做法 9 |
| i2-F6 | 綁定計劃收尾沒提示 | HIT | 折:doctor 一行涵蓋 |
| r2-F1 | 分支合併前因別處收尾變紅 | HIT | 折:推送不看開不開 |
| r2-F2 | 寬限寫死 | HIT | 折:同 c2-F1 |
| r2-F3 | 推送起點本來就會變 | HIT | 折:隱患改寫 |
| r2-F4 | scan --at 用今天 | HIT | 折:隱患寫明 |
| r2-F5 | 退回再升級 | HIT | 折:隱患 |
| r2-F6 | 表態驗磁碟、推送驗 tip | HIT | 折:推送只看有沒有綁 |
| r2-F7 | 沒起點不限全新 repo | HIT:`_push_no_mainline` | 折:做法 7 |
| s2-F1 | 推送建樹過重 | HIT | 折 |
| s2-F2 | until 冗餘 | HIT | 放行 |
| s2-F3 | 路徑字面檢查多餘 | HIT | 折 |
| s2-F4 | prev_ack 新形狀 | HIT | 折:單一分支 |
| s2-F5 | 開著判斷寫兩次 | HIT | 折:`_drift_route_open` |
| s2-F6 | 常數與旗標確認 | HIT | 放行 |
| a2-F1 | today=None 語意、status_of 撞名 | HIT:`scripts/lumos` 第 769 行同名函式 | 折:as_of、note_state |
| a2-F2 | prev_ack 取法另訂 | HIT | 折:沿用 `_drift_bound_latest` |
