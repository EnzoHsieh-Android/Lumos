severity: major

**說明**:設計大方向走對了:子指令接在 `cohort` 旁、錯誤處理與 JSON 輸出沿用既有做法、驗證筆記作廢寫法合乎慣例。有一條 major,是計劃把工具改成執行目標 repo 程式碼,卻沒處理工具文件宣告的唯讀不執行。

**問 1:子指令放進 `review_convergence.py` 合乎它的定位嗎?**

結論:骨架合乎,定位文字需要更新。

- 骨架合乎。`cohort` 已經讀同一份帳、取 `code-` 開頭的迴圈、排除 `spec-gate`、用 token 去重。
  - file: `governance/eval/review_convergence.py:169-185`
  - 子指令分派、`DataError` 轉 rc 2、`render_json` 輸出,都在 `main()` 裡。
  - file: `governance/eval/review_convergence.py:540-577`
- 但這個工具自述是「唯讀、有界的證據收集與成對試行比較」。
  - file: `governance/eval/review_convergence.py:1`
  - 工具說明也寫「不執行模型、測試或檔案中的命令」。
  - file: `governance/eval/review_convergence.md:3`
- `repair-size` 是觀察性迴歸(Mantel-Haenszel、邏輯迴歸、bootstrap)。這跟成對試行的因果比較是兩種性質,而且需要純標準函式庫自寫迴歸。
- 計劃的 `lands_in` 與「做」那節都沒列要更新 `governance/eval/review_convergence.md`。該檔是 `Systems/review-convergence-eval` 的 `about_code`,責任句寫的是「審查帳衍生資料集、案例來源及試行證據比較」。
  - file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:1-20`
- 結構是對的,所以不算 major。

引句:「本 repo 既有的收斂評估工具 `review_convergence.py` 已有讀帳與 JSON 輸出的骨架,回放接成它的子指令,不另開一支工具。」
severity: minor
blocking: 否
落點對、定位沒跟著更新。子指令寫成後,`review_convergence.md` 的子指令清單與「不執行命令」那句、Systems 節點的 `responsibility` 都要同步。迴歸類的數字也要沿用該文件「不證明因果」的口吻。

**問 2:從 eval 工具載入 `scripts/lumos` 讀簿記常數,是跨層或第二種做法嗎?**

結論:載入本身有先例,但這份設計的載入條件造成一個跟工具定位衝突的新做法。

- 先例有,但全是載入本 repo 自己的主程式:
  - `k1_stop_replay.py` 用 `SourceFileLoader` 載入 `_HERE.parent.parent.parent / "scripts" / "lumos"`,並 import `_estimate_remaining_defects`。
    - file: `governance/eval/k1_stop_replay.py:7-15`
  - `home_audit.py` 載入主程式;`--lumos` 外部路徑還特地收窄到專案內。
    - file: `governance/eval/home_audit.py:38-49`
  - `retrieval_eval.py` 與 `refresh_labels.py` 是「目標 repo 有 vendored `scripts/lumos` 就用它,否則回退本體」。
    - file: `governance/eval/retrieval_eval.py:14`
    - file: `governance/eval/refresh_labels.py:101`
- 計劃寫的是載入 `<repo 根>/scripts/lumos`,而 repo 根是命令列參數。這會用 `exec_module` 執行任意 repo 根底下的程式。這跟下面兩處都衝突:
  - `review_convergence.py` 的讀檔紀律:`read_bytes` 拒絕符號連結與非一般檔、設大小上限。
    - file: `governance/eval/review_convergence.py:19-43`
  - 工具文件「不執行…檔案中的命令」「應用固定的可信本機檔案」。
    - file: `governance/eval/review_convergence.md:3`
- `exec_module` 還會載入一個九萬行級的主程式,載入失敗是計劃自己列的 rc 2 路徑。
- 這個工具從來沒載入過任何主程式,所以是第一個。
- 計劃要的只是兩個常數,加上它自己手寫的「新增行逐行序列比對」。
  - `scripts/lumos` 已有 `_CANARY_SCOPE_SOFT_CAP_LINES = 1800`。計劃的文字另寫 1800,又自創 600 與 5000 兩個門檻,沒說明跟既有常數的關係。
    - file: `scripts/lumos:13271`
  - 凍結 patch 的檔名解析已有 `_patch_files_from_text` / `_patch_file_changes`。計劃沒提,看起來是另寫一套 `+++` 解析。
    - file: `scripts/lumos:26671-26681`
  - 新增行已有 `_diff_added_lines`,但它回傳 `{檔: 行號集合}`,不是內容,所以內容比對確實得自己寫。
    - file: `scripts/lumos:29423`
- 載入來源不同於本 repo 時,簿記判準會隨目標 repo 版本漂,跟「消費專案帳」的對比分析會混版本。計劃沒寫。

引句:「簿記判準直接載入 `<repo>/scripts/lumos` 讀 `_BOOKKEEPING_FILES` 與 `_BOOKKEEPING_DIRS`(同 `scripts/test_lumos.py` 載入主程式的做法),不在工具裡另抄一份;載入失敗 rc 2。」
severity: major
blocking: 是
照字面做,一支宣告「只讀、不執行」的工具,會對命令列給的任意 repo 根 `exec_module` 其 `scripts/lumos`。這是專案裡原本沒有的第二種做法:既有先例載入的是本 repo 自己的主程式(`k1_stop_replay`、`home_audit` 還限制路徑在專案內)。修法有兩條:
- 固定載入本 repo 的 `scripts/lumos`,跟 `k1_stop_replay` 一樣。
- 明示放寬工具的唯讀定位,並限定在專案內。

另外要說明為何不重用既有的 patch 檔名解析與 1800 常數。

引句:「超過 5000 行(重定基底)的輪排除並列在 `skipped`。」
severity: minor
blocking: 否
600 與 5000 是新的魔術數字,1800 已有常數。若採固定載入本 repo 主程式,可以直接讀既有常數;否則把三個數字放成工具頂部具名常數,並在 `RETIRE-IF` 或說明裡寫清楚它們跟 1800 軟上限的關係。

**問 3:手冊建議、門檻說明落點與驗證筆記改寫,有沿用慣例嗎?**

結論:大致沿用,有兩處落點小偏差。

- 單元測試包裝沿用既有做法。一個 `t_review_eval_*` 呼叫 `_review_convergence_unit_group`,以子行程跑 `test_review_convergence.py` 的某個類別,逾時 90 秒。
  - file: `scripts/test_lumos.py:90876-90898`
  - 計劃的 `t_review_eval_repair_size` 與 `RepairSizeTests` 合此慣例。
  - S3 的 90 秒也是對齊該逾時,但目前 `repair-size` 帶 500 次 bootstrap 的邏輯迴歸,測試要靠 `--bootstrap 50` 才進得了。這是 minor,可見設計已意識到。
- 手冊建議的落點對。
  - 凍結材料是第 1 步,1800 行拆審的說明也在同一行。
    - file: `skills/lumos-code-loop/SKILL.md:19`
  - 「細節與依據放 `reference.md`」也合乎入口頁與 reference 的分工。
    - file: `skills/lumos-code-loop/reference.md:232-233`(1800 軟上限已在 reference 有段落,出處放在歷史段)
    - file: `skills/lumos-code-loop/reference.md:547-548`
- 驗證筆記作廢的寫法沿用既有格式:`WHY: [status:superseded] … [被取代:…]`。
  - file: `docs/lumos-toolchain-knowledge/Systems/ablation-lumos-first.md:64`
  - 計劃 S7 對應這個格式,沒問題。
- 現行驗證筆記還有 `REVISIT:2026-11-03`,綁在要作廢的那條 WHY(量「連 minor 一起折」佔修補行數多少)上。作廢後它指向的前提一起消失,但計劃沒說要不要一起處理。
  - file: `docs/lumos-toolchain-knowledge/Verification/2026-10-14_修補大小與下一輪major回放.md:55`
- 入口頁不寫日期與事故這條,現況入口頁並沒有守住:`SKILL.md` 步驟 1 和步驟 5 已經帶事故與卷證路徑。
  - file: `skills/lumos-code-loop/SKILL.md:20`
  - file: `skills/lumos-code-loop/SKILL.md:49`
- 所以計劃寫「入口頁不寫日期與事故」是約定而非現況。手冊那一行只要不帶日期就合此約定。

引句:「`reference.md` 那段一句話講清三個數字各管什麼:600 行是建議開審前拆案、1800 行是單席審材上限(超過拆開審)、5000 行是回放時排除重定基底。」
severity: minor
blocking: 否
落點偏差。`reference.md` 已有兩處講 1800(軟上限段與歷史出處段),新增一句講三個數字會變成第三處散落。
- 應把 600 寫進那一個既有的「一輪能丟多少」段,或明寫以哪一處為單源。
- 5000 是回放工具的內部排除值,不是手冊規則。放進手冊會讓讀手冊的人誤以為是審查規則;建議留在子指令說明或 `review_convergence.md`。

引句:「舊的「併進修復穩定性試行」那行 WHY 標成作廢、指向本計劃;內嵌腳本拿掉。」
severity: minor
blocking: 否
作廢那行 WHY 的同一篇還有 `REVISIT:2026-11-03`,它的前提(併進試行)一併失效。應在 S7 或「做」那節寫明一起改掉或標結案,否則 doctor 到期會唸一條已無依據的回頭條件。

不對齊共 4 條,其中 major 1 條。

涉及的主要檔案(絕對路徑,均在 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/` 下):
- `governance/eval/review_convergence.py`
- `governance/eval/review_convergence.md`
- `governance/eval/k1_stop_replay.py`
- `governance/eval/home_audit.py`
- `scripts/test_lumos.py`
- `skills/lumos-code-loop/SKILL.md`
- `skills/lumos-code-loop/reference.md`
