# 第二輪低共識發現辯方核對

唯讀辯方對凍結版 730b06fe 的兩條 finding 均判 agree，未找到反證；實驗只在 TemporaryDirectory 內進行，沒有修改工作目錄。

R2C1：一般 repo 有 linked worktree 時，舊 `make_sandbox` 接受；副本 `git worktree list --porcelain` 列出外部路徑。從副本執行 `git worktree repair <真實linked>` 回 rc0，外部 `.git` 指到副本；刪除副本後外部 `git status` 回 rc128。現象成立。辯方認為修法可在首次模型／Git 寫入前拒絕或移除副本 `.git/worktrees/*`，並驗外部 byte 不變。

R2C2：父環境四個 `GIT_AUTHOR_*`／`GIT_COMMITTER_*` 值下，副本 config 顯示 probe，但快照與後續模型式提交作者/提交者仍為環境的真身分；移除環境值再提交才回 probe。現象成立。辯方認為清除或固定環境變數、測試真提交的 `%an/%ae/%cn/%ce` 是適當最小修法。
