# Review: delguard changes (scripts/lumos) — r1-diff.patch

Scope: `_delguard_log_degraded`, the `subprocess.TimeoutExpired` except clause, the
generic-error-branch vault resolution, `LUMOS_DELGUARD_DEADLINE` 2.0→5.0, `_KNOWN_GATES`
+ `"delguard"`. Reviewed as an outside contributor's PR against the real files at HEAD
(2859ed7), not just the patch text.

## Finding 1 — MAJOR: error-branch vault re-resolution writes the ledger outside the repo for standalone-vault layouts

`cmd_delguard_check`'s `except Exception as e:` block (scripts/lumos:11686-11698) re-derives
`_gr` when the exception fired before `gr` was bound:

```python
except Exception as e:
    _gr = locals().get("gr")
    if not _gr:
        try:
            _gr = find_vault(Path(str(_cochange_repo_root(repo) or os.getcwd())))
        except Exception:
            _gr = None
    _delguard_log_degraded(_gr, f"error:{e.__class__.__name__}", len(locals().get("tokens", [])))
```

The happy path guards against **standalone vault repos** (vault root == repo root, e.g.
`_vault_in()` at scripts/lumos:9304-9317, documented layout "d 本身就是 vault root(standalone,
如核心 repo)" — a real layout: `/Users/enzo/backend/citrus-core-knowledge` has `MOC/` +
`Verification/` directly at repo root, no `docs/` prefix) via the `gr_rel == "."` early return
right after `gr = find_vault(root)` (scripts/lumos ~11610-11615), before anything that could
raise. That guard is **not repeated** in the exception-branch re-derivation. `_append_governance_log`
(scripts/lumos:421-441) always computes the ledger path as `vault.parent / ".governance-log.jsonl"`
— for a standalone vault, `vault == repo root`, so `vault.parent` is **the repo's parent directory**,
outside git entirely.

Reproduction (built a synthetic standalone vault repo, ran the real `scripts/lumos`):

```
$ mkdir -p repo/{MOC,Verification,Systems,scripts}; cd repo; git init -q
$ cp .../scripts/lumos scripts/lumos
$ git commit --allow-empty -qm init
$ echo y >> Verification/a.md && git add -A
$ LUMOS_DELGUARD_RAISE=1 python3 scripts/lumos delguard --staged --repo "$PWD"
delguard: 內部錯誤(RuntimeError),放行(已記治理帳 delguard/degraded)
$ find .. -maxdepth 2 -name ".governance-log.jsonl"
../.governance-log.jsonl        # <-- outside the repo, in its PARENT dir
$ cat ../.governance-log.jsonl
{"ts": "...", "commit": "8c064a3", "gate": "delguard", "kind": "degraded", ...}
```

`LUMOS_DELGUARD_RAISE=1` is the test hook (scripts/lumos ~11607: `if os.environ.get("LUMOS_DELGUARD_RAISE"): raise RuntimeError(...)`), fired before `root`/`gr` are assigned, which is exactly the "早期 git 失敗" case the comment on line 11688 says this fallback exists for — so any real early failure (e.g. `_cochange_repo_root` raising) in a standalone-vault repo hits the same path. In a repo where the vault-owning repo also runs `scripts/lumos delguard --staged` from a pre-commit hook (the documented/supported standalone layout), this leaks a file onto the filesystem outside the git repo, outside version control, and outside the `docs/.gitignore` that's supposed to hide these ledgers.

Fix direction: reuse the same `gr_rel == "."` check (or equivalently reject `_gr == repo_root`) after re-deriving `_gr` in the exception branch, mirroring the main path's guard.

## Finding 2 — MAJOR: writing the ledger from pre-commit leaves a git-tracked file permanently dirty after commit

`_delguard_log_degraded` (scripts/lumos:11576-11584) is now called from the timeout and
exception branches, which fire on every `delguard --staged` invocation from
`scripts/hooks/pre-commit:57` on **every commit**. It appends to `docs/.governance-log.jsonl`
via `_append_governance_log`, whose write (scripts/lumos:437-441) is a raw file append, not a
`git add`.

In this repo, `docs/.governance-log.jsonl` is git-tracked (`git ls-files | grep governance-log`
→ `docs/.governance-log.jsonl`), a state the diff's own comment at scripts/lumos:8980-8985
acknowledges as a known, unfixed pre-existing bug ("本 repo 帳檔因此全被追蹤...既有 repo 已追蹤的
帳檔不受影響"). Because the append happens *after* the index is already fixed for the commit
(pre-commit hook, before the commit object exists) and is never staged, the new line is **not**
part of the commit, and the working tree is left dirty immediately after a clean commit.

This is not hypothetical — it already happened to the commit that lands this very diff. Right
now, before any action of mine, the repo shows:

```
$ git status --porcelain docs/.governance-log.jsonl
 M docs/.governance-log.jsonl
$ git diff docs/.governance-log.jsonl | tail -3
+{"ts": "2026-08-21T22:17:32+08:00", "commit": "2044557", "gate": "delguard", "kind": "degraded",
  "hard": false, "nodes": [], "note": "reason=timeout tokens=14"}
```
That line postdates commit `2859ed7`'s own `anchor-approve` ledger entry (22:17:26) and was
never folded into it — `2859ed7`'s pre-commit run degraded (timeout) and appended a line that
sits uncommitted right now.

Note the deadline was raised from 2.0→5.0 specifically because "2.0 在本 repo 幾乎必超(2026-08-21
一天降級 5+ 次)" — i.e. the PR's own diagnosis is that this fires several times a day in this repo
even after the fix. So this turns a previously occasional side effect (the *same* underlying
defect already existed via `doctor --ci`'s unconditional `doctor-run` append in `pre-push`,
scripts/lumos:1327-1334 — pre-existing, not introduced here) into a near-constant one on the much
hotter pre-commit path. Practical consequences: `git status` is non-clean after most commits going
forward; a later `git add -A`/`git commit -a` will silently fold stray delguard-degraded lines into
an unrelated commit (harmless content-wise since `.governance-log.jsonl` is on the
`_BOOKKEEPING_FILES` allowlist for code-loop invalidation purposes, but it does mean the "clean
tree after commit" assumption other tooling/humans rely on no longer holds).

This doesn't corrupt any single commit's content and doesn't trip the "只准簿記檔 commit" code-loop
invalidation check (that check diffs *committed* SHAs, and `docs/.governance-log.jsonl` is
whitelisted in `_BOOKKEEPING_FILES` at scripts/lumos:10316), so it's not a hard breakage — but it
is a real, now-confirmed-live regression in hygiene that this diff actively makes worse while
fixing something else.

## Non-findings (checked, hold up)

- **`subprocess` in scope at the except clauses**: `import json, os, subprocess, time` executes
  unconditionally at the top of `cmd_delguard_check` (before any try/except), so
  `except subprocess.TimeoutExpired:` is safe — not a lazy/conditional import.
- **Except-clause ordering**: `except subprocess.TimeoutExpired:` is listed before
  `except Exception as e:`, so it isn't shadowed by the broader handler.
- **`locals().get("tokens", [])`**: `tokens = []` is the first statement inside the outer `try`,
  before any operation that can raise, and is reassigned exactly once
  (`tokens = parsed["tokens"][:DELGUARD_TOKEN_CAP]`). No comprehension/closure shadows it. Always
  resolves to the intended list, never a stray variable.
- **`_append_governance_log` called from pre-commit context**: empirically verified `git`
  hooks run with `GIT_DIR` *unset* (only `GIT_INDEX_FILE=.git/index`, a relative path, is set) —
  confirmed via a live test hook. `git rev-parse --short HEAD` needs neither the index nor `GIT_DIR`
  to resolve `HEAD`, and `vault` is always an absolute path (`find_vault` calls `.resolve()`), so
  the commit-sha lookup itself resolves correctly regardless of hook cwd quirks.
- **`gov --stats` drift test (`t_gov_stats_gate_drift`)**: still holds — ran it directly; the new
  literal `"gate": "delguard"` is captured by the literal-scan regex and is present in the updated
  `_KNOWN_GATES` tuple, and the dynamic-gate-site count stays at 1 (the pre-existing read-side
  passthrough). `python3 scripts/test_lumos.py -k gov_stats` → 28 passed.
- **`--json` degraded contract**: unchanged — `{"tokens", "hits": [], "fake_sync": [], "degraded", "reason"}`
  shape is identical on both the timeout and error paths; verified via the passing
  `delguard 超時降級 --json 形狀完整` / `delguard 內部錯誤 --json 形狀完整` tests.
- **All 88 `-k delguard` tests pass**, including the new `體檢 #9` tests for governance-log writes
  on timeout/error.

## Minor observations (not scored as blocker/major)

- `_append_governance_log`'s `subprocess.run(["git", "rev-parse", "--short", "HEAD"], ...)`
  (scripts/lumos:430) has no `timeout=`, unlike every other git subprocess call in the delguard
  path. It's now reachable from delguard's fail-open/degraded branches, whose whole point is
  bounded latency. Low practical risk (`rev-parse HEAD` doesn't need the index/lock and is
  normally instant) but it's an unbounded call inside an otherwise deadline-disciplined path; no
  forcing repro available so not scored.
- The invalid-env fallback `except (ValueError, TypeError): deadline = 2.0` (scripts/lumos:11598-11599)
  was left at the old value while the primary default moved to 5.0 specifically because 2.0
  "幾乎必超" in this repo. A non-numeric `LUMOS_DELGUARD_DEADLINE` reverts to the deadline the PR
  itself says almost always times out. No test pins this fallback at 5.0.

## Severity count: 2 major, 0 blocker
