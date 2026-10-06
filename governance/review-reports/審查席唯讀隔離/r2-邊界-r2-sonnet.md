severity: major

審查範圍:凍結快照 r2-snapshot.md 全文。實測佐證:governance/review-reports/ 347 個資料夾、docs/.canary-log.jsonl 3112 筆(425 個迴圈編號)、引擎型別檔、使用者記憶檔。未改 repo。立場:極端輸入。

### F1 輪次格式比真實輪次窄,不合格的派工詞被靜默當成非審查席,隔離整席失效
severity: major
blocking: 是 — 真實卷證已有不符規則的輪次寫法,失敗時不擋、不報,席位完全沒有隔離
引句:「不合就不是審查席(不擋)」
- 快照規定輪次要符合 `^r[0-9]+[a-z]?$`。我掃 canary 帳全部 round 欄,不符的有 `r3-dref`(3 筆)、`r4-dref-delta`(2 筆)、`r5-recap`(2 筆)、空字串(249 筆)。卷證資料夾還有檔名前綴為 `驗收-` 的整批(「驗收紀錄寫明驗了哪些功能」等,檔名 `驗收-通才4-opus.md`、`驗收-intake.md`)。編排者照真實輪次寫 `LUMOS-SEAT: <迴圈>/r3-dref/<席名>`,外掛判不合格,放行,席位能寫 repo。
- 大寫 `R2`、全形字元、`r3B` 同樣靜默失效。
- 失敗原因是「不合格」與「沒帶標記」被併成同一種結果。第一行以 `LUMOS-SEAT` 開頭卻格式錯,幾乎一定是編排者想隔離卻寫壞了。建議這種情形拒絕派工(deny)並用三段式說明哪裡寫壞,而不是放行。
- 邊界:派工詞第一行前有 BOM(U+FEFF)或全形空白(U+3000)時,「空行」與「去頭尾空白」的定義沒寫。若實作的空行判定是 `line === ""`,只含 U+3000 的行會被當成第一行,標記漏掉。快照要寫明「去掉開頭的空白行」是指 trim 後為空,且 trim 要含 BOM 與 U+3000。
- 派工詞第一行有 `LUMOS-SEAT：`(全形冒號)也是同一類靜默漏掉。
file: `docs/.canary-log.jsonl`(round 欄 `r3-dref`、`r4-dref-delta`、`r5-recap`)
file: `governance/review-reports/驗收紀錄寫明驗了哪些功能/驗收-intake.md`
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·一)

### F2 迴圈編號與卷證資料夾名不同,保護路徑指到不存在的資料夾;repo 根怎麼找也沒定義
severity: major
blocking: 是 — 保護目標以迴圈編號組路徑,真實帳上約四分之一的迴圈編號找不到資料夾
引句:「卷證資料夾 `governance/review-reports/<這席的迴圈編號>/` 裡,同一輪(檔名以 `<輪次>-` 開頭)的席報告與收貨紀錄」
- 我拿 canary 帳 425 個 `loop` 值去比對 347 個資料夾,有 110 個不存在:`enforcement可觀測性-b` 的報告在資料夾 `enforcement可觀測性`、`code-audit-batch4b` 在 `code-audit-batch4`、`code-收工點名問版本控制` 在 `收工點名問版本控制`(報告檔名前綴 `code-r1-`)。外掛用迴圈編號組路徑,保護的是不存在的資料夾,S2 的卷證那一半在這些迴圈上全空。
- `-v2`、`-std` 共用資料夾的情形反向:`精簡版update指令/` 內同時有 `r1-s1.md` 與 `std-r1-s1.md`,兩個迴圈編號共用一個資料夾,別迴圈的同輪報告不受保護。
- 快照沒寫 `governance/review-reports/` 相對於哪個目錄。審查在獨立 clone 或 worktree 裡跑時(本次審查就是獨立 clone),外掛怎麼知道 repo 根,沒有定義。上一輪我提的「落到哪個實際路徑」仍沒答案。
- 要請作者明講:路徑如何從標記推出,或改成「卷證資料夾下所有檔,除共用材料」並以 repo 根為基準。
file: `governance/review-reports/enforcement可觀測性/r1-外家否決.md`
file: `docs/.canary-log.jsonl`(`loop` 值 `enforcement可觀測性-b` 對 `report_path`)

### F3 「同輪席報告」的檔名判定,外掛根本分不出 snapshot、dispatch 與別席報告;真實檔名前綴多樣
severity: minor
blocking: 否 — 同輪席報告進卷證時所有席都已交回,內容落在 repo 內的窗口極短,誤判的影響小
引句:「席報告是 `<輪次>-<席名>.md`(以及 `.stdout`)、收貨紀錄是 `<輪次>-intake.md`」
- 外掛只知道自己這席的席名,別席席名要從登記表才知道;快照沒說保護清單怎麼產生。若是「`<輪次>-` 開頭、扣掉共用材料」,共用材料的清單(「snapshot、dispatch、delta 等」)是開放的:真實還有 `r1-dispatch-s1.json`、`r1-repro.md`、`r3-work.md`、`驗收-dispatch-common.md`、`roster-alerts.log`,哪個算共用沒有答案。
- 真實席報告前綴不是 `<輪次>-` 的:`std-r1-s1.md`、`v2-r1-簡化-sonnet.md`、`code-r1-資安-sonnet.md`、`驗收-通才4-opus.md`。依本條不受保護。
- 席名與檔名中間的不一致:標記席名 `架構對齊-sonnet` 對檔名 `r1-arch-架構對齊.md`,精確比對對不上。
- 建議:把這一半改成「只保護席報告暫存處」,卷證那半在帳上命名不齊時價值有限,或寫成明確的檔名樣式清單。
file: `governance/review-reports/精簡版update指令/std-r1-s1.md`
file: `governance/review-reports/收工點名問版本控制/v2-r1-簡化-sonnet.md`

### F4 暫存區放行規則遇到「repo 本身在暫存區」就把寫入保護全關,S13 的驗收情境自相矛盾
severity: major
blocking: 是 — S13 照字面做會讓「改 repo 應被擋」那一項不可能通過,而且現實中 repo 或 clone 在暫存區的情況常見
引句:「落在暫存區、而且不在席報告暫存處 → 放行;其餘(repo、家目錄、使用者設定、其他專案)一律擋」
- 失敗場景一:S13 寫「暫存 repo 放一份假暫存處,claude -p 搭 --plugin-dir 兩支外掛跑一場」。暫存 repo 放在 `/private/tmp` 底下是自然做法,那它整個在暫存區裡,審查席寫它的檔是放行。要讓第一項「改 repo 裡的檔被擋」成立,暫存 repo 必須放在暫存區外,快照沒寫。
- 失敗場景二:記憶檔載明推送與對照組用 `git clone --shared … $CLAUDE_JOB_DIR/tmp/clone-x` 開私有 clone。審查席的 cwd 若是這種 clone(審查在 clone 裡跑),repo 在暫存區,保護對它不存在,而外掛不報。
- 暫存區包含整個 `/private/var/folders`、`/tmp`、所有別的 session 的 scratchpad(本機路徑形如 `/private/tmp/claude-501/<專案>/<session>/scratchpad`),寫入沒有 repo 範圍判定可以扣掉暫存區裡的 repo。
- 建議:放行規則加一個「且不在任何 git 工作樹內(含 `.git` 檔或資料夾的祖先)」的條件,或限縮成席位專屬的臨時資料夾。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·二·2 與條款 S13)
file: `/Users/enzo/.claude/projects/-Users-enzo-harness-lumos-toolchain/memory/worktree-push-pass-branch-gap.md:12`

### F5 斷詞失敗時的結果沒寫,配上「外掛出錯就放行」,最常見的 `gh pr create` heredoc 寫法可能整串漏掉
severity: major
blocking: 是 — 阻擋 `gh` 是這份隔離的核心承諾,斷詞一失敗就掉到放行,而失敗輸入是常態寫法
引句:「把整串指令做 shell 斷詞(引號、跳脫照 shell 規則)」
- 快照沒寫「斷詞遇到未閉合引號、heredoc、`$'…\'…'`、巢狀 `$(…)` 時怎麼辦」。配上第 6 點「外掛自己出錯時引擎會跳過它(放行)」,斷詞丟例外就等於放行。
- 失敗場景:`gh pr create --title t --body "$(cat <<'EOF'` 接多行,內文有單獨一個 `"` 或 `it's`。對 shell 合法(heredoc 內文不解析),但逐字元做引號配對的斷詞器在 `"` 處會看到未閉合,丟例外或把 `gh` 吞進引號詞。這正是模型寫 PR 的標準寫法。
- 同族:`$'it\'s'`(ANSI-C 引號)、反斜線接換行、`#` 註解、`<<-EOF` 縮排結尾。
- 極長指令(MB 級 heredoc)與含 NUL 的指令:快照沒給長度上限或 NUL 的處理;遞迴斷詞 `bash -c "bash -c \"…\""` 的深度上限沒寫,深度夠就可能堆疊溢位而放行。這幾項成本低,建議一併寫:斷詞失敗、深度或長度超限時,對審查席的 Bash 一律擋(fail-closed),這是 S8 的明列例外。
- 要附一條先紅的測試:上述 heredoc 寫法且 `gh` 在命令位置,應擋。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·二·4 與第 6 點)

### F6 內嵌 shell 的辨識只寫了 `-c` 單獨出現,常見寫法 `bash -lc`、`bash <<<`、`sh 腳本` 全繞過
severity: major
blocking: 是 — S3 明寫「夾在 bash -c 字串裡的」要擋,而模型習慣寫的變體不在規則內
引句:「`sh -c`、`bash -c`、`zsh -c` 的字串參數遞迴斷詞」
- `bash -lc 'gh pr create'`、`zsh -ic '…'`、`bash --noprofile -c '…'`:`-c` 與其他旗標合併或夾在後面,字面「`-c` 的字串參數」認不到。快照沒寫旗標合併怎麼解。
- `echo 'gh pr create' | sh`、`bash <<<'gh pr create'`、`sh <<EOF`:指令文字從 stdin 進來,不是 `-c` 參數。
- `Write` 把腳本寫到暫存區(白名單允許)再 `bash /tmp/x.sh`:這是「被誘導」的最自然兩步,而且快照在「不做」只列了 `python -c`、變數、`eval`,沒有點名腳本檔。
- 建議:至少把旗標合併(含 `c` 的短旗標群)與 stdin 餵 shell(`| sh`、`<<<`、heredoc 餵 `bash`)納入;腳本檔要嘛納入「不做」並寫進誠實界線,要嘛擋「`bash`/`sh` 執行暫存區內由 Write 寫的檔」。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·二·4 與範圍·不做)

### F7 對暫存區的 git 允許所有子指令,`push`、`fetch`、`remote` 都放行,與「擋開 PR」的目標不一致
severity: major
blocking: 是 — 快照要防的是被誘導對外動作,這條規則留了一條不經 gh 的對外寫入通道
引句:「每個 `-C` 疊起來的結果照第 2 點判在暫存區」
- 規則是「非唯讀白名單的子指令,只要 `-C` 指到暫存區就放行」。審查席在暫存區用 `git -C /tmp/x init`、`remote add origin <真實網址>`、`push origin HEAD:refs/heads/foo` 全都放行;或對既有的私有 clone(記憶檔載明推送用 `$CLAUDE_JOB_DIR/tmp/clone-x` 且已設 remote)直接 `git -C <clone> push`,remote 憑證是使用者的。
- `git -C <暫存區裡 repo 的 worktree> …` 的物件庫與 ref 是共用的,commit 與 branch 操作會寫回真 repo 的 refs。
- 失敗場景不需要惡意:被文件誘導「幫忙把分支推上去」,模型會自然選 `git -C /tmp/clone push`。
- 建議:暫存區內的放行也要有子指令白名單,明確排除 `push`、`fetch`、`pull`、`remote`、`clone`、`submodule`、`worktree`、`config`、`credential`。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·二·4)
file: `/Users/enzo/.claude/projects/-Users-enzo-harness-lumos-toolchain/memory/worktree-push-pass-branch-gap.md:12`

### F8 唯讀 git 白名單的旗標禁用誤擋常見用法,「整句」範圍不明,且 `-c` 的環境變數等價物沒擋
severity: minor
blocking: 否 — 誤擋的代價是席位換寫法重試;環境變數那項屬於「有心繞」範疇
引句:「而且整句沒有 `--output`、`-o`、`--ext-diff`、`-c`、`--exec-path`、`--git-dir`、`--work-tree`」
- 誤擋:`git ls-files -o`(列未追蹤)、`git log -c`、`git show -c`、`git grep -c`(計數)都是合法唯讀旗標;「整句」若指整個 Bash 字串,連 `git diff --stat | grep -c .`、`git log | grep -o x` 都被擋。快照沒說比對單位是詞還是子字串、是這個 git 段還是整行。`--output-indicator-new` 若用子字串比對也會誤擋。
- 漏擋:`-c` 被視為危險(能設 `core.pager`、`diff.external`),但等價的 `GIT_CONFIG_COUNT/KEY_0/VALUE_0`、`GIT_EXTERNAL_DIFF=…`、`GIT_PAGER` 只在第二支分支(非白名單子指令)檢查,唯讀白名單那支沒查。`git grep -O<指令>`(開啟檔案的外部程式)同理。
- 建議:寫明比對單位是同一個 git 段的詞;把 `GIT_` 開頭變數的檢查提到兩支分支共用。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·二·4)

### F9 席報告暫存處的前綴比對、迴圈編號含 `..`、祖先目錄搜尋三個邊界沒定義
severity: minor
blocking: 否 — 都要編排者或席位寫出怪值才會觸發,影響限於誤擋或漏擋單一路徑
引句:「`<暫存區>/lumos-seat-staging/<迴圈編號>/`」
- 資料夾名比對沒寫「整段比對」還是「字串前綴」:前綴比對會讓寫到 `lumos-seat-staging2/…`(使用者別的暫存資料夾)被誤判成席報告暫存處而擋寫,或反過來。
- 標記值只規定「以 `/` 切成恰好三段、每段非空」,所以迴圈編號 `..` 與 `.` 合格:`<暫存區>/lumos-seat-staging/../` 就是整個暫存區,等於把暫存區全部當成受保護、席位什麼都寫不了、什麼都讀不了;卷證資料夾變成 `governance/`。席名同樣可以是 `..`。應在標記驗證加「每段不得為 `.` 或 `..`、不含路徑分隔字元(`\` 等)」。
- 「指到…席報告暫存處這個資料夾本身」只擋指向該資料夾或其內,不擋它的祖先:`Grep path=/private/tmp pattern=.` 遞迴搜整個暫存區,同輪別席報告照樣被搜到。快照理由「別席報告在 repo 外,搜 repo 碰不到」只對不帶 path 的搜尋成立。
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,名詞與做法·二·3)

### F10 等待逾時與 fail-open 沒有任何留痕,而且等的是整批不是自己那一筆
severity: minor
blocking: 否 — 逾時只在引擎異常時才發生,但一旦發生,RETIRE-IF 與 REVISIT 要用的數字全部看不到
引句:「最多等 5 秒讓它們回報完再查表;等不到就照查不到處理(不是審查席,放行)」
- 5 秒逾時、斷詞失敗、真實路徑取不到(這項是擋)、外掛內部錯誤(放行),只有最後一項引擎會記;前兩種逾時放行外掛沒說要記。RETIRE-IF ① 要用「一次都沒擋過」判斷風險沒發生,而「根本沒生效」也長得一樣。建議逾時與 fail-open 時用 `$.ui.notice` 或固定開頭字串的事件留痕,REVISIT 的比例才算得出來。
- 等的是「同一會談所有啟動中的派工」。同時派十席時,表裡查不到的呼叫(非席位子代理、引擎的 fork 與 workflow 代理,型別檔說這類 id 沒有任何清單命名)每次碰到登記中的批次都等到齊;若十席分批交錯派出,等待可持續到 5 秒上限,拖慢非席位代理每一次工具呼叫。快照仍寫成「不會互卡」,型別檔只保證派工結果在子代理「啟動後」回報(型別檔第 362 行)。
- 席位極快結束:登記晚到時它已跑完,表項留到 `session.end`,量小但沒寫;且一個會談內累積的「啟動中」清單在 `/clear` 後是否還在,與誠實界線「`/clear` 都會清掉對應表」要對上(型別檔 4174 行寫 `/clear` 不重新載入外掛,表是否被清取決於實作)。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:359-368`
file: `docs/lumos-toolchain-knowledge/Projects/審查席唯讀隔離_計劃.md`(同引句所在節,做法·一與誠實界線)

### F11 相對路徑只以會談 cwd 解,子代理自己的 cwd 與 Bash 的持久目錄沒納入
severity: minor
blocking: 否 — `Write`、`Edit` 要求絕對路徑,實際只影響 `Grep`、`Glob` 的相對 `path` 與 Bash 的相對 `-C`,落空方向多半是誤擋
引句:「目標路徑先以會談 cwd 補成絕對路徑」
- 型別檔 `AgentSpawnInput.cwd` 允許子代理在別的目錄跑(型別檔 350-355 行)。審查席 cwd 在暫存區的 worktree 時,`Grep path=.` 解成會談 cwd(repo),誤擋或誤放都有。
- Bash 的當前目錄會隨先前 `cd` 持久,外掛看不到:`cd /tmp/t && git -C . commit` 被解成會談 cwd(多半是 repo)而擋(誤擋);反方向,會談 cwd 本身在暫存區時 `cd /repo && git -C . commit` 被解成暫存區而放行。
- 建議:相對 `-C` 與相對 `path` 一律擋(要求絕對路徑)並在理由文字教它改絕對路徑。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:350-355`

### 前輪修復驗收

對照 r1-邊界-sonnet.md 的 12 條:
- 前輪 F1(標記首字限 ASCII):格式限制已拿掉,中文迴圈編號與席名可過。但輪次欄新加的窄格式讓真實輪次 `r3-dref`、`r4-dref-delta`、`r5-recap`、`驗收` 不合格,且不合格時靜默放行。只修了一半,殘留見本輪 F1。
- 前輪 F2(別席報告在實際流程裡位置錯位):用「席報告暫存處」固定位置修了主流程;快照承認這是新慣例,而記憶檔現行寫的是 `$CLAUDE_JOB_DIR/tmp`,要編排者改。卷證那半仍以迴圈編號組路徑,與資料夾名不一致,repo 根來源也沒定,見本輪 F2。
- 前輪 F3(Grep/Glob 不帶 path 一律擋):已修。不帶 path 不擋,只看明確指向。
- 前輪 F4(同輪檔名規則兩頭誤判):delta、snapshot 不再被擋,已修一半;`std-r1-`、`v2-r1-`、`code-r1-`、`驗收-` 前綴的席報告仍不受保護,以及共用材料清單開放,見本輪 F3。
- 前輪 F5(第一行取法):只取第一個非空行、整行比對、不認程式碼區塊與縮排,已修。BOM 與全形空白的空行定義仍沒寫,見本輪 F1。
- 前輪 F6(repo 範圍只用會談 cwd):repo 範圍判定整段拿掉,原問題消失;換成相對路徑用會談 cwd 補全的小問題,見本輪 F11。
- 前輪 F7(路徑只做字串正規化):已修。改用真實路徑、折疊大小寫、NFC。唯一殘留是暫存區內有 repo 的情形,見本輪 F4。
- 前輪 F8(切段與包裝詞旁路):`&`、`env`、`command`、子殼層、`$(…)`、`bash -c` 都已納入,空白分隔的 `--git-dir` 也被整句比對擋住。斷詞失敗與 `-lc` 等變體是新缺口,見本輪 F5、F6。
- 前輪 F9(`-C` 的變數、波浪號、多個疊加):變數與波浪號改為擋、多個 `-C` 疊加已寫。相對 `-C` 的基準目錄仍沒定,見本輪 F11。
- 前輪 F10(啟動中等待沒有逾時):逾時 5 秒、`finally` 清除、成功被拒丟錯都清,已修;仍等整批,且逾時無留痕,見本輪 F10。
- 前輪 F11(同名席重派互通):快照沒再提,未處理,維持原判定(影響低)。
- 前輪 F12(10 分鐘快取):快取連同 repo 範圍判定一起拿掉,已修。

總結:最嚴重 major,blocking 6 條
