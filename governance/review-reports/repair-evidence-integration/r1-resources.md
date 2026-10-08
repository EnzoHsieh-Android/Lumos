severity: major

resources-F1

severity: major

blocking: 是

觀察：固定樹只固定「讀取來源」，沒有把整個 gate 結果綁定到同一棵仍待提交的樹。索引在檢查期間改變時，spec 只撤回額外測試路由證據，仍允許用舊樹算出的改動、設定、圖譜與分類結果通過或擋下。現行整合點另有 `gate=off` 等提前返回，發生在索引版本複查之前；待實作方案沒有要求把複查移到所有返回路徑共同經過的 finally/finalization 階段。

獨立判準：以暫存區為審查對象的 gate，只有在「受檢樹＝最後採用的暫存樹」時才能輸出有效裁決。若索引已分歧，應重試、整體撤銷裁決或要求重新檢查；只撤回其中一類借證，不能保留舊樹的正式裁決。

具體場景：先捕獲合法樹 T0；檢查期間另一程序把未安家的新程式檔加入索引，形成 T1。結尾雖發現版本不同，但只清空測試路由證據，`changes/N/config` 仍來自 T0，最後回傳通過，隨後提交 T1。更直接的變體是 T0 設定為 `node_home.gate=off`，函式在版本複查前就回傳 0。反向情況也會以已被移除的 T0 違規錯擋 T1。

引句:「結尾若索引讀不到或版本不同，撤回額外測試路由證據。」

必要佐證 file: `/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修補驗證與來源留存整合_計劃.md:31`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:943`

必要佐證 file: `/tmp/lumos-future-repair-regression-research/governance/review-reports/repair-evidence-integration/r1-materials.md:979`

覆蓋與未驗邊界：

- 增量封存與前置版本取得：spec 已要求受保護 ref 或封存入口、前置 commit 的取回入口、指紋核對，以及實際還原 commit/tree/blob；並明定普通 archive 不能單獨還原提交血緣，因此不重報已補正問題。
- `c4f2b0cf` 前置物件閉包與冷還原收據的實際內容不在本席指定必讀正文中；未讀其他卷證，也不因既有綠色紀錄推定它目前可取回。
- 現行函式尚未實作固定樹；本 finding 評的是待實作方案的裁決綁定缺口，不把「現在尚未實作」本身列為問題。
- 未執行外部代碼、Git 操作或安裝，也未讀其他席／前輪報告。

實際閱讀帳：

- `lumos-design-loop/SKILL.md` 1–79：79 行
- 唯一真 spec 1–67：67 行
- 凍結副本 1–67：67 行
- `r1-materials.md` 1–1185：1185 行
- 因工具顯示截斷而定點重讀 `r1-materials.md` 141–160：20 行
- 行數盤點輸出：5 行
- 合計：1423 行，未超過 1800 行

最高級：major  
blocking 數：1