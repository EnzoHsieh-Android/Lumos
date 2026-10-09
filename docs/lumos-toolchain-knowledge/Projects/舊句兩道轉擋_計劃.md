---
type: project
status: doing
created: 2026-10-09
updated: 2026-10-09
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/存量漂移守衛
  - Systems/筆記內容審
  - Systems/bound-tests-gate
related:
  - "[[Projects/守檔筆記對照改動_計劃]]"
  - "[[Projects/舊句檢查_計劃]]"
  - "[[Projects/漂移防治路線圖_計劃]]"
---
# 舊句兩道轉擋_計劃

白話:程式改了、筆記前面的舊句沒人回頭改,是防筆記過期最弱的一環。現有兩道只提醒:名稱消失檢查(推送範圍裡被刪或改名的 Python 名稱、旗標、檔案路徑,筆記還在提)與回頭重讀守檔筆記(程式和管它的筆記這次都改了,提醒交給判定者整篇重讀)。本計劃把兩道都改成預設擋。

## 原問題與範圍

- Enzo 2026-10-09 裁:不等兩週量測,直接擋(原話「我想直接擋,多檢查一次沒有損失吧」);重讀選「兩層都擋」(沒跑判定擋;判定點出的規則類行沒處理擋)。
- 擋之前的帳(主線 `docs/.governance-log.jsonl`,2026-10-09 數):回頭重讀 reminded 18 次、recorded 5 次、none 12 次——提醒之後真的去跑判定並記錄的不到三成,提醒形同虛設,是改擋的主因。名稱消失檢查 35 次全是 passed,而且 35 次的候選數都是 0:它在生產上從沒命中過,改擋的誤報率沒有任何實測,只能靠上線後的 RETIRE-IF 抽樣。
- 做:①名稱消失檢查 `drift_check.old_sentence` 沒寫時照總開關 `drift_check.gate`(總開關預設本來就是 block);②回頭重讀 `note_reread.gate` 沒寫與各種壞設定時改成 block,而且 block 真的會擋;③重讀擋兩層(定義見〈設計〉);④`lumos drift ack` 多一種 `--kind reread`,綁點出那一行的判定紀錄;⑤推送前掛鉤與 CI 照回傳碼擋(CI 只擋第二層與判不了,見〈設計〉);⑥被這次改動弄成說謊的筆記條款、手冊、說明文字一起改(清單見〈設計〉);⑦`LUMOS_VERSION` 升 v1.3、CHANGELOG 加同版一段;⑧既有測試裡釘「不擋」的斷言改成新行為。
- 不做:推送當下呼叫模型(判定仍由編排者派,閘只讀已提交的紀錄);擴大重讀範圍到「這次沒改的家筆記」(另案,成本要先量);非規則類行的判定結果仍只提醒;改對照指紋的組成;替消費專案的 CI 加 reread 步驟(`lumos update` 帶不到 CI,消費專案只有本機掛鉤這一道,另案)。

PRIOR-ART: ①最小解在既有層——重讀已有範圍計算、對照指紋、判定紀錄與預留的 `note_reread.gate`(寫 block 時印「轉擋還沒做」);名稱消失檢查已有 `drift_check.old_sentence` 三值開關,而「子開關沒寫照總開關」有 `_drift_retire_config` 的先例;照留表態已有 `drift ack`,「表態綁當時的證據」有 c2、c3、c6 綁 related 與 seq 的先例(`_DRIFT_BOUND_KINDS`、`_drift_split_acked`);「判不了」的提示有 `_drift_unknown_hint`;判定拆三段有 `_drift_m1_guarded`、`_drift_retire_guarded` 的先例;規則類行的判斷用既有的 `INVARIANT_RE`、`_notelines_regions`、`_ns_summary_logical`。第二層是新的小機制(讀已提交判定紀錄內容、比對引句、比對表態),零件都用既有的。②世界解過——Swimm 的 code-coupled docs 在合併前把「引用的程式改了、文件沒更新」標成失敗;本案第一層等於同一件事,判斷交給已提交的判定紀錄。③借用:擋規則類行照 [[Projects/守檔筆記對照改動_計劃]]〈做法〉5 寫好的轉擋起點建議(實驗二這類行 6 行裡 5 行是真問題;那份計劃標明這是起點建議、樣本只有 6 行,本案照人裁採用)。

RETIRE-IF: 上線後 8 週內任一成立就把該道的預設改回 warn(設定一行、不刪程式):重讀第二層 blocked 事件記下的規則類行裡,抽樣人工判誤報超過一半;或 `note-reread` 的 skipped-env 事件(`LUMOS_SKIP_REREAD_CHECK` 單次略過)累計 3 次以上;或名稱消失檢查記成要處理(must)的發現裡,抽樣人工判誤報超過一半(`drift-check` 的 skipped-env 不分子檢查,累計 3 次以上時逐筆人工看是不是為了舊句才略過)。

## 設計

### 開關

- **名稱消失檢查**:`_drift_old_sentence_config` 改照 `_drift_retire_config` 的寫法:`old_sentence` 沒寫、寫 null、值看不懂 → 照總開關 `drift_check.gate` 的值(總開關沒寫是 block;總開關 off 時 m1 照 retire 的先例也不跑);讀不成 JSON、`drift_check` 不是物件、整份設定不是物件 → block,各講一句「照預設 block」;寫 warn、block、off 照原義。連帶改:`_drift_config` 說明、`drift check` 的 `--help`、doctor 舊句檢查提示行(`_drift_old_sentence_doctor_lines`)。這會作廢 [[Systems/存量漂移守衛]] 那條「m1 沒寫是 warn、不跟 gate 走」的 RULE(Enzo 2026-10-09 人裁翻案),落地時把它標 `[status:superseded]` 並寫新 RULE。
- **重讀**:`_note_reread_config` 沒寫、寫 null、值看不懂、讀不成 JSON、`note_reread` 不是物件 → block(壞設定各講一句「照預設 block」);寫 block 照實回 block,拿掉「轉擋還沒做」;warn、off 照原義。設定讀不到之前就發生的例外,照 block 處理(預設就是 block)。

### 重讀:候選與兩層

- 候選照舊(推送範圍裡程式和管它的筆記都改了的守檔筆記),範圍照舊。
- **第一層(沒跑判定)**:候選的對照指紋沒有任何已提交、而且 `provenance_ok` 為真的判定紀錄 → 列為「沒對照」。對照指紋照舊含程式 blob、不含筆記自己的內容:筆記改了不必重判;程式改了(含合併主線帶進別人對同一支程式的改動、筆記的 about_code 增減)就要重判,訊息要講這點。**只在本機推送前擋**;環境變數 `CI` 有值時第一層只印、不擋——CI 在主線推送時用整個 PR 的累計範圍重算,合併讓程式 blob 變了,指紋必然對不上,擋了只會在主線留下修不掉的紅燈。
- **第二層(點出的規則類行沒處理)**:對每篇候選,不論第一層成不成立都跑。讀頂端提交裡 `governance/reread-verdicts/` 下所有判定紀錄,取 `note` 欄等於這篇路徑的(依筆記路徑,不依指紋,所以合併後在 CI 照樣判得出;`provenance_ok` 不論真假都算,較保守),逐列看:
  - 引句 = 那一列的 `quote`(去頭尾空白);`quote` 缺或空時退回整行 `text`。
  - 頂端版筆記全文找不到這段引句 → 這一列算處理過(改掉或刪掉了)。
  - 找得到 → 看含這段引句的每一行是不是**規則類行**:在摘要區(`_notelines_regions` 判)而且所屬邏輯行(`_ns_summary_logical` 把接續行併起來)以 `RULE:` 開頭且沒標 `[status:superseded]`、或符合 `INVARIANT_RE`、或以摘要前綴(`WHY:`、`RULE:`、`PITFALL:`、`FACT:`、`FLOW:`、`DEP:`、`KEY:`)開頭且含 `[test:`。正文、圍欄、引用區塊裡的行一律不算。這個判斷收成一支共用函式,第二層與 `drift ack --kind reread` 都用它。
  - 規則類行、而且沒有對到「同一路徑、同一行原文、綁了點出它的那份判定紀錄對照指紋」的 kind=reread 表態 → 要處理。
  - 非規則類行:只印「判定點出幾行一般行」,不擋。
- 兩層同時成立時兩邊都印,記一筆 `blocked`。
- 判定紀錄檔用 `_nodehome_cat_blobs_capped` 讀,單檔上限 256 KB、全部上限 8 MB;超過、讀不成 JSON、`rows` 不是清單、某列不是物件或 `quote`/`text` 都不是字串 → 判不了(印是哪個檔、怎麼修:修好或刪掉那份紀錄再提交)。

### 回傳碼與判不了

- `_note_audit_resolve` 的原因種類多一種 `undecidable`:讀不到頂端檔案清單(git 失敗)改記這一種;淺層 clone、沒有圖譜照舊 `skipped`。只有重讀的 prepare 與 check 有傳 `reasons`,其他呼叫端不受影響;prepare 把 `undecidable` 當 `skipped` 處理(行為不變)。
- reread-check 的終點找不到(`_lens_full_sha` 回 None,多半是 git 暫時失敗)改歸判不了,不是參數錯。
- 分三類:
  - 參數錯(推送參數只給一個、範圍格式錯):回 2。
  - 環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線):回 0,記 `skipped` 或 `none`。
  - 判不了(`undecidable`、終點找不到、逾時、判定紀錄讀不了或讀不懂、沒預料的例外):block 時回 1、印原因與單次略過寫法(`_drift_unknown_hint` 加一個參數共用,不另寫)、記 `blocked`;warn 時回 0、記 `skipped`。
- 本體照 m1、retire 的先例拆成判定、兜底、印出記帳三段,回傳碼在印出前定好。
- 治理帳:block 擋下記 `blocked`,detail 記兩層各幾篇、第二層要處理的每一行(路徑、引句前 80 字、判定紀錄指紋);warn 照舊記 `reminded`(沿用既有 18 筆的名字,不改成 `warned`)。

### 輸出

- 擋下原因走標準錯誤、開頭「擋下:」,跟其他會擋的閘一樣;只提醒的內容照舊走標準輸出。掛鉤那一段不再丟掉標準錯誤。
- 擋下時不印「這只是提醒、不擋」那句;印逃生:第一層 → prepare 指令(派判定者、record、提交);第二層 → 改掉那句,或 `lumos drift ack <節點> <行號> --kind reread --reason "…"`;另印 `LUMOS_SKIP_REREAD_CHECK=1 git push`(單次略過、會留帳)與 `note_reread.gate` 改 warn 的寫法。
- 從判定紀錄與筆記來的字串(路徑、引句、理由)一律過 `_note_reread_show`;照留指令的節點名用 `shlex.quote`;第二層每次最多列 `_NOTE_REREAD_LIST_MAX` 行,其餘只講還有幾行。
- `cmd_note_audit_reread_record` 收尾那句「確認是誤判就不動——這一版不需要表態」改成:點出的若是規則類行,推送時會擋——改掉那句或用 `drift ack --kind reread` 表態。

### 照留表態

- `lumos drift ack <節點> <行號> --kind reread --reason "…"`:讀工作目錄的那一行;那一行要是規則類行(共用函式判),而且工作目錄 `governance/reread-verdicts/` 裡至少有一份 `note` 欄等於這篇、某列引句出現在這一行的判定紀錄;兩個條件不成立就回 2(講清楚:非規則類行不需要表態;沒有判定點出這一行就不能事先表態)。
- 記 path、text、kind、reason,再加 `verdicts`:點出這一行的那些判定紀錄的對照指紋(排序去重)。reread 加進 `_DRIFT_BOUND_KINDS` 那一類的比對:第二層只認 `verdicts` 含點出那一列的紀錄指紋的表態;之後程式又改、新判定再點出同一行,就要重新表態。
- `_DRIFT_KIND_NAMES` 加名字;`drift scan` 的種類計數排除 reread(它只在推送時判);不收 `--tracked-in`。

### 掛鉤與 CI

- 推送前掛鉤 reread-check 那段照其他會擋的閘:128 以上交 `pp_stop_if_signaled`;回 1 擋下並印逃生段;其他非零(含舊版工具不認得子指令回 2)講一句「這次沒檢查」放行。
- CI 那一步照 drift check 那步的寫法:拿掉 `|| true` 與 `continue-on-error`,改成回 1 時印 `::error::` 說明後失敗、其他非零照原碼失敗;步驟名稱拿掉「只提醒、不擋」。

### 要一起改的說法

- 筆記:[[Systems/存量漂移守衛]] 的 m1 預設 RULE(標 superseded、寫新 RULE)與「那段只提醒、恆放行」「沒寫是 warn」的句子;[[Systems/筆記內容審]] 的 reread 段與複雜度放行說明;[[Systems/bound-tests-gate]] 的「只提醒的回頭重讀」段與 CI 步驟指紋說明;[[Projects/守檔筆記對照改動_計劃]] 的 S7、S9、S13 與做法段「任何情況都回 0」「只提醒」(條款改寫成新行為並註明被本案取代);[[Projects/舊句檢查_計劃]] 的 RETIRE-IF 與 2026-10-14 那行 REVISIT(人裁轉擋,加結案註記)。
- 手冊:`skills/lumos-project-notes/commands/06-代碼審與推送.md`、`08-自動跑的.md`、`04-自檢與健康.md` 寫「只提醒」「恆回 0」「沒寫是 warn」的句子;README 與英文版的推送前段落。
- 程式說明:reread-check 與 drift check 的 `--help`、命令表說明、相關函式說明、掛鉤與 CI 的註解。

### 對消費專案的影響

- `lumos update` 之後:舊句檢查跟總開關(總開關設 warn 或 off 的專案不會被新擋);重讀變預設擋,每次改程式又改到家筆記的推送都要先派判定者——沒有 Claude/Codex 環境、或程式碼不能送外部模型的專案,在 `.lumos/config.json` 寫 `note_reread.gate` 為 warn 或 off。CHANGELOG v1.3 寫明這兩點。
- 照既有手冊把 reread-check 接進自家 CI(不加 `|| true`)的消費專案:第二層與判不了會讓 CI 失敗,第一層在 CI 不擋。

## 驗收條款

- [S1] 當設定沒寫 `drift_check.old_sentence`、總開關也沒寫,而推送範圍有名稱消失的舊句時,drift check 應回 1 並印舊句清單。[test:t_old_sentence_default_follows_gate]
- [S2] 當 `drift_check.gate` 寫 warn 而 `old_sentence` 沒寫,而推送範圍有名稱消失的舊句時,drift check 應回 0 只印清單。[test:t_old_sentence_default_follows_gate]
- [S3] 當 `.lumos/config.json` 讀不成 JSON,而推送範圍有名稱消失的舊句時,drift check 應回 1 並另印一句照預設 block。[test:t_old_sentence_default_follows_gate]
- [S4] 當 `note_reread.gate` 沒寫、寫 block、寫 null 或值看不懂,而本機推送範圍裡有候選沒有 provenance_ok 為真的已提交判定紀錄時,reread-check 應回 1、在標準錯誤印「擋下:」與 prepare 指令、記一筆 blocked,而且不印「這只是提醒」那句。[test:t_reread_block_layer1]
- [S5] 當環境變數 CI 有值,而有候選沒有判定紀錄、第二層也沒有要處理的行時,reread-check 應回 0 並印出沒對照的候選。[test:t_reread_block_layer1]
- [S6] 當候選只有 provenance_ok 為假的判定紀錄時,reread-check 應把它當成沒對照。[test:t_reread_block_layer1]
- [S7] 當 `note_reread.gate` 寫 warn,而有候選沒有判定紀錄時,reread-check 應回 0、記 reminded。[test:t_reread_block_layer1]
- [S8] 當判定紀錄點出一行摘要區的 `RULE:` 行、引句還在頂端版筆記、也沒有綁那份紀錄的表態時,reread-check 應回 1 並印那一行與照留指令,CI 環境也一樣。[test:t_reread_block_layer2]
- [S9] 當判定紀錄點出的引句在頂端版筆記已找不到時,reread-check 應把那一列算處理過;只改同一行引句以外的字時應照樣擋。[test:t_reread_block_layer2]
- [S10] 當判定紀錄點出的是正文裡提到 `RULE:` 或 `★INVARIANT★` 字樣的說明句時,reread-check 不應擋。[test:t_reread_block_layer2]
- [S11] 當同一行有 kind=reread、綁了點出它的那份紀錄指紋的表態時,reread-check 應放行;表態綁的是另一份紀錄的指紋、而新紀錄又點出同一行時,應擋。[test:t_reread_block_layer2]
- [S12] 當同一篇有兩份判定紀錄、只有較舊那份點出還留著的規則類行時,reread-check 應照樣擋下。[test:t_reread_block_layer2]
- [S13] 當第一層與第二層同時成立時,reread-check 應兩層都印、只記一筆 blocked。[test:t_reread_block_layer2]
- [S14] 當 block 時 reread-check 遇到讀不到頂端檔案清單、終點找不到、逾時、判定紀錄讀不懂或沒預料的例外,應回 1 並印原因與 LUMOS_SKIP_REREAD_CHECK;warn 時應回 0、記 skipped。[test:t_reread_block_undecidable]
- [S15] 當 reread-check 遇到淺層 clone、不是 git 專案或範圍沒有新東西時,應回 0;推送參數只給一個時應回 2。[test:t_reread_block_undecidable]
- [S16] 當設了 `LUMOS_SKIP_REREAD_CHECK=1`,reread-check 應回 0 並記 skipped-env。[test:t_reread_block_undecidable]
- [S17] 當 `drift ack --kind reread` 指到非規則類行、或指到沒有任何判定紀錄點出的規則類行時,lumos 應回 2 並說明原因,不寫帳。[test:t_drift_ack_reread_kind]
- [S18] 當 `drift ack --kind reread` 指到有判定紀錄點出的規則類行時,lumos 應寫入一筆含 kind=reread、path、text、reason、verdicts 的表態並印成功訊息。[test:t_drift_ack_reread_kind]
- [S19] 當 `drift scan` 讀到 kind=reread 的表態時,種類計數不應出現 reread。[test:t_drift_ack_reread_kind]
- [S20] 推送前掛鉤的 reread-check 段應在回傳 1 時擋下並印逃生段、128 以上交給中斷處理、其他非零講一句放行,而且不丟掉標準錯誤;CI 的 reread-check 那一步不應帶 `|| true` 或 `continue-on-error`,回 1 時應印 `::error::`。[test:t_reread_block_hook_and_ci_wiring]
- [S21] `cmd_note_audit_reread_record` 收尾的提示不應再出現「不需要表態」。[test:t_reread_block_hook_and_ci_wiring]

## 實務隱患

- 判定者不穩:同一批材料重派可能多點或少點幾行;只擋規則類行把波動限制在最少的那一類,而且改掉那段引句就放行,不會因重判而循環。
- 同一篇多份紀錄取聯集(依路徑):舊紀錄點出、新紀錄沒點出的規則類行也會擋。這是刻意保守;那一行若已不成立,改掉或表態都是幾秒的事。上線前已提交的 5 份紀錄裡點出的規則類行,上線那次推送就要處理一次。
- 每次推送要讀全部判定紀錄找 `note` 欄:現在 5 份約 20 KB;上限 8 MB 擋住惡意大檔;REVISIT 那天量份數與耗時。
- 合併主線讓指紋變:本機推送前第一層會要求重判,這是刻意的(合進來的程式沒人對照過),訊息要講清楚原因;CI 不擋第一層。
- 判定要把筆記全文與程式 diff 交給判定模型;Codex 編排時是外部服務。原本是可選的提醒,現在成了推送的必經步驟,有保密要求的專案要設 warn 或 off。
- 設定從被推的頂端提交讀:推送者可以在同一個提交把開關改成 warn 自我解除——這是所有閘共有的既有性質,RETIRE-IF 看不到,留給代碼審與人工抽查。
- 主程式的 `_note_reread_check` 已被複雜度放行、約定 2026-11-01 前拆小;本案拆成三段正好一起處理。
- 會被新行為弄紅、要一起改斷言的既有測試(不刪測試):`t_note_audit_reread_check_never_blocks`、`t_note_audit_reread_check_wired`、`t_note_audit_reread_mode_and_isolation`、`t_note_audit_reread_check_reminds`、`t_note_audit_reread_non_utf8_path_logs`、`t_note_audit_reread_prepare_skips_uncommitted_records`、`t_ci_yml_matrix_and_gates_shape`(CI 步驟指紋與名稱)、`t_prepush_gates_stop_on_signal`(數 `pp_stop_if_signaled` 行數)、`t_drift_m1_layers_and_mode`、`t_drift_m1_review_r2_doctor_old_sentence`;實作時跑 `-k reread`、`-k m1`、`-k drift_ack`、`-k prepush`、`-k ci_yml` 找出其餘。
- 已排除:金流:只動本機與 CI 的檢查回傳碼,不碰任何付款或計費
- 已排除:不可逆:擋下只是讓推送失敗,改設定或還原提交即恢復;表態檔只追加,舊表態留著無害
- 對外送出:閘本身不送資料,但判定是推送必經步驟,見上
- 守衛面:本案就是改守衛的擋放行為,照走設計審與代碼審

## 回退

兩道都只要把設定改成 warn 就回到提醒(本機與 CI 都讀同一份設定)。要整案回退,同一個 revert 提交還原:兩支設定解析、reread-check 的三段與回傳碼、`_note_audit_resolve` 的 `undecidable`、第二層、共用的規則類行判斷、`drift ack` 的 reread 類別與種類表、掛鉤與 CI 的兩段、說明文字與 doctor 提示行、`LUMOS_VERSION` 與 CHANGELOG、改過斷言的既有測試、被改寫的筆記條款(含標 superseded 的 RULE)。`drift-acks.jsonl` 裡 kind=reread 的表態留著無害:`_drift_load_acks` 只收 `_DRIFT_KINDS` 裡的種類,舊版讀到會略過。已經 `lumos update` 的消費專案要再 update 一次才回退。

REVISIT:2026-12-04 上線滿 8 週照 RETIRE-IF 三條量(上線日若晚於 2026-10-09 就順延同樣天數):治理帳 `note-reread` 與 `drift-check` 的 blocked 與 skipped-env 事件,抽第二層擋下的規則類行與 m1 要處理的發現人工判真假,並量判定紀錄份數與讀取耗時

## 審計修正紀錄

- r1(2026-10-09,6 席:正確性、邊界、接手、併發、回滾、架構對齊,皆 sonnet):63 條/blocking 19/核心改三處——第一層只在本機擋(合併讓指紋變)、第二層改依筆記路徑讀紀錄並比對引句、表態綁點出它的判定紀錄;其餘補判不了的分法、規則類行收窄、子開關照總開關、要改的說法清單。席報告與處置在 `governance/review-reports/舊句兩道轉擋/`。
- 例:同一個 PR 先推改程式與筆記、再推只改程式 → 合併進主線後 CI 第一層不擋(只印),第二層照依路徑找到的紀錄判;判定點出 `RULE:` 行、作者只把同一行的 `[confirmed:]` 日期往後改 → 引句還在,照樣擋。
