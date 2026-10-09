severity: major

派工尾端沒有附固定席節點,所以沒有節點可逐條判。

審查範圍:spec 全文逐節讀過,對照 `scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`、`scripts/test_lumos.py`、`governance/reread-verdicts/*.json` 查證。

## Finding

### F1 照留表態沒綁程式狀態,同一行第二次被點出會被舊表態直接放行
severity: major
blocking: 是(放行了該擋的,第二層的核心出口失效)
- spec 段落:〈設計〉照留表態。
- 失敗場景:
  1. 程式改動 A 後,判定者點出 `RULE:` 行 L。
  2. 作者表態「仍成立」,並提交。
  3. 程式改動 B 真的讓 L 失效,新對照指紋、新判定紀錄再點出同一行 L。
  4. 表態的鍵只有「路徑加原文加 kind」,第一輪的表態直接命中,第二次不擋。
- 引句:「筆記那一行之後被改,原文對不上,表態自然失效」
- 查證:
  - file: `scripts/lumos:37264` 非綁定種類只看 `k in keys`,不看程式狀態或期限。
  - file: `scripts/lumos:35035` 和 `scripts/lumos:35039` 對照 c2/c3/c6 綁 related 與 seq,probe/retire 會到期。
  - spec 明寫不收 `--tracked-in`,且〈實務隱患〉沒把這條永久豁免列為已接受的風險。
- 缺口:表態沒綁對照指紋或程式提交,就是一條對之後所有程式變動永久有效的免擋條。

### F2 「改掉那一行」的出口用整行相等比對,碰任何一字都算處理過
severity: major
blocking: 是(放行了該擋的)
- spec 段落:〈設計〉重讀第二層,第二個子點。
- 失敗場景:判定者點的是行內一小段,作者不修那段,只改同一行的別處就放行。典型是把 RULE 行的 `[confirmed:日期]` 往後改。
  - 這樣做不留帳,比表態還省事。
  - 還會讓舊句重新拿到 CLAUDE.md 說的「近期確認過的 RULE 可推翻程式」效力。
- 引句:「那一行改掉或刪掉了就算處理過」
- 查證:
  - 真實紀錄 6 筆 rows 的 `quote` 全是 `text` 的子字串。
  - `quote` 只有 18 到 62 字,整行 `text` 是 106 到 803 字(file: `governance/reread-verdicts/*.json`)。
  - file: `scripts/lumos:34868` 的 rows 同時存 `quote` 與整行 `text`,spec 卻只用整行 `text`。
- 建議方向:放行條件改成 `quote` 不再出現在頂端版那一行。

### F3 來源錨點對不上或空清單的判定紀錄,兩層都當作已對照
severity: major
blocking: 是(放行了該擋的)
- spec 段落:〈原問題與範圍〉不做那一條、〈設計〉第一層。
- 失敗場景:
  1. 作者寫一份只有 ` ```json\n[]\n``` ` 的報告,不派判定者。
  2. 跑 `reread-record`,它只印警告,照收並標 `provenance_ok: false`。
  3. 提交後,第一層因檔名前綴命中而放行,第二層因 rows 為空而放行。
- 引句:「閘只讀已提交的紀錄,所以 CI 也判得出」
- 查證:
  - file: `scripts/lumos:34876-34884` 對不上只警告。
  - file: `scripts/lumos:34697-34710` `_note_reread_committed` 只比檔名。
  - 前案 `Projects/守檔筆記對照改動_計劃.md:77` 寫「轉擋另案再決定要不要驗」,本案是那個另案,卻沒裁。
- ⚠ 交編排者:這是信任模型取捨(`provenance_ok: false` 的紀錄要不要算數),不是純實作缺口。

### F4 判不了與環境沒東西的分法,對不上 `_note_audit_resolve` 的原因種類
severity: major
blocking: 是(實作者無從分流,會讓 S8 與 S9 其中一邊判錯)
- spec 段落:〈設計〉判不了的分法。
- 引句:「判不了(git 呼叫失敗、讀不到檔案清單、逾時、讀不了或讀不懂判定紀錄、沒預料的例外)」
- 引句:「環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線)」
- 查證:
  - file: `scripts/lumos:33721` 淺層 clone、`33759` 讀不到檔案清單(git 失敗)、`33764` 沒有圖譜,這三個都用同一個種類 `skipped`。
  - file: `scripts/lumos:34953` 現行只用 `kind != "none"` 一刀切。
  - spec 要求 `_NoteRereadStop` 帶種類,卻沒說 `_note_audit_resolve` 的 `skipped` 要拆開。
  - 依 `skipped` 一律放行實作,檔案清單 git 失敗會在 block 下靜默通過,正是 spec 自己說要堵的繞法。
  - 依 `skipped` 一律擋實作,淺層 clone 會被擋,違反 S9。
- 附帶缺口:
  - file: `scripts/lumos:34941` 設定在這一行才讀到。
  - file: `scripts/lumos:34904-34924` 最外層例外處理器在設定讀到前拋的例外,不知道該用 block 還是 warn,spec 沒說。
  - 沒說第二層讀紀錄受不受 30 秒截止時間管。

### F5 第一層與第二層的先後,spec 前後矛盾
severity: minor
blocking: 否(兩種讀法回傳碼都是 1,只差輸出與帳)
- spec 段落:〈設計〉重讀第二層。
- 引句:「候選全部對照過之後才跑」
- 引句:「第一層與第二層同時成立時兩層都印,記一筆 `blocked`」
- 前者的前提是 `left` 為空,後者要兩層同時成立,兩者不可能同時為真。
- 要不要對已對照的子集先跑第二層,spec 沒定。

### F6 「照舊只印判定點出幾行」現行程式沒有這個行為
severity: minor
blocking: 否
- spec 段落:〈設計〉重讀第二層,第三個子點。
- 引句:「非結構行、或結構行已改掉、或已表態:照舊只印判定點出幾行(不擋)」
- 查證:file: `scripts/lumos:34927-35014` `_note_reread_check` 完全不讀判定紀錄內容。
  - 這是新行為,不是「照舊」。
  - 第二層通過時要記 `covered` 還是別的種類,spec 也沒定。

### F7 結構行定義兩處偏寬
severity: minor
blocking: 否(有表態可以出,只是多擋)
- spec 段落:〈設計〉結構行定義。
- 引句:「結構行 = `text` 去掉頭尾空白與 `\r`、再去掉開頭的列表符號」
- 偏寬一:「含 `[test:`」「含 `★INVARIANT★`」是整行子字串比對。
  - 圖譜裡 1628 行含 `[test:`,其中 1199 行不是以 RULE/WHY/PITFALL/KEY/FACT/FLOW/DEP 開頭,像 `[S1] … [test:…]` 這種驗收條款。
  - 另有 165 行提到 ★INVARIANT★ 卻不是 `KEY:` 開頭,多半是說明文。
  - 這些行被點出就得表態。
- 偏寬二:沒排除已標 `[status:superseded]` 的 RULE。
  - file: `scripts/lumos:35951-35960` 的 `_retire_lines` 排除了這種行,因為「標作廢就是處理完了」。
  - 本案卻會要求對已作廢的 RULE 表態。
  - 圖譜裡 RULE 開頭的行只有 23 行,實際量小,但判準與既有慣例不一致。

### F8 「會被弄紅的既有測試」清單不全
severity: minor
blocking: 否(跑測試就會發現,但 spec 宣稱的清單是錯的)
- spec 段落:〈實務隱患〉。
- 引句:「會被新行為弄紅、要一起改的既有測試:`t_note_audit_reread_check_never_blocks`」
- 漏列:
  - file: `scripts/test_lumos.py:62204-62211` 和 `62274-62277` 的 `_DR_CI_GATE_STEP_FP` 釘了 CI 步驟的指令、`continue-on-error` 和步驟名稱(名稱含「只提醒、不擋」)的指紋,拿掉 `|| true` 和 `continue-on-error` 必紅(`t_ci_yml_matrix_and_gates_shape`)。
  - file: `scripts/test_lumos.py:64305-64335` `t_note_audit_reread_check_reminds`,預設設定下斷言 `rc == 0` 與 reminded。
  - file: `scripts/test_lumos.py:64987-65002` `t_note_audit_reread_non_utf8_path_logs`,同樣斷言 `rc == 0` 與 reminded。
  - file: `scripts/test_lumos.py:65415-65425` `t_note_audit_reread_prepare_skips_uncommitted_records`,斷言 `rc == 0`。

### F9 掛鉤對 128 以上其他回傳碼的處理沒定
severity: minor
blocking: 否(CI 無 `|| true` 後會補擋)
- spec 段落:〈設計〉掛鉤與 CI。
- 引句:「推送前掛鉤 reread-check 那段改成」
- 現況:file: `scripts/hooks/pre-push:540-544` 只特判 130,其餘非零(含 143、137)印「照推——這道只提醒、不擋」,`t_note_audit_reread_check_wired` ⑦ 也釘著 143 照推。
- 問題:
  - spec 只列 1、2、130,沒說 137 與 143 要不要擋。
  - 保留舊行為就留著一條「殺掉進程就能繞過」的路,與 spec 自己說的「把閘弄慢或弄壞就能繞過」理由矛盾。
  - 掛鉤那句「只提醒、不擋」要改,spec 沒列為待改文字。
  - 對照 file: `scripts/hooks/pre-push:70-75` drift 那段用 `pp_stop_if_signaled` 擋所有 128 以上。

### F10 drift_check.gate 設 off 的專案,舊句檢查會從 warn 變 block
severity: minor
blocking: 否(有 `old_sentence: warn` 可退)
- spec 段落:〈設計〉對消費專案的影響。
- 引句:「要暫緩的專案在 `.lumos/config.json` 寫 `drift_check.old_sentence` 或 `note_reread.gate` 為 warn」
- 查證:file: `scripts/lumos:38632-38637` 與 `38711-38715` 舊句檢查獨立於 `gate`,`gate: off` 只關 c1 到 c5。
  - 刻意關掉存量漂移檢查的專案升級後也會被擋。
  - spec 與 CHANGELOG 預告沒點出這一類。

## 逐節結果
- 〈原問題與範圍〉:治理帳數字核對屬實。
  - note-reread 為 none 12、recorded 5、reminded 18。
  - drift-check 的 old-sentence 為 passed 35、沒有 warned 或 blocked。
  - 只有 F3 涉及「不做」那條。
- PRIOR-ART、RETIRE-IF:已讀,無 finding。
  - 引用的 `_drift_load_acks`(`37220`)、`_drift_ack_key`(`37235`)和預留的「轉擋還沒做」(`34650`)都存在。
  - `drift-acks.jsonl` 裡 reread 的表態在回退後會被 `_drift_load_acks` 以 kind 濾掉(`37232`)。
- 〈設計〉名稱消失檢查開關:只有 F10。
- 〈設計〉重讀開關、第一層:已讀,無 finding。`_metric_gate_off` 取 `[0]` 的回傳形狀不變。
- 〈設計〉第二層:F1、F2、F5、F6、F7。
  - `\r`、前導空白、列表符號和 `summary: |-` 內縮排的 RULE 行,用 `strip()` 與列表符號去除能正確判斷。
  - 路徑 NFC 與原文 strip 與 `_drift_ack_key` 一致。
  - 同指紋多份紀錄取聯集本身沒有判錯路徑。
- 〈設計〉判不了的分法:F4。
- 〈設計〉輸出、照留表態:
  - `_DRIFT_KIND_NAMES` 加名字的理由屬實(`37508` 與 `37521` 會用到)。
  - `_DRIFT_SCAN_KINDS` 要排除 reread 的說明屬實。
  - 無 finding。
- 〈設計〉掛鉤與 CI:F9;CI 步驟的指紋釘見 F8。
- 〈驗收條款〉:S1 到 S13 的交叉引用都存在,測試名是待新增。
  - 缺條款:沒有 F1、F2、F3 的負向案例,沒有「設定壞掉時 reread 照預設 block」的獨立條款。
- 〈實務隱患〉:F8。
- 〈回退〉:已讀,無 finding。

## 實務隱患鏡頭
- 併發:無。
  - 閘只讀已提交的樹。
  - 表態寫入走既有的 `_vault_write_lock`,判定檔原子換名。
  - 別的會談未提交的紀錄不會被讀到。
- 效能:有風險,屬 F4 的附帶缺口。
  - 第二層每篇候選多讀幾個小 JSON,成本可忽略。
  - 但預算耗盡由「提醒略過」變成「擋」。
  - drift 的治理帳已出現過一筆「超過 60 秒預算」的 warned。
  - 大 repo 或新分支首推從空樹掃,可能被誤擋。
  - 出口是 `LUMOS_SKIP_REREAD_CHECK`,CI 仍會重判。
- 資源:無。沒有新增常駐進程,也沒有無界讀取。判定檔只累積,每篇候選只讀同前綴那幾份。
- 回滾:設定改 warn 或整案 revert 都成立,這點已核對屬實。

最嚴重的是 F1、F2、F3:第二層的兩個出口(改一個字、永久表態)和第一層的資格(任何紀錄都算)都能在不修舊句的情況下放行;blocking 共 4 條(F1 到 F4)。
