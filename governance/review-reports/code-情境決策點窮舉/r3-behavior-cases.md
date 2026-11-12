# code-情境決策點窮舉 r3 待驗案例

修前 594f97e95b3752202df285f455f8dee6d84e83b9 → 修後 6d5394398c30d25756a063be468e8a9ef3fb24eb。下表只是待驗範圍,不是「已修好」或因果的證據;席位可自行補案例。組別編號對應 `r2-fix.json`。

修前證據:編排者保存了修前紅的那一支(`r2-repro.txt` 開頭:`t_kt_catalog_evidence_patterns` 9 過 2 紅),其餘修前逐案原始輸出沒保存;要比較請在 `/tmp/lumos-seat-work/code-情境決策點窮舉/<席名>/` 用 `git -C <repo> worktree add <那個目錄>/before 594f97e95b3752202df285f455f8dee6d84e83b9` 自己跑。

| 組 | 角色 | 待驗行為 | 出處 | 修後證據指標 |
|---|---|---|---|---|
| G1 | repair | 真型錄的證據樣式測試全過:決策表列數只在〈情境決策表〉節裡數;D-4 主證據樣式是一條、跳脫直線已還原、比得到 flatMapLatest 與 `?.cancel()` | 型錄〈情境決策表〉 | `t_kt_catalog_evidence_patterns` |
| G2 | repair | 壞例檔:前一行註解裡有換頁字元時 // BAD 對到自己那一行;字串裡的 // BAD 不是標記;// BAD 下一行是「@註記 + 同一行程式」時標到那一行;同一行字串裡有 U+2028 時行尾 // BAD 照認;三份行數不一致回問題 | 計劃〈範圍〉`規則 <id>` 那條 | `t_kt_catalog_bad_snippets_reach_rows` |
| G3 | repair | 沒關的圍欄:keep_fenced=True 時內文算到檔尾(最後一行不丟),跟 scripts/lumos 的 `_visible_lines` 一致;範本小節圍欄沒關時片段落在最後一行照算 | CommonMark 圍欄程式區塊;計劃〈依據來源〉 | `t_kotlin_template_fence_parity`、`t_kt_catalog_bad_snippets_reach_rows` |
| G4 | repair | 〈叫不出的壞寫法〉片段格反引號外還有字時照整格原文(不吞尾巴),整格一段反引號時取內文;兩種都還原 `\|` | 計劃〈範圍〉反查表 | `t_kt_catalog_bad_snippets_reach_rows` |
| — | repair | D-4 例外:不適用時文字有 flatMapMerge、例外證據樣式比得到 flatMapMerge 與 flatMapConcat;樣本「搜尋框用 flatMapMerge」只對標準寫法算錯,新增 flatMapMerge 並行上傳是例外正例 | 型錄 D-4;規則包筆記新的 WHY 行 | `--catalog-only`(含證據樣式自測)、`-k evidence_samples` |
| 全部 | preserve | 既有的 // BAD 標法照舊:行尾 // BAD、`//BAD`、`// BAD-NEXT` 標續行、`// BADGE` 不算、整行 `@Foo` 註記跳過、非 UTF-8 回問題 | 計劃〈範圍〉 | `t_kt_catalog_bad_snippets_reach_rows` 既有案例 |
| 全部 | preserve | keep_fenced=False 的圍欄判定不變(十一個對照案例) | 既有對照測試 | `t_kotlin_template_fence_parity` |
| 全部 | preserve | 真型錄 `--catalog-only` 0 個問題;`--sg <ast-grep 0.51.x>` 規則 228 條 0 個問題 | 型錄自檢 | 修後實跑 |
| 全部 | preserve | 統計數字不變(公開名稱 434、壞寫法 111 等) | 型錄〈統計〉 | `t_kt_catalog_stats_consistent` |
| 全部 | preserve | 推送前情境段切段與表態核對不變 | scripts/lumos | `-k kt_situation`(145) |
