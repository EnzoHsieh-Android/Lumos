severity: major

審查範圍:只審 r2-snapshot.md。逐節讀完,spec 引用的函式、常數、檔名、指令旗標都已對照 `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-check` 查證。查證不到的明寫在對應 finding 裡。

### F1 回合時間戳在續做那一輪被推進,範圍 3 的結論與〈天花板〉1 互相矛盾
severity: major
blocking: 是——實作者照範圍 3 的結論做,會做出「續做改的檔永遠沒人查」的系統,而且以為有查。
段落:範圍 3 最後一條「回合時間戳」,對照〈天花板〉1。
問題:
- 範圍 3 寫「這道一開始(任何提早離開之前,含 `stop_hook_active` 那一次)先讀出上一個時間戳,接著立刻寫入這一次的時刻」,並下結論「所以續做那一輪改的檔,下一次收工會被查」。
- 時序是這樣:第 N 次收工寫入 T_N 並擋下。模型續做改檔,檔案修改時間在 T_N 之後。第 N+1 次收工(帶 `stop_hook_active`)讀 T_N、不檢查、寫入 T_{N+1},而 T_{N+1} 晚於續做改的檔。下一個使用者回合收工時,「上一個時間戳」是 T_{N+1},續做改的檔修改時間早於它,不算「這一回合碰過」。
- 結論實際上是反的。〈天花板〉1 也寫「續做那輪新加的告警,等代碼審通過前或推送前閘」,與範圍 3 那句直接矛盾。
- 修好的檔、以及續做時新加的告警,永遠不會被這道查。「模型修完還要被再查一次」的預期落空。
引句:「所以續做那一輪改的檔,下一次收工會被查」
佐證:
- file: `scripts/hooks/claude/check-graph-sync.py:1008-1114` 現行主流程沒有任何回合時間戳。
- S4 沒有任何條款釘住「續做那輪改的檔下次被查」,所以這句矛盾不會被測試抓到。

### F2 lint 名額先佔、輸出延到「最後」,既有那道的 7 條提早返回與逾時會讓擋停永久遺失
severity: major
blocking: 是——實作者會做出「佔了名額、卻沒輸出擋停」的狀態,同一批告警之後再也不會被擋。
段落:範圍 3 的「防無限擋」與「兩道都要擋時」兩條。
問題:
- 範圍 68 要求「先佔名額再輸出」。範圍 69 要求兩道各自佔名額,「最後只輸出一則」。
- 既有 `main()` 在 lint 判完之後還有多處不輸出的 `return 0`:`graph_touched` 分支(動過筆記)、同批已講過、`entries is None`、沒有 code_entries 等。
- 另外兩條路也會讓 lint 名額落空:既有那道可能丟例外;外層 55 秒時限也可能把整支砍掉。既有那道實測需要 25 秒,transcript 還整份讀進記憶體。
- spec 沒規定這些路徑必須先把 lint 的待輸出理由吐出去。名額一旦用掉,同名檔存在就等於「同一批已擋過」,該批永久不再擋。
- 範圍 63 又要求「動過筆記」「沒有圖譜」仍要跑寫法檢查,所以 `graph_touched` 這條路就是 spec 自己指定要擋的路徑。
引句:「兩道都要擋時:各自先判、各自佔名額,最後只輸出一則 `decision: block`,原因是兩段接起來」
佐證:
- file: `scripts/hooks/claude/check-graph-sync.py:1001` `return 0` 是沒有圖譜的專案。
- file: `scripts/hooks/claude/check-graph-sync.py:1038` `return 0` 是動過筆記的分支,只印 stderr。
- file: `scripts/hooks/claude/check-graph-sync.py:1055` `return 0` 是同批已講過。
- file: `scripts/hooks/claude/check-graph-sync.py:1108` 既有的輸出點是 `stop_block_decision` 之後的 `sys.stdout.buffer.write`,既有的佔名額與輸出同步,沒有跨道延後。
- file: `scripts/hooks/claude/check-graph-sync.py:1109-1111` 只有 Exception 才退名額,被 SIGKILL 時沒有退名額的機會。

### F3 自動執行白名單:S3 正例與規則互斥,「安裝目錄」未定義,`..` 穿越沒有規定
severity: major
blocking: 是——這是 spec 唯一的資安控制,實作者照字面做不出一致的行為。
段落:〈用詞〉自動執行白名單,與 [S3]。
問題:
1. S3 正例 `--config x.yml` 是相對路徑。白名單規則要求值展開 `$HOME` 後落在工具鏈安裝目錄,而 S3 自己又寫「`--config` 指向專案自己的檔 應不通過」。cwd 是專案時 `x.yml` 就是專案自己的檔,同一份文件裡正反都有。
2. 「整條命令除了開頭的 `$HOME` 之外不得含 `$`」寫的是命令開頭。實際範本的 `$HOME` 在 `--config` 的值裡,不在命令開頭;命令開頭必須是 `ast-grep`。照字面讀,所有真實宣告都不合,工作樹模式永遠 not-checked。
3. 「lumos 工具鏈自己的安裝目錄」沒定義怎麼算:`LUMOS_HOME`、`~/harness/lumos-toolchain`、`which lumos` 的 realpath 三個來源並存。也沒要求先正規化路徑(`..`、symlink)再比前綴。例如 `$HOME/harness/lumos-toolchain/../../Downloads/evil/sgconfig.yml` 的字串前綴通過,實際落在專案裡。S3 沒有 `..` 反例。
引句:「`ast-grep scan --config x.yml --format sarif {LINT_FILES} > {LINT_SARIF_OUT}` 應 通過」
佐證:
- file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:158` 真實範本是 `--config $HOME/harness/lumos-toolchain/configs/ast-grep/kotlin-android/sgconfig.yml`。
- file: `scripts/hooks/claude/check-graph-sync.py:660-664` 現有可信來源解析是 `LUMOS_HOME` 或 `~/harness/lumos-toolchain`,另有 `which lumos`,與規則裡「安裝目錄」是否等同沒有交代。

### F4 「沿用 `_handoff_files` 那一族的 `--no-optional-locks` 解法」查證不實
severity: minor
blocking: 否——S1 的「索引檔位元組相同」測試會抓到,不致做出壞系統,但 spec 的現況宣稱錯了。
段落:PRIOR-ART ②,以及範圍 2 的「改動清單」。
問題:
- spec 說沿用既有 `_handoff_files` 那一族的 `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all`。
- 實際 `_handoff_files` 是 `_lens_git(root, "status", "--porcelain", "-z", "-uall")`,沒有 `--no-optional-locks`,也沒有 `=v1` 或 `--untracked-files=all` 長旗標。
- 整個 `scripts/lumos` 與三支 hook 對 `no-optional-locks` 搜不到任何一筆。這個解法是新寫的,沒有現成可沿用。
- 實作者若照「沿用」直接呼叫 `_handoff_files` 的寫法,會改寫索引。
- 另外,`_harden_git_env`(關掉 `core.fsmonitor`、`diff.external`)只在 hook 的環境裡設,`_lens_git` 本身不帶。獨立執行的 `lumos lint-new --worktree` 對「被打開的專案」沒有這層保護,spec 的資安段落也沒要求。
引句:「沿用既有 `_handoff_files` 那一族的 `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` 解法」
佐證:
- file: `scripts/lumos:72868` `_handoff_files` 的實際呼叫。
- file: `scripts/lumos:66210-66225` `_lens_git` 不帶 `-c` 硬化,也不帶 `--no-optional-locks`。
- file: `scripts/hooks/claude/check-graph-sync.py:968-984` 硬化是靠 hook 環境變數繼承。

### F5 預算算式漏算 SIGKILL 寬限與 transcript 讀取,餘裕只有 1.5 秒
severity: minor
blocking: 否——只在慢機器加最壞時序才讓既有那道靜默放行,正常情況不受影響。
段落:範圍 3 的「時間」條,以及〈實務隱患〉第一條。
問題:
- spec 算 55×0.7−12=26.5 秒,說「不少於它實測需要的 25 秒」。
- 實際 lint 最壞耗時是 12 秒送 SIGTERM,再等 1 秒送 SIGKILL,共 13 秒,餘 25.5 秒,只剩 0.5 秒餘裕。
- 現行 `_BUDGET_START` 要等到第一次呼叫 `_inner_budget` 才記,第一次呼叫在 `_git_status_entries`(`_git`),發生在整份 transcript 讀完之後。spec 要把它搬到 `main()` 開頭,讓「已耗時」變成包含 transcript 讀取與 `emit_queue_patrol`。
- REVISIT 自己寫 406MB 逐字稿常駐約 4GB,讀取不可能是零秒。lint 跑滿加讀檔超過 0.5 秒時,既有那道的 `subprocess.run(timeout=…)` 拿到不足 25 秒的上限,逾時被 `except Exception` 吞掉,回 `None`,整道靜默放行。
- 算式要把 13 秒與 transcript 耗時列進去。
引句:「55 × 0.7 − 12 = 26.5 秒,不少於它實測需要的 25 秒」
佐證:
- file: `scripts/hooks/claude/check-graph-sync.py:327` `_git` 的 `timeout=_inner_budget(default=20)`。
- file: `scripts/hooks/claude/check-graph-sync.py:1010` `collect_turn_actions` 在第一次 `_inner_budget` 之前。
- file: `scripts/hooks/claude/check-graph-sync.py:1017-1019` 例外與逾時一律回 `None` 然後 `return 0`。
- file: `scripts/hooks/claude/check-graph-sync.py:732-734` `_BUDGET_START` 現行語意。

### F6 驗收條款與範圍使用未定義的旗標名,兩旗標組合沒有規定
severity: minor
blocking: 否——只是條款命名對不上,實作者能猜出意圖。
段落:[S1],與範圍 1。
問題:
- S1 寫「`--only` 跟改動清單沒有交集 應判 no-files」。全文只定義 `--only-stdin`,`--only` 不存在。
- 範圍 1 只說 `--only-stdin` 掛在 `--worktree` 底下,沒說 `--diff --only-stdin` 是 rc2、被忽略、還是有效。
引句:「`--only` 跟改動清單沒有交集 應 判 no-files」
佐證:
- file: `scripts/lumos` 對 `lint-new` 指令搜尋,目前只有常數與帳務字串,指令本身不存在(`python3.14 scripts/lumos lint-new --help` 回「沒有『lint-new』這個指令」),所以旗標以 spec 為單源,衝突無從以程式碼裁。

### F7 決策表的來源路徑沒定義,程式碼裡沒有任何讀型錄的現成函式
severity: minor
blocking: 否——可推出由 skill symlink 讀,但消費機沒有時的行為沒寫。
段落:範圍 4,第三與第四條。
問題:
- spec 說 lumos「讀決策表」,但沒說從哪個路徑讀、找不到時怎麼辦。
- `scripts/lumos` 對 `checks-catalog` 搜尋零筆,沒有讀型錄的現成程式。
- 型錄 341KB。每次 `.kt` 編輯、包括無圖譜專案(範圍 4 第二條要求照樣呼叫),都要由新啟動的 lumos 讀檔、解析、剝註解。
- 型錄不在消費專案內時的退化(不推、不報錯、不寫 fails)沒有規定。
引句:「`_kt_decision_table` 依表頭名稱取欄,不依欄位位置(第三批會多加欄)」
佐證:
- file: `skills/kotlin-idioms/checks-catalog.md:663-669` 表頭是 `列編號|情境|…|觸發字|…`,取欄依表頭名可行。
- file: `scripts/hooks/claude/impact-hook.py:414` 既有 `DELTA_TEXT_CAP = 2*1024*1024` 與 `delta_text` 已把編輯內容送進 payload,spec 另造 `delta_new` 沒提這個既有鍵。

### F8 `_kotlin_strip` 沒處理字元字面值,出現 `'"'` 後會吞掉後面的觸發字
severity: minor
blocking: 否——只造成漏推,不擋任何東西。
段落:範圍 4 第三條。
問題:
- spec 列的處理對象只有 `//`、巢狀 `/* */`、`"…"`、`"""…"""`。
- Kotlin 的 `'"'` 字元字面值會被當成字串起點,之後同一份 `new_string` 的程式碼被當成字串內容剝成空白。典型是 `if (c == '"') … .flatMapLatest {…}`。
- Edit 傳入的 `new_string` 只是片段,常沒有完整的前後文,所以不閉合的 `"` 或 `'"'` 更常見。
- S5 沒有「字元字面值」這個案例。
引句:「處理 `//`、巢狀 `/* */`、`"…"`、`"""…"""`,字串樣板 `${…}` 裡的程式碼保留」
佐證:查證靠 spec 自述與 Kotlin 語法,`scripts/lumos` 目前沒有 `_kotlin_strip`,無現成實作可對照。

### F9 時間戳先寫,lint 被逾時殺掉或 rc3 時那一回合的檔永遠不再被查
severity: minor
blocking: 否——推送前閘與代碼審通過前檢查兜底。
段落:範圍 3 最後一條,與〈天花板〉。
問題:
- 時間戳「一開始就寫」。之後 `lint-new` 回 rc3(沒裝工具、宣告檔有未提交修改),或整支 hook 被 55 秒時限殺掉,下一次收工的「上一個時間戳」已經晚於那些檔,該批從此不被這道看見,也沒有「待重查」標記。
- 〈天花板〉1 只提「同一回合先寫後提交的、續做那輪」,沒提 rc3 與被殺。
- 範圍 3 條件寫「專案根有 `.lumos/lint.json`」。Codex 沒有 `CLAUDE_PROJECT_DIR`,專案根是 payload 的 `cwd`。`cwd` 若是子目錄,既有 `find_graph_root` 也不往上找,所以這道會靜默不跑。
引句:「先讀出上一個時間戳,接著立刻寫入這一次的時刻」
佐證:
- file: `scripts/hooks/claude/check-graph-sync.py:88-100` `find_graph_root` 只看 `project_root/docs`,不往上找。
- file: `scripts/hooks/claude/check-graph-sync.py:992-996` 專案根取 `CLAUDE_PROJECT_DIR` 或 payload 的 `cwd`。

### F10 暫存區新增檔(`A` 狀態)的基準沒規定
severity: minor
blocking: 否——可以猜成跟 `??` 同樣處理。
段落:範圍 2 的「改動清單」。
問題:
- spec 只寫「未追蹤檔(`??`)基準為空」。AI 常用 `git add 新檔`,這會出現 `A ` 或 `AM`,HEAD 沒有該檔。
- 狀態碼 `A` 的檔該拿 HEAD 的空基準、還是走「同名已刪除檔」配對,沒有規定。S1 也沒有案例。
引句:「未追蹤檔(`??`)基準為空,但若同一份清單裡有已刪除的檔」
佐證:file: `scripts/lumos:72868` 既有解析只處理 `R`/`C` 的雙路徑,沒有 `A` 的語意可沿用。

### 各節已讀,無 finding
- 白話、用詞中除白名單外的各條、範圍 1 的退出碼三分類、範圍 5、範圍 6、〈開審前的改寫〉、〈回退〉:已讀,無 finding。
- 退出碼三分類對得上程式碼的八種狀態(`_lint_new_verdict` docstring 與 `_lint_new_classify`)。
- 以下查證都成立:`stop-block`、`stop-printed`、`_stop_dir_ok`、七天清理、`LUMOS_STOP_BLOCK_OFF`、`HOOK_BUDGET["check-graph-sync.py"]=40`、`--stdin-payload`、`--incidents-only`、`_codeloop_guard_verdict` 的 `keep_going`、`code-loop pass` 的 rc2。
- 交叉引用:`Projects/Android協程與API寫法機械檢查標準_計劃`、`Android的detekt推送前真的擋_計劃`、`Android寫法語意情境表態與盲判_計劃`、`Systems/graph-sync-coverage`、`改檔前推播`、`hook逾時預算`、`棧別提問表態閘`、`pitfalls-code-loop` 都存在。`Systems/回合結束寫法檢查` 是新開節點,屬預期。

### 實務隱患逐類(最壞時序)
1. **逾時或中斷時沒被收掉的程序**:`lint-new` 被 SIGKILL 時,各工具在新 session 的孫程序成為孤兒,但靠各自跑完或 8 秒預算自收,spec 有寫快照殘留一天清。**無新 finding**。hook 被外層砍時 `lint-new` 另開程序群組,最多再跑約 8 秒就自己結束。
2. **預算加總**:見 F5。
3. **標記檔與名額檔中途失敗留下的狀態**:見 F2(名額已佔、輸出沒出去)與 F9(時間戳先推進)。
4. **大檔或整本帳一次讀進記憶體**:`lint-new` 本身沒有整帳讀入。`git cat-file --batch` 讀「已刪除同名檔」的範圍沒規定上限。我給不出具體失敗場景,所以不標。
5. **兩個會談同時收工**:時間戳與名額檔都以會談編號分檔,O_EXCL 建檔;「同會談 3 個」的計數與建檔不是同一個動作,但同一個會談同時收工不會發生。**無新 finding**。
6. **磁碟滿**:建檔失敗等於「不擋」,與既有性質一致。**無新 finding**。

### 節點固定席
- **pitfalls-code-loop(★RISK★)**:不影響。範圍 5 的兩道在 `pass` 進留痕驗證之前跑,節點的 WHY(「閘放在 pass,綁定只在 pass 當下產生」)與簿記白名單豁免都不動。唯一變化是 `pass` 範圍變成整條分支,spec 已在〈實務隱患〉自述。
- **lumos-cli-lifecycle(★INVARIANT★ re-inject 只覆蓋 sentinel 之間)**:不影響。本案只改 `merge-claude-settings.py` 的 `HOOK_BUDGET` 數字,寫的是 settings.json,不碰 CLAUDE.md 的 sentinel 區塊。也沒有新增 hook 檔,不會觸發 `_prune_dangling` 剪註冊。
- **canary-audit、design-loop、lumos-cli-read 的 INVARIANT**:不影響。本案不碰 canary 紀錄、設計審處置閘或 search 過濾。S1 到 S6 帶 `[test:]`,S7 是 `[manual:]`,不違反處置閘第五步「任一條款綁定測試」。
- **Issues/hook卸載殘留註冊**:不影響,理由同上,沒有新增或移除 hook 檔。

最嚴重 severity 是 major,blocking 共 3 條(F1、F2、F3)。
