severity: major

我逐問對照了 r3-snapshot.md 與 `scripts/lumos`、`scripts/hooks/pre-push`。沒有建任何暫存目錄,也沒改任何檔。

## 1. 分層與依賴方向:對齊

- **基準重播放在 `--push-check` 裡**:跟鄰居同一條線。`_spec_gate_push_check`(`scripts/lumos:16307`)是 pre-push 唯一呼叫點(`scripts/hooks/pre-push:565`),旁邊的 `_spec_gate_push_scan`(`scripts/lumos:16248`)已經直接呼叫 `_spec_gate_judge_items`(`scripts/lumos:15105`)再進 `_run_bound_tests`(`scripts/lumos:69029`)。起點用 `_range_base`(`scripts/lumos:61298`),`_spec_gate_status_at`(`scripts/lumos:16217`)已經這樣用。沒有跨層直呼。
- **簽核寫治理帳、推送前讀**:寫的方向是 `_gate_event`(`scripts/lumos:1799`,已有 `signoff`、`spec-gate` 兩個閘名)。讀的方向是 `_gov_vc_gate_events`(`scripts/lumos:22229`),審查收斂規則的 residual-ask 與 guard-audit 早就拿治理帳當主要紀錄。統計沿用 fix-check 在 `_gov_row`(`scripts/lumos:16987`)按閘名多帶欄位的做法。
- **`--expected` 旗標**:早期分支到另一支函式,跟 lint-waive 的 `--ack`(`scripts/lumos:38517` 一帶)、端到端驗收的 `--ack` 同形。
- **「某一筆符合就算簽過」**:這是計劃自己寫明理由的刻意分歧,不同於 `_spec_gate_pick`(`scripts/lumos:15508`)的「取最晚一筆」,不列為不對齊。
- 計劃沒交代新檢查放在 `_spec_gate_push_check` 的哪個位置。這個函式有兩個提早 `return 0`:`if not plans`(`scripts/lumos:16334`)和 `if bad is None`(`scripts/lumos:16336`)。放在它們後面,平台設定讀不動時整個重播會被跳過。這點併進下面第 2 問的第一條。

## 2. 命名與錯誤處理:大致對齊,5 條 minor

事件 kind 都是 kebab-case,跟 `nogo-light-review-missing`、`spec-gate-record` 同形。簽核答 n 回 1、檢查不過回 2,跟 `scripts/lumos:38517`、`:43518` 一致。`origin` 欄名取自 lint-waive,`who` 取自 `_e2e_who`(`scripts/lumos:43283`),`_NOTE_LINT_PLAN_SINCE`(`scripts/lumos:12694`)的生效寫法也照用。不對齊的有:

- **重播跑不了時擋下,跟鄰居同樣的失敗放行。**
  - `_spec_gate_push_scan` 讀不動平台設定時印一句就放行(`scripts/lumos:16283`–`16286`)。
  - `_spec_gate_push_check` 的 docstring 明寫「算不出範圍/索引 fail-open,推送閘不能因為工具壞而擋所有人」(`scripts/lumos:16307`–`16312`)。
  - 計劃把同樣的觸發(平台設定讀不動)改成擋下,另外加了起點取不到、建樹失敗,沒說為什麼跟鄰居不同。出口只有 `base_replay_skip`。

severity: minor
blocking: 否
引句:「或重播跑不了(起點取不到、建樹失敗、平台設定讀不動)」
file: `scripts/lumos:16283`

- **生效常數名字停在已被拿掉的舊構想。** `_HIGH_RED_SINCE` 現在管基準重播、預期值表、簽核三件事,鄰居都依功能命名(`_SPEC_GATE_SINCE`、`_NOTE_LINT_PLAN_SINCE`)。

severity: minor
blocking: 否
引句:「生效日:程式常數 `_HIGH_RED_SINCE`,純日期」
file: `scripts/lumos:12694`

- **`base_replay_skip` 沒登記到欄位清單。** 計劃說用 `lumos set` 寫,但 `SCALAR_KEYS`(`scripts/lumos:28705`)沒有它,`_cmd_set_locked` 會直接擋下(`scripts/lumos:29605`),也沒進 `_KNOWN_FRONTMATTER_KEYS`(`scripts/lumos:12274`)。照 `plan_risk` 的先例,至少要登記後者。現在計劃寫的出口,照寫的指令寫不進去。

severity: minor
blocking: 否
引句:「理由去掉空白標點至少 10 個字,用 `lumos set` 寫」
file: `scripts/lumos:28705`

- **新事件的欄位與鄰居不一致。**
  - `rows` 在 note-reread 與 drift 事件裡是清單(`_gate_event_fit` 的 list_key,`scripts/lumos:53663`–`53683`)。`_GOV_FIELD_TYPES` 的註解要求同名欄位型別一致(`scripts/lumos:16912`–`16916`),這裡卻拿 `rows` 當整數列數。
  - `origin` 沒進 `_GOV_FIELD_TYPES`(`scripts/lumos:16917`),註解要求新 mapper 用到的欄位一起補。
  - 事件沒說帶 `nodes=[計劃]`,spec-gate-record(`scripts/lumos:14296`)與 `_nogo_light_block_event`(`scripts/lumos:16102`)都帶,少了它 `lumos gov <計劃>` 查不到。
  - 也沒說 `hard` 是真是假。

severity: minor
blocking: 否
引句:「`rows`(列數)、`origin`(human 或 ai,同 lint-waive 的欄名)」
file: `scripts/lumos:16917`

- **簽核提示沒走外來文字清理,「沒簽」訊息也對不上。** `_waive_origin_tty`(`scripts/lumos:38429`)自己寫死印「沒放行」,計劃要印「沒簽」,沒說是加參數還是另印一行。鄰居呼叫端把外來字串都先過 `_out_clean`(`scripts/lumos:38425`、`19955`),計劃把整張表直接放進提示字串。

severity: minor
blocking: 否
引句:「用 `_waive_origin_tty`,把整張表與」
file: `scripts/lumos:38429`

## 3. 第二種做法:有 3 條 major、4 條 minor

**隔離工作樹**

- **工作樹準備長出第三種做法,漏了鄰居處理過的三個環境問題。**
  - 修正關卡在同樣的工作樹裡做了三件事:設定檔沒進版控就複製進樹(`scripts/lumos:21944`),依賴資料夾連回主目錄(`_lint_link_deps`,`scripts/lumos:21990`、`39221`;有 `fix_check.link_deps` 開關,`:21492`),平台根在樹外或子模組就標「釘不住版本」(`scripts/lumos:21948`–`21975`)。
  - guard kill 則是在平台根自己的 git 上建樹(`scripts/lumos:26384`)。
  - 計劃寫「平台設定用它自己的」,三件事都沒提。
  - 後果:node 或 venv 專案的新工作樹沒有 `node_modules`、`.venv`,兩棵樹的測試都起不來。對照組、推送版都不綠,等於每個這類專案都被擋。平台根在樹外時,「舊程式」其實是現在的程式,會誤判成「在舊程式上就綠」。
  - 修正關卡這段是寫在 `cmd_fix_check` 裡的內聯程式碼,沒有可呼叫的函式。要嘛抽成共用函式,要嘛計劃寫明差異,不然會有第三份。

severity: major
blocking: 是
引句:「分岔點那一棵其餘檔維持舊版,平台設定用它自己的」
file: `scripts/lumos:21944`

- **把測試檔覆蓋進舊版樹,既有做法有兩種,計劃只說「複製」。** 一種是修正關卡只複製位元組、不帶檔案模式(`scripts/lumos:21944` 的註解)。另一種是 guard kill 的 realpath 圍欄(`scripts/lumos:26376`)加 `git checkout -- ":(literal)…"`(`scripts/lumos:26462`)。計劃沒說測試檔是符號連結、路徑含特殊字元時怎麼處理。實作時很容易再長出第三種。⚠ 這條是規格含糊,還不是已成形的第二套,請編排者裁。

severity: minor
blocking: 否
引句:「從推送版複製進分岔點那一棵(刪掉的不動)」
file: `scripts/lumos:26462`

**判定規則**

- **紅綠判定把既有的雙向門規則重寫了一份。**
  - 「新行為一定要紅、keeps 要綠、弱證據不算紅」正是 `_spec_gate_twoway_run_verdict`(`scripts/lumos:14242`)的真值表,配 `_spec_gate_run_clauses`(`scripts/lumos:15127`)產生的逐條款判定。
  - 計劃的借用清單沒列這兩支。計劃的「做法 4」另寫了四種擋下:舊版就綠、推送版不綠、對照組不綠、弱證據。三種擋下理由跟既有函式是同一組規則,卻是新文字、新函式。
  - 「逾時的紅不算」的判法是 `_redbase_row_reason` 裡私有的 `startswith("超時")`(`scripts/lumos:14345`),計劃也沒說是抽出共用還是再寫一次。
  - 該做的是:分岔點那一棵直接呼叫既有判定函式,推送版那一棵只判全綠。

severity: major
blocking: 是
引句:「擋——對照組在分岔點不綠」
file: `scripts/lumos:14242`

- **「改到程式檔」又寫了第三個定義。**
  - 計劃寫「不算圖譜目錄底下的檔、不算帳本、不算測試」,沒有副檔名判斷。
  - 專案裡已有兩個單一來源:`_is_code_file`(`scripts/lumos:15579`)是「需要有家的程式檔」,`_pitfall_tier` 也用它(`scripts/lumos:60911`)。小改動閘用 `_sc_changed_files` 的 `_bk`(`scripts/lumos:15611`–`15622`),註解明寫「自開正則=第二套判準會漂」(`scripts/lumos:13903`)。
  - 計劃的寫法會把 README、yaml、鎖檔也算成程式檔,觸發重播,跟 `_is_code_file` 的結果不同。

severity: major
blocking: 是
引句:「這次範圍另外改到至少一支程式檔——不算圖譜目錄底下的檔」
file: `scripts/lumos:15579`

**表格與字數判定**

- **表格拆格是第三份,計劃沒說跟前兩份的關係。** 現有兩處寬鬆拆法(`scripts/lumos:27561`、`:51363`)都是 `strip("|").split("|")`,不認 `\|`。新的是嚴格 GFM 拆格,目的不同(驗證與指紋),但計劃沒寫是做成共用函式還是各用各的。這是 r2 的 a9,折入時只加了規則,沒交代關係。

severity: minor
blocking: 否
引句:「拆格:去掉行頭行尾空白後,外側的 `|` 各去掉一個(只去一個)」
file: `scripts/lumos:27561`

- **「去掉空白標點後至少 N 個字」沒指名共用的 `_real_chars`。** `_real_chars`(`scripts/lumos:13923`)的註解寫明「不抄第二份」。同類的最短字數檢查現在有三種寫法:lint-waive 用 `\s` 加 `[^\W_]`,端到端驗收只去 `\s`,`_real_chars` 去標點。計劃兩處(理由 10 字、來源欄 4 字)沒說用哪一種。

severity: minor
blocking: 否
引句:「來源欄去掉空白與標點後至少 4 個字(中文字、英文字母、數字都算)」
file: `scripts/lumos:13923`

**簽核事件與統計**:不算第二套。它跟 `.signoff-log.jsonl` 分開存,有 fix-check 與跑滿回顧的先例。`_gov_row` 加 token 的寫法也是 fix-check 的先例。計劃寫明不寫 `.signoff-log.jsonl`,`guard abandon` 讀的簽核帳不受影響。

## 4. 落點:大致合理,1 條 minor

- **`Systems/規格閘`**(66060 位元組,管 `scripts/lumos`):基準重播進這裡合理。`responsibility`(該檔第 6 行)已含「推送前讀留痕跑測試(--push-check)」,基準重播與預期值表檢查就是它的延伸,不需要另開節點。
- **`Systems/reversibility-governance-ledger`**(22872 位元組):新 kind 的 WHY 行放這裡合理,它已有 signoff 的 KEY(第 31 行)與 gov 彙整說明。目前沒寫負責範圍,計劃已寫要補。
- **`Systems/bound-tests-gate`**(47098 位元組,管 `scripts/hooks/pre-push`):只改掛鉤訊息的家,合理。
- **漏列**:`_isolated_worktree` 與樹準備是修正關卡的家,`Systems/代碼審修正關卡` 的測試清單有 `t_fix_check_tree_setup` 與 `t_isolated_worktree_shared`,`Systems/guard-kill` 也提到它。如果依上面第一條 major 抽成共用函式,家就在這兩篇,`lands_in` 要補。另外 `Systems/規格閘` 的 `responsibility` 沒涵蓋基準重播、預期值表與簽核,計劃只寫了補「風險高照半套那幾行」,沒寫要改負責範圍。

severity: minor
blocking: 否
引句:「前綴 `lumos-replay-`,建樹前清同前綴的殘骸」
file: `docs/lumos-toolchain-knowledge/Systems/代碼審修正關卡.md:23`

不對齊共 12 條,其中 major 3 條

主要涉及的檔案:
- `/Users/enzo/harness/lumos-highrisk-evidence/scripts/lumos`
- `/Users/enzo/harness/lumos-highrisk-evidence/scripts/hooks/pre-push`
- `/Users/enzo/harness/lumos-highrisk-evidence/docs/lumos-toolchain-knowledge/Systems/規格閘.md`
