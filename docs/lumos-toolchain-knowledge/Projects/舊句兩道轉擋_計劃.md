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

- Enzo 2026-10-09 裁:不等兩週量測,直接擋(原話「我想直接擋,多檢查一次沒有損失吧」);重讀選「兩層都擋」。
- 擋之前的帳(主線 `docs/.governance-log.jsonl`,2026-10-09 數):名稱消失檢查 35 次跑完、全是 passed,沒有 warned 或 blocked;回頭重讀 reminded 18 次、recorded 5 次、none 12 次。提醒之後真的去跑判定並記錄的不到三成,提醒形同虛設,是改擋的主因。
- 做:①名稱消失檢查 `drift_check.old_sentence` 沒寫與各種壞設定時改成 block;②回頭重讀 `note_reread.gate` 沒寫與各種壞設定時改成 block,而且 block 真的會擋(原本寫 block 也照 warn);③重讀擋兩層(定義見〈設計〉);④`lumos drift ack` 多一種 `--kind reread`;⑤推送前掛鉤與 CI 照回傳碼擋;⑥寫死「預設 warn」或「任何情況都回 0」的說明文字、doctor 提示行、`--help`、CHANGELOG 一起改;⑦既有測試裡釘「不擋」的斷言改成新行為。
- 不做:推送當下呼叫模型(判定仍由編排者派,閘只讀已提交的紀錄,所以 CI 也判得出);擴大重讀範圍到「這次沒改的家筆記」(另案,成本要先量);非結構行的判定結果仍只提醒;改對照指紋的組成。

PRIOR-ART: ①最小解在既有層——重讀已有範圍計算、對照指紋、判定紀錄與預留的 `note_reread.gate`(寫 block 時印「轉擋還沒做」);名稱消失檢查已有 `drift_check.old_sentence` 三值開關;照留表態已有 `drift ack` 以路徑與原文綁定的帳(`_drift_load_acks` 讀提交的樹、`_drift_ack_key` 比對)。第一層與開關只改預設與回傳碼;第二層是新的小機制(讀已提交判定紀錄的內容、判結構行、比對表態),零件都用既有的。②世界解過——Swimm 的 code-coupled docs 在合併前把「引用的程式改了、文件沒更新」標成失敗;本案第一層等於同一件事,判斷交給已提交的判定紀錄。③借用:結構行的擋法照 [[Projects/守檔筆記對照改動_計劃]]〈做法〉5 寫好的轉擋起點建議(實驗二這類行 6 行裡 5 行是真問題)。

RETIRE-IF: 上線後 8 週內任一成立就把該道的預設改回 warn(設定一行、不刪程式):重讀第二層擋下的結構行裡,抽樣人工判誤報超過一半;或治理帳裡這兩道的 `skipped-env`(用 `LUMOS_SKIP_DRIFT_CHECK`/`LUMOS_SKIP_REREAD_CHECK` 單次略過)加上 CI 在這兩步擋下的次數(本機 `--no-verify` 繞過只有 CI 看得到)累計 3 次以上;或名稱消失檢查記成「要處理」(must)的發現裡,抽樣人工判誤報超過一半。

## 設計

- **名稱消失檢查開關**:`_drift_old_sentence_config` 沒寫、寫 null、讀不成 JSON、`drift_check` 不是物件、整份設定不是物件、值看不懂時一律回 block;壞設定各講一句,說「照預設 block」;warn、off 照原義。連帶改:`_drift_config` 說明、`drift check` 的 `--help`、doctor 的舊句檢查提示行(`_drift_old_sentence_doctor_lines` 讀不懂設定時改講「推送時擋」)。
- **重讀開關**:`_note_reread_config` 沒寫與各種壞設定改回 block(壞設定各講一句「照預設 block」);寫 block 照實回 block,拿掉「轉擋還沒做」那句;warn、off 照原義。
- **重讀第一層(沒對照)**:block 時有 `left`(對照指紋沒有任何已提交判定紀錄的候選)→ 印清單、prepare 指令與一句「擋下」,記 `blocked`,回 1;warn 照原樣記 `reminded`、回 0。對照指紋照舊不含筆記自己的內容:筆記改了不必重判,程式改了才要。
- **重讀第二層(點出的結構行沒處理)**:候選全部對照過之後才跑。對每篇候選,讀頂端提交裡、檔名前綴等於它對照指紋的**所有**判定紀錄(同一指紋可能有多份,取聯集),逐列看 `text`:
  - 結構行 = `text` 去掉頭尾空白與 `\r`、再去掉開頭的列表符號(`-`、`*`、`+`、`N.`)後,以 `RULE:` 開頭、或含 `★INVARIANT★`、或含 `[test:`。
  - 只看頂端版筆記裡**還一字不差留著**的結構行(逐行去頭尾空白後比對);那一行改掉或刪掉了就算處理過。判定紀錄的 `text` 是判定當時那版的原文,所以「改掉那一行」本身就是出口,不用重判。
  - 還留著、而且 `drift-acks.jsonl`(用 `_drift_load_acks` 讀頂端提交的樹,`_drift_ack_key` 比對路徑與原文)沒有 kind=reread 的同一行表態 → block 時印每一行(路徑、頂端版行號、原文節錄、判定理由、照留指令)、記 `blocked`、回 1;warn 時同樣印、記 `reminded`、回 0。
  - 非結構行、或結構行已改掉、或已表態:照舊只印判定點出幾行(不擋)。
  - 第一層與第二層同時成立時兩層都印,記一筆 `blocked`。
- **判不了的分法**:`_NoteRereadStop` 帶一個種類。
  - 參數錯(推送參數只給一個、範圍格式錯、終點找不到):回 2(跟 drift check 參數錯一樣)。
  - 環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線):照舊回 0、記 `skipped` 或 `none`。
  - 判不了(git 呼叫失敗、讀不到檔案清單、逾時、讀不了或讀不懂判定紀錄、沒預料的例外):block 時回 1、印原因與 `LUMOS_SKIP_REREAD_CHECK=1` 單次略過的寫法、記 `blocked`;warn 時照舊回 0、記 `skipped`。理由:不然把閘弄慢或弄壞就能繞過(drift check 核心判定與 m1 判不了也算要處理;它的 RULE 撤除條件判不了只列出,是另一道的取捨,本案不照那條)。
- **輸出**:所有輸出照舊走標準輸出(掛鉤丟掉標準錯誤)。block 而且擋下時不印結尾那句「這只是提醒、不擋」;`cmd_note_audit_reread_check` 的說明與 `--help` 改寫回傳碼。
- **照留表態**:`lumos drift ack <節點> <行號> --kind reread --reason "…"`。`_DRIFT_KINDS` 加 reread、`_DRIFT_KIND_NAMES` 加一個名字(成功訊息與 dry-run 會用到)、`drift scan` 的種類計數排除 reread(跟 m1 一樣,它只在推送時判);`_drift_ack_line_err` 多一個分支:那一行不是結構行就回 2,說明非結構行不需要表態;不收 `--tracked-in`(reread 不在會到期的種類裡)。筆記那一行之後被改,原文對不上,表態自然失效。
- **掛鉤與 CI**:推送前掛鉤 reread-check 那段改成「回傳 1 就擋、130 交給中斷處理、2 也擋並講參數錯」;CI 那一步拿掉 `|| true` 與 `continue-on-error`。
- **對消費專案的影響**:`lumos update` 之後兩道都變預設擋;要暫緩的專案在 `.lumos/config.json` 寫 `drift_check.old_sentence` 或 `note_reread.gate` 為 warn。CHANGELOG 同版寫明。

## 驗收條款

- [S1] 當設定檔沒寫 `drift_check.old_sentence`、寫成 null、整份讀不成 JSON、`drift_check` 不是物件或值看不懂,而推送範圍有名稱消失的舊句時,drift check 應回 1 並印舊句清單;壞設定的情況另印一句「照預設 block」。[test:t_old_sentence_default_blocks]
- [S2] 當 `drift_check.old_sentence` 寫 warn,而推送範圍有名稱消失的舊句時,drift check 應回 0 只印清單。[test:t_old_sentence_default_blocks]
- [S3] 當 `note_reread.gate` 沒寫、寫 block、寫 null 或值看不懂,而推送範圍裡有要對照的守檔筆記沒有已提交的判定紀錄時,reread-check 應回 1、印 prepare 指令、記一筆 blocked,而且不印「這只是提醒」那句。[test:t_reread_block_layer1_missing_verdict]
- [S4] 當 `note_reread.gate` 寫 warn,而有候選沒有判定紀錄時,reread-check 應回 0、記 reminded(原行為)。[test:t_reread_block_layer1_missing_verdict]
- [S5] 當候選全部對照過,判定紀錄點出一行 `RULE:` 結構行、頂端版筆記還一字不差留著那一行、也沒有照留表態時,reread-check 應回 1 並印那一行與照留指令。[test:t_reread_block_layer2_structural_rows]
- [S6] 當判定紀錄點出的結構行在頂端版筆記已改掉、或有 kind=reread 的同一行表態、或點出的只有非結構行時,reread-check 應回 0。[test:t_reread_block_layer2_structural_rows]
- [S7] 當同一個對照指紋有兩份已提交判定紀錄,只有較舊那份點出還留著的結構行時,reread-check 應照樣擋下。[test:t_reread_block_layer2_structural_rows]
- [S8] 當 block 時 reread-check 遇到 git 失敗、逾時、判定紀錄讀不懂或沒預料的例外,應回 1 並印原因與 LUMOS_SKIP_REREAD_CHECK。[test:t_reread_block_undecidable_blocks]
- [S9] 當 reread-check 遇到淺層 clone、不是 git 專案或範圍沒有新東西,應回 0;推送參數只給一個時應回 2。[test:t_reread_block_undecidable_blocks]
- [S10] 當設了 `LUMOS_SKIP_REREAD_CHECK=1`,reread-check 應回 0 並記 skipped-env。[test:t_reread_block_undecidable_blocks]
- [S11] 當 `drift ack --kind reread` 指到非結構行時,lumos 應回 2 並說明非結構行不需要表態,不寫帳。[test:t_drift_ack_reread_kind]
- [S12] 當 `drift ack --kind reread` 指到結構行時,lumos 應在 `drift-acks.jsonl` 寫入一筆含 kind=reread、path、text、reason 的表態,並印成功訊息。[test:t_drift_ack_reread_kind]
- [S13] 推送前掛鉤的 reread-check 段應在回傳 1 或 2 時擋下推送、130 時交給中斷處理;CI 的 reread-check 那一步不應帶 `|| true` 或 `continue-on-error`。[test:t_reread_block_hook_and_ci_wiring]

## 實務隱患

- 判定者不穩:同一批材料重派可能多點或少點幾行;只擋結構行把波動限制在最少的那一類,而且改掉那一行就放行,不會因重判而循環。
- 同一指紋多份紀錄取聯集:舊份點出、新份沒點出的行也會擋。這是刻意保守;那一行若已不成立,改掉或表態都是幾秒的事。
- 讀判定紀錄內容是新的成本:每篇候選多讀幾個小 json(各數 KB),在 30 秒預算內。
- 會被新行為弄紅、要一起改的既有測試:`t_note_audit_reread_check_never_blocks`、`t_note_audit_reread_check_wired`、`t_note_audit_reread_mode_and_isolation`,以及斷言舊句檢查預設 warn 的測試;改的是斷言、不是刪測試。
- 消費專案升級後第一次推送可能被擋;CHANGELOG 要寫明怎麼改回 warn。
- 已排除:金流:只動本機與 CI 的檢查回傳碼,不碰任何付款或計費
- 已排除:對外送出:閘只讀本機版控裡已提交的判定紀錄與表態檔,推送當下不呼叫模型、不送資料到外部
- 已排除:不可逆:擋下只是讓推送失敗,改設定或還原提交即恢復;表態檔只追加,舊表態留著無害
- 守衛面:本案就是改守衛的擋放行為,照走設計審與代碼審

## 回退

兩道都只要把設定改成 warn 就回到提醒。要整案回退,同一個 revert 提交還原:兩支設定解析的預設、reread-check 的回傳碼與判不了的分法、第二層、`drift ack` 的 reread 類別與種類表、掛鉤與 CI 的兩段、說明文字與 doctor 提示行、CHANGELOG 段落與改過斷言的既有測試。`drift-acks.jsonl` 裡 kind=reread 的表態留著無害(沒有讀它的程式;`drift scan` 讀到不認得的種類照舊略過)。

REVISIT:2026-12-04 上線滿 8 週照 RETIRE-IF 三條量:治理帳 `note-reread` 與 `drift-check` 的 blocked 與 skipped-env 事件、CI 在這兩步擋下的次數,抽第二層擋下的結構行人工判真假
