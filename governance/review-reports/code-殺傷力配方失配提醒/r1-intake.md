# 代碼審第 1 輪收貨紀錄:殺傷力配方失配提醒

8 席全收齊後才動程式。材料拆兩份(程式 858 行、測試 494 行);通才席審測試,其餘審程式。四道機械檢查:8 份都已是正規化格式;quote-check 全數錨定;refcheck 引用的檔與行號都存在;席位都在自己的 clone 做實驗,repo 根 reflog 無異動。規格符合席交回後自己改過報告裡三條佐證行的行號,refcheck 照樣全數對得上。外家 finder/否決照 2026-09-30 使用者裁定預設不派。

本輪有 major(正確性 F1)→ 全折。

finding 編號:c=正確性-opus、k=併發-sonnet、b=邊界-sonnet、g=合約圖譜-sonnet、t=通才-sonnet、p=spec-conformance-sonnet、a=架構對齊-sonnet、s=資安-opus。

| 編號 | 席 F | 等級 | 重現 | 處置 | 修法與測試 |
|---|---|---|---|---|---|
| c1 | 正確性 F1 | major | HIT(編排者用 negguard 版重跑席位腳本:kill-add 印「不在提交裡」、P2 列出、真跑 guard kill 判 survived) | 折 | `_kill_alias`:字面不在提交裡、檔案系統開得到時改用提交裡的名字;對照測試加「檔名拆開的 Unicode 寫法」「大小寫跟提交裡不同」兩格(期望值照當下檔案系統算) |
| c2 | 正確性 F2 | minor | HIT(編排者實測 git 還原:`prod.py/.`、`prod.py/x/..`、`../gpx/prod.py`、`lnk/x.py`、`PROD.py` 都失敗;`./`、`a/../`、`.//` 成功) | 折 | 新狀態 unrestorable + `_kill_pathspec` 照 git 字面規則算還原路徑;對照測試四格改判、加 `/.` 與 `zz/../prod.py` 兩格;ok 不再收「還原失敗」 |
| k1 | 併發 F1 | minor | 未能重現(席位自標;本機 ls-tree 0.03 秒) | 折 | git 子程序各加 10 秒上限(`_KILL_GIT_TIMEOUT`),逾時歸讀不了 |
| k2 | 併發 F2 | minor | HIT(讀碼:失敗時 raise 不快取) | 折 | `_kill_tree` 讀不了也記住、回 (None, 原因),判成 noroot 併成每個平台一行 |
| b1 | 邊界 F1 | minor | HIT(對照測試「缺 new」一格:判斷 ok、guard kill rc1 KeyError) | 折 | `_kill_bad_fields` 加 new/test;test 名過不了白名單也算 malformed;對照測試加「缺 new」「test 名不合法」兩格 |
| b2 | 邊界 F2 | minor | HIT(條款測試 ⑦c 改前兩行) | 折 | 人寫的欄位經 `_kill_show` 跳脫;kill-add 測試 ⑦c |
| b3 | 邊界 F3 | minor | HIT(條款測試 ⑩d 拿掉保護即紅) | 折 | Check T 讀平台設定包例外保護、只跳過存在性檢查;Issue 結案;doctor 測試 ⑩d |
| b4 | 邊界 F4 | minor | HIT | 折 | 格式不對印「第 N 條配方欄位格式不對(哪個欄位)」;doctor 測試 ② 斷言沒有 `::` |
| b5 | 邊界 F5 | minor | HIT | 折 | 訊息改「8 到 64 個」;kill-rm 測試 ①c |
| g1 | 合約圖譜 F1 | minor | HIT(讀碼) | 折 | 平台不在設定裡那行也附修法;kill-rm 訊息與系統筆記改成「逐條列出的配方修法裡都有短身分、平台合併那行不附」 |
| g2 | 合約圖譜 F2 | minor | HIT | 折 | skill reference.md 健康巡檢那列補 P2 |
| p1 | 規格符合 F1 | minor | HIT | 折 | 併進 unrestorable,提醒字面不再自相矛盾;kill-add 測試 ⑦b |
| p2 | 規格符合 F2 | minor | HIT | 折 | 同 b4 |
| p3 | 規格符合 F3 | minor | HIT(讀碼:遇 cfg 就 return、items 清空) | 折 | 設定檔讀不了時照樣逐條走,格式不對照列;doctor 測試 ⑩b 兩種排列 |
| a1 | 架構對齊 F1 | minor | HIT(讀碼) | 折 | 整段兜底改 `warn_soft([], "這一段算不出來…")`,同 S13/S14 |
| s1 | 資安 F1 | minor | HIT(席位腳本;doctor 測試 ⑫ 拿掉跳脫即紅) | 折 | `_kill_show`:json 引號跳脫 + Cc/Cf/Zl/Zp 轉成 \uXXXX;doctor 測試 ⑫、kill-add 測試 ⑦c |
| t1 | 通才 F1 | minor | HIT | 折 | 判重改用失配的那條擋(kill-add 測試 ②) |
| t2 | 通才 F2 | minor | HIT | 折 | 對照測試加「CRLF 檔、原文跨行」一格 |
| t3 | 通才 F3 | minor | HIT | 折 | kill-rm 測試 ① 加「只對到中間一段」 |
| t4 | 通才 F4 | minor | HIT | 折 | kill-rm 測試 ② 加 inode 換了 |
| t5 | 通才 F5 | minor | HIT | 折 | doctor 測試 ⑩c |
| t6 | 通才 F6 | minor | HIT | 折 | doctor 測試 ⑫ 用超過 30 字的合約片段 |
| t7 | 通才 F7 | minor | HIT | 折 | kill-add 測試 ⑮ 行程內換掉判斷函式讓它丟錯 |

翻紅(編排者在另一份 clone 逐一還原修法,清 __pycache__ 後跑):拿掉別名 → 大小寫、拆開寫法兩格紅;拿掉還原檢查 → 資料夾連結、經 wt 爬回等格紅;拿掉跳脫 → doctor ②⑤⑪⑫ 紅;拿掉 Check T 保護 → doctor ⑩d 紅;不驗 new/test → 缺 new 一格紅。修完四支條款測試全綠(27/27/63/21),`-k kill` 281、`-k doctor` 304、`-k check_t` 11 全綠。
重現不到而沒折的:無(refuted-set none)。放行的:無。
