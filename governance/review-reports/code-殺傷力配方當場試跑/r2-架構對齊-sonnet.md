severity: major

# 架構對齊-sonnet 第 2 輪報告

## 三問

1. 分層與依賴方向:新函式都落在同一支 scripts/lumos 內既有的同層位置。`_fix_recipe_rerun_notes` 多收 `rr`、`tree`,跟 `cmd_loop_fix_check` 裡 `load_platforms(tree)`、`_fix_check_config(tree)` 同一個「讀樹裡(提交裡)那份」基準,方向一致,沒有跨層直呼。`_kill_log_latest` 只拿 ts 比大小,沒碰別層。對照:file: `scripts/lumos:12081`、`scripts/lumos:11607`。
2. 命名與錯誤處理:`_kill_recipe_shape_bad` 命名和 `_fix_bad_strings`、`_fix_test_name_bad`(file: `scripts/lumos:11695`、`scripts/lumos:11748`)的 `_bad` 尾碼一致;回「原因字串或空字串」跟 `_kill_path_issue`(file: `scripts/lumos:14109`)同型。錯誤處理有一處不一樣(F2):知識庫不在 repo 內時 `_fix_recipe_rerun_notes` 靜靜回空清單,鄰居 `unpinned` 與外層 try 都會留一行說明。提醒前綴 `⚠ 提醒:` 改成跟 `_kill_add_warn`(file: `scripts/lumos:14229`)同一個,對齊。
3. 第二種做法:有。`_kill_recipe_shape_bad` 是第二套「配方格式壞不壞」的判斷,`_kill_recipe_judge` 的 malformed 分支已經在做同一件事(F1)。`_kill_log_latest` 改成「同 ts 取先出現」,註解說跟合約背書同規則,我核對 `_backing_judge_groups` 沒有可共用的現成函式,屬各自實作,不列。

## F1 配方格式壞的判斷出現第二套,跟既有的 malformed 判定判得不一樣
severity: major
blocking: 是
引句:「def _kill_recipe_shape_bad(r):」
file: `scripts/lumos:14059`
file: `scripts/lumos:14075`
file: `scripts/lumos:14094`
file: `scripts/lumos:15338`
1. 專案裡「這條配方格式壞不壞」的唯一答案是 `_kill_recipe_judge` 的 `malformed` 狀態(不是物件、platform 不可雜湊、file 不是字串、test 名不合法),kill-add 提醒與 doctor P2 都走它(file: `scripts/lumos:14209`、`scripts/lumos:14360`)。修正新增了獨立的 `_kill_recipe_shape_bad`,另立一套欄位清單(invariant/file/old/new 必須是字串、platform 必須是字串或 null),沒有重用也沒有在 `_kill_recipe_judge` 旁註明兩者分工。
2. 兩套已經判得不同,最小重現(在 negguard 唯讀載入,輸出為「shape_bad 結果 | judge 狀態」):
   - `platform: 5`:`platform 不是字串 | noplat`
   - `new: 123`:`new 不是字串 | hits`
   同一條配方,doctor/kill-add 的判法不把它當格式壞,`guard kill --id` 卻擋下並叫人 kill-rm,使用者會看到兩個指令對同一條配方說法不一。日後有人補欄位檢查,必須兩處都改。
3. 計劃自己在註解裡寫「兩邊不分家靠 t_kill_recipe_check_matches_guard_kill」(file: `scripts/lumos:13908`),這套新判斷沒有被那個對照測試涵蓋。
4. 建議:`_kill_recipe_shape_bad` 改成呼叫 `_kill_recipe_judge` 的格式檢查段(抽出欄位型別那幾行共用),或在 `_kill_recipe_judge` 之前明確只當 guard-kill 專用並由對照測試鎖住差異。

## F2 知識庫不在 repo 內時提醒靜默消失,沒留說明行
severity: minor
blocking: 否
引句:「    except ValueError:      # 知識庫不在這個 repo 裡:配方的 file 對不到這裡改過的檔」
file: `scripts/lumos:11952`
file: `scripts/lumos:12081`
1. 同一個函式的鄰居(平台釘不住版本)都會往 `notes` 加一行說明,外層 `except Exception` 也會加「算不出來」一行;這裡是第三種處理:靜默回 `[]`。結構對,只是錯誤處理的慣例不一致。
2. 次要觀察:迴圈仍用工作目錄的 `env.notes` 決定哪些節點、再從 `vtree` 讀配方,兩份來源混用;`_kill_note_skipped(n)` 看的是工作目錄的 `kill_recipes` 欄。屬同一個「基準」問題的邊角,給不出具體失敗場景,不另列。

不對齊共 2 條,其中 major 1 條
最高等級:major,blocking 共 1 條
