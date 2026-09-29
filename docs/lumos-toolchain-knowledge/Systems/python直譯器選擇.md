---
type: system
status: doing
created: 2026-09-29
updated: 2026-09-29
responsibility: 負責找一支 Python 3.14 以上的直譯器:候選清單與順序、驗版本、lumos python-path、lumos 開頭的版本檢查與改用 3.14 重跑、找不到時的說明、LUMOS_PYTHON 與 LUMOS_PYTHON_SEARCH_DIRS;不負責 git 掛鉤與安裝腳本各自的業務邏輯(它們只內嵌一段找任何版本 python 的清單把 lumos 叫起來)
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/system
  - status/doing
  - scope/platform
summary: |-
  WHY:[2026-09-29 Projects/最低Python版本改3.14_計劃,Enzo 裁]工具最低 Python 改成 3.14:macOS 內建的 3.9 碰到巢狀很深的程式,ast.parse 會讓整個程序 SIGSEGV(不是丟例外),存量漂移防線乙為它補的事先篩選連兩輪被審出新洞;拉高下限讓這整類問題消失
  WHY:[2026-09-29 設計審 r2,外家否決席與邊界席]找 3.14 只有 lumos 裡這一份,git 掛鉤與安裝腳本只內嵌「找任何版本的 python 把 lumos 叫起來」:第一版讓掛鉤 source 一支共用 shell 檔,舊版的更新程式在啟動時已把要複製的檔案清單讀進記憶體,更新時複製了改過的掛鉤卻漏掉它不認得的新檔,第一次升級必定半套、提交被擋;被 source 進 set -euo pipefail 的腳本還會無聲結束、Git Bash 的路徑帶 \r
  WHY:[2026-09-29 設計審 r1 正確性席]開頭檢查放在最前面那幾行標準庫 import 之後、所有定義之前,只在主程式身分且版本低於 3.14 時觸發:3.9 在定義當下就會對 `def f(x: int | None)` 丟 TypeError,放在檔尾的 __main__ 段就跑不到;被測試用 import 載入時不能觸發
  WHY:[2026-09-29 設計審 r2,五席各自報到]LUMOS_PYTHON 只在版本不夠時才用來找 3.14,不讓一支已經是 3.14 的 lumos 重跑:指到 pyenv shim 或自寫包裝時,包裝啟動的真正路徑與設定的路徑永遠不同,會無限重跑
  WHY:[2026-09-29 設計審 r2 正確性席]LUMOS_PYTHON_SEARCH_DIRS 換掉固定位置清單,是測試接縫:維護者的 Mac 上 /opt/homebrew/bin/python3.14 一定存在,不換掉就造不出「找不到 3.14」的情境
  RULE:[since:2026-09-29][retire:工具改成用 uv tool / pipx 這類有 requires-python 的方式發佈,或把 scripts/lumos 拆成只做檢查的小入口加本體時][confirmed:2026-09-29]scripts/lumos、scripts/merge-claude-settings.py、scripts/hooks/claude 底下的 .py 必須一直能被 Python 3.9 解析:Python 要先解析完整支檔才跑第一行,舊版啟動時要能跑到開頭的版本檢查才講得出「需要 3.14」;CI 用釘版本的 ruff 以 py39 查語法錯誤 [test:t_lumos_parses_under_old_grammar]
  PITFALL:[2026-09-29 實作自測]macOS 的 /usr/bin/python3 是一層轉接,真正在跑的是開發工具底下那支,sys.executable 與 /usr/bin/python3 不同;比對「是不是同一支直譯器」要用它自己回報的 sys.executable,不能用啟動時的路徑 [test:t_lumos_old_python_reexec_or_explain]
  PITFALL:[2026-09-29 存量漂移防線乙代碼審 r3 外家席、r4 正確性席]3.9 的 ast.parse 在單一邏輯行約 21.6 萬字元的負號串、約 16 萬層的 elif 鏈就 SIGSEGV,接不到例外;重現:`/usr/bin/python3 -c "import ast; ast.parse('-'*500000+'1')"`,回傳碼 139
  PITFALL:[2026-09-29 代碼審 r1 核心席與資安席]doctor 探查掛鉤直譯器時,若只看命令裡有沒有 hooks/,會把別的工具的掛鉤(shell 條件式、bash 包一層、直接寫腳本)的第一個字拿去跑 `-c <探針>`——誤報重跑 lumos install 修不掉,還真的執行了別人的腳本;只認「第二段是 lumos 自家掛鉤檔、放在這一家 lumos 裝的目錄(兩家分開精確比對,不用後綴)、第一段像 python」的命令;測試拿合併程式真的寫出的兩家設定餵,安裝端改命令形狀就會紅 [test:t_doctor_flags_stale_hook_python]
  PITFALL:[2026-09-29 代碼審 r1 核心席]lumos update 在同一個行程裡先拉新來源再複製,執行的是拉新之前就載進記憶體的舊程式——新版才加的更新期提示,第一個專案一定印不出來;要讓人知道的事改在失敗現場講(CI 裡找不到 3.14 的說明自帶 setup-python 那一行) [test:t_update_prints_python314_notice_and_slim_strips_floor]
  PITFALL:[2026-09-29 代碼審 r1 資安席]Windows 找指令會先看目前目錄,git 掛鉤的目前目錄是 repo 根:用裸指令名探直譯器,陌生 repo 放一支 python3.14.exe 就會被執行;一律先解析成絕對路徑、落在目前目錄本身的不收、PATH 相對路徑項找到的不收(r2:擋整棵子樹的話,目前目錄是家目錄或磁碟根時正常安裝也消失;r3:位置只解析所在目錄那一層,整條解析會讓 repo 根指進子目錄的符號連結逃過比對) [test:t_python_resolver_order_and_floor]
  PITFALL:[2026-09-29 推上主線後 CI 紅]經符號連結啟動的 Python 回報的 sys.executable,在 macOS(Homebrew)會解到真實路徑、在 Linux 就是連結本身;測試或程式要比「是不是同一支直譯器」,兩邊都先 realpath 再比,只在本機跑綠不代表 CI 綠 [test:t_python_resolver_order_and_floor]
  TEST:t_python_resolver_order_and_floor、t_lumos_old_python_reexec_or_explain、t_hooks_block_without_python314、t_installers_require_python314、t_hook_cmd_uses_running_python、t_ci_runs_python314_and_old_syntax_check、t_lumos_parses_under_old_grammar、t_test_run_cmd_uses_running_python、t_update_prints_python314_notice_and_slim_strips_floor、t_doctor_flags_stale_hook_python、t_python_launcher_blocks_agree
related:
  - "[[Projects/最低Python版本改3.14_計劃]]"
  - "[[Issues/蘋果內建Python3.9跑全套仍紅]]"
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Systems/codex-harness]]"
  - "[[Systems/bound-tests-gate]]"
---
# python直譯器選擇

白話:工具需要 Python 3.14 以上。這篇管「在一台機器上找到那支 3.14」這件事:lumos 被舊版 Python 叫起來時,自己找 3.14 重跑一次;git 掛鉤先問 lumos 要 3.14 的路徑,找不到就擋下並說明怎麼裝,不會拿舊版硬跑。設計與取捨全在 [[Projects/最低Python版本改3.14_計劃]],這裡只記程式碼看不出來的部分。

## 幾個入口怎麼分工

- lumos 本體:唯一一份「找 3.14」的清單與驗法,對外是 `lumos python-path`。
- git 掛鉤與安裝腳本:各自內嵌同一段「找任何版本的 python」,只負責把 lumos 叫起來;版本判斷交給 lumos。這段在七支腳本裡逐字一致,由測試守著。掛鉤的家見 [[Systems/每支檔有家]](pre-commit)與 [[Systems/bound-tests-gate]](pre-push),安裝腳本的家見 [[Systems/lumos-cli-lifecycle]]。
- Claude/Codex 掛鉤的註冊:寫進設定檔的是跑註冊那支程式的直譯器,見 [[Systems/codex-harness]]。
- 精簡版:不拉下限。它的產物由生成器從主程式衍生,生成器會剝掉開頭呼叫版本檢查那三行。
