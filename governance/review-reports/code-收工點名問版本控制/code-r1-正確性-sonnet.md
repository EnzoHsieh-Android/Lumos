severity: major

## Finding 1 — 擋停訊息取交集後,對「用 shell 改的檔」永遠列不出檔名(正是這次改動的主要目標場景)
severity: major
blocking: 是 — 送給模型的 block reason 在這批改動最主要的目標場景(echo/sed/heredoc 改碼)下,實測必定走進「這一輪動到的檔算不出來,所以不列檔名」的泛用訊息,模型看不到任何具體檔名。
`model_rel` 是 `rel`(git status 算出的清單)與 `turn_rel`(僅來自逐字稿裡 Edit/Write/MultiEdit 或 rm/mv/cp 命令)的交集;`echo >`、`sed -i`、heredoc 這些新支援的改法從未被寫進 `file_paths`,所以 `turn_rel` 永遠不含它們,`model_rel` 在這個場景下必定是空集合、落入 fallback 訊息,而 stderr 那份雖有完整檔名但檔案自己註明「模型看不到」。已用真實 hook 端到端重現:同一支 `scripts/foo.py` 被 Bash `echo >>` 改動時回傳「…這一輪動到的檔算不出來,所以不列檔名。」,改用 Edit 工具改同一支檔時 reason 正確列出 `` `src/foo.py` ``。新增的 7 支測試全部透過共用的 `_run_stop` 呼叫 hook,而它固定帶 `LUMOS_STOP_BLOCK_OFF=1`,等於這條 JSON block-reason 路徑在新測試裡從未被執行到一次。
引句:「model_rel = [r for r in rel if r in turn_rel]」
引句:「這一輪動到的檔算不出來,所以不列檔名」
引句:「env = {**_os.environ, "LUMOS_STOP_BLOCK_OFF": "1"}」
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch:377` — `model_rel` 交集邏輯
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch:379` — 空交集時的 fallback 訊息
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch:1083` — 新測試共用的 `_run_stop` helper,固定關閉擋停
file: `/tmp/stopfix_review/proj1`(臨時 repo,已重現) — payload 用 Bash `echo >>` 的逐字稿跑 hook,stdout 得到 `{"decision": "block", "reason": "LUMOS-STOP:...\n工作樹上有 1 個程式碼檔還沒提交、筆記沒跟著動;這一輪動到的檔算不出來,所以不列檔名。"}`;同一支檔改用 Edit 工具的逐字稿時 reason 正確含 `` `src/foo.py` ``。

## Finding 2 — 非 ASCII(中文)檔名被 git 轉義成八進位跳脫字串,解析後指向不存在的路徑
severity: major
blocking: 是 — 解析出來的相對路徑不是真檔名,`project_root / relpath` 對不上磁碟上的檔案,提醒訊息與後續 `find_notes_mentioning`/`_impact_missing` 都會拿到亂碼路徑。
`_git_status_entries` 呼叫 `git status --porcelain -uall` 時沒有帶 `-c core.quotePath=false`;git 預設會把非 ASCII 檔名跳脫成 `"\346\226\207..."` 這種八進位字串並加雙引號。程式碼只 `.strip().strip('"')` 去掉引號,沒有反跳脫,所以中文/日文等檔名被解析成一串反斜線八進位文字,而不是原始檔名。已直接跑這支 patch 裡的解析邏輯(未經任何後續修正)對真實 repo 的中文檔名 `src/文件.py`,得到 `rest = '\\346\\226\\207\\344\\273\\266.py'` 而不是 `'src/文件.py'`。
引句:「r = subprocess.run(["git", "-C", str(project_root), "status", "--porcelain", "-uall"],」
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch:73` — 缺 `-c core.quotePath=false`
file: `/tmp/stopfix_review/parse_test.py`(對照真 repo 執行結果) — `git -C repo1 status --porcelain -uall` 對 `文件.py` 回 `?? "\346\226\207\344\273\266.py"\`,套用這支 patch 的 parsing 邏輯後 `rest` 仍是逐字的八進位跳脫字串,不是 `文件.py`。
file: `scripts/hooks/claude/check-graph-sync.py:326`(目前工作樹版本,晚於這份被審的 r1-code.patch) — 已補上 `-c core.quotePath=false`,註解寫「代碼審 r1 外家備援 blocker」,代表這個問題已在別的審查通道被抓到並修掉;但被凍結審查的 r1-code.patch 本身沒有這行,故如實列出。

## Finding 3 — 改名列若新舊檔名都含字面 " -> ",naive split 取到錯的新路徑
severity: minor
blocking: 否 — 需要同一次改名的新舊檔名都恰好包含字面 `" -> "` 子字串才會觸發,現實工作流極端罕見,且失敗結果只是「路徑對不上導致該筆漏報/位置報錯」而非崩潰或誤放行更危險的東西。
`if "R" in code or "C" in code: rest = rest.split(" -> ")[-1]` 對整段「舊路徑 -> 新路徑」做無條件 split,若新舊檔名各自也含 `" -> "`,`split(" -> ")[-1]` 只會拿到新檔名最後一段。已實測 `git mv "weird -> name.py" "renamed -> also.py"` 後,這段邏輯算出 `rest == 'also.py'`,不是正確的 `'renamed -> also.py'`。
引句:「rest = rest.split(" -> ")[-1]」
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch:85` — rename 解析
file: `/tmp/stopfix_review/parse_test2.py`(真 repo 執行結果) — `git status --porcelain -uall` 回 `R  "weird -> name.py" -> "renamed -> also.py"`,套用該行邏輯得到 `rest = 'also.py'`。

## Finding 4 — 新增又刪除、從未進過任何一次提交的無副檔名 shebang 檔,靜默偵測不到
severity: minor
blocking: 否 — 屬既有限制的延伸(舊版對「已刪除、磁碟上也不存在」的無副檔名檔一樣偵測不到,因為 `_shebang_script` 先問檔案存不存在),`_head_shebang` 只補上了「曾經提交過、之後被刪」這個子情境,「新增又刪除、從未提交」仍是舊坑,不是這次改動新引入的回歸,場景也偏窄(同一輪內建立又丟棄一支無副檔名腳本、且從未 commit)。
`_entry_is_code` 對狀態含 `D` 且無副檔名的項目改叫 `_head_shebang`,而它讀 `git show HEAD:<path>`;若該檔從未出現在任何一次提交裡(例如先 `git add` 再刪除,或全新空倉庫),`git show` 回非 0,函式回 `False`,於是這支檔完全不進清單、不觸發任何提醒。已在既有提交的 repo 與全新空 repo 兩種情況下各自重現:`git add` 一支 `newscript`(shebang、無副檔名)後 `rm` 掉,`git status --porcelain -uall` 顯示 `AD src/newscript`,hook 端到端跑完後完全不印任何東西、也不回 JSON block。
引句:「檔案刪掉之後永遠回 False——而本 repo 主程式正是沒有副檔名、只能靠首行認出來的檔」
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch:95` — `_head_shebang` 設計說明
file: `/tmp/stopfix_review/proj1`、`/tmp/stopfix_review/proj_empty`(已重現) — `git add newscript && rm newscript` 後 `git status --porcelain -uall` 顯示 `AD ...newscript`;跑 hook(payload 的 Bash 動作是 `rm src/newscript`)後 rc=0、stdout/stderr 完全無輸出。

## Finding 5 — 安全檢查從比對寫死目錄名改成比對 `d.name`,查證後未放寬(僅為澄清此檢核項)
severity: minor
blocking: 否 — 兩個實際呼叫點(`_stop_block_dir`/`_printed_dir`)傳進 `_cache_dir_under_home` 的 `name` 都是檔案內寫死的字面值(`"stop-block"`、`"stop-printed"`),`d.name` 不是任何外部輸入,所以「比對自己的名字」在目前用法下跟「比對寫死字串」等價,沒有新增可被利用的繞路面。
`_stop_dir_ok` 原本硬寫 `"stop-block"`,若同一層底下新增別的目錄名(例如這次新加的 `stop-printed`)就永遠比對不過,是這次改動要解決的真問題(不是我在找的 bug);改法本身經查證沒有放寬安全性,因為呼叫端沒有把外部可控字串傳進 `d.name`。
引句:「if d.resolve() != (Path.home().resolve() / ".cache" / "lumos" / d.name):」
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch:260` — 改動後的比對式
file: `governance/review-reports/code-收工點名問版本控制/r1-code.patch` 全文 grep `_cache_dir_under_home(` 僅兩處呼叫,`name` 參數皆為字面字串 `"stop-block"` / `"stop-printed"`

## 實務隱患鏡頭
- 併發:「無」(有 fail-open 設計)——多個 session 共用同一 worktree 時,`git status` 可能撞上另一 session 正在寫 index(commit/add)導致的鎖,但 `_git_status_entries` 對非 0 return code 一律回 `None`,呼叫端 `entries is None: return 0` 靜默放行,不會誤判或崩潰,只是那次 Stop 少提醒一次(設計本身承認的取捨)。
- 效能:「有,但是刻意取捨」——閘門 2/3 從純記憶體運算(比對逐字稿路徑)變成每次 Stop 都無條件跑一次 `git status --porcelain -uall`;`-uall` 刻意不摺疊未追蹤目錄,在 untracked 檔案多的 repo(這次對話開頭的 `git status` 本身就列出數十筆 `governance/rel-cascade/*.jsonl` 等未追蹤檔)會比摺疊模式慢,且是每一輪 Stop 都要付的成本,不是一次性的。
- 資源:「有,較次要」——`_head_shebang` 對每一個「無副檔名且被刪除」的項目用 `capture_output=True` 讀整份 `git show HEAD:<path>` 到記憶體,沒有大小上限(如 `head -c` 之類的截斷),若被刪的是一支很大的無副檔名二進位檔,單次讀取成本會偏高,但觸發條件窄(無副檔名+刪除),影響有限。
- 失敗路徑:「已檢查,無新增問題」——`_git_status_entries`/`_head_shebang` 都用 try/except 包住,任何非 0 或例外都 fail-open(回 `None`/`False`),跟檔案其他既有查詢的慣例一致。

## 總結
最嚴重等級:major;blocking 共 2 條(Finding 1、Finding 2)。
