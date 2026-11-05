---
type: project
status: doing
created: 2026-11-05
updated: 2026-11-05
tags:
  - type/project
  - status/doing
  - scope/guards-gates
related:
  - "[[Projects/推送與CI提速_計劃]]"
  - "[[Projects/雙向門放行_計劃]]"
  - "[[Systems/bound-tests-gate]]"
lands_in:
  - Systems/bound-tests-gate
pending_questions:
  - id: Q1
    text: 全域 CLAUDE.md〈推送前〉的「不要只跑針對性測試或守衛測試就推」要不要改成「不要繞過本機閘」(上線後本機閘本身只跑受影響子集)?
    class: 流程
    stage: 交付
    status: 待查
---
# 推送只跑受影響測試_計劃

> 白話:現在推一個改到程式的功能分支,本機推送前要跑完 3700 多支測試(四片同時跑,平常 5–10 分,2026-11-05 實測一次跑了將近一小時),PR 的 CI 又全套跑一次。這篇改成:推功能分支時本機與 PR 的 CI 只跑「跟這次改到的函式與檔名有關」的測試,全套挪到合併進主線之後與每晚各跑一次;主線全套紅了自動開一篇 GitHub Issue 點名是哪次合併。使用者原話(2026-11-05):「是不是可以不要每次開發新功能就把既有的斷言全部跑過一遍?如果後續造成什麼功能壞掉,在返休就好了」,看過代價說明後回「同意,照這個方向做」。這是 [[Projects/推送與CI提速_計劃]] 留下的第二階段(那篇的 REVISIT 寫「推送前掛鉤的大改合併後,開第二階段」)。

PRIOR-ART: 業界共識是「提交前跑受影響的、完整測試在後面某處一定要跑」:Martin Fowler 的測試影響分析一文說合併前測過的,合併後在 CI 也要再測(https://martinfowler.com/articles/rise-test-impact-analysis.html);AWS DevOps 指引引 Google 的做法,全套在開發流程外非同步跑、結果最終一致(https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/qa.ft.4-balance-developer-feedback-and-test-coverage-using-advanced-test-selection.html);Red Hat 內部提案:不認得的路徑或改動太大退回全套、每晚全套兜底、統計漏抓(https://issues.redhat.com/browse/RHIDP-12297)。漏抓的代價:2022 年比較四種 Java 選測工具,平均抓錯能力比全套低 8.75%(https://www.se.cs.uni-saarland.de/conferences/ASE/ase2022/details/ase-2022/ase-2022-journal-first-papers/18/An-empirical-comparison-of-four-Java-based-regression-test-selection-techniques.html);只看靜態相依的選法挑得少、會漏,靠每晚全套兜底(Soetens 等 2015,https://azaidman.github.io/publications/soetensEMSE2015.pdf)。採用:本 repo 既有的關鍵字子集(原始碼整字提到改到的函式或檔名的測試,`_keys_mentioned`)當選法,加上退回全套的條件、合併後與每晚全套、紅了自動開 Issue。不採:動態選測(跑一次全套記下每支測試碰到哪些函式,像 pytest-testmon,https://pypi.org/project/pytest-testmon/0.9.18 ):本 repo 測試多半另開子程序跑主程式,要另外接覆蓋率才記得到,列為下一步,不在這篇;自動回退(Chromium Findit 只對穩定重現的失敗做、量有上限,https://sites.google.com/chromium.org/cat/findit ):單人加兩三個 AI 會談,回退可能連別人的工作一起退,改成開 Issue 交人或會談處理。

RETIRE-IF: 上線後八週內,主線合併後全套紅、而且紅的那支在那次推送的子集裡沒有被選到(子集漏抓)累計 3 次以上 → 推功能分支改回推送前跑全套(設成 `LUMOS_PREPUSH_FULL` 預設開);或八週內功能分支推送前的測試時間中位數沒有比上線前少一半以上 → 撤掉這套、回到現行。

## 舊否決對照

- [[Projects/CI加速_計劃]](2026-10-06)否決過「只跑受影響的測試子集」,理由是覆蓋變少;同處也否決「本機全綠就不等 CI 先合併」(要改全域規則、Linux 才出的錯變成合併後才發現)。這篇不同的地方:全套沒有拿掉,是從推送前挪到合併後與每晚跑,紅了自動開 Issue;總覆蓋不變,變的是發現時間。使用者 2026-11-05 看過「漏抓的壞東西會先進主線」的代價說明後裁定照做(原話:「是不是可以不要每次開發新功能就把既有的斷言全部跑過一遍?如果後續造成什麼功能壞掉,在返休就好了」「同意,照這個方向做」)。全域規則那一句另列待決問題 Q1,不由 AI 改。

## 現況(2026-11-05 量)

- 推送前掛鉤(`scripts/hooks/pre-push` 的測試套件閘):每個 ref 由 `lumos pitfalls --diff <範圍> --json` 的 `suite` 判範圍。只改文件 → 文件子集;改到程式但 `spec-gate --push-check` 判成 light 而且 `light_ok` → 文件子集加關鍵字子集(`--suite keys`;抽不出關鍵字就只跑文件子集);其他一律全套,切四片同時跑。
- 判範圍的函式是 `scripts/lumos` 的 `_test_suite_for_range`:守衛本身的檔(`_DOCS_ONLY_NEVER`,含測試檔的簽名基準 `governance/anchor-baseline.json`)→ 全套;簿記檔不算;剩下全是文件 → docs;否則 full,另回 `light_ok`(非文件檔全是需要有家的程式檔;測試檔不算程式檔)。所以只要改了測試檔,簽名基準就跟著變、整次推送一定全套——幾乎每個功能都是這樣。
- 關鍵字(`_affected_test_keys`):改到的程式檔裡動到的頂層函式名,加檔名去副檔名;選測(`_keys_mentioned`)是測試原始碼整字提到任一關鍵字就選。
- CI(`.github/workflows/ci.yml`):push 到 main、pull_request、tag 觸發;prep 只在 push 事件問 lumos,PR 事件一律全套;全套切 16 份給 8 台機器。concurrency 群組鍵含事件名。
- 合併後主線那次 CI 已經在跑全套,但 workflow 裡沒有任何通知步驟(GitHub 帳號層會不會寄信是帳號設定,程式碼驗不到)。
- 代碼審表態閘算適用題的起點用 `_mainline_ref`:先認 `main@{upstream}`,認不到才用本機 main。本機 main 的追蹤設定指向名叫 `origin` 的遠端,但這個 repo 的遠端叫 `Lumos`,追蹤認不到、退回本機 main;本機 main 落後時把別人已合併的改動算成這次的。這跟 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 是同一族(起點算法各閘不一),那篇管其他閘的 `_lens_push_base`。

量測(2026-11-05,本機,`scripts/test_lumos.py --suite keys --keys … --list` 數選中支數;全部 3202 支;取最近 10 次改到 `scripts/lumos` 的提交):

| 改到的頂層函式數 | 只用函式名 | 函式名加直接呼叫者一層 | 再加檔名 `lumos` |
|---|---|---|---|
| 2 | 1 | 2 | 877 |
| 8–26 | 9–17 | 27–162 | 約 885 |
| 24–77 | 26–44 | 111–233 | 約 890–913 |
| 56–139(大改) | 約 460–500 | 未量 | 約 1170–1190 |

檔名 `lumos` 一個字就選中 876 支(27%),因為幾乎每支測試都會跑主程式;只用函式名又會漏掉「改了底層輔助、測試只提到上層指令」的情形。

FACT:PR #158 合併後 CI 第 10 份耗時 1217 秒,同次本機推送前全套約一小時 [來源:生產] [confirmed:2026-11-05]
FACT:t_prepush_new_branch_block_range 在合併前版本本機也要 135 秒,CI 慢時偶發超過 180 秒 [來源:人工] [confirmed:2026-11-05]

## 範圍

- 做:推功能分支(遠端目的 ref 是 `refs/heads/*` 而且不是 main)時,本機推送前只跑受影響子集;PR 的 CI 也只跑同一個子集;推到 main 的 CI 照舊全套;CI 新增每晚一次全套;主線(含每晚)全套紅了自動開 Issue;退回全套的條件;強制全套的環境變數;表態閘的適用範圍改從遠端主線分岔點算。
- 不做:動態選測(見 PRIOR-ART);自動回退;改其他閘(合約測試真跑、新增告警閘、規格閘、代碼審留痕都照舊,它們本來就只看這次改動);消費專案(推送前掛鉤本來就只在來源 repo 跑測試);改測試內容。

## 做法

1. **新範圍 `affected`**:`_test_suite_for_range` 多回一種結果。條件全部成立才是 affected,否則照現行(docs / full):
   - 推送的遠端目的 ref 是功能分支:`refs/heads/*` 而且不是 main 或 master(跟 `_push_mainlines` 認主線的口徑一致)。呼叫端傳入:pitfalls 加旗標 `--target-ref <ref>`;沒給就不判 affected,維持現行。PR 事件以 PR 的頭分支為目的(合進 main 的 PR 走 affected);直推 main 或 master 照現行(含 light),不受這篇影響。
   - 非文件檔都是程式檔或測試檔(`scripts/test_lumos.py`),不含下面的基礎設施清單。這比現行 `light_ok` 寬:多收測試檔。守衛檔裡的測試檔簽名基準 `governance/anchor-baseline.json` 在這裡不強制全套(它只是跟著測試檔改、由測試檔的改動代表),其他守衛檔照舊強制全套。
   - 抽得出關鍵字。關鍵字改成新函式 `_affected_test_keys_wide`(既有 `_affected_test_keys` 留給 light 用、不改):
     - 改到的頂層函式名;`cmd_` 開頭的加子命令名(既有做法)。
     - 擴一層:`scripts/lumos` 裡改到的是 `_` 開頭的輔助時,直接呼叫它的頂層函式也算(量測見〈現況〉表:典型改動選中 2–233 支)。
     - 檔名:頂層函式超過 200 個的大檔(`scripts/lumos`、`scripts/test_lumos.py`)不用檔名當關鍵字(檔名一個字就選中 27%);其他檔照舊用檔名。
     - 測試檔:改到或新增的 `t_` 函式名本身算關鍵字(新測試一定被選到);改到的非 `t_` 輔助照上面「擴一層」處理(用到它的測試會整字提到它)。
   - 關鍵字選中的測試數不超過全部的一半(超過就沒有省到,直接全套)。
   - 沒設 `LUMOS_PREPUSH_FULL=1`。
2. **基礎設施清單(一律全套)**:`scripts/hooks/`、`.github/workflows/`、`install.sh`;`scripts/test_lumos.py` 裡的執行器本體函式——機械判準:頂層函式名不是 `t_` 開頭、而且沒有任何一支 `t_` 測試的原始碼整字提到它(被測試呼叫的是輔助,走關鍵字;沒被任何測試提到的就是執行器自己,例如 `main`、分片、計時、快取);`scripts/lumos` 裡選測本身的函式(`_test_suite_for_range`、`_keys_mentioned`、`_affected_test_keys`、`_affected_test_keys_wide`、`_autoloop_full_for`,寫成常數 `_SELECTION_FUNCS`,新增選測函式要一起登記);以及 `_DOCS_ONLY_NEVER` 守衛檔(測試檔簽名基準除外,見上)。理由:這些檔壞了會讓「選測」本身失準或讓所有測試假綠,子集看不出來。
3. **推送前掛鉤**:`suite=affected` 時跑「文件子集 + 關鍵字子集」(同現行 light 的跑法,同樣分片同時跑);印一行說明「這次只跑跟改動有關的 N 支;合併進主線後 CI 跑全套,紅了會自動開 Issue」。順手修現行的誤導:`run_group` 只要任一片回 3(這一片分到 0 支)就整組回 3,選中支數比片數少時空片必然回 3,掛鉤卻印「沒有測試提到這次改到的函式或檔名」;改成「每片都回 3 才算一支都沒選到」(那個沒用到的 `_krc_all3` 變數就是原本的意圖)。直推 main 或 master 照現行。
4. **CI**:
   - prep:PR 事件也問 lumos(範圍 `origin/main` 與 PR 頭的分岔點..PR 頭,目的 ref 視為功能分支);結果是 affected 就跑「文件子集 + 關鍵字子集」那一步,不跑 shards。推到 main 一律全套(不問 affected)。
   - PR 事件 affected 時,gates 工作的自主迴圈測試照推送前掛鉤同一條規則(`_autoloop_full_for`:關鍵字碰到自主迴圈就整支跑),不再只認 docs。
   - 新增 `schedule`(每天台北時間凌晨 3 點,cron `0 19 * * *` UTC)跑全套,針對 main 頂端;schedule 事件沒有 before,prep 照現行落到全套;concurrency 群組鍵含事件名,跟同一個提交的 push 事件不同組,不會互相取代。
   - 推到 main 與 schedule 的全套紅了:新工作 `notify` 用 `gh issue create` 開 Issue(標題「主線全套紅:<提交前 8 碼>」,內文列紅的測試名、觸發的合併或排程、run 網址,標籤 `main-red`);同標籤已有開著的 Issue 就改成留言,不重開。這個工作要 `issues: write` 權限,只給它,不給其他工作。
5. **漏抓統計**:只對「推到 main 的全套紅」做(schedule 沒有對應的合併,不標)。notify 工作拿合併提交的第一個父提交到合併提交這段(就是整個 PR 的改動)重算一次 `affected` 的選測清單,紅的那支不在清單裡就標「子集漏抓」、加標籤 `subset-miss`。口徑是「整個 PR 的改動當時會選到誰」,不是「PR 期間每次推送實際跑了誰」(那要跨 run 存清單,不做);RETIRE-IF 數的就是這個標籤。
6. **強制全套**:`LUMOS_PREPUSH_FULL=1 git push` 這次推送前跑全套(不留帳,它是多跑不是少跑)。
7. **表態閘範圍**:`_mainline_ref` 認不到 `main@{upstream}`(追蹤設定指向不存在的遠端,本 repo 就是)時,先找各遠端的 `main`/`master` 追蹤分支(同 `_push_mainlines` 的候選),取跟頂端分岔點最新的那個,都沒有才用本機 main。`remote_only=True` 的呼叫端(筆記形狀擋)也一樣只認遠端的。
8. **說明文字同步**:專案 CLAUDE.md〈本 repo 的測試子集怎麼跑〉一段、`Systems/bound-tests-gate` 的現況說明、推送前掛鉤印的提示改成新規則。使用者全域 CLAUDE.md〈推送前〉寫「不要只跑針對性測試或守衛測試就推」,跟這篇衝突,改寫那一句要使用者自己點頭(見〈待人〉)。

## 驗收條款

- [S1] 當推送目的是功能分支、改到的非文件檔都是程式檔或測試檔、抽得出關鍵字、選中不到全部一半、沒設強制全套時,`pitfalls --json` 應 回 `suite: affected` 並附關鍵字;測試檔裡新增或改到的 `t_` 函式名 應 在關鍵字裡;改到 `_` 開頭輔助時直接呼叫它的頂層函式 應 在關鍵字裡;大檔的檔名 應 不在關鍵字裡;只多改了測試檔簽名基準 應 照樣是 affected [test:t_suite_affected_for_feature_branch]
- [S2] 當直推 main 或 master、沒給 `--target-ref`、改到基礎設施清單裡的檔(含執行器本體函式與選測函式)、改到簽名基準以外的守衛檔、抽不出關鍵字、選中超過一半、或設了 `LUMOS_PREPUSH_FULL=1` 時,應 不回 affected(照現行判 docs/full),回 full 時 `suite_reason` 說明是哪一條 [test:t_suite_affected_falls_back_full]
- [S3] 當推送前掛鉤拿到 `affected` 時,應 只跑文件子集加關鍵字子集並印出「合併後 CI 跑全套」那行;選中支數比片數少時 應 不印「沒有測試提到」;每片都選中 0 支時 應 照舊印;直推 main 時 應 照現行 [test:t_prepush_affected_subset]
- [S4] 當 `ci.yml` 被讀時,PR 事件的 prep 應 問 lumos 並在 affected 時不跑 shards、gates 的自主迴圈照 `_autoloop_full_for`;推到 main 應 一律全套;應 有每天一次的 schedule 跑全套 [test:t_ci_yml_affected_shape]
- [S5] 當推到 main 或 schedule 的全套紅時,`notify` 工作 應 開或留言一篇帶 `main-red` 標籤的 Issue,內文有紅的測試名與 run 網址;只有它有 `issues: write` [test:t_ci_yml_main_red_opens_issue]
- [S6] 當本機 main 的追蹤設定指向不存在的遠端、本機 main 又落後遠端 main 時,`_mainline_ref` 應 改認遠端的 main 追蹤分支,表態閘算適用題 應 不把遠端已合併的改動算進來 [test:t_codeloop_applicable_range_uses_remote_main]
- [S7] 當 notify 工作對紅的測試重算子集、紅的那支不在當時的選測清單時,應 在 Issue 標「子集漏抓」並加 `subset-miss` 標籤 [manual:合併一個故意讓非關鍵字測試變紅的 PR 到測試用分支觀察 Issue 標籤]

## 回退

- 設 `LUMOS_PREPUSH_FULL=1` 就退回推送前全套(單次);要永久退回把 `_test_suite_for_range` 的 affected 分支拿掉。
- CI:把 PR 事件的 prep 改回一律全套、拿掉 schedule 與 notify 工作。

## 實務隱患

- 守衛面:這篇就是少跑測試。漏抓的壞東西會先進主線,要等合併後或當晚全套才被發現;補救是自動開 Issue 加漏抓統計加撤除條件。關鍵字選法是靜態的,靠反射、字串組指令名、子程序呼叫才連到的測試會漏(PRIOR-ART 的研究也指出靜態選法的漏洞主要在間接呼叫);執行器與掛鉤本身列進基礎設施清單一律全套。
- 已排除:金流:只動測試範圍與 CI 觸發,不碰付款或計費。
- 對外送出:CI 會在 GitHub 開 Issue 或留言,只在本 repo、只用內建 `GITHUB_TOKEN`、權限只給 notify 工作;Issue 內文只放測試名與 run 網址,不放測試輸出(輸出可能含路徑或環境資訊)。
- 已排除:不可逆:設定與程式都能還原;開出的 Issue 可以關。
- 併發:多個合併接連進主線、每個都跑全套,同一個紅可能開多篇 → 同標籤開著的 Issue 改留言。每晚全套與合併後全套撞在一起只是多跑一次。
- 時好時壞的測試:主線全套紅可能是偶發(例:2026-11-05 `t_prepush_new_branch_block_range` 在 CI 逾時、本機與合併前版本都 135 秒)。notify 只開 Issue、不回退,偶發的由人判;漏抓統計只數「子集沒選到」的,偶發紅也可能被數進去,撤除前要人看過那幾篇。
- 本機 main 過時:選測與表態閘都要從遠端主線的分岔點算([S6]),不然範圍膨脹、子集變全套。
- 選測漏洞:只看函式名加一層呼叫者,靠字串組指令名、子程序、反射才連到的測試會漏;量測表的選中數也只取了 10 個提交、單次量。

REVISIT:2026-12-31 上線八週左右,看 `subset-miss` 標籤筆數與功能分支推送前測試時間中位數,照 RETIRE-IF 判要不要撤
