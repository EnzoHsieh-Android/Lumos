severity: major

## F1 另一種找直譯器的方式
severity: major
blocking: 是
引句:「for name in ("python3.14", "python3.13", "python3.12", "python3.11", "python3"):」
說明:同檔既有的「逐一嘗試多支 Python」是 `cands = [sys.executable]`,再對固定絕對路徑 `("/usr/bin/python3", "/usr/local/bin/python3")` 用 `os.path.exists` 補進去(`scripts/test_lumos.py:37266-37269`),用 `sys.version_info` 印版本(`scripts/test_lumos.py:37272`)。新 helper 改用 `shutil.which` 掃版本名清單,再用 `Path.resolve()` 比對 sys.executable 去重,是專案原本沒有的第二種找法。兩者候選集合也不同:既有的會納入 /usr/bin/python3,新的只靠 PATH。同一件事(找另一支直譯器)該共用或比照既有寫法;若判斷 which 更好,也該抽成單一 helper 讓 `scripts/test_lumos.py:37266` 一併改用,而不是並存。

## F2 另一種套 patch 的方式
severity: major
blocking: 是
引句:「sweep = mock.patch.object(self.m, "FULL_SWEEP_SECONDS", 1)」
說明:`scripts/test_autonomous_loop.py` 其餘所有 patch 都用 `with mock.patch.object(...)`(如 `scripts/test_autonomous_loop.py:1686-1687`、`1694-1695`、`1715`、`219`),整檔沒有任何其他 `.start()` / `addCleanup`。本 diff 新增的 start + addCleanup(`scripts/test_autonomous_loop.py:1683-1685`)是該檔第一個此寫法。鄰居寫法可直接用 `with` 巢狀或併進同一個 with 的多行 patch(下一行已有 with 塊),無需第二種做法。

## 三問

1. 分層與依賴方向:對齊。`_toml_loads` 放在使用它的 `t_codex_d6_agent_toml` 正上方(`scripts/test_lumos.py:35831`),為底線開頭的模組內 helper,只被同檔測試呼叫,與 `_load_hook_mod`(`scripts/test_lumos.py:35400`)、`_need_src`(`scripts/test_lumos.py:150`)等同層 helper 一致;沒有跨層直呼。inline import 用 `_j/_sh/_sp` 別名也是同檔慣例。
2. 命名與錯誤處理:對齊。找不到解析器 raise RuntimeError,被 runner 的 `except Exception` 記 FAIL(`scripts/test_lumos.py:31617-31619`),等同判紅不跳過;跳過通道 `_SrcOnly` 定義為「來源 repo 才有的東西」(`scripts/test_lumos.py:129-`),tomllib 缺失不屬此類,不借用是對的,與「一條斷言都沒有判紅」(`scripts/test_lumos.py:31597-31604`)同方向(沒驗到=紅)。無日誌差異。細節:子行程失敗用 ValueError、找不到用 RuntimeError,兩種型別 runner 都同樣處理,無影響。
3. 第二種做法:有兩處,見 F1(找直譯器改用 which+版本名清單,對照 `scripts/test_lumos.py:37266-37272`)、F2(start+addCleanup,對照 `scripts/test_autonomous_loop.py:1686`)。f-string 修法(先算 `n_dup` 再放進 f-string)是單純改寫,無第二種做法。圖譜筆記與 anchor-baseline 的更新走既有流程,不列。

總結:不對齊共 2 條,其中 major 2 條。
