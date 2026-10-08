severity: blocker
審材：governance/review-reports/探針隔離與清理收斂/r1-snapshot.md

根因與取捨

F1：有效 Git 設定只驗 remote 與 hooksPath，但副本隨後執行 `git add -A`；來源可用 `filter.<name>.clean` 在模型啟動前執行外部程式、寫出副本外，隔離邊界仍可穿透。

severity: blocker
blocking: 是
引句:「此邊界只涵蓋繼承的 Git 設定及意外 `git push`，不宣稱封住模型主動指定 URL、停用 hook 或以其他網路工具外送」
file: `scripts/scenario_probe.py:561`

最小重現：在臨時來源 `git config filter.escape.clean "sh -c 'printf hit > $root/outside-marker; cat'"`，再以 `.gitattributes` 令 `*.txt filter=escape`、建立 `payload.txt`；呼叫 `make_sandbox`，本席實跑得到副本外 `outside-marker`，發生在 runner 啟動前。設計需在首次可能套用 filter 的 Git 命令前，明定禁用／拒絕 clean、process、fsmonitor 等可執行設定，並以副本外 byte-equal 反例驗收；只驗 remote 與 hook 不足。

驗收條款

F2：邊界建立失敗時，`--keep` 的契約互相衝突；同一輸入無法同時滿足 S2 的「清理副本」與 S3 的「各次保留」。

severity: major
blocking: 是
引句:「local include、worktree config 或錯誤返回若導致結果不符，刪除本次副本並報儀器錯誤；不得當作模型失敗。」

最小重現：以啟用 `extensions.worktreeConfig`、在 worktree scope 保留 remote 並覆寫 hooksPath 的普通 clone 執行 `scenario_probe.py --keep --repo <repo>`。若刪除拒絕現場，違反「`--keep` 各次保留並列出路徑」；若保留，違反 S2「應失敗並清理」。規格需明定 `--keep` 是否涵蓋「模型尚未啟動、邊界驗收失敗」的副本，以及此時路徑是否仍要印出。

先紅後綠與邊界、實務隱患、回退、審計修正紀錄皆已讀；除 F1 所述缺少可執行 Git 設定反例外，無額外 finding。

總結：最嚴重 severity 為 blocker，blocking 共 2 條。
