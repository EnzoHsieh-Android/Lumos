severity: major

邊界席 r1 報告,共 12 條。實驗用的臨時目錄已刪。

## 範圍 3(回合結束自動檢查)

### 1. 逐字稿「尾端 20 MB」跟「第一筆紀錄時間」互相打架,而且第一筆常常沒有時間
severity: major
blocking: 是。判準:照字面實作,大逐字稿或約 16% 的逐字稿會算不出「這一回合碰過的檔」,實作者得自己發明退路。
- spec 位置:〈用詞〉「這一回合碰過的檔」與範圍 3 的逐字稿一條。
引句:「會談第一次收工沒有時間戳檔時,用逐字稿第一筆紀錄的時間」
引句:「逐字稿只從尾端往前讀到這一回合的開頭,最多讀 20 MB」
- 問題一:第一筆紀錄在檔頭,只讀尾端 20 MB 就讀不到。REVISIT 那行自己寫了 406 MB 的逐字稿,那種逐字稿不可能同時滿足這兩句。
- 問題二:時間戳檔改成靠自己寫之後,「讀到這一回合的開頭」已經沒有用途。spec 也已否決用逐字稿判回合開始,這一條是遺留。
- 問題三:退路本身有洞。
- 佐證(指令與輸出):對本機 `~/.claude/projects` 335 份逐字稿讀第一行,輸出 `Counter({('queue-operation', True): 283, ('mode', False): 25, ('last-prompt', False): 23, ('custom-title', False): 3, ('ai-title', False): 1})`。51 份(約 15%)的第一筆沒有 `timestamp` 欄位。
- 退路還有一個洞:`--resume` 接回的舊會談,第一筆時間可能是幾天前。這時所有未提交的檔都會被當成這一回合碰過的。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:204`。既有的 `collect_turn_actions` 是整份 `read_text` 讀進來,spec 說的尾端讀取沒有現成可用的函式。

### 2. 合併、rebase 進行中:只處理了衝突檔,其餘被合進來的檔會被當成 AI 剛寫的
severity: major
blocking: 是。判準:AI 解合併衝突是常見情境,實作者照現文會做出「擋 AI 沒寫過的告警」的鉤子。
- spec 位置:範圍 2「改動清單」。
引句:「`u` 開頭(合併衝突)的檔不掃」
- 實驗:兩個分支衝突合併。
  - 指令:`git --no-optional-locks status --porcelain=v2 -z --untracked-files=all`
  - 輸出:`1 M. ... n.kt|1 A. ... new.kt|u UU ... c.kt|`
  - 結果:另一邊帶進來的 `n.kt`、`new.kt` 是一般已暫存的 `1 M.` / `1 A.`,跟 AI 自己的暫存改動無法分辨。
- 後果:這些檔的修改時間是合併當下,基準是 HEAD,所以對面分支整包的既有告警都變成「新增」。回合結束就擋停,最多三次。
- 此外:`git rebase`、`cherry-pick`、`stash pop` 同理。spec 的「天花板」和「實務隱患」都沒提這一類。

### 3. 未暫存的搬移加改 `package` 行,會讓整批舊告警變「新增」
severity: major
blocking: 是。判準:Android 搬套件一定要改 `package` 行,實作者照現文會做出每次重構都擋停、而且要手動放行幾百個指紋的鉤子。
- spec 位置:範圍 2 改名那一條。
引句:「部分修改後才改名的照新檔算,推送前閘會用 git 的改名偵測再判一次」
- 實驗:未暫存的 `mv A.kt B.kt`。
  - 輸出:`1 .D ... A.kt|? B.kt|`
  - 結果:只有內容逐位元組相同才配得上。
- 問題一:改過 `package` 行就配不上,B 的基準是空,B 裡本來就有的告警全算新增。
- 問題二:搬整個目錄時,每支檔都被改過、修改時間也是新的,所以每支都命中。擋停訊息只列 10 條,但放行要逐個指紋做。
- 問題三:同一批改動推送前閘不會擋,回合結束卻擋。這跟 spec 說的「推送前閘兜底」方向相反:兜底的閘比早期閘寬鬆。
- 另一個未定義處:「同一份清單裡已刪除的檔」要逐一比對 HEAD 內容。spec 沒說是 `git cat-file --batch` 加雜湊,還是每檔一個子程序。搬 2000 支檔時,做法沒釘就可能吃光 10 秒。

### 4. 快工具預設含 `sg`,而「安全形狀」又放行其他重導向,「只跑快工具」的資安保證撐不住
severity: major
blocking: 是。判準:這是 spec 自己宣稱的資安邊界,實作者照做會留下可被利用的缺口。
- spec 位置:〈用詞〉快工具、安全形狀。
引句:「字串清單,預設 `["ast-grep", "sg"]`」
引句:「命令裡除了佔位符與一個 `> {LINT_SARIF_OUT}` 重導向之外」
- 問題一:在多數 Linux 發行版上,`sg` 是 shadow-utils 的 `sg <群組> -c <命令>`,用來切換群組後執行任意命令。
  - 一條 `sg users -c rm …` 的宣告,第一個詞是快工具,也沒有 `; | & ` $( <`,安全形狀會放行。
  - 我在 macOS 上沒有 `sg`,這點是已知行為,沒在 Linux 上實跑,標 ⚠。
- 問題二:安全形狀的禁用清單沒有 `>`。「除了一個 `> {LINT_SARIF_OUT}` 之外」讀起來是 `>` 本身不禁,第二個 `> ~/.bashrc` 可以過。`>>` 同理。
- 問題三:引擎用 `shell=True`,所以 `$HOME`、`${…}`、`*` 都會展開,而清單只禁了 `$(`。
- 問題四:沒有限制工具旗標。`ast-grep` 的 `--update-all` / `-U` 會直接改使用者工作樹的檔,而且是在每次收工時自動執行。
- 佐證:file: `scripts/lumos:39188`。`_lint_run_and_parse` 是 `subprocess.Popen(injected_cmd, shell=True, …)`。

### 5. 子程序預算和外層 kill 同為 10 秒,被殺後的結果沒定義;「已耗時含這道」也不成立
severity: major
blocking: 是。判準:實作者會做出兩個計時器賽跑、被殺沒有輸出、且超過時間上限的鉤子。
- spec 位置:範圍 1 的 `--budget`,範圍 3 的「時間」與子程序條。
引句:「兩種都加 `--budget 秒`,預算從指令一開始起算(含抽檔)」
引句:「這道用固定上限 10 秒;鉤子時間上限從 40 秒加到 50 秒」
引句:「用新程序群組開、逾時整個群組一起殺」
引句:「加 10 秒的上限剛好抵掉這道用的時間」
- 問題一:`lint-new --budget 10` 與鉤子的 10 秒 kill 同值,沒有餘量(Python 啟動、git status、快照)。內層一次正常超時也會被外層同時殺掉。被殺時沒有輸出,spec 沒定義這是 rc3、還是靜默。
- 問題二:殺掉會讓 `.lumos/lintbase-*` 殘留(`finally` 的 `rmtree` 不會跑)。這個目錄靠一天後清理。不是每個消費專案都 `.gitignore` 它,spec 沒要求。
- 問題三:「已耗時含這道」不成立。
  - 佐證:file: `scripts/hooks/claude/check-graph-sync.py:732`。`_BUDGET_START` 是第一次呼叫 `_inner_budget` 才記的。
  - 新這道若不先呼叫它或傳 `elapsed`,既有那道照吃 `50×0.7=35` 秒,最壞 10+35+逐字稿讀取接近 50 秒的上限。
- 問題四:已安裝機器的設定檔裡 timeout 與 `--budget 40` 要重跑安裝才會更新。舊註冊配新碼時最壞 `10+28=38` 秒,對 40 秒幾乎沒餘量。spec 沒提重新安裝或版本檢查。
- 佐證:file: `scripts/merge-claude-settings.py:121`。`"check-graph-sync.py": 40`。

## 範圍 2(工作樹檢查)

### 6. 「宣告檔位元組跟 HEAD 相同」在 Windows 預設 autocrlf 下永遠不成立
severity: minor
blocking: 否。判準:只是自動檢查在這種設定下靜默不啟動,不是壞系統。
- spec 位置:範圍 2 末條,範圍 3 條件。
引句:「宣告檔 `.lumos/lint.json` 與 `.lumos/config.json` 的工作樹內容要跟 HEAD 那一版位元組相同才跑」
- 實驗:`core.autocrlf=true` 下提交 `.lumos/lint.json`,刪除後 `git checkout --` 還原。
  - 工作樹是 `{"a":1}\r\n`,`git show HEAD:…` 是 `{"a":1}\n`,位元組不同,但 `git status` 乾淨、`git diff --quiet HEAD -- .lumos/lint.json` 回 0。
- 後果:spec 宣稱支援原生 Windows,那裡預設 autocrlf,整個功能會靜默失效。
- 補充:零提交的 repo 沒有 HEAD,這條永遠不成立,所以範圍 2 的「沒有 HEAD」路只有 CLI 走得到,鉤子永遠走不到。

### 7. 工作樹模式裡沒有快工具可跑時,現有判定函式會回 `clean`
severity: minor
blocking: 否。判準:只有 CLI 輸出誤導;鉤子 rc0 本來就靜默。
- spec 位置:範圍 2 工作樹檢查,最後那一段。
引句:「列成「工作樹模式不跑」(不算沒檢查,推送前閘會跑)」
- 佐證:file: `scripts/lumos:39823`。`_lint_new_classify` 在 `ran` 空且 `report_only` 空時落到 `else: clean`,輸出「沒有新增的告警」。
- 後果:只宣告 detekt 的專案(Android 主流)跑 `lint-new --worktree` 會得到「clean」,但一條命令都沒跑。這正是該函式註解「一條都沒跑就不准說乾淨」要防的情況。spec 沒給這種情況一個狀態。

### 8. 專案根不等於 git 根、`--only` 參數長度
severity: minor
blocking: 否。判準:都是邊角,補一句即可。
- spec 位置:範圍 3 條件,範圍 2 `--only`。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:1010`。既有碼用 `project_root / r` 預設工作目錄就是 git 根。
- 問題一:`CLAUDE_PROJECT_DIR` 是 monorepo 子目錄時,`status --porcelain=v2` 給的是相對 git 根的路徑,`.lumos/` 和 `--only` 的基準就差一層,spec 沒定義。
- 問題二:這一回合碰過幾千個檔時(批次改名),`--only <檔>…` 會撞 `ARG_MAX`。spec 沒說改走 stdin 還是分批。
- 問題三:以 `-` 開頭的檔名會被 argparse 當選項,spec 沒要求 `--` 隔開。

### 9. 時間戳檔放哪個目錄不明,跟「這個目錄只有擋過的會談才留東西」衝突
severity: minor
blocking: 否。判準:實作者要自己選目錄,選錯會打破既有測試釘住的性質。
- spec 位置:〈用詞〉與範圍 3 名額標記。
引句:「回合結束鉤子每次跑都在自己的標記目錄寫一個這個會談的時間戳檔(新增)」
引句:「同一個目錄、過同一個信任檢查,檔名 `<會談>.lint.json`」
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:777`。既有註解明說去重紀錄「刻意跟擋停標記分開」,否則打破「只有擋過的 session 才留標記」。`<會談>.lint.json` 放同一個目錄,時間戳檔若也放那裡就違反。
- 同一處還有三個沒定義的情況:
  - 清理:那個目錄的檔 7 天不動就刪。
  - `stop_hook_active` 提早離開時有沒有更新時間戳。
  - `session_id` 空時:既有碼 `if not session_id: return False`,新這道沒寫。

## 範圍 4(改檔前推列)

### 10. 觸發字「不准收一般常用字」的把關指向一個不存在的條款,現有型錄已違反
severity: minor
blocking: 否。判準:型錄的觸發字會把推列變吵,不會做出壞系統;但 S4 的行為取決於它。
- spec 位置:範圍 4 末條。
引句:「型錄的觸發字由第一批的型錄格式檢查把關:不准收一般常用字」
- 佐證:file: `docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:105`。母計劃 S3 只規範欄位數、編號唯一、觸發字非空,沒有停用字表,spec 說「停用字表與檢查在 … S3」是壞引用。
- 佐證:file: `skills/kotlin-idioms/checks-catalog.md:670`。D-3 觸發字含 `map`、`forEach`,D-15 含 `first`、`take`、`collect`。
  - 這些就是 spec 自己點名的常用字。
  - `suspend` 同時出現在 D-1、D-2、D-6、D-19、D-20 五列,任何協程檔的編輯幾乎都命中。

### 11. 影響脈絡為空時的冷卻標記撤銷,是第三個要改的點
severity: minor
blocking: 否。判準:漏改只會讓冷卻窗行為變怪,實作者看測試會發現。
- spec 位置:範圍 4 第 3 條。
引句:「鉤子要改兩處:既有「影響脈絡是空的就不印、直接返回」那條路」
- 佐證:file: `scripts/hooks/claude/impact-hook.py:1004`。`_impact_for_file` 在 `ctx` 空時會 `_ttl_unmark` 撤冷卻標記並回 `None`。
- 問題:只有 `decision_rows` 時鉤子印了東西,卻撤掉冷卻標記。spec 說「改兩處」,實際是三處(還有這個函式)。
- 另外:`delta_new` 沒有像 `delta_text` 那樣的 2 MB 上限(file: `scripts/hooks/claude/impact-hook.py:414`),Write 一份很大的 `content` 會讓子程序輸入無上限。

## 範圍 5(代碼審通過前先查)

### 12. `pass` 呼叫共用函式時,範圍算不出來、`--diff` 與 `--worktree` 同時給或都沒給,都沒定義
severity: minor
blocking: 否。判準:都是補一句規則的缺口。
- spec 位置:範圍 1、範圍 5。
引句:「`pass` 的範圍跟 `code-loop check` 不帶 `--diff` 時相同(跟主線的分岔點到 HEAD)」
- 佐證:file: `scripts/lumos:71000`(約)。`_codeloop_guard_verdict` 在 merge-base 算不出、或等於 HEAD(在主線上直接 pass)時是 fail-open 放行。
- 問題一:`pass` 這兩種情況怎麼走,spec 沒說。是跟 check 一樣放行,還是擋?
- 問題二:detached HEAD 時分支名是空的,留痕綁定怎麼處理沒寫。
- 問題三:`lint-new` 的 `--diff` 與 `--worktree` 同時給或都沒給時,該報錯還是挑一個,spec 沒寫。
- 問題四:`--diff` 給單一版本(例如 `HEAD~3`),終點會被解成工作目錄,現有碼會走 env-unavailable → rc3。手冊要求「rc0 才派」,所以這種寫法會永遠派不出,spec 沒提醒。

## 逐節已讀
- 〈用詞〉其餘條目、範圍 6(手冊)、不做、回退、天花板、驗收條款:已讀,除上列外無 finding。
- 資安以外的風險類:
  - 金流、對外送出、不可逆:spec 已排除,我同意(`lint-new` 只讀本機、鉤子只印)。
  - 時鐘:本席只確認「時間戳回撥或檔案修改時間在未來」會讓檢查被漏掉或每次都檢查,這已在天花板第 3 條涵蓋,不另算。
  - 共用工作目錄:已在實務隱患提及。
- 資安風險類已在第 4 條涵蓋(`sg`、重導向、旗標)。

最嚴重 severity:major;blocking 共 5 條(第 1、2、3、4、5 條)。
