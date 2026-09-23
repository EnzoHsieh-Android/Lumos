severity: major

## F1 run_id 型別不同時,`_ci_latest_attempts` 不會把它們當同一次執行去重
severity: major
blocking: no

`_ci_latest_attempts` 直接拿 `r.get("run_id")` 原始值當 dict key 分組:

引句:「        cur = best.get(rid)」

沒有對 `rid` 做任何型別正規化(例如 `str(rid)`)。若同一個執行的兩筆記錄一筆 `run_id` 存成整數 `5`、一筆存成字串 `"5"`(函式自己的說明文字承認「帳是 JSON,不同版本的寫入端可能不同」,見下方引句),Python dict 會把 `5` 與 `"5"` 當成兩個不同 key,兩筆完全不會合併,舊的紅色那筆會單獨留在結果裡不被新的綠色蓋掉——這正是這支 patch 要修的原始症狀(「重跑變綠了還一直回報紅」)在型別不一致這個角落原封不動地重現。

引句:「只該跨不同執行★(2026-09-23 實踩):同一個提交的全部筆取最壞,是為了」

實測(在 /tmp 的獨立腳本重現,非改動 repo):把同一組 rows 的 `run_id` 一筆設成 `5`、一筆設成 `"5"`,`_ci_latest_attempts` 回傳兩筆各自獨立,舊的 `failure` 完全沒被去重掉。

不過機械查證了寫入端:唯一會寫這支帳的地方是 `_ci_record`,`rid = r.get("run_id")` 來自 `cmd_ci_wait` 組出的 `out` dict,而那個值全部來自 `gh run list --json` 的 `databaseId`(JSON number,`json.loads` 後恆為 Python `int`)。查證路徑:`scripts/lumos:24546`、`scripts/lumos:24558`、`scripts/lumos:24608`(`_ci_record` 的 `rid = r.get("run_id")`)。目前整個 repo 只有這一個寫入路徑(`grep -n "CI_LOG_NAME" scripts/lumos scripts/hooks/claude/ci-status-hook.py` 只在這兩支檔命中,讀端零改動),所以現況下不會真的產生字串型 `run_id`——這是一個真實但目前打不到的角落,不是本次 diff 引入的迴歸;但函式的說明文字聲稱要防「不同版本的寫入端」卻沒真的正規化型別,`t_ci_rerun_latest_attempt_wins` 與 `t_ci_latest_attempts_copies_identical` 兩支新測試都沒有涵蓋這個情境,屬於文件承諾與實作不符。

## F2 同一 run_id、同一 attempt 但結論不同時,挑哪一筆看檔案順序而非任何明講的語意
severity: minor
blocking: no

引句:「        if cur is None or att >= cur[0]:」

`>=` 讓「後面出現的那筆」在同 attempt 時蓋過前面那筆,但這只是迭代順序(即 log 檔的寫入順序)的副作用,函式的 docstring 完全沒提到「同 attempt 時怎麼挑」,兩支新測試(`t_ci_rerun_latest_attempt_wins`、`t_ci_latest_attempts_copies_identical`)也都只測了「不同 attempt」的情況,沒測「同 attempt、不同結論」這個組合。

實測(獨立腳本,非改動 repo):rows 為 `[{run_id:5, attempt:1, conclusion:"failure"}, {run_id:5, attempt:1, conclusion:"success"}]` 時回傳 `success`;把順序反過來,回傳 `failure`——同一組資料,只是寫入順序不同,結論就不同。

追查是否真的可能發生:`_ci_write` 的去重鍵是 `dedup_key = f"{rid}:{att}:{concl}"`(查證:`scripts/lumos:24610`),即同 run_id、同 attempt 但結論不同的兩筆,dedup 機制擋不住(key 不同),理論上能兩筆都寫進帳。但沿著 `cmd_ci_wait` 唯一的寫入路徑看,同一次呼叫不會為同一個 run 寫兩筆不同結論;要出現這個組合,必須是兩次分開呼叫 `ci-wait` 都查到同一個 `attempt`(即中間沒有真的重跑、attempt 沒有遞增)卻回報不同 `conclusion`,這只有 GitHub API 本身不一致/最終一致性延遲之類的罕見狀況才會發生,不是這支 patch 常態路徑會踩到的。列為 minor 是因為目前的順序依賴沒有文件化、沒有測試釘住,但可觸發條件罕見且非本次迴歸。

## F3 PITFALL 聲稱「重跑後 attempt 真的會遞增」,新測試沒有實際驗證這段
severity: minor
blocking: no

節點筆記與測試 docstring 都主張已經去查證 `ci-wait` 寫帳時拿到的 attempt 真的會遞增(鏡頭③要求的查證項目),但新增的測試直接繞過 `cmd_ci_wait` 讀 gh 回應、組 `attempt` 欄位那段程式,改成直接手寫 log 檔:

引句:「    put([row(5, 1, "failure"), row(5, 2, "success")])」

`t_ci_rerun_latest_attempt_wins` 全程只呼叫 `ci-status`/hook 去讀已經手寫好的帳,沒有一行透過 `_GH_STUB_HEAD` 之類的 gh 樁模擬「先回 attempt=1 failure、重跑後再回 attempt=2 success」讓 `cmd_ci_wait` 自己去寫兩筆帳,所以「`cmd_ci_wait` 寫帳時 attempt 真的會遞增」這件事在這支 patch 裡仍然只是敘述,沒有被機械驗證,消費的是 `r.get("attempt", 1)` 這行(查證:`scripts/lumos:24546`、`scripts/lumos:24558`)本身有沒有對(依 GitHub 公開行為,重跑整個執行或只重跑失敗工作皆會遞增 run 的 attempt 計數,這點我用既有知識核對、無法在此沙箱內連線 GitHub API 實測)。列為 minor:結論(遞增)大機率正確,缺的是這支 patch 自稱「有測試釘住」的那個環節其實沒有真的釘住寫入端。

---

## 實際驗過的路徑(補充,非發現)
- 在 /tmp 獨立腳本重跑 `_ci_latest_attempts` 邏輯,逐一餵入:attempt 缺、`0`、字串 `"2"`、負數、非數字字串、同 run_id 同 attempt 結論不同、run_id 型別不同 —— 除 F1/F2 外其餘皆按「留最大 attempt」正確運作(例如非數字字串 `attempt` 會被吃成 `0`,不會讓壞資料贏過正常 attempt)。
- 讀了 `scripts/lumos` 裡 `cmd_ci_wait`/`_ci_record`/`_ci_write`/`_ci_list_runs` 全段(約 24390–24630 行),確認 `run_id` 目前恆為 `gh` 回傳的 `databaseId`(int),唯一寫入路徑只有一條。
- 確認 `cmd_ci_status`(主程式)與 hook 各自在取得「latest attempts」之後、選 `last`/`reds[0]` 之前都先把 rows 篩到同一個 sha,不會有跨 sha 的 run_id 誤併(鏡頭⑤:URL、failed_step 印出來的那一筆確實對得上該 run 的最新 attempt,沒有欄位被不同 attempt 的資料混到)。
- 讀了 `t_ci_latest_attempts_copies_identical` 的 AST 比對邏輯,確認它會抓到兩份複本任何一行邏輯不同(已用 `ast.dump` 排除行號干擾、只跳過開頭 docstring),但它只保證「兩份一致」,不保證「這份邏輯本身對」——F1/F2 這種兩份都一樣錯的情境,這支守衛測試本來就過不了它、也不該指望它抓到(它的職責邊界寫得很清楚,不是這支測試的缺陷)。
