severity: clean

沒有發現需要擋的問題。我跑了 `python3.14 scripts/test_lumos.py -k macrobench`,結果是 197 passed、0 failed。

## 逐項查證(都沒有 finding)

1. **`_macrobench_read_one` 回傳值改成五個,呼叫點都跟上了。**
   - grep `scripts/` 與 `skills/`,正式程式裡只有一個呼叫點:`_macrobench_read_file` 解包成 `key, metrics, sampled, iters, cv`。
   - `scripts/test_lumos.py` 沒有直接呼叫 `_macrobench_read_one` 或 `_macrobench_read_file`。
   - file: `scripts/lumos:39554`

2. **變異係數的邊界,我用實際輸入跑過。**
   - `[1e308, 1e308]`:溢位被 `OverflowError` 接住,回 `None`。
   - 平均為 0:回 `None`。
   - 超大整數 `10**400` 或含 `True` 的 runs:`_macrobench_runs_count` 回 `None`,不會走到 `float()`。
   - 次正規數(subnormal)`[1e-310, 2e-310]`:回有限值 0.333。
   - 修補只擋「寫端產出讀端不收的值」,這一點我確認是對的。

3. **整數檢查是對的。**
   - `_secev_int` 用 `type(v) is int`,不收 bool。
   - 實測 `iterations=10**30` 會通過形狀檢查;只要比較式 `v >= least` 對 Python 大整數不出錯就沒事。
   - 實測 `cv=[]` 被拒;`iterations` 或 `cv` 為 `None` 時視同沒寫。

4. **不同指標輪數不同。**
   - 實測一個指標 3 輪、一個 4 輪,取最小值 3。
   - 任何一個沒忽略的指標讀不出輪數,整個情境不記輪數,所以不會誤放寬判定。

5. **新舊互讀。**
   - 新程式讀舊基準:缺 `iterations` 時 `_macrobench_iters_ok(None, 20)` 回 False,維持兩道都要過的舊判法。
   - 舊版程式讀新基準:舊的 `_macrobench_entry_ok` 不管多出來的欄位,所以能讀、判定照舊。
   - `--update-baseline` 用 `merged.update(current)` 整個情境覆蓋,不會留下半新半舊的欄位。

6. **測試抓得到改壞。**
   - 我讀了 `t_macrobench_mag_only_at_20`。把 `all` 改成 `any`,②③會紅;拿掉 `mag_only`,①會紅;連容差一起拿掉,④會紅。
   - `t_macrobench_baseline_records_iterations` 的 ⑤d、⑤f、⑤g、⑥ 分別釘住「平均為 0」「無限大」「溢位」「寫進去的值自己讀得回來」。

## 圖譜鏡頭(固定席節點)

- `guard-kill` 的 ★INVARIANT★ 管 guard kill 的 rc 優先序與 `--json` 輸出。
- `lumos-cli-read` 的 ★INVARIANT★ 管 search 的 superseded 濾網。
- `design-loop` 的 ★INVARIANT★ 管處置閘第五步。
- `lumos-cli-lifecycle` 的 ★INVARIANT★ 管 re-inject 與 sentinel。
- `測試假綠形態` 的 ★INVARIANT★ 管修 bug 的還原翻紅釘。
- 以上都在不同的函式與子命令,diff 只動 `_macrobench_*` 一帶與 macrobench 的測試,不影響這些節點宣稱的行為。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger` 的 ★RISK★ 沒有宣稱和 macrobench 相關的行為,不受影響。
- 新的 macrobench 函式沒有碰 `guard kill`,`--json` 鍵集合的擴充(`low_iterations`)也只在 macrobench 自己的輸出裡。

## 一個我決定不列的小疑慮

`--update-baseline` 遇到讀不了的舊基準時,`_macrobench_update` 會印「基準沒更新」並回 0,之後 `scripts/lumos:40215` 仍照印「輪數不足」提醒。沒有資料損壞,也不影響判定,所以不列為 finding。

總結:全篇最高為 clean
