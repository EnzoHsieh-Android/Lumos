severity: minor

我沒找到跨層直呼,也沒找到新引入的第二種做法。這輪的主題是把〈待決問題〉的正文解析整塊撤出,撤出乾淨。

我確認過的事:
- 在 b187b5e9 的 `scripts/lumos` 搜 `parse_pending_questions`、`pending_question_problems`、`_pq_decision_state`、`_pq_clause_tests`、`PQ_OPEN`、`PQ_STATUSES`、`pending_questions_blocking_gate`,全部 0 筆,沒有斷掉的呼叫。
- 用 python3.14 把 `scripts/lumos` 讀成語法樹,通過。
- `_h2_section_lines` 的 `nested` 參數已一併拿掉。剩下兩個呼叫端(`scripts/lumos` 的 `_ROLLBACK_H2_RE`、`_HAZARD_H2_RE` 兩處)都沒傳這個參數,沒有第二種找節邏輯。
- 規格閘前段、lint 的 `_lint_new_rules`、`cmd_pitfalls` 的 `--stage` 路徑,依賴方向跟撤出前一致,沒有新的跨層呼叫。
- 計劃筆記裡綁的三個測試名都存在:`t_backend_qo_question_section_not_parsed`、`t_backend_qo_stage_facets_only`、`t_stack_questions_kotlin_spring_triggers`,都在 `scripts/test_lumos.py`。
- 技能檔 `skills/lumos-project-notes/SKILL.md` 和 `reference.md` 都已改成「目前是給人看的清單,工具不讀」,跟程式一致。`Systems/情境出題.md` 裡「寫法照技能說明」指到的就是這段,引用沒有斷。
- 固定席的各條 ★INVARIANT★(bound-tests-gate、design-loop、guard-kill、lumos-cli-lifecycle、lumos-cli-read、授權與歸屬、測試假綠形態)談的是綁定測試閘、guard kill、re-inject、search 過濾、授權檔、還原翻紅釘。這輪的撤出沒有動到這些行為,判不影響。codex-harness 只牽連 `scenario_probe.py`,這輪沒改,也判不影響。

下面是兩條 minor 的發現。

severity: minor
blocking: 否
一、計劃筆記〈合約候選〉整節仍把已撤出的行為列為合約候選,跟同一篇的撤出橫幅和 S1 條款對不上。
引句:「規格閘遇到需求或架構階段、標阻塞、狀態待查或待人的題就回 1(S1)。」
說明:這句在 `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md` 的〈合約候選〉節。撤出後,規格閘不讀這一節,S1 說的是「不因它擋」,兩邊相反。這一節在後面,讀完前面的橫幅還可能照它蓋合約章。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:285`
歸因:有證據的修復回歸。
- 修前 46bc93c3:`git show 46bc93c3:<該筆記> | grep -c '規格閘遇到需求或架構階段、標阻塞'` 得 1。當時程式真的擋,這句是對的。
- 修後 b187b5e9:同一條指令也得 1,但程式已不擋。
- 這條筆記不在修補差異裡,所以是撤出之後沒跟著改。

severity: minor
blocking: 否
二、識別名 `PQ_STAGES` 留著「待決問題」的縮寫前綴,但它現在只管 `pitfalls --stage` 的階段值域。同一個檔裡跟它成對的 `PQ_STATUSES`、`PQ_OPEN` 都已拿掉,留一個孤兒前綴,下一個人會以為還有待決問題解析器。
引句:「PQ_STAGES = ("需求", "架構", "實作", "驗證", "效能", "交付")」
佐證:定義在 file: `scripts/lumos:6902`,用在 file: `scripts/lumos:42919`、file: `scripts/lumos:42920`。
說明:原本我只打算標這一條,是因為上面一行的註解已經說明用途,沒有造成實際誤導。命名只是跟鄰居不一致,屬於抑噪紀律裡「給不出具體失敗場景」的邊緣。改名成 `STAGES` 或 `_REQUIREMENT_STAGES` 即可,放在 `_REQUIREMENT_FACETS` 旁邊更貼近它的主要使用者。
歸因:有證據的修復回歸。
- 修前 46bc93c3:`git show 46bc93c3:scripts/lumos | grep -c PQ_STAGES` 得 7,且同檔有 `PQ_STATUSES` 等前綴同族(`grep -c 'PQ_STATUSES\|parse_pending_questions'` 得 10)。
- 修後 b187b5e9:`PQ_STAGES` 剩 3 處,`PQ_STATUSES`、`parse_pending_questions` 得 0。

我沒列的:撤出後的 `pitfalls --stage` 有自己的讀檔與錯誤輸出(file: `scripts/lumos:42893`),跟一般計劃模式的 `is_file()` 檢查(`scripts/lumos` 的 `cmd_pitfalls`)寫法不同。兩者的 rc2 語意一致,給不出會出錯的場景,所以不標。

總結:最嚴重 minor;blocking 共 0 條。
