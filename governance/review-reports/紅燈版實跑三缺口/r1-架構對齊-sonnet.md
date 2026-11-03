severity: minor

我只讀了程式和計劃,沒有改 repo,也沒有留任何暫存。這份設計沒有引入第二種做法,也沒有跨層直呼,所以沒有 major。有 8 條 minor,其中多條是設計沒寫清楚、實作時可能走歪,不是已經寫歪。

## 1. 分層與依賴方向

整體對齊,有兩處沒寫清楚。

- **切參數**:對齊。鄰居 `_tg_call_parts` 已經用 `_rg_bracket_map(_tg_strip(stmt))` 做括號配對,再回原文取字(`scripts/lumos:48973`)。測試防竄改比對呼叫 Room 守衛區的切參數函式已有先例,`_rg_split_args` 的 `angle=False` 就是專給比對用的開關(`scripts/lumos:47979`)。加選填遮罩參數、Room 守衛不帶遮罩,方向沒變。
- **規格閘讀測試防竄改比對的常數和函式**:這個方向有先例,如 `_TG_RB_DIR`、`_tg_rb_path_ok`(`scripts/lumos:14309`、`14430`)。提醒的共用判法若放在比對那側,規格閘去呼叫,方向就對。

**finding 1:推送前補平台時,沒指名用哪支條款解析**
severity: minor
引句:「才看現在計劃條款裡同名的引用」
- `_spec_gate_push_one` 手上只有留痕和重判結果,沒有計劃正文(`scripts/lumos:15919`)。
- 既有的條款解析是 `_clause_bindings_for`(`scripts/lumos:15551`)加 `_spec_gate_items`(`scripts/lumos:14887`),再交給 `resolve_test_refs`(`scripts/lumos:6419`)。
- 實作時若自己用正則掃正文,就等於推送閘繞過條款解析。設計該明寫「走這條既有路」。
file: `scripts/lumos:14887`

**finding 2:兩處要問「治理帳被忽略沒」,但沒指定共用同一支函式**
severity: minor
引句:「規格閘寫出紅燈版時也照同一個判法問一次」
- 現有 `git check-ignore` 的呼叫有四處:`scripts/lumos:1764`、`14298`、`14408`、`36817`。
- 「先判已追蹤、再判忽略」的兩步只在 `_local_ledger_doctor_msgs` 裡寫成行內程式(`scripts/lumos:1763`)。
- 設計新增的 `-v` 取規則來源,現有四處都沒有。
- 比對那側和規格閘那側若各抄一份,就多出兩份。設計要寫明抽成一支,放比對那側,規格閘去呼叫。
file: `scripts/lumos:1763`

## 2. 命名與錯誤處理

**對齊的部分**
- 提醒措辭的句型和 `_redbase_target_why` 同一種:「被 git 忽略,寫了也提交不進去(…)」(`scripts/lumos:14413`)。
- 設計說來源不一定是 `.gitignore`,比鄰居寫死 `.gitignore` 更準。
- git 呼叫借 `_lens_git`,和鄰居一致。

**finding 3:git 失敗和逾時沒寫,而鄰居彼此不一致 ⚠**
severity: minor
引句:「只在真有這兩種情形時問」
- 設計沒說 `_lens_git` 回 None、回傳碼不是 0 或 1 時怎麼辦。
- `_local_ledger_doctor_msgs` 是靜默不提醒(`scripts/lumos:1765-1767`)。
- `_git_ignored` 是回空集合,等於當沒被忽略(`scripts/lumos:36818`)。
- `_redbase_target_why` 是回一句「git 判不了…」(`scripts/lumos:14409-14410`)。
- 這裡「判不了」最合理的做法是照舊措辭,同 doctor 那條。設計要寫出來。
- 逾時也有分歧:比對函式 `_tg_redbase_cands` 收 `deadline`。`_tg_rb_deleted` 用有截止時間的 `_lens_git_dl`(`scripts/lumos:49694`),`_tg_rb_pending` 卻用 `_lens_git`(`scripts/lumos:49720`)。設計寫「借 `_lens_git`」,沒說選哪一邊。「一次推送最多問一次」怎麼記(傳參數或快取)也沒寫。
- 鄰居自己不一致,所以標 ⚠ 交編排者。
file: `scripts/lumos:49694`

**finding 4:固定身分字用中文,既有的是 ASCII**
severity: minor
引句:「兩句提醒的身分字改用固定字」
- 既有先例只有一個:`ident="deleted"`(`scripts/lumos:49742`)。
- 設計的固定字是「孤兒」「還沒提交」,和既有寫法不同。這不影響功能,只影響日後看帳的人。
file: `scripts/lumos:49742`

**finding 5:「遮罩」是專案裡沒有的叫法**
severity: minor
引句:「加一個選填的遮罩參數」
- 鄰居把同一件事叫「剝過的文字」,變數名是 `stripped`、`blank`、`keep`(`scripts/lumos:48865`、`49214`)。
- `_tg_strip` 的說明也是「剝註解…位置一一對應」(`scripts/lumos:48722`)。
- 參數名用 `stripped` 較一致。
file: `scripts/lumos:48722`

附註(不計條數):`_tg_call_parts` 對 `_rg_split_args` 有兩處呼叫,首呼叫在 `scripts/lumos:48976`,串接 `.isEqualTo(...)` 的參數在 `scripts/lumos:48983`。設計只寫「`_tg_call_parts` 帶遮罩」,沒說兩處都改。只改一處的話,同一個函式會有兩種切法。

附註(不計條數):做法 3 說規格閘「多印一行同樣的提醒」,S5 寫的卻是另一句(留痕進不了提交、推送時列成沒有留痕)。內文和條款對不上。

## 3. 第二種做法

沒有新工具、沒有新的子程序、沒有另一套詞法掃描。切參數、剝字串、判忽略都借既有的,PRIOR-ART 也寫了。下面兩條是容易走成兩套的地方。

**finding 6:平台記法在同一個閘的兩種事件裡不同 ⚠**
severity: minor
引句:「寫 tests 時非預設平台寫成」
- `spec-gate-green` 事件用成對的 `items`,`tests` 只留給人看(`scripts/lumos:14325-14326`)。
- 設計讓留痕事件的 `tests` 欄帶「平台:名字」字串。
- 這種字串其實是專案本來就有的另一種格式。留痕的讀者 `_spec_gate_push_one` 本來就用 `[test:{t}]` 加 `resolve_test_refs` 解析(`scripts/lumos:15939-15940`)。計劃條款也是這種寫法。所以不算新發明,但同一個閘的兩種事件記法不一致。
- 設計沒解釋為什麼不照 `items` 另開一欄。
- 另有一個疑點:設計要用 `_spec_gate_items` 算出來的平台去補 `tests`,可是 `tests` 目前來自 `_spec_gate_prepare` 的 `names`(`scripts/lumos:14181`)。`_spec_gate_items` 只收 `state == "bound"` 的條款,`names` 收所有解得出引用的條款,兩者可能不是同一個集合。設計要說清楚清單從哪來。
- 兩個鄰居各是一種,所以標 ⚠。
file: `scripts/lumos:14325`

**finding 7:切參數函式多一套深度規則,沒有等價綁定**
severity: minor
引句:「遮罩掃描不認 Kotlin 字串模板裡的巢狀引號」
- `_rg_bracket_map` 的說明明講:它和 `_rg_balanced` 是同一條規則的兩種查法,等價由隨機字串測試綁住,改一支要兩支一起改(`scripts/lumos:47967-47970`)。
- 設計讓 `_rg_split_args` 多算一份遮罩深度,同時要求原文深度也是 0。這條規則和 `_rg_bracket_map` 的深度可能日後分歧。
- 驗收條款 S1 只驗輸出,沒有要求綁這種等價。
- 這是既有慣例,不是新做法,所以只列 minor。
file: `scripts/lumos:47967`

## 4. 落點合不合理

**規格閘**:該寫進既有那篇。
- 它的 responsibility 明寫「規格閘紅燈版的寫入…推送前讀留痕跑測試(--push-check)」,而且不負責紅燈版比對(`規格閘.md` responsibility)。
- 現況是已存在、掛 0 份計劃、20 行 KEY、管 1 支檔、有寫負責範圍。
- 做法 2(留痕記平台、推送前補平台)和做法 3 的規格閘那半都歸這裡。
- `規格閘.md:33` 的 KEY 寫留痕有「全部測試名」,tests 欄加前綴後要改這一行,不要另加一行去和它矛盾。

**test-guard**:該寫進既有那篇。
- 它的 responsibility 包含斷言判讀、`tq/redbase-*`、紅燈版比對,做法 1 和做法 3 的比對那半都歸這裡。
- 這篇在 repo 工作樹裡有(51 行),只是不在派工附的會談目錄。

**room-guard**:合理,只需補一小行。
- 該篇已有一行 WHY 記「方法切法同時給測試防竄改比對用」。
- `_rg_split_args` 加選填參數,補一行即可,不用新開。

**bound-tests-gate**:不合理。
severity: minor
引句:「Systems/bound-tests-gate」
- 計劃的做法段沒有任何一項落在它身上。
- 它沒有負責範圍,18 行 KEY,管 3 支檔(`ci.yml`、`pre-push`、`scripts/lumos`)。它和本案只有兩處關係:`pre-push` 呼叫 `spec-gate --push-check`(KEY 在該篇第 36 行附近),以及它消費 `resolve_test_refs`。這兩處本案都沒改。
- 推送前補平台的行為歸規格閘。拿掉這個 lands_in,或在計劃寫明要在它身上記什麼。
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:59`

**不需要另開新篇**。4 篇裡有 3 篇對得上,第 4 篇建議移出 lands_in。

不對齊共 8 條,其中 major 0 條。

相關檔案:
- `/Users/enzo/harness/lumos-redbase-realrun/governance/review-reports/紅燈版實跑三缺口/r1-snapshot.md`
- `/Users/enzo/harness/lumos-redbase-realrun/scripts/lumos`
- `/Users/enzo/harness/lumos-redbase-realrun/docs/lumos-toolchain-knowledge/Systems/規格閘.md`
- `/Users/enzo/harness/lumos-redbase-realrun/docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`
