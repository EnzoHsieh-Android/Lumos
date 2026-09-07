<p align="center">
  <img src="assets/lumos-logo.png" alt="Lumos" width="420">
</p>

# Lumos

[繁體中文](README.md) · **English**

> That module you had an AI write three months ago? You need to change it today.
> You don't remember why it was built that way. Neither does the AI — every session, it starts as a stranger.
>
> **Lumos gives a project a second set of notes for everything the code can't say, then uses checks to make sure they actually get written.**

<p align="center">
  <img src="assets/graph-demo-en.svg" alt="A demo: an online store's notes — plan first, then the module, then a record" width="900">
</p>

---

## What this is

Code only tells you what things look like right now. Five things it can't tell you:

- **Why** this approach — what was compared, what was rejected.
- **Where this part ends**, and who gets hit if you change it.
- Which behaviours are **promises nobody may break**, and which just happen to be that way and are safe to refactor.
- Whether this was **ever verified**, and under what assumptions.
- Whether you can **take it back** if you get it wrong.

That knowledge used to live in a senior engineer's head, and left when they did. The AI era is worse: an AI is a stranger in every conversation. What you told it last time doesn't count this time.

Lumos writes those five things into a set of interlinked Markdown notes, then uses git checks (small programs that run when you commit or push) to close off the "changed the code, didn't touch the notes" path. **Not writing has to be more annoying than writing — otherwise nobody writes.**

Two things in that diagram are worth pausing on:

- **The gold ring isn't there from the start.** The blue module appears plain; the ring and star only grow once a green verification record is linked to it — because that's the rule: **claiming "this must not change" doesn't count until real evidence is bound to it.**
- **The orange line goes backwards.** An incident doesn't sit in a corner gathering dust; it gets wired into the next plan as required reading before anyone starts.

**You don't hand-write these notes, and you don't memorise commands.** You develop the way you already do — talking to an AI as you look things up, change things, decide things. Installing injects "when to look something up, when to write it back" into Claude Code's and Codex's rule files, so **the context that settles out of those conversations gets kept, because the rules make it get kept.**

---

## What's in a note

<p align="center">
  <img src="assets/graph-node-detail.jpg" alt="One note opened, showing its contract and a plain-language explanation" width="860">
  <br>
  <sub>The payment-integration note, opened. Lit up on the left: the notes connected to it.</sub>
</p>

Every note opens with a few summary lines you can take in at a glance. The real thing looks like this:

```
FLOW: checkout submitted → call the gateway with order_id → sync result → async confirmation → both must agree
KEY:★INVARIANT★ one order must never be charged twice [test:test_no_double_charge_on_retry]
KEY:★IRREVERSIBLE★ a charge that reached the gateway can't be pulled back, only refunded [rollback:decisions]
```

Those two starred markers are the heart of the whole thing:

- **★INVARIANT★ = this must not change; changing it breaks something else.**
  A claim that heavy can't just be asserted. That `[test:...]` has to name a test that **really exists and really runs** — if it doesn't resolve, the health check goes red.
- **★IRREVERSIBLE★ = once done, you can't take it back.**
  Marking it obliges you to write down real rollback steps — actual commands, an actual compensating flow. "Be careful" doesn't count.

So "what rules can't be touched in this project" isn't a question you ask a person. It's one command — usually one the AI runs for you:

```console
$ lumos contracts

# Systems/payment-integration.md
  ★INVARIANT★ one order must never be charged twice — resends, retries, duplicate webhooks all count
      ↳ bound test: test_no_double_charge_on_retry
# Systems/stock-deduction.md
  ★INVARIANT★ stock must never go negative — not by a single unit
      ↳ bound test: test_stock_never_goes_negative
# Systems/cart.md
  ★DEBT★ the cart lives in Redis with no database behind it; a Redis restart empties it.
          Known, currently acceptable, changeable any time.

4 contracts (changing one is a breaking change) | 2 debts (safe to change)
```

That last line matters more than it looks. **Spelling out which things are rules and which merely happen to be true means the next person refactoring doesn't have to guess.**

---

## Isn't this just Obsidian?

**The note format is Obsidian-compatible — open it in Obsidian if you like**, and you don't need to install any notes app for Lumos to work. We're not trying to replace it.

The difference in one line: **Obsidian is for people to browse. Lumos is for an AI to query.**

An ordinary notes app won't stop you, and won't find things for you either. Lumos adds this:

| | Ordinary notes app | Lumos |
|---|---|---|
| **An AI using it** | Dump files into context and go fishing | **One command back: ranked, filtered, compressed** |
| **Looking up from source code** | No such concept | **Give it a source file, get the notes it affects and which of them carry contracts** |
| You write "this rule must not change" | Saved. Fine. | Name the test that guards it. Can't? Health check goes red. |
| You changed code and touched no notes | Nobody notices | `git commit` stops you — fix it, or say in one line why it isn't needed |
| **Why it was decided that way** | Buried in prose; go read | **Decisions are their own field: id, date, reasoning, whether it was later overturned** |
| **A note has gone stale** | Nobody knows; people keep trusting it | **Verification records must state what would invalidate them, and get nagged when due** |

### The one that matters most: query it, don't pour it in

An AI handed an Obsidian vault can only read files into context. **This repo's notes come to 2.61 million characters** — they don't fit; and even if they did, the important parts would be diluted into noise.

Here's what 2.61 million characters looks like:

<p align="center">
  <img src="assets/graph-growth.gif" alt="Lumos's own knowledge graph growing to 440 notes over three months" width="820">
  <br>
  <sub>Lumos's own notes over three months: 440 of them, 1,572 links. Recorded from the actual tool, not drawn.</sub>
</p>

So Lumos lets it **issue a query** instead. Ask where a module's boundaries are, and this comes back:

```console
$ lumos context Systems/payment-integration --brief   # 783 chars back; the full note is 1,812
Heads up — this note carries a contract. Read it before you touch anything:
  ★INVARIANT★ one order must never be charged twice [test:test_no_double_charge_on_retry]
```

**Contracts are pinned to the top**, because that's the part you can least afford to miss. The difference isn't "faster" — it's **fits vs. doesn't fit**.

Two more lookups Obsidian can't give you:

```console
$ lumos impact --file payment/gateway.py    # I'm about to change this. What does it touch?

── direct (2) ──
  ⚠contract Systems/payment-integration.md ★IRREVERSIBLE★  (body-inline-code)
  ⚠contract Systems/checkout-flow.md ★INVARIANT★  (body-inline-code)
── indirect (12) ──
  hop1  Verification/2026-04-15_duplicate-charge-load-test.md  backlink ← via related ← payment-integration
  hop1  Issues/2026-05-06_points-not-refunded-on-cancel.md  backlink ← via related ← checkout-flow
```

```console
$ lumos query --tag status/doing            # What's still unfinished?

Projects/subscriptions_plan.md [doing]
Systems/push-notifications.md [doing]

2 nodes matched
```

The first is a **reverse lookup from source code** — hand it a filename, get back which notes are affected, which of those carry contracts you must not break, and for the indirect ones, which note they came through.

The second is a **structured query over tags**, not a full-text search. Tags come in families (`type/`, `status/`, and any you add such as `priority/` or `scope/`), and you can stack filters like "only what's still open" or "only what links to this note" — sliced by whatever taxonomy you chose.

The primary reader of these notes isn't a human — it's **the next session's AI**. So they're written so a stranger can follow them, and **designed to be queried rather than read**.

---

## The loop: it gets sharper each round

This is where Lumos parts ways with "a really well-written document". Documents go stale. This gets a little sharper every time it runs.

<p align="center">
  <img src="assets/loop-en.svg" alt="The graph feeds each review; each review writes back into the graph" width="900">
</p>

**One round goes like this:**

1. **Something arrives for review** — a design doc, or a batch of code about to be pushed.
2. **The machine works out which notes bear on this change and attaches them to the brief.** Reviewers don't go hunting, and they don't miss the lesson from an incident three months ago.
3. **A few AI reviewers, none told the backstory, each look for their own kind of hole.** The author doesn't get to judge their own work — that's a hard rule of the design.
4. **Every finding must be accounted for**: adopted ones change the draft, rejected ones need a written reason. Nothing ships until all of them are accounted for.
5. **The accounting is written back into the graph**, and becomes material for the next round.

Step five is the point. **Notes aren't the final output; they're the next round's input.** So round one might hand a reviewer three notes, and round five hands them eight — and all eight already earned their place in earlier rounds. Nobody dropped them in from memory.

In one line: **same reviewers, same time budget — only the material got sharper.**

> **The honest limit:** what a machine can prove is *form* — that a test exists, that a rollback is written, that someone independent reviewed it, that every finding was accounted for.
> Whether a rule still matches the business, or whether that rollback would actually run — **only a person can answer that.** Don't read "has evidence attached" as "safe".

---

## Who this is for — and who it isn't

**A fit if:**

- The project needs to live longer than a few months, and someone else (or another AI) will pick it up.
- You lean heavily on AI to write code and don't read every line yourself.
- There are places where a mistake really hurts: payments, inventory, permissions, data migrations.

**Not a fit if:**

- You'll finish it in two weeks and throw it away.
- It's a small solo tool you read every day and hold entirely in your head.
- You just want a nice notes app — Obsidian is genuinely enough for that.

**The cost, stated upfront:** this makes every commit take longer. What you buy is not having to do archaeology three months later. **If the project won't live three months, it doesn't pay for itself.**

---

## Getting it installed

### The project already uses Lumos

```bash
git clone <your-project> && cd <your-project>
python3 scripts/lumos bootstrap
```

One line: Lumos itself, the operating manual the AI reads, the global command, and the git checks. Then **restart your Claude Code or Codex conversation** — some of the prompting loads at session start.

### Adding it to a new project

Run this from inside your project directory:

```bash
curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.sh | bash
```

It asks "turn this directory into a lumos project? [y/N]" — press `y`.

- **The default is N**, so if you're standing in the wrong directory (your dotfiles, say), Enter skips it. No accidental installs.
- Don't want to pipe a remote script blind? `curl -fsSL <url> -o get.sh`, read it, then run it.
- Non-interactive environments like CI: append `-s -- --init` to create it without asking.

### Did it install?

```bash
lumos enforcement
```

It lists each layer of protection and whether it's **wired up** — note that it checks the wiring, not whether the judgement is right. All-green means the checks are registered, files are present, versions match. The Codex lines stop at "registered; can't tell locally whether it runs" — that's a platform limit, not a fault.

<details><summary>Windows (native PowerShell)</summary>

Prerequisites: Git for Windows, python on PATH, Claude Code.

```powershell
irm https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/release/get.ps1 | iex
# Restart the session. If lumos isn't found, add %USERPROFILE%\.local\bin to PATH.
cd <your-project>; lumos init
```
</details>

<details><summary>Partial install / offline / why there are two layers</summary>

**Why two layers:**
- **Project layer** — CI only sees your project repo, and git hooks are per-repo, so the checking tool has to be **copied into every project**. Update with `lumos update`.
- **Machine layer** — the operating manual the AI reads is **one copy per machine**, symlinked into the Claude Code / Codex directories. `git pull` the Lumos directory once and every project picks up the new version.

Project layer only: `lumos init` (`--no-hooks` creates the notes folder without the checks; existing notes are **never overwritten**). Machine layer only: `lumos install`. Fully manual:

```bash
git clone --branch release https://github.com/EnzoHsieh-Android/Lumos ~/harness/lumos-toolchain
cd ~/harness/lumos-toolchain && ./install.sh
python3 scripts/lumos install
scripts/install-graph-toolchain.sh --target <project-path> --slug <name>
```

`release` is the public line; only the maintainer moves it forward. Drop `--branch release` to follow the development line instead.

**Both Claude Code and Codex CLI are supported** — one install wires up both, with matching behaviour. Details in [the mental model](docs/心智模型.md).
</details>

---

## Your first time through

**You don't have to memorise a single command.** Open a Claude Code or Codex conversation and talk the way you normally would — the three things below happen on their own.

**1. Ask it a "why"**

> You: why does checkout reserve stock before it calls the payment gateway?

It won't go straight to the code. The discipline written into your rules file at install time makes it **read the notes first** — pulling out the boundaries and the contracts, then using the code to confirm the details. You'll see its answer carry things like "this one is a contract, and here's the test guarding it" — read from the notes, not guessed.

Here's what it sees behind the scenes:

```console
# Systems/payment-integration.md
type:system | status:done | created:2026-03-25 | updated:2026-06-10
Heads up — this note carries a contract. Read it before you touch anything:
  ★INVARIANT★ one order must never be charged twice [test:test_no_double_charge_on_retry]
summary:
  FLOW: checkout submitted → call the gateway with order_id → sync result → confirmation → both must agree
verified_by: [[Verification/2026-04-15_duplicate-charge-load-test]], [[Verification/2026-06-10_refund-drill]]
→ links out (3):
  • Systems/checkout-flow.md [done]
  • Verification/2026-04-15_duplicate-charge-load-test.md [done]
← links in (4):
  • Projects/subscriptions_plan.md [doing]
```

**Contracts go at the top, because that's the part you can least afford to skim past.**

**2. Tell it to record something**

> You: one order must never be charged twice — write that down; the test guarding it is `test_no_double_charge_on_retry`

It creates the note, writes the summary lines, binds the test and verifies its own write. You never have to know which fields to fill, what the markers look like, or which folder the file belongs in.

**3. Change some code, then wrap up**

If you changed code and touched no notes, **you get stopped once as you finish** — either update a note, or say in one line why it isn't needed. And when you go to commit, it stops you again:

```console
$ git commit -m "adjust checkout logic"

Blocked: this commit changes code, but not one word of the notes.
Code records what things look like now; notes record why they're that way. Change only
one side and the next person (or the next session's AI) will read new code with old reasons.

Pick one:
   1. Update the notes that need it, add them to the commit, commit again.
   2. This genuinely needs no note change (typo, formatting, a comment) →
      git commit --no-verify
      Skipping is recorded. It isn't a quiet pass.
```

**That block is the whole product.** Everything else exists to make it not annoying.

> **So what are all those `lumos <command>` lines in this README?**
>
> They're what the AI runs behind the scenes — not something for you to memorise. Installing writes "what to look up, and when" into Claude Code's `CLAUDE.md` and Codex's `AGENTS.md`, and wires up five checks that fire on their own: a session-start reminder, pushing the affected notes in front of it before it edits a file, attaching the relevant notes when reviewers are dispatched, the wrap-up check, and CI status.
>
> **You can absolutely run them yourself** ([command reference](docs/指令參考.md)) — you just won't need to day to day. This README shows the output so you can see what it actually read and what actually got stopped: **governance you can't see is governance that isn't there.**

---

## Why this exists

I believe fully autonomous development is coming.

But **an AI will never know a project's business experience on its own, and it won't know how the judgement calls were made.** Why the faster-looking approach was rejected. Which incident bought the rule that's in place now. Which number a person decided rather than calculated. None of that is in the code. It has always lived in people's heads — and when they leave, it goes with them. An AI has it worse: it arrives a stranger in every conversation.

Models will keep getting stronger. But a stronger model facing a project with no context is still a stranger.

So I'm convinced of this: **the foundation of the next generation of software development won't just be models that write better code — it will be the engineering discipline that keeps the context.**

Lumos is my answer to that.

---

## Going deeper

- **[The mental model and the machinery](docs/心智模型.md)** — the kinds of notes, how the three "attach your evidence" chains work, what each check blocks, and what this thing can't do.
- **[Command reference](docs/指令參考.md)** — the commands you'll actually use day to day. `lumos --help` is authoritative.
- **[Taking over a project with no notes](docs/接手舊專案.md)** — an old company system, or something you vibe-coded for a month: how to reconstruct the context into notes.
- [Onboarding detail](ONBOARDING.md) · [Architecture](ARCHITECTURE.md) · [How this differs from spec-driven development](SDD-vs-Lumos.md)
- Long-form methodology (Chinese): [The graph is the contract](docs/methodology/圖譜即合約.md) · [The whole picture](docs/methodology/圖譜即合約-全景圖.md) · [Written for outside readers](docs/methodology/圖譜即合約-對外論述.md)

---

## Scope

Lumos ships **general-purpose tooling only**: the notes CLI, the checks and git hooks, and the cross-project convention manuals for particular tech stacks (kotlin / vue / csharp — they aren't tied to any one project, so they live here).

What doesn't come in: your business notes, release scripts, framework choices that only one project makes.

---

## Licence

[MIT](LICENSE).

**The toolchain's own files are covered by it**, including the ones copied into your project (the main program and hooks — each carries a licence header, the main program carries the full text).

**What the tool writes into your project is yours** — the discipline block in your config, the notes you write. Lumos claims no rights over them. Third-party components are listed at the end of LICENSE.
