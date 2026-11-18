# code-選擇點第二批 r2 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 eebb84593d24959fc51bb54d3c6e2412333f77f1、修後 6cc9ad8c57bd4c9e5547121c971f62f86a116c1b。來源:計劃 docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md 的條款 S1–S9 與預期值表。修前版本的選擇點相關測試在第一輪派審前跑過一次全綠(choice 371、gov_stats 88、kt_catalog 320);那次輸出只在當時的工作階段,沒另存檔,修前通過證據以此為限。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| G1 | repair | `if (c) x.let { show(it) }`、for/while/else/when 分支沒大括號的 `.let` → C-34 不命中 | 計劃範圍 2「只收回傳值被用到的」 | t_choice_samples_batch2 |
| G1 | repair | `LaunchedEffect(-1)`、`LaunchedEffect('c')`、`remember(-1)` → C-36、C-37 不命中 | 計劃範圍 2 字面值定義 | t_choice_samples_batch2 |
| G1 | preserve | `val y = x.let { it + 1 }`、`val z = if (c) x.let { it + 1 } else 0` → C-34 命中;`LaunchedEffect(userId, id)`、`remember(k)` → 命中 | 預期值表 C-34、C-36、C-37 列 | t_choice_samples_batch2、t_choice_points_batch2_api、t_choice_points_compose |
| G2 | repair | 同一行兩筆放行時區不同(`+08:00` 與 `+00:00`)→ 取 UTC 較晚那筆;同壞法先殺掉後存活 → 終態殺掉 | S8(依列號統計) | t_gov_stats_choice_by_row |
| G2 | repair | 列號 `C-²` → 依列號段照印、不丟例外 | S8 | t_gov_stats_choice_by_row |
| G2 | preserve | 沒有列號的舊帳、「基準不綠沒跑」事件 → 不計入依列號;C-9 排在 C-32 前 | S8 | t_gov_stats_choice_by_row |
| G3 | repair | `?.` 前面有中文字 → `!!` 插入位置照位元組算 | S3(安全呼叫符錨點) | t_choice_points_nul_safecall |
| G3 | repair | 只改到 `remember(` 引數清單的右括號那一行 → 引數錨點照挑 | S3(引數錨點) | t_choice_points_compose |
| G3 | preserve | 一般 `a?.b` → `a!!.b`;改到引數清單第一行 → 挑得到 | S3 | t_choice_points_nul_safecall、t_choice_points_compose |
| G4 | repair | `已撤列號：C-31`(全形冒號)→ 照認;`- 已撤列號:C-31`、粗體、多寫一行 → 報看不懂 | S6(撤號守衛) | t_choice_table_batch2 |
| G4 | preserve | `已撤列號:(無)` → 不報;撤掉的列號再出現 → 報 | S6 | t_choice_table_batch2 |
| G5 | repair | 巢狀 300 層 `remember(k) {`、1MB 每行多個 `?.` → 掃描輸出線性成長 | 計劃〈實務隱患〉輸出量門檻 | 無自動測試(手動量測,數字在 r1-intake 重現表) |
| G5 | preserve | 第二批六列在樣本上的命中集合不變 | 預期值表 | t_choice_samples_batch2、t_choice_points_batch2_stable |

未覆蓋:第一版挑法(S7)對真專案的穩定性只靠 t_choice_points_batch2_stable 的 82 組釘;G5 沒有自動測試守輸出量。
