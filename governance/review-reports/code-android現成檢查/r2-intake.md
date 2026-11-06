# r2 收貨紀錄(code-android現成檢查)

## 收貨

- 第 2 輪,high,修訂輪。七席(正確性、資源、邊界、接手、通才、架構對齊、資安,全 sonnet)看本輪修補差異 r2-repair.patch(cafcd3ece..7742e4bd6,1198 行,sha256 ac7036ae…);資安看整份 r2-snapshot.patch(1918 行,sha256 f2dc541c…,不含卷證與帳本)。外家預設不派,結論寫成「單家族視角下」。
- 七份從逐字稿存檔,都是正規化格式(這輪派工詞寫明總結行不寫 severity,沒再退件)。quote-check:通才 6 句有 1 句錨不到,不採信,所屬那條另有實跑重現照採;其餘全錨。refcheck 全 ok。
- 席位沒有改 repo;審查席臨時目錄存完報告後已刪。
- 修正關卡:r1 的修正紀錄 r1-fix.json 補 note 後 `loop fix-check --round r1` 全部通過(266 秒)。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 二通1 | 通才 F1、正確性 F1 | `_android_ci_has_lint_task` 對 `./gradlew assembleDebug && cp app/build/outputs/apk/debug/app-debug.apk out/` | HIT:回 True(路徑裡的 build 被當任務) |
| 二邊1 | 邊界 F1 | Bitrise `gradle_task: lint`、Azure `task: Gradle@3` 加 `tasks: check` | HIT:回 False(有跑卻判沒有) |
| 二接1 | 接手 F1、邊界 F2 | `arguments: \|` 區塊裡單獨一行 `lint`;續行上單獨的 `check` | HIT:回 False |
| 二架1 | 架構 F1、通才 F2 | 把 A1 改成讀原文不去註解,`-k lint_android_ci` 照綠 | HIT(通才席實跑) |
| 二架2 | 架構 F2 | `grep -n "def _ktpack\b" scripts/test_lumos.py` | HIT:既有載入函式已存在 |
| 二正3 | 正確性 F3、通才 F3、邊界 F6 | toml 裡 `# android-application = …` | HIT:被判成 Android |
| 二邊5 | 邊界 F5、正確性 F2 | `--plugins \`echo $HOME/x.jar\``、`d/*.jar` | HIT:誤印 A3 |
| 二資0 | 資源席 | 50 MB CI 檔走 `_ci_workflow_texts` | 量到 8.4 秒(r1 收貨紀錄寫「約 1 秒」不對,在此更正;真實 CI 檔小數個量級) |

refuted: none

## 先查世界

- PRIOR-ART: A1 同一類(「CI 有沒有跑 lint」的字面判斷)第三次被打穿(設計審 r1、代碼審 r1 逐條解析命令、這輪「找字但限 gradle 那行」),照第三次規則先查業界正式做法:OpenSSF Scorecard 官方檢查文件 SAST「looks for known GitHub apps … or the use of github/codeql-action」並寫「it is challenging for an automated tool like Scorecard to detect them all」「A low score is therefore not a definitive indication」;CI-Tests 同樣只認一組已知名字(https://github.com/ossf/scorecard/blob/main/docs/checks.md )。上一輪引的 PR #5103 是被 stale bot 關掉的 PR,只算旁證,依據改指官方文件。採用:判斷題從「有沒有接」換成「找不到任何跡象才提醒」,跡象三種(lint 任務名、提到 gradle 的檔裡的 check/build、建置檔的 lint 區塊或基準線檔),提醒措辭不下定論。排除:任何「判斷有沒有接」的字面規則(三輪各被打穿一次)。
- 實驗:證據模型對 6 個公開專案實跑(r2-ciexp.md),判對 5 個,firefox-android(Taskcluster)屬天花板;Bitrise、Azure、續行、矩陣、路徑、`-D` 屬性各一例進測試。
- PRIOR-ART: lint 任務名出處——kotlinter README(`lintKotlin`)、Android lint 使用指南(`lintFix` 套用修正、`updateLintBaseline`)、DSL 參考頁 `checkReleaseBuilds`(lintVital 只看 fatal)。`lintAnalyze`、`lintReport` 找不到官方出處,從排除名單拿掉(寧可多算跡象)。
- PRIOR-ART: Slack 外掛版本——1.5.5 發行說明同時寫「Build against lint 32.3.2」「AGP lint plugin 9.3.2」,是 lint = AGP + 23 的直接證據;版本表照這條改:AGP 9.4+ 用 1.6.1、9.3 用 1.5.5、8.7–8.x 用 1.4.2(https://github.com/slackhq/compose-lints/releases )。

## 歸因

- 上一輪修補造成的(regression):二通1、二正1(切詞改成連 `/` 都切)、二邊1、二邊2、二接1(找字只認 gradle 那行)、二架1、二通2(測試重寫去註解)、二架2(測試另寫載入函式)、二架4(走訪器第三份複本)、二正2(A3 改寫後沒處理反引號)。
- 其餘是上一輪沒人看的角落或文件沒跟上。

## 逐條去向(34 條全折,0 放行,0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 二通1、二正1、二邊1、二邊2、二邊4、二接1、二接2 | 通才 F1,正確性 F1,邊界 F1、F2、F4,接手 F1、F2 | 折:A1 換成證據模型(見先查世界),切詞不切 `/`、`.`;測試補 Bitrise、Azure、續行、多行區塊、矩陣、路徑、`-D` 屬性、`--init-script` |
| 二邊3 | 邊界 F3 | 折:A1 略過 `//` 開頭的行(Jenkinsfile 的 Groovy 註解),測試補一例 |
| 二架1、二通2 | 架構 F1,通才 F2 | 折:測試寫暫存 CI 檔、經既有 `_ci_workflow_texts` 再判,不再自己去註解 |
| 二架2、二架5 | 架構 F2、F5 | 折:改用既有 `_ktpack()` 與 `_ktpack(copy=True)` 複本,刪掉新寫的載入函式與手動換 CATALOG |
| 二架3、二通4、二正4、二接9 | 架構 F3,通才 F4,正確性 F4,接手 F9 | 折:刪掉 `_ci_config_texts`,T4 直接走 `_ci_config_paths` 讀原文;計劃與 linter 目錄寫明 T4 讀原文、A1 去註解,不再說兩者同形 |
| 二架4、二通6 | 架構 F4,通才 F6 | 折:抽 `_detekt_walk_segments`,detekt 判定與 A3 共用;天花板那句補 REVISIT;CI 大檔耗時以實測數字更正於本紀錄 |
| 二正3、二通3、二邊6 | 正確性 F3,通才 F3,邊界 F6 | 折:版本目錄照 TOML 的 # 剝;模組放在跳過名單資料夾的情況寫進天花板 2 |
| 二正2、二邊5 | 正確性 F2,邊界 F5 | 折:A3 含反引號、萬用字元的值判不了、不算 |
| 二正5、二接7、二接8 | 正確性 F5,接手 F7、F8 | 折:計劃範圍 3、範圍 4 改成現況(口徑住在 check.py、A3 寫法、跳過名單) |
| 二接3、二接4、二接5、二接6 | 接手 F3–F6 | 折:依據來源換成 Scorecard 官方文件、lint 任務名官方出處、Slack 版本表照 +23 規則改正、實跑紀錄指到卷證(r2-ciexp.md、設計審 r1 正確性席報告) |
| 二接10 | 接手 F10 | 折:範圍外紀錄加一列更正、作廢上一列(那篇只追加) |
| 二通5 | 通才 F5 | 折:A3 的十個案例改成直接呼叫函式,不再各起一個 lint-check 子程序 |
| 二安1、二安2 | 資安 F1、F2 | 折:計劃實務隱患寫明打開陌生 repo 時 A3 展開環境變數只做存在判斷、不回顯,符號連結讀到的內容只比對字樣,判縱深防禦 |
