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

> 白話:現在推一個改到程式的功能分支,本機推送前要跑完 3700 多支測試(四片同時跑,平常 5–10 分,2026-11-05 實測一次一小時以上)。這篇是兩步走的第一步,**名字沿用、內容是「推功能分支本機不跑全套」**:推功能分支時本機只跑便宜的檢查與現行的關鍵字小子集(冒煙測試,不當保證);全套改由 CI 跑——推功能分支本身就觸發 CI 全套(不必等開 PR),合併前要等它綠。第二步(靠「每支測試上次碰過哪些函式」挑測試,讓 CI 也能少跑)另開 [[Projects/依實測覆蓋挑測試_計劃]]。使用者原話(2026-11-05):「是不是可以不要每次開發新功能就把既有的斷言全部跑過一遍?如果後續造成什麼功能壞掉,在返休就好了」;設計審 r1 指出靜態選測先天漏抓、查過世界解之後,使用者同意「兩步走」。這也是 [[Projects/推送與CI提速_計劃]] 留下的第二階段。

PRIOR-ART: 兩段式 CI:快的檢查每次推送跑、完整測試在要合併前跑(Mergify 兩段式做法 https://docs.mergify.com/merge-queue/two-step.md ;Fides 專案因「每支測試跑兩次」拿掉其中一次 https://github.com/ethyca/fides/pull/7672 );Martin Fowler:合併前測過的,合併後在 CI 也要再測(https://martinfowler.com/articles/rise-test-impact-analysis.html)。本 repo 的對應:本機推送前是「快的檢查」;推功能分支觸發的 CI 全套是「要合併前」那一次;推到 main 的 CI 全套照舊是合併後那一次。不採:這一步不做新選測(設計審 r1);不改 GitHub 的 repo 設定(分支保護另列待決問題 Q2,由使用者決定)。

RETIRE-IF: 上線後八週內,功能分支推送觸發的 CI 全套紅的次數超過這類推送次數的三成 → 改回推功能分支時本機跑全套(來回修 CI 的時間已經比本機多跑的時間多)。數法:GitHub 的 workflow run 清單(事件 push、分支不是 main)數 conclusion,唯讀統計、不進閘。

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

- 做:①CI 也在推功能分支時觸發全套;②推送前掛鉤對功能分支的 ref 不跑全套,改跑文件子集與關鍵字子集;③「這次推的是不是主線」由 lumos 用既有的 `_push_mainlines` 判,掛鉤只讀結果;④訊息照實講;⑤說明文字同步。
- 不做:新選測演算法(第二步另開);合併後通知;GitHub repo 設定(分支保護是 Q2);主線起點算法(本機 main 過時已有 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 與 [[Systems/pitfalls-code-loop]] 的 REVISIT 2026-11-13 在追);修 `run_group` 回 3 的判法(設計審 r2 正確性席實測:執行器對「子集有選到但這片分到 0 支」回 0,只有整個子集 0 支時每片才回 3,現行判法是對的);強制全套的環境變數(要全套直接跑 `python3.14 scripts/test_lumos.py`);其他閘(合約測試真跑、新增告警、規格閘、代碼審留痕、表態)照舊。

## 做法

1. **CI 推分支也跑全套**:`ci.yml` 的 `push` 觸發從 `branches: [main]` 改成所有分支(標籤照舊另走 `security_tag`)。prep 判範圍照現行(push 事件問 lumos,只改文件就文件子集,其他全套)。push 事件以提交編號分組、不取消,之後再推的帳本提交不會取消功能提交那一次。同一個提交開了 PR 會再跑一次 PR 事件(多花機器時間,不花人的等待;第二步再處理)。
2. **lumos 判主線**:`pitfalls` 加旗標 `--push-remote <遠端名> --pushed-ref <遠端 ref>`(跟 `lumos push-range`、筆記內容閘同名同義),`--json` 多一個欄位 `pushed_mainline`。判法用 `_push_mainlines` 同一份候選(遠端 HEAD、`main`/`master` 的追蹤分支、遠端的 `main`/`master`),逐個用既有的 `_push_mainline_full` 解出指到哪條 `refs/remotes/<遠端>/<分支>`;被推的 ref 對應的那條(`refs/remotes/<--push-remote>/<被推分支>`)等於其中任一 → true。注意 `_push_mainlines` 本身會刻意跳過「就是這次被推的那條」(它是算起點用的),所以不能直接拿它的回傳值判,要抽出共用的候選清單給兩邊用。被推的 ref 不是 `refs/heads/` 底下(標籤等)→ true;git 查詢失敗 → true(算不出就當主線、照全套);其他分支 → false;沒給兩個旗標 → 不輸出這個欄位。
3. **掛鉤**:每個 ref 叫 `pitfalls` 時帶上 `--push-remote "$1" --pushed-ref "$_rref"`。這個 ref 判 `full`、`pf_json` 讀得到、而且 `pushed_mainline` 明確是 false 時,改判 `light`(沿用 `_SUITE_LIGHT`),並在這個分支裡讀 `affected_keys` 與 `autoloop_full`(跟現行 light 那一段同樣的讀法)。以下照現行全套:`pf_json` 是空的或讀不懂(pitfalls 出錯、逾時、舊版沒有這個欄位)、`pushed_mainline` 是 true 或沒有這個欄位。原本判 docs 或 light 的照舊。多個 ref 照現行「任一要全套就全套」。
4. **訊息**:迴圈結束、`_suite_mode` 定案之後才印,只印一次:最終是 light 而且至少一個 ref 是因「功能分支」降下來的 → 「推功能分支:本機只跑文件子集與關鍵字子集(關鍵字是空的就只有文件子集),全套由這次推送觸發的 CI 跑;合併前 `lumos ci-wait` 的判定要是 green(rc 0 不等於綠)」。
5. **說明文字同步**(逐處):紀律範本 `scripts/templates/graph-discipline.md` 那句「全套留給推送前的閘」改寫,再用 `lumos update` 重新注入 `CLAUDE.md` 與 `AGENTS.md` 的紀律區塊;專案 `CLAUDE.md` 紀律區塊外〈本 repo 的測試子集怎麼跑〉一段直接改;`skills/lumos-project-notes/commands/08-自動跑的.md` 的 pre-push 那句;[[Systems/bound-tests-gate]] 2026-09-18 那一行的結論改成「功能分支也走 light 跑法、CI 推分支就跑全套」;掛鉤 `_suite_word` 的說明句;父計劃 [[Projects/推送與CI提速_計劃]] 的 REVISIT 2026-11-14 那行照 [[Projects/漂移防治路線圖_計劃]] 的寫法加 `[closed:]`。使用者全域 CLAUDE.md 那句是 Q1,不由 AI 改。

## 驗收條款

- [S1] 當推送目的是功能分支、這個 ref 原本判全套、`pf_json` 讀得到而且 `pushed_mainline` 是 false 時,掛鉤 應 只跑文件子集加關鍵字子集,迴圈後只印一次「全套由這次推送觸發的 CI 跑」那行 [test:t_prepush_feature_branch_skips_full]
- [S2] 當推 main、或 `pf_json` 是空的、或沒有 `pushed_mainline` 欄位(舊版 lumos)時,掛鉤 應 照舊全套而且不印那行 [test:t_prepush_feature_branch_failclosed]
- [S3] 當同一次推送有推 main 的 ref 也有功能分支的 ref 時,掛鉤 應 全套而且不印那行 [test:t_prepush_feature_branch_mixed_with_main]
- [S4] 當給了 `--push-remote` 與 `--pushed-ref` 時,`pitfalls --json` 應 對主線(含遠端 HEAD 指的分支)回 `pushed_mainline: true`、對其他分支回 false、對標籤回 true;沒給 應 不輸出這個欄位 [test:t_pitfalls_pushed_mainline]
- [S5] 當功能分支因這條降成 light、`autoloop_full` 為真時,自主迴圈測試 應 整支跑 [test:t_prepush_feature_branch_skips_full]
- [S6] 當 `ci.yml` 被讀時,`push` 觸發 應 涵蓋所有分支、push 事件的 concurrency 應 以提交編號分組且不取消 [test:t_ci_yml_push_all_branches]
- [S7] 當紀律範本改寫後重新注入時,`CLAUDE.md` 與 `AGENTS.md` 的紀律區塊(sentinel 之間)應 跟範本逐字一致、不再有「全套留給推送前的閘」 [test:t_prepush_doc_says_ci_runs_full]

## 回退

- 掛鉤:拿掉做法 3 的降級分支(推功能分支回到本機全套);同時刪掉 S1、S3、S5 的測試(S2 留著,它驗的是全套路徑)。
- CI:`push` 觸發改回 `branches: [main]`,刪 S6 的測試。
- `pitfalls` 的 `pushed_mainline` 欄位與旗標可以留著(沒人讀就沒影響)。
- 範本那句改回原文、`lumos update` 重新注入、刪 S7 的測試。改到測試檔要重簽簽名基準(`lumos anchor approve`)。

## 實務隱患

- 守衛面:本機不跑全套,壞東西要等 CI 才看到。CI 由推送本身觸發,所以只要推上去就有全套;剩下的洞是「CI 還沒綠就合併」——main 沒有分支保護,靠「合併前 `lumos ci-wait` 判定 green」這條既有規矩(rc 0 不等於綠)。要機械擋就是 Q2 的分支保護。
- 算不出來的方向:`pf_json` 空、舊版沒欄位一律照全套(做法 3),保住現行「算不出就多跑」。
- 機器時間:功能分支每次推都跑一次 CI 全套(約 15–20 分、8 台),開了 PR 的提交會再多一次 PR 事件。不讓人等,但 GitHub Actions 的用量會變多;公開 repo 的標準 runner 不計費(https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions),私有化時要重估。
- 併發:多個會談各自推分支,各自觸發 CI,互不取消(以提交編號分組)。
- 版本錯開:新掛鉤配舊 lumos(沒有 `pushed_mainline`)→ 全套;舊掛鉤配新 lumos → 舊掛鉤不帶旗標、不讀新欄位,照舊。
- 已排除:金流:不碰付款或計費。
- 已排除:對外送出:不開 Issue、不新增對外呼叫;CI 多跑的只是本 repo 的測試。
- 已排除:不可逆:掛鉤、CI 設定、範本都能還原。

## 審計修正紀錄

- r1(2026-11-05,6 席:正確性、邊界、平台、合約圖譜、通才、架構對齊,皆 sonnet):45 條/blocking 25 條/靜態關鍵字選測先天漏抓、通知機制做不出來、引入第二套做法;查過世界解後換形狀成兩步走,這篇只做本機不跑全套,選測移到 [[Projects/依實測覆蓋挑測試_計劃]]。例:改到一個沒有任何測試整字提到的輔助函式(主程式 62.6% 屬此類)→ 舊設計只選中 0 支測試就放行;新設計本機只跑小子集、PR 的 CI 跑全套才合併。卷證 governance/review-reports/推送只跑受影響測試/
- r2(2026-11-05,6 席:正確性、邊界、合約圖譜、通才、流程、架構對齊,皆 sonnet):30 條/blocking 18 條/換形狀後的小設計仍有洞:沒開 PR 時 CI 不跑、算不出來與守衛檔情境反而降級、掛鉤自己認主線是第三套做法、`run_group` 修法前提不成立、撤除條件量不到。改成推功能分支就觸發 CI 全套、算不出來照全套、主線改由 lumos 用 `_push_mainlines` 判、拿掉 `run_group` 那段、撤除條件改數 GitHub run。例:推功能分支後還沒開 PR → 舊設計本機只跑小子集、CI 也不跑;新設計這次推送就觸發 CI 全套。卷證 governance/review-reports/推送只跑受影響測試/

REVISIT:2026-12-31 上線八週左右,照 RETIRE-IF 數功能分支推送觸發的 CI 全套紅的比例
