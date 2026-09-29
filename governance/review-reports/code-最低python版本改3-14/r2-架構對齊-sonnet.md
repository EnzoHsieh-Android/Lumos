severity: minor

# 第 2 輪 架構對齊審查(修正差異 605b0a65..57314d47)

## F1 doctor 認「lumos 自家掛鉤」又寫了第三種做法
severity: minor
blocking: 否 — 結構對(來源仍取自 _GLOBAL_CLAUDE_HOOKS 單一清單),只是判斷式跟鄰居寫法不同,屬鄰居本身就不一致的區塊 ⚠
引句:「ours = {n for n in _GLOBAL_CLAUDE_HOOKS if n.endswith(".py") and not n.startswith("_")}」
1. 同一件事「設定裡哪一條命令是 lumos 自己的掛鉤」,repo 已有兩種寫法:enforcement_status 用子字串 `needle in cmd`(file: `scripts/lumos:19995`,needle 是寫死列舉);merge-claude-settings.py 用 `_hook_script` 抓 `([\w.-]+\.py)`、再以 `_HOOKS_SUBDIR` 比對路徑(file: `scripts/merge-claude-settings.py:303-321`)。
2. 這份 diff 的 `_hook_python_problems` 新增第三種:shlex 切開、第二字取 basename 精確比對 ours、第一字用自寫正規式判「像 python」(file: `scripts/lumos:19930-19938`)。
3. 三處各自認定,沒有機械守一致:掛鉤檔名清單一改,enforcement 那份列舉與這份不會同步報錯。實際影響有限(ours 是由 _GLOBAL_CLAUDE_HOOKS 推導的,新增掛鉤會自動納入),所以只判 minor;鄰居本身就有兩種,沒有單一既有做法可對,⚠。
未能重現為「壞掉」——這是一致性問題,不是行為錯誤。

## F2 目前目錄防護只補在完整版,同一件事的 Windows 另一份實作沒跟上
severity: minor
blocking: 否 — 兩份分岔在文件中已聲明是刻意的,只是這次新增的行為差沒被守衛盯
引句:「目前目錄底下的同名檔不收(同 _py_which 的說明)」
1. `_py_which` 只用在 lumos 的直譯器搜尋與 `_pick_windows_launcher`(file: `scripts/lumos:116-129`、`scripts/lumos:16600`)。
2. Windows 啟動指令挑選還有第二份實作 get.ps1,直接 `Get-Command $cand`,沒有「落在目前目錄底下就不收」(file: `get.ps1:41`)。`_pick_windows_launcher` 的說明寫「分岔是刻意的」,但只提到 py 與實際執行,沒提現在多了目錄防護的差異。
3. 守衛 t_windows_interpreter_pick_matches_slim 只盯順序一致(見 `_WIN_LAUNCHERS` 上方註解),所以這條資安防護在兩份之間是否一致沒有機械守衛。⚠ get.ps1 那邊是否受同一風險(PowerShell 的 Get-Command 預設也會先找目前目錄)我沒實測,只依註解 r1 資安席的論述類推。

## 三問結論
1. 分層與依賴方向:已看,無 finding。`_py_which` 放在 python-floor 區塊(檔頭、須 3.9 可讀),被同檔的 `_py_probe`、`_py_uv_find`、`_py_resolve`、`_pick_windows_launcher` 呼叫;`_pick_windows_launcher` 從檔中段往檔頭區塊呼叫,方向與既有(下層工具在前)一致。post-commit 與四支安裝腳本、三支 git 掛鉤的 LUMOS_PYTHON 一行新增七處逐一檢查都在(各含 1 個 python-launcher 區塊、1 行 LUMOS_PYTHON),七份由 t_python_launcher_blocks_agree 逐字守(file: `scripts/test_lumos.py:51360`),沒有跨層直呼。
2. 命名與錯誤處理:已看,無 finding(除 F1)。`_py_*` 前綴、回 (值, 說明) 元組、找不到回 None、錯誤走 stderr 與 rc 2,跟同區塊鄰居一致;CI 提示與 Codex 重新信任的說明併入既有 `_py_floor_message`、既有升級注意字串,沒另起新輸出通道。
3. 第二種做法:見 F1、F2。棧別檢核 py-external tension 四欄:existing 指的 scripts/slim-scan.py:41 未在本輪差異內,本輪 diff 沒改到它;hazard(lumos 卡在找直譯器時呼叫方永遠等)在本輪修正差異裡沒有新增無逾時的呼叫,`_py_probe` 仍帶逾時與 stdin=DEVNULL(file: `scripts/lumos:132`),已看,無 finding。

不對齊共 2 條,其中 major 0 條。最嚴重等級 minor,blocking 共 0 條。
