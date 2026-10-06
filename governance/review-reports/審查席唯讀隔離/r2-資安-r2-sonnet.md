severity: major

### F1 `git -C <暫存區>` 放行所有非唯讀子指令,其中有些能寫到暫存區以外或打到遠端
severity: major
blocking: 是 — 白名單宣稱「改狀態的 git 只准暫存區」,但放行條件只看 -C 落點,不看子指令本身的寫入目標與遠端副作用
引句:「每個 `-C` 疊起來的結果照第 2 點判在暫存區」
file: `r2-snapshot.md:73`
file: `claude-code.d.ts:15401`
說明:第 73 行對「不在唯讀白名單的子指令」只檢查 -C 落點,不限子指令種類。以下幾種在 -C 為暫存區時全部放行,卻不在暫存區裡落地。
- `git -C /tmp/x push <url 或 origin>`、`fetch`、`remote add`:可把提交推到 GitHub 遠端。gh 與 hub 雖被擋,「用 git push 建遠端分支」這條開 PR 前置路徑沒擋。暫存 clone 的 origin 常常就是真 repo。
- `git -C /tmp config --global ...`、`--file <絕對路徑>`:寫使用者的 ~/.gitconfig,例如放 alias 或 core.hooksPath。這正是 r1 F10 的使用者設定逃逸,換成 git 子指令仍通。
- `git -C /tmp clone <src> <repo內絕對路徑>`、`worktree add <絕對路徑>`、`checkout-index --prefix=`、`archive -o`、`init <絕對路徑>`:目標路徑是參數,-C 管不到。
- 先用 Write 在暫存區造 `/tmp/x/.git` 檔,內容 `gitdir: <repo>/.git`,再 `git -C /tmp/x commit` 或 `reset --hard`。-C 判在暫存區,實際改的是真 repo。有 `--git-dir` 與 `GIT_DIR` 的擋法都不涵蓋 gitfile 或 `core.worktree`。
- -C 為相對路徑時,是照會談 cwd 還是子代理自己的 cwd 判,設計沒寫。子代理可有自己的 cwd(AgentSpawnInput.cwd、isolation:worktree)。
設計該補:改狀態子指令改列小白名單(init、add、commit、checkout、switch、reset、stash、branch、apply 等)。明禁 push、fetch、pull、remote、config、clone、worktree、archive、checkout-index、submodule。凡帶絕對路徑參數的子指令都要判落點。-C 目錄裡 `.git` 若是檔案,或 config 有 `core.worktree`,一律擋。

### F2 Agent 的 isolation 參數(以及 subagent_type 選到自帶 isolation 的代理定義)可派出不經本機 tool.call 攔截的代理
severity: major
blocking: 是 — 准用 `Agent` 時沒查參數,`isolation:"remote"` 的代理在雲端環境跑,本機的 `tool.call` 看不到它的工具呼叫,隔離整個失效
引句:「派出去的子代理繼承標記」
file: `r2-snapshot.md:68`
file: `claude-code.d.ts:15219`
file: `claude-code.d.ts:491`
說明:型別檔 Agent 輸入有 `isolation?: "worktree" | "remote"`(第 15219 行),說明寫「remote 在雲端環境跑」。第 491 行顯示代理定義也能自帶 isolation,所以 `subagent_type` 一樣能間接觸發。`agent.spawn` 的輸入沒有 isolation 欄位,在 spawn 端也看不到。
- remote:雲端代理的工具呼叫不經本機外掛。設計的「繼承標記」只對本機 tool.call 有效,remote 是未涵蓋的逃逸。
- worktree:代理換 cwd,F1 的相對 -C 與外掛用的「會談 cwd」會對不上。它也會在真 repo 的 .git 建立 worktree 與分支,屬於寫 repo。
- `mode`(第 15217 行)標明「Deprecated; ignored」,無風險。`model`、`name` 無風險,因為 SendMessage 已擋。
設計該補:二.1 加一條,審查席的 `Agent` 呼叫帶 `isolation`(任何值)就擋。並寫明「代理定義自帶 isolation 的類型」怎麼處理,例如只准 `general-purpose`、`Explore` 這類已知類型,或以 spawn 結果判。

### F3 Grep/Glob 的 path 或 pattern 指到「席報告暫存處的上層」時,保護規則沒說擋不擋
severity: major
blocking: 是 — S2 的保護只列「指到別席報告或暫存處資料夾本身」,上層目錄遞迴搜尋能撈到整個暫存處,而且正是審查進行中報告所在的位置
引句:「指到受保護的別席報告(或席報告暫存處這個資料夾本身)→ 擋」
file: `r2-snapshot.md:70`
file: `r2-snapshot.md:36`
說明:`Grep({path:"/private/tmp", pattern:"finding|F1"})`、`Grep({path:"<暫存區>/lumos-seat-staging"})`、`Glob({pattern:"/tmp/**/*r2-*.md"})`,指到的是暫存處的祖先,不是暫存處本身。「指到」有沒有涵蓋「範圍包含」,設計沒定義。同一段「不帶 path 的全 repo 搜尋不擋」的理由,是報告在暫存處而搜 repo 碰不到,對以暫存區或其上層為 path 的搜尋這個理由不成立。
另外 Read 在這裡自洽,Read 對資料夾會報錯。`Glob` 的 `pattern` 含 `**` 或萬用字元時,「指到」要判展開結果,還是判固定前綴,也沒寫。
設計該補:改成「搜尋範圍(path 與 glob 的固定前綴)與受保護路徑有祖孫關係,即擋」。並寫 Glob 的 pattern 為絕對路徑、含 `..` 時怎麼判。型別檔的內建工具輸入表沒有列 Grep、Glob,參數名取自設計文字,無法在型別檔驗證,見 F6。

### F4 「暫存區」定義過寬:放進了真 repo 的 worktree、共用材料、別迴圈的暫存處與引擎自己的目錄,也與 S13 測試矛盾
severity: major
blocking: 是 — 寫檔規則唯一放行條件就是「落在暫存區」,暫存區內任何位置都成為可寫目標,與「防被誘導改 repo 與共用材料」的目的與 S13 都不一致
引句:「落在暫存區、而且不在席報告暫存處 → 放行」
file: `r2-snapshot.md:69`
file: `r2-snapshot.md:34`
file: `r2-snapshot.md:101`
說明:
- repo 或 worktree 位在暫存區底下時:S13 要求用「暫存 repo」做實驗,並預期「改 repo 裡的檔被擋」。但依第 69 行,暫存 repo 本身在暫存區內,寫入會放行,與 S13 預期矛盾。同理 CI 暫存 checkout、`isolation:worktree` 若建在暫存區也是。
- 共用材料:派工範本 `skills/lumos-design-loop/templates.md:28` 的 Spec 工作副本在 `/tmp/<id>-rN.md`。第 36 行保護的只有報告,不含 snapshot、dispatch 這類共用材料。任一席能改後續席要審的 spec 副本,破壞「各自獨立」。
- 席報告暫存處是「單一迴圈編號」的目錄(第 35 行)。同機同時有別迴圈時,別迴圈的暫存處既不受寫入排除也不在讀保護內。上層 `lumos-seat-staging/` 本身也未排除寫入,它的子目錄建立與改名沒有規則。
- 暫存區含 `/private/tmp/claude-501/` 這類引擎目錄(內建 skills、別會談的 scratchpad)。寫入這些位置,等於改編排者後續載入的提示材料。
- 平台列表:macOS 列 `/private/tmp`、`/private/var/folders`,Linux 列 `/tmp`、`/var/tmp`。macOS 的 `/var/tmp` 真實路徑是 `/private/var/tmp`,不在列表,會被擋(失敗方向安全,但與 S1「暫存區」口徑不一致),請對齊。
設計該補:寫入白名單縮到專用子目錄(例如 `<暫存區>/lumos-seat-work/<迴圈>/<席名>/` 或明確的 `$CLAUDE_JOB_DIR/tmp`),不開整個暫存區。至少要再加兩條排除:`lumos-seat-staging/` 整個資料夾(含別迴圈與上層),以及落點在 git 工作樹(`git rev-parse --show-toplevel` 有結果)而且該 repo 是會談 repo 或其 worktree 的路徑。

### F5 git 全域選項只擋 `-c`,漏 `--config-env`;選項比對方式未寫,縮寫與黏寫可能漏
severity: minor
blocking: 否 — 本設計已承認 Bash 是完整 shell,執行任意指令可另用 `python -c`;這裡是黑名單內部不一致,補一個字即可
引句:「整句沒有 `--output`、`-o`、`--ext-diff`、`-c`、`--exec-path`」
file: `r2-snapshot.md:73`
說明:`git --config-env=core.fsmonitor=VAR status` 與 `-c` 等效,卻不在列表。選項比對沒寫是整詞比對還是前綴。`-ccore.fsmonitor=...`(黏寫)、`--outp=f` 之類 parse-options 允許的縮寫、`git grep -O<cmd>`(`--open-files-in-pager` 會執行指令)都可能漏過整詞比對。另外「前面帶 `GIT_` 變數」只看同一命令前綴;`export GIT_DIR=...; git ...` 分兩句時沒涵蓋(`env GIT_DIR=`、`VAR=` 在同句已涵蓋)。
設計該補:列出 `--config-env`;說明比對採「詞以該字串開頭」;唯讀白名單的子指令禁 `-O`、`--open-files-in-pager`;前面語句裡出現 `export GIT_*` 或 `GIT_*=` 賦值就一律不放行 git。

### F6 寫檔規則用 `file_path` 的口吻涵蓋三個工具,型別檔裡 NotebookEdit 的參數名是 `notebook_path`;Grep、Glob 不在型別檔
severity: minor
blocking: 否 — 取不到路徑時規則寫的是「擋」,失敗方向安全,風險是把合法暫存區寫入誤擋
引句:「`Write`、`Edit`、`NotebookEdit` 的目標路徑先以會談 cwd 補成絕對路徑」
file: `r2-snapshot.md:69`
file: `claude-code.d.ts:15926`
file: `claude-code.d.ts:15489`
說明:Write 與 Edit 是 `file_path`(第 15926、15489 行);NotebookEdit 是 `notebook_path`(型別檔 NotebookEdit 段,`edit_mode` 在第 15623 行附近)。三者都註明路徑是絕對路徑,所以「以 cwd 補成絕對」對這三個工具是多餘的,而 cwd 在子代理有自己的 cwd 時還可能補錯(見 F2 的 worktree)。Grep、Glob 在型別檔的 `BuiltinToolInputs` 裡沒有項目(設計自己也寫了「某些建置不註冊」),所以 `path`、`glob`、`pattern` 這幾個參數名無法驗,測試要用實際建置驗一遍,不要只信設計文字。
設計該補:條款註明每個工具讀哪個欄位(Write、Edit 用 `file_path`、NotebookEdit 用 `notebook_path`);Grep、Glob 的欄位名在 S2 測試裡以實機工具定義釘住。

### F7 WebFetch、WebSearch、Bash 的 dangerouslyDisableSandbox 的能力超出「讀取類」假設,誠實界線沒寫
severity: minor
blocking: 否 — 範圍外威脅(外洩),屬於同一個 Bash 完整 shell 已承認的類別,補寫進誠實界線即可
引句:「審查席只准 `Read`、`Grep`、`Glob`、`Bash`、`WebFetch`、`WebSearch`、`ToolSearch`、`Agent`」
file: `r2-snapshot.md:68`
file: `claude-code.d.ts:15896`
file: `claude-code.d.ts:15902`
file: `claude-code.d.ts:15411`
說明:
- WebFetch 的 `url`、WebSearch 的 `query` 與 `allowed_domains` 沒有任何收窄。被誘導的審查席能把 repo 內容、報告或祕密放進網址或搜尋字串送出,也能抓內網與本機位址。設計第 111 行「對外送出」那條只說外掛本身不呼叫網路,沒有說審查席的網路能力。
- `Bash.dangerouslyDisableSandbox`(第 15411 行)能叫引擎略過沙盒。目前設計不倚賴沙盒,所以不構成繞過,但若日後採用「先查沙盒能不能限單一子代理寫入」(決策 d2 考慮的方案 ②),這個參數會讓它失效,應在那時一併擋。`run_in_background` 與 `timeout` 不影響,因為檢查在 command 字串上。
- ToolSearch 只載入工具綱要,實際呼叫仍過 `tool.call`,mcp__ 被擋,無額外能力。
設計該補:誠實界線加一句「網路外洩未擋」,並註記 dangerouslyDisableSandbox 在採用沙盒方案時要擋。

## 前輪修復驗收

- **F1 gh 開 PR、gh api 遠端改檔**:部分涵蓋。二.4 擋 `gh`、`hub`,涵蓋 gh。「不做」承認 curl 與 wget 打 API,也列進誠實界線。但 `git -C <暫存區> push` 這條遠端寫入路徑仍通(見 F1)。
- **F2 `-C` 加 `--git-dir`/`--work-tree` 抵消與同族 git 路徑**:部分涵蓋。唯讀白名單加上 `--output`、`-c`、`--ext-diff`、`--git-dir`、`--work-tree`、`GIT_*` 變數,把 `--output`、alias、fsmonitor、symbolic-ref、update-index 等一整批改成預設擋,取代了舊的黑名單,主體已處理。剩下 `--config-env`、gitfile 轉向與 -C 目錄下的絕對路徑子指令(見 F1、F5)。
- **F3 Monitor 是第二個 shell 入口**:已涵蓋。二.1 工具白名單不含 Monitor,也明列擋 PowerShell 與所有 `mcp__`。
- **F4 Workflow 的代理沒有 agent.spawn 登記**:已涵蓋(入口面)。白名單擋 `Workflow`、`TaskCreate`、`SendMessage`,審查席自己開不了無登記的代理;`Agent` 派出的有 parentAgentId 與「一律繼承」。查不到編號就放行的 fail-open 仍在,但已無入口使用。殘留的是 Agent 的 `isolation:"remote"`(見 F2),那是新的、不經攔截的代理入口。
- **F5 SendMessage 繞過**:已涵蓋。`SendMessage` 在白名單外,二.1 明列。
- **F6 macOS 大小寫不分與路徑別名**:已涵蓋。二.2 改成取最深已存在上層的真實路徑、折疊大小寫、NFC,再比暫存區白名單。這同時涵蓋 r1 的 F10(寫使用者設定),Write、Edit、NotebookEdit 已無此洞。殘留僅 F4 的「暫存區過寬」。
- **F7 同輪別席報告在席位還在跑時不在被保護資料夾**:部分涵蓋。定義了席報告暫存處並保護它,方向正確,也在誠實界線承認「編排者沒照做就不受保護」。但保護只涵蓋「指到暫存處本身」,祖先目錄搜尋沒涵蓋(F3);Bash 的 cat 本就擋不到(已承認);暫存處目前依賴新慣例,實務上是否照做要靠 S11 與 REVISIT 追蹤。

## 規則一致性檢查(第 3 點)摘要

- 「席報告暫存處」在暫存區底下,寫檔規則明文「不在席報告暫存處」,兩處措辭一致,沒有直接矛盾。縫在三處:
  1. 暫存處只是單一迴圈的子目錄,上層與別迴圈沒有排除(F3、F4)。
  2. 讀保護與寫排除用的是「暫存處」同一個詞,但沒說這是「自己迴圈」的還是「任何迴圈」的。
  3. 「暫存區」的放行條件沒有排除 git 工作樹,與 S13 預期衝突(F4)。
- 「受保護的別席報告」第 1 項包含暫存處底下所有檔(不分輪次、不分席名,也含自己的),第 2 項才區分「這席自己的不受保護」。兩項對「自己的報告」的處理不一致:暫存處裡自己那份也被擋讀。這對審查席無害(它不會去讀自己的),僅提醒措辭。

總結:最嚴重 major,blocking 4 條
