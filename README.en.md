<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/lumos-logo-dark.png">
    <img src="assets/lumos-logo.png" alt="Lumos" width="320">
  </picture>
</p>

# Lumos

[繁體中文](README.md) · **English**

> That module you had an AI write three months ago? You need to change it today.
> You don't remember why it was built that way. The AI can't reach it either — open a new session and everything you said last time is gone.

<p align="center">
  <img src="assets/hook-en.svg" alt="Left: three months ago the conversation compared three approaches, rejected two with reasons, agreed one unbreakable rule, and ran the tests. Right: three months later only the code remains and the trade-offs have evaporated" width="900">
</p>

In that conversation, everything was there: the approaches you compared, why you rejected the others, the one rule you agreed must never break. **When it shipped, only the code survived.**

That isn't anyone's memory failing. **Code, as a medium, simply cannot hold those things.** Open a file and it tells you exactly one thing — what it looks like right now. On these five, it has nothing to say:

- **Why** this approach — what was compared, what was rejected.
- **Where this part ends**, and who gets hit if you change it.
- Which behaviours are **promises nobody may break**, and which just happen to be that way and are safe to refactor.
- Whether this was **ever verified**, and under what assumptions.
- Whether you can **take it back** if you get it wrong.

Those five used to live in a senior engineer's head. While they were around you could just ask; when they left, it left with them.

**What Lumos does is simple: it writes those five things into a set of interlinked Markdown notes that live in the same project as the code, then uses git checks — small programs that run when you commit or push — to close off the "changed the code, didn't touch the notes" path.** Not writing has to be more annoying than writing; otherwise nobody writes.

Here's roughly what that grows into — an online store, where a plan comes first, then the module, then a record of what was done:

<p align="center">
  <img src="assets/graph-demo-en.svg" alt="A demo: an online store's notes — plan first, then the module, then a record" width="760">
</p>

Two things in this diagram are worth pausing on:

- **The gold ring isn't there from the start.** The blue module appears plain; the ring and star only grow once a green verification record is linked to it — because that's the rule: **claiming "this must not change" doesn't count until real evidence is bound to it.**
- **The orange line goes backwards.** An incident doesn't sit in a corner gathering dust; it gets wired into the next plan as required reading before anyone starts.

**You don't hand-write these notes, and you don't memorise commands.** You develop the way you already do — talking to an AI as you look things up, change things, decide things. Installing injects "when to look something up, when to write it back" into Claude Code's and Codex's rule files, so **the context that settles out of those conversations gets kept, because the rules make it get kept.**

---

**Understand it** &nbsp;[What's in a note](#whats-in-a-note) · [How this differs from Obsidian](#how-this-differs-from-obsidian) · [The loop that gets sharper](#the-loop-that-gets-sharper) · [The same holds in any language](#the-same-holds-in-any-language)<br>
**Is it for you** &nbsp;[Who this is for](#who-this-is-for) · [Why plain language](#why-plain-language)<br>
**Use it** &nbsp;[Getting it installed](#getting-it-installed) · [Your first time through](#your-first-time-through)<br>
**Beyond that** &nbsp;[Why this exists](#why-this-exists) · [Going deeper](#going-deeper) · [Scope](#scope) · [Licence](#licence)

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

**Nothing here conflicts with Obsidian.** These are ordinary Markdown files — open and edit them in Obsidian if you like; equally, install no notes app at all and everything still works.

The difference is one line: **Obsidian is for people to browse. Lumos is for an AI to query.** Every difference below grows out of that one sentence.

### An AI can't read it all, so it has to query

An AI handed an ordinary vault can do exactly one thing: read files in. **This project's notes come to 2.67 million characters** — they don't fit, and if they did, the important parts would be diluted into noise.

<p align="center">
  <img src="assets/graph-growth.gif" alt="Lumos's own notes growing from a handful to four hundred over three months" width="820">
  <br>
  <sub>Lumos's own notes over three months (440 notes and 1,572 links when this was recorded; 444 today). Recorded from the actual tool, not drawn.</sub>
</p>

So it works the other way round: **it issues a query and gets back a ranked, compressed answer.**

```console
$ lumos context Systems/payment-integration --brief   # 783 chars back; the full note is 1,812
Heads up — this note carries a contract. Read it before you touch anything:
  ★INVARIANT★ one order must never be charged twice [test:test_no_double_charge_on_retry]
```

**Contracts are pinned to the top.** The difference isn't "faster" — it's **fits vs. doesn't fit**.

### It also has to work backwards

You're holding a source file and you want to know which notes changing it will touch, and which of those carry rules that must not break. **That direction doesn't exist in a notes app.**

<p align="center">
  <img src="assets/impact-en.svg" alt="Give it a source file and the graph works out which notes are affected and which carry contracts" width="900">
</p>

Tags follow the same logic: they're a **structured query**, not full-text search (`lumos query --tag status/doing`). They come in families, and filters stack — "only what's still open", "only what links to this note".

### And four things a notes app won't keep track of for you

| What you did | Notes app | Lumos |
|---|---|---|
| Wrote "this rule must not change" | Saved. Fine. | **Name the test guarding it** — can't, and the health check goes red |
| Changed code, didn't touch the notes | Nobody notices | **`git commit` stops you** — write it up, or say why it isn't needed |
| Recorded why something was decided | Buried in prose | **Its own field**: id, date, reasoning, whether it was later overturned |
| Left a verification sitting for months | Nobody knows it went stale | You must **say up front what would invalidate it**; the health check nags when it's due |

To close it in one line: **the primary reader of these notes isn't a human — it's the next session's AI.** They're built to be queried, not read.

---

## The loop that gets sharper

**This is where Lumos parts ways with "a really well-written document".** A document is at its most accurate the day it is finished, and only decays from there. This runs the other way: every round, the material gets a little sharper.

<p align="center">
  <img src="assets/loop-en.svg" alt="The graph feeds each review; each review writes back into the graph" width="900">
</p>

The four stages run in order, and the last one is the point: **what gets accounted for is written back into the graph, and becomes the next round's material.**

**Notes aren't the final output; they're the next round's input.** Round one might hand a reviewer three notes; round five hands them eight — and all eight earned their place in earlier rounds; nobody threw them in from memory.

Same reviewers, same time budget. **The only thing that changed is the quality of what they were handed.**

> **The honest limit:** what a machine can prove is *form* — that a test exists, that a rollback is written, that someone independent reviewed it, that every finding was accounted for.
> Whether a rule still matches the business, or whether that rollback would actually run — **only a person can answer that.** Don't read "has evidence attached" as "safe".

---

## The same holds in any language

The review loop above is language-agnostic. But "is this Kotlin coroutine on the wrong dispatcher?" or "will this SQL end up scanning the whole table?" — **those questions are bound to a language, and a generic review won't ask them.**

**The tool has been asking all along.** Before an edit and before a push, it surfaces "the performance questions this stack should ask itself".

**But putting a question in front of someone isn't the same as getting it answered.** Going through the governance ledger: **of 178 recorded reviews, barely a dozen carry any response to those questions at all** — and **13 of those answered for Python, a language that isn't even on the list**.

So: **seen, then skipped past** — and the few who did answer answered about the wrong thing. This section is about closing that second half.

<p align="center">
  <img src="assets/stack-gate-en.svg" alt="The journey of one change: the extension identifies the stack and pulls its questions; before editing only the triggered ones surface; before pushing each needs an answer; push and CI block on any missing one; reviewers treat the answers as refutable claims" width="900">
</p>

### It only asks what you actually touched

Six stacks (Kotlin, C#, Vue, SQL, Swift, Node), **32 questions in total**, each carrying its own set of trigger words. The tool matches them against the lines this change added or removed — **only the questions you genuinely touched get surfaced**; the rest are logged as not-triggered.

That part matters: **it does not hand you all 32.** Handing over everything is the same as handing over nothing — people skim past it.

### Before you push, every question needs an answer

Three ways to answer. Pick one:

| Your answer | What you attach |
|---|---|
| **Done** | Evidence — which file and line, or which test guards it |
| **Not applicable** | One reason |
| **Not yet** | A link to an open issue |

**One missing answer blocks the push, and it doesn't care about the risk tier.** This is a separate gate from the earlier "high-risk changes need a review" one — **if your change touched a question, you answer it, however small the change is.**

### What the tool checks, and what it doesn't

This line has to be spelled out, or it reads as "the machine guarantees quality":

| You said | The tool checks | The tool **doesn't** check |
|---|---|---|
| Done, see this line | The file exists, the line is in range | **Whether that line actually solves it** |
| Done, there's a test | The test is findable, and in the pushed tree | **Whether that test has any teeth** |
| Not applicable | A reason was written, and is long enough | **Whether the reason holds** |
| Not yet | The issue exists and is still open | **Whether it will ever get done** |

**Whether an answer is right, the tool does not judge at all.** Those answers get attached to the reviewers' briefs — **what the review seats argue with is exactly these answers.**

### Switching language changes one box, not the path

The whole path is shared. **The only per-language difference is the first box**: the extension identifies the stack, and that stack's questions come out. `.ts` and `.js` look at the project config to tell frontend from backend.

**A language that isn't on the list simply doesn't trigger this gate** — Python itself isn't on it. In that case you're back to the "high-risk needs review" path alone. A project easing into this can also set the gate to high-risk-only, or turn it off entirely.

> **Honestly: this gate stops "couldn't be bothered to answer". It does not stop "answered carelessly".**
> Write "not applicable" with a bogus reason and the tool can't tell; cite a test that doesn't actually cover the point and it can't tell either.
> **It catches the laziest kind of lie. The rest is on the review seats and on you.**

---

## Who this is for

**A fit if:**

- The project needs to live longer than a few months, and someone else (or another AI) will pick it up.
- You lean heavily on AI to write code and don't read every line yourself.
- There are places where a mistake really hurts: payments, inventory, permissions, data migrations.

**Not a fit if:**

- **You still write most of the code by hand, or your token budget is tight.** The whole premise is that context settles out of conversations with an AI — talk to no one, and there's nothing to keep. The review loops burn tokens of their own, too.
- You'll finish it in two weeks and throw it away.
- It's a small solo tool you read every day and hold entirely in your head.

**The cost, stated upfront:** this makes every commit take longer. What you buy is not having to do archaeology three months later. **If the project won't live three months, it doesn't pay for itself.**

---

## Why plain language

That first "not a fit" — still writing most of the code by hand — comes down to this.

<p align="center">
  <img src="assets/shift-en.svg" alt="By hand: one track, trade-offs stay in your head. Plain language: several tracks, trade-offs land as notes" width="900">
</p>

Writing it yourself means three things happen at once:

- **One track at a time.** That isn't a question of how efficient you are — it's what serial attention means. Hands on the keys, you can't push three things forward at once.
- **A later AI can only work backwards from the code.** And the code never contained the *why*; it only ever shows the *what*.
- **The most valuable part never existed anywhere.** Which options you compared, why you rejected one, what you were assuming at the time — none of it left your head, because you never said it to anyone.

Develop in plain language and all three invert: you handle the decisions, the requirements and the trade-offs, while implementation runs on several tracks at once — and **the trade-offs already happen in the conversation**. No separate documentation pass; the rules make them land as notes.

**And the gap only widens.** The stronger models get, the worse the return on doing it by hand — but no matter how strong they get, what a model can't reach it can't reach. **The skill you're practising depreciates; the context you leave behind doesn't.**

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

**Both Claude Code and Codex CLI are supported** — one install wires up both, with matching behaviour. Details in [the mental model](docs/mental-model.md).
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

> You can run the commands yourself — see the [command reference](docs/command-reference.md). This README shows their output so you can see what got read and what got stopped: **governance you can't see is governance that isn't there.**

---

## Why this exists

I believe fully autonomous development is coming.

But **an AI will never know a project's business experience on its own, and it won't know how the judgement calls were made.** Why the faster-looking approach was rejected. Which incident bought the rule that's in place now. Which number a person decided rather than calculated. None of that is in the code. It has always lived in people's heads — and when they leave, it goes with them.

**An AI can't reach it either, for two reasons. The second one gets talked about less:**

- **Open a new session and it can't see what was said in the last one.** The trade-off you spent half an hour settling with it yesterday? It has no idea.
- **Stay in one session long enough and the early part gets pushed out.** The context window has a ceiling; past a certain length the oldest material is dropped — **you think it still remembers, and it doesn't.**

Models will keep getting stronger. But neither of those goes away with a stronger model — **they are questions of what it can reach, not how clever it is.**

**So the context has to live outside the model. But writing it down isn't enough.**

If what you wrote doesn't move with the code, then three months later it describes a three-month-old world — **which is worse than having nothing, because the next person will believe it.** This is where every "let's document things properly" initiative actually dies: not that nobody wrote anything, but that nothing forced it to keep up.

So the thing to guarantee isn't "was it written" — it's **"does it change when the code changes"**. Discipline can't deliver that. Only a machine can: **change the code without touching the notes, and the commit doesn't go through.**

So I'm convinced of this: **the foundation of the next generation of software development won't just be models that write better code — it will be the engineering discipline that keeps the context, and won't let it rot.**

What you want is something that **grows with the work** — **not a system that gets written once and starts rotting from that day on.**

Lumos is my answer to that.

---

## Going deeper

- **[The mental model and the machinery](docs/mental-model.md)** — how the three evidence chains work, what each check blocks, and the half a tool can't prove.
- **[Command reference](docs/command-reference.md)** — you won't need these day to day, but they're here.
- **[Taking over a project with no notes](docs/taking-over.md)** — reconstructing an old system's context into notes.
- [Onboarding detail](ONBOARDING.md) · [Architecture](ARCHITECTURE.md) · [Coming from SDD](SDD-vs-Lumos.en.md)
- Long-form methodology (Chinese, shortest first): [The whole picture](docs/methodology/圖譜即合約-全景圖.md) (every check on one page) · [Written for outside readers](docs/methodology/圖譜即合約-對外論述.md) (the plain-language full version) · [The graph is the contract](docs/methodology/圖譜即合約.md) (the internal design record, with its history — longest)

---

## Scope

Lumos ships **general-purpose tooling only**: the notes CLI, the checks and git hooks, and the cross-project convention manuals for particular tech stacks (kotlin / vue / csharp / swift / node — `ls skills/` is the source of truth; they aren't tied to any one project, so they live here).

What doesn't come in: your business notes, release scripts, framework choices that only one project makes.

---

## Licence

[MIT](LICENSE), covering the toolchain's own files, including the ones copied into your project.

**The notes you write are yours.** Lumos claims no rights over them.
