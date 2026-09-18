severity: blocker

## 前置驗證:作者宣稱的防護對它自己說的目標確實有效

實際重現:造一個惡意倉庫,在 `.git/config` 設 `core.fsmonitor = "sh -c 'touch /tmp/PWNED1' #"`,直接跑 `git status --porcelain -uall` 會執行攻擊者指令(已用 `ls -la /tmp/PWNED1` 確認檔案被建出來)。接著端到端跑真的 `check-graph-sync.py`(不改任何碼),`CLAUDE_PROJECT_DIR` 指向惡意倉庫、逐字稿帶一個 Bash 工具呼叫、工作樹同時有未提交的程式碼檔與圖譜筆記(觸發閘門 2+3、進而叫到 `_impact_missing()` → `lumos impact --diff HEAD --sync-check --json --repo <惡意倉庫>`):`/tmp/PWNED1` 沒有被建出來。也用一份拿掉 `_harden_git_env()` 呼叫的複本(只放在 /tmp,沒改 repo)重放同一情境,`/tmp/PWNED1` 會被建出來——證明測法真的有打到那條路,而正式碼確實擋住了 `core.fsmonitor` 這個已知洞。

## finding 1:防護只關 core.fsmonitor,同一條被自己標成「已涵蓋」的第三處呼叫路徑其實還能被 diff.external 打穿——完整 RCE

severity: blocker
blocking: 是

`_harden_git_env()` 的 docstring 自己講,閘門 3 呼叫主程式那條「之前」漏補、這次已經補齊:

引句:「★r1 的修法只補了自己新增的兩個呼叫點,漏了第三處★:閘門 3 那條會去呼叫主程式」

引句:「★子行程一律繼承★,所以主程式內部的呼叫也涵蓋得到(實測驗過)」

這個宣稱是錯的:它只驗過 `core.fsmonitor` 這一項,`scripts/lumos` 內部那條路(`cmd_impact_diff`,不在本次 diff 改動範圍,但正是「閘門 3 呼叫主程式」講的那條)有一處 **完全沒被這個環境變數保護**——`file: \`scripts/lumos:25261-25262\`` 的 `d = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false", "diff", diff_range, "--", f], ...)` 是逐檔跑的**純 `git diff`**(沒有 `--numstat`、沒有 `--no-ext-diff`、也沒有帶 `-c diff.external=`),會吃倉庫自己 `.git/config` 裡的 `diff.external` 設定。

實測重現(全程用真正、未修改的 `scripts/hooks/claude/check-graph-sync.py`,不是改過的複本):
1. 造惡意倉庫 `/tmp/victim3`,有 `docs/x-knowledge/Systems/s.md`(圖譜)與 `scripts/keep.py`(程式碼),先 commit 一版。
2. `git config diff.external "sh -c 'touch /tmp/DIFFEXT_PWNED3' #"`。
3. 兩個檔都改成未提交(`scripts/keep.py` 改內容、`docs/.../s.md` 改內容),模擬「這一輪動了程式碼、也動了筆記,但用 shell 改的」。
4. 組一份最小逐字稿(一個 user 訊息 + 一個 Bash tool_use)當 payload,`CLAUDE_PROJECT_DIR=/tmp/victim3`、`LUMOS_STOP_BLOCK_OFF=1` 直接跑 `python3 scripts/hooks/claude/check-graph-sync.py < payload`。
5. 結果:`/tmp/DIFFEXT_PWNED3` 被建出來,rc=0,hook 完全沒印任何錯誤或警告。
6. 對照組:`git config --unset diff.external` 後重跑同一份 payload,同一個惡意倉庫,檔案沒被建出來——確認觸發點就是 `diff.external`,不是別的雜訊。

這條路徑跟「r1/r2 已補的兩處」走的是同一種自動觸發面:使用者只要打開這個惡意資料夾、讓 Claude/Codex 做一輪任何動作(哪怕只是 `echo hi`),Stop hook 就自動跑到這裡——不需要使用者主動執行任何指令。誰:任何打開這個資料夾的人;從哪:資料夾自帶的 `.git/config` 的 `diff.external`;送什麼:任意 shell 指令;拿到什麼:以該使用者權限在其機器上執行(本示範用 `touch`,實務上可以是任何指令)。

## finding 2:GIT_CONFIG_PARAMETERS 已存在同名變數時的疊加順序——驗證是安全的(非 blocker,附驗證記錄)

severity: minor
blocking: 否

引句:「os.environ["GIT_CONFIG_PARAMETERS"] = (cur + " " + want).strip()」

這把自己的 disable 項接在既有值後面。實測 GIT_CONFIG_PARAMETERS 對同一個 key 的多筆設定是**後面蓋前面**(跟多個 `-c` flag同一套語意):用同一個乾淨倉庫分別測 `"'core.fsmonitor=touch /tmp/EARLY_MARK' 'core.fsmonitor='"`(惡意值在前、disable 在後)與反過來的順序,前者 EARLY_MARK 沒被建出來、後者 LATE_MARK 被建出來。這代表 `_harden_git_env()` 目前「附加在後面」的順序剛好是安全的方向——如果環境裡已經有人(或某個上游殼層)塞了一個惡意的 `core.fsmonitor`,程式碼的 disable 值仍會贏。標 minor 是因為這條在本威脅模型下沒有找到攻擊者能真的把值塞進 `GIT_CONFIG_PARAMETERS` 的路徑(它不是靠讀取被打開資料夾的檔案內容,而是這支 hook 進場時所在的 process 環境),純粹留一筆驗證記錄。

## 第 3 點:實際試過的其他設定項

- **alias**(別名):`git config alias.status '!touch /tmp/ALIAS_PWNED'` 後跑 `git status`——不觸發。git 的內建 porcelain 子命令(`status`/`diff`/`show`/`log` 這些)不能被同名 alias 覆蓋,實測確認。
- **diff.external**(跟外部程式有關):**觸發**,見 finding 1。經 `cmd_impact_diff()` 逐檔跑的純 `git diff` 命中;同函式裡另一個 `git diff --name-only HEAD`(取檔名清單那次)實測**不觸發**——`--name-only` 不會叫外部 diff 程式,只有拿內容那次的純 `git diff` 會。
- **core.pager**(分頁器):`git config core.pager "sh -c 'touch /tmp/PAGER_PWNED' #"` 後分別跑 `status --porcelain -uall`、`log`、`diff HEAD`(用 `subprocess`,stdout 非 tty)——都**不觸發**。git 判斷輸出不是終端機時不會叫 pager。
- **filter.<driver>.smudge**(替代路徑/內容還原程式):設 `.gitattributes` 讓 `a.py` 走 `filter=pwn`、`filter.pwn.smudge` 設成攻擊指令,分別測 `git show HEAD:a.py`(`_head_shebang` 用的那個呼叫)與 `git status --porcelain -uall`——都**不觸發**。smudge/clean 沒有被這兩個呼叫用到的路徑喚起。

## 總結

最嚴重等級:blocker。blocking 共 1 條(finding 1)。finding 2 為 minor、非阻塞,只是驗證記錄。
