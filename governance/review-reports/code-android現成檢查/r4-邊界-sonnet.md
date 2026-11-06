severity: major

注意:審查席的 Bash 擋掉了 `gh` 與 `api.github.com`,所以語料改用 `curl` 從 github.com、raw.githubusercontent.com 和 gitlab.com 抓。內容都是公開專案原文。

## Findings

### F1
severity: major
blocking: 是

A1 的第二種跡象(`check`/`build`)現在要求同一行有 `gradlew`/`gradle`。這把「靠設定欄位而不是命令列叫起 gradle 的 CI 寫法」全部判成沒跑 lint,A1 誤印。受影響的寫法有:Azure `Gradle@2` 的 `tasks:`、`gradle/gradle-build-action` 的 `arguments: build`、CircleCI gradle orb 的 `command: build`、Bitrise `gradle-runner` 的 `gradle_task: build`。這些寫法實際都會跑 `build`,而 `build` 會帶 `check`,`check` 再帶 lint。

這也是相對上一版(6793598b1)的退步。舊版那段說明明寫「Azure 的 `tasks:`、Bitrise 的 `gradle_task:` 都自然涵蓋」,新版把這句連同整檔判法一起拿掉。守衛測試只補了 `arguments: lint`、`gradle_task: lint` 這種含 lint 字樣的案例,沒有 `build`/`check` 的案例。

引句:「if any(_ANDROID_UMBRELLA_WORD.fullmatch(w) for w in words) and any(_is_gradle_head(w) for w in words):」

最小重現(新版印 A1,舊版不印)。建置檔用 `plugins { id("com.android.application") }`,`.lumos/lint.json` 宣告一條 detekt 命令:

- 真實檔案 `microsoft/appcenter-sampleapp-android/azure-pipelines.yml`,內容是 `tasks: 'clean build test assembleRelease assembleDebug assembleAndroidTest'`。輸出:新版 `A1`,舊版 `-`。人工判定是有跑,因為 `build` 帶 `check` 再帶 lint。
- `.github/workflows/c.yml` 寫 `- uses: gradle/gradle-build-action@v3` 加 `with:` 底下 `arguments: build`。輸出:新版 `A1`,舊版 `-`。
- `.circleci/config.yml` 寫 `gradle/run` 加 `command: build`。輸出:新版 `A1`,舊版 `-`。
- `bitrise.yml` 寫 `gradle-runner@2` 加 `gradle_task: build`。輸出:新版 `A1`,舊版 `-`。

建議修法:把「同行有 gradle 呼叫詞」放寬成「同行有 gradle 呼叫詞,或是 `tasks`/`arguments`/`command`/`gradle_task` 這幾個已知欄位的值」。

### F2
severity: minor
blocking: 否

Signal-Android 是真實專案,CI 跑 `./gradlew ciRemote`。該任務在根目錄 `build.gradle.kts` 裡 `dependsOn` 了 `:Signal-Android:lintPlayProdDebug`,所以有跑 Android Lint,但 A1 印了。這是 A1 文字自己承認的「任務藏在自訂聚合任務」天花板。新版比舊版多這一例,因為舊版靠整檔的 `build` 字樣碰巧不印。

引句:「CI 設定檔(.github/workflows/、.gitlab-ci.yml 等)裡都找不到 Android Lint 的跡象」

輸出:新版 A1,舊版沒有 A1。

### F3
severity: minor
blocking: 否

「lint」這個字在其他工具或其他語境出現,A1 就被壓掉,少印。屬於已接受的天花板,但審查指定的負例 `npm run lint` 確實漏。

引句:「寧可少印提醒、不誤報。」

重現:
- `.github/workflows/web.yml` 寫 `npm run lint` 加 `./gradlew assembleRelease`,A1 不印。
- AuroraStore 的 `.gitlab-ci.yml` 有 `stage: lint` 與任務 `lintChecks`,內容只跑 `./gradlew ktlintCheck`,A1 不印。
- YAML 行 `./gradlew assembleDebug // lint` 也被 `lint` 字樣壓掉。

### F4
severity: minor
blocking: 否

YAML 摺疊純量 `run: >`,內容為 `./gradlew` 換行 `build`,會被判成同一邏輯行而不印 A1。在 `run: |` 或 `>` 裡寫法不同結果不同,是罕見寫法。行尾 `\` 續行跨整行註解(`# …`)時,註解行先被剝掉再接行,也會把兩條 shell 命令接成一條。

引句:「for ln in text.replace("\\\n", " ").split("\n"):   # CRLF 已由 read_text 的通用換行轉成 \n」

### F5
severity: minor
blocking: 否

文件小不一致:`linter精選目錄` 的 A1 段末尾仍寫「只看建置檔與 CI 設定檔字面」,但 A1 已經不看建置檔。

引句:「只看建置檔與 CI 設定檔字面,不驗 CI 真的跑。」

## 修補驗收(沒找到問題)

- 擋掉大括號展開的 `--plugins`:`/nonexist/{a,b}.jar`、`/nonexist/{a.jar`、`./lint/{LINT_ROOT}/a.jar` 新版都不印 A3,舊版印。判不了所以不印,符合新註解。
- 其餘 `--plugins` 寫法行為正確:`$HOME`、`${HOME}`、`~`、`~user`、`--plugins=a,b`、`-p`、引號含空白、反斜線空白都正確印 A3。`$UNSET`、`$(pwd)`、`${X:-…}`、`a$b` 都判不了而不印。
- Jenkinsfile 剝註解:字串裡的 `//`(`curl http://host/x; ./gradlew assembleDebug`、`"echo //lintDebug"`)不當註解;`/* */` 與行尾 `//` 註解裡的 `lintDebug` 會被剝掉,A1 正確印出。
- CRLF 的 workflow、`gradlew.bat` 搭配 `check`、`./gradlew \` 換行 `build`,判斷都正確。
- 壓測:Jenkinsfile 2.4MB,含未閉合 `/*`、五萬行三引號、三十萬個 `'`、兩百萬個反斜線續行,耗時 1 到 3 秒,沒有例外。
- 符號連結略過邏輯沒有問題。

## 語料表

人工判定依據:實際 CI 檔裡有沒有會叫起 Android Lint 的命令。

| 專案 | 人工判定 | A1 新版 | A1 舊版 | 對錯 |
|---|---|---|---|---|
| android/nowinandroid | 有(`:app:lintProdRelease`) | 不印 | 不印 | 對 |
| android/architecture-samples | 無(只有 `connectedCheck`) | 印 | 印 | 對 |
| thunderbird-android | 有(`./gradlew lint`) | 不印 | 不印 | 對 |
| TeamNewPipe/NewPipe | 有(`lintContinuous`) | 不印 | 不印 | 對 |
| element-android | 有(`lintGplayRelease`) | 不印 | 不印 | 對 |
| signalapp/Signal-Android | 有(`ciRemote` 依賴 lint 任務,間接) | 印 | 不印 | 錯(F2,天花板) |
| owncloud/android | 無(detekt 與單元測試) | 印 | 不印 | 對(舊版漏報,新版修好) |
| android/compose-samples | 有(`lintDebug`) | 不印 | 不印 | 對 |
| android/sunflower | 無(`assembleDebug`) | 印 | 印 | 對 |
| fdroid(GitLab) | 有(`:app:lint`) | 不印 | 不印 | 對 |
| AuroraStore(GitLab) | 無(只有 `ktlintCheck`,`stage: lint` 名稱誤導) | 不印 | 不印 | 錯(F3,漏報) |
| bitrise-sdk22 | 無(`gradlew assemble`) | 印 | 印 | 對 |
| plaid(CircleCI) | 有(`./gradlew check`) | 不印 | 不印 | 對 |
| appcenter-sample(Azure) | 有(`tasks: 'clean build …'`) | 印 | 不印 | 錯(F1,誤報) |
| wire-android(Jenkinsfile) | 查無 gradle 命令,在共用函式庫裡,無法判 | 印 | 印 | 無法判定 |
| 負例:`needs: build` 加 `cache: gradle` 加 `assembleDebug` | 無 | 印 | 不印 | 對(修好) |
| 負例:GitLab `stage: build` 加 `cache: gradle` | 無 | 印 | 不印 | 對(修好) |
| 負例:只有基準線檔與 `lint {}` 區塊 | 無 | 印 | 不印 | 對(修好) |
| 負例:`npm run lint` 加 `assembleRelease` | 無 | 不印 | 不印 | 錯(F3,漏報) |
| 負例:`ktlintCheck detekt assembleDebug` | 無 | 印 | 印 | 對 |
| 負例:Bitrise `android-build` | 無 | 印 | 印 | 對 |
| 負例:沒有任何 CI | 無 | 印 | 印 | 對 |
| 正例:`lintDebug`、`./gradlew check`、Jenkinsfile 的 `lintRelease`、Jenkinsfile 的 `clean build` | 有 | 不印 | 不印 | 對 |

補充:wire-android 的 Jenkinsfile 是真實檔案,但沒找到公開的 Android 專案 Jenkinsfile 直接寫 gradle 命令,所以 Jenkins 的 gradle 案例只有合成的。

總結:最嚴重是 A1 漏掉 Azure `tasks:`、`gradle-build-action` 的 `arguments:`、CircleCI gradle orb 與 Bitrise `gradle_task:` 這幾種已知欄位寫法,對真實專案誤報而且比舊版退步,會擋 1 條。
