<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/lumos-logo-dark.png">
    <img src="assets/lumos-logo.png" alt="Lumos" width="320">
  </picture>
</p>

# Lumos

[繁體中文](README.md) · **English**

[![CI](https://github.com/EnzoHsieh-Android/Lumos/actions/workflows/ci.yml/badge.svg)](https://github.com/EnzoHsieh-Android/Lumos/actions/workflows/ci.yml)

**When AI writes your code, have it record the reasoning too.**

Lumos is built for natural-language development: you describe what you need, and AI proposes and implements a solution, without being tied to one programming language. It adds a layer of control and records—a harness—to address five problems: opaque work, lost context, stale notes, hard-to-verify results, and increasingly messy architecture. The goal is to keep people in control without reading every diff line by line, so they can delegate more development to AI and advance several projects at once.

Coding through conversation is fast, but trade-offs and rejected options stay in that conversation. Reopen it, and the context is there. Three months later, when someone edits the same file, nobody remembers which conversation it was; teammates and other AI tools cannot see it either. Code may check that "an order must never be refunded twice" without explaining why the check must stay. AI says the tests passed, but afterward you cannot tell which ones it ran.

Lumos keeps that context in the project. With Claude Code or Codex, it requires AI to record each code change's reasons, rules to preserve, and verification method in Markdown notes. Versioned alongside the code, the notes are available to anyone using any tool. At commit and push time, Git hooks check what can be automated, such as whether notes were updated. Think of ADRs (architecture decision records), CODEOWNERS, and pre-commit combined to check AI's work. For code quality, Lumos uses each language's existing linters and community rules, blocking only new warnings before a push. It assigns AI reviewers by risk to examine changes from several angles and confirms that tests ran and can catch problems.

The core toolset consists of a single-file Python CLI using only the standard library, Git hooks, AI working instructions in CLAUDE.md / AGENTS.md, and project notes. Claude Code also has three plugins: session event recording, handoff instructions during conversation compaction, and restrictions on marked review agents’ tools and direct file writes. These plugins have no Codex counterpart. The review restrictions are not a security sandbox: Bash remains a full shell. Use `lumos events` to inspect the event ledger.

## How it works

<p align="center">
  <a href="assets/map-en.svg">
    <img src="assets/map-en.svg" alt="Four steps around each change: read the code and add context from notes, dispatch AI reviewers by risk, review and handle every finding, write back; an outer loop checks the process itself" width="760">
  </a>
</p>

1. **Read the code, add context**: AI reads the code first. When it edits a file, the tool supplies related notes with reasons the code cannot reveal. For descriptions of code behavior, code takes precedence over conflicting notes. For deployment state, business constraints, and other questions code cannot answer, verify or ask a person.
2. **Assign AI reviewers based on risk**: See "How code review works" below.
3. **Every finding needs an outcome**: Fix it, explain why it will not be fixed, or disprove it with evidence. All findings must be addressed to pass.
4. **Update the notes**: Record trade-offs and verification methods in the note responsible for that file, ready for the next change.

The outer loop checks the process itself; see "How the toolkit keeps improving (evals)" below.

## Connecting plans, features, and verification

Linked notes form a “graph”; each note is a “node” covering a plan, feature description, verification record, or incident. The fictional shop below shows the sequence: plan checkout and payment integration, build the features, then record results from checkout end-to-end tests and duplicate-payment stress tests. The gold rings are only an illustration of a note that carries a contract and links to verification records; the tool has no “protected” status. What it actually does is record important rules as ★INVARIANT★ contract lines, bind the tests that guard them, have an AI that took no part in the work audit them independently, and optionally break the code on purpose in an isolated copy to confirm the tests turn red (`lumos guard`). If canceling an order fails to refund points, the incident links back to checkout, followed by a repair plan, a fix, and a regression test.

<p align="center">
  <a href="assets/graph-demo-en.svg">
    <img src="assets/graph-demo-en.svg" alt="An illustrative map of linked notes for a shop: plans connect to features and verification records; incident lessons feed later plans" width="760">
  </a>
</p>

## How code review works

<p align="center">
  <a href="assets/risk-review-en.svg">
    <img src="assets/risk-review-en.svg" alt="Review weight follows risk: new code is scanned with fixed rules; ordinary changes get one or two reviewers, high-risk changes at least seven per round, five problem-finders plus architecture and security; every finding must be fixed, waived with a reason or disproved; a high-risk push needs a review outcome" width="760">
  </a>
</p>

- **Assess risk first**: Before a push, fixed rules scan newly added code for patterns prone to problems.
- **Choose how many AI reviewers to assign**: Ordinary changes get 1 to 2; high-risk changes get at least 7 per round: 5 look for problems, 1 checks architectural consistency, and 1 checks security. A finalized design spec adds 1 reviewer to check against it.
- **High-risk changes need a review outcome to push**: Record a pass or a skip with a written reason before pushing; otherwise, the Git hook blocks the push.

**Fixing a defect must also preserve behavior that already worked.** Revision-round instructions pin the before and after versions, check that the original problem fails before and passes after, and separately check that existing behavior passes on both versions. Fresh reviewers then examine repair side effects. Repairs mixed with refactoring retain intermediate verification points; selected high-risk preservation cases also check whether tests detect degradation. `lumos loop fix-check` checks repair records and post-fix tests, but is advisory and does not replace these checks or the next review. Evidence references, snapshots, and records are also checked before accepting them. See the [code review instructions](skills/lumos-code-loop/SKILL.md).

Review is one layer. Risk classification, AI review, approval rules, external rules (linters), and tests each have gaps. Stacking them makes it harder for a problem to pass through them all: the Swiss cheese model.

<p align="center">
  <a href="assets/swiss-cheese-en.svg">
    <img src="assets/swiss-cheese-en.svg" alt="Five Swiss-cheese defence layers, with escaped defects feeding new rules or tests" width="760">
  </a>
</p>

## Tests must be useful, not a rewrite of the code

**All tests passing does not mean the feature is correct.** If a test computes its expected value with the same algorithm as the production code, both can make the same mistake and still pass. If it only checks that the source contains a certain function name, the actual behavior can break while the test stays green.

Say the requirement is "3 items at 5 each should total 15":

```python
# Bad: rewrites the implementation's algorithm, so it cannot independently judge whether the algorithm meets the requirement
expected = quantity * unit_price
assert total_price(quantity, unit_price) == expected

# Good: checks the actual result against a confirmed requirement case
assert total_price(quantity=3, unit_price=5) == 15
```

This case is only a starting point; discounts, empty orders, invalid input, and other behavior still need to be covered according to the requirements. Lumos asks developers to state "input, expected result, source of the oracle, and the error it should catch" up front. For bug fixes and key guards, they must also confirm that the fault actually turns the target assertion red, then restore the code and see it go green. Structure and wiring checks can stay, but they cannot replace behavior verification.

**Catching a broken program does not mean the expected answer is right.** The program and the test can copy the same wrong requirement; check an independent source for the answer first, then look at fault-red and restore-green. For behavior tests suspected of being tied to the implementation, also check that a behavior-preserving refactor stays green. Per-stack writing workflows, tool qualification exams, and evidence boundaries are in the [test quality onboarding standard](skills/lumos-project-notes/commands/test-quality-standard.md) (Chinese).

The full practice is in [Implementation test quality](skills/lumos-project-notes/commands/03-寫回圖譜.md#實作測試品質) (Chinese), shared by the development and review instructions. These are development and review requirements; automated checks verify record formats and cannot judge for a person whether a test is actually useful.

The installed `lumos test-quality scan <test file or directory> --json` provides a read-only candidate scan: for Python it finds four kinds of suspicious patterns, and for other languages an optional local Semgrep recognizes specific self-comparing assertions (PHP included). `capture` explicitly runs a trusted local runner and saves JUnit output and source snapshots; `check` verifies normal → fault → restored evidence, plus optional refactor evidence. **Zero candidates, a green run, or a detected fault cannot on its own prove that a test has an independent answer.** The tool provides no sandbox and does not replace reviewing the requirement source; check the scope with `capabilities` first, then read [operation and capability limits](skills/lumos-project-notes/commands/03-寫回圖譜.md#事後掃描與執行收證已安裝-cli) (Chinese).

## Where humans come in

By default, Lumos leaves line-by-line diff review to AI and automated checks. People handle these decisions:

- Requirements, trade-offs, risk acceptance, and irreversible operations.
- If a standard- or high-tier review (design or code review alike) has not passed after its 3-round cap, stop for a human decision; AI cannot declare a pass itself. Record the decision to add a round or accept risk with `lumos loop cap-decision`. Before continuing, record a valid retrospective with `lumos loop retro`, or a reasoned skip. Once a human decision has been recorded, missing retrospective evidence blocks subsequent recording and the disposal gate.
- Whether rules still fit the business requires human sign-off and a record; tests cannot establish this.
- Each round's review reports and outcomes stay in the repo for spot-checking at any time.

## How notes are kept from going stale (drift)

Notes that describe old code can mislead AI. When I planted incorrect notes in a synthetic project, the smaller model, Haiku 4.5, dropped from 20/25 correct answers to 12/25. Lumos therefore checks at three points: writing notes, committing, and pushing.

**First check: write only what code cannot reveal.** Fields, defaults, and flows that the code already shows are not copied into notes. The tool blocks only two fixed patterns at commit time: new code line references and current-state descriptions (such as deployment settings) without a source. The rest relies on working rules and review.

Some sentences go stale easily: “there is no refund page yet” becomes wrong once the page exists, but nobody returns to fix it. When such a sentence is added, the tool suggests a one-line “revisit condition” stating when to check again, such as “when the refund page's file appears.” If the writer follows that advice, the push adding that file is blocked and the check points to the sentence. Update it or give a reason to keep it before pushing. The suggestion itself does not block commits, but a revisit condition must sit on its own line: one buried mid-sentence or in a table blocks the commit. Mark a condition as closed once it no longer needs a look, and it stops reminding.

**Second check: update notes when committing code.** Code changes without any note updates, or new source files without an assigned note, block the commit. The “code changed, notes untouched” check always blocks and projects cannot turn it off; if no note change is really needed, skip it with `git commit --no-verify`; a post-commit hook records every skip.

**Third check: find outdated statements before pushing.** Pushes are blocked if Python functions, classes, module- or class-level variables and constants, or command-line flags were deleted or renamed, or code files deleted or moved, and the old names or paths are still mentioned in the home notes of the code files you changed or in any note's summary (mentions elsewhere are only listed), if a rule's test exists but its note still says “test to be added,” a linked note was deleted, a revisit condition is met, or a rule's own “retire when…” condition has come true. A test name bound in a note that no longer matches a real test only warns by default; projects can make it block. Broken links between notes always block.

One more pre-push check rereads notes. When a push changes both the code and the note that manages it, the note often just gets a new paragraph while older sentences go unread: the code moves from three variables to four, yet the note still says three. Literal matching can't catch this, so the change and the whole note go to AI first, which points out the lines that are no longer true. The local push is blocked until that reread is recorded and every rule line it flags is fixed or explicitly kept; CI only warns. To keep a flagged line, record that with `lumos drift ack --kind reread`. Projects that can't send code to an external model can set this check to warn or off.

**Which checks a project can relax.** In `.lumos/config.json`, a project can set these to warn or off: outdated-statement checks, the note reread, note wording rules, file ownership, and new linter warnings (a few less common switches are listed in the [command reference](docs/command-reference.md#project-switches)). These have no switch: code changes without note updates, broken links, a high-risk change without a review record, test or hook files changed without re-approval, a failing full test suite in Lumos's own repo, and a missing Python 3.14.

**Closing one note tidies the others.** After a plan wraps up, an issue closes, or a decision is overturned, other notes that link to it but still say “pending” or “queued” are listed before push, and one command appends the outcome to that sentence. Closing an issue with `lumos drift fix --kind c2 --close` is blocked while its summary still lists an undecided decision or unhandled revisit conditions; changing its status directly with `lumos set` only lists them and does not block.

Closing a note without updating its summary also triggers a warning; closed notes whose summaries still say “pending” appear in drift checks. Keeping a met revisit condition requires an expiry or a traceable destination. Use `lumos summary-line` to maintain summaries; preview stale update-date repairs with `lumos updated-sync --stale --dry-run`.

When a note says something like “there are N kinds,” it can be tied to the list in the code (Python for now); if the code gains an item and the note doesn't, the health check lists it and one command updates the number.

<p align="center"><a href="assets/drift-guard-en.svg"><img src="assets/drift-guard-en.svg" alt="Three checkpoints from writing notes to pushing: writing rules enforced at commit with a warning for new 'not yet…' sentences and a block for revisit conditions buried mid-sentence, note maintenance checked at commit, and outdated references, broken links, revisit and retire conditions that have come true, missing bound tests and sentences still pending on a closed note checked before push, and notes changed with the code must first be reread by AI (blocked on the local push); each check is labelled as a block or warning" width="760"></a></p>

## What it looks like

Take the commit check as an example. If AI changes the refund logic and commits without writing notes, it receives this message (real output, excerpted and translated from Chinese):

```text
$ git commit -m "feat: check whether an order was already refunded"

Blocked: this commit changes code, but not a single knowledge note was touched.
…
Code changed in this commit (1):
   • src/payment.py
…
Pick one of two paths:
   1. Update the notes that should change, add them to the commit, and commit again.
   2. This really needs no note change (typo, formatting, comments, work in progress) → skip this check:
        git commit --no-verify -m '<message>'
      Skipping is recorded; it is not a silent pass.
```

The message is for AI: its instructions require it to update the notes and retry. If no update is needed, such as for a typo fix, it can skip the check, but the skip is recorded. You mainly decide business trade-offs and whether to accept a risk.

## How the toolkit keeps improving (evals)

You cannot rely on gut feeling alone to tell whether a rule change broke something or the AI is following the rules. Lumos runs four evaluations (evals), each once a week:

- **Review replay**: Reviewed cases store a pass/fail verdict. The current judging code recomputes it (no new AI review); a mismatch is flagged so someone can check whether a rule change broke something.
- **Retrieval exam**: Uses questions with human-labelled answers to check whether the tool finds the notes it needs.
- **Scenario probes**: Gives the AI plain-language requests to carry out in an isolated copy of the repo, checking whether it looks up notes and uses the right commands on its own. Each run restarts from the same frozen copy, an incident stops the whole batch, and broken runs are not scored (details in the [October 7–10 update audit](docs/updates/2026-10-10-readme-audit.md) (Chinese)).
- **Missed notes**: Checks whether the notes shown before an edit omit any that should be read.

<p align="center">
  <a href="assets/evals-overview-en.svg">
    <img src="assets/evals-overview-en.svg" alt="The toolkit itself is checked every week: review replay, retrieval exam, scenario probes, and missed-note checks; results are recorded weekly, a person is alerted when something goes wrong, and fixes become rules or tests measured again the next week" width="760">
  </a>
</p>

Not every check alerts a person as the illustration's step suggests; the next paragraph says which ones do.

Results are recorded weekly. A person is alerted when review replay finds a case whose verdict no longer matches, needs refreezing, cannot be frozen, or the replay or catch-up freeze run hits an error, or when a scenario probe fails. A lower retrieval-exam score is only recorded, not alerted; the exam alerts a person only when one tenth or more of the candidate notes its scoring touches have no label yet (this can happen even when every question has an answer), so someone can label them. Missed-note checks produce a list and distribution. Fixes become new rules or tests, checked again the next week. Major changes in direction start with a controlled experiment: the principle "read the code first; notes only add context" was adopted only after such an experiment.

There is also an [offline review convergence evaluator](governance/eval/review_convergence.md). It collects case leads from ordinary and capped reviews and compares two workflows on pinned cases and versions, separating repair, preserved behavior, new defects, rounds, and cost. Missing data remains unknown. It is a read-only local analysis tool, outside the weekly schedule; it does not run models or re-execute acceptance checks. Fingerprints check declaration consistency, not truth, and do not prove that review rounds have decreased.

These evals run mainly in Lumos's own repo; the retrieval exam also covers one other project named in the scheduling script, when that machine has its exam. They ensure regressions are visible, but do not guarantee that every change is an improvement.

## Install and limits

You need Git, Python 3.14+, and Claude Code or Codex. Run this in the project directory:

```bash
curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.sh | bash
```

**Version scope: this README describes `main`; the installer above defaults to `release`.** The branches may differ. Check the installed source and version rather than assuming it includes every main update. The [October 1–7](docs/updates/2026-10-07-readme-audit.md) and [October 7–10](docs/updates/2026-10-10-readme-audit.md) update audits (Chinese) list each audit's commits, documentation changes, and release boundaries.

When asked to initialize the current directory, check that it is correct before entering `y`. After installation, start a new AI session and run `lumos enforcement` to confirm all checks are connected. For Windows, offline installation, and removal, see the [onboarding guide](ONBOARDING.md) (Chinese). To upgrade an existing project, run `lumos update --dry-run` first to preview which rule files and tool files would change; it changes nothing.

<details>
<summary>Projects already on an older Lumos: moving to Python 3.14</summary>

- After updating, commits and pushes are blocked on machines without 3.14, with install instructions (macOS: `brew install python@3.14` or `uv python install 3.14`). If `python3` points to an older version, lumos finds 3.14 and re-runs itself.
- Set your CI's `actions/setup-python` to 3.14.
- Once 3.14 is installed, run `lumos install` once so the Claude/Codex hooks use it too.
- This changes the Codex hook command lines, so Codex may ask you to re-approve them in an interactive session. Codex's trust state cannot be read locally; confirm with `lumos enforcement` plus one real trigger.

</details>

Lumos guarantees neither quality nor security and does not replace engineering judgment: notes can go stale, AI reviews can miss problems, and records do not prove correctness. People still decide business trade-offs, irreversible operations, and risk acceptance.

Further reading: [Mental model](docs/mental-model.md) · [Taking over a project](docs/taking-over.md) · [Command reference](docs/command-reference.md) · [Architecture](ARCHITECTURE.md) · [SDD and Lumos](SDD-vs-Lumos.en.md) · [Methodology](docs/methodology/圖譜即合約.md) (Chinese)

License: [MIT](LICENSE). Your notes belong to you; Lumos claims no rights over them.
