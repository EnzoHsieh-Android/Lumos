C1. pre-commit 有一道 Gate DG（位於 Gate CC 旁），呼叫 `lumos delguard --staged` | 預期驗證點: scripts/hooks/pre-commit（Gate DG / Gate CC 標記、delguard --staged 呼叫）

C2. S1 從 staged diff 的 `-` 行抽取被刪識別字，使用 per-file 回收表與 stopword，排除域路徑段，且 lockfile 與 .md 檔不抽 | 預期驗證點: delguard S1 抽取邏輯實作（lockfile/.md 排除判斷）

C3. 信心判定用單次 `git grep --cached` 判斷兩檔：符號在全域皆消失 = high confidence，呼叫點仍殘存 = low confidence | 預期驗證點: delguard 信心判定函式中的 `git grep --cached` 呼叫與 high/low 分級邏輯

C4. 掃描 vault 用三件套 regex 找「還在講它」的節點與原句，型別只用來排序不壓低命中，Systems 型別排最前 | 預期驗證點: delguard 掃描函式中的 regex 組合與 Systems 排序邏輯

C5. S2（純連結編輯，屬 LINK_KEYS 子集）若同時命中 S1，判定為「假同步嫌疑」（fake_sync） | 預期驗證點: delguard S2 實作、LINK_KEYS 常數定義、fake_sync 判定條件

C6. S3 在 stdout 印出「退場三問」 | 預期驗證點: delguard S3 實作的 stdout 輸出內容

C7. advisory 機制恆回傳 rc0（exit code 0）：crash 用 `|| true` 與 `except Exception` 兜底、timeout 用 python 內建 deadline（環境變數 LUMOS_DELGUARD_DEADLINE，預設 2.0 秒）、git diff rc≠0 皆降級放行，降級訊息走 stdout | 預期驗證點: delguard 主流程 return code、`|| true` 用法、`except Exception` catch、LUMOS_DELGUARD_DEADLINE 讀取與預設值 2.0

C8. `--json` 輸出包含欄位 tokens/hits/fake_sync/degraded | 預期驗證點: delguard `--json` 輸出 schema

C9. 快照契約為 staged index：git grep 用 `--cached`；git diff 帶 `-M`，並搭配 `-c core.quotePath=off -c diff.noprefix=false -c diff.mnemonicPrefix=false` | 預期驗證點: delguard 內 git diff 呼叫參數

C10. vault-only repo（graph_root=="."）時 delguard 靜默 return 0 | 預期驗證點: delguard 對 graph_root 值的判斷分支

C11. 先驗參數 cap=40（DELGUARD_TOKEN_CAP）、top-10（DELGUARD_TOP_N）；超過 cap 時保留高信心逐條，且統計行不清零 | 預期驗證點: delguard 原始碼中 DELGUARD_TOKEN_CAP=40、DELGUARD_TOP_N=10 常數與超 cap 分支邏輯

C12. 排除域與 pre-commit 的 should_exclude 對齊，共 7 目錄 + lockfile 三檔名；此清單由 t_precommit_whitelist_drift_guard 測試釘住以防第三份清單漂移 | 預期驗證點: scripts/hooks/pre-commit should_exclude 函式（7 目錄+3 lockfile）；scripts/test_lumos.py 中 t_precommit_whitelist_drift_guard

C13. S3 問句同步收錄在 lumos-project-notes skill 的退場段 | 預期驗證點: lumos-project-notes skill 檔案中退場段落是否含 S3 問句

C14. 測試 t_delguard 位於 scripts/test_lumos.py，共 85 條，涵蓋 S1 抽取/信心/掃描/S2/S3/fail-open/deadline/邊界輸入/鑑別力翻紅驗證 | 預期驗證點: scripts/test_lumos.py 中 t_delguard 相關測試函式數量

C15. 全量測試在 commit 95c4224 時為 2515/0（全數通過） | 預期驗證點: git commit 95c4224 附近的測試執行結果紀錄
