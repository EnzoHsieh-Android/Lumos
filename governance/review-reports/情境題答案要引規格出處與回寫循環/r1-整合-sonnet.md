severity: blocker

我照這份設計走了一遍完整循環(作者表態、盲判、未寫被擋、人裁寫回、重答、推送)。有兩處會永久卡死,另外有幾處手冊與程式現況已經對不上。

### 固定席節點判讀
- `Systems/guard-kill` 附了兩條 ★INVARIANT★:rc 優先序,以及 `--json` 成功時 stdout 恰一行 JSON。
  - 範圍 4 要把「跑臨時配方」抽成共用函式,再讓 `cmd_guard_kill` 改呼叫它。這條抽共用會動到兩條合約的綁定測試(`t_guard_kill_rc_precedence`、`t_guard_kill_json_purity`)。
  - 判「有風險,見 finding 8」。
- `pitfalls-code-loop`、`棧別提問表態閘`、`規格閘`:附到的內容裡沒有跟設計直接衝突的合約行,但手冊與筆記內文有衝突,見各 finding。

### 範圍 1 到 3(表態加欄位、未寫就擋、無計劃照擋)

**1. 未寫就擋沒有任何出口**
- 位置:〈範圍〉4 殺傷力驗證的最後一句,以及〈實務隱患〉「消費專案沒宣告測試平台」。
- 引句:「專案沒有宣告測試平台(`run_cmd`)時拒絕,訊息指出出口只剩既有的段放行(`lint-waive kt-situation:<段身分>`)。」
- 問題:設計說段放行是出口,但段放行解不開這個擋。
  - `_kt_sit_check` 的 `waived` 只略過證據提醒,docstring 寫明「缺段缺列照擋」。
  - `Systems/棧別提問表態閘` 的 WHY(`kt-situation` 段放行那條)寫「缺段缺列照擋、不給放行出口」,盲判那條寫「不給段放行出口」。
  - 所以消費專案第一次碰到,沒有 doing 計劃、沒有 `run_cmd` 的 `{method}` 時,任何答「適用」的列都推不出去。唯一的洞是環境變數 `LUMOS_KT_SIT_SPEC_SINCE`(`LUMOS_KT_SIT_SPEC_SINCE` 設遠未來日期,整套退回舊制),那是整道關掉,不是逐段出口。
  - RETIRE-IF ③ 拿「段放行次數」當繞過指標,也因此量不到真正的繞過。
- 佐證:file: `scripts/lumos:73721`(`_kt_sit_check` 的 `waived` 參數說明)與 `scripts/lumos:74295`(`_kt_sit_verdict_one` 的 docstring)。
severity: blocker
- blocking: 是。無出口的新擋下,第一個消費專案就卡死。

**2. 誠實答「適用」被擋,答「不適用」只被提醒**
- 位置:〈範圍〉1 的第二個要點,以及〈天花板〉5。
- 引句:「答「不適用」靠的是盲判獨立判一次(既有),盲判判適用、作者判不適用就照既有規則要仲裁。」
- 問題:新擋下只對答「適用」的列生效。作者把同一列改答 `applies:false` 就不用引出處。
  - 既有仲裁結果最多是 `_KT_BJ_MAJORITY` 或 `_KT_BJ_NO_MAJORITY`,兩者都只是提醒,不擋。
  - 結果是說謊的 AI 照樣推得出去,誠實的才被擋。
  - 天花板 5 只承認「兩位盲判都答不適用抓不到」,沒講到盲判判適用時也只是提醒。
- 佐證:file: `scripts/lumos:74519`(`_kt_bj_arbitrate`)與 `scripts/lumos:74543`(`_kt_bj_check`),盲判多數只進 `notes["majority"]` 不進 `probs`。
severity: blocker
- blocking: 是。閘的激勵反向,擋不住它要擋的情形。

**3. 表態形狀共用函式被規則包自檢引用,設計沒列**
- 位置:〈範圍〉1 的函式清單。
- 引句:「(`_kt_sit_template`、`_kt_sit_shape`、`_kt_sit_row_shape`、`_kt_sit_row_verdict`)」
- 問題:`_kt_sit_row_check` 是 `_kt_sit_row_verdict` 的薄包裝,被型錄自檢呼叫。
  - `_sit_first_pass` 組的答案是 `{"applies": True, "variant", "evidence"}`,沒有 `spec`。
  - 如果 `_kt_sit_row_shape` 對 `applies:true` 要求 spec 與 quote,自檢全部正例都會失敗。這會擋住型錄與規則包的自檢,連帶擋住安裝。
  - 舊紀錄(生效日前)讀回同一支形狀函式也會被拒。設計只說 `written_at` 傳給 `_kt_sit_verdict_one`,沒說傳進形狀檢查。
- 佐證:file: `configs/ast-grep/kotlin-android/check.py:693-702`(`_sit_first_pass` 呼叫 `_kt_sit_row_check`)與 `scripts/lumos:73643`(`_kt_sit_row_shape`)。
severity: major
- blocking: 是。漏掉第二個消費者,實作後自檢會紅。

**4. 對應計劃名單沿用的函式從磁碟讀計劃全文,不讀記憶體圖譜**
- 位置:〈用詞〉對應計劃名單。
- 引句:「用 `_drift_tree_env` 從被推版本(`at_sha`)的樹建一份只在記憶體裡的圖譜(`Env.from_texts`)交給 `_spec_gate_push_candidates`」
- 問題:`_spec_gate_push_candidates` 內部用 `(env.vault / prel).read_text(...)` 讀計劃正文。
  - `Env.from_texts` 的註解明說「讀全文用 env_text,不要自己開檔——這種 Env 的檔不在磁碟上」。
  - 在這個圖上,讀不到就變空字串,正文連結全丟。讀得到時讀的是工作目錄那版,不是被推版本。
  - 「只認已提交進範圍的內容」和「不另寫一套找法」兩句互相衝突,必須改共用函式,而規格閘推送前也呼叫它。
  - 設計也沒講 `touched` 怎麼算、名單算不出來(淺 clone、git 失敗、逾時)時是擋還是放。
- 佐證:file: `scripts/lumos:16461-16464`(`_spec_gate_push_candidates`)與 `scripts/lumos:979`(`from_texts` 說明)。
severity: major
- blocking: 是。名單可能錯,而整個閘依賴名單。

### 範圍 4(人裁寫回)與回寫循環

**5. 盲判紀錄每格第一筆永遠算數,重答後的出處比對走不通**
- 位置:〈範圍〉4 最後一點(印出接下來要做的事),以及〈範圍〉5 的出處比對。
- 引句:「印出接下來要做的事:提交計劃;重答那一列的 `spec` 值;這份計劃的規格閘留痕(條款雜湊變了)與預期值表簽核(表指紋變了)要重跑;改了計劃會讓已過的代碼審留痕失效。」
- 問題:循環的後半段沒有講盲判怎麼重判。
  - `_kt_bj_cells_add` 規定「每格只認第一筆」,`blind-judge` 整份都是已有的格時不寫、回 2。
  - `lumos-code-loop/SKILL.md` 與表態閘 PITFALL 都寫「重判的唯一路徑是段材料變了」。人裁寫回後段材料不變,只有 `specs` 變。
  - 情境:第一盲判在條款存在前答了「適用、未寫」,人裁寫回新條款,作者重答引新條款。
    - 這時最多還有一次仲裁機會能附和作者的新出處。
    - 仲裁用過一次的格,或第二輪人裁,就永遠沒有盲判附和,範圍 5 的「作者出處沒人附和就擋」變成永久擋。擋下訊息又印「人裁指令骨架」,但人裁其實已經做過。
  - 設計也沒更新仲裁挑格的 `_kt_bj_pick_rows`。它只挑票面不同的格,出處不同的格不會被挑進 `--disagreements` 材料。
  - 計劃提交會讓作者表態紀錄失效(見 finding 6),所以重答是強制的,但設計只把它當一步講。
- 佐證:file: `scripts/lumos:74461`(`_kt_bj_cells_add`)、`scripts/lumos:74630`(`_kt_bj_pick_rows`);`/Users/enzo/.claude/skills/lumos-code-loop/SKILL.md` 第 26 行「要重判只能等段材料變」。
severity: blocker
- blocking: 是。完整循環在最後一步走不通。

**6. 提交計劃會讓作者表態紀錄失效,設計沒講,順序也沒排**
- 位置:〈範圍〉3 的「寫回後**先提交**」,以及〈範圍〉4 最後一點。
- 引句:「寫回後**先提交**,那份計劃因為在範圍裡被改到才成為對應計劃」
- 問題:`docs/*-knowledge/Projects/*.md` 不在簿記白名單(`_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS`)。
  - 提交後 `_codeloop_record_valid` 判「記錄 sha 之後動了代碼」,作者表態紀錄失效。設計只講到代碼審留痕失效。
  - 另有兩個情況:(a) CLAUDE.md 規定推前壓成一個提交,壓提交又使 sha 不是祖先;(b) 人裁指令改計劃、寫治理帳,殺傷力又要求「工作目錄沒有未提交改動」,中間的提交順序沒寫出來。
  - 「工作目錄沒有未提交改動」若按字面是全樹,而 `docs/.governance-log.jsonl` 在表態與盲判後必然已改(目前狀態就是 `M`),人裁永遠過不了。要寫明只查 `--kill-file` 與測試檔兩支。
  - 計劃檔本身有未提交改動時,`cmd_guard_kill` 的 `node_dirty` 會把結果標弱證據,設計也沒把計劃檔列進「要已提交」的清單。
- 佐證:file: `scripts/lumos:40071-40092`(簿記白名單)、`scripts/lumos:74031`(`_codeloop_record_valid_ex`)、`scripts/lumos:27685`(`node_dirty`)。
severity: major
- blocking: 是。字面照做會在循環中卡住。

**7. 寫回的條款是綠測試,風險低計劃的規格閘會擋;預期值表簽核和表節的條件也沒處理**
- 位置:〈範圍〉4 寫回步驟。
- 引句:「在〈驗收條款〉節最後一條之後加 `- [S<下一個號>] <條款文字> [test:<測試名>]`」
- 問題一,風險低計劃:規格閘規定沒標 `[keeps]` 的條款,其綁定測試必須先紅;標 `[keeps]` 的測試必須在計劃第一次進 git 之前就存在。
  - 人裁的殺傷力流程要求 baseline 綠,測試是在計劃之後才寫的,兩條路都走不通。
  - 設計只寫「規格閘留痕要重跑」。對風險低、狀態 doing 的計劃會得到 `✗ 綠——沒標 keeps 的是新行為,測試現在就該紅`,推送前的 `--push-check` 則會因指紋過期而擋。
  - 風險高的計劃只印不擋,所以只有部分計劃卡住。
- 問題二,預期值表:`_expected_requirement` 在門判風險高且有新行為條款時要求預期值表節與簽核。
  - 設計只寫「有預期值表節時」加一列。計劃原本只有 `[keeps]` 條款、沒有表節時,加條款後就缺表。
  - 寫入的列 `輸入` 格是「段的檔:起訖行」,不是輸入,語意是湊格數,簽核人看不懂。
  - 簽核走 `_waive_origin_tty`,沒終端會記成 AI 簽,等於沒人看。
- 佐證:file: `scripts/lumos:15107-15160`(`_spec_gate_twoway_static`、`_spec_gate_twoway_run_verdict`)與 `scripts/lumos:14540-14545`(`_expected_requirement`)。
severity: blocker
- blocking: 是。風險低計劃上走不完循環。

**8. 抽共用 guard kill 與程式內「不要抽共用」的明文衝突**
- 位置:〈範圍〉4 殺傷力驗證。
- 引句:「本案把「跑一條臨時配方、交回判定」抽成一支共用函式(先例:`kill-add --try` 的 `result_out` 參數),guard kill 改呼叫它、行為不變。」
- 問題:`scripts/lumos:26216` 的註解明寫「★判法逐項對齊 cmd_guard_kill,但不改它的判法★(…抽共用會改到它的行為…)」,並用 `t_kill_recipe_check_matches_guard_kill` 守住,設計沒提這支測試。
  - `result_out` 先例只是「交回結果」,不是「吃臨時配方」。`cmd_guard_kill` 讀配方是從筆記檔 `_kill_read_recipes(path)`,分組、寫 kill-log、背書蓋章都綁節點。
  - 設計沒說臨時配方跑完寫不寫 `.kill-log.jsonl`、`node_dirty` 以哪個節點算(計劃?)。這影響兩條 ★INVARIANT★ 的綁定測試。
- 佐證:file: `scripts/lumos:26216-26222`、`scripts/lumos:27622`、`scripts/lumos:27854`。
severity: major
- blocking: 是。「行為不變」沒有保證,合約綁定測試有風險。

**9. 殺傷力只證明「這個檔被改壞會紅」,不證明改的是情境寫法**
- 位置:〈範圍〉4 殺傷力驗證。
- 引句:「`--kill-file` 要是這一段所在的檔」
- 問題:`--kill-old` 不需要落在該段的行範圍內,`--kill-new` 也不需要是型錄的另一寫法。
  - 命令列給任何會讓任一測試紅的壞法都過。
  - 〈範圍〉2「當場證明把寫法換成另一個,這支測試會紅」在機器上沒有對應檢查。
  - 天花板 3 只承認「不證斷言驗需求那一點」,沒承認連「改的是這一段」都沒驗。
  - `--consent` 沒有長度、唯一性限制,同一句原話可重複用在每一列。
- 佐證:file: `scripts/lumos:27622`(`cmd_guard_kill` 的配方欄位只有 file/old/new/test,無段範圍檢查)。
severity: major
- blocking: 是。核心保證只有字面,沒有機械守衛。

### 範圍 5(盲判看規格)與手冊

**10. 新增的擋下建在模型判斷上,違背同篇筆記先前的裁定理由**
- 位置:〈範圍〉5 比對第一點,以及「舊否決比對」的第 3 筆。
- 引句:「出處要有人附和:作者的 `spec` 至少要有一位判適用的盲判(第一盲判或仲裁)填了一樣的值,才算出處成立。」
- 問題:表態閘 WHY(盲判核對那條)否決「多數判作者沒照做就擋」,理由是「盲判是模型判斷、各列誤判率要靠提醒帳逐列量」,結論「先 Comment 不 Block」,升擋條件是真陽性至少 20、誤報少於一成。
  - 設計的舊否決比對第 3 筆說「本案不改那條,只新增」,但理由完全適用。
  - 兩個模型都得填對同一個條款編號才放行,沒有量過誤報就直接擋。
  - 對抗 finding 2:誠實答「適用」有此負擔,不適用則無。
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:66` 的 WHY 與 `:64` 的 REVISIT:2027-01-08。
severity: major
- blocking: 是。設計沒有回答自己引用的舊否決理由。

**11. 手冊與筆記沒有跟著改,而且有現成的矛盾說法**
- 位置:〈範圍〉全章,沒有「文件更新」項。
- 問題:下列說法會讓接手的人照舊做法操作:
  - `/Users/enzo/.claude/skills/lumos-code-loop/SKILL.md` 第 26 行:盲判四步、「要重判只能等段材料變」、「確定寫對就用 `lint-waive`」,都沒有 spec 與人裁。
  - `/Users/enzo/.claude/skills/lumos-project-notes/commands/06-代碼審與推送.md` 第 15 行:`blind-judge` 描述沒有 `specs` 欄或人裁。
  - `Systems/棧別提問表態閘.md` 第 62、66、69 行:段放行不給出口、盲判不給出口、重判要等材料變。
  - `scripts/lumos:73666` 的 docstring 還寫「誤擋要人裁的出口是段放行」,與同檔實作矛盾,設計順著這句寫。
  - `lands_in` 列了 `Systems/規格閘`,但設計沒有說明要在規格閘筆記寫什麼。
  - 治理帳事件登記:新增 `kind: situation-rule` 需要歸入 `LOOP_NOT_CLOSE_EVENTS`(`scripts/lumos:20519`)並登記 `_GOV_FIELD_TYPES`(`scripts/lumos:18080`)。設計只講「記一筆」,沒講 `gate` 名稱與歸類,不歸類 `t_loop_close_kinds_classified` 會紅。
severity: minor
- blocking: 否。單看是文件與登記工作,實作時會被測試逼出來。

**12. 內部不一致,以及條款和預期值表的缺口**
- 位置:〈範圍〉5 第一點,以及驗收條款 S4、S10。
- 引句:「材料**頂層**放一次 `specs`(對應計劃名單裡每份計劃的條款編號與出處本文、預期值表列編號與出處本文),各段不重複帶;不放作者的答案(作者選的 `spec`、`quote`)、不放人裁紀錄。」
- 問題:
  - 預期值表列裡有「人裁 <日期> <origin>:「<原話前 40 字>」」,放進 `specs` 就是放了人裁紀錄,與同一句「不放人裁紀錄」矛盾。
  - S4 的條款寫「樣板 應 印出」,測試名卻是 `t_kt_sit_spec_no_plan_blocks`,測的是擋,不是印。
  - 範圍 3 的「無計劃」、範圍 6 統計、人裁的 `|` 轉換、`_clause_grammar` 拒絕、缺節拒絕、`--carry` 都沒有對應條款。
  - 預期值表 S1 第二列「`未寫` 時引句必空」與 〈用詞〉一致,但沒有「第一列 `spec` 格式合法、`quote` 4 字」的獨立案例判別是哪一道擋。
  - 「`#預期<k>` 從 1 起算」和「只取四格、第一格是 `S<n>` 的列」,兩個口徑沒講錯格列算不算。
  - 人裁寫入的 `--test` 沒處理多平台的「平台:名字」寫法,也沒用 `clause_bindings` 驗寫入後條款狀態為 bound。
  - 有終端但逾時的情形,`_waive_origin_tty` 回「ai」,設計只有 human、chat 兩種 origin。
severity: minor
- blocking: 否。多為補條款或口徑,不影響主線設計成立。

### 逐節補述

- 前置白話、PRIOR-ART、RETIRE-IF:已讀,無 finding。八週算到 2027-01-08 與 REVISIT 對得上。引用網址我沒有逐一開。
- 〈不做〉:已讀,無 finding。
- 〈回退〉:已讀,無 finding。
- 〈依據來源〉:已讀,無 finding。
- 交叉引用:related 的三份計劃與 `Systems/pitfalls-code-loop` 都存在。`_clause_grammar`、`clause_bindings`、`_kill_recipe_key`、`_h2_section_lines`、`_expected_split_cells`、`_plan_sources_since` 都存在,簽名吻合。`_KT_SIT_SPEC_SINCE` 還不存在,屬於待新增。

### 風險類答覆:守衛面

- **守衛繞過**:有。finding 2(答不適用就繞過)、finding 9(任意壞法過殺傷力)、`LUMOS_KT_SIT_SPEC_SINCE` 環境變數可整套退回舊制,三處都是繞過口。
- **守衛誤擋**:有。finding 1、5、7 是新擋下沒有出口,finding 3 會擋住規則包自檢。
- **合約破壞**:有風險。finding 8,抽共用 guard kill 可能動到兩條 ★INVARIANT★ 的綁定測試。
- **性能**:無。我在 `_drift_tree_env` 實測 1037 篇、14MB 的圖譜,載入約 0.75 秒,在表態預算內。
- **併發**:寫計劃拿寫入鎖,沿用既有做法,沒有新增隱患。

severity 總結:最嚴重為 blocker;blocking 共 10 條(finding 1、2、3、4、5、6、7、8、9、10),minor 共 2 條(finding 11、12)。
