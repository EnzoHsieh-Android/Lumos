severity: minor

# ci-speedup r1 通才席審稿(正確性)

立場:假設照 spec 實作的 CI 會在某情境出錯。逐一推演了任務點名的幾個情境,結論先講。

## 覆核:點名情境多數站得住(不列 finding)

跳過判準是「檔案樹相等」,狀態記的是「當時真的測過的樹」,所以下列情境都落在安全方向(樹不同就照跑,樹相同就是測過同一份內容):
- 合併請求後來又推新提交、舊狀態還在:舊頭提交的狀態不會被拿來比,因為只看已合併、merge_commit_sha 等於推送頂端那一個合併請求的「最後頭提交」;頭提交換了樹就變。
- 同一個頭提交被兩個合併請求用:兩邊各寫各的樹,取到的狀態樹不等於主線樹就照跑,相等就代表那棵樹真的綠過。
- rebase/squash:樹等於「合併當下頭 + 主線」的樹時才相等,主線沒前進才成立,與〈天花板〉第 2 點一致;對不上只是多跑。
- 狀態在 mark 失敗前寫:mark 在 `needs: shards` 之後,shards 紅就不會跑(`if:` 沒寫狀態函式時 GitHub 自動補 success())。⚠ 這點請實作時用一次紅的 shards 驗 mark 確實被跳過。
- PR 的 CI 只跑文件子集:spec 的 suite 判斷只在 push 事件,pull_request 一律 full,所以 PR 不會寫出「只測過文件子集」的狀態。
- 手動改狀態:與〈實務隱患〉第二條同結論,寫得進狀態的人也推得進主線。

以下是找得到的洞。

## F1 樹相同不等於輸入相同:日期、Python 小版本、runner 映像、git 拓撲都被跳過吞掉
severity: minor
blocking: 否 + 判準:不是照字面實作就錯,是跳過條件只比檔案樹,測試的其他輸入漂移後主線紅不會再出現;⚠ 需實測才能判成 major。
引句:「判準是「檔案樹指紋一字不差」」
引句:「測試一條都不少,Linux 上跑的保護也還在。」
情境:合併請求某日綠了(`python-version: "3.14"` 解析到當時的 3.14.x、`ubuntu-latest` 當時的映像),擱置數天、主線沒前進就合併。這段時間內任何讀真日期的測試(回頭條件到期、`[until:]`、`[confirmed:]` 半年窗)、Python 小版本或映像更新、或「PR 環境(HEAD 是合併提交、main@{upstream} 是 B)與 push 環境(origin/main 就是 HEAD)」的 git 拓撲差異,在主線推送時本來會讓全套紅,現在 shards 直接不跑,紅被吞掉。ci.yml 自己的註解就承認 PR 與 push 的 git 環境曾經不同(2026-10-03 那次),而 `test_lumos.py` 有 92 處讀現在時間。
驗證方法:取一個已知會在 push 環境才紅的假設(例如把一支測試臨時改成「`git rev-parse origin/main` 必須等於 HEAD」),看 PR 綠、主線推送全套是否紅;再用 `faketime`/在乾淨 clone 上把日期撥後 30 天跑一次全套,看有沒有測試翻紅。有紅就升 major,並在跳過條件加一個「PR 綠到推送的間隔上限」(例如狀態時間超過 24 小時就照跑)。
file: `.github/workflows/ci.yml:17`
file: `scripts/test_lumos.py:33370`

## F2 RETIRE-IF 的撤除條件在跳過生效後無法被觸發
severity: minor
blocking: 否 + 判準:不影響單次 CI 結果,影響「判準失靈有沒有人會知道」,屬機制維護問題。
引句:「連續一季有任何一次「主線紅、但同一棵樹的合併請求是綠」,撤掉跳過(判準失靈)」
情境:判準失靈的唯一表現是「同樹、主線上全套會紅」,但這種情況下 shards 被跳過,主線的全套根本沒跑,所以永遠看不到「主線紅」。唯一可能紅的只剩 gates,而 gates 紅與判準失靈無關。撤除條件因此在跳過成功的世界裡恆為假,等於沒有撤除條件。補法:在撤除條件裡加一個探針——每月(或每 N 次跳過)強制抽一次不跳過、與 PR 結果比對;抽樣紅就算判準失靈。
file: `docs/lumos-toolchain-knowledge/Projects/CI加速_計劃.md`(本 spec 第 24 行)

## F3 拆工作後新工作沒有 timeout-minutes,掛住的一份會佔 6 小時,而 ci-wait 只等 30 分鐘
severity: minor
blocking: 否 + 判準:單份測試各自有逾時判紅,掛住要靠整支行程卡死才發生;但現況的 45 分鐘上限會被預設值悄悄放寬成 360 分鐘。
引句:「`shards`:`needs: prep`、`if: needs.prep.outputs.skip_full != 'true'`」
情境:spec 全篇沒提四個工作的 `timeout-minutes`,而現有 `test` 工作有 `timeout-minutes: 45`。照字面實作,四個工作都落到預設 360 分鐘。某一份(例如子行程卡住的那份)掛住時:該 matrix 腳 6 小時不結束,`mark` 一直等不到 shards,`lumos ci-wait` 在 1800 秒後逾時,推送既不紅也不綠。再加上 GitHub 免費帳號同時 20 個工作的上限:PR 與 push 兩次執行同時排隊時(各 1+8+1+1 個工作)會超過,排隊時間也會把牆鐘拖過 30 分鐘。補法:每個工作寫明 `timeout-minutes`(shards 約 15–20、gates 約 15、prep 約 10),並在〈做法〉0 量測時一併記牆鐘含排隊。
file: `.github/workflows/ci.yml:12`
file: `scripts/lumos:46530`

## F4 mark 的前提只有 shards 綠,gates 紅的合併請求照樣寫出「可跳過」狀態,而 spec 沒說這是刻意的
severity: minor
blocking: 否 + 判準:主線推送的 gates 照跑,所以不會讓紅放行;只是語意與狀態名稱 `full-suite-tree` 一致,屬措辭與意圖需寫明。
引句:「`mark`(記檔案樹):合併請求事件、全套全綠後,在合併請求頭提交上寫狀態。」
情境:PR 上 doctor 紅(gates 紅)、shards 綠,狀態仍寫 success;沒有分支保護,照樣能合併,主線 push 再被 gates 擋下。結果正確,但第一次紅是在主線而不是 PR,與拆分前「PR 上就紅」不同。補一句「狀態只代表全套綠,不代表 PR 整體綠」即可,避免後人把這個 context 當成 PR 綠燈使用。
file: `.github/workflows/ci.yml:108`

總結:全份最高等級 minor
