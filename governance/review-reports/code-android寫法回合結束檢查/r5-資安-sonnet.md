severity: major

我先核對第四輪資安席 F1,再找新問題。第四輪 F1 在五支鉤子上都已修好。新發現一條同根因的洞:鉤子呼叫 `git` 時,同樣會從 PATH 的空項解到 repo 根的同名檔。實驗都在臨時複本做,完事已用字面路徑刪掉。

**核對第四輪 F1(`_trusted_lumos` 對 PATH 空項或 `.` 解成相對路徑):已修好**
- 我在 repo 根放了可執行的 `lumos`,對五支鉤子的 `_trusted_lumos()` 各跑四種 PATH:`:/usr/bin:/bin`、`/usr/bin:/bin:`、`.:/usr/bin:/bin`、`bin:/usr/bin`。
- 二十種組合都回到 `~/harness/lumos-toolchain/scripts/lumos`,沒有回傳相對路徑,repo 裡的 `lumos` 沒被執行。
- `_ok` 第一步用 `is_absolute()` 拒掉相對路徑,五份逐字複本都套上了。

**F1 鉤子用裸名 `git`,PATH 有空項或 `.` 時會執行 repo 根的 `git`**
- 攻擊路徑:
  - 誰:把整個目錄交給使用者的人。純 clone 帶不來設定,交付形式是整個目錄,這點與第四輪相同。
  - 從哪:使用者非刻意殘留的環境,例如 `PATH=$PATH:$X` 而 `$X` 為空,或 PATH 含 `.`。這是第三輪 F3、第四輪 F1 同一種環境。鉤子啟動時的工作目錄就是被打開的專案目錄。
  - 送什麼:repo 根放一支可執行、自己名下的 `git`,內容先做壞事,再 `exec /usr/bin/git "$@"`,所以鉤子看起來照常運作。
  - 拿到什麼:收工鉤子與 CI 狀態鉤子一觸發,就在使用者帳號下執行對方的程式。
- 實跑:
  - 條件:`PATH=":/usr/bin:/bin"`,工作目錄是放了 `git` 的 repo。
  - 直接跑 `subprocess.run(["git","-C",repo,"rev-parse","--show-toplevel"])`,標記檔被造出來。
  - 用相同環境餵 JSON 給 `ci-status-hook.py`、`stop-lint-hook.py`,兩支都造出標記檔。
- 為什麼這輪要報:
  - `_trusted_lumos` 只修了找 `lumos` 的這一條,而同一批鉤子呼叫 `git` 的地方沒有任何對應防護。
  - 受影響位置:`check-graph-sync.py:338` 的 `_git`、`_hookevent.py:149`、`ci-status-hook.py:30`、`lumos-entry-hook.py:22`、`impact-hook.py:802`、`bypass-ask-hook.py:643`。
  - 這些行不在 patch 的 +/- 行裡,是沿用既有程式。但重點提示問的正是「工具路徑解析還有沒有別的方式落到 repo 內的同名檔」,第四輪 F1 的後果也一模一樣。
  - 主程式的 `_lint_wt_resolve_tool` 已有同類修法,可借用。
- 修法方向:
  - 鉤子啟動時先把 PATH 清掉空項和相對項,或用絕對路徑解一次 `git`(`shutil.which` 之後拒相對路徑)。
  - 放在 `_hookshared` 一處;各鉤子是獨立檔,要走複本加漂移守衛那套。
- 引句:「if not p.is_absolute():」
- file: `scripts/hooks/claude/check-graph-sync.py:338`(`_git` 以裸名 `git` 啟動子程序;`_hookevent.py:149`、`ci-status-hook.py:30`、`lumos-entry-hook.py:22` 同樣)
severity: major
blocking: 是

**其他已看,無**
- `_wt_changed_nofilter` 加 `-C <根>`、`--full-name`:
  - `ls-files`、`ls-tree`、`hash-object --no-filters --stdin-paths`、`rev-parse` 都不跑內容過濾器。
  - 新增的路徑也只用 lstat 和 `--no-filters`,沒有回到 `git status` 或 `git diff` 的路徑。
  - 結尾 CR 和換行的檔名一律當改過,不再送進 `--stdin-paths`。
- `_impact_line_delta`、`_impact_hunk_query`、`_impact_mode_entry`、`_impact_wants_head`:
  - 都是純位元組處理,不碰 git。
  - 讀檔用 `open(top / p, "rb")`,有 `S_ISREG` 判斷和 `cap` 上限。
  - 工作樹中間目錄被換成符號連結時,讀到的外部內容只進查詢文字(事故比對和排名用),沒有回顯路徑。我找不到完整的外洩路徑,不算 finding。
- `_lint_wt_toplevel`:走 `_lint_wt_git`,帶不信任 repo 的 `-c` 參數,失敗就退回原值。
- 兩份危險設定清單只改了註解和移除未用參數,守衛改雙向,沒有新的執行面。
- 提示注入、密鑰與信箱:這份 patch 沒有新增自由文字進派工詞的路徑,也沒有新增密鑰。

總結:最嚴重是 F1(鉤子裸名呼叫 `git`,PATH 有空項時會執行 repo 根的同名檔,實跑確認),會擋 1 條。第四輪 F1 已確實修好。
