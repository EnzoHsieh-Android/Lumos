# E — Ledgers and Automation Audit

Read-only audit. All counts machine-computed against the live repo state on 2026-08-21.

## 0. Ledger files: existence, size, writer, reader

| file | exists | lines | last write | writer | reader |
|---|---|---|---|---|---|
| `docs/.governance-log.jsonl` | yes | 20,566 | 2026-08-21 20:51 (today) | `_append_governance_log` (`scripts/lumos:437`) called from `doctor --ci` (7 `check-*` gates) + `code-loop` pass/skip (`:14038`) + `anchor approve` (`:10131`) | `lumos gov` (7-source aggregator, `:2965`) — human-invoked only |
| `docs/.canary-log.jsonl` | yes | 487 | 2026-08-21 20:29 (today) | `lumos canary record` (`:3212`) | `lumos gov` (source 4), `lumos loop status` (design/code-loop convergence check) |
| `docs/.bypass-log.jsonl` | yes | 61 | 2026-08-04 18:53 (17d stale) | post-commit hook, L2 bypass detection (`scripts/hooks/post-commit:79`) | `lumos gov` (mapped to gate=`L2`, `:2994`) — **the dedicated tool that's supposed to read it, `scripts/rot-queue-digest.sh`, does not exist anywhere in the repo** (see §3) |
| `docs/.usage-log.jsonl` | yes | 166 | 2026-08-21 12:43 (today) | `lumos context` / `lumos show` (`:6058`) | **none** — confirmed by grep: it never appears in `cmd_gov`'s 7-source load list, and no other script reads it. Pure write-only telemetry. |
| `docs/.signoff-log.jsonl` | yes | 8 | 2026-08-08 22:40 (13d) | `lumos signoff` (`:14403`, human-invoked) | `lumos gov` (source 6) |
| `docs/.ci-log.jsonl` | yes | 25 | 2026-08-21 21:02 (today) | `lumos ci-wait` (post-push CI polling, `:12490`) | `scripts/hooks/claude/ci-status-hook.py` (SessionStart hook, real safety net — injects "last push was red" into context) + `lumos gov` (conditional 7th source) |
| `docs/.rot-queue.jsonl` | **no — does not exist** | 0 | n/a | `scripts/hooks/claude/verification-rot-check.py` (PostToolUse hook) appends only when it detects a code change invalidating a Verification note | `check-graph-sync.py` (Stop hook, patrols and warns at ≥3 entries) + `scripts/rot-queue-digest.sh` (**referenced 4x in code, 3x in docs, does not exist** — see §3) + `lumos gov` (source 2, conditional on file existing) |
| `docs/.kill-log.jsonl` (bonus, named in `lumos gov`'s "7 ledgers" but not in the assignment) | **no — does not exist** | 0 | n/a | `lumos guard kill` (never invoked in this repo's history — 0 kill verdicts ever recorded) | `lumos gov` (source 5) |

## 1. `governance/` directory

| item | alive? | evidence |
|---|---|---|
| `governance/autonomous-loop.sh` (276 lines) | **alive but non-productive for 38 days** | Runs daily via `daily-governance.sh --dry-run 6`. Log shows rc=0 every day 2026-07-15→08-21, but every single day logs "無可展開 gap(N=1 gate 或 backlog 空),結束". Root cause (§4): `gap_select.pending_exists()` in dryrun mode returns True if **any** `.md` file sits in `governance/pending/` — and two files from 2026-07-14 have never been cleared, so the selector permanently short-circuits to "nothing to do." |
| `governance/daily-governance.sh` (33 lines) | alive | launchd-triggered wrapper, runs 3 sub-steps daily, rc=0 every day through 2026-08-21 per `governance/logs/daily-wrapper.log` |
| `governance/autonomous_loop/` (gap_select.py, backlog.py, etc.) | alive | actively imported by autonomous-loop.sh; `backlog.jsonl` is being appended to as recently as today |
| `governance/backlog.jsonl` (152 lines, 90KB) | alive, growing | 3 new entries dated 2026-08-20/21; **but nothing is ever popped off it** because `select()` never gets past the `pending_exists()` gate (see above) — it accumulates without ever draining |
| `governance/covered.jsonl` (9 lines) | **stale, 45 days (last 2026-07-07)** | Only written by `mark_covered()`, which only fires when a gap `requeue_unconverged`s 3x or an orchestrator explicitly judges a gap already covered. Given the selector has been dead since 07-15, this path can't fire either. |
| `governance/pending/` (2 files, both 2026-07-14) | **stale, 38 days** | These 2 files are the actual root cause: they block every subsequent selection cycle. Nobody has reviewed/moved/deleted them. |
| `governance/reports/` (69 files) | alive | `governance-YYYY-MM-DD.json` + `governance-history.md` written daily by `ai-governance-research.sh`, current through 2026-08-21 |
| `governance/golden/` (32 dirs) | alive | design-loop transcripts/snapshots, actively written (latest 2026-08-20/21, includes the in-flight "閘觸發帳統計" design covered in §5) |
| `governance/review-reports/` (30 dirs) | alive | code-loop / design-loop audit transcripts, latest 2026-08-21 20:05 |
| `governance/eval/` (29 items) | alive-ish | latest mtime 2026-08-18, retrieval/multiword eval harness |
| `governance/rel-cascade/` (2 files) | **thin** | only 2 event files (2026-08-04, 2026-08-11) — low but real volume, not obviously dead |
| `governance/code-loop/` (6 json files) | alive | `main.json` updated today 12:20 (a real code-loop skip event, matches commit e119ce0 in git log) |

## 2. launchd job

`~/Library/LaunchAgents/com.enzo.lumos.daily-governance.plist` — **loaded** (`launchctl list` shows `com.enzo.lumos.daily-governance` with last exit status 0). Fires 09:30 daily, paired with `pmset repeat wakeorpoweron` to force-wake a normally-clamshelled Mac. `governance/logs/daily-wrapper.log` confirms clean rc=0 runs every day through 2026-08-21 — **this is genuinely alive and not silently broken at the process level.** The silent failure is one layer down: the process succeeds every day while doing nothing useful (§1).

## 3. Dead reference: `scripts/rot-queue-digest.sh`

This script does not exist and has **no git history at all** in this repo (`git log --all -- "*rot-queue-digest*"` returns nothing), yet it is the documented/promised reader for two ledgers:

- `scripts/hooks/claude/verification-rot-check.py:401` — tells the user to run it after every rot-queue write
- `scripts/hooks/claude/check-graph-sync.py:341` — Stop hook tells the user to run it when rot-queue hits ≥3 entries
- `scripts/hooks/post-commit:12,106` — tells the user it shows weekly bypass rate
- `docs/methodology/圖譜即合約.md:243,282,373` — documents it as the weekly review tool for both L2 (bypass) and L3 (rot) ledgers

**Verdict: vaporware.** The only actual reader that exists is `lumos gov`, a generic 7-source aggregator with no bypass-rate computation, no weekly cadence, and no dedicated rot-queue triage UI. Both `.bypass-log.jsonl` and `.rot-queue.jsonl` are read only in the weak sense that a human can manually run `lumos gov` and see raw rows mixed in with everything else — the specific promised tool was never built.

## 4. `scripts/external-seat.sh` (Gemini external-panel caller)

40 lines, modified today (2026-08-21 12:20, same timestamp as `governance/code-loop/main.json`'s skip event — i.e. it was actually invoked today). Stateless single-shot `curl` wrapper, no ledger of its own by design ("恆單發無狀態,不落任何帳——記帳歸 loop 紀律", line 7). Not called from any script — it's invoked ad hoc by Claude/human following the design-loop/code-loop skill's prose instructions when an external panel seat is needed. Confirmed live and matches memory note "外家現役=Gemini API".

## 5. design-loop / code-loop record/status machinery

- **`lumos code-loop check`** (tier=high gate) — **hard enforcement**, confirmed at `scripts/hooks/pre-push:99-118`: on push, if `pitfalls --diff` hits `tier: high`, the hook calls `lumos code-loop check` and **blocks the push (exit non-zero)** unless converged or explicitly `lumos code-loop skip --note "..."`. This is a real, mechanically-enforced gate, not honor-system. Evidence it fires: `governance/code-loop/main.json` shows a skip event from today; `docs/.governance-log.jsonl` has 79 `code-loop` events.
- **`lumos loop status --disposal`** (design-loop convergence gate) — **soft / honor-system**. Grepped every hook (`pre-commit`, `pre-push`, `post-commit`) — `--disposal` is referenced only inside `scripts/lumos` itself and in skill prose (`lumos-design-loop`). Nothing mechanically blocks proceeding to implementation if a human/Claude skips this check. Contrast with code-loop above: code-loop's tier=high path is hard-blocked at push time; design-loop's disposal gate is not blocked anywhere — it relies entirely on the agent following the skill.
- **canary `record none`** — confirmed real and matches memory: the planted-error auditor-reliability protocol was disabled 2026-08-14. Machine count of `docs/.canary-log.jsonl` by `kind`, split at that date:
  - before 2026-08-14: `caught`=337, `missed`=67 (0 `none`)
  - after 2026-08-14: `none`=83 (0 `caught`/`missed`)
  This is a clean, complete protocol cutover — `.canary-log.jsonl` is now purely a disposition-ledger carrier for design/code-loop rounds, not an auditor-catch-rate instrument. `lumos gov` and `lumos loop status` still read it as documented.

## 6. Gate-firing counts (from `docs/.governance-log.jsonl`, all-time, raw lines)

This exact question — "which gates actually fire" — is the subject of an **in-progress design-loop already in this repo** (`governance/golden/閘觸發帳統計/r1..r3-snapshot.md`, converged 2026-08-20/21, and already shipped as `lumos gov --stats`, commit 7bd9ab2). Its machine-verified numbers corroborate this audit's independent count:

| gate | raw lines | fires? |
|---|---|---|
| `check-s` | 18,583 | yes — 90.4% of the entire ledger, and per the shipped design doc, 46+ days of zero-convergence spam on ~30 nodes before a batch fix |
| `check-e1` | 1,752 | yes, but is a strict subset of check-s's commit set (same 420 commits) |
| `anchor-approve` | 148 | yes — human-approval audit trail, working as intended |
| `code-loop` | 79 | yes |
| `doctor-run` | 4 | yes (new, low-volume bookkeeping event) |
| `check-r`, `check-j`, `check-k`, `check-e2`, `check-e3` | **0** | **never fired, ever** — confirmed both by this audit and by the shipped `--stats` design doc, which further found `check-j`'s entire branch is dead code: it's gated behind `if _regen_rels:` and zero nodes in the whole vault carry a `regen:` field, so the branch has literally never executed. |

The already-converged design doc explicitly flags the ceiling of this measurement: **hard gates (e.g. `anchor verify`, pre-push test gate) never write to this ledger at all** — a blocked push produces zero rows, so absence-from-ledger cannot be read as "gate is useless," only as "gate doesn't write here."

## Deficiencies (most important, blunt)

1. **The daily autonomous-loop has been a no-op for 38 straight days while reporting success.** `governance/autonomous-loop.sh` via launchd runs every day, exits 0, and does nothing, because `gap_select.pending_exists()` treats the mere presence of 2 stale `.md` files in `governance/pending/` (dated 2026-07-14, never reviewed) as "there's already pending work" and refuses to select anything new — permanently. `governance/backlog.jsonl` keeps growing (152 lines, 3 new entries in the last 2 days) with nothing ever being drained. This is exactly the failure mode the audit brief warns about: scheduled automation that is silently failing while reporting green. Fix: either clear/triage `governance/pending/*.md` or fix `pending_exists()` to not permanently wedge on stale files.

2. **`scripts/rot-queue-digest.sh` is documented in 7 places across hooks and methodology docs and has never existed.** Two hooks (`verification-rot-check.py:401`, `check-graph-sync.py:341`) tell the user to run it; it doesn't exist and never has (no git history). The bypass-rate reporting it's supposed to provide (`docs/methodology/圖譜即合約.md:243`) doesn't exist anywhere else either. This is textbook 虛設: a reminder that prints into a stream, pointing at a tool that was never built.

3. **`docs/.usage-log.jsonl` is a confirmed write-only ledger.** Written by `context`/`show` commands (166 lines, actively growing, last write today), read by nothing — not `lumos gov`'s 7-source list, not any hook, not any script in the repo. This was already independently confirmed inside the repo's own r1 audit of the `lumos gov --stats` design ("usage 帳檔… `gov` 根本沒讀它").

4. **Two of the seven "ledgers" named in the audit brief don't exist on disk** (`.rot-queue.jsonl`, and `.kill-log.jsonl` which is adjacent/related): rot-queue because no rot has been detected/queued recently (plausible — or the detector hook is quietly not firing, can't distinguish from ledger evidence alone), kill-log because `lumos guard kill` has never been invoked in this repo's history. Both are legitimate "zero ≠ broken" cases per the repo's own already-shipped `--stats` design doc caveat, but worth flagging that the audit brief's file list assumes files that are currently absent.

5. **Design-loop's `--disposal` convergence gate is honor-system; code-loop's `tier=high` gate is hard-enforced.** This asymmetry is real and undocumented as a contrast: a design can proceed to implementation without ever running `lumos loop status --disposal` — nothing blocks it. Only once code is written and diffed does the pre-push hook mechanically force a `code-loop check`. If the intent is "design gets audited before implementation," that intent currently has zero mechanical teeth.
