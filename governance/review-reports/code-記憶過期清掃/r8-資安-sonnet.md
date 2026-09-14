severity: major

## 發現1

severity: major

引句:「r = _git("rev-parse", "--show-toplevel", cwd=pathlib.Path.cwd())」

觀察到什麼:
r8 把「檔案存在檢查」的允許範圍從整個 `~/.claude` 收窄成 `~/.claude/hooks`、`~/.claude/skills` 與「目前 git 專案根」三處(`_ALLOWED_ROOTS()`)。但第三處是用 `git rev-parse --show-toplevel`、以 `pathlib.Path.cwd()` 當 cwd 現場問出來的——它問到的頂層目錄本身沒有再排除任何路徑。只要使用者用 bare-git/chezmoi/yadm 這類「把 `$HOME` 本身當 git 專案根」的常見 dotfiles 管理法(或這次 Claude Code 開的專案剛好是以 `$HOME` 為頂層的 repo),這第三個允許根就等於整個家目錄——r6/r7 想堵的那個「~/.ssh/id_rsa、登入憑證檔存不存在」探測器原封不動地回來了,而且範圍比 r6 之前的「整個 `~/.claude`」還大(是整個 `$HOME`)。

實測(在 `/tmp` 下建一個以自己為頂層的 git repo,模擬 `$HOME` 用 git 管理的情境,不動 repo 本身任何檔案):

```
$ mkdir -p /tmp/msweep-test/fakehome/.claude/{hooks,skills}
$ git -C /tmp/msweep-test/fakehome init -q && git -C ... commit -q -m init
$ echo '{"secret":"xxx"}' > /tmp/msweep-test/fakehome/.credentials.json
$ HOME=/tmp/msweep-test/fakehome python3 -c '
    os.chdir(HOME)
    exec(open("memory-sweep.py 的模組載入").read())
    print(ms._ALLOWED_ROOTS())
    print(ms._chk_file_exists("~/.credentials.json", cwd))
  '
allowed roots: [.../fakehome/.claude/hooks, .../fakehome/.claude/skills, .../fakehome]
chk_file_exists: True
```

`_safe_path("~/.credentials.json")` 順利通過白名單(因為 `real.relative_to(fakehome)` 成立),`_chk_file_exists` 回 `True`——精確反映該檔存不存在。對照組:cwd 不在「以家目錄為頂層」的 repo 時,同一條路徑會被擋掉(回 `None`),證明是這個第三根造成的。

會造成什麼:
攻擊者只要能讓一篇 `.md` 落進記憶目錄、塞一條 `file-exists: ~/.claude/.credentials.json`(或任何 `~/.ssh/id_rsa` 等)這種 verify claim,只要受害者在「dotfiles 用 git 管理、頂層是 `$HOME`」這種不算罕見的環境下用 Claude Code 開任何一個 session(不必是 dotfiles 專案本身,只要 cwd 往上第一個 `.git` 剛好是 `$HOME`),清掃報告就會精確告訴攻擊者「這個憑證檔存不存在」——回到 r7 報告點名要堵死的那個問卷機,而且波及面比修法之前(`~/.claude` 全部)更大(整個 `$HOME`)。這正是題目點名要測的「允許範圍能不能被繞過(專案根判定被 cwd 影響)」。

建議怎麼修:
`_ALLOWED_ROOTS()` 的第三根不該無條件信任 git 頂層本身;至少要排除「頂層等於或高於 `$HOME`」的情況(例如頂層 `== pathlib.Path.home().resolve()` 或是 `$HOME` 的祖先時就不加這一根,只信任 `~/.claude/hooks`、`~/.claude/skills` 兩處)。

## 發現2

severity: major

引句:「for f in sorted(here.glob("*.md")):」

觀察到什麼:
r8 把「灌檔淹沒真正過期警告」的防線做成:等 `read_memories()` 把記憶目錄裡**所有** `*.md` 全部讀進記憶體之後,才在 `sweep()` 裡用 `MAX_FILES`(300)裁切、並在報告最前面喊「結果不完整」。但 `read_memories()` 這個「列出目錄+逐檔打開讀取」的迴圈完全不吃 `_inner_budget`/`deadline`,也不提早 `break`——它一定會把目錄下所有檔案讀完才輪到 `sweep()` 判斷是否超量。

這支 hook 在 `scripts/merge-claude-settings.py` 裡實際註冊的逾時是 `HOOK_BUDGET["memory-sweep.py"] = 12`(秒),同時是傳給腳本的 `--budget 12`,也是 Claude Code 外層對這個子行程的 SIGKILL 時限。實測:

```
$ python3 -c '寫 150000 個小 .md 檔進記憶目錄'
$ python3 -c '
    files = ms.read_memories(here, tally)   # 還沒進 sweep() 的 MAX_FILES 裁切
  '
read_memories: 150000 files in 10.298s
```

單是「列目錄+逐檔開檔讀取」15 萬篇小檔就要 10.3 秒,已經逼近這支 hook 真實註冊的 12 秒逾時上限;算上後面 `sweep()`(還沒裁切前就先算完 `len(files)`)、`cross_check()`(對圖譜跑一次 `rglob`)等後續步驟,以及正式環境可能更慢的磁碟/雲端同步資料夾,file 數量不需要誇張到不合理的地步就能讓整支 hook 在跑到 `_emit()`、也就是「喊出結果不完整」那一步之前,先被外層以 SIGKILL(繞過 try/except,檔頭註解自己也承認這件事)砍掉——這種砍法連 `sys.exit(0)` 的 fail-open 都碰不到,報告完全不會印。

會造成什麼:
r7 想解決的問題是「灌檔讓真正的警告被淹沒但報告還在」,r8 的修法只驗證了「報告有印出來、而且喊了結果不完整」;但沒有處理「檔案枚舉+讀取本身要花的時間不受任何預算節流」這一段。攻擊者(或單純製造大量記憶檔的環境問題)只要讓記憶目錄檔案數量夠多,就能讓整支 hook 連「喊出來」的機會都沒有——結果是**完全沒有報告**印進對話,比修法設想的「報告不完整但有喊」更糟,而且從對話端完全看不出這支 hook 曾經跑過(唯一還能看出來的只有 `_hookevent` 記的那筆 `error`/逾時事件,但那不會進對話)。這正是題目點名要測的「灌檔同時讓報告在安靜模式不輸出」。

建議怎麼修:
`read_memories()` 的檔案列舉與讀取本身也要吃 `deadline`——例如 `sorted(here.glob("*.md"))` 之後先看檔案數量,一旦超過 `MAX_FILES` 就不要再繼續 open/read 剩下的檔(用 `itertools.islice` 或提早 slice 這個 iterable,而不是等全部讀完才在 `sweep()` 裡裁切),讓「喊出結果不完整」這件事的成本跟檔案數量無關、能穩定在預算內完成。

## 已確認

- `MAX_FILES`(300)/`MAX_CLAIMS_TOTAL`(600)上限與「結果不完整」喊聲,在檔案數量落在數萬篇這種量級內(尚未觸發發現2的 SIGKILL 情境)時,無論安靜或手動模式都會正確印出且排在報告最前面,`tally.changed` 也正確把 `flood` 算進去而不會被安靜模式吞掉(用 20000 篇檔實測、以及對照 `scripts/test_lumos.py` 的 ㉑ 案例都通過)。
- `_ALLOWED_ROOTS()` 收窄到 `~/.claude/hooks`、`~/.claude/skills` 之後,在「專案根不等於/不高於 `$HOME`」的一般情況下,`~/.ssh/id_rsa`、`~/.credentials.json`、`~/.claude/projects/<其他專案>` 這類路徑確實回 `None`,探測不到。
- `~/.claude/skills` 底下若有符號連結指向樹外的檔案,`_safe_path` 因為是對 `arg` 完整路徑 `.resolve()` 之後再跟已 `.resolve()` 過的允許根比對,連結會被還原到真正落點再判斷,實測指到樹外的連結一樣回 `None`,沒有被繞過。
