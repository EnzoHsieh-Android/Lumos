severity: major

我讀了計劃全文與既有的 `dispatch-lens` 程式,並做了實驗。實驗在臨時 repo 跑,已刪。實驗結果是三件事。第一,`GIT_INDEX_FILE` 指向暫存 index 時,`read-tree` 和 `update-index` 會執行 `post-index-change` 掛鉤,我裝的記號被寫了三次。第二,不掛 ref 的提交不會出現在 `rev-list --all` 的數量裡。第三,`hash-object` 會順著符號連結讀目標內容,而 `is_file()` 對指向檔案的連結回 true。

severity: major
blocking: 是 — S18 的「提交數不變」照字面寫成測試永遠綠,擋不住 spec-freeze 偷建提交
引句:「不建提交(物件庫的提交數不變)、不寫 `--out`」
問題:spec-freeze 建的是不掛 ref 的提交。測試最自然的量法是 `rev-list --all --count`,看不到這種提交。我實測建立提交後該數字仍是 1。條款沒指定量法。
具體失敗情境:實作先 `commit-tree` 再檢查,或檢查順序寫反,S18 照樣綠。要量得到必須用 `cat-file --batch-all-objects --batch-check` 數 commit 類物件,或比對前後物件清單,條款要寫明。
佐證:實驗輸出 `rev-list --all count: 1`(建立懸空提交之後)

severity: major
blocking: 是 — 做法 9 的拒絕清單漏掉 spec-freeze 自己的 1MB 上限,行為沒定義
引句:「最後用第 3 條同一支讀法從這個提交讀出計劃,原子寫進 `--out`」
問題:第 3 條的讀法有 1MB 上限,超過就回 `spec_too_large`。但提交已在這一步之前建好。做法 9 的拒絕清單(空白、路徑規則、非一般檔、無 HEAD)與 S18 都沒有「超過 1MB」。
具體失敗情境:對 2MB 的計劃跑 spec-freeze,結果有四種:留下懸空提交但不寫 `--out`;rc 沒定義;印出一行貼了之後,每個席都回 `spec_too_large`;或先擋。條款完全不約束。同一支 `_nodehome_cat_blobs_capped` 對單項回 None 也沒區分「過大」與「讀不到」。spec-freeze 失敗時印什麼代碼、rc 是多少也沒定義,只有「rc 非 0」。

severity: major
blocking: 是 — S9 在實作前就是綠的,先紅不成立,而且空記錄也會過
引句:「每一筆解析後都應在會談 repo 根底下,沒有一筆落在計劃所在的另一個工作樹」
問題:實作前,提交寫法會被當成工作樹路徑。舊程式只跑 `git -C <會談目錄> rev-parse --show-toplevel` 就以 rc 2 退出,所有記錄都在會談根底下。條款沒要求同時斷言 rc 0、輸出含固定席、且記錄至少有 ls-tree、cat-file 等預期呼叫,所以這條測試不會紅。
具體失敗情境:實作漏做,或提交讀取壞掉提早失敗,S9 都是「零筆違規」而綠。
另外,假 git 腳本的三個搭法細節也沒寫:
- 要用 `-C`、cwd、`GIT_DIR` 三種來源判斷「解析後」的位置。
- 它要先取得真 git 的絕對路徑再前置 PATH。
- 測試要把改過的 PATH 傳給 impact 子行程。既有測試是行程內直接呼叫 `m.cmd_dispatch_lens_spec`,環境繼承要明寫。
PATH 前置的腳本在 macOS 和 Linux CI 都可行,只要用 `#!/bin/sh`。
佐證:`scripts/test_lumos.py` 的 `t_dispatch_lens_spec_mode` 是行程內呼叫;`scripts/lumos` 的 `cmd_dispatch_lens_spec` 開頭只跑 `rev-parse`

severity: major
blocking: 是 — 「不跑掛鉤」的條款只測三種掛鉤,實測還有第四種會跑
引句:「會留記號的 pre-commit、commit-msg、post-commit 掛鉤與會留記號的 clean 過濾器」
問題:做法 9 與實務隱患都宣稱「不跑掛鉤」,S17 卻只列三種提交掛鉤加 clean 過濾器。我實測,指向暫存 index 時 `read-tree` 和 `update-index` 會執行 `post-index-change`,記號被寫了三次。`reference-transaction` 這次沒跑,但 S17 也沒列。`core.fsmonitor` 這類設定會執行外部程式,同樣沒涵蓋。
具體失敗情境:使用者裝了 `post-index-change` 掛鉤,spec-freeze 在計劃所在的工作樹執行掛鉤。S17 全綠,條款宣稱的性質卻不成立。要嘛改寫宣稱(只保證不跑提交類掛鉤),要嘛 S17 補測 `post-index-change`,並讓實作加 `-c core.hooksPath=/dev/null` 之類。
佐證:實驗輸出 `marks:` 之後出現三行 `run`

severity: major
blocking: 是 — spec-freeze 的「一般檔」判定放過符號連結,可把 repo 外檔案凍進提交
引句:「而且要是工作樹上的一般檔」
問題:這句話沒說用 `is_file()` 還是 `lstat`。`is_file()` 會順著連結走,`hash-object` 也一樣。我實測指向 `/etc/hosts` 的連結通過 `is_file`,`hash-object` 算出的 hash 等於 `/etc/hosts` 本身。
具體失敗情境:
- 計劃路徑是連結。`update-index --cacheinfo 100644` 把 repo 外檔案內容寫成 100644 的 blob,快照寫出去。這與工作樹那條路「計劃必須在 repo 內」(外家 r1 M3)的既有邊界矛盾。
- 路徑中間有符號連結目錄也是同理。
S18 的「不是一般檔」只說得出目錄,先紅用的夾具沒指明要含符號連結。
- 另一個沒定義的地方:`<mode>` 取自工作樹的執行位元,還是固定 100644,條款沒說。HEAD 裡是 100755 時結果不確定。

severity: major
blocking: 是 — 檢查順序沒定義,同時違反兩條規則的輸入沒有期望結果
引句:「不合就回 `spec_outside_repo`」
問題:提交寫法同時有多個失敗原因時,回哪個代碼沒有定義。幾個例子:
- 短編號加壞路徑,回 `spec_rev_missing` 還是 `spec_outside_repo`?
- 路徑合規但 slug 在會談目錄不存在,而且該 blob 在提交裡也不存在,回 `no_knowledge`(rc 3)還是 `spec_missing`(rc 2)?
- 空白或大小寫混用,例如 `Docs/` 或 `-Knowledge`。macOS 的 `is_dir()` 不分大小寫會通過,`ls-tree` 區分大小寫,於是同一份輸入在 macOS 與 Linux 回不同代碼。
S2、S3 只各測單一原因,無法釘住順序。
另外,「空白」的範圍沒定義:tab、換行、全形空白 U+3000、NBSP。標記文法 `\S+` 在 Python 的 str 模式下對 U+3000 的處理與「半形空白」不同。S3、S18 只說「空白」,測試無從選夾具。
其餘「前兩段」的邊界也沒期望結果:
- `docs/x-knowledge` 沒有第三段。
- `docs/-knowledge/…` 是空 slug。
- `docs/x-knowledge/` 在做法裡被「結尾 `/`」擋掉,S3 沒有對應夾具。

severity: minor
blocking: 否 — 屬於覆蓋缺口,不影響已有條款的先紅
引句:「剛好 1MB(1048576 位元組)照讀,多一個位元組就擋」
問題:上一輪列的邊界值現況如下。
- 有期望結果:大寫、非 40/64 碼、冒號後空、多冒號、`./`(算 `.` 段)、1MB 邊界、目錄、符號連結、子模組。
- 64 碼成功路徑完全沒測。S2 只測了 SHA-1 repo 寫 64 碼的失敗。要驗成功需要 `git init --object-format=sha256`,CI 的 git 版本與可用性沒說。我實測 SHA-1 repo 對補零到 64 碼的字串回 rc 1,符合預期。
- 混合大小寫的 40 碼沒測。
- 超過 64 碼的十六進位加冒號沒測。
- NFD 條款寫「不處理」且夾具只用 NFC,等於沒有期望結果。macOS 使用者貼 NFD 路徑時,拿到的是 `spec_missing` 還是 `spec_outside_repo`?
- 二進位計劃(含 NUL 或非 UTF-8)沒條款。做法寫了 `errors="replace"`,S4 沒測。
- 冒號前是 6 碼十六進位(算工作樹路徑)與恰好 7 碼(算提交寫法)的分界,S2 沒列。
具體失敗情境:實作把門檻寫成 `>= 8`,或 64 碼成功路徑壞掉,S2 到 S4 都不會紅。

severity: minor
blocking: 否 — 掛鉤層覆蓋不全,但現有條款沒有矛盾
引句:「`no_knowledge` 與範圍類代碼照現在記 `error`」
問題:S12 到 S14 之間有幾個缺口和一處矛盾。
- 做法 78 說 `no_knowledge` 記 `error`,做法 79 又說工作樹寫法失敗 note 是 `spec_worktree <代碼>`。`no_knowledge` 帶不帶字首沒定,S14 只斷言 kind 是 `error`。
- 沒測的組合:`spec_source: commit` 配 `spec_missing`、`spec_outside_repo`、`spec_too_large`;`worktree` 配 `no_knowledge`;逾時事件不帶字首;缺 `spec_source` 的新舊混搭;`lens_fail` 是計劃類代碼但標記值是範圍。
- S13 要求「不應出現範圍」,但說明行引用了 `{what}`。如果使用者的計劃路徑含「範圍」二字,斷言會誤紅,夾具要避開。
- S11 的「lumos 印得出的代碼集合」沒說從哪取,lumos 端沒有登記表。現況 `_dispatch_lens_fail` 只收字串,測試只能靠掃原始碼。要明定一份常數。

severity: minor
blocking: 否 — 輸出規格不完整,但不影響先紅判斷
引句:「`--json` 的成功列與失敗列都帶 `spec_source`」
問題:新代碼只在 `--json` 印出,S2、S3、S4 沒寫明要帶 `--json`。非 `--json` 時新代碼的 stderr 原文也沒定義,只能測 rc。「整批逾時回 `spec_missing`」沒有任何條款,也很難造夾具。`ls-tree` 的輸出在中文檔名下會被 quote(`core.quotePath` 預設值)。「正好一列」如果比對檔名會對不上,條款沒要求用 `-z` 或只看 mode 與 type。

severity: minor
blocking: 否 — S16 的比對方式可能因 git 自己刷新而假紅
引句:「真的 index 檔位元組、HEAD 與目前分支都應不變」
問題:工作樹的 index 路徑在 worktree 裡是 `.git/worktrees/<n>/index`,不是 `.git/index`,條款沒指明用 `rev-parse --git-path index`。測試在前後跑 `git status` 之類會刷新 index 的指令時,位元組會變而假紅。條款應限制「前後之間只許做唯讀不刷新的指令」。

已讀,無 finding:緣起、PRIOR-ART、回退各步、REVISIT 行的可執行性。

總結:最高等級 major,blocking 共 6 條。
