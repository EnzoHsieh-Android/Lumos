severity: major

**1. 分層與依賴方向:不對齊,有兩處跨層(major)**

- 引句出處要用的「對應計劃名單」,計劃說重用規格閘的 `_spec_gate_push_candidates`,並用 `_drift_tree_env` 加 `Env.from_texts` 建一份記憶體圖譜餵它(對照 `scripts/lumos:57830`、`scripts/lumos:979`)。
  - 但這支函式讀計劃正文時是 `(env.vault / prel).read_text(...)`(`scripts/lumos:16467`),直接開磁碟上的工作目錄檔。`from_texts` 的 Env「檔不在磁碟上」(`scripts/lumos:979` 的 docstring)。
  - 結果是被推提交的樹對不上工作目錄:名單會依工作目錄的計劃正文算,或讀不到變成空字串。這正好違反計劃自己寫的「本案不讀工作目錄的圖譜」。
  - 專案的既有讀法是 `env_text(env, rel)`(`scripts/lumos:1034`,記憶體 Env 從記憶體拿)。同一支檔 `scripts/lumos:16643` 也有同樣的直接開檔。
  - 計劃沒提這支函式要改,範圍裡也沒列。

  引句:「用 `_drift_tree_env` 從被推版本(`at_sha`)的樹建一份只在記憶體裡的圖譜(`Env.from_texts`)交給 `_spec_gate_push_candidates`」

severity: major
  blocking: 是

- `situation-rule` 掛在 `code-loop` 底下,但它要拿筆記庫寫入鎖、改計劃正文、跑 guard kill 的臨時配方。
  - 鄰居 `blind-judge`、`dispositions`、`recall-miss` 都在 `cmd_code_loop` 裡(`scripts/lumos:75904`、`scripts/lumos:75939`)。這一層只解 repo 根、分支、版本,沒有 `env`,不載圖譜。派發在 `scripts/lumos:78585`。
  - 會寫計劃、拿 vault 鎖的指令是頂層、帶 `env` 的:`cmd_summary_add`(`scripts/lumos:30832`)、`cmd_guard_kill_add`(`scripts/lumos:26956`,鎖 `scripts/lumos:27000` 附近)、`_cmd_signoff_expected`(`scripts/lumos:17581`)。
  - `cmd_guard_kill(env, node, …)`(`scripts/lumos:27622`)也要 `env`。
  - 計劃沒講 `situation-rule` 在 code-loop 層怎麼取得 vault 的 `env`。要嘛改成頂層指令(像 `signoff`),要嘛明寫 code-loop 這層可以載圖譜,並說明和「vault-free」這條的關係。

  引句:「人裁指令 `lumos code-loop situation-rule --seg <段身分> --row D-<n> --plan Projects/<計劃名>」

severity: major
  blocking: 是

**2. 命名與錯誤處理:大致對齊,有兩處小不一致**

- 治理帳 kind `situation-rule` 對得上鄰居的連字號寫法(`blind-judge`、`recall-miss`,`scripts/lumos:74431`)。
- 寫帳走 `_codeloop_gov_append`(`scripts/lumos:73819`),拒絕時 rc 2 加「擋下:」開頭,也跟 `_cmd_codeloop_blind_judge`(`scripts/lumos:74793` 起)一致。
- 生效日常數加環境變數覆寫,寫法同 `_expected_since`(`scripts/lumos:14515`)和 `_plan_sources_since`(`scripts/lumos:14678`),對齊。
- 不對齊的有兩條:
  - 旗標名 `--kill-file`、`--kill-old`、`--kill-new`。鄰居 `kill-add` 的旗標是 `--file`、`--old`、`--new`、`--test`(`scripts/lumos:26956`)。
  - 殺傷力的采信標準不同:計劃只認「沒有弱證據的 `killed`」,而 `_kill_add_try` 刻意「不看 weak」(`scripts/lumos:27034` 起的 docstring)。計劃有講理由(寫回時是為了保證會紅),但沒對照 `--try` 的差別。

  引句:「--kill-file <檔> --kill-old "<原文>" --kill-new "<壞法>" [--consent "<使用者原話>"]」

severity: minor
  blocking: 否

**3. 第二種做法:不對齊,有兩處(major)**

- **origin 多一種 `chat`**。
  - 既有的人簽與 AI 簽判法只有 `human` 或 `ai` 兩值,沒有 `--consent` 這個概念。
    - `_waive_origin_tty` 回 human / ai / None(`scripts/lumos:41783`)。
    - `_cmd_signoff_expected` 記 origin 為 human 或 ai(`scripts/lumos:17581` 起,事件欄位在 `scripts/lumos:17615`)。
    - 放行檔 `_lint_waiver_ai_unacked` 只認 `origin == "ai"`(`scripts/lumos:41799`)。
    - 治理帳讀回的 `sit_waive` 預設 `human`(`scripts/lumos:18187`)。
    - `scripts/lumos` 全檔沒有 `consent` 一詞。
  - 計劃明說「既有的 `_waive_origin_tty` 沒有終端時記成 AI、照收,本案不沿用」,這是刻意的第二套判法。
  - 既有做法夠用的部分:沒終端時記 `ai`,另存一個 `consent` 欄就能區分,不必多一個 origin 值。
  - 計劃沒說明新值對 `gov --stats`、ack 流程、doctor 計數(`_lint_waivers_ai_pending`,`scripts/lumos:41805`)的影響。
  - 拒絕沒終端又沒 `--consent` 的行為,在既有指令裡沒有先例(都是照收記 ai)。

  引句:「紀錄的 `origin` 只有兩種值:`human`(有互動終端、看完答 y;這時就算也帶了 `--consent`,照記 human、consent 原文照存)、`chat`」

severity: major
  blocking: 是

- **另一套讀條款本文與預期值表列**。
  - 計劃明說不呼叫 `_clause_body_of`(`scripts/lumos:13902`),另寫「保留反引號的出處本文」。
  - 預期值表列不用 `_expected_table`(`scripts/lumos:14617`),另用 `_h2_section_lines` 加 `_expected_split_cells`(`scripts/lumos:14552`)取「四格、第一格 `S<n>`」的列。
  - 這是兩套會各自演化的解析器,和簽核流程看的「表」可能對不上哪一列算列。例如簽核時整張表因格式問題回 None,引用卻照樣取得到列。
  - 既有函式不夠用的理由是真的(整張回 None、剝反引號)。比較對齊的做法是在 `_clause_body_of` 與 `_expected_table` 旁加參數或共用的低階函式,而不是在別處另寫。

  引句:「讀列不用 `_expected_table`(它有任一格式問題就整張回 None),改用同一支找節函式 `_h2_section_lines` 取〈預期值表〉節」

severity: major
  blocking: 是

- **對齊的地方**:
  - 殺傷力把「跑臨時配方、交回判定」抽成共用函式,`guard kill` 改呼叫它。這跟 `kill-add --try` 用 `result_out` 的先例同一方向(`scripts/lumos:27623` 起的 docstring、`scripts/lumos:27854`),沒有第二套殺傷力。
  - 配方身分用 `_kill_recipe_key`(`scripts/lumos:26193`)。
  - 改計劃正文沒有既有的「追加驗收條款」函式可比對。我找過,只有 `_guard_plan_write_node`(`scripts/lumos:25231`)是寫節點。所以新增寫入函式本身不算第二種做法,前提是它用同一把 `_vault_write_lock`(`scripts/lumos:30541`)加 `atomic_write_verify`(`scripts/lumos:30452`)。計劃寫了「拿寫入鎖、整檔原子寫」,對齊。

**4. 落點:不能直接判合理,交編排者 ⚠**

- 現況數字:
  - `Systems/棧別提問表態閘` 196 行、管 3 支檔、沒寫負責範圍。
  - `Systems/規格閘` 185 行、管 `scripts/lumos`、有寫負責範圍。
  - 兩篇都以整支 `scripts/lumos` 為 `about_code`。
- 規格閘的 `responsibility`(`規格閘.md:6`)明列了「條款句式/綁定/回退節」、預期值表與 `signoff --expected` 的簽核寫入,所以「人裁寫回一條新驗收條款加預期值表一列」歸規格閘符合它的範圍。
- 盲判材料與作答、表態加 `spec` / `quote` 兩欄、`situation-rule` 的治理帳,都是表態閘的既有主題(`blind-judge` 已記在表態閘與 `pitfalls-code-loop`)。
- 殺傷力臨時配方的抽共用函式屬 `Systems/guard-kill`(119 行),計劃把它列在 `related`,但 `lands_in` 沒列。
- 兩個疑慮:
  - 表態閘沒有 `responsibility`,再灌入一整條「引規格出處、人裁、盲判看規格」,範圍會更模糊。建議先替它補負責範圍。
  - 殺傷力共用函式的說明該寫進 `Systems/guard-kill`。
- 沒有明確既有做法可判是否該另開一篇,所以標 ⚠,不硬判。

  引句:「lands_in:
  - Systems/棧別提問表態閘
  - Systems/規格閘」

severity: minor
  blocking: 否

不對齊共 6 條,其中 major 4 條是讀工作目錄的計劃正文、指令放在 code-loop 層卻要寫 vault、新增 chat origin、另一套條款與表列讀法;minor 2 條是旗標名與采信標準、落點。
