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
  - Systems/test-profile-multiplatform
---
# 人裁殺傷力在真實Android專案跑得起來_計劃

## 白話

[[Projects/情境題答案要引規格出處與回寫循環_計劃]] 做好的人裁循環(規格沒寫 → 人點頭 → 先證明「把這段換成同一列另一種寫法、綁的測試會紅」→ 寫回條款),2026-11-13 第一次在真的 Gradle Android 專案跑,循環本身走通,但最常見的情境跑不動:把 `flatMapLatest` 換成 `flatMapConcat` 驗殺傷力時,檔頭逐一寫的 import 沒跟著換,換完編譯失敗,判成弱證據、人裁一律被拒。另外 `lumos init` 給 Android 的跑單支測試指令是壞的、錯誤訊息指向不存在的旗標、殺傷力帳本看不出失敗原因。這份計劃把這四個缺口補掉,讓人裁在真實 Android 專案用得起來;它也是 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]] 正反兩向共用的「換成兄弟寫法會紅」零件的地基。缺口原文在 [[Issues/人裁殺傷力在真實Android專案跑不動的四個缺口]]。

PRIOR-ART: Android 單元測試要跑單支,得對變體任務加 `--tests`(`:app:testDebugUnitTest --tests …`),頂層 `test` 不收 `--tests`(Stack Overflow 與 Gradle 文件);Kotlin 編譯器不對沒用到的 import 報警、`-Werror` 也不擋(只有 IDE 檢查),所以「加一行兄弟函式的 import、舊的不刪」編譯安全;變異測試工具 PIT 在位元碼層改所以沒有 import 問題,但不產 API 層兄弟寫法、且在 Kotlin 上雜訊大(2026-11-13 實驗,見雙向追溯計劃〈待驗〉)——這一版留在原始碼層、只補 import,位元碼層的自訂變異外掛留給雙向追溯計劃。
RETIRE-IF: 雙向追溯計劃改用位元碼層變異引擎(PIT 自訂外掛)取代原始碼層壞法後,範圍 1 的 import 連帶替換就該撤掉;或連帶替換上線兩個月內實際人裁沒有一次用到(真實專案都用整包 import)也撤掉。

## 舊否決比對

- 「壞法人宣告、不做自動變異生成」([[Projects/guard殺傷力驗證_計劃]] d1):連帶 import 不是生成新壞法——壞法照舊由人在 `--old`/`--new` 宣告,工具只依固定規則補上「讓那個壞法編譯得過」的那一行 import;不另生任何變異。概念上擦邊,交設計審判。
- 「另抽一支共用的殺傷力函式」([[Systems/guard-kill]] 那條否決):沿用 `recipes_override` 臨時配方那條路,只多一個 `also` 欄位,不另抽。
- 「從程式的 import 猜功能歸屬」([[Systems/android-e2e-acceptance]] 那條否決):那是端到端驗收猜功能歸屬;這裡是依 import 決定補哪一行,不猜歸屬,不同件事。

## 用詞

- **連帶替換**:人裁臨時配方除了段內那一處 `old → new`,在同一支檔額外做的替換;只收「在舊寫法觸發字那一行 import 的下一行,加一行同一套件、新寫法觸發字的 import」。
- **Android application 模組**:repo 根有 `settings.gradle` 或 `settings.gradle.kts`,它 `include` 的某個模組(例 `:app`、`:feature:home`)的建置檔(`<模組路徑>/build.gradle` 或 `.kts`)套用了 Android application 外掛——寫法是外掛 id `com.android.application`,或 version catalog 別名(`alias(libs.plugins.<名>)` 的 `<名>` 去掉點與連字號、轉小寫後等於 `androidapplication`)。
- **逐一 import / 整包 import**:逐一 import 是 `import a.b.Name` 這種一行一個名字;整包 import 是 `import a.b.*`。
- **觸發字**:沿用 [[Projects/情境題答案要引規格出處與回寫循環_計劃]] 的定義(Kotlin 型錄〈情境決策表〉每列的觸發字)。

## 範圍

1. **人裁壞法連帶補 import**(`lumos situation-rule`):
   - 讀被推版本(HEAD)的那支檔;對 `--new` 含、`--old` 不含的每個該列觸發字 T_new:在 `--old` 含的該列觸發字裡,找檔頭有一整行剛好是 `import <套件>.<T_old>`(沒有 `as` 別名)的那一個——剛好一個就用它的套件;零個或多個(不同套件)就不產生。檔裡已有 `import <套件>.T_new` 或 `import <套件>.*` 也不產生。產生時:那一行 import 換成「原行 + 換行 + `import <套件>.T_new`」。舊 import 不刪(同檔別處可能還在用;Kotlin 不因沒用到的 import 失敗)。
   - 檔頭是整包 import、或 T_old 沒有被 import(全名呼叫或擴充函式另處引入)時不產生連帶替換。
   - 連帶替換交給殺傷力驗證(臨時配方多一個 `also` 清單);使用者不能自己給 `also`。人裁在跑殺傷力之前先用範圍 2 的同一支格式檢查驗一次產生的 `also`,不合就拒絕(rc 2)、不跑基準。
2. **殺傷力驗證認連帶替換**(`cmd_guard_kill` 的 `recipes_override` 路徑):
   - 只有臨時配方(`recipes_override`)認 `also`;筆記宣告的配方格式不變、帶了也不理。
   - 每筆 `also` 的 `old` 要在套完主替換之後的檔裡**整行比對**恰好一行、而且是一整行 import(符合 `^import [\w.]+$`);`new` 要以那一行開頭、只多一行 import。不合就判 `error`、不套用壞法、不跑壞法那一次(基準在這之前可能已跑過——跟 old 不合的既有判法同一處)。
   - 還原照舊用 git checkout 整支檔還原,`also` 一起還原。
3. **init 給 Android 對的跑單支測試指令**:`lumos init` 偵測到**恰好一個** Android application 模組時,kotlin-junit 與 java-junit 兩個 profile 的 run_cmd 都給 `./gradlew <模組>:testDebugUnitTest --tests '*{method}'`(`<模組>` 照 `settings.gradle` 的 `include` 原樣,例 `:app`);單平台與多平台兩條骨架路徑都改。零個或多個 application 模組、只有 library 模組、或 `settings.gradle` 不在 repo 根(Gradle 根在子目錄)時不猜,照舊給 `./gradlew test --tests '*{method}'`。
4. **人裁先查 Android 的 run_cmd**:預設平台的 profile(`load_platforms` 給的 `profile_name`,不是平台鍵名)是 kotlin-junit 或 java-junit、run_cmd 用頂層 `test` 帶 `--tests`(空白正規化後含 `gradlew test --tests`)、而範圍 3 的偵測算得出模組時,在跑殺傷力之前拒絕(rc 2),印出範圍 3 算出的正確寫法與要改的設定檔;算不出模組就不擋(照舊跑)。不自動改設定。
5. **人裁補 `--diff`**:`lumos situation-rule --diff <A..B>` 跟 `code-loop check --diff` 同一套規則(`_codeloop_disp_range`):分支找得到主線分岔點時一律用分岔點、`--diff` 不生效;只在算不出分岔點(或推的就是主線)時用 `--diff`。不改那支共用函式。算不出分岔點的擋下訊息本來就指向 `--diff`,補了旗標之後才成真。
6. **殺傷力帳本留輸出摘錄**:判定是 `killed_unattributed` 或 `timed_out_weak` 時,kill-log 那筆的 `tail` 存**壞法那次**執行輸出的最後 400 字(現況:survived 與 abort 存的是基準輸出最後 200 字,壞法輸出一律沒存);`result_out` 每列多一個 `tail` 欄帶同一段;人裁被拒時,訊息另印摘錄最後 5 行(經 `_kill_esc`)。
7. **文件**:[[Systems/guard-kill]] 加一行 WHY 講 `also`;[[Systems/棧別提問表態閘]] 人裁那段補連帶 import、`--diff`、Android run_cmd 檢查;[[Systems/test-profile-multiplatform]] 加一行 WHY 講 Android 骨架。

## 不做

- 不做位元碼層變異(PIT 自訂外掛):留給 [[Projects/雙向追溯_需求與語法選擇點互證_計劃]]。
- 不自動改已接入專案的 `.lumos/config.json`:範圍 4 只拒絕並印正確寫法。
- 不處理 import 別名(`import … as X`)與 Java 的 import:別名少見、Java 不在情境決策表;遇到照舊可能判弱證據,訊息印摘錄讓人看懂。
- 不改筆記宣告配方的格式。

## 實務隱患

- 連帶替換放寬了「只改這一段」:限定只能加一行同套件、同一列觸發字的 import,不能改別的;實作要有「不是 import 行就 error」的反向案例。
- 同一支檔有兩個 import 都含舊觸發字(不同套件):取跟新觸發字在情境決策表同一列、而且套件相同的那一行;找不到就不產生連帶替換(照舊可能判弱證據,訊息有摘錄)。
- 多模組專案的模組名:範圍 3 只在恰好一個 application 模組時給;測試在別的模組、或多個 application 模組時要人手改。init 骨架本來就要人確認(檔頭的「請先確認」)。
- Gradle 根在子目錄(例 `android/`)的混合 repo:`settings.gradle` 不在 repo 根就不猜,照舊骨架;init 印一行提示要人手改 run_cmd。
- kill-log 多存 400 字輸出:帳本會變大一點;只在兩種弱證據判定時存,量少。輸出可能含路徑與測試名,不含祕密(殺傷力只跑專案自己的測試)。
- 新舊版本混用:臨時配方多 `also` 只在同一次執行內傳,不落帳;kill-log 的 `tail` 欄本來就有,舊版讀新帳不受影響。
- 已排除:金流:不碰付款與金額。
- 已排除:對外送出:只在本機隔離工作樹改檔跑測試、寫本機帳。
- 已排除:不可逆:寫回的條款與帳本行為不變;連帶替換只發生在隔離工作樹、跑完整支檔還原。

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| Android 跑單支單元測試要用變體任務加 --tests | 頂層 test 不收 --tests,要 :app:testDebugUnitTest | https://kaweah.freedombox.rocks/kiwix/stackoverflow.com_en_all_2023-11/questions/51823185/how-to-run-single-test-class-in-android-using-gradle-command |
| Android 跑單支單元測試要用變體任務加 --tests | Gradle 測試過濾 --tests 是測試任務的選項 | https://docs.gradle.org/current/userguide/java_testing.html |
| 連帶加 import、舊的不刪 | 沒用到的 import 只是 IDE 檢查,編譯器不報 | https://jetbrains.com/help/inspectopedia/KotlinUnusedImport.html |
| 連帶加 import、舊的不刪 | Kotlin 維護者:編譯器沒有也不打算有這個警告 | https://slack-chats.kotlinlang.org/t/452679/i-see-that-kotlin-compiler-doesn-t-issue-a-warning-for-unuse |
| 缺口來源 | 2026-11-13 真實 Gradle 專案實跑 | [[Issues/人裁殺傷力在真實Android專案跑不動的四個缺口]] |
| 先做 A 再做 B | 使用者對話裁定 | 使用者 2026-11-13:「好,先做 A,再做 B」 |

## 驗收條款

- [S1] 當被推版本的檔頭逐一 import 了舊寫法的觸發字,人裁的殺傷力壞法 應 連帶在那一行下面加上同一套件新寫法觸發字的 import [test:t_situation_rule_import_companion]
- [S2] 當檔頭是整包 import 或沒有 import 舊寫法的觸發字,人裁的殺傷力壞法 應 不產生連帶替換 [test:t_situation_rule_import_companion_none]
- [S3] 當臨時配方的連帶替換不是只多一行 import,殺傷力驗證 應 判 error 而且不套用壞法、不跑壞法那一次 [test:t_guard_kill_also_rejects_non_import]
- [S4] 當筆記宣告的配方帶了 also 欄位,殺傷力驗證 應 不理會那個欄位 [test:t_guard_kill_also_only_override]
- [S5] 當 repo 恰好有一個 Android application 模組,lumos init 應 給那個模組的 testDebugUnitTest 跑單支測試指令 [test:t_init_android_run_cmd]
- [S6] 當預設平台的 profile 是 kotlin-junit 或 java-junit、run_cmd 用頂層 test 帶 --tests 而算得出 Android application 模組,人裁指令 應 在跑殺傷力之前拒絕並印出正確寫法 [test:t_situation_rule_android_run_cmd_check]
- [S7] 當人裁帶 --diff 而算不出主線分岔點,人裁指令 應 用那個範圍算情境段 [test:t_situation_rule_diff_flag]
- [S8] 當殺傷力判定是 killed_unattributed 或 timed_out_weak,殺傷力帳本 應 存下壞法那次的輸出摘錄 [test:t_kill_log_tail_on_weak]
- [S9] 當在真實 Android 專案以逐一 import 的檔跑人裁(flatMapLatest 換 flatMapConcat、綁連送兩次值的測試),人裁指令 應 判 killed 並寫回條款 [manual:測試品質實驗室 Android 副本,SearchViewModel 改回逐一 import 後跑 lumos situation-rule,看判定是 killed、計劃多一條]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 檔頭 `import kotlinx.coroutines.flow.flatMapLatest`,`--old` 含 flatMapLatest、`--new` 含 flatMapConcat | 臨時配方帶一筆 also:那一行換成原行加 `import kotlinx.coroutines.flow.flatMapConcat` | 〈範圍〉1;2026-11-13 實跑缺口 |
| S1 | 同上,檔頭另外已有 `import kotlinx.coroutines.flow.flatMapConcat` | 不產生 also | 〈範圍〉1 已有就不加 |
| S2 | 檔頭 `import kotlinx.coroutines.flow.*` | 不產生 also | 〈範圍〉1 整包 import |
| S2 | 檔頭沒有 import flatMapLatest(全名呼叫) | 不產生 also | 〈範圍〉1 舊觸發字沒被 import 就不連帶 |
| S3 | also 的 new 多兩行、或 old 不是 import 行 | 判 error、檔不動、不跑測試 | 〈範圍〉2;〈實務隱患〉只改這一段 |
| S4 | 筆記配方帶 also,guard kill 正常呼叫 | also 不套用,結果跟沒帶一樣 | 〈範圍〉2 只有臨時配方認 |
| S5 | `settings.gradle.kts` 有 `include(":app")`,`app/build.gradle.kts` 套用 com.android.application | run_cmd 是 `./gradlew :app:testDebugUnitTest --tests '*{method}'` | 〈範圍〉3;Gradle 與 Stack Overflow |
| S5 | 同上但 `app/build.gradle.kts` 寫 `alias(libs.plugins.android.application)` | 同上(認得 version catalog 別名) | 〈用詞〉Android application 模組含別名寫法 |
| S5 | `settings.gradle.kts` include 兩個 application 模組 | 不猜,照舊 `./gradlew test --tests '*{method}'` | 〈範圍〉3 多個就不猜 |
| S5 | 沒有 Android 模組的 Kotlin 專案 | run_cmd 照舊 `./gradlew test --tests '*{method}'` | 〈範圍〉3 沒有 Android 模組照舊骨架 |
| S6 | 多平台設定平台鍵 `kotlin`(profile kotlin-junit)、run_cmd `./gradlew test --tests '*{method}'`、有 `:app` application 模組 | rc 2、殺傷力不跑、印 `:app:testDebugUnitTest` 寫法 | 〈範圍〉4 看 profile 名不看平台鍵 |
| S6 | 同上但算不出 application 模組(只有 library) | 不擋,照舊跑殺傷力 | 〈範圍〉4 算不出模組就不擋 |
| S7 | 沒有主線分岔點的 repo,帶 `--diff main..HEAD` | 用那個範圍算出情境段,不印算不出範圍 | 〈範圍〉5;2026-11-13 實跑缺口 |
| S7 | 分支找得到主線分岔點,另帶 `--diff` 指一個不同範圍 | 照分岔點算(跟 code-loop check 同規則),`--diff` 不生效 | 〈範圍〉5 同 _codeloop_disp_range |
| S8 | 壞法編譯失敗、判 killed_unattributed | kill-log 那筆 tail 是壞法那次輸出最後 400 字(含編譯錯誤);result_out 那列帶同一段 tail;人裁拒絕訊息印最後 5 行 | 〈範圍〉6;2026-11-13 實跑缺口 |
| S9 | 實驗副本逐一 import、綁 onlyLatestQueryShown | killed、計劃多一條條款 | 〈範圍〉1 端到端 |

## 回退

還原這次的提交即可:連帶替換只在隔離工作樹裡發生、跑完還原;init 只影響之後新產生的骨架;kill-log 多存的 tail 欄位舊版照讀。

## 天花板

1. 連帶替換只認逐一 import 的同套件兄弟函式;別名 import、擴充函式從別處引入、Java 檔都不處理,遇到可能照舊判弱證據(有摘錄可看)。
2. 原始碼層壞法只換文字;簽名不同的兄弟寫法(參數不同)換了會編譯失敗,這一版不處理,留給位元碼層的雙向追溯計劃。
3. Android application 模組偵測只認外掛 id 與 `alias(libs.plugins.<名>)` 這兩種寫法;用自訂約定外掛(build-logic 的 convention plugin)套 Android 外掛的專案偵測不到,照舊骨架、要人手改。
