severity: major

這次 hook 沒附圖譜固定席(鏡頭計算超時),所以沒有固定席可逐條判。Systems/guard-kill 的兩條 ★INVARIANT★ 我自己對照了,結果在 k4。

## k1 回報上限的抽法被「放行」打穿,放行抽中的行會讓沒抽中的存活全部變成必處置
severity: major
blocking: 是(文件宣稱的 S16 行為與程式不符,照文件走會一直被擋下)

壞在 `_choice_push_judge`。它在算「曾經存活過的行」集合 `ever` 之前,先把放行檔裡的行跳過(`if key in waived: continue`)。人用 `lint-waive choice:` 放行抽中的行後,`ever` 變小,種子隨之改變。當 `len(ever) <= cap` 時,`_choice_cap_pick` 直接全收。

計劃〈用詞〉回報上限寫的是「種子只看行指紋集合,所以提交帳本、rebase、型錄改動都不重抽;已處置的仍算處置」,S16 預期值也寫「沒抽到的 6 行仍不要求」。計劃〈範圍〉3 又把放行列為「換了一樣、不是需求」的主要出口。

最小重現(從 `/Users/enzo/harness/lumos-near-miss/scripts/lumos` 載入模組,20 行都曾存活,cap=14):

```
初抽中 14 未抽中 6
放行14行後:仍擋 6 未抽中 0
```

預期是放行 14 行後 6 行仍不要求,實際是 6 行全變成必處置。上限因此失效,而且是處置一批、下一批被擋的循環。

測試抓不住:`t_spec_gate_push_choice_cap` 只用 `killed` 事件處置,沒走放行路徑,所以照綠。

引句:「抽中的要有效處置,沒抽中的這個範圍內不要求。種子只看行指紋集合,所以提交帳本、rebase 改行號、型錄改動都不重抽;新的存活行出現時集合變了才重抽,已處置的仍算處置。」

file: `scripts/lumos:78123`(`_choice_push_judge`,`if key in waived: continue` 在 `ever.add` 之前)

## k2 文件說「提交放行檔不讓代碼審留痕失效」,實際會失效
severity: major
blocking: 是(照 SKILL 與計劃走會讓推送被擋)

`.lumos/lint-waivers.json` 不在 `_BOOKKEEPING_FILES`。我在暫存 repo 驗過:`code-loop pass` 記在 b,之後只提交放行檔,`_codeloop_record_valid` 回 `(False, '記錄 sha … 之後動了代碼(非純簿記增量)')`;之後只提交 `docs/.governance-log.jsonl` 才回 True。

計劃〈實務隱患〉把「choice-kill 只寫治理帳、lint-waive 只寫放行檔」都當成通過後可提交的帳本。lumos-code-loop 的 SKILL 寫「治理帳與放行檔要提交……之後只剩帳本提交,不讓留痕失效」。專案 CLAUDE.md 也規定通過後只准再提交帳本。順序若是 pass、然後 lint-waive、然後提交放行檔,留痕就作廢,要重審。

引句:「所以 situation-rule 會改計劃,所以 choice-kill 與處置在 `code-loop pass` 之前做;之後只有帳本提交(choice-kill 只寫治理帳、lint-waive 只寫放行檔)。」

引句:「④**治理帳與放行檔要提交**(推送閘只讀被推送版本的帳;之後只剩帳本提交,不讓留痕失效)。」

file: `scripts/lumos:40639`(`_BOOKKEEPING_FILES` 沒有放行檔),`scripts/lumos:74801`(`_codeloop_record_valid_ex`)

## k3 `stop_group_on_kill` 是不存在的名字
severity: minor
blocking: 否(文件措辭,未定義的詞,但沒有照做會出錯的路徑)

計劃〈實務隱患〉「同一壞法殺掉就停(`stop_group_on_kill`)」和〈回退〉「`source`、`stop_group_on_kill`、`on_row`」用了這個名字。程式、guard-kill 筆記和計劃自己的〈用詞〉與〈範圍〉2 都叫 `stop_group_on`。全 repo 只有這份計劃含 `stop_group_on_kill`,三個月後接手的人依〈回退〉去 grep 會找不到。

引句:「同一壞法殺掉就停(`stop_group_on_kill`);相關的測試排前面」

file: `scripts/lumos:28047`(簽名是 `stop_group_on`)

## k4 兩條 guard-kill 合約沒被破壞,但新選用參數沒有測試守著
severity: minor
blocking: 否(目前沒有具體的壞法會讓測試照綠且破壞合約)

兩條合約我都對過程式:

- **rc 優先序**:`cmd_guard_kill` 在算 rc 前先把 `skipped` 列濾掉(`verdicts = [... != "skipped"]`),survived、drifted/abort/error、全弱證據的判法沒動。
- **`--json` 純度**:JSON 輸出路徑沒變,`skipped` 只是 results 多一種 verdict。

`source` 非空就整個不寫殺傷力帳本,`_backing_kill_rows` 改成「`source` 非空就跳過」也沒動到合約文字。我找不到讓合約測試照綠、同時破壞合約的具體改壞,所以只記一條 minor。

引句:「略過的列不算進 `cmd_guard_kill` 自己的 rc(不改它的 rc 優先序)」

file: `scripts/lumos:28329`

## 第三段三處〈用詞〉改動與別處有沒有跟上

- **回報上限不算簿記檔與放行檔**:程式用 `_sc_changed_files` 加上排除 `_LINT_NEW_WAIVERS_REL`,簿記檔由 `_BOOKKEEPING_FILES` 排除,和文字一致,改得對。
- **抽法改洗牌取前段**:筆記與程式一致,改得對。只是放行路徑的集合縮小沒處理,見 k1。
- **生效日晚於今天整圈不跑**:`_choice_push_round` 先判 `since > today` 就 return,和〈用詞〉一致。`_choice_requirement` 的「沒碰到計劃看今天」分支同向,測試總檔預設 `9999-12-31` 也對得上,改得對。

其他我順手對過、沒發現不一致:`--push-remote/--pushed-ref` 的 dest 與掛鉤 grep 字樣、`choice-points` rc 3、`choice-kill` 預設值 30 與 1800、`_KNOWN_GATES` 與 `LOOP_NOT_CLOSE_EVENTS` 四個 kind、型錄 C-1 到 C-31 與規則檔都存在、`[test:]` 綁的 26 個測試名都存在。

最嚴重:major;blocking 共 2 條
