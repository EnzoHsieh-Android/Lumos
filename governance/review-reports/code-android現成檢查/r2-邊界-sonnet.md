severity: major

(臨時目錄已刪。型錄逐列只對了前半,沒找到判錯的列;compose-rules 預設關清單我沒能查證。)

## F1 A1 對 Bitrise、Azure 的標準寫法誤報(實際有跑 lint,卻印「找不到」)
severity: major
blocking: 是

引文:
引句:「只在提到 gradlew、gradle 或 `arguments:` 的行上才算。不解析命令:續行、多行區塊、矩陣變數因此都自然涵蓋;」

file: `scripts/lumos:39016`(`_android_ci_has_lint_task`)。`lint`、`check`、`build` 這三個字,只有那一行出現 `gradlew`、`\bgradle\b` 或 `arguments:` 才算。`bitrise.yml` 和 `azure-pipelines.yml` 都在 `_CI_OTHER_CONFIG_FILES`(`scripts/lumos:38922`)裡,但它們的標準寫法不含這些字。

重現(端到端,有跑):在臨時 repo 放 `build.gradle.kts` 寫 `plugins { id("com.android.application") }`,`.lumos/lint.json` 寫 `{"kt":["detekt --input app"]}`,再放下面的 `bitrise.yml`,然後跑 `lint-check --repo <臨時目錄>`:
```
workflows:
  primary:
    steps:
    - gradle-runner@2:
        inputs:
        - gradle_task: lint
```
實際輸出印出:`[CI] A1:專案是 Android,但 CI 設定檔(...)裡找不到 Android Lint 任務字樣`

直接呼叫函式,以下都回 False(都應該算有接):
- `gradle_task: lint`(`gradle_task` 裡的底線屬於 `\w`,`\bgradle\b` 對不上)
- `gradle_task: check`
- Azure 的 `- task: Gradle@3` 加 `tasks: 'build'`、`tasks: check`(`Gradle` 大寫,`tasks:` 那行沒有 gradle 字樣)
- Bitrise 內建的 `- android-lint@0.9:`(`android-lint` 被切成一個詞,不是 `lint`)

## F2 A1 的續行寫法漏判(已接卻判沒接)
severity: major
blocking: 是

引文:
引句:「只在提到 gradlew、gradle 或 `arguments:` 的行上才算。不解析命令:續行、多行區塊、矩陣變數因此都自然涵蓋;」

file: `scripts/lumos:39026`。函式逐行判斷,所以「`lint<變體>` 接在續行上」確實涵蓋,但純 `lint`、`check`、`build` 接在續行上不涵蓋。這句話對這三個字不成立。

輸入:
```
run: |
  ./gradlew \
    --no-daemon \
    check
```
輸出:`_android_ci_has_lint_task` 回 False,A1 誤報。`./gradlew\n  lint` 同樣回 False。

## F3 A1 的 Groovy `//` 註解沒剝,被註解掉的 lint 算有接
severity: minor
blocking: 否

引文:
引句:「整份檔任何地方出現 `lint` 接大寫開頭的變體名就算」

輸入 Jenkinsfile:`    // sh './gradlew lintDebug'` 加 `sh './gradlew assembleDebug'`。輸出:回 True(漏報)。`/* ... lintDebug ... */` 區塊註解也回 True。`_ci_workflow_texts` 只剝 `#`。這是少印提醒,所以降為 minor。

## F4 A1 在「lint<變體>」任何地方都算,路徑與網址也算
severity: minor
blocking: 否

引文:
引句:「整份檔任何地方出現 `lint` 接大寫開頭的變體名就算」

`curl https://example.com/lintFoo/x.sh` 回 True。`./gradlew -p lint assembleDebug` 回 True(`lint` 目錄被當任務)。`./scripts/lintDebug.sh` 回 True。這屬於已知天花板,只列出判成有接的例子。

## F5 A3 把路徑裡的反引號與 glob 當成缺檔(誤報)
severity: minor
blocking: 否

引文:
引句:「pth = _os.path.expanduser(_os.path.expandvars(raw))」

file: `scripts/lumos:39060`(`_android_plugin_missing`)。
- `detekt --plugins `pwd`/d/x.jar --input a`:該檔實際存在,回 True(誤報)。
- `detekt --plugins d/*.jar --input a`:有 `d/x.jar` 符合,回 True(誤報)。shell 會先展開,detekt 才收到值。
- Windows 路徑 `C:\libs\x.jar` 回 True。

沒有例外:NUL 字元、5000 字元的檔名、未閉合引號都沒丟例外。下面這些也都符合預期:`$(pwd)`、`${HOME:-/x}`、`$RUNNER_TEMP`(判不了就不印)、加引號的空白路徑、符號連結(有效的算存在、斷掉的算缺)、指到資料夾(算缺)、含逗號的 jar 名(被拆成兩段,detekt 自己也會這樣拆)。

## F6 建置檔掃描
severity: minor
blocking: 否

引文:
引句:「資料夾照 `_stack_scan_skip` 跳過、另不進隱藏資料夾」

`target/build.gradle.kts`、`vendor/app/build.gradle`、`build/build.gradle`(模組叫 `build`)、`Pods/`、`governance/`、`x-knowledge/` 都被整個跳過。如果專案唯一的 Android 模組在這些資料夾,就判成不是 Android,提醒整組不印(漏報,不誤報)。

另外 `gradle/libs.versions.toml` 的 `#` 註解沒剝。輸入:`# slack-lint = { module = "com.slack.lint.compose:compose-lint-checks" }` 加 `build.gradle` 寫 `android { compose = true }`。輸出:`"compose-lint-checks" in b` 為 True,A2 被這行註解壓掉。

Groovy 字串裡的 `//`(`url "https://x.com/m"`、單引號、`"a/*b"`、三引號字串)都沒有把後面的宣告剝掉,這項沒問題。

## 型錄口徑
我對 `skills/kotlin-idioms/checks-catalog.md` 主表 131 列重算 `batch4_expected_tags`,逐列比對,沒找到判錯的列。`UI-37`、`UI-38`、`UI-88` 的預設關、`CO-22` 的「待查」、`UI-41` 的「其他無」都判對。

## 圖譜鏡頭
範圍算不出,我沒讀 `Systems/lint-declaration-health` 與 `linter精選目錄`,這部分沒審。

總結:最嚴重是 A1 對 Bitrise、Azure 的標準 gradle 寫法與續行寫法誤報,會擋 2 條(F1、F2)。其餘 4 條是 minor。
