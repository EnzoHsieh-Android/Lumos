severity: clean

我只讀了 r2-snapshot.patch 和鄰居檔,沒讀 r2-repair.patch,也沒跑測試。修補的新增內容全在 r2-snapshot.patch 裡,三問都沒有不對齊。

**1. 分層與依賴方向:跟鄰居一樣**
- 改動全在 `scripts/scenario_probe.py` 的 `_attempt_ledger_transaction` 內部。對外的 `attempt_ledger_remaining` 和 `claim_model_attempt` 仍是原本那兩層薄包裝,簽名沒變,只轉傳 `now=`。file: `scripts/scenario_probe.py:1048`
- 沒有新 import 或跨層呼叫。`math` 本來就在函式內 import,`sqlite3` 也是函式內 import。file: `scripts/scenario_probe.py:982`
- 測試放進 `TestScenarioProbeAblation`,也就是既有用量帳測試所在的類別。file: `scripts/test_autonomous_loop.py:1987`
- 包裝測試放在 `t_scenario_probe_collect_only_and_answer_cap` 旁邊,同樣子程序呼叫 `scripts/test_autonomous_loop.py` 並傳測試名。file: `scripts/test_lumos.py:109571`

**2. 命名與錯誤處理:跟鄰居一樣**
- 例外一律用 `ProbeAttemptLedgerError`。訊息「用量帳時鐘不可判」沿用原字樣,只是多了一個拿鎖後才檢查的出口。
- 函式內放小函式 `clock_ok` 是檔裡已有的寫法(`is_instr`、`run_at` 也是巢狀)。file: `scripts/scenario_probe.py:1238`、`scripts/scenario_probe.py:1514`
- 測試控制時間的方式沿用既有做法:`mock.patch.object(self.sp.time, "time", ...)`,以及傳 `now=`。file: `scripts/test_autonomous_loop.py:1987`、`scripts/test_autonomous_loop.py:2005`
- 包裝測試的命名是 `t_` 開頭,斷言用 `check(..., run.returncode == 0 and f"Ran {len(names)} tests" in output, output[-4000:])`,跟第一個鄰居完全同形。timeout 也同為 120。file: `scripts/test_lumos.py:109571`
- 第二個鄰居 `t_qo_ablation_scorer_suite` 多一個 `_need_src` 前置檢查,新測試沒有。但那條檢查是因為被測檔在 `governance/eval/` 下才需要;這裡被測檔是 `scripts/scenario_probe.py`,沒帶也不算偏離。file: `scripts/test_lumos.py:109559`
- 圖譜筆記的 PITFALL 帶了必有的 `[出處:]`、`[根因:]`、`[test:]` 三欄,另加 `[修法:]`,都在規定的格式內。鍵的先後順序在 CLAUDE.md〈寫筆記時〉沒有硬性規定,既有 PITFALL 行也是把 `[修法:]` 放在 `[test:]` 之前,這裡順序相反,不列。
- 筆記的 `updated` 和簽名基準線的 `note` 欄都照現有寫法更新。

**3. 第二種做法:沒有**
- 時鐘合法判斷原本是行內的一條 `if`,現在收成函式內小函式,判斷條件逐字相同,沒有另起一套。
- 「拿鎖後才讀時間」沿用原本的 `BEGIN IMMEDIATE` 之後插入一步,沒有新增鎖機制或重試。
- 新測試的「模擬另一方搶先記帳」用 `mock.patch.object(sqlite3, "connect", ...)` 在連線時插入一筆。既有的搶名額測試則用子程序和真實鎖(`sqlite3.connect(ledger, isolation_level=None)` 先持鎖)。這是單程序決定性模擬對多程序真跑,測試手法略有不同。它是在同一類別裡補一個確定性重現,不取代舊測試,我歸為純風格,不列。file: `scripts/test_autonomous_loop.py:2016`

不對齊共 0 條,其中 major 0 條
