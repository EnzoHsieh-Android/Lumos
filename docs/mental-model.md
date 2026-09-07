# The mental model and the machinery

[← back to the README](../README.en.md) · [繁體中文](心智模型.md)

This is for people who have decided to use it and want to know how it actually works. The README covers why; this covers what's inside, what each check stops, what a tool can prove — and what only a person can answer.

---

## 1. The whole idea, in four sentences

1. **The notes are the source of truth for *why*.**
   But for *what it actually does right now*, the authority is the tests and production. When the two disagree, **the notes don't automatically win** — work out which side is wrong, then write up the incident.

2. **Read before you touch.**
   To change an existing system, your first move is to search the notes, not grep. The notes give you the boundaries and the landmines; the code confirms the details.

3. **Write back on the way out.**
   Put the decisions and the verification results back while you're still the witness — don't leave the next person doing archaeology.

4. **Enforce it at commit time.**
   The three above rot if they rely on discipline. So the pre-commit check hard-stops "code changed, notes untouched".

---

## 2. Five kinds of note

<p align="center">
  <img src="../assets/note-types-en.svg" alt="Five kinds of note: module, verification record, incident, plan, index" width="880">
</p>

Every note opens with a few prefixed summary lines: `FLOW:` (how it flows), `KEY:` (the load-bearing facts), `DEP:` (what it depends on), `TEST:` (test state), `DECISION:` (decisions).

**They're designed so the opening lines alone give you the whole shape** — you shouldn't have to read the body. For a big note, start with the compressed view (`lumos context <node> --brief`, contracts still pinned to the top) and only expand if you need to.

---

## 3. Three chains that demand evidence

The problem with an ordinary wiki is simple: **the writer has the last word, and nobody notices when it's wrong.**

Lumos hangs a chain off every load-bearing claim — the heavier the claim, the harder the evidence it has to carry.

<p align="center">
  <img src="../assets/chains-en.svg" alt="Three chains: bind a test, write the rollback, and the half only a person can answer" width="900">
</p>

Written out, they look like this:

```
KEY:★INVARIANT★ <a business rule that breaks things if changed>  [test:test_method_name] [audit:model/date]
KEY:★IRREVERSIBLE★ <can't be undone: a production migration, say>  [rollback:decisions]
KEY:★CHECKPOINT★   <hard to recover: deploying to staging, say>
KEY:★DEBT★         <known to be incidental; safe to change>
```

Three things to hold on to:

- **Not sure it's a contract? Don't mark it.** Never reverse-engineer rules from what the code happens to do — that turns the status quo into a rule, and it's the easiest way to mislead the next person.
- **Unmarked means reversible.** Go ahead and change it.
- **The third chain carries no machine evidence, and that's by design, not an oversight.** Whether a rule still matches the business, whether that rollback would actually run — a tool can't answer either. So it's written down plainly instead of quietly ignored.

---

## 4. Enforcement: from a nudge to a hard stop

<p align="center">
  <img src="../assets/enforcement-en.svg" alt="Six layers on a spectrum from a nudge on the left to a hard stop on the right" width="900">
</p>

**Further right stops more — and happens later.** The layers on the left exist so you find the problem while it's still cheap.

The design **fails open** a lot: if the environment isn't complete, it lets you through and leans on CI. That means one broken governance tool never blocks the whole company — but it also means **you can't tell how many layers are actually live**.

```bash
lumos enforcement
```

It checks each layer and prints how many are wired up. **Note that it checks the wiring, not whether the judgement is right.** Remote settings it can't see from your machine (a required GitHub check, say) are listed honestly as unknown rather than assumed present.

---

## 5. Those opening fields: use commands, don't hand-edit

The structured fields at the top of a note (status, links, decisions) are written by command — the command formats them and verifies its own write:

```bash
lumos set <node> <field> <value>
lumos append <node> related "[[X]]"
lumos decision-add <node> "<content>" --decided DATE
```

**The most common hand-editing trap is putting several links on one line.** That grows a "ghost node" — something in the graph that doesn't exist, and isn't easy to spot.

---

## 6. What the review loop actually runs

The README covers the loop's four stages; this is what happens inside each one.

```mermaid
flowchart TB
    NODES[("📚 Notes<br/>rules that must not break · past incidents · decisions made · what was verified<br/>both the input to review and its output")]

    subgraph R1["1. Open a round → brief → review → intake"]
        direction LR
        NEXT["Open a round<br/>risk tier, which round, how many seats<br/>list the notes this topic already has"] --> LENS["Attach notes automatically<br/>code review from the diff · design review from the plan note<br/>a timeout leaves a line, no longer silent"] --> SEATS["Review seats<br/>several same-family AIs, different angles<br/>+ an architecture seat + one from another vendor"] --> INTAKE["Machine-check intake<br/>do quotes resolve? line numbers real? material read?<br/>unanchored findings aren't accepted"]
    end

    subgraph R2["2. Account for each finding → ledger → gate → certificate"]
        direction LR
        FOLD["Revise<br/>adopted ones change the draft, rejected ones get a reason<br/>borderline ones go to an outside AI to rebut"] --> LEDGER["Ledger<br/>one entry per seat plus a summary<br/>what was found, what changed, what was rejected"] --> GATE{"Pass?<br/>every finding accounted for ∧ record recomputable ∧ all quotes resolve<br/>code review: severe ones must be fixed"} -->|pass| FREEZE["Freeze the verdict<br/>stored as the reference answer<br/>replayed weekly by machine"] --> PASS["The 'reviewed' certificate<br/>bound to this version<br/>honoured by push and CI"]
    end

    subgraph R3["3. Around the edges: measure it, run it"]
        direction LR
        OBS["Observation ledger<br/>were the attached notes used? how often did old decisions block?"] ~~~ AUTO["Daily automatic round<br/>pick a gap → write a design → same path → stop and wait for a human"] ~~~ PROBE["Scenario probe<br/>does the AI search the notes first?<br/>Claude and Codex on the same questions"]
    end

    NODES ==>|"input: relevant notes go into the brief"| R1
    R1 --> R2
    R2 -.->|"ledger"| R3
    NODES <==>|"write back: verification records · decisions · candidate rules"| R2
    R1 <-->|"didn't pass: another round (max 3, then a human decides)"| R2
    R1 <-.->|"numbers feed back into seat count and what gets attached"| R3
    NODES <-.->|"check the rules are actually being followed"| R3

    classDef gnode fill:#1b3a2a,stroke:#3ddc84,stroke-width:2px,color:#e8fff0
    classDef step fill:#2a2440,stroke:#9a7bd6,color:#f0ecff
    classDef gate fill:#3a2020,stroke:#dc5b5b,color:#ffe8e8
    classDef obs fill:#3a2a1b,stroke:#dcab3d,color:#fff5e0
    class NODES gnode
    class NEXT,LENS,SEATS,INTAKE,FOLD,LEDGER,FREEZE,PASS step
    class GATE gate
    class OBS,AUTO,PROBE obs
```

Claude Code and Codex CLI follow the same path. One install wires up both, and the wrap-up behaviour matches.

---

## 7. Four design principles

- **Zero dependencies** — pure Python standard library. CI runs it directly; nothing to install.
- **Don't over-govern** — only load-bearing claims get a chain. Soft reminders stay soft. No ceremony without matching value.
- **An honest ceiling** — the tool proves form, not business correctness. What it can't say, it says it can't say.
- **The author doesn't get to judge** — where there's no right answer, the call goes to an independent AI that wasn't told the backstory.
