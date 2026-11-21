# r3 待驗案例(修前 826ce8451 → 修後見 r3-repair-binding.json 的 after_commit)

案例只是待驗範圍,不是「已修好」的證據;新席自己跑兩版核對,可補案例。測試指令一律 `python3.14 scripts/test_lumos.py -k <關鍵字>`;修前版本用 `git -C <臨時目錄> worktree` 或 `git show 826ce8451:scripts/lumos` 取。

| 組 | 角色 | 待驗行為 | 出處 | 選例依據 |
|---|---|---|---|---|
| G1 | repair | Kotlin 專案沒有任何遠端 → pass 預判印「沒有遠端,選擇點留給推送前判」、rc 0、照常記通過;把那條放行改成擋下時測試要紅 | 計劃〈做法〉沒有遠端留給推送前判 | 席位指出那條沒有測試守 |
| G2 | repair | 有兩個遠端(都不是 origin)、分支沒設上游 → 印「判不出要比對哪個遠端」並教 `git config branch.<分支>.remote`,不印「沒有遠端」,rc 0 | git-push 文件預設遠端順序(上游→origin) | 席位實跑反例 |
| G2 | preserve | 有 origin,或分支設了上游 → 照常算範圍、照推送前同一圈判定(擋下時擋、沒問題時記通過) | 計劃 S1、S2、S10 | 既有斷言 t_codeloop_pass_choice_blocks、t_codeloop_pass_choice_range |
| G2 | preserve | detached HEAD、不是 Kotlin 專案 → 跟修前一樣(印「沒有分支」/不印字) | 計劃 S12 | 既有斷言 |
