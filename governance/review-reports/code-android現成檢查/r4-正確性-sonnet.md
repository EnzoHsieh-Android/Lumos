severity: minor

審查範圍是 r4 修補差異(6793598b1..cd36e5e04)。r3 的四個重現輸入全部修好,沒有發現新的 major 或 blocker。我跑了 `-k t_lint_android_ci_advice`,結果 112 passed、0 failed。

**實驗摘要**
- 在 `/tmp/lumos-seat-work/code-android現成檢查/正確性-sonnet/` 用 `git worktree add old 6793598b1` 取出修補前版本,同一組輸入前後各跑一次,跑完已用字面路徑 `worktree remove --force` 移除。
- 命令格式為「輸入 前 → 後」,`True` 表示找到 lint 跡象(A1 不印):
  - `needs: build` + `cache: gradle` + `./gradlew assemble`:True → False(修好)
  - `- ./gradlew assemble` 下一行 `- check`:True → False(修好)
  - Jenkinsfile 的 `/* sh './gradlew lint' */`:True → False(修好)
  - Azure `tasks: 'check'`:True → False(計劃已把這列為接受的天花板)
  - 外掛路徑 `tools/{p,q}.jar` 的 A3:缺檔 True → False(修好,`${HOME}/nope.jar` 仍判缺)
- 正例照舊判有跡象:
  - `./gradlew lintDebug`
  - 續行 `./gradlew \` 接 `check`
  - `gradle<tab>build`
  - 絕對路徑 `/opt/g/gradlew build`
  - `.\gradlew.bat check`
  - Jenkins `sh "./gradlew check"`
  - Jenkins 的 `sh 'echo http://a'; sh './gradlew lintDebug'`(字串裡的 `//` 沒被當註解)
- 反例照舊判沒跡象:註解裡的 lint、`lintKotlin`、`lintFixDebug`、`needs: build`、`uses: gradle/...` 配 `./build.sh`。
- `_is_gradle_head` 對 `./gradlew`、`gradlew`、`gradle`、`tools/gradlew`、`.\gradlew.bat` 回 True,對 `gradlewx`、`mygradle`、`GRADLEW` 回 False。
- A3 的 `_android_plugin_missing` 在 `_detekt_segment_codes` 與 `_detekt_plugin_values` 換用 `_is_gradle_head` 後行為不變。

**修補三問**
- 原問題都修好(三通1、三通2、三邊1、三邊7、三正5、三安1 都對得上上面的前後比對)。
- 帶進新錯:只有下面 F1,屬覆蓋缺口,不是新迴歸。
- 同形狀別處:
  - `_ci_config_paths` 與 `_android_build_texts` 都已加符號連結略過。
  - `_is_gradle_head` 讓 detekt 判定的 gradle 詞表與 A1 共用同一份。

**圖譜鏡頭**
- `lint-declaration-health.md` 的 WHY 行、`linter精選目錄.md` 的 A1 描述和程式一致。
- 唯一例外是 F1:`with: arguments: build` 這類寫法在這兩篇都沒提。

**驗收條款 S1–S5**
- S1、S2 的新增子句都有對應的程式分支與測試輸入:
  - 續行 `check`、`needs: build`、GitLab `stage: build`、Jenkinsfile 的 `/* */`、符號連結、大括號展開都有。
  - 全是 A1 該印的反例,翻回舊邏輯會紅。
- S3、S4 這輪沒改。
- S5 是 manual,維持原樣。

F1
severity: minor
blocking: 否
標題:GitHub `gradle-build-action`、`setup-gradle` 的 `with: arguments: build` 或 `check` 會被誤判成沒接 lint,多印一則 A1。
引句:「Gradle 的 build 帶 check)。整檔有 gradle 字樣不算——`needs: build`、`stage: build` 跟 `cache: gradle` 湊在一起」
重現(用 r4 版程式實跑):
- 輸入 `- uses: gradle/gradle-build-action@v3\n  with:\n    arguments: build\n`,`_android_ci_lint_evidence` 回 False,A1 會印。
- 輸入 `- uses: gradle/actions/setup-gradle@v4\n  with:\n    arguments: check\n`,同樣回 False。
- 對照:`run: ./gradlew --no-daemon build` 回 True。

原因:這是 GitHub Actions 官方 gradle action 最常見的呼叫形式,`gradle` 在 `uses:` 行、`build` 在 `arguments:` 行,不同邏輯行。計劃天花板只點名 Azure `tasks:` 與 Bitrise `gradle_task:`,漏了這個更常見的形式。

後果:這類專案其實會跑 lint,卻被提醒「可能沒接」,只是提醒、不擋,所以列 minor。測試只涵蓋 `arguments: lintDebug`(靠 lint 任務名認得)。建議至少把 `arguments:` 補進天花板文字;或把 `arguments:` 後面的詞也當 gradle 參數處理。

總結:最嚴重是 F1 的覆蓋缺口(minor),會擋 0 條。
