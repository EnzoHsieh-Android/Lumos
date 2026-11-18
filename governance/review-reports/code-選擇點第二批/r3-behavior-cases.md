# code-選擇點第二批 r3 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 6cc9ad8c57bd4c9e5547121c971f62f86a116c1b、修後 87093835a62c82da28aa1ff0a0dbf02ddc98dc40。來源:計劃 docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md 的範圍 2、條款 S6、S8 與預期值表。修後版本的選擇點相關測試跑過一次全綠(choice_points 105、kt_catalog 320、choice 401);修前版本在第二輪派審前同樣跑過全綠(數字在第二輪修補代理報告,沒另存檔),修前通過證據以此為限。修正關卡結果在 r2-fix-check.txt。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| G1 | repair | `if (a) { go() } else if (b) { x.let { show(it) } }`、沒大括號的 else-if、`if (c) if (d) x.let {…}`、`for (i in list) if (c) x.let {…}`、`if (c) when (d) {…}`、`if (c) try { x.let {…} }` 當陳述 → C-34 不命中 | 計劃範圍 2「只收確定是值的位置」 | t_choice_samples_batch2 |
| G1 | repair | `val q = if (c) 1 else if (d) x.let { it + 1 } else 0` → C-34 不命中(語法判不完不收,刻意漏抓) | 同上 | t_choice_samples_batch2 |
| G1 | preserve | `val y = x.let { it + 1 }`、`val z = if (c) x.let { it + 1 } else 0`、`fun h() = if (c) x.let { it + 1 } else 2` → C-34 命中 | 預期值表 C-34 列 | t_choice_samples_batch2、t_choice_points_batch2_api |
| G2 | repair | `LaunchedEffect(-1.coerceAtLeast(k))`、`remember(-1.0.coerceAtLeast(k))` → C-36、C-37 命中(key 會隨 k 變,不是常數) | 計劃範圍 2 字面值定義 | t_choice_samples_batch2 |
| G2 | preserve | `LaunchedEffect(-1)`、`LaunchedEffect(+2.5)`、`remember(-1)` → 不命中;`LaunchedEffect(-k)` → 命中 | 同上、預期值表 | t_choice_samples_batch2、t_choice_points_compose |
| G3 | repair | 依列號統計遇到列號 `C-` 加 5000 個 9 → 照印、不丟例外,排在 `C-7` 後面 | S8(依列號統計) | t_gov_stats_choice_by_row |
| G3 | preserve | `C-9` 排在 `C-32` 前;列號 `C-²` 照印 | S8 | t_gov_stats_choice_by_row |
| 另補 | repair | 型錄「已撤列號」那行前面有空白縮排 → 報「恰好一行」那句看不懂訊息 | S6(撤號守衛) | t_choice_table_batch2 |
| 另補 | preserve | 頂格 `已撤列號:C-31` → 照認;撤掉的列號再出現 → 報撤號衝突 | S6 | t_choice_table_batch2 |

未覆蓋:第二輪放行的「單行上千個 `?.` 輸出平方成長」沒有自動測試(修前修後同量級,數字在 r2-intake 重現表);1000 段 else-if 鏈與 1000 層巢狀的輸出量是手動量測(r2-intake 改壞驗證段)。
