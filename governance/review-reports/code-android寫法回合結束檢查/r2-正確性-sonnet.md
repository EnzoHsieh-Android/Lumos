severity: major

先逐條核對上一輪正確性席 F1–F3,都已修好。

- **F1(白名單被佔位符繞過):已修好。**
  - 輸入:`--filter {LINT_FILES}`、`--filter={LINT_FILES}`、`--globs '{LINT_FILES}'`。
  - 實際:`_lint_wt_allow` 三條都回 `None`。
  - 預期:拒絕。
  - 我另外拿檔名 `/tmp/x/app/x$(touch${IFS}PWN2) sp'a"ce;`id`.kt` 走 `_lint_wt_argv` 加 `_lint_run_and_parse(argv=…)`。假 `ast-grep` 收到的最後一個參數逐字等於該檔名,沒有 `PWN2` 檔出現,也沒有 `lumos-lint-*.sarif` 殘留。
- **F2(檔名含空白崩潰):已修好。**
  - 輸入:`_lint_wt_blobs` 傳入 `sp ace.kt`、`d d/in side.kt`、`d d`(目錄)、`x missing`(HEAD 真有的檔)、`nothere missing`、`x\ny`。
  - 實際:`sp ace.kt` 為 None;`d d/in side.kt` 與 `x missing` 讀回內容;`d d`(樹)為 None;`nothere missing` 為 None;含換行的 `x\ny` 為 None。
  - 預期:同上。
- **F3(SARIF 暫存殘留):已修好。**
  - 輸入:`lint_new_worktree_sigterm`、`lint_new_worktree` 等 95 個測試。
  - 實際:全過。
  - 預期:全過。
  - 備註:`mkstemp` 到 `temps.add` 之間仍有極短空窗,收到 SIGTERM 會留一個 0 位元組檔,窗口微秒級,不標。

另外驗過,沒問題:
- `_lens_git` 加 `data` 後,既有呼叫端不傳 `data` 時走原路,行為沒變。
- `_lint_wt_git` 改用 `GIT_OPTIONAL_LOCKS=0` 後,`.git/index` 前後雜湊相同。
- 過濾器名字寫成 `[FILTER "evil"] CLEAN=…` 或 `filter.Evil.Name.clean`,都被列出並關掉。
- `_kt_decision_rows` 的字集合預篩與原本逐觸發字比對等價,`decision_rows` 27 個測試全過。

### F1 `git status` 仍會執行 repo 設定裡的 `core.fsmonitor`,過濾器防護只關了一半
這是補丁沒關到的同類洞,不是新引入的迴歸。補丁要擋的是「被打開專案的 `.git/config` 讓 `git status` 執行外部命令」,但只處理了 `filter.*`。
- 輸入:臨時 repo 設 `git config core.fsmonitor <腳本>`,腳本會 `touch` 一個記號檔;再呼叫 `_lint_wt_git(R, "status", "--porcelain=v1", "-z")`。
- 實際:`_lint_wt_filter_args` 正常回傳,status 照常成功,記號檔被造出,表示任意命令被執行。
- 預期:不執行。實測 `git -c core.fsmonitor=false status` 不造記號檔,所以多帶一個 `-c core.fsmonitor=false` 就能補。
- 影響:收工鉤子對開在惡意專案上的會談,照樣會被 `.git/config` 帶著跑命令。同一個 `_lint_wt_git` 是工作樹模式所有 git 呼叫的入口。
- 順帶:`check-graph-sync.py` 的同族呼叫點原本就有這個洞。

引句:「關掉 repo 設定裡的內容過濾器(_lint_wt_filter_args);回 CompletedProcess(位元組)或 None(含過濾器關不掉)。」
severity: major
blocking: 是

總結:最嚴重是工作樹模式的 git 呼叫關了內容過濾器卻沒關 `core.fsmonitor`,惡意專案的設定仍能讓 `git status` 執行任意命令,會擋 1 條;上一輪正確性席 F1–F3 已實測修好。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/lumos`(`_lint_wt_git`、`_lint_wt_filter_args`)
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/governance/review-reports/code-android寫法回合結束檢查/r2-repair-甲.patch`

我的臨時目錄已刪(`/tmp/lumos-seat-work/code-android寫法回合結束檢查/正確性-sonnet`)。
