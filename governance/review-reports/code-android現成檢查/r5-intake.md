# r5 收貨紀錄(code-android現成檢查,第二次加開輪)

## 收貨

- 第 5 輪(第二次 cap-decision extra-round 已記,回顧已更新並記錄)。七席全 sonnet,看 r5-repair.patch(cd36e5e04..deb8969f5,811 行),資安看整份 r5-snapshot.patch。外家預設不派。
- 七份從逐字稿存檔,全正規化;通才 3 句有 1 句錨不到(不採信那句,所屬條目另有實跑),其餘全錨。席位臨時目錄與 worktree 已清。
- 邊界席另抓 20 個公開專案真實 CI 檔(15 個上輪沒用過),全部判對;r4 的三個重現(欄位值、資料夾連結、repo 內檔案連結)經正確性席前後兩版比對確認修好。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 五邊1 | 邊界 F1、正確性 F1、通才 F2 | CircleCI `run:` 的 `command: npm run build`、`command: |` 內 `make build` 加 `./gradlew assembleDebug` | HIT(三席):A1 不印,修補前會印 |
| 五架3 | 架構 F3 | `_path_resolves_in_root` 自稱唯一,`_events_path_safe` 與另一處仍內嵌 `resolve().is_relative_to` | HIT(讀碼) |

refuted: none

## 先查世界

- PRIOR-ART: `command` 是 CircleCI `run` step 的通用欄位(https://circleci.com/docs/configuration-reference/#run ),不專屬 gradle orb;`tasks`、`arguments`、`gradle_task` 在各自平台都專屬 gradle 任務。A1 是不擋的提醒,多印一則的代價小於該印卻被吞掉。採用:拿掉 `command`,CircleCI gradle orb 的 `command: build` 寫進天花板(會多印 A1)。排除:限定 orb 上下文(要再寫一套 YAML 結構判斷,又是字面判斷的新面)。
- PRIOR-ART: 路徑判定唯一一份——照既有「找既有防護工具重用」規則,把兩處內嵌改呼叫 `_path_resolves_in_root`,不改不了的就把說明縮到實際共用範圍。

## 逐條去向

- 折:五邊1(同 五正1、五通2)、五架3、五正2(同欄兄弟鍵負例)、五正3(`>`、`>-`、`|-` 與連結迴圈測試)、五資2(連結迴圈說明與行為不符:照實改說明或改 strict 解析)、五架1(`_detekt_segment_codes` 改呼叫 `_is_gradle_head`)、五架2(`_repo_path_unsafe` docstring 與呼叫端對齊新的錯誤處理)、五通1(Jenkinsfile `#` 註解行:天花板補寫)、五接1–3(文件措辭、語料列數、S6 排序)、五通3(語料測試暫存)。
- 放行(原報 minor):五資1(超長單行記憶體:舊有切詞、非本輪引入)、五邊2(Buildkite 不在清單:計劃天花板「只看已知名字」)、五邊3(正面確認,非缺陷)、五架4(縮排量法空格對 tab:YAML 不允許 tab 縮排)、五安1(檢查與開檔時間差:需刻意搶時序,屬範圍外天花板)。
