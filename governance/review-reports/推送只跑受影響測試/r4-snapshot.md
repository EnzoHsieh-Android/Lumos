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
  - "[[Projects/依實測覆蓋挑測試_計劃]]"
lands_in:
  - Systems/bound-tests-gate
  - Systems/pitfalls-code-loop
pending_questions:
  - id: Q1
    text: 全域 CLAUDE.md〈推送前〉的「不要只跑針對性測試或守衛測試就推」要不要改成「不要繞過本機閘」(上線後本機閘本身只跑受影響子集)?
    class: 流程
    stage: 交付
    status: 待查
  - id: Q2
    text: 要不要對 main 開分支保護、把 CI 的全套設成合併前必過?(開了之後 CI 沒綠就合不進去,包括使用者說「可以直接合併」的時候;會影響所有會談)
    class: 流程
    stage: 交付
    status: 待查
---

# 推送只跑受影響測試_計劃

> 白話:現在推一個改到程式的功能分支,本機推送前要跑完 3700 多支測試(四片同時跑,平常 5–10 分,2026-11-05 實測一次一小時以上)。這篇是兩步走的第一步,**名字沿用、內容是「推功能分支本機不跑全套」**:推功能分支時本機只跑便宜的檢查與現行的關鍵字小子集(冒煙測試,不當保證);全套照舊由 PR 的 CI 跑(PR 事件本來就一律全套),合併一律走 PR、等 PR 最新頭提交的全套綠。CI 不改。第二步(靠「每支測試上次碰過哪些函式」挑測試,讓 CI 也能少跑)另開 [[Projects/依實測覆蓋挑測試_計劃]]。使用者原話(2026-11-05):「是不是可以不要每次開發新功能就把既有的斷言全部跑過一遍?如果後續造成什麼功能壞掉,在返休就好了」;設計審 r1 指出靜態選測先天漏抓、查過世界解之後,使用者同意「兩步走」;r3 收不乾淨,使用者裁「收不乾淨的你就上網釐清方向」,查過後定成現在的形狀。這也是 [[Projects/推送與CI提速_計劃]] 留下的第二階段。

PRIOR-ART: 兩段式 CI:快的檢查每次推送跑、完整測試在要合併前跑(Mergify 兩段式 https://docs.mergify.com/merge-queue/two-step.md );pre-push 只跑快的、全套交 CI,而且掛鉤可以被繞過、CI 才是真正擋的那道(https://dev.to/jameson/pre-push-hooks-42g5 、https://pypi.org/project/prepush-ci/ )。CI 觸發的世界常規:push 只限預設分支、pull_request 不限,避免同一個提交推上去又開 PR 時跑兩次;代價是沒開 PR 的功能分支沒有 CI,RubyGems 明寫接受(https://adamj.eu/tech/2025/05/14/github-actions-avoid-simple-on/ 、https://docs.publishing.service.gov.uk/manual/test-and-build-a-project-with-github-actions.html 、https://github.com/rubygems/rubygems/commit/924d916a73 )——本 repo 的 ci.yml 正是這個形狀,所以不改。GitHub 的必過檢查要在 PR 最新的頭提交上過,舊提交的結果不算(https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks );本 repo 用「合併前對 PR 頭提交 `lumos ci-wait` 判定 green」做同一件事,機械擋要分支保護(Q2)。不採:r2–r3 試過的「CI 推任何分支都跑」(把 gates 的後盾閘、沒有本機 main 的環境、逐次推送的增量範圍一起帶進功能分支,三輪都收不乾淨;世界常規也不這樣做)。

RETIRE-IF: 上線後八週內,PR 的 CI 全套(shards 工作)在 PR 頭提交上紅、要回頭修的 PR 超過這段期間 PR 數的三成 → 改回推功能分支時本機跑全套(來回修 CI 的時間已經比本機多跑的時間多)。數法:GitHub 的 PR 清單與各 PR 的 shards 工作結論,唯讀統計、不進閘;基準先記上線前八週的同一比例(上線當天量)。

## 舊否決對照

- [[Projects/CI加速_計劃]](2026-10-06)否決「只跑受影響的測試子集」(覆蓋變少)與「本機全綠就不等 CI 先合併」(要改全域規則)。這一步不同:全套沒有變少,只是從本機換到 CI 跑,合併前照等;兩條舊否決的理由都不成立。

## 現況(2026-11-05 量)

- 推送前掛鉤(`scripts/hooks/pre-push` 的測試套件閘):每個 ref 由 `lumos pitfalls --diff <範圍> --json` 的 `suite` 判範圍。只改文件 → 文件子集;改到程式但 `spec-gate --push-check` 判成 light 而且 `light_ok` → 文件子集加關鍵字子集,自主迴圈照 `autoloop_full`(`affected_keys`、`autoloop_full` 只在這個條件區塊裡讀);其他一律全套。任何一個 ref 要全套就全套;只刪遠端分支的推送沒有 ref 進判定,也落在全套。
- 改了測試檔,簽名基準 `governance/anchor-baseline.json` 跟著變;它在守衛檔清單 `_DOCS_ONLY_NEVER`,`_test_suite_for_range` 碰到守衛檔提早回 full 而且 `code` 是空的,所以 `affected_keys` 也是空的。過代碼審的分支還會改到 `governance/code-loop/`,同樣是守衛檔。
- CI(`.github/workflows/ci.yml`):觸發只有 push 到 main、tag、pull_request;PR 事件一律全套;concurrency 群組鍵含事件名,PR 以編號分組並取消進行中的,push 以提交編號分組、不取消。功能分支推上去、沒開 PR 之前,CI 不跑。
- `lumos ci-wait`:未定、逾時、no-run、工具缺席都回 rc0,只有判定是 green 才是綠(`cmd_ci_wait` 的說明)。
- main 沒有設分支保護。

FACT:PR #158 合併後 CI 第 10 份耗時 1217 秒,同次本機推送前全套約一小時 [來源:生產] [confirmed:2026-11-05]
FACT:main 沒有分支保護 [來源:外部] [confirmed:2026-11-05] [查:gh api repos/EnzoHsieh-Android/Lumos/branches/main/protection]

## 範圍

- 做:①推送前掛鉤對功能分支的 ref 不跑全套,改跑文件子集與關鍵字子集;②「這次推的是不是主線」沿用既有 `_note_reread_mainline_names`,由 `pitfalls --json` 輸出、掛鉤只讀;③算不出範圍、算不出主線時照全套;④訊息照實講,包括「合併一律走 PR、等 PR 頭提交的全套綠」;⑤說明文字同步。
- 不做:CI 任何改動(見 PRIOR-ART);新選測演算法(第二步);合併後通知;GitHub repo 設定(分支保護是 Q2);主線起點算法(本機 main 過時已有 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 與 [[Systems/pitfalls-code-loop]] 的 REVISIT 2026-11-13 在追);修 `run_group` 回 3 的判法(r2 正確性席實測前提不成立);強制全套的環境變數(要全套直接跑 `python3.14 scripts/test_lumos.py`);其他閘照舊;記憶與歷史紀錄裡的舊說法(記憶是衍生層,照記憶過期清掃處理;已結案計劃的歷史敘述不改)。

## 做法

1. **pitfalls 輸出兩個新欄位**:
   - `pitfalls` 加旗標 `--pushed-ref <遠端 ref>`(只用來判主線,不改 `--diff` 的範圍;不需要遠端名)。給了就在 `--json` 輸出 `pushed_mainline`:被推的不是 `refs/heads/` 底下 → true;分支短名在 `_note_reread_mainline_names(root, tip)` 回的集合裡 → true(這個集合永遠含 `main`、`master`,再加主線候選實際指到的分支名,不看遠端名——推網址、別名遠端、新遠端首推 main 都認得);其他 → false。沒給旗標 → 不輸出這個欄位。
   - `--json` 一律多輸出 `suite_computed`:`_test_suite_for_range` 算得出改動清單時 true;「範圍算不出來」「算不出改動清單」時 false。
2. **掛鉤**:每個 ref 叫 `pitfalls` 時多帶 `--pushed-ref "$_rref"`(用掛鉤既有的 `pp_q` 引號寫法)。這個 ref 判 `full` 時,只有三個條件都成立才改判 `light`:`pf_json` 裡有 `"pushed_mainline": false`、有 `"suite_computed": true`、而且能讀到這兩個欄位(用掛鉤現有讀 `pf_json` 的 `grep` 寫法)。降成 light 時在這個分支裡讀 `affected_keys` 與 `autoloop_full`(跟現行 light 那段同樣讀法)。其他情況(`pf_json` 空或讀不懂、舊版沒欄位或不認得旗標、推主線、算不出範圍)照現行全套。原本判 docs 或 light 的照舊;多個 ref 照現行「任一要全套就全套」。降級刻意不受 `light_ok` 約束(改到測試檔、守衛檔也降):全套由 PR 的 CI 跑。
3. **訊息**:迴圈結束、`_suite_mode` 定案之後只印一次:最終是 light 而且至少一個 ref 是因「功能分支」降下來的 → 「推功能分支:本機只跑文件子集與關鍵字子集(關鍵字空的就只有文件子集);全套由 PR 的 CI 跑——合併一律走 PR,等 PR 最新頭提交的 `lumos ci-wait` 判定是 green(rc 0 不等於綠)才合併」。
4. **說明文字同步**(逐處):紀律範本 `scripts/templates/graph-discipline.md` 那句「全套留給推送前的閘」改寫,用 `lumos update` 重新注入 `CLAUDE.md` 與 `AGENTS.md` 的紀律區塊;專案 `CLAUDE.md` 紀律區塊外〈本 repo 的測試子集怎麼跑〉一段;`skills/lumos-project-notes/commands/08-自動跑的.md` 的 pre-push 那句;[[Systems/bound-tests-gate]] 2026-09-18 那行的結論;掛鉤 `_suite_word` 的說明句;[[Systems/pitfalls-code-loop]] 寫 `--pushed-ref`、`pushed_mainline`、`suite_computed`;父計劃 [[Projects/推送與CI提速_計劃]] 的 REVISIT 2026-11-14 那行照 [[Projects/漂移防治路線圖_計劃]] 的寫法加 `[closed:]`。使用者全域 CLAUDE.md 是 Q1,不由 AI 改。

## 驗收條款

- [S1] 當推送目的是功能分支、這個 ref 原本判全套、`pushed_mainline` 是 false、`suite_computed` 是 true 時,掛鉤 應 只跑文件子集加關鍵字子集,迴圈後只印一次「全套由 PR 的 CI 跑」那行 [test:t_prepush_feature_branch_skips_full]
- [S2] 當推 main、或 `pf_json` 是空的、或沒有 `pushed_mainline`(舊版 lumos)、或 `suite_computed` 是 false 時,掛鉤 應 照舊全套而且不印那行 [test:t_prepush_feature_branch_failclosed]
- [S3] 當同一次推送有推 main 的 ref 也有功能分支的 ref 時,掛鉤 應 全套而且不印那行 [test:t_prepush_feature_branch_mixed_with_main]
- [S4] 當給了 `--pushed-ref` 時,`pitfalls --json` 應 對 `refs/heads/main`、`refs/heads/master`、遠端 HEAD 指的分支回 `pushed_mainline: true`(沒有任何遠端追蹤 ref 時推 main 也是 true),對其他分支回 false,對標籤回 true;沒給 應 不輸出這個欄位 [test:t_pitfalls_pushed_mainline]
- [S5] 當範圍算不出來時,`pitfalls --json` 應 回 `suite_computed: false`;算得出時 應 回 true [test:t_pitfalls_suite_computed]
- [S6] 當功能分支因這條降成 light、`autoloop_full` 為真時,自主迴圈測試 應 整支跑 [test:t_prepush_feature_branch_skips_full]
- [S7] 當紀律範本改寫後重新注入時,`CLAUDE.md` 與 `AGENTS.md` 的紀律區塊(sentinel 之間)應 跟範本逐字一致、不再有「全套留給推送前的閘」 [test:t_prepush_doc_says_ci_runs_full]

## 回退

- 掛鉤:拿掉做法 2 的降級分支與多帶的旗標(推功能分支回到本機全套);刪 S1、S3、S6 的測試(S2 留著)。
- `pitfalls` 的兩個欄位與旗標可以留著(沒人讀就沒影響)。
- 說明文字:做法 4 的每一處改回原文,範本改回後 `lumos update` 重新注入;刪 S7 的測試。改到測試檔要重簽簽名基準(`lumos anchor approve`)。

## 實務隱患

- 守衛面:本機不跑全套,壞東西要等 PR 的 CI 才看到。PR 事件一律全套、帳本提交會在 PR 頭上再觸發一次全套,所以 PR 頭提交一定有全套結果;剩下的洞是「沒走 PR 直接合」或「沒等綠就合」——main 沒有分支保護,靠訊息與既有規矩,機械擋是 Q2。沒開 PR 的功能分支沒有任何全套(世界常規接受的代價),只要不合併就不影響主線。
- 算不出來的方向:`pf_json` 空、舊版沒欄位或不認得旗標(argparse 拒絕、`|| true` 吞掉 → `pf_json` 空)、`suite_computed` false 一律照全套。舊版 lumos 不認得新旗標時連純文件推送也會變全套(比現在慢,方向安全)。
- 主線判定查候選失敗:只剩 `main`、`master` 兩個固定名;預設分支叫別的名字(例如 develop)時那次會被當功能分支——本 repo 的主線就是 main,接受。
- 時間:PR 的 CI 全套約 15–20 分(16 份給 8 台);GitHub 免費帳號同時執行的工作有上限,多個會談同時開 PR 會排隊,`ci-wait` 逾時(rc 0、判定 timeout)不等於綠,要再等。
- 併發:多個會談各自推分支,本機各自只跑小子集,負載比現在低。
- 已排除:金流:不碰付款或計費。
- 已排除:對外送出:不改 CI、不開 Issue、不新增對外呼叫。
- 已排除:不可逆:掛鉤、`pitfalls` 欄位、範本都能還原。

## 審計修正紀錄

- r1(2026-11-05,6 席:正確性、邊界、平台、合約圖譜、通才、架構對齊,皆 sonnet):45 條/blocking 25 條/靜態關鍵字選測先天漏抓、通知機制做不出來、引入第二套做法;查過世界解後換形狀成兩步走,這篇只做本機不跑全套,選測移到 [[Projects/依實測覆蓋挑測試_計劃]]。例:改到一個沒有任何測試整字提到的輔助函式(主程式 62.6% 屬此類)→ 舊設計只選中 0 支測試就放行;新設計本機只跑小子集、PR 的 CI 跑全套才合併。卷證 governance/review-reports/推送只跑受影響測試/
- r2(2026-11-05,6 席:正確性、邊界、合約圖譜、通才、流程、架構對齊,皆 sonnet):30 條/blocking 18 條/換形狀後的小設計仍有洞:沒開 PR 時 CI 不跑、算不出來與守衛檔情境反而降級、掛鉤自己認主線是第三套做法、`run_group` 修法前提不成立、撤除條件量不到。改成推功能分支就觸發 CI 全套、算不出來照全套、主線改由 lumos 用 `_push_mainlines` 判、拿掉 `run_group` 那段、撤除條件改數 GitHub run。例:推功能分支後還沒開 PR → 舊設計本機只跑小子集、CI 也不跑;新設計這次推送就觸發 CI 全套。卷證 governance/review-reports/推送只跑受影響測試/

- r3(2026-11-05,6 席:正確性、邊界、合約圖譜、通才、流程、架構對齊,皆 sonnet):30 條/blocking 12 條/「CI 推任何分支都跑」把後盾閘、沒有本機 main 的環境、逐次推送的增量範圍一起帶進功能分支;主線判法綁遠端名是已被淘汰的舊形狀;算不出範圍也會降級。上網查過(使用者裁「收不乾淨的你就上網釐清方向」),世界常規是 CI 只在預設分支 push 與 PR 跑、必過檢查看 PR 頭提交;改成 CI 不改、合併一律走 PR 等頭提交綠、主線沿用 `_note_reread_mainline_names`、加 `suite_computed`。例:推網址到 main → 舊設計判成功能分支、跳過本機全套;新設計分支名 main 在固定名集合裡,照全套。卷證 governance/review-reports/推送只跑受影響測試/

REVISIT:2026-12-31 上線八週左右,照 RETIRE-IF 數 PR 頭提交全套紅、要回頭修的 PR 比例
