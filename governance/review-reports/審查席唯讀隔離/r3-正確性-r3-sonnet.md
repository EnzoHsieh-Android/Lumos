severity: major

審稿立場:假設照 r3 字面實作外掛。重點驗〈做法〉二·4 的 Bash 粗擋與〈做法〉三的事後查,並驗收前輪修復。實測都放在 `/tmp/lumos-seat-work/審查席唯讀隔離/正確性-r3-sonnet/`,沒有改 repo。

### F1 基準在「登記」時才拿,而且拿基準比等待上限還慢,第一批工具呼叫會變成放行
severity: major
blocking: 是 — 大 repo 上審查席剛起跑的幾秒完全沒有隔離,又拿到被污染的基準
引句:「拿到結果的 `agentId` 就登記」
引句:「最多等 5 秒讓它們回報完再查表;等不到就照查不到處理(不是審查席,放行)」
- 〈做法〉一把 repo 基準列在登記欄位裡,〈做法〉三的基準是五支 git,每支上限 10 秒。登記完成要等基準拿完。
- 輸入:大 repo、`git status --untracked-files=all` 跑 8 秒。審查席一起跑就先呼叫 `Bash`:`gh pr create ...`。
- 預期:被擋。字面實作:`tool.call` 最多等 5 秒,登記還沒完成,走逾時放行,只跳一個 toast,那次 `gh` 照跑。
- 同一批登記的其他席也會被「等整批」拖到 5 秒。
- 基準晚拿還有第二個後果。`agent.spawn` 的 `next(e)` 回來時子代理已經在跑(型別檔:「resolve once the subagent started」)。基準是在它起跑之後才拿的,這段時間它做的改動會被吞進基準,事後查看不到。
- 建議:先登記(欄位先寫、基準欄位標「進行中」,守衛規則照常套),基準在背景補;基準必須在 `agent.spawn` 的 `next(e)` 之前拿,但那一步的時間要算進派工。至少寫明順序,並讓逾時放行只用於「登記中」而不是「基準中」。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:359-368`

### F2 `git status --porcelain` 看不到「已經是髒的檔」再被改,事後查漏報
severity: major
blocking: 是 — 事後查的本職(發現 repo 被動過)在髒工作區上直接失效
引句:「`git status --porcelain=v1 -z --untracked-files=all` 的輸出」
- 實測:臨時 repo 裡 `a` 已是 ` M a`,再 `echo b >> a`、再 `echo c >> a`,`git status --porcelain` 兩次輸出都是 ` M a`,一模一樣。
- 輸入:本 repo 開工時就是髒的(`M governance/nags-last-week.txt`、一堆 `??`)。審查席用 Bash `echo x >> governance/nags-last-week.txt`,或覆寫既有未追蹤檔。
- 預期:報變動。字面實作:基準與比對的輸出相同,不報。
- 同理 `git rev-parse HEAD`、`for-each-ref`、`worktree list` 也不含內容,只有「新增或刪除路徑、狀態碼變化、提交變化」會被看到。
- 另外 `git status` 預設不含被 `.gitignore` 的路徑,寫進被忽略的檔也看不到。
- 建議:在狀態輸出之外,對髒路徑與未追蹤路徑補內容指紋(`git diff HEAD --binary` 的雜湊加每個未追蹤檔的 `git hash-object`),或誠實界線明寫「只看路徑集合,不看內容」。
- 規格現況:誠實界線第二點只說「repo 外的檔、`.git` 裡沒列的地方」看不到,沒承認髒檔內容變化看不到。

### F3 在 linked worktree 裡 `.git` 是檔案,`.git/config` 與 `.git/hooks/` 讀不到
severity: major
blocking: 是 — 本專案的標準工作方式(全域規則要求另開 worktree)下,事後查整個壞掉或靜默放行
引句:「`.git/config`、`.git/hooks/` 底下每個檔的大小與修改時間」
- 實測:`/Users/enzo/harness/lumos-toolchain-seat-guard` 就是 linked worktree,`cat .git` 得到 `gitdir: /Users/enzo/harness/lumos-toolchain/.git/worktrees/lumos-toolchain-seat-guard`,`ls .git/config` 回 `Not a directory`。
- 輸入:在 worktree 裡派審查席。
- 預期:正確比對 repo 設定與 hooks。字面實作:`$.fs` 讀 `<repo根>/.git/config` 丟 ENOTDIR。規格只說「git 失敗 → 基準拿不到」,沒說 `$.fs` 失敗;若照 S8「外掛出錯放行」,結果是整個事後查沒做事、也沒警告。若算「拿不到」,每席每次答完都附「事後查沒做成」,變成噪音。
- 建議:用 `git rev-parse --git-common-dir` 與 `--git-dir` 取路徑,hooks 另看 `core.hooksPath`,`config.worktree` 也要列。
- 附帶:`.git` 在 worktree 下是檔案,它本身的內容(指向的 gitdir)也該進指紋。
file: `/Users/enzo/harness/lumos-toolchain-seat-guard/.git:1`

### F4 事後查跑的 `git status` 會改寫 index、搶 `index.lock`,不是唯讀
severity: major
blocking: 是 — 外掛自己可能讓編排者同時進行的 `git add`、`git commit` 失敗
引句:「每支 git 都用 `$.process.run`、帶 `-c core.fsmonitor=false`、逾時 10 秒」
- 實測:`git -c core.fsmonitor=false status --porcelain` 跑完後,`.git/index` 的 mtime 從 1791253564 變成 1791253565(它重寫了 index 去更新 stat 快取);改用 `git --no-optional-locks status` 就不動。
- 輸入:四席並行,各自答完時跑 `git status`;編排者正在 `git add` 或 `git commit`(收貨與記帳階段正是如此)。
- 預期:編排者的 git 照常。字面實作:`index.lock` 競爭,編排者看到 `fatal: Unable to create '.git/index.lock': File exists`。
- 規格〈實務隱患〉「已排除:對外送出」那條還寫「它跑的 git 只有〈做法〉三列的唯讀指令」,這是對 `status` 的錯誤斷言。
- 建議:每支 git 加 `--no-optional-locks`(或環境變數 `GIT_OPTIONAL_LOCKS=0`),S13 補測試:比對前後 `.git/index` mtime 不變。
- 還有一點:五支 git 若是串行,上限 50 秒才放行子代理的回答,會拖慢收貨;建議並行或收窄逾時。

### F5 基準的 repo 取自會談 cwd,派工時指定的 cwd 被登記了卻不用
severity: major
blocking: 是 — 審查席實際工作在別的 repo 或 worktree 時,事後查看錯地方
引句:「在會談 cwd 跑 `git rev-parse --show-toplevel` 找 repo 根」
- 輸入:會談 cwd 是 `/Users/enzo/harness/lumos-toolchain`,派工時 `cwd` 指到 `/Users/enzo/harness/lumos-toolchain-seat-guard`(本次審查就是這種配置)。
- 預期:比對審查席實際工作的 repo。字面實作:基準與比對都在主 repo,審查席在 worktree 的任何改動都看不到;反過來主 repo 被別的會談改動,卻報成「這席審查期間 repo 有變動」。
- 會談 cwd 不是 repo 時,更會判成「沒有 repo」而完全不做事後查,即使審查席派到 repo 裡。
- 規格〈做法〉一記了「工作目錄(輸入的 `cwd`,沒給就是會談 cwd)」,〈做法〉三卻沒用它。
- 建議:以登記的工作目錄為起點找 repo 根;會談 cwd 與工作目錄不同 repo 時兩邊都記。

### F6 Grep 的 `pattern` 是正規表示式不是路徑,被當成搜尋範圍而誤擋
severity: major
blocking: 是 — 在 repo 裡搜「/tmp」這種很常見的內容,會被擋
引句:「再接上 `glob`、`pattern` 第一個萬用字元之前的固定段(`pattern` 是絕對路徑時就用它)」
- 輸入:審查席 `Grep { pattern: "/tmp", path: "/Users/enzo/harness/lumos-toolchain-seat-guard" }`(找文件裡提到 /tmp 的地方,審這份設計時天天做)。
- 預期:放行(席報告暫存處不在 repo 範圍裡,也不是搜尋標的)。
- 字面實作:`pattern` 以 `/` 開頭 → 被當絕對路徑 → 搜尋範圍變成 `/tmp` → 真實路徑 `/private/tmp` → 是席報告暫存處的上層 → 擋。`pattern: "/private"`、`"/var/folders"`、`"/"` 同樣中。
- 該套「固定前綴」規則的是 `Glob` 的 `pattern`(它本來就是路徑樣式,S2 的例子 `pattern=/tmp/**/*.md` 也是 Glob)。Grep 的 `glob` 是檔名過濾,不是路徑。
- 建議:Grep 只看 `path`、Glob 才加 `pattern` 固定段;Grep 的 `glob` 若是絕對路徑樣式才另算。S2 補反例:`Grep pattern=/tmp path=<repo>` 應放行。

### F7 `Skill` 在白名單內,forked skill 的子迴圈沒有 `agent.spawn`,不在對應表,守衛放行
severity: major
blocking: 是 — 「審查席再派出去的子代理一律繼承」這條合約有個沒封住的口
引句:「遇到表裡查不到的子代理、而同一會談有」
引句:「`WebSearch`、`ToolSearch`、`TodoWrite`、`TaskOutput`、`TaskStop`、`Skill`、`Agent`」
- 型別檔明寫:有一類迴圈「with no `agent.spawn` (a forked skill)」,但仍列在 `$.agent.list()`。這類子迴圈的 `tool.call` 帶自己的 `agentId`,對應表查不到,照規格「查不到 → 不是審查席 → 放行」。
- 輸入:審查席 `Skill` 呼叫任何 `context: fork` 的技能(本機有 `code-review`、`simplify` 之類會再開代理的技能)→ 它的 Write、Bash 完全不受守衛管。
- 預期:繼承審查席的標記。
- 建議:查不到時用 `$.agent.list()` 的 `parentId` 往上追,祖先是審查席就繼承;或把 `Skill` 移出白名單、改成明確列允許的技能名。S6 補這個案例。
file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3083`

### F8 事後查警告能不能到編排者手上沒定,而偵測管道只有它
severity: minor
blocking: 否 — 設計自己承認、S14 會驗,屬排程與保證等級問題,不是字面實作出錯
引句:「編排者收不收得到這段文字沒實測,S14 會驗」
- 型別檔的範例用 `on("turn.complete", ($, e, next) => (got[e.agentId]?.(e.answer), next(e)))` 取答案,Agent 工具回給編排者的是 `e.answer`;hook 回的 `text` 只說「a text other than a main-loop answer's is shown beneath it」,不保證進編排者的上下文。
- 風險:S13 條款「回答後面應附 …」可能做出來只剩 toast;無人看顧的長迴圈看不到 toast,事後查就等於沒有。
- `turn.complete` 的語意補三點:每次迴圈跑完觸發一次,包含 `reason` 為 `aborted` 或 `error` 的(規格沒寫這幾種要不要比對);teammate 閒置後被叫醒會再觸發;`isAborted` 時警告可能不顯示。
- 建議:S14 列為提交前必過,而不是推到 REVISIT 2026-11-06。同時預先備好「改由事件帳記一筆」的路徑,別等實測失敗才設計。

### F9 事後查在多會談環境下會頻繁誤報,可用「這席有沒有呼叫過 Bash」去噪
severity: minor
blocking: 否 — 規格已註明「不一定是這席做的」,屬訊噪比問題
引句:「不一定是這席做的(編排者或別的會談也可能動到)」
- 全域規則寫明同一 repo 常有別的 Claude 會談在動;本 repo 的 `governance/` 底下有自動排程與別的會談在產檔。長時間的審查席答完時幾乎必有 diff,警告會被習慣性忽略。
- `~/.claude/settings.json` 與 `~/.claude/CLAUDE.md` 也會被 Claude Code 自己或別的會談改寫。
- 去噪法:本席沒呼叫過 `Bash`(且 `Write`、`Edit` 都被限制在工作資料夾)時,repo 不可能被這席改動,可直接略過比對或只提示一行。
- 建議:守衛順手記每席是否用過 `Bash`、是否呼叫過 `Agent`(孫代理可能有 Bash)。

### F10 〈實務隱患〉「已排除:不可逆」的斷言與 Bash 不事前擋的決策矛盾
severity: minor
blocking: 否 — 行為由決策 d3 明定,錯的是風險聲明;但會誤導後續審查
引句:「已排除:不可逆:只擋不改,擋錯的代價是審查員那次工具呼叫失敗、換做法」
- 粗擋不擋 `git clean -fd`、`git checkout -- .`、`rm`、`git stash -u`。這些對未追蹤、未提交的檔(本 repo 現在就有幾十個 `??`)是不可逆的;事後查只會列出前 20 個消失的路徑,救不回來。
- 事後查也沒有存內容,警告沒法提供還原。
- 建議:這條改成「未提交的工作區內容被 Bash 破壞時無法還原」,放進誠實界線並附回頭條件;或接受 `git stash create` 之類的低成本快照。

### F11 讀保護只擋字面 `lumos-seat-staging`,用 glob 與引擎自己的任務輸出檔可讀同輪別席結果
severity: minor
blocking: 否 — 屬誠實界線已寫的 Bash 繞法,但有非刻意的常見形狀
引句:「字串含 `lumos-seat-staging`」
- 輸入:`cat /tmp/lumos-seat-st*/*/r2-*.md`、`rg -n foo /private/tmp`、`find /tmp -name 'r2-*.md'`。字串都不含 `lumos-seat-staging`,放行;`Grep path=/private/tmp` 卻被擋,兩條路徑不一致。
- 席位工作資料夾彼此可讀:規格叫席位把「草稿」放在那裡,別席的草稿同樣讀得到。
- 背景席的輸出檔在 `/private/tmp/claude-501/<專案>/<會談>/tasks/`(我看到目錄存在但是空的,⚠ 沒能確認裡面是否放席輸出),不在 staging 下。
- 建議:誠實界線補一句「別席的工作資料夾與引擎任務輸出不受保護」,範本寫明草稿不要放工作資料夾。

### F12 Bash 粗擋誤擋頻率:`git` 配 `push` 在本 repo 的審查裡很常見
severity: minor
blocking: 否 — 設計明寫「寧可誤擋」,理由文字會教換寫法
引句:「有詞 `git`,同時有詞 `push` 或 `send-email`。」
- 輸入:`git grep -n push -- docs`、`git log --oneline | grep push`、`command -v gh`。審本專案時「pre-push 關卡」「`push`」出現在大量檔案,審查員查證時一定會打到。
- 預期:放行(只讀)。字面實作:擋。
- 建議:REVISIT 2026-11-06 的統計要把這一類單獨計數;理由文字給具體替代,例如「把關鍵字放進檔案再 `grep -f`」。

### 前輪修復驗收
- F1(git 唯讀子指令被 `-c`/`-o` 整句誤擋):已修。逐詞解析整套拿掉,S3 明列 `git grep -c x` 放行。
- F2(`-C` 值帶 `$` 就擋):已修。S3 列 `T=$(mktemp -d); git -C "$T" init` 放行,也不再解析 `-C`。
- F3(`git init <路徑>`、`git clone`、白名單缺子指令):已修。這些在粗擋下都放行,白名單子指令表不需要了。
- F4(heredoc 內文被當命令位置):已修,方式是改成整串判斷。heredoc 內文含 `gh` 或 `git`+`push` 會被擋,規格已明寫為誤擋並教換寫法(見本輪 F12)。
- F5(寫檔判定 `..` 與連結):已修。「任何一段是空的、`.`、`..` → 擋」「懸空連結 → 擋」「`notebook_path`」「帶分隔字元比對」四點都寫進規格並列入 S1。
- F6(Grep/Glob 的 glob、pattern 不是路徑):部分。取固定前綴與祖孫關係已補,但把 Grep 的 `pattern`(正規表示式)也當路徑,產生新的誤擋(本輪 F6)。
- F7(共用材料名單未定):已修。改成整個 staging 受保護、卷證資料夾不保護。殘留的前提風險(編排者實際把同輪席報告放在卷證資料夾而非 staging)規格已在誠實界線承認。
- F8(包裝詞表不全、`command -v gh` 誤擋):已修(以粗擋取代)。包裝詞漏擋全消;`command -v gh` 仍被擋,屬已接受的誤擋。
- F9(`marketplace update` 失敗處理):已修。「非零只警告」「移除任一支失敗保留市集」「實作前先實測」都寫明。
- F10(白名單漏輔助工具):已修。`TodoWrite`、`TaskOutput`、`TaskStop`、`Skill`、`Task` 都加入;`LSP`、`AskUserQuestion` 未列,仍屬可接受的誤擋。但 `Skill` 的加入帶來本輪 F7。
- F11(暫存區三個根、保護範圍):已修。暫存根列齊、整個 `lumos-seat-staging` 受保護、比對帶分隔字元。

總結:最嚴重 major,blocking 7 條
