severity: major

彙總載體,非新增審查席。31 條由四份原報告逐字彙整,只在每條 severity 行前加 ID 行。


來源:r1-通才-sonnet.md


我逐節讀完整份 spec,並對照 `Word-wild-search-ci` 的程式與筆記查證。「已讀,無 finding」的節:PRIOR-ART 與 RETIRE-IF 外的外部連結沒有逐一開啟,此外頂端 frontmatter 的 `related` 與 `lands_in` 目標(`Projects/CI加速_計劃`、`世界解重新註解2026-10_總覽_調研`、`Systems/bound-tests-gate`、`Systems/測試假綠形態`)都存在。「回退」一節除下面幾條外也無 finding。

**固定席判定(對照 `推送與CI提速_計劃` 節點宣稱的行為與合約)**
- 這份 spec 與同名計劃節點一致,不破壞該節點的行為宣稱。
- 它與既有 `Projects/CI加速_計劃` 的 `WHY:不做「推到主線時,同一棵檔案樹已在合併請求跑綠就不重跑全套」` 有張力。spec 以「比同一個提交」重新設計,但沒有列出要翻案、改寫那條 WHY。判「不破壞但漏同步」,見 finding 9。

- finding 1
ID: t1
severity: major
blocking: 是
判準:不改,實作者會去改一個不存在的「合併步驟」,S5 的人工驗收也無法執行。
spec 段落:「做法」第三條,以及 S5。
引句:「代碼審手冊(`skills/lumos-code-loop/SKILL.md` 第 8 步與 `lumos-project-notes/commands/06-代碼審與推送.md`)的合併步驟改寫成這樣」
問題:兩份手冊都沒有「合併步驟」可改。
佐證:
- file: `skills/lumos-code-loop/SKILL.md:54` 第 8 步是「過了留痕」:先 impact、凍結、`code-loop pass`、只准提交帳本、推送、`ci-wait`。其中沒有任何合併或按鈕合併的敘述。
- file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:7` 只有表格一格提到「合併請求合進主線時…合併提交本身不手改」,整份沒有「合併步驟」小節。
- 這句 7 行的合約文字是在描述合併提交與留痕的關係,快轉後前提就變了(沒有合併提交)。spec 沒要求改它。
建議:spec 要明寫「新增一個第 9 步」或「改哪一格」。同時說明快轉後上述「合併提交不手改」的前提怎麼處理。

- finding 2
ID: t2
severity: major
blocking: 是
判準:不改,實作者照字面寫出來的 `concurrency` 會讓主線某次推送的 CI 被取消,與 spec 自己的承諾相反。
spec 段落:「做法」取消過期 CI 與「實務隱患」併發。
引句:「取消只作用在同一個 PR 分支的舊工作,主線永遠跑完。」
問題:
- GitHub `concurrency` 即使 `cancel-in-progress: false`,同群組內「排隊中的舊工作」仍會被新工作取代。主線若用固定群組,兩次連續推送時中間那次可能被直接取消,那次的後盾閘就不跑了。
- 主線群組鍵必須含 `github.sha`,讓每次推送自成一組。
- spec 只說「群組照事件與分支分開」,沒指定鍵。
- PR 群組若用 `github.head_ref`,不同來源(fork)同名分支會互相取消;應含 PR 號。
佐證:file: `.github/workflows/ci.yml:1` 目前完全沒有 `concurrency`,所以這是新增的行為,沒有既有慣例可抄。

- finding 3
ID: t3
severity: major
blocking: 是
判準:不改,第一階段交付後,「每個提交全套只跑一次」的目標並未達成,使用者還可能更慢。
spec 段落:白話摘要、「範圍」④、「做法」最後一條。
引句:「推 main、tag 或明示環境變數時才跑全套。」
問題:
- 合併改成 `git push <remote> <頂端提交>:main`,本機推送前掛鉤對推 main 一律走全套。
- 非 main 分支推送的全套是下一階段才改的。
- 所以第一階段的實況是:分支推送本機全套,加上 PR 的 CI,再加上推 main 時本機又一次全套(只省了主線 CI 的全套)。總次數沒有降到一次。
- spec 的白話段把三次降為一次當賣點,卻沒承認第一階段做不到。
佐證:file: `scripts/hooks/pre-push:629` 一帶以 `LUMOS_TEST_SHARDS` 預設 4 片跑全套,沒有「此提交已在同一分支測過就略過」的路徑。
建議:第一階段要嘛一併讓推 main 的掛鉤對「已推過且綠」的提交略過,要嘛把目標說成「只省主線 CI」。

- finding 4
ID: t4
severity: major
blocking: 是
判準:不改,實作者會在 `skip` 這個新值的流向上踩到既有判斷,多半被改回 `full`,或在 gates 的自主迴圈步驟誤判。
spec 段落:「做法」第三條第二點與 S4。
引句:「有就把範圍判成 `skip`,shards 不跑,gates 照跑」
問題:既有 prep 的 `suite` 步驟末尾強制收斂為兩值,`skip` 一產生就會被洗掉。
佐證:
- file: `.github/workflows/ci.yml:84` 這一行是 `[ "$suite" = docs ] || suite=full`。
- file: `.github/workflows/ci.yml:145` gates 的自主迴圈測試只認 `docs`,其餘一律跑全部。`skip` 時 gates 會跑全量自主迴圈測試,與「只省 shards」意圖不衝突但 spec 沒說。
- 文件子集步驟的條件也只認 `docs`。
- `skip` 與 `docs` 同時成立時(純文件的推送,而且它的 PR 也綠)優先序沒定。
- 現有守衛 `t_ci_yml_matrix_and_gates_shape` 鎖了「後盾指令逐字相同」與 `needs.prep.outputs.suite == 'full'`。改 prep 步驟與權限(`actions: read`)會動到它,spec 沒列出要同步改這支測試。

- finding 5
ID: t5
severity: minor
blocking: 否
判準:不改,風險是測得不夠,不會做出壞系統,但「保守方向多跑」只由人眼守。
spec 段落:S4 與「實務隱患」API 查詢。
引句:「查不到、API 失敗、權限不足一律跑全套。」
問題:
- 這句是整個略過機制最關鍵的保守分支,但 S4 綁的 `t_ci_yml_speed_shape` 只能讀 YAML 形狀,測不到判斷邏輯(回傳為空、非 JSON、權限 403、有多筆結果、run 為 cancelled 或 failure 時要走哪邊)。
- 邏輯塞在 workflow 內聯 bash 裡,幾乎無法單測。
- 建議抽成 `scripts/lumos` 子指令吃假 API 回應,並比照 `claude` 手冊「實作測試品質」寫翻紅釘(例如 API 回傳 `conclusion: failure` 時必須判成 `full`)。

- finding 6
ID: t6
severity: minor
blocking: 否
判準:不改,撤除條件量不出來;但退場條件本身寫得不可驗,不影響實作正確性。
spec 段落:白話摘要、現況、RETIRE-IF。
引句:「最快一份 4.9 分、最慢 9.1 分」
問題:
- 現況同一節自己承認單份耗時 CI 沒印。引句為:「單份耗時 CI 沒印,量不到,只看得到每台」。
- 所以白話段的每份數字來源不明,與現況段數字(每台 6.1–14.3 分)互相矛盾。
- RETIRE-IF 說「最慢一份…縮短 1 分鐘以上」,但 spec 沒有任何一條要求 CI 開始印每份耗時。上線後仍量不到,撤除條件無法判定。
- 另外 CI 以每台兩份並行跑(`matrix.shards: "1 2"` 這種寫法),LPT 平衡的是份,瓶頸卻是機器的兩份總和。若要看成效,量測單位應是「每台」。
佐證:file: `.github/workflows/ci.yml:117` 目前的 matrix 以 `"1 2"`、`"3 4"` 成對配機器。

- finding 7
ID: t7
severity: minor
blocking: 否
判準:不改,實作者會自行決定這些細節,最壞是分得不平均,不會漏跑。
spec 段落:「做法」依耗時分片的耗時來源。
引句:「把各支實測秒數寫進 `.lumos/test-durations*.json`」
問題:
- 現有的 `SLOWEST` 計時只在測試正常跑完時才記錄。例外、逾時、跳過(`_SrcOnly`)的測試沒有秒數。
- 用 `-k` 或 `--suite` 只跑子集時,各檔只含子集。
- 「取最近一次」沒說多個 `test-durations*.json`(各片與不同 N 的檔,例如 `shard1of4` 與 `shard1of16`)怎麼合併,用 mtime 還是什麼順序。
- 耗時從開發機(macOS,索引程序干擾,兩片並行)取,拿去分 Linux CI 的片,系統差異會讓表偏。
- 現有快取目錄的讀取是 glob `test-cache*.json` 一次全吃,舊 N 的殘檔會一直留著。
- 寫進版控的 `scripts/test-durations.json` 每次刷新都是一次提交,會觸發全套 CI,也沒說多久刷新一次。
佐證:file: `scripts/test_lumos.py:39301` 是快取檔名規則(依 `--shard` 字串命名)。file: `scripts/test_lumos.py:39308` 起是用 glob 讀全部快取的寫法。

- finding 8
ID: t8
severity: minor
blocking: 否
判準:不改,實作者會自行補邊界。
spec 段落:「做法」、S2。
引句:「表讀不到或壞掉就退回現行的照名字輪流分,並印一行說明。」
問題:
- 「壞掉」只該涵蓋非 JSON。形狀不對的有效 JSON(陣列、值是字串、負數、`NaN`)、空表、鍵值全是已刪除的測試名,都沒定義。
- 「表中位數」是針對表內所有項目,還是只算本次測試清單裡有紀錄的?兩種算法在各片之間一致,但實作者可能挑錯。
- 各片「分法一模一樣」要求所有片讀到同一份表。CI 各台各自 checkout 同一個提交,這點成立。但請在 S1 補一條「同一個提交下各片結果一致」的測試輸入,而不只靠 spec 內文宣稱。

- finding 9
ID: t9
severity: minor
blocking: 否
判準:不改,是治理帳的簿記漏洞,不影響功能。
spec 段落:現況第三條與 frontmatter `lands_in`。
引句:「使用者 2026-10-14 裁定同意改這條」
問題:
- 被改掉的是 `Projects/CI加速_計劃` 裡一條有四欄理由的決策(`WHY:不做「推到主線時,同一棵檔案樹…」`),應走 `lumos decision-add` 並標示翻案。
- spec 只在散文中提「裁定同意」,`lands_in` 也沒有 `Projects/CI加速_計劃`。
- 新檔 `scripts/test-durations.json` 與新旗標也沒指明哪個 Systems 節點管它,CLAUDE.md 鐵則 5 要求每支檔有家。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/CI加速_計劃.md:17` 是那條 WHY。

- finding 10
ID: t10
severity: minor
blocking: 否
判準:不改,是對先前根因的過度宣稱,不影響實作。
spec 段落:現況第三條。
引句:「PR 直接測分支頂端那個提交,合併用快轉,主線的提交就是被測過的那一個,歷史也一樣,正好消掉那次的根因」
問題:
- `測試假綠形態` 那條 PITFALL 記錄的根因與修法是 `_lens_smallest_commit`,屬於測試範圍的選法,與 PR 測的是哪個提交無關。這條已經修過,並綁了 `t_lens_tests_avoid_branch_dependent_range` 防再發。
- 該 PITFALL 的同族條目又說明還有其他測試拿「主線..HEAD」當範圍。改測分支頂端,這類測試的輸入會變:`git branch --track main origin/main` 之後 main 領先於 HEAD,範圍成了反向或空。spec 沒盤點這些測試。
- 「快轉前必須已含最新主線」只在合併時由 git 擋;PR 的 CI 跑的當下分支仍可能落後,這些範圍型測試在 PR 的 CI 上結果可能和主線不同。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:25`。

- finding 11
ID: t11
severity: minor
blocking: 否
判準:不改,可能讓治理帳出現誤報,不致做出壞系統。
spec 段落:「做法」取消過期 CI。
引句:「只有 PR 事件 `cancel-in-progress`,推到 main 不取消。」
問題:被取消的 PR 舊工作會以 `cancelled` 結束。`lumos ci-wait` 與 `ci-status` 要進治理帳,而 SKILL.md 第 8 步規定:「rc0 不等於綠 … 紅燈當輪修」。spec 沒說被取消的舊 run 如何被這兩個指令視為「已被新推送取代」而不是紅燈或 `undetermined`。
佐證:file: `skills/lumos-code-loop/SKILL.md:60` 是 ci-wait 的語意說明。

**實務隱患逐類**
- 併發:有隱患,見 finding 2(主線排隊中的工作會被取代、PR 群組鍵沒含 PR 號)與 finding 11(被取消的 run 與 ci-wait 的語意)。
- 效能:LPT 分片本身 O(n log n) 且確定性,無問題;只是平衡成效看 finding 6、7 的量測與耗時來源。
- 資源:每次推 main 多一次 API 呼叫(`GITHUB_TOKEN` 額度綽綽有餘),無新隱患。
- 回滾:刪表即退回輪流分、還原 YAML 即回原狀,成立。唯一缺口是 ff 合併已執行後 PR 被標已合併,沒有「回退合併」的步驟,但這屬 git 層面可 revert,不阻塞。

blocking 共 4 條(finding 1 至 4),全份最嚴重等級為 major。

來源:r1-邊界失效-sonnet.md


審查範圍:逐節讀 `/tmp/推送與CI提速-r1.md`,對照 `.github/workflows/ci.yml`、`scripts/test_lumos.py` 的 `--shard` 段和 `scripts/hooks/pre-push`。模擬腳本在 `/tmp/lumos-seat-work/推送與CI提速/邊界失效-sonnet/sim.py`。

**固定席逐條判:會不會破壞節點宣稱的行為或合約**
- 「各片聯集等於全部」的現行行為:有影響,見 F1。現行切法靠排序位置,每片獨立決定;改成讀檔後,各片能不能算出同一分法,取決於表的讀取結果。
- 「`--list` 排在所有篩選之後」:不影響。spec 沒動篩選順序;但 spec 沒寫新分法放在 `-k` 之前還是之後,見 F7。
- 「快取只在來源 repo 寫」:不影響。spec 的 `.lumos/test-durations*.json` 沿用同一條件,而且實測值在跑完測試後取得。
- 「`--suite` 子集在分片之前挑、空片算過」:不影響,spec 明寫保留。但 F4 的全零耗時會讓整個子集都落進同一片。
- 「主線永遠跑完、gates 照跑」:有影響,見 F2、F3。

ID: e1
severity: major
blocking: 是
F1 各片讀到不同的表時,聯集不再等於全部,而且是靜默綠。spec 的保證只靠「同一份表、同一份測試清單,各份算出來的分法一模一樣」,但各片是獨立行程,各自讀檔。
- 重現條件:本機推送前掛鉤同時起 4 片,其中一片讀表失敗,其他片讀成功。例如表在跑的當下被 `git checkout`、rebase,或別的會談改動(`scripts/hooks/pre-push:676` 起的並行迴圈)。
- 結果:讀失敗的片退回照名字輪流分,其他片用耗時分法,有的測試跑兩次,有的一次都沒跑。
- 現行程式的註解(`scripts/test_lumos.py:39286` 附近)記過同型事故:各片讀到的快取不同,聯集不等於全部。spec 的退回規則反而重新開了這個洞。
- 只有「表讀不到」這一條分支需要每片獨立降級,其他分支不用。
- 建議:每片在輸出與 `--json-summary` 裡印表的雜湊、測試總數和分到幾支;彙總的一方驗證所有片的雜湊一致、分到的支數總和等於總數。

引句:「同一份表、同一份測試清單,各份算出來的分法一模一樣,所以各份聯集仍等於全部、沒有重複。」

ID: e2
severity: major
blocking: 是
F2 主線 `concurrency` 不取消進行中的 run,但 GitHub 會把「排隊中」的舊 run 換掉,所以「主線永遠跑完」不成立。
- 重現條件:同群組有一個 run 在跑,main 上又連續推兩次。第二次的 run 在排隊,第三次一到,第二次的 run 就被取消。`cancel-in-progress: false` 不管排隊中的 run。
- 後果:被取消的那個提交,全套和 gates 都沒跑。gates 裡有 `--no-verify` 繞過的唯一後盾,也就是 `ci.yml:176` 的 code-loop gate。
- 疊加主線略過:該提交若有成功的 PR run,連全套的後盾也沒有;若沒有,就是零檢查。
- 建議:push 事件的群組帶 `github.sha`(每個提交各自一組),只有 PR 事件才用分支群組。

引句:「併發:取消只作用在同一個 PR 分支的舊工作,主線永遠跑完。」

ID: e3
severity: major
blocking: 是
F3 「PR 測的是同一個提交」只對齊了提交編號,沒有對齊執行環境,2026-10-04 那類「PR 綠、主線紅」的根因類別沒有消除。
- 依據:PR 事件的 `ci.yml:29-30` 把本機 `main` 追蹤到 `origin/main`,也就是 PR 的底。推到 main 之後,本機 `main` 是含該提交的新頂端。再加上 PR 是 detached HEAD(checkout `head.sha`),主線是在分支上。
- 結果:凡是讀 `main@{upstream}`、`merge-base`、當前分支名、「主線頂端與前一個提交」的測試(`scripts/test_lumos.py:20512`、`:44524`、`:44644` 都用 `main@{upstream}`),兩邊看到的範圍不同。
- 影響:略過後,主線上唯一那次「提交已在主線上」環境的全套被拿掉。
- 缺口:RETIRE-IF 寫「略過的主線提交在之後的重跑裡變紅」,但略過的提交沒人會去重跑,這條永遠觀測不到。
- 建議:至少在 PR 的 CI 裡讓本機 `main` 與分支名模擬 ff 之後的狀態,或把略過的條件加上「沒有測試依賴 `main@{upstream}`」的機械檢查。

引句:「這篇不比檔案樹,改成比「同一個提交」:PR 直接測分支頂端那個提交,合併用快轉,主線的提交就是被測過的那一個,歷史也一樣,正好消掉那次的根因」

ID: e4
severity: major
blocking: 是
F4 耗時為 0 時,貪婪分法會把所有零耗時測試丟進同一片,空片和失衡同時出現。
- 重現條件:表的值四捨五入、大多數測試記成 0.0。我用 `sim.py` 模擬,規則照 spec:由大到小,丟給總秒數最少的片,同總秒數取編號小的。
- 結果:100 支測試(10 支 5 秒、90 支 0 秒)切 4 片,各片支數是 `[3, 3, 92, 2]`。新增 40 支未知測試且表中位數是 0 時,變成 `[3, 3, 132, 2]`。
- 原因:加 0 不改變總秒數,所以每次都選同一片。
- 後果:一片過載,又在「測試不比片數少」的全套下可能出現空片擋下(rc 1)。`--suite` 子集下空片算過,等於靜默少跑。
- 中位數的問題不限於零:表中絕大多數測試很快,中位數遠小於真實平均,新增的重測試永遠被低估。
- 建議:所有權重加下限(例如 `max(t, 0.05)`),並讓平手時用已分到的支數當第二關鍵字。

引句:「表裡沒有的測試以表中位數計;表讀不到或壞掉就退回現行的照名字輪流分,並印一行說明。」

ID: e5
severity: major
blocking: 是
F5 耗時表進版控後,誰更新、何時更新、更新提交觸發什麼,spec 全沒定義,而且會踩到別的閘。
- 事實:`scripts/test-durations.json` 不在 `_DOCS_ONLY_PATHS` 裡(`scripts/lumos:44930` 的白名單只含 README、docs/、assets/、governance/ 等),所以只改這支檔的推送在 CI 跑全套,在掛鉤也不判成純文件。
- 推論(未實跑):專案規則是「代碼審留痕綁版本,通過後只准再提交帳本」,一份剛過審的分支再提交耗時表,留痕就失效。直接推 main 更新表則是 12 分鐘全套換一份資料檔。
- 本機實測來源也有問題。`--refresh-durations` 合併 `.lumos/test-durations*.json`,多個片檔案各有不同的 n、跑在不同提交;「取最近一次」的粒度沒定義。本機 Mac 四片並行的秒數,也不等於 CI 上 ubuntu 兩片同機的秒數。
- 另有兩個記錄缺口:`SLOWEST.append` 在 `scripts/test_lumos.py:39361`,只在 `run_with_timeout` 正常返回時才記;逾時、拋例外、`_SrcOnly` 跳過的測試都不進表,而最慢的測試恰恰最可能逾時。這些測試永遠用中位數估,等於最需要被分平均的那批永遠沒有正確權重。
- 建議:寫明更新時機(例如只在每日治理或專用流程做)、更新提交的類型,並讓「只改這支檔」被判成低風險。

引句:「新增旗標 `--refresh-durations` 把這些合併進 `scripts/test-durations.json`(取最近一次,沒跑到的保留舊值)。」

ID: e6
severity: minor
blocking: 否
F6 表「合法 JSON 但形狀不對」沒涵蓋,實作容易直接崩潰。
- 重現條件:表是 `{}`。用 `statistics.median` 時 `StatisticsError: no median for empty data`(我實跑過)。`[]`、值是字串、`null`、負數或 `NaN` 也同理。
- 後果:這些是合法 JSON,不會觸發「讀壞」分支,可能整支 `--shard` 在每一片都以例外退出。這是大聲失敗,不是靜默,所以列 minor。
- 建議:S2 的驗收明列這些形狀,一律退回輪流分,而且各片要得出同一結論(見 F1)。
- 消費專案沒有表時走「不存在」分支,每片各印一行說明,功能無虞。

引句:「當耗時表不存在或讀壞時,`--shard` 應 退回照名字輪流分並印一行說明」

ID: e7
severity: minor
blocking: 否
F7 spec 沒定義新分法放在 `-k`、`--suite`、`--ff`、`--seed` 的哪個位置。
- 現行程式的順序是:`--suite` 先篩,再切片,再 `--ff` 重排,再 `--seed` 打亂,最後 `-k` 篩選(`scripts/test_lumos.py:39265` 到 `:39330`)。
- 風險一:實作者若把 `-k` 提到切片前,`-k` 選中 0 支的行為(退出碼 1)會和現行不同。現行測試用 `--shard i/n -k zzz` 讀「分到 N 支」那行(`:21770`)。
- 風險二:`--suite` 子集下,中位數該用全表還是子集算,要寫明。實作兩種都能自洽,但各片必須一致(見 F1)。
- 建議:在 S1 補一句「分片發生在 `--suite` 之後、`-k` 之前,中位數用全表」,並在 `t_runner_shard_by_duration` 加一條 `--suite keys` 與 `-k` 的組合斷言。

引句:「`--shard i/n` 讀耗時表:照秒數由大到小、同秒數照名字」

ID: e8
severity: major
blocking: 是
F8 主線略過的 API 查詢規則沒有明確定義,誤判和權限的靜默失效沒有守衛。
- 權限:`ci.yml:12` 全域只給 `permissions: contents: read`。不加 `actions: read`,查詢永遠 403,一律跑全套,功能「上線」了卻永遠沒生效,也不會有任何警示。S4 只是文字形狀測試,抓不到這種情況。
- 一個提交對應多個 run 時,spec 只說「已成功完成」,沒定義取哪一個:
  - 同一 `head_sha` 有成功、有失敗的 run(重新開啟 PR、重跑)時,「任何一個成功」就略過。
  - 該成功 run 若是舊版 workflow 檔跑的,略過的覆蓋範圍可能比現在少。
  - 進行中、被取消(例如被新推送的 `cancel-in-progress` 取消)的 run 不是成功,這一條 spec 的保守方向是對的,但規則要寫進條款。
- PR 來自 fork:fork 提交的 `head_sha` 一樣會被查到成功 run,但它是 fork 的受限權限跑的(無 secrets,需人工核准),跟 main 上跑的環境不等價。spec 對 fork 一句未提。
- 需補的:查詢條件(`event=pull_request`、`conclusion=success`、最新 attempt、`head_repository` 等於本 repo),以及「略過」要在日誌裡印出依據的 run id,方便事後核對。

引句:「查不到、API 失敗、權限不足一律跑全套。」

ID: e9
severity: minor
blocking: 否
F9 取消過期 CI 的群組鍵要考慮 fork 同名分支與 re-run。
- 重現條件:兩個 fork 的 PR 都用同名分支(例如都叫 `main` 或 `patch-1`),若群組鍵只用 `github.head_ref`,彼此會互相取消對方的 CI。
- 另外,有人手動重跑舊 run,可能被剛推的新 run 取消。
- 建議:群組鍵含 `github.event.pull_request.number`,不要只用 `head_ref`。

引句:「`ci.yml` 加 `concurrency`,群組照事件與分支分開;只有 PR 事件 `cancel-in-progress`,推到 main 不取消。」

最嚴重等級 major,blocking 共 5 條(F1、F2、F3、F4、F5、F8 中的 F1、F2、F3、F4、F5、F8,實為 6 條:F1、F2、F3、F4、F5、F8)。更正:blocking 為「是」的共 6 條,minor 3 條(F6、F7、F9)。

來源:r1-平台語意-sonnet.md


我沒能做到的事先講:Bash 守衛擋了 `gh api`,所以 Actions 紀錄、`branches/main/protection` 與 rulesets 我都沒查到。下面的平台宣稱只有「讀 spec 與 `ci.yml`」和「已知的 GitHub 文件行為」當佐證,凡是沒實測的我都標明。

**1. PR 與主線測的環境不同,「消掉 2026-10-04 根因」的說法不成立**

ID: p1
severity: major
blocking: 是

引句:「正好消掉那次的根因(使用者 2026-10-14 裁定同意改這條)」

- 該 PITFALL 的根因是測試取「主線 tip 與 tip~1」當範圍(file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:25`)。
- 測試找主線靠 `main@{upstream}`(file: `scripts/test_lumos.py:17987`、`:40886`、`:41006`)。
- PR 事件 checkout `head.sha` 時,`ci.yml` 的「補本機 main」步驟(`git branch --track main origin/main`)補出來的 `main` 是舊的基底頂端,不是被測提交。
- 所以 PR 的 CI 看到的「主線 tip、tip~1」是基底與基底的父提交。
- 快轉後主線 tip 才變成被測提交,tip~1 才是舊基底,範圍並不相同。
- 測試若用 `main..HEAD` 當範圍,PR 裡是整個 PR,快轉後主線上是空範圍。
- 被測提交的 SHA 相同,但「測試看到的 git 環境」不同。這類依賴主線位置的測試,PR 綠不保證主線綠。
- 這正是 spec 想靠略過主線重跑來省掉的那一次風險。
- 建議:
  - 要嘛 PR 的 CI 把本機 `main` 補成「被測提交的父提交」,模擬快轉後的狀態。
  - 要嘛列舉所有讀主線位置的測試,證明它們對這個差異不敏感。
  - 否則 RETIRE-IF 的「主線重跑變紅」會在上線後才被踩到。

**2. 主線的排隊中 run 會被後來的 run 取消**

ID: p2
severity: major
blocking: 是

引句:「只有 PR 事件 `cancel-in-progress`,推到 main 不取消。」

- `cancel-in-progress: false` 並不等於「不取消」。
- GitHub 文件規定同一個 concurrency 群組裡「已排隊(pending)的 run 會被新的取代」,只有進行中的 run 受 `cancel-in-progress` 管。
- 文件:https://docs.github.com/en/actions/using-jobs/using-concurrency
- 若主線群組只用「事件加分支」,連推三次 main 時,第二次推送的 run 會被第三次取消。
- 那個提交就沒有任何主線 CI,後盾閘(code-loop、note-shape、drift check)也沒跑。
- 這和「併發:取消只作用在同一個 PR 分支的舊工作,主線永遠跑完」直接矛盾。
- 現況的 `ci.yml` 完全沒有 concurrency,所以不會發生;spec 加進去才引入。
- 建議:push 事件的群組鍵要帶 `github.sha`(或 `github.run_id`),讓每個主線 run 各自一組。
- 另外,`cancel-in-progress` 寫成 `${{ github.event_name == 'pull_request' }}` 語法可行。
- 但群組鍵要把 PR 與 push 分開,PR 用 `github.head_ref`。`github.ref` 在 PR 事件是 `refs/pull/N/merge`,也可以,只是 spec 沒寫清楚用哪個。

**3. 「查同一提交已成功的 PR run」缺少條件,無法保證那次跑過全套**

ID: p3
severity: major
blocking: 是

引句:「查同一個提交(`head_sha` 等於這次推送的提交)有沒有已成功完成的 PR 事件 CI;有就把範圍判成 `skip`」

- 可用的端點是 `GET /repos/{o}/{r}/actions/runs?head_sha=…&event=pull_request&status=success`,另有 `workflow_id` 與 `branch` 可篩。pull_request run 的 `head_sha` 是 PR 分支頂端,不是合成合併提交,這點與 spec 一致。
- 但 spec 沒寫以下區分:
  - **篩 workflow**:不篩 `workflow_id` 或路徑,同 SHA 上別的 workflow 的成功 run 也會命中。
  - **篩目標分支**:基底不是 main 的 PR(例如疊在另一個分支上的 PR),同一個 SHA 會有 run,但測的是別的基底。
  - **確認真的跑了全套**:`conclusion=success` 只代表整個 run 成功。
    - 目前 `ci.yml` 對 PR 事件永遠判 `full`,所以暫時成立。
    - 但 spec 沒要求去查那個 run 的 jobs,確認 shards 的結論是 success 而不是 skipped。
    - 日後若 PR 也開了文件子集或 `skip`,誤判不會被察覺。
  - **重跑**:`run_attempt` 重跑失敗的 job 後,run 的結論是最新一次的結果,多次 run 取哪一個沒規定。
  - **取消的 run**:被取消的 run 結論是 `cancelled`,`status=success` 已排除,這點沒問題。
- 權限:`ci.yml` 頂層是 `permissions: contents: read`,其餘權限全為 none,所以 prep 必須明確加 `actions: read`,spec 有提到。
- 另一點:`GITHUB_TOKEN` 查 API 的失敗(含 rate limit)一律跑全套,這個保守方向是對的。
- 建議:條款 [S4] 補上篩 workflow 檔名、`base`/`branch`、查 jobs 的 shards 結論,並規定同一 SHA 多個 run 時「只要有一個 run 的 shards 全數 success 就算」。

**4. `git push <sha>:main` 會讓 PR 自動變已合併,但它不是文件保證,主線保護也未驗**

ID: p4
severity: minor
blocking: 否

引句:「GitHub 會自動把 PR 標成已合併」

- 實務上,分支頂端提交進了基底分支,GitHub 會把開啟中的 PR 標成 merged,這是長期已知的行為。
- 但官方文件沒有逐字保證,而且只對「PR 仍開啟、基底是 main」成立。
- 我沒能查 `branches/main/protection` 與 rulesets(`gh` 被擋)。
- 若主線有保護(要求 PR、要求狀態檢查),直接推 main 會被拒。
- 反之沒保護,spec 也沒說要不要保留「PR 綠才准推」的機械擋,這步完全靠手冊紀律。
- 建議:spec 加一條上線前實測的驗收(開 PR、快轉推、看 PR 狀態與 `merged_at`)。

**5. 推 main 的本機 pre-push 全套會讓「全套只跑一次」打折**

ID: p5
severity: minor
blocking: 否

引句:「推 main、tag 或明示環境變數時才跑全套。」

- 這句是下一階段才交付。
- 但本階段的快轉就是「推 main」,現行掛鉤對非輕量改動會再跑一次本機全套(spec 現況寫約 5 到 10 分)。
- 所以本階段實際是本機一次、PR 的 CI 一次、快轉時本機又一次。
- 另外掛鉤是否正確解析 `<sha>:main` 這種「來源不是分支名」的 refspec,spec 沒說。
- 建議:至少寫明這是已知的暫時狀態,並加上「回頭條件」。

**6. 其他平台語意的查證結果**

ID: p6
severity: minor
blocking: 否

- **`github.sha` 的殘留用法**:`ci.yml` 裡的 `SHA: ${{ github.sha }}` 只出現在 push 事件才執行的步驟(prep 的範圍判斷用在 `github.event_name = push` 的分支裡、gates 的四個 push 步驟)。
  - 改測 `head.sha` 後 PR 事件沒有任何步驟還在用合成合併提交,「補本機 main」「文件子集判斷」「code-loop gate」都不受影響。
  - 這部分我判不影響,理由是它們全都被 `if: github.event_name == 'push'` 圍住。
- **快轉後主線提交就是被測提交**:`git push` 快轉不會改寫提交,所以主線的 SHA 與 PR 的 `head_sha` 相同。
  - 這是 git 的語意,GitHub 不會改寫。只有按鈕的 squash 或 rebase 合併才會產生新 SHA。
  - 該 SHA 上的 check 本來就掛在提交上,因此不是問題。
- **checkout 行為**:`actions/checkout@v4` 在 `fetch-depth: 0` 且 `ref: <head.sha>` 時,取出的是分離 HEAD。
  - 同 repo 的 PR 分支 SHA 都可由 `refs/heads/*` 抓到,不會壞。
  - 分離 HEAD 會讓 `--branch`、`git rev-parse --abbrev-ref HEAD` 類的呼叫行為與現況不同,值得跑一次確認。
  - 這些在目前 `ci.yml` 裡只出現在 push 事件的步驟。
- **「先 rebase 再推再等 CI」會形成追逐**:rebase 會換 SHA,舊 PR 的 CI 結果對新 SHA 作廢,主線每動一次就要重等約 12 分。
  - 單人場景影響小,spec 的「由 git 擋」說法成立。

最嚴重等級:major;blocking 共 3 條(第 1、2、3 條)。

來源:r1-架構對齊-sonnet.md


整體說法:分層與依賴方向大致對得上,有一處在 CI 範圍判定上另立第二套做法。以下分四問回答。

## 問 1 分層與依賴方向
- 分片:既有切法是執行器內一行 `k % _n`(`scripts/test_lumos.py:39278`)。推送前掛鉤和 CI 都只靠 `--shard i/n` 旗標呼叫執行器(`scripts/hooks/pre-push:682`、`.github/workflows/ci.yml:109`、`.github/workflows/ci.yml:128`)。設計把分法換成讀耗時表,依賴方向不變,對得上。
- CI 範圍判定:既有做法是 yaml 只把 `lumos pitfalls --json` 算出的 `suite` 轉交,判斷邏輯在 lumos,yaml 只收 full/docs 兩值(`.github/workflows/ci.yml:52`、`.github/workflows/ci.yml:70`)。同一個 `suite` 輸出又被 shards(`.github/workflows/ci.yml:86`)和 gates 拿去用。設計把 `skip` 判定直接寫在 prep 的 shell 裡查 GitHub API,不走 lumos。判定邏輯從 lumos 搬到 yaml,這就是下面的 finding 1。

## 問 2 命名與錯誤處理
- 旗標名 `--refresh-durations` 是 kebab-case,跟 `--json-summary`、`--keep-tmp` 同風格(`scripts/test_lumos.py:39210`、`scripts/test_lumos.py:39220`)。命名本身沒問題。
- 執行器既有旗標都只改「這次怎麼跑」(`-x`、`--ff`、`--seed`、`--shard`、`--suite`,見 `scripts/test_lumos.py:39212` 到 `scripts/test_lumos.py:39222`)。`--refresh-durations` 卻會改寫進版控的檔案。
- 本機落地檔 `.lumos/test-durations*.json` 沿用 `test-cache*` 的命名、`_is_src` 條件(`scripts/test_lumos.py:39298`)和先寫暫存再 rename 的原子寫法(`scripts/test_lumos.py:39400` 附近),三項都一致。但 `.gitignore:35` 只列了 `.lumos/test-cache*.json`,設計沒說要補忽略規則。
- 讀表失敗的處理跟既有快取不同:既有快取讀壞時 `except (OSError, ValueError): pass`,靜默略過(`scripts/test_lumos.py:39308`)。設計改成「退回輪流分並印一行說明」。這個差異有道理,但見 finding 3。

## 問 3 第二種做法
- CI 查「同一個提交有沒有成功的 CI」:`scripts/lumos:46279` 的 `cmd_ci_wait` 已經在查 CI 執行紀錄(含 sha、結論、fail-open)。設計在 ci.yml 內另寫一套查詢。
- 測試狀態檔:耗時表的落地沿用 `.lumos/*.json`,沒有另立一套寫法,對得上。
- 合併方式:`skills/lumos-project-notes/commands/06-代碼審與推送.md:7` 現在描述的是「合併請求合進主線、合併提交」的情境。設計要改成快轉,是明講的取代,不算第二種做法。要改的不只第 8 步(`skills/lumos-code-loop/SKILL.md:54`),06 的第 7 行也要同步。

## 問 4 落點
- `Systems/bound-tests-gate` 的 `about_code` 列了 ci.yml 和 pre-push,已有 CI 拆工作與分片的 WHY/KEY(行 17、行 41)。concurrency、skip、分片改法該寫在這篇,合理。
- `Systems/測試假綠形態` 是 `scripts/test_lumos.py` 的家(`about_code`),但主題是假綠形態,跟耗時分片不同題。「改到哪支檔就寫進它的家」的規則照樣要求在這篇留一句,主文不適合放這裡。
- 新檔 `scripts/test-durations.json` 沒有家,`lands_in` 也沒列。
- 要被翻案的舊決策是 `Projects/CI加速_計劃` 的「不做檔案樹相同就不重跑」那條 WHY,設計沒把這篇放進 `lands_in`。

## Findings

1. 範圍判定另立第二套做法(⚠ 偏重,判不準是 major 還是 minor)
ID: a1
severity: major
blocking: 是
引句:「推到 main 時,prep 用 GitHub API 查同一個提交」
說明:既有 prep 的 `suite` 判定在 lumos 內(`.github/workflows/ci.yml:52`),CI 查詢也已有 `scripts/lumos:46279`。設計把 skip 判定和 API 查詢直接寫進 yaml 的 shell,等於 `suite` 一個輸出有兩套來源。建議把「同一提交已有成功 PR CI」做成 lumos 子指令,yaml 只轉交,並復用 ci-wait 的查詢。

2. 耗時表放 `scripts/`,偏離既有資料檔位置
ID: a2
severity: minor
blocking: 否
引句:「測試耗時表放新檔 `scripts/test-durations.json`」
說明:`scripts/` 底下版控的非程式檔只有 hooks、templates、vendor。進版控的資料檔既有位置是 `.lumos/`(config.json、lint.json)和 `governance/`(anchor-baseline.json)。另外 `.gitignore:35` 沒涵蓋 `.lumos/test-durations*.json`。

3. 讀表退回的處理,跟既有「各片聯集必須等於全部」的處理方式不一致
ID: a3
severity: minor
blocking: 否
引句:「表讀不到或壞掉就退回現行的照名字輪流分,並印一行說明。」
說明:`scripts/test_lumos.py:39317` 到 `scripts/test_lumos.py:39325` 的註解記過:各片是獨立行程,讀到的狀態可能不同,聯集就會錯。設計是每片各自決定要不要退回,只要有一片讀失敗、其他片沒失敗,就會混用兩種分法。建議讓分法判定只吃一個所有片都會得到同樣結果的輸入(例如只在表格式驗證通過才用,並在 CI 先驗一次)。

4. `--refresh-durations` 的性質跟其他旗標不同
ID: a4
severity: minor
blocking: 否
引句:「新增旗標 `--refresh-durations` 把這些合併進 `scripts/test-durations.json`」
說明:這個旗標改寫版控內的檔案,其餘執行器旗標都只影響這次怎麼跑。⚠ 若要沿用「改版控基準要有簽名動作」的做法,更新耗時表宜走 lumos 子指令。這點只是提示,判不準。

5. 落點不全
ID: a5
severity: minor
blocking: 否
引句:「Systems/測試假綠形態」
說明:耗時分片的主文放這篇會離題。建議主文寫進 `Systems/bound-tests-gate`(改它的行 17、行 41),`測試假綠形態` 只留指標。新檔 `scripts/test-durations.json` 要有家(新開一篇很小的 Systems 節點,或掛進 bound-tests-gate 的 `about_code`)。`lands_in` 要補上 `Projects/CI加速_計劃`,並用 `lumos decision-add` 記翻案。

不對齊共 5 條,其中 major 1 條
