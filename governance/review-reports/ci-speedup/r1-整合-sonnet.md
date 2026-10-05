severity: major

# CI加速_計劃 r1 外部審稿(整合席,sonnet)

立場:三個月後接手的人,預設文件與現實對不上。唯讀,未改 repo 任何檔。對照物:`/Users/enzo/harness/lumos-ci-speed` 的 ci.yml、pre-push、scripts/lumos、圖譜筆記與 test_lumos.py。

白話一句:這份 spec 把一條流水線拆成並排的四條,再加一個「同一棵樹測過就不重測」的捷徑。拆線本身有現成的測試釘住、做得出來;捷徑的前提(樹一樣=結果一樣)repo 自己就有反例,而且捷徑一旦走了,它自己的失靈偵測器也跟著不會響。

## 範本問題的結論(使用者另問)

lumos 沒有整份 CI 範本給消費專案。scripts/lumos 裡只有三段「貼進既有工作的步驟片段」:note-shape(`_note_audit_doctor_lines` 與 note-shape doctor 區段內的 step 字串)、note-audit check、`_DRIFT_CI_STEP`;圖譜也明講「工具鏈也沒有分發任何 CI 樣板」。片段裡沒有測試切份、沒有 prep/shards 結構,所以拆工作與 `ci-reuse` 不需要同步到範本,rtb 那類專案維持單一工作照跑全套即可,不會因分岔壞掉。要守住的是另一條線:`_DRIFT_CI_STEP` 與 ci.yml 的 drift check 那步被測試逐字比對(`_dr_ci_bodies`),搬進 `gates` 後縮排與內容必須一字不變,否則比對測試紅。spec 沒有寫「範本不改」與理由,見 F8。

## Findings

### F1 樹指紋相同不等於測試結果相同,spec 對此斷言過頭
severity: major
blocking: 是 — 照字面實作會讓依賴提交歷史的測試在主線只剩合併前的一次驗證,spec 又宣稱保護沒少。
引句:「測試一條都不少,Linux 上跑的保護也還在。」
引句:「合併請求跑完後主線又被推進別的東西,合併結果的樹就不同,照跑全套」
spec 的判準只比樹。但 repo 內有測試的結果取決於提交圖而非檔案內容:`PITFALL:鏡頭逾時暖快取那支測試在主線合併一個大 PR 之後 CI 假紅` 的根因就是「範圍取主線 tip 與 tip~1」,同一棵樹、不同歷史,PR 事件綠、主線推送紅。另外 ci.yml 自己也承認 PR 事件與主線推送是不同環境(PR 取出的是不在分支上的合併提交,要補本機 main 才拉齊)。PR 事件的 HEAD 是 GitHub 造的測試合併提交,主線推送的 HEAD 是真合併提交,父提交與 `main@{upstream}` 都不同。所以「樹一樣就視為全套已驗」對這類測試不成立,spec 要嘛把這類測試列為不受跳過保護的已知缺口(寫進〈天花板〉),要嘛限定只在確認無歷史相依時跳過。
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:20`
file: `.github/workflows/ci.yml:23`
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:17`

### F2 撤除判準無法被觸發,跳過後 CI 帳也看不出這次沒跑全套
severity: major
blocking: 是 — spec 把這條當「判準失靈」的唯一偵測器,實際上跳過發生時它不會響。
引句:「主線推送跳過全套後,連續一季有任何一次」
跳過的那次主線推送根本沒跑 shards,工作結論只會是綠或被後盾紅,「主線紅、但同一棵樹的合併請求是綠」這個事件只會發生在沒被跳過(照跑)的推送上,也就是跟跳過無關的案例。也就是跳過所冒的風險(F1 那類)被跳過本身遮住。再者 `ci-wait` 記帳以工作層級結論為準(`_ci_list_runs` 取 run 的 conclusion,`_ci_failed_step` 只記失敗步驟),跳過的推送在 ci-log 裡是一筆普通的綠;三個月後的人看帳會以為主線每次都跑過全套。spec 要補:跳過時在帳或提交狀態留一筆可查詢的「skipped-reuse」,而且 RETIRE-IF 改成可觀測的事件(例如定期抽一次主線頂端強制跑全套比對)。
file: `scripts/lumos:39180`
file: `scripts/lumos:39206`

### F3 寫回圖譜範圍不足,而且與「後盾逐字不改」互相衝突
severity: major
blocking: 是 — 照字面實作後,圖譜與 ci.yml 會留下多句假話,且 spec 禁止改其中在 ci.yml 內的幾句。
引句:「後盾那幾步除了 `steps.suite.outputs` 改成 `needs.prep.outputs` 之外 應 跟拆分前逐字相同」
〈做法〉6 只列兩處(bound-tests-gate 的「切 4 片」那行、ci.yml 開頭 timeout 註解)。拆分後以下句子變假:
- ci.yml 的 drift check 步驟註解「全套測試在這步前面(既有安排,沒搬)」:拆分後 shards 與 gates 並行,沒有先後。這行在 `gates` 內、被 S3 要求逐字不變,改了測試紅,不改就是假話。spec 必須明講這行註解的處置。
- ci.yml 的 `LUMOS_SKIP_BOUND_TESTS` 註解「CI 已跑全套當後盾」:主線推送被跳過時,該次執行沒跑全套;bound-tests-gate 摘要的 KEY 行(CI 設該變數、CI 已跑全套)同樣不精確。
- bound-tests-gate 的「CI 的全套測試仍在它前面」那段 WHY,與同檔的純文件子集 KEY「CI 對 light 照跑全套當後盾」。
- 雙向門放行〈推送前與 CI 的測試範圍〉的「CI 仍跑全套當後盾」,與 Issues/合約測試閘只在高風險推送跑 內的 CI 說法。
這些筆記的家只有 bound-tests-gate 一篇列在 `lands_in`,其餘在別篇,spec 沒列,鐵則 5 要求改到的句子要在對應節點修。
file: `.github/workflows/ci.yml:165`
file: `.github/workflows/ci.yml:116`
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:32`
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:35`
file: `docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md:149`
file: `docs/lumos-toolchain-knowledge/Issues/合約測試閘只在高風險推送跑.md:38`

### F4 權限段自相矛盾:工作層級還是整份 workflow 層級沒定
severity: minor
blocking: 否 — 不會做錯功能,只是權限比 spec 自己宣稱的寬。
引句:「`statuses: write`(`mark` 寫狀態要用;其他工作只讀)」
〈做法〉5 寫「workflow 加 `permissions:`」,放在 workflow 層級時每個工作(含執行 PR 程式碼的 shards)都拿到 statuses 寫入,與「其他工作只讀」相反。要做到只讀,得在 `mark` 工作層級單獨提權,workflow 層級只留 `contents: read` 與 `pull-requests: read`。spec 的「有人偽造狀態」那條用「本來就能推主線」排除,同 repo 分支確實如此,但「其他工作只讀」的字面要改成可實作的寫法。

### F5 各工作的 timeout 與耗時目標沒有寫
severity: minor
blocking: 否 — 不寫會落到預設 360 分鐘,但不改變正確性。
引句:「目標:全套那一步在 10 分鐘內。」
現有唯一工作有 `timeout-minutes: 45`,註解掛在它身上。拆成四個工作後,spec 沒說 prep、shards、gates、mark 各自的 timeout;shards 卡住會燒到預設上限。〈做法〉0 也沒寫兩組實驗都超過 10 分鐘時怎麼辦(多加台數?放寬?)。
file: `.github/workflows/ci.yml:12`

### F6 S3 的「拆分前逐字」沒有基準,且「N 寫在同一處」在 matrix 做不到
severity: minor
blocking: 否 — 屬測試實作歧義,先紅後綠時會被迫補決定。
引句:「分份總數 N 寫在同一處」
兩點:①S3 要測「跟拆分前逐字相同」,但拆分後 repo 裡不再有拆分前的檔;測試得內嵌一份黃金文字或讀 git 歷史(`git show <提交>:.github/workflows/ci.yml`),spec 沒指定,而 `steps.suite.outputs` 改成 `needs.prep.outputs` 的替換規則也要寫進測試。②GitHub Actions 的 `strategy.matrix` 不能讀 `env` context,N 只能同時出現在 matrix 清單與步驟腳本兩處,「同一處」要改成「由 matrix 的一個欄位(例如每台帶 `n`)傳進腳本,S3 測它與清單一致」。另外 `skip_full` 在 PR 事件或 docs 範圍時 ci-reuse 那步不跑,spec 沒要求 prep 明確輸出 false,雖然 `!= 'true'` 剛好容錯,仍應寫明。

### F7 ci-reuse 取「頭提交」的來源沒定義,combined status 有分頁
severity: minor
blocking: 否 — 失敗方向是照跑全套,功能退化而非出錯。
引句:「`gh api repos/{repo}/commits/<頭提交>/status` 取 context `lumos/full-suite-tree`、state success 的那筆」
前一步 `commits/<sha>/pulls` 的回應裡 head.sha 才是頭提交,spec 沒寫從哪取。combined status 的 statuses 清單有預設分頁(30),若頭提交上別的 context 很多,目標那筆會落在第一頁之外,會永久判成沒有而無聲失效;應帶 per_page=100 或改查 `statuses` 端點取該 context 最新一筆。結果仍是 fail-safe,所以只算 minor。

### F8 spec 沒交代 CI 範本要不要改
severity: minor
blocking: 否 — 結論是不用改(見上方結論),缺的是 spec 裡的明文與守衛。
引句:「做:新指令 `lumos ci-reuse` 判斷主線推送可不可以不重跑全套(〈做法〉3)」
`ci-reuse` 會隨 scripts/lumos 分發給消費專案,但沒有任何範本呼叫它,沒有分岔風險。該寫進〈範圍〉的是:「不做:消費專案範本(只有步驟片段,不含測試切份)」,並指出唯一需要同步守住的是 `_DRIFT_CI_STEP` 與 ci.yml drift check 步驟的逐字比對測試,搬進 `gates` 時縮排不能動。不寫的話,三個月後有人看到 rtb 沒切份會當成漏改。
file: `scripts/lumos:36687`
file: `scripts/test_lumos.py:54874`
file: `docs/lumos-toolchain-knowledge/Issues/合約測試閘只在高風險推送跑.md:49`

### F9 推送前掛鉤與 CI 的分工沒寫,掛鉤訊息有幾句會變成半假
severity: minor
blocking: 否 — 掛鉤行為不變,只是提示文字與事實有落差。
引句:「推送前掛鉤與 CI 共用;純文件推送只跑文件子集」
掛鉤本機切 `LUMOS_TEST_SHARDS` 預設 4 份跑全套,是功能分支推送時的第一道;CI 在 PR 再跑一次,現在主線推送會被跳過。掛鉤提示「CI 會跑全套當後盾」「CI 還是會再跑一次」在合併後的主線推送上不一定成立。spec 沒說掛鉤的份數 4 與 CI 的 N 無關(兩邊測試快取檔名按份數分開,不衝突),也沒說掛鉤文案不改的理由,三個月後會有人懷疑兩邊要同步。
file: `scripts/hooks/pre-push:630`
file: `scripts/hooks/pre-push:672`
file: `scripts/hooks/pre-push:691`
file: `scripts/test_lumos.py:33388`

### F10 上線後人工確認沒有接電的回頭條件
severity: minor
blocking: 否 — 是治理格式缺口,不影響 CI 行為。
引句:「上線後第一次主線推送人工看日誌確認(〈實作紀錄〉記結果)」
專案鐵則 4 要求承認風險要附回頭條件、帶日期的寫成獨立一行 `REVISIT:YYYY-MM-DD ...`。spec 這句只有「第一次」沒有日期或事件入口,純散文沒人會回頭;S4 的手動驗收也同樣沒日期。同理 F2 的偵測缺口需要一行 REVISIT 掛上。

### F11 已確認可以照做、不構成問題的幾點(供接手者省時間)
severity: clean
blocking: 否 — 無需修改。
引句:「大約 9 支測試讀本 repo 真的 ci.yml(逐字比對步驟內容、步驟順序、縮排、`python-version`)」
實查 test_lumos.py 讀真 ci.yml 的測試有 9 處左右,數字屬實。檢查過的接線測試在 spec 描述的結構下仍會綠:`t_prepush_and_ci_wired_for_docs_suite` 的字串都還在檔案裡(含 `extra="$extra --graph"`、`test_autonomous_loop.py $extra`);drift check 與 reread 兩步維持相鄰(`i_ci_rr == i_ci_dr + 1`);`note-audit check` 字樣沒有出現;`_ci_jobs_calling_without_full_history` 以工作為單位檢查 fetch-depth,四個工作都設 0 即可。`_ci_step_is_test` 只看步驟名(「/」之後),shards 的步驟名保留「Full test suite」即仍被判為測試紅;spec 要求 mark 的工作名避開 test 字樣其實不必要,但無害。
file: `scripts/lumos:39398`
file: `scripts/test_lumos.py:58560`

總結:全份最高等級 major
