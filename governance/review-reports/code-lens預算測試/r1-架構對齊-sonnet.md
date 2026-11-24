severity: minor

我用更正後的範圍跑了 `lumos impact --diff`。`Systems/test-quality-handbook.md` 排第一,標「家」。`scripts/test_lumos.py` 的家節點是它,所以我原先標 ⚠ 的疑慮解除:PITFALL 放在這篇是對的。

另外兩篇家節點 `測試假綠形態.md`(帶 INVARIANT)和 `arch-alignment-lens.md`,我 grep 了「預算 / 暫調 / finally / 模組常數」,沒有命中,沒有與這份 diff 衝突的條文。

**問 1　分層與依賴方向:對齊。**
- 新碼只在測試函式 `t_dispatch_lens_spec_mode_core` 內,沒有新增函式或 import。它呼叫的 `m.cmd_dispatch_lens_spec` 和 `m._LENS_SPEC_BUDGET` 與鄰居用的是同一組符號。
- 對照:`scripts/test_lumos.py:57830-57837`(`t_dispatch_lens_spec_scan_budget_truncates`)和 `scripts/test_lumos.py:58475-58483` 都是直接賦值模組常數。
- 筆記放在 `docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:20`,和同檔第 19 行的測試類 PITFALL 在同一位置。

**問 2　命名與錯誤處理:大體對齊,有一處不一致。**
- 還原方式:鄰居是 `try / finally`,本 diff 也是。賦值放在 `try` 內也一樣(`scripts/test_lumos.py:57833`、`58478`)。
- 命名:鄰居的暫存變數叫 `old`、`old_b`,本 diff 叫 `_old_budget`。同函式的 import 全用底線前綴(`_io`、`_j`),所以這個名字貼合函式內部風格,只是和鄰居不同,屬 minor。
- 暫調值:鄰居調小(`0.0`、`1.5`),本 diff 調寬到 `120.0`。方向相反是目的不同,不算不一致。
- 筆記行:`PITFALL:` 前綴正確,帶 `[出處:]`、`[根因:]`、`[test:]`,三選一條件滿足。`[修法:]` 是選填。寫法與第 19 行相同,對齊。

**問 3　第二種做法:沒有引入。**
- 沒有 monkeypatch 工具、context manager 或 fixture,仍是專案既有的手動賦值加 `finally` 還原。
- `governance/anchor-baseline.json` 的雜湊與 note 更新,是「改測試檔要先簽名」的既有流程。

**finding 1**
severity: minor
blocking: 否
引句:「_old_budget = m._LENS_SPEC_BUDGET」
暫存變數命名和鄰居不同:鄰居用 `old`(`scripts/test_lumos.py:57830`)和 `old_b`(`scripts/test_lumos.py:58475`),本 diff 用 `_old_budget`。結構對,只是名字不同。

不對齊共 1 條,其中 major 0 條。
