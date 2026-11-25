severity: minor

hook 有附上固定席段(guard-kill、lumos-cli-read、bound-tests-gate 等十餘條 ★INVARIANT★ 或 ★RISK★ 節點)。

## 結論

這份修補沒有找到 major,也沒有會出錯的候選。只有 1 條文件措辭的 minor。八個角度的結果在後面。

## finding

severity: minor
blocking: 否(只是計劃筆記的標點與重複,照文件做不會做出錯的操作;判準屬於措辭)
file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md`(r3-repair.patch 第 85 行)
引句:「設計審 r1 邊界 F4;代碼審 r1 i5、b1、r2 e1;、正確性與通才:合併基準不乾淨時印字與記帳的原因要分開」
失敗場景:S10 預期值表「來源」欄多了一個「;、」殘字,語意也斷開。S10 條款的 `merge_off` 列舉(r3-repair.patch 第 67 行)連列兩次 `平台不穩或筆記未提交`,對應「平台 flaky」與「計劃筆記未提交」兩案,是刻意的,但讀者容易當成筆誤。
歸因:有證據的修復回歸。這兩處字樣都是本次修補新寫的,修前版本(95977c1)沒有。

## 八個角度

1. **逐行。** 修補 hunk 有三處:`_kill_merge_iter` 的 `except _KillHalt` 改成 `"中斷" if mg.interrupted else "時限到"`;新增模組常數 `_CHOICE_MERGE_TRIPPED`;新增一個測試案。
   - 我讀了整個 `_kill_merge_iter`、`_kill_merge_base`、`_kill_merge_singles`、`_KillHalt.between`、`_ChoiceKillRun.stop` 與 `_situation_rule_signals`。
   - `_KillHalt` 只有兩種來源:訊號,或 `stop()` 的 `st.got` 與總時限判斷。
   - 訊號路徑上,handler 先記 `st.got`,再呼叫 `on_first`(即 `mg.on_signal`,設 `mg.interrupted`),然後才回主流程。Python handler 在 bytecode 之間原子執行,所以 `_KillHalt` 被丟出時 `mg.interrupted` 已為真,分類正確。
   - 唯一的小空窗:時限先到、`_KillHalt` 已丟出、`except` 尚未求值時才來訊號,會記成「中斷」。結果仍是停,無害。
2. **被刪掉的行為。** 「中斷」從單一情況拆成「中斷」與「時限到」,字面「斷路器」換成常數。
   - 原本守住的是 `run.merge_off` 不得出現「斷路器」(它另有 `merge_tripped`)。新常數在 `scripts/lumos:29095` 寫入、`scripts/lumos:79113` 過濾,兩處同值,守衛仍在。
   - 全庫沒有其他地方用裸字串 `"斷路器"` 比對。
   - 「中斷」的案例由 `t_choice_kill_merge_interrupt`(test 第 146772 行,斷言 `merge_off == {"kotlin-junit": "中斷"}` 且不印「這次不合併(中斷)」)繼續守。
   - 斷路器那案由 `t_choice_kill_merge_unclean_reasons`(test 第 147585 行,斷言 `merge_off == {}`)守。
3. **跨檔追蹤。** `mg.interrupted` 的讀寫處只有 `scripts/lumos` 的 28204、28914、29006、29138、29169 五處,分類只動 29169 一處。
   - `_CHOICE_MERGE_TRIPPED` 的使用處只有 29095 與 79113,沒有漏改的地方。
   - 讀端 `_GOV_FIELD_TYPES` 與 `_gov_row` 沒被這次修補碰到,`merge_off` 仍是 dict,型別不變。
4. **重用。** 沒有發現。新測試案沿用既有的 `_ckm_repo`、`_ckm_inproc`、`_ckm_recipes` 與 `t_choice_kill_merge_edges` 的卡線寫法。
5. **簡化。** 沒有發現。
6. **效率。** 沒有發現。修補只加一次布林判斷。
7. **修的深度。** `_kill_merge_iter` 的 `except _KillHalt` 現在涵蓋訊號與時限到。
   - 同一個函式內,量完基準之後的 `c.hk.between()`(`scripts/lumos:29178`)不在 `try` 裡。那裡停下時平台已記為 `(True, "")`,不會誤記成不合併。這是修前就有的行為,也符合「合併有開」的語意,不算漏。
8. **慣例。** 全域 CLAUDE.md 與專案 CLAUDE.md 要求的行長、白話、測試綁定,我沒找到能逐字引用並指出違反行的地方,所以不報。

## 圖譜固定席判定

- **guard-kill 兩條 INVARIANT**(rc 優先序、`--json` 純度)不影響。修補只改 `merge_off` 的原因字串與一個常數,沒碰 `cmd_guard_kill` 的 rc 計算與 stdout。
- **lumos-cli-read、bound-tests-gate、design-loop、lumos-cli-lifecycle、測試假綠形態**不影響。修補沒動 search 濾網、固定席測試綁定、處置閘、re-inject 或還原翻紅釘。
- **測試假綠形態**那條還要求修 bug 的測試配「前置斷言證明現場成立」。新測試案有:先斷言 `mg.plats == {"kotlin-junit": (False, "時限到")}`、`mg.interrupted is False` 與標準錯誤不含「這次不合併」,才檢查 run 事件。
- pitfalls-code-loop 與 loop-convergence-recording 兩個 ★RISK★ 節點,沒有看到這次修補碰到它們宣稱的行為。

## 三問與證據

**問一:原問題的修復效果。**
- claim:量基準途中總時限用完時,記「時限到」,不再誤記「中斷」。
- input:基準每支睡 2 秒,`should_stop` 在 3 秒後回真。
- expected:`mg.plats == {"kotlin-junit": (False, "時限到")}`、`mg.interrupted` 為假、不印「這次不合併」、run 事件 `merge_off == {"kotlin-junit": "時限到"}` 且 `interrupted` 為假。
- case_source:`t_choice_kill_merge_off_reasons` 新增案(對應 r2-fix.json 的 repair 案例)。
- before:修前 `scripts/lumos` 一律記 `中斷`。我從 `git show 95977c1` 的 hunk 比對確認,沒有實跑修前版本,所以修前結果是靜態推得,未實跑。
- after:實跑 `python3.14 scripts/test_lumos.py -k t_choice_kill_merge_off_reasons`,17 passed、0 failed,新增兩條斷言都綠,耗時 32 秒。
- attribution:有證據的修復有效。

**問二:修補處的正常、錯誤與相鄰路徑。**
- claim:訊號路徑仍記「中斷」,斷路器仍記 `斷路器` 且不進 `merge_off`。
- case_source:`t_choice_kill_merge_interrupt`、`t_choice_kill_merge_unclean_reasons`(preserve 案例,我自選)。
- 我只靜態核對了這兩案的斷言(上面角度 2)。這兩支測試我這輪沒有實跑,結果未判定。
- 另外我追了 `on_first` 順序,確認訊號路徑會把 `mg.interrupted` 設好才讓 `_KillHalt` 被丟出。

**問三:新發現的同一案例在修前、修後。**
- 唯一的新發現是上面那條文件 minor,修前沒有,修後才有,歸因是修補。

## 未驗範圍

- 沒有實跑修前版本。
- 沒有對新常數與 `mg.interrupted` 分類做變異翻紅實驗。靜態上「中斷」與「時限到」各有斷言守,但沒實測拿掉其中一條判斷後測試會紅。
- 沒有跑 guard-kill 兩條 INVARIANT 綁的測試(`t_guard_kill_rc_precedence`、`t_guard_kill_json_purity`)。

總結:最高嚴重度 minor,blocking 0 條。
