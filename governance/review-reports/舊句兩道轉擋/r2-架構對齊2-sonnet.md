severity: major

審查對象是 `/tmp/舊句兩道轉擋-r2.md`。對照 repo 是 `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone-reread-block`。以下 `scripts/lumos:行號` 都是那個 repo 裡的位置。

## 1. 分層與依賴方向:大致對齊,有一處新增的反向依賴

對齊的部分:
- 三段拆分(判定、兜底、印出記帳)跟鄰居一致。`_drift_m1_guarded` 兜底後交 `_drift_m1_report`(`scripts/lumos:39629`)。`_drift_retire_guarded` 交 `_drift_retire_report`(`scripts/lumos:38633`),它的 rc 也是在印出之前就定好(`scripts/lumos:38681` 附近)。
- 設計裡「判不了時 block 回 1」,跟 m1 的兜底一致(`scripts/lumos:39629` 起),也跟 `cmd_drift_check` docstring 說的「判不了的算要處理」一致(`scripts/lumos:38586`)。
- 設定解析照 `_drift_retire_config` 的寫法(`scripts/lumos:38503`)、`_drift_old_sentence_config`(`scripts/lumos:38533`)。
- 「總開關 off 時 m1 也不跑」照 retire 的先例(`scripts/lumos:38623` 的 `rt_mode` 判法)。
- 掛鉤與 CI 的寫法,見第 3 問。

**不對齊一條:筆記內容審這邊的 reread-check,要去呼叫存量漂移那一側的內部函式。**
- 設計要讓 `_note_reread_check` 呼叫 `_drift_unknown_hint`(加參數共用)、`_drift_load_acks` 和表態比對。
- 目前方向是反過來的:漂移檢查呼叫筆記內容審的零件(`_note_audit_resolve`、`_path_special_chars`、`_nodehome_*`)。
- 回頭重讀那一段(`scripts/lumos:33500` 到 `35016`)裡只有 `_drift_empty_tree` 一個 `_drift_` 呼叫(`scripts/lumos:34398`、`:34539`),那是純 git 常數。
- 表態比對現有做法是每一類各有自己的比對函式放在漂移那一側(例如 `_drift_m1_split_acked`,`scripts/lumos:37278` 附近)。如果新比對也放那裡再由 reread 呼叫,方向仍是新的。
- 設計沒說「共用的規則類行判斷」放哪一段,所以這個方向無從判定。
- ⚠ 交編排者:這是同檔兩道閘之間的橫向呼叫,我判不準算不算「跨層直呼」,先記 minor。

引句:「印原因與單次略過寫法(`_drift_unknown_hint` 加一個參數共用,不另寫)」

severity: minor
blocking: 否

## 2. 命名與錯誤處理:鍵名、環境變數逃生口、`blocked` 都對齊,四處不一致

對齊的部分:
- `note_reread.gate` 鍵名、值域 `block/warn/off`、壞設定一律 block,跟 `_note_shape_config`(`scripts/lumos:30326`)、`_drift_gate_config` 一致。
- `LUMOS_SKIP_REREAD_CHECK` 只認 `1`、記 `skipped-env`,既有且一致(`scripts/lumos:34912`)。
- 擋下走標準錯誤、開頭「擋下:」,跟 `scripts/lumos:39548` 一致。
- 攔下時記 `blocked`,跟 m1 的 `kind` 判法一致(`scripts/lumos:39628`)。

不對齊的有四條。

**(a) 照留指令的產生方式是第二套。**
- 設計寫「照留指令的節點名用 `shlex.quote`」,等於在 reread-check 裡另寫一個產生 `lumos drift ack …` 的地方。
- 專案已經規定提示指令的單一產生處是 `_drift_fix_hint`(`scripts/lumos:37645`,docstring 寫明「提示的單一產生處」),參數一律過 `_drift_sh`(`scripts/lumos:37636`)。
- `_drift_sh` 處理的情況裡,直接 `shlex.quote` 會漏掉兩種:
  - 以 `-` 開頭的節點名,要補成 `./` 開頭。
  - 路徑含特殊字元時,m1 不印可貼的指令(`scripts/lumos:37652` 附近)。
- 另外,中文節點名原樣印,不加引號。
- 這是第二種做法,所以判 major。

引句:「照留指令的節點名用 `shlex.quote`」

severity: major
blocking: 是

**(b) reread 表態記錄的兩個落地細節沒寫,會重蹈 retire 踩過的坑。**
- `_drift_ack_text`(`scripts/lumos:37444`)和 `_drift_ack_line_err`(`scripts/lumos:37453`)對 retire 特別處理:
  - 記整條邏輯行。
  - 行號要給條目第一行。
- 原因是 retire 當初只記實體行,表態永遠對不上(`scripts/lumos:35970` 附近的註解)。
- 設計說「讀工作目錄的那一行」,第二層則比對「同一行原文」。引句可能落在續行,沒有寫明記實體行還是整條。
- `cmd_drift_ack` 結尾把表態記成 `drift-check` 閘的 `acked` 事件(`scripts/lumos:37520`),但 reread 的統計和 RETIRE-IF 看的是 `note-reread` 閘。設計沒交代 reread 表態記在哪個閘名。

引句:「記 path、text、kind、reason,再加 `verdicts`:點出這一行的那些判定紀錄的對照指紋(排序去重)。」

severity: minor
blocking: 是

**(c) 判不了的原因分類,跟 `drift check` 不同。**
- 設計把 reread-check 的「終點找不到」(`_lens_full_sha` 回 None)改歸判不了,block 時回 1。
- `drift check` 對同一件事(`_note_audit_resolve`,`scripts/lumos:33741` 附近)的處理是回 2 當參數錯。註解寫「放行等於整道檢查沒跑」。
- 結果是同一種 git 失敗,本機掛鉤上 drift 放行、reread 擋下。
- ⚠ 設計有講理由(多半是 git 暫時失敗),但沒說為什麼跟鄰居不同。

引句:「reread-check 的終點找不到(`_lens_full_sha` 回 None,多半是 git 暫時失敗)改歸判不了,不是參數錯。」

severity: minor
blocking: 否

**(d) 只提醒路徑的事件名和輸出流,跟鄰居分岔。**
- 設計保留 `reminded`(理由是沿用既有 18 筆),判不了 + warn 記 `skipped`。
- drift-check 的 warn 路徑記 `warned`(`scripts/lumos:38740` 附近、m1 `scripts/lumos:39628`),而且「提醒:」走標準錯誤(`scripts/lumos:39549`)。
- 設計卻說「只提醒的內容照舊走標準輸出」。原本走標準輸出的理由是「掛鉤把標準錯誤丟掉」,設計自己也把那個丟棄拿掉了,理由已不在。
- `blocked` 事件要不要帶 `hard=True`,設計沒寫。drift 系每筆都明確寫。

引句:「warn 照舊記 `reminded`(沿用既有 18 筆的名字,不改成 `warned`)」

severity: minor
blocking: 否

## 3. 第二種做法:有三處做法專案原本沒有

**(a) 用環境變數 `CI` 改變閘的判定結果,專案沒有先例。**
- `CI` 在 `scripts/lumos` 只出現在兩處,都不改判定結果:
  - `scripts/lumos:232`:決定要不要多印一句修法。
  - `scripts/lumos:34980`:只用來給治理帳的來源標籤分 `ci` 和 `hook`。
- 掛鉤和 CI 之間行為不同,專案原本一貫是由呼叫端傳參數或差異化處理:
  - `scripts/hooks/pre-push:82`:`pp_touched_file` 的清單「CI 不給」。
  - 兩邊對非 1 的回傳碼處理不同,`ci.yml` 的註解就寫著「兩邊刻意不同」。
- 設計的「第一層在 CI 只印不擋」,改用閘內部讀 `CI` 環境變數來決定,是第二種做法。
- 副作用:本機 shell 或其他容器若碰巧設了 `CI=true`,本機第一層就不擋了。
- 對齊的做法是 `ci.yml` 那一步傳一個明確旗標,例如 `--no-layer1`,由呼叫端決定。
- 所以判 major。

引句:「環境變數 `CI` 有值時第一層只印、不擋」

severity: major
blocking: 是

**(b) 「已對照」有兩種定義。**
- 現況:`reread-prepare` 和 `reread-check` 都用 `_note_reread_committed`(`scripts/lumos:34697`)。它只列目錄、比檔名,檔名裡的對照指紋有就算已對照。prepare 的 docstring 還特別寫「口徑跟 check 同一支 `_note_reread_fps`」(`scripts/lumos:34735`),prepare 在 `scripts/lumos:34774` 用它略過已對照的篇。
- 設計:第一層要求「已提交、而且 `provenance_ok` 為真」,得讀內容。設計沒有提到 prepare 同步改。
- 後果:一份 `provenance_ok` 為假的已提交紀錄,check 判「沒對照」並印 prepare 指令,prepare 卻因為檔名已有該指紋而說「已對照,略過」。人必須知道要加 `--all`,而 check 印的指令沒有 `--all`。
- 這是在兄弟指令之間分出兩套「已對照」的口徑,而它們原本被刻意統一。判 major。

引句:「候選的對照指紋沒有任何已提交、而且 `provenance_ok` 為真的判定紀錄」

severity: major
blocking: 是

**(c) 表態多一個 `verdicts` 欄的綁法,跟 related/seq 不是同一套,而且設計的說法互相矛盾。**
- 設計說「reread 加進 `_DRIFT_BOUND_KINDS`」,但這個元組的定義是「表態要綁 related 與序號 seq 的種類」(`scripts/lumos:35035`)。它在三處有實質影響:
  - `cmd_drift_ack` 對這一類會先呼叫 `_drift_current_finding`(`scripts/lumos:37500`)。reread 沒有這種發現,會得到「現在不是 reread」而回 2。
  - `_drift_ack_buckets` 只收有 `related` 且 seq 合法的表態(`scripts/lumos:37283`)。reread 表態沒有 `related`,會被丟掉,第二層永遠找不到,變成永遠擋。
  - `_drift_split_acked` 對這一類的比對是「取 seq 最大的幾筆、全部涵蓋」(`scripts/lumos:37239`)。設計要的是「表態的 `verdicts` 含該指紋就算」,語意不同。
- 對齊的做法是跟 m1 一樣自成一支。m1 就是 `_drift_m1_split_acked`,「m1 不放進 `_DRIFT_BOUND_KINDS`」(`scripts/lumos:37245`)。同理還有 probe/retire 的期限那一支。
- 「每一類有自己的證據欄、自己的比對分支」這個模式有先例,所以結構方向對,但設計的文字要改成「新增自己的比對分支,不放進 `_DRIFT_BOUND_KINDS`」。
- 另外,設計只說「`_DRIFT_KIND_NAMES` 加名字」,沒提 `_DRIFT_KINDS`。後者決定 `_drift_load_acks` 收不收(`scripts/lumos:37232`)和 argparse 的 choices(`scripts/lumos:50311`),`_DRIFT_SCAN_KINDS` 的排除寫法在 `scripts/lumos:35025`。
- ⚠ 照字面實作會壞,所以 blocking 是;但結構上有先例,我判 minor 交編排者定奪。

引句:「reread 加進 `_DRIFT_BOUND_KINDS` 那一類的比對:第二層只認 `verdicts` 含點出那一列的紀錄指紋的表態」

severity: minor
blocking: 是

**(d) 規則類行判斷是專案裡第四種「摘要行分類」。**
- 現有的鄰居:
  - `_retire_lines`(`scripts/lumos:35951`):只用 `_ns_summary_logical`,以 `startswith("RULE:")` 加 `_ns_superseded` 判斷。
  - `_ns_test_ref_lines`(`scripts/lumos:32490`):用 `_note_summary_entries`,把 `INVARIANT_RE` 分成 contract/plain,`[test:` 用 `slot_parse`/`TEST_REF_RE`(`scripts/lumos:5450`)判。
  - `_contract_key_matches`(`scripts/lumos:44954`):docstring 寫「全檔唯一的合約行掃描,別再各寫一份」。
  - `_slot_summary_entries`(`scripts/lumos:4046` 附近):可傳前綴清單的摘要條目讀法。
- 設計:用 `_notelines_regions` 加 `_ns_summary_logical`。`_ns_summary_logical` 本身已經按 summary 區過濾,所以前者重複。
  - 前綴清單手寫了 7 個,沒有從 `SYMBOL_NAMES` 或 `_NOTE_SHAPE_PREFIX_RULES` 取。
  - `[test:` 寫成字串包含判斷,沒走 `slot_parse` 或 `TEST_REF_RE`。
  - 單行 `summary:` 寫法(`_ns_summary_logical` 讀不到)沒說怎麼辦,`_note_summary_entries`(`scripts/lumos:4027`)才處理。`_retire_lines` 有同樣的缺口,算有先例。
- 設計也沒說這支共用函式放哪一段。
- 結構上是「把兩處用的判斷收成一支」,方向對,但建議明寫:放哪一段、`[test:` 與前綴怎麼判,才不會長成又一份。判 minor。

引句:「在摘要區(`_notelines_regions` 判)而且所屬邏輯行(`_ns_summary_logical` 把接續行併起來)以 `RULE:` 開頭」

severity: minor
blocking: 否

**掛鉤與 CI 的寫法本身,跟鄰居對齊:**
- 掛鉤 `rr_rc` 那段改成跟 drift 那段(`scripts/hooks/pre-push:510` 到 `:520`)同一形狀:
  - `pp_stop_if_signaled`。
  - 回 1 擋下並印逃生段。
  - 其他非零講一句放行。
  - 不再 `2>/dev/null`。
- CI 照 drift 那步(`.github/workflows/ci.yml:239` 到 `:246`)的 `|| { rc=$?; … ::error:: … exit "$rc"; }`,拿掉 `|| true` 與 `continue-on-error`。

## 4. 落點:對齊

- 三篇都已存在,不需另開新節點。三篇的職責對得上:
  - `Systems/存量漂移守衛`:responsibility 寫明「推送前掛鉤與 CI 裡呼叫 drift check 的那一段、緊接在後呼叫 reread-check 的那一段」,about_code 含 `scripts/hooks/pre-push` 與 `ci.yml`。drift ack 與 m1 設定也歸它。
  - `Systems/筆記內容審`:管 reread-check 本體、`_note_reread_config`、範圍解析的 `reasons`。
  - `Systems/bound-tests-gate`:about_code 也含 hook 與 CI。它有「推送前掛鉤多一段只提醒的回頭重讀」整段(`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:107`),CI 步驟指紋的 WHY 也提到回頭重讀提醒(同檔第 17 行)。這兩處會被新行為弄成說謊,所以放進 `lands_in` 是對的。
- ⚠ 一個小提醒:共用的規則類行判斷函式,要在其中一篇當家寫明,另一篇用 `[[連結]]` 指過去。這取決於問 1、問 3(d)裡它最後放在哪一段,設計還沒定。

不對齊共 9 條,其中 major 3 條
