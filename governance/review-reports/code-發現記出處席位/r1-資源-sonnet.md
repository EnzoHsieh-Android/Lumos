severity: clean

資源鏡頭沒有可成立的 finding。我逐 hunk 讀完整份 diff,並在 `/Users/enzo/harness/lumos-finding-seat` 真跑量時。

量測結果:
- 對真帳(`docs/.canary-log.jsonl` 6601 行)跑 `python3.14 scripts/lumos gov --stats`,約 3.1 秒;加 `--since 9999` 也是約 3.1 秒。逐席段在真帳裡沒資料(整段不印),所以這是「沒帶欄位」的狀況,不是新段落大量輸出的狀況。
- `python3.14 scripts/test_lumos.py -k finding_seat` 共 43 項全過。最慢的 `t_canary_record_finding_seat` 29.1 秒(上限 180 秒,餘裕 6 倍);`t_gov_stats_finding_seat` 2.7 秒。
- 我只建了 `/tmp/fs_out.txt` 這一個暫存檔,已用字面路徑刪掉。

三問逐條判定:

1. **子程序與執行緒**:這份 diff 沒有新增任何子程序、執行緒、`subprocess` 或訊號處理。新碼只有 `_gate_event_or_warn(...)`,是既有的追加寫入。Ctrl-C 或例外時沒有殘留物。
2. **時間預算**:沒有新的固定時間預算,只有 56 天的資料窗口。
   - 寫側的 `_finding_seat_required_block` 對同迴圈帳每列各算一次 `_loop_ts_key`,迴圈帳是一個迴圈的幾十列,不是整本帳。
   - 讀側的 `_seat_noise_window_start` 算一次,`_seat_noise_carriers` 掃已載入的 rows 一遍。
   - 慢機器不會把正常操作擋下。
3. **記憶體與二次方**:
   - `_gov_event_types_ok` 每列多一次 `_finding_sources_typed`,是 O(該欄大小)。
   - `_seat_noise_counts` 是載體數乘每條發現,線性。
   - `_SEAT_ROUND_MARK_RE` 的前瞻用 `[\w.]*$`,遇到 `-` 就停,病態席名(如 `1-a1-a1-a…`)也只掃一小段,不會變二次方。
   - 全程沒有把整本帳另外複製或再讀一次。`_finding_seat_write_block` 吃的是 `cmd_canary` 已讀好的 `_lrows`,讀帳仍是一次。

固定席(`LUMOS-LENS` 說鏡頭計算超時,沒附節點)。我只能依 diff 裡寫明的 `lands_in` 判斷,所以這兩條是推論,不是照附的節點逐條對:
- `Systems/loop-convergence-recording`(載體最後記、一輪一筆載體、寫側讀帳一次):不影響。新增檢查放在既有「讀帳一次」之後,不新增讀帳;擋下時不寫帳,沒動「載體最後記」的判定。處置閘的 `finding_sources` 路徑沒碰,只共用 `_finding_sources_typed`。
- `Systems/canary-audit`:不影響。diff 新增 d6,說明 d4 否決的跨期統計不涵蓋逐席沒用率;沒有改 d1 到 d5。

severity: clean
