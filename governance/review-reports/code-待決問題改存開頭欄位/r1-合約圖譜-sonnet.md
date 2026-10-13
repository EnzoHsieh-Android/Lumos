severity: major

我是用 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/合約圖譜-sonnet/` 下的 `--shared` clone 驗的,沒碰 repo 根。先交代跑過的證據。
- `python3.14 scripts/test_lumos.py -k qfm` 結果是 100 passed, 0 failed。
- 另跑 `-k decision_`(91 passed)、`note_lint`(24 passed)、`command_index`、`every_subcommand_has_when`、`repo_graph_passes`,全綠。
- `lumos doctor` 結果是 0 issues,「宣稱/實測」漂移清單跟 a31b2043 比完全一樣。
- 原計劃 7 題搬遷:我用 `pq_parse` 讀新版,和 `git show a31b2043:` 的舊版逐鍵比對,id、text、class、stage、status、blocking、irreversible、decision、source、reason 全部一致。Q1 到 Q7 的順序也對。
- 決策連結 d5、d6、d8、d9 在 `Projects/後端工程提問與證據擴充_計劃.md` 都是 `valid: true`。
- 測試名 `t_qfm_*` 五支加 `t_qfm_absent_field_unchanged`,以及 `t_backend_qo_question_section_not_parsed`,都存在。

S1 到 S6 的行為我都實際跑過,和條款字面相符:
- 決策連結的 `.md` 全域形式能收,`#D1` 這種大寫、`#d06` 這種前導零會被擋。
- 在 `[]` 上加題能成功;BOM 檔寫入拒絕。
- lint 的行號是對的(第 25 行的錯誤確實在第 25 行)。

接手會撞牆的地方如下。

1. 過期的現況句沒清,三個月後的人會被誤導
severity: major
   - blocking: 是
   - 引句:「規格閘、lint 不讀正文這一節,`pitfalls --stage` 只列需求風險面 [出處:代碼審 code-後端情境出題 三輪 21 席、使用者裁先拆出]」
   - 〈要一起改的既有文字〉清單沒涵蓋下面這幾處,它們現在跟程式相反。
     - `Systems/情境出題.md` 的 WHY(diff 第 466 行)在現在式裡寫 `--stage` 只列需求風險面。`--stage` 現在會列題目。
     - `Systems/情境出題.md:6` 寫「改存開頭欄位另案」。`Systems/情境出題.md:26` 寫「改存開頭欄位另案」。這項已實作。
     - `Projects/後端工程提問與證據擴充_計劃.md:210` 的橫幅寫「現在規格閘與 lint 不讀正文…`pitfalls --stage` 只列需求風險面…在 [[…]] 重做」。
     - 同檔 `:195` 的 RETIRE-IF 寫「另案重做」。
     - 同檔 `:277` 寫「〈待決問題〉的檢查只讀計劃筆記、不寫共用檔,沒有並行寫入面」。現在 `question-add` 要寫檔,而且上鎖。
     - 同檔 `:283` 寫「擋法另案重做時再評守衛面」。
     - 同檔 `:260` 和 `:262` 的示範流程,仍叫人把題目手寫進〈待決問題〉。
   - 複現:`git grep -n "另案\|只列需求風險面" -- docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md docs/lumos-toolchain-knowledge/Systems/情境出題.md`。
   - 同一個檔的 d11 是有效決策,寫著「pitfalls --stage(只列需求風險面)」,只是範圍限定在那篇計劃。
   - 照 CLAUDE.md,這類 `decisions` 帶有挑戰程式碼的效力,和它前一輪 r4 修過的 d7 是同一型問題。這些殘句要改掉,或對 d10 補一條新決策、翻掉舊的。

2. 計劃自己的回頭條件沒結案
severity: minor
   - blocking: 否
   - 引句:「REVISIT:2027-01-31 這篇還是草案就決定:排進下一輪實作(先過 spec-gate),或撤案並在原計劃記一條決策」
   - 計劃已實作,白話段也寫「已實作」,但這行沒有 `[closed:…]`,2027-01-31 到期時 doctor 會唸一條不成立的話。
   - 同一份計劃的 status 還是 `doing`,可以一併確認。

3. 指向不存在的章節
severity: minor
   - blocking: 否
   - 引句:「開頭欄位版的擋法與合約候選在 [[Projects/待決問題改存開頭欄位_計劃]]」
   - 新計劃沒有〈合約候選〉這一節。`grep -n "合約\|INVARIANT"` 只命中同步清單和順手處理兩行。
   - 規格閘新增的擋法沒有任何合約或殺傷力配方。要嘛補〈合約候選〉並說不標的理由,要嘛把後端計劃那句指標改掉。

4. note_lint.gate 的 RULE 沒跟上第六條規則
severity: minor
   - blocking: 否
   - 引句:「`_lint_new_rules` 多一條 `_nl_rule_pending_questions`(擋不擋照 note_lint.gate)」
   - `Systems/lumos-cli-read.md:22` 的 RULE 還在有效期內(confirmed 2026-09-25),窮舉了「新規則」五條,沒有 `pending_questions`。
   - 本 repo 的 gate 是 `on`,所以手改壞開頭欄位會讓提交被擋。這點只寫在新增的小節,讀 RULE 的人看不到。
   - 圖譜鏡頭:`Systems/lumos-cli-write.md`、`Systems/pitfalls-code-loop.md` 的新增段落,與程式和測試名對得上,沒發現問題。

5. 推送前提醒會對整份被刪除或歸檔的計劃誤報「題號不見了」
severity: minor
   - blocking: 否
   - 引句:「那一版有、這一版不見了(題目不刪,改成延後或已決;真的要刪就在提交說明寫為什麼)」
   - 複現:在 clone 裡提交一份帶兩題的計劃,再 `git rm` 後執行 `spec-gate --push-check HEAD~1..HEAD`。
   - 輸出:`提醒:Projects/zz探針_計劃.md Q1 在 HEAD~1 那一版有、這一版不見了…`,Q2 也一樣。
   - 原因是 `_spec_gate_push_check` 的 `git diff --name-only` 包含被刪的檔。這只是提醒、不擋,所以不算 blocking。
   - ⚠ 三點範圍 `A...B` 時,程式拿 `A` 當基準而不是 merge-base,與計劃寫的「合併基準那一版」不符。我沒實測,只是讀程式的判斷。

6. 測試斷言偏弱,S2 說要驗的東西其實沒驗
severity: minor
   - blocking: 否
   - 引句:「"第 " in lt.stdout and " 行" in lt.stdout」
   - 條款 S2 要求「逐處報檔案行號與原因」,測試只看到有「第 」和「 行」這兩段字,既沒對實際行號,也沒對原因。
   - 變異實驗:把 `_pq_fm_of_text` 的 `return fm or [], 2` 改成 `7`,讓規格閘的行號全偏,再跑 `-k qfm_strict_parse`,結果 35 passed, 0 failed,沒有翻紅。
   - 讀實作:30 個壞例子大多同時違反多條規則(例如 tab 例子也缺 `text`),拿掉其中一條規則,同一個例子仍會被別條擋下。這違反〈實作測試品質〉第 4 點「別讓另一道守衛代打」。
   - `t_qfm_absent_field_unchanged` 是把 n0、n1、n2 三種寫法互相比,沒和改動前的輸出比。S6 說「跟現行相同」,這裡沒有獨立的預期值。
   - 這支測試的耗時也偏吃緊。單獨跑它 45.5s,跑 `-k qfm` 整組時是 107s,後者被套件標了「餘裕不足 3 倍」。它綁在 S2,而規格閘跑綁定測試的逾時上限是 180s。

7. 規格閘筆記的家與流程摘要沒更新
severity: minor
   - blocking: 否
   - 引句:「這篇管 `scripts/lumos` 裡的 `cmd_spec_gate`、`_clause_check`、`_clause_grammar`」
   - `Systems/規格閘.md` 的「管到的檔」沒列新函式 `_spec_gate_pending`、`_pq_push_remind`。
   - 同檔摘要的 FLOW 行還是「⓪門 ①句式 …風險高:只印、指路 loop next」,沒有新加的待決問題那一步,也沒說明風險高時這一步會回 1。
   - 本文新加的那一節有寫,所以只是摘要沒跟上。

8. 〈順手處理〉的 `PQ_STAGES` 改名項已不成立,卻沒結案
severity: minor
   - blocking: 否
   - 引句:「重做時改成不帶待決問題縮寫的名字(代碼審 r4 架構席)」
   - 程式保留了 `PQ_STAGES`,現在它真的是給 pending questions 用的,名字反而合適。
   - 條款 S5 的測試也直接引用 `lm.PQ_STAGES`。這個待辦要劃掉或寫明不改的理由,否則下個人會照它去改名而弄壞 S5。
   - ⚠ `_qo_plan` 的 decisions 參數那一項我沒逐一查證用到沒有。

總結:程式、測試和 7 題搬遷都照條款做到,gate 與 doctor 皆綠;唯一要擋的是第 1 條(過期現況句與有效決策仍寫「--stage 只列需求風險面」、「另案」),其餘 7 條為不擋的 minor。
