# 代碼審第 4 輪收貨紀錄:殺傷力配方失配提醒(超過上限的破例輪)

Enzo 2026-10-01 在第 3 輪上限後裁「破例再審一小輪」:只派正確性、資安兩席,只審第 3 輪修正差異(r4-delta.patch,709 行)。2 席全收齊後才動程式。四道機械檢查:2 份都已是正規化格式;quote-check 全錨;refcheck 全數對得上;兩欄一致;repo 根 reflog 無異動。

本輪 3 條 major,兩條是第 3 輪修正引進的(s1 記憶體、c1 檔案連結判法)。四輪下來 major 都在「模擬 guard kill 怎麼解析怪路徑」那塊 → 照約定停下來問人。★Enzo 裁「換做法:規定正式路徑」★:`file` 必須是提交裡的正式路徑,不是的一律提醒改寫、不預測 guard kill;模擬整塊拿掉。本輪 6 條都以這次改法處置(折)。

finding 編號:c=正確性-opus、s=資安-opus。

| 編號 | 席 F | 等級 | 重現 | 處置 | 修法與測試 |
|---|---|---|---|---|---|
| c1 | 正確性 F1 | major | HIT(讀碼:檔案連結時 guard kill 還原 rc0、不報 error;席位附 `_krc_match` 對照) | 折 | 檔案連結不是正式路徑 → path;還原判斷整塊拿掉;對照測試「repo 內檔案連結」判 path |
| c2 | 正確性 F2 | major | HIT(對照測試新格「new 含寫不成 UTF-8 的替身字元」:guard kill rc1 UnicodeEncodeError) | 折 | new 含替身字元 → malformed;file 含替身字元走 `_path_special_chars` → path |
| c3 | 正確性 F3 | minor | HIT(單元比對;本機造不出只不分大小寫的檔案系統) | 折 | 比對鍵與別名整塊拿掉;建議只用「去 ./ .. 後不分大小寫與寫法」查一次表 |
| c4 | 正確性 F4 | minor | HIT | 折 | `_kill_add_warn`、`cmd_guard_kill_add` 說明改成「寫入成功、放掉鎖之後驗」 |
| s1 | 資安 F1 | major | HIT(席位腳本:80KB 配方 1.88GB) | 折 | 別名快取整塊拿掉;`t_kill_recipe_check_fs_and_git` 段數 5000 的路徑 2 秒內判成 path |
| s2 | 資安 F2 | minor | HIT(doctor 測試 ⑪b 加設定檔平台名與找不到那行) | 折 | Check T 三行的筆記路徑、test 段、平台名清單全跳脫 |

翻紅(編排者在另一份 clone 逐一還原,清 __pycache__):連結與子模組也當正式路徑、不擋拆開寫法(新格:提交裡存拆開寫法、precompose 開)、不擋冒號開頭、不擋 new 的替身字元、找不到測試那行不跳脫、平台名清單不跳脫、不給建議——七個翻紅;「不擋控制字元路徑」照綠,屬等效突變(含控制字元的名字在這些格子裡本來就不在提交清單、照樣判 path;留著是為了顯示安全)。修完 `-k kill` 306、`-k check_t` 11、`-k doctor` 307 全綠。
重現不到而沒折的:無(refuted-set none)。放行的:無。
換做法後的改動另派第 5 輪審。
