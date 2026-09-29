severity: major

鏡頭:邊界與可執行性。實測環境:macOS,/opt/homebrew/bin/python3.14、/usr/bin/python3(3.9)、perl 5、uv 0.11;Windows 與 Linux 沒有真機,標 ⚠ 的是推論。實驗都在 mktemp 目錄。

## F1 `LUMOS_PYTHON` 指到 shim 或包裝腳本時,第 2 點的比對規則會無限重跑
severity: major
blocking: 是 — 照字面實作,`LUMOS_PYTHON` 設成 pyenv/asdf shim 這類常見值,lumos 與 git 掛鉤會無限 exec、永不結束
引句:「版本低於 3.14,或 `LUMOS_PYTHON` 有設、而且不是目前這一支(兩者都比 `os.path.realpath`)」
1. 用 mktemp 造 `shim`(內容 `exec /opt/homebrew/bin/python3.14 "$@"`),照 spec 字面寫了一個 20 行的檢查腳本:LUMOS_PYTHON 與 sys.executable 比 realpath、不同就用候選印出的 sys.executable 做 execv、重跑前設 `LUMOS_REEXEC_PYTHON`。
2. 執行 `LUMOS_PYTHON=$D/shim python3.14 lum.py`:候選探測通過,印出 `/opt/homebrew/.../python3.14`;重跑後新行程的 `realpath(LUMOS_PYTHON)`(shim 本身)仍不等於自己的 realpath,又判「不是目前這一支」,又重跑。重跑六次以上仍未通過(我在腳本裡設上限 6 才停)。
3. 防無限重跑只在「變數等於自己、而且版本仍舊」時才擋;這裡版本是 3.14,擋不到。「通過檢查後才清變數」也沒機會發生。
4. 同型輸入:任何 realpath 不等於它印出的 `sys.executable` 的值——pyenv/asdf shim、shell 包裝腳本、Nix 或 conda 的 wrapper。
5. 缺的條款:通過條件要改成「重跑後已經在 `LUMOS_REEXEC_PYTHON` 指的那支上」就算通過(不再比 LUMOS_PYTHON),或比對的兩邊都用探測印出的路徑。

## F2 get.sh 舊安裝複本的新訊息「請加 --pull 重跑」加了也一樣失敗
severity: major
blocking: 是 — 訊息叫人做的動作在現行 get.sh 下不會改變結果,使用者卡在死循環
引句:`get.sh` clone 或已存在之後 source 共用檔
1. 現行 get.sh 自己不做 pull:`--pull` 只是原樣轉給 `python3 scripts/lumos bootstrap`,由 Python 端的 `_pull_source_or_abort` 去拉。
2. 舊複本沒有共用檔 → get.sh 在呼叫 bootstrap 之前就要 source 它 → 印「加 --pull 重跑」回 2,根本走不到 bootstrap。
3. 使用者加 `--pull` 重跑:get.sh 仍然先 source、仍然找不到,同一句訊息,回 2。spec 沒說 get.sh 要自己在 source 之前先 `git pull`,也沒說這種情況該怎麼救。
4. 對照 get.ps1:它用自己的清單找到 3.14 之後才呼叫 bootstrap,拉新會發生,沒有這個問題;只有 get.sh 死。
5. 缺的條款:get.sh 見到 `--pull` 時自己先在 source 之前 `git -C "$LUMOS_HOME" pull`(或改成訊息叫人直接 `git -C ~/harness/lumos-toolchain pull` 再重跑);[S4] 的測試要用「舊複本 + --pull」實跑一次。
file: `get.sh:47`

## F3 perl alarm 包起來的探測對「不存在的路徑」回 0 且沒輸出,會被當成合格
severity: major
blocking: 是 — 候選是過期的 `git config lumos.python`(被刪掉的 venv、升級後消失的 Cellar 路徑)時,字面實作會接受一個空路徑
引句:shell 那份有 perl 就用 `perl -e 'alarm 5; exec @ARGV'` 包起來,逾時算這個候選不合格
1. 實測 `perl -e 'alarm 5; exec @ARGV' /nonexistent -c 1 </dev/null; echo $?` 印 `0`,沒有任何錯誤訊息(perl 沒開 -w 時 exec 失敗不吭聲、正常退出)。沒包 perl 時同樣的呼叫是 127。
2. spec 對「不合格」的定義寫的是「回 1」與「逾時」;沒有一句說輸出必須非空、必須是絕對路徑、必須指到可執行檔。逾時實測 rc=142,所以逾時那條會照 rc 判對;不存在這條會判錯。
3. 結果:有 perl 的機器上(基本上是全部的 macOS/Linux),`git config lumos.python` 指到已消失的路徑 → 第 ② 個候選「通過」、印出空字串 → 呼叫端拿空字串當直譯器,之後 `"$PY" scripts/lumos` 是「command not found」127,掛鉤沒有走到「找不到 3.14」的說明;沒有 perl 的容器反而走對。同一條輸入兩種行為,測試只在其中一邊會紅。
4. 缺的條款:通過條件 = rc 0 而且輸出是非空的絕對路徑而且該路徑 `-x`;[S1] 的測試要造「不存在的候選 + 有 perl」這一格。

## F4 共用檔在 `set -e`/`set -u` 的呼叫端會提早靜默死亡或報 unbound variable
severity: major
blocking: 是 — get.sh 是 `set -euo pipefail`,pre-commit 是 `set -u`;共用檔沒有寫「不得因候選失敗而終止呼叫端」,字面實作會讓掛鉤與 get.sh 在最該印說明的時候直接死掉
引句:被 source 時找一次、結果放進變數,呼叫端不重找
1. 實測 `set -euo pipefail; out=$(perl -e 'alarm 1; exec @ARGV' sleep 3 </dev/null)`:腳本靜默以 142 結束,「not reached」沒印。任何一個不合格候選(3.9 的 `python3` 回 1、逾時 142)在 get.sh 裡只要不是寫成 `|| true`/`if`,get.sh 就無訊息退出——而不合格候選是這段的常態,不是例外。
2. 實測 `env -i PATH=/usr/bin:/bin bash -c 'set -u; echo $HOME/.local/bin/python3.14'`:`HOME: unbound variable`,rc=127。第 ④ 點固定位置含 `$HOME/.local/bin/python3.14`,而 spec 說固定位置是給「路徑很短的環境」(排程、圖形用戶端)用的——正是最可能沒有 HOME 的環境;pre-commit、pre-push 都是 `set -u`,掛鉤會以 rc 127 與一句 bash 錯誤結束,而不是 [S3] 要的說明。
3. 缺的條款:共用檔內一律 `${HOME:-}` 並跳過空 HOME 的候選、所有探測寫成不會觸發 errexit 的形式;[S1]/[S3] 的測試要在 `set -euo pipefail` 與 `env -i` 下跑一次。

## F5 Git Bash 上 Python 印出的路徑帶 `\r`,shell 那份會拿到壞路徑
severity: major
blocking: 是 — ⚠ 未在 Windows 真機驗,但這是 Git Bash 的已知行為:原生 Windows Python 的 `print` 在管線上輸出 `\r\n`,MSYS bash 的 `$(...)` 只剝 `\n`
引句:★之後一律用它印出的絕對路徑★(重跑、寫設定、擋下訊息)
1. spec 明說 ⑤ `py -3.14` 「Git Bash 裡也叫得到」,shell 那份因此會在 Git Bash 執行:`PY="$(py -3.14 -c '…print(sys.executable)')"` 得到 `C:\Python314\python.exe\r`。
2. 之後 `"$PY" scripts/lumos` 是「command not found」,或說明訊息裡路徑尾巴多一個 `\r` 把終端游標拉回行首、訊息被蓋掉。
3. 缺的條款:shell 那份取得輸出後 `tr -d '\r'`(或 Python 端 `sys.stdout.write(sys.executable)`,不用 print、不帶換行,兩邊都不出問題);同一段也讓 shell 與 PowerShell 兩份「共同項目」的比對測試多一格 Windows 輸出。
4. 同一個環境上的旁註 ⚠:Git for Windows 的 MSYS perl 上 `alarm 5; exec @ARGV` 是否真的殺得掉 exec 出去的原生 Windows 行程,我沒有機器驗;spec 的「誠實界線」只講了「沒有 perl」,沒講「有 perl 但 alarm 殺不掉」。

## F6 Windows `lumos.cmd` 用「PATH 上有」判斷會選到商店替身
severity: major
blocking: 是 — 與同份 spec 自己的「找得到一律要真的執行成功」矛盾,而且正是現行程式碼那段註解記過的事故
引句:PATH 上有 `python3`/`python` 就寫指令名,都沒有而有 `py` 就寫 `py -3`,版本交給第 2 點
1. 現行 `cmd_install` 用 `shutil.which(c)` 判斷,Windows 上 `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe`(商店替身)`which` 找得到、執行卻失敗。spec 第 5 點自己寫「Windows 的商店替身 `python.exe` 找得到、執行卻失敗」,卻把這條規則只套在安裝入口,`lumos.cmd` 那段沿用「有沒有在 PATH 上」。
2. 輸入:只裝了 python.org 的 3.14(有 `py`,PATH 上沒有真的 `python3`)、系統另有商店替身的機器。`lumos install` 由 3.14 跑完,shim 寫 `python3 "…lumos" %*`;之後每次打 `lumos` 都是替身,「版本交給第 2 點」根本走不到(替身連 Python 都不是)。
3. 更直接的做法:`lumos install` 已經跑在 ≥3.14 上(spec 自己說),`lumos.cmd` 可以寫進 `sys.executable` 的絕對路徑;若堅持只寫指令名,判斷條件要改成「執行成功」而不是「在 PATH 上」。
file: `scripts/lumos:16379`

## F7 lumos 開頭的檢查沒有說 git 不存在或不在 repo 內時怎麼辦,會印出追蹤
severity: minor
blocking: 否 — 只影響極端環境的錯誤呈現;正常路徑與「找不到 3.14」的說明不受影響
引句:②`git config lumos.python`(`lumos init`、`lumos update`、`lumos install` 在該 repo 跑完時
1. 第 ② 個候選要在 lumos 開頭(標準庫 import 之後)讀 `git config lumos.python`。環境沒有 git(精簡容器、PATH 被清空,我用 `env -i PATH=/nonexistent` 驗的是 git 找不到)時,`subprocess.run(["git", …])` 丟 FileNotFoundError;spec 沒有規定要吞掉,字面實作會在最前面炸出追蹤,違反 [S2]「不印追蹤」。
2. 在非 repo 目錄(實測 `git config --get lumos.python` 回 1、無輸出)與 bare repo 不是問題,只要呼叫端把「非 0 = 沒設」當正常。
3. cwd 與目標 repo 不同時(全域 `lumos` 從別處對某專案下指令),讀的是 cwd 那個 repo 的設定,不是目標專案的;spec 沒說以哪個為準。
4. 已驗無問題:相對的 `core.hooksPath=scripts/hooks` 下,pre-commit 從根目錄與子目錄 commit 時 `${BASH_SOURCE[0]}` 都是 `scripts/hooks/pre-commit`,`cd "$REPO_ROOT"` 之後仍存在——只要 source 發生在 cd 之前或路徑先解成絕對,沒有問題(spec 說「或 checkout 路徑定位」,實作時要挑後者)。

## F8 `lumos init/update/install` 會把一次性的 `LUMOS_PYTHON` 或暫時路徑固化進 repo 設定
severity: minor
blocking: 否 — 事後有 doctor 提醒與候選驗證兜底,壞的是「意外固化」而不是擋人
引句:在該 repo 跑完時,把自己的 `sys.executable` 寫進去
1. 輸入:`LUMOS_PYTHON=/tmp/venv/bin/python lumos update`,或在 uv run、tox 暫存環境裡跑 update。`sys.executable` 是暫時路徑,被寫進 `.git/config`;spec 沒有排除。
2. 之後那個路徑消失,第 ② 個候選失敗而往下(不會擋),但每次多一個失敗候選;若人手動 `git config lumos.python <指定的>`,下一次 `lumos update` 用別支直譯器跑就會把它覆寫,spec 沒有「已有值且仍合格就不覆寫」的條款。
3. 缺的條款:已設且仍合格則不動;`sys.executable` 位於暫存目錄(或由 `LUMOS_PYTHON` 臨時指定)時不寫。

## 各節
- 範圍、做法第 3、4、6、7、9、10、12、13 點、回退、實務隱患、誠實界線:已讀,邊界面無新 finding(效能數字「第一個候選就命中約 30 毫秒」我沒重測,不判)。
- 固定位置在 Linux(`/opt/homebrew` 不存在)只是跳過候選,行為正確;Linux Homebrew 在 `/home/linuxbrew/.linuxbrew/bin`、不在清單,屬覆蓋面而非錯誤,靠 PATH 的 ③ 兜住。
- `LUMOS_PYTHON` 含空白路徑、符號連結、venv:perl 的 list 形式 exec 與 Python 的 realpath 比對都實測正常(venv 的 realpath 落在基底直譯器,與被 venv 外的同一支比對相等,不會誤重跑)。真正的問題在 F1(realpath 不等於印出的 sys.executable 的那一類)。
- `uv python find --system --no-python-downloads '>=3.14'`:uv 0.11.19 上旗標有效,找不到時 rc 2、不下載。

最嚴重等級 major,blocking 共 6 條(F1–F6),minor 2 條(F7、F8)。
