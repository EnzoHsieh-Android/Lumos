severity: major

## F1 LUMOS_PYTHON 指向包裝腳本或 shim 時,重跑守衛擋不住,無限 execv 空轉
severity: major
blocking: 是 — 照字面實作,設了 LUMOS_PYTHON 指向 pyenv/asdf/mise shim 的人,每次 lumos 啟動與每次 Claude/Codex 掛鉤都會卡死在重跑迴圈
引句:「防無限重跑:重跑前設 `LUMOS_REEXEC_PYTHON=<目標絕對路徑>`;開頭檢查時,只有「這個變數有值、而且等於自己的 `sys.executable`、版本卻還是舊的」才算重跑失敗」
1. 第 2 點的重跑條件是「版本低於 3.14,或 `LUMOS_PYTHON` 有設且 realpath 不等於目前這一支」;第 1 點又規定重跑一律用候選印出的 `sys.executable` 絕對路徑,不用候選名字。
2. `LUMOS_PYTHON` 是 shim(pyenv/asdf 的 shims 是 shell 腳本)或任何包裝腳本時:候選驗證印出的是底層真直譯器路徑,重跑後子行程的 `realpath(sys.executable)` 是底層真路徑,`realpath(LUMOS_PYTHON)` 是 shim 自己,兩者永遠不等,第二次開頭檢查又判「要重跑」。
3. 防重跑守衛只在「版本仍舊」時才報錯;這裡版本是 3.14,守衛不成立;且 spec 規定通過檢查後把變數清掉,無從累計。結果是無限 execv。
4. 實測(臨時腳本照 spec 字面寫開頭檢查,`LUMOS_PYTHON` 指向 `exec /opt/homebrew/bin/python3.14 "$@"` 的 shell 包裝):跑滿我設的 200 次上限才停,共 11.8 秒、user 3.8 秒、sys 1.6 秒(每次約 59 毫秒);沒上限就永遠不停。對照:`LUMOS_PYTHON` 是指向同一支 3.14 的 symlink 時,realpath 相同,0 次重跑正常。
5. 放大:Claude/Codex 掛鉤每次工具呼叫都啟動 lumos,這個環境設定下每次工具呼叫都卡住(掛鉤逾時前吃滿 CPU);spec 自己在第 1 點與 PRIOR-ART 點名 pyenv shims 是預期環境。
6. 缺口修法方向:「不是目前這一支」的比對要用「候選驗證印出的 sys.executable」對「自己的 sys.executable」,不是拿 `LUMOS_PYTHON` 原值 realpath 比;或重跑後子行程只要 `LUMOS_REEXEC_PYTHON` 等於自己就不再因 `LUMOS_PYTHON` 重跑。spec 兩者都沒寫。

## F2 多個 lumos init/update/install 同時寫 `git config lumos.python`,git 會拒絕(rc 255),spec 沒說失敗怎麼處理
severity: minor
blocking: 否 — 只影響同一 repo 同時跑兩個寫入指令的罕見時序,實作者最多讓指令多報一次錯,不會做出壞系統
引句:「`lumos init`、`lumos update`、`lumos install` 在該 repo 跑完時,把自己的 `sys.executable` 寫進去」
1. 實測:同一個 repo 一次背景啟動 30 個 `git config lumos.python /x/N`,多個回 `error: could not lock config file .git/config: File exists`(非零退出);全部結束後沒有殘留 `config.lock`,最後值是其中一個(/x/29),沒有損壞。第二輪 60 個同時寫也是同樣現象。
2. spec 與 [S1] 寫「應寫進」,沒寫寫入失敗(鎖競爭、`.git/config` 唯讀、殘留 stale `config.lock`、bare/非 repo)時 init/update/install 是失敗還是忽略。字面實作(檢查回傳碼)會讓一次鎖競爭把整個 `lumos update` 變成非零退出,而 update 已經完成了其他更新。
3. 另一個時序:寫入與別的會談的 `git commit`/`git gc` 也搶同一把 `.git/config.lock`,同一原因。
4. 多 worktree 共用同一份 `.git/config`:兩個 worktree 各用不同 3.14 跑 update,後寫者覆蓋前者,無害但候選②的值是「最後一次 update 的那支」,不是每個 worktree 各自的。
5. 缺口:未規定寫入是盡力而為(失敗只印警告、不改變回傳碼)、也未規定是否重試。

## F3 效能節只給單點數字,沒涵蓋最壞總時間與設了 LUMOS_PYTHON 的常態成本
severity: minor
blocking: 否 — 措辭與精度問題,不改不會做出壞行為
引句:「第一個候選就命中約 30 毫秒,全部落空加 uv 約 0.2 秒」
1. 實測(本機 macOS,3.14 在 /opt/homebrew,20 次平均):跑一次 3.14 空程式 26 毫秒;`perl -e 'alarm 5; exec @ARGV'` 包起來 30 毫秒(perl 額外約 3 毫秒,可忽略);`git config --get lumos.python` 每次是一個獨立 git 行程,約 18 毫秒(讀得到或讀不到相同);`command -v` 找不存在的名字約 6 毫秒(兩個);`uv python find --system --no-python-downloads` 找得到 187 毫秒、找不到 175 毫秒;`os.execv` 重跑到同一個 3.14 約多 20 毫秒(實測雙倍啟動 46 對 26)。spec 的 30 毫秒、65 毫秒、0.2 秒與實測同量級,數字可信。
2. 最常見機器候選數:macOS+Homebrew 3.14 在 PATH 或固定位置,①未設、②18 毫秒、③或④命中,約 1 到 3 次啟動探測,約 50 到 80 毫秒;Linux 只有系統 3.12:②18 毫秒、③④用 `command -v`/檢查檔案存在幾乎 0、⑤無 py、⑥有裝 uv 就加約 180 毫秒、⑦`python3` 探測 3.12 約 30 毫秒、`python` 再約 30 毫秒,全部落空約 80 毫秒(無 uv)到 260 毫秒(有 uv),之後擋下。可接受。
3. spec 沒寫的最壞情況:每個候選逾時 5 秒,共約 12 個可探測候選,全部卡住時 shell 有 perl 約 60 秒才擋下;無 perl 則無上限(誠實界線已承認);Python 那份(lumos 開頭)另外也走一次同樣的最壞路徑,掛鉤先走完 shell 再叫 lumos,總時間是兩份相加,而且結果不共用(掛鉤找到的目標其實可以用 `LUMOS_PYTHON` 或環境傳給 lumos 省掉第二次)。
4. 沒裝開發工具的 macOS,`/usr/bin/python3` 是最後候選,舊碼路徑下每次提交會再跳一次安裝對話框(perl 5 秒逾時只殺行程,不關對話框);spec 已寫「排在後面」,但沒 3.14 的機器會走到它,誠實界線沒提每次提交重跳。
5. 設了 `LUMOS_PYTHON` 且與 Claude/Codex 註冊的直譯器 realpath 不同(例如註冊用 uv 的 3.14、環境變數指 Homebrew 的),每次工具呼叫多一次重跑約 20 到 30 毫秒(實測,重跑發生在檔案最前面、還沒載入 3.5 萬行前,所以不貴);spec 效能節只算了舊註冊那一種。整支 `lumos --version` 本身約 440 毫秒,所以相對成本約 5%,不構成問題。

## 已讀,無 finding
- 範圍、做法第 3 到 13 點、條款 S3 到 S10、回退、誠實界線:併發、資源角度無額外 finding。post-commit 不 source 共用檔,不增加提交路徑成本;`realpath` 比對本身成本可忽略(實測與 3.14 空程式相同,約 25 毫秒總量)。
- 並行寫檔:除 F2 外沒有其他共享可寫狀態;共用檔是 source 進變數,每個掛鉤行程各自找一次,無跨行程共享,無競態。

最高 major,blocking 共 1 條
