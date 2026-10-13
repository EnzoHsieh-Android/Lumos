severity: clean

沒有 finding。這份 diff 沒有引入第二種做法,也沒有跨層直呼。逐項對照如下。

## 對照結果

**1. 借 scripts/lumos 單源函式(python)**
- 既有寫法:原 `_codex_home_dir` 用 importlib 的 `spec_from_file_location` 加 `SourceFileLoader` 載入 `scripts/lumos`。載入失敗時退回同語意的預設值,並往 stderr 印一行提示。
- diff 的寫法:把載入抽成 `_load_lumos()`,`_codex_home_dir` 和新的 `_wilson()` 都改用它。`_wilson()` 載不進時回 None,`weekly_alert` 再退回「有題沒過就通知」。
- 結論:同一種載入方式,只是從一處搬成共用。Wilson 是借 `scripts/lumos` 的 `_wilson_interval`,沒有另寫第二套;`scripts/lumos` 之外也找不到別的 Wilson 實作。對齊。
- file: `scripts/lumos:11679`(`_wilson_interval` 單源)

**2. shell 的 MSG: 前綴協定**
- 既有寫法:`run_replay` 由 python 組好單行訊息,shell 用 `sed -n 's/^MSG://p'` 抽出,再送 `line_notify.build_report`(`governance/autonomous-loop.sh:450-456`)。檔內註解稱它是「刻意的新慣例,後續新週期任務照此」。
- diff 的寫法:`weekly_alert_message` 在 python 端組句。shell 用同一條 sed 抽前綴,同一個 LINE 呼叫(`build_report('scenario-probe', ...)`)。
- 結論:同一種慣例。差在三處,都不算第二種做法:
  - 取最後一行用 `tail -1`,`run_replay` 用 `head -1`。探針 log 只有一行 MSG,實際沒差。
  - 來源是合併了 stderr 的 log 檔,不是 stdout 變數。這是因為 `run_probe` 本來就把輸出導進 log 再 grep。
  - 多了一個「週評通知:」判定行來決定要不要認 MSG 行。這是為了在探針沒印判定行(舊版或中途壞掉)時能退回 p≠n,有理由,並有測試釘住。
- 舊的 p≠n 退路訊息仍在 shell 內組字,等於同一函式裡有兩處組字。這是向後相容的退路,不是新機制。

**3. 純函式放在 `scenario_probe.py`**
- 既有寫法:`run_replay` 的邏輯在 `governance/autonomous_loop/replay_weekly.py`,探針的判分與摘要原本就在 `scripts/scenario_probe.py`(`summarize_results`、`history_record`)。
- diff 的寫法:`weekly_alert` 等函式放在 `scenario_probe.py`,緊貼 `summarize_results` 和 `history_record`。
- 結論:跟探針既有的分層一致,沒有把判斷邏輯塞進 shell,對齊。

**4. 歷史檔讀寫**
- diff 沿用既有的 `_open_history` 寫入,另用 `Path.read_text` 加逐行 `json.loads` 讀取。
- `scenario_probe.py` 內沒有別的讀歷史的做法,所以沒有第二種讀法。

**5. 測試**
- 新增的 `_wk` 輔助函式、`_load_probe_module("sp_wa*")`、`_probe_res`、`check(...)` 加尾行 `print("  ✓ t_...")`,都是既有 `t_probe_*` 的格式。
- shell 測試 `t_autoloop_probe_alert_follows_verdict` 沿用既有手法:用正則把 `run_probe` 整段抽出,在沙盒用假探針腳本和假的 `line_notify` 跑,不碰真的 claude 和 LINE。
- 命名與歸屬(`t_weekly_alert_*`、`t_probe_history_records_ids`、`t_autoloop_*`)都落在既有分類內。

## 三問(沒有 finding,就我對照到的範圍回答)
- **① 原問題的修復效果:** 測試裡有對應的行為案例。判定為否時不印 MSG 行,且 MSG 前綴剝乾淨。沒有判定行時雜散的 MSG 行不送。總結行的 grep 錨在行首後,「log 的情境探針結果」抓到的是總結行,不是 MSG 行。這些是從 diff 讀到的測試斷言,我沒有實際執行。
- **② 相鄰呼叫路徑:** 舊的 p≠n 退路、`_codex_home_dir` 的載入失敗退路,以及「非週抽種子不印」都仍在。從 diff 看,這些路徑的程式結構沒有被改壞。
- **③ 新案例的修前修後差異:** 本席只判寫法對不對齊,沒有發現新案例,不適用。

總結:最高等級 clean
