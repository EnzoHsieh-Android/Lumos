severity: clean

## 說明
鎖檔 `…/ec6275be….json.warming` 我沒有動它。派工詞最後一句說照派工詞審查即可,而且它不是我建的。

## 已驗主張

**一、新測試在例外與提早結束時有還原被換掉的函式,也有收掉暫存目錄**

引句:「_ck_cleanup(root, fake, tmp)」
引句:「m._kill_run = orig」

- `t_choice_kill_merge_cap_wiring` 把 `m._kill_run` 換成 spy,還原寫在 `finally` 裡。
- `root = fake = None` 先宣告。`_ckm_repo` 中途丟例外時,`_ck_cleanup` 會跳過空值,不會噴第二個例外。
- 我看了 `_ck_cleanup` 的實作,它有 `if x:` 判斷。
- `t_choice_kill_merge_budget_edge` 新增的耗時不等案例也在原本的 `try/finally` 內還原。
- 跑完 5 組測試後,`/var/folders/.../T` 下沒有留下 `gctl-ckm-*` 或 `gctl-run-*`,也沒有殘留的假 Gradle 程序。
- 這項只驗了正常通過路徑上的收尾,沒有人為注入例外去測還原。

**二、時間餘裕夠**

下表的修後數字取自上限 180 秒的統計,機器負載約 6.9。

| 測試 | 修後第一次 | 修後第二次 | 餘裕 |
|---|---|---|---|
| `t_choice_kill_merge_cap_wiring` | 9.5s | 4.5s | 19x 至 40x |
| `t_choice_kill_merge_budget_edge` | 0.1s | 0.1s | 1700x |
| `t_choice_kill_merge_screen_cap` | 16.8s | 17.4s | 10x 至 11x |
| `t_choice_kill_merge_budget_reestimate` | 58.3s | 58.4s | 3x |

- `t_choice_kill_merge_screen_cap` 在修前(744f7b6d)跑一次是 32.4s,餘裕 6x。
- `t_choice_kill_merge_budget_reestimate` 這輪沒改,餘裕只有 3x,是這批裡最小的。
- 這個測試保留了「絕對時限」,這是上一輪刻意的選擇。兩次都穩定通過,沒有隨機紅。
- 新的 `cap_wiring` 用 spy 斷言傳入的逾時值,不靠真實睡眠,所以不受負載影響,這是這次修補的主要資收益。

**三、spy 測試真的抓得到錯(變異驗證)**

- 在我自己的修後 worktree 裡,把 `scripts/lumos:29075` 的快篩上限改回 `max(m_el * 5, c.floor), merge=mg)`。
- `t_choice_kill_merge_cap_wiring` 翻紅:`✗ r2 通才 #1 兩個快篩收到的逾時都 ≤ 剩下總時限 60 [59.33, 300.0, 300.0]`。
- 合併基準那條仍綠,與測試註解所說的翻紅釘一致。
- 第一次嘗試的 sed 因 macOS 語法失敗、沒有改到檔案,所以那次的綠不算證據。第二次改用 Python 確實替換後才出現紅。
- 這項只驗了快篩那一處,合併基準那處我沒有逐一改壞。

## 三問回答
1. **原問題的修復效果**:靠真實睡眠的端到端案例在負載下隨機紅,現在換成 spy 斷言。修後連跑兩次都綠,變異驗證會紅。修前沒有對應的 `cap_wiring` 測試,所以無法對同一案例做修前修後比較,這一項歸為未判定。
2. **修補處的正常、錯誤與相鄰路徑**:`screen_cap`、`budget_edge`、`budget_reestimate` 修後都通過,耗時不等案例(1、3、1 秒,剩 3.0 或 2.99 秒)通過。
3. **新發現**:無。

未驗範圍:
- 沒有人為在測試中途注入例外。
- 沒有跑 `t_choice_kill_merge_edges`、`t_choice_kill_merge_baseline_red`、`t_choice_kill_merge_no_lane_chunk`,它們不在這次修補的資源面。
- 沒有跑不帶 `-k` 的全套。

worktree 與暫存檔已用字面路徑清除。

總結:最高嚴重度 clean
