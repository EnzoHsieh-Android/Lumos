severity: major

## F1 找直譯器的候選清單在 bash 與 lumos 各寫一份,漂移測試只守 bash 那七份,沒守 bash 對 lumos
severity: major
blocking: 是 — 同一件事(找 3.14 的候選順序與固定位置)兩處各寫一份、宣稱有機械守一致,實際只守了一半,接手的人要在兩套之間猜
引句:「# LUMOS_PYTHON_SEARCH_DIRS(冒號分隔)有設就換掉固定位置——測試接縫,跟 lumos 內部那份同一個。」
1. 專案既有的「複製一份 + 一條測試盯住不准漂」先例:t_windows_interpreter_pick_matches_slim 真的把兩邊的候選順序與退回值各自解析出來比對。
   file: `scripts/test_lumos.py:7705`
2. 這份 diff 的 bash 內嵌段(`_lumos_any_python`:python3.14/3.15/3.16 → /opt/homebrew/bin、/usr/local/bin、~/.local/bin → python3、python → py)與 lumos 內的 `_py_candidates`、`_py_fixed_candidates` 是同一份清單的兩種語言寫法。
   file: `scripts/lumos:87`
   file: `scripts/lumos:105`
3. 守衛測試 docstring 與計劃都說「順序跟 lumos 內部清單的共同項目一致」,但測試本體只讀 bash 那七份互比、再對第一份的內部順序做 find,從頭到尾沒讀 scripts/lumos 的清單。
   file: `scripts/test_lumos.py:51333`
   file: `scripts/test_lumos.py:51335`
4. 重現(在 mktemp 臨時目錄複製 install.sh、get.sh、get.ps1、scripts/,只改複本):把 lumos 複本的 _py_candidates 改成 ("python3.16", "python3.15", "python3.14")、_py_fixed_candidates 的 names 改成 ("python3", "python3.16"),跑
   `/opt/homebrew/bin/python3 scripts/test_lumos.py -k t_python_launcher_blocks_agree`
   輸出:`11 passed, 0 failed`(該紅沒紅)。
5. 三問結論:分層與依賴方向——lumos 端在最前面標準庫層、bash 端在各入口,層次符合設計,無跨層直呼;第二種做法——即本條。

## 已看,無 finding
- 問 1 分層與依賴方向:新 cmd_python_path、_run_cmd_expand、_hook_python_problems、doctor Check Q 都放在同類鄰居旁,doctor 段用 warn_soft 不計 issues,與 Check N 同寫法;掛鉤只呼叫 lumos python-path,沒有跨層直呼(對照 `scripts/lumos:19885`、`scripts/lumos:3020`)。
- 問 2 命名與錯誤處理:「擋下:」前綴、rc=2、HELP_WHEN 加登記、sub.add_parser 加 help,與既有 cmd_* 一致;子行程呼叫帶 timeout、stdin=DEVNULL,寫法與 `scripts/lumos:31855` 一致。開頭版本檢查段用 % 格式而鄰居多用 f-string,屬風格偏好不列。
- 問 3 第二種做法:
  - _run_cmd_expand 把三處各自代換 {method} 收成一支,是收斂不是新增(grep 確認 `scripts/lumos` 已無其他地方自己代 {method} 後執行)。
  - 七份 bash 內嵌段互相、以及 pre-commit 與 pre-push 的 python-314 段,有 t_python_launcher_blocks_agree 逐字守,符合專案既有「複製 + 測試盯」做法。
  - _pick_windows_launcher 是第三份 Windows 挑直譯器判斷,t_windows_interpreter_pick_matches_slim 已改成守「去掉 py 後與精簡版一致、與 get.ps1 順序一致」,守得住(已實際讀測試本體)。
  - merge-claude-settings.py 內另有一份 _py_floor_gate(與 lumos 內同名、同一個 LUMOS_REEXEC_PYTHON 防重跑協定),但它是委託 lumos python-path 找直譯器而不是自己再找一份,計劃做法第 4 點明訂,且 t_hook_cmd_uses_running_python 有行為測試釘 ⚠ 兩份重跑骨架與環境變數名沒有機械守一致,只靠行為測試,判不準是否算第二種做法,不列 finding。
- 棧別檢核 py-external(tension):hazard 指「問 lumos 要路徑那一呼叫不帶逾時會永遠等」,在此 diff 不成立——merge-claude-settings.py 的呼叫帶 timeout=60、stdin=DEVNULL,與 chosen 一致;existing 指的 scripts/slim-scan.py 寫法本席未逐行核對 ⚠,不列 finding。

不對齊共 1 條,其中 major 1 條(blocking 共 1 條)。最嚴重等級 major。
