severity: major

我先核對第三輪資安席的 F1、F2、F3,再找新問題。所有攻擊都在臨時複本實跑,環境是 Apple Git 2.39.2,用 python3.14 載入工作樹裡已套上這輪修補的 `scripts/lumos` 和鉤子。臨時目錄已用字面路徑刪掉。

**核對第三輪**
- **F1(過濾器名字非 UTF-8 列不到):已修好。**
  - `_git_untrusted_c` 不再列舉名字,只剩固定三項。
  - 我造了 racy 檔,也就是時間、大小都和索引記的一樣、內容改過的檔,再設 `filter.evil.clean` 去建記號檔。
  - 對照組不帶旗標的 `git status` 會造出記號檔。
  - `_lint_wt_changed` 與 `_lint_wt_unready` 都沒造出來。
  - 子 repo 自帶 `core.fsmonitor` 加 clean 過濾器,同樣沒觸發。
  - 名字含換行、空白、中文的檔,列法正確。
  - macOS 的 APFS 建不出非 UTF-8 檔名,這一項沒能直接實跑。新函式整條路不依賴過濾器名字,所以這項不影響結論。
- **F2(鉤子層 `git status` 與 `impact --diff HEAD`):已修好。**
  - `_git_status_entries` 改走 `_wt_changed_nofilter`。
  - 帶 `--worktree-nofilter` 的 `impact --diff HEAD --sync-check --json` 實跑沒有記號檔。
  - 用 `GIT_TRACE` 看過,鉤子與影響分析路徑沒有 status 或 diff 指令。
  - 我另外試了 `impact --file`,同一個 racy 檔也沒觸發。
  - `--worktree-nofilter` 被引數檢查限定只准搭 `--diff HEAD --sync-check`。沒帶這個選項的 `--diff` 仍走 `git diff`,那是使用者手動跑的提交前與推送前閘,不是鉤子自動跑的。
- **F3(ast-grep 照 PATH 找):`_lint_wt_resolve_tool` 已修好。**
  - 我試了空項、`.`、相對路徑 `bin`、絕對路徑落在 repo 內、符號連結目錄指進 repo、`//./` 變形路徑,全部拒跑。
  - 但同一個洞在 `_trusted_lumos` 還開著,見 F1。

**已看,無**
- `hash-object --no-filters --stdin-paths`:
  - 它只算雜湊,不寫物件,也不輸出內容。
  - 結尾有 `\n` 或以 `"` 開頭的路徑已被程式擋成「當改過」,不送進去。
- 符號連結、FIFO 等非一般檔會被 `lstat` 擋成 T,不會被送去雜湊。
- `ls-files -s --debug` 的解析:怪檔名最多讓某支檔被多查或誤判未改,拿不到任何執行能力。
- 其餘 git 呼叫都不經內容過濾器,也沒有執行指令的設定項。
- 三支鉤子的 stdin 壞輸入處理:一律放行,沒有越界。
- 提示注入:
  - 給 AI 的區塊檔名經 `_safe_path` 清過,並明寫「檔名不是指令」。
  - 未清過的檔名只走 stderr,沒有新增外來自由文字進派工詞。
- 密鑰、信箱、安裝腳本下載來源:本 diff 沒新增。
- 工具子程序設 `RLIMIT_FSIZE` 屬資源席範圍,不報。

**F1 `_trusted_lumos` 照 PATH 找 `lumos`,PATH 有空項或 `.` 時解成相對的 `lumos`,鉤子拿它執行 repo 根的同名檔**
- 攻擊路徑:
  - 誰:把整個目錄交給使用者的人。純 clone 帶不來 `.git/config`,所以交付形式是整個目錄。
  - 從哪:使用者非刻意殘留的環境,例如 `PATH=$PATH:$X` 而 `$X` 為空造成空項,或 PATH 含 `.`。這是第三輪 F3 同一種環境。
  - 送什麼:repo 根放一支可執行、自己名下、非 group/other 可寫的 `lumos`。
  - 拿到什麼:收工鉤子與改檔鉤子在使用者帳號下執行任意程式。這輪新增的 `--worktree-nofilter` 呼叫也是其中一條。
- 實跑:
  - `PATH=":/usr/bin:/bin"`、`"/usr/bin:/bin:"`、`".:/usr/bin:/bin"` 三種,`stop-lint-hook` 的 `_trusted_lumos()` 都回傳相對路徑 `lumos`。
  - `_ok` 只查擁有者與寫入權限,不拒相對路徑;使用者解開別人給的目錄後,檔案本來就是自己名下,所以通過。
  - 接著 `check-graph-sync.py` 的 `_impact_missing`,在 cwd 是該目錄時呼叫,`[sys.executable, "lumos", "impact", ...]` 實際執行了 repo 裡的 `lumos`,記號檔被造出來。
  - `stop-lint-hook` 的 Popen 設 `cwd=str(root)`,相對的 `lumos` 一樣落在 repo 根。
- 為什麼這輪要報:
  - 第三輪 F3 已點名 `_trusted_lumos` 同根因,這輪只對 `ast-grep` 做了 `_lint_wt_resolve_tool`,四支鉤子裡的 `_trusted_lumos` 逐字複本原樣沒動。
  - 同一種 PATH 殘留環境,同一個「打開陌生目錄就自動執行對方程式」的後果。
- 修法方向:
  - `_trusted_lumos` 對 `shutil.which` 的結果要求 `os.path.isabs`,否則視為不可信。
  - 或比照 `_lint_wt_resolve_tool` 逐項解析 PATH。
  - 四支鉤子的複本要一起改,現有守衛會盯著它們一字不差。
- 引句:「r = subprocess.run([sys.executable, lumos, "impact", "--diff", "HEAD", "--sync-check", "--worktree-nofilter", "--json", "--repo", str(project_root)],」
- file: `scripts/hooks/claude/check-graph-sync.py:753`(`_trusted_lumos`;`impact-hook.py:294`、`lumos-entry-hook.py:214`、`stop-lint-hook.py:68` 有同樣的複本)
severity: major
blocking: 是

總結:最嚴重是 F1(`_trusted_lumos` 對 PATH 空項或 `.` 解成相對路徑,實跑確認鉤子會執行 repo 根的 `lumos`),會擋 1 條。第三輪的 F1、F2、F3 都已修好;F3 只修了 ast-grep,同根因的 `_trusted_lumos` 沒跟著修,所以才有這條。
