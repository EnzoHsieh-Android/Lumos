severity: major

核對第三輪:F1(git 出錯 rc 128 被當刻意不查)已修好。`rev-parse` 現在只有回 1 才算沒有 HEAD,其餘回 `failed`。F2(SARIF 上限套到推送前閘)已修好。`wt = argv is not None or _LINT_WT_REG is not None` 把上限限在工作樹模式,推送前閘照舊整份解析。F3 的放行理由我認為成立。

過濾器那題(鏡頭 3)這輪改成不跑 `git status`,不再有名字寫法漏關的問題。ls-files、ls-tree、hash-object 對照 `git status` 的結果,我實跑了這幾種:大小不變內容改、改名、改名又改內容、`rm --cached`、`add -N`、已加入又刪除、檔名含空白、linked worktree。結果一致,只有下面列的差異。`_lens_git` 加 `data` 後,既有呼叫端不傳 `data`,行為沒變(鏡頭 4)。

## F1 `repo_root` 是 git 工作樹的子目錄時,乾淨的樹也被報成一堆改動
- 輸入:monorepo 內 `mono/app/` 當 `repo_root`,工作樹完全乾淨。
- 實際:`_wt_changed_nofilter` 回 `[('R',' ','A.kt','app/A.kt'), ('D',' ','other/B.kt',None), ('D',' ','root.kt',None)]`。鉤子的 `_git_status_entries` 回 `[('R ','A.kt'),('D ','other/B.kt'),('D ','root.kt')]`。
- 預期:`git status` 回空。
- 原因:`ls-tree --full-tree` 給的是從 repo 根算起的路徑,`ls-files -s` 和 `ls-files -o` 給的是從目前目錄算起的路徑,兩邊對不起來。
- 檔案改過、需要算雜湊時更糟。同一個 `mono/app`,改 `A.kt` 後 `hash-object --stdin-paths` 回 rc 128(`could not open 'A.kt'`),整個函式回 None。`hash-object --stdin-paths` 的路徑是從 repo 根算起,不是從 `-C` 的目錄。
- 影響:收工點名鉤子的 `payload.get("cwd")` 或 `CLAUDE_PROJECT_DIR` 若落在子目錄,乾淨的樹會被報成「改了程式碼」,觸發收工擋停。lint-new 的 `--repo` 若指向子目錄,同樣得到錯的改動清單。舊版 `git status --porcelain` 在子目錄乾淨時回空,這是這輪新引入的退步。
- 修法:用 `ls-files --full-name`、`ls-files -o --full-name` 統一成 repo 根相對路徑,`-C` 改指 `--show-toplevel`。要不然就在函式開頭偵測 `rev-parse --show-prefix` 非空時改走 toplevel。
引句:「raw = ok("ls-tree", "-r", "-z", "--full-tree", "HEAD", *lit) if h.returncode == 0 else b""」
severity: major
blocking: 是

## F2 檔名結尾是 CR 的檔案讓整輪「沒能檢查」
- 輸入:已追蹤的檔 `cr\r`,內容改過且大小不變。
- 實際:`hash-object --no-filters --stdin-paths` 收到 `cr\r\n`,把 `\r` 當行尾去掉,回 128(`could not open 'cr'`)。`ok(...)` 回 None,整個 `_wt_changed_nofilter` 回 None,判定成 `failed`。
- 預期:只有這一支被當「改過」(`M`),其他檔照查。
- 現有的防護只擋含換行和開頭是 `"` 的路徑。
- 影響:一支結尾帶 CR 的檔名,就讓該 repo 每回合的收工檢查都沒作用。屬於已列的「多查不漏查」方向以外的情況,後果是整個不查。
- 修法:守衛加上 `p.endswith(b"\r")`,走 `M` 分支。
引句:「elif b"\n" in p or p[:1] == b'"':」
severity: minor
blocking: 否

## F3 含換行的檔名讓收工點名鉤子的影響分析整個失敗
- 輸入:已追蹤、檔名含換行(`nl\nx.kt`)且改過的檔。
- 實際:`_nodehome_cat_sizes` 對含 `\n` 的 spec 回 None,`_impact_wt_nofilter` 回 None,`cmd_impact_diff` 印「擋下:git 算不出工作樹上的改動」並 rc 2。鉤子視為沒資料、放行。
- 預期:跟舊的 `git diff --name-only -z` 一樣能列出這支檔。舊路徑原本就是為了特殊檔名改成 NUL 分隔(「特殊檔名不能被引號化／拆行」)。
- 影響:這種檔名極罕見,但這輪是回歸;同一個 repo 只要有一支這樣的檔被改,整輪點名就沒了。
- 修法:把含 `\n` 的路徑從 specs 拿掉,走 `fallback`(只用路徑當查詢文字)。
引句:「sizes = _nodehome_cat_sizes(repo_root, specs, pre=_git_untrusted_c()) if specs else []」
severity: minor
blocking: 否

總結:最嚴重是 F1(`repo_root` 是 git 工作樹的子目錄時,乾淨的樹被報成改動,收工鉤子會誤擋),會擋 1 條。

臨時目錄已刪,未修改 repo。
