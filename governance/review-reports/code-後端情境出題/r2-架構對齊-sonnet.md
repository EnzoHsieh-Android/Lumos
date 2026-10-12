severity: major

**對照範圍**:甲、乙兩份修補差異逐行讀過,並以 112ad15f 的 `scripts/lumos`、`scripts/scenario_probe.py` 為準對照鄰居。

**修補裡做對的收斂(不列為問題)**
- `_nl_rule_pending_questions` 把自寫的 `_env_note_text` 改用既有的 `env_text`,自寫那份已刪。對照:file: `scripts/lumos:761`
- 圍欄判定走全檔唯一的 `_visible_lines`。對照:file: `scripts/lumos:4898`
- 測試名正規化走 `slot_parse` 加 `_test_names_of`,跟條款綁定同一套。對照:file: `scripts/lumos:32915`
- 條款定義行走 `_strip_inline_markup` 加 `_CLAUSE_LEAD_RE`,與條款綁定同一套。
- 回答上限改成參數一路傳到執行場次,不再改寫模組全域值。這收掉了 r1 的第二種做法。對照:file: `scripts/scenario_probe.py:1022`、`scripts/scenario_probe.py:1291`
- 計分器拿掉 `run` 子命令,不再有第二套逐場執行器。
- `item_pairs` 抽成 `agree` 與 `final` 共用。

**finding 1:〈待決問題〉找節的迴圈是第三套,專案明文禁止**

severity: major
blocking: 是

位置:`scripts/lumos` 的 `_pq_sections`(約 6928 行),修補新寫的 `_PQ_HEAD_RE`、`_PQ_ANY_HEAD_RE`、`_pq_sections`。

專案已有共用的「找節」函式 `_h2_section_lines(text, h2_re)`。它的 docstring 寫明「回退節與實務隱患節共用……找節邏輯不准長出第三套」。對照:file: `scripts/lumos:7166`、`scripts/lumos:7289`

`_pq_sections` 另外自己做了一次:自己的標題正規式、自己的層級判斷、自己的結束條件。它只共用了 `_visible_lines`,節的界線邏輯是第二套。

兩套行為不同,是會被使用者撞到的:
- `_h2_section_lines` 只在遇到 `## ` 或 `# ` 時結束。
- `_pq_sections` 在同級或更淺的標題結束。

引句:「+def _pq_sections(lines):」

最小重現(在 112ad15f 的 `scripts/lumos` 上對同一段文字各跑一次,輸出實測):
```
t = "# x\n### 待決問題\n- [Q1] a [類:需求][階段:需求][狀態:待人]\n### 別節\n- [Q2] b 不是題\n"
pq: [3]
h2: [3, 5]
```
同一份計劃裡,`### 別節` 底下的內容,被 `_h2_section_lines` 算進去,被 `_pq_sections` 排除。專案裡的找節結果因此不一致。

建議:讓 `_h2_section_lines` 接受層級參數,或讓它回傳多節;〈待決問題〉改用它。若認定這一節必須例外(任意層級、多節),要把理由寫進 `_h2_section_lines` 的 docstring,並明講為什麼那條「不准第三套」的規則在這裡不適用。

歸因:有證據的原有漏查。
- 查證命令:`git show c960f6de:scripts/lumos` 的 `parse_pending_questions`。
- 結果:修前已有自己的 `for k in range(start + 1, len(lines))` 加 `re.match(r"^#{1,2}\s", ln)` 找節迴圈,沒用 `_h2_section_lines`。
- 修後:112ad15f 的 `_pq_sections` 把這個自寫迴圈擴大成通用版,沒有收斂到共用函式。

**逐條回答三問(其餘部分)**
- ① 分層與依賴方向:`parse_pending_questions` 只吃文字,不讀圖譜。查決策與測試名的檢查只在 lint 一側,規格閘只看狀態。`pending_question_problems` 以參數注入 `decision_state` 與 `clause_tests`。這跟既有「解析函式不碰 env」的做法一致,無跨層直呼。
- ② 命名與錯誤處理:新函式用 `_pq_` 前綴,跟鄰居 `_nl_rule_*`、`_spec_gate_*` 同風格。`_pitfalls_stage` 讀檔的錯誤訊息改成「擋下:…」並回 2,與同檔其他讀不動的路徑一致。`except (OSError, UnicodeDecodeError)` 對齊 `env_text`:file: `scripts/lumos:761`。
- ③ 第二種做法:除 finding 1 之外,未發現。`_pq_decision_state` 沿用既有的 `parse_decisions`,本次修補沒動。

**圖譜鏡頭:固定席節點逐條判斷**
- codex-harness:不影響。`scenario_probe.py` 只改回答上限的傳遞方式與 `grade` 對 `expect` 的容錯,不碰 Codex 判定邏輯。
- lumos-cli-read(search 預設排除 superseded):不影響。本次沒碰 `search`。
- bound-tests-gate:不影響。`t_qo_ablation_scorer_suite` 與 `t_scenario_probe_collect_only_and_answer_cap` 是新測試入口,不改閘的行為。
- design-loop(處置閘第五步):不影響。
- guard-kill(rc 優先序、`--json` 純度):不影響。
- lumos-cli-lifecycle(re-inject):不影響。
- 授權與歸屬:不影響。新檔 `qo_ablation.py` 與 `scenario_probe.py` 都不在複製清單,`scripts/lumos` 的 SPDX 檔頭沒動。
- 測試假綠形態(還原翻紅釘須配前置斷言):影響但已符合。新測試 `t_backend_qo_parser_robust` 的 ③ 先確認 `qs` 有解出來才比對;`test_answer_max_flows_as_argument_not_global` 同時比對預設值與傳參值。
- pitfalls-code-loop、arch-alignment-lens 等「只列名」的節點:未逐篇讀,不判。

總結:最嚴重 major;blocking 共 1 條。
