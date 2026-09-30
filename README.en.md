<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/lumos-logo-dark.png">
    <img src="assets/lumos-logo.png" alt="Lumos" width="320">
  </picture>
</p>

# Lumos

[繁體中文](README.md) · **English**

[![CI](https://github.com/EnzoHsieh-Android/Lumos/actions/workflows/ci.yml/badge.svg)](https://github.com/EnzoHsieh-Android/Lumos/actions/workflows/ci.yml)

**When an AI writes your code, make it leave the "why" behind too.**

Having an AI write code through conversation is fast, but it doesn't remember anything for the project. The trade-offs you discussed and the options you rejected are gone the next time a conversation starts; a rule like "an order must never be refunded twice" can't be seen in the code; and when the AI says the tests passed, there's no way to check afterwards which ones ran.

Lumos fills that gap. It sits next to Claude Code or Codex and asks the AI, with every change, to write down why, which rules must not break, and how it was verified, as Markdown notes kept in the same repo as the code; at commit and push time, Git hooks check the parts that can be checked mechanically, such as whether the notes were updated. Think of it as ADRs (architecture decision records), CODEOWNERS and pre-commit wired together, except the one being checked is the AI.

The whole thing is small: a single-file Python command-line tool (standard library only), a set of Git hooks, working instructions written into CLAUDE.md / AGENTS.md, and the notes themselves.

## What it looks like

Suppose the AI changes the refund logic and commits without writing any note. It receives this message (real output, trimmed and translated from the tool's Chinese):

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

The reader of that message is the AI, not you. Its working instructions tell it to add the note and commit again; if no note is really needed (say, a typo fix) it can skip, and the skip is recorded. Your part is mainly business trade-offs, and whether to accept a given risk.

## How it works

<p align="center">
  <a href="assets/map-en.svg">
    <img src="assets/map-en.svg" alt="Four steps around each change: read the code and add context from notes, dispatch AI reviewers by risk, review and handle every finding, write back; an outer loop checks the process itself" width="760">
  </a>
</p>

1. **Read the code, add context**: the AI reads the code first; when it edits a file, the tool pushes the related notes to it to add the reasons the code can't show. When a note's description of code behaviour disagrees with the code, the code wins; things the code can't answer, like deployment state or business constraints, have to be checked at the source or asked.
2. **Dispatch AI reviewers by risk**: see the next section.
3. **Every finding needs an outcome**: fixed, waived with a reason, or disproved with evidence; nothing passes until that's done.
4. **Write back**: the trade-offs and how it was verified go into the note that owns the file, so the next change there can find them.

The outer loop checks the process itself: in Lumos's own repo, every case that completed review and has a design spec stores its pass/fail verdict; each week cases are re-run under the same version of the rules (sampled in rotation when there are too many to run in time) to confirm the same case still gets the same verdict. If a verdict changes, a rule change broke something and needs fixing.

Notes link to each other. Below is an illustrative online shop: plans link to the features they produced and their verification records; when an incident happens, it leads back to a fix plan and a regression test.

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

- **Rate the risk first**: before a push, the tool scans the newly added code with fixed rules for patterns that tend to cause trouble.
- **Then decide how many AI reviewers**: one or two for ordinary changes; at least 7 per round for high-risk ones, each looking from one angle: 5 look for problems, 1 checks consistency with the existing architecture, 1 checks security, plus 1 against the design spec when a finalized one exists.
- **No push until high-risk review is done**: a high-risk push must leave a review outcome (passed, or skipped with a written reason), or the Git hook blocks it.

Review is only one layer. Risk tiers, multiple AI reviewers, release rules, external rules (linters), and tests each have holes; stacked, it is harder for a problem to get through all of them (the Swiss cheese model).

<p align="center">
  <a href="assets/swiss-cheese-en.svg">
    <img src="assets/swiss-cheese-en.svg" alt="Five Swiss-cheese defence layers, with escaped defects feeding new rules or tests" width="760">
  </a>
</p>

**Where do humans come in?** By default Lumos doesn't require a person to read every diff line by line; that goes to several AIs and machine checks, and people handle the judgement calls below.

- Requirements, trade-offs, accepting a risk, and irreversible operations are decided by a person.
- A high-risk review runs at most 3 rounds; if it still hasn't passed, it stops and goes to a person, and the AI doesn't declare it passed itself (this is a working rule; the tool only warns when the cap is reached).
- Whether a rule still fits the business needs a person's sign-off, with a record; tests can't prove that.
- Every round's review reports and outcomes stay in the repo for anyone to audit.

**A real example.** The day the first small Vue project adopted Lumos (2026-09-10), the tool scanned the files it had installed as if they were the project's own code. The fix was rated high-risk: in round 1, 4 of 7 reviewers independently found the same hole; in round 3, a reviewer found the fix still had a hole; all 46 findings across four rounds were handled before the commit. Every round's [original review reports](governance/review-reports/code-工具自裝檔不算消費專案/) are in the repo (in Chinese).

<p align="center">
  <a href="assets/case-review-en.svg">
    <img src="assets/case-review-en.svg" alt="Timeline of one real review: four rounds with 7, 4, 7 and 5 completed review reports found 12, 6, 17 and 11 issues; in round 1 four reviewers found the folder-matching hole, in round 3 the fix was found to still have a hole, so it switched to content fingerprints; all 46 were handled before committing" width="760">
  </a>
</p>

## How notes are kept from going stale (drift)

When code changes but a note still describes the old behaviour, an AI reading it can be led astray. I deliberately planted incorrect notes in a synthetic project, and the smaller model, Haiku 4.5, dropped from 20/25 correct answers to 12/25. Lumos tackles this at three points: when writing notes, at commit, and before push.

The first check starts with what goes into a note. Fields, defaults, and flows that can be read from the code shouldn't be copied into notes; notes are for reasons the code can't explain. The tool can only enforce two fixed patterns here: newly added code line references and current-state descriptions, such as deployment settings, that don't cite a source. Both are blocked at commit. The rest depends on the working rules and review.

At commit, the second check asks whether the notes were maintained alongside the code. It blocks code changes that touch no notes, and new source files that have no note assigned to cover them. Before push, the third check looks for outdated references. If a function was deleted or a file renamed but a note still mentions the old name or path, it only warns. If a rule's test is already in place but the note still says “test to be added,” or a linked note has been deleted, it blocks the push. Code changes without a note update and broken note links always block; projects can set the other blocking checks to warn instead.

<p align="center"><a href="assets/drift-guard-en.svg"><img src="assets/drift-guard-en.svg" alt="Three checkpoints from writing notes to pushing: writing rules enforced at commit, note maintenance checked at commit, and outdated references and broken links checked before push; each check is labelled as a block or warning" width="760"></a></p>

How much does this catch? In another project using Lumos, we found 20 genuinely stale passages and ran each through the tools. The checks caught 7 cases of existing drift (35%). Had these checks been in place before the original pushes, they could have caught about 13.5, or roughly two-thirds. One case was only half covered, so it counts as half. Some changes still slip through: a feature is added while a note still says it doesn't exist, or a value changes while its name stays the same. We haven't finished measuring how many of the findings are false alarms.

The second check also has a straightforward limit: it can tell whether a note changed, but not whether the revised content is correct. In that same project, we sampled 55 current-state statements. Of the 54 we could assess, 22 were already stale. That is why the first check was added later, to address what gets written in the first place. Whether the notes are actually right still comes down to review and people.

<details>
<summary>More: review data and skip records</summary>

- **Do multiple reviewers help?** In 85 multi-reviewer rounds on Lumos itself (2026-07 to 08), 531 of 822 problems (64.6%) were caught by only one reviewer, so reviewers see different things. It's only descriptive: it can't predict what one more or one fewer reviewer would change, and how many reviewers caught each problem was entered by hand by the AI that dispatches and collects the reviews.
- **Were the findings real problems?** As of 2026-09-30, only 58 of 6,195 findings (0.9%) were judged not to need action. That judgement, though, was also made by AI.
- **Were skipped checks justified?** The "change code, touch notes" check was skipped 84 times across about 2,070 commits in Lumos's own repo. Claude and Codex each reviewed every one independently: both agreed 8 changed behaviour without recording why; 17 only changed test files; most of the rest were mid-way commits on a feature branch whose notes were added later. [Per-skip judgements](governance/eval/readme-bypass-judge/)
- **What about larger models?** Opus 5 scored 25/25 in all four groups of the experiment above and wasn't misled, but with notes each run took 2 to 5 times as long.
- **Did notes actually help?** Another 80 runs tested rules the code can't reveal: with code only, 0 of 5 correct; with notes, 8 of 15. One synthetic project with questions I designed, so it supports the direction rather than settling it.
- **What it can't stop**: some auxiliary checks let the change through if they fail themselves, so a tool failure doesn't stall development; skipping at commit time is recorded, but skipping the push checks with `--no-verify` leaves no local record, and CI only reruns them on pushes to main or pull requests.
- Raw records you can check: [blocks and passes](docs/.governance-log.jsonl), [skips](docs/.bypass-log.jsonl), [review reports](governance/review-reports/).

</details>

## Install and limits

You need Git, Python 3.14+, and Claude Code or Codex. From the project you want to onboard, run:

```bash
curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.sh | bash
```

When the script asks whether to initialize the current directory, check it's the right one before answering `y`. After installing, restart the AI session and run `lumos enforcement` to confirm the checks are wired up. For Windows, offline installation, and removal, see [onboarding](ONBOARDING.md) (Chinese).

<details>
<summary>Projects already on an older Lumos: moving to Python 3.14</summary>

- After updating, commits and pushes are blocked on machines without 3.14, with install instructions (macOS: `brew install python@3.14` or `uv python install 3.14`). If `python3` points to an older version, lumos finds 3.14 and re-runs itself.
- Set your CI's `actions/setup-python` to 3.14.
- Once 3.14 is installed, run `lumos install` once so the Claude/Codex hooks use it too.
- This changes the Codex hook command lines, so Codex may ask you to re-approve them in an interactive session. Codex's trust state cannot be read locally; confirm with `lumos enforcement` plus one real trigger.

</details>

Lumos does not guarantee quality or security, and it does not replace engineering judgement: notes can go stale, AI review can miss things, and a record does not make the content correct. Business trade-offs, irreversible operations, and whether to accept a risk still need a person to decide.

Further reading: [Mental model](docs/mental-model.md) · [Taking over a project](docs/taking-over.md) · [Command reference](docs/command-reference.md) · [Architecture](ARCHITECTURE.md) · [SDD and Lumos](SDD-vs-Lumos.en.md) · [Methodology](docs/methodology/圖譜即合約.md) (Chinese)

Licence: [MIT](LICENSE). Your notes are yours; Lumos claims no rights over them.
