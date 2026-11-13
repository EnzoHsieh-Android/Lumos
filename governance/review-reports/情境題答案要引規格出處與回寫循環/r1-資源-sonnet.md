severity: major

**節點對照**:派工尾端附了 `Systems/規格閘`、`Systems/棧別提問表態閘`、`Systems/guard-kill`、`Systems/pitfalls-code-loop`。
- `規格閘` 與 `棧別提問表態閘` 各 0 條合約,這份設計沒有破壞它們宣稱的行為。
- `guard-kill` 有兩條 ★INVARIANT★:rc 優先序(`t_guard_kill_rc_precedence`)、`--json` 成功時 stdout 恰一行 JSON(`t_guard_kill_json_purity`)。
  - 本案是新指令 `situation-rule`,不直接動這兩條。
  - 但範圍 4 要把 `cmd_guard_kill` 內嵌的隔離與判定抽成共用函式。只要抽得不乾淨就會破壞這兩條,見 F7。
- `pitfalls-code-loop` 只附了名字,沒有宣稱可對照,判不影響:本案只加欄位與比對,不改它的 pitfalls 分級。

**實測(本機)**
- 指令:`python3.14 t.py`,用 `SourceFileLoader` 載入 `scripts/lumos`,呼叫 `m._drift_tree_env(root,"HEAD","docs/lumos-toolchain-knowledge")`。
- 輸出:`env 0.71 1037`,即 1037 篇筆記建圖 0.6–0.7 秒;`_spec_gate_push_candidates` 0.25–0.28 秒;`maxrss` 120–409 MB(兩次量測差很大,以上限計)。
- 時間與記憶體本身扛得住,問題在 F1、F5、F6。

---

**F1 「不讀工作目錄」的宣稱與 `_spec_gate_push_candidates` 的實作不符**
severity: major
- blocking: 是(守衛的核心前提不成立,會算錯名單)
- spec 段:〈用詞〉對應計劃名單
- 引句:「所以本案不讀工作目錄的圖譜:用 `_drift_tree_env` 從被推版本(`at_sha`)的樹建一份只在記憶體裡的圖譜」
- 問題:`_spec_gate_push_candidates` 在判斷 doing 計劃有沒有連到被改節點時,不用記憶體圖譜。
- 佐證:file: `scripts/lumos:16452-16470`。該函式迴圈裡直接 `(env.vault / prel).read_text(...)` 讀磁碟,`OSError` 時 `ptxt=""`。`Env.from_texts` 的註解(file: `scripts/lumos:979`)寫明「讀全文用 env_text,不要自己開檔——這種 Env 的檔不在磁碟上」。
- 後果:
  - 被推版本的計劃若不在目前工作目錄(別分支、未 checkout、剛 rebase),正文連結(`WIKILINK_RE`)讀不到或讀到別版,名單就算錯。
  - 它只靠 `lands_in`/`related`/DEP 還撐得住,正文連結這條路會悄悄漏掉,漏掉等於整條分支被判「找不到對應計劃」而全擋。
  - 反過來,工作目錄有未提交的連結會讓名單變大,違反「名單只認已提交」。
- 規格沒要求改這支函式讀 `env_text`,而範圍裡「本案不另寫一套找法」。必須補一條要求,並寫一條「工作目錄與被推版本不同」的先紅測試。

**F2 殺傷力驗證被 Ctrl-C 或逾時打斷,測試子程序與隔離工作樹會殘留**
severity: major
- blocking: 是(最壞時序下資源洩漏,且此專案已有過暫存累積的前科)
- spec 段:範圍 4 殺傷力驗證
- 引句:「guard kill 的隔離工作樹照 `HEAD` 建,有未提交改動時判定不可信」
- 問題:`_kill_run` 用 `start_new_session=True` 開子程序,但只在 `subprocess.TimeoutExpired` 時 `_kill_proc_group`。
- 佐證:file: `scripts/lumos:27500-27530`。`KeyboardInterrupt` 沒被接。Ctrl-C 只送前景程序群組,新 session 的 `gradle`/shell 繼續跑,然後 `_isolated_worktree` 的 finally 把它腳下的樹 `worktree remove --force`。
- 清殘骸:file: `scripts/lumos:27417-27475`。`sweep_repo` 預設 `None`,「guard kill 不清,行為不變」。本案說共用函式「行為不變」,就等於沿用不清殘骸。
- 逾時預算:baseline 用 `max(600, floor)`(file: `scripts/lumos:27755`),加壞法再一次,最壞約 20 分鐘。AI 在對話裡跑指令的上限多半是 10 分鐘,所以「被逾時打斷」是常態。
- 規格只說「指令印預估、在背景跑的提醒」,沒有:
  - 中斷時收程序群組;
  - 本案開 `sweep_repo`;
  - 逾時上限與 rc。
- 沒有任何一條驗收條款涵蓋中斷。

**F3 計劃檔與治理帳兩邊寫,沒有順序,也沒有冪等或補救**
severity: major
- blocking: 是(半途失敗後兩邊不一致,會導向錯誤訊息)
- spec 段:範圍 4 寫回與記帳
- 引句:「治理帳記一筆 `kind: situation-rule`:段身分、列、計劃、條款編號、條款文字、測試名、origin、consent 原文、殺傷力判定與配方身分。」
- 問題:先寫計劃再記帳,或先記帳再寫計劃,規格都沒定。
- 佐證:`_codeloop_gov_append` 會回 `(False, 原因)`(file: `scripts/lumos:73819`):沒有 `docs/` 或寫不進去就失敗。計劃已寫、帳沒記:
  - 範圍 2 的擋下訊息看帳。查不到人裁,就再印「人裁指令骨架」。
  - 使用者照做就在計劃再加一條重複條款 S(n+2),因為殺傷力驗證不會偵測重複。
  - 反過來(帳先記、計劃寫失敗),帳說有、計劃沒有,訊息叫作者「改填 `Projects/…#S9`」,但 S9 不存在,又被範圍 1 擋,形成死循環。
- 範圍 2 的「要改填的 `spec` 值」只來自帳,不核對計劃真的有那一條。
- 要補:
  - 規定順序,例如先寫計劃、再記帳;
  - 帳記失敗時回報計劃已寫、不要重跑;
  - 擋下訊息改查「計劃裡真的有那條」,並對同一段同一列的重複人裁定義取哪一筆。

**F4 條款編號在殺傷力驗證之前算,寫回時沒有「鎖內重讀重算」,兩個會談會拿到同號或互蓋**
severity: major
- blocking: 是(最壞時序,一人兩個會談是明列要考慮的情形)
- spec 段:範圍 4
- 引句:「配方身分用 `_kill_recipe_key(計劃節點, 條款編號, 檔, 原文)`(條款編號是寫回時會拿到的下一個號)。」
- 問題:編號在驗證前算(驗證要數分鐘),寫回時才「拿寫入鎖、整檔原子寫」。
- 佐證:
  - 規格沒寫鎖內重讀計劃、重算下一個號。
  - 兩個會談同時對同一份計劃走完驗證,都拿到 S(n+1)。後寫的若沿用先前讀到的全文,會覆蓋先寫的整條(丟更新);若重算則編號和配方身分不一致。
  - `_vault_write_lock` 最多等 60 秒(file: `scripts/lumos:30541`),所以鎖不能在殺傷力驗證期間持有,必須只包「重讀、重算、寫」。規格沒講。
- 另外,範圍 4 的「整檔原子寫」沒指名寫入函式。`atomic_write_verify`(file: `scripts/lumos:30452`)是寫開頭欄位用的,規格改的是正文條款與表格,需要另一支寫法。

**F5 建圖失敗、逾時時的行為沒定,守衛可能失敗放行**
severity: major
- blocking: 是(守衛面,失敗要擋而不是過)
- spec 段:〈用詞〉對應計劃名單與範圍 1 推送前核對
- 引句:「只在這次有情境段、而且有答「適用」的列時才建。本案不另寫一套找法。」
- 問題:`_drift_tree_env` 在 `git` 失敗時回 `None`。
- 佐證:
  - file: `scripts/lumos:57830-57858`。`_kt_sit_verdict_one` 對逾時的既有行為是 `over_budget` 並「回 None(過)」(file: `scripts/lumos:74292-74330`),預算 `_KT_SIT_BUDGET=30` 秒與切段共用。
  - 規格沒寫建圖 `None`、逾時、樹上讀不出計劃(`_note_unreadable`)時要擋還是放,也沒有對應驗收條款。
  - 照既有的 `over_budget` 慣例,「出處核對」會被當成沒核、悄悄放行,而這正是本案要防的。
- 還有 cache:既有 `cache` 在同一次核對內共用,但規格沒說把圖譜與名單存進去。
  - 每段每列各建一次,保守估 30 段約 20 秒,吃掉大半預算。
  - 同一次推送裡 `pitfalls`、`code-loop check`、推送前閘會各算一次。

**F6 `specs` 放盲判材料頂層,沒有上限,實測可到幾十萬字**
severity: major
- blocking: 是(材料大到盲判塞不下就等於無法盲判,而且分份時乘以份數)
- spec 段:範圍 5 材料
- 引句:「材料**頂層**放一次 `specs`(對應計劃名單裡每份計劃的條款編號與出處本文、預期值表列編號與出處本文)」
- 實測:對 `scripts/lumos` 這種被很多 doing 計劃連到的家,`_spec_gate_push_candidates` 回 177 份計劃,〈驗收條款〉節合計 193,396 字、1098 條 `[S`。這還沒算預期值表。
- 規格的對策只有「放頂層一次、份數變多是代價」。
- 問題:
  - 沒有上限,沒有「只帶作者引的那幾份加各段最相關的」之類的縮減。
  - 分份時每份都帶完整 `specs`,份數乘整份大小。
  - 盲判要是被撐爆,後續行為(不寫、整份拒)也沒定。
- 規格要定上限與超過時的做法(擋或截斷後標明),並給一支大輸入的測試。

**F7 殺傷力判定的 TOCTOU,以及抽共用函式的回歸**
severity: minor
- blocking: 否(窗口小;回歸風險靠既有綁定測試抓,但要寫進條款)
- spec 段:範圍 4
- 引句:「本案把「跑一條臨時配方、交回判定」抽成一支共用函式(先例:`kill-add --try` 的 `result_out` 參數),guard kill 改呼叫它、行為不變。」
- 問題:
  - 帳裡只記配方身分,沒記驗證時的 `HEAD` sha。驗證數分鐘期間別的會談提交或 rebase 了,綁定測試或 kill-file 變了,記下的「killed」對應的是另一版程式,事後無法分辨。
  - `cmd_guard_kill` 內嵌了弱證據蓋章(整套跑、flaky、修改時間沒錯開、筆記未提交)與 `unsure`/`mstate` 邏輯(file: `scripts/lumos:27700-27760`)。抽共用函式時漏帶任何一個,「只認沒有弱證據的 killed」就失守。驗收條款只有 S6、S7 兩條新指令的案例,沒有「`guard kill` 的 `--json` 純度與 rc 優先序不變」的回歸條款。要把 `t_guard_kill_rc_precedence`、`t_guard_kill_json_purity` 列為必跑。

**F8 `origin` 判定與生效日邊界各有一處沒定**
severity: minor
- blocking: 否(單人工具,有終端卻逾時的情形少見;日期邊界只差一天)
- spec 段:〈用詞〉人裁與生效日
- 問題:
  - `_waive_origin_tty` 在「有終端但逾時、沒回答」時回 `"ai"`(file: `scripts/lumos:41783`),與「沒有終端」同一類。規格只說「沒有互動終端」,有終端逾時算 `chat` 還是拒絕沒講。
  - 生效日比對 `written_at`(帶時區的微秒時間,file: `scripts/lumos:73815`)和一個日期常數,規格沒定用本機時區還是 UTC。實作提交當天的邊界可能把一筆新舊制判反。

**F9 寫入內容的最後一道清洗不夠**
severity: minor
- blocking: 否(威脅模型是單人、自家 AI;只會造成規格閘整份失敗,不會繞過守衛)
- spec 段:範圍 4 條款文字與預期值表列
- 引句:「`--consent` 原文寫進預期值表前把 `|` 換成 `／`、換行換成空格(不然整張表的格數會亂、規格閘整份失敗)。」
- 問題:`--consent` 原話前 40 字進表格第四格,只清了 `|` 和換行,沒清 `[S`、`[test:`、`[manual:` 等條款標記字樣。這些字樣出現在預期值表的任一格裡,是否被 `clause_bindings` 或別處當成標記,規格沒查。`--plan` 路徑也沒寫要限制在 vault 的 `Projects/` 之下。

---

**已讀無 finding 的節**
- 〈不做〉、〈回退〉:已讀,無 finding。
- 〈依據來源〉、PRIOR-ART、RETIRE-IF:已讀,無 finding。
- 〈天花板〉、REVISIT:已讀,無 finding。

**守衛面逐類**
- 失敗放行:有,F5(建圖失敗、逾時)。
- 半途失敗不一致:有,F3、F4。
- 資源與程序殘留:有,F2。
- 規模爆量:有,F6(材料)。圖譜記憶體 120–409 MB、建圖約 0.7 秒,無問題。
- 金流、對外送出、不可逆:無。規格已排除,而且本案只寫本機檔與治理帳。
- 併發寫治理帳:不在威脅模型內,不列。但同一人兩個會談改同一份計劃仍在範圍內,見 F4。

最嚴重 severity:major,blocking 共 5 條(F1、F2、F3、F4、F5、F6 為 major,其中 F6 與 F1 至 F5 一起算,共 6 條 blocking: 是;minor 3 條 blocking: 否)。

修正總結:最嚴重 major,blocking 共 6 條。
