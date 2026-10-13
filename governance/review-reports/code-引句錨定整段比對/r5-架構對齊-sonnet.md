severity: minor

我沒有找到引入第二種做法或跨層直呼的地方,所以沒有 blocking 條。除了下面兩條 minor,其餘各項都用對了既有函式。

**1. 計劃筆記留有「比較模式」的殘文**
severity: minor
blocking: 否
引句:「寫側求 `kind` 那一次與比較模式同一規則(r2 架構對齊席)」
file: `docs/lumos-toolchain-knowledge/Projects/引句錨定整段比對_計劃.md:72`
- 人裁拿掉 `--compare-rules` 後,程式與測試的殘骸已清乾淨(`scripts/lumos` 與 `scripts/test_lumos.py` 都搜不到 compare 相關字樣)。
- 計劃第 72 行這句還在引用已不存在的「比較模式」,「同一規則」現在沒有對照對象,下一個讀的人會去找一個不存在的路徑。
- 程式碼裡 `_quote_block_note` 的註解已改成「處置閘與寫側」,筆記沒跟上。這句應改成只講處置閘與寫側。
- 同一份計劃的第 88 行對這件事是對的,它寫了「不做成指令」。

**2. ⚠ 事件 note 裡 `report=` 路徑沒跳脫,`quote=` 片段有跳脫**
severity: minor
blocking: 否
引句:「return (f"quote-rule:{write_rule} kind={kind} cats={','.join(cats)} report={report} report_sha={sha12} "」
file: `scripts/lumos:25847`
- 同一條 note 裡,審查席可控的片段已改用 `_kill_esc` 跳脫,但 `report=` 這個路徑欄位仍原樣寫入。
- 控制字元落進 JSON 帳不會出事,因為 `_append_governance_log` 用 `json.dumps` 逐筆寫入。
- 只有在 `lumos gov` 把 note 印到終端時,這個路徑才可能帶方向覆寫字元。
- 同檔其他 canary blocked 事件的 note 都不放路徑,所以這是本分支獨有的欄位,我沒有既有做法可以對照。
- 我沒有查 `gov` 的顯示端有沒有再過 `_esc_clean`,所以標 ⚠。若顯示端已消毒,這條可撤。
- 這一行是上一輪就有的,不是本輪修補新增的。

**核對過、沒有問題的項目**
- **`_kill_esc` 取代自寫過濾**:`_kill_esc` 在 `scripts/lumos:17167`,類別走共用的 `_PATH_SPECIAL_CATS`(`scripts/lumos:36167`)。這是同檔專給不加引號字串用的無損跳脫,也已被 `_lens_visible` 和 `_kill_show` 重用。換過去之後,分支上不再有自寫的 Cf/Co 過濾。
- **診斷行的組合**:`_path_special_chars` 加 `_drift_sh(node=True)` 的組合,跟 `_drift_fix_hint`(`scripts/lumos:40003`)的「路徑含特殊字元就不印可照貼的指令」同一做法,是對的。
  - 直接呼叫 `_path_special_chars`(預設 `surrogate=True`)沒問題:這裡路徑非 UTF-8 時本來就不該印可貼指令。`_drift_m1_special_chars` 只是它的薄包裝。
  - 1000 字上限是新寫的常數,`_drift_fix_hint` 用的是 4000。兩個上限不一致,但性質是風格,我不列。
- **`[disposal] ` 前綴**:新診斷行的前綴跟同一區塊其他行(例如 `scripts/lumos:26534`)一致。
- **事件記帳**:寫側擋下事件用 `_gate_event_or_warn(..., "canary", "blocked", ..., hard=True)`,跟 `scripts/lumos:10936`、`10946` 同一寫法。`id=` 隨機碼也沿用既有做法。
- **報告指紋**:`report_sha` 取 `_validated_sha`(`scripts/lumos:10909`),跟既有的雜湊驗證機制共用,沒有新開第二套。
- **測試注入**:`_qfs_lumos` 用 `SourceFileLoader` 在子程序載入模組,跟 `scripts/test_lumos.py` 裡反覆出現的寫法(例如 662、681、780 行)同形。`m._kill_esc` 的 `mock.patch` 沿用先前對 `_esc_clean` 的同款手法,沒有新引入注入方式。
- **變更前後一致**:`MemoryError` 往外丟的處理在處置閘與寫側都一致,沒有因為拿掉比較模式而出現不一致的分支。

總結:最高等級 minor,blocking 共 0 條
