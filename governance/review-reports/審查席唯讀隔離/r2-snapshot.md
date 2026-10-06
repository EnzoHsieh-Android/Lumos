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
    valid: true
---
# 審查席唯讀隔離_計劃

白話:設計審、代碼審派出去的審查員是用 Agent 工具開的子代理,會繼承編排者的全部權限——被審的文件如果藏了惡意指令,審查員可以被誘導去改 repo、開 PR、改使用者設定;同一輪的審查員也看得到別席已經交回的報告,「各自獨立」只靠派工詞自律。這份計劃新增一支 Claude Code 外掛 `lumos-guard`:派工詞第一行是 `LUMOS-SEAT:` 的子代理,改用白名單——只准用讀取類工具與 Bash、只准寫暫存區、git 只准唯讀指令(改狀態的只准對暫存區)、不准用 `gh`、不准讀別席報告;白名單外的一律擋。防的是「被文件裡的指令誘導」,不防一個有心繞的審查員(Bash 仍是完整的 shell)。

PRIOR-ART: 最小解在 harness 的工具呼叫攔截點,不在提示詞。[[Systems/nested-agent-permission-scope]] 2026-06 設計過另一條路——把審查員改成 `claude -p --allowedTools "Read,Grep,Glob"` 子程序(工具清單在 harness 層收窄),但一直沒實作,而且審查員常要跑 Bash 做重現實驗(`claude -p`、`git -C <臨時目錄>`),工具清單收到只剩讀取就做不了。本案改用外掛的 `tool.call` 攔截:引擎每次要跑工具前都經過它,`e.agentId` 指出是哪個子代理,`{ deny }` 擋下(型別檔 'tool.call' 說明);子代理是誰派的、派工詞是什麼,從 `agent.spawn` 的輸入 `prompt`、`parentAgentId` 與結果 `agentId` 對起來。設計審第一輪四席證明「看指令文字列黑名單」漏得一塌糊塗(大小寫不分的路徑、`--git-dir`、`gh`、其他能跑 shell 或代做的工具),所以改成白名單(Enzo 2026-10-06 裁,決策 d2)。外掛寫法、市集、測試做法沿用 [[Systems/lumos事件帳]](核心邏輯可注入、`claude plugin test`、條款以測試標題開頭綁、本 repo 的 `.claude-plugin/marketplace.json`);標記解析照 `scripts/hooks/claude/dispatch-lens-hook.py` 讀 `LUMOS-IMPACT:` 的寫法(整行比對、去頭尾空白);擋下理由照本 repo 工具輸出的三段式(發生什麼、為什麼在意、要怎麼做獨立一行)。
RETIRE-IF: ①上線兩個月內 `lumos events` 看得到的審查席工具呼叫裡,這支外掛一次都沒擋過,而且審查卷證也沒出現過席位改 repo、讀別席報告或用白名單外的工具——風險沒在真實發生,維護成本不值;②誤擋多過真擋(席位常被擋下合法的重現實驗);③Claude Code 的 Agent 工具開始支援逐次指定可用工具與寫入範圍(那時改用官方機制)。

## 名詞

- **審查席**:派工詞第一個非空行是 `LUMOS-SEAT: <迴圈編號>/<輪次>/<席名>` 的子代理,以及審查席再派出去的子代理(一律繼承)。
- **暫存區**:作業系統的暫存目錄——取真實路徑後是 `/private/tmp`、`/private/var/folders`(macOS)或 `/tmp`、`/var/tmp`(Linux)底下;**不含**下面的「席報告暫存處」。
- **席報告暫存處**:`<暫存區>/lumos-seat-staging/<迴圈編號>/`。編排者收到席報告時先存這裡,全部交回才搬進卷證資料夾(把使用者記憶「報告存 repo 外」那條做法定成固定位置,讓外掛找得到要保護的地方)。
- **受保護的別席報告**:①席報告暫存處底下的所有檔;②卷證資料夾 `governance/review-reports/<這席的迴圈編號>/` 裡,同一輪(檔名以 `<輪次>-` 開頭)的席報告與收貨紀錄——席報告是 `<輪次>-<席名>.md`(以及 `.stdout`)、收貨紀錄是 `<輪次>-intake.md`;同輪的 snapshot、dispatch、delta 等共用材料不算。這席自己的報告不受保護(它本來就沒有)。

## 範圍

- **做**:
  1. 新外掛 `mods/claude/lumos-guard/`,加進同一份市集檔;安裝流程改成支援多支外掛。
  2. 認出審查席(見〈做法〉一)。
  3. 對審查席的每次工具呼叫套白名單(見〈做法〉二);不在白名單的回 `{ deny }`。
  4. 修事件帳外掛:它的 `spawn` 事件用 `e.agentId` 記發起方,引擎給的欄位叫 `parentAgentId`(型別檔 `AgentSpawnInput`),子代理再派子代理時發起方被記成空的;改用 `parentAgentId` 並補測試。獨立成一個 fix 提交。
  5. 派工範本與編排者須知:`skills/lumos-design-loop/templates.md` 的 §1 審計員、§3 code-loop reviewer、§7.6 架構對齊、§7.8 資安四段的派工詞第一行加 `LUMOS-SEAT: <loop>/<rN>/<席名>`;編排者須知寫明這行必須在第一行、席報告收到時存進席報告暫存處。設計審與代碼審手冊「先到的席報告先存檔放著」那句指到席報告暫存處。
- **不做**:
  - 擋 Bash 的一般讀寫(`cat`、`>`、`tee`、`sed -i`、`python -c` 寫檔、變數或 `eval` 組出來的指令):Bash 仍是完整的 shell,防不了有心繞;靠派工詞與代碼審。
  - 擋 `curl`、`wget` 呼叫 GitHub API:網址可以拼出來,文字比對擋不乾淨;寫進誠實界線。
  - Codex 編排的審查席(Codex 沒有同等攔截點)。
  - 自主迴圈解禁 `--pr`:這份隔離只防被誘導,Bash 仍能做任何事,**不構成** [[Systems/nested-agent-permission-scope]] 決策 d4 的解禁依據。
  - 驗席位自報的模型:事件帳的 `spawn` 事件已記引擎實際解析出的模型;比對派工單另案。

落點:新開 `Systems/lumos-guard`(管外掛檔);市集檔的家仍是 [[Systems/lumos事件帳]]、安裝流程的家仍是 [[Systems/lumos-cli-lifecycle]],只在那兩篇補一句。

## 做法

### 一、認出審查席

- `agent.spawn` 進來時(還沒 `next(e)`):
  - 發起方是審查席(輸入的 `parentAgentId` 在對應表裡)→ 新子代理一律繼承發起方的標記,派工詞自己帶的標記不算數。
  - 否則看派工詞:去掉開頭空行後的第一行,去頭尾空白(含 `\r`)後整行要符合 `^LUMOS-SEAT:\s*(\S+)$`;值以 `/` 切成恰好三段,每段非空、不含空白與控制字元;第二段(輪次)要符合 `^r[0-9]+[a-z]?$`(例 `r2`、`r3b`)。不合就不是審查席(不擋)。只看第一行,所以派工詞內文貼進來的被審材料、範本範例裡的標記不會被誤認。
  - 是審查席時,把這次派工放進該會談的「啟動中」清單,再 `next(e)`;拿到結果的 `agentId` 就登記「子代理編號 → 迴圈、輪次、席名」;不論成功、被拒、丟錯,都在 `finally` 裡把它從「啟動中」拿掉。
- `tool.call` 遇到表裡查不到的子代理、而同一會談有「啟動中」的審查席派工時,最多等 5 秒讓它們回報完再查表;等不到就照查不到處理(不是審查席,放行)。引擎在子代理啟動後才回報派工結果,子代理的工具呼叫在啟動之後,等這一下正常情況不會互卡;上限 5 秒是防萬一。
- 會談結束(`session.end`)清掉那個會談的對應與「啟動中」清單。

### 二、白名單

1. **工具**:審查席只准 `Read`、`Grep`、`Glob`、`Bash`、`WebFetch`、`WebSearch`、`ToolSearch`、`Agent`(派出去的子代理繼承標記),以及目標在暫存區的 `Write`、`Edit`、`NotebookEdit`。其他一律擋,包括 `SendMessage`、`Monitor`、`Workflow`、`TaskCreate`、`EnterWorktree`、`PowerShell`、所有 `mcp__` 開頭的工具、外掛自己註冊的工具。工具名用字串比對(`Grep`、`Glob` 在某些建置不註冊,不影響)。
2. **寫檔**:`Write`、`Edit`、`NotebookEdit` 的目標路徑先以會談 cwd 補成絕對路徑,取「最深一層已存在的上層」的真實路徑(`$.fs.stat(p, { resolve: true })` 的 `realPath`)再接上剩下的段,在 macOS 折疊大小寫、統一成 NFC 後比對:落在暫存區、而且不在席報告暫存處 → 放行;其餘(repo、家目錄、使用者設定、其他專案)一律擋。真實路徑取不到 → 擋。
3. **讀別席報告**:`Read` 的目標、`Grep` 的 `path` 與 `glob`、`Glob` 的 `path` 與 `pattern`,照上一點同樣取真實路徑與折疊後,指到受保護的別席報告(或席報告暫存處這個資料夾本身)→ 擋。不帶 `path` 的全 repo 搜尋不擋:審查進行中別席報告在 repo 外的暫存處,搜 repo 碰不到。
4. **Bash**:把整串指令做 shell 斷詞(引號、跳脫照 shell 規則),`sh -c`、`bash -c`、`zsh -c` 的字串參數遞迴斷詞;在所有詞裡找命令位置的詞(行首、`;`、`&&`、`||`、`|`、`&`、`(`、`{`、`$(`、反引號、換行之後,跳過 `VAR=值` 前綴與 `env`、`command`、`exec`、`xargs`、`nice`、`time`、`sudo` 這類包裝詞):
   - 詞是 `gh`、`hub`(或以 `/gh`、`/hub` 結尾)→ 擋。
   - 詞是 `git`(或以 `/git` 結尾):跳過全域選項找子指令;子指令在唯讀白名單(`log`、`show`、`diff`、`status`、`rev-parse`、`ls-files`、`ls-tree`、`cat-file`、`blame`、`grep`、`shortlog`、`describe`、`merge-base`、`rev-list`、`name-rev`、`for-each-ref`、`show-ref`、`help`、`version`)而且整句沒有 `--output`、`-o`、`--ext-diff`、`-c`、`--exec-path`、`--git-dir`、`--work-tree` → 放行;其餘子指令只在「有 `-C <路徑>`、每個 `-C` 疊起來的結果照第 2 點判在暫存區、沒有 `--git-dir`、`--work-tree`、`-c`,而且命令前沒有 `GIT_DIR=`、`GIT_WORK_TREE=` 等 `GIT_` 開頭的變數」時放行;`-C` 的值帶 `$`、反引號、`~` 這類要展開的寫法 → 擋(靜態判不了)。其餘情況都擋。
   - 其他指令照常。
5. **擋下理由**:三段式,例「擋下:審查席不准寫暫存區以外的檔(/Users/x/repo/a.md)。\n為什麼在意:被審材料裡的指令不能讓審查員改到 repo 或你的設定。\n要做實驗請寫到暫存區,例如:\n  /tmp/<你的臨時目錄>/」;三類(工具、寫檔、讀別席報告)與 Bash 各一種固定開頭字串。
6. 不擋的照原樣 `next(e)`,外掛不改輸入、不改結果。外掛自己出錯時引擎會跳過它(放行)。

### 三、安裝流程改成多外掛

- `scripts/lumos` 的 `_LEDGER_PLUGIN` 改成外掛清單 `_LUMOS_PLUGINS`(兩支);常數、訊息與函式名裡寫死「事件帳外掛」的改成通用說法。
- 同步:市集照舊確保一次;外掛清單逐支「使用者範圍沒裝就裝」;已登記市集的既有使用者先跑一次 `claude plugin marketplace update lumos-toolchain` 再裝(資料夾型市集是否需要這步沒驗證,跑了無害)。各支的結果分開印,回傳值取最差的一支(failed > no-source > absent > ok)。
- 移除:外掛清單逐支移除,全部處理完才移除市集一次;手動補做的指令只列沒做成的那幾支加市集。
- 既有測試 `t_ledger_plugin_files_valid` 的「市集只列一個外掛」改成「市集列出的外掛恰好是清單那幾支」。

## 條款

外掛行為的條款綁在 `mods/claude/lumos-guard/hooks/guard.test.ts`,測試標題以條款編號開頭,用 `claude plugin test mods/claude/lumos-guard` 在本機跑(CI 沒有 Claude,同事件帳外掛的做法)。

- [S1] 當審查席對暫存區以外的路徑(repo、家目錄、使用者設定)呼叫 `Write`、`Edit` 或 `NotebookEdit`,外掛應擋;大小寫不同、經過連結、相對路徑的寫法照真實路徑判;寫到暫存區(不含席報告暫存處)應照常 [manual:claude plugin test mods/claude/lumos-guard 的 S1 測試全綠]
- [S2] 當審查席用 `Read`、`Grep`、`Glob` 指到受保護的別席報告(席報告暫存處、或卷證資料夾裡同輪的席報告與收貨紀錄),應擋;同輪的 snapshot、dispatch、delta 與前幾輪的檔、不帶 path 的 repo 內搜尋應照常 [manual:claude plugin test mods/claude/lumos-guard 的 S2 測試全綠]
- [S3] 當審查席在 `Bash` 用 `gh`、`hub`,或用不在唯讀白名單的 git 子指令而沒有符合條件的 `-C 暫存區`,應擋;包含夾在 `&&`、`;`、`&`、子殼層、`bash -c` 字串裡的、前面帶 `VAR=` 或 `env` 的、帶 `--git-dir`、`--work-tree`、`-c`、`--output` 的;`git -C /tmp/x commit`、`git log`、`git diff` 應照常 [manual:claude plugin test mods/claude/lumos-guard 的 S3 測試全綠]
- [S4] 當審查席呼叫工具白名單以外的工具(`SendMessage`、`Monitor`、`Workflow`、`TaskCreate`、`EnterWorktree`、`mcp__` 開頭的),應擋 [manual:claude plugin test mods/claude/lumos-guard 的 S4 測試全綠]
- [S5] 若子代理的派工詞第一行不是合格的 `LUMOS-SEAT:`(含標記出現在內文、程式碼區塊、第二行以後),或呼叫者是主會談,外掛應完全不擋、不改輸入與結果;中文開頭的迴圈編號與席名(例 `審查席唯讀隔離/r1/資安-sonnet`)應認得 [manual:claude plugin test mods/claude/lumos-guard 的 S5 測試全綠]
- [S6] 若審查席再派子代理(輸入帶 `parentAgentId`),新子代理應繼承發起方的標記、忽略自己派工詞裡的標記 [manual:claude plugin test mods/claude/lumos-guard 的 S6 測試全綠]
- [S7] 若審查席子代理在登記完成前就呼叫工具,外掛應先等同一會談啟動中的審查席派工(最多 5 秒)再判斷;派工被拒或丟錯時應從啟動中清單移除 [manual:claude plugin test mods/claude/lumos-guard 的 S7 測試全綠]
- [S8] 當外掛內部出錯,該次工具呼叫應照常放行 [manual:claude plugin test mods/claude/lumos-guard 的 S8 測試全綠]
- [S9] 當 `lumos install` 與 `uninstall` 執行,外掛清單的兩支應各自裝上與移除、市集只在全部移完後移除一次,任一支失敗只影響它自己並照實印出 [test:t_install_registers_guard_plugin]
- [S10] 當檢查 repo 內的外掛檔,`lumos-guard` 的描述檔與 hooks.json 應合法,市集列出的外掛恰好是清單那兩支,外掛原始碼不改寫任何輸入或結果 [test:t_guard_plugin_files_valid]
- [S11] 當設計審與代碼審的派工範本更新,§1、§3、§7.6、§7.8 四段的派工詞第一行應是合格的 `LUMOS-SEAT:`,且編排者須知寫明席報告暫存處 [test:t_seat_templates_carry_marker]
- [S12] 當事件帳外掛記 `spawn` 事件,發起方應取 `parentAgentId`,子代理派的孫代理那筆的 `agent` 欄應是那個子代理的編號 [manual:claude plugin test mods/claude/lumos-ledger 的 S12 測試全綠]
- [S13] 當用 `claude -p` 載入兩支外掛、派一個第一行帶 `LUMOS-SEAT:` 的子代理叫它改 repo 裡的檔、讀席報告暫存處的別席報告、`git commit` 與 `gh pr create`,四者都應被擋,repo 內容不變 [manual:暫存 repo 放一份假暫存處,claude -p 搭 --plugin-dir 兩支外掛跑一場,比對 git status 與 lumos events]

## 回退

- 把 `lumos-guard` 從外掛清單與市集檔拿掉,同步流程照 [[Projects/Lumos事件帳_計劃]] 回退節第 1 步的做法改成「確保它不在」,下次 install / update 就會移除;再刪外掛資料夾、測試與手冊那一行。外掛不寫任何檔,沒有資料要清。

## 實務隱患

- 已排除:金流:只擋本機工具呼叫,不碰付款
- 已排除:對外送出:外掛不呼叫網路,也不跑外部指令(取真實路徑用引擎的檔案介面)
- 已排除:不可逆:只擋不改,擋錯的代價是審查員那次工具呼叫失敗、換做法;拿掉外掛即回到現狀
- 守衛面:審查席改成白名單,白名單外的工具、寫檔、讀別席報告、git 與 gh 一律擋;fail-open;S1 到 S8 綁測試。
- 效能:每次工具呼叫多一次記憶體查表;只有審查席的呼叫才取真實路徑與斷詞。
- 併發:多個審查席同時跑,各自以子代理編號查表;「啟動中」清單以會談為鍵、只在派工期間存在。
- 誤擋:Bash 白名單會擋下席位合法的 git 用法(例如在 repo 裡 `git stash` 做實驗);理由文字教它改用 `-C 暫存區`。
REVISIT:2026-11-06 用 lumos events 數這一個月審查席被擋的次數與種類,誤擋多就調白名單

## 誠實界線

- Bash 仍是完整的 shell:`cat` 讀別席報告、`>` 寫 repo、`curl` 打 GitHub API、`python -c`、變數與 `eval` 組出來的指令都擋不到。這道隔離防的是「被文件裡的指令誘導,直接用工具改 repo、開 PR、讀別席報告」,不防一個有心繞的審查員,也不夠當自主迴圈解禁 `--pr` 的依據。
- 標記靠派工詞第一行:編排者漏寫或寫錯位置,那一席就沒有隔離。S11 只盯範本,盯不到編排者實際派工時有沒有照抄。
REVISIT:2026-11-06 用 lumos events 數這一個月派出的審查席裡,派工詞第一行帶 LUMOS-SEAT 的比例;低於九成就把「派工有沒有帶標記」接進收貨檢查
- 外掛熱重載、行程重啟、`/clear`、`--resume` 都會清掉對應表,之前派出、還在背景跑的席位之後不受保護;fail-open 也一樣。
- 席報告暫存處是新的慣例:編排者沒照做(把報告存別處)時,別席報告不受保護。
- Codex 編排的審查席不受保護。

## 審計修正紀錄

- r1(2026-10-06,4 席:正確性、邊界、資安、架構對齊;外家席依 Enzo 指示不派):40 條/blocking 26/兩席獨立抓到 blocker:標記格式首字限英數,真實席名多數判不合格、隔離靜默全關;資安席實測 7 條繞法(gh 開 PR、--git-dir 抵消 -C、Monitor 與 Workflow 與 SendMessage 繞過、macOS 大小寫不分的路徑、別席報告審查中在 repo 外)。Enzo 裁改白名單、防被誘導(決策 d2 取代 d1)。卷證 `governance/review-reports/審查席唯讀隔離/`。
  - 折入:工具改白名單、寫檔只准暫存區(取真實路徑、折疊大小寫)、git 改唯讀白名單並整串斷詞、gh 擋、定席報告暫存處並保護它、讀別席報告只擋明確指向、標記只認第一行且中文可、子代理一律繼承、啟動中清單 try/finally 與 5 秒上限;不再需要 repo 範圍判定,pickMain 與漂移守衛整段拿掉;安裝流程多外掛細節寫齊;外掛行為條款綁 TS 測試標題;明寫這份隔離不構成自主迴圈解禁依據。
