# code-各棧測試資料夾 r2 收貨紀錄(編排者)

## 收貨

- 六席 Claude 從輸出紀錄抽最終回覆,原樣存檔(牽連席那份收貨時漏存、事後從同一份輸出紀錄補抽,內容未動)。外家 finder 本輪沒派:修正會再改一次,與其讓 Codex 審即將被取代的版本、多燒一份額度(帳號用量剛撞過上限),改到第三輪審最終版;編制表上外家缺席只提醒不擋。
- 派工詞要求 clean 的觀察不要寫成 ### F 條目,六份報告都照做;report-normalize 六份都已正規化,quote-check 六份全數錨定;refcheck 只有牽連席一處把測試指令寫成路徑樣子(不是壞引用)。
- 席報告合計(照各席 ### F 與總結句):正確性 2 條(blocking 0)、邊界 1(1)、接手的人 1(0)、牽連 1(0)、架構對齊 2(2)、資安 2(0),共 9 條、blocking 3。

## 機械重現

| 發現 | 重現做法 | 結果 |
|---|---|---|
| D1 取副檔名另寫一份、沒轉小寫(架構對齊 F1、正確性 F1) | `scripts/lumos` 新函式自己 rsplit 取副檔名;同檔 `_testmap_ext` 已有、會轉小寫;`PosTerminalTests/Fixture.SWIFT` 判成要家 | HIT |
| D2 頂層資料夾另算一份、沒排除點開頭(架構對齊 F2) | `_nodehome_refs` 的算法排除點開頭,新寫的那行沒有 | HIT |
| D3 Gradle 那條不看副檔名與深度(邊界 F1、牽連 F1、資安 F2) | 改動前版本實跑:`backend/src/internal/androidTest/handler.go`、`tools/src/androidTest/backdoor.py` 回 False,改動後回 True;邊界席舉的 `backend/src/internal/test/handler.go` 改動前就回 True(資料夾名 test 走的是既有測試地圖的資料夾規則),那一半不是這次引入的 | HIT(test 那半 MISS) |
| D4 同名資料夾只看名字存在(資安 F1) | `scriptsTests/inject.cs` 在有 `scripts/` 的 repo 回 True | HIT |
| D5 兩道錨仍可能被命名巧合同時滿足(正確性 F2) | `Payment/` 與 `PaymentTests/SandboxModeController.swift` 回 True | HIT |
| D6 裸名 UITests/、IntegrationTests/ 被新錨擋掉(接手的人 F1) | `UITests/LaunchHelper.swift` 回 False,第一輪版本回 True | HIT |

## 去重分組與處置(本輪有 major:accepted 必須為空)

| 組 | 等級 | 怎麼處置 |
|---|---|---|
| D1 | major | 折:改用 `_testmap_ext`(小寫),補上點號對齊對照表寫法;測試加大小寫一條 |
| D2 | major | 折:抽出 `_nodehome_top_dirs`(點開頭的不算),別人的檔那條與測試資料夾錨共用;測試加一條 |
| D3 | major | 折:Gradle 那條要緊接在 src 下一層、同模組 src/main 有同一種副檔名的檔;兩個反例寫進測試,Java 的 androidTest 照認 |
| D4 | minor | 折:頂層那條要去掉結尾的同名資料夾裡「有同一種副檔名的檔」,不只是存在;反例寫進測試 |
| D5 | minor | 折(寫明天花板):事故筆記「沒涵蓋」補過鬆那一面,旁邊加 REVISIT:2026-10-12 列出被這條規則免家的檔逐支看 |
| D6 | minor | 折:資料夾就叫結尾樣式本身、副檔名對得上的直接認;兩個例子寫進測試 |

- 突變檢查十種全殺(第一次跑「推太鬆」存活,因為新錨讓原本那個反例剛好無害;補一個 src/main 也有 .py 的反例後殺掉)。
