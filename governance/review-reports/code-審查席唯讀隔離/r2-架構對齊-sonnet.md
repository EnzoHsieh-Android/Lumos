severity: major

分層與依賴方向:沒有跨層直呼。錯誤處理與命名只有小處不一致。有一處引入第二種做法:`$.state` 持久化,而且同一個工具坑(熱重載後模組變數歸零)在事件帳外掛已有另一種處理。

## 問 1:分層與依賴方向

- **TS 外掛:一致。**
  - 核心邏輯放 `createGuard(io)`,I/O(`real`、`now`、`sleep`、`toast`,這次加的 `loadSeats`/`saveSeats`)由 `makeIo($)` 注入。這跟事件帳的 `createLedger(io)` 同一層次與同一方向。
  - 核心函式不直接碰 `$`,`$.state` 只出現在 `makeIo`。
  - 對照:`mods/claude/lumos-guard/hooks/register.ts:326-329`、`mods/claude/lumos-ledger/hooks/register.ts:259`。
- **Python 端:一致。**
  - 新增的 `_lumos_plugin_listed`、`_lumos_plugin_ensure`、`_teardown_claude_plugin` 改動,都只呼叫同段既有的 `_lumos_plugin_user`、`_lumos_plugin_market`、`_same_local_path`、`_plugin_sync_msg`。
  - `no-source` 訊息改走 `_plugin_sync_msg`,收斂到共用函式,比之前更貼近鄰居。
  - 對照:`scripts/lumos:22085-22095`、`scripts/lumos:21917`。

## 問 2:命名與錯誤處理

- **TS 端:一致。**
  - 擋下理由走 `why(...)` 三段式。
  - `.catch` 寫法跟事件帳「觀察壞掉不能影響本業」一樣不外拋,只是方向相反(守衛是 Bash 擋、其他放行)。
  - 對照:`mods/claude/lumos-guard/hooks/register.ts:232`、`mods/claude/lumos-ledger/hooks/register.ts:291`。
- **Python 端:例外元組一致。** `(RuntimeError, ValueError, OSError, subprocess.TimeoutExpired)` 跟同函式其他處一樣。

### F1 熱重載存活用 `$.state` 持久化,事件帳同一問題是接受歸零
severity: major
blocking: 是 — 引入第二種做法(第一次用 `$.state`)
引句:「外掛熱重載後(對照表從 `$.state` 讀回)執行中的審查席與它派的子代理應照擋」
對照: `mods/claude/lumos-guard/hooks/register.ts:328`(`$.state.get/set`)對照 `mods/claude/lumos-ledger/hooks/register.ts:259`(同樣面對「模組變數在重載時歸零」,選擇不存、讓新實例自己排序避撞名)。
- repo 內只有 guard 用 `$.state`,事件帳完全沒有,Grep 也找不到別處。
- 理由站得住:守衛失憶就等於放行,所以要存。
- 但這個理由只寫在計畫條款 S7,沒有進決策欄,也沒說明為何事件帳不跟進。
- 建議把「兩個外掛處理熱重載的方式不同、為什麼」補成決策,或給 `$.state` 一個共用的寫法。

### F2 types 合約檔與 `plugin.json` 的 `types` 欄位是第一次出現
severity: minor
blocking: 否 — 沒有第二條行為路徑,只是新增型別檔,且依附 F1
引句:「"types": "./types/index.d.ts"」
對照: `mods/claude/lumos-guard/.claude-plugin/plugin.json:5`(有)、`mods/claude/lumos-ledger/.claude-plugin/plugin.json`(無),`mods/claude/lumos-guard/types/index.d.ts`。
- 事件帳沒有 `types/`,全程用 `$: any`。
- guard 的 `index.d.ts` 用 `declare module 'claude-code'` 擴充 `PluginState`,但 `register.ts` 的 `$` 仍是 `any`,所以型別只被 `GuardSeat` 一個別名用到。
- 結構上是新增物,不是第二種流程。
- 若 F1 保留,這份合約檔該同步說明是「`$.state` 專用」。

## 問 3:第二種做法

- **`$.state` 持久化:**第一次出現,理由有但未記錄,見 F1。
- **types 合約檔:**第一次出現,見 F2。
- **`spawnEvent` 純函式給齊參數:**
  - 它在事件帳(`mods/claude/lumos-ledger/hooks/register.ts:333`),不在 guard,也不在這次 delta。
  - 而且它跟同檔的 `spawnFields`、`createLedger(io)` 是同一種「核心邏輯純函式化、接線只轉交」寫法。
  - 這是事件帳內部新加的抽法,但沒有跟既有做法並存的衝突,**不算第二種做法**。

### F3 「這是不是我們的市集」判斷在同函式出現第三份,形狀還不同
severity: minor
blocking: 否 — 結構對,只是同一條判準寫了兩種形狀
引句:「ours = bool(mk and mk.get("source") == "directory" and mk.get("path") and _same_local_path(mk["path"], src))」
對照: `scripts/lumos:22086`(新,三態 True/False/None)對照 `scripts/lumos:22095`(同函式 else 分支,內嵌 `mk is not None and ... and _same_local_path(...)`)。
- 同一個判斷在 `_teardown_claude_plugin` 裡有兩份寫法。
- 一份回三態,另一份是內嵌布林。
- 同檔既有 `_lumos_plugin_ensure_market`(`scripts/lumos:22018`)是第三處類似判斷。
- 一邊改了另一邊容易漏。

### F4 測試函式命名跟鄰居不同
severity: minor
blocking: 否 — 只是命名慣例
引句:「def t_lumos_plugin_install_review_fixes():」
對照: `scripts/test_lumos.py:70355` 對照 `scripts/test_lumos.py:69497`(`t_install_registers_ledger_plugin`)、`scripts/test_lumos.py:70217`(`t_install_registers_guard_plugin`)。
- 鄰居的名稱是「行為/對象」。
- 這支的名稱是審查輪次的產物 `review_fixes`,不描述行為。
- 圖譜條款 S9 已綁它,改名時要連同條款一起改。

總結:最嚴重 major,blocking 1 條
