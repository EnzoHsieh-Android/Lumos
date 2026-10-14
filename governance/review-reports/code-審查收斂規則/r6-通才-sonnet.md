severity: minor

## 回歸檢查結果

**已讀,無 finding 的部分**
- 沒有殘留的 repo:起點索引沒有任何殘留時,`bnotes` 是空的,`_residual_note_hits` 不會產生任何命中。照常出 light,只改 README 也不升級。`docs/README.md` 不在圖譜資料夾,`_residual_graph_file` 回 False。
- `asks_dropped` 語意改變:全 repo 只有 `_residual_tier_reasons_bad` 一處讀它,舊的 `-1` 分支已隨之移除。新的 `asks_unknown` 只在治理帳被動到時才設,沒有殘留的讀者受影響。
- 鏡頭快取 schema 升 5:`_LENS_SCHEMA` 進快取鍵,舊快取自然 miss,測試也同步改成 5。
- 拿掉 `_git_env_no_replace` 與 `no_replace=`:全 repo 已無殘留參照。`_lens_git` 的其餘呼叫者簽名沒變,`_residual_blob_at` 改走 `_lens_git` 後,讀不出與 missing 的判定與舊版一致。`time` 在檔頭已匯入,`deadline` 預設 None 時行為不變。
- 入口清 git 環境:我實測 `GIT_GRAFT_FILE=/dev/null/...` 在 git 2.39.2 下 `log`、`commit`、`diff`、`worktree list` 都不報錯也不警告。測試要在入口執行的路徑上才有保護,而 pre-push 走子命令進 `main()`,所以有涵蓋。
- 我實跑 `python3.14 scripts/test_lumos.py -k residual`:403 通過,0 失敗。
- 實驗倉庫在 `cr-rc6-通才/` 下,審完要刪(尚未刪,屬自己建的)。

## Finding

severity: minor
blocking: 否 — 只影響升級後第一次,而且訊息已教使用者跑 `--reindex`,不會放行壞東西
引句:「索引裡的 {_kill_esc(g[0])}(指紋 {_kill_esc(g[1])}、殘留」
問題:`_residual_index_row_key` 把 `notes` 納入比對鍵,`_residual_index_entries` 也新增了 `notes` 欄。沒有 `notes` 欄的既有索引(升級前產生的)會被 `lumos doctor` 的索引比對判成「索引的 notes 跟圖譜不同」。同時 `_residual_index_notes` 讓所有舊索引條目的筆記變成 None,於是只要改到任何圖譜檔,就會觸發 `notes_unknown`,升成 high。
具體失敗情境:消費專案升級 lumos 後,索引裡已有殘留但還沒重跑 `lumos guard residual --reindex`。這時 doctor 報不一致,每次只動筆記的推送都被判 high,要走代碼審。這是升級路徑上的摩擦,不是漏判。
佐證:``file: `scripts/lumos:19336` ``(`_residual_index_row_key` 把 notes 納入鍵)、``file: `scripts/lumos:44631` ``(`_residual_index_notes`,notes 缺時設為 None)。
本 repo 的 `governance/` 底下目前沒有 `residual-index.json`,所以這一輪實測不會踩到。

最高等級 minor,blocking 0 條。
