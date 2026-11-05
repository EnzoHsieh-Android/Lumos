severity: clean

我逐條用 ast-grep 實跑了這輪改到的規則。沒有會擋推送的問題。

**工具與環境**
- 用 ast-grep 0.51.1。
- 修後版本取自 `ba5996e5a`,修前版本取自 `af64ec645`,各自 `git archive` 到臨時目錄,用各自的 `sgconfig.yml` 掃同一批片段。
- 自我檢查 `check.py` 在 repo 根只讀跑過,輸出「規則 207 條,問題 0 個」。
- 本席臨時目錄已刪。

**問題一:原問題的修復效果有何行為證據?**
- **kt-long-lived-scope-plain-job(加法接 SupervisorJob):**
  - 輸入:`private val job = SupervisorJob(); private val scope = CoroutineScope(Dispatchers.Main) + job`
  - 預期:不報。
  - 修前:報。修後:不報。
  - 輸入 `CoroutineScope(Dispatchers.Main + CoroutineName("x")) + job`:修前報,修後不報。
  - 兩版用同一批片段,可比,修復可歸因。
- **kt-ktor-client-per-call(同一個變數 use):**
  - 輸入:`val c = HttpClient(CIO); return c.use { it.get("x").bodyAsText() }`
  - 預期:不報。
  - 修前:報。修後:不報。
- **kt-savedstate-bang(拿掉泛用名 state):**
  - 輸入 `state.get<String>("id")!!` 和 `state["id"]!!`,其中 `state` 宣告成 SavedStateHandle:修前報,修後不報。
  - 這是刻意取捨:`state` 是 SavedStateHandle 時會漏報。擋推送的規則寧可少報,我不算它是問題。
  - 同一片段裡的 `savedStateHandle` 仍報,所以 `handle` 與 `savedState` 這幾個名字沒被拿掉。
- **kt-okhttp-response-not-closed、kt-datastore-read-no-catch(搬到 rules-review/):**
  - 兩條在 `rules-review/` 都是 info 等級,bad 樣本在 `sgconfig-review.yml` 下各命中自己。
  - 同樣的 bad 樣本在 `sgconfig.yml`(`rules/`)下命中 0 筆,`rules/` 沒有殘影。
  - 全 repo 只有 `rules-review/api.yml`、`rules-review/data.yml` 與型錄兩處引用,沒有失效的引用。
  - 型錄 `skills/kotlin-idioms/checks-catalog.md` 的 API-17、DATA-10 兩列已改成語意覆核級。

**問題二:修補處的正常、錯誤與相鄰路徑是否仍成立?**
- **Ktor 錯誤路徑仍報:**
  - `w.use { }` 關的是別的資源,仍報。
  - 另一個 client `d` 被 use,但 `c` 沒關,仍報。
- **long-lived scope 錯誤路徑仍報:**
  - 加法接的是普通 `Job`(`other`),仍報。
  - `CoroutineScope(x) + CoroutineName("n")`,仍報。
  - `+ CoroutineName(job.toString())`(`job` 不是加法的直接運算元),仍報。
  - `+ Job() + job.hashCode().let{…}`,仍報。
- **long-lived scope 相鄰路徑仍成立:**
  - `+ jobA + CoroutineName("a")`(`jobA` 是外層加法的直接運算元),不報。
  - `Dispatchers.Main + job` 寫在括號內,不報。
- **問題三(新發現同案例修前修後):** 沒有新發現。

**非阻擋觀察(不另列為問題)**
- 類別裡有兩個 SupervisorJob 屬性、scope 只用第二個(例如 `jobB`)時,`CoroutineScope(x) + jobB` 與 `CoroutineScope(x + jobB)` 兩種寫法修前修後都仍報,會誤報。
  - 原因是 `$J` 只綁到第一個符合的屬性,這是舊限制。
  - 本輪沒有放大它,我也沒有逐一確認加法路徑與括號路徑是否共用同一限制。
  - 寫成 `.plus(jobA)` 也仍報。
- 這類寫法很少見,所以不列為問題。

**未驗範圍**
- 本席沒跑 `test_lumos.py`。
- 沒審 check.py 的 files 區塊、型錄統計與測試改名,那些不在我這份規則 patch 裡。
- 沒有「整體無回歸」的保證,只涵蓋上述片段。
