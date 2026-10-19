severity: minor

整合席第 3 輪(合約與圖譜一致,文件那半修補)。我對 web-ledger 的 `scripts/lumos`(與 5248791e 完全相同)逐項核對了決策、筆記和程式行為,沒有 major,找到 4 條 minor。

**已驗證的主張**
- d1/d2/d3 的決策文字與程式一致:
  - none 保留字:`_none_reserved_lines` 擋 `--findings-set`、`--refuted-set` 的 id 叫 none,也擋其他清單把 none 跟別的 id 並列,不分大小寫。
  - 整串只寫 none 當空集合。`--regression-set` 只收 `code-` 開頭,且 none 的判法與折入、放行同一支。
  - 混用擋下三種「接下來」,以及帳壞訊息 `_round_format_bad_lines`,都和筆記、計劃一致。
  - 帳壞時,有人裁紀錄的迴圈照舊落 `cap-ledger-bad`,其他由輪次規則擋(`_cap_retro_record_block` 加 `_round_format_write_block`)。
- 結局帳在四個讀審查列的入口濾掉,程式裡確實是這四處:`_canary_ledger_scan`、`_loop_status_read`、`cmd_loop_replay`、`_spec_gate_ledger_index`。
- 子集測試全綠:`outcome_row` 18、`none_is_reserved` 5、`set_none` 5、`reads_ledger_once` 11、`hint_quotes` 4、`tail_without_newline` 1、`orchestrator_bad_ledger` 1、`regression_set` 15、`round_format` 15、`record_persist` 7、`canary_carrier_quote` 12。
- 相關四篇筆記的 `lumos lint` 都是 0 問題。

**Finding**

1. 說明文字還留著修前的 none 規則
   - 位置:`scripts/lumos` 的 `canary record --help`(約第 57733 行,`--folded-set` 的說明)。`--accepted-set` 說「規則同 --folded-set」,所以一起帶錯。
   - 問題:說明寫「一條都沒有寫 none(=空集合;--findings-set 真有叫 none 的 id 時照字面)」。這是 r2 之前的規則,d3 已改成保留字。
   - 例:照說明在 `--findings-set` 放一個叫 none 的 id,現在 rc2 並說 none 是保留字。
   - 歸因:有證據的原有漏查。修補的程式與文件差異都沒碰這行,`--help` 實際輸出可驗。
   - 引句:「一條都沒有寫 none(=空集合;--findings-set 真有叫 none 的 id 時照字面),none 不能跟其他 id 並列」
severity: minor
   - blocking: 否

2. 修補過的小節裡還有一句指向已刪除的函式
   - 位置:`Systems/loop-convergence-recording.md` 約第 205 行,與 `Projects/記帳與迴圈工具小修_計劃.md` 第 1 節約第 77 行。
   - 問題:兩處都寫「結局帳列不算(先過 `_review_rows`)」。`scripts/lumos` 已經沒有 `_review_rows`,`grep` 只剩 `_escape_review_rows_by_loop`。同一小節兩條之後才講真正的做法:`_is_outcome_row` 在讀帳入口濾。
   - 例:三個月後的人搜 `_review_rows` 找不到,會以為過濾邏輯不見了。
   - 歸因:有證據的修復回歸,是 r3 改文件時漏改這句。
   - 引句:「**結局帳列不算**(`_review_rows` 先濾掉;結局帳結構上不能帶輪次,原本照算會讓帶輪次的迴圈寫完結局帳就卡死——代碼審 r1 通才 1)」
severity: minor
   - blocking: 否

3. 審查帳寫入器補了帳尾換行,但兩處筆記還說沒補
   - 位置:`Issues/治理帳與審查帳其他讀寫函式的硬化缺口.md` 的第 ③ 項,與 `Systems/reversibility-governance-ledger.md` 的 PITFALL。
   - 問題:兩處都說 `_jsonl_append_verified` 沒接帳尾檢查,第 ③ 項還附了「審查帳檔尾留半行後 canary record 第一次回 2」的重現。這輪 `_jsonl_append_verified` 已呼叫 `_ledger_tail_needs_newline`,測試 `t_canary_record_tail_without_newline` 通過。
   - 例:接手的人照 Issue 再補一次帳尾換行,或照重現步驟找不到症狀。
   - 歸因:有證據的修復回歸,是這輪改程式後沒同步到這兩篇。
   - 引句:「`_jsonl_append_verified`(審查帳)直接 `open(path, "a")`,前兩支只接 `OSError`」
severity: minor
   - blocking: 否

4. 載體零引句計劃的 [S3] 說某個測試「改驗被擋」,但那個測試其實把 none 的案例拿掉了
   - 位置:`Projects/載體零引句在記帳前拒收_計劃.md` 的 [S3],綁測試 `t_canary_carrier_quote_positive_controls`(`scripts/test_lumos.py` 約第 30847 行)。
   - 問題:[S3] 寫「包括真實 ID none(2026-10-15 起改成保留字、這個案例改驗被擋)」。這支測試只剩 `F1` 和 `F1,F2` 兩組,斷言 none 被擋的在另一支 `t_canary_record_none_is_reserved_id`。測試 docstring 還寫「literal none 真實 ID……不可被新守衛誤擋」。
   - 例:把保留字擋刪掉,這支綁定測試照綠,[S3] 那半句沒有測試守。
   - 歸因:有證據的修復回歸。
   - 引句:「包括真實 ID none(2026-10-15 起改成保留字、這個案例改驗被擋)」
severity: minor
   - blocking: 否

**回答三問**
- 原問題的修復效果:結局帳在讀側不算混用、none 保留字、整本帳只讀一次、帳尾補換行、編號 quote 不截斷,這些在 `outcome_row`、`set_none` 等相關子集有行為證據,測試都過。
- 修補處的正常、錯誤與相鄰路徑:沒有發現讀程式或跑測試時會做出錯行為的缺口。剩下的都是文字與說明沒跟上(上面 4 條)。
- 同一案例修前修後:我沒有在修前版本(69ee6d76)重跑,上面 4 條都是修後文字與程式的對照,「回歸」二字是指這輪改程式或文件時沒同步,不是行為回歸。

**未驗範圍**
- 沒有在 `lumos` 修前版本上重跑任何案例。
- 沒有做拿掉過濾看測試會不會紅的破壞測試(那是測試鏡頭)。
- `_cap_retro_record_block` 的 `q = _esc_clean(_shlex.quote(loop_id), 200)` 仍截斷 200 字,與 S42「不截斷」的精神不同。需要超過 200 字的編號才會碰到,我沒有為它開 finding。

最嚴重 severity:minor,blocking 共 0 條。

我開的空臨時目錄已刪。
