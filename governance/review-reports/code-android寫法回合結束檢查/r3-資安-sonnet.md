severity: major

審了 `r3-repair.patch` 全份,對照 HEAD `8717114b0` 的實際檔案。所有攻擊都在臨時複本實跑,git 版本 Apple Git 2.39.2。臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/資安-sonnet/` 和另外兩個暫存檔已用字面路徑刪掉。

**核對第二輪資安席**
- **r2 F1(嵌套 repo 過濾器)**:已堵住。我用外層 repo、gitlink 子 repo、子 repo 自己 `.git/config` 設 clean 過濾器、racy 檔重做。不帶旗標的 `git status` 造出記號檔;帶 `--ignore-submodules=all` 後記號檔不出現。工作樹模式其餘 git 呼叫(`rev-parse`、`cat-file -e`、`cat-file --batch-check`、`cat-file --batch`、`ls-tree`、`config`)都不會執行過濾器、fsmonitor 或外部 diff。`status` 的兩個呼叫點都經 `_lint_wt_git`,都帶旗標。
- **r2 F2(ast-grep 照 PATH 找)**:處置不夠,見下面 F3。
- **其他已看,無**:
  - 白名單與不開 shell 的路徑沒退步。
  - 暫存 SARIF 清掃只刪自己 uid 的一般檔,用 `lstat` 檢查,不跟符號連結。
  - SARIF 暫存檔由 `mkstemp` 建立。
  - `_mark_event` 的匯入路徑是鉤子自己的已解析目錄。
  - SIGINT、SIGHUP 收尾只讓鉤子靜默放行,不涉及越界。
  - `unchecked_kind` 只用來分類事件,內容不進給 AI 的文字。
  - 密鑰、信箱、安裝腳本下載來源:本 diff 沒新增。
  - 提示注入面:沒有新增的外來自由文字進派工詞。

**F1 `_git_untrusted_c` 用 `--get-regexp` 列過濾器名字,名字含非 UTF-8 位元組時列不到,工作樹模式的 `git status` 仍執行 clean 指令**

- 攻擊路徑:
  - 誰:把整個目錄交給使用者的人。純 clone 不會帶 `.git/config`,所以交付形式是整個目錄(與 hook信任邊界 記載的交付路徑相同)。
  - 從哪:收工鉤子啟動 `lint-new --worktree`。`_lint_wt_pairs` 跑 `git status --porcelain=v1 -z --untracked-files=all`,實際走 `_lint_wt_git`。
  - 送什麼:
    - `.gitattributes` 寫 `*.txt filter=ev\xffil`。
    - `.git/config` 寫 `[filter "ev\xffil"]` 加 `clean = <指令>`。
    - 一支大小不變但內容改過的 racy 檔。
    - 已提交的 `.lumos/lint.json`,內含 ast-grep 字樣。
  - 拿到什麼:使用者帳號下執行任意指令。
- 成因:`git config --get-regexp '^filter\..*\.(clean|…)$'` 在 UTF-8 locale 下,`.` 不匹配非法位元組,整條設定不列出。我實測 `git config -z --name-only --get-regexp …` 完全沒有輸出。`_git_untrusted_c` 因此認為沒有過濾器,只回三個固定項。
- 實跑:
  - 載入 HEAD 的 `scripts/lumos`,對臨時 repo 呼叫 `_git_untrusted_c`,回傳只有 `core.fsmonitor=false`、`core.hooksPath=/dev/null`、`diff.external=` 三項。
  - 接著呼叫 `_lint_wt_git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")`,回傳 rc=0,記號檔被造出來。
  - 環境是 `LANG=en_US.UTF-8`。
- 補充:就算列得到,`k.decode("utf-8","replace")` 也會把名字改成含 U+FFFD,`-c filter.<改過的名>.clean=` 對不上原名,同樣關不掉。
- 修法方向:改用 `git config -z --list --name-only` 取全部鍵,在 Python 裡依位元組篩 `filter.` 開頭;名字不是合法 UTF-8 就當收不了,回 None(整次不檢查,fail closed)。這和既有的「名字含 `=` 或換行就不做」同一條。
- 引句:「r = _lens_git(repo_root, "config", "-z", "--name-only", "--get-regexp", r"^filter\..*\.(clean|smudge|process|required)$",」
- file: `scripts/lumos:40093`(`_git_untrusted_c`)
severity: major
blocking: 是

**F2 鉤子層自己的 `git status` 與 `lumos impact --diff HEAD` 沒走單一來源,可利用,不只是縱深**

- 攻擊路徑:
  - 誰:同 F1,交付整個目錄的人。
  - 從哪:Stop 時 `check-graph-sync.py` 跑,不需要 `.lumos/lint.json`。只要目錄有 `docs/*-knowledge/` 就過閘門 0,AI 該回合有任何編輯或 Bash 動作就過閘門 1,然後 `_git_status_entries` 跑 `git status --porcelain -uall`。
  - 送什麼:`.git/config` 設任意 clean 過濾器、`.gitattributes` 指到它、一支 racy 檔。
  - 拿到什麼:使用者帳號下執行任意指令。
- 實跑:
  - 用 `scripts/hooks/` 底下 `check-graph-sync.py` 的真檔,餵假逐字稿和 payload,鉤子結束後記號檔出現。
  - 單獨用該鉤子 `_git` 的完整旗標(`-c core.fsmonitor= -c diff.external=`)跑 `git status --porcelain -uall` 也造出記號檔。
  - `git diff HEAD --no-ext-diff --no-textconv --name-only`(`lumos impact --diff HEAD` 的形狀)在 racy 檔上同樣執行過濾器。
  - 嵌套 repo 版本同 r2 F1,鉤子層同樣沒擋。
- 判斷:
  - 編排者已知的 REVISIT:2026-11-20 寫「要不要改交人裁」,但這是已證實可直接利用的任意碼執行,觸發條件(開陌生目錄、一個回合的編輯)與當初設資安席的起因相同。
  - `_hookshared` 註解「已實測不觸發、因此沒列入的:…過濾器的塗抹指令」與實測相反。
  - 這個洞不是本 diff 新開的,但單一來源已存在、兩處改法很小:status 呼叫改走 `_git_untrusted_c` 並加 `--ignore-submodules=all`,或鉤子層用 `-c core.hooksPath=/dev/null` 加過濾器同樣的清單。把處置延到 11-20 不夠。
- 引句:「REVISIT:2026-11-20 收工點名鉤子自動跑的兩條還沒走 _git_untrusted_c、沒帶 --ignore-submodules:check-graph-sync.py 自己的 git status,與它呼叫的 lumos impact --diff HEAD(git diff 拿工作樹對 HEAD,racy 檔會跑 clean 過濾器);」
- file: `scripts/hooks/claude/check-graph-sync.py:336`
severity: major
blocking: 是

**F3 r2 資安 F2 的處置不夠:ast-grep 照 PATH 找,PATH 有空項或 `.` 時會執行 repo 根的同名檔**

- 攻擊路徑:
  - 誰:交付整個目錄的人。
  - 從哪:使用者非刻意殘留的環境,例如 `PATH=$PATH:$X` 而 `$X` 為空造成空項,或 `.`。`lint-new --worktree` 以 `subprocess.Popen(argv, shell=False, cwd=repo_root)` 執行白名單通過的 `ast-grep`。
  - 送什麼:repo 根放一支可執行的 `ast-grep`,加已提交的 `.lumos/lint.json` 宣告 ast-grep。
  - 拿到什麼:使用者帳號下執行任意指令。
- 實跑:`PATH=":/usr/bin:/bin"`、`"/usr/bin:/bin:"`、`".:/usr/bin:/bin"` 三種,`Popen(["ast-grep","scan"], cwd=<repo>)` 都跑到 repo 根的假 `ast-grep`。本機 `which ast-grep` 找不到,所以沒有別的解析結果擋在前面。
- 處置判斷:
  - Systems/pitfalls-code-loop 的 REVISIT 只寫了「專案自帶的 bin 進了 PATH(direnv、node_modules/.bin)」,沒涵蓋空項或 `.`。這種觸發更窄但不需要專案配合。
  - 回頭條件的描述需要補;修法也很便宜:啟動前用 `shutil.which` 解成絕對路徑,解出的路徑落在 `repo_root` 底下就不跑,或改用解出的絕對路徑執行。
  - 不改程式本身我歸 minor(前提是 PATH 非預設);建議至少把這個觸發補進 REVISIT。
- 同根因的 `stop-lint-hook.py` 的 `_trusted_lumos` 用 `shutil.which("lumos")`,對 PATH 空項也有同一形狀,但該段不在本 diff 內,這裡只順手提一句。
- 引句:「proc = subprocess.Popen(argv, shell=False, cwd=repo_root, start_new_session=True,」
- file: `scripts/lumos:41145`(`_lint_spawn`)
severity: minor
blocking: 否

總結:最嚴重是 F1(單一來源的過濾器列舉對非 UTF-8 名字失效,工作樹模式 `git status` 仍可執行任意指令)與 F2(鉤子層 `git status` 與 `impact --diff HEAD` 已實證可用同一手法執行任意碼),會擋 2 條。
