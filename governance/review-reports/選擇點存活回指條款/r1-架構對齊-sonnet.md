severity: major

## 1. 分層與依賴方向:對齊
- 覆蓋階段掛在 choice-kill 裡,自己用 `_isolated_worktree`(`scripts/lumos:28095`)從 HEAD 另建一棵樹。它不呼叫也不改 `cmd_guard_kill`,這點跟 choice-kill 現況一致(`cmd_choice_kill`,`scripts/lumos:79361`)。
- 中斷處理沿用 `_situation_rule_signals`(`scripts/lumos:77313`)。
- 結果檔大小上限沿用 `_CHOICE_MERGE_FILE_MAX`(`scripts/lumos:28763`)。
- 讀帳、輸出、推送閘提示都走 `_choice_points_lines`(`scripts/lumos:78662`)、`_choice_disposition`(`scripts/lumos:78800`)和 `_choice_push_round`(`scripts/lumos:79699`)。
- 計劃要求讀者先篩 kind,這點對應 `_choice_disposition` 只看同鍵最新一筆的做法。
- 我沒看到跨層直呼。

## 2. 命名與錯誤處理:大致對齊,有兩處小差異
- 對齊的部分:
  - `--no-reach` 對應既有的 `--no-merge`。
  - `choice-layer` 跟 `choice-kill`、`choice-points` 同一個命名家族。
  - 材料與記錄的形狀照 `code-loop blind-judge --template`,拒收一律 rc2(`scripts/lumos:76866`)。
  - 閘名照 choice-kill,`token` 欄位自帶,跟 `scripts/lumos:18552` 一致。
  - 「同鍵取最新一筆」跟 `_choice_disposition` 一致。它跟 blind-judge「每格只認第一筆」不同,但計劃已明寫這個差異。
- 不對齊 1:`coverage.run` 的 `{tests}` 展開成含字面 `--tests` 的整串。既有 `run_cmd` 的 `{method}` 前面要自己寫 `--tests`(`_choice_merge_shape`,`scripts/lumos:28783`)。同一份設定檔裡兩個佔位符的語意不同。
- 不對齊 2:新增的 `kind: "reach"` 和 `kind: "layer"` 沒有登記進治理帳的 (gate, kind) 白名單。`scripts/lumos:21047-21054` 現在只列 choice-kill 的 choice-kill、run、blocked、unverified。計劃只提到 `_GOV_FIELD_TYPES`(`scripts/lumos:18434`)的欄位表要補,沒提這張表。我沒有跑實作確認漏掉會怎樣,所以這條標 ⚠ 交編排者。

## 3. 第二種做法:有一處第二套 XML 讀法,一處分份規則是新寫的
- 讀 XML:專案現在只有一條讀法。`_secev_junit_facts`(`scripts/lumos:9046`)經過 `tq.junit`,而 `scripts/test_quality.py:151-178` 的 `NoDtdTreeBuilder` 是唯一的 DTD 拒收點,不接受任何 DTD。計劃範圍 3 另寫了 JaCoCo 讀法:自己判斷開頭的 DOCTYPE 字串,只放行那一種外部宣告,有 `[` 或 `<!ENTITY` 才整份拒收。這是第二套 DTD 政策與解析路徑。
- 分份:計劃自己承認「盲判那支只按段數分份」(`_KT_BJ_PART_MAX`,`scripts/lumos:76336`),另外新寫了大小上限加減半再切。`--part` 與份數印出的形狀沿用 blind-judge,所以我判 minor。它在你列的「另一套分份」之內,判不準,標 ⚠。
- 其餘沒有第二種做法:
  - 代換與引號走 `_run_cmd_expand`。
  - 工作樹、訊號處理沿用既有的。
  - 記帳走同一份治理帳,沒另開檔。

## 4. 落點:不合理
- `Systems/guard-kill` 的 responsibility 明寫「不負責:挑哪些行產生壞法(規格閘的選擇點那段)」,而且它已經是「掛 0 份計劃、沒寫負責範圍」的 170 行節點。
- 計劃範圍 8 要把覆蓋 WHY、RULE、PITFALL 搬進它。覆蓋階段、層判讀、reach 與 layer 帳,都不是 guard kill 的殺傷力判定。
- 覆蓋與層屬於 choice-kill 的一段,既有說明主要在 `Systems/規格閘`(提到 choice-kill 10 次,guard-kill 只有 7 次)。
- 建議:
  - 覆蓋、層、換候選的現況寫進規格閘的選擇點那段,或另開一篇 choice-kill 的家。
  - guard-kill 只留「覆蓋階段不動 `cmd_guard_kill`」這一句。
  - 計劃要補 lands_in 的理由。

## Findings

severity: major
blocking: 是
引句:「只接受這一種不帶內部子集的外部宣告」
對照:`scripts/test_quality.py:151-178`、`scripts/lumos:9046`。JaCoCo 另寫一套 DOCTYPE 判斷與解析,沒有走既有的唯一 DTD 拒收點。建議擴充 `NoDtdTreeBuilder` 或共用 helper,讓政策只有一處。

severity: minor
blocking: 否
引句:「大小上限與減半再切是這裡新寫的」
對照:`scripts/lumos:76336`。blind-judge 只按段數分份,這裡多一套大小分份。⚠ 判不準是不是「另一套分份」。

severity: minor
blocking: 否
引句:「它不經 `_choice_merge_shape`」
對照:`scripts/lumos:28783`。兩個佔位符語意不一致(`{method}` 前面自己帶 `--tests`,`{tests}` 本身含 `--tests`)。

severity: minor
blocking: 否
引句:「治理帳讀取的欄位白名單與型別表要補 reach 與 layer 事件的新欄位」
對照:`scripts/lumos:21047-21054`。(gate, kind) 白名單沒提;⚠ 沒跑實作確認漏掉的後果。

severity: minor
blocking: 否
引句:「[[Systems/guard-kill]] 補一條 WHY(分類用條款群組的覆蓋、不用全部測試的覆蓋」
對照:`docs/lumos-toolchain-knowledge/Systems/guard-kill.md:5`(responsibility 的不負責範圍)。

不對齊共 5 條,其中 major 1 條。
