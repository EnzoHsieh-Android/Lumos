# 代碼審第 3 輪收貨紀錄:殺傷力配方失配提醒(上限輪)

4 席全新、只審第 2 輪的修正差異(r3-delta.patch,886 行;全貌 r3-snapshot.patch 供參考)。4 席全收齊後才動工作目錄(修法先在另一份 clone 準備、驗過,收齊後才搬回)。四道機械檢查:4 份都已是正規化格式;quote-check 對修正差異:3 份全錨,架構對齊席交 clean、零引句(不當載體);refcheck 全數對得上;兩欄(severity/blocking)全部一致;repo 根 reflog 無異動。

本輪有 major → 全折。達上限(3 輪)且末輪有 major:折完不再派席,攤給使用者裁。

finding 編號:c=正確性-opus、s=資安-opus、t=通才-sonnet;架構對齊-sonnet 0 條。

| 編號 | 席 F | 等級 | 重現 | 處置 | 修法與測試 |
|---|---|---|---|---|---|
| c1 | 正確性 F1 | major | HIT(對照測試新格「old 沒寫、檔是空的」:突變拿掉修法後判 ok、guard kill rc1 KeyError) | 折 | 原文恰好一次之後 old 或 new 沒寫 → malformed |
| c2 | 正確性 F2 | major | HIT(對照測試「repo 內相對符號連結」改兩條配方:guard kill 第二條 drifted) | 折 | `_kill_restorable` 回 git 對到的路徑集合,被改的那支不在裡面 → unrestorable |
| c3 | 正確性 F3 | minor | HIT(新格「平台不在設定裡而且 file 不是字串」:guard kill error 不在 config) | 折 | file 型別放到分平台、test 白名單之後才判;doctor 測試 ②⑩b 期望照新順序調整 |
| c4 | 正確性 F4 | minor | HIT(編排者掃 U+0370–U+1FFF:8 個字新舊鍵不同,例 ΐ 對拆開的大寫 Ϊ́) | 折 | `_kill_fold_key`:nfc(NFD(x).casefold());別名單元格加 ΐ |
| c5 | 正確性 F5 | minor | HIT(讀碼:驗原文在鎖內) | 折 | kill-add 驗原文移到鎖外(warn_box);`t_kill_recipe_check_fs_and_git` 斷言驗原文時鎖已放掉 |
| s1 | 資安 F1 | major | HIT(突變「對照表不快取」:5000 支檔、5000 段 → 12.2 秒;修後 2 秒內) | 折 | `_kill_alias` 每個 repo 掃一次提交、每個資料夾建一次對照表 |
| s2 | 資安 F2 | minor | HIT(kill-add 測試 ⑭d ⑭e 拿掉跳脫即紅) | 折 | 成功行的 test 名與舊 covers 過 `_kill_esc` |
| s3 | 資安 F3 | minor | HIT(doctor 測試 ⑪b) | 折 | Check T「平台前綴未定義」那行的平台名與 test 段過 `_kill_esc` |
| t1 | 通才 F1 | minor | HIT(突變「暫存索引改用工作目錄索引」新格翻紅) | 折 | 對照測試加「工作目錄的索引跟 HEAD 不同」 |
| t2 | 通才 F2 | minor | HIT(突變「不蒐集資料夾」新格翻紅) | 折 | 對照測試加「資料夾大小寫跟提交裡不同」 |
| t3 | 通才 F3 | minor | HIT(突變「kill-rm 完整內容不跳脫」「例外訊息不跳脫」翻紅) | 折 | kill-rm 測試 ⑥b 加 C1 與雙向覆寫字元;kill-add 測試 ⑮ 例外訊息帶控制字元 |

翻紅(編排者在修正 clone 逐一還原,清 __pycache__):old 沒寫不判格式不對、不看還原到哪支、file 型別搬回最前面、比對順序改回先組合、對照表不快取(補強後)、提醒拿掉、成功行 test 不跳脫(補強後)、成功行舊 covers 不跳脫、Check T 平台名不跳脫、暫存索引改用工作目錄索引、不蒐集資料夾、kill-rm 完整內容不跳脫、例外訊息不跳脫——十三個都翻紅(「對照表不快取」「成功行 test 不跳脫」兩個第一次照綠,補強測試後翻紅)。修完 `-k kill` 324、`-k check_t` 11、`-k doctor` 307 全綠。
重現不到而沒折的:無(refuted-set none)。放行的:無。
未再審:本輪折入(scripts/lumos 約 100 行、測試約 100 行)沒有席位看過,攤使用者裁。
