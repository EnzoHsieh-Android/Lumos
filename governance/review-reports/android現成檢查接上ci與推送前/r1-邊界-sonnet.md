severity: major

## 逐節範圍

已讀,無 finding 的節:用詞(Android 專案定義的邊界見 F10)、回退、天花板、預期值表。其餘各節的 finding 如下。

我把 compose-rules 0.4.28 的 jar 實際下載,sha256 與 spec 一致(`b8c732…ddd6`)。用 detekt 1.23.8 搭 `android.yml` 加 `FunctionNaming ignoreAnnotated: ['Composable']` 跑了壞例。`@Composable fun Header()` 不報 `FunctionNaming`,一般函式 `fun Other()` 照報,`RememberMissing` 有報。這幾點 spec 說對了。

### F1 範圍 2、實務隱患「FunctionNaming 改設定的影響」:共用設定只放寬 FunctionNaming,Compose 的其他誤報會讓閘擋住新寫的 Composable
severity: major
blocking: 是,加外掛後推送前閘會擋掉每一個新寫的長參數 Composable 和 `@Preview`,而 spec 完全沒提。

引句:「只加 `naming: FunctionNaming: ignoreAnnotated: ['Composable']`,理由寫在檔內註解」

- 實跑同一份設定加外掛。`@Composable fun Many(a..g 七個預設值參數)` 報 `LongParameterList`(門檻 6)。
- `@Preview @Composable private fun XPreview()` 報 `UnusedPrivateMember`。
- compose-rules 官方規則頁明寫:「Be sure to set Detekt's ignoreAnnotated configuration to ['Preview'] for compatibility with this rule.」(https://mrmans0n.github.io/compose-rules/rules/)
- 新增告警閘只擋新增的告警。所以每個新寫的私有 preview 或大參數 Composable 都會被擋。
- spec 的 RETIRE-IF 預期的是外掛自己的誤報,沒考慮這條。實務隱患節也沒列。
- ⚠ spec 另稱「compose-rules 官方建議對 `Composable` 註解忽略」。我讀了 `/detekt/` 與 `/rules/` 兩頁,都找不到 FunctionNaming 的建議。出處需要補上,或改成「實跑得知」。

### F2 範圍 4、S4:型錄裡預設關閉的 compose-rules 規則會被標成「推送前:detekt 外掛 compose-rules」,實際沒在跑
severity: major
blocking: 是,通電批次欄會宣稱「已接電」,規則實際沒開,而且 S4 的判法照字面寫就會判錯。

引句:「點名 compose-rules 規則碼的列改成「批四(推送前:detekt 外掛 compose-rules)」」

- 外掛 jar 內的 `config/config.yml` 有三條 `active: false`:`Material2`、`PreviewNaming`、`UnstableCollections`。
- 型錄對應的三列已寫 `cr:compose:material-two(opt-in)`、`cr:compose:preview-naming(opt-in)`、`cr:compose:unstable-collections / UnstableCollections(opt-in)`。
- spec 同節稱「`Compose: active: true` 不必要(外掛規則預設開)」,對這三條不成立。
- 只寫「點名規則碼」的判法會把它們標成已接電,不看 opt-in。
- file: `skills/kotlin-idioms/checks-catalog.md`,用 `grep -n "opt-in"` 可找到這幾列。

### F3 範圍 3 A1:`lint` 接大寫變體名的字面規則,會把 kotlinter 的 `lintKotlin` 當成 Android Lint
severity: minor
blocking: 否,影響只在健檢提醒,但這是字面規則本身的洞。

引句:「任務名剛好是 `lint`,或 `lint` 接大寫開頭的變體名,前面是 `gradlew` 或 `:模組:`」

- `./gradlew lintKotlin` 是 kotlinter 外掛的任務,不是 Android Lint。它符合「lint + 大寫開頭 + 前面是 gradlew」。
- 結果是 workflow 只跑 kotlinter 時 A1 不印,正好漏報。
- 排除表只列 Fix、Vital、Analyze、Report 四個開頭,沒有 Kotlin。
- 反過來,flavor 名叫 `Fixture`、`Report…` 的專案,真正的 `lintFixtureDebug` 會被排除表誤殺。

### F4 範圍 3 A1:「前面是 gradlew」的字面判法,對常見寫法會誤印;`check`、`build` 也會帶 lint
severity: minor
blocking: 否,只是提醒,但誤印是常態寫法造成的。

引句:「前面是 `gradlew` 或 `:模組:`」

- `./gradlew clean lintDebug`、`./gradlew --no-daemon lintDebug`、`./gradlew assembleDebug lintDebug` 中,`lintDebug` 前面都不是 `gradlew`。
- GitHub Actions 常見的 `with: arguments: lintDebug`(setup-gradle 或 gradle-build-action)也沒有 `gradlew` 字樣。
- 以上情況都會誤印 A1。
- `./gradlew check` 與 `build` 會帶 `lint` 任務,同樣誤印。
- 天花板第 2 項與實務隱患「健檢字面判斷誤判」只承認 shell 腳本和 composite action 兩種。
- 對照 T4:`_detekt_ci_has_typed_task` 是整檔 `\bdetekt[A-Za-z0-9]*` 比對,沒有前綴要求,見 file: `scripts/lumos:38915-38930`。A1 若沿用 T4 的做法,前兩類誤印就消失。

### F5 範圍 4、S4:「點名 Android Lint」的關鍵字沒定義,型錄實際用的是「內建」與「androidx」
severity: minor
blocking: 否,這是可執行性缺口,判定口徑被延到實作時才寫。

引句:「現成規則欄點名了 Android Lint、androidx、Slack 規則碼(不是「待查」)的列」

- 型錄現成規則欄從不寫「Android Lint」。型錄 file: `skills/kotlin-idioms/checks-catalog.md:15` 的簡稱表是「androidx/內建 = Android Lint」。
- 統計該欄:以「內建:」開頭的列約 72 列(例 `內建:TrustAllX509TrustManager`)。字面比對「Android Lint」會全部漏掉。
- 邊界列有四類:
  - `androidx UnnecessaryLambdaCreation 待查`:同時點名 androidx 與待查,spec 的括號條件互相打架。
  - `內建:MainScopeUsage(說明待查)`:同上,內建與待查並存。
  - `無(相近:androidx.activity:InvalidFragmentVersionForActivityResult 只檢查 Fragment 版本)`:批次是批一,並未被這條規則守住,卻出現了 androidx 字樣。S4 的「點名就含字樣」會把它誤標。
  - 同時含 detekt 規則碼(已在推送前)與 Android Lint 的列,例如 `SC KMP_003:detekt MainScopeWithoutCancel;內建:MainScopeUsage`。
- 「兩者都有寫兩個」沒說明兩個字樣在單一格內的分隔符與順序。S4 只驗「含」,沒驗格式。

### F6 範圍 3、天花板第 2 項:非 GitHub CI 和沒有 `.lumos/lint.json` 的 Android 專案
severity: minor
blocking: 否,影響只是提醒的噪音與涵蓋面。

引句:「`.github/workflows/` 底下的 `.yml`/`.yaml` 沒有任何 Android Lint 檢查任務字樣」

- 用 GitLab CI、Bitrise、CircleCI、Jenkins 的 Android 專案沒有 `.github/workflows/`。預期值表直接寫「沒有 workflow → 印 A1」。
- 這樣的專案會永遠印「Android Lint 與 Slack compose-lints 哪裡都沒擋」,而 CI 其實有跑。這句話是假的,也沒有消音辦法。
- 反向:前提是「宣告裡有 `kt` 棧」,所以沒有 `.lumos/lint.json` 的專案。`cmd_lint_check` 在 `declared == False` 時提早 return(`scripts/lumos:39099` 附近),不會跑任何 advisories。
- 這些專案沒有 A1、A2。spec 沒把這個涵蓋面缺口列進天花板。

### F7 範圍 3「掃的檔」:建置檔解碼方式沒說,Big5 或 GBK 註解的建置檔可能整支被當作讀不了
severity: minor
blocking: 否,影響只是漏判。

引句:「讀不了的當沒有」

- workflow 讀法沿用 `read_text(encoding="utf-8", errors="replace")`,不會中斷。
- 建置檔那段只寫「讀不了的當沒有」,沒指定 `errors="replace"`。
- 若實作用嚴格 UTF-8 解碼,繁中註解以 Big5 存的 `build.gradle` 會丟 `UnicodeDecodeError`,整支被當作沒有。這個專案就判成非 Android,A1、A2 全不印。
- spec 要明寫 `errors="replace"`,並補一個非 UTF-8 的測試案例。S1、S2 都沒有。

### F8 範圍 2:外掛檔缺席時,detekt 整條失效而不只是 compose-rules
severity: minor
blocking: 否,spec 已承認並自述「閘的既有行為,不改」,但後果沒量化,也沒對應的健檢提醒。

引句:「外掛檔不在時 detekt 整條失敗、新增告警閘照既有規則判環境不可用」

- 我實跑 `detekt --input a.kt --plugins /nonexistent/x.jar`:丟出 `ParameterException: Provided path '/nonexistent/x.jar' does not exist!`,沒有 SARIF。
- `_lint_run_and_parse` 讀不到 SARIF 就回 `([], False)`(file: `scripts/lumos:39572-39640`)。環境不可用的路徑自動放行。
- 結果是任何沒下載外掛的機器,連內建 detekt 規則(GlobalCoroutineUsage、複雜度等)都不再擋。這比加外掛前更弱。
- A1、A2 不檢查「`--plugins` 指向的檔案是否存在」。靜態層(`lint-check` 不帶 `--smoke`)也不會發現。
- 只有 `--smoke` 或自動放行計數看得到。

### F9 PRIOR-ART:Slack 範本版本和 AGP 要求的說法可能不一致
severity: minor
blocking: 否,範本寫的是字面版本,且「官方行為,lumos 判不到」已列入隱患。

引句:「`lintChecks("com.slack.lint.compose:compose-lint-checks:1.6.1")`(註明 1.6.x 要 AGP 9.3 以上」

- 官方發行說明:1.6.0 寫「Note this requires AGP/lint 9.3+.」。1.6.1 沒寫最低版本,只寫「Build against lint `32.4.1`」(https://github.com/slackhq/compose-lints/releases)。
- spec 把「1.6.x 要 9.3 以上」套到 1.6.1。lint 32.4.1 對應的 AGP 版本我沒查到,⚠ 判不準 1.6.1 的實際下限是否仍是 9.3。
- 範本釘 1.6.1 又註明 9.3,若 1.6.1 實際要求更高,按範本接的專案會碰到「載不進外掛」。

### F10 用詞「Android 專案」:只掃根目錄與下一層,多層目錄結構的專案會被判成非 Android
severity: minor
blocking: 否,範圍限制已列於實務隱患「掃建置檔的成本」,但漏判的後果沒有進天花板。

引句:「專案根目錄與下一層的 Gradle 建置檔」

- monorepo 常見的結構 `apps/android/app/build.gradle.kts`、`mobile/android/app/build.gradle` 的 `com.android.application` 在第三層或更深。
- 這種專案若宣告了 `kt` 棧,判成非 Android,A1、A2 都不印,而且沒有任何提示說「沒掃到」。
- 若 `gradle/libs.versions.toml` 不在預設位置(例如 `settings.gradle` 裡 `from(files("../shared/libs.versions.toml"))`),建置檔只有 camelCase 別名 `libs.plugins.androidApplication`。用詞節的別名模式(`android.application`、`android-application`)不含 camelCase,同樣判成非 Android。

## 實務隱患逐類

- 金流:無,spec 已排除,功能只讀本機檔。
- 對外送出:無,健檢不連網。唯一的外部動作是人照抄下載指令。F8 是缺檔時的降級,不是外送。
- 不可逆:無,新增提醒與文件,退提交即回原狀。
- 守衛面:有,見 F1。放寬 FunctionNaming 的影響比 spec 說的大,另外還有未處理的誤報。
- 資安:sha256 釘版本我核對相符。外掛 jar 是任意程式碼會在每次推送前被載入,spec 只靠「下載後比對不符就不要用」,而比對是人工步驟。這是單人自用框架(依 lumos 威脅模型),不另列 finding。
- 效能與記憶體:掃建置檔上限(200 支 × 1 MB)夠用。我沒發現超大建置檔造成的問題。
- 符號連結、極端輸入:workflow 讀法用 `p.is_file()` 跟隨 symlink,沒有問題。建置檔的 symlink 處理 spec 沒寫,但兩層深度加 1 MB 上限能擋住迴圈。

## 節點固定席

- `Systems/linter精選目錄`:這份設計新增一節,並改 detekt 範本段。我看不出會破壞它既有的行為或合約。
- `Systems/lint-declaration-health`:合約是 lint-check 的退出碼語意(0 健康、1 問題、2 非 JSON)。spec 把 A1、A2 做成「不進 problems、不改退出碼」,與 `cmd_lint_check` 現有的 T4 做法一致(`scripts/lumos:39114`)。所以不影響。
- `Systems/kotlin規則包`:這份設計只動 `configs/detekt/android.yml`、型錄與健檢,不碰規則包的 ast-grep 檔。不影響。這裡不含 F1,F1 屬於共用 detekt 設定。

最嚴重的 severity 是 major,blocking 共 2 條(F1、F2)。
