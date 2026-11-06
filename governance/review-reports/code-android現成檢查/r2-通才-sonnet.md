severity: major

這輪我讀完整份 patch 與 r1-intake,跑了 `lint_android_ci`、`catalog_batch4`、`compose_rules` 三組測試(全綠),另外用腳本實測了下面的重現。八個角度各自收齊後去重,留下 6 條。

## F1
severity: major
blocking: 是

A1 現在把 `lint`、`check`、`build` 三個字認成任務字樣,但切詞改成了 `[A-Za-z][\w:-]*`,會把 `/` 和 `.` 也切開。同一行只要有 gradlew,路徑裡的 `build/`、`check.gradle` 就被當成 `build`、`check`,A1 被壓掉。上一版的切詞是用空白與標點切,不會把路徑切開。

實際會中的寫法很常見:`./gradlew assembleDebug && cp app/build/outputs/apk/debug/app-debug.apk out/`。這種 CI 完全沒跑 lint,卻判成已接上,A1 不印。這不是計劃天花板裡列的「`-x lint`、`echo`」那兩種接受的少印。

引句:「            if re.search(r"gradlew|\bgradle\b|\barguments:", ln) and any(」

最小重現(我實跑,回 True,應為 False):
```
m._android_ci_has_lint_task([["- run: ./gradlew assembleDebug && cp app/build/outputs/apk/debug/app-debug.apk out/"]])
```
`--init-script ci/check.gradle` 也回 True。`cd build && ./gradlew assembleDebug` 同樣。

file: `scripts/lumos:39017`

## F2
severity: minor
blocking: 否

A1 的「註解不算」只靠測試裡的 `has()` 重寫了一份讀檔與去註解邏輯來守,沒有走真實路徑。我把 `_lint_android_ci_advisories` 改成餵原文行(不經 `_ci_workflow_texts`),`python3.14 scripts/test_lumos.py -k lint_android_ci` 仍是 80 passed, 0 failed。

所以 `# ./gradlew lintDebug`、`# TODO add lint check later` 這幾個負例沒有守住「真實路徑有去註解」。r1 的 一通2 修的正是這件事,而且這條路徑日後被改走 `_ci_config_texts` 時測試不會紅。專案 CLAUDE.md 〈實作測試〉要求測試不能只是把實作重寫一次。

引句:「        \"\"\"照 lumos 的讀法:每支檔的文字經既有的去註解(整行註解拿掉、行尾註解切掉)再判。\"\"\"」

file: `scripts/test_lumos.py:126263`

## F3
severity: minor
blocking: 否

`_android_build_texts` 的 docstring 與依據表都說「剝掉註解,同 `_kt_build_verdict`」,但 `gradle/libs.versions.toml` 也走了 `_kt_strip_comments`,而 `_strip_c_comments` 只認 C 式 `//` 和 `/* */`,不認 TOML 的 `#`。

我造了 JVM 專案:`build.gradle.kts` 只有 `kotlin("jvm")`,`libs.versions.toml` 裡有一行 `# android-application = { id = "com.android.application" ... }`。`_android_build_texts` 之後 `_KT_BUILD_ANDROID.search` 回 True,被判成 Android,會多印 A1、A2。

引句:「        out.append(_kt_strip_comments(txt, xml=rp.endswith("pom.xml")))」

最小重現:見上,實跑回 True。`rp.endswith("pom.xml")` 在這個函式裡永遠是 False,是死參數。

file: `scripts/lumos:38147`

## F4
severity: minor
blocking: 否

`_ci_config_texts` 改成薄包裝後,只剩 T4 一個呼叫端,而且只用 `github_only=True`,所以 `github_only=False` 那條分支是死碼。docstring 與計劃第 3 條仍寫它是「T4 與 Android 那幾則提醒共用」。計劃正文也還寫「抽一支共用函式 `_ci_config_texts`」,而 A1 實際改走 `_ci_config_paths` 加 `_ci_workflow_texts`。

另一個落差:T4 的 `_detekt_ci_has_typed_task` 仍吃未去註解的原文,A1 吃去註解後的行,但計劃說 A1「跟 T4 同一個形狀」。`# ./gradlew detektDebug` 會讓 T4 判成有接。這是舊行為,但現在兩者口徑不一致。

引句:「def _ci_config_texts(repo_root, github_only=False):」

file: `scripts/lumos:38938`、`scripts/lumos:38951`

## F5
severity: minor
blocking: 否

`t_lint_android_ci_advice` 這輪新增了十幾次 `lint-check` 子程序(A3 八組、具名管道、205 個模組目錄等)。我實跑的結果是 84.9s,上限 180s,測試執行器自己印「餘裕 2x ⚠ 餘裕不足 3 倍」。CI 機器比本機慢時有逾時的風險,本地只改這個測試就先紅。

引句:「    check("r1 折入 A3:一條命令裡兩支都不在 → 只印一則",」

file: `scripts/test_lumos.py:126258`

## F6
severity: minor
blocking: 否

兩個小問題:

- **A1 效率**:A1 現在先讀整份 CI 檔再逐行 `findall` 加 `any()`,沒有大小上限。我合成 62 MB 的 workflow,`_android_ci_has_lint_task` 約 10 秒;r1-intake 寫「50 MB 約 1 秒」,新形狀慢了一個量級,而 `_android_build_texts` 有 1 MB 上限,CI 檔沒有。
- **重用**:`_detekt_plugin_values` 照 `_detekt_command_codes` 的流程又寫了一遍(逐行切、`sh -c` 展開、深度限制),`_detekt_command_codes` 本身已經處理這些。

另外,計劃〈天花板〉第 4 條新寫的「(只是提醒,不擋)」違反專案 CLAUDE.md 鐵則 4:「寫『沒機械守衛 / 只提醒不擋 / 單次量測 / 還沒有 X』這種會過期的話,把那一句本身搬成獨立一行回頭條件」。這一句沒有對應的 `REVISIT:` 行。

引句:「    for lines in lines_per_file:」

file: `scripts/lumos:39017`

總結:最嚴重是 F1(A1 把 gradlew 行上的路徑 `build/` 當成 build 任務,A1 被壓掉),會擋 1 條。

我審查用的暫存目錄 `/private/tmp/lumos-seat-work/code-android現成檢查/通才-sonnet` 已刪除,repo 沒有被我改動。
