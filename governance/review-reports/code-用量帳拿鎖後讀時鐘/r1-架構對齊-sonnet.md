severity: minor

我只讀了凍結 patch 和鄰居檔案,沒有跑任何測試,也沒有改檔。

**1. 分層與依賴方向:對齊。**
- 新碼留在原本的 `_attempt_ledger_transaction`(`scripts/scenario_probe.py`),沒有新增函式、跨層呼叫或新依賴。
- 它仍只靠函式內 `import math` 和 `import sqlite3`,對外 API 沒變。`attempt_ledger_remaining` 和 `claim_model_attempt` 也維持原樣(`scripts/scenario_probe.py:1038-1043`)。
- 模組已有的 `time.time()` 用法在 `scripts/scenario_probe.py:1075,1106,1174`,新碼沿用同一用法,沒有改成 `datetime` 或自己包一層時鐘函式。
- 測試放在 `TestScenarioProbeAblation` 的帳本測試群(`scripts/test_autonomous_loop.py:1920-2077`)。
- 筆記補在這兩支檔的家 `Systems/codex-harness.md`(`about_code` 有列 `scenario_probe.py`),符合家規。

**2. 命名與錯誤處理:大致對齊,有兩處小不一致。**
- 命名:測試名 `test_attempt_ledger_reads_clock_after_lock` 跟鄰居 `test_attempt_ledger_*` 同一前綴。
- 錯誤處理:新增的時鐘不可判一律丟 `ProbeAttemptLedgerError("用量帳時鐘不可判")`,訊息文字跟原本一字不差。這個丟出發生在外層 `try` 之內,會被 `except Exception` 原樣重丟(`scripts/scenario_probe.py:1036-1038`),`finally` 也會回滾並關連線。
- 時間控制的兩條路:
  - 有傳 `now` 時行為不變,既有測試不受影響。
  - 沒傳時用 `mock.patch.object(self.sp.time, "time", ...)`,跟鄰居 `scripts/test_autonomous_loop.py:1987,2005` 一樣。這點對齊。
- 不一致之處見 A1、A2。

**3. 第二種做法:有一處。**
- 模擬並發的方式:鄰居用真的第二個程序(`:1955` `two_processes_share_last_slot`、`:2031` `process_death`、`:2077` `two_parent_race`)或真的執行緒(`:2011` `lock_timeout`)。新測試改用 `mock.patch.object(sqlite3, "connect", racing_connect)`,在連線瞬間偷偷插入一筆帳。這是本測試群原本沒有的做法,見 A1。
- 沒有新增依賴或新機制,時鐘讀取沒有被抽成共用輔助函式。

A1
severity: minor
blocking: 否
引句:「mock.patch.object(sqlite3, "connect", racing_connect)」
對照:`scripts/test_autonomous_loop.py:1955`、`:2011`、`:2077`。這三處的帳本並發測試都用真程序或真執行緒搶真鎖,沒有人 mock `sqlite3.connect`。新測試是用替身偽造競態。判成 minor 的理由:結構沒壞,只是同一群測試出現第二種「模擬並發」的寫法。⚠ 若審查員認為鄰居的真並發在 CI 上本來就不穩(也就是這次要修的 flaky),這個選擇有它的理由,對齊度可以降為不列。

A2
severity: minor
blocking: 否
引句:「if not read_clock_after_lock and (not isinstance(now, (int, float)) or not math.isfinite(now) or now < 0):」
對照:`scripts/scenario_probe.py:1002-1004`(新增的第二份 `isfinite`/`< 0` 檢查)。時鐘合法性檢查現在分成兩處,條件寫法也不同:前一處帶 `isinstance`,後一處沒有。兩處丟的錯誤訊息相同,結構沒壞。⚠ 判不準:`time.time()` 恆回 float,少 `isinstance` 實務上無差。

A3
severity: minor
blocking: 否
引句:「[repro:python3.14 scripts/test_autonomous_loop.py TestScenarioProbeAblation.test_attempt_ledger_reads_clock_after_lock]」
對照:`docs/lumos-toolchain-knowledge/Systems/codex-harness.md:31,43`。鄰近的既有 PITFALL 多用 `[test:t_…]` 綁測試。專案 CLAUDE.md〈寫筆記時〉允許 `[test:]`/`[repro:]`/`[防回歸:]` 三選一,所以 `[repro:]` 本身合法。但 patch 內的 `.governance-log.jsonl` 顯示 note-shape 對這個測試名報了「指不到真測試(fake)」(warn 模式,不擋)。同檔 `:47`、`docs/lumos-toolchain-knowledge/Systems/historical-test-quality.md:35`、`docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:44` 也用 `[repro:python3 …]`,所以形狀本身跟專案做法一致,只是這支檔裡是第一次用 `repro:`。⚠ 這條是否算「不對齊」判不準,列為 minor 供收貨者裁。

不對齊共 3 條,其中 major 0 條
