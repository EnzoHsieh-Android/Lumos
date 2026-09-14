severity: clean

## 結論

這一輪(r2)相對 r1 新增兩處會碰到「不可信輸入」的改動:①`_lint_run_and_parse` 共用的 uri→相對路徑正規化,在字面算不出專案內路徑時多補一次 `os.path.realpath` 兩邊重算;②`lumos lint-check --smoke` 新增 `_lintcheck_smoke_cmd`,用 `git ls-files -z -- '*.<棧鍵>'` 抓專案裡真的有的檔、`shlex.quote()` 後替換進宣告命令的 `{LINT_FILES}` 佔位符再執行。逐條追了資料流向與消費點,兩處都沒有找到「誰、從哪個入口、送什麼、拿到什麼」四件成立的攻擊路徑。沒有 finding 要開。

**威脅前提(自己寫清楚)**:
- 誰能控制專案裡的檔名——任何能提交檔案進這個 repo 的人(含惡意 fork/PR),或直接被拿來 clone 冒煙的整個陌生 repo 的作者。
- 誰能控制 `.lumos/lint.json`——寫這個消費專案的人;此檔宣告的 `cmds` 本身就是整段 shell 指令字串,r1 已裁定「誰能改它,誰就已經對這道閘有完整任意 shell 指令執行權」,這是既有信任邊界,這一輪沒有改變它。
- 誰能控制工具輸出裡的路徑——被宣告命令呼叫的那支分析器(dart/eslint/sqlfluff/…)本身,或者間接地、透過它去分析的專案檔案內容(例如檔案路徑、symlink)。

## 逐類

**1. 不可信輸入流到危險操作(命令注入 / 路徑穿越)**

已看,無可利用路徑。兩個新增點分開追:

- **`_lintcheck_smoke_cmd` 的命令注入疑慮**:`stack` 這個鍵來自 `.lumos/lint.json` 的 `config.items()`,`git ls-files -z -- "*." + str(stack)` 是用 `subprocess.run([...])` 的 argv 清單呼叫(scripts/lumos:17173-17174,非 `shell=True`),`stack` 混進 pathspec 頂多讓 glob 比對出乎意料,不會被 shell 解讀,不構成命令注入。真正會進 `shell=True` 的是 `git ls-files` 選出來的**檔名**,這些檔名逐一 `shlex.quote()` 後才 `cmd.replace(_LINT_NEW_FILES_TOKEN, ...)`(scripts/lumos:17179)。`shlex.quote` 是 POSIX shell 安全跳脫的標準做法,任何 `;`、`` ` ``、`$()`、空白、換行都會被包進單引號、不會被 shell 當成指令邊界——實際檔名清單是 `git ls-files -z` 用 NUL 分隔取出來的(scripts/lumos:17176),連檔名本身帶換行都不會拆錯。這條路徑跟既有主閘 `_lint_new_verdict` 裡「逐檔 quote 再接 `{LINT_FILES}`」(scripts/lumos:18261-18264)是同一套寫法、同一風險水位,r1 已審過主閘那份是 clean,這次只是把同一套邏輯複用到 `--smoke`,不是新的注入面。
  - 有另外想過「dash 開頭檔名讓下游分析器把檔名誤判成旗標」(argument injection,例如檔名叫 `--rulesdir=x.py`):`shlex.quote` 只保證 shell 把它當成一個字面 token 傳給程式,並不保證**該程式自己**不會把開頭 `--` 的字面內容解讀成旗標。查了這批棧會呼叫的工具(dart analyze / ruff / eslint / sqlfluff / PMD / detekt / SwiftLint / checkstyle / osv-scanner),沒有找到具體「純粹靠檔名位置的參數就能觸發執行任意碼」的旗標——這條寫不出「送什麼→拿到什麼」的具體鏈,只能是推論,而且**冒煙路徑跟正式閘用的是同一套「逐檔 quote、不加 `--` 分隔」寫法**,不是這次新增的缺口,所以不單獨開 finding,只在此記錄已排除。
  - 也想過「repo 裡追蹤一個指向 repo 外的 symlink,誘使分析器讀到 symlink 目標、把內容片段回吐進診斷訊息」:`--smoke` 這條路徑即使命令跑成功,`_claims` 直接丟棄不印(`cmd_lint_check` 裡 `_claims, ok = _lint_run_and_parse(...)`,scripts/lumos 附近的 `--smoke` 迴圈只在 `not ok` 時印 `cmd[:60]`,從不印診斷內容)——沒有輸出通道可以外洩,所以就算分析器真的跟隨 symlink 讀到東西,`--smoke` 本身也不會把內容吐出來。真正會把 claims 內容印出去、寫進治理帳的是既有的推送前閘主流程(`_lint_new_verdict`),那條這次沒有動,不在本輪 delta 範圍內,而且屬於 r1 已認可的既有信任邊界(消費專案自己的分析器行為)。

- **`_lint_run_and_parse` 的 realpath 正規化 → 路徑穿越疑慮**:確認過這個 `rel` 值(scripts/lumos:17605-17622)唯一的消費點是 `_lint_new_key`(scripts/lumos:17985-18000)拿去當 `text_by_file.get(f)` 的查表鍵,而 `text_by_file`(即 `base_text`/`head_text`,scripts/lumos:18016-18017)是用 `_lint_new_extract` 從 git 兩個版本安全解出來的**已知專案內檔案**建的字典,鍵集合完全由 git diff 決定,不受這個 `f` 影響。真正拿去 `open()`/`read_text()` 讀檔的是字典裡查到的 value(`base_files[f]`/`head_files[f]`,已知的暫存快照路徑),不是 `f` 這個字串本身——所以就算工具回報一個指到專案外或帶 `..` 的絕對路徑,`realpath` 轉換出來的 `rel` 頂多讓這個查表 miss(退化成弱比對的 `~msg~` 分支)或誤配到另一支同名檔案,不會讓程式去讀取「專案外的檔」的內容。跟 r1 對舊版 `_dart_rel` 的結論一致:這條路徑正規化只影響「新增比對」的指紋計算,不是檔案讀寫的路徑輸入。
  - `os.path.realpath` 本身會跟隨 symlink,但這裡 `repo_root` 也同步做 `os.path.realpath`,兩邊等價正規化後才比較是否還有 `..`——不會出現「原本在專案外的路徑被 realpath 洗成看似專案內」這種穿越(如果穿越前後都不在 repo_root 底下,`_real.startswith("..")` 仍然成立,不會覆蓋 `rel`)。

**2. 登入與權限**

已看,無。兩處改動都不涉及任何身分驗證或授權判斷。

**3. 密鑰與個資**

已看,無新增揭露面。`cmd_dart_sarif` 新的錯誤訊息把 `str(e)[:80]`(其中 `e` 可能包在 `_dart_sarif_results` 拋出的 `ValueError`,內容是 `str(g)[:80]`,即讀不懂的診斷項目片段)印到 stderr——跟 r1 審過的舊版 `print(f"開頭是:{raw.strip()[:80]!r}")` 同一等級:自動化的推送前閘 `_lint_run_and_parse` 一律 `stdout=DEVNULL, stderr=DEVNULL`(scripts/lumos:17552-17553),這條 stderr 訊息在閘裡直接丟進黑洞;`--smoke` 一樣透過 `_lint_run_and_parse` 執行,同一套 DEVNULL,不會外流。唯一看得到這行輸出的是使用者自己手動在終端機跑 `dart analyze | lumos dart-sarif`,來源與觀看者是同一人,沒有跨信任邊界。`dart analyze --format=json` 的診斷內容本身是靜態分析訊息(規則代碼/訊息/位置),不是一般會夾帶密鑰的欄位。

**4. 加密與傳輸**

已看,無。純本機檔案 I/O、subprocess 與 stdin/stdout,不涉及網路傳輸。

**5. 執行邊界(hook/pre-push/CI 執行不可信位置的檔;shell 插值;符號連結導向寫入)**

已看,無新增風險:

- `_lintcheck_smoke_cmd` 呼叫的 `git ls-files` 本身是唯讀查詢(不執行任何被列出的檔案),抓到的檔名只拿去做字串替換,不會被當成可執行檔直接呼叫。
- shell 插值:這次新增的兩處插值(`_lintcheck_smoke_cmd` 的檔名清單、既有 `{LINT_SARIF_OUT}`/`{LINT_FILES}` 佔位符)全部先過 `shlex.quote()` 才進 `cmd.replace(...)`,沒有任何字串未跳脫就接進 `shell=True` 的指令。
- 寫檔目標被符號連結導去別處:`cmd_dart_sarif` 的 `open(out, "w")` 這次多包了 `try/except OSError` 只是把例外訊息講清楚(rc2、不留 Python traceback),沒有改變「用什麼路徑開檔」的邏輯——自動化路徑的 `--out` 仍然是 `_lint_run_and_parse` 用 `tempfile.mkstemp()` 現生的隨機檔名(scripts/lumos:17539),跟 r1 的結論一樣不構成攻擊者能預先埋符號連結的窗口。

**6. 行動端**

已看,無,跟行動端(iOS/Android)無關。

**額外檢查:新加的依賴**

這次 delta 只用到 `shlex`、`subprocess`、`os`、`json`,全部是既有已使用的標準庫,沒有新增任何第三方 Python 依賴,零依賴家規沒被打破。消費專案自己安裝的 `dart` SDK 仍是既有信任邊界(誰能在 PATH 上放一支假 dart,誰本來就已經有本機任意執行能力),這次沒有新增或改變這一層。
