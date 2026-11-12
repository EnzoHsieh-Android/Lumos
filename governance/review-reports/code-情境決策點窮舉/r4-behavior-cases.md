# code-情境決策點窮舉 r4 待驗案例

修前 6d5394398c30d25756a063be468e8a9ef3fb24eb → 修後 e160da75e67b842669bb4b606d2eb0a78f717934。下表只是待驗範圍,不是「已修好」或因果的證據;席位可自行補案例。組別編號對應 `r3-fix.json`。

修前證據:編排者沒有保存修前逐案原始輸出;要比較請在 `/tmp/lumos-seat-work/code-情境決策點窮舉/<席名>/` 用 `git -C <repo> worktree add <那個目錄>/before 6d5394398c30d25756a063be468e8a9ef3fb24eb` 自己跑。

| 組 | 角色 | 待驗行為 | 出處 | 修後證據指標 |
|---|---|---|---|---|
| G1 | repair | 單獨一行的 // BAD 下一行是「只有註記」的行時跳過、標到它修飾的語句:註記帶巢狀括號、具名參數帶呼叫、泛型、`@[…]`、參數跨行、一行兩個註記;註記括號到檔尾都沒關時不當註記 | 計劃〈範圍〉`規則 <id>` 那條;〈依據來源〉Error Prone 列 | `t_kt_catalog_bad_snippets_reach_rows` |
| G2 | repair | 去註解後三份行數對不上時報問題;〈叫不出〉片段格不是整格一段反引號時照整格原文、`\|` 照樣還原;`\|` 還原在 check.py 只有一個出口 | 計劃〈範圍〉反查表 | `t_kt_catalog_bad_snippets_reach_rows` |
| G3 | repair | 範本檔有寬鬆讀法也關不上的圍欄時,範本改由報問題,不拿外洩到下一組的內文背書 | 計劃〈範圍〉`範本 T<n>` 那條;CommonMark | `t_kt_catalog_bad_snippets_reach_rows` |
| G4 | repair | 證據樣式測試切〈情境決策表〉用 check.py 的 `_section` | 既有切節函式 | `t_kt_catalog_evidence_patterns` |
| — | preserve | 為過新增告警閘把 `_bad_lines` 拆成 `_bad_lines_in`、`_next_statement`,註記讀法拆出 `_one_annotation_end`:行為不變 | 驗證紀錄 | `-k bad_snippets_reach`(57) |
| 全部 | preserve | 既有 // BAD 標法:行尾 // BAD、`//BAD`、`// BAD-NEXT` 標續行、`// BADGE` 不算、整行 `@Foo` 跳過、`@Composable fun A()` 標那一行、字串裡的 // BAD 不算、換頁字元與 U+2028 不錯行、非 UTF-8 回問題 | 計劃〈範圍〉 | `t_kt_catalog_bad_snippets_reach_rows` 既有案例 |
| 全部 | preserve | 圍欄判定跟 scripts/lumos 一致(keep_fenced 兩條路) | 既有對照測試 | `t_kotlin_template_fence_parity` |
| 全部 | preserve | 真型錄 `--catalog-only` 0 個問題;`--sg <ast-grep 0.51.x>` 規則 228 條 0 個問題;壞例樣本 `_bad_lines` 輸出不變 | 型錄自檢 | 修後實跑 |
| 全部 | preserve | 讀型錄的整組測試全過 | — | `-k kt_catalog`(320)、`-k kt_situation`(145) |
