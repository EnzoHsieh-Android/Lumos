# 探針隔離修補：第二輪差異審處置

凍結審材 `r2-snapshot.patch`，SHA-256 `1519d58a38be5491326dd86f853091fafdcf384abb9240a512d1be80f477ff2c`，558行，僅含 2854d961..730b06fe 的程式與測試修補。正確性與架構席獨立讀這版；兩席收齊後才改程式。正確性席報2條、架構席clean。兩條低共識 major+ 均交唯讀辯方重做臨時 Git 實驗，皆為 agree，沒有降級。

| id | 原席／重現 | 處置 |
|---|---|---|
| R2C1 | 正確性 blocker；HIT：舊副本保留主 Git `worktrees/*/gitdir` 指向真 linked worktree，辯方從副本執行 `git worktree repair` 後真 linked `.git` 改指副本，刪副本後外部 worktree 不可用。 | folded：副本建立前拒絕主 Git `worktrees/`；`t_probe_boundary_review2_linked_worktree` 前置證明 linked 指標存在，舊碼拒絕斷言紅，修後綠且外部 byte 不變。 |
| R2C2 | 正確性 major；HIT：父環境四個 `GIT_AUTHOR_*`／`GIT_COMMITTER_*` 值會蓋過 fake config，舊快照與後續提交均帶真身分；只讀 config 的測試假綠。 | folded：`_git_env` 清除四項及同前綴變數，儀器與兩種 runner 共用；`t_probe_boundary_review2_effective_identity` 真的做快照與後續提交核作者/提交者，舊碼兩個斷言紅，修後綠。 |

編排者另自查 `global_skills_health()` 讀取拋錯時被當成普通題失敗而繼續後題，最終讀取拋錯甚至不寫結果。這是非席位發現，不列進上表兩條或 `--findings-set`。同一修補加入 `t_probe_boundary_review2_health_unreadable`；舊碼下一題仍跑且 fatal=false，修後中途立即停批、最終檢查失敗也留下 JSON 的 fatal/inconclusive。

初次修前定向測試 3 passed / 4 failed；新增最終檢查情境後修後定向 8 passed / 0 failed。完整 `python3.14 scripts/test_lumos.py -k probe_` 為 251 passed / 0 failed，輸出在 `r2-postfix-regression.txt`；`py_compile` 與 `git diff --check` 通過。沒有真模型、真網路推送或全套測試。第二輪的修補仍待第三輪審查，這些綠燈不是五案試行收斂率。

本輪 `lumos loop next` 在首輪 `--disposal` PASS 後誤走已退場 panel 路由而 rc2；見 [[Issues/代碼審next把新處置帳誤判舊panel]]。派工以凍結快照、兩席原報告及本 intake 留痕；用 `loop status --disposal` 判定，沒有改寫錯帳或把 rc2 當審查 FAIL。
