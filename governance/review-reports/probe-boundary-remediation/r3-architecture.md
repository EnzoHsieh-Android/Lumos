severity: clean
blocking: 否

比較範圍：凍結 patch SHA256 `cdbfac731efbea0d59b566865cc2cf1c307954e515f038202c976870274e21e5`，730b06fe..cfe7a703，235行。

分層與依賴方向：已讀，無 finding。Git 環境清洗集中於 `_git_env()`，Claude／Codex runner 與沙盒 Git 命令共用同一入口。專用 `ProbeHealthError` 沿用既有 `SourceProbeCleanupError` 的錯誤分類，沒有第二套 Git 執行器、健康檢查器或沙盒生命週期。linked worktree 與提交身分測試用臨時真 Git repo，健康檢查例外測試只 mock 分流與輸出；計劃與 `Systems/codex-harness` 對齊。

驗證：`probe_boundary_review2` 8 passed，`probe_boundary_` 45 passed，`probe_source_probe_git_env` 1 passed。架構席未發現新問題。
