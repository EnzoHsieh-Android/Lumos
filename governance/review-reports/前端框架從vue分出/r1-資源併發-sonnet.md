severity: major

審查鏡頭是資源併發:新加的檢查在大輸入下會不會變慢或吃光記憶體、子程序有沒有收掉、推送前閘的時間預算夠不夠。

我讀完整份凍結審材,並對照工作樹 `scripts/lumos` 查證。判棧、init、doctor、原有題組這幾塊沒有資源面的問題。下面三條是新增的風險。

## F1 B10 的 Kotlin 判定沒有讀取上限,也沒說它要用哪一種讀法

- **位置**:〈做法〉B10 的「判伺服端的訊號」與「接線」,以及〈實務隱患〉的效能那條。
- **問題**:這個判定一旦實作,會在兩條路徑上讀檔。計劃只說「結果快取」和「每份只讀一次」,沒定四件事:
  - **預算和上限**:不讀多少位元組、不看多少支檔、什麼時候放棄。
  - **快取鍵**:是 `.kt` 檔的結果,還是建置檔的文字。
  - **讀法**:讀工作樹,還是讀 base/head 的版本。
  - **角色路徑要先登記**:角色那條路要先在 `_review_role_wanted` 登記要讀哪些檔。
- **具體例 1(pitfalls --diff 與推送前閘)**:
  - 輸入:一次改動 3000 支 `.kt`(例如 codemod 或改套件名),其中混了一支 100MB 的產生檔。
  - 預期:跟既有的角色路徑一樣有上限(`_ROLE_READ_CAP` 300 支、`_ROLE_MAX_BYTES` 512KB、`_ROLE_BUDGET` 3 秒)。
  - 照 spec 會得到:「全部 `.kt` 都判伺服端才拿掉 Android 三題」得替每一支改動的 `.kt` 各判一次。
    - 計劃沒說讀檔頭要讀幾個位元組,照字面容易寫成整檔 `read_text`。
    - 若快取只存「每支 `.kt` 的結果」,同一份 `build.gradle` 會被每支檔重讀。快取該存的是建置檔文字,做法同 `_node_pkg_text`。
- **具體例 2(角色路徑)**:
  - 輸入:`_review_role_for` 要對 `.kt` 判後端。
  - 現況:這條路只能讀 `_review_role_wanted` 事先批次讀好的 blob,讀的是 base/head 版本,而且受 3 秒預算限制。
  - 問題:計劃沒說要把「往上每層的 `build.gradle.kts`、`build.gradle`、`pom.xml`」加進 `_review_role_wanted`。
  - 兩種實作都會出事:
    - 不加進去:讀不到建置檔,角色永遠判不出,S26 在真實路徑上不成立。
    - 照字面用「同一支判定」讀工作樹:會繞過預算和版本隔離,在有預算的路徑上做不受限的檔案系統爬升。
  - 加的話,候選數 = 檔數 × 3 × 目錄深度。`_review_role_wanted` 自己的註解寫「★上限數檔,不數候選★」,所以 300 支檔最多可展開約 10000 個候選。
- **佐證**:
  - 引句:「pitfalls --diff 由改動檔的判定結果算出集合傳進去」
  - 引句:「同一支判定回伺服端時」
  - file: `scripts/lumos:30316` 的 `_review_role_for` 只吃 `reader` 和 `content`。
  - file: `scripts/lumos:30420` 到 `30470` 的 `_review_role_wanted` 只登記手機檔本身和 `_package_json_candidates`。
  - file: `scripts/lumos:30387` 起的 `_review_roles` 有批次讀取、512KB 上限、秒數預算。
  - file: `scripts/lumos:47276` 附近的 pitfalls 棧別迴圈沒有任何上限。
- **要補的**:
  - 讀檔頭有位元組上限。
  - 建置檔文字以路徑為鍵快取。
  - 角色路徑把建置檔候選併進 `_review_role_wanted`,並標明候選數怎麼算。
  - pitfalls 路徑對「判了幾支」設上限,超過的一律判不出(照舊附 Android 題,不會漏問)。
  - 補一條驗收條款:大量 `.kt` 與超大單檔輸入下,判定能在預算內收手而且不放寬任何擋下。
severity: major
- blocking: 是。實作者會在無上限的熱路徑上讀檔,或讓角色判定在真實路徑上永遠判不出。

## F2 統一後的「跑過的證據」樣式有二次方的卡死風險

- **位置**:〈做法〉F1 的 `_RAN_EVIDENCE`,spec 原文是「統一一條樣式,不分兩份」。
- **問題**:新樣式描述成「行首、`Tests` 後面可有可無冒號,同一行有 N passed」。照這個描述寫,中間會是 `Tests:?` 後接 `.*?` 再接 `[1-9]\d*\s+passed`,這形狀有二次方回溯。
  - 現行 jest 樣式 `Tests:.*?[1-9]\d*\s+passed` 本來就有這個毛病,但只有出現 `Tests:` 字面才觸發。
  - 新樣式把觸發條件放寬到「任何以 Tests 開頭的行」。
- **具體例**:
  - 輸入:vitest 或 jest 輸出裡有一行以 `Tests` 開頭、後面接一長串連續數字(長度會受 `_KILL_OUT_CAP` 256KB 限制)。
  - 預期:在合理時間內判定。
  - 照 spec 會得到:我用接近的樣式(`^[ \t]*Tests:?.*?[1-9]\d*\s+passed`,多行模式)實測,Python 3.14,輸出整份只有這一行加一行 `Test Files 1 passed`:

    | 數字長度 | 耗時 |
    |---|---|
    | 2 萬 | 2.76 秒 |
    | 4 萬 | 11.03 秒 |
    | 8 萬 | 44.24 秒 |

  - 長度到 256KB 時會是小時級。
- **兩個呼叫點都會中**:
  - `_ran_evidence_check` 對整份輸出做 `re.search`。
  - `_kill_cap` 對被砍掉的中段逐行做 `re.search(keep_re, l)`。`keep_re` 就是 `_ran_evidence_re` 的樣式。
  - 這兩處都在 `timeout` 之後,不受單支測試逾時保護,推送會卡在這裡。
- **佐證**:
  - 引句:「統一一條樣式,不分兩份」
  - file: `scripts/lumos:54306` 的 `_ran_evidence_check`。
  - file: `scripts/lumos:19378` 的 `_kill_cap`。
  - file: `scripts/lumos:54423`,`jobs[key]` 把同一個樣式當 `keep_re` 傳下去。
- **要補的**:樣式限定行內長度,例如 `[^\n]{0,200}?`。驗收條款再補一條(例如 S5 旁邊):超長數字行的輸出,在固定秒數內回答。
severity: minor
- blocking: 否。觸發需要罕見的輸出(以 Tests 開頭的超長連續數字行),實作者照 spec 做不會做出錯的行為,只是留了一個可被輸出觸發的卡死。

## F3 vitest 骨架的每支測試成本沒有算進推送前閘的時間預算

- **位置**:〈做法〉F1「`_init_config_skeleton`」,和〈實務隱患〉只談了判棧與 eslint 偵測的效能。
- **問題**:
  - `_run_bound_tests` 的去重鍵是 (root, 展開後指令),所以每支綁定測試各跑一次 `npx vitest run -t <名>`。
  - 預設序列執行(`_bound_tests_parallel` 預設 1)。
  - 每次都要啟動 Vite 並載入所有測試檔做收集(`-t` 只過濾測試,不過濾檔案)。
  - 這是 jest 骨架本來就有的成本,新計劃讓 Vite 專案一律走這條,而且 `node-vitest` 一旦加進 `_RAN_EVIDENCE`,就不再走「一次冒煙測試」那條省時路。
- **具體例**:
  - order-web 實測:9 個測試檔,單次 760ms。
  - 一個 100 個測試檔的專案,單次可能到 10 秒以上,40 支綁定測試序列跑就是 400 秒以上,超過 `LUMOS_TEST_TIMEOUT` 預設 180 秒的單支上限不會觸發,但整體閘會讓人等很久。
  - 上面的 10 秒是推估,不是實測。
- **處理**:計劃至少該寫出這個成本,並指到 `bound_tests.parallel` 這個既有出路。`vitest run` 本身不會進 watch 模式。子程序由 `_kill_run` 的程序群組在逾時時一起收掉,沒有孤兒問題。
- **佐證**:
  - file: `scripts/lumos:54388` 的 `_run_bound_tests` 把去重鍵設成 `(root, cmd)`。
  - file: `scripts/lumos:54579` 的 `_bound_tests_parallel` 預設回 1。
severity: minor
- blocking: 否。這是文件精度問題:成本不會讓實作做錯,但讀者不知道預算。

## 已讀無 finding 的部分

- **F2/W2 判棧拆分**:`_node_flavor_of` 本來就只讀一份 package.json,結果快取在 `_NODE_FLAVOR_CACHE`,不會多讀。
- **react 七題觸發樣式**:都是線性比對。`_stack_applicability` 的 `over` 門檻會讓超過 300 行的情況跳過逐行比對。
- **W7 eslint 偵測**:只看根目錄 12 個固定檔名,沒有掃樹。
- **init 的 vitest 判定**:只看根目錄,而且只在 init 跑一次。
- **子程序收尾**:沒有新增子程序,`_kill_run` 的程序群組回收沿用,`npx vitest run` 的 worker 會一併被收掉。
- **記憶體**:輸出已由 `_kill_cap` 在 256KB 截斷。

最嚴重 severity:major。blocking 共 1 條(F1)。
