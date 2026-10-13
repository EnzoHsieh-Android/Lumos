severity: clean

沒有架構對齊的 major 或 blocker。這份 diff 沒有引入第二種做法,也沒有跨層直呼。我只讀了 diff 和既有檔案,沒跑測試或 shell。

比對三處,都對得上既有寫法:

1. **借 `scripts/lumos` 單源函式(python)**
   - 既有寫法在 `scripts/scenario_probe.py` 的 `_codex_home_dir`:用 `SourceFileLoader` 載 `scripts/lumos`,呼叫它的 `_codex_home()`,載不進就退回預設。
   - diff 把載入段抽成 `_load_lumos()`,並用 `_LUMOS_MOD` 快取一次。`_codex_home_dir` 和新的 `_wilson()` 都走它。載不進時的退路形狀不變。
   - Wilson 區間沿用 `scripts/lumos` 的 `_wilson_interval`(`scripts/lumos:11679`,逃逸帳統計已在用)。沒有另寫一份,也沒有在別處重複載入程式。
   - 載入程式變成單點,比修前更對齊既有慣例。

2. **`MSG:` 前綴協定(shell)**
   - 既有寫法在 `governance/autonomous-loop.sh` 的 `run_replay`:`sed -n 's/^MSG://p'` 抽前綴,非空才呼叫 `line_notify.send(line_notify.build_report(...))`。訊息由 python 端組成單行,對應 `governance/autonomous_loop/replay_weekly.py:203` 的 `print("MSG:" + m)`。
   - diff 的 `weekly_alert_message` 在 python 端組整句,主程式印 `MSG:`,`run_probe` 只抽前綴轉交。LINE 發送那段與其他週期段同形。
   - 沒有判定行才退回 `p≠n` 的舊訊息。這是這段自己的相容退路,不算第二種做法。
   - 有一處差異我判為風格:`run_replay` 用 `head -1`,`run_probe` 用 `tail -1`。探針 log 是 stdout 加 stderr 混在一起,取最後一行合理。我想不到會壞的具體場景,所以不列。

3. **測試**
   - 純函式測試 `t_weekly_alert_*` 走 `_load_probe_module("sp_waN")` 加 `check(...)`,與既有 `t_probe_*` 一樣。`_wk` 輔助函式沿用既有 `_probe_res` 的造列做法。
   - `t_autoloop_probe_alert_follows_verdict` 用 regex 把 `run_probe` 從腳本抽出來,在沙盒用假 `scenario_probe.py` 和假 `line_notify` 跑。這與任務說明指定的做法一致,沒有真的呼叫 `claude` 或 LINE。
   - 不同於 `TestReplayWeekly` 放在 `scripts/test_autonomous_loop.py`,這支測試放在 `scripts/test_lumos.py`。`test_lumos.py:45120` 的 run_exam/run_probe/run_nags/run_replay 清單測試也在這裡,探針相關測試本來就集中在這裡,位置合理。

三問:

1. 原問題的修復效果:我只看了結構對齊,沒有行為證據。行為面請交給正確性席。
2. 修補處的相鄰呼叫路徑:`_codex_home_dir` 改走 `_load_lumos()` 後,載入失敗仍印同一行 stderr 訊息並退回預設。`_wilson()` 載入失敗回 `None`,`weekly_alert` 有對應退路。形狀與既有一致。
3. 新案例修前修後:沒有新的對不齊案例。歸因為「未判定」,且沒有 finding 需要歸因。

總結:最高等級 clean
