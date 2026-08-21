# Audit A — git hooks + Claude Code hooks

Scope: `scripts/hooks/{pre-commit,pre-push,post-commit}`, `scripts/hooks/claude/*.py`,
installed copies in `~/.claude/hooks/`, registration in `~/.claude/settings.json`.
Method: read all hook source, cross-checked against `docs/.governance-log.jsonl` (20,566
lines), `docs/.bypass-log.jsonl` (61 lines), `docs/.ci-log.jsonl` (25 lines),
`docs/.usage-log.jsonl` (166 lines), `.github/workflows/ci.yml`, `git log`, and live
timing runs (`time python3 scripts/lumos ...`) against the real repo state (read-only,
no writes performed).

## Table

| mechanism | purpose | enforcement | fires? | reaches Claude? | verdict | proposed fix |
|---|---|---|---|---|---|---|
| **pre-commit Gate 1** (圖譜污染指紋) | catch notesmd-cli `frontmatter --edit` silently quoting date fields, corrupting Obsidian property types | hard (exit 1) | no direct ledger; design documented 2026-06-13 P0 audit finding | yes — git hook stderr lands in Bash tool result | 保留 | none — cheap, targeted, has a named incident |
| **pre-commit Gate CC** (cochange 警告) | warn when a code file's usual co-change partner wasn't staged | soft (`\|\| true`, advisory) | `cochange` referenced 343× in governance-log (mostly via code-loop review text, not itself a firing ledger); no dedicated fire-counter | yes, stdout/stderr | 精簡 | add one-line counter event to governance-log so "does it actually fire on real staged commits" is answerable without inference |
| **pre-commit Gate DG** (delguard) | code-side deletion propagation guard | soft (`\|\| true`) | same as above — 151 mentions, mostly narrative (code-loop review text about the delguard *feature*, not per-commit fire events); `t_delguard` has 111 assertions at unit level | yes, stdout/stderr | 保留 | same — add fire-counter to distinguish "ran and found nothing" from "never ran" |
| **pre-commit Gate 2/3** (圖譜同步硬擋 — code without graph .md) | core L2 gate: code changed, no `docs/*-knowledge/*.md` staged → block | hard (exit 1) | 61 bypass-log entries total, most recent 2026-08-04; **0 entries since**, but 228 commits since 2026-08-04 and 18 commits today (2026-08-21) all correctly paired code+graph — real gate discipline, not silence from being dead | yes, stderr in Bash tool result | 保留 | fix CODE_EXTS gap below (this is the real defect, not the gate concept) |
| **post-commit bypass logger** (→ `.bypass-log.jsonl`) | detect `--no-verify` bypasses of the pre-commit graph-sync gate by re-running the same code/graph inference on the landed commit (post-commit is never skipped by `--no-verify`) | soft, log-only, `trap 'exit 0' ERR` | confirmed correct design — `--no-verify` skips pre-commit+commit-msg but **not** post-commit, so this is a real, working backstop; 61 real entries over ~3 months | log only, not surfaced to Claude in-session (Claude only sees it if it greps the file or runs `rot-queue-digest.sh`) | 保留 | nothing structurally wrong; the one gap is it only detects *this specific* bypass shape, see deficiencies |
| **pre-push: anchor verify** | verifier files (hooks/runner) unmodified vs baseline, so "tests pass / doctor clean" claims are trustworthy | hard (exit 1) | 148 `anchor-approve` events in governance-log — actively used | yes, stderr | 保留 | none |
| **pre-push: test_lumos.py full suite** | catch red tests before they reach main (2026-07-07 incident: red tests slipped into main twice) | hard (exit 1), source-repo only (`skills/lumos-project-notes` dir gate) | timing measured indirectly via script comment "~32s"; CI also runs full suite (`.github/workflows/ci.yml:23`) as backstop | yes, stderr + tail of log file | 保留 | none — has a named incident and a CI backstop |
| **pre-push: pitfalls --diff tier=high + code-loop check** | force adversarial code review before push when diff hits high-risk code patterns | hard for `refs/heads/*` (exit 1), advisory for tags/other refs | 79 code-loop events in governance-log: 56 passed / 23 skipped — actively exercised, not vacuous | yes, stderr (full pitfalls dump) | 保留 but 修 the bypass hole | **`git push --no-verify` skips this gate with zero trace anywhere** — no bypass-log equivalent, and `.github/workflows/ci.yml` does NOT re-run `pitfalls`/`code-loop` (only test suite + doctor + anchor verify). See deficiency #1. |
| **pre-push: doctor --ci** | catch broken graph state (dangling links, missing verified_by/plan_refs) before push | hard (exit 1) | governance-log `doctor-run` events = 4, but that ledger event was only added **today** (commit `9a95bc4`, 2026-08-21) — the gate itself has been running via CI since the repo existed, just wasn't logged locally until today | yes, stderr; live timing: **0.86s** | 保留 | none, now that it logs |
| **impact-hook.py** (PreToolUse Edit/Write/MultiEdit) | inject "must-check contracts/incidents + related nodes + stack-perf questions" before Claude edits code | soft, advisory only, PreToolUse `additionalContext` | no dedicated ledger; TTL cache dir (`$TMPDIR/lumos-impact-<session>`) not found on disk at audit time (expected — TTL-scoped, not persistent); 38 test functions cover the underlying logic; live timing of `lumos impact --file ... --json`: **0.95s** | yes — uses the official `hookSpecificOutput.additionalContext` PreToolUse channel, confirmed in source (line 377-405) | 保留 | add a one-line append-only firing counter (even just `{ts, file}` to a local log) so "does it actually inject" is falsifiable instead of asserted |
| **verification-rot-check.py** (PostToolUse, matcher=Bash) | after `git commit`, ask Sonnet (`claude -p`) whether the diff invalidates an existing Verification note | soft, never blocks | **strong 虛設 signal**: its own cache file `docs/.rot-check-cache.json` (gitignored, would persist across all runs) does not exist on disk; its output ledger `docs/.rot-queue.jsonl` also does not exist. Given hundreds of `git commit` calls have happened through Claude Code Bash tool in this repo's history, and cache is written on *every* LLM invocation regardless of verdict, absence of both files means the LLM body has essentially **never executed** — either `GIT_COMMIT_RE`/`CLAUDE_PROJECT_DIR` never resolves in this environment, or `find_candidate_verifications` never returns candidates, or `claude -p` subprocess never succeeds (nested Claude-Code-inside-Claude-Code auth is a plausible failure mode) | would be additionalContext via stderr print — but only if it ever fires | 砍 or 修 | either instrument it to prove it runs (log every invocation attempt + exit reason to a ledger, not just successful findings) or remove it — right now it costs a subprocess + up to 5 parallel `claude -p` calls (25s timeout each) on **every single Bash tool call matching the commit regex**, for a payoff with zero observed output in the available history |
| **ci-status-hook.py** (SessionStart) | CI red-light backstop when the "push → same-turn ci-wait" main path got interrupted | soft, advisory, fail-open everywhere | `.lumos/config.json` has `ci` block declared (gate is live, not silently off); `.ci-log.jsonl` has 25 entries, latest = 2026-08-21 21:02 success for sha `9a95bc4` | yes, SessionStart `additionalContext` | 保留 | none — small, well-scoped, fails open by design |
| **check-graph-sync.py** (Stop hook) | end-of-turn reminder: this turn edited code files but didn't touch the graph | soft, stderr print, never blocks turn | inference-only (reads transcript for file edits + bash commands each Stop); no persistent fire-ledger of its own beyond the `.rot-queue.jsonl` patrol sub-feature (`emit_queue_patrol`, threshold ≥3 findings) — and since `.rot-queue.jsonl` doesn't exist, that sub-feature has also never fired | yes, printed to stderr at Stop — Claude Code surfaces Stop-hook stderr back into context per documented behavior | 保留 | same CODE_EXTS gap as pre-commit (see deficiency #2) |
| **Double registration in `~/.claude/settings.json`** (verification-rot-check.py under PostToolUse, check-graph-sync.py under Stop) | n/a — appears to be an installation/merge artifact, not intentional | n/a | **structurally confirmed**: `hooks.PostToolUse` has two separate array entries each running `verification-rot-check.py` (once via full `/opt/homebrew/bin/python3` path, once via bare shebang path); `hooks.Stop` has the identical duplicate pattern for `check-graph-sync.py`. Neither script has any invocation-dedup guard (checked both files for lock/seen/already-ran logic — none exists at the process level). Claude Code does not documented-dedupe identical hook entries across separate array blocks, so this reads as real double-execution, not just a display artifact | n/a | 修 | delete one of each duplicate pair in `~/.claude/settings.json`; for verification-rot-check.py this doubles subprocess+LLM cost on every matching Bash call, for check-graph-sync.py it doubles the Stop-hook reminder text shown to Claude every turn |

## The "code file" definition gap (specifically requested)

`pre-commit` (bash, line 85), `post-commit` (bash, line 46), `check-graph-sync.py`
(`CODE_EXTS`, line 24), and `impact-hook.py` (`CODE_EXTS`, line 27) **all four**
independently define "code file" as the same fixed extension set:

```
.cs .vue .js .ts .tsx .jsx .mjs .sql .py .kt .kts .java .swift .go .rs .c .cc .cpp .h .hpp
```

**`.sh` is not in the set, in any of the four copies.** Neither is `.json`, `.yaml`/`.yml`,
`.rb`, `.php`, or `.cjs`. This is consequential because the toolchain's own governance
surface is partly shell: `scripts/external-seat.sh`, `scripts/graph-rename.sh`,
`governance/*.sh` (4 files), plus the hook files themselves (`pre-commit`, `pre-push`,
`post-commit` are themselves `.sh`-shaped and would be exempt from their own gate).

**Live confirmation, not hypothetical**: commit `d13df3b` today (2026-08-21,
`fix(external-seat): 開檔改 with(pitfalls 資源類命中,非假陽性)`) changed
`scripts/external-seat.sh` and only paired it with `docs/.governance-log.jsonl` (not a
`docs/*-knowledge/*.md` node) — this is a real behavioral fix to governance-relevant
code that sailed through the graph-sync gate untouched and un-bypass-logged, because
`.sh` was never in scope for the check in the first place. It is not a caught bypass;
it's invisible to the gate by definition.

There is **zero test coverage** for `CODE_EXTS` consistency: `grep -n "CODE_EXTS"
scripts/test_lumos.py` returns nothing. The four copies can drift from each other
silently (bash regex vs. three separate Python sets) and nothing would catch it.

## Bypass counts today (2026-08-21) and this cycle

- `git log --since 2026-08-21`: 18 commits, all on `main`, all pairing code changes
  with a `docs/*-knowledge/*.md` node **except** `d13df3b` (the `.sh` gap above, which
  the gate never saw as a violation) and `eb3c083` (touches `scripts/test_lumos.py`
  but correctly paired with a Verification node — not a bypass).
- `docs/.bypass-log.jsonl`: 0 entries dated 2026-08-21, 61 total, last real entry
  2026-08-04. Read together with the commit sample above, this says the *logged* gate
  (code-ext-recognized files) is holding, not that nothing is slipping through — the
  `.sh` gap slips through silently, uncounted, by design of the extension list rather
  than by anyone using `--no-verify`.
- 19 commits in `git log --all --grep="no-verify"` (commit messages that *mention*
  no-verify, e.g. discussing the policy) — not the same as commits made *with*
  `--no-verify`; this repo has no ledger of raw `--no-verify` invocation counts, only
  the inferred post-commit detector described above.

## Deficiencies, ranked

1. **`git push --no-verify` silently skips the tier=high code-loop gate with zero trace anywhere.**
   Unlike the commit-level gate (which has a post-commit inference backstop because
   post-commit always runs), there is no git-side hook that always runs after push, and
   `.github/workflows/ci.yml` only re-runs the test suite + `doctor --ci` + `anchor
   verify` — **not** `pitfalls --diff` / `code-loop check`. A developer (or an agent)
   who hits a tier=high finding at push time and types `git push --no-verify` leaves no
   record distinguishable from a clean push, and CI won't catch it either.
   Evidence: `scripts/hooks/pre-push:73-137` (only local enforcement point) vs.
   `.github/workflows/ci.yml:1-29` (no `pitfalls`/`code-loop` step).
   Fix: add a lightweight CI step that runs `lumos pitfalls --diff <merge-base>..HEAD
   --json` on push and fails/warns if tier=high with no matching `code-loop`
   passed/skipped ledger entry at that sha.

2. **`CODE_EXTS` excludes `.sh` (and `.json`/`.yaml`) across all four independent
   copies, with zero drift-guard test, and this is not hypothetical — it happened today**
   (`d13df3b`, see above). Given three of this repo's own git hooks are themselves
   `.sh` files, and `governance/*.sh` carries real logic, this is a structural blind
   spot in a self-referential system. Fix: add `.sh` to all four `CODE_EXTS`
   definitions (or better, factor them into one shared source both bash and Python read,
   plus a `t_code_exts_consistency` test asserting the four sets are identical).

3. **`verification-rot-check.py` shows no evidence of ever executing its core logic** in
   the available lifetime of the repo — its own gitignored cache file
   (`docs/.rot-check-cache.json`) and output queue (`docs/.rot-queue.jsonl`) both don't
   exist, despite being written on every LLM invocation regardless of verdict. It is
   registered on **every** Bash tool call (filtered internally to `git commit`), doubled
   by the settings.json duplication (deficiency #4), each doubled invocation capable of
   spawning up to 5 parallel `claude -p` subprocesses with 25s timeouts. This is the
   strongest 虛設 candidate in the whole area — a mechanism with real cost and a paper
   citation backing its design, but no observable trace of ever paying off. Fix: log
   every invocation attempt (even "skipped: diff too small" / "skipped: no candidates")
   to a small ledger, then re-audit in 2 weeks with real firing data before deciding
   keep/cut.

4. **Duplicate hook registration in `~/.claude/settings.json`** for
   `verification-rot-check.py` (PostToolUse) and `check-graph-sync.py` (Stop) — each
   appears twice as separate array blocks (once invoked via absolute
   `/opt/homebrew/bin/python3` path, once via bare shebang path), with no
   invocation-dedup guard in either script. This is pure waste at minimum (2x subprocess
   overhead every Bash call / every Stop) and, if `verification-rot-check.py` ever does
   fire, doubles LLM API cost per commit. Fix: delete one entry from each pair.

5. **Gate CC (cochange) and Gate DG (delguard) in pre-commit have no dedicated firing
   ledger** — their apparent frequency in `governance-log.jsonl` (343 / 151 mentions) is
   almost entirely narrative text from *code-loop review reports about the features*,
   not per-commit fire events. Unlike the graph-sync gate (which has the post-commit
   bypass-log as an independent firing signal), there's no way to answer "how many real
   staged commits actually triggered a cochange/delguard warning" without adding
   instrumentation. Both are advisory (`|| true`) so the cost of being wrong here is
   low, but the audit question "does it actually fire" is currently unanswerable from
   ledger data alone.

## Not deficiencies (confirmed working, evidence-backed)

- pre-commit Gate 2/3 (graph-sync core gate): 61 real bypass-log entries over 3 months,
  0 in the last 17 days despite 228 commits — genuinely enforced, not silent.
- post-commit bypass detector: correctly exploits the fact `--no-verify` doesn't skip
  post-commit; this is good design, confirmed by reading git hook semantics + the code.
- pre-push anchor verify / test suite / doctor --ci: all have real ledger evidence
  (148 / CI logs / 4 fresh doctor-run entries) and CI backstops for at least two of the
  three.
- code-loop tier=high gate itself (not counting the `--no-verify` hole): 79 real events,
  56 passed / 23 skipped — actively used, not decorative.
- impact-hook.py: correctly uses the official PreToolUse `additionalContext` channel,
  0.95s overhead per Edit/Write, 38 tests on underlying logic.
