severity: clean

我讀了整份 snapshot patch 和修補段 patch,另外用 `git show eeb1721c…` 對照了鄰居碼。以下行號是對 `eeb1721c` 的 `scripts/lumos`、`scripts/test_lumos.py` 和範本腳本的行號。三問都對齊,沒有 finding。

**1. 分層與依賴方向:對齊**
- 範本腳本只做現場收集:`maestro_has_evidence_flags`、`device_time`、`crash_log`,最後寫進 `steps.json` 的 `evidence`。它沒有碰 `history.jsonl`,也沒有碰 lumos 的帳本函式。
- lumos 只讀 `steps.json`,不重做收集:`_e2e_ui_evidence` 在 `scripts/lumos:40818`(patch 內位置),輸出欄位叫 `fail_evidence`,刻意跟總表的 `evidence`(run 目錄)區分開。
- 查證紀錄這邊沒有被總表欄位反過來影響。`_e2e_case_results` 的 docstring 寫明 items 不帶「第二次才過」,總表那份由 `_e2e_history_append` 在寫出前補上。查證紀錄 `feature_runs` 沒動。
- 寫帳走原本的 `_local_ledger_append` 和 `_ledger_tail_needs_newline`(`scripts/lumos:1698`),讀帳走原本的 `_canary_ledger_rows`(`scripts/lumos:20387`)。這幾處都跟鄰居同一條路。
- 範本腳本的新全域變數 `EVIDENCE` 和 `global EVIDENCE` 跟原有的 `SEL` 同寫法(`android-e2e-run.sh:52`、`:558` 的 `global SEL`)。

**2. 命名與錯誤處理:對齊**
- 新函式都用 `_e2e_` 前綴、常數用 `E2E_` 前綴,跟同檔的 `E2E_GATE_BUDGET_SEC` 這批一致。
- 讀不到總表的處理跟原本一致:歷史指令走 `_say_block` 回 rc2,點名只提醒、不改判定。
- `_e2e_print_runs` 內部的 `say()` 有前例,例如 `scripts/lumos:46759` 的 `_ns_test_refs_collected` 內部 `say`。它的出口走 `_out_clean`,符合 `_out_clean` docstring 說的底層共用規則和 `t_android_e2e_say_single_exit` 的守則(e2e 區不直接印「擋下:」)。
- 範本腳本的 `say`、`die`、`adb`、`run` 都沿用原有的。
- `device_time` 的 `date '+%m-%d %H:%M:%S.000'` 跟收集腳本 `android-stability-collect.sh:484` 的格式一樣。

**3. 第二種做法:沒有,作者寫明不共用的理由也成立**
- **`_e2e_run_key` 不共用 `_ci_latest_attempts`(`scripts/lumos:59015`)的理由是真的。** 我對照了兩邊的碼:
  - 相同處:兩邊都只把 `run_id is None` 當沒有 run_id,且都 `str()` 轉字串。
  - 不同處:CI 那支靠 `attempt` 和 `conclusion` 欄位挑「次數大的贏、同次取比較糟的」。總表沒有這兩個欄位,套進去的話所有行都是 att 0、bad 1,實際變成「先出現的贏」。tally 要的是「最後一個判出結果的那次」,語意相反。
  - 另外 CI 那支吃整份清單,還有掛鉤裡的逐字複本。
  - 所以另寫一份「執行鍵」是合理的。
- 歸併的規則只有一套。`_e2e_flaky_tally` 負責 flow 層的同一次執行,`_e2e_history_cmd` 的 `runs` 負責 `--last` 數執行次數,兩邊都呼叫 `_e2e_run_key`,key 的定義只有一處。
- 外來文字清理只有 `_out_clean` 一個出口。`_e2e_history_line`、`_e2e_flaky_notify`、`_e2e_flaky_report` 和 `_e2e_print_runs` 的 `say` 都走它。
- 跨腳本格式比對的測試寫法是既有的。`t_android_e2e_crash_log` 用 regex 抽出兩支腳本的 date 格式比相等,跟 `preflight` 裡「逐字相同(測試抽出兩邊那一行比相等)」那條同一套做法。
- 測試用 `_load_lumos_inproc()` 呼叫內部函式也是既有寫法,全檔有 763 處,例如 `test_lumos.py:28611`、`:28796`。

不對齊共 0 條,其中 major 0 條
