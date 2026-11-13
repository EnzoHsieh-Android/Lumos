severity: major

圖譜節點判讀:派工尾端附到的節點中,只有 guard-kill 帶了內容(兩條 INVARIANT)。
- **guard-kill 的兩條 INVARIANT:不影響。** 一條是 rc 優先序,一條是 `--json` 成功時 stdout 恰一行 JSON。範圍 4 說「抽成共用函式、行為不變」,所以不改 rc 與輸出契約。前提是抽取後兩支綁定測試仍綠(`t_guard_kill_rc_precedence`、`t_guard_kill_json_purity`);見 finding 10 對抽取風險的說明。
- **棧別提問表態閘、規格閘、pitfalls-code-loop:沒附到內容,只有連結。** 無法逐條判,以下 finding 直接對照程式碼。

## 已讀無 finding 的節
- frontmatter(related 三篇 Projects、四篇 Systems 都存在)
- 〈回退〉
- 〈天花板〉第 1、3、4 點
- 〈依據來源〉表
- 〈不做〉
- 〈用詞〉的「宣告式壞法」「出處」兩條,除下列已點的處

---

**Finding 1**(範圍 4 最後一點、〈用詞〉人裁、RETIRE-IF ③)
severity: major
blocking: 是——不改,實作者會做出一個沒有出口的守衛:沒宣告測試平台或 `run_cmd` 沒有 `{method}` 的消費專案,情境段答「適用」的列永遠推不過。
- spec 段:引句:「專案沒有宣告測試平台(`run_cmd`)時拒絕,訊息指出出口只剩既有的段放行」
- 問題:輸入是消費專案沒有 `run_cmd`,或只能整套跑,拿不到無弱證據的 killed。人裁被拒後,spec 說出口是 `lint-waive kt-situation:<段身分>`。但現行段放行只關閉證據提醒與多數決提醒,擋下類(缺段、缺列、形狀不對)照擋。新的「未寫就擋」「出處沒人附和就擋」不在 spec 說的放行範圍內。spec 沒要求放行要略過新擋,所以 `lint-waive` 不是出口。RETIRE-IF ③(放行數超過人裁數兩倍)也因此量不到有意義的東西。
- 佐證:
  - file: `scripts/lumos:73721`。`_kt_sit_check` 的 docstring 寫 waived 只略過那段的證據提醒,缺段缺列照擋。
  - file: `scripts/lumos:41778`。放行說明文字寫「只關掉這段的證據提醒,缺段缺列照擋」。
  - file: `scripts/lumos:74319`。`waived` 只送進 `_kt_bj_check` 的 majority 提醒分支。

**Finding 2**(範圍 5 比對、S8、S9)
severity: major
blocking: 是——不改,「出處不同、票面相同」的列永遠派不出仲裁,推送卡死。
- spec 段:引句:「第一盲判判適用而且出處跟作者不同(含一邊是 `未寫`)→ 要仲裁;票面相同也要」
- 問題:spec 只列了 `_kt_bj_check`、`_kt_bj_arbitrate` 要改。但派仲裁材料靠 `lumos code-loop blind-judge --template --disagreements`。它走 `_kt_bj_pick_rows`,該函式在 `_kt_bj_author_vote(ans) == _kt_bj_blind_vote(first)` 時直接略過那列。作者與第一盲判都判「適用且照做」、只有出處不同時,這列不會進仲裁材料,`code-loop check` 卻要求仲裁。
- 另外:`_kt_bj_arbitrate(av, fv, rv)` 只吃票面三元組,出處判定要另開入口。`_kt_bj_validate` 的 arbiter 路徑、`_cmd_codeloop_bj_template` 讀 `author_rows` 的段也要連動。spec 範圍 5 的函式清單漏了這些。
- 佐證:file: `scripts/lumos:74631`(`_kt_bj_pick_rows`)、`scripts/lumos:74519`、`scripts/lumos:74738`。

**Finding 3**(〈用詞〉對應計劃名單)
severity: major
blocking: 是——「只認已提交進範圍的內容、不讀工作目錄」這個承諾,照 spec 指定的重用方式做不到。
- spec 段:引句:「用 `_drift_tree_env` 從被推版本(`at_sha`)的樹建一份只在記憶體裡的圖譜(`Env.from_texts`)交給 `_spec_gate_push_candidates`」
- 問題:`_spec_gate_push_candidates` 內部判 doing 計劃的正文連結時,用 `(env.vault / prel).read_text(...)` 直接讀磁碟,不是 `env_text(env, rel)`。`Env.from_texts` 的 docstring 明寫「讀全文用 env_text,不要自己開檔——這種 Env 的檔不在磁碟上」。
- 輸入:推 `HEAD:別名`、推舊 sha、或工作目錄的計劃比 `at_sha` 新或舊。
- 後果:正文連結改由工作目錄版本決定,讀不到時是 `""`。名單因此漏掉或多出計劃。spec 又寫「本案不另寫一套找法」,實作者要嘛違背 spec、要嘛改共用函式,而推送閘也在用它。
- 佐證:file: `scripts/lumos:16452`、`scripts/lumos:1034`(`env_text`)、`scripts/lumos:979`(`from_texts`)。

**Finding 4**(〈用詞〉對應計劃名單、範圍 1「推送前核對」)
severity: major
blocking: 是——失敗語意不明,守衛可能在最重的一步靜默放行。
- spec 沒定義 `_drift_tree_env` 回 None(git 失敗)、`_drift_vault_rel` 回 None(被推版本沒有圖譜)、deadline 逾時時,核對要擋還是放。
- 現行 `_kt_sit_verdict_one` 對逾時走 `over_budget`,回 None 即放行;對算不出來則擋(「無法驗證…擋下」)。兩套慣例相反。
- 新增的重步驟是列整個圖譜的所有 .md 並逐篇 cat-file,最容易逾時。照 over_budget 慣例實作,大圖譜上「引不到規格」就被放過。照無法驗證慣例實作,則消費專案沒有圖譜時整條分支被擋,而 spec 說的出口(Finding 1)不通。
- 佐證:file: `scripts/lumos:57830`(`_drift_tree_env` 回 None 的路徑)、`scripts/lumos:74292`(over_budget 回 None)。

**Finding 5**(範圍 4 條款文字、寫回)
severity: major
blocking: 是——寫回可能產出規格閘自己會拒的計劃,而 spec 沒要求寫回後自驗。
- spec 段:引句:「條款文字:不准有 `[S`、`[test:`、`[manual:`、`|`、換行」
- 問題 a,條款含單一反引號:禁字清單不含奇數個反引號。我實跑 `clause_bindings`,`- [S1] 當有 `x 時,系統 應 回 [test:t_a]` 的狀態是 untagged、refs 為空,因為未閉合反引號之後不信,尾端 `[test:…]` 被吞掉。寫回後該計劃的規格閘 FAIL。
- 問題 b,「下一個號」未定義:現有編號有缺號、重複定義、只在散文提到的 `[S9]` 時,取最大值加 1 還是填缺號,spec 沒講。
- 問題 c,插入位置與標題:「〈驗收條款〉節最後一條之後」未定義。程式碼裡沒有現成的驗收條款節標題 regex,要新寫。末條有續行或節內沒有任何條款定義行時,插入位置沒有定義。
- 問題 d,沒有自驗:寫回前沒要求對最終那一行跑 `clause_bindings` 與 `_clause_grammar`,也沒要求確認綁定狀態是 bound。`--test` 名在測試索引裡找不到時,kill 可能因 baseline 非綠而拒絕,但名稱解析與綁定判定走不同路徑。
- 佐證:file: `scripts/lumos:15702`(`clause_bindings` 的「未閉合反引號之後不信」)、`scripts/lumos:13945`(`_h2_section_lines`)。

**Finding 6**(〈用詞〉引句、範圍 1 形狀)
severity: major
blocking: 是——「至少 10 個字」可以用空白湊滿,引句核對在最極端輸入下失效。
- spec 段:引句:「至少 10 個字。比對前兩邊都做同樣兩步:轉 NFC、連續空白收成一個空格」
- 問題:字數看的是未正規化的原字串,比對看的是正規化後的字串。引句填 10 個全形空白,形狀通過(10 字),正規化成單一空格,出處本文只要有一個空白就逐字命中。標點串、`---` 這類湊字數也同理。
- 佐證:`re.sub(r"\s+", " ", "　"*10) == " "`(我跑過)。file: `scripts/lumos:14098`。`_real_chars` 已是專案計「實字」的現成算法,spec 沒指名用它。

**Finding 7**(〈用詞〉出處、預期值表列編號)
severity: minor
blocking: 否——對應的計劃壞了規格閘本來就會擋,這裡只是編號對不齊的小坑。
- spec 段:引句:「改用同一支找節函式 `_h2_section_lines` 取〈預期值表〉節、`_expected_split_cells` 拆格,只取「四格、而且第一格是 `S<n>`」的列編號」
- 問題 1:格內 `|` 沒跳脫的列變 5 格,被靜默排除出編號。作者數的 k 與現有 `_expected_table` 的資料列序(`rows[2:]`)錯位。
- 問題 2:節出現兩次或節內有第二張表時,沒說取哪張。現有 `_expected_table_lines` 取第一段相連表格,spec 沒指名要用它。
- 問題 3:`clause_bindings` 掃全文,「〈驗收條款〉的第 n 條」與全文定義行不同。同編號重複定義時 spec 取哪一行沒講,state 為 duplicate 的條款能被引用。
- 佐證:file: `scripts/lumos:14552`、`scripts/lumos:14620`(`_expected_table`)。

**Finding 8**(〈用詞〉生效日、S11)
severity: minor
blocking: 否——判準:邊界日附近會多擋幾次或漏擋幾次,實作者補一個決定即可。
- spec 段:引句:「判的是**作者表態事件**的 `written_at`:早於生效日的表態與它對應的盲判照舊制核對」
- 問題 a,缺值:事件沒有 `written_at`(舊事件或欄位缺)時怎麼判沒定義。當舊制會讓刪欄位繞過,當新制會擋舊事件。
- 問題 b,下傳:`_kt_sit_shape`、`_kt_sit_row_shape`、`_kt_sit_row_verdict` 是寫側與讀側共用,也被 `_kt_sit_row_check` 供型錄自檢正反例用。這些都沒有 `written_at` 參數。spec 只說傳到 `_kt_sit_verdict_one`。若預設走新制,型錄自檢的既有正例會翻紅。
- 問題 c,混舊制與新制:作者在生效日後寫、盲判在生效日前寫時,舊盲判沒有 `spec` 欄,會被當成「出處不同」而要求仲裁。
- 佐證:file: `scripts/lumos:72163`、`scripts/lumos:73682`、`scripts/lumos:73815`。

**Finding 9**(範圍 5 作答、S12)
severity: minor
blocking: 否——判準:舊版 lumos 讀不了新帳是已知的版本不一致,spec 沒講但不會讓實作做錯。
- 問題:`_kt_bj_vote_ok` 用 `set(v) - _KT_BJ_ROW_KEYS`,多出的鍵整票判不合。帶 `spec`/`quote` 的盲判事件寫進治理帳後,CI 或隊友機器上裝的舊版 lumos 讀回會整筆消失,報「缺第一盲判」。spec 只說白名單四處一起加,沒提版本差、沒給升級順序或讀端容忍策略。
- 佐證:file: `scripts/lumos:74441`。

**Finding 10**(範圍 4 殺傷力驗證)
severity: minor
blocking: 否——判準:實作時補決定即可,不致做出壞系統。
- 問題 a,弱證據:`cmd_guard_kill` 的弱證據旗標含 `node_dirty`(筆記工作樹有未提交改動)。臨時配方沒有筆記節點,`node_dirty` 該對誰算(計劃檔?)沒定義。
- 問題 b,版本不一致:kill 的隔離工作樹用目前 HEAD 建,段身分與段材料算在 `at_sha`。兩者不同時(推舊 sha、`HEAD:別名`),`--kill-old` 在 HEAD 版檔案裡恰好出現一次,不保證是那一段。
- 問題 c,留痕:kill-log 會以計劃節點與 recipe_id 落一筆,該配方並不存在於任何筆記的 kill_recipes。下游怎麼看待這種孤兒紀錄,spec 沒有查。
- 佐證:file: `scripts/lumos:27622`(`cmd_guard_kill`)。

**Finding 11**(範圍 4 指令列、範圍 2 訊息)
severity: minor
blocking: 否——判準:實作者補參數與取捨規則即可。
- 問題 a,定位:`situation-rule` 沒有 `--branch` 或範圍參數,「段身分要在這次範圍算得出來」的範圍從哪來沒講。其他 code-loop 指令都帶 `--branch`。
- 問題 b,查找:範圍 2 的「看治理帳有沒有這一段這一列的人裁紀錄」,同段同列多筆、跨分支、紀錄指向已被改號或刪除的條款時取哪筆沒定義。
- 問題 c,tty 模式:「看完答 y」沒說畫面上要顯示條款全文、kill 判定、目標計劃。條款是作者 AI 起草、再回頭被盲判讀到,確認的是什麼就得講清楚。
- 問題 d,計劃名:`Projects/<計劃名>#S<n>` 的剖析規則沒定義。名字含 `#`、空白、括號時怎麼切?是否須 NFC?是否含 `.md`?

**Finding 12**(驗收條款、預期值表覆蓋)
severity: minor
blocking: 否——判準:缺的是測試條款,不是行為決定。
- 問題:persona 點名的邊界,多數沒有條款或預期值列:consent 跳脫(`|`、換行→`／`、空白)、`_clause_grammar` 拒絕、缺〈驗收條款〉節拒絕、未提交拒絕、無 `run_cmd` 拒絕、名單空時的人裁路徑、兩盲判都判不適用、分份帶完整 specs、統計四個數。
- 這些是守衛的主要反例,沒有條款綁測試,實作者最容易漏。

---

## 守衛面風險類逐項
- **fail-open:有。** Finding 4。
- **繞過:有。** Finding 1,放行不是出口;Finding 6,空白湊字數。
- **偽造:無新增。** 對話核可的 AI 偽造已由〈天花板〉第 2 點明文收窄。
- **自證循環:⚠。** 條款文字、`kill-new` 壞法、測試名都由同一個作者 AI 挑,工具驗的是「這個壞法會讓這支測試紅」。〈天花板〉第 3 點承認,我判不準這是否足以守住使用者要的「測試守住需求」,留給人裁。
- **提示注入:無。** 盲判材料附的是倉庫內計劃文字,單人自用、威脅模型明文不防作者自注入。

最嚴重 severity: major;blocking: 是共 6 條(Finding 1、2、3、4、5、6)。
