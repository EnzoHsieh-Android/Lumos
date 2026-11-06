severity: major

## Findings

### F1 `command:` 欄位被當成 gradle 任務列,非 gradle 步驟裡的 build/check 會讓 A1 漏報
severity: major
blocking: 是

引句:「CircleCI gradle orb 的 command、Bitrise gradle-runner 的 gradle_task(出處見計劃〈依據來源〉;代碼審 r4 四席)。」

新正規式 `_CI_GRADLE_TASK_FIELD` 把任何 `command:` 的值都當 gradle 任務列。`command:` 是 CircleCI `run`、GitHub Actions 的 `with:`(cargo、docker 等)、Buildkite 等通用欄位,不限 gradle。值裡只要有一個詞剛好是 `build` 或 `check`,就判成「有跑 Android Lint 的跡象」,A1 提醒被吞掉。

重現,每組都是 Android 專案加 `./gradlew assembleDebug`,沒有任何 lint。程式端的行為:

- CircleCI:`- run:` 底下 `command: npm run build`
  - 預期印 A1,實際不印。
- GitHub Actions:`with:` 底下 `command: build`
  - 預期印 A1,實際不印。
- GitHub Actions:`actions-rs/cargo@v1` 加 `with:` `command: check`
  - 預期印 A1,實際不印。
- CircleCI:`command: |` 區塊裡有 `docker build .` 加 `./gradlew assembleDebug`
  - 預期印 A1,實際不印。
  - 這條連區塊內的詞都算,所以非 gradle 行也被吞。
- 同一組合再加 `command: make check`
  - 實際不印。

修補前同樣輸入會印 A1,所以這是第四輪修補新造成的漏報。建議 `command` 要求值本身帶 gradle 呼叫詞,或限定在 CircleCI 的 gradle orb 上下文。`arguments`、`tasks`、`gradle_task` 名稱專屬度高,可以留著。

### F2 Buildkite 和 `.buildkite` 不在 CI 設定檔清單
severity: minor
blocking: 否

- `_CI_OTHER_CONFIG_FILES` 沒有 `.buildkite/pipeline.yml`。
- 真實語料 WordPress-Android 的 lint 寫在 `.buildkite/commands/lint.sh`,pipeline 裡只有 `command: ".buildkite/commands/lint.sh wordpress"`(label 是 `Lint WordPress`)。
- 這屬於「只看已知名字」的計劃天花板,A1 對這類專案本來就看不到。
- 所以我只降成 minor 並記一筆,不要求修。

### F3 Jenkinsfile 原樣未誤判(正面確認)
severity: minor
blocking: 否

`_ci_workflow_texts` 對 Jenkinsfile 改走 Groovy 註解剝除。我測了 6 種寫法,都符合預期:

- 註解裡的 `lint` 不算。
- 字串裡的 `#` 與 `//` 不誤剝。
- `/*` 沒有結尾時不崩。
- `#` 開頭的行照樣讀。

這條只是記錄,沒有缺陷。

## 新欄位邊界(21 個合成案例)

符合預期的:

- `tasks: $(gradleTasks)`:印(沒有 build/check 詞,正確)。
- `arguments: ${{ matrix.args }}`:印。
- `subtasks:`、`my-tasks:`、`x_arguments:`:印,欄位名子字串不誤認。
- `tasks:` 的清單寫法、`arguments: |` 區塊、`tasks: [clean, build]`、`tasks: "build"`:不印。
- `gradle_task: check`、`gradle_task: |-` 區塊:不印。
- CRLF 的 `arguments: build`:不印。
- 欄位值結束後的 `name: build`、`workflows:` 底下的 `build:`:印,狀態有收回。

不符合預期的只有 F1 那 4 個案例。

另外兩個我標「?」的案例:
- `arguments:` 後面接 `- name: build`(畸形):不印。
- 用 tab 縮排:不印,YAML 本來就不合法。

兩者罕見,不算 finding。

## 符號連結

全部不崩、結果合理:

- 資料夾連結指向 repo 內:照讀,不印。
- 檔案連結指向 repo 內:不印。
- 連結鏈(3 層):照讀。
- 兩檔互指的迴圈、自指的 `.gitlab-ci.yml`:印,不崩。
- `.github/workflows` 指到 repo 根、`Jenkinsfile` 指到 `.`:印,不崩。
- 指到 repo 外的資料夾:印,不讀外面。
- 子資料夾 `up` 連回上層:不印,沒有無限遞迴。
- 60 層連結鏈:印,Linux 的 ELOOP 當成不在 repo 內。
- 每個案例約 0.8 秒,沒有效能問題。

## 擴大語料(上一輪沒用過的 10 個以上)

| 專案 | 人工判定 | A1 | 對錯 |
|---|---|---|---|
| AntennaPod | 有(`./gradlew checkstyle lint`) | 不印 | 對 |
| duckduckgo/Android | 有(`./gradlew lint`) | 不印 | 對 |
| home-assistant/android | 有(`./gradlew lint --continue`) | 不印 | 對 |
| AnkiDroid | 有(Run Lint Debug) | 不印 | 對 |
| nowinandroid(Build.yaml) | 有(`:app:lintProdRelease`) | 不印 | 對(上輪用過,這是換檔再驗) |
| square/okhttp | 有(`android-test-app:lint`) | 不印 | 對 |
| chrisbanes/tivi | 有(`./gradlew check \` 續行) | 不印 | 對 |
| cashapp/paparazzi | 有(`./gradlew check`) | 不印 | 對 |
| skydoves/Pokedex | 有(`./gradlew build`) | 不印 | 對 |
| android/platform-samples | 有(`lintDebug`) | 不印 | 對 |
| element-x-android | 無(`assembleGplayDebug`,`compileGplayNightlySources`) | 印 | 對 |
| bitwarden/android | 無(只有 assemble、bundle) | 印 | 對 |
| skydoves/pokedex-compose | 無(`spotlessCheck` 加 `assembleDebug`) | 印 | 對 |
| mihon | 無(`spotlessCheck`、`testDebugUnitTest`、`assembleRelease`) | 印 | 對 |
| android/socialite | 無(`spotlessCheck` 加 `assembleDebug`) | 印 | 對 |
| Azure `Gradle@2` 範本(`tasks: 'build'`) | 有 | 不印 | 對 |
| microsoft/appcenter-sampleapp-android(`tasks: 'clean build …'`) | 有 | 不印 | 對(上輪是誤報,已修好) |
| Bitrise Android 範例(`android-lint@0`) | 有 | 不印 | 對 |
| bitrise-io/sample-apps-android-sdk22 | 無(`assemble`) | 印 | 對 |
| wordpress-mobile/WordPress-Android(Buildkite) | 有(`lint.sh`) | 見 F2 | 天花板 |

我試抓的 CircleCI Android orb 專案多半 404,抓到的 `android-orb` repo 本身不是 Android 專案,不計。真實語料裡沒有找到 `with: arguments:` 多行寫法的專案,這部分只做了合成測試。

臨時目錄 `/private/tmp/lumos-seat-work/code-android現成檢查/邊界-sonnet` 已刪除。

總結:最嚴重是 F1(`command:` 欄位把非 gradle 步驟的 build/check 當成 lint 跡象,A1 漏報),會擋 1 條。語料表 20 個專案全對,符號連結全數通過,F2 屬計劃天花板。
