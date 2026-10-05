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
  - Systems/codex-harness
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
    valid: true
---
# Lumos事件帳_計劃

白話:Lumos 要判斷「AI 這一輪做了什麼」(改了哪些檔、跑了哪些測試、成不成功、派了哪些子代理),目前只能事後去解析 Claude Code 與 Codex 的逐字稿。逐字稿官方明說不是穩定介面,格式一變判斷就靜默失效(2026-10-05 實測:Codex 收工檢查只認 0.144.1/0.153.2,本機 0.160.0 每次都略過);有些情境逐字稿根本不落地(從 Claude 開出來的終端機、互動會談的子代理)。Claude Code 2.1.289 的 mod(外掛裡的函式 hook)可以在行程內直接看到結構化的回合、工具呼叫與子代理。這份計劃做一個只觀察的 mod,把這些寫成 Lumos 自己的事件帳,再給一個唯讀的讀取指令;之後的收工檢查、接手視圖、推播量測改讀它(各自另案)。

依據:Enzo 2026-10-05 在「Hook Refactor」會談選定方向(Claude mod 能讓治理切得更細,不必遷就 Codex),地毯式對照圖譜約 70 條限制後排為第 1 名;前提由 [[Verification/2026-10-05_Claude-mod能力實測]] 實測成立。

PRIOR-ART: 最小解在 Lumos 自己這一層,資料源借平台。①寫入慣例借本 repo 既有的 hook 事件帳(`_hookevent.py`):放 repo 樹內 `governance/runtime/`、只寫在成功點、觀測壞掉不影響本業。忽略設定不靠消費專案的 `governance/.gitignore`(init 只在那個檔不存在時才寫 `runtime/`,既有檔不補,calc-ios 就因此提交過 hook 事件帳),改借 `_note_audit_work_dir` 的做法:第一次寫入時在事件帳資料夾放一個內容只有 `*` 的 `.gitignore`,讓它自己忽略自己。分段塊檔則是新做法,只借位置與 fail-open 慣例。②檔案切塊借日誌系統的分段檔(Kafka segment、logrotate):每次寫一個新塊檔,不重寫舊檔,避開 mod 檔案 API 沒有附加寫入、單次寫入上限 4 MiB 的限制。③資料源用平台的 mod 事件(`turn.start`、`turn.complete`、`tool.call`、`agent.spawn`、`session.append`),不自己解析逐字稿。④安裝借 Claude Code 自己的外掛市集機制(`claude plugin marketplace add` + `claude plugin install`),實測在隔離設定目錄裝得起來、`claude -p` 不帶參數也載入。
RETIRE-IF: 任一成立就撤掉或重想:①上線兩個月內沒有任何消費端(收工檢查、接手視圖、推播量測)改讀它(機械數:`grep -rn "_events_read" scripts/` 只剩讀取指令自己);②Claude Code 連續兩個版本讓 mod 事件改名或失效,而官方仍沒有穩定承諾;③官方提供穩定的結構化事件匯出(例如逐字稿宣告為穩定介面),那時改讀官方的。
REVISIT:2026-12-05 量 RETIRE-IF ①,並重跑一次 [[Verification/2026-10-05_Claude-mod能力實測]] 的最小實驗確認 mod 事件沒變

## 範圍

- **做**:
  1. mod `lumos-ledger`:放 `mods/claude/lumos-ledger/`(`.claude-plugin/plugin.json`、`hooks/hooks.json`、`hooks/register.ts`),只觀察、不擋、不改、不注入。
  2. repo 根放市集檔 `.claude-plugin/marketplace.json`,市集名 `lumos-toolchain`,只列這一個外掛。
  3. 事件帳:寫在會談所在 git repo 頂層的 `governance/runtime/events/<會談編號>/<塊序號>.jsonl`;只在頂層有 `docs/*-knowledge/` 時寫;`governance/runtime/events/.gitignore`(內容 `*`)由 mod 第一次寫入時補上。
  4. 讀取:`scripts/lumos` 加 `_events_read(root, session)` 與唯讀指令 `lumos events [--session <編號>] [--json]`(沒給編號就列最近的會談)。
  5. 安裝:`lumos install` 偵測得到 `claude` 指令、且執行中的 `scripts/lumos` 所在 repo 有 `.claude-plugin/marketplace.json` 時,加市集並安裝外掛(使用者層),已裝過就改跑更新;`lumos uninstall` 移除(`teardown` 經由它,不另寫)。
  6. `lumos enforcement` 加一列「事件帳」:Claude 顯示已安裝且近期有事件 / 已安裝但近期沒有 / 沒裝 / 無法判斷;Codex 顯示「不支援」。
- **不做**:消費端改讀(收工檢查、接手視圖、推播量測,各自另案);任何會改變 AI 行為的事(擋、改寫、注入);Codex 對應(平台沒有同等事件);實驗用 mod 的「讓位」功能。

落點:新開 `Systems/lumos事件帳`(`lumos new system lumos事件帳 --code mods/claude/lumos-ledger/hooks/register.ts --code mods/claude/lumos-ledger/hooks/hooks.json --code mods/claude/lumos-ledger/.claude-plugin/plugin.json --code .claude-plugin/marketplace.json`),管 mod 與市集檔;`scripts/lumos` 裡的改動依功能寫進既有的家:安裝與移除進 `Systems/lumos-cli-lifecycle`,`lumos events` 讀取進 `Systems/lumos-cli-read`,enforcement 那一列進 `Systems/codex-harness`。

## 做法

### 1. 事件與格式(第 1 版)

每行一筆 JSON,共同欄位:`v`(固定 1)、`ts`(ISO 8601 帶時區)、`session`、`turn`(回合編號,子代理也有自己的)、`agent`(子代理編號,主會談為 null)、`kind`。

| kind | 來自哪個 mod 事件 | 額外欄位 |
|---|---|---|
| `turn_start` | `turn.start` | `origin`:這一回合的提示是誰送的,取最近一筆 `session.append` 的 prompt 列的來源原樣字串(實測看過 `unclassified`、`task-notification`、`coordinator`);`prompt_len` |
| `turn_end` | `turn.complete` | `reason`:`answer` / `aborted` / `refusal` / `error` |
| `tool` | `tool.call`(等工具跑完) | `tool`、`ok`(`isError` 不是 true 且沒被拒)、`denied`、`paths`(工具輸入裡的 `file_path` / `path`,有才記)、`cmd`(Bash 指令前 500 字) |
| `spawn` | `agent.spawn` | `agent_type`、`model`(引擎解析後的實際模型)、`denied` |
| `ledger_error` | mod 自己 | `what`:上一次寫塊失敗的原因(只記一次,寫進下一塊) |

不記:提示全文、模型回應、工具結果內容(要內容就去讀逐字稿;事件帳只回答「發生了什麼」)。

### 2. 寫入

- mod 記憶體裡一個緩衝;遇到 `turn_end`、緩衝滿 50 筆、或 `session.end` 時,把緩衝寫成一個新塊檔(序號遞增、補零 6 位),清空緩衝。不重寫舊塊。
- 第一次要寫之前,用 `$.process.run(["git","rev-parse","--show-toplevel"])` 找頂層,再用 `$.fs.list` 看 `docs/` 底下有沒有 `*-knowledge`;沒有就整個會談都不寫(結果記在模組變數,不每次查)。有的話,`governance/runtime/events/.gitignore` 不存在就先寫一個內容 `*` 的檔,再寫塊檔。
- 寫失敗:吞掉,記下原因,下一塊開頭補一筆 `ledger_error`;不重試同一塊(避免越積越大)。
- 所有 hook 一律先 `next(e)`、照原樣回傳結果;mod 例外時引擎本來就會跳過它(fail-open)。

### 3. 讀取

- `_events_read(root, session)`:依塊序號讀、合併;壞行與 `v` 不是 1 的行略過並各自計數;回傳事件清單與兩個計數。
- `lumos events`:沒給 `--session` 就列最近 10 個會談(會談編號、最後事件時間、回合數、工具呼叫數、失敗數);給了就逐筆印。`--json` 給機器讀。沒有事件帳時回 0,印「沒有事件帳」與可能原因(mod 沒裝、這不是 Claude 會談、repo 沒有圖譜)。

### 4. 安裝與移除

- `lumos install`:兩個條件都成立才做——`shutil.which("claude")` 找得到;執行中這支 `scripts/lumos` 的上兩層(`cmd_install` 用的來源 repo)有 `.claude-plugin/marketplace.json`(消費專案 vendored 的 lumos 沒有這個檔,不能把專案自己當市集加進去)。依序跑 `claude plugin marketplace add <來源 repo>`、`claude plugin install lumos-ledger@lumos-toolchain`;`claude plugin list --json` 已列出這個外掛時改跑 `claude plugin update lumos-ledger@lumos-toolchain`(讓重跑 install 能拿到新版 mod)。「已加過市集」怎麼判成功,以退出碼加輸出判斷,實際訊息在實作時用真的 `claude` 量一次、寫進 Systems 節點;測試用假的 `claude` 腳本涵蓋。任何一步失敗只印一行(含錯誤輸出第一行),不改 `cmd_install` 的回傳碼。任一條件不成立就印一行略過。
- 放在 `cmd_install` 開頭的探針拒絕(`_refuse_if_probe`)之後,所以探針模式下安裝與移除都照既有規則被擋,不另加。`lumos update`、`bootstrap` 走的 `_sync_global_hooks` 不碰外掛(要新版就重跑 `lumos install`)。
- `lumos uninstall`(`teardown` 第三步就是呼叫它):`claude plugin uninstall lumos-ledger@lumos-toolchain`、`claude plugin marketplace remove lumos-toolchain`,失敗只印一行,並附上這兩個手動移除指令。
- 子行程逾時 60 秒。

### 5. enforcement

- 判定順序(先便宜後貴):本 repo `governance/runtime/events/` 最近 7 天有塊檔 → 已安裝且近期有事件,不再查別的;沒有 → 才跑 `claude plugin list --json`(逾時 3 秒),有 `lumos-ledger@lumos-toolchain` 且 enabled → 已安裝但近期沒有;沒有 → 沒裝;`claude` 指令不在、逾時或輸出解析不了 → 無法判斷。理由:進場 hook 每次開場都跑 `lumos enforcement --json`,`claude plugin list` 本機實測約 0.9 秒,常態路徑不該付這筆。
- 狀態值只用三種:已安裝且近期有事件=`active`;已安裝但近期沒有=`stale`;沒裝、無法判斷、Codex 不支援=`unknown`。絕不使用 `inactive` 或 `degraded`——開場提醒只點名這兩種(`lumos-entry-hook.py` 的 `down` 清單),enforcement 的分母也只排除 `unknown`、`stale`、`registered-trust-unknown`;用錯就會讓沒裝 mod、只用 Codex 的人每次開場都被唸,也會讓 enforcement 印出「請重跑 lumos install --force」。

## 條款

- [S1] 當 Claude Code 會談(互動或 `claude -p`)在有圖譜的 git repo 裡跑、`lumos-ledger` 已安裝,事件帳應在 `governance/runtime/events/<會談編號>/` 下出現塊檔,含 `turn_start`、`turn_end`、`tool`、`spawn` 四種,失敗的工具呼叫 `ok` 為 false,子代理的事件帶 `agent` 編號 [manual: 本機互動會談與 claude -p 各跑一場含失敗指令與子代理的任務,lumos events 比對]
- [S2] 當會談所在目錄不在 git repo 裡、或頂層沒有 `docs/*-knowledge/`,mod 應不寫任何檔 [manual: 在無圖譜的臨時 git repo 跑一場 claude -p,確認沒有 events 資料夾]
- [S3] 當塊檔寫入失敗,會談應照常進行,下一塊開頭應有一筆 `ledger_error` [manual: 把 events 資料夾換成唯讀後跑一場,恢復後再跑一回合,看下一塊]
- [S4] 當 `lumos events --session <編號>` 讀一個會談,應依塊序號合併,壞行與版本不是 1 的行略過並分別計數印出 [test:t_events_reader_merges_chunks]
- [S5] 當沒有事件帳,`lumos events` 應回 0 並印「沒有事件帳」與可能原因 [test:t_events_reader_no_ledger]
- [S6] 當 `lumos install` 偵測得到 `claude` 指令且來源 repo 有市集檔,應依序呼叫加市集與安裝外掛兩個指令(外掛已列出時改呼叫更新),任一步失敗只印一行、回傳碼不變;偵測不到 `claude` 或來源 repo 沒有市集檔時應略過並印一行 [test:t_install_registers_ledger_plugin]
- [S7] 當 `lumos uninstall` 執行(含 `teardown` 經由它),應呼叫移除外掛與移除市集兩個指令,失敗只印一行並附上兩個手動移除指令 [test:t_teardown_removes_ledger_plugin]
- [S8] 當 `lumos enforcement` 執行,Claude 列應多一行事件帳狀態,已安裝且近期有事件為 `active`、已安裝但近期沒有為 `stale`、沒裝或無法判斷為 `unknown`,Codex 列為 `unknown` 並註明不支援;這一列不得出現 `inactive` 或 `degraded`;近期有事件時不得呼叫 `claude` 指令 [test:t_enforcement_ledger_row]
- [S9] 當檢查 repo 內的外掛檔,市集檔與外掛描述檔應是合法 JSON、市集的 source 指到存在的外掛資料夾、mod 原始碼裡寫檔的路徑只在 `governance/runtime/events/` 底下、不呼叫任何會改變行為的 API(拒絕、改寫輸入、注入) [test:t_ledger_plugin_files_valid]

## 回退

- 移除外掛:`claude plugin uninstall lumos-ledger@lumos-toolchain` 與 `claude plugin marketplace remove lumos-toolchain`(`lumos uninstall` 會做)。
- 程式:刪 `mods/claude/lumos-ledger/`、`.claude-plugin/marketplace.json`;`scripts/lumos` 拿掉 `_events_read`、`events` 指令、install / uninstall 的兩段呼叫、enforcement 那一列;刪 S4–S9 的測試。
- 已寫出的事件帳在 `governance/runtime/events/`,本來就不進版控,留著無害,要清就刪資料夾。
- 本計劃不改任何既有 hook 與閘的行為,回退不影響它們。

## 實務隱患

- 已排除:金流:只記錄回合與工具呼叫,不碰任何付費、計費或額度流程。
- 已排除:對外送出:事件帳只寫在本機 repo 內不進版控的資料夾,mod 不呼叫任何網路 API、不送訊息給其他會談。
- 不可逆:安裝會改使用者層的 Claude 設定(加一個市集、裝一個外掛)。可以用 `lumos uninstall` 撤回;風險是 Claude 外掛指令的參數或行為改了,移除失敗而殘留——回退節列了手動移除的兩個指令,`lumos uninstall` 失敗時也印出這兩個指令。
- 已排除:守衛面:mod 不擋、不改、不注入,不碰任何既有 hook 與 git 閘;enforcement 只多一列資訊,且明定不算進降級(見做法第 5 節)。

## 誠實界線

- 只有 Claude Code;Codex 沒有同等事件,enforcement 明講不支援。
- mod API 沒有找到穩定承諾(型別檔約 14,000 行、說明都沒寫);官方改版可能讓事件改名或失效。上面的 REVISIT 會重跑最小實驗。
- fail-open:mod 出錯時引擎跳過它,那段時間沒有事件;緩衝最多 49 筆在當機時遺失。事件帳只能當「有記到的就是真的」,不能當「沒記到就沒發生」。
- `cmd` 記 Bash 指令前 500 字,可能含秘密;跟本機逐字稿同一等級的暴露面,放在不進版控的資料夾。若被強制加進版控會外洩——沒有機械擋。REVISIT:2026-12-05 一併查 `git ls-files governance/runtime` 在本 repo 與 calc-ios 是否為空
- `lumos install` 多依賴 Claude 的指令列工具;沒裝 Claude 的機器(只用 Codex)會略過。
- 這些 mod 介面只讀過型別檔、沒有實測:`session.end`、`$.process.run`、`$.fs.list`、結束原因 `aborted` 與 `refusal`、單次寫入 4 MiB 上限;實作時第一個測試就要逐一跑到(見 S1、S3)。
