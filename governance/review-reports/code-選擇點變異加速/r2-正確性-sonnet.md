severity: clean

我逐 hunk 讀完 r2-repair.patch,對照 HEAD 02fd3bdf5 的真碼追了案例。五項重點都沒找到會出錯的輸入,零 finding。

我自己沒有拿到測試結果。`python3.14 scripts/test_lumos.py -k choice_kill_merge` 在 after worktree 跑了超過 6 分鐘都沒收尾,我中止了。修前版(22751fcc)我沒起 worktree,所以「修前、修後各自的結果」那條沒做,以下結論都是靜態追碼得來,不是行為證據。worktree 已移除,臨時目錄已空。

## 已驗主張(靜態追碼)

**1. 登記後再看停止旗標(訊號競態)成立。**
引句:「if merge is not None and merge.interrupted:   # 訊號在登記之前就來過:回呼沒看到這支,當場收掉」
- 訊號落在三個位置的結果:
  - Popen 之前或 `_lumos_merge` 標記之前:登記後的檢查會收掉。
  - 登記之後、檢查之前:回呼已收一次,檢查再收一次,對已死程序群組重複 kill 無害。
  - 檢查之後:回呼收得到。
- 回呼設旗標與 `st.got` 在同一個訊號處理器內,不會被打斷,所以 `should_stop` 與 `interrupted` 不會互相矛盾。
- 呼叫端善後都有接上:
  - 合併基準在 `_kill_run` 之後檢查 `mg.interrupted`,有就 `_KillHalt`。
  - 快篩先還原壞法,再檢查 `interrupted`。還原失敗回 "break" 時,下個平台迴圈開頭的 `hk.between()` 會因 `st.got` 丟 `_KillHalt`。
- 單支基準與逐支流程不傳 `merge`,不會被誤收。
- file: `scripts/lumos:28198`、`scripts/lumos:28891`

**2. 量基準時的時限重估成立。**
引句:「if measured and mg.remaining() < sum(measured) / len(measured) * left * _CHOICE_MERGE_BUDGET_K:」
- 第一支沒有 `measured`,不重估;`left` 含當前這支,算法對。
- 重估觸發就回 False,`_kill_merge_base` 回 None,平台組標「基準」並退回逐支。已量的基準留在 `baselines`,沒量的由逐支流程用到才量。
- 截斷的那支:`b_to and cap < full` 時不寫入基準就回 False,逐支會照完整上限重量,不會被記成基準非綠。
- 卡線情形:`cap == full` 而逾時,基準照寫並以 `b_to=True` 排除出合併道,語意正確。
- `base_secs` 在 `finally` 累加,收手與中斷也照記。
- file: `scripts/lumos:28984`

**3. 快篩逾時上限成立。**
引句:「return min(max(m_el * 5, floor), max(remaining, 1.0))」
- 剩餘時限為負時上限是 1 秒,但 `_kill_merge_screen` 開頭已先看 `should_stop`(含總時限),實務上不會用 1 秒去跑。
- 被總時限截斷而逾時的快篩算「逾時」並計入斷路器、改交逐支,隨後 `between` 因總時限丟 `_KillHalt`,不會誤判存活。
- 不會有「回合併判存活」的錯方向,這點符合合併只判存活的合約。

**4. 沒有合併道的壞法跳過快篩成立。**
引句:「or not _kill_merge_in_lane(c, chunk, lane):」
- 配方全不在合併道時不套壞法、不開快篩,直接交逐支,逐支那邊會記 abort。
- 這個壞法不進 `survived`,`judged` 是 single。
- 判斷前一行先跑 `hk.between()`,上一個壞法的列已交出。
- 部分配方在合併道、部分不在時,仍走快篩;不在道的記 abort,與修前行為相同。

**5. 刪掉 `on_row` 的 `judged` 欄位後的讀者沒有受影響。**
引句:「plats = p.get("plats") or ()」
- 全 repo 對 `judged` 的讀取只有兩處,都讀帳上的 choice-kill 事件,不讀 `on_row` 的列:
  - `scripts/lumos:18559`
  - `scripts/lumos:78342`
- `_ChoiceKillRun.add` 一律初始化 `p["plats"]=set()`,且只收有配方的平台。舊的 `or {…}` 回退分支本來就走不到,拿掉不改行為。
- `finish` 現在才讀 `merge.survived`。`survived` 只增不減,而且是在 `_kill_merge_emit` 之後才加入,列是下一次 `hk.flush` 才交出,所以時序與舊版在 `on_row` 內算的一致。
- 多平台案例:A 平台快篩判全存活、B 平台逐支,結果是 single,正確。
- file: `scripts/lumos:78919`、`scripts/lumos:78944`

**6. 新舊互讀。** 修補沒動帳的欄位與型別登記,缺 `judged` 的舊帳仍讀成 single(`scripts/lumos:18559`)。

## 回答三問

- **①原問題的修復效果有何行為證據?** 靜態上看,四個原問題的修補機制都成立。行為證據(新增測試 `t_choice_kill_merge_budget_reestimate`、`_signal_race`、`_screen_cap`、`_edges`、`_no_lane_chunk` 在修前紅、修後綠)沒有跑成,標未判定。
- **②修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
  - 靜態追碼成立:無訊號、訊號在登記前、訊號在登記後、時限不足、基準被截斷、單平台、多平台、`--no-merge`,這些路徑都追過。
  - 未驗:真實 Gradle 的程序行為,以及 `_kill_run` 在 Windows 的路徑。
- **③新發現的同一案例在修前、修後各是什麼結果?** 沒有新發現,不適用。

未驗範圍:修前版的實跑結果;`t_choice_kill_merge_*` 全組的實際通過數。

總結:最高嚴重度 clean
