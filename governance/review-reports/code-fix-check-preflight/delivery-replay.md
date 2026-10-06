# 固定版本重驗

這是編排者的重驗說明，不是新審查席或下一輪。兩份原始 clean 報告沒有 finding 引句，quote-check 不適用；refcheck 只證座標存在，不證語意。原始報告、intake、canary 列均不改寫。首次 none 與第二次空字串的處置集合輸入都被 rc2 擋下；最終依 CLI 指示不帶處置集合，兩個正式記帳列與處置閘皆通過。

Git 標準 bundle 保存凍結審材的提交與分支引用，避免本機壓提交後另一台無法重驗；本包需要本功能前的 main 基準 74d9d1c8，正常 clone main 已有。

```sh
git bundle verify governance/review-reports/code-fix-check-preflight/review-source-history.bundle
git fetch governance/review-reports/code-fix-check-preflight/review-source-history.bundle 'refs/heads/archive/*:refs/remotes/review-sources/archive/*'
python3 scripts/lumos loop replay code-fix-check-preflight --golden governance/replay/code-fix-check-preflight/verdict.json --repo .
```

源碼版為 6839c102eac55a941f5af633371a9def85067564。材料與完整測試均用兩支程式 SHA-256 綁定；最終整併只加入圖譜驗收、卷證與基準線，程式位元必須維持 manifest 雜湊。需要對照原報告行號時，使用 `git show` 讀固定版本並用實際 LF 換行定位；refcheck 的 Unicode splitlines 存在性輸出不是逐字佐證核對。

官方格式與匯入方式：https://git-scm.com/docs/git-bundle
