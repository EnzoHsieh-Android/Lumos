---
type: project
status: doing
created: 2026-09-29
updated: 2026-09-29
tags:
  - type/project
  - status/doing
  - scope/platform
lands_in:
  - Systems/lumos-cli-lifecycle
  - Systems/bound-tests-gate
  - Systems/codex-harness
  - Systems/python直譯器選擇
related:
  - "[[Issues/蘋果內建Python3.9跑全套仍紅]]"
  - "[[Projects/全repo審視_計劃]]"
  - "[[Projects/存量漂移防線_計劃]]"
  - "[[Systems/測試假綠形態]]"
  - "[[Systems/筆記內容閘]]"
---
# 最低Python版本改3.14_計劃

白話:工具鏈原本對外說「Python 3.9+ 就能用」,但沒有任何地方檢查版本,每個入口都拿路徑上第一個 `python3`——在 macOS 上常常就是蘋果內建的 3.9。3.9 碰到極深的巢狀運算式會讓解析器整個程序崩潰(不是丟例外)。這一篇把最低版本改成 3.14,並讓所有入口**找得到 3.14 就用、找不到就講清楚**,不再默默拿 3.9 去跑。

依據:Enzo 2026-09-29 裁「工具最低版本改成 3.14」(存量漂移防線乙的代碼審連兩輪卡在 3.9 的 ast.parse 崩潰之後);同日裁定四項:①找不到 3.14 時 git 掛鉤擋下並講清楚怎麼裝 ②自動找 3.14、lumos 被舊版啟動時改用找到的 3.14 重跑 ③安裝器找不到時報錯附安裝指令、不替人裝 ④舊版相容寫法只清擋路的。這個裁定回答了 [[Issues/蘋果內建Python3.9跑全套仍紅]] 與 [[Systems/測試假綠形態]] 留的「CI 要不要加 3.9」,也翻掉 [[Projects/全repo審視_計劃]] F65「不加啟動時版本檢查」那一條(當時註明再拉高下限要人裁)。

存量漂移防線乙因此先暫停:它的提交與第 4 輪卷證留在工具鏈 repo 的本機分支 `wip/存量漂移防線乙`(沒推),第 4 輪 10 條發現還沒處置;本計劃落地後回去收,屆時拿掉它為 3.9 加的事先篩選並重接到主線。

PRIOR-ART: 世界上的做法是「宣告 + 安裝時擋」:套件用 `requires-python`,pip / uv 安裝時就拒絕;uv 的 `--python 3.14` 與 `uv python find`、pyenv 的 shims、Windows 的 `py -3.14` 啟動器負責「找對的直譯器」。本工具零依賴、不是 pip 套件、入口有 git 掛鉤與 Claude/Codex 掛鉤,借不到 requires-python 的擋法,所以自己做最小的一層:一份固定順序的候選清單、每個候選用 `sys.version_info` 驗一次;uv 只當候選之一(有裝才用),不當依賴。
RETIRE-IF: 工具改成用 uv tool / pipx 這類有 requires-python 的方式發佈、由安裝器擋版本時,自製的找直譯器與啟動時重跑整套撤掉;或三個月內「找不到 3.14 被擋」的事件為 0 而且所有已知機器都已裝 3.14 時,改成只在安裝時檢查。

## 範圍

- 在範圍內:`scripts/lumos` 與 `scripts/hooks/**`(git 掛鉤會被複製進消費專案)、Claude/Codex 掛鉤註冊(`scripts/merge-claude-settings.py`)、安裝入口(`install.sh`、`get.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh`)與 Windows `lumos.cmd` 包裝、測試指令(`.lumos/config.json` 的 `run_cmd` 與 `scripts/test_lumos.py` 開頭)、CI、README 兩份與 ONBOARDING 前置需求表、lumos 建議給消費專案的 CI 範例、測試裡擋路的 3.9 專用寫法。
- 不在範圍內(Enzo 2026-09-29 確認):精簡版 `slim/**`——它是另一個對外發佈的東西,自己承諾「Python 3 標準庫」、Windows 真機驗過 3.8,這次不拉它的下限。完整版 Windows 包裝因此會跟精簡版的候選順序分岔(完整版多一個 `py`),是刻意的。
- 不在範圍內:其餘約 10 處為 3.8/3.9 寫的繞路寫法(刻意不用 `is_relative_to`、dict `|`、`write_text(newline=)`、禁止 `zip(strict=)` 等)——無害,留著;而且 `scripts/lumos` 本來就要維持 3.9 能解析(見第 2 點),這些寫法剛好不衝突。
- 不在範圍內:維護者自己的排程腳本(`governance/*.sh`)——它們用 `python3 scripts/lumos` 啟動,經第 2 點的開頭檢查會自己改用 3.14;不另改。它們把錯誤輸出吞掉、失敗也不回報(`|| true`),在沒有 3.14 的機器上會默默不做事;只跑在維護者裝了 3.14 的機器上,接受。

## 做法

1. **一份候選清單、兩處實作加 PowerShell 一份,測試守三邊同步**。順序:
   ①`$LUMOS_PYTHON`(★有設就只認它★:不合格就停下報錯,不往下找——明寫了要用哪一支的人,不該被默默換成別支;值是一支執行檔的路徑,不能帶參數、不展開 `~`,空字串等於沒設)→ ②`git config lumos.python`(`lumos init`、`lumos update`、`lumos install` 在該 repo 跑完時,把自己的 `sys.executable` 寫進去——這三個指令經第 2 點一定跑在 ≥3.14 上;git 設定不靠行程的環境變數,從 Dock 啟動的 git 圖形用戶端、pyenv 鎖了專案版本的目錄都讀得到)→ ③`python3.14`、`python3.15`、`python3.16` → ④固定位置 `/opt/homebrew/bin/python3.14`、`/usr/local/bin/python3.14`、`$HOME/.local/bin/python3.14`(路徑很短的環境靠這一段)→ ⑤`py -3.14`(Windows 啟動器;Git Bash 裡也叫得到)→ ⑥`uv python find --system --no-python-downloads '>=3.14'`(只找系統裝好的、★不准觸發下載★)→ ⑦`python3`、`python` 放最後(它們最常是舊版;沒裝開發工具的 macOS 執行 `/usr/bin/python3` 會跳出安裝對話框,排在後面,有 3.14 的機器就碰不到它)。找到一個就停。
   每個候選的驗法一樣:用它跑一段「版本 ≥ 3.14 就印出 `sys.executable`,否則回 1」,標準輸入接 `/dev/null`;Python 與 PowerShell 那兩份設 5 秒逾時,shell 那份有 perl 就用 `perl -e 'alarm 5; exec @ARGV'` 包起來,逾時算這個候選不合格。★之後一律用它印出的絕對路徑★(重跑、寫設定、擋下訊息),不用候選的名字——`os.execv` 不會去 PATH 找名字,`py -3.14` 也不是一個路徑。
   實作:①`scripts/lumos` 開頭(Python);②`scripts/hooks/` 底下一支新的共用檔(shell),`pre-commit`、`pre-push` 與 `install.sh`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh`、`get.sh` 用 `${BASH_SOURCE[0]}` 或 checkout 路徑定位後 source,被 source 時找一次、結果放進變數,呼叫端不重找(`post-commit` 不用它,見第 3 點);③`get.ps1` 自己一份 PowerShell 清單(它在 clone 之前就要跑,拿不到共用檔)。同步測試逐項比對三份的共同部分(①③⑤⑥⑦);只屬於某個平台的項目列成測試裡的明文豁免:④的 POSIX 固定位置不進 PowerShell,②的 git 設定不進 `get.ps1`(clone 之前還沒有 repo)。`lumos.cmd` 包裝只寫指令名、不挑版本,不算一份清單。
   ★為什麼 git 掛鉤改成 source 共用檔★(架構對齊席問過,專案原本是三支掛鉤各自內嵌、靠漂移測試對齊):這段有七類候選、驗法、逾時、說明文字,兩支掛鉤加四支安裝腳本各抄一份再加漂移測試,比一支共用檔多出五份要同步的東西;而且整個 `scripts/hooks/` 本來就是整夾被複製,共用檔會跟著走。這是本專案第一個被掛鉤 source 的檔,新系統筆記要記這個理由。
   新共用檔要登記三張名單:工具自裝檔精確名單(`t_vendored_file_list_matches_what_install_ships`)、錨點清單 `ANCHOR_FILES` 與 `governance/anchor-baseline.json`(要跑 `lumos anchor approve`,那支檔決定掛鉤擋不擋、用哪支直譯器,本來就該被錨點盯著)。
2. **lumos 開頭先檢查版本**:緊接在檔案最前面那幾行標準庫 import 之後,在 `__name__ == "__main__"` 時檢查兩件事:版本低於 3.14,或 `LUMOS_PYTHON` 有設、而且不是目前這一支(兩者都比 `os.path.realpath`)——後者讓 `LUMOS_PYTHON` 在 lumos 本體與 git 掛鉤效力一樣;被測試用 import 載入時不觸發;舊版只需要執行這幾行就到得了檢查,不必先跑完 3.5 萬行的模組頂層(`def f(x: int | None)` 這種寫法在 3.9 定義當下就會丟 TypeError)。不夠就照清單找,找到就用它重跑:POSIX `os.execv(絕對路徑, [絕對路徑, __file__, *原參數])`;Windows 的 execv 不會真的取代行程、呼叫端拿不到回傳碼,改成子行程跑完用它的回傳碼結束。找不到就印「需要 Python 3.14 以上,現在是 X.Y(路徑);找過的候選與各自結果:…;安裝:…」並回 2,不印追蹤。
   防無限重跑:重跑前設 `LUMOS_REEXEC_PYTHON=<目標絕對路徑>`;開頭檢查時,只有「這個變數有值、而且等於自己的 `sys.executable`、版本卻還是舊的」才算重跑失敗、直接報錯;★通過檢查後立刻把這個變數從環境拿掉★,所以 lumos 之後叫起的任何子孫行程都不會繼承到它(不然孫行程被舊版叫起時,會被誤判成重跑失敗)。
   `scripts/lumos` 因此★必須一直能被 3.9 解析★(Python 要先解析完整支檔才跑第一行):`.lumos/lint.json` 的 ruff 目標版本維持 `py39`,不改成 py314——ruff 在 py39 下會把 3.12 才合法的 f-string 寫法報成語法錯誤,是目前唯一抓得到這一類的工具(`ast.parse(feature_version=(3,9))` 放過這種寫法,實測)。
3. **git 掛鉤**:`pre-commit`、`pre-push` 在「確定這次會叫 lumos」那一步才 source 共用檔——pre-commit 在圖譜不存在、staged 是空的、沒有 `scripts/lumos` 這三種提早放行之後;pre-push 在把標準輸入讀完之後、而且有 `scripts/lumos` 時。找不到 3.14 就擋下(rc 1)並印說明——★不退回 3.9★。現況兩支都是「找不到任何 python 就印提醒放行、找到 3.9 就拿 3.9 跑」,這兩種都改掉。共用檔本身不見了(殘缺安裝)印「共用檔 <路徑> 不見了,請重跑 lumos update」並擋下,跟「沒有 3.14」分開講。說明裡講明出口:設 `LUMOS_PYTHON` 或 `git config lumos.python <路徑>`,真要提交只能 `git commit --no-verify`。
   `post-commit` 不改:它只負責把「這次用 --no-verify 跳過了」寫進跳過帳,用的是任何版本都跑得動的一段標準庫程式;沒有 3.14 的機器正是最常用 --no-verify 的機器,這筆帳不能因為設了下限而寫不進去。
4. **Claude/Codex 掛鉤註冊**:`merge-claude-settings.py` 寫進設定檔的直譯器改成 `sys.executable`,POSIX 分支用 shell 引號包起來(原本只有 Windows 分支加引號,路徑含空白整條命令就壞);它自己開頭也加同一個版本檢查(低於 3.14 就報錯回 2、不寫設定),因為使用者也可能直接用 `python3` 手動跑它。
5. **安裝入口**:`install.sh`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh` 與它們 source 的共用檔在同一份 checkout 裡,改成 source 共用檔找 3.14;`get.sh` clone 或已存在之後 source 共用檔;沒有共用檔(舊的安裝複本、沒帶 `--pull`)就印「安裝複本太舊,請加 --pull 重跑」回 2,不退回 `python3`(只有 `python3.14` 的機器上退回 `python3` 會變成沒說明的 127);`get.ps1` 用自己那份 PowerShell 清單。都找不到就印安裝指令(macOS:`brew install python@3.14` 或 `uv python install 3.14`;Linux:發行版套件或 uv;Windows:python.org 安裝器或 `winget install Python.Python.3.14`)回 2,不替人裝。候選「找得到」一律要真的執行成功才算(Windows 的商店替身 `python.exe` 找得到、執行卻失敗)。Windows 的 `lumos.cmd` 包裝:PATH 上有 `python3`/`python` 就寫指令名,都沒有而有 `py` 就寫 `py -3`,版本交給第 2 點;因此改 `t_windows_interpreter_pick_matches_slim`,改成「完整版比精簡版多一個 py」。
6. **測試指令**:`.lumos/config.json` 的 `run_cmd` 改成 `{python} scripts/test_lumos.py -k {method}`,由 lumos 代入自己的 `sys.executable`(合約測試閘與 guard kill 用 shell 跑它,原本吃 PATH 上的 `python3`,3.14 只以 `python3.14` 存在的機器會把每一支綁定測試跑紅);`scripts/test_lumos.py` 開頭加同樣的版本檢查(不夠就印說明回 2)。pre-push 擋下時提示的 `python3 scripts/test_lumos.py …` 與 CLAUDE.md 的子集指令改寫成找得到 3.14 的寫法。
7. **CI**:`python-version` 改成 `"3.14"`;既有的「編譯全部檔」與「SyntaxWarning 歸零」兩道會在 3.14 上重跑,新警告一起清。ruff 目標版本不動(理由見第 2 點);CI 另加一步裝 ruff、以 py39 為目標只檢查語法錯誤(`--select E9`)`scripts/lumos`——CI 的 ubuntu 內建 python3 是 3.12,拿它編譯擋不到 3.12 的 f-string 寫法,ruff 是 CI 上唯一守得住 [S7] 的東西(ruff 只在 CI 當工具裝,不是工具鏈的依賴)。lumos 建議給消費專案的 CI 範例(`lumos doctor --ci` 等步驟)補上安裝 3.14 的那一步——GitHub 的 ubuntu 預設 python3 是 3.12,不補的話消費專案 CI 一更新就回 2。
8. **通知與文件**:README 與 README.en(安裝需求兩處、README.en 另一處「running Lumos itself needs Python 3.9+」)改成 3.14+,寫一句為什麼(系統內建 3.9 會崩潰)與升級注意;ONBOARDING 的前置需求表加版本;`get.ps1` 的錯誤訊息跟著改。`lumos update` 在消費專案更新到這一版時印一次升級注意(沒有 3.14 的機器提交會被擋、CI 要裝 3.14、怎麼設 `LUMOS_PYTHON`)。不寫 CHANGELOG——它自己規定只記發版,由下次發版的人帶進去。隊友 `git pull` 拿到新掛鉤、沒跑過 update 的,第一次看到的就是擋下訊息,所以擋下訊息要自己講得清楚(第 3 點)。
9. **偵測設定壞掉**:`lumos doctor` 多一項:Claude/Codex 設定裡註冊的直譯器路徑不存在或版本低於 3.14 時提醒「重跑 lumos install」——`sys.executable` 可能落在 uv、pyenv、venv、Homebrew 某個版本目錄底下,會隨它們更新或刪除而消失,原本沒有任何東西會發現。
10. **清擋路的舊碼**:測試的 `_toml_loads` 代解分支改回直接 `import tomllib`;所有會複製單支掛鉤或直接跑掛鉤、或模擬「PATH 上沒有 python 就放行」的測試(`-k hook` 全跑一次盤點;已知 `t_hooks_python_fallback` 只盯兩支、`scripts/test_lumos.py` 約 36619 行附近只複製 pre-push 一支)改成連共用檔一起複製,並把「沒 python 就放行」的斷言反轉成擋下。
11. **收尾連帶**(不列進 lands_in,是順手更新):[[Issues/蘋果內建Python3.9跑全套仍紅]] 結案,依據寫「3.14 跑過全套綠」,不寫成「原因已查清」(那兩件的原因它自己標了沒驗);它與 [[Systems/測試假綠形態]] 各有一條 `REVISIT:2026-10-29`,兩條都改寫成已由本計劃回答;[[Systems/筆記內容閘]] 那條 zip(strict=) 的 PITFALL 補一句下限已改、禁令為何保留(第 2 點);[[Projects/全repo審視_計劃]] F65 記一行被本計劃翻掉;存量漂移防線乙回來收尾時拿掉它為 3.9 加的事先篩選。
12. **每支檔有家**:新開一篇系統筆記(暫定 `Systems/python直譯器選擇`,已列進 lands_in)管共用檔與「找直譯器」這件事(負責:挑直譯器、驗版本、找不到時的說明、`git config lumos.python`;不負責:各入口自己的業務邏輯)。原本沒有家的 `install.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh` 交給 [[Systems/lumos-cli-lifecycle]](它已經管 `get.sh`)。
13. **落地驗收**:實作完在本機跑一次 `lumos install --force`,對 Claude 與 Codex 兩個部署位置的掛鉤檔各比一次 sha256,並確認設定檔裡寫的是加了引號的 3.14 絕對路徑——改 `merge-claude-settings.py` 不會自己重寫家目錄底下的設定。

## 條款

- [S1] 當 git 掛鉤、安裝入口或 lumos 要找 Python,工具應照第 1 點的固定順序試候選,找到一個就停,只接受實際執行印出 ≥3.14 的那一個、並改用它印出的絕對路徑;`LUMOS_PYTHON` 有設但不合格時應停下報錯,不往下找;lumos init、update、install 跑完應把自己的直譯器寫進該 repo 的 `git config lumos.python`;shell、Python、PowerShell 三份的共同項目順序應一致、平台專屬項目只准照第 1 點列的豁免;每個候選的驗法應隔開標準輸入,Python 那份應有逾時 [test:t_python_resolver_order_and_floor]
- [S2] 當 lumos 以主程式身分被 3.14 以前的 Python 啟動、或 `LUMOS_PYTHON` 指的不是目前這一支,工具應在執行完開頭幾行 import 後就檢查,找到 ≥3.14 就用它的絕對路徑跑同一支檔同一組參數並回傳它的回傳碼;找不到應印出需要的版本、現在的版本與路徑、找過的候選與各自結果、安裝指令,回 2,不印追蹤;`LUMOS_REEXEC_PYTHON` 等於自己又仍是舊版時應直接報錯;通過檢查後應清掉這個變數,子孫行程被舊版叫起時應照常重跑;被 import 載入時不應觸發。測試應在找得到真的舊版直譯器時用它跑,找不到時應明說這一格沒驗到,並比對輸出內容而不只比回傳碼 [test:t_lumos_old_python_reexec_or_explain]
- [S3] 當 pre-commit 或 pre-push 確定這次要叫 lumos、卻找不到 ≥3.14(包括只找得到 3.9、或完全沒有 python),工具應擋下(rc 非 0)並印說明,不得改用較舊的 Python;圖譜不存在、staged 為空、沒有 scripts/lumos 時應照舊放行;共用檔不見時應印另一段說明並擋下;post-commit 的跳過帳應照舊用任何版本寫入 [test:t_hooks_block_without_python314]
- [S4] 當安裝入口在只有 python3.14、只有 Windows 的 py 啟動器、或只有商店替身的機器上執行,工具應找到真的 3.14 或印安裝指令回 2,不得自行安裝;get.sh 的安裝複本沒有共用檔時應叫人加 --pull 並回 2 [test:t_installers_require_python314]
- [S5] 當註冊 Claude/Codex 掛鉤,工具應寫入目前執行的那一支直譯器的絕對路徑並加引號(路徑含空白時命令照樣可執行);merge-claude-settings.py 被 3.14 以前的 Python 直接執行時應報錯回 2、不寫設定 [test:t_hook_cmd_uses_running_python]
- [S6] 當 CI 執行,應在 3.14 上跑全套,並以 ruff(py39)檢查 scripts/lumos 的語法;lumos 產生給消費專案的 CI 範例應包含安裝 3.14 的步驟 [test:t_ci_runs_python314_and_old_syntax_check]
- [S7] 當 scripts/lumos 被修改,它仍應能被 3.9 語法解析:ruff 以 py39 為目標檢查語法錯誤;找得到真的 3.9 直譯器時應實際編譯一次,找不到時應明說沒驗到 [test:t_lumos_parses_under_old_grammar]
- [S8] 當合約測試閘或 guard kill 跑專案測試指令,應以執行中的 lumos 那一支直譯器代入 `{python}`;scripts/test_lumos.py 被 3.14 以前的 Python 執行時應印說明回 2 [test:t_test_run_cmd_uses_running_python]
- [S9] 當新增共用檔,它應同時在工具自裝檔名單、錨點清單與錨點基準線裡 [test:t_python_resolver_registered_everywhere]
- [S10] 當 Claude/Codex 設定裡註冊的直譯器不存在或低於 3.14,lumos doctor 應提醒重跑安裝 [test:t_doctor_flags_stale_hook_python]

## 回退

- **全部回退**:還原本計劃的提交,再到每個已更新的消費專案用★全域或工具鏈來源那份★ lumos 跑 `lumos update`,把舊掛鉤複製回去——專案裡自帶的那份 lumos 已是新版,在只有 3.9 的機器上會回 2,用不了。更新完手動刪掉消費專案 `scripts/hooks/` 底下留下的共用檔(工具只複製名單上的檔、不刪舊檔,殘檔會被當成專案自己的程式掃)。各專案的 `git config lumos.python` 留著無害。Claude/Codex 設定裡的 3.14 絕對路徑照樣跑得動舊版掛鉤,不重跑安裝也不會壞。
- **主線已有後續提交時**:還原前先用真的 3.9 編譯一次 `scripts/lumos` 與 `scripts/hooks/**`,確認回退窗口裡沒人寫進 3.10 以上的語法;存量漂移防線乙若已合併、拿掉了 3.9 事先篩選,要一起補回來,否則 3.9 的 ast.parse 崩潰原樣重現。圖譜的收尾(Issue 結案、兩條 REVISIT、F65)不跟著還原,另外補一篇說明「下限退回 3.9」並重開那篇 Issue。
- **只回退「擋下」**:git 掛鉤找不到 3.14 時改成印提醒並跳過檢查——★是整道檢查不跑,不是改用 3.9 跑★;同時把 [S3] 與它的測試改成斷言放行,並經 `lumos update` 才到消費專案。後果要講明:只有 3.9 的機器上,掛鉤放行、但任何 lumos 指令照樣因第 2 點回 2,治理帳一筆都不會有;比本計劃之前(拿 3.9 跑檢查)還弱,兜底只剩 CI(3.14)。提醒文字要改成「找得到 Python X.Y,但需要 3.14,這次沒跑檢查」。
- 消費專案被擋時的暫時出口:裝 3.14、設 `LUMOS_PYTHON`、或 `git config lumos.python <3.14 的路徑>`。

## 實務隱患

- **守衛面(碰到)**:git 掛鉤從「沒 Python 就放行」改成「沒 3.14 就擋」,擋的條件變寬;錯的時候是誤擋。防法:候選含 git 設定與固定位置(圖形用戶端、排程這類路徑很短的環境)、只在確定要叫 lumos 時才擋、擋下訊息列出每個候選與它的結果;三份清單用測試守同步。
- **對外送出(碰到)**:改的是對外發佈的安裝說明與安裝腳本,更新後的消費專案在沒裝 3.14 的機器上提交會被擋、CI 會回 2。防法:`lumos update` 印升級注意、README 寫升級注意、CI 範例補安裝 3.14、擋下訊息附三種平台的安裝指令與兩種指定直譯器的方法;不自動安裝任何東西,uv 探測帶 `--no-python-downloads`。
- **不可逆(碰到一半)**:程式碼還原提交就回去,但消費專案的掛鉤副本要逐一更新回去、會留殘檔,見〈回退〉。
- **效能**:pre-commit、pre-push 各找一次直譯器;第一個候選就命中約 30 毫秒,全部落空加 uv 約 0.2 秒。舊註冊(設定還寫著 3.9)在重跑安裝前每次呼叫 lumos 多一次重跑,約 65 毫秒;第 9 點的 doctor 提醒負責讓人去重跑。
- **自我治理(碰到)**:改的是治理守衛自己——掛鉤擋不擋、錨點清單、合約測試閘用哪支直譯器跑。改壞的後果是全專案誤擋或整道檢查沒跑。防法:共用檔進錨點(改了要人重簽)、[S3] 與 [S8] 釘住擋下與測試指令、落地驗收比 sha256。
- 已排除:金流:這個工具不碰任何付款或計費。

## 誠實界線

- **shell 那份沒有 perl 時沒有逾時**:macOS 沒有內建 `timeout` 指令,shell 靠 perl 的 alarm 設逾時;沒有 perl 的環境(精簡容器)只隔開標準輸入,某個候選卡住不回,掛鉤會跟著卡住。
REVISIT:2026-12-29 看這段期間有沒有「掛鉤卡住」的回報;有的話改用背景行程加 kill 的做法
- **全域 `lumos` 指令靠 `#!/usr/bin/env python3` 啟動**:完全沒有 `python3` 這個名字的機器(只用 uv 裝了 `python3.14` 的 Linux)上,打 `lumos` 在跑到第 2 點之前就失敗(env 找不到 python3);git 掛鉤不受影響(走共用檔)。這種機器要 `uv python install 3.14 --default` 或自己加 `python3` 別名;擋下與安裝訊息會提這一句。
- **舊版要能解析 scripts/lumos**:[S7] 用 ruff(py39)與真的 3.9 編譯守語法;機器上沒有舊版直譯器、也沒有 ruff 時守不到,測試會明說沒驗到。開頭那幾行 import 之後才出現的載入期問題不影響(檢查在它們之前)。
- **`--no-verify` 會留跳過帳、不會留閘的帳**:post-commit 照舊記下「這次跳過了」,但被擋的那幾道檢查本身沒有跑,也沒有它們的紀錄。
- **設定檔裡的絕對路徑會過期**:uv、pyenv、venv、Homebrew 升版都可能讓它消失;第 9 點的 doctor 提醒是事後偵測,不是事前防止。

## 審計修正紀錄

- r1(2026-09-29,7 席:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet 5.5;外家否決 Codex;前置掃描已跑):51 條,去重後約 30 件,major 33 條(機器數各報告的 F 標題與 severity 行;最初手數成 52/28,已更正);全數錨定(架構對齊席一句「lands_in」不到 10 字不採信,那條改用其敘述)。卷證在 `governance/review-reports/最低python版本改3-14/r1-*`。
  - 折入(全數):版本檢查搬到檔案最前面(正確性);scripts/lumos 維持 3.9 能解析、ruff 目標版本不改(正確性、接手,推翻原本第 6 點);候選清單加 git 設定與固定位置、`LUMOS_PYTHON` 有設就只認它、`py` 兩份都有、uv 帶 `--system --no-python-downloads`、一律用印出的絕對路徑、驗法隔開輸入並設逾時(邊界、正確性、接手、併發、外家);防重跑變數命名並在通過後清掉(併發、正確性、邊界、接手、架構對齊);掛鉤在確定要叫 lumos 時才擋、共用檔缺席另一段說明、找一次(邊界、正確性、接手、併發);post-commit 不設下限(正確性);註冊命令加引號(邊界、外家、正確性);安裝入口補齊候選並真的執行(邊界、正確性、外家、接手);測試指令 `{python}` 與測試總檔版本檢查(正確性);三張名單登記(接手、正確性、外家);四支沒家的檔交給 lumos-cli-lifecycle(外家);落地驗收比 sha256(外家);doctor 偵測過期路徑(回滾);消費專案通知與 CI 範例(接手);回退節重寫(回滾);CHANGELOG 前後矛盾(正確性、外家、接手);ONBOARDING 與筆記內容閘收尾(接手);lands_in 拿掉每支檔有家與測試假綠形態(架構對齊)。
  - 鏡像核對(便宜席,材料含席報告目錄):51 條已處理 43、部分 8、未處理 0、相反 0;新矛盾 7。已補:`git config lumos.python` 由 init/update/install 寫入並進 [S1];get.sh 沒有共用檔改成叫人加 --pull、不退回 python3;`LUMOS_PYTHON` 值的語意與在 lumos 本體也有效;python3/python 挪到候選最後、找到即停;shell 有 perl 時用 alarm 設逾時;全域 lumos 的 shebang 與排程腳本默默失效寫進界線;新系統筆記列進 lands_in;[S6] 測試名改掉 py314 字樣、CI 加 ruff 守 [S7];post-commit 不 source 的說法統一;三份清單的比對與平台豁免寫明;白話段刪掉已被另一會談修掉的「測試總檔有 3.12 寫法」。
