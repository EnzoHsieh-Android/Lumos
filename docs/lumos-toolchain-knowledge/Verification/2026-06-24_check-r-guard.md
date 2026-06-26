---
type: verification
status: pass
feature: "[[Systems/check-r-guard]]"
commit: eb73b22
date: 2026-06-24
valid_under:
  - "doctor/lint Check R 對 ★IRREVERSIBLE★ 兩軌(rollback/guard)任一合規放行、兩軌皆無報 error"
  - "★CHECKPOINT★ 行為不變(有 guard 靜默忽略、無 rollback 仍軟提醒)"
revalidate_when:
  - "extract_reversibility tuple 形狀或 _guard_resolved/_rollback_resolved 判定條件改動"
  - "Check R(doctor:625 / lint:1230)inner 分支結構改動"
  - "v2 支援 [guard:non-decisions-ref] 或新增 marker"
summary: |-
  Check R [guard:decisions] 事前預防路徑驗證:design-loop 3 輪收斂(canary 3/3 全中、跨家族複核 2 輪 endorsed)+ Python 回歸測試(doctor/lint/漂移守衛)全綠。
---
# Verification: check-r-guard

## design-loop 收斂證據(2026-06-24)
- CONVERGED:3 輪 adversarial 審計,canary 3/3 全中(審計員每輪都抓到偷植瑕疵)、r2+r3 連 2 good 自動收斂;跨家族複核 2 輪 endorsed。
- r1 揪出 F-DRIFT(major,漂移測試宣稱不成立)+ F-CHECKPOINT(minor,共用條件誤消軟提醒),均折入。
- r2/r3 折入 minor(型別守衛 inner-delta 釐清、組件同 commit、命名正交辯方反證、測試斷言補強)。
- 跨家族複核 Finding H(major)經辯方反證為假陽性(marker 集合封閉);Finding A(minor)措辭提醒接受。

## 回歸測試(`scripts/test_lumos.py`,subprocess 風格)
- `t_reversibility_guard_doctor`(`:1128`):IRREVERSIBLE + 非空 guard → doctor `--ci` rc0;兩軌皆無 → error 且訊息含 `[guard:decisions]` 與 `[rollback:decisions]`。
- `t_reversibility_lint`(`:1061`):IRREVERSIBLE + 非空 guard → rc0;空 guard → rc1;rollback+guard 雙保險 → rc0;CHECKPOINT + guard → guard 靜默忽略、無 rollback 仍軟提醒。
- `t_marker_doc_sync`(`:1195`):tuple 含 `"[guard:"`,斷言其同時出現在 `graph-discipline.md` 與 `SKILL.md`(漂移守衛)。

## 結論
PASS——機制按分支真值表行為,事前/事後兩軌與 CHECKPOINT 隔離均有測試覆蓋,知識同步有漂移守衛。
