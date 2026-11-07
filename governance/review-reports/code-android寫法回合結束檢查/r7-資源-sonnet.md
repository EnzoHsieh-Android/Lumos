severity: minor

第六輪資源席本來是 clean。我照原鏡頭重看了這輪的 patch。這輪沒有新增 `Popen` 或背景程序,所以子程序群組沒有新的退出路徑。也沒有新增暫存檔或登記檔。`_git_status_entries` 也沒有多開 git 呼叫:`main()` 把原本的 `_repo_top` 往前挪了,並把結果傳進去。

F1 是效能問題,上限可預期,所以只標 minor。
`_rel_in_project` 對每一筆條目都重新做 `project_root.resolve()` 和 `top.resolve()`。前綴 `pfx` 對所有條目其實相同,卻重算了 N 次。我實測結果如下:
- 2,000 筆約 0.074 秒。
- 50,000 筆約 1.7 秒,約 34 微秒一筆。
- 外推 30 萬筆未跟踪檔約 10 秒,會吃掉收工點名約 30 秒預算的三分之一。

這份成本是這輪新增的。出口濾器上線前,每筆條目只做常數時間的運算。
失敗場景是 repo 裡有很大一批未被 ignore 的未跟踪檔(例如建置產物)。一般專案只有幾十到幾千筆,不會碰到。
修法是把 `pfx` 在 `_git_status_entries` 算一次,再傳進 `_rel_in_project`。

引句:「pfx = project_root.resolve().relative_to((top or project_root).resolve()).parts」
file: `scripts/hooks/claude/check-graph-sync.py`(`_rel_in_project`,檔案的行號區間見 patch 第 414-425 行)
severity: minor
blocking: 否

我另外查過這幾項,沒有標成 finding:
- 三支 shell 掛鉤的 PATH 過濾迴圈每圈都重切字串,所以是平方時間。我用 10 萬項的 PATH 試,180 秒仍沒跑完,已手動停掉。但 PATH 是環境變數,不是 repo 能控制的,一般只有幾十項,沒有可用的觸發場景,所以不標。
- `_lumos_any_python` 新增的 `case` 沒有迴圈和程序,沒有成本。
- 影響分析 `--worktree-nofilter` 的 SARIF/大輸出路徑這輪沒動。

我已刪掉臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/資源-sonnet`,也沒有改動 repo。

總結:最嚴重是 minor(`_rel_in_project` 每筆重複 resolve,5 萬筆約 1.7 秒),會擋 0 條
