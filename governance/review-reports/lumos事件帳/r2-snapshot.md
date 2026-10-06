---
type: project
status: doing
created: 2026-10-05
updated: 2026-10-05
tags:
  - type/project
  - status/doing
  - scope/platform
lands_in:
  - Systems/lumos事件帳
  - Systems/lumos-cli-lifecycle
  - Systems/lumos-cli-read
  - Systems/hook信任邊界
related:
  - "[[Systems/codex-harness]]"
decisions:
  - content: repo 內放 TypeScript 寫的 Claude mod(mods/claude/lumos-ledger/),不帶任何 npm 套件,型別由 Claude Code 引擎提供。考慮過的其他做法:①只用設定檔的命令型 hook(Python),但它碰不到 turn.complete、agent.spawn、session.append 這些 mod 專屬事件;②mod 放另一個 repo,但會跟 lumos 本體版本脫鉤。代價:repo 多一種語言;mod 行為的測試要靠 claude plugin test 或真會談,CI 沒有 Claude 跑不了,那幾條條款是人工驗。
    id: d1
    context: 零依賴 Python 是本 repo 家規;mod 只能用 TypeScript/JavaScript 寫
    why_chosen: Enzo 2026-10-05 在 Hook Refactor 會談接受;mod 事件是事件帳唯一的穩定結構化來源
    decided: 2026-10-05
    valid: true
  - content: lumos install 透過 Claude 的指令列工具安裝 mod:claude plugin marketplace add <lumos 來源 repo> 再 claude plugin install lumos-ledger@lumos-toolchain;偵測不到 claude 指令就略過。考慮過的其他做法:①直接改 ~/.claude/settings.json 的外掛欄位(本 repo 已有合併設定檔的程式),但沒驗證這樣會不會自動安裝外掛;②請使用者手動裝。代價:安裝流程多依賴一個外部指令,它的參數或行為改了要跟著改。
    id: d2
    context: mod 要長期生效必須以外掛形式安裝;2026-10-05 在隔離設定目錄實測這條路裝得起來、claude -p 不帶參數也載入
    why_chosen: Enzo 2026-10-05 在 Hook Refactor 會談接受;唯一實測過能用的路
    decided: 2026-10-05
    valid: false
    superseded_by: d3
    ended: 2026-10-05
  - content: lumos install / update 透過 Claude 的指令列工具安裝 mod:市集來源一律用 _lumos_src()($LUMOS_HOME 或 ~/harness/lumos-toolchain),不用執行中這支 lumos 的位置;claude plugin marketplace add <來源> --scope user 再 claude plugin install lumos-ledger@lumos-toolchain --scope user;同名市集來源不同時先移除再加;偵測不到 claude 或來源沒有市集檔就略過。考慮過的其他做法:①直接改 ~/.claude/settings.json 的外掛欄位(沒驗證會不會自動安裝);②用執行中 lumos 的位置當來源(d2 原寫法,從 worktree 安裝後刪 worktree 外掛就失效)。代價:安裝流程多依賴一個外部指令;外掛跟著來源 repo 目前的分支走。
    id: d3
    context: d2 的來源寫法在設計審 r1 被三席指出:資料夾型市集直接讀來源資料夾,登記成會被刪的 worktree 會讓外掛失效
    why_chosen: Enzo 2026-10-05 接受「安裝依賴 Claude 指令列」;來源改法是設計審 r1 折入,不改變 Enzo 接受的方向
    decided: 2026-10-05
    valid: true
---
# Lumos事件帳_計劃

白話:Lumos 要判斷「AI 這一輪做了什麼」(改了哪些檔、跑了哪些測試、成不成功、派了哪些子代理),目前只能事後去解析 Claude Code 與 Codex 的逐字稿。逐字稿官方明說不是穩定介面,格式一變判斷就靜默失效(2026-10-05 實測:Codex 收工檢查只認 0.144.1/0.153.2,本機 0.160.0 每次都略過);有些情境逐字稿根本不落地(從 Claude 開出來的終端機、互動會談的子代理)。Claude Code 2.1.289 的 mod(外掛裡的函式 hook)可以在行程內直接看到結構化的回合、工具呼叫與子代理。這份計劃做一個只觀察的 mod,把這些寫成 Lumos 自己的事件帳,再給一個唯讀的讀取指令;之後的收工檢查、接手視圖、推播量測改讀它(各自另案)。

依據:Enzo 2026-10-05 在「Hook Refactor」會談選定方向(Claude mod 能讓治理切得更細,不必遷就 Codex),地毯式對照圖譜約 70 條限制後排為第 1 名;前提由 [[Verification/2026-10-05_Claude-mod能力實測]] 實測成立。

PRIOR-ART: 最小解在 Lumos 自己這一層,資料源借平台。①寫入慣例借本 repo 既有的 hook 事件帳(`_hookevent.py`):放 repo 樹內 `governance/runtime/`、只寫在成功點、觀測壞掉不影響本業。忽略設定不靠消費專案的 `governance/.gitignore`(init 只在那個檔不存在時才寫 `runtime/`,既有檔不補,calc-ios 就因此提交過 hook 事件帳),改借 `_note_audit_work_dir` 的做法:第一次寫入時在事件帳資料夾放一個內容只有 `*` 的 `.gitignore`,讓它自己忽略自己。分段塊檔則是新做法,只借位置與 fail-open 慣例。②檔案切塊借日誌系統的分段檔(Kafka segment、logrotate):每次寫一個新塊檔,不重寫舊檔,避開 mod 檔案 API 沒有附加寫入(`$.fs.write` 是整檔覆寫)、單次寫入上限 4 MiB 的限制。③資料源用平台的 mod 事件(`turn.start`、`turn.complete`、`tool.call`、`agent.spawn`、`session.append`),不自己解析逐字稿。④安裝借 Claude Code 自己的外掛市集機制(`claude plugin marketplace add` + `claude plugin install`),實測在隔離設定目錄裝得起來、`claude -p` 不帶參數也載入;接進既有的全域同步流程(跟 Codex 審查席設定同一處)。⑤塊檔用「時間加隨機字串」命名,借日誌與物件儲存常見的不可變分段檔做法,避開覆寫與序號競態。
RETIRE-IF: 任一成立就撤掉或重想:①上線兩個月內沒有任何消費端(收工檢查、接手視圖、推播量測)改讀它(機械數:`grep -rn "_events_read" scripts/` 只剩讀取指令自己);②Claude Code 連續兩個版本讓 mod 事件改名或失效,而官方仍沒有穩定承諾;③官方提供穩定的結構化事件匯出(例如逐字稿宣告為穩定介面),那時改讀官方的。
REVISIT:2026-12-05 量 RETIRE-IF ①,並重跑一次 [[Verification/2026-10-05_Claude-mod能力實測]] 的最小實驗確認 mod 事件沒變

## 範圍

- **做**:
  1. mod `lumos-ledger`:放 `mods/claude/lumos-ledger/`(`.claude-plugin/plugin.json`、`hooks/hooks.json`、`hooks/register.ts`),只觀察、不擋、不改、不注入。
  2. repo 根放市集檔 `.claude-plugin/marketplace.json`,市集名 `lumos-toolchain`,只列這一個外掛,`source` 用相對路徑 `./mods/claude/lumos-ledger`。
  3. 事件帳:寫在主 checkout 的 `governance/runtime/events/<會談編號>/<塊檔名>.jsonl`(在 git worktree 裡跑的會談也寫到主 checkout,事件帶 `worktree` 欄位);只在那個 checkout 有 lumos 認得的圖譜時寫;`governance/runtime/events/.gitignore`(內容 `*`)由 mod 第一次寫入時補上。
  4. 讀取:`scripts/lumos` 加 `_events_root(root)`、`_events_read(root, session)`、唯讀指令 `lumos events [--session <編號>] [--json]`;另有會刪檔的 `lumos events --prune [--days N]`(預設 30 天),不屬於唯讀。
  5. 安裝:在既有的全域同步流程 `_sync_global_hooks(src, "claude")` 裡加市集與外掛;移除在 `_teardown_global_claude` 裡做(`lumos uninstall`、`teardown` 都會經過它)。
  6. `lumos enforcement` 加一列 `claude-event-ledger`,只看事件帳時間,不呼叫任何外部指令。
- **不做**:消費端改讀(收工檢查、接手視圖、推播量測,各自另案);任何會改變 AI 行為的事(擋、改寫、注入);Codex 對應(平台沒有同等事件);實驗用 mod 的「讓位」功能;git 子模組裡的會談(見誠實界線);slim 安裝路徑(見誠實界線)。

落點:新開 `Systems/lumos事件帳`(`lumos new system lumos事件帳 --code mods/claude/lumos-ledger/hooks/register.ts --code mods/claude/lumos-ledger/hooks/ledger.test.ts --code mods/claude/lumos-ledger/hooks/hooks.json --code mods/claude/lumos-ledger/.claude-plugin/plugin.json --code .claude-plugin/marketplace.json`),管 mod、市集檔,以及事件帳格式與它跟 `hook-events.jsonl` 的關係;`scripts/lumos` 裡的改動依功能寫進既有的家:安裝與移除進 `Systems/lumos-cli-lifecycle`,`lumos events` 進 `Systems/lumos-cli-read`,enforcement 那一列進 `Systems/hook信任邊界`(既有 hook 事件帳「活著沒」的判法住在那篇),`Systems/lumos事件帳` 與 `Systems/hook信任邊界` 互連。新指令另要登記:`HELP_WHEN` 與指令說明字典、argparse 與分派、`skills/lumos-project-notes/commands/INDEX.md` 與對應的指令子檔。新的頂層資料夾 `mods/` 與 `.claude-plugin/` 只屬於工具鏈來源 repo:不進 `lumos vendor` 複製到消費專案的名單、不進 slim 建置、不進 anchor 保護名單(mod 不是閘);實作時逐一開那三份名單確認沒有用萬用規則把它們捲進去。

## 做法

### 1. 事件與格式(第 1 版)

每行一筆 JSON,共同欄位:`v`(固定 1)、`ts`(ISO 8601 帶時區)、`session`、`agent`(這筆事件發生在哪個子代理的迴圈,主會談為 null)、`worktree`(會談所在的 worktree 頂層,主 checkout 為 null)、`ev`(事件種類)。種類欄位刻意叫 `ev` 不叫 `kind`:同資料夾的 `hook-events.jsonl` 用 `kind` 表示結果(ok/timeout/error),同名異義會讓之後讀兩份帳的人猜錯。

| ev | 來自哪個 mod 事件 | 額外欄位 |
|---|---|---|
| `turn_start` | `turn.start`(只有主會談會觸發;引擎不為子代理觸發它) | `turn`(回合編號)、`origin`:這一回合的提示是誰送的,取主會談(`agentId` 為空)最近一筆 `door` 為 `prompt` 的 `session.append` 的 `origin.kind`(實測看過 `unclassified`、`task-notification`);`prompt_len` |
| `turn_end` | `turn.complete`(主會談與子代理都會觸發) | `turn`、`reason`:`answer` / `aborted` / `refusal` / `error` |
| `tool` | `tool.call`(等工具跑完) | `tool`、`ok`(`isError` 不是 true 且沒被拒)、`denied`、`paths`(工具輸入裡的 `file_path`、`path`、`notebook_path`,有才記)、`cmd`(Bash 指令前 500 字) |
| `spawn` | `agent.spawn` | `agent_type`、`model`(引擎解析後的實際模型)、`child`(被派出子代理的編號,取自 `next(e)` 結果的 `agentId`)、`denied`;這一筆的 `agent` 是發起派工的那一方 |
| `ledger_error` | mod 自己 | `what`:上一次寫塊失敗的原因 |

回合歸屬:工具事件沒有回合編號(引擎不給),讀取端這樣框:主會談的工具事件屬於前一筆 `turn_start` 到下一筆 `turn_end` 之間;子代理沒有 `turn_start`,它的工具事件屬於「它自己的上一筆 `turn_end`(沒有就從派出它的那筆 `spawn`)之後、到下一筆 `turn_end`」。子代理只有結束不是缺頭,不當成錯誤。

不記:提示全文、模型回應、工具結果內容(要內容就去讀逐字稿;事件帳只回答「發生了什麼」)。`session.append` 只用 `{ door: "prompt" }` 篩過的那一支 hook,其他列不經過 mod。

### 2. 寫入

- 狀態全部以會談編號為鍵(`/clear` 與 resume 會在同一個行程裡換會談編號,不觸發 `session.start`)。會談編號在寫塊當下用 `$.session.id()` 取,`session.end` 用事件自己的 `sessionId`。
- 塊檔名:`<寫入時的毫秒時間 13 位>-<隨機 8 個十六進位字元>.jsonl`。每次都是新名字,任何情況(熱重載、行程重啟、resume、並行)都不會覆蓋舊塊;讀取端依檔名排序。不靠記憶體裡的序號。
- 每筆事件先放進該會談的記憶體緩衝。寫塊時先同步取走整個緩衝(換成空的)再開始非同步寫,寫入中進來的事件留在新緩衝;所有寫塊排成一條串行佇列,一次只寫一個。觸發時機:`turn_end`、緩衝滿 50 筆、`session.end`。
- `session.end`:先寫塊、再呼叫 `next(e)`(引擎對結束只給一段很短的共用時間);寫不完就算了,不等。
- 順序:寫塊時先解出寫的位置並判完圖譜,成功了才同步取走緩衝;位置解不出來時緩衝原封不動,不先取再放回。
- 寫的位置:每次寫塊前用 `$.process.run(["git","rev-parse","--path-format=absolute","--show-toplevel","--git-common-dir"], { timeoutMs: 3000 })`,cwd 用 `$.session.cwd()`。主 checkout 頂層 = `--git-common-dir` 的上一層(它是名叫 `.git` 的資料夾時),否則用 `--show-toplevel`;兩者不同就表示在 worktree 裡,事件帶 `worktree`。所有寫檔路徑都用這個頂層組成絕對路徑。結果以「cwd」為鍵快取。git 回非零碼時分兩種:錯誤輸出含 `not a git repository` → 確定不在 repo 裡,快取成「不寫」並丟掉這個會談的緩衝、之後不再收(S2 的情境);其他非零碼、逾時、輸出解析不了 → 暫時失敗,不快取,這一塊不寫、緩衝留著,同一個 cwd 5 分鐘內不再重試 git;緩衝超過 500 筆就丟掉最舊的,記下丟了幾筆,等第一次寫成功時在那一塊開頭補一筆 `ledger_error`。
- 圖譜判定跟 lumos 的 `_vault_in` 同三種:`docs/*-knowledge/`、`docs/knowledge/`、或頂層就是獨立 vault(有 `MOC/` 且有 `Systems/` 或 `Verification/`)。用 `$.fs.list` 判資料夾(`kind` 為 `dir`)。
- 寫塊前若 `governance/runtime/events/.gitignore` 不存在,先寫一個內容只有 `*` 加換行的檔(跟 `_note_audit_work_dir` 寫的內容相同)。
- 寫失敗:吞掉,記下原因,下一塊開頭補一筆 `ledger_error`;不重試同一塊。所有 hook 照原樣回傳 `next(e)` 的結果(`session.end` 例外,先寫再 `next`);mod 例外時引擎本來就會跳過它(fail-open)。

### 3. 讀取與保留

- `_events_read(root, session)`:找事件帳資料夾一律先解主 checkout(見下一段),塊檔依「檔名開頭的毫秒時間、再比檔名」排序讀、合併,塊內照行序;同一毫秒的兩塊靠事件自己的 `ts` 已足夠判讀,不另保證先後;壞行與 `v` 不是 1 的行略過並各自計數;回傳事件清單與兩個計數。
- 主 checkout 怎麼找(讀取端與 enforcement 共用一支 `_events_root(root)`):`git -C <root> rev-parse --path-format=absolute --git-common-dir`,它是名叫 `.git` 的資料夾時取上一層,否則用 `root`;git 失敗或逾時(3 秒)就用 `root`。所以在 worktree 裡跑 `lumos events` 或 `lumos enforcement`,讀的是主 checkout 的事件帳。
- `lumos events`:沒給 `--session` 就列最近 10 個會談——先只看會談資料夾的修改時間排序、取前 10 個,只讀這 10 個的塊檔(會談編號、最後事件時間、回合數、工具呼叫數、失敗數)。給了就逐筆印。`--json` 給機器讀。沒有事件帳時回 0;`--session` 給了不存在的編號時回 2。兩者訊息都用本 repo 工具輸出的三段式(發生什麼 → 為什麼在意 → 指令獨立一行),可能原因列 mod 沒裝、這不是 Claude 會談、repo 沒有圖譜。
- `lumos events --prune [--days N]`:刪掉修改時間早於 N 天(預設 30)的會談資料夾,印刪了幾個。只動 `governance/runtime/events/` 底下;資料夾是符號連結時不跟。REVISIT:2026-11-05 看本 repo 事件帳資料夾大小與會談數,決定要不要把 prune 接進每日自主迴圈或 doctor
- 兩份帳的關係寫進 `Systems/lumos事件帳`:`hook-events.jsonl` 記「lumos 的 hook 自己有沒有跑」,事件帳記「AI 做了什麼」;互不取代。

### 4. 安裝與移除

- 位置:新開 `_sync_claude_plugin()`,由 `_sync_global_hooks(src, "claude")` 在既有步驟做完之後呼叫(`lumos install`、`update`、`bootstrap` 都會經過它;bootstrap 是以子行程跑 `install --force`);移除新開 `_teardown_claude_plugin()`,由 `_teardown_global_claude` 呼叫。都在既有探針拒絕之後,探針模式下照舊被擋。
- 回報:外掛步驟有自己的狀態(`ok` / `skipped` / `failed`)與自己的訊息,★不併進 `_sync_global_hooks` 的回傳字串★——那個字串現在有 ok、probe、merge-failed、absent 等值,`cmd_install` 只看 merge-failed、`_sync_global_claude` 用等於 ok 判斷,混進新值會讓它們誤判。成功與略過印到標準輸出,失敗印到標準錯誤。
- 適用範圍:來源固定是 `_lumos_src()`,跟這次是從哪個專案跑的無關——所以只要這台機器有 lumos 來源 repo,任何專案跑 `lumos install` 或 `lumos update` 都會確保外掛裝好。這是刻意的:外掛是使用者層的,本來就該一台機器一份。
- 開關:環境變數 `LUMOS_SKIP_CLAUDE_PLUGIN=1` 時兩邊都整段略過並印一行。測試執行器在建立拋棄式家目錄的同一處設定它、並清掉 `CLAUDE_CONFIG_DIR`;要測外掛那幾支測試自己取消開關、放一支假的 `claude` 腳本在 PATH 前面。
- 找 `claude` 用既有的 `_py_which`(只認絕對路徑、不撿目前目錄裡的檔)。
- 來源:市集來源一律用 `_lumos_src()`(`$LUMOS_HOME` 或 `~/harness/lumos-toolchain`),不用執行中這支 lumos 的位置——資料夾型市集是直接讀那個資料夾本身、不讀安裝時的拷貝,登記成一個會被刪掉的 worktree,外掛就會在 worktree 刪除後失效。`_lumos_src()` 底下沒有 `.claude-plugin/marketplace.json`(來源 repo 還是舊版,或那台機器沒有來源 repo)就略過並印一行。
- 安裝流程:`claude plugin marketplace list --json` 讀現有市集——沒有 `lumos-toolchain` → `claude plugin marketplace add <來源> --scope user`;有但來源不同 → 先 `claude plugin marketplace remove lumos-toolchain --scope user` 再加;一樣 → 不動。接著 `claude plugin list --json` 沒列出 `lumos-ledger@lumos-toolchain` 才 `claude plugin install lumos-ledger@lumos-toolchain --scope user`。之後拿新版 mod 不用任何外掛指令:`lumos update` 拉到新版後,下一個會談(或 `/reload-plugins`)就讀到。任何一步回非零碼、逾時(每步 30 秒)或 JSON 讀不懂,印一行(含錯誤輸出第一行)並回「失敗」狀態;外掛失敗不改 `lumos install` 的回傳碼(hook 註冊失敗才回 2 的既有規則不變)。
- 移除流程:找不到 `claude` 或 `claude plugin list --json` 沒列出這個外掛 → 不印任何失敗,略過;有 → `claude plugin uninstall lumos-ledger@lumos-toolchain`,再 `claude plugin marketplace remove lumos-toolchain --scope user`(只動使用者範圍)。失敗印一行並附這兩個手動指令。`teardown` 的確認清單加一行「Claude 外掛 lumos-ledger 與市集 lumos-toolchain」。

### 5. enforcement

- 一列,`layer` 名 `claude-event-ledger`。只看 `_events_root(root)` 解出的主 checkout 的 `governance/runtime/events/` 底下會談資料夾的修改時間(只看資料夾這一層,不讀塊檔):最近 7 天有 → `active`;資料夾存在但 7 天內沒有 → `stale`;資料夾不存在 → `unknown`。`detail` 寫明「只有 Claude Code 會寫;Codex 沒有對應」。
- 不呼叫 `claude` 或任何外部指令;結果只取決於檔案系統(解主 checkout 的那一次 `git rev-parse` 是本 repo 既有閘本來就在用的指令,不是新的外部依賴),跟注入的 `home` 一樣可以在測試裡隔離。
- 狀態值只用這三種,絕不使用 `inactive` 或 `degraded`——開場提醒只點名這兩種(`lumos-entry-hook.py` 的 `down` 清單),enforcement 的分母也只排除 `unknown`、`stale`、`registered-trust-unknown`;用錯會讓沒裝 mod 的人每次開場都被唸。
- 既有測試 `t_enforcement_never_raises_on_missing` 釘「恰 23 列」,要跟著改成 24 並在說明裡加這一列。

## 條款

- [S1] 當 Claude Code 會談(互動或 `claude -p`)在有圖譜的 git repo 裡跑、`lumos-ledger` 已安裝,事件帳應在主 checkout 的 `governance/runtime/events/<會談編號>/` 下出現塊檔,含 `turn_start`、`turn_end`、`tool`、`spawn` 四種,失敗的工具呼叫 `ok` 為 false,子代理的 `tool` 與 `turn_end` 帶 `agent` 編號,`spawn` 帶 `child` 且等於那個子代理事件的 `agent` [manual: 本機互動會談與 claude -p 各跑一場含失敗指令與兩個並行子代理的任務,lumos events --json 比對]
- [S2] 當會談所在目錄不在 git repo 裡、或主 checkout 沒有 lumos 認得的圖譜,mod 應不寫任何檔;會談從 repo 的子資料夾或 worktree 開時,應寫到主 checkout 頂層、不在子資料夾建 `governance/` [manual: 在無圖譜的臨時 git repo、本 repo 的 scripts 子資料夾、本 repo 的一個 worktree 各跑一場 claude -p,檢查寫入位置]
- [S3] 當塊檔寫入失敗,會談應照常進行,下一塊開頭應有一筆 `ledger_error`;mod 熱重載後的下一塊不得覆蓋任何既有塊檔 [manual: 把 events 資料夾換成唯讀跑一回合,恢復後再跑一回合看下一塊;另在會談中改 register.ts 觸發熱重載,比對重載前後塊檔清單只增不改]
- [S4] 當 `lumos events --session <編號>` 讀一個會談,應依檔名排序合併,壞行與版本不是 1 的行略過並分別計數印出;子代理只有 `turn_end` 時不得當成錯誤 [test:t_events_reader_merges_chunks]
- [S12] 當 `lumos events` 在一個 worktree 裡執行,應讀主 checkout 的事件帳,列得出在 worktree 裡跑的會談 [test:t_events_reader_from_worktree]
- [S5] 當沒有事件帳,`lumos events` 應回 0 並用三段式印「沒有事件帳」與可能原因;`--session` 給不存在的編號應回 2 [test:t_events_reader_no_ledger]
- [S6] 當安裝流程跑到 Claude 那一段且沒有 `LUMOS_SKIP_CLAUDE_PLUGIN`,應以 `_lumos_src()` 為市集來源:市集不存在就加、來源不同就先移除再加、已列出外掛就不再安裝;任一步失敗只讓外掛步驟回 `failed` 並在標準錯誤印一行,`_sync_global_hooks` 的回傳字串與 `lumos install` 的回傳碼都不變;來源沒有市集檔或找不到 `claude` 時回 `skipped` [test:t_install_registers_ledger_plugin]
- [S7] 當移除流程跑到 Claude 那一段,外掛有列出時應呼叫移除外掛與 `--scope user` 移除市集;找不到 `claude` 或沒列出外掛時不得印失敗;失敗時印一行並附兩個手動指令 [test:t_teardown_removes_ledger_plugin]
- [S8] 當 `lumos enforcement` 執行(在主 checkout 或它的 worktree 裡都一樣讀主 checkout 的事件帳),應多一列 `claude-event-ledger`,近 7 天有會談資料夾為 `active`、資料夾在但 7 天內沒有為 `stale`、資料夾不存在為 `unknown`;這一列不得出現 `inactive` 或 `degraded`,且整個計算不得呼叫任何外部指令 [test:t_enforcement_ledger_row]
- [S9] 當檢查 repo 內的外掛檔,市集檔與外掛描述檔應是合法 JSON、市集的 `source` 是 `./` 開頭的相對路徑且指到存在的外掛資料夾(回退時「外掛讀不到資料夾就載入失敗」的推論靠這個前提)、mod 原始碼裡寫檔的路徑只在 `governance/runtime/events/` 底下、寫的 `.gitignore` 內容與 `_note_audit_work_dir` 寫的相同、不呼叫任何會改變行為的 API(拒絕、改寫輸入、注入) [test:t_ledger_plugin_files_valid]
- [S10] 當測試執行器建立拋棄式家目錄,應同時設定 `LUMOS_SKIP_CLAUDE_PLUGIN=1` 並清掉 `CLAUDE_CONFIG_DIR`,使既有的 install / uninstall 測試不會呼叫真的 `claude` [test:t_runner_isolates_claude_plugin]
- [S13] 當同一會談的主迴圈與兩個子代理在同一個寫塊期間各送事件、以及 mod 被重新載入後再寫,所有事件都應各出現在恰好一個塊檔裡、沒有任何塊檔被改寫 [manual: mods/claude/lumos-ledger/hooks/ledger.test.ts 用 claude-code/testing 的模擬引擎跑並行與重新載入兩個案例,`claude plugin test mods/claude/lumos-ledger` 全綠;CI 沒有 Claude,這條在本機跑]
- [S11] 當 `lumos events --prune --days N` 執行,應只刪除修改時間早於 N 天的會談資料夾、不跟符號連結、不碰 events 以外的路徑 [test:t_events_prune_only_old_sessions]

## 回退

- 分兩步,順序不能反:
  1. 先發一版「安裝不再加外掛,但移除照舊」(拿掉 `_sync_global_hooks` 裡的安裝段,保留 `_teardown_global_claude` 的移除段),請每台機器跑一次 `lumos uninstall`(或手動 `claude plugin uninstall lumos-ledger@lumos-toolchain`、`claude plugin marketplace remove lumos-toolchain --scope user`)。哪些機器裝過無法從 repo 得知,只能靠使用者自己;漏掉的機器在第 2 步之後外掛會因為讀不到 `mods/` 而載入失敗(資料夾型市集直接讀來源資料夾),不會繼續寫事件帳,只是留下一筆失效的市集登記。
  2. 再拿掉其餘程式:刪 `mods/claude/lumos-ledger/`、`.claude-plugin/marketplace.json`;`scripts/lumos` 拿掉 `_events_read`、`events` 指令、移除段、enforcement 那一列(測試的列數改回 23)、測試執行器的開關;刪 S4–S11 的測試。
- 已寫出的事件帳在 `governance/runtime/events/`,有自帶的 `.gitignore`,留著無害,要清就刪資料夾。
- 本計劃不改任何既有 hook 與 git 閘的行為,回退不影響它們。

## 實務隱患

- 已排除:金流:只記錄回合與工具呼叫,不碰任何付費、計費或額度流程。
- 已排除:對外送出:事件帳只寫在本機 repo 內自帶忽略檔的資料夾,mod 不呼叫任何網路 API、不送訊息給其他會談。
- 不可逆:安裝會改使用者層的 Claude 設定(加一個市集、裝一個外掛)。可以用 `lumos uninstall` 撤回;程式回退要照回退節兩步的順序,漏跑移除的機器會留下一筆失效的市集登記(外掛本身載入失敗、不再寫帳)。
- 已排除:守衛面:mod 不擋、不改、不注入,不碰任何既有 hook 與 git 閘;enforcement 只多一列資訊,狀態值限定不觸發開場提醒的三種。
- 刪檔:`lumos events --prune` 會刪資料夾。只刪 `_events_root` 底下 `governance/runtime/events/` 的直接子資料夾、不跟符號連結、只看修改時間;刪錯的代價是丟掉事件帳(不影響程式與圖譜),S11 守。
- 並行與資料完整性:同一會談的主迴圈與多個子代理同時觸發寫塊。用「先同步取走緩衝、串行佇列寫、每塊唯一檔名」處理,不靠序號(做法第 2 節);自動測試在 mod 自己的測試檔(S13),因為 Python 測試碰不到 mod 的執行環境。

## 誠實界線

- 只有 Claude Code;Codex 沒有同等事件,enforcement 那一列的說明寫明。
- mod API 沒有找到穩定承諾(型別檔約 14,000 行、說明都沒寫);官方改版可能讓事件改名或失效。上面的 REVISIT 會重跑最小實驗。
- fail-open:mod 出錯時引擎跳過它,那段時間沒有事件;熱重載與當機會丟掉還在緩衝裡的事件(最多 50 筆,git 判定一直失敗時最多 500 筆)。事件帳只能當「有記到的就是真的」,不能當「沒記到就沒發生」。
- 寫失敗補的 `ledger_error` 本身也可能寫不進去(例如磁碟滿),那時事件帳裡沒有任何痕跡。
- git 子模組裡的會談,頂層是子模組;子模組通常沒有圖譜,整場不寫。
- 只用 slim 安裝的人沒有事件帳(slim 不裝 Claude 外掛)。
- `cmd` 記 Bash 指令前 500 字,可能含秘密;跟本機逐字稿同一等級的暴露面,放在自帶忽略檔的資料夾。若被強制加進版控會外洩——沒有機械擋。REVISIT:2026-12-05 一併查 `git ls-files governance/runtime` 在本 repo 與 calc-ios 是否為空
- 保留期限靠人或排程跑 `lumos events --prune`,目前沒有自動跑;上面的 REVISIT:2026-11-05 決定要不要接進自主迴圈。
- `lumos install` 多依賴 Claude 的指令列工具;沒裝 Claude 的機器(只用 Codex)會略過。`claude plugin marketplace list --json` 的輸出欄位(怎麼讀出來源路徑)只看過說明、沒實測,實作第一步先用隔離設定目錄量一次,寫進 `Systems/lumos事件帳`。
- 這些 mod 介面只讀過型別檔、沒有實測:`session.end`、`$.process.run`、`$.fs.list`、結束原因 `aborted` 與 `refusal`、`session.append` 用 `door` 篩;實作時第一個測試就要逐一跑到(見 S1、S3)。

## 審計修正紀錄

- r1(2026-10-05,3 席+架構對齊席,外家否決席依 Enzo 指示缺席):33 條/blocking 18/寫入端的並行與序號、寫入位置、安裝來源、enforcement 與測試隔離是主要的洞,全數折入。席報告在 `governance/review-reports/lumos事件帳/`。
  - 依根因十組折入:①回合歸屬——子代理不觸發 `turn.start`、工具事件沒有回合編號,改成只有主會談記 `turn_start`、讀取端用前後框出回合(正確性小項、邊界 F1、接手 F1);②並行寫入與覆寫——塊檔改「時間加隨機字串」唯一檔名、先同步取走緩衝、串行佇列(正確性 F1 F2、邊界 F2 F6、接手 F3);③寫入位置——絕對路徑、寫到主 checkout、失敗不快取、圖譜判定對齊 `_vault_in`、cwd 為鍵(邊界 F3 F4 F5、接手 F4);④enforcement 與測試——不呼叫任何外部指令、只看資料夾時間、單列 `claude-event-ledger`、既有 23 列測試改 24、測試執行器設 `LUMOS_SKIP_CLAUDE_PLUGIN` 並清 `CLAUDE_CONFIG_DIR`(新增 S10)(正確性 F5 F6、接手 F6、架構 F2);⑤安裝來源——用 `_lumos_src()`、同名不同來源先移除再加、接進 `_sync_global_hooks`、找指令用 `_py_which`、bootstrap 的錯誤描述更正、新版靠重新載入不靠 update(正確性 F3 F4、邊界 F9、接手 F7 F9、架構 F3);⑥移除與回退——先判有沒有裝、`--scope user`、teardown 確認清單、回退分兩步(接手 F8、正確性小項);⑦欄位——`origin.kind`、`session.append` 依 `door` 篩、`spawn` 記 `child`、`notebook_path`(邊界 F7 F8、接手 F2、正確性小項);⑧保留——`lumos events --prune` 與只看資料夾層、REVISIT(邊界 F10、正確性 F7、架構 F1 的保留半);⑨會談結束——先寫再 `next`、用事件自己的 `sessionId`(接手 F5、邊界 F2 場景 C、正確性小項);⑩落點與慣例——enforcement 列改進 `Systems/hook信任邊界`、`ev` 取代 `kind` 避免與 hook 事件帳同名異義、讀取指令三段式與回傳碼、`.gitignore` 內容同 `_note_audit_work_dir`、登記處、slim 與子模組界線、新頂層資料夾不進三份名單(架構 F1 F4 F5 F6、接手 F10)。
  - 編排者裁定一處:接手 F8 第三點「回退後外掛從快取繼續載入並寫事件帳」與官方說明不符(`reference.md` 第 72 行:資料夾型市集直接讀來源資料夾、不讀安裝拷貝),該小點不採信;同條其餘兩點(未裝 claude 誤報、`--scope`)與回退順序照折。
  - 架構 F1 原報 major/blocking 否,兩欄矛盾,退回該席重判為 major/blocking 是(紀錄在席報告內)。
  - 鏡像核對(便宜席,材料含席報告目錄):39 項已處理 34、部分 5、未處理 0、相反 0;修補自己引進 7 個新洞,已補:外掛步驟狀態獨立不併進 `_sync_global_hooks` 回傳、輸出走向;`_lumos_src()` 的適用範圍寫明;先解位置再取緩衝;讀取端與 enforcement 用 `_events_root` 找主 checkout(新增 S12);非 git 與暫時失敗分開判、5 分鐘重試間隔;子代理的回合框法;塊檔排序規則;市集 source 必須是相對路徑(S9);mod 自己的並行與重新載入測試(新增 S13);prune 刪檔進實務隱患;決策 d2 以 d3 取代(來源改用 `_lumos_src()`)。

