severity: minor

我找到 3 條候選,沒有 major。

先答圖譜鏡頭。這次沒附固定席節點,我只能照派工詞查 repo。這份 diff 沒有破壞 `cmd_guard_kill` 的其他呼叫者,也沒有破壞 `_choice_merge_classify` 的其他呼叫者。

- `cmd_guard_kill` 有三個呼叫處:`scripts/lumos:27697`(`guard kill` 的 `kill-add --try`)、`scripts/lumos:77195`(`situation-rule`)、`scripts/lumos:84161`(`guard kill` 命令列)。這三處都不傳 `stop_group_on`、`on_row`、`should_stop`,所以 `hk.on` 是假。新加的 `res["_single"]` 只在 `hk.on` 時設,它們的結果列完全不變。
- 只有 choice-kill 會帶上 hook。`_single` 在 `--json` 輸出裡有被濾掉,`result_out` 的列是白名單欄位,所以不會漏出去。
- `_choice_merge_classify` 新加的 `failed` 是選用參數,回傳形狀沒變。在 `_kill_merge_base` 裡呼叫時不傳 `failed`,行為跟舊的一樣。
- 八個角度裡,「被刪掉的行為」那條,我找到的新增行為都有補在別處:
  - 拿掉「少於 2 個壞法不合併」:已有測試翻案,文件、計劃、docstring 都同步改過,沒有殘留舊字樣。
  - 時限門移到最後:`tq`、`rdir` 這幾道改成各自印原因,條件沒放寬。

候選一

severity: minor
blocking: 否。講得出具體情境,但這是計劃明寫接受的取捨,不會做出錯判。

file: `scripts/lumos:29075`(`_kill_merge_iter` 的 `yield from _kill_merge_failed_first(c, chunk)`)

引句:「代價:判定可能在殺掉與跑不出結果之間換,不會變成存活」

失敗情境:守 a、b、c 三支,壞法其實 a 能殺掉,但 c 單支會逾時。

- 合併快篩把 c 列進失敗名單。
- 先紅順序先跑 c。c 逾時是 `timed_out_weak`,算決定性,於是整個壞法記成 no_result。
- `--no-merge` 照原順序先跑 a,結果是 killed。

這個情境在 `t_choice_kill_merge_failed_first` 的 S1 案五有測,所以是已知行為。我列出來是因為同一份程式在「開或關合併」之間會給出不同判定。這份分歧會寫進治理帳,而治理帳是 RETIRE-IF 判斷合併要不要保留的依據。計劃已經把它當成取捨接受,所以只列為 minor。

候選二

severity: minor
blocking: 否。只是效率上的退步,不是行為錯。

file: `scripts/lumos`,`_kill_merge_ready` 拿掉 `n_mutants < 2` 那一行的地方。

引句:「一個壞法也合併(存活的單一壞法逐支要付全部支數的呼叫)」

失敗情境:`--only <某行>` 且那個壞法很快就被第一支測試殺掉。

- 現在一定先把全部 N 支單支基準量齊,再跑合併基準、合併快篩,最後才逐支。
- 舊流程是用到哪支才量哪支,第一支就殺掉時只付 1 次基準加 1 次壞法呼叫。
- 計劃只量化了「存活」那一側的收益,「被殺掉」那一側變慢沒有數字。
- 時限門會擋掉量不齊的情況,所以不會失控,只是在 169 支的 `--only` 上,一個早殺掉的壞法要多付整輪基準。

我沒有實機重現,只讀碼推出來,所以維持 minor。

候選三(清理)

severity: minor
blocking: 否。具體代價是死參數與浪費的計算。

file: `scripts/lumos`,`_KillMerge.__init__` 的 `n_mutants`,以及 `_ChoiceKillRun.run` 裡 `len({r["group"] for r in self.recipes})`。

引句:「n_mutants(只剩建構簽名相容,不再當合併條件:一個壞法也合併,」

- `n_mutants` 現在沒有任何讀者(grep 只剩建構式的賦值和 docstring),卻仍在每次建構時算一遍。
- 兩份筆記都把它寫成「只剩簽名相容」,等於承認是死碼。
- 順帶一個不精確處:`_kill_merge_off` 對「基準量不齊」印的「合併要先量齊 {n} 支基準」,n 是還沒量的支數(`left`),不是全部支數。使用者會被誤導成只缺 n 支。

已確認沒問題的幾處

- `single_runs`:只有 `cmd_guard_kill` 那條真的逐支跑的路徑會標 `_single`。合併判存活交出的列、略過列、基準不綠的 abort 列都不帶,所以計數沒有多算。
- `merge_kind`、`merge_unclean`、`merge_off`:型別都有登進 `_GOV_FIELD_TYPES`,舊帳缺欄的讀法有測試覆蓋。
- `_kill_merge_breaker` 累計的原因字串全是固定字串,沒有帶使用者內容,印出來不用額外跳脫。

總結:最高嚴重度 minor,blocking 0 條。
