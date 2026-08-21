# F-tokens: token/compute cost audit of lumos-toolchain

Methodology: char counts are real (`wc -c` / direct measurement or live command runs on 2026-08-21). Token estimates use the brief's own conversion (~1.6 chars/token Chinese, ~4 chars/token code); most files here are mixed CJK-prose + code, so a blended ~2.2-2.8 chars/token is used unless noted. All commands were run read-only against the live repo; `lumos loop next` appended to `docs/.governance-log.jsonl`/`.usage-log.jsonl` as a side effect of normal usage tracking (noted, not undone — consistent with how the tool is meant to be run).

---

## 1. Per-session fixed load

| Artifact | Chars | Lines | Loads |
|---|---|---|---|
| `CLAUDE.md` | 6,797 | 47 | **every session** (system prompt injection) |
| `scripts/templates/graph-discipline.md` | 6,565 | 44 | not loaded directly — its content is **embedded verbatim inside CLAUDE.md** (confirmed: same "圖譜先行" opening paragraphs, doctor Check [D] literally diffs CLAUDE.md's discipline block against this template to catch drift). So this isn't a second load — CLAUDE.md *is* ~97% this file. |
| `skills/lumos-pitfalls-gapfill/SKILL.md` | 5,098 | 47 | on demand (Skill tool call) |
| `skills/lumos-core-knowledge/SKILL.md` | 7,578 | 107 | on demand |
| `skills/csharp-idioms/SKILL.md` | 8,881 | 127 | on demand |
| `skills/vue-idioms/SKILL.md` | 7,705 | 128 | on demand |
| `skills/kotlin-idioms/SKILL.md` | 10,614 | 157 | on demand |
| `skills/lumos-code-loop/SKILL.md` | 27,559 | 229 | on demand |
| `skills/lumos-design-loop/SKILL.md` | 30,240 | 233 | on demand |
| `skills/lumos-project-notes/SKILL.md` | 20,591 | 256 | on demand |
| `skills/lumos-project-notes/reference.md` | 87,860 | 922 | **only** on explicit `Read` when SKILL.md's own "何時去翻 reference.md" table says to |
| `skills/lumos-design-loop/reference.md` | 13,003 | 202 | same, on-demand |
| `skills/lumos-design-loop/templates.md` | 15,782 | 212 | same, on-demand |
| `skills/lumos-code-loop/reference.md` | 21,741 | 257 | same, on-demand |

**Finding**: the reference/templates split is already implemented correctly — each SKILL.md's head explicitly says "本頭版摘要;細節在 reference.md,撞到情境才 Read" with a lookup table. That part of the "split into operative card + on-demand reference" optimization is **already done**. What's *not* done: the "operative card" itself (SKILL.md) is 20–30K chars for the three lumos-* skills — 3–5x the ≤2K-char target the brief describes. Every `Skill` tool invocation of `lumos-design-loop` costs ~30,240 chars ≈ **11–14K tokens** just for the card, before any reference.md is opened.

Fixed cost that hits **every session regardless of task**: CLAUDE.md, ~6.8K chars ≈ **2,600–4,300 tokens**. This is small in absolute terms (context windows are 200K+) but it's mostly a strict rule-manifest — dense, not skippable, and stacks with SessionStart hook injection.

---

## 2. Per-tool-call overhead (Claude hooks)

`~/.claude/settings.json` hook registration (confirmed by direct read):

| Event | Matcher | Hook | Timeout | Registered |
|---|---|---|---|---|
| PostToolUse | Bash | `verification-rot-check.py` | 60s | **2x** (identical command, once via explicit `/opt/homebrew/bin/python3 "…"`, once via bare `${HOME}/.claude/hooks/….py`) |
| Stop | (none) | `check-graph-sync.py` | 10s | **2x** (same duplication pattern) |
| PreToolUse | Edit\|Write\|MultiEdit | `impact-hook.py` | 30s | 1x |
| SessionStart | (none) | `ci-status-hook.py` | 15s | 1x |

**This is a real bug, not a design choice** — both registrations are byte-identical except for how python3 is invoked. Every `Bash` tool call runs `verification-rot-check.py` twice; every `Stop` runs `check-graph-sync.py` twice. Confirmed via `python3 -m json.tool` dump of the actual settings.json hooks block.

### impact-hook.py (PreToolUse, Edit/Write/MultiEdit)
- Filters to code extensions (18 exts), excludes `/docs/`, `/node_modules/`, `/dist/`, etc.
- TTL cooldown: 20 min default per (session, file) — repeat edits to the same file within 20 min are compressed to `--incidents-only` (cheap path).
- Outside cooldown: shells out to `lumos impact --ranked --stdin-payload --json` (subprocess, 30s timeout), then formats the ranked result as `additionalContext`.
- **Live measurement** (dry run against `scripts/lumos` itself, the toolchain's own hub file): `lumos impact` returned 41 ranked results out of 312 candidates, of which **33 were unconditionally pinned** (contract/incident tag = auto-pin, no cap) plus a top-8 ranked list. Formatted injection = **2,007 chars ≈ 700–900 tokens**, for a *single* Edit call on a hub file. Because `scripts/lumos` (the CLI itself) touches 33 contract/incident nodes, editing it repeatedly triggers this every 20 minutes for the whole session — on a long lumos-development session this is easily 5,000–10,000 tokens/session from this one hook, on a file with no cap on the "必看" pinned set.
- **Finding**: "top-8" is only true for the *ranked/free* tier; the *pinned* tier (contracts+incidents) has **no size limit** at all. For high-fan-in files (scripts/lumos, CLAUDE.md, hooks) this defeats the whole point of ranking/truncation.

### verification-rot-check.py (PostToolUse, Bash — runs on **every** Bash call)
- Cheap path (not a `git commit`): regex match on the command string, return 0. Near-zero cost, but doubled by the registration bug above → 2x process spawns per Bash call all session long.
- Expensive path (command matches `git commit`, diff is 10–2000 lines): searches for up to 5 candidate Verification notes via `obsidian search`, then for **each candidate spawns a real `claude -p --model sonnet --output-format json` subprocess** (25s timeout, up to 5 parallel) to judge whether the commit invalidates that Verification's conclusion. This is genuine **extra LLM spend outside the parent conversation** — up to 5 Sonnet calls per commit, each with ≤4,000 chars diff + ≤1,500 chars verification text in the prompt (~1,500–2,000 tokens in, small JSON out). A repo with disciplined small commits (this one: pre-commit gate enforces graph updates) will trigger this reasonably often.
- Has an LRU result cache (500 entries) keyed on (commit, verification, content-hash) to avoid re-paying for identical diffs — good mitigation already in place.
- Because of the double-registration, **every qualifying commit likely pays for this twice** — up to 10 Sonnet calls instead of 5.

### check-graph-sync.py (Stop, every turn end) — also double-registered, 10s timeout each, so every Stop event pays 2x whatever this checks (reminder-only, doesn't call an LLM per the code header, so cost here is mostly wasted wall-clock/process-spawn, not tokens).

---

## 3. Per-command output volume (live runs, 2026-08-21)

| Command | Lines | Chars | Notes |
|---|---|---|---|
| `scripts/lumos doctor` | 105 | 7,243 | **All 18 checks print inline, no hide flag.** Hard checks (orphans, wikilinks, contract binding) mixed with explicitly-labeled "軟提醒、不擋 CI" checks ([V] valid_under, [P] dead-file refs, [N] recomputable-number drift) — no way to see only the checks that gate CI without reading all of them. Today's real output includes 5 "失效背書" (stale-but-still-linked verifications), 19 dead-path references, 6 missing symbols, 1 drifted number claim — all soft, all printed by default. |
| `scripts/lumos context Systems/design-loop` | 74 | 15,312 | one node's context dump |
| `scripts/lumos loop next 檢核收緊五件 --tier high --spec …` | 8 | 534 | short here because this loop is already `phase=cap-reached` (3 rounds hit the tier-high cap) — a real, live example of the cap firing, not hypothetical |
| `scripts/lumos pitfalls <spec>` | 10 | 779 | fixed generic pitfalls prompt (concurrency/perf/resource + risk-class follow-ups); this is boilerplate reprinted for every spec regardless of what changed |

`scripts/lumos loop next` boilerplate (from source, `scripts/lumos:4929-4938`, the `scope_cap` field): a fixed ~700-char paragraph about the 1,800-line/30K-token soft scope cap, printed on **every** `phase=plant-canary` round (i.e., most rounds that aren't cap-reached/converged/gate-pending). Notably, the same paragraph now includes an internal retraction ("this repo's own data doesn't support the threshold — two controlled experiments found no scale effect") — so the tool is paying ~700 chars/round to repeat a caveat about a rule it admits isn't evidence-backed for this project. A `cluster_hint` block (~450 chars) is added on top for N=1 rounds. This is pure repeated prose, not computed data.

---

## 4. Design-loop / code-loop cost model

`_TIER_PARAMS` (`scripts/lumos:4589`): `light=(width1,cap2)`, `standard=(width3,cap3)`, `high=(width5,cap3)`, `legacy=(width1,cap6)`.
`_TIER_ROSTER` (`scripts/lumos:4627-4653`): design/high = 5 Claude seats + 1 external-veto (note-if-absent); code/high = 4 Claude + external finder + external veto (both **required-fail-closed**) + conditional spec-conformance seat — up to 7 seats/round.

**Real ledger counts** (`docs/.canary-log.jsonl`, 487 entries total):
- `tier=high`: 94 entries across 11 distinct loops → avg 8.5 seat-records/loop (max possible 5×3=15, so loops average under 2 full rounds before converging or hitting cap — the panel isn't always burning all 3 rounds, but when it does the cost below applies).
- `tier=standard`: 148 entries / 22 loops → avg 6.7/loop.
- `tier=none` (post 2026-08-14 canary-off): 237 entries / 41 loops — now the majority of traffic, confirming canary protocol really is retired in practice, not just on paper.
- `docs/.canary-log.jsonl` has **zero** entries with populated `tokens` or `wallclock_min` fields out of 487 — the schema supports cost telemetry but nothing has ever written it. There is currently **no mechanism to answer "how many tokens did this loop cost" from the ledger itself**; every number in this report had to be reconstructed from report-file sizes.

**Real example — 檢核收緊五件 (tier=high, 3 rounds, s1–s7 seats)**: `governance/review-reports/檢核收緊五件/` = 2,290 lines / **262,330 chars** across 29 files (per-seat .md reports 4–23K chars each, snapshots ~14–15K chars each, dispatch .json ~170 bytes each — dispatch overhead is negligible, seat *reports* are the cost). At ~2.5 chars/token blended, that's **~105,000 tokens of review-report prose alone** for one high-tier loop — not counting what each of the ~19 seat-invocations (7 seats × up to 3 rounds) individually read to produce those reports, which includes rereading source under review each time.

**Real example — doctor-run事件 (escalated light→standard, 4 rounds total)**: the actual code change was `scripts/lumos +28/-lines` (git show `9a95bc4`: 9 files changed, 152 insertions/13 deletions total, but the functional diff in `scripts/lumos` itself is 28 lines). Review artifacts: light r1 = 9,008 chars (1 seat), then standard r1/r2/r3 = 73,208 chars (3 rounds × 3 seats) = **82,216 chars total ≈ 33,000 tokens of review prose to land a ~28-line diff** — a ~1,200:1 ratio of review-text-chars to changed-code-lines. This is the single clearest evidence in the repo that **tier is driven by risk classification, not diff size**, and a small self-governance change (doctor's own scoring logic touches `_KNOWN_GATES`/ratchet machinery, hence "self-governance" risk tag) pays full standard-tier panel cost regardless of how small the patch is.

**Structural cost driver**: `scripts/lumos` is 15,068 lines / **782,671 chars ≈ ~195,000 tokens** if read whole. Design/code-loop seats are dispatched as fresh agents with no shared context — if even a subset of seats read the full file rather than a diff-scoped excerpt each round, a high-tier loop (5 seats × up to 3 rounds = 15 seat-invocations) could each be paying a six-figure-token entry cost just to load the file under review, dwarfing the ~100K tokens of report prose measured above. (I did not instrument individual seat dispatches to confirm full-file reads happen in practice — flagging as the highest-leverage unmeasured cost, not a confirmed number.)

---

## 5. L4 cross-audit cost

`governance/l4-audit/2026-08-21/`: 61 files, **328,815 chars (444K on disk)** for a stated 30 nodes × 2 agents design. Per-file average ~5,390 chars; individual `.verify.md`/`.claims.md` files sampled at 4.7K–6.8K chars each. At ~2.3 chars/token (heavier code-symbol content here — `check-u-overgeneralization`, `test-profile-multiplatform` etc.), that's **~143,000 tokens** for one day's L4 self-audit pass, before counting whatever each of the 60 agent dispatches read from the graph/repo to produce its file (this number is output-only, not input cost).

---

## Ranked optimizations

### Tier 1 — high savings, near-zero risk (config changes, do these first)

1. **Dedupe the double-registered hooks in `~/.claude/settings.json`.**
   `verification-rot-check.py` (PostToolUse/Bash, 60s) and `check-graph-sync.py` (Stop, 10s) are each registered twice with byte-identical commands (only the python3-invocation style differs). This doubles process-spawn overhead on *every* Bash call and *every* Stop event for the whole session, and — worse — doubles real Sonnet API spend on every qualifying `git commit` (up to 10 calls instead of 5). **Fix**: delete one entry per event in settings.json. Config-only change. Expected saving: ~50% of hook-triggered LLM spend on commits, ~50% of hook process-spawn overhead session-wide. Risk: none — it's a pure duplicate, not two different checks.

2. **Cap the "pinned" set in impact-hook's ranked output.**
   `build_ranked_context` in `impact-hook.py` puts *all* contract/incident-tagged direct+indirect hits into the unconditional "必看" section with no limit — measured 33 pinned entries for one edit to `scripts/lumos`. The doc claims "top-8 + 合約" but only the free/ranked tier is capped at 8; pinned is uncapped. **Fix**: cap pinned at e.g. 15 with an overflow counter, same pattern already used for the free tier (`meta['truncated']`). Code change, small (~10 lines in `build_ranked_context`). Expected saving: for high-fan-in files, cuts injection from ~2K chars to under ~1K chars per triggering edit — real saving scales with how central the file is (worst on scripts/lumos itself, the file most often edited).

3. **Populate `tokens`/`wallclock_min` in `.canary-log.jsonl` before optimizing further.**
   Every cost number in this report had to be reconstructed from file sizes because 0/487 ledger entries have the cost fields the schema already supports. **Fix**: have the loop-orchestrating Claude session (or a wrapper around the seat-dispatch Agent calls) fill these two fields on `canary record`. Config/process change, no code needed if the fields already exist — just start using them. This isn't a saving by itself, but it's the prerequisite for measuring whether any *other* optimization here actually worked, and for building tier-vs-diff-size cost curves instead of guessing from artifact sizes.

### Tier 2 — real savings, moderate engineering, worth doing next

4. **Share a pre-read evidence packet across seats instead of each seat re-reading `scripts/lumos` (782K chars / ~195K tokens) from scratch.**
   Structurally the biggest unmeasured cost in the system: a high-tier code-loop round dispatches up to 5+2 seats, each a fresh agent with no shared context. If seats read the whole file rather than a diff/excerpt, a single 3-round high-tier loop could burn 10+ full-file reads. **Fix**: have the orchestrator extract the relevant diff + touched-function context once, hand seats that packet instead of "go read scripts/lumos." Risk: a shared packet can bias independent seats toward the same blind spot (defeats the "N independent lenses" design intent) — needs the packet to include enough surrounding context that seats can still catch things outside the diff. Not a pure win; needs a design pass, not just a config flag.

5. **Scale seats/rounds by diff size, not only risk class.**
   Real evidence: doctor-run事件 (28-line functional diff) paid 4 rounds / ~33K tokens of review prose because it was tagged "self-governance" risk, same tier a much larger change would get. The `_CANARY_SCOPE_SOFT_CAP_LINES` mechanism (1,800 lines) already exists as a *ceiling* but nothing currently *lowers* width/rounds for small diffs within a risk class. **Fix**: within a risk tier, let `cap` scale down (e.g. standard-tier diffs under ~50 lines get cap=1 unless a first-round finding escalates). Code change in `_TIER_PARAMS`/`cmd_loop_next`. Risk: could let a small-but-load-bearing diff (e.g. a 5-line auth check) under-review; needs the risk-class tag to still dominate for known-dangerous categories (payment/external-send/irreversible), only diff-size-discount the generic "self-governance"/"internal-tooling" categories.

6. **Trim `doctor` default output — move the four soft-only checks ([V]/[P]/[Y]/[N], all explicitly labeled "軟提醒、不擋 CI") behind a `--full` flag, default output shows only counts + "see --full for detail".**
   Measured: today's real doctor run is 105 lines/7,243 chars; roughly 60 of those lines (56+ across E1/P/Y/N sections combined) are soft-advisory detail that never gates anything. **Fix**: default to one summary line per soft check ("⚠ 5 dead verified_by — run --full"), full detail only on demand. Config/code change (doctor already has a `--full`/`--stats` distinction per the git log — extend the same pattern to these checks). Expected saving: ~40-50% of doctor's default output size, with zero loss of gating behavior since these checks never block CI either way.

### Tier 3 — worth doing but needs more validation first

7. **Cheaper model for extraction-only phases (L4 phase 1, pre-flight/dispatch-json generation).**
   The 61-file L4 audit output includes many small dispatch/claims files that look like structured extraction, not judgment — plausible Haiku candidates. Not verified here which phases are pure extraction vs. judgment; would need to read the L4 audit orchestration code (out of scope for this pass) before recommending which specific calls to downgrade. Flagging as a lead, not a ready-to-ship fix.

8. **Forbid full-suite test runs inside review agents.**
   Not directly measured in this pass (would require instrumenting actual seat-dispatch transcripts), but the review-report file sizes (13-23K chars per seat) are consistent with seats pasting large command output rather than only findings. Recommend a follow-up pass specifically greping review-report .md files for pasted test-runner output / stack traces vs. actual finding prose, to size this one properly before prescribing a fix.

9. **Collapse `loop next`'s repeated boilerplate** (`scope_cap` ~700 chars, `cluster_hint` ~450 chars) into a one-line pointer on rounds after the first, full text only on round 1 or `--verbose`. Small saving in absolute terms (~1K chars/round) but it's pure constant-string overhead with no informational content after the first time a session sees it — cheapest possible fix (code change, ~5 lines) for a real if modest per-round tax across every panel loop in the repo (245 non-`none` canary-log entries × these two fields where applicable).

10. **Cache per-repo code maps** — not evaluated in this pass; would need to know what "code map" infrastructure (if any) already exists for seat dispatch before proposing a cache layer. Likely subsumed by #4 (shared evidence packet) rather than a separate mechanism.
