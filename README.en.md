<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/lumos-logo-dark.png">
    <img src="assets/lumos-logo.png" alt="Lumos" width="320">
  </picture>
</p>

# Lumos

[繁體中文](README.md) · **English**

**Lumos is an engineering governance toolkit for AI-assisted development.**

From understanding a request to implementation, review, verification, and handoff, Lumos connects project context, important rules, and development checks. A change leaves more than code: it also leaves the reasoning, its impact, and how it was checked.

The toolkit combines a Markdown knowledge graph, a CLI, AI working instructions, and enforcement checks for Claude Code or Codex. You describe the goal and make trade-offs; the AI follows the workflow to retrieve context, implement, and write back. Business decisions and risk acceptance remain human responsibilities.

Each change moves through four stations: **Notes → Dispatch → Review → Write-back**. Around that loop, evals use the accumulated records to check and calibrate the process.

<p align="center">
  <img src="assets/map-en.svg" alt="The Lumos loop: retrieve context from notes, dispatch, review, and write back; evals use each round's records to calibrate the process" width="900">
</p>

[Who it's for](#who-this-is-for) · [Install](#getting-it-installed) · [First use](#your-first-time-through) · [The four stations](#notes) · [Limits and scope](#scope) · [Documentation](#going-deeper)

## Who this is for

Lumos is most useful when you rely heavily on AI for development and need to maintain a project across people or sessions. Changes involving payments, inventory, permissions, or data migrations need more than working code: they need clear boundaries, preserved behaviour, and an understanding of downstream effects.

It connects work that is otherwise easy to scatter across tools and conversations:

| Question during development | What Lumos provides |
| --- | --- |
| Why was this designed this way? Which rules must hold? | Searchable decisions, boundaries, and contract notes |
| Who should review this change, and what should they check? | Relevant context, separate review perspectives, and risk tiers |
| What supports the claim that this was verified? | Bound contract tests, verification records, and gates |
| Can the next session pick up where this one stopped? | Decisions, review dispositions, and results written back to the graph |

**There is an adoption cost.** Maintaining notes, running checks, and using multiple reviewers consume time and tokens. A disposable prototype or a mostly hand-written project with little handoff may not need the whole workflow. Using Lumos does not mean turning every small edit into a design project.

## Getting it installed

You need **Git, Python 3.9+**, and Claude Code or Codex. Installation adds more than a CLI: it installs shared tools and skills, and project initialization adds a knowledge graph, AI instructions, and hooks. See [onboarding](ONBOARDING.md) for the scope of those changes.

Run this from the project you want to onboard:

```bash
curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.sh | bash
```

When the script asks whether to initialize the current directory, check the directory before answering `y`. Pressing Enter skips initialization. You can also download and inspect the script before running it.

After installation, **start a new AI session**, then check the wiring:

```bash
lumos enforcement
```

This reports whether checks are installed, registered, and connected. **It does not establish that their judgements are correct.** Information unavailable locally, such as platform trust settings, is reported as unknown and needs separate confirmation.

For Windows, existing Lumos projects, offline installation, and removal, see [onboarding](ONBOARDING.md).

## Your first time through

Start with a small change that is easy to verify. For example, tell the AI:

> Add refunds to the existing payment flow. First check the project notes and identify rules that must hold, affected areas, and how to verify the change. Confirm the approach before implementing it, then write back the decisions and verification results.

This illustrates the workflow; it is not a complete refund specification. If eligibility, amounts, or permissions are unclear, the AI should ask you.

<p align="center">
  <img src="assets/first-change-en.svg" alt="Illustrative workflow: request refunds; the AI reads payment rules, implements and tests; decisions and verification results remain available for future work" width="900">
  <br>
  <sub>Workflow illustration, not a recorded test result. Actual steps depend on project rules and change risk.</sub>
</p>

You do not need to memorize the CLI. Installed instructions tell the AI when to query and write back; hooks remind it or block incomplete work at the relevant stages.

For example, changing code without updating notes triggers the commit check. The AI needs to update the relevant context or handle a no-note-change exception according to project rules. This brings unfinished work back into the workflow; **it does not guarantee the AI can resolve every block on its own**. Trade-offs and risk decisions still need you.

At the end, look for three things: **what changed, what was actually verified, and which decisions or limitations were recorded**. A test that was not run should not be reported as passing.

## Notes

**Station ①: retrieve the context the change needs.**

The knowledge graph is a set of linked Markdown notes that can be versioned with the project. It records design reasoning, module boundaries, important rules, incident lessons, and the conditions under which something was verified.

For example, a shop can connect a refund plan to the payment module, a rule against duplicate refunds, and the test that guards that rule:

<p align="center">
  <img src="assets/graph-demo-en.svg" alt="An illustrative shop knowledge graph: plans connect to features and verification records; incident lessons feed later plans" width="760">
</p>

The AI can search by question or look up notes associated with a changed file, retrieving material relevant to the task. **Registered links are not a complete dependency analysis**: the graph provides leads that still need checking against code and actual behaviour.

Important rules can be marked as contracts and bound to tests. That makes a “must not change” claim traceable, but passing tests establish only the scenarios they cover. Whether a rule still fits the business is not a tool-only decision.

[See note structure and impact-query illustrations](docs/mental-model.md#9-visual-reference)

## Dispatch

**Station ②: equip reviewers without removing independent judgement.**

<p align="center">
  <img src="assets/dispatch-overview-en.svg" alt="One brief branches into independent reviewers, whose findings are collected and addressed" width="900">
</p>

Dispatch packages the change, related notes, and important rules for reviewers with different perspectives. Seats cannot see one another's reports, reducing the opportunity to copy conclusions. Agreement still does not guarantee correctness.

At intake, citations are checked and findings are recorded as adopted, rejected, or awaiting action. The point is not simply to ask more AIs: each finding needs a basis and a disposition.

[See the full dispatch, intake, and disposal-gate flow](docs/mental-model.md#7-reading-the-detailed-diagrams)

## Review

**Station ③: check architecture, known problems, and actual behaviour separately.**

<p align="center">
  <img src="assets/review-overview-en.svg" alt="Architecture review and three complementary checks: linters, questions and reviewers, and tests" width="900">
</p>

Review covers more than bugs. An architecture seat compares the change with existing code at the same layer, looking for a second competing approach or calls that bypass established boundaries—not merely differences in personal style.

Complementary checks cover the implementation:

- **Linters** check encoded rules and common violations.
- **Stack questions and review seats** require explanations for relevant performance and reliability concerns, then challenge their evidence.
- **Tests** execute the bound tests for affected contracts and check actual behaviour.

Pre-push code review is risk-tiered; small changes do not all trigger the same review effort. Gates can require answers and evidence to exist, but format checks alone cannot establish that an answer is correct.

[See the three layers, stack triggers, and push gates](docs/mental-model.md#7-reading-the-detailed-diagrams)

## Write-back

**Station ④: turn this change's results into the next change's input.**

After a change, the AI writes design trade-offs, review dispositions, verification results, and unresolved work into the relevant notes. The next session can retrieve the reasoning and constraints instead of reconstructing everything from code.

More notes are not automatically better. Decisions can expire and tests have assumptions. Records need updating, re-verification, or stale markers as the system changes.

<details>
<summary>See the growth of Lumos's own knowledge graph</summary>

<p align="center">
  <img src="assets/graph-growth.gif" alt="A recording of the Lumos knowledge graph accumulating notes and links during development" width="820">
  <br>
  <sub>440 notes and 1,572 links at recording time. This illustrates scale; it is not a reading guide or evidence of improved quality.</sub>
</p>

</details>

## evals

**The outer loop: evaluate the process itself, so changes can be compared.**

Evals are evaluations. Lumos records review seats, findings, and dispositions, freezes accepted gate verdicts as replay references, and uses weekly replay to check whether rule changes alter earlier outcomes. Retrieval has a separate set of human-labelled questions for comparing algorithm changes.

These records support calibration; they do not guarantee that review quality improves with every round. [Explore the machinery](docs/mental-model.md#6-what-the-review-loop-actually-runs)

## Why plain language

The primary workflow is conversational: you describe the goal, state constraints, and compare approaches, then the AI executes. Those conversations already contain useful design context. Lumos brings it into a queryable, verifiable development workflow.

This does not mean engineers no longer need to understand code, or that writing code by hand has no value. You still need to assess requirements, architecture, deployment, and verification. Lumos aims to reduce repeated context-setting and after-the-fact record keeping.

## Why this exists

I believe AI will take on more implementation work. But a model that writes better code does not automatically preserve every project trade-off, or keep rules, documentation, and tests aligned.

I want context to live outside the model, with its maintenance connected to development. The foundation of the next generation of software development is not just code generation: it is also evidence behind changes, traceable decisions, and systems that the next person can maintain.

Lumos is my implementation of that idea.

## Scope

Lumos supplies the reusable toolkit: the notes CLI, working instructions, checks, Git hooks, and cross-project stack conventions. Business knowledge, framework choices, and release procedures belong to each project.

It **does not guarantee quality or safety, or replace engineering judgement**:

- The graph can be incomplete or stale. Resolve conflicts against code, tests, and actual operation.
- AI reviewers can miss problems. An answer or a record is not proof that its contents are correct.
- Effective enforcement depends on installation, platform settings, and CI wiring—not just a healthy local report.
- Business trade-offs, irreversible actions, and risk acceptance still need human confirmation.

## Going deeper

- **How does each check work?** [The mental model and the machinery](docs/mental-model.md)
- **Installing or taking over an existing setup?** [Onboarding](ONBOARDING.md) (Chinese)
- **No notes in the existing project?** [Taking over a project](docs/taking-over.md)
- **Looking up an operation?** [Command reference](docs/command-reference.md)
- **Internal design or a comparison with SDD?** [Architecture](ARCHITECTURE.md) · [SDD and Lumos](SDD-vs-Lumos.en.md)
- **The full methodology?** [Overview](docs/methodology/圖譜即合約-全景圖.md) · [Public explanation](docs/methodology/圖譜即合約-對外論述.md) · [Design and evolution](docs/methodology/圖譜即合約.md) (Chinese)

## Licence

[MIT](LICENSE), covering the Lumos toolkit files, including tools copied into your project.

Your notes are yours. Lumos claims no rights over them.
