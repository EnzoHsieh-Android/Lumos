severity: clean

**審查結果:資源鏡頭沒有發現問題,零 finding。** 先用白話講:這次新增的程式沒有新開長壽程序,也沒有新的二次方或無上限的記憶體用量。

## 已驗主張

1. **子程序都有收:** 新增的 `_kill_merge_base_run` 和重試路徑,都走原本的 `_kill_run`。
   - 逾時走 `_kill_proc_group` 再 `wait()`。
   - Ctrl-C 的 `KeyboardInterrupt` 也會先收程序群組再往上丟。
   - 訊號落在登記之前的空窗,有「登記後再看一次 interrupted」補上。
   - 重試前有 `c.hk.between()`,重試後有 `mg.interrupted` 判斷並丟 `_KillHalt`。
   - 事件初始化腳本放在 `scratch` 底下,隨 `_isolated_worktree` 收尾整個刪掉,不會殘留。
   - 證據:file: `scripts/lumos:28194`(`_kill_run`);diff 的 `_isolated_worktree` hunk 把 `scratch=parent` 掛在 `parent` 上,收尾刪的就是 `parent`。
2. **時間預算:** 重試上限是 `min(cap, max(mg.remaining(), 1.0))`,不會超過總時限。快篩上限仍受 `_choice_merge_screen_cap` 約束。
   - 重試只在「帶腳本且原因是找不到 JUnit 結果檔」時發生,逾時不重試。所以一次基準最多多一次;Gradle 拒收腳本時是在跑測試前就失敗,多花的時間很短。
3. **記憶體與計算量:** 我把 `_choice_merge_events` 抽出來實測,輸出上限 `_KILL_OUT_CAP` 是 256KB。
   - 30 萬字元的單行、`" > "` 重複 6 萬次的長行、一行裡 4 萬個 `" > "` 的寬行,都在 3 毫秒內解完,是線性的。
   - 500 名字配 500 筆事件:0.08 秒。
   - 人工湊出的最壞輸入(1000 名字配 8000 筆互不相同的事件)需要 2.4 秒。但 `--tests` 篩選把輸出限制在合併道的測試上,事件筆數接近名字數,所以實際不會到這個量。`_choice_merge_cmd` 的長度上限 32768 位元組也限制了名字數。
   - 逾時時 `_choice_merge_timeout_kind` 呼叫一次 `names=[]` 的解析,之後 `_kill_merge_screen` 再解一次。兩次都是線性,不是二次方。
4. **文件與程式對得上:** 逐項對過(`_choice_merge_events` 的測試是 diff 裡新加的,`pitfall` 的 repro 我另外跑了):
   - `\xa0`、`\r` 靠 `rstrip()` 處理,與文件一致。
   - 重試上限的公式與 S6 的「≤ 30」測試一致。
   - `hang_breaker` 建構參數存在。
   - 恢復後兩個連續計數都歸零,`_kill_merge_trip` 與 `_kill_merge_breaker` 的恢復分支都做到。
   - `guard-kill.md` 的 PITFALL 例子(`foo (bar)` 因 `(` 被截掉)我跑過,回 failed 空,與寫的一致。
5. **修前修後:** 兩版 `scripts/` 相同,這輪修補只動文件(`r3-repair.patch` 全是計劃與 `guard-kill.md`),所以沒有修復回歸。

## 未驗範圍

- 沒用真 Gradle 跑,只在假 Gradle 與單元層面看。
- 沒測 Windows 路徑。
- `_CHOICE_MERGE_HANG_BREAKER=15` 的時間成本只讀碼估算,沒實測:最多 15 次逾時,每次上限約基準時間的 5 倍,且受剩餘總時限約束。這是計劃裡承認的取捨,不是缺陷。
- 其他席負責的角落沒重審:不同時寫入、安全面、資安護欄登記。

## 三問

1. **有沒有會殘留孤兒程序的路徑?** 沒有。理由見主張 1,與原本的 `_kill_run` 路徑一致。
2. **時間預算會不會在大輸入或慢機器上把正常操作擋下或放行?** 沒有。重試與快篩都受剩餘時限夾住。唯一的放寬是掛住斷路器從 5 改 15,最壞多花時間,但仍受 `--max-seconds` 限制,結果不會變錯。
3. **有沒有一次讀大輸出進記憶體或二次方工作?** 沒有新增的。輸出被 256KB 上限截斷,解析是線性的。唯一的 N×U 比對在實際規模下是毫秒級,最壞人造輸入約 2.4 秒,也不會讓結果變錯。

最高 clean,blocking 0 條
