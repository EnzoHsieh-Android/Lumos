severity: minor

先交代:派工詞附的鎖檔 `…9715c2af….json.warming` 在這台機器上不存在(`ls` 回 No such file),我沒有刪或動任何鎖。

我在修後版(f14bd5881)的複本上做了 29 個具體改壞,每次改前清 `__pycache__`,跑 `-k t_choice_kill_merge_budget`、`-k t_choice_kill_merge_cap_wiring`、`-k t_choice_kill_merge_ledger_counts`。修後版未改動時這幾組都綠。

## 已驗主張

引句:「check("r4 通才 #1 耗時 1、5、1 秒、剩 3.0 秒 → 量了 2 支就收手(平均 3,不是最小值或第一支的 1)", got is False and len(c.baselines) == 2,」

- **重估統計量**:換成最小值、第一支、最大值、最後一支、總和、中位數,budget 那組全紅(6 個改壞都被抓到)。
- **重估的其他部分**:`left` 改成 `len(uniq)`、改成 1、改成 `max(left-1,0)`,`<` 改 `<=`,`_CHOICE_MERGE_BUDGET_K` 改 1.0,budget 那組全紅。
- **單支基準保底 1 秒**:拿掉 `max(…,1.0)`、改 0.0、改 2.0、整個改成 `full`,budget 那組全紅。
- **截斷那支不寫進基準**:改成寫進基準、或整個不檢查,都紅。

引句:「check("r4 邊界 #2 量完單支基準後剩下時限 -5 秒 → 合併基準收到的上限是保底 1 秒", bool(seen) and seen[0] == 1.0, str(seen))」

- **合併基準呼叫端**:拿掉 `max(mg.remaining(), 1.0)`、改成 `1e9`、改成 0.0,`cap_wiring` 都紅(3 個改壞)。
- **快篩呼叫端**:改成傳 `1e9`、改回舊算式 `max(m_el * 5, c.floor)`,`cap_wiring` 都紅(2 個改壞)。

引句:「check("r4 整合 #1 合併開著時 --json 輸出的存活列不帶 judged(判法只在收尾算一份)",」

- **結果列加欄位**:`_kill_merge_emit` 的存活列加 `"judged": "merged"`,`cap_wiring` 紅。
- **結果列只加在 `result_out` 白名單**:我改了 `result_out` 白名單加 `judged`,三組都綠。這不算 finding:派工說明寫明該白名單不走 `--json`,而且 `result_out` 的使用者是 kill-add,沒有讀 `judged` 的人。

## Findings

1. 單支基準「被截斷才不記」的比較式 `cap < full` 沒有邊界測試

severity: minor
blocking: 否

引句:「        if b_to and cap < full:   # 被剩下時限截斷:不算這支的基準」

(此行是修補前後都在的上下文行,不在 r5-repair.patch 內,以下為 patch 內相鄰逐字引句:`+        check("r4 邊界 #3 剩下時限 -5 秒 → 第一支單支基準收到的上限是保底 1 秒", bool(caps) and caps[0] == 1.0, str(caps))`,這個測試只驗上限,沒驗「剛好等於 full」。)

file: `scripts/lumos:28972`(`_kill_merge_singles`,量單支基準的函式)

失敗場景:
- 把 `cap < full` 改成 `cap <= full`。
- 剩餘總時限 ≥ full(600 秒)時 `cap == full`,單支真的跑滿上限逾時,應該記成「非綠基準」、讓這支退出合併道。
- 改壞後這種情況被當成「被截斷」:整個平台組不合併,退回逐支。方向是多擋,不會放行錯判,影響只是少了加速。

重現:在修後版複本把該行改成 `<=`,跑 `-k t_choice_kill_merge`(整個合併子集)得 140 passed, 0 failed,mutant 沒被殺。作者這輪新加的案例(1、5、1 秒與 -5 秒)都不碰 `cap == full`。

歸因:有證據的原有漏查。這一行修補前就在,這次修補沒動它。我沒有跑修前版,因為修前版這一行與修後版相同,結果不會不同。

## 三問答覆

1. **原問題修復效果**:r4 點名的重估統計量、保底值、呼叫端傳剩下時限、`--json` 不帶 `judged`,各自有對應的紅燈測試。我用 29 個改壞驗過,除上面那一條,沒有其他通過測試的 mutant。
2. **修補處的正常、錯誤與相鄰路徑**:
   - 正常路徑:修後版 `t_choice_kill_merge` 子集 140 passed(跑了兩次,兩次相同)。
   - 錯誤路徑:剩餘時限為負時單支基準與合併基準都保底 1 秒,有測試守住。
   - 相鄰路徑:快篩上限的內層保底 `max(remaining, 1.0)`,被我拿掉或改 0 時,在三組指定的 `-k` 下是綠的。
3. **新發現的同一案例修前修後**:我沒有跑修前版,理由同上。

**未驗範圍**:
- 快篩上限內層保底 `max(remaining, 1.0)`、`_choice_merge_screen_cap` 的 ×5、`_choice_merge_base_cap` 的 ×2:這三處我只在指定三組 `-k` 下跑,結果是綠。專屬的純函式測試在別的 `-k`(`scripts/test_lumos.py:147309` 有「剩負數 → 1」)。最後那次整個子集的跑法只在 `cap <= full` 的 mutant 上做過,這三處沒有在整個子集下重跑,所以無法判定它們有沒有被抓到。
- `anchor-baseline.json` 的簽章流程與 `guard-kill.md` 的文字沒有核對。

臨時目錄與 worktree 已移除,`/tmp/lumos-seat-work/code-選擇點變異加速/` 底下剩正確性席的目錄與共用檔,不是我建的,我沒動。

總結:最高嚴重度 minor
