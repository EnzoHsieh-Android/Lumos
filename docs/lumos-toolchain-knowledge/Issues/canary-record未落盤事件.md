---
type: issue
status: open
created: 2026-07-29
updated: 2026-07-29
tags:
  - type/issue
  - status/open
related:
  - "[[Systems/canary-audit]]"
pitfall_when:
  - "content:canary record"
summary: |-
  FLAG:TECHNICAL
  KEY:2026-07-28 code-testmap r2 三筆 canary record 工具回報成功(印出 CANARY-ae139e51/521d397f/031e7381)但檔案系統與 git 全史皆無落盤痕跡——外審對話輪(Codex round1 Q3)清點原始帳時發現;已依 design-loop skill 中斷恢復條款補記(c7f22351/b633e6bf/5375e20d,note 明標補記)
  KEY:影響——審計帳「可稽核性」宣稱在該窗口不成立;「11 席 10 中」統計已降級敘述為「8 筆原生+3 筆補記」
  KEY:待查方向——①record 寫入的 vault/log 路徑解析是否受 cwd 影響(當時 session 有多次 cwd 漂移)②寫後是否缺 readback 自驗(嫌疑最大:回報成功僅代表函式跑完,未證檔案已 append)③硬化案=record 輸出印落盤絕對路徑+append 後讀回驗證該行存在(對齊「寫後自驗」家規),綁測試
  DECISION:[2026-07-29]補記走明標路線(note 註明佚失事件+證據源),不偽裝原生紀錄——帳的誠實優先於帳的漂亮
---
# canary record 未落盤事件（2026-07-29）

外審對話輪清點 `docs/.canary-log.jsonl` 時發現 code-testmap r2 三筆紀錄缺失；當時工具輸出「✓ canary caught 留痕: CANARY-ae139e51…」三行，但該三 ID 於檔案系統（含 /tmp、scratchpad）與 git 全史（`git log --all -S`）零命中——回報成功、實未落盤。

## 復原與後續

- 已補記三筆（note 明標補記與證據源）；「11 席 10 中」相關敘述降級。
- 硬化票（待辦）：`canary record` 輸出改印落盤絕對路徑，且 append 後讀回驗證該行存在、驗不到即 rc 非 0 報錯——「寫後自驗」家規本應覆蓋此路徑而未覆蓋。
- 根因調查（待辦）：重現 cwd 漂移情境下的 vault 解析行為。
