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

> 白話:現在推一個改到程式的功能分支,本機推送前要跑完 3700 多支測試(四片同時跑,平常 5–10 分,2026-11-05 實測一次一小時以上),PR 的 CI 又全套跑一次。這篇是兩步走的第一步:**推功能分支時本機不跑全套**,只跑便宜的檢查與現行的關鍵字小子集(當冒煙測試,不當保證);全套照舊由 PR 的 CI 跑,合併前要綠。第二步(靠「每支測試上次碰過哪些函式」挑測試,讓 PR 的 CI 也能少跑)另開 [[Projects/依實測覆蓋挑測試_計劃]]。使用者原話(2026-11-05):「是不是可以不要每次開發新功能就把既有的斷言全部跑過一遍?如果後續造成什麼功能壞掉,在返休就好了」;設計審 r1 指出靜態選測先天漏抓、查過世界解之後,使用者同意「兩步走」。這也是 [[Projects/推送與CI提速_計劃]] 留下的第二階段(那篇 REVISIT 寫「開第二階段(本機推功能分支不跑全套)」)。

PRIOR-ART: 兩段式 CI:快的檢查每次推送跑、完整測試只在要合併前跑一次(Mergify 兩段式做法 https://docs.mergify.com/merge-queue/two-step.md ;Fides 專案因「每支測試跑兩次」拿掉其中一次 https://github.com/ethyca/fides/pull/7672 );Martin Fowler:合併前測過的,合併後在 CI 也要再測(https://martinfowler.com/articles/rise-test-impact-analysis.html)。本 repo 的對應:本機推送前是「每次推送」那一段、PR 的 CI 全套是「要合併前」那一段;推到 main 的 CI 全套照舊是合併後那一次。不採:這一步不做任何新選測(設計審 r1 量到靜態關鍵字選測漏得很兇,見〈審計修正紀錄〉);不改 CI。

RETIRE-IF: 上線後八週內,功能分支的 PR 在 CI 全套紅、而且同一個提交的本機推送前檢查是綠的,累計超過 PR 數的三成 → 改回推功能分支時本機跑全套(來回修 CI 的時間已經比本機多跑的時間多)。數法:`lumos ci-status` 記進治理帳的 PR 結果,對照同提交的推送前檢查紀錄。

## 舊否決對照

- [[Projects/CI加速_計劃]](2026-10-06)否決「只跑受影響的測試子集」(覆蓋變少)與「本機全綠就不等 CI 先合併」(要改全域規則)。這一步不同:全套沒有變少,只是不在本機跑,PR 的 CI 照跑,合併前照等;所以兩條舊否決的理由都不成立。

## 現況(2026-11-05 量)

- 推送前掛鉤(`scripts/hooks/pre-push` 的測試套件閘):每個 ref 由 `lumos pitfalls --diff <範圍> --json` 的 `suite` 判範圍。只改文件 → 文件子集;改到程式但 `spec-gate --push-check` 判成 light 而且 `light_ok` → 文件子集加關鍵字子集(`--suite keys`;抽不出關鍵字就只跑文件子集),自主迴圈照 `autoloop_full`;其他一律全套,切四片同時跑。任何一個 ref 要全套就全套。
- 改了測試檔,測試檔簽名基準 `governance/anchor-baseline.json` 就跟著變;它在守衛檔清單 `_DOCS_ONLY_NEVER`,所以幾乎每個功能推送都判成全套。
- CI(`.github/workflows/ci.yml`):PR 事件一律全套(16 份給 8 台);推到 main 只改文件跑文件子集,其餘全套。
- main 沒有設分支保護(`gh api repos/<repo>/branches/main/protection` 回 404):CI 紅也能合併,合不合併靠人或 AI 先跑 `lumos ci-wait`。

FACT:PR #158 合併後 CI 第 10 份耗時 1217 秒,同次本機推送前全套約一小時 [來源:生產] [confirmed:2026-11-05]
FACT:main 沒有分支保護 [來源:外部] [confirmed:2026-11-05] [查:gh api repos/EnzoHsieh-Android/Lumos/branches/main/protection]

## 範圍

- 做:推送目的 ref 是功能分支時,本機推送前測試套件閘不跑全套,改跑現行 light 那一套(文件子集 + 關鍵字子集 + 自主迴圈規則);印一行講清楚全套由 PR 的 CI 跑、合併前要綠;順手修掉 light 現行的誤導訊息;說明文字同步。
- 不做:新選測演算法(第二步另開);CI 任何改動;合併後通知;主線起點算法(本機 main 過時的問題已有 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 與 [[Systems/pitfalls-code-loop]] 的 REVISIT 2026-11-13 在追,不在這裡另開一條);強制全套的環境變數(要全套直接跑 `python3.14 scripts/test_lumos.py`);其他閘(合約測試真跑、新增告警、規格閘、代碼審留痕、表態)照舊。

## 做法

1. **認功能分支**:掛鉤每個 ref 迴圈裡已經有遠端目的 ref(`_rref`)。目的是 `refs/heads/<名>` 而且名字不是 `main` 或 `master` → 這個 ref 算功能分支;其他(推 main/master、標籤、別的 ref 形狀)照現行。判斷寫在掛鉤裡、用字串比對,跟掛鉤現有「`refs/heads/*` → 分支」的判法同一處同一種寫法,不另寫 lumos 子指令。
2. **功能分支降成 light 跑法**:這個 ref 原本判 `full` 時改判 `light`(沿用 `_SUITE_LIGHT`,不新增狀態);關鍵字照現行從 `pf_json` 的 `affected_keys` 取、自主迴圈照現行 `autoloop_full`。判 `docs` 的照舊 docs。多個 ref 一起推:照現行「任何一個要全套就全套」——同一次推送有推 main 的 ref,就全套。
3. **訊息**:功能分支因這條降成 light 時,印一行「推功能分支:本機只跑文件子集與跟改動有關的測試,全套由 PR 的 CI 跑;合併前要 `lumos ci-wait` 綠」。
4. **修 light 現行的誤導**:`run_group` 只要任一片回 3(這片分到 0 支)就整組回 3,選中支數比片數少時必有空片,掛鉤就印「沒有測試提到這次改到的函式或檔名」——但其實有選到、也跑了。改成每片都回 3 才算一支都沒選到(那個宣告了沒用到的 `_krc_all3` 就是原本的意圖)。
5. **說明文字同步**:紀律範本 `scripts/templates/graph-discipline.md` 裡「全套留給推送前的閘」改寫成新規則,再用安裝程式重新注入 `CLAUDE.md` 與 `AGENTS.md`(紀律區塊靠範本注入,不手改);專案 CLAUDE.md 自己的〈本 repo 的測試子集怎麼跑〉一段(紀律區塊外)直接改;[[Systems/bound-tests-gate]] 2026-09-18 那行「CI 對 light 照跑全套當後盾」補一句功能分支也走這條;父計劃 [[Projects/推送與CI提速_計劃]] 的 REVISIT 2026-11-14「開第二階段」那行加 `[closed:]` 指向這篇。

## 驗收條款

- [S1] 當推送目的是功能分支、這個 ref 原本判全套時,推送前掛鉤 應 只跑文件子集加關鍵字子集、應 印「全套由 PR 的 CI 跑」那行;同一次推送另有推 main 的 ref 時 應 照舊全套;推 main 時 應 照舊全套;推標籤時 應 照現行 [test:t_prepush_feature_branch_skips_full]
- [S2] 當關鍵字子集選中的支數比片數少時,掛鉤 應 不印「沒有測試提到」;每片都選中 0 支時 應 照舊印 [test:t_prepush_keys_fewer_than_shards_no_false_alarm]
- [S3] 當功能分支推送判成 light 跑法、而 `autoloop_full` 為真時,自主迴圈測試 應 整支跑(照現行 light 規則) [test:t_prepush_feature_branch_skips_full]
- [S4] 當紀律範本改寫後重新注入時,`CLAUDE.md` 與 `AGENTS.md` 的紀律區塊 應 跟範本逐字一致,不再出現「全套留給推送前的閘」 [test:t_prepush_doc_says_ci_runs_full]

## 回退

- 把掛鉤裡「功能分支降成 light」那一段拿掉,就回到推功能分支本機跑全套;範本那句改回原文再重新注入。

## 實務隱患

- 守衛面:本機不跑全套,壞東西要等 PR 的 CI 才看到;main 沒有分支保護,CI 還沒綠就合併的話會直接進主線。補救是〈待決問題〉Q2(要不要開分支保護、把 CI 設成必過);在那之前靠「合併前先 `lumos ci-wait`」這條既有規矩。
- 時間:PR 的 CI 全套約 15–20 分(16 份給 8 台);這段在背景跑,推完可以先做別的,合併前才等。
- 已排除:金流:只動推送前要跑哪些測試,不碰付款或計費。
- 已排除:對外送出:不改 CI、不開 Issue、不新增對外呼叫。
- 已排除:不可逆:掛鉤一段程式與一句說明,都能直接還原。
- 併發:多個會談同時推各自的功能分支,各自只跑小子集,本機負載比現在低。
- 舊掛鉤配新 lumos、新掛鉤配舊 lumos:這篇只改掛鉤本身與範本,不改 `pitfalls --json` 的欄位,兩邊錯開不影響判定。

## 審計修正紀錄

- r1(2026-11-05,6 席:正確性、邊界、平台、合約圖譜、通才、架構對齊,皆 sonnet):45 條/blocking 25 條/靜態關鍵字選測先天漏抓、通知機制做不出來、引入第二套做法;查過世界解後換形狀成兩步走,這篇只做本機不跑全套,選測移到 [[Projects/依實測覆蓋挑測試_計劃]]。例:改到一個沒有任何測試整字提到的輔助函式(主程式 62.6% 屬此類)→ 舊設計只選中 0 支測試就放行;新設計本機只跑小子集、PR 的 CI 跑全套才合併。卷證 governance/review-reports/推送只跑受影響測試/

REVISIT:2026-12-31 上線八週左右,照 RETIRE-IF 數 PR 的 CI 紅而本機綠的比例
