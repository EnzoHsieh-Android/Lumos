# code-room資料庫測試守衛 r1 收貨紀錄

- 分級:standard(`lumos pitfalls --diff faecd422..2327a527` 印 tier: standard);一位審查員(正確性-sonnet)加架構對齊-sonnet,外家未派(單家族視角)。
- 材料:整份 `r1-snapshot.patch` 3058 行超過 1800 行上限,按鏡頭拆兩包:`r1-pack-正確性.patch`(scripts/lumos、pre-push、test_lumos.py,1588 行)、`r1-pack-架構對齊.patch`(scripts/lumos、pre-push、skills、圖譜筆記,1296 行)。設計審卷證、replay 判定、治理帳與 anchor 基準檔沒送審(已過設計審處置閘、不是程式)。
- 修復穩定性試行:不適用。試行只認指定工作樹登記的唯一編排者,本會談在 lumos-room-test 工作樹、沒有登記,照一般代碼審走。
- 收貨機械三道:report-normalize 兩份都已是正規格式;quote-check 兩份全數錨定(正確性 5 句、架構 4 句);refcheck 架構 21 處 ok、正確性 0 處(只引函式名);seat-check 印「派工單沒列任何要查的材料」——派工單的 materials 放在 seats 陣列裡、工具讀頂層,判成 vacuous。這是編排者寫派工單的格式失誤,派工單是證據不改,本輪照實記;r2 起 materials 放頂層。
- 收貨時 `git status`:只有本卷證目錄是新檔,repo 沒被席位動過;正確性席自述已用字面路徑刪掉自己的臨時目錄。
- 圖譜固定席:兩席都回報派工詞尾端沒有附固定席節點(鏡頭計算約 44 秒,接近 45 秒上限),也沒有新增殘留段;本 diff 沒有新增殘留或合約行。

## id 對照

| id | 席 | 原條 | severity | 一句 |
|---|---|---|---|---|
| c1 | 正確性 | F1 | major | mock 只認 mockk<Dao>(),四種常見寫法放行 |
| c2 | 正確性 | F2 | major | 整個專案沒有結構檔時碰 Room 就擋,補法做不到 |
| c3 | 正確性 | F3 | minor | 整段刪掉方法會要求鄰居補測試 |
| c4 | 正確性 | F4 | minor | 只改常數檔升版、沒結構檔時整個不觸發 |
| a1 | 架構對齊 | F1 | major | 剝註解另寫第二支 |
| a2 | 架構對齊 | F2 | major | 分岔點自己重組一份主線候選 |
| a3 | 架構對齊 | F3 | minor | 找 repo 根與起點沒用既有小函式 |
| a4 | 架構對齊 | F4 | minor | 索引表把 reread- 子指令名縮短 |

## 重現表(編排者機械重現,先寫測試、修前跑)

| id | 重現 | 結果 |
|---|---|---|
| c1 | `python3.14 scripts/test_lumos.py -k room_dao_mock_forms_all_count`(修前) | HIT:型別在變數上 mockk(relaxed)/mockk()、mock<OrderDao>()、@RelaxedMockK 同一行四項紅;@MockK 換行、Java 三種、mockk<>(relaxed) 原本就擋 |
| c2 | `-k room_mig_never_exported_warns_not_blocks`(修前) | HIT:四條斷言全紅,印「結構檔最大只到 0」並擋下 |
| c3 | `-k room_dao_whole_method_deletion_no_neighbor`(修前) | HIT:兩種刪法都擋下、點名鄰居 |
| c4 | `-k room_mig_constant_bump_without_schema_blocks`(修前) | HIT:三種常數寫法都 rc0(不觸發);同名兩值對照組 rc0 |
| a1 | `-k strip_c_comments_keep_newlines`(修前) | HIT:`_strip_c_comments` 沒有 keep_newlines,例外 |
| a2 | 讀碼:`_rg_fork_point` 自組 `_push_mainlines` + `merge-base --all` + `_push_pick_base`,`_push_range_start` 說明寫「起點只在這裡算一處」 | HIT(讀碼) |
| a3 | 讀碼:`_rg_root`、`_rg_range` 與 `_note_audit_root`、`_note_audit_start` 同形 | HIT(讀碼) |
| a4 | `git diff faecd422 -- skills/lumos-project-notes/commands/INDEX.md` | HIT:原本 `reread-prepare·reread-record·reread-check` |

## 判讀與處置

- c1 折:mock 認法統一成四種形狀(泛型參數、傳類別、型別標在變數上、欄位註記),不逐個寫法補。同族一起掃:測試含 Kotlin 七種、Java 三種與「mock 別的型別、DAO 用真的」對照組。
- c2 折:觀察對(沒匯出位置的專案碰 Room 就擋、補法做不到);判準自己重想後擴成同族兩條——整個專案沒有結構檔只提醒一次怎麼設匯出位置;[S5] 只判這次碰到的資料庫(原始碼、常數定義檔或結構檔目錄有改),主線上本來就有的缺口不擋碰到別處的推送(架構席 ⚠4 上線點截斷的同一個理由)。另補 `t_room_mig_untouched_db_old_gap_not_blocked`。
- c3 折:純刪除記成刪除點兩行之間(c+0.5),方法範圍含它等於前後兩行都在同一個方法裡;[S26] 方法裡刪一行照舊要求。
- c4 折:[S5] 遇到常數版本,到非測試原始碼找 `val/int 名稱 = 整數`,恰好一個值才用;改到定義它的檔也算觸發。升級路徑那半仍以結構檔為準。
- a1 折:`_strip_c_comments` 加 keep_newlines,`_rg_strip` 只轉呼叫它。
- a2 折:`_rg_fork_point` 改問 `_push_range_start(舊值全 0)`,不再自組。
- a3 折:改用 `_note_audit_root`、`_note_audit_start`。
- a4 折:改寫成 `reread-{prepare,record,check}`(索引上限 4500 字,改後剛好 4500)。
- 架構席 ⚠ 交編排者五項(不是 finding,不進帳):⚠1 測試路徑判斷第四支——鄰居四支規則本來就不同、沒有單一標準可對,不改;⚠2 判不了放行——WHY 已寫取捨,不改;⚠3 CI 後盾沒有回頭條件——成立,補 `REVISIT:2027-01-31` 到 Systems/room-guard、掛鉤註解改指向它;⚠4 上線點截斷——由 c2 的「只判碰到的資料庫」處理;⚠5 第三處 @@ 解析——已用共用的差異讀取與檔頭判斷,沒有統一出口可對,不改。
- 正確性席「gate=block 只有提醒時記成 passed」小瑕疵:席位沒立 finding,不進帳;提醒照樣印在推送輸出。

## 修補紀錄

- 每條先紅後綠;修後 `-k room` 123 條斷言全綠,另補的舊缺口測試 2 條斷言綠。改壞檢查逐道一次,結果見下方。
- 改壞檢查(每道新判斷各改壞一次、清 __pycache__、跑對應測試,跑完還原並核對雜湊):mock 四種形狀各拿掉一條、純刪除改回前後兩行、純刪除改成不記、沒結構檔只提醒那段拿掉、只判碰到的資料庫那條拿掉、常數檔改到不觸發、常數值不解、常數兩個值也取一個、只判碰到時漏算常數檔、保留換行拿掉——13 道全紅。
