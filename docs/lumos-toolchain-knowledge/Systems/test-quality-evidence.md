---
type: system
status: done
created: 2026-10-07
updated: 2026-10-07
responsibility: 固定可信案例驗證測試判準的互補性與各棧接入標準；不執行模型輸出或自動裁決業務答案
self_audit: GPT-6-Codex-clean-agent/2026-10-08
aliases: []
about_code:
  - governance/eval/test_quality_evidence.py
tags:
  - type/system
  - status/done
  - scope/evals
summary: |-
  WHY: 分開判準來源、抓錯與重構證據 [出處:2026-10-07 使用者要求實驗轉成各棧接入標準] [因:重抄算法可與独立答案呈現相同紅綠結果，故障證據不能替代來源核對]
verified_by:
  - "[[Verification/2026-10-07_測試三項證據固定實驗]]"
  - "[[Verification/2026-10-08_PHP與Laravel測試接入規格核對]]"
related:
  - "[[Systems/test-quality-scan]]"
  - "[[Systems/test-quality-multilang]]"
---
# test-quality-evidence

## 決定與用途

WHY: 三項證據分工而不合成真假分數 [出處:[[Verification/2026-10-07_測試三項證據固定實驗]]] [因:同算法expected能抓程式故障，甚至承受重構，但無法獨立挑戰同一業務誤解]。共用接入標準保留來源人工審查；工具只報其可驗的執行事實。

固定合成 runner 的責任在 `governance/eval/test_quality_evidence.py`，只接受新输出目錄，固定可信來源而不執行模型輸出；不是通用沙盒。語言差異用同一需求與事前已知結果做示範，不把多格排列當独立實驗事件。

重構檢查僅對疑似耦合的行為測試實跑；結構測試依其實際合約裁判。一般開發不要求每輪加做重構或全套mutation，避免機械往返反增審查成本。

來源：Oracle Problem Survey https://discovery.ucl.ac.uk/id/eprint/1471263/ ；Google Change-Detector Tests https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html 。各棧接入需求在共用手冊，平台支援边界見 [[Systems/test-quality-multilang]]。
REVISIT:2026-10-21 核對第一個真專案原生runner是否完成負例資格考卷，再裁是否擴大接入或修訂標準。

## PHP／Laravel 接入取捨

WHY: Laravel接入另驗框架情境與fake邊界 [出處:2026-10-08 使用者補充PHP/Laravel及官方測試文件] [因:純PHP斷言不能證明HTTP授權、Eloquent事件或真queue進場，工具分數也不能證明expected來源獨立]。Unit／Feature、PHPUnit／Pest、資料庫與fake範圍分開留證；共用撰寫原則沿同一標準。
REVISIT:2026-10-21 PHP／Laravel標準目前是planned的文件接入規格，第一個消費專案固定版本後跑原生負例資格考卷；不得拿Python/Node固定機制實驗或其他語言掃描結果代替。
