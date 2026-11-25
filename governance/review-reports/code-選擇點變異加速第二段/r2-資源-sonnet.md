severity: clean

資源席 r2,只看修補差異 r2-repair.patch 的 `scripts/lumos` 部分(patch 第 228–534 行),並對照修後真碼 `_kill_merge_ready`、`_kill_merge_base`、`_kill_merge_singles`。我沒有實跑實驗,全是讀碼推論。固定席筆記沒附(鏡頭計算超時)。

**問題①:逾時、Ctrl-C、例外時有沒有子程序沒被收掉**

這次修補沒有碰程序的建立或回收。新增或改動的都是記帳:
- `_kill_merge_off` 多了 `quiet`。
- `merge_off` 改由 `mg.plats` 算出。
- `_single` 改名 `_ran_solo`。
- `__init__` 去掉 `n_mutants`。

程序回收路徑原樣沒動:
- 第一個訊號來時,`on_signal` 照舊用 `_kill_proc_group` 收掉帶合併標記的程序群組。
- 合併基準途中被中斷時,`_kill_merge_base` 在 `_kill_run` 回來後看 `mg.interrupted`、丟 `_KillHalt`;`finally` 照舊累加 `base_secs`。
- `_kill_merge_iter` 接住 `_KillHalt`,記「中斷」後再往外丟。這裡的「中斷」記進 `mg.plats[plat] = (False, "中斷")`,`quiet=True` 只是不印,沒有新增任何需要收的資源。
- 「合併道不足 2 支」(`_kill_merge_ready` 與 `_kill_merge_base` 兩處)都是在還沒開子程序前、或單支基準已跑完且正常結束後提前 return。

- claim:修補沒有引入新的孤兒程序
- input:Ctrl-C 或終止訊號落在合併基準途中,以及落在單支基準量測的兩段之間(`hk.between` 丟 `_KillHalt`)
- expected:合併程序群組被收掉,單支基準照既有行為等跑完
- case_source:`on_signal` 與 `_kill_merge_base`,都不在 r2-repair.patch 的改動行內
- before/after:該段程式修前修後相同
- comparison:未判定因果的實測,只有讀碼比對

**問題②:時間預算在大輸入或慢機器上會不會誤擋或誤放**

- 「合併道不足 2 支」放在時限門之前,同名測試不到 2 支就直接不合併。這會讓只有 1 支名字的平台組不再被提示「調大時限」,而照做後仍不合併,方向正確。
- 時限提示的支數與估秒改用全部支數估。重跑是新的一次呼叫,`c.baselines` 從空開始,基準要全部重量。所以用全部支數估才對。
- 一處小不對稱,不構成 finding:`_kill_merge_singles` 內「要不要收手」的門用 `left`(還沒量的支數),提示用的是全部支數,而且 X 還把已花的秒數算進去。結果是提示偏保守,多帶一些秒數,不會導致帶了仍不合併,也沒有讓正常操作被擋下。
- 沒有新增迴圈或睡眠,時間成本沒有變大。

**問題③:大輸入一次讀進記憶體或二次方工作**

patch 新增的資料結構只有這幾個:
- `mg.plats`,key 是平台,規模是平台數。
- `merge_off` 的字典推導,同樣是平台數。
- `unclean` 計數,key 是固定原因字串。

這幾個都跟輸入大小無關。沒有新增讀整檔或巢狀掃描。

**其他**

`merge_off` 現在由 `mg.plats` 算,排除原因「斷路器」(另由 `merge_tripped` 表達)。我檢查了所有寫入 `mg.plats` 的位置:`_kill_merge_off`、斷路器那行、啟用那行。沒有第四種寫法會產生未預期的原因字串進報告。

總結:最高嚴重度 clean,blocking 0 條。未驗範圍:沒有實跑巨量壞法(約 169 支)的時間與記憶體,也沒有實測 Ctrl-C 後殘留程序。
