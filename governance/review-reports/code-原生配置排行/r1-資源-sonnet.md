severity: minor

我沒找到 blocker 或 major,只有 3 條 minor。

## 1. 時間預估把第一段的快照與掃描也乘三倍,慢機器上會多擋
severity: minor
blocking: 否 這只會讓第二段多跳過,而且文字輸出有印原因,屬 minor。
引句:「    if budget and elapsed + (2 * elapsed + 120) > float(budget):   # 第二段預估 = 第一段的兩倍加停錄、拉檔、查詢的 120 秒」
file: `scripts/templates/android-stability-collect.sh:579`(後來的檔裡 `native_skip`)加 `main()` 傳入的 `time.time() - t_start`。`elapsed` 是整個量測段,包含 `load_config`、兩次 `java_heap_dump`、兩次 `dumpsys meminfo --unreachable` 和兩次快照查詢。

- 具體情境:`native_skip` 要求 `test_data` 為 true 才會跑到預估這行。所以第二段打開時,第一段一定含兩次快照。
- 第二段不做快照、不做 unreachable 掃描,實際耗時只有暖機、N 輪、停錄和一次查詢。
- 設 e2e 上限 3600,預估條件等於「第一段超過約 1160 秒就不跑」。
- 例子:第一段 1200 秒,其中 700 秒是快照與掃描。第二段實際約 500 秒,預估卻是 1200 + 2520 > 3600,於是回 `failed 時間不夠`。
- 後果是慢機器或大 App 的排行永遠不出,只留一行提醒。

## 2. 預估沒涵蓋查詢逾時,而且結果檔最後才寫,超時時第一段的量測會一起丟掉
severity: minor
blocking: 否 超時要同時滿足預估通過和第二段異常慢,我沒能重現,⚠ 判不準。
引句:「        res["native_retained"] = native_phase(st, scen, res, run_dir, state, time.time() - t_start)」
file: `scripts/templates/android-stability-collect.sh:668`(`main`)。`stability.json` 要到 `native_phase` 回來之後才寫(`main` 末段)。e2e 的 `kill_group` 先送 TERM、寬限 `GRACE`=60 秒,再補 KILL(`scripts/templates/android-e2e-run.sh:115`)。

- 預估只給拉檔和查詢固定 120 秒。查詢實際上限是 `T_LONG` 1800 秒,暖機驅動和 N 輪驅動也各是 1800 秒。
- 情境:第一段花 1000 秒,預估 3120 通過。第二段的 `trace_processor` 在大錄檔上跑超過 2600 秒,e2e 的 3600 秒到了就 TERM。
- 收集腳本走 Terminated 路徑,印「沒寫結果檔」後回 2。第一段已經量好的 `unreachable`、heap、`cycle_trace` 全丟,`lumos` 看到的是整步逾時。
- 這和註解「不連累量測那段」的說法不符,只在預估準時才成立。
- 查詢耗時只有程式註解沒有實測,我沒有 heapprofd 錄檔可以量。

## 3. `device_dirty` 只有中斷路徑讀得到,一般意外後裝置上的錄製與暫存會無聲留著
severity: minor
blocking: 否 裝置端殘留可自行清,而且 `max_record_s` 到了錄製會自己結束。
引句:「            state["device_dirty"] = True   # 收不掉:被中斷時 main 照實寫裝置上可能還留著」
file: `scripts/templates/android-stability-collect.sh:629`。`grep -n device_dirty` 只有 629 行(寫)和 644 行(`cleanup` 內讀)。

- 情境:`native_run` 丟出非 Terminated 的例外,例如 `st["driver"]` 取值失敗。同時 adb 離線,`native_phase` 的 finally 裡 `abort_record` 回 False。
- 於是 `device_dirty` 被設起來,但 `main` 沒進 `cleanup`,繼續寫 `stability.json`。
- 結果檔只有 `第二段出了意外(KeyError)`,沒提 `/data/misc/perfetto-traces/lumos-native-<id>.pftrace` 與設定檔可能還在,heapprofd 也可能還掛在 App 上。
- 同一件事在中斷路徑會被 `cleanup` 照實講,兩條路徑不一致。

## 其他已讀,無 finding

- **錄製收尾:** 登記時機、各條失敗路徑、兩次中斷與裝置離線都走得通。
  - `start_record` 在 `adb push` 之前就把 `state["rec"]` 登記好。
  - `native_phase` 的 finally 一律 `pop` 並 `abort_record`,三種出口都收得到:正常、`Exception`、Terminated 或 KeyboardInterrupt。
  - `stop_listening` 讓第二次中斷被忽略。裝置離線時 `abort_record` 回 False,設 `device_dirty`,`cleanup` 回 `not state.get("device_dirty")`,message 會照實講。
  - 順序有一點變:Terminated 時 `abort_record` 現在在 `cleanup` 的「收尾中」提示之前跑。總時間不變,只是少一段提示。
- **本機檔:** `heap-native.pftrace` 的檔名符合 `prune_old_snapshots` 的 `heap-.*\.pftrace`,7 天後被刪。`record-native.pbtxt` 很小,不清。`cycle.pftrace` 已經是同樣的不清理狀況,不算這次新增。
- **子程序:** 新的 `trace_processor` 和驅動都走既有 `run()`,逾時整組 `kill_group`。`tp_rows` 的暫存 `.sql` 在 finally 裡 `unlink`。
- **查詢範本:**
  - 我用 `python3.14` 的 sqlite3(3.53.4)做合成資料,把這支 SQL 去掉結尾分號實跑。
  - 結果是 3.3 萬個 callsite 0.4 秒,25 萬個 3.2 秒,216 萬個(5 萬 leaf、深度 50、40 萬列配置)35.7 秒、尖峰記憶體約 550MB(含造的資料)。成長接近線性,沒有二次方連接。
  - 這不是 `trace_processor` 本身的數字,它的記憶體與速度我沒量到。
  - 輸出最多 200 列 site 加 1 列 rows 與 stats,hex 欄各 ≤1000 字元。
- **lumos 端:** 印前 20 個,`--json` 帶最多 200 個。func 與 caller 在收集端已截成 500 字元,成本可忽略。`sites_err` 對整個清單是線性檢查。
- **預算變數:** `LUMOS_STABILITY_STEP_BUDGET_S` 在 `main` 先驗過 `float`。e2e 傳 `f"{T_LONG:g}"`,3600 或 1e+06 都解得開。

## pitfalls manifest 逐條判定(15 條)
全部誤報,沒有真隱患。

- **資源類(檔案 handle,2 條):**
  - 行 259 是 `tp_rows` 裡的 `open(...).read().replace(...)`。
  - 行 312 是 `start_record` 裡的 `open(...).read()`。
  - 兩處都是單行讀完即丟,CPython 引用計數會立刻關檔。
- **效能類 sleep(行 577):** 是 `native_run` 裡一次性的 `time.sleep(SETTLE)`,不在迴圈裡。
- **效能類 N+1(SQL 行 17、20、22、51、60、74、77、80、83、87、89、91,共 12 條):**
  - 這 12 條是 CTE 與 join 的集合運算,不是應用層迴圈裡逐次發查詢。
  - 實測成長接近線性(見上面「查詢範本」)。
- 併發類題目這次 manifest 沒有。

## 圖譜固定席
都不影響,逐組說明如下。

- **`lumos-cli-read`(search 預設排除 superseded):** diff 只動 macrobench 的結果列印與設定檢查,沒碰 search 的濾網。
- **`guard-kill`(rc 優先序與 `--json` 純度):** 沒碰 guard kill。`macrobench --json` 的 stdout 仍是一行 JSON,`native_retained` 只多一個鍵,印文字走另一條輸出。
- **`lumos-cli-lifecycle`(re-inject 只覆蓋 sentinel 之間 body):** `_VENDORED_TREE_FILES` 只加兩個範本檔名。diff 同時新增這兩個檔,不會有登記了卻不存在的檔。
- **`pitfalls-code-loop`、`loop-convergence-recording`、`design-loop`、`bound-tests-gate`、`測試假綠形態`:** 牽連檔雖列 `scripts/lumos`,diff 內容全在 macrobench 區塊,沒碰審查迴圈、帳本、處置閘或綁定測試的程式。
- **超出上限只列名的節點:** 沒逐篇打開。

## 本案特定鏡頭:`cleanup(state)` 架構裡的位置
已讀,除上面第 3 條外無 finding。

- `state["rec"]` 槽:`native_run` 在 `del state["rec"]` 之前被中斷,槽還在,finally 的 `pop` 收得到。
- `native_phase` 的 finally 已經 `pop` 掉 `rec`,所以 `cleanup` 之後不會重複 abort。

最嚴重 severity:minor;blocking 共 0 條。
