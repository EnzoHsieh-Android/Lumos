# r1 收貨紀錄(code-人裁殺傷力android)

七席全到(正確性、資源、邊界、通才、合約、架構對齊、資安;皆 sonnet),引句全數錨定 r1-snapshot.patch(資源席 clean 無引句)。
席報告收齊後才一次寫進卷證;收貨前沒動工作目錄。

## 分組(依根因)

| 組 | 根因 | 發現 | 最高 | 處置 |
|---|---|---|---|---|
| G1 | 人裁 run_cmd 檢查自寫一套 Gradle 切詞與選項表,沒重用 detekt 那組;只認 `:` 開頭的模組路徑 | a1(major)、t2、t1、c3、b4 | major | 折:改用 `_detekt_walk_segments`/`_detekt_strip_prefix` 取段、選項表用 `_GRADLE_VALUE_OPTS` 加 `--tests`;`app:test`(含 `:`、不以 `:` 開頭)當相對根專案的模組路徑 |
| G2 | 殺傷力在工作樹最上層跑 run_cmd、合約測試閘在平台根跑,同一條設定兩種執行目錄;計劃叫人加 `cd <平台根> &&` 只顧一邊 | g1(major) | major | 折:`cmd_guard_kill` 改在工作樹裡的平台根跑(同 `_run_bound_tests`);拿掉 `cd` 前綴的教法(訊息、手冊、筆記、計劃) |
| G3 | 檔頭區判定沒照 Kotlin 文法:多行 `@file:` 註記、BOM、區塊註解裡的 import | t3、c2、b1、b2 | minor | 折:照 Kotlin 文法 kotlinFile = shebang? fileAnnotation* packageHeader importList;註解是隱藏記號——註解內的行不算 import、`@file:` 括號跨行跟到閉合、剝 BOM、`package` 後接任何空白 |
| G4 | `--import` 名稱檢查:兩個 `--import` 同名不同套件照收;整字比對沒有測試守 | b3、c4 | minor | 折:同一批 `--import` 名稱重複就拒;補「名稱只是 `--new` 某識別字的一部分」的測試 |
| G5 | 路徑遮罩:家目錄前綴沒對路徑分隔邊界;遮罩順序沒有測試守 | b6、c5 | minor | 折:只在後面接 `/` 或字尾時取代;補 wt 在家目錄底下的測試 |
| G6 | 計劃 S1/S2 條款字面寫「觸發字」,跟〈範圍〉1 與預期值表(名稱不必是觸發字)矛盾 | c1、b5 | minor | 折:改條款字面,對齊範圍 1 |
| G7 | 讀單一資料夾建置檔另寫一份、建置檔名常數另列 | a2、t4 | minor | 折:建置檔名用 `_KT_BUILD_FILES`;讀單一資料夾抽共用或改叫 `_android_build_texts` |
| — | 失敗摘錄原樣進 AI 上下文(推論) | x1 | minor | 放行:單人自用、輸出來自自己的建置,已過 `_kill_esc` 與長度上限;同 lumos 威脅模型「外來文字回顯放行」 |
| — | 失敗摘錄進版控帳,遮罩只涵蓋工作樹與家目錄(推論) | x2 | minor | 放行:既有 `tail` 欄已有同樣暴露面且不遮,`fail_excerpt` 比它多一層遮罩,沒有變糟 |

## 先查世界

- G1 PRIOR-ART:Gradle 命令列任務路徑相對根專案,`app:test` 與 `:app:test` 同義(https://docs.gradle.org/current/userguide/command_line_interface.html#executing_tasks_in_multi_project_builds);切詞用 Python 標準庫 shlex(https://docs.python.org/3/library/shlex.html),專案已有包裝好的 `_detekt_walk_segments`,採用既有,不另寫。
- G2 PRIOR-ART:Gradle 從專案目錄找 settings 檔決定建置(https://docs.gradle.org/current/userguide/build_lifecycle.html#sec:initialization);同一條 run_cmd 兩處執行目錄不同是設定語意不一致,照合約測試閘(先有、推送前每次跑)的語意統一,不另立 `cd` 慣例。
- G3 PRIOR-ART:Kotlin 文法 kotlinFile 規則(https://kotlinlang.org/docs/reference/grammar.html#kotlinFile):`[shebangLine] {NL} {fileAnnotation} packageHeader importList {topLevelObject} EOF`,註解是隱藏記號(https://kotlinlang.org/spec/syntax-and-grammar.html#lexical-grammar,區塊註解可巢狀);照規格定義寫,拿規格的例子當語料。排除:逐行看前綴字串判檔頭(本輪三席各打穿一種)。
- G4、G5、G6、G7:內部一致性與邊界,不涉外部規格;G5 路徑前綴比對照 os.path.commonpath 的分隔邊界語意(https://docs.python.org/3/library/os.path.html#os.path.commonpath)。

## 重現

| id | 重現 | 結果 |
|---|---|---|
| g1 | 合約席給的 `_run_bound_tests` 指令(root=android、run_cmd 前綴 `cd android &&`) | HIT(席報告附輸出);編排者讀 `cmd_guard_kill` 的 `_kill_run(cmd, wt, …)` 與 `_run_bound_tests` 的 `(pentry.root, cmd)` 確認兩處執行目錄不同 |
| a1 | 讀 `_gradle_task_list` 與 `_GRADLE_VALUE_OPTS`/`_detekt_walk_segments` | HIT(兩套並存,前者選項表是後者子集) |
| c3、b4、t1 | 席報告的 `_gradle_blocked_tasks` 實跑 | HIT |
| c2、b1、b2、t3 | 席報告附的函式呼叫 | HIT |
| c4、c5 | 席位在複本改壞、測試照綠 | HIT |
