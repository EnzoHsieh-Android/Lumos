---
type: system
status: doing
created: 2026-10-28
updated: 2026-10-28
responsibility: 負責 lumos room-guard 推送前 Room 守衛:升級那半(結構檔、升級路徑、升級測試、主線上結構檔被改或刪)、DAO 與型別轉換那半、它的設定與治理帳事件,以及推送前掛鉤裡呼叫它的那一段;不負責範圍起點與主線候選的算法(推送範圍那幾支共用函式)、測試品質規範裡 Room 一節的內容(test-quality-cli)、其他閘的順序(bound-tests-gate)
aliases: []
about_code:
  - scripts/lumos
  - scripts/hooks/pre-push
tags:
  - type/system
  - status/doing
  - scope/guards-gates
summary: |-
  WHY:升級那半以 Room 匯出的結構檔為準,不從原始碼猜版本號 [出處:[[Projects/Room資料庫測試守衛_計劃]] 設計審 r1] [因:版本號常寫成常數、類別名前常疊 @TypeConverters、巢狀類別與搬套件都讓原始碼解析猜錯;結構檔目錄名就是 Room 自己認的類別完整名稱] [不選:只看改動的 @Database 檔(改常數檔、刪 Migration 都漏掉)] [test:t_room_mig_constant_version_uses_schema]
  WHY:升級那半跟「與主線的分岔點」比,不跟這次推送的起點比 [出處:同計劃設計審 r1] [因:主線上的版本才可能已經發給使用者;只在分支上的版本反覆編譯改寫、退回、刪掉都是正常開發] [不選:跟範圍起點比(第二次推送就把自己分支上的版本當成已發布)] [test:t_room_mig_schema_rewrite_branch_only_passes]
  WHY:DAO 測試認「沒 mock 這個 DAO 的測試以 .方法名( 呼叫它」加「全庫至少一支真 Room 測試」,不要求同一支檔有 Room 建法 [出處:同計劃設計審 r1] [因:資料庫常建在基底類別、JUnit Rule 或 Hilt 測試模組] [代價:名字撞名的方法會被別的 DAO 的測試放行] [test:t_room_dao_test_via_base_class_passes]
  WHY:判不清一律講一句放行並記帳,跟 Android 端到端驗收的判不清就擋刻意不同 [出處:同計劃〈實務隱患〉] [因:這道是靜態看程式碼形狀,git 算不出來時擋下等於工具壞了就擋所有人] [test:t_room_guard_range_start_tag_and_empty]
  SEE:[[Systems/test-quality-cli]] [[Systems/bound-tests-gate]] [[Projects/Room資料庫測試守衛_計劃]]
  WHY:原始碼那邊的「這一版結構檔沒提交」只判這次碰到的資料庫,整個專案一個結構檔都沒有時只提醒怎麼開匯出 [出處:代碼審 code-room資料庫測試守衛 r1 正確性席] [因:沒設匯出位置時訊息教的補法做不到;主線上本來就有的缺口不該擋碰到別處的推送] [不選:每次碰到 Room 就判全部資料庫] [test:t_room_mig_never_exported_warns_not_blocks]
  REVISIT:2027-01-31 看 room-guard 的擋下、跳過帳與誤擋回報,決定要不要在 CI 補一步(推送時加 --no-verify 就繞得過推送前掛鉤)
verified_by:
  - "[[Verification/2026-10-28_Room守衛實驗專案實跑]]"
---
# room-guard

推送前看 Android 專案的 Room 資料庫與 DAO 有沒有該有的升級路徑、結構檔與測試。子指令與它的判斷都在 `scripts/lumos`(函式名都以 `_rg_` 開頭,入口 `cmd_room_guard`),推送前掛鉤 `scripts/hooks/pre-push` 裡排在存量漂移之後、回頭重讀之前的那一段呼叫它。

- 範圍起點與主線候選沿用推送閘的共用算法(掛鉤帶遠端與 ref 時同存量漂移檢查),這裡不另算一份;那套的家見 [[Systems/bound-tests-gate]] 列的推送閘順序。
- 測試要怎麼寫才對(七種情況、mock 與真 Room 的分工、故障挑選)不在這裡判,寫在測試品質規範的 Room 一節,家在 [[Systems/test-quality-cli]]。
- 設定鍵:`.lumos/config.json` 的 `room_guard.gate`、`room_guard.dao`(各 block/warn/off)、`room_guard.allow_destructive`(類別完整名稱清單);單次跳過 `LUMOS_SKIP_ROOM_GUARD=1`。治理帳閘名 `room-guard`:blocked、warned、skipped、skipped-env 記版控帳,有觸發而放行的 passed 記本機帳。
