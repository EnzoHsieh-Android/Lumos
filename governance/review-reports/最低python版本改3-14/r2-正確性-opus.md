severity: major

# r2 正確性與邏輯席(opus)

審材:最低python版本改3-14-r2.md(106 行,凍結稿)。對照 repo:clone-314(HEAD 92add6cd)。實驗一律在 mktemp 目錄,沒動任何 repo。

## F1 LUMOS_PYTHON 指向包裝腳本(pyenv/asdf 的 shim、自寫 wrapper)時開頭檢查會無限重跑,防重跑變數攔不到
severity: major
blocking: 是 — 照字面實作,設了 LUMOS_PYTHON 的 pyenv 使用者每個 lumos 指令、每次 git commit/push 都卡死在 exec 迴圈
引句:「或 `LUMOS_PYTHON` 有設、而且不是目前這一支(兩者都比 `os.path.realpath`)」
file: `scripts/lumos:35508`
1. 第 2 點的條件是 realpath(LUMOS_PYTHON) ≠ realpath(sys.executable) 就去找、找到就重跑;重跑的目標卻是候選「印出的 sys.executable」(第 1 點)。當 LUMOS_PYTHON 是一支 shell 包裝(pyenv/asdf/mise 的 shim 都是 bash 腳本,`export LUMOS_PYTHON=$(command -v python3.14)` 在 pyenv 機器上拿到的就是 shim),包裝的 realpath 是包裝自己,印出的 sys.executable 是真正的直譯器,兩者永遠不相等。
2. 重跑後的新行程版本是 3.14,所以防重跑規則(要求「版本卻還是舊的」才算失敗)不會觸發;新行程再判一次 LUMOS_PYTHON 不相等,又重跑一次,沒有盡頭。
3. 實測(mktemp 目錄,照第 2 點字面寫的 20 行模擬):`wrap.sh` 內容 `exec /opt/homebrew/bin/python3.14 "$@"`,`LUMOS_PYTHON=wrap.sh`,不管從 /usr/bin/python3(3.9)還是 /opt/homebrew/bin/python3.14 啟動,每一輪都印 `reexec -> /opt/homebrew/opt/python@3.14/bin/python3.14`,連重跑 5 次仍不相等(模擬裡加了 5 次上限才停,rc 99)。
4. git 掛鉤一樣中招:shell 那份照第 1 點拿印出的真路徑去跑 lumos,LUMOS_PYTHON 還在環境裡,lumos 開頭判不相等,進同一個迴圈。Claude 掛鉤呼叫 lumos 時也一樣,會一直卡到外層預算把它砍掉,掛鉤就靜默不生效。
5. Windows 走子行程,同一個迴圈會變成一層套一層的子行程。⚠ Windows 的 App Execution Alias(`WindowsApps\python3.14.exe`)與 uv 在 Windows 上的 trampoline 也是「包裝的路徑 ≠ 印出的 sys.executable」,推論會中招,沒在 Windows 真機驗。
6. 防重跑規則只能抓到「重跑到的還是舊版」,這件事在「拿印出的路徑重跑」的設計下幾乎不會發生;真正會發生的是「重跑後身分還是對不上」,規則卻沒涵蓋。比對的對象要改成「LUMOS_PYTHON 驗證時印出的 sys.executable」,或者只要 LUMOS_REEXEC_PYTHON 等於自己就一律視為已通過、不再比 LUMOS_PYTHON。[S2] 的測試也要加一格 shim 型的 LUMOS_PYTHON。

## F2 固定位置是絕對路徑、又沒有給測試用的覆寫口,[S2][S3][S4]「找不到 3.14」那一格在維護者的 Mac 上造不出來
severity: major
blocking: 是 — 沒有覆寫口,這些測試在本機要嘛翻紅擋住推送前的全套,要嘛被寫成跳過、變成假綠
引句:「④固定位置 `/opt/homebrew/bin/python3.14`、`/usr/local/bin/python3.14`、`$HOME/.local/bin/python3.14`」
file: `scripts/test_lumos.py:3697`
1. [S3] 要驗「只找得到 3.9、或完全沒有 python → 擋下」;[S2] 要驗「找不到 → 印說明回 2」;[S4] 要驗「只有商店替身 → 印安裝指令回 2」。既有的掛鉤測試造「沒有 python」的方法是縮 PATH(例如 `_precommit_run` 直接帶 os.environ 去跑 bash)。
2. 第 1 點的候選④有兩條是寫死的絕對路徑,改 PATH 蓋不掉。這台機器 `/opt/homebrew/bin/python3.14` 存在(實測 `ls -la`),所以不管 PATH 怎麼縮,共用檔都會找到 3.14、不會擋,[S3] 的斷言會紅。只有 `$HOME/.local/bin/python3.14` 能靠改 HOME 蓋掉。
3. 候選②`git config lumos.python` 不指定範圍時會讀到開發者的全域 git 設定,測試還要設 `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`;開發者 shell 裡的 `LUMOS_PYTHON` 也會漏進子行程(候選①「有設就只認它」)。spec 對這三個漏洞都沒交代測試要怎麼隔離。
4. CI 的 ubuntu 用 setup-python 把 3.14 裝在 /opt/hostedtoolcache,④ 在 CI 上都不存在,所以同一支測試在 CI 綠、在維護者的 Mac 紅。pre-push 在本機會跑全套(`scripts/hooks/pre-push:476`),實作者最可能的反應是「有 /opt/homebrew/bin/python3.14 就 _SrcOnly 跳過」,本機就永遠沒驗到擋下這條。
5. spec 要寫明一個只給測試用的覆寫口(例如用環境變數換掉④的清單),並把它列進第 1 點的同步測試與豁免;不寫的話,實作者自己加的覆寫口就會變成三份清單以外、沒人管的第四個入口。

## F3 get.sh 叫人「加 --pull 重跑」,但 --pull 是 bootstrap 裡面才做的,加了也還是同一句
severity: major
blocking: 是 — 手上有舊安裝複本的使用者照指示加 --pull 還是收到同一句 rc 2,裝不起來
引句:「`get.sh` clone 或已存在之後 source 共用檔;沒有共用檔(舊的安裝複本、沒帶 `--pull`)就印」
file: `get.sh:45`
file: `scripts/lumos:18370`
1. get.sh 自己只負責 clone,既有複本的 `git pull` 是 `lumos bootstrap --pull` 的第 1 步做的(`cmd_bootstrap` 裡的 `if pull:` → `_pull_source_or_abort`);get.sh 只是把 `--pull` 轉給 bootstrap。
2. 照第 5 點,get.sh 在「clone 或已存在之後」、呼叫 bootstrap 之前就 source 共用檔。舊複本(沒有共用檔)加 `--pull` 重跑:get.sh 看到複本已存在 → source 共用檔 → 不存在 → 印「請加 --pull 重跑」回 2,根本走不到 bootstrap 去 pull。
3. 這正好是第 5 點想處理的情境(curl 下來的 get.sh 是新版、`$LUMOS_HOME` 是舊複本)。要嘛 get.sh 在有 `--pull` 時自己先 `git -C "$LUMOS_HOME" pull`,再 source;要嘛訊息改成一行可以直接照抄的 `git -C … pull`。[S4] 的測試要有「舊複本 + --pull」這一格。

## F4 寫入 git config lumos.python 的時機漏了 bootstrap 接掛鉤那條路,install 又不屬於任何 repo
severity: major
blocking: 是 — 候選②就是為新隊友、pyenv 鎖版目錄這類機器設的,照字面實作卻正好在這些機器上寫不進去
引句:「`lumos init`、`lumos update`、`lumos install` 在該 repo 跑完時,把自己的 `sys.executable` 寫進去」
file: `scripts/lumos:18415`
file: `scripts/lumos:16370`
1. 新機器、新隊友的上手入口是 get.sh → `lumos bootstrap`。在已經是 lumos 專案的 repo 裡,bootstrap 走分支①,只呼叫 `_set_hooks_path(root)`(註解寫「git config 每機器要重接」),不經 init 也不經 update;隊友平常也不會跑 update(那是把 vendored 檔提交進 repo 的人才跑)。所以照字面實作,隊友機器上的 `.git/config` 永遠不會有 lumos.python。
2. 第 1 點舉的受益情境是「pyenv 鎖了專案版本的目錄」:專案 `.python-version` 鎖 3.9 時,`python3.14` shim 會報「command exists in these versions」後失敗,③ 就落空。這時只有②救得了,偏偏②在這條路上是空的。寫入點應該跟 `core.hooksPath` 綁在一起(`_set_hooks_path`),那才是每台機器、每個 clone 各做一次的地方。
3. bootstrap 分支③是用 Python 直接呼叫 `cmd_init(...)` 函式,不經過 main 的 init 分派。寫入邏輯如果放在 main 的分派之後,這條路也會漏掉;spec 沒指定放哪一層。
4. `lumos install` 是機器層指令(裝 `~/.local/bin/lumos`、skills、全域掛鉤),不屬於任何 repo。「該 repo」如果解讀成目前所在目錄:在家目錄跑會因為不是 git repo 而失敗(git config rc 128,spec 沒說失敗了怎麼辦);在某個無關的 repo 裡跑,就會把設定寫進那個 repo。spec 要嘛把 install 從名單拿掉,要嘛明寫寫到哪一個 repo(例如來源 repo `_src_repo`)。

## F5 lumos.cmd 只看 PATH 上有沒有 python3/python 就寫進去,商店替身永遠在,[S4] 宣稱的「只有商店替身也找得到真的 3.14」會在安裝完之後壞掉
severity: major
blocking: 是 — Windows 預設設定下(python.org 安裝器沒勾 Add to PATH),安裝顯示成功,但之後每次打 lumos 都叫到商店替身,lumos 從此啟動不了
引句:「PATH 上有 `python3`/`python` 就寫指令名,都沒有而有 `py` 就寫 `py -3`」
file: `scripts/lumos:16394`
1. 現有程式是 `next((c for c in ("python3", "python") if _shutil.which(c)), "python")`,只看有沒有這個名字。Windows 10/11 預設在 `%LOCALAPPDATA%\Microsoft\WindowsApps` 放了 `python.exe`、`python3.exe` 兩個 App Execution Alias,而且這個資料夾預設就在 PATH 上。所以 `which("python3")` 幾乎一定找得到,結果就是替身。
2. 第 5 點自己寫了「候選找得到一律要真的執行成功才算(Windows 的商店替身 python.exe 找得到、執行卻失敗)」,但同一段給 lumos.cmd 的規則還是「有就寫」,沒套用這條。
3. 情境:只裝了 python.org 的 3.14(會附 `py`,沒加 PATH)。get.ps1 透過 `py -3.14` 找到真的 3.14,跑 `lumos install`;install 寫出 `python3 "…\lumos" %*`。之後每次打 `lumos` 都跑到替身,印「Python was not found…」,lumos 開頭的檢查根本沒機會執行。[S4] 列的「只有 py 啟動器」「只有商店替身」兩種機器正好就是這個情境。⚠ 沒在 Windows 真機驗,靠的是 Windows 預設別名的已知行為加上第 5 點自己的敘述。
4. 挑選規則要改成「真的執行成功才寫」,或在找不到能執行的 python3/python 時寫 `py -3`;改完之後,`t_windows_interpreter_pick_matches_slim` 那條「完整版比精簡版多一個 py」的對齊條件也要跟著改寫。

## F6 {python} 直接字串代入 shell 命令,沒有加引號,而且 run_cmd 被代入的地方有三處,spec 只點名兩道閘
severity: major
blocking: 是 — Windows 的 3.14 裝在 `C:\Program Files\…` 時,每一支綁定測試都會跑紅(這正是第 6 點想修的症狀);代入漏一處的話,推送前的判定會錯
引句:「`.lumos/config.json` 的 `run_cmd` 改成 `{python} scripts/test_lumos.py -k {method}`,由 lumos 代入自己的 `sys.executable`」
file: `scripts/lumos:12411`
file: `scripts/lumos:12599`
file: `scripts/lumos:32067`
file: `scripts/lumos:32116`
1. run_cmd 是用 `subprocess.Popen(cmd, shell=True)` 跑的(`_kill_run`)。現在的 `{method}` 代入之所以安全,是因為方法名只允許英數字與底線。`sys.executable` 是路徑,Windows 全使用者安裝的預設位置是 `C:\Program Files\Python314\python.exe`,含空白。不加引號,cmd.exe 會把命令切在空白處;用 `shlex.quote` 會包單引號,cmd.exe 又不認單引號。POSIX 與 Windows 要各用各的引號規則(`shlex.quote` / `subprocess.list2cmdline`)。[S5] 的註冊命令明寫要加引號,這裡沒寫。
2. 代入 `{method}` 的地方有三處:guard kill(`_kill_run` 前的 replace)、`_bound_tests_filter_probe`(判斷這條測試指令能不能只跑一支)、`_run_bound_tests`(合約測試閘與 spec-gate 共用)。[S8] 只點名「合約測試閘或 guard kill」。如果只在點名的兩處代入,過濾探針會把字面上的 `{python} …` 丟給 shell,得到 127。
3. 牽連固定席 [[Systems/bound-tests-gate]] 的合約:「★證不出跑過(unfilterable)★ → blocked=True rc1」。字面 `{python}` 或沒加引號的路徑造成的 127,在閘裡會被判成紅燈或「證不出跑過」,每一次推送都會被 code-loop check 擋下,原因卻不是測試本身。
4. spec 要寫明:代入點集中在讀設定那一層(`load_platforms` 讀 run_cmd 的地方),而且依平台加引號。[S8] 的測試要有一格「路徑含空白」。

## F7 [S6] 要改的「lumos 給消費專案的 CI 範例」在 repo 裡不存在
severity: major
blocking: 是 — 這條條款沒有對象可以實作,〈實務隱患〉對外送出那一項靠它擋的「消費專案 CI 一更新就回 2」其實沒有被擋
引句:「lumos 產生給消費專案的 CI 範例應包含安裝 3.14 的步驟」
file: `.github/workflows/ci.yml:19`
1. 在 scripts/lumos、skills/、README 兩份、ONBOARDING、ARCHITECTURE、docs/ 裡找 `setup-python`、`runs-on`、`actions/checkout`、`doctor --ci` 的 YAML 範例:scripts/lumos 沒有任何產生 workflow 的程式;ARCHITECTURE.md 只有一張流程圖;`setup-python` 只出現在工具鏈自己的 ci.yml 和一篇發版計劃。沒有「lumos 建議給消費專案」的那份範例。
2. 所以 [S6] 綁的 `t_ci_runs_python314_and_old_syntax_check` 後半段沒有東西可以斷言。實作者要嘛自己發明一份新範例(這樣就是新功能,spec 沒寫它放在哪、誰來發佈),要嘛默默跳過。
3. 真正會壞的是:消費專案自己寫的 CI 在 ubuntu-latest(python3 是 3.12)上跑 `python scripts/lumos doctor --ci`,更新後會找不到 3.14、回 2。spec 要嘛寫明範例要新建在哪裡、怎麼送到消費專案手上,要嘛把這句從 [S6] 與〈實務隱患〉拿掉,只保留 `lumos update` 印出的升級注意,並承認這一項沒有擋。

## F8 [S5]、[S8] 說舊版 Python 會得到「回 2 加說明」,但這兩支檔能不能被 3.9 解析沒有任何東西守
severity: minor
blocking: 否 — 實作當下是對的,等之後有人在這兩支檔用了 3.10 以後的語法才會壞;修法是把 [S7] 的範圍擴大
引句:「merge-claude-settings.py 被 3.14 以前的 Python 直接執行時應報錯回 2、不寫設定」
1. 第 2 點講得很清楚,Python 要先解析完整支檔才會執行第一行,所以才特別要求 scripts/lumos 維持 3.9 能解析,並用 [S7] 守住。merge-claude-settings.py 和 scripts/test_lumos.py 也要在 3.9 上跑到開頭的檢查才印得出說明,但 [S7] 只守 scripts/lumos。
2. 下限改成 3.14 以後,這兩支檔用 match 或 PEP 701 的 f-string 看起來完全合法(spec 範圍外的段落甚至說舊寫法可以慢慢清)。一旦用了,3.9 會直接丟 SyntaxError 加追蹤、回 1,[S5]、[S8] 宣稱的行為就消失了;test_lumos.py 最近才修過一次 3.12 語法(提交 8f691726)。
3. 目前實測這兩支都還能被 3.9 解析(`/usr/bin/python3` compile 通過)。`.lumos/lint.json` 的 ruff py39 雖然是整個 repo 都套,但指令尾巴是 `|| true`、只輸出 SARIF,⚠ 它是不是一道會擋的閘,沒有逐一確認。[S7] 應該把這兩支檔一起列進去。

## F9 [S3] 寫「沒有 scripts/lumos 時照舊放行」,但現況 pre-commit 沒有 scripts/lumos 時還是會擋
severity: minor
blocking: 否 — 既有測試 t_precommit_vendored_exempt 會抓到照字面寫出的退步
引句:「圖譜不存在、staged 為空、沒有 scripts/lumos 時應照舊放行」
file: `scripts/hooks/pre-commit:50`
file: `scripts/test_lumos.py:3713`
1. 現在的 pre-commit 沒有「沒有 scripts/lumos 就提早放行」這個出口。沒有 scripts/lumos 時,只是跳過需要 python 的那幾道(CC/DG/L/H/NS);不需要 python 的 Gate 1(日期欄位被加引號)和 Gate 2/3(改了程式卻沒動筆記)照樣會擋。
2. 第 3 點說「沒有 scripts/lumos 這三種提早放行」,[S3] 說「照舊放行」。照字面加一行 `[ -f scripts/lumos ] || exit 0`,會讓沒有 vendored lumos 的 repo 失去兩道硬擋。既有的 `t_precommit_vendored_exempt` 第②③格(fixture 裡沒有 scripts/lumos,斷言會擋)會翻紅,所以列 minor。正確寫法是「沒有 scripts/lumos 時不 source 共用檔、只跳過要 python 的那幾道」。

## F10 候選⑥uv 的「驗法一樣」說不通,「--system 只找系統裝好的」也跟 uv 的實際行為不符
severity: minor
blocking: 否 — 實作者多半會自己補出兩步驟,但三份清單各自補,同步測試就比不出來
引句:「`uv python find --system --no-python-downloads '>=3.14'`(只找系統裝好的、★不准觸發下載★)」
1. 其他候選都是「拿它跑一段版本檢查」;uv 這一項是一條會印出路徑的指令,沒辦法「拿 uv 跑那一段」。要先拿到 uv 印出的路徑,再用那個路徑跑檢查、改用它印出的 sys.executable。spec 沒寫第二步,三份實作可以各做各的。
2. `--system` 的說明是「Only find system Python interpreters」,意思是跳過虛擬環境,uv 自己管理的安裝一樣會找。實測把 PATH 縮短後,錯誤訊息是「No interpreter found for Python >=3.14 in managed installations or search path」,代表它有去 managed installations 找。括號裡的「只找系統裝好的」要改寫,免得有人為了符合字面去加 `--python-preference only-system`,把 `uv python install 3.14` 裝的那一支排除掉。

## F11 CI 的「編譯全部檔」那一步其實從來沒編譯過 scripts/lumos
severity: minor
blocking: 否 — SyntaxWarning 歸零那一步有用 compile() 真的編譯 scripts/lumos,保護還在,只是 spec 的敘述不準
引句:「兩道會在 3.14 上重跑,新警告一起清」
file: `.github/workflows/ci.yml:21`
1. CI 跑的是 `python -m compileall -q scripts/lumos scripts/test_lumos.py`。compileall 會默默略過沒有 .py 副檔名的檔。實測:一支語法壞掉、沒有副檔名的檔,compileall 回 0;同樣內容存成 .py,回 1。
2. 所以兩道之中真的在 3.14 上編譯 scripts/lumos 的只有 SyntaxWarning 那一步。第 7 點把兩道都當成守衛;將來如果有人為了清警告拿掉 SyntaxWarning 那一步,scripts/lumos 在 CI 上就沒有任何編譯檢查了。

## F12 「舊註冊每次多一次重跑約 65 毫秒」沒算到 3.9 先解析整支檔的時間
severity: minor
blocking: 否 — 只是數字不準,不影響設計決定
引句:「舊註冊(設定還寫著 3.9)在重跑安裝前每次呼叫 lumos 多一次重跑,約 65 毫秒」
1. 3.9 要先把 3.5 萬行解析完才跑得到開頭的檢查(第 2 點自己也這樣說)。實測 `/usr/bin/python3` compile scripts/lumos 連三次都是 0.22 秒,空腳本啟動 0.02 秒。每次重跑實際多出來的是 0.22 秒以上,再加上找候選與 3.14 本身的啟動時間。Claude 掛鉤每個工具呼叫都會叫 lumos,舊註冊期間每次多約 0.25 秒以上。

## F13 共用檔會被 source 進不同 shell 選項的腳本,spec 沒要求它在 set -e 下也不會中途結束
severity: minor
blocking: 否 — 大多數寫法會用 if 包起來,但 get.sh 那條路一寫錯,就正好退回第 5 點想消滅的「沒說明的 127」
引句:「被 source 時找一次、結果放進變數,呼叫端不重找」
file: `get.sh:45`
1. get.sh 是 `set -euo pipefail`,兩支掛鉤是 `set -u`。被 source 的程式會繼承呼叫端的選項。沒設時 `git config lumos.python` 回 1,找不到 `python3.14` 回 127;只要有一個探測沒用 if 或 `||` 包起來,get.sh 就會在那一行直接結束,印出沒有說明的 127。
2. 另外,共用檔要是自己 `exit`,掛鉤要 rc 1、安裝器要 rc 2 就沒辦法各自決定。spec 要寫明共用檔只設變數、一律用 return、在 `set -euo pipefail` 下也安全,並在 [S1] 或 [S4] 的測試加一格「在 set -e 的腳本裡 source」。

## F14 LUMOS_PYTHON 可以是相對路徑,掛鉤和直接打 lumos 會解析到不同的檔
severity: minor
blocking: 否 — 只有寫相對路徑的人會碰到,結果是報錯停下,不會默默挑錯
引句:「值是一支執行檔的路徑,不能帶參數、不展開 `~`,空字串等於沒設」
file: `scripts/hooks/pre-commit:26`
1. 掛鉤會先 `cd "$REPO_ROOT"` 才解析,lumos 則是用使用者當下所在的目錄解析。`LUMOS_PYTHON=.venv/bin/python` 在掛鉤裡可以用;在子目錄直接打 lumos 時會找不到,又因為「有設就只認它」,就停下報錯。要嘛規定必須是絕對路徑(不是就報錯並講明),要嘛規定一律以 repo 根目錄為基準解析。

## 逐節交代

- 開頭欄位、白話、依據、PRIOR-ART、RETIRE-IF:已讀,無 finding。
- 範圍:已讀,無 finding(排程腳本那一段,F1 的 shim 迴圈一樣會碰到,不另外列)。
- 做法第 1 點:F1、F2、F10、F13、F14。第 2 點:F1、F12。第 3 點:F9。第 4 點:已讀,無 finding(`_hook_script` 用 `[\w.-]+\.py` 抓腳本名,拿 Homebrew、pyenv、uv、conda、Windows 的直譯器路徑逐一代入,都不會先匹配到直譯器路徑,遷移與去重照舊成立)。第 5 點:F3、F5。第 6 點:F6、F8。第 7 點:F7、F11。第 8 點、第 10 到 13 點:已讀,無 finding(第 10 點引的 `t_hooks_python_fallback` 只盯兩支、36619 行附近只複製 pre-push,都核對屬實)。第 9 點:已讀,無 finding。第 12 點:F4 提到 bootstrap,不影響這一點的歸屬。
- 條款:[S1] F1、F2、F4、F10;[S2] F1、F2;[S3] F2、F9;[S4] F2、F3、F5;[S5] F8;[S6] F7;[S7] 已讀,無 finding(實測 ruff 0.16.7 `--target-version py39 --select E9` 對沒有副檔名的檔也有效,match、except*、type、PEP 695、PEP 701 都報得出來;括號包起來的多個 with 3.9 本身就能解析,ruff 不報是對的);[S8] F6、F8;[S9] 已讀,無 finding;[S10] 已讀,無 finding。內部交叉引用(第 N 點、[SN])都核對過,目標都存在。
- 回退:已讀,無 finding。
- 實務隱患:守衛面的誤擋見 F1(卡死而不是擋下)、F2;對外送出見 F7;不可逆:無新的,消費專案的殘檔 spec 已經寫了;併發:無,每次 hook 各自找一次、不共用狀態,防重跑變數通過後清掉的邏輯本身沒問題;效能見 F12。
- 誠實界線:已讀,無 finding。

## 固定席節點

- [[Systems/bound-tests-gate]] ★INVARIANT★「證不出跑過 → blocked」:會被 F6 破壞(字面 `{python}` 或沒加引號的路徑,在過濾探針與綁定測試裡得到 127,被判成擋下)。
- [[Systems/lumos-cli-lifecycle]] ★INVARIANT★「re-inject 只覆蓋 sentinel 之間」:不影響。這份設計只改 CLAUDE.md 裡「本 repo 的測試子集怎麼跑」那一節的指令寫法,那一節在注入區塊外面,是人手改的,不經 re-inject。
- [[Systems/codex-harness]] RULE「探針前先驗目標在不在」:不影響。這份設計只改 Codex 掛鉤註冊命令的直譯器與引號,不碰探針題目與目標比對。

最嚴重的等級是 major;會卡住實作的共 7 條(F1–F7),另有 minor 7 條。
