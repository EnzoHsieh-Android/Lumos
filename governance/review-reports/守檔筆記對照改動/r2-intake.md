# 設計審第 2 輪收貨紀錄:守檔筆記對照改動

3 席全收齊後才動計劃。四道機械檢查:3 份都已是正規化格式;quote-check 全數錨定;refcheck 只有 `governance/reread-verdicts/` 不存在(本案新建);席位沒回報動過 git,reflog 無異動。

finding 編號:c=正確性-opus、b=邊界-sonnet、a=架構對齊-sonnet,後面接報告裡的 F 編號。

| 編號 | 席 F | 等級 | 處置 | 折在哪 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | 折 | 做法 2 指紋只看程式那一半、不含筆記 blob;S6 |
| c2 | 正確性 F2 | major | 折 | 做法 2 prepare 必帶 --orchestrator;做法 4 印的指令帶要人填的 --orchestrator |
| c3 | 正確性 F3 | major | 折 | S1 拿掉 NFD 承諾;〈誠實界線〉寫明既有限制、實作時開 Issue |
| c4 | 正確性 F4 | minor | 折 | 做法 4 資料夾不存在=沒紀錄;S6 |
| c5 | 正確性 F5 | minor | 折 | 做法 2 OTHERS 只列程式檔、NOTETEXT 照實驗格式;做法 0 切行照實驗 |
| c6 | 正確性 F6 | minor | 折 | 做法 1 prepare 提早結束與起點算不出只印不記 |
| c7 | 正確性 F7 | minor | 折 | 做法 1 不讀 node_home 設定;S1 |
| c8 | 正確性 F8 | minor | 折 | 做法 2 指紋一支共用函式、口徑寫死 |
| c9 | 正確性 F9 | minor | 折 | 〈誠實界線〉筆記改名加移出 |
| b1 | 邊界 F1 | major | 折 | 做法 0 --literal-pathspecs;S1 |
| b2 | 邊界 F2 | major | 折 | 做法 4 掛鉤只在 130 停下;〈實務隱患〉;S9 |
| b3 | 邊界 F3 | minor | 折 | 做法 4 最外層只接 Exception |
| b4 | 邊界 F4 | minor | 折 | 做法 4 開關讀取時機與壞值處理;S13 |
| b5 | 邊界 F5 | minor | 折 | 做法 2 補測試檔帶佈局;〈誠實界線〉兩種佈局 |
| b6 | 邊界 F6 | minor | 折 | 做法 3 json 區塊去尾、大小寫、未收尾退回;quote/why 轉字串截長、過 _esc_clean |
| b7 | 邊界 F7 | minor | 折 | 做法 4 30 秒寫成軟上限、共用函式收截止時間 |
| a1 | 架構 F1 | major | 折 | 同 c4 |
| a2 | 架構 F2 | major | 折 | 同 c2 |
| a3 | 架構 F3 | major | 折 | 做法 4 note_reread.gate、值域 block/warn/off、四種壞設定;S13 |
| a4 | 架構 F4 | major | 折 | 做法 1 改動清單用 _nodehome_name_status(norm=False) 同時留原樣與 NFC |
| a5 | 架構 F5 | minor | 折 | 做法 1 選配參數連印出也關掉 |
| a6 | 架構 F6 | minor | 折 | 做法 4 LUMOS_SKIP_REREAD_CHECK 記 skipped-env |

重現不到而沒折的:無(refuted-set none)。放行的:無。
