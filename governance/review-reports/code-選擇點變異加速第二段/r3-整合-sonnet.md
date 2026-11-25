severity: major

**hook 固定席段:有附上。** 附上的有 `Systems/guard-kill`、`lumos-cli-read`、`bound-tests-gate` 等節點,其餘列名。表態記錄的 py-* 五題都標 na。

## Findings

severity: major
blocking: 是(驗收條款 S10 的一句承諾,有能當場翻紅的改壞而測試照綠)
file: `scripts/test_lumos.py:147872`、`scripts/lumos:79091`
引句:「量基準途中總時限用完、沒收到訊號時 應 記 `時限到`、不印、run 的 `interrupted` 是假」
失敗場景:
- 新測試 `t_choice_kill_merge_off_reasons` 裡的 `check("r2 e1 run 的 merge_off {kotlin-junit: 時限到}、interrupted 假", …)` 沒有驗到真程式。
- 它的 `kr` 是手建的 `types.SimpleNamespace(..., interrupted=False, ...)`,再餵給 `_choice_kill_report`,所以 `got[0].get("interrupted") is False` 恆為真。
- 真正決定這個值的是 `_ChoiceKillRun.run` 的 `self.interrupted = bool(st.got)`。這支測試沒走過這一行。
- 重現:在複製的 repo(28543fb)把那行改成 `self.interrupted = bool(st.got or self.halted)`,也就是總時限到也算被中斷。跑 `python3.14 scripts/test_lumos.py -k choice_kill_merge`,結果 `205 passed, 0 failed`,沒有任何一支轉紅。
- 讀程式確認:修後版本總時限到時 `interrupted` 確實是假(`stop()` 只設 `halted`)。所以文件說的是對的,只是沒有測試守著。
歸因:有證據的修復回歸。這個「interrupted 假」的檢查是 r3 修補新加的。
- 修前版本沒有這條檢查,也沒有 `時限到` 這個原因。
- 修前版本的 `self.interrupted = bool(st.got)` 沒變。程式沒壞,是測試主張落空。
建議:不要手建 `kr`。改用真的 `_ChoiceKillRun` 跑到總時限到,再讀它的 `interrupted`。

severity: minor
blocking: 否(措辭錯字,照文件做不會出錯)
file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md` 預期值表 S10 列最後一格
引句:「設計審 r1 邊界 F4;代碼審 r1 i5、b1、r2 e1;、正確性與通才:合併基準不乾淨時印字與記帳的原因要分開」
失敗場景:
- 「e1;、正確性」多了一個頓號,是改寫時留下的殘字。
- 「來源」欄把兩份出處黏成一句,讀不出「正確性與通才」是接在哪一份審查後面。
歸因:有證據的修復回歸(r3 修補新改的那一格)。

## 逐項回答

**1. 計劃 [S1]–[S10] 與預期值表對測試斷言、程式輸出。**
- S7:計劃寫「單支 2 秒、守 3 支、剩 5.99 秒、已花 33 秒 → 約需 9 秒,剩 5 秒,--max-seconds 200」,表列另寫「照還沒量的 2 支估會是 6 秒、100」。`t_choice_kill_merge_budget_hint` 的斷言逐字吻合。t0 接線(12345.0 → 12405.0)也吻合。實跑 8 passed。
- S10:計劃條款列的 10 個原因,與測試迴圈 9 案加 2 個真跑案(合併道不足 2 支、對不到名字)的順序一致。兩個 `平台不穩或筆記未提交` 對 flaky 與筆記未提交。
- S10 表列「六案」是 python 指令、flaky、筆記未提交、`_secev_tq` 回 None、工作樹外 `-p`、aCase 兩次。數量與測試吻合。
- `時限到` 那案的 `merge_off`、不印「這次不合併」、`mg.interrupted is False` 都是真跑驗證。實跑 17 passed。
- 唯一斷不到的是上面那條 `run.interrupted` 假。

**2. 「中斷」「時限到」「斷路器」與常數名的一致性。**
- 程式:
  - `scripts/lumos:29169` 寫 `"中斷" if mg.interrupted else "時限到"`。
  - `_CHOICE_MERGE_TRIPPED` 只出現在定義、`_kill_merge_breaker` 與 `_choice_kill_report` 的過濾三處,沒有殘留的 `"斷路器"` 字面值。
- 計劃做法 3(第 78、79 行)、WHY(第 33 行)、`Systems/guard-kill`(WHY)、`Systems/規格閘`(第 98 行)、`_kill_merge_off`、`_kill_merge_iter` 的 docstring:都寫成「中斷=收到訊號、時限到=總時限用完、兩者只記不印」。
- 舊說法「中斷含總時限到」:沒有殘留。
- 小落差:計劃第 28 行摘要「合併沒開時每次都印一行講原因」沒帶例外。同一份第 33 行的 WHY 有寫例外,屬 minor,不另列 finding。

**3. 筆記行格式。**
- `lumos lint Projects/選擇點變異加速第二段_計劃` 和 `lint Systems/guard-kill`:都是 0 問題。
- 新改的 WHY 都有 `[出處:]`、`[因:]`,`[test:]` 指到的 8 支測試都存在(逐支數過,各 1 支)。
- 計劃已沒有 `n_mutants` 的殘留,只剩「拿掉它」的說明。

## 圖譜固定席逐條判

- `Systems/guard-kill`(INVARIANT:rc 優先序、`--json` 純度):不影響。r3 只改 `_kill_merge_iter` 記原因的字串與 `_choice_kill_report` 的過濾常數。`cmd_guard_kill` 的 rc 路徑與 `--json` 的輸出都沒碰。`on_row` 多的 `ran_solo` 欄位只是文件補寫,不會寫進 JSON。
- `lumos-cli-read`、`pitfalls-code-loop`、`loop-convergence-recording`、`bound-tests-gate`、`測試假綠形態`、`design-loop`、`lumos-cli-lifecycle`:不影響。diff 沒碰 search 濾網、帳本記錄、處置閘或 re-inject。
- `bound-tests-gate` 補充:這份 diff 新增的 `[test:]` 都指到存在的測試。懸空與偽證據都是 0。
- `測試假綠形態`(還原翻紅釘要配前置斷言):相關。上面的 major 就是這個形態。測試斷言恆真,沒有前置斷言證明被測路徑真的被執行到。

## 已驗主張證據

- claim:`時限到` 與 `中斷` 分開記。
  - input:訊號路徑與總時限路徑各一案。
  - expected:各記對應原因、都不印。
  - case_source:`scripts/test_lumos.py:146772`(中斷)、`147860`(時限到)。
  - before:修前一律記 `中斷`(`scripts/lumos` 舊碼)。
  - after:兩案各自吻合。
  - 歸因:有證據的修復效果。
- claim:S7、S10 的表列與條款和測試吻合。
  - 兩支測試實跑 8 passed、17 passed。
  - 未驗範圍:未實跑修前版本,只讀了修前碼。

臨時目錄 `/private/tmp/lumos-seat-work/code-選擇點變異加速第二段/整合-sonnet` 已刪。

總結:最高嚴重度 major,blocking 1 條。
