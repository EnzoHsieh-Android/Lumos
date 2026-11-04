# r3 待驗案例(修前 6e10ae5b → 修後 d4bbaaea 之後的帳本提交)

案例只是待驗範圍,不是「已修好」的證據;新席自己核對、可補案例。改壞驗證原始結果在同目錄 r2-repro.txt。

| 組 | 角色 | 待驗行為 | 出處 | 案例 | 修前 | 修後 |
|---|---|---|---|---|---|---|
| G1 | repair | 只寫 remote.<名>.promisor/partialCloneFilter 的複製也認成部分複製,不為判祖先連遠端 | 計劃做法 1 d、S8 | t_redbase_branch_rows_fallback_keeps「只寫 promisor 的部分複製」 | 修前沒有案例(r2 席以 git 2.39 實測照樣連遠端) | 綠;改壞 J1 紅 |
| G1 | repair | 回頭條件那支也用同一個判斷 | 回頭條件計劃 | t_drift_born_unknown「③partial clone」 | 綠(只測舊式設定) | 綠;改壞 J6 紅 |
| G1 | preserve | 舊式 extensions.partialClone 照認、不連遠端 | 計劃 S8 | 同支「部分複製」三條 | 綠 | 綠;改壞 H2 紅 |
| G2 | repair | 帳被忽略時不算分岔點、不讀那一版 | 計劃做法 1 讀取 | 同支「帳被忽略:不算分岔點」 | 修前會算(r2 資源席實測部分複製卡 60 秒) | 綠;改壞 J2 紅 |
| G2 | preserve | 帳判不了有沒有被忽略時照舊算分岔點、不過濾 | 計劃做法 1 | 同支「判不了帳有沒有被忽略」與 ★對照★ | 沒有案例 | 綠;改壞 J5 紅 |
| G3 | repair | 分離 HEAD 只看祖先;還沒有提交的 HEAD 不崩、照留 | 計劃天花板二、做法 1 b | 同支「分離 HEAD」「還沒有提交的 HEAD」 | 沒有案例 | 綠;改壞 J3、J4 紅 |
| G3 | repair | 同名重開案例有前置斷言 | 測試假綠形態 | t_spec_gate_redbase_green_other_branch ★前置★ | 沒有 | 綠 |
| G4 | preserve | 有同名 tag 時分支名照樣對得上(取分支名改借回頭重讀那支) | 計劃 S2 | 同支 S2 同名 tag | 綠 | 綠;改壞 H4 紅 |

未覆蓋:真實的 blobless/treeless 遠端複製(用設定與留記號的腳本代替)、Windows、時鐘倒退、大 repo 沒有 commit-graph(寫成天花板)。
