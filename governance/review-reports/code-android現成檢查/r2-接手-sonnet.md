severity: major

審查材料是 `r2-repair.patch`。repo 在 `7742e4bd6`,工作樹沒有被我改動。本機有跑的有:新下載指令好壞雜湊各一次、`lint-check` 實跑、`t_kt_catalog_batch4_wiring`(13 條全過)。網址部分,13 個網址全部打得開並逐一核對內文。「6 個公開專案實跑」那條因審查席不能對外連 GitHub API 而沒重跑。

**文件對程式(鏡頭 1)**
- 下載指令:好雜湊時印 `...jar.part: OK`,jar 改名到正式檔名。壞雜湊時印 `FAILED`,結尾是「下載或雜湊比對失敗,沒有裝」,rc=1,目錄裡沒留任何檔。linter 目錄寫的行為與實跑一致。
- A3 的說法對得上程式:只印「第幾條」、不回顯檔名,`$HOME`、`~`、相對路徑都能展開。
- A1 的說法對不上,見 F1、F2。

F1
severity: major
blocking: 是
引句:「不解析命令:續行、多行區塊、矩陣變數因此都自然涵蓋;」
說明:`lint`、`check`、`build` 只在含 gradlew、gradle 或 `arguments:` 的那一行才算。續行或多行區塊裡單獨一行的 `lint`,不在那一行上,A1 會誤報「沒接」。這正是上一輪 `一通1` 的同一族(已接卻判沒接),只修了 `lint<變體>`,沒修三個常見字。
重現(`setup-gradle` 官方 `arguments: |` 寫法,已實跑):
1. 在臨時 Android repo 放 `.github/workflows/ci.yml`,內容是 `arguments: |` 底下兩行 `assembleDebug`、`lint`。
2. 宣告 kt 棧後跑 `lumos lint-check --repo <repo>`,仍印 `[CI] A1:...`。
3. 同樣是 False 的單元層案例:`run: |\n  ./gradlew \\\n    check\n`、`matrix:\n  task: [lint, test]`。
4. 測試只覆蓋 `lintDebug` 這類帶變體名的寫法。
5. 計劃天花板與 linter 目錄都沒提這一類。
file: `scripts/lumos:39022`

F2
severity: minor
blocking: 否
引句:「只在提到 gradlew、gradle 或 `arguments:` 的行上才算」
說明:程式用 `[A-Za-z][\w:-]*` 切詞,點號會把詞切斷。結果 `./gradlew assembleDebug -Dkotlin.build.report.output=f` 和 `-Pci.check=true` 都判成「找到」,`name: cache gradle build output` 也算。文件只說「一個詞剛好是」,沒交代這個誤判方向(少印提醒,不擋)。已實跑:這三種都回 True。
file: `scripts/lumos:39020`

**〈依據來源〉逐行核對(鏡頭 2)**

F3
severity: minor
blocking: 否
引句:「A1 只看字面找字(不解析命令) | OpenSSF Scorecard 判 CI 有沒有跑靜態分析只認簡單字面證據」
說明:出處 `ossf/scorecard#5103` 是已關閉、沒合併的 PR(被 stale bot 關掉),內容是新增 Semgrep、Bandit、gosec 的偵測。作者的論點是「沒偵測到是 false negative、要補」,只有一句「`uses:` 範圍小、false-positive 風險低」。它不支撐「承認判不到不代表沒做」,這句要靠 xygeni 的頁面(內文有 Small Print),但計劃那一列沒列 xygeni。A1 是任意位置找字,跟 Scorecard 的錨定 `uses:` 也不同形。這是旁證,不是依據。
網址:https://github.com/ossf/scorecard/pull/5103

F4
severity: minor
blocking: 否
引句:「kotlinter 外掛的任務名;AGP 的 lintFix 改檔、lintVital 只看 fatal、後兩者是 lint 任務的中間步驟」
說明:`lintFix`、`lintAnalyze`、`lintReport` 在所列四個網址(kotlinter README、lint 頁、DSL 參考頁、AOSP 提交)裡一個都找不到。`lintVital` 只出現在 AOSP 提交的程式碼裡;DSL 頁只有 `checkReleaseBuilds` 屬性。「改檔」「中間步驟」的說法沒有出處。

F5
severity: minor
blocking: 否
引句:「AGP 9.3 以上用 1.6.1;AGP 8.x 用 1.4.2(用 lint 31.7.1 建)」
說明:同一列自己的規則是「挑建置用 lint 版本不高於 AGP 加 23 的」。發行說明寫 1.6.1 用 lint 32.4.1 建,對應 AGP 9.4.1,而 AGP 9.3 對應 lint 32.3。1.5.5 才是 32.3.2。依規則,AGP 9.3.x 該挑 1.5.5,不是 1.6.1。「1.6.0 requires AGP/lint 9.3+」那句在發行說明裡緊跟著「Reclassify ComposeModifierComposed as a PERFORMANCE issue」,更像只指那項變更。「AGP 8.x 用 1.4.2」依同一規則其實要 AGP 8.7 以上。「lint = AGP + 23」這個公式,安裝頁和發行說明都沒寫。未能重現(沒有實際用 AGP 9.3 載入 1.6.1),所以自降為 minor。
網址:https://github.com/slackhq/compose-lints/releases

F6
severity: minor
blocking: 否
引句:「2026-11-06 本機 detekt 1.23.8 加外掛 0.4.28 實跑壞例,四條規則都報 | https://mrmans0n.github.io/compose-rules/detekt/ ;代碼審卷證 governance/review-reports/code-android現成檢查/」
說明:代碼審卷證目錄裡只有 patch,沒有那次實跑的記錄。「四條規則都報」實際在設計審卷證 `governance/review-reports/android現成檢查接上ci與推送前/r1-正確性-sonnet.md` 第 9 行。另外,「不用型別資訊」是實跑結論,官方 detekt 頁沒寫。
說明二(同一類):「A1 換形狀後的實測」那列,出處 `r1-intake.md` 只有專案名與判定,`lintProdRelease`、`lintGplayDebug`、`lintContinuous` 這些任務字串在任何卷證裡都沒有(只出現在計劃本身)。我沒能重跑,所以這些任務字串無從驗證。

**文件對文件(鏡頭 3)**

F7
severity: major
blocking: 是
引句:「改由一次性腳本依這個口徑判,不手改;腳本不進 repo,口徑寫進型錄〈輸入與口徑〉通電批次那一條,值清單同步加這三個字樣;S4 的測試照同一口徑重算一次、跟型錄比對。」
說明:計劃範圍 4 這句跟現況相反。口徑現在住在 repo 內的 `configs/ast-grep/kotlin-android/check.py` 的 `batch4_expected_tags`。S4 測試是呼叫 check.py,不再自己重算。同一句還寫「以 `androidx`、`內建`、`slack` 開頭」,漏了這輪補的 `Android Lint:`。已用 grep 確認,代碼審的修補沒有動這一段計劃文字。
file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:57`

F8
severity: minor
blocking: 否
引句:「讀 CI 設定檔抽一支共用函式 `_ci_config_texts(repo_root)`(新增,T4 的 `_detekt_ci_has_typed_task` 改用它」
說明:計劃範圍 3 的這一段有四處變假。
- `_ci_config_texts` 現在只有 T4 用;A1 改走 `_ci_config_paths` 加 `_ci_workflow_texts`。
- 同段「條目格式 `[CI] A1:<一句>`」,現在 A3 是 `[kt 第 N 條] A3:`。
- A3 那條「(展開 `$HOME`)」,現在是 `expandvars` 加 `expanduser`、相對路徑對 repo 根。
- 「掃建置檔」那條只列了 `build/`、`.gradle/`、`node_modules/`,現在是 `_stack_scan_skip`(多了 `Pods`、`vendor`、`dist`、`target`、`governance`、`DerivedData`、`*-knowledge` 等)。
file: `docs/lumos-toolchain-knowledge/Projects/Android現成檢查接上CI與推送前_計劃.md:52`

F9
severity: minor
blocking: 否
引句:「字樣的判法跟 T4 找 `detekt<變體>` 同一個形狀,只看字面、不解析命令」
說明:T4 的 `_detekt_ci_has_typed_task` 讀的是未去註解的原文,被註解掉的 `# ./gradlew detektDebug` 也算。A1 先經 `_ci_workflow_texts` 去註解。linter 目錄的「跟 T4 一樣只看字面找字」同樣會讓人以為兩邊註解處理一樣。

**圖譜鏡頭(鏡頭 4)**
範圍算不出來,所以我改讀 `lint-declaration-health.md`、`linter精選目錄.md`、`kotlin規則包.md`、`Issues/工具鏈範圍外手法紀錄.md`。
- `lint-declaration-health` 和 `kotlin規則包` 新改的摘要行跟程式對得上,`--catalog-only` 實跑回「型錄問題 0 個」。
- `Issues/工具鏈範圍外手法紀錄.md` 有一條對不上,見 F10。

F10
severity: minor
blocking: 否
引句:「| 2026-11-06 | code-android現成檢查 r1 | shell 殘留測試用環境變數讓外掛測試改載入別支 jar | compose-rules 外掛測試找檔順序 | 無(測試設定,沒有保護說法) |」
說明:同一篇「現在怎麼繞」最後一句寫「判不出是刻意設定還是照常操作殘留的(例:shell 裡留著的 `LUMOS_SKIP_*`),當範圍內的第 ③ 類處置,不記在這裡」。這一列自己寫的手法就是「shell 殘留」,不是刻意偽造,依該篇規則不該記在這裡。

總結:最嚴重是 major(A1 對多行區塊和續行裡單獨的 `lint`、`check` 誤報、計劃範圍 4 與現況相反),會擋 2 條。
