# code-選擇點第二批 r4 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 87093835a62c82da28aa1ff0a0dbf02ddc98dc40、修後 59c410383b0337ed842ce8e1a9e25d8eb7a3c476。來源:計劃 docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md 的範圍 2、條款 S6 與預期值表。修後版本的選擇點相關測試跑過一次全綠(choice_points 105、kt_catalog 320、choice 404),check.py 型錄檢查 0 問題;修前版本在第三輪派審前跑過全綠(choice 401)。修正關卡結果在 r3-fix-check.txt。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| G1 | repair | 拿掉 C-34 值位置的任一選項(when 分支值、if 或 when 大括號區塊最後一個陳述、try 區塊、catch 區塊)→ 樣本測試翻紅 | 計劃範圍 2「只收確定是值的位置」;Semgrep 規則測試每個排除條件各一行 | t_choice_samples_batch2 |
| G1 | repair | 拿掉 C-36、C-37 字面值清單任一種(boolean、null、integer、real、long、hex、bin、unsigned)或帶號運算元任一種(long、hex、bin、unsigned)→ 樣本測試翻紅 | 計劃範圍 2 字面值定義 | t_choice_samples_batch2 |
| G1 | preserve | 第三輪前既有的 C-34、C-36、C-37 樣本行(else-if 鏈不收、`-1.coerceAtLeast(k)` 命中、`LaunchedEffect(-1)` 不命中)結果不變 | 預期值表 | t_choice_samples_batch2、t_choice_points_compose |
| G2 | repair | 型錄「已撤列號:C-４０」(全形)、「C-040」(前導零)、「C-４0」(全形混半形),表裡有 C-40 → 報「已撤列號那一行要寫…」看不懂,不靜默放過 | S6(撤號守衛) | t_choice_table_batch2 |
| G2 | preserve | 頂格 `已撤列號:C-31` → 照認;多個列號用頓號、逗號、空白隔開照認;撤掉的列號再出現 → 報撤號衝突;縮排的撤號行 → 報恰好一行 | S6 | t_choice_table_batch2 |

未覆蓋:第三輪放行的兩條(括號包住的常數 key 照樣命中、引數層層巢狀的輸出平方成長)沒有自動測試,修前修後同結果,數字在 r3-intake 重現表;逐條拿掉的掃描是編排者手動跑(r3-intake 重現表 c1 g1、c2 列),不是測試的一部分。
