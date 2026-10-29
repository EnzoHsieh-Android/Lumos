severity: major

LUMOS-SEAT 架構對齊審查(第 2 輪)。python-idioms 沒讀到,所以沒套用它的慣例,只比專案內的鄰居。表態記錄沒附,所以沒有 status=tension 的題要查。

## 問 1 分層與依賴方向:對齊
- **收集腳本只收集、不判過不過。** 新的 `native_run`、`native_phase` 只寫 `stability.json` 的 `native_retained` 段。判定與印出都在 lumos。這跟 `measure()` 一樣,鄰居是 `scripts/templates/android-stability-collect.sh:430` 附近的 `measure()`。
- **lumos 沒碰裝置。** 新增的 `_macrobench_native_retained` 與 `_macrobench_native_print` 只讀結果檔,接在 `_macrobench_print_thresholds`(`scripts/lumos:40305`)旁邊。
- **設定只驗一次,沒有重驗。** `native_retained` 的形狀驗證放在 `_macrobench_stab_optional_err`(`scripts/lumos:39549` 起)與 `_macrobench_stab_top_err`。收集腳本靠既有的 `--check-config`(`load_config`)取得結果,沒有自己重驗。
- **e2e 範本只多傳一個環境變數。** `scripts/templates/android-e2e-run.sh:516` 沒有新的跨層呼叫。
- **修補補強了一致性。** 修補把 `test_data` 改成沿用 `preflight` 讀到的那一個,不另讀設定。
- **兩段共用同一套流程。** `fresh_launch`、`tp_rows`、`start_record` 與 `stop_record` 的參數化,都是把既有流程抽出共用,沒有複製一套。
- **唯一的跨層問題:** 見 finding 1。e2e 與收集腳本之間多了一條預算傳遞,量測那段原本沒有。

## 問 2 命名與錯誤處理:大體對齊,有兩處小不一致
- **對齊的部分:**
  - 結果格式沿用 `src()`(`scripts/templates/android-stability-collect.sh:386` 一帶)的 status/reason,`native_phase` 用 `{"enabled": …, **src({}, why, status)}`。
  - 預算值不合法時用 `die()` 回 2,跟 `preflight` 的 `die` 一樣。
  - 缺範本也在 `preflight` 裡 `die`,不白跑暖機。
  - lumos 印出走 `_events_clean`、標明只提醒不擋,跟 `_macrobench_print_thresholds` 一致。
  - 修補拿掉 `MACROBENCH_NATIVE_BAD` 這個專屬常數,改回寫死字串,是往鄰居靠。
- **不對齊:** finding 2(逾時判斷)、finding 3(參數與函式同名)、finding 4(讀結果檔段落的方式)。

## 問 3 第二種做法
- **另一套逾時或截止時間的算法:有,見 finding 1。**
- **解析 trace_processor 輸出:** 沒有第二套。`heap_counts` 與 `cycle_numbers` 已改成共用 `tp_rows`。原生排行的文字欄先 hex 再解回,是 SQL 檔頭註明的刻意做法,切法仍是同一支。
- **清理裝置暫存:** 沒有第二套。仍走 `abort_record` 與 `stop_record` 的 `finally`。修補拿掉 `device_dirty`,也沒另開路。
- **驗外來 JSON 數字:** 沒有第二套。`retained` 用 `_secev_int`,這支函式在 `scripts/lumos` 裡有 17 處在用。

## Findings

**1. 為原生那段新增了一套「上層預算」截止時間算法,環境變數還在兩處各讀一次**
severity: major
blocking: 是
引句:「    deadline = None if b is None else t_start + b - NATIVE_MARGIN」
file: `scripts/templates/android-stability-collect.sh:669`(對照既有寫法 `scripts/templates/android-stability-collect.sh:348`,只有 `STOP_WAIT` 這種「現在加固定秒數」的截止時間;各呼叫的上限是固定的 `T_LONG`,取自 `LUMOS_STABILITY_LONG_TIMEOUT`)。
- 新增的有三塊:
  - `main` 解析並驗證 `LUMOS_STABILITY_STEP_BUDGET_S`。
  - `left()` 用 `min(T_LONG, deadline - time.time())` 算每次呼叫的上限。
  - `native_skip` 另外用 `elapsed + (2 * elapsed + 120) > float(budget)` 預估,第 582 行把同一個環境變數再讀並轉 float 一次。
- `deadline` 與預估是兩套各自的計算,常數(180、120、2 倍)也各寫各的,沒有統一來源。
- e2e 範本(`scripts/templates/android-e2e-run.sh:516`)還要傳 `T_LONG` 過去,等於兩支腳本的逾時從此互相綁住。
- ⚠ 交編排者:這是否算「第二種做法」,取決於你們認不認「兩支腳本共用一個預算」是新的合法機制。依派工詞的錨,我判 major。
- 代價:往後有人改量測段或 e2e 的逾時,要同時記得調這三處常數。

**2. 查詢逾時靠比對 `run()` 回的錯誤訊息開頭,鄰居的查詢不這樣判**
severity: minor
blocking: 否
引句:「    if rc is None and err.startswith("逾時"):」
file: `scripts/templates/android-stability-collect.sh:306`(`cycle_numbers` 與 `heap_counts` 的 `if rc != 0` 一律走通用的「trace_processor 算不了…」)。
- 代價:`run()` 的訊息文字一改,這個分支就悄悄失效。逾時也不再有統一的處理入口。

**3. `preflight` 的參數名 `native_on` 跟同檔的函式 `native_on` 同名**
severity: minor
blocking: 否
引句:「def preflight(st, native_on=False):」
file: `scripts/templates/android-stability-collect.sh:564`(函式 `native_on(st, scen)`;鄰居的參數如 `test_data`、`mapping` 都沒跟函式撞名)。
- 代價:`preflight` 內若之後要呼叫 `native_on()`,會被參數遮蔽,是會誤導人的命名撞名。

**4. lumos 另寫一套讀結果檔來源段的方式,沒走 `_macrobench_stab_src`,reason 的說法也不同**
severity: minor
blocking: 否
引句:「    elif sec.get("status") not in ("ok", "failed", "unsupported"):」
file: `scripts/lumos:40020`(`_macrobench_stab_src` 統一回 `f"{name} 沒收到({s.get('status')}):…"`)。
- 新段自己判 status 與 reason,印成「原生配置排行沒跑成:…」,連 `unsupported` 也歸在同一句。
- 它不進判定,所以結構上說得通,只是跟鄰居的用詞與入口不同。
- 代價:往後 reason 的格式或欄位要改時,得改兩處。

不對齊共 4 條,其中 major 1 條
