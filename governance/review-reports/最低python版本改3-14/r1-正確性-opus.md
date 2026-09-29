severity: major

# r1 正確性與邏輯席(opus)——最低Python版本改3.14_計劃

審材:凍結版 `最低python版本改3-14-r1.md`(81 行)。對照 repo:clone-314。
本機實驗用 /opt/homebrew/bin/python3.14(3.14.6)、/usr/bin/python3(3.9.6)、ruff 0.16.7、uv 0.11.19,全部在 mktemp 目錄做,沒動任何 repo 檔、沒執行任何掛鉤。

逐節結論:
- 開頭白話/依據/PRIOR-ART/RETIRE-IF:已讀,無 finding。
- 範圍:F4(漏了一個挑直譯器的入口)。
- 做法 1:F7、F9、F11。做法 2:F1、F3、F8。做法 3:F5、F10。做法 4:F11。做法 5:F6。做法 6:F2。做法 7、8、9、10:已讀,無 finding。
- 條款 [S1]–[S7]:[S2] 見 F8、F12;[S3] 見 F10;[S7] 見 F1、F2;[S1][S4][S5][S6] 已讀,另見 F6/F11。
- 回退:已讀,無 finding(「只回退擋下」寫明不退回 3.9,和第 3 點一致)。
- 實務隱患:F7(守衛面的誤擋情境沒列)、F13(和做法 7 互相矛盾)。
- 誠實界線:F1、F2(自稱守住的範圍比實際大)。
- 交叉引用:第 2 點、第 3 點、[S7] 都有對應的段落或條款,沒有斷掉的引用。

## F1 版本檢查放在檔尾,舊版得先把 3.5 萬行的模組頂層全部跑完;[S7] 只驗語法,載入時就炸的寫法攔不到

severity: major
blocking: 是 — 照字面把檢查放在檔尾的 `__main__` 段,之後任何人寫一個 `X | None` 型別註記,3.9 在跑到檢查之前就丟出追蹤,「找不到就講清楚」這件事整個失效,而 [S7] 照樣綠
引句:「這段與它之前的所有程式碼必須能被舊版解析(見 [S7])」
file: `scripts/lumos:35508`
1. 現況 `if __name__ == "__main__":` 在 scripts/lumos 第 35508 行,也就是檔案最後。做法 2 要把檢查放在「那段、進 `main()` 之前」。這表示 3.9 要先把前面 3.5 萬行模組頂層的每一句都**執行**完(每個 def 的註記求值、裝飾器、模組層常數、`re.compile`),不只是解析完。
2. 能重現的輸入:scripts/lumos 沒有 `from __future__ import annotations`(grep 過,只有 merge-claude-settings.py 有)。在任何函式上寫 `def f(x: int | None)`:3.14 下註記是延後求值,沒事;`/usr/bin/python3 -c "def f(x: int | None): pass"` 則是 `TypeError: unsupported operand type(s) for |`。這發生在模組載入階段,早於檔尾的檢查,結果就是一大段追蹤,不是要求的說明。
3. `ast.parse(feature_version=(3,9))` 接受這種寫法(本機實測 union_ann → ACCEPTED),所以 [S7] 照樣綠。誠實界線只承認「新版標準庫函式在載入時被呼叫」,沒有列出「註記在定義當下就求值」這種最可能發生的漂移——最低版本改成 3.14 之後,寫 `X | None` 正是一般寫法。
4. 改法:把檢查搬到檔案最上面,緊接在那幾行標準庫 import 之後,寫成 `if __name__ == "__main__" and sys.version_info < (3, 14): …`。被 import 時一樣不觸發,但 3.9 需要執行的程式只剩那幾行;〈誠實界線〉也要改寫成「只有檢查之前那幾行需要能在舊版跑」。

## F2 [S7] 的做法其實守不住語法:在 3.14 上用 feature_version=(3,9) 解析,會放過 3.12 的 f-string 寫法;做法 6 還把唯一抓得到它的 ruff 關掉了

severity: major
blocking: 是 — 照 [S7] 字面實作,3.9 解析不了的 f-string 會通過測試上線,舊版啟動時在檢查之前就丟出語法錯誤;這正是 [S7] 宣稱要擋的情況
引句:「[S7] 用舊語法版本解析守著」
file: `.lumos/lint.json:3`
1. 本機實測,在 3.14.6 上跑 `ast.parse(src, feature_version=(3,9))`:下列寫法全部 **ACCEPTED**,但 3.9 會丟 SyntaxError——`f"{d["a"]}"`(f-string 裡重用外層引號,PEP 701)、`f"{'\n'.join(x)}"`(f-string 運算式裡放反斜線)、f-string 內寫註解、`a[*b]`、`a[x:=1]`。已實測 3.9:前兩個的訊息分別是「f-string: unmatched '['」和「f-string expression part cannot include a backslash」。feature_version 只擋得到 match、except*、type、泛型、t-string 這類有明確版本閘的語法。
2. f-string 重用外層引號是 3.12 之後最常順手寫出來的寫法,也就是 [S7] 最需要擋的那一種。
3. 做法 6 把 `.lumos/lint.json` 的 `--target-version` 從 py39 改成 py314。本機實測 ruff 0.16.7 用 `--target-version py39 --select E9` 會報「Cannot reuse outer quote character in f-strings on Python 3.9」,改成 py314 之後報「All checks passed」。目前唯一能抓到這一類的工具被這一步關掉了。同一個改動也讓 scripts/lumos 和 test_lumos.py 多出 10 條 B905 加 1 條 RUF007(py39 → py314 的差集,實測)。
4. 改法(擇一或併用):①[S7] 的測試在找得到 <3.12 的直譯器時(macOS 的 /usr/bin/python3)真的用它 `compile`,找不到就要明說沒驗到,不准默默綠;②lint.json 對 scripts/lumos 維持 py39(ruff 可以按檔設定目標版本),其餘檔才改 py314;③直接照 REVISIT 那條,現在就把 scripts/lumos 拆成「只做檢查的小入口 + 本體」,入口只要幾十行,就能用真的舊版驗到底。

## F3 防重跑的環境變數會被所有子孫行程繼承,之後合法由舊版啟動的 lumos 會被誤判成「重跑後仍是舊版」而報錯

severity: major
blocking: 是 — 照字面實作(看到變數有設、版本又舊就報錯),同一棵行程樹裡任何由舊版 python 叫起來的 lumos,都會錯誤結束,不會改用 3.14 重跑
引句:「重跑前設一個環境變數,重跑後的程序若還是舊版就直接報錯,不會無限重跑」
file: `scripts/lumos:32116`
1. 重跑用的是 execv 或子行程,`os.environ` 會整份帶過去;spec 沒說 3.14 那個行程通過檢查之後要把這個變數清掉。
2. 重現的鏈:使用者打 `python3 scripts/lumos bound-tests …`(3.9)→ 設變數 → 改用 3.14 重跑 → lumos 用 shell 跑 `.lumos/config.json` 的 `run_cmd` = `python3 scripts/test_lumos.py -k …`(scripts/lumos:32116 經 `_kill_run`,shell=True)→ 這裡的 python3 還是 3.9 → 測試裡用 `sys.executable` 叫 lumos → 這個 lumos 是 3.9 而且繼承了變數 → 照 spec 直接報錯,不重跑。凡是 lumos 叫外部工具、外部工具又用 PATH 上的 python3 叫回 lumos 的路徑,都一樣。
3. 改法:變數值寫成「重跑目標的絕對路徑」,只有 `sys.executable` 等於那個值、版本卻還是舊的,才算重跑失敗;另外,通過檢查之後立刻 `os.environ.pop` 掉。[S2] 要多一條情境:變數被繼承、由舊版啟動的孫行程,仍然要能正常重跑。

## F4 範圍漏了一個挑直譯器的入口:合約測試閘的 run_cmd 寫死 `python3 scripts/test_lumos.py`,測試總檔本身也沒有版本檢查

severity: major
blocking: 是 — python3 是舊版、3.14 只以 python3.14 存在的機器上(照 spec 自己推薦的 `uv python install 3.14` 裝完就是這樣),推送前的合約測試閘會把每一支綁定測試都跑紅,高風險推送被擋
引句:「在範圍內:`scripts/lumos` 與 `scripts/hooks/**`」
file: `.lumos/config.json:5`
1. `.lumos/config.json` 的 `test.run_cmd` 是 `python3 scripts/test_lumos.py -k {method}`;合約測試閘(scripts/lumos:32116)和 guard kill(12599)都用 shell 執行它,解析的是 PATH 上的 `python3`,不經過做法 1 的清單。
2. test_lumos.py 不在做法 2 的重跑範圍內(只改 scripts/lumos)。而且做法 8 把 `_toml_loads` 的代解分支拿掉,改回直接 `import tomllib` 之後,3.9 載入測試總檔會直接 `ModuleNotFoundError` 丟出追蹤,連說明都沒有。
3. 情境:macOS 使用者照擋下訊息跑 `uv python install 3.14`。uv 預設只在 ~/.local/bin 放一支帶版本號的 `python3.14`,要 `--default` 才會多放 `python3`,所以 `python3` 仍然指向 /usr/bin/python3(3.9)。git 掛鉤找到 python3.14、lumos 用 3.14 在跑,但合約測試閘叫的 `python3 scripts/test_lumos.py` 是 3.9,全紅。[[Systems/bound-tests-gate]] 的 ★INVARIANT★ 規定任何一支紅就 blocked=True rc1,高風險推送因此被擋。
4. 同一類還有:pre-push 擋下時提示的 `python3 scripts/test_lumos.py --ff -x`(scripts/hooks/pre-push:527)、CLAUDE.md 的子集指令,在同一台機器上都會紅。
5. 改法:在範圍裡加上 test_lumos.py(同樣在檔頭做檢查並重跑,或至少印說明回 2),並且把 run_cmd 改成不依賴 PATH 上的 python3(例如用 `{python}` 佔位符,由 lumos 代入 `sys.executable`)。

## F5 post-commit 是記錄「跳過檢查」的那一支;改成非 3.14 不可之後,最需要留紀錄的那次提交反而不會留紀錄

severity: major
blocking: 是 — post-commit 的合約是「--no-verify 的提交一律留痕」;照字面實作,沒有 3.14 的機器(也就是只能靠 --no-verify 提交的機器)跳過紀錄一筆都寫不進去,每週的跳過率會少算
引句:「改成 source 共用檔、找不到就印一行提醒後正常結束」
file: `scripts/hooks/post-commit:95`
1. post-commit 的開頭註解寫明它是「bypass 留痕」:`--no-verify` 只會跳過 pre-commit,post-commit 照樣會跑,所以它是唯一的偵測點。它用 python 做的事只是一段 heredoc,往 `docs/.bypass-log.jsonl` 追加一行 JSON(json/os/sys/datetime),3.x 任何版本都跑得動。
2. 新設計下:沒有 3.14 → pre-commit 擋下 → 使用者照說明改用 `--no-verify` → post-commit 找不到 3.14 → 只印提醒,不記帳。〈誠實界線〉說「沒有 3.14 就沒有能寫治理帳的直譯器」,但對這一支不成立,是這份設計自己把紀錄丟掉的。
3. 現況描述也不對:post-commit 有 `trap 'exit 0' ERR`,找不到 python 時 `PY="$(command -v python3 || command -v python)"` 這一行就會觸發 ERR 並安靜地 exit 0,根本不會「執行空字串指令出錯」(用同樣三行在 mktemp 目錄實測:指派之後的那行沒有執行,rc 0)。連帶的影響是:如果共用檔裡找直譯器的函式找不到時回非零,post-commit 會被這個 trap 安靜結束,spec 要的「印一行提醒」根本印不出來。
4. 改法:post-commit 寫紀錄那一段不設版本下限(沿用任何 python,或改成純 shell 的 printf),只有要叫 lumos 的地方才用共用清單;〈誠實界線〉的「`--no-verify` 不留帳」要照實改寫。

## F6 安裝入口的「任何 python」只試 python3 和 python;只裝了帶版本號 3.14、或在 Windows 只有 py 啟動器的機器,永遠走不到 lumos 開頭那份清單,還會被叫去重裝

severity: major
blocking: 是 — 照字面實作,使用者照 spec 給的指令裝好 3.14 之後,安裝器仍然說找不到 python、要他再裝一次,形成死循環
引句:「它們只改一件事:連任何 python 都找不到時,印同一套安裝指令」
file: `get.ps1:36`
1. get.sh:45、install.sh:5、scripts/install-hooks.sh:6、scripts/install-graph-toolchain.sh:17/19 都寫死 `python3`;get.ps1:36 試的是 `python3`、`python`。做法 5 讓它們維持原樣,只在「連任何 python 都找不到」時報錯。
2. Linux 或容器(沒有系統 python3):使用者照擋下訊息跑 `uv python install 3.14`,uv 預設只放 `~/.local/bin/python3.14`,沒有 python3。get.sh 找不到 python3 → 印「請安裝 3.14」→ 使用者其實已經裝了。lumos 開頭那份清單第一個就會試 python3.14,可是 lumos 從來沒被叫起來。
3. Windows:python.org 安裝器預設不勾「加入 PATH」,只裝 py 啟動器;Windows 10/11 預設在 WindowsApps 放了 `python.exe`/`python3.exe` 兩個商店替身。get.ps1 的 `Get-Command python3` 會找到替身 → 執行後印「Python was not found」並回 9009,不是 spec 說的那段安裝說明。`lumos.cmd` 包裝寫的也是 python3/python 這兩個名字,所以做法 1 為 Windows 加的 `py -3.14` 候選只在「已經有另一支真的 python.exe 把 lumos 叫起來」時才用得到,只有 py 的機器根本碰不到它。
4. 改法:安裝入口的「任何 python」探測至少要加上 `python3.14`(依序也要有 3.15、3.16)和 Windows 的 `py`,並且真的執行一次(`-c pass`)才算找到,不能只用 `command -v`/`Get-Command`;[S4] 的測試要多兩個情境:「只有 python3.14」和「只有商店替身」。

## F7 找得到 3.14 卻判成找不到:GUI git 用戶端的精簡 PATH、pyenv 的專案版本鎖定;spec 給的解法 LUMOS_PYTHON 在這兩種情境都用不了

severity: major
blocking: 是 — 守衛面明說錯的方向是「誤擋」,但這兩種常見設定都會穩定誤擋,擋下訊息叫人去裝已經裝好的東西 ⚠(GUI 用戶端會不會帶 shell 的 PATH,依用戶端而定)
引句:「依序試 `$LUMOS_PYTHON`、`python3.14`、`python3.15`、`python3.16`、`python3`、`python`」
file: `scripts/hooks/pre-commit:50`
1. 在 macOS 上,從 Dock 啟動的 GUI 程式,PATH 是 launchd 預設的 `/usr/bin:/bin:/usr/sbin:/sbin`,也不會讀 shell 裡 export 的 LUMOS_PYTHON。在這類 git 用戶端裡提交:python3.14 不在 PATH → python3 = /usr/bin/python3(3.9)→ uv 在 ~/.local/bin 或 /opt/homebrew/bin,也不在 PATH → 擋下。現況在同一個情境下是用 3.9 跑完檢查然後放行。
2. pyenv:消費專案目錄裡有 `.python-version`(例如 3.11)時,pyenv 的 `python3.14` shim 會回「command not found … exists in these Python versions: 3.14.x」,rc 127;`python3` shim 則給 3.11。機器上明明有 3.14,仍然擋下。
3. 擋下訊息會列出每個候選和它的版本,但這只能讓人看出哪裡錯,解不了:GUI 情境下 LUMOS_PYTHON 傳不進去,唯一的出口是 `--no-verify`。
4. 改法:安裝時(`lumos init/update/install`,這時 lumos 已經在 ≥3.14 上跑)把 `sys.executable` 寫進 repo 的 git 設定(例如 `git config lumos.python`)。掛鉤的清單在 `$LUMOS_PYTHON` 之後先試它:git 設定不依賴行程的環境變數,GUI 和 pyenv 兩種情境都讀得到。兩份清單要一起改,並寫進 [S1]。

## F8 候選是指令名稱,但 os.execv 不會去 PATH 找;Windows 的 `py -3.14` 是兩個詞,也不是一個路徑

severity: major
blocking: 是 — 照字面拿清單挑到的候選去 `os.execv`,最常見的那一條(python3.14 在 PATH 上)會丟 FileNotFoundError 並印出追蹤,違反 [S2]「不印追蹤」;用絕對路徑 LUMOS_PYTHON 寫的測試抓不到
引句:「POSIX 用 `os.execv`;Windows 的 execv 不會真的取代行程」
1. 做法 1 的候選是 `python3.14`、`python3` 這類裸名字;`os.execv(path, args)` 不會搜尋 PATH,拿裸名字會被當成相對於目前目錄的路徑,結果是 FileNotFoundError。
2. `py -3.14` 必須當成 argv 前綴,不能當成單一路徑傳給 execv 或 subprocess。
3. [S2] 在 CI 上最容易的寫法,是讓 LUMOS_PYTHON 指向 `sys.executable`(絕對路徑),剛好繞過這個錯;按名字找到的那條路徑沒有任何條款會跑到。
4. 改法:規定每個候選在驗版本時同時印出 `sys.executable`,之後重跑、擋下訊息、寫進設定,一律用這個絕對路徑(POSIX 用 execv,Windows 用子行程);[S2] 加一個情境:候選只以名字出現在 PATH 上(暫存目錄裡放一支 `python3.14` 捷徑,並且把 LUMOS_PYTHON 清掉)。

## F9 新共用檔放進 scripts/hooks 卻沒登記到錨點清單:本 repo 的測試會紅、推送會被 anchor verify 擋,而決定檢查要不要跑的那支檔也沒人看守

severity: major
blocking: 是 — spec 點名只要登記工具自裝檔那一份清單,少了錨點清單和基準線,「會自動跑的掛鉤都要進錨點」這條合約就漏了;照字面做,推送前那道永遠不可跳過的閘會擋下
引句:「新共用檔要登記進工具自裝檔的精確名單」
file: `scripts/lumos:18573`
1. `ANCHOR_FILES`(scripts/lumos:18573)把 scripts/hooks 底下的檔逐一列出來;測試 test_lumos.py:15935 附近斷言 `git ls-files scripts/hooks` 要和清單相等;`cmd_anchor_verify` 用檔案系統掃 scripts/hooks,只要有沒登記在基準線裡的檔就回 rc1(「scripts/hooks 底下多了 N 支沒登記的檔」),而 pre-push 第一道就是它。
2. 照 spec 只改自裝檔清單:測試紅,pre-push 被擋;消費專案如果有 anchor 基準線,`lumos update` 把新檔帶進去之後也會被擋,直到有人跑 `anchor approve`。
3. 更重要的是:這支共用檔決定 git 掛鉤要不要擋、用哪一支直譯器跑全部的檢查,屬於「一打開資料夾就自動跑」的裁判檔,應該受錨點看守。
4. 改法:做法 1 的登記清單加上 `ANCHOR_FILES`、`governance/anchor-baseline.json`(跑 `anchor approve`),以及上面那支錨點名單測試。

## F10 git 掛鉤「找不到就擋」要插在哪一道之前沒寫,和現有的提早放行條件怎麼接也沒寫

severity: minor
blocking: 否 — 放錯位置會多擋一些本來不需要 python 的提交(沒有圖譜的 repo、空提交、沒 vendor lumos 的 repo),但不會放過該擋的東西
引句:「找不到 3.14 時擋下(rc 1)並印同一段說明」
file: `scripts/hooks/pre-commit:38`
1. pre-commit 在找 python 之前有三道提早放行:沒有圖譜(38 行)、staged 是空的(44 行),以及每道要 python 的檢查都有的 `-f "$REPO_ROOT/scripts/lumos"` 條件(沒 vendor 就跳過)。pre-push 在 118 行則是 `-z "$PY" || ! -f "$GRAPHCTL"` 合在一起判斷。spec 沒說新的擋下要放在這些判斷之前還是之後。最自然的寫法是在檔頭 source 共用檔、找不到就擋,那樣沒有圖譜的 repo、或根本沒有 scripts/lumos 的 repo,也會因為缺 3.14 被擋。
2. 共用檔的定位:掛鉤如果用 `$(dirname "$0")` 找共用檔,消費專案用 husky 之類另設 hooksPath、再從它的掛鉤裡 source 或 `.` 我們的 pre-commit 時,`$0` 會是對方的掛鉤,找不到共用檔。bash 在非 posix 模式下 `source` 不存在的檔只會回 1、腳本繼續往下跑,於是變成印出「沒有 3.14」這個誤導的說明。
3. 改法:寫明擋下的位置在「確定這次會叫 lumos」之後(pre-commit 在 Gate 0 和空 staged 之後,並且要有 scripts/lumos);共用檔用 `${BASH_SOURCE[0]}` 定位,source 失敗時印「共用檔不見了」,和「沒有 3.14」分開。

## F11 uv 候選沒加 `--system`,會挑到當下專案的 .venv;改用 sys.executable 之後,設定檔裡的直譯器路徑綁死在某個小版本、某個專案

severity: minor
blocking: 否 — 行為仍然是 ≥3.14,但全域 Claude/Codex 設定可能指到一個之後會被刪掉的專案 venv,所有掛鉤會安靜地失效;〈誠實界線〉只承認了 uv 自己管理的直譯器會搬家這一種
引句:「有 uv 時再試 `uv python find '>=3.14'`」
file: `scripts/merge-claude-settings.py:118`
1. 本機實測(mktemp 目錄):在一個有 3.14 `.venv` 的目錄和它的子目錄裡,`uv python find '>=3.14'` 回的是 `<該目錄>/.venv/bin/python3`,不需要先啟用 venv;加 `--system` 才會回 /opt/homebrew/opt/python@3.14/bin/python3.14。如果在這種目錄裡跑 `lumos install`,merge-claude-settings 會把那個專案的 venv 路徑寫進全域設定,之後 `rm -rf .venv`,每個專案的掛鉤都壞掉。
2. Homebrew 的情況:sys.executable 是 `/opt/homebrew/opt/python@3.14/bin/python3.14`,綁在 3.14 這個配方上;原本 `which python3` 拿到的 `/opt/homebrew/bin/python3` 會跟著預設版本走。python@3.14 之後被 `brew autoremove` 移掉時,掛鉤會安靜地失效。
3. POSIX 的命令格式是 `f'{_PY} "${{HOME}}/…"'`(118 行),直譯器路徑沒加引號;sys.executable 比原本更常落在家目錄底下(uv、pyenv versions),家目錄名稱有空白時整條命令就壞了。
4. 改法:uv 候選改成 `uv python find --system '>=3.14'`;寫設定時,如果 `which python3` 或 `which python3.14` 本身就 ≥3.14,優先用這個比較穩定的名字對應的路徑;POSIX 分支的直譯器路徑也加引號。

## F12 [S2] 的測試要從哪裡拿到一支「真的舊版」、怎麼證明舊版那條路真的有跑到,都沒寫

severity: minor
blocking: 否 — CI 的 ubuntu 有 3.12 的 /usr/bin/python3 可以用,但如果用假版本號之類的方式模擬,F1、F2 那種只有真舊版才會爆的錯會全綠
引句:「被 import 載入時不應觸發 [test:t_lumos_old_python_reexec_or_explain]」
1. CI 經 setup-python 拿到的是 3.14;要測「被舊版啟動」,只能靠系統自帶的 python3(ubuntu 24.04 是 3.12,macOS 是 3.9),或者用環境變數假裝版本。後者跑到的不是真的舊版解析和載入路徑。
2. [[Systems/測試假綠形態]] 的 ★INVARIANT★ 要求要有前置斷言證明現場成立;這裡的前置斷言應該是「啟動用的直譯器確實 <3.14」,找不到舊版時要明說沒驗到,不准默默跳過而顯示綠。
3. 另外,rc 2 和 argparse 錯誤、以及很多子命令的「擋下」共用同一個值,測試不能只靠 rc 2 判定「找不到 3.14」,要比對輸出。

## F13 實務隱患節說 CHANGELOG 寫升級說明,做法 7 說不寫 CHANGELOG

severity: minor
blocking: 否 — 文件前後矛盾,實作者照哪一邊都不會做出壞系統,只是升級說明放哪裡不清楚
引句:「防法:CHANGELOG 寫升級說明,擋下訊息附三種平台的安裝指令」
1. 第 72 行的「對外送出」防法寫的是 CHANGELOG;第 47 行(做法 7)明寫「不寫 CHANGELOG——它自己規定只記發版」,升級注意寫在 README。前置掃描改了做法 7,這一節沒有跟著改。
2. 改法:第 72 行改成「README 寫升級注意(發版時帶進 CHANGELOG)」。

## 固定席節點(lands_in 五篇)逐條判

- [[Systems/lumos-cli-lifecycle]] ★INVARIANT★「re-inject 只覆蓋 sentinel 之間」:不影響。版本檢查和重跑都發生在 `main()` 之前,不碰 CLAUDE.md 的寫入路徑;重跑時參數原樣傳下去,init/update 的行為不變。
- [[Systems/bound-tests-gate]] ★INVARIANT★「綁的測試逐支真跑,任一紅 → blocked rc1」:會受影響,見 F4。run_cmd 寫死 `python3`,在「python3 是舊版、3.14 另外存在」的機器上,每支綁定測試都會紅,閘照合約擋下,但原因是環境不是程式。
- [[Systems/每支檔有家]](沒有合約):不影響。新共用檔在做法 10 開了自己的家;pre-commit 的 Gate H 在同一個提交裡看得到這個家。
- [[Systems/codex-harness]](沒有合約):大致不影響。Codex 的目標和 Claude 共用 `_PY`,換成 sys.executable 之後兩邊一起變;F11 講的 venv 和路徑穩定性問題兩邊都有。
- [[Systems/測試假綠形態]] ★INVARIANT★「還原翻紅釘要有前置斷言證明現場成立」:[S2]、[S3] 的測試有踩到這條的風險,見 F12。[S3] 在開發機上還要把 LUMOS_PYTHON、uv、~/.local/bin 從環境裡拿掉,否則「只找得到 3.9」這個現場根本造不出來。

## 實務隱患逐類

- 守衛面:碰到,而且比 spec 列的更寬。見 F7(找得到卻判找不到)、F10(不需要 python 的提交也被擋)、F9(錨點閘會擋推送)。
- 對外送出:碰到。見 F6(安裝入口在 3.14 只以帶版本號的名字存在時,會叫人重裝)、F13。
- 不可逆:碰到,而且範圍比 spec 承認的大。見 F11:全域設定會指到專案的 venv,刪掉 venv 之後掛鉤安靜地失效。
- 併發:F3 的環境變數繼承算是跨行程的狀態外洩;此外沒有新的併發面,掛鉤各自解析、互不共享狀態。
- 效能:無實質問題。重跑多花的是試候選時起幾支直譯器(每支約數十毫秒,最多約 7 支),掛鉤的時間預算(10–60 秒)吃得下。

總結:最嚴重為 major;會擋實作的共 9 條(F1–F9),另有 4 條 minor(F10–F13)。
