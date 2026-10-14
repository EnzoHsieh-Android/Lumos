severity: major

審查範圍:逐節讀 `/tmp/推送與CI提速-r1.md`,對照 `.github/workflows/ci.yml`、`scripts/test_lumos.py` 的 `--shard` 段和 `scripts/hooks/pre-push`。模擬腳本在 `/tmp/lumos-seat-work/推送與CI提速/邊界失效-sonnet/sim.py`。

**固定席逐條判:會不會破壞節點宣稱的行為或合約**
- 「各片聯集等於全部」的現行行為:有影響,見 F1。現行切法靠排序位置,每片獨立決定;改成讀檔後,各片能不能算出同一分法,取決於表的讀取結果。
- 「`--list` 排在所有篩選之後」:不影響。spec 沒動篩選順序;但 spec 沒寫新分法放在 `-k` 之前還是之後,見 F7。
- 「快取只在來源 repo 寫」:不影響。spec 的 `.lumos/test-durations*.json` 沿用同一條件,而且實測值在跑完測試後取得。
- 「`--suite` 子集在分片之前挑、空片算過」:不影響,spec 明寫保留。但 F4 的全零耗時會讓整個子集都落進同一片。
- 「主線永遠跑完、gates 照跑」:有影響,見 F2、F3。

severity: major
blocking: 是
F1 各片讀到不同的表時,聯集不再等於全部,而且是靜默綠。spec 的保證只靠「同一份表、同一份測試清單,各份算出來的分法一模一樣」,但各片是獨立行程,各自讀檔。
- 重現條件:本機推送前掛鉤同時起 4 片,其中一片讀表失敗,其他片讀成功。例如表在跑的當下被 `git checkout`、rebase,或別的會談改動(`scripts/hooks/pre-push:676` 起的並行迴圈)。
- 結果:讀失敗的片退回照名字輪流分,其他片用耗時分法,有的測試跑兩次,有的一次都沒跑。
- 現行程式的註解(`scripts/test_lumos.py:39286` 附近)記過同型事故:各片讀到的快取不同,聯集不等於全部。spec 的退回規則反而重新開了這個洞。
- 只有「表讀不到」這一條分支需要每片獨立降級,其他分支不用。
- 建議:每片在輸出與 `--json-summary` 裡印表的雜湊、測試總數和分到幾支;彙總的一方驗證所有片的雜湊一致、分到的支數總和等於總數。

引句:「同一份表、同一份測試清單,各份算出來的分法一模一樣,所以各份聯集仍等於全部、沒有重複。」

severity: major
blocking: 是
F2 主線 `concurrency` 不取消進行中的 run,但 GitHub 會把「排隊中」的舊 run 換掉,所以「主線永遠跑完」不成立。
- 重現條件:同群組有一個 run 在跑,main 上又連續推兩次。第二次的 run 在排隊,第三次一到,第二次的 run 就被取消。`cancel-in-progress: false` 不管排隊中的 run。
- 後果:被取消的那個提交,全套和 gates 都沒跑。gates 裡有 `--no-verify` 繞過的唯一後盾,也就是 `ci.yml:176` 的 code-loop gate。
- 疊加主線略過:該提交若有成功的 PR run,連全套的後盾也沒有;若沒有,就是零檢查。
- 建議:push 事件的群組帶 `github.sha`(每個提交各自一組),只有 PR 事件才用分支群組。

引句:「併發:取消只作用在同一個 PR 分支的舊工作,主線永遠跑完。」

severity: major
blocking: 是
F3 「PR 測的是同一個提交」只對齊了提交編號,沒有對齊執行環境,2026-10-04 那類「PR 綠、主線紅」的根因類別沒有消除。
- 依據:PR 事件的 `ci.yml:29-30` 把本機 `main` 追蹤到 `origin/main`,也就是 PR 的底。推到 main 之後,本機 `main` 是含該提交的新頂端。再加上 PR 是 detached HEAD(checkout `head.sha`),主線是在分支上。
- 結果:凡是讀 `main@{upstream}`、`merge-base`、當前分支名、「主線頂端與前一個提交」的測試(`scripts/test_lumos.py:20512`、`:44524`、`:44644` 都用 `main@{upstream}`),兩邊看到的範圍不同。
- 影響:略過後,主線上唯一那次「提交已在主線上」環境的全套被拿掉。
- 缺口:RETIRE-IF 寫「略過的主線提交在之後的重跑裡變紅」,但略過的提交沒人會去重跑,這條永遠觀測不到。
- 建議:至少在 PR 的 CI 裡讓本機 `main` 與分支名模擬 ff 之後的狀態,或把略過的條件加上「沒有測試依賴 `main@{upstream}`」的機械檢查。

引句:「這篇不比檔案樹,改成比「同一個提交」:PR 直接測分支頂端那個提交,合併用快轉,主線的提交就是被測過的那一個,歷史也一樣,正好消掉那次的根因」

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

severity: major
blocking: 是
F5 耗時表進版控後,誰更新、何時更新、更新提交觸發什麼,spec 全沒定義,而且會踩到別的閘。
- 事實:`scripts/test-durations.json` 不在 `_DOCS_ONLY_PATHS` 裡(`scripts/lumos:44930` 的白名單只含 README、docs/、assets/、governance/ 等),所以只改這支檔的推送在 CI 跑全套,在掛鉤也不判成純文件。
- 推論(未實跑):專案規則是「代碼審留痕綁版本,通過後只准再提交帳本」,一份剛過審的分支再提交耗時表,留痕就失效。直接推 main 更新表則是 12 分鐘全套換一份資料檔。
- 本機實測來源也有問題。`--refresh-durations` 合併 `.lumos/test-durations*.json`,多個片檔案各有不同的 n、跑在不同提交;「取最近一次」的粒度沒定義。本機 Mac 四片並行的秒數,也不等於 CI 上 ubuntu 兩片同機的秒數。
- 另有兩個記錄缺口:`SLOWEST.append` 在 `scripts/test_lumos.py:39361`,只在 `run_with_timeout` 正常返回時才記;逾時、拋例外、`_SrcOnly` 跳過的測試都不進表,而最慢的測試恰恰最可能逾時。這些測試永遠用中位數估,等於最需要被分平均的那批永遠沒有正確權重。
- 建議:寫明更新時機(例如只在每日治理或專用流程做)、更新提交的類型,並讓「只改這支檔」被判成低風險。

引句:「新增旗標 `--refresh-durations` 把這些合併進 `scripts/test-durations.json`(取最近一次,沒跑到的保留舊值)。」

severity: minor
blocking: 否
F6 表「合法 JSON 但形狀不對」沒涵蓋,實作容易直接崩潰。
- 重現條件:表是 `{}`。用 `statistics.median` 時 `StatisticsError: no median for empty data`(我實跑過)。`[]`、值是字串、`null`、負數或 `NaN` 也同理。
- 後果:這些是合法 JSON,不會觸發「讀壞」分支,可能整支 `--shard` 在每一片都以例外退出。這是大聲失敗,不是靜默,所以列 minor。
- 建議:S2 的驗收明列這些形狀,一律退回輪流分,而且各片要得出同一結論(見 F1)。
- 消費專案沒有表時走「不存在」分支,每片各印一行說明,功能無虞。

引句:「當耗時表不存在或讀壞時,`--shard` 應 退回照名字輪流分並印一行說明」

severity: minor
blocking: 否
F7 spec 沒定義新分法放在 `-k`、`--suite`、`--ff`、`--seed` 的哪個位置。
- 現行程式的順序是:`--suite` 先篩,再切片,再 `--ff` 重排,再 `--seed` 打亂,最後 `-k` 篩選(`scripts/test_lumos.py:39265` 到 `:39330`)。
- 風險一:實作者若把 `-k` 提到切片前,`-k` 選中 0 支的行為(退出碼 1)會和現行不同。現行測試用 `--shard i/n -k zzz` 讀「分到 N 支」那行(`:21770`)。
- 風險二:`--suite` 子集下,中位數該用全表還是子集算,要寫明。實作兩種都能自洽,但各片必須一致(見 F1)。
- 建議:在 S1 補一句「分片發生在 `--suite` 之後、`-k` 之前,中位數用全表」,並在 `t_runner_shard_by_duration` 加一條 `--suite keys` 與 `-k` 的組合斷言。

引句:「`--shard i/n` 讀耗時表:照秒數由大到小、同秒數照名字」

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

severity: minor
blocking: 否
F9 取消過期 CI 的群組鍵要考慮 fork 同名分支與 re-run。
- 重現條件:兩個 fork 的 PR 都用同名分支(例如都叫 `main` 或 `patch-1`),若群組鍵只用 `github.head_ref`,彼此會互相取消對方的 CI。
- 另外,有人手動重跑舊 run,可能被剛推的新 run 取消。
- 建議:群組鍵含 `github.event.pull_request.number`,不要只用 `head_ref`。

引句:「`ci.yml` 加 `concurrency`,群組照事件與分支分開;只有 PR 事件 `cancel-in-progress`,推到 main 不取消。」

最嚴重等級 major,blocking 共 5 條(F1、F2、F3、F4、F5、F8 中的 F1、F2、F3、F4、F5、F8,實為 6 條:F1、F2、F3、F4、F5、F8)。更正:blocking 為「是」的共 6 條,minor 3 條(F6、F7、F9)。
