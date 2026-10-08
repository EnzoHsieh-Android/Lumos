# 代碼審第 2 輪收貨紀錄:殺傷力配方失配提醒

5 席全新、只審第 1 輪的修正差異(r2-delta.patch,944 行;全貌 r2-snapshot.patch 供參考)。5 席全收齊後才動程式。四道機械檢查:5 份都已是正規化格式;quote-check 對修正差異:4 份全錨,邊界席 3 句有 1 句(F3 引的 `_kill_read_text` 既有碼)只錨得到全貌、錨不到修正差異 → 編排者機械重現(見下表 b3);refcheck 全數對得上;repo 根 reflog 無異動。

兩欄矛盾退回自判三次(severity 與 blocking 不一致,編排者不改席報告):架構對齊 F1(major/否 → 席降 minor/否)、正確性 F4(major/否 → 席改 major/是,理由:冒號開頭與關掉 precompose 兩種已實跑重現漏報)、邊界 F1(major/否 → 席降 minor/否)。

本輪有 major → 全折。正確性 F1–F4 與第 1 輪 c1/c2 是同一類(判斷函式模擬 guard kill 的路徑與還原對不上),照「同類兩輪換形狀」整類換掉:還原改問 git、檔案系統特性改量暫存資料夾、判斷順序照 guard kill。

finding 編號:c=正確性-opus、s=資安-opus、a=架構對齊-sonnet、b=邊界-sonnet、t=通才-sonnet。

| 編號 | 席 F | 等級 | 重現 | 處置 | 修法與測試 |
|---|---|---|---|---|---|
| c1 | 正確性 F1 | major | HIT(對照測試新格「結尾斜線而且原文 0 次」:舊版判 unrestorable、guard kill drifted) | 折 | 判斷順序照 guard kill:數原文、套 new 之後才判還原;對照測試加「結尾斜線而且原文 0 次」「缺 new 而且原文 0 次」 |
| c2 | 正確性 F2 | major | HIT(新格「test 寫成數字」:guard kill 照跑) | 折 | test 照 guard kill 用 `_kill_method_name(r.get("test",""))` 轉字串再比白名單 |
| c3 | 正確性 F3 | major | HIT(讀碼:`_kill_alias` 以工作目錄 lexists 推論) | 折 | `_kill_fs_fold` 量暫存資料夾的檔案系統;對照測試加「工作目錄另有沒提交的同名變體」;`t_kill_recipe_check_fs_and_git` 四種設定各走一遍 |
| c4 | 正確性 F4 | major | HIT(編排者實測 28 種寫法:ls-files 與 checkout 判定一致;新格「冒號開頭」「關掉 precompose」) | 折 | `_kill_restorable`:暫存索引 + `git ls-files --error-unmatch`,刪掉 `_kill_pathspec` |
| c5 | 正確性 F5 | minor | HIT | 折 | 有配方就回報設定檔讀不了;doctor 測試 ⑩b「配方全是格式不對」 |
| s1 | 資安 F1 | major | HIT(席位腳本照畫面貼上建出標記檔;kill-rm 測試 ⑥b) | 折 | kill-rm 完整內容過 `_kill_esc`、範本裡帶控制字元的欄位印佔位字 |
| s2 | 資安 F2 | minor | HIT(doctor 測試 ⑬) | 折 | `_kill_rel` 跳脫筆記路徑;`_kill_node_arg` 帶控制字元時印佔位字 |
| s3 | 資安 F3 | minor | HIT(kill-add 測試 ⑭b ⑭c) | 折 | 設定檔來的字、例外訊息、Check T 那行都過 `_kill_esc` |
| a1 | 架構對齊 F1 | minor | HIT(讀碼:另抄一組類別、少 Cs) | 折 | `_kill_esc` 改用共用 `_PATH_SPECIAL_CATS`;別名改用既有 `nfc()` |
| b1 | 邊界 F1 | minor | HIT(同 s3) | 折 | 同 s3 |
| b2 | 邊界 F2 | minor | HIT(同 c2;invariant 是數字時 guard kill 不讀它) | 折 | 同 c2;invariant 不再當格式條件 |
| b3 | 邊界 F3 | minor | HIT(引句錨不到修正差異,編排者機械重現:對照測試新格「file 含 NUL 字元」,guard kill rc1 ValueError) | 折 | file 含 NUL 判 malformed;對照表 malformed 收 ValueError |
| t1 | 通才 F1 | minor | HIT | 折 | 對照測試加「repo 裡剛好有 wt/prod.py」那格(還原改問 git 後此突變點已不存在,格子照留) |
| t2 | 通才 F2 | minor | HIT | 折 | doctor 測試 ⑫ 加 U+202E、U+2028 |
| t3 | 通才 F3 | minor | HIT | 折 | `t_kill_recipe_check_fs_and_git`:行程內數 git 呼叫,斷言每個都帶上限秒數、提交讀不了只問一次 |
| t4 | 通才 F4 | minor | HIT | 折 | 同 c3:別名改成注入檔案系統設定的單元格,不靠本機特性 |

翻紅(編排者在另一份 clone 逐一還原,清 __pycache__):還原一律當成功、還原檢查搬到數原文前、檔案系統一律當分大小寫、test 只收字串、跳脫只認 Cc、範本不擋控制字元、節點名不擋控制字元、全是格式不對時不講設定檔、還原檢查拿掉上限秒數、提交讀不了不記住——十個都翻紅(第一個突變錨點一開始沒套上、測試照綠,重做後翻紅)。修完五支條款測試全綠(8/29/29/22/79),`-k kill` 310、`-k check_t` 11、`-k doctor` 306 全綠。
順手:邊界席回報設定檔最外層是清單時 doctor 在符號設定段崩潰(既有、非本案改動),編排者重現後開 Issues/設定檔最外層不是物件時doctor在符號設定段崩潰。
重現不到而沒折的:無(refuted-set none)。放行的:無。
