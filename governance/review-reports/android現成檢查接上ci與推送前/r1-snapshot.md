---
type: project
status: todo
created: 2026-11-06
updated: 2026-11-06
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
related:
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Projects/Android的detekt推送前真的擋_計劃]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/lint-declaration-health]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/linter精選目錄
  - Systems/lint-declaration-health
  - Systems/kotlin規則包
---
# Android現成檢查接上CI與推送前_計劃

> 白話:Android 寫法型錄 473 列裡,有 176 列只靠現成工具接電(第四批),其中 detekt 已在 [[Projects/Android的detekt推送前真的擋_計劃]] 接好;剩下最大的兩塊是 Android Lint(含 androidx 函式庫附帶的檢查,型錄約 100 列提到)與兩套 Compose 規則(Slack compose-lints 22 列、mrmans0n compose-rules 29 列)。這案把它們接上:compose-rules 是 detekt 外掛、不用型別資訊,推送前跟著 detekt 一起擋;Android Lint 與 Slack compose-lints 官方只支援用 Gradle 整個模組跑,放在消費專案的 CI 用基準線擋新增。lumos 這邊給範本,健檢在專案是 Android 卻沒接時說實話。

PRIOR-ART: ①Android Lint 怎麼跑:官方文件寫明 Gradle 專案「一律用 `./gradlew lint`」,單機版 lint 對 Gradle 專案會報錯;變體任務是 `lint<變體>`;只擋新增用 `lint { baseline = file("lint-baseline.xml") }`,官方並寫「強烈建議把 lint 明確放進 CI」(https://developer.android.com/studio/write/lint )。DSL 的 `warningsAsErrors`、`checkDependencies`、`sarifReport` 語意照官方參考頁(https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint )。採用:CI 跑 `lint<變體>` 加基準線,不在推送前跑(要整個模組、要 Gradle 建置)。②Slack compose-lints:官方安裝法是 `lintChecks("com.slack.lint.compose:compose-lint-checks:<版本>")`,掛在 Android Lint 上跑(https://slackhq.github.io/compose-lints/ );1.6.x 要 AGP/lint 9.3 以上(GitHub 1.6.0 發行說明)。採用,跟 Android Lint 同一步。③compose-rules:官方 detekt 頁寫 CLI 用 `-p detekt-compose-<版本>-all.jar`,版本表 0.4.23 起對 detekt 1.23.8、0.5.0 起對 detekt 2.x(https://mrmans0n.github.io/compose-rules/detekt/ );2026-11-06 用本機 detekt 1.23.8 加 0.4.28 外掛、只給 `--input` 實跑壞例,`RememberMissing`、`MutableParams`、`MutableStateAutoboxing`、`ComposableNaming` 都報、SARIF 有 `detekt.Compose.*` 規則碼,不用型別資訊。採用:推送前 detekt 宣告加外掛。同次實跑 detekt 內建 `FunctionNaming` 把大寫開頭的 `@Composable` 報成命名錯,compose-rules 官方建議對 `Composable` 註解忽略,共用設定照做。不選:④santimattius structured-coroutines(型錄 26 列)只有 0.1.0、規則清單與版本還沒核對,留待查證;Sonar(7 列)要伺服器,IntelliJ 檢查(4 列)只在 IDE 跑,都不接。
RETIRE-IF: 連續三個月沒有任何消費專案照範本接 Android Lint 或 compose-rules(健檢那兩則提醒拆掉、範本留在目錄當參考);或 compose-rules 的 detekt 外掛在推送前誤報超過命中的一成(照型錄規則包同一條 Tricorder 門檻,改回只在 CI 跑)。

## 用詞

- **Android Lint**:隨 Android Gradle 外掛(AGP)附的檢查工具;androidx 函式庫(lifecycle、compose、fragment 等)會隨依賴帶自己的 lint 檢查進來,一起跑。
- **Slack compose-lints**:Slack 出的 Compose 檢查,是 Android Lint 的外掛,掛在 `lintChecks` 依賴上。
- **compose-rules**:mrmans0n 出的 Compose 檢查,有 detekt 外掛版(單一 jar),不用型別資訊。
- **基準線**:Android Lint 的 `lint-baseline.xml`,記下現有告警,之後只報新增的。
- **Android 專案**:專案根目錄與下一層的 Gradle 建置檔(`build.gradle`、`build.gradle.kts`、`settings.gradle(.kts)`)或 `gradle/libs.versions.toml` 裡,出現 Android 應用或函式庫外掛字樣(`com.android.application`、`com.android.library`,或版本目錄的外掛別名:`android.application`、`android-application`、`android.library`、`android-library`,也就是 `android` 接一個 `.` 或 `-` 再接 `application` 或 `library`)。
- **用 Compose 的專案**:同一批檔裡出現 `compose = true`、`org.jetbrains.kotlin.plugin.compose`、`kotlin-compose` 或 `androidx.compose` 字樣。

## 範圍

1. **CI 範本**([[Systems/linter精選目錄]] 加〈Android Lint 與 Compose lint 標準接法〉一節,跟 detekt 的 CI 型別檢查範本並列):模組層 `android { lint { baseline = file("lint-baseline.xml"); warningsAsErrors = true; checkDependencies = true; sarifReport = true } }`、`dependencies { lintChecks("com.slack.lint.compose:compose-lint-checks:1.6.1") }`(註明 1.6.x 要 AGP 9.3 以上,舊 AGP 照發行說明挑對得上的版本);第一次本機跑 `./gradlew lint<變體> -Dlint.baselines.continue=true` 產基準線並提交;CI 加一步 `./gradlew lint<變體>`。`warningsAsErrors` 的理由寫明:不開時只有 error 級會讓建置失敗,型錄 Android Lint 列多半是 warning 級。detekt 的 CI 範本(`detekt<變體>`)那段加 `detektPlugins("io.nlopez.compose.rules:detekt:0.4.28")`,讓 CI 那步也帶 compose-rules。
2. **推送前 detekt 宣告加 compose-rules**:linter 目錄的 detekt 標準接法加一條帶外掛的寫法 `--plugins $HOME/.local/share/lumos/detekt-plugins/detekt-compose-0.4.28-all.jar`(本機目錄,新增慣例、不進 repo),外掛下載指令釘版本與 sha256(`b8c732880e9d26fac90f44733ecd9dab099e2abb1f597b76ceab29e676d4ddd6`,2026-11-06 自算;官方沒公布雜湊)、放在不會被系統清掉的位置(承接 detekt jar 放 `/tmp` 被清兩次的前科);外掛檔不在時 detekt 整條失敗、新增告警閘照既有規則判環境不可用(閘的既有行為,不改)。共用設定 `configs/detekt/android.yml` 加 `Compose: active: true` 不必要(外掛規則預設開),只加 `naming: FunctionNaming: ignoreAnnotated: ['Composable']`,理由寫在檔內註解。本 repo 的 CI(`.github/workflows/ci.yml` 裝 detekt 那一步)照 detekt 的做法多下載 compose-rules 0.4.28 外掛並比對同一個 sha256,讓 S3 在 CI 必跑。
3. **健檢提醒**(lint-check 與健檢 F 段;跟 detekt 的 T4 一樣只看字面、不執行、不改退出碼,但不放進 detekt 那支函式與「detekt 宣告實際會怎樣」標題底下——新函式 `_lint_android_ci_advisories(config, repo_root)`(新增)自帶代號與文字表,lint-check 的文字與 `--json` 的 `advisories` 清單接在 detekt 提醒之後、另起標題「Android 現成檢查有沒有接上」,健檢 F 段另起一則同標題的提醒;T4 要求宣告裡有 detekt 命令,A1、A2 不要求):宣告裡有 `kt` 棧而且是 Android 專案時——
   - **A1**:`.github/workflows/` 底下的 `.yml`/`.yaml` 沒有任何 Android Lint 檢查任務字樣(任務名剛好是 `lint`,或 `lint` 接大寫開頭的變體名,前面是 `gradlew` 或 `:模組:`;變體名以 `Fix`、`Vital`、`Analyze`、`Report` 開頭的,以及 `updateLintBaseline`,不算——`lintFix` 會改檔、`lintVital<變體>` 只看 fatal 級、`lintAnalyze<變體>` 與 `lintReport<變體>` 是 lint 任務的中間步驟、`updateLintBaseline` 只產基準線)→ 印「Android Lint 與 Slack compose-lints 哪裡都沒擋」並指向範本。
   - **A2**:用 Compose 的專案,建置檔沒有 `compose-lint-checks` 也沒有 `io.nlopez.compose.rules`,而且宣告的 kt 命令都沒帶 `detekt-compose` 字樣(不看版本) → 印「Compose 規則哪裡都沒接」並指向範本。
   掃的檔:專案根目錄與下一層資料夾的上述建置檔與 `gradle/libs.versions.toml`,每支最多讀 1 MB(超過只讀前 1 MB)、依路徑排序後最多看 200 支,`build/`、`.gradle/`、隱藏資料夾不進;讀不了的當沒有。workflow 檔沿用 T4 的讀法(不設上限,同 `_detekt_ci_has_typed_task`)。
4. **型錄通電批次**(`skills/kotlin-idioms/checks-catalog.md`):現成規則欄點名了 Android Lint、androidx、Slack 規則碼(不是「待查」)的列,通電批次從「批四(現成規則)」改成「批四(CI 範本:Android Lint)」;點名 compose-rules 規則碼的列改成「批四(推送前:detekt 外掛 compose-rules)」;兩者都有寫兩個;型錄〈輸入與口徑〉通電批次那一條的值清單同步加這兩個字樣。只寫待查、Sonar、IntelliJ、structured-coroutines 的列不動。改由一次性腳本依欄位內容判,不手改;腳本不進 repo,判定口徑寫進型錄〈輸入與口徑〉的通電批次那一條。

**不做**:不在推送前跑 Android Lint 或 Slack compose-lints;不替消費專案改 Gradle 檔;不接 Sonar、IntelliJ 檢查;structured-coroutines 留在待查證;不改新增告警閘本身的判定。

## 實務隱患

- **warningsAsErrors 讓舊專案一接就紅**:基準線先產再開;範本步驟順序寫死「先產基準線、提交,再加 CI 步驟」。
- **基準線過期**:改掉舊告警後基準線留著已修的項目,官方會印資訊級提醒;範本寫要清舊帳時刪檔重產。
- **AGP 版本與 Slack 外掛不合**:1.6.x 要 AGP 9.3+;範本寫明挑版本的規則,不合時 lint 任務會載不進外掛(官方行為,lumos 判不到)。
- **compose-rules 外掛版本綁 detekt**:0.4.x 對 detekt 1.23.x、0.5 起對 2.x;本機 detekt 升 2.0 時外掛要一起換,範本寫在同一段。外掛檔不在時新增告警閘判環境不可用自動放行並記帳,健檢的自動放行計數看得到。
- **FunctionNaming 改設定的影響**:只對 `@Composable` 註解的函式忽略命名規則,其他函式照舊;compose-rules 自己的 `ComposableNaming` 接手檢查 Composable 命名。
- **健檢字面判斷誤判**:workflow 裡用別的寫法呼叫(包在 shell 腳本、用 composite action)會判成沒接而多印提醒;只是提醒、不擋,這是只看字面的代價(跟 T4 同形)。
- **掃建置檔的成本**:只掃兩層、有檔數與大小上限,健檢與 lint-check 都在手動或推送前閘外的路徑上。
- **舊否決對照**(2026-11-06 跑 `lumos rejections`,453 行,按概念比對):[[Projects/Macrobenchmark退步提醒_計劃]] 決定「Lumos 只讀結果檔,不負責建置或執行」(要 Gradle、跨專案設定各異、以分鐘計);本案同向——Android Lint 不在推送前由 lumos 跑,交消費專案 CI,lumos 只給範本與看 workflow 字面。沒有撞到否決。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:健檢只讀本機檔,不連網;範本的下載指令由人照抄執行
- 已排除:不可逆:新增提醒與文件,退提交即回原狀
- 守衛面:共用 detekt 設定對 `@Composable` 函式關掉 `FunctionNaming`,推送前閘對這類函式少擋一條命名規則(放寬);改由 compose-rules 的 `ComposableNaming` 接手,走完整設計審
- 資安:範本的外掛下載釘 sha256,下載後比對不符就不要用;lumos 不自動下載或執行任何東西

## 驗收條款

- [S1] 當宣告有 kt 棧、專案根目錄的 `build.gradle.kts` 有 `id("com.android.application")`、`.github/workflows/` 沒有 Android Lint 任務時,`lumos lint-check` 與健檢 F 段 應 印 A1;workflow 有 `./gradlew lintDebug` 或 `./gradlew :app:lint` 應 不印;只有 `lintFix`、`lintVitalRelease`、`lintAnalyzeDebug`、`updateLintBaseline` 應 照印;Android 外掛字樣只寫在 `gradle/libs.versions.toml` 的 `android-application` 應 認成 Android 專案;不是 Android 專案(只有 `org.jetbrains.kotlin.jvm`)應 不印 A1 與 A2;宣告沒有 kt 棧 應 不印;lint-check 的退出碼 應 不因 A1、A2 改變 [test:t_lint_android_ci_advice]
- [S2] 當 Android 專案的建置檔有 `compose = true` 而沒有 `compose-lint-checks`、`io.nlopez.compose.rules`,宣告的 kt 命令也沒帶 `detekt-compose` 時 應 印 A2;建置檔有其中一個字樣 應 不印;宣告的 detekt 命令帶 `--plugins …detekt-compose-0.4.28-all.jar` 應 不印;帶 `detekt-compose-0.5.0-all.jar` 應 一樣不印;第 201 支(依路徑排序)以後的建置檔才有 Compose 字樣時 應 不算用 Compose;不用 Compose 的專案 應 不印;`build/` 底下的建置檔 應 不算 [test:t_lint_android_ci_advice]
- [S3] 當共用設定 `configs/detekt/android.yml` 給 detekt 1.23.8 加 compose-rules 0.4.28 外掛跑 `@Composable fun Header()` 時,detekt 應 不報 `FunctionNaming`;一般函式 `fun Header()` 應 照報;`@Composable` 函式裡沒包 remember 的 `mutableStateOf` 應 報 `RememberMissing`(本機沒有 detekt 或外掛時跳過並印原因,CI 必跑) [test:t_detekt_compose_rules_shared_config]
- [S4] 當型錄自檢跑過時,現成規則欄點名 Android Lint、androidx 或 Slack 規則碼的列 應 通電批次含「CI 範本:Android Lint」;點名 compose-rules 規則碼的列 應 含「推送前:detekt 外掛 compose-rules」;只寫待查的列 應 不含這兩個字樣 [test:t_kt_catalog_batch4_wiring]
- [S5] 當在一個真的 Android 專案(公開範例專案)照範本加 Android Lint、Slack compose-lints 與 compose-rules,產基準線後故意加一處 Compose 錯誤寫法時,`./gradlew lint<變體>` 與 `detekt<變體>` 應 失敗並點名那一處;耗時記進驗證紀錄 [manual:在暫存區複本實跑一次範本的每一步,記下任務名、耗時與報出的規則碼]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | kt 宣告、根 `build.gradle.kts` 有 `com.android.application`、沒有 workflow | 印 A1 | 官方 lint 頁:Gradle 專案用 `./gradlew lint`、建議放進 CI(https://developer.android.com/studio/write/lint ) |
| S1 | 同上,workflow 有 `./gradlew lintDebug` | 不印 A1 | 同上:變體任務是 `lint<變體>` |
| S1 | 同上,workflow 只有 `./gradlew lintVitalRelease` | 印 A1 | AGP DSL 參考頁:release 建置只檢查 fatal 級(`checkReleaseBuilds`) |
| S1 | 只有 `org.jetbrains.kotlin.jvm` 外掛 | 不印 A1、A2 | 本計劃〈用詞〉Android 專案的定義 |
| S2 | Android 專案有 `compose = true`、沒有任一 Compose 規則字樣 | 印 A2 | 本計劃〈用詞〉用 Compose 的專案的定義 |
| S2 | 宣告 detekt 命令帶 `--plugins …detekt-compose-0.4.28-all.jar` | 不印 A2 | compose-rules 官方 detekt 頁的 CLI 用法 |
| S3 | `@Composable fun Header()` 經共用設定加外掛 | 不報 `FunctionNaming` | compose-rules 官方建議對 `Composable` 註解忽略 `FunctionNaming`;2026-11-06 實跑:不加設定時會報 |
| S3 | `@Composable` 裡 `val s = mutableStateOf(0)` | 報 `RememberMissing` | 2026-11-06 本機 detekt 1.23.8 加外掛 0.4.28 實跑輸出 |
| S5 | 範例專案照範本接好、產基準線後加一處沒包 remember 的 `mutableStateOf` | `lint<變體>` 與 `detekt<變體>` 失敗並點名那一處 | 官方 lint 頁:基準線之後只報新增;compose-rules 規則頁 RememberMissing |
| S4 | 現成規則欄寫 `slack:ComposeItemKeyHashCode` 的列 | 通電批次含「CI 範本:Android Lint」 | 本計劃範圍 4 |

## 回退

退回本案的提交:A1、A2 提醒不再印;共用設定的 `FunctionNaming` 忽略註解拿掉後,大寫開頭的 Composable 會被報命名錯(推送前新增告警閘只擋新增的);型錄通電批次字樣回到「批四(現成規則)」。消費專案已照範本加的 Gradle 設定與 detekt 外掛宣告不受影響。

## 天花板

1. Android Lint 與 Slack compose-lints 只在 CI 擋,推送前不擋;AI 寫完到 CI 跑完之間的空窗,只有規則包與 detekt(含 compose-rules)守。
2. 健檢只看 workflow 字面,不驗 CI 真的跑、跑的是哪個模組;多模組專案只對 `:app:lint` 有字樣也算接上。
3. structured-coroutines 26 列、Sonar 7 列、IntelliJ 4 列仍沒有機械守衛,只靠告警訊息與代碼審。

## 審計修正紀錄
