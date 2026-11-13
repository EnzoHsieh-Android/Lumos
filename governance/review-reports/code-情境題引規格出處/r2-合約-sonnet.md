severity: clean

## 附:三問、圖譜鏡頭

**複驗結果**
- 我複驗了 `1d535b07b` 的計劃檔、三篇 Systems 筆記和 `scripts/lumos` 裡相關函式,沒找到會讓人照文件做出錯操作、讓測試或推送被擋、或跟合約衝突的地方。
- 沒有被這輪新規格推翻的舊說法。範圍 4 的 `|`、CRLF、`[S` 接數字、計劃路徑限制都跟程式一致。範圍 2、範圍 6 的編號、天花板 7 和 8、預期值表 S13 三列、審計修正紀錄也都對得上程式。

**命令與結果**
- `python3.14 scripts/lumos spec-gate 情境題答案要引規格出處與回寫循環_計劃 --no-run` 的結果:條款綁定 19 條全標、預期值表 27 列通過。
- `python3.14 scripts/lumos lint` 跑了計劃和 `Systems/棧別提問表態閘`、`Systems/規格閘`、`Systems/guard-kill` 三篇,都是 0 問題。
- `python3.14 scripts/test_lumos.py -k situation_rule` 得到 89 passed, 0 failed。
- `python3.14 scripts/test_lumos.py -k spec_gate_ruled` 得到 9 passed, 0 failed。
- `python3.14 scripts/lumos situation-rule --help` 的旗標跟計劃範圍 4 一致。

**①原問題的修復效果**
- 規格閘認人裁條款改成也比綁的測試。
  - 程式在 `scripts/lumos` 的 `_spec_gate_ruled_ids`,要求 `got[1] == {e["test_name"]}`,也就是綁的測試恰好是帳上那支。
  - `t_spec_gate_ruled_clause_as_keeps` 有換綁(⑥)和多綁(⑦)兩個案例,都被一般條款規則擋下。
  - 預期值表也跟著改了:`_expected_requirement` 先判門與生效日,過了才讀治理帳。
- 範圍 4 的 `|` 只擋反引號外。我實測了五種輸入:
  - `` `a|b` `` 放行。
  - `` `a` | b `` 擋下。
  - `[[Foo|bar]]` 在反引號外,擋下。
  - `` `items[S1]` `` 被 `[S` 接數字規則擋下,跟計劃寫的一致。
  - `_kt_sit_plan_clauses` 對 `` `a|b` `` 的條款正常讀出。
- 配方檔路徑從平台根所在 repo 的最上層算。`_situation_rule_platform` 用 `_kill_plat_top`,`t_situation_rule_recipe_id_subdir_platform` 守這一點。
- 計劃的 CRLF 拒絕、路徑解開後要在 `Projects/` 底下、同文同測試不重複插入,都有對應程式(`_situation_rule_read`、`_situation_rule_plan`、`_situation_rule_insert`)和測試。

**②修補處的正常與相鄰路徑**
- 殺傷力期間 SIGTERM、SIGHUP 轉成同 Ctrl-C 的收尾。
  - 進來前是忽略的訊號照留,離開時還原。
  - 這個處理器只包住 `cmd_guard_kill` 那一段,終端確認和寫入階段不在內,計劃檔對這一點的描述正確。
- `--keep-worktree` 保留的現場寫 `.lumos-keep`,清殘骸跳過。
  - 計劃天花板 8 說「超過一天、沒有保留標記的才清」,跟 `_isolated_worktree_sweep` 一致。
  - `_ISOLATED_WT_STALE_SEC` 沿用 lint-new 的值。
- 三篇 WHY 行都有 `[出處:]`、`[因:]`,`[test:]` 指的測試名都存在。

**③同一案例在修前與修後**
- 換綁(文字不變、`[test:]` 換成另一支綠的測試),修前會被當人裁條款放行,修後照一般條款判、綠就擋。依據是 S13 第三列和測試 ⑥。
- 反引號裡的 `|` 修前一律被拒,修後放行。
- 重跑同一條人裁(寫了計劃、帳沒記到),修前會多插一條重複條款,修後拒絕並指出已寫過哪一條。

**文件之間一致**
- `skills/lumos-code-loop/SKILL.md` 完全沒提 `situation-rule`,所以沒有因這輪修補過時。
- `skills/lumos-project-notes/commands/06-代碼審與推送.md` 第 16 行只講指令骨架、殺傷力、提交和重答,沒寫拒絕條件,也沒有過時。

**圖譜鏡頭**
- 派工詞說這次沒附固定席筆記,我只看到修補差異牽連的三篇 Systems 筆記,即 `Systems/棧別提問表態閘`、`Systems/規格閘`、`Systems/guard-kill`,這三篇的 WHY 行都跟程式現況一致。
- `Systems/代碼審修正關卡.md:55` 寫「修正關卡會在開頭清掉同前綴、超過一天的殘骸」。共用的 `_isolated_worktree_sweep` 現在會跳過有保留標記的資料夾,這句沒補這個例外。
- 因為清殘骸是按前綴找資料夾,修正關卡的前綴不會碰到 guard kill 的保留現場,所以我判定不影響實際行為。

severity: clean
blocking 共 0 條。
