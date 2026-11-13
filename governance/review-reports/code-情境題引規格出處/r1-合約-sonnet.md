severity: minor

## g1 計劃內部的範圍編號互相指錯(盲判捷徑擋被寫成範圍 5)
severity: minor
blocking: 否
引句:「答不適用的列由範圍 5 的盲判那道抓捷徑」
file: `docs/lumos-toolchain-knowledge/Projects/情境題答案要引規格出處與回寫循環_計劃.md:48`
1. 計劃的「範圍 5」是規格閘認人裁條款,盲判捷徑擋在「範圍 6」。〈實務隱患〉和〈天花板〉5 都正確寫成範圍 6,所以計劃自己前後不一致。
2. 同樣的錯在範圍 2。引句:「略過本案新增的所有出處擋(範圍 1 的內容核對、本條、範圍 5 的捷徑擋)」,位置在 `...計劃.md:51`。
3. 三個月後的接手者照範圍 2 去找「捷徑擋」,會翻到規格閘那一條,找不到。
4. 這份計劃是 doing 的活規格,盲判段(範圍 6)與〈實務隱患〉會拿它當準。

## 附:圖譜鏡頭
這次沒有附固定席節點(鏡頭計算超時),我只照派工詞判這份 diff 牽連到的節點。

- **Systems/棧別提問表態閘**:不影響它宣稱的合約。
  - 新增的 WHY、RULE、PITFALL 行都過了 `lumos lint`,0 問題;`[test:]` 指的測試都存在於 `scripts/test_lumos.py`。
  - 我逐條核對了那幾條 WHY:段放行蓋過出處三道擋、缺段缺列缺盲判照擋,和程式一致。這是看 `_kt_sit_spec_waived` 和 `_kt_bj_check` 的判斷點得出的,沒有跑反例。
  - 「段放行不給出口」「要重判只能等段材料變」兩句已改寫。留下的「缺段缺列照擋、不給放行出口」、「缺盲判不給段放行出口」兩句,對那兩種情形仍然成立,沒有互相矛盾。
  - `scripts/lumos:75364` 的訊息「要重判只能等段材料變了」是票面重判,和新寫的「票面要重判」一致。
- **Systems/規格閘**:不影響。
  - 新 WHY 描述的雜湊算法(`_clause_body_of(keep_code=True)`、NFC、sha256)和 `cmd_situation_rule` 寫帳的算法一致。
  - 程式有三處讀人裁條款:風險低靜態條件、跑完的放行判定、預期值表的新行為判定,筆記也是這三處。
  - 「不要求測試在計劃建立前就存在」也和程式註解一致。
- **Systems/guard-kill**:不影響。
  - `recipes_override`、`weak_why`、kill-log 的 `source: situation-rule`、`_backing_kill_rows` 跳過、`_kill_run` 遇 Ctrl-C 收程序群組,都在 `r1-code.patch` 找得到。
  - 筆記裡 `t_guard_kill_rc_precedence`、`t_guard_kill_json_purity` 沒被改動,所以那兩條合約的綁定測試沒被動到。
- **手冊與索引**
  - `skills/lumos-code-loop/SKILL.md`、`06-代碼審與推送.md`、`INDEX.md`、`reference.md`、`ARCHITECTURE.md` 的說法彼此一致。
  - `python3.14 scripts/lumos --help` 的頂層命令數實測是 100,和三處文件的「100」一致,`t_docs_enumeration_drift` 也通過。
  - 擋下訊息印的骨架、`situation-rule` 的旗標、next-step 提示裡的 `pitfalls --dispositions-template --carry` 和 `spec-gate`,我用 `--help` 和程式比對過,旗標都存在。
- **本案特定鏡頭**
  - 計劃 S1 到 S19 的 `[test:]` 全部在 `scripts/test_lumos.py` 裡有同名測試。`spec-gate --no-run` 顯示條款綁定 19/19、預期值表 26 列都通過。
  - `lands_in` 的三篇(棧別提問表態閘、規格閘、guard-kill)都寫回了計劃要求的內容。計劃範圍 8 要求的 `responsibility` 欄也補上了。
  - 我沒有跑 `situation-rule` 實際寫回,也沒跑 `t_kt_sit_spec_*` 以外的新測試,所以流程是否順暢只驗到說明文字與程式碼對得上。

最嚴重 severity:minor,blocking 共 0 條。
