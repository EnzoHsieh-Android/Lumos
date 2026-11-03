# r4 待驗案例(修前 fe970227 → 修後 c8ce2022 之後的帳本提交)

案例只是待驗範圍,不是「已修好」的證據;新席自己核對、可補案例。
修前欄是實跑:開停在 fe970227 的暫存工作樹、放進修後的測試檔、`-k` 逐支跑(2026-11-04)。改壞驗證原始結果在同目錄 r3-repro.txt。

| 組 | 角色 | 待驗行為 | 出處 | 案例 | 修前(實跑) | 修後 |
|---|---|---|---|---|---|---|
| G1 | repair | 裸鍵 promisor、promisor = 2 認成部分複製;遠端名含空白且 promisor = false 不認 | git 布林規則、計劃做法 1 | t_git_partial_clone_keys 三案 | 紅(三條) | 綠;改壞 K1、K2、K3 紅 |
| G1 | repair | 回頭條件那支判不了是不是部分複製時判不了 | 計劃 S8、回頭條件計劃「每一步有一點不確定就判不了」 | t_git_partial_clone_keys「S8 判不了是不是部分複製」 | 紅 | 綠;改壞 K4 紅 |
| G1 | preserve | 三個設定各自單獨就算、promisor 為假不算 | git 部分複製設計文件 | t_git_partial_clone_keys 其餘八案 | 綠 | 綠;改壞 K7 紅 |
| G2 | repair | 帳進版控的部分複製不讀分岔點那一版、印一句 | 計劃 S10 | t_redbase_branch_rows_fallback_keeps「S10」 | 紅 | 綠;改壞 K5 紅 |
| G2 | repair | SHA-256 的 repo 帳被忽略時同分支判綠照算 | 計劃做法 1 讀取 | 同支「S8 SHA-256」 | 紅 | 綠;改壞 K6 紅 |
| G2 | preserve | 帳被忽略時不算分岔點;判不了帳有沒有被忽略時照舊算分岔點 | 計劃做法 1 | 同支「帳被忽略」「判不了」兩條 | 綠 | 綠 |
| G3 | 守衛 | 回頭條件那側認新式部分複製(只寫 promisor 與 filter) | 回頭條件計劃第 5 點 | t_drift_born_unknown「③新式 partial clone」 | 綠(行為 r2 已改對,r3 補的是沒有測試) | 綠;改壞 K8(改回只看 extension)紅 |
| G4 | 測試 | 兩處淺複製、部分複製呼叫改傳秒數 | — | t_redbase_branch_rows_fallback_keeps | — | 綠 |

未覆蓋:真實的 blobless/treeless 遠端複製(用設定、重打包與留記號的腳本代替)、Windows、git 2.39 以外的版本、時鐘倒退、大 repo 沒有 commit-graph(寫成天花板)。
