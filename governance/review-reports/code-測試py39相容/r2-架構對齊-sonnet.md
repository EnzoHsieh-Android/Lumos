severity: clean

## 問 1 分層與依賴方向:對齊
新增的 `_toml_loads` 放在 `scripts/test_lumos.py` 的 `t_codex_d6_agent_toml` 前面,和該檔其他測試輔助函式一樣是同檔頂層函式。它只被同檔的 d6 測試呼叫,只依賴標準函式庫。沒有跨層直呼。對照:同檔 `scripts/test_lumos.py:37268` 的時間戳測試也是同檔內自帶找直譯器的邏輯。`scripts/test_autonomous_loop.py:1683` 的改動維持在測試類別內,用 `self.m` 套 patch,不牽動別層。

## 問 2 命名與錯誤處理:對齊
`_toml_loads` 用底線開頭的私有輔助函式命名,函式內 import 也寫成 `import json as _j, subprocess as _sp, os as _os`,與 `scripts/test_lumos.py:37263` 的 `import shutil as _sh, ... as _sp, os as _os` 同一風格。錯誤處理是直接丟例外(ValueError / RuntimeError),由測試框架記成紅,不吞、不跳過。對照:`SKIP` 通道只留給來源 repo 才有的東西,見 `scripts/test_lumos.py:121`。沒有新增日誌方式。

## 問 3 第二種做法:沒有
- 找直譯器:用固定路徑清單加 `os.path.exists`,與 `scripts/test_lumos.py:37268-37270` 同一做法。候選清單多了 `/opt/homebrew/bin/python3`,但仍是同一個做法,只是清單內容不同。沒有引入 `shutil.which` 或別的探測方式(全檔 grep 沒有其他做法)。
- 套 patch:改成 `with mock.patch.object(...)` 巢狀,與同檔既有寫法一致。同檔沒有用 `enterContext` 或 `addCleanup(mock...)` 的先例(grep 確認),所以沒有第二種做法。見 `scripts/test_autonomous_loop.py:1683`。
- 子行程呼叫:用 `_sp.run([...], capture_output=True, text=True, timeout=60)`,與 `scripts/test_lumos.py:37277-37285` 及 `scripts/test_lumos.py:670` 同形。
- f-string 反斜線:改成先算 `n_dup` 再放進 f-string,是消除語法差異的局部修法,不是新工具。
- `tomllib` 在整個 `scripts/` 下只出現在 `scripts/test_lumos.py` 這一支,沒有既有的共用 toml 解析輔助函式可對,也就沒有自創重複。

⚠ 交編排者(不算不對齊):`_toml_loads` 的候選直譯器清單沒有像 `scripts/test_lumos.py:37267` 那樣把 `sys.executable` 放第一個。這裡不需要,因為 `sys.executable` 已經 import 失敗才走到這一步,屬合理差異。

總結:不對齊共 0 條,其中 major 0 條。
