---
type: verification
status: pass
feature: reversibility-governance-ledger
commit: e3edaf3
date: 2026-06-26
valid_under:
  - macOS / python3 / lumos test_lumos.py subprocess harness
  - vault 為全專案結構(root/docs/<slug>-knowledge),gov 測用此非 bare mkvault
revalidate_when:
  - 動到 extract_reversibility / _rollback_resolved / _guard_resolved / parse_decisions 的 rollback/guard 解析
  - 動到 run_doctor 的 warn_soft / Check R / Check H 或 cmd_gov 四來源 dedup
  - 新增/改 ★IRREVERSIBLE★ / ★CHECKPOINT★ / [rollback:] / [guard:] marker 字串(需同步 graph-discipline + SKILL.md,漂移測試守)
---
# Verification: reversibility-governance-ledger

驗 [[Systems/reversibility-governance-ledger]] 的可逆性 Check R + 治理帳 `lumos gov`。

## 證據
- **全測**：`python3 scripts/test_lumos.py` → **258 passed, 0 failed**(macOS)。
- **design-loop**：四輪 fresh-agent 對抗審計，第四輪 CONVERGED（三輪修正逐一對著 code 驗證屬實：ci 參數 plumbing、warn_soft 保 rc0、parse_decisions 吃 rollback、env.vault.parent=docs/）。詳見設計稿末。

## 對應回歸測試（test_lumos.py）
- `t_reversibility_lint`：`★IRREVERSIBLE★` 缺回退 → rc1「缺實質回退」；`[rollback:decisions]` + decisions 有非空 → rc0；標 Issue → 標錯型別；`[guard:decisions]` 兩軌。
- `t_reversibility_doctor`：只有 `★CHECKPOINT★` 缺回退 → doctor `--ci` 仍 **rc0**(驗 warn_soft 不誤計 issues)。
- `t_reversibility_guard_doctor`：`[guard:decisions]` 有非空 guard → 放行;無守衛 → 擋。
- `t_governance_log_write`：doctor `--ci` 對 `★IRREVERSIBLE★` 缺回退 → 寫 `.governance-log.jsonl`(含 `check-r`)。
- `t_gov_query`：全專案結構 fixture 三/四來源合併、stem 比對、`gov <node>` 命中 governance-log 事件。
- 漂移測試：marker 字串(`★CHECKPOINT★`/`★IRREVERSIBLE★`/`[rollback:`/`[guard:`)須同時出現在 SKILL.md 與 graph-discipline.md;skills 不存在(vendored)則優雅跳過。

## 限界
- subprocess-only harness：`parse_decisions` 讀 `rollback`/`guard`(含 block scalar)走 Check R 整合測間接驗。
- 工具天花板:這些測證明「強制路徑成立」,不證明寫下的 rollback/guard 步驟真能執行回退。
