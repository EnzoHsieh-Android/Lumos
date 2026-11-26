severity: major

我讀完整份 diff,並對照 repo 內的程式、計劃與 `commands/06`。合約與圖譜大致對得上。新 kind 的讀寫端、`_GOV_FIELD_TYPES`、`LOOP_NOT_CLOSE_EVENTS`、argparse 與說明表都有同步。bound-tests 與測試我沒有另外跑。有兩處不一致:

severity: major
blocking: 是
`scripts/lumos:79181` 的 `_choice_kill_pick` 新分支:依覆蓋判的存活(via cov)帶過去時,不看守的測試雜湊有沒有帶 `_CHOICE_TESTS_UNKNOWN`。
引句:「            if cov_sha_of is not None and evs[-1].get("cov_sha") == cov_sha_of(x):」
- 失敗場景:守的測試所在檔查不到,或查檔逾時。`_choice_tests_sha` 的尾端會帶不明標記,`cov_sha` 又算進這個雜湊,兩次都是同一個字串。於是測試檔內容改了,`cov_sha` 照樣相等,被判成「帶過去、不重跑」。
- 既有規則(`_choice_kill_pick` 的說明寫「守的測試雜湊帶 _CHOICE_TESTS_UNKNOWN → 當成變了,survived 也重跑(只多跑不漏;r2 H1)」)只在 via run 那條擋得住。
- `choice-points` 的 `_choice_reach_valid` 同樣把這種 reach 當有效,印「未判讀」而不是「未分類」。
- 最小重現(我已跑過,`python3.14` 載入 `scripts/lumos`,用 `_choice_kill_pick` 比較兩種事件):`ts="h"+m._CHOICE_TESTS_UNKNOWN`,兩筆事件的 `tests_sha` 都是 `ts`(cov 那筆前面加 `cov:`),`cov_sha_of=lambda _x:"abc"`。
  - via run:`todo=1, carried={}`,會重跑。
  - via cov(`cov_sha` 也是 `abc`):`todo=0, carried={('a.kt','f'): 'survived'}`,不重跑。
- 測試 `t_choice_cov_carry` 沒蓋到不明標記。

severity: minor
blocking: 否
`scripts/lumos` 的 `_ChoiceKillRun.reach_done` 讓依覆蓋判的存活進了 `stats["survived"]`,也就進了 run 那筆的 `ran`。但 `judged` 計數(`merged`、`single`)沒有加這些列。
引句:「run 那筆多 merged、single(相加等於這次判定數)」
- 失敗場景:開覆蓋且有行被直接記存活時,`merged + single` 小於 `ran`。`Systems/規格閘` 那條 WHY 與程式註解「merged + single = 這次判定的壞法數」都不再成立。
- 該條 WHY 與 `_choice_event_extra` 的說明也還寫 `judged` 只有 merged 或 single,新值 `cov` 沒補。
- 讀帳判斷合併省了多少的人會被誤導。

固定席逐條判定(`lens.txt` 列的節點):
- `Systems/guard-kill`:兩條 ★INVARIANT★ 不受影響。rc 優先序(survived→1、drifted/abort/error→2)與 `--json` 純淨都沒動:`prep` 只在 `cmd_guard_kill` 迴圈前換 `plist`,途中印的字都走 stderr,`prep_only` 只是 `continue`。
- `Systems/lumos-cli-read`:`search` 的篩選沒動,不影響。
- `Systems/bound-tests-gate`:新程式沒碰這道閘的挑測試與跑測試路徑。上面兩條 guard-kill 合約綁的測試還需要它跑一次。
- `Systems/lumos-cli-lifecycle`:re-inject 沒動,不影響。
- `Systems/測試假綠形態`:這份改動沒有修 bug 用的還原釘,不影響。
- `Systems/design-loop`:處置閘沒動,不影響。
- `Systems/pitfalls-code-loop`、`Systems/loop-convergence-recording`:新 kind `reach`、`reach-run` 已登記進 `LOOP_NOT_CLOSE_EVENTS`,不影響。

總結:最高等級是 major(1 條 major、1 條 minor)
