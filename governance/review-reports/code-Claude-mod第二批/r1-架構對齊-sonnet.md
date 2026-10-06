severity: minor

## 問 1 分層與依賴方向:對齊
- 新外掛目錄結構與 lumos-ledger 一對一:plugin.json、hooks/hooks.json(內容同為 `{ "modules": ["./register.ts"] }`)、hooks/register.ts、tsconfig.json(同樣 extends .claude-plugin/types)、hooks/*.test.ts。對照 file: `mods/claude/lumos-ledger/hooks/hooks.json:1`、file: `mods/claude/lumos-ledger/tsconfig.json:2`。
- TS 層:純邏輯(withHandoff/hasMark)匯出供測試、register 只做接線,與 ledger 的 createLedger + register 分法相同。對照 file: `mods/claude/lumos-ledger/hooks/register.ts:303`。context.test.ts 用同一個 `claude-code/testing` 匯入,對照 file: `mods/claude/lumos-ledger/hooks/ledger.test.ts:1`。
- Python 安裝端:仍在 `_sync_claude_plugin` / `_teardown_claude_plugin` 同一段,沿用 `_claude_json`/`_claude_do`/`_same_local_path`,沒有跨層直呼。外掛清單 `_LUMOS_PLUGINS`、`_PLUGIN_RANK`、`worst = max(..., key=_PLUGIN_RANK.__getitem__)` 與 seat-guard 分支逐字相同(只差第二個 id),對照 file: `/Users/enzo/harness/lumos-toolchain-seat-guard/scripts/lumos:21887`。

## 問 2 命名與錯誤處理:大致對齊,有兩點小差
- 命名:`_ledger_*` 一律改成 `_lumos_plugin_*`、`_LEDGER_*` 改 `_LUMOS_*`,全檔無殘留引用(grep 確認),與 seat-guard 分支同名,對齊。
- 錯誤處理:安裝端仍是「例外 → 印 ⚠ 到 stderr、回 failed、附手動指令」,例外元組 `(RuntimeError, ValueError, OSError, subprocess.TimeoutExpired)` 與舊寫法一致。
- TS 失敗放行方式:ledger 在每個 handler 內自己 try/catch 吞錯,context 改用 `.catch(($, e, next) => next(e))` 鏈。這是專案內第一個用 `.catch` 的外掛(`grep '\.catch(' mods` 只有 context),手法不同但目的相同(失敗放行)。見 F2。

## 問 3 第二種做法:有一處重複驗證、一處待裁
- 市集檔等於外掛清單的斷言,舊的 `t_ledger_plugin_files_valid` 已改成比對 `_LUMOS_PLUGINS`,新的 `t_plugin_market_matches_list` 又做了一次同一件事。見 F1。
- 未動這次功能的測試標籤 S7 被改成 S4,見 F3(⚠)。

### F1 市集清單比對在兩支測試各做一次
severity: minor
blocking: 否 — 結構對、只是同一條不變量守在兩處,不是第二種做法
引句:「check("S9 市集列出的外掛恰好是外掛清單那幾支(lumos-ledger 是其中一支)」
對照:file: `scripts/test_lumos.py:71549`(t_ledger_plugin_files_valid 內)與 file: `scripts/test_lumos.py:71747`(t_plugin_market_matches_list)。新測試的逐支檢查(source 以 ./ 開頭、描述檔、hooks.json、名稱一致)與舊測試對 ledger 的檢查重疊,日後改清單要改兩處。

### F2 失敗放行改用 `.catch` 鏈,鄰居是 handler 內 try/catch
severity: minor
blocking: 否 — 失敗放行的語意一致,只是機制不同,且鄰居沒有「改寫事件」的外掛可對
引句:「.catch(($, e, next) => next(e))」
對照:file: `mods/claude/lumos-ledger/hooks/register.ts:303`(每個 handler 內 `catch { /* 同上 */ }`)。ledger 只觀察不改事件,context 會改 `instructions`,場景不同,⚠ 無既有做法可直接對,交編排者裁:是否要在計劃筆記註明 `.catch` 是改寫型外掛的標準寫法。

### F3 ⚠ 無關測試標籤 S7 改 S4
severity: minor
blocking: 否 — 只是標籤字串,不影響行為;疑為避免新條款編號 S4 與舊 S7 在同一檔衝突,判不準
引句:「check("S4 決策內容結尾裸冒號 → 加引號(標準 YAML 否則報錯)」
對照:file: `scripts/test_lumos.py:2400`。鄰居的條款標籤(例如 t_decision_add_standard_yaml_safe 的 `[S7]` docstring)沒有同步改,同檔出現 docstring S7、check 內 S4 的不一致;但本檔本來就多套 S 編號並存(file: `scripts/test_lumos.py:2323`),⚠ 交編排者確認這批改動是否為本功能必要。

總結:不對齊共 3 條,其中 major 0 條
