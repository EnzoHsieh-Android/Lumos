severity: clean

資源鏡頭沒找到資源問題。新增的兩段測試在兩次 guard kill 之後,暫存目錄、子程序、被換掉的函式都收乾淨,逾時餘裕也夠。

## 已驗主張

**1. 暫存目錄收得乾淨。**
引句:「_ck_cleanup(root, fake, tmp)」
- `run()` 的 `tmp`、`root`、`fake` 都在 `finally` 裡經 `_ck_cleanup` 收掉。`finally` 裡同時用 `m._kill_run = orig` 還原函式。
- 兩次 `run()` 各自建、各自刪,第二次不依賴第一次的殘留。
- 實測:修後版跑了 1+2+4 次 `t_choice_kill_merge_cap_wiring`,每次跑完 `$TMPDIR` 下 `gctl-ckm-*` 都是 0 個。

**2. 被換掉的函式與 `_KillMerge` 屬性不外洩。**
引句:「mg.remaining = lambda: 60.0 if singles[0] < 3 else -5.0」
- `mg.remaining` 只掛在這個測試自己的 `_KillMerge` 實例上,不碰類別,隨實例丟棄。
- `m._kill_run` 在 `run()` 的 `finally` 還原。
- `budget_edge` 新增的兩段也走原本的 `finally: m._kill_run = orig`。這兩段沿用同一個 `finally`,所以中途拋例外也會還原。

**3. 保底 1 秒的逾時不會留下假 Gradle 殘留。**
引句:「check("r4 邊界 #2 量完單支基準後剩下時限 -5 秒 → 合併基準收到的上限是保底 1 秒", bool(seen) and seen[0] == 1.0, str(seen))」
- 假 Gradle 是 Python 腳本,啟動時間可能撞到 1 秒上限。
- 撞到的話走 `_kill_run` 的 `TimeoutExpired` 分支:`_kill_proc_group(proc)` 加 `proc.wait()`,在 `_KILL_RUN_LIVE` 的 `finally` 裡登記移除。
- 程序用 `start_new_session` 開,整個群組都收得到。
- 斷言讀的是 `seen[0]`,逾時發生在 spy 記錄之後,斷言本身不受影響。
- 實測:四份並行跑完後再查程序表,沒有我留下的 gradlew。
- 期間看到兩個 gradlew 程序(`gctl-run-5bhdo0as`、`gctl-run-qt0je7nz`)。它們分別是我跑第 2、3 輪時已看不到(另一個會談的)、跑完 4 份並行後才出現的新程序(存活 2 秒),不是我的測試留下的,我沒有碰。

**4. 耗時與時限餘裕(兩次以上重跑)。**

| 測試 | 修後(f14bd588) | 修前(100d3851) |
|---|---|---|
| `t_choice_kill_merge_cap_wiring` 單跑 | 14.3s、9.4s、9.3s | 9.4s(只有 3 條斷言,新增的 2 條不存在) |
| 同上,四份並行 | 10.3s,餘裕 17x 至 18x,四份 5 passed | 未跑 |
| `t_choice_kill_merge_budget_edge` | 0.1s,6 passed | 未跑 |
| `t_choice_kill_merge_budget_reestimate` | 58.8s,餘裕 3x,3 passed | 未跑 |

- 第一次 14.3s 是冷啟動加機器有別的負載。
- 新增的第二次 guard kill 讓 `cap_wiring` 比修前慢,但上限 180 秒下餘裕 17x 以上,並行負載也沒紅。
- `reestimate` 餘裕只有 3x,但不在這次 patch 內,也沒有因修補變慢,只在此註記。

## 能否比較與歸因
- 修前版只有 3 條斷言,新增的 `--json` 不帶 judged 與保底 1 秒兩條在修前不存在,無法拿同一案例比。
- 兩版 `-k t_choice_kill_merge_cap_wiring` 都綠,所以沒有修補造成的資源回歸。這只證明這個測試沒有資源問題,不代表整份修補無回歸。

## 未驗範圍
- 沒有對正式程式做翻紅釘變異,那是其他席的鏡頭。
- 沒有在更重的負載(多於四份並行)下重跑。
- `--json` 不帶 judged 的程式路徑正確性不在資源鏡頭內。

收工:兩個 worktree 與臨時目錄都已移除。

總結:最高嚴重度 clean
