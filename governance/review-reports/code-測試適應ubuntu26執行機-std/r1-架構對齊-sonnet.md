severity: minor

**1. 分層與依賴方向**

放的位置對。兩處測試修改都留在 `scripts/test_lumos.py`,沒有新增檔案,也沒有新的跨層依賴。家筆記 `Systems/測試執行器.md` 的 `about_code` 列了這支檔,PITFALL 寫在對的家。
- `_py314_old_interpreter` 的候選補在該函式內部。它的其他呼叫處是 `scripts/test_lumos.py:88251`、`scripts/test_lumos.py:88563`、`scripts/test_lumos.py:88875`,全部直接拿它的回傳值,所以補候選不改依賴方向。
- `t_hooks_block_without_python314` 改走 `_py314_old_interpreter`,和 `scripts/test_lumos.py:88251` 的用法一致。

**2. 命名與寫法**

大致和鄰居一樣。
- `preexec_fn=_ppc_sigint_default` 的寫法與 `scripts/test_lumos.py:31136`、`scripts/test_lumos.py:85386`、`scripts/test_lumos.py:86195` 相同。
- 函式內 `import ... as _gl` 沿用該函式原有的 `import subprocess as _sp, os as _os` 風格。
- 找不到直譯器時的提示改成「找不到 3.14 以前的直譯器」,與 `scripts/test_lumos.py:88564` 的措辭一致。
- A2:PITFALL 行的鍵順序和同檔既有行不同。既有行是 `[出處:] [根因:] [修法:] [test:]`(`docs/lumos-toolchain-knowledge/Systems/測試執行器.md:19`),新行把 `[test:]` 放在 `[修法:]` 前面。這只是鍵順序,CLAUDE.md〈寫筆記時〉明說欄位寫在句子前後都行。

**3. 第二種做法**

沒有另寫鄰居已有的工具函式:SIGINT 裝回預設用既有的 `_ppc_sigint_default`,找舊版直譯器用既有的 `_py314_old_interpreter`。
- A1:`t_hooks_block_without_python314` 原本用 `_py314_sysbin(tmp, keep_python=True)` 造「只有舊版 python 的目錄」。新程式改成手動 `mkdir` 加 `symlink`,另造 `oldpy` 目錄。這是同一件事的第二種造法,但原做法在 Ubuntu 26 上不成立(系統 python3 是 3.14),要指定舊版直譯器不得不改。
- 副作用是 `keep_python` 參數變成沒人用的死參數。其餘呼叫處 `scripts/test_lumos.py:86404`、`scripts/test_lumos.py:88593` 都沒傳 `keep_python`,函式本身見 `scripts/test_lumos.py:88337`。
- 結構上沒放錯層,只是留下一個孤兒參數與兩套造 PATH 的寫法。

severity: minor
blocking: 否
引句:「        withpy = tmp / "oldpy"」
file: `scripts/test_lumos.py:88337`

**審材外佐證**
- 新的 `preexec_fn=_ppc_sigint_default` 與 `scripts/test_lumos.py:31136` 的寫法一致。
- `_py314_old_interpreter` 的其他呼叫處都用 `old is None` 判斷沒找到,新呼叫處用 `old_exe is not None`,寫法等價。

不對齊共 1 條,其中 major 0 條
