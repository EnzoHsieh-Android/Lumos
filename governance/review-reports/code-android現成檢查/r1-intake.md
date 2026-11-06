# r1 收貨紀錄(code-android現成檢查)

## 收貨

- 第 1 輪,high(`pitfalls --diff 87c825676..cafcd3ece` 判定:命中資源型樣 `open(`)。整份凍結 patch 2445 行,拆甲(程式、CI、設定 401 行)、乙(測試 341 行)、丙(文件、型錄、筆記 845 行);正確性、資源、邊界、通才看甲乙(742 行),接手、架構對齊看甲丙(1246 行),資安看整份(2445 行,照規矩不拆)。七席全 sonnet;外家預設不派,結論照實寫成「單家族視角下」。
- 本機 main 停在舊提交,派工鏡頭算不出範圍;派工詞改點名 Systems/lint-declaration-health、linter精選目錄、kotlin規則包、bound-tests-gate、pitfalls-code-loop 讓席位自己讀。
- 七席交回後一次從逐字稿存檔。正確性、邊界、接手、架構對齊四席的結尾總結行被格式檢查當成多一行 severity 宣告,退回原席只改那一行重交(其餘一字不改),重存後七份都是正規化格式;quote-check 七份全錨、refcheck 全 ok。
- 席位沒有改 repo:`git status` 只有本輪卷證與治理帳;審查席臨時目錄存完報告後已刪。
- manifest 原本 3694 條是改到的兩支大檔整檔 ruff 舊告警(新增告警閘比對過這次新增 0 條),派工時只留內建風險型樣 1 條(`r1-manifest-builtin.json`);七席都判那條 `open(` 是誤報(有 with)。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 一通1 | 通才 F1、邊界 F1、正確性 F3 | `_android_ci_has_lint_task(["run: \|\n  ./gradlew assembleDebug \\\n    lintDebug\n"])` | HIT:回 False(已接卻判沒接) |
| 一通2 | 通才 F2、邊界 F2、正確性 F2、接手 F2 | 同函式對 `# ./gradlew lintDebug`、`./gradlew build -x lint` | HIT:回 True |
| 一通3 | 通才 F3、正確性 F1、F4、邊界 F3 | `_android_plugin_paths("detekt --plugins $RUNNER_TEMP/x.jar")`;相對路徑從 cwd=/ 跑 lint-check | HIT:原樣回傳、誤印 A3 |
| 一接1 | 接手 F1 | detekt 1.23.8 加共用設定跑 `const val MAX_ITEMS = 5` | HIT:報 TopLevelPropertyNaming |
| 一邊5 | 邊界 F5 | 數型錄現成規則欄寫 `Android Lint:` 的第四批列 | HIT:19 列沒被標 |
| 一架5–一架9 | 架構 F5–F9 | grep 既有 `_detekt_split_segments`、`_kt_strip_comments`、`_stack_scan_skip`、`_lint_run_and_parse`、check.py `catalog_problems` | HIT:都已存在,新碼另起一套 |
| 一資1 | 資源 F1 | 根目錄放 `mkfifo build.gradle` 跑 lint-check | HIT:卡住 |
| 一安2 | 資安 F2 | 範本下載指令雜湊不符時 | HIT:jar 留在正式位置 |

refuted: none

## 先查世界

- PRIOR-ART: A1 判「CI 有沒有跑 lint」——設計審 r1 與這輪連兩次被字面寫法打穿(續行、註解、`-x`、echo、變體名),照「同類字面判斷第二次被打穿就換形狀」查業界:OpenSSF Scorecard 的 SAST 檢查判 CI 有沒有跑靜態分析,只認 workflow 裡 `uses:` 這種簡單字面證據,PR 作者明說是為了壓低誤報,第三方說明也寫判不到不代表專案沒做(https://github.com/ossf/scorecard/pull/5103 、https://detectors.xygeni.io/xydocs/compliance/checkpoints/openssf_scorecard/sast_in_use.html )。專案鄰居 T4 找 `detekt<變體>` 也是整份檔找字。採用:A1 改成找字(去註解後 `lint<變體>` 任何地方都算;`lint`、`check`、`build` 只在 gradle 那行算),不解析命令;寫了卻沒跑判成有接,寧可少印、不誤報。排除:逐條模擬 Gradle 命令列(這輪實作過,七條寫法各要一個特例,又被四席打穿)。
- 實驗:換形狀後下載 6 個公開 Android 專案的 workflow 實跑——nowinandroid、thunderbird、element-x、NewPipe 判有接,architecture-samples(只有 connectedCheck)判沒接,都對;firefox-android 的 CI 在 Taskcluster,判沒接、多印提醒,寫進天花板。
- PRIOR-ART: A3 路徑展開——Python `os.path.expandvars` 照 shell 規則展開、沒設的變數原樣保留(https://docs.python.org/3/library/os.path.html#os.path.expandvars );新增告警閘以 repo 根當工作目錄經 shell 執行(`_lint_spawn`)。採用,沒設的變數判不了就不印。
- PRIOR-ART: Compose 專案的 detekt 常數命名——detekt 預設 `constantPattern` 是 `[A-Z][_A-Z0-9]*`(Kotlin 慣例全大寫加底線),Compose 指引要 PascalCase;兩種都收,樣式加底線。
- PRIOR-ART: kotlinter 任務名——README 寫 `lintKotlin`、`lintKotlin<SourceSet>`(https://github.com/jeremymailen/kotlinter-gradle ),排除名單照收。
- 其餘(重用既有函式、具名管道、文件位置)是專案內一致性與 Python 檔案語意,不需業界查。

## 歸因

- 第一輪,沒有上一輪修補可回歸。

## 逐條去向(37 條全折,0 放行,0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 一通1、一通2、一邊1、一邊2、一正2、一正3、一接2 | 通才 F1、F2,邊界 F1、F2,正確性 F2、F3,接手 F2 | 折:A1 換形狀成找字(見先查世界),測試釘已接、找不到、天花板三組 |
| 一通3、一通5、一通6、一正1、一正4、一邊3、一架2、一架5、一架6、一安1 | 通才 F3、F5、F6,正確性 F1、F4,邊界 F3,架構 F2、F5、F6,資安 F1 | 折:A3 改用 detekt 判定的切段與 `sh -c` 展開、`expandvars` 加 `expanduser`、相對 repo 根、沒設的變數不判、一條只印一則、標 `[kt 第 N 條]` 不回顯檔名;測試補 $HOME、${HOME}、~、其他變數、相對路徑、sh -c、等號寫法 |
| 一通4、一資1、一資2、一架7、一架4、一邊4、一正5 | 通才 F4,資源 F1、F2,架構 F7、F4,邊界 F4,正確性 F5 | 折:建置檔掃描沿用 `_stack_scan_skip` 加隱藏資料夾、`_kt_strip_comments` 剝註解、只開一般檔、依層數排序根目錄先讀;build-logic 的 .kt 看不到寫進天花板;測試補跳過名單、註解、具名管道、排序、隱藏資料夾、符號連結、toml、settings、1 MB、四種 CI 檔 |
| 一資3 | 資源 F3 | 折:CI 設定檔改走既有 `_ci_workflow_texts`(同一套讀法),大檔情況實測 50 MB 約 1 秒、真實 CI 檔遠小於此,記在本列不另設上限 |
| 一架8 | 架構 F8 | 折:S3 改照 linter 目錄範本那兩行原文經 `_lint_run_and_parse` 跑,拿掉測試裡另寫的 SARIF 解析 |
| 一架9、一邊5 | 架構 F9,邊界 F5 | 折:口徑搬進 check.py 的 `batch4_expected_tags`,`catalog_problems` 逐列比對;補 `Android Lint:` 前綴,型錄補標 19 列;測試改呼叫 check.py 並用變異副本驗自檢抓得到 |
| 一架1、一架3 | 架構 F1、F3 | 折:輸出照 `_ANDROID_ADVICE_ORDER` 排序;健檢那則套 20 條上限 |
| 一接1 | 接手 F1 | 折:`constantPattern` 改 `[A-Z][A-Za-z0-9_]*`,S3 補全大寫加底線常數 |
| 一接3、一接4、一接5、一安2 | 接手 F3、F4、F5,資安 F2 | 折:linter 目錄改「兩套」並提 A3;章節移到 detekt 三條說明之後;下載改 curl、先存暫存檔、雜湊對了才改名、不對就刪並回報失敗(實跑好壞雜湊各一次) |
| 一通7 | 通才 F7 | 折:`--json` 的 advisories 照舊是字串清單,A 系列條目有固定前綴可分;在 lint-declaration-health 的 WHY 行記明兩種提醒共用同一個清單 |
| 一安3 | 資安 F3 | 折(範圍外):測試讀 `LUMOS_DETEKT_COMPOSE_JAR` 是刻意的測試設定;在 Issues/工具鏈範圍外手法紀錄記一行 |
