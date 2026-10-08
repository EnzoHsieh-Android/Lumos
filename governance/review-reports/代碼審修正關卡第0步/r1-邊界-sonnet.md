severity: major

# 邊界-sonnet 第 1 輪(鏡頭:邊界與輸入)

白話:作者想的是「設定檔不見」這一種怪況,但設定檔「在、只是跟提交裡那份不一樣」、平台根「在工作目錄、不在提交裡」這兩種更常見的怪況沒想到——而且我在使用者本機的 `pos-ios` 專案上兩種都看到了真的。另外「改名」這個邊界會讓第 5 項變成永遠過不了。

## F1 設定檔「已進版控但有未提交改動」時,先決條件看主工作目錄的版本、測試卻跑提交裡的版本
severity: major
blocking: 是
引句:「直接複製那一份進樹的同一位置,輸出說一句。」
file: `/Users/enzo/harness/pos-ios/.lumos/config.json`(本機實況:`git status` 顯示 ` M .lumos/config.json`,HEAD 版沒有 `platforms` 鍵,工作目錄版有 `ios`、`maestro` 兩個平台)
file: `scripts/lumos:4811`(`load_platforms` 讀的是傳進去那個根底下的 `.lumos/config.json`)
1. 快照只處理「樹裡沒有設定檔」才複製。設定檔已進版控、工作目錄有未提交修改時,樹裡是提交版,不會複製、也不會提醒「設定不一樣」。
2. 先決條件「每個平台的平台根(`load_platforms` 解析後)」對主工作目錄算;第 4、5 項用的 `load_platforms(樹)`、`_run_bound_tests`、`_bound_tests_check(Path(樹), …)` 讀樹裡那份。兩邊是兩份不同的設定。
3. 重現(唯讀):`git -C ~/harness/pos-ios show HEAD:.lumos/config.json` 讀不到 `platforms`(舊制單平台、沒有 `run_cmd`);主工作目錄版有 `platforms.ios.run_cmd`。照字面實作,先決條件按多平台通過,樹裡卻是舊制設定:`run_cmd` 是空的,第 5 項會走 `no-config` / 沒跑,結果跟 push 前閘(跑主工作目錄設定)對不上,而且「未提交改動提醒」只列檔名、不說這支檔會改變行為。
4. 缺口:沒有規定「樹與主工作目錄的設定檔不一致時怎麼辦」。前例 `_lint_copy_configs` 另外有 `is_file()`、大小上限、`OSError` 處理,快照的「直接複製」三樣都沒有:主工作目錄的設定檔是壞掉的連結或超大檔時會丟例外,不是回 2。
5. 修法方向:先決條件改用樹裡那份設定判(建樹之後才驗),或不一致就明講並判不過;複製段要有型別、大小、例外處理。
未實測 fix-check 本身(指令還不存在),依據是讀碼加上 pos-ios 實況。

## F2 平台根「在工作目錄、不在提交裡」(未追蹤的資料夾、巢狀 repo、子模組)通過先決條件,樹裡卻沒有這個資料夾;不支援的專案還會被 `loop next` 永遠提醒
severity: major
blocking: 是
引句:「平台根在 repo 外的專案(多根設定)本步直接回 2,不支援;」
file: `/Users/enzo/harness/pos-ios/.lumos/config.json`(`maestro` 平台 `root: ".maestro/"`;`git -C ~/harness/pos-ios ls-tree HEAD --name-only` 沒有 `.maestro`,`git status --short .maestro` 是 `?? .maestro/`)
file: `scripts/lumos:14105`(guard kill 用 `_kill_plat_top` 對每個平台根找它「自己的」repo 頂,表示平台根在別的 repo 裡是已知形態)
1. 快照的判法只問「平台根在 repo 頂底下嗎」。巢狀 repo、未追蹤資料夾都在工作目錄的頂底下,所以過關;但 `git worktree add` 只檢出提交,這種資料夾在樹裡不存在。
2. 最小重現(我在臨時目錄做的):外層 repo 底下有一個自己 `git init` 的 `ios/`,外層 `.git/info/exclude` 排除它;`git worktree add --detach ../n-wt HEAD` 之後 `ls ../n-wt` 只有 `README`,`ls ../n-wt/ios` 報不存在;同時 `Path('ios').resolve()` 在外層頂底下(判「在 repo 內」為真)。
3. 後果:`load_platforms(樹)` 只印一行警告、`_platform_test_index(樹)` 這個平台是空的,第 3 項對這個平台每支測試都報「找不到」;使用者照提示去補紀錄也修不好——失敗不可修復。另外,在這種資料夾裡改的程式,不會出現在 `base..修正後`。
4. 回 2 不記帳 + `loop next` 提醒只看「有沒有符合的 `passed`/`skipped-env` 事件」。於是:平台根在 repo 外、或上面這種專案,每次 `loop next` 都印「請跑 fix-check」,而那個指令永遠回 2;只有 `LUMOS_SKIP_FIX_CHECK=1` 能消掉。快照的隱患段把這件事當成「靠使用者回報」,但提醒本身就是會一直響的噪音。
5. 修法方向:先決條件改成「平台根的 `git rev-parse --show-toplevel` 等於 repo 頂,而且該路徑在 `修正後` 的樹(`git ls-tree`)裡」;不支援的專案要讓 `loop next` 提醒也識別得出來(同一支判斷共用),不要只在 fix-check 裡回 2。

## F3 `base..修正後` 內只要有任何一次改名,第 5 項就無條件判不過、而且沒有任何補救動作
severity: major
blocking: 是
引句:「`base..修正後` 有程式檔被改名時(`git diff -M --name-status -z` 的改名條目,判程式檔用 `_nodehome_code_kind`)這項也判不過」
file: `scripts/lumos:24797`(`_nodehome_code_kind`:沒有副檔名一律回 `'shebang?'`,不是 `None`)
1. 實測(`/opt/homebrew/bin/python3` 載入 `scripts/lumos` 後直接呼叫):`LICENSE`、`Makefile`、`Dockerfile`、`.gitignore`、`.weekly-stamp`、`scripts/run` 都回 `'shebang?'`;只有 `.md` 之類有副檔名的非程式檔才回 `None`。快照名詞段也寫了「沒副檔名、要看首行的也算,寧多判」。
2. 所以 `base..修正後` 之間只要有人改名過任何一個沒副檔名的檔(含簿記檔 `.weekly-stamp`、`.rotation-cursor` 這類,本 repo 的 git status 就有),第 5 項判不過。
3. 補救不存在:改名是歷史、紀錄檔無欄位可聲明、`base` 要往後挪就得放棄涵蓋範圍。唯一出口是跳過整道關(`LUMOS_SKIP_FIX_CHECK`)。快照把它當「保守」,但保守的前提是使用者能把它修成綠;這裡不能。
4. 而且 `loop next` 在沒有 `passed` 事件前一直提醒,等於改名一次、提醒永遠不消。
5. 修法方向:改名只算「對舊路徑補算一次波及」或判成「過但附警告」;至少「程式檔」在這裡要用真的判法(有副檔名且在清單裡,或首行真有 `#!`),不要用寧多判的那個。

## F4 `at` 的檔案與函式段:路徑形狀、檔案種類、讀法都沒規定,連「驗得到字面」這件事都能被標點或目錄騙過
severity: minor
blocking: 否
引句:「`unaffected` 的檔要在修正後的提交裡、函式段要找得到。不驗它真的是函式定義(各棧寫法不同,驗到字面就停)。」
file: `scripts/lumos:4811`(僅作對照;`git show` 實測見下)
實測(臨時 repo,git 2.39.2):
1. `git show HEAD:sub`(目錄)印出 `tree HEAD:sub` 加檔名清單,`git cat-file -e HEAD:sub/` 回 0;所以 `unaffected` 寫 `at: "sub:f.py"` 若用「在提交裡」判存在、再用 `git show` 取內容找函式段,會拿目錄清單當程式碼比對,通過。
2. 追蹤的符號連結(模式 120000)`git show HEAD:lnk.py` 印的是連結目標字串;若改成從樹的磁碟路徑讀,則 `Path(樹)/"../../etc/hosts"`、絕對路徑 `/etc/hosts`、`lnk.py` 都會讀到樹外面(實測 `ESCAPES`)。快照沒說用哪一種讀法,也沒有路徑正規化規則(`./x`、`x//y` 對 `git diff --name-only` 的輸出比不上,`HEAD:./x` 是相對於目前工作目錄解析)。
3. 函式段只說「不能是空的」。` `(一個空白)、`.`、`(` 這類沒有英數字的段,「前後不接英數字或底線」幾乎在每支檔都成立,等於不驗。
4. 檔名含冒號(POSIX 允許)寫不出來,因為第一個冒號就切。非 UTF-8、超大、二進位的檔怎麼讀也沒規定(快照自己在別處提到「非 UTF-8 另有 Issue」)。
5. 修法方向:`at` 的檔先正規化並拒絕絕對路徑、`..`、`.` 段;用 `git ls-tree` 確認是一般檔(100644/100755);函式段至少要含一個英數或底線字元,且先去空白;讀檔給大小上限與解碼容錯。

## F5 輸入大小與總耗時沒有上限(紀錄檔、`tests` 清單、`base` 範圍)
severity: minor
blocking: 否
引句:「一次大約 5 分鐘,多半花在合約測試。」
file: `scripts/lumos:38606`(`_run_bound_tests` 每支單獨逾時預設 180 秒,整批沒有總預算;`LUMOS_TEST_TIMEOUT` 可調)
1. 5 分鐘是 `base` 設對的情況。`base` 寫成離很遠的提交(例如整條分支的起點)時 `base..修正後` 牽連的合約數隨之放大,第 5 項串行跑,沒有總時限、沒有進度、中途 Ctrl-C 留樹與孤兒子行程(快照已承認)。
2. 紀錄裡 `tests` 沒有筆數上限:每支獨立 `-k` 跑(本 repo 約 2.7 秒/支,逾時時 180 秒/支),幾百支就是半小時以上。
3. 紀錄檔本身沒有大小上限(只提到「解析深度過深」);`<輪>-fix.json` 若是符號連結、具名管道或超大檔,`loop next` 為了算 `record_sha256` 也要整份讀進來。
4. 修法方向:紀錄檔大小上限(例如 1 MB)、非一般檔不讀;`tests` 筆數與全程總時限寫進先決條件,超過就回 2 並說明。

## F6 「前一輪」的認定與前一輪紀錄的讀法沒有定義邊界
severity: minor
blocking: 否
引句:「審查帳上這一輪的前一輪(照帳上輪次出現的順序)有修正紀錄、其中有一組跟這組同類別」
file: `scripts/lumos:20589`(`_disposal_round_groups` 已有分輪規則,含 `__seqN` 與「被隔開又重現就擋」)
1. 真帳實況(我數 `docs/.canary-log.jsonl`):輪次字串有 `r3b`、`r3-dref`、`r4-dref-delta`、`r5-recap`;帳內有 10 個迴圈最新一輪沒有載體席。「前一輪」若取順序上緊鄰的那輪,遇到沒有載體的輪就等於沒有修正紀錄,第 2 項靜默略過;快照沒說取「前一個有載體的輪」。
2. 前一輪的輪次字串來自帳、不是來自 `--round`,而路徑字元檢查只管 `--round` 與迴圈編號;`canary record --round` 只擋 `__` 開頭,帶 `/` 的輪次寫得進帳,拼成 `<迴圈>/<前一輪>-fix.json` 就是路徑穿越讀。
3. 前一輪的紀錄檔壞掉、不存在、過深時怎麼辦沒寫:靜默略過會讓第 2 項整個失效,回 2 又會讓本輪被上一輪卡死。
4. 修法方向:沿用 `_disposal_round_groups` 取分輪;「前一輪」限定為有載體席的輪;前一輪的輪次字串也過同一組字元檢查;前一輪紀錄不可讀時明講規則(建議視為「無」並印一行說明)。

## F7 `--regression-set` 的空值判法:`,`、空白、重複 id 會混過「空字串回 2」
severity: minor
blocking: 否
引句:「其餘解析照 `--folded-set`;空字串回 2;id 都要在 `--findings-set` 裡,否則回 2」
file: `scripts/lumos:8566`(`_ids`:`[x.strip() for x in raw.split(",") if x.strip()]`)
file: `scripts/lumos:8606`(`--refuted-set` 對空項明確回 2,理由就是「空項會被當 none」)
實測 `_ids` 的輸出:`''`→`[]`、`','`→`[]`、`' '`→`[]`、`'F1,,F2'`→`['F1','F2']`、`'F1,F1'`→`['F1','F1']`、`'none,'`→`['none']`、`'None'`→`['None']`。
1. 「其餘解析照 `--folded-set`」會連 `_ids` 一起繼承。`,` 與 ` ` 解析成空清單,跟 `none`(存空清單)同一個結果,而快照要靠「沒填 vs 明寫 none」區分「沒判過」與「判過沒有」;字面的「空字串回 2」只擋得到 `''`,這兩個漏網就是 `--refuted-set` 那段註解已經警告過的混法。
2. 重複 id 不擋:`F1,F1` 存成兩筆,REVISIT 那天「上一輪修補造成的發現有幾條」會灌水(`--findings-set` 自己有擋重複,這裡沒有)。
3. `none,` 會被當成 id `none`、再因不在 `--findings-set` 回 2,訊息看起來莫名;大寫 `None`、`NONE` 同理。
4. 修法方向:規定「解析後為空清單一律回 2(不是只看原字串)」「重複回 2」「有空項回 2」,並在訊息裡提示要寫小寫 `none`。

## F8 平台根比對沒規定兩邊都取實際路徑;`load_platforms` 遇到壞設定會丟 `TypeError`
severity: minor
blocking: 否
引句:「每個平台的平台根(`load_platforms` 解析後)都在 repo 頂底下;」
file: `scripts/lumos:4811`(多平台分支 `root = (repo_root / root_str).resolve()`;單平台分支回的是沒取實際路徑的 `repo_root`)
實測:用符號連結路徑 `lnk -> repo` 當 `repo_root`,`load_platforms` 回的 `root` 是 `…/repo`,`root.relative_to(lnk)` 丟 `ValueError`(「在 repo 外」);`a`(`root: "."`)與 `b`(`root: "scripts"`)都被誤判。macOS 的 `/var` 對 `/private/var` 是同一種形狀。快照只在清殘骸那段寫了「兩邊都先取實際路徑」。
另測:`platforms.a.root` 是 `5`、`null`、`["a"]` 時 `load_platforms` 丟 `TypeError`(不是它 docstring 說的 `ValueError`);含 NUL 時丟 `ValueError`。快照的先決條件沒說「`load_platforms` 丟任何例外都回 2」,照字面會是未處理的例外加回傳碼 1。
修法方向:先決條件兩邊都 `resolve()` 再比;`load_platforms` 呼叫整個包 `except Exception` 回 2。

## F9 測試名過 `[test:名]` 解析時,名字裡的 `]` 會被截掉,紀錄寫的跟實際驗的不是同一支
severity: minor
blocking: 否
引句:「每支測試名包成 `[test:名]` 交給 `resolve_test_refs`(它丟 `ValueError` 時接住,這支判不過並附原因),要恰好解析出一支」
file: `scripts/lumos:4463`(`TEST_REF_RE = \[test:\s*([^\]]+)\]`)與 `scripts/lumos:4887`(`invariant_test_refs` 逗號切分)
實測 `resolve_test_refs`:`'t_x]junk'` →`[('python','t_x')]`(恰好一支、通過);`'t_x] [test:t_y'` →兩支(判不過,這個方向沒事);`'t_a,t_b'` →兩支。
1. 紀錄寫 `t_x]junk`,工具驗的是 `t_x`——「恰好一支」成立、`_KILL_METHOD_OK_RE` 對解析後的 `t_x` 也成立,通過;紀錄裡那個名字從沒被驗過。
2. 修法方向:解析後的方法名必須等於原名去掉前後空白(多平台時等於去掉平台前綴後的原名),不等就判不過。
(此條只是邊緣輸入,失敗方向是放寬一支名字,所以標 minor。)

---
已讀,無 finding 的節:「名詞」「回退」。「`base` 各種寫法」我實測了 `git rev-parse --verify --end-of-options "<x>^{commit}"`:空字串、`-x`、`--help`、帶空白或換行、`HEAD^{tree}` 都回非零,`HEAD`、`HEAD@{0}`、分支名都轉成 40 碼;`:/文字` 這種寫法因為被後面的 `^{commit}` 吃進去也回非零。快照那段(「以 `-` 開頭的輸入不會被當成旗標」)核對成立。派工單形狀我數了 `governance/review-reports` 真檔:`seats` 428 份、頂層單席 105 份、頂層陣列 1 份;沒有字面 `<輪>-dispatch.json`、只有 `-dispatch-<席>.json` 的輪有 29/459,這些輪 `base` 會留空由人補,不是錯。`--regression-set` 的「第一輪」判法與載體席取法沒有發現額外邊界問題(另兩個迴圈有歷史上同輪兩筆載體,屬舊帳、快照寫的是新寫入規則)。

最高等級:major,blocking 共 3 條
