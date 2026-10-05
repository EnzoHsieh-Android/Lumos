severity: major

# CI加速 r1 外部審稿:邊界與失敗情境

總評:跳過全套的判準本身(合併請求已合併、合併提交等於推送頂端、檔案樹指紋一致、任何錯誤一律 false)在我能想到的情境下都落在安全方向,首推、force-push、tag(ci.yml 只聽 main 分支,tag 推送不觸發)、草稿、fork、關閉未合併都不會讓全套被錯跳。真正會做出錯行為的是「新拆出的工作沒有逾時規定」。其餘是措辭與缺口。

## 情境逐項(照 spec 字面做會怎樣)

- 首推/force-push/BEFORE 全零:prep 現有那步在對不到起點時 suite=full,再進 ci-reuse;只有樹指紋一致才跳過。安全。
- tag 推送:file: `.github/workflows/ci.yml:6`(只有 branches: [main])不觸發,無事。
- fork 合併請求:mark 不跑、ci-reuse 查不到狀態,主線照跑全套。安全。
- 草稿合併請求:照常觸發 pull_request、mark 照寫;合併時 merged_at 與 merge_commit_sha 照判。安全。
- 合併請求關閉未合併:merged_at 為空,ci-reuse 回 false。安全。
- GitHub API 回空陣列/分頁/限流:全部落到「查不到=false=跑全套」。安全(只是失去加速)。
- 空份:子集配分片空份回 0、非子集空份回 1,見 finding 3。
- CI 機器被砍/逾時/只跑一半:matrix 工作 cancelled 或 failure,`mark` 的 `needs: shards` 不成立所以不寫狀態,下游不跳過。安全;但逾時值本身見 finding 1。

## Finding 1
severity: major
blocking: 是——照 spec 字面實作,四個新工作沒有逾時上限,卡死的工作要等到 GitHub 預設 360 分才被砍,而 prep 在最前面,卡住就整條 CI 都不動。
引句:「離工作上限 45 分只剩約 7 分」
spec 全文只拿「45 分上限」當動機,從頭到尾沒有任何一句規定 `prep`、`shards`、`gates`、`mark` 各自的 `timeout-minutes`。現行單一工作有顯式 45 分(file: `.github/workflows/ci.yml:12`);拆成四個工作後,每個工作各自適用預設值 360 分。具體失敗:`prep` 裡的 `gh api` 或 `pip install ruff` 掛住(GitHub 限流/慢/網路半死),下游 `shards`、`gates` 全 `needs: prep`,整次 CI 在 prep 卡數小時;`lumos ci-wait` 預設 1800 秒就回「逾時未定」(file: `scripts/lumos:39257`,rc0、不算過),人得手動查,而卡住的工作還占著機器。反過來若實作者照舊把 45 抄到每個工作,matrix 份工作又沒有「依實測最慢份 ×2」的依據。要補的條款:`prep` 約 10 分、`shards` 依〈做法〉0 實測最慢份的約 2 倍(目標 10 分、上限不超過 25)、`gates` 約 20 分(自主迴圈 63 秒+doctor+錨點)、`mark` 約 5 分;並寫進 [S3] 讓測試釘住每個工作都有 timeout-minutes。

## Finding 2
severity: minor
blocking: 否——prep 的 ci-reuse 步驟在例外或卡住時的行為沒寫,但落在多跑/紅燈方向;不會漏測。
引句:「`gh` 不在、沒有 token、網路錯、JSON 看不懂,都算 false。」
這句列舉的是已預期的失敗,[S2] 也只測這三種。沒有涵蓋:Python 例外(例如 API 回的是物件而非陣列、欄位型別不對)導致指令非零,而 spec 要求「回傳碼一律 0」;以及 `gh` 無逾時掛住。若 prep 那步因此非零,prep 紅,整次主線推送 CI 紅(假紅),且 ci-wait 會記成逃逸。已有現成輪子:file: `scripts/lumos:39167` 的 `_ci_gh` 預設 60 秒逾時並把逾時轉成 (None,…);ci-reuse 應明寫重用它,且 ci.yml 那一步加 `|| echo reuse=false` 當第二道。另外 prep 怎麼讀 `reuse=true`(讀 stdout 哪一行)沒寫:原因文字若夾帶 `reuse=true` 字樣,鬆散比對會誤判為真,要求嚴格比對整行開頭並由 [S1] 加一條「原因文字含 reuse=true 字樣仍判 false」的測試。

## Finding 3
severity: minor
blocking: 否——純文件推送搭配 matrix 不會漏測也不會誤紅,只是更慢、更貴;但 spec 沒有交代。
引句:「多台機器同時跑,每台跑一份或幾份」
純文件推送(suite=docs)文件子集約 66 支、四組同時跑 38 秒(file: `scripts/test_lumos.py:50864` 附近的註解)。spec 的 `shards` 對 docs 也展開成 4 到 8 台,每台各付 checkout(fetch-depth: 0)+裝 Python 的約 1 分鐘,加上前面串行的 prep,純文件推送的牆鐘時間反而比現在單一工作更長,還多占 8 個並行額度(公開 repo 同時 20 台,數個合併請求同時跑會排隊)。空份處理本身沒問題:子集配分片空份回 0(file: `scripts/test_lumos.py:33368`),66 支分 8 份每份都有東西;非子集空份回 1 只會在 N 大於全部測試數時發生,3700 支不會。要補的是:docs 時 matrix 縮成一台跑 `--suite docs` 不切份(或接受變慢並寫進〈天花板〉),並且 [S3] 加一條「suite=docs 時切份數不得超過子集大小」(防日後有人把 N 調到 100 以上、子集縮小後某份靜默空過卻不被抓)。

## Finding 4
severity: minor
blocking: 否——實驗只量一次會選到偶然快的組合,正式 CI 抖動時才超過上限;影響是目標沒達成,不是守衛被繞。
引句:「選最快、又不超過 10 分鐘的那組」
2026-09 到 10 月同一套全套測試在 CI 上從 32 漲到 38.5 分,代表共享機器的耗時抖動是兩位數百分比。〈做法〉0 兩組各量一次就選,單次樣本可能把偶然快的組合當成最優,正式推上去最慢份 11 到 12 分就違反 [S4]。⚠ 抖動幅度沒實測:驗證方法是實驗分支每組至少跑 3 次(用 workflow_dispatch 或空提交重推),取最慢份的最大值而不是平均值來比 10 分。

## Finding 5
severity: minor
blocking: 否——權限寫法有兩種讀法,字面照做的那種比意圖寬;寫狀態的權限要靠主線寫入權本來就有的信任,沒有新增可被利用的門,但多給了測試步驟不需要的寫入權。
引句:「`mark` 寫狀態要用;其他工作只讀」
同一條說「workflow 加 `permissions:`」(整份層級),又說其他工作只讀,兩者矛盾:整份層級宣告 `statuses: write` 時 `shards`(執行合併請求上的程式碼,同 repo 分支的合併請求)也拿到寫狀態權限,測試過程中任何腳本都能對自己的頭提交寫出 `lumos/full-suite-tree` success。同 repo 寫入者本來就能改 ci.yml,所以不是新的越權,但最小權限應該是整份層級只給 `contents: read`、`pull-requests: read`,`statuses: write` 只寫在 `mark` 的工作層級,[S3] 順手釘住。

## Finding 6
severity: minor
blocking: 否——只影響紅燈後的診斷資訊品質與逃逸帳的歸因,不影響通過與否。
引句:「每台各自印失敗片段,GitHub 介面上每個 matrix 工作分開看。」
`lumos ci-wait` 紅了抓的是整個 run 的 `gh run view --log-failed` 尾 40 行再截 4000 字(file: `scripts/lumos:39224`)。拆成多個工作後,同時有多份紅或 gates 也紅時,尾 40 行只會是排在最後的那個工作的輸出,真正的失敗斷言(在 shards 某一份)進不了帳也印不出來。`_ci_failed_step`(file: `scripts/lumos:39206`)會把所有 failure 步驟串起來,多一個 `gates` 紅就讓「是不是測試紅」的判斷被別的工作影響。⚠ 工作層級 `continue-on-error: true` 的 `mark` 在 jobs API 裡 conclusion 是 failure 還是 success 我無法確定:驗證方法是在實驗分支故意讓 mark 的 gh api 失敗,跑 `gh run view <id> --json jobs` 看 steps 與 job 的 conclusion;若是 failure,只要同一輪另有紅就會把 mark 的步驟名混進失敗步驟。

## Finding 7
severity: minor
blocking: 否——跳過全套用的是合併請求當時跑綠的結果,時間相依測試過期時晚一步才被抓到,不會永久漏。
引句:「合併請求跑完後主線又被推進別的東西,合併結果的樹就不同,照跑全套」
spec 的新鮮度只看檔案樹,沒有時間上限。情境:合併請求某日全套綠,主線三週沒動,三週後合併,樹一致而跳過全套;若測試裡有隨日期到期的斷言(⚠ file: `scripts/test_lumos.py` 裡有約 99 處時間函式呼叫,哪些是真依賴今天日期而不是造假資料我沒逐一查),那次主線推送應該紅卻是綠,下一次不相關的推送才紅。驗證方法:`grep -n "date.today\|datetime.now" scripts/test_lumos.py` 逐處看是否拿今天去比對 repo 內容的到期日;若有,在 ci-reuse 加上「狀態 `created_at` 超過 7 天就回 false」一條並補進 [S1]。另外 ⚠ `commits/<sha>/pulls` 與合併提交欄位在合併後數秒內可能尚未更新,屬於安全方向的 false,不用處理,只需在上線後第一次主線推送日誌留意。

總結:全份最高等級 major
