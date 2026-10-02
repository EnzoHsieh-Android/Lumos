severity: minor

**審查範圍**:修正是否成立,以及筆記與程式是否對得上。
- 在 `1685194c` 的 repo 上跑了 `scripts/lumos doctor --verbose`:S16 有 6 條 RULE 缺 `[confirmed:]`,屬舊帳,不是新誤報;S17、S18、S19 全綠,沒有誤報。
- `lumos lint` 跑了改到的四篇(撤除條件檢查末輪遺留四項、筆記格子寫法與過期檢查_計劃、lumos-cli-read、存量漂移守衛),都是 0 問題。
- 測試子集全綠。`-k t_slots` 193 過 0 敗;`-k note_shape` 178 過;`-k slots_edited` 4 過;`-k old_sentence` 5 過;`-k doctor_lists_stale` 8 過。
- [S13] 綁的三支測試(`t_slots_doctor_reminders`、`t_slots_doctor_reminders_edges`、`t_slots_doctor_reminders_r2`)都存在且綠。
- 沒有 blocking 級問題。

**R3G1** 筆記講的共用讀法名字跟程式現在對不上
severity: minor
blocking: 否 — 只是函式名過期,行為沒壞,但是這輪新加的名字漏同步。
- `_drift_jsonl_iter` 是這輪新加的。帳增速段與 S18 的 `_gov_metric_events` 都改成讀它。
- `Systems/lumos-cli-read` 還寫「跟帳增速那段共用 `_gov_tail_bytes` 與 `_drift_jsonl_parse`」,讀者會去找錯函式。
- 同一份 diff 裡的程式註解也沒改,仍寫「走帳檔共用的 `_drift_jsonl_parse` … 跟度量段(S18)同一種讀法」。
- 這與計劃效能那行的「逐筆解析、不留整份清單」不一致。
引句:「治理帳檔尾只讀一遍,跟帳增速那段共用 _gov_tail_bytes 與 _drift_jsonl_parse」
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:14`、`scripts/lumos:2055`

**R3G2** ⚠ 推送那支改回「先印後記」後,兜底的那句 print 又沒包保護
severity: minor
blocking: 否 — 要 stderr 壞掉才會發生,而且鄰居(m1、c1 到 c5)本來就是這樣寫。
- 場景:stderr 已關或管線斷。`_drift_retire_print` 丟例外,`except` 裡那句 `print(..., file=sys.stderr)` 再丟一次,例外會一路冒出 `_drift_retire_report`。這時帳沒記、rc 也沒回。
- r1 併發資源席抓的就是這個洞,當時用 `_drift_retire_quiet` 補;r2 為了跟鄰居一致拿掉了它,洞跟著回來。
- 沒有測試釘「stderr 壞掉」。
- 圖譜的 Issue、Systems 都寫「印出與記帳各自兜、出錯只講一句、不改判定」。把「講一句」這個動作本身出錯的情形算進去,這句話就不成立。
引句:「print(f"存量漂移檢查:RULE 撤除條件的清單印到一半出錯({type(ex).__name__}),判定照舊", file=sys.stderr)」
file: `scripts/lumos:32413`

**R3G3** ⚠ S18 的 fail-open 行直接印例外全文,沒清控制字元
severity: minor
blocking: 否 — 寫法與鄰近的帳增速、前掃兩段相同,不是退步。
- 圖譜寫「印出前清控制字元」,是講 S17 到 S19 的提醒行。但 fail-open 這一行用 `{_e18}` 印例外訊息原文,裡面可能帶路徑或筆記內容。
- 這一輪的資安席才剛要求 S17、S18 清控制字元,這行是漏網處。
引句:「ok(f"度量式撤除條件觀測跳過(fail-open:{_e18})")」
file: `scripts/lumos:2536`

**逐項對照的結果**
- **推送那支的順序**:`_drift_retire_report` 現在先 `_drift_retire_print`、後 `_drift_retire_ledger`。這和 Issue「修法」、`Systems/存量漂移守衛`「先印後記(同 m1 與 c1 到 c5)」逐字成立。m1 的記帳(`scripts/lumos:33448`)也在印出之後。
- **舊說法**:計劃、Issue、Systems 全文已搜過「先記帳再印」「先記後印」「最多 20 條」「`_drift_retire_quiet`」,殘留都是歷史敘述。
  - Issue 第 2 項的原文「先記帳再印清單」是問題描述,合理。
  - 計劃第 141 行的「最多 20 條」已註明是被取代的舊說法。
  - 計劃第 34 行的「維持 doctor 不評估條件」屬設計審 r3 的歷史 WHY,沒改。S18 度量式存在後讀者可能混淆,但天花板 13 與效能行已補上「`when-*`」限定。
- **S16 到 S19 共用讀法**:S16 的 `_doctor_stale_rules`、S17 到 S19 的 `_slot_summary_entries` 都走 `_note_summary_entries`,「統一」成立。S16 的 `_esc_clean` 也已補上。
- **讀設定檔「統一走 `_doctor_cfg_bytes`」**:S18 的 `_doctor_metric_lines` 與 `_metric_gate_off(lint-new)` 現在都用同一份快照。其他呼叫 `_lint_new_config(repo_root)` 的地方(`scripts/lumos:24846`、`scripts/lumos:41319`)不在 doctor 路徑,不衝突。
- **`_ns_summary_logical` 改 join**:輸出相同(`{行號: 整條}`),`cont` 的記錄也沒動。`note_shape`、`slots_edited`、`old_sentence` 三組子集全綠,提交時筆記檢查的既有合約沒被破壞。

**圖譜鏡頭**
派工尾端沒有固定席筆記,只給了 `LUMOS-IMPACT: 384f4574..1685194c` 範圍。我只對這份 diff 實際碰到的節點逐項判:
- `Systems/lumos-cli-read`:行為宣稱成立,只有 R3G1 的函式名過期。
- `Systems/存量漂移守衛`:先印後記、條數 null、續行行號擋下都與程式一致,不影響。
- `Issues/撤除條件檢查末輪遺留四項`:修法敘述與程式一致。R3G2 是「各自兜」的邊角。
- `Projects/筆記格子寫法與過期檢查_計劃`:[S13] 補綁成立,天花板 13 與效能行與程式一致。
- 筆記內容閘、筆記形狀那一族:`_ns_summary_logical` 只改內部累積方式,不影響。

新寫的筆記行格子齊,沒有寫別人家的檔。

最高嚴重度 minor,blocking 0 條
