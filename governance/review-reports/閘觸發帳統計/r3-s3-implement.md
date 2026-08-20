# r3-s3 implementability review — 閘觸發帳統計

Lens: could a competent implementer build exactly this spec without asking a question? Verified against `scripts/lumos` (14,969 lines) and real ledger data as of 2026-08-20.

## Verified accurate (not findings, stated for calibration)

- Ran the drift scan myself: `grep -oE '"gate":\s*"[^"]*"' scripts/lumos` → 19 matches, 15 distinct values (L2, L3, check-r, check-s, check-e1, check-e2, check-e3, check-k, check-j, signoff, kill, canary, ci, anchor-approve, code-loop). Matches the doc's "19 處、15 個不重複" exactly. No comment-embedded or test-file false positives leak in when the scan target is `scripts/lumos` alone (`scripts/test_lumos.py` has its own 4 literal-gate occurrences, all within the same 15-value set, but the doc scopes the scan to `scripts/lumos` only, so this doesn't matter). The one non-literal `"gate":` site (`scripts/lumos:2917`, `"gate": d.get("gate", "?")`, the governance-log mapper) is correctly excluded by the regex and correctly not a missed value, since the actual gate names it can produce are all already covered by the 15 write-side literals. `_KNOWN_GATES`, if implemented as a plain tuple/set of name strings, would not itself match the `"gate": "..."` pattern, so the test is not self-satisfying under the natural implementation.
- Reproduced the full 六欄 baseline table by hand (independent Python script replicating `cmd_gov`'s exact load/dedup logic) for check-s, check-e1, anchor-approve, code-loop: raw/dedup/node/commit counts all match the doc's table exactly (e.g. check-s 18283/7287/42/420). The line citations I spot-checked for the pipeline (`2950-2957` dedup, `2958-2960` node-filter, `2961-3000` presentation denoise, `2911-2912` bypass, `2931-2932` canary, `2944-2947` ci, `10071` anchor-approve) all point to exactly the code they claim to.

## Findings

### MAJOR — "mapper 硬寫 nodes: []" list misclassifies `code-loop`; its citation points at the writer, not the mapper, and the resulting rule conflicts with how `anchor-approve` is (correctly) treated

引句：「mapper 硬寫 `nodes: []` 的來源(code-loop `scripts/lumos:13956`、canary `2931-2932`、ci `2944-2945`、bypass `2911-2912`)→ 印 `n/a(該來源不記節點)`。」

`scripts/lumos:13956` is inside `_codeloop_gov_log` (the function that *writes* `.governance-log.jsonl` — `"gate": "code-loop", "kind": status, ... "nodes": [], ...`), not inside any `load()` mapper of `cmd_gov`. `code-loop` rows are read back by `cmd_gov` through the *same generic, dynamic* `.governance-log.jsonl` mapper used for `check-s`, `check-r`, `check-e1/2/3`, `check-k`, `check-j`, and `anchor-approve` (`scripts/lumos:2916-2919`): `"nodes": [stem(x) for x in d.get("nodes", [])]`. That mapper does **not** hardcode `nodes: []` — it reads whatever the JSONL row has. `code-loop`'s node column is empty today purely because the *writer* never populates it, which is a data fact, not a mapper fact.

This is the exact same mechanism as `anchor-approve`, which the doc explicitly places in the opposite bucket ("compute the real value, don't presuppose"; verified: `anchor-approve` genuinely has 5 distinct nodes in real data, with some individual rows empty). There is no principled distinction given between the two — only a wrong citation.

Consequence for an implementer: if they build the n/a-classification by literally checking "does this gate's `load()` lambda in `cmd_gov` hardcode `nodes: []`?" (which is the only concrete instruction given), `code-loop` will **not** match — it will fall into the "compute real per-window value" bucket like `anchor-approve`, and the column will print the literal number `0` instead of `n/a(該來源不記節點)`. I confirmed this by running the real dedup/aggregation myself: `code-loop` real distinct-node count = `0`, computed the same way `anchor-approve`'s `5` is computed. `0` and `n/a` look similar today by coincidence but are semantically different labels the doc insists on distinguishing (§"逐 gate 輸出"), and `t_gov_stats_na_columns` (test #3) doesn't say which bucket `code-loop` belongs to either — it only names the two rules generically, inheriting the same ambiguity. If `_codeloop_gov_log` is ever extended to record real nodes (a plausible future change, unrelated to `cmd_gov`), an implementation that hardcoded `code-loop` into the static n/a list (matching the doc's literal instruction) would silently keep suppressing real data forever — the opposite of what "逐 gate 逐窗口實算,不預設哪些 gate 沒節點" demands two sentences later in the same paragraph.

### MAJOR — the "統計區塊前三行固定序" rule never defines line 3's content for the (majority) non-`node`-filtered invocation, and test #6 / test #7 read as testing different line counts

引句：「**首行資訊的排序**:三條「印在首行」的規則(載入源清單 / 實際窗口 / 節點縮限警示)改為**統計區塊的前三行,固定此序**,不搶既有輸出的第一行(r2 s1 席:三條規則互斥、同時觸發時無法同時滿足)」

The only concrete wording given for the third line is scoped entirely to the `node`-filter case:

引句：「帶位置參數 node + `--stats` → 首行印縮限警示」

Nothing in the doc says what (if anything) occupies the third header line when `--stats` is invoked *without* a positional `node` — the ordinary, majority case. Two readings are both consistent with the text as written, and they produce different byte-level output:

(a) exactly 3 header lines always print, with line 3 carrying some unspecified neutral/default text when not node-scoped; or
(b) only the rules that "apply" produce a line — 2 lines in the default case, 3 only when node-filtered — and "固定此序" only constrains relative order among lines that exist.

引句：「前三行固定序(載入源→窗口→縮限警示)」

Test #6 (`t_gov_stats_layout`) names all three items as "the first three lines" without stating which invocation mode it fixtures against, while test #7 only asserts the third line's *presence* conditionally on `node` being passed — it never asserts its *absence* otherwise. `t_gov_stats_full` and `t_gov_stats_rc`'s "golden fixture" byte-comparison (test #10) is downstream of whichever reading is chosen, so an implementer must guess before they can write the golden fixture at all. This is a genuine "no answer given" gap in the placement/ordering section that the doc otherwise treats as fully resolved (r2 s1 already fixed the *ordering* conflict; this is a distinct, still-open *line-count* conflict).

### MINOR — 未出現清單 disclaimer's "逐字印出、整段比對" requirement is an inherently brittle duplicate-string test

引句：「整段比對,不是關鍵字命中」

Implementable (embed the identical string literal in both `scripts/lumos` and `scripts/test_lumos.py`), but by construction the test only proves the two copies agree with each other, not that the copy in the source is well-formed prose — any future edit to the disclaimer must touch both places by hand with no compiler/lint help catching drift between them (unlike `_KNOWN_GATES`, which has a scan-based drift test). Worth a one-line note in the design (e.g. "test imports the exact string constant from `scripts/lumos` rather than re-typing it") so the two copies can't diverge; as written, nothing stops a future edit from updating one and not the other.

### MINOR — 六欄 declared "全部是可重算的硬事實" but first-seen/last-seen date computation doesn't address rows with missing/empty `ts`

引句：「六欄,全部是可重算的硬事實:去重後筆數、原始行數、不同節點數、不同commit數、首見日、末見日。」

Every mapper defaults `ts` to `""` via `d.get("ts", "")`. `cmd_gov`'s own `--since` cutoff filter already special-cases this (`(r["ts"][:10] or "9999") >= cutoff` — treats a blank ts as "far future" so it's never dropped by the window filter), which implies the authors of `cmd_gov` know blank `ts` rows are a real (if rare) possibility. If a `--stats` implementation does a naive `min()`/`max()` over `r["ts"][:10]` per gate to get 首見日/末見日, a blank-`ts` row would sort as the empty string, which is lexicographically less than any real ISO date, corrupting 首見日 to a blank/garbage value rather than a real date. I confirmed no row in the current 5 checkable ledgers (`.governance-log.jsonl`, `.bypass-log.jsonl`, `.signoff-log.jsonl`, plus checked field presence) has a missing/blank `ts` today, so this is currently latent, not demonstrated — but the doc doesn't say to reuse `cmd_gov`'s existing `or "9999"` guard (or an equivalent) for this specific computation, so nothing prevents an implementer from writing the naive version.

### MINOR — 未出現清單 disclaimer doesn't mention "this gate's source wasn't loaded this run" as a reason for absence, though the design elsewhere establishes that's a real case

引句：「未出現 ≠ 無用。本帳看不到硬擋事件(`anchor verify` 擋下 push 時不寫任何帳),也分不出三種零:跑了沒事／接了帳但沒被觸發／守的功能從沒被用過。」

S1 separately establishes that the CI source is conditionally loaded per-repo (「第 7 源 ci 帳是條件載入...專案未宣告 ci 區塊就完全不 load」) and that the fix for this is printing the loaded-sources list on line 1 of the block. For `lumos-toolchain` itself this is moot — `docs/.ci-log.jsonl` exists, so `ci` is loaded and has real data. But for a consuming/mirror repo without a CI block declared (the scenario `CLAUDE.md` itself calls out for mirrors like `Citrus_Lumos_Full`), `ci` would permanently sit in the 未出現清單 with zero rows for a reason distinct from the three already enumerated (跑了沒事／接了帳但沒被觸發／守的功能從沒被用過) — "this source isn't even wired up here." The disclaimer text is required to be printed verbatim and compared whole-string by test #5, so this omission can't be patched later without also touching the drift test that pins it.

## Severity count

blocker: 0 / major: 2 / minor: 3
