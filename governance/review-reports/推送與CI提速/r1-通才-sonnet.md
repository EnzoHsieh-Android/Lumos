severity: major

我逐節讀完整份 spec,並對照 `Word-wild-search-ci` 的程式與筆記查證。「已讀,無 finding」的節:PRIOR-ART 與 RETIRE-IF 外的外部連結沒有逐一開啟,此外頂端 frontmatter 的 `related` 與 `lands_in` 目標(`Projects/CI加速_計劃`、`世界解重新註解2026-10_總覽_調研`、`Systems/bound-tests-gate`、`Systems/測試假綠形態`)都存在。「回退」一節除下面幾條外也無 finding。

**固定席判定(對照 `推送與CI提速_計劃` 節點宣稱的行為與合約)**
- 這份 spec 與同名計劃節點一致,不破壞該節點的行為宣稱。
- 它與既有 `Projects/CI加速_計劃` 的 `WHY:不做「推到主線時,同一棵檔案樹已在合併請求跑綠就不重跑全套」` 有張力。spec 以「比同一個提交」重新設計,但沒有列出要翻案、改寫那條 WHY。判「不破壞但漏同步」,見 finding 9。

- finding 1
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
