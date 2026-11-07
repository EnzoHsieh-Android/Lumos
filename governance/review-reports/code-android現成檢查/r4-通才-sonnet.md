severity: minor

這一輪我只找到 4 條 minor,沒有 blocker 或 major。我用 `python3.14` 載入 `scripts/lumos`,在暫存目錄實跑重現了 F1 到 F3,F4 是讀碼推出來的。

八個角度的結論:
- **刪掉的行為:** `_android_lint_config_evidence` 與 `_ANDROID_LINT_CONFIG` 在 repo 內已無呼叫端。計劃與 WHY 行都改成「`lint {}` 與基準線檔不算跡象」,新碼不需要補回。
- **YAML 略過 `//` 開頭行:** 非 Jenkinsfile 的 CI 檔本來就不會有 Groovy 註解,不需要補回。
- **Jenkinsfile 剝註解:** `_strip_c_comments` 對註解裡含 `'`、字串裡含 `//` 的 Jenkinsfile 判得對。
- **CRLF 續行:** 靠 `read_text` 的通用換行已轉成 `\n`,`\` 加 CRLF 的續行實測可接起來。
- **`_is_gradle_head` 換進 `_detekt_segment_codes` 與 `_detekt_plugin_values`:** 判定只多認 Windows 的 `.\gradlew.bat`,其餘跟原本的 `basename` 比對相同。
- **`_strip_c_comments` 的其他呼叫者:** 它的簽章與預設行為沒動。

F1
severity: minor
blocking: 否
引句:「整檔有 gradle 字樣不算——`needs: build`、`stage: build` 跟 `cache: gradle` 湊在一起」
`check`、`build` 改成必須跟 gradle 呼叫詞同一邏輯行後,兩種常見寫法會被判成沒接,A1 誤印。
- 重現一:`- uses: gradle/gradle-build-action@v2` 搭配 `with:` 下 `arguments: build`,`_android_ci_lint_evidence` 回 False(r2 版會回 True)。
- 重現二:`task: [check, test]` 加 `./gradlew ${{ matrix.task }}`,回 False。
- 計劃天花板只列了 Azure 的 `tasks:` 與 Bitrise 的 `gradle_task:`,沒列這兩種;測試正例也只用了 `[lint, test]` 的矩陣。
- 影響:只會多印一則提醒,不改退出碼。要補的話至少把這兩種寫進天花板。

F2
severity: minor
blocking: 否
引句:「檔案本身是符號連結的略過(不跟著讀到 repo 外,代碼審 r3 資安席)」
資安修補只擋檔案本身是連結,上層資料夾是連結照樣讀得到 repo 外。
- 重現:`.circleci` 是指向外部資料夾的連結,`_ci_config_paths` 仍列出 `.circleci/config.yml`。
- 重現:`.github/workflows` 是連結,也照列裡面的檔。
- `_android_build_texts` 用 `followlinks=False`,不會進連結資料夾,兩邊口徑不一致。
- 計劃只寫「本身是符號連結的一律略過」,文字沒說謊,但 r3 資安席要擋的「讀到 repo 外」沒完全擋住。

F3
severity: minor
blocking: 否
引句:「`_CI_OTHER_CONFIG_FILES` 裡存在的一般檔;檔案本身是符號連結的略過」
`_ci_config_paths` 是 T4 與 A1 共用的,連結一律略過,也讓 repo 內合法的連結被略過。
- 重現:`.github/workflows/ci.yml` 是指向 `../../ci/real.yml` 的 repo 內連結,內容有 `./gradlew detektDebug`,`_detekt_ci_has_typed_task` 回 False(原本回 True),T4 會誤印「型別規則哪裡都沒擋」。
- S1 條款寫「T4 應照舊只看 `.github/workflows/`」,測試沒蓋連結案例。
- `_android_build_texts` 略過連結建置檔也有同形風險:被連結的 `build.gradle.kts` 不會被認成 Android 專案。
- 可考慮只略過解析後落在 repo 外的連結。

F4
severity: minor
blocking: 否
引句:「②同一邏輯行裡有 gradle 呼叫詞(`_is_gradle_head`)而且有一個詞是 `check` 或 `build`」
鑑別力還有缺口:同一行只要有 gradle 呼叫詞和 `check` 或 `build`,不管它是不是被執行的任務都算跡象。
- 讀碼推出(未實跑):`./gradlew assembleDebug -x check`、`./gradlew assemble && cd build` 都會被當成有跡象,A1 少印。
- `-x lint` 的同類情形已列入天花板,`-x check` 與 `cd build` 沒列。
- 因為只是少印提醒,我把它放最後,不用改程式,補一句天花板即可。

總結:最嚴重是 minor,共 4 條(F1 到 F4),會擋 0 條。
