severity: major

鏡頭:邊界與可執行性。實測環境:本機 /usr/bin/python3=3.9.6、/opt/homebrew/bin/python3.14 存在;用 `env -i PATH=/usr/bin:/bin` 造短 PATH、用 sh 造含空白的直譯器路徑。

## F1 短 PATH 環境(git GUI 客戶端、Xcode、非登入 shell)候選清單全落空,誤擋提交
severity: major
blocking: 是 — 照字面實作,裝了 3.14 的機器在 GUI 客戶端提交會被誤擋,唯一出口是不留帳的 --no-verify,實作者會做出壞系統。
引句:「依序試 `$LUMOS_PYTHON`、`python3.14`、`python3.15`、`python3.16`、`python3`、`python`」
file: `scripts/hooks/pre-commit:50`
1. 候選全是「靠 PATH 解析的指令名」,沒有任何已知安裝位置(/opt/homebrew/bin、/usr/local/bin、~/.local/bin、pyenv shims、uv 管理目錄)。
2. 實測:`env -i PATH=/usr/bin:/bin` 下 `python3.14` 找不到,`python3` 是 /usr/bin/python3=3.9,其餘不存在。此時 /opt/homebrew/bin/python3.14 明明存在,照 spec 會判「找不到 3.14」並 rc 1 擋下。
3. 現況(pre-commit:50、pre-push:70)在同環境會拿 3.9 跑而通過,所以這是新增的誤擋面,不是既有行為。Tower、Fork、GitHub Desktop、從 Dock 啟動的 IDE 的 PATH 常是這種短 PATH。
4. spec 給的出口只有 `LUMOS_PYTHON`(GUI 客戶端環境幾乎設不到)或 `--no-verify`(不留帳)。〈實務隱患〉守衛面只想到「找得到 3.14 卻判找不到」是清單順序錯,沒想到「清單根本看不到」。
5. 缺:候選要含固定絕對路徑探測,或讓使用者把解析結果存進設定檔(如 git config / repo 內檔案)供掛鉤讀。

## F2 shell 掛鉤沒有 Windows 的 py 啟動器候選,只裝了 py 啟動器的 Windows 機器被誤擋且訊息錯誤
severity: major
blocking: 是 — Windows 上 lumos 能靠 `py -3.14` 跑,git 掛鉤卻判找不到並教人「安裝 Python」,誤擋且訊息誤導。
引句:「Windows 多一個候選 `py -3.14`」
1. 該候選只寫在第 1 點①(scripts/lumos 那份),shell 共用檔(②)沒有;git for Windows 的掛鉤跑在 Git Bash,只看得到 PATH 上的 python3/python。
2. python.org 官方安裝器預設不勾「加入 PATH」,只留 `py` 啟動器;此時 PATH 上沒有 python3.14/python3/python(或只有 Microsoft Store 的別名殘樁),shell 清單全落空 → 擋下並印「需要 3.14」的安裝指令,但 3.14 其實已裝。
3. [S1] 又規定「shell 與 Python 兩份清單的順序應一致」,與「Windows 多一個候選」互相打架:同步測試 t_python_resolver_order_and_floor 要不要豁免這一格,spec 沒說,實作者只能自己猜。
4. Windows 的殘樁(`python3.exe` 應用程式別名)還會被當候選執行,spec 沒規定殘樁的非零/無輸出算「不合格候選」還是「掛鉤失敗」。⚠ 未在 Windows 實測。

## F3 安裝入口目前只找 python3,「任何 python」的前提對不上,只有 3.14 的機器會被說成沒有 python
severity: major
blocking: 是 — [S4] 的觸發條件「找不到任何 python」在字面實作下會對已裝 3.14 的機器誤觸發,教人安裝已裝好的東西。
引句:「它們只改一件事:連任何 python 都找不到時,印同一套安裝指令」
file: `install.sh:5`
1. spec 說安裝入口「照舊」找 python,但現況 install.sh:5、install-hooks.sh:6、install-graph-toolchain.sh:17,19、get.sh:45 全是寫死的 `exec python3`(不試 `python`、不試 `python3.14`);get.ps1 試 `python3`、`python` 兩個名字,不試 `py`。
2. 情境:只用 `uv python install 3.14`(只產生 python3.14,沒有 python3)的 Linux/macOS 機器,或只有 py 啟動器的 Windows,「任何 python」不成立於現況清單,照字面實作要嘛維持現況(exec 不存在的 python3,shell 只回 127、沒有說明,違反 [S4] 要印指令回 2),要嘛實作者自己擴清單(spec 沒定義擴成什麼、跟第 1 點兩處實作的關係)。
3. 沒寫:「只有 python(沒有 python3)」的機器,install.sh 要不要用 `python`。python 在老 Linux 可能是 Python 2,`scripts/lumos` 在 py2 下是語法錯誤,不是說明——這種情況 spec 沒歸類。
4. 補一條:get.sh 走 `curl | bash` 冷啟動(舊複本沒有新共用檔),所以沒法借 shell 共用檔,spec 已知;但因此要在每支入口自己寫一段「找 python*」,spec 說「不各自找直譯器」與此衝突。

## F4 掛鉤註冊的直譯器路徑在 POSIX/Codex 分支沒加引號,改用 sys.executable 後含空白的路徑會讓 hook 全壞
severity: major
blocking: 是 — 家目錄含空白(/Users/John Smith)或直譯器裝在含空白的目錄時,寫進設定檔的命令被 shell 切詞,所有 Claude/Codex hook 靜默失敗。
引句:「不再用 `shutil.which("python3")`」
file: `scripts/merge-claude-settings.py:118`
1. 現況 POSIX 分支 `return f'{_PY} "${{HOME}}/.claude/hooks/{rel_path}"{_bf}'`(:118)與 Codex 非 Windows 分支(:103、:107)都只引號括 hook 路徑,直譯器 `{_PY}` 沒括;只有 Windows 分支有引號。
2. 實測:`sh -c "<含空白路徑>/python3.14 -c 'print(1)'"` → `No such file or directory`(在第一個空白處被切開)。
3. 以前 `shutil.which("python3")` 通常落在 /usr/bin 或 /opt/homebrew/bin,無空白;spec 改成 `sys.executable` 後,uv / pyenv / venv / 使用者自訂目錄下的直譯器都可能成為被寫入的值,曝光面變大。[S5] 的測試名 t_hook_cmd_uses_running_python 只驗「寫的是目前這支」,沒要求引號。
4. 此外:sys.executable 為空字串或 None(嵌入式執行)時 spec 沒說怎麼辦。

## F5 LUMOS_PYTHON 的語意只有「第一個候選」,空字串、不存在、舊版、帶參數、含 ~ 都沒定義
severity: minor
blocking: 否 — 有訊息列出候選版本可診斷,屬語意未定義,不會做出壞系統。
引句:「依序試 `$LUMOS_PYTHON`、`python3.14`、`python3.15`、`python3.16`、`python3`、`python`」
1. 實測 bash:`LUMOS_PYTHON=""` → 執行 `"$LUMOS_PYTHON" -c …` 得 `: command not found`(shell 份要先 `[ -n ]`);`LUMOS_PYTHON="py -3.14"` → command not found(整串當一個指令名);`LUMOS_PYTHON="~/bin/python3"`(引號內 ~ 不展開)→ No such file。Python 份用 os.execv 也不吃帶參數的字串。
2. 「挑第一個過的」意味著使用者釘住的 LUMOS_PYTHON 打錯或指到 3.9 時被靜默略過、改用後面某個 3.14 跑;釘版本的人(CI 容器、除錯)得到與預期不同的直譯器。spec 沒說「有設但不合格」該擋還是略過。
3. 重跑守衛的環境變數會被子行程繼承:lumos 被 3.9 啟動 → execv 3.14(守衛已設)→ 它再叫的任何子行程若又用 PATH 上的 `python3 scripts/lumos`(測試、腳本),會在舊版走到「重跑後仍是舊版 → 直接報錯」而不是重跑。引句:「重跑前設一個環境變數,重跑後的程序若還是舊版就直接報錯,不會無限重跑」——守衛需要綁「這次重跑的目標路徑/行程」而非全域旗標。⚠ 未實作驗證,由環境變數繼承語意推得。

## F6 pre-commit / pre-push 沒說「擋」放在哪一道,字面實作會連沒有圖譜的專案、空提交、只改文件的提交都擋
severity: major
blocking: 是 — 第 3 點寫成一條「找不到就擋」,pre-commit 現況大量提早 exit 0,實作者把共用檔放最前面就會擋掉本來根本用不到 Python 的提交。
引句:「`pre-commit`、`pre-push` 改 source 共用檔;找不到 3.14 時擋下(rc 1)並印同一段說明」
file: `scripts/hooks/pre-commit:37`
1. pre-commit 有 Gate 0「圖譜不存在 → 放行」(:37)、空 staged → exit 0、docs-only 於 Gate 2 exit 0;Python 只在 :50 之後才用。若「source 共用檔並擋」放在檔頭(最自然的做法,取代 :50 的 CC_PY),這些原本 exit 0 的提交在沒有 3.14 的機器上一律變成被擋。
2. `core.hooksPath` 設成共用路徑、或 hooks 被複製進沒有 scripts/lumos 的 repo 時,原本「無 lumos → 放行」的降級(pre-push:68-70、:118-120 註解稱「不為缺環境 brick push,CI 兜底」)被改成 brick;spec 沒說 -f scripts/lumos 不存在時要放行還是擋。
3. pre-push 也逐 ref 處理刪除分支/tag 推送(_lsha 為零則 continue)——這類推送原本也不需要 Python,放檔頭一樣被擋。
4. 需要 spec 明說:擋下發生在「第一次確定需要 Python」之處(例如 :50 位置之後、且已判定 lumos 專案)。

## F7 探測本身的成本與副作用未估:macOS 殘樁與 uv 查詢每次提交多次執行
severity: minor
blocking: 否 — 只是效能與提示副作用,不影響正確性。
引句:「工具應依固定順序試候選、只接受版本 ≥ 3.14 的那一個」
1. 沒有 Command Line Tools 的 macOS,執行 /usr/bin/python3 會跳出安裝 CLT 的對話框(GUI 客戶端還會卡住);候選探測會在每次 commit 的三支掛鉤各跑一次。
2. 最壞情況(全落空)要起 6 個候選子行程加一次 `uv python find`;`uv python find` 在含 .venv 的目錄下優先回傳專案 venv 的直譯器,結果隨 cwd 變。spec 未說要不要快取(例如同一次 git 操作只解一次、或存環境變數傳給後面的掛鉤)。

## F8 升級後既有的 Claude/Codex 設定仍指向舊 3.9 絕對路徑,spec 只寫了「回退」的重跑安裝,沒寫「升級」的
severity: minor
blocking: 否 — hook 會經第 2 點的重跑機制自救,只是慢且訊息位置不對。⚠ hook 是否把子行程 rc 2 往外傳未逐支驗。
引句:「使用者機器上的 Claude/Codex 設定:回退程式碼之後」
file: `scripts/hooks/claude/impact-hook.py:833`
1. 升級後使用者不重跑安裝,設定裡仍是 /usr/bin/python3(3.9);各 hook 以 `[sys.executable, lumos, …]` 叫 lumos(impact-hook:833、dispatch-lens-hook:239、check-graph-sync:750、lumos-entry-hook:256)→ 在 3.9 下走第 2 點:有 3.14 就多一次 exec(hook 天花板 10~15 秒,冷啟動吃預算),沒有就回 2 並印說明。
2. Claude hook 的 exit 2 語意是「阻擋」;這些 hook 是包子行程並吞回傳碼,通常 fail-open,但 spec 沒要求驗這件事,也沒把「升級後重跑 install」寫進〈文件〉的升級注意。
3. 第 4 點只讓「新寫入」的設定用 sys.executable,舊設定何時被覆蓋(lumos update?)沒寫。

## F9 Windows 的 lumos.cmd 包裝在只有 py 啟動器的機器上叫不起來,與「版本交給 lumos 開頭」的前提衝突
severity: minor
blocking: 否 — 只影響「只有 py 啟動器」這一種機器,且 `py -3.14 scripts\lumos` 可手動繞。⚠ 未在 Windows 實測。
引句:「Windows 的 `lumos.cmd` 包裝照舊寫指令名不寫死路徑,版本同樣交給 lumos 開頭」
file: `scripts/lumos:16394`
1. 包裝內容是 `python3 "src" %*` 或 `python "src" %*`(安裝當下 `shutil.which` 挑,挑不到寫 `python`)。PATH 上沒有 python/python3 只有 `py` 時,包裝本身就找不到指令,根本跑不到「lumos 開頭」的 `py -3.14` 候選。
2. 「版本交給 lumos 開頭」只在 PATH 上有任一 python 時成立,spec 第 5 點沒交代這個前提。

## 已讀無 finding
- 〈做法〉第 6 點 CI:CI 容器(python:3.14 映像或 setup-python 3.14)取得 3.14 無疑,不受上述環境問題影響;已讀,無 finding。
- 〈做法〉第 8、10 點、〈範圍〉、〈回退〉除 F8 外:已讀,無 finding。
- Linux 只有 python3.12:照 spec 走 rc 1/rc 2 並印發行版套件或 uv 指令,行為明確;訊息清楚度取決於實作,spec 已要求列出候選與版本,無 finding。
- 「找到 python3=3.14 但路徑含空白」在 git 掛鉤 shell 份:只要實作時候選路徑有加引號即可,spec 未禁止;F4 只針對寫進設定檔那一處。

最嚴重等級 major,blocking 共 5 條(F1、F2、F3、F4、F6)。
