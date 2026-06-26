---
type: verification
status: pass
feature: "[[Systems/doctor-irreversible-hint]]"
commit: 2482746
date: 2026-06-25
valid_under:
  - "scripts/test_lumos.py t_check_h_irreversible_hint 全 7 案例綠(整套 258 passed, 0 failed,macOS)"
  - "git diff 標準 +++ b/ 前綴(非 diff.noprefix/mnemonicPrefix)"
revalidate_when:
  - "IRREVERSIBLE_HINT_PATTERNS 增刪 pattern"
  - "_scan_diff_for_irreversible_hints 的掃描範圍/過濾邏輯改動"
  - "run_doctor 的 ci 旗標分派或 section 插入點變動"
---
# Verification:doctor-irreversible-hint(Check H)

`scripts/test_lumos.py:t_check_h_irreversible_hint` 7 案例,跑全套 `python3 scripts/test_lumos.py` → **258 passed, 0 failed**(macOS)。

| # | 案例 | 斷言 | 結果 |
|---|---|---|---|
| 1 | smoke | staged `requests.post("https://prod.api.com/charge")` → 報「疑似碰外部不可逆」 | ✓ |
| 2 | filter test-file | staged `test_email.py` 含 `sendmail(...)` → 不報 | ✓ |
| 3 | filter comment | staged 純注解 `# sendgrid.send(...)` → 不報 | ✓ |
| 4 | config-file | staged `config.yaml` 含 `prod.stripe` → 報(SKIP_EXT 不排 .yaml) | ✓ |
| 5 | no-ci | `--strict`(無 `--ci`)→ 印「互動模式略過」、不掃 | ✓ |
| 6 | non-git | 普通 vault(非 git repo)→ 靜默無疑似、不崩 | ✓ |
| 7 | initial-commit | 只有初始 commit、無 parent → `HEAD~1..HEAD` rc≠0 → 靜默回 [] | ✓ |

## design-loop 收斂證據
設計稿 `docs/design/2026-06-25-doctor-irreversible-hint.md` 尾段:5 輪 canary 對抗審計每輪 caught + cross-audit 1 輪(qwen,2 FALSE POSITIVE 自 grep 駁回、1 TRUE 折修)。關鍵真 blocker:r1-F1(module-level helper 缺 `import subprocess` → NameError)。
