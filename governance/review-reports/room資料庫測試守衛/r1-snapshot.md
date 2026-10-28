---
type: project
status: doing
created: 2026-10-28
updated: 2026-10-28
tags:
  - type/project
  - status/doing
  - scope/guards-gates
summary: |-
  FLAG:TECHNICAL
  WHY:推送前加一道 Room 守衛,只判程式碼看得出來的事:資料庫版本號變大時每一步有沒有升級路徑、新版本的結構檔有沒有提交、升級測試有沒有跟著動;已提交的結構檔被改了雜湊;這次改到的 DAO 方法與型別轉換有沒有測試提到它(DAO 要用真的 Room) [出處:2026-10-28 Enzo 裁「做 1、2」「希望覆蓋到 Room 的所有測試情況」並選「規範全寫、檢查加 DAO」] [因:升級出錯會在使用者手機上閃退或清資料、DAO 只用 mock 測證不了 SQL,而官方與社群都沒有現成的推送前檢查] [不選:題組表態(只問不擋)、推送前故障注入(要編譯跑 Android 測試,太慢)]
  WHY:測試品質規範補 Android 資料層一節,把七種情況(查詢、資料限制、交易、升級、Flow/LiveData 重送、型別轉換、預載資料庫)的測法寫齊 [出處:2026-10-28 乾淨 agent 盤點] [因:規範裡 Laravel 有整段資料庫測試,Android 只有一句;AI 寫測試時先讀這份;測試寫得對不對機械判不了,只能靠規範與審查]
lands_in:
  - Systems/room-guard
  - Systems/test-quality-cli
related:
  - "[[Projects/Android端到端驗收_計劃]]"
  - "[[Systems/bound-tests-gate]]"
---
# Room資料庫測試守衛_計劃

> 題目一句:Android 專案改了 Room 的資料庫版本、結構、DAO 或型別轉換,推送前要能機械地看出「該有的升級路徑、結構檔、測試」有沒有缺;另外把 Android 資料層的測試寫法補進測試品質規範。
> 派工者:Enzo 2026-10-28 裁「先網上調研,然後準備接入,做 1、2,然後在實驗專案上測試」,中途補「希望可以覆蓋到 Room 的所有測試情況」,選「規範全寫、檢查加 DAO」。

## 緣起

- 乾淨 agent 2026-10-28 盤點:Lumos 對 Room 測試沒有任何專門支援;Kotlin 題組刻意排除 Room(怕誤判成 Spring),測試品質規範的 Android 列只有「Robolectric、裝置分開,JVM 不等於 Android」一句。
- Room 升級出錯的後果在使用者手機上:找不到升級路徑會丟 `IllegalStateException` 閃退;開了 `fallbackToDestructiveMigration()` 則是靜默清空資料(官方文件 migrating-db-versions)。
- DAO 用 mock 測時 SQL 根本沒執行,查詢條件、資料限制、交易回滾寫錯都會假裝成功。

## 調研(2026-10-28 網搜與官方文件)

- 官方測試頁(training/data-storage/room/testing-db):建議在裝置上跑 JUnit 測試;Room KMP 可在本機 JVM 跑並搭 `BundledSQLiteDriver`(電腦、Android、iOS 用同一份 SQLite);**明寫「不建議用 Robolectric 跑 Android 本機單元測試,改用 Room KMP 的本機 JVM 測試」**;測試要用記憶體資料庫;DAO 可 mock,但那只在「不是在測資料庫本身」時成立。
- 官方升級頁:自動升級寫在 `@Database(autoMigrations = [AutoMigration(from = 1, to = 2)])`;手寫升級是 `object : Migration(1, 2)` 並 `addMigrations`;找不到路徑丟 `IllegalStateException`;`MigrationTestHelper` 依賴匯出的結構檔;官方建議另有一支跑完全部升級的測試。
- 結構檔慣例:Room 編譯時把結構寫成 `<結構目錄>/<資料庫類別完整名稱>/<版本>.json`,內含 `identityHash`;版本號沒變但結構改了,重新編譯會覆寫同一個版本的檔(identityHash 變了)。
- 社群:Robolectric 跑 `MigrationTestHelper` 要把結構檔加進 debug 的 assets(測試資料夾的 assets 讀不到);沒找到任何現成的「版本變了升級沒跟上」或「DAO 沒真測」的 CI 檢查或 lint 規則,大家各自寫腳本。

PRIOR-ART: 推送前閘的形狀照抄筆記形狀擋與每支檔有家(子指令帶 `--diff A..B --repo`、內容一律從被推的提交讀、rc1 擋 rc0 放、`LUMOS_SKIP_*=1` 單次跳過留帳、`.lumos/config.json` 的 gate 設 warn/off、掛鉤裡 `pp_stop_if_signaled` 與 `pp_record_block`);判斷規則照 Room 官方文件的事實(升級路徑由 Migration 與 AutoMigration 組成、找不到路徑會閃退、結構檔是 MigrationTestHelper 的輸入、測資料庫本身要用記憶體資料庫);世界上沒找到現成的推送前檢查可借。
RETIRE-IF: 上線後半年內,用 Room 的消費專案裡這道擋下的次數中,一半以上被單次跳過或事後判成誤擋,或是連續半年零觸發而且沒有任何專案在用 Room——撤成只提醒(gate 預設 warn)或整道拿掉;DAO 那半另看:擋下後補的測試多半只是「提到名字」而沒驗結果(審查卷證裡被點出),把 DAO 那半降成提醒;另外如果 Room 官方出了在編譯或 lint 階段就擋同一件事的機制,改成要求專案開那個機制、對應那半撤掉。
REVISIT:2027-04-28 數治理帳裡 room-guard 的 blocked/skipped-env/warned 筆數與誤擋比例,對照 RETIRE-IF 判撤不撤

## 現況(2026-10-28 讀本工作樹 scripts/lumos 與掛鉤,以程式為準)

- 推送前掛鉤依序跑:裁判簽名、圖譜健檢、每支檔有家、筆記形狀擋、規格閘放行、代碼審判定(含 Android 端到端驗收)、存量漂移、回頭重讀,最後全套測試。
- 沒有任何一道讀 `@Database`、`@Dao`、Migration 或結構檔。

## 做法

1. **新子指令 `lumos room-guard --diff <起點>..<終點> [--repo <根>]`**,比範圍起點與被推的終點提交(起點照筆記形狀擋用的 `_lens_push_base` 算;掛鉤傳的是 `_brange`:一般推送是遠端舊值..本地頂端,新分支首推是跟主線的分岔點);內容全從提交讀,工作目錄沒提交的不算。判斷前先剝掉註解(註解裡的 `Migration(1, 2)` 不算)。
   - **測試路徑**:路徑裡有一段 `src/<名稱>/`,而 `<名稱>` 是 `test` 或以 `Test` 結尾(`androidTest`、`jvmTest`、`commonTest`、`androidUnitTest`、`androidInstrumentedTest` 都算);其他都是非測試路徑。
   - **結構檔**:路徑形狀 `<…>/<含點的類別完整名稱>/<整數>.json`,而且內容是 JSON、帶 `formatVersion` 與 `database.identityHash` 兩個鍵;只有形狀對、內容不是 Room 結構的 json 不算。
2. **升級那半**:
   - 找資料庫類別:改動過的 `.kt`/`.java` 檔含 `@Database(`(或 `@androidx.room.Database(`、`@androidx.room3.Database(`)的;類別名取註解後第一個 `class 名稱`,完整名稱 = 檔頭 `package` + 類別名;版本取註解參數裡的 `version = 整數`。
   - 只在「起點有、終點也有、版本號變了」時判(新寫的資料庫沒有舊使用者):
     - 版本變小 → 擋(Room 預設不支援降版)。
     - 版本變大(a → b)→ 要同時有:**升級路徑**(終點非測試路徑的 `Migration(x, y)` 與這個類別註解裡的 `AutoMigration(from = x, to = y)` 當成邊,從 a 走得到 b)、**結構檔**(a+1 到 b 每一版都有 `<…>/<完整名稱>/<版本>.json`;一個都沒有時另外講「沒匯出結構檔」)、**升級測試**(測試路徑裡有同時提到 `MigrationTestHelper` 與這個類別名的檔,而且它這次改過,或某行 `runMigrationsAndValidate(` 帶著 b)。
     - 版本判不出(寫成常數)→ 只提醒、不擋。
   - **已提交的結構檔被改**:範圍裡改到的 `<…>/<名稱>/<整數>.json`,起點就有、兩邊 `identityHash` 不同 → 擋(多半是結構改了忘記升版號);只改排版、雜湊一樣 → 放行。
3. **DAO 那半**:
   - 找 DAO:改動過的 `.kt`/`.java` 檔含 `@Dao` 的;方法 = 帶 `@Query`、`@Insert`、`@Update`、`@Delete`、`@Upsert`、`@RawQuery`、`@Transaction` 其中之一的函式。每個方法的範圍從它第一個註解行到下一個方法的第一個註解行之前。
   - **這次改到的方法**:檔是新的就全部算;否則終點上那個方法的範圍跟這次改動的行有交集就算。
   - 每個改到的方法要有一支測試路徑裡的檔,**同時**含真的 Room 建法(`inMemoryDatabaseBuilder` 或 `databaseBuilder`)、提到這個 DAO(類別名或首字小寫的變數名,例如 `OrderDao` 或 `orderDao`)、以單字提到方法名;只用 mock 的測試不算。
   - **型別轉換**:帶 `@TypeConverter` 的函式,這次改到的要有一支測試路徑裡的檔以單字提到函式名(型別轉換是純函式,不要求真的 Room)。
4. **允許清空的資料庫**:`.lumos/config.json` 的 `room_guard.allow_destructive` 列出的完整類別名(例如純快取的資料庫),升級那半不要求路徑、結構檔與測試。
5. **開關與逃生**:`room_guard.gate` 為 `block`(預設)/`warn`/`off`,管整道;`room_guard.dao` 為 `block`(預設)/`warn`/`off`,只管 DAO 與型別轉換那半(讓專案可以先只提醒 DAO、升級照擋);`LUMOS_SKIP_ROOM_GUARD=1` 單次跳過並記治理帳;擋下與提醒才記帳,沒事的放行不記。不是 git、淺層 clone、git 算不出來 → 講一句、放行(淺層 clone 另記一筆 skipped-env,跟筆記形狀擋一樣)。
6. **接進推送前掛鉤**:接在筆記形狀擋那個 `if [[ -n "$_hrange" ]]` 區塊之後、區塊外面(`_hrange` 是空的時候照樣判),用會擋的範圍 `_brange`;跟鄰居一樣先過 `pp_stop_if_signaled`、回 1 用 `pp_record_block room-guard` 記下(所有閘跑完、全套測試之前統一擋,跟其他閘同一個判斷點);其他非零(含舊版 lumos 沒有這個子指令回 2)印一句「Room 守衛這次沒檢查(rc=N),放行」,照存量漂移那段的寫法,不靜默。掛鉤「中斷就停」清單加一行、假 lumos 認得 `room-guard`。CI 第一版不接(跟 Android 端到端驗收第一版同樣只在本機推送時判)。
7. **測試品質規範補〈Android 資料層(Room)的撰寫補充〉一節**:七種情況(查詢、資料限制、交易、升級、Flow/LiveData 重送、型別轉換、預載資料庫 `createFromAsset`)各一條怎麼測與常見假綠;mock DAO 只證 Repository 自己的邏輯;記憶體資料庫;官方不建議 Robolectric、建議 Room KMP 本機 JVM 加 `BundledSQLiteDriver`,裝置上另跑;升級用 `MigrationTestHelper` 加一支跑完全部升級的測試、Robolectric 時結構檔進 debug assets;故障挑選方向;並寫明這道守衛只證「有測試提到」,不證測試寫得對。`03-寫回圖譜.md`〈實作測試品質〉加一句指過去。

## 驗收條款

- [S1] 當 `@Database` 版本從 1 改成 2、終點沒有任何 `Migration(1, 2)` 或 `AutoMigration(from = 1, to = 2)` 時,`room-guard` 應回 1,訊息點名資料庫類別與缺的那一步 1→2。[test: t_room_mig_bump_without_path_blocks]
- [S2] 當版本從 1 改成 2、終點有 `Migration(1, 2)`、`<完整名稱>/2.json`、而且這次改過一支提到 `MigrationTestHelper` 與類別名的測試時,應回 0。[test: t_room_mig_bump_with_all_parts_passes]
- [S3] 當升級路徑只寫在註解參數 `AutoMigration(from = 1, to = 2)` 時,應算有路徑。[test: t_room_mig_automigration_counts]
- [S4] 當版本從 1 改成 3、終點只有 `Migration(1, 3)` 時,應算有路徑;只有 `Migration(1, 2)` 時應回 1 並點名 2→3。[test: t_room_mig_multistep_path]
- [S5] 當版本從 1 改成 2、路徑與測試都有、但終點沒有 `<完整名稱>/2.json` 時,應回 1 並點名缺的結構檔。[test: t_room_mig_missing_schema_json_blocks]
- [S6] 當版本從 1 改成 2、路徑與結構檔都有、但沒有任何符合條件的升級測試時,應回 1 並說缺升級測試。[test: t_room_mig_missing_test_blocks]
- [S7] 當起點就有的 `<名稱>/1.json` 在終點 `identityHash` 變了、版本號沒變時,應回 1,訊息說結構改了沒升版。[test: t_room_mig_schema_changed_without_bump_blocks]
- [S8] 當起點就有的結構檔只改排版、`identityHash` 相同時,應回 0。[test: t_room_mig_schema_reformat_passes]
- [S9] 當版本從 2 改成 1 時,應回 1 並說降版。[test: t_room_mig_downgrade_blocks]
- [S10] 當版本寫成 `version = DB_VERSION` 這類常數時,應回 0 並印一行「提醒:」說判不出版本號。[test: t_room_mig_unresolved_version_warns]
- [S11] 當 `@Database` 類別是這次新增的檔(起點沒有)時,升級那半應不要求路徑、結構檔與測試。[test: t_room_mig_new_database_no_requirement]
- [S12] 當範圍裡沒有任何 `@Database`、`@Dao`、`@TypeConverter` 檔與結構檔改動時,應回 0、不印任何東西、不寫治理帳。[test: t_room_guard_unrelated_diff_silent]
- [S13] 當設了 `LUMOS_SKIP_ROOM_GUARD=1` 而本來會擋時,應回 0,治理帳多一筆 room-guard 的 skipped-env。[test: t_room_guard_skip_env_records]
- [S14] 當終點的 `.lumos/config.json` 把 `room_guard.gate` 設成 `warn` 時,本來會擋的情況應回 0、印「提醒:」並記一筆 warned;設成 `off` 時應回 0 且不判。[test: t_room_guard_gate_warn_and_off]
- [S15] 當 `Migration(1, 2)` 只存在工作目錄、沒有提交時,應照樣回 1。[test: t_room_guard_reads_tip_not_worktree]
- [S16] 當 `Migration(1, 2)` 只出現在註解裡(`//` 或 `/* */`)時,應不算路徑。[test: t_room_mig_commented_migration_ignored]
- [S17] 當資料庫類別用 Java 寫(`@Database(entities = {User.class}, version = 2)`、`new Migration(1, 2)`)時,應跟 Kotlin 一樣判。[test: t_room_mig_java_syntax]
- [S18] 當類別完整名稱列在 `room_guard.allow_destructive` 時,版本變大而沒有路徑、結構檔與測試應回 0。[test: t_room_mig_allow_destructive_listed]
- [S19] 當 DAO 新增一個 `@Query` 方法 `getUnpaid`、終點沒有任何真 Room 測試提到它時,應回 1,訊息點名 `OrderDao.getUnpaid`。[test: t_room_dao_new_method_without_test_blocks]
- [S20] 當終點有一支測試含 `inMemoryDatabaseBuilder`、提到 `orderDao` 與 `getUnpaid` 時,同一個改動應回 0。[test: t_room_dao_method_with_real_room_test_passes]
- [S21] 當唯一提到 `getUnpaid` 的測試只用 mockk、沒有任何 Room 建法時,應回 1,訊息說只用 mock 的測試不算。[test: t_room_dao_mock_only_test_blocks]
- [S22] 當既有 DAO 只改了 `getPaid` 那個方法的行時,應只要求 `getPaid` 有測試,同檔其他沒改的方法不要求。[test: t_room_dao_only_changed_methods_required]
- [S23] 當 `@Transaction` 方法只改了函式本體(註解與簽名沒變)時,應算改到、要求測試。[test: t_room_dao_transaction_body_change_required]
- [S24] 當新增一個 `@TypeConverter` 函式 `fromInstant` 而沒有測試提到它時,應回 1;有任何一支測試以單字提到 `fromInstant` 時應回 0。[test: t_room_typeconverter_needs_test]
- [S25] 當 `room_guard.dao` 設成 `warn`、同一次推送同時缺 DAO 測試與升級路徑時,DAO 那條應只印「提醒:」,升級那條照樣讓它回 1。[test: t_room_dao_warn_separate_from_migration]
- [S26] 當推送前掛鉤跑到這道而它回 1 時,應記一筆 room-guard 擋下、在全套測試之前跟其他閘一起擋;它回 2 時應印「這次沒檢查」並放行;它被訊號殺掉時應整支掛鉤停下,而且「中斷就停」清單有這一行。[test: t_prepush_room_guard_wired]
- [S27] 當讀 test-quality-standard.md 時,應有 Android 資料層(Room)一節,依序提到查詢、資料限制、交易、升級、Flow、TypeConverter、createFromAsset 七種情況,並提到記憶體資料庫、`MigrationTestHelper`、`BundledSQLiteDriver` 與官方不建議 Robolectric;03-寫回圖譜.md〈實作測試品質〉有一句指到那一節。[test: t_test_quality_standard_android_room_section]
- [S28] 當在實驗專案 macrobench-lab(本機 `/Users/enzo/orca/workspaces/macrobench-lab`,另開獨立工作樹做)加 Room 資料庫 v1(含 DAO 與真 Room 測試)、再升 v2 時,漏了 Migration 或新 DAO 方法沒測試推送前應被擋,補齊後應放行,而且升級測試與 DAO 測試實跑是綠的。[manual: 實驗專案 macrobench-lab 的獨立工作樹裡實跑,收據記進 Verification]

## 回退(由後往前)

- 第 7 步:測試品質規範那一節與 03 的指向句還原提交,不影響任何程式。
- 第 6 步:掛鉤那段還原;要先停就在消費專案設 `room_guard.gate: off`(只停 DAO 那半設 `room_guard.dao: off`),不用改掛鉤。
- 第 1–5 步:子指令整支還原;舊版掛鉤沒有呼叫它,新版掛鉤配舊版 lumos 時子指令不存在會回 2,掛鉤照「其他非零放行」講一句放行。

## 實務隱患

- **誤擋(升級)**:同一個版本還沒發布給使用者(只在開發分支上),又改了一次結構,結構檔雜湊那條會擋;擋下訊息要講「這個版本還沒發布可以單次跳過」。
- **誤擋(DAO)**:只改了註解或排版也算改到方法;第一次接入的專案,碰到舊 DAO 的任一方法就要補那個方法的測試——這是刻意的(邊改邊補),`room_guard.dao: warn` 是過渡用的逃生。
- **一個專案多個資料庫**:`Migration(x, y)` 不帶類別資訊,A 資料庫的升級物件會被算進 B 的路徑;判不出時寧可放行,寫進誠實界線。
- **名稱撞名**:兩個 DAO 都有 `insert`,測試提到另一個 DAO 的 `insert` 也可能被算到;要求同檔也提到這個 DAO 的名字來降低機率,不保證。
- **效能**:只讀改動檔、改動行號與終點的測試檔內容(一次 `git grep` 列出測試路徑裡含 Room 建法或 `MigrationTestHelper` 的檔);大 repo 也只多幾次 git 呼叫。
- **相容**:掛鉤配舊版 lumos(沒有這個子指令)回 2 要放行,不能擋所有人。
- **判不清時放行,跟 Android 端到端驗收的「判不清就擋」刻意不同**:那道判的是實機驗收紀錄,判不清代表驗收狀態不明;這道是靜態看程式碼形狀,跟筆記形狀擋、每支檔有家同類,git 算不出來時擋下等於工具壞了就擋所有人;判不清的情況各自印一句提醒,讓人看得到這次沒判。
- 已排除:金流:這道只讀提交裡的程式碼與結構檔,不碰任何付款流程
- 已排除:對外送出:不打網路、不呼叫任何外部服務,只跑本機 git
- 已排除:不可逆:這道只擋推送、不改任何檔或資料;計劃裡的「Migration」是被檢查對象的名字,不是這道會做的動作,還原提交就回到原狀
- **守衛面(不排除)**:這道本身就是新的推送前閘,所以照風險高走設計審;不改既有任何一道閘的判定,只在掛鉤裡多一段呼叫。

## 誠實界線

- 只證「程式碼裡有升級路徑、結構檔,以及有測試提到這個方法」,**不證測試跑過、跑綠,也不證測試真的驗了結果**;跑綠要靠專案的 CI 或 Android 端到端驗收,驗得對不對要靠測試品質規範與審查。
- 改了 Entity 卻沒重新編譯(結構檔沒更新)時看不出來——要編譯才知道結構變了,這道不跑 Gradle。
- `Migration(x, y)` 沒辦法對到哪個資料庫;多資料庫專案可能被別的資料庫的升級物件放行。
- 資料限制(主鍵、唯一、外鍵)、Flow 重送、預載資料庫這三種情況沒有可靠的程式碼訊號對應到「該有哪支測試」,只寫在規範裡、守衛不判。
