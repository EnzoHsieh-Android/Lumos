# r3 收貨紀錄(code-android現成檢查)

## 收貨

- 第 3 輪(上限輪),high,修訂輪。七席全 sonnet:正確性、資源、邊界、接手、通才、架構對齊看 r3-repair.patch(7742e4bd6..6793598b1,806 行)並可查 r3-snapshot.patch;資安看整份 r3-snapshot.patch(2019 行,sha256 f46030f1…)。外家預設不派,結論寫成「單家族視角下」。
- 七份從逐字稿存檔,都已是正規化格式。quote-check:通才 8 句、正確性 5 句各 1 句錨不到(不採信那句;所屬條目另有實跑重現照採);資源席 clean 無引句;其餘全錨。
- 席位沒有改 repo;資源席自述壓測腳本一度開出約 620 個程序、已自行殺掉,收貨時 `ps` 查無殘留。審查席臨時目錄已用字面路徑刪除。
- 修正關卡:r2-fix.json 補 prior 與錨點後 `loop fix-check --round r2` 全部通過(228 秒)。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 三通1 | 通才 F1、正確性 F1、接手 F1 | CI 只寫 `./gradlew lintAnalyzeDebug`,A1 不印;計劃 S1 條款原文仍寫照印 | HIT(三席各自實跑) |
| 三通2 | 通才 F2、接手 F4 | 無 CI 檔、只有 `app/lint-baseline.xml` 或 `android { lint { … } }`,A1 不印 | HIT |
| 三邊1 | 邊界 F1、通才 F3、正確性 F2、接手 F7 | `needs: build` 加 `cache: gradle` 加 `./gradlew assembleDebug`,A1 不印;GitLab `stage: build` 同 | HIT |
| 三通8 | 通才 F8 | 測試 mkdtemp 的 gctl-andci-* 留暫存 | MISS:測試跑在拋棄式 gctl-run- 暫存根底下(`scripts/test_lumos.py` 前置斷言檢查 gctl-run-),資源席以 TMPDIR 指臨時目錄實跑結束後為空 |

refuted: 三通8

## 先查世界

- PRIOR-ART: 「CI 有沒有跑 Android Lint」第四次被同類寫法打穿(設計審 r1、代碼審 r1 逐條解析、r2 限 gradle 行、r3 整檔找詞)。這輪三席獨立指到同一件事:跡象門檻寬到失去鑑別力(`needs: build`、範本自己的基準線檔)。查 AGP 任務關係:社群與既有慣例 `./gradlew check -x lint`、`build -x lint` 顯示 lint 掛在 check 與 build 底下(https://stackoverflow.com/questions/21143556/avoid-lint-when-gradle-execute-check ,社群旁證,官方任務圖頁未找到);Scorecard checks.md 的取向是「低分不是定論」,只認已知名字(https://github.com/ossf/scorecard/blob/main/docs/checks.md )。採用:跡象只認「真的會叫起 Android Lint 的命令」——①lint 任務名(照舊,任何位置,因 Bitrise step 名與續行也要認)②`check`/`build` 只在同一邏輯行(續行合併後)有 gradle 呼叫詞(`gradlew`、`gradlew.bat`、`gradle`)時才算——這把 r2 被打穿的「lint 名只認 gradle 行」與 r3 的「umbrella 整檔」各取對的那半;③建置檔的 lint 區塊與基準線檔不再算跡象(它們是範本前兩步的痕跡,不代表 CI 有跑)。排除:整檔找 umbrella 詞(r3 打穿)、拿建置設定當 CI 證據(r3 打穿)。
- 天花板照實寫:job 名叫 lint、別的工具的 lint(`npm run lint`)、composite action 與 GitLab include 讀不到、命令先 cd 再用相對外掛路徑——這幾種方向都是少印或多印一則提醒,只是提醒、不擋。

## 歸因

- 上一輪修補造成的(regression):三通1(排除名單改了、條款沒跟)、三通2(證據模型新增 ③)、三邊1(r2 把 umbrella 從 gradle 行放寬到整檔)、三架1/三通4(③ 帶進第二次走訪)。
- 其餘是上一輪沒人看的角落或文件沒跟上。

## 逐條去向

折(程式):三通1、三通2、三邊1(同 三通3、三正2)、三通4、三架1(③ 拿掉後走訪消失)、三邊3、三邊6(③ 拿掉後不再相關)、三通5、三邊7(Jenkinsfile `/* */` 與行尾 `//` 剝除)、三架2(gradle 呼叫詞表共用一份)、三正5(大括號展開判不了)、三安1(建置檔與 CI 檔是符號連結就略過)、三正4(守衛測試補齊)。
折(文件):三正3(dry-run 核對補 REVISIT)、三通6、三接5(版本表補 AGP 9.0–9.2 並寫明邊界照「建置用 lint 不高於專案 lint」挑)、三通7、三接2(舊 WHY 行改寫)、三接3(計劃兩處舊說法)、三接6(lintVital 出處改 AOSP 提交、指南改名)、三接7、三邊5(天花板補)。
放行:三架3(T4 讀原文、A1 去註解是有意分歧,`_ci_config_paths` 說明已寫)、三邊2(job 名叫 lint 計劃已列為接受的代價)、三邊4(composite action 與 include,A1 文字已自述)、三接8(測試耗時 72 秒、上限 180 秒,自 r2 未變慢,資源席實量)。
駁回:三通8(見重現表)。
