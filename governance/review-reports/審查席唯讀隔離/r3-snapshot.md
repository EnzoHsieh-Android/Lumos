---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/agent-dag
lands_in:
  - Systems/lumos-guard
decisions:
  - content: 審查席隔離放在新外掛 lumos-guard 的 tool.call 攔截點,以派工詞的 LUMOS-SEAT 行認出席位,擋寫 repo、讀同輪別席報告、在 repo 裡跑改狀態的 git;不放進事件帳外掛。考慮過:①審查員改 claude -p 子程序帶唯讀工具清單(nested-agent-permission-scope 的方案 C;但審查員要跑 Bash 做重現實驗,收到只剩讀取就做不了,且一直沒實作);②擋在事件帳外掛裡(它的合約是只觀察、S9 測試釘著不准有拒絕);③只靠派工詞自律(就是現況)。代價:Bash 的一般寫檔讀檔擋不到;標記漏寫就沒有隔離。
    id: d1
    decided: 2026-10-06
    valid: false
    superseded_by: Projects/審查席唯讀隔離_計劃.md#d2
    ended: 2026-10-06
  - content: 審查席改用白名單:只准讀取類工具、Bash、網路查詢與派子代理;寫檔只准暫存區;git 只准唯讀白名單(改狀態只准 -C 暫存區);gh 擋;別席報告(席報告暫存處與卷證資料夾同輪席報告)擋讀;其他工具一律擋。防的是被誘導,不防有心繞,不構成自主迴圈解禁依據。考慮過:①黑名單擋寫 repo、讀別席報告、改狀態的 git(設計審 r1 四席實測多條繞法);②先查作業系統層沙盒能不能對單一子代理限寫入(要另花一輪調查,可能做不到)。Enzo 2026-10-06 裁白名單。代價:會誤擋席位部分合法的 git 實驗用法;Bash 仍是完整 shell。
    id: d2
    decided: 2026-10-06
    valid: false
    superseded_by: Projects/審查席唯讀隔離_計劃.md#d3
    ended: 2026-10-06
  - content: 審查席的 Bash 改成粗擋加事後查:不再逐詞解析 git 指令,只在指令字串出現 gh、hub、git 配 push 或 send-email、GitHub API 網址、席報告暫存處路徑時擋(寧可誤擋);審查席每次答完,外掛比對 repo 的檔案狀態、目前提交、分支、worktree 清單、repo 與使用者設定檔跟派工時是否一樣,不一樣就在回答後附警告並跳提示。寫檔只准這席自己的工作資料夾;讀保護只管席報告暫存處,卷證資料夾不擋。考慮過:①照逐詞解析補洞(設計審 r2 四席又抓到十多條同類漏擋誤擋,連兩輪同一類);②縮案、Bash 整類不管(改 repo 與開 PR 完全不擋)。Enzo 2026-10-06 裁粗擋加事後查。代價:在 repo 裡改檔或改狀態的 git 變成事後抓到而不是事前擋住;指令裡提到 push 之類的字也會被誤擋。
    id: d3
    decided: 2026-10-06
    valid: true
---
# 審查席唯讀隔離_計劃

白話:設計審、代碼審派出去的審查員是用 Agent 工具開的子代理,會繼承編排者的全部權限——被審的文件如果藏了惡意指令,審查員可以被誘導去改 repo、開 PR、改使用者設定;同一輪的審查員也看得到別席已經交回的報告,「各自獨立」只靠派工詞自律。這份計劃新增一支 Claude Code 外掛 `lumos-guard`:派工詞第一行是 `LUMOS-SEAT:` 的子代理,工具改用白名單、寫檔只准它自己的工作資料夾、不准碰席報告暫存處;Bash 只做粗擋(提到 `gh`、`git push`、GitHub API 這類對外動作就擋);在 repo 裡改東西改成「事後查」——審查員每次答完,外掛比對 repo 跟派工時一不一樣,不一樣就在它的回答後面附警告。防的是「被文件裡的指令誘導」,不防一個有心繞的審查員(Bash 仍是完整的 shell)。

PRIOR-ART: 最小解在 harness 的工具呼叫攔截點,不在提示詞。[[Systems/nested-agent-permission-scope]] 2026-06 設計過另一條路——把審查員改成 `claude -p --allowedTools "Read,Grep,Glob"` 子程序(工具清單在 harness 層收窄),但一直沒實作,而且審查員常要跑 Bash 做重現實驗(`claude -p`、`git -C <臨時目錄>`),工具清單收到只剩讀取就做不了。本案改用外掛的 `tool.call` 攔截:引擎每次要跑工具前都經過它,`e.agentId` 指出是哪個子代理,`{ deny }` 擋下(型別檔 'tool.call' 說明);子代理是誰派的、派工詞是什麼,從 `agent.spawn` 的輸入 `prompt`、`parentAgentId`、`cwd` 與結果 `agentId` 對起來;子代理答完時引擎發 `turn.complete`(帶 `agentId`,結果 `{ text }` 可附文字),外掛用 `$.process.run` 跑唯讀的 git 做比對(型別檔:引擎跑 git 時關掉 repo 掛鉤)。設計審第一輪證明「看指令文字列黑名單」漏得一塌糊塗,改成白名單(決策 d2);第二輪四席又在「逐詞解析 Bash 指令」這一類抓到十多條漏擋與誤擋(heredoc、`bash -lc`、包裝詞、`git -C` 暫存區照樣能 push、造 `.git` 檔導回真 repo),連兩輪同一類,所以換形狀:Bash 只粗擋對外動作,repo 內的改動改用外層比對(Enzo 2026-10-06 裁,決策 d3)。外掛寫法、市集、測試做法沿用 [[Systems/lumos事件帳]](核心邏輯可注入、`claude plugin test`、條款以測試標題開頭綁、本 repo 的 `.claude-plugin/marketplace.json`);標記解析照 `scripts/hooks/claude/dispatch-lens-hook.py` 讀 `LUMOS-IMPACT:` 的寫法(整行比對、去頭尾空白);擋下理由照本 repo 工具輸出的三段式(發生什麼、為什麼在意、要怎麼做獨立一行)。
RETIRE-IF: ①上線兩個月內 `lumos events` 看得到的審查席工具呼叫裡,這支外掛一次都沒擋過、事後查也沒報過變動,而且審查卷證也沒出現過席位改 repo、讀別席報告或用白名單外的工具——風險沒在真實發生,維護成本不值;②誤擋多過真擋(席位常被擋下合法的重現實驗);③Claude Code 的 Agent 工具開始支援逐次指定可用工具與寫入範圍(那時改用官方機制)。

## 名詞

- **審查席**:派工詞第一個非空行是合格 `LUMOS-SEAT: <迴圈編號>/<輪次>/<席名>` 的子代理,以及審查席再派出去的子代理(一律繼承)。
- **暫存根**:作業系統暫存目錄的真實路徑:macOS 是 `/private/tmp`、`/private/var/tmp`、`/private/var/folders/<兩層>/T`;Linux 是 `/tmp`、`/var/tmp`。比對一律帶路徑分隔字元(`/private/tmpX` 不算)。
- **席位工作資料夾**:`<任一暫存根>/lumos-seat-work/<迴圈編號>/<席名>/`。審查席唯一能用 `Write`、`Edit`、`NotebookEdit` 寫的地方;派工範本叫它把實驗、臨時 repo、草稿都放這裡。
- **席報告暫存處**:`<任一暫存根>/lumos-seat-staging/`(整個資料夾,不分迴圈)。編排者收到席報告時先存 `lumos-seat-staging/<迴圈編號>/`,全部交回才搬進卷證資料夾(把使用者記憶「報告存 repo 外」那條做法定成固定位置,讓外掛找得到要保護的地方)。卷證資料夾不保護:報告搬進去時同輪各席都已交回。

## 範圍

- **做**:
  1. 新外掛 `mods/claude/lumos-guard/`,加進同一份市集檔;安裝流程改成支援多支外掛。
  2. 認出審查席(見〈做法〉一)。
  3. 對審查席的每次工具呼叫套規則(見〈做法〉二);不合的回 `{ deny }`。
  4. 審查席答完時比對 repo(見〈做法〉三)。
  5. 修事件帳外掛:它的 `spawn` 事件用 `e.agentId` 記發起方,引擎給的欄位叫 `parentAgentId`(型別檔 `AgentSpawnInput`),子代理再派子代理時發起方被記成空的;改用 `parentAgentId` 並補測試。獨立成一個 fix 提交。
  6. 派工範本與編排者須知:`skills/lumos-design-loop/templates.md` 的 §1 審計員、§3 code-loop reviewer、§7.6 架構對齊、§7.8 資安四段的派工詞第一行加 `LUMOS-SEAT: <loop>/<rN>/<席名>`,並把「實驗用臨時目錄」改指席位工作資料夾;編排者須知寫明這行必須在第一行、席報告收到時存進 `lumos-seat-staging/<迴圈編號>/`。設計審與代碼審手冊「先到的席報告先存檔放著」那句指到席報告暫存處;使用者記憶「報告存 repo 外」那條改指這個位置。
- **不做**:
  - 逐詞解析 Bash 指令(決策 d3 否決;設計審 r1、r2 連兩輪在這一類抓到漏擋與誤擋)。Bash 只做〈做法〉二·4 的粗擋。
  - 事前擋 Bash 在 repo 裡改檔或跑改狀態的 git:改成〈做法〉三的事後查。
  - 擋審查席的網路外洩(`WebFetch` 網址、`curl` 帶內容送出):寫進誠實界線。
  - Codex 編排的審查席(Codex 沒有同等攔截點)。
  - 自主迴圈解禁 `--pr`:這份隔離只防被誘導,Bash 仍能做任何事,**不構成** [[Systems/nested-agent-permission-scope]] 決策 d4 的解禁依據。
  - 驗席位自報的模型:事件帳的 `spawn` 事件已記引擎實際解析出的模型;比對派工單另案。

落點:新開 `Systems/lumos-guard`(管外掛檔);市集檔的家仍是 [[Systems/lumos事件帳]]、安裝流程的家仍是 [[Systems/lumos-cli-lifecycle]],只在那兩篇補一句。

## 做法

### 一、認出審查席

- `agent.spawn` 進來時(還沒 `next(e)`):
  - 發起方是審查席(輸入的 `parentAgentId` 在對應表裡)→ 新子代理一律繼承發起方的標記,派工詞自己帶的標記不算數。
  - 否則看派工詞:先去掉開頭的 BOM,再跳過「去掉空白後為空」的行(空白含 `\r`、全形空白 U+3000),取第一行去頭尾空白。
    - 整行符合 `^LUMOS-SEAT:\s*(\S+)$`,值以 `/` 切成恰好三段,每段非空、不是 `.` 或 `..`、不含 `\`、空白與控制字元 → 是審查席。輪次不限格式(真實帳上有 `r3-dref`、`驗收` 這類寫法)。
    - 第一行不分大小寫以 `LUMOS-SEAT` 開頭(含全形冒號 `：`)卻不合上一點 → 回 `{ deny }` 擋下這次派工,理由說哪裡寫壞:編排者想隔離卻寫錯,靜默放行等於整席沒保護。
    - 其他 → 不是審查席(不擋)。只看第一行,所以派工詞內文貼進來的被審材料、範本範例裡的標記不會被誤認。
  - 是審查席時,把這次派工放進該會談的「啟動中」清單,再 `next(e)`;拿到結果的 `agentId` 就登記「子代理編號 → 迴圈、輪次、席名、工作目錄(輸入的 `cwd`,沒給就是會談 cwd)、repo 基準(見〈做法〉三)」;不論成功、被拒、丟錯,都在 `finally` 裡把它從「啟動中」拿掉。
- `tool.call` 遇到表裡查不到的子代理、而同一會談有「啟動中」的審查席派工時,最多等 5 秒讓它們回報完再查表;等不到就照查不到處理(不是審查席,放行),並 `$.ui.toast` 一行固定開頭 `lumos-guard 逾時放行:` 的提示。等的是整批,同時派很多席時非審查席的子代理可能多等,上限 5 秒。
- 會談結束(`session.end`)清掉那個會談的對應與「啟動中」清單。

### 二、審查席的工具規則

1. **工具白名單**:`Read`、`Grep`、`Glob`、`Bash`、`WebFetch`、`WebSearch`、`ToolSearch`、`TodoWrite`、`TaskOutput`、`TaskStop`、`Skill`、`Agent`(某些建置叫 `Task`,兩個名字都認),以及照第 2 點判過的 `Write`、`Edit`、`NotebookEdit`。其他一律擋,包括 `SendMessage`、`Monitor`、`Workflow`、`TaskCreate`、`EnterWorktree`、`PowerShell`、所有 `mcp__` 開頭的工具、外掛自己註冊的工具。工具名用字串比對(`Grep`、`Glob` 在某些建置不註冊,不影響)。
   - `Agent` 帶 `isolation`(任何值)→ 擋:`remote` 在雲端跑、本機攔截點看不到,`worktree` 會在真 repo 開分支。`subagent_type` 只准沒給、`general-purpose`、`Explore`、`Plan`:其他代理定義可能自帶 isolation,外掛在呼叫端看不到。
2. **寫檔**:讀的欄位是 `Write`、`Edit` 的 `file_path`、`NotebookEdit` 的 `notebook_path`;欄位不是字串、不是絕對路徑,或任何一段是空的、`.`、`..` → 擋。其餘取「最深一層已存在的上層」:`$.fs.stat(p, { resolve: true })` 拿不到 `realPath`(含懸空連結)→ 擋;拿得到就接上剩下的段,在 macOS 折疊大小寫、統一成 NFC 後比對:落在這席自己的席位工作資料夾裡 → 放行;其餘一律擋。
3. **席報告暫存處**:
   - `Read` 的 `file_path` 照第 2 點取真實路徑,落在席報告暫存處裡 → 擋。
   - `Grep`、`Glob` 的搜尋範圍 = `path`(相對路徑以這席的工作目錄補全;含 `..` 段 → 擋;沒給就是工作目錄),再接上 `glob`、`pattern` 第一個萬用字元之前的固定段(`pattern` 是絕對路徑時就用它);取真實路徑(同第 2 點的「最深一層已存在的上層」)後,範圍跟席報告暫存處有祖孫關係(範圍在暫存處裡,或暫存處在範圍裡,例如 `path=/private/tmp`)→ 擋。
4. **Bash 粗擋**:先把指令字串切成詞(以 `A-Z a-z 0-9 _ . -` 以外的字元為界,`/usr/bin/gh` 切出 `gh`),再判下面任一條成立就擋,不管它在引號、heredoc、`bash -lc`、子殼層或註解裡:
   - 有詞 `gh` 或 `hub`。
   - 有詞 `git`,同時有詞 `push` 或 `send-email`。
   - 字串含 `api.github.com` 或 `uploads.github.com`。
   - 字串含 `lumos-seat-staging`。
   - 指令超過 1MB,或判斷本身出錯 → 擋(這一項 fail-closed,是第 6 點的例外)。
   - 寧可誤擋:heredoc 或說明文字裡出現這些字也會被擋,理由文字教它換寫法(報告內容直接寫在回答裡,或用 `Write` 寫進席位工作資料夾)。其他指令照常,在 repo 裡改檔、`git commit` 不事前擋,交給〈做法〉三。
5. **擋下理由**:三段式,例「擋下:審查席只能寫自己的工作資料夾(/Users/x/repo/a.md 不在裡面)。\n為什麼在意:被審材料裡的指令不能讓審查員改到 repo 或你的設定。\n要做實驗請寫到:\n  /tmp/lumos-seat-work/<迴圈>/<席名>/」;派工、工具、寫檔、暫存處、Bash 各一種固定開頭字串。
6. 不擋的照原樣 `next(e)`,外掛不改工具呼叫的輸入與結果。外掛自己出錯時引擎會跳過它(放行),第 4 點的 Bash 判斷除外。

### 三、事後查 repo

- **基準**:登記審查席(〈做法〉一)時,在會談 cwd 跑 `git rev-parse --show-toplevel` 找 repo 根(不是 repo 就不做事後查,登記一筆「沒有 repo」);在 repo 根記下:
  - `git status --porcelain=v1 -z --untracked-files=all` 的輸出
  - `git rev-parse HEAD`、`git for-each-ref` 的輸出、`git worktree list --porcelain` 的輸出
  - `.git/config`、`.git/hooks/` 底下每個檔的大小與修改時間、使用者的 `~/.gitconfig`、`~/.claude/settings.json`、`~/.claude/CLAUDE.md` 的內容指紋(用 `$.fs` 讀)
  - 每支 git 都用 `$.process.run`、帶 `-c core.fsmonitor=false`、逾時 10 秒;任一支失敗 → 該席基準記成「拿不到」。
  - 繼承來的子代理不另記基準,只有直接被派的審查席記。
- **比對**:有基準的審查席在 `turn.complete` 時(子代理每答完一次)用同樣指令再拿一份,跟基準比:
  - 一樣 → 照原樣回傳。
  - 不一樣 → 在 `next(e)` 回來的 `text` 後面附一段固定開頭 `⚠ lumos-guard:這席審查期間 repo 有變動` 的警告,列出哪幾類變了(檔案狀態列出前 20 個路徑、目前提交、分支、worktree、設定檔),註明「不一定是這席做的(編排者或別的會談也可能動到)」;同時 `$.ui.toast` 同一句開頭。
  - 基準「拿不到」或這次比對失敗 → 附一行 `⚠ lumos-guard:事後查沒做成:<原因>`,不判有沒有變。
  - 比對完把基準換成這次的結果,同一席下一次答完只報新的變動。

### 四、安裝流程改成多外掛

- `scripts/lumos` 的 `_LEDGER_PLUGIN` 改成外掛清單 `_LUMOS_PLUGINS`(兩支);常數、訊息與函式名裡寫死「事件帳外掛」的改成通用說法(`_ledger_*` 改 `_lumos_plugin_*`,對應測試名跟著改)。
- 同步:市集照舊確保一次;已登記市集的既有使用者先跑一次 `claude plugin marketplace update lumos-toolchain`,非零只印警告、不中止;外掛清單逐支「使用者範圍沒裝就裝」,裝完以外掛列表確認真的在,不在就判那支 failed。各支的結果分開印,回傳值取最差的一支(failed > no-source > absent > ok)。
  - 實作前先在隔離的 Claude 設定資料夾實測資料夾型市集的 `marketplace update`(返回碼、不跑它時新外掛裝不裝得上),結果寫進驗證紀錄;實測證明不需要就拿掉這步。
- 移除:外掛清單逐支移除(各支獨立做);全部成功才移除市集,任一支失敗就保留市集,手動補做的指令列出失敗的那幾支加市集。
- 既有測試 `t_ledger_plugin_files_valid` 的「市集只列一個外掛」改成「市集列出的外掛恰好是清單那幾支」。

## 條款

外掛行為的條款綁在 `mods/claude/lumos-guard/hooks/guard.test.ts`,測試標題以條款編號開頭,用 `claude plugin test mods/claude/lumos-guard` 在本機跑(CI 沒有 Claude,同事件帳外掛的做法)。

- [S1] 當審查席呼叫 `Write`、`Edit`(`file_path`)或 `NotebookEdit`(`notebook_path`),只有落在自己席位工作資料夾的才放行;repo、家目錄、別席的工作資料夾、暫存根的其他位置、相對路徑、含 `.` 或 `..` 段的、最深已存在上層是懸空連結的、大小寫不同或經過連結指到外面的都應擋 [manual:claude plugin test mods/claude/lumos-guard 的 S1 測試全綠]
- [S2] 當審查席用 `Read` 讀席報告暫存處裡的檔,或 `Grep`、`Glob` 的搜尋範圍跟席報告暫存處有祖孫關係(含 `path=/private/tmp`、`pattern=/tmp/**/*.md`),應擋;卷證資料夾、repo 內搜尋、不碰暫存處的暫存根搜尋應照常 [manual:claude plugin test mods/claude/lumos-guard 的 S2 測試全綠]
- [S3] 當審查席的 `Bash` 指令字串有詞 `gh` 或 `hub`、同時有 `git` 與 `push` 或 `send-email`、含 GitHub API 網址或 `lumos-seat-staging`、超過 1MB,應擋,不論包在引號、heredoc、`bash -lc` 或子殼層裡;`git log`、`git grep -c x`、`git -C /tmp/lumos-seat-work/l/s commit`、`T=$(mktemp -d); git -C "$T" init`、`git clone <repo> /tmp/x` 應照常 [manual:claude plugin test mods/claude/lumos-guard 的 S3 測試全綠]
- [S4] 當審查席呼叫工具白名單以外的工具(`SendMessage`、`Monitor`、`Workflow`、`TaskCreate`、`EnterWorktree`、`mcp__` 開頭的),或呼叫 `Agent`/`Task` 帶 `isolation`、`subagent_type` 不在准用清單,應擋;`TodoWrite`、`TaskOutput`、`TaskStop`、`Skill` 應照常 [manual:claude plugin test mods/claude/lumos-guard 的 S4 測試全綠]
- [S5] 若派工詞第一個非空行不以 `LUMOS-SEAT` 開頭(含標記出現在內文、程式碼區塊、第二行以後),或呼叫者是主會談,外掛應完全不擋、不改輸入與結果;第一行以 `LUMOS-SEAT` 開頭卻不合格(少一段、`..`、全形冒號、大小寫不同)應擋下派工;中文迴圈編號與席名、`r3-dref` 這類輪次、開頭有 BOM 或全形空白行的應認得 [manual:claude plugin test mods/claude/lumos-guard 的 S5 測試全綠]
- [S6] 若審查席再派子代理(輸入帶 `parentAgentId`),新子代理應繼承發起方的標記、忽略自己派工詞裡的標記 [manual:claude plugin test mods/claude/lumos-guard 的 S6 測試全綠]
- [S7] 若審查席子代理在登記完成前就呼叫工具,外掛應先等同一會談啟動中的審查席派工(最多 5 秒)再判斷,逾時放行並跳 `lumos-guard 逾時放行:` 提示;派工被拒或丟錯時應從啟動中清單移除 [manual:claude plugin test mods/claude/lumos-guard 的 S7 測試全綠]
- [S8] 當外掛內部出錯,該次工具呼叫應照常放行,Bash 判斷出錯除外(應擋) [manual:claude plugin test mods/claude/lumos-guard 的 S8 測試全綠]
- [S9] 當 `lumos install` 與 `uninstall` 執行,外掛清單的兩支應各自裝上(裝完列表確認)與移除;`marketplace update` 非零只警告;市集只在全部外掛移除成功後才移除,任一支失敗保留市集並照實印出 [test:t_install_registers_guard_plugin]
- [S10] 當檢查 repo 內的外掛檔,`lumos-guard` 的描述檔與 hooks.json 應合法,市集列出的外掛恰好是清單那兩支,外掛原始碼不改寫任何工具呼叫的輸入或結果 [test:t_guard_plugin_files_valid]
- [S11] 當設計審與代碼審的派工範本更新,§1、§3、§7.6、§7.8 四段的派工詞第一行應是合格的 `LUMOS-SEAT:`、實驗目錄指到席位工作資料夾,且編排者須知寫明席報告暫存處 [test:t_seat_templates_carry_marker]
- [S12] 當事件帳外掛記 `spawn` 事件,發起方應取 `parentAgentId`,子代理派的孫代理那筆的 `agent` 欄應是那個子代理的編號 [manual:claude plugin test mods/claude/lumos-ledger 的 S12 測試全綠]
- [S13] 當審查席答完而 repo 的檔案狀態、目前提交、分支、worktree 清單或那幾個設定檔跟派工時不同,回答後面應附 `⚠ lumos-guard:這席審查期間 repo 有變動` 與變了哪幾類;沒變應原樣回傳;git 失敗應附「事後查沒做成」;同一席第二次答完只報新的變動 [manual:claude plugin test mods/claude/lumos-guard 的 S13 測試全綠]
- [S14] 當用 `claude -p` 載入兩支外掛、在暫存根以外的暫存 repo 派一個第一行帶 `LUMOS-SEAT:` 的子代理,叫它用 `Write` 改 repo 的檔、讀席報告暫存處的別席報告、`gh pr create`、用 Bash 在 repo 裡改一個檔,前三者應被擋,第四件應在編排者收到的回答裡看到事後查警告 [manual:暫存 repo 建在家目錄下的臨時資料夾、放一份假暫存處,claude -p 搭 --plugin-dir 兩支外掛跑一場,比對 git status、lumos events 與編排者收到的回答]

## 回退

- 把 `lumos-guard` 從外掛清單與市集檔拿掉,同步流程照 [[Projects/Lumos事件帳_計劃]] 回退節第 1 步的做法改成「確保它不在」,下次 install / update 就會移除;再刪外掛資料夾、測試與手冊那一行。外掛不寫任何檔,沒有資料要清。

## 實務隱患

- 已排除:金流:只擋本機工具呼叫,不碰付款
- 已排除:對外送出:外掛本身不呼叫網路;它跑的 git 只有〈做法〉三列的唯讀指令(`$.process.run`,掛鉤關閉、fsmonitor 關閉)
- 已排除:不可逆:只擋不改,擋錯的代價是審查員那次工具呼叫失敗、換做法;事後查只附文字;拿掉外掛即回到現狀
- 守衛面:審查席工具白名單、寫檔只准席位工作資料夾、席報告暫存處擋讀、Bash 粗擋對外動作;fail-open(Bash 判斷例外);S1 到 S8、S13 綁測試。
- 效能:每次工具呼叫多一次記憶體查表;審查席的呼叫才取真實路徑;事後查每席每次答完跑五支 git,`git status` 在大 repo 可能要幾秒,上限 10 秒。
- 併發:多個審查席同時跑,各自以子代理編號查表、各有自己的基準;「啟動中」清單以會談為鍵、只在派工期間存在。同時派很多席時,非審查席子代理的工具呼叫可能因等整批而慢,上限 5 秒。
- 誤擋:Bash 粗擋會擋下指令裡只是提到 `push`、`gh` 的合法寫法(heredoc、說明文字);理由文字教它換寫法。事後查會把編排者或別的會談在審查期間的改動也報出來,警告裡註明不一定是這席做的。
REVISIT:2026-11-06 用 lumos events 數這一個月審查席被擋的次數與種類、事後查報變動的次數、逾時放行的提示次數,誤擋多就調規則

## 誠實界線

- Bash 仍是完整的 shell:`cat` 讀 repo 外的檔、`python -c`、變數或編碼組出來的指令、先寫腳本再執行(腳本內容不掃)都擋不到;在 repo 裡改檔、改狀態的 git 只在事後被報出來,不會被擋或還原。這道隔離防的是「被文件裡的指令誘導,直接改 repo、開 PR、讀別席報告」,不防一個有心繞的審查員,也不夠當自主迴圈解禁 `--pr` 的依據。
- 事後查只看〈做法〉三列的那幾樣:repo 外的檔(暫存區裡的共用材料、別的專案)、`.git` 裡沒列的地方被改,都看不到。
- 事後查的警告附在子代理回答後面;引擎說非主迴圈的 `turn.complete` 文字「顯示在回答下方」,編排者收不收得到這段文字沒實測,S14 會驗;收不到時只剩提示。
REVISIT:2026-11-06 依 S14 實測結果改寫這一句;編排者收不到就把事後查結果改由事件帳記一筆、收貨時查
- 網路外洩不擋:審查席能把內容放進 `WebFetch` 網址或 `curl` 送出。`Bash` 的 `dangerouslyDisableSandbox` 對這份設計沒影響(不倚賴沙盒);日後改用作業系統沙盒時要一併擋。
- 標記靠派工詞第一行:編排者漏寫,那一席就沒有隔離(寫壞會被擋下派工,漏寫不會)。S11 只盯範本,盯不到編排者實際派工時有沒有照抄。
REVISIT:2026-11-06 用 lumos events 數這一個月派出的審查席裡,派工詞第一行帶 LUMOS-SEAT 的比例;低於九成就把「派工有沒有帶標記」接進收貨檢查
- 子代理在 Bash 裡 `cd` 之後的工作目錄外掛看不到;`Grep`、`Glob` 的相對路徑只以派工時的工作目錄補全。
- 外掛熱重載、行程重啟、`/clear`、`--resume` 都會清掉對應表,之前派出、還在背景跑的席位之後不受保護;fail-open 也一樣。
- 席報告暫存處是新的慣例:編排者沒照做(把報告存別處)時,別席報告不受保護。
- Codex 編排的審查席不受保護。

## 審計修正紀錄

- r1(2026-10-06,4 席:正確性、邊界、資安、架構對齊;外家席依 Enzo 指示不派):40 條/blocking 26/兩席獨立抓到 blocker:標記格式首字限英數,真實席名多數判不合格、隔離靜默全關;資安席實測 7 條繞法(gh 開 PR、--git-dir 抵消 -C、Monitor 與 Workflow 與 SendMessage 繞過、macOS 大小寫不分的路徑、別席報告審查中在 repo 外)。Enzo 裁改白名單、防被誘導(決策 d2 取代 d1)。卷證 `governance/review-reports/審查席唯讀隔離/`。
  - 折入:工具改白名單、寫檔只准暫存區(取真實路徑、折疊大小寫)、git 改唯讀白名單並整串斷詞、gh 擋、定席報告暫存處並保護它、讀別席報告只擋明確指向、標記只認第一行且中文可、子代理一律繼承、啟動中清單 try/finally 與 5 秒上限;不再需要 repo 範圍判定,pickMain 與漂移守衛整段拿掉;安裝流程多外掛細節寫齊;外掛行為條款綁 TS 測試標題;明寫這份隔離不構成自主迴圈解禁依據。
- r2(2026-10-06,4 席:正確性、邊界、資安、架構對齊;資安席首派被安全分類器中斷、改防禦面框架重派):32 條/blocking 19/三席 major:逐詞解析 Bash 這一類連兩輪漏擋與誤擋(heredoc、`bash -lc`、包裝詞、`git -C` 暫存區可 push、造 `.git` 檔導回真 repo、`-c`/`-o` 誤擋);暫存區太寬(repo 在暫存區時保護全關、共用材料可改);Agent 的 `isolation` 可派出不受攔截的代理;輪次格式太窄且寫壞時靜默放行。Enzo 裁 Bash 改粗擋加事後查(決策 d3 取代 d2)。卷證同上。
  - 折入:Bash 改粗擋(gh、hub、git push、send-email、GitHub API 網址、暫存處路徑、超長、判斷出錯即擋);新增事後查 repo(檔案狀態、提交、分支、worktree、設定檔指紋,附在回答後並跳提示);寫檔只准席位工作資料夾、欄位名分清、相對路徑與 `.`/`..` 段與懸空連結擋;席報告暫存處改整個資料夾、讀保護改祖孫關係、卷證資料夾不保護;暫存根列齊並帶分隔字元比對;Agent 擋 `isolation` 與未知代理類型;工具白名單加 `TodoWrite`、`TaskOutput`、`TaskStop`、`Skill`、`Task`;標記不限輪次格式、寫壞擋下派工、BOM 與全形空白;逾時放行跳提示;`marketplace update` 失敗只警告並排實測、裝完列表確認、移除失敗保留市集;條款 S13 改事後查、S14 為真機驗收(暫存 repo 放家目錄下)。
