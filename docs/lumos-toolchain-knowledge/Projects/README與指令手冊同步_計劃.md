---
type: project
status: done
created: 2026-10-07
updated: 2026-10-07
tags:
  - type/project
  - status/done
  - scope/ux-docs-hygiene
verified_by:
  - "[[Verification/2026-10-07_README更新清點]]"
lands_in:
  - Systems/lumos-cli-read
---
# README與指令手冊同步_計劃

## 目標與範圍

使用者先要求清點10/1起更新與README落差，再要求找出有指令但Claude／Codex不知道如何使用的入口，兩項改動一起提交。保留來源提交的完整更新帳，公開文件只補使用者能理解的能力與邊界，共用手冊補操作時機、路徑、結果判讀與接線方式。

PRIOR-ART:沿用既有README分段、共用情境指令索引及各功能CLI help，不另建一份規則或指令定義。
RETIRE-IF:後續同一項能力已移到唯一來源教學入口，移除本次過渡說明與重複列舉，保留歷史更新帳作版本證據。

這次只有文件、工作指引與驗證脈絡，沒有新增閘或改程式行為；小改動跳過設計審，交由文件子集、連結／CLI入口檢查與獨立架構對齊審核。

## 驗收

- 固定來源與時區的完整提交清單，將未合併及研究更新分開列。[manual:重算Git提交與表格列數]
- 中英文README新增能力相符，提醒、硬閘、離線分析與發布界線不混淆。[manual:逐段對照實作與來源]
- 新CLI與獨立評測入口在兩家共用手冊可找到，且提供時機、用法與結果判讀。[manual:CLI差異清單與手冊路由核對]
- 文件檢查通過，驗證紀錄附有效前提與重驗時機。[manual:文件子集、lint、doctor與審查報告]
