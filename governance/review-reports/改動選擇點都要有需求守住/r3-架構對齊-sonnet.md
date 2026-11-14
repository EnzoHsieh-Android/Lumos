severity: major

## 問 1 分層與依賴方向:大致對齊
新增的推送前那一圈放在 `_spec_gate_push_check` 裡、接在 `_spec_gate_push_scan` 後面,而且重用 `_kt_sit_read_many`、`_gov_rows_at`、`_push_mainlines`、`_drift_tree_env`。`spec-gate --push-check` 新增成對的 `--push-remote`、`--pushed-ref`,也有 drift、room-guard、reread-check 的先例(`scripts/lumos:79703`、`79955`、`79968`)。只有一處對不上:`ast-grep` 在 `scripts/lumos` 裡現在只出現在白名單執行規則包命令的地方(`scripts/lumos:41577` 附近)。計劃讓 lumos 本體自己呼叫 `ast-grep` 並解析 JSON,這是新的呼叫方式,見 a1。沒看到跨層直呼。
引句:「在 `_spec_gate_push_check` 裡、`_spec_gate_push_scan` 之後另起一圈(沒有候選計劃也跑)」
對照:`scripts/lumos:17387`、`scripts/lumos:17243`

## 問 2 命名與錯誤處理:大致對齊,有 ⚠
`choice-points`、`choice-kill` 是頂層指令,沿用 `situation-rule` 這類扁平命名。ast-grep 不在 PATH 時,choice-points 回 3、choice-kill 回 2,計劃說是照新增告警那道的 rc 3 語意。我沒在 `scripts/lumos` 裡找到那個 rc 3 的程式碼出處,不確定,標 ⚠。新治理帳事件 `choice-kill` 的 gate 與 kind 形狀,跟 `situation-rule` 的登記方式一致(`_KNOWN_GATES`、`LOOP_NOT_CLOSE_EVENTS`、`_gov_row`)。
引句:「`lumos choice-points [--diff <範圍>] [--branch <名>]`:唯讀,列出改到的行與每行挑中的壞法」
對照:`scripts/lumos:20661`、`scripts/lumos:17706`、`scripts/lumos:18295`

## 問 3 第二種做法:有兩處
- **掃描:不對齊。** kt-situation 是用「型錄觸發字正規式加縮排切段」掃改到的行(`_kt_sit_hits`、`_kt_sit_group`、`_kt_sit_material`)。選擇點掃描則是 ast-grep 語法樹,讀命中節點的起訖與後設變數。同一件事有兩套掃描,兩套都在掃「改到的行」。計劃有交代為什麼換(r1、r2 被文字近似打穿),但沒說情境題那邊以後要不要也改走語法樹、現在兩套怎麼共存。
- **殺傷力:對齊。** `choice-kill` 沿用 `cmd_guard_kill` 的 `recipes_override`,只加選用參數,跟 `situation-rule` 的先例同形。
- **人裁處置:不對齊。** 看 a2。
- **兩張表:** 〈選擇點表〉和情境決策表互相指列號,用途有分,見 a3。

引句:「不引進外部變異工具(PIT 等);ast-grep 只當剖析器,是 Kotlin 規則包既有的外部工具。」
對照:`scripts/lumos:40184`、`scripts/lumos:40207`、`scripts/lumos:27902`、`scripts/lumos:76534`

## 問 4 落點:大致合理,有 ⚠
掃描、推送閘、治理帳事件寫進 `Systems/規格閘`,殺傷力批次參數寫進 `Systems/guard-kill`,型錄與規則寫進 `Systems/kotlin規則包`,這個分法跟程式的分層一致。但 `Systems/guard-kill` 現在沒寫負責範圍,而計劃要往它塞 `source`、`stop_group_on_kill`、`on_row` 和「choice-kill 不寫殺傷力帳本」的口徑。要先補負責範圍,才不會讓那篇變成雜物間。
引句:「`cmd_guard_kill` 新增的選用參數(都不傳時行為不變):`source`(寫進殺傷力帳本與配方 note)、`stop_group_on_kill`、`on_row`」
對照:`scripts/lumos:27902`、`scripts/lumos:77491`

## a1 選擇點掃描是第二套「掃改到的行」的做法
severity: major
blocking: 是
引句:「lumos 以參數清單(不開 shell)執行 `ast-grep scan --config <那份設定> --json=stream <檔>`」
file: `scripts/lumos:40184`

## a2 choice-judge 另開一條放行路徑,沒併進既有放行
severity: major
blocking: 是
引句:「讀 HEAD 版的檔與範圍(跟 choice-kill 同一套範圍),不跑測試、不要求工作目錄乾淨」
file: `scripts/lumos:42153`

- 情境題同類的放行,既有做法是 `lumos lint-waive kt-situation:<段身分>`(`scripts/lumos:74161`、`78644`)。它跟新增告警共用放行檔、理由、origin、ack 和 doctor 計數。
- `choice-judge` 另寫 kind `judged`,自己有 origin 和 consent 欄位,也自己做 `_waive_origin_tty` 那套,等於第二套放行機制。
- 計劃說它「同 guard 的 kill-add 那種只寫帳的指令形狀」,這句有誤。`cmd_guard_kill_add`(`scripts/lumos:27215`)寫的是筆記裡的配方,不是治理帳。

## a3 選擇點表跟情境決策表是兩張表
severity: minor
blocking: 否
引句:「壞法只有選擇點表一個來源」
file: `scripts/lumos:39325`

計劃已用「對應的情境決策表列號」欄互指,並說明用途不同。同一份型錄讀兩張表,結構上沒壞。

## a4 新指令的命名和錯誤處理有兩處對不上鄰居
severity: minor
blocking: 否
引句:「ast-grep 不在 → rc 3;型錄缺檔 → 提醒、rc 0;表壞 → rc 2。」
file: `scripts/lumos:39302`

- rc 3 沿用新增告警那道的語意,但我沒找到那段程式的出處,標 ⚠。
- 型錄缺檔回 0,跟 `_kt_catalog_path()` 目前的缺檔處理是否一致,我沒驗,標 ⚠。

不對齊共 4 條,其中 major 2 條
