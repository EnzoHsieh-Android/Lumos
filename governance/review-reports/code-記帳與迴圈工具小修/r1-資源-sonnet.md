severity: minor

沒有找到 blocker 或 major。我在 web-ledger 的 d2da0e8c 上實測:記帳多讀的整本帳在現有規模下很快,到 10 萬列才開始明顯。這一包也沒有新增逾時或 Ctrl-C 時沒收掉的子程序。

實測方法:把真實帳 `docs/.canary-log.jsonl`(4796 列)複製放大到 10 萬列,直接呼叫 `_loop_records_checked`(記帳多讀的就是這支)。

| 帳長 | 單次讀帳時間 | 讀帳時的最大記憶體 |
|---|---|---|
| 4796 列(現況) | 0.07 秒 | 約 17 MB |
| 10 萬列 | 1.34 秒 | 整個行程約 0.9 GB |

**1. 每筆記帳最多讀三次整本帳,沒帶 `--round` 的記帳是這次多出的一次**

severity: minor
blocking: 否

- 範圍:`cmd_canary` 的寫側輪次規則。
- 走法:一筆帶 `--loop` 的記帳(不是結局帳)會走到三處讀帳。
  - 第一處是新增的 `_loop_records_checked(env, loop)`。
  - 第二處是 `--orchestrator` 檢查裡的 `_loop_records(env, loop)`。
  - 第三處是 `--regression-set` 檢查裡的 `_loop_records(env, loop)`。
- 這次的變化:
  - 帶 `--round` 的記帳沒有多讀,原本那次讀帳被搬到前面,後面用 `_lrows` 重用。
  - 沒帶 `--round` 的記帳以前不讀這本帳,現在多讀一次。
- 代價:每次讀帳都是 O(整本帳),而且 `_canary_ledger_scan` 會把所有迴圈的列都解析進記憶體,不只目前這個編號。10 萬列時最壞約 3 × 1.3 秒,現況 4796 列約 0.2 秒。這個量級不會擋住正常操作,所以只列 minor。
- 何時要回頭看:帳超過約 5 萬列、或單筆記帳超過約 2 秒時,再考慮把 `_lrows` 傳給後兩處,或只掃目標編號。
- 引句:「+    _lrows, _lerr = _loop_records_checked(env, loop) if (loop and outcome is None) else ([], None)」

我另外查過這幾處,都沒有資源問題:
- `_round_format_write_block` 和 `_loop_round_format` 只對單一迴圈的列做線性掃描。呼叫 10 萬列帳時,規則本身耗時約 1e-5 秒,沒有二次方工作。
- `_loop_next_hints` 和 `_pitfall_tier_review_lines` 只是固定長度的字串和名冊查表。
- `_disp_type_err` 和 `_disp_value_type_err` 在 `existing` 迴圈裡有 `ex[:_DISP_EXISTING_MAX]` 上限,不會因輸入變大而變慢。
- 擋下時呼叫的 `_gate_event_or_warn(..., hard=True)` 內部會跑 `git rev-parse`,沒有逾時。這是既有行為,而且只在擋下路徑才跑,所以不報。
- 新增的測試用 `shutil.rmtree` 在 `finally` 清理 `_rf_fix` 建的暫存目錄,這部分沒問題。`t_loop_next_code_standard_round_not_panel` 裡的 `subprocess.run(... loop next ...)` 沒設 `timeout`,同檔其他測試多半也沒設。如果被測程式卡住,測試會一起卡住,但看不出這次改動讓卡住更容易發生,所以不算 finding。

我的實驗目錄 `/private/tmp/lumos-seat-work/code-記帳與迴圈工具小修/資源-sonnet` 已刪,刪前確認沒有程序開著。

最嚴重 severity:minor;blocking 共 0 條。
