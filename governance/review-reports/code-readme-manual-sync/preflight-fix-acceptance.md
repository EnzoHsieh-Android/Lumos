修復驗收結果：PASS。原正式報告與 severity 保留不變。

- Finding 1 已折入：`[來源:…]` 已復原，INDEX 為 4494 字元。相關測試 8/8、14/14 通過。
- Finding 2 已折入：考卷模式與 history 模式已拆開，明寫 `--history` 不讀考卷。表格測試 2/2 通過。
- `git diff --check` 通過。

本次未重開全掃，沒有新增驗收 finding。
