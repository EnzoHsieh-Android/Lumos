# r4 收貨紀錄(code-android現成檢查,加開輪)

## 收貨

- 第 4 輪(到頂後人裁加開,cap-decision extra-round 已記、跑滿回顧已記)。七席全 sonnet;正確性、資源、邊界、接手、通才、架構對齊看 r4-repair.patch(6793598b1..cd36e5e04,614 行),資安看整份 r4-snapshot.patch(2078 行,sha256 bc11b99f…)。外家預設不派,結論寫成「單家族視角下」。
- 七份從逐字稿存檔,全正規化、引句全錨。席位沒改 repo;臨時目錄與席位開的 worktree 已清。
- 回顧教訓落地:邊界席用 curl 抓 15 個公開專案的真實 CI 檔加 8 個負例做固定語料,修補前後兩版各跑一次(gh 被席位權限擋,改 curl)。新版判錯 4 列(Azure tasks、Signal 聚合任務、AuroraStore 與 npm 的 lint 字樣),舊版判錯 4 列(owncloud 與三個負例)。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 四邊1 | 邊界 F1、通才 F1、正確性 F1、接手 F1 | Azure `tasks: 'clean build …'`、`gradle-build-action` 的 `arguments: build`、CircleCI orb `command: build`、Bitrise `gradle_task: build` | HIT(四席實跑):新版印 A1、舊版不印 |
| 四通2 | 通才 F2、資安 F1 | `.github/workflows` 是指向 repo 外的資料夾連結 | HIT:仍讀到連結目標裡的檔 |
| 四通3 | 通才 F3 | workflow 檔是指向 repo 內 `ci/real.yml` 的連結 | HIT:T4 誤印 |

refuted: none

## 先查世界

- PRIOR-ART: 「靠欄位而不是命令列叫 gradle」——Azure Pipelines Gradle@2 任務的 `tasks` 輸入(https://learn.microsoft.com/azure/devops/pipelines/tasks/reference/gradle-v2 )、gradle/actions setup-gradle 舊版 `arguments` 輸入(https://github.com/gradle/gradle-build-action )、Bitrise gradle-runner 的 `gradle_task`、CircleCI gradle orb 的 `command`。採用:這四個已知欄位的值視同 gradle 任務列,跟命令列同一套判斷;其他欄位照舊不算(避免回到整檔找詞)。
- PRIOR-ART: 符號連結——Python `os.path.realpath` 解析後用 `commonpath` 判是否仍在 repo 根底下(lumos 既有路徑限制在根底下的寫法,實作前先搜既有函式重用);在 repo 內照讀、在外略過。
- 固定語料:邊界席這輪的 23 列樣本(真實檔節錄加負例)寫成測試,修補前後都跑(回顧 avoid 欄的做法)。

## 逐條去向

- 折(程式):四邊1(同 四通1、四正1、四接1)、四通2(同 四安1)、四通3、四架1(取檔名寫法統一)、四架2(Jenkinsfile 註解判斷收回 `_ci_workflow_texts`)。
- 折(文件與天花板):四通4、四接4(同一行任何 check/build 字樣都算、`-x check`)、四接2(版本表 AGP 9.4.0 與 8.7.0 邊界)、四接3(r2 實測標成舊模型,改引本輪語料)、四接5、四邊5(提醒標題措辭)、四邊2(Signal 聚合任務)、四邊3(別的工具的 lint 字樣)、四邊4(YAML 摺疊純量與續行跨註解)。
- 放行(原報 minor):四資1(50 MB CI 檔 8.8 秒,讀檔本來就沒有上限、非本次引入)、四資2(測試 83 秒、上限 180 秒,別會談並行時量的、自 r2 未變慢)、四安2(外掛路徑展開只得到存在與否的布林,不回顯)。
