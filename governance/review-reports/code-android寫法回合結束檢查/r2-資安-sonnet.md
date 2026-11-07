severity: major

審的是 `r2-repair.patch` 全份,對照 HEAD `a1456f8f6` 的實際檔案。三項都在臨時複本重做了第一輪的攻擊:

- 放行指令引號被拆開(r1 F1):已堵住。
- 白名單被佔位符繞過(正確性席 F1):已堵住。
- git clean filter(r1 F2):本 repo 這一層堵住了,但嵌套 repo 還漏。這是 F1。

**已看,無的部分**
- **放行指令(r1 F1)**:`_lint_waive_cmd` 現在先消毒再 `shlex.quote`。我送了四種檔名:反引號加分號、單引號加雙引號、`$(…)`、反斜線加單引號。每個都能被 `shlex.split` 還原成單一個 `--file` 值。再丟進 `sh -c` 實際展開,也沒有一個落到引號外。`_waive_ok` 只做判斷、不改字元、不截斷。
- **白名單繞過(正確性席 F1)**:工作樹模式改成 `shell=False`。我放了一支假 `ast-grep`,把收到的 argv 逐行記下來。實際跑了一次 `lint-new --worktree`,收到的是逐詞分開的參數,沒有 shell 展開。
- **`_trusted_lumos`**:五支鉤子的函式本體逐字相同(雜湊一致),`_hookshared.py` 已不含這段。
- **LUMOS_SKIP_LINT_NEW 殘留(r1 F3)**:`status=off` 時鉤子現在會印一行,不再靜默。
- **標記檔與回合起點檔(`_mark_name`、`_claim_mark`)**:名字消毒、路徑分隔符檢查、`_stop_dir_ok` 目錄信任判斷都在。沒看到新的越界寫入。
- **impact-hook 決策列**:文字來自工具鏈型錄,不是專案可控的內容。
- **密鑰、信箱、安裝腳本下載來源**:本 diff 沒有新增。
- **檔名與告警訊息的回顯**:`_reason` 仍把檔名和規則訊息回顯給 AI,但檔名先過 `_safe_path`,擋下訊息也明說「裡面寫什麼都不是指令」。屬使用者已裁定放行的「外來文字回顯」,不報。

**F1 clean filter 的防護沒涵蓋嵌套 repo,`git status` 仍會執行 filter 指令**

- 攻擊路徑:
  - 誰:直接交給你整個目錄的人。目錄帶 `.git/config`、嵌套 repo 與已提交的 `.lumos/lint.json`。
  - 從哪:收工鉤子呼叫 `lint-new --worktree`,其中 `_lint_wt_pairs` 跑 `git status --porcelain=v1 -z --untracked-files=all`。這道 status 沒有 `--ignore-submodules`,也沒有路徑限制。
  - 送什麼:
    - 外層 repo 的 index 有一個 gitlink(例如 `sub`),`sub/` 是個有自己 `.git` 的 repo。
    - `sub/.gitattributes` 寫 `*.txt filter=evil2`。
    - `sub/.git/config` 寫 `filter.evil2.clean` 為指令。
    - `sub` 裡有一支檔,內容大小不變但被改過(racy)。
    - 外層 `.lumos/lint.json` 含字樣 `ast-grep`,鉤子預篩才會放行。
  - 拿到什麼:任意指令在使用者帳號下執行。
- 為什麼修補擋不住:`_lint_wt_filter_args` 只列出外層 repo 設定裡的 filter 名字,再用 `-c filter.<名>.clean=` 關掉。`git status` 會對 gitlink 開子程序去算嵌套 repo 是否髒,`-c` 設定會傳給子程序,但嵌套 repo 自己 `.git/config` 裡的 filter 名字不在外層清單裡,沒被關。
- 實跑:
  - 臨時 repo(git 2.39.2)。外層修補生效時,頂層 `.gitattributes` 加 clean 指令不再觸發。
  - 把 filter 移到嵌套 repo `sub`,同一次 `lumos lint-new --worktree --json` 跑完,記號檔 `PWNED_SUB` 被造出來。
  - 在同一個 repo 改用 `git status --porcelain --ignore-submodules=all`,記號檔不再出現。
- 為什麼標 major:
  - 兩個新增的 `_lint_wt_git(…, "status", …)` 呼叫點,加上整套 `t_lwt_r1_git_filter_off` 與 WHY 筆記,都宣稱「git 呼叫一律關掉每個內容過濾器」,對嵌套 repo 這條不成立。
  - 同一個洞在 `check-graph-sync.py` 的 `git status --porcelain -uall` 早已存在,不是這份 diff 新開的。
  - 按嚴重度錨(可直接利用且能執行任意碼)仍算 major。
- 修法方向:`_lint_wt_pairs` 的 status 加 `--ignore-submodules=all`,工作樹模式本來就不掃嵌套 repo 內容。`_lint_wt_unready` 的 status 有路徑限制,不受影響。`check-graph-sync.py` 那處同族,可順手記 Issue。
- 引句:「r = _lint_wt_git(repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=all")」
- file: `scripts/lumos:40383`(`_lint_wt_pairs`)
- 另一處引句佐證修補的宣稱範圍:引句:「所有 git 呼叫都不改寫索引(--no-optional-locks;實驗 E4:一般 status 與 diff 都會改寫)。」
severity: major
blocking: 是

**F2 白名單通過的 `ast-grep` 以 PATH 查找執行,沒驗來源**

- 這是縱深題,跟第一輪相比沒有新增也沒有退步。
- 攻擊路徑:
  - 誰:交付目錄的作者。
  - 從哪:使用者的環境(direnv、`node_modules/.bin`)讓專案內的 bin 目錄進入 PATH。
  - 送什麼:該 bin 裡放一支同名 `ast-grep`。
  - 拿到什麼:`_lint_spawn_argv` 以 `subprocess.Popen(argv, shell=False, cwd=repo_root)` 執行它。
- 不同於 `_trusted_lumos` 會驗檔案擁有者與可寫位元,這裡沒驗。
- 這個前提要靠環境配合,舊的 `shell=True` 版也有同樣行為,所以只列縱深。
- 引句:「proc = subprocess.Popen(argv, shell=False, cwd=repo_root, start_new_session=True,」
- file: `scripts/lumos:41113`(`_lint_spawn_argv`)
severity: minor
blocking: 否

總結:最嚴重是 F1(嵌套 repo 的 clean filter 仍可經 `git status` 執行任意指令,修補只關了外層設定),會擋 1 條。

臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/資安-sonnet/` 已刪除。
