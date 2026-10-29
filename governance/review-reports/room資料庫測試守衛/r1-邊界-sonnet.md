severity: major

我讀完整份 spec,並對照 `scripts/hooks/pre-push` 與 `scripts/lumos` 查證。下面共 16 條 finding,其中 blocking 是 9 條。

**固定席節點 `Systems/bound-tests-gate`:不影響。** spec 只新增獨立子指令 `room-guard` 並在掛鉤多一段呼叫。`code-loop check` 對 impact 固定席合約綁定測試的判定路徑,spec 沒有碰。新增的 `t_room_*` 沒有綁到該 INVARIANT。

### F1
severity: major
blocking: 是(會擋人且預設就擋,屬 major)
- 段落:做法 1 與 6。
- 引句:「起點照筆記形狀擋用的 `_lens_push_base` 算;掛鉤傳的是 `_brange`」
- 問題:spec 把「筆記形狀擋的起點」和 `_brange` 當成同一件事,實際上是兩套。
- 查證:file: `scripts/hooks/pre-push:512` 的筆記形狀擋用的是 `_hrange`。這個變數在舊值本機找不到時取最早未上遠端提交的上一個,不用空樹。同檔 `483` 的註解寫明「這道會擋,把整段歷史當新改動就是誤擋。別把兩套合併成一套」。
- 查證:`_brange` 來自 `pp_block_range_for`,它的退路是空樹。`pp_range_for`(`pre-push:41`)在舊值全零或本機沒有該物件時回 `EMPTY_TREE..tip`。`push-range` 失敗或舊版 lumos 也走這條路。
- 失敗情境:force-push 之後舊遠端值本機沒有,`_brange` 變成 `空樹..tip`。
  - 所有 `@Database` 都是「起點沒有」,升級那半全部略過。
  - 所有含 `@Dao` 的檔都算「檔是新的」,每個方法都要有真 Room 測試。
  - 一個既有的 Room 專案會被整包 DAO 擋下,逃生只剩單次跳過。
- 另一處不一致:spec 說的「起點照 `_lens_push_base`」其實不會發生。掛鉤從不傳全零,`_lens_push_base` 的「頂端已在主線,沒有新東西」回 None 也沒被 spec 定義成 rc 與帳。

### F2
severity: major
blocking: 是
- 段落:做法 2。
- 引句:「結構檔(a+1 到 b 每一版都有」
- 問題:Room 只在編譯到某版時才寫該版的 json。
- 失敗情境:開發者把版本從 1 直接改成 3,手寫 `Migration(1, 3)`,實際只編出 `3.json`,中間的 `2.json` 從未存在。spec 字面會回 1 並點名缺 2.json,正確的推送被擋。
- 補充:S4 的測試意圖(只有 `Migration(1, 3)` 算有路徑)也沒覆蓋這個組合。

### F3
severity: major
blocking: 是
- 段落:做法 2。
- 引句:「改動過的 `.kt`/`.java` 檔含 `@Database(`」
- 問題:升級那半只在「`@Database` 檔本身被改」時啟動。
- 失敗情境(三種輸入都不動 `@Database` 檔,都走到「與升級無關的 diff」那條,靜默 rc0,S12 還明寫不印任何東西):
  - 版本不變,只刪掉 `Migration(1, 2)` 的檔。
  - 版本不變,只刪掉 `1.json`。
  - 版本不變,把 `Migration(2, 3)` 的 `to` 改成別的值。
- 結果:已發布使用者的升級路徑被破壞,守衛看不見。

### F4
severity: major
blocking: 是
- 段落:做法 2 與 3。
- 引句:「只在「起點有、終點也有、版本號變了」時判」
- 問題:起點與終點怎麼對應沒有定義(用路徑、完整名稱還是類別名),改名搬家直接成為繞法。
- 失敗情境:
  - `AppDatabase.kt` 搬到別的目錄或改包名並同時升版。路徑與完整名稱都對不上,被當成「新檔」,升級那半全免。schema 目錄名跟著完整名稱變,舊 json 也成「新檔」。
  - 反方向:`OrderDao.kt` 純改名或搬家。「檔是新的就全部算」讓所有方法都要補測試。
- 查證:同檔 `_nodehome_changed_vs_disk` 用 `--no-renames`,工具鏈現行慣例也不偵測 rename。spec 沒說這道要不要偵測。

### F5
severity: major
blocking: 是
- 段落:調研與做法 2(結構檔)。
- 引句:「版本號沒變但結構改了,重新編譯會覆寫同一個版本的檔」
- 問題:調研承認 Room 結構檔靠編譯產生,但 spec 沒處理 `exportSchema = false`。
- 失敗情境:`@Database(version = 2, exportSchema = false)` 的專案,每次升版都因「沒匯出結構檔」被擋。唯一出口是 `allow_destructive`,但它連路徑要求一起免掉,等於要求專案假裝自己可以清空。
- 另一種情境:`exportSchema = false` 的專案也沒有 `MigrationTestHelper` 可用,「升級測試」條件同樣永遠不滿足。

### F6
severity: major
blocking: 是
- 段落:做法 1「判斷前先剝掉註解」與 3 的方法範圍。
- 問題:剝註解的規則不完整,而且沒說行號會不會保留。
- 失敗情境(三種輸入):
  - Kotlin 的 `/* */` 可以巢狀,Java 不行。`/* 舊 /* 內 */ Migration(1, 2) */` 用不巢狀的剝法會留下 `Migration(1, 2) */`,算成有路徑。這正是 S16 想擋的。
  - 字串裡出現 `"http://..."` 或 SQL 的 `'/*'`,剝註解會吃掉同行或後續真實程式碼。
  - 字串裡的 `"Migration(1, 2)"` 沒被剝,算成路徑。
- 行號:DAO 那半用「改動的行號」與終點方法範圍相交。剝註解若刪行,範圍和 `git diff` 的行號對不上;spec 沒要求「換成空白、保留換行」。

### F7
severity: major
blocking: 是
- 段落:做法 3,方法範圍與「這次改到的方法」。
- 引句:「每個方法的範圍從它第一個註解行到下一個方法的第一個註解行之前。」
- 問題:這個範圍定義和改動行判定在三種輸入下不成立。
- 失敗情境:
  - 純刪除:多行 `@Query` 刪掉一行 `AND paid = 1`。終點上沒有對應的新行,hunk 是 `+n,0`,與方法範圍交集為空,判成沒改到。S22、S23 的情境同樣是只刪不加,結果相反。
  - 最後一個方法的範圍延伸到檔尾,改 `}` 或檔尾的 helper 都算它被改。
  - 方法 B 上方的 KDoc 在 A 的範圍內,改 B 的文件會要求 A 的測試。
  - 沒帶清單裡七種註解的方法(例如 abstract class 裡的 `open fun` 預設實作)不在判定範圍。
- 另外「第一個註解行」遇到多註解疊在一起(`@Transaction` 加 `@Query`)也沒定義。

### F8
severity: major
blocking: 是
- 段落:做法 3,DAO 測試判定。
- 引句:「同時含真的 Room 建法(`inMemoryDatabaseBuilder` 或 `databaseBuilder`)、提到這個 DAO」
- 問題:三項必須在同一支檔裡。
- 失敗情境:資料庫建在 JUnit Rule、共用 base class 或 Hilt `@TestInstallIn` 模組(另一支檔),測試檔只拿注入的 `dao.getUnpaid()`。變數叫 `dao` 不叫 `orderDao`,類別名也沒出現,三條都不成立,被擋。
- 副作用:作者為了過閘會在測試裡塞一個類別名字面值。守衛因此只證「有人提到名字」,和 RETIRE-IF 預見的失效是同一個,但預設是 block。

### F9
severity: minor
blocking: 否(有 `room_guard.dao: warn` 可降級,但屬字面照做就爆的輸入)
- 段落:做法 2,版本號。
- 引句:「版本取註解參數裡的 `version = 整數`」
- 失敗情境:`version = 99999999999` 或 `2147483647`,「a+1 到 b 每一版」的迴圈不設上限,掛鉤卡住。同一個類別含兩個 `@Database`(同檔)、巢狀或內部類別(完整名稱是 `Outer.Inner` 還是 `Outer$Inner` 沒說)、預設包(沒有點,不符結構檔路徑形狀)都沒有定義。
- spec 的資料型態沒訂上限,也沒寫「超過 N 版就當判不出」。

### F10
severity: minor
blocking: 否
- 段落:做法 2,升級路徑。
- 引句:「終點非測試路徑的 `Migration(x, y)` 與這個類別註解裡的 `AutoMigration(from = x, to = y)` 當成邊」
- 失敗情境:
  - `Migration(1, 2)` 寫了但沒有 `addMigrations`,實際上 Room 找不到路徑會閃退,守衛放行。
  - `AutoMigration(to = 2, from = 1)` 引數順序顛倒或夾 `spec =`,格式沒定義。
  - `Migration(START, END)` 用常數,對應 S10 的版本常數,但邊用常數時沒說怎麼處理。
- 跟隱患節「Migration 不帶類別資訊」重疊的部分已被誠實界線承認,不重報,這裡是承認範圍之外的「沒註冊」。

### F11
severity: minor
blocking: 否
- 段落:做法 2,升級測試。
- 引句:「而且它這次改過,或某行 `runMigrationsAndValidate(` 帶著 b」
- 失敗情境:
  - 測試檔因為別的原因被碰過(改縮排、換 import),就算「這次改過」。
  - 「帶著 b」若用子字串比對,b=2 會命中 `12`、`20`、`runMigrationsAndValidate(DB, 1, ...)` 後面的雜訊。字邊界沒說。
- 這是靜態比對,誠實界線只承認「不證測試真的驗了結果」,沒承認連「測試和這次升版有關」也證不到。

### F12
severity: minor
blocking: 否
- 段落:做法 1,結構檔判定。
- 引句:「內容是 JSON、帶 `formatVersion` 與 `database.identityHash` 兩個鍵」
- 失敗情境:`2.json` 遇到合併衝突標記、BOM、git LFS 指標或非 UTF-8,被當「不算結構檔」。接著 S5 的訊息說「缺結構檔」,但檔其實在,訊息誤導。
- `.kt`/`.java` 非 UTF-8 解碼失敗的處理也沒寫(靜默放行還是 rc2)。

### F13
severity: minor
blocking: 否
- 段落:做法 5。
- 引句:「不是 git、淺層 clone、git 算不出來 → 講一句、放行」
- 失敗情境:
  - 範圍終點為全 0(刪除分支):`note-shape` 有專門處理,spec 沒寫,又沒有測試。
  - `--diff` 格式不對、設定檔 JSON 壞掉、`room_guard.gate` 填了 `Block` 或 `warning`:rc 與提示沒定義。`note-shape` 的 `_note_shape_config` 有 warns 慣例,這裡沒對應。
  - 筆記形狀擋有 `_nodehome_clamp_base` 截到上線點,spec 沒說這道要不要;不截的話新接入的專案第一次推送就吃上面 F1 的整包。

### F14
severity: minor
blocking: 否
- 段落:實務隱患「效能」。
- 引句:「只讀改動檔、改動行號與終點的測試檔內容」
- 問題:這與做法 2 自相矛盾。
- 失敗情境:判「終點有沒有 `Migration(x, y)`」要搜整個非測試樹,結構檔要列出整個 schema 目錄(`ls-tree -r` 全樹),`_nodehome_list` 就是對整個 tip 做 `ls-tree -r --full-tree`。大 repo 的成本主要在這,不是「只多幾次 git 呼叫」。
- 另外 20 秒單次 git 逾時(`_nodehome_list` 預設)的後果沒定義:逾時算放行還是 rc2。

### F15
severity: minor
blocking: 否
- 段落:做法 2,降版。
- 引句:「版本變小 → 擋(Room 預設不支援降版)」
- 失敗情境:合併主線、rebase 後強推、revert 一個還沒發布的升版,範圍的起點與終點之間版本變小。revert 提交整個被擋,出口只有 `LUMOS_SKIP_ROOM_GUARD=1`。
- 這跟 F1 的範圍問題同族:合併時 `rsha..lsha` 會把主線上別人尚未受這道把關的 DAO 與升版算到自己頭上。

### F16
severity: minor
blocking: 否
- 段落:lands_in 與 related 的交叉引用。
- 查證:`Systems/test-quality-cli` 存在;`Systems/room-guard` 不存在,是要新開的節點;`Projects/Android端到端驗收_計劃` 存在;`test-quality-standard.md` 與 `03-寫回圖譜.md` 都在 `skills/lumos-project-notes/commands/`。
- 目標檔都對得上,`room-guard` 是新建節點的預期。

### 實務隱患鏡頭
- 金流:無。只讀提交內容,不碰付款流程(已讀,同意 spec 的排除)。
- 對外送出:無。只跑本機 git(同意)。
- 不可逆:無。只擋推送,不改檔(同意)。
- 守衛面:有,見 F1 到 F8。預設 `block` 加上 F1、F2、F4、F5、F8 的誤擋,對既有 Room 專案的第一次推送衝擊最大。
- 資料損毀與併發:無。只讀。
- 效能與資源:有,見 F9(版本迴圈)與 F14。
- 相容:F1 提到的舊版 lumos 退路是空樹,和 spec「回 2 放行」只處理了子指令不存在的一半。

最嚴重 severity: major,blocking 共 9 條(F1 到 F8,另加 F13 的隱含條件不計)。

更正:blocking 共 8 條,為 F1、F2、F3、F4、F5、F6、F7、F8;F9 到 F16 為 minor、blocking 否。
