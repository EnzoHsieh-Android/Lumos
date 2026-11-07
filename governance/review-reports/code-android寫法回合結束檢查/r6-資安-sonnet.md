severity: major

第五輪 F1 這輪確實修好了,但同一個洞還留在另外三支 shell 掛鉤。實驗都在臨時複本做,做完已用字面路徑刪掉。

**核對第五輪 F1(鉤子裸名 `git`,PATH 空項會執行 repo 根的 `git`):`_clean_path_env` 已修好**
- 我在 victim repo 根放了十幾支假的可執行檔(`git`、`python3`、`ast-grep`、`lumos`、`env`、`sh` 等,被呼叫就寫 canary)。
- 八支 Python 鉤子、五種事件的 payload,以 `PATH=":/usr/bin:/bin"` 啟動:canary 零命中。
- 對照組:把 `_clean_path_env()` 那句換成 `pass` 的複本,`git` canary 命中(`rev-parse --show-toplevel`),證明實驗本身有效。
- 主程式用 `PATH` 取 `:/usr/bin:/bin`、`.`、`bin:/usr/bin`、空字串、`/usr/bin::/bin` 五種,各跑 `--help`、`doctor`、`impact --worktree-nofilter`、`lint-new --worktree`、`ci-status`、`enforcement`、`pitfalls`:零命中。
- 模組層沒有在 `_clean_path_env` 之前開子程序。

**F1 三支 shell 掛鉤(pre-push、pre-commit、post-commit)找 python 用 `command -v`,PATH 有空項時執行 repo 根的 `python3.14`、`bash`**
- 攻擊路徑:
  - 誰:把整個目錄交給使用者的人。
  - 從哪:使用者或照常操作的 AI 在該 repo 跑 `git push`、`git commit`。環境有非刻意殘留的 PATH 空項(`PATH=$PATH:$X`、`$X` 為空),這跟第三、四、五輪的前提相同。
  - 送什麼:repo 根放一支可執行的 `python3.14`(untracked 即可)。
  - 拿到什麼:掛鉤以使用者身分執行對方的程式。
- 實跑:
  - `PATH=":/usr/bin:/bin"`,工作目錄是 repo 根,放假的 `python3.14`。
  - 直接跑 `pre-push`:canary 被寫入,命令是 `.../r4/./python3.14 .../scripts/lumos python-path`,也就是 `command -v` 回了相對的 `./python3.14` 並被執行。
  - 再放假的 `bash`:掛鉤第一行 `#!/usr/bin/env bash` 讓 `env` 依 PATH 空項解到 `./bash`,canary 寫入 `./bash ./.pp-exec`,連 python 都還沒找就被執行。
- 為什麼這輪要報:
  - 這三支檔不在這份 patch 的 +/- 行裡,是沿用既有程式。
  - 但 patch 的紀錄和筆記宣稱「入口洗一次,整個程序吃乾淨的 PATH」,只涵蓋 Python 的九個入口。同一根因(PATH 空項等於目前目錄)在 shell 這三個入口沒洗。
  - 這是第四次同類被打穿。
  - 依「同類兩輪換形狀」,應該由 shell 入口也做同一件事,而不是再補 `python3.14`。
- 修法方向:
  - 三支掛鉤開頭先把 `PATH` 濾成只剩絕對項,空了就退回固定的 `/usr/bin:/bin`。
  - `#!/usr/bin/env bash` 在它執行之前就已被解析,要改成 `#!/bin/bash` 之類的絕對路徑。
  - `_LUMOS_ANY_EXE` 取到後再拒絕相對值,當第二層。
- 引句:「+# ★下面這支是主程式 scripts/lumos 同名函式的逐字複本★(安全邏輯,照 [[Systems/hook信任邊界]];守衛 t_r5path_hooks_verbatim)」
- file: `scripts/hooks/pre-push:234`、`scripts/hooks/pre-commit:84`、`scripts/hooks/post-commit:129`(`command -v "$_c"` 加 `_LUMOS_ANY_EXE="$(command -v "$_c")"`)
severity: major
blocking: 是

**F2 `ls-files -v` 之後,標了 assume-unchanged 或 skip-worktree 的檔被改,收工檢查與收工點名完全看不到**
- 攻擊路徑:
  - 誰:使用者本人,為了本機設定檔標過 `git update-index --assume-unchanged`,或用了 sparse-checkout。
  - 從哪:AI 照常編輯該檔。
  - 送什麼:該檔的內容改動。
  - 拿到什麼:收工寫法檢查、收工點名這道守衛不會點名它。
- 實跑:標 `h`(assume-unchanged)的 `A.kt` 與標 `S` 的 `C.kt` 都被追加了 `evil`,`_wt_changed_nofilter` 只回報沒標旗標的兩支。
- 這跟 `git status` 一致,是設計決定。但計劃天花板第 4 條寫「方向都是多查不漏查」,這個改動讓那句對這兩類檔不再成立。
- 沒有直接攻擊路徑,只是少一層守衛,所以只算縱深。建議在天花板補一句。
- 引句:「+            if tag == b"S" or tag.islower():」
severity: minor
blocking: 否

**已看,無**
- `_wt_changed_nofilter` 兩份逐字複本與新加的 `-v`:在 `.git/config` 設好 `filter.x.clean`、`filter.x.process`、`core.fsmonitor`、`diff.x.textconv`、`diff.external`、`core.pager`、`core.attributesFile`、`.gitattributes` 指到 canary,把檔案改成同大小內容:函式路徑零命中。檔名含空白、換行都解析正確,沒有退回 `git diff`。
- `--worktree-nofilter`:沒找到其他路徑能讓鉤子或影響分析回到 `git diff` 或 `git status`。
- `_repo_top` 走鉤子的 `_git`,有帶 `core.fsmonitor=` 和 `diff.external=`;`_git_toplevel` 走 `_lint_wt_git`,帶固定三項。
- `_trusted_lumos` 與 `_lint_wt_resolve_tool` 的相對路徑拒絕仍在。
- 提示注入:查詢文字只進事故比對與排名,沒有新的自由文字進派工詞。
- 密鑰與信箱:無新增。
- 補一個我沒深究的點:`_wt_changed_nofilter` 的 `top` 取自 `rev-parse --show-toplevel`,而 `core.worktree` 可由對方的 `.git/config` 指到別處。這是沿用既有的行為,輸出只進提醒文字,沒有寫入面,我沒有往下做。

總結:最嚴重是 F1(三支 shell 掛鉤的 PATH 空項會執行 repo 根的 `python3.14`、`bash`,實跑確認),會擋 1 條。第五輪 F1 在九個 Python 入口已確實修好。
