severity: minor

我在修後版(`100d3851c`)複本上做了 13 種具體改壞,涵蓋 S22、S23、S24 的主要路徑。9 種被測試抓到,3 種全部照綠,1 種(`M10`)被整批 `-k` 抓到但我沒用目標測試單獨驗過。沒有 major 以上的發現。修補差異只動測試檔、計劃與圖譜文件,以及 `governance/anchor-baseline.json`,`scripts/lumos` 本身沒有改,所以沒有修前/修後的行為差可比。

## 已驗主張

三處改壞分別對應 S22 呼叫端接線、S23 平均重估、S24 不在合併道的快篩,測試都紅了。

引句:「合併基準呼叫端改成不帶剩下時限(例 1e9)→ 第一次超過 60 而紅;快篩呼叫端改回 max(基準 × 5, 下限) → 後兩次 300 而紅。」

- **S22 合併基準呼叫端:** 改成 `1e9` 後,`t_choice_kill_merge_cap_wiring` 紅,收到的逾時是 `[300.0, 58.7, 56.7]`。
- **S22 快篩呼叫端:** 改回 `max(m_el * 5, c.floor)` 後同一支測試紅,收到的逾時是 `[59.25, 300.0, 300.0]`。
- **S22 快篩的 `max(R,1)`:** 拿掉後 `t_choice_kill_merge_screen_cap` 紅。
- **S22 基準上限的 `min`:** 拿掉 `min(...)` 這一改壞我只跑了整批 `-k choice_kill_merge`,沒另外記是哪一支紅,不能單獨歸給 `cap_wiring`。這次只在另一個 worktree 中途被我自己殺掉重跑,不影響結論。
- **S23 平均換成總和、最後一筆或最大值:** `budget_edge` 紅,輸出為「剩 3.0 秒 → 量了 3 支」那條斷言。
- **S23 比較式與常數:** `<` 改 `<=`、拿掉 1.5 倍、`left` 改成全部支數,`budget_edge` 與 `budget_reestimate` 都紅。
- **S23 截斷逾時仍寫進 baselines:** 改壞後 `merge_budget` 紅(3 條斷言)。
- **單支基準呼叫端不帶剩餘時限:** `budget_reestimate` 紅。
- **S24 `_kill_merge_in_lane` 恆回 True:** `t_choice_kill_merge_no_lane_chunk` 紅,輸出為「壞法 2 只配 charlieCase(基準紅、不在合併道)→ 沒有合併呼叫」那條斷言。
- **S20/S19 相鄰路徑:** 開跑門檻 `<` 改 `<=`,整批 `-k choice_kill_merge` 紅;拿掉 `measured and` 後同批紅,`S2` 兩條斷言失敗。

[test:] 對應檢查:S22 掛的 `cap_wiring` 與 `screen_cap`、S23 掛的 `budget_edge` 與 `budget_reestimate`、S24 掛的 `no_lane_chunk`,都真的守到各自那條的主要改壞。下面三處缺口都不影響主要路徑。

## Findings

1. 重估用的統計量換成最小值,測試照綠

severity: minor
blocking: 否
引句:「量完第二支平均 2、門檻 2×1×1.5=3 照量 → 三支量齊。改成總和(門檻 6)或最後一筆、最大值(門檻 4.5)→ 第二支後就收手而紅。」
file: `scripts/lumos`(`_kill_merge_singles`,`mg.remaining() < sum(measured) / len(measured) * left * _CHOICE_MERGE_BUDGET_K`)
失敗場景:把 `sum(measured) / len(measured)` 改成 `min(measured)`,`-k merge_budget` 結果是 10 passed 0 failed。中位數與這組輸入(1、3、1 秒)的最小值相同,也等同過關。
原因:新案例只試剩 3.0 與 2.99 兩個值,最小值與平均在這兩點上的收手決定一樣。若再加剩 2.0:平均門檻 3 會收手,最小值門檻 1.5 會照量,就分得開。
重現:在修後版把該行改成 `min(measured)` 後跑 `python3.14 scripts/test_lumos.py -k merge_budget`。
歸因:未判定(修補新增的案例沒擋住這個變體;修前版沒有這個案例,我沒跑修前版)。

2. S22 條款說基準上限也是 max(R,1),但沒有任何測試守基準這一側

severity: minor
blocking: 否
引句:「當總時限只剩 R 秒、而且 R 小於下限時,choice-kill 送給合併基準與合併快篩的逾時上限 應 都不超過 max(R, 1) 秒」
file: `scripts/lumos`(`_kill_merge_base`,`_choice_merge_base_cap(..., c.floor, max(mg.remaining(), 1.0))`)
失敗場景:把呼叫端的 `max(mg.remaining(), 1.0)` 改成 `mg.remaining()`,`cap_wiring`、`screen_cap`、`merge_budget`、`merge_edges` 四支都綠。`cap_wiring` 的剩餘時限固定約 60 秒,沒有小於 1 秒的情境,所以只有快篩那側的 `max(...,1)` 被 `screen_cap` 守住。
重現:同上改壞後逐支跑上述四個 `-k`。
歸因:未判定(沒跑修前版)。

3. 單支基準上限的 `max(..., 1.0)` 沒有測試守

severity: minor
blocking: 否
引句:「還沒量的支數 × 已量的平均耗時 × 1.5 超過剩下的總時限時,choice-kill 應 不再量、這個平台組這次不合併」
file: `scripts/lumos`(`_kill_merge_singles`,`cap = min(full, max(mg.remaining(), 1.0))`)
失敗場景:改成 `min(full, mg.remaining())`,四支目標測試全綠。這處不在 S22/S23 條款字面內,只是同族呼叫端。
歸因:未判定。

## 三問

- **原問題的修復效果:** 靠真實睡眠的端到端案例被換成 spy 攔 `_kill_run` 的參數,改壞呼叫端時能穩定翻紅。
- **修補處的相鄰路徑:** 我跑到的路徑都仍成立。
- **新發現同一案例的修前/修後:** 三條 finding 都是修後版缺口,修前我沒跑。

## 未驗範圍與雜項

- **未驗範圍:** 並行負載下的隨機紅(`rc 1` 但未列出 FAILED 行,出現在 `M9` 的 `cap_wiring`、`screen_cap`、`merge_edges`)我沒分析原因,未判定。
- **暫存清理:** 已刪我確認的 13 個 `gctl-run-*` 現場,刪前跑過 `lsof +D` 無程序開著,另有約 5 個我沒能從輸出確認是自己的,沒動。兩個 worktree(`after`、`after2`)已用 `worktree remove --force` 移除,臨時目錄 `/tmp/lumos-seat-work/code-選擇點變異加速/邊界-sonnet` 已移除。
- **鎖檔:** 派工詞附的 `dispatch-lens/....json.warming` 我沒有動,也沒檢查內容。

總結:最高嚴重度 minor
