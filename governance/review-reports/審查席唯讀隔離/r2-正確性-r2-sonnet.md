severity: major

審稿立場:假設照 r2 做出外掛,會在某個輸入下判錯。以下 F1~F5 是實測或可由實測推得的誤擋與漏擋。快照路徑簡寫為 r2-snapshot.md,全名 `/Users/enzo/harness/lumos-toolchain-seat-guard/governance/review-reports/審查席唯讀隔離/r2-snapshot.md`。

### F1 git 唯讀子指令被「整句不得有 -c / -o」誤擋
severity: major
blocking: 是 — 審查員最常用的唯讀指令(`git grep -c`、`git log | wc -c`、`git ls-files -o`)會被擋,誤擋會逼人關掉外掛
引句:「而且整句沒有 `--output`、`-o`、`--ext-diff`、`-c`、`--exec-path`、`--git-dir`、`--work-tree` → 放行」
- 我在臨時 repo 實測:`git grep -c hi` 與 `git ls-files -o` 都是合法唯讀,正常輸出。
- 這些短選項在唯讀子指令裡另有意思:`git grep -c`(計數)、`git grep -o`(只印比對)、`git ls-files -o`(列未追蹤檔)、`git diff -c`、`git log -c`、`git log -o`。
- 「整句」若指整串 Bash 字串,連管線後面別的指令都會誤擋:`git log --oneline | wc -c`、`| head -c`、`| rg -o`、`| sort -o`。
- 建議:`-c`、`-o` 只在 git 全域選項位置(子指令之前)判。子指令之後只擋 `--output`、`--output=`、`--ext-diff`。
- ⚠ 我試過 `git log --outp=`、`git show --ou=` 等縮寫,這版 git(2.39.2)都拒收,縮寫繞法我沒證到。
file: `r2-snapshot.md:73`

### F2 -C 值帶 `$` 就擋,`mktemp -d` 變數寫法全軍覆沒
severity: major
blocking: 是 — 審查員建臨時 repo 的標準寫法被擋
引句:「`-C` 的值帶 `$`、反引號、`~` 這類要展開的寫法 → 擋(靜態判不了)」
- 真實審查員幾乎都寫 `T=$(mktemp -d); git -C "$T" init; git -C "$T" commit ...`,斷詞後 `-C` 的值是字面 `$T`,必擋。
- 同樣中招的還有 `git -C $(mktemp -d) init`、`git -C ~/tmp/x`。
- 理由文字教人「改用 `-C 暫存區`」,但審查員能照做的只剩寫死的 `/tmp/固定名`。
- 建議:至少追蹤同一條指令內 `VAR=$(mktemp ...)` 或 `VAR=/tmp/...` 的賦值再判。否則在〈誤擋〉節承認它,並把「在寫死路徑下實驗」寫進範本。
file: `r2-snapshot.md:73`

### F3 `git init <路徑>`、`git clone`、`cd <暫存> && git commit` 全被擋,而 `-C` 對不存在的目錄不可用
severity: major
blocking: 是 — 白名單設計下,建立臨時 repo 的合法路徑只剩一條窄路
引句:「其餘子指令只在「有 `-C <路徑>`、每個 `-C` 疊起來的結果照第 2 點判在暫存區」
- 我實測:`git -C /tmp/不存在 init` 回 `fatal: cannot change to ... No such file or directory`。
- 要先 `mkdir`,再 `git -C`。
- `git init /tmp/x`(路徑當參數,實測可用)沒有 `-C`,被擋。
- `git clone <repo> /tmp/x`(重現實驗的標準起手式)被擋。
- `cd /tmp/x && git init && git commit` 也被擋,因為只認 `-C`,不認 cwd 在暫存區。
- 建議:非唯讀子指令的放行條件加兩條。一是 `init`、`clone` 的目的路徑參數判在暫存區。二是 Bash 的 cd 已在暫存區時也放行。
- 同時要補唯讀白名單漏掉的子指令。
  - 本地唯讀:`config --get`、`branch`(僅列出)、`tag -l`、`remote -v`、`stash list`、`reflog`、`diff-tree`、`diff-index`、`check-ignore`、`count-objects`、`fsck`、`show-branch`、`cherry`、`range-diff`、`worktree list`、`submodule status`、`verify-commit`。
  - 查遠端:`ls-remote`。
- `branch`、`tag`、`config`、`remote`、`stash` 同名子指令有寫入版,需要看後面的參數,不能整個子指令放進白名單。
file: `r2-snapshot.md:73`

### F4 heredoc 內文與多行字串中「換行之後」被當命令位置
severity: major
blocking: 是 — 席位寫臨時腳本、寫報告都是 heredoc
引句:「`$(`、反引號、換行之後,跳過 `VAR=值` 前綴與 `env`、`command`、`exec`、`xargs`、`nice`、`time`、`sudo` 這類包裝詞」
- 規格沒提 heredoc。若斷詞只做引號與跳脫、不認 `<<'EOF'`,heredoc 內文每一行行首都會被當命令。
- 例 1:`python3 - <<'EOF'` 裡寫 `git = 1`,命令位置詞是 `git`、子指令是 `=`,不在白名單又無 `-C`,整串被擋。
- 例 2:`cat > /tmp/x/note.md <<EOF` 裡寫一行 `gh 沒登入所以...`,或用 `gh = ...` 當變數名,同樣被擋。
- 例 3:行首是 `git commit 之後…` 的散文也會被擋。
- 建議:斷詞要認 heredoc(含 `<<-`、引號分界符),內文整段略過。S3 要加「heredoc 內文不誤擋」的測試。
- 反方向:`echo "$(gh pr create)"` 這種雙引號內的 `$(` 在 shell 裡會執行。規格只說「引號照 shell 規則」,沒說雙引號內 `$(`、反引號要遞迴,⚠ 判不準會不會漏。
file: `r2-snapshot.md:71`

### F5 寫檔判定:`..` 與連結的處理順序有洞(漏擋)
severity: major
blocking: 是 — 該擋的寫 repo 擋不到,這是 S1 的核心
引句:「取「最深一層已存在的上層」的真實路徑(`$.fs.stat(p, { resolve: true })` 的 `realPath`)再接上剩下的段」
- 剩下的段若含 `..`,接在真實路徑後沒有折疊就拿去比對。
- 實測 `python3 os.path.realpath('/tmp/nonexist/../../Users')` 得 `/private/Users`,而作業系統實際會失敗或跳出。
- 攻擊面:`Write /tmp/nonexist/../../Users/enzo/repo/a.md`。
  - 最深已存在上層是 `/tmp`,realPath 為 `/private/tmp`。
  - 接上剩段後字串前綴是 `/private/tmp`,判成暫存區放行。
  - 檔案工具再把 `..` 折掉,實際寫到 repo。
- 反向:先用字串折疊 `..` 再取真實路徑也不對。實測 `$D/ln/L/../x`,其中 `L -> /Users`,作業系統解成 `/x`,字串折疊成 `$D/ln/x`。在暫存區內建一條指向 repo 的連結(Bash 的 `ln -s` 沒被擋)再接 `/..`,詞法判定會判成暫存區。
- 建議:凡剩餘段含 `..` 或空段、`.`,一律擋(或要求整條路徑能 stat 到)。
- 規格還需補三點:
  - 前綴比對必須帶分隔符,避免 `/private/tmpX` 誤判。
  - 「最深已存在上層」遇到懸空連結(stat 成功、`isLink` 為真、realPath 缺)要明寫「擋」。型別檔註明懸空連結 realPath 缺,若實作寫成「stat 不到 realPath 就往上一層」,寫 `/tmp/x/link.md`(指向 repo 尚不存在的檔)會放行。
  - NotebookEdit 的路徑欄位叫 `notebook_path`。⚠ 若實作只讀 `file_path`,拿到 undefined 會丟錯,而 S8 規定出錯放行,就等於 NotebookEdit 全放行。
file: `r2-snapshot.md:69`

### F6 讀保護:Grep 的 glob、Glob 的 pattern 不是路徑,取不到真實路徑時怎麼判沒定義
severity: major
blocking: 是 — 兩種讀法都會判錯:全擋或漏擋
引句:「`Read` 的目標、`Grep` 的 `path` 與 `glob`、`Glob` 的 `path` 與 `pattern`,照上一點同樣取真實路徑與折疊後」
- 「上一點」寫著「真實路徑取不到 → 擋」。
- `glob: "**/*.md"`、`pattern: "src/**/*.ts"` 都含萬用字元,`stat` 不到。照字面,每個帶 glob 的 Grep、每個 Glob 都被擋,審查員搜尋功能整個壞掉。
- 若改成「取不到就放行」,又漏:`Grep path=/private/tmp`(暫存區上層、遞迴搜尋)會把席報告暫存處的同輪別席報告全搜出來。受保護清單只擋「指到」暫存處,沒擋「含有」。
- 建議:glob 與 pattern 只取字面前綴目錄(第一個萬用字元之前)去比對。再明寫上層目錄遞迴搜尋的處理:擋掉會涵蓋暫存處的 `path`,或承認漏。
file: `r2-snapshot.md:70`

### F7 同輪「共用材料」的名單沒定,真實卷證的共用檔會被當席報告擋掉
severity: major
blocking: 是 — 審查員讀不到自己的審查材料
引句:「席報告是 `<輪次>-<席名>.md`(以及 `.stdout`)、收貨紀錄是 `<輪次>-intake.md`;同輪的 snapshot、dispatch、delta 等共用材料不算」
- 單看檔名形狀 `rN-<任意>.md`,`r2-snapshot.md` 也符合,審查員被指定要讀的快照會被擋。規格沒說用什麼區分。
- 我列了真實卷證,同輪還有很多既非席報告、也非 snapshot/dispatch/delta 的檔:
  - `preflight.md`、`mirror.md`、`common.md`、`dispatch-common.md`
  - `snapshot-s1.md`、`snapshot.patch`、`delta.patch`
  - `邊界-prompt.txt`、`codex-prompt.txt`、`codex-raw.txt`
  - `lens.txt`、`sha256.txt`、`manifest.json`、`fix.json`、`reviewer.md`、`report.md`
- 舊迴圈還有不帶輪次前綴的席報告:`s1.md`、`通才.md`、`arch.md`、`ext.md` 等。
- 白名單式的「共用材料」定義漏了就誤擋,黑名單式的「席報告」定義漏了就漏擋。
- 建議:改成以派工單(`rN-dispatch.json` 的 seats 與席名)精確列出受保護檔名,或約定席報告必進暫存處、卷證資料夾一律不擋(因為搬進來時已全部交回)。
- 補一點:守衛不知道 repo 根,卷證資料夾只能靠路徑尾段比對。規格要寫明是比對 `…/governance/review-reports/<迴圈編號>/`,並說明相對路徑怎麼判。
file: `r2-snapshot.md:36`

### F8 命令位置的包裝詞表不全,選項處理未定;同時 `command -v gh` 這類查詢會被誤擋
severity: major
blocking: 是 — 擋 `gh` 的 S3 有現成繞法,也有誤擋
引句:「跳過 `VAR=值` 前綴與 `env`、`command`、`exec`、`xargs`、`nice`、`time`、`sudo` 這類包裝詞」
- 漏擋:`timeout 30 gh pr create`、`nohup`、`setsid`、`stdbuf`、`watch`、`find -exec gh`、`bash -lc '…'`、`zsh -ic '…'`。
- 規格只列 `sh -c`、`bash -c`、`zsh -c`,而常見的 `-lc` 是合併旗標,不等於 `-c`。這些是被誘導的模型很自然寫出的形狀,不是有心繞。
- 規格沒說包裝詞自帶選項怎麼跳:`env -i FOO=1 gh`、`nice -n 10 gh`、`sudo -u x gh`、`xargs -I{} gh`。
- 誤擋:`command -v gh`、`type gh`、`which gh`。`command` 被當包裝詞跳過後,下一個詞 `-v` 不是 gh,但若實作「跳過旗標」就會落到 `gh`。審查員用它確認環境,被擋會困惑。
- 建議:包裝詞要列明各自的選項規則。`command -v`、`-V`、`type`、`which` 不當命令位置。補 `timeout`、`nohup`、`setsid`、`stdbuf`,並處理 `-lc` 這類合併旗標。
file: `r2-snapshot.md:71`

### F9 安裝流程:`marketplace update` 的失敗處理沒定,是未查證的假設
severity: major
blocking: 是 — 既有使用者升級時可能整個安裝失敗,或靜默裝不到新外掛
引句:「已登記市集的既有使用者先跑一次 `claude plugin marketplace update lumos-toolchain` 再裝(資料夾型市集是否需要這步沒驗證,跑了無害)」
- 「跑了無害」沒有證據。現有 `_claude_do` 對非零返回碼直接丟 RuntimeError(`scripts/lumos:21933` 附近),若資料夾型市集對 update 回非零,`_sync_claude_plugin` 會整個判 failed,連事件帳也被連累。
- 反方向:若 update 是空操作而 install 又找不到新外掛(市集索引快取舊),guard 裝不上,卻因「事件帳已裝」而看不出。
- 規格也沒說 update 失敗要不要吞掉繼續。
- 建議:先實測資料夾型市集的 update 行為再寫進規格,並明定 update 失敗的處置。
- 次要:移除流程寫「全部處理完才移除市集一次」,但沒說有一支外掛移除失敗時市集還移不移。現行程式是各步獨立都做,手動補做清單的組法也需寫明。「failed > no-source > absent > ok」取最差是合理的。
file: `r2-snapshot.md:81`

### F10 工具白名單漏掉審查員做重現實驗會用到的輔助工具
severity: minor
blocking: 否 — 擋了只是那次呼叫失敗、換做法,不會讓審查無法進行
引句:「其他一律擋,包括 `SendMessage`、`Monitor`、`Workflow`、`TaskCreate`、`EnterWorktree`、`PowerShell`、所有 `mcp__` 開頭的工具、外掛自己註冊的工具」
- 白名單沒有的:`TodoWrite`、`TaskStop`、`TaskOutput`(或 `BashOutput`、`KillShell`)、`Skill`、`AskUserQuestion`、`LSP`。
- 審查員用 `run_in_background` 跑 `claude -p` 之後要等結果或停掉它,可能就用到這幾個。`Monitor` 更被明列擋,但 Bash 工具說明正是叫人用它等背景作業。
- ⚠ 型別檔的 Agent 工具在某些建置叫 `Task`;只列 `Agent` 的話,那些建置的審查席派不了子代理。
- 這些都不影響「防被誘導」的目標。建議把「安全的內部輔助工具」(`TodoWrite`、`TaskStop`、`TaskOutput`、`Skill`)加入白名單,或在 REVISIT 的誤擋統計裡特別數它們。
file: `r2-snapshot.md:68`

### F11 席報告暫存處的「暫存區」有三個根,保護範圍與編排者實際路徑可能對不上
severity: minor
blocking: 否 — 只削弱保護,不致誤擋
引句:「**席報告暫存處**:`<暫存區>/lumos-seat-staging/<迴圈編號>/`」
- macOS 暫存區是 `/private/tmp` 與 `/private/var/folders` 兩個根(Linux 也有兩個),`$TMPDIR` 指到 `/var/folders/…/T`、Claude 的 scratchpad 在 `/private/tmp/claude-501/…`。
- 規格沒說守衛要保護所有根下的 `lumos-seat-staging`,還是只保護某一個。
- 同樣沒說是只保護「這席迴圈編號」那一個子資料夾,還是整個 `lumos-seat-staging`。
- 並行的另一個迴圈(不同編號)若不受保護,兩個同時進行的審查迴圈之間可以互讀。
- 「暫存區」含整個 `/private/var/folders`,裡面有各 app 的快取目錄,席位的 Write 在那裡不受限。對「防被誘導」影響不大,但與「只准暫存區」的字面不符,可能還是要收窄成 `…/T`。
file: `r2-snapshot.md:35`

總結:最嚴重 major,blocking 9 條
