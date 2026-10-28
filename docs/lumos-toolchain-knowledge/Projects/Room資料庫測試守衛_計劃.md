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
  WHY:推送前加一道 Room 守衛,只判程式碼看得出來的事:資料庫升版時升級路徑、新版本的結構檔、升級測試有沒有跟上,主線上已有的結構檔有沒有被改或刪;這次改到的 DAO 方法有沒有沒被 mock 的測試呼叫到它(全庫要有真 Room 測試);型別轉換只提醒 [出處:2026-10-28 Enzo 裁「做 1、2」「希望覆蓋到 Room 的所有測試情況」並選「規範全寫、檢查加 DAO」] [因:升級出錯會在使用者手機上閃退或清資料、DAO 只用 mock 測證不了 SQL,而官方與社群都沒有現成的推送前檢查] [不選:題組表態(只問不擋)、推送前故障注入(要編譯跑 Android 測試,太慢)]
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
RETIRE-IF: 以治理帳量(room-guard 的 blocked/skipped-env/warned/passed):上線後半年內,所有消費專案合計 skipped-env 筆數達 blocked 的一半以上 → 整道撤成只提醒(gate 預設 warn);其中只因 DAO 種類被擋的那些 blocked,跳過比例達一半以上 → 只把 DAO 那半預設改 warn;半年內沒有任何 passed 或 blocked(沒人用 Room 或都沒碰到)→ 整道拿掉。
REVISIT:2027-04-28 數治理帳裡 room-guard 各類筆數對照 RETIRE-IF 判撤不撤;同時查 Room 2 與 Room 3 的版本說明,官方若已在編譯或 lint 階段擋同一件事,改成要求專案開那個機制、對應那半撤掉

## 現況(2026-10-28 讀本工作樹 scripts/lumos 與掛鉤,以程式為準)

- 推送前掛鉤依序跑:裁判簽名、圖譜健檢、每支檔有家、筆記形狀擋、規格閘放行、代碼審判定(含 Android 端到端驗收)、存量漂移、回頭重讀,最後全套測試。
- 沒有任何一道讀 `@Database`、`@Dao`、Migration 或結構檔。

## 做法

1. **新子指令 `lumos room-guard --diff <遠端舊值>..<終點> [--push-remote <遠端名> --pushed-ref <遠端 ref>] [--repo <根>]`**,內容全從提交讀,工作目錄沒提交的不算。
   - **範圍起點**:帶了 `--push-remote`/`--pushed-ref`(掛鉤)就照存量漂移檢查,交給 `_push_range_start` 算(推 tag、force push 後舊值找不到、合過主線都由它處理,不另算一份),它回 `(起點, 說明)`,起點分四種處理:一般提交 → 照判;`None`(終點已在主線上、沒有新東西)→ 一句、rc0、記 skipped;`_PUSH_START_UNKNOWN`(git 查詢失敗)→ 一句「這次沒檢查」、rc0、記 skipped;**空樹 → 一句「找不到可比的歷史,這次不判」、rc0、記 skipped**(不把整個 repo 當新改動)。手動跑沒帶就用 `_lens_push_base`(它不判主線;回 `None` 時同上一句、rc0、記 skipped)。**不截上線點**(筆記形狀擋的 `_nodehome_clamp_base`):範圍已經只含這次推送真正的新提交,剛接入的專案第一次推送不會把舊 DAO 算進來。
   - **主線分岔點**:升級那半的比對一律拿終點跟「與主線的分岔點」比(主線候選照 `_push_range_start` 用的那套找,跟所有候選的 `merge-base`);主線上已有的版本才可能已經發給使用者,只存在這條分支上的版本怎麼改、退回、刪都不擋。找不到主線 → 改用範圍起點,而且結構檔改寫那條降成提醒。DAO 那半看的是範圍裡這次推送的改動。
   - **重用既有工具,不另寫**:git 呼叫走 `_lens_git`;範圍與狀態用 `_lens_range_ok`、`_lens_full_sha`、`_is_git_worktree`;列終點檔案用 `_nodehome_list`、讀提交裡的檔(含 `.lumos/config.json`)用 `_nodehome_reader`;差異解析用 `_diff_text_lines` 與 `_lens_diff_header`;設定照 `_note_shape_config` 的形狀寫一支讀終點文字、壞值回預設並附提醒字串的解析;剝程式註解重用 `_strip_c_comments` 背後的同一個掃描式 `_C_STRIP_PAT`,換一個替換函式:程式註解與字串內容換成空白、**保留換行**(行號才對得上差異),所以字串裡與程式註解裡的 `Migration(1, 2)` 都不算。
   - **測試路徑**:路徑裡有一段 `src/<名稱>/`,而 `<名稱>` 是 `test`、以 `test` 或 `androidTest` 開頭(`testDebug`、`testFixtures`、`androidTestDebug`),或以 `Test` 結尾(`jvmTest`、`commonTest`、`androidUnitTest`、`androidInstrumentedTest`);其他都是非測試路徑。找 `@Database`、`@Dao`、`Migration` 一律只看非測試路徑的 `.kt`/`.java`。
   - **結構檔**:路徑形狀 `<…>/<類別完整名稱>/<整數>.json`(預設套件沒有點也算);內容是帶 `formatVersion` 與 `database.identityHash` 的 JSON 才算 Room 結構檔。形狀對、看得出是 Room 結構檔(含 `formatVersion` 或 `identityHash` 字樣)卻讀不懂(合併衝突標記、截斷、非 UTF-8)→ 擋,訊息說「結構檔讀不懂」,不說「缺」;不含這兩個字樣的同形狀 json(例如資源檔)不算,不擋。
   - **觸發**:範圍裡的改動(含刪除與改名)碰到結構檔,或碰到起點或終點內容含 `@Database`、`@Dao`、`@TypeConverter`、`Migration`、`AutoMigration` 字樣的非測試 `.kt`/`.java` 檔才判;都沒碰到 → rc0、不印、不記帳。原始碼不是 UTF-8 時用替換字元讀,不中斷。
   - **用詞**:下面「註記」指 `@` 開頭的 annotation,「程式註解」指 `//` 與 `/* */`。
2. **升級那半(以 Room 自己匯出的結構檔為準)**:
   - **資料庫與版本**:一個資料庫 = 一個結構檔目錄(目錄名就是類別完整名稱,巢狀類別、常數版本號、`@TypeConverters(Converters::class)` 這類都不用從原始碼猜;同一支檔有好幾個 `@Database` 也各自一個目錄)。某個提交上的「目前版本」= 該目錄裡最大的整數。終點若找得到這個類別的 `@Database` 註記、而且 `version =` 是整數字面,這個數比結構檔最大值還大 → 擋「這一版的結構檔沒提交(多半沒重新編譯或沒加進提交)」。找類別:平衡括號跳過整個 `@Database(...)` 與其後其他註記,取第一個 `class 名稱`,巢狀時前面接外層類別名。
   - **改名搬家與刪除**:分岔點某目錄的結構檔在終點不見了,而終點另一個目錄有 `identityHash` 相同的檔 → 視為同一個資料庫搬家,接著照下面比;對不到 → 擋「主線上已有的結構檔被刪掉」。
   - **升級路徑不倒退**:用分岔點的程式算出「分岔點時能升到當時目前版本 a 的所有版本」(含 a),終點上這些版本每一個都要能走到終點目前版本 b。這一條同時涵蓋「升版沒寫路徑」與「版本沒變卻刪掉某條 Migration」。b < a → 擋「降版」(只存在分支上的升版被退回時,分岔點的 a 本來就比較小,不會擋)。
   - **邊怎麼認**:非測試路徑的 `Migration(整數, 整數)`(也認 `startVersion =`/`endVersion =` 具名),與 `AutoMigration(...)` 參數裡的兩個整數(`from =`/`to =` 具名任意順序,或位置參數)。終點有任何一個 `Migration(` 或 `AutoMigration(` 的參數不是整數字面(常數、工廠函式、自訂基底類別)時,路徑缺口改成只提醒「升級路徑寫法判不出」,不擋。多步升級只要求終點版本 b 的結構檔,不要求中間版本。
   - **升級測試**(b > a 時):測試路徑裡要有一支檔同時提到 `MigrationTestHelper` 與這個資料庫的類別簡名,而且(一)`runMigrationsAndValidate(` 或 `createDatabase(` 的參數裡以獨立數字出現 b,或(二)檔裡有 `addMigrations(*` 這種跑完全部升級的寫法(官方建議的那支)。
   - **沒匯出結構檔**:改動的 `@Database` 註記寫了 `exportSchema = false` → 提醒「這個資料庫沒匯出結構檔,這道判不了它的升級」,不擋。
   - **結構檔被改寫**:終點某個 `N.json` 的 `identityHash` 跟分岔點上同一檔不同 → 擋(主線上已有的版本被改,多半是結構改了忘記升版號);只存在這條分支上的版本重新編譯被改寫 → 不擋;找不到主線時這條降成提醒。擋下訊息要講兩件事:結構改了要升版號並寫升級路徑;確定這個版本還沒發布給使用者時可以單次跳過。
   - **允許清空的資料庫**:`.lumos/config.json` 的 `room_guard.allow_destructive` 列出的類別完整名稱,升級那半整個不要求。缺路徑而非測試程式裡有 `fallbackToDestructiveMigration` 時,擋下訊息多一句「現在的寫法會在使用者手機上清空這個資料庫」。
3. **DAO 那半**:
   - **DAO 與方法**:非測試路徑含 `@Dao` 的 `.kt`/`.java`。方法 = 宣告(`fun 名稱(` 或 Java 方法簽章)正上方連續的註記行裡,有 `@Query`、`@Insert`、`@Update`、`@Delete`、`@Upsert`、`@RawQuery`、`@Transaction` 其中之一;疊好幾個註記也只算一個方法。**範圍**:從正上方連續註記的第一行,到宣告結束——沒有本體到參數括號閉合那一行,有本體到對應的右大括號,`=` 單行運算式到那一行。範圍以外的行(輔助函式、companion、檔尾)不算任何方法的。
   - **改到**:差異用 git 的改名偵測對應起點檔;終點上的改動行 = 每段差異新增的行,純刪除的那段算刪除點前後兩行。方法範圍跟改動行有交集,或方法在起點不存在,就算改到;只搬家改套件名的 DAO,只有真的改了的行算。
   - **測試認定**:測試路徑裡有一支檔以 `.方法名(` 的成員呼叫形式提到它,而且那支檔沒有把這個 DAO 型別做成 mock(`mockk<名稱>`、`mockk(名稱`、`mock(名稱::class`、`mock(名稱.class`,或 `@MockK`/`@Mock` 標在型別是這個 DAO 的屬性上)。資料庫建在基底類別、JUnit Rule 或 Hilt 測試模組都可以,不要求同一支檔有建法;但**整個終點的測試路徑裡至少要有一支檔用到真的 Room 建法**(`inMemoryDatabaseBuilder` 或 `databaseBuilder`;同一支檔有 `mockkStatic(Room` 或 `mockStatic(Room` 的不算),一支都沒有 → 這半全部擋,訊息說「沒有任何用真 Room 的測試」。
   - **型別轉換**:改到的 `@TypeConverter` 函式沒有任何測試提到 → 只提醒(常見的測法是經 DAO 存取一圈,名字不會出現在測試裡)。
4. **開關與逃生**:`room_guard.gate` 為 `block`(預設)/`warn`/`off`,管整道;`room_guard.dao` 同三值,只管 DAO 與型別轉換那半;壞值照預設並印提醒(同 `_note_shape_config`)。`LUMOS_SKIP_ROOM_GUARD=1` 單次跳過並記 skipped-env。淺層 clone → 一句、記 skipped-env。`--diff` 格式不對 → rc2;終點全 0(刪分支)→ 一句、rc0;單次 git 逾時 → 一句「這次沒檢查」、rc0、記 skipped。
5. **治理帳**:閘名 `room-guard` 加進 `_KNOWN_GATES`。記 blocked(附這次擋的種類:升級/結構檔/DAO)、warned、skipped、skipped-env;**有觸發而放行時記一筆 passed**,只帶判了幾個資料庫、幾個 DAO 方法(RETIRE-IF 要分得出「沒人用 Room」跟「用了都過」);沒觸發不記。
6. **接進推送前掛鉤**:照存量漂移那段的形狀,排在存量漂移那段之後、回頭重讀那段之前(不放在筆記形狀擋那個 `if` 區塊裡):`room-guard --diff "$_rsha..$_lsha" --push-remote "$_PP_REMOTE" --pushed-ref "$_rref"`,分支與 tag 都跑;先過 `pp_stop_if_signaled`;回 1 → 印逃生段(照上面各條修、確定還沒發布的結構檔改寫單次跳過 `LUMOS_SKIP_ROOM_GUARD=1`、整個專案先只提醒 `room_guard.gate: warn`、只鬆 DAO 那半 `room_guard.dao: warn`)並 `pp_record_block room-guard`(所有閘跑完、全套測試前統一擋);其他非零(含舊版 lumos 沒有這個子指令回 2)→ 印「Room 守衛這次沒檢查(rc=N),放行」。CI 第一版不接。
   - **要一起改的登記處**:`_KNOWN_GATES`、子指令說明表(`HELP_WHEN`)、argparse 與入口分派、掛鉤「中斷就停」清單加一行並更新那行的道數說明、測試裡的假 lumos 認得 `room-guard`、`skills/lumos-project-notes/commands/INDEX.md` 與 06-代碼審與推送.md 的指令速查。掛鉤與 `scripts/test_lumos.py` 是裁判簽名檔,改了要 `lumos anchor approve`,照規矩先跟使用者說明改了什麼、拿到使用者那一次的核可才簽。
7. **測試品質規範補〈Android 資料層(Room)的撰寫補充〉一節**(照〈網頁前端〉一節的形狀,家在 [[Systems/test-quality-cli]]):七種情況(查詢、資料限制、交易、升級、Flow/LiveData 重送、型別轉換、預載資料庫 `createFromAsset`)各一條怎麼測與常見假綠;mock DAO 只證 Repository 自己的邏輯;記憶體資料庫;官方不建議 Robolectric、建議 Room KMP 本機 JVM 加 `BundledSQLiteDriver`,純 Android 模組的真 Room 測試實務上在裝置或模擬器上跑(交給 CI 或 Android 端到端驗收);升級用 `MigrationTestHelper` 加一支跑完全部升級的測試,`exportSchema` 要開;Room 2(`androidx.room`)與 Room 3(`androidx.room3`)名稱對照;Robolectric 跑升級測試時結構檔進 debug assets **標明是社群做法**;故障挑選方向(拿掉 WHERE 條件、拿掉 `@Transaction`、刪掉一條 Migration);並寫明守衛只證「有測試提到」,不證測試跑過或寫得對。`03-寫回圖譜.md`〈實作測試品質〉加一句指過去。

## 驗收條款

- [S1] 當結構檔目錄從 `1.json` 長到 `2.json`、終點沒有任何 `Migration(1, 2)` 或對應的 `AutoMigration` 時,`room-guard` 應回 1,訊息點名資料庫類別與缺的那一步 1→2。[test: t_room_mig_bump_without_path_blocks]
- [S2] 當版本從 1 升到 2、終點有 `Migration(1, 2)`、`2.json`、以及一支提到 `MigrationTestHelper` 與類別簡名、`runMigrationsAndValidate(` 參數帶 2 的測試時,應回 0。[test: t_room_mig_bump_with_all_parts_passes]
- [S3] 當升級路徑寫成 `AutoMigration(from = 1, to = 2)`、`AutoMigration(to = 2, from = 1)` 或 `AutoMigration(1, 2)` 任一種時,應算有路徑。[test: t_room_mig_automigration_forms_count]
- [S4] 當版本從 1 升到 3、終點只有 `Migration(1, 3)` 與 `3.json`(沒有 `2.json`)時,應回 0;只有 `Migration(1, 2)` 時應回 1 並點名 2→3。[test: t_room_mig_multistep_path]
- [S5] 當 `@Database` 註記寫 `version = 2`、結構檔目錄最大只有 `1.json` 時,應回 1,訊息說這一版的結構檔沒提交。[test: t_room_mig_missing_schema_json_blocks]
- [S6] 當版本從 1 升到 2、路徑與結構檔都有、但沒有符合條件的升級測試時,應回 1 並說缺升級測試。[test: t_room_mig_missing_test_blocks]
- [S7] 當唯一的升級測試用 `addMigrations(*ALL_MIGRATIONS)` 跑完全部升級、沒有寫出數字 2 時,應算有升級測試。[test: t_room_mig_migrate_all_test_counts]
- [S8] 當 `1.json` 在與主線的分岔點就存在、終點的 `identityHash` 變了時,應回 1,訊息講要升版號、以及確定還沒發布時可以單次跳過。[test: t_room_mig_schema_changed_on_mainline_blocks]
- [S9] 當 `2.json` 只存在這條分支上(主線沒有)、第二次推送時它被重新編譯改寫時,應回 0。[test: t_room_mig_schema_rewrite_branch_only_passes]
- [S10] 當結構檔只改排版、`identityHash` 相同時,應回 0。[test: t_room_mig_schema_reformat_passes]
- [S11] 當主線分岔點上結構檔目錄最大值是 2、終點變成 1 時,應回 1 並說降版;2 只存在分支上、被退回成 1 時應回 0。[test: t_room_mig_downgrade_blocks]
- [S12] 當 `@Database(version = DB_VERSION)`、這次只改了常數檔並新增 `2.json`、沒寫 Migration 時,應回 1(版本從結構檔讀)。[test: t_room_mig_constant_version_uses_schema]
- [S13] 當路徑有缺口、但終點有 `migration(1, 2) { … }` 這種參數不是整數字面的寫法時,應回 0 並印「提醒:」說升級路徑寫法判不出。[test: t_room_mig_unresolvable_migration_warns]
- [S14] 當版本沒變、這次刪掉了 `Migration(1, 2)`,而主線分岔點時版本 1 能升到 2 時,應回 1。[test: t_room_mig_deleted_migration_blocks]
- [S15] 當主線分岔點上的 `1.json` 在終點被刪、別處也沒有同雜湊的檔時,應回 1;整個結構檔目錄跟著改套件名搬家(雜湊相同)時,應視為同一個資料庫照常判。[test: t_room_mig_schema_delete_and_move]
- [S16] 當結構檔目錄在主線分岔點上不存在(這條分支新增的資料庫)時,升級那半應不要求路徑與升級測試。[test: t_room_mig_new_database_no_requirement]
- [S17] 當改動的 `@Database` 寫了 `exportSchema = false` 時,應回 0 並印「提醒:」說這個資料庫判不了升級。[test: t_room_mig_export_schema_false_warns]
- [S18] 當 `@Database(...)` 後面接 `@TypeConverters(Converters::class)` 再接 `abstract class AppDatabase`、版本寫 2 而結構檔只有 1 時,訊息應點名 `AppDatabase`,不是 `Converters`。[test: t_room_mig_class_name_skips_annotations]
- [S19] 當資料庫與升級用 Java 寫(`@Database(entities = {User.class}, version = 2)`、`new Migration(1, 2)`)時,應跟 Kotlin 一樣判。[test: t_room_mig_java_syntax]
- [S20] 當 `Migration(1, 2)` 只出現在程式註解或字串裡時,應不算路徑;剝完程式註解與字串後的行數應跟原檔相同。[test: t_room_guard_strip_keeps_lines]
- [S21] 當類別完整名稱列在 `room_guard.allow_destructive` 時,升版而沒有路徑與測試應回 0。[test: t_room_mig_allow_destructive_listed]
- [S22] 當 DAO 新增 `@Query` 方法 `getUnpaid`、沒有任何測試以 `.getUnpaid(` 提到它時,應回 1,訊息點名 `OrderDao.getUnpaid`。[test: t_room_dao_new_method_without_test_blocks]
- [S23] 當提到 `.getUnpaid(` 的測試檔本身沒有 Room 建法(繼承基底類別)、但另一支測試檔有 `inMemoryDatabaseBuilder` 時,應回 0。[test: t_room_dao_test_via_base_class_passes]
- [S24] 當唯一提到 `.getUnpaid(` 的測試檔有 `mockk<OrderDao>` 時,應回 1,訊息說 mock 的測試不算。[test: t_room_dao_mock_only_test_blocks]
- [S25] 當終點所有測試檔都沒有 Room 建法時,改到 DAO 方法應回 1,訊息說沒有任何用真 Room 的測試。[test: t_room_dao_no_real_room_anywhere_blocks]
- [S26] 當既有 DAO 只刪掉 `getPaid` 那個 `@Query` 裡的一行時,應要求 `getPaid` 有測試,同檔其他沒改的方法不要求。[test: t_room_dao_changed_methods_incl_deletion]
- [S27] 當 `@Transaction` 方法只改了函式本體時,應算改到、要求測試。[test: t_room_dao_transaction_body_change_required]
- [S28] 當 DAO 檔只是搬到別的套件(`git mv` 加改 `package` 那行)時,應不要求任何方法補測試。[test: t_room_dao_rename_only_changed_lines]
- [S29] 當新增的 `@TypeConverter` 函式沒有測試提到時,應回 0 並印「提醒:」。[test: t_room_typeconverter_warns]
- [S30] 當 `room_guard.dao` 設成 `warn`、同一次推送同時缺 DAO 測試與升級路徑時,DAO 那條應只印「提醒:」,升級那條照樣讓它回 1。[test: t_room_dao_warn_separate_from_migration]
- [S31] 當範圍裡沒碰到任何結構檔與含 Room 字樣的非測試檔時,應回 0、不印任何東西、不寫治理帳。[test: t_room_guard_unrelated_diff_silent]
- [S32] 當有觸發而且全部通過時,治理帳應多一筆 room-guard 的 passed,帶判了幾個資料庫與幾個 DAO 方法。[test: t_room_guard_records_passed_when_triggered]
- [S33] 當設了 `LUMOS_SKIP_ROOM_GUARD=1` 而本來會擋時,應回 0,治理帳多一筆 skipped-env。[test: t_room_guard_skip_env_records]
- [S34] 當 `room_guard.gate` 設成 `warn` 時,本來會擋的情況應回 0、印「提醒:」並記 warned;設成 `off` 時應回 0 且不判;填了不認得的值時應照 block 判並印一行提醒。[test: t_room_guard_gate_modes]
- [S35] 當 `Migration(1, 2)` 只存在工作目錄、沒有提交時,應照樣回 1。[test: t_room_guard_reads_tip_not_worktree]
- [S36] 當帶 `--push-remote`/`--pushed-ref` 推一個 tag 時,起點應照 `_push_range_start` 算(不從空樹比);分支合過主線、主線那邊改了 DAO 方法時,那些方法應不要求這次補測試;起點算出來是空樹時,應回 0、印「這次不判」並記 skipped。[test: t_room_guard_range_start_tag_and_empty]
- [S37] 當升級測試放在 `src/androidTestDebug/`、DAO 測試放在 `src/testDebug/` 時,應認得是測試路徑;放在 `src/androidTestDebug/` 的 `Migration(1, 2)` 應不算路徑。[test: t_room_guard_test_path_variants]
- [S38] 當 `2.json` 內容有合併衝突標記時,應回 1,訊息說結構檔讀不懂。[test: t_room_mig_unreadable_schema_blocks]
- [S39] 當推送前掛鉤跑到這道而它回 1 時,應印逃生段、記一筆 room-guard 擋下、在全套測試之前跟其他閘一起擋;回 2 時應印「這次沒檢查」並放行;被訊號殺掉時應整支掛鉤停下,而且「中斷就停」清單有這一行。[test: t_prepush_room_guard_wired]
- [S40] 當讀 `_KNOWN_GATES`、`lumos --help`、INDEX.md 與 06-代碼審與推送.md 時,都應有 room-guard。[test: t_room_guard_registered]
- [S41] 當讀 test-quality-standard.md 時,應有 Android 資料層(Room)一節,依序提到查詢、資料限制、交易、升級、Flow、TypeConverter、createFromAsset 七種情況,並提到記憶體資料庫、`MigrationTestHelper`、`BundledSQLiteDriver`、官方不建議 Robolectric、mock DAO 證不了 SQL、故障挑選;03-寫回圖譜.md〈實作測試品質〉有一句指到那一節。[test: t_test_quality_standard_android_room_section]
- [S42] 當在實驗專案 macrobench-lab(本機 `/Users/enzo/orca/workspaces/macrobench-lab`,另開獨立工作樹做)加 Room 資料庫 v1(含 DAO 與真 Room 測試)、再升 v2 時,漏了 Migration、新 DAO 方法沒測試各自應被這道擋下,補齊後應放行,而且升級測試與 DAO 測試在裝置上實跑是綠的、故意改壞查詢或拿掉交易時會翻紅。[manual: 實驗專案的獨立工作樹裡實跑 room-guard 與裝置測試,收據記進 Verification]

## 回退(由後往前)

- 第 7 步:測試品質規範那一節與 03 的指向句還原提交,不影響任何程式。
- 第 6 步:掛鉤那段還原(要重新 anchor approve);要先停就在消費專案設 `room_guard.gate: off`(只停 DAO 那半設 `room_guard.dao: off`),不用改掛鉤。
- 第 1–5 步:子指令整支還原,`_KNOWN_GATES` 那一項一起拿掉;新版掛鉤配舊版 lumos 時子指令不存在會回 2,掛鉤印「這次沒檢查」放行。

## 實務隱患

- **誤擋(結構檔改寫)**:主線上已有、但其實還沒發布給使用者的版本又改了結構,會擋;訊息講可以單次跳過。
- **誤擋(DAO)**:只改了程式註解或排版也算改到方法;第一次接入的專案,碰到舊 DAO 的任一方法就要補那個方法的測試——這是刻意的(邊改邊補),`room_guard.dao: warn` 是過渡用的逃生。
- **一個專案多個資料庫**:`Migration(x, y)` 不帶類別資訊,A 資料庫的升級物件會被算進 B 的路徑;寫進誠實界線。
- **名稱撞名**:兩個 DAO 都有 `insert`,測試以 `.insert(` 呼叫另一個 DAO 也會被算到;不保證。
- **效能**:終點與分岔點各一次 `ls-tree` 列全部檔(`_nodehome_list`,大 repo 的主要成本)、算分岔點的 `merge-base` 一次、讀觸發到的檔與兩邊的結構檔、終點與分岔點各一次 `git grep` 篩出含 `Migration` 的非測試檔、終點一次 `git grep` 篩測試檔、一次帶改名偵測的差異;升級路徑用圖的走訪,版本號再大也不會逐一列舉。單次 git 逾時照第 4 步放行。
- **相容**:掛鉤配舊版 lumos(沒有這個子指令)回 2 要放行,不能擋所有人。
- **判不清時放行,跟 Android 端到端驗收的「判不清就擋」刻意不同**:那道判的是實機驗收紀錄,判不清代表驗收狀態不明;這道是靜態看程式碼形狀,跟筆記形狀擋、每支檔有家同類,git 算不出來時擋下等於工具壞了就擋所有人;判不清的情況各自印一句提醒並記 skipped,讓人看得到這次沒判。
- 已排除:金流:這道只讀提交裡的程式碼與結構檔,不碰任何付款流程
- 已排除:對外送出:不打網路、不呼叫任何外部服務,只跑本機 git
- 已排除:不可逆:這道只擋推送、不改任何檔或資料;計劃裡的「Migration」是被檢查對象的名字,不是這道會做的動作,還原提交就回到原狀
- **守衛面(不排除)**:這道本身就是新的推送前閘,所以照風險高走設計審;不改既有任何一道閘的判定,只在掛鉤裡多一段呼叫。

## 誠實界線

- 只證「程式碼裡有升級路徑、結構檔,以及有測試提到這個方法」,**不證測試跑過、跑綠,也不證測試真的驗了結果**;跑綠要靠專案的 CI 或 Android 端到端驗收,驗得對不對要靠測試品質規範與審查。
- 改了 Entity 卻沒重新編譯(結構檔沒更新)時看不出來——要編譯才知道結構變了,這道不跑 Gradle。
- `Migration(x, y)` 沒辦法對到哪個資料庫;多資料庫專案可能被別的資料庫的升級物件放行。
- Migration 物件寫了卻沒有 `addMigrations` 註冊,這道看不出來(執行時一樣閃退);靠升級測試裡跑完全部升級的那支抓。
- 跑完全部升級的測試只認「有這種寫法」,不證陣列裡真的放了新的那條。
- Kotlin 允許巢狀區塊程式註解,剝程式註解的掃描式不處理巢狀;巢狀程式註解裡的 `Migration(1, 2)` 可能被算成路徑。
- 資料庫沒匯出結構檔(`exportSchema = false`)時升級那半判不了,只提醒。
- 結構檔目錄形狀 `<類別完整名稱>/<版本>.json` 是 Room 2 的慣例(實驗專案用 Room 2.8.5 實測);Room 3 沒找到官方明文寫目錄形狀,接 Room 3 專案時要先實測一次。
- 資料限制(主鍵、唯一、外鍵)、Flow 重送、預載資料庫這三種情況沒有可靠的程式碼訊號對應到「該有哪支測試」,只寫在規範裡、守衛不判。

## 合約候選

- 升級路徑缺口在判得出的寫法下一定擋(`Migration`/`AutoMigration` 整數字面),判不出的寫法才降成提醒——改成「判不出也擋」會讓工廠函式寫法的專案永遠推不上去,改成「缺口也只提醒」等於拿掉這道的主要功能。候選,不等於已標。
- 結構檔改寫只擋主線分岔點上已有的版本。候選,不等於已標。

## 實作偏離紀錄

- 2026-10-28 實作:結構檔「讀不懂就擋」收窄成「看得出是 Room 結構檔(含 formatVersion 或 identityHash 字樣)卻讀不懂才擋」。原文照字面實作時,`res/raw/1.json` 這類同形狀但不是 Room 的資源檔壞掉也會擋推送;收窄後 [S38] 的合併衝突情境照擋。
- 2026-10-28 實作:有觸發而放行的 passed 照鄰居(存量漂移、每支檔有家)記在本機帳 `docs/.governance-local.jsonl`,不進版控帳——每次推送一筆沒資訊的行是帳本雜訊;RETIRE-IF 數 passed 時要連本機帳一起看。
- 2026-10-28 代碼審 r1:「這一版的結構檔沒提交」([S5])只判這次碰到的資料庫(它的原始碼、版本常數的定義檔或結構檔目錄有改);整個專案一個結構檔都沒有時改成只提醒怎麼設匯出位置。原文照字面實作時,沒設匯出位置的專案只要碰到 Room 就被擋,訊息教的「把 N.json 加進提交」做不到;主線上本來就有的缺口也會擋碰到別處的推送。[test: t_room_mig_never_exported_warns_not_blocks]
- 2026-10-28 代碼審 r1:`version =` 寫成常數時,[S5] 那一條到非測試原始碼找 `val/int 名稱 = 整數` 的定義,恰好一個值才用;改到定義它的檔也算碰到 Room。原文「常數版本號不用從原始碼猜」只講升級路徑那半(仍以結構檔為準),[S5] 照字面只認整數字面時,只改常數升版、忘了提交結構檔的推送整個不觸發。[test: t_room_mig_constant_bump_without_schema_blocks]
- 2026-10-28 代碼審 r1 到 r3:刪掉的行改對回舊檔——舊檔某個 DAO 方法被刪到一部分(不是整段刪掉)、終點還在,就算改到它;終點同名函式還在但 Room 註記全拿掉了也算([S26] 方法裡刪一行、刪最上面的註記行都要求測試;整段刪掉的方法不要求,同名多載刪掉一個不牽連留下的那個,鄰居沒被刪到也不要求)。原文「刪除點前後兩行」照字面實作時,整段刪掉一個方法會要求相鄰、沒改過的方法補測試;r1 改成「前後兩行都在同一個方法裡」又漏掉刪方法最上面那一行。[test: t_room_dao_whole_method_deletion_no_neighbor] [test: t_room_dao_partial_deletion_edges_required]

## 審計修正紀錄

- r1(2026-10-28,4 席:正確性、邊界、通才、架構對齊,全 sonnet;只有同一家模型審過):去重成 15 組根因、全折(折入後派鏡像核對,補齊 7 處折得不完整、6 處前後不一致、2 處程式宣稱不符),只放行 1 條(席位自述引用都對得上、沒有缺陷);blocking 20 條(正確性 8、邊界 8、通才 3、架構 1;架構那條原標 minor 又標 blocking 是,退回該席重判後改 major)。卷證 `governance/review-reports/room資料庫測試守衛/`。結論:原稿以「改動的 `@Database` 檔」為入口太窄、範圍照錯了變數、DAO 測試認定太死;改成以結構檔為準、起點交給 `_push_range_start`、DAO 測試改成「呼叫到且沒 mock、全庫有真 Room」。
- r1 新增機制的最小解檢查:`passed` 帳(不加就分不出「沒人用 Room」與「用了都過」,RETIRE-IF 量不出來);`--push-remote/--pushed-ref`(不加就只能用掛鉤的空樹退路,推 tag 會把整個 repo 當新改動);其他折法都是改判斷規則或重用既有工具,沒有新設定鍵。
