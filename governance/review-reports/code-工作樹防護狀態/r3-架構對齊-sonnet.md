severity: clean

不對齊共 0 條,其中 major 0 條。

## 三問

**1. 分層與依賴方向**
- 修補沒有新增跨層呼叫。新的 `try/except OSError` 和 `continue` 都在 `enforcement_status` 裡(`scripts/lumos:26018-26021`)。
- 讀不到本工作目錄 hook 時,它仍用該函式自己的 `add(layer, "degraded", …)` 記錄結果。這跟 `scripts/lumos:25892`、`25931`、`25996` 的 degraded 寫法一致。
- git 呼叫仍走 `_lens_git`(`scripts/lumos:45955`),3 秒上限跟 `_events_root` 一樣(`scripts/lumos:25562`)。
- `_hooks_path_dir` 的解析仍只有一份,`_hooks_path_sibling_worktree` 沒有另寫解析。
- `_hooks_path_is_ours` 沒被放寬,拆除路徑不受影響。

**2. 命名與錯誤處理**
- **import 位置**:`import filecmp` 從迴圈前搬到函式開頭,緊貼 `import json as _json`(`scripts/lumos:25837`)。既有的 `_vendored_pending` 也是函式開頭 import(`scripts/lumos:22815`),所以修補後更一致。
- **例外處理**:只接 `OSError`,跟 `scripts/lumos:156`、`183`、`442` 一樣,也跟 `_enforcement_prepush_ungated` 讀 hook 時接 `OSError` 的寫法一樣(`scripts/lumos:26137`)。改列 degraded 而不掉進外層 `except Exception → unknown`,是在外層既有機制前再補一道更具體的接法,不算新寫法。
- **測試權限還原**:`chmod 000` 後用 `try/finally` 還原,跟 `scripts/test_lumos.py:12255` 一致。
- **root 跳過**:新測試用 `_os.access(R_OK) and _os.geteuid() != 0` 當條件,沒有在函式開頭 `return`。專案有三種寫法:
  - 開頭早退並印 `check("★skip★…")`(`scripts/test_lumos.py:10052`、`29999`)
  - 只判 `getuid() != 0` 後靜默略過(`scripts/test_lumos.py:78762`)
  - 開檔探測能不能讀(`scripts/test_lumos.py:12255`)

  新寫法是在整體測試中途只略過其中一條斷言,屬於第二、三種的混合,沒有哪種寫法被取代,不列為 finding。
- **命名**:`differs` 和 `wpc` 跟周邊的短名風格一致。測試新增的 `fn = layer.removeprefix("git-")` 沒引入新命名慣例。

**3. 第二種做法(實查)**
- 全檔 `import filecmp` 只有兩處:`scripts/lumos:22815` 和 `25837`,都在函式開頭,沒有迴圈內 import。
- 比內容用 `filecmp.cmp(..., shallow=False)`,跟 `_vendored_pending` 的用法一樣(`scripts/lumos:22821`)。
- 「接 OSError 後改列狀態」沒有第二套平行機制。
- 測試新增的 `0o644`/`0o755` 切換、`write_text` 改檔再還原,都沿用 `t_hooks_path_forms_all_recognized` 同系列的 `_sp`/`_os` 別名與 `check(...)` 寫法。
- 在 `scripts/lumos` 搜尋 `Path | None` 型別提示,沒有看到對立慣例。這屬於 r2 之前就有的內容,不是修補差異。

這一輪沒有發現引入新的「第二種做法」,只有 `enforcement_status` 內部的一個小改動和對應測試,跟既有做法一致。

不對齊共 0 條,其中 major 0 條。
