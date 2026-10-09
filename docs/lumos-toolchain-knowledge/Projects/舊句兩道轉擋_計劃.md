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

白話:程式改了、筆記前面的舊句沒人回頭改,是防筆記過期最弱的一環。現有兩道只提醒:名稱消失檢查(推送範圍裡被刪或改名的 Python 名稱、旗標、檔案路徑,筆記還在提)與回頭重讀守檔筆記(程式和管它的筆記這次都改了,提醒交給判定者整篇重讀)。本計劃把兩道都改成在本機推送前預設擋;CI 維持現狀。

## 原問題與範圍

- Enzo 2026-10-09 三次裁定:①不等兩週量測,直接擋(原話「我想直接擋,多檢查一次沒有損失吧」);②重讀選「兩層都擋」(沒跑判定擋;判定點出的規則類行沒處理擋);③設計審第二輪後,重讀「只在本機擋」、CI 維持提醒,並「接受」第一層的成本照擋。
- 擋之前的帳(主線 `docs/.governance-log.jsonl`,事件時間 2026-09-30 到 10-04;10-04 起這幾種例行事件改寫本機帳,沒算進來):回頭重讀 reminded 18 次(每次推送一筆)、recorded 5 份(每篇筆記一筆,其中 4 份同一批)、none 12 次;18 筆 reminded 全是「已對照 0 篇」,合計要判 47 篇。單位不同,比例只看方向:提醒之後真的去判的很少。主因之一是對照指紋含程式 blob,主程式被約 70 篇筆記認領、幾乎每個提交都改,判完再改一行程式就作廢。名稱消失檢查 35 次全是 passed、候選數都是 0:改擋的誤報率沒有任何實測,只能靠上線後的 RETIRE-IF 抽樣。
- 做:①名稱消失檢查 `drift_check.old_sentence` 沒寫時照總開關;②回頭重讀 `note_reread.gate` 沒寫與各種壞設定時改成 block,而且 block 真的會擋——只在呼叫端帶 `--gate` 時;③重讀擋兩層(定義見〈設計〉);④`lumos drift ack` 多一種 `--kind reread`,綁點出那一行的判定紀錄;⑤推送前掛鉤 reread-check 那段帶 `--gate` 並照回傳碼擋;⑥「已對照」的口徑 prepare 與 check 共用一支,並且只認來源核對過的紀錄;⑦被這次改動弄成說謊的筆記條款、手冊、執行時訊息與說明文字一起改(清單見〈設計〉);⑧`LUMOS_VERSION` 升 v1.3、CHANGELOG 加同版一段;⑨既有測試裡釘「不擋」的斷言改成新行為。
- 不做:CI 擋重讀(CI 那一步不帶 `--gate`,維持只提醒;理由見〈設計〉);推送當下呼叫模型;擴大重讀範圍到「這次沒改的家筆記」;非規則類行的判定結果仍只提醒;改對照指紋的組成;判定紀錄的保留與清理(另案,見 REVISIT);替消費專案的 CI 加 reread 步驟。

PRIOR-ART: ①最小解在既有層——重讀已有範圍計算、對照指紋、判定紀錄與預留的 `note_reread.gate`(寫 block 時印「轉擋還沒做」);名稱消失檢查已有 `drift_check.old_sentence` 三值開關,「子開關沒寫照總開關」有 `_drift_retire_config` 的先例;照留表態已有 `drift ack`,「每一類有自己的證據欄與自己的比對分支」有 m1 的先例(`_drift_m1_split_acked`,m1 不放進 `_DRIFT_BOUND_KINDS`);照貼指令的單一產生處是 `_drift_fix_hint`(參數過 `_drift_sh`);判不了的提示有 `_drift_unknown_hint`;判定拆三段有 `_drift_m1_guarded`、`_drift_retire_guarded` 的先例;摘要條目讀法有 `_note_summary_entries`(含單行 summary 與接續行),合約行有 `INVARIANT_RE`,測試綁定有 `TEST_REF_RE`;「掛鉤與 CI 行為不同由呼叫端決定」有 `pp_touched_file` 只在掛鉤給的先例。第二層是新的小機制(讀已提交判定紀錄內容、比對引句、比對表態),零件都用既有的。②世界解過——Swimm 的 code-coupled docs 在合併前把「引用的程式改了、文件沒更新」標成失敗;本案第一層等於同一件事,判斷交給已提交的判定紀錄。③借用:擋規則類行照 [[Projects/守檔筆記對照改動_計劃]]〈做法〉5 寫好的轉擋起點建議(那份計劃標明是起點建議、樣本只有 6 行,本案照人裁採用)。

RETIRE-IF: 上線後 8 週內任一成立就把該道的預設改回 warn(設定一行、不刪程式):第一層 blocked 的推送平均要重判超過 4 篇,或第一層擋下後用 `LUMOS_SKIP_REREAD_CHECK` 略過的佔第一層擋下次數一半以上(成本大到大家繞路);或重讀第二層 blocked 事件記下的規則類行裡,抽樣人工判誤報超過一半;或名稱消失檢查記成要處理(must)的發現裡,抽樣人工判誤報超過一半(`drift-check` 的 skipped-env 不分子檢查,累計 3 次以上時逐筆人工看是不是為了舊句才略過)。

## 設計

### 開關

- **名稱消失檢查**:`_drift_old_sentence_config` 只有在 `old_sentence` **沒寫**(含寫 null、值看不懂)時改照總開關 `drift_check.gate` 的值(總開關沒寫是 block;總開關 off 時沒寫的 m1 也不跑);讀不成 JSON、`drift_check` 不是物件、整份設定不是物件 → block,各講一句「照預設 block」;**明寫的 warn、block、off 照原義,不受總開關影響**(既有 `gate=off` 加 `old_sentence=block` 照跑照擋的行為與測試不變)。行為變化:原本 `gate=off`、`old_sentence` 沒寫的專案 m1 照跑只印,現在不跑;CHANGELOG 寫明。連帶改:`_drift_config` 說明、`drift check` 的 `--help`、doctor 舊句檢查提示行(`_drift_old_sentence_doctor_lines`)、`_drift_check_c` 在 gate=off 時的提示句、推送前掛鉤與 CI 那兩處「改 gate 沒用」的逃生句(沒寫 old_sentence 的專案改 gate 就有用了)。這會作廢 [[Systems/存量漂移守衛]] 那條「m1 沒寫是 warn、不跟 gate 走」的 RULE(Enzo 2026-10-09 人裁翻案),落地時把它標 `[status:superseded]`、補 `[被取代:Projects/舊句兩道轉擋_計劃]`,並寫新 RULE。
- **重讀**:`_note_reread_config` 沒寫、寫 null、值看不懂、讀不成 JSON、`note_reread` 不是物件 → block(壞設定各講一句「照預設 block」);寫 block 照實回 block,拿掉「轉擋還沒做」;warn、off 照原義。
- **重讀的擋只在呼叫端帶 `--gate` 時生效**:`lumos note-audit reread-check` 多一個 `--gate` 旗標;不帶時(CI、手動跑)不論設定都照舊只印、回 0、記既有事件。只有推送前掛鉤帶 `--gate`。理由:本機推送看的是「這次推的增量」,合併後主線 CI 看的是「整個 PR 的累計」,兩邊候選與指紋都不同,設計審前兩輪找到的 CI 誤擋情境(合併讓指紋變、分次推送、兩個分支各自表態)都出在這裡;而且照既有手冊不加 `|| true` 接了這一步的消費專案 CI 不會因升級變紅。代價:用 `--no-verify` 跳過本機掛鉤時,重讀這道沒有 CI 兜底(其他會擋的閘 CI 照擋)。

### 重讀:候選與兩層(以下都只在帶 `--gate` 而且設定是 block 時擋)

- 候選照舊(推送範圍裡程式和管它的筆記都改了的守檔筆記),範圍照舊。路徑帶控制字元而被排在候選外的筆記照舊只印一句跳過(放過而非誤擋,本案不改)。
- **「已對照」的共用口徑**:新的一支 `_note_reread_covered(root, tip)` 取代 `_note_reread_committed`:列頂端提交 `governance/reread-verdicts/` 裡檔名符合 `_NOTE_REREAD_VERDICT_NAME_RE` 的檔,讀內容,只收 `provenance_ok` 為真的,回對照指紋集合。check 的第一層與 prepare 的「略過已對照」都用它,所以只有來源核對沒過的紀錄時,check 擋、prepare 也會重產項目檔(不用 `--all`)。
- **第一層(沒跑判定)**:候選的對照指紋不在 `_note_reread_covered` 的集合裡 → 列為沒對照。對照指紋照舊含筆記路徑與程式 blob、不含筆記自己的內容:筆記改了不必重判;程式改了(含合併主線帶進別人對同一支程式的改動、筆記改名、about_code 增減)就要重判,擋下訊息要講這點。
- **第二層(點出的規則類行沒處理)**:對每篇候選,不論第一層成不成立都跑。讀頂端提交裡檔名符合 `_NOTE_REREAD_VERDICT_NAME_RE` 的所有判定紀錄(不論 `provenance_ok`,較保守),取 `note` 欄經 `_note_reread_show` 轉換後等於這篇路徑同一轉換的(依筆記路徑,不依指紋;筆記改名後舊路徑的紀錄不再適用,改名本身會讓第一層要求重判),逐列決定**比對字串**:
  - `quote` 去頭尾空白後至少 6 個字、而且是 `text` 的子字串 → 用 `quote`;否則用 `text` 去頭尾空白;兩者都是空字串 → 這一列點不出任何行,略過(印一句「判定紀錄某列沒有可比對的原文」)。
  - 比對字串在頂端版筆記找不到 → 這一列算處理過(那一行改掉或刪掉了)。
  - 找得到 → 找出含它的每一個實體行,換成它所屬的摘要條目:用 `_note_summary_entries` 同一套讀法(區塊寫法接續行併回所屬條目、單行 summary 整個值算一條);實體行落在某條目的開頭行到下一條目之前,就屬於那一條;不在摘要裡的實體行一律不算。
  - **規則類條目** = 以 `RULE:` 開頭且沒標 `[status:superseded]`;或符合 `INVARIANT_RE`;或以摘要前綴開頭(前綴清單取專案既有的摘要前綴表,不另寫)且含 `TEST_REF_RE` 認得的測試綁定。`★IRREVERSIBLE★`、`★CHECKPOINT★` 這類其他合約行不算:人裁時給的範圍是「RULE、★INVARIANT★、帶測試綁定」,不另擴;它們若帶測試綁定就照第三種算。這個判斷收成一支共用函式 `_reread_rule_entry`,放在筆記內容審的回頭重讀常數那一段(照 `_path_special_chars` 的先例,存量漂移那邊 `drift ack` 來呼叫它)。
  - 規則類條目,而且沒有「同一路徑、同一條目原文(整條,接續行併回後去頭尾空白)、`verdicts` 含點出這一列那份紀錄對照指紋」的 kind=reread 表態 → 要處理。
  - 非規則類:只印「判定點出幾行一般行」,不擋。
- 兩層同時成立時兩邊都印,記一筆 `blocked`。
- 判定紀錄用 `_nodehome_cat_blobs_capped` 讀,傳 reread 的 deadline;單檔上限 256 KB、全部上限 8 MB;單檔超過、讀不成 JSON、`rows` 不是清單、某列不是物件或 `quote`/`text` 都不是字串 → 判不了,印是哪個檔、怎麼修(修好或用 `git rm` 刪掉那份再提交;刪掉會讓那篇第一層要求重判);總量超過時印最大的五份檔名。

### 回傳碼與判不了

- `_note_audit_resolve` 的原因種類多一種 `undecidable`:讀不到頂端檔案清單(git 失敗)改記這一種;淺層 clone、沒有圖譜照舊 `skipped`。只有重讀的 prepare 與 check 有傳 `reasons`,其他呼叫端不受影響;prepare 把 `undecidable` 當 `skipped` 處理(行為不變)。
- 分三類(只在帶 `--gate` 時影響回傳碼;不帶時全部回 0、事件照舊):
  - 參數錯(推送參數只給一個、範圍格式錯、終點找不到):回 2,跟 drift check 對同一件事的處理一樣(掛鉤傳的終點是它自己剛算出的提交,本機一定有)。
  - 環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線):回 0,記 `skipped` 或 `none`。
  - 判不了(`undecidable`、逾時、判定紀錄讀不了或讀不懂、沒預料的例外):設定是 block 時回 1、印原因與單次略過寫法(`_drift_unknown_hint` 加一個參數共用,不另寫)、記 `blocked`;warn 時回 0、記 `skipped`。設定讀到之前就發生的例外:改讀工作目錄的 `.lumos/config.json` 判模式,也讀不到才照 block。
- 本體照 m1、retire 的先例拆成判定、兜底、印出記帳三段,回傳碼在印出前定好(順帶結掉 [[Systems/筆記內容審]] 那筆 2026-11-01 前要拆小的複雜度放行)。
- 治理帳:擋下記 `blocked`(帶 `hard=True`,同其他閘),detail 記兩層各幾篇、第一層要重判幾篇、第二層要處理的前 50 行(路徑、引句前 80 字、判定紀錄指紋);warn 照舊記 `reminded`(沿用既有 18 筆的名字)。

### 輸出

- 擋下原因走標準錯誤、開頭「擋下:」,跟其他會擋的閘一樣;只提醒的內容照舊走標準輸出。
- 擋下時不印「這只是提醒、不擋」那句;印逃生:第一層 → prepare 指令(派判定者、record、提交;說明程式改了就要重判);第二層 → 改掉那句(提醒:改筆記會讓已過的代碼審留痕失效,已過代碼審的推送優先表態),或照留指令;另印 `LUMOS_SKIP_REREAD_CHECK=1 git push`(單次略過、會留帳)與 `note_reread.gate` 改 warn 的寫法。
- 照留指令由 `_drift_fix_hint` 多一個 reread 分支產生(參數過 `_drift_sh`;路徑帶特殊字元時照 m1 的做法不印可照貼的指令),不在 reread-check 另寫。
- 從判定紀錄與筆記來的字串(路徑、引句、理由)一律過 `_note_reread_show`;第二層每次最多列 `_NOTE_REREAD_LIST_MAX` 行,其餘只講還有幾行。
- `cmd_note_audit_reread_record` 收尾那句「確認是誤判就不動——這一版不需要表態」改成:點出的若是規則類行,推送時會擋——改掉那句或用 `drift ack --kind reread` 表態。它印的 `git add` 提示改列這次寫的具體檔名(不整個資料夾,免得夾帶殘檔與別的會談的紀錄)。

### 照留表態

- `lumos drift ack <節點> <行號> --kind reread --reason "…"`:讀工作目錄的那一篇;行號要是一條摘要條目的開頭行(跟 retire 一樣,記整條);那一條要是規則類條目(共用函式判),而且工作目錄 `governance/reread-verdicts/` 裡至少有一份檔名合規、`note` 欄等於這篇、某列比對字串(同第二層的取法)出現在這一條的判定紀錄;不成立就回 2(講清楚:非規則類不需要表態;沒有判定點出這一條就不能事先表態;行號不是條目開頭就講開頭在第幾行)。
- 記 path、text(整條)、kind、reason,再加 `verdicts`:點出這一條的那些判定紀錄的對照指紋(排序去重)。
- 比對照 m1 的先例自成一支 `_drift_reread_split_acked`,**不放進 `_DRIFT_BOUND_KINDS`**:同一條目的所有 reread 表態取 `verdicts` 聯集(不取 seq 最新),點出某列的紀錄指紋在聯集裡就算涵蓋。
- `_DRIFT_KINDS` 加 reread(`_drift_load_acks` 收、argparse 的 `--kind` 選項有);`_DRIFT_KIND_NAMES` 加名字;`_DRIFT_SCAN_KINDS` 跟 m1 一樣排除 reread(它只在推送時判);不收 `--tracked-in`;表態事件照 drift ack 現有寫法記在 `drift-check` 閘(detail 標 kind=reread)。

### 掛鉤與 CI

- 推送前掛鉤 reread-check 那段帶 `--gate`,照其他會擋的閘處理回傳碼:128 以上交 `pp_stop_if_signaled`;回 1 擋下並印逃生段;其他非零(含舊版工具不認得 `--gate` 回 2)講一句「這次沒檢查」放行。標準錯誤照其他會擋的閘不丟(擋下原因在那裡;舊版工具的用法說明也會印出,這是部分更新時的已知雜訊)。
- CI 那一步不改(不帶 `--gate`、照舊 `continue-on-error`),步驟名稱「只提醒、不擋」照舊成立。

### 要一起改的說法

- 筆記:[[Systems/存量漂移守衛]] 的 m1 預設 RULE 與「那段只提醒、恆放行」「沒寫是 warn」的句子;[[Systems/筆記內容審]] 的 reread 段(「只列目錄、不讀內容」、兩層、`--gate`)與複雜度放行說明;[[Systems/bound-tests-gate]] 的「只提醒的回頭重讀」段;[[Projects/守檔筆記對照改動_計劃]] 的 S7、S9、S13、做法段與實作紀錄裡「任何情況都回 0」「只提醒」「只列目錄、不讀內容」「不做:擋推送」、RETIRE-IF 與 2026-10-15、2026-11-26 兩行 REVISIT(條款改寫成「不帶 `--gate` 時」的行為並註明本案取代;綁的測試名照舊、斷言改成新行為;S9「掛鉤與 CI 不應出現連續字串 note-audit check」的限制保留);[[Projects/舊句檢查_計劃]] 的 RETIRE-IF、2026-10-14 與 2026-12-14 兩行 REVISIT、相容性說明;[[Projects/舊句偵測實驗_計劃]] 2026-10-26 那行 REVISIT 與「達標才改擋」門檻(人裁轉擋,加結案註記);[[Systems/README圖產生器]] 管的推送前關卡圖(重讀那列改成擋)。
- 手冊:`skills/lumos-project-notes/commands/06-代碼審與推送.md` 第 4 步與「只提醒、不擋」「不用表態」的句子(消費專案 CI 那段照舊成立:CI 不帶 `--gate` 仍恆回 0)、`08-自動跑的.md` 與 `04-自檢與健康.md` 寫「只提醒」「沒寫是 warn」「改 gate 沒用」的句子;README 與英文版的推送前段落與圖的替代文字。
- 程式:reread-check 與 drift check 的 `--help`、命令表說明、相關函式說明、掛鉤與 CI 的註解(改寫時不准出現筆記內容審的上線字串)、上面列的執行時逃生句。

### 對消費專案的影響

- `lumos update` 之後:舊句檢查沒寫子開關的跟總開關(總開關設 warn 或 off 的專案不會被新擋);重讀在本機掛鉤變預設擋,每次改程式又改到家筆記的推送都要先派判定者——沒有 Claude/Codex 環境、或程式碼不能送外部模型的專案,在 `.lumos/config.json` 寫 `note_reread.gate` 為 warn 或 off。CHANGELOG v1.3 寫明這兩點與 `gate=off` 那個行為變化。
- 照既有手冊把 reread-check 接進自家 CI 的消費專案不受影響(CI 不帶 `--gate`)。

## 驗收條款

- [S1] 當設定沒寫 `drift_check.old_sentence`、總開關也沒寫,而推送範圍有名稱消失的舊句時,drift check 應回 1 並印舊句清單。[test:t_old_sentence_default_follows_gate]
- [S2] 當 `drift_check.gate` 寫 warn 而 `old_sentence` 沒寫,而推送範圍有名稱消失的舊句時,drift check 應回 0 只印清單。[test:t_old_sentence_default_follows_gate]
- [S3] 當 `drift_check.gate` 寫 off 而 `old_sentence` 明寫 block,而推送範圍有名稱消失的舊句時,drift check 應回 1。[test:t_old_sentence_default_follows_gate]
- [S4] 當 `.lumos/config.json` 讀不成 JSON,而推送範圍有名稱消失的舊句時,drift check 應回 1 並另印一句照預設 block。[test:t_old_sentence_default_follows_gate]
- [S5] 當帶 `--gate`、`note_reread.gate` 沒寫或寫 block,而推送範圍裡有候選的對照指紋不在已對照集合時,reread-check 應回 1、在標準錯誤印「擋下:」與 prepare 指令、記一筆 blocked,而且不印「這只是提醒」那句。[test:t_reread_block_layer1]
- [S6] 當不帶 `--gate`,而有候選沒有判定紀錄時,reread-check 應回 0 並記 reminded,不論設定是什麼。[test:t_reread_block_layer1]
- [S7] 當候選只有 provenance_ok 為假的判定紀錄時,帶 `--gate` 的 reread-check 應把它當成沒對照,而 reread-prepare 不帶 `--all` 也應為它產項目檔。[test:t_reread_block_layer1]
- [S8] 當 `note_reread.gate` 寫 warn 而帶 `--gate`,有候選沒有判定紀錄時,reread-check 應回 0、記 reminded。[test:t_reread_block_layer1]
- [S9] 當判定紀錄點出一條摘要 `RULE:` 條目、比對字串還在頂端版筆記、也沒有涵蓋它的表態時,帶 `--gate` 的 reread-check 應回 1 並印那一條與照留指令。[test:t_reread_block_layer2]
- [S10] 當比對字串在頂端版筆記已找不到時,reread-check 應把那一列算處理過;只改同一條目比對字串以外的字時應照樣擋。[test:t_reread_block_layer2]
- [S11] 當判定紀錄點出的是正文裡提到 `RULE:` 或 `★INVARIANT★` 字樣的說明句、或沒帶測試綁定的 `WHY:` 條目時,reread-check 不應擋。[test:t_reread_block_layer2]
- [S12] 當某列 `quote` 少於 6 字或不是 `text` 的子字串時,應改用 `text` 比對;`quote` 與 `text` 都空時應略過那一列、不擋任何條目。[test:t_reread_block_layer2]
- [S13] 當同一條目有兩筆 kind=reread 表態、各綁一份紀錄指紋,而頂端兩份紀錄都點出它時,reread-check 應放行;只有一份被涵蓋時應擋。[test:t_reread_block_layer2]
- [S14] 當引句落在摘要條目的接續行時,reread-check 應以那一整條判規則類,照留指令的行號應是條目開頭行。[test:t_reread_block_layer2]
- [S15] 當第一層與第二層同時成立時,reread-check 應兩層都印、只記一筆 blocked。[test:t_reread_block_layer2]
- [S16] 當 `governance/reread-verdicts/` 裡有檔名不符正規式的檔(例如殘檔)時,reread-check 應忽略它,不判成判不了。[test:t_reread_block_undecidable]
- [S17] 當帶 `--gate`、設定是 block,而 reread-check 遇到讀不到頂端檔案清單、逾時、判定紀錄讀不懂或沒預料的例外時,應回 1 並印原因與 LUMOS_SKIP_REREAD_CHECK;設定是 warn 時應回 0、記 skipped。[test:t_reread_block_undecidable]
- [S18] 當 reread-check 遇到淺層 clone、不是 git 專案或範圍沒有新東西時,應回 0;推送參數只給一個或終點找不到時應回 2。[test:t_reread_block_undecidable]
- [S19] 當設了 `LUMOS_SKIP_REREAD_CHECK=1`,reread-check 應回 0 並記 skipped-env。[test:t_reread_block_undecidable]
- [S20] 當 `drift ack --kind reread` 指到非規則類條目、沒有任何判定紀錄點出的規則類條目、或不是條目開頭的行號時,lumos 應回 2 並說明原因,不寫帳。[test:t_drift_ack_reread_kind]
- [S21] 當 `drift ack --kind reread` 指到有判定紀錄點出的規則類條目開頭行時,lumos 應寫入一筆含 kind=reread、path、整條 text、reason、verdicts 的表態並印成功訊息。[test:t_drift_ack_reread_kind]
- [S22] 當 `drift scan` 讀到 kind=reread 的表態時,種類計數不應出現 reread。[test:t_drift_ack_reread_kind]
- [S23] 推送前掛鉤的 reread-check 段應帶 `--gate`、在回傳 1 時擋下並印逃生段、128 以上交給中斷處理、其他非零講一句放行;CI 的 reread-check 那一步應照舊不帶 `--gate`。[test:t_reread_block_hook_and_ci_wiring]
- [S24] `cmd_note_audit_reread_record` 收尾的提示不應再出現「不需要表態」,`git add` 提示應列具體檔名。[test:t_reread_block_hook_and_ci_wiring]

## 實務隱患

- 第一層的成本(人裁接受):主程式被約 70 篇筆記認領,改主程式又改到家筆記的推送,那幾篇都要先判;判完再改程式要重判。歷史帳 18 次推送合計 47 篇,平均約 2.6 篇,判定者每篇約 0.17 美元(列價,實驗量的)加幾分鐘。RETIRE-IF 第一條量這個。
- 判定者不穩:同一批材料重派可能多點或少點幾行;只擋規則類條目把波動限制在最少的那一類,改掉比對字串就放行,不會因重判而循環。
- 同一篇多份紀錄取聯集(依路徑):舊紀錄點出、新紀錄沒點出的規則類條目也會擋,是刻意保守;已提交的 5 份紀錄(約 7.8 KB)逐列對過,現存的規則類條目是 0,上線那次推送不會被舊紀錄擋。
- 判定紀錄只增不減:照歷史速度(每份約 1.6 KB)離 8 MB 上限很遠;保留與清理另案,REVISIT 那天量份數。
- 判定要把筆記全文與程式 diff 交給判定模型;Codex 編排時是外部服務。原本是可選的提醒,現在成了本機推送的必經步驟,有保密要求的專案要設 warn 或 off。
- 設定從被推的頂端提交讀:推送者可以在同一個提交把開關改成 warn 自我解除——這是所有閘共有的既有性質,RETIRE-IF 看不到,留給代碼審與人工抽查。
- `--no-verify` 跳過本機掛鉤時重讀沒有 CI 兜底(人裁接受,見〈開關〉)。
- 會被新行為弄紅、要一起改斷言的既有測試(不刪測試、不改名):`t_note_audit_reread_check_never_blocks`(改成「不帶 `--gate` 時從不擋」,名字照舊成立)、`t_note_audit_reread_check_wired`、`t_note_audit_reread_mode_and_isolation`、`t_note_audit_reread_check_reminds`、`t_note_audit_reread_non_utf8_path_logs`、`t_note_audit_reread_prepare_skips_uncommitted_records`、`t_prepush_gates_stop_on_signal`(數 `pp_stop_if_signaled` 行數)、`t_drift_m1_layers_and_mode`、`t_drift_m1_review_r2_doctor_old_sentence`、`t_drift_m1_gate_off_wording`;實作時跑 `-k reread`、`-k m1`、`-k drift_ack`、`-k prepush`、`-k ci_yml` 找出其餘。CI 那一步不改,`t_ci_yml_matrix_and_gates_shape` 的步驟指紋照舊。
- 已排除:金流:只動本機掛鉤與工具的回傳碼,不碰任何付款或計費
- 已排除:不可逆:擋下只是讓推送失敗,改設定或還原即恢復;表態檔只追加,舊表態留著無害
- 對外送出:閘本身不送資料,但判定是本機推送必經步驟,見上
- 守衛面:本案就是改守衛的擋放行為,照走設計審與代碼審

## 回退

兩道都只要把設定改成 warn 就回到提醒(掛鉤讀被推頂端的設定;設定讀到之前的失敗改讀工作目錄設定)。要整案回退,走前進版本:發 v1.4 撤回(不倒回 v1.2——消費專案的版本提示只在來源版本較新時出現,倒回去它們收不到更新提示),同一個提交還原兩支設定解析、reread-check 的 `--gate` 與三段、`_note_audit_resolve` 的 `undecidable`、`_note_reread_covered`、第二層與共用的規則類判斷、`drift ack` 的 reread 類別與種類表與 `_drift_fix_hint` 分支、掛鉤那一段、說明文字與 doctor 提示行與執行時逃生句、改過斷言的既有測試、被改寫的筆記條款(含標 superseded 的 RULE);CHANGELOG 加 v1.4 撤回段,不刪 v1.3。`drift-acks.jsonl` 裡 kind=reread 的表態留著無害:`_drift_load_acks` 只收 `_DRIFT_KINDS` 裡的種類,撤回後讀到會略過。

REVISIT:2026-12-04 上線滿 8 週照 RETIRE-IF 四條量(上線日若晚於 2026-10-09 就順延同樣天數):治理帳 `note-reread` 的 blocked(第一層重判篇數)與 skipped-env、`drift-check` 的 blocked 與 skipped-env,抽第二層擋下的規則類條目與 m1 要處理的發現人工判真假,並量判定紀錄份數與讀取耗時,決定要不要另開保留與清理

## 審計修正紀錄

- r1(2026-10-09,6 席:正確性、邊界、接手、併發、回滾、架構對齊,皆 sonnet):63 條/blocking 19/核心改三處——第一層只在本機擋(合併讓指紋變)、第二層改依筆記路徑讀紀錄並比對引句、表態綁點出它的判定紀錄;其餘補判不了的分法、規則類行收窄、子開關照總開關、要改的說法清單。席報告與處置在 `governance/review-reports/舊句兩道轉擋/`。
- 例:同一個 PR 先推改程式與筆記、再推只改程式 → 合併進主線後 CI 第一層不擋(只印),第二層照依路徑找到的紀錄判;判定點出 `RULE:` 行、作者只把同一行的 `[confirmed:]` 日期往後改 → 引句還在,照樣擋。
- r2(2026-10-09,6 席:正確性、邊界、接手、併發、回滾、架構對齊,皆 sonnet):65 條/blocking 17/核心改兩處——依 Enzo 裁定重讀只在本機帶 `--gate` 時擋、CI 照舊只提醒(合併與分次推送的 CI 誤擋整類消失);「已對照」prepare 與 check 共用一支並只認來源核對過的紀錄;另補表態自成一支取聯集、比對字串取法與空引句、殘檔過濾、摘要條目口徑、明寫子開關不受總開關壓、要改的說法清單、前進式回退。席報告與處置在 `governance/review-reports/舊句兩道轉擋/`。
- 例:判定紀錄某列 `quote` 是空字串、`text` 是空白行 → 這一列略過,不會把整篇規則類條目都算成被點出;判定者把 `quote` 寫成「…」節錄、不是 `text` 的子字串 → 改用整行 `text` 比對,那一行沒改就照樣判。
