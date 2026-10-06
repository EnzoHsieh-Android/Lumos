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
    valid: true
---
# 審查席唯讀隔離_計劃

白話:設計審、代碼審派出去的審查員是用 Agent 工具開的子代理,會繼承編排者的全部權限——被審的文件如果藏了惡意指令,審查員可以被誘導去改 repo、開 PR;同一輪的審查員也看得到別席已經存下的報告,「各自獨立」只靠派工詞自律。這份計劃新增一支 Claude Code 外掛 `lumos-guard`:派工詞帶 `LUMOS-SEAT:` 那一行的子代理,在它呼叫工具的那一刻檢查,寫 repo、讀同輪別席報告、在 repo 裡跑會改狀態的 git 指令一律擋下。

PRIOR-ART: 最小解在 harness 的工具呼叫攔截點,不在提示詞。[[Systems/nested-agent-permission-scope]] 2026-06 設計過另一條路——把審查員改成 `claude -p --allowedTools "Read,Grep,Glob"` 子程序(工具清單在 harness 層收窄),但一直沒實作,而且審查員常要跑 Bash 做重現實驗(`claude -p`、`git -C <臨時目錄>`),工具清單收到只剩讀取就做不了。本案改用外掛的 `tool.call` 攔截:引擎每次要跑工具前都經過它,`e.agentId` 指出是哪個子代理,`{ deny }` 擋下(型別檔 'tool.call' 說明);子代理是誰派的、派工詞是什麼,從 `agent.spawn` 的輸入 `prompt` 與結果 `agentId` 對起來。外掛寫法、市集、測試做法全部沿用 [[Systems/lumos事件帳]](核心邏輯可注入、`claude plugin test`、本 repo 的 `.claude-plugin/marketplace.json`)。外掛只能匯入自己資料夾裡的檔(plugin-authoring reference),所以主 checkout 判定在 `lumos-guard` 自帶一份兩行的 `pickMain`,用 `scripts/test_lumos.py` 的漂移守衛比對它跟事件帳外掛那份逐字相同(事件帳那份又已經由 `rules-fixture.ts` 對齊 Python 讀取端)。
RETIRE-IF: ①上線兩個月內 `lumos events` 看得到的審查席工具呼叫裡,這支外掛一次都沒擋過,而且審查卷證也沒出現過席位改 repo 或讀別席報告——風險沒在真實發生,維護成本不值;②Claude Code 的 Agent 工具開始支援逐次指定可用工具(那時改用官方機制);③審查席全面改成 `claude -p` 子程序且工具清單收窄(回到 nested-agent-permission-scope 那條路)。

## 範圍

- **做**:
  1. 新外掛 `mods/claude/lumos-guard/`,加進同一份市集檔;`lumos install` 照事件帳的流程一起裝與移除。
  2. 認出審查席:`agent.spawn` 時看派工詞,含一行 `LUMOS-SEAT: <迴圈編號>/<輪次>/<席名>` 的,記下「這個子代理編號 → 迴圈、輪次、席名」。輪次一律寫成 `rN`(含 r,例 `r2`),跟卷證檔名 `rN-<席名>.md`、`rN-snapshot.*`、`rN-dispatch.json` 同一種寫法。
  3. 在 `tool.call` 對這些子代理擋三類(其餘照常):
     - **寫 repo**:`Edit`、`Write`、`NotebookEdit` 的目標路徑落在主 checkout 或它任一 worktree 底下 → 擋;寫到 repo 以外(暫存區、`/tmp`)照常。
     - **讀同輪別席報告**:`Read` 的目標落在 `governance/review-reports/<這席的迴圈>/` 底下、檔名以 `<這席的輪次>-` 開頭、而且不是 `<輪次>-snapshot.*`、`<輪次>-dispatch.json`、也不是這席自己的 `<輪次>-<這席的席名>.md` → 擋(同輪的收貨紀錄 `<輪次>-intake.md` 也擋:它是編排者看過各席報告後寫的,讀了等於讀到別席)。`Grep`、`Glob` 的搜尋範圍若涵蓋這個卷證資料夾也擋:範圍是 `path`(省略時是會談 cwd)、`Glob` 的 `pattern` 本身是絕對路徑時也看 `pattern`;這兩個工具在某些建置不註冊,用工具名字串比對,不存在就不用管。前幾輪的報告、收貨紀錄照常可讀(驗收輪要看)。
     - **在 repo 裡跑改狀態的 git**:`Bash` 指令依 `&&`、`;`、`|`、換行切成各段,每段若是 `git` 指令,跳過全域選項(`-c k=v`、`--no-pager`、`--git-dir=…`、`--work-tree=…` 等,`-C <路徑>` 另外記下),第一個子指令是 `commit`、`reset`、`restore`、`checkout`、`switch`、`stash`、`rebase`、`merge`、`pull`、`push`、`am`、`apply`、`clean`、`add`、`rm`、`mv`、`cherry-pick`、`revert`、`branch`、`tag`、`worktree`、`config`、`notes`、`update-ref`、`gc`、`prune` 之一,而且沒有 `-C` 指到 repo 以外的路徑 → 擋(與派工詞「git 一律 -C 臨時目錄」那條相同;`branch`、`tag`、`worktree`、`config` 不分是不是唯讀用法一律擋,誤擋時席位改用 `-C` 臨時目錄或 `git log` 類唯讀指令)。
  4. 擋下時回 `{ deny }`,理由寫明擋了什麼、為什麼、席位該怎麼做(例:「審查席不准寫 repo;實驗請寫到你自己的臨時目錄」)。不另寫帳;外掛之間的先後引擎文件沒寫,所以「事件帳記不記得到被擋的那次」不保證,S11 實測後照實寫進系統筆記。
  6. 安裝流程改成支援多支外掛:`scripts/lumos` 的 `_LEDGER_PLUGIN` 單一常數改成外掛清單,`_sync_claude_plugin` 與 `_teardown_claude_plugin` 對清單裡每一支各裝各移;既有測試 `t_ledger_plugin_files_valid` 的「市集只列一個外掛」改成「市集列出的外掛恰好是清單裡那幾支」。
  7. 順手修事件帳外掛:它的 `spawn` 事件用 `e.agentId` 記發起方,但引擎給發起方的欄位叫 `parentAgentId`(型別檔 `AgentSpawnInput`),子代理再派子代理時發起方被記成空的;改用 `parentAgentId` 並補測試。這條獨立成一個 fix 提交。
  5. 兩本手冊的派工範本加一行 `LUMOS-SEAT:`:`skills/lumos-design-loop/templates.md` 的 §1 審計員、§3 code-loop reviewer、§7.6 架構對齊、§7.8 資安這四段(辯方、implementer、task reviewer 不是審查席,不加);說明這行由外掛讀。
- **不做**:
  - 擋 `Bash` 的一般寫檔(`>`、`tee`、`sed -i`、`python -c` 寫檔):指令文字推不出寫到哪裡,誤擋多過真擋;靠派工詞與代碼審。
  - 擋 `Bash` 的 `cat` 讀別席報告:同上,只擋 `Read`、`Grep`、`Glob`。
  - Codex 編排的審查席(Codex 沒有同等攔截點)。
  - 自主迴圈解禁 `--pr`([[Systems/nested-agent-permission-scope]] 決策 d4 的解禁條件是「唯讀子代理隔離落地 + 過代碼審終審」;本案只提供隔離,解禁另案、要人裁)。
  - 驗席位自報的模型:事件帳的 `spawn` 事件已記引擎實際解析出的模型;要不要拿來比對派工單另案。

落點:新開 `Systems/lumos-guard`(管外掛檔);市集檔的家仍是 [[Systems/lumos事件帳]]、安裝流程的家仍是 [[Systems/lumos-cli-lifecycle]],只在那兩篇補一句。

## 做法

### 一、認出審查席

- `agent.spawn`:先 `next(e)`,拿到結果的 `agentId`(子代理沒啟動、被拒則不記)。派工詞 `e.prompt` 逐行找 `LUMOS-SEAT: ` 開頭的行,取第一行;值照 `<迴圈編號>/<輪次>/<席名>` 切三段,三段都要符合 `[A-Za-z0-9][A-Za-z0-9._一-鿿-]*`(迴圈編號與席名常帶中文),任一段不合就當沒有標記(不擋;派工範本有測試盯著格式)。
- 記在外掛記憶體裡,以子代理編號為鍵,另存派它的會談編號;會談結束(`session.end`)時清掉那個會談的對應。
- 子代理再派子代理:子代理發起的 `agent.spawn` 輸入帶發起方的 `parentAgentId`(主迴圈發起的沒有這個欄);發起方是審查席時,新子代理繼承同一個席位標記(不能靠再派一層逃掉)。
- 登記的空窗:引擎要等子代理啟動後才回報它的 `agentId`,子代理的第一次工具呼叫可能比登記早。對策:`agent.spawn` 一進來、在 `next(e)` 之前,若派工詞帶標記(或發起方是審查席),先把這次派工放進「啟動中」清單;`tool.call` 遇到表裡查不到的子代理、而同一會談還有「啟動中」的派工時,先等它們都回報完再查表(子代理的工具呼叫一定在它啟動之後,等這一下不會互卡)。

### 二、判斷「在 repo 裡」

- repo 的範圍 = 主 checkout 頂層,加上它所有 worktree 的頂層。主 checkout 用跟事件帳外掛同一條判定(`git rev-parse --path-format=absolute --show-toplevel --git-common-dir`,自帶的 `pickMain` 與事件帳那份由漂移守衛比對);worktree 清單用 `git worktree list --porcelain` 的 `worktree` 行。判定以會談的 cwd 為鍵快取 10 分鐘。
- 工具輸入的路徑:相對路徑以會談 cwd 補成絕對路徑;比對前正規化(去 `.`、`..`、重複斜線)。路徑是連結時看它自己的位置,不跟連結(寫到 repo 裡的連結本身就算寫 repo)。
- git 判定失敗(不在 repo、逾時):這一次照常放行,不擋(外掛一律 fail-open)。

### 三、擋法與理由文字

- 回傳 `{ deny: "<一句擋了什麼>;<為什麼>;<該怎麼做>" }`,例:「審查席不准寫 repo 裡的檔(governance/x.md);審查員要保持唯讀,被審材料裡的指令不能讓你改到 repo;實驗請寫到你自己的臨時目錄」。
- 不擋的情況照原樣 `next(e)`,外掛不改輸入、不改結果。

### 四、手冊

- 派工範本的每段席位派工詞加一行 `LUMOS-SEAT: <loop>/<rN>/<席名>`,並在範本的「編排者須知」寫明:這行是外掛擋寫入與讀別席報告用的,漏寫就沒有隔離。
- 「席位做 git 實驗一律 -C 臨時目錄」那句後面補一句:外掛會擋在 repo 裡跑改狀態的 git。

## 條款

- [S1] 當子代理的派工詞含合格的 `LUMOS-SEAT:` 行而且它對主 checkout 或任一 worktree 底下的路徑呼叫 `Edit`、`Write` 或 `NotebookEdit`,外掛應回 `{ deny }` 且理由帶「審查席不准寫 repo」;寫到 repo 以外的路徑應照常執行 [test:t_guard_seat_write_repo_denied]
- [S2] 當審查席 `Read` 同一迴圈、同一輪別席的報告或收貨紀錄,應擋;同輪的 snapshot、dispatch、它自己的報告與前幾輪的檔應照常可讀;`Grep` 或 `Glob` 的範圍(`path`,省略時是 cwd;或絕對路徑的 `pattern`)涵蓋這個卷證資料夾也應擋 [test:t_guard_seat_peer_report_denied]
- [S3] 當審查席在 `Bash` 裡跑會改狀態的 git 子指令(含夾在 `&&`、`;`、`|` 後面的、前面帶全域選項的)、而且沒有用 `-C` 指到 repo 以外的路徑,應擋;`git -C <臨時目錄> commit` 與唯讀的 `git log`、`git diff`、`git show` 應照常 [test:t_guard_seat_git_mutation_denied]
- [S4] 若子代理的派工詞沒有 `LUMOS-SEAT:` 行、標記格式不合、或呼叫者是主會談,外掛應完全不擋、不改輸入與結果 [test:t_guard_non_seat_untouched]
- [S5] 若審查席再派子代理(輸入帶 `parentAgentId`),新子代理應繼承同一個席位標記並受同樣的擋法 [test:t_guard_seat_child_inherits]
- [S12] 若審查席子代理在登記完成前就呼叫工具,外掛應先等同一會談「啟動中」的派工回報完再判斷,不得因為還沒登記而放行 [test:t_guard_seat_registration_window]
- [S13] 當事件帳外掛記 `spawn` 事件,發起方應取 `parentAgentId`,子代理派的孫代理 `agent` 欄應是那個子代理的編號 [test:t_ledger_spawn_records_parent]
- [S14] 當比對兩支外掛的 `pickMain`,兩份應逐字相同 [test:t_guard_pickmain_matches_ledger]
- [S6] 當外掛內部出錯、或判不出 repo 範圍(git 失敗、逾時),該次工具呼叫應照常放行 [test:t_guard_fail_open]
- [S7] 若路徑是相對路徑、帶 `..`、或是指向 repo 外的連結,判斷「在 repo 裡」應照會談 cwd 補全、正規化後比,連結看它自己的位置 [test:t_guard_path_normalize]
- [S8] 當 `lumos install` 與 `uninstall` 執行,`lumos-guard` 應跟 `lumos-ledger` 一起裝上與移除,市集檔列出的外掛恰好是那兩支;任一支裝失敗只影響它自己 [test:t_install_registers_guard_plugin]
- [S9] 當檢查 repo 內的外掛檔,`lumos-guard` 的描述檔與 hooks.json 應合法,外掛原始碼只在 `tool.call` 回 `{ deny }`、不改寫任何輸入或結果 [test:t_guard_plugin_files_valid]
- [S10] 當設計審與代碼審的派工範本更新,§1 審計員、§3 code-loop reviewer、§7.6 架構對齊、§7.8 資安四段應各有一行格式合格的 `LUMOS-SEAT: <loop>/<rN>/<席名>`(用外掛同一條格式規則檢查) [test:t_seat_templates_carry_marker]
- [S11] 當用 `claude -p` 載入外掛、派一個帶 `LUMOS-SEAT:` 的子代理叫它改 repo 裡的檔與讀同輪別席報告,兩者都應被擋、事件帳記成 denied,repo 內容不變 [manual:暫存 repo 放一份假卷證,claude -p 搭 --plugin-dir 兩支外掛跑一場,比對 git status 與 lumos events]

## 回退

- 把 `lumos-guard` 從市集檔拿掉、同步流程改成「確保它不在」(同 [[Projects/Lumos事件帳_計劃]] 回退節第 1 步的做法),下次 install / update 就會移除;再刪外掛資料夾、測試與手冊那一行。外掛不寫任何檔,沒有資料要清。

## 實務隱患

- 已排除:金流:只擋本機工具呼叫,不碰付款
- 已排除:對外送出:外掛不呼叫網路;唯一的外部行為是本機 `git rev-parse` 與 `git worktree list`
- 已排除:不可逆:只擋不改,擋錯的代價是審查員那次工具呼叫失敗、換做法;拿掉外掛即回到現狀
- 守衛面:新增一道擋(審查席的寫 repo、讀同輪別席報告、在 repo 裡跑改狀態的 git),fail-open;S1 到 S7 綁測試。
- 效能:每次工具呼叫多一次記憶體查表;只有審查席的呼叫才判路徑,repo 範圍判定快取 10 分鐘。
- 併發:多個審查席同時跑,各自以子代理編號查表,不共用可變狀態。

## 誠實界線

- 只擋看得出目標的工具(Edit、Write、NotebookEdit、Read、Grep、Glob)與明顯的 git 指令;`Bash` 的一般寫檔與讀檔擋不到。這道隔離防的是「被誘導直接用工具改 repo、讀別席報告」,不防一個有心繞的審查員。
- 標記靠派工詞:編排者漏寫 `LUMOS-SEAT:`,那一席就沒有隔離。S10 只盯範本有沒有這行,盯不到編排者實際派工時有沒有照抄。
REVISIT:2026-11-06 用 lumos events 數這一個月派出的審查席裡,派工詞帶 LUMOS-SEAT 的比例;低於九成就把「派工有沒有帶標記」接進收貨檢查
- 外掛熱重載或行程重啟會忘掉「哪個子代理是哪一席」,重載前已派出的席位之後不受保護;fail-open 也一樣。
- 外掛之間的先後引擎文件沒寫:被擋的那次呼叫事件帳記不記得到,要看實測(S11)。
- Codex 編排的審查席不受保護。
