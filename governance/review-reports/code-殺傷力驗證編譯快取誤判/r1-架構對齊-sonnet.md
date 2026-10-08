severity: clean

核對範圍:等待迴圈、旁路欄、只印一次、新測試寫法,對照專案既有寫法,沒有發現「第二種做法」或跨層直呼。

## F1 核對:等待迴圈與 sleep 與既有等待同形(無問題)
severity: clean
blocking: 否
引句:「while int(time.time()) <= max(state["w"], state["r"]) and time.time() < deadline:」
佐證行:file: `scripts/lumos:34343`(ci-wait 迴圈用 deadline 加 time.sleep(min(..., deadline - time.time())) 的同一形狀);`scripts/lumos:34300`
1. 專案其他等待(ci-wait)是「deadline 絕對時間 + time.sleep」輪詢,新的 `_kill_wait_new_second` 同形,沒引入新機制(沒用 threading.Event、signal 等)。`_kill_after_write` 的 `time.sleep(1.0)` 是固定一次一秒重試,不是輪詢,語意不同,不構成第二種做法。
2. 全檔 time.sleep 只有 ci-wait 與這兩處,沒有鎖等待的 sleep 寫法可比對。

## F2 核對:旁路欄 _mtime_unsure 與 _logged、_rid 同一種處理(無問題)
severity: clean
blocking: 否
引句:「if k not in ("_logged", "_rid", "_mtime_unsure")}」
佐證行:file: `scripts/lumos:14073`(既有 _logged、_rid 同一個濾除點);`scripts/lumos:13890`(_rid 同樣以底線前綴旁路欄掛在 results 上)
1. 旁路欄慣例是「底線前綴、掛在結果 dict、--json 輸出前濾掉」,新欄位照辦,且 kill-log 寫入是白名單欄位(不會漏旁路欄),人讀輸出也是點名取欄位,不會印出旁路欄。
2. `weak` 在收尾重算處納入 `_mtime_unsure`,跟既有 ws/flaky/node_dirty 並列,只改 weak 不改 verdict,與既有弱證據處理一致(「killed」帶 weak=True,不進全弱 rc1 判斷)。這是既有慣例,不是新做法。

## F3 核對:只印一次的寫法(無問題)
severity: clean
blocking: 否
引句:「mt_warned = [False]   # 修改時間沒錯開的提醒整次只印一次」
佐證行:file: `scripts/lumos:13891`
1. 全檔搜尋沒有其他「提醒只印一次」的共用輔助(搜 `_warned`、`_once`、`[False]` 只有這一處),故不存在可沿用的既有寫法;函式區域內的一格旗標清單是最小做法,不算第二種做法。

## F4 核對:新測試與既有 t_guard_kill* 寫法一致(無問題)
severity: clean
blocking: 否
引句:「orig = m._kill_after_write」
佐證行:file: `scripts/test_lumos.py:225`(_load_lumos_inproc 既有);`scripts/test_lumos.py:59847`(_kill_log_rows_of 既有);`scripts/test_lumos.py:20339`(_mk_kill_env 既有)
1. 測試用既有的 `_mk_kill_env`、`_kr_note`、`_kr_commit`、`_kill_log_rows_of`、`_load_lumos_inproc`;in-proc 打樁用「存 orig、try/finally 還原」,與同檔 kill-add 測試(`m._kill_recipe_judge = spy2` 再還原)同形。
2. `_kgk_run` 是新的子程序輔助,跟同檔其他 `_xxx_run(...)` 輔助(例如 `_ci_run`、`_testmap_run`)命名與形狀同族,沒有重複既有輔助。

最高等級:clean
