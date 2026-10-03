severity: major

審查立場:極端輸入代言人。對照的程式碼是 rw 工作樹(提交 a1223abd)的 `scripts/lumos`。下面的「驗證」都是我在 /tmp/b2x 臨時目錄用 importlib 載入該檔實跑的結果,沒動 repo。

## 第 1 輪修法有沒有真的解決原問題

- 第 1 輪正確性席 C2(讀壞了也會「找不到」而提早成立):spec 補了 NUL 與 LFS 指標檔,但 Big5 / GBK / Latin-1 這類「沒有 NUL 的非 UTF-8 文字檔」沒收進去,原問題只修一半,見 B1。
- 第 1 輪邊界席 B10 的 NFC/NFD 與正確性席 C4 的反引號:反引號在提交時的檢查補了,但 `_ns_revisit_cond_viol` 以外的路徑(RULE 撤除條件)沒補,見 B6。
- 第 1 輪通才席 U5、架構對齊席 Z2(列舉鍵的地方漏改):spec 補了兩句訊息與一份技能手冊,但還有四處列舉沒進清單,見 B7。
- 其餘第 1 輪項目(`-S` 找錯提交、資料夾/連結檔/子模組、淺層講法、`born` 欄形狀、git 逾時)在文字上已修,我沒重報;但「用什麼 git 呼叫去實作」的事實有落差,見 B4。

## 逐節

### 範圍
已讀,無 finding。

### 做法 1. 條件鍵 when-gone

**B1 帶字串的 when-gone 讀到非 UTF-8 文字檔(Big5 等)會讀成亂碼、字串找不到、條件提早成立;而且 spec 說的「讀位元組」不是 `_read` 實際給的東西**
severity: major
blocking: 是 — when-gone 是唯一「讀壞了就觸發」的鍵,spec 自己已點名要防「誤讀成亂碼也會找不到」,但漏掉最常見的一類(沒有 NUL 的非 UTF-8 文字檔),照字面實作會在寫下當下就誤成立。
引句:「否則把字串編成 UTF-8 在位元組裡找,找不到 → 成立」

1. spec 段落:〈做法〉1.2「帶字串」那條。保護清單只有:路徑不是一般檔、讀不出、含 NUL、LFS 指標檔。
2. 問題一(漏類):台灣專案常見的 Big5 / GBK / Shift-JIS / Latin-1 文字檔不含 NUL,也不是 LFS。`_read` 回的是 `_drift_decode(b)`(`utf-8-sig`、`errors="replace"`),不丟錯、不回 None。
   - 輸入:`REVISIT:[when-gone:legacy/報表.sql::暫存檔][by:2027-01-31] …`,目標檔是 Big5 編碼、裡面確實有「暫存檔」。
   - 照字面實作:讀得出來、沒 NUL、不是 LFS → 在文字裡找 UTF-8 的「暫存檔」→ 找不到 → 回成立。條件寫下當下就成立,推送被點名「條件已經成立」,scan 也標「寫下時就已成立」。
   - 驗證:我用 `m._drift_decode("暫存檔 tmp_audit 設定".encode("big5"))` 實跑,結果 `NUL: False`、`U+FFFD: True`、`"暫存檔" in txt` 為 False。
3. 問題二(機制說反):spec 寫「讀位元組(既有的 `_read`…)」「編成 UTF-8 在位元組裡找」。但 `_read` 把解碼後的文字存進 `self._text`(`_drift_decode` 已去 BOM、把壞位元組換成 U+FFFD),位元組不留。要照 spec 的「位元組」做,得另開一條讀法,這就違反 spec 自己「一個條件碰到哪支檔只有一份算法」;要照 `_read` 做,「含 NUL」可用文字裡的 `\x00` 判,但「解碼有替代字元」這個訊號 spec 沒用上。
4. 同一個機制還有兩個極端:檔很大(`_read` 無大小上限,disk 模式 `read_bytes()` 整檔進記憶體,git 模式 `_drift_cat` 也無上限;對照:往回查那邊有 `_nodehome_cat_blobs_capped`);字串是 NFD 而檔是 NFC(路徑段做了 NFC,字串段沒有,macOS 貼上的日文濁音、韓文會對不上)。spec 的〈天花板〉第 4 點只列 `]`、換行、反引號,這兩項也沒進。
5. 驗收條款:S1 的「判不了」只列「資料夾、內容含 NUL、是 LFS 指標檔或讀不出」,沒有「文字含替代字元」的案例,所以這個洞測試也守不到。
6. 查證佐證:file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw/scripts/lumos:32180`(`_drift_decode`)、file: `…/scripts/lumos:32265`(`_read`,disk 分支 `_drift_decode((Path(self.root) / p).read_bytes())`)。

**B2 往回查「連續都還有這一條」沒交代中間某一版讀不出、太大、非 UTF-8 時怎麼辦;整串歷史一次批次讀沒有總量上限**
severity: major
blocking: 是 — 這個鏈的任何一版被當成「沒有這一條」,就會把「這一世的開頭」往後推,輸出一個斷言式的假標記「寫下時就已成立(提交 X)」或漏標,而 spec 的「判不了」清單裡沒有這一類。
引句:「逐版用同一支抽取(`_probe_lines`)找同一條」

1. spec 段落:〈做法〉2.1、2.2(第二條)、2.3。三態只列了「還沒提交、淺層 clone、找不到、git 失敗、超過預算、那一版的樹讀不出」。「那一版的樹讀不出」是指**判定用的樹**,不是**筆記自己的歷史版本**。
2. 問題:批次讀法 `_nodehome_cat_blobs_capped(repo_root, specs, max_bytes, timeout)` 的語意是:超過 `max_bytes` 的版本回 None;git 讀不到的回 None;整批含換行的 spec 會整批回 None。spec 沒給 `max_bytes`,也沒說某一版是 None、或解碼 UTF-8 失敗時算什麼。
   - 輸入:一篇筆記有 30 個版本,第 12 版因為有人暫時貼進一張 base64 圖,超過上限;第 13 版刪掉。
   - 照字面實作的兩種走法都出事:(a) None 當成「沒有這一條」→ 鏈在第 12 版斷,這一世的開頭變成第 13 版之後,拿較晚的樹判定,可能把「早就成立」標成「不成立、不標」(漏標),或把「寫下時不成立」標成「成立」(假標記);(b) 例外往上丟 → scan 整個崩(第 1 輪邊界席 B5 擋掉的那種崩潰換了形狀回來)。
3. 總量:每版有 cap,但版本數沒有 cap。批次讀把全部版本一次載入記憶體:版本數 × 筆記大小。本 repo 單篇最多 80 個提交、最大筆記約 69KB,量很小;但消費專案的長壽計劃筆記沒有這個保證,而「最老的條件」(本功能要查的對象)正好是歷史最長的那批,所以最容易碰到上限而變成判不了。spec 的〈實務隱患〉效能段只量了單次 git log 與建圖譜,沒量這一段。
4. 缺的驗收案例:S5、S6 沒有「歷史中間有一版讀不出/太大/非 UTF-8」的案例。
5. 查證佐證:file: `…/scripts/lumos:26527`(`_nodehome_cat_blobs_capped` 的語意:超過上限回 None)、file: `…/scripts/lumos:26541`(`_nodehome_cat_blobs` 路徑含換行整批回 None)。

**B3 「判定、預讀、點名讀不出的檔、候選篩選、正規化、值驗證全部呼叫它」與程式現況不符;沒帶 `::` 的 when-gone 要切成什麼沒定義;spec 提到的「問題」訊息沒有出口**
severity: major
blocking: 是 — 這句是 spec 對「一個條件碰到哪支檔只有一份算法」的承諾,實作者照這份清單去改,會留下三處各自切字串的第二份,和六處用鍵名白名單擋掉 gone 的地方。
引句:「判定、預讀、點名讀不出的檔、候選篩選、正規化、值驗證全部呼叫它」

1. spec 段落:〈做法〉1.1 第二個子點、1.2 的「帶字串」「判不了,scan 列成問題」、〈實務隱患〉效能「有預讀」。
2. 問題 A(現況不是這樣):
   - 正規化 `_probe_norm_value`(`scripts/lumos:31929`)、值驗證 `_probe_named_err`(`:31945`)、路徑提示 `_drift_probe_path_warn`(`:32608`,內有 `v.rsplit("::", 1)[0]`)三處都是自己 `rsplit("::", 1)`,沒有呼叫 `_drift_cond_split`。spec 說它們「呼叫它」,但沒列成要改的點;實作者要嘛各自加 gone 分支(第二份),要嘛重構(spec 沒要求)。
   - 預讀 `prefetch`(`:32290`)用 `k in ("symbol", "test")` 先篩;`unread_for`(`:32311`)的非 symbol/test 分支落到「語料」邏輯;`_drift_row_unread`(`:32537`)用 `elif k in ("symbol", "test")`。gone 不在這些白名單裡。照 spec 只改 `one`、`_drift_cond_split`、`_drift_probe_cond_candidate`,gone 的檔不會被預讀(每條各開一次 git,正是第 2 輪併發席修過的老問題),判不了時也不點名是哪支檔。
3. 問題 B(未定義):`_drift_cond_split(v)` 現在沒有 `::` 時回 `("", v)`(路徑空、整串當名稱)。spec 只說「gone 切第一個」,沒說 `[when-gone:src/a.py]`(無 `::`)回什麼。若照現有 fallthrough 回 `("", "src/a.py")`,`_drift_probe_cond_candidate` 的 `if path:` 為假,落到「不帶路徑的名稱」分支,gone 純路徑條件就被當成全庫名稱搜尋的候選(`code_shape` 時一律是候選);S4(`[retire:when-gone:src/a.py]`)的路徑形式就是這種。
4. 問題 C(出口不存在):spec 要「scan 列成問題 when-gone 帶字串時路徑要是一般檔」。問題文字的產生處是 `_drift_probe_row_problems`(`:32630`),它只認 file 指到資料夾與 symbol/test 路徑提示;`tree.one` 對這種情況回 None,scan 因此只會印通用的「判不了(git 讀不出程式檔或筆記)」,不是 spec 說的那句。
5. 驗收條款:S3、S7 沒有「無 `::` 純路徑」的 split 案例,也沒有 prefetch / 點名檔案的案例。

### 做法 1.3、1.4

**B4 git 呼叫的事實與 `_nodehome_git` 不符:它沒有 `-c` 旗標、沒有逾時參數、也不是字面路徑;預算用完時的處理沒寫**
severity: minor
blocking: 否 — 都是實作時會撞到、不會靜默出錯的落差;唯一會靜默的是路徑含萬用字元時多撈到別篇的提交,影響只是多讀幾版。
引句:「走 `_nodehome_git`,`-c` 關掉外部差異與文字轉換的既有旗標,`--` 隔開路徑」

1. spec 段落:〈做法〉2.2(第二條)與〈實務隱患〉跨環境「往回查走 `_nodehome_git` 的既有旗標」;2.5 預算「每個 git 呼叫的逾時取剩餘預算與既有 20 秒的較小值」。
2. 問題:
   - `_nodehome_git(repo_root, *args)` 只轉呼叫 `_lens_git(..., binary=True)`,沒有加任何 `-c`、也不接 `timeout`;`_lens_git` 才有 `timeout=20` 參數。要「取剩餘預算與 20 秒較小值」得改 `_nodehome_git` 的簽名(影響其他呼叫端),spec 沒列。「`-c` 關掉外部差異與文字轉換的既有旗標」在這支函式沒有;本 repo 的是 `_ns_diff` 等處的 `--no-ext-diff --no-textconv`(對 `git log --format=%H -- path` 與 `cat-file --batch` 其實都不影響)。
   - `--` 只隔開路徑與選項,不關掉萬用字元:筆記檔名含 `[`、`*`、`?` 時,git 把它當 pathspec 樣式。本 repo 其他處一律加 `--literal-pathspecs`(`scripts/lumos:30786`、`:31089`、`:33198`)。我實測 `git log -- 'n[1].md'` 同時有字面匹配,所以不會漏;但會多撈到檔名符合樣式的其他筆記的提交。
   - 剩餘預算 ≤ 0 時(「scan 預算剛好用完」)spec 只說「超過預算標判不了」,沒說在 spawn git 之前先檢查;`min(剩餘, 20)` 為 0 或負值時會先 spawn 一次行程才逾時。
3. 查證佐證:file: `…/scripts/lumos:26179`(`_nodehome_git`)、file: `…/scripts/lumos:39854`(`_lens_git`)。

**B5 〈實務隱患〉「已排除:對外送出:不呼叫網路」對 partial clone 不成立**
severity: minor
blocking: 否 — 只影響用 `--filter=blob:none` 的 CI/clone,結果是變慢到逾時、一律判不了,不會誤判;但「已排除」是明寫的判斷,與事實不符。
引句:「已排除:對外送出:不呼叫網路」

1. spec 段落:〈實務隱患〉已排除三行。
2. 問題:往回查要 `cat-file --batch` 讀舊提交的筆記版本;partial clone(blob:none)裡這些 blob 不在本機,`cat-file` 會對 promisor remote 發請求補抓。淺層 clone 有偵測(`_git_is_shallow`),partial clone 沒有。
3. 驗證:我在 /tmp/b2x 建了來源 repo,`git clone --filter=blob:none`,用 `printf 'HEAD~2:n[1].md\nHEAD~3:n[1].md\n' | git cat-file --batch` 讀,讀前 `git rev-list --objects --missing=print HEAD` 缺 6 個物件,讀後缺 4 個,代表真的去抓了兩個 blob(沒有任何報錯)。
4. 影響:逐版抓 blob 受網路往返影響,會吃光 20 秒逾時,整批回 None;因為 B2 沒定義 None 的語意,連鎖更糟。
5. 沒有對應的驗收案例或天花板條目。

### 做法 1.4(撤除條件)

**B6 RULE 撤除條件這條路的值驗證與 REVISIT 那條路不一致:路徑要求自相矛盾、`..\x` 與反引號不擋**
severity: minor
blocking: 否 — 撤除條件寫錯時 scan 會列成問題,不會靜默放行該擋的推送,只是提交時沒擋住。
引句:「`_slot_retire_err` 對 `gone` 照 symbol/test 的規矩要求帶路徑(本來就必帶)」

1. spec 段落:〈做法〉1.4 與 S3、S4。
2. 問題一(自相矛盾):`_slot_retire_err` 對 symbol/test 的「規矩」是 `"::" not in val` 就擋(「要帶路徑(路徑::名稱),撤除條件不做全庫掃」)。對 gone 照這條做,`[retire:when-gone:src/a.py]`(S4 的範例、純路徑形式)會被擋;spec 同時說「本來就必帶」,指的若是路徑本身必帶,就不該說「照 symbol/test 的規矩」。兩句讀法相反。
3. 問題二(S3 的案例只守 REVISIT 那條路):`_slot_retire_err` 呼叫 `_probe_value_err(k, val)` 時沒有先把反斜線轉斜線。驗證:`_slot_retire_err("when-file:..\\x.py")` 回 None(放行),`a/../x.py` 才被擋。接著 `_retire_lines` 走 `_probe_parse` 把它標成 bad,於是撤除條件變成「提交時沒擋、推送判定也不評估、只有 scan 列問題」的死條件。gone 的撤除條件同樣。
4. 問題三(反引號):〈天花板〉第 4 點與 S3 說字串不能含反引號,理由是「可見文字的規矩會剝掉」。RULE 摘要行走 `slot_parse`,不剝行內程式碼;驗證:`_slot_retire_err("when-symbol:src/a.py::`x`")` 回 None。所以撤除條件的 when-gone 字串含反引號不會被擋,而且比對的是含反引號的字面串,和 REVISIT 那條路相反,spec 沒說這是故意的。
5. 補充(REVISIT 那條路的錯誤訊息):`_ns_revisit_cond_viol` 收到的 `rest` 是 `_strip_inline_markup` 剝過之後的文字。驗證:``[when-file:src/a.py::`foo`]`` 剝成 `src/a.py::`(空字串);``::foo `bar` baz`` 剝成 `::foo  baz`,解析沒有任何錯誤(`errs: []`);未閉合的反引號會把後面整個截掉,解析報「沒有條件標記」。spec 說「新寫的 REVISIT 行原文裡…同一個標記內出現反引號,提交時報條件寫錯」,所以檢查必須看原文行 `ln`(該函式有收到 `ln`,可行),但 spec 沒寫明要看原文,照 `rest` 實作會讓中間那個案例靜默通過。
6. 查證佐證:file: `…/scripts/lumos:3866`(`_slot_retire_err`)、file: `…/scripts/lumos:27982`(`_ns_revisit_cond_viol`)、file: `…/scripts/lumos:368`(`_strip_inline_markup`)。

**B7 列舉條件鍵的地方還有四處沒進同步清單,守衛測試也守不到**
severity: minor
blocking: 否 — 只影響文件與範本的一致性(以及 RETIRE-IF ① 的「兩個月零使用」是否因為沒人知道這個鍵而發生)。
引句:「技能手冊 `skills/lumos-project-notes/commands/03-寫回圖譜.md` 四種鍵那句補第五種」

1. spec 段落:〈做法〉1.4 末句、〈做法〉3、S7。
2. 問題:grep `when-test` 還列舉四個鍵的地方:file: `…/CLAUDE.md:52`、file: `…/AGENTS.md:53`(「`[retire:]` 只收機器式:`when-file:路徑`、`when-symbol:…`」)、file: `…/scripts/templates/graph-discipline.md:50`(同句,它是會注入消費專案 CLAUDE.md 的範本,與 CLAUDE.md 有 sentinel 同步測試)、file: `…/skills/lumos-project-notes/reference.md:404`(「事件:`when-file`、`when-symbol`、`when-test`、`when-status`」)。spec 只列了 `03-寫回圖譜.md`。
3. S7 的守衛只比對三則程式內訊息是否提到 `_PROBE_KEYS` 的每個鍵,上述四處不在比對範圍;範本與 CLAUDE.md 的 sentinel 測試只比兩者彼此相同,同時漏改也會是綠的。
4. 後果:`CLAUDE.md` 這句是 agent 讀到的 RULE 撤除條件規則,不補它,agent 不知道可以寫 `[retire:when-gone:…]`。

### 做法 1.1(評估語意)

**B8 從沒存在過的路徑(錯字、全形冒號、被 gitignore 的檔)一律「已消失」,沒有像 symbol/test 那樣的路徑提示,而且推送點名訊息會講錯原因**
severity: minor
blocking: 否 — 新寫的會在第一次推送被擋下,作者看得到;問題在訊息把原因講成「條件已經成立」,而不是「路徑從來沒有」。
引句:「找不到這個路徑、或那支檔裡不再出現這段字就成立」

1. spec 段落:〈做法〉1.1 第一條與〈實務隱患〉繞過。
2. 問題:`[when-gone:src/a.py：：foo]`(全形冒號)沒有半形 `::`,切法得到純路徑 `src/a.py：：foo`,樹上必然找不到 → 成立。驗證:`_probe_parse("[when-file:src/a.py：：foo][by:2027-01-01]")` 的值是 `src/a.py：：foo`,沒有任何錯誤。同理,路徑指到被 `.gitignore` 的產物(`build/out.txt`)或拼錯的資料夾,在任何提交的樹上都不存在,從第一天起成立。
3. 現況對照:symbol/test 有 `_drift_probe_path_warn`(路徑找不到、也不像檔案路徑就在 scan 列問題);file 有「指到資料夾」提示。gone 因為語意相反,「找不到」本身就是成立,這類提示更需要,但 spec 沒有任何對應(連「這個路徑在這份歷史上出現過沒有」都不看)。
4. 照字面實作:作者把全形冒號打進去,推送被點名「這次新寫(或改了條件)的回頭條件,條件已經成立」。作者看到的是「條件成立」而不是「你的路徑多半打錯了」。表態「照留」(spec 稱為繞過)後這條永遠被當成已成立,而 scan 只會標「寫下時就已成立」,仍沒說路徑根本沒出現過。

### 做法 2. 寫下時就已成立

**B9 「同一個提交的樹與圖譜只建一次」沒有淘汰規則,而共用的列樹快取上限是 8**
severity: minor
blocking: 否 — 只在一次 scan 同時有多個不同出生提交的存量條件時出現,結果是變慢或吃記憶體,預算會擋住,不會誤判。
引句:「同一個提交的樹與圖譜只建一次」

1. spec 段落:〈做法〉2.5、〈實務隱患〉效能。
2. 問題:`_drift_tree_env` 把整個圖譜的所有 `.md` 讀進記憶體並建 `Env`。我在本 repo(圖譜約 8.6MB、約 600 篇)連建 8 個不同提交:每個約 0.15 秒,八個合計行程高峰記憶體約 195MB(`ru_maxrss`)。「只建一次」若指全部保留到 scan 結束,N 個不同出生提交就是 N 份:這個量級下 40 個約 1GB。〈實務隱患〉說「成立的條件通常是個位數」,但本功能的服務對象是消費專案清漂移的存量(回傳第 11 項只舉了四條,不代表上限),大型 vault 與百條存量時這個假設沒有依據。
3. 另外三點:(a) `git log` 與批次讀是「每條成立的條件一次」,同一篇筆記有多條成立的條件時重複查同一份歷史;(b) `_DRIFT_LS_CACHE` 在滿 8 筆時整個清空(`scripts/lumos:32150` 一帶),往回查的樹和圖譜之間互相擠掉,「只建一次」靠不住;(c) 從 HEAD 一路往回讀到「鏈斷掉」或最早,沒有提前結束的規則,最老的條件讀最多版。
4. 修法方向 spec 沒定:依出生提交排序處理並在用完後丟掉環境、同一篇筆記只查一次歷史。

**B10 「這一世的開頭」在合併歷史與改名/拆篇時會輸出斷言式的假標記 ⚠**
severity: minor
blocking: 否 — 標記旁有提交短碼,人可以點進去核對;但「從沒提醒過」是對歷史的斷言,與證據強度不符。
引句:「筆記改過名,找到的是改名後那一版,寫下當時的狀態可能看不到(會標成那一版的判定)」

1. spec 段落:〈天花板〉2、〈做法〉2.1、2.2。
2. 問題:
   - 改名/拆篇:天花板 2 承認找到的是改名後那一版,但輸出仍是「寫下時就已成立(提交 X)」。證據不足時應該是判不了,而不是肯定句;這個圖譜工具有改名、拆節點的慣用操作(`lumos` 的改名與 regen),天花板假設它罕見,本 repo 圖譜目前只有 1 次 R100,但消費專案沒有量。純改名提交對 `git log -- path`(沒有 `--follow`)就是「這個路徑第一次被加入」。
   - 合併歷史 ⚠:`git log --format=%H <起點> -- <路徑>` 預設做歷史簡化,合併提交若與某個親代在該路徑 TREESAME 就只跟那一側。於是「這一世的開頭」可能落在側枝上的一個提交,用側枝的樹去判定,而不是主線被合進來時的樹。spec 沒指定 `--first-parent` 或 `--full-history`,我沒有造出具體的反例,所以標 ⚠:判不準會不會讓判定翻向。
3. 缺的驗收案例:S5、S6 沒有合併提交與改名的案例。

### 做法 2.3 至 2.7、3、驗收條款、回退、天花板、審計修正紀錄
已讀,無 finding(除上面已列的各點外)。

## 實務隱患逐類(本功能碰到的風險類)

- 併發:無新問題。只讀 git 物件;若其他會談在 scan 中途提交,`git log HEAD` 與之後用提交編號讀的內容是同一份輸出,彼此一致。唯一要小心的是 B2(中間版本讀不出)。
- 效能與記憶體:有,見 B2(批次讀總量)、B9(建樹/圖譜的保留與快取上限)、B1 第 4 點(`_read` 無大小上限)。
- 回滾:無新問題。還原提交後 when-gone 變成「不認得的條件鍵」,新寫的提交時擋、已寫的在 scan 變成寫錯的條件、推送判定因 `bad` 旗標略過;我核對了推送判定的篩選(`lines = [x for x in lines if x[3]["conds"] and not x[3]["bad"]]`)。
- 誤擋與繞過:有,見 B1(誤成立)、B3(判不了時的點名與預讀)、B8(寫錯路徑的訊息講錯原因)。
- 網路/外送:有,見 B5。
- 跨環境:macOS / Linux 的 NFC/NFD 檔名行為不同(我在 macOS 上造了 NFD 存檔名,`git log -- <NFC>` 與 `cat-file HEAD:<NFC>` 都找得到,Linux 上第 1 輪程式註解 `_drift_cat` 說讀不到);因為 spec 對「找不到」已標判不了,方向是安全的,所以不另立 finding。

最嚴重 severity 是 major;blocking 共 3 條(B1、B2、B3)。
