---
type: system
status: doing
created: 2026-10-06
updated: 2026-10-06
responsibility: 審查跑滿回顧:人裁紀錄(loop cap-decision)、跑滿回顧檔的骨架/驗證/記帳/跳過(loop retro)、跨迴圈彙整(loop retro-stats),以及五個呼叫端共用的合格回顧判定;不負責處置閘其他七步、canary record 其他寫側檢查、cap-hint 提示(那些歸 loop-convergence-recording)
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/system
  - status/doing
  - scope/loop-engineering
summary: |-
  WHY:[2026-10-05 [[Projects/審查跑滿回顧_計劃]] d6]要不要寫跑滿回顧看「人裁紀錄」,不看機械訊號:cap-reached 事件九、十月零筆,輪數超過上限會誤擋全折後派新席複核的例行輪(r3b),到上限那輪仍有 major 的多數其實已過閘;所以由人裁那一刻用 `loop cap-decision` 當場記(只收多席、2026-08-26 後開、非 light、帳上輪數已到上限) [test:t_cap_retro_decision_preconditions]
  WHY:[2026-10-05 d7]合格回顧綁最新一筆人裁紀錄:之後最新一筆是指紋相符且通過檢查的 recorded,或 skipped;跳過與回顧都只對它之前那筆人裁有效,再記人裁要重寫或重跳。處置閘第八步、canary record、loop next、doctor、retro-stats 五處共用同一支判定,任何一處另判就會口徑分岔 [test:t_cap_retro_gate_binds_latest_decision] [test:t_cap_retro_stats_aggregates_families]
  WHY:[2026-10-05 d7]讀治理帳直接讀原始 jsonl、依檔內順序、壞行跳過,以結構化欄位 loop 逐字比對;不經 gov 的載入器(它以提交與種類去重、保留第一筆,同一提交上兩次 --record 會折成舊的那筆)。寫帳用有回傳值的通用寫入器,寫不進去一律回 1、不印成功 [test:t_cap_retro_record_and_skip_write_gov_log]
  WHY:[2026-10-05 d2]回顧由沒參與這個迴圈的乾淨代理起草歸族、編排者補怎麼避免與行動項(編排者自己寫容易替自己的修法找理由);機器只驗得了起草者不是帳上審查席、不等於補完者,驗不了起草者真的沒看過編排者的看法 [test:t_cap_retro_check_rejects_each_defect]
  WHY:[2026-10-05 計劃〈一〉]不代建卷證資料夾:別處拿「資料夾在不在」判斷是不是暫存迴圈(處置閘的 intake 觀測、doctor 前掃滾動窗);沒有資料夾的迴圈記人裁照記,但不需要回顧 [test:t_cap_retro_out_of_scope_not_checked]
  WHY:[2026-10-05 計劃〈三〉2]凍結判定不涵蓋第八步:凍結兩趟與回放都印 —、不讀回顧檔,回顧檔也不進凍結閉包(它可能在凍結後補內容,進閉包會讓回放假紅);所以凍結存下的 rc 可能是 0,即使即時問閘第八步是 ✗(目前沒有程式拿凍結判定當放行依據) [test:t_cap_retro_out_of_scope_not_checked]
  PITFALL:[2026-10-06 實作時讀碼]處置閘的 roster 觀測尾端遇到席位異常會建卷證資料夾,而它跑在第八步之前——只看資料夾在不在,沒有卷證的迴圈問過一次閘、資料夾被建出來之後就會被誤判成要回顧;所以「有卷證資料夾」改成資料夾裡真的有這個編號帳上的席報告(`_retro_has_dossier`),帳讀不動時才退回只看資料夾(寧擋不放) [test:t_cap_retro_out_of_scope_not_checked]
  PITFALL:[2026-10-06 計劃〈實務隱患〉帳壞]審查帳不是 UTF-8 或某列輪次不是字串時,既有讀帳會冒解碼錯誤、分輪會冒 startswith 錯誤;新路徑(canary record 擋點、處置閘第八步、retro --template)各自接住、不丟堆疊,只對有人裁紀錄的迴圈擋(原因碼 cap-ledger-bad;出口是修帳,或最新人裁是 extra-round 時 --skip;最新人裁是 accept-risk 時 --skip 解不了,出口是修帳或改記 extra-round [test:t_cap_retro_accept_risk_ledger_bad_exit]);沒有人裁紀錄的迴圈維持原行為 [test:t_cap_retro_bad_ledger_fail_closed]
  PITFALL:[2026-10-06 代碼審 code-審查跑滿回顧 r1 四席]提示原本印 `lumos loop retro X --template > 回顧檔`,照貼時 shell 先把已寫好的回顧截斷清空、失敗還留 0 位元組檔;改成 `--template --write`(只在檔不存在時以 O_EXCL 建,已存在回 2 不動檔),過期時只叫人改好現有檔再 --record,所有提示與手冊都不再印重導向 [test:t_cap_retro_template_write_no_clobber]
  PITFALL:[2026-10-06 代碼審 r1 正確性、邊界席;r2;r3 架構對齊席]審查帳與治理帳寫入端不跳脫 U+2028/U+2029/U+0085,splitlines 會把含它們的一列劈開丟掉、輪數少算(人裁記不了、擋點把舊輪當新輪);切行只認 \r\n、\n、\r,走 _ledger_lines(r2 只接了三處,r3 把兩本帳其餘用 splitlines 的讀者——凍結回放、doctor、逃逸帳、loop list、verify-progress、代碼審留痕讀者等共 20 處——換掉,原始碼掃描守著;★不是所有讀者★:_drift_jsonl_iter 系與 _fix_check_events 仍只認 \n,r4 四席指出、本分支沒改,見 [[Issues/治理帳與審查帳其他讀寫函式的硬化缺口]]),跑滿回顧一族用既有讀法(_loop_records_checked),不另寫一套 [test:t_cap_retro_ledger_line_separators] [test:t_cap_retro_r2_cr_line_endings] [test:t_cap_retro_r3_ledger_lines_everywhere]
  PITFALL:[2026-10-06 代碼審 r1 併發席]治理帳檔尾缺換行(上次寫一半)時,新事件黏在半行後面、整行被讀側丟掉而指令回成功;通用寫入器追加前檔非空且末位元組不是換行就先補一個(帳尾檢查本身的寫法記在 [[Systems/reversibility-governance-ledger]]) [test:t_cap_retro_gov_tail_newline]
  PITFALL:[2026-10-06 代碼審 r1 併發、邊界席;r2 架構對齊席]回顧檔被換成管線或捷徑會讓讀檔卡住或跟隨到別處:讀回顧檔走既有 _regular_own_fd(不跟隨捷徑、非阻塞開檔、開檔後判一般檔),★不要求是自己的檔★(require_owner=False;共用機器或 CI 用別的帳號 checkout 時合格回顧不能被判過期);--record 驗與算指紋用同一份位元組 [test:t_cap_retro_fifo_symlink_not_read] [test:t_cap_retro_record_reads_once] [test:t_cap_retro_read_not_owner_ok] [test:t_cap_retro_r2_gov_not_regular]
  PITFALL:[2026-10-06 代碼審 r3 合約、併發、資安、邊界四席]r2 把讀治理帳改成不跟捷徑,寫端(通用寫入器 open(path, "a"))照舊跟捷徑:治理帳是捷徑時 cap-decision 回「已記人裁」,三個擋點卻讀不到、當成沒有人裁而放行;捷徑指到 repo 外時還會往外面追加。改成讀寫同一條規則 _retro_gov_path_err(走既有帳檔寫入前檢查 _drift_ledger_path_err:任一層符號連結、跑出 repo、不是一般檔、有別的硬連結 = 帳壞):寫端回 2 一個位元組都不寫;讀端 fail-closed——帳上已到上限、在範圍、有卷證的迴圈判 gov-bad 擋下(canary 擋下原因碼 cap-gov-bad,這筆不寫進治理帳),不到上限的迴圈記不了人裁、照常放行。只管跑滿回顧一族;其他閘仍跟隨捷徑讀寫(計劃〈誠實界線〉) [test:t_cap_retro_r3_gov_ledger_rule]
  PITFALL:[2026-10-06 代碼審 r1 邊界席;r2 邊界、併發席]孤立代理字元(不能編碼成 UTF-8 的字串)三種來源各自怎麼處理:①回顧檔內容 → --check 判型別不合格,retro-stats 與 doctor 每個迴圈各自 try、只標那一個;②帳上欄位(審查帳的 auditor/report_path 進 --template 的 context)→ context 印 null,--write 先把整份編碼成位元組再建檔、不留 0 位元組殘檔;帳上輪次(審查帳或最新人裁紀錄)不能編碼 → cap-decision 與 retro 回 2、不寫帳;③argv(編號、--note)→ 回 2、不寫帳。判法用既有 _fix_bad_strings(nul=False:只看能不能編碼,空字元不算;r3 收回另寫的一支);印到終端一律過 _esc_clean(已涵蓋孤立代理字元、雙向覆寫、C1);--template 的標準輸出與 --write 的檔把帳上帶來的 C1、雙向、行段分隔字元以 \uXXXX 跳脫(_json_text_escaped,類別用共用的 _PATH_SPECIAL_CATS;值不變,r3 資安席);治理帳三支寫入器遇到編碼錯誤都回「寫不進去」不丟堆疊 [test:t_cap_retro_surrogate_no_crash] [test:t_cap_retro_r2_unencodable] [test:t_cap_retro_r3_template_escapes] [test:t_cap_retro_r3_writers_portable] [test:t_cap_retro_r3_one_way]
  PITFALL:[2026-10-06 代碼審 r2 資安席;r3 架構對齊席]卷證資料夾本身是捷徑時,O_NOFOLLOW 只管最後一段檔名,--template --write 會在 repo 外建檔;r2 自寫的 realpath 檢查只看資料夾本身、上層是捷徑就放行。改成寫端、讀端、提示都問同一支 _retro_path_unsafe(逐層判走共用的 _repo_path_unsafe),卷證資料夾或上層是捷徑、跑出 repo → 不寫也不讀 [test:t_cap_retro_r2_write_symlink_dossier] [test:t_cap_retro_r3_write_path_shared_guard]
  WHY:[2026-10-06 代碼審 r2 通才、正確性、邊界席;r3 合約、通才、正確性、邊界、併發席]回顧不合格時叫人做什麼只由 _cap_retro_fix_cmd 一支決定,狀態對提示是一張表(函式說明裡):治理帳壞 → 換回一般檔;卷證資料夾或上層是捷徑 → 換成一般資料夾或 --skip;檔不在(含記過後被刪)→ --template --write;位置是資料夾、捷徑、管線 → 移除再 --template --write;讀不動、超過 256KB、空檔、建一半、不是 JSON 物件 → 刪除或改名再 --template --write;讀得動:過期 → 改好現有檔,沒記 → --check 再 --record。r2 只看 lstat 類型,讀不動或太大的檔叫人跑 --check、--check 又印同一句(繞圈);判「壞到要重建」與 --check 共用 _retro_parse。七個印提示的地方都呼叫它,每種狀態照做之後不會回到同一句;印給人照貼的指令由 _retro_cmd 組(編號 shlex.quote、整行 _esc_clean) [test:t_cap_retro_r2_prompt_no_deadend] [test:t_cap_retro_r2_one_way] [test:t_cap_retro_r3_prompt_table]
  PITFALL:[2026-10-06 代碼審 code-審查跑滿回顧 r4 架構、通才、正確性、合約席]上一輪為了讓 converged 也看得到人裁入口,在 [cap-hint] 另組一份記人裁指令,結果兩處各自決定:loop next 到 cap-reached 印兩次,治理帳壞或已記人裁時 [cap-hint] 還叫人去記(記了回 2)。改成只有 `_cap_retro_next_lines` 決定印什麼(治理帳壞只講判不了與出口、已有人裁改印回顧狀態、還沒有才叫人記),[cap-hint] 的「人裁:」那段就是它的輸出、只決定要不要叫人記;loop next 文字輸出不再另印 cap_retro(--json 欄位照留) [test:t_cap_retro_r4_cap_decision_single_source] [test:t_cap_hint_at_cap_shows_cap_decision]
  PITFALL:[2026-10-06 代碼審 r4 架構、通才、正確性、邊界、合約席]治理帳壞時 `_cap_retro_scan` 曾塞一筆假編號「(治理帳)」進迴圈清單,retro-stats 把它算成一個記了人裁的迴圈(totals.loops 被灌 1、人裁 ? 1)。改成回 (清單, 治理帳壞原因):retro-stats 另外報「治理帳讀不了」(--json 多 gov_error 欄)、doctor I2 另列一行,都不算進迴圈數 [test:t_cap_retro_r4_gov_bad_not_a_loop]
  PITFALL:[2026-10-06 代碼審 r4 併發、邊界席]治理帳是一般檔但讀不動(權限)時也判 gov-bad,出口原本只叫人「換回一般檔」,照做不會好。`_cap_retro_fix_cmd` 的 gov-bad 分支先看路徑規則過了、檔在、讀不動 → 改講權限 [test:t_cap_retro_r4_gov_unreadable_hint]
  PITFALL:[2026-10-06 代碼審 r4 資安席]帳上的輪次編號(canary record --round 不擋控制字元,版控的審查帳也能植入)在 [cap-hint] 每輪那行與處置閘 FAIL 橫幅原樣印到終端;印出前都過 _esc_clean [test:t_cap_retro_r4_round_id_escaped]
verified_by:
  - "[[Verification/2026-10-07_跑滿回顧因果證據銜接驗證]]"
---
# loop-retro

跑滿回顧(Projects/審查跑滿回顧_計劃 落地):多席審查迴圈到分級上限,人裁決定破例再開一輪(extra-round)或接受剩下的風險(accept-risk)時記一筆人裁紀錄;有人裁紀錄、又有卷證資料夾的迴圈,繼續之前要留一份固定格式的回顧或記跳過。

- 指令:`loop cap-decision`(人裁紀錄)、`loop retro --template|--check|--record|--skip`(回顧檔 `governance/review-reports/<編號>/cap-retro.json`)、`loop retro-stats [--json]`(以迴圈為單位彙整)。三種事件都記在治理帳,閘名 loop-retro(kind:cap-decision / recorded / skipped),不在 design-loop、code-loop 兩個閘底下,不影響 loop list 的關門判定。
- 擋點與提醒:canary record 記人裁之後的新一輪、處置閘第八步、loop next 判到 cap-reached 多印的幾行、doctor 的 I2 段(只提醒)。前兩個怎麼接進既有流程寫在 [[Systems/loop-convergence-recording]]。
- 擋不到的路(計劃〈誠實界線〉):到上限沒記人裁就繼續或結束、整份重寫開新編號;人裁 accept-risk 之後直接結束的只有 doctor 列出。
- 起草派工詞在 lumos-design-loop 的 templates.md §9;五處到頂句與指令速查都接到人裁與回顧指令。
