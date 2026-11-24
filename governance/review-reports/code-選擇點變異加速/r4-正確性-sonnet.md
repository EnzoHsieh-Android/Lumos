severity: clean

**審查結論**

修補差異只動測試、帳本簽名和筆記,沒有改 `scripts/lumos`。我在 after(100d3851)與 before(744f7b6d)兩個臨時 worktree 各跑了指定的測試,也各改壞程式一次看新測試會不會紅。臨時 worktree 已移除,`git worktree list` 已確認。

**已驗主張**

1. `t_choice_kill_merge_cap_wiring` 攔到的是真正那兩個呼叫端。
   引句:「        return orig(cmd, cwd, timeout, *a, **kw)」
   - `scripts/lumos` 裡帶 `merge=` 的 `_kill_run` 呼叫只有兩處:合併基準 `scripts/lumos:28959` 和合併快篩 `scripts/lumos:29075`。單支基準 `scripts/lumos:28987` 和逐支 `scripts/lumos:28529` 都不帶,所以 `kw.get("merge") is not None` 剛好篩出這兩處。
   - `_kill_run` 是模組全域名稱,`m._kill_run = spy` 攔得到。
   - after 版實跑 3 個 ✓,實際收到的逾時值約 59 秒、58.9 秒、56.9 秒。
2. 斷言能被合理改壞翻紅。每次改完都先清掉快取再跑。
   - 合併基準的上限改成 `1e9`:第一次收到 300,「邊界 #1」那條紅。
   - 快篩上限改回 `max(m_el * 5, c.floor)`:後兩次收到 300,「通才 #1」那條紅。
   - 改壞後都已用 `git checkout` 還原。
3. 例外路徑有還原。
   - `spy` 的設定在 `try` 內,還原在 `finally`,攔截不會漏掉。
   - `root = fake = None` 先設好,`_ck_cleanup` 有 `if x` 判斷(`scripts/test_lumos.py:144196`),`_ckm_repo` 丟例外時不會再炸一次。
   - `_ckm_inproc` 的 `finally` 也還原環境與工作目錄。
4. 重估卡線新案例的預期值手算對,跑出來也是 3 支與 1 支。計算時 `mg.remaining` 是常數。
   - 剩 3.0 秒:量完第一支(1 秒),門檻 1×2×1.5=3.0,`3.0<3.0` 不成立,照量;量完第二支平均 2,門檻 2×1×1.5=3.0,照量第三支。結果量齊 3 支。
   - 剩 2.99 秒:第一支後 `2.99<3.0`,收手,只留 1 支。
   - 改成總和:第二支後門檻 6,收手而紅。改成最後一筆或最大值:門檻 4.5,收手而紅。
   引句:「        took = {"run aCase": 1.0, "run bCase": 3.0, "run cCase": 1.0}」
5. S22–S24 的字面跟程式一致。
   - S22:基準上限 `min(max(total*2,floor), max(remaining,1))`,快篩上限 `min(max(m_el*5,floor), max(remaining,1))`,都不超過 max(R,1)。
   - S23:`mg.remaining() < 平均 × left × 1.5` 才停,剛好等於照量;`left` 含當前這支。
   - S24:`_kill_merge_in_lane`(`scripts/lumos:29091`)先看配方跟合併道有沒有交集。
   - 條款重新綁定後 `t_choice_kill_merge_no_lane_chunk`、`t_choice_kill_merge_budget_edge`、`t_choice_kill_merge_budget_reestimate` 都還在檔裡。
   - S20「綠的不到 2 支不合併」改由 `t_choice_kill_merge_baseline_red` 的第二案守,檢查內容對得上。
   引句:「- [S24] 當某個壞法的配方一支都不在合併道時,choice-kill 應 不套壞法開快篩、直接交逐支流程,這個壞法的 `judged` 應 不是 merged」

**修前與修後**
- before 版 `-k choice_kill_merge_screen_cap`:6 passed,耗時 32.7 秒,是靠真實睡眠的舊端到端案例。
- after 版 `-k choice_kill_merge_cap_wiring`:3 passed,8.7 秒。
- after 版 `-k choice_kill_merge_budget_edge`:4 passed,0.1 秒。
- 舊案例「負載下隨機紅」那個說法我沒有重現,維持未判定。

**未驗範圍**
- 沒跑 `_reestimate` 以外的其他測試,也沒跑全套。
- 兩次改壞實驗用同一指令各跑一次,結果穩定,沒有需要重跑的不穩定。

**唯一的小缺口,依抑噪紀律不列為 finding**
- 把快篩呼叫端的 `mg.remaining()` 換成常數 `60.0` 時,測試仍綠(我實測過)。
- 原因是斷言只比 `≤ 60`,沒比「隨時間遞減」。這種改法不像合理的回歸,不影響 S22 宣稱要擋的錯(下限穿過剩下時限)。

總結:最高嚴重度 clean
