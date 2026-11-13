---
type: project
status: doing
created: 2026-11-13
updated: 2026-11-13
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/guard-kill
  - Systems/棧別提問表態閘
  - Systems/lumos-cli-lifecycle
---
# 人裁殺傷力在真實Android專案跑得起來_計劃

## 白話

[[Projects/情境題答案要引規格出處與回寫循環_計劃]] 做好的人裁循環(規格沒寫 → 人點頭 → 先證明「把這段換成同一列另一種寫法、綁的測試會紅」→ 寫回條款),2026-11-13 第一次在真的 Gradle Android 專案跑,循環本身走通,但最常見的情境跑不動:把 `flatMapLatest` 換成 `flatMapConcat` 驗殺傷力時,檔頭逐一寫的 import 沒跟著換,換完編譯失敗,判成弱證據、人裁一律被拒。另外 `lumos init` 給 Android 的跑單支測試指令是壞的、錯誤訊息指向不存在的旗標、殺傷力帳本看不出失敗原因。這份計劃把這四個缺口補掉,讓人裁在真實 Android 專案用得起來;它也是 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 正反兩向共用的「換成兄弟寫法會紅」零件的地基。缺口原文在 [[Issues/人裁殺傷力在真實Android專案跑不動的四個缺口]]。

設計審 r1 後換了形狀:import 不再由工具猜(型錄觸發字混著成員名、點號寫法、跨套件名稱,猜套件會補出不存在的 import),改由給壞法的人或 AI 用 `--import` 明寫;跑測試指令不再由工具推模組(Android 的單元測試任務是每模組、每 flavor 各一條),改成偵測到 Android 就說明格式、要人照自己的任務填。

PRIOR-ART: Android 單元測試要跑單支,得對變體任務加 `--tests`(`:app:testDebugUnitTest --tests …`),頂層 `test` 不收 `--tests`;有 product flavor 時變體是 `<flavor><BuildType>`,任務名跟著變(`testFreeDebugUnitTest`),AGP 9 起預設只建受測建置類型的單元測試任務——所以任務名只能照專案實際填,工具不猜;Kotlin 編譯器不對沒用到的 import 報警、`-Werror` 也不擋,所以「多加一行 import、舊的不刪」編譯安全;變異測試工具 PIT 在位元碼層改所以沒有 import 問題,但不產 API 層兄弟寫法、且在 Kotlin 上雜訊大(2026-11-13 實驗,見雙向追溯計劃〈待驗〉)——這一版留在原始碼層、import 由人明寫,位元碼層的自訂變異外掛留給雙向追溯計劃。
RETIRE-IF: 雙向追溯計劃改用位元碼層變異引擎(PIT 自訂外掛)取代原始碼層壞法後,`--import` 就該撤掉;或上線兩個月內實際人裁沒有一次用到 `--import`(真實專案都用整包 import)也撤掉。

## 舊否決比對

- 「壞法人宣告、不做自動變異生成」([[Projects/guard殺傷力驗證_計劃]] d1,理由兩軸:工具不內建語言知識、自動生成有等價變異不可判定):r1 草稿讓工具依觸發字自動補 import,設計審四席判它碰到第一軸(語言知識進工具)、也不再全是人宣告;改成 `--import` 由人明寫之後,壞法(含補的 import)全由人宣告,工具只驗格式——兩軸都不碰。
- 「另抽一支共用的殺傷力函式」([[Systems/guard-kill]] 那條否決):沿用 `recipes_override` 臨時配方那條路,只多一個 `also` 欄位;格式檢查照 `_kill_old_issue`/`_kill_new_issue` 的先例抽一支小檢查函式給人裁與殺傷力共用,不是另一套殺傷力函式。
- 「從程式的 import 猜功能歸屬」([[Systems/android-e2e-acceptance]] 那條否決):新形狀不從 import 猜任何東西。

## 用詞

- **補 import**:人裁用 `--import` 明寫、要在殺傷力壞法裡多加的 import 行;整行 fullmatch `import [A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+`(ASCII 識別字,不收 `*`、`as`、反引號、尾隨空白),最後一段是 `<名稱>`。
- **連帶替換(`also`)**:人裁臨時配方除了段內那一處 `old → new`,在同一支檔額外做的替換,資料形狀是清單(這一版最多一筆);只由 `--import` 產生,使用者不能直接給。行一律只用 `\n` 切(不用 `splitlines`)。
- **檔頭區**:照 Kotlin 文法 kotlinFile 規則(shebang、檔案註記、package、import 清單):剝掉檔首 BOM 後,檔案開頭到第一個既不是空行、註解(行註解與可巢狀的區塊註解,註解內的行一律跳過、不算 import)、`@file:` 註記(括號跨行時跟到閉合)、`package`(後接任何空白)、`import` 的行之前。註解與字串(含三引號字串、字串樣板)照全庫唯一的 Kotlin 剝法 `_strip_c_comments(kotlin=True)` 剝,字串裡的 `import` 不算、字串裡的括號不數;行尾落在註解、字串或 `@file:` 括號裡的行不當插入點。(代碼審 r1 G3 改;r2 R2 改用既有剝法)
- **Android 專案**:預設平台的根(`load_platforms` 給的 `root`,不是 repo 根)往下的建置檔裡,`_android_build_texts` 剝完註解後有 `_KT_BUILD_ANDROID` 認得的 Android 外掛宣告——跟既有 Android 現成檢查提醒(`_lint_android_ci_advisories`)同一套判法。
- **任務清單**:沿用 detekt 那組既有的 Gradle 命令解析(`_detekt_walk_segments` 取段,含剝環境變數與 `env`/`time` 包裝、`sh -c` 展開):每一個第一個檔名是 `gradlew` 或 `gradle` 的段都算(`&&`、`;`、`||` 串起來的每一段,任務合併),取那個詞之後、不以 `-` 開頭的詞;帶值選項表用 `_GRADLE_VALUE_OPTS` 加 `--tests`,選項的值不算任務;`#` 開頭的詞起到行尾是 shell 註解,不算任務;那一段的 `-p`/`--project-dir` 的值是它的專案目錄(相對平台根)。(代碼審 r1 G1 改;r2 R1 改每一段、註解、`-p`)
- **擋下的 test 任務**:任務清單裡,(a) 沒有模組前綴、剛好是 `test` 或 `:test`(根專案的 test),而且是 Android 專案;或 (b) `:<模組>:test` 或相對根專案的 `<模組>:test`(Gradle 兩者同義),而那個模組是 Android 模組(模組資料夾的 `build.gradle(.kts)` 剝完註解後 `_KT_BUILD_ANDROID` 認得)。那一段有 `-p` 時,(a) 的「Android 專案」與 (b) 的模組資料夾都從那個專案目錄算。純 JVM 模組的 `:core:domain:test` 不擋;`testDebugUnitTest` 這類變體任務不擋。(r2 R1 加 `:test` 與 `-p`)
- **觸發字**:沿用 [[Projects/情境題答案要引規格出處與回寫循環_計劃]] 的定義(Kotlin 型錄〈情境決策表〉每列的觸發字)。

## 範圍

1. **人裁收 `--import`**(`lumos situation-rule`,可重複給):
   - 每個 `--import` 先驗形狀(〈用詞〉補 import);`<名稱>` 要在 `--new` 裡以識別字整字出現(`\b<名稱>\b`),而且 HEAD 那支檔的檔頭區沒有 import 它(同一行、同名不同套件、或 `<套件>.*` 都算已有);不合一律 rc 2、殺傷力不跑。名稱不必是觸發字(D-5 換成 `SharingStarted.Lazily` 要補 `SharingStarted`)。
   - 插入點:HEAD 那支檔**檔頭區**裡最後一行 `import ` 開頭的行之後(逐行比對、取行號,不用子字串);檔頭區沒有 import 就插在 `package` 那一行之後;兩者都沒有就拒絕。檔頭區以外的行一律不看(多行字串裡的 `import ` 開頭行不算)。舊 import 不刪(Kotlin 不因沒用到的 import 失敗)。
   - 產生一筆 `also`(old 是插入點那一整行加換行,new 是那一行加換行再加所有 `--import` 行),交給殺傷力驗證;人裁在跑殺傷力前先用範圍 2 的同一支檢查驗一次。
   - 確認畫面多印「補 import」那幾行;治理帳 situation-rule 那筆多一欄 `imports`(清單);kill-log 那筆的 `note` 帶上補的 import。
2. **殺傷力驗證認 `also`**(`cmd_guard_kill` 的 `recipes_override` 路徑):
   - 只有臨時配方(`recipes_override`)認 `also`;筆記宣告的配方格式不變、帶了也不理。
   - 一支小檢查函式(`_kill_also_issue`,人裁與殺傷力共用,照 `_kill_old_issue` 先例):每筆 `also` 的 `old` 要是一整行(以換行結尾、只有一行),`new` 要以 `old` 開頭、多出來的每一行都是〈用詞〉補 import 的形狀。
   - 套用:主替換套好之後在記憶體裡對字串逐行找 `old` 那一行(整行相等),恰好一行才替換;不合判 `error`(不是 `drifted`:`also` 每次由這次的 HEAD 現算,不會因舊配方漂移而對不上,對不上就是錯),不寫檔、不跑壞法那一次(基準在這之前可能已跑過——跟 old 不合的既有判法同一處)。
   - 還原照舊用 git checkout 整支檔還原,`also` 一起還原。
   - 執行目錄:基準與壞法在隔離工作樹裡的平台根跑 run_cmd(工作樹加上平台根相對所在 repo 最上層的路徑),跟推送前的合約測試閘(`_run_bound_tests` 在平台根跑)同一處,同一條 run_cmd 兩邊都跑得起來;平台根就是 repo 最上層時就是工作樹本身;平台根在 HEAD 那一版不是資料夾判 `error`、基準不跑。配方的 `file` 照舊從工作樹最上層算。
3. **init 偵測到 Android 時給可用的格式**:`lumos init` 判斷是 Android 專案時,kotlin-junit 與 java-junit 兩個 profile 的骨架 run_cmd 改成 `./gradlew :YOUR_MODULE:testDebugUnitTest --tests '*{method}'`(佔位用 `YOUR_MODULE`,不用角括號——角括號在 shell 是轉向),同一份骨架的 `_請先確認` 說明多一句:換成測試所在模組;有 product flavor 時任務名是 `test<Flavor>DebugUnitTest`,`./gradlew tasks --all` 看實際名稱。單平台與多平台兩條骨架路徑都改;不是 Android 照舊。
4. **人裁先查 Android 的 run_cmd**:預設平台的 profile(`load_platforms` 的 `profile_name`,不是平台鍵名)是 kotlin-junit 或 java-junit,而 run_cmd 的任務清單有〈用詞〉擋下的 test 任務、或 run_cmd 含 `YOUR_MODULE` 佔位時,在跑殺傷力之前拒絕(rc 2),印出:要改哪個設定檔的哪個鍵、正確格式 `./gradlew :<模組>:test<Variant>UnitTest --tests '*{method}'`(不加 `cd`:殺傷力在隔離工作樹裡的平台根執行 run_cmd,跟推送前的合約測試閘同一處,見範圍 2)、這段所在檔推出的模組候選(從 `--file` 往上找最近一層有 `build.gradle` 或 `build.gradle.kts` 的資料夾,相對平台根轉成 `:a:b`;資料夾名不合 `^[A-Za-z0-9_.-]+$` 就不印候選)、flavor 與 `./gradlew tasks --all` 的提示。不自動改設定。「Android 專案」從平台根判(既有 lint 提醒從 repo 根判,這裡要的是跑測試那個 Gradle 專案,刻意不同)。
5. **人裁補 `--diff`**:`lumos situation-rule --diff <A..B>` 跟 `code-loop check --diff` 同一套規則(`_codeloop_disp_range`):分支找得到主線分岔點(或分支頂端已在主線)時一律照共用函式、`--diff` 不生效,這時印一行「你給的 --diff 沒採用,改用 <實際範圍>」(只要給了 `--diff` 而共用函式回的範圍字串不等於它就印);只在算不出分岔點時用 `--diff`。入口另驗:值不准以 `-` 開頭(同 `impact`、`pitfalls` 的先例),只收兩點寫法 `A..B`(三點寫法拒絕),兩端都要解析得到提交,右端要等於 HEAD 的提交,否則 rc 2。不改那支共用函式。
6. **殺傷力帳本留失敗摘錄**:判定是 `killed_unattributed`、`timed_out_weak` 或 `abort`(基準非綠)時,kill-log 那筆多一欄 `fail_excerpt`(跟既有 `tail` 分開,`tail` 不改):取那次執行的輸出(`_kill_run` 回的全文,本來就有 256KB 上限、超過砍中段),**先遮路徑**——隔離工作樹路徑(字面與 realpath 兩種,macOS 的 `/var/…` 與 `/private/var/…`)換成 `<worktree>`、使用者家目錄換成 `~`——再挑錯誤行:以 `e: `、`error:`、`E  `、`FAILED ` 開頭,以 ` FAILED` 結尾,或 `* What went wrong:` 之後到下一個空行;每行截到 200 字、依原順序取到 800 字;一行都挑不到才退回取結尾 800 字。`result_out` 每列也帶 `fail_excerpt`;人裁被拒時訊息印它(經 `_kill_esc`,最多 12 行)。
7. **文件**:[[Systems/guard-kill]] 加一行 WHY 講 `also` 與 `fail_excerpt`;[[Systems/棧別提問表態閘]] 人裁那段補 `--import`、`--diff`、Android run_cmd 檢查;[[Systems/lumos-cli-lifecycle]](init 骨架的家)加一行 WHY 講 Android 骨架。

## 不做

- 不做位元碼層變異(PIT 自訂外掛):留給 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]]。
- 不自動猜 import 的套件、不自動推 Gradle 模組與任務名:設計審 r1 四席證明兩者在型錄現有觸發字與常見 Android 版面上都會猜錯。
- 不自動改已接入專案的 `.lumos/config.json`:範圍 4 只拒絕並印正確寫法。
- 不處理 import 別名(`import … as X`)與 Java 的 import:別名少見、Java 不在情境決策表。
- 不改筆記宣告配方的格式、不改既有 `tail` 欄的語意。

## 實務隱患

- `--import` 給錯(套件寫錯):殺傷力會編譯失敗、判 killed_unattributed 被拒,`fail_excerpt` 會印出 `Unresolved reference`,人看得懂、改了重跑;工具不替人驗套件存在(那要跑編譯器)。
- 連帶替換放寬了「只改這一段」:只准多加 import 行、不准刪改既有行;`_kill_also_issue` 要有「多出來不是 import 行就 error」的反向案例。
- 隔離工作樹不含 git 忽略的檔(`local.properties` 的 `sdk.dir`、`google-services.json`):沒設 `ANDROID_HOME` 的機器基準會 abort;`fail_excerpt` 會印出 SDK 找不到之類的原因。2026-11-13 實驗副本在設了 `ANDROID_HOME` 的機器上不帶 `local.properties` 照跑得起來。
- Gradle daemon:`_kill_run` 收的是測試程序群組,Gradle daemon 自己 setsid、不在群組裡,中斷或逾時後會閒置到 daemon 自己的逾時才結束;不另處理(daemon 是使用者機器上本來就常駐的東西)。
- 冷建構時間與磁碟:每次殺傷力都在新工作樹冷建構,基準加壞法可能十幾分鐘,`build/` 與 `.gradle` 留在暫存工作樹裡、跑完照 `_isolated_worktree` 收尾刪掉(被強殺的留給清殘骸)。
- `fail_excerpt` 進殺傷力帳本,而 `docs/.kill-log.jsonl` 在工具鏈 repo 是進版控的:摘錄可能含測試輸出(路徑、測試名、測試印的東西),已把工作樹路徑遮成 `<worktree>`、家目錄遮成 `~`(例:SDK 找不到時的 `/Users/<帳號>/Library/Android/sdk`);不宣稱不含祕密,800 字上限與只在弱證據判定時存讓量很少。
- 新舊版本混用:`also` 只在同一次執行內傳、不落帳;`fail_excerpt` 是新欄位,舊版讀帳不認得就略過;治理帳 situation-rule 多 `imports` 欄,舊版讀帳略過不認得的欄。
- 已排除:金流:不碰付款與金額。
- 已排除:對外送出:只在本機隔離工作樹改檔跑測試、寫本機帳。
- 已排除:不可逆:連帶替換只發生在隔離工作樹、跑完整支檔還原;寫回的條款與帳本行為不變。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| Android 跑單支單元測試要用變體任務加 --tests | 頂層 test 不收 --tests,要 :app:testDebugUnitTest | https://kaweah.freedombox.rocks/kiwix/stackoverflow.com_en_all_2023-11/questions/51823185/how-to-run-single-test-class-in-android-using-gradle-command |
| Android 跑單支單元測試要用變體任務加 --tests | Gradle 測試過濾 --tests 是測試任務的選項 | https://docs.gradle.org/current/userguide/java_testing.html |
| 任務名照專案實際填、工具不猜 | 變體是 flavor 加建置類型,任務名跟著變 | https://android-developers.googleblog.com/2015/12/leveraging-product-flavors-in-android.html |
| 任務名照專案實際填、工具不猜 | AGP 9 起預設只建受測建置類型的單元測試任務 | https://slack-chats.kotlinlang.org/t/33344942/i-m-upgrading-to-agp-9-from-8-are-testreleaseunittest-not-go |
| 補 import、舊的不刪 | 沒用到的 import 只是 IDE 檢查,編譯器不報 | https://jetbrains.com/help/inspectopedia/KotlinUnusedImport.html |
| 補 import、舊的不刪 | Kotlin 維護者:編譯器沒有也不打算有這個警告 | https://slack-chats.kotlinlang.org/t/452679/i-see-that-kotlin-compiler-doesn-t-issue-a-warning-for-unuse |
| import 由人明寫、不由工具猜套件 | 設計審 r1 四席:型錄觸發字混著成員名、點號寫法、跨套件名稱,猜會補出不存在的 import | 實測 2026-11-13:設計審 r1 邊界與正確性席用 `_KT_DT_ROWS` 逐列列出觸發字,D-5、D-7、D-16 的成員名與跨套件名都會補出不存在的 import |
| 失敗摘錄挑錯誤行而不是只取結尾 | Gradle 失敗時結尾是固定提示,編譯錯誤行在前面(設計審 r1 三席) | 實測 2026-11-13:實驗副本 Gradle 編譯失敗輸出,`e:` 錯誤行在 FAILURE 與 Try 區塊之前 |
| 缺口來源 | 2026-11-13 真實 Gradle 專案實跑 | [[Issues/人裁殺傷力在真實Android專案跑不動的四個缺口]] |
| 先做 A 再做 B | 使用者對話裁定 | 使用者 2026-11-13:「好,先做 A,再做 B」 |

## 驗收條款

- [S1] 當人裁帶 --import 而且那一行的名稱在 --new 裡以識別字整字出現、檔頭區還沒 import 它,人裁的殺傷力壞法 應 在檔頭區最後一行 import 之後加上那一行 [test:t_situation_rule_import_flag_inserts]
- [S2] 當 --import 的名稱沒在 --new 裡以識別字整字出現、或形狀不合、或檔頭區已經 import 了這個名稱,人裁指令 應 在跑殺傷力之前拒絕 [test:t_situation_rule_import_flag_rejects]
- [S3] 當臨時配方的連帶替換多出來的不是 import 行,殺傷力驗證 應 判 error 而且不寫檔、不跑壞法那一次 [test:t_guard_kill_also_rejects_non_import]
- [S4] 當筆記宣告的配方帶了 also 欄位,殺傷力驗證 應 不理會那個欄位 [test:t_guard_kill_also_only_override]
- [S5] 當 lumos init 判斷是 Android 專案,骨架 應 給 testDebugUnitTest 格式並以 YOUR_MODULE 佔位、說明 flavor [test:t_init_android_run_cmd]
- [S6] 當預設平台的 profile 是 kotlin-junit 或 java-junit、是 Android 專案而 run_cmd 含頂層 test 任務或 YOUR_MODULE 佔位,人裁指令 應 在跑殺傷力之前拒絕並印出正確格式與模組候選 [test:t_situation_rule_android_run_cmd_check]
- [S7] 當人裁帶 --diff 而算不出主線分岔點,人裁指令 應 用那個範圍算情境段 [test:t_situation_rule_diff_flag]
- [S8] 當殺傷力判定是 killed_unattributed、timed_out_weak 或 abort,殺傷力帳本 應 存下挑出錯誤行的失敗摘錄 [test:t_kill_log_fail_excerpt]
- [S9] 當假平台在檔頭缺少新寫法觸發字的 import 時編譯失敗,人裁帶對的 --import 應 判 killed 並寫回條款 [test:t_situation_rule_import_e2e]
- [S10] 當在真實 Android 專案以逐一 import 的檔跑人裁(flatMapLatest 換 flatMapConcat、帶 --import、綁連送兩次值的測試),人裁指令 應 判 killed 並寫回條款 [manual:測試品質實驗室 Android 副本(或重建同樣的副本),SearchViewModel 改回逐一 import 後帶 --import 跑 lumos situation-rule,看判定是 killed、計劃多一條]
- [S11] 當平台根是 repo 的子資料夾,殺傷力驗證 應 在隔離工作樹裡的平台根跑 run_cmd,同一條 run_cmd 合約測試閘也跑得起來 [test:t_guard_kill_runs_at_platform_root]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 檔頭有 `import kotlinx.coroutines.flow.flatMapLatest` 等三行 import,`--old` 含 flatMapLatest、`--new` 含 flatMapConcat,`--import "import kotlinx.coroutines.flow.flatMapConcat"` | 臨時配方帶一筆 also:最後一行 import 之後多一行 flatMapConcat 的 import;確認畫面印出這一行;治理帳 imports 欄有它 | 〈範圍〉1;2026-11-13 實跑缺口 |
| S1 | 同上但檔裡沒有任何 import、只有 package 行 | also 插在 package 那一行之後 | 〈範圍〉1 插入點 |
| S1 | 檔頭三行 import,函式裡的多行字串有一行 `import foo.Bar` | also 插在檔頭第三行 import 之後,不插進字串 | 〈用詞〉檔頭區 |
| S1 | D-5:`--old` 含 `WhileSubscribed(5000)`、`--new` 含 `SharingStarted.Lazily`、檔頭沒 import SharingStarted,`--import "import kotlinx.coroutines.flow.SharingStarted"` | 收下、產生 also | 〈範圍〉1 名稱不必是觸發字 |
| S2 | `--import "import kotlinx.coroutines.flow.flatMapLatest"`(檔頭已 import flatMapLatest) | rc 2、殺傷力不跑 | 〈範圍〉1 檔頭已有就拒絕 |
| S2 | `--import "import kotlinx.coroutines.flow.debounce"`,`--new` 裡沒有 debounce | rc 2 | 〈範圍〉1 名稱要在 --new 出現 |
| S2 | `--import "import kotlinx.coroutines.flow.*"` 或帶 `as` | rc 2、殺傷力不跑 | 〈用詞〉補 import 形狀 |
| S2 | 檔裡已有 `import kotlinx.coroutines.flow.flatMapConcat`、又給同一行 | rc 2(多餘) | 〈範圍〉1 已有就拒絕 |
| S3 | also 的 new 多一行 `val x = 1` | 判 error、檔不動、不跑壞法那一次 | 〈範圍〉2;〈實務隱患〉只准多加 import |
| S4 | 筆記配方帶 also,guard kill 正常呼叫 | also 不套用,結果跟沒帶一樣 | 〈範圍〉2 只有臨時配方認 |
| S5 | 平台根有 `app/build.gradle.kts` 宣告 com.android.application | run_cmd 是 `./gradlew :YOUR_MODULE:testDebugUnitTest --tests '*{method}'`,_請先確認 提到 flavor 與 tasks --all | 〈範圍〉3;Gradle 與 Android 文件 |
| S5 | 建置檔寫 `alias(libs.plugins.android.application)`(`_KT_BUILD_ANDROID` 認得的寫法) | 同上 | 〈用詞〉Android 專案沿用既有判法 |
| S5 | 不是 Android 的 Kotlin 專案 | run_cmd 照舊 `./gradlew test --tests '*{method}'` | 〈範圍〉3 不是 Android 照舊 |
| S6 | 多平台設定平台鍵 `kotlin`(profile kotlin-junit)、run_cmd `./gradlew test --tests '*{method}'`、Android 專案、`--file` 在 `feature/search/src/main/…`(`feature/search/build.gradle.kts` 存在) | rc 2、殺傷力不跑、印格式與模組候選 `:feature:search` | 〈範圍〉4 看 profile 名、從檔推模組 |
| S6 | run_cmd `./gradlew clean test --tests '*{method}'` | 同樣 rc 2(任務清單裡有頂層 test) | 〈用詞〉頂層 test 任務 |
| S6 | run_cmd 是 `./gradlew :YOUR_MODULE:testDebugUnitTest --tests '*{method}'`(沒改佔位) | rc 2、要人換成實際模組 | 〈範圍〉4 佔位未改 |
| S6 | run_cmd `./gradlew :app:testDevDebugUnitTest --tests '*{method}'` | 不擋,照舊跑殺傷力 | 〈用詞〉變體任務不擋 |
| S6 | run_cmd `./gradlew :core:domain:test --tests '*{method}'`,`core/domain/build.gradle.kts` 只套 `kotlin("jvm")` | 不擋(純 JVM 模組的 test 收 --tests) | 〈用詞〉擋下的 test 任務只擋 Android 模組 |
| S6 | 平台根是 `android`,run_cmd `./gradlew test --tests …` | rc 2,印的格式不加 `cd`、講在平台根執行 | 〈範圍〉4;範圍 2 殺傷力與合約測試閘都在平台根跑 |
| S7 | repo 沒有 main 也沒有 master、分支是 develop,帶 `--diff develop~2..HEAD` | 用那個範圍算出情境段,不印算不出範圍 | 〈範圍〉5;2026-11-13 實跑缺口 |
| S7 | 分支找得到主線分岔點,另帶 `--diff` 指一個不同範圍 | 照分岔點算,印「--diff 沒採用」那一行 | 〈範圍〉5 同 _codeloop_disp_range |
| S7 | `--diff=--output=x` 或右端不是 HEAD | rc 2 | 〈範圍〉5 入口驗 |
| S8 | 壞法編譯失敗,輸出依序是三行 `e: file:///private/var/…/wt/app/…kt:12:5 Unresolved reference: flatMapConcat`、FAILURE、What went wrong、Try 四行、BUILD FAILED | fail_excerpt 含三行 e:(路徑變成 `<worktree>`)與 What went wrong 區塊;tail 欄不變;人裁拒絕訊息印出摘錄 | 〈範圍〉6;設計審 r1 三席 |
| S8 | 紅燈來自別支測試,Gradle 輸出有 `OtherTest > foo() FAILED` | fail_excerpt 含那一行 | 〈範圍〉6 行尾 FAILED |
| S9 | 假平台的 run_cmd 腳本:被改檔用到 `flatMapConcat` 卻沒有它的 import 就印 `e: Unresolved reference` 並回 1,否則跑測試(基準用 flatMapLatest、照常綠);不帶 `--import` 跑人裁 → killed_unattributed;帶 `--import` → killed | 不帶時 rc 2、計劃不動;帶時寫回條款 | 〈範圍〉1 端到端;設計審 r1 整合席 |
| S10 | 實驗副本逐一 import、帶 `--import`、綁 onlyLatestQueryShown | killed、計劃多一條條款 | 〈範圍〉1 真實專案 |
| S11 | 平台根 `sub`、run_cmd `python3 test_guard.py`(不帶 cd,測試檔只在 sub/ 底下) | 殺傷力基準綠、壞法紅、判 killed,跑的資料夾是工作樹裡的 sub;同一條 run_cmd 合約測試閘綠 | 〈範圍〉2 執行目錄;代碼審 r1 g1 |
| S11 | 平台根在 HEAD 那一版不存在(沒提交) | 判 error、講平台根、基準不跑 | 〈範圍〉2 執行目錄 |

## 回退

還原這次的提交即可:連帶替換只在隔離工作樹裡發生、跑完還原;init 只影響之後新產生的骨架;kill-log 多的 `fail_excerpt` 欄與治理帳多的 `imports` 欄,舊版照讀(略過不認得的欄)。

## 天花板

1. `--import` 只驗形狀與名稱,不驗套件真的存在;寫錯會編譯失敗、判弱證據被拒(有摘錄可看),不會誤放行。
2. 原始碼層壞法只換文字;簽名不同的兄弟寫法(參數不同)換了會編譯失敗,這一版不處理,留給位元碼層的雙向追溯計劃。
3. Android 專案判法沿用 `_android_build_texts` + `_KT_BUILD_ANDROID`,它也讀 `gradle/libs.versions.toml`:約定外掛專案只要版本目錄宣告了 AGP 就判得到;反過來,版本目錄列了 AGP 的非 Android 專案會被判成 Android——所以範圍 4 的 `:<模組>:test` 只在那個模組自己的建置檔是 Android 時才擋。建置檔深過三層判不到,照舊骨架、人裁不先擋(壞的 run_cmd 在基準 abort,摘錄看得到原因)。
5. `testDebugUnitTest` 不帶模組前綴、在多模組專案會讓沒有那支測試的模組因 No tests found 失敗,這一版不擋(要跑完基準才 abort,摘錄看得到);`gradle`、`gradlew` 以外的建置指令不判。
4. 模組候選只看 `--file` 往上最近的建置檔資料夾;用 `projectDir` 改目錄的模組候選會不對,所以只當「候選」印,不寫進設定。

## 審計修正紀錄

- r1(2026-11-13,4 席):29 條/blocking 11(席報告總結句加總)/前掃 12 條先折;四席一致指出工具猜 import 套件與猜 Gradle 模組都會猜錯——換形狀成 `--import` 由人明寫、run_cmd 只偵測 Android 並說明格式;失敗摘錄改挑錯誤行;`--diff` 補忽略提示與入口驗;偵測沿用 `_android_build_texts`;init 骨架說明落到 Systems/lumos-cli-lifecycle;加假平台端到端測試。席報告在 governance/review-reports/人裁殺傷力在真實android專案跑得起來/。
- r1 收斂後複審(2026-11-13,1 席通才,不記帳):12 條/blocking 2/全修;頂層 test 只擋 Android 模組、平台根在子目錄時格式加 cd、插入點限檔頭區、摘錄規則細化、--import 名稱放寬到 --new 出現且未 import 的識別字。報告在 governance/review-reports/人裁殺傷力在真實android專案跑得起來/r1-收斂後複審.md。
- 代碼審 r1(2026-11-13,7 席):20 條/blocking 2/兩條 major 是殺傷力與合約測試閘對同一條 run_cmd 執行目錄不同(改成殺傷力在平台根跑、拿掉 `cd <平台根> &&` 的教法,新增 S11)與 Gradle 任務清單自寫切詞(改用 detekt 那組拆段與選項表、`app:test` 也擋);其餘 minor 全折(檔頭區照 Kotlin 文法、同一批 --import 同名擋、遮路徑看邊界、S1 S2 條款字面對齊範圍 1),x1 x2 放行。
- 代碼審 r1 卷證:席報告、收貨分組與處置在 governance/review-reports/code-人裁殺傷力android/(r1-intake.md)。
- 代碼審 r2(2026-11-13,7 席):10 條/blocking 3/兩條 major 是又另寫一套(檔頭區自寫 Kotlin 剝註解改走既有 `_strip_c_comments`、`--diff` 自叫 git 改走 `_lens_full_sha`),其餘全折:任務清單看每個 gradle 段、shell 註解不算、`-p` 換專案目錄、`:test` 照頂層 test 擋、run_cmd 不是字串照設定錯 rc 2、檔頭掃描只留 import 與 package 行(4MB 空行檔記憶體回到修補前量級)。
- 代碼審 r2 卷證:席報告、收貨分組與處置在 governance/review-reports/code-人裁殺傷力android/(r2-intake.md)。
