severity: minor

我先對程式現況實跑,再逐條核對文件和外部出處。實跑結果:

- 用 Python 3.14 在最小 repo 裡跑了 18 種輸入(Azure、gradle action、CircleCI、Bitrise 四個欄位,欄位值結束後的 `build`,Jenkinsfile 註解,檔案與資料夾符號連結在 repo 內外)。A1 的結果全部和計劃〈S1〉的寫法一致。
- `python3.14 scripts/test_lumos.py -k lint_android_ci` 跑完 160 passed、0 failed。
- 提醒標題三處(`run_doctor` 的 warn、`_lint_android_print`、linter 目錄)用語一致,都寫「A1 看 CI 設定檔、A2 看建置檔、A3 看宣告」。
- 舊說法殘留:全文搜「同一邏輯行」「只看建置檔」「整檔」。計劃第 53、147 行、`lint-declaration-health.md` 第 34 行、linter 目錄第 186 行和 `scripts/lumos` 的 docstring 都已補上四個欄位,沒有殘留。計劃第 145 行的「整檔有 gradle 字樣」明寫是 r2 舊模型的歷史,不算殘留。
- 四個 CI 欄位出處打開核對,全部對得上:
  - Azure Gradle 頁:`tasks` 為 Required、Default `build`。
  - gradle-build-action:`arguments` 寫「Gradle command line arguments (supports multi-line input)」,並有棄用訊息。
  - Bitrise:`gradle_task` 標題為「Gradle task to run」。
  - CircleCI orb:`./gradlew << parameters.command >>`,`command` 預設 `build`。
- Slack 發行說明:1.4.0 的「Build against Lint `8.7.0`」、1.4.2 的 31.7.1、1.5.0 的 32.2.1、1.5.5 的 32.3.2 與 AGP lint plugin 9.3.2、1.6.1 的 32.4.1,版本表的邊界和這些一致。

F1
severity: minor
blocking: 否
引句:「1.4.3 的發行說明沒寫建置用 lint 版本(只有一則 PR 標題寫 lint 31.13.2),不列。」
計劃第 44 行、〈依據來源〉和 linter 目錄第 182 行都有這句,「只有一則」不夠精確。
- 1.4.3 發行說明裡還有兩則 PR 標題:「Update dependency com.android.tools.lint:lint-api to v32.2.0」和「Update plugin lint to v9.2.0」。
- 網址:https://github.com/slackhq/compose-lints/releases/tag/1.4.3
- 結論「發行說明沒寫建置用 lint 版本所以不列」仍成立。建議改成「PR 標題裡有 31.13.2 與 32.2.0 兩個數字、互相矛盾」之類的措辭。

F2
severity: minor
blocking: 否
引句:「當代碼審 r4 邊界席的固定語料(15 個公開專案真實 CI 檔的最小節錄加 8 個負例與正例)逐列跑 A1 時」
計劃的 S6、預期值表和〈依據來源〉都寫「15 + 8」。
- file: `scripts/test_lumos.py:126629`,對應的 `_ANDROID_CI_CORPUS` 實際是 15 列真實專案加 7 列負例加 4 列正例,共 26 列。
- 同一支測試的 docstring 還寫著綁 S1,但計劃把它綁在 S6 上。
- 建議把列數改成「15 個公開專案加 11 個負例與正例」,docstring 改指 S6。

F3
severity: minor
blocking: 否
引句:「| S6 | r4 語料:microsoft/appcenter-sampleapp-android、nowinandroid 等 15 個公開專案的 CI 檔節錄 | 各列照人工判定;三列天花板照現行 |」
S6 的條款和預期值表列被插在 S4 與 S5 之間、S1 的列中間,順序亂了。
- 條款順序變成 S1、S2、S3、S4、S6、S5。
- 預期值表的 S6 列夾在兩條 S1 列中間。
- 不影響判讀,但接手的人會以為編號有漏。

總結:最嚴重是 minor,會擋 0 條。
