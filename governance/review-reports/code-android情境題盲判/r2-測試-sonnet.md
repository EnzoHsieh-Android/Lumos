severity: minor

先核對第一輪測試席 F1 到 F5,全部真的補上了。我在 `--shared` 複本上對程式改壞約 60 處(含複本內的 `check.py`),F1 到 F5 對應的每一處都翻紅:
- F1(多數決在統計裡算反):把統計裡區分證據提醒與多數決提醒的判斷拿掉,測試翻紅。
- F2(pitfalls 的盲判四步跟著 gate 設定):把條件改成「只要不是 off 就印」或「只認 all」,測試都翻紅。
- F3(doctor 印出 AI 段放行):把 doctor 那段 `_n_ais` 的印出改成不執行、把推送前的待看計數改成恆為 0,測試都翻紅。
- F4(`--disagreements` 排除已仲裁的格):拿掉排除條件,測試翻紅。
- F5(統計的邊界):終局判定改壞、先到者勝改後到者勝、`dict.fromkeys` 去重拿掉、總數事件 keys 展開拿掉、kappa 門檻 `>=20` 改 `>20`,各自翻紅。
- A2(仲裁採作者要記照做):改壞後測試翻紅。

作者說「39 處全翻紅」我沒抽到反例,下面的存活處都在他們挑的那 39 處之外。

鏡頭 2:兩條舊 S4 案例改成「兩位盲判都說沒照做」沒有拿掉原本該守的行為。「兩位盲判都判不適用」改成不出提醒,由 `t_blind_judge_two_blinds_needed_for_majority` 的三方列舉逐格守著。我把 `fv == ("applies", False)` 改成 `fv != ("na",)`,測試翻紅。

鏡頭 3:新測試的假輸入形狀跟真實寫入的 `blind-judge`、`dispositions`、`warned` 事件一致,沒有發現不一致。

鏡頭 4:筆記與程式在行為上沒有相反的地方。計劃、`Systems/棧別提問表態閘`、`Systems/kotlin規則包` 這幾處的 PITFALL、WHY、REVISIT 都跟程式對得上,只有下面 F5 一處名稱不準。

F1
severity: minor
blocking: 否
引句:「範圍走共用的 _codeloop_disp_range(推的不是主線就用 merge-base(主線, 版本)..版本,--diff 是推送範圍;分支頂端已在主線上就沒有段)」
- 這是 `_codeloop_disp_range` 裡「推的不是主線」那個判斷,測試沒有守。
- 改壞:`scripts/lumos` 的 `if ml and marker_branch and marker_branch != ml[0].split("@")[0]:` 改成 `if ml and marker_branch:`。
- 指令:`t_kt_situation`(135 項)、`t_dispositions_situation`(15 項)、`t_blind_judge`(97 項)。結果:全綠。
- 新增的 `t_blind_judge_range_shared_with_check` 只走「非主線分支」這一邊。
- 場景:推主線本身時範圍會誤走 merge-base 分支。
- 影響不大:merge-base 通常不等於被推版本,範圍多半只是偏大,只有「推送沒有新提交」時才會整題消失。

F2
severity: minor
blocking: 否
引句:「盲判就讀那一側的帳、那一側的分支名;目標分支自己有有效表態時,讀目標分支、讀工作目錄的帳。」
- 這是 `_disp_bj_source` 裡「合進來那一側的帳讀不到」的退路,測試沒有守。
- 改壞:`return rec.get("branch"), ("" if raw is None else raw)` 改成 `... raw)`。這樣一來側帳讀不到時,會退回讀工作目錄的帳。
- 指令:`-k t_blind_judge_follows_disposition_branch`,結果 2 passed。
- 程式註解寫明「讀不到就給空帳:照擋缺盲判,不退回讀工作目錄的帳」。測試的 `merge_ledger` 只回傳過非 None 的帳。

F3
severity: minor
blocking: 否
引句:「--disagreements 只列作者與第一盲判不一致、還沒仲裁的格:已有仲裁 → 不列;沒仲裁 → 列;」
- 這是 `_kt_bj_pick_rows` 在 disagreements 模式下「該格沒有第一盲判」要略過的那個分支,測試沒有案例。
- 改壞:拿掉 `not isinstance(first, dict) or`。
- 指令:`-k t_blind_judge_pick_rows_skips_arbitrated`,結果 5 passed。
- 改壞後的後果:`_kt_bj_blind_vote(first)` 會對 `None` 呼叫 `.get`,丟 AttributeError。
- 場景:`code-loop check` 同時印「缺第一盲判」和「缺仲裁」時,照提示跑 `--template --disagreements` 會直接崩。

F4
severity: minor
blocking: 否
引句:「兩位盲判一致判照做或不適用(跟作者不同)放行、印一行不用改碼」
- `blind_agree` 的摘要警告沒有測試。
- 改壞一:`cache["blind_agree"] = cache.get("blind_agree", 0) + notes["blind_agree"]` 改成 `pass`。
- 改壞二:`_kt_sit_summary_warnings` 裡的鍵名 `blind_agree` 改成別的字。
- 指令:`t_blind_judge_majority` 與 `t_blind_judge_two_blinds_needed_for_majority`。結果:兩者各自 13 passed。
- 後果:筆記宣稱「印一行不用改碼」,壞了之後作者看不到這個說明,但不影響放行判定。

F5
severity: minor
blocking: 否
引句:「仲裁採作者與採盲判的次數、段放行次數(分 ai 與 human)」
- 範圍 7 與統計的「採盲判」把「三方各異」也算進去了。
- 程式位置:`_render_gov_situation` 裡 `sum(1 for k, av in dis if arb[k] != av)`。
- 場景:作者判適用照做、第一盲判判不適用、仲裁判適用但沒照做,仲裁其實跟誰都不同,這一格仍被記成「採盲判 1」。
- 這是 r1 丙新增「三方各異」之後沒有同步改這處統計。只影響統計數字,不影響推送閘。

總結:最嚴重是主線判斷、側帳退路、`--disagreements` 缺第一盲判分支、`blind_agree` 摘要都改壞後測試仍綠,另有統計「採盲判」名稱不準,都屬只是覆蓋不全或不影響閘判定,會擋 0 條。

臨時目錄 `/tmp/lumos-seat-work/code-android情境題盲判/測試-sonnet` 已用字面絕對路徑刪除,repo 本體沒有被修改。
