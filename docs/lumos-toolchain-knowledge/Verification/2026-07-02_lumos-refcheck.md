---
type: verification
status: pass
created: 2026-07-02
updated: 2026-07-02
tags:
  - type/verification
  - status/pass
related:
  - "[[Systems/lumos-refcheck]]"
valid_under: scripts/lumos cmd_refcheck(FENCE_RE/INLINE_CODE_RE 抽取 + (token,line) 去重 + rc 0/1/2);消費端=orchestrator-prompt §2.8/§2.5a + design-loop SKILL 步驟 2.5
revalidate_when: 改 cmd_refcheck 抽取/核對/rc 邏輯;改 Check P 抽取規則(同源複製,需比對分歧是否仍刻意);改 orchestrator-prompt §2 步驟結構
summary: |-
  TEST:t_refcheck 14 checks 全綠(missing/ok+excerpt 精確比對/line_out_of_range/範圍 2-4 首尾行/同檔多行號 4 claims 不塌/目錄型 dir 註記/url·非頂層·無斜線·glob·fenced 全跳/統計欄位/rc 0·1·2/人讀版);294 passed 0 failed 無回歸(doctor Check P 行為不變)
  VERIFY:真 spec smoke——refcheck docs/design/2026-07-02-spec-refcheck.md 座標核對可跑
---
# 2026-07-02 lumos-refcheck 驗證

`python3 scripts/test_lumos.py`:t_refcheck 14 checks 全綠,294 passed 0 failed(既有測試無回歸)。
真 spec smoke:`./scripts/lumos refcheck docs/design/2026-07-02-spec-refcheck.md --repo .` 正常輸出 manifest 與統計。
消費端接線以 grep 驗證:orchestrator-prompt.md ≥4 處 refcheck 措辭、SKILL.md ≥3 處、methodology/project-notes 各 ≥1。
