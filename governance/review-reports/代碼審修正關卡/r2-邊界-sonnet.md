severity: major

席:邊界-sonnet。實驗在 `fg-r2-work-邊界-sonnet/e`(自建小 repo,macOS APFS 預設大小寫不分)與 `fg-r2-work-邊界-sonnet/repo`(共用 clone,只讀碼)。

## F1 紅樹造法沒指定 -z:中文、空白、引號檔名會被 git 加引號,整段路徑對不上
severity: major
blocking: 是
引句:「非測試檔一律換回 `base` 的內容(`base` 沒有的就刪掉);測試檔、輔助檔、測試資料都留修正後的版本」
file: `scripts/lumos:24815-24830`(`_nodehome_git`/`_nodehome_split_z`:本 repo 讀 git 路徑一律走 `-z` 加位元組解碼,這份設計寫的 `git diff --no-renames --name-status` 沒有 -z)
1. 實測(`e` repo):base 有 `中文 檔.py`、`we"ird.py`,修正後改了它們。`git diff --no-renames --name-status B H` 印出 `M	"\344\270\255\346\226\207 \346\252\224.py"` 與 `D	"we\"ird.py"`(整串帶雙引號、八進位跳脫);加 `-z` 才是 `M|中文 檔.py|`、`D|we"ird.py|`。
2. 字面實作會把帶引號的整串當路徑:`git show base:"\344..."` 失敗,被歸成「`base` 沒有的就刪掉」,磁碟上的真檔根本沒被換回 base。紅樹因此還帶著修正,測試在紅樹通過,判「修之前就通過」回 1,而且每次重跑都一樣,使用者找不到原因。
3. 同一份清單還用在 `fixed` 的檔「在 base..修正後 之間有改動」那條檢查:有中文檔名的 `fixed` 路徑一律被判「標了已修卻沒改過那支檔」。
4. 本 repo 的圖譜筆記與消費專案(中文專案)都有中文檔名,不是理論輸入。失敗方向是擋,但沒有任何補救路徑(只能整道跳過)。
5. 修法方向:規格寫明用 `-z` 並用位元組解碼(同 `_nodehome_split_z`),`status` 那條已寫 -z,這條漏了。

## F2 「把非測試檔換回 base」沒定義各種檔案型態的換法:符號連結會穿透寫、檔案變資料夾會當掉、大小寫改名會把檔案刪掉
severity: major
blocking: 是
引句:「非測試檔一律換回 `base` 的內容(`base` 沒有的就刪掉)」
file: `scripts/lumos:24815`(`_nodehome_git` 位元組讀法可借用,但設計沒指定)
實測都在 `e` repo,同一個根因(逐檔「讀 base 內容、寫進紅樹」沒分檔案型態與順序):
1. 符號連結穿透:`git ls-tree` 顯示 base 的 `lnk` 是 `120000`,`git show base:lnk` 吐出的是連結目標文字 `a.py`。紅樹裡 `lnk` 在修正後是指向別處的連結(或原本是普通檔、修正後改成指向 `../outside.txt` 的連結)時,`open('L','wb').write(...)` 會寫進連結目標:實測 `outside.txt` 的 `SECRET` 被改成 `base content`。目標可以在工作樹之外,代表修正關卡會改到使用者的別的檔案。
2. 檔案變資料夾(D/F):base 的 `fileA` 是檔、修正後是資料夾 `fileA/x`。`--no-renames --name-status` 順序是 `D fileA` 先、`A fileA/x` 後;對 `D fileA` 寫入回 `IsADirectoryError: [Errno 21] Is a directory: 'fileA'`(實測),整次修正關卡當掉而不是回 1 或 2。
3. 大小寫改名:macOS 預設檔案系統大小寫不分(`core.ignorecase=true`)。`Foo.py`→`foo.py` 的 diff 是 `D Foo.py`、`A foo.py`(實測)。照順序先把 base 的 `Foo.py` 寫回(其實是寫到同一支 `foo.py`),再因 `A foo.py` 刪掉它,紅樹最後沒有這支檔,測試在紅樹因找不到檔而紅,被當成「先紅」通過(放錯)。
4. 子模組指標:`A subm`(模式 160000)實測 `git show H:subm` 回 `fatal: path 'subm' does not exist`,沒有「讀 base 內容」這回事。
5. 二進位檔要用位元組讀寫(文字模式會損毀);只改了執行權限位元(`chmod +x`)的非測試檔內容沒變,「換內容」換不回權限。設計一個字都沒提,字面實作對這幾類各自走出不同的當掉或放水路。
6. 修法方向:規格寫明「照 git 的模式逐型態還原(用 `git checkout base -- 路徑` 或 `git restore --source` 這類由 git 處理型態與權限的做法,不自己寫檔)」,而且先處理刪除再處理寫入。

## F3 依賴資料夾只連「平台根」那一層:repo 頂或祖先層的 `node_modules`、`.venv` 沒連,子資料夾平台的測試整個跑不起來
severity: major
blocking: 是
引句:「兩棵樹在平台根都把依賴資料夾連回主工作目錄(`_lint_link_deps`:`node_modules`、`.venv`、`venv`;」
file: `scripts/lumos:23630-23638`(`_lint_link_deps` 只連傳進來的那一層,`_LINT_DEP_DIRS` 在 `scripts/lumos:23590`)
file: `scripts/lumos:23594-23604, 23623-23628`(設計自稱沿用的先例 `_lint_new_support` 是對「所有祖先目錄,含專案根」逐層連,這份設計只連平台根)
1. 場景:多平台設定 `backend` 的 `root` 是 `backend/`,Python 的 `.venv` 在 repo 頂(很常見);或 npm workspaces、pnpm 把 `node_modules` 提到 repo 頂,平台根是 `apps/web`。
2. 設計只呼叫 `_lint_link_deps(主/backend, 樹/backend)`:`主/backend/.venv` 不存在,`src.is_dir()` 為假,靜默略過(函式裡也沒有任何輸出)。隔離工作樹在系統暫存資料夾,Node 往上找不到任何 `node_modules`,Python 的 `run_cmd` 若寫 `.venv/bin/pytest`(相對於 repo 頂)也不存在。
3. 結果:綠樹第一支就不過,輸出只剩那句通用提示「如果是隔離工作樹缺東西……」;使用者無法靠改紀錄修好,只能整道跳過。這恰好是「平台根是子資料夾、主工作目錄沒有那個資料夾」那種輸入。
4. 修法方向:對平台根與它的所有祖先層直到 repo 頂都連(直接呼叫 `_lint_support_dirs` 那套),找不到任何依賴資料夾時在輸出明講「沒連到任何依賴資料夾」。
5. 資料夾很大本身沒問題:連結不複製;`worktree remove --force` 與 `shutil.rmtree` 遇到符號連結只拿掉連結不跟進(未實測 rmtree 跟 git 的組合,依據是這兩者對符號連結的標準行為,⚠ 交編排者在 S4「暫存資料夾已刪、主目錄不變」的測試裡順手驗 `node_modules` 還在)。

## F4 平台根「相對 repo 頂的路徑」怎麼算沒寫:`load_platforms` 回的是 `resolve()` 後的絕對路徑,repo 路徑含符號連結或平台根在 repo 之外就算不出來
severity: minor
blocking: 否
引句:「平台根相對 repo 頂的路徑」
file: `scripts/lumos:4852`(`root = (repo_root / root_str).resolve()`)
file: `scripts/lumos:38626`(合約測試閘直接用這個絕對 `root` 當 cwd,從沒需要換算成別棵樹的路徑)
1. 實測:repo 在 `/tmp/rr`(macOS 的 `/tmp` 是 `/private/tmp` 的連結),`(/tmp/rr/ios).resolve()` 是 `/private/tmp/rr/ios`,`relative_to(Path('/tmp/rr'))` 丟 `ValueError`;平台根設成 `../elsewhere` 時 `relative_to` 也丟 `ValueError`。
2. 設計是新增的換算,合約測試閘本身沒這問題所以沒有可沿用的先例。字面實作遇到使用者用符號連結路徑開專案(`~/code` 連到別的磁碟很常見)就當掉。
3. 修法方向:兩邊都先 `resolve()` 再相對,相對不出來(平台根在 repo 外)就回 2 並說明。

## F5 殘骸清理:標記檔缺失怎麼判沒定義、前綴比對在 macOS 會失配、可能誤刪別人用 --force 的工作樹
severity: major
blocking: 是
引句:「掃 `git worktree list --porcelain` 裡路徑帶修正關卡前綴、標記檔的行程已經不在的,`worktree remove --force` 加刪資料夾,再 `worktree prune`」
file: `scripts/lumos:14105`(`cmd_guard_kill` 現在沒有任何殘骸掃描,這段是全新寫法)
1. 標記檔不存在時怎麼辦沒寫:「行程已經不在」對「根本讀不到標記檔」(寫不進去、磁碟滿、被人刪、另一個會談剛建好工作樹但還沒寫標記)沒有判法。若當作「行程不在」就清:兩個會談同時開頭清殘骸時,A 剛 `git worktree add` 完、標記還沒落地,B 掃到就 `--force` 刪掉 A 正在用的樹,A 的測試在中途失去工作目錄,結果是亂紅或亂綠(S10 只測了「行程已死」與「標記存在且行程活著」兩個格,這個格沒測)。若當作「不動」,標記寫不進去的那次一旦被 SIGKILL 就永遠清不掉。
2. 「路徑帶前綴」在 macOS 實測會失配:`tempfile.mkdtemp(prefix=...)` 回 `/var/folders/.../lumos-fixcheck-xxx`,而 `git worktree list --porcelain` 印的是 `/private/var/folders/.../lumos-fixcheck-xxx/wt`(realpath,實測)。用 mkdtemp 的字串去 `startswith` 比會永遠比不中,殘骸永遠不清。
3. 「前綴」沒定義比的是整條路徑還是最後一段:別人(或別的工具,審查提到的「別的工具建的工作樹」)手建、路徑裡剛好含這個前綴的工作樹,沒標記檔,會被 `--force` 刪(含未提交的改動)。
4. 行程編號被重用:標記裡的 pid 被別的行程拿去用,`kill -0` 判活,殘骸不清(安全方向,但設計沒講會殘留到那個行程結束);反過來若只看 pid 不看啟動時間,同機別的使用者的行程碰巧同號也一樣。設計沒說是否在標記裡多記啟動時間。
5. 修法方向:規格明寫(a)標記檔在 `worktree add` 之前寫好、(b)缺標記檔只在樹的建立時間超過某個寬限(例如 10 分鐘)才清、(c)兩邊都用 realpath 比、前綴只比暫存資料夾最後一段、(d)不是自己建的(沒有標記、沒有前綴)絕不動。

## F6 `at` 的函式段比對:空字串、特殊字元、中文名稱、路徑正規化都沒定
severity: minor
blocking: 否
引句:「函式那段要在那支檔裡出現、前後不接英數字或底線」
1. 空的函式段:`"at": "scripts/lumos:"` 或根本沒有冒號。設計沒說怎麼辦;字面實作 `"" in 內容` 恆真(實測 `"" in "anything"` 為 True),「函式找得到」被空字串騙過。
2. 「不接英數字或底線」若用 `\b` 或 `\w` 實作:名稱頭尾是非字元(Ruby/Kotlin 的 `empty?`、C++ 的 `operator()`)時 `\bempty\?\b` 在 `empty? foo` 上不命中(實測 False)。若用 `[A-Za-z0-9_]` 就命中(實測 True)。兩種寫法結果相反,設計沒指定。
3. 中文函式名:用 `[A-Za-z0-9_]` 時 `def 檢查路徑(x)` 會讓 `檢查` 命中(實測 True)——這是設計想擋的「前綴湊巧」;用 `\w`(Python 的 Unicode 預設)就擋住(False),但同一個 `\w` 會讓中文註解裡的 `呼叫檢查函式` 命中不了。本 repo 目前沒有中文 `def`(grep 過),但設計要接消費專案。
4. 函式名要不要當字面(escape)沒寫:`operator+`、`foo$bar` 當正規式會誤判或丟例外。
5. 檔路徑要不要正規化沒寫:`./scripts/lumos`、`scripts//lumos` 跟 `git diff` 輸出的 `scripts/lumos` 對不上,「`fixed` 的檔有改動」會誤判沒改過。
6. 修法方向:規格寫明「函式段去空白後不得為空、當字面比對(不是正規式)、邊界字元類用哪一套(建議 Unicode 的 `\w`)、檔路徑先 `posixpath.normpath` 且不得以 `/` 或 `..` 開頭」。

## F7 總時間上限:非數字、0、負數沒定義,而且只在項目之間檢查,擋不住單一項目超時
severity: minor
blocking: 否
引句:「`.lumos/config.json` 的 `fix_check.max_minutes`(預設 20)用完,還沒跑的測試與項目不跑、這項判不過」
file: `scripts/lumos:38618`(合約測試閘的 `float(環境變數 or "180") or 0) or None`,「0=不限」;非數字會直接丟 ValueError)
1. 設定值沒有讀取規則:壓力指令那條寫了「讀不懂用預設並警告」,`max_minutes` 沒寫。`0`:是「立刻用完、什麼都不跑、回 1」還是跟 `LUMOS_TEST_TIMEOUT` 一樣的「0=不限」?設定檔寫 `0` 的人通常是想「不限」。負數、字串 `"20"`、JSON 的 `true`(Python 裡 `True==1`,等於 1 分鐘)、`Infinity`(Python 的 `json.loads` 接受),設計一概沒說。
2. 沿用合約測試閘的每支逾時時,`LUMOS_TEST_TIMEOUT=0`(不限)加上總時間只在「還沒跑的」之間檢查,一支卡住的測試讓整個指令不會回來,總時間形同虛設;環境變數是非數字(例如 `abc`)時 `float()` 在 `scripts/lumos:38618` 就丟例外,修正關卡繼承這個行為。
3. 第 5 項是 `_bound_tests_check` 一整支黑盒(設計自己寫「一次推送實測 59 支約 4 分鐘」),先紅後綠在第 19 分鐘結束時第 5 項照跑完,整體可超過上限幾分鐘;第 2 步壓力指令每條逾時 300 秒也沒被剩餘時間削減。S11 只測「停止還沒跑的測試」。
4. 修法方向:規格寫「`max_minutes` 必須是有限正數,否則用預設並警告;`LUMOS_TEST_TIMEOUT` 與壓力指令逾時都取 min(自己的值, 剩餘總時間)」。

## F8 `--template`:輸出走哪個串流沒寫、先決條件有沒有適用沒寫
severity: minor
blocking: 否
引句:「印出骨架到標準輸出(照表態樣板的做法,不寫檔)」
file: `scripts/lumos:33929`(表態樣板的先例:提示一律寫 stderr,標準輸出只留純 JSON,才能 `> 檔`)
file: `scripts/lumos:40022`(先例用法就是 `--dispositions-template > 檔`)
1. 設計在同一節寫「輸出列出這幾條判成不用修正紀錄」、「輸出提醒『記帳時帶 `--finding-kind`……』」,以及「要修正紀錄的折入是 0 條 → 印『這輪沒有要修正紀錄的折入』回 0」,沒說這些字走標準輸出還是標準錯誤。走標準輸出,使用者照先例 `--template > r1-fix.json` 存下來的就不是合法 JSON,接著 `fix-check` 回 2(S2 的「不是合法 JSON」)。
2. `--template` 跑不跑〈先決條件〉沒寫:手冊第 5 步要求「修完寫修正紀錄,可用 `--template`」,此時修正還沒提交。照字面把先決條件(工作目錄不得有受版控改動、修正紀錄讀得到)套在 `--template` 上,它在最需要的時機回 2。S12 只測「印出含每條折入發現的骨架」。
3. 「各列一組待填」字面是每條發現一組,跟整份設計「每組是一個根因、收好幾條發現」相反;骨架一條一組後,使用者得手動合併才符合規則。
4. 修法方向:規格寫明提示全走標準錯誤、`--template` 只做讀審查帳那一步(不驗工作目錄、不讀紀錄、不掃殘骸)、骨架只放一個空組附所有待收發現清單在註解欄或標準錯誤。

## F9 `base` 不要求是祖先:rebase 後 `base..修正後` 夾帶上游全部改動,先紅變成「什麼都紅」
severity: minor
blocking: 否
引句:「不要求它是修正後提交的祖先(壓提交、改寫提交之後就不是了)」
1. 場景:長命分支做完修正、`git rebase origin/main`(專案規則推送前要 rebase)之後,對舊的 `base` 跑 `fix-check`(例如到上限、推送前那次)。`base..修正後` 是兩個點的差異,等於「修正+主線從舊 base 到現在新增的全部」。
2. 紅樹把這些非測試檔全換回舊 base:被上游新增、新測試依賴的函式與輔助模組一併消失,新測試會因為 ImportError 之類的原因紅,被判「先紅」過;真正「測試有守住這次的修正」沒有被證明(放錯)。幾百支檔改動時紅樹耗時也會膨脹(逐檔 `git show`)。
3. 設計刻意允許非祖先,所以只能補:紀錄 `base` 不是 `修正後` 的祖先時,輸出標「base 非祖先,先紅可能因上游改動而紅」,或要求用 `git merge-base` 交集算差異範圍。

## F10 `git status --porcelain -z` 的改名條目有兩個欄位:只看第一個路徑會漏掉舊路徑在 `docs/` 之外的改名
severity: minor
blocking: 否
引句:「工作目錄裡,`docs/` 與 `governance/` 以外沒有任何已受版控的改動(含已暫存;用 `git status --porcelain -z`)」
1. 實測:`git mv src.py docs/src.py` 後 `git status --porcelain -z` 是 `R  docs/src.py|src.py|`(新路徑在前、舊路徑在後,舊路徑單獨成一欄,沒有狀態碼)。
2. 只取第一個路徑判斷「在不在 `docs/` 底下」,這條改名被當成只動了 `docs/`,先決條件放行;實際上 `src.py` 已被刪除、尚未提交,驗的內容跟提交的不一樣——正是這條先決條件想擋的事。反過來把第二欄當成另一個條目又會解析錯位。
3. 修法方向:規格寫明 `R`/`C` 條目兩個路徑都要判。

## F11 `regression_set` 的「有沒有帶」靠欄位存在、不是靠內容:`none` 存空清單,慣用的 `or []` 讀法會把「判過沒有」跟「沒填」混成一樣
severity: minor
blocking: 否
引句:「存成排過序的 `regression_set` 清單(`none` 存空清單)」
file: `scripts/lumos:8121`(`len(carrier.get("folded_set") or [])` 這個本 repo 慣用的讀法,空清單與缺欄同值)
file: `scripts/lumos:8566`(`_ids`:`None`=沒給、`""`=明示空集合,兩者語意不同,寫側已分,讀側習慣沒分)
1. 設計在兩個讀端依賴「有沒有這個欄」:`fix-check` 的「載體席沒有 `regression_set` 欄 → 印一行提醒」,以及統計的「帶了的輪才算進分母,沒帶的印 ?」。
2. 用 `if not carrier.get("regression_set")` 這種寫法判「沒帶」,帶了 `none`(存 `[]`)的輪會被當成沒帶:`fix-check` 對已經判過的輪重複提醒,統計的分母少算「判過、這輪沒有」的輪,比例偏高。第一輪判定同理(`none` 在第一輪合法)。
3. 另外 `round` 型別在帳上可以是字串或整數(`scripts/lumos:7583` 的 `round: (str, int, type(None))`),設計說「`<輪>` 是字串、不解析數字」,但紀錄檔名 `<輪>-fix.json` 與 `loop next`、`fix-check` 對輪的比對在 `round: 1`(整數)的帳上會跟命令列的 `--round 1`(字串)對不上,沒有說統一轉字串。
4. 修法方向:規格寫明「用鍵是否存在判,不用真假值」,並在讀端統一 `str(round)`。

已讀無 finding 的節:〈範圍〉〈跟提案不同〉〈回退〉〈上線〉〈條款 S8–S10、S12 以外的 S 條〉(只在跟上面幾條打架時才報,已併入各 finding)。

最高等級:major,blocking 共 4 條
