severity: major  
blocking: 是  
逐字引句:「`--max-per-window 0` 仍明示不設限制」  
佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:28`

同份設計又要求兩個 runner 每次都先 claim，且新帳建立後封鎖五小時，卻未規定 `max-per-window=0` 必須繞過建帳與 claim。

具體輸入：全新主機、帳檔不存在、執行 `scenario_probe.py --max-per-window 0`。  
推導：若照第 29、31 行無條件初始化與 claim，會因新帳冷卻五小時而停止；但第 28 行明確承諾 0 是不設限制。現有零值語意也會直接啟動模型（`scripts/scenario_probe.py:954`、`scripts/scenario_probe.py:1040`、`scripts/scenario_probe.py:1050`）。需明定零值完全不開帳、不查帳、不 claim，或改寫零值承諾。

severity: major  
blocking: 是  
逐字引句:「其後被本機額度拒絕的重試應零新增 launch-intent，且不再先等待300秒」  
佐證 file: `governance/review-reports/probe-attempt-ledger/r1-snapshot.md:39`

驗收要求「額度已滿時不先等 300 秒」，但設計把重新 claim 放在 `run_one`／`run_one_codex` 內；現有 `main` 則在下一次呼叫 runner 以前就先睡眠。

具體輸入：`max-per-window=1`、`wait-on-limit=300`，第一個模型啟動已成功 claim，隨後回傳供應商 limit。  
推導：`main` 在看到 `limit_hit` 後立即執行 `time.sleep(300)` 並 `continue`（`scripts/scenario_probe.py:1115`、`scripts/scenario_probe.py:1120`、`scripts/scenario_probe.py:1121`）；第二次 claim 尚未發生，因此 runner 內的交易無法阻止這次睡眠。設計需指定睡眠前的同帳額度檢查或調整 claim／等待順序。

實際覆蓋：完整初讀 52 行凍結 snapshot；核對 `scripts/scenario_probe.py` 的 `run_one_codex`、`run_one`、`main`，以及 `governance/eval/ablation_lumos_first.py` 的 `run_job`。總閱讀低於 1800 行；未讀其他報告、作者 intake、秘密，也未呼叫外部服務或寫檔。

未驗資格：未執行模型、程序死亡或 SQLite 故障注入；未驗尚不存在的 helper 實作，因此不對連線關閉、rollback、schema 驗證或檔案權限宣稱已正確，只審查凍結設計能否唯一導出正確行為。