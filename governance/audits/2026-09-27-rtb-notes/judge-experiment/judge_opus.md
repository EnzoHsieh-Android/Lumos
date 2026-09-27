| n | label | confidence | code location (or —) | one-line reason |
|---|---|---|---|---|
| 1 | CODE | high | src/rtb/demo/page.py:432-434 | meta refresh `content="2; ..."` is in the page renderer (confirmed) |
| 2 | MIXED | high | claims/*.json (5 files); evidence nodes total 78 (e.g. claims/concurrency.json:266); src/rtb/demo/driver.py:1497 says 77 | CODE: 5 lists, 75 evidence tests (now 78, refuted). CONTEXT: "42.4 秒" is a measured run time |
| 3 | CONTEXT | high | — | What the project wants to demonstrate plus a design principle; intent, not code state |
| 4 | CONTEXT | med | — | Stated as an aim ("讓…") and a from-day-one design intent; code alone cannot establish the intent |
| 5 | CODE | high | tests/executor/audit_guard.py:13-14 | Claim that no guard exists; write_stops/approvals/dsp_calls/operations are in the append-only guard list (refuted) |
| 6 | CODE | low | src/rtb/demo/driver.py:1821 (comment says no longer relaxed); driver.py:1676-1690 (limits 120/150/300 s) | Scenario time limits and relaxation are code constants; no recording-mode relaxation or 60 s cap was found (probably refuted) |
| 7 | MIXED | med | src/rtb/eval/rule_mining_vocab.py:22; src/rtb/eval/rule_mining_prompt.py:9-14 | CODE: the version bump to phase15-rule-mining-v2 and changes applied to both the AI and exhaustive sides. CONTEXT: plan mandate, expected no bias, and the rationale section |
| 8 | CODE | high | src/rtb/analyzer/instrumented.py:85-110 | Says re-read happens only on the AI path; `rule_source` re-reads in rule step C (refuted) |
| 9 | CODE | high | src/rtb/eval/generator.py:19-20; src/rtb/domain/worth.py:33-38 | 5 cells × BASES_PER_CELL=20 × 3 VARIANTS (confirmed) |
| 10 | CODE | high | src/rtb/stepbudget.py:22-25 | MODEL_TIMEOUT 15, GROUP_EXIT_WAIT 5, SETTLE_ATTEMPTS 3 (confirmed) |
| 11 | CODE | high | src/rtb/analyzer/policy.py:156-158 | code_rule now calls the nine rules, not just positive impressions/clicks (refuted) |
| 12 | CODE | high | src/rtb/analyzer/flow.py:238,259; src/rtb/analyzer/runner.py:1-3 | operation_lookup parameter is code; "no launcher" is refuted by runner.py |
| 13 | CODE | high | src/rtb/analyzer/policy.py:12,156-158 | What the formal decision looks at is code; it is now nine rules with four queries (refuted) |
| 14 | CONTEXT | high | — | Reasons for choosing the test framework |
| 15 | CODE | high | src/rtb/analyzer/flow.py:428-434 | _BLOCK_CODES is a fixed set of 7, not 5 (partly refuted) |
| 16 | CONTEXT | med | — | Reasoning about what is needed to reproduce a failure mode (design rationale) |
| 17 | CODE | high | src/rtb/httpkit.py:29,253-255 | LOOPBACK 127.0.0.1; a missing Host is allowed only for HTTP/1.0 (confirmed) |
| 18 | CODE | high | src/rtb/executor/runner.py:39 | EXIT_UNSAFE_DB = 5 for hard-linked db (confirmed) |
| 19 | CODE | high | src/rtb/analyzer/policy.py:32; src/rtb/analyzer/dsp_client.py:389 | Nine rules are wired into the formal path, and the cross-window check exists (refuted) |
| 20 | CONTEXT | high | — | Record-keeping requirement and why eval batch changed (motive) |
| 21 | CODE | high | src/rtb/ops/metrics.py:74,84-85 | MAX_WINDOW 24h, EXIT_WINDOW_TOO_LONG 4, EXIT_UNSTABLE 5 (confirmed) |
| 22 | CODE | high | src/rtb/executor/dsp_client.py:148 | Executor DSP client has `write` (refuted) |
| 23 | CODE | high | src/rtb/analyzer/policy.py:338-343 | Demo-rule proposal hard-codes revision=1 (confirmed) |
| 24 | CODE | high | src/rtb/domain/nine_rules.py:291-293 | now >= D+4 00:00 UTC (confirmed) |
| 25 | CODE | med | src/rtb/analyzer/policy.py:12; src/rtb/stepbudget.py:38 | Claims evidence sufficiency is unimplemented and fixed at two pieces of evidence; the rule round now reads four queries in A/B/C steps (refuted) |
| 26 | CODE | high | src/rtb/analyzer/flow.py:238,259; src/rtb/analyzer/runner.py:1-3 | Same as 12 (parameter confirmed, "no launcher" refuted) |
| 27 | CODE | high | src/rtb/analyzer/task_store.py:22-27 | renew_lease removed; leases are only acquired and released, never renewed (refuted) |
| 28 | CODE | high | src/rtb/modelcore.py:56-57 | DEMO_CAP 1 USD, MONTH_CAP 20 USD (confirmed) |
| 29 | CODE | high | src/rtb/ops/slo.py:42,118-121 | Burn rates 14.4 / 6, SCALE=60 (confirmed) |
| 30 | CONTEXT | med | — | Design requirement or goal for the security rules |
| 31 | CODE | high | 18 modules with `__main__` under src/ (e.g. src/rtb/analyzer/runner.py, src/rtb/ops/slo.py) | Count of CLI entry points is repo-countable; now 18, not 9 (refuted) |
| 32 | CODE | high | src/rtb/dsp/store.py:72-74 | OPERATION_PAGE = 50 (confirmed) |
| 33 | CODE | high | src/rtb/analyzer/task_store.py:144,830 | f"replan_limit_reached={MAX_GENERATION}" with MAX_GENERATION=3 (confirmed) |
| 34 | CODE | high | src/rtb/analyzer/task_store.py:122-125 | LEASE_DURATION 60 s, commented 暫用 (confirmed) |
| 35 | CODE | med | src/rtb/dsp/server.py:117; src/rtb/dsp/capability.py:29 | Campaign write actions are update_budget and pause_campaign; the capability also allows void_operation (mostly confirmed) |
| 36 | CODE | high | src/rtb/executor/inbox_store.py:65-67 | 50 revisions, 5000 rows, 2h retention (confirmed) |
| 37 | CODE | high | src/rtb/analyzer/policy.py:156-158; src/rtb/domain/worth.py:94 | The ">0" check survives only as a cell classifier; the current code rule is the nine rules (refuted as the "current rule") |
| 38 | CODE | high | src/rtb/demo/flow.py:63,142-144 | a_candidate branch still present (confirmed) |
| 39 | CODE | high | src/rtb/eval/adoption.py:29-32 | 0.95/73, 0.80/16 (confirmed) |
| 40 | CODE | med | src/rtb/analyzer/runner.py:41 | EXIT_UNSAFE_CONFIG = 7; the "改" (a past change) is minor history (confirmed) |
| 41 | CODE | high | src/rtb/executor/capability_signer.py:41-46,102-111 | Tenant has campaigns, max_budget, and aggregate_limit, which is three fields (refuted) |
| 42 | CODE | high | src/rtb/analyzer/runner.py:42,163 | Doubling backoff capped at 10 s (confirmed) |
| 43 | CODE | high | src/rtb/demo/driver.py:938 | F7_CAMPAIGNS 300, F7_WORKERS 8 (confirmed) |
| 44 | CODE | high | src/rtb/analyzer/policy.py:156-158 | Says worth is a one-line proxy; it is now the nine rules (refuted) |
| 45 | CODE | high | src/rtb/analyzer/runner.py:4-7; src/rtb/analyzer/task_store.py:122-124 | The runner asserts the lease inequalities at startup (refuted) |
| 46 | CODE | high | src/rtb/eval/investigation_eval.py:4,121; src/rtb/analyzer/ai_judge.py:3,20 | Per-case ai_judge call confirmed; "same function as the formal path" and the renew callback are refuted (eval-only, callback removed) |
| 47 | MIXED | med | src/rtb/analyzer/policy.py:188-197; src/rtb/domain/worth.py:88 | CODE: routing ignores the cell when there is no candidate, and the cell type and function exist. CONTEXT: "在增量 1" is delivery history |
| 48 | CODE | high | src/rtb/executor/runner.py:42-43 | BUSY_LIMIT 3, EXIT_BUSY 6 (confirmed) |
| 49 | CODE | high | src/rtb/executor/guardrails.py:19 | DECISION_FRESHNESS 15 min (confirmed) |
| 50 | CODE | high | src/rtb/analyzer/task_store.py:121,743 | MAX_ERROR_DETAIL_LENGTH 2000 truncation (confirmed) |
| 51 | CODE | high | src/rtb/capabilitykit.py:34,54-55 | MIN_KEY_BYTES 32 and is_usable_key (confirmed) |
| 52 | CODE | high | src/rtb/analyzer/flow.py:322,343,349,370,404 | Five FAILED sites (evidence corruption, pure-computation errors, etc.) (refuted) |
| 53 | MIXED | med | src/rtb/eval/rule_mining_prompt.py:9-12; src/rtb/eval/rule_mining_baseline.py:138; src/rtb/eval/rule_mining_vocab.py:22 | CODE: preflight checks denominators and bytes, not sign or rank, and the version is now v2 so "首版" is stale. CONTEXT: "計劃要求" is the plan mandate |
| 54 | CONTEXT | high | — | User ruling and the conclusion of the evaluation |
| 55 | CONTEXT | med | — | Security goal and threat-model assumption |
| 56 | CODE | high | src/rtb/analyzer/policy.py:78 | `__call__(worth_input, timeout_seconds)` (confirmed) |
| 57 | CODE | high | tools/verify_claims.py:53; src/rtb/demo/driver.py:1499 | 900 / 960 (confirmed) |
| 58 | CODE | high | src/rtb/analyzer/runner.py:14-16,73-78 | --ai-judge no longer exists (refuted) |
| 59 | CONTEXT | high | — | Design principle (testability, no speculative abstraction) |
| 60 | CODE | high | src/rtb/analyzer/runner.py:1-7 | Launcher and lease guard both exist (refuted) |
| 61 | CODE | high | src/rtb/domain/evidence.py:23; src/rtb/domain/_checks.py:15 | 512 / 128 (confirmed) |
| 62 | MIXED | low | claims/prompt-injection.json ("policy" field) | CODE: the claim's current scope is checkable, and it now says AI does not take part at all (stale). CONTEXT: "改成" is a past revision event |
| 63 | CODE | high | src/rtb/domain/_checks.py:28; src/rtb/domain/nine_rules.py:93-95 | Fixed two-decimal amount strings (confirmed) |
| 64 | CODE | high | src/rtb/executor/inbox_store.py:69 | MAX_EVENTS_PER_CODE 200 (confirmed) |
| 65 | CODE | high | src/rtb/analyzer/runner.py:14-16,73-78 | Flags removed, fixed rule round (confirmed) |
| 66 | CODE | high | src/rtb/executor/attempt_store.py:51-54 | 3 / 5 / 50 / 20 (confirmed) |
| 67 | CODE | high | src/rtb/demo/driver.py:148 | NINE_RULES for every demo decision (confirmed) |
| 68 | MIXED | med | src/rtb/executor/attempt_store.py:769-772,791 | CODE: the overflow fallback path exists. CONTEXT: the rejected "store the total separately" alternative and its reason |

**Counts:** CODE 53 · CONTEXT 9 · MIXED 6 (total 68)

- CONTEXT: 3, 4, 14, 16, 20, 30, 54, 55, 59
- MIXED: 2, 7, 47, 53, 62, 68
