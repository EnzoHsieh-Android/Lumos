severity: major

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/baf3be87…json.warming` 不存在(ls 與 cat 都回 No such file),沒有可刪或可保留的鎖。圖譜鏡頭沒附固定席筆記,這份報告沒有逐條核對圖譜合約。

本輪修補只動了測試、計劃筆記、guard-kill 筆記和 anchor 基準。`scripts/lumos` 在 02fd3bd 與 744f7b6 之間完全沒變。所有改壞都做在修後版 744f7b6 的複本上,每次改前清 `__pycache__`,改完還原。

## 1. 合併基準逾時上限的「剩下總時限」呼叫端沒有任何測試守(全部 132 支合併測試照綠)

severity: major
blocking: 是

引句:「合併快篩與合併基準的上限都不超過剩下的總時限(最少 1 秒),所以一次呼叫最多超出 `--max-seconds` 約 1 秒加一支逐支的時間」

file: `scripts/lumos:28957`

這句是本輪新寫進計劃做法 4 的條款,對應 S7「合併基準的上限應是 min(max(S × 2, 下限), 剩下的總時限)」。

- 本輪只替快篩補了端到端案例。
- 合併基準走 `_choice_merge_base_cap(..., max(mg.remaining(), 1.0))` 這個呼叫端,沒有對應的端到端案例,純函式測試也碰不到它。
- 這跟本輪新寫的 PITFALL 是同一類:「只測上限的純函式時,呼叫端改回舊算式測試照綠」。

失敗場景:呼叫端不再傳剩下時限,合併基準就可能睡滿 `max(S×2, 下限)`,遠超 `--max-seconds`。這正是 S7、S9 想擋的拖過寬限期。

重現(修後版複本):把 `c.floor, max(mg.remaining(), 1.0))` 換成 `c.floor, 1e9)`,執行 `python3.14 scripts/test_lumos.py -k t_choice_kill_merge`。結果是 `132 passed, 0 failed`。縮小範圍到 `-k t_choice_kill_merge_baseline` 是 14 支全綠。

對照組:同樣改壞快篩那處(`_choice_merge_screen_cap(...)` 換成 `max(m_el * 5, c.floor)`),`-k t_choice_kill_merge_screen_cap` 會紅。

歸因:有證據的原有漏查。修補沒有造成它,但修補宣稱的條款涵蓋它。修前 `scripts/lumos` 與修後相同,修前測試集是修後的子集,所以修前同樣全綠。修前版我沒另外跑,這是依「程式與測試子集關係」的推論,不是實跑結果。

## 2. `t_choice_kill_merge_budget_edge` 沒釘「已量平均」,只是用「全部一樣」的耗時

severity: minor
blocking: 否

引句:「m._kill_run = lambda cmd, run_dir, cap, **_kw: (0, "", 2.0, False)」

file: `scripts/lumos:28984`

- 每支耗時都固定 2.0 秒,所以平均、最後一支、最大值在這案算出來都一樣。
- 計劃與 PITFALL 寫的是「用實測平均重估」。

改壞後的結果(都在修後版複本):

| 改壞 | `-k …budget_edge` | `-k t_choice_kill_merge_budget`(8 支) |
|---|---|---|
| `sum(measured) / len(measured) * left` → `measured[-1] * left` | 全綠 | 全綠 |
| 換成 `max(measured) * left` | 全綠 | 全綠 |
| 換成 `sum(measured) * left`(忘了除) | 全綠 | 全綠 |

被保護的行為是「重估多保守」,不是會放行錯誤結果,所以降為 minor。⚠ 編排者可決定要不要補一個耗時不等的案例(例如 1 秒與 3 秒)。

歸因:未判定。這支測試是修補新增的,修前沒有,沒有可比較的修前結果。

## 3. 條款 `[test:]` 掛載

- S4 新掛的 `t_choice_kill_merge_screen_cap` 守的是快篩的剩下時限上限。這比較貼近 S7 的上限公式,S4 的七種不乾淨情境它碰不到。這是措辭上的錯位,不會讓測試或推送擋下,所以不單列為 finding。
- S19 新掛的 `t_choice_kill_merge_edges` 有守門檻的邊界。我把 `mg.remaining() < len(uniq) * …` 改成 `<=`,該測試紅在「三支、剩 45.0 秒(門檻 45)→ 合併」。
- S20 新掛的 `t_choice_kill_merge_no_lane_chunk` 有守「壞法配方一支都不在合併道就不開快篩」。我把 `_kill_merge_in_lane` 的回傳改成 `return True`,該測試紅 2 條。

## 已驗主張(修後版)

引句:「呼叫端要真的把剩下時限傳進上限,只測純函式時呼叫端改回 max(基準 × 5, 下限) 照綠。」

- 快篩上限的端到端測試:改回舊算式 → `5 passed, 1 failed`,紅在「快篩有開跑、被剩下時限收掉」。拿掉 `max(remaining, 1.0)` 的下限保護 → 紅在「剩負數 → 1」。改成 `max(…)` 取大 → 5 條紅。
- `t_choice_kill_merge_budget_edge`:
  - `<` → `<=`,剩 6.0 那案紅。
  - 拿掉重估(`if False`),剩 5.99 那案紅。
  - `left` 改成 `left-1` 或 `len(uniq)`,紅。
  - 倍數 K 改成 1.0,紅。
- 抗不穩定性:`t_choice_kill_merge_screen_cap`(約 34 秒)在 14 個吃滿 CPU 的程序下四份並行,四份都是 6 passed。單跑也是 6 passed。
- 單支基準被截斷不記成基準:把 `cap = min(full, max(mg.remaining(), 1.0))` 改成 `cap = full` → `t_choice_kill_merge_budget_reestimate` 紅。

引句:「`_gradle_test_module` 只跟它共用模組各段的檢查(`_gradle_module_parts`),回傳不變」

- `_gradle_module_parts` 存在於 `scripts/lumos:77444`,筆記句子與程式一致。

## 三問

1. 原問題(r2 邊界 #1 重估卡線、r2 通才 #1 快篩上限呼叫端):
   - 這兩處的修復有行為證據。
   - 快篩那處,改壞測試會紅。
   - 重估那處,`<`/`<=`、有無重估、`left`、K 改壞都會紅。
   - 平均 vs 其他統計量沒被釘住(finding 2)。
2. 相鄰呼叫路徑:合併基準的剩下時限呼叫端沒守(finding 1),同類路徑沒被一併補上。其他路徑(單支基準截斷、門檻邊界、無合併道)改壞會紅。
3. 同一案例的修前結果:`scripts/lumos` 沒變,所以修前修後行為相同。新增的兩支測試在修前不存在,修前版我沒另外跑。

未驗範圍:S9 的 `signal_race`、S8 斷路器、S10 多平台、S14 的真實路徑圍欄。這些本輪沒有改動,我沒改壞驗證。

工作樹與暫存目錄已移除,沒有殘留的 `邊界-sonnet` 目錄與 worktree。

總結:最高嚴重度 major
