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
  - Systems/reversibility-governance-ledger
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

- 在範圍內:`scripts/lumos`、git 掛鉤 `scripts/hooks/pre-commit`、`pre-push`、`post-commit`(會被複製進消費專案)、Claude/Codex 掛鉤註冊 `scripts/merge-claude-settings.py`、安裝入口(`install.sh`、`get.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh`)與 Windows `lumos.cmd` 包裝、測試指令(`.lumos/config.json` 的 `run_cmd`)、CI、README 兩份與 ONBOARDING、doctor 印給消費專案的三處 CI 步驟提示、精簡版生成器 `scripts/slim-gen.py`(只為了剝掉開頭檢查)、測試裡擋路的 3.9 專用寫法。
- 不在範圍內(Enzo 2026-09-29 確認):精簡版 `slim/**` 不拉下限。精簡版交付庫 2026-08-20 起已獨立(`slim/FROZEN.md`),本 repo 的 `slim/` 只剩測試與歷史;但產物由 `scripts/slim-gen.py` 從 `scripts/lumos` 衍生,所以生成器要剝掉第 2 點的開頭檢查,產物才不會要求 3.14。完整版 Windows 包裝會跟精簡版的候選順序分岔(完整版多一個 `py`),是刻意的。
- 不在範圍內:其餘約 10 處為 3.8/3.9 寫的繞路寫法——無害,留著;`scripts/lumos` 本來就要維持 3.9 能解析(第 2 點),這些寫法剛好不衝突。
- 不在範圍內:維護者的排程腳本(`governance/*.sh`)。其中呼叫 `scripts/lumos` 的會經第 2 點自己改用 3.14;直接用 `python3` 跑其他 Python 檔的(`retrieval_eval.py`、`scenario_probe.py` 等)照舊吃 PATH 上的 python3,不受本計劃約束。它們吞掉錯誤輸出(`|| true`),在沒有 3.14 的機器上會默默不做事;只跑在維護者裝了 3.14 的機器上,接受。

## 做法

1. **找 3.14 只有一份實作,在 `scripts/lumos` 裡**(Python;對外是子指令 `lumos python-path`,印出一支 ≥3.14 直譯器的絕對路徑,找不到印說明回 2)。候選順序:
   ①`$LUMOS_PYTHON`——★有設就只認它★:必須是絕對路徑、指到一支 ≥3.14 的執行檔,否則停下報錯、不往下找(相對路徑在掛鉤與手打時會解析到不同的檔,所以直接拒收);空字串等於沒設 → ②`python3.14`、`python3.15`、`python3.16` → ③固定位置:`/opt/homebrew/bin/python3.14`、`/usr/local/bin/python3.14`、`~/.local/bin/python3.14`,以及 uv 與 pyenv 自己的安裝目錄(`~/.local/share/uv/python/cpython-3.1[4-9]*/bin/python3`、`~/.pyenv/versions/3.1[4-9]*/bin/python3`);Windows 是 `%LOCALAPPDATA%\Programs\Python\Python31[4-9]\python.exe`。從 Dock 啟動的 git 圖形用戶端、排程這類路徑很短的環境,以及 pyenv 把專案鎖在舊版的目錄,靠這一段找到 → ④Windows 的 `py -3.14` → ⑤`uv python find --system --no-python-downloads '>=3.14'`(不找虛擬環境、★不准觸發下載★;拿到它印的路徑,再用那個路徑照一般候選驗一次)→ ⑥`python3`、`python` 放最後(最常是舊版;沒裝開發工具的 macOS 執行 `/usr/bin/python3` 會跳出安裝對話框,排在後面,有 3.14 的機器就碰不到)。找到一個就停。
   每個候選的驗法一樣:用它跑一段「版本 ≥ 3.14 就印出 `sys.executable`,否則回 1」,標準輸入接空、單一候選 5 秒逾時、整份清單最多 15 秒;★之後一律用它印出的絕對路徑★,不用候選的名字(`os.execv` 不會去 PATH 找名字,`py -3.14` 也不是一個路徑)。
   ③的固定位置清單可以用 `LUMOS_PYTHON_SEARCH_DIRS`(以路徑分隔字元隔開的目錄)整份換掉——給測試造「這台機器找不到 3.14」(維護者的 Mac 上 `/opt/homebrew/bin/python3.14` 一定存在),也給特殊環境用;這類測試也要把開發者環境裡的 `LUMOS_PYTHON`、`LUMOS_REEXEC_PYTHON` 清掉;新系統筆記要記下它是測試接縫。
   ★為什麼不讓 shell 自己找 3.14★(設計審 r1 架構對齊席、r2 外家席):第一版讓三支掛鉤 source 一支新的共用 shell 檔,結果①舊版的更新程式在啟動時已把「要複製哪些檔」讀進記憶體,更新時複製了改過的掛鉤、卻漏掉它不認得的新共用檔,第一次升級必定半套、提交被擋;②被 source 進 `set -euo pipefail` 的腳本時,一個探測失敗就讓整支腳本無聲結束;③Git Bash 印出的路徑帶 `\r`;④要登記進三張名單與錨點。改成 shell 只負責「找一支任何版本的 python 把 lumos 叫起來」,判斷版本全交給 lumos,這四件都不存在。
2. **lumos 開頭先檢查版本**:緊接在檔案最前面那幾行標準庫 import 之後寫 `if __name__ == "__main__" and sys.version_info < (3, 14):`——被測試用 import 載入時不觸發;舊版只需要執行這幾行就到得了檢查(`def f(x: int | None)` 這種寫法在 3.9 定義當下就會丟 TypeError,所以檢查必須在所有定義之前)。不夠就照第 1 點找,找到就用它重跑:POSIX `os.execv(絕對路徑, [絕對路徑, __file__, *原參數])`;Windows 的 execv 不會真的取代行程、呼叫端拿不到回傳碼,改成子行程跑完用它的回傳碼結束。找不到就印「需要 Python 3.14 以上,現在是 X.Y(路徑);找過的候選與各自結果:…;安裝:…」並回 2,不印追蹤。★只有版本低於 3.14 才找、才重跑★——版本夠就直接跑,`LUMOS_PYTHON` 不會讓一支已經是 3.14 的 lumos 再重跑(否則 `LUMOS_PYTHON` 指到 pyenv shim 或自寫包裝時,包裝啟動的那支真正路徑跟設定的路徑永遠不同,會無限重跑)。
   防重跑:重跑前設 `LUMOS_REEXEC_PYTHON=<目標絕對路徑>`;開頭檢查時,這個變數有值、等於自己的 `sys.executable`、版本卻還是舊的,就算重跑失敗、直接報錯;★通過檢查後立刻把它從環境拿掉★,lumos 之後叫起的子孫行程不會繼承到。舊版每次重跑要先花約 0.22 秒解析整支檔(系統 python3.9 實測),再加上找候選與 3.14 啟動。
   `scripts/lumos` 因此★必須一直能被 3.9 解析★(Python 要先解析完整支檔才跑第一行)。同理必須 3.9 能解析的還有 `scripts/merge-claude-settings.py`(第 4 點)與 `scripts/hooks/claude/*.py`(設定還寫著舊直譯器的過渡期,它們跑在舊版上)。守法見 [S7]:`.lumos/lint.json` 的 ruff 目標版本維持 `py39`,不改成 py314(ruff 在 py39 下會把 3.12 才合法的 f-string 寫法報成語法錯誤;`ast.parse(feature_version=(3,9))` 放過這種寫法,實測)。
3. **git 掛鉤**:三支掛鉤各自內嵌同一段「找一支任何版本的 python」:`python3.14`、`python3.15`、`python3.16` → 可執行的 `/opt/homebrew/bin/python3.14`、`/usr/local/bin/python3.14`、`$HOME/.local/bin/python3.14`(HOME 沒設就略過這一格)→ `python3`、`python` → Windows 的 Git Bash 再試 `py -3`。固定位置排在 `python3` 前面:從 Dock 啟動的 git 圖形用戶端 PATH 很短,不先試固定位置就會先執行 `/usr/bin/python3`,沒裝開發工具的 macOS 會跳出安裝對話框;Linux 上 3.14 只在 `~/.local/bin`、PATH 又短的機器,也靠這一格才不會被判成「連任何 python 都沒有」。這段是 lumos 內部清單(第 1 點)的子集,只負責把 lumos 叫起來,版本判斷仍交給 lumos。三支掛鉤與第 5 點四支安裝腳本一共七份,用漂移測試守一致——這是專案原本的做法(各掛鉤內嵌、靠測試對齊)。
   `pre-commit`、`pre-push` 在「第一次需要叫 lumos」時才用找到的那支跑一次 `scripts/lumos python-path`,拿到的絕對路徑(去掉結尾 `\r`)用在這支掛鉤之後的所有呼叫。pre-commit 的順序照舊:圖譜不存在、staged 為空 → 放行;接著第一個用到 python 的是只提醒的 co-change 那道(排在會擋的 Gate 1–3 之前),`python-path` 失敗時★只提醒的幾道跳過並印一行★、不擋,不需要 python 的 Gate 1–3 照跑照擋,到第一道★會擋的★要 python 的閘才擋下;沒有 `scripts/lumos` 時照舊只跳過要 python 的那幾道。pre-push:標準輸入讀完之後、有 `scripts/lumos` 時。`python-path` 回非 0 時會擋的閘擋下(rc 1),原樣轉印 lumos 的說明——★不退回 3.9★;連任何 python 都找不到,掛鉤自己印安裝指令並擋下;找到的 python 一執行就失敗(Windows 商店替身),說明裡點名「找到的是 <路徑>,執行失敗,可能是商店替身」。現況「找不到任何 python 就印提醒放行、找到 3.9 就拿 3.9 跑」兩種都改掉。說明裡講明出口:設 `LUMOS_PYTHON`,真要提交只能 `git commit --no-verify`。這段只設變數、所有探測都用 `if` 包起來,在 `set -u`、`set -e` 下都不會中途結束。
   `post-commit` 用同一段「任何版本」清單寫跳過帳,★不設下限★:它只負責把「這次用 --no-verify 跳過了」寫進跳過帳,用的是任何版本都跑得動的標準庫程式;沒有 3.14 的機器正是最常用 --no-verify 的機器,這筆帳不能寫不進去。清單補上 `python3.14`,只裝了版本化指令的機器也寫得進去。
4. **Claude/Codex 掛鉤註冊**:`merge-claude-settings.py` 寫進設定檔的直譯器改成 `sys.executable`,POSIX 分支用 shell 引號包起來(原本只有 Windows 分支加引號,路徑含空白整條命令就壞)。它開頭也檢查版本:低於 3.14 就用 `[sys.executable, <同目錄的 lumos>, "python-path"]` 問出 3.14 的路徑、用它重跑自己;問不到就報錯回 2、不寫設定。這樣舊版的更新程式用舊直譯器叫新版的它,註冊照樣寫成 3.14。
5. **安裝入口只負責把 lumos 叫起來**:`install.sh`、`get.sh`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh` 各自內嵌同一段「任何版本」清單(跟第 3 點同一份,漂移測試一起守),找到就用它跑 `scripts/lumos …`,版本交給第 2 點;連任何 python 都找不到就印安裝指令(macOS:`brew install python@3.14` 或 `uv python install 3.14`;Linux:發行版套件或 uv;Windows:python.org 安裝器或 `winget install Python.Python.3.14`)回 2,不替人裝。`get.sh` 不再讀任何 repo 裡的檔,舊的安裝複本也照樣能把新版 lumos 叫起來。`get.ps1` 試 `py -3`、`python3`、`python`,★每個都真的執行一次(`-c pass`)才算找到★(Windows 的商店替身 `python.exe` 找得到、執行卻失敗)。Windows 的 `lumos.cmd` 包裝在安裝當下(這時已經跑在 3.14 上)同樣用「真的執行成功」挑:`py -3` 能跑就寫它,否則寫能跑的 `python3` 或 `python`,仍然只寫指令名、不寫死路徑;因此改 `t_windows_interpreter_pick_matches_slim`,改成「完整版比精簡版多一個 py、而且要執行成功」。
6. **測試指令**:`.lumos/config.json` 的 `run_cmd` 改成 `{python} scripts/test_lumos.py -k {method}`。代入集中到一支函式,依平台加引號(POSIX 用 shell 引號;Windows 用 cmd 的雙引號規則),所有讀 `run_cmd` 的地方都改呼叫它——現在是三處各自 `.replace("{method}", …)`:guard kill、合約測試閘的過濾探針(也就是確認「測試指令分不分得出找不到測試」的那支冒煙測試)、合約測試閘本體(spec-gate 共用);測試用 grep 確認沒有地方再自己代換。原本吃 PATH 上的 `python3`,3.14 只以 `python3.14` 存在的機器會把每一支綁定測試跑紅、被當成「證不出跑過」擋推送。`scripts/test_lumos.py` 本身不加版本檢查(由 `{python}` 保證用對的直譯器;人手用舊版跑它,照舊得到舊版的錯誤)。pre-push 擋下時提示的 `python3 scripts/test_lumos.py …` 與 CLAUDE.md 的子集指令改寫成「用 3.14 跑」。
7. **CI**:`python-version` 改成 `"3.14"`;既有的「SyntaxWarning 歸零」一道會在 3.14 上重跑,新警告一起清。另加一步:裝釘死版本的 ruff(`pip install ruff==<版本>`,只在 CI 當工具裝,不是工具鏈的依賴),以 py39 為目標、只查語法錯誤(`--select E9`),檢查第 2 點列的三類檔——CI 的 python 是 3.14,拿它編譯擋不到 3.12 的 f-string 寫法;原本的「編譯全部檔」一步用副檔名挑檔,從來沒編譯過沒有副檔名的 `scripts/lumos`。doctor 印給消費專案的三處 CI 步驟提示(筆記形狀擋、存量漂移檢查、筆記內容審)各加一句「這一步要在 Python 3.14 上跑(setup-python 設 3.14)」——lumos 沒有給消費專案的完整 CI 範本,只有這三處提示;GitHub 的 ubuntu 預設 python3 是 3.12,消費專案自己的 CI 更新後會回 2,這一項只能靠提示與升級注意,沒有偵測。
8. **通知與文件**:README 與 README.en(安裝需求兩處、README.en 另一處「running Lumos itself needs Python 3.9+」)改成 3.14+,寫一句為什麼(系統內建 3.9 會崩潰)與升級注意;ONBOARDING 的前置需求表加版本,正文裡 `python3 scripts/lumos …` 的指令改寫成「用 3.14 跑」並註明只有 `python3.14` 的機器怎麼打;`get.ps1` 的錯誤訊息跟著改。`lumos update` 把掛鉤複製進消費專案時,更新前的 pre-commit 裡沒有 `python-path` 字樣(代表是從還沒升級的版本更新上來),就印一段升級注意(沒有 3.14 的機器提交會被擋、CI 要用 3.14、怎麼設 `LUMOS_PYTHON`)。不寫 CHANGELOG——它自己規定只記發版,由下次發版的人帶進去。隊友 `git pull` 拿到新掛鉤、沒跑過 update 的,第一次看到的就是擋下說明,所以擋下說明要自己講得清楚(第 3 點)。
9. **偵測設定壞掉**:`lumos enforcement` 的 python 那一列改成列出 Claude/Codex 設定裡註冊的直譯器路徑與實際版本(用那個路徑執行一次);`lumos doctor` 多一段軟提醒(不計 issues,因為 `doctor --ci` 是推送前的硬擋,Homebrew 升版讓路徑消失不該擋住每個專案的推送;段落代號實作時照 doctor 既有代號挑一個沒用過的),在註冊的直譯器不存在或低於 3.14 時提醒「重跑 lumos install」。
10. **清擋路的舊碼**:測試的 `_toml_loads` 代解分支改回直接 `import tomllib`。會讀、複製或直接跑掛鉤的測試,用 grep 對測試檔找 `hooks/pre-`、`pre-push`、`pre-commit`、`post-commit` 的引用列出清單逐支檢查(不能只靠 `-k hook`,名稱含 hook 的只有約 41 支);其中模擬「PATH 上沒有 python 就放行」的斷言反轉成擋下,`t_hooks_python_fallback` 改成斷言三支掛鉤與四支安裝腳本的內嵌清單一致。精簡版生成器把第 2 點那段(用固定的開始、結束註解框起來)剝掉,`t_slim_*` 跟著確認產物不要求 3.14。
11. **收尾連帶**(不列進 lands_in):[[Issues/蘋果內建Python3.9跑全套仍紅]] 結案,依據寫「3.14 跑過全套綠」,不寫成「原因已查清」;它與 [[Systems/測試假綠形態]] 各有一條 `REVISIT:2026-10-29`,兩條都改寫成已由本計劃回答;[[Systems/筆記內容閘]] 那條 zip(strict=) 的 PITFALL 補一句下限已改、禁令為何保留(第 2 點);[[Projects/全repo審視_計劃]] F65 與 quick win 12(「Python 版本宣告訂成 ≥3.9」)各記一行被本計劃翻掉;掛鉤的既有家筆記([[Systems/每支檔有家]] 管 pre-commit、[[Systems/bound-tests-gate]] 管 pre-push)各加一行連到新系統筆記;存量漂移防線乙回來收尾時拿掉它為 3.9 加的事先篩選。
12. **每支檔有家**:新開 `Systems/python直譯器選擇` 管「找 3.14」這件事(負責:候選清單、驗版本、`python-path`、開頭檢查與重跑、找不到時的說明、`LUMOS_PYTHON` 與 `LUMOS_PYTHON_SEARCH_DIRS`;不負責:各入口自己的業務邏輯)。原本沒有家的 `install.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh` 交給 [[Systems/lumos-cli-lifecycle]](它已經管 `get.sh`);`scripts/hooks/post-commit` 交給 [[Systems/reversibility-governance-ledger]](它寫的 `.bypass-log.jsonl` 是那篇彙整的六本帳之一)。
13. **落地驗收**(寫成一篇驗證紀錄,plan_refs 連回本計劃):改到的既有錨點檔(三支掛鉤、測試總檔等)在工具鏈 repo 跑 `lumos anchor approve`;本機跑一次 `lumos install --force`,對 Claude 與 Codex 兩個部署位置的掛鉤檔各比一次 sha256,並確認設定檔裡寫的是加了引號的 3.14 絕對路徑——改 `merge-claude-settings.py` 不會自己重寫家目錄底下的設定。

## 條款

- [S1] 當 `lumos python-path` 或 lumos 開頭要找 Python,工具應照第 1 點的固定順序試候選,找到一個就停,只接受實際執行印出 ≥3.14 的那一個、並改用它印出的絕對路徑;`LUMOS_PYTHON` 有設但不是絕對路徑或不合格時應停下報錯,不往下找;uv 應帶 `--no-python-downloads`;設了 `LUMOS_PYTHON_SEARCH_DIRS` 時固定位置應只看它;驗法應隔開標準輸入並有單一與整份的逾時 [test:t_python_resolver_order_and_floor]
- [S2] 當 lumos 以主程式身分被 3.14 以前的 Python 啟動,工具應在執行完開頭幾行 import 後就檢查,找到 ≥3.14 就用它的絕對路徑跑同一支檔同一組參數並回傳它的回傳碼;找不到應印出需要的版本、現在的版本與路徑、找過的候選與各自結果、安裝指令,回 2,不印追蹤;`LUMOS_REEXEC_PYTHON` 等於自己又仍是舊版時應直接報錯;通過檢查後應清掉這個變數,子孫行程被舊版叫起時應照常重跑;版本已是 3.14 時不應因 `LUMOS_PYTHON` 重跑;被 import 載入時不應觸發。測試應在找得到真的舊版直譯器時用它跑,找不到時應明說這一格沒驗到,並比對輸出內容而不只比回傳碼 [test:t_lumos_old_python_reexec_or_explain]
- [S3] 當 pre-commit 或 pre-push 確定這次要叫 lumos、而 `lumos python-path` 找不到 ≥3.14(包括只找得到 3.9、或完全沒有 python),工具應擋下(rc 非 0)並印說明,不得改用較舊的 Python;圖譜不存在、staged 為空時應照舊放行,沒有 scripts/lumos 時應照舊只跳過要 python 的幾道;post-commit 應在只有 python3.14 的機器上照樣寫入跳過帳;掛鉤的內嵌段在 `set -euo pipefail` 下也不應中途結束 [test:t_hooks_block_without_python314]
- [S4] 當安裝入口在只有 python3.14、只有 Windows 的 py 啟動器、或只有商店替身的機器上執行,工具應把 lumos 叫起來(再由 lumos 找 3.14)或印安裝指令回 2,不得自行安裝;Windows 包裝應寫入實際執行成功的啟動方式 [test:t_installers_require_python314]
- [S5] 當註冊 Claude/Codex 掛鉤,工具應寫入目前執行的那一支直譯器的絕對路徑並加引號(路徑含空白時命令照樣可執行);merge-claude-settings.py 被 3.14 以前的 Python 執行時應改用 3.14 重跑自己,找不到時報錯回 2、不寫設定 [test:t_hook_cmd_uses_running_python]
- [S6] 當 CI 執行,應在 3.14 上跑全套並以釘版本的 ruff(py39)檢查三類必須 3.9 能解析的檔;doctor 印給消費專案的三處 CI 步驟提示應講明要用 Python 3.14 [test:t_ci_runs_python314_and_old_syntax_check]
- [S7] 當 scripts/lumos、scripts/merge-claude-settings.py 或 scripts/hooks/claude/*.py 被修改,它們仍應能被 3.9 語法解析:ruff 以 py39 為目標檢查語法錯誤,測試應附一行 3.12 才合法的樣本確認 ruff 真的會報;找得到真的 3.9 直譯器時應實際編譯一次;兩者都沒有時應明說沒驗到 [test:t_lumos_parses_under_old_grammar]
- [S8] 當 guard kill、合約測試閘本體或過濾探針展開測試指令,應都經同一支代入函式,以執行中的 lumos 那一支直譯器代入 `{python}` 並依平台加引號(路徑含空白時照樣可執行) [test:t_test_run_cmd_uses_running_python]
- [S9] 當新版 lumos 執行 update、消費專案的 pre-commit 還是舊的,應印一段升級注意;在 CI 裡找不到 3.14 時,說明應多一行 setup-python 怎麼設;精簡版生成器的產物不應含開頭版本檢查 [test:t_update_prints_python314_notice_and_slim_strips_floor]
- [S10] 當 Claude/Codex 設定裡註冊的直譯器不存在或低於 3.14,lumos doctor 應印軟提醒(不計 issues)叫人重跑安裝,lumos enforcement 應列出註冊的直譯器與版本 [test:t_doctor_flags_stale_hook_python]

## 回退

- **全部回退**:還原本計劃的提交(`.lumos/config.json` 的 `run_cmd` 必須跟 lumos 本體一起還原——舊版 lumos 不認得 `{python}`,會把它原樣交給 shell 得到 127)。再到每個已更新的消費專案用★全域或工具鏈來源那份★ lumos 跑 `lumos update`,把舊掛鉤複製回去(專案裡自帶的那份 lumos 已是新版,在只有 3.9 的機器上會回 2,用不了);有錨點基準線的消費專案接著跑 `lumos anchor approve --note "<回退原因>"`——掛鉤內容換回舊版,sha256 對不上基準線,推送前那道不可跳過的錨點檢查會擋。`lumos update` 會順手重寫整台機器的 Claude/Codex 設定(改回舊版的註冊寫法),這是機器全域的動作,同一台機器上還沒回退的其他消費專案共用同一份設定;舊版寫法照樣跑得動新舊掛鉤。
- **主線已有後續提交時**:還原前用真的 3.9 實際跑一次(`/usr/bin/python3 scripts/lumos --version` 加一組子集測試),不能只編譯——`def f(x: int | None)`、`import tomllib` 這類寫法編譯得過、執行才壞;掛鉤是 shell,用 `bash -n` 查語法。存量漂移防線乙若已合併、拿掉了 3.9 事先篩選,要一起補回來,否則 3.9 的 ast.parse 崩潰原樣重現。圖譜:`Systems/python直譯器選擇` 標 superseded、四篇 lands_in 節點改寫過的段落改回;Issue 結案、兩條 REVISIT、F65 與 quick win 12 的收尾不跟著還原,另外補一篇說明「下限退回 3.9」並重開那篇 Issue。
- **只回退「擋下」**:掛鉤在 `python-path` 失敗(找不到 3.14、`LUMOS_PYTHON` 不合格、找到的 python 執行失敗)時一律改成印提醒並跳過需要 lumos 的檢查——★是那幾道檢查不跑,不是改用 3.9 跑★;同時把 [S3] 與它的測試改成斷言放行,並經 `lumos update` 才到消費專案(有錨點基準線的要重簽)。後果要講明:只有 3.9 的機器上,掛鉤放行、但任何 lumos 指令照樣因第 2 點回 2,治理帳一筆都不會有;比本計劃之前(拿 3.9 跑檢查)還弱,兜底只剩 CI(3.14)。提醒文字要改成「找得到 Python X.Y,但需要 3.14,這次沒跑檢查」。
- 以上每一種回退本身都是一次提交,照紀律要跟圖譜的對應改動放同一個提交。
- 消費專案被擋時的暫時出口:裝 3.14,或設 `LUMOS_PYTHON` 指到一支 3.14 的絕對路徑。

## 實務隱患

- **守衛面(碰到)**:git 掛鉤從「沒 Python 就放行」改成「沒 3.14 就擋」,擋的條件變寬;錯的時候是誤擋。防法:固定位置涵蓋 Homebrew、uv、pyenv 的安裝目錄(圖形用戶端、排程這類路徑很短的環境、pyenv 鎖了舊版的目錄)、只在確定要叫 lumos 時才擋、擋下說明列出每個候選與它的結果、找 3.14 只有一份實作。
- **對外送出(碰到)**:改的是對外發佈的安裝說明與安裝腳本,更新後的消費專案在沒裝 3.14 的機器上提交會被擋、CI 會回 2。防法:`lumos update` 印升級注意、README 寫升級注意、doctor 的 CI 步驟提示講明要 3.14、擋下說明附三種平台的安裝指令與 `LUMOS_PYTHON` 的用法;不自動安裝任何東西,uv 探測帶 `--no-python-downloads`。
- **不可逆(碰到一半)**:程式碼還原提交就回去,但消費專案的掛鉤副本要逐一更新回去並重簽錨點,見〈回退〉。
- **自我治理(碰到)**:改的是治理守衛自己——掛鉤擋不擋、合約測試閘用哪支直譯器跑。改壞的後果是全專案誤擋或整道檢查沒跑。防法:[S3] 與 [S8] 釘住擋下與測試指令、改到的錨點檔重簽、落地驗收比 sha256。
- **效能**:掛鉤每次各找一次:shell 那段只是 `command -v`,之後一次 `python-path`(第一個候選就命中時約 0.1 秒內;要重跑時多約 0.3 秒,見第 2 點)。舊註冊(設定還寫著 3.9)在重跑安裝前每次呼叫 lumos 多一次重跑;第 9 點的提醒負責讓人去重跑。整份候選清單最壞 15 秒(每個候選都卡到逾時)。
- 已排除:金流:這個工具不碰任何付款或計費。

## 誠實界線

- **舊版要能解析那三類檔**:[S7] 用 ruff(py39,釘版本、附必紅樣本)與真的 3.9 編譯守語法;機器上兩者都沒有時守不到,測試會明說沒驗到。開頭幾行 import 之後才出現的載入期問題不影響 scripts/lumos(檢查在它們之前),merge-claude-settings.py 的檢查放在它自己那幾行標準庫 import(os、sys、subprocess)之後、其餘程式之前,道理相同。
- **全域 `lumos` 指令靠 `#!/usr/bin/env python3` 啟動**:完全沒有 `python3` 這個名字的機器(只用 uv 裝了 `python3.14` 的 Linux)上,打 `lumos` 在跑到第 2 點之前就失敗;git 掛鉤與安裝入口不受影響(內嵌清單含 `python3.14` 與固定位置)。
- **掛鉤第一跳沒有逾時**:shell 那段只用 `command -v` 與「檔案可執行」挑,不執行候選;但接著用挑到的那支跑 `lumos python-path` 這一步沒有逾時(macOS 沒有內建 `timeout` 指令)。那支直譯器一啟動就卡住時,掛鉤跟著卡住;lumos 內部的候選驗證有逾時,不受影響。這種機器要 `uv python install 3.14 --default` 或自己加 `python3` 別名;擋下與安裝說明會提這一句。
- **PATH 上的 python 本身仍被信任**:shell 那段找到的候選(`LUMOS_PYTHON` 以外)只看 `command -v`,不驗是不是 python;pre-commit/pre-push 會驗 `lumos python-path` 回的路徑真的是 3.14 python 才拿來跑閘,但安裝腳本與 post-commit 直接用找到的那支。PATH 上放假程式的人本來就控制了這台機器,改動前掛鉤拿 PATH 上的 `python3` 也一樣(代碼審 r3 外家席)。
- **`--no-verify` 會留跳過帳、不會留閘的帳**:post-commit 照舊記下「這次跳過了」,但被擋的那幾道檢查本身沒有跑,也沒有它們的紀錄。
- **設定檔裡的絕對路徑會過期**:uv、pyenv、venv、Homebrew 升版都可能讓它消失;第 9 點的提醒是事後偵測,不是事前防止。
- **消費專案自己的 CI 沒有偵測**:它們的 workflow 用 3.12 時,更新後 CI 回 2;靠 CI 裡回 2 的那段說明自己講怎麼設 setup-python、doctor 的 CI 步驟提示,與新版執行 update 時的升級注意。
- **第一個專案看不到升級注意**:全域 lumos 指到來源 clone,`lumos update` 先在同一個行程裡拉新來源再複製,執行的是拉新之前就載進記憶體的舊程式,印不出新版才加的升級注意(代碼審 r1);同一台機器第二個專案起才由新程式執行。所以 CI 那一段改成失敗現場自己講清楚,本機掛鉤擋下的訊息本來就附安裝指令。
REVISIT:2026-12-29 看這段期間有沒有「掛鉤誤擋」「消費專案 CI 因版本回 2」的回報;有的話補偵測(doctor 讀消費專案 workflow 的 setup-python 版本)

## 實作時的決定(跟上面寫的不一樣或更細的地方)

- **enforcement 的 python 列狀態不變**:維持 active,註冊的直譯器與問題寫在說明文字裡。原本想有問題就標 degraded,但既有測試與約定是「四支掛鉤、兩支 git 掛鉤、python、CI 共 8 列 active」,改狀態會動到分母;提醒改由 doctor 的 Q 段(軟提醒、不計 issues)負責。
- **精簡版生成器只剝「呼叫版本檢查」那三行**:用 `python-floor gate begin/end` 兩行註解框起來。找 3.14 的函式本身留著——`lumos python-path` 與 doctor Q 段都用到它們,整段剝掉精簡版一跑到那些地方就會出錯。
- **掛鉤與安裝腳本的內嵌清單也認 `LUMOS_PYTHON_SEARCH_DIRS`**(冒號分隔):內嵌清單自己也寫了固定位置,不能被換掉的話,維護者的 Mac 上造不出「找不到 3.14」的掛鉤測試。
- **doctor 新段代號是 Q**:doctor 已有兩段都叫 N,Q 是還沒用過的字母。
- **升級注意的觸發條件**:更新前消費專案的 pre-commit 裡沒有 `python-path` 字樣、而且這次真的把 pre-commit 換新了,才印。只有新程式執行 update 時才走得到(見〈誠實界線〉第一個專案那條)。
- **doctor Q 段只看 lumos 自己註冊的掛鉤**(代碼審 r1、r2、r3):命令的第二段是 lumos 自家掛鉤檔、放在這一家 lumos 裝的那個目錄(Claude 認 `${HOME}/.claude/hooks` 與展開後的家目錄路徑,Codex 認 `CODEX_HOME/hooks`,兩家分開、精確比對,不用後綴——後綴會收進別人家目錄底下的 `.claude/hooks`)、第一段看起來是 python(含 free-threaded 的 `python3.14t`),才拿去探版本;自家掛鉤檔名單只有一份,enforcement 各列找的檔名必須在裡面(測試守)。第一版把任何含 `hooks/` 的命令都拿第一個字跑 `-c <探針>`,在維護者自己的機器上把別的工具的掛鉤(shell 條件式、`bash` 包一層)列成問題,還真的執行了別人的腳本。
- **shell 那段先認 `LUMOS_PYTHON`**(代碼審 r1、r2):只收絕對路徑、而且實際執行印得出記號的(真的是 python)才用它叫 lumos,版本夠不夠仍由 lumos 判;不合格就記下原因往下找,找不到任何 python 時說明第一行講它為什麼被略過。第一版只看能不能執行:設成 `/usr/bin/true` 時安裝腳本回 0 卻沒裝、post-commit 直接把程式交給它跑而漏寫跳過帳(r2 外家席)。找不到時的說明叫人設它,第一步不認等於給了一個用不了的出口。
- **目前目錄裡的同名檔不收**(代碼審 r1 資安席、r2 正確性席):Windows 找指令會先看目前目錄,掛鉤的目前目錄是 repo 根;找直譯器、問 uv、挑包裝啟動指令都改用絕對路徑執行,Windows 上落在目前目錄本身的不收、各平台 PATH 相對路徑項找到的不收。只擋目前目錄本身、不擋整棵子樹:第一版擋子樹,目前目錄是家目錄或磁碟根時正常裝在底下的直譯器也被當成不存在。位置看檔案放在哪個目錄、只解析目錄那一層:第二版整條解析,repo 根放一個指進子目錄的符號連結就逃過比對(r3 外家席)。 包裝檔 `lumos.cmd` 裡照舊寫指令名(版本管理工具換 exe 是常態),那一層不在這次範圍:在陌生 repo 根打 `lumos`,cmd.exe 解析 `py`/`python` 仍會先看目前目錄,這個攻擊面在本計劃之前就存在。PowerShell 安裝入口不受影響(PowerShell 不執行目前目錄裡沒寫路徑的指令)。
REVISIT:2026-12-29 決定 lumos.cmd 要不要改寫絕對路徑,或在包裝檔裡先設 NoDefaultCurrentDirectoryInExePath;順便看這段期間有沒有 Windows 使用者
- **pre-commit/pre-push 驗 `python-path` 回的路徑**(代碼審 r3):要是絕對路徑、執行起來是 3.14 以上的 python 才拿它跑閘;叫 lumos 的那支是假的時,閘會全部假放行。
- **uv 的結果分三種**(代碼審 r2、r3):逾時、執行失敗(帶回傳碼、第一行 error 與最後一行:真的 uv 把壞掉的檔名印在第一行、原因印在最後一行)、找不到 3.14。uv 沒找到跟自己出錯回傳碼都是 2,只能看錯誤訊息有沒有 `No interpreter found`。
- **安裝腳本在 `LUMOS_PYTHON` 被略過、改用別支時當場講**(代碼審 r3、r4):不然安裝安靜成功,下一次提交才因同一個值被擋。印的是原因加後果(lumos 只認 `LUMOS_PYTHON`,之後的檢查會擋下),放在 shell 共用段裡,七個呼叫端不各寫一份(r4 架構對齊席:第一版四支安裝腳本各貼一行、放在測試守不到的地方)。包裝檔 `lumos.cmd` 裡照舊寫指令名(版本管理工具換 exe 是常態),那一層不在這次範圍:在陌生 repo 根打 `lumos`,cmd.exe 解析 `py`/`python` 仍會先看目前目錄,這個攻擊面在本計劃之前就存在。PowerShell 安裝入口不受影響(PowerShell 不執行目前目錄裡沒寫路徑的指令)。
- **只推刪除也擋**:推送前的錨點檢查不看這次推了哪些 ref、每次都叫 lumos,所以「確定要叫 lumos」恆成立。
- **版本檢查之前的 import 有清單**(代碼審 r1):ruff 只查語法,檔頭多 import 一個 3.11 才有的模組,3.9 啟動會在印出說明之前就炸;[S7] 的測試多一格,版本檢查之前只准 import 清單上的標準庫模組。
- **測試裡的假 lumos**:幾支掛鉤測試用假 lumos 記錄呼叫,現在掛鉤第一步會問 `python-path`,三個假 lumos 補上「印自己的直譯器路徑」這個回答;精簡版「錨點非唯一」那支測試原本把假錨點塞在第一個 `if __name__`,那一個現在是會被剝掉的版本檢查,改塞在最後一個(真正的主程式入口)。

## 合約候選

設計審過閘後列的「改了就壞」候選;候選不等於已標,實作與代碼審後照「不確定不標」走 guard scaffold → bind → audit。
- git 掛鉤找不到 3.14 時,會擋的閘擋下、不改用較舊的 Python 跑([S3])。
- lumos 開頭檢查只在主程式身分且版本低於 3.14 時觸發,被 import 不觸發;通過後清掉 `LUMOS_REEXEC_PYTHON`([S2])。
- scripts/lumos、merge-claude-settings.py、Claude 掛鉤腳本維持 3.9 能解析([S7])。
- 讀 `run_cmd` 的地方都經同一支代入函式([S8])。
- post-commit 寫跳過帳不設版本下限([S3])。

## 審計修正紀錄

- r1(★這一段列的共用 shell 檔、git config lumos.python、`LUMOS_PYTHON` 在本體生效、perl 逾時,r2 已整類拿掉★;2026-09-29,7 席:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet 5.5;外家否決 Codex;前置掃描已跑):51 條,去重後約 30 件,major 33 條(機器數各報告的 F 標題與 severity 行;最初手數成 52/28,已更正);全數錨定(架構對齊席一句「lands_in」不到 10 字不採信,那條改用其敘述)。卷證在 `governance/review-reports/最低python版本改3-14/r1-*`。
  - 折入(全數):版本檢查搬到檔案最前面(正確性);scripts/lumos 維持 3.9 能解析、ruff 目標版本不改(正確性、接手,推翻原本第 6 點);候選清單加 git 設定與固定位置、`LUMOS_PYTHON` 有設就只認它、`py` 兩份都有、uv 帶 `--system --no-python-downloads`、一律用印出的絕對路徑、驗法隔開輸入並設逾時(邊界、正確性、接手、併發、外家);防重跑變數命名並在通過後清掉(併發、正確性、邊界、接手、架構對齊);掛鉤在確定要叫 lumos 時才擋、共用檔缺席另一段說明、找一次(邊界、正確性、接手、併發);post-commit 不設下限(正確性);註冊命令加引號(邊界、外家、正確性);安裝入口補齊候選並真的執行(邊界、正確性、外家、接手);測試指令 `{python}` 與測試總檔版本檢查(正確性);三張名單登記(接手、正確性、外家);四支沒家的檔交給 lumos-cli-lifecycle(外家);落地驗收比 sha256(外家);doctor 偵測過期路徑(回滾);消費專案通知與 CI 範例(接手);回退節重寫(回滾);CHANGELOG 前後矛盾(正確性、外家、接手);ONBOARDING 與筆記內容閘收尾(接手);lands_in 拿掉每支檔有家與測試假綠形態(架構對齊)。
  - 鏡像核對(便宜席,材料含席報告目錄):51 條已處理 43、部分 8、未處理 0、相反 0;新矛盾 7。已補(★其中 git config、`LUMOS_PYTHON` 在本體生效、perl 逾時、共用檔四項 r2 已整類拿掉,見 r2 段★):`git config lumos.python` 由 init/update/install 寫入並進 [S1];get.sh 沒有共用檔改成叫人加 --pull、不退回 python3;`LUMOS_PYTHON` 值的語意與在 lumos 本體也有效;python3/python 挪到候選最後、找到即停;shell 有 perl 時用 alarm 設逾時;全域 lumos 的 shebang 與排程腳本默默失效寫進界線;新系統筆記列進 lands_in;[S6] 測試名改掉 py314 字樣、CI 加 ruff 守 [S7];post-commit 不 source 的說法統一;三份清單的比對與平台豁免寫明;白話段刪掉已被另一會談修掉的「測試總檔有 3.12 寫法」。
- r2(2026-09-29,7 席全新,同編制;審 r1 折入後的整份):53 條,major 29 條(機器數;架構對齊席第一次交的報告沒有逐條標題,請它只改格式重交,內容不變);全數錨定。卷證在 `governance/review-reports/最低python版本改3-14/r2-*`。
  - 結論:大部分 major 出在 r1 為了補洞新加的四樣東西(掛鉤共用 shell 檔、`git config lumos.python`、`LUMOS_PYTHON` 在本體也生效、perl 逾時),同一類問題連兩輪,換形狀、整類拿掉,不再逐條補:找 3.14 只留 lumos 裡的 Python 一份(新增 `lumos python-path`),shell 只負責找任何版本的 python 把 lumos 叫起來(外家 F1 舊版更新程式漏發新檔、邊界 F4 set -e、F5 Git Bash \r、正確性 F13、接手 F1 get.sh --pull、回滾 F1 錨點都因此不存在);`git config lumos.python` 拿掉,改由固定位置補 uv 與 pyenv 目錄(正確性 F4、併發 F2、邊界 F3 F8);`LUMOS_PYTHON` 只在版本不夠時生效、必須是絕對路徑(正確性 F1 F14、邊界 F1、併發 F1、接手 F2、外家 F2 的無限重跑)。
  - 其餘折入:固定位置的測試接縫 `LUMOS_PYTHON_SEARCH_DIRS`(正確性 F2);`{python}` 的代入點是三處,不是四處(過濾探針就是那支冒煙測試;鏡像核對更正);Windows 包裝與 get.ps1 用「真的執行成功」挑(正確性 F5、邊界 F6、外家 F4);`{python}` 集中代入並依平台加引號、三個代入點(正確性 F6、架構對齊 F1、接手 F3、外家 F6);CI 範本不存在→改成 doctor 三處 CI 步驟提示(正確性 F7、接手 F11);3.9 能解析的守衛擴到 merge 與 Claude 掛鉤、ruff 釘版本附必紅樣本(正確性 F8、接手 F6、外家 F5);pre-commit 沒有 scripts/lumos 時的現況寫對(正確性 F9、接手 F4);uv 兩步驗與說明改寫(正確性 F10);CI 編譯步驟沒涵蓋 lumos(正確性 F11);重跑成本含 0.22 秒解析(正確性 F12、併發 F3);post-commit 清單補 python3.14(外家 F3);merge 被舊版叫起時改用 3.14 重跑(外家 F1 第 3 點);ONBOARDING 正文指令(外家 F7);doctor 段落定性為軟提醒並併入 enforcement(接手 F7);測試盤點改用 grep(接手 F8);範圍對排程腳本與精簡版的陳述更正、生成器剝掉開頭檢查(接手 F9 F10);升級注意的觸發條件與落地驗收寫成驗證紀錄(接手 F12 F13);回退補錨點重簽、update 會改全機設定、run_cmd 要跟本體一起退、3.9 要實跑不只編譯、圖譜節點處理、「只回退擋下」三條擋下路徑一起退(回滾 F1–F5);CI 裝 ruff 與新增做法的理由寫明(架構對齊 F2);掛鉤家筆記加連結(架構對齊 F3)。
  - 鏡像核對(便宜席,材料含席報告目錄):53 條已處理 32、已處理(機制拿掉)18、部分 3、未處理 0、相反 0;新矛盾 6。已補:掛鉤與安裝入口的「任何版本」清單加固定位置並排在 python3 前(圖形用戶端短路徑跳對話框、Linux 只有 ~/.local/bin);pre-commit 在只提醒的閘遇到找不到 3.14 時跳過、會擋的閘才擋;代入點更正為三處;merge 的 import 順序說法統一;掛鉤第一跳沒逾時寫進界線;post-commit 交給 reversibility-governance-ledger;掛鉤家筆記點名;測試要清開發者環境的 LUMOS_PYTHON;回退本身要提交;r1 段標明已撤的機制。
- 代碼審 r1(2026-09-29,5 席:兩席單 reviewer 分段審(核心 opus、掛鉤與安裝 sonnet 5.5)、架構對齊 sonnet、資安 sonnet、外家 Codex;凍結 patch 3384 行拆五份):13 條,blocking 4(機器數;各席總結句)。卷證在 `governance/review-reports/code-最低python版本改3-14/r1-*`。
  - 折入(全數):doctor Q 段與 enforcement 只看 lumos 自家掛鉤(核心 F1、資安 F1);升級注意在第一個專案印不出→CI 裡的說明自己講、條款 [S9] 照實改寫(核心 F2);doctor 測試改比問題數(核心 F3);註解更正(核心 F4);找不到時列出每個候選(核心 F5、外家 F2);shell 第一步認 `LUMOS_PYTHON`(外家 F1);shell 與 lumos 兩份候選清單逐項比對(架構對齊 F1);版本檢查之前的 import 清單(掛鉤 F1);升級說明補 Codex 要重新信任(掛鉤 F2);只推刪除也擋的理由寫進掛鉤(掛鉤 F3);Windows 目前目錄的同名檔不收(資安 F2)。
- 代碼審 r2(2026-09-29,4 席全新:單 reviewer opus、架構對齊 sonnet、資安 sonnet、外家 Codex;只審 r1 修正差異 1047 行):9 條,blocking 1(機器數;各席總結句;資安席 clean)。卷證在 `governance/review-reports/code-最低python版本改3-14/r2-*`。
  - 折入(全數):shell 第一步認 `LUMOS_PYTHON` 要驗絕對路徑與真的是 python、不合格講原因(外家 F1、正確性 F3);自家掛鉤篩選收 `python3.14t`、比對目錄(正確性 F1、外家 F2);目前目錄防護只擋目前目錄本身與 PATH 相對路徑項(正確性 F2);lumos.cmd 那層補回頭條件(正確性 F4);自家掛鉤名單只留一份、enforcement 的檔名由測試守在名單裡(架構對齊 F1);PowerShell 安裝入口不需要目前目錄防護的理由寫進腳本(架構對齊 F2);uv 逾時與執行失敗分開講(外家 F3)。
- 代碼審 r3(2026-09-29,4 席全新,同編制;只審 r2 修正差異 939 行;上限最後一輪):8 條,blocking 3(機器數;各席總結句;資安席 clean)。卷證在 `governance/review-reports/code-最低python版本改3-14/r3-*`。第 3 輪仍有 major,停下來問人;Enzo 同日裁「修完再破例審一小輪」(只審這次修正差異)。
  - 折入(全數):目前目錄判斷改看檔案所在目錄、不跟符號連結(外家 F2);pre-commit/pre-push 驗 python-path 回的路徑、PATH 上的 python 仍被信任寫進界線(外家 F1);doctor 掛鉤目錄兩家分開精確比對、測試拿合併程式真的寫出的兩家設定餵(架構對齊 F1、外家 F4);變數改名(架構對齊 F2);uv 出錯與找不到分開(單 reviewer F1、外家 F3);安裝腳本當場講 LUMOS_PYTHON 被略過(單 reviewer F2)。
- 代碼審 r4(2026-09-29,破例一小輪,Enzo 核准;4 席全新,同編制;只審 r3 修正差異 596 行):5 條,blocking 1(機器數;各席總結句;資安席、外家席 clean)。卷證在 `governance/review-reports/code-最低python版本改3-14/r4-*`。仍有 major,再問人;Enzo 同日裁「修完直接推」——★r4 的修正差異沒有經過審查★,每條各有翻紅測試。
  - 折入(全數):印 `LUMOS_PYTHON` 被略過的原因搬進 shell 共用段、並講後果(架構對齊 F1、單 reviewer F1);掛鉤驗 3.14 只看最後一行,跟 lumos 的探針一致(單 reviewer F2);uv 出錯帶第一行 error 與最後一行、測試照真 uv 的多行形狀(單 reviewer F3);lumos.cmd 那段搬回目前目錄那條(單 reviewer F4)。
