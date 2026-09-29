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
  - Systems/每支檔有家
  - Systems/codex-harness
  - Systems/測試假綠形態
related:
  - "[[Issues/蘋果內建Python3.9跑全套仍紅]]"
  - "[[Projects/全repo審視_計劃]]"
  - "[[Projects/存量漂移防線_計劃]]"
  - "[[Systems/測試假綠形態]]"
---
# 最低Python版本改3.14_計劃

白話:工具鏈原本對外說「Python 3.9+ 就能用」,但沒有任何地方檢查版本,每個入口都拿路徑上第一個 `python3`——在 macOS 上常常就是蘋果內建的 3.9。3.9 碰到極深的巢狀運算式會讓解析器整個程序崩潰(不是丟例外),測試總檔也有 3.12 才合法的寫法。這一篇把最低版本改成 3.14,並讓所有入口**找得到 3.14 就用、找不到就講清楚**,不再默默拿 3.9 去跑。

依據:Enzo 2026-09-29 裁「工具最低版本改成 3.14」(存量漂移防線乙的代碼審連兩輪卡在 3.9 的 ast.parse 崩潰之後);同日裁定四項:①找不到 3.14 時 git 掛鉤擋下並講清楚怎麼裝 ②自動找 3.14、lumos 被舊版啟動時改用找到的 3.14 重跑 ③安裝器找不到時報錯附安裝指令、不替人裝 ④舊版相容寫法只清擋路的。這個裁定回答了 [[Issues/蘋果內建Python3.9跑全套仍紅]] 與 [[Systems/測試假綠形態]] 留的「CI 要不要加 3.9」,也翻掉 [[Projects/全repo審視_計劃]] F65「不加啟動時版本檢查」那一條(當時註明再拉高下限要人裁)。

存量漂移防線乙因此先暫停:它的提交與第 4 輪卷證留在工具鏈 repo 的本機分支 `wip/存量漂移防線乙`(沒推),第 4 輪 10 條發現還沒處置;本計劃落地後回去收,屆時拿掉它為 3.9 加的事先篩選並重接到主線。

PRIOR-ART: 世界上的做法是「宣告 + 安裝時擋」:套件用 `requires-python`,pip / uv 安裝時就拒絕;uv 的 `--python 3.14` 與 `uv python find`、pyenv 的 shims、Windows 的 `py -3.14` 啟動器負責「找對的直譯器」。本工具零依賴、不是 pip 套件、入口有 git 掛鉤與 Claude/Codex 掛鉤,借不到 requires-python 的擋法,所以自己做最小的一層:一份固定順序的候選清單、每個候選用 `sys.version_info` 驗一次;uv 只當候選之一(有裝才用),不當依賴。
RETIRE-IF: 工具改成用 uv tool / pipx 這類有 requires-python 的方式發佈、由安裝器擋版本時,自製的找直譯器與啟動時重跑整套撤掉;或三個月內「找不到 3.14 被擋」的事件為 0 而且所有已知機器都已裝 3.14 時,改成只在安裝時檢查。

## 範圍

- 在範圍內:`scripts/lumos` 與 `scripts/hooks/**`(git 掛鉤會被複製進消費專案)、Claude/Codex 掛鉤註冊(`scripts/merge-claude-settings.py`)、安裝入口(`install.sh`、`get.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh`)、CI、ruff 設定、README 兩份、測試裡擋路的 3.9 專用寫法。
- 不在範圍內(Enzo 2026-09-29 確認):精簡版 `slim/**`——它是另一個對外發佈的東西,自己承諾「Python 3 標準庫」、Windows 真機驗過 3.8,這次不拉它的下限。
- 不在範圍內:其餘約 10 處為 3.8/3.9 寫的繞路寫法(刻意不用 `is_relative_to`、dict `|`、`write_text(newline=)` 等)——無害,留著,之後碰到那一段再順手改。

## 做法

1. **一份候選清單、兩處實作、一支測試守兩邊同步**:依序試 `$LUMOS_PYTHON`、`python3.14`、`python3.15`、`python3.16`、`python3`、`python`,有 uv 時再試 `uv python find '>=3.14'`;每個候選跑一次「版本 ≥ 3.14 嗎」,挑第一個過的。★只有兩處實作★:①`scripts/lumos` 開頭(Python;Windows 多一個候選 `py -3.14`);②`scripts/hooks/` 底下一支新的共用檔(shell,只給 git 掛鉤 source)。兩份的候選順序用一支測試比對,改一邊沒改另一邊就紅。新共用檔要登記進工具自裝檔的精確名單(跟 `t_vendored_file_list_matches_what_install_ships` 一起改),消費專案才會把它當工具檔、跟著掛鉤一起被複製。
2. **lumos 被舊版啟動時自己改用 3.14 重跑**:版本檢查放在 `if __name__ == "__main__":` 那段、進 `main()` 之前(被測試用 import 載入時不觸發);不夠就用上面的清單找,找到就用它重跑 `__file__` 加原本的參數(POSIX 用 `os.execv`;Windows 的 execv 不會真的取代行程、呼叫端拿不到回傳碼,改成子行程跑完再用它的回傳碼結束);找不到就印「需要 Python 3.14 以上,現在是 X.Y(路徑);找過的候選與各自的版本:…;安裝:…」並回 2,不印追蹤。重跑前設一個環境變數,重跑後的程序若還是舊版就直接報錯,不會無限重跑。這段與它之前的所有程式碼必須能被舊版解析(見 [S7])。
3. **git 掛鉤**:`pre-commit`、`pre-push` 改 source 共用檔;找不到 3.14 時擋下(rc 1)並印同一段說明——★不退回 3.9★。現況:兩支都是「找不到任何 python 就印提醒放行、找到 3.9 就拿 3.9 跑」,這兩種都改掉。說明裡講明:沒有 3.14 就寫不了治理帳,真要提交只能 `git commit --no-verify`(不留帳)。`post-commit` 擋不了提交:現況找不到 python 時會執行空字串指令出錯,改成 source 共用檔、找不到就印一行提醒後正常結束。
4. **Claude/Codex 掛鉤註冊**:`merge-claude-settings.py` 寫進設定檔的直譯器改成「跑這支程式的那一支」(`sys.executable`),不再用 `shutil.which("python3")`;它自己開頭也加同一個版本檢查(低於 3.14 就報錯回 2、不寫設定),因為除了經 lumos 啟動,使用者也可能直接用 `python3` 手動跑它。
5. **安裝入口不各自找直譯器**:`install.sh`、`get.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh` 照舊只負責「找一支任何版本的 python 把 lumos 叫起來」,找 3.14 與找不到時的說明全交給第 2 點(lumos 開頭)——所以舊的安裝複本沒有新共用檔也沒關係,PowerShell 也不用再寫一份。它們只改一件事:連任何 python 都找不到時,印同一套安裝指令(macOS:`brew install python@3.14` 或 `uv python install 3.14`;Linux:發行版套件或 uv;Windows:python.org 安裝器或 `winget install Python.Python.3.14`),回 2,不替人裝。Windows 的 `lumos.cmd` 包裝照舊寫指令名不寫死路徑,版本同樣交給 lumos 開頭,所以跟精簡版共用的包裝候選順序不動。
6. **CI 與 ruff**:CI 的 `python-version` 改成 `"3.14"`;`.lumos/lint.json` 的 `--target-version` 改成 `py314`。CI 既有的「編譯全部檔」與「SyntaxWarning 歸零」兩道會在 3.14 上重跑,3.14 新增的警告要一起清。
7. **文件**:README 與 README.en(安裝需求那兩處,加上 README.en 另一處「running Lumos itself needs Python 3.9+」)改成 3.14+,並寫一句為什麼(系統內建 3.9 會崩潰)與升級注意(更新後沒有 3.14 的機器,提交會被擋);`get.ps1` 的錯誤訊息跟著改。不寫 CHANGELOG——它自己規定只記發版,這段升級注意由下次發版的人帶進去。
8. **清擋路的舊碼**:測試的 `_toml_loads` 代解分支(沒有 tomllib 就找另一支直譯器代解,最低 3.14 之後是死碼)改回直接 `import tomllib`;`t_hooks_python_fallback`(現在只盯 post-commit 與 pre-push 兩支寫 `command -v python3 || command -v python`)改成斷言三支掛鉤都 source 共用檔。
9. **收尾連帶**:[[Issues/蘋果內建Python3.9跑全套仍紅]] 結案(兩件 3.9 專屬問題在 3.14 下不存在);[[Systems/測試假綠形態]] 那條「CI 要不要加 3.9」的 REVISIT 改寫成已由本計劃回答;[[Projects/全repo審視_計劃]] F65 記一行被本計劃翻掉;存量漂移防線乙回來收尾時,拿掉它為 3.9 加的事先篩選(`_drift_py_too_deep`)。
10. **新開一篇系統筆記**管共用清單那支新檔與「找直譯器」這件事(負責:挑直譯器、驗版本、找不到時的說明;不負責:各入口自己的業務邏輯)。

## 條款

- [S1] 當 git 掛鉤或 lumos 要找 Python,工具應依固定順序試候選、只接受版本 ≥ 3.14 的那一個;shell 與 Python 兩份清單的順序應一致 [test:t_python_resolver_order_and_floor]
- [S2] 當 lumos 以主程式身分被 3.14 以前的 Python 啟動,工具應找到 ≥3.14 就改用它跑同一支檔同一組參數並回傳它的回傳碼;找不到應印出需要的版本、現在的版本與路徑、找過的候選與各自版本、安裝指令,回 2,不印追蹤;重跑後仍是舊版時應直接報錯,不再重跑;被 import 載入時不應觸發 [test:t_lumos_old_python_reexec_or_explain]
- [S3] 當 pre-commit 或 pre-push 找不到 ≥3.14(包括只找得到 3.9、或完全沒有 python),工具應擋下(rc 非 0)並印同一段說明,不得改用較舊的 Python 執行檢查;post-commit 找不到時應印提醒後正常結束 [test:t_hooks_block_without_python314]
- [S4] 當安裝入口連任何 python 都找不到,工具應印安裝指令並回 2,不得自行安裝;找得到舊版時應交給 lumos 開頭處理 [test:t_installers_require_python314]
- [S5] 當註冊 Claude/Codex 掛鉤,工具應寫入目前執行的那一支直譯器的路徑;merge-claude-settings.py 被 3.14 以前的 Python 直接執行時應報錯回 2、不寫設定 [test:t_hook_cmd_uses_running_python]
- [S6] 當 CI 執行,應在 3.14 上跑全套;ruff 的目標版本應是 py314 [test:t_ci_and_lint_target_python314]
- [S7] 當 scripts/lumos 被修改,它仍應能被舊語法(3.9)解析,這樣舊版啟動時才跑得到第 2 點的版本檢查 [test:t_lumos_parses_under_old_grammar]

## 回退

- 全部回退:還原本計劃的提交即可,沒有資料格式改變。回退後 3.9 的崩潰與測試總檔的 3.12 寫法問題照舊存在。
- 只回退「擋下」:把 git 掛鉤找不到 3.14 時改成印提醒並放行(第 3 點)——放行是整道檢查不跑,★不是改用 3.9 跑★;其餘保留。這會讓沒裝 3.14 的機器檢查整個沒跑。
- 消費專案:更新後沒裝 3.14 的機器提交會被擋;暫時解法是裝 3.14(`brew install python@3.14`)或設 `LUMOS_PYTHON` 指到一支 ≥3.14 的直譯器。
- 使用者機器上的 Claude/Codex 設定:回退程式碼之後,設定檔裡寫進去的直譯器路徑不會自己變回來,要重跑一次安裝(`lumos install --force` 或 `install.sh`)。

## 實務隱患

- **守衛面(碰到)**:git 掛鉤從「沒 Python 就放行」改成「沒 3.14 就擋」,擋的條件變寬;錯的時候是誤擋(找得到 3.14 卻判找不到)。防法:找直譯器的判定只有一份清單、兩處實作用測試守同步;擋下訊息列出找過的每個候選與它的版本,誤擋時看得出是哪一步判錯。
- **對外送出(碰到)**:改的是對外發佈的安裝說明與安裝腳本(README、get.sh、get.ps1),更新後的消費專案在沒裝 3.14 的機器上提交會被擋。防法:CHANGELOG 寫升級說明,擋下訊息附三種平台的安裝指令與 `LUMOS_PYTHON` 的用法;不自動安裝任何東西。
- **不可逆(碰到一半)**:程式碼本身還原提交就回去;但 Claude/Codex 設定檔裡寫進去的直譯器絕對路徑,在使用者機器上要重跑安裝才會換回來。回退節寫明要重跑安裝。
- 已排除:金流:這個工具不碰任何付款或計費。

## 誠實界線

- **舊版要能把 scripts/lumos 解析完,版本檢查才跑得到**:Python 要先把整支檔解析完才會執行第一行,檔案裡只要出現 3.10 以上才有的語法(例如 match),3.9 就在檢查之前丟語法錯誤。[S7] 用舊語法版本解析守著;但 `ast.parse(feature_version=…)` 只擋得到語法,擋不到「新版才有的標準庫函式在載入時就被呼叫」這類,所以不是完整保證。git 掛鉤先經過共用清單,碰不到這條;安裝入口與手打 `python3 scripts/lumos` 會碰到。
REVISIT:2026-12-29 看這段期間有沒有人回報「用舊版跑出語法錯誤、看不到說明」;有的話把 scripts/lumos 拆成一支只做檢查的小入口加本體
- **`--no-verify` 不留帳**:沒有 3.14 就沒有能寫治理帳的直譯器,擋下之後唯一的出口是 git 自己的 `--no-verify`,這一次不會進治理帳。
- **uv 找到的直譯器可能是 uv 自己管的**:它會隨 uv 更新搬家;寫進 Claude/Codex 設定的是絕對路徑,搬家後掛鉤會失效,要重跑安裝。
