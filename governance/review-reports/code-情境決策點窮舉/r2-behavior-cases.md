# code-情境決策點窮舉 r2 待驗案例

修前 8cd6d3c5e76bc669181a357ba303155ad2d869cb → 修後 594f97e95b3752202df285f455f8dee6d84e83b9。下表只是待驗範圍,不是「已修好」或因果的證據;席位可自行補案例。組別編號對應 `r1-fix.json`。

修前證據:編排者沒有保存修前版本逐案的原始輸出,修前一律「未保存」;要比較請在 `/tmp/lumos-seat-work/code-情境決策點窮舉/<席名>/` 用 `git -C <repo> worktree add <那個目錄>/before 8cd6d3c5e76bc669181a357ba303155ad2d869cb` 自己跑。

| 組 | 角色 | 待驗行為 | 出處 | 修後證據指標 |
|---|---|---|---|---|
| G1 | repair | 〈叫不出的壞寫法〉表的每道守衛(範本三道、規則目錄與訊息編號、起訖行上界、`…` 依序、只有 `…`、`\|` 還原、`--sg` 索引接線)各有一個只有它會擋的案例 | 計劃〈叫不出的壞寫法〉條款與預期值表 | `t_kt_catalog_bad_snippets_reach_rows`、`t_kotlin_rulepack_samples` |
| G1 | repair | 〈API 決策點〉表的每道守衛(同名兩列、停用列、jvm 雜湊、錨點、下限、jvm-only 兩道格式、同名異義出口)各有一個只有它會擋的案例 | 計劃〈API 決策點〉條款與預期值表 | `t_kt_catalog_api_decision_points` |
| G2 | repair | 壞例檔的 `// BAD` 標記:`//BAD`、`// BAD:`、單獨一行標下一個語句(含 `.`/`?.` 續行、跳過 `@` 註記)都認;`// BADGE` 不算;字串裡的 `//` 不截斷;非 UTF-8 檔回問題不崩 | 規則包壞例樣本慣例(`configs/ast-grep/kotlin-android/rules/` 底下 `// BAD` 標法) | `t_kt_catalog_bad_snippets_reach_rows` 的 `_reach_route_guards` |
| G3 | repair | 片段只有 `…` 或空白時判不通過 | 計劃〈叫不出的壞寫法〉 | `t_kt_catalog_bad_snippets_reach_rows` |
| G4 | repair | 同一個(列, 對應檢查, 片段)出現兩列要報 | 計劃〈叫不出的壞寫法〉 | `t_kt_catalog_bad_snippets_reach_rows` |
| G5 | repair | 主程式載入失敗時,錯誤訊息帶的是載入原因,不被後面 SARIF 迴圈的變數蓋掉 | check.py 的 `check()` | `t_kotlin_rulepack_samples` |
| G6 | repair | 圍欄判讀、正規化、片段拆解、路徑正規化改走既有函式後行為一致;macOS 暫存路徑 `/var` 與 `/private/var` 判成同一檔 | check.py 既有 `_visible_lines`、`_norm`、`_snippets` | `t_kt_catalog_bad_snippets_reach_rows` |
| 全部 | preserve | 真型錄 `python3.14 configs/ast-grep/kotlin-android/check.py --catalog-only` 回 0 個問題 | 型錄自檢的既有合約(推送前會跑) | 修後實跑 |
| 全部 | preserve | 規則包完整模式(有 ast-grep)0 個問題,5 條「規則」改由的單位都對得上壞例 `// BAD` 行 | `t_kotlin_rulepack_samples` | 需 `LUMOS_AST_GREP` 指到 ast-grep 0.51.x |
| 全部 | preserve | 推送前情境段切段(`_kt_sit_path_ok` 共用)對測試檔與一般檔的判法不變 | scripts/lumos `_kt_situation_segments` | `t_kt_situation_segments`、`t_kt_situation_api_family_e2e` |
| 全部 | preserve | 〈統計〉兩組數字(公開名稱 434、壞寫法 111 等)與表一致 | 型錄〈統計〉 | `t_kt_catalog_stats_consistent` |
| D-4 | preserve | D-4 觸發字補了 flatMapConcat/flatMapMerge/mapLatest/transformLatest 之後,樣本檔的 main/alt/反例判定都照標註 | `configs/ast-grep/kotlin-android/samples/situation/D-4.kt.txt` | `-k evidence_samples` |

沒有 preserve 案例的組:G5(載入失敗只有錯誤路徑,沒有正常路徑可比)。
