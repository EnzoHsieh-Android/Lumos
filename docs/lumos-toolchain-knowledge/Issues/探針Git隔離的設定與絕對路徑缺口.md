---
type: issue
status: open
created: 2026-10-03
updated: 2026-10-03
self_audit: gpt-5.6-sol/2026-10-03
aliases: []
about_code:
  - scripts/scenario_probe.py
tags:
  - type/issue
  - status/open
  - scope/evals
summary: |-
  FLAG: TECHNICAL
  PITFALL: Git設定注入與absolute gitfile會繞過副本隔離，修前後皆在臨時repo重現；來源與重現見 [[Verification/2026-10-03_修復穩定性試行第1案續辦]] 及本文。
  WHY: 三輪用滿仍有阻擋缺口，未部署；先由使用者裁決後續範圍，入口為本Issue與試行計劃。出處 [[Verification/2026-10-03_修復穩定性試行第1案續辦]]。
related:
  - "[[Verification/2026-10-03_修復穩定性試行第1案續辦]]"
  - "[[Systems/codex-harness]]"
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
