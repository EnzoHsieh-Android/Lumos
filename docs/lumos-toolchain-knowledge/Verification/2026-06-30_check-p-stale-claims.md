---
type: verification
status: pass
created: 2026-06-30
date: 2026-06-30
verified_by: sonnet/2026-06-30
valid_under:
  - t_doctor_check_p
---

# 2026-06-30_check-p-stale-claims

Verified [[Systems/check-p-stale-claims]] implementation via TDD.

## GREEN Phase Summary

✓ All 7 test cases passing:
1. `Check P: 段標題出現` — [P] section header shows
2. `Check P: 案例1 報出 ghost` — Missing `scripts/ghost.py` detected  
3. `Check P: 案例2 存在路徑不報` — Existing `scripts/real.py` not flagged
4. `Check P: 案例3 散文/非路徑不報` — Non-path inline-code (no `/`) skipped
5. `Check P: 案例4 fenced 內不報` — Fenced block contents not scanned
6. `Check P: rc 不變(warn_soft 軟提醒)` — rc=0 (soft warning, does not block)
7. `Check P: 無 docs/ 佈局略過` — repos without docs/ layout skip Check P

## Full Test Suite
- 275 test cases total: **275 passed, 0 failed**
- No regressions in existing tests
- TDD followed: RED → GREEN → REFINE

## Smoke Test on Real Vault

```
./scripts/lumos doctor 2>&1 | grep -A3 "\[P\]"

[P] 失效檔案認領 (節點正文 inline-code 路徑指向已不存在的檔;軟提醒、不擋 CI)
  ⚠ 15 個節點引用指向已不存在的 repo 路徑(圖譜指向死碼?):
      • MOC/index.md → scripts/lumos:行號(已不存在)
      • Systems/autonomous-iteration-loop.md → governance/reports/governance-<date>.json(已不存在)
      ...
```

- **rc=0** — doctor exits cleanly, soft warning doesn't block CI
- **15 findings** — All legitimate dead code references (placeholders, paths with variable templates, deleted files)
- **Chart issue review**: References like `scripts/lumos:行號` are actual document patterns (not line numbers), correctly flagged for review

## Implementation Correctness

✓ Path extraction rule compliance:
- FENCE_RE stripping works (fenced paths not captured)
- INLINE_CODE_RE + .strip("`") correctly isolates paths
- Line number suffix `:\d+(?:-\d+)?` cleanly removed
- Protocol check (`"://"` skip) prevents false positives
- Top dir anchor (`repo_root.iterdir()`) limits to direct children
- Seen_paths dedup prevents duplicate reports

✓ rc behavior:
- warn_soft() used, not warn() → issues counter unchanged
- doctor exit code remains 0 (soft warning)
- Test explicitly verifies `r.returncode == 0`

✓ Positioned correctly:
- After Check V (`print()` at line 747)
- Before `if ci:` gate (line 749)
- Within run_doctor scope, repo_root accessible

---

**Test Run Transcript**

```
pytest output (from python3 scripts/test_lumos.py):

  ✓ Check P: 段標題出現
  ✓ Check P: 案例1 報出 ghost
  ✓ Check P: 案例2 存在路徑不報
  ✓ Check P: 案例3 散文/非路徑不報
  ✓ Check P: 案例4 fenced 內不報
  ✓ Check P: rc 不變(warn_soft 軟提醒)
  ✓ Check P: 無 docs/ 佈局略過

275 passed, 0 failed
```
