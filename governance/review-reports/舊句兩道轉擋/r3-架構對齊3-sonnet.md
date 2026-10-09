severity: minor

審查對象是 `/tmp/舊句兩道轉擋-r3.md`,對照的 repo 是 aspidochelone-reread-block 工作樹。沒有 major,有 6 條 minor。

## 1. 分層與依賴方向:大致對齊,沒有跨層直呼

- **子開關照總開關(對齊)。**
  - 設計說名稱消失檢查沒寫 `old_sentence` 時改照 `drift_check.gate`。這跟 `_drift_retire_config(cfg, bad, gate)` 一樣:先解析 gate,再傳進子開關。
  - 對照 file: `scripts/lumos:38503`、`scripts/lumos:38484`。
  - 「gate=off 時 retire 一律不跑、m1 明寫了仍照跑」這個不對稱,設計保留了原狀,也一致。
  - 對照 file: `scripts/lumos:38586`(`rt_mode = ... if mode != "off" else "off"`)。
- **三段拆法(對齊)。** 判定、兜底、印出記帳三段,回傳碼在印出前定好,跟 `_drift_m1_guarded`(`scripts/lumos:39629`)和 `_drift_retire_guarded`(`scripts/lumos:38633`)同形。
- **新模組呼叫既有共用件(對齊)。**
  - reread-check 會呼叫 `_drift_load_acks`、`_drift_fix_hint`、`_drift_unknown_hint`,屬於回頭重讀區段往存量漂移區段呼叫。
  - 單檔 CLI 裡已有這種先例:`_drift_empty_tree` 被 `scripts/lumos:34398` 和 `scripts/lumos:34539` 呼叫。
  - 反方向的先例是 `_path_special_chars`(`scripts/lumos:34341`)被存量漂移區段呼叫,`_reread_rule_entry` 照這個放法。
  - 所以不算跨層直呼。
- **`_drift_reread_split_acked`(對齊)。**
  - 它自成一支、不進 `_DRIFT_BOUND_KINDS`,取 `verdicts` 聯集,形狀同 `_drift_m1_split_acked`(`scripts/lumos:37293`)。
  - 它由 reread-check 直接呼叫,不經 `_drift_split_acked` 的 m1 分派(`scripts/lumos:37245` 一帶)。reread 發現不走那條流程,所以不會出事。
  - 但 `_drift_ack_buckets`(`scripts/lumos:37278`)會把 reread 表態放進一般的 `keys` 堆。設計沒提這點,建議實作時在註解寫明。
- **`undecidable` 原因種類(對齊,但行為比 drift check 嚴)。**
  - 只走 `reasons` 這條 quiet 路徑,其他呼叫端不受影響。對照 file: `scripts/lumos:33701`、`scripts/lumos:33775`。
  - 同一個「讀不到頂端檔案清單」,drift check 目前是靜默回 0。reread 在 block 模式會回 1,比鄰居嚴。這符合 drift check 自己 docstring 的「判不了算要處理」,所以不另算 finding。

## 2. 命名與錯誤處理:大致對齊,有 5 處小不一致

- **對齊的部分。**
  - 回傳碼:參數錯回 2、環境沒東西可判回 0、判不了在 block 回 1,跟 `cmd_drift_check`(`scripts/lumos:38586`)一致。
  - 治理帳:`blocked` 帶 `hard=True`、`reminded` 沿用舊名,跟 `_drift_retire_ledger`(`scripts/lumos:38656` 一帶)一致。`note-reread` 的例行事件白名單(`scripts/lumos:1363`)也不受影響。
  - 環境變數 `LUMOS_SKIP_REREAD_CHECK` 沿用現有名稱。
  - 擋下原因走標準錯誤、開頭「擋下:」,跟 `_drift_retire_print` 一致。
  - 掛鉤 128 以上交 `pp_stop_if_signaled`,跟 `scripts/hooks/pre-push:512` 同一種處理。
  - `drift ack` 的 `--kind` 選項由 `_DRIFT_KINDS` 自動帶出,表態事件照現有寫在 `drift-check` 閘(`scripts/lumos:37519`)。
  - 版本升 v1.3 加 CHANGELOG 同版一段,跟 v1.1、v1.2「改了掛鉤就升版」的慣例一致(`CHANGELOG.md`)。
  - `_DRIFT_SCAN_KINDS` 需要改成同時排除 m1 和 reread(`scripts/lumos:35025`)。設計寫的是「跟 m1 一樣排除」,方向對。
- **不對齊的部分:** F1 到 F5,見下。

### F1 設定值 block 的效力變成取決於呼叫端
severity: minor
blocking: 否

引句:「只有推送前掛鉤帶 `--gate`」

- `note_audit`、`drift_check`、`note_shape`、`node_home` 這一族的 `*.gate` 都是設定決定,掛鉤和 CI 呼叫同一支碼,看到 block 都擋。對照 file: `scripts/lumos:38586`、`scripts/hooks/pre-push:510`、`.github/workflows/ci.yml:239`。
- 設計讓 `note_reread.gate=block` 在 CI 不生效,要靠旗標 `--gate`。這是設定與旗標兩個條件合取,是這一族第一次出現。
- 設計引的先例 `pp_touched_file` 是掛鉤給輸入清單,不是改擋放模式。對照 file: `scripts/hooks/pre-push:83`。
- 比較貼近的先例是 `doctor --strict/--ci`(`scripts/lumos:49508`)和 `bound-tests --advisory`(`scripts/lumos:50396`),它們確實是呼叫端旗標決定嚴格度。但沒有一個是「設定寫 block 還要再加旗標才算」。
- 旗標名 `--gate` 跟 `loop status --gate`(`scripts/lumos:49638`)同樣是「升級成閘」的意思,語意不衝突。
- ⚠ 我判 minor。這是人裁範圍(Enzo 裁定 CI 維持提醒),要不要視為「第二種做法」交編排者。若判為第二種做法,這條就升 major。

### F2 「設定讀到之前的例外」改讀工作目錄設定,鄰居沒有這層
severity: minor
blocking: 否

引句:「改讀工作目錄的 `.lumos/config.json` 判模式」

- 各閘的設定都從被推頂端提交讀(`_nodehome_reader(root, tip)`),讀不到或寫壞就走預設值,沒有「再退一層讀工作目錄」。對照 file: `scripts/lumos:38586`、`scripts/lumos:32997`、`scripts/lumos:34936`。
- 直接讀工作目錄設定在 repo 裡有先例(`scripts/lumos:26781` 的 `stack_questions`),但都是主要來源,不是退路。
- 現行程式裡 `_note_reread_check` 已在算候選之前先讀設定。「設定讀到之前」只剩 `_lens_full_sha` 一類極少數例外。這層可以省,直接照預設 block。
- 若保留,要在筆記說明為什麼這道閘需要鄰居沒有的第二層退路。

### F3 預設值沒有具名常數,RETIRE-IF 的「設定一行」站不住
severity: minor
blocking: 否

引句:「就把該道的預設改回 warn」

- 存量漂移有 `_DRIFT_DEFAULT_GATE` 這種具名常數,並附上裁定出處註解。2026-09-30 轉擋就是改這一行。對照 file: `scripts/lumos:35045` 到 `scripts/lumos:35048`。
- 現在的 `_note_reread_config` 把 `"warn"` 字面值寫在每個分支裡(`scripts/lumos:34627` 到 `scripts/lumos:34650`)。照設計改成 block,會散在 6 處以上。
- 建議新增 `_NOTE_REREAD_DEFAULT_GATE` 加一段裁定註解。名稱消失檢查的新預設同理,走總開關,不另存字面值。

### F4 「同一套讀法」沒指到共用函式,reread-check 與 `drift ack` 可能各寫一份
severity: minor
blocking: 否

引句:「用 `_note_summary_entries` 同一套讀法」

引句:「而且工作目錄 `governance/reread-verdicts/` 裡至少有一份檔名合規」

- `_note_summary_entries(n)` 吃的是已解析的筆記物件(`scripts/lumos:4027`)。
- reread-check 讀的是頂端提交的文字。鄰居的文字版是 `_ns_summary_logical(text)`,`_retire_lines`、`_drift_ack_text`、`_drift_ack_line_err` 都用它。對照 file: `scripts/lumos:31963`、`scripts/lumos:35951`、`scripts/lumos:37451`、`scripts/lumos:37456`。
- 兩者的差別是單行 `summary:` 寫法:`_note_summary_entries` 會算進去,`_ns_summary_logical` 不會。
  - 若 check 用前者、`drift ack` 沿用 retire 的後者,單行寫法的規則條目會被擋住,卻沒辦法表態。
  - 反過來也會出現行為不一致。
- 設計只點名了共用 `_reread_rule_entry`(判斷條目是不是規則類)。
  - 「讀出條目 {行號: 整條}」和「判定紀錄某列 → 比對字串 → 對上哪個條目」這兩段,第二層和 `drift ack` 都要用,設計寫的是「同第二層的取法」,沒有指名同一支。
  - 這正是 `_note_summary_entries` 註解裡寫過的「S16 到 S19 原本各自重組」那種重複的來源。
- 建議在設計裡指明用一支文字版共用函式(以 `_ns_summary_logical` 為底,補單行 summary)。
- 引句 2 是 `drift ack` 的檢核條件。第二層的比對字串取法與判定紀錄載入也該落在同一組共用函式裡。

### F5 擋下時的逃生訊息,工具和掛鉤誰印沒分清
severity: minor
blocking: 否

引句:「另印 `LUMOS_SKIP_REREAD_CHECK=1 git push`」

引句:「回 1 擋下並印逃生段」

- 設計〈輸出〉段說工具(reread-check)印單次略過寫法和改 warn 的寫法。〈掛鉤與 CI〉段又說掛鉤印逃生段。
- 鄰居的分工是兩邊都印,內容不同:
  - 工具印每一筆的改法和該閘專屬的設定鍵,例如 `_drift_m1_report`(`scripts/lumos:39668` 前後的「改的是 old_sentence」)和 `_drift_unknown_hint`(`scripts/lumos:39477`)。
  - 掛鉤印一段通用的逃生:`SKIP_*` 加設定開關加「改 gate 沒用」(`scripts/hooks/pre-push:513` 到 `scripts/hooks/pre-push:517`)。
- 設計沒講 reread 是照這個分法,還是由某一邊獨印。可能兩邊重複,也可能都漏。
- 建議明寫:工具印「第幾層、改什麼、照留指令」,掛鉤印「`SKIP` 與 `note_reread.gate` 改 warn」。

## 3. 第二種做法:只有 F1 值得一提,其餘是新機制但零件用既有的

- 表態比對(聯集、不進 `_DRIFT_BOUND_KINDS`)、判不了提示共用 `_drift_unknown_hint`、照留指令由 `_drift_fix_hint` 加分支、規則類判斷放常數段共用,全照既有做法。
- 「讀判定紀錄內容、比對引句」是新機制,設計自己也這樣說明,而且零件(`_nodehome_cat_blobs_capped` 在 `scripts/lumos:29495`、`_NOTE_REREAD_VERDICT_NAME_RE`)都是既有的。
- 表態事件記在 `drift-check` 閘、擋下事件記在 `note-reread` 閘,是因為 `cmd_drift_ack` 本來就把所有種類的表態寫到 `drift-check`(`scripts/lumos:37519`)。這是沿用,不算新做法。
- 但 RETIRE-IF 抽樣時要看兩個閘的帳,REVISIT 那條已寫「`drift-check` 的 blocked 與 skipped-env」,算有照顧到。
- F1 的呼叫端旗標與 F2 的退路層,是這份設計唯二偏離「各閘由設定檔決定、工作目錄不當設定來源」的地方。

## 4. 落點

### F6 `lands_in` 漏了 README 圖產生器那篇
severity: minor
blocking: 否

引句:「[[Systems/README圖產生器]] 管的推送前關卡圖」

- 〈要一起改的說法〉要把關卡圖裡「重讀」那一列改成擋。圖的文字寫在 `assets/readme-diagrams/generate.py`:`scripts/lumos` 之外的 `assets/readme-diagrams/generate.py:488`、`assets/readme-diagrams/generate.py:497`、`assets/readme-diagrams/generate.py:499`(中英文各一份),要改。
- 家是 `Systems/README圖產生器`(about_code 列 `assets/readme-diagrams/generate.py`)。
- 專案鐵則 5 要求改到的程式檔的家要在 `lands_in` 裡,現在的 `lands_in` 只有三篇,應補上這一篇。

其餘的落點判斷:

- `Systems/存量漂移守衛` 管 `scripts/lumos` 的 drift 部分、`scripts/hooks/pre-push`、`ci.yml`,放 `--kind reread`、掛鉤和設定解析是對的。
- `Systems/筆記內容審` 已有 reread 描述(17 處提及),放判定、兩層和 `_note_audit_resolve` 是對的。
- `Systems/bound-tests-gate` 現有「只提醒的回頭重讀」段(`bound-tests-gate.md:107`),要改寫,也是對的。
- 不需要另開新 Systems 節點。

不對齊共 6 條,其中 major 0 條
