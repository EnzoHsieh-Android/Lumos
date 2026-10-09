severity: major

審稿對象是 `/tmp/舊句兩道轉擋-r2.md`。對照的程式碼在 `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone-reread-block`。派工尾端沒附固定席節點,所以那一項不適用。

我把程式裡的測試、判定紀錄、治理帳數字都對過一遍。治理帳的 18 / 5 / 12、35 次全是 passed 且候選數 0,與現況一致。spec 列的既有測試名稱都存在。

我也沒找到「作者無論怎麼做都推不出去」的純死結。每一個擋點都至少有一條出口:改那一句、`drift ack`、`LUMOS_SKIP_REREAD_CHECK=1`,或把設定改成 warn。但下面 F1 到 F3 會讓出口變得很窄或很貴。

## Findings

### F1 第一層:判定紀錄有了、`provenance_ok` 為假,check 說沒對照、prepare 說都對照過
severity: major
blocking: 是(擋下時印出的指令走不通,只剩略過環境變數可用)
- **spec 位置**:〈重讀:候選與兩層〉第一層,以及 S6。
- **引句**:
引句:「候選的對照指紋沒有任何已提交、而且 `provenance_ok` 為真的判定紀錄」
引句:「prepare 把 `undecidable` 當 `skipped` 處理(行為不變)」
- **壞在哪**:
  - 報告開頭四行跟項目檔對不上時,`reread-record` 照收,但標 `provenance_ok: false`(file: `scripts/lumos:34880`)。
  - 新的第一層把這份紀錄算「沒對照」,並印出逃生指令 `_note_reread_cmdline`,這個指令沒有 `--all`(file: `scripts/lumos:34726`)。
  - 照貼執行 `reread-prepare` 時,`done = _note_reread_committed(root, tip)` 只比檔名裡的指紋,不看內容(file: `scripts/lumos:34774`、`scripts/lumos:34782`)。這份紀錄的指紋已提交,所以 `todo` 為空,印「都對照過這一版程式了,不產項目檔」後回 0(file: `scripts/lumos:34789`)。
  - 結果是 check 一直擋、prepare 一直說不用做,逃生路上沒有任何提示指到 `--all`。
  - spec 只改了 check 的判法,沒提 prepare 的 `done` 與 `wip` 也要跟著排除 `provenance_ok` 為假的紀錄。
- **補強**:`provenance_ok` 目前只有 record 會寫入,沒有任何讀取端(file: `scripts/lumos:34884`)。第一層是第一個讀它的地方,所以 prepare 沒對齊。
- **建議**:prepare 的略過集合改成與 check 同一口徑,或讓擋下訊息在這種情形帶 `--all`。

### F2 第二層:引句找不到就算「處理過」,但範本明寫「節錄即可」
severity: major
blocking: 是(該擋的規則類行會被放過)
- **spec 位置**:〈第二層〉第一個子項與第二個子項。
- **引句**:
引句:「頂端版筆記全文找不到這段引句 → 這一列算處理過(改掉或刪掉了)。」
- **壞在哪**:
  - 判定者範本寫的是 `"quote": "原句(節錄即可)"`(file: `scripts/templates/note-audit-reread.md:14`)。
  - `_note_reread_rows` 只截 500 字,不檢查引句是否真是那一行的子字串(file: `scripts/lumos:34693`)。
  - 判定者用「…」節錄、換標點或改寫時,引句不是逐字子字串,所以任何時候都找不到。
  - spec 把這種情形一律當「這行已改掉」放行,而那一行原封未動。
  - 現有 6 筆樣本的引句都是逐字子字串,但那是模型這次剛好守規矩,不是機制保證。
- **補強**:紀錄裡已存整行 `text`(file: `scripts/lumos:34873`)。可以用「整行 `text` 是否仍在」當第二判準,或在 record 時要求引句必為 `text` 的子字串。

### F3 第二層:引句與整行都是空字串時,等於點中筆記裡每一條規則類行
severity: major
blocking: 是(一次判定缺口就擋掉整篇,要逐行表態或略過)
- **spec 位置**:〈第二層〉引句定義。
- **引句**:
引句:「引句 = 那一列的 `quote`(去頭尾空白);`quote` 缺或空時退回整行 `text`。」
- **壞在哪**:
  - `_note_reread_rows` 允許缺 `quote`,預設成空字串(file: `scripts/lumos:34693`)。
  - `text` 取自 `lines[line-1]`,行號只要在 1 到筆記行數之間就收,所以空白行也收(file: `scripts/lumos:34873`)。
  - 判定者的行號差一行、落在空白行,又沒給引句,就得到引句為空字串、退回的 `text` 也是空字串。
  - 空字串是任何行的子字串,「含這段引句的每一行」變成全筆記。
  - 以本 repo 為例,規則類行很多(PITFALL 帶測試的就有 132 行),要逐行表態。ack 對這種情形不會拒絕(每行都含空引句),所以不是死結,只是代價不合理。
- **建議**:引句空或只有空白時,視為不點出任何行,或判不了。

### F4 第一層的「CI 有值」是通用環境變數,本機設了就無痕關掉第一層
severity: minor
blocking: 否(只放過,有出口,不影響擋人邏輯的一致性)
- **spec 位置**:〈第一層〉。
- **引句**:
引句:「環境變數 `CI` 有值時第一層只印、不擋」
- **壞在哪**:
  - 程式現況是 `os.environ.get("CI")` 只看真假,`CI=0`、`CI=false` 也算有值(file: `scripts/lumos:34980`)。
  - `CI=1 git push` 或 shell 預設帶 `CI` 的環境,第一層只印、不擋,而且不記 `skipped-env`。
  - RETIRE-IF 靠 `skipped-env` 累計 3 次來撤預設,看不到這條繞路。
  - 另一處判 CI 的地方多認一個 `GITHUB_ACTIONS`(file: `scripts/lumos:232`),口徑也不一致。
- **建議**:改認 `GITHUB_ACTIONS`,或本機看到 `CI` 時記一筆帳。

### F5 子開關照總開關:總開關 off 時,明寫的 `old_sentence` 跑不跑,spec 自己前後矛盾
severity: minor
blocking: 否(上線前由既有測試③④攔得住,但實作者會讀到兩種意思)
- **spec 位置**:〈開關〉名稱消失檢查。
- **引句**:
引句:「總開關 off 時 m1 照 retire 的先例也不跑」
引句:「寫 warn、block、off 照原義」
- **壞在哪**:
  - retire 的先例是 `rt_mode = parts["retire"] if mode != "off" else "off"`,明寫的值也被總開關蓋掉(file: `scripts/lumos:38611` 附近)。
  - m1 現行行為相反:`gate=off` 加 `old_sentence=block` 照跑照擋。測試④釘的是這個(file: `scripts/test_lumos.py:68363`),`_drift_check_c` 的提示句也這樣講(file: `scripts/lumos:38712`)。
  - 照字面實作「先例」,會讓明寫 `{"gate":"off","old_sentence":"block"}` 的專案悄悄失去這道檢查。
  - spec 要改的說法清單沒列 `_drift_check_c` 的 `gate=off` 提示句(file: `scripts/lumos:38712`),它在新行為下可能變成說謊。
- **建議**:一句話講清楚「只有沒寫的才跟總開關;明寫的照原義」,並把這句提示列進要改清單。

### F6 `drift ack --kind reread` 的接法與表態結構不符
severity: minor
blocking: 否(S18 測試會攔,但照字面實作 ack 會全部被拒)
- **spec 位置**:〈照留表態〉。
- **引句**:
引句:「reread 加進 `_DRIFT_BOUND_KINDS` 那一類的比對」
- **壞在哪**:
  - `_DRIFT_BOUND_KINDS` 的語意是「綁 related 與 seq 的發現型表態」。
  - `cmd_drift_ack` 對這一類會去呼叫 `_drift_current_finding`(file: `scripts/lumos:37500`)。reread 不是 `_drift_state_findings` 產生的發現,所以永遠回「現在不是 reread」,ack 一律 rc 2。
  - `_drift_ack_buckets` 也要求紀錄帶 `related` 與合法 `seq`(file: `scripts/lumos:37283`),reread 的表態沒有。
  - 另外,spec 只寫「`_DRIFT_KIND_NAMES` 加名字」,沒寫 `_DRIFT_KINDS` 要加。但 ack 的載入、驗證、argparse 選項都吃 `_DRIFT_KINDS`(file: `scripts/lumos:37232`、`scripts/lumos:37411`、`scripts/lumos:50311`)。
  - 〈回退〉段反而預設它已在 `_DRIFT_KINDS` 裡,前後不一致。
- **建議**:改成「reread 走自己的比對分支,不放進 `_DRIFT_BOUND_KINDS`」,並明寫 `_DRIFT_KINDS` 要加,同時處理 `_DRIFT_SCAN_KINDS` 的連動。

### F7 第二層列舉判定紀錄沒說檔名過濾,殘檔會讓所有推送「判不了」
severity: minor
blocking: 否(有出口:刪掉那個檔,但會擋住所有帶候選的推送)
- **spec 位置**:〈第二層〉第一個子項與判不了段。
- **引句**:
引句:「讀頂端提交裡 `governance/reread-verdicts/` 下所有判定紀錄」
- **壞在哪**:
  - 現有 `_NOTE_REREAD_VERDICT_NAME_RE` 的註解明說 `.tmp-wlf` 殘檔不算(file: `scripts/lumos:34324`)。
  - spec 的「所有」沒套這個過濾。
  - 殘檔或 `.gitkeep` 一旦被 `git add governance/reread-verdicts` 提交進去(record 印的提示正是這條),就會「讀不成 JSON → 判不了 → block」。
- **建議**:明寫沿用同一個檔名正規式。

### F8 規則類行不含 `★IRREVERSIBLE★` 與 `★CHECKPOINT★` 合約行
severity: minor
blocking: 否(漏擋的是少數合約行,設計者可能是有意的)
- **spec 位置**:〈第二層〉規則類行定義。
- **引句**:
引句:「或符合 `INVARIANT_RE`、或以摘要前綴」
- **壞在哪**:
  - 同名的 `IRREVERSIBLE_RE`、`CHECKPOINT_RE` 與 `INVARIANT_RE` 並存(file: `scripts/lumos:5915`、`scripts/lumos:5916`)。
  - 判定者點出一條不帶 `[test:]` 的 `KEY:★IRREVERSIBLE★` 行時,只印「一般行」、不擋。
  - 源頭計劃只提 RULE、INVARIANT、帶 `[test:]` 的結構行(file: `docs/lumos-toolchain-knowledge/Projects/守檔筆記對照改動_計劃.md:102`),所以可能是有意收窄。
  - 但回頭重讀要守的正是「程式看不到的限制」,不可逆合約行被排除在外,spec 沒說理由。

### F9 第二層忽略判定列的行號,短引句會連帶擋沒被點出的行;真修了也可能放不掉
severity: minor
blocking: 否(S9 有明寫,有表態出口)
- **spec 位置**:S9 與第二層「含這段引句的每一行」。
- **引句**:
引句:「只改同一行引句以外的字時應照樣擋」
- **壞在哪**:
  - 沒有最短長度,判定者節錄一個常見詞(例如「預設 warn」)時,其他沒被點出的規則類行只要含這個詞就一起擋。
  - 反過來,判定者節錄的是句子的前半,作者修的是後半,也就是真正錯的那段,引句還在,照擋。
  - 這時只能用 `drift ack` 的「照留」,而作者其實已修好。
  - 6 筆樣本的引句都夠長(最短 18 字),目前沒出事,但規則沒保護。

### F10 路徑帶控制字元的筆記在兩層都被靜默排除
severity: minor
blocking: 否(放過而非誤擋)
- **spec 位置**:〈候選照舊〉。
- **引句**:
引句:「候選照舊(推送範圍裡程式和管它的筆記都改了的守檔筆記),範圍照舊。」
- **壞在哪**:
  - `_note_reread_scan` 把控制字元路徑另放 `ctrl`,不進 `cands`(file: `scripts/lumos:34430`)。
  - 預設變 block 後,這類筆記兩層都不判,只在提示列印一句「跳過」,仍回 0。
  - Cf 類別含零寬字元,複製貼上的檔名可能不小心帶到。
  - spec 沒說 block 下這種筆記該怎麼處理(算判不了?),大概是沿用提醒版時代的行為。

### F11 多行邏輯行:規則類判定與表態的「原文」口徑沒定
severity: minor
blocking: 否(本 repo 摘要區 3699 條邏輯行中零條有接續行,實害目前為零,但消費專案會有)
- **spec 位置**:〈第二層〉規則類行,以及〈照留表態〉。
- **引句**:
引句:「這個判斷收成一支共用函式,第二層與 `drift ack --kind reread` 都用它。」
引句:「記 path、text、kind、reason,再加 `verdicts`」
- **壞在哪**:
  - `_ns_summary_logical(text)` 只回首行號對整條的對照。要把續行對回所屬邏輯行,得傳 `cont` 參數(file: `scripts/lumos:31963`)。spec 沒提,實作者容易只用首行號集合,於是引句落在續行時被誤判成非規則類而放過。
  - `text` 記哪一種沒定:`_drift_ack_text` 對 retire 記整條,其他種類預設記實體行(file: `scripts/lumos:37444`)。
  - 第二層若比對整條、ack 記實體行(或反過來),多行 RULE 的表態永遠對不上,等於沒有出口。
- **建議**:明寫「引句落在續行時,以哪個行號列、ack 記哪個原文」,兩邊同一口徑。

### F12 讀設定之前的失敗一律 block,連 `off`/`warn` 專案也躲不掉
severity: minor
blocking: 否(出口是略過環境變數)
- **spec 位置**:〈開關〉重讀。
- **引句**:
引句:「設定讀不到之前就發生的例外,照 block 處理(預設就是 block)。」
- **壞在哪**:
  - 現況是 `_lens_full_sha(root, rg[1])` 回 None 才讀不到設定(file: `scripts/lumos:34949` 附近)。`_lens_git` 逾時回 None,所以 git 暫時變慢時,明寫 `off` 的專案也會被 block。
  - 唯一出口是單次略過環境變數,設定檔改不了,因為設定本身就是從那個讀不到的提交讀的。
  - 另外,`_NoteRereadStop` 的各種原因(起點算不出來、讀不到起點圖譜、逾時)哪些歸判不了、哪些歸參數錯,spec 只列了幾種。

## 逐節讀完且沒有 finding 的部分
- 〈原問題與範圍〉:已讀,無 finding。數字與治理帳一致。
- 〈對消費專案的影響〉、〈回退〉:已讀,無 finding。舊版會略過未知種類,屬實(file: `scripts/lumos:37232`)。
- 〈掛鉤與 CI〉:已讀,無 finding。
  - 掛鉤現況是 `2>/dev/null` 加只認 130(file: `scripts/hooks/pre-push:537-541`),spec 的改法與其他閘一致。
  - CI 步驟只在 `push` 事件跑(file: `.github/workflows/ci.yml:253`),所以第一層在 CI 只印,範圍是 before 到 sha 的累計,與 spec 的描述相符。
- 〈輸出〉、〈治理帳〉:已讀,無 finding。`blocked` 與 `skipped-env` 不在本機帳分流名單,`reminded` 與 `covered` 在,RETIRE-IF 取數口徑沒問題。
- 驗收條款 S1 到 S21:已讀,無 finding。S5 的測試輔助函式已會移除環境變數 `CI`(file: `scripts/test_lumos.py:63678`)。

## 專題問題的回答
- **死結檢查**:
  - 第二層「依筆記路徑讀」加「表態綁指紋」不會造成永遠推不出去。
  - 表態記的是工作目錄裡所有點出該行的紀錄指紋,新紀錄只要相同指紋就沿用。
  - 程式又改時,第一層要求重判,新紀錄點出同一行就要重表態,這是 S11 要的。
  - 舊紀錄(舊指紋)仍點出該行時,表態的指紋是聯集,所以一次 ack 就涵蓋。
- **改名或搬家筆記**:
  - 紀錄的 `note` 欄是舊路徑,新路徑查不到紀錄,第二層不判。本機第一層會因指紋含路徑而要求重判。CI 沒有第一層,所以只有 CI 的話,改名加改程式可以不經判定通過。
  - 這是依路徑設計的結果,但 spec 沒講。
- **第一層 CI 只印、本機擋的分法**:
  - 邏輯上說得通,只是 F4 的通用環境變數會繞過。PR 在 GitHub 介面直接合併時,兩層都沒人在本機跑,也是設計上就有的缺口。
- **規則類行遇到多行邏輯行**:見 F11。本 repo 實測零案例,但寫法沒定。
- **子開關照總開關對 m1 既有行為的相容**:見 F5。

## 實務隱患鏡頭
- **守衛面**:本案就是改擋放行為。主要風險是上面 F1 到 F3。判定者品質左右第二層,F2 與 F3 是兩個沒有防禦的入口。
- **對外送出**:判定要把筆記全文與程式 diff 交給模型。spec 已列為隱患並給了 warn 或 off 的出路,我不另標。
- **金流**:無,只動檢查回傳碼。
- **不可逆**:無。擋下只是讓推送失敗,表態檔只追加。
- **併發**:無新風險。
  - 第二層只讀已提交的樹,不受別的會談影響。
  - 表態寫入走既有 `_vault_write_lock`。
  - 沿用的提示 `git add governance/reread-verdicts` 與 `git add governance/drift-acks.jsonl` 會夾帶別的會談未提交的檔,是既有性質。
- **效能與資源**:
  - 上限 256 KB 加 8 MB 已設。`_nodehome_cat_blobs_capped` 超過總量時,被略過的是目錄清單順序後面的檔,和該筆記無關(file: `scripts/lumos:29495`)。到那天會對所有人「判不了」,但離現況(約 20 KB)很遠。
  - 重讀預算 30 秒是軟上限,逾時現在變 block(F12 一併提過)。我沒有實測大型圖譜的耗時,標 ⚠ 交編排者。
- **資安與輸入**:路徑與引句經 `_note_reread_show` 過濾,節點名過 `shlex.quote`,spec 都有處理。F10 是控制字元路徑被排除,屬放過而非注入。
- **相容與升級**:舊版工具讀到新種類會略過,屬實。回退要 consumers 再 update 一次,spec 已講。

最嚴重的是 F1,擋下時印出的逃生指令走不通,與 F2、F3 並列 major(第二層的放行與誤擋入口);blocking 共 3 條。
