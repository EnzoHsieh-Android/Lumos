preflight-4: ran

# r1 收貨紀錄(lumos事件帳)

## 前掃(便宜席,sonnet,2026-10-05)

- ①②③ 與存在類命中直接修真檔,不算 findings:①-1 session.end 未實測、①-2 未實測介面、①-3 狀態值未定義(併入④-3);②-1 lands_in 新節點未寫開法(補落點段)、②-3 teardown 經 uninstall;③-1 範圍6 與 S8 狀態數不一、③-2 不進版控前提(併入④-2)、③-3 teardown 不另寫。
- ④ 語意類逐條(修真檔,改前→改後見下表):④-2 init 只在 governance/.gitignore 不存在時寫 runtime/(scripts/lumos `_init` 段 `if not gov_ignore.exists()`)→ 改成 mod 自寫 events/.gitignore,借 `_note_audit_work_dir`;④-3 開場提醒只點名 inactive/degraded(lumos-entry-hook.py `down` 清單)、分母排除 unknown/stale/registered-trust-unknown → 指定 active/stale/unknown 三值,常態不呼叫 claude;④-4 探針拒絕在 cmd_install 開頭,安裝與移除都擋 → 改句;④-5 vendored 的 lumos 來源 repo 是專案自己、update/bootstrap 不碰外掛 → 加市集檔條件、重跑 install 改跑 update;④-6 重複 add/install 的退出碼未驗 → 改成實作時實測、測試用假 claude。④-1 成立不改。
- 碰核心裁定:d1、d2 未被推翻。④-2、④-3 動到範圍第 3、6 項的寫法(位置不變、只補忽略檔;狀態值對齊程式),★交第一輪席位照常審,不當已裁★。
- refcheck:`governance/runtime/`、`governance/runtime/events/` 報 missing——執行期才建、不進版控的資料夾,預期,不改。

## 前掃改前→改後

### e1
改前:①寫入慣例借本 repo 既有的 hook 事件帳(`_hookevent.py`):放 repo 樹內 `governance/runtime/`(消費專案 init 時已忽略這層)、只寫在成功點、觀測壞掉不影響本業。

改後:①寫入慣例借本 repo 既有的 hook 事件帳(`_hookevent.py`):放 repo 樹內 `governance/runtime/`、只寫在成功點、觀測壞掉不影響本業。忽略設定不靠消費專案的 `governance/.gitignore`(init 只在那個檔不存在時才寫 `runtime/`,既有檔不補,calc-ios 就因此提交過 hook 事件帳),改借 `_note_audit_work_dir` 的做法:第一次寫入時在事件帳資料夾放一個內容只有 `*` 的 `.gitignore`,讓它自己忽略自己。分段塊檔則是新做法,只借位置與 fail-open 慣例。

### e2
改前:3. 事件帳:寫在會談所在 git repo 頂層的 `governance/runtime/events/<會談編號>/<塊序號>.jsonl`;只在頂層有 `docs/*-knowledge/` 時寫。

改後:3. 事件帳:寫在會談所在 git repo 頂層的 `governance/runtime/events/<會談編號>/<塊序號>.jsonl`;只在頂層有 `docs/*-knowledge/` 時寫;`governance/runtime/events/.gitignore`(內容 `*`)由 mod 第一次寫入時補上。

### e3
改前:- 第一次要寫之前,用 `$.process.run(["git","rev-parse","--show-toplevel"])` 找頂層,再用 `$.fs.list` 看 `docs/` 底下有沒有 `*-knowledge`;沒有就整個會談都不寫(結果記在模組變數,不每次查)。

改後:- 第一次要寫之前,用 `$.process.run(["git","rev-parse","--show-toplevel"])` 找頂層,再用 `$.fs.list` 看 `docs/` 底下有沒有 `*-knowledge`;沒有就整個會談都不寫(結果記在模組變數,不每次查)。有的話,`governance/runtime/events/.gitignore` 不存在就先寫一個內容 `*` 的檔,再寫塊檔。

### e4
改前:6. `lumos enforcement` 加一列「事件帳」:Claude 顯示已安裝 / 近期有事件 / 沒裝;Codex 顯示「不支援」。

改後:6. `lumos enforcement` 加一列「事件帳」:Claude 顯示已安裝且近期有事件 / 已安裝但近期沒有 / 沒裝 / 無法判斷;Codex 顯示「不支援」。

### e5
改前:- Claude 列加「事件帳」:`claude plugin list` 有 `lumos-ledger@lumos-toolchain` 且 enabled → 已安裝;再看本 repo `governance/runtime/events/` 最近 7 天有沒有塊檔 → 近期有事件 / 近期沒有。`claude` 指令不在 → 「無法判斷」。 ⏎ - Codex 列:「不支援(平台沒有同等事件)」。 ⏎ - 這一列只是資訊:不論哪一種狀態,都不算進 enforcement 的降級計數,也不讓開場提醒多出警報(沒裝 mod、只用 Codex 的人不該每次開場都被唸)。 ⏎ 

改後:- 判定順序(先便宜後貴):本 repo `governance/runtime/events/` 最近 7 天有塊檔 → 已安裝且近期有事件,不再查別的;沒有 → 才跑 `claude plugin list --json`(逾時 3 秒),有 `lumos-ledger@lumos-toolchain` 且 enabled → 已安裝但近期沒有;沒有 → 沒裝;`claude` 指令不在、逾時或輸出解析不了 → 無法判斷。理由:進場 hook 每次開場都跑 `lumos enforcement --json`,`claude plugin list` 本機實測約 0.9 秒,常態路徑不該付這筆。 ⏎ - 狀態值只用三種:已安裝且近期有事件=`active`;已安裝但近期沒有=`stale`;沒裝、無法判斷、Codex 不支援=`unknown`。絕不使用 `inactive` 或 `degraded`——開場提醒只點名這兩種(`lumos-entry-hook.py` 的 `down` 清單),enforcement 的分母也只排除 `unknown`、`stale`、`registered-trust-unknown`;用錯就會讓沒裝 mod、只用 Codex 的人每次開場都被唸,也會讓 enforcement 印出「請重跑 lumos install --force」。 ⏎ 

### e6
改前:Claude 列應多一行事件帳狀態(已安裝且近期有事件 / 已安裝但近期沒有 / 沒裝 / 無法判斷),Codex 列應顯示不支援;這一列的任何狀態都不應讓 enforcement 的整體狀態或開場提醒變成降級 [test:t_enforcement_ledger_row]

改後:Claude 列應多一行事件帳狀態,已安裝且近期有事件為 `active`、已安裝但近期沒有為 `stale`、沒裝或無法判斷為 `unknown`,Codex 列為 `unknown` 並註明不支援;這一列不得出現 `inactive` 或 `degraded`;近期有事件時不得呼叫 `claude` 指令 [test:t_enforcement_ledger_row]

### e7
改前:5. 安裝:`lumos install` 偵測得到 `claude` 指令時,加市集並安裝外掛(使用者層);`lumos uninstall`、`teardown` 對稱移除。

改後:5. 安裝:`lumos install` 偵測得到 `claude` 指令、且執行中的 `scripts/lumos` 所在 repo 有 `.claude-plugin/marketplace.json` 時,加市集並安裝外掛(使用者層),已裝過就改跑更新;`lumos uninstall` 移除(`teardown` 經由它,不另寫)。

### e8
改前:- `lumos install`:`shutil.which("claude")` 找得到才做,依序跑 `claude plugin marketplace add <lumos 來源 repo>`、`claude plugin install lumos-ledger@lumos-toolchain`;已加過或已裝過算成功;任何一步失敗只印一行(含錯誤輸出第一行),不讓整個安裝失敗。找不到 `claude` 就印一行略過。

改後:- `lumos install`:兩個條件都成立才做——`shutil.which("claude")` 找得到;執行中這支 `scripts/lumos` 的上兩層(`cmd_install` 用的來源 repo)有 `.claude-plugin/marketplace.json`(消費專案 vendored 的 lumos 沒有這個檔,不能把專案自己當市集加進去)。依序跑 `claude plugin marketplace add <來源 repo>`、`claude plugin install lumos-ledger@lumos-toolchain`;`claude plugin list --json` 已列出這個外掛時改跑 `claude plugin update lumos-ledger@lumos-toolchain`(讓重跑 install 能拿到新版 mod)。「已加過市集」怎麼判成功,以退出碼加輸出判斷,實際訊息在實作時用真的 `claude` 量一次、寫進 Systems 節點;測試用假的 `claude` 腳本涵蓋。任何一步失敗只印一行(含錯誤輸出第一行),不改 `cmd_install` 的回傳碼。任一條件不成立就印一行略過。 ⏎ - 放在 `cmd_install` 開頭的探針拒絕(`_refuse_if_probe`)之後,所以探針模式下安裝與移除都照既有規則被擋,不另加。`lumos update`、`bootstrap` 走的 `_sync_global_hooks` 不碰外掛(要新版就重跑 `lumos install`)。

### e9
改前:- `lumos uninstall` / `teardown`:`claude plugin uninstall lumos-ledger@lumos-toolchain`

改後:- `lumos uninstall`(`teardown` 第三步就是呼叫它):`claude plugin uninstall lumos-ledger@lumos-toolchain`

### e10
改前:- 子行程逾時 60 秒;探針模式(`LUMOS_PROBE`)照既有規則拒絕安裝。

改後:- 子行程逾時 60 秒。

### e11
改前:- [S6] 當 `lumos install` 偵測得到 `claude` 指令,應依序呼叫加市集與安裝外掛兩個指令,任一步失敗只印一行、安裝整體照樣成功;偵測不到應略過並印一行 [test:t_install_registers_ledger_plugin]

改後:- [S6] 當 `lumos install` 偵測得到 `claude` 指令且來源 repo 有市集檔,應依序呼叫加市集與安裝外掛兩個指令(外掛已列出時改呼叫更新),任一步失敗只印一行、回傳碼不變;偵測不到 `claude` 或來源 repo 沒有市集檔時應略過並印一行 [test:t_install_registers_ledger_plugin]

### e12
改前:- [S7] 當 `lumos uninstall` 或 `teardown`,應呼叫

改後:- [S7] 當 `lumos uninstall` 執行(含 `teardown` 經由它),應呼叫

### e13
改前:## 做法 ⏎ 

改後:落點:新開 `Systems/lumos事件帳`(`lumos new system lumos事件帳 --code mods/claude/lumos-ledger/hooks/register.ts --code mods/claude/lumos-ledger/hooks/hooks.json --code mods/claude/lumos-ledger/.claude-plugin/plugin.json --code .claude-plugin/marketplace.json`),管 mod 與市集檔;`scripts/lumos` 裡的改動依功能寫進既有的家:安裝與移除進 `Systems/lumos-cli-lifecycle`,`lumos events` 讀取進 `Systems/lumos-cli-read`,enforcement 那一列進 `Systems/codex-harness`。 ⏎  ⏎ ## 做法 ⏎ 

### e14
改前:- `lumos install` 多依賴 Claude 的指令列工具;沒裝 Claude 的機器(只用 Codex)會略過。

改後:- `lumos install` 多依賴 Claude 的指令列工具;沒裝 Claude 的機器(只用 Codex)會略過。 ⏎ - 這些 mod 介面只讀過型別檔、沒有實測:`session.end`、`$.process.run`、`$.fs.list`、結束原因 `aborted` 與 `refusal`、單次寫入 4 MiB 上限;實作時第一個測試就要逐一跑到(見 S1、S3)。

