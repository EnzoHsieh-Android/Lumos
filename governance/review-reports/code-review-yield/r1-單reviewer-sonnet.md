severity: blocker

### f1 `_SEV_RESIDUE_RE` false-positives on ordinary hyphen/list prose containing "minor"/"major"/"blocker", causing legitimate reports to be rejected with no machine-fixable path
severity: blocker
blocking: 是
file: `scripts/lumos:4967` (see also `_report_normalize_issues` at 4972, `normalize_report_text` at 5005)
引句:「[—–-]\s*(?:BLOCKER|MAJOR|MINOR)\b)")」
`_SEV_RESIDUE_RE` treats any hyphen/dash directly followed by `blocker`/`major`/`minor` (case-insensitive) as a "殘留" severity declaration, but markdown list markers are hyphens: a perfectly normal report line `- minor 問題:文件裡有錯字,不影響邏輯` (a bullet using the domain word "minor" as prose, not a declaration) matches and gets rejected. Reproduced end-to-end: `canary record` on a report containing that one line returns rc2 "還沒正規化" for the whole report; `report-normalize --write` cannot fix it (`changed=0`, issue stays), forcing the author to rewrite legitimate content just to get past the gate — exactly the "改內容才能過關" the S1/d5 design explicitly tried to avoid. Also reproduces on plain compound words like `這是個 non-major 的調整`.

### f2 `gov --stats` "審查有沒有用" section — including the write-side-rejection counter it was built for — is fully suppressed when no successful `reported`-bearing round exists yet, reproducing the exact blind spot the feature claims to fix
severity: major
blocking: 是
file: `scripts/lumos:4525` (gating `if`), `scripts/lumos:4542` (`_rej` computed/printed only inside that block)
引句:「if _K or escapes:」
The whole section — including `_rej = [r for r in ded if r.get("gate") == "canary" and r.get("kind") == "rejected"]` and its "記帳被寫側擋下 N 次" print — is nested inside `if _K or escapes:`. Reproduced: wrote 3 rejected write-side events into `.governance-log.jsonl` for a loop that has zero successful `reported` rounds and zero escapes; `lumos gov --stats` prints nothing about "審查有沒有用" or "記帳被寫側擋下" even though 3 rejections are in the ledger. This is the identical failure the diff's own commentary cites as the r3 blocker reason for adding the rejection event in the first place ("rc2 不落帳=永遠看不到撞牆幾次") — now the event IS logged, but stays invisible in the one summary view meant to surface it until at least one round succeeds.

### f3 `--refuted-set` intake matching doesn't exclude fenced code blocks, so a "format example" in the intake file counts as real reproduction evidence
severity: major
blocking: 是
file: `scripts/lumos:5456`
引句:「for ln in _itext.splitlines())」
The intake-row match loop (`_pat.search(ln) and any(w in ln for w in _kw) for ln in _itext.splitlines()`) scans every raw line of the intake file with no fence awareness (unlike `_report_normalize_issues`/`_report_severities`, which deliberately use `_visible_lines`). Reproduced: an intake file containing only a fenced block explicitly labeled "這是格式範例,不是真的重現紀錄" with `| a1 | 範例說明 | MISS |` inside the fence makes `canary record --refuted-set a1=跑三次都沒重現 --intake <file>` return rc0 — the guard accepts a documented non-evidence example as if it were a real machine reproduction row. This is exactly the "編排者填個值就能把數字做好看" gaming path the task asked to hunt for.

### f4 "整字比對" for `--refuted-set` ids only excludes ASCII alnum boundaries, so CJK ids reproduce the same a1/a10 substring-collision bug the guard claims to have fixed
severity: minor
blocking: 否
file: `scripts/lumos:5454`
引句:「_pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![A-Za-z0-9])")」
The lookaround boundary characters are `[A-Za-z0-9]` only. For a non-ASCII id such as `甲`, both the preceding and following characters in a CJK sentence are themselves outside `[A-Za-z0-9]`, so the lookaround never blocks a match — `甲` matches inside the unrelated id `甲乙`. Reproduced directly: `re.compile(r"(?<![A-Za-z0-9])甲(?![A-Za-z0-9])").search("甲乙 這行沒有提到重現 MISS")` → `True`. Decision d3 explicitly claims this "整字" check was added so `a1` isn't matched by `a10`; that guarantee silently doesn't hold once ids aren't ASCII. Low practical severity only because SOP convention keeps ids ASCII (`f1`/`a1` style); no test in the diff exercises a non-ASCII id.

### f5 canary/rejected dedup uses second-resolution timestamp as the 5th key, so two rejections in the same wall-clock second still collapse into one
severity: minor
blocking: 否
file: `scripts/lumos:4704`
引句:「"token": d.get("ts", "") if (d.get("gate") == "canary" and d.get("kind") == "rejected") else ""})」
`_gate_event`'s `ts` is `isoformat(timespec="seconds")`, so the new de-dup discriminator only distinguishes rejections that land in different seconds. Reproduced: two identical `canary/rejected` rows sharing one `ts` (same second) still fold to "近 9999 天共 1 筆治理事件" in `lumos gov`, i.e. the exact "同 commit 連撞三次被折成 1" bug this fix's own commentary says it closes is only narrowed (to a one-second collision window), not eliminated — plausible for a script/orchestrator retrying `canary record` in a tight loop.

## 圖譜鏡頭

- `Systems/bound-tests-gate.md` ★INVARIANT★:不影響。該 INVARIANT 管的是 code-loop check 對固定席綁定測試的真跑/懸空判定,這次改動完全落在 `cmd_canary`/`_render_gov_stats`/`report-normalize` 這幾個函式,跟 bound-tests 邏輯零交集,只是恰好同一個檔案(`scripts/lumos`)。
- `Systems/canary-audit.md` ★INVARIANT★ ×2:不影響。①「record/second 回報成功 ⟺ 已落盤可讀回」——新加的 S1/S2 驗證(`_report_normalize_issues`、`--refuted-set` 檢查)全部發生在 `_jsonl_append_verified` 呼叫**之前**,被拒的記錄根本沒進入寫入路徑,寫入+讀回自驗那段程式碼本身未被此 diff 觸碰。②「second 純 telemetry 不影響 gate rc」——`cmd_canary_second` 函式完全沒被這次 diff 修改。
- `Systems/guard-kill.md` ★INVARIANT★ ×2:不影響。guard kill 的 rc 優先序與 `--json` 純淨輸出跟本次改動(review-yield 記帳/gov 統計/report-normalize)在程式碼路徑上完全不相交。
- `Systems/lumos-cli-read.md` ★INVARIANT★:不影響。`search` 的 superseded/stale 過濾邏輯未被這次 diff 碰到。
- `Systems/slim-install-安裝器.md`、`Systems/slim-uninstall-一行卸載.md`、`Systems/授權與歸屬.md`(合計 9 條 ★INVARIANT★):不影響。三者都因為「牽連檔 scripts/lumos」被列為間接相依,但它們管的是 CLAUDE.md 注入/備份還原/manifest/授權檔白名單,跟這次改動的函式(canary record 寫側、report-normalize、gov --stats、disposal 尾端漏斗)在程式碼上完全獨立,無交集。
- `Systems/slim-get-一行安裝.md` ★INVARIANT★(`.ps1` 編碼/`$Args` 保留名):不影響,同上理由,純屬同檔掛名。

最嚴重 severity: blocker,blocking 條數 3
