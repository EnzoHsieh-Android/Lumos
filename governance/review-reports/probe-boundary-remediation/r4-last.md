# r4 最後全新差異席原報告

材料核對：`r4-last-snapshot.patch` SHA256 `55971cefc174d106ff86b14a5b6d45b6be1b6ddee6781ce1d8f00b8c9e0102e6`、235 行，HEAD 為 `79d3f371`。

live schema 與型別：已讀，無 finding。
severity: clean
blocking: 否。
引句：「or type(d.get("fatal")) is not bool or type(d.get("inconclusive")) is not bool」
file: `governance/eval/ablation_lumos_first.py:185`。
`results`、逐列 dict、兩個布林與健康清單均在 live 邊界驗證；缺欄、錯型、半檔會設 stop。

普通 rc1 與真 producer 契約：已讀，無 finding。
severity: clean
blocking: 否。
引句：「return 0 if p == n else 1」
file: `scripts/scenario_probe.py:1175`。
真 producer 正常落檔必寫三個健康欄；普通題失敗回 rc1，與測試替身一致，仍可採信。

舊歷史輸出互讀：已讀，無 finding。
severity: clean
blocking: 否。
引句：「if invalid_batch_evidence(d):」
file: `governance/eval/ablation_lumos_first.py:104`。
新 schema 強檢只在 `run_job` 的 live 產物；`load_results` 仍以舊新共用失效證據讀歷史檔，未強迫舊健康檔補新欄。

停批訊號、summary 與 rc：已讀，無 finding。
severity: clean
blocking: 否。
引句：「if live_failed and not poisoned:」
file: `governance/eval/ablation_lumos_first.py:351`。
記憶體 stop 在事後磁碟重掃後仍轉成 `skills_health_poisoned`，完全缺檔也會寫入 summary 並回 rc3。

測試有效性：已讀，無 finding。
severity: clean
blocking: 否。
引句：「stop.is_set() is (shape != "valid")」
file: `scripts/test_lumos.py:37634`。
獨立重跑第四輪定向測試 12 passed；原消融讀取測試 23 passed。缺檔、半檔、缺欄、錯型、有效 rc1、舊事故檔及頂層 rc/summary 均有覆蓋。

總結：最嚴重 severity: clean，blocking: 0 條。
