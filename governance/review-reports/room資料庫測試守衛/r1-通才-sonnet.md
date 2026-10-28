severity: major

**逐節結果**
- 緣起、調研:已讀。官方測試頁與升級頁我都查過,見 F5 的說明。
- 做法 1、2、3、4、5:有 finding,見 F1、F2、F4、F6、F7、F8。
- 做法 6:有 finding,見 F9。
- 做法 7:有 finding,見 F5、F10。
- 驗收條款:有 finding,見 F10、F11。
- 回退:已讀,無 finding。
- RETIRE-IF 與 REVISIT:有 finding,見 F3。
- 實務隱患、誠實界線:有 finding,見 F6、F7、F12。
- 文件內部交叉引用:`Systems/room-guard` 本來就是新節點,不算錯。`Systems/test-quality-cli` 存在。
- `[[Projects/Android端到端驗收_計劃]]` 和 `[[Systems/bound-tests-gate]]` 我沒逐一核對。
- 「中斷就停」清單那條連結,見 F9。

**固定席節點**
- `Systems/bound-tests-gate` 判不影響。這份設計不碰 `bound-tests` 的判定,只在掛鉤多一段呼叫。
- 唯一的接點是新增條款 S1 到 S28 的 `[test:]` 綁定。這些綁定要求方法名存在於測試索引,而這些測試現在都還沒寫。

---

severity: major
blocking: 是(接 Android 專案的常見寫法會誤擋,而且開發者看不出為什麼)
F1. 做法 2,找資料庫類別名稱的規則會抓錯
- spec 位置:做法 2「找資料庫類別」。
- 引句:「完整名稱 = 檔頭 `package` + 類別名」
- 問題:類別名取「註解後第一個 `class 名稱`」。Android 專案慣例是在 `@Database(...)` 後面緊接 `@TypeConverters(Converters::class)`(Java 寫成 `Converters.class`),再接 `abstract class AppDatabase`。
- 失敗情境:第一個出現的 `class` 其實是 `Converters::class`。算出的完整名稱變成 `pkg.Converters`,於是找不到 `schemas/pkg.Converters/2.json`。
- 結果:每次升版都被判「結構檔缺」,開發者看到的檔名還是錯的。
- 其他同類失敗:
  - 巢狀類別的完整名稱不是 `package + 類別名`,Room 的結構檔目錄名會不同。
  - `entities = [User::class]` 若沒有先平衡括號吃掉整個註解,也會命中。
- spec 沒寫要排除 `::class` / `.class`,也沒寫巢狀類別怎麼處理。S17 的 Java 例子的註解參數也有 `User.class`,卻沒有「註解後再接別的註解」的案例。
- 查證:官方升級頁範例是 `@Database(...)` 後直接接 `abstract class`,所以沒有抓到這種常見組合。

severity: major
blocking: 是(預設 block,常見的測試結構會被擋)
F2. 做法 3,DAO 測試要在同一個檔裡同時滿足三件事
- 引句:「含真的 Room 建法(`inMemoryDatabaseBuilder` 或 `databaseBuilder`)、提到這個 DAO」
- 問題:真 Room 建法、DAO 名稱、方法名三樣必須在同一支測試檔。常見的合法寫法都做不到:
  - 抽象基底類別 `BaseDbTest` 在 `@Before` 裡建 in-memory DB,各 DAO 測試繼承它。
  - Hilt 的測試 module 提供資料庫。
  - DAO 存取器改名,例如 `db.orders()`,而 DAO 類別叫 `OrderDao`,變數叫 `dao`。此時檔裡沒有 `OrderDao`,也沒有 `orderDao`。
- 失敗情境:測試真實存在、真用 Room,卻被擋。
- 開發者只剩三條路:
  - 在檔裡硬塞名字(等於教人湊字串)。
  - 把 `room_guard.dao` 設成 warn(等於關掉 DAO 這半)。
  - 單次跳過(整道一起跳過,連升級那半也不判)。
- spec 的「名稱撞名」那段只講誤放,沒有講這種誤擋。S20 與 S21 只測了單檔情況。

severity: major
blocking: 是(撤除條件寫了但量不出來,等於沒有條件)
F3. RETIRE-IF 與 REVISIT 的數字沒有資料來源
- 引句:「一半以上被單次跳過或事後判成誤擋」
- 問題一,「事後判成誤擋」:全 spec 沒有任何機制記這件事,沒有 ledger 欄位,也沒有 `--mark-false-block` 一類的指令。REVISIT 要「數誤擋比例」,但分母分子都沒有來源。
- 問題二,「連續半年零觸發而且沒有任何專案在用 Room」:S12 規定無關改動「不寫治理帳」,放行也不記。所以「零觸發」分不出是沒人用 Room,還是用了但都通過。「用 Room 的專案數」不可量。
- 問題三,DAO 那半的撤除條件寫「審查卷證裡被點出」:這要看消費專案有沒有跑代碼審,spec 沒有掛勾。
- 問題四,「Room 官方出了…機制」不是可偵測事件,沒有 `when-*` 式條件。
- 查證:file: `scripts/lumos:1910`,`_gate_event_or_warn` 只記 blocked、warned、skipped-env 等事件,沒有判成誤擋的類別。

severity: minor
blocking: 否(有逃生口,只是邊緣情況)
F4. 做法 1,測試路徑判定漏掉 Gradle 的變體測試目錄
- 引句:「而 `<名稱>` 是 `test` 或以 `Test` 結尾」
- 問題:Gradle 的 variant 測試目錄是 `src/testDebug/`、`src/testFree/`、`src/androidTestDebug/`。名稱以 `Debug`、`Free` 結尾,不符合規則,會被當成非測試路徑。
- 失敗情境:
  - 放在 `testDebug` 的 `MigrationTestHelper` 測試不算。
  - 放在 `androidTestDebug` 的 Migration 物件反而被當成正式碼路徑,算進升級邊。

severity: minor
blocking: 否
F5. 做法 7、調研,規範內容與官方現行頁面有差
- 我查了 developer.android.com 的測試頁和升級頁。
- 一致的部分:
  - 測試頁明寫「We don't recommend Android local unit tests with Robolectric. Use local JVM tests using Room KMP instead.」
  - 也建議記憶體資料庫與 `BundledSQLiteDriver`。
- 有差的部分:
  - 現行升級頁用的是 Room 3(`androidx.room3`、`room3-testing`、`MigrationTestHelper(instrumentation, databaseClass, driver, file)`、`runMigrationsAndValidate(2, listOf(...))`、`Migration.migrate(connection)`)。spec 的調研和做法 7 全用 Room 2 名詞。
  - 「Robolectric 時結構檔進 debug assets」不是官方說法。官方只說在不用 Room Gradle plugin 時,把結構檔位置加進測試 app 的 assets。spec 的調研段有標社群,但做法 7 要寫進規範時沒保留這個區別。
  - 官方只在 `exportSchema=false` 時明說自動升級會失敗,沒說手寫升級可以不匯出。
- ⚠ Room 3 的結構檔目錄形狀(`<fqcn>/<版本>.json`)我沒查到官方明文。spec 的結構檔偵測只靠這個形狀。
- 另一個實作上的矛盾:純 Android 專案的 `src/test` 要用真 Room,在官方不建議 Robolectric 之後就剩 KMP 一條路。守衛卻只看字串,所以只在裝置端才跑得了的測試也算通過,而推送前永遠不會執行它。

severity: minor
blocking: 否
F6. 緣起提到的最危險情況守衛沒有判
- 引句:「開了 `fallbackToDestructiveMigration()` 則是靜默清空資料」
- 問題:builder 帶 `fallbackToDestructiveMigration` 時,缺升級路徑不會閃退而是清空資料。但守衛不偵測這個呼叫,誠實界線也沒列這項。
- 與 `allow_destructive` 的關係:專案要放行純快取資料庫,得另外在 config 列類別名,和程式碼裡的 builder 呼叫是兩份各自維護的事實。
- 另外 `exportSchema = false` 的專案,每次升版都因缺結構檔被擋。spec 只提「沒匯出結構檔」的訊息,沒設計「不匯出」的出路。唯一的出路是 `allow_destructive`,但它同時豁免路徑和測試,語意過寬。

severity: minor
blocking: 否
F7. 做法 2,升級邊的辨識有漏洞
- 引句:「終點非測試路徑的 `Migration(x, y)` 與這個類別註解裡的 `AutoMigration(from = x, to = y)` 當成邊」
- 問題一:Migration 物件寫了但沒有 `addMigrations` 也算有路徑,會誤放。
- 問題二:Kotlin 允許位置參數 `AutoMigration(1, 2)`。也可能寫 `to = 2, from = 1`,或 `Migration(startVersion = 1, endVersion = 2)`。S3 與 S4 只測了 `from=…, to=…` 這一種寫法。
- 問題三:資料庫類別搬檔、改名後,在起點找不到同一檔,被當成新資料庫而不判。這會讓升版的要求靜默消失。

severity: minor
blocking: 否
F8. 做法 6,接進掛鉤與工具鏈時還有 spec 沒寫的登記處
- 引句:「掛鉤「中斷就停」清單加一行、假 lumos 認得 `room-guard`」
- 問題:新增閘名要登進治理帳允許清單。
  - file: `scripts/lumos:16040` 附近有閘名清單,例如 `"note-shape"`。
  - file: `scripts/lumos:68085` 有子指令說明表。
  - 還有 argparse 註冊(`ns_p = sub.add_parser("note-shape"…` 在 `scripts/lumos:69240`)和入口分派(`scripts/lumos:69619`)。
  - 這些位置 spec 都沒寫,實作者會靠測試翻紅才發現。
- 掛鉤清單註解的字樣「9 道閘裡的 8 支」要跟著更新。
- file: `scripts/hooks/pre-push:365` 有 `anchor verify`。改掛鉤與 `scripts/test_lumos.py` 屬裁判檔,要 anchor approve。S26 與回退段都沒提這一步,實作者的第一次推送會被擋。
- 擋下時給開發者的逃生說明段(像 `home`、`note-shape` 那兩段 echo)spec 沒要求,也沒有條款綁。
- 實測的對照:file: `scripts/hooks/pre-push:501` 之後的 `home check` 與 `note-shape` 兩處,各有一段印逃生說明的 echo。

severity: minor
blocking: 否
F9. 做法 1,範圍與起點的寫法前後不一
- 引句:「起點照筆記形狀擋用的 `_lens_push_base` 算;掛鉤傳的是 `_brange`」
- 問題:file: `scripts/lumos:60954` 的 `_lens_push_base` 的註解寫明,它在「合過主線、沒設 upstream」等情況會算錯,掛鉤與 CI 的存量漂移檢查特意改走 `_push_range_start`。
- spec 的 `lumos room-guard --diff` 沒說直接用手動 `--diff` 起點時是否會踩到同一個問題,也沒寫合過主線的測試條款。
- 掛鉤這邊用 `_brange` 是對的。問題是子指令手動執行與掛鉤執行的行為可能不同,spec 沒覆蓋。

severity: minor
blocking: 否
F10. S27 的測試只能是關鍵字清單
- 引句:「依序提到查詢、資料限制、交易、升級、Flow、TypeConverter、createFromAsset 七種情況」
- 問題:這條能寫成會翻紅的測試,但只驗字串存在。規範寫成關鍵字堆也會過。
- 做法 7 還要求寫「故障挑選方向」與「mock DAO 只證 Repository 自己的邏輯」,這兩樣 S27 完全沒綁。
- 這符合 spec 自己承認的限制(內容品質靠審查)。但驗收條款少列了兩項,審查者無法用條款核對。

severity: minor
blocking: 否
F11. 升級測試與 DAO 測試的「提到」判準太弱
- 引句:「而且它這次改過,或某行 `runMigrationsAndValidate(` 帶著 b」
- 問題一:只要動過那支測試檔的任何一行(例如改一個 import),就算升級測試通過。
- 問題二:方法名是「單字」比對。`insert`、`delete`、`getAll` 這類通用名,幾乎任何測試檔都會出現。
- spec 在誠實界線與 RETIRE-IF 提到這個限制,但驗收條款沒有任何一條針對「只改 import」或「只在註解外提到通用名」的情況,所以弱點沒有反例測試。

severity: minor
blocking: 否
F12. 誤擋說明與驗收條款沒對上
- 引句:「同一個版本還沒發布給使用者(只在開發分支上),又改了一次結構,結構檔雜湊那條會擋」
- 問題:這個情況的訊息要求寫在實務隱患段,驗收條款 S7 只驗「訊息說結構改了沒升版」,沒有驗它有講單次跳過。
- 其他「擋下時開發者看不懂要做什麼」的風險:S19 到 S25 的訊息只指定要點名方法或 DAO,沒有指定要講怎麼補(例如該寫哪種測試)。

最嚴重 severity: major;blocking 共 3 條(F1、F2、F3)。
