---
type: project
status: doing
created: 2026-09-29
updated: 2026-09-29
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/存量漂移守衛
  - Systems/guard-kill
  - Systems/lumos-cli-write
related:
  - "[[Projects/存量漂移防線_計劃]]"
---
# 存量漂移改法_計劃

白話:存量漂移健檢(`lumos drift scan`)現在只會「指出」過期的句子,改要人自己動手。rtb 2026-09-29 照清單修的時候,28 筆裡有 24 筆工具沒有路可走,只能留著。這份計劃補「改法」:一個指令 `lumos drift fix`,依發現的種類給現成的改法;另外補兩個結案時的漏洞(結案 Issue 的回頭條件、c2 表態會蓋掉之後的新情況)。

依據:Enzo 2026-09-29 裁「現在開始」(原排 10/13 決定);缺口清單出自 rtb 會談實測回報,記在 [[Projects/存量漂移防線_計劃]]〈修復結果〉。

PRIOR-ART: 最小解在工具鏈自己這一層。①c1 的改句邏輯現成(`_guard_settle_rewrite`,guard settle 第二步),rtb 會談直接呼叫它,7 篇全改對——只差入口;「已 pass 但預告句還在」是新狀態,不是既有的「pending 做到一半補完」,本計劃新加。②外面的做法:lint 工具的 `--fix`(ruff、eslint)是「偵測與改法同一條規則、改法只做機械確定的、其他只提示」,本計劃照這個分:c1 自動改、c3 改狀態加一行、c4 只給證據、由人給要換的片段。③表態帶「當時的關係清單」借 ADR 的 superseded 鏈:決定綁著當時的前提,前提變了決定不再自動適用。④git 查詢借既有做法:`_nodehome_git`(有逾時、回位元組要解碼)已經用 `git log -S`(每支檔有家的上線點),c1 的 `-G` 查詢照同一支;c4 的「第一次提交」直接用既有的 `_plan_first_commit`(`git log --diff-filter=A`,它的說明寫了為什麼不信開頭欄位的 created),不另寫一支。
RETIRE-IF: 上線兩個月後任一成立就撤掉或重想:①修復帳 `governance/drift-fixes.jsonl` 在工具鏈與 rtb 合計不到 5 筆(大家寧可手改,入口沒價值;機械數:兩邊各 `wc -l`);②c1 改過的筆記,事後被人再改那幾行的比例超過兩成(改法不對;人工量:對修復帳每筆 c1 的路徑跑 `git log --since=<修復日> -p -- <路徑>` 看改句那幾行有沒有再動);③c4 在修復帳裡照抄證據範本(帳上 `template_used: true`)的不到一半(證據不準)。
REVISIT:2026-11-28 跟 [[Projects/存量漂移防線_計劃]] 的 RETIRE-IF 一起量上面三個數

## 範圍

- **做**:①`lumos drift fix <節點> <行號> --kind <種類>`:c1、c3、c4 三種有改法,其他種類說明沒有改法、指到 `drift ack` 或 `guard settle`;②c1 補改預告句(轉正日期從守衛紀錄的歷史推、跟手補的「已轉正」段不疊、家節點沒有正式行的不改);③c3 改狀態並在正文加一行;④c4 列出證據與範本,由人給「原片段、新片段」精確替換;⑤`guard settle` 對「pass 但預告句還在」補做改句,`--test` 改選填、多一個 `--date`;⑥doctor E5 對已結案 Issue 的到期回頭條件標出「這篇已結案」,`lumos set` 把 Issue 改成結案狀態時列出它還留著的回頭條件;⑦c2、c3 的表態記下當時連著的已收尾計劃,之後多了新的收尾計劃就重新列出;⑧修復帳:每改一筆記改前整篇與改後指紋,退得回去;⑨提示文字改成指到新指令(drift check 擋下時、drift scan 每種發現的建議、drift ack 的提示)。
- **不做**:c2、c5 的自動改法(c2 要人判 Issue 解決沒;c5 已有 `guard settle` 重跑);改 drift check 的判定規則;rtb 那 24 筆由 rtb 會談用新指令修(本計劃只負責工具)。

## 做法

### 1. `lumos drift fix` 入口與寫入順序

- 語法:`lumos drift fix <節點> <行號> --kind <種類> [--dry-run] [種類專屬參數]`。`--kind` 接受全部種類(同 `drift ack` 的 choices=_DRIFT_KINDS),c2、c5 與其他沒有改法的由函式回 2 並印該走的指令(`drift ack`、`guard settle`)——不在 argparse 那層擋,那層印的是用法訊息。
- 順序(每一步失敗都回 2、印原因,前一步已寫的照下面規則處理):
  1. **鎖外先做只讀的準備**:c1 查 git 推轉正日期(第 2 節)、c4 查證據(第 4 節)。放在鎖外,因為寫入鎖 30 秒沒放就被當成死鎖接手(`_VAULT_LOCK_STALE_SEC`),git 在大 repo 可能超過。參數與種類不合(例:`--kind c3` 卻給 `--old`、c1 給 `--by`)、`--date` 格式錯,在這一步就回 2。
  2. **拿筆記庫寫入鎖**(`_vault_write_lock`,可重入)。
  3. **鎖內從磁碟重讀那一篇並重新解析**:讀檔後用 `_note_from_text` 重建那一篇的筆記物件、換進 env(`_drift_state_findings` 的 status、type、plan_refs、valid_under 都讀筆記物件的開頭欄位,只重讀正文不夠),再用 `_drift_state_findings` 重判,確認指定的行現在確實是這一種發現(c1 的 line 是檔案行號,c3、c4 是 `_drift_field_line` 找到的欄位行);不是就回 2、不寫,訊息講「這一行現在不是 <種類>:可能已經被修掉(c1 一次改整篇),重跑 drift scan 看最新清單」。兩個會談同修一篇時,第二個會在這一步停下。
  4. **算出改後內容**,`--dry-run` 印改前改後就回 0,不寫筆記也不寫帳。
  5. **寫筆記**:`atomic_write_verify`。它的自驗只看開頭欄位,所以寫完再從磁碟重讀、同第 3 步重建筆記物件、用同一支判定確認那一筆發現已經不在;★不在才算成功,還在就把改前原文寫回去(原子寫入),回 2★——自驗失敗時檔案已經落盤,不能只報錯。
  6. **寫修復帳**:往 `governance/drift-fixes.jsonl`(常數 `_DRIFT_FIXES`,跟 `_DRIFT_ACKS` 放一起)追加一行(`_jsonl_append_verified`,同表態檔):`id`(`DFIX-` + 8 碼)、`path`(repo 相對,同表態檔的 path)、`line`、`kind`、`date`、`before`(改前整篇原文)、`after_sha256`(改後整篇的指紋)、`via`(`drift fix` 或 `guard settle`)、c4 另記 `template_used`。★帳寫不進去就把筆記還原成改前原文、回 2★:筆記改了、帳上沒有,事後就找不回來。成功後記一筆治理事件(閘名 `drift-fix`,同 `drift ack` 記事件的方式),並印「修復帳要跟筆記一起提交」。
- 修復帳進簿記檔名單 `_BOOKKEEPING_FILES`(同表態檔):它是人對發現的處理紀錄,不是程式改動,提交它不應讓代碼審留痕失效、不應被當成程式改動擋推送。帳檔跟筆記一起進版控;多個工作樹各自追加、合併時兩邊都加了行,照既有的 JSONL 聯集合併做法處理(`_pull_source_or_abort` 對簿記 JSONL 取聯集),跟治理帳、表態檔同一種風險與解法。
- 分派:`drift` 子命令現在「不是 scan 就當 ack」,加 fix 要改成明確分三支,不然 fix 會被當成 ack 執行;`_CMD_HELP` 的 drift 說明與 argparse 的 help 一起補。

### 2. c1:已 pass 的守衛紀錄補改預告句

- 前提檢查(第 1 節第 3 步內):守衛紀錄要讀得出 `預告的合約:` 那一行(讀不出回 2,說明被手改過);家節點(守衛紀錄指名的功能節點)現在的摘要裡,要真的有這條合約的正式行(`_guard_formal_line`,不限測試名);沒有就回 2,說明兩條出路:「這條合約其實還沒轉正——把 status 改回 pending 後走 guard settle」或「正式行寫在別處——手動改句後對剩下的 c1 用 drift ack」。不指到 `guard settle` 本身(pass 節點走 settle 也會碰到同一個檢查)。不然會把「已轉正、由正式合約行守」寫進一篇根本沒轉正的紀錄。
- 改法:`_guard_settle_rewrite` 改整篇(同一篇的四種預告句是一組,只改一句會留下自相矛盾的半套;改完那篇的 c1 全部消失,不會有「改了一句、下一句行號位移」的問題)。
- 轉正日期(只有這次改寫真的要寫日期時才推——TEST、WHY 兩句與換成「(日期 已轉正)」的 settle 句要日期;只改「為什麼還不做:」或 settle 句因手補段而刪掉時不推,推不出也不擋),依序:
  1. `--date YYYY-MM-DD` 有給就用(格式錯回 2)。
  2. 守衛紀錄自己的歷史:`git -c core.quotePath=false log --reverse --format=%H%x09%as -G "^status: pass" -- <守衛紀錄>`(路徑用 git 列出的原樣,NFC/NFD 照每支檔有家的既有做法),逐筆讀那個提交的那一篇,第一筆 status 是 pass 的,取它的日期。`guard settle` 轉正時同一次寫入就把 status 改成 pass,所以這一筆就是轉正那天。★不用 `git log -S <合約文字>`★:settle 是把預告行原地換成正式行,合約文字出現的次數不變,`-S` 只列次數有變的提交,永遠找不到轉正那次(設計審 r1 四席各自報到,編排者重現:-S 只找到預告那次、-G 才找到轉正那次)。
  3. 推不出來(沒有這樣的提交、repo 是 shallow(`_git_is_shallow`)、守衛紀錄改過名)就回 2,要人給 `--date`;不拿今天充數(rtb 的 F1–F3 實際轉正在 2026-09-23,用今天會寫錯歷史)。
- 跟手補的段不疊(新行為,現在一律替換):改寫「做完之後跑 lumos guard settle 轉正」那句時,往下跳過空行,下一個非空行如果符合 `^\(?\d{4}-\d{2}-\d{2}\)? ?已轉正` 就刪掉這一行(連同它後面緊接的一個空行,避免留兩個空行),不換成「(日期 已轉正)」(rtb F4–F7 當時人手補過)。因手補段而刪掉的 settle 句算「處理過」,不進 `missing`(不然會多印一行誤導的「找不到」)。`_guard_settle_rewrite` 現在是逐行一對一輸出,改成可以刪行;settle 與 fix 共用這一支。
- 找不到的句型照 settle 現在的做法印提醒(`missing`),不當錯誤。

### 3. `guard settle` 對 pass 節點

- 現在:pass 一律印「已轉正,不用再做」回 0。改成:還有預告句就走第 2 節同一支(日期規則、前提檢查、不疊、修復帳 `via: guard settle`);沒有預告句照舊。這是新行為,不是既有的「做到一半補完」(那個指家節點已是正式行、守衛紀錄還 pending)。
- 參數:`--test` 從必填改成選填——pending 沒給就回 2(訊息同現在必填時的說明);pass 補改句用不到,給了也不檢查。現在 `cmd_guard_settle` 一開頭就驗測試名合法(`IDENT_RE`),要挪到讀完狀態、確定是 pending 之後;pass 補改句的成功訊息不印 `[test:…]`。新增 `--date YYYY-MM-DD`,給 pass 補改句用;pending 轉正照舊用今天(那一刻就是轉正日)。推不出日期時訊息指到 `--date`,不是死路。

### 4. c3 與 c4

- **c3**:參數 `--status`(必填)、`--by <節點>`(選填)。合法值是驗證紀錄的合法狀態扣掉 pending——把 `cmd_lint` 裡的類型狀態表抽成模組層常數(`_TYPE_STATUSES`),lint 與 fix 共用,不另寫一份。寫入:status 用 `edit_fm_scalar` + `edit_fm_sync_status_tag`(同 `cmd_set`);正文最後加一行「YYYY-MM-DD 狀態改為 <值>(存量漂移 c3)」,有 `--by` 就接「,由 `[[<節點>]]` 解決」;`--by` 找不到回 2。原本的正文不改(歷史說法保留)。
- **c4 不帶改寫參數**(`--dry-run` 同):列證據與範本,回 0 不寫——①那篇驗證紀錄第一次被提交的提交編號(`_plan_first_commit`;改過名的只看得到改名後那次,寫進界線);②`governance/review-reports/` 底下目錄名含那篇 plan_refs 計劃名(去 `_計劃`、NFC、不分大小寫、`.` 與空白轉連字號)的卷證目錄;③範本句「提交 <sha>;代碼審見 <卷證>」。查不到的項目寫「查不到」;筆記還沒提交(①查不到)照樣列②③;shallow 時①寫「shallow,查不到最早提交」。
- **c4 帶 `--old "<原片段>" --new "<新片段>"`**:在 valid_under 的每一項裡找 `--old`,★全部項目合計要剛好出現一次★(零次或好幾次都回 2,並列出每一項讓人挑更長的片段);換掉那一段,其他項目與同一項的其他文字一字不動。寫入借既有的 `_set_conditions_locked` 的寫法(它已經處理單行、清單、空的、多行區塊四種寫法,並擋空值與換行),但那支自己讀檔、寫入、印「✓ set」,不能直接呼叫——拆出「給舊的行、回新的行」那一段(`_conditions_rewrite`),set 與 fix 共用;寫入、驗證、還原、記帳照第 1 節的順序走。新值清單的項數與原本相同。換完那一項還含「未提交/還沒提交/uncommitted」就回 2(會立刻再被列出),提示改用 `drift ack`。`--new` 跟範本句一樣時修復帳記 `template_used: true`。

### 5. 結案 Issue 的回頭條件

- doctor E5:到期清單裡,來源筆記是 Issue(type: issue)而且 status(用 `_drift_str` 讀,防清單值)在 `QUERY_CLOSED_STATUSES` 的,那一行後面加「(這篇 Issue 已結案)」;照樣列、照樣計數。只標 Issue:已收尾的計劃常刻意留著撤除用的回頭條件(例:[[Projects/兩席相反時端出張力_計劃]] 已收尾,還留著之後才到期的 REVISIT),標上「已結案」反而讓人以為可以刪;驗證紀錄 pass 是「現在成立」,不是結案。
- `lumos set <Issue> status <值>`,那篇是 Issue、值在 `QUERY_CLOSED_STATUSES`(set 不驗類型值域,所以要同時看類型;對 Issue 實際會用到的是 done、resolved、wontfix):改完之後,用跟 E5 同一套判定(`_search_visible_lines` 剝程式碼區,餵 `_strip_inline_markup` 之後的 `_revisit_split`;圍欄與行內程式碼裡的範例不算)列出這篇還留著的回頭條件(行號加原文),提示「結案了,這幾行要改成結案說明或刪掉」;只印、不擋、不改。實作成一支新函式 `_issue_close_revisits`,在 main 分派處 `cmd_set` 成功之後呼叫(跟計劃收尾的 `_drift_print_followups` 同一個位置,但不塞進 `_drift_plan_followups`——那支的合約是「計劃連著哪些別的筆記」)。行號用 `cmd_set` 寫完之後從磁碟重讀的內容算。

### 6. c2、c3 表態綁當時的關係

- `drift ack --kind c2|c3`:寫入前先用 `_drift_state_findings` 算那一篇當下的發現,指定的行要真的是這一種發現,不是就回 2(說明「這一行現在不是 c2/c3,不用表態」);是就多記 `related`:那筆發現列出的已收尾計劃(排序、NFC、圖譜內相對路徑,跟發現物一樣)。其他種類照舊。
- 比對(`_drift_split_acked`),同一個鍵(路徑+原文+種類)可能有好幾筆表態:★以最新一筆為準★(表態檔只追加不改,後寫的蓋前寫的)——最新一筆沒記 `related` 就照舊對得上;記了就要它涵蓋現在的清單(現在的是它的子集)才算已表態;`related` 不是字串清單(手改壞了)當成沒涵蓋、重新列出。沒涵蓋就重新列出,說明印「這篇以前表態過(最近一次當時連著 X),現在多了 Y;最近一次理由:…」。舊理由用一支新的「同路徑、同原文、同種類,取最近一筆」查找,不借 `_drift_old_reason`(它為了分辨改名,原路徑還在就跳過)。
- 舊表態:最新一筆沒記 `related` 的照舊對得上。實作收尾時,對工具鏈 2026-09-29 那 17 筆 c2 表態各重跑一次 `drift ack`(同理由)——新寫的那筆帶 `related`、而且是最新一筆,所以這批已知案例從此受新規則保護;rtb 那 2 筆由 rtb 會談自己補。
- 行號移位:表態本來就不綁行號(比的是路徑+原文+種類),寫一條測試釘住「同一篇上面插幾行,表態照樣對得上」。

### 7. 提示與同步

- 提示改成指到新指令:`drift check` 擋下時「預告句那幾筆」那段(現在教人手改,改寫)、`drift scan` 的輸出(現在沒有下一步建議,新增:c1/c3/c4 每筆印 `lumos drift fix <節點> <行號> --kind <種類>`)、doctor Z 段的建議。
- 同步改的筆記與文件:Systems/存量漂移守衛(drift fix、修復帳、表態綁 related)、Systems/guard-kill(settle 對 pass 的新行為、`--test` 選填、`--date`)、Systems/lumos-cli-write(set 把 Issue 結案時列回頭條件)、[[Projects/存量漂移防線_計劃]] 的〈修復結果〉缺口段標成「已由本計劃處理」並撤掉那條 10/13 的 REVISIT;lumos-project-notes 的指令文件:`commands/` 底下沒有存量漂移專檔,drift 家族在 04 只有 drift-history 一列——在 04 補 drift check/scan/ack/fix 各一列、INDEX 補一行、06 的 guard settle 那列拿掉「--test 必填」、reference.md 的子命令全覽補 fix;Systems/存量漂移守衛 的 responsibility 那行補 fix。
- 要跟著改的既有測試:`t_guard_settle_rewrites_planned_prose`(斷言 settle 句整行換成「已轉正」,手補段那種情況改成刪行)、`t_guard_settle_recovers_half_done`(斷言 pass 印「已轉正」回 0,改成「沒有預告句時」才這樣)。

## 條款

- [S1] 當 `lumos drift fix` 指定的行在鎖內重讀後不是那一種發現,工具應擋下回 2、不寫任何檔;c2、c5 與其他種類應回 2 並指到 `drift ack` 或 `guard settle` [test:t_drift_fix_refuses_wrong_kind]
- [S2] 當 c1 修一篇已 pass 的守衛紀錄,工具應改寫四種預告句、日期取 `--date` 或守衛紀錄第一次變成 pass 的提交日期;推不出日期或 repo 是 shallow 時擋下、不用今天;家節點沒有正式合約行時擋下;下一個非空行已是手補的「已轉正」說明時應刪掉 settle 句而不疊一行 [test:t_drift_fix_c1_rewrites_with_commit_date]
- [S3] 當 `guard settle` 遇到 pass 但還留著預告句的守衛紀錄,工具應用同一支補改(同 [S2] 的日期、前提與不疊規則),不需要 `--test`、接受 `--date`;沒有預告句時照舊回 0 印「已轉正」;pending 沒給 `--test` 應擋下回 2 [test:t_guard_settle_pass_completes_prose]
- [S4] 當 c3 修一篇驗證紀錄,工具應只收合法狀態表裡驗證紀錄扣掉 pending 的值、改 status 並同步標籤、在正文最後加一行狀態說明(有 `--by` 時帶連結),`--by` 找不到時擋下;原本的正文不改 [test:t_drift_fix_c3_sets_status_and_note]
- [S5] 當 c4 沒帶改寫參數,工具應只列出證據與範本、不寫檔;帶 `--old`/`--new` 時,`--old` 在全部項目合計剛好出現一次才換、只換那一段,其他項目與文字一字不動;零次或好幾次、換完仍含那三個詞時擋下 [test:t_drift_fix_c4_evidence_then_replace]
- [S6] 當 doctor E5 列出到期回頭條件,來源是已結案 Issue 的那幾行(在顯示上限內的)應標「這篇 Issue 已結案」,照樣列出與計數;其他類型不標 [test:t_doctor_revisit_marks_closed_issues]
- [S7] 當 `lumos set` 把 Issue 改成結案狀態,工具應用 E5 同一套判定列出它還留著的回頭條件行(程式碼區與行內程式碼裡的不算),不擋不改 [test:t_set_issue_closed_lists_revisits]
- [S8] 當 c2 或 c3 表態,工具應先確認那一行當下是那一種發現,記下當時的已收尾計劃清單;同一個鍵有好幾筆表態時以最新一筆為準——沒記清單照舊對得上,記了要涵蓋現在的清單才算,清單壞掉或沒涵蓋就重新列出並印那一筆的理由;同一篇行號移位不影響表態 [test:t_drift_ack_binds_related_plans]
- [S9] 所有寫入應在筆記庫寫入鎖內、從磁碟重讀後重判、原子寫入,寫完重讀並確認那一筆發現已不在,不在才寫修復帳;重讀驗證失敗或修復帳寫不進去時應把筆記還原成改前原文並回 2;`--dry-run` 不寫檔也不寫帳;修復帳在簿記檔名單裡 [test:t_drift_fix_dry_run_lock_and_ledger]
- [S10] 當 drift check 擋下或 drift scan 列出 c1/c3/c4,訊息應指到 `lumos drift fix` 指令,不再教人手改;`lumos drift fix` 應走自己的分派,不被當成 ack [test:t_drift_hints_point_to_fix]

## 回退

- `drift fix` 是新指令:回退就是拿掉子命令與三支改法函式,既有指令不受影響。已經用它改過的筆記:修復帳每一筆都有改前整篇原文,c1、c3、c4 都能逐筆寫回(寫回前比對 `after_sha256` 跟現在的檔一樣,不一樣表示之後又被改過,要人判)。
- `guard settle` 對 pass 的新行為:回退成原本的「已轉正,不用再做」一行、`--test` 改回必填、拿掉 `--date`。已經補改的筆記是「預告句改成歷史說法」,不用還原;要還原照修復帳(`via: guard settle` 那幾筆)。
- E5 標記與 set 的列出:純多印,回退就是拿掉那幾行印出。
- c2/c3 表態的 `related`:回退時比對忽略這個欄位即可(舊行為);已寫的欄位留在表態檔裡無害(`_drift_load_acks` 整行原樣回傳、下游只取 path、text、kind、reason)。
- 修復帳檔案本身:回退後留著無害;若也要拿掉,同時從 `_BOOKKEEPING_FILES` 移除。

## 實務隱患

- **資料正確性(碰到)**:c1、c3、c4 會改筆記內容。防法:只改認得的句型或人指定的片段,其他一字不動;鎖內重讀後重判;`--dry-run`;寫完重讀驗證,失敗還原。
- **歷史日期(碰到)**:c1 的轉正日期寫錯會改寫歷史。防法:從守衛紀錄變成 pass 的提交推;推不出、shallow 就擋,不拿今天。
- **併發(碰到)**:多個會談同時修同一篇,或同時追加修復帳與表態檔。防法:git 查詢放鎖外、寫入在鎖內且鎖內重讀重判;帳檔用 `_jsonl_append_verified` 追加後讀回自驗(同表態檔)。
- **自我治理(碰到)**:改的是漂移健檢的表態比對,放寬會讓該列的不列。防法:[S8] 只有「沒記清單的舊表態」照舊放行,新寫的一律帶清單,今天那 17 筆也補上(補的那筆是最新一筆)。
- **向後相容(碰到)**:表態檔多一個欄位、多一個修復帳檔。舊版 lumos 讀表態檔不會壞(整行原樣回傳、下游只取四個鍵);但舊版寫的新表態不帶 `related`,而且以最新一筆為準——舊版在新版之後又寫了一筆,會蓋掉帶清單的那筆,新保護對它不生效,只能靠升級。
已排除:金流:只改圖譜筆記與帳檔,不碰任何金額或付款流程
已排除:對外送出:不寄信、不打外部服務,只讀本機 git
- 不可逆(碰到,可還原):改的是版控裡的筆記,git 還原得回來;修復帳逐筆存改前原文,不靠 git 也找得回來
- 效能(不碰):一次只修一篇;c1 的 git 查詢限定守衛紀錄一支檔,放在鎖外

## 誠實界線

- c4 的卷證目錄是用名字比對猜的,可能漏或多;所以只提議、不寫入。
- c1 的日期看守衛紀錄第一次變成 pass 的提交:守衛紀錄改過名(`git log` 不跟改名)、或當時人手改 status 再另外 settle,推出來的日子會不對或推不出,這種要人給 `--date`。日期取作者日期(`%as`),推送前把好幾個提交壓成一個時,是壓成的那一筆的作者日期(通常是第一個提交那天),可能比實際轉正早一兩天。
- c4 的「第一次提交」:驗證紀錄改過名的,只看得到改名後那一次。
- c2 表態的 `related` 存的是路徑:連著的計劃改名後,清單裡是新路徑,會被當成「多了新計劃」重新列出(誤報,方向是多列不是漏列);重新表態一次就好。
- c2 的 `related` 只記「哪幾篇」,不記它們當時的狀態:同一份計劃重新打開、又再收尾一次,清單不變,舊表態照樣算數。這種情況靠 Issue 本身的回頭條件兜底。
REVISIT:2026-11-28 看修復帳與表態檔,有沒有計劃重開又收尾而 c2 表態沒重新列出的案例;有的話表態改記計劃當時的狀態與日期
- E5 只標已結案的 Issue:已結案計劃留著的過時回頭條件照樣唸、沒有標記,靠計劃收尾時的連帶待辦處理。
- 舊版與新版 lumos 並存時,舊版寫的表態不帶清單,新規則對它們不生效。

## 合約候選

(設計審過閘後填。)

## 審計修正紀錄

- r1(2026-09-29,7 席:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet 5.5;外家否決 Codex;前置掃描已跑):61 條,major 25 條(機器數各報告的 F 標題與 severity 行);引句除邊界席一句太短外全數錨定。卷證在 `governance/review-reports/存量漂移改法/r1-*`。
  - 折入(全數):轉正日期改看守衛紀錄第一次變成 pass 的提交,不用 `git log -S`(正確性 F1、邊界 F1、併發 F1、外家 F1;編排者重現);c1 前先確認家節點有正式行(正確性 F2);c4 改成 `--old/--new` 精確替換、全部項目合計剛好一次、寫入走既有 `_set_conditions_locked`(正確性 F3 F4、邊界 F3 F4、外家 F3、架構對齊 F2);修復帳進簿記檔名單、存改前整篇、先寫筆記驗證再寫帳、帳失敗還原筆記(接手 F1、回滾 F1 F2 F3、架構對齊 F1 F7、外家 F5 F6、併發 F4);鎖內重讀重判、git 放鎖外(接手 F4、併發 F2 F3、邊界 F6);自驗失敗還原(外家 F2);`drift ack` 先確認當下發現、多筆表態任一涵蓋就算、今天 17 筆補 related、路徑 NFC(接手 F3、邊界 F2 F7、併發 F6、正確性 F6 F7、架構對齊 F9);同計劃重新收尾寫進界線並加 REVISIT(外家 F4);提示改指 drift fix(正確性 F9、接手 F2、邊界 F11);結案列回頭條件用 E5 同一套判定、新函式不塞進計劃連帶待辦(架構對齊 F4 F5、正確性 F11、接手 F7、併發 F5);E5 只標 Issue(正確性 F8、邊界 F10);settle 加 `--date`、`--test` 語意(正確性 F5、接手 F5、邊界 F5);合法狀態表抽成常數共用(架構對齊 F6);git 查詢借 `_nodehome_git` 與既有 `-S`/`--diff-filter=A` 用法(架構對齊 F3);c4 證據空結果與 shallow(邊界 F8);手補段判準與刪行版面(邊界 F9);同步清單與 RETIRE-IF 的量法(接手 F8 F9);回退與實務隱患的舊說法(回滾 F4 F5 F6、架構對齊 F8、外家 F7、正確性 F10、邊界 F12);一篇改完整篇、不會行號位移(接手 F6);寫入失敗處理(架構對齊 F10)。
  - 鏡像核對(便宜席,材料含席報告目錄):61 條已處理 43、部分 16、未處理 0、相反 2;新矛盾 6。已補:表態比對改成「以最新一筆為準」(原寫「任一筆沒記清單就算」跟補 17 筆的做法打架,邊界 F2 要的方向相反);鎖內重讀要重建筆記物件(只重讀正文,開頭欄位還是舊的);c1 前提失敗的出口不指回 settle;c4 寫入拆出 `_conditions_rewrite` 共用、不直接呼叫會自己寫檔的 `_set_conditions_locked`;PRIOR-ART 的 git 先例說法更正、c4 首次提交改用 `_plan_first_commit`;drift 分派要分三支、`_CMD_HELP`、doctor Z 段;scan 的建議是新增不是改寫;commands/ 沒有存量漂移專檔,改列要補的三檔;c1 只在要寫日期時才推;參數與種類不合回 2;手補段刪掉的 settle 句不進 missing;settle 的測試名檢查挪後、成功訊息不印 test;set 列出要同時看類型是 Issue;E5 讀 status 用 `_drift_str`、標記只斷言顯示上限內;修復帳常數名、治理事件、提示提交、多工作樹合併;要跟著改的兩支既有測試;界線補壓提交的日期、改名後的首次提交、計劃改名造成的 c2 誤報。
