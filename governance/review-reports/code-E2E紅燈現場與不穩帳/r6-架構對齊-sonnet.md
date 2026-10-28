severity: minor

## 問 1 分層與依賴方向:對齊

- 範本腳本(`scripts/templates/android-e2e-run.sh`)只寫 `steps.json` 的 `evidence` 欄位,沒有直接讀寫 lumos 的帳本。
  - 它補欄位的寫法是 `st.data["steps"][-1]["evidence"] = …; st.save()`,跟同檔 `collector_override` 的寫法一樣。
  - 它拿 lumos 的結果仍然靠 `lumos("android-e2e", "judge", …)` 這個子程序呼叫,沒有 import。
  - 開跑前檢查把模組全域 `EVIDENCE` 在 `preflight` 裡用 `global EVIDENCE` 設定,跟同檔 `global SEL`(約第 558 行)是同一種做法。
- lumos 這側(`scripts/lumos`)沒有重做範本腳本的事:
  - `_e2e_ui_evidence` 只讀 `steps.json` 帶過來的 `dir` 和 `crash` 欄位,並用 `os.path.exists` 篩。
  - 判定結果的新欄位 `fail_evidence`,明確避開了範本腳本寫的 `evidence` 和總表的 `evidence`(`_e2e_judge_ui` 行內註解)。
- 總表欄位沒有反過來影響綁版本的查證紀錄:
  - `_e2e_history_append` 只替總表那份 `case_results` 補 `flaky`。
  - `_e2e_case_results` 的 docstring 明寫「items 不帶第二次才過」。
  - 對照:`scripts/lumos:41348`(`_e2e_history_append`)與 `_e2e_case_results`。
- 呼叫方向順:`judge` 呼叫 `_e2e_history_append`,後者呼叫 `_e2e_flaky_notify`,再呼叫 `_e2e_flaky_counts`,再呼叫 `_e2e_flaky_tally`。
  - `history --flaky` 走 `_e2e_history_rows`,再走 `_e2e_flaky_report`,最後也到 `_e2e_flaky_tally`。
  - 點名和彙總共用同一支 tally。
  - 逐行讀帳全走既有的 `_canary_ledger_rows`(`scripts/lumos:20387`),追加走 `_local_ledger_append`(`:1698`)。

## 問 2 命名與錯誤處理:大致對齊,有一條 minor

- 命名跟同群一致:
  - `_e2e_*` 前綴、`E2E_FLAKY_*` 常數、範本腳本的 `crash_log` / `device_time` / `maestro_has_evidence_flags` 都跟鄰居同風格。
  - 常數放在函式中間,跟 `E2E_GATE_BUDGET_SEC`(`:41531`)的位置習慣一樣。
- 終端訊息出口一致:
  - `_e2e_history_line`、`_e2e_flaky_report`、`_e2e_flaky_notify` 都過 `_out_clean`。
  - `_e2e_print_runs` 內部的 `say()` 收成單一出口,不再直接 `print`。
  - 擋下仍走 `_say_block`。`t_android_e2e_say_single_exit` 只掃以「擋下:」開頭的 `print`,新碼沒碰。
- 錯誤處理:
  - 範本腳本的讀閃退紀錄失敗回 `None`,不丟例外,跟同檔 `adb()` 回 `(rc, out, err)` 的風格一致。
  - 總表讀不了時,`_e2e_history_cmd` 用 `except OSError` 配 `_say_block`,維持原樣。
  - `_e2e_flaky_notify` 讀不到就靜默不印,筆記有寫明,屬於只提醒的設計。
- 修補新引入的寫法見下方 F1。

## 問 3 第二種做法:查過,不成立

- `_e2e_run_key` 沒有重做 `_ci_latest_attempts`(`scripts/lumos:59022`)。
  - 我開兩邊對照過,作者的理由是真的。
  - `_ci_latest_attempts` 要靠 `attempt` 和 `conclusion` 兩欄挑「嘗試次數大的贏、同次取較糟的」,吃整份清單,還在掛鉤裡有逐字複本。總表沒有這兩欄。
  - 兩邊相同的只有「`run_id` 為 `None` 才算沒有、其他轉字串」這一句。全檔搜不到別的執行鍵 helper,所以不單獨判 major。
- 逐行讀:兩處都走 `_canary_ledger_rows`,沒有自己寫 `open` 加 `split`。
- 外來文字清理:走 `_out_clean`,沒有新的清理函式。
- 跨腳本格式比對:`t_android_e2e_crash_log` 用「抽出兩支腳本的 `date '+…'` 那一行比相等」,跟既有 `E2E_SCENARIO_KEYS` 和 `test_data` 兩處的「測試抽出兩邊比相等」同一寫法。
- 測試載入模組:`_load_lumos_inproc()`(`scripts/test_lumos.py:238`,快取單例)和 `_load_lumos()`(`:12918`)在 e2e 測試群裡本來就並存。
  - 前者例如 `t_android_e2e_fingerprint`、`t_android_e2e_vendored`,後者例如 `t_android_e2e_say_single_exit`、`t_android_e2e_coverage_*`。
  - 新測試用前者不算新做法。

### F1 `_e2e_history_rows` 依 `flaky` 參數回傳兩種型別,呼叫端再分一次
severity: minor
blocking: no
引句:「    return runs if flaky else rows」
對照的既有檔位置:file: `scripts/lumos:41484`(新函式),對照 file: `scripts/lumos:20387`(`_canary_ledger_rows`,同一個 `errors` 參數不改變回傳型別)

1. 修補把原本內嵌在 `_e2e_history_cmd` 的迴圈抽成 `_e2e_history_rows`。
   - 它在 `flaky=True` 時回 `OrderedDict`(執行鍵對應該次的行串列),否則回 `deque`(單純的行)。
   - 呼叫端 `_e2e_history_cmd` 又用同一個 `flaky` 分一次(`for rs in got.values()` 對 `for r in got`),等於分支散在兩處。
2. 同檔的鄰居(`_e2e_history_items` 回固定的 `(list, res)`,`_canary_ledger_scan` 回固定三元組,`_canary_ledger_rows` 的 `errors` 不改變型別)都是固定型別。
   - 這裡是新寫法,接手的人要在呼叫端記得 `got` 是哪一種。
3. 結構上沒有第二套邏輯:篩選、讀檔、`OSError` 交給呼叫端這三件事都跟原本內嵌時行為一樣,也沒有跨層。所以只算 minor。

不對齊共 1 條,其中 major 0 條
