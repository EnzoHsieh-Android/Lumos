# B — `lumos doctor` 全檢查 + `cmd_lint` 稽核

Evidence sources: `scripts/lumos` read directly (line refs below), `docs/.governance-log.jsonl`
(20,566 lines), `scripts/lumos gov --since 9999 --stats`, live `scripts/lumos doctor` run on this
repo (2026-08-21, 313 nodes), `git log`/`git blame` on flagged nodes, `scripts/hooks/pre-push`,
`scripts/hooks/pre-commit`, `.github/workflows/ci.yml`, `scripts/test_lumos.py` (495 `t_*` tests).

**Key mechanical fact governing everything below**: `warn()` increments `issues` (→ rc=1 under
`--strict`/`--ci`, which is what `pre-push`/CI use) — **hard**. `warn_soft()` never touches
`issues` — **soft**, cosmetic only, cannot ever block anything regardless of content. Ledger
writes (`gov_events.append`) only happen inside 7 checks; `gov --stats` (run at `--since 9999`,
i.e. all-time) confirms exactly this — of the 16 gate names the tool knows about
(`_KNOWN_GATES`, line 2897), doctor contributes 8: `check-e1 check-e2 check-e3 check-j check-k
check-r check-s doctor-run`. **check-e2, check-e3, check-j, check-k, check-r have ZERO entries
in 20k lines of ledger, ever** (confirmed via `gov --stats` "未出現的 gate" list AND by grepping
`"gate": "check-x"` directly — both zero). Every other doctor check (1/4–4/4, 1.5/4, C, D, G, H,
L, M, N, P, T, V, Y) **cannot appear in the ledger at all** — no `gov_events.append` call exists
in their code path, hard or soft.

Enforcement path verified: `pre-push` (`scripts/hooks/pre-push:148`) does
`if "$PY" "$GRAPHCTL" doctor --ci; then exit 0; fi` — **rc only, no grep of section content**.
`.github/workflows/ci.yml:25` — same, `python scripts/lumos doctor --ci`, rc only. So every soft
section's text is cosmetic in the *enforcement* sense; it only matters if a human or Claude reads
stdout. `cmd_lint` is invoked by **neither** hook nor CI (`grep -rn "lumos lint" .github/
scripts/hooks/` → zero hits) — it is 100% opt-in, triggered only by a human/Claude manually
running `lumos lint <node>` per CLAUDE.md prose ("寫完節點 lumos lint 自驗"). Nothing mechanically
checks that this happened.

## Table

| mechanism | purpose | enforcement | fires? | reaches Claude? | verdict | proposed fix |
|---|---|---|---|---|---|---|
| **[1/4] Verification orphans** | Verification 節點沒被任何 Systems 認領 (line 490) | hard (rc) | not ledgered; live=0. Code comment (line 491, "真遺忘第二刀 2026-07-26") shows it did misfire on `superseded` nodes before that fix | yes, if it fires (blocks push, text in stdout) | 保留 | none — it's hard+tested, just invisible to gov audit; add ledger write so retention decisions have data |
| **[1.5/4] 未閉合 frontmatter** | catches `split_frontmatter` silently treating whole file as body → contracts vanish, wikilinks in block-scalars become real edges | hard (rc) | not ledgered; live=0. Explicit incident cited in comment (line 517-525): "2026-08-03 code-loop r4 抓到的既有 major" | yes | 保留 | add ledger write (it's the single scariest silent-corruption class in the tool — should have a firing history) |
| **[2/4] Unresolved wikilinks** | broken `[[link]]` targets | hard (rc) | not ledgered; live=0 | yes | 保留 | none |
| **[3/4] verified_by 雙向同步** | Verification→Systems back-link missing | hard (rc) | not ledgered; live=0 | yes | 保留 | none |
| **[4/4] plan_refs 意圖鏈** | closed Project has a newer Verification that didn't update it | hard (rc) | not ledgered; live=0 | yes | 保留 | none |
| **[G] 同名 basename 守衛** | duplicate basenames → ambiguous bare `[[link]]` resolution | hard (rc) | not ledgered; live=0 | yes | 保留 | none |
| **[L] frontmatter lint** | 鐵則 1/3/4 fingerprints + pollution fingerprints | hard (rc) | not ledgered; live=0 | yes | 保留 | none |
| **[M] 狀態標籤漂移** | `status:` field vs `status/*` tag disagree | hard (rc) | not ledgered; live=0 | yes | 保留 | none |
| **[C] core_refs 跨repo指針** | cross-repo file pointer dangling | hard (rc), only runs if `core_refs` used | not ledgered; live: N/A (no `core_refs` in this repo at all — section always prints "無 core_refs 指針") | n/a here | 保留(other consumer repos) | none |
| **[T] ★INVARIANT★ 合約測試綁定** | every load-bearing contract claim must cite a real, existing, independently-audited test method (not prose, not a fake name) | **hard** (rc) | **NOT ledgered at all** — no `gov_events.append` anywhere in the whole ~70-line block (lines 705-775), despite being arguably the single most important contract-integrity check in the tool. Live: 22/22 bound+audited, 0 issues | yes (hard, blocks push) | 修 | add `gov_events.append` for naked/fake/dangling/unaudited findings — right now there is no historical record of how often "someone tried to add an unaudited contract" happens, which is exactly the maker/checker metric this tool cares about elsewhere |
| **[R] 可逆性回退綁定** | ★IRREVERSIBLE★ must cite rollback/guard; ★CHECKPOINT★ soft-nudged | hard (err) + soft (checkpoint) | **ledgered** (`check-r`) — **0 entries ever** in 20k lines despite 12 live `★IRREVERSIBLE★` + 5 `★CHECKPOINT★` markers in the graph today. Explained: `gov_events.append` only fires on a *finding*, not on a clean pass — live doctor confirms all 17 markers currently resolve cleanly, so "0 fires" = "always compliant," not "never ran." Consistent with unit tests `t_reversibility_doctor`, `t_reversibility_lint`, `t_reversibility_guard_doctor` | yes | 保留 | the 0-ledger-entries fact is legitimately ambiguous evidence (clean vs. broken) — log a `passed` event too, not just findings, so "never checked" can be told apart from "always clean" |
| **[S] L4 自足性審計提醒** | Systems node missing/expired `self_audit` (nobody ever ran an independent maker≠checker re-audit) | **soft**, never blocks | **ledgered** (`check-s`) — **by far the highest-volume gate in the whole tool: 7,407 deduped / 18,583 raw entries**, 42 distinct nodes, spanning 2026-07-02→2026-08-21 (7 weeks). Top offender `anchor-integrity`: **1,013 repeated firings across 7 weeks**, unresolved, then cleared in one shot today by commit `8528198` "L4 交叉審計 30 節點清帳" (30 nodes cleared at once). Sampled: same 42 node names recur near-daily for weeks with zero incremental fix | technically yes (stdout), but see verdict | 精簡 | this is the textbook "reminder printed into a stream nobody reads incrementally" — 7 weeks of the same warning firing multiple times *per day* before a single bulk catch-up session cleared it. The per-push nag drove zero incremental behavior; only a deliberate audit sprint did. Either (a) throttle to "print once, then suppress until re-triggered" (like the `E2` ledger-suppression trick already built for that check, line 895-905) or (b) accept it's a batch-mode tool and stop pretending it's a per-push signal — cap the printed list harder (already caps at 8 via `_soft_list`, but 42 distinct nodes still means the same top offenders reprint every run) |
| **[E1] 失效背書** | `verified_by` points at a stale/fail/superseded Verification (dead endorsement, false confidence) | soft | **ledgered** (`check-e1`) — 703 deduped / 1752 raw since 2026-07-29 (3 weeks old feature). Live: 5 active findings, all pointing at the same superseded `2026-08-03_Windows真機驗證五缺陷修復` verification across 4 Systems + 1 stale `guard-kill` verification | yes | 保留 | genuinely catches something real (dead confidence signal) and has real live findings today — but nobody has fixed the 5 current ones; consider whether E1 findings should promote to hard once a dead endorsement is >N days old (mirrors the V check's 90-day staleness pattern) |
| **[E2] 建在被推翻決策上** | source node built on a since-reversed (`valid:false`) decision, didn't update after | soft | **ledgered** (`check-e2`) — **0 entries ever**, despite 15 files with `valid: false` decisions existing in the graph. Feature added with its own ledger-suppression mechanism (line 895-905) that was apparently never needed because it never fired even once | unknown (never fired) | 精簡 | can't tell "sound feature, no actual drift yet" from "logic bug that never engages" without a synthetic test — the code exists, is unit-tested (`t_check_e2_ledger_suppress`, `t_check_e2_build_on_superseded`), so probably the former, but 0/20k-lines over 7 weeks on a 313-node graph with 15 reversed decisions is suspicious enough to warrant one live dry-run before trusting it |
| **[E3] 意圖鏈斷義** | `decision_refs` pointing at a reversed decision | soft | **ledgered** (`check-e3`) — **0 entries ever**. Structurally explained: `decision_refs:` is used in exactly **1 file** in the entire 313-node graph — the feature this check depends on is essentially unadopted | n/a | 砍/精簡 | this isn't "the check never finds anything," it's "the field it checks is basically unused" — either drive adoption of `decision_refs` or retire E3 until it is |
| **[H] 漏標可逆性提醒** | diff touches something that smells irreversible (prod/external API/send) but no `★IRREVERSIBLE★` tag nearby | soft, **--ci only** (interactive `doctor` always skips it, line 1004-1005) | **not in `_KNOWN_GATES` at all** — no ledger path exists even in principle, hard or soft. Zero observability by design | only reaches Claude if Claude runs `doctor --ci` specifically (not plain `doctor`) and reads that section | 精簡 | give it a gate name and ledger write, or drop it — right now there is categorically no way to ever know if this has caught anything in its lifetime |
| **[K] ★COMBO★ 組合覆蓋提醒** | most-critical invariant (`★COMBO★`) should bind ≥2 tests, not just happy-path | soft | **ledgered** (`check-k`) — **0 entries ever**. Structurally explained: grep finds 6 files mentioning `★COMBO★`, but all are *documentation about the mechanism itself* (`Systems/check-t-sentinel.md`, `Projects/*_計劃.md` design docs) — **zero live `★INVARIANT★...★COMBO★[test:]` lines exist anywhere in the graph today**. Live doctor confirms: "✓ 無 ★COMBO★ 標記" | n/a | 精簡 | the mechanism has literally never had a single real target in this repo's lifetime; keep the code (cheap, tested) but stop counting it as an active gate until someone actually uses the marker |
| **[D] 紀律區塊漂移守衛** | CLAUDE.md injected discipline block drifted from `scripts/templates/graph-discipline.md` | **hard** (uses `warn()`, not `warn_soft()` — line 1070, 1078) | not ledgered (no `gov_events.append` in the block at all, despite being hard/rc-blocking). Live: 0 issues (in sync) | yes, and it can fail your push | 保留 | this is a template-sync check masquerading as a graph-integrity check, and it's the *only* hard check with zero ledger visibility on top of that — add the write |
| **[V] valid_under 過期率** | `valid_under` (entry-prompt precondition) nodes >90 days stale, precondition may no longer hold | soft | not ledgered. Live: 0/116 (0%) — currently clean | yes | 保留 | fine as-is; cheap and currently 0% so not noise |
| **[P] 失效檔案認領** | inline-code repo paths cited in graph nodes that no longer exist on disk | soft | not ledgered. Live: **19 lines every run**. Sampled 4 of the flagged source nodes via `git log`/status: all `status: done` / `superseded` / `pass` (completed Projects/Verification referencing scratch paths deliberately deleted post-completion) — i.e. **these are permanent historical noise, not live drift**, and Check P has no status-based exemption (unlike E1, which explicitly skips `stale/fail/superseded`) | yes, but see verdict | 修 | add the same `status in (done/pass/superseded)` exemption E1 already uses (or scope to `status: doing`/open nodes only) — otherwise this list only grows and never reaches 0, training everyone to skip past `[P]` |
| **[Y] 被提及符號存在性** | symbol named in a Systems node's inline-code doesn't exist in repo (wrong name / renamed, catches drift that never shows in a diff) | soft | not ledgered. Live: **6 lines every run, but all 6 are from the check's own self-documenting example nodes** (`Systems/check-y-symbol-existence.md`, `Systems/drift-history.md`) quoting *historical* bug examples (`ActivityService.RegisterAsync` etc.) as illustration prose, not live claims — same class of false-positive Check N already patched for its own docs on 2026-08-21 ("圍欄內是語法範例不是宣稱" fix, line 1244) but Check Y never got the equivalent fix | yes, but 100% self-inflicted noise right now | 修 | same fence-vs-prose fix Check N just got for itself — Check Y is currently permanently "dirty" from its own documentation |
| **[N] 可重算數字宣稱** | body has `<!--lumos:count=N re=... in=...-->` and the recomputed count disagrees | soft | not ledgered. Live: 1 line (a Projects doc claims 15, actual 16) | yes | 保留 | good design (doctest-style single source of truth), low noise, keep |
| **[J] regen 重生來源守衛** | from-scratch node contracts need provenance evidence (`[src:]`/`[git:]`), can't invent a contract from nothing | hard (err) + soft (warn), section only prints if any `regen:` field exists | **ledgered** (`check-j`) for hard errs — **0 entries ever**, structurally explained: **0 nodes in this graph use the `regen` field at all** (`grep -rl "^regen:"` → 0). The entire J section is dead code in this repo (guarded by `if _regen_rels:`, never true) | n/a here | 保留(other repos) | none for this repo; note for cross-repo audits that "regen" adoption should be checked separately |
| **[N] 版本更新提示** *(dev-machine advisory)* | nudge to run `lumos update` when local tool version is behind | soft | not ledgered. **Reuses the section label `"N"`** — literal duplicate of Check N above (`grep -n 'section("N"' scripts/lumos` → lines 1231 and 1323, two unrelated mechanisms both printed as `[N]`) | yes when it fires (not observed live today — versions in sync) | 修 | rename this section (e.g. `[U]` or `[Nv]`) — a human or script scanning for `^\[N\]` conflates two unrelated checks; also it isn't a graph-integrity check at all, it's a CLI self-update nag and arguably doesn't belong in `doctor` output |
| **doctor-run** (meta marker) | distinguishes "ran clean" from "ran and found nothing to report" in the ledger, since silence was previously ambiguous | n/a (always `hard: False`, no `nodes`) | **ledgered** — 2 entries, both today (2026-08-21) — feature literally just shipped this session (`Verification/2026-08-21_doctor-run事件落地.md`, mentioned in [P]'s own findings list as a dead-path — ironic) | n/a | 保留 | too new to judge; revisit after a few weeks of data |

## cmd_lint (line 2606-2798) — never invoked by any hook or CI

Confirmed via `grep -rn "lumos lint\|cmd_lint" .github/workflows/ scripts/hooks/` → **zero hits**.
Pure opt-in, human/Claude must type `lumos lint <node>` per CLAUDE.md prose instruction; nothing
mechanically checks that this happened. None of its findings ever write to the governance ledger
(explicit code comment, line 2741: "lint 一律不落帳(高頻)").

| mechanism | purpose | enforcement | fires? | reaches Claude? | verdict | proposed fix |
|---|---|---|---|---|---|---|
| frontmatter fingerprints (`n.lint`) | ghost-trap / dup-key / quoted-date pollution | hard (errs→rc1) | overlaps doctor `[L]`, same 0-issue live state | only if Claude manually runs `lumos lint` | 保留 | none |
| type/summary presence | missing `type`, unknown `type`, missing `summary` block for system/issue | hard | not measured (no ledger, no live sample beyond current clean graph) | same as above | 保留 | none |
| `aliases:` requirement (cutoff 2026-08-05) | force a judged decision on synonyms, not silently absent (`aliases: []` = judged-none) | hard, cutoff-gated (new nodes only) | untested here; incident: 2026-08-05 Enzo ruling per comment, no drift data since nothing calls lint automatically | only if manually run | 保留 | wire into pre-commit for newly-created system/issue nodes at minimum — cutoff-gated rules that nothing enforces are trivially forgettable |
| status/priority/risk/FLAG enum enforcement (cutoff 2026-08-06) | closes free-text drift ("13 status同義混用, 50+ FLAG自由文字") | hard, cutoff-gated | incident well-documented in comment (Landmark 野化 measurement); zero mechanical enforcement path exists — a node can violate every enum rule and pass pre-commit/pre-push/CI cleanly forever, since only `lumos lint` checks this and nothing calls it | only if manually run | 修 | same as above — this is exactly the kind of rule that needs a mechanical trigger, not honor system, per the tool's own design philosophy elsewhere (pre-commit/pre-push are "the mechanical guard" pattern used everywhere else) |
| `feature/area` tag deprecation | migrate old tag family to `scope/` | soft (warn) | n/a | only if manually run | 保留 | none |
| decisions structural guard | catches YAML indentation swallowing decision entries silently (2026-07-29 外審實錘, explicit incident) | hard | real incident cited in comment (line 2676-2678) | only if manually run | 修 | this guards against a *silent* corruption class per its own comment ("doctor 全綠——綠燈≠schema 有效") — exactly the kind of thing that should NOT depend on someone remembering to run `lumos lint`; promote to doctor or a hook |
| status/status-tag drift | duplicate of doctor `[M]`, single-file version | hard | overlaps `[M]` | only if manually run | 精簡 | redundant with doctor `[M]` which *is* on the pre-push path — this copy's only value is faster feedback during editing, keep as advisory |
| symbol-line typo (KEY/FLOW/DEP/…) | catches misspelled summary-line prefixes | soft (warn) | n/a | only if manually run | 保留 | none |
| `★INVARIANT★`/`★DEBT★` marker position | marker must be KEY-line prefix or contracts/doctor won't see it | hard | n/a | only if manually run | 保留 | none |
| naked/unaudited `★INVARIANT★` (Check T single-file) | same as doctor `[T]`, single-file, catches it before the node is even committed | hard | overlaps `[T]`, which is itself hard+ledger-blind (see above) | only if manually run | 保留 | none |
| Check J single-file (regen) | same as doctor `[J]` | hard+soft | 0 regen nodes in this repo | only if manually run | 保留(other repos) | none |
| Check R single-file (reversibility) | same as doctor `[R]` | hard+soft | overlaps `[R]` | only if manually run | 保留 | none |
| **Check U** 全稱宣稱未綁測試 | catches "全稱量詞 + 程式實體 + 義務語氣" claims presented as universal rules but not backed by a test (fitness-function pattern) — added 2026-08-12 | soft (warn only) | real incident cited: LandmarkMember 24-file audit, 389 claims/59 inconsistencies, one real case (`CustTransfer`/滿額贈 folding guard) sat wrong from 2026-06-02 to 07-21 before a user reported it. Precision-tuned (17%→1% false-positive rate per comment) | only if manually run | 保留 | genuinely good design (borrowed from ArchUnit/fitness-function prior art per its own comment) but same problem as everything else in this file: **nothing calls `lumos lint`**, so this only fires if a human remembers |

## Top 5 deficiencies (blunt)

1. **`cmd_lint` is a complete no-op in practice.** Zero hooks, zero CI steps call it
   (`scripts/hooks/pre-commit`, `scripts/hooks/pre-push`, `.github/workflows/ci.yml` — none
   reference it). Every rule in it, including ones with real documented incidents (decisions
   structural guard, 2026-07-29; enum enforcement, Landmark 野化; Check U, 2026-06-02→07-21
   silent-wrong period) is honor-system: "Claude reads CLAUDE.md and remembers to type `lumos
   lint`." That's the exact failure mode the rest of this toolchain was built to eliminate
   (pre-commit/pre-push exist *because* honor-system was deemed insufficient for graph sync).

2. **Check [S] fired 1,013 times on one node over 7 weeks before being fixed in a single bulk
   commit today** (`8528198`, "L4 交叉審計 30 節點清帳"). 7,407 deduped / 18,583 raw ledger
   entries total — by far the highest-volume mechanism in the tool, and the data shows the
   per-push nag drove zero incremental fixing; only a deliberate audit sprint cleared it. A soft
   warning that reprints unchanged for 7 weeks is functionally invisible.

3. **Check [T] (★INVARIANT★↔test binding — arguably the most important contract-integrity check
   in the whole tool) writes to no ledger at all**, hard or soft — same for Check [D] (CLAUDE.md
   sync, also hard/rc-blocking). Both can fail a push and nobody can query "how often has this
   actually caught something" from governance data — you'd have to grep doctor's stdout history,
   which isn't retained anywhere.

4. **Checks [Y] and [P] currently print noise on every single run that will never resolve**:
   [Y]'s 6 findings are 100% self-inflicted from its own example-documentation node quoting
   historical bugs as prose (same false-positive class Check N already patched for itself on
   2026-08-21, but the fix wasn't applied to Y); [P]'s 19 findings are dead paths in
   `done`/`superseded`/`pass` historical records that Check P has no status exemption for (E1 has
   this exemption, P doesn't). Both will reprint indefinitely — training readers to skip `[P]`/`[Y]`
   entirely, which then hides any *real* future finding in the same sections.

5. **check-e2, check-e3, check-j, check-k, check-r have literally zero ledger entries across
   20,566 lines / 7 weeks**, and for 3 of them (check-k, check-j, check-e3) the reason is
   structural, not "everything's clean": the features they gate (`★COMBO★` on a live invariant,
   `regen:` field, `decision_refs:`) are essentially unused in this graph (0, 0, and 1 occurrence
   respectively). These aren't proven-working safety nets catching zero problems — they're mostly
   untested-in-anger code paths whose trigger conditions almost never occur here.
