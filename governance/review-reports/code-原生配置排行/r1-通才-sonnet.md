severity: clean

我讀完整份 diff,另外對照了 repo 真碼:`android-stability-collect.sh` 的 `run`、`measure`、`driver`、`read_exits`、`pidof`、`stop_record`,`scripts/lumos` 的 `_macrobench_mode`、`_macrobench_stab_load`、`_macrobench_stab_cfg_err`、`_e2e_scenarios_err`,e2e 範本的 `step`,以及 `test_lumos.py` 裡 vendored 清單的測試。沒有找到講得出具體失敗情境的缺陷,所以沒有 finding。

## 八個角度的結論

1. **逐行**
   - `native_skip` 的順序、`native_run` 的暖機與開錄失敗分支、`del state["rec"]` 的時機、`native_query` 的檢查順序,都對得上 `run`、`stop_record`、`start_record` 的實際回傳形狀。
   - `tp_rows` 在逾時時回 `(None, [], "逾時…")`,`native_query` 的 `rc is None and err.startswith("逾時")` 對得上,而且就算漏接也會落到後面的 `rc != 0`。
   - `tp_rows` 對空行切出 `['']`,各處的 `c[0]` 和 `len(c)` 判斷都不會 IndexError。
2. **被刪掉的行為**
   - `heap_counts` 原本的 `splitlines()[1:]` 換成 `rows[1:]`,等價。
   - `cycle_numbers` 原本的 `startswith('"cycle"')` 換成 `cells[0] == "cycle"`。`android-stability-cycle.sql` 的表頭第一欄是 `key` 不是 `cycle`,所以表頭不會被誤收。
   - `start_record` 和 `stop_record` 寫死的檔名,預設值都保留了原值。
   - `load_config` 現在回 `(設定, 情境名)`,整個 repo 只有 `main` 一個呼叫者。
   - `cleanup` 的回傳多看 `device_dirty`,並沒有拿掉原本「有 rec 就回 `abort_record`」的行為。
3. **跨檔**
   - `_macrobench_mode` 新增的 `native_retained` 鍵只被兩個列印路徑讀。`stab_res` 合併進 `judged` 的迴圈走的是另一個字典,不受影響。
   - e2e judge 讀的是 `stability_unjudged` 和 `low_iterations`,和新鍵無關。
   - `@default` 不會跟情境名撞,因為 `_e2e_scenarios_err` 的情境名正規式 `[A-Za-z0-9_-]+` 不收 `@`。
   - `test_lumos.py:23305` 的 `t_android_memstab_vendored` 已經把兩個新範本納入。
4. **重用**:新碼用了既有的 `_secev_int`(排除 bool)、`_out_clean`、`_events_clean`、`abort_record`、`exit_diff`。沒有重做既有函式。
5. **簡化**:沒有死碼。`native_query` 裡 `rc is None and 逾時` 那一行和後面的 `rc != 0` 部分重複,但只是多一句更精確的訊息,不是缺陷。
6. **效率**:我用 sqlite3 造了合成資料跑 `android-stability-native.sql`。2 萬個葉節點、深度約 66,約 14 秒完成,在 `T_LONG` 內。查詢輸出的三種列(`site`、`rows`、`stat`)切法正確。
7. **修的深度**:`start_record` 和 `stop_record` 加的是預設參數,沒有疊特例。三支查詢的切法統一收進 `tp_rows`,是往統一規則走。
8. **慣例**:全域和 repo 的 CLAUDE.md 我都對照過,沒有能逐字引出、又能指到違反那一行的規則。

## manifest 15 條逐條判定

- **collect.sh:259(`open(` 沒關)**:誤報。那是 `load_mapping` 既有的逐行讀檔寫法,不是這次 diff 新增,函式結束後會被回收。
- **collect.sh:312(`open(` 沒關)**:誤報。那是 `start_record` 讀範本和寫設定檔的既有寫法,每次只開一次,不會累積。
- **collect.sh:577(`time.sleep`)**:誤報。那一行是 `native_run` 裡單次的 `time.sleep(SETTLE)`,不在迴圈裡,不會累積延遲。
- **native.sql 的 12 條 N+1(行 17、20、22、51、60、74、77、80、83、87、89、91)**:全部誤報。那是單一檔案的一個 CTE 查詢,內部的 `select` 是子查詢和 union,不是被迴圈呼叫。我跑過,一次執行就出完整結果。
- 沒有判成真隱患的條目。

## 圖譜鏡頭(固定席)

這份 diff 只動 `scripts/lumos` 的 macrobench 區塊、e2e 範本、收集腳本和新範本,下列節點宣稱的行為都沒被碰到。

- **lumos-cli-read(search 預設排除 superseded)**:不影響。diff 沒碰 `search` 的路徑。
- **guard-kill(rc 優先序、`--json` 純度)**:不影響。diff 沒碰 `guard kill`。
- **design-loop(處置閘第五步)**:不影響。diff 沒碰處置閘或 `loop` 子命令。
- **測試假綠形態(還原翻紅釘)**:不影響。這個節點約束的是測試寫法,diff 沒有改測試。
- **lumos-cli-lifecycle(re-inject 保留使用者內容)**:不影響。diff 沒碰 re-inject。
- **bound-tests-gate(`code-loop check` 逐支真跑合約綁的測試)**:不影響。diff 沒碰這道閘。
- **pitfalls-code-loop、loop-convergence-recording**:不影響。diff 沒碰 pitfalls 或帳本邏輯。
- **只列名的節點**:照名稱判斷,都和這次的 macrobench 與收集腳本改動無關。

最嚴重 severity: clean,blocking 共 0 條。
