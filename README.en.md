<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/lumos-logo-dark.png">
    <img src="assets/lumos-logo.png" alt="Lumos" width="320">
  </picture>
</p>

# Lumos

[繁體中文](README.md) · **English**

> That module you had an AI write three months ago? You need to change it today.
> You don't remember why it was built that way. Neither does the AI — every session, it starts as a stranger.
>
> **Lumos gives a project a second set of notes for everything the code can't say, then uses checks to make sure they actually get written.**

<p align="center">
  <img src="assets/graph-demo-en.svg" alt="A demo: an online store's notes — plan first, then the module, then a record" width="760">
</p>

**Understand it** &nbsp;[What this is](#what-this-is) · [What's in a note](#whats-in-a-note) · [How this differs from Obsidian](#how-this-differs-from-obsidian) · [The loop that gets sharper](#the-loop-that-gets-sharper) · [Why plain language](#why-plain-language)<br>
**Use it** &nbsp;[Who this is for](#who-this-is-for) · [Getting it installed](#getting-it-installed) · [Your first time through](#your-first-time-through)<br>
**Beyond that** &nbsp;[Why this exists](#why-this-exists) · [Going deeper](#going-deeper) · [Scope](#scope) · [Licence](#licence)

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
  <img src="assets/note-anatomy-en.svg" alt="The anatomy of a note: machine-read fields, summary lines, contracts with their evidence, and below the divider the part for people" width="900">
</p>

Those two starred markers are the heart of the whole thing — **a heavy claim can't just be asserted; evidence has to hang off it**, and if it doesn't resolve, the health check goes red.

So "what rules can't be touched in this project" isn't a question you ask a person. It's one command — usually one the AI runs for you:

```console
$ lumos contracts

# Systems/payment-integration.md
  ★INVARIANT★ one order must never be charged twice
              — resends, retries, duplicate webhooks all count
      ↳ bound test: test_no_double_charge_on_retry
# Systems/stock-deduction.md
  ★INVARIANT★ stock must never go negative — not by a single unit
      ↳ bound test: test_stock_never_goes_negative
# Systems/cart.md
  ★DEBT★ the cart lives in Redis with nothing behind it; a restart empties it
          Known, acceptable for now, changeable any time

4 contracts (changing one is a breaking change) | 2 debts (safe to change)
```

That last line matters more than it looks. **Spelling out which things are rules and which merely happen to be true means the next person refactoring doesn't have to guess.**

---

## How this differs from Obsidian

**The note format is Obsidian-compatible — open it in Obsidian if you like**, and you don't need to install any notes app for Lumos to work. We're not trying to replace it.

The difference in one line: **Obsidian is for people to browse. Lumos is for an AI to query.**

| | Notes app | Lumos |
|---|---|---|
| **An AI using it** | Pour files into context | **One command: ranked and compressed** |
| **Lookup from source code** | No such concept | **Which notes it affects, which carry contracts** |
| "This rule must not change" | Saved. Fine. | **Name the test guarding it, or go red** |
| Code changed, notes untouched | Nobody notices | **`git commit` stops you** |
| **Why it was decided** | Buried in prose | **Its own field: id, date, reasoning, overturned?** |
| **A note gone stale** | Nobody knows | **Must say what invalidates it; nagged when due** |

### The one that matters most: query it, don't pour it in

An AI handed an Obsidian vault can only read files into context. **This repo's notes come to 2.61 million characters** — they don't fit; and if they did, the important parts would be diluted into noise.

<p align="center">
  <img src="assets/graph-growth.gif" alt="Lumos's own knowledge graph growing to 440 notes over three months" width="820">
  <br>
  <sub>Lumos's own notes over three months: 440 of them, 1,572 links. Recorded from the actual tool, not drawn.</sub>
</p>

Lumos lets it **issue a query** instead:

```console
$ lumos context Systems/payment-integration --brief   # 783 chars back; the full note is 1,812
Heads up — this note carries a contract. Read it before you touch anything:
  ★INVARIANT★ one order must never be charged twice [test:test_no_double_charge_on_retry]
```

**Contracts are pinned to the top.** The difference isn't "faster" — it's **fits vs. doesn't fit**.

One more lookup Obsidian can't give you — a **reverse lookup from source code**:

<p align="center">
  <img src="assets/impact-en.svg" alt="Give it a source file and the graph works out which notes are affected and which carry contracts" width="900">
</p>

Tags are also a **structured query**, not full-text search (`lumos query --tag status/doing`). They come in families, and filters stack: "only what's still open", "only what links to this note".

The primary reader of these notes isn't a human — it's **the next session's AI**. So they're **designed to be queried rather than read**.

---

## The loop that gets sharper

This is where Lumos parts ways with "a really well-written document". Documents go stale. This gets a little sharper every time it runs.

<p align="center">
  <img src="assets/loop-en.svg" alt="The graph feeds each review; each review writes back into the graph" width="900">
</p>

The four stages run in order, and the last one is the point: what gets accounted for is written back into the graph, and becomes the next round's material.

**Notes aren't the final output; they're the next round's input.** Round one might hand a reviewer three notes; round five hands them eight — and all eight already earned their place. Same reviewers, same time budget; only the material got sharper.

> **The honest limit:** what a machine can prove is *form* — that a test exists, that a rollback is written, that someone independent reviewed it, that every finding was accounted for.
> Whether a rule still matches the business, or whether that rollback would actually run — **only a person can answer that.** Don't read "has evidence attached" as "safe".

---

## Why plain language

<p align="center">
  <img src="assets/shift-en.svg" alt="By hand: one track, trade-offs stay in your head. Plain language: several tracks, trade-offs land as notes" width="900">
</p>

Writing it yourself means three things happen at once:

- **One track at a time.** That isn't a question of how efficient you are — it's what serial attention means. Hands on the keys, you can't push three things forward at once.
- **A later AI can only work backwards from the code.** And the code never contained the *why*; it only ever shows the *what*.
- **The most valuable part never existed anywhere.** Which options you compared, why you rejected one, what you were assuming at the time — none of it left your head, because you never said it to anyone.

Develop in plain language and all three invert: you handle the decisions, the requirements and the trade-offs, while implementation runs on several tracks at once — and **the trade-offs already happen in the conversation**. No separate documentation pass; the rules make them land as notes.

**And the gap only widens.** The stronger models get, the worse the return on doing it by hand — but no matter how strong they get, a model facing a project with no context is still a stranger. **The skill you're practising depreciates; the context you leave behind doesn't.**

---

## Who this is for

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

**You won't have to memorise a single command.** Open a Claude Code or Codex conversation and talk the way you normally would:

<p align="center">
  <img src="assets/usage-en.svg" alt="Left: three things you say in plain language. Right: what it runs on its own." width="900">
</p>

Those three lines on the left are your whole job. The commands on the right **you never touch and never memorise** — installing writes "what to look up, and when" into Claude Code's `CLAUDE.md` and Codex's `AGENTS.md`, and wires up five checks that fire on their own (session-start reminder, pushing affected notes before an edit, attaching relevant notes when reviewers are dispatched, the wrap-up check, CI status).

When you go to commit with the notes untouched, this is what you get:

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

> You can run the commands yourself — see the [command reference](docs/指令參考.md). This README shows their output so you can see what got read and what got stopped: **governance you can't see is governance that isn't there.**

---

## Why this exists

I believe fully autonomous development is coming.

But **an AI will never know a project's business experience on its own, and it won't know how the judgement calls were made.** Why the faster-looking approach was rejected. Which incident bought the rule that's in place now. Which number a person decided rather than calculated. None of that is in the code. It has always lived in people's heads — and when they leave, it goes with them. An AI has it worse: it arrives a stranger in every conversation.

Models will keep getting stronger. But a stronger model facing a project with no context is still a stranger.

So I'm convinced of this: **the foundation of the next generation of software development won't just be models that write better code — it will be the engineering discipline that keeps the context.**

Lumos is my answer to that.

---

## Going deeper

- **[The mental model and the machinery](docs/心智模型.md)** — how the three evidence chains work, what each check blocks, and what this can't do.
- **[Command reference](docs/指令參考.md)** — you won't need these day to day, but they're here.
- **[Taking over a project with no notes](docs/接手舊專案.md)** — reconstructing an old system's context into notes.
- [Onboarding detail](ONBOARDING.md) · [Architecture](ARCHITECTURE.md) · [How this differs from spec-driven development](SDD-vs-Lumos.md)
- Long-form methodology (Chinese): [The graph is the contract](docs/methodology/圖譜即合約.md) · [The whole picture](docs/methodology/圖譜即合約-全景圖.md) · [Written for outside readers](docs/methodology/圖譜即合約-對外論述.md)

---

## Scope

Lumos ships **general-purpose tooling only**: the notes CLI, the checks and git hooks, and the cross-project convention manuals for particular tech stacks (kotlin / vue / csharp — they aren't tied to any one project, so they live here).

What doesn't come in: your business notes, release scripts, framework choices that only one project makes.

---

## Licence

[MIT](LICENSE), covering the toolchain's own files, including the ones copied into your project.

**The notes you write are yours.** Lumos claims no rights over them.
