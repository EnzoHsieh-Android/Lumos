---
type: issue
status: open
created: 2026-10-03
updated: 2026-10-04
self_audit: gpt-5.6-sol/2026-10-04
aliases: []
about_code:
  - scripts/scenario_probe.py
tags:
  - type/issue
  - status/open
  - scope/evals
summary: |-
  FLAG: TECHNICAL
  PITFALL: 環境注入與頂層absolute gitfile已局部修補；local/worktree設定及巢狀Git仍可繞過副本隔離。兩版臨時repo重現見 [[Verification/2026-10-04_修復穩定性試行第1案例外續修]] 與本文最新節。
  WHY: 使用者曾授權一次第4輪；審查仍FAIL、未部署，下一次同案工作先界定修補與審查輪次。出處 [[Projects/代碼審修復穩定性試行_計劃]]。
related:
  - "[[Verification/2026-10-03_修復穩定性試行第1案續辦]]"
  - "[[Systems/codex-harness]]"
  - "[[Verification/2026-10-04_修復穩定性試行第1案例外續修]]"
---
# 探針Git隔離的設定與絕對路徑缺口

FLAG: TECHNICAL

PITFALL: 2026-10-03 試行第1案第三輪發現 Git 設定注入與副本 Git 絕對路徑兩個既有漏網輸入；來源 [[Verification/2026-10-03_修復穩定性試行第1案續辦]]。重現步驟與修前後輸出存於 governance/review-reports/code-repair-pilot-01/r3-parent-reproduction.md，兩版都成立，未執行網路或真推送。

## 症狀

R3-B1／資安 Finding 1：環境注入 remote 與 core.hooksPath 後，本機 push --dry-run 從控制組 rc1 變成 rc0，副本原本的防推 hook 被繞過；臨時 bare repo 仍空。邊界席報 major、資安席報 blocker，保留較高等級，沒有把未發生的外部寫入說成事故。

資安 Finding 2：來源的 .git 檔以絕對路徑指向來源內部 .hidden-git 時，建立副本會刪掉來源 remote、改寫來源 hooksPath、推進來源 HEAD。只在自建臨時來源驗證，沒有改動真專案。

## 根因

前者是只清 Git 定位環境變數，沒有隔離 command-scope config；後者是只驗來源 gitdir 位於來源內，複製後沒有再驗副本 gitdir。來源內 absolute indirection 通過原正面条件，複製後仍指回來源。兩個輸入在 1c91755a 與 4a60b231 皆壞，歸原有漏看；不能把本輪新增呼叫頻率當成首次引入。

## 現在怎麼繞

本案未放行、未部署，停止真模型探針；保留本機候選及失敗卷證供裁決。不得把只驗過 GIT_DIR/GIT_WORK_TREE 的測試，擴張成所有 Git 環境與目錄形狀都安全。舊 [[Issues/探針以工作樹為來源會改到本體]] 的來源外 gitdir 修復仍成立，本篇記不同的漏網輸入。

## 什麼條件算修好

先裁決三輪上限後的修復範圍；重啟入口為本 Issue 與試行計劃。要求設定注入不能恢復有效 remote 或覆蓋防推 hook，兩 runner 都驗；任何副本 Git 寫入前驗副本 gitdir 確實隔離，拒絕絕對指回來源的反例，並驗普通 clone 的正常路徑。全部用臨時 repo 驗來源設定、檔案、HEAD 不變；通過授權範圍的審查後才可談部署。

REVISIT:2026-11-03 隨五案試行回顧檢查本案未決隔離缺口與重啟裁決。

## 2026-10-04 第四輪後仍開放

以上是第3輪停手時的排查紀錄。使用者已明確授權修三缺口加唯一第4輪，局部修補與回歸測試完成，卻在同輪再見仍可繞過的合法Git資料形狀；最新證據見 [[Verification/2026-10-04_修復穩定性試行第1案例外續修]]、r4-intake.md及r4-parent-reproduction.json。來源與副本路徑的頂層檢查擋住先前絕對gitfile/commondir/符號連結反例；環境GIT_CONFIG注入也被清洗，但來源local include與worktree scope設定可讓副本保留有效remote並覆蓋防推勾子。正常子模組仍保留自己的remote，臨時副本子模組向本機bare新增ref；兩者在637989b1及8922c3c9都成立，屬舊漏看／本輪隔離邊界修補不完整，不是這一輪首次引入。資安席另指出絕對巢狀gitfile可能指回來源；該特定變體未實跑，不能冒稱已證。

目前繞法：不執行真模型探針，不把此候選分支當成可安全推出的沙盒；測試只用臨時repo及本機bare。修好條件是建立副本後真正生效的remote為空、防推勾子有效，巢狀Git也不能寫出副本或推出；任何Git清理失敗應在啟動模型前停止。需要以local include、worktree config、正常子模組及頂層好例做相同修前後驗證，並檢查拒絕後來源byte-equal。第4輪處置閘FAIL且授權輪次用盡，後續同案工作先界定修補與審查輪次，不自動開r5。
