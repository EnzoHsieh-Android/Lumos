---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/bound-tests-gate
related:
  - "[[Systems/bound-tests-gate]]"
summary: |-
  WHY:CI 的全套測試拆給多台機器同時跑,並在推到主線、而且同一棵檔案樹已經在合併請求的 CI 跑綠時不重跑全套(後盾檢查照跑) [出處:Enzo 2026-10-06「CI 好慢,拖慢整個開發速度」「1 跟 2 一起做」] [因:全套在 CI 已從 2026-09-12 的約 10 分漲到 32–38.5 分,離工作上限 45 分只剩約 7 分;每個功能合併請求一次、主線推送又一次,光 CI 就 60–70 分] [不選:本機全綠就不等 CI 先合併(要改全域規則,Linux 才出的錯變成合併後才發現);只跑受影響的測試子集(覆蓋變少)]
---
# CI加速_計劃

白話:CI 慢在「全套測試」那一步——四份測試擠在同一台 GitHub 機器上,現在要 32 到 38.5 分鐘,工作上限是 45 分,快被砍了。這次做兩件事:①把全套拆給多台機器同時跑(CI 拆成準備、全套、後盾、記檔案樹四個工作);②推到主線時,如果同一棵檔案樹剛在合併請求的 CI 跑綠過,就不再重跑全套,只跑後盾檢查。測試一條都不少,Linux 上跑的保護也還在。

依據:Enzo 2026-10-06 對話裁定「1 跟 2 一起做」。repo 公開(GitHub 標準機器不另收費);主線沒有分支保護(改工作名稱不會卡合併)。

PRIOR-ART: GitHub Actions 的 `strategy.matrix` 把同一個工作分給多台機器(業界拆測試的標準做法,pytest-split、Jest `--shard` 同一招);「合併後不重跑已驗過的樹」對應 GitHub merge queue 與 Bors 的「測的就是要合進去的那棵樹」,本案用「比對檔案樹指紋」取代 merge queue(個人 repo 不開 merge queue)。同專案:測試執行器早有 `--shard i/n`(排序後輪流分配,`t_runner_shard_partitions_completely` 守聯集完整);推送前掛鉤與 CI 共用;純文件推送只跑文件子集([[Systems/bound-tests-gate]] 的 suite 機制)。
RETIRE-IF: 全套在 CI 的最慢一份連續一個月低於 5 分鐘、而且機器數已經降回 1 台就夠快,撤掉多台拆分;主線推送跳過全套後,連續一季有任何一次「主線紅、但同一棵樹的合併請求是綠」,撤掉跳過(判準失靈)。

## 範圍

- 做:CI 拆成四個工作——
  - `prep`(準備):編譯檢查、3.9 語法守衛、SyntaxWarning 閘、決定測試範圍,輸出 `suite`(full 或 docs)、`graph`(純文件推送裡有沒有圖譜筆記,有的話文件子集加 `--graph`)、`skip_full`(true 時不跑全套);
  - `shards`(全套測試):多台機器同時跑,每台跑一份或幾份;
  - `gates`(後盾):自主迴圈測試、健檢、代碼審留痕閘、筆記形狀閘、存量漂移檢查、回頭重讀提醒、錨點驗證;
  - `mark`(記檔案樹):合併請求事件、全套全綠後,在合併請求頭提交上寫狀態。
- 做:每個工作各自 `actions/checkout`(`fetch-depth: 0`)、合併請求事件補本機 main(`git branch --track main origin/main`)、裝 Python 3.14——工作之間不共用機器,以前靠同一台機器前一步留下的東西都要各自重做。
- 做:機器數與每台跑幾份,先用真的 CI 量出來再定(〈做法〉0)。目標:全套那一步在 10 分鐘內。
- 做:新指令 `lumos ci-reuse` 判斷主線推送可不可以不重跑全套(〈做法〉3);查不到、對不上、任何一步出錯一律跑全套。
- 不做:跳過後盾檢查(那幾道就是要抓 `--no-verify` 繞過的,主線推送照跑)。
- 不做:改測試執行器的切份演算法(輪流分配不保證每份耗時一樣,實驗量最慢那份)。
- 不做:Windows 機器上的 CI(另案)。
- 不做:開分支保護或 merge queue。

## 做法

0. **先量**:開實驗分支(只放實驗用的兩組 matrix,量完關掉不合併),試 8 台各跑 1 份(`--shard i/8`)、4 台各跑 2 份(同一台背景跑兩份 `--shard`)兩組,記下最慢那個工作的分鐘數與整次牆鐘時間;選最快、又不超過 10 分鐘的那組。量到的數字寫進本篇〈實作紀錄〉。
1. **拆工作**:
   - `prep`:現有的編譯類三步與「這次推送要跑哪個測試範圍」那步搬進來;用 job 層級 `outputs:` 輸出 `suite`、`graph`、`skip_full`。
   - `shards`:`needs: prep`、`if: needs.prep.outputs.skip_full != 'true'`、`strategy.matrix` 用一個清單列出每台要跑的份數編號(例:`shards: ["1 2", "3 4", …]`),`fail-fast: false`;每台照現在的寫法對自己那幾份背景同時跑、印失敗片段;分份總數 N 寫在同一處。
   - `gates`:`needs: prep`(不等 `shards`,兩者同時跑——以前全套紅了後面就不跑,現在後盾照跑,資訊變多);後盾那幾步照搬,★除了把讀前一步輸出的 `${{ steps.suite.outputs.* }}` 改成 `${{ needs.prep.outputs.* }}`,其他每一行逐字不改★;步驟順序照原樣(筆記形狀閘在錨點驗證之前、存量漂移檢查的下一步緊接回頭重讀提醒);不新增含「note-audit check」字樣的註解或步驟(既有測試與健檢靠那串判接線)。
   - 只在推送事件跑的幾步照留 `if: github.event_name == 'push'`。
2. **記檔案樹(`mark`)**:`needs: shards`、只在合併請求事件而且來源是同一個 repo(`github.event.pull_request.head.repo.full_name == github.repository`)時跑、`continue-on-error: true`(寫不進去不讓 CI 紅);checkout 合併請求事件取出的合併提交,算 `git rev-parse HEAD^{tree}`,用 `gh api` 對 `github.event.pull_request.head.sha` 寫狀態 context `lumos/full-suite-tree`、state success、description=檔案樹指紋。工作與步驟名稱避開「test」「測試」字樣(`ci-wait` 記帳時拿失敗步驟名判斷是不是測試紅)。
3. **`lumos ci-reuse --sha <推送頂端> --repo .`**(放 scripts/lumos,家是 [[Systems/bound-tests-gate]]):
   - `gh api repos/{repo}/commits/<sha>/pulls`,只認 `merged_at` 有值、`merge_commit_sha` 等於這個 sha 的合併請求(2026-10-06 實查:合併請求 #9 的 merge_commit_sha 就是主線上的 ce2a961f);
   - `gh api repos/{repo}/commits/<頭提交>/status` 取 context `lumos/full-suite-tree`、state success 的那筆;
   - 比對 description 與 `git rev-parse <sha>^{tree}`;
   - 全部成立印 `reuse=true` 與原因(含合併請求編號);任何一步失敗印 `reuse=false` 與原因;回傳碼一律 0。`gh` 不在、沒有 token、網路錯、JSON 看不懂,都算 false。
   - repo 名從 `git remote get-url origin` 或環境變數 `GITHUB_REPOSITORY` 取。
4. **prep 接上**:推送事件、suite=full 時呼叫 `lumos ci-reuse`(那一步帶 `GH_TOKEN: ${{ github.token }}`),true 就把 `skip_full` 設成 true 並在日誌印「同一棵檔案樹已在合併請求 #N 跑綠,這次不重跑全套」。
5. **權限**:workflow 加 `permissions:`——`contents: read`、`pull-requests: read`、`statuses: write`(`mark` 寫狀態要用;其他工作只讀)。
6. **寫回圖譜**:[[Systems/bound-tests-gate]] 摘要加 WHY(拆工作、跳過的判準與不選),改掉「切 4 片」那行(CI 不再是同一台切 4 片),ci.yml 開頭「切片後約 10 分」那句註解一併改。

## 實務隱患

- **跳過判準失靈 → 主線上壞東西沒人測**:判準是「檔案樹指紋一字不差」,合併請求跑完後主線又被推進別的東西,合併結果的樹就不同,照跑全套;查詢任何一步出錯一律照跑。狀態只有能寫入的人寫得進去(`GITHUB_TOKEN` 只在同 repo 的 CI 有寫入權;fork 來的合併請求 `mark` 不跑)。
- **有人偽造狀態讓主線跳過全套**:能寫提交狀態的人本來就能推主線、改 CI 設定,沒有多開一扇門。
- **`gh` 沒拿到 token 時無聲失效**:`reuse=false` 是安全方向,但功能等於沒做;`prep` 那步一定帶 `GH_TOKEN`,上線後第一次主線推送人工看日誌確認(〈實作紀錄〉記結果)。
- **拆成多台後失敗訊息分散**:每台各自印失敗片段,GitHub 介面上每個 matrix 工作分開看。
- **既有測試與健檢對 ci.yml 的字串檢查**:大約 9 支測試讀本 repo 真的 ci.yml(逐字比對步驟內容、步驟順序、縮排、`python-version`),健檢 `_ci_jobs_calling_without_full_history` 檢查呼叫閘的工作有沒有 `fetch-depth: 0`——後盾步驟逐字、順序、縮排照舊,所在工作帶完整歷史。
- **測試在多台機器上的狀態互相干擾**:每台是獨立機器,沒有共用磁碟;快取檔名本來就按份數分開(`test-cache-shard{i}of{n}.json`)。
- **自我治理(改的是治理機制本身)**:這次改的是 CI 這道最後後盾怎麼跑,不是被它守的東西;改壞了不會有更外層的東西抓到。所以:跳過全套的判斷寫成 lumos 指令、有測試先紅後綠([S1][S2]);ci.yml 的形狀有測試釘住([S3]);上線後第一次主線推送人工看一次日誌,確認是照預期跳過或照跑(〈實作紀錄〉記結果)。
- 已排除:金流:只改 CI 設定與一支查詢指令
- 已排除:對外送出:只呼叫 GitHub API 讀狀態與寫本 repo 的提交狀態,不送任何資料到第三方
- 已排除:不可逆:提交狀態可以覆寫,CI 設定可以還原
- **守衛面(沒排除)**:CI 是 `--no-verify` 的最後一道後盾;跳過全套等於放寬一道守衛,判準見第一條。

## 驗收條款

- [S1] 當 `lumos ci-reuse` 查到已合併的合併請求、它頭提交上 `lumos/full-suite-tree` 狀態是 success、記的檔案樹等於這次推送的檔案樹時,應 印 `reuse=true`;檔案樹不同、狀態不是 success、沒有那個狀態、合併請求沒合併、合併提交不是這個 sha、查不到合併請求時 應 印 `reuse=false` 並寫出原因 [test:t_ci_reuse_decides_by_tree]
- [S2] 當 `gh` 不在、`gh api` 回非零、回的 JSON 看不懂時,`lumos ci-reuse` 應 印 `reuse=false`、回傳碼 0 [test:t_ci_reuse_fails_safe]
- [S3] 當讀 ci.yml 時,全套測試應 在 matrix 工作裡、matrix 清單裡的份數編號合起來剛好是 1 到 N 各一次、`fail-fast` 是 false、有 `skip_full` 為真時不跑的條件;後盾那幾步除了 `steps.suite.outputs` 改成 `needs.prep.outputs` 之外 應 跟拆分前逐字相同、順序相同;四個工作 應 都有 `fetch-depth: 0`;`mark` 應 有 `continue-on-error: true` 而且只在同 repo 的合併請求事件跑 [test:t_ci_yml_matrix_and_gates_shape]
- [S4] 當 CI 的全套測試跑在多台機器上時,最慢那個工作 應 在 10 分鐘內完成 [manual:看實驗分支與上線後第一次 CI 的各 matrix 工作耗時,記進實作紀錄]

## 回退

還原本案的提交即可:ci.yml 回到單一工作、`lumos ci-reuse` 指令沒有人呼叫就無作用;已寫進提交的 `lumos/full-suite-tree` 狀態只是標記,不影響任何東西。

## 天花板

1. 測試切份是按名字輪流分,不按耗時;某一份剛好分到很多慢測試時,那份就是瓶頸。
2. 主線推送跳過全套只在「合併當下主線沒前進」時成立;常常好幾個合併請求同時排隊時,大多照樣重跑。
3. fork 來的合併請求不寫狀態,主線推送照跑全套。

## 實作紀錄

(〈做法〉0 的量測結果、上線後第一次主線推送的日誌確認寫在這裡。)

## 審計修正紀錄

- r1 前掃(2026-10-06,sonnet 一席):〈實作紀錄〉沒這節、`graph` 沒定義、寫狀態的工作沒名字、一台跑幾份怎麼寫沒定義;bound-tests-gate 沒有「約 10 分」(那句在 ci.yml 註解);三個工作其實是四個;「一字不改」做不到(讀前一步輸出那行要改);寫不進狀態會讓 CI 紅;prep、shards 也要完整歷史與補本機 main;既有測試釘住步驟順序與縮排;`gh` 要 `GH_TOKEN`;「37 處」是 grep 行數、讀真 ci.yml 的測試約 9 支。全部修進本版,修前修後對照在 `governance/review-reports/ci-speedup/r1-intake.md`。
