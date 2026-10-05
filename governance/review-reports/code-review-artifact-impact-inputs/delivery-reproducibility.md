# 交付後重驗第三輪

本檔是編排者的重驗說明，不是新席報告或第四輪。原始報告、snapshot 與 canary 帳列維持原樣。乾淨副本核對見 delivery-reproducibility-audit.md。

Git 官方 bundle 可轉移物件與引用並透過 git fetch 讀取。本次借用既有格式保存壓縮前的審材與測試版本，功能分支歷史維持一個功能提交與一個帳本提交。來源：https://git-scm.com/docs/git-bundle

## 恢復歷史物件與可驗的引用

從專案根執行。增量包需要 main 的 ce2a961f 與56f38db9歷史；完整下載本功能分支已包含這兩個基準。

```sh
git bundle verify governance/review-reports/code-review-artifact-impact-inputs/review-source-history.bundle
git fetch governance/review-reports/code-review-artifact-impact-inputs/review-source-history.bundle 'refs/heads/archive/*:refs/remotes/review-sources/archive/*'
```

fetch 同時恢復物件與遠端追蹤引用，符合既有釘版檢查需要 branch 包含提交的規格。歷史包SHA與引用清單見 delivery-reproducibility-manifest.json。

## 原報告座標按派工版本解讀

以下只補原引用的版本，不修改原席報告。refcheck 驗座標存在；原報告對 snapshot 的 quote-check 驗引句來源。兩者分別核對。

### r3-correctness.md

引句:「一般改名仍取新路徑；只有簿記終點被排除時，不能把舊程式刪除一起藏掉。」

file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:24432`

file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:24433`

### r3-architecture.md

引句:「一般改名算新路徑；跨到被排除的簿記終點另保留舊程式、讀起點版本。」

引句:「Verification/2026-10-06_附件種子修復獨立驗收」

file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:24433`

file: `docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md@9a6e21e49a96677db09286a63beaf38f381a0104:31`

file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md@9a6e21e49a96677db09286a63beaf38f381a0104:48`

file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:794`

### r3-orchestrator-utf8.md

引句:「candidates = [os.fsdecode(f) for f in r.stdout.split(b"\0") if f]」

file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:41342`

## 重驗指令

```sh
python3 scripts/lumos refcheck governance/review-reports/code-review-artifact-impact-inputs/delivery-reproducibility.md --repo .
python3 scripts/lumos refcheck governance/review-reports/code-review-artifact-impact-inputs/r3-orchestrator-utf8.md --repo .
python3 scripts/lumos loop fix-check code-review-artifact-impact-inputs --round r3
```

兩個正式席原報告的未釘行號由本檔補足版本；原 draft 未採用，不當正式卷證。原報告对 snapshot 的 quote-check 結果保留。歷史包為重驗資料，不改當前checkout。


## 引句在派工版本的精確位置

原報告列的佐證座標與引句位置分別保留。下面位置由9a版檔案逐字搜尋得出；每條都附版本與原文，不把refcheck的「行存在」當成「引句匹配」。

來源報告：r3-correctness.md
引句:「一般改名仍取新路徑；只有簿記終點被排除時，不能把舊程式刪除一起藏掉。」
file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:24432`

來源報告：r3-architecture.md
引句:「一般改名算新路徑；跨到被排除的簿記終點另保留舊程式、讀起點版本。」
file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:24410`

來源報告：r3-architecture.md
引句:「Verification/2026-10-06_附件種子修復獨立驗收」
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md@9a6e21e49a96677db09286a63beaf38f381a0104:48`

來源報告：r3-orchestrator-utf8.md
引句:「candidates = [os.fsdecode(f) for f in r.stdout.split(b"\0") if f]」
file: `scripts/lumos@9a6e21e49a96677db09286a63beaf38f381a0104:41342`

