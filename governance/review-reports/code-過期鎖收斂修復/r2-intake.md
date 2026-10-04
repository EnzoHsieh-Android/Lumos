# code-過期鎖收斂修復 r2 收貨與處置

審材：`r2-snapshot.patch` 是 r1 修補的 222 行差異，SHA256 `92df0e9a9032663ea0c6f718018358ecf9fba995bc354589289e1c95368ee546`。兩席先獨立收齊；架構席 clean，正確性席回一條 major。正確性席報告的引句錨定於當輪凍結 patch，`report-normalize`、`quote-check`、`refcheck` 通過；`seat-check` 僅有未逐字點名材料的觀測提醒，無越界引句。報告原文存 `r2-single-reviewer.md`、`r2-architecture.md`。

## 重現與去向

| ID | 觀察及編排者重現 | 去向 |
|---|---|---|
| F1 | HIT。無 `getuid` 且派工快取目錄連到外部時，等待端首、次呼叫均 rc5、只啟動一次背景、在外部留下 `.warming`；`t_lens_untrusted_cache_never_creates_external_lock` 的目錄不可信前置成立且核心斷言先紅。建鎖前改走既有逐層私有目錄判準後轉綠，兩次均回既有 lock_error、Popen 零次、外部無鎖。 | 折入；major，code。 |

`t_lens_trusted_cache_still_spawns_warmer` 反向驗合法私有目錄仍建鎖與啟動一次背景；此測試全綠。以任意暫存路徑呼叫等待 helper 的舊單元測試只隔離新目錄守衛，專項負向／正向測試和真背景整合測試保留真實守衛，避免以 mock 冒充入口驗證。相鄰 `lens_spawn_failure` 7、`lens_warmer` 13、`lens_stale_lock_reports_uncertainty` 9、期限末 2 條斷言均全綠。修後累積差異為 `r2-result.patch`；第三輪必須由全新席審這次補丁與相鄰回歸，且是本迴圈上限。

外家否決席未取得；standard 編制結論限於同家族審查與本地實測。
