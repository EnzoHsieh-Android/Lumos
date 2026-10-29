severity: minor

我沒找到會讓行為出錯的洞,只有一條 minor:新測試裡有一個解包後沒用到的變數。我跑了 `t_android_native` 相關測試(`python3.14 scripts/test_lumos.py -k t_android_native`),184 項全過、0 失敗。我用 `TMPDIR` 把暫存導到自己的座位目錄,跑完已用字面路徑刪掉。

## Findings

### 1. 新測試解包出來的 `d` 沒用到,新增的 ruff 告警
severity: minor
blocking: 否 只是新增一條 ruff 告警,不改變任何執行行為。
引句:「r, d, fake, _ = _ms_native_collect(td, env={"LUMOS_STABILITY_STEP_BUDGET_S": v})」
file: `scripts/test_lumos.py:18990`
歸因:有證據的修復回歸。這個測試 `t_android_native_budget_values` 是修補輪(G3)新寫的,修前版本沒有這個函式。兩版查證:修後版本讀 `scripts/test_lumos.py:18985-18993`,`d` 在函式內確實沒再用到,manifest 也點名這一行。我沒另外去 checkout 修前版本比對。
失敗場景:`d` 解包後沒用,ruff 報 RUF059。全域鉤子 `prepush-lint.py` 在 push 前跑 ruff,如果專案把新增告警算進閘,推送會被擋下。我在 repo 實測 `ruff check --select RUF059` 時,檔案裡 1426 行等既有位置也有同類告警,所以閘是否真的擋這一條判不準 ⚠。修法是把 `d` 改成 `_`。

## 三問

① 原問題的修復效果。
- G1(印出格式):`x["retained"] * 10 // 1048576` 全用整數算,不會溢位。三段文字各自 `_events_clean` 再接數字,長名字不會把大小截掉。對應的 `t_android_native_lumos_print` 與 `t_android_native_lumos_shape` 在修後版本通過。
- G2(SQL 偽框架):`caller` 的 ERROR 偽框架已改記 `?`,排序 `caller = '?'` 讓有名字的先排。我只讀 SQL 判斷這兩處沒問題,沒有真的跑 trace_processor。
- G3(時間上限):`b = math.nan` 的 NaN 會被 `math.isfinite` 擋下,"nan"、"inf"、"0"、"-5" 都回 2。`left()` 讓剩餘時間不夠時驅動被砍。這部分的測試通過。
- G4 到 G7:對應測試都在 184 項裡通過。

② 修補處的正常、錯誤與相鄰呼叫路徑。
- `fresh_launch` 的順序跟原本一樣:停 App、讀結束紀錄、啟動、等、讀 pid。第一段(`measure`)與第二段(`native_run`)用的是同一支函式,行為一致。
- `tp_rows` 取代了舊的三處切列。`cycle_numbers` 舊寫法比對 `startswith('"cycle"')`,新寫法比對 `cells[0] == "cycle"`,兩者等價。`heap_counts` 的 `rows[1:]` 跟舊的 `splitlines()[1:]` 一致。
- 例外路徑:`native_phase` 用 `except Exception`,不攔 `Terminated` 與 `KeyboardInterrupt`;`state.pop("rec")` 之後呼叫 `abort_record`。`rec[2] is None` 的情況(start_record 沒開成)會直接回 True。
- 呼叫端核對:e2e 範本傳 `LUMOS_STABILITY_STEP_BUDGET_S` 等於 `T_LONG`,跟該步的逾時一致。這個變數若是 inf 或 0 會讓整個收集 die,但正常設定不會碰到。
- 預算估計 `3e+120 ≤ b` 與截止時間 `b-180` 在邊緣上略不一致,後果只是那段寫成 failed,不會壞資料,不列。

③ 新發現的同一案例在修前與修後各是什麼結果。
- 唯一的新發現(finding 1)只在修後版本存在,修前沒有該函式,所以無修前結果可比。
- 其他各組(G1 到 G7)的 repair 與 preserve 案例,我只拿修後版本跑過。修前版本沒有逐一重跑,這些項目的修前結果標「未判定」,原因是缺修前證據。
- G8(`fresh_launch` 重構)沒有獨立測試對應,preserve 靠整套 `t_android_memstab` 系列。這一輪我沒跑那一批。

## pitfalls manifest(16 條)

- `scripts/test_lumos.py:18990` RUF059:真隱患,對應上面 finding 1。
- `android-stability-collect.sh:261` 與 `:314` 的 `open(`(`tp_rows` 與 `start_record`):誤報。兩處都是 `open(...).read()` 一次性讀完,CPython 引用計數會立刻關檔。這種寫法在這支檔裡本來就有,不是新引入的風險。
- `android-stability-collect.sh:487` 的 `time.sleep`(`fresh_launch` 的 `SETTLE`):誤報。它只睡一次、不在迴圈裡,不會累積延遲。
- `android-stability-native.sql` 的 18、21、23、52、61、75、78、81、84、88、90、92 行(各個 SELECT):全部誤報。這是單次的遞迴 CTE 查詢,不是迴圈裡反覆查詢,沒有 N+1。

## IMPACT 固定席

這次沒附固定席節點(鏡頭計算超時),沒有可逐條回答的筆記。我沒有自己補算。

未驗範圍:沒有真的跑 trace_processor 與真機的 heapprofd,SQL 邏輯只靠讀;沒有 diff 修前與修後的 SQL 實際輸出。

總結:最嚴重為 minor,blocking 0 條。
