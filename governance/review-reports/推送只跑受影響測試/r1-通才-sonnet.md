severity: major

我讀完整份 spec,並對照 push-subset repo 的 `scripts/lumos`、`scripts/test_lumos.py`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml` 查證。基礎設施清單的機械判準與 spec 自己的例子互相矛盾,另有 3 條會讓照字面實作的結果出錯。

---

severity: major
blocking: 是(照字面實作會把該跑全套的執行器改動放成 affected)
spec 段落:〈做法〉第 2 點基礎設施清單,`scripts/test_lumos.py` 執行器本體函式的機械判準。
問題:判準與它自己舉的例子互相矛盾。
引句:「被測試呼叫的是輔助,走關鍵字;沒被任何測試提到的就是執行器自己」
佐證:
- 我用腳本把 `scripts/test_lumos.py` 切成 3202 支 `t_` 測試和 843 支非 `t_` 頂層函式,逐個做整字比對。
- 只有 24 支沒被任何 `t_` 測試提到,例如 `_keys_suite_select`、`_helper_sources_in`。
- spec 例子裡的 `main` 被測試整字提到,所以按判準算輔助,不進全套清單。
- `run`、`check` 也被測試提到。`check` 是每支測試都用的斷言函式,它壞了就是「所有測試假綠」,正是這一節要防的情形。
- 換句話說,判準只擋得住 24 支沒人提到的函式,擋不住 `main`、`check`、`run`。
- 要靠 `main` 名字被提到來判斷,本來就不可靠,因為 `main` 也是分支名,測試原始碼裡到處是。
- `scripts/test_test_lumos.py:58`(實際為 `scripts/test_lumos.py:58`)

---

severity: major
blocking: 是
spec 段落:〈做法〉第 1 點「選中數不超過全部的一半」,以及關鍵字擴一層。
問題:執行器現行有「單一關鍵字選中超過 30% 就整個丟掉」的規則。spec 沒提這條,也沒說「選中數」由誰算、怎麼算,所以兩者會打架。
引句:「關鍵字選中的測試數不超過全部的一半(超過就沒有省到,直接全套)」
佐證:
- `_keys_suite_select(tests, keys, cap=0.3)` 會把選中超過 30% 的關鍵字丟掉,不選任何測試。
- 改到的函式剛好是 `check` 或 `run` 這類泛用名稱時,該關鍵字被靜默丟棄。
- 剩下的關鍵字若仍選得到幾支,`pitfalls` 會判 affected 並少跑,這支被丟掉的函式實際一支測試都沒跑。
- spec 的「一半」門檻和執行器的 30% 門檻不同,後者先動手,前者永遠不會觸發。
- spec 也沒說 `pitfalls`(在 `scripts/lumos`)要如何數選中數。它得用執行器那份邏輯,或自己重寫一份,而且要是消費專案沒有 `test_lumos.py` 時行為不明。
- `scripts/test_lumos.py:58`
- `scripts/lumos:61758`

---

severity: major
blocking: 是
spec 段落:〈做法〉第 1 點關鍵字改成 `_affected_test_keys_wide`,以及基礎設施清單的 `_SELECTION_FUNCS`。
問題:關鍵字只認 `def` 函式名。改模組層常數、正規式、表格、分派表時抽不出關鍵字。
引句:「改到的頂層函式名;`cmd_` 開頭的加子命令名(既有做法)。」
佐證:
- 沿用的 `_affected_test_keys` 只看 `@@ … @@` 標頭或 `+/-` 頂格行裡的 `def`。
- 依正規式字面,改 `_DOCS_ONLY_NEVER`、`_KEY_OK_RE`、`_BOOKKEEPING_FILES` 這類常數時,標頭顯示的是常數行或前一個函式,抽不到、或歸錯函式。
- 一次改動若同時動了某個函式和某個選測相關常數,只有函式進關鍵字,常數被漏掉,而 `_SELECTION_FUNCS` 只登記了 5 個函式名。
- 這條我只從正規式字面推論,沒有實際造 diff 跑。
- `scripts/lumos:61758`

---

severity: major
blocking: 是
spec 段落:〈做法〉第 5 點漏抓統計、〈驗收條款〉S7、〈RETIRE-IF〉。
問題:`subset-miss` 的判準會誤算,RETIRE-IF 的「累計 3 次」也算不出來。
引句:「紅的那支不在清單裡就標「子集漏抓」、加標籤 `subset-miss`」
佐證:
1. 主線上已經存在的紅,或偶發紅,會在之後每一次合併的 push CI 都再紅一次。對那些合併來說,這支測試通常不在它的選測清單,於是每次都被標成漏抓。
2. 重算結果若是 full 或 docs(例如那個 PR 改到基礎設施清單),spec 沒說該標什麼。那種 PR 本來就跑了全套,不是子集漏抓。
3. 「同標籤已有開著的 Issue 就改成留言」,所以 `subset-miss` 標籤會落在同一篇 Issue 上,累計「次數」就數不出來。RETIRE-IF 要的是「3 次以上」。
4. S7 只有 `[manual:…]`,沒有任何會翻紅的自動測試。重算邏輯有壞,CI 也不會紅。

---

severity: minor
blocking: 否(措辭或可量性缺口,不影響程式行為)
spec 段落:〈RETIRE-IF〉第二半。
引句:「八週內功能分支推送前的測試時間中位數沒有比上線前少一半以上」
問題:現況沒有任何紀錄推送前測試時間的地方,「上線前」也沒有基準值。
佐證:`scripts/hooks/pre-push` 對 `duration`、`elapsed`、`SECONDS` 搜尋 0 筆。spec 做法裡也沒有新增這筆紀錄。〈現況〉裡「一小時」只是單次人工量測。

---

severity: minor
blocking: 否
spec 段落:〈做法〉第 6 點、〈回退〉。
問題:`LUMOS_PREPUSH_FULL` 在 repo 目前不存在,spec 沒說由誰讀。S2 要求 `pitfalls` 讀它,hook 也要讀。
佐證:
- 對 `scripts`、`.github` 搜尋 `LUMOS_PREPUSH_FULL` 0 筆。
- RETIRE-IF 說「設成 `LUMOS_PREPUSH_FULL` 預設開」,但沒說預設值改在哪、怎麼改。
- CI 端沒有等價的強制全套開關。「CI 回退」靠改 yml,所以回退節對本機是單次環境變數,對 CI 要重發版。這不算錯,但回退節沒講明這個差別。

---

severity: minor
blocking: 否
spec 段落:〈做法〉第 3 點推送前掛鉤。
問題:一次推多個 ref 時,affected 與現有 docs、light、full 三態怎麼合併沒有定義。
佐證:
- 現行 hook 對每個 ref 用 grep 取 `suite`,任一 ref 要 full 就 full(`scripts/hooks/pre-push:466`、`:544`)。
- affected 與 light 並存時,誰的關鍵字集合勝出,以及 `--target-ref` 如何對應到各 ref,spec 都沒說。

---

severity: minor
blocking: 否
spec 段落:〈現況〉量測表。
問題:最大改動那一列「函式名加直接呼叫者一層」寫「未量」。
佐證:函式名單獨就已選中約 460–500 支(約 15%),加一層呼叫者後會不會超過「一半」門檻,沒有資料。這個門檻也就沒有對最壞情況驗過。

---

實務隱患逐類:
- 守衛面:見上方 4 條 major,都出在選測會少跑、卻不知道自己少跑。
- 金流:無,只動測試範圍與 CI。
- 對外送出:spec 已寫 `gh issue create` 只用內建 token 且權限只給 notify,Issue 內文只放測試名與網址。已讀,無 finding。
- 不可逆:無,設定與程式都能還原。
- 併發:spec 已寫同標籤改留言。上面第 4 條指出這個設計同時讓次數算不出來。
- 本機 main 過時:已核對。`branch.main.remote` 是 `origin`,但 repo 遠端叫 `Lumos`,所以 `main@{upstream}` 認不到,會退回本機 main,與 spec 現況描述一致(`scripts/lumos:65710`)。已讀,S6 的前提屬實,無 finding。
- PRIOR-ART 與實作是否一致:引用的「不認得就退全套、每晚兜底」都有對應條款。實作採用既有 `_keys_mentioned` 並加一層呼叫者,與引文一致。已讀,無 finding。

共 8 條 finding,其中 4 條 major 會擋(blocking 是),4 條 minor 不擋。
