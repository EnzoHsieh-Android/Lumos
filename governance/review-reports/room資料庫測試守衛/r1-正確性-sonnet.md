severity: major

審查範圍:逐節讀完 spec 全文,並對照 `scripts/lumos` 與 `scripts/hooks/pre-push`。交叉引用 `Projects/Android端到端驗收_計劃`、`Systems/bound-tests-gate`、macrobench-lab 都存在。`Systems/room-guard` 是預定新開的節點,不算錯字。

### Finding 1(做法 6,掛鉤接線用的範圍)
severity: major
blocking: 是。推 tag 就整個 repo 當新增,預設擋下,屬誤擋。
- 問題:spec 指定用 `_brange`,但 `_brange` 在非分支 ref 與「遠端舊值本機找不到」時是空樹範圍。
- 引句:「用會擋的範圍 `_brange`」
- 失敗情境:
  1. Room 專案推 release tag(`git push origin v1.2.0`)。
  2. `pp_block_range_for` 只替 `refs/heads/*` 的新分支換成真起點,tag 的 `_brange` 是 `EMPTY_TREE..tip`。
  3. `_lens_push_base` 遇到空樹原樣回傳,所以所有 `@Dao` 檔都是「檔是新的」,每個方法都要有測試。
  4. 只要有一個沒測試的舊 DAO 方法,推 tag 就被擋。
  5. 舊 `@Database` 在起點不存在,升級那半反而全部判成「新資料庫」而漏放。
- 另一個場景:分支合過主線後再推,`old..tip` 會帶進別人在主線改的 DAO 方法,由推的人背測試債。
- 查證:
  - file: `scripts/hooks/pre-push:54`。`pp_block_range_for` 只在 `$3 == refs/heads/*` 且舊值全零時才換起點,其餘走 `pp_range_for`。
  - file: `scripts/hooks/pre-push:483`。註解明寫筆記形狀擋與每支檔有家「刻意不同」,用 `_hrange`,因為空樹會把整段歷史當新改動而誤擋。
  - 筆記形狀擋的 `_hrange` 遇到 tag(舊值全零)時,若 tag 指向的提交已在遠端就是空字串,整段略過。
  - spec 自己說「照筆記形狀擋的形狀」,卻選了筆記形狀擋刻意避開的那個範圍。
  - 沒有任何驗收條款覆蓋 tag 推送或 `_brange` 空樹退回。

### Finding 2(做法 3,DAO 測試認定)
severity: major
blocking: 是。常見的 Hilt 或共用基底類別寫法會被誤擋。
- 問題:「真的 Room 建法」必須跟 DAO 名、方法名出現在同一支檔。
- 引句:「每個改到的方法要有一支測試路徑裡的檔,**同時**含真的 Room 建法」
- 失敗情境:
  1. 專案用 Hilt `@TestInstallIn` 模組、Koin 測試模組、共用 `abstract class DatabaseTest`,或 `@get:Rule val dbRule = DatabaseRule()`,把 `Room.inMemoryDatabaseBuilder` 放在別的檔。
  2. `OrderDaoTest.kt` 只有 `db.orderDao().getUnpaid()`,檔裡沒有 `inMemoryDatabaseBuilder`,判成「只用 mock」,被擋。
  3. 補測試也補不過,除非把建法複製進每支測試檔。
- 同族的另一條失敗路徑:DAO 存取子不叫 `orderDao`。
  - 例:`abstract fun orders(): OrderDao`,測試寫 `db.orders().getUnpaid()`,檔裡沒有 `OrderDao`、也沒有 `orderDao`。
  - 例:DAO 類別叫 `OrderDAO`,首字小寫變成 `orderDAO`,對不上慣用的 `orderDao()`。
- 反方向漏放:`mockkStatic(Room::class); every { Room.databaseBuilder(...) }` 會被當成真 Room。
- 這個誤擋的逃生口只有 `room_guard.dao: warn`,spec 沒提供「建法在別檔」的認定路徑。

### Finding 3(做法 2,升級測試認定)
severity: major
blocking: 是。官方建議的「跑完全部升級」寫法會被誤擋。
- 問題:升級測試必須是這次改過的檔,或某行 `runMigrationsAndValidate(` 直接帶著 b。
- 引句:「測試路徑裡有同時提到 `MigrationTestHelper` 與這個類別名的檔,而且它這次改過」
- 失敗情境:
  1. 專案已有官方建議的全升級測試,例如 `helper.createDatabase(DB,1)`,再 `Room.databaseBuilder(...).addMigrations(*ALL_MIGRATIONS).build()`。
  2. 這次只在主程式的 `ALL_MIGRATIONS` 陣列加 `MIGRATION_2_3`,測試檔不用動。
  3. 沒有 `runMigrationsAndValidate(` 行帶字面值 3,測試檔也沒改,判成缺升級測試,被擋。
  4. 唯一的解法是為了過閘去碰測試檔。
- 另一個漏放方向:只要隨便改該檔一行(排版、註解)就算「改過」,跟 spec 想驗的「升級測試有沒有跟著動」無關。
- 判斷模糊:`runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)` 的 `MIGRATION_1_2` 裡的 2,算不算「帶著 b」,spec 沒定義字界。

### Finding 4(做法 2 的結構檔要求與 S4 互相矛盾)
severity: major
blocking: 是。S4 允許的合法路徑實際上會被誤擋。
- 引句:「a+1 到 b 每一版都有」
- 引句:「當版本從 1 改成 3、終點只有 `Migration(1, 3)` 時,應算有路徑」
- 失敗情境:
  1. 開發者在同一分支直接把版本從 1 跳到 3,中間的 2 從沒編譯過,寫了 `Migration(1, 3)`。
  2. Room 每個版本只在編譯那個版本時才匯出 json,所以沒有 `2.json`。
  3. 升級路徑算有,但結構檔要求 `2.json`,被擋。
  4. S4 只驗路徑那條,沒說這種情況的結構檔結論。
  5. 擋下的訊息會要人補一個 Room 根本不會產生的檔。

### Finding 5(做法 2,版本解析)
severity: major
blocking: 是。版本升了卻完全沒檢查,屬漏放。
- 問題:只在「改動過的 `@Database` 檔」判版本,常數寫法只提醒。
- 引句:「找資料庫類別:改動過的 `.kt`/`.java` 檔含」
- 失敗情境:
  1. 專案把 `const val DB_VERSION = 3` 放在 `Constants.kt` 或 `companion object`,`@Database(version = DB_VERSION)`。
  2. 版本改成 3、沒寫 Migration,只改 `Constants.kt`。
  3. 範圍裡沒有 `@Database` 檔,走 S12 的「靜默回 0」。
  4. 就算 `@Database` 檔有改,S10 也只提醒。
- 這是 Room 專案裡很常見的寫法,而且守衛已有訊號可用:新增的 `<完整名稱>/N.json`(新結構檔)。
- spec 把常數版本列為「提醒」,等於最常見的寫法放行。

### Finding 6(做法 3,「改到的方法」判法)
severity: major
blocking: 是。查詢語意被改了卻沒要求測試,漏放。
- 引句:「終點上那個方法的範圍跟這次改動的行有交集就算」
- 失敗情境 A,純刪除:
  1. 開發者刪掉 `@Query("""...""")` 裡的一行 `AND deleted = 0`,或刪掉 `@Transaction` 方法本體的一行。
  2. 這個改動沒有終點側新增行號,與方法範圍沒有交集,判成沒改到。
  3. 這正是「查詢條件寫錯」那一類風險。
- 失敗情境 B,範圍切法:
  - 引句:「每個方法的範圍從它第一個註解行到下一個方法的第一個註解行之前」
  - 範圍只在「帶指定註解」的方法間切。中間的非註解輔助函式(例如 abstract class DAO 裡的 `open fun` 或 `fun` 預設實作)、`companion object`、檔尾其他類別,都被併進前一個註解方法。
  - 改這些行,會要求無關方法補測試。
  - 最後一個方法的範圍一路延伸到檔尾。
  - 方法上另有 `@RewriteQueriesToDropUnusedColumns`、`@SkipQueryVerification` 時,範圍起點是第一個「指定註解」還是任何註解,spec 沒定義。
  - `@Transaction` 加 `@Query` 疊在同一函式上,算幾個方法也沒定義。
- 查證:spec 的 S22、S23 只驗新增、修改行,沒有純刪除案例。

### Finding 7(做法 2,升級物件認定)
severity: major
blocking: 是。下列寫法會誤擋,另有一種漏放。
- 引句:「終點非測試路徑的 `Migration(x, y)` 與這個類別註解裡的」
- 誤擋輸入,升級路徑靠字面 `Migration(整數, 整數)` 抓:
  - 具名參數:`Migration(startVersion = 1, endVersion = 2)`。
  - 常數:`Migration(V1, V2)`。
  - 工廠函式:`fun migration(from: Int, to: Int, block: ...) = object : Migration(from, to)`,呼叫端寫 `migration(1, 2) { ... }`。
  - 基底類別:`abstract class BaseMigration(s: Int, e: Int) : Migration(s, e)`,再寫 `object : BaseMigration(1, 2)`。
  - 以上全部抓不到邊,版本升了就被擋。
  - `AutoMigration(to = 2, from = 1)` 倒序也同理。
- 漏放輸入:
  - 只存在 `Migration(1, 2)` 物件,但 `Room.databaseBuilder(...)` 沒有 `addMigrations(...)`。
  - 執行時仍丟 `IllegalStateException`,守衛卻因為找到物件而放行。
  - spec 的核心動機正是這個閃退。

### Finding 8(做法 2,結構檔比對:未發布版本的第二次推送)
severity: major
blocking: 是。常見的審查後再推流程會被擋。
- 引句:「起點就有、兩邊 `identityHash` 不同 → 擋(多半是結構改了忘記升版號)」
- 失敗情境:
  1. 分支升版到 2,首推時 `2.json` 已提交。
  2. 審查後改 Entity,Room 重新編譯覆寫同一個 `2.json`,這個版本尚未發布。
  3. 第二次推送,起點是遠端舊值,`2.json` 起點就有且雜湊不同,被擋。
  4. 每次迭代推送都被擋,只能 `LUMOS_SKIP_ROOM_GUARD=1`。
- 守衛沒有任何訊號分辨「版本已發布」與「還在開發」。
- spec「實務隱患」已承認這點,但只用擋下訊息提示跳過,不是修法。
- 預設就擋、常態工作流觸發,與 RETIRE-IF 要等半年才檢討的節奏不搭。

### Finding 9(做法 1,測試路徑認定)
severity: minor
blocking: 否。多數專案不受影響,且有 `warn` 逃生口。
- 引句:「路徑裡有一段 `src/<名稱>/`,而 `<名稱>` 是 `test` 或以 `Test` 結尾」
- 漏掉的目錄:AGP 的變體測試 `src/testDebug/`、`src/testRelease/`、`src/testFlavorDebug/`、`src/androidTestDebug/`。
- 失敗情境:DAO 測試放在這些目錄,不算測試路徑,被擋。
- 同一個測試路徑規則也會把 `src/testFixtures/` 判成非測試。

### Finding 10(做法 2,類別完整名稱)
severity: minor
blocking: 否。巢狀 `@Database` 類別少見。
- 引句:「完整名稱 = 檔頭 `package` + 類別名」
- 失敗情境:`@Database` 類別巢狀在別的類別裡。
- Room 的結構檔目錄用 `qualifiedName`,即 `pkg.Outer.Inner`,spec 算出 `pkg.Inner`,找不到 `<…>/pkg.Inner/2.json`,誤報「沒匯出結構檔」。

### Finding 11(做法 1,剝註解與字串字面值)
severity: minor
blocking: 否。需要特殊字串內容才觸發。⚠ 未實測,僅依 spec 文字推斷。
- 引句:「判斷前先剝掉註解(註解裡的 `Migration(1, 2)` 不算)」
- spec 沒提字串字面值。
- 失敗情境:
  - `@Query("... LIKE '/*'")` 或含 `//` 的 URL 字串,剝註解會誤吃後面的內容,把同一行或後續的 `Migration(...)` 吃掉。
  - Kotlin 支援巢狀 `/* /* */ */`,非貪婪剝法會留下殘餘字串。

### Finding 12(做法 3,新增檔與搬移)
severity: minor
blocking: 否。
- 引句:「檔是新的就全部算」
- 失敗情境:
  1. 把 `OrderDao.kt` 搬到別的 package(`git mv`),或換目錄。
  2. 不開重命名偵測時整檔是新增,所有方法都要補測試。
  3. 同樣搬移 `@Database` 檔:起點的類別完整名稱不同,「起點有、終點也有」不成立,升級那半靜默略過。
  4. spec 沒講重命名怎麼算。
- DAO 偵測也沒排除測試路徑:測試目錄裡假的 `@Dao` 被改,也要求測試。

### Finding 13(做法 3,型別轉換)
severity: minor
blocking: 否。
- 引句:「帶 `@TypeConverter` 的函式,這次改到的要有一支測試路徑裡的檔以單字提到函式名」
- 失敗情境(誤擋):型別轉換透過 DAO 做往返測試(官方建議的做法之一),檔裡沒出現 `fromInstant`,被擋。
- 失敗情境(漏放):函式名是 `toString`、`fromString`、`toList` 這類通用名,任何測試檔都有同一個字,形同無條件放行。

### Finding 14(做法 5,治理帳)
severity: minor
blocking: 否。實作時測試會立刻紅,是遺漏而非設計錯。
- 引句:「擋下與提醒才記帳,沒事的放行不記」
- spec 沒提要把 `room-guard` 加進 `_KNOWN_GATES`。
- 查證:
  - file: `scripts/lumos:1825`。`_gate_event` 對不在 `_KNOWN_GATES` 的閘名不寫、印警告並回 False。
  - file: `scripts/lumos:16040` 附近有閘名清單與說明文字。
  - 不補的話 S13、S14 要求的 skipped-env、warned 帳寫不進去。
  - 還得更新 gov 統計用的清單,RETIRE-IF 與 REVISIT 要數的治理帳筆數才有來源。

### 已讀,無 finding 的節
- 緣起、調研、現況(`Room 官方文件`的事實與掛鉤現況描述一致)。
- 做法 4:`allow_destructive` 的讀法與 `fallbackToDestructiveMigration` 的關係。
- 做法 7(規範補一節)。
- 回退。
- 誠實界線。

### 固定席節點:`Systems/bound-tests-gate`
判不影響。
- 它的合約是 `code-loop check` 對 impact 固定席上合約綁的測試逐支跑,紅、懸空、偽證據就擋。
- room-guard 是獨立子指令,只在掛鉤多一段呼叫,不改 `code-loop check` 的判定與 `bound-tests` 的呼叫。
- 只要第 6 步照 spec 說的「只在掛鉤裡多一段呼叫」做,就不碰到它的 `rc` 語意。

### 實務隱患鏡頭
- 誤擋與漏放:見 Finding 1–13。
- 金流、對外送出、不可逆:同意 spec 排除。只讀 git 物件,不打網路,不改檔。
- 效能:`git grep` 一次列測試檔、只讀改動檔,沒有放大隱患。
  - 但 Finding 1 的空樹範圍會把整個 repo 當新檔掃,在大 repo 上這一點也會變慢。
- 併發:同機並行會談寫同一本治理帳,沿用既有 `_gate_event` 的寫法,無新增風險。

總結:最嚴重 severity 是 major;blocking 共 8 條(Finding 1–8)。
