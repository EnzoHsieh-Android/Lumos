# code-android儀器測試範本 r1 收貨(2026-11-06)

範圍:`a80039ef6..fc1ceb85a`。分級工具判 light(它不把測試總檔算程式檔),編排者升 standard:這批改了測試總檔 235 行、範本 3347 行,範本會被 AI 照抄。材料 4591 行拆五包:範本甲(骨架、T6–T8)、範本乙(T9–T10)、範本丙(T11–T13)、丁(測試、型錄、標準文件、筆記)。五席:範本甲、範本乙、範本丙、測試、架構對齊(丁)。

## 收貨三道

- 正規化:五份已是正規化格式。
- quote-check:四份對各自那一包全數錨定;測試席 F1 第一句引句出自範本(範本丙那包),對整份 r1-snapshot.patch 比對全數錨定。
- refcheck:全部對得上。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 範本丙-F1 | 席位讀 ArchUnit 1.5.1 原始碼 `FreezingArchRule.evaluate` 的 `!store.contains(delegate)` 分支與 `TextFileBasedViolationStore.getStoredRulesFile`;官方手冊 8.6.2 只寫 allowStoreCreation 管「建新的違規清單」、沒寫索引在而規則是新的情況(https://www.archunit.org/userguide/html/000_Index.html ) | HIT(讀原始碼;修補時實驗驗證) |
| 測試-F1 | `grep -n allowStoreCreation skills/kotlin-idioms/test-templates.md`:散文 5876、5889 兩處也含 `allowStoreCreation=false` 與 `freeze.store.default.path`;守衛 `scripts/test_lumos.py` 126821 只比對整節字串 | HIT |
| 測試-F2、F3 | 席位在複本改 UI-39 標準寫法欄回舊說法跑 `-k kotlin_catalog` 60 passed;改壞對照只比對舊字串本身 | HIT |
| 測試-F4 | 席位 WebFetch 強跳過官方頁,頁上逐字有 `===` | HIT |
| 範本甲-F1、範本乙-F1/F2、範本丙-F2、架構對齊-F1/F2 | 讀材料與驗證紀錄原文對照 | HIT |

## 先查世界

PRIOR-ART:ArchUnit 凍結規則——官方手冊 8.6.2:allowStoreCreation 預設 false、CI 不該建新清單;allowStoreUpdate 可設 false 禁止更新已凍結規則的違規;refreeze 預設 false(https://www.archunit.org/userguide/html/000_Index.html )。手冊沒寫「清單索引在、規則是新的」怎麼辦,範本丙席讀原始碼指出這時會把當下違規存成新的凍結並回綠。採用:範本照實寫明 allowStoreCreation 只擋「索引檔整份不見」;用實驗查 allowStoreUpdate=false 是否擋得住新規則被靜默凍結,擋得住就寫進範本並加矩陣格,擋不住就加一支斷言索引裡規則清單等於已知規則的測試;排除:只改說明文字不加任何會紅的守衛。
PRIOR-ART:守衛測試被散文湊過——同一類「字串出現在整段就算」的檢查,既有做法是先切出程式碼圍欄再比對(`m._visible_lines`、`template_sections` 的圍欄判定);採用:只在 properties 圍欄內比對完整的 `key=value`。

## 分組與去向(全數折入)

- 甲 T12 凍結守衛:範本丙-F1(major)、測試-F1(major)→ 範本說法照實寫、實驗後加守衛;資料測試只在圍欄內比對完整 key=value,改壞只改程式行要紅。
- 乙 測試守衛缺口:測試-F2、F3(minor)→ UI-39 標準寫法欄加斷言;改壞對照改成拿改壞後的資料跑同一組判準。
- 丙 範本與型錄措辭:範本甲-F1、範本乙-F1/F2、範本丙-F2、測試-F4(minor)→ 檔頭實跑環境分開寫;TEST-29 壞測試註解改成實測結論;「九列」改對;STATE-17 說明改成「通知一次、內容兩筆」;UI-39 後果欄只標結論那一半是推論。
- 丁 一致性:架構對齊-F1/F2(minor)→ 缺節訊息照既有「範本檔沒有 T<n> 節」;S2 內容檢查搬進 content_guards;標準文件指路句照既有格式、不重抄骨架細節。
