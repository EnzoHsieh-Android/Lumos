severity: major

審的是 `/tmp/舊句兩道轉擋-r2.md`,對照 `aspidochelone-reread-block` 的 `scripts/lumos`。派工沒有附固定席節點,所以沒有節點可判。實驗檔只放在 `/tmp/lumos-seat-work/舊句兩道轉擋/邊界2-sonnet/`。

**F1 空引句且空 text 時,第二層會對整篇每條規則類行發作**
severity: major
blocking: 是(判準:一個判定者常見的錯誤輸出就能讓整篇規則行全部被擋,而 spec 沒有任何防線)
- spec 段落:〈重讀:候選與兩層〉第二層的引句取法。
- 輸入:判定者的 json 把 `line` 指到空白行(行號差一常見),或漏寫 `quote`。
- 壞在哪:`cmd_note_audit_reread_record` 收這一列時,`text` 是那一版筆記該行的原文,空白行就是 `""`。`quote` 缺時存成 `""`。第二層的規則是引句缺或空就退回 `text`,於是引句變成 `""`,`"" in 全文` 恆真,「含這段引句的每一行」就是每一行,所有規則類行都成為要處理。
- 後果:`drift ack --kind reread` 的條件「某列引句出現在這一行」對 `""` 也恆真,所以得逐行表態。
- 查證:file: `scripts/lumos:34670-34693`(`_note_reread_rows` 不擋空 `quote`,也沒要求 `text` 非空)。我用 `存量漂移守衛.md` 實測,`""` 命中 175 行,其中規則類行 41 條,要 41 次 ack。
引句:「`quote` 缺或空時退回整行 `text`。」

**F2 `drift ack --kind reread` 的接線寫法照字面做會失敗,漏了 `_DRIFT_KINDS`**
severity: major
blocking: 是(判準:照 spec 字面實作,S18 不可能過)
- spec 段落:〈照留表態〉。
- 輸入:`lumos drift ack <節點> <行號> --kind reread --reason ...`。
- 壞在哪(三點):
  1. spec 把 reread 放進 `_DRIFT_BOUND_KINDS` 那一類。但 `cmd_drift_ack` 對這一類會呼叫 `_drift_current_finding`,它只回 c2/c3/c6 的發現,reread 永遠回「現在不是 reread」並回 2。
  2. `_drift_ack_buckets` 只收有 `related` 且 `seq` 合法的表態,spec 的欄位清單沒有 `related`。
  3. spec 只說 `_DRIFT_KIND_NAMES` 加名字,沒提 `_DRIFT_KINDS`。`--kind` 的 `choices` 和 `_drift_load_acks` 的過濾都吃 `_DRIFT_KINDS`,不加則 argparse 直接拒,也讀不回來。§回退卻又假設 reread 在 `_DRIFT_KINDS` 裡。
- 附帶:`_DRIFT_SCAN_KINDS` 是「全部去掉 m1」派生的,加進去後 scan 迴圈會多出 reread。S19 只有條款,沒說怎麼排除。
- 查證:file: `scripts/lumos:37500-37506`、`:37283-37286`、`:37411`、`:35025`、`:39742`、`:50311`。
引句:「reread 加進 `_DRIFT_BOUND_KINDS` 那一類的比對」

**F3 第二層「讀所有判定紀錄」沒有檔名過濾,資料夾裡一個雜檔會讓全 repo 的候選都判不了**
severity: major
blocking: 是(判準:一個殘檔就把每個推送擋成判不了,CI 也紅且沒有環境變數可略過;而第一層的讀法明明有過濾)
- spec 段落:〈重讀:候選與兩層〉第二層的讀檔範圍。
- 輸入:`governance/reread-verdicts/` 提交進一個 `.tmp-wlf` 殘檔、`.gitkeep`、README,或子資料夾。
- 壞在哪:`_write_lf` 被中斷會留下 `<名>.json.<pid>-<hex>.tmp-wlf`,而 `cmd_note_audit_reread_record` 印的是 `git add governance/reread-verdicts`,整個資料夾一起加,殘檔會被提交進去。`_note_reread_committed` 用 `_NOTE_REREAD_VERDICT_NAME_RE` 過濾,第二層「所有判定紀錄」沒說要過濾。
- 後果:殘檔半寫的 JSON 讀不成,直接成為「判定紀錄讀不懂」而回 1。子資料夾經 `cat-file --batch` 回 None,也被當讀不到。
- 查證:file: `scripts/lumos:34323-34324`、`:34697-34710`、`:19333`、`:29495-29521`。
引句:「讀頂端提交裡 `governance/reread-verdicts/` 下所有判定紀錄」

**F4 短引句或通用引句會在筆記別處命中無關的規則類行**
severity: minor
blocking: 否(判準:誤擋有逃生,但 spec 沒設引句最短長度,也沒用紀錄裡的 `line` 和 `text` 當錨)
- spec 段落:〈重讀:候選與兩層〉第二層的比對步驟。
- 輸入:判定者用 `warn`、`m1` 這類短詞當 `quote`,或被點的正文句和某條摘要 `RULE:` 行內容重複。
- 壞在哪:規則是「含這段引句的每一行」只要有一行是規則類就要處理。在 `存量漂移守衛.md` 實測,`warn` 命中 10 行(規則類 4 條),`m1` 命中 27 行(規則類 9 條)。判定者點的是正文,被擋的卻是摘要的 `RULE:` 行。
- 查證:紀錄本來就存了 `line` 和 `text`,spec 完全沒用到。
引句:「看含這段引句的每一行是不是」

**F5 引句找不到一律當「已處理」,對轉述、去標記、跨行的引句靜默放行**
severity: minor
blocking: 否(判準:fail-open,只在判定者引句不是逐字時發生,實測 6 列都逐字)
- spec 段落:〈重讀:候選與兩層〉第二層的「找不到」分支。
- 輸入:判定者去掉反引號或 `**` 的引句、用 `…` 縮寫的引句,或含 `\n` 跨兩行的引句。
- 壞在哪(兩種):
  1. 找不到 → 算處理過。`cmd_note_audit_reread_record` 從不驗 `quote` 是否真在 `text` 裡,所以轉述過的引句永遠找不到、永遠放行。
  2. 跨兩行的引句整段能在全文找到,但沒有任何單一實體行含完整引句,「含這段引句的每一行」是空集合,同樣靜默放行。
- 查證:file: `scripts/lumos:34670-34693`。我對現有 5 份紀錄的 6 列實測,引句都是 `text` 的子字串,所以今天沒壞。
引句:「頂端版筆記全文找不到這段引句 → 這一列算處理過(改掉或刪掉了)。」

**F6 第一層的 CI 豁免靠使用者能控制的環境變數,而且不留帳**
severity: minor
blocking: 否(判準:標題閘可被靜默繞過,而 RETIRE-IF 的 skipped-env 計數看不到)
- spec 段落:〈重讀:候選與兩層〉第一層。
- 輸入:`CI=0 git push`、`CI=false`,或 shell 設定檔裡 export 了 `CI`。
- 壞在哪:條件是「有值」,`CI=0` 也算有值。現有程式也是 `src = "ci" if os.environ.get("CI")`。這條路徑沒進 `skipped-env`,RETIRE-IF 的「skipped-env 累計 3 次以上」抓不到。spec 沒區分本機掛鉤和真 CI(例如判斷 `GITHUB_ACTIONS`)。
- 查證:file: `scripts/lumos:34986`。
引句:「環境變數 `CI` 有值時第一層只印、不擋」

**F7 讀端有 256 KB / 8 MB 上限,寫端沒有上限也沒有清理途徑**
severity: minor
blocking: 否(判準:要極端輸入才觸發,且有 `LUMOS_SKIP_REREAD_CHECK` 和 warn 兩個逃生口)
- spec 段落:〈重讀:候選與兩層〉末段與〈實務隱患〉。
- 輸入:一份判定者回報點了幾百行、每行很長的紀錄,或紀錄累積到總量超過 8 MB。
- 壞在哪:
  - `_note_reread_rows` 不限列數,`text` 存整行原文不截。能寫進去的紀錄,讀端可能超過 256 KB 而判不了。
  - 「刪掉那份紀錄再提交」會同時丟掉第一層的對照證據,重派判定者又寫出同樣大的紀錄,繞不出來。
  - 超過總量時,`_nodehome_cat_blobs_capped` 會依檔名(指紋)順序跳過後面的檔,被跳過的是隨機的,可能正好是最新的。
  - spec 沒有任何保留、輪替或清理政策。
- 數字更正:spec 寫的「5 份約 20 KB」不對,實測 7855 位元組。
- 查證:file: `scripts/lumos:29495-29521`。
引句:「現在 5 份約 20 KB;上限 8 MB 擋住惡意大檔;」

**F8 治理帳 detail 沒有上限**
severity: minor
blocking: 否(判準:帳寫出的行可能很大,但不影響判定)
- spec 段落:〈回傳碼與判不了〉末段的治理帳。
- 輸入:F1 或 F4 這類命中幾十到幾百條規則行的情況。
- 壞在哪:detail 要記「第二層要處理的每一行」。第一層的帳有 `[:50]` 截斷,這裡沒有。`_gate_event_build` 把 `note` 和 `detail` 各存一份,相同內容寫兩次。
- 查證:file: `scripts/lumos:34980-34983`(第一層的截斷)。
引句:「第二層要處理的每一行(路徑、引句前 80 字、判定紀錄指紋)」

**F9 掛鉤改成 128 以上就停,違反「改成 warn 就回到提醒」的回退保證**
severity: minor
blocking: 否(判準:只在被外部砍掉時觸發,回退說法不實)
- spec 段落:〈掛鉤與 CI〉與〈回退〉。
- 輸入:`note_reread.gate` 是 warn 或 off,reread-check 被 OOM 殺掉(137)或遇到 SIGPIPE(141)。
- 壞在哪:現行掛鉤刻意只讓 130(Ctrl-C)停整支掛鉤,其他被砍掉的放行。spec 改成 128 以上都停,掛鉤看不到設定,warn 模式下也會擋。
- 查證:file: `scripts/hooks/pre-push:70-75` 與 `:538-547`。
引句:「推送前掛鉤 reread-check 那段照其他會擋的閘:128 以上交 `pp_stop_if_signaled`」

**F10 紀錄的 `note` 欄比對、改名、設定讀不到前的例外**
severity: minor
blocking: 否(判準:都是邊角,且第一層在本機補得了大半)
- spec 段落:〈重讀:候選與兩層〉與〈開關〉。
- 輸入(兩種):
  1. 筆記改名或搬資料夾,或路徑含非 UTF-8、超過 1000 字。
  2. 專案設 warn 或 off,而 `_lens_full_sha` 暫時失敗。
- 壞在哪:
  1. `note` 欄存的是 `_note_reread_show` 之後的字串(替換、截 1000 字)。spec 沒說比對時也要過同一個轉換。舊路徑的紀錄會被靜默略過,第二層對改名後的筆記失效。本機因為對照指紋含路徑,第一層會要求重判;CI 不擋第一層,所以 CI 漏掉。
  2. spec 說設定讀不到之前的例外照 block。tip 在讀設定之前就查不到,這時 warn 或 off 的專案也會回 1,和 S14「warn 時回 0」衝突。
- 查證:file: `scripts/lumos:34360-34364`、`:34885`、`:34945-34954`。
引句:「設定讀不到之前就發生的例外,照 block 處理(預設就是 block)。」

**F11 摘要接續行的規則類判斷,spec 引用的函式做不到**
severity: minor
blocking: 否(判準:本 repo 沒有接續行,但寫給消費專案的規則會漏)
- spec 段落:〈重讀:候選與兩層〉第二層的規則類判斷。
- 輸入:摘要裡折行的 `RULE:` 條目,引句落在接續行。
- 壞在哪(兩點):
  1. `_ns_summary_logical(text)` 預設只回「條目第一行 → 整條」,接續行要傳 `cont` 參數才有對應。spec 沒提 `cont`,引句在接續行就查不到所屬條目,被當成非規則類而靜默放行。
  2. `_drift_ack_line_err` 的簽名沒有 `root`,而 reread 的「至少一份判定紀錄點出這一行」要讀 `governance/reread-verdicts/`,需要改簽名。
- 實測:本 repo 全部筆記的摘要接續行是 0。
- 查證:file: `scripts/lumos:31963-31979`、`:37453`。
引句:「所屬邏輯行(`_ns_summary_logical` 把接續行併起來)」

**F12 表態的讀取來源、多筆表態語意、指紋欄位沒講清**
severity: minor
blocking: 否(判準:spec 缺口,實作者會各猜各的)
- spec 段落:〈照留表態〉與〈重讀:候選與兩層〉。
- 輸入:同一行有多筆 reread 表態,或本機有未提交的表態。
- 壞在哪(三點):
  1. 第二層讀的是頂端提交裡的表態檔,還是工作目錄,spec 沒寫。`_drift_load_acks(where=)` 兩種都有。工作目錄版本讓本機放行、CI 失敗。
  2. 「加進 `_DRIFT_BOUND_KINDS` 那一類」的現行語意是只取 `seq` 最大的那幾筆。兩個分支各自表態再合併,舊那筆的 `verdicts` 指紋不會被算進來,反而重擋。
  3. 「對照指紋」到底是紀錄的 `contrast_fp` 欄,還是檔名前綴,spec 沒說。第一層現在用檔名前綴,而 `provenance_ok` 要讀內容。
- 查證:file: `scripts/lumos:37220-37233`、`:37262-37290`。
引句:「第二層只認 `verdicts` 含點出那一列的紀錄指紋的表態」

**F13 「上線前 5 份紀錄在上線推送要處理一次」不成立**
severity: minor
blocking: 否(判準:只是 spec 宣稱不準,對行為無害)
- spec 段落:〈實務隱患〉。
- 實測:對現在的筆記逐列比對,6 列裡 3 列的引句已不在筆記中(算處理過),其餘 3 列都不是規則類行:
  - 1 列在正文(`筆記內容閘.md` 第 57 行)。
  - 1 列是沒有 `[test:` 的 WHY(`存量漂移守衛.md` 第 46 行)。
  - 1 列的引句已找不到。
  所以規則類行是 0 條。
- 這是投稿者沒量就寫的宣稱。上線推送真正的負擔是第一層:`scripts/lumos` 會被許多家筆記共用,上線那次推送要先派判定者重判一批。
引句:「上線前已提交的 5 份紀錄裡點出的規則類行,上線那次推送就要處理一次。」

**F14 第一層要求 `provenance_ok` 為真,但 prepare 的略過口徑沒跟著改**
severity: minor
blocking: 否(判準:使用者會被誤導一輪,有 `--all` 逃生)
- spec 段落:〈重讀:候選與兩層〉第一層與〈回傳碼與判不了〉。
- 輸入:候選唯一的紀錄 `provenance_ok` 為假。
- 壞在哪:`cmd_note_audit_reread_prepare` 用 `_note_reread_committed`,只比檔名指紋,不管 `provenance_ok`。新的第一層會說「沒對照」並印 prepare 指令,但 prepare 回「這次要對照的 N 篇守檔筆記都對照過這一版程式了,不產項目檔」。同時會印「要全部重產加 --all」,所以走得出來,但擋下訊息沒提 `--all`。spec 沒要求 prepare 的略過口徑跟 `provenance_ok` 一致。
- 查證:file: `scripts/lumos:34697-34710`、`:34803-34823`。
引句:「候選的對照指紋沒有任何已提交、而且 `provenance_ok` 為真的判定紀錄」

**逐節**
- 原問題與範圍、〈輸出〉、〈對消費專案的影響〉:已讀,無 finding。
- 〈開關〉:見 F10。
- 〈驗收條款〉:S1 到 S21 都沒覆蓋 F1、F3、F5、F7、F11、F12 的輸入,補條款時一併處理。
- 〈要一起改的說法〉:已讀,無 finding。我核對過列出的函式和既有測試名,全部存在。

**實務隱患鏡頭**
- 金流:無。只改本機與 CI 的回傳碼。
- 不可逆:無。擋下只是推送失敗,表態檔只追加。F7 的「刪紀錄」會丟第一層的證據,但在 git 裡可還原。
- 對外送出:閘本身不送資料,判定者會收筆記全文與程式 diff,spec 已承認(外部服務)。
- 守衛面:有。F1、F2、F3 讓擋放的結果錯誤,F6、F9 是繞過或回退不乾淨。

最嚴重的是 F1(空引句且空 text 讓整篇規則行全擋)、F2(表態接線字面照做必失敗)、F3(殘檔讓全 repo 判不了),blocking 共 3 條。
