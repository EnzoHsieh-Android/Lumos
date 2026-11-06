---
type: project
status: doing
created: 2026-11-06
updated: 2026-11-06
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
related:
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Projects/Android的detekt推送前真的擋_計劃]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/lint-declaration-health]]"
  - "[[Systems/kotlin規則包]]"
  - "[[Systems/bound-tests-gate]]"
lands_in:
  - Systems/linter精選目錄
  - Systems/lint-declaration-health
  - Systems/kotlin規則包
  - Systems/bound-tests-gate
---
# Android現成檢查接上CI與推送前_計劃

> 白話:Android 寫法型錄 473 列裡,有 176 列只靠現成工具接電(第四批),其中 detekt 已在 [[Projects/Android的detekt推送前真的擋_計劃]] 接好;剩下最大的兩塊是 Android Lint(含 androidx 函式庫附帶的檢查,型錄約 100 列提到)與兩套 Compose 規則(Slack compose-lints 22 列、mrmans0n compose-rules 29 列)。這案把它們接上:compose-rules 是 detekt 外掛、不用型別資訊,推送前另一條 detekt 宣告跑它;Android Lint 與 Slack compose-lints 官方只支援用 Gradle 整個模組跑,放在消費專案的 CI 用基準線擋新增。順手修一個既有的誤報:共用 detekt 設定對標準寫法的 Compose 檔會報 6 條(元件大寫命名、`@Preview` 沒被呼叫、參數多、頂層常數命名、顏色常數),照 detekt 官方 Compose 頁的建議調。lumos 這邊給範本,健檢在專案是 Android 卻沒接時說實話。

PRIOR-ART: ①Android Lint 怎麼跑:官方文件寫明 Gradle 專案「一律用 `./gradlew lint`」,單機版 lint 對 Gradle 專案會報錯;變體任務是 `lint<變體>`;只擋新增用 `lint { baseline = file("lint-baseline.xml") }`,官方並寫「強烈建議把 lint 明確放進 CI」(https://developer.android.com/studio/write/lint )。DSL 的 `warningsAsErrors`、`checkDependencies`、`sarifReport` 語意照官方參考頁(https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint )。採用:CI 跑 `lint<變體>` 加基準線,不在推送前跑(要整個模組、要 Gradle 建置)。②Slack compose-lints:官方安裝法是 `lintChecks("com.slack.lint.compose:compose-lint-checks:<版本>")`,掛在 Android Lint 上(https://slackhq.github.io/compose-lints/ );版本要對 AGP:lint 的版本號是 AGP 版本加 23(lint 31.x 對 AGP 8.x、32.x 對 AGP 9.x),GitHub 發行說明寫 1.6.0「requires AGP/lint 9.3+」、1.6.1 用 lint 32.4.1 建、1.4.2 用 lint 31.7.1 建(https://github.com/slackhq/compose-lints/releases )。採用,跟 Android Lint 同一步。③compose-rules:官方 detekt 頁寫 CLI 用 `-p detekt-compose-<版本>-all.jar`,版本表 0.4.23 起對 detekt 1.23.8、0.5.0 起對 detekt 2.x(https://mrmans0n.github.io/compose-rules/detekt/ );外掛自帶設定裡 `Material2`、`PreviewNaming`、`UnstableCollections` 三條預設關。2026-11-06 用本機 detekt 1.23.8 加 0.4.28 外掛、只給 `--input` 實跑壞例,`RememberMissing`、`MutableParams`、`MutableStateAutoboxing`、`ComposableNaming` 都報、SARIF 有 `detekt.Compose.*` 規則碼,不用型別資訊;`--plugins` 指不存在的 jar 時 detekt rc 1、不產 SARIF。採用:推送前另開一條 detekt 宣告只跑外掛規則(`--disable-default-rulesets`),外掛缺檔時只有這條被判環境不可用,原本那條 detekt 照擋。④Compose 專案的 detekt 設定:detekt 官方 Compose 頁(https://detekt.dev/docs/introduction/compose/ )建議六項——`FunctionNaming` 對 `Composable` 忽略、`TopLevelPropertyNaming` 常數允許 PascalCase、`LongParameterList` 忽略有預設值的參數、`MagicNumber` 忽略屬性宣告、未使用私有函式對 `Preview` 忽略(1.23 版規則名是 `UnusedPrivateMember`)、`TooManyFunctions` 不算 `Preview`;compose-rules 規則頁也寫「Be sure to set Detekt's ignoreAnnotated configuration to ['Preview']」(https://mrmans0n.github.io/compose-rules/rules/ )。2026-11-06 實跑:現行共用設定對一支標準 Compose 檔報 `FunctionNaming`、`LongParameterList`、`MagicNumber`、`TopLevelPropertyNaming`、`UnusedPrivateMember` 共 6 條,加上六項後只剩一般函式 `fun Other()` 的 `FunctionNaming`。採用,寫進共用設定。不選:⑤santimattius structured-coroutines(型錄 26 列)只有 0.1.0、規則清單與版本還沒核對,留待查證;Sonar(7 列)要伺服器,IntelliJ 檢查(4 列)只在 IDE 跑,都不接。⑥外掛 jar 放哪:沒有套件管理器的配方(brew、sdkman 都沒有),二進位檔不進 repo;放本機固定目錄 `$HOME/.local/share/lumos/detekt-plugins/`、下載指令釘版本與 sha256,是 [[Systems/linter精選目錄]]「外部工具一律裝進套件管理器」的例外,理由寫進那一條。
RETIRE-IF: 連續三個月沒有任何消費專案照範本接 Android Lint 或 compose-rules(健檢那幾則提醒拆掉、範本留在目錄當參考);或 compose-rules 那條推送前宣告的誤報超過命中的一成(照型錄規則包同一條 Tricorder 門檻,改回只在 CI 跑)。

## 用詞

- **Android Lint**:隨 Android Gradle 外掛(AGP)附的檢查工具;androidx 函式庫(lifecycle、compose、fragment 等)會隨依賴帶自己的 lint 檢查進來,一起跑。
- **Slack compose-lints**:Slack 出的 Compose 檢查,是 Android Lint 的外掛,掛在 `lintChecks` 依賴上。
- **compose-rules**:mrmans0n 出的 Compose 檢查,有 detekt 外掛版(單一 jar),不用型別資訊。
- **基準線**:Android Lint 的 `lint-baseline.xml`,記下現有告警,之後只報新增的。
- **Android 專案**:沿用 lumos 既有的 Kotlin 建置檔判法——`_KT_BUILD_FILES` 那幾種建置檔裡 `_KT_BUILD_ANDROID` 比得到(`com.android.`、`libs.plugins.android`、行首 `android {`);本案多看 `settings.gradle(.kts)` 與 `gradle/libs.versions.toml`,同一支正規式。
- **用 Compose 的專案**:同一批檔裡出現 `compose = true`、`org.jetbrains.kotlin.plugin.compose`、`kotlin-compose` 或 `androidx.compose` 字樣。
- **CI 設定檔**:`.github/workflows/` 底下的 `.yml`/`.yaml`,加上 `.gitlab-ci.yml`、`bitrise.yml`、`.circleci/config.yml`、`Jenkinsfile`、`azure-pipelines.yml`。

## 範圍

1. **CI 範本**([[Systems/linter精選目錄]] 加〈Android Lint 與 Compose lint 標準接法〉一節,跟 detekt 的 CI 型別檢查範本並列):
   - 模組層 `android { lint { baseline = file("lint-baseline.xml"); warningsAsErrors = true; checkDependencies = true; sarifReport = true } }`。`warningsAsErrors` 的理由寫明:不開時只有 error 級會讓建置失敗,型錄 Android Lint 列多半是 warning 級。
   - `dependencies { lintChecks("com.slack.lint.compose:compose-lint-checks:<版本>") }`,版本挑法:Slack 外掛建置用的 lint 版本不高於專案的 lint 版本,而 lint 版本 = AGP 版本加 23(1.5.5 的發行說明同時寫「lint 32.3.2」與「AGP lint plugin 9.3.2」)。依各版發行說明的常見對照:AGP 9.4.1 以上用 1.6.1(lint 32.4.1);AGP 9.3.2 到 9.4.0 用 1.5.5(lint 32.3.2);AGP 9.2.1 到 9.3.1 用 1.5.0(lint 32.2.1);AGP 8.7.1 到 9.2.0 用 1.4.2(lint 31.7.1);AGP 8.7.0 用 1.4.0(Build against Lint 8.7.0,即 lint 31.7.0);更舊的照發行說明挑;表寫在範本裡、附發行說明網址。表只是常見對照,邊界一律照「建置用 lint 版本不高於專案 lint(= AGP 加 23)」挑;1.4.3 的發行說明沒寫建置用 lint 版本,只列一串依賴更新的 PR 標題(lint-api 從 31.7.2 一路升到 32.2.0、lint 外掛升到 9.2.0,另一則寫 lint 31.13.2),看不出最後用哪版建置,不列。
   - 第一次本機跑 `./gradlew lint<變體> -Dlint.baselines.continue=true` 產基準線並提交;之後 CI 加一步 `./gradlew lint<變體>`。步驟順序寫死「先產基準線、提交,再加 CI 步驟」。
   - detekt 的 CI 範本(`detekt<變體>`)那段加 `detektPlugins("io.nlopez.compose.rules:detekt:0.4.28")`,讓 CI 那步也帶 compose-rules。
2. **推送前 compose-rules 與共用設定**:
   - linter 目錄的 detekt 標準接法加第二條宣告,只跑外掛規則:`detekt --input {LINT_FILES_CSV} --disable-default-rulesets --plugins $HOME/.local/share/lumos/detekt-plugins/detekt-compose-0.4.28-all.jar --build-upon-default-config --config $HOME/harness/lumos-toolchain/configs/detekt/compose.yml --report sarif:{LINT_SARIF_OUT}`(`--build-upon-default-config` 不能少,見審計修正紀錄的實作更正);原本那條不動。外掛下載指令釘版本與 sha256(`b8c732880e9d26fac90f44733ecd9dab099e2abb1f597b76ceab29e676d4ddd6`,2026-11-06 自算;官方沒公布雜湊),放本機固定目錄(理由見 PRIOR-ART ⑥,linter 目錄「一律裝進套件管理器」那一條補上這個例外)。外掛缺檔時只有這條被新增告警閘判環境不可用(閘的既有行為),原本那條照擋。
   - 新增 `configs/detekt/compose.yml`(新增):只寫 compose-rules 三條預設關規則要不要開——`UnstableCollections`、`PreviewNaming`、`Material2` 照外掛預設不開,檔內註解寫原因(外掛作者標成選用);其餘外掛規則用外掛預設。
   - 共用設定 `configs/detekt/android.yml` 加 PRIOR-ART ④ 的六項(1.23 版規則名),檔頭用法註解與 linter 目錄「共用設定開的五條」那句一起改寫。
   - 本 repo 的 CI(`.github/workflows/ci.yml` 裝 detekt 那一步)照 detekt 的做法多下載 compose-rules 0.4.28 外掛、比對同一個 sha256,路徑放進環境變數 `LUMOS_DETEKT_COMPOSE_JAR`;S3 的測試用這個變數找外掛,沒設時找本機固定目錄;環境變數 `CI` 為真而找不到外掛時測試判紅,本機找不到才跳過並印原因。
3. **健檢提醒**(lint-check 與健檢 F 段;只看字面、不執行、不改退出碼):新函式 `_lint_android_ci_advisories(config, repo_root)`(新增)自帶代號與文字表;A1、A2 看整個專案、條目寫成 `[CI] A1:<一句>`,A3 看單條命令、寫成 `[kt 第 N 條] A3:<一句>`(同 detekt 逐條提醒,不回顯命令內容);lint-check 用新的印出函式另起標題「Android 現成檢查有沒有接上」,`--json` 的 `advisories` 清單接在 detekt 提醒之後;健檢 F 段另起一則同標題的提醒(套 20 條上限)。列 CI 設定檔用 `_ci_config_paths`(新增,T4 只看 GitHub 那幾支、讀原文;A1 看全部、經既有 `_ci_workflow_texts` 去註解,Jenkinsfile 在同一支裡照 Groovy 剝 `/* */` 與 `//`;解析真實路徑後不在 repo 根底下的略過,檔案或資料夾那層是連結都算,repo 內的連結照讀)。條件是宣告裡有 `kt` 棧而且是 Android 專案:
   - **A1**:**證據模型**——CI 設定檔裡找不到 Android Lint 的跡象才印「Android Lint 與 Slack compose-lints 可能沒有在 CI 跑」並指向範本;找到任何一個跡象就不印(照 OpenSSF Scorecard 官方檢查文件的做法:只找已知名字、承認自動偵測會漏,見〈依據來源〉)。CI 設定檔去 `#` 註解(Jenkinsfile 改剝 Groovy 的 `/* */` 與 `//`,字串裡的 `//` 不算),反斜線續行接成同一邏輯行,再以空白、引號、標點切詞(`/`、`.` 不切,路徑與 `-D` 屬性是一個詞)。跡象只有兩種:①任何一個詞是 lint 任務名(`lint`、`lint` 接大寫變體名、可帶 `:模組:` 前綴、Bitrise 的 `android-lint`;`lintKotlin`、`lintFix`、`lintVital` 開頭接結尾或大寫的不算;任何位置都算);②「gradle 任務列」裡有一個詞是 `check` 或 `build`;gradle 任務列是同一邏輯行裡有 gradle 呼叫詞(`gradlew`、`gradlew.bat`、`gradle`,可帶 `./` 這類路徑前綴;跟 detekt 判定共用一份詞表)的行,或三個已知會叫 gradle 跑任務的欄位的值——Azure Gradle 任務的 `tasks:`、gradle action 的 `arguments:`、Bitrise gradle-runner 的 `gradle_task:`(值寫同一行、引號、流式清單、區塊純量或縮排更深的清單都算;其他欄位不算,CircleCI 的 `command:` 是 run 步驟的通用欄位、也不算)(AGP 讓 `check` 依賴 `lint`;Gradle 的 `build` 依賴 `check`)。整檔有 gradle 字樣不算(`needs: build`、`stage: build` 跟 `cache: gradle` 湊在一起不是在跑 lint);建置檔的 `lint { }`、`lintOptions { }` 區塊與 `lint-baseline.xml` 不算(那是範本第 1、2 步的痕跡,做完這兩步還沒做第 3 步正是該提醒的狀態)。寫了字樣卻沒真的跑(`-x lint`、`echo gradlew build`)判成有跡象,寧可少印、不誤報。
   - **A2**:用 Compose 的專案,建置檔沒有 `compose-lint-checks` 也沒有 `io.nlopez.compose.rules`,而且宣告的 kt 命令都沒帶 `detekt-compose` 字樣(不看版本) → 印「Compose 規則哪裡都沒接」並指向範本。
   - **A3**:宣告的 kt 命令帶 `--plugins <路徑>`(走跟 detekt 判定共用的 `_detekt_walk_segments`,`sh -c` 包住也看得到;照 shell 規則展開環境變數與 `~`;相對路徑對 repo 根;含反引號、萬用字元或展開後還有 `$` 的判不了、不算)而那支檔不存在 → 這條命令印一則「外掛檔不在,推送前會被判環境不可用、自動放行」並指向下載指令。
   掃建置檔:專案根目錄往下最多三層,資料夾照既有 `_stack_scan_skip`(`build`、`.gradle`、`node_modules`、`Pods`、`vendor`、`target` 等)跳過、另不進隱藏資料夾、不跟符號連結進資料夾、不開一般檔以外的東西;Gradle 建置檔走既有 `_kt_strip_comments` 剝註解,`gradle/libs.versions.toml` 照 TOML 的 `#` 剝;依(層數、路徑)排序、根目錄先讀,最多 200 支、每支前 1 MB;讀不了的當沒有。
4. **型錄通電批次**(`skills/kotlin-idioms/checks-catalog.md`):現成規則欄以「;」「、」切段,某一段含 `androidx:`、`androidx.<套件>:`、`內建:`、`slack:`、`Android Lint:` 接大寫開頭的規則碼,而且那一段不含「待查」「預設關」「相近」「opt-in」的列,通電批次從「批四(現成規則)」改成「批四(CI 範本:Android Lint)」;某一段含 `cr:compose:<規則>`、不含上述四個字樣的列改成「批四(推送前:detekt 外掛 compose-rules)」;兩者都有寫成「批四(CI 範本:Android Lint;推送前:detekt 外掛 compose-rules)」。其他列不動。口徑寫在型錄自檢 `configs/ast-grep/kotlin-android/check.py` 的 `batch4_expected_tags`,`catalog_problems` 逐列比對(改壞一列或把不該標的列標上都會報);型錄〈輸入與口徑〉通電批次那一條寫同一份口徑原文,值清單同步加這三個字樣;S4 的測試呼叫型錄自檢、並用複本改壞驗它抓得到。
5. **跟著變假的句子**:`skills/kotlin-idioms/SKILL.md` 第 R16 條的 compose-rules 條數(寫 32 條,型錄口徑 29 列,改成指向型錄)、「加掛 compose-rules(detekt plugin jar)補 R16 整組」那句改成指向 linter 目錄的接法、開頭那條 `REVISIT:2027-05-01` 核對 compose-rules 與 Slack 規則名的回頭條件改寫成本案實跑的日期與還沒核對的部分。

**不做**:不在推送前跑 Android Lint 或 Slack compose-lints;不替消費專案改 Gradle 檔;不接 Sonar、IntelliJ 檢查;structured-coroutines 留在待查證;不改新增告警閘本身的判定;不開 compose-rules 預設關的三條。

## 實務隱患

- **warningsAsErrors 讓舊專案一接就紅**:基準線先產再開;範本步驟順序寫死。
- **基準線過期**:改掉舊告警後基準線留著已修的項目,官方會印資訊級提醒;範本寫要清舊帳時刪檔重產。
- **AGP 版本與 Slack 外掛不合**:範本給版本表;表外的 AGP(7.x 以下)寫「照發行說明挑 lint 版本不高於 AGP 加 23 的」,不合時 lint 任務會載不進外掛(官方行為,lumos 判不到)。
- **compose-rules 外掛版本綁 detekt**:0.4.x 對 detekt 1.23.x、0.5 起對 2.x;本機 detekt 升 2.0 時外掛要一起換,範本寫在同一段;不合時那一條宣告跑不起來、被自動放行並記帳,原本那條 detekt 不受影響,健檢的自動放行計數看得到。
- **共用設定放寬六項**:六項都只對 Compose 的慣用寫法放寬(`Composable`、`Preview` 註解、有預設值的參數、屬性宣告的數字、PascalCase 常數);非 Compose 專案受影響的只有後三項的一般寫法(有預設值的長參數清單、屬性宣告的魔術數字、PascalCase 頂層常數不再報)。改由 compose-rules 的 `ComposableNaming` 等規則接手 Composable 的檢查。
- **健檢字面判斷誤判**:任務包在 shell 腳本、用 composite action 或 GitLab `include:`、寫在 CI 設定檔以外的地方時找不到跡象而多印提醒;寫了 lint 字樣卻沒真的跑時找到跡象而少印。只是提醒、不擋,這是只找跡象的代價(T4 讀原文、A1 去註解,兩者口徑不同)。
- **掃建置檔的成本**:最多三層、200 支、每支 1 MB;健檢與 lint-check 都在手動或推送前閘外的路徑上。
- **打開陌生 repo 時的健檢**(代碼審 r2 資安席):A3 對對方 `lint.json` 的 `--plugins` 值照 shell 規則展開環境變數後只做「檔在不在」判斷,輸出只有固定文字與條號、不回顯路徑或展開值;建置檔與 CI 設定檔解析真實路徑後不在 repo 根底下的一律略過,檔案或資料夾那層是連結都算(代碼審 r3、r4 資安席:原本會跟著連結讀到 repo 外;內容只拿來比對字樣、不回顯,仍照縱深防禦收緊);repo 內的連結照讀(r4 通才席:一律略過會讓 T4 誤印)。
- **舊否決對照**(2026-11-06 跑 `lumos rejections`,453 行,按概念比對):[[Projects/Macrobenchmark退步提醒_計劃]] 決定「Lumos 只讀結果檔,不負責建置或執行」(要 Gradle、跨專案設定各異、以分鐘計);本案同向——Android Lint 不在推送前由 lumos 跑,交消費專案 CI,lumos 只給範本與看 CI 設定檔字面。沒有撞到否決。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:健檢只讀本機檔,不連網;範本的下載指令由人照抄執行
- 已排除:不可逆:新增提醒、設定與文件,退提交即回原狀
- 守衛面:共用 detekt 設定放寬六項(推送前閘對這些寫法少擋),新增一條推送前 detekt 宣告;走完整設計審
- 資安:外掛 jar 是每次推送前都會載入執行的程式;範本的下載指令釘 sha256,比對不符就不要用;lumos 不自動下載或執行任何東西(單人自用的威脅模型,比對是人工步驟)

## 驗收條款

- [S1] 當宣告有 kt 棧、專案根目錄的 `build.gradle.kts` 有 `id("com.android.application")`、沒有任何 CI 設定檔時,`lumos lint-check` 與健檢 F 段 應 印 A1;CI 設定檔有 `./gradlew lintDebug`、`./gradlew --no-daemon assembleDebug lintDebug`、`./gradlew :app:lint`、`./gradlew check`、`./gradlew --no-daemon build`、續行 `./gradlew \` 下一行 `check`、`with: arguments: lintDebug` 任一行 應 不印;只有 `lintKotlin`、`lintFix`、`lintVitalRelease`、`updateLintBaseline` 應 照印;workflow 只有 `needs: build`、`cache: gradle` 與 `./gradlew assembleDebug` 應 照印;`.gitlab-ci.yml` 只有 `stage: build` 與 `./gradlew assemble` 應 照印;沒有 CI 設定檔、只有 `app/lint-baseline.xml` 或建置檔的 `lint { }` 區塊 應 照印;Jenkinsfile 只在 `/* */` 裡寫 `./gradlew lint` 應 照印;`tasks: 'clean build test'`(Azure)、`with: arguments: build`(gradle action,`>`、`>-`、`|-` 區塊寫法也算)、`gradle_task: build`(Bitrise)任一種 應 不印;CircleCI `run:` 的 `command: npm run build`、`command: |` 裡的 `make build` 加 `./gradlew assembleDebug` 應 照印;`needs: build`、`stage: build`、`name: build`,以及已知欄位的值結束後別的欄位(含同一欄的兄弟鍵)底下的 `build` 應 照印;CI 設定檔或建置檔解析後落在 repo 外(檔案或資料夾連結)應 略過,指到 repo 內的連結 應 照讀;只在 `.gitlab-ci.yml` 寫 `./gradlew lintDebug` 應 不印;Android 外掛只寫成 `alias(libs.plugins.androidApplication)` 應 認成 Android 專案;Android 模組在第三層(`apps/android/app/build.gradle.kts`)應 認得;不是 Android 專案(只有 `org.jetbrains.kotlin.jvm`)應 不印 A1、A2、A3;宣告沒有 kt 棧 應 不印;建置檔有非 UTF-8 位元組時 應 照判不出錯;lint-check 的退出碼 應 不因 A1、A2、A3 改變;T4 應 照舊只看 `.github/workflows/` 裡的 `detekt<變體>`(`detektBaseline<變體>` 不算) [test:t_lint_android_ci_advice]
- [S2] 當 Android 專案的建置檔有 `compose = true` 而沒有 `compose-lint-checks`、`io.nlopez.compose.rules`,宣告的 kt 命令也沒帶 `detekt-compose` 時,健檢 應 印 A2;建置檔有其中一個字樣 應 不印;宣告的 detekt 命令帶 `--plugins …detekt-compose-0.4.28-all.jar` 或 `detekt-compose-0.5.0-all.jar` 應 不印;不用 Compose 的專案 應 不印;`build/` 底下的建置檔 應 不算;依路徑排序第 201 支以後才有 Compose 字樣 應 不算;宣告的 `--plugins` 指到不存在的檔時 應 印 A3,檔存在時 應 不印;外掛路徑寫成 `tools/{p,q}.jar` 這類大括號展開時 應 不印 A3 [test:t_lint_android_ci_advice]
- [S3] 當共用設定 `configs/detekt/android.yml` 給 detekt 1.23.8 跑一支標準 Compose 檔(大寫命名的 `@Composable`、七個有預設值參數的 `@Composable`、`@Preview` 私有函式、PascalCase 頂層常數、`val Brand = Color(0xFFEA6D7E)`)時,detekt 應 不報 `FunctionNaming`、`LongParameterList`、`UnusedPrivateMember`、`TopLevelPropertyNaming`、`MagicNumber`;一般函式 `fun Other()` 應 照報 `FunctionNaming`;compose-rules 那條宣告加 0.4.28 外掛跑 `@Composable` 裡沒包 remember 的 `mutableStateOf` 時 應 報 `RememberMissing`,而且 應 不報任何 detekt 內建規則;外掛路徑不存在時那條 應 不產 SARIF(本機沒有 detekt 或外掛時跳過並印原因;CI 找不到時判紅) [test:t_detekt_compose_rules_shared_config]
- [S4] 當照範圍 4 的口徑重算型錄時,每列的通電批次 應 跟型錄寫的一致;寫 `slack:ComposeItemKeyHashCode` 的列 應 含「CI 範本:Android Lint」;寫 `內建:TrustAllX509TrustManager` 的列 應 含「CI 範本:Android Lint」;寫 `cr:compose:unstable-collections`(opt-in)的列 應 不含「推送前:detekt 外掛 compose-rules」;寫「WrongThreadInterprocedural(預設關)」的列 應 不含「CI 範本:Android Lint」;只寫待查的列 應 不含這兩個字樣 [test:t_kt_catalog_batch4_wiring]
- [S5] 當在一個真的 Android 專案(公開範例專案,記下它的 AGP 版本)照範本加 Android Lint、Slack compose-lints 與 compose-rules,產基準線後故意加一處 Compose 錯誤寫法時,`./gradlew lint<變體>` 與 `detekt<變體>` 應 失敗並點名那一處;耗時記進驗證紀錄 [manual:在暫存區複本實跑一次範本的每一步,記下 AGP 版本、任務名、耗時與報出的規則碼]
- [S6] 當代碼審 r4 邊界席的固定語料(15 個公開專案真實 CI 檔的最小節錄,加 12 列負例、正例與合成例)逐列跑 A1 時,每列 應 符合人工判定;Signal 自訂聚合任務、AuroraStore `stage: lint`、`npm run lint`、CircleCI gradle orb `command: build` 四列 應 照天花板維持現行判法並標成已知判錯 [test:t_lint_android_ci_corpus]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | kt 宣告、根 `build.gradle.kts` 有 `com.android.application`、沒有 CI 設定檔 | 印 A1 | 官方 lint 頁:Gradle 專案用 `./gradlew lint`、建議放進 CI(https://developer.android.com/studio/write/lint ) |
| S1 | 同上,workflow 有 `./gradlew --no-daemon assembleDebug lintDebug` | 不印 A1 | 同上:變體任務是 `lint<變體>`;Gradle 一行可接多個任務與選項 |
| S1 | 同上,workflow 只有 `./gradlew lintKotlin` | 印 A1 | kotlinter 外掛的 ktlint 任務叫 `lintKotlin`,不是 Android Lint |
| S1 | 同上,`azure-pipelines.yml` 的 Gradle 任務寫 `tasks: 'clean build test assembleRelease'` | 不印 A1 | Azure Gradle 任務的 `tasks` 輸入就是要跑的 gradle 任務(https://learn.microsoft.com/azure/devops/pipelines/tasks/reference/gradle-v2 );`build` 帶 `check` 帶 lint |
| S1 | 同上,workflow 只有 `needs: build`、`cache: gradle` 與 `./gradlew assembleDebug` | 印 A1 | `needs:` 是 job 依賴、`cache: gradle` 是快取設定,`assembleDebug` 不帶 lint;代碼審 r3 三席重現 |
| S1 | 沒有 CI 設定檔、只有 `app/lint-baseline.xml` | 印 A1 | 範本第 2 步產基準線、第 3 步才加 CI;基準線檔不代表 CI 有跑 |
| S1 | 同上,workflow 只有 `./gradlew lintVitalRelease` | 印 A1 | AGP DSL 參考頁:release 建置只檢查 fatal 級(`checkReleaseBuilds`) |
| S1 | 只有 `org.jetbrains.kotlin.jvm` 外掛 | 不印 A1、A2、A3 | 本計劃〈用詞〉Android 專案沿用 `_KT_BUILD_ANDROID` |
| S2 | Android 專案有 `compose = true`、沒有任一 Compose 規則字樣 | 印 A2 | 本計劃〈用詞〉用 Compose 的專案的定義 |
| S2 | 宣告 detekt 命令帶 `--plugins …detekt-compose-0.4.28-all.jar` | 不印 A2 | compose-rules 官方 detekt 頁的 CLI 用法 |
| S3 | 標準 Compose 檔經現行共用設定 | 報 6 條(FunctionNaming 2、LongParameterList、MagicNumber、TopLevelPropertyNaming、UnusedPrivateMember) | 2026-11-06 本機 detekt 1.23.8 實跑 |
| S3 | 同一支檔經加六項後的共用設定 | 只剩 `fun Other()` 的 FunctionNaming | detekt 官方 Compose 頁六項建議;2026-11-06 實跑 |
| S3 | `@Composable` 裡 `val s = mutableStateOf(0)` 經外掛那條 | 報 `RememberMissing` | 2026-11-06 本機 detekt 1.23.8 加外掛 0.4.28 實跑 |
| S4 | 現成規則欄寫 `cr:compose:unstable-collections / UnstableCollections(opt-in)` | 不標「推送前:detekt 外掛 compose-rules」 | compose-rules 外掛自帶設定 `UnstableCollections` 預設關 |
| S4 | 現成規則欄寫 `slack:ComposeItemKeyHashCode` 的列 | 通電批次含「CI 範本:Android Lint」 | 本計劃範圍 4 |
| S5 | 範例專案照範本接好、產基準線後加一處沒包 remember 的 `mutableStateOf` | `lint<變體>` 與 `detekt<變體>` 失敗並點名那一處 | 官方 lint 頁:基準線之後只報新增;compose-rules 規則頁 RememberMissing |
| S6 | r4 語料:microsoft/appcenter-sampleapp-android、nowinandroid 等 15 個公開專案的 CI 檔節錄 | 各列照人工判定;四列天花板照現行 | 代碼審 r4 邊界席語料表,`governance/review-reports/code-android現成檢查/r4-邊界-sonnet.md` |

## 回退

退回本案的提交:A1、A2、A3 提醒不再印;共用設定的六項放寬拿掉後,標準 Compose 寫法又會被報 6 條(推送前新增告警閘只擋新增的);`configs/detekt/compose.yml` 消失,消費專案照範本加的 compose-rules 那條宣告會因設定檔找不到而被判環境不可用、自動放行;型錄通電批次字樣回到「批四(現成規則)」。消費專案已照範本加的 Gradle 設定不受影響。

## 天花板

1. Android Lint 與 Slack compose-lints 只在 CI 擋,推送前不擋;AI 寫完到 CI 跑完之間的空窗,只有規則包與 detekt(含 compose-rules)守。
2. 健檢只看 CI 設定檔字面(GitHub、GitLab、Bitrise、CircleCI、Jenkins、Azure 的固定檔名;Taskcluster 這類別的 CI 會多印 A1),不驗 CI 真的跑、跑的是哪個模組;多模組專案只對 `:app:lint` 有字樣也算接上;寫了 lint 字樣卻用 `-x lint` 排除、或只出現在 `echo` 裡,也算有跡象(A1 少印,不誤報);job 或 stage 名叫 `lint`(例 `name: lint` 底下只跑 `ktlintCheck`)、別的工具的 lint(`npm run lint`)也算有跡象(少印)。composite action(`uses: ./.github/actions/…`)與 GitLab `include:` 引進的檔讀不到,任務寫在那裡會多印 A1。gradle 任務列裡任何位置的 `check`、`build` 字樣都算(`./gradlew assembleDebug -x check`、`-PbuildType=check`、`./gradlew test && cd build`),少印。任務藏在自訂聚合任務裡(Signal-Android 的 `./gradlew ciRemote` 在根建置檔 `dependsOn` lint 任務)看不到,多印。別的工具或名稱裡的 `lint` 字樣也算跡象(GitLab `stage: lint` 底下只跑 `ktlintCheck`、`npm run lint`、YAML 行尾 `./gradlew assembleDebug // lint`),少印。YAML 摺疊純量(`run: >` 把 `./gradlew` 與下一行 `build` 接成一行)與反斜線續行跨過整行 `#` 註解時,本來是兩條命令也被接成一條,少印。CircleCI gradle orb 的 `command: build` 會跑 build,但 `command` 是 CircleCI run 步驟的通用欄位(`command: npm run build` 收進來會吞掉提醒,代碼審 r5 三席),不收,多印。Jenkinsfile 照 Groovy 剝註解、不套 `#` 規則,`sh '''…'''` 區塊裡 shell 的 `# ./gradlew lint` 註解行也算跡象,少印。已知欄位沒寫、靠預設值(Azure `tasks` 預設是 `build`),或任務放在矩陣變數(`task: [check, test]` 加 `./gradlew ${{ matrix.task }}`)裡,看不到,多印。Android 模組放在 `_stack_scan_skip` 會跳過的資料夾名(`target/`、`vendor/`、`build/` 等)時判成不是 Android 專案,三則提醒都不印(少印,不誤報)。
3. 健檢的三則提醒只在專案有 `.lumos/lint.json` 而且宣告了 kt 棧時才判(跟 T4 同一個前提);完全沒宣告的 Android 專案不會被提醒。
4. A2 只讀 Gradle 建置檔與版本目錄;把 `lintChecks`、`detektPlugins` 寫在 `build-logic/`、`buildSrc/` 這類建置邏輯模組的 `.kt` 檔裡的專案(Now in Android 的寫法),健檢看不到、會多印 A2。任務藏在 shell 腳本或 composite action 裡時,A1 找不到跡象而多印提醒。A3 的相對外掛路徑一律對 repo 根解析,命令先 `cd tools && detekt-cli --plugins x.jar` 再用相對路徑時會誤印 A3。
5. structured-coroutines 26 列、Sonar 7 列、IntelliJ 4 列與 compose-rules 預設關的三條,仍沒有機械守衛,只靠告警訊息與代碼審。

REVISIT:2026-12-15 照 S5 在一個 AGP 8.x 與一個 AGP 9.3 以上的公開 Android 專案各實跑一次範本,記下 Slack compose-lints 版本表是否成立,並用 ./gradlew check --dry-run 核對 lint 任務真的掛在 check 底下
REVISIT:2027-02-15 數消費專案健檢印 A2 的次數裡有幾次其實接在 build-logic 的 .kt 檔,超過一半就把建置邏輯模組納入掃描
REVISIT:2027-02-15 判 structured-coroutines 有沒有正式版、compose-rules 預設關的三條要不要開

## 依據來源

每個機制一行:依據是什麼、在哪裡看得到。(使用者 2026-11-06:「我們開發的過程中，所有機制的依據來源，最後也要補回plan，方便後續迭代」「而且我要變成規則，機制來源必填」)

| 機制 | 依據 | 出處 |
|---|---|---|
| Android Lint 只在 CI 跑、不在推送前跑 | 官方:Gradle 專案一律用 `./gradlew lint`,單機版對 Gradle 專案會報錯;官方建議把 lint 放進 CI | https://developer.android.com/studio/write/lint |
| CI 範本的 `baseline`、`warningsAsErrors`、`checkDependencies`、`sarifReport` | AGP Lint DSL 官方參考頁各屬性的說明 | https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint |
| 先產基準線再加 CI 步驟、`-Dlint.baselines.continue=true` | 官方 lint 頁〈Create a warnings baseline〉 | https://developer.android.com/studio/write/lint |
| Slack compose-lints 的接法與版本挑法(lint 版本 = AGP 加 23) | 官方安裝頁;GitHub 發行說明:1.5.5 同時寫「Build against lint 32.3.2」與「AGP lint plugin 9.3.2」(+23 的直接證據)、1.6.1「Build against lint 32.4.1」、1.5.0「Build against lint `32.2.1`」(對 AGP 9.2.1)、1.4.2「Build against lint 31.7.1」、1.4.0「Build against Lint `8.7.0`」(對 AGP 8.7.0);1.6.0 的「requires AGP/lint 9.3+」寫在 ComposeModifierComposed 那項變更旁邊,不拿來當整版的下限 | https://slackhq.github.io/compose-lints/ 、https://github.com/slackhq/compose-lints/releases |
| Slack 預設關的三條不標接電 | Slack 規則頁:ComposeUnstableReceiver、ComposeUnstableCollections「disabled by default」、ComposeM2Api「opt-in」 | https://slackhq.github.io/compose-lints/rules/ |
| compose-rules 用 detekt 外掛、不用型別資訊 | 官方 detekt 頁 CLI 用法與版本表(官方頁沒寫型別資訊這件事,是實跑結論);2026-11-06 本機 detekt 1.23.8 加外掛 0.4.28、只給 `--input` 實跑壞例,RememberMissing、MutableParams、MutableStateAutoboxing、ComposableNaming 四條都報 | https://mrmans0n.github.io/compose-rules/detekt/ ;實跑紀錄見設計審卷證 `governance/review-reports/android現成檢查接上ci與推送前/r1-正確性-sonnet.md` 開頭的查證段 |
| compose-rules 另開一條宣告(`--disable-default-rulesets`) | 2026-11-06 實測:`--plugins` 指不存在的 jar 時 detekt rc 1、不產 SARIF,整條會被判環境不可用 | 設計審卷證 governance/review-reports/android現成檢查接上ci與推送前/r1-intake.md |
| 那條宣告一定要帶 `--build-upon-default-config` | 2026-11-06 實測:少了它外掛規則一條都不跑、也不報錯 | 本計劃審計修正紀錄「實作更正」;測試 t_detekt_compose_rules_shared_config |
| compose-rules 預設關的三條不開 | 外掛自帶設定 `active: false`(UnstableCollections、PreviewNaming、Material2) | 外掛 jar 內 config/config.yml;設計審 r1 邊界席實讀 |
| 共用 detekt 設定的六項 Compose 放寬 | detekt 官方 Compose 頁的六項建議;compose-rules 規則頁要求 `ignoreAnnotated: ['Preview']`;2026-11-06 實跑現行設定對標準 Compose 檔報 6 條、加上後只剩一般函式那條 | https://detekt.dev/docs/introduction/compose/ 、https://mrmans0n.github.io/compose-rules/rules/ |
| `TopLevelPropertyNaming` 樣式收底線 | detekt 預設樣式 `[A-Z][_A-Z0-9]*`(Kotlin 慣例全大寫加底線)要保留;代碼審 r1 接手席實跑抓到只寫 PascalCase 會讓 `MAX_ITEMS` 被報 | 代碼審卷證 r1-接手-sonnet.md;測試 t_detekt_compose_rules_shared_config |
| 外掛 jar 放本機固定目錄、下載釘雜湊、驗過才改名 | linter 目錄既有規則「外部工具一律裝進套件管理器,嚴禁易失位置」的例外:brew、sdkman 沒有配方;下載加比對雜湊沿用本 repo CI 下載 detekt 的做法;暫存檔驗過才改名是代碼審 r1 資安席指出壞檔會留在正式位置 | Systems/linter精選目錄;.github/workflows/ci.yml 裝 detekt 那一步 |
| A1 用證據模型(找不到任何跡象才提醒) | OpenSSF Scorecard 官方檢查文件:SAST 檢查「looks for known GitHub apps … or the use of github/codeql-action in a GitHub workflow」,並寫「it is challenging for an automated tool like Scorecard to detect them all」「A low score is therefore not a definitive indication」;CI-Tests 檢查同樣只認一組已知名字並寫「may still receive a low score」。代碼審 r1、r2 連續打穿「判斷有沒有接」的字面寫法(逐條解析命令、找字但限 gradle 那行)後,改成只找跡象、找不到才提醒、提醒措辭不下定論 | https://github.com/ossf/scorecard/blob/main/docs/checks.md |
| A1 證據模型的實測 | 現行判法以代碼審 r4 邊界席的固定語料為準(15 個公開專案真實 CI 檔加 12 列負例、正例與合成例,寫成測試 `t_lint_android_ci_corpus`,修補前後都跑)。下面這段是 r2 舊模型(整檔有 gradle 字樣、建置檔設定也算)的實測,只留作歷史:2026-11-06 下載 6 個公開 Android 專案的 GitHub workflow 實跑:nowinandroid、thunderbird、element-x、NewPipe 找到跡象,architecture-samples(只有 connectedCheck)與 firefox-android(CI 在 Taskcluster)找不到;每個專案找到的跡象詞記在卷證 | `governance/review-reports/code-android現成檢查/r4-邊界-sonnet.md` 語料表;舊模型實測 `governance/review-reports/code-android現成檢查/r2-ciexp.md` |
| A1 認 `check`、`build` | AGP 讓 `check` 依賴 `lint`;Gradle `build` 依賴 `check`;社群慣用 `./gradlew check -x lint`、`build -x lint` 排除 lint,旁證 lint 掛在兩者底下(官方任務圖頁未找到,S5 實跑時用 `--dry-run` 核對) | https://android.googlesource.com/platform/tools/base/+/cc9093a%5E%21 、https://docs.gradle.org/current/userguide/base_plugin.html 、https://stackoverflow.com/questions/21143556/avoid-lint-when-gradle-execute-check |
| A1 的 `check`、`build` 只在同一邏輯行有 gradle 呼叫詞時才算,建置設定不算 | 代碼審 r3 三席各自實跑重現:整檔有 gradle 字樣就認 `check`/`build` 時,`needs: build` 加 `cache: gradle`、GitLab `stage: build` 讓沒接 lint 的專案靜默;建置檔 `lint { }` 與 `lint-baseline.xml` 是範本第 1、2 步的痕跡,把第 3 步缺漏的提醒關掉。排除:整檔找詞(r3 打穿)、拿建置設定當 CI 證據(r3 打穿);採 r2 的「限 gradle 那行」與 r3 的「lint 名任何位置都算」各取對的那半 | 代碼審卷證 `governance/review-reports/code-android現成檢查/r3-intake.md` 與同目錄 r3 席報告 |
| A1 把 `tasks:`、`arguments:`、`gradle_task:` 三個欄位的值當 gradle 任務列,不收 `command:` | 各工具官方定義:Azure Pipelines Gradle@2 的 `tasks` 輸入(「Tasks. Default: build」);gradle-build-action 的 `arguments` 輸入「Gradle command line arguments (supports multi-line input)」(已標為棄用、改建議先 setup 再自己跑 gradle,舊專案仍常見);Bitrise steps-gradle-runner 的 `gradle_task`「Gradle task to run」。代碼審 r4 四席實跑重現 r3 版把這幾種寫法判成沒跑;只收這三個名字,其他欄位照舊不算(不回到整檔找詞)。`command:` 在 r4 收過、r5 拿掉:CircleCI 設定參考頁的 run 步驟寫 `command`「Command to run via the shell」,是通用欄位,不專屬 gradle orb(orb 的 `run` job 雖以 `./gradlew << parameters.command >>` 組命令、預設 build),`command: npm run build` 會吞掉提醒(代碼審 r5 三席重現);限定 orb 上下文要再寫一套 YAML 結構判斷,不做 | https://learn.microsoft.com/azure/devops/pipelines/tasks/reference/gradle-v2 、https://github.com/gradle/gradle-build-action/blob/main/action.yml 、https://github.com/bitrise-steplib/steps-gradle-runner/blob/master/step.yml 、https://circleci.com/docs/configuration-reference/#run 、https://github.com/CircleCI-Public/gradle-orb/blob/main/src/jobs/run.yml |
| CI 設定檔與建置檔解析真實路徑、在 repo 外才略過 | 代碼審 r4 通才與資安席:只擋檔案本身是連結時,資料夾連結照樣讀到 repo 外,repo 內的合法連結反被略過讓 T4 誤印;沿用 lumos 既有「解析後要在 repo 內」的判法(`_repo_path_unsafe` 的 outside 判定抽成 `_path_resolves_in_root` 共用;r5 架構對齊席指出事件帳路徑守衛與殺傷力配方讀筆記還各自內嵌一份,一併改呼叫它)。非嚴格解析下連結迴圈不丟例外,留在 repo 內就判在,後面開檔自然失敗(r5 資源席實測) | scripts/lumos;Python `pathlib.Path.resolve` 與 `is_relative_to` |
| A1 不算 `lintKotlin`、`lintFix`、`lintVital` 開頭的任務 | kotlinter README:`lintKotlin`「report Kotlin lint errors」(ktlint,不是 Android Lint);googlesamples custom-lint-rules 使用手冊:`lintFix` 是「running the lint command with --apply-suggestions」(套用修正、改原始碼);AOSP 提交 cc9093a 的 `lintVitalRelease` 只檢查 fatal 級(DSL 參考頁 `checkReleaseBuilds` 寫 release 建置只看 severity=fatal,是旁證)。`lintAnalyze`、`lintReport` 找不到官方出處,不收 | https://github.com/jeremymailen/kotlinter-gradle 、https://googlesamples.github.io/android-custom-lint-rules/user-guide.html 、https://android.googlesource.com/platform/tools/base/+/cc9093a%5E%21 、https://developer.android.com/reference/tools/gradle-api/8.7/com/android/build/api/dsl/Lint |
| CI 設定檔納入 GitLab、Bitrise、CircleCI、Jenkins、Azure | 設計審 r1 邊界與接手兩席指出只看 GitHub 會讓其他 CI 的專案永遠誤印 | 設計審卷證 r1-intake.md |
| A3 外掛路徑照 shell 展開、相對 repo 根、判不了不判 | 新增告警閘以 repo 根當工作目錄、經 shell 執行命令;Python `os.path.expandvars` 對沒設的變數原樣保留;反引號與萬用字元要 shell 才算得出(代碼審 r2 邊界席實測誤報) | scripts/lumos 的 `_lint_spawn`;https://docs.python.org/3/library/os.path.html#os.path.expandvars |
| Android 專案判法、建置檔剝註解、資料夾跳過名單 | 沿用 lumos 既有的 `_KT_BUILD_ANDROID`、`_kt_strip_comments`、`_stack_scan_skip`(代碼審 r1 架構對齊席:不另立一套) | scripts/lumos |
| 型錄第四批口徑住在型錄自檢 | 型錄的欄位、出處檢查原本就集中在 check.py 的 `catalog_problems`(代碼審 r1 架構對齊席) | configs/ast-grep/kotlin-android/check.py |

## 審計修正紀錄
- r1(2026-11-06,四席 sonnet:正確性、邊界、接手、架構對齊):30 條/blocking 12/接上 compose-rules 後 detekt 內建規則對 Compose 寫法還有五種誤報(兩席獨立實跑抓到,其實現行設定就有)、預設關的三條規則會被型錄標成已接電(兩席)、A1 的字面判法對常見 CI 寫法誤報又把 `lintKotlin` 當 Android Lint(四席)、外掛缺檔會拖垮整條 detekt(三席);共用設定照 detekt 官方 Compose 頁加六項、compose-rules 另開一條只跑外掛的宣告、A1 改整行掃任務詞、型錄口徑改切段判並排除預設關與 opt-in、Android 判法沿用既有正規式;全部折入,逐條去向在 r1-intake.md。卷證:governance/review-reports/android現成檢查接上ci與推送前/。
- 實作更正(2026-11-06):範圍 2 原本寫的 compose-rules 命令少了 `--build-upon-default-config`,實作時本機實跑發現少了它外掛規則一條都不跑、也不報錯(rc 0、SARIF 空),照實改正文並在 S3 釘住範本那行要帶它;測試執行器會隔離家目錄,S3 在本機靠 `LUMOS_DETEKT_COMPOSE_JAR` 找外掛,本機固定目錄那個後備路徑只在真實使用時用得到。
