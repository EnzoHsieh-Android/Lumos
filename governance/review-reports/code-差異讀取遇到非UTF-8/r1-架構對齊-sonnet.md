severity: clean

### 三問比對(逐問查證,無 finding)

1. 分層與依賴方向:對齊。九處新增寫法跟 delguard 既有先例同款——file: `scripts/lumos:17681-17685` 是 base 已有的 `capture_output=True, text=True, errors="replace", cwd=root`(這段不是本次 diff 改的,是被抄的先例)。diff 新增九處之一同款,引句:「capture_output=True, text=True, errors="replace", cwd=cwd)」。這九個呼叫點修改前就分散在 `_scan_diff_for_irreversible_hints`/`cmd_cochange_check`/`_pitfall_diff_collect`/`cmd_test_layers`/`cmd_impact_diff`(兩處)/`_codeloop_record_valid` 六個不同函式裡各自內聯 `subprocess.run`,不是這次才變分散;`_lens_git`、`_testmap_git` 這兩個既有 git 包裝也只是各自模組(dispatch-lens、test-layers)的本地 wrapper,不是通用讀差異函式。維持現狀分散、不收成共用函式,不算引入新做法或跨層直呼。

2. 命名與錯誤處理:`_lens_git` 拆成兩條 return,是必要修正而非隨意分歧。引句(diff 刪除行,對照 base 單行三元式):「return _sp.run(cmd + list(args), capture_output=True, text=not binary, timeout=20)」;引句(diff 新增行):「return _sp.run(cmd + list(args), capture_output=True, timeout=20)」。查證(diff 外,佐證):Python `subprocess.Popen.__init__` 內 `self.text_mode = encoding or errors or text or universal_newlines`——只要傳了 `errors=` 不論 `text` 是否為 False 都會被轉成文字模式;若沿用舊三元式在同一行直接加 `errors="replace"`,`binary=True` 分支會被文字模式蓋掉、回傳型別從 bytes 變 str,破壞呼叫端要拿 bytes 做指紋比對的既有用法(file: `scripts/lumos:13437` `_lens_git(root, "show", f"{ref}:{p}", binary=True)`)。結構對,不算不一致。

3. 第二種做法:沒有查到。九處全部只用「同一支既有 subprocess.run 呼叫上補 `errors="replace"`」這一招(含 `_lens_git`、`_testmap_git` 兩個既有 wrapper 原地修補,不是新開一支);新增測試沿用既有 fixture 慣例,對照 file: `scripts/test_lumos.py:9775-9776` 同款 `def git(*a): sp.run(...)` / `def commit(msg): git(...)` 寫法,以及既有共用 helper file: `scripts/test_lumos.py:135` `_load_lumos_inproc()`,沒有另立新測試基礎設施。

不對齊共 0 條,其中 major 0 條
總結:最高 severity clean,blocking 共 0 條
