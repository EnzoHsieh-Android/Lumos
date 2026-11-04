severity: major

我逐問對照了 r4-snapshot.md 和 `scripts/lumos`、`scripts/hooks/pre-push`。沒建暫存目錄,也沒改任何檔。python-idioms skill 在審查席被擋,沒讀,照鄰居程式碼判。

上一輪三處的處理驗證如下:
- 樹準備抽成共用函式:方向對,仍有幾個細節沒交代(見第 3 問)。
- 逐支自寫判定並附理由:理由只有一半站得住(見第 3 問)。
- 程式檔改用 `_is_code_file`:已對齊。`scripts/lumos:15579` 本來就排除測試檔,計劃再疊 `_nodehome_is_test` 加專案目錄設定只是更嚴,不是第三個定義。

## 1. 分層與依賴方向:對齊

- 重播放進 `_spec_gate_push_check`(`scripts/lumos:16307`),跟鄰居 `_spec_gate_push_scan` → `_spec_gate_judge_items`(`:15105`)→ `_run_bound_tests`(`:69029`)是同一條線,沒有跨層直呼。
- 掛鉤新增 `--push-remote`、`--pushed-ref`,跟 drift check、room-guard 的呼叫寫法一致(`scripts/hooks/pre-push:700`、`:718`,`pp_block_range_for` 在 `:58`)。
- `_isolated_worktree`(`:26074`)的前綴 `lumos-replay-` 跟 `lumos-fixcheck-`(`:21484`)、`lumos-kill-` 同形。
- 殘骸時限沿用 `_ISOLATED_WT_STALE_SEC`(86400 秒,`:38949`),比重播預算長,併發清殘骸不會誤砍。
- 簽核寫治理帳走 `_gate_event`(`:1799`)。`signoff` 在 `_KNOWN_GATES`,四個新 kind 不在 `_GOV_LOCAL_PAIRS`,會進版控帳,跟計劃的假設一致。

## 2. 命名與錯誤處理:大致對齊,4 條 minor

事件 kind 都是 kebab-case。`table_sha` 對應 `clause_sha`。`origin` 對應 lint-waive(`:38524`)。`row_count` 避開了 `rows` 的型別衝突。`_HIGH_RISK_EVIDENCE_SINCE` 的命名同 `_NOTE_LINT_PLAN_SINCE`(`:12694`)。不對齊的有:

- **專案層開關的形狀。** 鄰居都是「區塊加 `gate` 鍵」:`lint_new.gate`(`:39113`)、`security_evidence.gate`(`:8847`)、`fix_check.link_deps`(`:21492`)。計劃寫成頂層純量 `high_risk_evidence: block|warn|off`。計劃也沒說這個開關讀哪一版的設定。drift、room-guard、security_evidence 讀的是被推頂端提交那一版(`_lumos_config_at_ref`,`:60011`)。讀工作目錄的話,沒提交的 `off` 就能關掉整道。

severity: minor
blocking: 否
引句:「`.lumos/config.json` 加 `high_risk_evidence: block|warn|off`(預設 block)」
file: `scripts/lumos:39113`

- **擋下事件沒說 `hard`。** 計劃只替 `expected-signed` 寫了「hard 為否」。`base-replay-failed`、`expected-unsigned` 這兩種擋下沒交代。鄰居的擋下事件是 `hard: True`(`_nogo_light_block_event`,`:16102`)。r3 提過同一點,只修了一半。

severity: minor
blocking: 否
引句:「每一種擋寫一筆治理帳事件(閘 `spec-gate`、kind `base-replay-failed`、`nodes` 帶計劃、原因分類)」
file: `scripts/lumos:16102`

- **簽核逾時多開了第二個旋鈕。** 現有逾時只有一處:`_confirm_tty_timeout()` 讀 `LUMOS_TTY_TIMEOUT`(`:34220`),`_confirm_tty`(`:34193`)沒有逾時參數。計劃只說替 `_waive_origin_tty` 加選填逾時(預設 300 秒),沒說怎麼穿過 `_confirm_tty`,也沒說跟環境變數誰優先。

severity: minor
blocking: 否
引句:「與選填逾時(簽核預設 300 秒,表要讀;其他呼叫端不傳、照舊)」
file: `scripts/lumos:34193`

- **跑測試的參數與預算接不起來。**
  - 計劃的呼叫路徑是 `_spec_gate_judge_items`(`:15105`)呼叫 `_run_bound_tests`,但只替後者加了三個參數,中間那層沒交代要轉傳。
  - `_kill_run`(`:26155`)的 `Popen` 也沒有 `env` 參數。
  - 「在兩支測試之間檢查總預算」在批次跑法裡沒有掛點。要嘛改成逐支呼叫,那就繞過 `bound_tests.parallel`(`:69xxx` 的批次與並行);要嘛有第四個沒列的參數。
  - 計劃說「串行路徑也把子程序登記進去」,實際 `_one` 兩條路徑都已經經 `procs.launch` 登記。缺的是串行路徑出例外時的收尾,不是登記。

severity: minor
blocking: 否
引句:「整個重播另有總預算 `LUMOS_REPLAY_BUDGET`(預設 1800 秒),在兩支測試之間檢查」
file: `scripts/lumos:15105`

## 3. 第二種做法:2 條 major、6 條 minor

**major 兩條**

- **讀推送版治理帳,計劃另寫了第三種讀法。**
  - 已有兩套:
    - 工作目錄版:`_gov_vc_gate_events`(`:22229`),帶路徑守衛,回事件 dict。
    - 指定版本版:`_gov_rows_at`(`:61061`)加 `_residual_blob_at`(`:60917`)。它用 `git show --no-textconv`,狀態分 ok、missing、unreadable。
  - `_gov_rows_at` 的說明明寫「兩版治理帳的讀法只留一份」,殘留問答和規格閘紅燈版(`:14454`、`:14464`)都共用它。
  - 計劃要的「推送版沒有帳或解析不了就擋」正好對上它的狀態值。針對 `expected-signed` 只要給 needle 和 keep 就能用,不需要新讀法。
  - 計劃借用清單沒列這兩支,只寫「`git show`、同樣的解析」。「同樣」指哪一套不明,照字面實作就會長出第三套。

severity: major
blocking: 是
引句:「讀推送版裡的治理帳(`git show <推送版>:docs/.governance-log.jsonl`,同樣的解析)」
file: `scripts/lumos:61061`

- **推送版計劃的筆記物件,計劃要手工組,但已有單一來源。**
  - `_note_from_text(rel, text)`(`:900`)的說明寫「load_vault 與某個提交的樹共用,不另寫第二套解析」。它產出 `fields`、`block_keys`、`targets`、`lint`。
  - `_door_judge`(`:14007`)的連結訊號靠 `note.fields` 和 `targets`,手工只用 `split_frontmatter` 加 `parse_frontmatter` 組,很容易缺欄位而判門跟 load_vault 不同。
  - 同檔 `:60348` 也已拿 `_note_from_text` 解析 git 取出的文字。

severity: major
blocking: 是
引句:「再用 `split_frontmatter` 與 `parse_frontmatter` 從這份文字組出判門要的筆記物件」
file: `scripts/lumos:900`

**minor 六條**

- **自寫逐支判定(不借 `_spec_gate_twoway_run_verdict`):理由只有一半站得住。** ⚠ 請編排者裁。
  - 站得住的部分:
    - 要同時判兩棵樹。
    - 要回原因代碼給事件分類,既有函式只回訊息字串。
    - 逐支判才不會被「同條款另一支紅」蓋掉。
  - 站不住的部分:計劃把「合條款」算在 `_spec_gate_twoway_run_verdict`(`:14242`)頭上,但合併發生在上游 `_spec_gate_run_clauses`(`:15127`)。判定函式只吃以條款編號為鍵的 `verdicts` dict。餵逐支的鍵(例如 `S2/測試名`)就不會合併,同一張真值表可以重用。
  - 現在分岔點那一半(新行為要紅、keeps 要綠、弱證據不算紅)等於把同一張表再寫一份,日後低風險規則改了會漂。
  - 建議抽出共用的「真值表加原因代碼」,兩邊各自呼叫。
  - 判成 minor 的理由:語意是逐支,不是同一條規則的第二種判法,理由也寫進了計劃。若編排者認為「重寫同一張表」就算第二套,升 major 站得住。

severity: minor
blocking: 否
引句:「判定寫成一支新函式、回原因代碼(舊版就綠、對照組不綠、分岔點弱證據、推送版不綠),不借 `_spec_gate_twoway_run_verdict`」
file: `scripts/lumos:14242`

- **分岔點的算法在 `_rg_fork_point`(`:48423`)已經寫過一份。**
  - 它也是「舊值全 0 丟給 `_push_range_start`」,理由註解相同。
  - 計劃沒說抽共用還是再寫一份。
  - 兩處也不同:Room 守衛沒帶推送參數時退到 `_lens_default_base`;計劃是跳過並寫 `base-replay-skipped`。

severity: minor
blocking: 否
引句:「把遠端舊值當成全零,交給推送範圍指令的 `_push_range_start`」
file: `scripts/lumos:48423`

- **`_h2_section_lines` 本來就回行號。**
  - 它回 `[(行號, 原始行)]`(`:13774`),行號來自 `_visible_lines`,是原檔 1 起算的行號。
  - 計劃說要加「回傳每行的行號」的選填參數,多餘。照字面做會讓同一函式有兩種回傳形狀。
  - 該加的只有「標題出現幾次」。

severity: minor
blocking: 否
引句:「替它加兩個選填參數:回報這個標題出現幾次、回傳每行的行號」
file: `scripts/lumos:13774`

- **借 `_spec_gate_twoway_static` 時有兩處沒交代。**
  - 它內部寫死「全部條款都靠人驗……走小改動閘」那句(`:14229`)。風險高計劃推送時不走小改動閘,這句會誤導。計劃的選填參數只換前綴,而計劃自己另寫了「全是 manual 時不重播、印一句」,兩句會同時出現。
  - 它內部呼叫 `_plan_first_commit(rr, …)`(`:14194`),沿 HEAD 找。計劃只替日期那一處加了起點參數,keeps 存在性那一處照走 HEAD。推送的 ref 不是 HEAD 時,同一份計劃會有兩個歷史起點。

severity: minor
blocking: 否
引句:「重播前在推送版那份計劃上直接呼叫 `_spec_gate_twoway_static`」
file: `scripts/lumos:14218`

- **共用樹準備函式抽出後,有幾個差異沒定。**
  - 計劃把準備段抽成共用函式,方向對。
  - 但 `cmd_fix_check` 的設定檔只在樹裡沒有時才複製(`:21941`),計劃要分岔點那棵也用推送版設定,即覆蓋舊檔,這是新行為,沒說函式怎麼參數化。
  - 連依賴資料夾是否連,現在由 `fix_check.link_deps`(`:21492`、`:21979`)開關決定。共用後重播也被 `fix_check` 區塊管,或單獨不受管,計劃沒說。
  - 計劃寫死資料夾名,實際該走 `_LINT_DEP_DIRS`(`:39181`)。

severity: minor
blocking: 否
引句:「用 `_lint_link_deps` 把 `node_modules`、`.venv`、`venv` 連回主目錄」
file: `scripts/lumos:21941`

- **改檔清單的解析器沒指名。**
  - 計劃寫 `git diff --name-status -M`,沒說用哪支解析。
  - 共用的 `-z` 解析是 `_nodehome_name_status`(`:44527`)。`_pq_renames`(`:15200`)的說明明寫用它,是為了路徑含 tab 或換行時不切錯。`cmd_fix_check` 另有手寫迴圈。
  - 重播要靠這份清單處理改名、刪檔,不指名容易再長出第三種。

severity: minor
blocking: 否
引句:「推送範圍(用推送版對分岔點算 `git diff --name-status -M`)改到這份計劃檔」
file: `scripts/lumos:44527`

**對齊的部分**
- 逾時的紅不算:計劃把 `_redbase_row_reason`(`:14338`)的逾時判斷抽成共用小函式,這樣做是對的。
- 簽核存治理帳而不是 `.signoff-log.jsonl`:跟 fix-check、跑滿回顧一樣有先例。兩邊的 `guard abandon` 讀的是舊帳,不受影響。
- 表格拆格另寫一份嚴格版,沒動 `:27561`、`:51363` 那兩處寬鬆版:用途不同(要認 `\|`),計劃已承諾在寫回筆記時註明三者關係,可接受。
- 表指紋用 JSON 編碼,而不是 `_clause_block_sha`(`:14296` 附近)的 `|` 串接:有理由(避免碰撞)。
- `_real_chars`、`_waive_origin_tty`、`_e2e_who`、`origin` 欄、`_plan_first_commit`、`_NOTE_LINT_PLAN_SINCE` 的借用都指名了。

## 4. 落點:合理

- `Systems/規格閘`、`Systems/bound-tests-gate`、`Systems/reversibility-governance-ledger`、`Systems/代碼審修正關卡` 四個 lands_in 都說得通:
  - 重播與預期值表是規格閘推送前檢查的延伸。
  - 掛鉤訊息歸 bound-tests-gate。
  - 新 kind 與 signoff 歸治理帳節點(它已有 signoff 的 KEY)。
  - 樹準備抽共用,家本來就在修正關卡,r3 漏列的這一點已補上。
- 沒有發現需要另開節點的理由,也沒有跨家寫別人檔名的跡象。

不對齊共 12 條,其中 major 2 條

主要涉及的檔案:
- `/Users/enzo/harness/lumos-highrisk-evidence/scripts/lumos`
- `/Users/enzo/harness/lumos-highrisk-evidence/scripts/hooks/pre-push`
- `/Users/enzo/harness/lumos-highrisk-evidence/governance/review-reports/高風險測試證據加嚴/r4-snapshot.md`
