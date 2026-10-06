severity: minor

整體很一致。沒有發現第二種做法,也沒有跨層直呼。唯一不一致是 `scripts/lumos` 裡一處訊息沒走既有的共用函式(F1)。TS 外掛沒有對應的 idioms skill,寫「無」。Python 端我對照了 `python-idioms` 慣例,沒有牴觸。

### 問 1 分層與依賴方向:一致
- `lumos-guard` 的目錄結構跟 `lumos-ledger` 一樣:`.claude-plugin/plugin.json`、`hooks/hooks.json`(同為 `{ "modules": ["./register.ts"] }`)、`hooks/register.ts`、`hooks/*.test.ts`、`tsconfig.json`(同為 extends `./.claude-plugin/types/tsconfig.json`)。對照 `mods/claude/lumos-ledger/hooks/register.ts:1`。
- 核心邏輯放在 `createGuard`,I/O 用 `Io` 型別注入,`makeIo($)` 在最外層組真實實作,`register` 只掛事件。這跟 ledger 的 `createLedger(io)` + `Io` + `register` 同一種分層。對照 `register.ts:30-45`(`createLedger`)與檔尾的 `register`。
- 測試用假 `Io` 測規則本身,跟 `ledger.test.ts` 的 `fakeIo()` 做法相同。
- 新增的 `spawnFields` 是純函式,從 `onSpawn` 抽出來單獨測。這跟 ledger 既有的 `toolExtra`、`pickMain` 抽法同型。
- Python 端的 `_sync_claude_plugin` 與 `_teardown_claude_plugin` 仍在原本「Claude 外掛」那一段,呼叫方向沒變。
- 外掛清單是 `_LUMOS_PLUGINS` 元組加 `_PLUGIN_RANK`。`_claude_json`、`_claude_do`、`_lumos_plugin_wait` 都是沿用的舊函式,只改名。

### 問 2 命名與錯誤處理:大致一致,一處不一致(F1)
- 命名:`_ledger_*` 整批改成 `_lumos_plugin_*`、常數改成 `_LUMOS_*`,前綴有統一。測試名 `t_install_registers_guard_plugin`、`t_guard_plugin_files_valid` 對應既有的 `t_install_registers_ledger_plugin`、`t_ledger_plugin_files_valid`。
- 給人看的訊息:guard 的 `why()` 與 `BASH_ERROR` 是三段式,第三段是獨立一行的做法。Python 端沿用既有的 `✓` / `⚠` 單行風格,跟 `_sync_msg` 一樣。
- TS 外掛的錯誤處理:ledger 沒有 `.catch`,出錯都在各 handler 內 `try {…} catch { /* 同上 */ }`。guard 同樣在 handler 內 try/catch,另外多掛 `.catch`。這是擋人鉤子才需要的(`tool.call` 與 `agent.spawn` 出錯時引擎會直接跳過、等於放行),而且 `t_guard_plugin_files_valid` 有機械檢查。我判為「結構對、有理由」,不列 finding。

### F1 無來源的略過訊息繞過共用函式
severity: minor
blocking: 否 — 命名/訊息跟鄰居不一致,但結構是對的
引句:「print(f"  (略過 Claude 外掛:lumos 來源 repo 沒有 .claude-plugin/marketplace.json——{src})")」
對照: `scripts/lumos:21925`(diff 所在段落,`_plugin_sync_msg` 的 no-source 分支)

- 外掛步驟的「狀態對應給人看的一行」本來都走 `_plugin_sync_msg(state, detail)`。
- 這次 `_sync_claude_plugin` 在「整個來源 repo 沒有市集檔」這個分支,把訊息直接寫成字面字串。同一個函式下面的逐支 `no-source` 分支(來源有市集檔、但沒列該外掛)卻走 `_plugin_sync_msg("no-source", …, pid)`。
- 結果同一個狀態 `no-source` 有兩處產生訊息,措辭已經分叉:一處是「沒有 .claude-plugin/marketplace.json」,另一處是「.claude-plugin/marketplace.json 沒有它」。
- 改回 `_plugin_sync_msg("no-source", str(src))` 即可。
- 這是同一條狀態機的兩處出口,不是新的做法,所以不到 major。

### 問 3 第二種做法:無
- 沒有自創工具函式:市集查詢、安裝等待、使用者範圍判定都是舊函式改名,沒有另起一套。
- `_lumos_plugin_listed` 是新函式,但專案裡原本沒有任何函式讀 `marketplace.json` 的內容,只有 `is_file()` 檢查(`scripts/lumos:23887`)。所以不算重造鄰居已有的功能。
- 測試仍用既有的 `_fake_claude_env`、`_with_env`、`check`、`_need_src`、`_load_lumos_inproc`。偽 `claude` 腳本只多了兩個環境變數(`FAKE_CLAUDE_FAIL_ID`、`FAKE_CLAUDE_INSTALL_NOOP`),是在原有機制上擴充,沒有另一套測試寫法。
- 外掛結構(`hooks.json` 載入單一 `register.ts`、`plugin.json` 欄位)沒有出現第二種。

總結:最嚴重 minor,blocking 0 條
